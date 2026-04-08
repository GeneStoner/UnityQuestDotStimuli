#!/usr/bin/env python3
"""
Trajectory figure for Exp_DecoupledDots_005m — Stoner & Blanc line style.

Line convention (follows Stoner & Blanc 2010):
  Field A (always-on, CW):  SOLID lines   (bottom track in motion panel)
  Field B (delayed, CCW):   DASHED lines  (top track — dashed on top, arbitrary)
  Coherent subfield: heavy line;  Noise subfield: light line.

Layout (transposed from original):
  Rows : N, C, Z, CZ          (swap type — row label on left)
  Cols : CUED-Near, CUED-Far, UNCUED-Near, UNCUED-Far

Within each row (same swap), CUED and UNCUED panels are identical except for
which field translates at tStart. Before tStart they are visually identical:
same pre-onset display (Field A only), same delayed-onset event (Field B
appears), same rotation. They diverge only at the translation window.

Output: Agents/Figures/decoupled_dots_traj.png
"""

import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.lines import Line2D
import matplotlib.patches as mpatches

OUT_PATH = os.path.expanduser(
    '~/Projects/ObjectBasedAttention/VRDots/Agents/Figures/decoupled_dots_traj.png')

# ── Timing (frames at 75 Hz) ──────────────────────────────────────────────
ONSET   = 56
T_START = 78
T_END   = 84
TOTAL   = 114

# Motion codes
CW, LINEAR, NONCOH, CCW = 1, 2, 3, 4
MOT_LABELS = {CW: 'CW', LINEAR: 'T(c)', NONCOH: 'T(n)', CCW: 'CCW'}

# Depth codes
NEAR, FAR = 1, 2

# Field color codes
F_RED, F_GRN = 1, 2
FIELD_COLOR  = {F_RED: '#CC3333', F_GRN: '#228B22', 0: '#DDDDDD'}
DEPTH_COLOR  = {NEAR: '#AA2222', FAR: '#116611'}

# Line weights: heavy for coherent subfield, light for noise subfield
LW = {0: 1.8, 1: 0.9, 2: 1.8, 3: 0.9}   # keyed by subfield index

C_CUED   = '#1a3a8b'
C_UNCUED = '#884400'
SWAP_COLORS = {'N': '#444444', 'C': '#CC6600', 'Z': '#116688', 'CZ': '#553388'}


def build(swap, delayed_depth, cued):
    """
    swap          : 'N', 'C', 'Z', 'CZ'
    delayed_depth : NEAR or FAR  — depth of Field B (delayed onset)
    cued          : True = S2 translates (Field B); False = S0 translates (Field A)
    Returns mt[TOTAL,4], dep[TOTAL,4], fcol[TOTAL,4]
    """
    a_dep = FAR  if delayed_depth == NEAR else NEAR
    b_dep = delayed_depth

    color_swap = swap in ('C', 'CZ')
    depth_swap = swap in ('Z', 'CZ')

    A_COL_DEFAULT = F_GRN
    B_COL_DEFAULT = F_RED

    mt   = np.zeros((TOTAL, 4), dtype=int)
    dep  = np.zeros((TOTAL, 4), dtype=int)
    fcol = np.zeros((TOTAL, 4), dtype=int)

    for f in range(TOTAL):
        ao  = f >= ONSET
        as_ = f >= T_START
        tr  = T_START <= f < T_END

        a_col = B_COL_DEFAULT if (color_swap and as_) else A_COL_DEFAULT
        b_col = A_COL_DEFAULT if (color_swap and as_) else B_COL_DEFAULT

        a_d = b_dep if (depth_swap and as_) else a_dep
        b_d = a_dep if (depth_swap and as_) else b_dep

        if not as_:
            m = [CW, CW,
                 CCW if ao else 0,
                 CCW if ao else 0]
        elif tr:
            if cued:
                m = [CW, CW, LINEAR, NONCOH]
            else:
                m = [LINEAR, NONCOH, CCW, CCW]
        else:
            m = [CW, CW, CCW, CCW]

        mt[f]   = m
        dep[f]  = [a_d,  a_d,
                   b_d if ao else 0,
                   b_d if ao else 0]
        fcol[f] = [a_col, a_col,
                   b_col if ao else 0,
                   b_col if ao else 0]

    return mt, dep, fcol


def plot_panel(ax_mt, ax_dep, mt, dep, fcol, title, swap, cued, delayed_depth):
    """Draw a single panel using Stoner & Blanc line style."""

    for si in range(4):
        # Field A = subfields 0,1 → solid; Field B = subfields 2,3 → dashed
        ls  = '--' if si >= 2 else '-'
        lw  = LW[si]

        # Collect frames where this subfield is active
        frames = [f for f in range(TOTAL)
                  if fcol[f, si] != 0 and mt[f, si] != 0]
        if not frames:
            continue

        # Split into pre-tStart and post-tStart segments to handle color changes
        segments = []
        seg_start = frames[0]
        seg_col_m   = FIELD_COLOR[fcol[frames[0], si]]
        seg_col_d   = DEPTH_COLOR[dep[frames[0], si]]

        for idx, f in enumerate(frames):
            new_col_m = FIELD_COLOR[fcol[f, si]]
            new_col_d = DEPTH_COLOR[dep[f, si]]
            # Break segment on color or depth change
            if new_col_m != seg_col_m or new_col_d != seg_col_d:
                # flush current segment up to (not including f)
                seg_frames = [x for x in frames if seg_start <= x < f]
                if seg_frames:
                    ax_mt.plot(seg_frames, [mt[x, si] for x in seg_frames],
                               color=seg_col_m, ls=ls, lw=lw, solid_capstyle='round',
                               zorder=4)
                    ax_dep.plot(seg_frames, [dep[x, si] for x in seg_frames],
                                color=seg_col_d, ls=ls, lw=lw, solid_capstyle='round',
                                zorder=4)
                seg_start = f
                seg_col_m = new_col_m
                seg_col_d = new_col_d

        # flush final segment
        seg_frames = [x for x in frames if x >= seg_start]
        if seg_frames:
            ax_mt.plot(seg_frames, [mt[x, si] for x in seg_frames],
                       color=seg_col_m, ls=ls, lw=lw, solid_capstyle='round',
                       zorder=4)
            ax_dep.plot(seg_frames, [dep[x, si] for x in seg_frames],
                        color=seg_col_d, ls=ls, lw=lw, solid_capstyle='round',
                        zorder=4)

    # Phase markers
    for ax in (ax_mt, ax_dep):
        ax.axvspan(T_START, T_END, alpha=0.12, color='steelblue', zorder=1)
        ax.axvline(ONSET,   color='#CCCCCC', lw=0.7, ls=':', zorder=2)
        ax.axvline(T_START, color='#6688AA', lw=0.8, ls='--', zorder=2)

    # Highlight translator depth plane after tStart
    if cued:
        trans_dep = (FAR if (swap in ('Z','CZ')) else delayed_depth) \
                    if delayed_depth == NEAR else \
                    (NEAR if (swap in ('Z','CZ')) else delayed_depth)
    else:
        a_dep_default = FAR if delayed_depth == NEAR else NEAR
        trans_dep = (delayed_depth if (swap in ('Z','CZ')) else a_dep_default)
    ax_dep.axhspan(trans_dep - 0.40, trans_dep + 0.40,
                   alpha=0.18, color='gold', zorder=0)

    # Motion axis
    ax_mt.set_yticks([CW, LINEAR, NONCOH, CCW])
    ax_mt.set_yticklabels(['CW', 'T(c)', 'T(n)', 'CCW'], fontsize=5)
    ax_mt.set_ylim(0.4, 4.6)
    ax_mt.tick_params(axis='x', labelbottom=False)
    ax_mt.tick_params(axis='y', labelsize=5, length=2)
    ax_mt.set_xlim(-2, TOTAL + 1)

    # Depth axis
    ax_dep.set_yticks([NEAR, FAR])
    ax_dep.set_yticklabels(['Near', 'Far'], fontsize=5)
    ax_dep.set_ylim(0.4, 2.6)
    ax_dep.set_xlabel('Frame', fontsize=5)
    ax_dep.tick_params(axis='both', labelsize=5, length=2)
    ax_dep.set_xlim(-2, TOTAL + 1)

    ax_mt.set_title(title, fontsize=6, pad=2, color=SWAP_COLORS[swap])

    for ax in (ax_mt, ax_dep):
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)


# ── Layout ────────────────────────────────────────────────────────────────
# Rows = swap type; Cols = CUED-Near, CUED-Far, UNCUED-Near, UNCUED-Far
#
# Top-left  = CUED-Near  (swap=N)
# Top-right = UNCUED-Far (swap=N)
# Within each row, CUED (left pair) and UNCUED (right pair) panels are
# identical except for which field translates at tStart.

NEAR_c, FAR_c = NEAR, FAR   # depth of delayed-onset field

COL_DEFS = [
    (True,  NEAR_c),   # CUED-Near
    (True,  FAR_c),    # CUED-Far
    (False, NEAR_c),   # UNCUED-Near
    (False, FAR_c),    # UNCUED-Far
]
ROW_SWAPS = ['N', 'C', 'Z', 'CZ']

COL_HEADERS = [
    'CUED\nDelayed=Near+Red\nAlways=Far+Green',
    'CUED\nDelayed=Far+Red\nAlways=Near+Green',
    'UNCUED\nDelayed=Near+Red\nAlways=Far+Green',
    'UNCUED\nDelayed=Far+Red\nAlways=Near+Green',
]
ROW_LABELS = {
    'N':  'N\nNo swap',
    'C':  'C\nColor swap\nat tStart',
    'Z':  'Z\nDepth swap\nat tStart',
    'CZ': 'CZ\nColor+Depth\nat tStart',
}

fig = plt.figure(figsize=(20, 14))
fig.patch.set_facecolor('white')
fig.suptitle(
    'Exp_DecoupledDots_005m — Trajectories\n'
    'RotA  ·  Field B (delayed onset) = Red (dashed)  ·  '
    'Field A (always-on) = Green (solid)  ·  linkDepthColor=0\n'
    'Solid = Field A (always-on, CW)  ·  Dashed = Field B (delayed onset, CCW)  ·  '
    'Heavy = coherent subfield  ·  Light = noise subfield\n'
    'Motion: dot color = field color  ·  Depth: dot color = depth plane  ·  '
    'Gold band = translator depth after tStart  ·  Blue shading = translation window',
    fontsize=8.5, y=1.01, va='bottom')

outer = gridspec.GridSpec(4, 4, hspace=0.85, wspace=0.38,
                          left=0.09, right=0.99, top=0.93, bottom=0.06)

for ri, swap in enumerate(ROW_SWAPS):
    for ci, (cued, ddep) in enumerate(COL_DEFS):

        inner = gridspec.GridSpecFromSubplotSpec(
            2, 1, subplot_spec=outer[ri, ci],
            height_ratios=[3, 1.5], hspace=0.06)

        ax_mt  = fig.add_subplot(inner[0])
        ax_dep = fig.add_subplot(inner[1], sharex=ax_mt)

        mt, dep, fcol = build(swap, ddep, cued)

        dep_str  = 'Near' if ddep == NEAR else 'Far'
        cued_str = 'CUED' if cued else 'UNCUED'
        title    = f'{cued_str} · Del={dep_str} · {swap}'

        plot_panel(ax_mt, ax_dep, mt, dep, fcol, title, swap, cued, ddep)

        # Row labels (leftmost column only)
        if ci == 0:
            sc = SWAP_COLORS[swap]
            ax_mt.set_ylabel(ROW_LABELS[swap] + '\n\nMotion',
                             fontsize=6, fontweight='bold', color=sc,
                             labelpad=4)
        else:
            ax_mt.set_ylabel('Motion', fontsize=5)
        ax_dep.set_ylabel('Depth', fontsize=5)

        # Column headers (top row only)
        if ri == 0:
            cc = C_CUED if cued else C_UNCUED
            ax_mt.set_title(COL_HEADERS[ci] + '\n' + title,
                            fontsize=6.5, fontweight='bold', pad=14, color=cc)

# ── Legend ────────────────────────────────────────────────────────────────
legend_handles = [
    Line2D([0],[0], color='#228B22', ls='-',  lw=1.8, label='S0  Field A · coh  (solid heavy, default Green)'),
    Line2D([0],[0], color='#228B22', ls='-',  lw=0.9, label='S1  Field A · noise (solid light)'),
    Line2D([0],[0], color='#CC3333', ls='--', lw=1.8, label='S2  Field B · coh  (dashed heavy, default Red)'),
    Line2D([0],[0], color='#CC3333', ls='--', lw=0.9, label='S3  Field B · noise (dashed light)'),
    Line2D([0],[0], color='gray',    ls='-',  lw=1.2,
           label='After C/CZ swap: Field A→Red solid, Field B→Green dashed'),
    mpatches.Patch(facecolor='gold',      alpha=0.4, edgecolor='#999', label='Translator depth plane'),
    mpatches.Patch(facecolor='steelblue', alpha=0.2, edgecolor='none', label='Translation window'),
    Line2D([0],[0], color='#CCCCCC', lw=0.8, ls=':', label='Field B onset'),
    Line2D([0],[0], color='#6688AA', lw=0.8, ls='--', label='tStart'),
]

fig.legend(handles=legend_handles, loc='lower center', ncol=3,
           fontsize=7, frameon=True, framealpha=0.95,
           edgecolor='#CCC', bbox_to_anchor=(0.5, -0.05))

os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
fig.savefig(OUT_PATH, dpi=150, bbox_inches='tight', facecolor='white')
print('Saved: {}'.format(OUT_PATH))
