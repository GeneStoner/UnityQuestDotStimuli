#!/usr/bin/env python3
"""
decoupled_dots_factor_performance.py

Six-panel figure — all 4 DecoupledDots sessions combined (n≈2051):

  Row 0: Raw % correct for the cued vs uncued arm of each factor
    (A) Dot cueing:         CUED vs UNCUED (temporal onset)
    (B) Depth-field cueing: depth-cued✓ vs depth-uncued✗
    (C) Color-field cueing: color-cued✓ vs color-uncued✗

  Row 1: Pairwise comparisons of the three "cued" arms
    (D) Dot-cued vs Depth-cued
    (E) Dot-cued vs Color-cued
    (F) Depth-cued vs Color-cued

Factor definitions (fully orthogonal 2³ design):
  Dot-cued ✓      = CUED condition (temporal onset marks translator)
  Depth-cued ✓    = translator ends in same depth plane delayed field first appeared:
                    {CUED+N, CUED+C, UNCUED+Z, UNCUED+CZ}
  Color-cued ✓    = translator color matches delayed field's original color:
                    {CUED+N, CUED+Z, UNCUED+C, UNCUED+CZ}

Output:
  Agents/Figures/decoupled_dots_factor_performance.png
  Agents/Figures/decoupled_dots_factor_performance.pdf
"""

import csv, datetime, math, os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.stats import chi2_contingency

DATE_STR = datetime.date.today().strftime('%Y-%m-%d')

# ── Paths ──────────────────────────────────────────────────────────────────────
SESSIONS = [
    ("/tmp/quest_pull2/files/vr_dots_session_260406_1532.tsv", False),
    ("/tmp/quest_pull2/files/vr_dots_session_260406_1754.tsv", True),
    ("/tmp/quest_pull3/files/vr_dots_session_260407_0643.tsv", True),
    ("/tmp/quest_pull3/files/vr_dots_session_260407_0731.tsv", False),
]

FIG_DIR    = os.path.expanduser("~/Projects/ObjectBasedAttention/VRDots/Agents/Figures/")
FIG_DIR_SP = os.path.expanduser("~/Projects/ObjectBasedAttention/VRDots/Agents/SwapPilot/Figures/")
OUT_PNG    = os.path.join(FIG_DIR,    "decoupled_dots_factor_performance.png")
OUT_PDF    = os.path.join(FIG_DIR,    "decoupled_dots_factor_performance.pdf")
OUT_PDF_SP = os.path.join(FIG_DIR_SP, "decoupled_dots_factor_performance.pdf")

CHANCE = 1 / 8  # 8-AFC

DEPTH_FIELD_CUED = {
    'CUED':   {'N': True,  'C': True,  'Z': False, 'CZ': False},
    'UNCUED': {'N': False, 'C': False, 'Z': True,  'CZ': True},
}
COLOR_FIELD_CUED = {
    'CUED':   {'N': True,  'C': False, 'Z': True,  'CZ': False},
    'UNCUED': {'N': False, 'C': True,  'Z': False, 'CZ': True},
}

# ── Stats ──────────────────────────────────────────────────────────────────────
def normal_cdf(x):
    return 0.5 * (1 + math.erf(x / math.sqrt(2)))

def wilson_ci(k, n, z=1.96):
    if n == 0:
        return 0.0, 0.0
    p = k / n
    denom = 1 + z**2 / n
    centre = (p + z**2 / (2 * n)) / denom
    hw = z * math.sqrt(p * (1 - p) / n + z**2 / (4 * n**2)) / denom
    return (centre - hw) * 100, (centre + hw) * 100   # return as %

def chi2_compare(k1, n1, k2, n2):
    table = [[k1, n1 - k1], [k2, n2 - k2]]
    chi2v, pval, _, _ = chi2_contingency(table, correction=False)
    return chi2v, pval

def stars(p):
    return ('***' if p < .001 else '**' if p < .01 else '*' if p < .05
            else '†' if p < .1 else 'n.s.')

# ── Data loading ───────────────────────────────────────────────────────────────
def is_correct(td, rd):
    d = (float(rd) - float(td) + 360) % 360
    return (360 - d if d > 180 else d) <= 22.5

def load_all():
    valid = []
    for path, invert in SESSIONS:
        with open(path, newline='') as f:
            rows = list(csv.DictReader(f, delimiter='\t'))
        for r in rows:
            if not r.get('TransDeg', '').strip() or not r.get('RespDeg', '').strip():
                continue
            if r.get('EndKey', '') in ('timeout', 'skip', 'requeue'):
                continue
            cond = r['Cond']
            if invert:
                cond = 'UNCUED' if cond == 'CUED' else 'CUED'
            swap = r['SwapType']
            if cond not in ('CUED', 'UNCUED') or swap not in ('N', 'C', 'Z', 'CZ'):
                continue
            valid.append({'correct': int(is_correct(r['TransDeg'], r['RespDeg'])),
                          'cond': cond, 'swap': swap})
    return valid

def aggregate(valid):
    acc = {k: [0, 0] for k in
           ('dot_cu', 'dot_un', 'dep_cu', 'dep_un', 'col_cu', 'col_un')}
    for r in valid:
        cond, swap, corr = r['cond'], r['swap'], r['correct']
        acc['dot_cu' if cond == 'CUED' else 'dot_un'][0] += corr
        acc['dot_cu' if cond == 'CUED' else 'dot_un'][1] += 1
        dk = 'dep_cu' if DEPTH_FIELD_CUED[cond][swap] else 'dep_un'
        acc[dk][0] += corr; acc[dk][1] += 1
        ck = 'col_cu' if COLOR_FIELD_CUED[cond][swap] else 'col_un'
        acc[ck][0] += corr; acc[ck][1] += 1
    return acc

# ── Plotting helpers ───────────────────────────────────────────────────────────
C_DOT_CU  = '#1565C0'   # blue
C_DOT_UN  = '#5B8FD6'   # lighter blue
C_DEP_CU  = '#1a6e8b'   # teal
C_DEP_UN  = '#7ab8cc'   # lighter teal
C_COL_CU  = '#8b5a1a'   # brown
C_COL_UN  = '#c49a5e'   # lighter brown

YLIM = (0, 72)


def pct(k, n):
    return k / n * 100 if n > 0 else 0.0


def draw_bar(ax, x, k, n, color, width=0.52, label=None, hatch=None):
    p = pct(k, n)
    lo, hi = wilson_ci(k, n)
    ax.bar(x, p, width, color=color, alpha=0.88, zorder=3,
           label=label, edgecolor='white', linewidth=0.5, hatch=hatch)
    ax.errorbar(x, p, yerr=[[p - lo], [hi - p]], fmt='none',
                color='#333', capsize=4, capthick=1.2, lw=1.2, zorder=4)
    # n and % inside bar
    if p > 12:
        ax.text(x, p / 2, f'{p:.0f}%\n(n={n})',
                ha='center', va='center', fontsize=7, color='white', fontweight='bold')
    else:
        ax.text(x, p + 1.5, f'{p:.0f}%\n(n={n})',
                ha='center', va='bottom', fontsize=7, color='#333')
    return p


def style_ax(ax, title=''):
    ax.axhline(CHANCE * 100, color='#AAAAAA', lw=1.0, ls='--', zorder=2)
    ax.text(1.01, CHANCE * 100, 'chance\n(12.5%)', transform=ax.get_yaxis_transform(),
            fontsize=6.5, color='#999', va='center')
    ax.set_ylim(*YLIM)
    ax.set_title(title, fontsize=9, fontweight='bold', pad=6)
    ax.set_ylabel('% correct', fontsize=8)
    ax.tick_params(labelsize=8)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.grid(axis='y', lw=0.4, alpha=0.35, zorder=0)


def sig_bracket(ax, x1, x2, p1, p2, pval):
    diff = p1 - p2
    y_top = max(p1, p2) + 7
    # horizontal bracket
    ax.plot([x1, x1, x2, x2],
            [y_top - 1.5, y_top, y_top, y_top - 1.5],
            color='#444', lw=0.9)
    s = stars(pval)
    ax.text((x1 + x2) / 2, y_top + 0.5,
            f'Δ = {diff:+.1f}pp  {s}',
            ha='center', va='bottom', fontsize=8.5, color='#222', fontweight='bold')


def two_bar_panel(ax, k1, n1, c1, lbl1, k2, n2, c2, lbl2, title, factor_lbl1, factor_lbl2):
    p1 = draw_bar(ax, 0, k1, n1, c1, label=lbl1)
    p2 = draw_bar(ax, 1, k2, n2, c2, label=lbl2)
    _, pval = chi2_compare(k1, n1, k2, n2)
    sig_bracket(ax, 0, 1, p1, p2, pval)
    ax.set_xticks([0, 1])
    ax.set_xticklabels([factor_lbl1, factor_lbl2], fontsize=9)
    style_ax(ax, title=title)


# ── Load data ──────────────────────────────────────────────────────────────────
print("Loading all 4 sessions …")
valid = load_all()
n_total = len(valid)
print(f"  n = {n_total} valid trials")

acc = aggregate(valid)

# Print summary table
print(f"\n{'Factor arm':<22} {'k':>5} {'n':>5}  {'%corr':>6}")
labels_map = [
    ('Dot-cued ✓',     'dot_cu'),
    ('Dot-uncued ✗',   'dot_un'),
    ('Depth-cued ✓',   'dep_cu'),
    ('Depth-uncued ✗', 'dep_un'),
    ('Color-cued ✓',   'col_cu'),
    ('Color-uncued ✗', 'col_un'),
]
for lbl, key in labels_map:
    k, n = acc[key]
    print(f"  {lbl:<20} {k:>5} {n:>5}  {pct(k,n):>6.1f}%")

print()
for name, k1, n1, k2, n2 in [
    ('Dot cueing Δ',   acc['dot_cu'][0], acc['dot_cu'][1],
                       acc['dot_un'][0], acc['dot_un'][1]),
    ('Depth-field Δ',  acc['dep_cu'][0], acc['dep_cu'][1],
                       acc['dep_un'][0], acc['dep_un'][1]),
    ('Color-field Δ',  acc['col_cu'][0], acc['col_cu'][1],
                       acc['col_un'][0], acc['col_un'][1]),
]:
    chi2v, pval = chi2_compare(k1, n1, k2, n2)
    diff = pct(k1, n1) - pct(k2, n2)
    print(f"  {name:<18} Δ={diff:+.1f}pp  χ²={chi2v:.2f}  p={pval:.4f}  {stars(pval)}")

# ── Build figure ───────────────────────────────────────────────────────────────
fig, axes = plt.subplots(2, 3, figsize=(13, 9.5))
fig.patch.set_facecolor('white')
fig.suptitle(
    f'DecoupledDots — Three cueing factors: raw performance (n={n_total}, all 4 sessions)\n'
    'Row 1: cued vs uncued arm for each factor  ·  Row 2: pairwise comparison of cued arms',
    fontsize=11, fontweight='bold', y=1.02)

# ── Row 0: Cued vs Uncued ─────────────────────────────────────────────────────
two_bar_panel(axes[0, 0],
    *acc['dot_cu'], C_DOT_CU, 'Dot-cued',
    *acc['dot_un'], C_DOT_UN, 'Dot-uncued',
    'A.  Dot cueing\n(temporal onset marks translator)',
    'Dot-cued ✓\n(CUED)', 'Dot-uncued ✗\n(UNCUED)')

two_bar_panel(axes[0, 1],
    *acc['dep_cu'], C_DEP_CU, 'Depth-cued',
    *acc['dep_un'], C_DEP_UN, 'Depth-uncued',
    'B.  Depth-field cueing\n(translator in same depth plane as delayed field)',
    'Depth-cued ✓\n{CUED+N/C, UNCUED+Z/CZ}', 'Depth-uncued ✗\n{CUED+Z/CZ, UNCUED+N/C}')

two_bar_panel(axes[0, 2],
    *acc['col_cu'], C_COL_CU, 'Color-cued',
    *acc['col_un'], C_COL_UN, 'Color-uncued',
    'C.  Color-field cueing\n(translator color matches delayed field)',
    'Color-cued ✓\n{CUED+N/Z, UNCUED+C/CZ}', 'Color-uncued ✗\n{CUED+C/CZ, UNCUED+N/Z}')

# ── Row 1: Pairwise comparisons of cued arms ──────────────────────────────────
two_bar_panel(axes[1, 0],
    *acc['dot_cu'], C_DOT_CU, 'Dot-cued',
    *acc['dep_cu'], C_DEP_CU, 'Depth-cued',
    'D.  Dot-cued  vs  Depth-cued\n(performance in the "favored" arm of each factor)',
    'Dot-cued ✓\n(CUED)', 'Depth-cued ✓\n(correct plane)')

two_bar_panel(axes[1, 1],
    *acc['dot_cu'], C_DOT_CU, 'Dot-cued',
    *acc['col_cu'], C_COL_CU, 'Color-cued',
    'E.  Dot-cued  vs  Color-cued',
    'Dot-cued ✓\n(CUED)', 'Color-cued ✓\n(matching color)')

two_bar_panel(axes[1, 2],
    *acc['dep_cu'], C_DEP_CU, 'Depth-cued',
    *acc['col_cu'], C_COL_CU, 'Color-cued',
    'F.  Depth-cued  vs  Color-cued',
    'Depth-cued ✓\n(correct plane)', 'Color-cued ✓\n(matching color)')

fig.text(
    0.5, 0.01,
    'Error bars: 95% Wilson CI  |  Dashed line = chance 12.5% (8-AFC)  |  '
    'Δ test: two-sided Pearson χ²  |  †p<.1  *p<.05  **p<.01  ***p<.001  |  '
    'All 4 sessions: 260406_1532, 260406_1754, 260407_0643, 260407_0731',
    ha='center', va='bottom', fontsize=6.5, color='#555')

plt.tight_layout(rect=[0, 0.025, 1, 1.0])

fig.text(0.01, 0.005, f'{os.path.basename(OUT_PDF)}  ·  {DATE_STR}',
         fontsize=5, color='#888888', ha='left', va='bottom')
fig.text(0.99, 0.005, 'p. 1/1', fontsize=5, color='#888888', ha='right', va='bottom')

os.makedirs(FIG_DIR, exist_ok=True)
os.makedirs(FIG_DIR_SP, exist_ok=True)
fig.savefig(OUT_PNG, dpi=150, bbox_inches='tight', facecolor='white')
fig.savefig(OUT_PDF, bbox_inches='tight', facecolor='white')
fig.savefig(OUT_PDF_SP, bbox_inches='tight', facecolor='white')
print(f"\nSaved PNG: {OUT_PNG}")
print(f"Saved PDF: {OUT_PDF}")
print(f"Saved PDF: {OUT_PDF_SP}")
