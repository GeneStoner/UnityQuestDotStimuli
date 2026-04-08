#!/usr/bin/env python3
"""
Dot trajectory traces for Exp_DecoupledDots_005m.

Circular aperture, accumulated dot positions across a window around translation.
  Filled dots = Near plane   Open dots = Far plane
  Red dots    = Field B      Green dots = Field A
  (colors can swap at tStart for C / CZ conditions)
  Alpha gradient: pre-translation faint → translation full → post-translation medium

Single-panel usage (default):
    python plot_dot_traces_decoupled.py
    python plot_dot_traces_decoupled.py --swap Z --cond CUED --depth NEAR --heading 45

Multi-panel (2 rows CUED/UNCUED × 4 cols N/C/Z/CZ):
    python plot_dot_traces_decoupled.py --multi [--depth NEAR]

Arguments:
    --swap    N | C | Z | CZ          (default: N)
    --cond    CUED | UNCUED           (default: CUED)
    --depth   NEAR | FAR              delayed field depth (default: NEAR)
    --heading float                   translation heading degrees (default: 0)
    --pre     int                     frames before translation (default: 6)
    --post    int                     frames after translation  (default: 6)
    --dots_per_field int              (default: 63)
    --seed    int                     (default: 42)
    --dot_size      float             filled dot marker size² (default: 6)
    --dot_size_open float             open dot marker size²   (default: 14)
    --multi                           produce 2×4 grid figure
    --out     filename                (default: dot_trace_decoupled.png)
"""

import argparse
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.lines import Line2D

# ── Stimulus constants ──────────────────────────────────────────────────────────
VIEW_DIST_M    = 2.0
APERTURE_DEG   = 3.5
ROT_DEG_S      = 81.0
TRANS_DEG_S    = 2.26
SIM_HZ         = 75
ONSET          = 56
T_START        = 78
T_END          = 84
TOTAL          = 114

METERS_PER_DEG = VIEW_DIST_M * np.tan(np.deg2rad(1.0))
R_APERTURE     = VIEW_DIST_M * np.tan(np.deg2rad(APERTURE_DEG))
ROT_RAD_STEP   = np.deg2rad(ROT_DEG_S / SIM_HZ)
TRANS_M_STEP   = TRANS_DEG_S * METERS_PER_DEG / SIM_HZ

_nc = np.array([[1,0],[1,1],[0,1],[-1,1],[-1,0],[-1,-1],[0,-1],[1,-1]], dtype=float)
NONCOH_DIRS = _nc / np.linalg.norm(_nc, axis=1, keepdims=True)

CW, LINEAR, NONCOH, CCW = 1, 2, 3, 4
NEAR, FAR = 1, 2
F_RED, F_GRN = 1, 2

COL_RED = "#CC3333"
COL_GRN = "#228B22"
FIELD_COLORS = {F_RED: COL_RED, F_GRN: COL_GRN}

SWAP_COLORS = {'N': '#444444', 'C': '#CC6600', 'Z': '#116688', 'CZ': '#553388'}


# ── Motion / depth / color array builder ───────────────────────────────────────
def build(swap, delayed_depth, cued):
    """
    swap          : 'N', 'C', 'Z', 'CZ'
    delayed_depth : NEAR or FAR  — depth plane of Field B (delayed-onset field)
    cued          : True  = Field B (delayed) translates
                    False = Field A (always-on) translates

    Field A = always-on, default color Green (F_GRN), default depth = opposite of delayed
    Field B = delayed onset at frame ONSET, default color Red  (F_RED)

    Returns mt[TOTAL,4], dep[TOTAL,4], fcol[TOTAL,4]
      Subfields: S0(coh,A), S1(noise,A), S2(coh,B), S3(noise,B)
    """
    a_dep = FAR  if delayed_depth == NEAR else NEAR   # Field A default depth
    b_dep = delayed_depth                              # Field B default depth

    color_swap = swap in ('C', 'CZ')
    depth_swap = swap in ('Z', 'CZ')

    mt   = np.zeros((TOTAL, 4), dtype=int)
    dep  = np.zeros((TOTAL, 4), dtype=int)
    fcol = np.zeros((TOTAL, 4), dtype=int)

    for f in range(TOTAL):
        ao  = f >= ONSET
        as_ = f >= T_START
        tr  = T_START <= f < T_END

        # Field colors — swap at tStart if colorSwap
        a_col = F_RED if (color_swap and as_) else F_GRN
        b_col = F_GRN if (color_swap and as_) else F_RED

        # Depth planes — swap at tStart if depthSwap
        a_d = b_dep if (depth_swap and as_) else a_dep
        b_d = a_dep if (depth_swap and as_) else b_dep

        # Motions (RotA: Field A=CW, Field B=CCW)
        if not as_:
            m = [CW, CW, CCW if ao else 0, CCW if ao else 0]
        elif tr:
            if cued:    # Field B (S2/S3) translates
                m = [CW, CW, LINEAR, NONCOH]
            else:       # Field A (S0/S1) translates
                m = [LINEAR, NONCOH, CCW, CCW]
        else:
            m = [CW, CW, CCW, CCW]

        mt[f]   = m
        dep[f]  = [a_d,  a_d,
                   b_d if ao else 0,
                   b_d if ao else 0]
        fcol[f] = [a_col, a_col,
                   b_col if ao else 0,
                   b_col if ao else 0]

    return mt, dep, fcol


# ── Simulation ─────────────────────────────────────────────────────────────────
def uniform_disk(n, R, rng):
    u     = rng.uniform(0.0, 1.0, n)
    theta = rng.uniform(0.0, 2 * np.pi, n)
    r     = R * np.sqrt(u)
    return np.column_stack([r * np.cos(theta), r * np.sin(theta)])

def step_rotation(dots, sign):
    ang = sign * ROT_RAD_STEP
    c, s = np.cos(ang), np.sin(ang)
    dots[:] = dots @ np.array([[c, -s], [s, c]]).T

def step_translation(dots, heading_rad):
    dots += np.array([np.cos(heading_rad), np.sin(heading_rad)]) * TRANS_M_STEP

def step_noncoh(dots):
    for k in range(len(dots)):
        dots[k] += NONCOH_DIRS[k % 8] * TRANS_M_STEP

def handle_oob(dots, rng):
    r2  = (dots ** 2).sum(axis=1)
    oob = r2 > R_APERTURE ** 2
    n   = oob.sum()
    if n:
        u     = rng.uniform(0.0, 1.0, n)
        theta = rng.uniform(0.0, 2 * np.pi, n)
        r     = R_APERTURE * np.sqrt(u)
        dots[oob, 0] = r * np.cos(theta)
        dots[oob, 1] = r * np.sin(theta)

def simulate(mt, dep, fcol, heading_deg, dots_per_field, seed, pre, post):
    """
    Returns stored[frame] = list of (xy_m, depth_code, field_color_code) per subfield,
    plus w_start and w_end (inclusive window bounds).
    """
    rng = np.random.RandomState(seed)

    n_hi = (dots_per_field + 1) // 2
    n_lo = dots_per_field // 2
    n_per_sf = [n_hi, n_lo, n_hi, n_lo]

    dots = [uniform_disk(n_per_sf[sf], R_APERTURE, rng) for sf in range(4)]

    heading_rad = np.deg2rad(heading_deg)
    w_start = T_START - pre
    w_end   = T_END + post - 1

    stored = {}
    for f in range(TOTAL):
        if w_start <= f <= w_end:
            stored[f] = [(dots[sf].copy(), int(dep[f, sf]), int(fcol[f, sf]))
                         for sf in range(4)]
        for sf in range(4):
            mk = mt[f, sf]
            if mk == CW:
                step_rotation(dots[sf], -1)
            elif mk == CCW:
                step_rotation(dots[sf], +1)
            elif mk == LINEAR:
                step_translation(dots[sf], heading_rad)
            elif mk == NONCOH:
                step_noncoh(dots[sf])
            handle_oob(dots[sf], rng)

    return stored, w_start, w_end


# ── Alpha schedule ─────────────────────────────────────────────────────────────
def frame_alpha(f, w_start, w_end):
    if T_START <= f < T_END:
        return 1.0
    elif f < T_START:
        frac = (f - w_start) / max(1, T_START - w_start)
        return 0.08 + frac * 0.27    # 0.08 → 0.35
    else:
        frac = (f - T_END) / max(1, w_end - T_END + 1)
        return 0.50 - frac * 0.35    # 0.50 → 0.15


# ── Single-panel plot ──────────────────────────────────────────────────────────
def m_to_deg(pos_m):
    return np.rad2deg(np.arctan(pos_m / VIEW_DIST_M))

def draw_aperture(ax):
    aperture_circle = plt.Circle((0, 0), APERTURE_DEG,
                                 fill=False, color='0.72', lw=1.0, zorder=0)
    ax.add_patch(aperture_circle)

def draw_dots(ax, stored, w_start, w_end, s_filled, s_open):
    for f in sorted(stored.keys()):
        alpha = frame_alpha(f, w_start, w_end)
        for pos_m, d_code, fc_code in stored[f]:
            if d_code == 0 or fc_code == 0:
                continue
            pos_deg = m_to_deg(pos_m)
            x, y    = pos_deg[:, 0], pos_deg[:, 1]
            col     = FIELD_COLORS[fc_code]

            if d_code == NEAR:
                ax.scatter(x, y, s=s_filled, c=col,
                           alpha=alpha, linewidths=0, zorder=2)
            else:   # FAR
                ax.scatter(x, y, s=s_open, facecolors='none',
                           edgecolors=col, alpha=alpha,
                           linewidths=0.7, zorder=2)

def draw_arrow(ax, heading_deg):
    arrow_r = APERTURE_DEG * 0.28
    hr = np.deg2rad(heading_deg)
    ax.annotate('', xy=(arrow_r * np.cos(hr), arrow_r * np.sin(hr)),
                xytext=(0, 0),
                arrowprops=dict(arrowstyle='->', color='navy', lw=1.8),
                zorder=6)

def style_aperture_ax(ax, heading_deg):
    lim = APERTURE_DEG * 1.18
    ax.set_xlim(-lim, lim)
    ax.set_ylim(-lim, lim)
    ax.set_aspect('equal')
    ax.set_xlabel('Horizontal (deg)', fontsize=8)
    ax.set_ylabel('Vertical (deg)', fontsize=8)
    ax.tick_params(labelsize=7.5)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

def make_legend_handles():
    return [
        Line2D([0],[0], marker='o', color='w', markerfacecolor=COL_RED,
               markersize=7, ls='None', label='Near · Field B (Red default)'),
        Line2D([0],[0], marker='o', color='w', markerfacecolor=COL_GRN,
               markersize=7, ls='None', label='Near · Field A (Green default)'),
        Line2D([0],[0], marker='o', color='w', markeredgecolor=COL_RED,
               markerfacecolor='none', markersize=8, markeredgewidth=0.9,
               ls='None', label='Far · Field B'),
        Line2D([0],[0], marker='o', color='w', markeredgecolor=COL_GRN,
               markerfacecolor='none', markersize=8, markeredgewidth=0.9,
               ls='None', label='Far · Field A'),
        Line2D([0],[0], color='navy', lw=1.5, label='Translation heading'),
    ]


# ── Single-panel figure ────────────────────────────────────────────────────────
def single_panel(args):
    swap    = args.swap
    cued    = (args.cond == 'CUED')
    ddep    = NEAR if args.depth == 'NEAR' else FAR
    heading = args.heading

    mt, dep, fcol = build(swap, ddep, cued)
    stored, w_start, w_end = simulate(
        mt, dep, fcol, heading, args.dots_per_field, args.seed, args.pre, args.post)

    fig, ax = plt.subplots(figsize=(6, 6.5))
    fig.patch.set_facecolor('white')

    draw_aperture(ax)
    draw_dots(ax, stored, w_start, w_end, args.dot_size, args.dot_size_open)
    draw_arrow(ax, heading)
    style_aperture_ax(ax, heading)

    n_pre  = T_START - w_start
    n_post = w_end - T_END + 1
    cued_str = 'CUED' if cued else 'UNCUED'
    dep_str  = 'Near' if ddep == NEAR else 'Far'
    ax.set_title(
        f'Swap={swap}  {cued_str}  Delayed={dep_str}  heading={heading:.0f}°\n'
        f'Frames {w_start}–{w_end}  (pre={n_pre} | trans=6 | post={n_post})\n'
        f'Filled=Near  Open=Far  '
        f'Red=FieldB  Green=FieldA  '
        f'Alpha: pre↗ trans↘ post',
        fontsize=8, loc='left')

    ax.legend(handles=make_legend_handles(), loc='lower right', fontsize=7,
              framealpha=0.9)

    plt.tight_layout()
    plt.savefig(args.out, dpi=200, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f'Wrote: {args.out}')


# ── Multi-panel figure (2 rows CUED/UNCUED × 4 cols N/C/Z/CZ) ─────────────────
def multi_panel(args):
    ddep     = NEAR if args.depth == 'NEAR' else FAR
    heading  = args.heading
    dep_str  = 'Near' if ddep == NEAR else 'Far'

    CONDS  = [(True, 'CUED'), (False, 'UNCUED')]
    SWAPS  = ['N', 'C', 'Z', 'CZ']
    SWAP_FULL = {
        'N':  'N — no swap',
        'C':  'C — color swap\n(field colors swap at tStart)',
        'Z':  'Z — depth swap\n(depth planes swap at tStart)',
        'CZ': 'CZ — color + depth\n(both swap at tStart)',
    }

    fig = plt.figure(figsize=(16, 9))
    fig.patch.set_facecolor('white')
    fig.suptitle(
        f'Exp_DecoupledDots_005m — Dot traces in aperture\n'
        f'Delayed field (Field B) depth = {dep_str}  ·  heading = {heading:.0f}°  ·  '
        f'pre={args.pre} | trans=6 | post={args.post} frames  ·  '
        f'Filled=Near  Open=Far  Red=FieldB  Green=FieldA  '
        f'(colors swap at tStart for C/CZ)',
        fontsize=10, fontweight='bold', y=1.01)

    gs = gridspec.GridSpec(2, 4, left=0.05, right=0.98,
                           top=0.93, bottom=0.10,
                           hspace=0.35, wspace=0.25)

    for ri, (cued, cued_str) in enumerate(CONDS):
        for ci, swap in enumerate(SWAPS):
            ax = fig.add_subplot(gs[ri, ci])

            mt, dep, fcol = build(swap, ddep, cued)
            stored, w_start, w_end = simulate(
                mt, dep, fcol, heading,
                args.dots_per_field, args.seed,
                args.pre, args.post)

            draw_aperture(ax)
            draw_dots(ax, stored, w_start, w_end, args.dot_size, args.dot_size_open)
            draw_arrow(ax, heading)
            style_aperture_ax(ax, heading)

            # Panel title
            sc = SWAP_COLORS[swap]
            ax.set_title(f'{cued_str} · {swap}', fontsize=9, fontweight='bold',
                         color=sc, pad=5)

            # Row label (left column)
            if ci == 0:
                from matplotlib.colors import to_rgba
                row_col = '#1565C0' if cued else '#E65100'
                ax.set_ylabel(
                    f'{cued_str}\n(delayed field {"translates" if cued else "rotates"})\n\nVertical (deg)',
                    fontsize=8, fontweight='bold', color=row_col)
            else:
                ax.set_ylabel('Vertical (deg)', fontsize=7.5)

            # Column header (top row)
            if ri == 0:
                ax.set_title(
                    SWAP_FULL[swap] + f'\n{cued_str} · delayed={dep_str}',
                    fontsize=8.5, fontweight='bold', color=sc, pad=8)

    # Legend
    fig.legend(handles=make_legend_handles(), loc='lower center', ncol=5,
               fontsize=8.5, framealpha=0.95, bbox_to_anchor=(0.5, 0.01))

    out = args.out if args.out != 'dot_trace_decoupled.png' else \
          f'dot_trace_decoupled_multi_{dep_str.lower()}.png'
    plt.savefig(out, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f'Wrote: {out}')


# ── Entry point ────────────────────────────────────────────────────────────────
def main():
    p = argparse.ArgumentParser(
        description='Accumulated dot trajectory traces — DecoupledDots N/C/Z/CZ')
    p.add_argument('--swap',           default='N',   choices=['N','C','Z','CZ'])
    p.add_argument('--cond',           default='CUED', choices=['CUED','UNCUED'])
    p.add_argument('--depth',          default='NEAR', choices=['NEAR','FAR'],
                   help='Delayed field (Field B) depth plane')
    p.add_argument('--heading',        type=float, default=0.0)
    p.add_argument('--pre',            type=int,   default=6)
    p.add_argument('--post',           type=int,   default=6)
    p.add_argument('--dots_per_field', type=int,   default=63)
    p.add_argument('--seed',           type=int,   default=42)
    p.add_argument('--dot_size',       type=float, default=6.0)
    p.add_argument('--dot_size_open',  type=float, default=14.0)
    p.add_argument('--multi',          action='store_true',
                   help='Produce 2×4 grid (CUED/UNCUED × N/C/Z/CZ)')
    p.add_argument('--out',            default='dot_trace_decoupled.png')
    args = p.parse_args()

    if args.multi:
        multi_panel(args)
    else:
        single_panel(args)


if __name__ == '__main__':
    main()
