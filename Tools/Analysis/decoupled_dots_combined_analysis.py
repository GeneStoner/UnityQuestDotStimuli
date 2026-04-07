#!/usr/bin/env python3
"""
decoupled_dots_combined_analysis.py — Analysis & figures for two DecoupledDots sessions

Session 1 (260406_1532): DecoupledDots_005m        — delayTranslator=true  (CUED=translator cued)
Session 2 (260406_1754): DecoupledDots_Inv_005m    — delayTranslator=false (labels INVERTED)

Label inversion for session 2:
  Raw "CUED"   in file → behavioral UNCUED (temporal cue marks rotator)
  Raw "UNCUED" in file → behavioral CUED   (temporal cue marks translator)
  → We flip before any analysis so that CUED always means "cue correctly marks translator."

SwapTypes:
  N  = no swap (baseline)
  C  = color-only swap
  Z  = depth-only swap
  CZ = color + depth swap

Outputs:
  Agents/Figures/decoupled_dots_260406_1754.png   — Session 2 alone
  Agents/Figures/decoupled_dots_combined.png      — Both sessions combined
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

# ── Paths ──────────────────────────────────────────────────────────────────────
DATA_S1 = "/tmp/quest_pull2/files/vr_dots_session_260406_1532.tsv"
DATA_S2 = "/tmp/quest_pull2/files/vr_dots_session_260406_1754.tsv"
DATA_S3 = "/tmp/quest_pull3/files/vr_dots_session_260407_0643.tsv"
DATA_S4 = "/tmp/quest_pull3/files/vr_dots_session_260407_0731.tsv"

FIG_DIR = os.path.expanduser(
    "~/Projects/ObjectBasedAttention/VRDots/Agents/Figures/")

OUT_S1       = os.path.join(FIG_DIR, "decoupled_dots_260406_1532.png")
OUT_S2       = os.path.join(FIG_DIR, "decoupled_dots_260406_1754.png")
OUT_S3       = os.path.join(FIG_DIR, "decoupled_dots_260407_0643.png")
OUT_S4       = os.path.join(FIG_DIR, "decoupled_dots_260407_0731.png")
OUT_COMB     = os.path.join(FIG_DIR, "decoupled_dots_combined.png")
OUT_COMB4    = os.path.join(FIG_DIR, "decoupled_dots_combined_s1s2s3s4.png")
OUT_SESS_CMP = os.path.join(FIG_DIR, "decoupled_dots_session_comparison.png")

CHANCE = 1/8

# ── Field-cueing factor membership ────────────────────────────────────────────
# Depth-field cued ✓ = translator ends up in same plane delayed field first appeared
DEPTH_FIELD_CUED = {
    'CUED':   {'N': True,  'C': True,  'Z': False, 'CZ': False},
    'UNCUED': {'N': False, 'C': False, 'Z': True,  'CZ': True},
}
# Color-field cued ✓ = translator color matches delayed field's original color at translation
COLOR_FIELD_CUED = {
    'CUED':   {'N': True,  'C': False, 'Z': True,  'CZ': False},
    'UNCUED': {'N': False, 'C': True,  'Z': False, 'CZ': True},
}

# ── Stats helpers ──────────────────────────────────────────────────────────────
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

def load_data(path, invert_cond=False):
    """Load session TSV. If invert_cond=True, flip CUED/UNCUED labels."""
    with open(path, newline='') as f:
        rows = list(csv.DictReader(f, delimiter='\t'))
    valid = [r for r in rows
             if r.get('TransDeg','').strip() and r.get('RespDeg','').strip()
             and r.get('EndKey','') not in ('timeout','skip','requeue')]
    for r in valid:
        if invert_cond:
            r['Cond'] = 'UNCUED' if r['Cond'] == 'CUED' else 'CUED'
        r['correct'] = int(is_correct(r['TransDeg'], r['RespDeg']))
    return valid

# ── Aggregate ──────────────────────────────────────────────────────────────────
def aggregate(valid):
    SWAP_ORDER = ['N', 'C', 'Z', 'CZ']
    COND_ORDER = ['CUED', 'UNCUED']

    main        = collections.defaultdict(lambda: [0, 0])   # (cond, swap) -> [k, n]
    by_dfd      = collections.defaultdict(lambda: [0, 0])   # (cond, dfd)
    by_dfc      = collections.defaultdict(lambda: [0, 0])   # (cond, dfc)
    by_dfd_swap = collections.defaultdict(lambda: [0, 0])   # (cond, swap, dfd)
    by_dfc_swap = collections.defaultdict(lambda: [0, 0])   # (cond, swap, dfc)
    # Field-cueing factors: overall + breakdown by dot-cueing condition
    fc_depth     = {'cued': [0,0], 'uncued': [0,0]}
    fc_color     = {'cued': [0,0], 'uncued': [0,0]}
    fc_depth_dot = {'cued':   {'CUED':[0,0],'UNCUED':[0,0]},
                    'uncued': {'CUED':[0,0],'UNCUED':[0,0]}}
    fc_color_dot = {'cued':   {'CUED':[0,0],'UNCUED':[0,0]},
                    'uncued': {'CUED':[0,0],'UNCUED':[0,0]}}

    for r in valid:
        cond = r['Cond']
        swap = r['SwapType']
        dfd  = r['DelayedFieldDepth']
        dfc  = r['DelayedFieldColor']
        corr = r['correct']

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

        if cond in ('CUED','UNCUED') and swap in ('N','C','Z','CZ'):
            dc = 'cued' if DEPTH_FIELD_CUED[cond][swap] else 'uncued'
            cc = 'cued' if COLOR_FIELD_CUED[cond][swap]  else 'uncued'
            fc_depth[dc][0] += corr;  fc_depth[dc][1] += 1
            fc_color[cc][0] += corr;  fc_color[cc][1] += 1
            fc_depth_dot[dc][cond][0] += corr; fc_depth_dot[dc][cond][1] += 1
            fc_color_dot[cc][cond][0] += corr; fc_color_dot[cc][cond][1] += 1

    return {
        'n_valid':      len(valid),
        'main':         dict(main),
        'by_dfd':       dict(by_dfd),
        'by_dfc':       dict(by_dfc),
        'by_dfd_swap':  dict(by_dfd_swap),
        'by_dfc_swap':  dict(by_dfc_swap),
        'fc_depth':     fc_depth,
        'fc_color':     fc_color,
        'fc_depth_dot': fc_depth_dot,
        'fc_color_dot': fc_color_dot,
        'SWAP_ORDER':   SWAP_ORDER,
        'COND_ORDER':   COND_ORDER,
    }

# ── Chi-square helpers ─────────────────────────────────────────────────────────
def chi2_2x2(k1, n1, k2, n2):
    table = [[k1, n1-k1], [k2, n2-k2]]
    chi2, p, dof, _ = chi2_contingency(table, correction=False)
    return chi2, p, dof

# ── Print summary ──────────────────────────────────────────────────────────────
def print_summary(data, label=''):
    n     = data['n_valid']
    main  = data['main']
    SWAP_ORDER = data['SWAP_ORDER']

    total_k = sum(v[0] for v in main.values())
    total_n = sum(v[1] for v in main.values())

    print(f"\n{'='*70}")
    print(f"  {label}")
    print(f"{'='*70}")
    print(f"  Total trials: {n}   Correct: {total_k}   "
          f"Accuracy: {total_k/total_n*100:.1f}%  "
          f"(+{acc_pp(total_k,total_n):.1f}pp above chance)")
    s_all, p_all = sig_vs_chance(total_k, total_n)
    print(f"  vs chance: {s_all}  (p={p_all:.4f})")

    # ── Main table ─────────────────────────────────────────────────────────────
    print(f"\n{'─'*70}")
    print(f"  MAIN TABLE: Cond × SwapType")
    print(f"{'─'*70}")
    print(f"  {'Condition':<12} {'Swap':<5} {'k':>4} {'n':>4}  "
          f"{'%corr':>6}  {'pp>chance':>9}  {'sig':>5}")
    print(f"  {'─'*65}")

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
        kc, nc = main.get(('CUED',   swap), [0, 0])
        ku, nu = main.get(('UNCUED', swap), [0, 0])
        if nc > 0 and nu > 0:
            eff = acc_pp(kc, nc) - acc_pp(ku, nu)
            _, p = z_test(kc, nc, ku, nu)
            cueing_effects[swap] = (eff, p)
            print(f"  {'→ Cueing Δ':<12} {swap:<5} {'':>4} {'':>4}  "
                  f"{'':>6}  {eff:>+7.1f}pp  {stars(p):>5}")
        print()

    # ── By DelayedFieldDepth ───────────────────────────────────────────────────
    print(f"{'─'*70}")
    print(f"  SECONDARY: By DelayedFieldDepth (N=Near, F=Far)")
    print(f"{'─'*70}")
    by_dfd = data['by_dfd']
    for cond in ['CUED', 'UNCUED']:
        for dfd in ['N', 'F']:
            k, n_c = by_dfd.get((cond, dfd), [0, 0])
            if n_c == 0:
                continue
            s, _ = sig_vs_chance(k, n_c)
            label_str = 'Near' if dfd == 'N' else 'Far '
            print(f"  {cond:<12} {label_str}  {k:>4}/{n_c:<4}  "
                  f"{k/n_c*100:>6.1f}%  {acc_pp(k,n_c):>+7.1f}pp  {s}")
    # Near/Far cueing delta
    for dfd in ['N', 'F']:
        kc, nc = by_dfd.get(('CUED',   dfd), [0, 0])
        ku, nu = by_dfd.get(('UNCUED', dfd), [0, 0])
        if nc > 0 and nu > 0:
            eff = acc_pp(kc, nc) - acc_pp(ku, nu)
            _, p = z_test(kc, nc, ku, nu)
            label_str = 'Near' if dfd == 'N' else 'Far '
            print(f"  {'→ Cueing Δ':<12} {label_str}  {'':>4} {'':>4}  "
                  f"{'':>6}  {eff:>+7.1f}pp  {stars(p)}")
    print()

    # ── By DelayedFieldDepth × SwapType ───────────────────────────────────────
    print(f"{'─'*70}")
    print(f"  SECONDARY: By SwapType × DelayedFieldDepth")
    print(f"{'─'*70}")
    by_dfd_swap = data['by_dfd_swap']
    for swap in SWAP_ORDER:
        print(f"  SwapType = {swap}")
        for cond in ['CUED', 'UNCUED']:
            for dfd in ['N', 'F']:
                k, n_c = by_dfd_swap.get((cond, swap, dfd), [0, 0])
                if n_c == 0:
                    continue
                s, _ = sig_vs_chance(k, n_c)
                label_str = 'Near' if dfd == 'N' else 'Far '
                print(f"    {cond:<12} {label_str}  {k:>4}/{n_c:<4}  "
                      f"{k/n_c*100:>6.1f}%  {acc_pp(k,n_c):>+7.1f}pp  {s}")
        print()

    # ── Chi-square tests ───────────────────────────────────────────────────────
    print(f"{'─'*70}")
    print(f"  CHI-SQUARE TESTS")
    print(f"{'─'*70}")

    # (a) Overall CUED vs UNCUED
    kc_all = sum(main.get(('CUED',   s), [0,0])[0] for s in SWAP_ORDER)
    nc_all = sum(main.get(('CUED',   s), [0,0])[1] for s in SWAP_ORDER)
    ku_all = sum(main.get(('UNCUED', s), [0,0])[0] for s in SWAP_ORDER)
    nu_all = sum(main.get(('UNCUED', s), [0,0])[1] for s in SWAP_ORDER)
    chi2, p, dof = chi2_2x2(kc_all, nc_all, ku_all, nu_all)
    eff = acc_pp(kc_all, nc_all) - acc_pp(ku_all, nu_all)
    print(f"  (a) CUED vs UNCUED (overall): Δ={eff:+.1f}pp  "
          f"χ²({dof})={chi2:.2f}  p={p:.4f}  {stars(p)}")

    # (b) Each swap vs N baseline
    kn_c, nn_c = main.get(('CUED',   'N'), [0,0])
    kn_u, nn_u = main.get(('UNCUED', 'N'), [0,0])
    print(f"\n  (b) Each swap vs N baseline:")
    for swap in ['C', 'Z', 'CZ']:
        ks_c, ns_c = main.get(('CUED',   swap), [0,0])
        ks_u, ns_u = main.get(('UNCUED', swap), [0,0])
        if ns_c > 0 and nn_c > 0:
            chi2, p, dof = chi2_2x2(kn_c, nn_c, ks_c, ns_c)
            eff = acc_pp(kn_c, nn_c) - acc_pp(ks_c, ns_c)
            print(f"    CUED:   N vs {swap}: Δ={eff:+.1f}pp  "
                  f"χ²({dof})={chi2:.2f}  p={p:.4f}  {stars(p)}")
        if ns_u > 0 and nn_u > 0:
            chi2, p, dof = chi2_2x2(kn_u, nn_u, ks_u, ns_u)
            eff = acc_pp(kn_u, nn_u) - acc_pp(ks_u, ns_u)
            print(f"    UNCUED: N vs {swap}: Δ={eff:+.1f}pp  "
                  f"χ²({dof})={chi2:.2f}  p={p:.4f}  {stars(p)}")

    # (c) CUED×SwapType interaction
    print(f"\n  (c) CUED×SwapType interaction:")
    table_cued   = [[main.get(('CUED',   s), [0,0])[0],
                     main.get(('CUED',   s), [0,0])[1] - main.get(('CUED',   s), [0,0])[0]]
                    for s in SWAP_ORDER]
    table_uncued = [[main.get(('UNCUED', s), [0,0])[0],
                     main.get(('UNCUED', s), [0,0])[1] - main.get(('UNCUED', s), [0,0])[0]]
                    for s in SWAP_ORDER]
    chi2_c, p_c, dof_c, _ = chi2_contingency(table_cued, correction=False)
    chi2_u, p_u, dof_u, _ = chi2_contingency(table_uncued, correction=False)
    print(f"    CUED only (accuracy across N/C/Z/CZ?):   "
          f"χ²({dof_c})={chi2_c:.2f}  p={p_c:.4f}  {stars(p_c)}")
    print(f"    UNCUED only (accuracy across N/C/Z/CZ?): "
          f"χ²({dof_u})={chi2_u:.2f}  p={p_u:.4f}  {stars(p_u)}")

    table_8x2 = np.array([[main.get((cond, s), [0,0])[0],
                           main.get((cond, s), [0,0])[1] - main.get((cond, s), [0,0])[0]]
                          for cond in ['CUED','UNCUED'] for s in SWAP_ORDER])
    chi2_int, p_int, dof_int, _ = chi2_contingency(table_8x2, correction=False)
    print(f"    Full 2×4 (Cond × Swap):                  "
          f"χ²({dof_int})={chi2_int:.2f}  p={p_int:.4f}  {stars(p_int)}")

    print(f"\n{'='*70}\n")
    return cueing_effects

# ── Plotting style constants ───────────────────────────────────────────────────
C_CUED   = '#1565C0'
C_UNCUED = '#E65100'
C_NEAR   = '#CC3333'
C_FAR    = '#228B22'

SWAP_COLORS = {'N': '#555555', 'C': '#8B008B', 'Z': '#005F8F', 'CZ': '#8B4513'}
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

def style_ax(ax, title='', ylim=(-18, 68), ylabel=True):
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
    pp  = acc_pp(k, n)
    pct = k/n*100 if n > 0 else 0
    ax.text(x, pp/2, f'n={n}\n{pct:.0f}%',
            ha='center', va='center', fontsize=5.5, color='white', fontweight='bold')

def draw_main_panel(ax, main, SWAP_ORDER, cueing_effects, title=''):
    group_width = 1.0
    bar_width   = 0.38
    gap         = 0.08
    group_gap   = 0.35
    x_ticks = []
    x_tick_labels = []

    for gi, swap in enumerate(SWAP_ORDER):
        x_base   = gi * (group_width + group_gap)
        x_cued   = x_base
        x_uncued = x_base + bar_width + gap
        group_center = (x_cued + x_uncued) / 2

        kc, nc = main.get(('CUED',   swap), [0, 0])
        ku, nu = main.get(('UNCUED', swap), [0, 0])

        pp_c, lo_c, hi_c = draw_bar(ax, x_cued,   kc, nc, C_CUED,
                                     width=bar_width,
                                     label='CUED' if gi == 0 else None)
        pp_u, lo_u, hi_u = draw_bar(ax, x_uncued, ku, nu, C_UNCUED,
                                     width=bar_width,
                                     label='UNCUED' if gi == 0 else None)

        sc, _ = sig_vs_chance(kc, nc)
        su, _ = sig_vs_chance(ku, nu)
        sig_label_bar(ax, x_cued,   max(pp_c, hi_c), sc)
        sig_label_bar(ax, x_uncued, max(pp_u, hi_u), su)

        bar_annotation(ax, x_cued,   kc, nc)
        bar_annotation(ax, x_uncued, ku, nu)

        if swap in cueing_effects:
            eff, p_eff = cueing_effects[swap]
            y_ann = 55
            ax.annotate('', xy=(x_uncued + bar_width/2, y_ann - 3),
                        xytext=(x_cued - bar_width/2, y_ann - 3),
                        arrowprops=dict(arrowstyle='<->', color='#444', lw=0.9))
            ax.text(group_center, y_ann + 0.5,
                    f'Δ{eff:+.1f}pp {stars(p_eff)}',
                    ha='center', va='bottom', fontsize=6.8, color='#333',
                    fontweight='bold')

        x_ticks.append(group_center)
        x_tick_labels.append(SWAP_LABELS_FULL[swap])

    ax.set_xticks(x_ticks)
    ax.set_xticklabels(x_tick_labels, fontsize=7.5)
    style_ax(ax, title=title, ylim=(-18, 68))
    cued_patch   = mpatches.Patch(color=C_CUED,   label='CUED')
    uncued_patch = mpatches.Patch(color=C_UNCUED,  label='UNCUED')
    ax.legend(handles=[cued_patch, uncued_patch], fontsize=8,
              loc='upper right', framealpha=0.9)

def draw_cueing_panel(ax, main, SWAP_ORDER, cueing_effects, title=''):
    xs_b = np.arange(len(SWAP_ORDER))
    eff_vals, eff_stars, eff_cols = [], [], []
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
        ax.bar(xi, ev, 0.55, color=ec, alpha=0.85, zorder=3,
               edgecolor='white', linewidth=0.5)
        y_lbl = ev + 1.5 if ev >= 0 else ev - 1.5
        va_lbl = 'bottom' if ev >= 0 else 'top'
        ax.text(xi, y_lbl, es, ha='center', va=va_lbl, fontsize=8, color='#333')
        ax.text(xi, ev/2, f'{ev:+.1f}pp', ha='center', va='center',
                fontsize=6.5, color='white', fontweight='bold')

    ax.set_xticks(xs_b)
    ax.set_xticklabels([SWAP_LABELS_FULL[s] for s in SWAP_ORDER], fontsize=7)
    style_ax(ax, title=title, ylim=(-18, 68), ylabel=False)
    ax.set_ylabel('Δ pp (CUED − UNCUED)', fontsize=7)

def draw_dfd_panel(ax, by_dfd, title=''):
    dep_positions = {'CUED': {'N': 0.0, 'F': 0.42}, 'UNCUED': {'N': 1.05, 'F': 1.47}}
    dep_colors_map = {'N': C_NEAR, 'F': C_FAR}
    cond_alphas    = {'CUED': 1.0, 'UNCUED': 0.75}

    for cond in ['CUED', 'UNCUED']:
        for dfd in ['N', 'F']:
            k, n_c = by_dfd.get((cond, dfd), [0, 0])
            x = dep_positions[cond][dfd]
            pp, lo, hi = draw_bar(ax, x, k, n_c, dep_colors_map[dfd],
                                  width=0.38, alpha=cond_alphas[cond])
            sc, _ = sig_vs_chance(k, n_c)
            sig_label_bar(ax, x, max(pp, hi), sc)
            bar_annotation(ax, x, k, n_c)

    ax.annotate('', xy=(0.80, -13), xytext=(-0.19, -13),
                arrowprops=dict(arrowstyle='-', color=C_CUED, lw=1.5))
    ax.annotate('', xy=(1.85, -13), xytext=(0.87, -13),
                arrowprops=dict(arrowstyle='-', color=C_UNCUED, lw=1.5))
    ax.text(0.21, -15.8, 'CUED',   ha='center', fontsize=8, color=C_CUED,   fontweight='bold')
    ax.text(1.36, -15.8, 'UNCUED', ha='center', fontsize=8, color=C_UNCUED, fontweight='bold')

    ax.set_xticks([0.0, 0.42, 1.05, 1.47])
    ax.set_xticklabels(['Near\n(N)', 'Far\n(F)', 'Near\n(N)', 'Far\n(F)'], fontsize=7.5)
    near_patch = mpatches.Patch(color=C_NEAR, label='Near (DelFieldDepth=N)')
    far_patch  = mpatches.Patch(color=C_FAR,  label='Far  (DelFieldDepth=F)')
    ax.legend(handles=[near_patch, far_patch], fontsize=6.5,
              loc='upper right', framealpha=0.9)
    style_ax(ax, title=title, ylim=(-18, 68))

def draw_table_panel(ax, main, SWAP_ORDER):
    ax.axis('off')
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
        if swap != SWAP_ORDER[-1]:
            table_rows.append(['','','','','','',''])

    col_widths = [0.22, 0.10, 0.08, 0.08, 0.12, 0.12, 0.12]
    xs_t = np.cumsum([0] + col_widths[:-1]) + 0.02
    y0   = 0.95
    lh   = 0.065

    for xi, (h, xpos) in enumerate(zip(headers, xs_t)):
        ax.text(xpos, y0, h, transform=ax.transAxes,
                fontsize=7, fontweight='bold', va='top', color='#222')
    ax.plot([0, 1], [y0 - lh*0.6]*2, color='#aaa', lw=0.8,
            transform=ax.transAxes, clip_on=False)

    row_colors = ['#EEF4FF', '#FFF4EE', '#EEF4FF', '#FFF4EE',
                  '#F0F8F0', '#F8F0F8', '#F0F8F0', '#F8F0F8']
    for ri, row in enumerate(table_rows):
        y = y0 - lh*(ri+1) - 0.01
        if all(c == '' for c in row):
            ax.plot([0.02, 0.98], [y + lh*0.3]*2, color='#ddd', lw=0.5,
                    transform=ax.transAxes, clip_on=False)
            continue
        bg = row_colors[ri % len(row_colors)]
        ax.axhspan(y - lh*0.45, y + lh*0.55, xmin=0.01, xmax=0.99,
                   facecolor=bg, alpha=0.5, transform=ax.transAxes)
        for xi, (cell, xpos) in enumerate(zip(row, xs_t)):
            color = '#222'
            if xi == 0:
                color = C_CUED if cell == 'CUED' else (C_UNCUED if cell == 'UNCUED' else '#222')
            ax.text(xpos, y, cell, transform=ax.transAxes,
                    fontsize=6.5, va='center', color=color)
    ax.set_title('E.  Accuracy table', fontsize=9, fontweight='bold', pad=4)

C_DEPTH_FC = '#1a6e8b'
C_COLOR_FC = '#8b5a1a'

def draw_field_cueing_panel(ax, fc_overall, fc_by_cond, title, factor_color):
    """Depth-field or color-field cueing panel.
    Two groups (cued✓, uncued✗), each split into Dot-CUED / Dot-UNCUED bars.
    """
    bar_w  = 0.30
    x_grp  = [0.0, 1.2]          # group centres
    offset = [-0.17, 0.17]        # CUED left, UNCUED right within each group

    for gi, grp in enumerate(('cued','uncued')):
        xc = x_grp[gi]
        for ci, (cond, col) in enumerate(zip(('CUED','UNCUED'), (C_CUED, C_UNCUED))):
            k, n = fc_by_cond[grp][cond]
            x = xc + offset[ci]
            pp, lo, hi = draw_bar(ax, x, k, n, col, width=bar_w, alpha=0.88,
                                  label=cond if gi == 0 else None)
            sc, _ = sig_vs_chance(k, n)
            sig_label_bar(ax, x, max(pp, hi), sc)
            bar_annotation(ax, x, k, n)

    # Overall field-cueing delta annotation
    kc, nc = fc_overall['cued']
    ku, nu = fc_overall['uncued']
    chi2v, p, _ = chi2_2x2(kc, nc, ku, nu)
    eff = acc_pp(kc, nc) - acc_pp(ku, nu)
    y_br = 59
    ax.annotate('', xy=(x_grp[1] - 0.30, y_br), xytext=(x_grp[0] + 0.30, y_br),
                arrowprops=dict(arrowstyle='<->', color=factor_color, lw=1.1))
    ax.text(0.60, y_br + 1.5, f'Δ={eff:+.1f}pp  {stars(p)}',
            ha='center', va='bottom', fontsize=7.5, color=factor_color, fontweight='bold')

    ax.set_xticks(x_grp)
    ax.set_xticklabels(['Field-cued ✓', 'Field-uncued ✗'], fontsize=8.5)
    style_ax(ax, title=title, ylim=(-18, 68))
    cued_p   = mpatches.Patch(color=C_CUED,   label='Dot-CUED')
    uncued_p = mpatches.Patch(color=C_UNCUED,  label='Dot-UNCUED')
    ax.legend(handles=[cued_p, uncued_p], fontsize=7, loc='upper right', framealpha=0.9)


def draw_three_factor_panel(ax, main, fc_depth, fc_color, title=''):
    """Summary: dot cueing, depth-field cueing, color-field cueing Δ side by side."""
    SWAP_ORDER = ['N', 'C', 'Z', 'CZ']
    # Dot cueing (overall)
    kc = sum(main.get(('CUED',   s), [0,0])[0] for s in SWAP_ORDER)
    nc = sum(main.get(('CUED',   s), [0,0])[1] for s in SWAP_ORDER)
    ku = sum(main.get(('UNCUED', s), [0,0])[0] for s in SWAP_ORDER)
    nu = sum(main.get(('UNCUED', s), [0,0])[1] for s in SWAP_ORDER)
    dot_eff = acc_pp(kc, nc) - acc_pp(ku, nu)
    _, dot_p, _ = chi2_2x2(kc, nc, ku, nu)

    # Depth-field cueing
    kd_c, nd_c = fc_depth['cued']
    kd_u, nd_u = fc_depth['uncued']
    dep_eff = acc_pp(kd_c, nd_c) - acc_pp(kd_u, nd_u)
    _, dep_p, _ = chi2_2x2(kd_c, nd_c, kd_u, nd_u)

    # Color-field cueing
    kco_c, nco_c = fc_color['cued']
    kco_u, nco_u = fc_color['uncued']
    col_eff = acc_pp(kco_c, nco_c) - acc_pp(kco_u, nco_u)
    _, col_p, _ = chi2_2x2(kco_c, nco_c, kco_u, nco_u)

    factors = ['Dot\ncueing', 'Depth-field\ncueing', 'Color-field\ncueing']
    effs    = [dot_eff, dep_eff, col_eff]
    ps      = [dot_p,   dep_p,   col_p]
    cols    = [C_CUED,  C_DEPTH_FC, C_COLOR_FC]

    xs = np.arange(3)
    for xi, (lbl, eff, p, col) in enumerate(zip(factors, effs, ps, cols)):
        ax.bar(xi, eff, 0.55, color=col, alpha=0.88, zorder=3,
               edgecolor='white', linewidth=0.5)
        y_lbl = eff + 1.5 if eff >= 0 else eff - 1.5
        va_lbl = 'bottom' if eff >= 0 else 'top'
        ax.text(xi, y_lbl, stars(p), ha='center', va=va_lbl, fontsize=9, color='#333')
        ax.text(xi, eff/2 if abs(eff) > 4 else eff + 3,
                f'{eff:+.1f}pp', ha='center', va='center',
                fontsize=7, color='white' if abs(eff) > 4 else '#333', fontweight='bold')

    ax.set_xticks(xs)
    ax.set_xticklabels(factors, fontsize=8)
    ax.set_ylabel('Δ pp (cued − uncued)', fontsize=7.5)
    style_ax(ax, title=title, ylim=(-18, 68), ylabel=True)
    ax.axhline(0, color='#888', lw=0.8, ls='--', zorder=2)


def make_figure_session(data, cueing_effects, out_path, session_label, subtitle):
    """Generic per-session figure (works for S1 and S2)."""
    n_valid = data['n_valid']
    main    = data['main']
    SWAP_ORDER    = data['SWAP_ORDER']
    fc_depth      = data['fc_depth']
    fc_color      = data['fc_color']
    fc_depth_dot  = data['fc_depth_dot']
    fc_color_dot  = data['fc_color_dot']

    fig = plt.figure(figsize=(14, 10))
    fig.patch.set_facecolor('white')
    fig.text(0.5, 0.978, f'{session_label}   (n={n_valid} trials)',
             ha='center', va='top', fontsize=12, fontweight='bold', color='#111')
    fig.text(0.5, 0.953, subtitle,
             ha='center', va='top', fontsize=8.5, color='#555')

    gs = gridspec.GridSpec(2, 3, top=0.920, bottom=0.09,
                           left=0.07, right=0.97, hspace=0.55, wspace=0.42)

    ax_a = fig.add_subplot(gs[0, 0:2])
    draw_main_panel(ax_a, main, SWAP_ORDER, cueing_effects,
                    title='A.  Accuracy by Condition × SwapType  [dot cueing]')

    ax_b = fig.add_subplot(gs[0, 2])
    draw_cueing_panel(ax_b, main, SWAP_ORDER, cueing_effects,
                      title='B.  Dot cueing Δ by SwapType')

    ax_c = fig.add_subplot(gs[1, 0])
    draw_field_cueing_panel(ax_c, fc_depth, fc_depth_dot,
                            title='C.  Depth-field cueing\n'
                                  '✓={CUED+N/C, UNCUED+Z/CZ}',
                            factor_color=C_DEPTH_FC)

    ax_d = fig.add_subplot(gs[1, 1])
    draw_field_cueing_panel(ax_d, fc_color, fc_color_dot,
                            title='D.  Color-field cueing\n'
                                  '✓={CUED+N/Z, UNCUED+C/CZ}',
                            factor_color=C_COLOR_FC)

    ax_e = fig.add_subplot(gs[1, 2])
    draw_table_panel(ax_e, main, SWAP_ORDER)

    fig.text(0.5, 0.025,
             'Error bars: 95% Wilson CI  |  Stars vs chance (12.5%): '
             '†p<.1  *p<.05  **p<.01  ***p<.001  |  '
             'Dot-cueing Δ = CUED − UNCUED  |  '
             'Field-cueing Δ = field-cued✓ − field-uncued✗  |  '
             'C=color swap, Z=depth swap, CZ=both, N=no swap',
             ha='center', va='bottom', fontsize=6, color='#666')

    os.makedirs(FIG_DIR, exist_ok=True)
    fig.savefig(out_path, dpi=150, bbox_inches='tight', facecolor='white')
    print(f"Saved: {out_path}")
    plt.close(fig)


# ── Figure 1: Session 2 alone ──────────────────────────────────────────────────
def make_figure_s2(data, cueing_effects):
    make_figure_session(
        data, cueing_effects, OUT_S2,
        session_label='DecoupledDots_Inv_005m — Session 260406_1754  (labels flipped to behavioral convention)',
        subtitle='delayTranslator=false  •  Cond labels inverted in raw file  •  '
                 'Swap types: N / C (color) / Z (depth) / CZ (color+depth)'
                 '  •  depth=0.05m  •  8-AFC  •  chance=12.5%')

# ── Figure 2: Combined ─────────────────────────────────────────────────────────
def make_figure_combined(data, cueing_effects,
                         title_line1=None, title_line2=None, out_path=None):
    n_valid      = data['n_valid']
    main         = data['main']
    SWAP_ORDER   = data['SWAP_ORDER']
    fc_depth     = data['fc_depth']
    fc_color     = data['fc_color']
    fc_depth_dot = data['fc_depth_dot']
    fc_color_dot = data['fc_color_dot']

    if title_line1 is None:
        title_line1 = (f'DecoupledDots — Combined Sessions 260406_1532 + 260406_1754   '
                       f'(n={n_valid} trials)')
    if title_line2 is None:
        title_line2 = ('Sessions: delayTranslator=true (1532) + delayTranslator=false/inverted (1754)  •  '
                       'Swap types: N / C (color) / Z (depth) / CZ (color+depth)'
                       '  •  depth=0.05m  •  8-AFC  •  chance=12.5%')
    if out_path is None:
        out_path = OUT_COMB

    fig = plt.figure(figsize=(16, 13))
    fig.patch.set_facecolor('white')

    fig.text(0.5, 0.984, title_line1,
             ha='center', va='top', fontsize=13, fontweight='bold', color='#111')
    fig.text(0.5, 0.960, title_line2,
             ha='center', va='top', fontsize=8.5, color='#555')

    # Row 0: main bars (3 wide) + dot cueing summary (1 wide)
    # Row 1: depth-field cueing (2 wide) + color-field cueing (2 wide)
    # Row 2: table (2 wide) + 3-factor summary (2 wide)
    gs = gridspec.GridSpec(3, 4, top=0.938, bottom=0.07,
                           left=0.07, right=0.97,
                           hspace=0.58, wspace=0.42)

    # ── Row 0: Dot cueing ─────────────────────────────────────────────────────
    ax_a = fig.add_subplot(gs[0, 0:3])
    draw_main_panel(ax_a, main, SWAP_ORDER, cueing_effects,
                    title='A.  Accuracy by Condition × SwapType  [dot cueing]')

    ax_b = fig.add_subplot(gs[0, 3])
    draw_cueing_panel(ax_b, main, SWAP_ORDER, cueing_effects,
                      title='B.  Dot cueing Δ\nby SwapType')

    # ── Row 1: Field cueing ───────────────────────────────────────────────────
    ax_c = fig.add_subplot(gs[1, 0:2])
    draw_field_cueing_panel(ax_c, fc_depth, fc_depth_dot,
                            title='C.  Depth-field cueing\n'
                                  '✓={CUED+N/C, UNCUED+Z/CZ}  ✗={CUED+Z/CZ, UNCUED+N/C}',
                            factor_color=C_DEPTH_FC)

    ax_d = fig.add_subplot(gs[1, 2:4])
    draw_field_cueing_panel(ax_d, fc_color, fc_color_dot,
                            title='D.  Color-field cueing\n'
                                  '✓={CUED+N/Z, UNCUED+C/CZ}  ✗={CUED+C/CZ, UNCUED+N/Z}',
                            factor_color=C_COLOR_FC)

    # ── Row 2: Table + 3-factor summary ──────────────────────────────────────
    ax_e = fig.add_subplot(gs[2, 0:2])
    draw_table_panel(ax_e, main, SWAP_ORDER)

    ax_f = fig.add_subplot(gs[2, 2:4])
    draw_three_factor_panel(ax_f, main, fc_depth, fc_color,
                            title='F.  Three-factor cueing summary\n(overall Δ each factor)')

    fig.text(0.5, 0.025,
             'Error bars: 95% Wilson CI  |  Stars vs chance (12.5%): '
             '†p<.1  *p<.05  **p<.01  ***p<.001  |  '
             'Dot-cueing Δ = CUED − UNCUED  |  Field-cueing Δ = field-cued✓ − field-uncued✗  |  '
             'C=color swap, Z=depth swap, CZ=both, N=no swap',
             ha='center', va='bottom', fontsize=6, color='#666')

    os.makedirs(FIG_DIR, exist_ok=True)
    fig.savefig(out_path, dpi=150, bbox_inches='tight', facecolor='white')
    print(f"Saved: {out_path}")
    plt.close(fig)


# ── Figure 3: Per-session comparison ──────────────────────────────────────────
def make_figure_sessions_comparison(session_list, out_path=None):
    """
    session_list: list of dicts with keys:
        label      — short label (e.g. 'S1\n260406_1532')
        asset      — asset name
        invert     — bool
        data       — aggregate() output
        cueing     — cueing_effects dict from print_summary
        anomaly    — str or None (footnote annotation)
    """
    if out_path is None:
        out_path = OUT_SESS_CMP

    n_sess = len(session_list)
    FACTORS = ['Dot\ncueing', 'Depth-field\ncueing', 'Color-field\ncueing']
    FCOLS   = [C_CUED, C_DEPTH_FC, C_COLOR_FC]
    SWAP_ORDER = ['N', 'C', 'Z', 'CZ']

    def _three_factor_effects(d):
        """Return [(eff_pp, p), ...] for dot/depth/color."""
        main     = d['main']
        fc_depth = d['fc_depth']
        fc_color = d['fc_color']

        kc  = sum(main.get(('CUED',   s), [0,0])[0] for s in SWAP_ORDER)
        nc  = sum(main.get(('CUED',   s), [0,0])[1] for s in SWAP_ORDER)
        ku  = sum(main.get(('UNCUED', s), [0,0])[0] for s in SWAP_ORDER)
        nu  = sum(main.get(('UNCUED', s), [0,0])[1] for s in SWAP_ORDER)
        dot_eff = acc_pp(kc, nc) - acc_pp(ku, nu)
        _, dot_p, _ = chi2_2x2(kc, nc, ku, nu)

        kd_c, nd_c = fc_depth['cued']
        kd_u, nd_u = fc_depth['uncued']
        dep_eff = acc_pp(kd_c, nd_c) - acc_pp(kd_u, nd_u)
        _, dep_p, _ = chi2_2x2(kd_c, nd_c, kd_u, nd_u)

        kco_c, nco_c = fc_color['cued']
        kco_u, nco_u = fc_color['uncued']
        col_eff = acc_pp(kco_c, nco_c) - acc_pp(kco_u, nco_u)
        _, col_p, _ = chi2_2x2(kco_c, nco_c, kco_u, nco_u)

        return [(dot_eff, dot_p), (dep_eff, dep_p), (col_eff, col_p)]

    # Group layout: each session is a cluster of 3 bars
    grp_width  = 0.9
    bar_width  = 0.25
    grp_gap    = 0.55
    offsets    = [-bar_width, 0, bar_width]  # dot / depth / color within group

    fig, ax = plt.subplots(figsize=(14, 5.5))
    fig.patch.set_facecolor('white')

    xtick_pos = []
    xtick_lbl = []

    for si, sess in enumerate(session_list):
        fxs = _three_factor_effects(sess['data'])
        n   = sess['data']['n_valid']
        x_grp = si * (grp_width + grp_gap)

        for fi, ((eff, p), fc, off) in enumerate(zip(fxs, FCOLS, offsets)):
            xb = x_grp + off
            s  = stars(p)
            ax.bar(xb, eff, bar_width * 0.88, color=fc, alpha=0.85, zorder=3,
                   edgecolor='white', linewidth=0.5,
                   label=FACTORS[fi] if si == 0 else None)
            # sig label
            y_lbl = eff + 1.5 if eff >= 0 else eff - 2.5
            va_lbl = 'bottom' if eff >= 0 else 'top'
            ax.text(xb, y_lbl, s, ha='center', va=va_lbl, fontsize=7.5, color='#333')
            # value label inside bar
            if abs(eff) > 5:
                ax.text(xb, eff / 2, f'{eff:+.0f}pp',
                        ha='center', va='center', fontsize=6, color='white', fontweight='bold')
            else:
                ax.text(xb, eff + (3 if eff >= 0 else -5), f'{eff:+.0f}pp',
                        ha='center', va='bottom', fontsize=6, color='#333')

        # anomaly marker
        if sess.get('anomaly'):
            ax.text(x_grp, -20, '⚠', ha='center', va='bottom', fontsize=11, color='#CC4400')

        xtick_pos.append(x_grp)
        xtick_lbl.append(f"{sess['label']}\n(n={n})")

    ax.axhline(0, color='#888', lw=0.8, ls='--', zorder=2)
    ax.set_xticks(xtick_pos)
    ax.set_xticklabels(xtick_lbl, fontsize=8.5)
    ax.set_ylabel('Δ pp (cued − uncued)', fontsize=9)
    ax.set_ylim(-24, 38)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.grid(axis='y', lw=0.4, alpha=0.4, zorder=0)

    # Legend
    patches = [mpatches.Patch(color=fc, label=lbl)
               for fc, lbl in zip(FCOLS, ['Dot cueing', 'Depth-field cueing', 'Color-field cueing'])]
    ax.legend(handles=patches, fontsize=8, loc='upper right', framealpha=0.9)

    # Anomaly footnotes
    notes = [s['anomaly'] for s in session_list if s.get('anomaly')]
    if notes:
        ax.text(0.01, 0.02, '⚠ ' + '  |  '.join(notes),
                transform=ax.transAxes, fontsize=7, color='#CC4400', va='bottom')

    fig.suptitle(
        'DecoupledDots — Per-session three-factor effects\n'
        '(bars = Dot / Depth-field / Color-field cueing Δpp within each session)',
        fontsize=11, fontweight='bold', y=1.01)

    os.makedirs(FIG_DIR, exist_ok=True)
    fig.savefig(out_path, dpi=150, bbox_inches='tight', facecolor='white')
    print(f"Saved: {out_path}")
    plt.close(fig)


# ── Main ──────────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    # ── Load all sessions ─────────────────────────────────────────────────────
    print("\nLoading Session 1 (260406_1532, DecoupledDots_005m, delayTranslator=true) ...")
    valid_s1 = load_data(DATA_S1, invert_cond=False)
    print(f"  → {len(valid_s1)} valid trials")

    print("Loading Session 2 (260406_1754, DecoupledDots_Inv_005m, delayTranslator=false, labels inverted) ...")
    valid_s2 = load_data(DATA_S2, invert_cond=True)
    print(f"  → {len(valid_s2)} valid trials (after label flip)")

    print("Loading Session 3 (260407_0643, DecoupledDots_Inv_005m, delayTranslator=false, labels inverted) ...")
    valid_s3 = load_data(DATA_S3, invert_cond=True)
    print(f"  → {len(valid_s3)} valid trials (after label flip)")

    print("Loading Session 4 (260407_0731, DecoupledDots_005m, delayTranslator=true) ...")
    valid_s4 = load_data(DATA_S4, invert_cond=False)
    print(f"  → {len(valid_s4)} valid trials")

    # ── Part A: Session 1 alone ────────────────────────────────────────────────
    data_s1 = aggregate(valid_s1)
    cueing_s1 = print_summary(
        data_s1,
        label='PART A: Session 1 alone — 260406_1532 (DecoupledDots_005m, delayTranslator=true)')
    make_figure_session(
        data_s1, cueing_s1, OUT_S1,
        session_label='DecoupledDots_005m — Session 260406_1532',
        subtitle='delayTranslator=true  •  '
                 'Swap types: N / C (color) / Z (depth) / CZ (color+depth)'
                 '  •  depth=0.05m  •  8-AFC  •  chance=12.5%')

    # ── Part B: Session 2 alone ────────────────────────────────────────────────
    data_s2 = aggregate(valid_s2)
    cueing_s2 = print_summary(
        data_s2,
        label='PART B: Session 2 alone — 260406_1754 (DecoupledDots_Inv_005m, labels flipped)')
    make_figure_s2(data_s2, cueing_s2)

    # ── Part C: Session 3 alone ────────────────────────────────────────────────
    data_s3 = aggregate(valid_s3)
    cueing_s3 = print_summary(
        data_s3,
        label='PART C: Session 3 alone — 260407_0643 (DecoupledDots_Inv_005m, labels flipped)')
    make_figure_session(
        data_s3, cueing_s3, OUT_S3,
        session_label='DecoupledDots_Inv_005m — Session 260407_0643  (labels flipped)',
        subtitle='delayTranslator=false  •  Cond labels inverted  •  '
                 'Swap types: N / C (color) / Z (depth) / CZ (color+depth)'
                 '  •  depth=0.05m  •  8-AFC  •  chance=12.5%')

    # ── Part D: Session 4 alone ────────────────────────────────────────────────
    data_s4 = aggregate(valid_s4)
    cueing_s4 = print_summary(
        data_s4,
        label='PART D: Session 4 alone — 260407_0731 (DecoupledDots_005m, delayTranslator=true)')
    make_figure_session(
        data_s4, cueing_s4, OUT_S4,
        session_label='DecoupledDots_005m — Session 260407_0731  [ANOMALOUS: flat dot cueing]',
        subtitle='delayTranslator=true  •  '
                 'Dot cueing anomalously low (+4.8pp n.s.) — elevated UNCUED, not depressed CUED  •  '
                 'Noted: ±22.5° criterion difficulty; mild jerky-motion sensation; no post-hoc exclusion criterion  •  '
                 'depth=0.05m  •  8-AFC  •  chance=12.5%')

    # ── Part E: S1+S2 Combined (original 2-session figure) ────────────────────
    valid_comb12 = valid_s1 + valid_s2
    data_comb12  = aggregate(valid_comb12)
    cueing_comb12 = print_summary(
        data_comb12,
        label='PART E: Combined S1+S2 — 260406_1532 + 260406_1754  (n≈1026 trials)')
    make_figure_combined(data_comb12, cueing_comb12)   # writes OUT_COMB (original)

    # ── Part F: All 4 sessions combined ───────────────────────────────────────
    valid_comb4 = valid_s1 + valid_s2 + valid_s3 + valid_s4
    data_comb4  = aggregate(valid_comb4)
    cueing_comb4 = print_summary(
        data_comb4,
        label='PART F: Combined S1+S2+S3+S4 — all 4 sessions')
    n4 = data_comb4['n_valid']
    make_figure_combined(
        data_comb4, cueing_comb4,
        title_line1=(f'DecoupledDots — Combined S1+S2+S3+S4   (n={n4} trials)'),
        title_line2=('Sessions: 260406_1532(DT) + 260406_1754(DTinv) + '
                     '260407_0643(DTinv) + 260407_0731(DT)  •  '
                     'S4 anomalous (flat cueing, elevated UNCUED)  •  '
                     'depth=0.05m  •  8-AFC  •  chance=12.5%'),
        out_path=OUT_COMB4)

    # ── Part G: Per-session comparison figure ─────────────────────────────────
    session_list = [
        dict(label='S1\n260406_1532\nDT_005m',
             data=data_s1, cueing=cueing_s1, anomaly=None),
        dict(label='S2\n260406_1754\nDTinv_005m',
             data=data_s2, cueing=cueing_s2, anomaly=None),
        dict(label='S3\n260407_0643\nDTinv_005m',
             data=data_s3, cueing=cueing_s3, anomaly=None),
        dict(label='S4\n260407_0731\nDT_005m',
             data=data_s4, cueing=cueing_s4,
             anomaly='S4: dot cueing flat (+4.8pp n.s.); elevated UNCUED, '
                     'not depressed CUED; ±22.5° criterion difficulty noted; '
                     'jerky motion sensation; included (no pre-defined exclusion criterion)'),
    ]
    make_figure_sessions_comparison(session_list)

    print("\nDone.")
    print(f"  Individual: {OUT_S1}")
    print(f"             {OUT_S2}")
    print(f"             {OUT_S3}")
    print(f"             {OUT_S4}")
    print(f"  Combined (S1+S2):    {OUT_COMB}")
    print(f"  Combined (S1–S4):    {OUT_COMB4}")
    print(f"  Session comparison:  {OUT_SESS_CMP}")
