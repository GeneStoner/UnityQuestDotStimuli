#!/usr/bin/env python3
"""
Swap condition trajectories — 4-subfield, Fig-1B pairing convention.

S0, S1 = initially CW field (green)   — delayed in CUED,   non-delayed in UNCUED
S2, S3 = initially CCW field (red)    — non-delayed in CUED, delayed in UNCUED

Within each CUED/UNCUED pair the CW field translates in both rows; only
the onset timing differs.  Both color assignments and rotation directions
were balanced; one representative is shown.

Symbols (open larger / closed smaller — decomposable when superimposed):
  S0 ●  CW  field, coherent
  S1 □  CW  field, noise
  S2 ▲  CCW field, coherent
  S3 ◇  CCW field, noise

Y-axis levels:  CW = 2.0  |  Trans(noise) = 1.5  |  Trans(coh) = 1.0  |  CCW = 0.0
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.lines as mlines

# ── Timing & levels ───────────────────────────────────────────────────────────
T_A=0.000; T_B=0.490; T_S=0.686; T_E=0.739; T_TOT=1.000
CW=2.0; TRANS_COH=1.0; TRANS_NOI=1.5; CCW=0.0

C_CW    = '#228B22'   # green — CW field (S0, S1)
C_CCW   = '#CC3333'   # red   — CCW field (S2, S3)
C_TRANS = '#CCCCCC'
C_FRAME = '#333333'

# ── Marker grid ───────────────────────────────────────────────────────────────
_base   = np.linspace(T_A + 0.01, T_TOT - 0.01, 14)
T_MARKS = np.unique(np.sort(np.concatenate([_base, [(T_S+T_E)/2]])))

def _interp(t_key, v_key, t_q):
    return np.interp(t_q, t_key, v_key)

# ── Symbol specs ──────────────────────────────────────────────────────────────
SF = {
    'S0': ('o', 5.5, True ),   # small filled circle
    'S1': ('s', 9.0, False),   # large open square
    'S2': ('^', 6.0, True ),   # small filled triangle
    'S3': ('D', 8.5, False),   # large open diamond
}
SF_COLOR = {'S0': C_CW, 'S1': C_CW, 'S2': C_CCW, 'S3': C_CCW}

def _plot_sf(ax, name, t_key, v_key, t_query):
    color = SF_COLOR[name]
    mk, ms, filled = SF[name]
    mfc = color if filled else 'none'
    mew = 1.0 if filled else 1.6
    ax.plot(t_key, v_key, color=color, lw=0.8, ls='-',
            solid_capstyle='round', zorder=3)
    v_q = _interp(t_key, v_key, t_query)
    ax.plot(t_query, v_q, marker=mk, markersize=ms, markeredgewidth=mew,
            markerfacecolor=mfc, markeredgecolor=color, ls='none', zorder=5)


# ── Trajectory builders ───────────────────────────────────────────────────────
# t_cw  = onset of CW  field (S0, S1): T_B if CUED, T_A if UNCUED
# t_ccw = onset of CCW field (S2, S3): T_A if CUED, T_B if UNCUED

def _traj_noswap(is_cued):
    t_cw  = T_B if is_cued else T_A
    t_ccw = T_A if is_cued else T_B
    tS0=np.array([t_cw, T_S,T_S,T_E,T_E,T_TOT]); vS0=np.array([CW,CW,TRANS_COH,TRANS_COH,CW,CW])
    tS1=np.array([t_cw, T_S,T_S,T_E,T_E,T_TOT]); vS1=np.array([CW,CW,TRANS_NOI,TRANS_NOI,CW,CW])
    tS2=np.array([t_ccw,T_TOT]);                  vS2=np.array([CCW,CCW])
    tS3=np.array([t_ccw,T_TOT]);                  vS3=np.array([CCW,CCW])
    return tS0,vS0, tS1,vS1, tS2,vS2, tS3,vS3


def _traj_motionswap(is_cued):
    """CW field translates then lands at CCW (swapped). CCW field jumps to CW at T_S."""
    t_cw  = T_B if is_cued else T_A
    t_ccw = T_A if is_cued else T_B
    tS0=np.array([t_cw, T_S,T_S,T_E,T_E,T_TOT]); vS0=np.array([CW,CW,TRANS_COH,TRANS_COH,CCW,CCW])
    tS1=np.array([t_cw, T_S,T_S,T_E,T_E,T_TOT]); vS1=np.array([CW,CW,TRANS_NOI,TRANS_NOI,CCW,CCW])
    tS2=np.array([t_ccw,T_S,T_S,T_TOT]);          vS2=np.array([CCW,CCW,CW,CW])
    tS3=np.array([t_ccw,T_S,T_S,T_TOT]);          vS3=np.array([CCW,CCW,CW,CW])
    return tS0,vS0, tS1,vS1, tS2,vS2, tS3,vS3


def _traj_dots50(is_cued):
    """S1 (CW noise) and S3 (CCW noise) swap field membership at T_S.
    S0 (CW coh) translates; S3 (now in CW) translates as noise.
    S2 (CCW coh) stays; S1 (now in CCW) takes CCW rotation."""
    t_cw  = T_B if is_cued else T_A
    t_ccw = T_A if is_cued else T_B
    tS0=np.array([t_cw, T_S,T_S,T_E,T_E,T_TOT]); vS0=np.array([CW,CW,TRANS_COH,TRANS_COH,CW,CW])
    tS1=np.array([t_cw, T_S,T_S,T_TOT]);          vS1=np.array([CW,CW,CCW,CCW])
    tS2=np.array([t_ccw,T_TOT]);                  vS2=np.array([CCW,CCW])
    tS3=np.array([t_ccw,T_S,T_S,T_E,T_E,T_TOT]); vS3=np.array([CCW,CCW,TRANS_NOI,TRANS_NOI,CW,CW])
    return tS0,vS0, tS1,vS1, tS2,vS2, tS3,vS3


TRAJ_FNS = {
    'noswap':     _traj_noswap,
    'motionswap': _traj_motionswap,
    'dots50':     _traj_dots50,
}

SWAP_SECTIONS = [
    ('noswap',     'No Swap',            '#2244AA'),
    ('motionswap', 'Motion Swap (100%)', '#883300'),
    ('dots50',     'Dots50 Swap (50%)',  '#226622'),
]


def draw_panel(ax, swap_type, is_cued, show_labels=False):
    tS0,vS0, tS1,vS1, tS2,vS2, tS3,vS3 = TRAJ_FNS[swap_type](is_cued)

    t_cw  = T_B if is_cued else T_A
    t_ccw = T_A if is_cued else T_B
    m_cw  = T_MARKS[T_MARKS >= t_cw]
    m_ccw = T_MARKS[T_MARKS >= t_ccw]

    _plot_sf(ax, 'S0', tS0, vS0, m_cw)
    _plot_sf(ax, 'S1', tS1, vS1, m_cw)
    _plot_sf(ax, 'S2', tS2, vS2, m_ccw)
    _plot_sf(ax, 'S3', tS3, vS3, m_ccw)

    ax.set_xlim(T_A-.01, T_TOT+.01)
    ax.set_ylim(-.35, 2.55)
    ax.set_xticks([])
    ax.set_yticks([CCW, TRANS_COH, TRANS_NOI, CW])
    ax.set_yticklabels(['CCW', 'Trans\n(coh)', 'Trans\n(noise)', 'CW'], fontsize=6.5)
    ax.tick_params(axis='y', length=2, pad=1)
    ax.axvspan(T_S, T_E, color=C_TRANS, alpha=0.6, zorder=1)
    ax.axvline(T_B, color='#AAAAAA', lw=0.8, ls='--', zorder=2)
    for sp in ax.spines.values():
        sp.set_visible(True); sp.set_linewidth(0.8); sp.set_edgecolor(C_FRAME)
    if show_labels:
        for x, lbl in [((T_A+T_B)/2,'A only'), ((T_B+T_S)/2,'A+B'), ((T_S+T_E)/2,'T')]:
            ax.text(x, 2.50, lbl, ha='center', va='top', fontsize=6,
                    color='#888888', style='italic')


# ── Figure ────────────────────────────────────────────────────────────────────
fig = plt.figure(figsize=(6, 13))
fig.patch.set_facecolor('white')

gs = gridspec.GridSpec(6, 1, figure=fig,
                       hspace=0.35,
                       top=0.91, bottom=0.10,
                       left=0.18, right=0.88)

for sec_idx, (swap_type, swap_label, swap_color) in enumerate(SWAP_SECTIONS):
    row_cued   = sec_idx * 2
    row_uncued = sec_idx * 2 + 1

    for row, is_cued in [(row_cued, True), (row_uncued, False)]:
        ax = fig.add_subplot(gs[row, 0])
        draw_panel(ax, swap_type, is_cued,
                   show_labels=(sec_idx==0 and is_cued))
        ax.set_ylabel('CUED' if is_cued else 'UNCUED',
                      fontsize=9.5, fontweight='bold', labelpad=5)

    pos_top = gs[row_cued,   0].get_position(fig).y1
    pos_bot = gs[row_uncued, 0].get_position(fig).y0
    mid_y   = (pos_top + pos_bot) / 2
    fig.text(0.905, mid_y, swap_label,
             ha='left', va='center', fontsize=9, fontweight='bold',
             color=swap_color, rotation=90)

    if sec_idx < len(SWAP_SECTIONS) - 1:
        sep_y = pos_bot - 0.009
        fig.add_artist(plt.Line2D([0.18, 0.88], [sep_y, sep_y],
            transform=fig.transFigure, color='#BBBBBB', lw=1.2, ls='--'))

fig.suptitle('Swap Conditions — 4-Subfield Trajectories',
             fontsize=11, fontweight='bold', y=0.975)

# ── Legend — symbols only ─────────────────────────────────────────────────────
leg_handles = [
    mlines.Line2D([],[],color=C_CW,  marker='o', ms=5.5, mew=1.0,
                  mfc=C_CW,   ls='none', label='S0'),
    mlines.Line2D([],[],color=C_CW,  marker='s', ms=9.0, mew=1.6,
                  mfc='none', ls='none', label='S1'),
    mlines.Line2D([],[],color=C_CCW, marker='^', ms=6.0, mew=1.0,
                  mfc=C_CCW,  ls='none', label='S2'),
    mlines.Line2D([],[],color=C_CCW, marker='D', ms=8.5, mew=1.6,
                  mfc='none', ls='none', label='S3'),
]
fig.legend(handles=leg_handles,
           loc='lower center', ncol=4, fontsize=9,
           frameon=True, framealpha=0.92, edgecolor='#CCCCCC',
           bbox_to_anchor=(0.53, 0.015))

out_path = ('/Users/genestoner1/Projects/ObjectBasedAttention/VRDots/'
            'Agents/Figures/swap_traj_4subfield.png')
fig.savefig(out_path, dpi=150, bbox_inches='tight', facecolor='white')
print(f"Saved: {out_path}")
