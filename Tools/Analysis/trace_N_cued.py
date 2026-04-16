#!/usr/bin/env python3
"""
trace_N_cued.py
---------------
Dot trajectory traces for the N-condition CUED arm.
Shows the path of every dot from delayed-field onset (frame 56)
through and past translation (frames 78–84).

Field A (S0+S1, non-delayed, red/salmon): rotating CW throughout.
Field B (S2, delayed, solid green): coherent translator — rotates CCW, then translates.
Field B (S3, delayed, pale green): non-coherent — rotates CCW, then splits into 8 directions.

Each dot's position is drawn as a continuous line; time runs along the line.
Dots are coloured by role. A filled circle marks T_START position on each trace.
"""

import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
matplotlib.rcParams['pdf.fonttype'] = 42
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

OUT = os.path.normpath(os.path.join(
    os.path.dirname(__file__),
    '../../Agents/SwapPilot/Figures/trace_N_cued.svg'))
os.makedirs(os.path.dirname(OUT), exist_ok=True)

# ── Parameters ─────────────────────────────────────────────────────────────────
SIM_HZ          = 75.0
ROT_SPD_DEG     = 81.0          # deg / sec
TRANS_SPD_DEG   = 2.26          # deg / sec
AP_RAD          = 3.5           # deg
ONSET_F         = 56
T_START         = 78
T_END           = 84
TOTAL_FRAMES    = 100           # show a few frames after translation
HEADING_DEG     = 0.0           # rightward → translation shifts traces to the right
N_DOTS          = 16            # per subfield (keeps figure readable)
SEED            = 42

ROT_PER_FRAME   = ROT_SPD_DEG   / SIM_HZ    # 1.08 °/frame
TRANS_PER_FRAME = TRANS_SPD_DEG / SIM_HZ    # 0.030 °/frame

heading_rad = np.radians(HEADING_DEG)
TRANS_VEC   = np.array([np.cos(heading_rad), np.sin(heading_rad)]) * TRANS_PER_FRAME

# 8 balanced non-coherent directions (same as StimulusBuilder.cs)
_d = np.array([[1,0],[1,1],[0,1],[-1,1],[-1,0],[-1,-1],[0,-1],[1,-1]], dtype=float)
NC_DIRS = (_d / np.linalg.norm(_d, axis=1, keepdims=True)) * TRANS_PER_FRAME

def rot(pos, sign):
    """Rotate positions by sign × ROT_PER_FRAME degrees around origin."""
    ang = np.radians(sign * ROT_PER_FRAME)
    c, s = np.cos(ang), np.sin(ang)
    R = np.array([[c, -s], [s, c]])
    return pos @ R.T

def respawn(pos, rng):
    mag = np.linalg.norm(pos, axis=1)
    oob = mag > AP_RAD
    if oob.any():
        n  = oob.sum()
        u  = rng.random(n)
        th = rng.random(n) * 2 * np.pi
        pos[oob] = np.column_stack([AP_RAD * np.sqrt(u) * np.cos(th),
                                     AP_RAD * np.sqrt(u) * np.sin(th)])
    return pos

def make_dots(seed):
    rng = np.random.default_rng(seed)
    u  = rng.random(N_DOTS)
    th = rng.random(N_DOTS) * 2 * np.pi
    return np.column_stack([AP_RAD * np.sqrt(u) * np.cos(th),
                             AP_RAD * np.sqrt(u) * np.sin(th)])

# ── Simulate ───────────────────────────────────────────────────────────────────
rngs = [np.random.default_rng(SEED + sf * 99) for sf in range(4)]
pos  = [make_dots(SEED + sf * 7)  for sf in range(4)]

# Burn-in Field A from frame 0 to ONSET_F so it's in its natural rotated state
for _ in range(ONSET_F):
    pos[0] = respawn(rot(pos[0], -1), rngs[0])
    pos[1] = respawn(rot(pos[1], -1), rngs[1])

# Record history from ONSET_F onward
hist = [[] for _ in range(4)]   # hist[sf][t] = (N,2) position array

for f in range(ONSET_F, TOTAL_FRAMES):
    for sf in range(4):
        hist[sf].append(pos[sf].copy())

    in_trans = T_START <= f < T_END

    if in_trans:
        # CUED: S2 translates coherently, S3 non-coherent, S0+S1 keep rotating
        pos[0] = respawn(rot(pos[0], -1), rngs[0])
        pos[1] = respawn(rot(pos[1], -1), rngs[1])
        pos[2] = respawn(pos[2] + TRANS_VEC,                          rngs[2])
        pos[3] = respawn(pos[3] + NC_DIRS[np.arange(N_DOTS) % 8],    rngs[3])
    else:
        # Outside translation: Field A CW, Field B CCW
        pos[0] = respawn(rot(pos[0], -1), rngs[0])
        pos[1] = respawn(rot(pos[1], -1), rngs[1])
        pos[2] = respawn(rot(pos[2], +1), rngs[2])
        pos[3] = respawn(rot(pos[3], +1), rngs[3])

# Convert to arrays: shape (n_frames, N_DOTS, 2)
frames_shown = list(range(ONSET_F, TOTAL_FRAMES))
n_frames     = len(frames_shown)

H = [np.stack(hist[sf], axis=0) for sf in range(4)]  # (n_frames, N_DOTS, 2)

# ── Plot ───────────────────────────────────────────────────────────────────────
fig, ax = plt.subplots(1, 1, figsize=(6.5, 6.5))
fig.patch.set_facecolor('white')

ax.set_aspect('equal')
ax.set_facecolor('white')

# Aperture
aperture = plt.Circle((0, 0), AP_RAD, color='#f2f2f2', zorder=0)
ax.add_patch(aperture)
aperture_edge = plt.Circle((0, 0), AP_RAD, color='#cccccc', fill=False,
                            lw=0.8, zorder=1)
ax.add_patch(aperture_edge)

# T_START and T_END reference frames (index into hist)
ti_start = T_START - ONSET_F
ti_end   = T_END   - ONSET_F

# ── Draw traces ───────────────────────────────────────────────────────────────
# Colour scheme
C_A    = '#cc5533'   # Field A (non-delayed, rotating)
C_S2   = '#1a7a3a'   # S2 coherent translator
C_S3   = '#88bb99'   # S3 non-coherent

alpha_pre   = 0.30   # frames before T_START
alpha_trans = 0.90   # translation window
alpha_post  = 0.55   # frames after T_END

for sf in range(4):
    if sf == 0:   col = C_A;  lw = 0.9;  zorder = 2
    elif sf == 1: col = C_A;  lw = 0.9;  zorder = 2
    elif sf == 2: col = C_S2; lw = 1.4;  zorder = 4
    else:         col = C_S3; lw = 0.9;  zorder = 3

    for d in range(N_DOTS):
        x = H[sf][:, d, 0].copy()
        y = H[sf][:, d, 1].copy()

        # Break line at respawn teleports: large jumps = dot went OOB and reappeared
        JUMP_THRESH = AP_RAD * 0.6
        dx = np.diff(x); dy = np.diff(y)
        jumps = np.where(np.sqrt(dx**2 + dy**2) > JUMP_THRESH)[0] + 1
        xb, yb = x.astype(float), y.astype(float)
        for j in jumps:
            xb = np.insert(xb, j, np.nan)
            yb = np.insert(yb, j, np.nan)
        # Recompute insertion-shifted indices for segment boundaries
        offsets = np.zeros(n_frames, dtype=int)
        for j in jumps:
            offsets[j:] += 1
        ts  = ti_start + offsets[min(ti_start, n_frames-1)]
        te  = ti_end   + offsets[min(ti_end,   n_frames-1)]
        end = len(xb) - 1

        def seg(a, b, alpha):
            if b <= a: return
            ax.plot(xb[a:b+1], yb[a:b+1], color=col, lw=lw, alpha=alpha,
                    solid_capstyle='round', zorder=zorder)

        seg(0,   ts,   alpha_pre)
        seg(ts,  te,   alpha_trans)
        seg(te,  end,  alpha_post)

        # Mark T_START position with a small filled dot
        if sf == 2:  # highlight the coherent translator most
            ax.plot(x[ti_start], y[ti_start], 'o', color=col,
                    ms=3.5, zorder=5, alpha=0.9)

# Shade translation window as a subtle horizontal band?
# No — that doesn't make sense in x/y space. Instead, annotate with arrow.

# Translation arrow (in the aperture, along heading direction)
arrow_len = 0.6
ax.annotate('',
    xy     =(arrow_len * np.cos(heading_rad), arrow_len * np.sin(heading_rad)),
    xytext =(0, 0),
    arrowprops=dict(arrowstyle='->', color='#444444', lw=1.5),
    zorder=10)
ax.text(arrow_len * np.cos(heading_rad) + 0.08,
        arrow_len * np.sin(heading_rad) + 0.08,
        f'{HEADING_DEG:.0f}°\nheading',
        fontsize=7, color='#444444', va='bottom', ha='left')

# Fixation
ax.plot(0, 0, '+', color='#333333', ms=8, mew=1.2, zorder=6)

ax.set_xlim(-AP_RAD - 0.5, AP_RAD + 1.0)
ax.set_ylim(-AP_RAD - 0.5, AP_RAD + 0.5)
ax.set_xlabel('Horizontal position (°)', fontsize=9)
ax.set_ylabel('Vertical position (°)', fontsize=9)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.tick_params(labelsize=8)

# ── Legend ────────────────────────────────────────────────────────────────────
legend_elements = [
    mpatches.Patch(color=C_A,  label='Field A — non-delayed, rotating (CW)'),
    mpatches.Patch(color=C_S2, label='Field B S2 — delayed, coherent translator'),
    mpatches.Patch(color=C_S3, label='Field B S3 — delayed, non-coherent'),
]
ax.legend(handles=legend_elements, fontsize=7.5, frameon=False,
          loc='lower right')

# Time annotation
n_rot_frames = T_START - ONSET_F
ax.set_title(
    f'N condition · CUED arm · dot trajectories\n'
    f'Frames {ONSET_F}→{TOTAL_FRAMES-1}  '
    f'(delayed onset → +{TOTAL_FRAMES-1-ONSET_F} frames)  '
    f'[translation: frames {T_START}–{T_END}, '
    f'{(T_END-T_START)/SIM_HZ*1000:.0f} ms]\n'
    f'Darker/more opaque traces = translation window  ·  '
    f'● marks T_start on S2\n'
    f'rot {ROT_SPD_DEG}°/s  ·  trans {TRANS_SPD_DEG}°/s  ·  aperture {AP_RAD}° radius',
    fontsize=8, loc='left')

plt.tight_layout()
plt.savefig(OUT, bbox_inches='tight', facecolor='white')
plt.savefig(OUT.replace('.svg', '.png'), dpi=150, bbox_inches='tight', facecolor='white')
print(f'Saved: {OUT}')
print(f'Saved: {OUT.replace(".svg", ".png")}')
