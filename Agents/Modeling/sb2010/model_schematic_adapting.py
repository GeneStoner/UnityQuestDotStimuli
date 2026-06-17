"""
Two new SB-2010 figures, styled to mesh with the R&H normalization figures
so model components can be reused across the modeling story:

  1. web_model_circuit_adapting.png — the biased-competition circuit
     (web_model_circuit.png) with the Stage-1 adapting channels added below
     the pool.  Reynolds / Reynolds-Chelazzi-Desimone-1999 idiom; symbols
     only, the caption carries the cortical mapping.

  2. web_model_adapting_inputs.png — the Stage-1 adapting responses that
     feed the detector, CUED vs UNCUED, in the same palette / window-shade /
     delayed-onset-marker idiom as translation_response.png and the R&H
     response set.  Colour = field role (red = first-on/adapted,
     green = delayed/fresh, blue = translation), identical across columns,
     so the only thing that differs between CUED and UNCUED is WHICH channel
     gaps during the translation window.

Run:  /usr/bin/python3 model_schematic_adapting.py
"""

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Ellipse, FancyArrowPatch

# Reuse the exact site palette + rcParams from web_figures.  Importing it has
# no side effects beyond the shared style (its figure drawing is under
# __main__), so the two new figures are locked to the same visual language.
from web_figures import (
    INK, INK2, SURFACE, BORDER, ACCENT,
    CUED, UNCUED, INHIB, GRID, WIN, _style_axes,
)
from parameters import (
    T_END, T_FIELD2_ON, T_TRANS_START, T_TRANS_END,
)
from model import simulate_adapting_channel
from stimulus import channels_for_trial


# ======================================================================
# FIGURE 1 — biased-competition circuit + Stage-1 adapting channels
# ======================================================================

def _blob(ax, center, theta_deg, color, r):
    """Filled synaptic terminal tangent on a soma of radius r."""
    th = np.radians(theta_deg)
    P = (center[0] + r * np.cos(th), center[1] + r * np.sin(th))
    ax.add_patch(Ellipse(P, 4.6, 2.2, angle=theta_deg + 90,
                         facecolor=color, edgecolor=color, zorder=6))
    return P


def _project(ax, src, P, color, rad, r_src, lw=2.0):
    """Curved projection from a source soma (radius r_src) to terminal P."""
    d = (P[0] - src[0], P[1] - src[1])
    L = np.hypot(*d)
    start = (src[0] + d[0] / L * r_src, src[1] + d[1] / L * r_src)
    ax.add_patch(FancyArrowPatch(
        start, P, arrowstyle="-", connectionstyle=f"arc3,rad={rad}",
        color=color, lw=lw, zorder=2, shrinkA=0, shrinkB=2))


def _adapt_motif(ax, Rc, Ic, rin, rI):
    """Reciprocal adaptation loop between a channel neuron R (center Rc) and
    its adaptation interneuron I (center Ic, drawn to the LEFT of R):
        R -> I   excitatory drive   (Eq 5:  tau_a dI/dt = -I + R)
        I -> R   subtractive self-inhibition, '-' terminal (Eq 4: -w_a I)."""
    # interneuron soma
    ax.add_patch(Circle(Ic, rI, facecolor="white", edgecolor=INK2, lw=1.6,
                        zorder=4))
    ax.text(Ic[0], Ic[1], "$I$", ha="center", va="center", fontsize=11,
            color=INK2, zorder=5)

    # R -> I  (upper arc, excitatory drive)
    a = np.radians(152)
    b = np.radians(28)
    pR = (Rc[0] + rin * np.cos(a), Rc[1] + rin * np.sin(a))
    pI = (Ic[0] + rI * np.cos(b), Ic[1] + rI * np.sin(b))
    ax.add_patch(FancyArrowPatch(pR, pI, arrowstyle="-|>", mutation_scale=9,
                 connectionstyle="arc3,rad=0.35", color=INK2, lw=1.4,
                 zorder=3, shrinkA=1, shrinkB=1))

    # I -> R  (lower arc, '-' subtractive terminal on R)
    a2 = np.radians(208)
    b2 = np.radians(-28)
    pImin = (Ic[0] + rI * np.cos(b2), Ic[1] + rI * np.sin(b2))
    pRmin = (Rc[0] + rin * np.cos(a2), Rc[1] + rin * np.sin(a2))
    ax.add_patch(FancyArrowPatch(pImin, pRmin, arrowstyle="-",
                 connectionstyle="arc3,rad=0.35", color=INK2, lw=1.4,
                 zorder=3, shrinkA=1, shrinkB=2))
    ax.add_patch(Ellipse(pRmin, 2.6, 2.6, facecolor="white",
                 edgecolor=INK2, lw=1.3, zorder=6))
    ax.text(pRmin[0], pRmin[1], "$-$", ha="center", va="center",
            fontsize=10, color=INK2, zorder=7)


def fig_circuit_adapting():
    fig, ax = plt.subplots(figsize=(8.4, 9.4))
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.set_aspect("equal", adjustable="box")
    ax.axis("off")

    # ---- Stage 2: pool neuron -------------------------------------------
    cx, cy, R = 56.0, 80.0, 11.0
    ax.add_patch(Circle((cx, cy), R, facecolor="white", edgecolor=INK,
                        lw=2.2, zorder=4))
    ax.text(cx, cy, "$R_{TD}$", ha="center", va="center", fontsize=19,
            color=INK, zorder=5)

    # ---- Stage 1: channel neurons ---------------------------------------
    yN = 47.0
    rin = 6.5
    R1 = (28.0, yN)   # CW  = first-on rotation (adapted)
    T  = (56.0, yN)   # translation
    R2 = (84.0, yN)   # CCW = delayed rotation (fresh)
    rI = 3.6
    I1 = (15.0, yN)
    IT = (43.0, yN)
    I2 = (71.0, yN)

    def neuron(c, lab, col):
        ax.add_patch(Circle(c, rin, facecolor="white", edgecolor=INK,
                            lw=2.0, zorder=4))
        ax.text(c[0], c[1], lab, ha="center", va="center", fontsize=14,
                color=INK, zorder=5)
        # small colour cue ring at the base of the soma
        ax.add_patch(Ellipse((c[0], c[1] - rin), 5.0, 2.2, facecolor=col,
                     edgecolor=col, zorder=3, alpha=0.9))

    neuron(R1, "$R_1$", UNCUED)
    neuron(T,  "$R_T$", ACCENT)
    neuron(R2, "$R_2$", CUED)

    # adaptation interneurons + reciprocal motifs
    for Rc, Ic in ((R1, I1), (T, IT), (R2, I2)):
        _adapt_motif(ax, Rc, Ic, rin, rI)

    # ---- Stage-1 stimulus drive arrows (from below) ---------------------
    for c, lab in ((R1, "first-on\nfield"), (T, "translation"),
                   (R2, "delayed\nfield")):
        ax.add_patch(FancyArrowPatch((c[0], 33.5), (c[0], c[1] - rin - 0.5),
                     arrowstyle="-|>", mutation_scale=12, color=INK,
                     lw=1.7, zorder=2))
        ax.text(c[0], 30.5, lab, ha="center", va="top", fontsize=9.5,
                color=INK2)
    ax.text(R1[0] - rin - 2.0, 35.0, "$S$", ha="right", va="center",
            fontsize=12, color=INK)

    # ---- Stage1 -> pool projections -------------------------------------
    # translation: excitatory (+) at soma bottom
    pT = _blob(ax, (cx, cy), 270, ACCENT, R)
    _project(ax, T, pT, ACCENT, 0.0, rin)
    ax.text(cx + 4.0, cy - R - 0.3, "$W^{+}$", fontsize=13, color=ACCENT,
            ha="left", va="center")
    # rotations: inhibitory (-) on the sides
    pR1 = _blob(ax, (cx, cy), 214, INHIB, R)
    _project(ax, R1, pR1, INHIB, 0.10, rin)
    ax.text(pR1[0] - 4.6, pR1[1] + 0.4, "$W^{-}$", fontsize=13, color=INHIB,
            ha="right", va="center")
    pR2 = _blob(ax, (cx, cy), 326, INHIB, R)
    _project(ax, R2, pR2, INHIB, -0.10, rin)
    ax.text(pR2[0] + 4.6, pR2[1] + 0.4, "$W^{-}$", fontsize=13, color=INHIB,
            ha="left", va="center")

    # ---- stage labels (open left gutter, clear of the somata) -----------
    ax.text(6, 90, "Stage 2", ha="left", va="center", fontsize=10,
            color=INK2, style="italic")
    ax.text(6, 58, "Stage 1", ha="left", va="center", fontsize=10,
            color=INK2, style="italic")

    # ---- equations, two grouped + numbered columns ----------------------
    ax.text(20, 23.0, "Stage 1 — adapting channel  ($i = 1, 2, T$)",
            fontsize=10.5, color=INK2, ha="center", va="center")
    s1 = [r"$\tau\,\dot{R}_i = -R_i + N(S_i - w_a I_i)$",
          r"$\tau_a\,\dot{I}_i = -I_i + R_i$",
          r"$N(x) = N_{max}\,[x]_+^{2}/(\sigma_N^{2}+[x]_+^{2})$"]
    for eq, y in zip(s1, (17.5, 12.0, 6.0)):
        ax.text(2, y, eq, fontsize=12, color=INK, ha="left", va="center")

    ax.text(78, 23.0, "Stage 2 — translation detector",
            fontsize=10.5, color=INK2, ha="center", va="center")
    s2 = [(r"$E = W^{+} R_T$", "1"),
          (r"$I = W^{-}(R_1 + R_2)$", "2"),
          (r"$R_{TD} = \dfrac{K\,E}{E + I + \sigma}$", "3")]
    for (eq, n), y in zip(s2, (17.5, 12.0, 5.5)):
        ax.text(58, y, eq, fontsize=12, color=INK, ha="left", va="center")
        ax.text(99, y, f"({n})", fontsize=11, color=INK2, ha="right",
                va="center")

    fig.savefig("web_model_circuit_adapting.png", bbox_inches="tight",
                pad_inches=0.2)
    plt.close(fig)
    print("wrote web_model_circuit_adapting.png")


# ======================================================================
# FIGURE 2 — Stage-1 adapting responses (the inputs to the detector)
# ======================================================================

def adapting_responses(condition, motion_swap=False, dt=1.0):
    """Return (t, R_cw, R_ccw, R_trans) — the Stage-1 adapting responses."""
    t = np.arange(0.0, T_END + dt, dt)
    s_cw, s_ccw, s_tr = channels_for_trial(condition, motion_swap)
    R_cw, _ = simulate_adapting_channel(s_cw, t)
    R_ccw, _ = simulate_adapting_channel(s_ccw, t)
    R_tr, _ = simulate_adapting_channel(s_tr, t)
    return t, R_cw, R_ccw, R_tr


def _survivor_level(t, R_survivor):
    """Mean of the surviving rotation channel across the translation window
    (this is the inhibition the detector sees)."""
    m = (t >= T_TRANS_START) & (t < T_TRANS_END)
    return float(R_survivor[m].mean())


def fig_adapting_inputs():
    fig, axes = plt.subplots(1, 2, figsize=(12.4, 5.2), sharey=True)

    panels = [
        ("A.  CUED — delayed field translates",   "cued"),
        ("B.  UNCUED — first-on field translates", "uncued"),
    ]
    for ax, (title, cond) in zip(axes, panels):
        t, R_cw, R_ccw, R_tr = adapting_responses(cond)
        _style_axes(ax)
        ax.axvspan(T_TRANS_START, T_TRANS_END, **WIN)
        ax.axvline(T_FIELD2_ON, color=INK2, lw=0.9, ls=(0, (4, 3)), alpha=0.7)

        ax.plot(t, R_cw,  color=UNCUED, lw=2.3,
                label="first-on rotation  ($R_1$, CW)")
        ax.plot(t, R_ccw, color=CUED, lw=2.3,
                label="delayed rotation  ($R_2$, CCW)")
        ax.plot(t, R_tr,  color=ACCENT, lw=2.0, ls="--",
                label="translation  ($R_T$)")

        # mark the surviving rotation = the inhibition I in the window
        survivor = R_cw if cond == "cued" else R_ccw   # the one that does NOT gap
        scol = UNCUED if cond == "cued" else CUED
        lev = _survivor_level(t, survivor)
        # offset the callout up for the low (cued) survivor, down for the
        # high (uncued) survivor so it never crowds the legend.
        dy = 22 if cond == "cued" else -24
        va = "bottom" if cond == "cued" else "top"
        ax.annotate(f"surviving rotation\n= inhibition  $I\\approx{lev:.0f}$",
                    xy=(T_TRANS_END, lev),
                    xytext=(T_TRANS_END + 120, lev + dy),
                    fontsize=9.5, color=scol, va=va,
                    arrowprops=dict(arrowstyle="->", color=scol, lw=1.2))

        ax.set_title(title, loc="left", fontsize=12.5, fontweight="bold")
        ax.set_xlabel("time  (ms)")
        ax.set_xlim(0, T_END)
        ax.set_ylim(0, 125)
    axes[0].set_ylabel("adapting response  $R$  (Hz)")
    axes[0].text(T_FIELD2_ON + 12, 119, "delayed onset", fontsize=9,
                 color=INK2, va="top")
    axes[1].legend(fontsize=9.5, loc="upper right", frameon=True,
                   framealpha=0.95)

    fig.tight_layout()
    fig.savefig("web_model_adapting_inputs.png", bbox_inches="tight",
                pad_inches=0.2)
    plt.close(fig)
    print("wrote web_model_adapting_inputs.png")


if __name__ == "__main__":
    fig_circuit_adapting()
    fig_adapting_inputs()
    print("done.")
