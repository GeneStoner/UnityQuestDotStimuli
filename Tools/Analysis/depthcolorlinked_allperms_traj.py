#!/usr/bin/env python3
"""
depthcolorlinked_allperms_traj.py
----------------------------------
Full-permutation trajectory figures for Exp_DepthColorLinked_005m.

Same 4-symbol scatter style as depth_color_linked_traj.py (filled/open ×
circle/triangle), extended to all 8 row permutations × CUED/UNCUED.
Two separate PDFs — one per swap condition (ZdA / ZdB).

Outputs:
  Agents/Figures/depthcolorlinked_ZdA_allperms.pdf  (4 pages, 2 rows/page)
  Agents/Figures/depthcolorlinked_ZdB_allperms.pdf
  Agents/Figures/depthcolorlinked_ZdA_condensed.pdf (single-page 4-quadrant)
  Agents/Figures/depthcolorlinked_ZdB_condensed.pdf
  Agents/Figures/depthcolorlinked_ZdA_allperms.png
  Agents/Figures/depthcolorlinked_ZdB_allperms.png

DCL mechanics (linkDepthColor=1):
  ZdA — coherent subfields S0+S2 exchange BOTH color+depth at tStart
  ZdB — noise subfields S1+S3 exchange BOTH color+depth at tStart

Subfield symbols (same as depth_color_linked_traj.py):
  S0 ● Field A · coherent  (filled circle)
  S1 ○ Field A · noise     (open circle)
  S2 ▲ Field B · coherent  (filled triangle)    ← always absent pre-onset
  S3 △ Field B · noise     (open triangle)      ← always absent pre-onset

Color = current color assignment of that subfield (follows its depth in DCL).
  Red  = original color-label of one plane
  Green = original color-label of the other plane
  b_green / b_near are INDEPENDENT in the DCL data (all 4 combinations appear).

Row convention (translator-centric, same as decoupled_N_traj.py and
depthcolorlinked_per_condition.py):
  rot_cfg=1 → Field B=CW, Field A=CCW
  rot_cfg=0 → Field B=CCW, Field A=CW
  b_green: True → Field B starts Green, Field A starts Red
  b_near:  True → Field B starts Near,  Field A starts Far

  CUED  params = Field B's properties when B is the translator.
  UNCUED params = Field B's properties for the complementary trial where
                  Field A (with the row label's identity) is the translator.
"""

import os
import datetime
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.lines import Line2D
import matplotlib.patches as mpatches
from matplotlib.backends.backend_pdf import PdfPages

DATE_STR = datetime.date.today().strftime('%Y-%m-%d')

# ── Paths ──────────────────────────────────────────────────────────────────────
BASE         = os.path.normpath(os.path.join(os.path.dirname(__file__), '../../Agents/Figures'))
BASE_SWAPPILOT = os.path.normpath(os.path.join(os.path.dirname(__file__), '../../Agents/SwapPilot/Figures'))
os.makedirs(BASE, exist_ok=True)
os.makedirs(BASE_SWAPPILOT, exist_ok=True)

# ── Timing ────────────────────────────────────────────────────────────────────
ONSET   = 56
T_START = 78
T_END   = 84
T_MID   = (T_START + T_END) / 2
TOTAL   = 114

# Motion codes
CW, LINEAR, NONCOH, CCW = 1, 2, 3, 4
PLOT_Y = {CW: 1, LINEAR: 2, NONCOH: 3, CCW: 4}

# Depth codes
NEAR, FAR = 1, 2

# Color codes  (separate from depth — b_green and b_near are independent)
RED, GREEN = 1, 2
COLOR_HEX = {RED: '#CC3333', GREEN: '#228B22', 0: '#DDDDDD'}

# Accent colors
C_DOT_CUE   = '#1a3a8b'
C_DOT_UNCUE = '#884400'

# Subfield symbols: S0=filled●, S1=open○, S2=filled▲, S3=open△
SF_MARKER = {0: 'o', 1: 'o', 2: '^', 3: '^'}
SF_FILLED = {0: True, 1: False, 2: True, 3: False}
SF_SIZE   = {0: 22, 1: 22, 2: 26, 3: 26}
SAMPLE_STEP = max(1, TOTAL // 20)

# ── Row definitions ───────────────────────────────────────────────────────────
# Label = translator identity.  CUED/UNCUED param dicts give Field B's properties
# in the corresponding trial type (same convention as decoupled_N_traj.py).
ROWS = [
    # ── CCW translates first (consistent with existing DCL traj convention) ──
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


# ── Build trajectory ──────────────────────────────────────────────────────────
def build(rot_cfg, b_green, b_near, cued, swap_type):
    """
    Returns mt[TOTAL,4], dep[TOTAL,4], col[TOTAL,4].

    Full identity swap at tStart (motion + depth + color):
      ZdA: S0↔S2 — S0 takes Field B identity (rot_b/d_B/c_B),
                    S2 takes Field A identity (rot_a/d_A/c_A).
           Translation: S2 still executes scheduled LINEAR (it was the cued translator);
                        S0 still executes scheduled LINEAR (uncued translator).
           S3 (unchanged Field B noise) gets NONCOH during Field B translation.
           S1 (unchanged Field A noise) gets NONCOH during Field A translation.
      ZdB: S1↔S3 — S1 takes Field B identity (rot_b/d_B/c_B),
                    S3 takes Field A identity (rot_a/d_A/c_A).
           Translation: S2 LINEAR (cued) / S0 LINEAR (uncued) as before.
           S1 (now Field B noise) gets NONCOH during Field B (cued) translation.
           S3 (now Field A noise) gets NONCOH during Field A (uncued) translation.
    Result: depth planes and motion groups are always monochromatic.
    """
    rot_b = CW  if rot_cfg == 1 else CCW
    rot_a = CCW if rot_cfg == 1 else CW
    d_B = NEAR  if b_near  else FAR
    d_A = FAR   if b_near  else NEAR
    c_B = GREEN if b_green else RED
    c_A = RED   if b_green else GREEN

    d_A_post_A = d_B; c_A_post_A = c_B   # S0 after ZdA (takes Field B)
    d_B_post_A = d_A; c_B_post_A = c_A   # S2 after ZdA (takes Field A)
    d_A_post_B = d_B; c_A_post_B = c_B   # S1 after ZdB (takes Field B)
    d_B_post_B = d_A; c_B_post_B = c_A   # S3 after ZdB (takes Field A)

    mt  = np.zeros((TOTAL, 4), dtype=int)
    dep = np.zeros((TOTAL, 4), dtype=int)
    col = np.zeros((TOTAL, 4), dtype=int)

    for f in range(TOTAL):
        ao  = f >= ONSET
        as_ = f >= T_START
        tr  = T_START <= f < T_END

        # ── Depth and color ──
        d0, d1 = d_A, d_A
        d2 = d_B if ao else 0
        d3 = d_B if ao else 0
        c0, c1 = c_A, c_A
        c2 = c_B if ao else 0
        c3 = c_B if ao else 0

        if as_:
            if swap_type == 'ZdA':
                d0, c0 = d_A_post_A, c_A_post_A
                if ao:
                    d2, c2 = d_B_post_A, c_B_post_A
            else:  # ZdB
                d1, c1 = d_A_post_B, c_A_post_B
                if ao:
                    d3, c3 = d_B_post_B, c_B_post_B

        # ── Motion ──
        if not as_:
            m0, m1 = rot_a, rot_a
            m2 = rot_b if ao else 0
            m3 = rot_b if ao else 0
        else:
            # Base rotations after full identity swap
            if swap_type == 'ZdA':
                # S0→Field B (rot_b), S1 unchanged (rot_a)
                # S2→Field A (rot_a), S3 unchanged (rot_b)
                m0b, m1b, m2b, m3b = rot_b, rot_a, rot_a, rot_b
            else:  # ZdB
                # S0 unchanged (rot_a), S1→Field B (rot_b)
                # S2 unchanged (rot_b), S3→Field A (rot_a)
                m0b, m1b, m2b, m3b = rot_a, rot_b, rot_b, rot_a

            if tr:
                if cued:   # Field B translation: S2=LINEAR
                    if swap_type == 'ZdA':
                        # S2 = scheduled translator → LINEAR
                        # S3 = unchanged Field B noise → NONCOH
                        m0, m1 = m0b, m1b
                        m2, m3 = LINEAR, NONCOH
                    else:  # ZdB
                        # S2 = unchanged Field B coherent → LINEAR
                        # S1 = now Field B noise → NONCOH
                        # S3 = now Field A noise → rot_a
                        m0 = m0b
                        m1 = NONCOH
                        m2 = LINEAR
                        m3 = m3b
                else:      # Field A translation: S0=LINEAR
                    if swap_type == 'ZdA':
                        # S0 = scheduled translator → LINEAR
                        # S1 = unchanged Field A noise → NONCOH
                        m0, m1 = LINEAR, NONCOH
                        m2, m3 = m2b, m3b
                    else:  # ZdB
                        # S0 = unchanged Field A coherent → LINEAR
                        # S3 = now Field A noise → NONCOH
                        # S1 = now Field B noise → rot_b
                        m0 = LINEAR
                        m1 = m1b
                        m2 = m2b
                        m3 = NONCOH
            else:
                m0, m1, m2, m3 = m0b, m1b, m2b, m3b

        mt[f]  = [m0, m1, m2, m3]
        dep[f] = [d0, d1, d2, d3]
        col[f] = [c0, c1, c2, c3]

    return mt, dep, col


# ── Translator metadata ────────────────────────────────────────────────────────
def translator_info(rot_cfg, b_green, b_near, cued, swap_type):
    """Return (trans_label, dot_s, dep_s, t_dep) for the info/title boxes."""
    rot_b = CW  if rot_cfg == 1 else CCW
    rot_a = CCW if rot_cfg == 1 else CW
    d_B = NEAR  if b_near  else FAR
    d_A = FAR   if b_near  else NEAR
    c_B = GREEN if b_green else RED
    c_A = RED   if b_green else GREEN

    if cued:
        rot_dir = rot_b
        # S2 is translator
        t_dep = d_A if swap_type == 'ZdA' else d_B   # ZdA: S2 swaps to A's depth
        t_col = c_A if swap_type == 'ZdA' else c_B
    else:
        rot_dir = rot_a
        # S0 is translator
        t_dep = d_B if swap_type == 'ZdA' else d_A   # ZdA: S0 swaps to B's depth
        t_col = c_B if swap_type == 'ZdA' else c_A

    rot_str = 'CW'  if rot_dir == CW  else 'CCW'
    col_str = 'Red' if t_col == RED   else 'Grn'
    dep_str = 'Near' if t_dep == NEAR else 'Far'
    trans_label = f'{col_str}/{rot_str}/{dep_str}'

    dot_s = '✓' if cued else '✗'
    # Depth✓ when translator's coherent subfield is unchanged (ZdB only)
    dep_s = '✓' if swap_type == 'ZdB' else '✗'

    return trans_label, dot_s, dep_s, t_dep


# ── Plot panel ────────────────────────────────────────────────────────────────
def plot_panel(ax_mt, ax_dep, mt, dep, col,
               rot_cfg, b_green, b_near, cued, swap_type):
    trans_label, dot_s, dep_s, t_dep = translator_info(
        rot_cfg, b_green, b_near, cued, swap_type)

    # Delayed-field label (Field B identity at onset, before any swap)
    b_col_str = 'Grn' if b_green else 'Red'
    b_rot_str = 'CW'  if rot_cfg == 1 else 'CCW'
    b_dep_str = 'Near' if b_near else 'Far'
    delayed_label = f'{b_col_str}/{b_rot_str}/{b_dep_str}'

    # ── Symbol assignment: tied to rotation direction, not field identity ──────
    # CCW field → triangles (▲/△);  CW field → circles (●/○)
    # Filled = coherent;  Open = noise
    # rot_cfg=0: B=CCW→triangles, A=CW→circles  (default)
    # rot_cfg=1: B=CW→circles,    A=CCW→triangles (swapped)
    if rot_cfg == 0:
        mk = {0: 'o', 1: 'o', 2: '^', 3: '^'}
        fl = {0: True, 1: False, 2: True, 3: False}
        sz = {0: 22,  1: 22,  2: 26,  3: 26}
    else:
        mk = {0: '^', 1: '^', 2: 'o', 3: 'o'}
        fl = {0: True, 1: False, 2: True, 3: False}
        sz = {0: 26,  1: 26,  2: 22,  3: 22}

    samples = list(range(0, TOTAL, SAMPLE_STEP))
    if samples[-1] != TOTAL - 1:
        samples.append(TOTAL - 1)

    for si in range(4):
        marker = mk[si]
        filled = fl[si]
        ms     = sz[si]

        # Faint connecting lines — colored by current subfield color
        # Break at T_START to avoid diagonal artifacts when subfields swap identity
        plot_y_mt = np.vectorize(lambda v: PLOT_Y.get(v, 0))(mt)
        for ax, arr in [(ax_mt, plot_y_mt), (ax_dep, dep)]:
            prev_f = prev_v = None
            for f in range(TOTAL):
                if f == T_START or f == T_END:
                    prev_f = prev_v = None  # break line at swap / end-of-translation
                v = arr[f, si] if arr[f, si] != 0 else None
                if v is None:
                    prev_f = prev_v = None
                    continue
                c = COLOR_HEX.get(col[f, si], '#DDDDDD')
                if prev_f is not None:
                    ax.plot([prev_f, f], [prev_v, v],
                            color=c, lw=0.5, alpha=0.4, zorder=2)
                prev_f, prev_v = f, v

        # Scatter symbols
        for f in samples:
            if col[f, si] == 0 or mt[f, si] == 0:
                continue
            c   = COLOR_HEX[col[f, si]]
            yv  = PLOT_Y[mt[f, si]]

            for ax, yval in [(ax_mt, yv), (ax_dep, dep[f, si])]:
                if dep[f, si] == 0:
                    continue
                if filled:
                    ax.scatter(f, yval, marker=marker, c=c,
                               edgecolors='none', s=ms, zorder=4)
                else:
                    ax.scatter(f, yval, marker=marker, facecolors='none',
                               edgecolors=c, s=ms, linewidths=1.1, zorder=4)

    # Phase markers
    for ax in (ax_mt, ax_dep):
        ax.axvspan(T_START, T_END, alpha=0.12, color='steelblue', zorder=1)

    # Gold band at translator's depth plane after tStart
    ax_dep.axhspan(t_dep - 0.40, t_dep + 0.40,
                   alpha=0.18, color='gold', zorder=0)

    # Annotation boxes above depth track — same positions as decoupled_N_traj.py
    # Left: delayed field identity (gold border)
    ax_dep.text(0.03, 1.10, f'* {delayed_label}',
                ha='left', va='bottom', fontsize=5.5, color='#111111',
                transform=ax_dep.transAxes, clip_on=False,
                bbox=dict(boxstyle='round,pad=0.25', facecolor='#fffde7',
                          edgecolor='#997700', lw=0.6))
    # Right: translator identity at tStart (gray border)
    ax_dep.text(0.97, 1.10, f'▶ {trans_label}',
                ha='right', va='bottom', fontsize=5.5, color='#111111',
                transform=ax_dep.transAxes, clip_on=False,
                bbox=dict(boxstyle='round,pad=0.25', facecolor='#f8f8f8',
                          edgecolor='#888888', lw=0.6))


    # Axes
    ax_mt.set_yticks([1, 2, 3, 4])
    ax_mt.set_yticklabels(['CW', 'Lin', 'NCH', 'CCW'], fontsize=5)
    ax_mt.set_ylim(0.4, 6.2)
    ax_mt.tick_params(axis='x', labelbottom=False)
    ax_mt.tick_params(axis='y', labelsize=5, length=2)
    ax_mt.set_xlim(-2, TOTAL + 1)

    ax_dep.set_yticks([NEAR, FAR])
    ax_dep.set_yticklabels(['Near', 'Far'], fontsize=5)
    ax_dep.set_ylim(0.4, 2.6)
    ax_dep.set_xlabel('Frame', fontsize=5)
    ax_dep.tick_params(axis='both', labelsize=5, length=2)
    ax_dep.set_xlim(-2, TOTAL + 1)

    for ax in (ax_mt, ax_dep):
        ax.spines[['top', 'right']].set_visible(False)


# ── Legend ─────────────────────────────────────────────────────────────────────
def make_legend():
    return [
        Line2D([0],[0], marker='^', color='w', markerfacecolor='#666',
               markersize=8, ls='None', label='▲ CCW field · coherent  (filled triangle)'),
        Line2D([0],[0], marker='^', color='w', markerfacecolor='none',
               markeredgecolor='#666', markersize=8, markeredgewidth=1.3,
               ls='None', label='△ CCW field · noise  (open triangle)'),
        Line2D([0],[0], marker='o', color='w', markerfacecolor='#666',
               markersize=7, ls='None', label='● CW field · coherent  (filled circle)'),
        Line2D([0],[0], marker='o', color='w', markerfacecolor='none',
               markeredgecolor='#666', markersize=7, markeredgewidth=1.3,
               ls='None', label='○ CW field · noise  (open circle)'),
        mpatches.Patch(facecolor='none', edgecolor='#CC3333', lw=1.5,
                       label='Red color label'),
        mpatches.Patch(facecolor='none', edgecolor='#228B22', lw=1.5,
                       label='Green color label'),
        mpatches.Patch(facecolor='#fffde7', edgecolor='#997700', lw=0.8,
                       label='* = delayed field identity at onset'),
        mpatches.Patch(facecolor='#f8f8f8', edgecolor='#888888', lw=0.8,
                       label='▶ = translator identity at tStart'),
        mpatches.Patch(facecolor='gold', alpha=0.4, edgecolor='#999',
                       label='Translator depth plane'),
        mpatches.Patch(facecolor='steelblue', alpha=0.2, edgecolor='none',
                       label='Translation window'),
    ]


# ── Page / figure builders ────────────────────────────────────────────────────
COND_META = {
    'ZdA': dict(
        title='ZdA (ZdCoh): coherent subfields exchange depth+color at tStart',
        cued_title  ='Dot✓   Depth✗   Color✗',
        uncued_title='Dot✗   Depth✗   Color✗',
    ),
    'ZdB': dict(
        title='ZdB (ZdNoi): noise subfields exchange depth+color at tStart; coherent subfields unchanged',
        cued_title  ='Dot✓   Depth✓   Color✓',
        uncued_title='Dot✗   Depth✓   Color✓',
    ),
}


def build_figure(swap_type, row_subset, figsize=(8.5, 11), page_num=None, total_pages=None, filename=''):
    meta = COND_META[swap_type]
    n    = len(row_subset)
    fig  = plt.figure(figsize=figsize)
    fig.patch.set_facecolor('white')
    fig.suptitle(
        f'Exp_DepthColorLinked_005m  ·  {meta["title"]}\n'
        '▲△=CCW field  ●○=CW field  ·  filled=coherent  open=noise  '
        '·  Color=current subfield color  ·  Gold=translator depth  ·  Blue=translation window',
        fontsize=7.5, y=1.01, va='bottom')
    footer = filename + (f'  ·  {DATE_STR}' if filename else DATE_STR)
    fig.text(0.01, 0.005, footer, fontsize=5, color='#888888', ha='left', va='bottom')
    if page_num is not None and total_pages is not None:
        fig.text(0.99, 0.005, f'p. {page_num}/{total_pages}', fontsize=5,
                 color='#888888', ha='right', va='bottom')

    gs = gridspec.GridSpec(
        n * 2, 2,
        height_ratios=[3, 1.5] * n,
        hspace=0.55, wspace=0.38,
        top=0.89, bottom=0.09, left=0.12, right=0.99,
    )

    for ri, row in enumerate(row_subset):
        for ci, side in enumerate(['cued', 'uncued']):
            params = row[side]
            rc = params['rot_cfg']
            bg = params['b_green']
            bn = params['b_near']
            cued_flag = (side == 'cued')

            mt, dep, col = build(rc, bg, bn, cued_flag, swap_type)
            _, dot_s, dep_s, _ = translator_info(rc, bg, bn, cued_flag, swap_type)

            ax_mt  = fig.add_subplot(gs[ri * 2,     ci])
            ax_dep = fig.add_subplot(gs[ri * 2 + 1, ci], sharex=ax_mt)

            plot_panel(ax_mt, ax_dep, mt, dep, col, rc, bg, bn, cued_flag, swap_type)

            # Panel title: Dot✓/✗   Depth✓/✗   Color✓/✗
            title_str = f'Dot{dot_s}   Depth{dep_s}   Color{dep_s}'
            cc = C_DOT_CUE if cued_flag else C_DOT_UNCUE
            ax_mt.set_title(title_str, fontsize=6, pad=5, color=cc,
                            fontweight='bold',
                            bbox=dict(boxstyle='round,pad=0.35',
                                      facecolor='#f0f4ff' if cued_flag else '#fff4e8',
                                      edgecolor=cc, lw=0.8))

            # Row label on leftmost column
            if ci == 0:
                ax_mt.set_ylabel(row['label'] + '\n\nMotion', fontsize=6,
                                 fontweight='bold', labelpad=4)
            else:
                ax_mt.set_ylabel('Motion', fontsize=5)
            ax_dep.set_ylabel('Depth', fontsize=5)

    return fig


def build_condensed(swap_type, figsize=(11, 17), filename='', page_num=None, total_pages=None):
    """All 16 panels (8 rows × CUED/UNCUED) in 4 quadrants — one page."""
    meta = COND_META[swap_type]
    fig  = plt.figure(figsize=figsize)
    fig.patch.set_facecolor('white')
    fig.suptitle(
        f'Exp_DepthColorLinked_005m  ·  {meta["title"]}  ·  All 16 permutations\n'
        '▲△=CCW field  ●○=CW field  ·  filled=coherent  open=noise  '
        '·  Color=current subfield color',
        fontsize=7.5, fontweight='bold', y=0.99)
    footer = filename + (f'  ·  {DATE_STR}' if filename else DATE_STR)
    fig.text(0.01, 0.005, footer, fontsize=5, color='#888888', ha='left', va='bottom')
    pg_str = (f'p. {page_num}/{total_pages}' if page_num is not None and total_pages is not None
              else 'p. 1/1')
    fig.text(0.99, 0.005, pg_str, fontsize=5, color='#888888', ha='right', va='bottom')

    outer = gridspec.GridSpec(2, 2, hspace=0.28, wspace=0.28,
                              top=0.94, bottom=0.04, left=0.09, right=0.99)
    quad_slices = [ROWS[0:2], ROWS[2:4], ROWS[4:6], ROWS[6:8]]

    for qi, row_subset in enumerate(quad_slices):
        qr, qc = divmod(qi, 2)
        n = len(row_subset)
        inner = gridspec.GridSpecFromSubplotSpec(
            n * 2, 2, subplot_spec=outer[qr, qc],
            height_ratios=[3, 1.5] * n,
            hspace=0.55, wspace=0.38,
        )
        for ri, row in enumerate(row_subset):
            for ci, side in enumerate(['cued', 'uncued']):
                params = row[side]
                rc, bg, bn = params['rot_cfg'], params['b_green'], params['b_near']
                cued_flag = (side == 'cued')

                mt, dep, col = build(rc, bg, bn, cued_flag, swap_type)
                _, dot_s, dep_s, _ = translator_info(rc, bg, bn, cued_flag, swap_type)

                ax_mt  = fig.add_subplot(inner[ri * 2,     ci])
                ax_dep = fig.add_subplot(inner[ri * 2 + 1, ci], sharex=ax_mt)

                plot_panel(ax_mt, ax_dep, mt, dep, col, rc, bg, bn, cued_flag, swap_type)

                title_str = f'Dot{dot_s}   Depth{dep_s}   Color{dep_s}'
                cc = C_DOT_CUE if cued_flag else C_DOT_UNCUE
                ax_mt.set_title(title_str, fontsize=5, pad=4, color=cc,
                                fontweight='bold',
                                bbox=dict(boxstyle='round,pad=0.3',
                                          facecolor='#f0f4ff' if cued_flag else '#fff4e8',
                                          edgecolor=cc, lw=0.7))
                if ci == 0:
                    ax_mt.set_ylabel(row['label'] + '\nMot', fontsize=5,
                                     fontweight='bold', labelpad=3)
                else:
                    ax_mt.set_ylabel('Mot', fontsize=4)
                ax_dep.set_ylabel('Dep', fontsize=4)

    return fig


# ── Generate outputs ───────────────────────────────────────────────────────────
ROWS_PER_PAGE = 2
page_groups = [ROWS[i:i+ROWS_PER_PAGE] for i in range(0, len(ROWS), ROWS_PER_PAGE)]

for swap in ('ZdA', 'ZdB'):
    out_pdf  = os.path.join(BASE, f'depthcolorlinked_{swap}_allperms.pdf')
    out_cond = os.path.join(BASE, f'depthcolorlinked_{swap}_condensed.pdf')
    out_png  = os.path.join(BASE, f'depthcolorlinked_{swap}_allperms.png')

    # Multi-page PDF (2 rows per page)
    n_pages = len(page_groups)
    pdf_fname = os.path.basename(out_pdf)
    with PdfPages(out_pdf) as pdf:
        for pi, grp in enumerate(page_groups, 1):
            fig_p = build_figure(swap, grp, figsize=(8.5, 11),
                                 page_num=pi, total_pages=n_pages,
                                 filename=pdf_fname)
            pdf.savefig(fig_p, bbox_inches='tight')
            plt.close(fig_p)
    print(f'Saved: {out_pdf}')

    # Condensed single-page PDF
    cond_fname = os.path.basename(out_cond)
    fig_c = build_condensed(swap, figsize=(11, 17), filename=cond_fname,
                            page_num=1, total_pages=1)
    with PdfPages(out_cond) as pdf:
        pdf.savefig(fig_c, bbox_inches='tight')
    plt.close(fig_c)
    print(f'Saved: {out_cond}')

    # Full-height PNG (all 8 rows)
    fig_all = build_figure(swap, ROWS, figsize=(10, 20))
    fig_all.savefig(out_png, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close(fig_all)
    print(f'Saved: {out_png}')

# ── Combined condensed PDF (ZdA p.1 + ZdB p.2) → SwapPilot/Figures ───────────
combined_fname = 'depthcolorlinked_combined_condensed.pdf'
out_combined = os.path.join(BASE_SWAPPILOT, combined_fname)
swap_list = ('ZdA', 'ZdB')
with PdfPages(out_combined) as pdf:
    for pi, swap in enumerate(swap_list, 1):
        fig_c = build_condensed(swap, figsize=(11, 17), filename=combined_fname,
                                page_num=pi, total_pages=len(swap_list))
        pdf.savefig(fig_c, bbox_inches='tight')
        plt.close(fig_c)
print(f'Saved: {out_combined}')
