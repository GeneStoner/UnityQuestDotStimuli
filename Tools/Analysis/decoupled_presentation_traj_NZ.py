"""
decoupled_presentation_traj_NZ.py
----------------------------------
Simplified presentation figure: N and Z swap conditions only × 2 (CUED / UNCUED) = 4 panels.
Tests the role of depth by comparing no-swap (N) vs depth-swap (Z).

Pairing principle (matches Stoner & Blanc convention):
  Each CUED/UNCUED pair has IDENTICAL post-onset tracks — same translator
  color/direction/depth, same rotator color/direction/depth.
  The only visible difference is which field's line is ABSENT before onset.

Fixed pair:
  Translator field:  Red  / CCW / → (Near pre-swap, depth-swaps to Far in Z)
  Rotator field:     Green / CW  / → (Far  pre-swap, depth-swaps to Near in Z)

  CUED:   translator = delayed field (gap before onset in Red line)
  UNCUED: translator = always-on field (gap before onset in Green line)

Cueing labels (Dot / Depth / Color):
  N  CUED:   ✓ ✓ ✓   UNCUED: ✗ ✗ ✗
  Z  CUED:   ✓ ✗ ✓   UNCUED: ✗ ✓ ✗

Output: Agents/SwapPilot/Figures/decoupled_presentation_traj_NZ.pdf / .png
"""

import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
matplotlib.rcParams['pdf.fonttype'] = 42
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.patches as mpatches
from matplotlib.backends.backend_pdf import PdfPages

OUT_BASE = os.path.normpath(os.path.join(
    os.path.dirname(__file__),
    '../../Agents/SwapPilot/Figures/decoupled_presentation_traj_NZ'))
os.makedirs(os.path.dirname(OUT_BASE), exist_ok=True)

# ── Timing ────────────────────────────────────────────────────────────────────
ONSET   = 56
T_START = 78
T_END   = 84
TOTAL   = 114
SIM_HZ  = 75.0
t = np.arange(TOTAL) / SIM_HZ

Y_CW, Y_TRANS, Y_CCW = 2, 1, 0

COL_RED   = '#CC3333'
COL_GREEN = '#228B22'
LS_RED    = '-'
LS_GREEN  = ':'
LW        = 2.0

C_CUED   = '#1a3a8b'
C_UNCUED = '#884400'

SWAP_COLORS = {'N': '#444444', 'Z': '#116688'}
ROW_LABELS  = {
    'N': 'N\n(no swap)',
    'Z': 'Z\n(depth swap\nat tStart)',
}

# ── Fixed field identities ─────────────────────────────────────────────────────
T_COL, T_LS, T_DIR, T_DEP = COL_RED,   LS_RED,   Y_CCW, 1.0   # Near=1
R_COL, R_LS, R_DIR, R_DEP = COL_GREEN, LS_GREEN, Y_CW,  0.0   # Far=0


def seg(val, start, stop):
    arr = np.full(TOTAL, np.nan)
    if start < stop:
        arr[start:stop] = val
    return arr


def make_tracks(swap, cued):
    color_swap = swap in ('C', 'CZ')
    depth_swap = swap in ('Z', 'CZ')

    t_col2 = R_COL if color_swap else T_COL
    t_ls2  = R_LS  if color_swap else T_LS
    t_dep2 = R_DEP if depth_swap else T_DEP

    r_col2 = T_COL if color_swap else R_COL
    r_ls2  = T_LS  if color_swap else R_LS
    r_dep2 = T_DEP if depth_swap else R_DEP

    if cued:
        del_col,  del_ls,  del_dir,  del_dep  = T_COL, T_LS, T_DIR, T_DEP
        del_col2, del_ls2, del_dep2            = t_col2, t_ls2, t_dep2
        on_col,   on_ls,   on_dir,   on_dep   = R_COL, R_LS, R_DIR, R_DEP
        on_col2,  on_ls2,  on_dep2             = r_col2, r_ls2, r_dep2
    else:
        del_col,  del_ls,  del_dir,  del_dep  = R_COL, R_LS, R_DIR, R_DEP
        del_col2, del_ls2, del_dep2            = r_col2, r_ls2, r_dep2
        on_col,   on_ls,   on_dir,   on_dep   = T_COL, T_LS, T_DIR, T_DEP
        on_col2,  on_ls2,  on_dep2             = t_col2, t_ls2, t_dep2

    def seg3(pre_val, pre_start, trans_val, post_val):
        """Three disconnected segments: pre-rotation | translation | post-rotation.
        NaN gaps at T_START and T_END prevent any diagonal linking lines."""
        pre  = np.full(TOTAL, np.nan); pre[pre_start:T_START]  = pre_val
        trans = np.full(TOTAL, np.nan); trans[T_START:T_END]   = trans_val
        post = np.full(TOTAL, np.nan); post[T_END:TOTAL]       = post_val
        return pre, trans, post

    # Always-on field motion: rotates pre, translates if UNCUED, rotates post
    on_trans_val = Y_TRANS if not cued else on_dir
    on_m_pre, on_m_tr, on_m_post = seg3(on_dir, 0, on_trans_val, on_dir)

    # Delayed field motion: absent until ONSET, translates if CUED, rotates post
    del_trans_val = Y_TRANS if cued else del_dir
    del_m_pre, del_m_tr, del_m_post = seg3(del_dir, ONSET, del_trans_val, del_dir)

    on_dep_arr = np.full(TOTAL, np.nan)
    on_dep_arr[:T_START] = on_dep
    on_dep_arr[T_START:] = on_dep2

    del_dep_arr = np.full(TOTAL, np.nan)
    del_dep_arr[ONSET:T_START] = del_dep
    del_dep_arr[T_START:]      = del_dep2

    return dict(
        # Always-on field — 3 motion segments + pre/post depth
        on_m_pre=on_m_pre, on_m_tr=on_m_tr, on_m_post=on_m_post,
        on_col_pre=on_col, on_ls_pre=on_ls,
        on_col_post=on_col2, on_ls_post=on_ls2,
        on_dep_pre  = np.where(np.arange(TOTAL) < T_START, on_dep_arr, np.nan),
        on_dep_post = np.where(np.arange(TOTAL) >= T_START, on_dep_arr, np.nan),
        # Delayed field — 3 motion segments + pre/post depth
        del_m_pre=del_m_pre, del_m_tr=del_m_tr, del_m_post=del_m_post,
        del_col_pre=del_col, del_ls_pre=del_ls,
        del_col_post=del_col2, del_ls_post=del_ls2,
        del_dep_pre  = np.where((np.arange(TOTAL) >= ONSET) & (np.arange(TOTAL) < T_START), del_dep_arr, np.nan),
        del_dep_post = np.where(np.arange(TOTAL) >= T_START, del_dep_arr, np.nan),
        delayed_str = f"{'Red' if del_col==COL_RED else 'Grn'}/{'CCW' if del_dir==Y_CCW else 'CW'}/{'Near' if del_dep==1.0 else 'Far'}",
        trans_str   = f"{'Red' if t_col2==COL_RED else 'Grn'}/CCW/{'Near' if t_dep2==1.0 else 'Far'}",
    )


def cueing_labels(swap, cued):
    color_swap = swap in ('C', 'CZ')
    depth_swap = swap in ('Z', 'CZ')
    dot_s  = '✓' if cued else '✗'
    dep_s  = '✓' if (cued == (not depth_swap)) else '✗'
    col_s  = '✓' if (cued == (not color_swap)) else '✗'
    return f'Dot{dot_s}   Depth{dep_s}   Color{col_s}'


def draw_cell(ax_m, ax_d, swap, cued,
              show_xlabel=False, show_row_label=False, show_col_title=False):
    tr = make_tracks(swap, cued)
    cc = C_CUED if cued else C_UNCUED
    t_s = T_START / SIM_HZ
    t_e = T_END   / SIM_HZ

    for ax in (ax_m, ax_d):
        ax.axvspan(t_s, t_e, color='#e8e8e8', alpha=1.0, zorder=0)
        ax.set_xlim(0, TOTAL / SIM_HZ)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)

    # Pre-rotation and post-rotation segments (no diagonal links to translation)
    ax_m.plot(t, tr['on_m_pre'],    color=tr['on_col_pre'],  ls=tr['on_ls_pre'],  lw=LW)
    ax_m.plot(t, tr['on_m_post'],   color=tr['on_col_post'], ls=tr['on_ls_post'], lw=LW)
    ax_m.plot(t, tr['del_m_pre'],   color=tr['del_col_pre'], ls=tr['del_ls_pre'], lw=LW)
    ax_m.plot(t, tr['del_m_post'],  color=tr['del_col_post'],ls=tr['del_ls_post'],lw=LW)
    # Translation segments (drawn separately — no link to rotation level)
    ax_m.plot(t, tr['on_m_tr'],     color=tr['on_col_post'], ls=tr['on_ls_post'], lw=LW)
    ax_m.plot(t, tr['del_m_tr'],    color=tr['del_col_post'],ls=tr['del_ls_post'],lw=LW)

    ax_m.set_yticks([Y_CCW, Y_TRANS, Y_CW])
    ax_m.set_yticklabels(['CCW', 'TRANS', 'CW'], fontsize=7)
    ax_m.set_ylim(-0.6, 2.8)
    ax_m.tick_params(labelbottom=False, bottom=False, labelsize=7)

    ax_d.plot(t, tr['on_dep_pre'],   color=tr['on_col_pre'],  ls=tr['on_ls_pre'],  lw=LW)
    ax_d.plot(t, tr['on_dep_post'],  color=tr['on_col_post'], ls=tr['on_ls_post'], lw=LW)
    ax_d.plot(t, tr['del_dep_pre'],  color=tr['del_col_pre'], ls=tr['del_ls_pre'], lw=LW)
    ax_d.plot(t, tr['del_dep_post'], color=tr['del_col_post'],ls=tr['del_ls_post'],lw=LW)

    ax_d.set_yticks([0.0, 1.0])
    ax_d.set_yticklabels(['Far', 'Near'], fontsize=7)
    ax_d.set_ylim(-0.35, 1.35)

    if show_xlabel:
        ax_d.set_xlabel('Time (s)', fontsize=8)
        ax_d.tick_params(axis='x', labelsize=7)
    else:
        ax_d.tick_params(labelbottom=False, bottom=False)

    ax_d.text(0.02, 1.18, f'* {tr["delayed_str"]}',
              ha='left', va='bottom', fontsize=6.5, color='#111',
              transform=ax_d.transAxes, clip_on=False,
              bbox=dict(boxstyle='round,pad=0.25', facecolor='#fffde7',
                        edgecolor='#997700', lw=0.7))

    ax_d.text(0.98, 1.18, f'▶ {tr["trans_str"]}',
              ha='right', va='bottom', fontsize=6.5, color='#111',
              transform=ax_d.transAxes, clip_on=False,
              bbox=dict(boxstyle='round,pad=0.25', facecolor='#f8f8f8',
                        edgecolor='#888', lw=0.7))

    title_str = cueing_labels(swap, cued)
    ax_m.set_title(title_str, fontsize=11, fontweight='bold', pad=6, color=cc,
                   bbox=dict(boxstyle='round,pad=0.35',
                             facecolor='#f0f4ff' if cued else '#fff4e8',
                             edgecolor=cc, lw=0.9))

    if show_row_label:
        sc = SWAP_COLORS[swap]
        ax_m.set_ylabel(ROW_LABELS[swap] + '\n\nMotion',
                        fontsize=9, fontweight='bold', color=sc, labelpad=5)
        ax_d.set_ylabel('Depth', fontsize=8, labelpad=5)
    else:
        ax_m.set_ylabel('Motion', fontsize=8, labelpad=4)
        ax_d.set_ylabel('Depth', fontsize=8, labelpad=4)


# ── Build figure ──────────────────────────────────────────────────────────────

SWAPS = ['N', 'Z']

fig = plt.figure(figsize=(9, 8))
fig.patch.set_facecolor('white')
fig.suptitle(
    'DecoupledDots — N (no swap) vs Z (depth swap): role of depth\n'
    'CUED / UNCUED pairs matched: post-onset tracks identical; only the pre-onset gap differs\n'
    'Red solid = translator field (Red/CCW)  ·  Green dotted = rotator field (Green/CW)',
    fontsize=9, y=1.02, va='bottom')

outer = gridspec.GridSpec(
    2, 2, hspace=0.85, wspace=0.28,
    top=0.90, bottom=0.10, left=0.15, right=0.97)

for ri, swap in enumerate(SWAPS):
    for ci, cued in enumerate([True, False]):
        inner = gridspec.GridSpecFromSubplotSpec(
            2, 1, subplot_spec=outer[ri, ci],
            height_ratios=[3, 1.5], hspace=0.10)
        ax_m = fig.add_subplot(inner[0])
        ax_d = fig.add_subplot(inner[1], sharex=ax_m)
        draw_cell(ax_m, ax_d, swap, cued,
                  show_xlabel=(ri == len(SWAPS) - 1),
                  show_row_label=(ci == 0),
                  show_col_title=(ri == 0))

# ── Column headers ────────────────────────────────────────────────────────────
fig.text(0.33, 0.935, 'CUED', ha='center', fontsize=13, fontweight='bold',
         color=C_CUED)
fig.text(0.75, 0.935, 'UNCUED', ha='center', fontsize=13, fontweight='bold',
         color=C_UNCUED)

# ── Legend ────────────────────────────────────────────────────────────────────
legend_handles = [
    mpatches.Patch(color=COL_RED,   label='Translator field (Red/CCW) — delayed in CUED'),
    mpatches.Patch(color=COL_GREEN, label='Rotator field (Green/CW) — delayed in UNCUED'),
    mpatches.Patch(facecolor='#fffde7', edgecolor='#997700', lw=0.8,
                   label='* = delayed field at onset'),
    mpatches.Patch(facecolor='#f8f8f8', edgecolor='#888', lw=0.8,
                   label='▶ = translating field (identical across pair)'),
    mpatches.Patch(facecolor='gray', alpha=0.35, label='Translation window'),
]
fig.legend(handles=legend_handles, loc='lower center', ncol=3, fontsize=8,
           frameon=True, framealpha=0.95, edgecolor='#CCC',
           bbox_to_anchor=(0.5, -0.04))

plt.savefig(OUT_BASE + '.png', dpi=150, bbox_inches='tight', facecolor='white')
plt.savefig(OUT_BASE + '.svg', bbox_inches='tight', facecolor='white')
with PdfPages(OUT_BASE + '.pdf') as pdf:
    pdf.savefig(fig, bbox_inches='tight', facecolor='white')

print(f'Saved: {OUT_BASE}.png')
print(f'Saved: {OUT_BASE}.svg')
print(f'Saved: {OUT_BASE}.pdf')
