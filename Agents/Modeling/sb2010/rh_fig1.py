"""
Reynolds & Heeger (2009) FIGURE 1 layout — the plus-sign flow schematic —
rendered for the SB delayed-onset stimulus using the VERIFIED port of
attentionModel.m.

Layout (after R&H Fig. 1):

                 [ Attention field ]
    [ Stimulus ] [ Stimulus drive  ] [ Population response ]
                 [ Suppressive drive] [ equations ]

Flow arrows: stimulus -> stimulus drive; attention field -> stimulus drive;
stimulus drive -> suppressive drive; stimulus drive (normalized by the
suppressive drive) -> population response.

All fields come from the verified port, so the suppressive drive
I = E * (I_x ⊗ I_θ) is the broadly-pooled drive — present throughout the
trial, not just during the translation.

Run:  /usr/bin/python3 rh_fig1.py
"""

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.patches import FancyArrowPatch

from parameters import T_END, T_TRANS_START, T_TRANS_END
from rh_activity_maps import cascade, SIGMA
from sb_rh_verified import (
    THETA_PREFS, ETHETA_WIDTH, ITHETA_WIDTH, ATTN_DIR_DEG, APEAK, ABASE,
)


def _map(ax, mat, t, title):
    vmax = mat.max() if mat.max() > 0 else 1.0
    ax.imshow(mat, extent=[t[0], t[-1], THETA_PREFS[0], THETA_PREFS[-1]],
              origin="lower", aspect="auto", cmap="gray_r", vmin=0, vmax=vmax)
    for tx in (T_TRANS_START, T_TRANS_END):
        ax.axvline(tx, color="#C0392B", lw=0.6, alpha=0.8)
    ax.set_yticks([-180, -90, 0, 90, 180])
    ax.set_yticklabels(["±180", "−90", "0", "90", "180"], fontsize=7)
    ax.set_xlabel("Time (ms)", fontsize=8)
    ax.set_ylabel("Pref. dir. (°)", fontsize=8)
    ax.set_title(title, fontsize=10.5, fontweight="bold")
    ax.tick_params(labelsize=7)


def _arrow(fig, a, b, color="#444"):
    p1, p2 = a.get_position(), b.get_position()
    if p2.x0 > p1.x1:                       # b to the right
        xs, ys, xe, ye = p1.x1, (p1.y0 + p1.y1) / 2, p2.x0, (p2.y0 + p2.y1) / 2
    elif p2.x1 < p1.x0:                      # b to the left
        xs, ys, xe, ye = p1.x0, (p1.y0 + p1.y1) / 2, p2.x1, (p2.y0 + p2.y1) / 2
    elif p2.y0 > p1.y1:                      # b above
        xs, ys, xe, ye = (p1.x0 + p1.x1) / 2, p1.y1, (p2.x0 + p2.x1) / 2, p2.y0
    else:                                    # b below
        xs, ys, xe, ye = (p1.x0 + p1.x1) / 2, p1.y0, (p2.x0 + p2.x1) / 2, p2.y1
    fig.patches.append(FancyArrowPatch(
        (xs, ys), (xe, ye), transform=fig.transFigure,
        arrowstyle="-|>,head_width=4,head_length=8",
        color=color, lw=1.7, shrinkA=6, shrinkB=6, zorder=50))


def _equations(ax):
    ax.axis("off")
    ax.text(0.0, 1.0, "Cascade  (Reynolds & Heeger, 2009)", fontsize=10.5,
            fontweight="bold", va="top", transform=ax.transAxes)
    for y, s in [(0.83, r"$E_{\rm raw} = \mathrm{stim} \ast (E_x \otimes E_\theta)$"),
                 (0.67, r"$E = A(\theta)\, E_{\rm raw}$"),
                 (0.51, r"$I = E \ast (I_x \otimes I_\theta)$"),
                 (0.33, r"$R = \dfrac{E}{\,I + \sigma\,}$")]:
        ax.text(0.0, y, s, fontsize=13, va="top", transform=ax.transAxes)
    ax.text(0.0, 0.14,
            f"$E_\\theta\\,\\sigma$={ETHETA_WIDTH:.0f}°,  "
            f"$I_\\theta\\,\\sigma$={ITHETA_WIDTH:.0f}° (pool all θ)\n"
            f"$\\theta_{{\\rm attn}}$={ATTN_DIR_DEG:.0f}°,  "
            f"a/b={APEAK:.0f}/{ABASE:.0f},  σ={SIGMA:.0e}",
            fontsize=8, color="#555", va="top", transform=ax.transAxes)


def render(condition, motion_swap, out, page_title):
    dt = 1.0
    t = np.arange(0.0, T_END + dt, dt)
    c = cascade(condition, motion_swap, t)

    fig = plt.figure(figsize=(13.5, 10.0))
    gs = gridspec.GridSpec(
        3, 3, width_ratios=[1.0, 1.1, 1.1], height_ratios=[0.85, 1.0, 0.85],
        left=0.07, right=0.97, top=0.90, bottom=0.07, hspace=0.55, wspace=0.34)

    ax_A    = fig.add_subplot(gs[0, 1])   # top:    attention field
    ax_stim = fig.add_subplot(gs[1, 0])   # left:   stimulus
    ax_E    = fig.add_subplot(gs[1, 1])   # centre: stimulus drive
    ax_R    = fig.add_subplot(gs[1, 2])   # right:  population response
    ax_S    = fig.add_subplot(gs[2, 1])   # bottom: suppressive drive
    ax_eq   = fig.add_subplot(gs[2, 2])   # bottom-right: equations

    _map(ax_A,    c["A"],    t, "Attention field  $A(\\theta)$")
    _map(ax_stim, c["stim"], t, "Stimulus")
    _map(ax_E,    c["Eraw"], t, "Stimulus drive  $E$")
    _map(ax_R,    c["R"],    t, "Population response  $R$")
    _map(ax_S,    c["I"],    t, "Suppressive drive  $I$")
    _equations(ax_eq)

    fig.suptitle(page_title, fontsize=13, fontweight="bold", y=0.95)
    fig.canvas.draw()
    _arrow(fig, ax_stim, ax_E)               # stimulus -> drive
    _arrow(fig, ax_A,    ax_E, color="#888")  # attention -> drive
    _arrow(fig, ax_E,    ax_S, color="#888")  # drive -> suppressive
    _arrow(fig, ax_E,    ax_R)               # drive -> response
    _arrow(fig, ax_S,    ax_R, color="#aaa")  # suppressive normalizes response

    fig.savefig(out, dpi=160, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"wrote {out}")


def main():
    render("cued", False, "rh_fig1_cued.png",
           "Normalization-model cascade — CUED  (R&H Figure 1 layout)")
    render("uncued", False, "rh_fig1_uncued.png",
           "Normalization-model cascade — UNCUED  (R&H Figure 1 layout)")


if __name__ == "__main__":
    main()
