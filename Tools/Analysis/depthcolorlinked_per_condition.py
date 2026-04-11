#!/usr/bin/env python3
"""
depthcolorlinked_per_condition.py
----------------------------------
Per-condition % correct for Exp_DepthColorLinked_005m.

Analogous to decoupled_dots_per_condition.py — 2-page PDF, one page per swap
condition (ZdA / ZdB), each page a 2×2 grid of sub-plots.

Each sub-plot: 4 bars (CUED row_a, CUED row_b, UNCUED row_a, UNCUED row_b)
mirroring the trajectory figure layout.

Row convention (translator-centric, same as depthcolorlinked_allperms_traj.py):
  rot_cfg=1 → Field B=CW, Field A=CCW
  rot_cfg=0 → Field B=CCW, Field A=CW
  b_green: True → Field B=Green, Field A=Red
  b_near:  True → Field B=Near, Field A=Far

CUED  params = Field B's (delayed) properties when B translates.
UNCUED params = Field B's (delayed) properties when A translates,
                chosen so the TRANSLATOR (Field A) has the row label's identity.

ZdA: coherent subfields S0+S2 swap → translator changes depth+color.
ZdB: noise subfields S1+S3 swap   → translator is unchanged.

Sessions pooled:
  S1  260404_0940  DepthColorLinked_005m
  S2  260404_1123  DepthColorLinked_005m
  S3  260406_1001  DepthColorLinked_005m
  S4  260406_1034  DepthColorLinked_005m

Output: Agents/Figures/depthcolorlinked_per_condition.pdf
"""

import csv, collections, math, os, datetime
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.patches import Patch
from matplotlib.backends.backend_pdf import PdfPages

DATE_STR = datetime.date.today().strftime('%Y-%m-%d')

# ── Paths ──────────────────────────────────────────────────────────────────────
SESSIONS = [
    "/tmp/quest_pull2/files/vr_dots_session_260404_0940.tsv",
    "/tmp/quest_pull2/files/vr_dots_session_260404_1123.tsv",
    "/tmp/quest_pull2/files/vr_dots_session_260406_1001.tsv",
    "/tmp/quest_pull2/files/vr_dots_session_260406_1034.tsv",
]
BASE    = os.path.normpath(os.path.join(os.path.dirname(__file__), '../../Agents/SwapPilot/Figures'))
OUT_PDF = os.path.join(BASE, 'depthcolorlinked_per_condition.pdf')
CHANCE  = 1 / 8

# ── ROWS ──────────────────────────────────────────────────────────────────────
# Same 8-row permutation space as DecoupledDots.
# Label = translator identity (color / rotation / depth).
ROWS = [
    # ── CCW translates first (matches traj figure row order) ──────────────────
    dict(label='Green/CCW/Far',
         cued  =dict(rot_cfg=0, b_green=True,  b_near=False),
         uncued=dict(rot_cfg=1, b_green=False, b_near=True)),
    dict(label='Green/CCW/Near',
         cued  =dict(rot_cfg=0, b_green=True,  b_near=True),
         uncued=dict(rot_cfg=1, b_green=False, b_near=False)),
    dict(label='Red/CCW/Far',
         cued  =dict(rot_cfg=0, b_green=False, b_near=False),
         uncued=dict(rot_cfg=1, b_green=True,  b_near=True)),
    dict(label='Red/CCW/Near',
         cued  =dict(rot_cfg=0, b_green=False, b_near=True),
         uncued=dict(rot_cfg=1, b_green=True,  b_near=False)),
    # ── CW translates ─────────────────────────────────────────────────────────
    dict(label='Green/CW/Far',
         cued  =dict(rot_cfg=1, b_green=True,  b_near=False),
         uncued=dict(rot_cfg=0, b_green=False, b_near=True)),
    dict(label='Green/CW/Near',
         cued  =dict(rot_cfg=1, b_green=True,  b_near=True),
         uncued=dict(rot_cfg=0, b_green=False, b_near=False)),
    dict(label='Red/CW/Far',
         cued  =dict(rot_cfg=1, b_green=False, b_near=False),
         uncued=dict(rot_cfg=0, b_green=True,  b_near=True)),
    dict(label='Red/CW/Near',
         cued  =dict(rot_cfg=1, b_green=False, b_near=True),
         uncued=dict(rot_cfg=0, b_green=True,  b_near=False)),
]

SWAP_ORDER  = ['ZdA', 'ZdB']
SWAP_TITLES = {
    'ZdA': 'ZdA (ZdCoh) — coherent subfields S0+S2 swap depth+color',
    'ZdB': 'ZdB (ZdNoi) — noise subfields S1+S3 swap; coherent translator unchanged',
}

# Cueing labels per swap condition (CUED, UNCUED)
# In ZdA: coherent translator changes → Depth✗ for BOTH arms (S0 and S2 both swap)
# In ZdB: noise-only swap → coherent translator unchanged → Depth✓ for BOTH arms
CUEING_LABELS = {
    'ZdA': ('Dot✓  Depth✗  Color✗', 'Dot✗  Depth✗  Color✗'),
    'ZdB': ('Dot✓  Depth✓  Color✓', 'Dot✗  Depth✓  Color✓'),
}

# Page groupings: 4 sub-plots per page, each covering 2 rows
PAGES = [(0, 1), (2, 3), (4, 5), (6, 7)]
PAGE_LABELS = [
    'Green/CCW/Far  &  Green/CCW/Near',
    'Red/CCW/Far  &  Red/CCW/Near',
    'Green/CW/Far  &  Green/CW/Near',
    'Red/CW/Far  &  Red/CW/Near',
]

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
    for path in SESSIONS:
        with open(path, newline='') as f:
            for r in csv.DictReader(f, delimiter='\t'):
                if (not r.get('TransDeg', '').strip() or
                        not r.get('RespDeg', '').strip() or
                        r.get('EndKey', '') in ('timeout', 'skip', 'requeue')):
                    continue
                trials.append(dict(
                    swap    = r['SwapType'],
                    cond    = r['Cond'],
                    rot_cfg = int(r['RotCfg']),
                    b_green = (r['DelayedFieldColor'] == 'G'),
                    b_near  = (r['DelayedFieldDepth']  == 'N'),
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
BAR_W   = 0.55
COL_GAP = 0.55
ROW_GAP = 0.12

def draw_subplot(ax, swap, row_a_idx, row_b_idx, counts,
                 show_ylabel=False, page_title=''):
    row_a = ROWS[row_a_idx]
    row_b = ROWS[row_b_idx]

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

    ax.axhline(CHANCE * 100, color='#cc4444', lw=0.8, ls='--', zorder=1)

    cued_cx   = (x_ca + x_cb) / 2 + BAR_W / 2
    uncued_cx = (x_ua + x_ub) / 2 + BAR_W / 2
    cued_lbl, uncued_lbl = CUEING_LABELS[swap]
    ax.text(cued_cx,   103, cued_lbl,   ha='center', va='bottom',
            fontsize=6.5, fontweight='bold', color='#1a3a8b',
            bbox=dict(boxstyle='round,pad=0.3', facecolor='#f0f4ff',
                      edgecolor='#1a3a8b', lw=0.8))
    ax.text(uncued_cx, 103, uncued_lbl, ha='center', va='bottom',
            fontsize=6.5, fontweight='bold', color='#884400',
            bbox=dict(boxstyle='round,pad=0.3', facecolor='#fff4e8',
                      edgecolor='#884400', lw=0.8))

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
def build_page(swap, counts, figsize=(8.5, 11), page_num=None, total_pages=None, filename=''):
    fig = plt.figure(figsize=figsize)
    fig.suptitle(
        f'Unity Asset: Exp_DepthColorLinked_005m  ·  {SWAP_TITLES[swap]}  ·  '
        f'% correct per condition  ·  All 4 sessions pooled',
        fontsize=8, fontweight='bold', y=0.98)
    footer = filename + (f'  ·  {DATE_STR}' if filename else DATE_STR)
    fig.text(0.01, 0.005, footer, fontsize=5, color='#888888', ha='left', va='bottom')
    if page_num is not None and total_pages is not None:
        fig.text(0.99, 0.005, f'p. {page_num}/{total_pages}', fontsize=5,
                 color='#888888', ha='right', va='bottom')

    gs = gridspec.GridSpec(2, 2, hspace=0.55, wspace=0.30,
                           top=0.91, bottom=0.08, left=0.10, right=0.97)

    for gi, (ra, rb) in enumerate(PAGES):
        ax = fig.add_subplot(gs[gi // 2, gi % 2])
        draw_subplot(ax, swap, ra, rb, counts,
                     show_ylabel=(gi % 2 == 0),
                     page_title=PAGE_LABELS[gi])

    leg_handles = [
        Patch(facecolor='#555555', label='Dot✓ (CUED)'),
        Patch(facecolor='#aaaaaa', label='Dot✗ (UNCUED)'),
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

fname = os.path.basename(OUT_PDF)
with PdfPages(OUT_PDF) as pdf:
    for pi, swap in enumerate(SWAP_ORDER, 1):
        fig = build_page(swap, counts, page_num=pi,
                         total_pages=len(SWAP_ORDER), filename=fname)
        pdf.savefig(fig, bbox_inches='tight')
        plt.close(fig)
        print(f'  Saved page: {SWAP_TITLES[swap]}')

print(f'Saved: {OUT_PDF}')
