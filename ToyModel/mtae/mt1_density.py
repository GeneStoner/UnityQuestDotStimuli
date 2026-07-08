"""
Density stress test of the trained one-MT-hypercolumn cued-swap model.

Vary dots per field on an L-position grid; the two fields sample positions
independently, so as density rises they increasingly OVERLAP in space (transparent).
At each density we train a fresh 50/50 (swap+no-swap) model with trainable V1 lateral
and measure whether cued > uncued survives -- especially on no-swap trials, which
require actually tracking the cued object (not the adaptation shortcut).

Run: /usr/bin/python3 mt1_density.py
"""
import os
import numpy as np
import torch
import torch.nn.functional as F
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import ps_train as P

torch.manual_seed(0); np.random.seed(0)
FIGS = os.path.join(P.HERE, "figs")


def gen(bs, n_dots, force=None):
    drive = np.zeros((bs, P.T, P.L, P.D), np.float32); cued = np.zeros(bs, np.int64)
    for b in range(bs):
        PA = np.random.choice(P.L, n_dots, replace=False)      # fields sampled independently
        PB = np.random.choice(P.L, n_dots, replace=False)      # -> overlap grows with density
        dA0 = np.random.randint(2); dB0 = 1-dA0
        swap = (np.random.rand() < 0.5) if force is None else force
        for t in range(P.T):
            dA, dB = (dA0, dB0) if (not swap or t < P.T_SWAP) else (dB0, dA0)
            drive[b, t, PA, dA] = 1.0
            if t >= P.T_ON:
                drive[b, t, PB, dB] = 1.0
        cued[b] = dA0 if swap else dB0
    return torch.tensor(drive, device=P.DEV), torch.tensor(cued, device=P.DEV)


def train_eval(n_dots, steps=2200):
    net = P.VMT(use_lat=True).to(P.DEV); opt = torch.optim.Adam(net.parameters(), lr=5e-3)
    for s in range(steps):
        d, c = gen(64, n_dots); loss = F.cross_entropy(net(d), c)
        opt.zero_grad(); loss.backward(); opt.step()
    out = {}
    for force, lab in [(True, "swap"), (False, "noswap")]:
        d, c = gen(3000, n_dots, force=force)
        with torch.no_grad():
            meff = net(d)
        idx = torch.arange(len(c))
        out[lab] = ((meff.argmax(1) == c).float().mean().item(),
                    meff[idx, c].mean().item(), meff[idx, 1-c].mean().item())
    return out


if __name__ == "__main__":
    os.makedirs(FIGS, exist_ok=True)
    Ns = [4, 8, 12, 16, 24, 32]
    dens = [n / P.L for n in Ns]
    swap_acc, noswap_acc, swap_ratio, noswap_ratio = [], [], [], []
    print(f"L={P.L} positions; overlap grows with density\n")
    for n in Ns:
        r = train_eval(n)
        sa, sc, su = r["swap"]; na, nc, nu = r["noswap"]
        swap_acc.append(sa); noswap_acc.append(na)
        swap_ratio.append(sc/max(su, 1e-3)); noswap_ratio.append(nc/max(nu, 1e-3))
        print(f"n_dots={n:2d} (density {n/P.L:.2f}):  swap acc {sa*100:3.0f}% ratio {sc/max(su,1e-3):.2f}x | "
              f"no-swap acc {na*100:3.0f}% ratio {nc/max(nu,1e-3):.2f}x")

    fig, ax = plt.subplots(1, 2, figsize=(12, 4.3))
    ax[0].plot(dens, np.array(swap_acc)*100, "-o", label="swap")
    ax[0].plot(dens, np.array(noswap_acc)*100, "-s", label="no-swap (needs tracking)")
    ax[0].axhline(50, color="gray", ls=":", lw=1); ax[0].set_ylim(0, 105)
    ax[0].set_xlabel("dot density (dots per field / positions)"); ax[0].set_ylabel("cued-correct %"); ax[0].legend(); ax[0].set_title("Cued-swap accuracy vs density")
    ax[1].plot(dens, swap_ratio, "-o", label="swap"); ax[1].plot(dens, noswap_ratio, "-s", label="no-swap")
    ax[1].axhline(1.0, color="gray", ls=":", lw=1)
    ax[1].set_xlabel("dot density"); ax[1].set_ylabel("cued/uncued response ratio"); ax[1].legend(); ax[1].set_title("Cueing magnitude vs density")
    fig.tight_layout(); p = os.path.join(FIGS, "mt1_density.png")
    fig.savefig(p, dpi=115, bbox_inches="tight"); plt.close(fig)
    print("\nfigure ->", p)
