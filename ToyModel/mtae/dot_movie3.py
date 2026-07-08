"""Correct cued-swap stimulus movie (half speed):
 - two transparent dot fields in OPPOSITE linear motion (A left, B right),
 - the cued (delayed) field B then BRIEFLY translates in the ORTHOGONAL direction
   (up) at 50% coherence (half its dots move up, half move randomly).
Two densities. Saves a GIF."""
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.animation as animation

np.random.seed(4)
FIGS = os.path.dirname(os.path.abspath(__file__)) + "/figs"
R = 10.0
VH = 0.28                         # base horizontal speed (opposite dirs)
VT = 0.42                         # brief translation speed (orthogonal, up)
T_ON = 16                         # field B (cued) delayed onset
T_TR0, T_TR1 = 52, 66             # BRIEF orthogonal-translation window
COH = 0.5                         # 50% coherence during the translation
T = 88
DENS = [25, 80]                   # dots per field


def init_field(n):
    pts = []
    while len(pts) < n:
        p = np.random.uniform(-R, R, 2)
        if p[0]**2 + p[1]**2 < 0.97*R**2:
            pts.append(p)
    return np.array(pts)


def wrap(P):
    P[:, 0] = ((P[:, 0] + R) % (2*R)) - R
    return P


panels = []
for n in DENS:
    A = init_field(n); B = init_field(n)
    coh = np.random.rand(n) < COH        # which B dots are coherent during translation
    panels.append([A, B, coh])

fig, axes = plt.subplots(1, 2, figsize=(10.5, 5.8))
scat = []
for ax, n in zip(axes, DENS):
    ax.set_xlim(-R-1, R+1); ax.set_ylim(-R-1, R+3); ax.set_aspect("equal"); ax.axis("off")
    ax.add_patch(plt.Circle((0, 0), R, fill=False, color="gray", lw=1))
    sA = ax.scatter([], [], s=16, c="#d1495b")
    sB = ax.scatter([], [], s=16, c="#3f88c5")
    scat.append((sA, sB)); ax.set_title(f"{n} dots/field", fontsize=11)
suptitle = fig.suptitle("")


def update(t):
    translating = T_TR0 <= t < T_TR1
    phase = ("field A only (moving left)" if t < T_ON else
             ">>> cued field B: BRIEF orthogonal translation, 50% coherent <<<" if translating else
             "two fields, opposite motion (A left, B right)")
    suptitle.set_text(f"frame {t}   {phase}\nred = A (continuous, ←) · blue = B (cued, delayed)")
    for (A, B, coh), (sA, sB) in zip(panels, scat):
        wrap(A[:, :]); A[:, 0] -= VH                       # A drifts left
        if t >= T_ON:
            if translating:                                # B briefly translates UP (orthogonal), 50% coherent
                B[coh, 1] += VT
                B[~coh] += (np.random.rand((~coh).sum(), 2)-0.5)*2*VT
            else:
                B[:, 0] += VH; wrap(B[:, :])               # B drifts right
        mA = A[:, 0]**2 + A[:, 1]**2 < R**2
        sA.set_offsets(A[mA])
        if t >= T_ON:
            mB = (B[:, 0]**2 + B[:, 1]**2 < R**2) | (B[:, 1] > 0)
            sB.set_offsets(B[mB])
        else:
            sB.set_offsets(np.empty((0, 2)))
    return []


ani = animation.FuncAnimation(fig, update, frames=T, interval=110, blit=False)
out = os.path.join(FIGS, "dot_movie3.gif")
ani.save(out, writer=animation.PillowWriter(fps=9))       # half speed
plt.close(fig)
print("movie ->", out)
