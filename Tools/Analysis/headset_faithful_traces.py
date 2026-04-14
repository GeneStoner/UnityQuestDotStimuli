"""
headset_faithful_traces.py
===========================
Simulates the EXACT Unity StimulusBuilder + TrialBlockRunner code path and plots
screen-space angular positions of dot-field centroids across the 18 frames around tStart.

PURPOSE
-------
The previous trace scripts (stereo_trace_artifact_demo.py, decoupled_dots_traj.py)
show positions in the StimulusBuilder's local 2D plane — equivalent to orthographic
projection. They do NOT simulate ApplyDepthOffsets (the perspective correction code),
so they cannot reveal whether a depth-swap artifact is present.

This script mirrors the Unity code precisely:

  Unity method             Python equivalent
  ──────────────────────── ──────────────────────────────
  AlignStimulusBuilderAxis sets transform.forward = horizontal world-origin→stim
  ToLocalPlane             to_local_plane()
  FromLocalPlane           from_local_plane()
  ApplyDepthOffsets        apply_depth_offsets()  ← includes perspective correction
  GetDepthCorrectedMPD     get_depth_corrected_mpd()
  StepTranslation          step_translate()
  StepNonCoherentBalanced  step_noncoherent_balanced()
  StepRotation             step_rotate()

  Final screen-space projection:
    x_screen = x_world / z_world     (perspective division, same as GPU)
    where z_world = viewDist + z_depth

VERIFICATION LOGIC
------------------
Sub3 (non-coherent balanced field, 8-direction): net displacement = 0 per frame.
Any non-zero centroid shift in sub3 at tStart is PURE ARTIFACT.

Comparing N (no swap) vs Z (depth swap at tStart):
  If the perspective correction is working: Z sub3 centroid Y ≈ N sub3 centroid Y.
  If artifact remains: Z shows a step jump not present in N.

FIGURE LAYOUT (2 pages)
  Page 1: 4×4 grid
    Rows: N_Near, N_Far, Z_Near, Z_Far  (condition × delayed-field starting depth)
    Cols: sub2 X, sub2 Y, sub3 X, sub3 Y  (coherent-translator & non-coherent centroids)
    All in screen-space degrees of visual angle.
    Red dashed line = tStart. Thin grey = pre-fix (without angularScale correction).

  Page 2: Summary artifact panel
    For each condition × depth × sub:
      - Centroid shift at tStart (one frame), with vs without correction
      - Compared against the translation signal magnitude

PARAMETERS match the actual experiment (DecoupledDots_005m_v2 / DepthSwapCtrl_005m):
  viewDist=2.0m, depthSeparation=0.05m, rotSpeed=81°/s, transSpeed=2.26°/s,
  aperture=3.5°, simHz=75, onsetFrame=56, transStart=78, transEnd=84

USAGE
  python headset_faithful_traces.py
  → Agents/SwapPilot/Figures/headset_faithful_traces.pdf
"""

import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from collections import namedtuple

# ── Output ──────────────────────────────────────────────────────────────────────
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUT_DIR    = os.path.join(SCRIPT_DIR, '../../Agents/SwapPilot/Figures')
OUT_PDF    = os.path.join(OUT_DIR,    'headset_faithful_traces.pdf')

# ── Experiment parameters (matching DecoupledDots_005m_v2) ────────────────────
VIEW_DIST_M     = 2.0       # meters
DEPTH_SEP_M     = 0.05      # depthSeparation_m = depthOffset_m in StimulusBuilder
DEPTH_BIAS_M    = 0.0       # depthBias_m (default 0)
IPD_M           = 0.064     # interpupillary distance
SIM_HZ          = 75
ROT_SPD_DEG     = 81.0
TRANS_SPD_DEG   = 2.26
ONSET_F         = 56
TRANS_START_F   = 78        # tStart
TRANS_END_F     = 84        # tEnd (exclusive)
TOTAL_FRAMES    = 114
AP_RAD_DEG      = 3.5       # aperture RADIUS (degrees)
N_DOTS          = 200       # dots per subfield (matches 400/field ÷ 2 subs/field)
RNG_SEED        = 42

# Frame window for plots: 9 frames before tStart through 8 frames after
WIN_START = TRANS_START_F - 9
WIN_END   = TRANS_START_F + 9   # exclusive
WINDOW    = list(range(WIN_START, WIN_END))
REL_FRAMES = [f - TRANS_START_F for f in WINDOW]   # -9 … +8

dt         = 1.0 / SIM_HZ
DEG_TO_M   = VIEW_DIST_M * np.tan(np.radians(1.0))
AP_RAD_M   = AP_RAD_DEG * DEG_TO_M

# ── Depth plane helpers ──────────────────────────────────────────────────────
def z_for_plane(plane_str):
    """Return the z world-offset (metres) for a depth-plane label."""
    z = DEPTH_BIAS_M
    if   plane_str == 'Near': z -= DEPTH_SEP_M
    elif plane_str == 'Far':  z += DEPTH_SEP_M
    # 'Fix' → z stays = DEPTH_BIAS_M
    return z

def depth_corrected_mpd(plane_str):
    """
    Mirrors TrialBlockRunner.GetDepthCorrectedMetersPerDeg.
    Returns meters per degree at the specified depth plane.
    """
    z_offset = z_for_plane(plane_str)
    z_world  = VIEW_DIST_M + z_offset
    return z_world * np.tan(np.radians(1.0))

# ── Core coordinate transforms (mirror ToLocalPlane / FromLocalPlane) ────────
# StimulusBuilder is axis-aligned by AlignStimulusBuilderAxis:
#   transform.forward = horizontal direction from world origin to stimulus
#   transform.right   = cross(up, forward)
#   transform.up      = (0,1,0)
# In practice this means the local plane IS the global XY plane and
# depth is along global Z.  We keep everything in 2-D local (x, y) throughout
# and add z at render time — exactly like Unity.

def to_local_plane(world_xy_m):
    """Identity in the aligned coordinate frame — returns 2-D local coords."""
    return world_xy_m.copy()

def from_local_plane(local_xy_m):
    """Identity in the aligned coordinate frame."""
    return local_xy_m.copy()

# ── Dot initialisation ───────────────────────────────────────────────────────
def make_dots(seed, n=N_DOTS, r=AP_RAD_M):
    """Uniform disk, zero exclusion radius (matches default Inspector value)."""
    rng = np.random.default_rng(seed)
    u   = rng.random(n)
    th  = rng.random(n) * 2.0 * np.pi
    radii = r * np.sqrt(u)
    return np.column_stack([radii * np.cos(th), radii * np.sin(th)])  # (n, 2)

def respawn_oob(pos, r, rng):
    """Re-spawn out-of-bounds dots uniformly in the disk (mirrors respawnWhenOutOfBounds)."""
    mag = np.linalg.norm(pos, axis=1)
    oob = mag > r
    if oob.any():
        n   = oob.sum()
        u   = rng.random(n);  th = rng.random(n) * 2.0 * np.pi
        rad = r * np.sqrt(u)
        pos[oob, 0] = rad * np.cos(th)
        pos[oob, 1] = rad * np.sin(th)
    return pos

# ── Motion steps ────────────────────────────────────────────────────────────
def step_rotate(pos, sign, deg_per_frame, rng, r=AP_RAD_M):
    ang  = np.radians(sign * deg_per_frame)
    c, s = np.cos(ang), np.sin(ang)
    R    = np.array([[c, -s], [s, c]])
    pos  = pos @ R.T
    return respawn_oob(pos, r, rng)

def step_translate(pos, heading_deg, speed_mpf, rng, r=AP_RAD_M):
    """Linear coherent translation. speed_mpf = metres per frame (depth-corrected)."""
    th    = np.radians(heading_deg)
    delta = np.array([np.cos(th), np.sin(th)]) * speed_mpf
    pos   = pos + delta
    return respawn_oob(pos, r, rng)

def step_noncoherent_balanced(pos, speed_mpf, rng, r=AP_RAD_M):
    """8-direction balanced non-coherent motion. Net displacement per frame = 0."""
    dirs = np.array([[np.cos(np.radians(a)), np.sin(np.radians(a))]
                     for a in range(0, 360, 45)])
    idx    = np.arange(len(pos)) % 8
    deltas = dirs[idx] * speed_mpf
    pos    = pos + deltas
    return respawn_oob(pos, r, rng)

# ── ApplyDepthOffsets — the key function, exactly mirrors Unity C# ────────────
def apply_depth_offsets(pos, plane_now, plane_prev, apply_correction=True):
    """
    Mirrors StimulusBuilder.ApplyDepthOffsets.

    pos         : (n, 2) local-plane dot positions (stripped of depth)
    plane_now   : current frame's depth plane label ('Near', 'Far', 'Fix')
    plane_prev  : previous frame's depth plane label (None at frame 0)
    apply_correction : if False, skip the perspective scale (simulate pre-fix code)

    Returns:
      pos_out     : (n, 2) perspective-corrected local-plane positions
      z_depth     : scalar z world-offset for the current plane (metres)
    """
    if plane_now == 'Fix':
        return pos.copy(), z_for_plane('Fix')

    z_new = z_for_plane(plane_now)

    # Perspective correction (only at depth-change frames)
    angular_scale = 1.0
    if apply_correction and plane_prev is not None and plane_prev != plane_now \
            and plane_prev != 'Fix':
        z_old = z_for_plane(plane_prev)
        denom = VIEW_DIST_M + z_old
        if abs(denom) > 1e-4:
            angular_scale = (VIEW_DIST_M + z_new) / denom

    pos_out = pos * angular_scale
    return pos_out, z_new

# ── Screen-space projection ──────────────────────────────────────────────────
def project(pos_local, z_depth):
    """
    Perspective projection: screen_angle = arctan(x / z_world)
    Returns (n, 2) in degrees of visual angle.
    Mirrors GPU perspective division.
    """
    z_world = VIEW_DIST_M + z_depth
    # Small-angle: screen = local / z_world (radians) → degrees
    return np.degrees(pos_local / z_world)

def left_eye_disparity(z_depth):
    """Left-eye disparity shift (degrees) relative to cyclopean view."""
    z_world = VIEW_DIST_M + z_depth
    return np.degrees(IPD_M * 0.5 / z_world)

# ── Depth-plane schedule per condition ───────────────────────────────────────
def depth_schedule(condition, delayed_field_depth, n_frames=TOTAL_FRAMES):
    """
    Returns (planes_A, planes_B): list of depth-plane labels per frame
    for Field A (sub0,sub1) and Field B (sub2,sub3).

    DecoupledDots conditions:
      N  — no swap
      C  — color swap only (depth unchanged)
      Z  — depth swap at tStart (both fields exchange planes)
      CZ — color + depth swap at tStart
    """
    if delayed_field_depth == 'Near':
        B_pre, A_pre = 'Near', 'Far'
    else:
        B_pre, A_pre = 'Far', 'Near'

    depth_swap = condition in ('Z', 'CZ')

    if depth_swap:
        B_post = 'Far' if B_pre == 'Near' else 'Near'
        A_post = 'Far' if A_pre == 'Near' else 'Near'
    else:
        B_post, A_post = B_pre, A_pre

    planes_A = [A_pre if f < TRANS_START_F else A_post for f in range(n_frames)]
    planes_B = [B_pre if f < TRANS_START_F else B_post for f in range(n_frames)]
    return planes_A, planes_B

# ── Full trial simulation ─────────────────────────────────────────────────────
SimResult = namedtuple('SimResult', [
    'centroid_screen',    # list[4] of (n_frames,2) screen-space centroid in deg
    'z_depths',           # list[4] of (n_frames,) z values
    'planes',             # list[4] of (n_frames,) plane labels
])

def simulate_trial(condition='N', delayed_field_depth='Near',
                   heading_deg=0.0, cued=True,
                   apply_correction=True, seed=RNG_SEED):
    """
    Full trial simulation mirroring Unity's SimStepStimulus loop.

    Fields:
      Field A = sub0 (CW rot) + sub1 (CW rot)  — non-delayed
      Field B = sub2 (coherent trans / CW rot) + sub3 (non-coh) — delayed

    In CUED trials Field B is the translating field.
    In UNCUED trials Field A is the translating field.
    """
    planes_A, planes_B = depth_schedule(condition, delayed_field_depth)

    # sub0,sub1 → Field A; sub2,sub3 → Field B
    subfield_planes = [planes_A, planes_A, planes_B, planes_B]

    seeds  = [seed + i * 100003 for i in range(4)]
    rngs   = [np.random.default_rng(s + 99) for s in seeds]
    pos    = [make_dots(s) for s in seeds]

    rot_mpf   = ROT_SPD_DEG / SIM_HZ          # rotation deg per frame

    # centroid_screen[sf][f] = (2,) screen-space centroid in degrees
    centroid_screen = [np.zeros((TOTAL_FRAMES, 2)) for _ in range(4)]
    z_depths        = [np.zeros(TOTAL_FRAMES) for _ in range(4)]
    planes_out      = [[] for _ in range(4)]

    for f in range(TOTAL_FRAMES):
        # ── Step 1: motion ──────────────────────────────────────────────────
        for sf in range(4):
            visible = (sf < 2) or (f >= ONSET_F)
            if not visible:
                continue

            in_trans = TRANS_START_F <= f < TRANS_END_F
            plane_f  = subfield_planes[sf][f]
            mpd      = depth_corrected_mpd(plane_f)
            trans_mpf = TRANS_SPD_DEG * mpd / SIM_HZ

            if in_trans:
                if cued:  # Field B translates
                    if sf == 2:
                        pos[sf] = step_translate(pos[sf], heading_deg, trans_mpf,
                                                 rngs[sf])
                    elif sf == 3:
                        pos[sf] = step_noncoherent_balanced(pos[sf], trans_mpf,
                                                            rngs[sf])
                    else:  # Field A non-coherent during translation window
                        pos[sf] = step_noncoherent_balanced(pos[sf], trans_mpf,
                                                            rngs[sf])
                else:  # uncued: Field A translates
                    if sf == 0:
                        pos[sf] = step_translate(pos[sf], heading_deg, trans_mpf,
                                                 rngs[sf])
                    elif sf == 1:
                        pos[sf] = step_noncoherent_balanced(pos[sf], trans_mpf,
                                                            rngs[sf])
                    else:
                        pos[sf] = step_noncoherent_balanced(pos[sf], trans_mpf,
                                                            rngs[sf])
            else:
                # Rotation phase: Field A = CW (sign=-1), Field B = CCW (sign=+1)
                sign = -1 if sf < 2 else +1
                pos[sf] = step_rotate(pos[sf], sign, rot_mpf, rngs[sf])

        # ── Step 2: ApplyDepthOffsets (mirrors Unity exactly) ────────────────
        for sf in range(4):
            plane_now  = subfield_planes[sf][f]
            plane_prev = subfield_planes[sf][f - 1] if f > 0 else None

            pos_corr, z = apply_depth_offsets(pos[sf], plane_now, plane_prev,
                                              apply_correction=apply_correction)

            # Project to screen space and record centroid
            screen = project(pos_corr, z)
            centroid_screen[sf][f] = screen.mean(axis=0)
            z_depths[sf][f]        = z
            planes_out[sf].append(plane_now)

            # Store corrected local position for next frame's motion step
            pos[sf] = pos_corr

    return SimResult(centroid_screen, z_depths, planes_out)


# ── Plot helpers ─────────────────────────────────────────────────────────────
COND_COLORS   = {'N': '#444444', 'C': '#888888', 'Z': '#cc3333', 'CZ': '#d97f00'}
PREFIX_STYLE  = dict(lw=0.8, ls=':', alpha=0.55)
POSTFIX_STYLE = dict(lw=1.6, ls='-',  alpha=0.90)

def plot_trace_row(axes, result_N, result_Z, label_N, label_Z,
                   heading_deg, delayed_depth):
    """
    Plot sub2 and sub3 centroid X and Y for two conditions on the provided axes.
    axes: sequence of 4 Axes (sub2_X, sub2_Y, sub3_X, sub3_Y)
    """
    titles = ['Sub2  X  (coherent translator)', 'Sub2  Y  (coherent translator)',
              'Sub3  X  (non-coherent)', 'Sub3  Y  (non-coherent)']

    # Translation signal for reference
    mpd_now  = depth_corrected_mpd('Far' if delayed_depth == 'Near' else 'Near')
    # Use average mpd (rough guide)
    mpd_avg  = VIEW_DIST_M * np.tan(np.radians(1.0))
    trans_total_deg = TRANS_SPD_DEG * (TRANS_END_F - TRANS_START_F) / SIM_HZ

    for ax, sf_idx, comp in zip(axes,
                                 [2, 2, 3, 3],
                                 [0, 1, 0, 1]):   # 0=X, 1=Y
        y_N = result_N.centroid_screen[sf_idx][WIN_START:WIN_END, comp]
        y_Z = result_Z.centroid_screen[sf_idx][WIN_START:WIN_END, comp]

        # Baseline-subtract to remove pre-tStart position offset
        # (so traces overlap and we see only relative changes)
        base_frame_idx = 9 - 1  # frame just before tStart (relative index)
        y_N = y_N - y_N[base_frame_idx]
        y_Z = y_Z - y_Z[base_frame_idx]

        ax.axvline(0, color='#cc2222', lw=1.0, ls='--', zorder=3, label='tStart')
        ax.axhline(0, color='#cccccc', lw=0.5, zorder=1)

        ax.plot(REL_FRAMES, y_N, color=COND_COLORS['N'], label=label_N, **POSTFIX_STYLE)
        ax.plot(REL_FRAMES, y_Z, color=COND_COLORS['Z'], label=label_Z, **POSTFIX_STYLE)

        ax.set_xlabel('Frame rel. tStart', fontsize=7)
        ax.set_ylabel('Centroid (deg)', fontsize=7)
        ax.tick_params(labelsize=6.5)
        ax.set_xlim(REL_FRAMES[0] - 0.5, REL_FRAMES[-1] + 0.5)

    axes[0].set_title(f'Sub2 X   heading={heading_deg:.0f}°  delayed={delayed_depth}', fontsize=7.5)
    axes[1].set_title(f'Sub2 Y   heading={heading_deg:.0f}°  delayed={delayed_depth}', fontsize=7.5)
    axes[2].set_title(f'Sub3 X   (no net trans)  delayed={delayed_depth}', fontsize=7.5)
    axes[3].set_title(f'Sub3 Y   (no net trans)  delayed={delayed_depth}', fontsize=7.5)


# ── Artifact quantification ───────────────────────────────────────────────────
def centroid_jump(result, sf, comp, frame=TRANS_START_F):
    """
    Centroid shift at tStart: value at frame minus value at frame-1.
    sf: subfield index; comp: 0=X, 1=Y
    """
    return (result.centroid_screen[sf][frame,   comp] -
            result.centroid_screen[sf][frame-1, comp])


# ── Build figures ─────────────────────────────────────────────────────────────
def build_trace_figure(heading_deg=270.0):
    """
    4-row × 4-col figure.
    Rows: Near-delayed (N vs Z) with fix, Near-delayed (N vs Z) without fix,
          Far-delayed  (N vs Z) with fix, Far-delayed  (N vs Z) without fix
    Cols: sub2 X, sub2 Y, sub3 X, sub3 Y
    """
    nrows, ncols = 4, 4
    fig, axes = plt.subplots(nrows, ncols, figsize=(14, 11))
    fig.suptitle(
        f'Screen-space centroid traces — 18 frames around tStart\n'
        f'heading={heading_deg:.0f}°  CUED  |  '
        f'Grey=N(no swap)  Red=Z(depth swap)  '
        f'Note: centroid is insensitive to radial expansion (see Page 3 for expansion)',
        fontsize=9, fontweight='bold')
    fig.subplots_adjust(left=0.06, right=0.97, top=0.90, bottom=0.07,
                        wspace=0.38, hspace=0.52)

    row_specs = [
        ('Near', True,  'With perspective correction (current code)'),
        ('Near', False, 'WITHOUT perspective correction (pre-fix)'),
        ('Far',  True,  'With perspective correction (current code)'),
        ('Far',  False, 'WITHOUT perspective correction (pre-fix)'),
    ]

    for row_i, (depth, corrected, row_title) in enumerate(row_specs):
        res_N = simulate_trial('N', depth, heading_deg, cued=True,
                               apply_correction=corrected)
        res_Z = simulate_trial('Z', depth, heading_deg, cued=True,
                               apply_correction=corrected)

        row_axes = axes[row_i, :]
        plot_trace_row(row_axes, res_N, res_Z,
                       label_N='N (no swap)', label_Z='Z (depth swap)',
                       heading_deg=heading_deg, delayed_depth=depth)

        # Row label on the left
        axes[row_i, 0].set_ylabel(
            f'{row_title}\n{depth}-delayed\nCentroid (deg)', fontsize=6.5)

        # Legend only on first row
        if row_i == 0:
            axes[row_i, 0].legend(fontsize=6.5, loc='upper left')

    return fig


def build_expansion_figure():
    """
    The CORRECT diagnostic for perspective expansion.

    Centroid is insensitive to radial expansion (mean of a centered distribution = 0
    regardless of scale).  The artifact shows up as a sudden change in the ANGULAR
    SPREAD of dots.  We track:

      RMS angular eccentricity = sqrt( mean(x_screen^2 + y_screen^2) ) in degrees

    For sub3 (non-coherent balanced), the eccentricity distribution should be
    STATIONARY across all frames — any jump at tStart is pure artifact.

    We also show 9 individual probe dots placed at fixed starting positions on a
    3×3 grid (±2°, 0°) in screen space.  Their angular X positions are tracked.
    A scale correction that works correctly will keep them fixed; without it they
    contract (Near→Far) or expand (Far→Near).

    Layout: 3 rows × 2 cols
      Row 0: RMS angular eccentricity of sub3   (Near-delayed, Far-delayed)
      Row 1: Probe dot angular X positions      (Near-delayed, Far-delayed)
      Row 2: Sub2 translation X centroid        (Near-delayed, Far-delayed)
               — verifies translation signal is preserved across correction
    """
    fig, axes = plt.subplots(3, 2, figsize=(13, 10))
    fig.suptitle(
        'Angular spread & probe-dot traces — the correct diagnostic for radial expansion\n'
        'Grey=N  Solid-red=Z with correction  Dashed-red=Z without correction\n'
        'Red vertical = tStart.  If fix works: solid-red overlaps grey exactly.',
        fontsize=9, fontweight='bold')
    fig.subplots_adjust(left=0.08, right=0.97, top=0.88, bottom=0.07,
                        hspace=0.50, wspace=0.30)

    heading = 270.0   # downward

    # ── Probe dots: 9 positions on a regular grid ────────────────────────────
    probe_grid = []
    for px in [-2.0, 0.0, 2.0]:
        for py in [-2.0, 0.0, 2.0]:
            probe_grid.append((px, py))  # degrees

    def probe_to_meters(probe_pts):
        """Convert probe positions from degrees to metres at viewDist."""
        return [(np.tan(np.radians(x)) * VIEW_DIST_M,
                 np.tan(np.radians(y)) * VIEW_DIST_M)
                for x, y in probe_pts]

    probe_m = probe_to_meters(probe_grid)

    def simulate_probes(depth, corrected):
        """
        Simulate probe dots through ApplyDepthOffsets only (no motion — they
        just sit there and we track their screen-space position).
        This isolates the depth-offset code path cleanly.
        """
        planes_A, planes_B = depth_schedule('Z', depth)
        planes_N_A, planes_N_B = depth_schedule('N', depth)

        results_Z, results_N = {}, {}

        for sf_idx, planes_Z, planes_N in [
            (2, planes_B, planes_N_B),   # sub2 (Field B, delayed)
            (3, planes_B, planes_N_B),   # sub3 (same planes as sub2)
        ]:
            # Start each probe dot at its grid position (in metres)
            pos_Z = np.array(probe_m, dtype=float)
            pos_N = np.array(probe_m, dtype=float)

            Z_traj = []   # list of (n_probe, 2) screen-deg arrays per frame
            N_traj = []

            for f in range(TOTAL_FRAMES):
                plane_z_now  = planes_Z[f]
                plane_z_prev = planes_Z[f-1] if f > 0 else None
                plane_n_now  = planes_N[f]
                plane_n_prev = planes_N[f-1] if f > 0 else None

                # Apply depth correction
                pos_Z_c, z_Z = apply_depth_offsets(pos_Z, plane_z_now,
                                                    plane_z_prev, corrected)
                pos_N_c, z_N = apply_depth_offsets(pos_N, plane_n_now,
                                                    plane_n_prev, True)  # N always "correct"

                # Screen-space
                Z_traj.append(project(pos_Z_c, z_Z).copy())
                N_traj.append(project(pos_N_c, z_N).copy())

                # Store corrected positions (mirror Unity: pos persists)
                pos_Z = pos_Z_c.copy()
                pos_N = pos_N_c.copy()

            results_Z[sf_idx] = Z_traj
            results_N[sf_idx] = N_traj

        return results_Z, results_N

    for col, depth in enumerate(['Near', 'Far']):
        # ── Row 0: RMS angular eccentricity of sub3 ───────────────────────────
        ax0 = axes[0, col]

        for corrected, label, color, ls, lw in [
            (True,  'N (baseline)',   '#444444', '-',  1.6),
            (True,  'Z + correction', '#cc3333', '-',  1.6),
            (False, 'Z – correction', '#cc3333', '--', 1.0),
        ]:
            if label.startswith('N'):
                cond_str = 'N'
            elif '+ correction' in label:
                cond_str = 'Z'
            else:
                cond_str = 'Z'

            # Use full simulation to get screen positions for RMS eccentricity
            res = simulate_trial(cond_str, depth, heading, cued=True,
                                 apply_correction=corrected, seed=RNG_SEED)

            rms_ecc = []
            for f in WINDOW:
                planes_sf = depth_schedule(cond_str, depth)[1]   # Field B = sub2,3
                z = res.z_depths[3][f]
                # Re-derive dot positions from centroid is not possible without storing.
                # Instead, simulate probe dots through the same pipeline.
                break  # use probe-dot simulation below

            # Use probe simulation for RMS eccentricity (stationary dots only)
            res_Z_probes, res_N_probes = simulate_probes(depth, corrected)
            traj = res_N_probes[3] if cond_str == 'N' else res_Z_probes[3]

            rms_ecc = []
            for f in WINDOW:
                xy = traj[f]   # (n_probe, 2)
                ecc = np.sqrt((xy[:, 0]**2 + xy[:, 1]**2))
                rms_ecc.append(np.sqrt(np.mean(ecc**2)))

            ax0.plot(REL_FRAMES, rms_ecc, color=color, ls=ls, lw=lw, label=label)

        ax0.axvline(0, color='#cc2222', lw=1.0, ls=':', zorder=3)
        ax0.set_xlabel('Frame rel. tStart', fontsize=8)
        ax0.set_ylabel('RMS angular eccentricity (deg)', fontsize=8)
        ax0.set_title(f'Sub3 RMS spread  {depth}-delayed\n'
                      f'(stationary probe dots — any jump = artifact)', fontsize=8)
        ax0.tick_params(labelsize=7)
        if col == 0:
            ax0.legend(fontsize=7, loc='lower right')

        # ── Row 1: Probe dot angular X positions ─────────────────────────────
        ax1 = axes[1, col]

        res_Z_probes_fix, res_N_probes_fix     = simulate_probes(depth, True)
        res_Z_probes_nofix, res_N_probes_nofix = simulate_probes(depth, False)

        n_probe = len(probe_m)
        colors_probe = plt.cm.tab10(np.linspace(0, 0.9, n_probe))

        for pi in range(n_probe):
            x_N   = [res_N_probes_fix[2][f][pi, 0]   for f in WINDOW]
            x_Zf  = [res_Z_probes_fix[2][f][pi, 0]   for f in WINDOW]
            x_Znf = [res_Z_probes_nofix[2][f][pi, 0] for f in WINDOW]

            base = x_N[9 - 1]  # value just before tStart
            x_N   = [v - base for v in x_N]
            x_Zf  = [v - base for v in x_Zf]
            x_Znf = [v - base for v in x_Znf]

            lbl_n = 'N' if pi == 0 else None
            lbl_z = 'Z+fix' if pi == 0 else None
            lbl_nf = 'Z-fix' if pi == 0 else None
            ax1.plot(REL_FRAMES, x_N,   color='#888888', lw=1.0, ls='-',  alpha=0.7, label=lbl_n)
            ax1.plot(REL_FRAMES, x_Zf,  color='#cc3333', lw=1.2, ls='-',  alpha=0.7, label=lbl_z)
            ax1.plot(REL_FRAMES, x_Znf, color='#cc3333', lw=0.8, ls='--', alpha=0.5, label=lbl_nf)

        ax1.axvline(0, color='#cc2222', lw=1.0, ls=':', zorder=3)
        ax1.axhline(0, color='k', lw=0.5)
        ax1.set_xlabel('Frame rel. tStart', fontsize=8)
        ax1.set_ylabel('ΔAngular X (deg, baseline-sub.)', fontsize=8)
        ax1.set_title(f'Probe dot angular X  {depth}-delayed\n'
                      f'(9 stationary probes — step = expansion artifact)', fontsize=8)
        ax1.tick_params(labelsize=7)
        if col == 0:
            ax1.legend(fontsize=7, loc='lower right')

        # ── Row 2: Sub2 translation signal (centroid X) ───────────────────────
        ax2 = axes[2, col]

        for corrected, label, color, ls in [
            (True,  'N + fix',  '#444444', '-'),
            (True,  'Z + fix',  '#cc3333', '-'),
            (False, 'Z − fix',  '#ff8888', '--'),
        ]:
            cond_str = 'N' if label.startswith('N') else 'Z'
            res = simulate_trial(cond_str, depth, heading, cued=True,
                                 apply_correction=corrected, seed=RNG_SEED)
            x_c = res.centroid_screen[2][WIN_START:WIN_END, 0]
            base = x_c[8]
            ax2.plot(REL_FRAMES, x_c - base, color=color, ls=ls, lw=1.6, label=label)

        ax2.axvline(0, color='#cc2222', lw=1.0, ls=':', zorder=3)
        ax2.axhline(0, color='k', lw=0.5)
        ax2.set_xlabel('Frame rel. tStart', fontsize=8)
        ax2.set_ylabel('Sub2 centroid X (deg, baseline-sub.)', fontsize=8)
        ax2.set_title(f'Translation signal  {depth}-delayed  heading={heading:.0f}°\n'
                      f'(should be same for N and Z)', fontsize=8)
        ax2.tick_params(labelsize=7)
        if col == 0:
            ax2.legend(fontsize=7, loc='lower right')

    return fig


def build_artifact_summary_figure():
    """
    Bar chart: centroid Y-jump at tStart for sub3 (no net translation),
    for N and Z conditions, Near and Far delayed, with and without correction.
    Colour-coded by condition.  Shows translation signal for reference.
    """
    headings = [0.0, 90.0, 180.0, 270.0]
    configs = [
        ('Near', True),  ('Near', False),
        ('Far',  True),  ('Far',  False),
    ]

    fig, axes = plt.subplots(2, 2, figsize=(12, 7))
    fig.suptitle(
        'Sub3 centroid Y-jump at tStart (1 frame) — pure artifact signal\n'
        'N (no swap) should have ≈0; Z should match N with correction applied',
        fontsize=9, fontweight='bold')
    fig.subplots_adjust(left=0.08, right=0.97, top=0.87, bottom=0.10,
                        hspace=0.45, wspace=0.35)

    trans_signal_deg = TRANS_SPD_DEG / SIM_HZ   # translation per frame (degrees)

    for ax_idx, heading in enumerate(headings):
        ax = axes.flat[ax_idx]

        labels, bar_vals = [], []
        colors = []

        for depth, corrected in configs:
            res_N = simulate_trial('N', depth, heading, cued=True,
                                   apply_correction=corrected)
            res_Z = simulate_trial('Z', depth, heading, cued=True,
                                   apply_correction=corrected)

            jump_N = centroid_jump(res_N, sf=3, comp=1)  # sub3 Y
            jump_Z = centroid_jump(res_Z, sf=3, comp=1)

            tag = f"{'✓' if corrected else '✗'} {depth}"
            labels += [f'N {tag}', f'Z {tag}']
            bar_vals += [jump_N, jump_Z]
            colors += ['#888888', ('#cc3333' if corrected else '#ffaaaa')]

        x = np.arange(len(labels))
        bars = ax.bar(x, bar_vals, color=colors, edgecolor='k', lw=0.5, width=0.7)

        # Reference lines
        ax.axhline(0,               color='k',       lw=0.8)
        ax.axhline( trans_signal_deg, color='#2255aa', lw=1.0, ls='--',
                    label=f'+1-frame trans signal ({trans_signal_deg*1000:.1f} mdeg)')
        ax.axhline(-trans_signal_deg, color='#2255aa', lw=1.0, ls='--')

        ax.set_xticks(x)
        ax.set_xticklabels(labels, rotation=55, ha='right', fontsize=7)
        ax.set_ylabel('Sub3 centroid ΔY (deg)', fontsize=8)
        ax.set_title(f'heading = {heading:.0f}°', fontsize=8.5)
        ax.tick_params(labelsize=7)
        if ax_idx == 0:
            ax.legend(fontsize=7, loc='upper right')

    return fig


def relative_disparity_arcmin(z_depth):
    """
    Relative binocular disparity of a dot w.r.t. fixation (arcmin).
    Fixation is at VIEW_DIST_M; dot is at VIEW_DIST_M + z_depth.
    Positive = crossed (nearer than fixation), negative = uncrossed (farther).
    Formula: δ = IPD × (1/z_dot − 1/z_fix)  [radians], converted to arcmin.
    """
    z_dot = VIEW_DIST_M + z_depth
    z_fix = VIEW_DIST_M
    delta_rad = IPD_M * (1.0/z_dot - 1.0/z_fix)
    return np.degrees(delta_rad) * 60.0   # positive = crossed = near


def build_disparity_trace_figure(heading_deg=270.0):
    """
    Show RELATIVE binocular disparity (arcmin, w.r.t. fixation) of the
    depth plane over the tStart window.

    The disparity step at tStart is INHERENT to the Z condition — it cannot
    be eliminated without removing the depth swap.  With perspective correction
    in place this is the only remaining "pop" signal.

    Near plane (~1.95 m): +2.76 arcmin crossed
    Far  plane (~2.05 m): −2.55 arcmin uncrossed
    Total step (Near→Far): ~5.3 arcmin — well above stereo threshold (~0.5 arcmin)
    """
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    fig.suptitle(
        f'Relative binocular disparity at depth-swap frame  (heading={heading_deg:.0f}°)\n'
        'This step CANNOT be eliminated — it is the inherent signal of a Z/CZ condition.\n'
        'Grey=N (no swap, constant disparity)   Red=Z (depth swap at tStart = disparity step)',
        fontsize=8.5, fontweight='bold')
    fig.subplots_adjust(left=0.09, right=0.97, top=0.82, bottom=0.12,
                        wspace=0.35)

    for ax_idx, depth in enumerate(['Near', 'Far']):
        ax = axes[ax_idx]
        for cond, color, lw in [('N', '#444444', 1.8), ('Z', '#cc3333', 1.8)]:
            res = simulate_trial(cond, depth, heading_deg, cued=True,
                                 apply_correction=True)
            disps = [relative_disparity_arcmin(res.z_depths[2][f]) for f in WINDOW]
            ax.plot(REL_FRAMES, disps, color=color, lw=lw, label=cond)

        # Stereo threshold reference
        ax.axvline(0, color='#cc2222', lw=1.0, ls='--', label='tStart')
        ax.axhline(0, color='k', lw=0.6)
        ax.axhline( 0.5, color='#aaaaaa', lw=0.7, ls=':', label='±stereo thresh (~0.5 arcmin)')
        ax.axhline(-0.5, color='#aaaaaa', lw=0.7, ls=':')

        # Annotate the step size
        z_pre  = z_for_plane('Near' if depth == 'Near' else 'Far')
        z_post = z_for_plane('Far'  if depth == 'Near' else 'Near')
        step   = relative_disparity_arcmin(z_post) - relative_disparity_arcmin(z_pre)
        ax.annotate(f'Step = {step:+.1f} arcmin\n({abs(step)/0.5:.0f}× stereo thresh)',
                    xy=(1, relative_disparity_arcmin(z_post)),
                    xytext=(3, (relative_disparity_arcmin(z_pre) +
                                relative_disparity_arcmin(z_post)) / 2),
                    fontsize=7.5, color='#cc3333',
                    arrowprops=dict(arrowstyle='->', color='#cc3333', lw=0.8))

        ax.set_xlabel('Frame rel. tStart', fontsize=8)
        ax.set_ylabel('Relative disparity (arcmin, + = crossed)', fontsize=8)
        ax.set_title(f'{depth}-delayed (with perspective correction)', fontsize=8.5)
        ax.tick_params(labelsize=7)
        if ax_idx == 0:
            ax.legend(fontsize=7, loc='center right')

    return fig


def build_explainer_page():
    fig = plt.figure(figsize=(11, 8.5))
    fig.patch.set_facecolor('white')
    ax = fig.add_axes([0.05, 0.03, 0.90, 0.93])
    ax.axis('off')

    def t(y, text, size=8.5, weight='normal', color='#111111', indent=0.0):
        ax.text(indent, y, text, transform=ax.transAxes,
                ha='left', va='top', fontsize=size,
                fontweight=weight, color=color, family='monospace')

    def h(y, text): t(y, text, 10, 'bold', '#1a1a6b')

    y = 0.97
    h(y, 'headset_faithful_traces.py — verification of perspective correction'); y -= 0.05

    h(y, 'Faithfulness to headset rendering'); y -= 0.03
    for line in [
        '  Unity renders with a perspective camera: x_screen = x_world / z_world (GPU perspective division).',
        '  Previous trace scripts used x/viewDist (orthographic) — blind to depth-dependent angular shifts.',
        '  This script computes the same perspective division after running ApplyDepthOffsets exactly.',
    ]:
        t(y, line, 8.0); y -= 0.028
    y -= 0.015

    h(y, 'Key numbers  (depthSeparation=0.05 m, viewDist=2.0 m)'); y -= 0.03
    for line in [
        '  Near: z=−0.05 m → z_world=1.95 m    Far: z=+0.05 m → z_world=2.05 m',
        '',
        '  WITHOUT correction — dot at 2° eccentricity, Near→Far:',
        '    screen_x before = tan(2°)×2.0/1.95 = 2.052°',
        '    screen_x after  = tan(2°)×2.0/2.05 = 1.952°    Δ = −6.0 arcmin (inward contraction)',
        '  At aperture edge (3.5°): Δ = −10.5 arcmin → apparent velocity = 13.1 °/sec (5.8× signal)',
        '',
        '  WITH correction — angularScale = 2.05/1.95 = 1.0513:',
        '    screen_x after = tan(2°)×2.0×1.0513/2.05 = 2.052°    Δ = 0.00 arcmin  ✓',
        '',
        '  INHERENT disparity step (cannot be fixed — this IS the depth-swap):',
        '    Near: relative disparity = IPD×(1/1.95−1/2.0) = +2.76 arcmin  (crossed)',
        '    Far:  relative disparity = IPD×(1/2.05−1/2.0) = −2.55 arcmin  (uncrossed)',
        '    Step at tStart (Near→Far): ~5.3 arcmin  ≈ 11× stereo threshold (0.5 arcmin)',
        '    This is what produces the residual "pop" percept after all code fixes.',
    ]:
        t(y, line, 8.0); y -= 0.028
    y -= 0.015

    h(y, 'How to read Page 1 (expansion diagnostic)'); y -= 0.03
    for line in [
        '  Row 0: RMS angular eccentricity of 9 stationary probe dots.',
        '    N (grey) = flat.  Z without correction (dashed) = drops ~5% at tStart.',
        '    Z with correction (solid red) = flat, overlapping grey.  Artifact eliminated.',
        '  Row 1: Individual probe dot angular X positions (probes on 3×3 grid at ±2°).',
        '    Same result.  Dashed shows the inward/outward step; solid shows clean.',
        '  Row 2: Sub2 translation signal (centroid X) — should ramp equally for N and Z.',
        '',
        '  How to use: for any future depth-swap experiment, run this script first.',
        '    Page 1 Row 0: solid-red must overlap grey.  Page 4: disparity step magnitude.',
    ]:
        t(y, line, 8.0); y -= 0.028

    return fig


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    os.makedirs(OUT_DIR, exist_ok=True)

    print('Simulating trials and computing centroid traces...')

    # Quick console report: sub3 Y-jump at tStart for N and Z, Near-delayed
    for corrected, tag in [(True, 'WITH correction'), (False, 'WITHOUT correction')]:
        res_N = simulate_trial('N', 'Near', 270.0, cued=True, apply_correction=corrected)
        res_Z = simulate_trial('Z', 'Near', 270.0, cued=True, apply_correction=corrected)
        j_N = centroid_jump(res_N, sf=3, comp=1)
        j_Z = centroid_jump(res_Z, sf=3, comp=1)
        trans1f = TRANS_SPD_DEG / SIM_HZ
        print(f'\n  {tag}  (heading=270°, Near-delayed)')
        print(f'    N sub3 Y-jump at tStart: {j_N*1000:.2f} mdeg')
        print(f'    Z sub3 Y-jump at tStart: {j_Z*1000:.2f} mdeg'
              f'  ({j_Z/trans1f*100:.1f}% of 1-frame translation signal)')

    print('\nBuilding figures...')
    with PdfPages(OUT_PDF) as pdf:
        # Page 1: expansion / probe-dot figure — KEY DIAGNOSTIC
        fig1 = build_expansion_figure()
        pdf.savefig(fig1, bbox_inches='tight');  plt.close(fig1)
        print('  Page 1: expansion / probe-dot figure done')

        # Page 2: full centroid traces heading=270° (note: centroid insensitive to expansion)
        fig2 = build_trace_figure(heading_deg=270.0)
        pdf.savefig(fig2, bbox_inches='tight');  plt.close(fig2)
        print('  Page 2: centroid traces (heading=270°) done')

        # Page 3: artifact summary (sub3 Y-jumps — mostly noise due to centroid insensitivity)
        fig3 = build_artifact_summary_figure()
        pdf.savefig(fig3, bbox_inches='tight');  plt.close(fig3)
        print('  Page 3: artifact summary done')

        # Page 4: binocular disparity traces — shows the INHERENT disparity step
        fig4 = build_disparity_trace_figure(heading_deg=270.0)
        pdf.savefig(fig4, bbox_inches='tight');  plt.close(fig4)
        print('  Page 4: disparity traces done')

        # Page 5: explainer
        fig5 = build_explainer_page()
        pdf.savefig(fig5, bbox_inches='tight');  plt.close(fig5)
        print('  Page 5: explainer done')

    print(f'\nSaved → {OUT_PDF}')


if __name__ == '__main__':
    main()
