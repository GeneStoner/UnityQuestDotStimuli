"""
stereo_trace_artifact_demo.py
==============================
Demonstrates what the depth-swap upward-motion artifact looks like in stereo-projected
traces, compared to the 2D local-space traces that were previously used.

Three panels for a single Z-condition CUED trial:
  Panel A: 2D local-space traces  — what old trace figures show (artifact INVISIBLE)
  Panel B: Screen-space cyclopean projection, pre-fix  (transform.forward pitched 5° up)
           — artifact VISIBLE as upward jump at tStart
  Panel C: Screen-space cyclopean projection, post-fix (camera.forward = gaze direction)
           — CLEAN: only tiny radial expansion at tStart

Physics parameters match the actual experiment:
  viewDistance_m = 2.0, depthOffset_m = 0.05, rotSpeed = 81 deg/sec,
  transSpeed = 2.26 deg/sec, apertureRadius_deg = 3.5, simHz = 75
  onsetFrame = 56, transStartFrame = 78, transEndFrame = 84
  headingDeg = 270  (DOWNWARD — worst case: artifact is most visible here)
  IPD = 0.064m (standard interpupillary distance)
  Pitch misalignment: 5° (pre-fix scenario; realistic for a world-space StimulusBuilder)
"""

import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

# ── Output ─────────────────────────────────────────────────────────────────────
OUT_DIR = os.path.join(os.path.dirname(__file__), '../../Agents/SwapPilot/Figures')
OUT_PDF = os.path.join(OUT_DIR, 'stereo_trace_artifact_demo.pdf')

# ── Experiment parameters ───────────────────────────────────────────────────────
VIEW_DIST_M   = 2.0       # viewing distance (m)
DEPTH_OFFS_M  = 0.05      # ±depth offset (m)
SIM_HZ        = 75        # frames per second
AP_RAD_DEG    = 3.5       # aperture radius (degrees)
ROT_SPD_DEG   = 81.0      # rotation speed (deg/sec)
TRANS_SPD_DEG = 2.26      # translation speed (deg/sec)
ONSET_F       = 56        # frame when Field B appears
TRANS_START_F = 78        # frame when translation starts
TRANS_END_F   = 84        # frame when translation ends (exclusive)
TOTAL_FRAMES  = 114
HEADING_DEG   = 270.0     # DOWNWARD — artifact maximally conflicts with signal
N_DOTS        = 30        # dots per subfield (display subset)
IPD_M         = 0.064     # interpupillary distance (m)
PITCH_DEG     = 5.0       # forward-axis pitch above gaze (pre-fix scenario)
RNG_SEED      = 42

DEG_TO_M = VIEW_DIST_M * np.tan(np.radians(1.0))  # meters per degree at view dist

def deg_to_m(d): return d * DEG_TO_M
def m_to_deg(m): return m / DEG_TO_M

AP_RAD_M = deg_to_m(AP_RAD_DEG)
dt = 1.0 / SIM_HZ

# ── Dot initialisation ─────────────────────────────────────────────────────────
def make_dots(seed, n=N_DOTS, r=AP_RAD_M):
    rng = np.random.default_rng(seed)
    u = rng.random(n)
    th = rng.random(n) * 2 * np.pi
    radii = r * np.sqrt(u)
    return np.column_stack([radii * np.cos(th), radii * np.sin(th)])  # (n, 2)

# ── Motion step helpers ────────────────────────────────────────────────────────
def step_rotate(pos, sign, deg_per_frame):
    ang = np.radians(sign * deg_per_frame)
    c, s = np.cos(ang), np.sin(ang)
    R = np.array([[c, -s], [s, c]])
    return pos @ R.T

def respawn_oob(pos, r, rng):
    mag = np.linalg.norm(pos, axis=1)
    oob = mag > r
    if oob.any():
        n = oob.sum()
        u = rng.random(n); th = rng.random(n) * 2 * np.pi
        radii = r * np.sqrt(u)
        pos[oob, 0] = radii * np.cos(th)
        pos[oob, 1] = radii * np.sin(th)
    return pos

def step_translate(pos, heading_deg, speed_m_per_frame, rng, r=AP_RAD_M):
    th = np.radians(heading_deg)
    delta = np.array([np.cos(th), np.sin(th)]) * speed_m_per_frame
    pos = pos + delta
    return respawn_oob(pos, r, rng)

def step_noncoherent_balanced(pos, speed_m_per_frame, rng, r=AP_RAD_M):
    dirs = np.array([[np.cos(np.radians(a)), np.sin(np.radians(a))]
                     for a in range(0, 360, 45)])
    idx = np.arange(len(pos)) % 8
    deltas = dirs[idx] * speed_m_per_frame
    pos = pos + deltas
    return respawn_oob(pos, r, rng)

# ── Stereo projection ──────────────────────────────────────────────────────────
def project_cyclopean(xy_m, z_depth_m):
    """
    Cyclopean (average eye) screen projection.
    xy_m: (n, 2) dot positions in local plane (meters)
    z_depth_m: scalar depth offset (positive = farther from viewer)
    Returns (n, 2) projected positions in degrees of visual angle.
    """
    z_world = VIEW_DIST_M + z_depth_m
    x_proj = xy_m[:, 0] / z_world  # radians
    y_proj = xy_m[:, 1] / z_world
    return np.degrees(np.column_stack([x_proj, y_proj]))

def project_cyclopean_prefix(xy_m, z_depth_m, pitch_deg=PITCH_DEG):
    """
    Pre-fix projection: depth offset applied along an axis pitched upward by pitch_deg
    relative to the true gaze direction. The upward component creates an apparent
    screen-vertical displacement when z_depth changes.

    For a pitch of θ degrees, moving along the pitched forward axis by z meters produces:
      - z_along_gaze = z * cos(θ)   [depth component]
      - z_upward     = z * sin(θ)   [spurious vertical component in screen space]
    """
    pitch_rad = np.radians(pitch_deg)
    # The forward axis (pitched by θ) has a component along the gaze direction (z_world_true)
    # and a component along screen-up (y_screen).
    z_along_gaze = z_depth_m * np.cos(pitch_rad)
    y_screen_bias = z_depth_m * np.sin(pitch_rad)  # added to all dot y positions

    z_world = VIEW_DIST_M + z_along_gaze
    x_proj = xy_m[:, 0] / z_world
    y_proj = (xy_m[:, 1] + y_screen_bias) / z_world
    return np.degrees(np.column_stack([x_proj, y_proj]))

# ── Simulate a single Z-condition CUED trial ──────────────────────────────────
def simulate_trial():
    """
    Simulate subfields 0–3 for a Z-condition CUED trial.
    Subfields: 0,1 = Field A (non-delayed, CW rotation), 2,3 = Field B (delayed, CCW rotation)
    At TRANS_START_F: depth planes swap (Field A gets Far, Field B gets Near)
    During translation: sub2 = Linear (heading 270°), sub3 = NonCoherent

    Returns: list of (pos_history, depth_history) per subfield.
    pos_history[f] = (n, 2) array of dot positions at frame f
    depth_history[f] = depth_offset (m)
    """
    seeds = [RNG_SEED, RNG_SEED+1, RNG_SEED+2, RNG_SEED+3]
    rngs = [np.random.default_rng(s+100) for s in seeds]

    # Initial positions
    pos = [make_dots(seeds[i]) for i in range(4)]

    # Depth assignments
    # Field B (sub2,3) = delayed = Near initially; Field A = Far
    # fieldBDepth = Near (-DEPTH_OFFS_M), fieldADepth = Far (+DEPTH_OFFS_M)
    def get_depth(sf, frame):
        after_swap = frame >= TRANS_START_F
        if sf in (0, 1):  # Field A
            return DEPTH_OFFS_M if not after_swap else -DEPTH_OFFS_M  # Far→Near
        else:             # Field B
            return -DEPTH_OFFS_M if not after_swap else DEPTH_OFFS_M  # Near→Far

    rot_speed_per_frame = ROT_SPD_DEG / SIM_HZ
    trans_speed_per_frame = deg_to_m(TRANS_SPD_DEG) / SIM_HZ

    pos_hist  = [[] for _ in range(4)]
    dep_hist  = [[] for _ in range(4)]

    for f in range(TOTAL_FRAMES):
        for sf in range(4):
            pos_hist[sf].append(pos[sf].copy())
            dep_hist[sf].append(get_depth(sf, f))

        # Step motion
        if f >= ONSET_F:  # Field B visible after onset
            pass  # all fields always step

        for sf in range(4):
            visible = (sf < 2) or (f >= ONSET_F)
            if not visible:
                continue

            in_trans = TRANS_START_F <= f < TRANS_END_F

            if in_trans and sf == 2:      # sub2: Linear (coherent)
                pos[sf] = step_translate(pos[sf], HEADING_DEG, trans_speed_per_frame,
                                         rngs[sf])
            elif in_trans and sf == 3:    # sub3: NonCoherent
                pos[sf] = step_noncoherent_balanced(pos[sf], trans_speed_per_frame,
                                                    rngs[sf])
            elif sf in (0, 1):            # Field A: CW
                pos[sf] = step_rotate(pos[sf], -1, rot_speed_per_frame)
                pos[sf] = respawn_oob(pos[sf], AP_RAD_M, rngs[sf])
            else:                         # Field B: CCW
                pos[sf] = step_rotate(pos[sf], +1, rot_speed_per_frame)
                pos[sf] = respawn_oob(pos[sf], AP_RAD_M, rngs[sf])

    return pos_hist, dep_hist

# ── Build figure ───────────────────────────────────────────────────────────────
FRAMES_TO_SHOW = list(range(72, 90))   # frames around tStart (78)
FRAME_LABELS   = [f-TRANS_START_F for f in FRAMES_TO_SHOW]  # relative to tStart

# Colours and styles
SF_COLORS  = ['#cc3333', '#cc3333', '#2255aa', '#2255aa']
SF_FILLED  = [True, True, False, False]   # field A filled, field B open

def draw_traces(ax, pos_hist, dep_hist, projection_fn, title, frames=FRAMES_TO_SHOW):
    """
    Draw dot traces using specified projection function.
    projection_fn(xy_m, z_depth_m) -> (n, 2) projected positions in degrees.
    """
    ax.set_aspect('equal')
    ap_patch = plt.Circle((0, 0), AP_RAD_DEG, color='#e8e8e8', zorder=0)
    ax.add_patch(ap_patch)
    ax.set_xlim(-AP_RAD_DEG-0.3, AP_RAD_DEG+0.3)
    ax.set_ylim(-AP_RAD_DEG-0.3, AP_RAD_DEG+0.3)

    n_frames = len(frames)
    alphas = np.linspace(0.15, 0.95, n_frames)

    for fi, f in enumerate(frames):
        is_swap_frame = (f == TRANS_START_F)
        for sf in range(4):
            xy = pos_hist[sf][f]           # (n, 2) local-plane positions (meters)
            z  = dep_hist[sf][f]           # depth offset (m)
            proj = projection_fn(xy, z)    # (n, 2) in degrees

            ms = 2.5
            fc = SF_COLORS[sf] if SF_FILLED[sf] else 'white'
            ec = SF_COLORS[sf]
            lw = 0.5 if not is_swap_frame else 1.5
            mk = 'o'
            ax.scatter(proj[:, 0], proj[:, 1], s=ms**2, facecolors=fc,
                       edgecolors=ec, linewidths=lw, alpha=alphas[fi], zorder=2)

    # Mark tStart with a vertical line in time — instead, draw an arrow for translation
    ax.annotate('', xy=(AP_RAD_DEG*0.55, -AP_RAD_DEG*0.85),
                xytext=(AP_RAD_DEG*0.55, -AP_RAD_DEG*0.55),
                arrowprops=dict(arrowstyle='->', color='#444444', lw=1.5))
    ax.text(AP_RAD_DEG*0.58, -AP_RAD_DEG*0.7, 'TRUE\n270°', fontsize=6.5,
            color='#444444', ha='left', va='center')

    ax.axhline(0, color='#bbbbbb', lw=0.5, zorder=1)
    ax.axvline(0, color='#bbbbbb', lw=0.5, zorder=1)
    ax.set_xlabel('Horizontal (deg)', fontsize=8)
    ax.set_ylabel('Vertical (deg)', fontsize=8)
    ax.set_title(title, fontsize=8.5, pad=4)
    ax.tick_params(labelsize=7)

def make_time_series_panel(ax, pos_hist, dep_hist, projection_fn, title):
    """
    Plot y-position (vertical screen position) of centroid of Field B (sub2) over time.
    Shows the step artifact at tStart as a time series.
    """
    frames_all = list(range(60, 95))
    y_centroids = []
    for f in frames_all:
        proj = projection_fn(pos_hist[2][f], dep_hist[2][f])
        y_centroids.append(np.mean(proj[:, 1]))

    t = [f / SIM_HZ for f in frames_all]
    t_start = TRANS_START_F / SIM_HZ
    ax.plot(t, y_centroids, 'b-', lw=1.5)
    ax.axvline(t_start, color='red', lw=1, ls='--', label='tStart (depth swap)')
    ax.set_xlabel('Time (s)', fontsize=8)
    ax.set_ylabel('Field B centroid Y (deg)', fontsize=8)
    ax.set_title(title, fontsize=8.5, pad=4)
    ax.legend(fontsize=7, loc='upper left')
    ax.tick_params(labelsize=7)

def make_figure(pos_hist, dep_hist):
    fig = plt.figure(figsize=(14, 9))
    fig.suptitle(
        'Stereo-projected trace demo — Z condition, CUED, heading 270° (DOWNWARD)\n'
        'Comparing: 2D local traces (old method) vs screen-space projections (pre-fix and post-fix)',
        fontsize=10, fontweight='bold', y=0.99)

    fig.subplots_adjust(left=0.06, right=0.97, top=0.88, bottom=0.10,
                        wspace=0.38, hspace=0.45)

    # Row 1: snapshot traces (dots at frames 72–89)
    ax1 = fig.add_subplot(2, 3, 1)
    ax2 = fig.add_subplot(2, 3, 2)
    ax3 = fig.add_subplot(2, 3, 3)

    draw_traces(ax1, pos_hist, dep_hist,
                lambda xy, z: np.degrees(xy / VIEW_DIST_M),
                'A. 2D local-plane traces\n(old method — no depth projection)\nArtifact: INVISIBLE')

    draw_traces(ax2, pos_hist, dep_hist,
                lambda xy, z: project_cyclopean_prefix(xy, z, PITCH_DEG),
                f'B. Screen-space — PRE-FIX\n(transform.forward pitched {PITCH_DEG}° up)\nArtifact: VISIBLE — upward jump at tStart')

    draw_traces(ax3, pos_hist, dep_hist,
                lambda xy, z: project_cyclopean(xy, z),
                'C. Screen-space — POST-FIX\n(camera.forward aligned with gaze)\nArtifact: ABSENT — tiny radial expansion only')

    # Row 2: time-series of Field B vertical centroid
    ax4 = fig.add_subplot(2, 3, 4)
    ax5 = fig.add_subplot(2, 3, 5)
    ax6 = fig.add_subplot(2, 3, 6)

    make_time_series_panel(ax4, pos_hist, dep_hist,
                           lambda xy, z: np.degrees(xy / VIEW_DIST_M),
                           'A2. Field B centroid Y — 2D local\n(depth swap invisible)')

    make_time_series_panel(ax5, pos_hist, dep_hist,
                           lambda xy, z: project_cyclopean_prefix(xy, z, PITCH_DEG),
                           f'B2. Field B centroid Y — pre-fix\n(upward jump {PITCH_DEG}° pitch → jump at tStart)')

    make_time_series_panel(ax6, pos_hist, dep_hist,
                           lambda xy, z: project_cyclopean(xy, z),
                           'C2. Field B centroid Y — post-fix\n(no directional jump)')

    # Legend
    from matplotlib.lines import Line2D
    legend_elements = [
        Line2D([0], [0], marker='o', color='w', markerfacecolor='#cc3333',
               markeredgecolor='#cc3333', markersize=6, label='Field A (non-delayed, CW)'),
        Line2D([0], [0], marker='o', color='w', markerfacecolor='white',
               markeredgecolor='#2255aa', markersize=6, label='Field B (delayed, CCW)'),
        Line2D([0], [0], color='red', ls='--', lw=1.2, label='tStart (depth swap)'),
    ]
    fig.legend(handles=legend_elements, loc='lower center', ncol=3, fontsize=8,
               bbox_to_anchor=(0.5, 0.01))

    return fig

def make_explainer_page():
    """Text page explaining the three panels and the math."""
    fig = plt.figure(figsize=(10, 7.5))
    fig.patch.set_facecolor('white')
    ax = fig.add_axes([0.06, 0.04, 0.88, 0.92])
    ax.axis('off')

    def t(y, text, size=9, weight='normal', color='#111111', indent=0.0):
        ax.text(indent, y, text, transform=ax.transAxes,
                ha='left', va='top', fontsize=size, fontweight=weight, color=color)

    t(0.97, 'Stereo-projected traces: the math and the fix', 11, 'bold')
    y = 0.91

    blocks = [
        ('What the 2D traces show', [
            'The existing trace figures plot dot (x, y) positions in the StimulusBuilder\'s local plane,',
            'in units of metres or degrees of visual angle. Depth is encoded symbolically (filled vs open',
            'circles). This is equivalent to an orthographic projection from infinitely far away — it has',
            'no perspective and no depth. The depth-offset code (ApplyDepthOffsets) is never called.',
            'Result: the figure represents the stimulus *design* correctly but is blind to any rendering',
            'artifact that lives in the depth-offset code.',
        ]),
        ('The projection math', [
            'For a dot at local position (x, y) [metres] and depth offset z [metres, positive = farther]:',
            '  z_world = viewDistance + z_depth  (total viewing distance)',
            '  x_screen = x / z_world  [radians]   y_screen = y / z_world  [radians]',
            '  binocular disparity = IPD / z_world  (positive = uncrossed = "far")',
            '',
            'Pre-fix artifact (transform.forward pitched θ° above gaze):',
            '  The forward axis has a spurious upward component: Δy_screen = z_depth × sin(θ) / z_world',
            '  For z_depth = 0.10m, θ = 5°, z_world ≈ 2m:',
            f'    Δy ≈ 0.10 × sin(5°) / 2.0 ≈ 0.0044 rad ≈ 0.25°',
            f'    Over 1 frame (13ms at 75 Hz) → apparent velocity ≈ 0.25°/0.013s ≈ 19 deg/sec',
            f'    Translation signal: 2.26 deg/sec. The artifact is ~8× faster.',
        ]),
        ('Post-fix behaviour', [
            'With camera.forward aligned to the gaze direction, the depth offset has no upward component.',
            'The only residual effect is a tiny perspective-induced radial expansion: dots at the aperture',
            'edge (2° eccentricity, 0.07m) shift outward by ≈0.05° when depth changes ±0.10m at 2m.',
            'This is 2% of the translation signal, radially symmetric, and physically correct.',
        ]),
        ('How to use these traces as a verification tool', [
            '1. For any new design with depth swaps, generate stereo traces before collecting data.',
            '2. Check that the depth-swap frame (tStart) produces ONLY small radial expansion, no',
            '   directional jump in the centroid time series.',
            '3. If a directional jump is visible, check that Camera.main is correctly set in the scene',
            '   and that StimulusBuilder has no unexpected rotation in its parent hierarchy.',
            '4. After any engine/build changes, re-run the verification — Unity XR updates can',
            '   change camera rig hierarchy and tag assignments.',
        ]),
    ]

    for heading, lines in blocks:
        t(y, heading, 9.5, 'bold', '#1a1a6b')
        y -= 0.032
        for l in lines:
            if l == '':
                y -= 0.010
            else:
                t(y, l, 8.2, indent=0.02)
                y -= 0.028
        y -= 0.018

    return fig

# ── Main ───────────────────────────────────────────────────────────────────────
def main():
    print('Simulating Z-condition trial...')
    pos_hist, dep_hist = simulate_trial()
    print(f'  {TOTAL_FRAMES} frames, {len(pos_hist[0][0])} dots/subfield')

    # Report centroid shifts at tStart for each projection
    def centroid_shift(project_fn, sf=2):
        before = np.mean(project_fn(pos_hist[sf][TRANS_START_F-1],
                                     dep_hist[sf][TRANS_START_F-1])[:, 1])
        after  = np.mean(project_fn(pos_hist[sf][TRANS_START_F],
                                     dep_hist[sf][TRANS_START_F])[:, 1])
        return after - before

    shift_2d      = centroid_shift(lambda xy, z: np.degrees(xy / VIEW_DIST_M))
    shift_prefix  = centroid_shift(lambda xy, z: project_cyclopean_prefix(xy, z, PITCH_DEG))
    shift_postfix = centroid_shift(lambda xy, z: project_cyclopean(xy, z))

    print(f'\nField B centroid Y-shift at tStart (depth Near→Far):')
    print(f'  2D local (no projection):  {shift_2d:.4f}°  [artifact invisible]')
    print(f'  Pre-fix ({PITCH_DEG}° pitch):      {shift_prefix:.4f}°  [artifact = {shift_prefix:.3f}° upward]')
    print(f'  Post-fix (aligned):        {shift_postfix:.4f}°  [residual ≈ 0]')
    print(f'\n  Translation signal over full window: '
          f'{TRANS_SPD_DEG * (TRANS_END_F-TRANS_START_F)/SIM_HZ:.3f}°')
    print(f'  Pre-fix artifact / signal ratio: '
          f'{abs(shift_prefix) / (TRANS_SPD_DEG/SIM_HZ):.1f}× per frame')

    os.makedirs(OUT_DIR, exist_ok=True)
    with PdfPages(OUT_PDF) as pdf:
        fig = make_figure(pos_hist, dep_hist)
        pdf.savefig(fig, bbox_inches='tight')
        plt.close(fig)

        fig2 = make_explainer_page()
        pdf.savefig(fig2, bbox_inches='tight')
        plt.close(fig2)

    print(f'\nSaved → {OUT_PDF}')

if __name__ == '__main__':
    main()
