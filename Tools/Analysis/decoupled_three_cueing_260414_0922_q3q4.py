#!/usr/bin/env python3
"""
decoupled_three_cueing_260414_0922_q3q4.py

3-panel cueing figure for session 260414_0922, Q3+Q4 only (trial >= 263).
Q1 contaminated by early re-don before tracking stabilized; Q3+Q4 clean.

All three panels show cueing-effect delta bars (cued-arm minus uncued-arm).
The "cued arm" for each cueing type is whichever of CUED/UNCUED has the
translation in the cue plane:

  Dot cueing:   always CUED − UNCUED
  Depth cueing: CUED−UNCUED for N,C  |  UNCUED−CUED for Z,CZ
  Color cueing: CUED−UNCUED for N,Z  |  UNCUED−CUED for C,CZ

In the N condition all three cueing types agree (CUED−UNCUED throughout).

Output:
  Agents/SwapPilot/Figures/decoupled_three_cueing_260414_0922_q3q4.png
"""

import csv, math, os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.stats import chi2_contingency

DATA = "/tmp/vr_dots_session_260414_0922.tsv"
Q3Q4_TRIAL_START = 263

BASE = os.path.normpath(os.path.join(
    os.path.dirname(__file__), '../../Agents/SwapPilot/Figures'))
os.makedirs(BASE, exist_ok=True)
OUT = os.path.join(BASE, 'decoupled_three_cueing_260414_0922_q3q4.png')

CHANCE = 1 / 8
SWAPS = ['N', 'C', 'Z', 'CZ']
SWAP_LABELS = {'N': 'N\n(baseline)', 'C': 'C\n(color\nswap)',
               'Z': 'Z\n(depth\nswap)', 'CZ': 'CZ\n(both\nswap)'}

# For each swap condition, which arm has translation in the cue plane?
# True  → cued arm is CUED   → delta = CUED − UNCUED
# False → cued arm is UNCUED → delta = UNCUED − CUED
DEPTH_CUED_IS_CUED = {'N': True,  'C': True,  'Z': False, 'CZ': False}
COLOR_CUED_IS_CUED = {'N': True,  'C': False, 'Z': True,  'CZ': False}

# ── Stats ──────────────────────────────────────────────────────────────────────

def is_correct(td, rd):
    d = (float(rd) - float(td) + 360) % 360
    return (360 - d if d > 180 else d) <= 22.5

def pct(k, n): return k/n*100 if n > 0 else 0.0

def wilson_ci(k, n, z=1.96):
    if n == 0: return 0.0, 0.0
    p = k/n; denom = 1 + z**2/n
    c  = (p + z**2/(2*n)) / denom
    hw = z * math.sqrt(p*(1-p)/n + z**2/(4*n**2)) / denom
    return (c - hw)*100, (c + hw)*100

def chi2_p(k1, n1, k2, n2):
    if n1 == 0 or n2 == 0: return float('nan')
    _, pval, _, _ = chi2_contingency([[k1, n1-k1],[k2, n2-k2]], correction=False)
    return pval

def stars(p):
    if p is None or (isinstance(p, float) and math.isnan(p)): return ''
    return '***' if p<.001 else '**' if p<.01 else '*' if p<.05 else '†' if p<.1 else 'n.s.'

# ── Load — Q3+Q4 only ─────────────────────────────────────────────────────────

rows = []
trial_num = 0
with open(DATA, newline='') as f:
    for r in csv.DictReader(f, delimiter='\t'):
        if not r.get('TransDeg','').strip() or not r.get('RespDeg','').strip():
            continue
        if r.get('EndKey','') in ('timeout','skip','requeue'):
            continue
        trial_num += 1
        if trial_num < Q3Q4_TRIAL_START:
            continue
        rows.append(dict(
            cond    = r['Cond'],
            swap    = r['SwapType'],
            correct = int(is_correct(r['TransDeg'], r['RespDeg']))
        ))

n_total = len(rows)

def cell(filt):
    sub = [r for r in rows if filt(r)]
    k = sum(r['correct'] for r in sub)
    return k, len(sub)

cued   = {s: cell(lambda r,s=s: r['cond']=='CUED'   and r['swap']==s) for s in SWAPS}
uncued = {s: cell(lambda r,s=s: r['cond']=='UNCUED' and r['swap']==s) for s in SWAPS}

def cueing_delta(swap, cued_is_cued):
    """Return (delta, k_cued_arm, n_cued_arm, k_uncued_arm, n_uncued_arm)."""
    if cued_is_cued:
        kc, nc = cued[swap]; ku, nu = uncued[swap]
    else:
        kc, nc = uncued[swap]; ku, nu = cued[swap]   # flip: UNCUED is the cued arm
    return pct(kc,nc) - pct(ku,nu), kc, nc, ku, nu

# ── Print summary ──────────────────────────────────────────────────────────────

print(f"\nSession 260414_0922 — Q3+Q4 (n={n_total})")
print(f"{'Swap':4s}  {'Dot cueing':>18s}  {'Depth cueing':>18s}  {'Color cueing':>18s}")
for s in SWAPS:
    d_dot,   kd1,nd1,kd2,nd2 = cueing_delta(s, True)
    d_depth, kz1,nz1,kz2,nz2 = cueing_delta(s, DEPTH_CUED_IS_CUED[s])
    d_color, kc1,nc1,kc2,nc2 = cueing_delta(s, COLOR_CUED_IS_CUED[s])
    arm_d = '(C-U)' if DEPTH_CUED_IS_CUED[s] else '(U-C)'
    arm_c = '(C-U)' if COLOR_CUED_IS_CUED[s] else '(U-C)'
    print(f"  {s:2s}:  dot={d_dot:+.1f}pp {stars(chi2_p(kd1,nd1,kd2,nd2)):5s}  "
          f"depth={arm_d}{d_depth:+.1f}pp {stars(chi2_p(kz1,nz1,kz2,nz2)):5s}  "
          f"color={arm_c}{d_color:+.1f}pp {stars(chi2_p(kc1,nc1,kc2,nc2)):5s}")

# ── Figure ─────────────────────────────────────────────────────────────────────

fig, axes = plt.subplots(1, 3, figsize=(15, 6))
fig.patch.set_facecolor('white')
fig.suptitle(
    f'Session 260414_0922  ·  DecoupledDots_005m_v2  ·  Q3+Q4 clean  ·  n={n_total}\n'
    'All panels: cueing effect = (translation-in-cue-plane arm) − (other arm)',
    fontsize=11, fontweight='bold', y=1.01)

YLIM = (-55, 75)

def style(ax, title, ylabel=''):
    ax.axhline(0, color='#888', lw=0.9, zorder=1)
    ax.set_ylim(*YLIM)
    ax.set_title(title, fontsize=10, fontweight='bold', pad=8)
    ax.set_ylabel(ylabel, fontsize=9)
    ax.tick_params(labelsize=9)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.grid(axis='y', lw=0.4, alpha=0.3, zorder=0)

def draw_delta_bar(ax, x, delta, k1, n1, k2, n2, color, width=0.55):
    lo1, hi1 = wilson_ci(k1, n1)
    lo2, hi2 = wilson_ci(k2, n2)
    p1, p2 = pct(k1,n1), pct(k2,n2)
    err_lo = delta - ((p1 - lo1) + (hi2 - p2))
    err_hi = (hi1 - p1) + (p2 - lo2)
    ax.bar(x, delta, width, color=color, alpha=0.85, zorder=3,
           edgecolor='white', linewidth=0.5)
    ax.errorbar(x, delta, yerr=[[max(0, delta - err_lo)],[max(0, err_hi)]],
                fmt='none', color='#333', capsize=4, capthick=1.1, lw=1.2, zorder=4)
    pv = chi2_p(k1, n1, k2, n2)
    s = stars(pv)
    y_lbl = max(delta, 0) + err_hi + 1.5
    ax.text(x, y_lbl, s, ha='center', va='bottom', fontsize=9,
            color='#222', fontweight='bold')
    if abs(delta) > 8:
        ax.text(x, delta/2, f'{delta:+.1f}pp', ha='center', va='center',
                fontsize=8, color='white', fontweight='bold')
    else:
        ax.text(x, delta + (3 if delta >= 0 else -3), f'{delta:+.1f}pp',
                ha='center', va='bottom' if delta >= 0 else 'top',
                fontsize=8, color='#333', fontweight='bold')

xs = np.arange(len(SWAPS))

# ── Panel A: Dot cueing — always CUED − UNCUED ────────────────────────────────

ax = axes[0]
dot_colors = ['#1a5276', '#5dade2', '#154360', '#85c1e9']
for i, swap in enumerate(SWAPS):
    delta, k1,n1,k2,n2 = cueing_delta(swap, True)
    draw_delta_bar(ax, xs[i], delta, k1,n1,k2,n2, dot_colors[i])
ax.set_xticks(xs); ax.set_xticklabels([SWAP_LABELS[s] for s in SWAPS], fontsize=9)
ax.set_xlim(-0.6, len(SWAPS)-0.4)
style(ax, 'A.  Dot (temporal) cueing\nCUED − UNCUED  [all swap conditions]',
      ylabel='Cueing effect (pp)')
ax.text(0.5, 0.97, 'cued arm = CUED (all conditions)',
        transform=ax.transAxes, ha='center', va='top', fontsize=7.5, color='#555',
        style='italic')

# ── Panel B: Depth cueing ─────────────────────────────────────────────────────

ax = axes[1]
depth_colors = ['#1d6a4a', '#1d6a4a', '#a93226', '#a93226']
# green = cued arm is CUED (depth agrees with temporal cue)
# red   = cued arm is UNCUED (depth opposes temporal cue)
for i, swap in enumerate(SWAPS):
    delta, k1,n1,k2,n2 = cueing_delta(swap, DEPTH_CUED_IS_CUED[swap])
    draw_delta_bar(ax, xs[i], delta, k1,n1,k2,n2, depth_colors[i])
ax.set_xticks(xs); ax.set_xticklabels([SWAP_LABELS[s] for s in SWAPS], fontsize=9)
ax.set_xlim(-0.6, len(SWAPS)-0.4)
style(ax, 'B.  Depth cueing\n(translation-in-cue-plane arm) − (other arm)',
      ylabel='Cueing effect (pp)')
# Arm labels below each bar
for i, swap in enumerate(SWAPS):
    lbl = 'C−U' if DEPTH_CUED_IS_CUED[swap] else 'U−C'
    ax.text(xs[i], YLIM[0]+1, lbl, ha='center', va='bottom', fontsize=7.5,
            color='#555', style='italic')
ax.text(0.5, 0.97,
        'green: depth agrees with temporal cue (N,C)  |  red: depth opposes (Z,CZ)',
        transform=ax.transAxes, ha='center', va='top', fontsize=7.5, color='#555',
        style='italic')

# ── Panel C: Color cueing ─────────────────────────────────────────────────────

ax = axes[2]
color_colors = ['#6e2f8e', '#a93226', '#6e2f8e', '#a93226']
# purple = cued arm is CUED (color agrees with temporal cue)
# red    = cued arm is UNCUED (color opposes temporal cue)
for i, swap in enumerate(SWAPS):
    delta, k1,n1,k2,n2 = cueing_delta(swap, COLOR_CUED_IS_CUED[swap])
    draw_delta_bar(ax, xs[i], delta, k1,n1,k2,n2, color_colors[i])
ax.set_xticks(xs); ax.set_xticklabels([SWAP_LABELS[s] for s in SWAPS], fontsize=9)
ax.set_xlim(-0.6, len(SWAPS)-0.4)
style(ax, 'C.  Color cueing\n(translation-in-cue-plane arm) − (other arm)',
      ylabel='Cueing effect (pp)')
for i, swap in enumerate(SWAPS):
    lbl = 'C−U' if COLOR_CUED_IS_CUED[swap] else 'U−C'
    ax.text(xs[i], YLIM[0]+1, lbl, ha='center', va='bottom', fontsize=7.5,
            color='#555', style='italic')
ax.text(0.5, 0.97,
        'purple: color agrees with temporal cue (N,Z)  |  red: color opposes (C,CZ)',
        transform=ax.transAxes, ha='center', va='top', fontsize=7.5, color='#555',
        style='italic')

# ── Footer ─────────────────────────────────────────────────────────────────────

fig.text(0.5, -0.04,
         'Delta = accuracy(cued arm) − accuracy(uncued arm)  ·  '
         '"Cued arm" = whichever of CUED/UNCUED has the translation in the cue plane  ·  '
         'In N, all three cueing types agree (all = CUED−UNCUED)  ·  '
         'Error bars: propagated Wilson 95% CI  ·  χ² significance  ·  '
         '†p<.1  *p<.05  **p<.01  ***p<.001',
         ha='center', va='bottom', fontsize=7, color='#555')

plt.tight_layout()
plt.savefig(OUT, dpi=150, bbox_inches='tight', facecolor='white')
print(f"\nSaved: {OUT}")
