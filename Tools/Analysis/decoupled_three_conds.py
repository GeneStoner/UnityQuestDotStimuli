#!/usr/bin/env python3
"""
Three key conditions for Depth × Color decoupling.
All maintain single color per depth plane throughout the trial.

A: Dots✓  Depth✓  Color✓  — no swap (baseline)
B: Dots✓  Depth✓  Color✗  — global color swap at tStart (Stoner & Blanc)
C: Dots✓  Depth✗  Color✓  — translator depth swap + global color swap

DFD = Near = Red  (Far = Green).  CUED throughout (delayed field translates).

Output: Agents/WriteUps/decoupled_three_conds.pdf
"""

import sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.lines import Line2D
from matplotlib.patches import Patch, FancyArrowPatch

OUT = (sys.argv[1] if len(sys.argv) > 1 else
       "/Users/genestoner1/Projects/ObjectBasedAttention/VRDots/"
       "Agents/WriteUps/decoupled_three_conds.pdf")

# ── Timing ────────────────────────────────────────────────────────────────────
T_TOT = 1.000
T_B   = 0.490   # Field B (delayed) onset
T_S   = 0.686   # translation start
T_E   = 0.739   # translation end
NF    = 400

T = np.linspace(0, T_TOT, NF)
f_B = int(T_B / T_TOT * NF)
f_S = int(T_S / T_TOT * NF)
f_E = int(T_E / T_TOT * NF)

# ── Motion codes (y-axis values) ─────────────────────────────────────────────
CW, TCOH, TNOI, CCW = 3.0, 2.0, 1.0, 0.0
MOT_LABELS = {0.0: "CCW", 1.0: "T(n)", 2.0: "T(c)", 3.0: "CW"}

# ── Color / depth codes ───────────────────────────────────────────────────────
NEAR, FAR   = 0, 1
RED,  GRN   = 0, 1
HEX = {RED: "#CC3333", GRN: "#228B22"}

# ── Subfield markers ──────────────────────────────────────────────────────────
# S0 = delayed coherent (translator), S1 = delayed noise companion
# S2 = non-delayed coherent,          S3 = non-delayed noise
MK = {
    0: dict(marker="o", ms=6.0, filled=True,  lw=1.8, ls="-",  zorder=5),
    1: dict(marker="s", ms=7.0, filled=False, lw=1.3, ls="--", zorder=4),
    2: dict(marker="^", ms=5.5, filled=True,  lw=1.0, ls="-",  zorder=3),
    3: dict(marker="D", ms=6.0, filled=False, lw=0.8, ls="--", zorder=2),
}
SF_ALPHA = {0: 1.0, 1: 1.0, 2: 0.50, 3: 0.50}

# Marker time-points (sampled along full trial)
_base   = np.linspace(0.02, 0.98, 14)
T_MARKS = np.unique(np.sort(np.concatenate([_base, [T_B + 0.01, T_S + 0.005, T_E + 0.005]])))


def build_condition(cond):
    """
    Returns mot, dep, col  shape (NF, 4).
    S0/S1 = delayed field (appear at T_B).
    S2/S3 = non-delayed field (present from frame 0).
    DFD = Near = Red  throughout.

    Conditions:
      'A': no swap
      'B': global color swap at f_S
      'C': S0 depth Near->Far + global color swap at f_S
    """
    mot = np.full((NF, 4), np.nan)
    dep = np.zeros((NF, 4), dtype=int)
    col = np.zeros((NF, 4), dtype=int)

    for f in range(NF):
        after_swap = (f >= f_S)

        # ── S0: delayed coherent translator ──────────────────────────────────
        if f < f_B:
            pass  # hidden — leave NaN / don't draw
        else:
            # depth: only C swaps depth at tStart
            if cond == 'C' and after_swap:
                dep[f, 0] = FAR
            else:
                dep[f, 0] = NEAR

            # color:
            #   A → S0 keeps RED (cued color) throughout
            #   B → S0 = entire Field B flips Red→Green at tStart (S&B color swap)
            #   C → S0 keeps RED (cued color); depth changes but color stays
            if cond == 'B' and after_swap:
                col[f, 0] = GRN
            else:
                col[f, 0] = RED

            # motion
            if f_S <= f < f_E:
                mot[f, 0] = TCOH
            else:
                mot[f, 0] = CCW        # delayed field = CCW

        # ── S1: delayed noise companion ───────────────────────────────────────
        if f < f_B:
            pass  # hidden
        else:
            dep[f, 1] = NEAR           # S1 always stays Near
            # color: changes in B and C (global color swap)
            if (cond in ('B', 'C')) and after_swap:
                col[f, 1] = GRN        # Near → Green after swap
            else:
                col[f, 1] = RED        # Near = Red before swap

            if f_S <= f < f_E:
                mot[f, 1] = TNOI
            else:
                mot[f, 1] = CCW

        # ── S2: non-delayed coherent ──────────────────────────────────────────
        dep[f, 2] = FAR                # always Far
        # color: changes in B and C (Far: Green → Red after swap)
        if (cond in ('B', 'C')) and after_swap:
            col[f, 2] = RED
        else:
            col[f, 2] = GRN
        mot[f, 2] = CW                 # non-delayed field = CW throughout

        # ── S3: non-delayed noise ─────────────────────────────────────────────
        dep[f, 3] = FAR
        if (cond in ('B', 'C')) and after_swap:
            col[f, 3] = RED
        else:
            col[f, 3] = GRN
        mot[f, 3] = CW

    return mot, dep, col


def plot_track(ax, t_seg, y_seg, s, c_key, onset_mask=None):
    """Draw one segment of one subfield track with markers."""
    sty   = MK[s]
    hex_c = HEX[c_key]
    mfc   = hex_c if sty["filled"] else "none"
    alp   = SF_ALPHA[s]

    if onset_mask is not None:
        # apply mask (NaN where not yet visible)
        y_plot = y_seg.copy().astype(float)
        y_plot[~onset_mask] = np.nan
        valid = ~np.isnan(y_plot)
    else:
        y_plot = y_seg.astype(float)
        valid  = ~np.isnan(y_plot)

    if valid.sum() < 2:
        return

    ax.plot(t_seg[valid], y_plot[valid],
            color=hex_c, lw=sty["lw"], ls=sty["ls"],
            alpha=alp, solid_capstyle="round", zorder=sty["zorder"])

    # markers at T_MARKS within this segment
    t0_v, t1_v = t_seg[valid][0], t_seg[valid][-1]
    t_mk = T_MARKS[(T_MARKS >= t0_v) & (T_MARKS <= t1_v)]
    if len(t_mk):
        y_mk = np.interp(t_mk, t_seg[valid], y_plot[valid])
        ax.plot(t_mk, y_mk,
                marker=sty["marker"], ms=sty["ms"], mew=0.9,
                mfc=mfc, mec=hex_c, ls="none",
                alpha=alp, zorder=sty["zorder"] + 1)


def draw_panel(axes, mot, dep, col, cond_label,
               dots_ok, depth_ok, color_ok):
    ax_m, ax_d, ax_c = axes

    # For each subfield, split at f_S (swap boundary)
    for s in range(4):
        segs = [(0, f_S), (f_S, NF)]
        for start, end in segs:
            t_seg = T[start:end]
            # S0, S1 are only visible from f_B onward
            if s in (0, 1):
                onset_mask = np.arange(start, end) >= f_B
            else:
                onset_mask = np.ones(end - start, dtype=bool)

            if onset_mask.sum() == 0:
                continue

            # color at midpoint of this segment (post-onset)
            mid = (start + end) // 2
            c_key = int(col[min(mid, NF - 1), s])

            # Motion row
            plot_track(ax_m, t_seg,
                       mot[start:end, s],
                       s, c_key, onset_mask)

            # Depth row
            plot_track(ax_d, t_seg,
                       dep[start:end, s].astype(float),
                       s, c_key, onset_mask)

            # Color row
            plot_track(ax_c, t_seg,
                       col[start:end, s].astype(float),
                       s, c_key, onset_mask)

    # Phase markers
    for ax in (ax_m, ax_d, ax_c):
        # Pre-onset shading (Field B not yet present)
        ax.axvspan(0, T_B, alpha=0.06, color="#888888", zorder=0)
        ax.axvspan(T_S, T_E, alpha=0.13, color="steelblue", zorder=0)
        ax.axvline(T_B, color="#666666", lw=1.2, ls=":", zorder=2)
        ax.axvline(T_S, color="steelblue", lw=0.9, ls="--", zorder=2)

    # Annotate phases on motion axis
    ax_m.text(T_B / 2, 3.62, "Field A only\n(S0,S1 hidden)",
              fontsize=4.8, color="#888", ha="center", va="top", style="italic")
    ax_m.text(T_B + 0.01, 3.62, "← Field B appears",
              fontsize=5.0, color="#555", va="top", ha="left")

    # Motion axis
    ax_m.set_ylim(-0.45, 3.75)
    ax_m.set_yticks([0, 1, 2, 3])
    ax_m.set_yticklabels(["CCW", "T(n)", "T(c)", "CW"], fontsize=5.5)
    ax_m.tick_params(axis="y", length=2, pad=1)
    ax_m.tick_params(axis="x", bottom=False, labelbottom=False)

    # Depth axis
    ax_d.set_ylim(-0.4, 1.5)
    ax_d.set_yticks([NEAR, FAR])
    ax_d.set_yticklabels(["Near", "Far"], fontsize=5.5)
    ax_d.tick_params(axis="y", length=2, pad=1)
    ax_d.tick_params(axis="x", bottom=False, labelbottom=False)

    # Color axis
    ax_c.set_ylim(-0.4, 1.5)
    ax_c.set_yticks([RED, GRN])
    ax_c.set_yticklabels(["Red", "Grn"], fontsize=5.5)
    ax_c.tick_params(axis="y", length=2, pad=1)
    ax_c.tick_params(axis="x", bottom=False, labelbottom=False)

    for ax in (ax_m, ax_d, ax_c):
        ax.set_xlim(-0.01, T_TOT + 0.01)
        for sp in ax.spines.values():
            sp.set_linewidth(0.6)

    # Title
    dot_s = "Dots✓"  if dots_ok  else "Dots✗"
    dep_s = "Depth✓" if depth_ok else "Depth✗"
    clr_s = "Color✓" if color_ok else "Color✗"

    dot_c = "#1a6b1a" if dots_ok  else "#555"
    dep_c = "#1a3a8b" if depth_ok else "#aa2222"
    clr_c = "#228B22" if color_ok else "#CC3333"

    ax_m.set_title(
        f"{cond_label}\n{dot_s}  {dep_s}  {clr_s}",
        fontsize=9, fontweight="bold", pad=5, color="#111")

    # Plane-color summary boxes below the color track
    for plane, label, y_pos in [(NEAR, "Near", 1.3), (FAR, "Far", -0.3)]:
        # get colors in this plane after tStart
        mid_post = (f_S + NF) // 2
        plane_cols = {col[mid_post, s] for s in range(4)
                      if dep[mid_post, s] == plane
                      and not np.isnan(mot[mid_post, s]) or s > 1}
        # for S0/S1 must also be visible
        plane_cols_vis = set()
        for s in range(4):
            visible = (s < 2 and mid_post >= f_B) or s >= 2
            if visible and dep[mid_post, s] == plane:
                plane_cols_vis.add(col[mid_post, s])
        if len(plane_cols_vis) == 1:
            bg = HEX[list(plane_cols_vis)[0]] + "33"
            ec = HEX[list(plane_cols_vis)[0]]
        else:
            bg = "#FFE0E0"; ec = "#CC4400"   # mixed — shouldn't happen


# ══════════════════════════════════════════════════════════════════════════════
# Build and draw
# ══════════════════════════════════════════════════════════════════════════════
CONDITIONS = [
    ('A', "Condition A", True,  True,  True),
    ('B', "Condition B", True,  True,  False),
    ('C', "Condition C", True,  False, True),
]

with PdfPages(OUT) as pdf:
    fig = plt.figure(figsize=(8.5, 11))
    fig.patch.set_facecolor("white")

    fig.text(0.5, 0.975,
             "Three Key Conditions — Depth × Color Decoupling",
             ha="center", va="top", fontsize=13, fontweight="bold", color="#111")
    fig.text(0.5, 0.954,
             "CUED (delayed onset field translates)  ·  DFD = Near = Red  ·  "
             "Far = Green  ·  Near/Far single-color maintained throughout",
             ha="center", va="top", fontsize=8, color="#555", style="italic")

    # Phase legend at top
    phase_txt = (
        "  ↑ B onset (dotted) = Field B (S0●, S1□) first appears     "
        "║ tStart–tEnd (blue band) = translation window"
    )
    fig.text(0.5, 0.938, phase_txt,
             ha="center", va="top", fontsize=7, color="#444")

    # 3 columns, each with 3 sub-rows (motion / depth / color)
    outer = gridspec.GridSpec(1, 3,
                              top=0.920, bottom=0.18,
                              left=0.10, right=0.97,
                              wspace=0.30)

    row_labels = ["Motion\ntype", "Depth\nplane", "Color\nident."]

    for col_i, (cond, lbl, dots_ok, depth_ok, color_ok) in enumerate(CONDITIONS):
        mot, dep, col_arr = build_condition(cond)

        inner = gridspec.GridSpecFromSubplotSpec(
            3, 1, subplot_spec=outer[col_i],
            height_ratios=[4, 2, 2], hspace=0.10)

        ax_m = fig.add_subplot(inner[0])
        ax_d = fig.add_subplot(inner[1], sharex=ax_m)
        ax_c = fig.add_subplot(inner[2], sharex=ax_m)

        draw_panel((ax_m, ax_d, ax_c),
                   mot, dep, col_arr,
                   lbl, dots_ok, depth_ok, color_ok)

        if col_i == 0:
            for ax, rl in zip((ax_m, ax_d, ax_c), row_labels):
                ax.set_ylabel(rl, fontsize=6.5, labelpad=4, color="#333")

    # ── Annotation table below panels ────────────────────────────────────────
    tbl_top = 0.170
    col_xs = [0.10, 0.38, 0.66]
    fig.text(0.5, tbl_top, "Summary — what changes at tStart?",
             ha="center", va="top", fontsize=9, fontweight="bold", color="#1a1a6e")

    rows = [
        ("",         "Condition A",             "Condition B",             "Condition C"),
        ("S0 (●coh translator)",
                     "Near+Red → Near+Red\n(no change)",
                     "Near+Red → Near+Green\n(color changes)",
                     "Near+Red → Far+Red\n(depth changes)"),
        ("S1 (□noi companion)",
                     "Near+Red → Near+Red",
                     "Near+Red → Near+Green\n(color changes)",
                     "Near+Red → Near+Green\n(color changes)"),
        ("S2 (▲coh other)",
                     "Far+Green → Far+Green",
                     "Far+Green → Far+Red\n(color changes)",
                     "Far+Green → Far+Red\n(color changes)"),
        ("S3 (◇noi other)",
                     "Far+Green → Far+Green",
                     "Far+Green → Far+Red\n(color changes)",
                     "Far+Green → Far+Red\n(color changes)"),
        ("Near plane after tStart",
                     "Red  ✓ (clean)",
                     "Green  ✓ (clean)",
                     "Green  ✓ (clean)"),
        ("Far plane after tStart",
                     "Green  ✓ (clean)",
                     "Red  ✓ (clean)",
                     "Red  ✓ (clean)"),
        ("Analog",
                     "N baseline",
                     "Stoner & Blanc\ncolor swap",
                     "ZdA depth swap\n+ global recolor"),
    ]

    y = tbl_top - 0.032
    import textwrap
    for ri, row in enumerate(rows):
        if ri == 0:
            weights = ["bold"] * 4
            cols_   = ["#1a1a6e"] * 4
        else:
            weights = ["bold", "normal", "normal", "normal"]
            cols_   = ["#333", "#333", "#333", "#333"]
        for ci, (x, cell, fw, fc) in enumerate(zip(
                [0.08, 0.30, 0.56, 0.78], row, weights, cols_)):
            fig.text(x, y, cell, ha="left", va="top",
                     fontsize=6.8, fontweight=fw, color=fc)
        y -= 0.050 if ri == 0 else 0.058
        if ri in (0, 4, 6):
            fig.add_artist(plt.Line2D([0.07, 0.97], [y + 0.045, y + 0.045],
                transform=fig.transFigure,
                color="#BBBBBB" if ri > 0 else "#888888", lw=0.6))

    # ── Legend ────────────────────────────────────────────────────────────────
    leg_handles = [
        Line2D([0],[0], color="#888", lw=1.8, ls="-",
               marker="o", ms=6, mfc="#888", mec="#888", label="S0 ● delayed coh (translator)"),
        Line2D([0],[0], color="#888", lw=1.3, ls="--",
               marker="s", ms=7, mfc="none", mec="#888", label="S1 □ delayed noi (companion)"),
        Line2D([0],[0], color="#888", lw=1.0, ls="-",  alpha=0.5,
               marker="^", ms=5.5, mfc="#888", mec="#888", label="S2 ▲ non-delayed coh"),
        Line2D([0],[0], color="#888", lw=0.8, ls="--", alpha=0.5,
               marker="D", ms=6, mfc="none", mec="#888", label="S3 ◇ non-delayed noi"),
        Line2D([0],[0], color="#CC3333", lw=2.0, label="Red line = dot is Red"),
        Line2D([0],[0], color="#228B22", lw=2.0, label="Green line = dot is Green"),
        Patch(facecolor="steelblue", alpha=0.2, label="Translation window"),
    ]
    fig.legend(handles=leg_handles,
               loc="lower center", ncol=4, fontsize=7,
               frameon=True, framealpha=0.92, edgecolor="#CCC",
               bbox_to_anchor=(0.5, 0.005))

    pdf.savefig(fig, bbox_inches="tight", facecolor="white")
    plt.close()

print(f"Wrote: {OUT}")
