#!/usr/bin/env python3
"""
analyze_depth_combined.py  —  Pool DepthBaseline sessions and run a
2×2 (Cond × DepthPlane) accuracy analysis with interaction statistics.

Usage:
    python3 analyze_depth_combined.py session1.tsv session2.tsv [...]

Outputs  (written alongside the first TSV):
    <prefix>_depth_combined_plots.png
    <prefix>_depth_combined_stats.txt
"""

import sys, os, math
from collections import defaultdict

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

# Normal CDF via math.erf (no scipy required)
def norm_cdf(x):
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))

CHANCE = 1 / 8          # 8-AFC direction judgement
ALPHA  = 0.05

# ── helpers ──────────────────────────────────────────────────────────────────

def read_tsv(path):
    with open(path, "r", encoding="utf-8-sig") as fh:
        lines = [ln.rstrip("\n") for ln in fh]
    hdr = None
    for i, ln in enumerate(lines):
        if ln.strip():
            hdr = ln.split("\t"); hi = i; break
    if hdr is None:
        raise RuntimeError(f"No header in {path}")
    rows = []
    for ln in lines[hi + 1:]:
        if not ln.strip(): continue
        parts = ln.split("\t")
        parts += [""] * max(0, len(hdr) - len(parts))
        rows.append(dict(zip(hdr, parts)))
    return rows

def parse_int(x, default=None):
    try: return int(x)
    except: return default

def parse_float(x, default=None):
    try: return float(x)
    except: return default

def is_correct(row):
    td = parse_float(row.get("TransDeg", "nan"), float("nan"))
    rd = parse_float(row.get("RespDeg",  "nan"), float("nan"))
    if math.isnan(td) or math.isnan(rd): return None
    return (int(round(td)) % 360) == (int(round(rd)) % 360)

def responded(row):
    return (parse_int(row.get("RespIndex", "-1"), -1) >= 0 and
            parse_float(row.get("RespDeg",  "-1"), -1.0) >= 0)

# ── binomial statistics ───────────────────────────────────────────────────────

def wilson_ci(k, n, z=1.96):
    """Wilson score 95 % confidence interval for proportion k/n."""
    if n == 0: return (float("nan"), float("nan"))
    p = k / n
    denom = 1 + z**2 / n
    centre = (p + z**2 / (2*n)) / denom
    half   = z * math.sqrt(p*(1-p)/n + z**2/(4*n**2)) / denom
    return (max(0, centre - half), min(1, centre + half))

def prop_z_test(k1, n1, k2, n2):
    """
    Two-sided z-test for H0: p1 == p2.
    Returns (z_stat, p_value).
    """
    if n1 == 0 or n2 == 0: return (float("nan"), float("nan"))
    p1 = k1 / n1; p2 = k2 / n2
    p_pool = (k1 + k2) / (n1 + n2)
    se = math.sqrt(p_pool * (1 - p_pool) * (1/n1 + 1/n2))
    if se == 0: return (float("nan"), float("nan"))
    z = (p1 - p2) / se
    pval = 2 * (1 - norm_cdf(abs(z)))
    return z, pval

def interaction_z_test(cells):
    """
    cells = {
        ('CUED',   'N'): (k, n),
        ('CUED',   'F'): (k, n),
        ('UNCUED', 'N'): (k, n),
        ('UNCUED', 'F'): (k, n),
    }
    Test the Cond × Depth interaction:
        delta_F = p(CUED,F) - p(UNCUED,F)
        delta_N = p(CUED,N) - p(UNCUED,N)
        interaction = delta_F - delta_N
    SE of interaction  = sqrt(SE(C,F)^2 + SE(U,F)^2 + SE(C,N)^2 + SE(U,N)^2)
    where  SE(c,d) = sqrt(p(c,d)*(1-p(c,d))/n(c,d))
    """
    def se(k, n):
        if n == 0: return float("nan")
        p = k / n
        return math.sqrt(p * (1 - p) / n)

    kCF, nCF = cells[("CUED",   "F")]
    kUF, nUF = cells[("UNCUED", "F")]
    kCN, nCN = cells[("CUED",   "N")]
    kUN, nUN = cells[("UNCUED", "N")]

    pCF = kCF/nCF if nCF else float("nan")
    pUF = kUF/nUF if nUF else float("nan")
    pCN = kCN/nCN if nCN else float("nan")
    pUN = kUN/nUN if nUN else float("nan")

    delta_F = pCF - pUF
    delta_N = pCN - pUN
    interaction = delta_F - delta_N

    se_int = math.sqrt(se(kCF,nCF)**2 + se(kUF,nUF)**2 +
                       se(kCN,nCN)**2 + se(kUN,nUN)**2)
    if se_int == 0: return interaction, float("nan"), float("nan")
    z = interaction / se_int
    pval = 2 * (1 - norm_cdf(abs(z)))
    return interaction, z, pval

# ── main ─────────────────────────────────────────────────────────────────────

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 analyze_depth_combined.py s1.tsv [s2.tsv ...]")
        sys.exit(1)

    tsv_paths = sys.argv[1:]
    session_labels = [os.path.basename(p).replace(".tsv","") for p in tsv_paths]

    # ── load & pool ──────────────────────────────────────────────────────────
    all_rows = []           # (session_label, row)
    session_rows = {}       # label -> [row, ...]

    for label, path in zip(session_labels, tsv_paths):
        rows = read_tsv(path)
        seen = set()
        deduped = []
        for r in rows:
            ti = parse_int(r.get("Trial","-1"), -999)
            if ti in seen: continue
            seen.add(ti)
            if responded(r):
                r["_correct"] = is_correct(r)
                r["_session"] = label
                deduped.append(r)
        session_rows[label] = deduped
        all_rows.extend(deduped)

    n_sessions = len(session_labels)

    # ── helper: build 2×2 cell counts  cond × depth ──────────────────────────
    def cell_counts(rows):
        """Returns {(cond, depth): (n_correct, n_total)}"""
        cells = defaultdict(lambda: [0, 0])
        for r in rows:
            cond  = r.get("Cond", "")
            depth = r.get("DelayedFieldDepth", "")
            if cond not in ("CUED","UNCUED") or depth not in ("N","F"):
                continue
            cells[(cond, depth)][1] += 1
            if r["_correct"]: cells[(cond, depth)][0] += 1
        return {k: tuple(v) for k, v in cells.items()}

    def cell_acc(cells, cond, depth):
        k, n = cells.get((cond, depth), (0, 0))
        return k/n if n else float("nan")

    pooled_cells     = cell_counts(all_rows)
    per_sess_cells   = {lb: cell_counts(session_rows[lb]) for lb in session_labels}

    # ── statistics (pooled) ──────────────────────────────────────────────────
    # Main effect of Cond
    kC  = sum(k for (c,d),(k,n) in pooled_cells.items() if c == "CUED")
    nC  = sum(n for (c,d),(k,n) in pooled_cells.items() if c == "CUED")
    kU  = sum(k for (c,d),(k,n) in pooled_cells.items() if c == "UNCUED")
    nU  = sum(n for (c,d),(k,n) in pooled_cells.items() if c == "UNCUED")
    z_cond, p_cond = prop_z_test(kC, nC, kU, nU)

    # Main effect of Depth
    kN  = sum(k for (c,d),(k,n) in pooled_cells.items() if d == "N")
    nN  = sum(n for (c,d),(k,n) in pooled_cells.items() if d == "N")
    kF  = sum(k for (c,d),(k,n) in pooled_cells.items() if d == "F")
    nF  = sum(n for (c,d),(k,n) in pooled_cells.items() if d == "F")
    z_depth, p_depth = prop_z_test(kF, nF, kN, nN)   # Far vs Near

    # Interaction
    interaction, z_int, p_int = interaction_z_test(pooled_cells)

    # Simple effects (within each depth level)
    z_cue_N, p_cue_N = prop_z_test(*pooled_cells.get(("CUED","N"),(0,0)),
                                    *pooled_cells.get(("UNCUED","N"),(0,0)))
    z_cue_F, p_cue_F = prop_z_test(*pooled_cells.get(("CUED","F"),(0,0)),
                                    *pooled_cells.get(("UNCUED","F"),(0,0)))

    # ── build results text ───────────────────────────────────────────────────
    def stars(p):
        if math.isnan(p): return ""
        if p < .001: return "***"
        if p < .01:  return "**"
        if p < .05:  return "*"
        return "n.s."

    lines = []
    lines.append("=" * 60)
    lines.append("COMBINED DEPTH ANALYSIS")
    lines.append("Sessions: " + ", ".join(session_labels))
    lines.append(f"Total responded trials pooled: {len(all_rows)}")
    lines.append("=" * 60)
    lines.append("")
    lines.append("── 2×2 Cell Accuracy (Cond × DelayedFieldDepth) ──")
    lines.append(f"                  Near (N)    Far (F)")
    for cond in ["CUED","UNCUED"]:
        accs = [cell_acc(pooled_cells, cond, d) for d in ("N","F")]
        ns   = [pooled_cells.get((cond,d),(0,0))[1] for d in ("N","F")]
        lines.append(f"  {cond:8s}       {accs[0]:.3f} (n={ns[0]})   {accs[1]:.3f} (n={ns[1]})")
    lines.append("")
    lines.append("── Cueing Effect (CUED − UNCUED) by Depth ──")
    dN = cell_acc(pooled_cells,"CUED","N") - cell_acc(pooled_cells,"UNCUED","N")
    dF = cell_acc(pooled_cells,"CUED","F") - cell_acc(pooled_cells,"UNCUED","F")
    lines.append(f"  Near:  {dN*100:+.1f} pp   z={z_cue_N:.2f}  p={p_cue_N:.4f} {stars(p_cue_N)}")
    lines.append(f"  Far:   {dF*100:+.1f} pp   z={z_cue_F:.2f}  p={p_cue_F:.4f} {stars(p_cue_F)}")
    lines.append("")
    lines.append("── Main Effects & Interaction (z-tests on proportions) ──")
    pC = kC/nC if nC else float("nan"); pU = kU/nU if nU else float("nan")
    pN_acc = kN/nN if nN else float("nan"); pF_acc = kF/nF if nF else float("nan")
    lines.append(f"  Main effect Cond:   CUED={pC:.3f}  UNCUED={pU:.3f}")
    lines.append(f"                      z={z_cond:.2f}  p={p_cond:.4f} {stars(p_cond)}")
    lines.append(f"  Main effect Depth:  Near={pN_acc:.3f}  Far={pF_acc:.3f}")
    lines.append(f"                      z={z_depth:.2f}  p={p_depth:.4f} {stars(p_depth)}")
    lines.append(f"  Cond × Depth interaction:")
    lines.append(f"    delta_Far − delta_Near = {interaction*100:+.1f} pp")
    lines.append(f"                      z={z_int:.2f}  p={p_int:.4f} {stars(p_int)}")
    lines.append("")
    lines.append("── Per-Session Cueing Effects ──")
    for lb in session_labels:
        sc = per_sess_cells[lb]
        dNs = cell_acc(sc,"CUED","N") - cell_acc(sc,"UNCUED","N")
        dFs = cell_acc(sc,"CUED","F") - cell_acc(sc,"UNCUED","F")
        overall = (sum(k for (c,d),(k,n) in sc.items() if c=="CUED") /
                   max(1, sum(n for (c,d),(k,n) in sc.items() if c=="CUED")) -
                   sum(k for (c,d),(k,n) in sc.items() if c=="UNCUED") /
                   max(1, sum(n for (c,d),(k,n) in sc.items() if c=="UNCUED")))
        lines.append(f"  {lb}:")
        lines.append(f"    Near: {dNs*100:+.1f} pp   Far: {dFs*100:+.1f} pp   Overall: {overall*100:+.1f} pp")
    lines.append("")
    lines.append("Note: z-tests assume independent binary observations.")
    lines.append("  Interaction z = (delta_Far − delta_Near) / pooled SE")
    lines.append(f"  Chance = {CHANCE:.3f} ({int(1/CHANCE)}-AFC)")

    stats_text = "\n".join(lines)
    print(stats_text)

    # ── plots ────────────────────────────────────────────────────────────────
    BLUE   = "#3A7ABF"
    ORANGE = "#E07B30"
    DEPTH_LABELS = {"N": "Near", "F": "Far"}
    COND_COLORS  = {"CUED": BLUE, "UNCUED": ORANGE}

    n_rows_plot = 1 + n_sessions   # pooled + one per session
    fig = plt.figure(figsize=(13, 4.5 * n_rows_plot))
    outer = gridspec.GridSpec(n_rows_plot, 1, hspace=0.55,
                               top=0.95, bottom=0.06, left=0.08, right=0.97)

    def plot_2x2_row(gs_row, cells, title_prefix):
        """Draw two side-by-side axes: 2×2 accuracy bars | cueing-effect bars."""
        inner = gridspec.GridSpecFromSubplotSpec(1, 2, subplot_spec=gs_row,
                                                  width_ratios=[3, 2], wspace=0.35)
        ax1 = fig.add_subplot(inner[0])
        ax2 = fig.add_subplot(inner[1])

        # ---- left: 2×2 accuracy ----
        depths = ["N", "F"]
        x = np.arange(len(depths))
        w = 0.33
        for ci, cond in enumerate(["CUED", "UNCUED"]):
            accs, lo_errs, hi_errs = [], [], []
            for d in depths:
                k, n = cells.get((cond, d), (0, 0))
                p = k / n if n else float("nan")
                lo, hi = wilson_ci(k, n)
                accs.append(p)
                lo_errs.append(p - lo)
                hi_errs.append(hi - p)
            offset = (ci - 0.5) * w
            bars = ax1.bar(x + offset, accs, width=w, color=COND_COLORS[cond],
                           alpha=0.85, label=cond, zorder=3)
            ax1.errorbar(x + offset, accs,
                         yerr=[lo_errs, hi_errs],
                         fmt="none", color="black", capsize=3, linewidth=1.2, zorder=4)

        ax1.axhline(CHANCE, color="gray", linestyle="--", linewidth=0.8, label=f"Chance ({CHANCE:.2f})")
        ax1.set_xticks(x)
        ax1.set_xticklabels([f"Delayed\n{DEPTH_LABELS[d]} plane" for d in depths])
        ax1.set_ylim(0, 1)
        ax1.set_ylabel("Proportion correct")
        ax1.set_title(f"{title_prefix} — Accuracy by Cond × Depth", fontsize=10, fontweight="bold")
        ax1.legend(fontsize=8, loc="upper right")
        ax1.set_axisbelow(True)
        ax1.yaxis.grid(True, alpha=0.4)

        # annotate n
        for ci, cond in enumerate(["CUED","UNCUED"]):
            for di, d in enumerate(depths):
                k, n = cells.get((cond,d),(0,0))
                offset = (ci - 0.5) * w
                ax1.text(di + offset, 0.02, f"n={n}", ha="center", va="bottom",
                         fontsize=7, color="white", fontweight="bold")

        # ---- right: cueing effects ----
        delta_N = cell_acc(cells,"CUED","N") - cell_acc(cells,"UNCUED","N")
        delta_F = cell_acc(cells,"CUED","F") - cell_acc(cells,"UNCUED","F")
        deltas  = [delta_N, delta_F]

        # SE of difference of proportions
        def se_diff(cells, d):
            kC, nC = cells.get(("CUED",   d),(0,0))
            kU, nU = cells.get(("UNCUED", d),(0,0))
            pC = kC/nC if nC else 0; pU = kU/nU if nU else 0
            return math.sqrt(pC*(1-pC)/max(1,nC) + pU*(1-pU)/max(1,nU))

        se_N = se_diff(cells,"N"); se_F = se_diff(cells,"F")
        ses  = [se_N, se_F]

        colors = []
        for d in deltas:
            colors.append("#2C7BB6" if d >= 0 else "#D7191C")

        bars2 = ax2.bar([0, 1], [d*100 for d in deltas], width=0.5,
                        color=colors, alpha=0.85, zorder=3)
        ax2.errorbar([0, 1], [d*100 for d in deltas],
                     yerr=[s*1.96*100 for s in ses],
                     fmt="none", color="black", capsize=4, linewidth=1.2, zorder=4)
        ax2.axhline(0, color="black", linewidth=0.8)
        ax2.set_xticks([0, 1])
        ax2.set_xticklabels([f"Delayed\n{DEPTH_LABELS[d]}" for d in ("N","F")])
        ax2.set_ylabel("Cueing effect (pp)")
        ax2.set_title(f"{title_prefix} — Cueing Effect", fontsize=10, fontweight="bold")
        ax2.set_axisbelow(True)
        ax2.yaxis.grid(True, alpha=0.4)
        yabs = max(abs(d*100) for d in deltas if not math.isnan(d)) * 1.4 + 5
        ax2.set_ylim(-yabs, yabs)

        # value labels
        for xi, (d, s) in enumerate(zip(deltas, ses)):
            if not math.isnan(d):
                ax2.text(xi, d*100 + (4 if d >= 0 else -4),
                         f"{d*100:+.1f}pp", ha="center",
                         va="bottom" if d >= 0 else "top", fontsize=9, fontweight="bold")

    # Row 0: pooled
    plot_2x2_row(outer[0], pooled_cells,
                 f"Pooled ({n_sessions} sessions, N={len(all_rows)} responded trials)")

    # Annotate interaction stats on pooled row
    ax_stat = fig.add_axes([0.58, 0.88 - 0.0 * (1/n_rows_plot), 0.38, 0.04])
    ax_stat.axis("off")
    inter_str = (f"Interaction z = {z_int:.2f},  p = {p_int:.4f} {stars(p_int)}  |  "
                 f"Cue main: p = {p_cond:.4f} {stars(p_cond)}  |  "
                 f"Depth main: p = {p_depth:.4f} {stars(p_depth)}")
    ax_stat.text(0.5, 0.5, inter_str, ha="center", va="center",
                 fontsize=8, fontstyle="italic",
                 transform=ax_stat.transAxes)

    # Rows 1…n: per session
    for i, lb in enumerate(session_labels):
        n_s = len(session_rows[lb])
        plot_2x2_row(outer[i+1], per_sess_cells[lb], f"{lb}  (N={n_s} responded)")

    # ── save ────────────────────────────────────────────────────────────────
    out_dir  = os.path.dirname(os.path.abspath(tsv_paths[0]))
    prefix   = "depth_combined_" + "_".join(lb.replace("vr_dots_session_","") for lb in session_labels)
    plot_out = os.path.join(out_dir, prefix + "_plots.png")
    stat_out = os.path.join(out_dir, prefix + "_stats.txt")

    fig.savefig(plot_out, dpi=180)
    plt.close(fig)
    with open(stat_out, "w") as fh:
        fh.write(stats_text + "\n")

    print(f"\nWrote:\n  {plot_out}\n  {stat_out}")

if __name__ == "__main__":
    main()
