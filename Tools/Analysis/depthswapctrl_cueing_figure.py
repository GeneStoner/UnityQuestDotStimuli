#!/usr/bin/env python3
"""
depthswapctrl_cueing_figure.py
--------------------------------
Data figure for DepthSwapCtrl (binocular sessions) mirroring the
DecoupledDots depth×color 2×2 layout as closely as possible.

Three swap conditions: N (no swap) / ZdA (50% depth, coherent translator
changes plane) / ZdB (50% depth, non-coherent moves into cued plane).

Layout:
  Left 3 panels:  N / ZdA / ZdB — each with 4 bars:
                  CUED+Far, CUED+Near, UNCUED+Far, UNCUED+Near
                  + cueing-effect bracket (CUED-UNCUED, collapsed Near+Far)
  Right strip:    Cueing effect (CUED-UNCUED) per swap, collapsed over Near/Far
                  — mirrors the marginal panels in decoupled_dots_depth_color_2x2

Depth-field cueing labels (analogous to DecoupledDots F2):
  CUED+N   → Depth✓  (translator stays at Field B onset depth)
  CUED+ZdB → Depth✓  (coherent stays; non-coh moves into cued plane)
  CUED+ZdA → Depth✗  (coherent translator moves to opposite plane)
  UNCUED+N  → Depth✗ (translator ≠ delayed field onset depth by design)
  UNCUED+ZdA → Depth✓ (Field A sub-field now at Field B onset depth)
  UNCUED+ZdB → Depth✗

Sessions: 6 binocular DepthSwapCtrl sessions (260330_1853, 260331_0621,
          260401_1313, 260401_1349, 260401_1541, 260401_1705)
Output: Agents/Figures/depthswapctrl_cueing.pdf
"""

import csv, math, os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.patches as mpatches
from matplotlib.backends.backend_pdf import PdfPages

BASE    = os.path.normpath(os.path.join(os.path.dirname(__file__), '../../Agents/Figures'))
OUT_PDF = os.path.join(BASE, 'depthswapctrl_cueing.pdf')
DATA    = os.path.expanduser('~/Library/Application Support/ThatsRandom/VRDotsDataFiles')
CHANCE  = 1 / 8

SESSIONS_BINO = [
    f'{DATA}/vr_dots_session_260330_1853.tsv',
    f'{DATA}/vr_dots_session_260331_0621.tsv',
    f'{DATA}/vr_dots_session_260401_1313.tsv',
    f'{DATA}/vr_dots_session_260401_1349.tsv',
    f'{DATA}/vr_dots_session_260401_1541.tsv',
    f'{DATA}/vr_dots_session_260401_1705.tsv',
]

# ── Helpers ────────────────────────────────────────────────────────────────────
def is_correct(td, rd):
    d = (float(rd) - float(td) + 360) % 360
    return (360 - d if d > 180 else d) <= 22.5

def wilson_ci(k, n, z=1.96):
    if n == 0: return 0.0, 0.0
    p = k / n; d = 1 + z**2/n
    c = (p + z**2/(2*n)) / d
    hw = z * math.sqrt(p*(1-p)/n + z**2/(4*n**2)) / d
    return c - hw, c + hw

def pct_ci(k, n):
    if n == 0: return 0.0, 0.0, 0.0
    pct = k/n*100
    lo, hi = wilson_ci(k, n)
    return pct, pct - lo*100, hi*100 - pct

def prop_ztest(k1, n1, k2, n2):
    if n1 == 0 or n2 == 0: return 0.0, 0.0, 1.0
    p1, p2 = k1/n1, k2/n2
    pp = (k1+k2)/(n1+n2)
    se = math.sqrt(max(pp*(1-pp)*(1/n1+1/n2), 1e-12))
    z = (p1-p2)/se
    return (p1-p2)*100, z, math.erfc(abs(z)/math.sqrt(2))

def sig(p):
    if p < 0.001: return '***'
    if p < 0.01:  return '**'
    if p < 0.05:  return '*'
    if p < 0.10:  return '†'
    return 'n.s.'

# ── Load data ──────────────────────────────────────────────────────────────────
# Key: (cond, swap, depth)  where depth = 'Near' or 'Far'
# We determine translator depth:
#   CUED  → translator = Field B → trans_near = b_near
#   UNCUED → translator = Field A → trans_near = NOT b_near
counts = {}

for path in SESSIONS_BINO:
    with open(path, newline='') as f:
        for r in csv.DictReader(f, delimiter='\t'):
            if (not r.get('TransDeg','').strip() or
                    not r.get('RespDeg','').strip() or
                    r.get('EndKey','') in ('timeout','skip','requeue')):
                continue
            cond  = r['Cond']
            swap  = r['SwapType']
            b_near = (r['DelayedFieldDepth'] == 'N')
            trans_near = b_near if cond == 'CUED' else not b_near
            depth = 'Near' if trans_near else 'Far'
            key = (cond, swap, depth)
            if key not in counts: counts[key] = [0, 0]
            counts[key][0] += is_correct(r['TransDeg'], r['RespDeg'])
            counts[key][1] += 1

def get(cond, swap, depth=None):
    if depth:
        return counts.get((cond, swap, depth), [0, 0])
    # Pool Near + Far
    kn, nn = counts.get((cond, swap, 'Near'), [0, 0])
    kf, nf = counts.get((cond, swap, 'Far'),  [0, 0])
    return [kn+kf, nn+nf]

# Print summary
total = sum(v[1] for v in counts.values())
print(f'Total trials: {total}')
print(f'\n{"Cond":7} {"Swap":5} {"Depth":5}  {"Acc%":>6}  n')
for swap in ['N','ZdA','ZdB']:
    for cond in ['CUED','UNCUED']:
        for depth in ['Far','Near']:
            k, n = get(cond, swap, depth)
            if n: print(f'{cond:7} {swap:5} {depth:5}  {k/n*100:5.1f}%  {n}')
    print()

# ── Figure ─────────────────────────────────────────────────────────────────────
COL_CUED   = '#2c5f8a'
COL_UNCUED = '#aaaaaa'
COL_FAR    = '#44aa88'   # teal for Far
COL_NEAR   = '#8844aa'   # purple for Near
SWAP_ORDER = ['N', 'ZdA', 'ZdB']
SWAP_TITLES = {
    'N':   'N — no swap\n(baseline)',
    'ZdA': 'ZdA — 50% depth\n(coherent translator\nchanges plane)',
    'ZdB': 'ZdB — 50% depth\n(non-coherent moves\ninto cued plane)',
}
DEPTH_LABELS = {
    'N':   ('Depth✓ (CUED)', 'Depth✗ (UNCUED)'),
    'ZdA': ('Depth✗ (CUED)', 'Depth✓ (UNCUED)'),
    'ZdB': ('Depth✓ (CUED)', 'Depth✗ (UNCUED)'),
}

fig = plt.figure(figsize=(13, 7))
fig.suptitle(
    'Exp_DepthSwapCtrl_005m  ·  Dot cueing × depth swap  ·  '
    'Binocular  ·  6 sessions  ·  n=1152 trials',
    fontsize=10, fontweight='bold', y=0.99)

outer = gridspec.GridSpec(
    1, 4,
    width_ratios=[1, 1, 1, 0.55],
    hspace=0.0, wspace=0.32,
    top=0.88, bottom=0.18, left=0.07, right=0.97
)

BAR_W  = 0.32
PAIR_G = 0.08   # gap within Near/Far pair
GROUP_G = 0.55  # gap between CUED and UNCUED groups

for si, swap in enumerate(SWAP_ORDER):
    ax = fig.add_subplot(outer[si])
    cued_lbl, uncued_lbl = DEPTH_LABELS[swap]

    # Four bars: CUED+Far, CUED+Near | UNCUED+Far, UNCUED+Near
    x_cf = 0.0
    x_cn = BAR_W + PAIR_G
    x_uf = x_cn + BAR_W + GROUP_G
    x_un = x_uf + BAR_W + PAIR_G

    bar_specs = [
        (x_cf, 'CUED',   'Far',  COL_FAR,  COL_CUED),
        (x_cn, 'CUED',   'Near', COL_NEAR, COL_CUED),
        (x_uf, 'UNCUED', 'Far',  COL_FAR,  COL_UNCUED),
        (x_un, 'UNCUED', 'Near', COL_NEAR, COL_UNCUED),
    ]

    pcts, ehis = [], []
    for x, cond, depth, fill_col, edge_col in bar_specs:
        k, n = get(cond, swap, depth)
        pct, elo, ehi = pct_ci(k, n)
        pcts.append(pct); ehis.append(ehi)
        ax.bar(x, pct, width=BAR_W*0.88, color=fill_col,
               edgecolor=edge_col, linewidth=1.2, zorder=2, alpha=0.88)
        ax.errorbar(x, pct, yerr=[[elo],[ehi]],
                    fmt='none', ecolor='#222', elinewidth=1, capsize=3, zorder=3)
        ax.text(x, pct + ehi + 1.5, f'n={n}',
                ha='center', va='bottom', fontsize=5, color='#555')

    # Cueing effect bracket (CUED pool vs UNCUED pool)
    ck, cn = get('CUED',   swap)
    uk, un = get('UNCUED', swap)
    delta, z_val, p_val = prop_ztest(ck, cn, uk, un)
    top = max(p+e for p, e in zip(pcts, ehis)) + 8
    mid_c = (x_cf + x_cn + BAR_W) / 2
    mid_u = (x_uf + x_un + BAR_W) / 2
    ax.plot([mid_c, mid_c, mid_u, mid_u],
            [top, top+2, top+2, top], lw=0.8, color='#333')
    sign = '+' if delta >= 0 else ''
    ax.text((mid_c + mid_u)/2, top + 3,
            f'Dot cueing: {sign}{delta:.1f} pp   {sig(p_val)}',
            ha='center', va='bottom', fontsize=7.5, fontweight='bold',
            color='#1a3a8b' if p_val < 0.05 else '#666')

    # Depth-field cueing labels
    ax.text((x_cf + x_cn + BAR_W)/2, -7, cued_lbl,
            ha='center', va='top', fontsize=6.5, color='#1a3a8b',
            style='italic', clip_on=False)
    ax.text((x_uf + x_un + BAR_W)/2, -7, uncued_lbl,
            ha='center', va='top', fontsize=6.5, color='#884400',
            style='italic', clip_on=False)

    # CUED/UNCUED group labels
    ax.text((x_cf + x_cn + BAR_W)/2, -13, 'CUED',
            ha='center', va='top', fontsize=7.5, fontweight='bold',
            color=COL_CUED, clip_on=False)
    ax.text((x_uf + x_un + BAR_W)/2, -13, 'UNCUED',
            ha='center', va='top', fontsize=7.5, fontweight='bold',
            color='#666', clip_on=False)

    ax.axvline((x_cn + BAR_W + x_uf)/2, color='#cccccc', lw=0.8, ls='--')
    ax.axhline(CHANCE*100, color='#cc4444', lw=0.9, ls='--', zorder=1)
    ax.set_xlim(x_cf - BAR_W*0.7, x_un + BAR_W*1.2)
    ax.set_ylim(0, 90)
    ax.set_yticks([0, 12.5, 25, 50, 75])
    ax.set_yticklabels(['0','12.5','25','50','75'], fontsize=6.5)
    ax.yaxis.grid(True, lw=0.4, color='#e0e0e0', zorder=0)
    ax.set_axisbelow(True)
    ax.set_xticks([])
    ax.spines[['top','right','bottom']].set_visible(False)
    ax.set_title(SWAP_TITLES[swap], fontsize=8.5, fontweight='bold', pad=6)
    if si == 0:
        ax.set_ylabel('% correct', fontsize=9)

# ── Right strip: cueing effect per swap ───────────────────────────────────────
ax_r = fig.add_subplot(outer[3])

cue_colors = {'N': '#1a6b1a', 'ZdA': '#c0392b', 'ZdB': '#4477bb'}
xs = [0.0, 0.7, 1.4]

for i, swap in enumerate(SWAP_ORDER):
    ck, cn = get('CUED',   swap)
    uk, un = get('UNCUED', swap)
    delta, z_val, p_val = prop_ztest(ck, cn, uk, un)
    se_pp = math.sqrt(max(ck*(cn-ck)/cn**3 + uk*(un-uk)/un**3, 1e-9)) * 100
    col = cue_colors[swap]
    ax_r.bar(xs[i], delta, width=0.55, color=col, alpha=0.88, zorder=2)
    ax_r.errorbar(xs[i], delta, yerr=[[1.96*se_pp],[1.96*se_pp]],
                  fmt='none', ecolor='#333', elinewidth=1, capsize=3.5, zorder=3)
    ax_r.text(xs[i], delta/2, f'{delta:+.1f}pp',
              ha='center', va='center', fontsize=7, color='white', fontweight='bold')
    ax_r.text(xs[i], max(delta + 1.96*se_pp + 1, 1),
              sig(p_val), ha='center', va='bottom', fontsize=8,
              fontweight='bold', color=col)
    ax_r.text(xs[i], -3.5, swap, ha='center', va='top', fontsize=7.5,
              fontweight='bold', color=col, clip_on=False)

ax_r.axhline(0, color='#333', lw=0.8, ls='--', zorder=1)
ax_r.set_xlim(-0.45, 1.95)
ax_r.set_ylim(-5, 35)
ax_r.set_yticks([0, 10, 20, 30])
ax_r.set_yticklabels(['0','10','20','30'], fontsize=6.5)
ax_r.set_ylabel('Cueing Δ (pp)', fontsize=8)
ax_r.yaxis.grid(True, lw=0.4, color='#e0e0e0', zorder=0)
ax_r.set_axisbelow(True)
ax_r.set_xticks([])
ax_r.spines[['top','right','bottom']].set_visible(False)
ax_r.set_title('Cueing effect\n(CUED−UNCUED)', fontsize=8, fontweight='bold', pad=5)

# ── Legend ─────────────────────────────────────────────────────────────────────
handles = [
    mpatches.Patch(facecolor=COL_FAR,  edgecolor=COL_CUED,   lw=1.2, label='CUED + Far translator'),
    mpatches.Patch(facecolor=COL_NEAR, edgecolor=COL_CUED,   lw=1.2, label='CUED + Near translator'),
    mpatches.Patch(facecolor=COL_FAR,  edgecolor=COL_UNCUED, lw=1.2, label='UNCUED + Far translator'),
    mpatches.Patch(facecolor=COL_NEAR, edgecolor=COL_UNCUED, lw=1.2, label='UNCUED + Near translator'),
    mpatches.Patch(facecolor='none', edgecolor='#cc4444', linestyle='--', lw=0.9, label='Chance (12.5%)'),
]
fig.legend(handles=handles, loc='lower center', fontsize=7.5, ncol=5,
           bbox_to_anchor=(0.5, 0.01), framealpha=0.9)

os.makedirs(BASE, exist_ok=True)
with PdfPages(OUT_PDF) as pdf:
    pdf.savefig(fig, bbox_inches='tight')
plt.close(fig)
print(f'\nSaved: {OUT_PDF}')
