#!/usr/bin/env python3
"""
Multi-page PDF write-up: Depth Baseline (no swap).
2 pages, US Letter portrait (8.5 × 11 in, 150 DPI).

  Page 1 — Introduction + Stimulus Conditions (trajectory panels)
  Page 2 — Results: bar panels + Findings + Notes

Sessions: 260325_1831 & 260325_1914 (0.10 m), 260325_2013 (0.03 m).
Output: Agents/WriteUps/depth_baseline_writeup.pdf

Near/Far labels use TRANSLATING-FIELD depth convention:
  Near translation = translating field is in the Near plane
    CUED+DelayedFieldDepth=N  (delayed B translates, B=Near)
    UNCUED+DelayedFieldDepth=F (non-delayed A translates, A=Near)
  Far translation = translating field is in the Far plane
    CUED+DelayedFieldDepth=F
    UNCUED+DelayedFieldDepth=N
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
    "~/Projects/ObjectBasedAttention/VRDots/Agents/WriteUps/depth_baseline_writeup.pdf")

# ── Page geometry ─────────────────────────────────────────────────────────────
PW, PH = 8.5, 11    # US Letter portrait
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
NEAR=0.0; FAR=1.0; CHANCE=1/8
C_CW='#228B22'; C_CCW='#CC3333'; C_TRANS='#CCCCCC'; C_FRAME='#333333'
C_NEAR='#4488CC'; C_FAR='#CC6644'

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
    with open(os.path.join(DATA_DIR,f"vr_dots_session_{sid}.tsv"),newline='') as f:
        return list(csv.DictReader(f,delimiter='\t'))

def is_correct(td,rd):
    d=(float(rd)-float(td)+360)%360
    return (360-d if d>180 else d)<=22.5

def trans_depth(cond, dfd):
    """Translating-field depth: CUED→dfd; UNCUED→opposite."""
    if cond=='CUED': return dfd
    return 'F' if dfd=='N' else 'N'

def analyze(rows):
    """Returns {(cond, trans_depth): [k,n]}"""
    import collections
    cnt=collections.defaultdict(lambda:[0,0])
    for r in rows:
        if r.get('EndKey','') in ('timeout','skip','requeue'): continue
        td=r.get('TransDeg',''); rd=r.get('RespDeg','')
        if not td or not rd: continue
        key=(r['Cond'], trans_depth(r['Cond'], r['DelayedFieldDepth']))
        cnt[key][0]+=int(is_correct(td,rd)); cnt[key][1]+=1
    return cnt

# ── 4-subfield trajectory drawing ─────────────────────────────────────────────
_base=np.linspace(T_A+0.01,T_TOT-0.01,14)
T_MARKS=np.unique(np.sort(np.concatenate([_base,[(T_S+T_E)/2]])))
def _interp(tk,vk,tq): return np.interp(tq,tk,vk)

SF={'S0':('o',5.5,True),'S1':('s',9.0,False),'S2':('^',6.0,True),'S3':('D',8.5,False)}
SF_COLOR={'S0':C_CW,'S1':C_CW,'S2':C_CCW,'S3':C_CCW}

def _plot_sf(ax,name,tk,vk,tq):
    c=SF_COLOR[name]; mk,ms,filled=SF[name]
    mfc=c if filled else 'none'; mew=1.0 if filled else 1.6
    ax.plot(tk,vk,color=c,lw=0.8,ls='-',solid_capstyle='round',zorder=3)
    ax.plot(tq,_interp(tk,vk,tq),marker=mk,ms=ms,mew=mew,
            mfc=mfc,mec=c,ls='none',zorder=5)

def _traj_noswap(is_cued):
    t0=T_B if is_cued else T_A; t2=T_A if is_cued else T_B
    tS0=np.array([t0,T_S,T_S,T_E,T_E,T_TOT]); vS0=np.array([CW,CW,TRANS_COH,TRANS_COH,CW,CW])
    tS1=np.array([t0,T_S,T_S,T_E,T_E,T_TOT]); vS1=np.array([CW,CW,TRANS_NOI,TRANS_NOI,CW,CW])
    tS2=np.array([t2,T_TOT]); vS2=np.array([CCW,CCW])
    tS3=np.array([t2,T_TOT]); vS3=np.array([CCW,CCW])
    return tS0,vS0,tS1,vS1,tS2,vS2,tS3,vS3

def draw_motion_panel(ax, is_cued, show_labels=False):
    tS0,vS0,tS1,vS1,tS2,vS2,tS3,vS3=_traj_noswap(is_cued)
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

def draw_depth_panel(ax, cw_depth, show_near_far=False):
    """Horizontal depth lines. cw_depth='N' or 'F' — depth of the CW (green) field.
    CCW field = red solid line; CW field = green dashed line."""
    cw_y  = NEAR if cw_depth=='N' else FAR
    ccw_y = FAR  if cw_depth=='N' else NEAR
    ax.plot([T_A,T_TOT],[ccw_y,ccw_y],color=C_CCW,lw=1.8,ls='-',zorder=3)
    ax.plot([T_B,T_TOT],[cw_y, cw_y], color=C_CW, lw=1.8,ls='--',dashes=(5,3),zorder=3)
    ax.set_xlim(T_A-.01,T_TOT+.01); ax.set_ylim(-0.5,1.5)
    ax.set_xticks([]); ax.set_yticks([NEAR,FAR])
    ax.set_yticklabels(['Near','Far'],fontsize=5.8)
    ax.tick_params(axis='y',length=2,pad=1)
    ax.axvspan(T_S,T_E,color=C_TRANS,alpha=0.6,zorder=1)
    ax.axvline(T_B,color='#AAAAAA',lw=0.8,ls='--',zorder=2)
    for sp in ax.spines.values():
        sp.set_visible(True); sp.set_linewidth(0.8); sp.set_edgecolor(C_FRAME)

# ── Text ──────────────────────────────────────────────────────────────────────
INTRO=(
    "Three sessions introduced stereoscopic depth separation between the two "
    "rotating dot fields. The flat (no-depth, no-swap) design was otherwise "
    "unchanged: 750 ms delayed onset, 80 ms translation, 8-AFC direction "
    "judgment at 2.0 m, no swap. Sessions 260325_1831 and 260325_1914 used "
    "a depth separation of 0.10 m (fields at \u00b10.05 m from fixation depth), "
    "which pilot observation confirmed produced clearly visible stereo depth "
    "planes. Session 260325_2013 used 0.03 m separation, at which depth was "
    "weakly perceptible. Each session comprised 128\u2013131 trials, fully "
    "crossing Cond (CUED/UNCUED) \u00d7 DelayedFieldDepth (Near/Far) \u00d7 "
    "DelayedFieldColor (G/R) \u00d7 RotConfig (0/1) \u00d7 TransDeg (8 directions), "
    "yielding approximately 8 trials per cell."
)

STIM_NOTE=(
    "Trajectory diagrams show one representative color-rotation pairing. "
    "Columns are organized by the depth of the translating field "
    "(Near translation | Far translation) rather than by the depth of the "
    "delayed field. S0\u25cf/S1\u25a1 = initially CW field (green); "
    "S2\u25b2/S3\u25c7 = initially CCW field (red). Depth track (below each "
    "motion panel) shows which field occupies which plane; the CW/translating "
    "field is shown dashed to match its delayed onset in the CUED row."
)

ANALYSIS_NOTE=(
    "Analysis: Near/Far labels throughout use translating-field depth. "
    "CUED Near = delayed field at Near (translates Near); "
    "UNCUED Near = non-delayed field at Near (translates Near, delayed field at Far). "
    "Proportion correct was computed per Cond \u00d7 translating-depth cell, "
    "pooled across color, rotation, and translation direction "
    "(\u2248 32 trials/cell). One-tailed z-test: CUED > UNCUED within each "
    "translating depth."
)

FINDINGS_010=(
    "Sessions 260325_1831 and 260325_1914 (0.10 m depth separation): a large "
    "performance asymmetry dominated both sessions. Far translation accuracy "
    "was high (\u224875\u201379% CUED, \u224847\u201359% UNCUED), while Near "
    "translation accuracy was at or near chance (\u224812\u201339% CUED, "
    "\u224816\u201319% UNCUED). This near-chance performance for Near "
    "translation is not a cueing failure but a stimulus-legibility floor: at "
    "0.10 m separation the Near plane dots move in strong stereo depth, and "
    "their 2D translational signal is substantially masked or overridden by "
    "the large disparity change. The cueing effect (CUED > UNCUED) was "
    "significant for Far translation in both sessions (+28 pp, p=.011; "
    "+19 pp, p=.045) and significant for Near translation in session 1 "
    "(+24 pp, p=.016) but not session 2 (\u22126 pp, n.s.), where Near "
    "accuracy was too low to detect a cueing effect. Overall cueing was "
    "+26 pp (p=.002) in session 1 and +7 pp (n.s.) in session 2, reflecting "
    "the large influence of the near-chance Near cells."
)

FINDINGS_003=(
    "Session 260325_2013 (0.03 m depth separation): with barely perceptible "
    "depth, both planes produced above-chance but modest accuracy. Far "
    "translation remained easier (CUED 49%, UNCUED 25%, \u0394+24 pp, "
    "p=.025) and Near translation showed a smaller positive cueing effect "
    "(CUED 39%, UNCUED 30%, \u0394+9 pp, n.s.). The overall cueing effect "
    "was +16 pp (p=.026). The residual Far > Near performance asymmetry "
    "at 0.03 m suggests that even weak stereo depth partially disrupts "
    "the legibility of Near-plane translation, though far less severely "
    "than at 0.10 m."
)

ISSUES=(
    "Notes: (1) The 0.10 m near-chance result for Near translation is a "
    "performance floor, not a cueing null. Any cueing effect that exists is "
    "undetectable when both CUED and UNCUED are near chance. This confound "
    "motivated the subsequent DepthParam experiment (0.03\u20130.15 m range) "
    "designed to find a depth separation that preserves legibility in both "
    "planes. (2) Session-to-session variability is high at n\u224832/cell. "
    "The reversal of the Near cueing effect between sessions 1 and 2 is "
    "likely noise. (3) The DepthBothPlanes session (260326_0550) and "
    "DepthSwap session (260326_0821) were also run at 0.10 m but are not "
    "included here as they introduce additional factors (swaps, "
    "joint-onset conditions) treated in later write-ups."
)

# ── Load data ──────────────────────────────────────────────────────────────────
SESSIONS=[
    ('260325_1831','260325_1831\n0.10 m  (session 1)','#1a3a6b'),
    ('260325_1914','260325_1914\n0.10 m  (session 2)','#1a3a6b'),
    ('260325_2013','260325_2013\n0.03 m','#4a1a6b'),
]

print("Loading sessions...")
session_data = {}
for sid,_,_ in SESSIONS:
    session_data[sid] = analyze(load(sid))

# ═════════════════════════════════════════════════════════════════════════════
# PAGE 1 — Introduction + Stimulus Conditions
# ═════════════════════════════════════════════════════════════════════════════
fig1 = plt.figure(figsize=(PW,PH)); fig1.patch.set_facecolor('white')
y = 0.970

# Title
fig1.text(0.50,y,'VRDots \u2014 Depth Baseline (No Swap)',
    ha='center',va='top',fontsize=13,fontweight='bold',color='#111111')
y -= lh(13,1.3)+0.006

# Session IDs line
fig1.text(0.50,y,
    'Sessions: 260325_1831, 260325_1914 (0.10 m)   260325_2013 (0.03 m)',
    ha='center',va='top',fontsize=6.5,color='#555555')
y -= lh(6.5,1.3)+0.010

# Intro paragraphs
for txt,fs,col,sty in [
    (INTRO,    8.5,'#222222','normal'),
    (STIM_NOTE,7.5,'#555555','italic'),
]:
    lns=textwrap.wrap(txt,width=WRAP_W)
    fig1.text(LMAR,y,'\n'.join(lns),ha='left',va='top',fontsize=fs,
              color=col,linespacing=1.5,style=sty)
    y -= len(lns)*lh(fs)+0.008

y -= 0.005

# "Stimulus Conditions" heading
fig1.text(0.50,y,'Stimulus Conditions',
    ha='center',va='top',fontsize=11,fontweight='bold',color='#1a3a6b')
y -= lh(11,1.3)+0.006

# Trajectory grid: GridSpec(4,2), height_ratios=[3,1,3,1]
TRAJ_H = 0.36
traj_top = y; traj_bot = traj_top - TRAJ_H

traj_gs = gridspec.GridSpec(4,2,
    top=traj_top, bottom=traj_bot,
    left=0.115, right=0.865,
    height_ratios=[3,1,3,1],
    hspace=0.10, wspace=0.25)

COL_TITLES=['Near Translation','Far Translation']
CW_DEPTHS=['N','F']

for col,(ctitle,cw_dep) in enumerate(zip(COL_TITLES,CW_DEPTHS)):
    # CUED motion (row 0)
    ax_cm=fig1.add_subplot(traj_gs[0,col])
    draw_motion_panel(ax_cm,is_cued=True,show_labels=(col==0))
    ax_cm.set_title(ctitle,fontsize=9.5,fontweight='bold',pad=4)
    if col==0: ax_cm.set_ylabel('CUED',fontsize=9,fontweight='bold',labelpad=4)

    # CUED depth (row 1)
    ax_cd=fig1.add_subplot(traj_gs[1,col])
    draw_depth_panel(ax_cd,cw_depth=cw_dep)
    if col==0: ax_cd.set_ylabel('Depth',fontsize=7,labelpad=4,color='#555555')

    # UNCUED motion (row 2)
    ax_um=fig1.add_subplot(traj_gs[2,col])
    draw_motion_panel(ax_um,is_cued=False)
    if col==0: ax_um.set_ylabel('UNCUED',fontsize=9,fontweight='bold',labelpad=4)

    # UNCUED depth (row 3)
    ax_ud=fig1.add_subplot(traj_gs[3,col])
    draw_depth_panel(ax_ud,cw_depth=cw_dep)
    if col==0: ax_ud.set_ylabel('Depth',fontsize=7,labelpad=4,color='#555555')

y = traj_bot - 0.010

# Trajectory legend
TLEG_H = 0.030
ax_tleg=fig1.add_axes([LMAR,y-TLEG_H,TXT_W,TLEG_H]); ax_tleg.axis('off')
ax_tleg.legend(handles=[
    mlines.Line2D([],[],color=C_CW, marker='o',ms=5.5,mew=1.0,mfc=C_CW,  ls='none',label='S0'),
    mlines.Line2D([],[],color=C_CW, marker='s',ms=8.5,mew=1.5,mfc='none',ls='none',label='S1'),
    mlines.Line2D([],[],color=C_CCW,marker='^',ms=6.0,mew=1.0,mfc=C_CCW, ls='none',label='S2'),
    mlines.Line2D([],[],color=C_CCW,marker='D',ms=8.0,mew=1.5,mfc='none',ls='none',label='S3'),
    mpatches.Patch(facecolor=C_TRANS,alpha=0.8,edgecolor='#888888',label='Translation window'),
    mlines.Line2D([],[],color='#AAAAAA',lw=1.2,ls='--',label='Delayed field onset'),
],loc='center',ncol=6,fontsize=8,frameon=True,framealpha=0.9,edgecolor='#CCCCCC')
y -= TLEG_H + 0.012

# Analysis note
an_lns=textwrap.wrap(ANALYSIS_NOTE,width=WRAP_W)
fig1.text(LMAR,y,'\n'.join(an_lns),ha='left',va='top',fontsize=8.0,
         color='#444444',linespacing=1.5)
y -= len(an_lns)*lh(8.0)+0.010

print(f"Page 1 bottom y = {y:.3f}")

# ═════════════════════════════════════════════════════════════════════════════
# PAGE 2 — Results: bar panels + Findings + Notes
# ═════════════════════════════════════════════════════════════════════════════
fig2 = plt.figure(figsize=(PW,PH)); fig2.patch.set_facecolor('white')
y = 0.970

# Small header
fig2.text(0.50,y,'VRDots \u2014 Depth Baseline (continued)',
    ha='center',va='top',fontsize=9,color='#555555')
y -= lh(9,1.3)+0.008

# "Results" heading
fig2.text(0.50,y,'Results',
    ha='center',va='top',fontsize=11,fontweight='bold',color='#1a3a6b')
y -= lh(11,1.3)+0.010

# Bar panels: GridSpec(1,3)
BAR_H = 0.30
bar_top=y; bar_bot=bar_top-BAR_H

bar_gs=gridspec.GridSpec(1,3,
    top=bar_top, bottom=bar_bot,
    left=LMAR+0.02, right=RMAR-0.02, wspace=0.38)

for si,(sid,slabel,scol) in enumerate(SESSIONS):
    cnt=session_data[sid]
    cn=cnt[('CUED','N')];   un=cnt[('UNCUED','N')]
    cf=cnt[('CUED','F')];   uf=cnt[('UNCUED','F')]
    groups=[cn,un,cf,uf]
    accs=[g[0]/g[1] for g in groups]
    cis=[wilson_ci(*g) for g in groups]
    zn,pn=z_test(cn[0],cn[1],un[0],un[1])
    zf,pf=z_test(cf[0],cf[1],uf[0],uf[1])
    dn=(accs[0]-accs[1])*100; df=(accs[2]-accs[3])*100

    xs=[0.0,0.65,1.80,2.45]
    bcolors=[C_NEAR,C_NEAR,C_FAR,C_FAR]
    hatch=['','///','','///']
    xlbls=['CUED','UNCUED','CUED','UNCUED']

    ax=fig2.add_subplot(bar_gs[0,si])
    for xi,ac,(lo,hi),bc,ht,g in zip(xs,accs,cis,bcolors,hatch,groups):
        ax.bar(xi,ac,width=0.58,color=bc,alpha=0.82,hatch=ht,
               edgecolor='#333333',linewidth=0.8,zorder=3)
        ax.errorbar(xi,ac,yerr=[[ac-lo],[hi-ac]],
                    fmt='none',color='#222222',capsize=4,lw=1.5,zorder=4)
        ax.text(xi,hi+0.025,f'{g[0]}/{g[1]}',ha='center',fontsize=7,color='#333333')

    ax.axhline(CHANCE,color='#999999',ls='--',lw=1.0,zorder=2)
    ax.text(2.82,CHANCE+0.01,'chance',fontsize=7,color='#999999',va='bottom')

    for ic,iu,dv,zv,pv in [(0,1,dn,zn,pn),(2,3,df,zf,pf)]:
        mc=xs[ic]; mu=xs[iu]
        yb=max(accs[ic],accs[iu])+0.11
        ax.annotate('',xy=(mu,yb),xytext=(mc,yb),
                    arrowprops=dict(arrowstyle='-',color='#444444',lw=1.1))
        sign='+' if dv>=0 else ''
        ax.text((mc+mu)/2,yb+0.017,f'\u0394={sign}{dv:.1f}pp {stars(pv)}',
                ha='center',va='bottom',fontsize=8.5,fontweight='bold',color='#111111')
        ax.text((mc+mu)/2,yb+0.072,f'z={zv:.2f}, p={pv:.3f}',
                ha='center',va='bottom',fontsize=6.5,color='#555555')

    ax.text((xs[0]+xs[1])/2,-0.09,'Near\nTrans.',ha='center',fontsize=8.5,
            fontweight='bold',color=C_NEAR,transform=ax.get_xaxis_transform())
    ax.text((xs[2]+xs[3])/2,-0.09,'Far\nTrans.',ha='center',fontsize=8.5,
            fontweight='bold',color=C_FAR,transform=ax.get_xaxis_transform())
    ax.axvline(1.22,color='#DDDDDD',lw=1.0,zorder=1)
    ax.set_xlim(-0.42,3.10); ax.set_ylim(0,1.05)
    ax.set_xticks(xs); ax.set_xticklabels(xlbls,fontsize=8.5)
    ax.set_yticks([0,.25,.50,.75,1.0])
    ax.set_yticklabels(['0%','25%','50%','75%','100%'],fontsize=8.5)
    if si==0: ax.set_ylabel('Proportion correct',fontsize=9)
    ax.set_title(slabel,fontsize=9.5,fontweight='bold',pad=10,color=scol)
    ax.spines[['top','right']].set_visible(False)
    ax.tick_params(axis='x',length=0)

y = bar_bot - 0.010

# Bar legend
BLEG_H = 0.028
ax_bleg=fig2.add_axes([LMAR,y-BLEG_H,TXT_W,BLEG_H]); ax_bleg.axis('off')
ax_bleg.legend(handles=[
    mpatches.Patch(facecolor=C_NEAR,alpha=0.82,edgecolor='#333333',label='Near translation (blue)'),
    mpatches.Patch(facecolor=C_FAR, alpha=0.82,edgecolor='#333333',label='Far translation (orange)'),
    mpatches.Patch(facecolor='white',hatch='///',edgecolor='#333333',label='UNCUED (hatched)'),
    mlines.Line2D([],[],color='#222222',lw=1.5,marker='|',markersize=6,label='Wilson 95% CI'),
],loc='center',ncol=4,fontsize=8.5,frameon=True,framealpha=0.9,edgecolor='#CCCCCC')
y -= BLEG_H + 0.022

# Narrative text
for heading,hcolor,paras in [
    ('Findings','#1a3a6b',[FINDINGS_010,FINDINGS_003]),
    ('Notes','#6b1a1a',[ISSUES]),
]:
    fig2.text(LMAR,y,heading,
        ha='left',va='top',fontsize=10,fontweight='bold',color=hcolor)
    y -= lh(10,1.4)+0.004
    for para in paras:
        lns=textwrap.wrap(para,width=WRAP_W)
        fig2.text(LMAR,y,'\n'.join(lns),
            ha='left',va='top',fontsize=8.2,color='#222222',linespacing=1.55)
        y -= len(lns)*lh(8.2)+0.009
    y -= 0.010

print(f"Page 2 bottom y = {y:.3f}")

# ── Save PDF ──────────────────────────────────────────────────────────────────
with PdfPages(OUT_PDF) as pdf:
    for fig in (fig1,fig2):
        pdf.savefig(fig,dpi=DPI,bbox_inches='tight')
        plt.close(fig)

print(f"Saved: {OUT_PDF}")
