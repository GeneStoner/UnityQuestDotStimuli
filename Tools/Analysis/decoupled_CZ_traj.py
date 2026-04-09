"""
decoupled_CZ_traj.py
--------------------
Stimulus trajectory figure for Exp_DecoupledDots_005m, CZ (color + depth swap) condition.
All 16 permutations as 8 CUED/UNCUED pairs following S&B Fig 1B / Fig 5 convention.

CZ swap: at tStart, field colors AND depth planes both exchange simultaneously.
  - Motion track: lines switch color+style at tStart (C component)
  - Depth track: lines switch color+style AND depth levels jump at tStart (C + Z)

Line-style convention: Green = dotted (:)  Red = solid (-)  (tied to color)
Output: Agents/Figures/decoupled_CZ_all_perms.pdf / .png
"""

import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.patches as mpatches
from matplotlib.backends.backend_pdf import PdfPages

ONSET   = 56
T_START = 78
T_END   = 84
TOTAL   = 114
SIM_HZ  = 75.0
t = np.arange(TOTAL) / SIM_HZ

Y_CW, Y_TRANS, Y_CCW = 2, 1, 0
COL_GREEN, COL_RED = '#228B22', '#CC3333'
LS_GREEN,  LS_RED  = ':', '-'
LW = 1.8

ROWS = [
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
]


def make_tracks(rot_cfg, b_green, b_near, cued):
    """CZ swap: colors swap AND depth planes swap at tStart."""
    y_B = Y_CW  if rot_cfg == 1 else Y_CCW
    y_A = Y_CCW if rot_cfg == 1 else Y_CW

    # Original colors (pre-swap)
    col_B = COL_GREEN if b_green else COL_RED
    col_A = COL_RED   if b_green else COL_GREEN
    ls_B  = LS_GREEN  if b_green else LS_RED
    ls_A  = LS_RED    if b_green else LS_GREEN

    # Post-swap colors (exchange)
    col_A2, ls_A2 = col_B, ls_B
    col_B2, ls_B2 = col_A, ls_A

    dep_B = 1.0 if b_near else 0.0
    dep_A = 0.0 if b_near else 1.0

    # ── Motion: color/style swaps at tStart ───────────────────────────────────
    a_mot_pre = np.full(TOTAL, float(y_A))
    a_mot_pre[T_START:] = np.nan

    a_mot_post = np.full(TOTAL, np.nan)
    a_mot_post[T_START:] = y_A
    if not cued:
        a_mot_post[T_START:T_END] = Y_TRANS

    b_mot_pre = np.full(TOTAL, np.nan)
    b_mot_pre[ONSET:T_START] = y_B

    b_mot_post = np.full(TOTAL, np.nan)
    b_mot_post[T_START:] = y_B
    if cued:
        b_mot_post[T_START:T_END] = Y_TRANS

    # ── Depth: color/style AND level both swap at tStart ─────────────────────
    # Field A: pre → dep_A in col_A; post → dep_B in col_A2 (both change!)
    a_dep_pre = np.full(TOTAL, dep_A)
    a_dep_pre[T_START:] = np.nan

    a_dep_post = np.full(TOTAL, np.nan)
    a_dep_post[T_START:] = dep_B   # depth jumps to B's original level

    # Field B: pre → dep_B in col_B; post → dep_A in col_B2
    b_dep_pre = np.full(TOTAL, np.nan)
    b_dep_pre[ONSET:T_START] = dep_B

    b_dep_post = np.full(TOTAL, np.nan)
    b_dep_post[T_START:] = dep_A   # depth jumps to A's original level

    return dict(
        a_mot_pre=a_mot_pre,  b_mot_pre=b_mot_pre,
        a_mot_post=a_mot_post, b_mot_post=b_mot_post,
        a_dep_pre=a_dep_pre,  b_dep_pre=b_dep_pre,
        a_dep_post=a_dep_post, b_dep_post=b_dep_post,
        col_A=col_A,   col_B=col_B,   ls_A=ls_A,   ls_B=ls_B,
        col_A2=col_A2, col_B2=col_B2, ls_A2=ls_A2, ls_B2=ls_B2,
    )


X_FRAC    = (T_START + T_END) / 2 / TOTAL
X_ON_FRAC = ONSET / TOTAL


def draw_cell(ax_mot, ax_dep, tr,
              show_xlabel=False, row_label='', col_title='',
              trans_label='', delayed_label=''):
    t_s  = T_START / SIM_HZ
    t_e  = T_END   / SIM_HZ

    for ax in (ax_mot, ax_dep):
        ax.axvspan(t_s, t_e, color='gray', alpha=0.18, zorder=0)
        ax.set_xlim(0, TOTAL / SIM_HZ)

    # Motion — pre and post swap
    ax_mot.plot(t, tr['a_mot_pre'],  color=tr['col_A'],  ls=tr['ls_A'],  lw=LW)
    ax_mot.plot(t, tr['b_mot_pre'],  color=tr['col_B'],  ls=tr['ls_B'],  lw=LW)
    ax_mot.plot(t, tr['a_mot_post'], color=tr['col_A2'], ls=tr['ls_A2'], lw=LW)
    ax_mot.plot(t, tr['b_mot_post'], color=tr['col_B2'], ls=tr['ls_B2'], lw=LW)
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
    # Delayed-onset field label — left side of gap, gold border
    if delayed_label:
        ax_dep.text(0.03, 1.10, f'* {delayed_label}',
                    ha='left', va='bottom', fontsize=5.5, color='#111111',
                    transform=ax_dep.transAxes, clip_on=False,
                    bbox=dict(boxstyle='round,pad=0.25', facecolor='#fffde7',
                              edgecolor='#997700', lw=0.6))
    # Translator label — right side of gap, gray border
    if trans_label:
        ax_dep.text(0.97, 1.10, f'▶ {trans_label}',
                    ha='right', va='bottom', fontsize=5.5, color='#111111',
                    transform=ax_dep.transAxes, clip_on=False,
                    bbox=dict(boxstyle='round,pad=0.25', facecolor='#f8f8f8',
                              edgecolor='#888888', lw=0.6))

    # Depth — pre: original color+level; post: swapped color+level
    ax_dep.plot(t, tr['a_dep_pre'],  color=tr['col_A'],  ls=tr['ls_A'],  lw=LW)
    ax_dep.plot(t, tr['b_dep_pre'],  color=tr['col_B'],  ls=tr['ls_B'],  lw=LW)
    ax_dep.plot(t, tr['a_dep_post'], color=tr['col_A2'], ls=tr['ls_A2'], lw=LW)
    ax_dep.plot(t, tr['b_dep_post'], color=tr['col_B2'], ls=tr['ls_B2'], lw=LW)
    ax_dep.set_yticks([0.0, 1.0])
    ax_dep.set_yticklabels(['Far', 'Near'], fontsize=6.5)
    ax_dep.set_ylim(-0.3, 1.3)
    if show_xlabel:
        ax_dep.set_xlabel('Time (s)', fontsize=8)
        ax_dep.tick_params(axis='x', labelsize=7)
    else:
        ax_dep.tick_params(labelbottom=False, bottom=False)


TITLE = ('Unity Asset: Exp_DecoupledDots_005m  ·  CZ (color + depth swap)  ·  '
         'All 16 permutations  ·  Heading = 0°')
LEG_HANDLES = [
    mpatches.Patch(facecolor='gray', alpha=0.35, label='Translation window'),
    mpatches.Patch(facecolor='#fffde7', edgecolor='#997700', lw=0.8,
                   label='* = delayed-field onset'),
    mpatches.Patch(facecolor='#f8f8f8', edgecolor='#888888', lw=0.8,
                   label='▶ = translating field'),
]

CUED_TITLE   = 'Dot✓   Depth✗   Color✗'
UNCUED_TITLE = 'Dot✗   Depth✓   Color✓'


def build_figure(row_subset, figsize):
    n = len(row_subset)
    fig = plt.figure(figsize=figsize)
    fig.suptitle(TITLE, fontsize=10, fontweight='bold', y=0.99)
    hr = [2, 0.8] * n
    gs = gridspec.GridSpec(n * 2, 2, height_ratios=hr,
                           hspace=0.18, wspace=0.28,
                           top=0.87, bottom=0.06, left=0.14, right=0.97)
    for ri, row in enumerate(row_subset):
        for ci, side in enumerate(['cued', 'uncued']):
            params = row[side]
            tr = make_tracks(**params, cued=(side == 'cued'))
            delayed_label = (f"{'Grn' if params['b_green'] else 'Red'}/"
                             f"{'CW' if params['rot_cfg']==1 else 'CCW'}/"
                             f"{'Near' if params['b_near'] else 'Far'}")
            ax_m = fig.add_subplot(gs[ri * 2,     ci])
            ax_d = fig.add_subplot(gs[ri * 2 + 1, ci])
            draw_cell(ax_m, ax_d, tr,
                      show_xlabel=(ri == n - 1),
                      row_label=row['label'] if ci == 0 else '',
                      col_title=(CUED_TITLE if ci == 0 else UNCUED_TITLE) if ri == 0 else '',
                      trans_label=row['label'],
                      delayed_label=delayed_label)
    fig.legend(handles=LEG_HANDLES, loc='upper center', ncol=3, fontsize=7,
               bbox_to_anchor=(0.5, 0.975), framealpha=0.9)
    return fig


def build_condensed_figure(figsize=(11, 17)):
    """All 16 permutations in 4 quadrants on one page (2×2 layout)."""
    fig = plt.figure(figsize=figsize)
    fig.suptitle(TITLE, fontsize=9, fontweight='bold', y=0.99)

    outer = gridspec.GridSpec(2, 2, hspace=0.22, wspace=0.22,
                              top=0.91, bottom=0.04, left=0.09, right=0.97)

    quad_slices = [ROWS[0:2], ROWS[2:4], ROWS[4:6], ROWS[6:8]]
    for qi, row_subset in enumerate(quad_slices):
        qr, qc = divmod(qi, 2)
        inner = gridspec.GridSpecFromSubplotSpec(
            4, 2, subplot_spec=outer[qr, qc],
            height_ratios=[2, 0.8, 2, 0.8],
            hspace=0.18, wspace=0.28,
        )
        for ri, row in enumerate(row_subset):
            for ci, side in enumerate(['cued', 'uncued']):
                params = row[side]
                tr = make_tracks(**params, cued=(side == 'cued'))
                delayed_label = (f"{'Grn' if params['b_green'] else 'Red'}/"
                                 f"{'CW' if params['rot_cfg']==1 else 'CCW'}/"
                                 f"{'Near' if params['b_near'] else 'Far'}")
                ax_m = fig.add_subplot(inner[ri * 2,     ci])
                ax_d = fig.add_subplot(inner[ri * 2 + 1, ci])
                draw_cell(ax_m, ax_d, tr,
                          show_xlabel=(ri == 1),
                          row_label=row['label'] if ci == 0 else '',
                          col_title=(CUED_TITLE if ci == 0 else UNCUED_TITLE) if ri == 0 else '',
                          trans_label=row['label'],
                          delayed_label=delayed_label)

    fig.legend(handles=LEG_HANDLES, loc='upper center', ncol=3, fontsize=7,
               bbox_to_anchor=(0.5, 0.975), framealpha=0.9)
    return fig


BASE = os.path.normpath(os.path.join(os.path.dirname(__file__), '../../Agents/Figures'))
os.makedirs(BASE, exist_ok=True)

fig_all = build_figure(ROWS, figsize=(10, 20))
fig_all.savefig(os.path.join(BASE, 'decoupled_CZ_all_perms.png'), dpi=150, bbox_inches='tight')
plt.close(fig_all)
print('Saved PNG')

with PdfPages(os.path.join(BASE, 'decoupled_CZ_all_perms.pdf')) as pdf:
    for i in range(0, len(ROWS), 2):
        fig_p = build_figure(ROWS[i:i+2], figsize=(8.5, 11))
        pdf.savefig(fig_p, bbox_inches='tight')
        plt.close(fig_p)
print(f'Saved PDF: {BASE}/decoupled_CZ_all_perms.pdf')

# Condensed 4-quadrant single-page PDF
fig_c = build_condensed_figure(figsize=(11, 17))
with PdfPages(os.path.join(BASE, 'decoupled_CZ_condensed.pdf')) as pdf:
    pdf.savefig(fig_c, bbox_inches='tight')
plt.close(fig_c)
print(f'Saved condensed PDF: {BASE}/decoupled_CZ_condensed.pdf')
