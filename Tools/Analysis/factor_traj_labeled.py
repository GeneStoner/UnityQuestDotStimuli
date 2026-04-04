#!/usr/bin/env python3
"""
Factor-labeled trajectory figure for all depth conditions.
12 panels: N / ZdA / ZdB × CUED Near / UNCUED Near / CUED Far / UNCUED Far
Each panel shows motion type + depth plane trajectories with F1/F2/F3 labels.

Usage: python3 factor_traj_labeled.py [output.png]
"""

import sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.lines import Line2D

ONSET   = 56
T_START = 78
T_END   = 84
TOTAL   = 114

CW, LINEAR, NONCOH, CCW = 1, 2, 3, 4
NEAR, FAR = 1, 2

GREEN = "#228B22"
RED   = "#CC3333"

SPECS = [
    {"marker": "o", "filled": True,  "s": 16, "lw": 1.0, "color": GREEN},  # S0
    {"marker": "s", "filled": False, "s": 36, "lw": 1.2, "color": GREEN},  # S1
    {"marker": "^", "filled": True,  "s": 18, "lw": 1.0, "color": RED},    # S2
    {"marker": "D", "filled": False, "s": 40, "lw": 1.2, "color": RED},    # S3
]


def build(swap, delayed_depth, cued):
    """
    delayed_depth : NEAR or FAR — depth of Field B (the delayed field)
    cued          : True  → Field B (S2/S3) translates
                    False → Field A (S0/S1) translates
    swap          : 'N', 'ZdA', 'ZdB'

    Field A depth = opposite of delayed_depth.
    """
    a_depth = FAR if delayed_depth == NEAR else NEAR
    b_depth = delayed_depth

    mt    = np.zeros((TOTAL, 4), dtype=int)
    depth = np.zeros((TOTAL, 4), dtype=int)

    for f in range(TOTAL):
        ao  = f >= ONSET
        as_ = f >= T_START
        tr  = T_START <= f < T_END

        # Pre-swap defaults
        m = [CW, CW, CCW if ao else 0, CCW if ao else 0]
        d = [a_depth, a_depth,
             b_depth if ao else 0, b_depth if ao else 0]

        if as_:
            if swap == 'ZdA':
                # S0↔S2 swap: S0→b_depth, S2→a_depth; S1 stays a_depth, S3 stays b_depth
                d = [b_depth, a_depth, a_depth, b_depth]
                if tr:
                    if cued:   m = [CW,     NONCOH, LINEAR, CW]
                    else:      m = [LINEAR,  CCW,   CCW,    NONCOH]
                else:          m = [CW,      CCW,   CCW,    CW]

            elif swap == 'ZdB':
                # S1↔S3 swap: S1→b_depth, S3→a_depth; S0 stays a_depth, S2 stays b_depth
                d = [a_depth, b_depth, b_depth, a_depth]
                if tr:
                    if cued:   m = [CW,     NONCOH, LINEAR, CW]
                    else:      m = [LINEAR,  CCW,   CCW,    NONCOH]
                else:          m = [CW,      CCW,   CCW,    CW]

            else:  # N — no swap
                d = [a_depth, a_depth, b_depth, b_depth]
                if tr:
                    if cued:   m = [CW,     CW,    LINEAR, NONCOH]
                    else:      m = [LINEAR, NONCOH, CCW,   CCW]
                else:          m = [CW,     CW,    CCW,    CCW]

        mt[f]    = m
        depth[f] = d

    return mt, depth


def get_factors(swap, delayed_depth, cued):
    """Return (F1, F2, F3, translation_depth)."""
    a_depth = FAR if delayed_depth == NEAR else NEAR

    # Which subfield translates, and where?
    if swap == 'N':
        trans_depth = delayed_depth if cued else a_depth  # S2 stays, S0 stays
    elif swap == 'ZdA':
        # S0→b_depth, S2→a_depth
        trans_depth = a_depth if cued else delayed_depth   # S2→a_depth, S0→b_depth
    elif swap == 'ZdB':
        # S0 and S2 unchanged
        trans_depth = delayed_depth if cued else a_depth

    f1 = "CUED"   if cued else "UNCUED"
    f2 = "SAME"   if trans_depth == delayed_depth else "DIFF"
    f3 = "Near"   if trans_depth == NEAR else "Far"

    return f1, f2, f3, trans_depth


def plot_panel(ax_mt, ax_depth, mt, depth, f1, f2, f3, trans_depth, label):
    sample = list(range(0, TOTAL, max(1, TOTAL // 20)))
    if sample[-1] != TOTAL - 1:
        sample.append(TOTAL - 1)

    for s in range(4):
        sp  = SPECS[s]
        col = sp["color"]

        ax_mt.plot(np.arange(TOTAL), mt[:, s],
                   color="#E8E8E8", lw=0.4, zorder=1)
        ax_depth.plot(np.arange(TOTAL), depth[:, s],
                      color="#E8E8E8", lw=0.4, zorder=1)

        xs_mt, ys_mt = [], []
        xs_d,  ys_d  = [], []
        for f in sample:
            if mt[f, s] != 0:
                xs_mt.append(f); ys_mt.append(mt[f, s])
            if depth[f, s] != 0:
                xs_d.append(f);  ys_d.append(depth[f, s])

        def scatter(ax, xs, ys):
            if not xs:
                return
            if sp["filled"]:
                ax.scatter(xs, ys, marker=sp["marker"], c=col,
                           edgecolors="none", s=sp["s"], zorder=3+s)
            else:
                ax.scatter(xs, ys, marker=sp["marker"], facecolors="none",
                           edgecolors=col, s=sp["s"],
                           linewidths=sp["lw"], zorder=3+s)

        scatter(ax_mt,    xs_mt, ys_mt)
        scatter(ax_depth, xs_d,  ys_d)

    # Phase markers
    for ax in (ax_mt, ax_depth):
        ax.axvspan(T_START, T_END, alpha=0.10, color="blue")
        ax.axvline(ONSET,   ls=":", color="gray", lw=0.7)
        ax.axvline(T_START, ls="--", color="blue", lw=0.7)
        ax.axvline(T_END,   ls="--", color="blue", lw=0.7)

    # Gold band on the plane that actually translates
    hi_y = 2 if trans_depth == FAR else 1
    ax_depth.axhspan(hi_y - 0.45, hi_y + 0.45,
                     alpha=0.20, color="gold", zorder=0)

    # Motion axis
    ax_mt.set_yticks([1, 2, 3, 4])
    ax_mt.set_yticklabels(["CW", "T-coh", "T-noise", "CCW"], fontsize=5.5)
    ax_mt.set_ylim(0.5, 4.5)
    ax_mt.tick_params(axis="x", labelbottom=False)
    ax_mt.tick_params(axis="y", labelsize=5.5)

    # Depth axis
    ax_depth.set_yticks([1, 2])
    ax_depth.set_yticklabels(["Near", "Far"], fontsize=6)
    ax_depth.set_ylim(0.5, 2.5)
    ax_depth.set_xlabel("Frame", fontsize=6)
    ax_depth.tick_params(axis="both", labelsize=5.5)

    # Factor label colours
    f1_c = "#005A9C" if f1 == "CUED"    else "#8B0000"
    f2_c = "#006400" if f2 == "SAME"    else "#8B4500"
    f3_c = "#005A9C" if f3 == "Far"     else "#8B4500"

    # Title: condition name on line 1, factor labels on line 2
    ax_mt.set_title(label, fontsize=7, fontweight="bold", pad=1)

    # Factor annotation box below title
    ax_mt.text(0.5, 1.01,
               f"F1={f1}  |  F2={f2}  |  F3={f3}",
               transform=ax_mt.transAxes, ha="center", va="bottom",
               fontsize=6.5,
               bbox=dict(boxstyle="round,pad=0.2", fc="#FFFFCC",
                         ec="gray", alpha=0.95))


# ── master layout ─────────────────────────────────────────────────────────────

CONDITIONS = [
    # (swap, delayed_depth, cued)
    ("N",   NEAR, True),   # col 0
    ("N",   NEAR, False),  # col 1
    ("N",   FAR,  True),   # col 2
    ("N",   FAR,  False),  # col 3
    ("ZdA", NEAR, True),
    ("ZdA", NEAR, False),
    ("ZdA", FAR,  True),
    ("ZdA", FAR,  False),
    ("ZdB", NEAR, True),
    ("ZdB", NEAR, False),
    ("ZdB", FAR,  True),
    ("ZdB", FAR,  False),
]

COL_HEADERS = [
    "CUED Near\n(delayed=Near)",
    "UNCUED Near\n(delayed=Near)",
    "CUED Far\n(delayed=Far)",
    "UNCUED Far\n(delayed=Far)",
]

ROW_HEADERS = ["N\n(no swap)", "ZdA\n(S0↔S2)", "ZdB\n(S1↔S3)"]

COND_LABELS = [
    "N — CUED Near",    "N — UNCUED Near",    "N — CUED Far",    "N — UNCUED Far",
    "ZdA — CUED Near",  "ZdA — UNCUED Near",  "ZdA — CUED Far",  "ZdA — UNCUED Far",
    "ZdB — CUED Near",  "ZdB — UNCUED Near",  "ZdB — CUED Far",  "ZdB — UNCUED Far",
]


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else "factor_labeled_trajectories.png"

    fig = plt.figure(figsize=(20, 15))
    fig.patch.set_facecolor("white")

    fig.suptitle(
        "Factor-Labeled Trajectories — All Depth Conditions (N / ZdA / ZdB)\n"
        "Green = Field A (S0●, S1□) non-delayed   |   Red = Field B (S2▲, S3◇) delayed\n"
        "Yellow box = F1/F2/F3 factor labels.   Gold band in depth row = plane where translation occurs.\n"
        "F1 dot cueing (CUED/UNCUED)   F2 depth-field match (SAME/DIFF)   F3 translation depth (Near/Far)",
        fontsize=9, y=1.02, va="bottom"
    )

    outer = gridspec.GridSpec(3, 4, hspace=0.80, wspace=0.40,
                              left=0.07, right=0.99, top=0.94, bottom=0.03)

    for idx, ((swap, ddepth, cued), label) in enumerate(zip(CONDITIONS, COND_LABELS)):
        row = idx // 4
        col = idx % 4

        inner = gridspec.GridSpecFromSubplotSpec(
            2, 1, subplot_spec=outer[row, col],
            height_ratios=[3, 1.5], hspace=0.06)

        ax_mt    = fig.add_subplot(inner[0])
        ax_depth = fig.add_subplot(inner[1], sharex=ax_mt)

        mt, depth = build(swap, ddepth, cued)
        f1, f2, f3, trans_depth = get_factors(swap, ddepth, cued)

        plot_panel(ax_mt, ax_depth, mt, depth, f1, f2, f3, trans_depth, label)

        # Row header (left edge of each row)
        if col == 0:
            ax_mt.set_ylabel(f"{ROW_HEADERS[row]}\n\nMotion", fontsize=7,
                             fontweight="bold")
        else:
            ax_mt.set_ylabel("Motion", fontsize=6)
        ax_depth.set_ylabel("Depth", fontsize=6)

        # Column header (top of each column, row 0 only)
        if row == 0:
            ax_mt.set_title(
                f"{COL_HEADERS[col]}\n{label}",
                fontsize=7, fontweight="bold", pad=1)

    # Shared legend
    handles = [
        Line2D([0],[0], marker="o", color="w", markerfacecolor=GREEN,
               markersize=6, ls="None", label="S0 FieldA coh"),
        Line2D([0],[0], marker="s", color="w", markeredgecolor=GREEN,
               markerfacecolor="none", markersize=6, markeredgewidth=1.2,
               ls="None", label="S1 FieldA noncoh"),
        Line2D([0],[0], marker="^", color="w", markerfacecolor=RED,
               markersize=6, ls="None", label="S2 FieldB coh (delayed)"),
        Line2D([0],[0], marker="D", color="w", markeredgecolor=RED,
               markerfacecolor="none", markersize=6, markeredgewidth=1.2,
               ls="None", label="S3 FieldB noncoh (delayed)"),
        Line2D([0],[0], color="none", label=""),
        Line2D([0],[0], color="blue", ls="--", lw=1, label="tStart / tEnd"),
        Line2D([0],[0], color="gray", ls=":", lw=1, label="FieldB onset"),
    ]
    fig.legend(handles=handles, loc="lower center", ncol=7,
               fontsize=7, framealpha=0.9,
               bbox_to_anchor=(0.5, -0.01))

    plt.savefig(out, dpi=160, bbox_inches="tight", facecolor="white")
    plt.close()
    print(f"Wrote: {out}")


if __name__ == "__main__":
    main()
