#!/usr/bin/env python3
"""
depthcolorlinked_cueing_figure.py
-----------------------------------
Data figure for DepthColorLinked (ZdA/ZdB, Near=Red, Far=Green,
linkDepthColor=1) mirroring the DecoupledDots depth×color 2×2 layout.

Two conditions (analogous to DecoupledDots depth rows):
  ZdNoi — translator stays in onset depth+color plane (Depth✓ for CUED)
           CUED+ZdB  /  UNCUED+ZdA
  ZdCoh — translator changes depth+color plane (Depth✗ for CUED)
           CUED+ZdA  /  UNCUED+ZdB

Each panel: 4 bars (CUED+Far, CUED+Near, UNCUED+Far, UNCUED+Near)
            + cueing-effect bracket (CUED−UNCUED, Near+Far pooled)
Right strip: cueing effect per condition (ZdNoi vs ZdCoh)

Sessions: 260404_0940, 260404_1123, 260406_1001, 260406_1034  (n=1024)
Output: Agents/Figures/depthcolorlinked_cueing.pdf
"""

import csv, math, os, datetime
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.patches as mpatches
from matplotlib.backends.backend_pdf import PdfPages

DATE_STR = datetime.date.today().strftime('%Y-%m-%d')

BASE    = os.path.normpath(os.path.join(os.path.dirname(__file__), '../../Agents/Figures'))
OUT_PDF = os.path.join(BASE, 'depthcolorlinked_cueing.pdf')
PULL2   = '/tmp/quest_pull2/files'
CHANCE  = 1 / 8

SESSIONS = [
    f'{PULL2}/vr_dots_session_260404_0940.tsv',
    f'{PULL2}/vr_dots_session_260404_1123.tsv',
    f'{PULL2}/vr_dots_session_260406_1001.tsv',
    f'{PULL2}/vr_dots_session_260406_1034.tsv',
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
# Key: (coh_label, cond, depth)
#   coh_label = 'ZdNoi' or 'ZdCoh' (translator perspective)
#   depth = 'Near' or 'Far' (translator depth)
counts = {}

for path in SESSIONS:
    if not os.path.exists(path):
        print(f'Missing: {path}'); continue
    with open(path, newline='') as f:
        for r in csv.DictReader(f, delimiter='\t'):
            if (not r.get('TransDeg','').strip() or
                    not r.get('RespDeg','').strip() or
                    r.get('EndKey','') in ('timeout','skip','requeue')):
                continue
            cond  = r['Cond']
            swap  = r['SwapType']   # ZdA or ZdB
            # ZdCoh = coherent translator changes plane:
            #   CUED+ZdA  or  UNCUED+ZdB
            coh = ((cond == 'CUED'   and swap == 'ZdA') or
                   (cond == 'UNCUED' and swap == 'ZdB'))
            coh_label = 'ZdCoh' if coh else 'ZdNoi'

            b_near = (r['DelayedFieldDepth'] == 'N')
            trans_near = b_near if cond == 'CUED' else not b_near
            depth = 'Near' if trans_near else 'Far'

            key = (coh_label, cond, depth)
            if key not in counts: counts[key] = [0, 0]
            counts[key][0] += is_correct(r['TransDeg'], r['RespDeg'])
            counts[key][1] += 1

def get(coh, cond, depth=None):
    if depth:
        return counts.get((coh, cond, depth), [0, 0])
    kn, nn = counts.get((coh, cond, 'Near'), [0, 0])
    kf, nf = counts.get((coh, cond, 'Far'),  [0, 0])
    return [kn+kf, nn+nf]

# Print summary
total = sum(v[1] for v in counts.values())
print(f'Total trials: {total}')
print(f'\n{"Coh":7} {"Cond":7} {"Depth":5}  {"Acc%":>6}  n')
for coh in ['ZdNoi','ZdCoh']:
    for cond in ['CUED','UNCUED']:
        for depth in ['Far','Near']:
            k, n = get(coh, cond, depth)
            if n: print(f'{coh:7} {cond:7} {depth:5}  {k/n*100:5.1f}%  {n}')
    print()

# Cueing effects
for coh in ['ZdNoi','ZdCoh']:
    ck, cn = get(coh,'CUED'); uk, un = get(coh,'UNCUED')
    d, z, p = prop_ztest(ck, cn, uk, un)
    print(f'{coh}: CUED={ck/cn*100:.1f}%  UNCUED={uk/un*100:.1f}%  '
          f'Δ={d:+.1f}pp  {sig(p)}')

# ── Figure ─────────────────────────────────────────────────────────────────────
COL_CUED   = '#2c5f8a'
COL_UNCUED = '#aaaaaa'
COL_FAR    = '#44aa88'
COL_NEAR   = '#8844aa'

PANEL_SPECS = [
    ('ZdNoi', 'ZdNoi  (translator stays in onset plane)',
     'Depth✓  Color✓ (CUED)', 'Depth✗  Color✗ (UNCUED)', '#1a6b1a'),
    ('ZdCoh', 'ZdCoh  (translator changes depth + color)',
     'Depth✗  Color✗ (CUED)', 'Depth✓  Color✓ (UNCUED)', '#c0392b'),
]

fig = plt.figure(figsize=(11, 7))
fig.suptitle(
    'Exp_DepthColorLinked_005m  ·  Dot cueing × depth-color swap  ·  '
    '4 sessions  ·  n=1024 trials  ·  Near=Red, Far=Green',
    fontsize=10, fontweight='bold', y=0.99)

outer = gridspec.GridSpec(
    1, 3,
    width_ratios=[1, 1, 0.55],
    hspace=0.0, wspace=0.32,
    top=0.88, bottom=0.20, left=0.08, right=0.97
)

BAR_W   = 0.32
PAIR_G  = 0.08
GROUP_G = 0.55

for pi, (coh, title, cued_lbl, uncued_lbl, title_col) in enumerate(PANEL_SPECS):
    ax = fig.add_subplot(outer[pi])

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
        k, n = get(coh, cond, depth)
        pct, elo, ehi = pct_ci(k, n)
        pcts.append(pct); ehis.append(ehi)
        ax.bar(x, pct, width=BAR_W*0.88, color=fill_col,
               edgecolor=edge_col, linewidth=1.2, zorder=2, alpha=0.88)
        ax.errorbar(x, pct, yerr=[[elo],[ehi]],
                    fmt='none', ecolor='#222', elinewidth=1, capsize=3, zorder=3)
        ax.text(x, pct + ehi + 1.5, f'n={n}',
                ha='center', va='bottom', fontsize=5, color='#555')

    # Cueing effect bracket (pooled Near+Far)
    ck, cn = get(coh, 'CUED'); uk, un = get(coh, 'UNCUED')
    delta, z_val, p_val = prop_ztest(ck, cn, uk, un)
    top = max(p+e for p, e in zip(pcts, ehis)) + 8
    mid_c = (x_cf + x_cn + BAR_W) / 2
    mid_u = (x_uf + x_un + BAR_W) / 2
    ax.plot([mid_c, mid_c, mid_u, mid_u],
            [top, top+2, top+2, top], lw=0.8, color='#333')
    sign = '+' if delta >= 0 else ''
    ax.text((mid_c+mid_u)/2, top+3,
            f'Dot cueing: {sign}{delta:.1f} pp   {sig(p_val)}',
            ha='center', va='bottom', fontsize=7.5, fontweight='bold',
            color='#1a3a8b' if p_val < 0.05 else '#666')

    # Depth-field cueing labels below groups
    ax.text((x_cf+x_cn+BAR_W)/2, -8, cued_lbl,
            ha='center', va='top', fontsize=6.5, color='#1a3a8b',
            style='italic', clip_on=False)
    ax.text((x_uf+x_un+BAR_W)/2, -8, uncued_lbl,
            ha='center', va='top', fontsize=6.5, color='#884400',
            style='italic', clip_on=False)

    ax.text((x_cf+x_cn+BAR_W)/2, -14.5, 'CUED',
            ha='center', va='top', fontsize=7.5, fontweight='bold',
            color=COL_CUED, clip_on=False)
    ax.text((x_uf+x_un+BAR_W)/2, -14.5, 'UNCUED',
            ha='center', va='top', fontsize=7.5, fontweight='bold',
            color='#666', clip_on=False)

    ax.axvline((x_cn+BAR_W+x_uf)/2, color='#cccccc', lw=0.8, ls='--')
    ax.axhline(CHANCE*100, color='#cc4444', lw=0.9, ls='--', zorder=1)
    ax.set_xlim(x_cf - BAR_W*0.7, x_un + BAR_W*1.2)
    ax.set_ylim(0, 80)
    ax.set_yticks([0, 12.5, 25, 50, 75])
    ax.set_yticklabels(['0','12.5','25','50','75'], fontsize=6.5)
    ax.yaxis.grid(True, lw=0.4, color='#e0e0e0', zorder=0)
    ax.set_axisbelow(True)
    ax.set_xticks([])
    ax.spines[['top','right','bottom']].set_visible(False)
    ax.set_title(title, fontsize=9, fontweight='bold', pad=6, color=title_col)
    if pi == 0:
        ax.set_ylabel('% correct', fontsize=9)

# ── Right strip: cueing effect ZdNoi vs ZdCoh ─────────────────────────────────
ax_r = fig.add_subplot(outer[2])
xs = [0.0, 0.7]
strip_cols = {'ZdNoi': '#1a6b1a', 'ZdCoh': '#c0392b'}
strip_labels = {'ZdNoi': 'ZdNoi\n(Depth✓)', 'ZdCoh': 'ZdCoh\n(Depth✗)'}

for i, coh in enumerate(['ZdNoi', 'ZdCoh']):
    ck, cn = get(coh,'CUED'); uk, un = get(coh,'UNCUED')
    delta, z_val, p_val = prop_ztest(ck, cn, uk, un)
    se_pp = math.sqrt(max(ck*(cn-ck)/cn**3 + uk*(un-uk)/un**3, 1e-9)) * 100
    col = strip_cols[coh]
    ax_r.bar(xs[i], delta, width=0.55, color=col, alpha=0.88, zorder=2)
    ax_r.errorbar(xs[i], delta, yerr=[[1.96*se_pp],[1.96*se_pp]],
                  fmt='none', ecolor='#333', elinewidth=1, capsize=3.5, zorder=3)
    ax_r.text(xs[i], delta/2, f'{delta:+.1f}pp',
              ha='center', va='center', fontsize=7.5, color='white', fontweight='bold')
    ax_r.text(xs[i], max(delta+1.96*se_pp+1, 1), sig(p_val),
              ha='center', va='bottom', fontsize=9, fontweight='bold', color=col)
    ax_r.text(xs[i], -3.5, strip_labels[coh],
              ha='center', va='top', fontsize=7, color=col,
              fontweight='bold', clip_on=False)

ax_r.axhline(0, color='#333', lw=0.8, ls='--', zorder=1)
ax_r.set_xlim(-0.45, 1.25)
ax_r.set_ylim(-5, 40)
ax_r.set_yticks([0, 10, 20, 30, 40])
ax_r.set_yticklabels(['0','10','20','30','40'], fontsize=6.5)
ax_r.set_ylabel('Cueing Δ (pp)', fontsize=8)
ax_r.yaxis.grid(True, lw=0.4, color='#e0e0e0', zorder=0)
ax_r.set_axisbelow(True)
ax_r.set_xticks([])
ax_r.spines[['top','right','bottom']].set_visible(False)
ax_r.set_title('Cueing effect\n(CUED−UNCUED)', fontsize=8, fontweight='bold', pad=5)

# ── Legend ─────────────────────────────────────────────────────────────────────
handles = [
    mpatches.Patch(facecolor=COL_FAR,  edgecolor=COL_CUED,   lw=1.2, label='CUED + Far translator  (Green)'),
    mpatches.Patch(facecolor=COL_NEAR, edgecolor=COL_CUED,   lw=1.2, label='CUED + Near translator  (Red)'),
    mpatches.Patch(facecolor=COL_FAR,  edgecolor=COL_UNCUED, lw=1.2, label='UNCUED + Far translator  (Green)'),
    mpatches.Patch(facecolor=COL_NEAR, edgecolor=COL_UNCUED, lw=1.2, label='UNCUED + Near translator  (Red)'),
    mpatches.Patch(facecolor='none', edgecolor='#cc4444', linestyle='--', lw=0.9, label='Chance (12.5%)'),
]
fig.legend(handles=handles, loc='lower center', fontsize=7.5, ncol=3,
           bbox_to_anchor=(0.5, 0.01), framealpha=0.9)

fig.text(0.01, 0.005, f'{os.path.basename(OUT_PDF)}  ·  {DATE_STR}', fontsize=5, color='#888888', ha='left', va='bottom')
fig.text(0.99, 0.005, f'p. 1/1', fontsize=5, color='#888888', ha='right', va='bottom')
os.makedirs(BASE, exist_ok=True)
with PdfPages(OUT_PDF) as pdf:
    pdf.savefig(fig, bbox_inches='tight')
plt.close(fig)
print(f'\nSaved: {OUT_PDF}')
