#!/usr/bin/env python3
"""
decoupled_three_cueing_260413_2051.py

3-panel figure for session 260413_2051 showing all three cueing types
across all four swap conditions.

Panel A — F1 Dot (temporal) cueing
  CUED − UNCUED delta for each swap condition (N, C, Z, CZ).
  Shows whether the temporal cue survives depth/color swaps.

Panel B — F2 Depth field cueing
  CUED accuracy for N, C, Z, CZ. Shaded by depth-field consistency:
  dark = translator stays in delayed-field depth plane (N, C),
  light = translator swaps depth plane (Z, CZ).
  Bracket shows the depth-consistency contrast.

Panel C — F3 Color field cueing
  CUED accuracy for N, C, Z, CZ. Shaded by color-field consistency:
  dark = translator color matches delayed-field (N, Z),
  light = translator color swaps (C, CZ).
  Bracket shows the color-consistency contrast.

Output:
  Agents/SwapPilot/Figures/decoupled_three_cueing_260413_2051.png
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
OUT = os.path.join(BASE, 'decoupled_three_cueing_260413_2051.png')

CHANCE = 1 / 8
SWAPS = ['N', 'C', 'Z', 'CZ']
SWAP_LABELS = {'N': 'N\n(baseline)', 'C': 'C\n(color\nswap)',
               'Z': 'Z\n(depth\nswap)', 'CZ': 'CZ\n(both\nswap)'}

# Factor memberships
# F2: depth-field consistent when CUED translator stays in the delayed-field plane
DEPTH_CONSISTENT = {'N': True, 'C': True, 'Z': False, 'CZ': False}
# F3: color-field consistent when CUED translator color matches delayed field
COLOR_CONSISTENT  = {'N': True, 'C': False, 'Z': True, 'CZ': False}

# Colors
CUED_COLOR   = '#1a5276'
UNCUED_COLOR = '#922b21'
DEPTH_CON    = '#1d6a4a'   # consistent (dark green)
DEPTH_INC    = '#a9dfbf'   # inconsistent (light green)
COLOR_CON    = '#6e2f8e'   # consistent (dark purple)
COLOR_INC    = '#d2b4de'   # inconsistent (light purple)

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

def sig_vs_chance(k, n):
    if n == 0: return ''
    z = (k/n - CHANCE) / math.sqrt(max(CHANCE*(1-CHANCE)/n, 1e-12))
    pv = 2*(0.5*(1+math.erf(-abs(z)/math.sqrt(2))))
    return stars(pv)

# ── Load ───────────────────────────────────────────────────────────────────────

rows = []
with open(DATA, newline='') as f:
    for r in csv.DictReader(f, delimiter='\t'):
        if not r.get('TransDeg','').strip() or not r.get('RespDeg','').strip():
            continue
        if r.get('EndKey','') in ('timeout','skip','requeue'):
            continue
        rows.append(dict(
            cond  = r['Cond'],
            swap  = r['SwapType'],
            depth = r['DelayedFieldDepth'],
            correct = int(is_correct(r['TransDeg'], r['RespDeg']))
        ))

n_total = len(rows)

def cell(filt):
    sub = [r for r in rows if filt(r)]
    k = sum(r['correct'] for r in sub)
    return k, len(sub)

# ── Pre-compute ────────────────────────────────────────────────────────────────

cued   = {s: cell(lambda r, s=s: r['cond']=='CUED'   and r['swap']==s) for s in SWAPS}
uncued = {s: cell(lambda r, s=s: r['cond']=='UNCUED' and r['swap']==s) for s in SWAPS}

# F1 deltas
f1_delta = {s: pct(*cued[s]) - pct(*uncued[s]) for s in SWAPS}
f1_p     = {s: chi2_p(cued[s][0], cued[s][1], uncued[s][0], uncued[s][1]) for s in SWAPS}

# F2: CUED accuracy, grouped by depth consistency
depth_con_cells = [(s, cued[s]) for s in SWAPS if DEPTH_CONSISTENT[s]]
depth_inc_cells = [(s, cued[s]) for s in SWAPS if not DEPTH_CONSISTENT[s]]
kdc = sum(c[0] for _,c in depth_con_cells); ndc = sum(c[1] for _,c in depth_con_cells)
kdi = sum(c[0] for _,c in depth_inc_cells); ndi = sum(c[1] for _,c in depth_inc_cells)
f2_delta = pct(kdc,ndc) - pct(kdi,ndi)
f2_p     = chi2_p(kdc, ndc, kdi, ndi)

# F3: CUED accuracy, grouped by color consistency
color_con_cells = [(s, cued[s]) for s in SWAPS if COLOR_CONSISTENT[s]]
color_inc_cells = [(s, cued[s]) for s in SWAPS if not COLOR_CONSISTENT[s]]
kcc = sum(c[0] for _,c in color_con_cells); ncc = sum(c[1] for _,c in color_con_cells)
kci = sum(c[0] for _,c in color_inc_cells); nci = sum(c[1] for _,c in color_inc_cells)
f3_delta = pct(kcc,ncc) - pct(kci,nci)
f3_p     = chi2_p(kcc, ncc, kci, nci)

print(f"\nSession 260413_2051  (n={n_total})")
print(f"F1 dot cueing (N):    {f1_delta['N']:+.1f}pp {stars(f1_p['N'])}")
print(f"F1 dot cueing (C):    {f1_delta['C']:+.1f}pp {stars(f1_p['C'])}")
print(f"F1 dot cueing (Z):    {f1_delta['Z']:+.1f}pp {stars(f1_p['Z'])}")
print(f"F1 dot cueing (CZ):   {f1_delta['CZ']:+.1f}pp {stars(f1_p['CZ'])}")
print(f"F2 depth field:       {f2_delta:+.1f}pp {stars(f2_p)}  (con={pct(kdc,ndc):.1f}% vs inc={pct(kdi,ndi):.1f}%)")
print(f"F3 color field:       {f3_delta:+.1f}pp {stars(f3_p)}  (con={pct(kcc,ncc):.1f}% vs inc={pct(kci,nci):.1f}%)")

# ── Figure ─────────────────────────────────────────────────────────────────────

fig, axes = plt.subplots(1, 3, figsize=(15, 6))
fig.patch.set_facecolor('white')
fig.suptitle(
    f'Session 260413_2051  ·  DecoupledDots_005m_v2  ·  n={n_total}  ·  All three cueing types\n'
    'Post-fix (jerk + expansion removed + per-trial rotation)',
    fontsize=11, fontweight='bold', y=1.01)

def style(ax, title, ylabel='', ylim=(-30, 80)):
    ax.axhline(0, color='#888', lw=0.8, ls='-', zorder=1)
    ax.set_ylim(*ylim)
    ax.set_title(title, fontsize=10, fontweight='bold', pad=8)
    ax.set_ylabel(ylabel, fontsize=9)
    ax.tick_params(labelsize=9)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.grid(axis='y', lw=0.4, alpha=0.3, zorder=0)

def draw_delta_bar(ax, x, delta, k1, n1, k2, n2, color, width=0.5):
    """Draw a delta (effect size) bar with CI from propagated Wilson CIs."""
    lo1, hi1 = wilson_ci(k1, n1)
    lo2, hi2 = wilson_ci(k2, n2)
    p1 = pct(k1, n1); p2 = pct(k2, n2)
    err_lo = delta - ((p1 - lo1) + (hi2 - p2))   # conservative
    err_hi = (hi1 - p1) + (p2 - lo2)
    ax.bar(x, delta, width, color=color, alpha=0.85, zorder=3,
           edgecolor='white', linewidth=0.5)
    ax.errorbar(x, delta, yerr=[[max(0, delta - err_lo)], [max(0, err_hi)]],
                fmt='none', color='#333', capsize=4, capthick=1.0, lw=1.2, zorder=4)
    pv = chi2_p(k1, n1, k2, n2)
    s  = stars(pv)
    y_lbl = max(delta, 0) + err_hi + 1.5
    ax.text(x, y_lbl, s, ha='center', va='bottom', fontsize=9,
            color='#222', fontweight='bold')
    ax.text(x, delta/2 if abs(delta) > 8 else delta + 2,
            f'{delta:+.1f}pp', ha='center', va='center', fontsize=8,
            color='white' if abs(delta) > 8 else '#333', fontweight='bold')

def draw_acc_bar(ax, x, k, n, color, width=0.5, hatch=None):
    p = pct(k, n); lo, hi = wilson_ci(k, n)
    ax.bar(x, p, width, color=color, alpha=0.85, zorder=3,
           edgecolor='white', linewidth=0.5, hatch=hatch)
    ax.errorbar(x, p, yerr=[[p-lo],[hi-p]], fmt='none',
                color='#333', capsize=4, capthick=1.0, lw=1.2, zorder=4)
    s = sig_vs_chance(k, n)
    if s and s not in ('n.s.',''):
        ax.text(x, hi+1.5, s, ha='center', va='bottom', fontsize=8,
                color='#222', fontweight='bold')
    if p > 16:
        ax.text(x, p/2, f'{p:.0f}%', ha='center', va='center',
                fontsize=8, color='white', fontweight='bold')
    return p, lo, hi

# ── Panel A: F1 Dot cueing — CUED minus UNCUED for each swap condition ─────────

ax = axes[0]
xs = np.arange(len(SWAPS))
colors_f1 = ['#1a5276', '#5dade2', '#154360', '#85c1e9']

for i, swap in enumerate(SWAPS):
    kc, nc = cued[swap]; ku, nu = uncued[swap]
    draw_delta_bar(ax, xs[i], f1_delta[swap], kc, nc, ku, nu, colors_f1[i])

ax.set_xticks(xs)
ax.set_xticklabels([SWAP_LABELS[s] for s in SWAPS], fontsize=9)
ax.set_xlim(-0.6, len(SWAPS)-0.4)
style(ax, 'A.  F1: Dot (temporal) cueing\nCUED − UNCUED per swap condition',
      ylabel='Cueing Δ (pp)', ylim=(-45, 65))
ax.axhline(0, color='#888', lw=0.8, zorder=1)

# ── Panel B: F2 Depth field cueing — CUED accuracy by depth consistency ────────

ax = axes[1]
# 4 bars (one per swap condition), colored dark/light by depth consistency
# Then a pooled bracket showing the overall depth-consistency contrast
xs_b = np.arange(len(SWAPS), dtype=float)

for i, swap in enumerate(SWAPS):
    color = DEPTH_CON if DEPTH_CONSISTENT[swap] else DEPTH_INC
    k, n = cued[swap]
    draw_acc_bar(ax, xs_b[i], k, n, color)

# Bracket: pooled consistent vs pooled inconsistent
y_br = 72
con_xs  = [xs_b[i] for i,s in enumerate(SWAPS) if DEPTH_CONSISTENT[s]]
inc_xs  = [xs_b[i] for i,s in enumerate(SWAPS) if not DEPTH_CONSISTENT[s]]
# bracket within each group
for grp_xs, k, n, lbl in [(con_xs, kdc, ndc, 'depth\nconsistent'),
                            (inc_xs, kdi, ndi, 'depth\ninconsistent')]:
    xL = grp_xs[0]-0.3; xR = grp_xs[-1]+0.3
    ax.plot([xL,xL,xR,xR],[y_br-2,y_br,y_br,y_br-2], color='#444', lw=0.9)
    ax.text((xL+xR)/2, y_br+0.5, f'{pct(k,n):.0f}%', ha='center', va='bottom',
            fontsize=8, color='#333')

# overall effect label
ax.text(1.5, y_br+7, f'F2 = {f2_delta:+.1f}pp  {stars(f2_p)}',
        ha='center', va='bottom', fontsize=9, color='#1d6a4a', fontweight='bold')

ax.set_xticks(xs_b)
ax.set_xticklabels([SWAP_LABELS[s] for s in SWAPS], fontsize=9)
ax.set_xlim(-0.6, len(SWAPS)-0.4)
ax.axhline(CHANCE*100, color='#aaa', lw=1.0, ls='--', zorder=2)
ax.text(3.6, CHANCE*100, 'chance', fontsize=7, color='#999', va='center')
style(ax, 'B.  F2: Depth field cueing\nCUED accuracy — dark=depth consistent (N,C), light=inconsistent (Z,CZ)',
      ylabel='CUED % correct', ylim=(-5, 90))

patches_b = [mpatches.Patch(color=DEPTH_CON, label='Depth consistent (N, C)'),
             mpatches.Patch(color=DEPTH_INC, label='Depth inconsistent (Z, CZ)')]
ax.legend(handles=patches_b, fontsize=7.5, loc='lower right', framealpha=0.9)

# ── Panel C: F3 Color field cueing — CUED accuracy by color consistency ────────

ax = axes[2]
xs_c = np.arange(len(SWAPS), dtype=float)

for i, swap in enumerate(SWAPS):
    color = COLOR_CON if COLOR_CONSISTENT[swap] else COLOR_INC
    k, n = cued[swap]
    draw_acc_bar(ax, xs_c[i], k, n, color)

# Bracket
y_br = 72
con_xs_c = [xs_c[i] for i,s in enumerate(SWAPS) if COLOR_CONSISTENT[s]]
inc_xs_c = [xs_c[i] for i,s in enumerate(SWAPS) if not COLOR_CONSISTENT[s]]
for grp_xs, k, n, _ in [(con_xs_c, kcc, ncc, ''), (inc_xs_c, kci, nci, '')]:
    xL = grp_xs[0]-0.3; xR = grp_xs[-1]+0.3
    ax.plot([xL,xL,xR,xR],[y_br-2,y_br,y_br,y_br-2], color='#444', lw=0.9)
    ax.text((xL+xR)/2, y_br+0.5, f'{pct(k,n):.0f}%', ha='center', va='bottom',
            fontsize=8, color='#333')

ax.text(1.5, y_br+7, f'F3 = {f3_delta:+.1f}pp  {stars(f3_p)}',
        ha='center', va='bottom', fontsize=9, color='#6e2f8e', fontweight='bold')

ax.set_xticks(xs_c)
ax.set_xticklabels([SWAP_LABELS[s] for s in SWAPS], fontsize=9)
ax.set_xlim(-0.6, len(SWAPS)-0.4)
ax.axhline(CHANCE*100, color='#aaa', lw=1.0, ls='--', zorder=2)
ax.text(3.6, CHANCE*100, 'chance', fontsize=7, color='#999', va='center')
style(ax, 'C.  F3: Color field cueing\nCUED accuracy — dark=color consistent (N,Z), light=inconsistent (C,CZ)',
      ylabel='CUED % correct', ylim=(-5, 90))

patches_c = [mpatches.Patch(color=COLOR_CON, label='Color consistent (N, Z)'),
             mpatches.Patch(color=COLOR_INC, label='Color inconsistent (C, CZ)')]
ax.legend(handles=patches_c, fontsize=7.5, loc='lower right', framealpha=0.9)

# ── Footer ─────────────────────────────────────────────────────────────────────

fig.text(0.5, -0.03,
         'Panel A: delta bars = CUED − UNCUED; CI from propagated Wilson 95% CI; χ² significance  ·  '
         'Panels B/C: CUED accuracy bars; significance vs chance (z-test above bar); '
         'pooled contrast F2/F3 from χ² on pooled consistent vs inconsistent cells  ·  '
         '†p<.1  *p<.05  **p<.01  ***p<.001',
         ha='center', va='bottom', fontsize=7, color='#555')

plt.tight_layout()
plt.savefig(OUT, dpi=150, bbox_inches='tight', facecolor='white')
print(f"Saved: {OUT}")
