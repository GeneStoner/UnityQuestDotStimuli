"""Animated dot stimuli: two transparent translating fields (left/right) sharing an
aperture, with a delayed onset for the cued field and a motion swap. Three densities
side by side. Saves a GIF."""
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.animation as animation

np.random.seed(2)
FIGS = os.path.dirname(os.path.abspath(__file__)) + "/figs"
R, T, T_ON, T_SWAP, SPEED = 10.0, 64, 14, 40, 0.30
DENS = [15, 45, 100]                       # dots per field


def init_field(n):
    pts = []
    while len(pts) < n:
        p = np.random.uniform(-R, R, 2)
        if p[0]**2 + p[1]**2 < R**2:
            pts.append(p)
    return np.array(pts)


fields = [[init_field(n), init_field(n)] for n in DENS]
fig, axes = plt.subplots(1, 3, figsize=(13, 5))
scat = []
for ax, n in zip(axes, DENS):
    ax.set_xlim(-R-1, R+1); ax.set_ylim(-R-1, R+1); ax.set_aspect("equal"); ax.axis("off")
    ax.add_patch(plt.Circle((0, 0), R, fill=False, color="gray", lw=1))
    sA = ax.scatter([], [], s=14, c="#d1495b")
    sB = ax.scatter([], [], s=14, c="#3f88c5")
    scat.append((sA, sB))
    ax.set_title(f"{n} dots/field", fontsize=11)
suptitle = fig.suptitle("")


def update(t):
    phase = ("field A only" if t < T_ON else
             "both translating (A→, B←)" if t < T_SWAP else "AFTER SWAP (A←, B→)")
    suptitle.set_text(f"t={t}   {phase}    red = A (continuous) · blue = B (cued, delayed)")
    for (A, B), (sA, sB) in zip(fields, scat):
        vA = SPEED if t < T_SWAP else -SPEED
        vB = -SPEED if t < T_SWAP else SPEED
        A[:, 0] += vA; B[:, 0] += vB
        A[:, 0] = ((A[:, 0] + R) % (2*R)) - R          # wrap x to keep density constant
        B[:, 0] = ((B[:, 0] + R) % (2*R)) - R
        mA = A[:, 0]**2 + A[:, 1]**2 < R**2
        mB = B[:, 0]**2 + B[:, 1]**2 < R**2
        sA.set_offsets(A[mA])
        sB.set_offsets(B[mB] if t >= T_ON else np.empty((0, 2)))
    return []


ani = animation.FuncAnimation(fig, update, frames=T, interval=80, blit=False)
out = os.path.join(FIGS, "dot_movie.gif")
ani.save(out, writer=animation.PillowWriter(fps=13))
plt.close(fig)
print("movie ->", out)
