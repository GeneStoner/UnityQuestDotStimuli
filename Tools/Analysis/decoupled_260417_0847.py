#!/usr/bin/env python3
"""
decoupled_260417_0847.py

Single-session figure for DecoupledDots_005m_v2, session 260417_0847 (n=512).
No artifact (UP direction) analysis.

Layout:
  Row 1 — Absolute accuracy CUED/UNCUED × swap type (with cueing brackets)
  Row 2 — Dot cueing Δ | Depth cueing Δ | Near/Far × Cond breakdown
"""

import csv, math, os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.gridspec import GridSpec
from scipy.stats import chi2_contingency

SESSION = '/tmp/quest_pull_latest/vr_dots_session_260417_0847.tsv'

BASE = os.path.normpath(os.path.join(os.path.dirname(__file__),
                                      '../../Agents/SwapPilot/Figures'))
os.makedirs(BASE, exist_ok=True)
OUT = os.path.join(BASE, 'decoupled_260417_0847.png')

CHANCE = 1/8
SWAPS  = ['N', 'C', 'Z', 'CZ']
SWAP_LABELS = {'N': 'N\n(baseline)', 'C': 'C\n(color\nswap)',
               'Z': 'Z\n(depth\nswap)', 'CZ': 'CZ\n(both\nswap)'}

DEPTH_CUED_IS_CUED = {'N': True, 'C': True, 'Z': False, 'CZ': False}

C_CUED   = '#1a5276'
C_UNCUED = '#922b21'
C_NEAR   = '#2e86ab'
C_FAR    = '#e84855'

# ── Stats ──────────────────────────────────────────────────────────────────────

def is_correct(td, rd):
    d = (float(rd) - float(td) + 360) % 360
    return (360 - d if d > 180 else d) <= 22.5

def pct(k, n): return k / n * 100 if n > 0 else 0.0

def wilson_ci(k, n, z=1.96):
    if n == 0: return 0.0, 0.0
    p = k / n
    denom = 1 + z**2 / n
    c  = (p + z**2 / (2*n)) / denom
    hw = z * math.sqrt(p*(1-p)/n + z**2/(4*n**2)) / denom
    return (c - hw)*100, (c + hw)*100

def chi2_p(k1, n1, k2, n2):
    if n1 == 0 or n2 == 0: return float('nan')
    _, pv, _, _ = chi2_contingency([[k1, n1-k1],[k2, n2-k2]], correction=False)
    return pv

def stars(p):
    if p is None or (isinstance(p, float) and math.isnan(p)): return ''
    return '***' if p<.001 else '**' if p<.01 else '*' if p<.05 else '†' if p<.1 else 'n.s.'

def sig_vs_chance(k, n):
    if n == 0: return ''
    z = (k/n - CHANCE) / math.sqrt(max(CHANCE*(1-CHANCE)/n, 1e-12))
    pv = 2 * (0.5*(1 + math.erf(-abs(z)/math.sqrt(2))))
    return stars(pv)

# ── Load ───────────────────────────────────────────────────────────────────────

rows = []
with open(SESSION, newline='') as f:
    for r in csv.DictReader(f, delimiter='\t'):
        if not r.get('TransDeg','').strip() or not r.get('RespDeg','').strip(): continue
        if r.get('EndKey','') in ('timeout','skip','requeue'): continue
        rows.append(dict(
            cond    = r['Cond'],
            swap    = r['SwapType'],
            depth   = r.get('DelayedFieldDepth','?'),   # 'N' or 'F'
            correct = int(is_correct(r['TransDeg'], r['RespDeg']))
        ))

print(f"n = {len(rows)}")

def cell(filt):
    sub = [r for r in rows if filt(r)]
    k = sum(r['correct'] for r in sub)
    return k, len(sub)

cued   = {s: cell(lambda r, s=s: r['cond']=='CUED'   and r['swap']==s) for s in SWAPS}
uncued = {s: cell(lambda r, s=s: r['cond']=='UNCUED' and r['swap']==s) for s in SWAPS}

def cueing_delta(swap, cued_is_cued):
    if cued_is_cued:
        k1,n1 = cued[swap];   k2,n2 = uncued[swap]
    else:
        k1,n1 = uncued[swap]; k2,n2 = cued[swap]
    return pct(k1,n1)-pct(k2,n2), k1,n1,k2,n2

# ── Figure ─────────────────────────────────────────────────────────────────────

fig = plt.figure(figsize=(16, 10))
fig.patch.set_facecolor('white')
fig.suptitle(
    'DecoupledDots_005m_v2  ·  Session 260417_0847  ·  n=512',
    fontsize=13, fontweight='bold', y=1.01)

gs = GridSpec(2, 3, top=0.93, bottom=0.10, left=0.07, right=0.97,
              hspace=0.55, wspace=0.35)

ax_abs  = fig.add_subplot(gs[0, :])
ax_dot  = fig.add_subplot(gs[1, 0])
ax_dep  = fig.add_subplot(gs[1, 1])
ax_nf   = fig.add_subplot(gs[1, 2])

xs   = np.arange(len(SWAPS))
bar_w = 0.33
gap   = 0.06

# ── Row 1: Absolute accuracy ───────────────────────────────────────────────────

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
        s = sig_vs_chance(k, n)
        if s and s not in ('n.s.', ''):
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
ax_abs.set_ylim(-3, 92)
ax_abs.set_ylabel('% correct', fontsize=10)
ax_abs.set_title('Absolute accuracy — CUED (blue) and UNCUED (red) per swap condition',
                 fontsize=11, fontweight='bold', pad=8)
ax_abs.spines['top'].set_visible(False)
ax_abs.spines['right'].set_visible(False)
ax_abs.grid(axis='y', lw=0.4, alpha=0.3, zorder=0)
ax_abs.legend(fontsize=9, loc='upper right', framealpha=0.9)

# cueing brackets
for i, swap in enumerate(SWAPS):
    kc,nc = cued[swap]; ku,nu = uncued[swap]
    d  = pct(kc,nc) - pct(ku,nu)
    pv = chi2_p(kc,nc,ku,nu)
    y_br = 80
    x_c = xs[i] - (bar_w+gap)/2; x_u = xs[i] + (bar_w+gap)/2
    ax_abs.plot([x_c,x_c,x_u,x_u],[y_br-1.5,y_br,y_br,y_br-1.5],color='#555',lw=0.9)
    ax_abs.text(xs[i], y_br+0.5, f'{d:+.0f}pp {stars(pv)}',
                ha='center', va='bottom', fontsize=8, color='#333', fontweight='bold')

# ── Helpers for delta panels ────────────────────────────────────────────────────

YLIM_DELTA = (-55, 75)

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
    p1,p2   = pct(k1,n1), pct(k2,n2)
    err_lo  = delta - ((p1-lo1)+(hi2-p2))
    err_hi  = (hi1-p1)+(p2-lo2)
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
                va='bottom' if delta >= 0 else 'top',
                fontsize=8, color='#333', fontweight='bold')

# ── Row 2, Panel A: Dot cueing ─────────────────────────────────────────────────

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

# ── Row 2, Panel B: Depth cueing ───────────────────────────────────────────────

depth_cols = {'N':'#1d6a4a','C':'#1d6a4a','Z':'#a93226','CZ':'#a93226'}
for i, swap in enumerate(SWAPS):
    delta,k1,n1,k2,n2 = cueing_delta(swap, DEPTH_CUED_IS_CUED[swap])
    draw_delta(ax_dep, xs[i], delta, k1,n1,k2,n2, depth_cols[swap])
ax_dep.set_xticks(xs)
ax_dep.set_xticklabels([SWAP_LABELS[s] for s in SWAPS], fontsize=9)
ax_dep.set_xlim(-0.6, len(SWAPS)-0.4)
style_delta(ax_dep, 'Depth cueing\n(translation-in-cue-plane) − (other)')
for i, swap in enumerate(SWAPS):
    lbl = 'C−U' if DEPTH_CUED_IS_CUED[swap] else 'U−C'
    ax_dep.text(xs[i], YLIM_DELTA[0]+2, lbl, ha='center', va='bottom',
                fontsize=7.5, color='#555', style='italic')
ax_dep.legend(handles=[
    mpatches.Patch(color='#1d6a4a', label='Depth agrees w/ temporal cue (N,C)'),
    mpatches.Patch(color='#a93226', label='Depth opposes temporal cue (Z,CZ)')],
    fontsize=7.5, loc='upper right', framealpha=0.9)

# ── Row 2, Panel C: Near / Far breakdown ──────────────────────────────────────

# 2×2: rows = CUED/UNCUED, columns = Near/Far, bars = absolute accuracy
nf_xs   = np.array([0, 1])   # Near, Far
nf_w    = 0.33
nf_gap  = 0.06

depth_labels = ['Near (translator\nin front)', 'Far (translator\nbehind)']

for ci, cond in enumerate(['CUED', 'UNCUED']):
    color = C_CUED if cond=='CUED' else C_UNCUED
    for di, dep in enumerate(['N', 'F']):
        k, n = cell(lambda r, c=cond, d=dep: r['cond']==c and r['depth']==d)
        p    = pct(k, n)
        lo, hi = wilson_ci(k, n)
        x = nf_xs[di] + (ci - 0.5) * (nf_w + nf_gap)
        label = cond if di == 0 else None
        ax_nf.bar(x, p, nf_w, color=color, alpha=0.87, zorder=3,
                  edgecolor='white', lw=0.5, label=label)
        ax_nf.errorbar(x, p, yerr=[[p-lo],[hi-p]], fmt='none',
                       color='#333', capsize=3, capthick=1, lw=1.1, zorder=4)
        s = sig_vs_chance(k, n)
        if s and s not in ('n.s.',''):
            ax_nf.text(x, hi+1, s, ha='center', va='bottom', fontsize=8,
                       color='#222', fontweight='bold')
        if p > 14:
            ax_nf.text(x, p/2, f'{p:.0f}%\n({k}/{n})', ha='center', va='center',
                       fontsize=7, color='white', fontweight='bold')
        else:
            ax_nf.text(x, max(p,0)+2, f'{p:.0f}%', ha='center', va='bottom',
                       fontsize=7, color='#333')

# brackets: Near CUED vs UNCUED and Far CUED vs UNCUED
for di, dep in enumerate(['N', 'F']):
    kc, nc_n = cell(lambda r, d=dep: r['cond']=='CUED'   and r['depth']==d)
    ku, nu_n = cell(lambda r, d=dep: r['cond']=='UNCUED' and r['depth']==d)
    d   = pct(kc,nc_n) - pct(ku,nu_n)
    pv  = chi2_p(kc,nc_n,ku,nu_n)
    x_c = nf_xs[di] - (nf_w+nf_gap)/2
    x_u = nf_xs[di] + (nf_w+nf_gap)/2
    y_br = 82
    ax_nf.plot([x_c,x_c,x_u,x_u],[y_br-1.5,y_br,y_br,y_br-1.5],color='#555',lw=0.9)
    ax_nf.text(nf_xs[di], y_br+0.5, f'{d:+.0f}pp {stars(pv)}',
               ha='center', va='bottom', fontsize=8, color='#333', fontweight='bold')

ax_nf.axhline(CHANCE*100, color='#bbb', lw=1, ls='--', zorder=2)
ax_nf.text(1.45, CHANCE*100, 'chance', fontsize=7, color='#999', va='center')
ax_nf.set_xticks(nf_xs)
ax_nf.set_xticklabels(depth_labels, fontsize=9)
ax_nf.set_xlim(-0.6, 1.6)
ax_nf.set_ylim(-3, 95)
ax_nf.set_ylabel('% correct', fontsize=9)
ax_nf.set_title('Near / Far\n(delayed-field = translator depth)',
                fontsize=10, fontweight='bold', pad=8)
ax_nf.spines['top'].set_visible(False)
ax_nf.spines['right'].set_visible(False)
ax_nf.grid(axis='y', lw=0.4, alpha=0.3, zorder=0)
ax_nf.legend(fontsize=9, loc='upper left', framealpha=0.9)

# ── Footer ──────────────────────────────────────────────────────────────────────

fig.text(0.5, 0.02,
         'Row 1 brackets: CUED−UNCUED per swap condition  ·  '
         'Row 2 left/mid: cueing = (translation-in-cue-plane arm) − (other arm)  ·  '
         'Row 2 right: Near/Far = depth of translator field (DelayedFieldDepth); brackets = CUED−UNCUED  ·  '
         'Error bars: propagated Wilson 95% CI  ·  χ²  ·  †p<.1  *p<.05  **p<.01  ***p<.001',
         ha='center', fontsize=7, color='#555')

plt.savefig(OUT, dpi=150, bbox_inches='tight', facecolor='white')
print(f"Saved: {OUT}")
