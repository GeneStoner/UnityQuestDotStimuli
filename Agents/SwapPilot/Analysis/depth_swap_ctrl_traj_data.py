#!/usr/bin/env python3
"""
depth_swap_ctrl_traj_data.py
----------------------------
Combined figure: feature trajectories (Stoner & Blanc style) + accuracy data
for Exp_DepthSwapCtrl_005m — ZdA, ZdB, N baseline.

Layout:
  Left  — 3×2 trajectory panels (rows=N/ZdA/ZdB, cols=CUED/UNCUED)
           Representative case: delayed Field B = Near
           Green solid = Field A (S0/S1); Red dashed = Field B (S2/S3)
           Heavy = coherent; Light = noise
           Depth track below motion track

  Right — Accuracy bar chart: N/ZdA/ZdB × CUED/UNCUED
           Data: binocular sessions 260330_1853 + 260331_0621
           Wilson 95% CIs

Key mechanics (DepthSwapCtrl, linkDepthColor=0 — depth independent of color):
  ZdA (coherent-half depth swap): S0+S2 swap depth planes at tStart
      ZdA-CUED:   translator = S2 → depth changes (Near→Far)   Depth✗
      ZdA-UNCUED: translator = S0 → depth changes (Far→Near)   Depth✗
  ZdB (noise-half depth swap): S1+S3 swap depth planes at tStart
      ZdB-CUED:   translator = S2 → depth unchanged (stays Near)  Depth✓
      ZdB-UNCUED: translator = S0 → depth unchanged (stays Far)   Depth✓
"""

import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.lines import Line2D
import matplotlib.patches as mpatches

# ── Paths ─────────────────────────────────────────────────────────────────────
DATA_FILES = [
    os.path.expanduser(
        '~/Library/Application Support/ThatsRandom/VRDotsDataFiles/'
        'vr_dots_session_260330_1853.tsv'),
    os.path.expanduser(
        '~/Library/Application Support/ThatsRandom/VRDotsDataFiles/'
        'vr_dots_session_260331_0621.tsv'),
]
OUT_BASE = os.path.expanduser(
    '~/Projects/ObjectBasedAttention/VRDots/Agents/SwapPilot/Figures/'
    'depth_swap_ctrl_traj_data')

# ── Timing (frames at 75 Hz) ──────────────────────────────────────────────────
ONSET   = 56
T_START = 78
T_END   = 84
T_MID   = (T_START + T_END) / 2
TOTAL   = 114

# Motion codes
CW, LINEAR, NONCOH, CCW = 1, 2, 3, 4
PLOT_Y = {CW: 1, LINEAR: 2, NONCOH: 2, CCW: 3}  # NONCOH plotted at T level

# Depth codes
NEAR, FAR = 1, 2
DEPTH_LABEL = {NEAR: 'Near', FAR: 'Far'}

# Representative case: delayed Field B = Near, always-on Field A = Far
B_DEP_DEFAULT = NEAR
A_DEP_DEFAULT = FAR

# Field/subfield visual properties (independent of depth in DepthSwapCtrl)
C_A = '#228B22'   # Field A (S0+S1): green (always-on)
C_B = '#CC3333'   # Field B (S2+S3): red (delayed onset)
SF_COLOR = {0: C_A, 1: C_A, 2: C_B, 3: C_B}
SF_LS    = {0: '-', 1: '-', 2: '--', 3: '--'}   # Field A solid, Field B dashed
SF_LW    = {0: 1.8, 1: 0.9, 2: 1.8, 3: 0.9}    # Coherent heavy, noise light

C_CUED   = '#1a3a8b'
C_UNCUED = '#884400'
ROW_SWAP_COLORS = {'N': '#444444', 'ZdA': '#C0392B', 'ZdB': '#1A6B1A'}

ROW_LABELS = {
    'N':   'N\nNo swap\n(baseline)',
    'ZdA': 'ZdA\nS0+S2 swap depth\nat tStart\n(translator disrupted)',
    'ZdB': 'ZdB\nS1+S3 swap depth\nat tStart\n(translator stable)',
}


# ── Build trajectory arrays ───────────────────────────────────────────────────
def build(swap, cued, b_dep=B_DEP_DEFAULT):
    """
    mt[TOTAL,4]  — motion codes (CW/LINEAR/NONCOH/CCW/0)
    dep[TOTAL,4] — depth codes (NEAR/FAR/0)

    swap : 'N', 'ZdA', 'ZdB'
    cued : True → Field B (S2) translates; False → Field A (S0) translates
    b_dep: depth of Field B at onset (representative case = NEAR)
    """
    a_dep = FAR if b_dep == NEAR else NEAR

    mt  = np.zeros((TOTAL, 4), dtype=int)
    dep = np.zeros((TOTAL, 4), dtype=int)

    for f in range(TOTAL):
        ao  = f >= ONSET
        as_ = f >= T_START
        tr  = T_START <= f < T_END

        # Default depths
        d0 = a_dep
        d1 = a_dep
        d2 = b_dep if ao else 0
        d3 = b_dep if ao else 0

        # Apply depth swap at tStart
        if as_:
            if swap == 'ZdA':    # S0+S2 (coherent) swap
                d0 = b_dep
                if ao: d2 = a_dep
            elif swap == 'ZdB':  # S1+S3 (noise) swap
                d1 = b_dep
                if ao: d3 = a_dep

        # Motion
        if not as_:
            m0, m1 = CW, CW
            m2 = CCW if ao else 0
            m3 = CCW if ao else 0
        elif tr:
            if cued:     # Field B (S2) translates
                m0, m1 = CW, CW
                m2, m3 = LINEAR, NONCOH
            else:        # Field A (S0) translates
                m0, m1 = LINEAR, NONCOH
                m2 = CCW if ao else 0
                m3 = CCW if ao else 0
        else:
            m0, m1 = CW, CW
            m2 = CCW if ao else 0
            m3 = CCW if ao else 0

        mt[f]  = [m0, m1, m2, m3]
        dep[f] = [d0, d1, d2, d3]

    return mt, dep


def translator_info(swap, cued, b_dep=B_DEP_DEFAULT):
    """Return (translator_depth_at_tStart, depth_check_str) for annotation."""
    a_dep = FAR if b_dep == NEAR else NEAR
    if cued:
        # Translator = S2 (Field B, default b_dep)
        t_dep = a_dep if swap == 'ZdA' else b_dep   # ZdA: S2 swaps to a_dep
    else:
        # Translator = S0 (Field A, default a_dep)
        t_dep = b_dep if swap == 'ZdA' else a_dep   # ZdA: S0 swaps to b_dep
    dep_s = '✗' if swap == 'ZdA' else '✓'
    return t_dep, dep_s


# ── Plot one trajectory panel ─────────────────────────────────────────────────
def plot_panel(ax_mt, ax_dep, mt, dep, swap, cued):
    t_dep, dep_s = translator_info(swap, cued)

    for si in range(4):
        frames = [f for f in range(TOTAL) if mt[f, si] != 0]
        if not frames:
            continue
        y_vals = [PLOT_Y[mt[f, si]] for f in frames]
        d_vals = [dep[f, si] for f in frames]

        ax_mt.plot(frames, y_vals,
                   color=SF_COLOR[si], ls=SF_LS[si], lw=SF_LW[si],
                   solid_capstyle='round', zorder=4)
        ax_dep.plot(frames, d_vals,
                    color=SF_COLOR[si], ls=SF_LS[si], lw=SF_LW[si],
                    solid_capstyle='round', zorder=4)

    # Phase markers
    for ax in (ax_mt, ax_dep):
        ax.axvspan(T_START, T_END, alpha=0.12, color='steelblue', zorder=1)
        ax.axvline(ONSET,   color='#CCCCCC', lw=0.7, ls=':', zorder=2)
        ax.axvline(T_START, color='#6688AA', lw=0.8, ls='--', zorder=2)

    # Gold band at translator depth (after tStart)
    ax_dep.axhspan(t_dep - 0.35, t_dep + 0.35, alpha=0.22, color='gold', zorder=0)

    # Translator label above translation window
    dir_str = 'CCW' if cued else 'CW'
    dep_str = DEPTH_LABEL[t_dep]
    ax_mt.text(T_MID, 3.65, f'Translator: {dir_str}/{dep_str}',
               ha='center', va='bottom', fontsize=4.5,
               color='#111', clip_on=False,
               bbox=dict(boxstyle='round,pad=0.25', facecolor='#f8f8f8',
                         edgecolor='#999', lw=0.6))

    # Axes
    ax_mt.set_yticks([1, 2, 3])
    ax_mt.set_yticklabels(['CW', 'T', 'CCW'], fontsize=5)
    ax_mt.set_ylim(0.4, 4.3)
    ax_mt.tick_params(axis='x', labelbottom=False)
    ax_mt.tick_params(axis='y', labelsize=5, length=2)
    ax_mt.set_xlim(-2, TOTAL + 1)

    ax_dep.set_yticks([NEAR, FAR])
    ax_dep.set_yticklabels(['Near', 'Far'], fontsize=5)
    ax_dep.set_ylim(0.4, 2.6)
    ax_dep.set_xlabel('Frame', fontsize=5)
    ax_dep.tick_params(axis='both', labelsize=5, length=2)
    ax_dep.set_xlim(-2, TOTAL + 1)

    for ax in (ax_mt, ax_dep):
        ax.spines[['top', 'right']].set_visible(False)


# ── Load & summarise data ─────────────────────────────────────────────────────
dfs = []
for p in DATA_FILES:
    dfs.append(pd.read_csv(p, sep='\t'))
df = pd.concat(dfs, ignore_index=True)

df = df[df['SwapType'].isin(['N', 'ZdA', 'ZdB'])].copy()
df['correct'] = (df['RespDeg'] == df['TransDeg']).astype(float)

summary = (df.groupby(['SwapType', 'Cond'])['correct']
             .agg(['mean', 'count', 'sum'])
             .reset_index())
summary.columns = ['SwapType', 'Cond', 'pct', 'n', 'hits']
summary['pct_pct'] = summary['pct'] * 100


def wilson_ci(hits, n, z=1.96):
    p = hits / n
    denom = 1 + z**2 / n
    centre = (p + z**2 / (2*n)) / denom
    half = z * np.sqrt(p*(1-p)/n + z**2/(4*n**2)) / denom
    return (centre - half)*100, (centre + half)*100


summary['lo']     = summary.apply(lambda r: wilson_ci(r.hits, r.n)[0], axis=1)
summary['hi']     = summary.apply(lambda r: wilson_ci(r.hits, r.n)[1], axis=1)
summary['err_lo'] = summary['pct_pct'] - summary['lo']
summary['err_hi'] = summary['hi'] - summary['pct_pct']

print("Summary:")
print(summary[['SwapType', 'Cond', 'n', 'pct_pct', 'lo', 'hi']].to_string(index=False))

# ── Figure ────────────────────────────────────────────────────────────────────
ROW_SWAPS = ['N', 'ZdA', 'ZdB']
COL_DEFS  = [(True, 'CUED'), (False, 'UNCUED')]

fig = plt.figure(figsize=(14, 10))
fig.patch.set_facecolor('white')
fig.suptitle(
    'DepthSwapCtrl_005m — Trajectories + Accuracy\n'
    'Binocular sessions 260330_1853 + 260331_0621  |  n=384  |  GS observer\n'
    'ZdA: coherent subfields (S0+S2) swap depth planes at tStart  ·  '
    'ZdB: noise subfields (S1+S3) swap depth planes at tStart  ·  linkDepthColor=0\n'
    'Trajectory representative case: Field B (delayed) = Near, Field A (always-on) = Far',
    fontsize=8.5, y=1.02)

outer = gridspec.GridSpec(1, 2, width_ratios=[2.2, 1.1], wspace=0.32,
                          left=0.08, right=0.97, top=0.90, bottom=0.10)

# ── Left: trajectory panels (3 rows × 2 cols) ────────────────────────────────
traj_gs = gridspec.GridSpecFromSubplotSpec(
    3, 2, subplot_spec=outer[0], hspace=1.00, wspace=0.30)

for ri, swap in enumerate(ROW_SWAPS):
    for ci, (cued, cond_label) in enumerate(COL_DEFS):

        inner = gridspec.GridSpecFromSubplotSpec(
            2, 1, subplot_spec=traj_gs[ri, ci],
            height_ratios=[3, 1.5], hspace=0.06)

        ax_mt  = fig.add_subplot(inner[0])
        ax_dep = fig.add_subplot(inner[1], sharex=ax_mt)

        mt, dep = build(swap, cued)

        _, dep_s = translator_info(swap, cued)
        dot_s = '✓' if cued else '✗'
        title = f'Dot{dot_s}   Depth{dep_s}'
        cc = C_CUED if cued else C_UNCUED
        title_kw = dict(fontsize=6.5, pad=4, color=cc, fontweight='bold',
                        bbox=dict(boxstyle='round,pad=0.3',
                                  facecolor='#f0f4ff' if cued else '#fff4e8',
                                  edgecolor=cc, lw=0.8))

        plot_panel(ax_mt, ax_dep, mt, dep, swap, cued)

        # Row + column headers
        if ri == 0:
            ax_mt.set_title(f'{cond_label}\n{title}', **title_kw)
        else:
            ax_mt.set_title(title, **title_kw)

        if ci == 0:
            rc = ROW_SWAP_COLORS[swap]
            ax_mt.set_ylabel(ROW_LABELS[swap] + '\n\nMotion',
                             fontsize=5.5, fontweight='bold', color=rc, labelpad=4)
        else:
            ax_mt.set_ylabel('Motion', fontsize=5)
        ax_dep.set_ylabel('Depth', fontsize=5)

# ── Right: accuracy bar chart ─────────────────────────────────────────────────
ax_bar = fig.add_subplot(outer[1])

swap_order = ['N', 'ZdA', 'ZdB']
swap_xlabels = {
    'N':   'N\n(baseline)',
    'ZdA': 'ZdA\n(coh swap)\ntrans. disrupted',
    'ZdB': 'ZdB\n(noise swap)\ntrans. stable',
}
x = np.arange(len(swap_order))
w = 0.30
chance = 100 / 8  # 12.5%

for ci, (cued, cond_label) in enumerate(COL_DEFS):
    color = C_CUED if cued else C_UNCUED
    vals, lo_errs, hi_errs, ns = [], [], [], []
    for sw in swap_order:
        row = summary[(summary.SwapType == sw) & (summary.Cond == cond_label)]
        if len(row):
            vals.append(row.pct_pct.values[0])
            lo_errs.append(row.err_lo.values[0])
            hi_errs.append(row.err_hi.values[0])
            ns.append(int(row.n.values[0]))
        else:
            vals.append(np.nan); lo_errs.append(0); hi_errs.append(0); ns.append(0)

    offset = (ci - 0.5) * w
    ax_bar.bar(x + offset, vals, w, color=color, alpha=0.85, label=cond_label,
               yerr=[lo_errs, hi_errs], capsize=4, error_kw={'lw': 1.2}, zorder=3)
    for xi, (v, hi_e, n) in enumerate(zip(vals, hi_errs, ns)):
        if not np.isnan(v):
            ax_bar.text(xi + offset, v + hi_e + 1.2, f'n={n}',
                        ha='center', va='bottom', fontsize=5.5, color=color)

# Cueing-effect annotations (Δ = CUED − UNCUED)
rng = np.random.default_rng(42)
for xi, sw in enumerate(swap_order):
    rc = summary[(summary.SwapType == sw) & (summary.Cond == 'CUED')]
    ru = summary[(summary.SwapType == sw) & (summary.Cond == 'UNCUED')]
    if len(rc) and len(ru):
        delta = rc.pct_pct.values[0] - ru.pct_pct.values[0]
        nc, hc = int(rc.n.values[0]), int(rc.hits.values[0])
        nu, hu = int(ru.n.values[0]), int(ru.hits.values[0])
        boot = (rng.binomial(nc, hc/nc, 5000)/nc -
                rng.binomial(nu, hu/nu, 5000)/nu) * 100
        ci_lo = np.percentile(boot, 2.5)
        ci_hi = np.percentile(boot, 97.5)
        # Significance stars
        if ci_lo > 0:
            stars = '***' if ci_lo > 5 else ('**' if ci_lo > 2 else '*')
        else:
            stars = 'n.s.'
        ax_bar.text(xi, 89, f'Δ={delta:+.1f}pp\n[{ci_lo:+.1f},{ci_hi:+.1f}]\n{stars}',
                    ha='center', va='center', fontsize=6, fontweight='bold',
                    color='#222',
                    bbox=dict(boxstyle='round,pad=0.25', facecolor='white',
                              edgecolor='#AAAAAA', lw=0.7))

ax_bar.axhline(chance, color='#AAAAAA', lw=1, ls='--', label='chance (12.5%)')
ax_bar.set_xticks(x)
ax_bar.set_xticklabels([swap_xlabels[s] for s in swap_order], fontsize=7)
ax_bar.set_ylabel('% Correct', fontsize=10)
ax_bar.set_ylim(0, 100)
ax_bar.set_title('Accuracy\n(CUED − UNCUED = cueing effect)',
                 fontsize=9, fontweight='bold')
ax_bar.legend(fontsize=8, framealpha=0.9, loc='upper left')
ax_bar.spines[['top', 'right']].set_visible(False)

# Add horizontal reference lines at notable accuracy levels
for y_ref, label, c_ref in [(37.5, 'N UNCUED', '#BBBBEE'), (53.1, 'N CUED', '#BBBBEE')]:
    ax_bar.axhline(y_ref, color=c_ref, lw=0.7, ls=':', zorder=0)

# ── Legend (bottom of left panel area) ───────────────────────────────────────
legend_handles = [
    Line2D([0],[0], color=C_A, ls='-',  lw=1.8,
           label='S0  Field A · coh  (solid heavy, green)'),
    Line2D([0],[0], color=C_A, ls='-',  lw=0.9,
           label='S1  Field A · noise  (solid light)'),
    Line2D([0],[0], color=C_B, ls='--', lw=1.8,
           label='S2  Field B · coh  (dashed heavy, red) — CUED translator'),
    Line2D([0],[0], color=C_B, ls='--', lw=0.9,
           label='S3  Field B · noise  (dashed light)'),
    mpatches.Patch(facecolor='gold',      alpha=0.4, edgecolor='#999',
                   label='Translator depth plane at tStart'),
    mpatches.Patch(facecolor='steelblue', alpha=0.2, edgecolor='none',
                   label='Translation window'),
    Line2D([0],[0], color='#CCCCCC', lw=0.8, ls=':', label='Field B onset'),
    Line2D([0],[0], color='#6688AA', lw=0.8, ls='--', label='tStart (depth swap)'),
]
fig.legend(handles=legend_handles, loc='lower center', ncol=4,
           fontsize=7, frameon=True, framealpha=0.95,
           edgecolor='#CCC', bbox_to_anchor=(0.5, -0.06))

os.makedirs(os.path.dirname(OUT_BASE), exist_ok=True)
fig.savefig(OUT_BASE + '.png', dpi=155, bbox_inches='tight', facecolor='white')
fig.savefig(OUT_BASE + '.pdf', bbox_inches='tight', facecolor='white')
print(f'\nSaved: {OUT_BASE}.png')
print(f'Saved: {OUT_BASE}.pdf')
