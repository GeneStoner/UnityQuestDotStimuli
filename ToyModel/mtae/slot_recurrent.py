"""
Fold slots INTO the recurrent V1<->MT scaffold.

MT is now OBJECT-FACTORED: K competing slots, each = a predicted density map (x)
a direction profile. The network SETTLES: at each step it (re)infers the slots
from the current V1 estimate, the slots project back to V1 as feedback, and V1
relaxes toward reconciling its drive with that top-down slot reconstruction.
This keeps the recurrent dynamics + feedback (hence a cueing TIME COURSE) while
giving the factored code that buys for-free selection.

Cueing = boost one slot's contribution to the feedback and watch V1 settle.

Run:            /usr/bin/python3 slot_recurrent.py
Retrain:  RETRAIN=1 /usr/bin/python3 slot_recurrent.py
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
K = 2
GAIN, ALPHA, SIGMA, NSTEP = 1.0, 0.4, 1.0, 15


class SlotRecurrent(nn.Module):
    def __init__(self, K=K):
        super().__init__()
        self.K = K
        self.enc = nn.Sequential(
            nn.Conv2d(NDIR, 32, 3, 1, 1), nn.ReLU(),
            nn.Conv2d(32, 48, 4, 2, 1), nn.ReLU(),   # 32->16
            nn.Conv2d(48, 64, 4, 2, 1), nn.ReLU(),   # 16->8
        )
        self.dens = nn.Conv2d(64, K, 3, 1, 1)        # INDEPENDENT per-slot density (like slot_ae)
        self.dirhead = nn.Sequential(nn.Linear(64, 64), nn.ReLU(), nn.Linear(64, K*NDIR))

    def slots(self, v):
        f = self.enc(v)
        d = F.softplus(F.interpolate(self.dens(f), size=(H, W), mode="bilinear", align_corners=False))  # (B,K,H,W)
        w = F.softmax(self.dirhead(f.mean((2, 3))).view(-1, self.K, NDIR), dim=2)  # (B,K,NDIR)
        return d, w

    def settle(self, s, gain=GAIN, alpha=ALPHA, n_steps=NSTEP, sigma=SIGMA,
               cue_slot=None, cue=0.0, record=None):
        v = s.clone()
        traj = []
        for t in range(n_steps):
            d, w = self.slots(v)
            pred_k = d[:, :, None] * w[:, :, :, None, None]        # (B,K,NDIR,H,W)
            g = torch.ones(v.shape[0], self.K, device=v.device)
            if cue_slot is not None:
                g[:, cue_slot] = 1.0 + cue
            pred = (g[:, :, None, None, None] * pred_k).sum(1)      # (B,NDIR,H,W)
            v = v + alpha * (RS.divnorm(F.relu(s + gain*pred), sigma) - v)
            if record is not None:
                traj.append(record(v, pred_k))
        return v, self.slots(v), traj


def settle_recon(net, s, **kw):
    v, (d, w), _ = net.settle(s, **kw)
    pred_k = d[:, :, None] * w[:, :, :, None, None]
    return v, pred_k, d, w


def batch(bs):
    dg, cl = [], []
    for _ in range(bs):
        a, b, _ = HA.make_sample(drop=0.25, occ_r=0.0, noise=0.05)
        dg.append(a); cl.append(b)
    return torch.tensor(np.stack(dg), device=DEV), torch.tensor(np.stack(cl), device=DEV)


def train(steps=3000, bs=24, lr=1e-3):
    net = SlotRecurrent().to(DEV)
    opt = torch.optim.Adam(net.parameters(), lr=lr)
    t0 = time.time()
    for s in range(steps):
        dg, cl = batch(bs)
        v, pred_k, d, w = settle_recon(net, dg)
        recon = pred_k.sum(1)                      # slots ARE the reconstruction -> gradient flows
        loss = (((recon - cl)**2) * APER_T).mean()
        opt.zero_grad(); loss.backward()
        torch.nn.utils.clip_grad_norm_(net.parameters(), 5.0)
        opt.step()
        if s % 300 == 0 or s == steps-1:
            print(f"  step {s:4d}  loss {loss.item():.5f}  ({time.time()-t0:.0f}s)")
    return net


def corr(a, b):
    m = np.broadcast_to(APER[None].astype(bool), a.shape)
    a, b = a[m], b[m]; a = a-a.mean(); b = b-b.mean()
    return float((a*b).sum()/(np.sqrt((a*a).sum()*(b*b).sum())+1e-9))


@torch.no_grad()
def slot_dirs(w):  # circular-mean direction of each slot
    return np.angle((w*np.exp(1j*CHAN_DIR)[None]).sum(1))


@torch.no_grad()
def eval_factor(net, n=80):
    sels = []
    for _ in range(n):
        d, c, surfs = HA.make_sample(drop=0.0, occ_r=0.0, noise=0.0)
        (eA, tA), (eB, tB) = surfs
        s = torch.tensor(d[None], device=DEV)
        _, pred_k, dd, w = settle_recon(net, s, n_steps=25)
        pk = pred_k[0].cpu().numpy(); wk = w[0].cpu().numpy()
        sd = slot_dirs(wk); ad = lambda a, b: abs((a-b+np.pi) % (2*np.pi)-np.pi)
        sA = int(np.argmin([ad(sd[k], tA) for k in range(net.K)]))
        sB = int(np.argmin([ad(sd[k], tB) for k in range(net.K)]))
        sels.append(0.5*((corr(pk[sA], eA)-corr(pk[sA], eB)) + (corr(pk[sB], eB)-corr(pk[sB], eA))))
    return float(np.mean(sels)), float(np.std(sels))


@torch.no_grad()
def cueing_timecourse(net, n=60, cue=1.5, n_steps=30):
    """Dynamic cueing: boost the slot matching surface A, record V1 enhancement of A over settling."""
    curves = []
    for _ in range(n):
        d, c, surfs = HA.make_sample(drop=0.0, occ_r=0.0, noise=0.0)
        (eA, tA), (eB, tB) = surfs
        s = torch.tensor(d[None], device=DEV)
        _, (dd, w), _ = net.settle(s, n_steps=6)   # find which slot is A
        sd = slot_dirs(w[0].cpu().numpy()); ad = lambda a, b: abs((a-b+np.pi) % (2*np.pi)-np.pi)
        sA = int(np.argmin([ad(sd[k], tA) for k in range(net.K)]))
        rec = lambda v, pk: corr(v[0].cpu().numpy(), eA) - corr(v[0].cpu().numpy(), eB)
        _, _, traj = net.settle(s, cue_slot=sA, cue=cue, n_steps=n_steps, record=rec)
        _, _, traj0 = net.settle(s, cue_slot=None, cue=0.0, n_steps=n_steps, record=rec)
        curves.append((np.array(traj), np.array(traj0)))
    cued = np.mean([c[0] for c in curves], 0); base = np.mean([c[1] for c in curves], 0)
    return cued, base


if __name__ == "__main__":
    os.makedirs(FIGS, exist_ok=True)
    print(f"device={DEV}  recurrent slots K={K}  settle={NSTEP}")
    ckpt = os.path.join(HERE, "slot_recurrent.pt")
    if os.environ.get("RETRAIN", "0") == "0" and os.path.exists(ckpt):
        print("loading cached checkpoint (RETRAIN=1 to retrain)...")
        net = SlotRecurrent().to(DEV); net.load_state_dict(torch.load(ckpt, map_location=DEV))
    else:
        print("training recurrent slot AE (denoising via settling)...")
        net = train(); torch.save(net.state_dict(), ckpt)
    torch.set_grad_enabled(False)

    sel, sd = eval_factor(net)
    print(f"\nfactoring selectivity (per-slot readout, recurrent): {sel:+.3f} +/- {sd:.3f}")
    cued, base = cueing_timecourse(net)
    print(f"dynamic cueing enhancement (final step): cued {cued[-1]:+.3f}  baseline {base[-1]:+.3f}")

    # figure: cueing time course
    fig, ax = plt.subplots(1, 2, figsize=(11, 4))
    ax[0].plot(cued, "-o", ms=3, label="cue surface A"); ax[0].plot(base, "-s", ms=3, label="no cue")
    ax[0].axhline(0, color="gray", lw=0.8); ax[0].set_xlabel("settling step")
    ax[0].set_ylabel("V1 enhancement of A  (corr_A − corr_B)"); ax[0].legend(); ax[0].set_title("Dynamic cueing time course")
    # slot readout example
    np.random.seed(9001)
    d, c, surfs = HA.make_sample(drop=0.0, occ_r=0.0, noise=0.0)
    (eA, tA), (eB, tB) = surfs
    _, pred_k, dd, w = settle_recon(net, torch.tensor(d[None], device=DEV), n_steps=25)
    pk = pred_k[0].cpu().numpy(); sd2 = slot_dirs(w[0].cpu().numpy())
    ad = lambda a, b: abs((a-b+np.pi) % (2*np.pi)-np.pi)
    sA = int(np.argmin([ad(sd2[k], tA) for k in range(K)])); sB = 1-sA
    ax[1].axis("off")
    sub = fig.add_axes([0.55, 0.1, 0.4, 0.8]); sub.axis("off")
    combo = np.concatenate([d.sum(0), pk[sA].sum(0), pk[sB].sum(0)], axis=1)
    sub.imshow(combo*np.concatenate([APER, APER, APER], 1), cmap="magma")
    sub.set_title("input  |  slot→A  |  slot→B", fontsize=10)
    fig.tight_layout(); p = os.path.join(FIGS, "slot_recurrent.png")
    fig.savefig(p, dpi=115, bbox_inches="tight"); plt.close(fig)
    print("figure ->", p)
