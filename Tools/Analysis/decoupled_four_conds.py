#!/usr/bin/env python3
"""
Eight conditions for Depth × Color decoupling — 100% swaps.
Full 2×2×2 factorial: DFD (Near/Far) × Depth swap × Color swap.

Page 1 — DFD = Near (Field B delayed, translates):
  Cond 1: Dots✓  Depth✓  Color✓  — no swap
  Cond 2: Dots✓  Depth✓  Color✗  — color swap (S&B Exp 2)
  Cond 3: Dots✓  Depth✗  Color✓  — depth swap
  Cond 4: Dots✓  Depth✗  Color✗  — depth + color swap

Page 2 — DFD = Far (Field A delayed, translates):
  Cond 5: Dots✓  Depth✓  Color✓  — no swap
  Cond 6: Dots✓  Depth✓  Color✗  — color swap
  Cond 7: Dots✓  Depth✗  Color✓  — depth swap
  Cond 8: Dots✓  Depth✗  Color✗  — depth + color swap

Both fields always swap together → single color per plane throughout.
Output: Agents/WriteUps/decoupled_four_conds.pdf
"""

import sys, textwrap
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.lines import Line2D
from matplotlib.patches import Patch

OUT = (sys.argv[1] if len(sys.argv) > 1 else
       "/Users/genestoner1/Projects/ObjectBasedAttention/VRDots/"
       "Agents/WriteUps/decoupled_four_conds.pdf")

# ── Timing ────────────────────────────────────────────────────────────────────
T_TOT = 1.000
T_B   = 0.490   # Field B delayed onset
T_S   = 0.686   # translation start
T_E   = 0.739   # translation end
NF    = 400

T   = np.linspace(0, T_TOT, NF)
f_B = int(T_B / T_TOT * NF)
f_S = int(T_S / T_TOT * NF)
f_E = int(T_E / T_TOT * NF)

# ── Codes ─────────────────────────────────────────────────────────────────────
CW, TCOH, TNOI, CCW = 3.0, 2.0, 1.0, 0.0
NEAR, FAR = 0, 1
RED, GRN  = 0, 1
HEX = {RED: "#CC3333", GRN: "#228B22"}

# ── Subfield markers ──────────────────────────────────────────────────────────
# S0 = Field B coherent (translator)   ●  solid line
# S1 = Field B noise companion         □  dashed line
# S2 = Field A coherent (rotator)      ▲  solid line, faded
# S3 = Field A noise                   ◇  dashed line, faded
MK = {
    0: dict(marker="o", ms=6.5, filled=True,  lw=2.0, ls="-",  alpha=1.0, zorder=5),
    1: dict(marker="s", ms=7.5, filled=False, lw=1.4, ls="--", alpha=1.0, zorder=4),
    2: dict(marker="^", ms=6.0, filled=True,  lw=1.1, ls="-",  alpha=0.45, zorder=3),
    3: dict(marker="D", ms=6.5, filled=False, lw=0.9, ls="--", alpha=0.45, zorder=2),
}

_base   = np.linspace(0.03, 0.97, 13)
T_MARKS = np.unique(np.sort(np.concatenate([_base,
           [T_B + 0.01, (T_S + T_E) / 2]])))


# ── Build arrays ──────────────────────────────────────────────────────────────
def build(cond):
    """
    Returns mot, dep, col  (NF, 4).
    S0/S1 = Field B (delayed, appears at T_B, translates).
    S2/S3 = Field A (non-delayed, present from start, rotates CW).
    Within each field all subfields share depth + color.

    cond 1: no swap
    cond 2: color swap at tStart (fields keep depth, swap color)
    cond 3: depth swap at tStart (fields keep color, swap depth)
    cond 4: depth + color swap at tStart (fields swap both)
    """
    # Initial state
    B_dep0, B_col0 = NEAR, RED    # Field B starts Near=Red
    A_dep0, A_col0 = FAR,  GRN    # Field A starts Far=Green

    # Post-swap state
    if cond == 1:
        B_dep1, B_col1 = NEAR, RED
        A_dep1, A_col1 = FAR,  GRN
    elif cond == 2:   # color swap: fields keep depth, swap color
        B_dep1, B_col1 = NEAR, GRN
        A_dep1, A_col1 = FAR,  RED
    elif cond == 3:   # depth swap: fields keep color, swap depth
        B_dep1, B_col1 = FAR,  RED
        A_dep1, A_col1 = NEAR, GRN
    elif cond == 4:   # depth + color swap: fields swap both
        B_dep1, B_col1 = FAR,  GRN
        A_dep1, A_col1 = NEAR, RED

    mot = np.full((NF, 4), np.nan)
    dep = np.zeros((NF, 4), dtype=int)
    col = np.zeros((NF, 4), dtype=int)

    for f in range(NF):
        sw = f >= f_S   # after-swap flag

        Bd = B_dep1 if sw else B_dep0
        Bc = B_col1 if sw else B_col0
        Ad = A_dep1 if sw else A_dep0
        Ac = A_col1 if sw else A_col0

        # S0 — Field B coherent (hidden before T_B)
        if f >= f_B:
            dep[f, 0] = Bd;  col[f, 0] = Bc
            mot[f, 0] = TCOH if f_S <= f < f_E else CCW

        # S1 — Field B noise (hidden before T_B)
        if f >= f_B:
            dep[f, 1] = Bd;  col[f, 1] = Bc
            mot[f, 1] = TNOI if f_S <= f < f_E else CCW

        # S2 — Field A coherent (always present)
        dep[f, 2] = Ad;  col[f, 2] = Ac
        mot[f, 2] = CW

        # S3 — Field A noise (always present)
        dep[f, 3] = Ad;  col[f, 3] = Ac
        mot[f, 3] = CW

    return mot, dep, col


def build_far(cond):
    """
    Dots✗ version: S0/S1 (●□, Red translator) are NON-delayed — present from start.
    S2/S3 (▲◇, Green rotator) are DELAYED — appear at T_B.

    Post-onset appearance is IDENTICAL to build(cond-4): same colors, same motions.
    The only difference from Cond (cond-4) is which field appeared first.

    cond 5 ↔ cond 1 post-onset  (no swap)
    cond 6 ↔ cond 2 post-onset  (color swap)
    cond 7 ↔ cond 3 post-onset  (depth swap)
    cond 8 ↔ cond 4 post-onset  (depth+color swap)
    """
    B_dep0, B_col0 = NEAR, RED
    A_dep0, A_col0 = FAR,  GRN

    if cond == 5:
        B_dep1, B_col1 = NEAR, RED;  A_dep1, A_col1 = FAR,  GRN
    elif cond == 6:
        B_dep1, B_col1 = NEAR, GRN;  A_dep1, A_col1 = FAR,  RED
    elif cond == 7:
        B_dep1, B_col1 = FAR,  RED;  A_dep1, A_col1 = NEAR, GRN
    elif cond == 8:
        B_dep1, B_col1 = FAR,  GRN;  A_dep1, A_col1 = NEAR, RED

    mot = np.full((NF, 4), np.nan)
    dep = np.zeros((NF, 4), dtype=int)
    col = np.zeros((NF, 4), dtype=int)

    for f in range(NF):
        sw = f >= f_S
        Bd = B_dep1 if sw else B_dep0
        Bc = B_col1 if sw else B_col0
        Ad = A_dep1 if sw else A_dep0
        Ac = A_col1 if sw else A_col0

        # S0 — Field B coherent (translator, NON-delayed, always present)
        dep[f, 0] = Bd;  col[f, 0] = Bc
        mot[f, 0] = TCOH if f_S <= f < f_E else CCW

        # S1 — Field B noise (non-delayed, always present)
        dep[f, 1] = Bd;  col[f, 1] = Bc
        mot[f, 1] = TNOI if f_S <= f < f_E else CCW

        # S2 — Field A coherent (rotator, DELAYED, appears at T_B)
        dep[f, 2] = Ad;  col[f, 2] = Ac
        if f >= f_B:
            mot[f, 2] = CW

        # S3 — Field A noise (rotator, delayed)
        dep[f, 3] = Ad;  col[f, 3] = Ac
        if f >= f_B:
            mot[f, 3] = CW

    return mot, dep, col


# ── Drawing ───────────────────────────────────────────────────────────────────
def draw_track(ax, t_seg, y_seg, s, c_key, onset_mask):
    sty   = MK[s]
    hex_c = HEX[c_key]
    mfc   = hex_c if sty["filled"] else "none"
    alp   = sty["alpha"]

    y_plot = y_seg.astype(float).copy()
    y_plot[~onset_mask] = np.nan
    valid  = ~np.isnan(y_plot)
    if valid.sum() < 2:
        return

    ax.plot(T[len(T) - len(t_seg):len(T) - len(t_seg) + len(t_seg)],
            y_plot,
            color=hex_c, lw=sty["lw"], ls=sty["ls"],
            alpha=alp, solid_capstyle="round", zorder=sty["zorder"])

    t0v = t_seg[valid][0];  t1v = t_seg[valid][-1]
    t_mk = T_MARKS[(T_MARKS >= t0v) & (T_MARKS <= t1v)]
    if len(t_mk):
        y_mk = np.interp(t_mk, t_seg[valid], y_plot[valid])
        ax.plot(t_mk, y_mk, marker=sty["marker"], ms=sty["ms"], mew=0.9,
                mfc=mfc, mec=hex_c, ls="none",
                alpha=alp, zorder=sty["zorder"] + 1)


def draw_panel(axes, mot, dep, col, title, depth_ok, color_ok,
               dots_cued=True, delayed_field="B"):
    """
    delayed_field: "B" → S0/S1 (●□) are delayed; "A" → S2/S3 (▲◇) are delayed.
    """
    ax_m, ax_d, ax_c = axes

    segs = [(0, f_S), (f_S, NF)]
    for s in range(4):
        if delayed_field == "B":
            onset = np.arange(NF) >= f_B if s < 2 else np.ones(NF, bool)
        else:  # delayed_field == "A": S2/S3 delayed, S0/S1 always present
            onset = np.ones(NF, bool) if s < 2 else np.arange(NF) >= f_B
        for start, end in segs:
            t_seg = T[start:end]
            om    = onset[start:end]
            if om.sum() == 0:
                continue
            mid   = (start + end) // 2
            c_key = int(col[min(mid, NF-1), s])

            draw_track(ax_m, t_seg, mot[start:end, s], s, c_key, om)
            draw_track(ax_d, t_seg, dep[start:end, s].astype(float), s, c_key, om)
            draw_track(ax_c, t_seg, col[start:end, s].astype(float), s, c_key, om)

    # Phase decorations
    for ax in (ax_m, ax_d, ax_c):
        ax.axvspan(0,   T_B, alpha=0.06, color="#888", zorder=0)
        ax.axvspan(T_S, T_E, alpha=0.15, color="steelblue", zorder=0)
        ax.axvline(T_B, color="#666", lw=1.2, ls=":", zorder=2)
        ax.axvline(T_S, color="steelblue", lw=1.0, ls="--", zorder=2)
        ax.set_xlim(-0.01, T_TOT + 0.01)
        for sp in ax.spines.values():
            sp.set_linewidth(0.6)

    # Motion axis
    ax_m.set_ylim(-0.5, 3.8)
    ax_m.set_yticks([CCW, TNOI, TCOH, CW])
    ax_m.set_yticklabels(["CCW", "T(n)", "T(c)", "CW"], fontsize=6)
    ax_m.tick_params(axis="y", length=2, pad=1)
    ax_m.tick_params(axis="x", labelbottom=False, bottom=False)
    other = "A" if delayed_field == "B" else "B"
    ax_m.text(T_B / 2, 3.75, f"{other} only\n({delayed_field} hidden)",
              ha="center", va="top", fontsize=5, color="#999", style="italic")
    ax_m.text(T_B + 0.01, 3.75, f"← {delayed_field} onset",
              ha="left", va="top", fontsize=5.5, color="#555")

    # Depth axis
    ax_d.set_ylim(-0.45, 1.55)
    ax_d.set_yticks([NEAR, FAR])
    ax_d.set_yticklabels(["Near", "Far"], fontsize=6)
    ax_d.tick_params(axis="y", length=2, pad=1)
    ax_d.tick_params(axis="x", labelbottom=False, bottom=False)

    # Color axis
    ax_c.set_ylim(-0.45, 1.55)
    ax_c.set_yticks([RED, GRN])
    ax_c.set_yticklabels(["Red", "Grn"], fontsize=6)
    ax_c.tick_params(axis="y", length=2, pad=1)
    ax_c.tick_params(axis="x", labelbottom=False, bottom=False)

    # Plane-color badges after tStart
    mid_post = (f_S + NF) // 2
    for plane, px in [(NEAR, 0.72), (FAR, 0.84)]:
        subs = [s for s in range(4) if dep[mid_post, s] == plane
                and (s >= 2 or mid_post >= f_B)]
        if subs:
            c = HEX[col[mid_post, subs[0]]]
            lbl = ("Near=" + ("Red" if col[mid_post,subs[0]]==RED else "Grn"))  \
                if plane == NEAR else \
                ("Far=" + ("Red" if col[mid_post,subs[0]]==RED else "Grn"))
            ax_c.text(px, -0.38, lbl, transform=ax_c.transAxes,
                      ha="center", va="bottom", fontsize=5.5,
                      color=c, fontweight="bold")

    # Title
    dot_s = "Dots✓" if dots_cued else "Dots✗"
    dep_s = "Depth✓" if depth_ok else "Depth✗"
    col_s = "Color✓" if color_ok else "Color✗"
    ax_m.set_title(
        f"{title}\n{dot_s}  {dep_s}  {col_s}",
        fontsize=9, fontweight="bold", pad=5, color="#111")


# ══════════════════════════════════════════════════════════════════════════════
CONDITIONS = [
    (1, "Cond 1 — No swap",         True,  True),
    (2, "Cond 2 — Color swap",       True,  False),
    (3, "Cond 3 — Depth swap",       False, True),
    (4, "Cond 4 — Depth+Color swap", False, False),
]

with PdfPages(OUT) as pdf:
    fig = plt.figure(figsize=(8.5, 11))
    fig.patch.set_facecolor("white")

    fig.text(0.5, 0.978,
             "Depth × Color Decoupling — Four Conditions (100% swaps)",
             ha="center", va="top", fontsize=13, fontweight="bold", color="#111")
    fig.text(0.5, 0.957,
             "Field B (delayed, ●□) always translates  ·  "
             "Field A (non-delayed, ▲◇) always rotates  ·  "
             "Both fields swap together → single color per plane throughout",
             ha="center", va="top", fontsize=8, color="#555", style="italic")
    fig.text(0.5, 0.941,
             "DFD = Near = Red  ·  Field A = Far = Green  ·  "
             "Gray shade = Field B hidden  ·  Blue band = translation window",
             ha="center", va="top", fontsize=7, color="#777")

    outer = gridspec.GridSpec(2, 2,
                              top=0.930, bottom=0.16,
                              left=0.09, right=0.97,
                              hspace=0.52, wspace=0.28)

    row_lbl = ["Motion\ntype", "Depth\nplane", "Color\nident."]

    for idx, (cond, title, depth_ok, color_ok) in enumerate(CONDITIONS):
        row = idx // 2;  col_ = idx % 2
        mot, dep, col = build(cond)

        inner = gridspec.GridSpecFromSubplotSpec(
            3, 1, subplot_spec=outer[row, col_],
            height_ratios=[4, 2, 2], hspace=0.10)

        ax_m = fig.add_subplot(inner[0])
        ax_d = fig.add_subplot(inner[1], sharex=ax_m)
        ax_c = fig.add_subplot(inner[2], sharex=ax_m)

        draw_panel((ax_m, ax_d, ax_c), mot, dep, col,
                   title, depth_ok, color_ok)

        if col_ == 0:
            for ax, rl in zip((ax_m, ax_d, ax_c), row_lbl):
                ax.set_ylabel(rl, fontsize=6.5, labelpad=3)

    # ── Summary table ─────────────────────────────────────────────────────────
    ty = 0.148
    fig.text(0.5, ty, "What changes at tStart?",
             ha="center", va="top", fontsize=9, fontweight="bold", color="#1a1a6e")

    cxs  = [0.06, 0.24, 0.42, 0.60, 0.77]
    hdrs = ["", "Cond 1", "Cond 2", "Cond 3", "Cond 4"]
    ty  -= 0.022
    for x, h in zip(cxs, hdrs):
        fig.text(x, ty, h, ha="left", va="top",
                 fontsize=7.5, fontweight="bold", color="#1a1a6e")
    ty -= 0.020
    fig.add_artist(plt.Line2D([0.05, 0.97], [ty + 0.015]*2,
        transform=fig.transFigure, color="#888", lw=0.7))

    tbl = [
        ("Field B (●□) depth",  "Near",      "Near",       "→ Far",      "→ Far"),
        ("Field B (●□) color",  "Red",        "→ Green",    "Red",        "→ Green"),
        ("Field A (▲◇) depth",  "Far",        "Far",        "→ Near",     "→ Near"),
        ("Field A (▲◇) color",  "Green",      "→ Red",      "Green",      "→ Red"),
        ("Near plane after",    "Red  ✓",     "Green  ✓",   "Green  ✓",   "Red  ✓"),
        ("Far plane after",     "Green  ✓",   "Red  ✓",     "Red  ✓",     "Green  ✓"),
        ("Translator (B) depth","Near=DFD ✓", "Near=DFD ✓", "Far≠DFD ✗",  "Far≠DFD ✗"),
        ("Translator (B) color","Red=orig ✓", "Green≠orig ✗","Red=orig ✓", "Green≠orig ✗"),
        ("Analog",              "N baseline", "S&B Exp 2\ncolor swap",
                                              "New",        "= current\nZdCoh"),
    ]

    SEP_AFTER = {3, 5, 7}
    for ri, row in enumerate(tbl):
        ty -= 0.021
        for ci, (x, cell) in enumerate(zip(cxs, row)):
            col_c = "#333"
            if ri >= 6:  # depth/color cue rows — color by ✓/✗
                col_c = "#1a3a8b" if "✓" in cell else "#aa2222" if "✗" in cell else "#444"
            fw = "bold" if ci == 0 else "normal"
            fig.text(x, ty, cell, ha="left", va="top",
                     fontsize=6.8, color=col_c, fontweight=fw)
        if ri in SEP_AFTER:
            fig.add_artist(plt.Line2D([0.05, 0.97], [ty - 0.007]*2,
                transform=fig.transFigure, color="#CCCCCC", lw=0.5))

    # ── Legend ────────────────────────────────────────────────────────────────
    leg = [
        Line2D([0],[0], color="#888", lw=2.0, ls="-",
               marker="o", ms=6.5, mfc="#888", mec="#888",
               label="S0 ● Field B coherent (translator)"),
        Line2D([0],[0], color="#888", lw=1.4, ls="--",
               marker="s", ms=7.5, mfc="none", mec="#888",
               label="S1 □ Field B noise companion"),
        Line2D([0],[0], color="#888", lw=1.1, ls="-",  alpha=0.5,
               marker="^", ms=6.0, mfc="#888", mec="#888",
               label="S2 ▲ Field A coherent (rotator)"),
        Line2D([0],[0], color="#888", lw=0.9, ls="--", alpha=0.5,
               marker="D", ms=6.5, mfc="none", mec="#888",
               label="S3 ◇ Field A noise"),
        Line2D([0],[0], color="#CC3333", lw=2.5, label="Red line = dot is Red"),
        Line2D([0],[0], color="#228B22", lw=2.5, label="Green line = dot is Green"),
        Patch(facecolor="steelblue", alpha=0.2, label="Translation window"),
    ]
    fig.legend(handles=leg, loc="lower center", ncol=4,
               fontsize=6.8, frameon=True, framealpha=0.92,
               edgecolor="#CCC", bbox_to_anchor=(0.5, 0.003))

    pdf.savefig(fig, bbox_inches="tight", facecolor="white")
    plt.close()

    # ══════════════════════════════════════════════════════════════════════════
    # Page 2 — DFD = Far  (Field A delayed + translating)
    # ══════════════════════════════════════════════════════════════════════════
    CONDITIONS_FAR = [
        (5, "Cond 5 — No swap",         True,  True),   # post-onset = Cond 1: Near+Red translates
        (6, "Cond 6 — Color swap",       True,  False),  # post-onset = Cond 2: Near+Green translates
        (7, "Cond 7 — Depth swap",       False, True),   # post-onset = Cond 3: Far+Red translates
        (8, "Cond 8 — Depth+Color swap", False, False),  # post-onset = Cond 4: Far+Green translates
    ]

    fig2 = plt.figure(figsize=(8.5, 11))
    fig2.patch.set_facecolor("white")

    fig2.text(0.5, 0.978,
              "Depth × Color Decoupling — Converse Four Conditions (DFD = Far)",
              ha="center", va="top", fontsize=13, fontweight="bold", color="#111")
    fig2.text(0.5, 0.957,
              "Field B (●□, Red) translates — NON-delayed, present from start  ·  "
              "Field A (▲◇, Green) rotates — DELAYED, appears at T_B",
              ha="center", va="top", fontsize=8, color="#555", style="italic")
    fig2.text(0.5, 0.941,
              "Post-onset appearance identical to matched Cond 1–4  ·  "
              "Only difference: temporal cue (onset) points to the rotator, not the translator  ·  "
              "Blue band = translation window",
              ha="center", va="top", fontsize=7, color="#777")

    outer2 = gridspec.GridSpec(2, 2,
                               top=0.930, bottom=0.16,
                               left=0.09, right=0.97,
                               hspace=0.52, wspace=0.28)

    for idx, (cond, title, depth_ok, color_ok) in enumerate(CONDITIONS_FAR):
        row = idx // 2;  col_ = idx % 2
        mot, dep, col = build_far(cond)

        inner = gridspec.GridSpecFromSubplotSpec(
            3, 1, subplot_spec=outer2[row, col_],
            height_ratios=[4, 2, 2], hspace=0.10)

        ax_m = fig2.add_subplot(inner[0])
        ax_d = fig2.add_subplot(inner[1], sharex=ax_m)
        ax_c = fig2.add_subplot(inner[2], sharex=ax_m)

        draw_panel((ax_m, ax_d, ax_c), mot, dep, col,
                   title, depth_ok, color_ok,
                   dots_cued=False, delayed_field="A")

        if col_ == 0:
            for ax, rl in zip((ax_m, ax_d, ax_c), row_lbl):
                ax.set_ylabel(rl, fontsize=6.5, labelpad=3)

    # Summary table for page 2
    ty2 = 0.148
    fig2.text(0.5, ty2, "What changes at tStart?  (DFD = Far, ●□ = Field A)",
              ha="center", va="top", fontsize=9, fontweight="bold", color="#1a1a6e")

    cxs2  = [0.06, 0.24, 0.42, 0.60, 0.77]
    hdrs2 = ["", "Cond 5", "Cond 6", "Cond 7", "Cond 8"]
    ty2  -= 0.022
    for x, h in zip(cxs2, hdrs2):
        fig2.text(x, ty2, h, ha="left", va="top",
                  fontsize=7.5, fontweight="bold", color="#1a1a6e")
    ty2 -= 0.020
    fig2.add_artist(plt.Line2D([0.05, 0.97], [ty2 + 0.015]*2,
        transform=fig2.transFigure, color="#888", lw=0.7))

    tbl2 = [
        ("Field B (●□) depth",  "Near",       "Near",       "→ Far",      "→ Far"),
        ("Field B (●□) color",  "Red",        "→ Green",    "Red",        "→ Green"),
        ("Field A (▲◇) depth",  "Far",        "Far",        "→ Near",     "→ Near"),
        ("Field A (▲◇) color",  "Green",      "→ Red",      "Green",      "→ Red"),
        ("Near plane after",    "Red  ✓",     "Green  ✓",   "Green  ✓",   "Red  ✓"),
        ("Far plane after",     "Green  ✓",   "Red  ✓",     "Red  ✓",     "Green  ✓"),
        ("Translator (B) depth","Near=DFD ✓", "Near=DFD ✓", "Far≠DFD ✗",  "Far≠DFD ✗"),
        ("Translator (B) color","Red=DFD ✓",  "Grn≠DFD ✗",  "Red=DFD ✓",  "Grn≠DFD ✗"),
        ("Dots✗ analog of",     "Cond 1",     "Cond 2",     "Cond 3",     "Cond 4"),
    ]

    for ri, row in enumerate(tbl2):
        ty2 -= 0.021
        for ci, (x, cell) in enumerate(zip(cxs2, row)):
            col_c = "#333"
            if ri >= 6:
                col_c = "#1a3a8b" if "✓" in cell else "#aa2222" if "✗" in cell else "#444"
            fw = "bold" if ci == 0 else "normal"
            fig2.text(x, ty2, cell, ha="left", va="top",
                      fontsize=6.8, color=col_c, fontweight=fw)
        if ri in SEP_AFTER:
            fig2.add_artist(plt.Line2D([0.05, 0.97], [ty2 - 0.007]*2,
                transform=fig2.transFigure, color="#CCCCCC", lw=0.5))

    fig2.legend(handles=leg, loc="lower center", ncol=4,
                fontsize=6.8, frameon=True, framealpha=0.92,
                edgecolor="#CCC", bbox_to_anchor=(0.5, 0.003))

    pdf.savefig(fig2, bbox_inches="tight", facecolor="white")
    plt.close()

print(f"Wrote: {OUT}")
