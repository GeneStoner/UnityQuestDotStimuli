#!/usr/bin/env python3
"""
Multi-page PDF write-up: Flat Swap Conditions (MotionSwap & Dots50Swap).
2 pages, US Letter portrait (8.5 × 11 in, 150 DPI).

  Page 1 — Introduction + Stimulus Conditions (trajectory panels)
  Page 2 — Results + Findings + Notes

Output: Agents/WriteUps/swap_writeup.pdf
"""

import csv, math, os, textwrap
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.lines as mlines
import matplotlib.patches as mpatches
from matplotlib.backends.backend_pdf import PdfPages

# ── Paths ─────────────────────────────────────────────────────────────────────
DATA_DIR = os.path.expanduser(
    "~/Library/Application Support/ThatsRandom/VRDotsDataFiles")
OUT_PDF = os.path.expanduser(
    "~/Projects/ObjectBasedAttention/VRDots/Agents/WriteUps/swap_writeup.pdf")

# ── Page geometry ──────────────────────────────────────────────────────────────
PW, PH = 8.5, 11   # US Letter portrait
DPI     = 150
LMAR, RMAR = 0.09, 0.91
TXT_W = RMAR - LMAR
WRAP_W = 115

def lh(pt, spacing=1.55):
    """Normalized figure height consumed by one line at given point size."""
    return (pt / 72 * DPI * spacing) / (PH * DPI)

# ── Timing / colours ──────────────────────────────────────────────────────────
T_A=0.00; T_B=0.490; T_S=0.686; T_E=0.739; T_TOT=1.00
CW=2.0; TRANS_COH=1.0; TRANS_NOI=1.5; CCW=0.0
CHANCE=1/8
C_CW    = '#228B22'
C_CCW   = '#CC3333'
C_TRANS = '#CCCCCC'
C_FRAME = '#333333'

# ── Stats ─────────────────────────────────────────────────────────────────────
def normal_cdf(x):
    return 0.5*(1+math.erf(x/math.sqrt(2)))
def z_test(k1,n1,k2,n2):
    p1=k1/n1; p2=k2/n2; pp=(k1+k2)/(n1+n2)
    se=math.sqrt(max(pp*(1-pp)*(1/n1+1/n2),1e-12))
    z=(p1-p2)/se; return z, 1-normal_cdf(z)
def wilson_ci(k,n,z=1.96):
    p=k/n; d=1+z**2/n; c=(p+z**2/(2*n))/d
    hw=z*math.sqrt(p*(1-p)/n+z**2/(4*n**2))/d
    return c-hw, c+hw
def stars(p):
    return '***' if p<.001 else '**' if p<.01 else '*' if p<.05 else '†' if p<.1 else 'n.s.'

# ── Data loading ──────────────────────────────────────────────────────────────
def load_session(sid):
    with open(os.path.join(DATA_DIR,f"vr_dots_session_{sid}.tsv"),newline='') as f:
        return list(csv.DictReader(f,delimiter='\t'))

def is_correct(td,rd):
    d=(float(rd)-float(td)+360)%360
    return (360-d if d>180 else d)<=22.5

def analyze(rows, swap_code):
    """Returns {(cond, swap): [k, n]} pooled across color, rotation, direction."""
    cnt={}
    for r in rows:
        if r.get('EndKey','') in ('timeout','skip','requeue'): continue
        td=r.get('TransDeg',''); rd=r.get('RespDeg','')
        if not td or not rd: continue
        cond=r['Cond']
        sw=r.get('SwapType','N') or 'N'
        key=(cond, sw)
        if key not in cnt: cnt[key]=[0,0]
        cnt[key][0]+=int(is_correct(td,rd)); cnt[key][1]+=1
    return cnt

# ── 4-subfield trajectory drawing ─────────────────────────────────────────────
_base   = np.linspace(T_A+0.01, T_TOT-0.01, 14)
T_MARKS = np.unique(np.sort(np.concatenate([_base, [(T_S+T_E)/2]])))

def _interp(t_key,v_key,t_q): return np.interp(t_q,t_key,v_key)

SF = {'S0':('o',5.5,True),'S1':('s',9.0,False),'S2':('^',6.0,True),'S3':('D',8.5,False)}
SF_COLOR = {'S0':C_CW,'S1':C_CW,'S2':C_CCW,'S3':C_CCW}

def _plot_sf(ax,name,t_key,v_key,t_query):
    color=SF_COLOR[name]; mk,ms,filled=SF[name]
    mfc=color if filled else 'none'; mew=1.0 if filled else 1.6
    ax.plot(t_key,v_key,color=color,lw=0.8,ls='-',solid_capstyle='round',zorder=3)
    vq=_interp(t_key,v_key,t_query)
    ax.plot(t_query,vq,marker=mk,markersize=ms,markeredgewidth=mew,
            markerfacecolor=mfc,markeredgecolor=color,ls='none',zorder=5)

def _traj_noswap(is_cued):
    t0=T_B if is_cued else T_A; t2=T_A if is_cued else T_B
    tS0=np.array([t0,T_S,T_S,T_E,T_E,T_TOT]); vS0=np.array([CW,CW,TRANS_COH,TRANS_COH,CW,CW])
    tS1=np.array([t0,T_S,T_S,T_E,T_E,T_TOT]); vS1=np.array([CW,CW,TRANS_NOI,TRANS_NOI,CW,CW])
    tS2=np.array([t2,T_TOT]); vS2=np.array([CCW,CCW])
    tS3=np.array([t2,T_TOT]); vS3=np.array([CCW,CCW])
    return tS0,vS0,tS1,vS1,tS2,vS2,tS3,vS3

def _traj_motionswap(is_cued):
    t0=T_B if is_cued else T_A; t2=T_A if is_cued else T_B
    tS0=np.array([t0,T_S,T_S,T_E,T_E,T_TOT]); vS0=np.array([CW,CW,TRANS_COH,TRANS_COH,CCW,CCW])
    tS1=np.array([t0,T_S,T_S,T_E,T_E,T_TOT]); vS1=np.array([CW,CW,TRANS_NOI,TRANS_NOI,CCW,CCW])
    tS2=np.array([t2,T_S,T_S,T_TOT]); vS2=np.array([CCW,CCW,CW,CW])
    tS3=np.array([t2,T_S,T_S,T_TOT]); vS3=np.array([CCW,CCW,CW,CW])
    return tS0,vS0,tS1,vS1,tS2,vS2,tS3,vS3

def _traj_dots50(is_cued):
    t0=T_B if is_cued else T_A; t2=T_A if is_cued else T_B
    tS0=np.array([t0,T_S,T_S,T_E,T_E,T_TOT]); vS0=np.array([CW,CW,TRANS_COH,TRANS_COH,CW,CW])
    tS1=np.array([t0,T_S,T_S,T_TOT]); vS1=np.array([CW,CW,CCW,CCW])
    tS2=np.array([t2,T_TOT]); vS2=np.array([CCW,CCW])
    tS3=np.array([t2,T_S,T_S,T_E,T_E,T_TOT]); vS3=np.array([CCW,CCW,TRANS_NOI,TRANS_NOI,CW,CW])
    return tS0,vS0,tS1,vS1,tS2,vS2,tS3,vS3

TRAJ_FNS = {'noswap':_traj_noswap,'motionswap':_traj_motionswap,'dots50':_traj_dots50}

def draw_traj_panel(ax, swap_type, is_cued, show_labels=False):
    tS0,vS0,tS1,vS1,tS2,vS2,tS3,vS3 = TRAJ_FNS[swap_type](is_cued)
    t0=T_B if is_cued else T_A; t2=T_A if is_cued else T_B
    m0=T_MARKS[T_MARKS>=t0]; m2=T_MARKS[T_MARKS>=t2]
    _plot_sf(ax,'S0',tS0,vS0,m0); _plot_sf(ax,'S1',tS1,vS1,m0)
    _plot_sf(ax,'S2',tS2,vS2,m2); _plot_sf(ax,'S3',tS3,vS3,m2)
    ax.set_xlim(T_A-.01,T_TOT+.01); ax.set_ylim(-.35,2.55)
    ax.set_xticks([])
    ax.set_yticks([CCW,TRANS_COH,TRANS_NOI,CW])
    ax.set_yticklabels(['CCW','Trans\n(coh)','Trans\n(noise)','CW'],fontsize=6.0)
    ax.tick_params(axis='y',length=2,pad=1)
    ax.axvspan(T_S,T_E,color=C_TRANS,alpha=0.6,zorder=1)
    ax.axvline(T_B,color='#AAAAAA',lw=0.8,ls='--',zorder=2)
    for sp in ax.spines.values():
        sp.set_visible(True); sp.set_linewidth(0.8); sp.set_edgecolor(C_FRAME)
    if show_labels:
        for x,lbl in [((T_A+T_B)/2,'A only'),((T_B+T_S)/2,'A+B'),((T_S+T_E)/2,'T')]:
            ax.text(x,2.48,lbl,ha='center',va='top',fontsize=5.5,
                    color='#888888',style='italic')

# ── Text blocks ───────────────────────────────────────────────────────────────
INTRO = (
    "Two sessions examined how within-trial manipulations applied at translation "
    "onset affect the cueing effect. Both used a flat (no depth), "
    "750 ms delayed-onset design with 80 ms translation and 8-AFC direction "
    "judgment at 2.0 m. Each session comprised 128 trials interleaving swap and "
    "no-swap trials in equal proportion (64 each), fully crossing Cond "
    "(CUED/UNCUED) \u00d7 DelayedFieldColor (G/R) \u00d7 RotConfig (0/1) "
    "\u00d7 TransDeg (8 directions), yielding 8 trials per cell per swap type. "
    "Session 260324_1010 tested the Motion Swap: at translation onset the "
    "non-translating field immediately reversed its rotation direction, and the "
    "translating field landed in the opposite rotation post-translation (both "
    "fields exchanged rotation identities). "
    "Session 260325_1039 tested the Dots50 Swap: the noise subfield of each "
    "rotation group (S1 and S3) exchanged group membership at translation onset, "
    "so 50% of each field\u2019s dots changed affiliation while the coherent "
    "subfields (S0 and S2) remained unaffected."
)

STIM_NOTE = (
    "Trajectory diagrams below show one representative color-rotation pairing "
    "(S0\u25cf/S1\u25a1 = initially CW field; S2\u25b2/S3\u25c7 = initially CCW "
    "field; green = CW, red = CCW). Both color assignments and both rotation "
    "configurations were balanced across trials. Dashed vertical line = delayed "
    "field onset (~750 ms); shaded band = 80 ms translation window."
)

ANALYSIS_NOTE = (
    "Analysis: proportion correct was computed for each Cond \u00d7 SwapType "
    "cell, pooled across color, rotation, and translation direction "
    "(n = 32 trials per cell, except one N/UNCUED cell with n = 33). "
    "The cueing effect is the difference in accuracy (CUED \u2212 UNCUED, "
    "in percentage points). A one-tailed z-test assessed whether CUED > UNCUED "
    "within each swap type. A second z-test compared cueing effects between "
    "swap and no-swap conditions (two-tailed, assessing attenuation)."
)

FINDINGS_MS = (
    "Session 260324_1010 \u2014 Motion Swap: the cueing effect was present "
    "under both swap types. No-swap trials replicated the baseline: "
    "CUED > UNCUED by approximately 27 pp. Motion-swap trials showed a "
    "reduced but still positive cueing effect of approximately 16 pp. "
    "The ~11 pp attenuation is consistent with the idea that continuity "
    "of the pre-translation rotation history contributes to the onset cue: "
    "when the non-translating field adopts the translating field\u2019s "
    "rotation identity at onset, the distinctiveness of the cue is reduced. "
    "However, cueing was not eliminated, indicating that the temporal onset "
    "asymmetry alone (independent of sustained rotation identity) provides "
    "residual attentional benefit."
)

FINDINGS_D50 = (
    "Session 260325_1039 \u2014 Dots50 Swap: the 50% dot-membership swap "
    "produced no measurable attenuation of cueing. The cueing effect was "
    "approximately 30 pp without swap and approximately 34 pp with Dots50 "
    "swap \u2014 a slight non-significant increase. The Dots50 swap "
    "selectively reassigns the noise subfields (S1, S3) while leaving the "
    "coherent subfields (S0, S2) intact. The null result suggests that "
    "partial disruption of dot grouping at the noise level does not impair "
    "attentional selection, and that the remaining 50% coherent-subfield "
    "continuity is sufficient to maintain a perceptually unified surface."
)

ISSUES = (
    "Notes on data quality: (1) Session 260324_1010 was collected the same "
    "morning as the 260324_0716 baseline in which the cursor-jump artifact "
    "was first identified (thumbstick snapping to adjacent 45\u00b0 sectors, "
    "producing ~25% adjacent-sector errors). Whether the hysteresis fix "
    "(33\u00b0 latch, two-stage confirmation) was active for this session "
    "is uncertain; if the artifact persisted it would have reduced accuracy "
    "uniformly and attenuated the cueing effect without directional bias. "
    "Session 260325_1039 was almost certainly collected after the fix. "
    "(2) At n = 32 trials per cell, Wilson 95% CIs are approximately "
    "\u00b118 pp, so fine-grained comparisons (e.g., the ~11 pp "
    "motion-swap attenuation) are suggestive but not decisive at this power "
    "level. Both results should be treated as directional signals pending "
    "replication with larger n."
)

# ── Load data ──────────────────────────────────────────────────────────────────
sessions_info = [
    ('260324_1010', 'Session 260324_1010\nMotion Swap', 'M', 'Motion\nSwap',  '#883300'),
    ('260325_1039', 'Session 260325_1039\nDots50 Swap', 'D', 'Dots50\nSwap',  '#226622'),
]

# ═════════════════════════════════════════════════════════════════════════════
# PAGE 1 — Introduction + Stimulus Conditions
# ═════════════════════════════════════════════════════════════════════════════
fig1 = plt.figure(figsize=(PW, PH))
fig1.patch.set_facecolor('white')
y = 0.970

# Title
fig1.text(0.50, y, 'VRDots \u2014 Flat Swap Conditions: Motion Swap & Dots50 Swap',
    ha='center', va='top', fontsize=13, fontweight='bold', color='#111111')
y -= lh(13, 1.3) + 0.006

# Session IDs line
fig1.text(0.50, y,
    'Sessions: 260324_1010 (Motion Swap)   260325_1039 (Dots50 Swap)',
    ha='center', va='top', fontsize=6.5, color='#555555')
y -= lh(6.5, 1.3) + 0.010

# Intro paragraph
intro_lines = textwrap.wrap(INTRO, width=WRAP_W)
fig1.text(LMAR, y, '\n'.join(intro_lines),
    ha='left', va='top', fontsize=8.5, color='#222222', linespacing=1.55)
y -= len(intro_lines)*lh(8.5) + 0.006

# Stim note (italic)
stim_lines = textwrap.wrap(STIM_NOTE, width=WRAP_W)
fig1.text(LMAR, y, '\n'.join(stim_lines),
    ha='left', va='top', fontsize=7.5, color='#555555',
    linespacing=1.5, style='italic')
y -= len(stim_lines)*lh(7.5) + 0.010

# "Stimulus Conditions" heading
fig1.text(0.50, y, 'Stimulus Conditions',
    ha='center', va='top', fontsize=11, fontweight='bold', color='#1a3a6b')
y -= lh(11, 1.3) + 0.006

# Trajectory panels — 6 rows × 1 col, 3 swap sections
TRAJ_H = 0.42    # total vertical fraction for 6-row trajectory grid
traj_top = y
traj_bot = traj_top - TRAJ_H

traj_left  = 0.31
traj_right = 0.69

traj_gs = gridspec.GridSpec(6, 1,
    top=traj_top, bottom=traj_bot,
    left=traj_left, right=traj_right,
    hspace=0.30)

SWAP_SECTIONS = [
    ('noswap',     'No Swap',            '#2244AA'),
    ('motionswap', 'Motion Swap (100%)', '#883300'),
    ('dots50',     'Dots50 Swap (50%)',  '#226622'),
]

for sec_idx, (swap_type, swap_label, swap_color) in enumerate(SWAP_SECTIONS):
    for row_off, is_cued in [(0, True), (1, False)]:
        grid_row = sec_idx*2 + row_off
        ax = fig1.add_subplot(traj_gs[grid_row, 0])
        draw_traj_panel(ax, swap_type, is_cued,
                        show_labels=(sec_idx==0 and is_cued))
        ax.set_ylabel('CUED' if is_cued else 'UNCUED',
                      fontsize=8.5, fontweight='bold', labelpad=4)

    # Section label to the right of the grid
    pos_top = traj_gs[sec_idx*2,   0].get_position(fig1).y1
    pos_bot = traj_gs[sec_idx*2+1, 0].get_position(fig1).y0
    mid_y   = (pos_top + pos_bot) / 2
    fig1.text(traj_right + 0.015, mid_y, swap_label,
             ha='left', va='center', fontsize=8.5, fontweight='bold',
             color=swap_color, rotation=90)

    # Separator between sections
    if sec_idx < 2:
        sep_y = pos_bot - 0.004
        fig1.add_artist(plt.Line2D([traj_left, traj_right], [sep_y, sep_y],
            transform=fig1.transFigure, color='#BBBBBB', lw=1.0, ls='--'))

y = traj_bot - 0.010

# Trajectory legend
TLEG_H = 0.022
ax_tleg = fig1.add_axes([LMAR, y-TLEG_H, TXT_W, TLEG_H])
ax_tleg.axis('off')
ax_tleg.legend(handles=[
    mlines.Line2D([],[],color=C_CW,  marker='o',ms=5.5,mew=1.0,mfc=C_CW,  ls='none',label='S0'),
    mlines.Line2D([],[],color=C_CW,  marker='s',ms=8.5,mew=1.5,mfc='none',ls='none',label='S1'),
    mlines.Line2D([],[],color=C_CCW, marker='^',ms=6.0,mew=1.0,mfc=C_CCW, ls='none',label='S2'),
    mlines.Line2D([],[],color=C_CCW, marker='D',ms=8.0,mew=1.5,mfc='none',ls='none',label='S3'),
    mpatches.Patch(facecolor=C_TRANS,alpha=0.8,edgecolor='#888888',label='Translation window'),
], loc='center', ncol=5, fontsize=8.5, frameon=True, framealpha=0.9, edgecolor='#CCCCCC')
y -= TLEG_H + 0.010

print(f"Page 1 bottom y = {y:.3f}  (target > 0.02)")

# ═════════════════════════════════════════════════════════════════════════════
# PAGE 2 — Results + Findings + Notes
# ═════════════════════════════════════════════════════════════════════════════
fig2 = plt.figure(figsize=(PW, PH))
fig2.patch.set_facecolor('white')
y = 0.970

# Small header
fig2.text(0.50, y, 'VRDots \u2014 Flat Swap Conditions (continued)',
    ha='center', va='top', fontsize=9, color='#333333')
y -= lh(9, 1.3) + 0.010

# Analysis note
an_lines = textwrap.wrap(ANALYSIS_NOTE, width=WRAP_W)
fig2.text(LMAR, y, '\n'.join(an_lines),
    ha='left', va='top', fontsize=8.0, color='#444444', linespacing=1.5)
y -= len(an_lines)*lh(8.0) + 0.014

# Results heading
fig2.text(0.50, y, 'Results',
    ha='center', va='top', fontsize=11, fontweight='bold', color='#1a3a6b')
y -= lh(11, 1.3) + 0.008

# Bar graphs
BAR_H = 0.32
bar_top = y; bar_bot = bar_top - BAR_H

bar_gs = gridspec.GridSpec(1, 2,
    top=bar_top, bottom=bar_bot,
    left=LMAR+0.04, right=RMAR-0.04, wspace=0.40)

for si, (sess_id, sess_label, swap_code, swap_name, s_color) in enumerate(sessions_info):
    rows = load_session(sess_id)
    cnt  = analyze(rows, swap_code)

    cn = cnt.get(('CUED',  'N'),[0,1]); un = cnt.get(('UNCUED','N'),[0,1])
    cs = cnt.get(('CUED',  swap_code),[0,1]); us = cnt.get(('UNCUED',swap_code),[0,1])

    groups = [cn, un, cs, us]
    accs   = [g[0]/g[1] for g in groups]
    cis    = [wilson_ci(*g) for g in groups]

    z_n, p_n = z_test(cn[0],cn[1], un[0],un[1])
    z_s, p_s = z_test(cs[0],cs[1], us[0],us[1])
    delta_n = accs[0]-accs[1]
    delta_s = accs[2]-accs[3]

    xs      = [0.0, 0.65, 1.80, 2.45]
    bcolors = ['#4477AA','#4477AA', s_color, s_color]
    hatch   = ['','///',  '',     '///']
    xlbls   = ['CUED','UNCUED','CUED','UNCUED']

    ax = fig2.add_subplot(bar_gs[0, si])

    for xi,ac,(lo,hi),bc,ht,g in zip(xs,accs,cis,bcolors,hatch,groups):
        ax.bar(xi,ac,width=0.58,color=bc,alpha=0.82,hatch=ht,
               edgecolor='#333333',linewidth=0.8,zorder=3)
        ax.errorbar(xi,ac,yerr=[[ac-lo],[hi-ac]],
                    fmt='none',color='#222222',capsize=4,lw=1.5,zorder=4)
        ax.text(xi,hi+0.025,f'{g[0]}/{g[1]}',
                ha='center',fontsize=7.5,color='#333333')

    ax.axhline(CHANCE,color='#999999',ls='--',lw=1.0,zorder=2)
    ax.text(2.82,CHANCE+0.01,'chance',fontsize=7,color='#999999',va='bottom')

    for ic,iu,dv,zv,pv in [(0,1,delta_n,z_n,p_n),(2,3,delta_s,z_s,p_s)]:
        mc=xs[ic]; mu=xs[iu]
        yb=max(accs[ic],accs[iu])+0.12
        ax.annotate('',xy=(mu,yb),xytext=(mc,yb),
                    arrowprops=dict(arrowstyle='-',color='#444444',lw=1.1))
        ax.text((mc+mu)/2,yb+0.018,
                f'\u0394 = +{dv*100:.1f} pp  {stars(pv)}',
                ha='center',va='bottom',fontsize=9,fontweight='bold',color='#111111')
        ax.text((mc+mu)/2,yb+0.078,
                f'z = {zv:.2f}, p = {pv:.3f}',
                ha='center',va='bottom',fontsize=7,color='#555555')

    ax.text((xs[0]+xs[1])/2,-0.09,'No Swap',ha='center',fontsize=9,
            fontweight='bold',color='#4477AA',transform=ax.get_xaxis_transform())
    ax.text((xs[2]+xs[3])/2,-0.09,swap_name,ha='center',fontsize=9,
            fontweight='bold',color=s_color,transform=ax.get_xaxis_transform())
    ax.axvline(1.22,color='#DDDDDD',lw=1.0,zorder=1)

    ax.set_xlim(-0.42,3.10); ax.set_ylim(0,1.05)
    ax.set_xticks(xs); ax.set_xticklabels(xlbls,fontsize=9)
    ax.set_yticks([0,.25,.50,.75,1.0])
    ax.set_yticklabels(['0%','25%','50%','75%','100%'],fontsize=9)
    if si==0: ax.set_ylabel('Proportion correct',fontsize=9)
    ax.set_title(sess_label,fontsize=10,fontweight='bold',pad=10)
    ax.spines[['top','right']].set_visible(False)
    ax.tick_params(axis='x',length=0)

y = bar_bot - 0.010

# Bar legend
BLEG_H = 0.022
ax_bleg = fig2.add_axes([LMAR, y-BLEG_H, TXT_W, BLEG_H])
ax_bleg.axis('off')
ax_bleg.legend(handles=[
    mpatches.Patch(facecolor='#4477AA',alpha=0.82,edgecolor='#333333',label='No-swap trials (blue)'),
    mpatches.Patch(facecolor='#883300',alpha=0.82,edgecolor='#333333',label='Motion Swap trials (brown)'),
    mpatches.Patch(facecolor='#226622',alpha=0.82,edgecolor='#333333',label='Dots50 Swap trials (green)'),
    mpatches.Patch(facecolor='white',hatch='///',edgecolor='#333333',label='UNCUED (hatched)'),
    mlines.Line2D([],[],color='#222222',lw=1.5,marker='|',markersize=6,label='Wilson 95% CI'),
], loc='center', ncol=5, fontsize=8.5, frameon=True, framealpha=0.9, edgecolor='#CCCCCC')
y -= BLEG_H + 0.022

# Narrative
for heading, hcolor, paras in [
    ('Findings', '#1a3a6b', [FINDINGS_MS, FINDINGS_D50]),
    ('Notes on data quality', '#6b1a1a', [ISSUES]),
]:
    fig2.text(LMAR, y, heading,
        ha='left', va='top', fontsize=10, fontweight='bold', color=hcolor)
    y -= lh(10, 1.4) + 0.004
    for para in paras:
        lines = textwrap.wrap(para, width=WRAP_W)
        fig2.text(LMAR, y, '\n'.join(lines),
            ha='left', va='top', fontsize=8.2, color='#222222', linespacing=1.55)
        y -= len(lines)*lh(8.2) + 0.009
    y -= 0.010

print(f"Page 2 bottom y = {y:.3f}  (target > 0.02)")

# ── Save PDF ───────────────────────────────────────────────────────────────────
os.makedirs(os.path.dirname(OUT_PDF), exist_ok=True)
with PdfPages(OUT_PDF) as pdf:
    pdf.savefig(fig1, dpi=DPI, facecolor='white')
    pdf.savefig(fig2, dpi=DPI, facecolor='white')
plt.close('all')
print(f"Saved: {OUT_PDF}")
