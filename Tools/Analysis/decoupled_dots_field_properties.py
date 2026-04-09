#!/usr/bin/env python3
"""
decoupled_dots_field_properties.py
------------------------------------
Two-page PDF:
  Page 1: % correct by TRANSLATING-FIELD properties
  Page 2: % correct by DELAYED-ONSET-FIELD properties

Each page: 3 panels (Color / Rotation / Depth), 2 bars per panel,
pooled across all swap types and both CUED/UNCUED arms.

Descriptor conventions (kept consistent with trajectory figures):
  Translating field:
    Color    — color of the translating dot field
    Rotation — pre-translation rotation direction of the translating field
               (during the translation window the dots translate, not rotate;
                the label reflects the field's rotational identity before/after)
    Depth    — depth plane of Field B at onset (b_near from params);
               note: in Z/CZ conditions depth swaps at tStart, so this is
               the ONSET depth, not necessarily the depth during translation

  Delayed-onset field (always Field B):
    Color    — color of Field B (the delayed-onset field)
    Rotation — rotation direction of Field B (pre-translation)
               NOTE: perfectly anti-correlated with translator rotation
               for UNCUED trials; identical for CUED trials
    Depth    — depth plane of Field B at onset

Translator derivation from raw params (rot_cfg, b_green, b_near describe Field B):
  CUED  → Field B translates: trans_green=b_green, trans_cw=(rot_cfg==1), trans_near=b_near
  UNCUED → Field A translates: trans_green=!b_green, trans_cw=(rot_cfg==0), trans_near=!b_near

Sessions pooled: S1–S4 (all 4 DecoupledDots sessions, inversion-corrected).
Output: Agents/Figures/decoupled_dots_field_properties.pdf
"""

import csv, math, os, collections
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
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
OUT_PDF = os.path.join(BASE, 'decoupled_dots_field_properties.pdf')
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
def compute_stats(trials):
    """
    Returns (trans_stats, delayed_stats).
    Each: dict of prop → {val: [hits, n]}  (pooled over CUED/UNCUED and all swaps)
    """
    def empty():
        return [0, 0]

    trans = {
        'Color':    {'Green': empty(), 'Red':  empty()},
        'Rotation': {'CW':    empty(), 'CCW':  empty()},
        'Depth':    {'Near':  empty(), 'Far':  empty()},
    }
    delayed = {
        'Color':    {'Green': empty(), 'Red':  empty()},
        'Rotation': {'CW':    empty(), 'CCW':  empty()},
        'Depth':    {'Near':  empty(), 'Far':  empty()},
    }

    for t in trials:
        cond    = t['cond']
        bg      = t['b_green']
        rc      = t['rot_cfg']
        bn      = t['b_near']
        correct = t['correct']

        # ── Translator ────────────────────────────────────────────────────────
        if cond == 'CUED':
            tr_green, tr_cw, tr_near = bg, (rc == 1), bn
        else:
            tr_green, tr_cw, tr_near = not bg, (rc == 0), not bn

        trans['Color'   ]['Green' if tr_green else 'Red' ][0] += correct
        trans['Color'   ]['Green' if tr_green else 'Red' ][1] += 1
        trans['Rotation']['CW'    if tr_cw    else 'CCW' ][0] += correct
        trans['Rotation']['CW'    if tr_cw    else 'CCW' ][1] += 1
        trans['Depth'   ]['Near'  if tr_near  else 'Far' ][0] += correct
        trans['Depth'   ]['Near'  if tr_near  else 'Far' ][1] += 1

        # ── Delayed field (always Field B) ────────────────────────────────────
        del_green, del_cw, del_near = bg, (rc == 1), bn

        delayed['Color'   ]['Green' if del_green else 'Red' ][0] += correct
        delayed['Color'   ]['Green' if del_green else 'Red' ][1] += 1
        delayed['Rotation']['CW'    if del_cw    else 'CCW' ][0] += correct
        delayed['Rotation']['CW'    if del_cw    else 'CCW' ][1] += 1
        delayed['Depth'   ]['Near'  if del_near  else 'Far' ][0] += correct
        delayed['Depth'   ]['Near'  if del_near  else 'Far' ][1] += 1

    return trans, delayed

# ── Panel spec ─────────────────────────────────────────────────────────────────
# (prop, [val_A, val_B], [color_A, color_B], description, rotation_note)
TRANS_PANELS = [
    ('Color',    ['Green', 'Red'],
     ['#228B22', '#CC3333'],
     'Color of the translating dot field',
     None),
    ('Rotation', ['CW', 'CCW'],
     ['#4477bb', '#ee7733'],
     'Pre-translation rotation direction of the translating field',
     '(during translation the dots translate, not rotate;\n'
     ' label reflects rotational identity before/after the window)'),
    ('Depth',    ['Near', 'Far'],
     ['#8844aa', '#44aa88'],
     'Depth plane of the translating field at onset\n'
     '(onset depth; in Z/CZ conditions depth swaps at tStart)',
     None),
]

DELAYED_PANELS = [
    ('Color',    ['Green', 'Red'],
     ['#228B22', '#CC3333'],
     'Color of the delayed-onset dot field (Field B)',
     None),
    ('Rotation', ['CW', 'CCW'],
     ['#4477bb', '#ee7733'],
     'Pre-translation rotation direction of the delayed-onset field (Field B)',
     '(perfectly correlated with translator rotation for CUED trials;\n'
     ' perfectly anti-correlated for UNCUED trials)'),
    ('Depth',    ['Near', 'Far'],
     ['#8844aa', '#44aa88'],
     'Depth plane of the delayed-onset field (Field B) at onset',
     None),
]

BAR_W = 0.55
GAP   = 0.35

# ── Stats ──────────────────────────────────────────────────────────────────────
def prop_ztest(hits1, n1, hits2, n2):
    """Two-proportion z-test, two-tailed. Returns (delta_pp, z, p)."""
    if n1 == 0 or n2 == 0:
        return 0.0, 0.0, 1.0
    p1, p2  = hits1 / n1, hits2 / n2
    p_pool  = (hits1 + hits2) / (n1 + n2)
    se      = math.sqrt(p_pool * (1 - p_pool) * (1/n1 + 1/n2))
    if se == 0:
        return 0.0, 0.0, 1.0
    z       = (p1 - p2) / se
    p_val   = math.erfc(abs(z) / math.sqrt(2))   # two-tailed
    return (p1 - p2) * 100, z, p_val

def sig_str(p):
    if p < 0.001: return '***'
    if p < 0.01:  return '**'
    if p < 0.05:  return '*'
    return 'n.s.'

# ── Panel drawing ──────────────────────────────────────────────────────────────
def draw_panel(ax, stats, prop, vals, colors, description, note, show_ylabel=False):
    val_a, val_b = vals
    col_a, col_b = colors

    x_a = 0.0
    x_b = x_a + BAR_W + GAP

    pcts, ehi_s, n_s = [], [], []
    for x, val, col in [(x_a, val_a, col_a), (x_b, val_b, col_b)]:
        hits, n = stats[prop][val]
        pct, elo, ehi = pct_ci(hits, n)
        pcts.append(pct); ehi_s.append(ehi); n_s.append(n)
        ax.bar(x, pct, width=BAR_W * 0.9, color=col,
               edgecolor='white', linewidth=0.5, zorder=2, alpha=0.85)
        ax.errorbar(x, pct, yerr=[[elo], [ehi]], fmt='none',
                    ecolor='#222222', elinewidth=1.0, capsize=3.5, zorder=3)
        ax.text(x, pct + ehi + 1.5, f'n={n}', ha='center', va='bottom',
                fontsize=5.5, color='#555555')
        ax.text(x, -7, val, ha='center', va='top', fontsize=8,
                fontweight='bold', color=col, clip_on=False)

    # ── Stats annotation ──────────────────────────────────────────────────────
    hits_a, n_a = stats[prop][val_a]
    hits_b, n_b = stats[prop][val_b]
    delta, z, p = prop_ztest(hits_a, n_a, hits_b, n_b)
    sign = '+' if delta >= 0 else ''
    stars = sig_str(p)
    p_str = f'p<0.001' if p < 0.001 else f'p={p:.3f}'
    stat_label = f'Δ = {sign}{delta:.1f} pp   z = {z:.2f}   {p_str}   {stars}'

    # Bracket spanning both bars
    top = max(pcts[0]+ehi_s[0], pcts[1]+ehi_s[1]) + 6
    ax.plot([x_a, x_a, x_b, x_b], [top, top+2, top+2, top],
            lw=0.9, color='#333333', clip_on=False)
    ax.text((x_a + x_b + BAR_W) / 2, top + 3, stat_label,
            ha='center', va='bottom', fontsize=6, color='#222222')

    ax.axhline(CHANCE * 100, color='#cc4444', lw=0.9, ls='--', zorder=1)

    ax.set_xlim(x_a - BAR_W * 0.7, x_b + BAR_W * 1.2)
    ax.set_ylim(0, 115)
    ax.set_yticks([0, 12.5, 25, 50, 75, 100])
    ax.set_yticklabels(['0', '12.5', '25', '50', '75', '100'], fontsize=6)
    ax.yaxis.grid(True, lw=0.4, color='#e0e0e0', zorder=0)
    ax.set_axisbelow(True)
    ax.set_xticks([])
    ax.spines[['top', 'right', 'bottom']].set_visible(False)
    if show_ylabel:
        ax.set_ylabel('% correct', fontsize=8)

    ax.set_title(prop, fontsize=11, fontweight='bold', pad=6)

    # ── Description below axes ────────────────────────────────────────────────
    desc_text = description
    if note:
        desc_text += '\n' + note
    ax.text(0.5, -0.22, desc_text,
            ha='center', va='top', fontsize=6, color='#444444',
            style='italic', transform=ax.transAxes, clip_on=False,
            wrap=False, multialignment='center')

# ── Page builder ───────────────────────────────────────────────────────────────
def build_page(stats, panel_specs, page_title, figsize=(11, 6.5)):
    fig, axes = plt.subplots(1, 3, figsize=figsize)
    fig.suptitle(
        f'Exp_DecoupledDots_005m  ·  {page_title}  ·  All 4 sessions pooled  ·  '
        f'Pooled across swap types and Dot-cueing condition',
        fontsize=9, fontweight='bold', y=0.99)

    for ax, (prop, vals, cols, desc, note) in zip(axes, panel_specs):
        draw_panel(ax, stats, prop, vals, cols, desc, note,
                   show_ylabel=(ax is axes[0]))

    fig.subplots_adjust(left=0.08, right=0.97, bottom=0.38, top=0.88, wspace=0.38)

    fig.legend(
        handles=[Patch(facecolor='none', edgecolor='#cc4444',
                       linestyle='--', linewidth=0.9, label='Chance (12.5%)')],
        loc='lower center', fontsize=7,
        bbox_to_anchor=(0.5, 0.01), framealpha=0.9)
    return fig

# ── Main ───────────────────────────────────────────────────────────────────────
os.makedirs(BASE, exist_ok=True)
trials = load_all()
print(f'Total valid trials: {len(trials)}')

trans_stats, delayed_stats = compute_stats(trials)

with PdfPages(OUT_PDF) as pdf:
    fig1 = build_page(trans_stats,   TRANS_PANELS,
                      'Translating-field properties')
    pdf.savefig(fig1, bbox_inches='tight')
    plt.close(fig1)
    print('  Saved page 1: Translating-field properties')

    fig2 = build_page(delayed_stats, DELAYED_PANELS,
                      'Delayed-onset-field properties')
    pdf.savefig(fig2, bbox_inches='tight')
    plt.close(fig2)
    print('  Saved page 2: Delayed-onset-field properties')

print(f'Saved: {OUT_PDF}')
