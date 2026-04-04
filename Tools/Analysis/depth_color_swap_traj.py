#!/usr/bin/env python3
"""
depth_color_swap_traj.py — Trajectories for depth+color linked swap conditions.

Design: each depth plane has a dedicated color.
    Near plane = Red   (#CC3333)
    Far  plane = Green (#228B22)

When subfields swap depth planes at T_S, they also change color.

ZdCoh (was ZdA): coherent subfields S0 & S2 swap depth+color at T_S.
                 The cued translator (S0) changes depth AND color.
ZdNoi (was ZdB): noise subfields S1 & S3 swap depth+color at T_S.
                 The cued translator (S0) stays in its plane and color.

This script shows ZdCoh only (the condition where the translator changes
depth and color).  Columns = Near / Far translation.  Rows = CUED / UNCUED.

Output: Agents/Figures/depth_color_swap_traj.png
"""

import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.lines as mlines
import matplotlib.patches as mpatches

OUT_PATH = os.path.expanduser(
    "~/Projects/ObjectBasedAttention/VRDots/Agents/Figures/depth_color_swap_traj.png")

# ── Timing ─────────────────────────────────────────────────────────────────────
T_A=0.00; T_B=0.490; T_S=0.686; T_E=0.739; T_TOT=1.00
CW=2.0; TRANS_COH=1.0; TRANS_NOI=1.5; CCW=0.0
NEAR_Y=0.0; FAR_Y=1.0
EPS = 1e-4

_base   = np.linspace(T_A+0.01, T_TOT-0.01, 14)
T_MARKS = np.unique(np.sort(np.concatenate([_base, [(T_S+T_E)/2]])))

# ── Colors ─────────────────────────────────────────────────────────────────────
C_NEAR  = '#CC3333'   # Red   — Near-plane dot color
C_FAR   = '#228B22'   # Green — Far-plane dot color
C_TRANS = '#CCCCCC'
C_FRAME = '#333333'

# ── Marker styles ─────────────────────────────────────────────────────────────
SF = {'S0':('o',5.5,True),'S1':('s',9.0,False),'S2':('^',6.0,True),'S3':('D',8.5,False)}

def _sf_colors(cw_dep):
    """Return (color_pre_swap, color_post_swap) dicts for ZdCoh.

    S0/S1 start in the CW (translating) plane; S2/S3 in the CCW plane.
    ZdCoh swaps S0 and S2 planes (and thus colors) at T_S.
    S1 and S3 stay in their original planes throughout.
    """
    cw_col  = C_NEAR if cw_dep == 'N' else C_FAR
    ccw_col = C_FAR  if cw_dep == 'N' else C_NEAR
    pre  = {'S0': cw_col,  'S1': cw_col,  'S2': ccw_col, 'S3': ccw_col}
    post = {'S0': ccw_col, 'S1': cw_col,  'S2': cw_col,  'S3': ccw_col}
    return pre, post


def _plot_twocolor(ax, name, tk, vk, tq, c_pre, c_post):
    """Draw a subfield trajectory with a color change at T_S.

    Strategy: draw full trajectory in c_pre, then overdraw the post-T_S
    segment in c_post (handles lines that span T_S without T_S as a node).
    Markers are split at T_S: pre markers in c_pre, post markers in c_post.
    """
    mk, ms, filled = SF[name]
    mew = 1.0 if filled else 1.6

    # Full line in pre-color
    ax.plot(tk, vk, color=c_pre, lw=0.9, solid_capstyle='round', zorder=3)

    # Overdraw post-T_S segment in post-color (only if colors differ)
    if c_pre != c_post:
        v_ts = float(np.interp(T_S, tk, vk))
        tk_post = np.concatenate([[T_S], tk[tk > T_S]])
        vk_post = np.concatenate([[v_ts], vk[tk > T_S]])
        if len(tk_post) >= 2:
            ax.plot(tk_post, vk_post, color=c_post, lw=0.9,
                    solid_capstyle='round', zorder=4)

    # Markers split at T_S
    for tq_seg, c in [(tq[tq < T_S], c_pre), (tq[tq >= T_S], c_post)]:
        if len(tq_seg) == 0:
            continue
        vq  = np.interp(tq_seg, tk, vk)
        mfc = c if filled else 'none'
        ax.plot(tq_seg, vq, marker=mk, ms=ms, mew=mew,
                mfc=mfc, mec=c, ls='none', zorder=5)


def draw_motion(ax, is_cued, cw_dep, show_labels=False):
    """ZdCoh motion trajectories with depth-color coding.

    Motion is identical to plain ZdA: S1 flips CW→CCW at T_S,
    S3 goes CCW→TRANS_NOI→CW.  The new element is that S0 and S2
    also change color at T_S (tracking their depth-plane change).
    """
    t0 = T_B if is_cued else T_A
    t2 = T_A if is_cued else T_B

    tS0 = np.array([t0, T_S,     T_S,       T_E,       T_E,  T_TOT])
    vS0 = np.array([CW, CW, TRANS_COH, TRANS_COH,      CW,    CW])
    tS1 = np.array([t0, T_S-EPS, T_S,   T_TOT])
    vS1 = np.array([CW, CW,      CCW,   CCW])
    tS2 = np.array([t2, T_TOT])
    vS2 = np.array([CCW, CCW])
    tS3 = np.array([t2, T_S-EPS, T_S,       T_E,       T_E,  T_TOT])
    vS3 = np.array([CCW, CCW, TRANS_NOI, TRANS_NOI,     CW,    CW])

    pre, post = _sf_colors(cw_dep)
    m0 = T_MARKS[T_MARKS >= t0]
    m2 = T_MARKS[T_MARKS >= t2]
    mq = {'S0':m0,'S1':m0,'S2':m2,'S3':m2}

    for name, tk, vk in [('S0',tS0,vS0),('S1',tS1,vS1),
                          ('S2',tS2,vS2),('S3',tS3,vS3)]:
        _plot_twocolor(ax, name, tk, vk, mq[name], pre[name], post[name])

    ax.set_xlim(T_A-.01, T_TOT+.01); ax.set_ylim(-.35, 2.55)
    ax.set_xticks([]); ax.set_yticks([CCW, TRANS_COH, TRANS_NOI, CW])
    ax.set_yticklabels(['CCW','Trans\n(coh)','Trans\n(noi)','CW'], fontsize=5.5)
    ax.tick_params(axis='y', length=2, pad=1)
    ax.axvspan(T_S, T_E, color=C_TRANS, alpha=0.6, zorder=1)
    ax.axvline(T_B, color='#AAAAAA', lw=0.8, ls='--', zorder=2)
    for sp in ax.spines.values():
        sp.set_visible(True); sp.set_linewidth(0.7); sp.set_edgecolor(C_FRAME)
    if show_labels:
        for x, lbl in [((T_A+T_B)/2,'A only'),((T_B+T_S)/2,'A+B'),((T_S+T_E)/2,'T')]:
            ax.text(x, 2.48, lbl, ha='center', va='top', fontsize=5,
                    color='#888888', style='italic')


def draw_depth(ax, is_cued, cw_dep):
    """Depth tracks for ZdCoh.  Marker color = dot color (Near=Red, Far=Green).

    S0 and S2 step to the opposite plane at T_S (and change color).
    S1 and S3 remain flat (no depth or color change).
    """
    cw_y  = NEAR_Y if cw_dep == 'N' else FAR_Y
    ccw_y = FAR_Y  if cw_dep == 'N' else NEAR_Y
    t_cw  = T_B if is_cued else T_A
    t_ccw = T_A if is_cued else T_B

    ts0 = np.array([t_cw,  T_S-EPS, T_S,   T_TOT])
    vs0 = np.array([cw_y,  cw_y,    ccw_y, ccw_y])
    ts1, vs1 = np.array([t_cw,  T_TOT]), np.array([cw_y,  cw_y])
    ts2 = np.array([t_ccw, T_S-EPS, T_S,   T_TOT])
    vs2 = np.array([ccw_y, ccw_y,   cw_y,  cw_y])
    ts3, vs3 = np.array([t_ccw, T_TOT]), np.array([ccw_y, ccw_y])

    pre, post = _sf_colors(cw_dep)
    for name, tk, vk, t_on in [('S0',ts0,vs0,t_cw), ('S1',ts1,vs1,t_cw),
                                 ('S2',ts2,vs2,t_ccw),('S3',ts3,vs3,t_ccw)]:
        tq = T_MARKS[T_MARKS >= t_on]
        _plot_twocolor(ax, name, tk, vk, tq, pre[name], post[name])

    ax.set_xlim(T_A-.01, T_TOT+.01); ax.set_ylim(-0.5, 1.5)
    ax.set_xticks([]); ax.set_yticks([NEAR_Y, FAR_Y])
    ax.set_yticklabels(['Near','Far'], fontsize=5.5)
    ax.tick_params(axis='y', length=2, pad=1)
    ax.axvspan(T_S, T_E, color=C_TRANS, alpha=0.6, zorder=1)
    ax.axvline(T_B, color='#AAAAAA', lw=0.8, ls='--', zorder=2)
    for sp in ax.spines.values():
        sp.set_visible(True); sp.set_linewidth(0.7); sp.set_edgecolor(C_FRAME)


# ── Figure ────────────────────────────────────────────────────────────────────
FIG_W, FIG_H = 7.0, 5.8
DPI = 150

fig = plt.figure(figsize=(FIG_W, FIG_H))
fig.patch.set_facecolor('white')

fig.text(0.50, 0.980,
    'ZdCoh (= ZdA)  —  Cued Translator Changes Depth & Color at T\u209B',
    ha='center', va='top', fontsize=10, fontweight='bold', color='#111111')
fig.text(0.50, 0.955,
    'Near plane = Red \u2003\u2003 Far plane = Green \u2003\u2003 '
    'Color changes at T\u209B for S0\u25cf and S2\u25b2 (coherent subfields)',
    ha='center', va='top', fontsize=7.5, color='#444444')

COL_TITLES = ['Near Translation', 'Far Translation']
CW_DEPTHS  = ['N', 'F']   # depth of the CW (translating-in-CUED) field

gs = gridspec.GridSpec(4, 2,
    top=0.905, bottom=0.07,
    left=0.105, right=0.920,
    height_ratios=[3, 1, 3, 1],
    hspace=0.09, wspace=0.22)

for ci, (ctitle, cw_dep) in enumerate(zip(COL_TITLES, CW_DEPTHS)):
    ax_cm = fig.add_subplot(gs[0, ci])
    draw_motion(ax_cm, is_cued=True,  cw_dep=cw_dep, show_labels=(ci==0))
    ax_cm.set_title(ctitle, fontsize=8.5, fontweight='bold', pad=3)
    if ci==0: ax_cm.set_ylabel('CUED',   fontsize=7.5, fontweight='bold', labelpad=3)

    ax_cd = fig.add_subplot(gs[1, ci])
    draw_depth(ax_cd, is_cued=True,  cw_dep=cw_dep)
    if ci==0: ax_cd.set_ylabel('Depth', fontsize=6, labelpad=3, color='#555')

    ax_um = fig.add_subplot(gs[2, ci])
    draw_motion(ax_um, is_cued=False, cw_dep=cw_dep)
    if ci==0: ax_um.set_ylabel('UNCUED', fontsize=7.5, fontweight='bold', labelpad=3)

    ax_ud = fig.add_subplot(gs[3, ci])
    draw_depth(ax_ud, is_cued=False, cw_dep=cw_dep)
    if ci==0: ax_ud.set_ylabel('Depth', fontsize=6, labelpad=3, color='#555')

# ── Legend ────────────────────────────────────────────────────────────────────
leg_handles = [
    mlines.Line2D([],[],color=C_NEAR,marker='o',ms=5.5,mew=1.0,mfc=C_NEAR,
                  ls='none', label='S0\u25cf  Near→Red (coh, translating)'),
    mlines.Line2D([],[],color=C_NEAR,marker='s',ms=8.5,mew=1.5,mfc='none',
                  ls='none', label='S1\u25a1  Near→Red (noise)'),
    mlines.Line2D([],[],color=C_FAR, marker='^',ms=6.0,mew=1.0,mfc=C_FAR,
                  ls='none', label='S2\u25b2  Far→Green (coh)'),
    mlines.Line2D([],[],color=C_FAR, marker='D',ms=8.0,mew=1.5,mfc='none',
                  ls='none', label='S3\u25c7  Far→Green (noise)'),
    mpatches.Patch(facecolor=C_TRANS, alpha=0.8, edgecolor='#888',
                   label='Translation window'),
]
ax_leg = fig.add_axes([0.04, 0.00, 0.92, 0.065])
ax_leg.axis('off')
ax_leg.legend(handles=leg_handles, loc='center', ncol=5, fontsize=6.8,
              frameon=True, framealpha=0.9, edgecolor='#CCC')

fig.savefig(OUT_PATH, dpi=DPI, bbox_inches='tight', facecolor='white')
print(f"Saved: {OUT_PATH}")
