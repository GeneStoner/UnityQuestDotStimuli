"""
decoupled_N_traces.py
---------------------
Dot-motion trace figure for Exp_DecoupledDots_005m, N (no swap) condition.
All 16 permutations as 8 CUED/UNCUED pairs. Heading = 0°.

Shows the physical dot traces for both fields across the peri-translation interval.

During rotation (all frames outside translation window):
  S0+S1 rotate together; S2+S3 rotate together — indistinguishable within field.

During translation window (T_START to T_END):
  CUED:   S2 → Linear (heading dir),  S3 → NonCoherent (8 balanced dirs, same speed)
  UNCUED: S0 → Linear (heading dir),  S1 → NonCoherent (8 balanced dirs, same speed)
  The other field's both subfields continue rotating.

Visual encoding:
  Color: Field A vs Field B (Green/Red per b_green parameter)
  Fill:  Filled circle = Near depth plane  |  Open circle = Far depth plane
  Alpha: early frames faint → later frames opaque
  Arrow: translation heading direction

Frames shown: every other frame, 6-before / 6-during / 6-after
  = 72, 74, 76 | 78, 80, 82 | 84, 86, 88  (9 total)

Output: Agents/Figures/decoupled_N_traces.pdf / .png
"""

import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.lines import Line2D
from matplotlib.backends.backend_pdf import PdfPages

# ── Experiment parameters ─────────────────────────────────────────────────────
ONSET   = 56
T_START = 78
T_END   = 84
SIM_HZ  = 75.0
ROT_DEG_PER_FRAME   = 81.0  / SIM_HZ   # 1.08°/frame
TRANS_DEG_PER_FRAME = 2.26  / SIM_HZ   # 0.030°/frame
APERTURE_RAD = 3.5
HEADING_RAD  = 0.0                      # 0° = rightward

# ── Selected frames ───────────────────────────────────────────────────────────
SHOW_FRAMES = list(range(T_START - 6, T_END + 6, 2))  # [72,74,76,78,80,82,84,86,88]

# ── 8 balanced NonCoherent directions (from StimulusBuilder.cs) ──────────────
_d = np.array([[1,0],[1,1],[0,1],[-1,1],[-1,0],[-1,-1],[0,-1],[1,-1]], dtype=float)
DIRS_8 = _d / np.linalg.norm(_d, axis=1, keepdims=True)

# ── Dot clouds ────────────────────────────────────────────────────────────────
N_DOTS   = 30     # per subfield
RNG_SEED = 42

def _make_cloud(seed_offset):
    rng = np.random.default_rng(RNG_SEED + seed_offset)
    r  = APERTURE_RAD * np.sqrt(rng.uniform(0, 1, N_DOTS))
    th = rng.uniform(0, 2 * np.pi, N_DOTS)
    return np.column_stack([r * np.cos(th), r * np.sin(th)])

S0_STARTS = _make_cloud(0)
S1_STARTS = _make_cloud(1)
S2_STARTS = _make_cloud(2)
S3_STARTS = _make_cloud(3)

# ── Colors ────────────────────────────────────────────────────────────────────
COL_GREEN = '#228B22'
COL_RED   = '#CC3333'

# ── Row definitions ───────────────────────────────────────────────────────────
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


def simulate_cloud(starts, onset_frame, max_frame, is_cw,
                   trans_linear=False, trans_noncoherent=False):
    """
    Simulate a cloud of N dots.
    trans_linear:      this subfield translates in heading dir during [T_START, T_END)
    trans_noncoherent: this subfield fans out in 8 balanced dirs during [T_START, T_END)
    All other frames: rotate CW or CCW.
    Returns {frame: ndarray (N, 2)}.
    """
    pos   = starts.copy()
    rot_r = np.radians(-ROT_DEG_PER_FRAME if is_cw else ROT_DEG_PER_FRAME)
    c_r, s_r  = np.cos(rot_r), np.sin(rot_r)
    trans_vec = TRANS_DEG_PER_FRAME * np.array([np.cos(HEADING_RAD), np.sin(HEADING_RAD)])
    # noncoherent: each dot's fixed direction vector scaled by step size
    nc_deltas = DIRS_8[np.arange(len(pos)) % 8] * TRANS_DEG_PER_FRAME  # (N, 2)

    positions = {}
    for f in range(onset_frame, max_frame + 1):
        positions[f] = pos.copy()
        if f < max_frame:
            in_trans = T_START <= f < T_END
            if trans_linear and in_trans:
                pos = pos + trans_vec
            elif trans_noncoherent and in_trans:
                pos = pos + nc_deltas
            else:
                x = pos[:, 0] * c_r - pos[:, 1] * s_r
                y = pos[:, 0] * s_r + pos[:, 1] * c_r
                pos = np.column_stack([x, y])
    return positions


def draw_panel(ax, rot_cfg, b_green, b_near, cued, row_label='', col_title=''):
    col_B = COL_GREEN if b_green else COL_RED
    col_A = COL_RED   if b_green else COL_GREEN
    b_cw  = (rot_cfg == 1)
    a_cw  = (rot_cfg == 0)
    a_near = not b_near   # Field A depth is opposite of Field B

    # Which subfield gets each motion mode during translation
    # CUED:   B-coh (S2) linear,    B-inc (S3) noncoherent,  A both rotate
    # UNCUED: A-coh (S0) linear,    A-inc (S1) noncoherent,  B both rotate
    max_f = max(SHOW_FRAMES)
    s0 = simulate_cloud(S0_STARTS, 0,     max_f, a_cw,
                        trans_linear=(not cued), trans_noncoherent=False)
    s1 = simulate_cloud(S1_STARTS, 0,     max_f, a_cw,
                        trans_linear=False,       trans_noncoherent=(not cued))
    s2 = simulate_cloud(S2_STARTS, ONSET, max_f, b_cw,
                        trans_linear=cued,        trans_noncoherent=False)
    s3 = simulate_cloud(S3_STARTS, ONSET, max_f, b_cw,
                        trans_linear=False,        trans_noncoherent=cued)

    # Aperture + crosshairs
    th = np.linspace(0, 2 * np.pi, 300)
    ax.plot(APERTURE_RAD * np.cos(th), APERTURE_RAD * np.sin(th),
            color='#bbbbbb', lw=0.8, ls='--', zorder=0)
    ax.axhline(0, color='#eeeeee', lw=0.4, zorder=0)
    ax.axvline(0, color='#eeeeee', lw=0.4, zorder=0)

    n_frames = len(SHOW_FRAMES)

    # (subfield dict, color, is_near)
    layers = [(s0, col_A, a_near), (s1, col_A, a_near),
              (s2, col_B, b_near), (s3, col_B, b_near)]

    for sf, col, is_near in layers:
        for fi, f in enumerate(SHOW_FRAMES):
            alpha = 0.12 + 0.88 * fi / (n_frames - 1)
            pts = sf[f]  # (N, 2)
            if is_near:
                ax.scatter(pts[:, 0], pts[:, 1], s=7,
                           facecolors=col, edgecolors='none',
                           alpha=alpha, zorder=2, linewidths=0)
            else:
                ax.scatter(pts[:, 0], pts[:, 1], s=12,
                           facecolors='none', edgecolors=col,
                           alpha=alpha, zorder=2, linewidths=0.6)

    # Translation arrow — heading direction, just inside bottom of aperture
    arr_y = -APERTURE_RAD + 0.55
    ax.annotate('', xy=(0.7, arr_y), xytext=(-0.7, arr_y),
                arrowprops=dict(arrowstyle='->', color='#555555',
                                lw=1.0, mutation_scale=7))

    ax.set_xlim(-4.3, 4.3)
    ax.set_ylim(-4.3, 4.3)
    ax.set_aspect('equal')
    ax.set_xticks([])
    ax.set_yticks([])
    ax.spines[['top', 'right', 'bottom', 'left']].set_visible(False)

    if col_title:
        ax.set_title(col_title, fontsize=11, fontweight='bold', pad=4)
    if row_label:
        ax.set_ylabel(row_label, fontsize=7, labelpad=3, va='center')


# ── Figure ────────────────────────────────────────────────────────────────────
TITLE    = ('Unity Asset: Exp_DecoupledDots_005m  ·  N (no swap)  ·  '
            'Dot traces  ·  Heading = 0°')
SUBTITLE = ('Peri-translation interval:  '
            'Pre 72–77 (80 ms)  ·  Trans 78–83 (80 ms)  ·  Post 84–89 (80 ms)  ·  '
            '75 Hz  ·  every other frame  ·  T\u2080 = frame 78 (1040 ms post-onset)')

LEG_HANDLES = [
    Line2D([0], [0], marker='o', color='#666666', lw=0, ms=5,
           markerfacecolor='#666666', label='Near (filled)'),
    Line2D([0], [0], marker='o', color='#666666', lw=0, ms=5,
           markerfacecolor='none', markeredgecolor='#666666',
           markeredgewidth=0.8, label='Far (open)'),
    Line2D([0], [0], marker='o', color='#aaaaaa', lw=0, ms=4,
           markerfacecolor='#aaaaaa', alpha=0.18, label='Earlier frames'),
    Line2D([0], [0], marker='o', color='#aaaaaa', lw=0, ms=4,
           markerfacecolor='#aaaaaa', alpha=1.0,  label='Later frames'),
]


def build_figure(row_subset, figsize):
    n = len(row_subset)
    fig = plt.figure(figsize=figsize)
    fig.suptitle(TITLE, fontsize=9, fontweight='bold', y=0.99)
    fig.text(0.5, 0.965, SUBTITLE, ha='center', va='top', fontsize=7, color='#444444')

    gs = gridspec.GridSpec(n, 2,
                           hspace=0.10, wspace=0.06,
                           top=0.87, bottom=0.04,
                           left=0.12, right=0.97)

    for ri, row in enumerate(row_subset):
        for ci, side in enumerate(['cued', 'uncued']):
            ax = fig.add_subplot(gs[ri, ci])
            draw_panel(ax, **row[side], cued=(side == 'cued'),
                       row_label=row['label'] if ci == 0 else '',
                       col_title=('CUED' if ci == 0 else 'UNCUED') if ri == 0 else '')

    fig.legend(handles=LEG_HANDLES, loc='upper right', fontsize=8,
               bbox_to_anchor=(0.97, 0.94), framealpha=0.9)
    return fig


# ── Save ──────────────────────────────────────────────────────────────────────
BASE = os.path.normpath(os.path.join(os.path.dirname(__file__), '../../Agents/Figures'))
os.makedirs(BASE, exist_ok=True)

fig_all = build_figure(ROWS, figsize=(10, 20))
fig_all.savefig(os.path.join(BASE, 'decoupled_N_traces.png'), dpi=150, bbox_inches='tight')
plt.close(fig_all)
print('Saved PNG')

with PdfPages(os.path.join(BASE, 'decoupled_N_traces.pdf')) as pdf:
    for i in range(0, len(ROWS), 2):
        fig_p = build_figure(ROWS[i:i+2], figsize=(8.5, 11))
        pdf.savefig(fig_p, bbox_inches='tight')
        plt.close(fig_p)
print(f'Saved PDF: {BASE}/decoupled_N_traces.pdf')
