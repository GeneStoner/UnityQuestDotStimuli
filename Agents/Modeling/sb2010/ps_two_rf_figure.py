"""
The V1 point-set figure — the SAME stimulus as Figure 2, plus two V1 RFs.

Pairs with `mt_rf_figure.py`. Both take their stimulus panel from
`ps_stimulus_common.draw_stimulus`, and the dot layout is computed once there, so
these two figures are the same picture: flipping between them shows the two V1 RFs
arriving and nothing else moving. That is the point of the pair, and it is why the
stimulus lives in a shared module rather than being duplicated.

  A   the stimulus, the MT RF, and two V1 RFs inside it. Dots only — no motion.
  B   BOTH V1 RFs magnified in one panel, each with its own dot's real trajectory
      through the probe

Two panels, not three. The blow-ups used to occupy a panel each, which left the
figure with no A/B structure and made it the only one of the three sharing this
stimulus that carried no panel letters. Putting both RFs in one panel is also the
older `ps_two_rf_B.png` design, recovered.

PANEL A IS LOAD-BEARING. check_stimulus_panels.py compares this stimulus panel
against mt_rf_figure's and ps_two_hc_figure's and requires them PIXEL-IDENTICAL,
so all three use the identical figsize (12.0, 6.0), width_ratios [6.4, 5.6],
margins and dpi. That is a stricter constraint than it looks: matching panel A's
width alone still fails, because a different overall figure width shifts the whole
panel by a sub-pixel and the check sees every dot move. Change any of it in one
figure and change it in all three.

The pair of V1 RFs is FOUND, not placed — see the module docstring of
`ps_stimulus_common`. Both RFs are guaranteed inside the MT RF by the search space
itself, each holds the same single dot of one surface on every sampled frame, and
no dot of the other surface overlaps either of them. Nothing is deleted from the
display to arrange that.

Run:  /usr/bin/python3 ps_two_rf_figure.py
"""

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
from matplotlib.lines import Line2D

import ps_stimulus_common as S
from ps_stimulus_common import (INK, INK2, SURFACE, RF_R_DEG, RF_DIAM_DEG,
                                DOT_DIAM_DEG, PRE_MS, TRANS_MS, OMEGA_DEG_S,
                                PROBE_DEG_S, ECC_DEG, MT_R_DEG)

# ── panel B's own frame ──
# Its aspect matches the axes (see fig_two_rf) so the drawing fills the panel.
# The two RFs are magnified by RF_MAG and re-centred here; degrees no longer mean
# anything inside this panel, which is why every quantity quoted in it is written
# out in degrees as text.
PB_X = 90.0                      # xlim +-90; ylim below matches the panel aspect
PB_Y0, PB_Y1 = -75.0, 75.0       # 150 tall against 180 wide = 1.20, the panel's
RF_MAG = 30.0 / RF_R_DEG         # RF radius -> 30 units
RF_CX, RF_CY = 48.0, 6.0         # the two RF centres sit at (+-RF_CX, RF_CY)


def _xf(pts, rf_c):
    """Data degrees around one RF centre -> panel-B units, unsigned x."""
    return (np.asarray(pts) - np.asarray(rf_c)) * RF_MAG


def _blowup_into(ax, which, cx):
    """Draw ONE magnified V1 RF into the shared panel, centred at (cx, RF_CY)."""
    p0, colour, sense, translates, rf_c, pdir = S.selected(which)
    centre = np.array([cx, RF_CY])
    R = 30.0

    ax.add_patch(Circle(centre, R, facecolor=SURFACE, edgecolor=INK,
                        lw=2.0, zorder=1))

    pre, during = S.dot_trajectory(p0, sense, translates, pdir)
    S.draw_trajectory(ax, _xf(pre, rf_c) + centre, _xf(during, rf_c) + centre,
                      colour, 2.0, 3.4, 16, z=4)
    dot_r = DOT_DIAM_DEG / 2 * RF_MAG
    ax.add_patch(Circle(_xf(p0, rf_c) + centre, dot_r, facecolor=colour,
                        edgecolor="none", zorder=6))
    ax.add_patch(Circle(_xf(pre[-1], rf_c) + centre, dot_r, facecolor="white",
                        edgecolor=colour, lw=1.8, zorder=6))

    note = ("rotation replaced by\nrightward translation" if translates
            else "rotation continues\nunchanged")
    ax.text(cx, RF_CY + R + 4.0, note, ha="center", va="bottom",
            fontsize=9.5, color=colour, fontweight="bold", linespacing=1.35)

    exc = S.excursion(np.vstack([pre, during]), rf_c)
    # rewrapped narrower than the three-panel version: each RF now has half a
    # panel rather than a whole one
    note2 = (f"\nprobe is {S.COHERENCE:.0%} coherent — this dot is one\n"
             f"of the coherent half; the rest fan over\n"
             f"8 directions at the same speed" if translates else "")
    ax.text(cx, RF_CY - R - 4.0,
            f"dot edge stays within {exc:.3f}° of centre\nRF radius {RF_R_DEG:.2f}° "
            f"({RF_R_DEG/exc:.2f}× margin){note2}",
            ha="center", va="top", fontsize=8.5, color=INK2, linespacing=1.35)
    return colour


def draw_both_blowups(ax):
    """PANEL B — both V1 RFs magnified, side by side in one axes."""
    ax.set_aspect("equal"); ax.axis("off")
    ax.set_xlim(-PB_X, PB_X); ax.set_ylim(PB_Y0, PB_Y1)

    for cx, which, lab, sub in (
            (-RF_CX, "left",  "left V1 RF · red dot",
             "CCW field — first-on (uncued)"),
            (+RF_CX, "right", "right V1 RF · green dot",
             "CW field — delayed-onset (cued)")):
        colour = _blowup_into(ax, which, cx)
        ax.text(cx, RF_CY + 30.0 + 32.0, lab, ha="center", va="bottom",
                fontsize=10.5, fontweight="bold", color=INK)
        ax.text(cx, RF_CY + 30.0 + 26.0, sub, ha="center", va="bottom",
                fontsize=9.5, color=colour)


def fig_two_rf(out="ps_two_rf_figure.png"):
    # THE INVARIANT: all three figures that share draw_stimulus use the IDENTICAL
    # figsize and width_ratios -- (12.0, 6.0) and [6.4, 5.6]. Matching panel A's
    # WIDTH is not enough. A different figure width changes the whole canvas's
    # pixel count, so panel A lands on a different sub-pixel phase and the entire
    # panel shifts by ~1 px; check_stimulus_panels then reports every dot, arc and
    # label as a difference. Diffing the crops shows it instantly -- a shift
    # outlines everything, a real change blobs in one place. Panel B must live
    # within whatever width this leaves it (5.17 in), not the other way round.
    fig, (axL, axR) = plt.subplots(
        1, 2, figsize=(12.0, 6.0), gridspec_kw=dict(width_ratios=[6.4, 5.6]))

    S.draw_stimulus(axL, show_v1_rfs=True)
    draw_both_blowups(axR)

    fig.subplots_adjust(left=0.015, right=0.985, top=0.865, bottom=0.145,
                        wspace=0.10)

    # Panel letters and headings as fig.text, hanging from ONE top edge — the
    # same mechanism mt_rf_figure.py and ps_two_hc_figure.py use, so all three
    # figures now carry the same A/B convention.
    HEAD_Y = 0.965
    posL, posR = axL.get_position(), axR.get_position()
    for pos, lab in ((posL, "A"), (posR, "B")):
        fig.text(pos.x0, HEAD_Y, lab, fontsize=15, fontweight="bold",
                 color=INK, ha="left", va="top")
    fig.text(posL.x0 + posL.width / 2, HEAD_Y,
             "The same stimulus, with two V1 RFs",
             fontsize=12, color=INK, ha="center", va="top")
    fig.text(posR.x0 + posR.width / 2, HEAD_Y,
             "Both V1 RFs magnified, with each dot's path through the probe",
             fontsize=12, color=INK, ha="center", va="top")

    fig.legend(handles=[
        Line2D([0], [0], color=INK2, lw=2.0, alpha=0.55,
               label=f"{PRE_MS:g} ms before the probe"),
        Line2D([0], [0], color=INK2, lw=3.4, label=f"{TRANS_MS:g} ms probe window"),
        Line2D([0], [0], marker="o", color="none", markerfacecolor="white",
               markeredgecolor=INK2, markersize=8, label="probe onset")],
        loc="lower center", ncol=3, frameon=False, fontsize=9.5,
        bbox_to_anchor=(posR.x0 + posR.width / 2, 0.045))

    fig.text(0.5, 0.008,
             f"V1 RF {RF_DIAM_DEG:.2f}° diameter, fixed (not scaled with eccentricity), "
             f"at {ECC_DEG:.2f}° · MT RF {2*MT_R_DEG:.1f}° · dots {DOT_DIAM_DEG:g}° · "
             f"{S.DENSITY:g} dots/deg²/field · rotation {OMEGA_DEG_S:g}°/s, "
             f"probe {PROBE_DEG_S:g}°/s",
             ha="center", va="bottom", fontsize=8.5, color=INK2)

    fig.savefig(out, dpi=170, facecolor="white")
    plt.close(fig)
    print(f"wrote {out}   (2 panels: stimulus + both RFs magnified)")


if __name__ == "__main__":
    S.report()
    print()
    fig_two_rf()
