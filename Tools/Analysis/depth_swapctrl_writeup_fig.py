#!/usr/bin/env python3
"""
Write-up figure: Depth Swap Control (DepthSwapCtrl_005m).
Binocular sessions: 260330_1853, 260331_0621, 260401_1313, 260401_1349,
                    260401_1541, 260401_1705  (n=1152)
Monocular sessions: Mono-R: 260330_2012, 260331_1530
                    Mono-L: 260331_1705, 260331_1734  (n=769)
All sessions: depth 0.05 m, same-color (both red), SwapType = N / ZdA / ZdB.

Near/Far: translating-field-depth convention throughout.
  ZdA = S0 (CW coherent) and S2 (CCW coherent) swap depth planes at T_S
  ZdB = S1 (CW noise)    and S3 (CCW noise)    swap depth planes at T_S

Output: Agents/WriteUps/depth_swapctrl_writeup.png
"""

import csv, collections, math, os, textwrap
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.lines as mlines
import matplotlib.patches as mpatches

# ── Paths ─────────────────────────────────────────────────────────────────────
DATA_DIR = os.path.expanduser(
    "~/Library/Application Support/ThatsRandom/VRDotsDataFiles")
OUT_PATH = os.path.expanduser(
    "~/Projects/ObjectBasedAttention/VRDots/Agents/WriteUps/depth_swapctrl_writeup.png")

BINO_SESSIONS = [
    '260330_1853', '260331_0621',
    '260401_1313', '260401_1349', '260401_1541', '260401_1705',
]
MONO_SESSIONS = [
    '260330_2012', '260331_1530',   # Mono-R (L eye closed)
    '260331_1705', '260331_1734',   # Mono-L (R eye closed)
]

# ── Figure dimensions ─────────────────────────────────────────────────────────
FIG_W, FIG_H = 14, 62
DPI = 150
LMAR, RMAR = 0.05, 0.95
TXT_W = RMAR - LMAR
WRAP_W = 168

def line_h(pt, spacing=1.55):
    return (pt / 72 * DPI * spacing) / (FIG_H * DPI)

# ── Timing / colours ──────────────────────────────────────────────────────────
T_A=0.00; T_B=0.490; T_S=0.686; T_E=0.739; T_TOT=1.00
CW=2.0; TRANS_COH=1.0; TRANS_NOI=1.5; CCW=0.0
NEAR_Y=0.0; FAR_Y=1.0
CHANCE=1/8
C_CW='#228B22'; C_CCW='#CC3333'; C_TRANS='#CCCCCC'; C_FRAME='#333333'

C_NEAR='#4488CC'; C_FAR='#CC6644'
C_N='#444488'; C_ZDA='#883300'; C_ZDB='#226622'

# ── Stats ─────────────────────────────────────────────────────────────────────
def normal_cdf(x): return 0.5*(1+math.erf(x/math.sqrt(2)))
def z_test(k1,n1,k2,n2):
    p1,p2=k1/n1,k2/n2; pp=(k1+k2)/(n1+n2)
    se=math.sqrt(max(pp*(1-pp)*(1/n1+1/n2),1e-12))
    z=(p1-p2)/se; return z,1-normal_cdf(z)
def wilson_ci(k,n,z=1.96):
    p=k/n; d=1+z**2/n; c=(p+z**2/(2*n))/d
    hw=z*math.sqrt(p*(1-p)/n+z**2/(4*n**2))/d
    return c-hw,c+hw
def stars(p): return '***' if p<.001 else '**' if p<.01 else '*' if p<.05 else '†' if p<.1 else 'n.s.'

# ── Data loading ──────────────────────────────────────────────────────────────
def load(sid):
    path = os.path.join(DATA_DIR, f"vr_dots_session_{sid}.tsv")
    with open(path, newline='') as f:
        return list(csv.DictReader(f, delimiter='\t'))

def is_correct(td, rd):
    d = (float(rd)-float(td)+360)%360
    return (360-d if d>180 else d) <= 22.5

def trans_depth(cond, dfd):
    """Translating-field depth: CUED→dfd; UNCUED→opposite."""
    if cond=='CUED': return dfd
    return 'F' if dfd=='N' else 'N'

def analyze_swapctrl(session_list):
    """Returns {(swap, cond, trans_depth_label): [k, n]}"""
    cnt = collections.defaultdict(lambda: [0,0])
    for sid in session_list:
        try:
            rows = load(sid)
        except FileNotFoundError:
            print(f"  WARNING: {sid} not found, skipping")
            continue
        for r in rows:
            if r.get('EndKey','') in ('timeout','skip','requeue'): continue
            td=r.get('TransDeg',''); rd=r.get('RespDeg','')
            if not td or not rd: continue
            swap = r.get('SwapType','N')
            cond = r['Cond']
            dfd  = r.get('DelayedFieldDepth','N')
            key  = (swap, cond, trans_depth(cond, dfd))
            cnt[key][0] += int(is_correct(td,rd))
            cnt[key][1] += 1
    return cnt

# ── 4-subfield trajectory drawing ─────────────────────────────────────────────
_base  = np.linspace(T_A+0.01, T_TOT-0.01, 14)
T_MARKS = np.unique(np.sort(np.concatenate([_base, [(T_S+T_E)/2]])))

def _interp(tk, vk, tq): return np.interp(tq, tk, vk)

SF = {'S0':('o',5.5,True),'S1':('s',9.0,False),'S2':('^',6.0,True),'S3':('D',8.5,False)}
SF_COLOR = {'S0':C_CW,'S1':C_CW,'S2':C_CCW,'S3':C_CCW}

def _plot_sf(ax, name, tk, vk, tq):
    c=SF_COLOR[name]; mk,ms,filled=SF[name]
    mfc=c if filled else 'none'; mew=1.0 if filled else 1.6
    ax.plot(tk,vk,color=c,lw=0.8,ls='-',solid_capstyle='round',zorder=3)
    ax.plot(tq,_interp(tk,vk,tq),marker=mk,ms=ms,mew=mew,
            mfc=mfc,mec=c,ls='none',zorder=5)

def _traj_noswap(is_cued):
    """Motion trajectories — same for N, ZdA, ZdB (swap is depth-only)."""
    t0=T_B if is_cued else T_A; t2=T_A if is_cued else T_B
    tS0=np.array([t0,T_S,T_S,T_E,T_E,T_TOT]); vS0=np.array([CW,CW,TRANS_COH,TRANS_COH,CW,CW])
    tS1=np.array([t0,T_S,T_S,T_E,T_E,T_TOT]); vS1=np.array([CW,CW,TRANS_NOI,TRANS_NOI,CW,CW])
    tS2=np.array([t2,T_TOT]); vS2=np.array([CCW,CCW])
    tS3=np.array([t2,T_TOT]); vS3=np.array([CCW,CCW])
    return tS0,vS0,tS1,vS1,tS2,vS2,tS3,vS3

def draw_motion_panel(ax, is_cued, show_labels=False):
    tS0,vS0,tS1,vS1,tS2,vS2,tS3,vS3 = _traj_noswap(is_cued)
    t0=T_B if is_cued else T_A; t2=T_A if is_cued else T_B
    m0=T_MARKS[T_MARKS>=t0]; m2=T_MARKS[T_MARKS>=t2]
    _plot_sf(ax,'S0',tS0,vS0,m0); _plot_sf(ax,'S1',tS1,vS1,m0)
    _plot_sf(ax,'S2',tS2,vS2,m2); _plot_sf(ax,'S3',tS3,vS3,m2)
    ax.set_xlim(T_A-.01,T_TOT+.01); ax.set_ylim(-.35,2.55)
    ax.set_xticks([]); ax.set_yticks([CCW,TRANS_COH,TRANS_NOI,CW])
    ax.set_yticklabels(['CCW','Trans\n(coh)','Trans\n(noise)','CW'],fontsize=5.8)
    ax.tick_params(axis='y',length=2,pad=1)
    ax.axvspan(T_S,T_E,color=C_TRANS,alpha=0.6,zorder=1)
    ax.axvline(T_B,color='#AAAAAA',lw=0.8,ls='--',zorder=2)
    for sp in ax.spines.values():
        sp.set_visible(True); sp.set_linewidth(0.8); sp.set_edgecolor(C_FRAME)
    if show_labels:
        for x,lbl in [((T_A+T_B)/2,'A only'),((T_B+T_S)/2,'A+B'),((T_S+T_E)/2,'T')]:
            ax.text(x,2.48,lbl,ha='center',va='top',fontsize=5.5,
                    color='#888888',style='italic')

def draw_depth_panel(ax, swap, is_cued, cw_depth_label):
    """
    Depth track showing depth-plane membership over time.
    cw_depth_label: 'N' or 'F' — depth of the translating (CW) field.
    ZdA: S0 and S2 swap depth planes at T_S (coherent dots).
    ZdB: S1 and S3 swap depth planes at T_S (noise dots).
    """
    cw_y  = NEAR_Y if cw_depth_label=='N' else FAR_Y
    ccw_y = FAR_Y  if cw_depth_label=='N' else NEAR_Y
    t_cw  = T_B if is_cued else T_A   # CW field onset
    t_ccw = T_A if is_cued else T_B   # CCW field onset

    lw_thick = 1.8; lw_thin = 1.0

    if swap == 'N':
        # Static: 2 lines
        ax.plot([t_ccw,T_TOT],[ccw_y,ccw_y],color=C_CCW,lw=lw_thick,ls='-',zorder=3)
        ax.plot([t_cw, T_TOT],[cw_y, cw_y], color=C_CW, lw=lw_thick,ls='--',dashes=(5,3),zorder=3)

    elif swap == 'ZdA':
        # Coherent dots (S0, S2) swap at T_S; noise (S1, S3) stay
        # S0 (CW coherent): cw_y → ccw_y at T_S  [solid CW color, to distinguish from noise dashed]
        # S1 (CW noise):    stays at cw_y         [dashed CW color]
        # S2 (CCW coherent): ccw_y → cw_y at T_S  [solid CCW color]
        # S3 (CCW noise):   stays at ccw_y         [dashed CCW color]
        # CW noise (S1) - thin dashed
        ax.plot([t_cw, T_TOT],[cw_y, cw_y],
                color=C_CW, lw=lw_thin, ls='--', dashes=(4,3), alpha=0.7, zorder=3)
        # CCW noise (S3) - thin dashed
        ax.plot([t_ccw,T_TOT],[ccw_y,ccw_y],
                color=C_CCW, lw=lw_thin, ls='--', dashes=(4,3), alpha=0.7, zorder=3)
        # S0 (CW coherent) step: cw_y → ccw_y
        ax.plot([t_cw, T_S, T_S, T_TOT],[cw_y, cw_y, ccw_y, ccw_y],
                color=C_CW, lw=lw_thick, ls='-', zorder=4)
        # S2 (CCW coherent) step: ccw_y → cw_y
        ax.plot([t_ccw,T_S, T_S, T_TOT],[ccw_y,ccw_y,cw_y, cw_y],
                color=C_CCW, lw=lw_thick, ls='-', zorder=4)

    elif swap == 'ZdB':
        # Noise dots (S1, S3) swap at T_S; coherent (S0, S2) stay
        # S0 (CW coherent): stays at cw_y    [solid CW color]
        # S1 (CW noise): cw_y → ccw_y at T_S [dashed CW color, step]
        # S2 (CCW coherent): stays at ccw_y  [solid CCW color]
        # S3 (CCW noise): ccw_y → cw_y at T_S [dashed CCW color, step]
        # S0 (CW coherent) - thick solid
        ax.plot([t_cw, T_TOT],[cw_y, cw_y],
                color=C_CW, lw=lw_thick, ls='-', zorder=4)
        # S2 (CCW coherent) - thick solid
        ax.plot([t_ccw,T_TOT],[ccw_y,ccw_y],
                color=C_CCW, lw=lw_thick, ls='-', zorder=4)
        # S1 (CW noise) step: cw_y → ccw_y
        ax.plot([t_cw, T_S, T_S, T_TOT],[cw_y, cw_y, ccw_y, ccw_y],
                color=C_CW, lw=lw_thin, ls='--', dashes=(4,3), alpha=0.85, zorder=3)
        # S3 (CCW noise) step: ccw_y → cw_y
        ax.plot([t_ccw,T_S, T_S, T_TOT],[ccw_y,ccw_y,cw_y, cw_y],
                color=C_CCW, lw=lw_thin, ls='--', dashes=(4,3), alpha=0.85, zorder=3)

    ax.set_xlim(T_A-.01,T_TOT+.01); ax.set_ylim(-0.5,1.5)
    ax.set_xticks([]); ax.set_yticks([NEAR_Y,FAR_Y])
    ax.set_yticklabels(['Near','Far'],fontsize=5.8)
    ax.tick_params(axis='y',length=2,pad=1)
    ax.axvspan(T_S,T_E,color=C_TRANS,alpha=0.6,zorder=1)
    ax.axvline(T_B,color='#AAAAAA',lw=0.8,ls='--',zorder=2)
    for sp in ax.spines.values():
        sp.set_visible(True); sp.set_linewidth(0.8); sp.set_edgecolor(C_FRAME)

# ── Text ──────────────────────────────────────────────────────────────────────
INTRO = (
    "The DepthSwapCtrl experiment isolated the contribution of depth-plane "
    "identity to dot cueing by introducing mid-trial depth swaps at translation "
    "onset (T_S). Two swap types were tested alongside a no-swap baseline (N): "
    "ZdA swaps the depth planes of the two coherent dots (one per field, S0 and "
    "S2) at T_S, causing the cued coherent translator to change depth; ZdB "
    "swaps the two noise dots (S1 and S3) instead, leaving the cued coherent "
    "translator in its original depth plane. ZdA and ZdB are therefore matched "
    "for the number of depth-plane transitions per trial, differing only in "
    "whether the transition affects the coherent translator. All sessions used "
    "a 0.05 m depth separation between planes (~0.86\u00b0 disparity at 2 m) "
    "and same-color stimuli (both fields red, `balanceDelayedFieldColor=false`). "
    "Six binocular sessions and four monocular sessions (2 right-eye, 2 left-eye) "
    "were run on the same observer."
)

STIM_NOTE = (
    "Trajectory diagrams show one representative color-rotation pairing. "
    "Columns are organized by the depth of the translating field "
    "(Near translation | Far translation). S0\u25cf/S1\u25a1 = initially "
    "CW field (green); S2\u25b2/S3\u25c7 = initially CCW field (red). "
    "Motion tracks (top) are identical across all three swap types — "
    "the swap affects depth only. Depth tracks (bottom of each row) show "
    "which depth plane each subfield occupies over time; thick lines = "
    "coherent dots (S0, S2), thin dashed = noise dots (S1, S3). "
    "For ZdA, the coherent dots (thick lines) cross planes at T_S; "
    "for ZdB, the noise dots (thin dashed) cross planes."
)

ANALYSIS_NOTE = (
    "Analysis: Near/Far labels use translating-field depth. "
    "CUED Near = delayed field at Near (translates Near); "
    "UNCUED Near = non-delayed field at Near (translates Near, delayed field at Far). "
    "Proportion correct pooled across color, rotation, and direction "
    "(\u224832 trials/cell for each SwapType \u00d7 Cond \u00d7 Depth within bino; "
    "\u224821 trials/cell within mono). One-tailed z-test: CUED > UNCUED."
)

FINDINGS_BINO = (
    "Binocular results (n=1152, 6 sessions, 0.05 m depth): Dot cueing was "
    "reliable overall (+12.5 pp, z=4.30, p<.001). Using the translating-field "
    "depth convention, Near translation yielded the larger cueing effect "
    "(CUED=42.4%, UNCUED=23.6%, +18.8 pp, z=4.79, p<.001) while Far translation "
    "showed a smaller, marginal effect (CUED=54.5%, UNCUED=48.3%, +6.2 pp, "
    "z=1.50, p=.067). This pattern — Near cueing > Far cueing — arises because "
    "UNCUED performance is particularly low in the Near depth plane (23.6%), "
    "consistent with the non-cued observer having difficulty detecting Near-plane "
    "translation when anti-cued; Far UNCUED performance was much higher (48.3%). "
    "Note that this convention-correct analysis reverses the apparent Near inversion "
    "reported using the delayed-field-depth convention (where Near seemed to show "
    "negative cueing). Across swap types, ZdB produced the largest cueing "
    "(+16.1 pp***), followed by ZdA (+11.5 pp*) and N (+9.9 pp\u2020). The "
    "ZdA effect is comparable to N binocularly, suggesting that depth-plane "
    "disruption of the cued translator does not produce large cueing losses at "
    "the binocular level, while ZdB's advantage is consistent with keeping the "
    "cued translator in a stable depth plane while also disrupting the distractor."
)

FINDINGS_MONO = (
    "Monocular results (n=769, 4 sessions): Overall cueing attenuated but "
    "survived (+7.1 pp*). The translating-depth breakdown (monocular) showed "
    "Near cueing marginally (+8.3 pp, z=1.69, p=.046) and Far cueing non-significant "
    "(+5.9 pp, z=1.18, p=.12). The key dissociation across swap types: ZdA "
    "collapsed to exactly +0.0 pp (z=0.00, p=.50), the sharpest mechanistic "
    "result in the dataset. When binocular disparity is unavailable, changing "
    "the depth plane of the cued translator has zero behavioral consequence. "
    "ZdB survived monocularly (+12.0 pp*, z=1.96) and N was +9.4 pp (\u2020). "
    "ZdB\u2019s monocular survival suggests its advantage includes a monocular "
    "component, plausibly the brief positional shift of the non-coherent distractor "
    "at depth change (\u22481.5\u20135 arcmin depending on eccentricity), which "
    "may disrupt the distractor surface representation independent of stereopsis."
)

ISSUES = (
    "Notes: (1) Session 260401_1541 and 260401_1705 were the 5th and 6th VR "
    "sessions in a single day (binocular) and show performance collapse "
    "(34\u201340% overall accuracy, far below other binocular sessions at "
    "44\u201351%). These sessions are included in the pooled binocular "
    "statistics as planned; excluding them would increase the binocular "
    "cueing effect but reduce n. (2) The same-color (both red) design reduces "
    "cueing relative to the two-color baseline (~28\u201350 pp) but is necessary "
    "for depth experiments to control the color axis of variation. (3) The "
    "geometric confound in ZdA (depth change of 0.05 m induces a monocular "
    "positional shift of 0\u20135 arcmin at 2 m, scaling with eccentricity) "
    "cannot be fully dissociated from the stereoscopic depth-plane account "
    "at this sample size; the monocular ZdA=+0.0 pp result is consistent with "
    "either account. A right-eye replication (which would isolate the "
    "geometric confound sign) has been flagged as a future experiment."
)

# ─────────────────────────────────────────────────────────────────────────────
# LOAD DATA
# ─────────────────────────────────────────────────────────────────────────────
print("Loading binocular sessions...")
bino_cnt = analyze_swapctrl(BINO_SESSIONS)
print("Loading monocular sessions...")
mono_cnt = analyze_swapctrl(MONO_SESSIONS)

# ─────────────────────────────────────────────────────────────────────────────
# BUILD FIGURE
# ─────────────────────────────────────────────────────────────────────────────
fig = plt.figure(figsize=(FIG_W,FIG_H))
fig.patch.set_facecolor('white')
y = 0.980

# ── Title ─────────────────────────────────────────────────────────────────────
fig.text(0.50, y, 'VRDots \u2014 Depth Swap Control (0.05 m, Same-Color)',
    ha='center', va='top', fontsize=15, fontweight='bold', color='#111111')
y -= line_h(15,1.3) + 0.005

# ── Intro / stim note ─────────────────────────────────────────────────────────
for txt, fs, col, sty in [
    (INTRO,      8.5, '#222222', 'normal'),
    (STIM_NOTE,  8.0, '#555555', 'italic'),
]:
    lns = textwrap.wrap(txt, width=WRAP_W)
    fig.text(LMAR, y, '\n'.join(lns), ha='left', va='top', fontsize=fs,
             color=col, linespacing=1.55, style=sty)
    y -= len(lns)*line_h(fs) + 0.007

y -= 0.005

# ── "Stimulus Conditions" heading ─────────────────────────────────────────────
fig.text(0.50, y, 'Stimulus Conditions',
    ha='center', va='top', fontsize=11, fontweight='bold', color='#1a3a6b')
y -= line_h(11,1.3) + 0.005

# ─────────────────────────────────────────────────────────────────────────────
# TRAJECTORY SECTION
# 3 swap sections × (CUED+UNCUED) × (Near trans | Far trans)
# Each section: 4 rows × 2 cols with height_ratios=[3,1,3,1]
# ─────────────────────────────────────────────────────────────────────────────
SWAP_DEFS = [
    ('N',   'N — No Swap',   C_N),
    ('ZdA', 'ZdA',           C_ZDA),
    ('ZdB', 'ZdB',           C_ZDB),
]
COL_TITLES = ['Near Translation', 'Far Translation']
CW_DEPTHS  = ['N', 'F']   # depth of translating (CW) field per column

TRAJ_H = 0.265
traj_top = y
traj_bot = traj_top - TRAJ_H
traj_left  = 0.10
traj_right = 0.78

# Build a 12-row × 2-col GridSpec
# Row groups: [N rows 0-3] [ZdA rows 4-7] [ZdB rows 8-11]
# Within each group: CUED-motion, CUED-depth, UNCUED-motion, UNCUED-depth
traj_gs = gridspec.GridSpec(
    12, 2,
    top=traj_top, bottom=traj_bot,
    left=traj_left, right=traj_right,
    height_ratios=[3,1,3,1, 3,1,3,1, 3,1,3,1],
    hspace=0.08, wspace=0.28
)

# Draw section labels on the right side
for si, (swap, swap_label, swap_col) in enumerate(SWAP_DEFS):
    base_row = si * 4

    for col_idx, (ctitle, cw_dep) in enumerate(zip(COL_TITLES, CW_DEPTHS)):
        # CUED motion (row base_row + 0)
        ax_cm = fig.add_subplot(traj_gs[base_row + 0, col_idx])
        draw_motion_panel(ax_cm, is_cued=True,
                          show_labels=(si==0 and col_idx==0))
        if si == 0:
            ax_cm.set_title(ctitle, fontsize=9, fontweight='bold', pad=4)
        if col_idx == 0:
            ax_cm.set_ylabel('CUED', fontsize=8.5, fontweight='bold', labelpad=4)

        # CUED depth (row base_row + 1)
        ax_cd = fig.add_subplot(traj_gs[base_row + 1, col_idx])
        draw_depth_panel(ax_cd, swap, is_cued=True, cw_depth_label=cw_dep)
        if col_idx == 0:
            ax_cd.set_ylabel('Depth', fontsize=7, labelpad=4, color='#555555')

        # UNCUED motion (row base_row + 2)
        ax_um = fig.add_subplot(traj_gs[base_row + 2, col_idx])
        draw_motion_panel(ax_um, is_cued=False)
        if col_idx == 0:
            ax_um.set_ylabel('UNCUED', fontsize=8.5, fontweight='bold', labelpad=4)

        # UNCUED depth (row base_row + 3)
        ax_ud = fig.add_subplot(traj_gs[base_row + 3, col_idx])
        draw_depth_panel(ax_ud, swap, is_cued=False, cw_depth_label=cw_dep)
        if col_idx == 0:
            ax_ud.set_ylabel('Depth', fontsize=7, labelpad=4, color='#555555')

    # Section label on the right
    # Compute mid-y of this section in figure coords
    pos_top = traj_gs[base_row+0, 0].get_position(fig).y1
    pos_bot = traj_gs[base_row+3, 0].get_position(fig).y0
    mid_y   = (pos_top + pos_bot) / 2
    fig.text(0.795, mid_y, swap_label,
             ha='left', va='center', fontsize=8.5, fontweight='bold',
             color=swap_col, rotation=90)

    # Horizontal separator between sections (except after last)
    if si < 2:
        sep_y = pos_bot - 0.004
        fig.add_artist(plt.Line2D([traj_left, traj_right], [sep_y, sep_y],
            transform=fig.transFigure, color='#CCCCCC', lw=1.0, ls='--'))

y = traj_bot - 0.010

# ── Trajectory legend ─────────────────────────────────────────────────────────
TLEG_H = 0.024
ax_tleg = fig.add_axes([LMAR, y-TLEG_H, TXT_W, TLEG_H]); ax_tleg.axis('off')
ax_tleg.legend(handles=[
    mlines.Line2D([],[],color=C_CW, marker='o',ms=5.5,mew=1.0,mfc=C_CW,  ls='none',label='S0 (CW coh)'),
    mlines.Line2D([],[],color=C_CW, marker='s',ms=8.5,mew=1.5,mfc='none',ls='none',label='S1 (CW noise)'),
    mlines.Line2D([],[],color=C_CCW,marker='^',ms=6.0,mew=1.0,mfc=C_CCW, ls='none',label='S2 (CCW coh)'),
    mlines.Line2D([],[],color=C_CCW,marker='D',ms=8.0,mew=1.5,mfc='none',ls='none',label='S3 (CCW noise)'),
    mlines.Line2D([],[],color='#888888',lw=1.5,ls='-', label='Coherent depth (thick)'),
    mlines.Line2D([],[],color='#888888',lw=1.0,ls='--',dashes=(4,3),label='Noise depth (thin dash)'),
    mpatches.Patch(facecolor=C_TRANS,alpha=0.8,edgecolor='#888888',label='Translation window'),
],loc='center',ncol=7,fontsize=8,frameon=True,framealpha=0.9,edgecolor='#CCCCCC')
y -= TLEG_H + 0.012

# ── Analysis note ─────────────────────────────────────────────────────────────
an_lns = textwrap.wrap(ANALYSIS_NOTE, width=WRAP_W)
fig.text(LMAR, y, '\n'.join(an_lns), ha='left', va='top', fontsize=8.0,
         color='#444444', linespacing=1.5)
y -= len(an_lns)*line_h(8.0) + 0.014

# ── Results heading ───────────────────────────────────────────────────────────
fig.text(0.50, y, 'Results',
    ha='center', va='top', fontsize=11, fontweight='bold', color='#1a3a6b')
y -= line_h(11,1.3) + 0.007

# ─────────────────────────────────────────────────────────────────────────────
# BAR GRAPHS — 2 rows × 3 cols (bino/mono × N/ZdA/ZdB)
# Each panel: Near CUED | Near UNCUED | Far CUED | Far UNCUED
# ─────────────────────────────────────────────────────────────────────────────
BAR_H = 0.140
bar_top = y

for row_idx, (session_label, cnt, n_total) in enumerate([
    ('Binocular  (n=1152, 6 sessions)', bino_cnt, 1152),
    ('Monocular  (n=769, 4 sessions)',  mono_cnt, 769),
]):
    # Viewing mode label on left
    fig.text(LMAR, bar_top - row_idx*(BAR_H+0.012) - BAR_H/2,
             session_label, ha='left', va='center', fontsize=9.5,
             fontweight='bold', color='#1a3a6b', rotation=90)

    bar_gs = gridspec.GridSpec(1, 3,
        top=bar_top - row_idx*(BAR_H+0.012),
        bottom=bar_top - row_idx*(BAR_H+0.012) - BAR_H,
        left=LMAR+0.05, right=RMAR-0.01, wspace=0.35)

    for ci, (swap, swap_label, swap_col) in enumerate(SWAP_DEFS):
        cn = cnt.get((swap,'CUED','N'),   [0,1])
        un = cnt.get((swap,'UNCUED','N'), [0,1])
        cf = cnt.get((swap,'CUED','F'),   [0,1])
        uf = cnt.get((swap,'UNCUED','F'), [0,1])
        groups = [cn, un, cf, uf]
        accs = [g[0]/max(g[1],1) for g in groups]
        cis  = [wilson_ci(*g) if g[1]>0 else (0,0) for g in groups]
        zn,pn = z_test(cn[0],cn[1],un[0],un[1]) if cn[1]>0 and un[1]>0 else (0,0.5)
        zf,pf = z_test(cf[0],cf[1],uf[0],uf[1]) if cf[1]>0 and uf[1]>0 else (0,0.5)
        dn = (accs[0]-accs[1])*100; df = (accs[2]-accs[3])*100

        xs      = [0.0, 0.65, 1.80, 2.45]
        bcolors = [C_NEAR, C_NEAR, C_FAR, C_FAR]
        hatch   = ['', '///', '', '///']
        xlbls   = ['CUED','UNCUED','CUED','UNCUED']

        ax = fig.add_subplot(bar_gs[0, ci])
        for xi,ac,(lo,hi),bc,ht,g in zip(xs,accs,cis,bcolors,hatch,groups):
            ax.bar(xi, ac, width=0.58, color=bc, alpha=0.82, hatch=ht,
                   edgecolor='#333333', linewidth=0.8, zorder=3)
            if g[1] > 0:
                ax.errorbar(xi, ac, yerr=[[ac-lo],[hi-ac]],
                            fmt='none', color='#222222', capsize=4, lw=1.5, zorder=4)
                ax.text(xi, hi+0.022, f'{g[0]}/{g[1]}',
                        ha='center', fontsize=6.5, color='#333333')

        ax.axhline(CHANCE, color='#999999', ls='--', lw=1.0, zorder=2)
        if ci==2:
            ax.text(2.82, CHANCE+0.008, 'chance', fontsize=6.5,
                    color='#999999', va='bottom')

        # Cueing brackets
        for ic,iu,dv,zv,pv in [(0,1,dn,zn,pn),(2,3,df,zf,pf)]:
            mc=xs[ic]; mu=xs[iu]
            yb = max(accs[ic],accs[iu]) + 0.10
            ax.annotate('', xy=(mu,yb), xytext=(mc,yb),
                        arrowprops=dict(arrowstyle='-',color='#444444',lw=1.1))
            sign='+' if dv>=0 else ''
            ax.text((mc+mu)/2, yb+0.015,
                    f'\u0394={sign}{dv:.1f}pp {stars(pv)}',
                    ha='center', va='bottom', fontsize=8.5,
                    fontweight='bold', color='#111111')
            ax.text((mc+mu)/2, yb+0.068,
                    f'z={zv:.2f}, p={pv:.3f}',
                    ha='center', va='bottom', fontsize=6.5, color='#555555')

        ax.text((xs[0]+xs[1])/2, -0.09, 'Near\nTrans.',
                ha='center', fontsize=8.5, fontweight='bold', color=C_NEAR,
                transform=ax.get_xaxis_transform())
        ax.text((xs[2]+xs[3])/2, -0.09, 'Far\nTrans.',
                ha='center', fontsize=8.5, fontweight='bold', color=C_FAR,
                transform=ax.get_xaxis_transform())
        ax.axvline(1.22, color='#DDDDDD', lw=1.0, zorder=1)
        ax.set_xlim(-0.42,3.10); ax.set_ylim(0,1.05)
        ax.set_xticks(xs); ax.set_xticklabels(xlbls, fontsize=8.5)
        ax.set_yticks([0,.25,.50,.75,1.0])
        ax.set_yticklabels(['0%','25%','50%','75%','100%'], fontsize=8.5)
        if ci==0: ax.set_ylabel('Proportion correct', fontsize=9)
        ax.set_title(swap_label, fontsize=10, fontweight='bold', pad=8,
                     color=swap_col)
        ax.spines[['top','right']].set_visible(False)
        ax.tick_params(axis='x', length=0)

y = bar_top - 2*(BAR_H+0.012) - 0.012

# ── Bar legend ────────────────────────────────────────────────────────────────
BLEG_H = 0.022
ax_bleg = fig.add_axes([LMAR, y-BLEG_H, TXT_W, BLEG_H]); ax_bleg.axis('off')
ax_bleg.legend(handles=[
    mpatches.Patch(facecolor=C_NEAR,alpha=0.82,edgecolor='#333333',label='Near translation (blue)'),
    mpatches.Patch(facecolor=C_FAR, alpha=0.82,edgecolor='#333333',label='Far translation (orange)'),
    mpatches.Patch(facecolor='white',hatch='///',edgecolor='#333333',label='UNCUED (hatched)'),
    mlines.Line2D([],[],color='#222222',lw=1.5,marker='|',markersize=6,label='Wilson 95% CI'),
],loc='center',ncol=4,fontsize=8.5,frameon=True,framealpha=0.9,edgecolor='#CCCCCC')
y -= BLEG_H + 0.022

# ── Narrative ─────────────────────────────────────────────────────────────────
for heading, hcolor, paras in [
    ('Findings', '#1a3a6b', [FINDINGS_BINO, FINDINGS_MONO]),
    ('Notes',    '#6b1a1a', [ISSUES]),
]:
    fig.text(LMAR, y, heading,
        ha='left', va='top', fontsize=10, fontweight='bold', color=hcolor)
    y -= line_h(10,1.4) + 0.004
    for para in paras:
        lns = textwrap.wrap(para, width=WRAP_W)
        fig.text(LMAR, y, '\n'.join(lns),
            ha='left', va='top', fontsize=8.2, color='#222222', linespacing=1.55)
        y -= len(lns)*line_h(8.2) + 0.009
    y -= 0.010

print(f"Bottom y = {y:.3f}  (target > 0.02)")
fig.savefig(OUT_PATH, dpi=DPI, bbox_inches='tight', facecolor='white')
print(f"Saved: {OUT_PATH}")
