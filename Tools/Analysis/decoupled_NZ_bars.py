#!/usr/bin/env python3
"""
decoupled_NZ_bars.py

4-bar performance figure: N and Z swap conditions × CUED / UNCUED.
Combined clean sessions: 260413_2051 (n=512) + 260414_0922 Q3+Q4 (trials ≥263).

Output: Agents/SwapPilot/Figures/decoupled_NZ_bars.svg / .pdf / .png
"""

import csv, math, os
import numpy as np
import matplotlib
matplotlib.use('Agg')
matplotlib.rcParams['pdf.fonttype'] = 42
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from scipy.stats import chi2_contingency

BASE = os.path.normpath(os.path.join(
    os.path.dirname(__file__), '../../Agents/SwapPilot/Figures'))
os.makedirs(BASE, exist_ok=True)
OUT = os.path.join(BASE, 'decoupled_NZ_bars')

SESSIONS = [
    ('/tmp/quest_pull7/files/vr_dots_session_260413_2051.tsv', None),
    ('/tmp/quest_pull7/files/vr_dots_session_260414_0922.tsv', 263),
]

CHANCE = 1/8

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
    _, pv, _, _ = chi2_contingency([[k1,n1-k1],[k2,n2-k2]], correction=False)
    return pv

def stars(p):
    return '***' if p<.001 else '**' if p<.01 else '*' if p<.05 else '†' if p<.1 else 'n.s.'

def stars_vs_chance(k, n):
    z = (k/n - CHANCE) / math.sqrt(CHANCE*(1-CHANCE)/n)
    from math import erf, sqrt
    pv = 2*(0.5*(1+erf(-abs(z)/sqrt(2))))
    return stars(pv)

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

def cell(swap, cond):
    sub = [r for r in rows if r['swap']==swap and r['cond']==cond]
    k = sum(r['correct'] for r in sub)
    return k, len(sub)

# ── Data ───────────────────────────────────────────────────────────────────────
C_CUED   = '#1a3a8b'
C_UNCUED = '#884400'

conditions = [
    ('N', 'CUED'),
    ('N', 'UNCUED'),
    ('Z', 'CUED'),
    ('Z', 'UNCUED'),
]

labels  = ['N\nCUED', 'N\nUNCUED', 'Z\nCUED', 'Z\nUNCUED']
colors  = [C_CUED, C_UNCUED, C_CUED, C_UNCUED]
xs      = np.array([0, 1, 2.6, 3.6])

# ── Figure ─────────────────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(6, 5))
fig.patch.set_facecolor('white')

for i, (swap, cond) in enumerate(conditions):
    k, n = cell(swap, cond)
    p    = pct(k, n)
    lo, hi = wilson_ci(k, n)

    ax.bar(xs[i], p, 0.7, color=colors[i], alpha=0.85, zorder=3,
           edgecolor='white', lw=0.5)
    ax.errorbar(xs[i], p, yerr=[[p-lo],[hi-p]],
                fmt='none', color='#222', capsize=5, capthick=1.2, lw=1.3, zorder=4)

    # significance vs chance
    s = stars_vs_chance(k, n)
    ax.text(xs[i], hi + 1.5, s, ha='center', va='bottom',
            fontsize=11, fontweight='bold', color='#111')

    # n label inside bar
    ax.text(xs[i], 4, f'n={n}', ha='center', va='bottom',
            fontsize=7.5, color='white', fontweight='bold')

# CUED vs UNCUED brackets + delta for each swap
for swap, x1, x2 in [('N', 0, 1), ('Z', 2.6, 3.6)]:
    kc, nc = cell(swap, 'CUED')
    ku, nu = cell(swap, 'UNCUED')
    delta  = pct(kc, nc) - pct(ku, nu)
    pv     = chi2_p(kc, nc, ku, nu)
    s      = stars(pv)
    xm     = (x1+x2)/2
    yb     = max(wilson_ci(kc,nc)[1], wilson_ci(ku,nu)[1]) + 5
    ax.plot([x1, x1, x2, x2], [yb-1, yb, yb, yb-1],
            color='#333', lw=1.0)
    ax.text(xm, yb+0.5, f'Δ={delta:+.1f}pp  {s}',
            ha='center', va='bottom', fontsize=9, fontweight='bold', color='#111')

ax.axhline(CHANCE*100, color='#999', lw=1.0, ls='--', zorder=1, label='Chance (12.5%)')
ax.set_xticks(xs)
ax.set_xticklabels(labels, fontsize=11)
ax.set_ylabel('Accuracy (%)', fontsize=11)
ax.set_ylim(0, 95)
ax.set_xlim(-0.6, 4.2)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.text(1.3, CHANCE*100 + 1.2, 'Chance', fontsize=8, color='#999', va='bottom')

# group labels
ax.text(0.5,  -12, 'N  (no swap)', ha='center', fontsize=10, color='#444',
        fontweight='bold', transform=ax.transData, clip_on=False)
ax.text(3.1, -12, 'Z  (depth swap)', ha='center', fontsize=10, color='#116688',
        fontweight='bold', transform=ax.transData, clip_on=False)

ax.set_title(
    f'DecoupledDots — N vs Z conditions\n'
    f'Combined clean sessions  ·  n={n_total}  ·  Wilson 95% CI  ·  χ² vs chance',
    fontsize=10, fontweight='bold', pad=10)

plt.tight_layout()
plt.savefig(OUT+'.png', dpi=150, bbox_inches='tight', facecolor='white')
plt.savefig(OUT+'.svg', bbox_inches='tight', facecolor='white')
with PdfPages(OUT+'.pdf') as pdf:
    pdf.savefig(fig, bbox_inches='tight', facecolor='white')

print(f'Saved: {OUT}.png / .svg / .pdf')

# ── Print summary ──────────────────────────────────────────────────────────────
print(f'\nn={n_total} total')
for swap, cond in conditions:
    k, n = cell(swap, cond)
    lo, hi = wilson_ci(k, n)
    print(f'  {swap} {cond:7s}: {k}/{n} = {pct(k,n):.1f}%  [{lo:.1f}, {hi:.1f}]  {stars_vs_chance(k,n)}')
