"""
Two direction-of-motion hypercolumns — the first schematic of the object-based section.

  A   the stimulus, with the two V1 RFs marked (the SAME panel as
      ps_two_rf_figure.py and mt_rf_figure.py — drawn by the one
      ps_stimulus_common.draw_stimulus, so all three stay in step)
  B   those same two RFs as what they are in the model: two 8-direction motion
      hypercolumns, projecting into one MT hypercolumn

The whole argument of the figure is the CORRESPONDENCE — the left circle in A is
the left rosette in B, the right circle is the right rosette. Nothing else in the
figure matters if a reader cannot see that.

STAGE ONE of GS's staging: motion only. Colour hypercolumns come later, and the two
together are the minimal point-set. So the units here are called motion hypercolumns,
not point-sets.

WHAT IS DRAWN is the moment of the probe, matching A's blow-ups in ps_two_rf_figure:
  - the uncued (red, CCW, first-on) field keeps rotating -> at an RF right of fixation
    its local motion is UP,
  - the cued (green, CW, delayed) field's rotation is REPLACED by the rightward
    translation -> RIGHT,
so MT sees one rotation direction and one translation direction at once. That
competition is the model.

THE ROSETTE IS PROVISIONAL. Every other two-unit drawing in this project (
web_model_architecture, model_diagram panel A, web_model_circuit*) represents a unit
as a box or a soma — one rate. A soma hides the direction tuning that makes a
hypercolumn a hypercolumn, which is why the rosette is being tried. If it does not
read well, only `draw_two_hc` below needs replacing: the fallbacks are 8 bars per
unit over preferred direction, or the Reynolds/Chelazzi/Desimone soma-with-terminals
idiom already used by Figure 4.

Run:  /usr/bin/python3 ps_two_hc_figure.py
"""

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Polygon, FancyArrowPatch

import ps_stimulus_common as S
from ps_stimulus_common import (INK, INK2, BORDER, GREEN, RED,
                                RF_DIAM_DEG, MT_R_DEG, DOT_DIAM_DEG, OMEGA_DEG_S)

# ── the hypercolumn: 8 directions, as in ps_pointset.py (D = 8, theta = 0..315) ──
N_DIR = 8
DIRS = np.arange(N_DIR) * (360.0 / N_DIR)      # 0 = right, 90 = up

# Which channel each unit is driven in AT THE PROBE. Index into DIRS.
K_RIGHT, K_UP = 0, 2

# Panel-B layout. The data box is 100 x 79 because the axes is that much wider
# than tall (width_ratios 5.6 of 12 in, against 0.72 of 6 in high) -- matching it
# means the drawing fills the panel instead of floating in a square.
PB_W, PB_H = 100.0, 79.0
RING = 1.62                      # ring radius as a multiple of the arrow ring
HC_Y, HC_R = 51.0, 8.0
HC_X_L, HC_X_R = 26.0, 74.0
MT_XY, MT_R = (50.0, 16.0), 8.5


def _arrowhead(ax, x, y, ang_deg, size, colour, alpha, z=5):
    """One direction's arrowhead, pointing along ang_deg."""
    pts = np.array([[0.0, -0.34], [0.92, 0.0], [0.0, 0.34]]) * size
    t = np.radians(ang_deg)
    rot = np.array([[np.cos(t), -np.sin(t)], [np.sin(t), np.cos(t)]])
    ax.add_patch(Polygon(pts @ rot.T + [x, y], closed=True, facecolor=colour,
                         edgecolor="none", alpha=alpha, zorder=z))


def _rosette(ax, cx, cy, r, active, colour, size=7.0, ring=True):
    """A direction-of-motion hypercolumn: 8 preferred directions round a centre.

    `active` are the indices driven at this instant; they take the field colour at
    full strength, the rest stay faint ink. Ported from HCPSFlow.tsx's Rosette so
    the simple model and the full one read as the same family.
    """
    if ring:
        ax.add_patch(Circle((cx, cy), r * 1.62, facecolor="#f6f5f3",
                            edgecolor=BORDER, lw=1.2, zorder=1))
    for k, a in enumerate(DIRS):
        x = cx + r * np.cos(np.radians(a))
        y = cy + r * np.sin(np.radians(a))
        on = k in active
        _arrowhead(ax, x, y, a, size * (1.28 if on else 1.0),
                   colour if on else INK2, 1.0 if on else 0.26)
    ax.add_patch(Circle((cx, cy), r * 0.11, facecolor=INK2, edgecolor="none",
                        zorder=6))


def draw_two_hc(ax):
    """PANEL B — the two motion hypercolumns feeding one MT hypercolumn.

    Swap this function alone to change the idiom; panel A and the layout do not
    depend on anything in here.
    """
    ax.set_aspect("equal"); ax.axis("off")
    ax.set_xlim(0, PB_W); ax.set_ylim(0, PB_H)

    # ── the two V1 motion hypercolumns ──
    _rosette(ax, HC_X_L, HC_Y, HC_R, active={K_UP}, colour=RED)
    _rosette(ax, HC_X_R, HC_Y, HC_R, active={K_RIGHT}, colour=GREEN)

    # Each unit's whole caption sits ABOVE it, in one block. Putting the driven
    # channel below instead collided with the projections and with MT's label.
    for x, colour, lab, field, driven in (
            (HC_X_L, RED,   "left RF",  "CCW field · first-on (uncued)",
             "rotation continues: locally UP"),
            (HC_X_R, GREEN, "right RF", "CW field · delayed-onset (cued)",
             "rotation replaced by the probe: RIGHT")):
        top = HC_Y + HC_R * RING
        ax.text(x, top + 12.5, lab, ha="center", va="bottom",
                fontsize=11, fontweight="bold", color=INK)
        ax.text(x, top + 7.0, field, ha="center", va="bottom",
                fontsize=9.5, color=colour)
        ax.text(x, top + 2.0, driven, ha="center", va="bottom",
                fontsize=9, color=INK2)

    # ── projections into MT ──
    for x, colour in ((HC_X_L, RED), (HC_X_R, GREEN)):
        ax.add_patch(FancyArrowPatch(
            (x + (50 - x) * 0.10, HC_Y - HC_R * RING - 2.0),
            (MT_XY[0] + (x - 50) * 0.30, MT_XY[1] + MT_R * RING + 1.5),
            arrowstyle="-|>", mutation_scale=15, color=colour, lw=1.8,
            alpha=0.75, shrinkA=0, shrinkB=2, zorder=3))

    # ── MT: one hypercolumn, seeing BOTH at once ──
    _rosette(ax, MT_XY[0], MT_XY[1], MT_R, active=(), colour=INK2, size=7.2)
    for k, colour in ((K_UP, RED), (K_RIGHT, GREEN)):
        a = DIRS[k]
        _arrowhead(ax, MT_XY[0] + MT_R * np.cos(np.radians(a)),
                   MT_XY[1] + MT_R * np.sin(np.radians(a)),
                   a, 7.2 * 1.28, colour, 1.0, z=7)
    # label to the LEFT: above is where the projections arrive, below is the rim
    ax.text(MT_XY[0] - MT_R * RING - 3.0, MT_XY[1], "MT\nhypercolumn",
            ha="right", va="center", fontsize=11, fontweight="bold",
            color=INK, linespacing=1.35)


def fig_two_hc(out="ps_two_hc_figure.png"):
    # figsize / width_ratios / subplots_adjust are mt_rf_figure.py's EXACTLY, so
    # panel A renders at an identical scale in all three figures and
    # check_stimulus_panels.py can compare them.
    fig, (axL, axR) = plt.subplots(
        1, 2, figsize=(12.0, 6.0), gridspec_kw=dict(width_ratios=[6.4, 5.6]))

    S.draw_stimulus(axL, show_v1_rfs=True)
    draw_two_hc(axR)

    fig.subplots_adjust(left=0.015, right=0.985, top=0.865, bottom=0.145,
                        wspace=0.10)

    HEAD_Y = 0.965
    posL, posR = axL.get_position(), axR.get_position()
    for pos, lab in ((posL, "A"), (posR, "B")):
        fig.text(pos.x0, HEAD_Y, lab, fontsize=15, fontweight="bold",
                 color=INK, ha="left", va="top")
    fig.text(posL.x0 + posL.width / 2, HEAD_Y,
             "Two V1 RFs inside the MT RF",
             fontsize=12, color=INK, ha="center", va="top")
    fig.text(posR.x0 + posR.width / 2, HEAD_Y,
             "Each RF is a direction-of-motion hypercolumn",
             fontsize=12, color=INK, ha="center", va="top")

    fig.text(0.5, 0.008,
             f"{N_DIR} directions per hypercolumn · V1 RF {RF_DIAM_DEG:.2f}° diameter · "
             f"MT RF {2*MT_R_DEG:.1f}° · dots {DOT_DIAM_DEG:g}° · "
             f"{S.DENSITY:g} dots/deg²/field · rotation {OMEGA_DEG_S:g}°/s",
             ha="center", va="bottom", fontsize=8.5, color=INK2)

    fig.savefig(out, dpi=170, facecolor="white")
    plt.close(fig)
    print(f"wrote {out}   (2 x {N_DIR}-direction V1 hypercolumns -> 1 MT hypercolumn; "
          f"driven channels: uncued UP, cued RIGHT)")


if __name__ == "__main__":
    fig_two_hc()
