#!/usr/bin/env python3
"""
decoupled_dots_N_2x2.py
-----------------------
Test of 2×2 bar layout for the N (no-swap) condition.
Each stimulus page → 2×2 inner grid of bars:
  top-left  = CUED   row_a    top-right  = UNCUED row_a
  bot-left  = CUED   row_b    bot-right  = UNCUED row_b

Below each bar:
  ▶ translating-field descriptor (gray box)
  * delayed-onset-field descriptor (gold box)
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
OUT_PDF = os.path.join(BASE, 'decoupled_dots_per_condition_2x2.pdf')
CHANCE  = 1 / 8

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
CUEING_LABELS = {
    'N':  ('Dot✓  Depth✓  Color✓', 'Dot✗  Depth✗  Color✗'),
    'C':  ('Dot✓  Depth✓  Color✗', 'Dot✗  Depth✗  Color✓'),
    'Z':  ('Dot✓  Depth✗  Color✓', 'Dot✗  Depth✓  Color✗'),
    'CZ': ('Dot✓  Depth✗  Color✗', 'Dot✗  Depth✓  Color✓'),
}

PAGES = [(0, 1), (2, 3), (4, 5), (6, 7)]

PAGE_LABELS = [
    'Grn/CW/Far & Grn/CW/Near',
    'Red/CW/Far & Red/CW/Near',
    'Grn/CCW/Far & Grn/CCW/Near',
    'Red/CCW/Far & Red/CCW/Near',
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

# ── 2×2 sub-plot ──────────────────────────────────────────────────────────────
def draw_subplot_2x2(fig, outer_spec, swap, row_a_idx, row_b_idx, counts,
                     quad_title=''):
    """
    One stimulus page as a 2×2 inner grid of individual bars.
    Columns: CUED (left) / UNCUED (right)  — mirrors stimulus layout
    Rows:    row_a (top) / row_b (bottom)
    """
    row_a = ROWS[row_a_idx]
    row_b = ROWS[row_b_idx]
    cued_lbl, uncued_lbl = CUEING_LABELS[swap]

    inner = gridspec.GridSpecFromSubplotSpec(
        2, 2, subplot_spec=outer_spec,
        hspace=0.55, wspace=0.25,
    )

    cells = [
        (0, 0, 'CUED',   row_a, row_a['cued']),
        (0, 1, 'UNCUED', row_a, row_a['uncued']),
        (1, 0, 'CUED',   row_b, row_b['cued']),
        (1, 1, 'UNCUED', row_b, row_b['uncued']),
    ]

    for ri, ci, cond, row, params in cells:
        ax = fig.add_subplot(inner[ri, ci])
        pct, elo, ehi, n = lookup(counts, swap, cond, params)

        col = '#555555' if cond == 'CUED' else '#aaaaaa'
        ax.bar(0, pct, width=0.55, color=col,
               edgecolor='white', linewidth=0.4, zorder=2)
        ax.errorbar(0, pct, yerr=[[elo], [ehi]], fmt='none',
                    ecolor='#222222', elinewidth=0.8, capsize=2.5, zorder=3)
        ax.axhline(CHANCE * 100, color='#cc4444', lw=0.8, ls='--', zorder=1)

        # n= label above bar
        ax.text(0, pct + ehi + 2, f'n={n}', ha='center', va='bottom',
                fontsize=4.5, color='#666666')

        # ── Descriptors below bar ─────────────────────────────────────────────
        delayed = (f"{'Grn' if params['b_green'] else 'Red'}/"
                   f"{'CW' if params['rot_cfg']==1 else 'CCW'}/"
                   f"{'Near' if params['b_near'] else 'Far'}")
        translator = row['label']

        ax.text(0, -6, f'* {delayed}',
                ha='center', va='top', fontsize=4.5, color='#333333',
                clip_on=False,
                bbox=dict(boxstyle='round,pad=0.2', facecolor='#fffde7',
                          edgecolor='#997700', lw=0.5))
        ax.text(0, -15, f'▶ {translator}',
                ha='center', va='top', fontsize=4.5, color='#333333',
                clip_on=False,
                bbox=dict(boxstyle='round,pad=0.2', facecolor='#f8f8f8',
                          edgecolor='#888888', lw=0.5))

        # ── Axes styling ──────────────────────────────────────────────────────
        ax.set_xlim(-0.65, 0.65)
        ax.set_ylim(0, 110)
        ax.set_yticks([0, 12.5, 25, 50, 75, 100])
        if ci == 0:
            ax.set_yticklabels(['0', '', '25', '50', '75', '100'], fontsize=5)
        else:
            ax.set_yticklabels([])
        ax.yaxis.grid(True, lw=0.4, color='#dddddd', zorder=0)
        ax.set_axisbelow(True)
        ax.set_xticks([])
        ax.spines[['top', 'right', 'bottom']].set_visible(False)

        # ── Column cueing header (top row only) ───────────────────────────────
        if ri == 0:
            header = cued_lbl if cond == 'CUED' else uncued_lbl
            cc = '#1a3a8b' if cond == 'CUED' else '#884400'
            ax.set_title(header, fontsize=5.5, fontweight='bold',
                         color=cc, pad=4,
                         bbox=dict(boxstyle='round,pad=0.3',
                                   facecolor='#f0f4ff' if cond == 'CUED' else '#fff4e8',
                                   edgecolor=cc, lw=0.8))

        # ── Row label: y-axis label on left column ────────────────────────────
        if ci == 0:
            ax.set_ylabel(f'% correct\n{row["label"]}', fontsize=5, labelpad=4)


# ── Page builder ───────────────────────────────────────────────────────────────
def build_page_2x2(swap, counts, figsize=(8.5, 11)):
    fig = plt.figure(figsize=figsize)
    fig.suptitle(
        f'Unity Asset: Exp_DecoupledDots_005m  ·  {SWAP_TITLES[swap]}  ·  '
        f'% correct per condition  ·  All 4 sessions pooled',
        fontsize=8, fontweight='bold', y=0.98)

    outer = gridspec.GridSpec(2, 2, hspace=0.35, wspace=0.30,
                              top=0.93, bottom=0.09, left=0.13, right=0.97)

    for gi, (ra, rb) in enumerate(PAGES):
        # Quad title via text annotation above each outer cell
        spec = outer[gi // 2, gi % 2]
        draw_subplot_2x2(fig, spec, swap, ra, rb, counts,
                         quad_title=PAGE_LABELS[gi])

    # Legend
    leg_handles = [
        Patch(facecolor='#555555', label='Dot✓ (CUED)'),
        Patch(facecolor='#aaaaaa', label='Dot✗ (UNCUED)'),
        Patch(facecolor='none', edgecolor='#cc4444',
              linestyle='--', linewidth=0.8, label='Chance (12.5%)'),
        Patch(facecolor='#f8f8f8', edgecolor='#888888', lw=0.8,
              label='▶ = translating field'),
        Patch(facecolor='#fffde7', edgecolor='#997700', lw=0.8,
              label='* = delayed-field onset'),
    ]
    fig.legend(handles=leg_handles, loc='lower center', fontsize=6,
               ncol=5, bbox_to_anchor=(0.5, 0.01), framealpha=0.9)
    return fig


# ── Main ───────────────────────────────────────────────────────────────────────
os.makedirs(BASE, exist_ok=True)
trials = load_all()
counts = aggregate(trials)

with PdfPages(OUT_PDF) as pdf:
    for swap in SWAP_ORDER:
        fig = build_page_2x2(swap, counts)
        pdf.savefig(fig, bbox_inches='tight')
        plt.close(fig)
        print(f'  Saved page: {SWAP_TITLES[swap]}')
print(f'Saved: {OUT_PDF}')
