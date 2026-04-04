#!/usr/bin/env python3
"""
Reference feature trajectory diagrams for DepthParam (no-swap, R/G balanced).

4 panels in a 2×2 grid:
  Rows: Near / Far  (depth of the delayed Field B)
  Cols: CUED / UNCUED

Color:  Field A (S0,S1) = Green (non-delayed)
        Field B (S2,S3) = Red   (delayed, hidden before ONSET)
No swaps. Rotation: Field A = CW, Field B = CCW.

Usage:  python3 depthparam_trajectories.py [output_path.png]
"""

import sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.lines import Line2D

# ── timing (75 Hz) ──────────────────────────────────────────────────
ONSET   = 56   # Field B appears  (~750 ms)
T_START = 78   # translation onset (~750 + 300 ms)
T_END   = 84   # translation ends  (80 ms = 6 frames)
TOTAL   = 114  # total frames

# ── codes ────────────────────────────────────────────────────────────
CW, LINEAR, NONCOH, CCW = 1, 2, 3, 4
NEAR, FAR = 1, 2

# ── colors ───────────────────────────────────────────────────────────
CMAP = {"R": "#CC3333", "G": "#228B22"}

SPECS = [
    {"marker": "o", "filled": True,  "s": 22, "lw": 1.0},   # S0 FieldA
    {"marker": "s", "filled": False, "s": 48, "lw": 1.5},   # S1 FieldA
    {"marker": "^", "filled": True,  "s": 26, "lw": 1.0},   # S2 FieldB
    {"marker": "D", "filled": False, "s": 56, "lw": 1.5},   # S3 FieldB
]


def build(delayed_depth, cued):
    """
    delayed_depth : NEAR or FAR  — depth of Field B (delayed)
    cued          : True  → Field B translates (CUED)
                    False → Field A translates (UNCUED)

    Returns (mt, colors, depth) arrays of shape (TOTAL, 4).
      S0,S1 = Field A (non-delayed, Green, CW, opposite depth)
      S2,S3 = Field B (delayed, Red, CCW, delayed_depth)
    """
    N = TOTAL
    mt     = np.zeros((N, 4), dtype=int)
    colors = np.empty((N, 4), dtype=object)
    depth  = np.zeros((N, 4), dtype=int)

    a_depth = FAR  if delayed_depth == NEAR else NEAR
    b_depth = delayed_depth

    for f in range(N):
        # Field A: non-delayed, CW, Red (solid), a_depth  [matches Fig 1B: red=non-delayed]
        mt[f, 0] = CW;  mt[f, 1] = CW
        colors[f, 0] = "R";  colors[f, 1] = "R"
        depth[f, 0] = a_depth;  depth[f, 1] = a_depth

        # Field B: delayed, hidden before ONSET, Green (dashed)  [matches Fig 1B: green=delayed]
        if f < ONSET:
            mt[f, 2] = 0;  mt[f, 3] = 0
            colors[f, 2] = None;  colors[f, 3] = None
            depth[f, 2] = 0;  depth[f, 3] = 0
        else:
            mt[f, 2] = CCW;  mt[f, 3] = CCW
            colors[f, 2] = "G";  colors[f, 3] = "G"
            depth[f, 2] = b_depth;  depth[f, 3] = b_depth

        # Translation window
        if T_START <= f < T_END:
            if cued:
                # CUED: Field B translates
                mt[f, 2] = LINEAR   # S2: coherent
                mt[f, 3] = NONCOH   # S3: noise
            else:
                # UNCUED: Field A translates
                mt[f, 0] = LINEAR   # S0: coherent
                mt[f, 1] = NONCOH   # S1: noise

    return mt, colors, depth


# ── plotting helpers ──────────────────────────────────────────────────

def _draw_field_lines(ax, data_arr, color_arr):
    """
    Draw one continuous line per sub-array using Fig 1B line conventions:
      Green dashed  = delayed field   (Field B: S2, S3)
      Red solid     = non-delayed field (Field A: S0, S1)
    Frames where data == 0 (pre-onset hidden dots) are masked as NaN.
    """
    nF, nS = data_arr.shape
    frames = np.arange(nF)

    for s in range(nS):
        # Determine color from the first non-None entry
        c_key = None
        for f in range(nF):
            ck = color_arr[f, s]
            if ck in CMAP:
                c_key = ck
                break
        if c_key is None:
            continue

        color = CMAP[c_key]
        ls  = "--" if c_key == "G" else "-"   # green dashed, red solid
        lw  = 1.8

        y = data_arr[:, s].astype(float)
        y[y == 0] = np.nan          # hide pre-onset frames
        ax.plot(frames, y, color=color, linestyle=ls, linewidth=lw, zorder=2)


def _phase_markers(ax):
    ax.axvspan(T_START, T_END, alpha=0.10, color="blue", label="_")
    ax.axvline(ONSET,   ls=":", color="gray", lw=0.8)
    ax.axvline(T_START, ls="--", color="blue", lw=0.8)
    ax.axvline(T_END,   ls="--", color="blue", lw=0.8)


def _legend(ax):
    handles = [
        Line2D([0],[0], color="#CC3333", linestyle="-",  linewidth=1.8,
               label="Field A — non-delayed (red solid)"),
        Line2D([0],[0], color="#228B22", linestyle="--", linewidth=1.8,
               label="Field B — delayed onset (green dashed)"),
    ]
    ax.legend(handles=handles, loc="upper right", fontsize=7, framealpha=0.8)


def plot_panel(ax_mt, ax_depth, mt_arr, color_arr, depth_arr, title, perf):
    # Motion type
    _draw_field_lines(ax_mt, mt_arr, color_arr)
    ax_mt.set_title(title, fontsize=10, fontweight="bold")
    ax_mt.set_ylabel("Motion type", fontsize=8)
    ax_mt.set_yticks([1, 2, 3, 4])
    ax_mt.set_yticklabels(["CW rot", "Trans (coh)", "Trans (noise)", "CCW rot"], fontsize=8)
    ax_mt.set_ylim(0.5, 4.5)
    ax_mt.tick_params(axis="x", labelbottom=False)
    _phase_markers(ax_mt)
    _legend(ax_mt)

    # Annotate performance
    ax_mt.text(0.02, 0.05, perf, transform=ax_mt.transAxes,
               fontsize=9, color="#333333",
               bbox=dict(boxstyle="round,pad=0.2", fc="lightyellow", ec="gray", alpha=0.9))

    # Depth plane
    _draw_field_lines(ax_depth, depth_arr, color_arr)
    ax_depth.set_xlabel("Frame", fontsize=8)
    ax_depth.set_ylabel("Depth plane", fontsize=8)
    ax_depth.set_yticks([1, 2])
    ax_depth.set_yticklabels(["Near", "Far"], fontsize=8)
    ax_depth.set_ylim(0.5, 2.5)
    _phase_markers(ax_depth)

    for ax in (ax_mt, ax_depth):
        ax.axvline(ONSET, ls=":", color="gray", lw=0.8)


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else "depthparam_trajectories.png"

    # 2×2: rows = CUED (top) / UNCUED (bottom) [follows Fig 1B convention]
    #       cols = Far translates (left) / Near translates (right)
    # Each column pairs the two cueing variants of the same translating depth.
    conditions = [
        # (delayed_depth, cued, row_label, translating_depth_label, performance_note)
        #  row=0 (CUED), col=0 (Far translates)
        (FAR,  True,  "CUED",   "Far translates",   "~84–91%  (***)"),
        #  row=0 (CUED), col=1 (Near translates)
        (NEAR, True,  "CUED",   "Near translates",  "~50–53%  (near chance)"),
        #  row=1 (UNCUED), col=0 (Far translates)
        (NEAR, False, "UNCUED", "Far translates",   "~69–75%  (**) "),
        #  row=1 (UNCUED), col=1 (Near translates)
        (FAR,  False, "UNCUED", "Near translates",  "~28–44%  (n.s./*)"),
    ]

    fig = plt.figure(figsize=(14, 10))
    fig.suptitle(
        "DepthParam — Feature Trajectories (no swap, R/G balanced)\n"
        "Field A (Red solid) = non-delayed   |   Field B (Green dashed) = delayed onset\n"
        "Blue band = translation window (80 ms).  Dotted line = Field B onset (~750 ms).  "
        "Performance = pooled 0.05–0.15 m single sessions.",
        fontsize=9, y=1.01
    )

    outer = gridspec.GridSpec(2, 2, hspace=0.55, wspace=0.35,
                              left=0.08, right=0.97, top=0.93, bottom=0.05)

    row_labels = ["CUED\n(delayed field translates)", "UNCUED\n(non-delayed field translates)"]
    col_labels  = ["Far translates", "Near translates"]

    for idx, (ddepth, cued, cue_lbl, trans_lbl, perf) in enumerate(conditions):
        row = idx // 2
        col = idx % 2

        inner = gridspec.GridSpecFromSubplotSpec(
            2, 1, subplot_spec=outer[row, col],
            height_ratios=[3, 1.5], hspace=0.08)

        ax_mt    = fig.add_subplot(inner[0])
        ax_depth = fig.add_subplot(inner[1], sharex=ax_mt)

        depth_lbl = "Near" if ddepth == NEAR else "Far"
        title = f"{cue_lbl}  |  delayed field = {depth_lbl}\n→ {trans_lbl}"

        mt_arr, color_arr, depth_arr = build(ddepth, cued)
        plot_panel(ax_mt, ax_depth, mt_arr, color_arr, depth_arr, title, perf)

        # Row / col annotations on outer edges
        if col == 0:
            ax_mt.set_ylabel(f"{row_labels[row]}\n\nMotion type", fontsize=8)
        if row == 0:
            ax_mt.set_title(f"{col_labels[col]}\n\n" + ax_mt.get_title(),
                            fontsize=9, fontweight="bold")

    # Add a clear summary annotation
    fig.text(0.5, -0.02,
             "Columns pair by translating field depth (Far left, Near right).  "
             "Rows: CUED = delayed field translates (top);  UNCUED = non-delayed translates (bottom).\n"
             "Left column: Far translation → high performance regardless of which field was delayed.  "
             "Right column: Near translation → low performance regardless of cueing.",
             ha="center", fontsize=8, style="italic", color="#444444")

    plt.savefig(out, dpi=180, bbox_inches="tight")
    plt.close()
    print(f"Wrote: {out}")


if __name__ == "__main__":
    main()
