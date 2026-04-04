#!/usr/bin/env python3
"""
Multi-page PDF write-up: Depth Swap Control (DepthSwapCtrl_005m).
3 pages, US Letter portrait (8.5 × 11 in, 150 DPI).

  Page 1 — Introduction + Stimulus Conditions (trajectory panels)
  Page 2 — Results: Binocular (N / ZdA / ZdB bar graphs)
  Page 3 — Results: Monocular + Findings + Notes

Output: Agents/WriteUps/depth_swapctrl_writeup.pdf
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
    "~/Projects/ObjectBasedAttention/VRDots/Agents/WriteUps/depth_swapctrl_writeup.pdf")

BINO_SESSIONS = [
    '260330_1853', '260331_0621',
    '260401_1313', '260401_1349', '260401_1541', '260401_1705',
]
MONO_SESSIONS = [
    '260330_2012', '260331_1530',   # Mono-R (L eye closed)
    '260331_1705', '260331_1734',   # Mono-L (R eye closed)
]

# ── Page geometry ──────────────────────────────────────────────────────────────
PW, PH = 8.5, 11   # US Letter portrait
DPI     = 150
LMAR, RMAR = 0.09, 0.91
TXT_W = RMAR - LMAR
WRAP_W = 115        # characters per line at this page width / font size

def lh(pt, spacing=1.55):
    """Normalized figure height consumed by one line at given point size."""
    return (pt / 72 * DPI * spacing) / (PH * DPI)

# ── Timing / colours ──────────────────────────────────────────────────────────
T_A=0.00; T_B=0.490; T_S=0.686; T_E=0.739; T_TOT=1.00
CW=2.0; TRANS_COH=1.0; TRANS_NOI=1.5; CCW=0.0
NEAR_Y=0.0; FAR_Y=1.0
CHANCE=1/8
C_CW='#228B22'; C_CCW='#CC3333'; C_TRANS='#CCCCCC'; C_FRAME='#333333'
C_SF='#CC3333'   # red — both fields were red in DepthSwapCtrl (same-colour design)
C_NEAR='#4488CC'; C_FAR='#CC6644'
C_N='#444488'; C_ZDA='#883300'; C_ZDB='#226622'

SWAP_DEFS = [
    ('N',   'N — No Swap',   C_N),
    ('ZdA', 'ZdA',           C_ZDA),
    ('ZdB', 'ZdB',           C_ZDB),
]
COL_TITLES = ['Near Translation', 'Far Translation']
CW_DEPTHS  = ['N', 'F']

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

def analyze(session_list):
    cnt=collections.defaultdict(lambda:[0,0])
    for sid in session_list:
        try: rows=load(sid)
        except FileNotFoundError: print(f"  SKIP: {sid}"); continue
        for r in rows:
            if r.get('EndKey','') in ('timeout','skip','requeue'): continue
            td=r.get('TransDeg',''); rd=r.get('RespDeg','')
            if not td or not rd: continue
            key=(r.get('SwapType','N'), r['Cond'],
                 trans_depth(r['Cond'],r.get('DelayedFieldDepth','N')))
            cnt[key][0]+=int(is_correct(td,rd)); cnt[key][1]+=1
    return cnt

# ── Trajectory drawing ────────────────────────────────────────────────────────
_base  = np.linspace(T_A+0.01,T_TOT-0.01,14)
T_MARKS = np.unique(np.sort(np.concatenate([_base,[(T_S+T_E)/2]])))
EPS = 1e-4   # keep x strictly increasing through depth steps

SF = {'S0':('o',5.5,True),'S1':('s',9.0,False),'S2':('^',6.0,True),'S3':('D',8.5,False)}
SF_COLOR = {'S0':C_SF,'S1':C_SF,'S2':C_SF,'S3':C_SF}

def _plot_sf(ax,name,tk,vk,tq):
    c=SF_COLOR[name]; mk,ms,filled=SF[name]
    mfc=c if filled else 'none'; mew=1.0 if filled else 1.6
    ax.plot(tk,vk,color=c,lw=0.8,ls='-',solid_capstyle='round',zorder=3)
    ax.plot(tq,np.interp(tq,tk,vk),marker=mk,ms=ms,mew=mew,
            mfc=mfc,mec=c,ls='none',zorder=5)

def _traj(swap, is_cued):
    """Return (tS0,vS0, tS1,vS1, tS2,vS2, tS3,vS3) motion trajectories.

    Convention: S0/S1 = CW field (delayed in CUED); always translates.
                S2/S3 = CCW field (non-delayed in CUED); never translates.

    N:       S1 shows TRANS_NOI; S3 stays CCW.
    ZdA/ZdB: Noise subfields join the opposite field's group at T_S.
             S1 (was CW noise) flips to CCW level.
             S3 (was CCW noise) joins translating group → TRANS_NOI → CW.
    """
    t0 = T_B if is_cued else T_A   # CW  field onset
    t2 = T_A if is_cued else T_B   # CCW field onset

    # S0: coherent translator — same for all swap types
    tS0 = np.array([t0, T_S, T_S, T_E, T_E, T_TOT])
    vS0 = np.array([CW, CW, TRANS_COH, TRANS_COH, CW, CW])

    # S2: coherent non-translator — stays CCW for all swap types
    tS2 = np.array([t2, T_TOT])
    vS2 = np.array([CCW, CCW])

    if swap == 'N':
        # S1: noise of translating (CW) field
        tS1 = np.array([t0, T_S, T_S, T_E, T_E, T_TOT])
        vS1 = np.array([CW, CW, TRANS_NOI, TRANS_NOI, CW, CW])
        # S3: stays CCW
        tS3 = np.array([t2, T_TOT])
        vS3 = np.array([CCW, CCW])
    else:  # ZdA or ZdB — noise subfields swap group membership at T_S
        # S1 (CW noise) joins CCW group → flips to CCW at T_S
        tS1 = np.array([t0, T_S-EPS, T_S, T_TOT])
        vS1 = np.array([CW,  CW,     CCW, CCW])
        # S3 (CCW noise) joins CW translating group → TRANS_NOI → CW after T_E
        tS3 = np.array([t2, T_S-EPS, T_S,      T_E,      T_E, T_TOT])
        vS3 = np.array([CCW, CCW,    TRANS_NOI, TRANS_NOI, CW, CW])

    return tS0,vS0, tS1,vS1, tS2,vS2, tS3,vS3

def draw_motion(ax, swap, is_cued, show_labels=False):
    tS0,vS0,tS1,vS1,tS2,vS2,tS3,vS3 = _traj(swap, is_cued)
    t0=T_B if is_cued else T_A; t2=T_A if is_cued else T_B
    m0=T_MARKS[T_MARKS>=t0]; m2=T_MARKS[T_MARKS>=t2]
    for name,tk,vk,mq in [('S0',tS0,vS0,m0),('S1',tS1,vS1,m0),
                           ('S2',tS2,vS2,m2),('S3',tS3,vS3,m2)]:
        _plot_sf(ax,name,tk,vk,mq)
    ax.set_xlim(T_A-.01,T_TOT+.01); ax.set_ylim(-.35,2.55)
    ax.set_xticks([]); ax.set_yticks([CCW,TRANS_COH,TRANS_NOI,CW])
    ax.set_yticklabels(['CCW','Trans\n(coh)','Trans\n(noise)','CW'],fontsize=5.5)
    ax.tick_params(axis='y',length=2,pad=1)
    ax.axvspan(T_S,T_E,color=C_TRANS,alpha=0.6,zorder=1)
    ax.axvline(T_B,color='#AAAAAA',lw=0.8,ls='--',zorder=2)
    for sp in ax.spines.values():
        sp.set_visible(True); sp.set_linewidth(0.7); sp.set_edgecolor(C_FRAME)
    if show_labels:
        for x,lbl in [((T_A+T_B)/2,'A only'),((T_B+T_S)/2,'A+B'),((T_S+T_E)/2,'T')]:
            ax.text(x,2.48,lbl,ha='center',va='top',fontsize=5,
                    color='#888888',style='italic')

def draw_depth(ax, swap, is_cued, cw_dep):
    """Depth tracks using full 4-subfield marker convention.

    ZdA: coherent dots (S0, S2) swap depth planes at T_S.
    ZdB: noise dots    (S1, S3) swap depth planes at T_S.
    """
    cw_y  = NEAR_Y if cw_dep=='N' else FAR_Y
    ccw_y = FAR_Y  if cw_dep=='N' else NEAR_Y
    t_cw  = T_B if is_cued else T_A
    t_ccw = T_A if is_cued else T_B

    def flat(t_on, y):
        return np.array([t_on, T_TOT]), np.array([y, y])
    def step(t_on, y0, y1):
        return (np.array([t_on, T_S-EPS, T_S, T_TOT]),
                np.array([y0,   y0,      y1,  y1]))

    if swap == 'N':
        ts0,vs0 = flat(t_cw,  cw_y)
        ts1,vs1 = flat(t_cw,  cw_y)
        ts2,vs2 = flat(t_ccw, ccw_y)
        ts3,vs3 = flat(t_ccw, ccw_y)
    elif swap == 'ZdA':                  # coherent swap: S0↔S2
        ts0,vs0 = step(t_cw,  cw_y,  ccw_y)
        ts1,vs1 = flat(t_cw,  cw_y)
        ts2,vs2 = step(t_ccw, ccw_y, cw_y)
        ts3,vs3 = flat(t_ccw, ccw_y)
    else:                                # ZdB: noise swap: S1↔S3
        ts0,vs0 = flat(t_cw,  cw_y)
        ts1,vs1 = step(t_cw,  cw_y,  ccw_y)
        ts2,vs2 = flat(t_ccw, ccw_y)
        ts3,vs3 = step(t_ccw, ccw_y, cw_y)

    for name,tk,vk,t_on in [('S0',ts0,vs0,t_cw), ('S1',ts1,vs1,t_cw),
                              ('S2',ts2,vs2,t_ccw),('S3',ts3,vs3,t_ccw)]:
        tq = T_MARKS[T_MARKS >= t_on]
        _plot_sf(ax, name, tk, vk, tq)

    ax.set_xlim(T_A-.01,T_TOT+.01); ax.set_ylim(-0.5,1.5)
    ax.set_xticks([]); ax.set_yticks([NEAR_Y,FAR_Y])
    ax.set_yticklabels(['Near','Far'],fontsize=5.5)
    ax.tick_params(axis='y',length=2,pad=1)
    ax.axvspan(T_S,T_E,color=C_TRANS,alpha=0.6,zorder=1)
    ax.axvline(T_B,color='#AAAAAA',lw=0.8,ls='--',zorder=2)
    for sp in ax.spines.values():
        sp.set_visible(True); sp.set_linewidth(0.7); sp.set_edgecolor(C_FRAME)

# ── Bar-panel helper ───────────────────────────────────────────────────────────
def draw_bars(ax, cnt, swap, show_ylabel=False, show_chance_label=False):
    cn=cnt.get((swap,'CUED','N'),  [0,1]); un=cnt.get((swap,'UNCUED','N'),[0,1])
    cf=cnt.get((swap,'CUED','F'),  [0,1]); uf=cnt.get((swap,'UNCUED','F'),[0,1])
    groups=[cn,un,cf,uf]
    accs=[g[0]/max(g[1],1) for g in groups]
    cis =[wilson_ci(*g) if g[1]>0 else (0,0) for g in groups]
    zn,pn=z_test(cn[0],cn[1],un[0],un[1]) if cn[1]>0 and un[1]>0 else (0,.5)
    zf,pf=z_test(cf[0],cf[1],uf[0],uf[1]) if cf[1]>0 and uf[1]>0 else (0,.5)
    dn=(accs[0]-accs[1])*100; df=(accs[2]-accs[3])*100

    xs=[0.0,0.70,2.00,2.70]
    bcolors=[C_NEAR,C_NEAR,C_FAR,C_FAR]
    hatch=['','///','','///']
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
        ax.text(3.05,CHANCE+0.01,'chance',fontsize=6.5,color='#999999',va='bottom')

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
    ax.text((xs[2]+xs[3])/2,-0.095,'Far\nTrans.', ha='center',fontsize=9,
            fontweight='bold',color=C_FAR, transform=ax.get_xaxis_transform())
    ax.axvline(1.35,color='#DDDDDD',lw=1.0,zorder=1)
    ax.set_xlim(-0.48,3.20); ax.set_ylim(0,1.05)
    ax.set_xticks(xs); ax.set_xticklabels(xlbls,fontsize=9)
    ax.set_yticks([0,.25,.50,.75,1.0])
    ax.set_yticklabels(['0%','25%','50%','75%','100%'],fontsize=9)
    if show_ylabel: ax.set_ylabel('Proportion correct',fontsize=9.5)
    ax.spines[['top','right']].set_visible(False)
    ax.tick_params(axis='x',length=0)

# ── Shared legend handles ──────────────────────────────────────────────────────
TRAJ_LEG = [
    mlines.Line2D([],[],color=C_SF,marker='o',ms=5.5,mew=1.0,mfc=C_SF,  ls='none',label='S0'),
    mlines.Line2D([],[],color=C_SF,marker='s',ms=8.5,mew=1.5,mfc='none',ls='none',label='S1'),
    mlines.Line2D([],[],color=C_SF,marker='^',ms=6.0,mew=1.0,mfc=C_SF,  ls='none',label='S2'),
    mlines.Line2D([],[],color=C_SF,marker='D',ms=8.0,mew=1.5,mfc='none',ls='none',label='S3'),
    mpatches.Patch(facecolor=C_TRANS,alpha=0.8,edgecolor='#888',label='Translation window'),
]
BAR_LEG = [
    mpatches.Patch(facecolor=C_NEAR,alpha=0.82,edgecolor='#333',label='Near translation'),
    mpatches.Patch(facecolor=C_FAR, alpha=0.82,edgecolor='#333',label='Far translation'),
    mpatches.Patch(facecolor='white',hatch='///',edgecolor='#333',label='UNCUED (hatched)'),
    mlines.Line2D([],[],color='#222',lw=1.5,marker='|',markersize=6,label='Wilson 95% CI'),
]

# ── Text blocks ────────────────────────────────────────────────────────────────
INTRO = (
    "The DepthSwapCtrl experiment isolated the contribution of depth-plane identity to dot cueing "
    "by introducing mid-trial depth swaps at translation onset (T\u209B). Two swap types were "
    "tested alongside a no-swap baseline (N): ZdA swaps the depth planes of the two coherent "
    "dots (S0 and S2) at T\u209B, causing the cued coherent translator to change depth plane; "
    "ZdB swaps the two noise dots (S1 and S3) instead, leaving the cued coherent translator "
    "in its original depth plane. ZdA and ZdB are matched for the number of depth-plane "
    "transitions per trial, differing only in whether the transition affects the coherent "
    "translator. All sessions used a 0.05 m depth separation (~0.86\u00b0 disparity at 2 m) "
    "and same-color stimuli (both fields red). Six binocular and four monocular sessions "
    "(2 right-eye, 2 left-eye) were collected from one observer."
)
STIM_NOTE = (
    "Trajectory diagrams reflect the all-red stimulus (both fields red; same-color design). "
    "Columns are organized by depth of the translating field (Near | Far). "
    "S0\u25cf/S1\u25a1 = CW field (delayed in CUED); S2\u25b2/S3\u25c7 = CCW field. "
    "Filled markers = coherent subfields (S0, S2); open markers = noise subfields (S1, S3). "
    "Motion tracks are identical across swap types \u2014 the swap is depth-only at T\u209B. "
    "Depth tracks (thin row below each motion panel): in ZdA the coherent markers "
    "(S0\u25cf, S2\u25b2) cross depth planes at T\u209B; in ZdB the noise markers (S1\u25a1, S3\u25c7) cross instead."
)
ANALYSIS_NOTE = (
    "Analysis: Near/Far labels use the translating-field-depth convention. "
    "CUED Near = delayed field at Near (it translates Near). "
    "UNCUED Near = non-delayed field at Near (it translates Near; delayed field is at Far). "
    "Proportion correct pooled across color, rotation, and translation direction "
    "(\u224832 trials/cell per swap\u00d7cond\u00d7depth within bino; \u224821 within mono). "
    "One-tailed z-test: CUED > UNCUED."
)
FINDINGS_BINO = (
    "Binocular results (n=1,152, 6 sessions, 0.05 m depth separation): Dot cueing was reliable "
    "overall (+12.5 pp, z=4.30, p<.001). Using the translating-field-depth convention, Near "
    "translation yielded the larger cueing effect (CUED=42.4%, UNCUED=23.6%, \u0394=+18.8 pp, "
    "z=4.79, p<.001) while Far translation showed a smaller marginal effect (CUED=54.5%, "
    "UNCUED=48.3%, \u0394=+6.2 pp, z=1.50, p=.067). UNCUED performance is particularly "
    "low in the Near depth plane (23.6%), consistent with the anti-cued observer having "
    "difficulty detecting Near-plane translation. Far UNCUED performance was much higher "
    "(48.3%), leaving less room for cueing. Note: this translating-field-depth analysis "
    "reverses the apparent Near inversion that appears when using the delayed-field-depth "
    "convention (which conflates translating-field depth with cueing condition). "
    "Across swap types: ZdB produced the largest cueing (+16.1 pp, z=3.19, p=.001), "
    "followed by ZdA (+11.5 pp, z=2.33, p=.010) and N (+9.9 pp, z=1.95, p=.026). "
    "ZdA cueing is comparable to N binocularly, suggesting that depth-plane disruption "
    "of the cued translator alone does not produce large binocular cueing losses; "
    "ZdB\u2019s advantage reflects the benefit of keeping the cued translator in a "
    "stable depth plane while disrupting the distractor plane."
)
FINDINGS_MONO = (
    "Monocular results (n=769, 4 sessions): Overall cueing attenuated but survived "
    "(+7.1 pp, z=2.02, p=.022). Near translation cueing: +8.3 pp (z=1.69, p=.046); "
    "Far translation cueing: +5.9 pp (z=1.18, p=.12). The critical swap-type dissociation: "
    "ZdA collapsed to exactly +0.0 pp (z=0.00, p=.50) monocularly \u2014 the sharpest "
    "mechanistic result in the dataset. When binocular disparity is unavailable, "
    "changing the depth plane of the cued translator has zero behavioral consequence. "
    "ZdB survived monocularly (+12.0 pp, z=1.96, p=.025) and N was +9.4 pp "
    "(z=1.51, p=.066). ZdB\u2019s monocular survival suggests its advantage includes "
    "a monocular component, plausibly the brief positional shift of the non-coherent "
    "distractor at depth change (\u22481.5\u20135 arcmin depending on eccentricity), "
    "which may disrupt the distractor surface representation independent of stereopsis."
)
NOTES = (
    "Notes: (1) Sessions 260401_1541 and 260401_1705 were the 5th and 6th VR sessions "
    "in a single day (binocular) and show performance collapse (34\u201340% overall "
    "accuracy vs. 44\u201351% for other binocular sessions). Included in pooled statistics "
    "as planned. (2) Two color-related factors likely contribute to reduced cueing vs. "
    "two-color baselines (~28\u201350 pp): (a) absence of between-field color differences "
    "eliminates a reliable color-based field-identity cue present in all prior baselines; "
    "(b) the specific color used (red only) may independently reduce cueing if perceptual "
    "sensitivity to motion cueing is stronger for green than red for this observer \u2014 "
    "a single-observer asymmetry that cannot yet be ruled out. A red-only vs. green-only "
    "baseline session would dissociate (a) from (b). "
    "(3) The geometric confound in ZdA (0.05 m depth change induces "
    "0\u20135 arcmin monocular positional shift at 2 m, scaling with eccentricity) "
    "cannot be fully dissociated from the stereoscopic depth-plane account at this "
    "sample size. The ZdA monocular null is consistent with either account."
)

# ── Load data ──────────────────────────────────────────────────────────────────
print("Loading binocular sessions..."); bino = analyze(BINO_SESSIONS)
print("Loading monocular sessions..."); mono = analyze(MONO_SESSIONS)

# ═════════════════════════════════════════════════════════════════════════════
# PAGE 1 — Introduction + Stimulus Conditions
# ═════════════════════════════════════════════════════════════════════════════
fig1 = plt.figure(figsize=(PW,PH)); fig1.patch.set_facecolor('white')
y = 0.970

# Title
fig1.text(0.50,y,'VRDots \u2014 Depth Swap Control (DepthSwapCtrl_005m)',
          ha='center',va='top',fontsize=13,fontweight='bold',color='#111111')
y -= lh(13,1.3)+0.008
fig1.text(0.50,y,
    'Binocular: 260330_1853, 260331_0621, 260401_1313, 260401_1349, 260401_1541, 260401_1705 (n=1,152)   '
    'Monocular-R: 260330_2012, 260331_1530   Monocular-L: 260331_1705, 260331_1734 (n=769)',
    ha='center',va='top',fontsize=6.5,color='#555555')
y -= lh(6.5,1.3)+0.010

# Intro
for txt,fs,col,sty in [(INTRO,8.5,'#111111','normal'),(STIM_NOTE,7.5,'#555555','italic')]:
    lns=textwrap.wrap(txt,width=WRAP_W)
    fig1.text(LMAR,y,'\n'.join(lns),ha='left',va='top',fontsize=fs,
              color=col,linespacing=1.5,style=sty)
    y -= len(lns)*lh(fs)+0.008

y -= 0.005
fig1.text(0.50,y,'Stimulus Conditions',ha='center',va='top',
          fontsize=11,fontweight='bold',color='#1a3a6b')
y -= lh(11,1.3)+0.006

# Trajectory GridSpec (12 rows × 2 cols)
TRAJ_BOT = 0.068   # fixed bottom margin for trajectories + legend
TRAJ_H   = y - TRAJ_BOT - 0.030   # leave 0.030 for legend
traj_top = y; traj_bot = y - TRAJ_H

traj_gs = gridspec.GridSpec(12,2,
    top=traj_top,bottom=traj_bot,
    left=0.115,right=0.865,
    height_ratios=[3,1,3,1, 3,1,3,1, 3,1,3,1],
    hspace=0.07,wspace=0.25)

for si,(swap,swap_label,swap_col) in enumerate(SWAP_DEFS):
    base=si*4
    for ci,(ctitle,cw_dep) in enumerate(zip(COL_TITLES,CW_DEPTHS)):
        ax_cm=fig1.add_subplot(traj_gs[base+0,ci])
        draw_motion(ax_cm,swap,is_cued=True,show_labels=(si==0 and ci==0))
        if si==0: ax_cm.set_title(ctitle,fontsize=8.5,fontweight='bold',pad=3)
        if ci==0: ax_cm.set_ylabel('CUED',fontsize=7.5,fontweight='bold',labelpad=3)

        ax_cd=fig1.add_subplot(traj_gs[base+1,ci])
        draw_depth(ax_cd,swap,is_cued=True,cw_dep=cw_dep)
        if ci==0: ax_cd.set_ylabel('Depth',fontsize=6,labelpad=3,color='#555')

        ax_um=fig1.add_subplot(traj_gs[base+2,ci])
        draw_motion(ax_um,swap,is_cued=False)
        if ci==0: ax_um.set_ylabel('UNCUED',fontsize=7.5,fontweight='bold',labelpad=3)

        ax_ud=fig1.add_subplot(traj_gs[base+3,ci])
        draw_depth(ax_ud,swap,is_cued=False,cw_dep=cw_dep)
        if ci==0: ax_ud.set_ylabel('Depth',fontsize=6,labelpad=3,color='#555')

    pos_t=traj_gs[base+0,0].get_position(fig1).y1
    pos_b=traj_gs[base+3,0].get_position(fig1).y0
    fig1.text(0.875,(pos_t+pos_b)/2,swap_label,ha='left',va='center',
              fontsize=7.5,fontweight='bold',color=swap_col,rotation=90)
    if si<2:
        sep=pos_b-0.004
        fig1.add_artist(plt.Line2D([0.115,0.865],[sep,sep],
            transform=fig1.transFigure,color='#CCCCCC',lw=0.9,ls='--'))

# Trajectory legend
ax_tleg=fig1.add_axes([LMAR,TRAJ_BOT-0.012,TXT_W,0.030]); ax_tleg.axis('off')
ax_tleg.legend(handles=TRAJ_LEG,loc='center',ncol=5,fontsize=7,
               frameon=True,framealpha=0.9,edgecolor='#CCC')

# ═════════════════════════════════════════════════════════════════════════════
# PAGE 2 — Results: Binocular
# ═════════════════════════════════════════════════════════════════════════════
fig2 = plt.figure(figsize=(PW,PH)); fig2.patch.set_facecolor('white')
y = 0.970

fig2.text(0.50,y,'VRDots \u2014 Depth Swap Control: Binocular Results',
          ha='center',va='top',fontsize=13,fontweight='bold',color='#111111')
y -= lh(13,1.3)+0.010

# Analysis note
an_lns=textwrap.wrap(ANALYSIS_NOTE,width=WRAP_W)
fig2.text(LMAR,y,'\n'.join(an_lns),ha='left',va='top',fontsize=8,
          color='#444',linespacing=1.5)
y -= len(an_lns)*lh(8)+0.015

# Results heading
fig2.text(0.50,y,'Results \u2014 Binocular  (n=1,152 / 6 sessions)',
          ha='center',va='top',fontsize=11,fontweight='bold',color='#1a3a6b')
y -= lh(11,1.3)+0.010

# Bar grid  — 1 row × 3 cols, generous height
BAR_H2 = 0.420
bar_gs2=gridspec.GridSpec(1,3,top=y,bottom=y-BAR_H2,
    left=LMAR+0.03,right=RMAR,wspace=0.35)
for ci,(swap,swap_label,swap_col) in enumerate(SWAP_DEFS):
    ax=fig2.add_subplot(bar_gs2[0,ci])
    draw_bars(ax,bino,swap,show_ylabel=(ci==0),show_chance_label=(ci==2))
    ax.set_title(swap_label,fontsize=11,fontweight='bold',pad=10,color=swap_col)
y -= BAR_H2+0.018

# Bar legend
ax_bl=fig2.add_axes([LMAR,y-0.028,TXT_W,0.028]); ax_bl.axis('off')
ax_bl.legend(handles=BAR_LEG,loc='center',ncol=4,fontsize=8.5,
             frameon=True,framealpha=0.9,edgecolor='#CCC')
y -= 0.028+0.018

# Findings — binocular
fig2.text(LMAR,y,'Findings',ha='left',va='top',fontsize=10,
          fontweight='bold',color='#1a3a6b')
y -= lh(10,1.4)+0.005
fb_lns=textwrap.wrap(FINDINGS_BINO,width=WRAP_W)
fig2.text(LMAR,y,'\n'.join(fb_lns),ha='left',va='top',fontsize=8.2,
          color='#222',linespacing=1.5)
y -= len(fb_lns)*lh(8.2)+0.012
print(f"Page 2 bottom y = {y:.3f}")

# ═════════════════════════════════════════════════════════════════════════════
# PAGE 3 — Results: Monocular + Findings + Notes
# ═════════════════════════════════════════════════════════════════════════════
fig3 = plt.figure(figsize=(PW,PH)); fig3.patch.set_facecolor('white')
y = 0.970

fig3.text(0.50,y,'VRDots \u2014 Depth Swap Control: Monocular Results',
          ha='center',va='top',fontsize=13,fontweight='bold',color='#111111')
y -= lh(13,1.3)+0.015

fig3.text(0.50,y,'Results \u2014 Monocular  (n=769 / 4 sessions)',
          ha='center',va='top',fontsize=11,fontweight='bold',color='#1a3a6b')
y -= lh(11,1.3)+0.010

BAR_H3 = 0.420
bar_gs3=gridspec.GridSpec(1,3,top=y,bottom=y-BAR_H3,
    left=LMAR+0.03,right=RMAR,wspace=0.35)
for ci,(swap,swap_label,swap_col) in enumerate(SWAP_DEFS):
    ax=fig3.add_subplot(bar_gs3[0,ci])
    draw_bars(ax,mono,swap,show_ylabel=(ci==0),show_chance_label=(ci==2))
    ax.set_title(swap_label,fontsize=11,fontweight='bold',pad=10,color=swap_col)
y -= BAR_H3+0.018

ax_bl3=fig3.add_axes([LMAR,y-0.028,TXT_W,0.028]); ax_bl3.axis('off')
ax_bl3.legend(handles=BAR_LEG,loc='center',ncol=4,fontsize=8.5,
              frameon=True,framealpha=0.9,edgecolor='#CCC')
y -= 0.028+0.018

for heading,hcol,txt in [
    ('Findings','#1a3a6b',FINDINGS_MONO),
    ('Notes',   '#6b1a1a',NOTES),
]:
    fig3.text(LMAR,y,heading,ha='left',va='top',fontsize=10,
              fontweight='bold',color=hcol)
    y -= lh(10,1.4)+0.005
    lns=textwrap.wrap(txt,width=WRAP_W)
    fig3.text(LMAR,y,'\n'.join(lns),ha='left',va='top',fontsize=8.2,
              color='#222',linespacing=1.5)
    y -= len(lns)*lh(8.2)+0.015

print(f"Page 3 bottom y = {y:.3f}")

# ── Save PDF ──────────────────────────────────────────────────────────────────
with PdfPages(OUT_PDF) as pdf:
    for fig in (fig1,fig2,fig3):
        pdf.savefig(fig,dpi=DPI,bbox_inches='tight')
        plt.close(fig)

print(f"Saved: {OUT_PDF}")
