#!/usr/bin/env python3
"""
Combined figure: hypothetical trajectories + session performance.
Layout: 3 rows (N / ZdA / ZdB), each row has:
  [CUED traj (mt+depth)] | [UNCUED traj (mt+depth)] | [accuracy bars]
"""

import sys, csv, math
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.lines import Line2D
from scipy import stats as scipy_stats

# ── trajectory parameters (must match Exp_DepthSwapCtrl.asset @ 75 Hz) ──────
ONSET   = 56   # delayedOnset_ms=750 → 56f
T_START = 78   # onset + preTranslation_ms(300) → +22f
T_END   = 84   # T_START + translationDuration_ms(80) → +6f
TOTAL   = 114  # T_END + 400ms post → +30f

CW, LINEAR, NONCOH, CCW = 1, 2, 3, 4
NEAR, FAR = 1, 2
RED = "#CC3333"

SPECS = [
    {"marker": "o", "filled": True,  "s": 22, "lw": 1.0},   # S0
    {"marker": "s", "filled": False, "s": 48, "lw": 1.5},   # S1
    {"marker": "^", "filled": True,  "s": 26, "lw": 1.0},   # S2
    {"marker": "D", "filled": False, "s": 56, "lw": 1.5},   # S3
]

YTICK_LABELS_MT    = ["CW", "Coh", "NonCoh", "CCW"]
YTICK_LABELS_DEPTH = ["Near", "Far"]


def build(swap, cued):
    mt    = np.zeros((TOTAL, 4), dtype=int)
    depth = np.zeros((TOTAL, 4), dtype=int)

    for f in range(TOTAL):
        ao  = f >= ONSET
        as_ = f >= T_START
        tr  = T_START <= f < T_END

        m = [CW, CW, CCW if ao else 0, CCW if ao else 0]
        d = [FAR, FAR, NEAR if ao else 0, NEAR if ao else 0]

        if as_:
            if swap == 'ZdA':
                d = [NEAR, FAR, FAR, NEAR]
                if tr:
                    m = ([CW, NONCOH, LINEAR, CW] if cued
                         else [LINEAR, CCW, CCW, NONCOH])
                else:
                    m = [CW, CCW, CCW, CW]

            elif swap == 'ZdB':
                d = [FAR, NEAR, NEAR, FAR]
                if tr:
                    m = ([CW, NONCOH, LINEAR, CW] if cued
                         else [LINEAR, CCW, CCW, NONCOH])
                else:
                    m = [CW, CCW, CCW, CW]

            else:  # N
                d = [FAR, FAR, NEAR, NEAR]
                if tr:
                    m = ([CW, CW, LINEAR, NONCOH] if cued
                         else [LINEAR, NONCOH, CCW, CCW])
                else:
                    m = [CW, CW, CCW, CCW]

        mt[f]    = m
        depth[f] = d

    return mt, depth


def scatter_subfields(ax, data, zero_color="#E0E0E0"):
    nF, nS = data.shape
    sample = list(range(0, nF, max(1, nF // 25)))
    if sample[-1] != nF - 1:
        sample.append(nF - 1)
    for s in range(nS):
        sp = SPECS[s]
        ax.plot(np.arange(nF), data[:, s], color="#D8D8D8", lw=0.5, zorder=1)
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


def add_traj_legend(ax):
    handles = [
        Line2D([0],[0], marker="o", color="w", markerfacecolor=RED,
               markersize=5, ls="None", label="S0"),
        Line2D([0],[0], marker="s", color="w", markeredgecolor=RED,
               markerfacecolor="none", markersize=6, markeredgewidth=1.5,
               ls="None", label="S1"),
        Line2D([0],[0], marker="^", color="w", markerfacecolor=RED,
               markersize=5, ls="None", label="S2 (delayed)"),
        Line2D([0],[0], marker="D", color="w", markeredgecolor=RED,
               markerfacecolor="none", markersize=6, markeredgewidth=1.5,
               ls="None", label="S3 (delayed)"),
    ]
    ax.legend(handles=handles, loc="upper right", fontsize=6,
              framealpha=0.7, handlelength=1)


# ── performance helpers ───────────────────────────────────────────────────────

def is_correct(r):
    try:
        td = int(round(float(r["TransDeg"]))) % 360
        rd = int(round(float(r["RespDeg"])))  % 360
        return td == rd
    except:
        return False


def acc_stats(subset):
    n = len(subset)
    if n == 0:
        return dict(n=0, c=0, p=float("nan"), lo=float("nan"), hi=float("nan"))
    c = sum(1 for r in subset if is_correct(r))
    p = c / n
    # Wilson score interval
    z = 1.96
    denom = 1 + z**2 / n
    centre = (p + z**2 / (2*n)) / denom
    half   = z * math.sqrt(p*(1-p)/n + z**2/(4*n**2)) / denom
    return dict(n=n, c=c, p=p, lo=max(0, centre-half), hi=min(1, centre+half))


def chi2_p(rows_a, rows_b):
    ca = sum(1 for r in rows_a if is_correct(r))
    cb = sum(1 for r in rows_b if is_correct(r))
    na, nb = len(rows_a), len(rows_b)
    if na == 0 or nb == 0:
        return float("nan")
    table = [[ca, na-ca], [cb, nb-cb]]
    _, p, _, _ = scipy_stats.chi2_contingency(table, correction=False)
    return p


def pstar(p):
    if math.isnan(p):  return ""
    if p < 0.001:      return "***"
    if p < 0.01:       return "**"
    if p < 0.05:       return "*"
    if p < 0.10:       return "†"
    return "n.s."


def draw_perf_bars(ax, rows, swap):
    """Bar chart: CUED/UNCUED × Near/Far for this swap condition."""
    groups = [
        ("CUED\nNear",   "CUED",   "N"),
        ("CUED\nFar",    "CUED",   "F"),
        ("UNCUED\nNear", "UNCUED", "N"),
        ("UNCUED\nFar",  "UNCUED", "F"),
    ]
    colors_bar = ["#CC4444", "#882222", "#4488CC", "#224488"]
    xs = np.arange(len(groups))

    for i, (label, cond, dep) in enumerate(groups):
        sub = [r for r in rows if r["Cond"]==cond and r["DelayedFieldDepth"]==dep]
        st  = acc_stats(sub)
        bar = ax.bar(xs[i], st["p"], color=colors_bar[i], alpha=0.85,
                     width=0.6, zorder=2)
        if not math.isnan(st["p"]):
            ax.errorbar(xs[i], st["p"],
                        yerr=[[st["p"]-st["lo"]], [st["hi"]-st["p"]]],
                        fmt="none", color="black", capsize=3, lw=1, zorder=3)
            ax.text(xs[i], st["hi"] + 0.02, f'{st["p"]:.2f}',
                    ha="center", va="bottom", fontsize=7)

    # Cueing effect annotations (CUED-UNCUED) per depth
    for dep, x_cued, x_uncued in [("N", 0, 2), ("F", 1, 3)]:
        label_dep = "Near" if dep=="N" else "Far"
        c_rows = [r for r in rows if r["Cond"]=="CUED"   and r["DelayedFieldDepth"]==dep]
        u_rows = [r for r in rows if r["Cond"]=="UNCUED"  and r["DelayedFieldDepth"]==dep]
        p = chi2_p(c_rows, u_rows)
        cs = acc_stats(c_rows); us = acc_stats(u_rows)
        if not math.isnan(cs["p"]) and not math.isnan(us["p"]):
            delta = cs["p"] - us["p"]
            y_top = max(cs["hi"], us["hi"]) + 0.08
            ax.plot([x_cued, x_cued, x_uncued, x_uncued],
                    [y_top-0.02, y_top, y_top, y_top-0.02],
                    color="gray", lw=0.8)
            ax.text((x_cued+x_uncued)/2, y_top + 0.01,
                    f'Δ={delta:+.2f} {pstar(p)}',
                    ha="center", va="bottom", fontsize=7)

    ax.axhline(0.125, ls="--", color="gray", lw=0.7, alpha=0.6)  # chance (8AFC)
    ax.set_ylim(0, 1.05)
    ax.set_xticks(xs)
    ax.set_xticklabels([g[0] for g in groups], fontsize=7)
    ax.set_ylabel("accuracy", fontsize=8)
    ax.set_title(f"Performance  (Swap={swap})", fontsize=8)
    ax.yaxis.grid(True, lw=0.4, alpha=0.5)
    ax.set_axisbelow(True)

    # legend
    legend_els = [
        matplotlib.patches.Patch(color="#CC4444", alpha=0.85, label="CUED"),
        matplotlib.patches.Patch(color="#4488CC", alpha=0.85, label="UNCUED"),
    ]
    ax.legend(handles=legend_els, fontsize=7, loc="upper right")


# ── main ─────────────────────────────────────────────────────────────────────

def main():
    tsv_path = sys.argv[1] if len(sys.argv) > 1 else None
    out_path  = sys.argv[2] if len(sys.argv) > 2 else "results_with_traj.png"

    rows = []
    if tsv_path:
        with open(tsv_path) as f:
            reader = csv.DictReader(f, delimiter="\t")
            for r in reader:
                rows.append(r)

    swaps = ["N", "ZdA", "ZdB"]
    swap_labels = {
        "N":   "N — No swap",
        "ZdA": "ZdA — S0↔S2 depth swap\n(cued dot Near→Far)",
        "ZdB": "ZdB — S1↔S3 depth swap\n(cued dot stays Near)",
    }

    fig = plt.figure(figsize=(18, 5.5 * len(swaps)))
    outer = gridspec.GridSpec(len(swaps), 1, hspace=0.55, figure=fig)

    for row_i, swap in enumerate(swaps):
        swap_rows = [r for r in rows if r["SwapType"]==swap]

        # Each row: [CUED traj | UNCUED traj | perf bars]
        inner = gridspec.GridSpecFromSubplotSpec(
            1, 3, subplot_spec=outer[row_i],
            width_ratios=[2, 2, 1.5], wspace=0.35)

        for col_i, (cued_bool, cond_label) in enumerate([(True, "CUED"), (False, "UNCUED")]):
            mt, depth = build(swap, cued_bool)

            traj_gs = gridspec.GridSpecFromSubplotSpec(
                2, 1, subplot_spec=inner[col_i],
                height_ratios=[3, 1.5], hspace=0.08)
            ax_mt    = fig.add_subplot(traj_gs[0])
            ax_depth = fig.add_subplot(traj_gs[1], sharex=ax_mt)

            scatter_subfields(ax_mt, mt)
            scatter_subfields(ax_depth, depth)

            title_str = (f"{swap_labels[swap]}\n{cond_label}"
                         if col_i == 0 else cond_label)
            ax_mt.set_title(title_str, fontsize=8, loc="left")
            ax_mt.set_ylabel("motion", fontsize=7)
            ax_mt.set_yticks([1, 2, 3, 4])
            ax_mt.set_yticklabels(YTICK_LABELS_MT, fontsize=7)
            ax_mt.set_ylim(0.5, 4.5)
            ax_mt.set_xticklabels([])
            add_phase_markers(ax_mt)
            if col_i == 0:
                add_traj_legend(ax_mt)

            ax_depth.set_xlabel("frame", fontsize=7)
            ax_depth.set_ylabel("depth", fontsize=7)
            ax_depth.set_yticks([1, 2])
            ax_depth.set_yticklabels(YTICK_LABELS_DEPTH, fontsize=7)
            ax_depth.set_ylim(0.5, 2.5)
            add_phase_markers(ax_depth)

        # Performance bars
        ax_perf = fig.add_subplot(inner[2])
        draw_perf_bars(ax_perf, swap_rows, swap)

    session_label = tsv_path.split("/")[-1] if tsv_path else "no data"
    fig.suptitle(
        f"DepthSwapCtrl — {session_label}\n"
        f"Trajectories (RotA, DelayedField=Near): hypothetical reference  |  "
        f"Dashed=chance(1/8)  Blue band=translation window",
        fontsize=9, y=1.005)

    plt.savefig(out_path, dpi=180, bbox_inches="tight")
    plt.close()
    print(f"Wrote: {out_path}")


if __name__ == "__main__":
    main()
