"""
decoupled_stereo_traces.py
==========================
Stereo-projected dot-cloud traces for all four DecoupledDots swap conditions
(N, C, Z, CZ) in CUED and UNCUED arms.

Produces a 2-page PDF:
  Page 1: PRE-FIX  — depth offset along transform.forward pitched ~5° above gaze.
           Artifact visible as upward centroid jump at tStart in Z and CZ conditions.
           N and C conditions: no depth swap at tStart → no artifact.
  Page 2: POST-FIX — depth offset along camera.forward (aligned with gaze).
           All four conditions clean. Tiny radial expansion at tStart in Z/CZ is
           below perceptual threshold.

Layout per page:
  4 rows (N, C, Z, CZ) × 2 columns (CUED / UNCUED)
  Each panel: dot snapshot overlay at 3 key time points
              + centroid trajectory strip below showing Y over time
  Heading = 270° (DOWN) — maximises contrast with upward artifact.

Physics parameters match Exp_DecoupledDots_005m:
  simHz=75, viewDistance=2m, depthOffset=0.05m, apertureRadius=3.5°,
  rotSpeed=81 deg/sec, transSpeed=2.26 deg/sec, onset=56, tStart=78, tEnd=84

Pitch estimate: 5° above gaze (consistent with ~50% UP in Z wrong responses;
artifact/signal ratio = 8.2× per frame at this angle).
"""

import os, collections
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.backends.backend_pdf import PdfPages

OUT_DIR = os.path.join(os.path.dirname(__file__), '../../Agents/SwapPilot/Figures')
OUT_PDF = os.path.join(OUT_DIR, 'decoupled_stereo_traces.pdf')

# ── Parameters ─────────────────────────────────────────────────────────────────
VIEW_DIST_M   = 2.0
DEPTH_OFFS_M  = 0.05
SIM_HZ        = 75
AP_RAD_DEG    = 3.5
ROT_SPD_DEG   = 81.0
TRANS_SPD_DEG = 2.26
ONSET_F       = 56
T_START       = 78
T_END         = 84
TOTAL_FRAMES  = 114
HEADING_DEG   = 270.0     # DOWN — maximises artifact contrast
N_DOTS        = 25        # dots per subfield (kept small for clarity)
PITCH_DEG     = 5.0       # estimated forward-axis pitch (pre-fix scenario)
RNG_SEED      = 7

DEG_TO_M = VIEW_DIST_M * np.tan(np.radians(1.0))

def deg2m(d): return d * DEG_TO_M

AP_RAD_M  = deg2m(AP_RAD_DEG)
dt        = 1.0 / SIM_HZ

# ── Dot initialisation ─────────────────────────────────────────────────────────
def make_dots(seed, n=N_DOTS, r=AP_RAD_M):
    rng = np.random.default_rng(seed)
    u = rng.random(n); th = rng.random(n) * 2*np.pi
    return np.column_stack([r*np.sqrt(u)*np.cos(th), r*np.sqrt(u)*np.sin(th)])

# ── Motion helpers ─────────────────────────────────────────────────────────────
def rotate(pos, sign):
    ang = np.radians(sign * ROT_SPD_DEG / SIM_HZ)
    c, s = np.cos(ang), np.sin(ang)
    return pos @ np.array([[c,-s],[s,c]]).T

def respawn(pos, rng, r=AP_RAD_M):
    mag = np.linalg.norm(pos, axis=1)
    oob = mag > r
    if oob.any():
        n = oob.sum(); u = rng.random(n); th = rng.random(n)*2*np.pi
        pos[oob] = np.column_stack([r*np.sqrt(u)*np.cos(th), r*np.sqrt(u)*np.sin(th)])
    return pos

def translate(pos, heading_deg, rng):
    step = deg2m(TRANS_SPD_DEG) / SIM_HZ
    d = np.array([np.cos(np.radians(heading_deg)), np.sin(np.radians(heading_deg))]) * step
    return respawn(pos + d, rng)

def noncoh(pos, rng):
    step = deg2m(TRANS_SPD_DEG) / SIM_HZ
    dirs = np.array([[np.cos(np.radians(a)), np.sin(np.radians(a))]
                     for a in range(0,360,45)])
    pos = pos + dirs[np.arange(len(pos))%8] * step
    return respawn(pos, rng)

# ── Depth assignment ───────────────────────────────────────────────────────────
# Field B (sub2,3) = delayed = Near initially (-DEPTH_OFFS_M)
# Field A (sub0,1) = non-delayed = Far (+DEPTH_OFFS_M)
# In Z: both swap at tStart.  In C: color swaps, depth unchanged.
# In CZ: both color and depth swap.  In N: nothing swaps.

def get_depth(sf, frame, swap):
    """Return depth offset (m) for subfield sf at frame, given swap condition."""
    field_a = (sf < 2)
    depth_swapped = swap in ('Z', 'CZ') and frame >= T_START
    if field_a:
        return -DEPTH_OFFS_M if depth_swapped else DEPTH_OFFS_M
    else:
        return DEPTH_OFFS_M if depth_swapped else -DEPTH_OFFS_M

def get_color_code(sf, frame, swap, b_green):
    """Return color (0=red, 1=green) for subfield sf at frame."""
    # Field B (delayed) has color b_green initially.
    # In C/CZ, colors swap at tStart.
    base_b = int(b_green)
    base_a = 1 - base_b
    color_swapped = swap in ('C', 'CZ') and frame >= T_START
    if (sf < 2):   # Field A
        return base_b if color_swapped else base_a
    else:           # Field B
        return base_a if color_swapped else base_b

# ── Simulate one trial ─────────────────────────────────────────────────────────
def simulate(swap, cued, b_green=True):
    """
    Returns pos_hist[sf][frame] = (N,2) array of dot positions in local plane (m),
            dep_hist[sf][frame] = depth offset (m)
            col_hist[sf][frame] = color code (0=red, 1=green)
    """
    rngs = [np.random.default_rng(RNG_SEED+sf*13) for sf in range(4)]
    pos  = [make_dots(RNG_SEED+sf*7) for sf in range(4)]

    pos_hist = [[None]*TOTAL_FRAMES for _ in range(4)]
    dep_hist = [[None]*TOTAL_FRAMES for _ in range(4)]
    col_hist = [[None]*TOTAL_FRAMES for _ in range(4)]

    for f in range(TOTAL_FRAMES):
        for sf in range(4):
            pos_hist[sf][f] = pos[sf].copy()
            dep_hist[sf][f] = get_depth(sf, f, swap)
            col_hist[sf][f] = get_color_code(sf, f, swap, b_green)

        # Step motion for each subfield
        in_trans = T_START <= f < T_END
        for sf in range(4):
            if sf >= 2 and f < ONSET_F:
                continue  # Field B hidden before onset
            if in_trans:
                if cued:
                    if sf == 2:    pos[sf] = translate(pos[sf], HEADING_DEG, rngs[sf])
                    elif sf == 3:  pos[sf] = noncoh(pos[sf], rngs[sf])
                    else:          pos[sf] = rotate(pos[sf], -1); pos[sf] = respawn(pos[sf], rngs[sf])
                else:
                    if sf == 0:    pos[sf] = translate(pos[sf], HEADING_DEG, rngs[sf])
                    elif sf == 1:  pos[sf] = noncoh(pos[sf], rngs[sf])
                    else:          pos[sf] = rotate(pos[sf], +1); pos[sf] = respawn(pos[sf], rngs[sf])
            else:
                if sf < 2:   pos[sf] = rotate(pos[sf], -1); pos[sf] = respawn(pos[sf], rngs[sf])
                else:        pos[sf] = rotate(pos[sf], +1); pos[sf] = respawn(pos[sf], rngs[sf])

    return pos_hist, dep_hist, col_hist

# ── Projection functions ───────────────────────────────────────────────────────
def project_postfix(xy_m, z_m):
    """Post-fix: camera-aligned, correct perspective."""
    z_world = VIEW_DIST_M + z_m
    return np.degrees(xy_m / z_world)

def project_prefiX(xy_m, z_m, pitch=PITCH_DEG):
    """Pre-fix: transform.forward pitched pitch degrees above gaze."""
    p = np.radians(pitch)
    z_world = VIEW_DIST_M + z_m * np.cos(p)
    y_bias  = z_m * np.sin(p)
    proj = xy_m / z_world
    proj = proj.copy()
    proj[:, 1] += y_bias / z_world
    return np.degrees(proj)

# ── Drawing helpers ────────────────────────────────────────────────────────────
COLORS = ['#cc3333', '#22aa44']   # red, green

def draw_panel(ax, pos_hist, dep_hist, col_hist, project_fn, cued,
               show_tstart=True, ap_rad=AP_RAD_DEG):
    """
    Draw dot snapshot at 3 frames: tStart-6, tStart, tStart+3.
    Field B (subfields 2,3) only — the attended field (CUED) or unattended (UNCUED).
    """
    ax.set_aspect('equal')
    circle = plt.Circle((0,0), ap_rad, color='#f0f0f0', zorder=0)
    ax.add_patch(circle)
    ax.set_xlim(-ap_rad-0.2, ap_rad+0.2)
    ax.set_ylim(-ap_rad-0.2, ap_rad+0.2)
    ax.set_xticks([]); ax.set_yticks([])

    key_frames = [T_START-6, T_START, T_START+3]
    alphas     = [0.25, 0.65, 1.0]
    sizes      = [6, 10, 14]

    for fi, (f, alpha, sz) in enumerate(zip(key_frames, alphas, sizes)):
        for sf in range(4):
            if f < ONSET_F and sf >= 2: continue
            xy = pos_hist[sf][f]
            z  = dep_hist[sf][f]
            c  = col_hist[sf][f]
            proj = project_fn(xy, z)

            # Field A: small filled; Field B: larger
            field_b = sf >= 2
            color = COLORS[c]
            fc = color if field_b else 'none'
            ec = color
            marker_sz = sz if field_b else sz*0.6
            ax.scatter(proj[:,0], proj[:,1], s=marker_sz, facecolors=fc,
                       edgecolors=ec, linewidths=0.6, alpha=alpha, zorder=2+fi)

    if show_tstart:
        ax.axhline(0, color='#cccccc', lw=0.4, zorder=1)

    # Translation arrow
    th = np.radians(HEADING_DEG)
    ax.annotate('', xy=(np.cos(th)*ap_rad*0.72, np.sin(th)*ap_rad*0.72),
                xytext=(np.cos(th)*ap_rad*0.45, np.sin(th)*ap_rad*0.45),
                arrowprops=dict(arrowstyle='->', color='#555555', lw=1.2))


def centroid_y_trace(pos_hist, dep_hist, project_fn, sf=2,
                     frames=None):
    """Y-centroid of subfield sf over time, in projected degrees."""
    if frames is None:
        frames = range(ONSET_F, TOTAL_FRAMES)
    ys = []
    for f in frames:
        proj = project_fn(pos_hist[sf][f], dep_hist[sf][f])
        ys.append(np.mean(proj[:,1]))
    return np.array(ys)


def draw_centroid_strip(ax, pos_hist, dep_hist, project_fn, cued,
                        color='#333333', label=None):
    frames = list(range(60, 95))
    t = [(f - T_START)/SIM_HZ*1000 for f in frames]  # ms relative to tStart
    sf = 2 if cued else 0   # coherent subfield
    ys = centroid_y_trace(pos_hist, dep_hist, project_fn, sf=sf, frames=frames)
    ax.plot(t, ys, color=color, lw=1.5, label=label)
    ax.axvline(0, color='#ee4444', lw=1.0, ls='--', alpha=0.7)
    ax.axhline(0, color='#bbbbbb', lw=0.5)
    ax.set_xlabel('ms rel. tStart', fontsize=6.5)
    ax.set_ylabel('Y centroid (°)', fontsize=6.5)
    ax.tick_params(labelsize=6)


# ── Build one page ─────────────────────────────────────────────────────────────
SWAPS  = ['N', 'C', 'Z', 'CZ']
SWAP_LABELS = {'N': 'N (no swap)', 'C': 'C (color swap)',
               'Z': 'Z (depth swap)', 'CZ': 'CZ (color+depth swap)'}
SWAP_COLORS = {'N':'#444444','C':'#e08000','Z':'#1a6bb5','CZ':'#9b2eaa'}

def make_page(pdf, project_fn, page_title, pitch_note):
    # Layout: 4 rows (swaps) × 5 columns:
    #   [dot panel CUED | centroid strip CUED | spacer | dot panel UNCUED | centroid strip UNCUED]
    fig = plt.figure(figsize=(14, 11))
    fig.patch.set_facecolor('white')
    fig.suptitle(page_title, fontsize=11, fontweight='bold', y=0.99)
    fig.text(0.5, 0.965, pitch_note, ha='center', fontsize=8.5, color='#555555')

    # Column widths: [dot, centroid, gap, dot, centroid]
    col_x   = [0.04,  0.21,  0.39,  0.52,  0.69]
    col_w   = [0.16,  0.16,  None,  0.16,  0.16]
    row_h   = 0.195
    row_gap = 0.015
    row_tops = [0.925 - i*(row_h+row_gap) for i in range(4)]

    for ri, swap in enumerate(SWAPS):
        top = row_tops[ri]
        sc  = SWAP_COLORS[swap]

        # Row label
        fig.text(0.005, top - row_h*0.4, SWAP_LABELS[swap],
                 va='center', ha='left', fontsize=9, fontweight='bold',
                 color=sc, rotation=90)

        for ci, (cued, col_offset) in enumerate([(True, 0), (False, 3)]):
            pos_hist, dep_hist, col_hist = simulate(swap, cued, b_green=(ci==0))

            # Dot panel
            ax_dot = fig.add_axes([col_x[col_offset], top - row_h,
                                   col_w[col_offset], row_h*0.88])
            draw_panel(ax_dot, pos_hist, dep_hist, col_hist, project_fn, cued)

            # Add swap indicator box in Z/CZ at tStart
            if swap in ('Z', 'CZ'):
                ax_dot.add_patch(plt.Rectangle((-AP_RAD_DEG-0.2, -AP_RAD_DEG-0.2),
                                               2*(AP_RAD_DEG+0.2), 2*(AP_RAD_DEG+0.2),
                                               fill=False, edgecolor=sc,
                                               linewidth=2.0, zorder=10))

            # Centroid strip
            ax_cen = fig.add_axes([col_x[col_offset+1], top - row_h,
                                   col_w[col_offset+1], row_h*0.88])
            draw_centroid_strip(ax_cen, pos_hist, dep_hist, project_fn,
                                cued=cued, color=sc)
            # Annotate jump
            frames = list(range(60, 95))
            t = [(f - T_START)/SIM_HZ*1000 for f in frames]
            sf = 2 if cued else 0
            ys = centroid_y_trace(pos_hist, dep_hist, project_fn, sf=sf, frames=frames)
            y_before = ys[frames.index(T_START)-1]
            y_after  = ys[frames.index(T_START)]
            jump = y_after - y_before
            ax_cen.annotate(f'Δ={jump:+.3f}°',
                            xy=(0, y_after), xytext=(15, y_after+0.05),
                            fontsize=6.5, color=sc,
                            arrowprops=dict(arrowstyle='->', color=sc, lw=0.8))

        # Column headers (first row only)
        if ri == 0:
            fig.text(col_x[0] + col_w[0]/2, top + 0.006,
                     'CUED — dot snapshot', ha='center', fontsize=8.5,
                     fontweight='bold', color='#333333')
            fig.text(col_x[1] + col_w[1]/2, top + 0.006,
                     'CUED — Field B centroid Y', ha='center', fontsize=8.5,
                     fontweight='bold', color='#333333')
            fig.text(col_x[3] + col_w[3]/2, top + 0.006,
                     'UNCUED — dot snapshot', ha='center', fontsize=8.5,
                     fontweight='bold', color='#333333')
            fig.text(col_x[4] + col_w[4]/2, top + 0.006,
                     'UNCUED — coherent centroid Y', ha='center', fontsize=8.5,
                     fontweight='bold', color='#333333')

    # Legend
    patches = [mpatches.Patch(color='#cc3333', label='Red field'),
               mpatches.Patch(color='#22aa44', label='Green field')]
    from matplotlib.lines import Line2D
    patches += [
        Line2D([0],[0], color='#ee4444', ls='--', lw=1.2, label='tStart'),
        mpatches.Patch(color='none', ec='#555555', label='Filled = Field B (delayed onset)'),
    ]
    fig.legend(handles=patches, loc='lower center', ncol=4, fontsize=8,
               bbox_to_anchor=(0.5, 0.003))

    # Notes
    fig.text(0.5, 0.022,
             f'Heading = 270° (DOWN) throughout. Dots shown at frames tStart−6 (faint), tStart (medium), tStart+3 (solid). '
             f'Colored border = depth swap active.',
             ha='center', fontsize=7.5, color='#666666')

    pdf.savefig(fig, bbox_inches='tight')
    plt.close(fig)


# ── Comparison page: jump magnitude table ─────────────────────────────────────
def make_comparison_table(pdf):
    fig = plt.figure(figsize=(10, 6.5))
    fig.patch.set_facecolor('white')
    ax = fig.add_axes([0.06, 0.10, 0.88, 0.82])
    ax.axis('off')

    def t(y, text, size=9, weight='normal', color='#111111', indent=0.0, ha='left'):
        ax.text(indent, y, text, transform=ax.transAxes,
                ha=ha, va='top', fontsize=size, fontweight=weight, color=color)

    t(0.97, 'Centroid Y-jump at tStart: pre-fix vs post-fix', 11, 'bold')
    t(0.90, 'Coherent subfield (Field B, CUED arm), heading = 270° (DOWN)', 9, color='#444')
    t(0.83, 'Values in degrees of visual angle.  Translation signal = 2.26 deg/sec × 13ms/frame = 0.030°/frame.', 8.5)

    # Table header
    cols = [0.02, 0.22, 0.42, 0.65, 0.85]
    hdrs = ['Condition', 'Pre-fix jump (°)', 'Post-fix jump (°)',
            'Artifact/signal ratio (pre)', 'Data: % UP in wrong resp.']
    data_up = {'N': '4%', 'C': '6%', 'Z': '50%', 'CZ': '51%'}

    y = 0.73
    for i, h in enumerate(hdrs):
        t(y, h, 8.5, 'bold', indent=cols[i])
    y -= 0.06
    ax.axhline(y+0.03, color='#cccccc', lw=0.8)

    signal_per_frame = TRANS_SPD_DEG / SIM_HZ  # deg/frame

    for swap in SWAPS:
        pos_hist, dep_hist, col_hist = simulate(swap, cued=True)

        def jump(project_fn):
            frames = list(range(60, 95))
            ys = centroid_y_trace(pos_hist, dep_hist, project_fn, sf=2, frames=frames)
            return ys[frames.index(T_START)] - ys[frames.index(T_START)-1]

        j_pre  = jump(project_prefiX)
        j_post = jump(project_postfix)
        ratio  = abs(j_pre) / signal_per_frame
        sc = SWAP_COLORS[swap]

        vals = [SWAP_LABELS[swap],
                f'{j_pre:+.4f}°',
                f'{j_post:+.4f}°',
                f'{ratio:.1f}×',
                data_up[swap]]
        for i, v in enumerate(vals):
            weight = 'bold' if swap in ('Z','CZ') and i in (1,3,4) else 'normal'
            col_v = sc if swap in ('Z','CZ') else '#444444'
            t(y, v, 9 if swap in ('Z','CZ') else 8.5, weight, col_v, indent=cols[i])
        y -= 0.09
        ax.axhline(y+0.04, color='#eeeeee', lw=0.5)

    y -= 0.02
    t(y, 'Summary:', 9.5, 'bold', '#1a1a6b')
    y -= 0.055
    lines = [
        '• N and C conditions: zero artifact in both pre-fix and post-fix (no depth swap at tStart).',
        '• Z and CZ conditions: pre-fix jump is 8–9× the per-frame translation signal → dominates direction percept.',
        '• Post-fix: residual jump ≈ 0.002° (perspective-induced radial expansion) — < 0.1× signal.',
        '• The pre-fix artifact direction is always upward (+Y) regardless of true translation direction,',
        '  consistent with observer GS reports of "jerky upward motion" and the UP-bias in wrong responses.',
        '• After fix: stereo traces for Z and CZ look identical to N (no directional jump at tStart).',
    ]
    for l in lines:
        t(y, l, 8.5, indent=0.02)
        y -= 0.065

    pdf.savefig(fig, bbox_inches='tight')
    plt.close(fig)


# ── Main ───────────────────────────────────────────────────────────────────────
def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    with PdfPages(OUT_PDF) as pdf:
        print('Rendering page 1: pre-fix traces...')
        make_page(pdf,
                  project_fn=project_prefiX,
                  page_title='DecoupledDots — STEREO TRACES  (PRE-FIX, buggy code)',
                  pitch_note=f'Depth offset applied along transform.forward pitched {PITCH_DEG}° above gaze. '
                              'Artifact visible as upward jump in Z and CZ centroid strips.')

        print('Rendering page 2: post-fix traces...')
        make_page(pdf,
                  project_fn=project_postfix,
                  page_title='DecoupledDots — STEREO TRACES  (POST-FIX, camera.forward)',
                  pitch_note='Depth offset applied along camera.forward (gaze-aligned). '
                              'No directional artifact. Tiny radial expansion at tStart in Z/CZ is sub-threshold.')

        print('Rendering comparison table...')
        make_comparison_table(pdf)

    print(f'\nSaved → {OUT_PDF}')


if __name__ == '__main__':
    main()
