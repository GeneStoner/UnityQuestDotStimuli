#!/usr/bin/env python3
"""
All flat (no-depth, no-swap) conditions — 4 columns × 2 rows.

Columns: Rot0×DelRed | Rot0×DelGreen | Rot1×DelRed | Rot1×DelGreen
Rows:    CUED (top)  |  UNCUED (bottom)

Line colors reflect actual dot colors (DelayedColor drives B's color; A gets the other).
Line style: solid = Field A (non-delayed), dashed = Field B (delayed).
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.lines as mlines

# ── Timing (normalized, 1530 ms total) ───────────────────────────────────────
T_A   = 0.000   # Field A onset
T_B   = 0.490   # Field B (delayed) onset   750/1530
T_S   = 0.686   # Translation start         1050/1530
T_E   = 0.739   # Translation end           1130/1530
T_TOT = 1.000

CW    = 2.0
TRANS = 1.0
CCW   = 0.0

C_RED   = '#CC3333'
C_GREEN = '#228B22'
C_TRANS = '#CCCCCC'
C_FRAME = '#333333'
LW = 2.0


# ── Trajectory builder ────────────────────────────────────────────────────────

def trajs(is_cued, is_rot0):
    """
    Return (tA, vA, tB, vB) motion trajectories.
    Rot0: A=CW, B=CCW.  Rot1: A=CCW, B=CW.  No motion swap.
    """
    a_rot = CW  if is_rot0 else CCW
    b_rot = CCW if is_rot0 else CW

    if is_cued:
        # B translates
        tA = [T_A, T_TOT]
        vA = [a_rot, a_rot]
        tB = [T_B, T_S, T_S, T_E, T_E, T_TOT]
        vB = [b_rot, b_rot, TRANS, TRANS, b_rot, b_rot]
    else:
        # A translates
        tA = [T_A, T_S, T_S, T_E, T_E, T_TOT]
        vA = [a_rot, a_rot, TRANS, TRANS, a_rot, a_rot]
        tB = [T_B, T_TOT]
        vB = [b_rot, b_rot]

    return np.array(tA), np.array(vA), np.array(tB), np.array(vB)


# ── Axes setup ────────────────────────────────────────────────────────────────

def setup_ax(ax, show_phase_labels=False):
    ax.set_xlim(T_A - 0.01, T_TOT + 0.01)
    ax.set_ylim(-0.45, 2.65)
    ax.set_xticks([])
    ax.set_yticks([CCW, TRANS, CW])
    ax.set_yticklabels(['CCW', 'TRANS', 'CW'], fontsize=7.5)
    ax.tick_params(axis='y', length=2, pad=2)
    # Translation window
    ax.axvspan(T_S, T_E, color=C_TRANS, alpha=0.7, zorder=1)
    # Delayed onset divider
    ax.axvline(T_B, color='#AAAAAA', lw=0.9, ls='--', zorder=2)
    # Rectangle frame
    for spine in ax.spines.values():
        spine.set_visible(True)
        spine.set_linewidth(0.8)
        spine.set_edgecolor(C_FRAME)
    if show_phase_labels:
        ax.text((T_A + T_B) / 2, 2.58, 'A only', ha='center', va='top',
                fontsize=6.5, color='#888888', style='italic')
        ax.text((T_B + T_S) / 2, 2.58, 'A + B', ha='center', va='top',
                fontsize=6.5, color='#888888', style='italic')
        ax.text((T_S + T_E) / 2, 2.58, 'T', ha='center', va='top',
                fontsize=6.5, color='#666666', style='italic')


def draw(ax, is_cued, is_rot0, c_a, c_b):
    tA, vA, tB, vB = trajs(is_cued, is_rot0)
    ax.plot(tA, vA, color=c_a, lw=LW, ls='-',  solid_capstyle='round', zorder=3)
    ax.plot(tB, vB, color=c_b, lw=LW, ls='--', dashes=(6, 3), zorder=3)


# ── Column definitions ────────────────────────────────────────────────────────
# (is_rot0, delayed_color_label, c_A, c_B)
# c_A = actual color of Field A (non-delayed); c_B = actual color of Field B (delayed)
# Each panel defined independently: (row, col, is_cued, is_rot0, c_a, c_b)
# Grouping principle: within each column, the SAME color+rotation translates.
# CUED = translating field is delayed (dotted). UNCUED = translating field is non-delayed (solid).
#
# Col 0: green CW translates (↓)  — CUED: Rot1/DelGreen  UNCUED: Rot0/DelRed
# Col 1: red CW translates   (↓)  — CUED: Rot1/DelRed    UNCUED: Rot0/DelGreen
# Col 2: green CCW translates (↑) — CUED: Rot0/DelGreen  UNCUED: Rot1/DelRed
# Col 3: red CCW translates   (↑) — CUED: Rot0/DelRed    UNCUED: Rot1/DelGreen

panels = [
    # row, col, is_cued, is_rot0, c_A,     c_B
    # Col 0 — green CW translates
    (0, 0, True,  False, C_RED,   C_GREEN),  # CUED:   Rot1, B=green dotted CW ↓
    (1, 0, False, True,  C_GREEN, C_RED),    # UNCUED: Rot0, A=green solid  CW ↓
    # Col 1 — red CW translates
    (0, 1, True,  False, C_GREEN, C_RED),    # CUED:   Rot1, B=red dotted CW ↓
    (1, 1, False, True,  C_RED,   C_GREEN),  # UNCUED: Rot0, A=red solid  CW ↓
    # Col 2 — green CCW translates
    (0, 2, True,  True,  C_RED,   C_GREEN),  # CUED:   Rot0, B=green dotted CCW ↑
    (1, 2, False, False, C_GREEN, C_RED),    # UNCUED: Rot1, A=green solid  CCW ↑
    # Col 3 — red CCW translates
    (0, 3, True,  True,  C_GREEN, C_RED),    # CUED:   Rot0, B=red dotted CCW ↑
    (1, 3, False, False, C_RED,   C_GREEN),  # UNCUED: Rot1, A=red solid  CCW ↑
]

col_titles = [
    'Green trans. (CW→↓)',
    'Red trans. (CW→↓)',
    'Green trans. (CCW→↑)',
    'Red trans. (CCW→↑)',
]

# ── Figure ────────────────────────────────────────────────────────────────────
fig = plt.figure(figsize=(12, 5.5))
fig.patch.set_facecolor('white')

gs = gridspec.GridSpec(2, 4, figure=fig,
                       hspace=0.30, wspace=0.28,
                       top=0.88, bottom=0.13, left=0.07, right=0.98)

for row_idx, col_idx, is_cued, is_rot0, c_a, c_b in panels:
    ax = fig.add_subplot(gs[row_idx, col_idx])
    setup_ax(ax, show_phase_labels=(row_idx == 0 and col_idx == 0))
    draw(ax, is_cued, is_rot0, c_a, c_b)

    if row_idx == 0:
        ax.set_title(col_titles[col_idx], fontsize=9, fontweight='bold', pad=5)
    if col_idx == 0:
        ax.set_ylabel('CUED' if is_cued else 'UNCUED',
                      fontsize=10, fontweight='bold', labelpad=5)

# ── Legend ────────────────────────────────────────────────────────────────────
leg_handles = [
    mlines.Line2D([], [], color=C_RED,   lw=2, ls='-',  label='Field A non-delayed (solid) — red dots'),
    mlines.Line2D([], [], color=C_GREEN, lw=2, ls='-',  label='Field A non-delayed (solid) — green dots'),
    mlines.Line2D([], [], color=C_RED,   lw=2, ls='--', dashes=(6,3), label='Field B delayed (dashed) — red dots'),
    mlines.Line2D([], [], color=C_GREEN, lw=2, ls='--', dashes=(6,3), label='Field B delayed (dashed) — green dots'),
]
fig.legend(handles=leg_handles, loc='lower center', ncol=4,
           fontsize=7.5, frameon=True, framealpha=0.9,
           bbox_to_anchor=(0.52, 0.01))

fig.suptitle('Flat (No Depth) — All Permutations, No Swap', fontsize=12, fontweight='bold', y=0.97)

out_path = ('/Users/genestoner1/Projects/ObjectBasedAttention/VRDots/'
            'Agents/Figures/flat_permutations.png')
fig.savefig(out_path, dpi=150, bbox_inches='tight', facecolor='white')
print(f"Saved: {out_path}")
