"""
Stress the slot AE with NON-separable motion energy.

The clean result used surfaces that are exactly rank-1 separable (single global
direction (x) density), matching the slot decoder by construction. Here each dot
within a surface gets its OWN jittered direction (theta_surf + N(0,jit)), so a
surface is a BROADENED, non-rank-1 mixture the separable slot can only approximate.
Train on a range of jitter, then measure how factoring degrades with:
  (1) within-surface direction spread (jitter), at fixed good separation,
  (2) between-surface separation, at moderate jitter.

Run:            /usr/bin/python3 stress_slot.py
Retrain:  RETRAIN=1 /usr/bin/python3 stress_slot.py
"""
import os, time
import numpy as np
import torch
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import recurrent_scaffold as RS
import head_a_recon as HA
import slot_ae as S

torch.set_grad_enabled(True)
torch.manual_seed(0); np.random.seed(0)
DEV, HERE, FIGS = RS.DEV, RS.HERE, RS.FIGS
NDIR, H, W, APER = RS.NDIR, RS.H, RS.W, RS.APER
xx, yy, CHAN_DIR = RS.xx, RS.yy, RS.CHAN_DIR
APER_T = torch.tensor(APER[None, None].astype(np.float32), device=DEV)


def render_perdot(pos, thetas):
    """Each dot has its own direction -> non-separable surface energy."""
    if len(pos) == 0:
        return np.zeros((NDIR, H, W), np.float32)
    dx = xx[None]-pos[:,0,None,None]; dy = yy[None]-pos[:,1,None,None]
    blob = np.exp(-(dx*dx+dy*dy)/(2*RS.SIG_SPACE**2))                  # (M,H,W)
    wdir = np.exp(RS.KAPPA*np.cos(thetas[:,None]-CHAN_DIR[None]))       # (M,NDIR)
    wdir /= wdir.max(1, keepdims=True)
    return np.einsum("md,mhw->dhw", wdir, blob).astype(np.float32)


def make_hard(n_per=30, n_surf=2, jit_deg=25.0, noise=0.05, dirs=None):
    clean = np.zeros((NDIR, H, W), np.float32); surfs = []
    for k in range(n_surf):
        th = (np.random.rand()*2*np.pi) if dirs is None else dirs[k]
        pos = HA.sample_dots(n_per)
        thetas = th + np.radians(jit_deg)*np.random.randn(len(pos))
        e = render_perdot(pos, thetas)
        clean += e; surfs.append((e*APER[None], th))
    if noise > 0:
        clean = np.clip(clean + noise*np.random.randn(*clean.shape).astype(np.float32), 0, None)
    return (clean*APER[None]).astype(np.float32), surfs


def batch(bs):
    xs = []
    for _ in range(bs):
        c, _ = make_hard(jit_deg=np.random.uniform(0, 40))   # train over a jitter range
        xs.append(c)
    x = torch.tensor(np.stack(xs), device=DEV)
    return x, x


def train(steps=3200, bs=32, lr=1e-3):
    net = S.SlotAE(K=2).to(DEV)
    opt = torch.optim.Adam(net.parameters(), lr=lr)
    t0 = time.time()
    for s in range(steps):
        x, c = batch(bs)
        recon, *_ = net(x)
        loss = (((recon-c)**2)*APER_T).mean()
        opt.zero_grad(); loss.backward(); opt.step()
        if s % 400 == 0 or s == steps-1:
            print(f"  step {s:4d}  loss {loss.item():.5f}  ({time.time()-t0:.0f}s)")
    return net


@torch.no_grad()
def sel_of(net, d, surfs):
    (eA, tA), (eB, tB) = surfs
    _, slots, _, w = net(torch.tensor(d[None], device=DEV))
    slots = slots[0].cpu().numpy(); wk = w[0].cpu().numpy()
    sdir = np.angle((wk*np.exp(1j*CHAN_DIR)[None]).sum(1))
    ad = lambda a,b: abs((a-b+np.pi)%(2*np.pi)-np.pi)
    sA = int(np.argmin([ad(sdir[k], tA) for k in range(net.K)]))
    sB = int(np.argmin([ad(sdir[k], tB) for k in range(net.K)]))
    return 0.5*((S.corr(slots[sA],eA)-S.corr(slots[sA],eB)) + (S.corr(slots[sB],eB)-S.corr(slots[sB],eA)))


if __name__ == "__main__":
    os.makedirs(FIGS, exist_ok=True)
    ckpt = os.path.join(HERE, "slot_hard.pt")
    if os.environ.get("RETRAIN","0")=="0" and os.path.exists(ckpt):
        print("loading cached checkpoint (RETRAIN=1 to retrain)...")
        net = S.SlotAE(K=2).to(DEV); net.load_state_dict(torch.load(ckpt, map_location=DEV))
    else:
        print("training slot AE on NON-separable (jittered) stimuli...")
        net = train(); torch.save(net.state_dict(), ckpt)

    torch.set_grad_enabled(False)
    print("\n(1) selectivity vs within-surface direction jitter (separation fixed 120°):")
    for jit in [0, 10, 20, 30, 40, 60]:
        ss = []
        for _ in range(50):
            tA = np.random.rand()*2*np.pi
            d, surfs = make_hard(jit_deg=jit, dirs=[tA, tA+np.radians(120)])
            ss.append(sel_of(net, d, surfs))
        print(f"   jitter {jit:2d}°   selectivity {np.mean(ss):+.3f} +/- {np.std(ss):.3f}")

    print("\n(2) selectivity vs separation (within-surface jitter fixed 25°):")
    for sep in [20, 45, 90, 135, 180]:
        ss = []
        for _ in range(50):
            tA = np.random.rand()*2*np.pi
            d, surfs = make_hard(jit_deg=25, dirs=[tA, tA+np.radians(sep)])
            ss.append(sel_of(net, d, surfs))
        print(f"   sep {sep:3d}°   selectivity {np.mean(ss):+.3f} +/- {np.std(ss):.3f}")

    # figure: jitter=30, separated
    fig, ax = plt.subplots(3, 5, figsize=(13, 7.5))
    for j in range(3):
        np.random.seed(7000+j)
        tA = np.random.rand()*2*np.pi
        d, surfs = make_hard(jit_deg=30, dirs=[tA, tA+np.radians(120+np.random.rand()*40)])
        (eA, tA), (eB, tB) = surfs
        _, slots, _, w = net(torch.tensor(d[None], device=DEV))
        slots = slots[0].cpu().numpy(); wk = w[0].cpu().numpy()
        sdir = np.angle((wk*np.exp(1j*CHAN_DIR)[None]).sum(1))
        ad = lambda a,b: abs((a-b+np.pi)%(2*np.pi)-np.pi)
        sA = int(np.argmin([ad(sdir[k], tA) for k in range(2)])); sB = 1-sA
        panels = [(d.sum(0),"input (both)"),(eA.sum(0),f"surf A ({np.degrees(tA):.0f}°)"),
                  (slots[sA].sum(0),"slot->A"),(eB.sum(0),f"surf B ({np.degrees(tB):.0f}°)"),
                  (slots[sB].sum(0),"slot->B")]
        for i,(im,t) in enumerate(panels):
            ax[j,i].imshow(im*APER, cmap="magma"); ax[j,i].axis("off")
            if j==0: ax[j,i].set_title(t, fontsize=9)
    fig.suptitle("Slot AE on non-separable (per-dot jitter 30°) surfaces", y=1.005)
    fig.tight_layout(); p = os.path.join(FIGS, "slot_stress.png")
    fig.savefig(p, dpi=115, bbox_inches="tight"); plt.close(fig)
    print("\nfigure ->", p)
