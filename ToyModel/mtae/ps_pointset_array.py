"""
Show the two dot fields SUPERIMPOSED on the array of V1 hypercolumns, at S&B density.

Purpose: ps_pointset.py collapses each transparent surface to ONE V1 hypercolumn. That collapse is
only legitimate if, at the V1 cRF scale, each active hypercolumn is dominated by ONE surface. This
figure draws the actual array and the actual dots to show (and quantify) that segregation.

S&B (2010) geometry: aperture dia 4 deg (r=2 deg), density 5 dots/deg^2/field -> ~63 dots/field.
V1 cRF (Dow 1981, d = 0.05 + 0.08*E at the ~1.3 deg mean eccentricity): diameter ~0.16 deg,
sigma ~0.08 deg. So dots per cRF per field = 5 * (pi * 0.08^2) ~ 0.1  ->  intrinsically segregated.
"""
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

np.random.seed(2)
FIGS = os.path.dirname(os.path.abspath(__file__)) + "/figs"
R = 2.0                       # aperture radius (deg)
DENS = 5.0                    # dots / deg^2 / field  (S&B)
N = int(round(DENS * np.pi * R**2))     # dots per field ~ 63
SIG_V1 = 0.08                 # V1 cRF sigma (deg)
CRF = 2*SIG_V1                # cRF diameter (deg)
GRID = 25                     # V1 hypercolumns per side (spacing ~ cRF -> tiles the aperture)


def make_field(n):
    pts = []
    while len(pts) < n:
        p = np.random.uniform(-R, R, 2)
        if p[0]**2 + p[1]**2 <= R**2:
            pts.append(p)
    return np.array(pts)


A = make_field(N)            # first-on field (moves left)
B = make_field(N)            # delayed/cued field (moves right)

# V1 hypercolumn centres tiling the aperture
gx = np.linspace(-R, R, GRID)
cx, cy = np.meshgrid(gx, gx)
centres = np.stack([cx.ravel(), cy.ravel()], 1)
centres = centres[centres[:, 0]**2 + centres[:, 1]**2 <= R**2]

# --- segregation metric: for each hypercolumn, dots within the cRF (1 sigma); classify ---
rSeg = SIG_V1
countA = np.array([np.sum(((A-c)**2).sum(1) <= rSeg**2) for c in centres])
countB = np.array([np.sum(((B-c)**2).sum(1) <= rSeg**2) for c in centres])
active = (countA + countB) > 0
single = active & ((countA == 0) | (countB == 0))
frac_single = single.sum() / max(active.sum(), 1)
dots_per_crf = DENS * np.pi * SIG_V1**2

print(f"aperture r={R} deg, density={DENS} dots/deg^2/field -> {N} dots/field")
print(f"V1 cRF sigma={SIG_V1} deg (diam {CRF} deg); {len(centres)} hypercolumns tile the aperture")
print(f"dots per cRF per field = {dots_per_crf:.3f}")
print(f"active hypercolumns (>=1 dot in cRF): {active.sum()};  single-surface: {single.sum()} "
      f"= {100*frac_single:.0f}%  -> intrinsically segregated")

# ---------------------------------------------------------------------------------------------
fig, ax = plt.subplots(1, 2, figsize=(15, 7.2))

# (a) full aperture: V1 array + both dot fields + motion arrows
a0 = ax[0]
a0.set_aspect("equal"); a0.set_xlim(-R-.15, R+.15); a0.set_ylim(-R-.15, R+.15)
a0.add_patch(plt.Circle((0, 0), R, fill=False, color="k", lw=1.2))
for c in centres:                                   # cRF extent (1 sigma) as faint circles
    a0.add_patch(plt.Circle(c, SIG_V1, fill=False, color="0.75", lw=0.5))
a0.plot(centres[:, 0], centres[:, 1], ".", ms=1.2, color="0.6")
a0.scatter(A[:, 0], A[:, 1], s=14, c="#d1495b", zorder=3, label=f"field A (first-on, ←)  n={N}")
a0.scatter(B[:, 0], B[:, 1], s=14, c="#3f88c5", zorder=3, label=f"field B (cued/delayed, →)  n={N}")
for p in A[::4]:
    a0.annotate("", xy=(p[0]-0.18, p[1]), xytext=(p[0], p[1]),
                arrowprops=dict(arrowstyle="->", color="#d1495b", lw=1))
for p in B[::4]:
    a0.annotate("", xy=(p[0]+0.18, p[1]), xytext=(p[0], p[1]),
                arrowprops=dict(arrowstyle="->", color="#3f88c5", lw=1))
a0.set_title(f"Two transparent fields on the V1 hypercolumn array\n"
             f"{DENS} dots/deg²/field = {N} dots/field · aperture r={R}° · "
             f"{len(centres)} cRF hypercolumns (σ={SIG_V1}°)", fontsize=10)
a0.legend(loc="upper right", fontsize=8); a0.set_xlabel("deg"); a0.set_ylabel("deg")

# (b) zoom: a 0.8x0.8 deg window at true cRF scale -> mostly <=1 dot per hypercolumn
a1 = ax[1]
z = 0.4                                              # half-window (deg)
cx0, cy0 = -0.3, 0.2
a1.set_aspect("equal"); a1.set_xlim(cx0-z, cx0+z); a1.set_ylim(cy0-z, cy0+z)
m = np.abs(centres[:, 0]-cx0) < z+SIG_V1
for c in centres[m]:
    a1.add_patch(plt.Circle(c, SIG_V1, fill=False, color="0.7", lw=0.8))
mA = (np.abs(A[:, 0]-cx0) < z) & (np.abs(A[:, 1]-cy0) < z)
mB = (np.abs(B[:, 0]-cx0) < z) & (np.abs(B[:, 1]-cy0) < z)
a1.scatter(A[mA, 0], A[mA, 1], s=60, c="#d1495b", zorder=3)
a1.scatter(B[mB, 0], B[mB, 1], s=60, c="#3f88c5", zorder=3)
a1.set_title(f"Zoom to cRF scale: each hypercolumn sees ≤ ~1 dot of ONE field\n"
             f"dots/cRF/field = {dots_per_crf:.2f}  →  {100*frac_single:.0f}% of active "
             f"hypercolumns are single-surface", fontsize=10)
a1.set_xlabel("deg"); a1.set_ylabel("deg")

fig.suptitle("Why 2 hypercolumns is faithful, not a cheat: at S&B density the stimulus is already "
             "segregated across the V1 cRF array\n(ps_pointset.py collapses each surface's "
             "single-dominated hypercolumns into one)", fontsize=11)
fig.tight_layout(rect=[0, 0, 1, 0.96])
p = os.path.join(FIGS, "ps_pointset_array.png")
fig.savefig(p, dpi=115, bbox_inches="tight"); plt.close(fig)
print("figure ->", p)
