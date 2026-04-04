#!/usr/bin/env python3
"""
Multi-page PDF write-up: DepthParam (parametric depth separation, no swap).
Sessions (all 260402, R/G balanced, no swap, n=128 each):
  260402_0716 — DepthParam_003m (0.03 m)
  260402_0757 — DepthParam_005m (0.05 m)
  260402_0624 — DepthParam_010m (0.10 m)
  260402_0656 — DepthParam_015m (0.15 m)

2 pages, US Letter portrait (8.5 × 11 in, 150 DPI).
  Page 1 — Introduction + Stimulus Conditions (4-subfield motion + depth tracks)
  Page 2 — Results (4 bar panels) + Findings + Notes

Depth tracks use the same S0/S1/S2/S3 marker convention as motion tracks.
Near/Far: translating-field-depth convention throughout.

Output: Agents/WriteUps/depthparam_writeup.pdf
"""

import csv, collections, math, os, textwrap
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
OUT_PDF  = os.path.expanduser(
    "~/Projects/ObjectBasedAttention/VRDots/Agents/WriteUps/depthparam_writeup.pdf")

SESSIONS = [
    ('260402_0716', '0.03 m', 'DepthParam_003m'),
    ('260402_0757', '0.05 m', 'DepthParam_005m'),
    ('260402_0624', '0.10 m', 'DepthParam_010m'),
    ('260402_0656', '0.15 m', 'DepthParam_015m'),
]

# ── Page geometry ──────────────────────────────────────────────────────────────
PW, PH = 8.5, 11
DPI     = 150
LMAR, RMAR = 0.09, 0.91
TXT_W = RMAR - LMAR
WRAP_W = 115

def lh(pt, spacing=1.55):
    return (pt / 72 * DPI * spacing) / (PH * DPI)

# ── Timing / colours ──────────────────────────────────────────────────────────
T_A=0.00; T_B=0.490; T_S=0.686; T_E=0.739; T_TOT=1.00
CW=2.0; TRANS_COH=1.0; TRANS_NOI=1.5; CCW=0.0
NEAR_Y=0.0; FAR_Y=1.0
CHANCE=1/8
C_CW='#228B22'; C_CCW='#CC3333'; C_TRANS='#CCCCCC'; C_FRAME='#333333'
C_NEAR='#4488CC'; C_FAR='#CC6644'

DEPTH_COLORS = {
    '0.03 m': '#BB4488',
    '0.05 m': '#4466BB',
    '0.10 m': '#117744',
    '0.15 m': '#BB6622',
}

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

# ── Data ──────────────────────────────────────────────────────────────────────
def load(sid):
    with open(os.path.join(DATA_DIR,f"vr_dots_session_{sid}.tsv"),newline='') as f:
        return list(csv.DictReader(f,delimiter='\t'))

def is_correct(td,rd):
    d=(float(rd)-float(td)+360)%360; return (360-d if d>180 else d)<=22.5

def trans_depth(cond,dfd):
    return dfd if cond=='CUED' else ('F' if dfd=='N' else 'N')

def analyze(sid):
    cnt=collections.defaultdict(lambda:[0,0])
    for r in load(sid):
        if r.get('EndKey','') in ('timeout','skip','requeue'): continue
        td=r.get('TransDeg',''); rd=r.get('RespDeg','')
        if not td or not rd: continue
        key=(r['Cond'], trans_depth(r['Cond'],r.get('DelayedFieldDepth','N')))
        cnt[key][0]+=int(is_correct(td,rd)); cnt[key][1]+=1
    return cnt

# ── 4-subfield trajectory drawing ─────────────────────────────────────────────
_base   = np.linspace(T_A+0.01, T_TOT-0.01, 14)
T_MARKS = np.unique(np.sort(np.concatenate([_base, [(T_S+T_E)/2]])))

# S0 = CW coherent  (small filled circle,   green)
# S1 = CW noise     (large open square,      green)
# S2 = CCW coherent (small filled triangle,  red)
# S3 = CCW noise    (large open diamond,     red)
SF = {
    'S0': ('o', 5.5, True,  C_CW),
    'S1': ('s', 9.0, False, C_CW),
    'S2': ('^', 6.0, True,  C_CCW),
    'S3': ('D', 8.5, False, C_CCW),
}

def _plot_sf(ax, name, tk, vk, tq):
    mk, ms, filled, c = SF[name]
    mfc = c if filled else 'none'; mew = 1.0 if filled else 1.6
    ax.plot(tk, vk, color=c, lw=0.8, ls='-', solid_capstyle='round', zorder=3)
    ax.plot(tq, np.interp(tq,tk,vk), marker=mk, ms=ms, mew=mew,
            mfc=mfc, mec=c, ls='none', zorder=5)

def draw_motion(ax, is_cued, show_labels=False):
    """4-subfield motion trajectory (no-swap: CW field translates in both CUED/UNCUED)."""
    t0 = T_B if is_cued else T_A   # CW field (S0/S1) onset
    t2 = T_A if is_cued else T_B   # CCW field (S2/S3) onset
    m0 = T_MARKS[T_MARKS >= t0]
    m2 = T_MARKS[T_MARKS >= t2]

    tS0=np.array([t0,T_S,T_S,T_E,T_E,T_TOT]); vS0=np.array([CW,CW,TRANS_COH,TRANS_COH,CW,CW])
    tS1=np.array([t0,T_S,T_S,T_E,T_E,T_TOT]); vS1=np.array([CW,CW,TRANS_NOI,TRANS_NOI,CW,CW])
    tS2=np.array([t2,T_TOT]);                  vS2=np.array([CCW,CCW])
    tS3=np.array([t2,T_TOT]);                  vS3=np.array([CCW,CCW])

    _plot_sf(ax,'S0',tS0,vS0,m0); _plot_sf(ax,'S1',tS1,vS1,m0)
    _plot_sf(ax,'S2',tS2,vS2,m2); _plot_sf(ax,'S3',tS3,vS3,m2)

    ax.set_xlim(T_A-.01,T_TOT+.01); ax.set_ylim(-.35,2.55)
    ax.set_xticks([]); ax.set_yticks([CCW,TRANS_COH,TRANS_NOI,CW])
    ax.set_yticklabels(['CCW','Trans\n(coh)','Trans\n(noise)','CW'], fontsize=5.5)
    ax.tick_params(axis='y', length=2, pad=1)
    ax.axvspan(T_S,T_E, color=C_TRANS, alpha=0.6, zorder=1)
    ax.axvline(T_B, color='#AAAAAA', lw=0.8, ls='--', zorder=2)
    for sp in ax.spines.values():
        sp.set_visible(True); sp.set_linewidth(0.8); sp.set_edgecolor(C_FRAME)
    if show_labels:
        for x,lbl in [((T_A+T_B)/2,'A only'),((T_B+T_S)/2,'A+B'),((T_S+T_E)/2,'T')]:
            ax.text(x,2.48,lbl,ha='center',va='top',fontsize=5,
                    color='#888888',style='italic')

def draw_depth(ax, is_cued, cw_depth_label, show_ylabel=False):
    """
    4-subfield depth track using the same S0/S1/S2/S3 marker convention.
    cw_depth_label: 'N' or 'F' — depth of the translating (CW) field.
    No swap: all subfields remain at their assigned depth throughout.
    S0/S1 (CW field) at cw_depth; S2/S3 (CCW field) at ccw_depth.
    When superimposed at the same level the open symbol frames the filled one.
    """
    cw_y  = NEAR_Y if cw_depth_label=='N' else FAR_Y
    ccw_y = FAR_Y  if cw_depth_label=='N' else NEAR_Y
    t_cw  = T_B if is_cued else T_A
    t_ccw = T_A if is_cued else T_B

    for name, y_level, t_onset in [
        ('S0', cw_y,  t_cw),
        ('S1', cw_y,  t_cw),
        ('S2', ccw_y, t_ccw),
        ('S3', ccw_y, t_ccw),
    ]:
        mk, ms, filled, c = SF[name]
        mfc = c if filled else 'none'; mew = 1.0 if filled else 1.6
        tq = T_MARKS[T_MARKS >= t_onset]
        # horizontal line
        ax.plot([t_onset,T_TOT],[y_level,y_level],
                color=c, lw=0.8, ls='-', zorder=3)
        # markers
        ax.plot(tq, [y_level]*len(tq),
                marker=mk, ms=ms, mew=mew,
                mfc=mfc, mec=c, ls='none', zorder=5)

    ax.set_xlim(T_A-.01,T_TOT+.01); ax.set_ylim(-0.5,1.5)
    ax.set_xticks([]); ax.set_yticks([NEAR_Y,FAR_Y])
    ax.set_yticklabels(['Near','Far'], fontsize=5.5)
    ax.tick_params(axis='y', length=2, pad=1)
    ax.axvspan(T_S,T_E, color=C_TRANS, alpha=0.6, zorder=1)
    ax.axvline(T_B, color='#AAAAAA', lw=0.8, ls='--', zorder=2)
    for sp in ax.spines.values():
        sp.set_visible(True); sp.set_linewidth(0.8); sp.set_edgecolor(C_FRAME)
    if show_ylabel:
        ax.set_ylabel('Depth', fontsize=6, labelpad=3, color='#555555')

# ── Bar-panel helper ───────────────────────────────────────────────────────────
def draw_bars(ax, cnt, depth_label, show_ylabel=False, show_chance_label=False):
    cn=cnt[('CUED','N')];   un=cnt[('UNCUED','N')]
    cf=cnt[('CUED','F')];   uf=cnt[('UNCUED','F')]
    groups=[cn,un,cf,uf]
    accs=[g[0]/max(g[1],1) for g in groups]
    cis =[wilson_ci(*g) if g[1]>0 else (0,0) for g in groups]
    zn,pn=z_test(cn[0],cn[1],un[0],un[1])
    zf,pf=z_test(cf[0],cf[1],uf[0],uf[1])
    dn=(accs[0]-accs[1])*100; df=(accs[2]-accs[3])*100

    xs=[0.0,0.70,2.00,2.70]
    bcolors=[C_NEAR,C_NEAR,C_FAR,C_FAR]; hatch=['','///','','///']
    xlbls=['CUED','UNCUED','CUED','UNCUED']

    for xi,ac,(lo,hi),bc,ht,g in zip(xs,accs,cis,bcolors,hatch,groups):
        ax.bar(xi,ac,width=0.62,color=bc,alpha=0.82,hatch=ht,
               edgecolor='#333333',linewidth=0.8,zorder=3)
        if g[1]>0:
            ax.errorbar(xi,ac,yerr=[[ac-lo],[hi-ac]],
                        fmt='none',color='#222222',capsize=4,lw=1.5,zorder=4)
            ax.text(xi,hi+0.022,f'{g[0]}/{g[1]}',ha='center',fontsize=6.5,color='#333333')

    ax.axhline(CHANCE,color='#999999',ls='--',lw=0.9,zorder=2)
    if show_chance_label:
        ax.text(3.08,CHANCE+0.010,'chance',fontsize=6.5,color='#999999',va='bottom')

    for ic,iu,dv,zv,pv in [(0,1,dn,zn,pn),(2,3,df,zf,pf)]:
        mc=xs[ic]; mu=xs[iu]
        yb=max(accs[ic],accs[iu])+0.09
        ax.annotate('',xy=(mu,yb),xytext=(mc,yb),
                    arrowprops=dict(arrowstyle='-',color='#444444',lw=1.1))
        sign='+' if dv>=0 else ''
        ax.text((mc+mu)/2,yb+0.012,f'\u0394={sign}{dv:.1f}pp {stars(pv)}',
                ha='center',va='bottom',fontsize=8,fontweight='bold',color='#111111')
        ax.text((mc+mu)/2,yb+0.060,f'z={zv:.2f}, p={pv:.3f}',
                ha='center',va='bottom',fontsize=6.5,color='#555555')

    ax.text((xs[0]+xs[1])/2,-0.095,'Near\nTrans.',ha='center',fontsize=9,
            fontweight='bold',color=C_NEAR,transform=ax.get_xaxis_transform())
    ax.text((xs[2]+xs[3])/2,-0.095,'Far\nTrans.',ha='center',fontsize=9,
            fontweight='bold',color=C_FAR,transform=ax.get_xaxis_transform())
    ax.axvline(1.35,color='#DDDDDD',lw=1.0,zorder=1)
    ax.set_xlim(-0.48,3.20); ax.set_ylim(0,1.05)
    ax.set_xticks(xs); ax.set_xticklabels(xlbls,fontsize=9)
    ax.set_yticks([0,.25,.50,.75,1.0])
    ax.set_yticklabels(['0%','25%','50%','75%','100%'],fontsize=9)
    if show_ylabel: ax.set_ylabel('Proportion correct',fontsize=9.5)
    ax.set_title(depth_label,fontsize=11,fontweight='bold',pad=10,
                 color=DEPTH_COLORS.get(depth_label,'#333333'))
    ax.spines[['top','right']].set_visible(False)
    ax.tick_params(axis='x',length=0)

# ── Shared legend handles ──────────────────────────────────────────────────────
TRAJ_LEG = [
    mlines.Line2D([],[],color=C_CW, marker='o',ms=5.5,mew=1.0,mfc=C_CW,  ls='none',label='S0 (CW coh)'),
    mlines.Line2D([],[],color=C_CW, marker='s',ms=8.5,mew=1.5,mfc='none',ls='none',label='S1 (CW noise)'),
    mlines.Line2D([],[],color=C_CCW,marker='^',ms=6.0,mew=1.0,mfc=C_CCW, ls='none',label='S2 (CCW coh)'),
    mlines.Line2D([],[],color=C_CCW,marker='D',ms=8.0,mew=1.5,mfc='none',ls='none',label='S3 (CCW noise)'),
    mpatches.Patch(facecolor=C_TRANS,alpha=0.8,edgecolor='#888',label='Translation window'),
    mlines.Line2D([],[],color='#AAAAAA',lw=1.2,ls='--',label='Delayed field onset'),
]
BAR_LEG = [
    mpatches.Patch(facecolor=C_NEAR,alpha=0.82,edgecolor='#333',label='Near translation'),
    mpatches.Patch(facecolor=C_FAR, alpha=0.82,edgecolor='#333',label='Far translation'),
    mpatches.Patch(facecolor='white',hatch='///',edgecolor='#333',label='UNCUED (hatched)'),
    mlines.Line2D([],[],color='#222',lw=1.5,marker='|',markersize=6,label='Wilson 95% CI'),
]

# ── Text ──────────────────────────────────────────────────────────────────────
INTRO = (
    "The DepthParam experiment measured dot cueing across four depth separations "
    "(0.03, 0.05, 0.10, 0.15 m) to characterize the Near/Far asymmetry as a "
    "function of stereoscopic depth magnitude. Unlike DepthSwapCtrl, no depth "
    "swaps were applied (SwapType = N only). Fields were two-color and "
    "rotation-balanced (DelayedFieldColor R/G, RotCfg 0/1 crossed), yielding "
    "128 trials per session, approximately 32 trials per Cond \u00d7 "
    "DelayedFieldDepth cell. All four sessions were collected in a single "
    "morning (260402). Depth separation is measured as the full distance "
    "between the two planes (each field is \u00b1half the separation from "
    "the fixation depth at 2.0 m)."
)
STIM_NOTE = (
    "Trajectory diagrams show one representative pairing: S0\u25cf/S1\u25a1 = "
    "initially CW field (green); S2\u25b2/S3\u25c7 = initially CCW field (red). "
    "Columns: Near translation (translating field at Near) | "
    "Far translation (translating field at Far). "
    "Motion tracks (upper) and depth tracks (lower) both use the 4-subfield "
    "marker convention. In the depth track, S0/S1 and S2/S3 share the same "
    "depth level so their symbols are superimposed \u2014 the open larger "
    "symbol (S1\u25a1 or S3\u25c7) frames the filled smaller one (S0\u25cf or S2\u25b2)."
)
ANALYSIS_NOTE = (
    "Analysis: Near/Far labels use the translating-field-depth convention. "
    "CUED Near = delayed field at Near, translating Near. "
    "UNCUED Near = non-delayed field at Near, translating Near (delayed field at Far). "
    "Proportion correct pooled across color, rotation, and direction "
    "(\u224832 trials/cell per session). One-tailed z-test: CUED > UNCUED."
)
FINDINGS = (
    "Overall cueing was present in all four sessions (range +12.5 to +25.0 pp). "
    "The 0.03 m session showed the strongest overall effect (+25.0 pp, p=.002), "
    "with significant Far cueing (+34.4 pp, p=.003) and marginal Near cueing "
    "(+15.6 pp, p=.094). At 0.05 m: overall +18.8 pp (p=.022), with Near "
    "(+18.8 pp, p=.025) and Far (+18.8 pp, p=.067) both contributing. "
    "At 0.10 m: overall +12.5 pp (p=.063), with Near CUED performance near "
    "floor (18.8%) making Near cueing undetectable (+6.2 pp, n.s.) while Far "
    "cueing was marginal (+18.8 pp, p=.063). At 0.15 m: overall +18.8 pp "
    "(p=.017), with Near cueing significant (+18.8 pp, p=.025) and Far "
    "marginal (+18.8 pp, p=.067). The Near/Far accuracy asymmetry "
    "(Near task harder) is visible at all depths but is most severe at 0.10 m "
    "where Near CUED drops to 18.8% (near chance). The pattern across depths "
    "is not monotonic: 0.03 m produces the highest Far cueing (+34.4 pp) "
    "despite having the smallest disparity, suggesting that very large "
    "depth separations may degrade Near-plane legibility without proportionally "
    "increasing Far-plane cueing."
)
NOTES = (
    "Notes: (1) n=32/cell is low; all effects should be interpreted cautiously. "
    "Second sessions are planned at each depth. "
    "(2) Unlike DepthSwapCtrl, these sessions are two-color (R/G balanced), "
    "making direct magnitude comparisons with DepthSwapCtrl confounded by "
    "color-axis differences. (3) The 0.05 m DepthParam session "
    "(260402_0757) provides a same-depth/different-color comparison with "
    "DepthSwapCtrl (also 0.05 m). DepthParam 0.05 m overall cueing: "
    "+18.8 pp* vs. DepthSwapCtrl bino: +12.5 pp***, consistent with "
    "two-color stimuli yielding stronger cueing than same-color. "
    "(4) Three aborted sessions (260402_0549, 0610, 0618) preceded the "
    "complete sessions and are excluded."
)

# ── Load data ──────────────────────────────────────────────────────────────────
print("Loading DepthParam sessions...")
all_cnt = {}
for sid, depth_label, _ in SESSIONS:
    all_cnt[depth_label] = analyze(sid)
    print(f"  {sid} ({depth_label}): loaded")

# ═════════════════════════════════════════════════════════════════════════════
# PAGE 1 — Introduction + Stimulus Conditions
# ═════════════════════════════════════════════════════════════════════════════
fig1 = plt.figure(figsize=(PW,PH)); fig1.patch.set_facecolor('white')
y = 0.970

# Title + session line
fig1.text(0.50,y,'VRDots \u2014 DepthParam (Parametric Depth, No Swap)',
          ha='center',va='top',fontsize=13,fontweight='bold',color='#111111')
y -= lh(13,1.3)+0.007
fig1.text(0.50,y,
    '260402_0716 (0.03 m)  \u2022  260402_0757 (0.05 m)  \u2022  '
    '260402_0624 (0.10 m)  \u2022  260402_0656 (0.15 m)  '
    '\u2014  R/G balanced, no swap, n=128/session',
    ha='center',va='top',fontsize=6.5,color='#555555')
y -= lh(6.5,1.3)+0.010

# Intro + stim note
for txt,fs,col,sty in [(INTRO,8.5,'#111111','normal'),(STIM_NOTE,7.5,'#555555','italic')]:
    lns=textwrap.wrap(txt,width=WRAP_W)
    fig1.text(LMAR,y,'\n'.join(lns),ha='left',va='top',fontsize=fs,
              color=col,linespacing=1.5,style=sty)
    y -= len(lns)*lh(fs)+0.008

y -= 0.005
fig1.text(0.50,y,'Stimulus Conditions',ha='center',va='top',
          fontsize=11,fontweight='bold',color='#1a3a6b')
y -= lh(11,1.3)+0.006

# Trajectory grid: 4 rows × 2 cols
# Rows: CUED-motion, CUED-depth, UNCUED-motion, UNCUED-depth
# Cols: Near translation, Far translation
TRAJ_BOT = 0.066
TRAJ_H   = y - TRAJ_BOT - 0.032   # leave room for legend
traj_top = y; traj_bot = y - TRAJ_H

traj_gs = gridspec.GridSpec(4,2,
    top=traj_top,bottom=traj_bot,
    left=0.115,right=0.870,
    height_ratios=[3,1,3,1],
    hspace=0.08,wspace=0.28)

COL_TITLES = ['Near Translation','Far Translation']
CW_DEPTHS  = ['N','F']

for ci,(ctitle,cw_dep) in enumerate(zip(COL_TITLES,CW_DEPTHS)):
    # CUED motion
    ax_cm = fig1.add_subplot(traj_gs[0,ci])
    draw_motion(ax_cm,is_cued=True,show_labels=(ci==0))
    ax_cm.set_title(ctitle,fontsize=9,fontweight='bold',pad=4)
    if ci==0: ax_cm.set_ylabel('CUED',fontsize=8,fontweight='bold',labelpad=4)

    # CUED depth
    ax_cd = fig1.add_subplot(traj_gs[1,ci])
    draw_depth(ax_cd,is_cued=True,cw_depth_label=cw_dep,show_ylabel=(ci==0))

    # UNCUED motion
    ax_um = fig1.add_subplot(traj_gs[2,ci])
    draw_motion(ax_um,is_cued=False)
    if ci==0: ax_um.set_ylabel('UNCUED',fontsize=8,fontweight='bold',labelpad=4)

    # UNCUED depth
    ax_ud = fig1.add_subplot(traj_gs[3,ci])
    draw_depth(ax_ud,is_cued=False,cw_depth_label=cw_dep,show_ylabel=(ci==0))

# Trajectory legend
ax_tl=fig1.add_axes([LMAR,TRAJ_BOT-0.010,TXT_W,0.030]); ax_tl.axis('off')
ax_tl.legend(handles=TRAJ_LEG,loc='center',ncol=6,fontsize=7.5,
             frameon=True,framealpha=0.9,edgecolor='#CCC')

# ═════════════════════════════════════════════════════════════════════════════
# PAGE 2 — Results
# ═════════════════════════════════════════════════════════════════════════════
fig2 = plt.figure(figsize=(PW,PH)); fig2.patch.set_facecolor('white')
y = 0.970

fig2.text(0.50,y,'VRDots \u2014 DepthParam: Results',
          ha='center',va='top',fontsize=13,fontweight='bold',color='#111111')
y -= lh(13,1.3)+0.010

# Analysis note
an_lns=textwrap.wrap(ANALYSIS_NOTE,width=WRAP_W)
fig2.text(LMAR,y,'\n'.join(an_lns),ha='left',va='top',fontsize=8,
          color='#444',linespacing=1.5)
y -= len(an_lns)*lh(8)+0.015

fig2.text(0.50,y,'Results',ha='center',va='top',
          fontsize=11,fontweight='bold',color='#1a3a6b')
y -= lh(11,1.3)+0.010

# Bar grid: 1×4 (all four depths in a single row)
BAR_H = 0.380
bar_gs=gridspec.GridSpec(1,4,top=y,bottom=y-BAR_H,
                         left=LMAR+0.01,right=RMAR,wspace=0.28)
for ci,(sid,depth_label,_) in enumerate(SESSIONS):
    ax=fig2.add_subplot(bar_gs[0,ci])
    draw_bars(ax,all_cnt[depth_label],depth_label,
              show_ylabel=(ci==0),
              show_chance_label=(ci==3))
y -= BAR_H+0.010

# Bar legend
ax_bl=fig2.add_axes([LMAR,y-0.028,TXT_W,0.028]); ax_bl.axis('off')
ax_bl.legend(handles=BAR_LEG,loc='center',ncol=4,fontsize=8.5,
             frameon=True,framealpha=0.9,edgecolor='#CCC')
y -= 0.028+0.018

# Findings
fig2.text(LMAR,y,'Findings',ha='left',va='top',fontsize=10,
          fontweight='bold',color='#1a3a6b')
y -= lh(10,1.4)+0.005
f_lns=textwrap.wrap(FINDINGS,width=WRAP_W)
fig2.text(LMAR,y,'\n'.join(f_lns),ha='left',va='top',fontsize=8.2,
          color='#222',linespacing=1.5)
y -= len(f_lns)*lh(8.2)+0.015

# Notes
fig2.text(LMAR,y,'Notes',ha='left',va='top',fontsize=10,
          fontweight='bold',color='#6b1a1a')
y -= lh(10,1.4)+0.005
n_lns=textwrap.wrap(NOTES,width=WRAP_W)
fig2.text(LMAR,y,'\n'.join(n_lns),ha='left',va='top',fontsize=8.2,
          color='#222',linespacing=1.5)
y -= len(n_lns)*lh(8.2)

print(f"Page 2 bottom y = {y:.3f}")

# ── Save PDF ──────────────────────────────────────────────────────────────────
with PdfPages(OUT_PDF) as pdf:
    for fig in (fig1,fig2):
        pdf.savefig(fig,dpi=DPI,bbox_inches='tight')
        plt.close(fig)

print(f"Saved: {OUT_PDF}")
