"""
Leverage check for the recurrent V1<->MT scaffold.

Stability milestone showed the net settles, but divisive normalization dominated
and the settled V1 ~= the feedforward drive (feedback/lateral near-inert). Before
training we must confirm the recurrent pathway CAN measurably reshape the fixed
point when its weights are meaningful.

Here we install biologically-structured (not trained) kernels:
  - feedforward V1->MT : like-to-like direction pooling
  - feedback   MT->V1 : like-to-like, spatial Gaussian spread
  - lateral    V1->V1, MT->MT : same-direction cooperation (Gaussian, no self-center)
then sweep recurrent gain and measure how far the settled V1 departs from the
gain=0 baseline (v0 = divnorm(drive)), and whether it stays stable.

Run: /usr/bin/python3 leverage_check.py
"""
import os
import numpy as np
import torch
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import recurrent_scaffold as RS

torch.set_grad_enabled(False)
NDIR, NDIR_MT = RS.NDIR, RS.NDIR_MT
APER = RS.APER


def gauss2d(k, sig, zero_center=False):
    ax = np.arange(k) - (k - 1) / 2
    g = np.exp(-(ax[:, None] ** 2 + ax[None, :] ** 2) / (2 * sig ** 2)).astype(np.float32)
    if zero_center:
        g[k // 2, k // 2] = 0.0
    return g / g.sum()


def install_structured(net):
    """Overwrite the random weights with like-to-like / cooperative kernels."""
    # feedforward V1->MT : (NDIR_MT, NDIR, 5,5), like-to-like pooling
    g = gauss2d(5, 1.0)
    w = np.zeros((NDIR_MT, NDIR, 5, 5), np.float32)
    for k in range(min(NDIR, NDIR_MT)): w[k, k] = g
    net.ff.weight.data = torch.tensor(w, device=RS.DEV); net.ff.bias.data.zero_()
    # feedback MT->V1 : ConvTranspose2d weight (NDIR_MT, NDIR, 6,6), like-to-like + spread
    g = gauss2d(6, 1.3)
    w = np.zeros((NDIR_MT, NDIR, 6, 6), np.float32)
    for k in range(min(NDIR, NDIR_MT)): w[k, k] = g
    net.fb.weight.data = torch.tensor(w, device=RS.DEV); net.fb.bias.data.zero_()
    # lateral V1->V1 : (NDIR, NDIR, 5,5) same-direction cooperation, no self-center
    g = gauss2d(5, 1.2, zero_center=True)
    w = np.zeros((NDIR, NDIR, 5, 5), np.float32)
    for k in range(NDIR): w[k, k] = g
    net.lv.weight.data = torch.tensor(w, device=RS.DEV); net.lv.bias.data.zero_()
    # lateral MT->MT
    w = np.zeros((NDIR_MT, NDIR_MT, 5, 5), np.float32)
    for k in range(NDIR_MT): w[k, k] = g
    net.lm.weight.data = torch.tensor(w, device=RS.DEV); net.lm.bias.data.zero_()


def reshape_pct(v, v0):
    m = np.broadcast_to(APER[None], v.shape)
    a = (v - v0)[m]; b = v0[m]
    return 100.0 * np.linalg.norm(a) / (np.linalg.norm(b) + 1e-9)


if __name__ == "__main__":
    net = RS.RecurrentVMT().to(RS.DEV)
    install_structured(net)
    s = RS.v1_drive()

    v0, _, d0, _ = net.settle(s, gain=0.0)          # baseline = divnorm(drive)
    v0 = v0[0].cpu().numpy()

    print("recurrent leverage: departure of settled V1 from gain=0 baseline\n")
    print("  sigma=1.0:")
    gains = [0.5, 1.0, 2.0, 4.0, 8.0]
    reshapes = {}
    for g in gains:
        v, mt, d, a = net.settle(s, gain=g, sigma=1.0)
        vnp = v[0].cpu().numpy()
        rp = reshape_pct(vnp, v0)
        reshapes[g] = rp
        conv = d[-1] < 1e-3 and a[-1] < 1e3
        print(f"    gain {g:>4.1f}:  reshape {rp:6.1f}%   final delta {d[-1]:.1e}   max act {a[-1]:.2f}   {'stable' if conv else 'UNSTABLE'}")

    print("  sigma lever (reshape% at gain=4.0):")
    for sig in [0.5, 1.0, 2.0]:
        v, _, d, a = net.settle(s, gain=4.0, sigma=sig)
        rp = reshape_pct(v[0].cpu().numpy(), v0)
        conv = d[-1] < 1e-3 and a[-1] < 1e3
        print(f"    sigma {sig:>4.1f}:  reshape {rp:6.1f}%   {'stable' if conv else 'UNSTABLE'}")

    # figure at a gain with clear-but-stable reshaping
    gshow = 4.0
    v, mt, d, a = net.settle(s, gain=gshow, sigma=1.0)
    vnp = v[0].cpu().numpy()
    diff = (vnp - v0)
    fig, ax = plt.subplots(1, 4, figsize=(15, 3.4))
    ax[0].plot(gains, [reshapes[g] for g in gains], "o-")
    ax[0].set_title("reshape vs recurrent gain"); ax[0].set_xlabel("gain"); ax[0].set_ylabel("% departure from baseline")
    ax[1].imshow((v0 * APER[None]).sum(0), cmap="magma"); ax[1].set_title("baseline settled V1 (gain 0)"); ax[1].axis("off")
    ax[2].imshow((vnp * APER[None]).sum(0), cmap="magma"); ax[2].set_title(f"settled V1 (gain {gshow})"); ax[2].axis("off")
    vlim = np.abs((diff * APER[None]).sum(0)).max()
    ax[3].imshow((diff * APER[None]).sum(0), cmap="coolwarm", vmin=-vlim, vmax=vlim)
    ax[3].set_title("difference (recurrence effect)"); ax[3].axis("off")
    fig.tight_layout(); p = os.path.join(RS.FIGS, "leverage.png")
    fig.savefig(p, dpi=115, bbox_inches="tight"); plt.close(fig)
    print("\nfigure ->", p)
