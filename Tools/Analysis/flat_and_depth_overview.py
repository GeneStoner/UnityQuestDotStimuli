#!/usr/bin/env python3
"""
Feature trajectory overview figure.

Top section (flat, no depth):
  CUED / UNCUED  ×  No-motion-swap / Motion-swap  (Fig 4 A–D from Stoner & Blanc 2010)

Bottom section (depth, no swap):
  CUED / UNCUED  ×  Near translation / Far translation
  (using translating-field-depth labeling — user's preferred convention)

Emphasis: pre-translation period (shaded gold) shows the onset-history asymmetry
that defines "dot cueing" — which field has the shorter rotation history.
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.lines as mlines

# ── Timing (normalized to total trial duration = 1530 ms) ─────────────────────
#   Delayed onset:    750 ms  → T_B = 750/1530
#   Pre-translation:  300 ms  → T_S = 1050/1530
#   Translation:       80 ms  → T_E = 1130/1530
#   Post-translation: 400 ms  → T_TOT = 1.0
T_A   = 0.000   # Field A onset (non-delayed)
T_B   = 0.490   # Field B onset (delayed)
T_S   = 0.686   # Translation start
T_E   = 0.739   # Translation end
T_TOT = 1.000

# ── Motion levels ─────────────────────────────────────────────────────────────
CW    = 2.0
TRANS = 1.0
CCW   = 0.0

# ── Depth levels (for depth-track axes) ───────────────────────────────────────
FAR  = 1.0
NEAR = 0.0

# ── Colors ────────────────────────────────────────────────────────────────────
C_RED    = '#CC3333'
C_GREEN  = '#228B22'
C_TRANS  = '#CCCCCC'   # translation window
C_FRAME  = '#333333'   # panel border
LW = 2.0
LW_DEPTH = 1.8


# ── Trajectory builders ───────────────────────────────────────────────────────

def motion_trajs(is_cued, is_motion_swap):
    """
    Return (t_A, v_A, t_B, v_B) — time/value arrays for Field A (red, non-delayed)
    and Field B (green, delayed).  Field B absent before T_B.
    """
    if is_cued:
        # Field B (green) translates
        if is_motion_swap:
            # A: CCW → jumps CW at T_S
            tA = [T_A, T_S, T_S, T_TOT];  vA = [CCW, CCW, CW, CW]
            # B: CW → TRANS → CCW (new rotation = A's old direction)
            tB = [T_B, T_S, T_S, T_E, T_E, T_TOT]
            vB = [CW,  CW,  TRANS, TRANS, CCW, CCW]
        else:
            tA = [T_A, T_TOT];  vA = [CCW, CCW]
            tB = [T_B, T_S, T_S, T_E, T_E, T_TOT]
            vB = [CW,  CW,  TRANS, TRANS, CW, CW]
    else:
        # Field A (red) translates
        if is_motion_swap:
            tA = [T_A, T_S, T_S, T_E, T_E, T_TOT]
            vA = [CCW, CCW, TRANS, TRANS, CW, CW]
            # B: CW → jumps CCW at T_S
            tB = [T_B, T_S, T_S, T_TOT];  vB = [CW, CW, CCW, CCW]
        else:
            tA = [T_A, T_S, T_S, T_E, T_E, T_TOT]
            vA = [CCW, CCW, TRANS, TRANS, CCW, CCW]
            tB = [T_B, T_TOT];  vB = [CW, CW]

    return (np.array(tA), np.array(vA),
            np.array(tB), np.array(vB))


# ── Axes decoration ───────────────────────────────────────────────────────────

def _common_bg(ax, ylim):
    """Shared background: translation window, onset divider, framed border."""
    ax.set_xlim(T_A - 0.01, T_TOT + 0.01)
    ax.set_ylim(*ylim)
    ax.set_xticks([])
    ax.axvspan(T_S, T_E, color=C_TRANS, alpha=0.7, zorder=1)   # translation window
    ax.axvline(T_B, color='#BBBBBB', lw=0.9, ls='--', zorder=2)  # delayed onset
    # Rectangle frame
    for spine in ax.spines.values():
        spine.set_visible(True)
        spine.set_linewidth(0.8)
        spine.set_edgecolor(C_FRAME)


def setup_motion_ax(ax, show_phase_labels=False):
    """Format a motion-trajectory axes (CW/TRANS/CCW)."""
    _common_bg(ax, ylim=(-0.4, 2.7))
    ax.set_yticks([CCW, TRANS, CW])
    ax.set_yticklabels(['CCW', 'TRANS', 'CW'], fontsize=7.5)
    ax.tick_params(axis='y', length=2, pad=2)
    if show_phase_labels:
        top = 2.62
        ax.text((T_A + T_B) / 2, top, 'A only\n(cue)', ha='center', va='top',
                fontsize=6.5, color='#666666', style='italic')
        ax.text((T_B + T_S) / 2, top, 'A + B', ha='center', va='top',
                fontsize=6.5, color='#666666', style='italic')
        ax.text((T_S + T_E) / 2, top, 'T', ha='center', va='top',
                fontsize=6.5, color='#555555', style='italic')


def setup_depth_ax(ax):
    """Format a depth-track axes (Near/Far)."""
    _common_bg(ax, ylim=(-0.5, 1.5))
    ax.set_yticks([NEAR, FAR])
    ax.set_yticklabels(['Near', 'Far'], fontsize=7.5)
    ax.tick_params(axis='y', length=2, pad=2)
    # label the y-axis
    ax.set_ylabel('Depth', fontsize=7, labelpad=2, color='#555555')


def draw_motion(ax, is_cued, is_motion_swap):
    tA, vA, tB, vB = motion_trajs(is_cued, is_motion_swap)
    ax.plot(tA, vA, color=C_RED,   lw=LW, ls='-',
            solid_capstyle='round', zorder=3)
    ax.plot(tB, vB, color=C_GREEN, lw=LW, ls='--', dashes=(6, 3), zorder=3)


def motion_trajs_rot(is_cued, is_rot0):
    """
    Build motion trajectories for Rot0 (A=CW, B=CCW) or Rot1 (A=CCW, B=CW).
    No motion swap. Field B absent before T_B.
    """
    a_rot = CW  if is_rot0 else CCW
    b_rot = CCW if is_rot0 else CW

    if is_cued:
        # B translates
        tA = [T_A, T_TOT];  vA = [a_rot, a_rot]
        tB = [T_B, T_S, T_S, T_E, T_E, T_TOT]
        vB = [b_rot, b_rot, TRANS, TRANS, b_rot, b_rot]
    else:
        # A translates
        tA = [T_A, T_S, T_S, T_E, T_E, T_TOT]
        vA = [a_rot, a_rot, TRANS, TRANS, a_rot, a_rot]
        tB = [T_B, T_TOT];  vB = [b_rot, b_rot]

    return np.array(tA), np.array(vA), np.array(tB), np.array(vB)


def draw_motion_rot(ax, is_cued, is_rot0):
    tA, vA, tB, vB = motion_trajs_rot(is_cued, is_rot0)
    ax.plot(tA, vA, color=C_RED,   lw=LW, ls='-',
            solid_capstyle='round', zorder=3)
    ax.plot(tB, vB, color=C_GREEN, lw=LW, ls='--', dashes=(6, 3), zorder=3)


def draw_depth(ax, a_depth, b_depth):
    """Horizontal depth lines: A (red) full width; B (green) from T_B."""
    ax.plot([T_A, T_TOT], [a_depth, a_depth],
            color=C_RED,   lw=LW_DEPTH, ls='-', zorder=3)
    ax.plot([T_B, T_TOT], [b_depth, b_depth],
            color=C_GREEN, lw=LW_DEPTH, ls='--', dashes=(6, 3), zorder=3)


# ── Figure construction ───────────────────────────────────────────────────────

fig = plt.figure(figsize=(9, 11))
fig.patch.set_facecolor('white')

outer = gridspec.GridSpec(
    2, 1, figure=fig,
    height_ratios=[1.0, 1.5],
    hspace=0.28,
    top=0.94, bottom=0.05
)

# ────────────────────────────────────────────────────────────────────────────
# TOP SECTION — flat (no depth), 2 rows × 2 cols
# ────────────────────────────────────────────────────────────────────────────
top_gs = gridspec.GridSpecFromSubplotSpec(
    2, 2, subplot_spec=outer[0],
    hspace=0.30, wspace=0.30
)

col_titles = ['Rot0  (A=CW, B=CCW)', 'Rot1  (A=CCW, B=CW)']
row_labels  = ['CUED', 'UNCUED']

# Panels: (is_cued, rot0, row, col)
# Rot0: A=CW, B=CCW  |  Rot1: A=CCW, B=CW
flat_panels = [
    (True,  True,  0, 0),   # CUED,   Rot0
    (True,  False, 0, 1),   # CUED,   Rot1
    (False, True,  1, 0),   # UNCUED, Rot0
    (False, False, 1, 1),   # UNCUED, Rot1
]

for is_cued, is_rot0, row, col in flat_panels:
    ax = fig.add_subplot(top_gs[row, col])
    setup_motion_ax(ax, show_phase_labels=(row == 0 and col == 0))
    draw_motion_rot(ax, is_cued, is_rot0)

    if row == 0:
        ax.set_title(col_titles[col], fontsize=9.5, fontweight='bold', pad=5)
    if col == 0:
        ax.set_ylabel(row_labels[row], fontsize=10, fontweight='bold', labelpad=5)

# Section header
fig.text(0.50, 0.965, 'Flat (No Depth)',
         ha='center', va='top', fontsize=12, fontweight='bold', color='#222222')

# ────────────────────────────────────────────────────────────────────────────
# BOTTOM SECTION — with depth (no swap), 2 rows × 2 cols
# Each cell = motion axes (tall) + depth axes (short), stacked
# ────────────────────────────────────────────────────────────────────────────
bot_gs = gridspec.GridSpecFromSubplotSpec(
    4, 2, subplot_spec=outer[1],
    height_ratios=[3, 1, 3, 1],
    hspace=0.08, wspace=0.30
)

# Depth assignments (translating-field-depth labeling):
#   CUED Near:   B translates, B=Near → A=Far
#   CUED Far:    B translates, B=Far  → A=Near
#   UNCUED Near: A translates, A=Near → B=Far
#   UNCUED Far:  A translates, A=Far  → B=Near
depth_panels = [
    # (is_cued, col, a_depth, b_depth)
    (True,  0, FAR,  NEAR),   # CUED Near
    (True,  1, NEAR, FAR),    # CUED Far
    (False, 0, NEAR, FAR),    # UNCUED Near
    (False, 1, FAR,  NEAR),   # UNCUED Far
]

depth_col_titles = ['Near Translation', 'Far Translation']

for is_cued, col, a_dep, b_dep in depth_panels:
    row_base = 0 if is_cued else 2

    ax_m = fig.add_subplot(bot_gs[row_base,     col])   # motion
    ax_d = fig.add_subplot(bot_gs[row_base + 1, col])   # depth

    setup_motion_ax(ax_m, show_phase_labels=(row_base == 0 and col == 0))
    draw_motion_rot(ax_m, is_cued, False)   # Rot1 (A=CCW, B=CW) for depth panels

    setup_depth_ax(ax_d)
    draw_depth(ax_d, a_dep, b_dep)

    # Titles / row labels
    if row_base == 0:
        ax_m.set_title(depth_col_titles[col], fontsize=9.5, fontweight='bold', pad=5)
    if col == 0:
        ax_m.set_ylabel(('CUED' if is_cued else 'UNCUED'),
                        fontsize=10, fontweight='bold', labelpad=5)

# Section header
fig.text(0.50, 0.515, 'With Depth (No Swap)',
         ha='center', va='top', fontsize=12, fontweight='bold', color='#222222')

# ── Legend ────────────────────────────────────────────────────────────────────
leg_A = mlines.Line2D([], [], color=C_RED,   lw=2, ls='-',
                      label='Field A  —  non-delayed, CCW rotation')
leg_B = mlines.Line2D([], [], color=C_GREEN, lw=2, ls='--', dashes=(6, 3),
                      label='Field B  —  delayed onset, CW rotation')
fig.legend(handles=[leg_A, leg_B],
           loc='lower center', ncol=2, fontsize=8.5,
           frameon=True, framealpha=0.9,
           bbox_to_anchor=(0.50, 0.005))

out_path = ('/Users/genestoner1/Projects/ObjectBasedAttention/VRDots/'
            'Agents/Figures/feature_trajectories_overview.png')
fig.savefig(out_path, dpi=150, bbox_inches='tight', facecolor='white')
print(f"Saved: {out_path}")
