#!/usr/bin/env python3
"""
session_260413_figure.py

Standard performance figure for session 260413_1406
(DecoupledDots_005m_v2, n=512).

Page 1:
  Panel A  — CUED vs UNCUED × swap (N/C/Z/CZ), Near & Far sub-bars
  Panel B  — Factor summary bars (F1 dot, F2 depth, F3 color, F4 Far−Near)
  Panel C  — Response direction bias on wrong trials:
             % wrong→90° (up) and % wrong→270° (down) per condition

Output:
  Tools/Analysis/Figures/session_260413_figure.pdf
"""

import csv, math, os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.patches as mpatches
from scipy.stats import chi2_contingency

DATA = "/tmp/quest_pull12/vr_dots_session_260413_1406.tsv"

BASE = os.path.normpath(os.path.join(os.path.dirname(__file__), 'Figures'))
os.makedirs(BASE, exist_ok=True)
OUT_PDF = os.path.join(BASE, 'session_260413_figure.pdf')

CHANCE = 1 / 8
SWAP_ORDER = ['N', 'C', 'Z', 'CZ']
SWAP_LABELS = {'N': 'N\n(baseline)', 'C': 'C\n(color swap)',
               'Z': 'Z\n(depth swap)', 'CZ': 'CZ\n(color+depth)'}

C_CUED_NEAR  = '#1a5276'
C_CUED_FAR   = '#5dade2'
C_UNCUED_NEAR = '#7b241c'
C_UNCUED_FAR  = '#f1948a'

# ── Stats ──────────────────────────────────────────────────────────────────────

def is_correct(td, rd):
    d = (float(rd) - float(td) + 360) % 360
    return (360 - d if d > 180 else d) <= 22.5

def pct(k, n):
    return k / n * 100 if n > 0 else 0.0

def wilson_ci(k, n, z=1.96):
    if n == 0: return 0.0, 0.0
    p = k / n; denom = 1 + z**2 / n
    c = (p + z**2 / (2*n)) / denom
    hw = z * math.sqrt(p*(1-p)/n + z**2/(4*n**2)) / denom
    return (c - hw) * 100, (c + hw) * 100

def chi2_p(k1, n1, k2, n2):
    if n1 == 0 or n2 == 0: return float('nan'), 1.0
    t = [[k1, n1-k1], [k2, n2-k2]]
    _, pval, _, _ = chi2_contingency(t, correction=False)
    return pval

def stars(p):
    if math.isnan(p): return ''
    return '***' if p < .001 else '**' if p < .01 else '*' if p < .05 else '†' if p < .1 else 'n.s.'

def sig_vs_chance(k, n):
    if n == 0: return ''
    p = k / n
    se = math.sqrt(max(CHANCE * (1-CHANCE) / n, 1e-12))
    z = (p - CHANCE) / se
    pval = 2 * (0.5 * (1 + math.erf(-abs(z) / math.sqrt(2))))
    return stars(pval)

# ── Load ───────────────────────────────────────────────────────────────────────

rows = []
with open(DATA, newline='') as f:
    for r in csv.DictReader(f, delimiter='\t'):
        if not r.get('TransDeg','').strip() or not r.get('RespDeg','').strip():
            continue
        if r.get('EndKey','') in ('timeout','skip','requeue'):
            continue
        td  = float(r['TransDeg'])
        rd  = float(r['RespDeg'])
        rows.append(dict(
            cond  = r['Cond'],
            swap  = r['SwapType'],
            depth = r['DelayedFieldDepth'],   # N=Near, F=Far translating field
            td=td, rd=rd,
            correct = int(is_correct(td, rd))
        ))

n_total = len(rows)

def cell(filt):
    sub = [r for r in rows if filt(r)]
    k = sum(r['correct'] for r in sub)
    return k, len(sub)

def wrong_dir_pct(filt, target_deg):
    sub = [r for r in rows if filt(r) and r['correct'] == 0]
    if len(sub) == 0: return 0.0, 0
    hit = sum(1 for r in sub if round(r['rd'] / 45) * 45 % 360 == target_deg)
    return hit / len(sub) * 100, len(sub)

# ── Style ──────────────────────────────────────────────────────────────────────

def style_ax(ax, title='', ylim=(-5, 85)):
    ax.axhline(CHANCE * 100, color='#AAAAAA', lw=1.0, ls='--', zorder=2)
    ax.text(1.01, CHANCE * 100, 'chance\n(12.5%)',
            transform=ax.get_yaxis_transform(), fontsize=6, color='#999', va='center')
    ax.set_ylim(*ylim)
    ax.set_title(title, fontsize=9, fontweight='bold', pad=5)
    ax.set_ylabel('% correct', fontsize=8)
    ax.tick_params(labelsize=8)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.grid(axis='y', lw=0.4, alpha=0.3, zorder=0)

def draw_bar(ax, x, k, n, color, width=0.28, hatch=None, label=None):
    p = pct(k, n)
    lo, hi = wilson_ci(k, n)
    ax.bar(x, p, width, color=color, alpha=0.88, zorder=3,
           label=label, edgecolor='white', linewidth=0.5, hatch=hatch)
    ax.errorbar(x, p, yerr=[[p - lo], [hi - p]], fmt='none',
                color='#333', capsize=3, capthick=1.0, lw=1.0, zorder=4)
    # small sig label above chance
    s = sig_vs_chance(k, n)
    if s and s not in ('n.s.', ''):
        ax.text(x, hi + 1.5, s, ha='center', va='bottom', fontsize=7,
                color='#222', fontweight='bold')
    # k/n inside bar
    if p > 14:
        ax.text(x, p / 2, f'{p:.0f}%', ha='center', va='center',
                fontsize=6.5, color='white', fontweight='bold')
    return p, lo, hi

# ── Figure ─────────────────────────────────────────────────────────────────────

fig = plt.figure(figsize=(15, 11))
fig.patch.set_facecolor('white')
fig.suptitle(
    f'Session 260413_1406  ·  DecoupledDots_005m_v2  ·  n={n_total}\n'
    'CUED (blue) = cue marks translator  ·  Near/Far = translating field depth',
    fontsize=11, fontweight='bold', y=0.99)

gs = gridspec.GridSpec(2, 3, top=0.92, bottom=0.07,
                       left=0.07, right=0.97,
                       hspace=0.48, wspace=0.35)

ax_a = fig.add_subplot(gs[0, 0:2])   # main panel
ax_b = fig.add_subplot(gs[0, 2])     # factor summary
ax_c = fig.add_subplot(gs[1, 0:3])   # response direction bias

# ── Panel A: main performance bars (CUED/UNCUED × swap × Near/Far) ─────────────

bar_w = 0.22
gap   = 0.04
group_gap = 0.45

xticks, xlabels = [], []
for gi, swap in enumerate(SWAP_ORDER):
    x0 = gi * (4 * bar_w + 3 * gap + group_gap)

    specs = [
        ('CUED',   'N', C_CUED_NEAR,   ''),
        ('CUED',   'F', C_CUED_FAR,    ''),
        ('UNCUED', 'N', C_UNCUED_NEAR, '//'),
        ('UNCUED', 'F', C_UNCUED_FAR,  '//'),
    ]
    xs = [x0 + i * (bar_w + gap) for i in range(4)]

    for xi, (cond, depth, color, hatch) in zip(xs, specs):
        k, n = cell(lambda r, c=cond, s=swap, d=depth:
                    r['cond']==c and r['swap']==s and r['depth']==d)
        lbl = None
        if gi == 0:
            lbl = f"CUED {'Near' if depth=='N' else 'Far'}" if cond == 'CUED' \
                  else f"UNCUED {'Near' if depth=='N' else 'Far'}"
        draw_bar(ax_a, xi, k, n, color, width=bar_w, hatch=hatch, label=lbl)

    # cueing effect bracket (CUED vs UNCUED, collapsed over depth)
    kc, nc = cell(lambda r, s=swap: r['cond']=='CUED'   and r['swap']==s)
    ku, nu = cell(lambda r, s=swap: r['cond']=='UNCUED' and r['swap']==s)
    pval = chi2_p(kc, nc, ku, nu)
    eff = pct(kc, nc) - pct(ku, nu)
    y_br = 72
    xL = xs[0] - bar_w/2
    xR = xs[3] + bar_w/2
    ax_a.plot([xL, xL, xR, xR], [y_br-1.5, y_br, y_br, y_br-1.5],
              color='#444', lw=0.8)
    ax_a.text((xL + xR) / 2, y_br + 0.5,
              f'Δ{eff:+.1f}pp {stars(pval)}',
              ha='center', va='bottom', fontsize=7.5, color='#222', fontweight='bold')

    group_center = (xs[0] + xs[3]) / 2
    xticks.append(group_center)
    xlabels.append(SWAP_LABELS[swap])

ax_a.set_xticks(xticks)
ax_a.set_xticklabels(xlabels, fontsize=8.5)
style_ax(ax_a, title='A.  Performance by swap condition  (Near/Far = translating field depth)',
         ylim=(-5, 85))

patches = [
    mpatches.Patch(color=C_CUED_NEAR,   label='CUED Near'),
    mpatches.Patch(color=C_CUED_FAR,    label='CUED Far'),
    mpatches.Patch(color=C_UNCUED_NEAR, label='UNCUED Near', hatch='//'),
    mpatches.Patch(color=C_UNCUED_FAR,  label='UNCUED Far',  hatch='//'),
]
ax_a.legend(handles=patches, fontsize=7, loc='upper right', framealpha=0.9,
            ncol=2, handlelength=1.5)

# ── Panel B: factor summary ─────────────────────────────────────────────────────

factors = [
    ('F1\nDot cueing',
     cell(lambda r: r['cond']=='CUED'   and r['swap']=='N'),
     cell(lambda r: r['cond']=='UNCUED' and r['swap']=='N'),
     '#1a5276', '#aed6f1'),
    ('F2\nDepth disrupt',
     cell(lambda r: r['cond']=='CUED'   and r['swap']=='N'),
     cell(lambda r: r['cond']=='CUED'   and r['swap']=='Z'),
     '#1d6a4a', '#a9dfbf'),
    ('F3\nColor',
     cell(lambda r: r['cond']=='CUED'   and r['swap']=='N'),
     cell(lambda r: r['cond']=='CUED'   and r['swap']=='C'),
     '#7e5109', '#f9e79f'),
    ('F4\nFar − Near',
     cell(lambda r: r['swap']=='N' and r['depth']=='F'),
     cell(lambda r: r['swap']=='N' and r['depth']=='N'),
     '#4477bb', '#cc4444'),
]

for fi, (lbl, (k1,n1), (k2,n2), c1, c2) in enumerate(factors):
    x1, x2 = fi * 1.2, fi * 1.2 + 0.5
    p1 = draw_bar(ax_b, x1, k1, n1, c1, width=0.42)[0]
    p2 = draw_bar(ax_b, x2, k2, n2, c2, width=0.42)[0]
    pval = chi2_p(k1, n1, k2, n2)
    eff = pct(k1, n1) - pct(k2, n2)
    y_br = 72
    ax_b.plot([x1 - 0.21, x1 - 0.21, x2 + 0.21, x2 + 0.21],
              [y_br-1, y_br, y_br, y_br-1], color='#444', lw=0.7)
    ax_b.text((x1 + x2) / 2, y_br + 0.5,
              f'{eff:+.1f}pp\n{stars(pval)}',
              ha='center', va='bottom', fontsize=7, color='#222', fontweight='bold')
    ax_b.text((x1 + x2) / 2, -5, lbl,
              ha='center', va='top', fontsize=7.5, color='#333')

ax_b.set_xticks([])
ax_b.set_xlim(-0.4, len(factors) * 1.2 - 0.3)
style_ax(ax_b, title='B.  Factor summary', ylim=(-12, 85))

# ── Panel C: response direction bias on wrong trials ──────────────────────────

# Show % wrong→90° (up) and % wrong→270° (down) for each cond×swap
# Highlight bars that exceed 2× chance (2 × 14.3% = 28.6%)

EXPECTED = 100 / 7   # ~14.3% per direction

conditions = []
for cond in ['CUED', 'UNCUED']:
    for swap in ['N', 'C', 'Z', 'CZ']:
        up_pct, n_wrong = wrong_dir_pct(
            lambda r, c=cond, s=swap: r['cond']==c and r['swap']==s, 90)
        dn_pct, _       = wrong_dir_pct(
            lambda r, c=cond, s=swap: r['cond']==c and r['swap']==s, 270)
        conditions.append((f'{cond}\n{swap}', up_pct, dn_pct, n_wrong,
                           cond, swap))

n_conds = len(conditions)
xs = np.arange(n_conds)
bar_w2 = 0.32
gap2   = 0.06

for i, (lbl, up, dn, n_wrong, cond, swap) in enumerate(conditions):
    x_up = xs[i] - bar_w2/2 - gap2/2
    x_dn = xs[i] + bar_w2/2 + gap2/2

    # upward bar
    up_color = '#c0392b' if up > 2 * EXPECTED else '#e8a5a0'
    ax_c.bar(x_up, up, bar_w2, color=up_color, zorder=3,
             label='→90° (up)' if i == 0 else None)
    ax_c.text(x_up, up + 0.8, f'{up:.0f}%', ha='center', va='bottom',
              fontsize=7, color='#222',
              fontweight='bold' if up > 2 * EXPECTED else 'normal')

    # downward bar
    dn_color = '#2471a3' if dn > 2 * EXPECTED else '#a9cce3'
    ax_c.bar(x_dn, dn, bar_w2, color=dn_color, zorder=3,
             label='→270° (down)' if i == 0 else None)
    ax_c.text(x_dn, dn + 0.8, f'{dn:.0f}%', ha='center', va='bottom',
              fontsize=7, color='#222',
              fontweight='bold' if dn > 2 * EXPECTED else 'normal')

    ax_c.text(xs[i], -6, lbl, ha='center', va='top', fontsize=7.5, color='#333')
    ax_c.text(xs[i], -12, f'n_wrong={n_wrong}', ha='center', va='top',
              fontsize=6, color='#777')

# Chance reference and 2× threshold
ax_c.axhline(EXPECTED, color='#888', lw=1.0, ls='--', zorder=2)
ax_c.axhline(2 * EXPECTED, color='#c0392b', lw=0.8, ls=':', alpha=0.6, zorder=2)
ax_c.text(n_conds - 0.4, EXPECTED + 0.5, 'expected\n(14.3%)',
          fontsize=6.5, color='#888', va='bottom')
ax_c.text(n_conds - 0.4, 2 * EXPECTED + 0.5, '2× expected\n(28.6%)',
          fontsize=6.5, color='#c0392b', va='bottom', alpha=0.8)

ax_c.set_xticks(xs)
ax_c.set_xticklabels(['' for _ in conditions])
ax_c.set_xlim(-0.7, n_conds - 0.3)
ax_c.set_ylim(-16, 95)
ax_c.set_ylabel('% of wrong trials\ngoing to direction', fontsize=8)
ax_c.set_title('C.  Response direction bias on wrong trials  '
               '(red = →90° up,  blue = →270° down;  bold/dark = >2× expected)',
               fontsize=9, fontweight='bold', pad=5)
ax_c.spines['top'].set_visible(False)
ax_c.spines['right'].set_visible(False)
ax_c.grid(axis='y', lw=0.4, alpha=0.3, zorder=0)
ax_c.legend(fontsize=8, loc='upper left', framealpha=0.9)

# Separator lines between CUED and UNCUED
ax_c.axvline(3.5, color='#ccc', lw=1.2, ls='-', zorder=1)
ax_c.text(1.5, 90, 'CUED', ha='center', va='top', fontsize=9,
          color='#1a5276', fontweight='bold')
ax_c.text(5.5, 90, 'UNCUED', ha='center', va='top', fontsize=9,
          color='#7b241c', fontweight='bold')

# ── Footer ─────────────────────────────────────────────────────────────────────

fig.text(0.5, 0.01,
         'Wilson 95% CI  ·  Sig vs chance (dashed): z-test  ·  '
         'Factor Δ: two-sided Pearson χ²  ·  '
         '†p<.1  *p<.05  **p<.01  ***p<.001  ·  '
         'Direction bias expected ~14.3%/direction (8-AFC, 7 wrong directions)',
         ha='center', va='bottom', fontsize=6.5, color='#555')

fig.text(0.01, 0.005, f'session_260413_figure.pdf', fontsize=5, color='#888', ha='left')

plt.savefig(OUT_PDF, bbox_inches='tight', facecolor='white')
print(f"Saved: {OUT_PDF}")
