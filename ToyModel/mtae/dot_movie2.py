"""Corrected dot-stimulus movie, half speed: two COUNTER-ROTATING transparent fields,
delayed onset for the cued field, then a BRIEF translation of the cued field (the
judged motion). Two densities. Saves a GIF."""
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.animation as animation

np.random.seed(3)
FIGS = os.path.dirname(os.path.abspath(__file__)) + "/figs"
R = 10.0
DTH = 0.045                       # rotation per frame (slow = half speed)
T_ON = 22                         # field B delayed onset
T_TR0, T_TR1 = 60, 70            # BRIEF translation window (cued field)
VTR = 0.55                        # translation speed (upward burst)
T = 92
DENS = [20, 70]                   # dots per field


def init_field(n):
    pts = []
    while len(pts) < n:
        p = np.random.uniform(-R, R, 2)
        if p[0]**2 + p[1]**2 < 0.98*R**2:
            pts.append(p)
    return np.array(pts)


def rot(P, dth):
    c, s = np.cos(dth), np.sin(dth)
    return P @ np.array([[c, s], [-s, c]])


fields = [[init_field(n), init_field(n)] for n in DENS]   # [A, B] per panel
fig, axes = plt.subplots(1, 2, figsize=(10.5, 5.6))
scat = []
for ax, n in zip(axes, DENS):
    ax.set_xlim(-R-1, R+3); ax.set_ylim(-R-1, R+3); ax.set_aspect("equal"); ax.axis("off")
    ax.add_patch(plt.Circle((0, 0), R, fill=False, color="gray", lw=1))
    sA = ax.scatter([], [], s=16, c="#d1495b")
    sB = ax.scatter([], [], s=16, c="#3f88c5")
    scat.append((sA, sB)); ax.set_title(f"{n} dots/field", fontsize=11)
suptitle = fig.suptitle("")


def update(t):
    if t < T_ON:
        phase = "field A rotating (CW)"
    elif t < T_TR0:
        phase = "both counter-rotating (A cw, B ccw)"
    elif t < T_TR1:
        phase = ">>> BRIEF TRANSLATION of cued field B <<<"
    else:
        phase = "translation over; rotating again"
    suptitle.set_text(f"frame {t}   {phase}\nred = A (continuous) · blue = B (cued, delayed)")
    for (A, B), (sA, sB) in zip(fields, scat):
        A[:] = rot(A, +DTH)                          # A rotates CW
        if t >= T_ON:
            B[:] = rot(B, -DTH)                      # B rotates CCW
        if T_TR0 <= t < T_TR1:
            B[:, 1] += VTR                           # brief upward translation of B
        mA = A[:, 0]**2 + A[:, 1]**2 < R**2
        sA.set_offsets(A[mA])
        if t >= T_ON:
            mB = (B[:, 0]**2 + B[:, 1]**2 < R**2) | (B[:, 1] > 0)   # keep translated dots visible
            sB.set_offsets(B[mB])
        else:
            sB.set_offsets(np.empty((0, 2)))
    return []


ani = animation.FuncAnimation(fig, update, frames=T, interval=110, blit=False)
out = os.path.join(FIGS, "dot_movie2.gif")
ani.save(out, writer=animation.PillowWriter(fps=9))     # slow playback
plt.close(fig)
print("movie ->", out)
