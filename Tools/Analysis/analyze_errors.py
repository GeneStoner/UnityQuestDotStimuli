#!/usr/bin/env python3
"""
analyze_errors.py  —  Direction-error analysis for VRDots sessions.

Computes the distribution of angular response errors (0°, ±45°, ±90°, ±135°, 180°)
broken down by Cond × DelayedFieldDepth, and tests for systematic biases.

Usage:
    python3 analyze_errors.py [--label LABEL] session1.tsv [session2.tsv ...]

Options:
    --label LABEL   Short label for output filenames (default: derived from TSV names)

Outputs (written alongside the first TSV):
    <label>_error_plots.png
    <label>_error_stats.txt
"""

import sys, os, math
from collections import defaultdict

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

# ── constants ────────────────────────────────────────────────────────────────

N_DIRS   = 8
CHANCE_CORRECT   = 1 / N_DIRS           # 0.125
# Under a uniform random response model, expected proportion at each offset:
# 0° → 1/8,  45° → 2/8 (±),  90° → 2/8,  135° → 2/8,  180° → 1/8
CHANCE_BY_OFFSET = {0: 1/8, 45: 2/8, 90: 2/8, 135: 2/8, 180: 1/8}
OFFSETS = [0, 45, 90, 135, 180]
OFFSET_LABELS = ["0°\n(correct)", "±45°", "±90°", "±135°", "180°\n(opposite)"]

CONDS  = ["CUED", "UNCUED"]
DEPTHS = ["N", "F"]
DEPTH_NAMES = {"N": "Near", "F": "Far"}

BLUE   = "#3A7ABF"
ORANGE = "#E07B30"
COND_COLORS = {"CUED": BLUE, "UNCUED": ORANGE}
CHANCE_COLOR = "#888888"

# ── helpers ───────────────────────────────────────────────────────────────────

def read_tsv(path):
    with open(path, "r", encoding="utf-8-sig") as fh:
        lines = [ln.rstrip("\n") for ln in fh]
    for i, ln in enumerate(lines):
        if ln.strip():
            hdr = ln.split("\t"); hi = i; break
    rows = []
    for ln in lines[hi + 1:]:
        if not ln.strip(): continue
        parts = ln.split("\t")
        parts += [""] * max(0, len(hdr) - len(parts))
        rows.append(dict(zip(hdr, parts)))
    return rows

def parse_float(x, default=None):
    try: return float(x)
    except: return default

def parse_int(x, default=None):
    try: return int(x)
    except: return default

def angular_offset(trans_deg, resp_deg):
    """Minimum absolute angular distance between two directions (0–180°),
    rounded to nearest 45° to absorb float noise."""
    raw = abs((resp_deg - trans_deg + 360) % 360)
    if raw > 180: raw = 360 - raw
    return int(round(raw / 45.0)) * 45

def norm_cdf(x):
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))

def prop_z(k, n, p0):
    """One-sample z-test: is observed proportion k/n different from p0?"""
    if n == 0: return float("nan"), float("nan")
    p = k / n
    se = math.sqrt(p0 * (1 - p0) / n)
    if se == 0: return float("nan"), float("nan")
    z = (p - p0) / se
    pval = 2 * (1 - norm_cdf(abs(z)))
    return z, pval

def prop_z2(k1, n1, k2, n2):
    """Two-sample z-test: p1 vs p2."""
    if n1 == 0 or n2 == 0: return float("nan"), float("nan")
    p1 = k1/n1; p2 = k2/n2
    pp = (k1+k2)/(n1+n2)
    se = math.sqrt(pp*(1-pp)*(1/n1+1/n2))
    if se == 0: return float("nan"), float("nan")
    z = (p1-p2)/se
    return z, 2*(1-norm_cdf(abs(z)))

def stars(p):
    if p is None or (isinstance(p, float) and math.isnan(p)): return ""
    if p < .001: return "***"
    if p < .01:  return "**"
    if p < .05:  return "*"
    return "n.s."

def wilson_ci(k, n, z=1.96):
    if n == 0: return (float("nan"), float("nan"))
    p = k/n
    d = 1 + z**2/n
    c = (p + z**2/(2*n))/d
    h = z*math.sqrt(p*(1-p)/n + z**2/(4*n**2))/d
    return (max(0, c-h), min(1, c+h))

# ── data loading ──────────────────────────────────────────────────────────────

def load_sessions(tsv_paths):
    """Returns list of (label, row) for all responded trials."""
    all_rows = []
    for path in tsv_paths:
        raw = read_tsv(path)
        seen = set()
        for r in raw:
            ti = parse_int(r.get("Trial","-1"), -999)
            if ti in seen: continue
            seen.add(ti)
            td = parse_float(r.get("TransDeg",""), None)
            rd = parse_float(r.get("RespDeg",""), None)
            ri = parse_int(r.get("RespIndex",""), -1)
            if td is None or rd is None or ri is None or ri < 0: continue
            r["_td"] = td
            r["_rd"] = rd
            r["_offset"] = angular_offset(td, rd)
            r["_session"] = os.path.basename(path).replace(".tsv","")
            all_rows.append(r)
    return all_rows

# ── aggregation ───────────────────────────────────────────────────────────────

def build_cell_distribution(rows):
    """
    Returns dict: (cond, depth) -> {offset: count}
    Also returns marginals: (cond,) and (depth,) -> {offset: count}
    """
    cells = defaultdict(lambda: defaultdict(int))
    for r in rows:
        cond  = r.get("Cond","")
        depth = r.get("DelayedFieldDepth","")
        off   = r.get("_offset", None)
        if cond not in CONDS or depth not in DEPTHS or off is None: continue
        cells[(cond, depth)][off] += 1
    return cells

def cell_n(dist):
    return sum(dist.values())

def cell_prop(dist, offset):
    n = cell_n(dist)
    if n == 0: return float("nan")
    return dist.get(offset, 0) / n

# ── stats text ────────────────────────────────────────────────────────────────

def make_stats_text(label, rows, cells):
    n_total = len(rows)
    lines = []
    lines.append("=" * 65)
    lines.append(f"ERROR ANALYSIS — {label}")
    lines.append(f"Responded trials: {n_total}")
    lines.append("=" * 65)

    # ── Table 1: error distributions per cell ──
    lines.append("")
    lines.append("── Response offset distribution by Cond × DelayedDepth ──")
    hdr = f"{'Cell':20s}  {'n':>5}  " + "  ".join(f"{lb:>8}" for lb in ["0°","±45°","±90°","±135°","180°"])
    lines.append(hdr)
    lines.append("-" * len(hdr))
    for cond in CONDS:
        for depth in DEPTHS:
            d = cells.get((cond, depth), {})
            n = cell_n(d)
            if n == 0: continue
            props = [d.get(o,0)/n for o in OFFSETS]
            counts = [d.get(o,0) for o in OFFSETS]
            tag = f"{cond} Delayed={DEPTH_NAMES[depth]}"
            row_str = f"{tag:20s}  {n:>5}  " + "  ".join(f"{p*100:>6.1f}% ({c})" for p,c in zip(props,counts))
            lines.append(row_str)
    lines.append("")
    lines.append(f"{'Chance':20s}  {'':>5}  " +
                 "  ".join(f"{CHANCE_BY_OFFSET[o]*100:>8.1f}%" for o in OFFSETS))

    # ── Table 2: key tests on 45° and 180° errors ──
    lines.append("")
    lines.append("── Tests vs. chance for 45° and 180° errors ──")
    lines.append("(one-sample z: observed proportion vs. uniform-random expectation)")
    lines.append("")
    for off, chance_p in [(45, 2/8), (180, 1/8)]:
        lines.append(f"  Offset = {off}° (chance = {chance_p*100:.1f}%):")
        for cond in CONDS:
            for depth in DEPTHS:
                d = cells.get((cond, depth), {})
                n = cell_n(d)
                if n == 0: continue
                k = d.get(off, 0)
                p_obs = k/n
                z, pval = prop_z(k, n, chance_p)
                tag = f"{cond} {DEPTH_NAMES[depth]}"
                lines.append(f"    {tag:18s}: {p_obs*100:.1f}% ({k}/{n})  "
                              f"z={z:.2f}  p={pval:.4f} {stars(pval)}")
        lines.append("")

    # ── Table 3: 180° cross-condition comparisons ──
    lines.append("── 180° error rate: cross-condition comparisons ──")
    for depth in DEPTHS:
        dC = cells.get(("CUED",   depth), {})
        dU = cells.get(("UNCUED", depth), {})
        kC, nC = dC.get(180,0), cell_n(dC)
        kU, nU = dU.get(180,0), cell_n(dU)
        if nC == 0 or nU == 0: continue
        z, pval = prop_z2(kC, nC, kU, nU)
        lines.append(f"  {DEPTH_NAMES[depth]:4s}:  CUED={kC/nC*100:.1f}%  UNCUED={kU/nU*100:.1f}%  "
                     f"z={z:.2f}  p={pval:.4f} {stars(pval)}")
    lines.append("")
    for cond in CONDS:
        dN = cells.get((cond, "N"), {})
        dF = cells.get((cond, "F"), {})
        kN, nN = dN.get(180,0), cell_n(dN)
        kF, nF = dF.get(180,0), cell_n(dF)
        if nN == 0 or nF == 0: continue
        z, pval = prop_z2(kN, nN, kF, nF)
        lines.append(f"  {cond:6s}: Near={kN/nN*100:.1f}%  Far={kF/nF*100:.1f}%  "
                     f"z={z:.2f}  p={pval:.4f} {stars(pval)}")

    # ── Table 4: signed error breakdown (CW vs CCW bias?) ──
    lines.append("")
    lines.append("── Signed 45° errors: CW (+45°) vs CCW (−45°) ──")
    lines.append("(asymmetry would indicate a systematic directional bias)")
    for cond in CONDS:
        for depth in DEPTHS:
            d = cells.get((cond, depth), {})
            n = cell_n(d)
            if n == 0: continue
            k_cw = d.get("cw45", 0)
            k_ccw = d.get("ccw45", 0)
            if k_cw + k_ccw == 0: continue
            lines.append(f"  {cond} {DEPTH_NAMES[depth]}: +45°={k_cw}  −45°={k_ccw}")

    return "\n".join(lines)

# ── plotting ──────────────────────────────────────────────────────────────────

def plot_dataset(fig, outer_gs, row_idx, label, rows, cells):
    """
    Draw one row of plots for a dataset:
      Left block:  4 subplots (one per Cond×Depth), error distribution bars
      Right block: 2 subplots (one per Depth), comparing CUED vs UNCUED 180° rate
    """
    inner = gridspec.GridSpecFromSubplotSpec(
        2, 3, subplot_spec=outer_gs[row_idx],
        width_ratios=[1, 1, 0.8], wspace=0.38, hspace=0.55
    )

    x = np.arange(len(OFFSETS))
    w = 0.32
    chance_props = [CHANCE_BY_OFFSET[o] for o in OFFSETS]

    for di, depth in enumerate(DEPTHS):
        for ci, cond in enumerate(CONDS):
            ax = fig.add_subplot(inner[ci, di])
            d = cells.get((cond, depth), {})
            n = cell_n(d)
            props = [d.get(o, 0)/n if n else 0 for o in OFFSETS]
            ci95_lo = [max(0, props[i] - wilson_ci(d.get(OFFSETS[i],0), n)[0]) for i in range(len(OFFSETS))]
            ci95_hi = [max(0, wilson_ci(d.get(OFFSETS[i],0), n)[1] - props[i]) for i in range(len(OFFSETS))]

            ax.bar(x, [p*100 for p in props], width=0.6,
                   color=COND_COLORS[cond], alpha=0.82, zorder=3)
            ax.errorbar(x, [p*100 for p in props],
                        yerr=[[e*100 for e in ci95_lo], [e*100 for e in ci95_hi]],
                        fmt="none", color="black", capsize=3, linewidth=1.0, zorder=4)

            # chance line per bar
            for xi, cp in enumerate(chance_props):
                ax.plot([xi-0.35, xi+0.35], [cp*100, cp*100],
                        color=CHANCE_COLOR, linewidth=1.2, linestyle="--", zorder=5)

            ax.set_xticks(x)
            ax.set_xticklabels(OFFSET_LABELS, fontsize=7)
            ax.set_ylim(0, max(70, max(p*100 for p in props)*1.25 + 5))
            ax.set_ylabel("% responses", fontsize=8)
            ax.set_title(f"{cond} | Delayed {DEPTH_NAMES[depth]}\n(n={n})",
                         fontsize=8.5, fontweight="bold")
            ax.set_axisbelow(True)
            ax.yaxis.grid(True, alpha=0.3)

            # annotate counts above bars
            for xi, (p, o) in enumerate(zip(props, OFFSETS)):
                c_count = d.get(o, 0)
                if c_count > 0:
                    ax.text(xi, p*100 + 1.0, str(c_count),
                            ha="center", va="bottom", fontsize=7, color="#333333")

    # Right column: 180° comparison across conditions, one row per depth
    for di, depth in enumerate(DEPTHS):
        ax = fig.add_subplot(inner[di, 2])
        dC = cells.get(("CUED",   depth), {})
        dU = cells.get(("UNCUED", depth), {})
        nC = cell_n(dC); nU = cell_n(dU)
        p180C = dC.get(180,0)/nC if nC else 0
        p180U = dU.get(180,0)/nU if nU else 0

        bars = ax.bar([0, 1], [p180C*100, p180U*100], width=0.5,
                      color=[BLUE, ORANGE], alpha=0.85, zorder=3)
        # CI
        for xi, (k, n) in enumerate([(dC.get(180,0),nC),(dU.get(180,0),nU)]):
            lo, hi = wilson_ci(k, n)
            p = k/n if n else 0
            ax.errorbar(xi, p*100, yerr=[[max(0,p-lo)*100],[max(0,hi-p)*100]],
                        fmt="none", color="black", capsize=4, linewidth=1.2, zorder=4)

        ax.axhline(CHANCE_BY_OFFSET[180]*100, color=CHANCE_COLOR,
                   linestyle="--", linewidth=1.2, label=f"Chance ({CHANCE_BY_OFFSET[180]*100:.0f}%)")
        ax.set_xticks([0,1]); ax.set_xticklabels(["CUED","UNCUED"], fontsize=8)
        ax.set_ylabel("% 180° errors", fontsize=8)
        ax.set_ylim(0, max(30, p180C*100*1.4+5, p180U*100*1.4+5))
        ax.set_title(f"180° errors\nDelayed {DEPTH_NAMES[depth]}", fontsize=8.5, fontweight="bold")
        ax.set_axisbelow(True); ax.yaxis.grid(True, alpha=0.3)

        # significance annotation
        z, pval = prop_z2(dC.get(180,0), nC, dU.get(180,0), nU)
        if not math.isnan(pval):
            s = stars(pval)
            ymax = max(p180C, p180U)*100 + 4
            ax.plot([0,1],[ymax,ymax], color="black", linewidth=0.8)
            ax.text(0.5, ymax+0.5, s, ha="center", fontsize=9)

    # Row title
    title_ax = fig.add_subplot(outer_gs[row_idx])
    title_ax.set_axis_off()
    title_ax.text(0.5, 1.02, label, ha="center", va="bottom",
                  fontsize=11, fontweight="bold", transform=title_ax.transAxes)

# ── main ──────────────────────────────────────────────────────────────────────

def main():
    args = sys.argv[1:]
    label = None
    tsv_paths = []
    i = 0
    while i < len(args):
        if args[i] == "--label" and i+1 < len(args):
            label = args[i+1]; i += 2
        else:
            tsv_paths.append(args[i]); i += 1

    if not tsv_paths:
        print(__doc__)
        sys.exit(1)

    if label is None:
        names = [os.path.basename(p).replace("vr_dots_session_","").replace(".tsv","")
                 for p in tsv_paths]
        label = "error_" + "_".join(names)

    # Load pooled
    all_rows = load_sessions(tsv_paths)

    # Build signed 45° breakdown too (for stats text)
    for r in all_rows:
        td = r["_td"]; rd = r["_rd"]
        signed = (rd - td + 360) % 360
        if abs(round(signed/45)*45 - 45) < 5:
            r["_signed45"] = "cw45"
        elif abs(round(signed/45)*45 - 315) < 5:
            r["_signed45"] = "ccw45"
        else:
            r["_signed45"] = None

    cells_pooled = build_cell_distribution(all_rows)

    # Inject signed 45° into cell dicts
    for r in all_rows:
        cond = r.get("Cond",""); depth = r.get("DelayedFieldDepth","")
        s45 = r.get("_signed45")
        if cond in CONDS and depth in DEPTHS and s45:
            cells_pooled[(cond,depth)][s45] = cells_pooled[(cond,depth)].get(s45,0) + 1

    # Per-session distributions
    sessions = sorted(set(r["_session"] for r in all_rows))
    per_sess = {}
    for s in sessions:
        sr = [r for r in all_rows if r["_session"] == s]
        per_sess[s] = build_cell_distribution(sr)

    # ── Stats text ──
    pool_label = label + f" (pooled {len(tsv_paths)} sessions, N={len(all_rows)})"
    stats_text = make_stats_text(pool_label, all_rows, cells_pooled)

    # Per-session stats appended
    if len(sessions) > 1:
        for s in sessions:
            sr = [r for r in all_rows if r["_session"] == s]
            stats_text += "\n\n" + make_stats_text(s, sr, per_sess[s])

    print(stats_text)

    # ── Figure ──
    n_plot_rows = 1 + (len(sessions) if len(sessions) > 1 else 0)
    fig = plt.figure(figsize=(14, 5.8 * n_plot_rows))
    outer = gridspec.GridSpec(n_plot_rows, 1, hspace=0.55,
                               top=0.95, bottom=0.04, left=0.07, right=0.97)

    plot_dataset(fig, outer, 0, pool_label, all_rows, cells_pooled)

    if len(sessions) > 1:
        for si, s in enumerate(sessions):
            sr = [r for r in all_rows if r["_session"] == s]
            plot_dataset(fig, outer, si+1, s, sr, per_sess[s])

    # ── Save ──
    out_dir  = os.path.dirname(os.path.abspath(tsv_paths[0]))
    plot_out = os.path.join(out_dir, label + "_plots.png")
    stat_out = os.path.join(out_dir, label + "_stats.txt")

    fig.savefig(plot_out, dpi=180)
    plt.close(fig)
    with open(stat_out, "w") as fh:
        fh.write(stats_text + "\n")

    print(f"\nWrote:\n  {plot_out}\n  {stat_out}")

if __name__ == "__main__":
    main()
