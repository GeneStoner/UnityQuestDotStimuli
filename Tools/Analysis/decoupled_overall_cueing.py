#!/usr/bin/env python3
"""
decoupled_overall_cueing.py

Overall cueing effect for each cue type, pooled across all 4 swap conditions.
Combined clean sessions: 260413_2051 (n=512) + 260414_0922 Q3+Q4 (~250).

For each cue type, the "cued arm" is whichever of CUED/UNCUED has the
translation in the cue plane:
  Dot:   cued arm = CUED always
  Depth: cued arm = CUED for N,C  |  UNCUED for Z,CZ
  Color: cued arm = CUED for N,Z  |  UNCUED for C,CZ

Overall effect = accuracy(cued arm pooled across all 4 swap conditions)
              − accuracy(uncued arm pooled across all 4 swap conditions)

Output:
  Agents/SwapPilot/Figures/decoupled_overall_cueing.png
"""

import csv, math, os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.stats import chi2_contingency

BASE = os.path.normpath(os.path.join(
    os.path.dirname(__file__), '../../Agents/SwapPilot/Figures'))
os.makedirs(BASE, exist_ok=True)
OUT = os.path.join(BASE, 'decoupled_overall_cueing.png')

SESSIONS = [
    ('/tmp/quest_pull7/files/vr_dots_session_260413_2051.tsv', None),
    ('/tmp/quest_pull7/files/vr_dots_session_260414_0922.tsv', 263),
]

CHANCE = 1/8
SWAPS  = ['N', 'C', 'Z', 'CZ']

DEPTH_CUED_IS_CUED = {'N': True,  'C': True,  'Z': False, 'CZ': False}
COLOR_CUED_IS_CUED = {'N': True,  'C': False, 'Z': True,  'CZ': False}

def is_correct(td, rd):
    d = (float(rd) - float(td) + 360) % 360
    return (360 - d if d > 180 else d) <= 22.5

def pct(k, n): return k/n*100 if n > 0 else 0.0

def wilson_ci(k, n, z=1.96):
    if n == 0: return 0.0, 0.0
    p = k/n; denom = 1 + z**2/n
    c  = (p + z**2/(2*n)) / denom
    hw = z * math.sqrt(p*(1-p)/n + z**2/(4*n**2)) / denom
    return (c-hw)*100, (c+hw)*100

def chi2_p(k1, n1, k2, n2):
    if n1==0 or n2==0: return float('nan')
    _, pv, _, _ = chi2_contingency([[k1,n1-k1],[k2,n2-k2]], correction=False)
    return pv

def stars(p):
    if p is None or (isinstance(p,float) and math.isnan(p)): return ''
    return '***' if p<.001 else '**' if p<.01 else '*' if p<.05 else '†' if p<.1 else 'n.s.'

# ── Load ───────────────────────────────────────────────────────────────────────

rows = []
for path, min_trial in SESSIONS:
    trial_num = 0
    with open(path, newline='') as f:
        for r in csv.DictReader(f, delimiter='\t'):
            if not r.get('TransDeg','').strip() or not r.get('RespDeg','').strip(): continue
            if r.get('EndKey','') in ('timeout','skip','requeue'): continue
            trial_num += 1
            if min_trial and trial_num < min_trial: continue
            rows.append(dict(
                cond    = r['Cond'],
                swap    = r['SwapType'],
                correct = int(is_correct(r['TransDeg'], r['RespDeg']))
            ))

n_total = len(rows)

def cell(filt):
    sub = [r for r in rows if filt(r)]
    return sum(r['correct'] for r in sub), len(sub)

cued   = {s: cell(lambda r,s=s: r['cond']=='CUED'   and r['swap']==s) for s in SWAPS}
uncued = {s: cell(lambda r,s=s: r['cond']=='UNCUED' and r['swap']==s) for s in SWAPS}

# ── Pool across all 4 swap conditions for each cue type ───────────────────────

def overall_effect(cued_arm_map):
    """
    cued_arm_map: dict swap -> True (cued arm = CUED) or False (cued arm = UNCUED)
    Returns: delta, k_cued, n_cued, k_uncued, n_uncued
    """
    k_c = n_c = k_u = n_u = 0
    for s in SWAPS:
        if cued_arm_map[s]:
            kc, nc = cued[s];   ku, nu = uncued[s]
        else:
            kc, nc = uncued[s]; ku, nu = cued[s]
        k_c += kc; n_c += nc
        k_u += ku; n_u += nu
    return pct(k_c,n_c) - pct(k_u,n_u), k_c, n_c, k_u, n_u

dot_all   = {s: True for s in SWAPS}
depth_all = DEPTH_CUED_IS_CUED
color_all = COLOR_CUED_IS_CUED

results = {
    'Dot\ncueing':   overall_effect(dot_all),
    'Depth\ncueing': overall_effect(depth_all),
    'Color\ncueing': overall_effect(color_all),
}

print(f"\nCombined clean n={n_total}")
print(f"\n{'Cue type':15s}  {'Cued arm %':>10s}  {'Uncued arm %':>12s}  {'Delta':>8s}  {'p':>6s}")
for lbl, (delta, kc, nc, ku, nu) in results.items():
    pv = chi2_p(kc, nc, ku, nu)
    print(f"  {lbl.replace(chr(10),' '):13s}  {pct(kc,nc):6.1f}% ({kc}/{nc})  "
          f"{pct(ku,nu):6.1f}% ({ku}/{nu})  {delta:+6.1f}pp  {stars(pv)}")

# ── Figure ─────────────────────────────────────────────────────────────────────

fig, ax = plt.subplots(figsize=(7, 6))
fig.patch.set_facecolor('white')

labels  = list(results.keys())
colors  = ['#1a5276', '#1d6a4a', '#6e2f8e']
xs = np.arange(len(labels))

for i, (lbl, (delta, kc, nc, ku, nu)) in enumerate(results.items()):
    lo_c, hi_c = wilson_ci(kc, nc)
    lo_u, hi_u = wilson_ci(ku, nu)
    pc, pu = pct(kc,nc), pct(ku,nu)
    err_lo = delta - ((pc - lo_c) + (hi_u - pu))
    err_hi = (hi_c - pc) + (pu - lo_u)

    ax.bar(xs[i], delta, 0.55, color=colors[i], alpha=0.87, zorder=3,
           edgecolor='white', lw=0.5)
    ax.errorbar(xs[i], delta,
                yerr=[[max(0, delta - err_lo)], [max(0, err_hi)]],
                fmt='none', color='#333', capsize=6, capthick=1.3, lw=1.5, zorder=4)

    pv = chi2_p(kc, nc, ku, nu)
    s  = stars(pv)
    y_lbl = max(delta, 0) + err_hi + 1.5
    ax.text(xs[i], y_lbl, s, ha='center', va='bottom', fontsize=13,
            color='#222', fontweight='bold')

    # value label inside/outside bar
    if abs(delta) > 6:
        ax.text(xs[i], delta/2, f'{delta:+.1f}pp',
                ha='center', va='center', fontsize=11,
                color='white', fontweight='bold')
    else:
        off = 2.5 if delta >= 0 else -2.5
        ax.text(xs[i], delta + off, f'{delta:+.1f}pp',
                ha='center', va='bottom' if delta >= 0 else 'top',
                fontsize=11, color='#333', fontweight='bold')

ax.axhline(0, color='#888', lw=1.0, zorder=1)
ax.set_xticks(xs)
ax.set_xticklabels(labels, fontsize=12)
ax.set_ylim(-15, 50)
ax.set_ylabel('Overall cueing effect (pp)', fontsize=11)
ax.set_title(
    f'Overall cueing effect by cue type\n'
    f'Combined clean sessions  ·  n={n_total}  ·  pooled across N, C, Z, CZ',
    fontsize=11, fontweight='bold', pad=10)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.grid(axis='y', lw=0.5, alpha=0.35, zorder=0)

fig.text(0.5, 0.01,
         'Effect = accuracy(translation-in-cue-plane arm) − accuracy(other arm), pooled across all 4 swap conditions\n'
         'Dot: cued arm always = CUED  ·  Depth/Color: cued arm = whichever has translation in cue plane\n'
         'Error bars: propagated Wilson 95% CI  ·  χ² significance  ·  †p<.1  *p<.05  **p<.01  ***p<.001',
         ha='center', fontsize=7.5, color='#555')

plt.tight_layout(rect=[0, 0.08, 1, 1])
plt.savefig(OUT, dpi=150, bbox_inches='tight', facecolor='white')
print(f"\nSaved: {OUT}")
