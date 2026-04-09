#!/usr/bin/env python3
"""
Trajectory figure for Exp_DecoupledDots_005m — Stoner & Blanc line style.

Line convention (follows Stoner & Blanc 2010):
  Field A (always-on, CW):  SOLID lines
  Field B (delayed, CCW):   DASHED lines
  Coherent subfield: heavy line;  Noise subfield: light line.
  NONCOH plotted at same y as LINEAR (T) — no separate T(n) label.

Layout:
  Rows : N, C, Z, CZ          (swap type — row label on left)
  Cols : Dot✓·Near, Dot✗·Near, Dot✓·Far, Dot✗·Far
         (CUED/UNCUED paired per depth, matching per-swap figure convention)

Per panel:
  Title (large rectangle, centered): Dot✓/✗  Depth✓/✗  Color✓/✗
  Small rectangle on motion track, above translation window: Color/Dir/Depth

Output: Agents/Figures/decoupled_dots_traj.png / .pdf
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
    '~/Projects/ObjectBasedAttention/VRDots/Agents/Figures/decoupled_dots_traj.png')
OUT_PDF  = os.path.expanduser(
    '~/Projects/ObjectBasedAttention/VRDots/Agents/Figures/decoupled_dots_traj.pdf')

# ── Timing (frames at 75 Hz) ──────────────────────────────────────────────
ONSET   = 56
T_START = 78
T_END   = 84
T_MID   = (T_START + T_END) / 2
TOTAL   = 114

# Motion codes — NONCOH plotted at LINEAR y-value (no separate label)
CW, LINEAR, NONCOH, CCW = 1, 2, 3, 4
PLOT_Y = {CW: CW, LINEAR: LINEAR, NONCOH: LINEAR, CCW: CCW}

# Depth codes
NEAR, FAR = 1, 2

# Field color codes
F_RED, F_GRN = 1, 2
FIELD_COLOR = {F_RED: '#CC3333', F_GRN: '#228B22', 0: '#DDDDDD'}
DEPTH_COLOR = {NEAR: '#AA2222', FAR: '#116611'}

# Line weights: heavy=coherent, light=noise
LW = {0: 1.8, 1: 0.9, 2: 1.8, 3: 0.9}

SWAP_COLORS = {'N': '#444444', 'C': '#CC6600', 'Z': '#116688', 'CZ': '#553388'}
C_DOT_CUE   = '#1a3a8b'
C_DOT_UNCUE = '#884400'


def translator_info(swap, cued, ddep):
    """
    Compute translator properties at tStart and cueing factor checkmarks.

    Returns
    -------
    trans_label : str   e.g. 'Grn/CW/Far'
    dot_s, dep_s, col_s : str  '✓' or '✗'
    """
    a_dep       = FAR if ddep == NEAR else NEAR
    color_swap  = swap in ('C', 'CZ')
    depth_swap  = swap in ('Z', 'CZ')

    if cued:
        col  = 'Grn' if color_swap else 'Red'
        dirn = 'CCW'
        dep  = a_dep if depth_swap else ddep
    else:
        col  = 'Red' if color_swap else 'Grn'
        dirn = 'CW'
        dep  = ddep if depth_swap else a_dep

    dep_str     = 'Near' if dep == NEAR else 'Far'
    trans_label = f'{col}/{dirn}/{dep_str}'

    dot_s = '✓' if cued else '✗'
    dep_ok = (not depth_swap) if cued else depth_swap
    dep_s  = '✓' if dep_ok else '✗'
    col_ok = (not color_swap) if cued else color_swap
    col_s  = '✓' if col_ok else '✗'

    return trans_label, dot_s, dep_s, col_s


def build(swap, delayed_depth, cued):
    """
    Returns mt[TOTAL,4], dep[TOTAL,4], fcol[TOTAL,4]
    """
    a_dep = FAR if delayed_depth == NEAR else NEAR
    b_dep = delayed_depth

    color_swap = swap in ('C', 'CZ')
    depth_swap = swap in ('Z', 'CZ')

    A_COL_DEFAULT = F_GRN
    B_COL_DEFAULT = F_RED

    mt   = np.zeros((TOTAL, 4), dtype=int)
    dep  = np.zeros((TOTAL, 4), dtype=int)
    fcol = np.zeros((TOTAL, 4), dtype=int)

    for f in range(TOTAL):
        ao  = f >= ONSET
        as_ = f >= T_START
        tr  = T_START <= f < T_END

        a_col = B_COL_DEFAULT if (color_swap and as_) else A_COL_DEFAULT
        b_col = A_COL_DEFAULT if (color_swap and as_) else B_COL_DEFAULT

        a_d = b_dep if (depth_swap and as_) else a_dep
        b_d = a_dep if (depth_swap and as_) else b_dep

        if not as_:
            m = [CW, CW,
                 CCW if ao else 0,
                 CCW if ao else 0]
        elif tr:
            if cued:
                m = [CW, CW, LINEAR, NONCOH]
            else:
                m = [LINEAR, NONCOH, CCW, CCW]
        else:
            m = [CW, CW, CCW, CCW]

        mt[f]   = m
        dep[f]  = [a_d, a_d,
                   b_d if ao else 0,
                   b_d if ao else 0]
        fcol[f] = [a_col, a_col,
                   b_col if ao else 0,
                   b_col if ao else 0]

    return mt, dep, fcol


def plot_panel(ax_mt, ax_dep, mt, dep, fcol, swap, cued, delayed_depth):
    """Draw one panel: motion track + depth track + annotations."""

    for si in range(4):
        ls = '--' if si >= 2 else '-'
        lw = LW[si]

        frames = [f for f in range(TOTAL)
                  if fcol[f, si] != 0 and mt[f, si] != 0]
        if not frames:
            continue

        # Map NONCOH → LINEAR y-value for plotting
        def yval(f, si=si):
            return PLOT_Y[mt[f, si]]

        seg_start = frames[0]
        seg_col_m = FIELD_COLOR[fcol[frames[0], si]]
        seg_col_d = DEPTH_COLOR[dep[frames[0], si]]

        for f in frames:
            new_col_m = FIELD_COLOR[fcol[f, si]]
            new_col_d = DEPTH_COLOR[dep[f, si]]
            if new_col_m != seg_col_m or new_col_d != seg_col_d:
                seg_frames = [x for x in frames if seg_start <= x < f]
                if seg_frames:
                    ax_mt.plot(seg_frames, [yval(x) for x in seg_frames],
                               color=seg_col_m, ls=ls, lw=lw,
                               solid_capstyle='round', zorder=4)
                    ax_dep.plot(seg_frames, [dep[x, si] for x in seg_frames],
                                color=seg_col_d, ls=ls, lw=lw,
                                solid_capstyle='round', zorder=4)
                seg_start = f
                seg_col_m = new_col_m
                seg_col_d = new_col_d

        seg_frames = [x for x in frames if x >= seg_start]
        if seg_frames:
            ax_mt.plot(seg_frames, [yval(x) for x in seg_frames],
                       color=seg_col_m, ls=ls, lw=lw,
                       solid_capstyle='round', zorder=4)
            ax_dep.plot(seg_frames, [dep[x, si] for x in seg_frames],
                        color=seg_col_d, ls=ls, lw=lw,
                        solid_capstyle='round', zorder=4)

    # Phase markers
    for ax in (ax_mt, ax_dep):
        ax.axvspan(T_START, T_END, alpha=0.12, color='steelblue', zorder=1)
        ax.axvline(ONSET,   color='#CCCCCC', lw=0.7, ls=':', zorder=2)
        ax.axvline(T_START, color='#6688AA', lw=0.8, ls='--', zorder=2)

    # Translator depth band
    if cued:
        trans_dep = (FAR if (swap in ('Z', 'CZ')) else delayed_depth) \
                    if delayed_depth == NEAR else \
                    (NEAR if (swap in ('Z', 'CZ')) else delayed_depth)
    else:
        a_dep_default = FAR if delayed_depth == NEAR else NEAR
        trans_dep = delayed_depth if (swap in ('Z', 'CZ')) else a_dep_default
    ax_dep.axhspan(trans_dep - 0.40, trans_dep + 0.40,
                   alpha=0.18, color='gold', zorder=0)

    # ── Translator label: small rectangle above translation window ─────────
    trans_label, dot_s, dep_s, col_s = translator_info(swap, cued, delayed_depth)
    ax_mt.text(T_MID, 4.55, trans_label,
               ha='center', va='bottom', fontsize=4.5,
               color='#111111', clip_on=False,
               bbox=dict(boxstyle='round,pad=0.25', facecolor='#f8f8f8',
                         edgecolor='#999999', lw=0.6))

    # Motion axis — no T(n) label; NONCOH maps to LINEAR y
    ax_mt.set_yticks([CW, LINEAR, CCW])
    ax_mt.set_yticklabels(['CW', 'T', 'CCW'], fontsize=5)
    ax_mt.set_ylim(0.4, 5.0)   # extra headroom for translator label
    ax_mt.tick_params(axis='x', labelbottom=False)
    ax_mt.tick_params(axis='y', labelsize=5, length=2)
    ax_mt.set_xlim(-2, TOTAL + 1)

    # Depth axis
    ax_dep.set_yticks([NEAR, FAR])
    ax_dep.set_yticklabels(['Near', 'Far'], fontsize=5)
    ax_dep.set_ylim(0.4, 2.6)
    ax_dep.set_xlabel('Frame', fontsize=5)
    ax_dep.tick_params(axis='both', labelsize=5, length=2)
    ax_dep.set_xlim(-2, TOTAL + 1)

    for ax in (ax_mt, ax_dep):
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)


# ── Layout ────────────────────────────────────────────────────────────────
# Cols: Dot✓-Near, Dot✗-Near, Dot✓-Far, Dot✗-Far
# (CUED/UNCUED paired per depth — matches per-swap figure convention)

COL_DEFS = [
    (True,  NEAR),   # Dot✓ · Near
    (False, NEAR),   # Dot✗ · Near
    (True,  FAR),    # Dot✓ · Far
    (False, FAR),    # Dot✗ · Far
]
ROW_SWAPS = ['N', 'C', 'Z', 'CZ']

COL_HEADERS = [
    'Dot✓\nDel=Red/CCW/Near',
    'Dot✗\nDel=Red/CCW/Near',
    'Dot✓\nDel=Red/CCW/Far',
    'Dot✗\nDel=Red/CCW/Far',
]
ROW_LABELS = {
    'N':  'N\nNo swap',
    'C':  'C\nColor swap\nat tStart',
    'Z':  'Z\nDepth swap\nat tStart',
    'CZ': 'CZ\nColor+Depth\nat tStart',
}

fig = plt.figure(figsize=(20, 16))
fig.patch.set_facecolor('white')
fig.suptitle(
    'Exp_DecoupledDots_005m — Trajectories\n'
    'Field B (delayed onset) = Red dashed (default)  ·  '
    'Field A (always-on) = Green solid (default)  ·  linkDepthColor=0\n'
    'Solid = Field A (CW)  ·  Dashed = Field B (CCW)  ·  '
    'Heavy = coherent subfield  ·  Light = noise subfield\n'
    'Title box: Dot / Depth / Color cueing (✓/✗)  ·  '
    'Small box above translation: translator Color/Dir/Depth at tStart  ·  '
    'Gold = translator depth plane  ·  Blue = translation window',
    fontsize=8.5, y=1.01, va='bottom')

outer = gridspec.GridSpec(4, 4, hspace=1.05, wspace=0.38,
                          left=0.09, right=0.99, top=0.93, bottom=0.06)

for ri, swap in enumerate(ROW_SWAPS):
    for ci, (cued, ddep) in enumerate(COL_DEFS):

        inner = gridspec.GridSpecFromSubplotSpec(
            2, 1, subplot_spec=outer[ri, ci],
            height_ratios=[3, 1.5], hspace=0.06)

        ax_mt  = fig.add_subplot(inner[0])
        ax_dep = fig.add_subplot(inner[1], sharex=ax_mt)

        mt, dep, fcol = build(swap, ddep, cued)

        # ── Panel title: Dot/Depth/Color cueing triad in rectangle ────────
        trans_label, dot_s, dep_s, col_s = translator_info(swap, cued, ddep)
        cueing_title = f'Dot{dot_s}   Depth{dep_s}   Color{col_s}'
        cc = C_DOT_CUE if cued else C_DOT_UNCUE
        ax_mt.set_title(cueing_title, fontsize=6.5, pad=5, color=cc,
                        fontweight='bold',
                        bbox=dict(boxstyle='round,pad=0.35',
                                  facecolor='#f0f4ff' if cued else '#fff4e8',
                                  edgecolor=cc, lw=0.8))

        plot_panel(ax_mt, ax_dep, mt, dep, fcol, swap, cued, ddep)

        # Row labels (leftmost column only)
        if ci == 0:
            sc = SWAP_COLORS[swap]
            ax_mt.set_ylabel(ROW_LABELS[swap] + '\n\nMotion',
                             fontsize=6, fontweight='bold', color=sc,
                             labelpad=4)
        else:
            ax_mt.set_ylabel('Motion', fontsize=5)
        ax_dep.set_ylabel('Depth', fontsize=5)

        # Column headers (top row only)
        if ri == 0:
            ax_mt.set_title(COL_HEADERS[ci] + '\n' + cueing_title,
                            fontsize=6.5, fontweight='bold', pad=14, color=cc,
                            bbox=dict(boxstyle='round,pad=0.35',
                                      facecolor='#f0f4ff' if cued else '#fff4e8',
                                      edgecolor=cc, lw=0.8))

# ── Legend ────────────────────────────────────────────────────────────────
legend_handles = [
    Line2D([0],[0], color='#228B22', ls='-',  lw=1.8,
           label='S0  Field A · coh  (solid heavy, default Green)'),
    Line2D([0],[0], color='#228B22', ls='-',  lw=0.9,
           label='S1  Field A · noise (solid light)'),
    Line2D([0],[0], color='#CC3333', ls='--', lw=1.8,
           label='S2  Field B · coh  (dashed heavy, default Red)'),
    Line2D([0],[0], color='#CC3333', ls='--', lw=0.9,
           label='S3  Field B · noise (dashed light)'),
    Line2D([0],[0], color='gray',    ls='-',  lw=1.2,
           label='After C/CZ swap: Field A→Red solid, Field B→Green dashed'),
    mpatches.Patch(facecolor='gold',      alpha=0.4, edgecolor='#999',
                   label='Translator depth plane'),
    mpatches.Patch(facecolor='steelblue', alpha=0.2, edgecolor='none',
                   label='Translation window'),
    Line2D([0],[0], color='#CCCCCC', lw=0.8, ls=':', label='Field B onset'),
    Line2D([0],[0], color='#6688AA', lw=0.8, ls='--', label='tStart'),
]

fig.legend(handles=legend_handles, loc='lower center', ncol=3,
           fontsize=7, frameon=True, framealpha=0.95,
           edgecolor='#CCC', bbox_to_anchor=(0.5, -0.05))

os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
fig.savefig(OUT_PATH, dpi=150, bbox_inches='tight', facecolor='white')
fig.savefig(OUT_PDF,  bbox_inches='tight', facecolor='white')
print('Saved: {}'.format(OUT_PATH))
print('Saved: {}'.format(OUT_PDF))
