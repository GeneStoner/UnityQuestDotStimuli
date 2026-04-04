#!/usr/bin/env python3
"""
depth_color_linked_traj.py
Factor-labeled trajectory figure for DepthColorLinked_005m (ZdCoh / ZdNoi only).

8 panels: ZdCoh / ZdNoi  ×  CUED Near / UNCUED Near / CUED Far / UNCUED Far
Each panel: motion track (top) + depth track (bottom).
Dot color = depth-plane color at each frame: Near=Red, Far=Green.

Factor labels (new framing):
  Dot Cueing  ✓/✗  — does the delayed-onset field translate?
  Depth Cueing ✓/✗ — does translation occur at the depth where cued field appeared?
                      YES = CUED+ZdNoi  OR  UNCUED+ZdCoh
                      NO  = CUED+ZdCoh  OR  UNCUED+ZdNoi

Output: Agents/Figures/depth_color_linked_traj.png
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
    '~/Projects/ObjectBasedAttention/VRDots/Agents/Figures/depth_color_linked_traj.png')

# ── Timing (frames at 75 Hz) ───────────────────────────────────────────────────
ONSET   = 56    # Field B onset
T_START = 78    # swap + translation start
T_END   = 84    # translation end
TOTAL   = 114

# Motion type codes
CW = 1; TRANS_COH = 2; TRANS_NOI = 3; CCW = 4

# Depth codes
NEAR = 1; FAR = 2

# Colors
C_NEAR = '#CC3333'   # Red  — Near plane
C_FAR  = '#228B22'   # Green — Far plane
C_TRAN = '#BBBBBB'   # translation window
C_DOT_Y = '#1a6b1a'; C_DOT_N = '#666666'
C_DEP_Y = '#1a3a8b'; C_DEP_N = '#aa2222'
C_ZDCOH = '#883300'; C_ZDNOI = '#226622'

DEPTH_COLOR = {NEAR: C_NEAR, FAR: C_FAR, 0: '#DDDDDD'}

# Marker specs: (marker, size, filled)
SF_SPEC = {
    0: ('o', 18, True),    # S0 coh
    1: ('s', 32, False),   # S1 noise
    2: ('^', 20, True),    # S2 coh
    3: ('D', 36, False),   # S3 noise
}

SAMPLE_STEP = max(1, TOTAL // 18)


def build(swap, delayed_depth, cued):
    """
    Build per-frame motion and depth arrays.
    swap         : 'ZdA' (ZdCoh) or 'ZdB' (ZdNoi)
    delayed_depth: NEAR or FAR — depth of Field B (the delayed/cued field)
    cued         : True → Field B translates; False → Field A translates
    """
    a_dep = FAR if delayed_depth == NEAR else NEAR
    b_dep = delayed_depth

    mt    = np.zeros((TOTAL, 4), dtype=int)
    depth = np.zeros((TOTAL, 4), dtype=int)

    for f in range(TOTAL):
        ao = f >= ONSET      # Field B has appeared
        as_ = f >= T_START   # swap has occurred
        tr  = T_START <= f < T_END  # translation window

        # Default depths (pre-swap)
        d = [a_dep, a_dep,
             b_dep if ao else 0, b_dep if ao else 0]
        # Default motions
        m = [CW, CW, CCW if ao else 0, CCW if ao else 0]

        if as_:
            if swap == 'ZdA':
                # Coherent subfields S0 & S2 swap planes
                d = [b_dep, a_dep, a_dep if ao else 0, b_dep if ao else 0]
                if tr:
                    m = ([CW, TRANS_NOI, TRANS_COH, CW] if cued
                         else [TRANS_COH, CCW, CCW, TRANS_NOI])
                else:
                    m = [CW, CCW, CCW if ao else 0, CW if ao else 0]
            else:  # ZdB — noise subfields S1 & S3 swap planes
                d = [a_dep, b_dep, b_dep if ao else 0, a_dep if ao else 0]
                if tr:
                    m = ([CW, TRANS_NOI, TRANS_COH, CW] if cued
                         else [TRANS_COH, CCW, CCW, TRANS_NOI])
                else:
                    m = [CW, CCW, CCW if ao else 0, CW if ao else 0]

        mt[f]    = m
        depth[f] = d

    return mt, depth


def factors(swap, delayed_depth, cued):
    """
    Dot Cueing  ✓ = cued (delayed field translates)
    Depth Cueing ✓ = translation occurs at DFD during translation window
      CUED+ZdNoi: translator (S2, cued) stays at b_dep = DFD → YES
      CUED+ZdCoh: translator (S2) swaps from b_dep to a_dep at T_START → NO
      UNCUED+ZdCoh: translator (S0) swaps from a_dep to b_dep at T_START → YES
      UNCUED+ZdNoi: translator (S0) stays at a_dep ≠ b_dep → NO
    """
    dot_cue  = cued
    dep_cue  = dot_cue != (swap == 'ZdA')   # XNOR(cued, ZdB)
    trans_dep = delayed_depth if dep_cue else (FAR if delayed_depth == NEAR else NEAR)
    return dot_cue, dep_cue, trans_dep


def plot_panel(ax_mt, ax_dep, mt, depth, dot_cue, dep_cue, trans_dep, title, swap):
    """Draw one panel with color-coded dot trajectories."""

    samples = list(range(0, TOTAL, SAMPLE_STEP))
    if samples[-1] != TOTAL - 1:
        samples.append(TOTAL - 1)

    for si in range(4):
        mk, ms, filled = SF_SPEC[si]

        # Split samples into pre-swap and post-swap for correct coloring
        for f in samples:
            d = depth[f, si]
            if d == 0:
                continue
            col = DEPTH_COLOR[d]
            mv  = mt[f, si]
            if mv == 0:
                continue

            # Motion panel
            if filled:
                ax_mt.scatter(f, mv, marker=mk, c=col, edgecolors='none',
                              s=ms, zorder=4)
            else:
                ax_mt.scatter(f, mv, marker=mk, facecolors='none',
                              edgecolors=col, s=ms, linewidths=1.2, zorder=4)

            # Depth panel
            if filled:
                ax_dep.scatter(f, d, marker=mk, c=col, edgecolors='none',
                               s=ms, zorder=4)
            else:
                ax_dep.scatter(f, d, marker=mk, facecolors='none',
                               edgecolors=col, s=ms, linewidths=1.2, zorder=4)

        # Faint connecting line (use depth color at each segment)
        # Draw pre-swap and post-swap segments separately
        for ax, arr in [(ax_mt, mt), (ax_dep, depth)]:
            prev_f = None
            prev_v = None
            for f in range(TOTAL):
                v = arr[f, si]
                if v == 0:
                    prev_f = prev_v = None
                    continue
                d = depth[f, si]
                col = DEPTH_COLOR[d]
                if prev_f is not None and prev_v is not None:
                    # If depth changed, draw in new color
                    ax.plot([prev_f, f], [prev_v, v], color=col,
                            lw=0.5, alpha=0.4, zorder=2)
                prev_f, prev_v = f, v

    # Phase markers — both panels
    for ax in (ax_mt, ax_dep):
        ax.axvspan(T_START, T_END, alpha=0.12, color='steelblue', zorder=1)
        ax.axvline(ONSET,   color='#AAAAAA', lw=0.8, ls=':', zorder=2)
        ax.axvline(T_START, color='#6688AA', lw=0.9, ls='--', zorder=2)
        ax.axvline(T_END,   color='#6688AA', lw=0.9, ls='--', zorder=2)

    # Gold band on translating depth plane
    hi_y = FAR if trans_dep == FAR else NEAR
    ax_dep.axhspan(hi_y - 0.42, hi_y + 0.42, alpha=0.18, color='gold', zorder=0)

    # Motion axis
    ax_mt.set_yticks([CW, TRANS_COH, TRANS_NOI, CCW])
    ax_mt.set_yticklabels(['CW', 'T(c)', 'T(n)', 'CCW'], fontsize=5.5)
    ax_mt.set_ylim(0.4, 4.6)
    ax_mt.tick_params(axis='x', labelbottom=False)
    ax_mt.tick_params(axis='y', labelsize=5.5, length=2)
    ax_mt.set_xlim(-2, TOTAL + 1)

    # Depth axis
    ax_dep.set_yticks([NEAR, FAR])
    ax_dep.set_yticklabels(['Near\n(Red)', 'Far\n(Grn)'], fontsize=5)
    ax_dep.set_ylim(0.4, 2.6)
    ax_dep.set_xlabel('Frame', fontsize=5.5)
    ax_dep.tick_params(axis='both', labelsize=5.5, length=2)
    ax_dep.set_xlim(-2, TOTAL + 1)

    # Title
    ax_mt.set_title(title, fontsize=7.5, fontweight='bold', pad=2,
                    color=C_ZDCOH if swap=='ZdA' else C_ZDNOI)

    # Factor annotation
    dot_str  = 'Dot ✓' if dot_cue else 'Dot ✗'
    dep_str  = 'Depth ✓' if dep_cue else 'Depth ✗'
    dot_col  = C_DOT_Y if dot_cue else C_DOT_N
    dep_col  = C_DEP_Y if dep_cue else C_DEP_N
    # Two colored text elements via annotate trick — use twin approach
    ax_mt.text(0.28, 1.04, dot_str, transform=ax_mt.transAxes,
               ha='center', va='bottom', fontsize=6.5, fontweight='bold',
               color=dot_col,
               bbox=dict(boxstyle='round,pad=0.15', fc='white', ec=dot_col,
                         alpha=0.9, lw=0.8))
    ax_mt.text(0.72, 1.04, dep_str, transform=ax_mt.transAxes,
               ha='center', va='bottom', fontsize=6.5, fontweight='bold',
               color=dep_col,
               bbox=dict(boxstyle='round,pad=0.15', fc='white', ec=dep_col,
                         alpha=0.9, lw=0.8))

    for ax in (ax_mt, ax_dep):
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)


# ── Layout ────────────────────────────────────────────────────────────────────
# 2 rows (ZdCoh=ZdA, ZdNoi=ZdB)  ×  4 cols (CuedNear, UncuedNear, CuedFar, UncuedFar)
CONDITIONS = [
    ('ZdA', NEAR, True),   # ZdCoh CUED Near
    ('ZdA', NEAR, False),  # ZdCoh UNCUED Near
    ('ZdA', FAR,  True),   # ZdCoh CUED Far
    ('ZdA', FAR,  False),  # ZdCoh UNCUED Far
    ('ZdB', NEAR, True),   # ZdNoi CUED Near
    ('ZdB', NEAR, False),  # ZdNoi UNCUED Near
    ('ZdB', FAR,  True),   # ZdNoi CUED Far
    ('ZdB', FAR,  False),  # ZdNoi UNCUED Far
]

COL_HEADERS = [
    'CUED — Near trans.',
    'UNCUED — Near trans.',
    'CUED — Far trans.',
    'UNCUED — Far trans.',
]
ROW_HEADERS = ['ZdCoh (ZdA)\nS0+S2 swap depth+color', 'ZdNoi (ZdB)\nS1+S3 swap depth+color']

COND_TITLES = [
    'ZdCoh · CUED · Near', 'ZdCoh · UNCUED · Near',
    'ZdCoh · CUED · Far',  'ZdCoh · UNCUED · Far',
    'ZdNoi · CUED · Near', 'ZdNoi · UNCUED · Near',
    'ZdNoi · CUED · Far',  'ZdNoi · UNCUED · Far',
]

fig = plt.figure(figsize=(20, 11))
fig.patch.set_facecolor('white')

fig.suptitle(
    'DepthColorLinked_005m — Factor-Labeled Trajectories\n'
    'Near plane = Red  ·  Far plane = Green  ·  '
    'Dot color follows depth plane, changes at T\u209B for swapping subfields\n'
    'Gold band = depth plane where translation occurs  ·  '
    'Blue shade = translation window  ·  Dashed gray = Field B onset',
    fontsize=9.5, y=1.01, va='bottom')

outer = gridspec.GridSpec(2, 4, hspace=0.72, wspace=0.38,
                          left=0.07, right=0.99, top=0.91, bottom=0.04)

for idx, ((swap, ddep, cued), title) in enumerate(zip(CONDITIONS, COND_TITLES)):
    row = idx // 4
    col = idx % 4

    inner = gridspec.GridSpecFromSubplotSpec(
        2, 1, subplot_spec=outer[row, col],
        height_ratios=[3, 1.5], hspace=0.06)

    ax_mt  = fig.add_subplot(inner[0])
    ax_dep = fig.add_subplot(inner[1], sharex=ax_mt)

    mt, depth = build(swap, ddep, cued)
    dot_cue, dep_cue, trans_dep = factors(swap, ddep, cued)

    plot_panel(ax_mt, ax_dep, mt, depth, dot_cue, dep_cue, trans_dep, title, swap)

    # Row labels (leftmost column only)
    if col == 0:
        ax_mt.set_ylabel(ROW_HEADERS[row] + '\n\nMotion', fontsize=7,
                         fontweight='bold',
                         color=C_ZDCOH if swap=='ZdA' else C_ZDNOI)
    else:
        ax_mt.set_ylabel('Motion', fontsize=5.5)
    ax_dep.set_ylabel('Depth', fontsize=5.5)

    # Column headers (top row only)
    if row == 0:
        ax_mt.set_title(COL_HEADERS[col] + '\n' + title,
                        fontsize=7.5, fontweight='bold', pad=14,
                        color=C_ZDCOH if swap=='ZdA' else C_ZDNOI)

# ── Legend ────────────────────────────────────────────────────────────────────
legend_handles = [
    Line2D([0],[0], marker='o', color='w', markerfacecolor=C_NEAR,
           markersize=7, ls='None', label='S0● coh  (Near=Red pre-swap)'),
    Line2D([0],[0], marker='s', color='w', markeredgecolor=C_NEAR,
           markerfacecolor='none', markersize=7, markeredgewidth=1.3,
           ls='None', label='S1□ noise (Near=Red pre-swap)'),
    Line2D([0],[0], marker='^', color='w', markerfacecolor=C_FAR,
           markersize=7, ls='None', label='S2▲ coh  (Far=Green pre-swap)'),
    Line2D([0],[0], marker='D', color='w', markeredgecolor=C_FAR,
           markerfacecolor='none', markersize=7, markeredgewidth=1.3,
           ls='None', label='S3◇ noise (Far=Green pre-swap)'),
    mpatches.Patch(facecolor='gold', alpha=0.4, edgecolor='#999',
                   label='Translation depth plane'),
    mpatches.Patch(facecolor='steelblue', alpha=0.2, edgecolor='none',
                   label='Translation window'),
    mpatches.Patch(facecolor='white', edgecolor=C_DOT_Y, lw=1.2,
                   label='Dot Cueing ✓'),
    mpatches.Patch(facecolor='white', edgecolor=C_DOT_N, lw=1.2,
                   label='Dot Cueing ✗'),
    mpatches.Patch(facecolor='white', edgecolor=C_DEP_Y, lw=1.2,
                   label='Depth Cueing ✓'),
    mpatches.Patch(facecolor='white', edgecolor=C_DEP_N, lw=1.2,
                   label='Depth Cueing ✗'),
]

fig.legend(handles=legend_handles, loc='lower center', ncol=5,
           fontsize=7.5, frameon=True, framealpha=0.95,
           edgecolor='#CCC', bbox_to_anchor=(0.5, -0.03))

os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
fig.savefig(OUT_PATH, dpi=150, bbox_inches='tight', facecolor='white')
print('Saved: {}'.format(OUT_PATH))
