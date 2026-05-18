"""
4 Dot Traces — Motion Swap CUED condition
Based solely on ExpSpecTestPhase.cs logic

Parameters (from Exp_SubfieldSwap_CatekExact_NMoCol.asset):
  simHz = 90
  apertureRadius_deg = 1.65
  dotSize_deg = 0.08  → radius = 0.04°
  rotationSpeed_degPerSec = 81  → 81/90 = 0.9°/frame
  translationSpeed_degPerSec = 2.26  → 2.26/90 ≈ 0.02511°/frame
  translationDuration_ms = 80  → 80*90/1000 = 7.2 → 7 frames
  delayedOnset_ms = 750  → 750*90/1000 = 67.5 → 68 frames
  preTranslation_ms = 300  → 300*90/1000 = 27 frames

Frame events:
  Frame 0:   Field A (sub0, sub1) appears and begins rotating CW
  Frame 68:  Field B (sub2, sub3) appears and begins rotating CCW
  Frame 95:  tStart — Motion swap fires:
               Field A: curARot flips from CW → CCW
               Field B sub2: enters Linear (translates rightward)
               Field B sub3: enters NonCoherent (scattered)
  Frame 102: tEnd — translation ends:
               Field B sub2: curBRot is now CW (aRot after swap)
               Field B sub3: resumes rotation at CW

Dots modeled:
  A-coh  (sub0): red,   initial (r=0.9°, θ=70°)
  A-noise (sub1): red,   initial (r=0.5°, θ=220°)
  B-coh  (sub2): green, initial (r=0.9°, θ=250°)
  B-noise (sub3): green, initial (r=0.5°, θ=40°)

CW  = clockwise  = θ decreases each frame (standard math: right-hand rule)
CCW = counter-CW = θ increases each frame

Translation direction chosen: rightward (0° = +x axis)
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.collections import PatchCollection
import matplotlib.cm as cm

# ── Parameters ────────────────────────────────────────────────────────────────
SIM_HZ      = 90
AP_DEG      = 1.65
DOT_RADIUS  = 0.04          # half of dotSize_deg=0.08
ROT_SPEED   = 81 / SIM_HZ  # 0.9 °/frame
TRANS_SPEED = 2.26 / SIM_HZ  # 0.02511 °/frame, rightward (+x)
ONSET_FR    = round(750 * SIM_HZ / 1000)   # 68
PRE_FR      = round(300 * SIM_HZ / 1000)   # 27
T_START     = ONSET_FR + PRE_FR            # 95
TRANS_FR    = int(80 * SIM_HZ / 1000)      # 7
T_END       = T_START + TRANS_FR           # 102
POST_FR     = 54                           # ~0.6 s after translation ends
N_FRAMES    = T_END + POST_FR              # 156

print(f"ONSET_FR={ONSET_FR}, PRE_FR={PRE_FR}, T_START={T_START}, TRANS_FR={TRANS_FR}, T_END={T_END}, N_FRAMES={N_FRAMES}")

# ── Initial dot positions (r, theta_deg) ─────────────────────────────────────
# All within aperture
dots = {
    'A-coh':   dict(r=0.90, theta=70.0,  color='#c0392b', label='A coherent (sub0)'),
    'A-noise': dict(r=0.50, theta=220.0, color='#e74c3c', label='A noise (sub1)',  ls='--'),
    'B-coh':   dict(r=0.90, theta=250.0, color='#27ae60', label='B coherent (sub2)'),
    'B-noise': dict(r=0.50, theta=40.0,  color='#2ecc71', label='B noise (sub3)',  ls='--'),
}

# ── Simulate positions ────────────────────────────────────────────────────────
def simulate(r0, theta0, field, key):
    xs = np.full(N_FRAMES, np.nan)
    ys = np.full(N_FRAMES, np.nan)
    theta = theta0
    tx = 0.0   # cumulative translation in x

    # Field A (sub0, sub1) visible from frame 0
    # Field B (sub2, sub3) visible from ONSET_FR
    first_frame = 0 if field == 'A' else ONSET_FR

    # Rotation assignments (from code):
    # aRot = CW, bRot = CCW (assigned deterministically; Field A=CW, Field B=CCW initially)
    # After motion swap at T_START: curARot = bRot = CCW; curBRot = aRot = CW
    # Translation window [T_START, T_END): sub2 → Linear, sub3 → NonCoherent

    for fr in range(N_FRAMES):
        if fr < first_frame:
            continue  # dot not visible yet

        if field == 'A':
            # Before swap: CW (-0.9°/frame)
            # After swap:  CCW (+0.9°/frame)
            if fr < T_START:
                theta -= ROT_SPEED
            else:
                theta += ROT_SPEED
            x = r0 * np.cos(np.deg2rad(theta))
            y = r0 * np.sin(np.deg2rad(theta))

        else:  # field == 'B'
            if key == 'B-coh':
                # Before swap: CCW (+0.9°/frame)
                # Translation window [T_START, T_END): Linear motion only (no rotation)
                # After tEnd: CW (-0.9°/frame)  [curBRot = aRot = CW after swap]
                if fr < T_START:
                    theta += ROT_SPEED
                elif fr < T_END:
                    # Linear translation rightward; angular position frozen during translation
                    tx += TRANS_SPEED
                else:
                    theta -= ROT_SPEED  # CW after swap
                x = r0 * np.cos(np.deg2rad(theta)) + tx
                y = r0 * np.sin(np.deg2rad(theta))

            else:  # B-noise (sub3)
                # Before swap: CCW (+0.9°/frame)
                # Translation window: NonCoherent — scattered; we show position frozen (realistic avg)
                # After tEnd: CW (-0.9°/frame)
                if fr < T_START:
                    theta += ROT_SPEED
                elif fr < T_END:
                    pass  # NonCoherent — dot direction random; show as stationary for trace clarity
                else:
                    theta -= ROT_SPEED
                x = r0 * np.cos(np.deg2rad(theta))
                y = r0 * np.sin(np.deg2rad(theta))

        xs[fr] = x
        ys[fr] = y

    return xs, ys

traces = {}
for key, d in dots.items():
    field = 'A' if key.startswith('A') else 'B'
    xs, ys = simulate(d['r'], d['theta'], field, key)
    traces[key] = (xs, ys)

# ── Figure ────────────────────────────────────────────────────────────────────
fig, axes = plt.subplots(1, 2, figsize=(13, 7), facecolor='#1a1a1a')
fig.subplots_adjust(wspace=0.35)

# time axis in ms
frames = np.arange(N_FRAMES)
times_ms = frames / SIM_HZ * 1000

# ─── Left panel: X-Y trajectory (spatial view) ───────────────────────────────
ax = axes[0]
ax.set_facecolor('#1a1a1a')
ax.set_aspect('equal')

# Aperture circle
aper = plt.Circle((0, 0), AP_DEG, color='#444', fill=False, lw=1.5, ls='-')
ax.add_patch(aper)

for key, d in dots.items():
    xs, ys = traces[key]
    color = d['color']
    ls    = d.get('ls', '-')
    field = 'A' if key.startswith('A') else 'B'
    # Portion indices
    f0 = 0 if field == 'A' else ONSET_FR

    # Draw path with time-gradient alpha
    valid = ~np.isnan(xs)
    vframes = frames[valid]
    vx = xs[valid]
    vy = ys[valid]

    # Segment: pre-tStart / translation window / post-tEnd
    for i in range(len(vframes)-1):
        fr = vframes[i]
        alpha = 0.3 + 0.7 * (i / max(len(vframes)-1, 1))
        segment_ls = ls
        lw = 1.8
        ax.plot([vx[i], vx[i+1]], [vy[i], vy[i+1]],
                color=color, alpha=alpha, lw=lw, ls=segment_ls, solid_capstyle='round')

    # Mark start position
    ax.plot(vx[0], vy[0], 'o', color=color, ms=5, alpha=0.9, zorder=5)
    # Dot circle at key time points
    for t_mark, label_str in [(T_START, 'swap'), (T_END, 'end trans')]:
        idx = np.where(vframes == t_mark)[0]
        if len(idx):
            i = idx[0]
            circ = plt.Circle((vx[i], vy[i]), DOT_RADIUS, color=color, alpha=0.7, zorder=6)
            ax.add_patch(circ)

# Mark events with vertical-ish annotations
for fr_ev, label_ev in [(ONSET_FR, f'Field B\nonset\n(fr {ONSET_FR})'),
                         (T_START,  f'tStart\nswap\n(fr {T_START})'),
                         (T_END,    f'tEnd\n(fr {T_END})')]:
    ax.axvline(x=np.nan)  # no-op; annotations handled in right panel

ax.set_xlim(-2.0, 2.5)
ax.set_ylim(-2.0, 2.0)
ax.set_xlabel('Horizontal position (°)', color='#ccc', fontsize=10)
ax.set_ylabel('Vertical position (°)', color='#ccc', fontsize=10)
ax.tick_params(colors='#ccc')
for spine in ax.spines.values():
    spine.set_edgecolor('#555')
ax.set_title('XY Trajectory\n(darker = later time)', color='white', fontsize=11, fontweight='bold')

# Legend
from matplotlib.lines import Line2D
legend_elements = [
    Line2D([0],[0], color=dots['A-coh']['color'],   lw=2, label='A coherent (sub0) — CW→CCW'),
    Line2D([0],[0], color=dots['A-noise']['color'],  lw=2, ls='--', label='A noise (sub1) — CW→CCW'),
    Line2D([0],[0], color=dots['B-coh']['color'],   lw=2, label='B coherent (sub2) — CCW→translate→CW'),
    Line2D([0],[0], color=dots['B-noise']['color'],  lw=2, ls='--', label='B noise (sub3) — CCW→stationary→CW'),
]
ax.legend(handles=legend_elements, loc='upper left', fontsize=7.5,
          facecolor='#2a2a2a', edgecolor='#555', labelcolor='#ccc')

# ─── Right panel: Time traces (x and y vs time) ──────────────────────────────
ax2 = axes[1]
ax2.set_facecolor('#1a1a1a')

for key, d in dots.items():
    xs, ys = traces[key]
    color = d['color']
    ls    = d.get('ls', '-')
    ax2.plot(times_ms, xs, color=color, lw=1.8, ls=ls, alpha=0.9,
             label=d['label'])
    ax2.plot(times_ms, ys, color=color, lw=1.0, ls=':', alpha=0.5)

# Event lines
ev_times = {
    ONSET_FR / SIM_HZ * 1000: ('Field B onset\n(750 ms)', '#aaa'),
    T_START  / SIM_HZ * 1000: ('tStart swap\n(1050 ms)', '#f39c12'),
    T_END    / SIM_HZ * 1000: ('tEnd\n(1128 ms)', '#e67e22'),
}
ymin, ymax = -2.0, 2.0
for t_ms, (lbl, col) in ev_times.items():
    ax2.axvline(t_ms, color=col, lw=1.2, ls='--', alpha=0.8)
    ax2.text(t_ms+5, ymax-0.15, lbl, color=col, fontsize=7.5, va='top')

ax2.axhline(0, color='#555', lw=0.8)
ax2.set_xlim(0, N_FRAMES / SIM_HZ * 1000)
ax2.set_ylim(ymin, ymax)
ax2.set_xlabel('Time (ms)', color='#ccc', fontsize=10)
ax2.set_ylabel('Position (°)', color='#ccc', fontsize=10)
ax2.tick_params(colors='#ccc')
for spine in ax2.spines.values():
    spine.set_edgecolor('#555')
ax2.set_title('Position vs Time\n(solid=X, dotted=Y)', color='white', fontsize=11, fontweight='bold')

leg2 = ax2.legend(loc='lower left', fontsize=7.5,
                   facecolor='#2a2a2a', edgecolor='#555', labelcolor='#ccc')

# ─── Super title ──────────────────────────────────────────────────────────────
fig.suptitle(
    'Dot Traces — Motion Swap, CUED condition  ·  SubfieldSwap_CatekExact_NMoCol_v1\n'
    'Ap=1.65°  ·  dot=0.08°  ·  rot=81°/s  ·  trans=2.26°/s  ·  80 ms  ·  90 Hz\n'
    'Red = Field A (CW→CCW at tStart)    Green = Field B (CCW→translate→CW)',
    color='white', fontsize=10, fontweight='bold', y=1.02
)

OUT = '/Users/genestoner1/Projects/ObjectBasedAttention/VRDots/Agents/SwapPilot/Figures/dot_traces_motion_swap.png'
plt.savefig(OUT, dpi=160, bbox_inches='tight', facecolor='#1a1a1a')
print(f'Saved: {OUT}')

# ── Print event summary ───────────────────────────────────────────────────────
print(f'\n=== Frame events ===')
print(f'  Frame   0 : Field A appears. Rotation = CW (−{ROT_SPEED:.2f}°/frame)')
print(f'  Frame  {ONSET_FR} : Field B appears. Rotation = CCW (+{ROT_SPEED:.2f}°/frame)')
print(f'  Frame  {T_START} : tStart — MOTION SWAP fires:')
print(f'            Field A curARot: CW → CCW (+{ROT_SPEED:.2f}°/frame)')
print(f'            Field B sub2: enters Linear (tx +{TRANS_SPEED:.5f}°/frame, rightward)')
print(f'            Field B sub3: enters NonCoherent (random direction each frame)')
print(f'  Frame {T_END} : tEnd — translation ends:')
print(f'            Field B sub2: resumes curBRot = CW (−{ROT_SPEED:.2f}°/frame)')
print(f'            Field B sub3: resumes curBRot = CW (−{ROT_SPEED:.2f}°/frame)')
print(f'  Total translation displacement: {TRANS_FR * TRANS_SPEED:.4f}° = {TRANS_FR}fr × {TRANS_SPEED:.5f}°/fr')
