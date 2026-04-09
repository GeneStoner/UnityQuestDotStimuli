"""
decoupled_N_traj.py
-------------------
Stimulus trajectory figure for Exp_DecoupledDots_005m, N (no swap) condition.
All 16 permutations shown as 8 CUED/UNCUED pairs following Stoner & Blanc (2010)
Fig 1B / Fig 5 A&C convention.

Full permutation space (DecoupledDots: color and depth are INDEPENDENT):
  2 (CUED/UNCUED) × 2 (rot_cfg) × 2 (b_green) × 2 (b_near) = 16 panels = 8 rows

Pairing principle:
  Each row pairs two DIFFERENT permutations that produce the SAME post-onset
  motion track.  The only visual difference: which field's line is absent pre-onset.
    CUED   – dipping field IS the delayed field (absent pre-onset)
    UNCUED – dipping field is NON-delayed; other field is delayed (absent pre-onset)

Line-style convention (tied to color, not field identity):
  Green = dotted  (:)   Red = solid  (-)
  Delayed field = line absent (nan) before ONSET frame.

Output: Agents/Figures/decoupled_N_all_perms.png
"""

import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.lines import Line2D
import matplotlib.patches as mpatches

# ── Timing ────────────────────────────────────────────────────────────────────
ONSET   = 56
T_START = 78
T_END   = 84
TOTAL   = 114
SIM_HZ  = 75.0
t = np.arange(TOTAL) / SIM_HZ

Y_CW, Y_TRANS, Y_CCW = 2, 1, 0

COL_GREEN = '#228B22'
COL_RED   = '#CC3333'
LS_GREEN  = ':'   # green always dotted
LS_RED    = '-'   # red always solid
LW        = 1.8

# ── Row definitions ───────────────────────────────────────────────────────────
# Parameters per panel:
#   rot_cfg : 1 → B=CW, A=CCW   |  0 → B=CCW, A=CW
#   b_green : True → B=Green, A=Red   |  False → B=Red, A=Green
#   b_near  : True → B=Near, A=Far    |  False → B=Far, A=Near
#
# Row label = translating-field identity (color / rotation / depth).
# CUED  params = permutation where dipping field = B (delayed).
# UNCUED params = complementary permutation where dipping field = A (non-delayed),
#                 and B (a different color/depth) is the delayed field.

ROWS = [
    # ── CW translates ─────────────────────────────────────────────────────────
    dict(label='Green/CW/Far',
         cued  =dict(rot_cfg=1, b_green=True,  b_near=False),  # B=Green=Far=CW dips
         uncued=dict(rot_cfg=0, b_green=False, b_near=True)),   # A=Green=Far=CW dips; B=Red=Near delayed
    dict(label='Green/CW/Near',
         cued  =dict(rot_cfg=1, b_green=True,  b_near=True),   # B=Green=Near=CW dips
         uncued=dict(rot_cfg=0, b_green=False, b_near=False)),  # A=Green=Near=CW dips; B=Red=Far delayed
    dict(label='Red/CW/Far',
         cued  =dict(rot_cfg=1, b_green=False, b_near=False),  # B=Red=Far=CW dips
         uncued=dict(rot_cfg=0, b_green=True,  b_near=True)),   # A=Red=Far=CW dips; B=Green=Near delayed
    dict(label='Red/CW/Near',
         cued  =dict(rot_cfg=1, b_green=False, b_near=True),   # B=Red=Near=CW dips
         uncued=dict(rot_cfg=0, b_green=True,  b_near=False)),  # A=Red=Near=CW dips; B=Green=Far delayed
    # ── CCW translates ────────────────────────────────────────────────────────
    dict(label='Green/CCW/Far',
         cued  =dict(rot_cfg=0, b_green=True,  b_near=False),  # B=Green=Far=CCW dips
         uncued=dict(rot_cfg=1, b_green=False, b_near=True)),   # A=Green=Far=CCW dips; B=Red=Near delayed
    dict(label='Green/CCW/Near',
         cued  =dict(rot_cfg=0, b_green=True,  b_near=True),   # B=Green=Near=CCW dips
         uncued=dict(rot_cfg=1, b_green=False, b_near=False)),  # A=Green=Near=CCW dips; B=Red=Far delayed
    dict(label='Red/CCW/Far',
         cued  =dict(rot_cfg=0, b_green=False, b_near=False),  # B=Red=Far=CCW dips
         uncued=dict(rot_cfg=1, b_green=True,  b_near=True)),   # A=Red=Far=CCW dips; B=Green=Near delayed
    dict(label='Red/CCW/Near',
         cued  =dict(rot_cfg=0, b_green=False, b_near=True),   # B=Red=Near=CCW dips
         uncued=dict(rot_cfg=1, b_green=True,  b_near=False)),  # A=Red=Near=CCW dips; B=Green=Far delayed
]


def make_tracks(rot_cfg, b_green, b_near, cued):
    """Compute motion and depth trajectories for one panel."""
    y_B = Y_CW  if rot_cfg == 1 else Y_CCW
    y_A = Y_CCW if rot_cfg == 1 else Y_CW

    # Line style by color (independent of delay status)
    col_B = COL_GREEN if b_green else COL_RED
    col_A = COL_RED   if b_green else COL_GREEN
    ls_B  = LS_GREEN  if b_green else LS_RED
    ls_A  = LS_RED    if b_green else LS_GREEN

    # Depth (independent of color in DecoupledDots)
    dep_B = 1.0 if b_near else 0.0   # Near=1, Far=0
    dep_A = 0.0 if b_near else 1.0

    # Motion: Field A (non-delayed, present from frame 0)
    a_mot = np.full(TOTAL, float(y_A))
    if not cued:
        a_mot[T_START:T_END] = Y_TRANS   # UNCUED: A dips

    # Motion: Field B (delayed, absent before ONSET)
    b_mot = np.full(TOTAL, np.nan)
    b_mot[ONSET:] = y_B
    if cued:
        b_mot[T_START:T_END] = Y_TRANS   # CUED: B dips

    # Depth: Field A
    a_dep = np.full(TOTAL, dep_A)

    # Depth: Field B (absent before ONSET)
    b_dep = np.full(TOTAL, np.nan)
    b_dep[ONSET:] = dep_B

    return dict(
        a_mot=a_mot, b_mot=b_mot,
        a_dep=a_dep, b_dep=b_dep,
        col_A=col_A, col_B=col_B,
        ls_A=ls_A,   ls_B=ls_B,
    )


T_MID_S = (T_START + T_END) / 2 / SIM_HZ
X_FRAC  = (T_START + T_END) / 2 / TOTAL   # axes-fraction for trans label


def draw_cell(ax_mot, ax_dep, tr,
              show_xlabel=False, row_label='', col_title='', trans_label=''):
    t_s  = T_START / SIM_HZ
    t_e  = T_END   / SIM_HZ

    for ax in (ax_mot, ax_dep):
        ax.axvspan(t_s, t_e, color='gray', alpha=0.18, zorder=0)
        ax.set_xlim(0, TOTAL / SIM_HZ)

    # Motion track
    ax_mot.plot(t, tr['a_mot'], color=tr['col_A'], ls=tr['ls_A'], lw=LW)
    ax_mot.plot(t, tr['b_mot'], color=tr['col_B'], ls=tr['ls_B'], lw=LW)
    ax_mot.set_yticks([Y_CCW, Y_TRANS, Y_CW])
    ax_mot.set_yticklabels(['CCW', 'TRANS', 'CW'], fontsize=6.5)
    ax_mot.set_ylim(-0.5, 2.5)
    ax_mot.tick_params(labelbottom=False, bottom=False)

    if col_title:
        cc = '#1a3a8b' if col_title.startswith('Dot✓') else '#884400'
        ax_mot.set_title(col_title, fontsize=9, fontweight='bold', pad=6, color=cc,
                         bbox=dict(boxstyle='round,pad=0.4',
                                   facecolor='#f0f4ff' if col_title.startswith('Dot✓') else '#fff4e8',
                                   edgecolor=cc, lw=0.9))
    if row_label:
        ax_mot.set_ylabel(row_label, fontsize=7, labelpad=4, va='center')
    if trans_label:
        ax_dep.text(X_FRAC, 1.22, trans_label,
                    ha='center', va='bottom', fontsize=5.5, color='#111111',
                    transform=ax_dep.transAxes, clip_on=False,
                    bbox=dict(boxstyle='round,pad=0.25', facecolor='#f8f8f8',
                              edgecolor='#888888', lw=0.6))

    # Depth track
    ax_dep.plot(t, tr['a_dep'], color=tr['col_A'], ls=tr['ls_A'], lw=LW)
    ax_dep.plot(t, tr['b_dep'], color=tr['col_B'], ls=tr['ls_B'], lw=LW)
    ax_dep.set_yticks([0.0, 1.0])
    ax_dep.set_yticklabels(['Far', 'Near'], fontsize=6.5)
    ax_dep.set_ylim(-0.3, 1.3)

    if show_xlabel:
        ax_dep.set_xlabel('Time (s)', fontsize=8)
        ax_dep.tick_params(axis='x', labelsize=7)
    else:
        ax_dep.tick_params(labelbottom=False, bottom=False)


# ── Figure helpers ────────────────────────────────────────────────────────────

LEG_HANDLES = [
    mpatches.Patch(facecolor='gray', alpha=0.35, label='Translation window'),
]

TITLE = 'Unity Asset: Exp_DecoupledDots_005m  ·  N (no swap)  ·  All 16 permutations  ·  Heading = 0°'

CUED_TITLE   = 'Dot✓   Depth✓   Color✓'
UNCUED_TITLE = 'Dot✗   Depth✗   Color✗'


def build_figure(row_subset, figsize):
    """Build one figure for a subset of ROWS.  Returns the figure."""
    n = len(row_subset)
    fig = plt.figure(figsize=figsize)

    fig.suptitle(TITLE, fontsize=10, fontweight='bold', y=0.99)

    hr = [2, 0.8] * n
    gs = gridspec.GridSpec(
        n * 2, 2,
        height_ratios=hr,
        hspace=0.07, wspace=0.28,
        top=0.87, bottom=0.06, left=0.14, right=0.97,
    )

    for ri, row in enumerate(row_subset):
        for ci, side in enumerate(['cued', 'uncued']):
            params = row[side]
            tr = make_tracks(**params, cued=(side == 'cued'))
            ax_m = fig.add_subplot(gs[ri * 2,     ci])
            ax_d = fig.add_subplot(gs[ri * 2 + 1, ci])
            draw_cell(
                ax_m, ax_d, tr,
                show_xlabel=(ri == n - 1),
                row_label=row['label'] if ci == 0 else '',
                col_title=(CUED_TITLE if ci == 0 else UNCUED_TITLE) if ri == 0 else '',
                trans_label=row['label'],
            )

    fig.legend(handles=LEG_HANDLES, loc='upper right', fontsize=8,
               bbox_to_anchor=(0.97, 0.94), framealpha=0.9)
    return fig


# ── Single tall PNG (all 16 panels) ──────────────────────────────────────────
fig_all = build_figure(ROWS, figsize=(10, 20))

OUT_PNG = os.path.normpath(os.path.join(
    os.path.dirname(__file__), '../../Agents/Figures/decoupled_N_all_perms.png'))
os.makedirs(os.path.dirname(OUT_PNG), exist_ok=True)
fig_all.savefig(OUT_PNG, dpi=150, bbox_inches='tight')
print(f'Saved PNG: {OUT_PNG}')
plt.close(fig_all)

# ── Multi-page PDF (2 rows per page, letter size) ─────────────────────────────
from matplotlib.backends.backend_pdf import PdfPages

OUT_PDF = OUT_PNG.replace('.png', '.pdf')
ROWS_PER_PAGE = 2
page_groups = [ROWS[i:i+ROWS_PER_PAGE] for i in range(0, len(ROWS), ROWS_PER_PAGE)]

with PdfPages(OUT_PDF) as pdf:
    for grp in page_groups:
        fig_p = build_figure(grp, figsize=(8.5, 11))
        pdf.savefig(fig_p, bbox_inches='tight')
        plt.close(fig_p)

print(f'Saved PDF: {OUT_PDF}')
