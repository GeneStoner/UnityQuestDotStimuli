"""
Original schematic (our own stimulus — not a reproduction of any published
figure): the two transparent counter-rotating dot fields, with a large MT
receptive field placed off to one side of fixation.  The point: for an
off-centre RF, each rigid rotation is *locally* well approximated by a
translation, so the two rotations (and the brief test translation) can all be
treated as motion directions on one axis.  V1 supplies that local direction
signal (the *input*, invariant to the feature swaps); the model's own stages
live in MT — the direction-selective channels that adapt, then the pattern /
MST unit that detects translation.  This lets us reason with a directional MT
drive without yet invoking MST / rotation-selective neurons.

Geometry: the RF sits directly to the LEFT of fixation, so the CW field's
local motion is UP and the CCW field's is DOWN — matching the drive figure
(DIR_CW = 90 deg = up, DIR_CCW = -90 deg = down).

Run:  /usr/bin/python3 mt_rf_figure.py
"""

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyArrowPatch
from matplotlib.lines import Line2D

from web_figures import INK, INK2, BORDER, ACCENT, CUED, UNCUED, SURFACE, GRID

GREEN, RED = CUED, UNCUED          # field colours (match the rest of the set)
APERTURE = 3.0                     # = 2.0 deg radius (4 deg stimulus, S&B 2010)
RF_C, RF_R = (-2.0, 0.0), 0.9      # MT RF: directly left of fixation, eccentric
                                   # enough to exclude the near-fixation dots
                                   # (whose local motion is not up/down)
OMEGA = 81.0                       # rotation speed, deg/s (Stoner & Blanc 2010)
TRACE_MS = 100.0                   # duration each dot-trace represents
SWEEP = OMEGA * TRACE_MS / 1000.0  # constant angular sweep (deg) ~ 12.15

# Dot density: S&B used 5 dots/deg^2 per field.  Here 1 deg = 1.5 units, so
# 1 deg^2 = 2.25 units^2 -> grid spacing = sqrt(2.25 / 5) ~ 0.67 units/field.
DENS_SPACING = 0.67


def _field(spacing, jitter, seed, offset=(0.0, 0.0), rmin=0.7, rmax=None):
    """A jittered grid of dot positions inside a disk: even density (unlike
    pure uniform-random, which clumps) yet still random-looking thanks to the
    per-dot jitter.  Two calls with different ``offset`` give two interleaved
    fields."""
    if rmax is None:
        rmax = APERTURE - 0.08
    rng = np.random.default_rng(seed)
    k = int(np.ceil(rmax / spacing)) + 1
    coords = np.arange(-k, k + 1) * spacing
    pts = []
    for x in coords:
        for y in coords:
            p = np.array([x + offset[0], y + offset[1]]) + \
                rng.uniform(-jitter, jitter, 2)
            if rmin < np.hypot(*p) < rmax:
                pts.append(p)
    return np.array(pts)


def _rotation_arrow(ax, a0_deg, a1_deg, color, R=3.45):
    th = np.radians(np.linspace(a0_deg, a1_deg, 30))
    ax.plot(R * np.cos(th), R * np.sin(th), color=color, lw=2.4,
            solid_capstyle="round")
    # arrowhead at the a1 end
    p1 = np.array([R * np.cos(th[-1]), R * np.sin(th[-1])])
    p0 = np.array([R * np.cos(th[-3]), R * np.sin(th[-3])])
    ax.add_patch(FancyArrowPatch(p0, p1, arrowstyle="-|>", mutation_scale=16,
                 color=color, lw=0, zorder=5))


def _arc_motion(ax, p, fix, sense, color, lw=1.7, head=8,
                sweep_deg=None, length=None):
    """Draw a short arrow that is a TRUE arc of the circle of rigid rotation
    about ``fix`` passing through dot ``p``.  sense='CW'/'CCW'.  Pass
    ``sweep_deg`` for a fixed DURATION (constant angle -> length scales with
    radius, as real rigid rotation does); or ``length`` for a fixed arc length
    (used only for the idealized zoom)."""
    p = np.asarray(p, float); fix = np.asarray(fix, float)
    rvec = p - fix
    R = np.hypot(*rvec)
    th0 = np.degrees(np.arctan2(rvec[1], rvec[0]))
    s = -1.0 if sense == "CW" else 1.0          # CW = decreasing angle
    if sweep_deg is None:
        sweep_deg = np.degrees(length / R)
    ths = np.radians(np.linspace(th0, th0 + s * sweep_deg, 16))
    xs = fix[0] + R * np.cos(ths)
    ys = fix[1] + R * np.sin(ths)
    ax.plot(xs, ys, color=color, lw=lw, solid_capstyle="round", zorder=4)
    ax.add_patch(FancyArrowPatch((xs[-2], ys[-2]), (xs[-1], ys[-1]),
                 arrowstyle="-|>", mutation_scale=head, color=color, lw=0,
                 zorder=4))


def fig_mt_rf(out="mt_rf_figure.png"):
    fig, (axL, axR) = plt.subplots(
        1, 2, figsize=(11.5, 5.6), gridspec_kw=dict(width_ratios=[1.15, 1.0]))

    # ============ LEFT: the stimulus + the MT RF ======================
    axL.set_aspect("equal"); axL.axis("off")
    axL.set_xlim(-4.0, 4.0); axL.set_ylim(-4.0, 4.0)

    axL.add_patch(Circle((0, 0), APERTURE, facecolor="#fafafa",
                  edgecolor=BORDER, lw=1.4, zorder=0))

    # the MT receptive field, highlighted
    axL.add_patch(Circle(RF_C, RF_R, facecolor="#eef2f1", edgecolor=INK,
                  lw=2.0, ls=(0, (5, 3)), zorder=1))

    # fixation
    axL.plot(0, 0, marker="+", ms=11, mew=2.0, color=INK, zorder=5)

    # every dot is drawn as a TRACE: a short arc of its rigid-rotation path
    # about fixation, tipped with an arrowhead for direction.  Green = CW
    # field, red = CCW field.  Two offset jittered grids -> even density.
    g = _field(spacing=DENS_SPACING, jitter=0.18, seed=11, offset=(0.0, 0.0))
    r = _field(spacing=DENS_SPACING, jitter=0.18, seed=12,
               offset=(DENS_SPACING / 2, DENS_SPACING / 2))
    for p in g:
        axL.scatter(*p, s=9, color=GREEN, zorder=3)
        _arc_motion(axL, p, (0, 0), "CW", GREEN, lw=1.4, head=7, sweep_deg=SWEEP)
    for p in r:
        axL.scatter(*p, s=9, color=RED, zorder=3)
        _arc_motion(axL, p, (0, 0), "CCW", RED, lw=1.4, head=7, sweep_deg=SWEEP)

    axL.text(RF_C[0], RF_C[1] - RF_R - 0.35, "MT receptive field",
             ha="center", va="top", fontsize=10.5, color=INK)
    axL.legend(handles=[
        Line2D([0], [0], color=GREEN, lw=2.2, label="CW field"),
        Line2D([0], [0], color=RED, lw=2.2, label="CCW field")],
        loc="upper right", frameon=False, fontsize=10)

    axL.set_title("Two counter-rotating fields + an off-centre MT RF",
                  fontsize=11.5, color=INK, pad=6)

    # ============ RIGHT: the SAME RF, exactly magnified ===============
    # Not an idealized patch — the identical dots and identical rotation arcs
    # from inside the RF on the left, scaled up about the (magnified) real
    # fixation so the motions shown are exactly those in the stimulus.
    axR.set_aspect("equal"); axR.axis("off")
    M = 1.45
    rz = RF_R * M
    fix_zoom = (-np.array(RF_C)) * M            # real fixation, magnified in
    axR.set_xlim(-rz - 0.3, rz + 1.2); axR.set_ylim(-rz - 0.7, rz + 0.4)
    axR.add_patch(Circle((0, 0), rz, facecolor=SURFACE, edgecolor=INK,
                  lw=2.0, ls=(0, (5, 3)), zorder=1))

    def _inrf(p):
        return np.hypot(p[0] - RF_C[0], p[1] - RF_C[1]) < RF_R - 0.04

    for p in g:
        if _inrf(p):
            zp = (np.asarray(p) - RF_C) * M
            axR.scatter(*zp, s=22, color=GREEN, zorder=3)
            _arc_motion(axR, zp, fix_zoom, "CW", GREEN, lw=2.4, head=11,
                        sweep_deg=SWEEP)
    for p in r:
        if _inrf(p):
            zp = (np.asarray(p) - RF_C) * M
            axR.scatter(*zp, s=22, color=RED, zorder=3)
            _arc_motion(axR, zp, fix_zoom, "CCW", RED, lw=2.4, head=11,
                        sweep_deg=SWEEP)

    axR.text(rz + 0.12, 0.42, "CW ≈ up", color=GREEN, fontsize=11,
             fontweight="bold", ha="left", va="center")
    axR.text(rz + 0.12, -0.42, "CCW ≈ down", color=RED, fontsize=11,
             fontweight="bold", ha="left", va="center")
    axR.set_title("The same RF, magnified — local motion ≈ translations",
                  fontsize=11.5, color=INK, pad=6)

    fig.tight_layout()
    fig.savefig(out, dpi=170, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"wrote {out}")


if __name__ == "__main__":
    fig_mt_rf()
