#!/usr/bin/env python3
"""
sb_traj_figure.py  —  Feature trajectory schematics, S&B replication.
Saves to: Figures/sb_traj_schematic.png/.pdf
          ~/Sites/open-perception/public/figures/sb_traj_schematic.png

To regenerate:
    python3 sb_traj_figure.py
"""

import os, shutil
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.patches as mpatches
from matplotlib.lines import Line2D

# ══════════════════════════════════════════════════════════════════════════════
#  CONFIG — edit here
# ══════════════════════════════════════════════════════════════════════════════
RCOL  = "#c0392b"   # non-translating field role — RED solid
GCOL  = "#1a7a1a"   # translating field role     — GREEN dashed
LW    = 2.2         # line weight

Y_CW    = 3.0       # CW rotation track (top)
Y_TRANS = 2.0       # translation track (middle)
Y_CCW   = 1.0       # CCW rotation track (bottom)

T0   =    0         # trial start (ms)
TB   =  750         # delayed-onset field appears (ms)
TS   = 1050         # translation start (ms)
TE   = 1094         # translation end (ms)
TEND = 1350         # end of depicted window (ms)

FIG_W, FIG_H = 9, 8.0   # figure size (inches)

COND_COLORS = {'N': '#2c6e2c', 'MC': '#7b2d8b'}
COND_LABELS = {'N': 'no swap', 'MC': 'color/motion swap'}

# CUED/UNCUED label per panel (ri, ci): top row standard; bottom row swapped (MC visual flip)
CUE_LABELS = {
    (0,0): ('CUED',   '#8b0000'),
    (0,1): ('UNCUED', '#00008b'),
    (1,0): ('UNCUED', '#00008b'),
    (1,1): ('CUED',   '#8b0000'),
}
PANEL_LETTERS = {(0,0): 'A', (0,1): 'B', (1,0): 'C', (1,1): 'D'}

FIGURE_TITLE = "Figure 1."
FIGURE_SUBTITLE = "Delayed-onset design with color/motion swaps (Stoner and Blanc, 2010)."
CAPTION_BODY = (
    "Feature trajectories of dots. Dots are distinguished by line style (dashed vs solid) and color.\n"
    "Motion type (i.e. clockwise, counterclockwise, or translation) is given by vertical position.\n"
    "A) \u201cCued Translation\u201d: delayed dots translate.  "
    "B) \u201cUncued Translation\u201d: always-on dots translate.\n"
    "C) \u201cUncued Translation\u201d: always-on dots translate.  "
    "D) \u201cCued Translation\u201d: delayed dots translate.\n"
    "See Stoner & Blanc (2010) for further explanation."
)

# ══════════════════════════════════════════════════════════════════════════════
#  DRAWING
# ══════════════════════════════════════════════════════════════════════════════
def hline(ax, t0, t1, y, col, ls='-'):
    ax.plot([t0, t1], [y, y], color=col, lw=LW, ls=ls, zorder=4, solid_capstyle='butt')

def vline(ax, t, y0, y1, col, ls='-'):
    ax.plot([t, t], [y0, y1], color=col, lw=LW, ls=ls, zorder=5, solid_capstyle='round')

def draw_traj(ax, is_cued, condition):
    ax.axvspan(TS, TE, color='#cccccc', alpha=0.45, zorder=0)
    g_start = TB if is_cued else T0   # GREEN onset: delayed if CUED, always-on if UNCUED
    r_start = T0 if is_cued else TB   # RED onset:   always-on if CUED, delayed if UNCUED

    if condition == 'N':
        # GREEN dashed: CW → step to TRANS (translation) → step back to CW
        hline(ax, g_start, TS,   Y_CW,    GCOL, '--')
        vline(ax, TS,  Y_CW,    Y_TRANS,  GCOL, '--')
        hline(ax, TS,  TE,      Y_TRANS,  GCOL, '--')
        vline(ax, TE,  Y_TRANS, Y_CW,     GCOL, '--')
        hline(ax, TE,  TEND,    Y_CW,     GCOL, '--')
        # RED solid: CCW flat
        hline(ax, r_start, TEND, Y_CCW,   RCOL, '-')

    else:  # MC — line style stays with field regardless of color change
        # Dashed field: GREEN at CW → drops to CCW as RED dashed at TS
        hline(ax, g_start, TS,  Y_CW,    GCOL, '--')
        vline(ax, TS, Y_CW,    Y_CCW,    RCOL, '--')   # drop (now RED dashed)
        hline(ax, TS,  TEND,   Y_CCW,    RCOL, '--')
        # Solid field: RED at CCW → GREEN through TRANS → RED at CW
        hline(ax, r_start, TS, Y_CCW,    RCOL, '-')
        vline(ax, TS, Y_CCW,   Y_TRANS,  GCOL, '-')    # rise (now GREEN solid)
        hline(ax, TS, TE,      Y_TRANS,  GCOL, '-')    # horizontal = translation
        vline(ax, TE, Y_TRANS, Y_CW,     RCOL, '-')    # rise to CW (reverts RED)
        hline(ax, TE, TEND,    Y_CW,     RCOL, '-')

    ax.set_xlim(T0-50, TEND+50)
    ax.set_ylim(Y_CCW-0.65, Y_CW+0.70)
    ax.set_yticks([Y_CCW, Y_TRANS, Y_CW])
    ax.set_yticklabels(['CCW\nrotation', 'Translation', 'CW\nrotation'], fontsize=8)
    ax.set_xticks([])
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_visible(False)

# ══════════════════════════════════════════════════════════════════════════════
#  FIGURE ASSEMBLY
# ══════════════════════════════════════════════════════════════════════════════
fig = plt.figure(figsize=(FIG_W, FIG_H), facecolor='white')
gs = gridspec.GridSpec(2, 2, figure=fig, height_ratios=[1,1],
                       hspace=0.55, wspace=0.30,
                       left=0.14, right=0.96, top=0.88, bottom=0.26)

for ri, cond in enumerate(['N', 'MC']):
    for ci, is_cued in enumerate([True, False]):
        ax = fig.add_subplot(gs[ri, ci])
        draw_traj(ax, is_cued, cond)
        ax.text(0.02, 0.97, PANEL_LETTERS[(ri,ci)], transform=ax.transAxes,
                fontsize=12, fontweight='bold', va='top', ha='left')
        lbl, lcol = CUE_LABELS[(ri,ci)]
        ax.text(0.5, 1.04, lbl, transform=ax.transAxes,
                ha='center', va='bottom', fontsize=11, fontweight='bold', color=lcol)
        if ci == 0:
            ax.set_ylabel(COND_LABELS[cond], fontsize=9, fontweight='bold',
                          color=COND_COLORS[cond], labelpad=10, rotation=90, va='center')

for ci in range(2):
    ab = fig.axes[2+ci]
    ab.annotate('', xy=(TEND+40, Y_CCW-0.55), xytext=(T0-40, Y_CCW-0.55),
                xycoords='data', textcoords='data',
                arrowprops=dict(arrowstyle='->', color='black', lw=1.1),
                annotation_clip=False)
    ab.text((T0+TEND)/2, Y_CCW-0.63, 'Time', ha='center', va='top',
            fontsize=8.5, style='italic', transform=ab.transData)

handles = [
    Line2D([0],[0], color=GCOL, lw=2, ls='--', label='Translating field role  (GREEN dashed)'),
    Line2D([0],[0], color=RCOL, lw=2, ls='-',  label='Non-translating field role  (RED solid)'),
    mpatches.Patch(color='#cccccc', alpha=0.45, label='Translation window'),
]
fig.legend(handles=handles, fontsize=8.5, loc='upper center', ncol=3,
           bbox_to_anchor=(0.55, 1.00), framealpha=0.9, handlelength=2.5)
fig.suptitle('Feature trajectory schematics  —  S&B Replication  (VRDots, Meta Quest 3)',
             fontsize=10, fontweight='bold', y=1.07)

LEFT = 0.14
fig.text(LEFT, 0.245, FIGURE_TITLE, ha='left', va='top',
         fontsize=9, fontweight='bold', color='black')
fig.text(LEFT + 0.072, 0.245, FIGURE_SUBTITLE, ha='left', va='top',
         fontsize=9, color='black')
fig.text(LEFT, 0.195, CAPTION_BODY, ha='left', va='top',
         fontsize=8, style='italic', color='#333', multialignment='left')

# ══════════════════════════════════════════════════════════════════════════════
#  SAVE
# ══════════════════════════════════════════════════════════════════════════════
BASE = os.path.dirname(os.path.abspath(__file__))
OUT  = os.path.normpath(os.path.join(BASE, '../Figures/sb_traj_schematic.png'))
plt.savefig(OUT, dpi=150, bbox_inches='tight', facecolor='white')
plt.savefig(OUT.replace('.png','.pdf'), bbox_inches='tight', facecolor='white')
plt.savefig(OUT.replace('.png','.svg'), bbox_inches='tight', facecolor='white')
print('Saved:', OUT)

SITE = os.path.expanduser('~/Sites/open-perception/public/figures/sb_traj_schematic.png')
os.makedirs(os.path.dirname(SITE), exist_ok=True)
shutil.copy(OUT, SITE)
print('Copied to site:', SITE)
