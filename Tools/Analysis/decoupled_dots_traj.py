#!/usr/bin/env python3
"""
Trajectory figure for Exp_DecoupledDots_005m.

Fixed:  RotA (Field A=CW, Field B=CCW)
        DelayedColor=Red  → Field B=Red, Field A=Green
        linkDepthColor=0  → color follows FIELD, not depth plane;
                            depth and color change independently at tStart

Varying:
  Rows  : CUED-Near, CUED-Far, UNCUED-Near, UNCUED-Far
  Cols  : N (no swap), C (color swap), Z (depth swap), CZ (both)

Each panel: motion track (top) + depth track (bottom).
Dot color = current field color (changes at tStart for C and CZ swaps).

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

# ── Timing (frames at 75 Hz) ──────────────────────────────────────────────────
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
FIELD_COLOR = {F_RED: '#CC3333', F_GRN: '#228B22', 0: '#DDDDDD'}

# Depth track uses different shade to distinguish Near/Far visually
DEPTH_COLOR = {NEAR: '#AA2222', FAR: '#116611'}

# Marker specs per subfield: (marker, size, filled)
SF_SPEC = {
    0: ('o', 20, True),   # S0  coh  Field A
    1: ('s', 36, False),  # S1 noise Field A
    2: ('^', 22, True),   # S2  coh  Field B
    3: ('D', 40, False),  # S3 noise Field B
}

SAMPLE_STEP = max(1, TOTAL // 20)

C_CUED   = '#1a3a8b'
C_UNCUED = '#884400'
SWAP_COLORS = {'N': '#444444', 'C': '#CC6600', 'Z': '#116688', 'CZ': '#553388'}


def build(swap, delayed_depth, cued):
    """
    swap          : 'N', 'C', 'Z', 'CZ'
    delayed_depth : NEAR or FAR  — depth of Field B (delayed onset)
    cued          : True = S2 translates (Field B); False = S0 translates (Field A)

    Returns mt[TOTAL,4], depth[TOTAL,4], field_color[TOTAL,4]
    """
    a_dep = FAR  if delayed_depth == NEAR else NEAR
    b_dep = delayed_depth

    color_swap = swap in ('C', 'CZ')
    depth_swap = swap in ('Z', 'CZ')

    # Default field colors: Field A=Green, Field B=Red
    A_COL_DEFAULT = F_GRN
    B_COL_DEFAULT = F_RED

    mt    = np.zeros((TOTAL, 4), dtype=int)
    dep   = np.zeros((TOTAL, 4), dtype=int)
    fcol  = np.zeros((TOTAL, 4), dtype=int)

    for f in range(TOTAL):
        ao  = f >= ONSET
        as_ = f >= T_START
        tr  = T_START <= f < T_END

        # Field colors (swap at tStart if colorSwap)
        a_col = B_COL_DEFAULT if (color_swap and as_) else A_COL_DEFAULT
        b_col = A_COL_DEFAULT if (color_swap and as_) else B_COL_DEFAULT

        # Depth planes (swap at tStart if depthSwap)
        a_d = b_dep if (depth_swap and as_) else a_dep
        b_d = a_dep if (depth_swap and as_) else b_dep

        # Motions (RotA: Field A=CW, Field B=CCW; translation during tr)
        if not as_:
            m = [CW, CW,
                 CCW if ao else 0,
                 CCW if ao else 0]
        elif tr:
            if cued:   # S2=Linear, S3=NonCoh; S0/S1 keep rotating
                m = [CW, CW, LINEAR, NONCOH]
            else:      # S0=Linear, S1=NonCoh; S2/S3 keep rotating
                m = [LINEAR, NONCOH, CCW, CCW]
        else:          # post-tStart, not translating
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
    samples = list(range(0, TOTAL, SAMPLE_STEP))
    if samples[-1] != TOTAL - 1:
        samples.append(TOTAL - 1)

    for si in range(4):
        mk, ms, filled = SF_SPEC[si]

        # Scatter dots
        for f in samples:
            c_code = fcol[f, si]
            if c_code == 0:
                continue
            mv = mt[f, si]
            dv = dep[f, si]
            if mv == 0 or dv == 0:
                continue
            col = FIELD_COLOR[c_code]
            dep_col = DEPTH_COLOR[dv]

            # Motion panel: use field color
            if filled:
                ax_mt.scatter(f, mv, marker=mk, c=col,
                              edgecolors='none', s=ms, zorder=4)
            else:
                ax_mt.scatter(f, mv, marker=mk, facecolors='none',
                              edgecolors=col, s=ms, linewidths=1.2, zorder=4)

            # Depth panel: use depth color
            if filled:
                ax_dep.scatter(f, dv, marker=mk, c=dep_col,
                               edgecolors='none', s=ms, zorder=4)
            else:
                ax_dep.scatter(f, dv, marker=mk, facecolors='none',
                               edgecolors=dep_col, s=ms, linewidths=1.2, zorder=4)

        # Connecting lines
        for ax, arr, use_depth_col in [
                (ax_mt,  mt,  False),
                (ax_dep, dep, True)]:
            prev_f = prev_v = None
            for f in range(TOTAL):
                v = arr[f, si]
                if v == 0:
                    prev_f = prev_v = None
                    continue
                if use_depth_col:
                    col = DEPTH_COLOR.get(dep[f, si], '#AAAAAA')
                else:
                    col = FIELD_COLOR.get(fcol[f, si], '#AAAAAA')
                if prev_f is not None:
                    ax.plot([prev_f, f], [prev_v, v],
                            color=col, lw=0.5, alpha=0.35, zorder=2)
                prev_f, prev_v = f, v

    # Phase shading / markers
    for ax in (ax_mt, ax_dep):
        ax.axvspan(T_START, T_END, alpha=0.12, color='steelblue', zorder=1)
        ax.axvline(ONSET,   color='#BBBBBB', lw=0.8, ls=':', zorder=2)
        ax.axvline(T_START, color='#6688AA', lw=0.9, ls='--', zorder=2)
        ax.axvline(T_END,   color='#6688AA', lw=0.9, ls='--', zorder=2)

    # Highlight translation depth plane
    # Translator depth after swap
    if cued:   # S2 translates; S2 is Field B
        trans_dep_after = (FAR if (swap in ('Z','CZ')) else delayed_depth) \
                          if delayed_depth == NEAR else \
                          (NEAR if (swap in ('Z','CZ')) else delayed_depth)
    else:      # S0 translates; S0 is Field A
        a_dep_default = FAR if delayed_depth == NEAR else NEAR
        trans_dep_after = (delayed_depth if (swap in ('Z','CZ')) else a_dep_default)

    ax_dep.axhspan(trans_dep_after - 0.42, trans_dep_after + 0.42,
                   alpha=0.18, color='gold', zorder=0)

    # Axes formatting — motion
    ax_mt.set_yticks([CW, LINEAR, NONCOH, CCW])
    ax_mt.set_yticklabels(['CW', 'T(c)', 'T(n)', 'CCW'], fontsize=5)
    ax_mt.set_ylim(0.4, 4.6)
    ax_mt.tick_params(axis='x', labelbottom=False)
    ax_mt.tick_params(axis='y', labelsize=5, length=2)
    ax_mt.set_xlim(-2, TOTAL + 1)

    # Axes formatting — depth
    ax_dep.set_yticks([NEAR, FAR])
    ax_dep.set_yticklabels(['Near', 'Far'], fontsize=5)
    ax_dep.set_ylim(0.4, 2.6)
    ax_dep.set_xlabel('Frame', fontsize=5)
    ax_dep.tick_params(axis='both', labelsize=5, length=2)
    ax_dep.set_xlim(-2, TOTAL + 1)

    # Panel title
    sc = SWAP_COLORS[swap]
    ax_mt.set_title(title, fontsize=6.5, fontweight='bold', pad=2, color=sc)

    for ax in (ax_mt, ax_dep):
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)


# ── Layout ────────────────────────────────────────────────────────────────────
# rows: CUED-Near, CUED-Far, UNCUED-Near, UNCUED-Far
# cols: N, C, Z, CZ
CUED_NEAR   = (True,  NEAR)
CUED_FAR    = (True,  FAR)
UNCUED_NEAR = (False, NEAR)
UNCUED_FAR  = (False, FAR)

ROW_DEFS = [CUED_NEAR, CUED_FAR, UNCUED_NEAR, UNCUED_FAR]
COL_SWAPS = ['N', 'C', 'Z', 'CZ']

ROW_LABELS = [
    'CUED\nDelayed=Near+Red\nAlways=Far+Green',
    'CUED\nDelayed=Far+Red\nAlways=Near+Green',
    'UNCUED\nDelayed=Near+Red\nAlways=Far+Green',
    'UNCUED\nDelayed=Far+Red\nAlways=Near+Green',
]
COL_LABELS = [
    'N — No swap',
    'C — Color swap\n(field colors swap at tStart)',
    'Z — Depth swap\n(field depth planes swap at tStart)',
    'CZ — Color + Depth\n(both swap at tStart)',
]

fig = plt.figure(figsize=(22, 14))
fig.patch.set_facecolor('white')
fig.suptitle(
    'Exp_DecoupledDots_005m — Trajectories\n'
    'RotA  ·  Field B (delayed onset) = Red  ·  Field A (always) = Green  ·  '
    'linkDepthColor=0: color follows field, depth and color change independently\n'
    'Motion panel: dot color = field color  ·  '
    'Depth panel: dot color = depth plane (dark red=Near, dark green=Far)  ·  '
    'Gold band = translator depth plane after tStart',
    fontsize=9, y=1.005, va='bottom')

outer = gridspec.GridSpec(4, 4, hspace=0.80, wspace=0.35,
                          left=0.08, right=0.99, top=0.94, bottom=0.05)

for ri, (cued, ddep) in enumerate(ROW_DEFS):
    for ci, swap in enumerate(COL_SWAPS):

        inner = gridspec.GridSpecFromSubplotSpec(
            2, 1, subplot_spec=outer[ri, ci],
            height_ratios=[3, 1.5], hspace=0.06)

        ax_mt  = fig.add_subplot(inner[0])
        ax_dep = fig.add_subplot(inner[1], sharex=ax_mt)

        mt, dep, fcol = build(swap, ddep, cued)

        dep_str   = 'Near' if ddep == NEAR else 'Far'
        cued_str  = 'CUED' if cued else 'UNCUED'
        title     = f'{cued_str} · Del={dep_str} · {swap}'
        plot_panel(ax_mt, ax_dep, mt, dep, fcol, title, swap, cued, ddep)

        # Row labels (leftmost column)
        if ci == 0:
            rc = C_CUED if cued else C_UNCUED
            ax_mt.set_ylabel(ROW_LABELS[ri] + '\n\nMotion',
                             fontsize=6, fontweight='bold', color=rc)
        else:
            ax_mt.set_ylabel('Motion', fontsize=5)
        ax_dep.set_ylabel('Depth', fontsize=5)

        # Column headers (top row)
        if ri == 0:
            ax_mt.set_title(COL_LABELS[ci] + '\n' + title,
                            fontsize=6.5, fontweight='bold', pad=14,
                            color=SWAP_COLORS[swap])

# ── Legend ────────────────────────────────────────────────────────────────────
legend_handles = [
    Line2D([0],[0], marker='o', color='w', markerfacecolor='#CC3333',
           markersize=7, ls='None', label='S0● coh  Field A (default: Green; Red after C/CZ)'),
    Line2D([0],[0], marker='s', color='w', markeredgecolor='#CC3333',
           markerfacecolor='none', markersize=7, markeredgewidth=1.3,
           ls='None', label='S1□ noise Field A'),
    Line2D([0],[0], marker='^', color='w', markerfacecolor='#228B22',
           markersize=7, ls='None', label='S2▲ coh  Field B (default: Red; Green after C/CZ)'),
    Line2D([0],[0], marker='D', color='w', markeredgecolor='#228B22',
           markerfacecolor='none', markersize=7, markeredgewidth=1.3,
           ls='None', label='S3◇ noise Field B'),
    mpatches.Patch(facecolor='gold', alpha=0.4, edgecolor='#999',
                   label='Translator depth plane (gold)'),
    mpatches.Patch(facecolor='steelblue', alpha=0.2, edgecolor='none',
                   label='Translation window'),
    Line2D([0],[0], color='#BBBBBB', lw=1, ls=':', label='Field B onset'),
    Line2D([0],[0], color='#6688AA', lw=1, ls='--', label='tStart (swap + translation)'),
]

fig.legend(handles=legend_handles, loc='lower center', ncol=4,
           fontsize=7, frameon=True, framealpha=0.95,
           edgecolor='#CCC', bbox_to_anchor=(0.5, -0.04))

os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
fig.savefig(OUT_PATH, dpi=150, bbox_inches='tight', facecolor='white')
print('Saved: {}'.format(OUT_PATH))
