#!/usr/bin/env python3
"""
decoupled_dots_translator_delayed.py
-------------------------------------
Two-page PDF:
  Page 1: % correct by TRANSLATOR field properties (color / rotation / depth)
  Page 2: % correct by DELAYED-ONSET field properties (color / rotation / depth)

Each page: 3 panels (one per property).
Each panel: 4 bars — property value A (CUED, UNCUED) and value B (CUED, UNCUED).

Translator = the field that TRANSLATES:
  CUED  trials → Field B translates
    trans_green = b_green,  trans_cw = (rot_cfg==1),  trans_near = b_near
  UNCUED trials → Field A translates
    trans_green = !b_green, trans_cw = (rot_cfg==0),  trans_near = !b_near

Delayed field = always Field B (delayed onset):
  del_green = b_green,  del_cw = (rot_cfg==1),  del_near = b_near
  (same regardless of CUED/UNCUED)

Sessions pooled: S1–S4 (all 4 sessions, inversion-corrected).
Output: Agents/Figures/decoupled_dots_translator_delayed.pdf
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
OUT_PDF = os.path.join(BASE, 'decoupled_dots_translator_delayed.pdf')
CHANCE  = 1 / 8

# ── Stats ──────────────────────────────────────────────────────────────────────
def wilson_ci(k, n, z=1.96):
    if n == 0:
        return 0.0, 0.0
    p = k / n
    d = 1 + z**2 / n
    c = (p + z**2 / (2*n)) / d
    hw = z * math.sqrt(p*(1-p)/n + z**2/(4*n**2)) / d
    return c - hw, c + hw

def pct_ci(hits, n):
    pct = hits / n * 100 if n > 0 else 0.0
    lo, hi = wilson_ci(hits, n)
    return pct, pct - lo*100, hi*100 - pct

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
                b_green = (r['DelayedFieldColor'] == 'G') ^ is_inv
                b_near  = (r['DelayedFieldDepth']  == 'N') ^ is_inv
                trials.append(dict(
                    cond    = cond,
                    rot_cfg = int(r['RotCfg']),
                    b_green = b_green,
                    b_near  = b_near,
                    correct = int(is_correct(r['TransDeg'], r['RespDeg'])),
                ))
    return trials

# ── Aggregation ────────────────────────────────────────────────────────────────
def make_empty():
    return {'CUED': [0, 0], 'UNCUED': [0, 0]}

def compute_stats(trials):
    """Returns (translator_stats, delayed_stats).
    Each is a dict: property → {value_A: {CUED:[hits,n], UNCUED:[hits,n]},
                                  value_B: ...}
    """
    trans = {
        'Color':    {'Green': make_empty(), 'Red':  make_empty()},
        'Rotation': {'CW':    make_empty(), 'CCW':  make_empty()},
        'Depth':    {'Near':  make_empty(), 'Far':  make_empty()},
    }
    delayed = {
        'Color':    {'Green': make_empty(), 'Red':  make_empty()},
        'Rotation': {'CW':    make_empty(), 'CCW':  make_empty()},
        'Depth':    {'Near':  make_empty(), 'Far':  make_empty()},
    }

    for t in trials:
        cond    = t['cond']
        bg      = t['b_green']
        rc      = t['rot_cfg']
        bn      = t['b_near']
        correct = t['correct']

        # ── Translator properties ─────────────────────────────────────────────
        if cond == 'CUED':
            tr_green = bg
            tr_cw    = (rc == 1)
            tr_near  = bn
        else:
            tr_green = not bg
            tr_cw    = (rc == 0)
            tr_near  = not bn

        trans['Color'   ]['Green' if tr_green else 'Red' ][cond][0] += correct
        trans['Color'   ]['Green' if tr_green else 'Red' ][cond][1] += 1
        trans['Rotation']['CW'    if tr_cw    else 'CCW' ][cond][0] += correct
        trans['Rotation']['CW'    if tr_cw    else 'CCW' ][cond][1] += 1
        trans['Depth'   ]['Near'  if tr_near  else 'Far' ][cond][0] += correct
        trans['Depth'   ]['Near'  if tr_near  else 'Far' ][cond][1] += 1

        # ── Delayed field properties (always Field B) ─────────────────────────
        del_green = bg
        del_cw    = (rc == 1)
        del_near  = bn

        delayed['Color'   ]['Green' if del_green else 'Red' ][cond][0] += correct
        delayed['Color'   ]['Green' if del_green else 'Red' ][cond][1] += 1
        delayed['Rotation']['CW'    if del_cw    else 'CCW' ][cond][0] += correct
        delayed['Rotation']['CW'    if del_cw    else 'CCW' ][cond][1] += 1
        delayed['Depth'   ]['Near'  if del_near  else 'Far' ][cond][0] += correct
        delayed['Depth'   ]['Near'  if del_near  else 'Far' ][cond][1] += 1

    return trans, delayed

# ── Panel drawing ──────────────────────────────────────────────────────────────
BAR_W   = 0.55
INTRA_G = 0.10   # gap within a property-value pair (CUED/UNCUED)
INTER_G = 0.55   # gap between the two property values

COL_CUED   = '#555555'
COL_UNCUED = '#aaaaaa'

PROP_ORDER = [
    ('Color',    ['Green', 'Red']),
    ('Rotation', ['CW', 'CCW']),
    ('Depth',    ['Near', 'Far']),
]

def draw_panel(ax, stats, prop, values, panel_title, show_ylabel=False):
    """Draw one panel: 4 bars (val_A/CUED, val_A/UNCUED, val_B/CUED, val_B/UNCUED)."""
    val_a, val_b = values

    x0 = 0.0
    x1 = x0 + BAR_W + INTRA_G
    x2 = x1 + BAR_W + INTER_G
    x3 = x2 + BAR_W + INTRA_G

    positions = [
        (x0, val_a, 'CUED',   COL_CUED),
        (x1, val_a, 'UNCUED', COL_UNCUED),
        (x2, val_b, 'CUED',   COL_CUED),
        (x3, val_b, 'UNCUED', COL_UNCUED),
    ]

    for x, val, cond, col in positions:
        hits, n = stats[prop][val][cond]
        pct, elo, ehi = pct_ci(hits, n)
        ax.bar(x, pct, width=BAR_W * 0.9, color=col,
               edgecolor='white', linewidth=0.4, zorder=2)
        ax.errorbar(x, pct, yerr=[[elo], [ehi]], fmt='none',
                    ecolor='#222222', elinewidth=0.9, capsize=3, zorder=3)
        ax.text(x, pct + ehi + 1.5, f'n={n}', ha='center', va='bottom',
                fontsize=5, color='#666666')

    # Property-value group labels
    mid_a = (x0 + x1) / 2 + BAR_W / 2
    mid_b = (x2 + x3) / 2 + BAR_W / 2
    ax.text(mid_a, -8, val_a, ha='center', va='top', fontsize=7,
            fontweight='bold', clip_on=False)
    ax.text(mid_b, -8, val_b, ha='center', va='top', fontsize=7,
            fontweight='bold', clip_on=False)

    # Divider between groups
    div_x = (x1 + BAR_W + x2) / 2
    ax.axvline(div_x, color='#cccccc', lw=0.7, zorder=0)

    ax.axhline(CHANCE * 100, color='#cc4444', lw=0.9, ls='--', zorder=1)
    ax.set_xlim(x0 - BAR_W * 0.6, x3 + BAR_W * 1.1)
    ax.set_ylim(0, 110)
    ax.set_yticks([0, 12.5, 25, 50, 75, 100])
    ax.set_yticklabels(['0', '12.5', '25', '50', '75', '100'], fontsize=6)
    ax.yaxis.grid(True, lw=0.4, color='#dddddd', zorder=0)
    ax.set_axisbelow(True)
    ax.set_xticks([])
    ax.spines[['top', 'right', 'bottom']].set_visible(False)
    ax.set_title(panel_title, fontsize=9, fontweight='bold', pad=6)
    if show_ylabel:
        ax.set_ylabel('% correct', fontsize=8)

# ── Page builder ───────────────────────────────────────────────────────────────
def build_page(stats, page_title, figsize=(8.5, 5)):
    fig, axes = plt.subplots(1, 3, figsize=figsize)
    fig.suptitle(
        f'Unity Asset: Exp_DecoupledDots_005m  ·  {page_title}  ·  All 4 sessions pooled',
        fontsize=9, fontweight='bold', y=1.01)

    for ax, (prop, values) in zip(axes, PROP_ORDER):
        draw_panel(ax, stats, prop, values,
                   panel_title=prop,
                   show_ylabel=(ax is axes[0]))

    fig.subplots_adjust(left=0.09, right=0.97, bottom=0.18, top=0.88, wspace=0.35)

    leg_handles = [
        Patch(facecolor=COL_CUED,   label='Dot✓ (CUED)'),
        Patch(facecolor=COL_UNCUED, label='Dot✗ (UNCUED)'),
        Patch(facecolor='none', edgecolor='#cc4444',
              linestyle='--', linewidth=0.9, label='Chance (12.5%)'),
    ]
    fig.legend(handles=leg_handles, loc='lower center', fontsize=7,
               ncol=3, bbox_to_anchor=(0.5, 0.01), framealpha=0.9)
    return fig

# ── Main ───────────────────────────────────────────────────────────────────────
os.makedirs(BASE, exist_ok=True)
trials = load_all()
print(f'Total valid trials: {len(trials)}')

trans_stats, delayed_stats = compute_stats(trials)

with PdfPages(OUT_PDF) as pdf:
    fig1 = build_page(trans_stats,   'Translating-field properties')
    pdf.savefig(fig1, bbox_inches='tight')
    plt.close(fig1)
    print('  Saved page 1: Translator properties')

    fig2 = build_page(delayed_stats, 'Delayed-onset-field properties')
    pdf.savefig(fig2, bbox_inches='tight')
    plt.close(fig2)
    print('  Saved page 2: Delayed-field properties')

print(f'Saved: {OUT_PDF}')
