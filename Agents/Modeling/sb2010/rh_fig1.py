"""
Reynolds & Heeger (2009) FIGURE 1 layout — matched to the published figure —
rendered for the SB delayed-onset stimulus using the VERIFIED port of
attentionModel.m.

Published topology (their Fig. 1):

                          [ Attention field ]
                                    |  (down into ×)
   [Stimulus] -> [Stimulus drive] -> (×) ----> (÷) -> [Population response]
                                      |               ^
                                 pool |  (the PRODUCT  | (denominator)
                                      v   E·A, pooled) |
                              [ Suppressive drive ] ---'

The stimulus drive is multiplied (×) by the attention field; that PRODUCT is
both the numerator (passed to ÷) and — pooled over the feature axis — the
suppressive drive that forms the denominator.  R = (E·A) / (pool(E·A) + σ).

Their axes are RF-center (x) × orientation preference (y); ours substitute
TIME for RF center, so the maps run over direction × time.  We do not pool over
time, so the pooling branch is labelled "pool over direction".

Run:  /usr/bin/python3 rh_fig1.py
"""

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch

from parameters import T_END, T_TRANS_START, T_TRANS_END
from rh_activity_maps import cascade
from sb_rh_verified import THETA_PREFS


def _map(ax, mat, t, title):
    vmax = mat.max() if mat.max() > 0 else 1.0
    ax.imshow(mat, extent=[t[0], t[-1], THETA_PREFS[0], THETA_PREFS[-1]],
              origin="lower", aspect="auto", cmap="gray", vmin=0, vmax=vmax)
    for tx in (T_TRANS_START, T_TRANS_END):
        ax.axvline(tx, color="#C0392B", lw=0.6, alpha=0.8)
    ax.set_yticks([-90, 0, 90]); ax.set_yticklabels(["−90", "0", "90"], fontsize=6)
    ax.set_xticks([0, 800, 1600]); ax.set_xticklabels(["0", "800", "1600"], fontsize=6)
    ax.tick_params(length=2, pad=1.5)
    if title:
        ax.set_title(title, fontsize=10.5, fontweight="bold", pad=4)


def _arrow(fig, x0, y0, x1, y1, color="#333"):
    fig.patches.append(FancyArrowPatch(
        (x0, y0), (x1, y1), transform=fig.transFigure,
        arrowstyle="-|>,head_width=4,head_length=8", color=color, lw=1.7,
        zorder=40))


def _op(fig, x, y, sym):
    fig.text(x, y, sym, ha="center", va="center", fontsize=17, zorder=61,
             bbox=dict(boxstyle="circle,pad=0.3", facecolor="white",
                       edgecolor="black", lw=1.8))


def _elbow(fig, x0, y0, x1, y1, color="#666"):
    """Right-angle arrow: leaves (x0,y0) horizontally, then turns up to (x1,y1)."""
    fig.patches.append(FancyArrowPatch(
        (x0, y0), (x1, y1), transform=fig.transFigure,
        connectionstyle="angle,angleA=0,angleB=90,rad=0",
        arrowstyle="-|>,head_width=4,head_length=8", color=color, lw=1.7,
        zorder=40))


def render(condition, motion_swap, out, page_title):
    dt = 1.0
    t = np.arange(0.0, T_END + dt, dt)
    c = cascade(condition, motion_swap, t)

    FIG_W, FIG_H = 16.0, 9.0
    PW = 0.125                       # panel width  (figure fraction)
    PH = PW * FIG_W / FIG_H          # panel height -> SQUARE in display, all equal
    R = 0.024                        # operator-circle clearance (x)

    fig = plt.figure(figsize=(FIG_W, FIG_H))
    XMUL, XDIV, YMID = 0.40, 0.51, 0.50     # operator x-positions, row centre
    XCOL = XMUL                              # attention/suppressive share the × column
    main_b = YMID - PH / 2                   # main-row panel bottom
    A_B, S_B = 0.700, 0.085                  # attention bottom, suppressive bottom

    ax_stim = fig.add_axes([0.040,        main_b, PW, PH])
    ax_E    = fig.add_axes([0.190,        main_b, PW, PH])
    ax_R    = fig.add_axes([0.610,        main_b, PW, PH])
    ax_A    = fig.add_axes([XCOL - PW / 2, A_B,   PW, PH])
    ax_S    = fig.add_axes([XCOL - PW / 2, S_B,   PW, PH])

    _map(ax_stim, c["stim"], t, "Stimulus")
    _map(ax_E,    c["Eraw"], t, "Stimulus drive  $E$")
    _map(ax_A,    c["A"],    t, "Attention field  $A$")
    _map(ax_R,    c["R"],    t, "Population response  $R$")
    _map(ax_S,    c["I"],    t, "")                         # label goes below
    fig.text(XCOL, S_B - 0.045, "Suppressive drive  $I$", ha="center", va="top",
             fontsize=10.5, fontweight="bold")

    s_top, main_top = S_B + PH, main_b + PH

    # main horizontal flow
    _arrow(fig, 0.040 + PW, YMID, 0.190 - 0.004, YMID)      # stimulus -> drive
    _arrow(fig, 0.190 + PW, YMID, XMUL - R,       YMID)     # drive    -> ×
    _arrow(fig, XMUL + R,   YMID, XDIV - R,       YMID)     # × (product) -> ÷
    _arrow(fig, XDIV + R,   YMID, 0.610 - 0.004,  YMID)     # ÷        -> response
    _op(fig, XMUL, YMID, "×")
    _op(fig, XDIV, YMID, "÷")

    # attention -> ×  (down) ; product -> suppressive (straight down, same column)
    _arrow(fig, XCOL, A_B,         XCOL, YMID + R, color="#666")
    _arrow(fig, XCOL, YMID - R,    XCOL, s_top,    color="#666")
    fig.text(XCOL - 0.055, (s_top + main_b) / 2, "pool over\ndirection",
             fontsize=8, style="italic", color="#555", ha="center", va="center")
    # suppressive -> ÷  (elbow: horizontal, then up)
    _elbow(fig, XCOL + PW / 2, S_B + PH / 2, XDIV, YMID - R, color="#666")

    fig.suptitle(page_title, fontsize=13, fontweight="bold", y=0.965)
    fig.savefig(out, dpi=160, facecolor="white")
    plt.close(fig)
    print(f"wrote {out}")


def main():
    render("cued", False, "rh_fig1_cued.png",
           "Normalization-model cascade — CUED  (Reynolds & Heeger Figure 1 layout)")
    render("uncued", False, "rh_fig1_uncued.png",
           "Normalization-model cascade — UNCUED  (Reynolds & Heeger Figure 1 layout)")


if __name__ == "__main__":
    main()
