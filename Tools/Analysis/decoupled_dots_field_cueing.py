#!/usr/bin/env python3
"""
Depth-field cueing and color-field cueing analysis for combined DecoupledDots data.

Depth-field cueing: did the delayed-onset field first appear in the same
depth plane where translation eventually occurred?
  Cued  ✓ = {CUED+N, CUED+C, UNCUED+Z, UNCUED+CZ}
  Uncued✗ = {CUED+Z, CUED+CZ, UNCUED+N, UNCUED+C}

Color-field cueing: at the time of translation, did the translating dots
share the color of the delayed field's original (pre-swap) color?
  Cued  ✓ = {CUED+N, CUED+Z, UNCUED+C, UNCUED+CZ}
  Uncued✗ = {CUED+C, CUED+CZ, UNCUED+N, UNCUED+Z}

Sessions:
  260406_1532  DecoupledDots_005m      (delayTranslator=1, labels normal)
  260406_1754  DecoupledDots_Inv_005m  (delayTranslator=0, labels INVERTED)

Output: Agents/Figures/decoupled_dots_field_cueing.png
"""

import csv, collections, math, os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from scipy.stats import chi2_contingency

# ── Paths ──────────────────────────────────────────────────────────────────────
DATA_S1 = "/tmp/quest_pull2/files/vr_dots_session_260406_1532.tsv"
DATA_S2 = "/tmp/quest_pull2/files/vr_dots_session_260406_1754.tsv"

OUT = os.path.expanduser(
    "~/Projects/ObjectBasedAttention/VRDots/Agents/Figures/"
    "decoupled_dots_field_cueing.png")

CHANCE = 1/8

# ── Factor membership ──────────────────────────────────────────────────────────
# depth_field_cued[cond][swap] = True if depth-cued, False if depth-uncued
DEPTH_FIELD_CUED = {
    'CUED':   {'N': True,  'C': True,  'Z': False, 'CZ': False},
    'UNCUED': {'N': False, 'C': False, 'Z': True,  'CZ': True},
}

# color_field_cued[cond][swap] = True if color-cued
COLOR_FIELD_CUED = {
    'CUED':   {'N': True,  'C': False, 'Z': True,  'CZ': False},
    'UNCUED': {'N': False, 'C': True,  'Z': False, 'CZ': True},
}

# ── Stats helpers ──────────────────────────────────────────────────────────────
def normal_cdf(x):
    return 0.5 * (1 + math.erf(x / math.sqrt(2)))

def chi2_2x2(k1, n1, k2, n2):
    table = [[k1, n1-k1], [k2, n2-k2]]
    chi2, p, dof, _ = chi2_contingency(table, correction=False)
    return chi2, p

def stars(p):
    return '***' if p < .001 else '**' if p < .01 else '*' if p < .05 else '†' if p < .1 else 'n.s.'

def acc_pp(k, n):
    return (k/n - CHANCE) * 100 if n else 0.0

def wilson_ci(k, n, z=1.96):
    if n == 0:
        return 0.0, 0.0
    p = k/n
    d = 1 + z**2/n
    c = (p + z**2/(2*n)) / d
    hw = z * math.sqrt(p*(1-p)/n + z**2/(4*n**2)) / d
    return c-hw, c+hw

def ci_pp(k, n):
    lo, hi = wilson_ci(k, n)
    return (lo - CHANCE)*100, (hi - CHANCE)*100

# ── Data loading ───────────────────────────────────────────────────────────────
def is_correct(td, rd):
    d = (float(rd) - float(td) + 360) % 360
    return (360 - d if d > 180 else d) <= 22.5

def load(path, invert=False):
    with open(path, newline='') as f:
        rows = list(csv.DictReader(f, delimiter='\t'))
    valid = [r for r in rows
             if r.get('TransDeg','').strip() and r.get('RespDeg','').strip()
             and r.get('EndKey','') not in ('timeout', 'skip', 'requeue')]
    for r in valid:
        if invert:
            r['Cond'] = 'UNCUED' if r['Cond'] == 'CUED' else 'CUED'
        r['correct'] = int(is_correct(r['TransDeg'], r['RespDeg']))
    return valid

# ── Aggregate by factor ────────────────────────────────────────────────────────
def aggregate(trials):
    """Returns dict with depth-field and color-field cueing counts."""
    depth = {'cued': [0,0], 'uncued': [0,0]}   # [correct, total]
    color = {'cued': [0,0], 'uncued': [0,0]}
    # Also break down by dot-cueing within each field-cueing group
    depth_by_dot = {'cued': {'CUED':[0,0],'UNCUED':[0,0]},
                    'uncued': {'CUED':[0,0],'UNCUED':[0,0]}}
    color_by_dot = {'cued': {'CUED':[0,0],'UNCUED':[0,0]},
                    'uncued': {'CUED':[0,0],'UNCUED':[0,0]}}

    for r in trials:
        cond = r['Cond']
        swap = r['SwapType']
        corr = r['correct']
        if cond not in ('CUED','UNCUED') or swap not in ('N','C','Z','CZ'):
            continue

        dc = 'cued' if DEPTH_FIELD_CUED[cond][swap] else 'uncued'
        cc = 'cued' if COLOR_FIELD_CUED[cond][swap]  else 'uncued'

        depth[dc][0] += corr;  depth[dc][1] += 1
        color[cc][0] += corr;  color[cc][1] += 1

        depth_by_dot[dc][cond][0] += corr;  depth_by_dot[dc][cond][1] += 1
        color_by_dot[cc][cond][0] += corr;  color_by_dot[cc][cond][1] += 1

    return depth, color, depth_by_dot, color_by_dot

# ── Main ───────────────────────────────────────────────────────────────────────
trials = load(DATA_S1, invert=False) + load(DATA_S2, invert=True)
print(f"Combined trials: {len(trials)}")

depth, color, depth_by_dot, color_by_dot = aggregate(trials)

# ── Print results ──────────────────────────────────────────────────────────────
def print_factor(label, d):
    kc, nc = d['cued']
    ku, nu = d['uncued']
    chi2, p = chi2_2x2(kc, nc, ku, nu)
    eff = acc_pp(kc, nc) - acc_pp(ku, nu)
    print(f"\n  {label}")
    print(f"    Cued  ✓: {kc}/{nc} = {kc/nc*100:.1f}%  (+{acc_pp(kc,nc):.1f}pp above chance)")
    print(f"    Uncued✗: {ku}/{nu} = {ku/nu*100:.1f}%  (+{acc_pp(ku,nu):.1f}pp above chance)")
    print(f"    Cueing Δ = {eff:+.1f}pp   χ²={chi2:.2f}  {stars(p)}  (p={p:.4f})")

print("\n" + "="*60)
print("  FIELD-CUEING ANALYSIS — Combined DecoupledDots (n=1026)")
print("="*60)
print_factor("DEPTH-FIELD CUEING", depth)
print_factor("COLOR-FIELD CUEING", color)

print("\n  Breakdown by dot-cueing within each depth-field group:")
for fc in ('cued','uncued'):
    kc, nc = depth_by_dot[fc]['CUED']
    ku, nu = depth_by_dot[fc]['UNCUED']
    eff = acc_pp(kc, nc) - acc_pp(ku, nu)
    chi2, p = chi2_2x2(kc, nc, ku, nu) if nc and nu else (0, 1)
    print(f"    Depth {'cued✓' if fc=='cued' else 'uncued✗'}:  "
          f"CUED={acc_pp(kc,nc):+.1f}pp  UNCUED={acc_pp(ku,nu):+.1f}pp  "
          f"Dot-cueing Δ={eff:+.1f}pp  {stars(p)}")

print("\n  Breakdown by dot-cueing within each color-field group:")
for fc in ('cued','uncued'):
    kc, nc = color_by_dot[fc]['CUED']
    ku, nu = color_by_dot[fc]['UNCUED']
    eff = acc_pp(kc, nc) - acc_pp(ku, nu)
    chi2, p = chi2_2x2(kc, nc, ku, nu) if nc and nu else (0, 1)
    print(f"    Color {'cued✓' if fc=='cued' else 'uncued✗'}:  "
          f"CUED={acc_pp(kc,nc):+.1f}pp  UNCUED={acc_pp(ku,nu):+.1f}pp  "
          f"Dot-cueing Δ={eff:+.1f}pp  {stars(p)}")

# ── Figure ─────────────────────────────────────────────────────────────────────
C_DEPTH  = '#1a6e8b'
C_COLOR  = '#8b5a1a'
C_CUED   = '#1a3a8b'
C_UNCUED = '#884400'

fig, axes = plt.subplots(1, 2, figsize=(10, 5))
fig.patch.set_facecolor('white')
fig.suptitle(
    'Field-Cueing Effects — Combined DecoupledDots\n'
    '(n ≈ 1026; Sessions 260406_1532 + 260406_1754)',
    fontsize=11, fontweight='bold', y=1.01)

def bar_pair(ax, data_dict, by_dot, fc_label, factor_color,
             conditions, cond_labels, cond_colors, title):
    """Draw bars for cued vs uncued groups with dot-cueing breakdown."""
    # Outer groups: field-cued ✓ vs ✗
    groups = ['cued', 'uncued']
    glabels = ['Field-cued ✓', 'Field-uncued ✗']

    # For each group, show overall + CUED dot + UNCUED dot
    x_base = np.array([0.0, 1.6])
    bar_w  = 0.22
    offsets = [-0.24, 0.0, 0.24]   # overall, CUED, UNCUED
    sub_labels = ['Overall', 'Dot-CUED', 'Dot-UNCUED']
    sub_colors = [factor_color, C_CUED, C_UNCUED]
    sub_alpha  = [1.0, 0.75, 0.75]

    bars_drawn = []
    for gi, grp in enumerate(groups):
        k_ov, n_ov = data_dict[grp]
        k_dc, n_dc = by_dot[grp]['CUED']
        k_du, n_du = by_dot[grp]['UNCUED']
        vals  = [acc_pp(k, n) for k,n in [(k_ov,n_ov),(k_dc,n_dc),(k_du,n_du)]]
        cis   = [ci_pp(k, n)  for k,n in [(k_ov,n_ov),(k_dc,n_dc),(k_du,n_du)]]

        for bi, (val, ci, sc, sa, sl) in enumerate(
                zip(vals, cis, sub_colors, sub_alpha, sub_labels)):
            x = x_base[gi] + offsets[bi]
            lo, hi = ci
            err_lo = val - lo
            err_hi = hi - val
            b = ax.bar(x, val, width=bar_w, color=sc, alpha=sa,
                       edgecolor='white', linewidth=0.5, zorder=3)
            ax.errorbar(x, val, yerr=[[err_lo],[err_hi]],
                        fmt='none', color='#333', capsize=3, lw=1, zorder=4)
            if gi == 0:
                bars_drawn.append((b, sl))

    ax.axhline(0, color='#AAAAAA', lw=0.8, ls='--', zorder=1)
    ax.set_xticks(x_base)
    ax.set_xticklabels(glabels, fontsize=10)
    ax.set_ylabel('Accuracy above chance (pp)', fontsize=9)
    ax.set_ylim(-5, 55)
    ax.set_title(title, fontsize=11, fontweight='bold', color=factor_color)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.tick_params(axis='both', labelsize=9)

    # Cueing effect annotation
    k_c1, n_c1 = data_dict['cued']
    k_c2, n_c2 = data_dict['uncued']
    chi2v, pv = chi2_2x2(k_c1, n_c1, k_c2, n_c2)
    eff = acc_pp(k_c1, n_c1) - acc_pp(k_c2, n_c2)
    ax.annotate(
        f'Field-cued ✓ vs ✗\nΔ = {eff:+.1f}pp  {stars(pv)}',
        xy=(0.5, 0.92), xycoords='axes fraction',
        ha='center', fontsize=8.5, color=factor_color,
        bbox=dict(boxstyle='round,pad=0.3', fc='white', ec=factor_color, lw=0.8))

    # Legend
    legend_els = [
        mpatches.Patch(facecolor=factor_color, label='Overall'),
        mpatches.Patch(facecolor=C_CUED, alpha=0.75, label='Dot-CUED'),
        mpatches.Patch(facecolor=C_UNCUED, alpha=0.75, label='Dot-UNCUED'),
    ]
    ax.legend(handles=legend_els, fontsize=7.5, loc='upper right',
              framealpha=0.9, edgecolor='#CCC')

bar_pair(axes[0], depth, depth_by_dot, 'depth', C_DEPTH,
         ['CUED','UNCUED'], ['CUED','UNCUED'], [C_CUED, C_UNCUED],
         'Depth-Field Cueing\n'
         '✓ = {CUED+N, CUED+C, UNCUED+Z, UNCUED+CZ}\n'
         '✗ = {CUED+Z, CUED+CZ, UNCUED+N, UNCUED+C}')

bar_pair(axes[1], color, color_by_dot, 'color', C_COLOR,
         ['CUED','UNCUED'], ['CUED','UNCUED'], [C_CUED, C_UNCUED],
         'Color-Field Cueing\n'
         '✓ = {CUED+N, CUED+Z, UNCUED+C, UNCUED+CZ}\n'
         '✗ = {CUED+C, CUED+CZ, UNCUED+N, UNCUED+Z}')

plt.tight_layout(rect=[0,0,1,0.96])
os.makedirs(os.path.dirname(OUT), exist_ok=True)
fig.savefig(OUT, dpi=150, bbox_inches='tight', facecolor='white')
print(f"\nSaved: {OUT}")
