"""
Recurrent V1<->MT scaffold — STABILITY TEST ONLY (no training yet).

Two retinotopic direction-hypercolumn levels with all three connection types:
  - feedforward  V1 -> MT   (downsampling conv)
  - feedback     MT -> V1   (upsampling conv)
  - lateral      V1 -> V1  and  MT -> MT   (same-scale conv)
Dynamics: leaky settling with Heeger-style divisive normalization as the
stabilizer (also our future density/gain-control lever). Weights are untrained
(small random) — the ONLY question here is: does it settle to a stable fixed
point, and over what recurrent-gain range?

Run: /usr/bin/python3 recurrent_scaffold.py
"""
import os
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

torch.manual_seed(0); np.random.seed(0)
DEV = "mps" if torch.backends.mps.is_available() else "cpu"
HERE = os.path.dirname(os.path.abspath(__file__))
FIGS = os.path.join(HERE, "figs")

# ---- geometry -------------------------------------------------------------
H = W = 32
NDIR = 8                       # V1 direction hypercolumn size
MT_H = MT_W = 16               # MT retinotopic (2x coarser)
NDIR_MT = 8
R = 13.0
SIG_SPACE = 0.9
KAPPA = 2.5
CHAN_DIR = np.arange(NDIR) * 2 * np.pi / NDIR

cx = cy = (H - 1) / 2.0
yy, xx = np.mgrid[0:H, 0:W]
APER = ((xx - cx) ** 2 + (yy - cy) ** 2) <= R ** 2


def v1_drive(n_per=30):
    """Static V1 direction-hypercolumn drive from a 2-surface motion stimulus."""
    def surf():
        th = np.random.rand() * 2 * np.pi
        pts = []
        while len(pts) < n_per:
            p = np.random.rand(2) * [W, H]
            if (p[0]-cx)**2 + (p[1]-cy)**2 <= R**2:
                pts.append(p)
        return np.array(pts, np.float32), th
    energy = np.zeros((NDIR, H, W), np.float32)
    for _ in range(2):
        pos, th = surf()
        dx = xx[None]-pos[:,0,None,None]; dy = yy[None]-pos[:,1,None,None]
        blob = np.exp(-(dx*dx+dy*dy)/(2*SIG_SPACE**2))
        wdir = np.exp(KAPPA*np.cos(th-CHAN_DIR)); wdir/=wdir.max()
        energy += np.einsum("d,mhw->dhw", wdir, blob).astype(np.float32)
    energy *= APER[None]
    return torch.tensor(energy[None], device=DEV)          # (1,NDIR,H,W)


def divnorm(r, sigma=1.0):
    """Heeger-style divisive normalization: bound activity -> stabilizer."""
    r = F.relu(r)
    pool = r.sum(1, keepdim=True)
    pool = F.avg_pool2d(pool, 3, stride=1, padding=1)
    return r / (sigma + pool)


class RecurrentVMT(nn.Module):
    def __init__(self, wscale=0.2):
        super().__init__()
        self.ff  = nn.Conv2d(NDIR, NDIR_MT, 5, stride=2, padding=2)          # V1->MT  32->16
        self.fb  = nn.ConvTranspose2d(NDIR_MT, NDIR, 6, stride=2, padding=2) # MT->V1  16->32
        self.lv  = nn.Conv2d(NDIR, NDIR, 5, padding=2)                       # V1->V1
        self.lm  = nn.Conv2d(NDIR_MT, NDIR_MT, 5, padding=2)                 # MT->MT
        for m in [self.ff, self.fb, self.lv, self.lm]:
            m.weight.data *= wscale
            if m.bias is not None:
                m.bias.data.zero_()

    @torch.no_grad()
    def settle(self, s, gain=1.0, alpha=0.25, n_steps=60, sigma=1.0):
        """Leaky settling. Returns final (v,m) and per-step relative deltas."""
        v = torch.zeros_like(s)
        m = torch.zeros(1, NDIR_MT, MT_H, MT_W, device=s.device)
        deltas, acts = [], []
        for _ in range(n_steps):
            Iv = s + gain * (self.lv(v) + self.fb(m))
            Im = gain * (self.ff(v) + self.lm(m))
            v_t = divnorm(Iv, sigma); m_t = divnorm(Im, sigma)
            dv = v + alpha * (v_t - v); dm = m + alpha * (m_t - m)
            step = ((dv - v).norm() / (v.norm() + 1e-6)).item()
            v, m = dv, dm
            deltas.append(step); acts.append(v.max().item())
        return v, m, np.array(deltas), np.array(acts)


if __name__ == "__main__":
    os.makedirs(FIGS, exist_ok=True)
    print(f"device={DEV}  V1={NDIR}x{H}x{W}  MT={NDIR_MT}x{MT_H}x{MT_W}")
    net = RecurrentVMT().to(DEV)
    s = v1_drive()

    # gain sweep: where does it settle vs blow up / oscillate?
    print("\ngain sweep (converged = final rel-delta < 1e-3, bounded activity):")
    gains = [0.5, 1.0, 1.5, 2.0, 3.0, 4.0]
    curves = {}
    for g in gains:
        v, m, d, a = net.settle(s, gain=g)
        curves[g] = (d, a)
        conv = d[-1] < 1e-3 and np.isfinite(a[-1]) and a[-1] < 1e3
        osc = d[-1] > 1e-3 and abs(d[-1] - d[-5]) < 0.2 * d[-1]  # plateau, not settling
        tag = "CONVERGED" if conv else ("blow-up" if a[-1] > 1e3 else "not-settled")
        print(f"  gain {g:.1f}:  final delta {d[-1]:.2e}   max act {a[-1]:.2f}   -> {tag}")

    # figure: convergence curves + settled states at a stable gain
    gstable = 1.0
    v, m, d, a = net.settle(s, gain=gstable)
    fig, ax = plt.subplots(1, 4, figsize=(15, 3.4))
    for g in gains:
        ax[0].semilogy(curves[g][0], label=f"gain {g}")
    ax[0].set_title("convergence (rel. Δ per step)"); ax[0].set_xlabel("iteration")
    ax[0].set_ylabel("‖Δv‖/‖v‖"); ax[0].legend(fontsize=7); ax[0].axhline(1e-3, color="gray", ls=":")
    ax[1].imshow((s[0].cpu().numpy()*APER[None]).sum(0), cmap="magma"); ax[1].set_title("V1 drive (Σ dir)"); ax[1].axis("off")
    ax[2].imshow((v[0].cpu().numpy()*APER[None]).sum(0), cmap="magma"); ax[2].set_title(f"settled V1 (gain {gstable})"); ax[2].axis("off")
    ax[3].imshow(m[0].cpu().numpy().sum(0), cmap="magma"); ax[3].set_title("settled MT (Σ dir)"); ax[3].axis("off")
    fig.tight_layout(); p = os.path.join(FIGS, "recurrent_settle.png")
    fig.savefig(p, dpi=115, bbox_inches="tight"); plt.close(fig)
    print("\nfigure ->", p)
