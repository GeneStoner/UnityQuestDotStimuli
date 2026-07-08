"""
Slot autoencoder (fork a): does an OBJECT-FACTORED bottleneck give object-based
attention for free, where a distributed MT map did not?

Transparent surfaces overlap in space, so slots cannot compete spatially -- they
factor by VELOCITY. V1 motion energy is separable (direction-profile (x) spatial
density), and each surface is exactly one such component. So each slot = a
separable component: a global direction distribution w_k(dir) and a spatial
density map d_k(x,y). K=2 slots compete to reconstruct the scene:
    recon(dir,x,y) = Σ_k d_k(x,y) * w_k(dir)
No cue, no attention training. "Attending surface k" = reading out slot k alone.
Test: do slots factor by surface on FRESH stimuli, and does one-slot readout
selectively recover one surface?

Run:            /usr/bin/python3 slot_ae.py
Retrain:  RETRAIN=1 /usr/bin/python3 slot_ae.py
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
CHAN_DIR = RS.CHAN_DIR
APER_T = torch.tensor(APER[None, None].astype(np.float32), device=DEV)
K = 2   # slots


class SlotAE(nn.Module):
    def __init__(self, K=K):
        super().__init__()
        self.K = K
        self.enc = nn.Sequential(
            nn.Conv2d(NDIR, 32, 3, 1, 1), nn.ReLU(),
            nn.Conv2d(32, 48, 4, 2, 1), nn.ReLU(),     # 32->16
            nn.Conv2d(48, 64, 4, 2, 1), nn.ReLU(),     # 16->8
        )
        self.dens = nn.Sequential(                     # density maps d_k at 16x16
            nn.ConvTranspose2d(64, 48, 4, 2, 1), nn.ReLU(),  # 8->16
            nn.Conv2d(48, K, 3, 1, 1),
        )
        self.dirhead = nn.Sequential(nn.Linear(64, 64), nn.ReLU(), nn.Linear(64, K*NDIR))

    def forward(self, x):
        f = self.enc(x)                                # (B,64,8,8)
        d = F.softplus(self.dens(f))                   # (B,K,16,16) >=0
        d = F.interpolate(d, size=(H, W), mode="bilinear", align_corners=False)  # (B,K,H,W)
        g = f.mean((2, 3))                             # (B,64)
        w = self.dirhead(g).view(-1, self.K, NDIR)
        w = F.softmax(w, dim=2)                        # (B,K,NDIR) direction profile per slot
        slots = torch.einsum("bkhw,bkd->bkdhw", d, w)  # (B,K,NDIR,H,W) per-slot recon
        recon = slots.sum(1)                           # (B,NDIR,H,W)
        return recon, slots, d, w


def batch(bs):
    dg, cl = [], []
    for _ in range(bs):
        d, c, _ = HA.make_sample(drop=0.0, occ_r=0.0, noise=0.05)
        dg.append(d); cl.append(c)
    return torch.tensor(np.stack(dg), device=DEV), torch.tensor(np.stack(cl), device=DEV)


def train(steps=3000, bs=32, lr=1e-3):
    net = SlotAE().to(DEV)
    opt = torch.optim.Adam(net.parameters(), lr=lr)
    t0 = time.time()
    for s in range(steps):
        x, c = batch(bs)
        recon, *_ = net(x)
        loss = (((recon - c)**2) * APER_T).mean()
        opt.zero_grad(); loss.backward(); opt.step()
        if s % 300 == 0 or s == steps-1:
            print(f"  step {s:4d}  loss {loss.item():.5f}  ({time.time()-t0:.0f}s)")
    return net


def corr(a, b):
    m = np.broadcast_to(APER[None].astype(bool), a.shape)
    a, b = a[m], b[m]; a = a-a.mean(); b = b-b.mean()
    return float((a*b).sum()/(np.sqrt((a*a).sum()*(b*b).sum())+1e-9))


@torch.no_grad()
def evaluate(net, n_trials=80):
    """Assign each slot to the nearest surface by direction; measure per-slot selectivity."""
    sels, recon_err = [], []
    for _ in range(n_trials):
        d, c, surfs = HA.make_sample(drop=0.0, occ_r=0.0, noise=0.0)
        (eA, tA), (eB, tB) = surfs
        x = torch.tensor(d[None], device=DEV)
        recon, slots, dens, w = net(x)
        recon = recon[0].cpu().numpy(); slots = slots[0].cpu().numpy()
        recon_err.append((((recon-c)**2)*APER[None]).sum()/(((c**2)*APER[None]).sum()+1e-9))
        # slot preferred direction (circular mean of w_k over channels)
        wk = w[0].cpu().numpy()
        slot_dir = np.angle((wk*np.exp(1j*CHAN_DIR)[None]).sum(1))
        # assign slot->surface by min angular distance
        def adist(a, b): return abs((a-b+np.pi) % (2*np.pi) - np.pi)
        sA = int(np.argmin([adist(slot_dir[k], tA) for k in range(net.K)]))
        sB = int(np.argmin([adist(slot_dir[k], tB) for k in range(net.K)]))
        selA = corr(slots[sA], eA) - corr(slots[sA], eB)
        selB = corr(slots[sB], eB) - corr(slots[sB], eA)
        sels.append(0.5*(selA+selB))
    return float(np.mean(sels)), float(np.std(sels)), float(np.mean(recon_err))


@torch.no_grad()
def fig_slots(net, path, seed0=5000, n=4):
    fig, ax = plt.subplots(n, 5, figsize=(13, 2.5*n))
    for j in range(n):
        np.random.seed(seed0+j)
        d, c, surfs = HA.make_sample(drop=0.0, occ_r=0.0, noise=0.0)
        (eA, tA), (eB, tB) = surfs
        x = torch.tensor(d[None], device=DEV)
        recon, slots, dens, w = net(x)
        slots = slots[0].cpu().numpy()
        wk = w[0].cpu().numpy()
        slot_dir = np.angle((wk*np.exp(1j*CHAN_DIR)[None]).sum(1))
        def adist(a,b): return abs((a-b+np.pi)%(2*np.pi)-np.pi)
        sA = int(np.argmin([adist(slot_dir[k], tA) for k in range(net.K)]))
        sB = int(np.argmin([adist(slot_dir[k], tB) for k in range(net.K)]))
        panels = [(c.sum(0), "input (both)"),
                  (eA.sum(0), f"surf A ({np.degrees(tA):.0f}°)"),
                  (slots[sA].sum(0), f"slot->A ({np.degrees(slot_dir[sA]):.0f}°)"),
                  (eB.sum(0), f"surf B ({np.degrees(tB):.0f}°)"),
                  (slots[sB].sum(0), f"slot->B ({np.degrees(slot_dir[sB]):.0f}°)")]
        for i,(im,t) in enumerate(panels):
            ax[j,i].imshow(im*APER, cmap="magma"); ax[j,i].axis("off")
            if j==0: ax[j,i].set_title(t, fontsize=9)
    fig.suptitle("Slot AE: one-slot readout vs surface truth (fresh stimuli)", y=1.005)
    fig.tight_layout(); fig.savefig(path, dpi=115, bbox_inches="tight"); plt.close(fig)


if __name__ == "__main__":
    os.makedirs(FIGS, exist_ok=True)
    print(f"device={DEV}  slots K={K}")
    ckpt = os.path.join(HERE, "slot_ae.pt")
    if os.environ.get("RETRAIN","0")=="0" and os.path.exists(ckpt):
        print("loading cached checkpoint (RETRAIN=1 to retrain)...")
        net = SlotAE().to(DEV); net.load_state_dict(torch.load(ckpt, map_location=DEV))
    else:
        print("training slot AE (reconstruction only)...")
        net = train(); torch.save(net.state_dict(), ckpt)

    sel, sd, rerr = evaluate(net)
    print(f"held-out reconstruction frac-var: {rerr:.3f}")
    print(f"one-slot readout selectivity (NO attention training): {sel:+.3f} +/- {sd:.3f}")
    print("  (compare head A recurrent AE cueing ~ +0.10; chance = 0)")
    fig_slots(net, os.path.join(FIGS, "slot_readout.png"))
    print("figure -> slot_readout.png")
