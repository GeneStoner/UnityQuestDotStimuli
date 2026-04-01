#!/usr/bin/env python3
"""
Dot trajectory trace: dots within circular aperture, past frames accumulated.
Shows a brief window around translation (pre, translation, post).
Phase 1: single panel, one condition.

Filled circles = Near plane, Open circles = Far plane.
Alpha gradient: pre-translation faint -> translation full -> post-translation medium.

Usage:
    python plot_dot_traces.py [--swap N] [--cond CUED] [--heading 0]
           [--pre 10] [--post 10] [--dots_per_field 63] [--seed 42]
           [--dot_size 4] [--dot_size_open 10] [--out dot_trace.png]
"""

import argparse
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# ── Stimulus constants (Exp_DepthSwapCtrl) ─────────────────────────────────────
VIEW_DIST_M    = 2.0
APERTURE_DEG   = 3.5
ROT_DEG_S      = 81.0
TRANS_DEG_S    = 2.26
SIM_HZ         = 75
ONSET          = 56
T_START        = 78
T_END          = 84
TOTAL          = 114

# Derived
METERS_PER_DEG = VIEW_DIST_M * np.tan(np.deg2rad(1.0))
R_APERTURE     = VIEW_DIST_M * np.tan(np.deg2rad(APERTURE_DEG))
ROT_RAD_STEP   = np.deg2rad(ROT_DEG_S / SIM_HZ)   # 1.08 deg per sim step
TRANS_M_STEP   = TRANS_DEG_S * METERS_PER_DEG / SIM_HZ

# Non-coherent: 8 balanced cardinal/diagonal directions, fixed by dot_index % 8
_nc = np.array([[1,0],[1,1],[0,1],[-1,1],[-1,0],[-1,-1],[0,-1],[1,-1]], dtype=float)
NONCOH_DIRS = _nc / np.linalg.norm(_nc, axis=1, keepdims=True)

# Motion kind codes (matches gen_hypothetical_traj.py)
CW, LINEAR, NONCOH, CCW = 1, 2, 3, 4
NEAR, FAR = 1, 2

RED = "#CC3333"


# ── Motion-kind array builder (direct copy of gen_hypothetical_traj.py logic) ──
def build(swap, cued):
    """
    Returns (mt, depth) arrays of shape (TOTAL, 4).
    FieldA(S0,S1)=Far/CW  FieldB(S2,S3)=Near/CCW (delayed onset at ONSET).
    """
    mt    = np.zeros((TOTAL, 4), dtype=int)
    depth = np.zeros((TOTAL, 4), dtype=int)
    for f in range(TOTAL):
        ao  = f >= ONSET
        as_ = f >= T_START
        tr  = T_START <= f < T_END

        m = [CW, CW, CCW if ao else 0, CCW if ao else 0]
        d = [FAR, FAR, NEAR if ao else 0, NEAR if ao else 0]

        if as_:
            if swap == 'ZdA':
                d = [NEAR, FAR, FAR, NEAR]
                if tr:
                    m = [CW, NONCOH, LINEAR, CW] if cued else [LINEAR, CCW, CCW, NONCOH]
                else:
                    m = [CW, CCW, CCW, CW]
            elif swap == 'ZdB':
                d = [FAR, NEAR, NEAR, FAR]
                if tr:
                    m = [CW, NONCOH, LINEAR, CW] if cued else [LINEAR, CCW, CCW, NONCOH]
                else:
                    m = [CW, CCW, CCW, CW]
            else:  # N — no swap
                d = [FAR, FAR, NEAR, NEAR]
                if tr:
                    m = [CW, CW, LINEAR, NONCOH] if cued else [LINEAR, NONCOH, CCW, CCW]
                else:
                    m = [CW, CW, CCW, CCW]

        mt[f]    = m
        depth[f] = d

    return mt, depth


# ── Dot initialisation ─────────────────────────────────────────────────────────
def uniform_disk(n, R, rng):
    u     = rng.uniform(0.0, 1.0, n)
    theta = rng.uniform(0.0, 2 * np.pi, n)
    r     = R * np.sqrt(u)
    return np.column_stack([r * np.cos(theta), r * np.sin(theta)])


# ── Per-step motion helpers ────────────────────────────────────────────────────
def step_rotation(dots, sign):
    """Rigid rotation of all dots around origin by sign * ROT_RAD_STEP."""
    ang = sign * ROT_RAD_STEP
    c, s = np.cos(ang), np.sin(ang)
    rot = np.array([[c, -s], [s, c]])
    dots[:] = dots @ rot.T


def step_translation(dots, heading_rad):
    dots += np.array([np.cos(heading_rad), np.sin(heading_rad)]) * TRANS_M_STEP


def step_noncoh(dots):
    for k in range(len(dots)):
        dots[k] += NONCOH_DIRS[k % 8] * TRANS_M_STEP


def handle_oob(dots, rng):
    """Respawn out-of-bounds dots uniformly within the aperture disk."""
    r2  = (dots ** 2).sum(axis=1)
    oob = r2 > R_APERTURE ** 2
    n   = oob.sum()
    if n:
        u     = rng.uniform(0.0, 1.0, n)
        theta = rng.uniform(0.0, 2 * np.pi, n)
        r     = R_APERTURE * np.sqrt(u)
        dots[oob, 0] = r * np.cos(theta)
        dots[oob, 1] = r * np.sin(theta)


# ── Simulate ───────────────────────────────────────────────────────────────────
def simulate(mt, depth, heading_deg, dots_per_field, seed, pre, post):
    """
    Simulate all frames 0..TOTAL-1.
    Store positions for the window [T_START-pre .. T_END+post-1] inclusive.

    Returns:
        stored  : dict frame -> list of (xy_m: ndarray(N,2), depth_code: int) per subfield
        w_start : first frame of window
        w_end   : last frame of window (inclusive)
    """
    rng = np.random.RandomState(seed)

    # Sub-array sizes: S0,S2 get ceil(dots_per_field/2); S1,S3 get floor
    n_hi = (dots_per_field + 1) // 2
    n_lo = dots_per_field // 2
    n_per_sf = [n_hi, n_lo, n_hi, n_lo]

    dots = [uniform_disk(n_per_sf[sf], R_APERTURE, rng) for sf in range(4)]

    heading_rad = np.deg2rad(heading_deg)
    w_start = T_START - pre
    w_end   = T_END + post - 1   # inclusive

    stored = {}

    for f in range(TOTAL):
        # Capture positions at start of this frame (before stepping)
        if w_start <= f <= w_end:
            stored[f] = [(dots[sf].copy(), int(depth[f, sf])) for sf in range(4)]

        # Step each sub-array
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
            # mk == 0: Field B pre-onset; no motion

            handle_oob(dots[sf], rng)

    return stored, w_start, w_end


# ── Convert metres to degrees of visual angle ──────────────────────────────────
def m_to_deg(pos_m):
    """Shape (N,2) metres -> (N,2) degrees."""
    return np.rad2deg(np.arctan(pos_m / VIEW_DIST_M))


# ── Alpha schedule ─────────────────────────────────────────────────────────────
def frame_alpha(f, w_start, w_end):
    if T_START <= f < T_END:
        return 1.0
    elif f < T_START:
        frac = (f - w_start) / max(1, T_START - w_start)
        return 0.08 + frac * 0.27         # 0.08 -> 0.35
    else:
        frac = (f - T_END) / max(1, w_end - T_END + 1)
        return 0.50 - frac * 0.35         # 0.50 -> 0.15


# ── Plot ───────────────────────────────────────────────────────────────────────
def plot_traces(stored, w_start, w_end, swap, cued, heading_deg,
                s_filled, s_open, out):

    fig, ax = plt.subplots(figsize=(6, 6))
    ax.set_aspect('equal')

    # Aperture boundary
    aperture_circle = plt.Circle((0, 0), APERTURE_DEG,
                                 fill=False, color='0.72', lw=1.0, zorder=0)
    ax.add_patch(aperture_circle)

    # Draw dots frame by frame (older frames first so newer sit on top)
    for f in sorted(stored.keys()):
        alpha = frame_alpha(f, w_start, w_end)
        for pos_m, d_code in stored[f]:
            if d_code == 0:
                continue   # Field B pre-onset (invisible)
            pos_deg = m_to_deg(pos_m)
            x, y = pos_deg[:, 0], pos_deg[:, 1]

            if d_code == NEAR:
                ax.scatter(x, y, s=s_filled, c=RED,
                           alpha=alpha, linewidths=0, zorder=2)
            else:  # FAR
                ax.scatter(x, y, s=s_open, facecolors='none',
                           edgecolors=RED, alpha=alpha,
                           linewidths=0.6, zorder=2)

    # Translation direction arrow
    arrow_r = APERTURE_DEG * 0.28
    hr = np.deg2rad(heading_deg)
    ax.annotate('', xy=(arrow_r * np.cos(hr), arrow_r * np.sin(hr)),
                xytext=(0, 0),
                arrowprops=dict(arrowstyle='->', color='navy', lw=1.8),
                zorder=6)

    # Axis limits & labels
    lim = APERTURE_DEG * 1.18
    ax.set_xlim(-lim, lim)
    ax.set_ylim(-lim, lim)
    ax.set_xlabel('Horizontal (deg)', fontsize=9)
    ax.set_ylabel('Vertical (deg)', fontsize=9)
    ax.tick_params(labelsize=8)

    cued_str = 'CUED' if cued else 'UNCUED'
    n_pre  = T_START - w_start
    n_post = w_end - T_END + 1
    ax.set_title(
        f'Swap={swap}  {cued_str}  heading={heading_deg:.0f}°\n'
        f'Frames {w_start}–{w_end}  '
        f'(pre={n_pre} | trans=6 | post={n_post})\n'
        f'Filled=Near  Open=Far  '
        f'Alpha: pre↗trans↘post  tStart=f{T_START} tEnd=f{T_END}',
        fontsize=8, loc='left'
    )

    # Legend
    from matplotlib.lines import Line2D
    legend_handles = [
        Line2D([0], [0], marker='o', color='w', markerfacecolor=RED,
               markersize=6, ls='None', label='Near (filled)'),
        Line2D([0], [0], marker='o', color='w', markeredgecolor=RED,
               markerfacecolor='none', markersize=7, markeredgewidth=0.8,
               ls='None', label='Far (open)'),
        Line2D([0], [0], color='navy', lw=1.5, label=f'Heading {heading_deg:.0f}°'),
    ]
    ax.legend(handles=legend_handles, loc='lower right', fontsize=7)

    plt.tight_layout()
    plt.savefig(out, dpi=200, bbox_inches='tight')
    plt.close()
    print(f'Wrote: {out}')


# ── Entry point ────────────────────────────────────────────────────────────────
def main():
    p = argparse.ArgumentParser(
        description='Accumulated dot trajectory traces within circular aperture')
    p.add_argument('--swap',           default='N',    choices=['N', 'ZdA', 'ZdB'],
                   help='Swap condition (default: N)')
    p.add_argument('--cond',           default='CUED', choices=['CUED', 'UNCUED'],
                   help='Cueing condition (default: CUED)')
    p.add_argument('--heading',        type=float, default=0.0,
                   help='Translation heading in degrees (default: 0)')
    p.add_argument('--pre',            type=int,   default=10,
                   help='Frames before translation window (default: 10)')
    p.add_argument('--post',           type=int,   default=10,
                   help='Frames after translation window (default: 10)')
    p.add_argument('--dots_per_field', type=int,   default=63,
                   help='Dots per field (default: 63)')
    p.add_argument('--seed',           type=int,   default=42,
                   help='RNG seed for initial dot placement (default: 42)')
    p.add_argument('--dot_size',       type=float, default=4.0,
                   help='Marker size² for filled (Near) dots (default: 4)')
    p.add_argument('--dot_size_open',  type=float, default=10.0,
                   help='Marker size² for open (Far) dots (default: 10)')
    p.add_argument('--out',            default='dot_trace.png',
                   help='Output filename (default: dot_trace.png)')
    args = p.parse_args()

    cued = (args.cond == 'CUED')
    mt, depth = build(args.swap, cued)

    stored, w_start, w_end = simulate(
        mt, depth, args.heading, args.dots_per_field, args.seed,
        args.pre, args.post
    )

    plot_traces(
        stored, w_start, w_end,
        args.swap, cued, args.heading,
        args.dot_size, args.dot_size_open,
        args.out
    )


if __name__ == '__main__':
    main()
