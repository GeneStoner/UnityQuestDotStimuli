"""Animated faithful stimulus + V1/MT activations, SWAP vs NO-SWAP side by side.
Top row = swap, bottom = no-swap. Left = V1 (dots; size proportional to gain, so the
adapted/uncued field's dots are smaller); right = MT 4-direction hypercolumn, with the
up/down TRANSLATION DETECTOR channels in gold."""
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import real_stim as S

FIGS = S.FIGS
R = S.R_AP
DIRLAB = ["R", "U", "L", "D"]

np.random.seed(1); V1s, MTs, trajS = S.simulate(60, "cued", S.UP, swap=True, keep_traj=True)
np.random.seed(1); V1n, MTn, trajN = S.simulate(60, "cued", S.UP, swap=False, keep_traj=True)
mtmax = max(MTs.max(), MTn.max())*1.05

fig, ax = plt.subplots(2, 2, figsize=(11, 9))
rows = []
for r, (traj, MT, tag) in enumerate([(trajS, MTs, "SWAP"), (trajN, MTn, "NO-SWAP")]):
    axsc, axbar = ax[r, 0], ax[r, 1]
    axsc.set_xlim(-R-1, R+2); axsc.set_ylim(-R-1, R+5); axsc.set_aspect("equal"); axsc.axis("off")
    axsc.add_patch(plt.Circle((0, 0), R, fill=False, color="gray", lw=1))
    axsc.set_title(f"{tag} — V1 (dot size ∝ gain; big = un-adapted/cued)", fontsize=10)
    sA = axsc.scatter([], [], c="#d1495b"); sB = axsc.scatter([], [], c="#3f88c5")
    bars = axbar.bar(range(4), [0]*4, color=["#888", "#e0a800", "#888", "#e0a800"])
    axbar.set_xticks(range(4)); axbar.set_xticklabels(DIRLAB); axbar.set_ylim(0, mtmax)
    axbar.set_title(f"{tag} — MT hypercolumn (gold = up/down detector)", fontsize=10)
    rows.append((traj, MT, sA, sB, bars))
sup = fig.suptitle("")


def update(t):
    ph = ("field A only" if t < S.T_ON else
          ">>> BRIEF ORTHOGONAL TRANSLATION (cued field, 50% coh) <<<" if S.T_TEST0 <= t < S.T_TEST1 else
          "two fields, opposite motion")
    sup.set_text(f"frame {t}    {ph}\nred = A (continuous) · blue = B (cued, delayed)")
    for (traj, MT, sA, sB, bars) in rows:
        posA, posB, gA, gB, testing = traj[t]
        sA.set_offsets(posA); sA.set_sizes(8 + 70*gA)
        if len(posB):
            sB.set_offsets(posB); sB.set_sizes(8 + 70*gB)
        else:
            sB.set_offsets(np.empty((0, 2)))
        for b, h in zip(bars, MT[t]):
            b.set_height(h)
    return []


ani = animation.FuncAnimation(fig, update, frames=S.T, interval=130, blit=False)
out = os.path.join(FIGS, "real_anim.gif")
ani.save(out, writer=animation.PillowWriter(fps=8))
plt.close(fig)
print("movie ->", out)
