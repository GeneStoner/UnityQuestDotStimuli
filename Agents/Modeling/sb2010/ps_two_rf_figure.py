"""
The V1 point-set figure — the SAME stimulus as Figure 2, plus two V1 RFs.

Pairs with `mt_rf_figure.py`. Both take their stimulus panel from
`ps_stimulus_common.draw_stimulus`, and the dot layout is computed once there, so
these two figures are the same picture: flipping between them shows the two V1 RFs
arriving and nothing else moving. That is the point of the pair, and it is why the
stimulus lives in a shared module rather than being duplicated.

  LEFT    the stimulus, the MT RF, and two V1 RFs inside it. Dots only — no motion.
  MIDDLE  the left V1 RF magnified: its red dot's real trajectory through the probe
  RIGHT   the right V1 RF magnified: its green dot's

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


def _blowup(ax, which, panel_lab, sub):
    p0, colour, sense, translates, rf_c, pdir = S.selected(which)
    ax.set_aspect("equal"); ax.axis("off")
    pad = RF_R_DEG * 0.34
    ax.set_xlim(rf_c[0] - RF_R_DEG - pad, rf_c[0] + RF_R_DEG + pad)
    ax.set_ylim(rf_c[1] - RF_R_DEG - pad, rf_c[1] + RF_R_DEG + pad * 1.5)
    ax.add_patch(Circle(rf_c, RF_R_DEG, facecolor=SURFACE, edgecolor=INK,
                        lw=2.0, zorder=1))

    pre, during = S.dot_trajectory(p0, sense, translates, pdir)
    S.draw_trajectory(ax, pre, during, colour, 2.0, 3.4, 16, z=4)
    ax.add_patch(Circle(p0, DOT_DIAM_DEG / 2, facecolor=colour,
                        edgecolor="none", zorder=6))
    ax.add_patch(Circle(pre[-1], DOT_DIAM_DEG / 2, facecolor="white",
                        edgecolor=colour, lw=1.8, zorder=6))

    note = ("rotation replaced by\nrightward translation" if translates
            else "rotation continues\nunchanged")
    ax.text(rf_c[0], rf_c[1] + RF_R_DEG + pad * 0.45, note, ha="center",
            va="bottom", fontsize=9.5, color=colour, fontweight="bold")

    exc = S.excursion(np.vstack([pre, during]), rf_c)
    ax.text(rf_c[0], rf_c[1] - RF_R_DEG - pad * 0.45,
            f"dot edge stays within {exc:.3f}° of centre\nRF radius {RF_R_DEG:.2f}° "
            f"({RF_R_DEG/exc:.2f}× margin)",
            ha="center", va="top", fontsize=8.5, color=INK2)
    ax.set_title(f"{panel_lab}\n{sub}", fontsize=10.5, color=INK, pad=6)


def fig_two_rf(out="ps_two_rf_figure.png"):
    fig, axes = plt.subplots(
        1, 3, figsize=(15.2, 6.0), gridspec_kw=dict(width_ratios=[6.4, 4.4, 4.4]))

    S.draw_stimulus(axes[0], show_v1_rfs=True)
    axes[0].set_title("The same stimulus, with two V1 RFs inside the MT RF",
                      fontsize=12, color=INK, pad=8)

    _blowup(axes[1], "left", "left V1 RF · red dot",
            "CCW field — first-on (uncued)")
    _blowup(axes[2], "right", "right V1 RF · green dot",
            "CW field — delayed-onset (cued)")

    fig.legend(handles=[
        Line2D([0], [0], color=INK2, lw=2.0, alpha=0.55,
               label=f"{PRE_MS:g} ms before the probe"),
        Line2D([0], [0], color=INK2, lw=3.4, label=f"{TRANS_MS:g} ms probe window"),
        Line2D([0], [0], marker="o", color="none", markerfacecolor="white",
               markeredgecolor=INK2, markersize=8, label="probe onset")],
        loc="lower center", ncol=3, frameon=False, fontsize=9.5,
        bbox_to_anchor=(0.72, 0.055))

    fig.text(0.5, 0.008,
             f"V1 RF {RF_DIAM_DEG:.2f}° diameter, fixed (not scaled with eccentricity), "
             f"at {ECC_DEG:.2f}° · MT RF {2*MT_R_DEG:.1f}° · dots {DOT_DIAM_DEG:g}° · "
             f"{S.DENSITY:g} dots/deg²/field · rotation {OMEGA_DEG_S:g}°/s, "
             f"probe {PROBE_DEG_S:g}°/s",
             ha="center", va="bottom", fontsize=8.5, color=INK2)

    # Margins are pinned rather than left to tight_layout, which reacts to
    # title and legend content and would render the stimulus panel at a
    # slightly different scale in each figure. Both use these exact values.
    fig.subplots_adjust(left=0.015, right=0.985, top=0.865, bottom=0.145,
                        wspace=0.10)
    fig.savefig(out, dpi=170, facecolor="white")
    plt.close(fig)
    print(f"wrote {out}")


if __name__ == "__main__":
    S.report()
    print()
    fig_two_rf()
