#!/usr/bin/env python3
"""
trace_N_cued_vs_uncued.py
--------------------------
CUED vs UNCUED side-by-side with IDENTICAL dot starting positions (same seed).
Any structural asymmetry outside the translation window will be immediately visible.

N condition (no depth/color swap).
Field A (S0+S1, red):  non-delayed, rotates CW from frame 0.
Field B (S2+S3, green): delayed, appears at frame 56, rotates CCW.

CUED:   S2 translates linearly at tStart; S3 non-coherent.  S0+S1 keep rotating.
UNCUED: S0 translates linearly at tStart; S1 non-coherent.  S2+S3 keep rotating.

Both panels use the SAME random seed → identical dot positions everywhere except
the 6-frame translation window.  Any difference outside that band = artifact.
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
    '../../Agents/SwapPilot/Figures/trace_N_cued_vs_uncued.svg'))
os.makedirs(os.path.dirname(OUT), exist_ok=True)

# ── Parameters (match Exp_DecoupledDots_005m) ──────────────────────────────────
SIM_HZ          = 75.0
ROT_SPD_DEG     = 81.0
TRANS_SPD_DEG   = 2.26
AP_RAD          = 3.5           # deg
ONSET_F         = 56
T_START         = 78
T_END           = 84
SHOW_TO         = 100           # show a few frames post-translation
HEADING_DEG     = 0.0           # rightward
N_DOTS          = 20            # per subfield
SEED            = 42

ROT_PER_FRAME   = ROT_SPD_DEG   / SIM_HZ
TRANS_PER_FRAME = TRANS_SPD_DEG / SIM_HZ

heading_rad = np.radians(HEADING_DEG)
TRANS_VEC   = np.array([np.cos(heading_rad), np.sin(heading_rad)]) * TRANS_PER_FRAME

_d = np.array([[1,0],[1,1],[0,1],[-1,1],[-1,0],[-1,-1],[0,-1],[1,-1]], dtype=float)
NC_DIRS = (_d / np.linalg.norm(_d, axis=1, keepdims=True)) * TRANS_PER_FRAME

def rot(pos, sign):
    ang = np.radians(sign * ROT_PER_FRAME)
    c, s = np.cos(ang), np.sin(ang)
    return pos @ np.array([[c, -s], [s, c]]).T

def respawn(pos, rng):
    mag = np.linalg.norm(pos, axis=1)
    oob = mag > AP_RAD
    if oob.any():
        n  = oob.sum()
        u  = rng.random(n); th = rng.random(n) * 2 * np.pi
        pos[oob] = np.column_stack([AP_RAD * np.sqrt(u) * np.cos(th),
                                     AP_RAD * np.sqrt(u) * np.sin(th)])
    return pos

def make_dots(seed):
    rng = np.random.default_rng(seed)
    u  = rng.random(N_DOTS); th = rng.random(N_DOTS) * 2 * np.pi
    return np.column_stack([AP_RAD * np.sqrt(u) * np.cos(th),
                             AP_RAD * np.sqrt(u) * np.sin(th)])

def simulate(cued):
    """Simulate from frame 0; return position history from ONSET_F onward."""
    rngs = [np.random.default_rng(SEED + sf * 99) for sf in range(4)]
    pos  = [make_dots(SEED + sf * 7)  for sf in range(4)]

    # Burn-in Field A for ONSET_F frames (Field B stationary / hidden)
    for _ in range(ONSET_F):
        pos[0] = respawn(rot(pos[0], -1), rngs[0])
        pos[1] = respawn(rot(pos[1], -1), rngs[1])

    hist = [[] for _ in range(4)]

    for f in range(ONSET_F, SHOW_TO):
        for sf in range(4):
            hist[sf].append(pos[sf].copy())

        in_trans = T_START <= f < T_END

        if in_trans:
            if cued:
                pos[0] = respawn(rot(pos[0], -1),                              rngs[0])
                pos[1] = respawn(rot(pos[1], -1),                              rngs[1])
                pos[2] = respawn(pos[2] + TRANS_VEC,                           rngs[2])
                pos[3] = respawn(pos[3] + NC_DIRS[np.arange(N_DOTS) % 8],     rngs[3])
            else:
                pos[0] = respawn(pos[0] + TRANS_VEC,                           rngs[0])
                pos[1] = respawn(pos[1] + NC_DIRS[np.arange(N_DOTS) % 8],     rngs[1])
                pos[2] = respawn(rot(pos[2], +1),                              rngs[2])
                pos[3] = respawn(rot(pos[3], +1),                              rngs[3])
        else:
            pos[0] = respawn(rot(pos[0], -1), rngs[0])
            pos[1] = respawn(rot(pos[1], -1), rngs[1])
            pos[2] = respawn(rot(pos[2], +1), rngs[2])
            pos[3] = respawn(rot(pos[3], +1), rngs[3])

    return [np.stack(h, axis=0) for h in hist]   # (n_frames, N_DOTS, 2)

H_cued   = simulate(cued=True)
H_uncued = simulate(cued=False)

n_frames = H_cued[0].shape[0]
ti_start = T_START - ONSET_F
ti_end   = T_END   - ONSET_F

# ── Colours ────────────────────────────────────────────────────────────────────
C_A_coh  = '#cc3333'   # Field A coherent translator (UNCUED: S0)
C_A_nc   = '#ee9999'   # Field A non-coherent (UNCUED: S1)
C_A_rot  = '#cc3333'   # Field A rotating
C_B_coh  = '#1a7a3a'   # Field B coherent translator (CUED: S2)
C_B_nc   = '#88cc99'   # Field B non-coherent (CUED: S3)
C_B_rot  = '#1a7a3a'   # Field B rotating

JUMP_THRESH = AP_RAD * 0.6

def break_jumps(x, y):
    """Insert NaN at respawn teleports."""
    dx = np.diff(x); dy = np.diff(y)
    jumps = np.where(np.sqrt(dx**2 + dy**2) > JUMP_THRESH)[0] + 1
    xb, yb = x.astype(float), y.astype(float)
    for j in reversed(jumps):
        xb = np.insert(xb, j, np.nan)
        yb = np.insert(yb, j, np.nan)
    return xb, yb

def draw_traces(ax, H, is_cued):
    """Draw all four subfield traces into ax."""
    # Define role of each subfield in this condition
    # CUED:   S0=A-rot, S1=A-rot, S2=B-coh-translator, S3=B-noncoh
    # UNCUED: S0=A-coh-translator, S1=A-noncoh, S2=B-rot, S3=B-rot
    if is_cued:
        roles = [('A-rot', C_A_rot, 0.8, 2),
                 ('A-rot', C_A_rot, 0.8, 2),
                 ('B-coh', C_B_coh, 1.4, 4),
                 ('B-nc',  C_B_nc,  0.8, 3)]
    else:
        roles = [('A-coh', C_A_coh, 1.4, 4),
                 ('A-nc',  C_A_nc,  0.8, 3),
                 ('B-rot', C_B_rot, 0.8, 2),
                 ('B-rot', C_B_rot, 0.8, 2)]

    for sf, (role, col, lw, zo) in enumerate(roles):
        for d in range(N_DOTS):
            x = H[sf][:, d, 0]
            y = H[sf][:, d, 1]
            xb, yb = break_jumps(x, y)

            # Remap ti_start/ti_end indices after NaN insertions
            jumps_before_ts = np.sum(np.diff(x[:ti_start+1])**2 +
                                     np.diff(y[:ti_start+1])**2 > JUMP_THRESH**2)
            jumps_before_te = np.sum(np.diff(x[:ti_end+1])**2 +
                                     np.diff(y[:ti_end+1])**2 > JUMP_THRESH**2)
            ts = ti_start + int(jumps_before_ts)
            te = ti_end   + int(jumps_before_te)

            kw = dict(solid_capstyle='round', zorder=zo)
            ax.plot(xb[:ts+1],  yb[:ts+1],  color=col, lw=lw, alpha=0.25, **kw)
            ax.plot(xb[ts:te+1], yb[ts:te+1], color=col, lw=lw*1.4, alpha=0.95, **kw)
            ax.plot(xb[te:],    yb[te:],    color=col, lw=lw, alpha=0.45, **kw)

            # Mark T_START on the coherent translator
            if 'coh' in role:
                ax.plot(x[ti_start], y[ti_start], 'o', color=col,
                        ms=4, zorder=6, alpha=0.9)

    # Aperture
    ax.add_patch(plt.Circle((0, 0), AP_RAD, color='#f2f2f2', zorder=0))
    ax.add_patch(plt.Circle((0, 0), AP_RAD, color='#cccccc',
                             fill=False, lw=0.8, zorder=1))

    # Translation window shading — not in x/y space, but mark tStart/tEnd on a centroid
    # Instead: draw a small arrow showing the heading
    ax.annotate('', xy=(0.55, 0), xytext=(0, 0),
                arrowprops=dict(arrowstyle='->', color='#555', lw=1.5), zorder=10)

    # Fixation cross
    ax.plot(0, 0, '+', color='#333', ms=8, mew=1.2, zorder=7)

    ax.set_aspect('equal')
    ax.set_xlim(-AP_RAD - 0.4, AP_RAD + 0.4)
    ax.set_ylim(-AP_RAD - 0.4, AP_RAD + 0.4)
    ax.set_xticks([-3, 0, 3]); ax.set_yticks([-3, 0, 3])
    ax.tick_params(labelsize=8)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

# ── Figure ────────────────────────────────────────────────────────────────────
fig, axes = plt.subplots(1, 2, figsize=(11, 5.5))
fig.patch.set_facecolor('white')

for ax, H, is_cued, label in [
        (axes[0], H_cued,   True,  'CUED\n(delayed field translates → S2)'),
        (axes[1], H_uncued, False, 'UNCUED\n(non-delayed field translates → S0)')]:
    draw_traces(ax, H, is_cued)
    ax.set_title(label, fontsize=10, fontweight='bold', pad=8)
    ax.set_xlabel('Horizontal position (°)', fontsize=9)

axes[0].set_ylabel('Vertical position (°)', fontsize=9)

fig.suptitle(
    'N condition · CUED vs UNCUED · IDENTICAL dot starting positions (same seed)\n'
    f'Frames {ONSET_F}–{SHOW_TO-1}  ·  Bold traces = translation window (frames {T_START}–{T_END})  ·  '
    f'● marks T_start on coherent translator\n'
    'Any structural difference OUTSIDE the bold region is a potential artifact',
    fontsize=8.5, y=1.01, ha='left', x=0.02)

# Shared legend
legend_elements = [
    mpatches.Patch(color=C_A_rot,  label='Field A — rotating (CW)'),
    mpatches.Patch(color=C_B_rot,  label='Field B — rotating (CCW), delayed onset'),
    mpatches.Patch(color=C_B_coh,  label='Coherent translator (bold = translation window)'),
    mpatches.Patch(color='#ee9999', label='Non-coherent (8 balanced dirs)'),
]
fig.legend(handles=legend_elements, fontsize=7.5, frameon=False,
           loc='lower center', ncol=4, bbox_to_anchor=(0.5, -0.04))

plt.tight_layout()
plt.savefig(OUT, bbox_inches='tight', facecolor='white')
plt.savefig(OUT.replace('.svg', '.png'), dpi=150, bbox_inches='tight', facecolor='white')
print(f'Saved: {OUT}')
print(f'Saved: {OUT.replace(".svg", ".png")}')
