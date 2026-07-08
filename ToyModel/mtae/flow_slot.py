"""
Flow-slot AE — the ROTATION stress test.

A single global direction per slot cannot represent rotation (local direction
depends on position). Here each slot is a RIGID FLOW: translation (vx,vy) + rotation
(omega). The local motion direction at every (x,y) is DERIVED from that flow:
    u_k(x,y) = (vx_k - omega_k*(y-cy),  vy_k + omega_k*(x-cx))
and the slot reconstructs V1 motion energy tuned to that local direction, scaled by
a density map d_k(x,y). Still only 3 motion params/slot, so factoring pressure holds.

Test on two COUNTER-ROTATING transparent fields (the VRDots cue-period stimulus):
does reading out one slot recover one rotation sense, with no attention training?

Run:            /usr/bin/python3 flow_slot.py
Retrain:  RETRAIN=1 /usr/bin/python3 flow_slot.py
"""
import os, time
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import recurrent_scaffold as RS
import head_a_recon as HA

torch.set_grad_enabled(True)
torch.manual_seed(0); np.random.seed(0)
DEV, HERE, FIGS = RS.DEV, RS.HERE, RS.FIGS
NDIR, H, W, APER = RS.NDIR, RS.H, RS.W, RS.APER
xx, yy, cx, cy = RS.xx, RS.yy, RS.cx, RS.cy
CHAN_DIR = RS.CHAN_DIR
KAPPA = RS.KAPPA
APER_T = torch.tensor(APER[None, None].astype(np.float32), device=DEV)
K = 2
VMAX, OMMAX, EPS = 2.0, 0.15, 1e-3

# torch grids / channel dirs on device
GX = torch.tensor((xx - cx).astype(np.float32), device=DEV)          # (H,W)
GY = torch.tensor((yy - cy).astype(np.float32), device=DEV)
COS_A = torch.tensor(np.cos(CHAN_DIR).astype(np.float32), device=DEV) # (NDIR,)
SIN_A = torch.tensor(np.sin(CHAN_DIR).astype(np.float32), device=DEV)
# coordinate channels (CoordConv) so the encoder can form position x direction
# moments -> detect rotation/curl, which mean-pooling alone cannot see
COORD = torch.stack([GX/RS.R, GY/RS.R])[None]                        # (1,2,H,W)


# ---------- stimulus (rigid-motion surfaces) -------------------------------
def flow_dir(pos, m):
    """Per-dot motion direction under rigid motion m=(vx,vy,om)."""
    gx, gy = pos[:, 0]-cx, pos[:, 1]-cy
    ux = m[0] - m[2]*gy
    uy = m[1] + m[2]*gx
    return np.arctan2(uy, ux)


def render_perdot(pos, thetas):
    if len(pos) == 0:
        return np.zeros((NDIR, H, W), np.float32)
    dx = xx[None]-pos[:, 0, None, None]; dy = yy[None]-pos[:, 1, None, None]
    blob = np.exp(-(dx*dx+dy*dy)/(2*RS.SIG_SPACE**2))
    wdir = np.exp(KAPPA*np.cos(thetas[:, None]-CHAN_DIR[None]))
    wdir /= wdir.max(1, keepdims=True)
    return np.einsum("md,mhw->dhw", wdir, blob).astype(np.float32)


def make_pair(mA, mB, n=30, noise=0.05):
    clean = np.zeros((NDIR, H, W), np.float32); surfs = []
    for m in (mA, mB):
        pos = HA.sample_dots(n)
        e = render_perdot(pos, flow_dir(pos, m))
        clean += e; surfs.append((e*APER[None], np.array(m, np.float32)))
    if noise > 0:
        clean = np.clip(clean + noise*np.random.randn(*clean.shape).astype(np.float32), 0, None)
    return (clean*APER[None]).astype(np.float32), surfs


def rand_motion():
    """Random rigid motion; ~half rotation-dominant, half translation-dominant."""
    if np.random.rand() < 0.5:
        om = np.random.uniform(0.06, OMMAX) * np.random.choice([-1, 1])
        return (np.random.uniform(-0.4, 0.4), np.random.uniform(-0.4, 0.4), om)
    th = np.random.rand()*2*np.pi
    v = np.random.uniform(1.0, 2.0)
    return (v*np.cos(th), v*np.sin(th), np.random.uniform(-0.03, 0.03))


def make_train():
    # rotation-heavy: 70% counter-rotating pairs so the model must USE omega
    if np.random.rand() < 0.7:
        mag = np.random.uniform(0.07, 0.15)
        mA = (np.random.uniform(-0.3, 0.3), np.random.uniform(-0.3, 0.3), +mag)
        mB = (np.random.uniform(-0.3, 0.3), np.random.uniform(-0.3, 0.3), -mag)
        if np.random.rand() < 0.5:
            mA, mB = mB, mA
        return make_pair(mA, mB)[0]
    mA = rand_motion()
    while True:
        mB = rand_motion()
        if abs(mA[2]-mB[2]) > 0.05 or (mA[0]-mB[0])**2 + (mA[1]-mB[1])**2 > 1.0:
            break
    return make_pair(mA, mB)[0]


def batch(bs):
    x = torch.tensor(np.stack([make_train() for _ in range(bs)]), device=DEV)
    return x, x


# ---------- model ----------------------------------------------------------
class FlowSlotAE(nn.Module):
    def __init__(self, K=K):
        super().__init__()
        self.K = K
        self.enc = nn.Sequential(
            nn.Conv2d(NDIR+2, 32, 3, 1, 1), nn.ReLU(),      # +2 coordinate channels
            nn.Conv2d(32, 48, 4, 2, 1), nn.ReLU(),
            nn.Conv2d(48, 64, 4, 2, 1), nn.ReLU(),
        )
        self.dens = nn.Sequential(
            nn.ConvTranspose2d(64, 48, 4, 2, 1), nn.ReLU(),
            nn.Conv2d(48, K, 3, 1, 1),
        )
        self.mhead = nn.Sequential(nn.Linear(64, 64), nn.ReLU(), nn.Linear(64, K*3))

    def forward(self, x):
        xc = torch.cat([x, COORD.expand(x.shape[0], -1, -1, -1)], 1)  # append coords
        f = self.enc(xc)                                    # (B,64,8,8)
        d = F.softplus(self.dens(f))                        # (B,K,16,16)
        d = F.interpolate(d, size=(H, W), mode="bilinear", align_corners=False)  # (B,K,H,W)
        p = self.mhead(f.mean((2, 3))).view(-1, self.K, 3)
        vx = torch.tanh(p[..., 0])*VMAX                     # (B,K)
        vy = torch.tanh(p[..., 1])*VMAX
        om = torch.tanh(p[..., 2])*OMMAX
        ux = vx[..., None, None] - om[..., None, None]*GY   # (B,K,H,W)
        uy = vy[..., None, None] + om[..., None, None]*GX
        sp = torch.sqrt(ux*ux + uy*uy) + EPS
        align = (COS_A[None, None, :, None, None]*ux[:, :, None] +
                 SIN_A[None, None, :, None, None]*uy[:, :, None]) / sp[:, :, None]  # (B,K,NDIR,H,W)
        w = torch.exp(KAPPA*align)
        w = w / w.amax(dim=2, keepdim=True)
        slots = d[:, :, None] * w                           # (B,K,NDIR,H,W)
        recon = slots.sum(1)
        params = torch.stack([vx, vy, om], -1)              # (B,K,3)
        return recon, slots, d, params


def train(steps=3500, bs=32, lr=1e-3):
    net = FlowSlotAE().to(DEV)
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


def corr(a, b):
    m = np.broadcast_to(APER[None].astype(bool), a.shape)
    a, b = a[m], b[m]; a = a-a.mean(); b = b-b.mean()
    return float((a*b).sum()/(np.sqrt((a*a).sum()*(b*b).sum())+1e-9))


@torch.no_grad()
def assign_and_sel(net, d, surfs):
    (eA, mA), (eB, mB) = surfs
    _, slots, _, params = net(torch.tensor(d[None], device=DEV))
    slots = slots[0].cpu().numpy(); P = params[0].cpu().numpy()   # (K,3)
    def pdist(p, m):
        return ((p[0]-m[0])/VMAX)**2 + ((p[1]-m[1])/VMAX)**2 + ((p[2]-m[2])/OMMAX)**2
    sA = int(np.argmin([pdist(P[k], mA) for k in range(net.K)]))
    sB = int(np.argmin([pdist(P[k], mB) for k in range(net.K)]))
    sel = 0.5*((corr(slots[sA], eA)-corr(slots[sA], eB)) + (corr(slots[sB], eB)-corr(slots[sB], eA)))
    return sel, slots, P, sA, sB


if __name__ == "__main__":
    os.makedirs(FIGS, exist_ok=True)
    print(f"device={DEV}  flow-slots K={K}")
    ckpt = os.path.join(HERE, "flow_slot.pt")
    if os.environ.get("RETRAIN", "0") == "0" and os.path.exists(ckpt):
        print("loading cached checkpoint (RETRAIN=1 to retrain)...")
        net = FlowSlotAE().to(DEV); net.load_state_dict(torch.load(ckpt, map_location=DEV))
    else:
        print("training flow-slot AE on rigid-motion (rotation+translation) stimuli...")
        net = train(); torch.save(net.state_dict(), ckpt)
    torch.set_grad_enabled(False)

    # reconstruction on counter-rotating fields
    rerr = []
    for _ in range(40):
        r = np.random.uniform(0.08, 0.14)
        d, surfs = make_pair((0, 0, +r), (0, 0, -r), noise=0.0)
        recon, *_ = net(torch.tensor(d[None], device=DEV)); recon = recon[0].cpu().numpy()
        rerr.append((((recon-d)**2)*APER[None]).sum()/(((d**2)*APER[None]).sum()+1e-9))
    print(f"\ncounter-rotation reconstruction frac-var: {np.mean(rerr):.3f}")

    print("\nfactoring selectivity, COUNTER-ROTATION, vs rotation magnitude:")
    for r in [0.04, 0.06, 0.08, 0.10, 0.14]:
        ss = []
        for _ in range(50):
            d, surfs = make_pair((0, 0, +r), (0, 0, -r), noise=0.0)
            ss.append(assign_and_sel(net, d, surfs)[0])
        print(f"   |omega| {r:.2f}   selectivity {np.mean(ss):+.3f} +/- {np.std(ss):.3f}")

    print("\nfactoring selectivity, same-sense rotation but different rate (control):")
    for r2 in [0.02, 0.06, 0.10]:
        ss = []
        for _ in range(40):
            d, surfs = make_pair((0, 0, 0.12), (0, 0, r2), noise=0.0)
            ss.append(assign_and_sel(net, d, surfs)[0])
        print(f"   omegas (0.12, {r2:.2f})   selectivity {np.mean(ss):+.3f} +/- {np.std(ss):.3f}")

    # figure: readouts on counter-rotation
    fig, ax = plt.subplots(3, 5, figsize=(13, 7.5))
    for j in range(3):
        np.random.seed(8000+j)
        r = np.random.uniform(0.09, 0.14)
        d, surfs = make_pair((0, 0, +r), (0, 0, -r), noise=0.0)
        (eA, mA), (eB, mB) = surfs
        _, slots, P, sA, sB = assign_and_sel(net, d, surfs)
        panels = [(d.sum(0), "input (both, counter-rot)"),
                  (eA.sum(0), f"surf A (CCW ω=+{r:.2f})"),
                  (slots[sA].sum(0), f"slot->A (ω={P[sA,2]:+.2f})"),
                  (eB.sum(0), f"surf B (CW ω=-{r:.2f})"),
                  (slots[sB].sum(0), f"slot->B (ω={P[sB,2]:+.2f})")]
        for i, (im, t) in enumerate(panels):
            ax[j, i].imshow(im*APER, cmap="magma"); ax[j, i].axis("off")
            if j == 0: ax[j, i].set_title(t, fontsize=8)
    fig.suptitle("Flow-slot AE: one-slot readout on two counter-rotating transparent fields", y=1.005)
    fig.tight_layout(); p1 = os.path.join(FIGS, "flow_slot_readout.png")
    fig.savefig(p1, dpi=115, bbox_inches="tight"); plt.close(fig)

    # figure: inferred flow fields (quiver) for one counter-rot example
    np.random.seed(8100)
    d, surfs = make_pair((0, 0, 0.12), (0, 0, -0.12), noise=0.0)
    _, slots, P, sA, sB = assign_and_sel(net, d, surfs)
    fig, ax = plt.subplots(1, 3, figsize=(12, 4))
    ax[0].imshow(d.sum(0)*APER, cmap="magma"); ax[0].set_title("input (both)"); ax[0].axis("off")
    step = 3; ys, xs = np.mgrid[2:H-2:step, 2:W-2:step]
    for idx, (slot, lab) in enumerate([(sA, "slot->A"), (sB, "slot->B")]):
        vx, vy, om = P[slot]
        u = vx - om*(ys-cy); v = vy + om*(xs-cx)
        ax[idx+1].imshow(slots[slot].sum(0)*APER, cmap="magma")
        ax[idx+1].quiver(xs, ys, u, -v, color="cyan", scale=30, width=0.005)
        ax[idx+1].set_title(f"{lab}  inferred ω={om:+.2f}"); ax[idx+1].axis("off")
    fig.suptitle("Inferred rigid-flow per slot (recovers opposite rotation sense)", y=1.02)
    fig.tight_layout(); p2 = os.path.join(FIGS, "flow_slot_field.png")
    fig.savefig(p2, dpi=115, bbox_inches="tight"); plt.close(fig)
    print("\nfigures ->", p1, "|", p2)
