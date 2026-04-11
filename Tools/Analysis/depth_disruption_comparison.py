#!/usr/bin/env python3
"""
depth_disruption_comparison.py
--------------------------------
Cross-experiment comparison of depth-swap disruption magnitude.

Three experiments, side-by-side:

  DepthSwapCtrl (N/ZdA/ZdB, same-color red/red, 50% depth swap)
    → pure 50% depth disruption, no color confound

  DepthColorLinked (ZdA/ZdB, Near=Red/Far=Green, 50% depth + color linked)
    → 50% depth + color together

  DecoupledDots (N/C/Z/CZ, decoupled, 100% depth swap)
    → 100% depth alone (Z), color alone (C), both (CZ)

Key comparison rows (all are CUED conditions where translator changes depth):
  DepthSwapCtrl  CUED+ZdA    50% depth, no color
  DepthColorLinked CUED+ZdCoh 50% depth + color
  DecoupledDots  CUED+C      0% depth, full color
  DecoupledDots  CUED+Z      100% depth, no color
  DecoupledDots  CUED+CZ     100% depth + color

Baseline references:
  DepthSwapCtrl  CUED+N      clean baseline (no swap)
  DepthColorLinked CUED+ZdNoi  best available (non-coherent depth swap)
  DecoupledDots  CUED+N      clean baseline

Output: Agents/Figures/depth_disruption_comparison.pdf
"""

import csv, datetime, math, os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.backends.backend_pdf import PdfPages

DATE_STR = datetime.date.today().strftime('%Y-%m-%d')

BASE       = os.path.normpath(os.path.join(os.path.dirname(__file__), '../../Agents/Figures'))
BASE_SP    = os.path.normpath(os.path.join(os.path.dirname(__file__), '../../Agents/SwapPilot/Figures'))
OUT_PDF    = os.path.join(BASE,    'depth_disruption_comparison.pdf')
OUT_PDF_SP = os.path.join(BASE_SP, 'depth_disruption_comparison.pdf')
DATA    = os.path.expanduser('~/Library/Application Support/ThatsRandom/VRDotsDataFiles')
PULL2   = '/tmp/quest_pull2/files'
PULL3   = '/tmp/quest_pull3/files'
CHANCE  = 1 / 8

# ── Session lists ──────────────────────────────────────────────────────────────
DEPTHSWAPCTRL_BINO = [
    f'{DATA}/vr_dots_session_260330_1853.tsv',
    f'{DATA}/vr_dots_session_260331_0621.tsv',
    f'{DATA}/vr_dots_session_260401_1313.tsv',
    f'{DATA}/vr_dots_session_260401_1349.tsv',
    f'{DATA}/vr_dots_session_260401_1541.tsv',
    f'{DATA}/vr_dots_session_260401_1705.tsv',
]

DEPTHCOLORLINKED = [
    f'{PULL2}/vr_dots_session_260404_0940.tsv',
    f'{PULL2}/vr_dots_session_260404_1123.tsv',
    f'{PULL2}/vr_dots_session_260406_1001.tsv',
    f'{PULL2}/vr_dots_session_260406_1034.tsv',
]

DECOUPLED = [
    (f'{PULL2}/vr_dots_session_260406_1532.tsv', False),
    (f'{PULL2}/vr_dots_session_260406_1754.tsv', True),
    (f'{PULL3}/vr_dots_session_260407_0643.tsv', True),
    (f'{PULL3}/vr_dots_session_260407_0731.tsv', False),
]

# ── Stats ──────────────────────────────────────────────────────────────────────
def is_correct(td, rd):
    d = (float(rd) - float(td) + 360) % 360
    return (360 - d if d > 180 else d) <= 22.5

def wilson_ci(k, n, z=1.96):
    if n == 0: return 0.0, 0.0
    p = k / n
    d = 1 + z**2 / n
    c = (p + z**2/(2*n)) / d
    hw = z * math.sqrt(p*(1-p)/n + z**2/(4*n**2)) / d
    return c - hw, c + hw

def pct_ci(k, n):
    if n == 0: return 0.0, 0.0, 0.0
    pct = k / n * 100
    lo, hi = wilson_ci(k, n)
    return pct, pct - lo*100, hi*100 - pct

def z_test_2prop(k1, n1, k2, n2):
    """Two-proportion z-test, two-tailed. Returns (delta_pp, z, p)."""
    if n1 == 0 or n2 == 0: return 0.0, 0.0, 1.0
    p1, p2 = k1/n1, k2/n2
    pp = (k1+k2)/(n1+n2)
    se = math.sqrt(max(pp*(1-pp)*(1/n1+1/n2), 1e-12))
    z = (p1-p2)/se
    p = math.erfc(abs(z)/math.sqrt(2))
    return (p1-p2)*100, z, p

def sig_str(p):
    if p < 0.001: return '***'
    if p < 0.01:  return '**'
    if p < 0.05:  return '*'
    if p < 0.1:   return '†'
    return 'n.s.'

def load_tsv(path):
    rows = []
    with open(path, newline='') as f:
        for r in csv.DictReader(f, delimiter='\t'):
            if (not r.get('TransDeg','').strip() or
                    not r.get('RespDeg','').strip() or
                    r.get('EndKey','') in ('timeout','skip','requeue')):
                continue
            rows.append(r)
    return rows

# ── Load DepthSwapCtrl ─────────────────────────────────────────────────────────
dsc_counts = {}   # (cond, swap) → [hits, n]
for path in DEPTHSWAPCTRL_BINO:
    for r in load_tsv(path):
        key = (r['Cond'], r['SwapType'])
        if key not in dsc_counts: dsc_counts[key] = [0, 0]
        dsc_counts[key][0] += is_correct(r['TransDeg'], r['RespDeg'])
        dsc_counts[key][1] += 1

print('=== DepthSwapCtrl (binocular, n={}) ==='.format(
    sum(v[1] for v in dsc_counts.values())))
for swap in ['N','ZdA','ZdB']:
    for cond in ['CUED','UNCUED']:
        k, n = dsc_counts.get((cond, swap), [0,0])
        print(f'  {cond:7} {swap:4}: {k/n*100:5.1f}%  (n={n})')

# ── Load DepthColorLinked ──────────────────────────────────────────────────────
# ZdCoh = conditions where coherent translator changes depth:
#   CUED+ZdA (translator=FieldB, ZdA swaps FieldB sub-fields' depth)
#   UNCUED+ZdB
# ZdNoi = non-coherent changes depth:
#   CUED+ZdB, UNCUED+ZdA
dcl_counts = {}
for path in DEPTHCOLORLINKED:
    if not os.path.exists(path): continue
    for r in load_tsv(path):
        key = (r['Cond'], r['SwapType'])
        if key not in dcl_counts: dcl_counts[key] = [0, 0]
        dcl_counts[key][0] += is_correct(r['TransDeg'], r['RespDeg'])
        dcl_counts[key][1] += 1

print('\n=== DepthColorLinked (n={}) ==='.format(
    sum(v[1] for v in dcl_counts.values())))
for swap in ['ZdA','ZdB']:
    for cond in ['CUED','UNCUED']:
        k, n = dcl_counts.get((cond, swap), [0,0])
        coh_label = 'ZdCoh' if (cond=='CUED' and swap=='ZdA') or (cond=='UNCUED' and swap=='ZdB') else 'ZdNoi'
        print(f'  {cond:7} {swap:4} ({coh_label}): {k/n*100:5.1f}%  (n={n})')

# ── Load DecoupledDots ─────────────────────────────────────────────────────────
dd_counts = {}
for path, is_inv in DECOUPLED:
    for r in load_tsv(path):
        cond = r['Cond']
        if is_inv:
            cond = 'UNCUED' if cond == 'CUED' else 'CUED'
        key = (cond, r['SwapType'])
        if key not in dd_counts: dd_counts[key] = [0, 0]
        dd_counts[key][0] += is_correct(r['TransDeg'], r['RespDeg'])
        dd_counts[key][1] += 1

print('\n=== DecoupledDots (n={}) ==='.format(
    sum(v[1] for v in dd_counts.values())))
for swap in ['N','C','Z','CZ']:
    for cond in ['CUED','UNCUED']:
        k, n = dd_counts.get((cond, swap), [0,0])
        print(f'  {cond:7} {swap:3}: {k/n*100:5.1f}%  (n={n})')

# ── Disruption table ───────────────────────────────────────────────────────────
# Each entry: (label, depth_pct, has_color, cued_k, cued_n, baseline_k, baseline_n, color)
print('\n=== DISRUPTION TABLE (CUED conditions) ===')
print(f'{"Condition":<42} {"CUED acc":>8} {"vs baseline":>12} {"sig":>5}')
print('-'*72)

rows_table = []

def disruption_row(label, depth_pct, has_color, k_test, n_test, k_base, n_base, col):
    pct_t = k_test/n_test*100 if n_test else 0
    pct_b = k_base/n_base*100 if n_base else 0
    delta, z, p = z_test_2prop(k_test, n_test, k_base, n_base)
    print(f'  {label:<40} {pct_t:5.1f}%    {delta:+.1f}pp  {sig_str(p):>5}  (n={n_test})')
    rows_table.append(dict(label=label, depth_pct=depth_pct, has_color=has_color,
                           pct=pct_t, delta=delta, p=p,
                           k=k_test, n=n_test, k_base=k_base, n_base=n_base, col=col))

# DepthSwapCtrl baselines and tests
k_dsc_base, n_dsc_base = dsc_counts.get(('CUED','N'),[0,0])
k_dsc_zda,  n_dsc_zda  = dsc_counts.get(('CUED','ZdA'),[0,0])
k_dsc_zdb,  n_dsc_zdb  = dsc_counts.get(('CUED','ZdB'),[0,0])
k_dsc_u_base, n_dsc_u_base = dsc_counts.get(('UNCUED','N'),[0,0])
k_dsc_u_zda,  n_dsc_u_zda  = dsc_counts.get(('UNCUED','ZdA'),[0,0])

print('\nDepthSwapCtrl (50% depth, no color):')
disruption_row('DepthSwapCtrl CUED+N  (baseline)',     0, False, k_dsc_base, n_dsc_base, k_dsc_base, n_dsc_base, '#888888')
disruption_row('DepthSwapCtrl CUED+ZdA (50% depth)',  50, False, k_dsc_zda,  n_dsc_zda,  k_dsc_base, n_dsc_base, '#4477bb')
disruption_row('DepthSwapCtrl CUED+ZdB (50% non-coh)',50, False, k_dsc_zdb,  n_dsc_zdb,  k_dsc_base, n_dsc_base, '#88bbdd')

# DepthColorLinked
k_dcl_zdnoi_c, n_dcl_zdnoi_c = dcl_counts.get(('CUED','ZdB'),[0,0])  # ZdNoi for CUED = ZdB
k_dcl_zdcoh_c, n_dcl_zdcoh_c = dcl_counts.get(('CUED','ZdA'),[0,0])  # ZdCoh for CUED = ZdA

print('\nDepthColorLinked (50% depth + color linked):')
disruption_row('DepthColorLinked CUED+ZdNoi (baseline)',0, True,  k_dcl_zdnoi_c, n_dcl_zdnoi_c, k_dcl_zdnoi_c, n_dcl_zdnoi_c, '#888888')
disruption_row('DepthColorLinked CUED+ZdCoh (50%d+col)', 50, True, k_dcl_zdcoh_c, n_dcl_zdcoh_c, k_dcl_zdnoi_c, n_dcl_zdnoi_c, '#cc7700')

# DecoupledDots
k_dd_n,  n_dd_n  = dd_counts.get(('CUED','N'),[0,0])
k_dd_c,  n_dd_c  = dd_counts.get(('CUED','C'),[0,0])
k_dd_z,  n_dd_z  = dd_counts.get(('CUED','Z'),[0,0])
k_dd_cz, n_dd_cz = dd_counts.get(('CUED','CZ'),[0,0])

print('\nDecoupledDots (100% swaps, decoupled):')
disruption_row('DecoupledDots  CUED+N  (baseline)',     0, False, k_dd_n,  n_dd_n,  k_dd_n, n_dd_n, '#888888')
disruption_row('DecoupledDots  CUED+C  (100% color)',   0, True,  k_dd_c,  n_dd_c,  k_dd_n, n_dd_n, '#ee9922')
disruption_row('DecoupledDots  CUED+Z  (100% depth)',  100, False, k_dd_z,  n_dd_z,  k_dd_n, n_dd_n, '#c0392b')
disruption_row('DecoupledDots  CUED+CZ (100% d+col)', 100, True,  k_dd_cz, n_dd_cz, k_dd_n, n_dd_n, '#8e1a0e')

# ── Cueing effect (CUED − UNCUED) ─────────────────────────────────────────────
print('\n=== CUEING EFFECT (CUED − UNCUED) ===')

def cueing_row(exp, swap, cued_k, cued_n, unc_k, unc_n):
    delta, z, p = z_test_2prop(cued_k, cued_n, unc_k, unc_n)
    print(f'  {exp:<22} {swap:<8}: {delta:+.1f}pp  {sig_str(p)}  (CUED={cued_k/cued_n*100:.1f}%  UNCUED={unc_k/unc_n*100:.1f}%)  n={cued_n}')

print('DepthSwapCtrl:')
for swap in ['N','ZdA','ZdB']:
    ck, cn = dsc_counts.get(('CUED',swap),[0,0])
    uk, un = dsc_counts.get(('UNCUED',swap),[0,0])
    cueing_row('DepthSwapCtrl',swap,ck,cn,uk,un)

print('DepthColorLinked (n includes 4 sessions):')
for swap, label in [('ZdA','ZdCoh'),('ZdB','ZdNoi')]:
    ck, cn = dcl_counts.get(('CUED',swap),[0,0])
    uk, un = dcl_counts.get(('UNCUED',swap),[0,0])
    cueing_row('DepthColorLinked',f'{swap}({label})',ck,cn,uk,un)

print('DecoupledDots:')
for swap in ['N','C','Z','CZ']:
    ck, cn = dd_counts.get(('CUED',swap),[0,0])
    uk, un = dd_counts.get(('UNCUED',swap),[0,0])
    cueing_row('DecoupledDots',swap,ck,cn,uk,un)

# ── Figure ─────────────────────────────────────────────────────────────────────
os.makedirs(BASE, exist_ok=True)
os.makedirs(BASE_SP, exist_ok=True)

BAR_SPECS = [
    # (x_pos, label, cued_k, cued_n, color, hatch)
    # Group 1: DepthSwapCtrl
    (0.0,  'DSC\nN',     *dsc_counts.get(('CUED','N'),  [0,0]), '#aaaaaa', None),
    (0.9,  'DSC\nZdA',   *dsc_counts.get(('CUED','ZdA'),[0,0]), '#4477bb', None),
    (1.8,  'DSC\nZdB',   *dsc_counts.get(('CUED','ZdB'),[0,0]), '#88bbdd', None),
    # Group 2: DepthColorLinked
    (3.2,  'DCL\nZdNoi', *dcl_counts.get(('CUED','ZdB'),[0,0]), '#aaaaaa', '//'),
    (4.1,  'DCL\nZdCoh', *dcl_counts.get(('CUED','ZdA'),[0,0]), '#cc7700', '//'),
    # Group 3: DecoupledDots
    (5.5,  'DD\nN',      *dd_counts.get(('CUED','N'), [0,0]), '#aaaaaa', None),
    (6.4,  'DD\nC',      *dd_counts.get(('CUED','C'), [0,0]), '#ee9922', None),
    (7.3,  'DD\nZ',      *dd_counts.get(('CUED','Z'), [0,0]), '#c0392b', None),
    (8.2,  'DD\nCZ',     *dd_counts.get(('CUED','CZ'),[0,0]), '#8e1a0e', None),
]

UNCUED_SPECS = [
    *[dsc_counts.get(('UNCUED', s), [0,0]) for s in ['N','ZdA','ZdB']],
    dcl_counts.get(('UNCUED','ZdB'),[0,0]),  # ZdNoi for UNCUED
    dcl_counts.get(('UNCUED','ZdA'),[0,0]),  # ZdCoh for UNCUED
    *[dd_counts.get(('UNCUED', s), [0,0]) for s in ['N','C','Z','CZ']],
]

GROUP_SEPS  = [2.6, 4.8]
GROUP_LABELS = [
    (0.9,  'DepthSwapCtrl\nExp_DepthSwapCtrl_005m\n(50% depth swap, same-color red/red)'),
    (3.65, 'DepthColorLinked\nExp_DepthColorLinked_005m\n(50% depth + color linked; Near=Red Far=Green)'),
    (6.85, 'DecoupledDots\nExp_DecoupledDots_005m (+Inv)\n(100% swaps; depth & color decoupled)'),
]

KEY = (
    'Abbreviations — Experiments:  '
    'DSC = DepthSwapCtrl  ·  DCL = DepthColorLinked  ·  DD = DecoupledDots\n'
    'Conditions:  '
    'N = no swap (baseline)  ·  '
    'C = 100% color swap only  ·  '
    'Z = 100% depth swap only  ·  '
    'CZ = 100% depth + color  ·  '
    'ZdA / ZdCoh = coherent subfields swap → translator changes depth plane  ·  '
    'ZdB / ZdNoi = noise subfields swap → coherent translator unchanged'
)

LEGEND_HANDLES = [
    mpatches.Patch(facecolor='#aaaaaa', label='Baseline (N / ZdNoi)'),
    mpatches.Patch(facecolor='#4477bb', label='DSC ZdA: 50% depth, no color'),
    mpatches.Patch(facecolor='#cc7700', hatch='//', label='DCL ZdCoh: 50% depth + color'),
    mpatches.Patch(facecolor='#ee9922', label='DD C: 100% color only'),
    mpatches.Patch(facecolor='#c0392b', label='DD Z: 100% depth, no color'),
    mpatches.Patch(facecolor='#8e1a0e', label='DD CZ: 100% depth + color'),
    mpatches.Patch(facecolor='#555555', alpha=0.88, label='CUED (solid)'),
    mpatches.Patch(facecolor='#555555', alpha=0.30, label='UNCUED (faded)'),
    mpatches.Patch(facecolor='none', edgecolor='#cc4444', linestyle='--', linewidth=0.9,
                   label='Chance / zero line'),
]

BAR_W   = 0.32
PAIR_OFF = 0.20  # CUED left, UNCUED right of centre x

fname = os.path.basename(OUT_PDF)

# ── Page 1: CUED + UNCUED accuracy ────────────────────────────────────────────
fig1, ax1 = plt.subplots(1, 1, figsize=(12, 7))
fig1.suptitle(
    'Cross-experiment depth-swap disruption  ·  Dot-cued (solid) vs Uncued (faded) accuracy',
    fontsize=11, fontweight='bold', y=0.98)

for i, spec in enumerate(BAR_SPECS):
    x, lbl, ck, cn, col, hatch = spec
    uk, un = UNCUED_SPECS[i]

    vc, eloc, ehic = pct_ci(ck, cn)
    vu, elou, ehiu = pct_ci(uk, un)

    ax1.bar(x - PAIR_OFF, vc, width=BAR_W, color=col, hatch=hatch,
            edgecolor='white' if not hatch else '#555555',
            linewidth=0.5, zorder=2, alpha=0.88)
    ax1.errorbar(x - PAIR_OFF, vc, yerr=[[eloc],[ehic]], fmt='none',
                 ecolor='#333333', elinewidth=1, capsize=2.5, zorder=3)
    ax1.text(x - PAIR_OFF, 1.5, 'C', ha='center', va='bottom',
             fontsize=5, color='#222222', fontweight='bold')

    ax1.bar(x + PAIR_OFF, vu, width=BAR_W, color=col, hatch=hatch,
            edgecolor='white' if not hatch else '#555555',
            linewidth=0.5, zorder=2, alpha=0.30)
    ax1.errorbar(x + PAIR_OFF, vu, yerr=[[elou],[ehiu]], fmt='none',
                 ecolor='#888888', elinewidth=0.8, capsize=2, zorder=3)
    ax1.text(x + PAIR_OFF, 1.5, 'U', ha='center', va='bottom',
             fontsize=5, color='#777777')

    ax1.text(x, -4, lbl, ha='center', va='top', fontsize=6.5, clip_on=False)

for sx in GROUP_SEPS:
    ax1.axvline(sx, color='#cccccc', lw=0.8, ls='--', zorder=0)
ax1.axhline(CHANCE*100, color='#cc4444', lw=0.9, ls='--', zorder=1)

ax1.set_xlim(-0.6, 8.8)
ax1.set_ylim(0, 100)
ax1.set_yticks([0, 12.5, 25, 50, 75])
ax1.set_yticklabels(['0','12.5','25','50','75'], fontsize=8)
ax1.set_ylabel('% correct', fontsize=10)
ax1.set_xticks([])
ax1.spines[['top','right','bottom']].set_visible(False)
ax1.yaxis.grid(True, lw=0.4, color='#e0e0e0', zorder=0)
ax1.set_axisbelow(True)

y_glbl = ax1.get_ylim()[1] * 0.97
for gx, glbl in GROUP_LABELS:
    ax1.text(gx, y_glbl, glbl, ha='center', va='top', fontsize=7,
             color='#333333', style='italic', clip_on=True)

fig1.legend(handles=LEGEND_HANDLES, loc='lower center', fontsize=7, ncol=5,
            bbox_to_anchor=(0.5, -0.01), framealpha=0.9)
fig1.subplots_adjust(left=0.07, right=0.97, bottom=0.22, top=0.93)
fig1.text(0.5, 0.13, KEY, ha='center', va='top', fontsize=5.8, color='#333333',
          bbox=dict(boxstyle='round,pad=0.4', facecolor='#f8f8f8',
                    edgecolor='#cccccc', lw=0.7))
fig1.text(0.01, 0.005, f'{fname}  ·  {DATE_STR}', fontsize=5,
          color='#888888', ha='left', va='bottom')
fig1.text(0.99, 0.005, 'p. 1/3', fontsize=5, color='#888888', ha='right', va='bottom')

# ── Page 2: Dot cueing effect ─────────────────────────────────────────────────
fig2, ax2 = plt.subplots(1, 1, figsize=(12, 7))
fig2.suptitle(
    'Cross-experiment depth-swap disruption  ·  Dot cueing effect (Dot-cued − Uncued, pp)',
    fontsize=11, fontweight='bold', y=0.98)

for i, spec in enumerate(BAR_SPECS):
    x, lbl, ck, cn, col, hatch = spec
    uk, un = UNCUED_SPECS[i]

    delta, z, p = z_test_2prop(ck, cn, uk, un)
    elo = ehi = 1.96 * math.sqrt(max(ck*(cn-ck)/cn**3 + uk*(un-uk)/un**3, 1e-9)) * 100
    bar_color = '#1a6ab5' if delta >= 0 else '#c0392b'

    ax2.bar(x, delta, width=BAR_W*2+0.05, color=bar_color, hatch=hatch,
            edgecolor='white' if not hatch else '#555555',
            linewidth=0.5, zorder=2, alpha=0.88)
    ax2.errorbar(x, delta, yerr=[[elo],[ehi]], fmt='none',
                 ecolor='#333333', elinewidth=1, capsize=3, zorder=3)
    ax2.text(x, -3, lbl, ha='center', va='top', fontsize=6.5, clip_on=False)

for sx in GROUP_SEPS:
    ax2.axvline(sx, color='#cccccc', lw=0.8, ls='--', zorder=0)
ax2.axhline(0, color='#cc4444', lw=0.9, ls='--', zorder=1)

ax2.set_xlim(-0.6, 8.8)
ax2.set_ylim(-10, 55)
ax2.set_yticks([0, 10, 20, 30, 40, 50])
ax2.set_yticklabels(['0','10','20','30','40','50'], fontsize=8)
ax2.set_ylabel('Dot cueing effect  Dot-cued − Uncued (pp)', fontsize=10)
ax2.set_xticks([])
ax2.spines[['top','right','bottom']].set_visible(False)
ax2.yaxis.grid(True, lw=0.4, color='#e0e0e0', zorder=0)
ax2.set_axisbelow(True)

y_glbl2 = ax2.get_ylim()[1] * 0.97
for gx, glbl in GROUP_LABELS:
    ax2.text(gx, y_glbl2, glbl, ha='center', va='top', fontsize=7,
             color='#333333', style='italic', clip_on=True)

fig2.legend(handles=LEGEND_HANDLES[:6] + LEGEND_HANDLES[-1:],
            loc='lower center', fontsize=7, ncol=4,
            bbox_to_anchor=(0.5, -0.01), framealpha=0.9)
fig2.subplots_adjust(left=0.07, right=0.97, bottom=0.22, top=0.93)
fig2.text(0.5, 0.13, KEY, ha='center', va='top', fontsize=5.8, color='#333333',
          bbox=dict(boxstyle='round,pad=0.4', facecolor='#f8f8f8',
                    edgecolor='#cccccc', lw=0.7))
fig2.text(0.01, 0.005, f'{fname}  ·  {DATE_STR}', fontsize=5,
          color='#888888', ha='left', va='bottom')
fig2.text(0.99, 0.005, 'p. 2/3', fontsize=5, color='#888888', ha='right', va='bottom')

# ── Page 3: Text summary ───────────────────────────────────────────────────────
fig3 = plt.figure(figsize=(8.5, 11))

SUMMARY_TITLE = 'What disrupts dot cueing? — Summary of findings across three experiments'

SUMMARY_BODY = """\
Dot cueing refers to the advantage conferred by an onset dot cue that briefly marks one of two
overlapping transparent motion fields. On a given trial the "dot-cued" field later translates;
the observer reports its direction. Dot cueing = (dot-cued accuracy) − (uncued accuracy).

─────────────────────────────────────────────────────────────────────────────
WHAT REDUCES DOT CUEING
─────────────────────────────────────────────────────────────────────────────

1.  Coherent-object depth-plane change at translation onset  [CRITICAL FACTOR]
    When the translating (dot-cued) field changes depth plane at the moment it starts to
    move, dot cueing drops substantially:
      • DSC ZdA  (50% depth, same-color):           cueing ≈ +12 pp  n.s.  (vs baseline +34 pp **)
      • DCL ZdCoh (50% depth + color, linked):       cueing ≈  +7 pp  †
      • DD  Z    (100% depth swap, color fixed):     cueing ≈  +9 pp  **   (vs baseline +28 pp ***)
    The translator losing its depth identity — even in just 50% of dot-cloud subfields —
    is sufficient to nearly abolish the cueing benefit.

2.  Combined depth + color change (coherent) does not add further disruption beyond depth alone.
    DD CZ ≈ DD Z in cueing magnitude, and DCL ZdCoh ≈ DSC ZdA.
    Color change alone (DD C) has no effect (see below).

─────────────────────────────────────────────────────────────────────────────
WHAT DOES NOT REDUCE DOT CUEING
─────────────────────────────────────────────────────────────────────────────

3.  Color swap alone (100%):  DD C cueing ≈ +22 pp ***  — indistinguishable from no-swap baseline.
    Color identity of the translating field is irrelevant to dot cueing.

4.  Noise-only depth swap (non-coherent subfields change depth):
      • DSC ZdB:   cueing ≈ +56 pp ***  (enhanced relative to baseline)
      • DCL ZdNoi: cueing ≈ +26 pp ***
    When the coherent translator is unchanged and only non-coherent subfields swap depth,
    dot cueing is maintained or enhanced — the cue remains predictive.

─────────────────────────────────────────────────────────────────────────────
KEY INFERENCE: DOSE DOES NOT EXPLAIN THE EFFECT
─────────────────────────────────────────────────────────────────────────────

5.  50% coherent swap (DCL ZdCoh) ≈ 100% depth swap (DD Z) in disruption magnitude.
    If disruption were proportional to the quantity of depth change in the scene, the
    100% swap should be twice as disruptive as the 50% swap. It is not.
    The effect tracks whether the coherent object changes depth identity, not the total
    amount of depth change in the stimulus.

─────────────────────────────────────────────────────────────────────────────
TERMINOLOGY NOTE
─────────────────────────────────────────────────────────────────────────────

  Dot cueing       — advantage from the onset dot marking the translating field (F1)
  Depth-field cueing — advantage from the translating field occupying its pre-cue depth plane (F2)
  Color-field cueing — advantage from the translating field retaining its pre-cue color (F3; null)
  These three factors were dissociated in Exp_DecoupledDots_005m (GLM2: F1×F2 interaction
  dominates; F3 AME = +0.9 pp, p = .64).
"""

fig3.text(0.5, 0.96, SUMMARY_TITLE, ha='center', va='top',
          fontsize=12, fontweight='bold', color='#111111')
fig3.text(0.07, 0.90, SUMMARY_BODY, ha='left', va='top',
          fontsize=8, color='#222222', family='monospace',
          linespacing=1.55)
fig3.text(0.01, 0.005, f'{fname}  ·  {DATE_STR}', fontsize=5,
          color='#888888', ha='left', va='bottom')
fig3.text(0.99, 0.005, 'p. 3/3', fontsize=5, color='#888888', ha='right', va='bottom')
fig3.patch.set_facecolor('white')

# ── Save ───────────────────────────────────────────────────────────────────────
for out in [OUT_PDF, OUT_PDF_SP]:
    with PdfPages(out) as pdf:
        pdf.savefig(fig1, bbox_inches='tight')
        pdf.savefig(fig2, bbox_inches='tight')
        pdf.savefig(fig3, bbox_inches='tight')
plt.close(fig1)
plt.close(fig2)
plt.close(fig3)
print(f'\nSaved: {OUT_PDF}')
print(f'Saved: {OUT_PDF_SP}')
