#!/usr/bin/env python3
"""
depth_color_linked_traj.py
--------------------------
Trajectory figure for Exp_DepthColorLinked_005m — analogous to
decoupled_dots_traj.py (same layout, same annotation style).

Near=Red, Far=Green (linkDepthColor=1). No color-only rows.
4 subfield symbols (filled/open × circle/triangle) replace the
solid/dashed line styles used in DecoupledDots.

Swap mechanics (ZdA / ZdB):
  ZdA — coherent subfields (S0+S2) swap depth+color at tStart
  ZdB — noise subfields (S1+S3) swap depth+color at tStart

Row labeling (translator-centric):
  ZdNoi — translator's coherent dots stay in onset plane  (Depth✓ for CUED)
           = ZdB when CUED; = ZdA when UNCUED
  ZdCoh — translator's coherent dots change plane         (Depth✗ for CUED)
           = ZdA when CUED; = ZdB when UNCUED

Layout (mirrors DecoupledDots):
  Rows : ZdNoi, ZdCoh        (swap condition — row label on left)
  Cols : Dot✓-Near, Dot✗-Near, Dot✓-Far, Dot✗-Far

Per panel:
  Title box    : Dot✓/✗   Depth✓/✗
  Info box     : translator Color/Dir/Depth at tStart (above translation window)
  Gold band    : translator depth plane during translation
  Blue shade   : translation window

Output: Agents/Figures/depth_color_linked_traj.png / .pdf
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

BASE     = os.path.normpath(os.path.join(os.path.dirname(__file__),
                                          '../../Agents/Figures'))
OUT_PATH = os.path.join(BASE, 'depth_color_linked_traj.png')
OUT_PDF  = os.path.join(BASE, 'depth_color_linked_traj.pdf')

# ── Timing (frames at 75 Hz) ──────────────────────────────────────────────────
ONSET   = 56
T_START = 78
T_END   = 84
T_MID   = (T_START + T_END) / 2
TOTAL   = 114

# Motion codes
CW, LINEAR, NONCOH, CCW = 1, 2, 3, 4
# NONCOH plotted at LINEAR y-level (same as DecoupledDots convention)
# T(c) and T(n) at separate y-levels so field splitting is visible
PLOT_Y = {CW: 1, LINEAR: 2, NONCOH: 3, CCW: 4}

# Depth codes
NEAR, FAR = 1, 2

# Color scheme — Near=Red, Far=Green (fixed for this experiment)
C_NEAR  = '#CC3333'
C_FAR   = '#228B22'
DEPTH_COLOR = {NEAR: C_NEAR, FAR: C_FAR, 0: '#DDDDDD'}

# Row accent colors (match DecoupledDots Z/N convention)
ROW_COLOR = {'ZdNoi': '#1a6b1a', 'ZdCoh': '#c0392b'}
C_DOT_CUE   = '#1a3a8b'
C_DOT_UNCUE = '#884400'

# 4 subfield symbols: filled/open × circle/triangle
#   S0 = Field A coh  : filled circle
#   S1 = Field A noise: open circle
#   S2 = Field B coh  : filled triangle
#   S3 = Field B noise: open triangle
SF_MARKER  = {0: 'o', 1: 'o', 2: '^', 3: '^'}
SF_FILLED  = {0: True, 1: False, 2: True, 3: False}
SF_SIZE    = {0: 22, 1: 22, 2: 26, 3: 26}
SAMPLE_STEP = max(1, TOTAL // 20)


# ── Build trajectory ──────────────────────────────────────────────────────────
def build(row, delayed_depth, cued):
    """
    row          : 'ZdNoi' or 'ZdCoh'
    delayed_depth: NEAR or FAR (depth of the delayed-onset Field B)
    cued         : True → Field B translates; False → Field A translates

    ZdA swaps coherent subfields S0+S2 at tStart.
    ZdB swaps noise subfields S1+S3 at tStart.

    ZdNoi for CUED  = ZdB  (translator = S2 stays)
    ZdCoh for CUED  = ZdA  (translator = S2 swaps)
    ZdNoi for UNCUED = ZdA  (translator = S0 stays)
    ZdCoh for UNCUED = ZdB  (translator = S0 swaps)
    """
    a_dep = FAR if delayed_depth == NEAR else NEAR
    b_dep = delayed_depth

    # Determine which swap type this panel corresponds to
    if row == 'ZdNoi':
        zda = not cued   # ZdA only when UNCUED+ZdNoi
    else:               # ZdCoh
        zda = cued       # ZdA only when CUED+ZdCoh

    mt    = np.zeros((TOTAL, 4), dtype=int)
    dep   = np.zeros((TOTAL, 4), dtype=int)

    for f in range(TOTAL):
        ao  = f >= ONSET
        as_ = f >= T_START
        tr  = T_START <= f < T_END

        # Depth (pre-swap defaults)
        d0, d1 = a_dep, a_dep
        d2 = b_dep if ao else 0
        d3 = b_dep if ao else 0

        if as_:
            if zda:   # ZdA: S0+S2 swap
                d0 = b_dep
                if ao: d2 = a_dep
            else:     # ZdB: S1+S3 swap
                d1 = b_dep
                if ao: d3 = a_dep

        # Motion
        if not as_:
            m0, m1 = CW, CW
            m2 = CCW if ao else 0
            m3 = CCW if ao else 0
        elif tr:
            if cued:   # Field B (S2) translates
                m0, m1 = CW, CW
                m2, m3 = LINEAR, NONCOH
            else:      # Field A (S0) translates
                m0, m1 = LINEAR, NONCOH
                m2 = CCW if ao else 0
                m3 = CCW if ao else 0
        else:
            m0, m1 = CW, CW
            m2 = CCW if ao else 0
            m3 = CCW if ao else 0

        mt[f]  = [m0, m1, m2, m3]
        dep[f] = [d0, d1, d2, d3]

    return mt, dep


def translator_info(row, delayed_depth, cued):
    """Translator color/dir/depth at tStart + cueing checkmarks."""
    a_dep = FAR if delayed_depth == NEAR else NEAR
    b_dep = delayed_depth

    if cued:
        dirn = 'CCW'
        t_dep = b_dep if row == 'ZdNoi' else a_dep
    else:
        dirn = 'CW'
        t_dep = a_dep if row == 'ZdNoi' else b_dep

    col_str = 'Red' if t_dep == NEAR else 'Grn'
    dep_str = 'Near' if t_dep == NEAR else 'Far'
    trans_label = f'{col_str}/{dirn}/{dep_str}'

    dot_s = '✓' if cued else '✗'
    # Depth✓ when translator ends at b_dep (the delayed field's onset depth)
    dep_ok = (t_dep == b_dep)
    dep_s = '✓' if dep_ok else '✗'

    return trans_label, dot_s, dep_s, t_dep


# ── Plot panel ────────────────────────────────────────────────────────────────
def plot_panel(ax_mt, ax_dep, mt, dep, row, delayed_depth, cued):
    trans_label, dot_s, dep_s, t_dep = translator_info(row, delayed_depth, cued)
    b_dep = delayed_depth
    a_dep = FAR if delayed_depth == NEAR else NEAR
    # Color✓/✗ = Depth✓/✗ in this experiment (always confounded)
    col_s = dep_s

    # Field B onset attributes annotation
    b_onset_col = 'Red' if b_dep == NEAR else 'Grn'
    b_onset_dep = 'Near' if b_dep == NEAR else 'Far'
    b_onset_label = f'B onset: {b_onset_col}/CCW/{b_onset_dep}'

    samples = list(range(0, TOTAL, SAMPLE_STEP))
    if samples[-1] != TOTAL - 1:
        samples.append(TOTAL - 1)

    for si in range(4):
        mk     = SF_MARKER[si]
        filled = SF_FILLED[si]
        ms     = SF_SIZE[si]

        # Faint connecting lines (split at depth changes)
        plot_y_mt = np.vectorize(lambda v: PLOT_Y.get(v, 0))(mt)
        for ax, arr in [(ax_mt, plot_y_mt), (ax_dep, dep)]:
            prev_f = prev_v = None
            for f in range(TOTAL):
                v = arr[f, si] if arr[f, si] != 0 else None
                if v is None:
                    prev_f = prev_v = None
                    continue
                d = dep[f, si]
                c = DEPTH_COLOR.get(d, '#DDDDDD')
                if prev_f is not None:
                    ax.plot([prev_f, f], [prev_v, v],
                            color=c, lw=0.5, alpha=0.4, zorder=2)
                prev_f, prev_v = f, v

        # Scatter symbols
        for f in samples:
            d = dep[f, si]
            if d == 0 or mt[f, si] == 0:
                continue
            col = DEPTH_COLOR[d]
            yv  = PLOT_Y[mt[f, si]]

            for ax, yval in [(ax_mt, yv), (ax_dep, d)]:
                if filled:
                    ax.scatter(f, yval, marker=mk, c=col,
                               edgecolors='none', s=ms, zorder=4)
                else:
                    ax.scatter(f, yval, marker=mk, facecolors='none',
                               edgecolors=col, s=ms, linewidths=1.1, zorder=4)

    # Phase markers
    for ax in (ax_mt, ax_dep):
        ax.axvspan(T_START, T_END, alpha=0.12, color='steelblue', zorder=1)

    # Gold band at translator depth
    ax_dep.axhspan(t_dep - 0.40, t_dep + 0.40,
                   alpha=0.18, color='gold', zorder=0)

    # Small info box above translation window: translator state at tStart
    ax_mt.text(T_MID, 5.55, trans_label,
               ha='center', va='bottom', fontsize=4.5, color='#111',
               clip_on=False,
               bbox=dict(boxstyle='round,pad=0.25', facecolor='#f8f8f8',
                         edgecolor='#999', lw=0.6))

    # Field B onset annotation (at ONSET frame)
    ax_mt.text(ONSET + 1, 5.55, b_onset_label,
               ha='left', va='bottom', fontsize=4.2, color='#444',
               clip_on=False,
               bbox=dict(boxstyle='round,pad=0.20', facecolor='#fff8f0',
                         edgecolor='#bbaa88', lw=0.5))

    # Axes — T(c) and T(n) at separate y-levels
    ax_mt.set_yticks([1, 2, 3, 4])
    ax_mt.set_yticklabels(['CW', 'T(c)', 'T(n)', 'CCW'], fontsize=5)
    ax_mt.set_ylim(0.4, 6.2)
    ax_mt.tick_params(axis='x', labelbottom=False)
    ax_mt.tick_params(axis='y', labelsize=5, length=2)
    ax_mt.set_xlim(-2, TOTAL + 1)

    ax_dep.set_yticks([NEAR, FAR])
    ax_dep.set_yticklabels(['Near\n(Red)', 'Far\n(Grn)'], fontsize=5)
    ax_dep.set_ylim(0.4, 2.6)
    ax_dep.set_xlabel('Frame', fontsize=5)
    ax_dep.tick_params(axis='both', labelsize=5, length=2)
    ax_dep.set_xlim(-2, TOTAL + 1)

    for ax in (ax_mt, ax_dep):
        ax.spines[['top', 'right']].set_visible(False)


# ── Layout ────────────────────────────────────────────────────────────────────
# Rows: ZdNoi (top), ZdCoh (bottom)  — stable condition first, same as N before Z
# Cols: Dot✓-Near, Dot✗-Near, Dot✓-Far, Dot✗-Far  (mirrors DecoupledDots)
ROW_DEFS = ['ZdNoi', 'ZdCoh']
COL_DEFS = [
    (True,  NEAR),   # Dot✓ · Near
    (False, NEAR),   # Dot✗ · Near
    (True,  FAR),    # Dot✓ · Far
    (False, FAR),    # Dot✗ · Far
]

COL_HEADERS = [
    'Dot✓\nDel=Red/CCW/Near',
    'Dot✗\nDel=Red/CCW/Near',
    'Dot✓\nDel=Red/CCW/Far',
    'Dot✗\nDel=Red/CCW/Far',
]
ROW_LABELS = {
    'ZdNoi': 'ZdNoi\nCoh dots stay\nin onset plane',
    'ZdCoh': 'ZdCoh\nCoh dots change\ndepth+color',
}

fig = plt.figure(figsize=(20, 12))
fig.patch.set_facecolor('white')
fig.suptitle(
    'Exp_DepthColorLinked_005m — Trajectories\n'
    'Near=Red  ·  Far=Green  ·  linkDepthColor=1  ·  '
    'ZdA: coherent subfields (S0+S2) swap depth+color at tStart  ·  '
    'ZdB: noise subfields (S1+S3) swap\n'
    'Filled = coherent subfield  ·  Open = noise subfield  ·  '
    'Circle = Field A (always-on, CW)  ·  Triangle = Field B (delayed, CCW)  ·  '
    'Color = depth plane at that frame\n'
    'Title box: Dot/Depth cueing (✓/✗)  ·  '
    'Small box above translation window: translator Color/Dir/Depth at tStart  ·  '
    'Gold = translator depth plane  ·  Blue = translation window',
    fontsize=8.5, y=1.02, va='bottom')

outer = gridspec.GridSpec(2, 4, hspace=1.05, wspace=0.38,
                          left=0.09, right=0.99, top=0.93, bottom=0.08)

for ri, row in enumerate(ROW_DEFS):
    rc = ROW_COLOR[row]
    for ci, (cued, ddep) in enumerate(COL_DEFS):

        inner = gridspec.GridSpecFromSubplotSpec(
            2, 1, subplot_spec=outer[ri, ci],
            height_ratios=[3, 1.5], hspace=0.06)

        ax_mt  = fig.add_subplot(inner[0])
        ax_dep = fig.add_subplot(inner[1], sharex=ax_mt)

        mt, dep = build(row, ddep, cued)
        _, dot_s, dep_s, _ = translator_info(row, ddep, cued)
        col_s = dep_s  # Color✓/✗ = Depth✓/✗ (always confounded here)
        # Panel title box
        cueing_title = f'Dot{dot_s}   Depth{dep_s}   Color{col_s}'
        cc = C_DOT_CUE if cued else C_DOT_UNCUE
        ax_mt.set_title(cueing_title, fontsize=6.5, pad=5, color=cc,
                        fontweight='bold',
                        bbox=dict(boxstyle='round,pad=0.35',
                                  facecolor='#f0f4ff' if cued else '#fff4e8',
                                  edgecolor=cc, lw=0.8))

        plot_panel(ax_mt, ax_dep, mt, dep, row, ddep, cued)

        # Row labels (leftmost column only)
        if ci == 0:
            ax_mt.set_ylabel(ROW_LABELS[row] + '\n\nMotion',
                             fontsize=6, fontweight='bold', color=rc, labelpad=4)
        else:
            ax_mt.set_ylabel('Motion', fontsize=5)
        ax_dep.set_ylabel('Depth', fontsize=5)

        # Column + panel title (top row only)
        if ri == 0:
            ax_mt.set_title(COL_HEADERS[ci] + '\n' + cueing_title,

                            fontsize=6.5, fontweight='bold', pad=14, color=cc,
                            bbox=dict(boxstyle='round,pad=0.35',
                                      facecolor='#f0f4ff' if cued else '#fff4e8',
                                      edgecolor=cc, lw=0.8))

# ── Legend ────────────────────────────────────────────────────────────────────
legend_handles = [
    Line2D([0],[0], marker='o', color='w', markerfacecolor=C_NEAR,
           markersize=7, ls='None', label='S0 ● Field A · coh  (filled circle, default Near=Red)'),
    Line2D([0],[0], marker='o', color='w', markerfacecolor='none',
           markeredgecolor=C_NEAR, markersize=7, markeredgewidth=1.3,
           ls='None', label='S1 ○ Field A · noise  (open circle)'),
    Line2D([0],[0], marker='^', color='w', markerfacecolor=C_FAR,
           markersize=7, ls='None', label='S2 ▲ Field B · coh  (filled triangle, default Far=Green)'),
    Line2D([0],[0], marker='^', color='w', markerfacecolor='none',
           markeredgecolor=C_FAR, markersize=7, markeredgewidth=1.3,
           ls='None', label='S3 △ Field B · noise  (open triangle)'),
    mpatches.Patch(facecolor='none', edgecolor='#CC3333', lw=1.5,
                   label='Near plane color (Red)'),
    mpatches.Patch(facecolor='none', edgecolor='#228B22', lw=1.5,
                   label='Far plane color (Green)'),
    mpatches.Patch(facecolor='gold', alpha=0.4, edgecolor='#999',
                   label='Translator depth plane'),
    mpatches.Patch(facecolor='steelblue', alpha=0.2, edgecolor='none',
                   label='Translation window'),
]

fig.legend(handles=legend_handles, loc='lower center', ncol=5,
           fontsize=7, frameon=True, framealpha=0.95,
           edgecolor='#CCC', bbox_to_anchor=(0.5, -0.05))

fig.text(0.01, 0.005, f'{os.path.basename(OUT_PDF)}  ·  {DATE_STR}', fontsize=5, color='#888888', ha='left', va='bottom')
fig.text(0.99, 0.005, f'p. 1/1', fontsize=5, color='#888888', ha='right', va='bottom')
os.makedirs(BASE, exist_ok=True)
fig.savefig(OUT_PATH, dpi=150, bbox_inches='tight', facecolor='white')
with PdfPages(OUT_PDF) as pdf:
    pdf.savefig(fig, bbox_inches='tight')
plt.close(fig)
print(f'Saved: {OUT_PATH}')
print(f'Saved: {OUT_PDF}')
