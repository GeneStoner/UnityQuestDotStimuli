#!/usr/bin/env python3
"""
decoupled_dots_depth_color_2x2.py
-----------------------------------
Visualises the depth-swap × color-swap factorial for DecoupledDots,
with dot cueing (CUED vs UNCUED) as the performance axis.

2×2 layout:
  rows    = depth swapped at tStart?   No (N, C)  /  Yes (Z, CZ)
  columns = color swapped at tStart?   No (N, Z)  /  Yes (C, CZ)

Each cell: paired CUED / UNCUED bars + cueing-effect (Δ) annotation.
Right margin strip: row and column marginals (depth effect, color effect).

Output: Agents/Figures/decoupled_dots_depth_color_2x2.pdf
"""

import csv, math, os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.patches as mpatches
from matplotlib.backends.backend_pdf import PdfPages

BASE    = os.path.normpath(os.path.join(os.path.dirname(__file__), '../../Agents/Figures'))
OUT_PDF = os.path.join(BASE, 'decoupled_dots_depth_color_2x2.pdf')
PULL2   = '/tmp/quest_pull2/files'
PULL3   = '/tmp/quest_pull3/files'
CHANCE  = 1 / 8

SESSIONS = [
    (f'{PULL2}/vr_dots_session_260406_1532.tsv', False),
    (f'{PULL2}/vr_dots_session_260406_1754.tsv', True),
    (f'{PULL3}/vr_dots_session_260407_0643.tsv', True),
    (f'{PULL3}/vr_dots_session_260407_0731.tsv', False),
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

def z2p(z):
    return math.erfc(abs(z) / math.sqrt(2))

def prop_ztest(k1, n1, k2, n2):
    """Two-proportion z-test (two-tailed). Returns (delta_pp, z, p)."""
    if n1 == 0 or n2 == 0: return 0.0, 0.0, 1.0
    p1, p2 = k1/n1, k2/n2
    pp = (k1+k2)/(n1+n2)
    se = math.sqrt(max(pp*(1-pp)*(1/n1+1/n2), 1e-12))
    z = (p1-p2)/se
    return (p1-p2)*100, z, z2p(z)

def sig(p):
    if p < 0.001: return '***'
    if p < 0.01:  return '**'
    if p < 0.05:  return '*'
    if p < 0.10:  return '†'
    return 'n.s.'

# ── Load data ──────────────────────────────────────────────────────────────────
counts = {}   # (cond, swap) → [hits, n]
for path, is_inv in SESSIONS:
    with open(path, newline='') as f:
        for r in csv.DictReader(f, delimiter='\t'):
            if (not r.get('TransDeg','').strip() or
                    not r.get('RespDeg','').strip() or
                    r.get('EndKey','') in ('timeout','skip','requeue')):
                continue
            cond = r['Cond']
            if is_inv:
                cond = 'UNCUED' if cond == 'CUED' else 'CUED'
            key = (cond, r['SwapType'])
            if key not in counts: counts[key] = [0, 0]
            counts[key][0] += is_correct(r['TransDeg'], r['RespDeg'])
            counts[key][1] += 1

def get(cond, swap):
    return counts.get((cond, swap), [0, 0])

# ── 2×2 cell definitions ───────────────────────────────────────────────────────
# (swap, depth_swap, color_swap, row_label, col_label)
CELLS = {
    (0, 0): ('N',  'No depth swap',  'No color swap'),
    (0, 1): ('C',  'No depth swap',  'Color swapped'),
    (1, 0): ('Z',  'Depth swapped',  'No color swap'),
    (1, 1): ('CZ', 'Depth swapped',  'Color swapped'),
}

COL_CUED   = '#2c5f8a'
COL_UNCUED = '#aaaaaa'
BAR_W = 0.38
GAP   = 0.12

# ── Figure ─────────────────────────────────────────────────────────────────────
fig = plt.figure(figsize=(10, 9))
fig.suptitle(
    'Exp_DecoupledDots_005m  ·  Depth swap × Color swap  ·  '
    'Dot cueing (CUED vs UNCUED)  ·  n=2051 trials',
    fontsize=10, fontweight='bold', y=0.99)

# Outer: 2 rows × 3 cols (last col = marginals)
outer = gridspec.GridSpec(
    2, 3,
    width_ratios=[1, 1, 0.55],
    hspace=0.45, wspace=0.32,
    top=0.91, bottom=0.13, left=0.09, right=0.97
)

row_labels  = ['No depth swap\n(N, C)', 'Depth swapped\n(Z, CZ)']
col_labels  = ['No color swap\n(N, Z)', 'Color swapped\n(C, CZ)']
row_colors  = ['#1a6b1a', '#c0392b']   # green = no-depth, red = depth swap
col_colors  = ['#1a1a8b', '#cc7700']   # blue = no-color, orange = color swap

# ── Draw each 2×2 cell ────────────────────────────────────────────────────────
for ri in range(2):
    for ci in range(2):
        swap, dlbl, clbl = CELLS[(ri, ci)]
        ax = fig.add_subplot(outer[ri, ci])

        ck, cn = get('CUED',   swap)
        uk, un = get('UNCUED', swap)

        cued_pct,  cued_elo,  cued_ehi  = pct_ci(ck, cn)
        uncued_pct, uncued_elo, uncued_ehi = pct_ci(uk, un)
        delta, z, p = prop_ztest(ck, cn, uk, un)

        x_c = 0.0
        x_u = BAR_W + GAP

        ax.bar(x_c, cued_pct,   width=BAR_W, color=COL_CUED,   zorder=2, alpha=0.88)
        ax.bar(x_u, uncued_pct, width=BAR_W, color=COL_UNCUED, zorder=2, alpha=0.88)
        ax.errorbar(x_c, cued_pct,   yerr=[[cued_elo],  [cued_ehi]],
                    fmt='none', ecolor='#222', elinewidth=1.1, capsize=3.5, zorder=3)
        ax.errorbar(x_u, uncued_pct, yerr=[[uncued_elo],[uncued_ehi]],
                    fmt='none', ecolor='#222', elinewidth=1.1, capsize=3.5, zorder=3)

        ax.text(x_c, cued_pct + cued_ehi + 2,   f'n={cn}', ha='center', va='bottom', fontsize=5.5, color='#555')
        ax.text(x_u, uncued_pct + uncued_ehi + 2, f'n={un}', ha='center', va='bottom', fontsize=5.5, color='#555')

        ax.text(x_c, -9, 'CUED',   ha='center', va='top', fontsize=7.5, fontweight='bold', color=COL_CUED,   clip_on=False)
        ax.text(x_u, -9, 'UNCUED', ha='center', va='top', fontsize=7.5, fontweight='bold', color=COL_UNCUED, clip_on=False)

        # Cueing-effect bracket + annotation
        top = max(cued_pct + cued_ehi, uncued_pct + uncued_ehi) + 8
        ax.plot([x_c, x_c, x_u+BAR_W, x_u+BAR_W],
                [top, top+2, top+2, top], lw=0.8, color='#444')
        sign = '+' if delta >= 0 else ''
        p_str = f'p<0.001' if p < 0.001 else f'p={p:.3f}'
        ax.text((x_c + x_u + BAR_W)/2, top + 3,
                f'Δ = {sign}{delta:.1f} pp   {sig(p)}',
                ha='center', va='bottom', fontsize=7, color='#222')

        ax.axhline(CHANCE*100, color='#cc4444', lw=0.9, ls='--', zorder=1)
        ax.set_xlim(-0.4, x_u + BAR_W + 0.35)
        ax.set_ylim(0, 80)
        ax.set_yticks([0, 12.5, 25, 50, 75])
        ax.set_yticklabels(['0','12.5','25','50','75'], fontsize=6.5)
        ax.yaxis.grid(True, lw=0.4, color='#e0e0e0', zorder=0)
        ax.set_axisbelow(True)
        ax.set_xticks([])
        ax.spines[['top','right','bottom']].set_visible(False)
        if ci == 0:
            ax.set_ylabel('% correct', fontsize=8)

        # Swap label as cell title
        ax.set_title(f'Swap = {swap}', fontsize=9, fontweight='bold',
                     color='#1a1a1a', pad=5)

        # Row / col header labels (top row and left col only)
        if ri == 0:
            ax.text(0.5, 1.22, col_labels[ci], ha='center', va='bottom',
                    fontsize=8, color=col_colors[ci], fontweight='bold',
                    transform=ax.transAxes)
        if ci == 0:
            ax.text(-0.32, 0.5, row_labels[ri], ha='right', va='center',
                    fontsize=8, color=row_colors[ri], fontweight='bold',
                    rotation=90, transform=ax.transAxes)

# ── Marginal panels (right column) ────────────────────────────────────────────
# Top right: depth effect (collapse over color)
# Bottom right: color effect (collapse over depth)

MARGINALS = [
    # (row_in_grid, title, (swap_A_label, swaps_A), (swap_B_label, swaps_B), color_A, color_B)
    (0, 'Depth swap effect\n(collapsed over color)',
        ('No depth\n(N+C)',  ['N','C']),
        ('Depth\n(Z+CZ)',    ['Z','CZ']),
        '#1a6b1a', '#c0392b'),
    (1, 'Color swap effect\n(collapsed over depth)',
        ('No color\n(N+Z)',  ['N','Z']),
        ('Color\n(C+CZ)',    ['C','CZ']),
        '#1a1a8b', '#cc7700'),
]

for row_idx, title, (lbl_a, swaps_a), (lbl_b, swaps_b), col_a, col_b in MARGINALS:
    ax = fig.add_subplot(outer[row_idx, 2])

    # Pool cueing effects across the two swap sets
    def cueing_pp(swaps):
        ck = cn = uk = un = 0
        for s in swaps:
            k_, n_ = get('CUED', s)
            ck += k_; cn += n_
            k_, n_ = get('UNCUED', s)
            uk += k_; un += n_
        delta, z, p = prop_ztest(ck, cn, uk, un)
        se_pp = math.sqrt(max(ck*(cn-ck)/cn**3 + uk*(un-uk)/un**3, 1e-9)) * 100
        return delta, 1.96*se_pp, p, cn

    da, se_a, pa, na = cueing_pp(swaps_a)
    db, se_b, pb, nb = cueing_pp(swaps_b)

    xs = [0.0, 0.75]
    for x, val, se, p_val, lbl, col, n in [
            (xs[0], da, se_a, pa, lbl_a, col_a, na),
            (xs[1], db, se_b, pb, lbl_b, col_b, nb)]:
        ax.bar(x, val, width=0.55, color=col, alpha=0.88, zorder=2)
        ax.errorbar(x, val, yerr=[[se],[se]], fmt='none',
                    ecolor='#222', elinewidth=1.1, capsize=3.5, zorder=3)
        ax.text(x, max(val+se+1, 1), f'{sig(p_val)}', ha='center', va='bottom',
                fontsize=8, fontweight='bold', color=col)
        ax.text(x, -3.5, lbl, ha='center', va='top', fontsize=6.5,
                color=col, fontweight='bold', clip_on=False)
        ax.text(x, val/2, f'{val:+.1f}pp', ha='center', va='center',
                fontsize=7, color='white', fontweight='bold')

    ax.axhline(0, color='#333', lw=0.8, ls='--', zorder=1)
    ax.set_xlim(-0.45, 1.25)
    ax.set_ylim(-5, 35)
    ax.set_yticks([0, 10, 20, 30])
    ax.set_yticklabels(['0','10','20','30'], fontsize=6.5)
    ax.set_ylabel('Cueing Δ (pp)', fontsize=7.5)
    ax.yaxis.grid(True, lw=0.4, color='#e0e0e0', zorder=0)
    ax.set_axisbelow(True)
    ax.set_xticks([])
    ax.spines[['top','right','bottom']].set_visible(False)
    ax.set_title(title, fontsize=7.5, fontweight='bold', pad=5)

# ── Legend ─────────────────────────────────────────────────────────────────────
handles = [
    mpatches.Patch(facecolor=COL_CUED,   label='CUED (dot temporal cue present)'),
    mpatches.Patch(facecolor=COL_UNCUED, label='UNCUED (dot temporal cue absent)'),
    mpatches.Patch(facecolor='none', edgecolor='#cc4444', linestyle='--', linewidth=0.9,
                   label='Chance (12.5%)'),
]
fig.legend(handles=handles, loc='lower center', fontsize=8, ncol=3,
           bbox_to_anchor=(0.5, 0.01), framealpha=0.9)

os.makedirs(BASE, exist_ok=True)
with PdfPages(OUT_PDF) as pdf:
    pdf.savefig(fig, bbox_inches='tight')
plt.close(fig)
print(f'Saved: {OUT_PDF}')
