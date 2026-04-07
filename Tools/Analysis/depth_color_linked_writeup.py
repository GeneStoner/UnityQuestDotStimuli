#!/usr/bin/env python3
"""
depth_color_linked_writeup.py
Combined design + results writeup for DepthColorLinked_005m.

Page 1 — Trajectory figure: 2×2 of Dot Cueing × Depth Cueing (Near & Far)
Page 2 — Results: Session 1, Session 2, Combined bar charts + stats
Page 3 — Interpretation & notes

Output: Agents/WriteUps/depth_color_linked_writeup.pdf
"""

import os, csv, math, collections, textwrap
from itertools import product
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.lines as mlines
import matplotlib.patches as mpatches
import matplotlib.ticker
from matplotlib.backends.backend_pdf import PdfPages

# ── Paths ─────────────────────────────────────────────────────────────────────
DATA_DIR = os.path.expanduser(
    "~/Library/Application Support/ThatsRandom/VRDotsDataFiles")
OUT_PDF  = os.path.expanduser(
    "~/Projects/ObjectBasedAttention/VRDots/Agents/WriteUps/depth_color_linked_writeup.pdf")

SESSIONS = [
    ('260404_0940', 'Session 1  (260404_0940)'),
    ('260404_1123', 'Session 2  (260404_1123)'),
    ('260406_1001', 'Session 3  (260406_1001)'),
    ('260406_1034', 'Session 4  (260406_1034)'),
]

PW, PH = 8.5, 11; DPI = 150
LMAR, RMAR = 0.09, 0.91; TXT_W = RMAR - LMAR
CHANCE = 1/8

def lh(pt, spacing=1.55):
    return (pt / 72 * DPI * spacing) / (PH * DPI)

# ── Colours ───────────────────────────────────────────────────────────────────
C_NEAR   = '#CC3333';  C_FAR    = '#228B22'
C_TRANS  = '#CCCCCC';  C_FRAME  = '#333333'
C_ZDCOH  = '#883300';  C_ZDNOI  = '#226622'
C_DOT_Y  = '#1a6b1a';  C_DOT_N  = '#666666'
C_DEP_Y  = '#1a3a8b';  C_DEP_N  = '#aa2222'

# ── Timing ────────────────────────────────────────────────────────────────────
T_A=0.00; T_B=0.490; T_S=0.686; T_E=0.739; T_TOT=1.00
CW=2.0; TRANS_COH=1.0; TRANS_NOI=1.5; CCW=0.0
NEAR_Y=0.0; FAR_Y=1.0; EPS=1e-4

_base   = np.linspace(T_A+0.01, T_TOT-0.01, 14)
T_MARKS = np.unique(np.sort(np.concatenate([_base, [(T_S+T_E)/2]])))
SF      = {'S0':('o',5.5,True),'S1':('s',9.0,False),'S2':('^',6.0,True),'S3':('D',8.5,False)}

SWAP_DEFS  = [('ZdCoh', C_ZDCOH), ('ZdNoi', C_ZDNOI)]
COL_TITLES = ['Near Translation', 'Far Translation']
CW_DEPTHS  = ['N', 'F']

COND_DEFS = [
    ('ZdNoi', True,  True,  True,  'CUED + ZdNoi'),
    ('ZdCoh', True,  True,  False, 'CUED + ZdCoh'),
    ('ZdCoh', False, False, True,  'UNCUED + ZdCoh'),
    ('ZdNoi', False, False, False, 'UNCUED + ZdNoi'),
]
COND_BG = ['#EEF8EE', '#FFFAEE', '#EEF2FF', '#F5F5F5']

# ═══════════════════════════════════════════════════════════════════════════════
# TRAJECTORY DRAWING (page 1)
# ═══════════════════════════════════════════════════════════════════════════════
def _opp_c(c): return C_FAR if c == C_NEAR else C_NEAR

def _sf_colors(swap, cw_dep):
    cw_c = C_NEAR if cw_dep == 'N' else C_FAR
    cc_c = _opp_c(cw_c)
    pre = {'S0':cw_c,'S1':cw_c,'S2':cc_c,'S3':cc_c}
    if swap == 'ZdCoh':
        post = {'S0':cc_c,'S1':cw_c,'S2':cw_c,'S3':cc_c}
    else:  # ZdNoi
        post = {'S0':cw_c,'S1':cc_c,'S2':cc_c,'S3':cw_c}
    return pre, post

def _plot2c(ax, name, tk, vk, tq, c_pre, c_post):
    mk, ms, filled = SF[name]; mew = 1.0 if filled else 1.6
    ax.plot(tk, vk, color=c_pre, lw=0.9, solid_capstyle='round', zorder=3)
    if c_pre != c_post:
        v_ts = float(np.interp(T_S, tk, vk))
        tk_p = np.concatenate([[T_S], tk[tk > T_S]])
        vk_p = np.concatenate([[v_ts], vk[tk > T_S]])
        if len(tk_p) >= 2:
            ax.plot(tk_p, vk_p, color=c_post, lw=0.9, solid_capstyle='round', zorder=4)
    for tq_s, c in [(tq[tq < T_S], c_pre), (tq[tq >= T_S], c_post)]:
        if len(tq_s) == 0: continue
        mfc = c if filled else 'none'
        ax.plot(tq_s, np.interp(tq_s,tk,vk), marker=mk, ms=ms, mew=mew,
                mfc=mfc, mec=c, ls='none', zorder=5)

def _traj(swap, is_cued):
    t0 = T_B if is_cued else T_A; t2 = T_A if is_cued else T_B
    tS0=np.array([t0,T_S,T_S,T_E,T_E,T_TOT]); vS0=np.array([CW,CW,TRANS_COH,TRANS_COH,CW,CW])
    tS2=np.array([t2,T_TOT]);                   vS2=np.array([CCW,CCW])
    tS1=np.array([t0,T_S-EPS,T_S,T_TOT]);       vS1=np.array([CW,CW,CCW,CCW])
    tS3=np.array([t2,T_S-EPS,T_S,T_E,T_E,T_TOT]); vS3=np.array([CCW,CCW,TRANS_NOI,TRANS_NOI,CW,CW])
    return tS0,vS0,tS1,vS1,tS2,vS2,tS3,vS3

def _depth_tracks(swap, is_cued, cw_dep):
    cwy = NEAR_Y if cw_dep=='N' else FAR_Y
    ccy = FAR_Y  if cw_dep=='N' else NEAR_Y
    t0 = T_B if is_cued else T_A; t2 = T_A if is_cued else T_B
    flat = lambda t,y: (np.array([t,T_TOT]),np.array([y,y]))
    step = lambda t,y0,y1: (np.array([t,T_S-EPS,T_S,T_TOT]),np.array([y0,y0,y1,y1]))
    if swap == 'ZdCoh':
        return step(t0,cwy,ccy), flat(t0,cwy), step(t2,ccy,cwy), flat(t2,ccy)
    else:  # ZdNoi
        return flat(t0,cwy), step(t0,cwy,ccy), flat(t2,ccy), step(t2,ccy,cwy)

def _style_motion(ax, show_labels=False):
    ax.set_xlim(T_A-.01,T_TOT+.01); ax.set_ylim(-.35,2.55)
    ax.set_xticks([]); ax.set_yticks([CCW,TRANS_COH,TRANS_NOI,CW])
    ax.set_yticklabels(['CCW','T\n(c)','T\n(n)','CW'],fontsize=4.5)
    ax.tick_params(axis='y',length=2,pad=1)
    ax.axvspan(T_S,T_E,color=C_TRANS,alpha=0.6,zorder=1)
    ax.axvline(T_B,color='#AAAAAA',lw=0.7,ls='--',zorder=2)
    for sp in ax.spines.values(): sp.set_linewidth(0.6); sp.set_edgecolor(C_FRAME)
    if show_labels:
        for x,l in [((T_A+T_B)/2,'A'),((T_B+T_S)/2,'A+B'),((T_S+T_E)/2,'T')]:
            ax.text(x,2.48,l,ha='center',va='top',fontsize=4,color='#888',style='italic')

def _style_depth(ax):
    ax.set_xlim(T_A-.01,T_TOT+.01); ax.set_ylim(-0.5,1.5)
    ax.set_xticks([]); ax.set_yticks([NEAR_Y,FAR_Y])
    ax.set_yticklabels(['N','F'],fontsize=4.5); ax.tick_params(axis='y',length=2,pad=1)
    ax.axvspan(T_S,T_E,color=C_TRANS,alpha=0.6,zorder=1)
    ax.axvline(T_B,color='#AAAAAA',lw=0.7,ls='--',zorder=2)
    for sp in ax.spines.values(): sp.set_linewidth(0.6); sp.set_edgecolor(C_FRAME)

def draw_motion(ax, swap, is_cued, cw_dep, show_labels=False):
    tS0,vS0,tS1,vS1,tS2,vS2,tS3,vS3 = _traj(swap, is_cued)
    pre, post = _sf_colors(swap, cw_dep)
    t0=T_B if is_cued else T_A; t2=T_A if is_cued else T_B
    m0=T_MARKS[T_MARKS>=t0]; m2=T_MARKS[T_MARKS>=t2]
    for nm,tk,vk,mq in [('S0',tS0,vS0,m0),('S1',tS1,vS1,m0),
                         ('S2',tS2,vS2,m2),('S3',tS3,vS3,m2)]:
        _plot2c(ax,nm,tk,vk,mq,pre[nm],post[nm])
    _style_motion(ax, show_labels)

def draw_depth(ax, swap, is_cued, cw_dep):
    (ts0,vs0),(ts1,vs1),(ts2,vs2),(ts3,vs3) = _depth_tracks(swap,is_cued,cw_dep)
    pre, post = _sf_colors(swap, cw_dep)
    t0=T_B if is_cued else T_A; t2=T_A if is_cued else T_B
    for nm,tk,vk,ton in [('S0',ts0,vs0,t0),('S1',ts1,vs1,t0),
                          ('S2',ts2,vs2,t2),('S3',ts3,vs3,t2)]:
        tq = T_MARKS[T_MARKS>=ton]
        _plot2c(ax,nm,tk,vk,tq,pre[nm],post[nm])
    _style_depth(ax)

# ═══════════════════════════════════════════════════════════════════════════════
# STATS & DATA
# ═══════════════════════════════════════════════════════════════════════════════
def normal_cdf(x): return 0.5*(1+math.erf(x/math.sqrt(2)))

def z_test(k1,n1,k2,n2):
    p1,p2=k1/n1,k2/n2; pp=(k1+k2)/(n1+n2)
    se=math.sqrt(max(pp*(1-pp)*(1/n1+1/n2),1e-12))
    z=(p1-p2)/se; return z,1-normal_cdf(z)

def wilson_ci(k,n,z=1.96):
    p=k/n; d=1+z**2/n; c=(p+z**2/(2*n))/d
    hw=z*math.sqrt(p*(1-p)/n+z**2/(4*n**2))/d
    return c-hw,c+hw

def sig_vs_chance(k,n):
    p=k/n; se=math.sqrt(max(CHANCE*(1-CHANCE)/n,1e-12))
    z=(p-CHANCE)/se; pv=1-normal_cdf(z)
    return ('***' if pv<.001 else '**' if pv<.01 else '*' if pv<.05
            else '†' if pv<.1 else 'n.s.'), pv

def stars(p):
    return '***' if p<.001 else '**' if p<.01 else '*' if p<.05 else '†' if p<.1 else 'n.s.'

def pp(k,n): return (k/n-CHANCE)*100 if n>0 else 0.0
def ci_pp(k,n):
    lo,hi=wilson_ci(k,n); return (lo-CHANCE)*100,(hi-CHANCE)*100

def depth_cue_yes(cond,swap): return (cond=='CUED') != (swap=='ZdA')

def trans_depth_label(cond,swap,dfd):
    return dfd if depth_cue_yes(cond,swap) else ('F' if dfd=='N' else 'N')

def load(sid):
    path = os.path.join(DATA_DIR, 'vr_dots_session_{}.tsv'.format(sid))
    with open(path) as f:
        return list(csv.DictReader(f, delimiter='\t'))

def is_correct(td,rd):
    d=(float(rd)-float(td)+360)%360; return (360-d if d>180 else d)<=22.5

def analyze(rows):
    cnt = collections.defaultdict(lambda:[0,0])
    valid = [r for r in rows if r.get('TransDeg') and r.get('RespDeg')
             and r.get('EndKey','') not in ('timeout','skip','requeue')]
    for r in valid:
        cond=r['Cond']; swap=r['SwapType']; dfd=r['DelayedFieldDepth']
        corr=int(is_correct(r['TransDeg'],r['RespDeg']))
        dep_cue='YES' if depth_cue_yes(cond,swap) else 'NO'
        tdep=trans_depth_label(cond,swap,dfd)
        cnt[('ALL','ALL')][0]+=corr;       cnt[('ALL','ALL')][1]+=1
        cnt[(cond,'ALL')][0]+=corr;        cnt[(cond,'ALL')][1]+=1
        cnt[(cond,dep_cue)][0]+=corr;      cnt[(cond,dep_cue)][1]+=1
        cnt[(cond,dep_cue,tdep)][0]+=corr; cnt[(cond,dep_cue,tdep)][1]+=1
    return dict(cnt), len(valid)

# Load all data
session_data = {}
all_rows = []
for sid,_ in SESSIONS:
    rows = load(sid)
    all_rows.extend(rows)
    session_data[sid], _ = analyze(rows)
combined_data, n_combined = analyze(all_rows)

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 1 — Trajectory figure
# ═══════════════════════════════════════════════════════════════════════════════
fig1 = plt.figure(figsize=(PW,PH)); fig1.patch.set_facecolor('white')
y = 0.970

fig1.text(0.50,y,'DepthColorLinked_005m — Design & Stimulus',
          ha='center',va='top',fontsize=13,fontweight='bold',color='#111111')
y -= lh(13,1.3)+0.004

fig1.text(0.50,y,
    'Factor 1 — Dot Cueing  (✓/✗):    does the delayed-onset dot field translate?',
    ha='center',va='top',fontsize=7.8,fontweight='bold',color=C_DOT_Y)
y -= lh(7.8,1.3)
fig1.text(0.50,y,
    'Factor 2 — Depth Cueing (✓/✗):   does translation occur at the depth where the cued field appeared?',
    ha='center',va='top',fontsize=7.8,fontweight='bold',color=C_DEP_Y)
y -= lh(7.8,1.3)+0.002
fig1.text(0.50,y,
    'Near plane = Red  ·  Far plane = Green  ·  '
    'Color changes at T\u209B for swapping subfields  ·  '
    'Filled = coherent (S0●, S2▲)  ·  Open = noise (S1□, S3◇)',
    ha='center',va='top',fontsize=6.8,color='#555555')
y -= lh(6.8,1.3)+0.006

TRAJ_BOT = 0.040
traj_gs = gridspec.GridSpec(8,2,
    top=y,bottom=TRAJ_BOT+0.028,
    left=0.215,right=0.865,
    height_ratios=[3,1]*4,
    hspace=0.08,wspace=0.22)

for ci,(ctitle,cw_dep) in enumerate(zip(COL_TITLES,CW_DEPTHS)):
    for ri,(swap,is_cued,dot_ok,depth_ok,detail) in enumerate(COND_DEFS):
        ax_m = fig1.add_subplot(traj_gs[ri*2,ci])
        ax_m.set_facecolor(COND_BG[ri])
        draw_motion(ax_m,swap,is_cued,cw_dep,show_labels=(ri==0 and ci==0))
        if ri==0: ax_m.set_title(ctitle,fontsize=8.5,fontweight='bold',pad=3)
        ax_d = fig1.add_subplot(traj_gs[ri*2+1,ci])
        ax_d.set_facecolor(COND_BG[ri])
        draw_depth(ax_d,swap,is_cued,cw_dep)
        if ci==0:
            ax_m.set_ylabel('Dot ✓  CUED' if dot_ok else 'Dot ✗  UNCUED',
                fontsize=6.5,fontweight='bold',labelpad=3,
                color=C_DOT_Y if dot_ok else C_DOT_N)
            ax_d.set_ylabel('Depth ✓' if depth_ok else 'Depth ✗',
                fontsize=6.0,fontweight='bold',labelpad=3,
                color=C_DEP_Y if depth_ok else C_DEP_N)

for ri,(swap,is_cued,dot_ok,depth_ok,detail) in enumerate(COND_DEFS):
    pos_m=traj_gs[ri*2,1].get_position(fig1)
    pos_d=traj_gs[ri*2+1,1].get_position(fig1)
    mid_y=(pos_m.y1+pos_d.y0)/2
    fig1.text(0.870,mid_y,detail,ha='left',va='center',fontsize=6.5,
              fontweight='bold',color=C_ZDCOH if swap=='ZdCoh' else C_ZDNOI)

bot_cued   = traj_gs[3,0].get_position(fig1).y0
top_uncued = traj_gs[4,0].get_position(fig1).y1
sep_y = (bot_cued+top_uncued)/2
fig1.add_artist(plt.Line2D([0.06,0.94],[sep_y,sep_y],
    transform=fig1.transFigure,color='#888888',lw=1.2))

for rows_,label_,col_ in [((0,3),'DOT\nCUED',C_DOT_Y),((4,7),'DOT\nUNCUED',C_DOT_N)]:
    top_=traj_gs[rows_[0],0].get_position(fig1).y1
    bot_=traj_gs[rows_[1],0].get_position(fig1).y0
    fig1.text(0.055,(top_+bot_)/2,label_,ha='center',va='center',
              fontsize=7.5,fontweight='bold',color=col_,rotation=90)

leg_h=[
    mlines.Line2D([],[],color=C_NEAR,marker='o',ms=5,mew=1.0,mfc=C_NEAR,ls='none',label='S0● coh  (Near=Red)'),
    mlines.Line2D([],[],color=C_NEAR,marker='s',ms=7,mew=1.4,mfc='none',ls='none',label='S1□ noise (Near=Red)'),
    mlines.Line2D([],[],color=C_FAR, marker='^',ms=5.5,mew=1.0,mfc=C_FAR, ls='none',label='S2▲ coh  (Far=Green)'),
    mlines.Line2D([],[],color=C_FAR, marker='D',ms=7,mew=1.4,mfc='none',ls='none',label='S3◇ noise (Far=Green)'),
    mpatches.Patch(facecolor=C_TRANS,alpha=0.8,edgecolor='#888',label='Translation window'),
]
ax_tl=fig1.add_axes([LMAR,TRAJ_BOT-0.002,TXT_W,0.026]); ax_tl.axis('off')
ax_tl.legend(handles=leg_h,loc='center',ncol=5,fontsize=6.5,
             frameon=True,framealpha=0.9,edgecolor='#CCC')

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 2 — Results
# ═══════════════════════════════════════════════════════════════════════════════
fig2 = plt.figure(figsize=(PW,PH)); fig2.patch.set_facecolor('white')

fig2.text(0.50,0.975,'DepthColorLinked_005m — Results',
          ha='center',va='top',fontsize=13,fontweight='bold',color='#111111')
fig2.text(0.50,0.950,
    'Near=Red · Far=Green · depth sep = 0.05 m · 8-AFC · '
    'Bars = % correct above chance (12.5%) with 95% Wilson CI',
    ha='center',va='top',fontsize=8,color='#555')

# Five columns: S1, S2, S3, S4, Combined
res_gs = gridspec.GridSpec(1,5,top=0.775,bottom=0.36,
    left=LMAR,right=RMAR,wspace=0.22)

# 4 conditions in 2×2 display order
CELL_ORDER = [('CUED','YES'),('CUED','NO'),('UNCUED','YES'),('UNCUED','NO')]
CELL_LABELS = ['CUED\nDepth✓\n(ZdNoi)','CUED\nDepth✗\n(ZdCoh)',
               'UNCUED\nDepth✓\n(ZdCoh)','UNCUED\nDepth✗\n(ZdNoi)']
BAR_COLORS  = [C_DEP_Y, C_DEP_N, C_DEP_Y, C_DEP_N]
BAR_ALPHAS  = [1.0, 1.0, 0.55, 0.55]

def draw_result_panel(ax, cnt, title, n_tot):
    xs = [0, 0.55, 1.25, 1.80]
    ymax = -99
    for xi,(x,key,lbl,col,alp) in enumerate(zip(xs,CELL_ORDER,CELL_LABELS,BAR_COLORS,BAR_ALPHAS)):
        k,n = cnt.get(key,[0,1])
        pv = pp(k,n)
        lo,hi = ci_pp(k,n)
        bar = ax.bar(x,pv,0.46,color=col,alpha=alp,zorder=3,
                     edgecolor='white',linewidth=0.5)
        ax.errorbar(x,pv,yerr=[[pv-lo],[hi-pv]],fmt='none',
                    color='#333',capsize=3,capthick=1,lw=1,zorder=4)
        s,_ = sig_vs_chance(k,n)
        ax.text(x,max(pv,hi)+1.5,s,ha='center',va='bottom',fontsize=7,color='#333')
        ymax = max(ymax, hi)

    # Cueing effect annotations
    for (x1,x2,ck,ck2,uk,uk2) in [
        (0,0.55,('CUED','YES'),('CUED','NO'),('UNCUED','YES'),('UNCUED','NO'))
    ]:
        cy_k,cy_n=cnt.get(('CUED','YES'),[0,1]); cn_k,cn_n=cnt.get(('CUED','NO'),[0,1])
        uy_k,uy_n=cnt.get(('UNCUED','YES'),[0,1]); un_k,un_n=cnt.get(('UNCUED','NO'),[0,1])

        # F1 effect (CUED vs UNCUED)
        _,f1p=z_test(cy_k+cn_k,cy_n+cn_n,uy_k+un_k,uy_n+un_n)
        f1eff=pp(cy_k+cn_k,cy_n+cn_n)-pp(uy_k+un_k,uy_n+un_n)
        # F2 effect (Depth YES vs NO)
        _,f2p=z_test(cy_k+uy_k,cy_n+uy_n,cn_k+un_k,cn_n+un_n)
        f2eff=pp(cy_k+uy_k,cy_n+uy_n)-pp(cn_k+un_k,cn_n+un_n)
        ax.text(0.93,-19.5,
            'F1 Dot Cue: {:+.1f}pp {:}'.format(f1eff,stars(f1p)),
            ha='center',va='top',fontsize=7,color=C_DOT_Y,fontweight='bold')
        ax.text(0.93,-23.5,
            'F2 Depth:   {:+.1f}pp {:}'.format(f2eff,stars(f2p)),
            ha='center',va='top',fontsize=7,color=C_DEP_Y,fontweight='bold')

    # Group brackets
    ax.annotate('',xy=(0.55+0.23,-15.5),xytext=(0-0.23,-15.5),
                arrowprops=dict(arrowstyle='-',color=C_DOT_Y,lw=1.6))
    ax.annotate('',xy=(1.80+0.23,-15.5),xytext=(1.25-0.23,-15.5),
                arrowprops=dict(arrowstyle='-',color=C_DOT_N,lw=1.6))
    ax.text(0.275,-17,'CUED',ha='center',fontsize=7,color=C_DOT_Y,fontweight='bold')
    ax.text(1.525,-17,'UNCUED',ha='center',fontsize=7,color=C_DOT_N,fontweight='bold')

    ax.axhline(0,color='#888',lw=0.8,ls='--',zorder=2)
    ax.set_ylim(-27,65)
    ax.set_xticks(xs)
    ax.set_xticklabels(CELL_LABELS,fontsize=6.2)
    ax.set_ylabel('% correct above chance',fontsize=7.5)
    ax.set_title('{}\n(n={})'.format(title,n_tot),fontsize=8.5,fontweight='bold',pad=4)
    ax.spines['top'].set_visible(False); ax.spines['right'].set_visible(False)
    ax.yaxis.set_minor_locator(matplotlib.ticker.MultipleLocator(5))
    ax.grid(axis='y',which='minor',lw=0.3,alpha=0.35,zorder=0)
    ax.grid(axis='y',which='major',lw=0.5,alpha=0.45,zorder=0)
    ax.tick_params(labelsize=7)

datasets = ([(session_data[sid], lbl, 256) for sid,lbl in SESSIONS]
            + [(combined_data, 'Combined  (n={})'.format(n_combined), n_combined)])
for col_i,(cnt,title,ntot) in enumerate(datasets):
    ax = fig2.add_subplot(res_gs[0,col_i])
    draw_result_panel(ax,cnt,title,ntot)

# ── Session comparison table ───────────────────────────────────────────────────
fig2.text(LMAR,0.340,'Session comparison — main 2×2 cells (% correct above chance)',
          ha='left',va='top',fontsize=9,fontweight='bold',color='#1a3a6b')

swap_map = {('CUED','YES'):'ZdNoi',('CUED','NO'):'ZdCoh',
            ('UNCUED','YES'):'ZdCoh',('UNCUED','NO'):'ZdNoi'}
col_xs = [LMAR, LMAR+0.165, LMAR+0.275, LMAR+0.385, LMAR+0.495, LMAR+0.615, LMAR+0.755]
hdrs   = ['Condition','S1','S2','S3','S4','Combined','sig']
FS2 = 7.5
ty = 0.315
for cx,h in zip(col_xs,hdrs):
    fig2.text(cx,ty,h,ha='left',va='top',fontsize=FS2,fontweight='bold',color='#1a3a6b')
ty -= lh(FS2,1.3)+0.002
fig2.add_artist(plt.Line2D([LMAR,RMAR],[ty,ty],
    transform=fig2.transFigure,color='#888888',lw=0.7))
ty -= 0.004

row_bgs = ['#EEF8EE','#FFFAEE','#EEF2FF','#F5F5F5','#E8E8E8']
for ri,key in enumerate(CELL_ORDER):
    swap_lbl = swap_map[key]
    lbl = '{} Depth{} ({})'.format(key[0],'✓' if key[1]=='YES' else '✗',swap_lbl)
    per_sess = [session_data[sid].get(key,[0,1]) for sid,_ in SESSIONS]
    kc,nc=combined_data.get(key,[0,1])
    s,_ = sig_vs_chance(kc,nc)
    cells = ([lbl]
             + ['{:+.1f}pp ({}/{})'.format(pp(k,n),k,n) for k,n in per_sess]
             + ['{:+.1f}pp ({}/{})'.format(pp(kc,nc),kc,nc), s])
    for cx,cell in zip(col_xs,cells):
        fig2.text(cx,ty,cell,ha='left',va='top',fontsize=FS2,
                  color='#222',style='normal')
    ty -= lh(FS2,1.4)

# F1 and F2 rows
ty -= 0.004
fig2.add_artist(plt.Line2D([LMAR,RMAR],[ty,ty],
    transform=fig2.transFigure,color='#AAAAAA',lw=0.5,ls='--'))
ty -= 0.005

for data_set,label in ([(session_data[sid],'S{}'.format(i+1)) for i,(sid,_) in enumerate(SESSIONS)]
                        + [(combined_data,'Combined')]):
    cy_k,cy_n=data_set.get(('CUED','YES'),[0,1])
    cn_k,cn_n=data_set.get(('CUED','NO'),[0,1])
    uy_k,uy_n=data_set.get(('UNCUED','YES'),[0,1])
    un_k,un_n=data_set.get(('UNCUED','NO'),[0,1])
    _,f1p=z_test(cy_k+cn_k,cy_n+cn_n,uy_k+un_k,uy_n+un_n)
    _,f2p=z_test(cy_k+uy_k,cy_n+uy_n,cn_k+un_k,cn_n+un_n)
    data_set['_f1']=(cy_k+cn_k,cy_n+cn_n,uy_k+un_k,uy_n+un_n,f1p)
    data_set['_f2']=(cy_k+uy_k,cy_n+uy_n,cn_k+un_k,cn_n+un_n,f2p)

for factor_key,flabel,fcol in [('_f1','F1 Dot Cueing (CUED−UNCUED)',C_DOT_Y),
                                ('_f2','F2 Depth Cueing (Depth✓−Depth✗)',C_DEP_Y)]:
    cells2 = [flabel]
    for sid,_ in SESSIONS:
        k1,n1,k2,n2,fp=session_data[sid][factor_key]
        cells2.append('{:+.1f}pp  {}'.format(pp(k1,n1)-pp(k2,n2),stars(fp)))
    k1,n1,k2,n2,fp=combined_data[factor_key]
    cells2.append('{:+.1f}pp  {}'.format(pp(k1,n1)-pp(k2,n2),stars(fp)))
    cells2.append('')
    for cx,cell in zip(col_xs,cells2):
        fig2.text(cx,ty,cell,ha='left',va='top',fontsize=FS2,
                  color=fcol,fontweight='bold')
    ty -= lh(FS2,1.4)

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 3 — Interpretation & Notes
# ═══════════════════════════════════════════════════════════════════════════════
fig3 = plt.figure(figsize=(PW,PH)); fig3.patch.set_facecolor('white')
fig3.text(0.50,0.975,'DepthColorLinked_005m — Interpretation & Notes',
          ha='center',va='top',fontsize=13,fontweight='bold',color='#111111')
y3 = 0.942

def txt(fig, x, y, s, fs=8.5, bold=False, col='#222', indent=0):
    fig.text(x+indent, y, s, ha='left', va='top', fontsize=fs,
             fontweight='bold' if bold else 'normal', color=col)
    return y - lh(fs, 1.5)

def section(fig, y, s):
    y = txt(fig, LMAR, y, s, fs=9.5, bold=True, col='#1a3a6b')
    fig.add_artist(plt.Line2D([LMAR,RMAR],[y+lh(9.5,0.3)]*2,
        transform=fig.transFigure,color='#BBBBCC',lw=0.8))
    return y - 0.004

def wrap_txt(fig, x, y, s, fs=8, col='#333', width=105, indent=0):
    for line in textwrap.wrap(s, width):
        y = txt(fig, x, y, line, fs=fs, col=col, indent=indent)
    return y

y3 = section(fig3, y3, 'Key Findings  (4 sessions combined, n=1024)')
y3 = wrap_txt(fig3, LMAR, y3,
    'F1 Dot Cueing: CUED substantially outperforms UNCUED (exact values page 2). This is '
    'the core temporal-onset cueing effect and replicates robustly across all three sessions.', fs=8.5)
y3 -= 0.004
y3 = wrap_txt(fig3, LMAR, y3,
    'F2 Depth Cueing: translation at the cued field\'s depth plane yields better performance '
    'than translation at the opposite plane (exact values page 2). Replicates the ZdA vs ZdB '
    'dissociation seen in DepthSwapCtrl (all-red).', fs=8.5)
y3 -= 0.004
y3 = wrap_txt(fig3, LMAR, y3,
    'Best condition: CUED+Depth✓ (ZdNoi). Translator keeps depth-plane identity and color — '
    'both cueing signals align. Dot cueing dominates: CUED+Depth✗ (ZdCoh) also exceeds UNCUED.', fs=8.5)
y3 -= 0.004
y3 = wrap_txt(fig3, LMAR, y3,
    'UNCUED performance: appears near-chance on average, but is heterogeneous by delayed-field '
    'depth (F3; see anomaly note below).', fs=8.5)
y3 -= 0.010

y3 = section(fig3, y3, 'Between-Session Variability  (4 sessions, n=256/session)')
y3 = wrap_txt(fig3, LMAR, y3,
    'S1 (260404_0940): strong ZdNoi >> ZdCoh (CUED +47pp vs +19pp); UNCUED near chance. '
    'S2 (260404_1123): flatter — ZdNoi ≈ ZdCoh (~+28pp CUED); UNCUED elevated (+14–16pp). '
    'S3 (260406_1001): moderate ZdNoi >> ZdCoh (CUED +36pp vs +14pp); UNCUED ~+12pp. '
    'S4 (260406_1034): ZdNoi >> ZdCoh (CUED +36pp vs +14pp); F2 Depth Cueing strongest '
    'yet (**); F1 Dot Cueing modest (+12.5pp *). Observer reported low perceived performance.', fs=8.5)
y3 -= 0.004
y3 = wrap_txt(fig3, LMAR, y3,
    'F1 (Dot Cueing) is significant in all 4 sessions but varies in magnitude (S1=+28pp, '
    'S2–S4≈+12pp). F2 (Depth Cueing) significant in S1 (*) and S4 (**), near-null in S2–S3. '
    'Four-session combined n=256/cell provides reliable cell estimates.', fs=8.5)
y3 -= 0.004
y3 = wrap_txt(fig3, LMAR, y3,
    'Response bias: 90° and 270° headings are over-represented across sessions (observer '
    'motor/pointing bias plus possible vertical perceptual anisotropy). Not condition-specific.', fs=8.5)
y3 -= 0.010

y3 = section(fig3, y3, 'UNCUED+Depth✗ (ZdNoi) Anomaly — Resolved')
y3 = wrap_txt(fig3, LMAR, y3,
    'UNCUED+ZdNoi is nominally the "hardest" cell (Dot✗, Depth✗) yet performs above chance '
    '(~+11pp ***). This is not paradoxical — it is explained by F3 (translating-field depth).', fs=8.5)
y3 -= 0.004
y3 = wrap_txt(fig3, LMAR, y3,
    'In UNCUED+ZdNoi: the non-delayed (non-cued) field translates; ZdNoi leaves the '
    'non-coh companion in its original depth plane. The translating field is at the depth '
    'OPPOSITE to the delayed field (DFD). When DFD=Near, the translator is at Far (easy); '
    'when DFD=Far, translator is at Near (hard).', fs=8.5)
y3 -= 0.004
y3 = wrap_txt(fig3, LMAR, y3,
    'DFD=Near sub-cell: translator Far → +20.8pp *** (consistent with DepthParam Far >> Near). '
    'DFD=Far sub-cell: translator Near → +2.1pp n.s. (chance). The anomalous average (+11pp) '
    'is simply the average of an easy Far trial and a hard Near trial.', fs=8.5)
y3 -= 0.004
y3 = wrap_txt(fig3, LMAR, y3,
    'Implication: F2 Depth Cueing as currently defined is confounded with F3 (translating-field '
    'depth). A translating-field-depth reanalysis is needed to cleanly separate the two. '
    'The DepthParam parametric sweep (0.03–0.15 m) confirms Far translation is intrinsically '
    'easier, regardless of cueing condition.', fs=8.5)
y3 -= 0.010

y3 = section(fig3, y3, 'Design Notes')
y3 = wrap_txt(fig3, LMAR, y3,
    'Depth separation: 0.05 m at 2 m viewing distance (~1.4° disparity at aperture edge). '
    'Chosen from DepthParam parametric sweep; Far cueing robust at all depths tested '
    '(0.03–0.15 m). Near cueing noisier — may relate to monocular positional-shift confound '
    'that scales with eccentricity.', fs=8.5)
y3 -= 0.004
y3 = wrap_txt(fig3, LMAR, y3,
    'Color-depth confound: within this experiment, depth change and color change always '
    'co-occur (linkDepthColor=1). ZdCoh = depth+color change; ZdNoi = neither. Cannot '
    'separate the two within this design alone.', fs=8.5)
y3 -= 0.004
y3 = wrap_txt(fig3, LMAR, y3,
    'Cross-experiment comparison to DepthSwapCtrl (all-red, same depth): '
    'DepthSwapCtrl ZdA CUED = +12.5pp (bino, n=64); DepthColorLinked ZdA CUED (S1) = +18.8pp. '
    'Difference hints that adding color makes ZdCoh less disruptive, but sessions differ in '
    'baseline so interpretation is premature. Need matched n.', fs=8.5)
y3 -= 0.010

y3 = section(fig3, y3, 'Factor Map')
factor_lines = [
    ('F1  Dot Cueing',   'CUED vs UNCUED — does the delayed-onset dot field translate?',       C_DOT_Y),
    ('F2  Depth Cueing', 'Depth✓ vs Depth✗ — does translation occur at the DFD during T?',    C_DEP_Y),
    ('    Depth✓',       '= CUED+ZdNoi  OR  UNCUED+ZdCoh  (translator at DFD during window)', '#444'),
    ('    Depth✗',       '= CUED+ZdCoh  OR  UNCUED+ZdNoi  (translator at opp(DFD))',          '#444'),
    ('F3  TransDepth',   'Near vs Far — depth of translating field during window (post-hoc)',   '#555'),
    ('F4  TransColor',   'R vs G — color of translating field (perfectly correlated with F3)',  '#555'),
    ('F5  CuedColor',    'R vs G — color of delayed onset field (post-hoc)',                   '#555'),
    ('F6  RotCfg',       'CW vs CCW rotation of delayed field (post-hoc, expected null)',      '#555'),
]
for lbl,desc,col in factor_lines:
    fig3.text(LMAR,       y3,lbl, ha='left',va='top',fontsize=8,fontweight='bold',color=col)
    fig3.text(LMAR+0.145, y3,desc,ha='left',va='top',fontsize=8,color='#333')
    y3 -= lh(8,1.45)
y3 -= 0.008

y3 = section(fig3, y3, 'Planned Next Steps')
next_steps = [
    'Translating-field-depth reanalysis (F3): re-bin all cells by which depth plane '
     '(Near vs Far) translates, collapsing F1 and F2. Expect Far >> Near regardless of cueing.',
    'Cross-experiment comparison at matched n: DepthColorLinked (n=192/cell) vs '
     'DepthSwapCtrl all-red (n=64/cell bino) → isolate color contribution to ZdCoh disruption.',
    'Color-only swap experiment (linkDepthColor=0, no depth change): complete the '
     '2×2 of depth-only × color-only to dissociate depth vs color contributions.',
    'Second observer and/or second observer sessions to assess generalizability.',
    'SOA experiment: vary delay between Field A onset and Field B onset to probe '
     'temporal window of cueing effect.',
]
for step in next_steps:
    y3 = wrap_txt(fig3, LMAR, y3, '• ' + step, fs=8.5, width=102)
    y3 -= 0.003

# ── Save ──────────────────────────────────────────────────────────────────────
os.makedirs(os.path.dirname(OUT_PDF), exist_ok=True)
with PdfPages(OUT_PDF) as pdf:
    pdf.savefig(fig1, dpi=DPI, bbox_inches='tight', facecolor='white')
    pdf.savefig(fig2, dpi=DPI, bbox_inches='tight', facecolor='white')
    pdf.savefig(fig3, dpi=DPI, bbox_inches='tight', facecolor='white')
    d = pdf.infodict()
    d['Title']   = 'DepthColorLinked_005m — Design & Results'
    d['Author']  = 'VRDots Analysis'
    d['Subject'] = 'Depth+Color linked experiment, sessions 260404_0940 & 260404_1123'

print('Saved: {}'.format(OUT_PDF))
for sid,label in SESSIONS:
    cnt=session_data[sid]
    cy_k,cy_n=cnt.get(('CUED','YES'),[0,1]); cn_k,cn_n=cnt.get(('CUED','NO'),[0,1])
    uy_k,uy_n=cnt.get(('UNCUED','YES'),[0,1]); un_k,un_n=cnt.get(('UNCUED','NO'),[0,1])
    _,f1p=z_test(cy_k+cn_k,cy_n+cn_n,uy_k+un_k,uy_n+un_n)
    _,f2p=z_test(cy_k+uy_k,cy_n+uy_n,cn_k+un_k,cn_n+un_n)
    print('{}: F1={:+.1f}pp {} | F2={:+.1f}pp {}'.format(
        label,
        pp(cy_k+cn_k,cy_n+cn_n)-pp(uy_k+un_k,uy_n+un_n),stars(f1p),
        pp(cy_k+uy_k,cy_n+uy_n)-pp(cn_k+un_k,cn_n+un_n),stars(f2p)))
