"""
decoupled_Z_traj.py
-------------------
Stimulus trajectory figure for Exp_DecoupledDots_005m, Z (depth swap) condition.
All 16 permutations as 8 CUED/UNCUED pairs following S&B Fig 1B / Fig 5 convention.

Z swap: at tStart, depth planes exchange between all subfields.
  - Motion track: colors/styles unchanged throughout
  - Depth track: each field's depth level jumps to the other value at tStart

Line-style convention: Green = dotted (:)  Red = solid (-)  (tied to color)
Output: Agents/Figures/decoupled_Z_all_perms.pdf / .png
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
    """Z swap: depth planes swap at tStart; colors/styles unchanged."""
    y_B = Y_CW  if rot_cfg == 1 else Y_CCW
    y_A = Y_CCW if rot_cfg == 1 else Y_CW

    col_B = COL_GREEN if b_green else COL_RED
    col_A = COL_RED   if b_green else COL_GREEN
    ls_B  = LS_GREEN  if b_green else LS_RED
    ls_A  = LS_RED    if b_green else LS_GREEN

    dep_B = 1.0 if b_near else 0.0   # original depth
    dep_A = 0.0 if b_near else 1.0

    # ── Motion track: colors/styles constant (no C component) ────────────────
    a_mot = np.full(TOTAL, float(y_A))
    if not cued:
        a_mot[T_START:T_END] = Y_TRANS

    b_mot = np.full(TOTAL, np.nan)
    b_mot[ONSET:] = y_B
    if cued:
        b_mot[T_START:T_END] = Y_TRANS

    # ── Depth track: two segments per field, same color/style throughout ──────
    # Field A — pre-swap: dep_A; post-swap: dep_B (jumped to other plane)
    a_dep_pre = np.full(TOTAL, dep_A)
    a_dep_pre[T_START:] = np.nan

    a_dep_post = np.full(TOTAL, np.nan)
    a_dep_post[T_START:] = dep_B   # A now occupies B's original depth

    # Field B — pre-swap: dep_B; post-swap: dep_A
    b_dep_pre = np.full(TOTAL, np.nan)
    b_dep_pre[ONSET:T_START] = dep_B

    b_dep_post = np.full(TOTAL, np.nan)
    b_dep_post[T_START:] = dep_A   # B now occupies A's original depth

    return dict(
        a_mot=a_mot, b_mot=b_mot,
        a_dep_pre=a_dep_pre,   b_dep_pre=b_dep_pre,
        a_dep_post=a_dep_post, b_dep_post=b_dep_post,
        col_A=col_A, col_B=col_B, ls_A=ls_A, ls_B=ls_B,
    )


X_FRAC = (T_START + T_END) / 2 / TOTAL


def draw_cell(ax_mot, ax_dep, tr,
              show_xlabel=False, row_label='', col_title='', trans_label=''):
    t_s  = T_START / SIM_HZ
    t_e  = T_END   / SIM_HZ

    for ax in (ax_mot, ax_dep):
        ax.axvspan(t_s, t_e, color='gray', alpha=0.18, zorder=0)
        ax.set_xlim(0, TOTAL / SIM_HZ)

    # Motion (colors unchanged)
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

    # Depth (same color/style, but level jumps at tStart)
    ax_dep.plot(t, tr['a_dep_pre'],  color=tr['col_A'], ls=tr['ls_A'], lw=LW)
    ax_dep.plot(t, tr['b_dep_pre'],  color=tr['col_B'], ls=tr['ls_B'], lw=LW)
    ax_dep.plot(t, tr['a_dep_post'], color=tr['col_A'], ls=tr['ls_A'], lw=LW)
    ax_dep.plot(t, tr['b_dep_post'], color=tr['col_B'], ls=tr['ls_B'], lw=LW)
    ax_dep.set_yticks([0.0, 1.0])
    ax_dep.set_yticklabels(['Far', 'Near'], fontsize=6.5)
    ax_dep.set_ylim(-0.3, 1.3)
    if show_xlabel:
        ax_dep.set_xlabel('Time (s)', fontsize=8)
        ax_dep.tick_params(axis='x', labelsize=7)
    else:
        ax_dep.tick_params(labelbottom=False, bottom=False)


TITLE = ('Unity Asset: Exp_DecoupledDots_005m  ·  Z (depth swap)  ·  '
         'All 16 permutations  ·  Heading = 0°')
LEG_HANDLES = [mpatches.Patch(facecolor='gray', alpha=0.35, label='Translation window')]

CUED_TITLE   = 'Dot✓   Depth✗   Color✓'
UNCUED_TITLE = 'Dot✗   Depth✓   Color✗'


def build_figure(row_subset, figsize):
    n = len(row_subset)
    fig = plt.figure(figsize=figsize)
    fig.suptitle(TITLE, fontsize=10, fontweight='bold', y=0.99)
    hr = [2, 0.8] * n
    gs = gridspec.GridSpec(n * 2, 2, height_ratios=hr,
                           hspace=0.07, wspace=0.28,
                           top=0.87, bottom=0.06, left=0.14, right=0.97)
    for ri, row in enumerate(row_subset):
        for ci, side in enumerate(['cued', 'uncued']):
            tr = make_tracks(**row[side], cued=(side == 'cued'))
            ax_m = fig.add_subplot(gs[ri * 2,     ci])
            ax_d = fig.add_subplot(gs[ri * 2 + 1, ci])
            draw_cell(ax_m, ax_d, tr,
                      show_xlabel=(ri == n - 1),
                      row_label=row['label'] if ci == 0 else '',
                      col_title=(CUED_TITLE if ci == 0 else UNCUED_TITLE) if ri == 0 else '',
                      trans_label=row['label'])
    fig.legend(handles=LEG_HANDLES, loc='upper right', fontsize=8,
               bbox_to_anchor=(0.97, 0.94), framealpha=0.9)
    return fig


BASE = os.path.normpath(os.path.join(os.path.dirname(__file__), '../../Agents/Figures'))
os.makedirs(BASE, exist_ok=True)

fig_all = build_figure(ROWS, figsize=(10, 20))
fig_all.savefig(os.path.join(BASE, 'decoupled_Z_all_perms.png'), dpi=150, bbox_inches='tight')
plt.close(fig_all)
print('Saved PNG')

with PdfPages(os.path.join(BASE, 'decoupled_Z_all_perms.pdf')) as pdf:
    for i in range(0, len(ROWS), 2):
        fig_p = build_figure(ROWS[i:i+2], figsize=(8.5, 11))
        pdf.savefig(fig_p, bbox_inches='tight')
        plt.close(fig_p)
print(f'Saved PDF: {BASE}/decoupled_Z_all_perms.pdf')
