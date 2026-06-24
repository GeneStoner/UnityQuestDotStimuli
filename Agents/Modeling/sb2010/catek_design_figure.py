"""
Our own remake of the delayed-onset design schematic (after Catek et al., 2022,
Cortex, Fig. 1) — NOT a copy of the published figure.

Panel A: the trial as a sequence of transparent counter-rotating dot-field
frames — first field rotates, the delayed field appears, both rotate, one field
translates briefly, both resume rotating — for the cued and uncued cases.
Panel B: the same trial as a feature-direction timeline (CW / CCW / translation),
colour = dot field, line style = field identity, the translating field dips into
the translation band during the brief window.

Run:  /usr/bin/python3 catek_design_figure.py
"""

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.patches import Circle, FancyArrowPatch

GREEN, RED = "#2e8b57", "#c0392b"     # first field (CW), delayed field (CCW)
INK = "#1e1e2a"

EPOCHS = ["rotation", "second\ndot field", "rotation", "translation", "rotation"]
TDIR = np.array([0.62, 0.42]); TDIR = TDIR / np.hypot(*TDIR)   # translation dir


def _dots(n, seed, r=0.9):
    rg = np.random.default_rng(seed)
    pts = []
    while len(pts) < n:
        p = rg.uniform(-r, r, 2)
        if np.hypot(*p) < r * 0.97:
            pts.append(p)
    return np.array(pts)


def _rotate(pts, deg):
    a = np.radians(deg); c, s = np.cos(a), np.sin(a)
    return pts @ np.array([[c, -s], [s, c]]).T


def _rot_arrow(ax, sense, color, R=1.12):
    a0, a1 = (118, 72) if sense == "CW" else (62, 108)
    th = np.radians(np.linspace(a0, a1, 16))
    ax.plot(R * np.cos(th), R * np.sin(th), color=color, lw=1.4,
            solid_capstyle="round")
    p0 = (R * np.cos(th[-2]), R * np.sin(th[-2]))
    p1 = (R * np.cos(th[-1]), R * np.sin(th[-1]))
    ax.add_patch(FancyArrowPatch(p0, p1, arrowstyle="-|>", mutation_scale=9,
                                 color=color, lw=0))


def _snapshot(ax, fields, translate=None):
    """fields: list of (color, dots, sense). translate: color of translating field."""
    ax.add_patch(Circle((0, 0), 1.0, fill=False, ec="#aaa", lw=1.1))
    for color, dots, sense in fields:
        ax.scatter(dots[:, 0], dots[:, 1], s=4.5, color=color, zorder=3)
        if translate == color:
            for p in dots[::3]:
                ax.add_patch(FancyArrowPatch(p, p + TDIR * 0.42, arrowstyle="-|>",
                             mutation_scale=7, color=color, lw=1.0, zorder=4))
        elif sense:
            _rot_arrow(ax, sense, color)
    ax.plot(0, 0, marker="+", ms=6, mew=1.3, color=INK, zorder=5)
    ax.set_xlim(-1.32, 1.32); ax.set_ylim(-1.32, 1.32)
    ax.set_aspect("equal"); ax.axis("off")


def _panelA(fig, gs_top):
    g = _dots(13, 1); r = _dots(13, 2)
    gsA = gridspec.GridSpecFromSubplotSpec(2, 5, subplot_spec=gs_top,
                                           hspace=0.12, wspace=0.12)
    for row, cond in enumerate(["cued", "uncued"]):
        transl = RED if cond == "cued" else GREEN     # cued: delayed(red) translates
        for col in range(5):
            ax = fig.add_subplot(gsA[row, col])
            gd = _rotate(g, -16 * col)                 # green rotates CW
            rd = _rotate(r,  16 * col)                 # red rotates CCW
            if col == 0:                               # first field only
                fields = [(GREEN, gd, "CW")]
            else:
                fields = [(GREEN, gd, "CW"), (RED, rd, "CCW")]
            _snapshot(ax, fields, translate=transl if col == 3 else None)
            if row == 0:
                ax.set_title(EPOCHS[col], fontsize=8.5, color=INK, pad=3)
            if col == 0:
                ax.text(-1.65, 0, cond, rotation=90, ha="center", va="center",
                        fontsize=11, fontweight="bold", color=INK)
    # time arrow under the panel (in the gap between A and B)
    fig.add_artist(FancyArrowPatch((0.13, 0.475), (0.92, 0.475),
                   transform=fig.transFigure, arrowstyle="-|>",
                   mutation_scale=12, color="#888", lw=1.4))
    fig.text(0.525, 0.487, "time", fontsize=9, style="italic", color="#666",
             ha="center")


def _traj(ax, cond):
    T, T1, W0, W1 = 1.0, 0.30, 0.55, 0.66          # schematic time fractions
    CCW, TRANS, CW = 2, 1, 0
    ax.set_ylim(-0.5, 2.5); ax.set_xlim(0, T)
    ax.set_yticks([CW, TRANS, CCW]); ax.set_yticklabels(["CW", "transl.", "CCW"],
                                                        fontsize=7.5)
    ax.set_xticks([]); ax.tick_params(length=0)
    for y in (CW, TRANS, CCW):
        ax.axhline(y, color="#ece9e3", lw=1, zorder=0)
    ax.axvspan(W0, W1, color="0.85", alpha=0.6, zorder=0)
    # green = first field (CW), solid ; red = delayed field (CCW), dashed (from T1)
    if cond == "cued":          # delayed (red) translates
        ax.plot([0, T], [CW, CW], color=GREEN, lw=2.2, solid_capstyle="butt")
        ax.plot([T1, W0], [CCW, CCW], color=RED, lw=2.2, ls=(0, (4, 2)))
        ax.plot([W0, W0, W1, W1], [CCW, TRANS, TRANS, CCW], color=RED, lw=2.2,
                ls=(0, (4, 2)))
        ax.plot([W1, T], [CCW, CCW], color=RED, lw=2.2, ls=(0, (4, 2)))
    else:                        # first (green) translates
        ax.plot([T1, T], [CCW, CCW], color=RED, lw=2.2, ls=(0, (4, 2)))
        ax.plot([0, W0], [CW, CW], color=GREEN, lw=2.2)
        ax.plot([W0, W0, W1, W1], [CW, TRANS, TRANS, CW], color=GREEN, lw=2.2)
        ax.plot([W1, T], [CW, CW], color=GREEN, lw=2.2)
    ax.text(0.012, 2.32, cond, fontsize=10, fontweight="bold", color=INK,
            va="top")


def main():
    fig = plt.figure(figsize=(11.0, 7.6))
    gs = gridspec.GridSpec(2, 1, height_ratios=[1.0, 0.62], top=0.93, bottom=0.06,
                           left=0.06, right=0.97, hspace=0.30)
    _panelA(fig, gs[0])

    gsB = gridspec.GridSpecFromSubplotSpec(2, 1, subplot_spec=gs[1], hspace=0.32)
    for i, cond in enumerate(["cued", "uncued"]):
        _traj(fig.add_subplot(gsB[i]), cond)

    fig.text(0.065, 0.955, "A", fontsize=15, fontweight="bold")
    fig.text(0.065, 0.40, "B", fontsize=15, fontweight="bold")
    fig.savefig("catek_design_figure.png", dpi=170, bbox_inches="tight",
                facecolor="white")
    plt.close(fig)
    print("wrote catek_design_figure.png")


if __name__ == "__main__":
    main()
