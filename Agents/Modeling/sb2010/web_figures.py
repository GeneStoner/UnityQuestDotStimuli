"""
Web-styled figures for the open-perception.org Modeling section.

Three publication-clean figures telling the Stoner & Blanc (2010)
motion-competition story, in the site's palette:

  1. web_model_architecture.png  — neurons & connectivity + equations
  2. web_model_mechanism.png     — adaptation asymmetry -> cued advantage
  3. web_model_swap.png          — the swap reversal the data refute

Run from this directory:
    /usr/bin/python3 web_figures.py

PNGs land alongside the source and are copied into the website's
public/figures/modeling/ by the deploy step.
"""

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Circle, Ellipse
from matplotlib.lines import Line2D

from parameters import (
    T_FIELD2_ON, T_TRANS_START, T_TRANS_END, T_END,
    W_ROT, W_TRANS,
)
from model import simulate_adapting_channel, translation_detector
from stimulus import channels_for_trial, channels_have_gap

# ----------------------------------------------------------------------
# Shared site palette + matplotlib style
# ----------------------------------------------------------------------

INK       = "#1e1e2a"   # text-primary
INK2      = "#4a4a62"   # text-secondary
SURFACE   = "#ffffff"   # surface
PAPER     = "#fdfcfa"   # surface-raised
BORDER    = "#ddd9d2"   # border
ACCENT    = "#3a6fd8"   # accent (blue)  -> translation / excitation
ACCENT_D  = "#dce6f7"   # accent-dim

CUED      = "#2e8b6f"   # green  -> cued / delayed (fresh) field
UNCUED    = "#c0504d"   # red    -> uncued / first-on (adapted) field
INHIB     = "#c0504d"   # red    -> normalization / inhibition
GRID      = "#ece9e3"

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Helvetica Neue", "Helvetica", "Arial", "DejaVu Sans"],
    "font.size": 13,
    "text.color": INK,
    "axes.edgecolor": BORDER,
    "axes.labelcolor": INK,
    "axes.titlecolor": INK,
    "xtick.color": INK2,
    "ytick.color": INK2,
    "axes.linewidth": 1.1,
    "figure.facecolor": SURFACE,
    "savefig.facecolor": SURFACE,
    "savefig.dpi": 200,
})

WIN = dict(color="#000000", alpha=0.05, lw=0)   # translation-window shading


def _style_axes(ax):
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.tick_params(length=4, width=1.0)
    ax.set_facecolor(SURFACE)
    ax.grid(True, color=GRID, lw=0.9, zorder=0)
    ax.set_axisbelow(True)


# ======================================================================
# FIGURE 1 — Architecture (neurons & connectivity)
# ======================================================================

def fig_architecture():
    fig, ax = plt.subplots(figsize=(11, 7.4))
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 70)
    ax.axis("off")

    def box(x, y, w, h, fc=PAPER, ec=BORDER, lw=1.6, r=0.025):
        p = FancyBboxPatch(
            (x, y), w, h,
            boxstyle=f"round,pad=0.4,rounding_size={r*100}",
            facecolor=fc, edgecolor=ec, linewidth=lw, zorder=3,
        )
        ax.add_patch(p)
        return (x + w / 2, y + h / 2)

    def node(x, y, label, sub, color, r=3.6):
        c = Circle((x, y), r, facecolor="white", edgecolor=color,
                   linewidth=2.2, zorder=4)
        ax.add_patch(c)
        ax.text(x, y, label, ha="center", va="center", fontsize=13,
                fontweight="bold", color=color, zorder=5)
        if sub:
            ax.text(x, y - r - 2.8, sub, ha="center", va="center",
                    fontsize=10, color=INK2, zorder=5)
        return (x, y)

    def arrow(p0, p1, color, rad=0.0, lw=2.4, shrinkA=4, shrinkB=2):
        a = FancyArrowPatch(
            p0, p1, connectionstyle=f"arc3,rad={rad}",
            arrowstyle="-|>", mutation_scale=16,
            color=color, lw=lw, zorder=2,
            shrinkA=shrinkA, shrinkB=shrinkB,
        )
        ax.add_patch(a)
        return a

    def inhib_bar(p0, p1, color, lw=2.0, bar=1.6, shrinkA=2, shrinkB=0):
        """Connector ending in a perpendicular T-bar = subtractive inhibition."""
        ax.add_patch(FancyArrowPatch(
            p0, p1, connectionstyle="arc3,rad=0.0", arrowstyle="-",
            color=color, lw=lw, zorder=2, shrinkA=shrinkA, shrinkB=shrinkB))
        dx, dy = p1[0] - p0[0], p1[1] - p0[1]
        L = (dx * dx + dy * dy) ** 0.5
        px, py = -dy / L, dx / L
        ax.plot([p1[0] - px * bar, p1[0] + px * bar],
                [p1[1] - py * bar, p1[1] + py * bar],
                color=color, lw=lw + 0.3, zorder=4, solid_capstyle="round")

    # --- Input nodes (left column) ---
    s1 = node(9, 50, "S₁", "first-on field\n(CW rotation)", UNCUED)
    s2 = node(9, 35, "S₂", "delayed field\n(CCW rotation)", CUED)

    # --- Stage 1: two adapting channels (middle) ---
    u1 = box(30, 46, 27, 8)
    ax.text(u1[0], u1[1] + 1.7, "Adapting channel 1", ha="center",
            va="center", fontsize=12, fontweight="bold", color=INK)
    ax.text(u1[0], u1[1] - 1.9, "rate  R₁", ha="center", va="center",
            fontsize=10.5, color=INK2)

    u2 = box(30, 31, 27, 8)
    ax.text(u2[0], u2[1] + 1.7, "Adapting channel 2", ha="center",
            va="center", fontsize=12, fontweight="bold", color=INK)
    ax.text(u2[0], u2[1] - 1.9, "rate  R₂", ha="center", va="center",
            fontsize=10.5, color=INK2)

    # --- adaptation feedback: R -> I (slow), I --| R (subtractive) ---
    for u, lab in [(u1, "I₁"), (u2, "I₂")]:
        cx = u[0]
        ty = u[1] + 4.0           # box top
        iy = ty + 5.6             # adaptation-variable node height
        node(cx, iy, lab, None, INK2, r=1.9)
        # R -> I  (excitatory drive of the slow variable)
        arrow((cx + 2.6, ty), (cx + 1.1, iy - 1.8), INK2, lw=1.7,
              shrinkA=1, shrinkB=1)
        ax.text(cx + 4.2, (ty + iy) / 2, r"$\tau_a$", fontsize=9,
                color=INK2, ha="left", va="center")
        # I --| R  (subtractive self-inhibition, T-bar)
        inhib_bar((cx - 1.1, iy - 1.8), (cx - 2.6, ty), INK2, lw=1.7,
                  bar=1.3, shrinkA=1, shrinkB=0)
        ax.text(cx - 4.4, (ty + iy) / 2, r"$-w_a$", fontsize=9,
                color=INK2, ha="right", va="center")

    # --- Stage 2: translation detector (right) ---
    td = box(70, 43, 24, 11, fc="white", ec=ACCENT, lw=2.0)
    ax.text(td[0], td[1] + 3.2, "Translation detector", ha="center",
            va="center", fontsize=12.5, fontweight="bold", color=INK)
    ax.text(td[0], td[1] - 1.6, r"$R_{TD}=\dfrac{K\,E}{E+I+\sigma}$",
            ha="center", va="center", fontsize=13, color=ACCENT)
    ax.text(td[0], td[1] - 9.0, "Stage 2 — divisive normalization",
            ha="center", va="center", fontsize=9.5, color=INK2,
            style="italic")

    # output
    arrow((td[0] + 12, td[1]), (99, td[1]), ACCENT, lw=2.6,
          shrinkA=2, shrinkB=0)
    ax.text(99.6, td[1], "$R_{TD}(t)$", ha="left", va="center",
            fontsize=12, color=ACCENT)

    # --- Translation input (feeds detector from below) ---
    ct = node(82, 17, "C", "translation\n(coherent shift)", ACCENT)
    arrow((ct[0], ct[1] + 3.6), (td[0], 43), ACCENT, lw=2.6,
          shrinkA=1, shrinkB=2)
    ax.text(td[0] + 1.8, 31, "E  (excitation)", ha="left", va="center",
            fontsize=9.5, color=ACCENT)

    # --- Connections: inputs -> channels (excitatory, gray) ---
    arrow(s1, (30, u1[1]), INK2, lw=2.0, shrinkA=4, shrinkB=1)
    arrow(s2, (30, u2[1]), INK2, lw=2.0, shrinkA=4, shrinkB=1)

    # --- channels -> detector (divisive normalization, filled-circle ends) ---
    for u, ey in [(u1, td[1] + 3.0), (u2, td[1] - 1.5)]:
        end = (70, ey)
        ax.add_patch(FancyArrowPatch(
            (57, u[1]), end, connectionstyle="arc3,rad=0.0",
            arrowstyle="-", color=INHIB, lw=2.2, zorder=2,
            shrinkA=1, shrinkB=2))
        ax.add_patch(Circle(end, 0.95, facecolor=INHIB, edgecolor=INHIB,
                            zorder=4))
    ax.text(66.5, td[1] + 5.2, "÷  (R₁+R₂)", ha="center", va="center",
            fontsize=9.5, color=INHIB)

    # --- Stage 1 equation block (directly under the channels) ---
    ax.add_patch(FancyBboxPatch(
        (22, 9), 42, 18, boxstyle="round,pad=0.4,rounding_size=1.5",
        facecolor=PAPER, edgecolor=BORDER, linewidth=1.3, zorder=1))
    ax.text(43, 24.6, "Stage 1 — adapting rotation channel   (i = 1, 2)",
            ha="center", va="center", fontsize=10, color=INK2,
            style="italic")
    ax.text(43, 20.4,
            r"$\tau\,\dfrac{dR_i}{dt} = -R_i + N\!\left(S_i - w_a\,I_i\right)$",
            ha="center", va="center", fontsize=13, color=INK)
    ax.text(43, 15.4,
            r"$\tau_a\,\dfrac{dI_i}{dt} = -I_i + R_i$",
            ha="center", va="center", fontsize=13, color=INK)
    ax.text(43, 11.2,
            r"$N(x)=N_{\max}\,[x]_+^{\,2}\,/\,(\sigma_{NR}^{2}+[x]_+^{\,2})$",
            ha="center", va="center", fontsize=10.5, color=INK2)

    # --- Legend strip (terminal conventions) ---
    leg = [
        Line2D([0], [0], color=ACCENT, lw=2.6, marker=">", markersize=8,
               markerfacecolor=ACCENT, markeredgecolor=ACCENT,
               label="excitation"),
        Line2D([0], [0], color=INK2, lw=2.0, marker="|", markersize=13,
               markeredgewidth=2.2,
               label="adaptation  (subtractive self-inhibition,  −)"),
        Line2D([0], [0], color=INHIB, lw=2.4, marker="o", markersize=8,
               markerfacecolor=INHIB,
               label="divisive normalization  (÷)"),
    ]
    ax.legend(handles=leg, loc="lower center", ncol=3, frameon=False,
              fontsize=10.5, bbox_to_anchor=(0.5, -0.01),
              handletextpad=0.6, columnspacing=2.2)

    ax.text(0, 69, "Stoner & Blanc (2010) motion-competition model",
            ha="left", va="top", fontsize=16, fontweight="bold", color=INK)
    ax.text(0, 65.3,
            "Two adapting direction channels divisively normalize a "
            "translation detector — no attention term.",
            ha="left", va="top", fontsize=11.5, color=INK2)

    fig.tight_layout()
    fig.savefig("web_model_architecture.png", bbox_inches="tight",
                pad_inches=0.25)
    plt.close(fig)
    print("wrote web_model_architecture.png")


# ======================================================================
# Shared simulation for figs 2 & 3
# ======================================================================

def _simulate(condition, motion_swap):
    """All three motion inputs (two rotations + translation) pass through the
    Eq. 4-5 adapting channel; the detector (Eq. 3) pools the adapting
    responses.  Per S&B App. A: 'These adapting responses constitute the
    inputs (the Cs in Eqs 1 and 2) to a translation detector (Eq 3).'"""
    t = np.linspace(0, T_END, 1591)
    cw, ccw, ctr = channels_for_trial(condition, motion_swap)
    R1, _ = simulate_adapting_channel(cw, t)
    R2, _ = simulate_adapting_channel(ccw, t)
    Rt, _ = simulate_adapting_channel(ctr, t)   # translation, adapted
    Rtd = translation_detector(Rt, R1, R2)       # E = W_TRANS * Rt
    return t, R1, R2, Rt, Rtd


def _peak_window(t, Rtd):
    # With the adapted translation drive the detector transient peaks near
    # translation offset and decays after; measure the peak of the full
    # transient, not just the stimulus window.
    m = (t >= T_TRANS_START) & (t <= T_TRANS_END + 120)
    return Rtd[m].max()


# ======================================================================
# FIGURE 2 — Mechanism (why cued > uncued)
# ======================================================================

def fig_mechanism():
    t, R1c, R2c, _Rtc, Rtd_c = _simulate("cued", False)
    _, R1u, R2u, _Rtu, Rtd_u = _simulate("uncued", False)

    peak_c = _peak_window(t, Rtd_c)
    peak_u = _peak_window(t, Rtd_u)
    bias = (peak_c / peak_u - 1) * 100

    fig, (axL, axR) = plt.subplots(1, 2, figsize=(11, 4.6),
                                   gridspec_kw=dict(width_ratios=[1.35, 1]))

    # --- Left: adaptation asymmetry (cued trial channels) ---
    _style_axes(axL)
    axL.axvspan(T_TRANS_START, T_TRANS_END, **WIN)
    axL.plot(t, R1c, color=UNCUED, lw=2.6,
             label="first-on field  (adapted)")
    axL.plot(t, R2c, color=CUED, lw=2.6,
             label="delayed field  (fresh)")
    axL.axvline(T_FIELD2_ON, color=INK2, lw=1.0, ls=":", alpha=0.7)
    axL.text(T_FIELD2_ON + 12, 6, "delayed\nfield on", fontsize=9,
             color=INK2, ha="left", va="bottom")
    axL.set_xlim(0, T_END)
    axL.set_ylim(0, 100)
    axL.set_xlabel("time  (ms)")
    axL.set_ylabel("rotation channel firing  R  (Hz)")
    axL.set_title("Adaptation makes the two competitors unequal",
                  fontsize=12.5, fontweight="bold", pad=8)
    axL.legend(loc="lower right", frameon=False, fontsize=10.5)
    axL.annotate("", xy=(T_TRANS_START, 85), xytext=(T_TRANS_START, 35),
                 arrowprops=dict(arrowstyle="<->", color=INK2, lw=1.3))
    axL.text(T_TRANS_START - 20, 60, "gap in\nstrength", fontsize=9,
             color=INK2, ha="right", va="center")

    # --- Right: translation-detector response, cued vs uncued ---
    _style_axes(axR)
    m = (t >= T_TRANS_START - 6) & (t <= T_TRANS_END + 6)
    axR.axvspan(T_TRANS_START, T_TRANS_END, **WIN)
    axR.plot(t[m], Rtd_c[m], color=CUED, lw=2.8, label="cued")
    axR.plot(t[m], Rtd_u[m], color=UNCUED, lw=2.8, label="uncued")
    axR.scatter([t[m][np.argmax(Rtd_c[m])]], [peak_c], color=CUED, s=40,
                zorder=5)
    axR.scatter([t[m][np.argmax(Rtd_u[m])]], [peak_u], color=UNCUED, s=40,
                zorder=5)
    axR.set_xlim(T_TRANS_START - 6, T_TRANS_END + 6)
    axR.set_ylim(0, max(peak_c, peak_u) * 1.18)
    axR.set_xlabel("time  (ms)")
    axR.set_ylabel("translation detector  $R_{TD}$")
    axR.set_title(f"Cued advantage  =  +{bias:.0f}%",
                  fontsize=12.5, fontweight="bold", pad=8)
    axR.legend(loc="upper left", frameon=False, fontsize=10.5)

    fig.suptitle(
        "Why the cued field wins:  it is the stronger competitor, so "
        "removing it during translation disinhibits the detector more",
        fontsize=12.5, color=INK2, y=1.02)
    fig.tight_layout()
    fig.savefig("web_model_mechanism.png", bbox_inches="tight",
                pad_inches=0.2)
    plt.close(fig)
    print(f"wrote web_model_mechanism.png   (cued bias +{bias:.1f}%)")
    return peak_c, peak_u


# ======================================================================
# FIGURE 3 — The swap reversal (falsification)
# ======================================================================

def fig_swap():
    _, _, _, _, Rtd_cn = _simulate("cued", False)
    t, _, _, _, Rtd_un = _simulate("uncued", False)
    _, _, _, _, Rtd_cs = _simulate("cued", True)
    _, _, _, _, Rtd_us = _simulate("uncued", True)

    pcn, pun = _peak_window(t, Rtd_cn), _peak_window(t, Rtd_un)
    pcs, pus = _peak_window(t, Rtd_cs), _peak_window(t, Rtd_us)
    bias_no = (pcn / pun - 1) * 100
    bias_sw = (pcs / pus - 1) * 100

    fig, (axL, axR) = plt.subplots(1, 2, figsize=(11, 4.6),
                                   gridspec_kw=dict(width_ratios=[1.1, 1]))

    # --- Left: grouped peak bars ---
    _style_axes(axL)
    x = np.array([0, 1])
    w = 0.36
    axL.bar(x - w / 2, [pcn, pcs], w, color=CUED, label="cued",
            edgecolor="white", lw=1.2, zorder=3)
    axL.bar(x + w / 2, [pun, pus], w, color=UNCUED, label="uncued",
            edgecolor="white", lw=1.2, zorder=3)
    for xi, (a, b) in zip(x, [(pcn, pun), (pcs, pus)]):
        axL.text(xi - w / 2, a + 0.6, f"{a:.0f}", ha="center", fontsize=10,
                 color=INK)
        axL.text(xi + w / 2, b + 0.6, f"{b:.0f}", ha="center", fontsize=10,
                 color=INK)
    axL.set_xticks(x)
    axL.set_xticklabels(["no swap", "motion swap"])
    axL.set_ylabel("peak  $R_{TD}$")
    axL.set_ylim(0, max(pcn, pcs, pun, pus) * 1.2)
    axL.set_title("Model: peak response by condition", fontsize=12.5,
                  fontweight="bold", pad=8)
    axL.legend(loc="upper center", frameon=False, fontsize=10.5,
               ncol=2, bbox_to_anchor=(0.5, 1.0))

    # --- Right: bias bars (the reversal) ---
    _style_axes(axR)
    cols = [CUED if bias_no > 0 else UNCUED, CUED if bias_sw > 0 else UNCUED]
    axR.axhline(0, color=INK2, lw=1.2)
    bars = axR.bar([0, 1], [bias_no, bias_sw], 0.5,
                   color=cols, edgecolor="white", lw=1.2, zorder=3)
    axR.text(0, bias_no + 3, f"+{bias_no:.0f}%", ha="center", fontsize=12,
             fontweight="bold", color=INK)
    axR.text(1, bias_sw - 3, f"{bias_sw:.0f}%", ha="center", va="top",
             fontsize=12, fontweight="bold", color=INK)
    axR.set_xticks([0, 1])
    axR.set_xticklabels(["no swap", "motion swap"])
    axR.set_ylabel("cued − uncued bias  (%)")
    axR.set_ylim(min(bias_sw, -10) * 1.35, max(bias_no, 10) * 1.35)
    axR.set_title("The model flips the bias under swap", fontsize=12.5,
                  fontweight="bold", pad=8)
    axR.text(0.5, axR.get_ylim()[1] * 0.96,
             "behavioral data do NOT reverse — this falsifies the model",
             ha="center", va="top", fontsize=10, color=UNCUED,
             style="italic")

    fig.suptitle(
        "A motion swap makes (cued, swap) inputs identical to (uncued, "
        "no-swap) — so the model must predict a full reversal",
        fontsize=12.5, color=INK2, y=1.02)
    fig.tight_layout()
    fig.savefig("web_model_swap.png", bbox_inches="tight", pad_inches=0.2)
    plt.close(fig)
    print(f"wrote web_model_swap.png   (no-swap +{bias_no:.1f}%, "
          f"swap {bias_sw:.1f}%)")


# ======================================================================
# FIGURE 4 — Fig. 3 replication (model responses, cued vs uncued)
# ======================================================================

def fig_responses():
    """Model responses across all four trial types (cued/uncued x
    no-swap/motion-swap).  Rows: rotation channel responses (dashed = the
    channel interrupted by translation), normalization I + drive E,
    translation detector R_TD.  Shows the cued advantage under no swap and
    its reversal under motion swap."""
    TEST, OTHER = CUED, UNCUED
    trials = [("CUED", "no swap", "cued", False),
              ("UNCUED", "no swap", "uncued", False),
              ("CUED", "motion swap", "cued", True),
              ("UNCUED", "motion swap", "uncued", True)]
    data = []
    for cue, sw_lab, cond, sw in trials:
        t, R1, R2, Rt, Rtd = _simulate(cond, sw)
        cw_gap, ccw_gap = channels_have_gap(cond, sw)
        test = R1 if cw_gap else R2          # channel interrupted by translation
        other = R2 if cw_gap else R1
        data.append(dict(cue=cue, sw=sw_lab, t=t, test=test, other=other,
                         I=W_ROT * (R1 + R2), E=W_TRANS * Rt, Rtd=Rtd,
                         peak=_peak_window(t, Rtd)))
    imax = max(d["I"].max() for d in data) * 1.12
    pmax = max(d["peak"] for d in data) * 1.25

    fig, axes = plt.subplots(3, 4, figsize=(13.5, 8.0), sharex=True)
    rlab = ["R  (Hz)", "drive  I, E", "$R_{TD}$"]
    for j, d in enumerate(data):
        t = d["t"]
        for i in range(3):
            ax = axes[i, j]
            _style_axes(ax)
            ax.axvspan(T_TRANS_START, T_TRANS_END, **WIN)
            ax.set_xlim(0, T_END)
            if j == 0:
                ax.set_ylabel(rlab[i])
        # row 0 — channel responses
        ax = axes[0, j]
        ax.plot(t, d["other"], color=OTHER, lw=2.2, zorder=3)
        ax.plot(t, d["test"], color=TEST, lw=2.2, ls=(0, (1, 1.5)), zorder=4)
        ax.set_ylim(0, 100)
        ax.set_title(f"{d['cue']}\n{d['sw']}", fontsize=11,
                     fontweight="bold", pad=8)
        # row 1 — detector inputs
        ax = axes[1, j]
        ax.plot(t, d["I"], color=INK, lw=2.2)
        ax.plot(t, d["E"], color=ACCENT, lw=2.0, ls="--")
        ax.set_ylim(0, imax)
        # row 2 — R_TD
        ax = axes[2, j]
        ax.fill_between(t, 0, d["Rtd"], color=ACCENT, alpha=0.18, lw=0)
        ax.plot(t, d["Rtd"], color=ACCENT, lw=2.2)
        ax.set_ylim(0, pmax)
        ax.text(T_TRANS_END + 40, d["peak"], f"{d['peak']:.0f}",
                fontsize=9.5, color=INK, va="center")
        ax.set_xlabel("time  (ms)")

    leg = [
        Line2D([0], [0], color=TEST, lw=2.2, ls=(0, (1, 1.5)),
               label="channel interrupted by translation"),
        Line2D([0], [0], color=OTHER, lw=2.2, label="other rotation channel"),
    ]
    axes[0, 0].legend(handles=leg, loc="lower right", frameon=False,
                      fontsize=7.5)
    axes[1, 0].legend(handles=[
        Line2D([0], [0], color=INK, lw=2.2, label="$I=R_1{+}R_2$"),
        Line2D([0], [0], color=ACCENT, lw=2.0, ls="--", label="$E$")],
        loc="upper left", frameon=False, fontsize=8, bbox_to_anchor=(0, 1.04))

    bias_ns = (data[0]["peak"] / data[1]["peak"] - 1) * 100
    bias_sw = (data[2]["peak"] / data[3]["peak"] - 1) * 100
    fig.tight_layout()
    fig.savefig("web_model_responses.png", bbox_inches="tight",
                pad_inches=0.2)
    plt.close(fig)
    print(f"wrote web_model_responses.png   (NS +{bias_ns:.1f}%, "
          f"SW {bias_sw:.1f}%)")


# ======================================================================
# FIGURE 5 — Feature trajectories (replication of S&B Fig. 1B)
# ======================================================================

def fig_trajectories():
    """Web-styled replication of S&B (2010) Fig. 1B feature-based depiction.

    Three feature tracks (CW / TRANS / CCW).  Each dot field is a line that
    sits on its rotation track and notches into TRANS during the 40 ms
    translation window.  Green dashed = delayed field, red solid = first-on
    field (S&B convention).  Built parallel to web_model_responses.png:
    same two columns (CUED / UNCUED), same time axis, same colors — so the
    stimulus trajectory stacks directly above the model response.
    """
    # S&B Fig 1B convention: line STYLE = dot-field identity, line COLOR = dot
    # color, vertical position = motion type.  The SAME field translates in
    # both conditions -> the dashed (test) field notches into TRANS in both;
    # onset role (delayed vs first-on) is shown by where each line starts.
    TEST, OTHER = CUED, UNCUED           # green dashed = test field, red solid = other
    CW, TRANS, CCW = 2, 1, 0
    ts, te = T_TRANS_START, T_TRANS_END
    T0 = T_FIELD2_ON                     # delayed onset

    # test field (dashed, on CW) — notches into TRANS; SAME field in both panels
    def test_line(start):
        return ([start, ts, ts, te, te, T_END],
                [CW, CW, TRANS, TRANS, CW, CW])

    fig, axes = plt.subplots(1, 2, figsize=(11, 3.6))
    for ax in axes:
        _style_axes(ax)
        ax.grid(False)
        for y in (CW, TRANS, CCW):       # faint track guides
            ax.axhline(y, color=GRID, lw=1.0, zorder=0)
        ax.axvspan(ts, te, **WIN)
        ax.set_xlim(0, T_END)
        ax.set_ylim(-0.6, 2.6)
        ax.set_yticks([CCW, TRANS, CW])
        ax.set_yticklabels(["CCW", "TRANS", "CW"])
        ax.set_xlabel("time  (ms)")

    # CUED — test field (dashed) is the DELAYED one (starts at T0);
    # the other field (solid) is first-on (full width from 0)
    ax = axes[0]
    ax.plot([0, T_END], [CCW, CCW], color=OTHER, lw=2.8)
    tx, ty = test_line(T0)
    ax.plot(tx, ty, color=TEST, lw=2.8, ls=(0, (1, 1.5)))
    ax.set_title("CUED", fontsize=13, fontweight="bold", pad=8)

    # UNCUED — test field (dashed) is the FIRST-ON one (full width from 0);
    # the other field (solid) is delayed (starts at T0)
    ax = axes[1]
    ax.plot([T0, T_END], [CCW, CCW], color=OTHER, lw=2.8)
    tx, ty = test_line(0)
    ax.plot(tx, ty, color=TEST, lw=2.8, ls=(0, (1, 1.5)))
    ax.set_title("UNCUED", fontsize=13, fontweight="bold", pad=8)

    fig.suptitle("Feature trajectories  —  replication of Stoner & Blanc "
                 "(2010), Fig. 1B", fontsize=14, fontweight="bold",
                 color=INK, y=1.02)
    fig.tight_layout()
    fig.savefig("web_model_trajectories.png", bbox_inches="tight",
                pad_inches=0.2)
    plt.close(fig)
    print("wrote web_model_trajectories.png")


# ======================================================================
# FIGURE 6 — Directional inputs (the trajectories as per-channel drive)
# ======================================================================

def _no_risers(t, y):
    """Return x, y with NaN breaks inserted at each level transition, so a
    line plot shows the horizontal level segments only — no vertical risers."""
    x, out = [t[0]], [y[0]]
    for i in range(1, len(t)):
        if y[i] != y[i - 1]:
            x.append(t[i - 1]); out.append(np.nan)
        x.append(t[i]); out.append(y[i])
    return np.array(x), np.array(out)


def _input_drives(t, cue, motion_swap):
    """Per-field drive placed on the track each field occupies over time
    (mirrors the feature trajectory).  Returns {row: (test_drive,
    competitor_drive)}.  Rotation drive = 50, translation = 25."""
    ts, te, T0 = T_TRANS_START, T_TRANS_END, T_FIELD2_ON
    test_onset = T0 if cue == "CUED" else 0
    comp_onset = 0 if cue == "CUED" else T0
    z = lambda: np.zeros_like(t)
    tCW, tTR, tCC = z(), z(), z()        # test field
    cCW, cTR, cCC = z(), z(), z()        # competitor
    tCW[(t >= test_onset) & (t < ts)] = 50
    tTR[(t >= ts) & (t < te)] = 25
    if motion_swap:
        tCC[t >= te] = 50
    else:
        tCW[t >= te] = 50
    if motion_swap:
        cCC[(t >= comp_onset) & (t < ts)] = 50
        cCW[t >= ts] = 50
    else:
        cCC[t >= comp_onset] = 50
    return {"CW": (tCW, cCW), "TRANS": (tTR, cTR), "CCW": (tCC, cCC)}


def fig_inputs():
    """Directional inputs S(t) across all four trial types.  Same convention
    as the trajectory figure: dashed = test field (translates), solid =
    competitor; the test field keeps its identity but changes rotation track
    under motion swap.  Rotation drive = 50, translation = 25 (Mode 1)."""
    TEST, OTHER = CUED, UNCUED
    t = np.linspace(0, T_END, 1591)
    trials = [("CUED", "no swap", False), ("UNCUED", "no swap", False),
              ("CUED", "motion swap", True), ("UNCUED", "motion swap", True)]
    rows = ["CW", "TRANS", "CCW"]

    fig, axes = plt.subplots(3, 4, figsize=(13.5, 5.6), sharex=True)
    for j, (cue, sw_lab, sw) in enumerate(trials):
        dr = _input_drives(t, cue, sw)
        for i, row in enumerate(rows):
            ax = axes[i, j]
            _style_axes(ax)
            ax.axvspan(T_TRANS_START, T_TRANS_END, **WIN)
            tsig, csig = dr[row]
            if csig.max() > 0:
                xx, yy = _no_risers(t, csig)
                ax.plot(xx, yy, color=OTHER, lw=2.2, zorder=3)
            if tsig.max() > 0:
                xx, yy = _no_risers(t, tsig)
                ax.plot(xx, yy, color=TEST, lw=2.2, ls=(0, (1, 1.5)),
                        zorder=4)
            ax.set_xlim(0, T_END)
            ax.set_ylim(-5, 58)
            ax.set_yticks([0, 25, 50])
            if j == 0:
                ax.set_ylabel(row, fontsize=11, fontweight="bold")
            if i == 0:
                ax.set_title(f"{cue}\n{sw_lab}", fontsize=11,
                             fontweight="bold", pad=8)
            if i == 2:
                ax.set_xlabel("time  (ms)")

    leg = [
        Line2D([0], [0], color=TEST, lw=2.2, ls=(0, (1, 1.5)),
               label="test field  (translates)"),
        Line2D([0], [0], color=OTHER, lw=2.2, label="other field"),
    ]
    axes[0, 3].legend(handles=leg, loc="upper right", frameon=False,
                      fontsize=8)
    fig.tight_layout()
    fig.savefig("web_model_inputs.png", bbox_inches="tight", pad_inches=0.2)
    plt.close(fig)
    print("wrote web_model_inputs.png")


# ======================================================================
# FIGURE 7 — Biased-competition circuit (Reynolds et al. 1999 idiom)
# ======================================================================

def fig_biased_competition():
    """Biased-competition circuit in the Reynolds, Chelazzi & Desimone (1999)
    Fig. 2 idiom: response variable inside the output circle, input variables
    inside the input circles, curved projections ending in filled synaptic
    terminals on the soma (excitatory + / inhibitory -) with weight labels,
    and the equations stacked and numbered below.  Symbols only — the caption
    carries the cortical mapping, the citations, and the role of adaptation."""
    fig, ax = plt.subplots(figsize=(7.6, 8.0))
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.set_aspect("equal", adjustable="box")
    ax.axis("off")

    cx, cy, r = 50.0, 70.0, 12.0          # output neuron (large, on top)

    # --- output neuron: response variable inside ---
    ax.add_patch(Circle((cx, cy), r, facecolor="white", edgecolor=INK,
                        lw=2.2, zorder=4))
    ax.text(cx, cy, "$R_{TD}$", ha="center", va="center", fontsize=20,
            color=INK, zorder=5)

    # --- input neurons: input variables inside ---
    yIn = 34.0
    rin = 7.0

    def innode(x, lab):
        ax.add_patch(Circle((x, yIn), rin, facecolor="white", edgecolor=INK,
                            lw=2.0, zorder=4))
        ax.text(x, yIn, lab, ha="center", va="center", fontsize=16,
                color=INK, zorder=5)
        return (x, yIn)

    nC = innode(50, "$T$")
    nR1 = innode(16, "$R_1$")
    nR2 = innode(84, "$R_2$")

    def blob(theta_deg, color):
        """Filled synaptic terminal sitting tangent on the soma."""
        th = np.radians(theta_deg)
        P = (cx + r * np.cos(th), cy + r * np.sin(th))
        ax.add_patch(Ellipse(P, 5.0, 2.4, angle=theta_deg + 90,
                     facecolor=color, edgecolor=color, zorder=6))
        return P

    def project(node, P, color, rad):
        """Curved projection from an input neuron to a terminal on the soma."""
        d = (P[0] - node[0], P[1] - node[1])
        L = (d[0] ** 2 + d[1] ** 2) ** 0.5
        start = (node[0] + d[0] / L * rin, node[1] + d[1] / L * rin)
        ax.add_patch(FancyArrowPatch(
            start, P, arrowstyle="-", connectionstyle=f"arc3,rad={rad}",
            color=color, lw=2.0, zorder=2, shrinkA=0, shrinkB=2))

    # excitatory (C, +) at the soma bottom; inhibitory (R1, R2, -) on the sides
    pC = blob(270, ACCENT)
    project(nC, pC, ACCENT, 0.0)
    ax.text(cx + 4.2, cy - r - 0.5, "$W^{+}$", fontsize=14, color=ACCENT,
            ha="left", va="center")

    pR1 = blob(206, INHIB)
    project(nR1, pR1, INHIB, 0.12)
    ax.text(pR1[0] - 4.8, pR1[1] + 0.3, "$W^{-}$", fontsize=14, color=INHIB,
            ha="right", va="center")

    pR2 = blob(334, INHIB)
    project(nR2, pR2, INHIB, -0.12)
    ax.text(pR2[0] + 4.8, pR2[1] + 0.3, "$W^{-}$", fontsize=14, color=INHIB,
            ha="left", va="center")

    # --- equations stacked and numbered below (Reynolds layout) ---
    eqs = [r"$E = W^{+}T$",
           r"$I = W^{-}(R_1 + R_2)$",
           r"$R_{TD} = \dfrac{K\,E}{E + I + \sigma}$"]
    yq = [17, 10, 2.5]
    for eq, y, n in zip(eqs, yq, "123"):
        ax.text(20, y, eq, fontsize=15, color=INK, ha="left", va="center")
        ax.text(82, y, f"({n})", fontsize=13, color=INK2, ha="right",
                va="center")

    fig.savefig("web_model_circuit.png", bbox_inches="tight", pad_inches=0.2)
    plt.close(fig)
    print("wrote web_model_circuit.png")


# ======================================================================
# Shared feature-trajectory panel drawer (for swap figures)
# ======================================================================

CW_, TRANS_, CCW_ = 2, 1, 0

# Single-RF interpretation (modeling-page toggle pair ONLY): an MT hypercolumn
# whose collective receptive field is positioned on the LEFT of the rotating
# display.  There, CW rotation is locally UPWARD motion and CCW rotation is
# locally DOWNWARD motion; the coherent translation is a rightward shift.  These
# labels are used by traj_figure_sb4.py and dirinputs_figure_sb4.py so that
# toggle pair stays consistent.  NOT used by _traj_panel / fig_motionswap, which
# keep S&B's abstract CW/TRANS/CCW coordinates for the replication figures.
# (Order matches yticks [CCW_, TRANS_, CW_] = bottom -> top.)
ROW_TICKS = [CCW_, TRANS_, CW_]
ROW_LABELS = ["Up", "Right", "Down"]


def _plot_field(ax, verts, tsplit, c_pre, c_post, ls, lw, z=3):
    """Plot a field's feature trajectory.  When the colour does not change
    (no colour swap) the whole line is drawn in one pass so the dash pattern
    stays continuous.  For a colour swap the colour switches at tsplit while
    the line style (= field identity) is kept fixed."""
    if c_pre == c_post:
        ax.plot([x for x, _ in verts], [y for _, y in verts], color=c_pre,
                ls=ls, lw=lw, solid_capstyle="round", zorder=z)
        return
    pre = [(x, y) for x, y in verts if x <= tsplit]
    post = [(x, y) for x, y in verts if x >= tsplit]
    if len(pre) >= 2:
        ax.plot([p[0] for p in pre], [p[1] for p in pre], color=c_pre,
                ls=ls, lw=lw, solid_capstyle="round", zorder=z)
    if len(post) >= 2:
        ax.plot([p[0] for p in post], [p[1] for p in post], color=c_post,
                ls=ls, lw=lw, solid_capstyle="round", zorder=z)


def _traj_panel(ax, cue, motion_swap=False, color_swap=False, field_color=None):
    """One feature-trajectory panel.  Convention: line STYLE = identity
    (dashed = test field that translates, solid = competitor); line COLOR
    = dot color (green test, red competitor; flips at swap if color_swap);
    vertical position = motion type.  The SAME (dashed) field translates.
    Pass field_color to render both fields in a single colour (e.g. CUED)."""
    GREEN, RED = CUED, UNCUED
    if field_color is not None:
        GREEN = RED = field_color
    ts, te, T0 = T_TRANS_START, T_TRANS_END, T_FIELD2_ON
    _style_axes(ax)
    ax.grid(False)
    for y in (CW_, TRANS_, CCW_):
        ax.axhline(y, color=GRID, lw=1.0, zorder=0)
    ax.axvspan(ts, te, **WIN)
    ax.set_xlim(0, T_END)
    ax.set_ylim(-0.6, 2.6)
    ax.set_yticks([CCW_, TRANS_, CW_])
    ax.set_yticklabels(["CCW", "TRANS", "CW"])

    # Cued = the DELAYED dots translate.  The green (dotted) field rotates
    # CW, the red (solid) field rotates CCW — fixed identities.  WITHOUT a
    # swap the green field translates; the motion swap changes WHICH dots
    # translate, so the RED field translates instead, while the non-
    # translating field reverses its rotation direction.  The translator is
    # the delayed field (onset T0) for cued, the first-on field (onset 0)
    # for uncued.
    transl_onset = T0 if cue == "CUED" else 0
    other_onset = 0 if cue == "CUED" else T0

    if not motion_swap:
        g_onset, r_onset = transl_onset, other_onset
        green_v = [(g_onset, CW_), (ts, CW_), (ts, TRANS_),
                   (te, TRANS_), (te, CW_), (T_END, CW_)]       # green translates
        red_v = [(r_onset, CCW_), (ts, CCW_), (T_END, CCW_)]    # red steady
    else:
        r_onset, g_onset = transl_onset, other_onset
        red_v = [(r_onset, CCW_), (ts, CCW_), (ts, TRANS_),
                 (te, TRANS_), (te, CW_), (T_END, CW_)]         # red translates
        green_v = [(g_onset, CW_), (ts, CW_),
                   (ts, CCW_), (T_END, CCW_)]                   # green reverses

    g_post = RED if color_swap else GREEN
    r_post = GREEN if color_swap else RED
    _plot_field(ax, red_v, ts, RED, r_post, "-", 2.6, z=3)
    _plot_field(ax, green_v, ts, GREEN, g_post, (0, (1, 1.5)), 2.6, z=4)


# ======================================================================
# FIGURE 8 — Motion-swap feature trajectories (S&B Fig. 4)
# ======================================================================

def fig_motionswap():
    fig, axes = plt.subplots(2, 2, figsize=(11, 5.4), sharex=True)
    cols = [("no motion swap", False), ("motion swap", True)]
    rows = ["CUED", "UNCUED"]
    for i, cue in enumerate(rows):
        for j, (ctitle, swap) in enumerate(cols):
            ax = axes[i, j]
            _traj_panel(ax, cue, motion_swap=swap, color_swap=False)
            if i == 0:
                ax.set_title(ctitle, fontsize=12, fontweight="bold", pad=10)
            if j == 0:
                ax.set_ylabel(cue, fontsize=11, fontweight="bold")
            if i == 1:
                ax.set_xlabel("time  (ms)")

    fig.tight_layout()
    fig.savefig("web_model_motionswap.png", bbox_inches="tight",
                pad_inches=0.2)
    plt.close(fig)
    print("wrote web_model_motionswap.png")


# ======================================================================
# FIGURE 9 — Color-swap feature trajectories (S&B Fig. 5 idiom)
# ======================================================================

def fig_colorswap():
    fig, axes = plt.subplots(2, 2, figsize=(11, 5.4), sharex=True)
    cols = [("no motion swap", False), ("motion swap", True)]
    rows = [("no colour swap", False), ("colour swap", True)]
    for i, (rtitle, cswap) in enumerate(rows):
        for j, (ctitle, mswap) in enumerate(cols):
            ax = axes[i, j]
            _traj_panel(ax, "CUED", motion_swap=mswap, color_swap=cswap)
            if i == 0:
                ax.set_title(ctitle, fontsize=12, fontweight="bold", pad=10)
            if j == 0:
                ax.set_ylabel(rtitle, fontsize=11, fontweight="bold")
            if i == 1:
                ax.set_xlabel("time  (ms)")

    fig.tight_layout()
    fig.savefig("web_model_colorswap.png", bbox_inches="tight",
                pad_inches=0.2)
    plt.close(fig)
    print("wrote web_model_colorswap.png")


# ======================================================================
# FIGURE 10 — Stimulus input to the normalization model (direction x time)
# ======================================================================

def _dir_content(t, cue, motion_swap=False):
    """Direction content of the stimulus over time.  The motion swap does
    NOT change this — it only changes which dots give rise to it — so
    motion_swap is ignored here.  CW (+90) = first-on rotation (from t=0);
    CCW (-90) = delayed rotation (from 750 ms = delayed onset).  Cued =
    the delayed dots translate, so the CCW rotation gaps during the window;
    uncued = the first-on dots translate, so the CW rotation gaps.
    Rotation drive = 50, translation = 25.  Returns (dCW, dTRANS, dCCW)."""
    ts, te, T0 = T_TRANS_START, T_TRANS_END, T_FIELD2_ON
    z = lambda: np.zeros_like(t)
    dCW, dTR, dCC = z(), z(), z()
    dTR[(t >= ts) & (t < te)] = 25
    if cue == "CUED":                 # delayed (CCW) translates -> CCW gaps
        dCW[t >= 0] = 50
        dCC[(t >= T0) & (t < ts)] = 50
        dCC[t >= te] = 50
    else:                             # first-on (CW) translates -> CW gaps
        dCC[t >= T0] = 50
        dCW[(t >= 0) & (t < ts)] = 50
        dCW[t >= te] = 50
    return dCW, dTR, dCC


def fig_stim_inputs():
    """Stimulus input to the normalization model in the R&H Fig-1 idiom:
    narrow bands on a continuous motion-direction axis (CW +90, TRANS 0,
    CCW -90) over time, for the four trial types.  This is the direction-
    only view the competition/normalization model receives — so the motion
    swap is invisible to it: CUED-swap is identical to UNCUED-no-swap, and
    UNCUED-swap identical to CUED-no-swap."""
    t = np.linspace(0, T_END, 600)
    th = np.linspace(-180, 180, 721)

    def band(center):
        # sharp, narrow band at the exact direction (input is NOT graded in
        # direction — directional grading belongs to the tuned drive E(theta))
        return (np.abs(th[:, None] - center) <= 2.5).astype(float)

    bCW, bTR, bCC = band(90), band(0), band(-90)

    fig, axes = plt.subplots(2, 2, figsize=(11, 6.4), sharex=True,
                             sharey=True)
    cols = [("no swap", False), ("motion swap", True)]
    rows = ["CUED", "UNCUED"]
    for i, cue in enumerate(rows):
        for j, (ctitle, swap) in enumerate(cols):
            ax = axes[i, j]
            dCW, dTR, dCC = _dir_content(t, cue, swap)
            D = bCW * dCW[None, :] + bTR * dTR[None, :] + bCC * dCC[None, :]
            ax.imshow(D, extent=[0, T_END, -180, 180], origin="lower",
                      aspect="auto", cmap="Greys", vmin=0, vmax=55,
                      interpolation="nearest")
            ax.axvline(T_TRANS_START, color=INHIB, lw=1.0, alpha=0.8)
            ax.axvline(T_TRANS_END, color=INHIB, lw=1.0, alpha=0.8)
            ax.set_yticks([-90, 0, 90])
            ax.set_yticklabels(["CCW", "TRANS", "CW"])
            ax.set_xlim(0, T_END)
            ax.tick_params(length=4, width=1.0, colors=INK2)
            for s in ax.spines.values():
                s.set_edgecolor(BORDER)
            if i == 0:
                ax.set_title(ctitle, fontsize=12, fontweight="bold", pad=8)
            if j == 0:
                ax.set_ylabel("motion direction", fontsize=10.5)
            if i == 1:
                ax.set_xlabel("time  (ms)")

    fig.tight_layout()
    fig.savefig("web_model_stiminputs.png", bbox_inches="tight",
                pad_inches=0.2)
    plt.close(fig)
    print("wrote web_model_stiminputs.png")


if __name__ == "__main__":
    fig_architecture()
    fig_trajectories()
    fig_inputs()
    fig_mechanism()
    fig_swap()
    fig_responses()
    fig_biased_competition()
    fig_motionswap()
    fig_colorswap()
    fig_stim_inputs()
    print("done.")
