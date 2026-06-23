"""
Reynolds & Heeger (2009) FIGURE 1 layout — matched to the published figure —
rendered for the SB delayed-onset stimulus using the VERIFIED port of
attentionModel.m.

Published layout (their Fig. 1), a left-to-right flow with two circled
operators in series:

                          [ Attention field ]
                                  |  v
   [Stimulus] -> [Stimulus drive] -> (x) -> (÷) -> [Population response]
                                  |pool        ^
                                  v            |
                          [ Suppressive drive ]'

The stimulus drive is multiplied (×) by the attention field, then divided (÷)
by the suppressive drive, to give the population response.  The suppressive
drive is the product pooled over the feature axis.  Their axes are
RF-center (x) × orientation preference (y); ours substitute TIME for RF center,
so the maps run over direction × time.  Because we do not pool over time, the
pooling branch is labelled "pool over direction" (see the note under Fig. 7).

All fields come from the verified port.

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
              origin="lower", aspect="auto", cmap="gray_r", vmin=0, vmax=vmax)
    for tx in (T_TRANS_START, T_TRANS_END):
        ax.axvline(tx, color="#C0392B", lw=0.6, alpha=0.8)
    ax.set_yticks([-90, 0, 90]); ax.set_yticklabels(["−90", "0", "90"], fontsize=6)
    ax.set_xticks([0, 800, 1600]); ax.set_xticklabels(["0", "800", "1600"], fontsize=6)
    ax.tick_params(length=2, pad=1.5)
    # axis identity, small, only where it won't collide (left edge / bottom)
    ax.set_ylabel("dir (°)", fontsize=6.5, labelpad=1)
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


def render(condition, motion_swap, out, page_title):
    dt = 1.0
    t = np.arange(0.0, T_END + dt, dt)
    c = cascade(condition, motion_swap, t)

    fig = plt.figure(figsize=(15.0, 7.5))
    #               [left,  bottom, width, height]
    ax_stim = fig.add_axes([0.020, 0.37, 0.120, 0.27])
    ax_E    = fig.add_axes([0.180, 0.37, 0.135, 0.27])
    ax_R    = fig.add_axes([0.530, 0.37, 0.150, 0.27])
    ax_A    = fig.add_axes([0.310, 0.72, 0.130, 0.22])   # top, over the ×
    ax_S    = fig.add_axes([0.360, 0.06, 0.130, 0.22])   # bottom, under × / ÷

    _map(ax_stim, c["stim"], t, "Stimulus")
    _map(ax_E,    c["Eraw"], t, "Stimulus drive  $E$")
    _map(ax_A,    c["A"],    t, "Attention field  $A$")
    _map(ax_R,    c["R"],    t, "Population response  $R$")
    _map(ax_S,    c["I"],    t, "Suppressive drive  $I$")

    XMUL, XDIV, YMID = 0.375, 0.458, 0.505

    # main horizontal flow
    _arrow(fig, 0.142, YMID, 0.176, YMID)            # stimulus -> drive
    _arrow(fig, 0.317, YMID, 0.352, YMID)            # drive    -> ×
    _arrow(fig, 0.398, YMID, 0.435, YMID)            # ×        -> ÷
    _arrow(fig, 0.481, YMID, 0.526, YMID)            # ÷        -> response
    _op(fig, XMUL, YMID, "×")
    _op(fig, XDIV, YMID, "÷")

    # attention field feeds down into ×
    _arrow(fig, XMUL, 0.715, XMUL, 0.535, color="#666")
    # pooling branch: drive -> suppressive drive (pool over direction)
    _arrow(fig, 0.330, 0.355, 0.412, 0.290, color="#666")
    fig.text(0.300, 0.318, "pool over\ndirection", fontsize=8, style="italic",
             color="#555", ha="center", va="center")
    # suppressive drive feeds up into ÷
    _arrow(fig, 0.470, 0.285, XDIV, 0.478, color="#666")

    fig.suptitle(page_title, fontsize=13, fontweight="bold", y=0.99)
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
