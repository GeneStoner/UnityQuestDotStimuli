"""Animated hand-wired PS model, CUED vs UNCUED translation on the SWAP trial.
Rows = which field briefly translates (top: cued/delayed B ; bottom: uncued/first-on A).
Cols = [2D dots (size proportional to gain: big = un-adapted) | V1 up-channel map |
        MT 4-direction hypercolumn, up/down translation detector in gold].
The cued field's brief orthogonal translation drives the MT up detector more strongly,
because the cooperative connection carries its (un-adapted) base-motion bias into the up
channel. Runs on the SWAP trial to show the advantage survives the motion swap."""
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import ps_wire as P

FIGS = P.FIGS; R = P.R_AP; G = P.G; DIRLAB = ["R", "U", "L", "D"]
np.random.seed(7); MTc, V1c, trajC = P.simulate(60, "cued", P.UP, swap=True, keep=True)
np.random.seed(7); MTu, V1u, trajU = P.simulate(60, "uncued", P.UP, swap=True, keep=True)
mtmax = max(MTc.max(), MTu.max())*1.05
vmax = max(max(f[:, :, P.UP].max() for f in V1c), max(f[:, :, P.UP].max() for f in V1u))*1.02

fig, ax = plt.subplots(2, 3, figsize=(13.5, 8.4), gridspec_kw={"width_ratios": [1.1, 0.9, 1.0]})
rows = []
for r, (traj, V1f, MT, who) in enumerate([(trajC, V1c, MTc, "CUED (delayed B) translates"),
                                          (trajU, V1u, MTu, "UNCUED (first-on A) translates")]):
    axsc, axv1, axbar = ax[r]
    axsc.set_xlim(-R-1, R+2); axsc.set_ylim(-R-1, R+4); axsc.set_aspect("equal"); axsc.axis("off")
    axsc.add_patch(plt.Circle((0, 0), R, fill=False, color="gray", lw=1))
    axsc.set_title(f"{who}\n(dot size ∝ gain; big = un-adapted)", fontsize=9)
    sA = axsc.scatter([], [], c="#d1495b"); sB = axsc.scatter([], [], c="#3f88c5")
    im = axv1.imshow(np.zeros((G, G)), origin="lower", cmap="magma", vmin=0, vmax=vmax,
                     extent=[-R, R, -R, R]); axv1.set_xticks([]); axv1.set_yticks([])
    axv1.set_title("V1 UP channel", fontsize=9)
    bars = axbar.bar(range(4), [0]*4, color=["#888", "#e0a800", "#888", "#e0a800"])
    axbar.set_xticks(range(4)); axbar.set_xticklabels(DIRLAB); axbar.set_ylim(0, mtmax)
    axbar.set_title("MT hypercolumn (gold = U/D detector)", fontsize=9)
    dtxt = axbar.text(0.5, 0.92, "", transform=axbar.transAxes, ha="center", fontsize=9, color="#7a2030")
    rows.append((traj, V1f, MT, sA, sB, im, bars, dtxt))
sup = fig.suptitle("")


def update(t):
    ph = ("field A only (left)" if t < P.T_ON else
          ">>> BRIEF ORTHOGONAL TRANSLATION (50% coherent) <<<" if P.T_TEST0 <= t < P.T_TEST1 else
          "two fields, opposite motion  (SWAP at test)")
    sup.set_text(f"frame {t}    {ph}\nred = A (first-on) · blue = B (cued, delayed)")
    for (traj, V1f, MT, sA, sB, im, bars, dtxt) in rows:
        posA, posB, gA, gB, testing = traj[t]
        sA.set_offsets(posA); sA.set_sizes(6 + 90*gA)
        if len(posB):
            sB.set_offsets(posB); sB.set_sizes(6 + 90*gB)
        else:
            sB.set_offsets(np.empty((0, 2)))
        im.set_data(V1f[t][:, :, P.UP].T)
        for b, h in zip(bars, MT[t]):
            b.set_height(h)
        det = MT[t][P.UP] - MT[t][P.DOWN]
        dtxt.set_text(f"detector (U−D) = {det:5.1f}" if testing else "")
    return []


ani = animation.FuncAnimation(fig, update, frames=P.T, interval=140, blit=False)
out = os.path.join(FIGS, "ps_wire_anim.gif")
ani.save(out, writer=animation.PillowWriter(fps=7))
plt.close(fig)
print("movie ->", out)
