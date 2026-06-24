"""
ROTATED variant of the biased-competition circuit (90° from
model_schematic_adapting.py / web_model_circuit_adapting.png).

Motivation: lay the Stage-1 channels out as a VERTICAL COLUMN — R1 (CW / first-on)
on top, R_T (translation) in the middle, R2 (CCW / delayed) at the bottom — so
the three neurons line up with the rows of the feature-trajectory, direction-
input, and cascade figures (CW / TRANS / CCW), and the whole thing reads
left -> right: stimulus inputs (left) -> adapting channels -> translation
detector R_TD (right, aligned with the translation row).

This is a NEW figure (web_model_circuit_adapting_rot.png); the original is
untouched so we can revert.

Run:  /usr/bin/python3 model_schematic_adapting_rot.py
"""

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Ellipse, FancyArrowPatch

from web_figures import INK, INK2, ACCENT, CUED, UNCUED, INHIB
from model_schematic_adapting import _blob, _project   # reuse terminal/projection


def _adapt_motif_v(ax, Rc, Ic, rin, rI):
    """Adaptation loop with the interneuron I drawn ABOVE the channel neuron R
    (the 90°-rotated version of the original left-side motif):
        R -> I  excitatory drive (right arc),  I -> R  subtractive '-' (left arc)."""
    ax.add_patch(Circle(Ic, rI, facecolor="white", edgecolor=INK2, lw=1.6,
                        zorder=4))
    ax.text(Ic[0], Ic[1], "$I$", ha="center", va="center", fontsize=10,
            color=INK2, zorder=5)
    # R -> I  (right side, excitatory, up into I)
    pR = (Rc[0] + rin * np.cos(np.radians(60)), Rc[1] + rin * np.sin(np.radians(60)))
    pI = (Ic[0] + rI * np.cos(np.radians(-60)), Ic[1] + rI * np.sin(np.radians(-60)))
    ax.add_patch(FancyArrowPatch(pR, pI, arrowstyle="-|>", mutation_scale=8,
                 connectionstyle="arc3,rad=0.35", color=INK2, lw=1.3,
                 zorder=3, shrinkA=1, shrinkB=1))
    # I -> R  (left side, subtractive '-' terminal on R)
    pImin = (Ic[0] + rI * np.cos(np.radians(240)), Ic[1] + rI * np.sin(np.radians(240)))
    pRmin = (Rc[0] + rin * np.cos(np.radians(120)), Rc[1] + rin * np.sin(np.radians(120)))
    ax.add_patch(FancyArrowPatch(pImin, pRmin, arrowstyle="-",
                 connectionstyle="arc3,rad=0.35", color=INK2, lw=1.3,
                 zorder=3, shrinkA=1, shrinkB=2))
    ax.add_patch(Ellipse(pRmin, 2.4, 2.4, facecolor="white", edgecolor=INK2,
                 lw=1.2, zorder=6))
    ax.text(pRmin[0], pRmin[1], "$-$", ha="center", va="center", fontsize=9,
            color=INK2, zorder=7)


def fig_circuit_rot():
    fig, ax = plt.subplots(figsize=(11.6, 8.0))
    ax.set_xlim(0, 130)
    ax.set_ylim(0, 100)
    ax.set_aspect("equal", adjustable="box")
    ax.axis("off")

    rin, rI = 6.5, 3.4
    xC = 42.0                       # channel-column x
    # Stage-1 channels, top -> bottom = CW / TRANS / CCW (trajectory row order)
    R1 = (xC, 80.0)   # CW  = first-on rotation (adapted)
    T  = (xC, 54.0)   # translation
    R2 = (xC, 28.0)   # CCW = delayed rotation (fresh)
    I1, IT, I2 = (xC, 93.5), (xC, 67.5), (xC, 41.5)   # interneurons above

    def neuron(c, lab, col):
        ax.add_patch(Circle(c, rin, facecolor="white", edgecolor=INK, lw=2.0,
                            zorder=4))
        ax.text(c[0], c[1], lab, ha="center", va="center", fontsize=14,
                color=INK, zorder=5)
        # colour cue at the soma base
        ax.add_patch(Ellipse((c[0], c[1] - rin), 5.0, 2.2, facecolor=col,
                     edgecolor=col, zorder=3, alpha=0.9))

    neuron(R1, "$R_1$", UNCUED)
    neuron(T,  "$R_T$", ACCENT)
    neuron(R2, "$R_2$", CUED)
    for Rc, Ic in ((R1, I1), (T, IT), (R2, I2)):
        _adapt_motif_v(ax, Rc, Ic, rin, rI)

    # ---- stimulus drive arrows (from the LEFT) --------------------------
    for c, lab in ((R1, "first-on field"), (T, "translation"),
                   (R2, "delayed field")):
        ax.add_patch(FancyArrowPatch((22.0, c[1]), (c[0] - rin - 0.5, c[1]),
                     arrowstyle="-|>", mutation_scale=12, color=INK, lw=1.7,
                     zorder=2))
        ax.text(20.5, c[1], lab, ha="right", va="center", fontsize=9.5,
                color=INK2)
    ax.text(22.0, R1[1] + 8.5, "$S$", ha="center", va="center", fontsize=12,
            color=INK)

    # ---- Stage 2 detector on the RIGHT, aligned with the translation row -
    cx, cy, R = 96.0, T[1], 11.0
    ax.add_patch(Circle((cx, cy), R, facecolor="white", edgecolor=INK, lw=2.2,
                        zorder=4))
    ax.text(cx, cy, "$R_{TD}$", ha="center", va="center", fontsize=19,
            color=INK, zorder=5)

    # translation: excitatory (+) into the detector's left
    pT = _blob(ax, (cx, cy), 180, ACCENT, R)
    _project(ax, T, pT, ACCENT, 0.0, rin)
    ax.text(pT[0] - 1.5, pT[1] + 4.2, "$W^{+}$", fontsize=13, color=ACCENT,
            ha="center", va="bottom")
    # rotations: inhibitory (-) into the detector's upper-/lower-left
    pR1 = _blob(ax, (cx, cy), 150, INHIB, R)
    _project(ax, R1, pR1, INHIB, -0.12, rin)
    ax.text(pR1[0] - 1.0, pR1[1] + 3.0, "$W^{-}$", fontsize=13, color=INHIB,
            ha="right", va="bottom")
    pR2 = _blob(ax, (cx, cy), 210, INHIB, R)
    _project(ax, R2, pR2, INHIB, 0.12, rin)
    ax.text(pR2[0] - 1.0, pR2[1] - 3.0, "$W^{-}$", fontsize=13, color=INHIB,
            ha="right", va="top")

    # ---- stage labels ---------------------------------------------------
    ax.text(xC, 99.5, "Stage 1", ha="center", va="center", fontsize=10,
            color=INK2, style="italic")
    ax.text(cx, cy + R + 4.0, "Stage 2", ha="center", va="center", fontsize=10,
            color=INK2, style="italic")

    # ---- equations (below) ----------------------------------------------
    ax.text(22, 17.5, "Stage 1 — adapting channel  ($i = 1, 2, T$)",
            fontsize=10.5, color=INK2, ha="center", va="center")
    s1 = [r"$\tau\,\dot{R}_i = -R_i + N(S_i - w_a I_i)$",
          r"$\tau_a\,\dot{I}_i = -I_i + R_i$",
          r"$N(x) = N_{max}\,[x]_+^{2}/(\sigma_N^{2}+[x]_+^{2})$"]
    for eq, y in zip(s1, (12.0, 7.0, 1.8)):
        ax.text(0, y, eq, fontsize=12, color=INK, ha="left", va="center")

    ax.text(96, 17.5, "Stage 2 — translation detector",
            fontsize=10.5, color=INK2, ha="center", va="center")
    s2 = [(r"$E = W^{+} R_T$", "1"),
          (r"$I = W^{-}(R_1 + R_2)$", "2"),
          (r"$R_{TD} = \dfrac{K\,E}{E + I + \sigma}$", "3")]
    for (eq, n), y in zip(s2, (12.0, 7.0, 1.5)):
        ax.text(74, y, eq, fontsize=12, color=INK, ha="left", va="center")
        ax.text(129, y, f"({n})", fontsize=11, color=INK2, ha="right",
                va="center")

    fig.savefig("web_model_circuit_adapting_rot.png", bbox_inches="tight",
                pad_inches=0.2)
    plt.close(fig)
    print("wrote web_model_circuit_adapting_rot.png")


if __name__ == "__main__":
    fig_circuit_rot()
