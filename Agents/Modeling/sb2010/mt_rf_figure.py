"""
Figure 2 of the computational section — the stimulus, and an MT receptive field.

Original schematic (our own stimulus, not a reproduction of any published figure):
two transparent counter-rotating dot fields, with a large MT receptive field off to
one side of fixation. The point: for an off-centre RF each rigid rotation is
*locally* well approximated by a translation, so the two rotations and the brief
test translation can all be treated as directions on one axis. V1 supplies that
local direction signal — the input, invariant to the feature swaps — while the
model's own stages live in MT.

Geometry: the RF sits to the RIGHT of fixation, so the CW field's local motion is
DOWN and the CCW field's is UP.

PAIRS WITH `ps_two_rf_figure.py`. Both take their stimulus from
`ps_stimulus_common.draw_stimulus`, and the dot layout is computed once there, so
this figure and the V1-RF figure show *the same picture* — the only difference
being that the other one adds two V1 RF circles. Change the stimulus here and it
changes there; that is deliberate.

  LEFT   the stimulus and the MT RF. Dots only — no motion is drawn.
  RIGHT  that RF magnified, with the real trajectory of every dot inside it:
         100 ms of rotation, then the 40 ms probe.

Run:  /usr/bin/python3 mt_rf_figure.py
"""

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyArrowPatch
from matplotlib.lines import Line2D

import ps_stimulus_common as S
from ps_stimulus_common import (INK, INK2, GREEN, RED, SURFACE,
                                MT_C, MT_R_DEG, DOT_DIAM_DEG, OMEGA_DEG_S)


def fig_mt_rf(out="mt_rf_figure.png"):
    fig, (axL, axR) = plt.subplots(
        1, 2, figsize=(12.0, 6.0), gridspec_kw=dict(width_ratios=[6.4, 5.6]))

    # ── LEFT: the shared stimulus, with the MT RF ──
    S.draw_stimulus(axL, show_v1_rfs=False)

    # ── RIGHT: that RF magnified, with the real motion inside it ──
    axR.set_aspect("equal"); axR.axis("off")
    pad = MT_R_DEG * 0.16
    axR.set_xlim(MT_C[0] - MT_R_DEG - pad, MT_C[0] + MT_R_DEG + pad * 2.6)
    axR.set_ylim(MT_C[1] - MT_R_DEG - pad, MT_C[1] + MT_R_DEG + pad)
    axR.add_patch(Circle(MT_C, MT_R_DEG, facecolor=SURFACE, edgecolor=INK,
                         lw=2.0, ls=(0, (5, 3)), zorder=1))

    # DIRECTION ONLY — no time extent. A dot dwells ~711 ms in this RF and the
    # trial runs ~1590 ms, so the population turns over ~2.2x: any short window
    # drawn here would be one arbitrary slice of what MT actually integrates.
    # The competition model reads the direction of the input over the whole trial,
    # so that is what this panel shows. The probe belongs to the V1 figure, where
    # the window matches the dwell (211-316 ms).
    #
    # Each arrow is the TRUE local tangent at that dot, not a drawn vertical: the
    # arrows come out near-vertical but visibly fanned, and that fan IS the
    # approximation error that sets the RF size (see MT_R_DEG in the common module).
    ARROW_DEG = 0.15                       # ~2 dot-widths; an indicator, not a path
    inside = S.dots_in(MT_C, MT_R_DEG)
    devs = []
    for p, colour, sense, translates, pdir, coh in inside:
        d = S.local_direction(p, sense)
        axR.add_patch(FancyArrowPatch(p, np.asarray(p) + d * ARROW_DEG,
                                      arrowstyle="-|>", mutation_scale=15,
                                      color=colour, lw=2.6, zorder=4))
        axR.add_patch(Circle(p, DOT_DIAM_DEG / 2, facecolor=colour,
                             edgecolor="none", zorder=6))
        devs.append(abs(np.degrees(np.arctan2(d[0], abs(d[1])))))   # from vertical

    axR.text(MT_C[0] + MT_R_DEG + pad * 0.4, MT_C[1] - 0.16, "CW ≈ down",
             color=GREEN, fontsize=11, fontweight="bold", ha="left", va="center")
    axR.text(MT_C[0] + MT_R_DEG + pad * 0.4, MT_C[1] + 0.16, "CCW ≈ up",
             color=RED, fontsize=11, fontweight="bold", ha="left", va="center")
    fig.text(0.5, 0.008,
             f"rotation {OMEGA_DEG_S:g}°/s · arrows show local direction only, not "
             f"displacement (a dot dwells ~{S.dwell_ms(MT_C, MT_R_DEG):.0f} ms in this RF) · "
             f"MT RF {2*MT_R_DEG:.1f}° diameter at {MT_C[0]:g}° eccentricity · "
             f"dots {DOT_DIAM_DEG:g}° · {S.DENSITY:g} dots/deg²/field",
             ha="center", va="bottom", fontsize=8.5, color=INK2)

    # Margins are pinned rather than left to tight_layout, which reacts to
    # title and legend content and would render the stimulus panel at a
    # slightly different scale in each figure. Both use these exact values.
    fig.subplots_adjust(left=0.015, right=0.985, top=0.865, bottom=0.145,
                        wspace=0.10)

    # Panel labels and headings are fig.text, not set_title, so that A's single
    # line and B's two lines hang from ONE top edge (va="top") instead of each
    # floating a fixed pad above its own axes. Positions are read back from the
    # axes after subplots_adjust rather than guessed.
    HEAD_Y = 0.965
    posL, posR = axL.get_position(), axR.get_position()
    for pos, lab in ((posL, "A"), (posR, "B")):
        fig.text(pos.x0, HEAD_Y, lab, fontsize=15, fontweight="bold",
                 color=INK, ha="left", va="top")
    fig.text(posL.x0 + posL.width / 2, HEAD_Y,
             "Two counter-rotating fields + an off-centre MT RF",
             fontsize=12, color=INK, ha="center", va="top")
    fig.text(posR.x0 + posR.width / 2, HEAD_Y,
             # No terminal periods: in-figure text is a LABEL, and every title
             # and annotation across these figures is punctuation-free. Full
             # stops belong to the caption below, which is prose.
             "MT RF, magnified\n"
             "Rotations ≈ vertical translations within the RF",
             fontsize=12, color=INK, ha="center", va="top", linespacing=1.45)

    fig.savefig(out, dpi=170, facecolor="white")
    plt.close(fig)
    print(f"wrote {out}   ({len(inside)} dots in the magnified RF; local "
          f"direction departs from vertical by up to {max(devs):.0f}°)")


if __name__ == "__main__":
    S.report()
    print()
    fig_mt_rf()
