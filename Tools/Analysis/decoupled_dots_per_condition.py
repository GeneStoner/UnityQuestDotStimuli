#!/usr/bin/env python3
"""
decoupled_dots_per_condition.py
--------------------------------
Per-condition % correct for Exp_DecoupledDots_005m.

4-page PDF — one page per swap condition (N, C, Z, CZ).
Each page: 2×2 grid of 4 sub-plots, each matching one page of the stimulus PDF.
Each sub-plot: 4 bars whose spatial placement mirrors the 4 stimulus panels:
  Left 2 bars  = CUED column   (row_a top, row_b bottom → left-to-right)
  Right 2 bars = UNCUED column (row_a top, row_b bottom)
  Column headers "CUED" / "UNCUED" match stimulus figure.
Each bar = one unique condition (no averaging across cued/uncued).

Sessions pooled:
  S1  260406_1532  DecoupledDots_005m      (standard,  invert=False)
  S2  260406_1754  DecoupledDots_Inv_005m  (inverted,  invert=True)
  S3  260407_0643  DecoupledDots_Inv_005m  (inverted,  invert=True)
  S4  260407_0731  DecoupledDots_005m      (standard,  invert=False)

Output: Agents/Figures/decoupled_dots_per_condition.pdf
"""

import csv, collections, math, os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.patches import Patch
from matplotlib.backends.backend_pdf import PdfPages

# ── Paths ──────────────────────────────────────────────────────────────────────
SESSIONS = [
    ("/tmp/quest_pull2/files/vr_dots_session_260406_1532.tsv", False),
    ("/tmp/quest_pull2/files/vr_dots_session_260406_1754.tsv", True),
    ("/tmp/quest_pull3/files/vr_dots_session_260407_0643.tsv", True),
    ("/tmp/quest_pull3/files/vr_dots_session_260407_0731.tsv", False),
]
BASE    = os.path.normpath(os.path.join(os.path.dirname(__file__), '../../Agents/Figures'))
OUT_PDF = os.path.join(BASE, 'decoupled_dots_per_condition.pdf')
CHANCE  = 1 / 8

# ── ROWS — exactly as in stimulus figures ─────────────────────────────────────
# Each entry has label + cued params + uncued params (complementary permutation)
ROWS = [
    dict(label='Grn/CW/Far',
         cued  =dict(rot_cfg=1, b_green=True,  b_near=False),
         uncued=dict(rot_cfg=0, b_green=False, b_near=True)),
    dict(label='Grn/CW/Near',
         cued  =dict(rot_cfg=1, b_green=True,  b_near=True),
         uncued=dict(rot_cfg=0, b_green=False, b_near=False)),
    dict(label='Red/CW/Far',
         cued  =dict(rot_cfg=1, b_green=False, b_near=False),
         uncued=dict(rot_cfg=0, b_green=True,  b_near=True)),
    dict(label='Red/CW/Near',
         cued  =dict(rot_cfg=1, b_green=False, b_near=True),
         uncued=dict(rot_cfg=0, b_green=True,  b_near=False)),
    dict(label='Grn/CCW/Far',
         cued  =dict(rot_cfg=0, b_green=True,  b_near=False),
         uncued=dict(rot_cfg=1, b_green=False, b_near=True)),
    dict(label='Grn/CCW/Near',
         cued  =dict(rot_cfg=0, b_green=True,  b_near=True),
         uncued=dict(rot_cfg=1, b_green=False, b_near=False)),
    dict(label='Red/CCW/Far',
         cued  =dict(rot_cfg=0, b_green=False, b_near=False),
         uncued=dict(rot_cfg=1, b_green=True,  b_near=True)),
    dict(label='Red/CCW/Near',
         cued  =dict(rot_cfg=0, b_green=False, b_near=True),
         uncued=dict(rot_cfg=1, b_green=True,  b_near=False)),
]

SWAP_ORDER  = ['N', 'C', 'Z', 'CZ']
SWAP_TITLES = {
    'N':  'N — no swap',
    'C':  'C — color swap',
    'Z':  'Z — depth swap',
    'CZ': 'CZ — color + depth swap',
}

# Stimulus page groupings (indices into ROWS)
PAGES = [(0, 1), (2, 3), (4, 5), (6, 7)]

# ── Stats ──────────────────────────────────────────────────────────────────────
def wilson_ci(k, n, z=1.96):
    if n == 0:
        return 0.0, 0.0
    p = k / n
    d = 1 + z**2 / n
    c = (p + z**2 / (2*n)) / d
    hw = z * math.sqrt(p*(1-p)/n + z**2/(4*n**2)) / d
    return c - hw, c + hw

# ── Data loading ───────────────────────────────────────────────────────────────
def is_correct(td, rd):
    d = (float(rd) - float(td) + 360) % 360
    return (360 - d if d > 180 else d) <= 22.5

def load_all():
    trials = []
    for path, is_inv in SESSIONS:
        with open(path, newline='') as f:
            for r in csv.DictReader(f, delimiter='\t'):
                if (not r.get('TransDeg', '').strip() or
                        not r.get('RespDeg', '').strip() or
                        r.get('EndKey', '') in ('timeout', 'skip', 'requeue')):
                    continue
                cond = r['Cond']
                if is_inv:
                    cond = 'UNCUED' if cond == 'CUED' else 'CUED'
                # b_green / b_near: in Inv sessions, DelayedField* refers to Field A,
                # so Field B's properties are the complement
                b_green = (r['DelayedFieldColor'] == 'G') ^ is_inv
                b_near  = (r['DelayedFieldDepth']  == 'N') ^ is_inv
                trials.append(dict(
                    swap    = r['SwapType'],
                    cond    = cond,
                    rot_cfg = int(r['RotCfg']),
                    b_green = b_green,
                    b_near  = b_near,
                    correct = int(is_correct(r['TransDeg'], r['RespDeg'])),
                ))
    return trials

def aggregate(trials):
    counts = collections.defaultdict(lambda: [0, 0])
    for t in trials:
        key = (t['swap'], t['cond'], t['rot_cfg'], t['b_green'], t['b_near'])
        counts[key][0] += t['correct']
        counts[key][1] += 1
    return counts

def lookup(counts, swap, cond, row_dict):
    p = row_dict
    k, n = counts[(swap, cond, p['rot_cfg'], p['b_green'], p['b_near'])]
    pct = (k / n * 100) if n > 0 else 0.0
    lo, hi = wilson_ci(k, n)
    return pct, (pct - lo*100), (hi*100 - pct), n

# ── Sub-plot drawing ───────────────────────────────────────────────────────────
BAR_W    = 0.55
COL_GAP  = 0.55   # gap between CUED and UNCUED column groups
ROW_GAP  = 0.12   # gap between the two bars within a column group

def draw_subplot(ax, swap, row_a_idx, row_b_idx, counts,
                 show_ylabel=False, page_title=''):
    row_a = ROWS[row_a_idx]
    row_b = ROWS[row_b_idx]

    # x positions: CUED group left, UNCUED group right
    # within each group: row_a bar, then row_b bar
    x_ca = 0.0
    x_cb = x_ca + BAR_W + ROW_GAP
    x_ua = x_cb + BAR_W + COL_GAP
    x_ub = x_ua + BAR_W + ROW_GAP

    bars = [
        (x_ca, swap, 'CUED',   row_a['cued'],   row_a['label'], '#555555'),
        (x_cb, swap, 'CUED',   row_b['cued'],   row_b['label'], '#555555'),
        (x_ua, swap, 'UNCUED', row_a['uncued'],  row_a['label'], '#aaaaaa'),
        (x_ub, swap, 'UNCUED', row_b['uncued'],  row_b['label'], '#aaaaaa'),
    ]

    for x, sw, cond, params, label, col in bars:
        pct, elo, ehi, n = lookup(counts, sw, cond, params)
        ax.bar(x, pct, width=BAR_W * 0.88, color=col,
               edgecolor='white', linewidth=0.4, zorder=2)
        ax.errorbar(x, pct, yerr=[[elo], [ehi]], fmt='none',
                    ecolor='#222222', elinewidth=0.8, capsize=2.5, zorder=3)
        ax.text(x, -6, label, ha='center', va='top', fontsize=5.5,
                rotation=35, clip_on=False)
        ax.text(x, pct + ehi + 1.5, f'n={n}', ha='center', va='bottom',
                fontsize=4.5, color='#666666')

    # Chance line
    ax.axhline(CHANCE * 100, color='#cc4444', lw=0.8, ls='--', zorder=1)

    # CUED / UNCUED column headers
    cued_cx   = (x_ca + x_cb) / 2 + BAR_W / 2
    uncued_cx = (x_ua + x_ub) / 2 + BAR_W / 2
    ymax = ax.get_ylim()[1] if ax.get_ylim()[1] > 10 else 100
    ax.text(cued_cx,   103, 'CUED',   ha='center', va='bottom',
            fontsize=7, fontweight='bold')
    ax.text(uncued_cx, 103, 'UNCUED', ha='center', va='bottom',
            fontsize=7, fontweight='bold')

    # Dividing line between CUED and UNCUED groups
    div_x = (x_cb + BAR_W + x_ua) / 2
    ax.axvline(div_x, color='#cccccc', lw=0.7, ls='-', zorder=0)

    ax.set_xlim(x_ca - BAR_W * 0.7, x_ub + BAR_W * 1.2)
    ax.set_ylim(0, 110)
    ax.set_yticks([0, 12.5, 25, 50, 75, 100])
    ax.set_yticklabels(['0', '12.5', '25', '50', '75', '100'], fontsize=6)
    ax.yaxis.grid(True, lw=0.4, color='#dddddd', zorder=0)
    ax.set_axisbelow(True)
    ax.set_xticks([])
    ax.spines[['top', 'right', 'bottom']].set_visible(False)
    ax.set_title(page_title, fontsize=7, pad=3)
    if show_ylabel:
        ax.set_ylabel('% correct', fontsize=7)


# ── Page builder ───────────────────────────────────────────────────────────────
PAGE_LABELS = [
    'Grn/CW/Far & Grn/CW/Near',
    'Red/CW/Far & Red/CW/Near',
    'Grn/CCW/Far & Grn/CCW/Near',
    'Red/CCW/Far & Red/CCW/Near',
]

def build_page(swap, counts, figsize=(8.5, 11)):
    fig = plt.figure(figsize=figsize)
    fig.suptitle(
        f'Unity Asset: Exp_DecoupledDots_005m  ·  {SWAP_TITLES[swap]}  ·  '
        f'% correct per condition  ·  All 4 sessions pooled',
        fontsize=8.5, fontweight='bold', y=0.98)

    gs = gridspec.GridSpec(2, 2, hspace=0.55, wspace=0.30,
                           top=0.91, bottom=0.08, left=0.10, right=0.97)

    for gi, (ra, rb) in enumerate(PAGES):
        ax = fig.add_subplot(gs[gi // 2, gi % 2])
        draw_subplot(ax, swap, ra, rb, counts,
                     show_ylabel=(gi % 2 == 0),
                     page_title=PAGE_LABELS[gi])

    leg_handles = [
        Patch(facecolor='#555555', label='CUED'),
        Patch(facecolor='#aaaaaa', label='UNCUED'),
        Patch(facecolor='none', edgecolor='#cc4444',
              linestyle='--', linewidth=0.8, label='Chance (12.5%)'),
    ]
    fig.legend(handles=leg_handles, loc='lower center', fontsize=7,
               ncol=3, bbox_to_anchor=(0.5, 0.01), framealpha=0.9)
    return fig


# ── Main ───────────────────────────────────────────────────────────────────────
os.makedirs(BASE, exist_ok=True)
trials = load_all()
counts = aggregate(trials)
print(f'Total valid trials: {sum(v[1] for v in counts.values())}')

with PdfPages(OUT_PDF) as pdf:
    for swap in SWAP_ORDER:
        fig = build_page(swap, counts)
        pdf.savefig(fig, bbox_inches='tight')
        plt.close(fig)
        print(f'  Saved page: {SWAP_TITLES[swap]}')

print(f'Saved: {OUT_PDF}')
