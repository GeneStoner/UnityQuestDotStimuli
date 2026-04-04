#!/usr/bin/env python3
"""
Reference trajectories for Exp_DepthSwapCtrl.
6 panels: N / ZdA / ZdB  ×  CUED / UNCUED.
Single rotation config (RotA: FieldA=CW, FieldB=CCW). Both fields red.
FieldA(S0,S1)=Far/CW, FieldB(S2,S3)=Near/CCW (delayed onset).
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
RED = "#CC3333"

SPECS = [
    {"marker": "o", "filled": True,  "s": 22, "lw": 1.0},   # S0
    {"marker": "s", "filled": False, "s": 48, "lw": 1.5},   # S1
    {"marker": "^", "filled": True,  "s": 26, "lw": 1.0},   # S2
    {"marker": "D", "filled": False, "s": 56, "lw": 1.5},   # S3
]

def build(swap, cued):
    """
    swap: 'N', 'ZdA', 'ZdB'
    cued: True = Field B (S2,S3) translates; False = Field A (S0,S1) translates
    """
    mt    = np.zeros((TOTAL, 4), dtype=int)
    depth = np.zeros((TOTAL, 4), dtype=int)

    for f in range(TOTAL):
        ao = f >= ONSET           # after Field B onset
        as_ = f >= T_START        # after swap / translation onset
        tr = T_START <= f < T_END # translation window
        pt = f >= T_END           # post-translation

        # ── default (pre-swap) ───────────────────────────────────────────────
        m = [CW, CW, CCW if ao else 0, CCW if ao else 0]
        d = [FAR, FAR, NEAR if ao else 0, NEAR if ao else 0]

        if as_:
            if swap == 'ZdA':
                # S0↔S2 swap. Near-group(S0,S3)=CW, Far-group(S1,S2)=CCW.
                d = [NEAR, FAR, FAR, NEAR]
                if tr:
                    if cued:   m = [CW,    NONCOH, LINEAR, CW]
                    else:      m = [LINEAR, CCW,   CCW,    NONCOH]
                else:          m = [CW,    CCW,    CCW,    CW]

            elif swap == 'ZdB':
                # S1↔S3 swap. Near-group(S1,S2)=CCW, Far-group(S0,S3)=CW.
                d = [FAR, NEAR, NEAR, FAR]
                if tr:
                    if cued:   m = [CW,    NONCOH, LINEAR, CW]
                    else:      m = [LINEAR, CCW,   CCW,    NONCOH]
                else:          m = [CW,    CCW,    CCW,    CW]

            else:  # N — no swap
                d = [FAR, FAR, NEAR, NEAR]
                if tr:
                    if cued:   m = [CW,    CW,    LINEAR, NONCOH]
                    else:      m = [LINEAR, NONCOH, CCW,  CCW]
                else:          m = [CW,    CW,    CCW,    CCW]

        mt[f]    = m
        depth[f] = d

    return mt, depth


def scatter_subfields(ax, data):
    nF, nS = data.shape
    sample = list(range(0, nF, max(1, nF // 25)))
    if sample[-1] != nF - 1:
        sample.append(nF - 1)
    for s in range(nS):
        sp = SPECS[s]
        ax.plot(np.arange(nF), data[:, s], color="#D0D0D0", lw=0.5, zorder=1)
        xs = [f for f in sample if data[f, s] != 0]
        ys = [data[f, s] for f in xs]
        if not xs:
            continue
        if sp["filled"]:
            ax.scatter(xs, ys, marker=sp["marker"], c=RED,
                       edgecolors="none", s=sp["s"], zorder=3 + s)
        else:
            ax.scatter(xs, ys, marker=sp["marker"], facecolors="none",
                       edgecolors=RED, s=sp["s"], linewidths=sp["lw"], zorder=3 + s)


def add_phase_markers(ax):
    ax.axvspan(T_START, T_END, alpha=0.08, color="blue")
    ax.axvline(ONSET,   ls=":",  color="gray", lw=0.8)
    ax.axvline(T_START, ls="--", color="blue", lw=0.8)
    ax.axvline(T_END,   ls="--", color="blue", lw=0.8)


def add_legend(ax):
    handles = [
        Line2D([0], [0], marker="o", color="w", markerfacecolor=RED,
               markersize=6, ls="None", label="S0 (FieldA)"),
        Line2D([0], [0], marker="s", color="w", markeredgecolor=RED,
               markerfacecolor="none", markersize=7, markeredgewidth=1.5,
               ls="None", label="S1 (FieldA)"),
        Line2D([0], [0], marker="^", color="w", markerfacecolor=RED,
               markersize=6, ls="None", label="S2 (FieldB, delayed)"),
        Line2D([0], [0], marker="D", color="w", markeredgecolor=RED,
               markerfacecolor="none", markersize=7, markeredgewidth=1.5,
               ls="None", label="S3 (FieldB, delayed)"),
    ]
    ax.legend(handles=handles, loc="upper right", fontsize=7)


# Factor labels for each panel.
# F1 (D+/D-): did the delayed field dots coherently translate?
# F2 (P+/P-): did the translating dots stay in the delayed field's onset depth plane?
# F3 (Near/Far): which depth plane contained the coherent translating dots?
PANELS = [
    # (swap, cued, swap_label, F1,   F2,   F3,     technical detail)
    ("N",   True,  "N",   "D+", "P+", "Near",
     "S2=Coh(Near), S3=NonCoh(Near) — delayed field stays in onset plane"),
    ("N",   False, "N",   "D−", "P−", "Far",
     "S0=Coh(Far),  S1=NonCoh(Far)  — non-delayed field translates in Far"),
    ("ZdA", True,  "ZdA", "D+", "P−", "Far",
     "S2=Coh(Far),  S1=NonCoh(Far)  — cued dot swaps Near→Far at tStart"),
    ("ZdA", False, "ZdA", "D−", "P+", "Near",
     "S0=Coh(Near), S3=NonCoh(Near) — S0 swaps Far→Near; translates in onset plane"),
    ("ZdB", True,  "ZdB", "D+", "P+", "Near",
     "S2=Coh(Near), S1=NonCoh(Near) — cued dot stays in onset plane (Near)"),
    ("ZdB", False, "ZdB", "D−", "P−", "Far",
     "S0=Coh(Far),  S3=NonCoh(Far)  — non-delayed field translates in Far"),
]

# Factor label colors
F3_COLOR = {"Near": "#c0392b", "Far": "#1a6faf"}


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else "hypothetical_traj.png"

    n = len(PANELS)
    fig = plt.figure(figsize=(16, 7.0 * n))
    outer = gridspec.GridSpec(n, 1, hspace=0.55)

    fig.text(0.01, 1.0,
             "FieldA(S0●S1□)=Far/CW/Red   FieldB(S2▲S3◇)=Near/CCW/Red (delayed onset)   "
             f"onset=fr{ONSET}  tStart=fr{T_START}  tEnd=fr{T_END}   (75Hz)",
             fontsize=8, color="#555", va="top")

    for i, (swap, cued, swap_label, f1, f2, f3, detail) in enumerate(PANELS):
        mt, depth = build(swap, cued)

        inner = gridspec.GridSpecFromSubplotSpec(
            2, 1, subplot_spec=outer[i], height_ratios=[3, 1.5], hspace=0.08)
        ax_mt    = fig.add_subplot(inner[0])
        ax_depth = fig.add_subplot(inner[1], sharex=ax_mt)

        scatter_subfields(ax_mt, mt)

        # Clean title: swap condition + technical detail on separate lines, no overlap
        cued_str = "CUED" if cued else "UNCUED"
        ax_mt.set_title(f"{swap_label} — {cued_str}\n{detail}",
                        fontsize=9, loc="left", pad=4)

        ax_mt.set_ylabel("motion type", fontsize=9)
        ax_mt.set_yticks([1, 2, 3, 4])
        ax_mt.set_yticklabels(["CW rot", "Trans (coh)", "Trans (noise)", "CCW rot"], fontsize=8)
        ax_mt.set_ylim(0.5, 4.5)
        ax_mt.set_xticklabels([])
        add_phase_markers(ax_mt)
        add_legend(ax_mt)

        # ── Factor label box in pre-onset space (x ~ frame 28, centre of 0..56) ──
        f3_col = F3_COLOR[f3]
        box_x = 28   # midpoint of pre-onset region
        box_y = 3.55 # near top of motion axis (ylim 0.5–4.5)

        factor_text = (
            f"F1: {f1}  (delayed={'translates' if f1=='D+' else 'does NOT translate'})\n"
            f"F2: {f2}  (trans in onset plane={'YES' if f2=='P+' else 'NO'})\n"
            f"F3: {f3}  (translating depth plane)"
        )
        ax_mt.text(box_x, box_y, factor_text,
                   fontsize=9, va="top", ha="center",
                   color=f3_col,
                   bbox=dict(boxstyle="round,pad=0.4", fc="white",
                             ec=f3_col, lw=1.5, alpha=0.95),
                   fontfamily="monospace")

        # Vertical line marking pre-onset region right edge
        ax_mt.axvline(ONSET, ls=":", color="gray", lw=0.8)

        scatter_subfields(ax_depth, depth)
        ax_depth.set_xlabel("frame", fontsize=9)
        ax_depth.set_ylabel("depth plane", fontsize=9)
        ax_depth.set_yticks([1, 2])
        ax_depth.set_yticklabels(["Near", "Far"], fontsize=8)
        ax_depth.set_ylim(0.5, 2.5)
        add_phase_markers(ax_depth)

    plt.savefig(out, dpi=200, bbox_inches="tight")
    plt.close()
    print(f"Wrote: {out}")


if __name__ == "__main__":
    main()
