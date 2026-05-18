"""
reconstruct_animation.py
Deterministic frame-by-frame reconstruction of VRDots stimuli.
Conditions: N, M, C, MC from SubfieldSwap_CatekExact_NMoCol_v1 (session 260515_0848)
One CUED trial per condition, RotCfg=0 (Field A=CW, Field B=CCW).

Controls:
  Slider  — scrub to any frame
  ← →     — step one frame
  Space   — play/pause
"""

import sys, os, math, time
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.widgets import Slider, Button

sys.path.insert(0, os.path.dirname(__file__))
from dotnet_random import DotNetRandom, uniform_annulus, dot_net_hash

# ── Asset parameters (from Exp_SubfieldSwap_CatekExact_NMoCol.asset) ──────────
SIM_HZ      = 90
AP_DEG      = 1.65          # aperture radius (degrees)
EXCL_DEG    = 0.5           # fixation exclusion radius
DOT_R_DEG   = 0.04          # dot display radius (half of 0.08°)
ROT_DEG_FR  = 81.0 / SIM_HZ  # 0.9°/frame
TRANS_DEG_FR = 2.26 / SIM_HZ # °/frame
DOTS_PER_SF = 43 // 2       # = 21  (Mathf.Max(1, dotsPerField/2))

# Fixation target geometry — from Fixation_Controller (outerDiam=1.8°, innerDiam=0.2°,
# crossThickness=0.375°) scaled by fixationScaleFactor=0.47 from the NMoCol asset.
FIX_OUTER_R  = 1.8 / 2 * 0.47   # white disc radius (0.423°)
FIX_CROSS_HW = 0.375 / 2 * 0.47  # cross arm half-width (0.088°)
FIX_INNER_R  = 0.2 / 2 * 0.47   # white center dot radius (0.047°)

# MotionKind enum values (from StimulusConditionsLibrary.cs)
MK_CW  = 1
MK_CCW = 2
MK_LIN = 3
MK_NC  = 4

# seed_base offsets matching StimulusBuilder.cs line 195
def seed_base(seed_a0, sf_index):
    if sf_index < 2:
        return seed_a0 + sf_index * 1000003
    else:
        return seed_a0 + 99991 + sf_index * 1000003

# ── Load trial data ────────────────────────────────────────────────────────────
DATA = '/Users/genestoner1/Projects/ObjectBasedAttention/VRDots/Agents/Data'
df = pd.read_csv(f'{DATA}/vr_dots_session_260515_0848.tsv', sep='\t')
df = df[df['RespDeg'] >= 0].reset_index(drop=True)

CONDITIONS = ['N', 'M', 'C', 'MC']
COND_LABELS = {'N': 'No Swap', 'M': 'Motion Swap', 'C': 'Color Swap', 'MC': 'Motion+Color'}
COND_COLORS = {'N': '#2ca02c', 'M': '#1f77b4', 'C': '#9467bd', 'MC': '#d62728'}

# Pick one CUED, RotCfg=0 trial per swap type
trials = {}
for swap in CONDITIONS:
    mask = (df['SwapType'] == swap) & (df['Cond'] == 'CUED') & (df['RotCfg'] == 0)
    row = df[mask].iloc[0]
    trials[swap] = row
    print(f"{swap:4s}: seed={row.SeedA0}  onset={row.OnsetFrame}  tStart={row.TransStartFrame}"
          f"  tEnd={row.TransEndFrame}  heading={row.TransDeg}°  nFrames={row.TotalFrames}"
          f"  delColor={row.DelayedFieldColor}")

# ── Motion-kind reconstruction ─────────────────────────────────────────────────
def build_motion_kinds(swap, row):
    """
    Reconstruct motionKindByFrame[subfield][frame] from trial parameters.
    Based exactly on ExpSpecTestPhase.cs BuildCondition() logic.
    Returns array shape (4, N_frames).
    """
    N  = int(row.TotalFrames)
    onset  = int(row.OnsetFrame)
    tStart = int(row.TransStartFrame)
    tEnd   = int(row.TransEndFrame)

    # RotCfg=0: aRot=CW, bRot=CCW
    rot_cfg = int(row.RotCfg)
    aRot = MK_CW  if rot_cfg == 0 else MK_CCW
    bRot = MK_CCW if rot_cfg == 0 else MK_CW

    motion_swap = swap in ('M', 'MC')

    mk = np.zeros((4, N), dtype=int)

    for f in range(N):
        after_onset = f >= onset
        after_swap  = f >= tStart

        curARot = bRot if (motion_swap and after_swap) else aRot
        curBRot = aRot if (motion_swap and after_swap) else bRot

        # delayTranslator=true: Field A always visible, Field B visible after onset
        # sub0, sub1 → Field A; sub2, sub3 → Field B
        # No dots50 swaps in NMoCol
        mk[0, f] = curARot                     # sub0: Field A
        mk[1, f] = curARot                     # sub1: Field A
        mk[2, f] = curBRot if after_onset else 0  # sub2: Field B (hidden=0)
        mk[3, f] = curBRot if after_onset else 0  # sub3: Field B (hidden=0)

    # Translation window override: CUED → sub2=Linear, sub3=NonCoherent
    for f in range(max(0, tStart), min(N, tEnd)):
        mk[2, f] = MK_LIN
        mk[3, f] = MK_NC

    return mk

# ── Color reconstruction ───────────────────────────────────────────────────────
def field_colors(swap, row, frame, tStart):
    """Returns (colorA, colorB) as matplotlib color strings."""
    color_swap = swap in ('C', 'MC')
    # DelayedFieldColor = color of Field B (delayed field)
    # 'G' → Field B=green, Field A=red
    b_is_green = (row.DelayedFieldColor == 'G')

    after_swap = frame >= tStart
    if color_swap and after_swap:
        b_is_green = not b_is_green  # swap

    colA = '#27ae60' if not b_is_green else '#c0392b'
    colB = '#27ae60' if b_is_green     else '#c0392b'
    return colA, colB

# ── Dot position reconstruction ────────────────────────────────────────────────
def init_positions(seed_a0):
    """
    Initialize dot positions for all 4 subfields.
    Returns pos[4][DOTS_PER_SF] as list of (x,y) arrays in degrees.
    Matches StimulusBuilder.BuildCondition(): shared rngA for sf0+sf1, rngB for sf2+sf3.
    """
    rng_a = DotNetRandom(seed_a0)
    rng_b = DotNetRandom(seed_a0 + 99991)

    pos = []
    for sf in range(4):
        rng = rng_a if sf < 2 else rng_b
        dots = []
        for _ in range(DOTS_PER_SF):
            x, y = uniform_annulus(rng, AP_DEG, EXCL_DEG)
            dots.append([x, y])
        pos.append(np.array(dots))  # shape (DOTS_PER_SF, 2)
    return pos

def step_rotation(pos, dir_sign):
    """Rotate all dots in pos (shape N,2) by dir_sign * ROT_DEG_FR degrees."""
    ang = math.radians(dir_sign * ROT_DEG_FR)
    ca, sa = math.cos(ang), math.sin(ang)
    x = pos[:, 0] * ca - pos[:, 1] * sa
    y = pos[:, 0] * sa + pos[:, 1] * ca
    pos[:, 0] = x
    pos[:, 1] = y

def handle_oob(pos, sf_idx, seed_a0, dot_idx, frame):
    """Respawn dot if outside aperture or inside exclusion. Returns new pos."""
    r2 = pos[0]**2 + pos[1]**2
    if r2 > AP_DEG**2 or (EXCL_DEG > 0 and r2 < EXCL_DEG**2):
        sb = seed_base(seed_a0, sf_idx)
        h  = dot_net_hash(sb, dot_idx, frame)
        rng = DotNetRandom(h)
        return list(uniform_annulus(rng, AP_DEG, EXCL_DEG))
    return list(pos)

def step_translation(pos_arr, heading_deg, sf_idx, seed_a0, frame):
    """Translate all dots; respawn OOB dots. Modifies pos_arr in-place."""
    dx = math.cos(math.radians(heading_deg)) * TRANS_DEG_FR
    dy = math.sin(math.radians(heading_deg)) * TRANS_DEG_FR
    for d in range(DOTS_PER_SF):
        pos_arr[d, 0] += dx
        pos_arr[d, 1] += dy
        pos_arr[d] = handle_oob(pos_arr[d], sf_idx, seed_a0, d, frame)

def step_noncoherent(pos_arr, sf_idx, seed_a0, frame):
    """Each dot gets a random heading from Hash; respawn OOB. Modifies in-place."""
    sb = seed_base(seed_a0, sf_idx)
    for d in range(DOTS_PER_SF):
        h  = dot_net_hash(sb, d, frame)
        rng = DotNetRandom(h)
        # StepTranslationBalanced uses UniformAnnulus to pick a random position offset
        # within a tiny disk of radius TRANS_DEG_FR — equivalent to random direction
        nx, ny = uniform_annulus(rng, TRANS_DEG_FR, 0.0)
        pos_arr[d, 0] += nx
        pos_arr[d, 1] += ny
        pos_arr[d] = handle_oob(pos_arr[d], sf_idx, seed_a0, d, frame)

def replot_subfield(pos_arr, sf_idx, seed_a0, frame):
    """ReplotSubfield: randomize all dot positions in a subfield at tStart."""
    sb = seed_base(seed_a0, sf_idx)
    for d in range(DOTS_PER_SF):
        h  = dot_net_hash(sb, d, frame + 7919983)
        rng = DotNetRandom(h)
        x, y = uniform_annulus(rng, AP_DEG, EXCL_DEG)
        pos_arr[d] = [x, y]

def simulate_trial(swap, row):
    """
    Full frame-by-frame simulation. Returns:
      positions[frame][sf] = np.array shape (DOTS_PER_SF, 2)
      mk[sf][frame] = motion kind int
    """
    seed_a0  = int(row.SeedA0)
    N        = int(row.TotalFrames)
    tStart   = int(row.TransStartFrame)
    tEnd     = int(row.TransEndFrame)
    heading  = float(row.TransDeg)

    mk = build_motion_kinds(swap, row)

    # initial positions
    pos = init_positions(seed_a0)  # list of 4 arrays shape (DOTS_PER_SF, 2)

    all_frames = []

    for f in range(N):
        # replotTranslatingAtTStart = false in this asset — no replot
        # Step each subfield
        for sf in range(4):
            kind = mk[sf, f]
            if kind == MK_CW:
                step_rotation(pos[sf], -1)
            elif kind == MK_CCW:
                step_rotation(pos[sf], +1)
            elif kind == MK_LIN:
                step_translation(pos[sf], heading, sf, seed_a0, f)
            elif kind == MK_NC:
                step_noncoherent(pos[sf], sf, seed_a0, f)
            # kind == 0 → hidden, don't move

        # Snapshot
        all_frames.append([p.copy() for p in pos])

    return all_frames, mk

# ── Run all simulations ────────────────────────────────────────────────────────
print("\nSimulating trials...")
sims = {}
trial_mk = {}
for swap in CONDITIONS:
    row = trials[swap]
    frames, mk = simulate_trial(swap, row)
    sims[swap]    = frames
    trial_mk[swap] = mk
    print(f"  {swap}: {len(frames)} frames done")

N_FRAMES = min(len(sims[s]) for s in CONDITIONS)

# ── Interactive figure ─────────────────────────────────────────────────────────
fig, axes = plt.subplots(1, 4, figsize=(18, 6))
fig.patch.set_facecolor('#111')
plt.subplots_adjust(bottom=0.22, top=0.88, wspace=0.05, left=0.03, right=0.97)

DOT_SIZE_PT = (DOT_R_DEG / AP_DEG * 120)**2   # scaled for scatter

dot_collections = {}
phase_texts     = {}

for ax, swap in zip(axes, CONDITIONS):
    ax.set_facecolor('#111')
    ax.set_aspect('equal')
    ax.set_xlim(-AP_DEG * 1.15, AP_DEG * 1.15)
    ax.set_ylim(-AP_DEG * 1.15, AP_DEG * 1.15)
    ax.set_xticks([]); ax.set_yticks([])

    # Aperture circle
    circ = plt.Circle((0, 0), AP_DEG, color='#444', fill=False, lw=1.2)
    ax.add_patch(circ)
    # Fixation target: white disc + black crosshairs + white center dot
    fix_disc = plt.Circle((0, 0), FIX_OUTER_R, color='white', zorder=9)
    ax.add_patch(fix_disc)
    cross_h = mpatches.Rectangle(
        (-FIX_OUTER_R, -FIX_CROSS_HW), 2 * FIX_OUTER_R, 2 * FIX_CROSS_HW,
        color='black', zorder=10)
    ax.add_patch(cross_h)
    cross_h.set_clip_path(fix_disc)
    cross_v = mpatches.Rectangle(
        (-FIX_CROSS_HW, -FIX_OUTER_R), 2 * FIX_CROSS_HW, 2 * FIX_OUTER_R,
        color='black', zorder=10)
    ax.add_patch(cross_v)
    cross_v.set_clip_path(fix_disc)
    fix_dot = plt.Circle((0, 0), FIX_INNER_R, color='white', zorder=11)
    ax.add_patch(fix_dot)

    # Dot scatter for each subfield
    scs = []
    for sf in range(4):
        sc = ax.scatter([], [], s=DOT_SIZE_PT, marker='o', linewidths=0, zorder=5)
        scs.append(sc)
    dot_collections[swap] = scs

    # Title and phase text
    ax.set_title(COND_LABELS[swap], color=COND_COLORS[swap],
                 fontsize=11, fontweight='bold', pad=4)
    pt = ax.text(0, -AP_DEG * 1.08, '', ha='center', va='top',
                 color='#aaa', fontsize=7.5)
    phase_texts[swap] = pt

# Frame counter and heading info
frame_text = fig.text(0.5, 0.92, '', ha='center', va='bottom',
                      color='white', fontsize=11, fontweight='bold')

def phase_label(swap, frame):
    row    = trials[swap]
    onset  = int(row.OnsetFrame)
    tStart = int(row.TransStartFrame)
    tEnd   = int(row.TransEndFrame)
    t_ms   = frame / SIM_HZ * 1000
    if frame < onset:
        return f'Field A solo  ({t_ms:.0f} ms)'
    elif frame < tStart:
        return f'Both rotating  ({t_ms:.0f} ms)'
    elif frame < tEnd:
        return f'TRANSLATION  ({t_ms:.0f} ms)'
    else:
        return f'Post-trans  ({t_ms:.0f} ms)'

def update(frame):
    frame = int(frame)
    for swap in CONDITIONS:
        if frame >= len(sims[swap]):
            continue
        pos_snap = sims[swap][frame]
        row      = trials[swap]
        tStart   = int(row.TransStartFrame)
        scs      = dot_collections[swap]

        colA, colB = field_colors(swap, row, frame, tStart)
        mk_snap  = trial_mk[swap][:, frame]

        for sf in range(4):
            p = pos_snap[sf]
            kind = mk_snap[sf]
            if kind == 0:          # hidden
                scs[sf].set_offsets(np.empty((0, 2)))
            else:
                scs[sf].set_offsets(p)
                col = colA if sf < 2 else colB
                scs[sf].set_facecolor(col)
                # Dim noise subfields slightly
                alpha = 0.9 if sf in (0, 2) else 0.5
                scs[sf].set_alpha(alpha)

        phase_texts[swap].set_text(phase_label(swap, frame))

    row0 = trials['N']
    t_ms = frame / SIM_HZ * 1000
    frame_text.set_text(
        f'Frame {frame} / {N_FRAMES-1}   ({t_ms:.1f} ms)   '
        f'onset={row0.OnsetFrame}   tStart={row0.TransStartFrame}   tEnd={row0.TransEndFrame}'
    )
    fig.canvas.draw_idle()

# Slider
ax_slider = fig.add_axes([0.12, 0.10, 0.76, 0.03])
ax_slider.set_facecolor('#222')
slider = Slider(ax_slider, 'Frame', 0, N_FRAMES - 1, valinit=0, valstep=1,
                color='#555', initcolor='none')
slider.label.set_color('white')
slider.valtext.set_color('white')
slider.on_changed(update)

# Play/pause button
ax_play = fig.add_axes([0.46, 0.02, 0.08, 0.05])
btn_play = Button(ax_play, '▶ Play', color='#333', hovercolor='#555')
btn_play.label.set_color('white')

playing = [False]
def toggle_play(event):
    playing[0] = not playing[0]
    btn_play.label.set_text('⏸ Pause' if playing[0] else '▶ Play')
btn_play.on_clicked(toggle_play)

# Keyboard stepping
def on_key(event):
    if event.key == ' ':
        toggle_play(None)
    elif event.key == 'right':
        slider.set_val(min(slider.val + 1, N_FRAMES - 1))
    elif event.key == 'left':
        slider.set_val(max(slider.val - 1, 0))
fig.canvas.mpl_connect('key_press_event', on_key)

# Playback timer
last_time = [time.time()]
FPS = 15  # playback speed (frames per second; real stim is 90 Hz)

def on_timer():
    if playing[0]:
        now = time.time()
        if now - last_time[0] > 1.0 / FPS:
            new_val = slider.val + 1
            if new_val >= N_FRAMES:
                new_val = 0
            slider.set_val(new_val)
            last_time[0] = now

timer = fig.canvas.new_timer(interval=int(1000 / FPS))
timer.add_callback(on_timer)
timer.start()

# Legend
from matplotlib.lines import Line2D
legend_elems = [
    Line2D([0],[0], marker='o', color='w', markerfacecolor='#c0392b', ms=7, label='Field A (non-delayed)', lw=0),
    Line2D([0],[0], marker='o', color='w', markerfacecolor='#27ae60', ms=7, label='Field B (delayed, translates)', lw=0),
    Line2D([0],[0], marker='o', color='w', markerfacecolor='#c0392b', ms=4, alpha=0.5, label='noise subfield', lw=0),
]
fig.legend(handles=legend_elems, loc='lower right', bbox_to_anchor=(0.99, 0.14),
           fontsize=8, facecolor='#222', edgecolor='#555', labelcolor='white')

fig.suptitle(
    'VRDots stimulus reconstruction — SubfieldSwap_CatekExact_NMoCol_v1  '
    '·  CUED · session 260515_0848\n'
    'Ap=1.65°  ·  43 dots/field  ·  80 ms  ·  90 Hz  '
    '·  Space=play/pause  ·  ←→=step',
    color='white', fontsize=9, y=0.99)

update(0)
print("\nOpening interactive animation. Use slider or arrow keys to step through frames.")
plt.show()
