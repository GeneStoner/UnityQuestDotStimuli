#!/usr/bin/env python3
"""
decoupled_abs_nearfar_260413_2051.py

3-panel figure for session 260413_2051 showing absolute accuracy
(not deltas) and Near/Far breakdown.

Panel A — CUED absolute accuracy for each swap condition (N, C, Z, CZ)
Panel B — UNCUED absolute accuracy for each swap condition
Panel C — Near vs Far split by CUED/UNCUED across all swap conditions

Output:
  Agents/SwapPilot/Figures/decoupled_abs_nearfar_260413_2051.png
"""

import csv, math, os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from scipy.stats import chi2_contingency

DATA = "/tmp/quest_pull5/files/vr_dots_session_260413_2051.tsv"
BASE = os.path.normpath(os.path.join(
    os.path.dirname(__file__), '../../Agents/SwapPilot/Figures'))
os.makedirs(BASE, exist_ok=True)
OUT = os.path.join(BASE, 'decoupled_abs_nearfar_260413_2051.png')

CHANCE = 1/8
SWAPS  = ['N', 'C', 'Z', 'CZ']
SWAP_LABELS = {'N': 'N\n(baseline)', 'C': 'C\n(color\nswap)',
               'Z': 'Z\n(depth\nswap)', 'CZ': 'CZ\n(both\nswap)'}

C_CUED_NEAR   = '#1a5276'
C_CUED_FAR    = '#5dade2'
C_UNCUED_NEAR = '#922b21'
C_UNCUED_FAR  = '#f1948a'

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
    return (c-hw)*100, (c+hw)*100

def chi2_p(k1, n1, k2, n2):
    if n1==0 or n2==0: return float('nan')
    _, pv, _, _ = chi2_contingency([[k1,n1-k1],[k2,n2-k2]], correction=False)
    return pv

def stars(p):
    if p is None or (isinstance(p,float) and math.isnan(p)): return ''
    return '***' if p<.001 else '**' if p<.01 else '*' if p<.05 else '†' if p<.1 else 'n.s.'

def sig_vs_chance(k, n):
    if n==0: return ''
    z = (k/n - CHANCE) / math.sqrt(max(CHANCE*(1-CHANCE)/n, 1e-12))
    pv = 2*(0.5*(1+math.erf(-abs(z)/math.sqrt(2))))
    return stars(pv)

# ── Load ───────────────────────────────────────────────────────────────────────

rows = []
with open(DATA, newline='') as f:
    for r in csv.DictReader(f, delimiter='\t'):
        if not r.get('TransDeg','').strip() or not r.get('RespDeg','').strip(): continue
        if r.get('EndKey','') in ('timeout','skip','requeue'): continue
        rows.append(dict(
            cond  = r['Cond'],
            swap  = r['SwapType'],
            depth = r['DelayedFieldDepth'],   # N=Near, F=Far translating field
            correct = int(is_correct(r['TransDeg'], r['RespDeg']))
        ))

n_total = len(rows)

def cell(filt):
    sub = [r for r in rows if filt(r)]
    k = sum(r['correct'] for r in sub)
    return k, len(sub)

# ── Pre-compute ────────────────────────────────────────────────────────────────

def draw_bar(ax, x, k, n, color, width=0.55, hatch=None, label=None):
    p = pct(k,n); lo, hi = wilson_ci(k,n)
    ax.bar(x, p, width, color=color, alpha=0.87, zorder=3,
           edgecolor='white', lw=0.5, hatch=hatch, label=label)
    ax.errorbar(x, p, yerr=[[p-lo],[hi-p]], fmt='none',
                color='#333', capsize=4, capthick=1.1, lw=1.2, zorder=4)
    s = sig_vs_chance(k, n)
    if s and s not in ('n.s.',''):
        ax.text(x, hi+1.5, s, ha='center', va='bottom', fontsize=9,
                color='#222', fontweight='bold')
    if p > 16:
        ax.text(x, p/2, f'{p:.0f}%\n({k}/{n})', ha='center', va='center',
                fontsize=7.5, color='white', fontweight='bold')
    return p, lo, hi

def style(ax, title, ylim=(-5, 90)):
    ax.axhline(CHANCE*100, color='#bbb', lw=1.0, ls='--', zorder=2)
    ax.text(1.01, CHANCE*100, 'chance\n12.5%',
            transform=ax.get_yaxis_transform(), fontsize=7, color='#999', va='center')
    ax.set_ylim(*ylim)
    ax.set_title(title, fontsize=10, fontweight='bold', pad=7)
    ax.set_ylabel('% correct', fontsize=9)
    ax.tick_params(labelsize=9)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.grid(axis='y', lw=0.4, alpha=0.3, zorder=0)

def bracket(ax, x1, x2, y, label, color='#444'):
    ax.plot([x1,x1,x2,x2],[y-2,y,y,y-2], color=color, lw=0.9)
    ax.text((x1+x2)/2, y+0.8, label, ha='center', va='bottom',
            fontsize=8, color=color, fontweight='bold')

# ── Figure ─────────────────────────────────────────────────────────────────────

fig = plt.figure(figsize=(16, 10))
fig.patch.set_facecolor('white')
fig.suptitle(
    f'Session 260413_2051  ·  DecoupledDots_005m_v2  ·  n={n_total}\n'
    'Absolute accuracy (not deltas)  ·  Near/Far = translating field depth',
    fontsize=11, fontweight='bold', y=1.01)

# Layout: top row = A+B (CUED, UNCUED abs), bottom = C (Near/Far full breakdown)
from matplotlib import gridspec
gs = gridspec.GridSpec(2, 2, top=0.93, bottom=0.08, left=0.07, right=0.97,
                       hspace=0.5, wspace=0.35)
ax_a = fig.add_subplot(gs[0, 0])
ax_b = fig.add_subplot(gs[0, 1])
ax_c = fig.add_subplot(gs[1, :])

xs = np.arange(len(SWAPS))

# ── Panel A: CUED absolute accuracy ────────────────────────────────────────────

for i, swap in enumerate(SWAPS):
    k, n = cell(lambda r, s=swap: r['cond']=='CUED' and r['swap']==s)
    draw_bar(ax_a, xs[i], k, n, C_CUED_FAR)   # single color for CUED collapsed

ax_a.set_xticks(xs)
ax_a.set_xticklabels([SWAP_LABELS[s] for s in SWAPS], fontsize=9)
ax_a.set_xlim(-0.6, len(SWAPS)-0.4)
style(ax_a, 'A.  CUED — absolute accuracy')

# annotate N→Z difference
kN, nN = cell(lambda r: r['cond']=='CUED' and r['swap']=='N')
kZ, nZ = cell(lambda r: r['cond']=='CUED' and r['swap']=='Z')
pv = chi2_p(kN, nN, kZ, nZ)
bracket(ax_a, xs[0], xs[2], 80,
        f'N→Z: {pct(kZ,nZ)-pct(kN,nN):+.1f}pp {stars(pv)}', color='#1a5276')

# ── Panel B: UNCUED absolute accuracy ──────────────────────────────────────────

for i, swap in enumerate(SWAPS):
    k, n = cell(lambda r, s=swap: r['cond']=='UNCUED' and r['swap']==s)
    draw_bar(ax_b, xs[i], k, n, C_UNCUED_FAR)

ax_b.set_xticks(xs)
ax_b.set_xticklabels([SWAP_LABELS[s] for s in SWAPS], fontsize=9)
ax_b.set_xlim(-0.6, len(SWAPS)-0.4)
style(ax_b, 'B.  UNCUED — absolute accuracy')

kNu, nNu = cell(lambda r: r['cond']=='UNCUED' and r['swap']=='N')
kZu, nZu = cell(lambda r: r['cond']=='UNCUED' and r['swap']=='Z')
pvu = chi2_p(kNu, nNu, kZu, nZu)
bracket(ax_b, xs[0], xs[2], 80,
        f'N→Z: {pct(kZu,nZu)-pct(kNu,nNu):+.1f}pp {stars(pvu)}', color='#922b21')

# ── Panel C: Near vs Far — CUED and UNCUED across all swap conditions ──────────
# 4 swap groups × 4 bars (CUED Near, CUED Far, UNCUED Near, UNCUED Far)

bar_w = 0.18; gap = 0.03; group_gap = 0.35
xtick_pos, xtick_lbl = [], []

for gi, swap in enumerate(SWAPS):
    x0 = gi * (4*bar_w + 3*gap + group_gap)
    specs = [
        ('CUED',   'N', C_CUED_NEAR,   '',   'CUED Near'),
        ('CUED',   'F', C_CUED_FAR,    '',   'CUED Far'),
        ('UNCUED', 'N', C_UNCUED_NEAR, '//', 'UNCUED Near'),
        ('UNCUED', 'F', C_UNCUED_FAR,  '//', 'UNCUED Far'),
    ]
    bar_xs = [x0 + j*(bar_w+gap) for j in range(4)]

    for xi, (cond, depth, color, hatch, lbl) in zip(bar_xs, specs):
        k, n = cell(lambda r, c=cond, s=swap, d=depth:
                    r['cond']==c and r['swap']==s and r['depth']==d)
        draw_bar(ax_c, xi, k, n, color, width=bar_w, hatch=hatch,
                 label=lbl if gi==0 else None)

    # Near vs Far bracket for CUED
    kCN, nCN = cell(lambda r, s=swap: r['cond']=='CUED'   and r['swap']==s and r['depth']=='N')
    kCF, nCF = cell(lambda r, s=swap: r['cond']=='CUED'   and r['swap']==s and r['depth']=='F')
    kUN, nUN = cell(lambda r, s=swap: r['cond']=='UNCUED' and r['swap']==s and r['depth']=='N')
    kUF, nUF = cell(lambda r, s=swap: r['cond']=='UNCUED' and r['swap']==s and r['depth']=='F')

    eff_c = pct(kCF,nCF) - pct(kCN,nCN)
    eff_u = pct(kUF,nUF) - pct(kUN,nUN)
    pv_c = chi2_p(kCF,nCF,kCN,nCN)
    pv_u = chi2_p(kUF,nUF,kUN,nUN)

    y_br = 76
    bracket(ax_c, bar_xs[0], bar_xs[1], y_br,
            f'Far−Near\n{eff_c:+.0f}pp {stars(pv_c)}', color='#1a5276')
    bracket(ax_c, bar_xs[2], bar_xs[3], y_br,
            f'Far−Near\n{eff_u:+.0f}pp {stars(pv_u)}', color='#922b21')

    group_center = (bar_xs[0]+bar_xs[3])/2
    xtick_pos.append(group_center)
    xtick_lbl.append(SWAP_LABELS[swap])

ax_c.set_xticks(xtick_pos)
ax_c.set_xticklabels(xtick_lbl, fontsize=9)
ax_c.axhline(CHANCE*100, color='#bbb', lw=1.0, ls='--', zorder=2)
ax_c.text(1.01, CHANCE*100, 'chance\n12.5%',
          transform=ax_c.get_yaxis_transform(), fontsize=7, color='#999', va='center')
ax_c.set_ylim(-5, 95)
ax_c.set_ylabel('% correct', fontsize=9)
ax_c.set_title('C.  Near vs Far — CUED (blue) and UNCUED (red) × all swap conditions\n'
               'Near/Far = depth of the translating field',
               fontsize=10, fontweight='bold', pad=7)
ax_c.spines['top'].set_visible(False)
ax_c.spines['right'].set_visible(False)
ax_c.grid(axis='y', lw=0.4, alpha=0.3, zorder=0)

# Vertical separators between swap groups
for gi in range(1, len(SWAPS)):
    xsep = gi*(4*bar_w+3*gap+group_gap) - group_gap/2
    ax_c.axvline(xsep, color='#ddd', lw=1.0, zorder=1)

patches = [
    mpatches.Patch(color=C_CUED_NEAR,   label='CUED Near'),
    mpatches.Patch(color=C_CUED_FAR,    label='CUED Far'),
    mpatches.Patch(color=C_UNCUED_NEAR, label='UNCUED Near', hatch='//'),
    mpatches.Patch(color=C_UNCUED_FAR,  label='UNCUED Far',  hatch='//'),
]
ax_c.legend(handles=patches, fontsize=8, loc='upper right',
            framealpha=0.9, ncol=2, handlelength=1.5)

# ── Footer ─────────────────────────────────────────────────────────────────────

fig.text(0.5, 0.01,
         'Wilson 95% CI  ·  Stars above bars = sig vs chance (z-test)  ·  '
         'Bracket labels: χ² two-sided  ·  k/n shown inside bars  ·  '
         '†p<.1  *p<.05  **p<.01  ***p<.001',
         ha='center', fontsize=7, color='#555')

plt.savefig(OUT, dpi=150, bbox_inches='tight', facecolor='white')
print(f"Saved: {OUT}")

# Quick printout
print(f"\nNear/Far summary (session 260413_2051, n={n_total}):")
for swap in SWAPS:
    for cond in ['CUED','UNCUED']:
        kN,nN = cell(lambda r,c=cond,s=swap: r['cond']==c and r['swap']==s and r['depth']=='N')
        kF,nF = cell(lambda r,c=cond,s=swap: r['cond']==c and r['swap']==s and r['depth']=='F')
        print(f"  {cond:6s} {swap:2s}: Near={pct(kN,nN):.1f}% ({kN}/{nN})  "
              f"Far={pct(kF,nF):.1f}% ({kF}/{nF})  "
              f"Far-Near={pct(kF,nF)-pct(kN,nN):+.1f}pp {stars(chi2_p(kF,nF,kN,nN))}")
