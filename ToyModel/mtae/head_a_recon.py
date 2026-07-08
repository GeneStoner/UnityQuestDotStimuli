"""
Head A — recurrent V1<->MT autoencoder trained by DENOISING/COMPLETION.

Unsupervised. V1 = direction-hypercolumn motion energy of two translating
surfaces. The DRIVE is degraded (drop dots + occlude a patch); the TARGET is the
clean full field. Local V1 lateral can't fill a big hole -> the MT->V1 feedback
must learn to reproject the coherent field into it (location recovery = Cavanagh's
feedback-specificity problem, turned into the loss). No cue, no attention here.

After training we (1) look at fill-in on fresh clips, (2) plot the learned
feedback/lateral kernels, (3) probe cueing: clamp one surface's MT band and ask
whether V1 is selectively enhanced at that surface's locations.

Run:            /usr/bin/python3 head_a_recon.py
Retrain:  RETRAIN=1 /usr/bin/python3 head_a_recon.py
"""
import os, time
import numpy as np
import torch
import torch.nn.functional as F
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import recurrent_scaffold as RS
import leverage_check as L

torch.set_grad_enabled(True)   # leverage_check disables grad at import; re-enable for training
torch.manual_seed(0); np.random.seed(0)
DEV, HERE, FIGS = RS.DEV, RS.HERE, RS.FIGS
H, W, NDIR, NDIR_MT = RS.H, RS.W, RS.NDIR, RS.NDIR_MT
MT_H, MT_W = RS.MT_H, RS.MT_W
APER = RS.APER
xx, yy, cx, cy, Rap = RS.xx, RS.yy, RS.cx, RS.cy, RS.R
CHAN_DIR = RS.CHAN_DIR
CHAN_DIR_MT = np.arange(NDIR_MT) * 2 * np.pi / NDIR_MT
APER_T = torch.tensor(APER[None, None].astype(np.float32), device=DEV)
APER3_T = torch.tensor(np.broadcast_to(APER[None], (NDIR, H, W))[None].astype(np.float32), device=DEV)
GAIN, ALPHA, SIGMA, NSTEP = 1.0, 0.3, 1.0, 20


def corr_loss(v, c, mse_w=0.1):
    """Structure-sensitive: 1 - masked correlation (+ tiny MSE anchor). A uniform
    blob has ~zero correlation -> loss ~1, so flooding is no longer a cheap minimum."""
    n = APER3_T.sum()
    mv = (v*APER3_T).sum([1,2,3], keepdim=True)/n
    mc = (c*APER3_T).sum([1,2,3], keepdim=True)/n
    vc = (v-mv)*APER3_T; cc = (c-mc)*APER3_T
    corr = (vc*cc).sum([1,2,3]) / torch.sqrt((vc*vc).sum([1,2,3])*(cc*cc).sum([1,2,3]) + 1e-8)
    mse = (((v-c)**2)*APER3_T).sum([1,2,3])/n
    return (1-corr).mean() + mse_w*mse.mean()


def sample_dots(n):
    pts = []
    while len(pts) < n:
        p = np.random.rand(2) * [W, H]
        if (p[0]-cx)**2 + (p[1]-cy)**2 <= Rap**2:
            pts.append(p)
    return np.array(pts, np.float32)


def render_energy(pos, th):
    if len(pos) == 0:
        return np.zeros((NDIR, H, W), np.float32)
    dx = xx[None]-pos[:,0,None,None]; dy = yy[None]-pos[:,1,None,None]
    blob = np.exp(-(dx*dx+dy*dy)/(2*RS.SIG_SPACE**2))
    wdir = np.exp(RS.KAPPA*np.cos(th-CHAN_DIR)); wdir/=wdir.max()
    return np.einsum("d,mhw->dhw", wdir, blob).astype(np.float32)


def make_sample(n_per=30, drop=0.25, occ_r=0.0, noise=0.1):
    """Return degraded drive, clean target, and per-surface (clean energy, theta).
    Degradation = dot dropout + additive noise (+ optional occlusion patch)."""
    clean = np.zeros((NDIR, H, W), np.float32)
    degraded = np.zeros((NDIR, H, W), np.float32)
    surfs = []
    for _ in range(2):
        th = np.random.rand()*2*np.pi
        pos = sample_dots(n_per)
        e = render_energy(pos, th)
        clean += e
        surfs.append((e * APER[None], th))
        keep = pos[np.random.rand(len(pos)) > drop]
        degraded += render_energy(keep, th)
    if occ_r > 0:
        ox = cx + (np.random.rand()*2-1)*Rap*0.5
        oy = cy + (np.random.rand()*2-1)*Rap*0.5
        patch = ((xx-ox)**2 + (yy-oy)**2) <= occ_r**2
        degraded *= (1 - patch)[None]
    if noise > 0:
        degraded = np.clip(degraded + noise*np.random.randn(*degraded.shape).astype(np.float32), 0, None)
    return (degraded*APER[None]).astype(np.float32), (clean*APER[None]).astype(np.float32), surfs


def batch(bs):
    dg, cl = [], []
    for _ in range(bs):
        d, c, _ = make_sample()
        dg.append(d); cl.append(c)
    return (torch.tensor(np.stack(dg), device=DEV),
            torch.tensor(np.stack(cl), device=DEV))


def settle(net, s, gain=GAIN, alpha=ALPHA, n_steps=NSTEP, sigma=SIGMA, cue=None, cue_channels=None):
    """Differentiable settling with MULTIPLICATIVE feedback (attentional gain on the
    feedforward drive): Iv = s*(1 + gain*relu(fb)) + gain*lateral. Feedback can only
    modulate where there IS drive -> it cannot flood empty space, and clamping the cued
    surface's MT band multiplies up exactly that surface's driven dots. Lateral additive.
    cue=(theta,strength) OR cue_channels=(NDIR_MT,) adds a top-down MT bias."""
    v = torch.zeros_like(s)
    m = torch.zeros(s.shape[0], NDIR_MT, MT_H, MT_W, device=s.device)
    cue_bias = None
    if cue_channels is not None:
        cue_bias = torch.tensor(np.asarray(cue_channels, np.float32)[None, :, None, None], device=s.device)
    elif cue is not None:
        th, cstr = cue
        w = np.exp(2.5*np.cos(th - CHAN_DIR_MT)).astype(np.float32); w /= w.max()
        cue_bias = cstr * torch.tensor(w[None, :, None, None], device=s.device)
    for _ in range(n_steps):
        Iv = s * (1.0 + gain*F.relu(net.fb(m))) + gain*net.lv(v)
        Im = gain*(net.ff(v) + net.lm(m))
        if cue_bias is not None:
            Im = Im + cue_bias
        v = v + alpha*(RS.divnorm(F.relu(Iv), sigma) - v)
        m = m + alpha*(RS.divnorm(F.relu(Im), sigma) - m)
    return v, m


def train(steps=2500, bs=16, lr=8e-4):
    net = RS.RecurrentVMT().to(DEV)
    L.install_structured(net)                       # PS-flavored start (has leverage)
    for p in net.parameters():
        p.data = p.data + 0.02*torch.randn_like(p)  # break symmetry
    opt = torch.optim.Adam(net.parameters(), lr=lr)
    t0 = time.time()
    for s in range(steps):
        dg, cl = batch(bs)
        v, _ = settle(net, dg)
        loss = corr_loss(v, cl)
        opt.zero_grad(); loss.backward()
        torch.nn.utils.clip_grad_norm_(net.parameters(), 5.0)
        opt.step()
        if s % 250 == 0 or s == steps-1:
            print(f"  step {s:4d}  loss {loss.item():.5f}  ({time.time()-t0:.0f}s)")
    return net


# ---- eval -----------------------------------------------------------------
@torch.no_grad()
def fig_fillin(net, path, seed0=3000, n=5):
    fig, ax = plt.subplots(3, n, figsize=(2.1*n, 6.3))
    for j in range(n):
        np.random.seed(seed0+j)
        d, c, _ = make_sample()
        v, _ = settle(net, torch.tensor(d[None], device=DEV), n_steps=40)
        v = v[0].cpu().numpy()
        for i,(im,t) in enumerate([(d,"degraded drive"),(v,"settled V1 (recon)"),(c,"clean target")]):
            ax[i,j].imshow((im*APER[None]).sum(0), cmap="magma"); ax[i,j].axis("off")
            if j==0: ax[i,j].set_ylabel(t, fontsize=10); ax[i,j].axis("on"); ax[i,j].set_xticks([]); ax[i,j].set_yticks([])
        ax[0,j].set_title(f"seed {seed0+j}", fontsize=9)
    fig.suptitle("Head A: denoising/completion on fresh clips", y=1.01)
    fig.tight_layout(); fig.savefig(path, dpi=115, bbox_inches="tight"); plt.close(fig)


@torch.no_grad()
def fig_kernels(net, path):
    fig, ax = plt.subplots(1, 3, figsize=(13, 4))
    # feedback MT->V1 direction interaction (center-tap spatial sum): [MT_dir, V1_dir]
    fb = net.fb.weight.data.cpu().numpy()   # (NDIR_MT, NDIR, kh, kw)
    fbmat = fb.sum((2,3))
    im0 = ax[0].imshow(fbmat, cmap="coolwarm", vmin=-np.abs(fbmat).max(), vmax=np.abs(fbmat).max())
    ax[0].set_title("feedback MT->V1\n(dir x dir, Σ space)"); ax[0].set_xlabel("V1 dir"); ax[0].set_ylabel("MT dir"); plt.colorbar(im0, ax=ax[0], fraction=0.046)
    # lateral V1 direction interaction
    lv = net.lv.weight.data.cpu().numpy()   # (NDIR, NDIR, kh, kw)
    lvmat = lv.sum((2,3))
    im1 = ax[1].imshow(lvmat, cmap="coolwarm", vmin=-np.abs(lvmat).max(), vmax=np.abs(lvmat).max())
    ax[1].set_title("lateral V1->V1\n(dir x dir, Σ space)"); ax[1].set_xlabel("to dir"); ax[1].set_ylabel("from dir"); plt.colorbar(im1, ax=ax[1], fraction=0.046)
    # lateral V1 spatial profile of like-to-like (diagonal, averaged over dir)
    prof = np.mean([lv[k,k] for k in range(NDIR)], 0)
    im2 = ax[2].imshow(prof, cmap="coolwarm", vmin=-np.abs(prof).max(), vmax=np.abs(prof).max())
    ax[2].set_title("lateral V1 same-dir\nspatial kernel"); plt.colorbar(im2, ax=ax[2], fraction=0.046)
    fig.tight_layout(); fig.savefig(path, dpi=115, bbox_inches="tight"); plt.close(fig)


@torch.no_grad()
def cueing_test(net, n_trials=60, cstr=0.5):
    def corr(a, b):
        m = np.broadcast_to(APER[None].astype(bool), a.shape)
        a, b = a[m], b[m]; a = a-a.mean(); b = b-b.mean()
        return float((a*b).sum()/(np.sqrt((a*a).sum()*(b*b).sum())+1e-9))
    sels = []
    for _ in range(n_trials):
        d, c, surfs = make_sample(drop=0.0, occ_r=0.0)   # clean input for cueing probe
        (eA, tA), (eB, tB) = surfs
        s = torch.tensor(d[None], device=DEV)
        vA, _ = settle(net, s, n_steps=40, cue=(tA, cstr))
        vB, _ = settle(net, s, n_steps=40, cue=(tB, cstr))
        vA, vB = vA[0].cpu().numpy(), vB[0].cpu().numpy()
        selA = corr(vA, eA) - corr(vA, eB)
        selB = corr(vB, eB) - corr(vB, eA)
        sels.append(0.5*(selA+selB))
    return float(np.mean(sels)), float(np.std(sels))


if __name__ == "__main__":
    os.makedirs(FIGS, exist_ok=True)
    print(f"device={DEV}  V1={NDIR}x{H}x{W}  MT={NDIR_MT}x{MT_H}x{MT_W}  gain={GAIN} steps/settle={NSTEP}")
    ckpt = os.path.join(HERE, "head_a.pt")
    if os.environ.get("RETRAIN","0")=="0" and os.path.exists(ckpt):
        print("loading cached checkpoint (RETRAIN=1 to retrain)...")
        net = RS.RecurrentVMT().to(DEV); net.load_state_dict(torch.load(ckpt, map_location=DEV))
    else:
        print("training (denoising/completion)...")
        net = train(); torch.save(net.state_dict(), ckpt)

    # held-out fill-in metrics
    errs, corrs = [], []
    m3 = np.broadcast_to(APER[None].astype(bool), (NDIR, H, W))
    with torch.no_grad():
        for s in range(500, 540):
            np.random.seed(s); d, c, _ = make_sample()
            v, _ = settle(net, torch.tensor(d[None], device=DEV), n_steps=40)
            v = v[0].cpu().numpy()
            num = (((v-c)**2)*APER[None]).sum(); den = ((c**2)*APER[None]).sum()+1e-9
            errs.append(num/den)
            a, b = v[m3], c[m3]; a = a-a.mean(); b = b-b.mean()
            corrs.append((a*b).sum()/(np.sqrt((a*a).sum()*(b*b).sum())+1e-9))
    print(f"held-out: completion frac-var {np.mean(errs):.3f}   structure corr {np.mean(corrs):.3f} +/- {np.std(corrs):.3f}")

    fig_fillin(net, os.path.join(FIGS, "headA_fillin.png"))
    fig_kernels(net, os.path.join(FIGS, "headA_kernels.png"))
    sel, sd = cueing_test(net)
    print(f"cueing selectivity (clamp MT band, NO attention training): {sel:+.3f} +/- {sd:.3f}")
    print("figures -> headA_fillin.png, headA_kernels.png")
