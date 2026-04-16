#!/usr/bin/env python3
"""
decoupled_combined_clean.py

Combines two clean DecoupledDots_005m_v2 sessions for preliminary results:
  - 260413_2051 : full session, n=512 (post-fix, no artifact)
  - 260414_0922 : Q3+Q4 only (trials >= 263), n~250 (Q1 excluded: re-don artifact)

Produces a 2-row figure:
  Row 1 — Absolute accuracy (CUED and UNCUED) per swap condition
  Row 2 — Three cueing effects as delta bars (dot, depth, color)

"Cueing effect" definition for each type:
  Dot:   always CUED − UNCUED
  Depth: CUED−UNCUED for N,C  |  UNCUED−CUED for Z,CZ
  Color: CUED−UNCUED for N,Z  |  UNCUED−CUED for C,CZ

Output:
  Agents/SwapPilot/Figures/decoupled_combined_clean.png
"""

import csv, math, os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from scipy.stats import chi2_contingency

BASE = os.path.normpath(os.path.join(
    os.path.dirname(__file__), '../../Agents/SwapPilot/Figures'))
os.makedirs(BASE, exist_ok=True)
OUT = os.path.join(BASE, 'decoupled_combined_clean.png')

SESSIONS = [
    ('/tmp/quest_pull7/files/vr_dots_session_260413_2051.tsv', None),      # all trials
    ('/tmp/quest_pull7/files/vr_dots_session_260414_0922.tsv', 263),       # Q3+Q4 only
]

CHANCE = 1/8
SWAPS  = ['N', 'C', 'Z', 'CZ']
SWAP_LABELS = {'N': 'N\n(baseline)', 'C': 'C\n(color\nswap)',
               'Z': 'Z\n(depth\nswap)', 'CZ': 'CZ\n(both\nswap)'}

DEPTH_CUED_IS_CUED = {'N': True,  'C': True,  'Z': False, 'CZ': False}
COLOR_CUED_IS_CUED = {'N': True,  'C': False, 'Z': True,  'CZ': False}

C_CUED   = '#1a5276'
C_UNCUED = '#922b21'

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
print(f"Combined clean n = {n_total}")

def cell(filt):
    sub = [r for r in rows if filt(r)]
    k = sum(r['correct'] for r in sub)
    return k, len(sub)

cued   = {s: cell(lambda r,s=s: r['cond']=='CUED'   and r['swap']==s) for s in SWAPS}
uncued = {s: cell(lambda r,s=s: r['cond']=='UNCUED' and r['swap']==s) for s in SWAPS}

def cueing_delta(swap, cued_is_cued):
    if cued_is_cued:
        kc,nc = cued[swap]; ku,nu = uncued[swap]
    else:
        kc,nc = uncued[swap]; ku,nu = cued[swap]
    return pct(kc,nc)-pct(ku,nu), kc,nc,ku,nu

# Print summary
print(f"\n{'Swap':4s}  {'CUED':>12s}  {'UNCUED':>12s}  {'Dot Δ':>10s}  {'Depth Δ':>10s}  {'Color Δ':>10s}")
for s in SWAPS:
    kc,nc = cued[s]; ku,nu = uncued[s]
    d_dot,   *_ = cueing_delta(s, True)
    d_depth, *_ = cueing_delta(s, DEPTH_CUED_IS_CUED[s])
    d_color, *_ = cueing_delta(s, COLOR_CUED_IS_CUED[s])
    print(f"  {s:2s}:  {pct(kc,nc):5.1f}%({kc}/{nc})  {pct(ku,nu):5.1f}%({ku}/{nu})  "
          f"{d_dot:+6.1f}pp  {d_depth:+6.1f}pp  {d_color:+6.1f}pp")

# ── Figure ─────────────────────────────────────────────────────────────────────

fig = plt.figure(figsize=(16, 10))
fig.patch.set_facecolor('white')
fig.suptitle(
    f'DecoupledDots_005m_v2  ·  Combined clean sessions  ·  n={n_total}\n'
    '260413_2051 (full, n=512) + 260414_0922 Q3+Q4 (n≈250, trials 1–262 excluded)',
    fontsize=12, fontweight='bold', y=1.01)

from matplotlib.gridspec import GridSpec
gs = GridSpec(2, 3, top=0.93, bottom=0.10, left=0.07, right=0.97,
              hspace=0.55, wspace=0.35)

ax_abs  = fig.add_subplot(gs[0, :])   # top: absolute accuracy
ax_dot  = fig.add_subplot(gs[1, 0])   # bottom left: dot cueing
ax_dep  = fig.add_subplot(gs[1, 1])   # bottom mid:  depth cueing
ax_col  = fig.add_subplot(gs[1, 2])   # bottom right: color cueing

xs = np.arange(len(SWAPS))

# ── Row 1: Absolute accuracy ───────────────────────────────────────────────────

bar_w = 0.33; gap = 0.06
for i, swap in enumerate(SWAPS):
    x_c = xs[i] - (bar_w+gap)/2
    x_u = xs[i] + (bar_w+gap)/2

    for x, (k,n), color, label in [
        (x_c, cued[swap],   C_CUED,   'CUED'   if i==0 else None),
        (x_u, uncued[swap], C_UNCUED, 'UNCUED' if i==0 else None),
    ]:
        p = pct(k,n); lo,hi = wilson_ci(k,n)
        ax_abs.bar(x, p, bar_w, color=color, alpha=0.87, zorder=3,
                   edgecolor='white', lw=0.5, label=label)
        ax_abs.errorbar(x, p, yerr=[[p-lo],[hi-p]], fmt='none',
                        color='#333', capsize=3, capthick=1, lw=1.1, zorder=4)
        s = sig_vs_chance(k,n)
        if s and s not in ('n.s.',''):
            ax_abs.text(x, hi+1, s, ha='center', va='bottom', fontsize=8,
                        color='#222', fontweight='bold')
        if p > 14:
            ax_abs.text(x, p/2, f'{p:.0f}%\n({k}/{n})', ha='center', va='center',
                        fontsize=7, color='white', fontweight='bold')

ax_abs.axhline(CHANCE*100, color='#bbb', lw=1, ls='--', zorder=2)
ax_abs.text(3.75, CHANCE*100, 'chance\n12.5%', fontsize=7, color='#999', va='center')
ax_abs.set_xticks(xs)
ax_abs.set_xticklabels([SWAP_LABELS[s] for s in SWAPS], fontsize=10)
ax_abs.set_xlim(-0.6, len(SWAPS)-0.4)
ax_abs.set_ylim(-3, 88)
ax_abs.set_ylabel('% correct', fontsize=10)
ax_abs.set_title('Absolute accuracy — CUED (blue) and UNCUED (red) per swap condition',
                 fontsize=11, fontweight='bold', pad=8)
ax_abs.spines['top'].set_visible(False)
ax_abs.spines['right'].set_visible(False)
ax_abs.grid(axis='y', lw=0.4, alpha=0.3, zorder=0)
ax_abs.legend(fontsize=9, loc='upper right', framealpha=0.9)

# Dot cueing brackets above grouped bars
for i, swap in enumerate(SWAPS):
    kc,nc = cued[swap]; ku,nu = uncued[swap]
    d = pct(kc,nc)-pct(ku,nu)
    pv = chi2_p(kc,nc,ku,nu)
    y_br = 76
    x_c = xs[i] - (bar_w+gap)/2; x_u = xs[i] + (bar_w+gap)/2
    ax_abs.plot([x_c,x_c,x_u,x_u],[y_br-1.5,y_br,y_br,y_br-1.5],color='#555',lw=0.9)
    ax_abs.text(xs[i], y_br+0.5, f'{d:+.0f}pp {stars(pv)}',
                ha='center', va='bottom', fontsize=8, color='#333', fontweight='bold')

# ── Helper for delta bars ──────────────────────────────────────────────────────

YLIM_DELTA = (-50, 65)

def style_delta(ax, title):
    ax.axhline(0, color='#888', lw=0.9, zorder=1)
    ax.set_ylim(*YLIM_DELTA)
    ax.set_title(title, fontsize=10, fontweight='bold', pad=8)
    ax.set_ylabel('Cueing effect (pp)', fontsize=9)
    ax.tick_params(labelsize=9)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.grid(axis='y', lw=0.4, alpha=0.3, zorder=0)

def draw_delta(ax, x, delta, k1,n1,k2,n2, color, width=0.55):
    lo1,hi1 = wilson_ci(k1,n1); lo2,hi2 = wilson_ci(k2,n2)
    p1,p2 = pct(k1,n1), pct(k2,n2)
    err_lo = delta - ((p1-lo1)+(hi2-p2))
    err_hi = (hi1-p1)+(p2-lo2)
    ax.bar(x, delta, width, color=color, alpha=0.87, zorder=3,
           edgecolor='white', lw=0.5)
    ax.errorbar(x, delta, yerr=[[max(0,delta-err_lo)],[max(0,err_hi)]],
                fmt='none', color='#333', capsize=4, capthick=1.1, lw=1.2, zorder=4)
    pv = chi2_p(k1,n1,k2,n2); s = stars(pv)
    y_lbl = max(delta,0) + err_hi + 1.5
    ax.text(x, y_lbl, s, ha='center', va='bottom', fontsize=9,
            color='#222', fontweight='bold')
    if abs(delta) > 7:
        ax.text(x, delta/2, f'{delta:+.1f}pp', ha='center', va='center',
                fontsize=8, color='white', fontweight='bold')
    else:
        off = 3 if delta >= 0 else -3
        ax.text(x, delta+off, f'{delta:+.1f}pp', ha='center',
                va='bottom' if delta>=0 else 'top',
                fontsize=8, color='#333', fontweight='bold')

# ── Row 2, Panel A: Dot cueing ────────────────────────────────────────────────

dot_colors = ['#1a5276','#5dade2','#154360','#85c1e9']
for i, swap in enumerate(SWAPS):
    delta,k1,n1,k2,n2 = cueing_delta(swap, True)
    draw_delta(ax_dot, xs[i], delta, k1,n1,k2,n2, dot_colors[i])
ax_dot.set_xticks(xs)
ax_dot.set_xticklabels([SWAP_LABELS[s] for s in SWAPS], fontsize=9)
ax_dot.set_xlim(-0.6, len(SWAPS)-0.4)
style_delta(ax_dot, 'Dot (temporal) cueing\nCUED − UNCUED')
ax_dot.text(0.5, 0.02, 'cued arm = CUED (all conditions)',
            transform=ax_dot.transAxes, ha='center', va='bottom',
            fontsize=7.5, color='#555', style='italic')

# ── Row 2, Panel B: Depth cueing ─────────────────────────────────────────────

depth_cols = {'N':'#1d6a4a','C':'#1d6a4a','Z':'#a93226','CZ':'#a93226'}
for i, swap in enumerate(SWAPS):
    delta,k1,n1,k2,n2 = cueing_delta(swap, DEPTH_CUED_IS_CUED[swap])
    draw_delta(ax_dep, xs[i], delta, k1,n1,k2,n2, depth_cols[swap])
ax_dep.set_xticks(xs)
ax_dep.set_xticklabels([SWAP_LABELS[s] for s in SWAPS], fontsize=9)
ax_dep.set_xlim(-0.6, len(SWAPS)-0.4)
style_delta(ax_dep, 'Depth cueing\n(translation-in-cue-plane) − (other)')
# arm labels
for i, swap in enumerate(SWAPS):
    lbl = 'C−U' if DEPTH_CUED_IS_CUED[swap] else 'U−C'
    ax_dep.text(xs[i], YLIM_DELTA[0]+1, lbl, ha='center', va='bottom',
                fontsize=7.5, color='#555', style='italic')
ax_dep.legend(handles=[
    mpatches.Patch(color='#1d6a4a', label='Depth agrees w/ temporal cue (N,C)'),
    mpatches.Patch(color='#a93226', label='Depth opposes temporal cue (Z,CZ)')],
    fontsize=7.5, loc='upper right', framealpha=0.9)

# ── Row 2, Panel C: Color cueing ─────────────────────────────────────────────

color_cols = {'N':'#6e2f8e','C':'#a93226','Z':'#6e2f8e','CZ':'#a93226'}
for i, swap in enumerate(SWAPS):
    delta,k1,n1,k2,n2 = cueing_delta(swap, COLOR_CUED_IS_CUED[swap])
    draw_delta(ax_col, xs[i], delta, k1,n1,k2,n2, color_cols[swap])
ax_col.set_xticks(xs)
ax_col.set_xticklabels([SWAP_LABELS[s] for s in SWAPS], fontsize=9)
ax_col.set_xlim(-0.6, len(SWAPS)-0.4)
style_delta(ax_col, 'Color cueing\n(translation-in-cue-plane) − (other)')
for i, swap in enumerate(SWAPS):
    lbl = 'C−U' if COLOR_CUED_IS_CUED[swap] else 'U−C'
    ax_col.text(xs[i], YLIM_DELTA[0]+1, lbl, ha='center', va='bottom',
                fontsize=7.5, color='#555', style='italic')
ax_col.legend(handles=[
    mpatches.Patch(color='#6e2f8e', label='Color agrees w/ temporal cue (N,Z)'),
    mpatches.Patch(color='#a93226', label='Color opposes temporal cue (C,CZ)')],
    fontsize=7.5, loc='upper right', framealpha=0.9)

# ── Footer ─────────────────────────────────────────────────────────────────────

fig.text(0.5, 0.02,
         'Row 1 brackets: CUED−UNCUED dot cueing per swap condition  ·  '
         'Row 2: cueing effect = (translation-in-cue-plane arm) − (other arm)  ·  '
         'In N all three cueing types agree (all = CUED−UNCUED)  ·  '
         'Error bars: propagated Wilson 95% CI  ·  χ² significance  ·  '
         '†p<.1  *p<.05  **p<.01  ***p<.001',
         ha='center', fontsize=7, color='#555')

plt.savefig(OUT, dpi=150, bbox_inches='tight', facecolor='white')
print(f"\nSaved: {OUT}")
