"""Visualize the 1-D cued-swap stimuli so density (and the disjoint-vs-overlap issue)
is concrete: position (y) x time (x) raster, colored by motion direction."""
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
import ps_train as P

FIGS = os.path.join(P.HERE, "figs")


def make(n, disjoint=True, seed=1):
    rng = np.random.RandomState(seed)
    if disjoint:
        PA = rng.choice(P.L, n, replace=False)
        PB = rng.choice(np.setdiff1d(np.arange(P.L), PA), n, replace=False)
    else:
        PA = rng.choice(P.L, n, replace=False)
        PB = rng.choice(P.L, n, replace=False)      # independent -> may overlap
    dA0, dB0, drive = 0, 1, np.zeros((P.T, P.L, P.D))
    for t in range(P.T):
        dA, dB = (dA0, dB0) if t < P.T_SWAP else (dB0, dA0)   # swap at T_SWAP
        drive[t, PA, dA] = 1
        if t >= P.T_ON:
            drive[t, PB, dB] = 1
    return (drive[:, :, 0] > 0)*1 + (drive[:, :, 1] > 0)*2      # 0 empty,1 right,2 left,3 both


cmap = ListedColormap(["#111111", "#d1495b", "#3f88c5", "#8e44ad"])  # empty, right, left, both
panels = [(4, True, "DISJOINT, density 0.25 (4 dots/field)"),
          (8, True, "DISJOINT, density 0.50 (8 dots/field)"),
          (16, True, "DISJOINT, density 1.00 (16 dots/field, full)"),
          (8, False, "OVERLAP, density 0.50 (independent -> purple = both motions at one spot)")]

fig, ax = plt.subplots(len(panels), 1, figsize=(9, 10))
for a, (n, disj, title) in zip(ax, panels):
    r = make(n, disj)
    a.imshow(r.T, aspect="auto", cmap=cmap, vmin=0, vmax=3, interpolation="nearest")
    a.axvline(P.T_ON-0.5, color="w", ls=":", lw=1.2); a.axvline(P.T_SWAP-0.5, color="w", ls="--", lw=1.2)
    a.text(P.T_ON, -1.5, "delayed onset", color="w", fontsize=8, ha="center")
    a.text(P.T_SWAP, -1.5, "swap", color="w", fontsize=8, ha="center")
    a.set_title(title, fontsize=10); a.set_ylabel("position"); a.set_yticks([0, P.L-1])
ax[-1].set_xlabel("time")
fig.suptitle("Cued-swap stimuli (red=rightward, blue=leftward, purple=both).  Field A from t=0; field B (cued) delayed; motions swap.", fontsize=10)
fig.tight_layout(rect=[0, 0, 1, 0.98])
p = os.path.join(FIGS, "stim_viz.png")
fig.savefig(p, dpi=115, bbox_inches="tight"); plt.close(fig)
print("figure ->", p)
