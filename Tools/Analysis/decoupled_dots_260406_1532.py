#!/usr/bin/env python3
"""
decoupled_dots_260406_1532.py — Analysis & figure for Exp_DecoupledDots_005m

Session: 260406_1532  (n=514 trials, 4 SwapTypes: N/C/Z/CZ × CUED/UNCUED)
Design: linkDepthColor=0 — depth and color independently varied
SwapTypes:
  N  = no swap (baseline)
  C  = color-only swap
  Z  = depth-only swap
  CZ = color + depth swap

Output: Agents/Figures/decoupled_dots_260406_1532.png
"""

import csv, collections, math, os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.patches as mpatches
import matplotlib.ticker
from scipy.stats import chi2_contingency

# ── Paths ─────────────────────────────────────────────────────────────────────
DATA_PATH = "/tmp/quest_pull2/files/vr_dots_session_260406_1532.tsv"
OUT_PATH  = os.path.expanduser(
    "~/Projects/ObjectBasedAttention/VRDots/Agents/Figures/decoupled_dots_260406_1532.png")

CHANCE = 1/8

# ── Stats helpers ─────────────────────────────────────────────────────────────
def normal_cdf(x):
    return 0.5 * (1 + math.erf(x / math.sqrt(2)))

def z_test(k1, n1, k2, n2):
    """One-tailed z-test: H1: p1 > p2."""
    p1, p2 = k1/n1, k2/n2
    pp = (k1+k2)/(n1+n2)
    se = math.sqrt(max(pp*(1-pp)*(1/n1+1/n2), 1e-12))
    z = (p1-p2)/se
    return z, 1 - normal_cdf(z)

def z_test_two(k1, n1, k2, n2):
    """Two-tailed z-test."""
    z, _ = z_test(k1, n1, k2, n2)
    p = 2 * min(normal_cdf(z), 1 - normal_cdf(z))
    return z, p

def z_vs_chance(k, n, chance=CHANCE):
    p = k/n
    se = math.sqrt(max(chance*(1-chance)/n, 1e-12))
    return (p - chance) / se

def wilson_ci(k, n, z=1.96):
    if n == 0:
        return 0.0, 0.0
    p = k/n
    d = 1 + z**2/n
    c = (p + z**2/(2*n)) / d
    hw = z * math.sqrt(p*(1-p)/n + z**2/(4*n**2)) / d
    return c-hw, c+hw

def stars(p):
    if p is None:
        return '—'
    return '***' if p < .001 else '**' if p < .01 else '*' if p < .05 else '†' if p < .1 else 'n.s.'

def sig_vs_chance(k, n, chance=CHANCE):
    if n == 0:
        return 'n.s.', 1.0
    zv = z_vs_chance(k, n, chance)
    p = 1 - normal_cdf(zv)
    return stars(p), p

def acc_pp(k, n):
    if n == 0:
        return 0.0
    return (k/n - CHANCE) * 100

def ci_pp(k, n):
    lo, hi = wilson_ci(k, n)
    return (lo - CHANCE)*100, (hi - CHANCE)*100

# ── Data loading ───────────────────────────────────────────────────────────────
def is_correct(td, rd):
    d = (float(rd) - float(td) + 360) % 360
    return (360 - d if d > 180 else d) <= 22.5

def load_data():
    with open(DATA_PATH, newline='') as f:
        rows = list(csv.DictReader(f, delimiter='\t'))
    valid = [r for r in rows
             if r.get('TransDeg','').strip() and r.get('RespDeg','').strip()
             and r.get('EndKey','') not in ('timeout','skip','requeue')]
    for r in valid:
        r['correct'] = int(is_correct(r['TransDeg'], r['RespDeg']))
    return valid

# ── Aggregate ─────────────────────────────────────────────────────────────────
def aggregate(valid):
    SWAP_ORDER = ['N', 'C', 'Z', 'CZ']
    COND_ORDER = ['CUED', 'UNCUED']

    # Main: Cond × SwapType
    main = collections.defaultdict(lambda: [0, 0])
    # By DelayedFieldDepth
    by_dfd = collections.defaultdict(lambda: [0, 0])
    # By DelayedFieldColor
    by_dfc = collections.defaultdict(lambda: [0, 0])
    # Cond × SwapType × DelayedFieldDepth
    by_dfd_swap = collections.defaultdict(lambda: [0, 0])
    # Cond × SwapType × DelayedFieldColor
    by_dfc_swap = collections.defaultdict(lambda: [0, 0])

    for r in valid:
        cond  = r['Cond']
        swap  = r['SwapType']
        dfd   = r['DelayedFieldDepth']
        dfc   = r['DelayedFieldColor']
        corr  = r['correct']

        main[(cond, swap)][0] += corr
        main[(cond, swap)][1] += 1

        by_dfd[(cond, dfd)][0] += corr
        by_dfd[(cond, dfd)][1] += 1

        by_dfc[(cond, dfc)][0] += corr
        by_dfc[(cond, dfc)][1] += 1

        by_dfd_swap[(cond, swap, dfd)][0] += corr
        by_dfd_swap[(cond, swap, dfd)][1] += 1

        by_dfc_swap[(cond, swap, dfc)][0] += corr
        by_dfc_swap[(cond, swap, dfc)][1] += 1

    return {
        'n_valid':     len(valid),
        'main':        dict(main),
        'by_dfd':      dict(by_dfd),
        'by_dfc':      dict(by_dfc),
        'by_dfd_swap': dict(by_dfd_swap),
        'by_dfc_swap': dict(by_dfc_swap),
        'SWAP_ORDER':  SWAP_ORDER,
        'COND_ORDER':  COND_ORDER,
    }

# ── Chi-square helpers ────────────────────────────────────────────────────────
def chi2_2x2(k1, n1, k2, n2):
    """2×2 chi-square: correct/incorrect for group1 vs group2."""
    table = [[k1, n1-k1], [k2, n2-k2]]
    chi2, p, dof, _ = chi2_contingency(table, correction=False)
    return chi2, p, dof

# ── Print summary ─────────────────────────────────────────────────────────────
def print_summary(data):
    n = data['n_valid']
    main = data['main']
    SWAP_ORDER = data['SWAP_ORDER']

    # Total accuracy
    total_k = sum(v[0] for v in main.values())
    total_n = sum(v[1] for v in main.values())
    print(f"\n{'='*65}")
    print(f"  DecoupledDots_005m — Session 260406_1532")
    print(f"{'='*65}")
    print(f"  Total trials: {n}   Correct: {total_k}   "
          f"Accuracy: {total_k/total_n*100:.1f}%  "
          f"(+{acc_pp(total_k,total_n):.1f}pp above chance)")
    s_all, p_all = sig_vs_chance(total_k, total_n)
    print(f"  vs chance: {s_all}  (p={p_all:.4f})")

    print(f"\n{'─'*65}")
    print(f"  MAIN ANALYSIS: Cond × SwapType")
    print(f"{'─'*65}")
    print(f"  {'Condition':<12} {'Swap':<5} {'k':>4} {'n':>4}  "
          f"{'%corr':>6}  {'pp>chance':>9}  {'sig':>5}")
    print(f"  {'─'*60}")

    cueing_effects = {}
    for swap in SWAP_ORDER:
        for cond in ['CUED', 'UNCUED']:
            k, n_c = main.get((cond, swap), [0, 0])
            if n_c == 0:
                print(f"  {cond:<12} {swap:<5} {'—':>4} {'—':>4}")
                continue
            s, _ = sig_vs_chance(k, n_c)
            print(f"  {cond:<12} {swap:<5} {k:>4} {n_c:>4}  "
                  f"{k/n_c*100:>6.1f}%  {acc_pp(k,n_c):>+7.1f}pp  {s:>5}")
        # Cueing effect for this swap
        kc, nc = main.get(('CUED', swap), [0, 0])
        ku, nu = main.get(('UNCUED', swap), [0, 0])
        if nc > 0 and nu > 0:
            eff = acc_pp(kc, nc) - acc_pp(ku, nu)
            _, p = z_test(kc, nc, ku, nu)
            cueing_effects[swap] = (eff, p)
            print(f"  {'→ Cueing Δ':<12} {swap:<5} {'':>4} {'':>4}  "
                  f"{'':>6}  {eff:>+7.1f}pp  {stars(p):>5}")
        print()

    # ── Secondary: by DelayedFieldDepth ───────────────────────────────────────
    print(f"{'─'*65}")
    print(f"  SECONDARY: By DelayedFieldDepth (N=Near, F=Far)")
    print(f"{'─'*65}")
    by_dfd = data['by_dfd']
    for cond in ['CUED', 'UNCUED']:
        for dfd in ['N', 'F']:
            k, n_c = by_dfd.get((cond, dfd), [0, 0])
            if n_c == 0:
                continue
            s, _ = sig_vs_chance(k, n_c)
            label = 'Near' if dfd == 'N' else 'Far '
            print(f"  {cond:<12} {label}  {k:>4}/{n_c:<4}  "
                  f"{k/n_c*100:>6.1f}%  {acc_pp(k,n_c):>+7.1f}pp  {s}")
    print()

    # ── Secondary: by DelayedFieldColor ───────────────────────────────────────
    print(f"{'─'*65}")
    print(f"  SECONDARY: By DelayedFieldColor (R=Red, G=Green)")
    print(f"{'─'*65}")
    by_dfc = data['by_dfc']
    for cond in ['CUED', 'UNCUED']:
        for dfc in ['R', 'G']:
            k, n_c = by_dfc.get((cond, dfc), [0, 0])
            if n_c == 0:
                continue
            s, _ = sig_vs_chance(k, n_c)
            label = 'Red ' if dfc == 'R' else 'Grn '
            print(f"  {cond:<12} {label}  {k:>4}/{n_c:<4}  "
                  f"{k/n_c*100:>6.1f}%  {acc_pp(k,n_c):>+7.1f}pp  {s}")
    print()

    # ── Chi-square tests ──────────────────────────────────────────────────────
    print(f"{'─'*65}")
    print(f"  CHI-SQUARE TESTS")
    print(f"{'─'*65}")

    # (a) Overall CUED vs UNCUED
    kc_all = sum(main.get(('CUED', s), [0,0])[0] for s in SWAP_ORDER)
    nc_all = sum(main.get(('CUED', s), [0,0])[1] for s in SWAP_ORDER)
    ku_all = sum(main.get(('UNCUED', s), [0,0])[0] for s in SWAP_ORDER)
    nu_all = sum(main.get(('UNCUED', s), [0,0])[1] for s in SWAP_ORDER)
    chi2, p, dof = chi2_2x2(kc_all, nc_all, ku_all, nu_all)
    eff = acc_pp(kc_all, nc_all) - acc_pp(ku_all, nu_all)
    print(f"  (a) CUED vs UNCUED (overall): Δ={eff:+.1f}pp  χ²({dof})={chi2:.2f}  p={p:.4f}  {stars(p)}")

    # (b) Each swap vs N baseline
    kn_c, nn_c = main.get(('CUED',   'N'), [0,0])
    kn_u, nn_u = main.get(('UNCUED', 'N'), [0,0])
    print(f"\n  (b) Each swap vs N baseline (CUED):")
    for swap in ['C', 'Z', 'CZ']:
        ks_c, ns_c = main.get(('CUED', swap), [0,0])
        if ns_c == 0 or nn_c == 0:
            continue
        chi2, p, dof = chi2_2x2(kn_c, nn_c, ks_c, ns_c)
        eff = acc_pp(kn_c, nn_c) - acc_pp(ks_c, ns_c)
        print(f"    CUED:   N vs {swap}: Δ={eff:+.1f}pp  χ²({dof})={chi2:.2f}  p={p:.4f}  {stars(p)}")
    print(f"  (b) Each swap vs N baseline (UNCUED):")
    for swap in ['C', 'Z', 'CZ']:
        ks_u, ns_u = main.get(('UNCUED', swap), [0,0])
        if ns_u == 0 or nn_u == 0:
            continue
        chi2, p, dof = chi2_2x2(kn_u, nn_u, ks_u, ns_u)
        eff = acc_pp(kn_u, nn_u) - acc_pp(ks_u, ns_u)
        print(f"    UNCUED: N vs {swap}: Δ={eff:+.1f}pp  χ²({dof})={chi2:.2f}  p={p:.4f}  {stars(p)}")

    # (c) CUED×swap interaction: 4-way chi-square across swap types
    print(f"\n  (c) CUED×SwapType interaction (4×2 chi-square, Cond×correct/incorrect):")
    table_cued   = [[main.get(('CUED',   s), [0,0])[0],
                     main.get(('CUED',   s), [0,0])[1] - main.get(('CUED',   s), [0,0])[0]]
                    for s in SWAP_ORDER]
    table_uncued = [[main.get(('UNCUED', s), [0,0])[0],
                     main.get(('UNCUED', s), [0,0])[1] - main.get(('UNCUED', s), [0,0])[0]]
                    for s in SWAP_ORDER]

    # Interaction: 4×2 within CUED, 4×2 within UNCUED, then compare patterns
    chi2_c, p_c, dof_c, _ = chi2_contingency(table_cued, correction=False)
    chi2_u, p_u, dof_u, _ = chi2_contingency(table_uncued, correction=False)
    print(f"    CUED only (does accuracy vary across N/C/Z/CZ?): "
          f"χ²({dof_c})={chi2_c:.2f}  p={p_c:.4f}  {stars(p_c)}")
    print(f"    UNCUED only (does accuracy vary across N/C/Z/CZ?): "
          f"χ²({dof_u})={chi2_u:.2f}  p={p_u:.4f}  {stars(p_u)}")

    # Full 8-cell 2×4 table (Cond × SwapType)
    table_full = [
        [main.get(('CUED',   s), [0,0])[0],
         main.get(('CUED',   s), [0,0])[1] - main.get(('CUED',   s), [0,0])[0]]
        for s in SWAP_ORDER
    ] + [
        [main.get(('UNCUED', s), [0,0])[0],
         main.get(('UNCUED', s), [0,0])[1] - main.get(('UNCUED', s), [0,0])[0]]
        for s in SWAP_ORDER
    ]
    # Rearrange as 2×4 (rows=Cond, cols=Swap) for correct/incorrect pooled
    table_2x4 = [
        [main.get(('CUED',   s), [0,0])[0] for s in SWAP_ORDER],
        [main.get(('UNCUED', s), [0,0])[0] for s in SWAP_ORDER],
    ]
    # This tests whether the pattern of accuracy across swaps differs by Cond
    table_2x4_inc = [
        [main.get(('CUED',   s), [0,0])[1] - main.get(('CUED',   s), [0,0])[0] for s in SWAP_ORDER],
        [main.get(('UNCUED', s), [0,0])[1] - main.get(('UNCUED', s), [0,0])[0] for s in SWAP_ORDER],
    ]
    # For a proper 2×4×2 interaction we use a combined 8-row table
    table_8x2 = np.array([[main.get((cond, s), [0,0])[0],
                           main.get((cond, s), [0,0])[1] - main.get((cond, s), [0,0])[0]]
                          for cond in ['CUED','UNCUED'] for s in SWAP_ORDER])
    chi2_int, p_int, dof_int, _ = chi2_contingency(table_8x2, correction=False)
    print(f"    Full 2×4 (Cond × Swap): χ²({dof_int})={chi2_int:.2f}  p={p_int:.4f}  {stars(p_int)}")

    print(f"\n{'='*65}\n")
    return cueing_effects

# ── Plotting helpers ───────────────────────────────────────────────────────────
C_CUED   = '#1565C0'   # blue for CUED
C_UNCUED = '#E65100'   # orange for UNCUED
C_NEAR   = '#CC3333'   # red = near
C_FAR    = '#228B22'   # green = far

SWAP_COLORS = {
    'N':  '#555555',
    'C':  '#8B008B',
    'Z':  '#005F8F',
    'CZ': '#8B4513',
}
SWAP_LABELS_FULL = {
    'N':  'N\n(baseline)',
    'C':  'C\n(color swap)',
    'Z':  'Z\n(depth swap)',
    'CZ': 'CZ\n(color+depth)',
}

def draw_bar(ax, x, k, n, color, width=0.35, alpha=1.0, label=None, hatch=None):
    pp = acc_pp(k, n)
    lo, hi = ci_pp(k, n)
    ax.bar(x, pp, width, color=color, alpha=alpha, zorder=3,
           label=label, edgecolor='white', linewidth=0.5, hatch=hatch)
    ax.errorbar(x, pp, yerr=[[pp-lo], [hi-pp]], fmt='none',
                color='#333', capsize=3, capthick=1, lw=1, zorder=4)
    return pp, lo, hi

def style_ax(ax, title='', ylim=(-15, 65), ylabel=True):
    ax.axhline(0, color='#888', lw=0.8, ls='--', zorder=2)
    ax.set_ylim(*ylim)
    ax.set_title(title, fontsize=9, fontweight='bold', pad=4)
    if ylabel:
        ax.set_ylabel('% correct above chance', fontsize=7.5)
    ax.tick_params(labelsize=7)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.yaxis.set_minor_locator(matplotlib.ticker.MultipleLocator(5))
    ax.grid(axis='y', which='minor', lw=0.3, alpha=0.4, zorder=0)
    ax.grid(axis='y', which='major', lw=0.5, alpha=0.5, zorder=0)

def sig_label_bar(ax, x, y_top, s):
    ax.text(x, y_top + 1.5, s, ha='center', va='bottom', fontsize=7, color='#333')

def bar_annotation(ax, x, k, n):
    """Print n and % inside/below bar."""
    pp = acc_pp(k, n)
    pct = k/n*100 if n > 0 else 0
    y = pp/2
    ax.text(x, y, f'n={n}\n{pct:.0f}%',
            ha='center', va='center', fontsize=5.5, color='white',
            fontweight='bold')

# ── Main figure ────────────────────────────────────────────────────────────────
def make_figure(data, cueing_effects):
    n_valid   = data['n_valid']
    main      = data['main']
    by_dfd    = data['by_dfd']
    by_dfc    = data['by_dfc']
    SWAP_ORDER = data['SWAP_ORDER']

    fig = plt.figure(figsize=(14, 10))
    fig.patch.set_facecolor('white')

    fig.text(0.5, 0.978,
             f'DecoupledDots_005m — Session 260406_1532   (n={n_valid} trials)',
             ha='center', va='top', fontsize=13, fontweight='bold', color='#111')
    fig.text(0.5, 0.953,
             'linkDepthColor=0   •   Swap types: N / C (color) / Z (depth) / CZ (color+depth)'
             '   •   depth=0.05m   •   8-AFC   •   chance=12.5%',
             ha='center', va='top', fontsize=8.5, color='#555')

    gs = gridspec.GridSpec(2, 3, top=0.920, bottom=0.09,
                           left=0.07, right=0.97,
                           hspace=0.50, wspace=0.40)

    # ── Panel A: Main Cond × SwapType bar chart ────────────────────────────────
    ax_a = fig.add_subplot(gs[0, 0:2])

    # Layout: 4 swap groups, each with [CUED, UNCUED] bars
    group_width = 1.0
    bar_width   = 0.38
    gap         = 0.08   # gap between CUED and UNCUED within group
    group_gap   = 0.35   # gap between groups

    group_centers = []
    x_ticks = []
    x_tick_labels = []

    for gi, swap in enumerate(SWAP_ORDER):
        x_base = gi * (group_width + group_gap)
        x_cued   = x_base
        x_uncued = x_base + bar_width + gap
        group_center = (x_cued + x_uncued) / 2
        group_centers.append(group_center)

        kc, nc = main.get(('CUED',   swap), [0, 0])
        ku, nu = main.get(('UNCUED', swap), [0, 0])

        pp_c, lo_c, hi_c = draw_bar(ax_a, x_cued,   kc, nc, C_CUED,
                                     width=bar_width, alpha=1.0,
                                     label='CUED' if gi == 0 else None)
        pp_u, lo_u, hi_u = draw_bar(ax_a, x_uncued, ku, nu, C_UNCUED,
                                     width=bar_width, alpha=1.0,
                                     label='UNCUED' if gi == 0 else None)

        # Significance vs chance labels on top of each bar
        sc, _ = sig_vs_chance(kc, nc)
        su, _ = sig_vs_chance(ku, nu)
        sig_label_bar(ax_a, x_cued,   max(pp_c, hi_c), sc)
        sig_label_bar(ax_a, x_uncued, max(pp_u, hi_u), su)

        # n and % annotation inside bars
        bar_annotation(ax_a, x_cued,   kc, nc)
        bar_annotation(ax_a, x_uncued, ku, nu)

        # Cueing effect annotation above the pair
        if swap in cueing_effects:
            eff, p_eff = cueing_effects[swap]
            y_ann = 55
            ax_a.annotate('', xy=(x_uncued + bar_width/2, y_ann - 3),
                          xytext=(x_cued - bar_width/2, y_ann - 3),
                          arrowprops=dict(arrowstyle='<->', color='#444', lw=0.9))
            ax_a.text(group_center, y_ann + 0.5,
                      f'Δ{eff:+.1f}pp {stars(p_eff)}',
                      ha='center', va='bottom', fontsize=6.8, color='#333',
                      fontweight='bold')

        # X-tick at group center with swap label
        x_ticks.append(group_center)
        x_tick_labels.append(SWAP_LABELS_FULL[swap])

    ax_a.set_xticks(x_ticks)
    ax_a.set_xticklabels(x_tick_labels, fontsize=7.5)
    style_ax(ax_a, title='A.  Accuracy by Condition × SwapType', ylim=(-18, 68))

    # Legend
    cued_patch   = mpatches.Patch(color=C_CUED,   label='CUED')
    uncued_patch = mpatches.Patch(color=C_UNCUED,  label='UNCUED')
    ax_a.legend(handles=[cued_patch, uncued_patch], fontsize=8,
                loc='upper right', framealpha=0.9)

    # ── Panel B: Cueing effects summary ───────────────────────────────────────
    ax_b = fig.add_subplot(gs[0, 2])
    xs_b = np.arange(len(SWAP_ORDER))
    eff_vals  = []
    eff_stars = []
    eff_cols  = []
    for swap in SWAP_ORDER:
        if swap in cueing_effects:
            eff, p = cueing_effects[swap]
            eff_vals.append(eff)
            eff_stars.append(stars(p))
            eff_cols.append(C_CUED if eff >= 0 else '#cc4444')
        else:
            eff_vals.append(0)
            eff_stars.append('n.s.')
            eff_cols.append('#aaaaaa')

    for xi, (swap, ev, es, ec) in enumerate(zip(SWAP_ORDER, eff_vals, eff_stars, eff_cols)):
        ax_b.bar(xi, ev, 0.55, color=ec, alpha=0.85, zorder=3,
                 edgecolor='white', linewidth=0.5)
        y_lbl = ev + 1.5 if ev >= 0 else ev - 1.5
        va_lbl = 'bottom' if ev >= 0 else 'top'
        ax_b.text(xi, y_lbl, es, ha='center', va=va_lbl, fontsize=8, color='#333')
        # Numerical label
        ax_b.text(xi, ev/2, f'{ev:+.1f}pp', ha='center', va='center',
                  fontsize=6.5, color='white', fontweight='bold')

    ax_b.set_xticks(xs_b)
    ax_b.set_xticklabels([SWAP_LABELS_FULL[s] for s in SWAP_ORDER], fontsize=7)
    ax_b.set_ylabel('Cueing effect (CUED − UNCUED, pp)', fontsize=7.5)
    style_ax(ax_b, title='B.  Cueing effect by SwapType', ylim=(-18, 68), ylabel=False)
    ax_b.set_ylabel('Δ pp (CUED − UNCUED)', fontsize=7)

    # ── Panel C: By DelayedFieldDepth (Near vs Far) ───────────────────────────
    ax_c = fig.add_subplot(gs[1, 0])

    dep_positions = {'CUED': {'N': 0.0, 'F': 0.42}, 'UNCUED': {'N': 1.05, 'F': 1.47}}
    dep_colors_map = {'N': C_NEAR, 'F': C_FAR}
    cond_alphas  = {'CUED': 1.0, 'UNCUED': 0.75}

    for cond in ['CUED', 'UNCUED']:
        for dfd in ['N', 'F']:
            k, n_c = by_dfd.get((cond, dfd), [0, 0])
            x = dep_positions[cond][dfd]
            col = dep_colors_map[dfd]
            alp = cond_alphas[cond]
            pp, lo, hi = draw_bar(ax_c, x, k, n_c, col, width=0.38, alpha=alp)
            sc, _ = sig_vs_chance(k, n_c)
            sig_label_bar(ax_c, x, max(pp, hi), sc)
            bar_annotation(ax_c, x, k, n_c)

    # Group brackets
    ax_c.annotate('', xy=(0.80, -13), xytext=(-0.19, -13),
                  arrowprops=dict(arrowstyle='-', color=C_CUED, lw=1.5))
    ax_c.annotate('', xy=(1.85, -13), xytext=(0.87, -13),
                  arrowprops=dict(arrowstyle='-', color=C_UNCUED, lw=1.5))
    ax_c.text(0.21, -15.8, 'CUED', ha='center', fontsize=8,
              color=C_CUED, fontweight='bold')
    ax_c.text(1.36, -15.8, 'UNCUED', ha='center', fontsize=8,
              color=C_UNCUED, fontweight='bold')

    ax_c.set_xticks([0.0, 0.42, 1.05, 1.47])
    ax_c.set_xticklabels(['Near\n(N)', 'Far\n(F)', 'Near\n(N)', 'Far\n(F)'], fontsize=7.5)
    near_patch = mpatches.Patch(color=C_NEAR, label='Near (DelFieldDepth=N)')
    far_patch  = mpatches.Patch(color=C_FAR,  label='Far (DelFieldDepth=F)')
    ax_c.legend(handles=[near_patch, far_patch], fontsize=6.5,
                loc='upper right', framealpha=0.9)
    style_ax(ax_c, title='C.  By DelayedFieldDepth', ylim=(-18, 68))

    # ── Panel D: By DelayedFieldColor (R vs G) ────────────────────────────────
    ax_d = fig.add_subplot(gs[1, 1])

    col_positions = {'CUED': {'R': 0.0, 'G': 0.42}, 'UNCUED': {'R': 1.05, 'G': 1.47}}
    dfc_colors_map = {'R': '#CC2222', 'G': '#228B22'}
    dfc_labels_map = {'R': 'Red', 'G': 'Green'}

    by_dfc = data['by_dfc']
    for cond in ['CUED', 'UNCUED']:
        for dfc in ['R', 'G']:
            k, n_c = by_dfc.get((cond, dfc), [0, 0])
            x = col_positions[cond][dfc]
            col = dfc_colors_map[dfc]
            alp = cond_alphas[cond]
            pp, lo, hi = draw_bar(ax_d, x, k, n_c, col, width=0.38, alpha=alp)
            sc, _ = sig_vs_chance(k, n_c)
            sig_label_bar(ax_d, x, max(pp, hi), sc)
            bar_annotation(ax_d, x, k, n_c)

    ax_d.annotate('', xy=(0.80, -13), xytext=(-0.19, -13),
                  arrowprops=dict(arrowstyle='-', color=C_CUED, lw=1.5))
    ax_d.annotate('', xy=(1.85, -13), xytext=(0.87, -13),
                  arrowprops=dict(arrowstyle='-', color=C_UNCUED, lw=1.5))
    ax_d.text(0.21, -15.8, 'CUED', ha='center', fontsize=8,
              color=C_CUED, fontweight='bold')
    ax_d.text(1.36, -15.8, 'UNCUED', ha='center', fontsize=8,
              color=C_UNCUED, fontweight='bold')

    ax_d.set_xticks([0.0, 0.42, 1.05, 1.47])
    ax_d.set_xticklabels(['Red\n(R)', 'Green\n(G)', 'Red\n(R)', 'Green\n(G)'], fontsize=7.5)
    red_patch   = mpatches.Patch(color='#CC2222', label='Red (DelFieldColor=R)')
    green_patch = mpatches.Patch(color='#228B22', label='Green (DelFieldColor=G)')
    ax_d.legend(handles=[red_patch, green_patch], fontsize=6.5,
                loc='upper right', framealpha=0.9)
    style_ax(ax_d, title='D.  By DelayedFieldColor', ylim=(-18, 68))

    # ── Panel E: Accuracy table ────────────────────────────────────────────────
    ax_e = fig.add_subplot(gs[1, 2])
    ax_e.axis('off')

    headers = ['Cond', 'Swap', 'k', 'n', '%corr', '+chc', 'sig']
    table_rows = []
    for swap in SWAP_ORDER:
        for cond in ['CUED', 'UNCUED']:
            k, n_c = main.get((cond, swap), [0, 0])
            if n_c == 0:
                continue
            s, _ = sig_vs_chance(k, n_c)
            table_rows.append([
                cond, swap, str(k), str(n_c),
                f'{k/n_c*100:.0f}%',
                f'{acc_pp(k,n_c):+.1f}',
                s
            ])
        # Blank row between swap groups
        if swap != SWAP_ORDER[-1]:
            table_rows.append(['','','','','','',''])

    col_widths  = [0.22, 0.10, 0.08, 0.08, 0.12, 0.12, 0.12]
    xs_t = np.cumsum([0] + col_widths[:-1]) + 0.02
    y0   = 0.95
    lh   = 0.065

    for xi, (h, xpos) in enumerate(zip(headers, xs_t)):
        ax_e.text(xpos, y0, h, transform=ax_e.transAxes,
                  fontsize=7, fontweight='bold', va='top', color='#222')

    ax_e.plot([0, 1], [y0 - lh*0.6]*2, color='#aaa', lw=0.8,
              transform=ax_e.transAxes, clip_on=False)

    row_colors = ['#EEF4FF', '#FFF4EE', '#EEF4FF', '#FFF4EE',
                  '#F0F8F0', '#F8F0F8', '#F0F8F0', '#F8F0F8']
    for ri, row in enumerate(table_rows):
        y = y0 - lh*(ri+1) - 0.01
        if all(c == '' for c in row):
            ax_e.plot([0.02, 0.98], [y + lh*0.3]*2, color='#ddd', lw=0.5,
                      transform=ax_e.transAxes, clip_on=False)
            continue
        bg = row_colors[ri % len(row_colors)]
        ax_e.axhspan(y - lh*0.45, y + lh*0.55, xmin=0.01, xmax=0.99,
                     facecolor=bg, alpha=0.5, transform=ax_e.transAxes)
        for xi, (cell, xpos) in enumerate(zip(row, xs_t)):
            color = '#222'
            if xi == 0:  # Cond column
                color = C_CUED if cell == 'CUED' else (C_UNCUED if cell == 'UNCUED' else '#222')
            ax_e.text(xpos, y, cell, transform=ax_e.transAxes,
                      fontsize=6.5, va='center', color=color)

    ax_e.set_title('E.  Accuracy table', fontsize=9, fontweight='bold', pad=4)

    # ── Footer ─────────────────────────────────────────────────────────────────
    fig.text(0.5, 0.025,
             'Error bars: 95% Wilson CI  |  Stars vs chance (12.5%): †p<.1  *p<.05  **p<.01  ***p<.001  |  '
             'Δ = CUED − UNCUED cueing effect in percentage points  |  '
             'C=color swap, Z=depth swap, CZ=both, N=no swap',
             ha='center', va='bottom', fontsize=6, color='#666')

    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    fig.savefig(OUT_PATH, dpi=150, bbox_inches='tight', facecolor='white')
    print(f"Saved: {OUT_PATH}")
    return fig

# ── Run ────────────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    valid = load_data()
    data  = aggregate(valid)
    cueing_effects = print_summary(data)
    make_figure(data, cueing_effects)
