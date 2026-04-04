#!/usr/bin/env python3
"""
depth_color_design_writeup.py
Design document for the Depth+Color experiment (ZdCoh / ZdNoi / N).

Page 1 — Trajectory figure: all three swap conditions with depth-color coding
Page 2 — Permutation table (48 trial types) + factor summary + key comparisons

Output: Agents/WriteUps/depth_color_design.pdf
"""

import os, csv, textwrap
from itertools import product
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.lines as mlines
import matplotlib.patches as mpatches
from matplotlib.backends.backend_pdf import PdfPages

OUT_PDF = os.path.expanduser(
    "~/Projects/ObjectBasedAttention/VRDots/Agents/WriteUps/depth_color_design.pdf")

PW, PH = 8.5, 11; DPI = 150
LMAR, RMAR = 0.09, 0.91; TXT_W = RMAR - LMAR
WRAP_W = 115

def lh(pt, spacing=1.55):
    return (pt / 72 * DPI * spacing) / (PH * DPI)

# ── Timing & colours ──────────────────────────────────────────────────────────
T_A=0.00; T_B=0.490; T_S=0.686; T_E=0.739; T_TOT=1.00
CW=2.0; TRANS_COH=1.0; TRANS_NOI=1.5; CCW=0.0
NEAR_Y=0.0; FAR_Y=1.0; EPS=1e-4

C_NEAR='#CC3333'; C_FAR='#228B22'   # Red=Near, Green=Far
C_TRANS='#CCCCCC'; C_FRAME='#333333'

# Swap-condition label colours
C_N='#444488'; C_ZDCOH='#883300'; C_ZDNOI='#226622'

SWAP_DEFS = [
    ('ZdCoh', 'ZdCoh',        C_ZDCOH),
    ('ZdNoi', 'ZdNoi',        C_ZDNOI),
]
COL_TITLES = ['Near Translation', 'Far Translation']
CW_DEPTHS  = ['N', 'F']

_base   = np.linspace(T_A+0.01, T_TOT-0.01, 14)
T_MARKS = np.unique(np.sort(np.concatenate([_base, [(T_S+T_E)/2]])))

SF = {'S0':('o',5.5,True),'S1':('s',9.0,False),'S2':('^',6.0,True),'S3':('D',8.5,False)}

def _opp(c): return C_FAR if c==C_NEAR else C_NEAR

def _sf_colors(swap, cw_dep):
    """Return (pre, post) colour dicts for each subfield."""
    cw_c = C_NEAR if cw_dep=='N' else C_FAR
    cc_c = _opp(cw_c)
    pre = {'S0':cw_c,'S1':cw_c,'S2':cc_c,'S3':cc_c}
    if swap=='N':
        post = dict(pre)
    elif swap=='ZdCoh':   # S0 and S2 swap
        post = {'S0':cc_c,'S1':cw_c,'S2':cw_c,'S3':cc_c}
    else:                 # ZdNoi: S1 and S3 swap
        post = {'S0':cw_c,'S1':cc_c,'S2':cc_c,'S3':cw_c}
    return pre, post

def _plot2c(ax, name, tk, vk, tq, c_pre, c_post):
    """Draw a subfield track with a colour change at T_S."""
    mk, ms, filled = SF[name]; mew = 1.0 if filled else 1.6
    ax.plot(tk, vk, color=c_pre, lw=0.9, solid_capstyle='round', zorder=3)
    if c_pre != c_post:
        v_ts = float(np.interp(T_S, tk, vk))
        tk_p = np.concatenate([[T_S], tk[tk>T_S]]); vk_p = np.concatenate([[v_ts], vk[tk>T_S]])
        if len(tk_p)>=2:
            ax.plot(tk_p, vk_p, color=c_post, lw=0.9, solid_capstyle='round', zorder=4)
    for tq_s, c in [(tq[tq<T_S], c_pre),(tq[tq>=T_S], c_post)]:
        if len(tq_s)==0: continue
        mfc = c if filled else 'none'
        ax.plot(tq_s, np.interp(tq_s,tk,vk), marker=mk, ms=ms, mew=mew,
                mfc=mfc, mec=c, ls='none', zorder=5)

def _traj(swap, is_cued):
    """Motion trajectories. N differs from ZdCoh/ZdNoi (no group reassignment)."""
    t0=T_B if is_cued else T_A; t2=T_A if is_cued else T_B
    tS0=np.array([t0,T_S,T_S,T_E,T_E,T_TOT]); vS0=np.array([CW,CW,TRANS_COH,TRANS_COH,CW,CW])
    tS2=np.array([t2,T_TOT]);                    vS2=np.array([CCW,CCW])
    if swap=='N':
        tS1=np.array([t0,T_S,T_S,T_E,T_E,T_TOT]); vS1=np.array([CW,CW,TRANS_NOI,TRANS_NOI,CW,CW])
        tS3=np.array([t2,T_TOT]);                    vS3=np.array([CCW,CCW])
    else:   # ZdCoh & ZdNoi have identical motion (group reassignment identical)
        tS1=np.array([t0,T_S-EPS,T_S,T_TOT]);              vS1=np.array([CW,CW,CCW,CCW])
        tS3=np.array([t2,T_S-EPS,T_S,T_E,T_E,T_TOT]); vS3=np.array([CCW,CCW,TRANS_NOI,TRANS_NOI,CW,CW])
    return tS0,vS0,tS1,vS1,tS2,vS2,tS3,vS3

def _depth_tracks(swap, is_cued, cw_dep):
    cwy=NEAR_Y if cw_dep=='N' else FAR_Y; ccy=_opp_y=FAR_Y if cw_dep=='N' else NEAR_Y
    t0=T_B if is_cued else T_A; t2=T_A if is_cued else T_B
    flat = lambda t,y: (np.array([t,T_TOT]),np.array([y,y]))
    step = lambda t,y0,y1: (np.array([t,T_S-EPS,T_S,T_TOT]),np.array([y0,y0,y1,y1]))
    if swap=='N':
        return flat(t0,cwy),flat(t0,cwy),flat(t2,ccy),flat(t2,ccy)
    elif swap=='ZdCoh':
        return step(t0,cwy,ccy),flat(t0,cwy),step(t2,ccy,cwy),flat(t2,ccy)
    else:  # ZdNoi
        return flat(t0,cwy),step(t0,cwy,ccy),flat(t2,ccy),step(t2,ccy,cwy)

def _ax_style_motion(ax, show_labels=False):
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

def _ax_style_depth(ax):
    ax.set_xlim(T_A-.01,T_TOT+.01); ax.set_ylim(-0.5,1.5)
    ax.set_xticks([]); ax.set_yticks([NEAR_Y,FAR_Y])
    ax.set_yticklabels(['N','F'],fontsize=4.5); ax.tick_params(axis='y',length=2,pad=1)
    ax.axvspan(T_S,T_E,color=C_TRANS,alpha=0.6,zorder=1)
    ax.axvline(T_B,color='#AAAAAA',lw=0.7,ls='--',zorder=2)
    for sp in ax.spines.values(): sp.set_linewidth(0.6); sp.set_edgecolor(C_FRAME)

def draw_motion(ax, swap, is_cued, cw_dep, show_labels=False):
    tS0,vS0,tS1,vS1,tS2,vS2,tS3,vS3 = _traj(swap, is_cued)
    pre,post = _sf_colors(swap, cw_dep)
    t0=T_B if is_cued else T_A; t2=T_A if is_cued else T_B
    m0=T_MARKS[T_MARKS>=t0]; m2=T_MARKS[T_MARKS>=t2]
    for nm,tk,vk,mq in [('S0',tS0,vS0,m0),('S1',tS1,vS1,m0),
                         ('S2',tS2,vS2,m2),('S3',tS3,vS3,m2)]:
        _plot2c(ax,nm,tk,vk,mq,pre[nm],post[nm])
    _ax_style_motion(ax, show_labels)

def draw_depth(ax, swap, is_cued, cw_dep):
    (ts0,vs0),(ts1,vs1),(ts2,vs2),(ts3,vs3) = _depth_tracks(swap,is_cued,cw_dep)
    pre,post = _sf_colors(swap, cw_dep)
    t0=T_B if is_cued else T_A; t2=T_A if is_cued else T_B
    for nm,tk,vk,ton in [('S0',ts0,vs0,t0),('S1',ts1,vs1,t0),
                          ('S2',ts2,vs2,t2),('S3',ts3,vs3,t2)]:
        tq=T_MARKS[T_MARKS>=ton]
        _plot2c(ax,nm,tk,vk,tq,pre[nm],post[nm])
    _ax_style_depth(ax)

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 1 — Trajectories
# ═══════════════════════════════════════════════════════════════════════════════
fig1 = plt.figure(figsize=(PW,PH)); fig1.patch.set_facecolor('white')
y = 0.970

fig1.text(0.50, y, 'Depth + Color Design — ZdCoh / ZdNoi',
          ha='center', va='top', fontsize=13, fontweight='bold', color='#111111')
y -= lh(13,1.3)+0.006

# Two primary factors
C_DOT_Y = '#1a6b1a'   # green: dot cued ✓
C_DOT_N = '#666666'   # gray:  dot uncued ✗
C_DEP_Y = '#1a3a8b'   # blue:  depth match ✓
C_DEP_N = '#aa2222'   # red:   depth mismatch ✗

fig1.text(0.50, y,
    'Factor 1 — Dot Cueing  (✓/✗):    does the delayed-onset dot field translate?',
    ha='center', va='top', fontsize=7.8, fontweight='bold', color=C_DOT_Y)
y -= lh(7.8,1.3)
fig1.text(0.50, y,
    'Factor 2 — Depth Cueing (✓/✗):   does translation occur at the depth where the cued field appeared?',
    ha='center', va='top', fontsize=7.8, fontweight='bold', color=C_DEP_Y)
y -= lh(7.8,1.3)+0.004
fig1.text(0.50, y,
    'Near = Red  ·  Far = Green  ·  '
    'Filled = coherent (S0●, S2▲)  ·  Open = noise (S1□, S3◇)  ·  '
    'Color changes at T\u209B for swapping subfields',
    ha='center', va='top', fontsize=7, color='#555555')
y -= lh(7,1.3)+0.008

# 4 conditions ordered as 2×2 of (Dot Cueing) × (Depth Cueing)
# (swap, is_cued, dot_ok, depth_ok, detail)
COND_DEFS = [
    ('ZdNoi', True,  True,  True,  'CUED + ZdNoi'),
    ('ZdCoh', True,  True,  False, 'CUED + ZdCoh'),
    ('ZdCoh', False, False, True,  'UNCUED + ZdCoh'),
    ('ZdNoi', False, False, False, 'UNCUED + ZdNoi'),
]
# Subtle row background tints: both-cued=green, dot-only=gold, depth-only=blue, neither=gray
COND_BG = ['#EEF8EE', '#FFFAEE', '#EEF2FF', '#F5F5F5']

TRAJ_BOT = 0.040
traj_gs = gridspec.GridSpec(8, 2,
    top=y, bottom=TRAJ_BOT+0.025,
    left=0.215, right=0.865,
    height_ratios=[3,1]*4,
    hspace=0.08, wspace=0.22)

for ci, (ctitle, cw_dep) in enumerate(zip(COL_TITLES, CW_DEPTHS)):
    for ri, (swap, is_cued, dot_ok, depth_ok, detail) in enumerate(COND_DEFS):
        ax_m = fig1.add_subplot(traj_gs[ri*2, ci])
        ax_m.set_facecolor(COND_BG[ri])
        draw_motion(ax_m, swap, is_cued, cw_dep, show_labels=(ri==0 and ci==0))
        if ri == 0:
            ax_m.set_title(ctitle, fontsize=8.5, fontweight='bold', pad=3)

        ax_d = fig1.add_subplot(traj_gs[ri*2+1, ci])
        ax_d.set_facecolor(COND_BG[ri])
        draw_depth(ax_d, swap, is_cued, cw_dep)

        if ci == 0:
            ax_m.set_ylabel(
                'Dot ✓  CUED' if dot_ok else 'Dot ✗  UNCUED',
                fontsize=6.5, fontweight='bold', labelpad=3,
                color=C_DOT_Y if dot_ok else C_DOT_N)
            ax_d.set_ylabel(
                'Depth ✓' if depth_ok else 'Depth ✗',
                fontsize=6.0, fontweight='bold', labelpad=3,
                color=C_DEP_Y if depth_ok else C_DEP_N)

# Right-side mechanism labels + group separators (computed after all subplots added)
for ri, (swap, is_cued, dot_ok, depth_ok, detail) in enumerate(COND_DEFS):
    pos_m = traj_gs[ri*2,   1].get_position(fig1)
    pos_d = traj_gs[ri*2+1, 1].get_position(fig1)
    mid_y = (pos_m.y1 + pos_d.y0) / 2
    fig1.text(0.870, mid_y, detail, ha='left', va='center', fontsize=6.5,
              fontweight='bold', color=C_ZDCOH if swap=='ZdCoh' else C_ZDNOI)

# Separator between Dot Cued group (rows 0-1) and Dot Uncued group (rows 2-3)
bot_cued   = traj_gs[3, 0].get_position(fig1).y0
top_uncued = traj_gs[4, 0].get_position(fig1).y1
sep_y = (bot_cued + top_uncued) / 2
fig1.add_artist(plt.Line2D([0.06, 0.94], [sep_y, sep_y],
    transform=fig1.transFigure, color='#888888', lw=1.2))

# Group bracket labels on far left
for rows, label, col in [
    ((0, 3), 'DOT\nCUED',   C_DOT_Y),
    ((4, 7), 'DOT\nUNCUED', C_DOT_N),
]:
    top = traj_gs[rows[0], 0].get_position(fig1).y1
    bot = traj_gs[rows[1], 0].get_position(fig1).y0
    fig1.text(0.055, (top+bot)/2, label, ha='center', va='center',
              fontsize=7.5, fontweight='bold', color=col, rotation=90)

print(f"Page 1 traj bottom: {TRAJ_BOT:.3f}")

# Trajectory legend
leg_h = [
    mlines.Line2D([],[],color=C_NEAR,marker='o',ms=5,mew=1.0,mfc=C_NEAR,ls='none',label='S0● coh  (Near=Red)'),
    mlines.Line2D([],[],color=C_NEAR,marker='s',ms=7,mew=1.4,mfc='none',ls='none',label='S1□ noise (Near=Red)'),
    mlines.Line2D([],[],color=C_FAR, marker='^',ms=5.5,mew=1.0,mfc=C_FAR, ls='none',label='S2▲ coh  (Far=Green)'),
    mlines.Line2D([],[],color=C_FAR, marker='D',ms=7,mew=1.4,mfc='none',ls='none',label='S3◇ noise (Far=Green)'),
    mpatches.Patch(facecolor=C_TRANS,alpha=0.8,edgecolor='#888',label='Translation window'),
]
ax_tl=fig1.add_axes([LMAR,TRAJ_BOT-0.002,TXT_W,0.025]); ax_tl.axis('off')
ax_tl.legend(handles=leg_h,loc='center',ncol=5,fontsize=6.5,
             frameon=True,framealpha=0.9,edgecolor='#CCC')

print(f"Page 1 traj bottom: {TRAJ_BOT:.3f}")

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 2 — Permutation table + Factor summary + Key comparisons
# ═══════════════════════════════════════════════════════════════════════════════
fig2 = plt.figure(figsize=(PW,PH)); fig2.patch.set_facecolor('white')
y = 0.970

fig2.text(0.50,y,'Depth + Color Design — Permutations & Analysis Framework',
          ha='center',va='top',fontsize=12,fontweight='bold',color='#111111')
y -= lh(12,1.3)+0.008

# ── Permutation table ──────────────────────────────────────────────────────────
fig2.text(LMAR,y,'Trial-type permutations (32 = 2 swap types × 4 binary variables × 8 TransDeg; N baseline dropped — see prior experiments)',
          ha='left',va='top',fontsize=8.5,fontweight='bold',color='#1a3a6b')
y -= lh(8.5,1.4)+0.003

# Generate rows
def opp_dep(d): return 'F' if d=='N' else 'N'
def opp_clr(c): return 'G' if c=='R' else 'R'
def del_rot(rc): return 'CCW' if rc==0 else 'CW'
def nondel_rot(rc): return 'CW' if rc==0 else 'CCW'
def identity_preserved(swap): return 'YES' if swap=='ZdNoi' else 'NO'

perm_rows = []
n=0
for swap,cond,dfd,nc,rc in product(['ZdCoh','ZdNoi'],
                                    ['CUED','UNCUED'],['N','F'],['R','G'],[0,1]):
    n+=1
    fc=opp_clr(nc)
    tdep  = dfd if cond=='CUED' else opp_dep(dfd)
    tclr  = nc  if tdep=='N' else fc
    trot  = del_rot(rc) if cond=='CUED' else nondel_rot(rc)
    cclr  = nc  if dfd=='N' else fc
    idpre = identity_preserved(swap)
    perm_rows.append((n,swap,cond,dfd,nc,rc,tdep,tclr,trot,cclr,idpre))

# Draw table header
FS=6.5
col_x = [LMAR, LMAR+0.034, LMAR+0.090, LMAR+0.152, LMAR+0.198,
          LMAR+0.238, LMAR+0.280, LMAR+0.320, LMAR+0.368,
          LMAR+0.418, LMAR+0.462, LMAR+0.515]
hdrs   = ['#','Swap','Cond','DFD','NClr','Rc',
          'TrDep','TrClr','TrRot','CuClr','IdPrsv',
          'F1 / F2 / F3 / F4 / F5 / F6']

for cx,hdr in zip(col_x,hdrs):
    fig2.text(cx,y,hdr,ha='left',va='top',fontsize=FS,
              fontweight='bold',color='#1a3a6b')
y -= lh(FS,1.3)+0.001
fig2.add_artist(plt.Line2D([LMAR,RMAR],[y,y],
    transform=fig2.transFigure,color='#888888',lw=0.8))
y -= 0.003

# Colours for swap sections
swap_bg = {'N':'#EEEEFF','ZdCoh':'#FFF3EE','ZdNoi':'#EEFFEE'}
swap_fc = {'N':C_N,'ZdCoh':C_ZDCOH,'ZdNoi':C_ZDNOI}
row_h = lh(FS,1.25)

for nr,swap,cond,dfd,nc,rc,tdep,tclr,trot,cclr,idpre in perm_rows:
    f_str = (f"{cond[:2]}  {tdep}  {tclr}  {trot[:3]}  {cclr}  "
             f"{'Y' if idpre=='YES' else 'N'}")
    row_vals = [str(nr),swap,cond,dfd,nc,str(rc),tdep,tclr,trot,cclr,idpre,f_str]
    tc = swap_fc[swap]
    for cx,val in zip(col_x,row_vals):
        fig2.text(cx,y,val,ha='left',va='top',fontsize=FS,color=tc)
    y -= row_h
    if nr == 16:   # separator between ZdCoh and ZdNoi
        fig2.add_artist(plt.Line2D([LMAR,RMAR],[y,y],
            transform=fig2.transFigure,color='#BBBBBB',lw=0.5,ls='--'))
        y -= 0.003

y -= 0.004
fig2.add_artist(plt.Line2D([LMAR,RMAR],[y,y],
    transform=fig2.transFigure,color='#888888',lw=0.8))
y -= 0.010

print(f"Page 2 table bottom: {y:.3f}")

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 3 — Factor summary + Key comparisons
# ═══════════════════════════════════════════════════════════════════════════════
fig3 = plt.figure(figsize=(PW,PH)); fig3.patch.set_facecolor('white')
fig3.text(0.50,0.975,'Depth + Color Design — Analysis Framework',
          ha='center',va='top',fontsize=12,fontweight='bold',color='#111111')
y = 0.945

# ── Abbreviations glossary ─────────────────────────────────────────────────────
fig3.text(LMAR,y,'Abbreviations',ha='left',va='top',
          fontsize=9,fontweight='bold',color='#1a3a6b')
y -= lh(9,1.4)+0.002

# Two-column layout: left col = design variables, right col = derived + subfields
COL2 = LMAR + 0.44

ABBREV_LEFT = [
    ('Design variables (trial parameters)', None),
    ('Swap',    'ZdCoh / ZdNoi — which subfields swap depth+color at T\u209B'),
    ('Cond',    'CUED: delayed-onset field translates  |  UNCUED: it does not'),
    ('DFD',     'Delayed Field Depth — depth plane of the onset-cued field (N=Near, F=Far)'),
    ('NClr',    'NearColor — color assigned to Near plane (R=Red, G=Green; Far gets the other)'),
    ('Rc',      'RotConfig — 0: delayed field rotates CCW  |  1: delayed field rotates CW'),
]
ABBREV_RIGHT = [
    ('Derived analysis variables', None),
    ('TrDep',   'Translator Depth — depth plane of the translating field'),
    ('TrClr',   'Translator Color — pre-swap color of translating field'),
    ('TrRot',   'Translator Rotation direction (CW / CCW)'),
    ('CuClr',   'Cued Color — color of the delayed (onset-cued) field'),
    ('IdPrsv',  'Identity Preserved — YES (ZdNoi): translator keeps depth+color after T\u209B; NO (ZdCoh): it changes'),
    ('', ''),
    ('Subfields (4 per trial)', None),
    ('S0\u25cf', 'Coherent CW — the translating field in CUED trials'),
    ('S1\u25a1', 'Noise CW'),
    ('S2\u25b2', 'Coherent CCW — the translating field in UNCUED trials'),
    ('S3\u25c7', 'Noise CCW'),
    ('', ''),
    ('Swap conditions', None),
    ('ZdCoh', 'Coherent subfields S0+S2 swap depth+color at T\u209B; '
              'translator (S0 in CUED) changes identity'),
    ('ZdNoi', 'Noise subfields S1+S3 swap depth+color at T\u209B; '
              'translator (S0 in CUED) retains its depth+color identity'),
]

y0_abbrev = y
for abbr,desc in ABBREV_LEFT:
    if desc is None:
        fig3.text(COL2-0.01,y,abbr,ha='right',va='top',fontsize=7,
                  fontweight='bold',color='#333333')
        y -= lh(7,1.4)
    else:
        fig3.text(LMAR,y,abbr,ha='left',va='top',fontsize=6.8,
                  fontweight='bold',color='#444444')
        for ln in textwrap.wrap(desc, width=54):
            fig3.text(LMAR+0.065,y,ln,ha='left',va='top',fontsize=6.5,color='#555555')
            y -= lh(6.5,1.3)

y_right = y0_abbrev
for abbr,desc in ABBREV_RIGHT:
    if desc is None:
        fig3.text(RMAR,y_right,abbr,ha='right',va='top',fontsize=7,
                  fontweight='bold',color='#333333')
        y_right -= lh(7,1.4)
    elif abbr == '':
        y_right -= lh(6.5,1.0)
    else:
        fig3.text(COL2,y_right,abbr,ha='left',va='top',fontsize=6.8,
                  fontweight='bold',color='#444444')
        for ln in textwrap.wrap(desc, width=52):
            fig3.text(COL2+0.065,y_right,ln,ha='left',va='top',fontsize=6.5,color='#555555')
            y_right -= lh(6.5,1.3)

y = min(y, y_right) - 0.008
fig3.add_artist(plt.Line2D([LMAR,RMAR],[y,y],
    transform=fig3.transFigure,color='#AAAAAA',lw=0.7))
y -= 0.010

# ── Factor summary ─────────────────────────────────────────────────────────────
fig3.text(LMAR,y,'Factor Summary',ha='left',va='top',
          fontsize=9,fontweight='bold',color='#1a3a6b')
y -= lh(9,1.4)+0.003

FACTORS = [
    ('F1','Dot-field cueing','CUED vs UNCUED',
     'Temporal-onset cueing effect. The primary question: does the delayed '
     'onset advantage survive the depth+color swap?'),
    ('F2','Translator depth','Near vs Far (= TransDepth)',
     'Is Near or Far translation easier? Orthogonal to F3 '
     '(each depth is equally often R or G via NearColor counterbalancing). '
     'Depth and color ARE separable within this experiment.'),
    ('F3','Translator color','Red vs Green (pre-swap)',
     'Does the pre-swap color of the translating field affect performance? '
     'Directly tests the red/green asymmetry hypothesis from DepthSwapCtrl.'),
    ('F4','Translator rotation','CW vs CCW',
     'Expected null. Included for completeness.'),
    ('F5','Cued-field color','R vs G (= color of delayed field)',
     'In CUED: equals F3 (same field). In UNCUED: diverges from F3 — '
     'cued field is not the translator. Tests whether the observer\'s '
     'color-based attention bias affects UNCUED performance.'),
    ('F6','Field-identity cueing','ZdNoi vs ZdCoh (IdPrsv = Y vs N)',
     'The new factor enabled by including ZdNoi. ZdNoi preserves '
     'the cued translator\'s depth+color; ZdCoh disrupts it. '
     'The ZdNoi − ZdCoh cueing difference = benefit of stable '
     'depth+color identity for the cued translator. '
     'This is the depth+color FIELD-IDENTITY cueing effect.'),
]

for fname,flabel,fvals,fdesc in FACTORS:
    fig3.text(LMAR,y,f'{fname}  {flabel}  [{fvals}]',
              ha='left',va='top',fontsize=7.5,fontweight='bold',color='#222222')
    y -= lh(7.5,1.3)
    for ln in textwrap.wrap(fdesc,width=WRAP_W):
        fig3.text(LMAR+0.012,y,ln,ha='left',va='top',fontsize=7,color='#444444')
        y -= lh(7,1.3)
    y -= 0.003

y -= 0.005
fig3.add_artist(plt.Line2D([LMAR,RMAR],[y,y],
    transform=fig3.transFigure,color='#AAAAAA',lw=0.7))
y -= 0.008

# ── Key comparisons table ──────────────────────────────────────────────────────
fig3.text(LMAR,y,'Key Within-Experiment Comparisons',ha='left',va='top',
          fontsize=9,fontweight='bold',color='#1a3a6b')
y -= lh(9,1.4)+0.003

COMPS = [
    ('N  vs  ZdCoh',
     'Total (depth+color) identity contribution to cueing. '
     'ZdCoh removes BOTH depth AND color as post-T\u209B field-identity cues. '
     'Any cueing that survives in ZdCoh is pure temporal-onset (dot) cueing.'),
    ('N  vs  ZdNoi',
     'Cost of disrupting the NOISE group\'s depth+color identity, '
     'while the translator itself remains in its original plane and color. '
     'If ZdNoi ≈ N, noise-group stability does not matter. '
     'If ZdNoi < N, even peripheral disruption hurts tracking.'),
    ('ZdCoh  vs  ZdNoi  (= F6)',
     'The critical dissociation: matched disruption count, different which subfields. '
     'ZdNoi − ZdCoh = benefit of keeping the TRANSLATOR in a stable '
     'depth+color identity. Directly answers: is depth+color field-identity '
     'cueing driven by the translator specifically, or by the group as a whole?'),
    ('F1 × F6  (Cuing × IdPrsv)',
     'Is the CUED>UNCUED advantage larger when translator identity is preserved '
     '(ZdNoi) than disrupted (ZdCoh)? This interaction is the core measure '
     'of depth+color field-identity cueing.'),
    ('Cross-experiment: ZdCoh+color  vs  ZdA+all-red (existing)',
     'Isolates the COLOR contribution specifically: same disruption pattern, '
     'different whether color also changes. Requires the current data vs prior DepthSwapCtrl.'),
]

for comp,desc in COMPS:
    fig3.text(LMAR,y,comp,ha='left',va='top',fontsize=7.5,
              fontweight='bold',color='#333333')
    y -= lh(7.5,1.3)
    for ln in textwrap.wrap(desc,width=WRAP_W):
        fig3.text(LMAR+0.012,y,ln,ha='left',va='top',fontsize=7,color='#444444')
        y -= lh(7,1.3)
    y -= 0.003

print(f"Page 3 bottom: {y:.3f}")

# ── Save ───────────────────────────────────────────────────────────────────────
with PdfPages(os.path.expanduser(OUT_PDF)) as pdf:
    pdf.savefig(fig1,dpi=DPI,facecolor='white')
    pdf.savefig(fig2,dpi=DPI,facecolor='white')
    pdf.savefig(fig3,dpi=DPI,facecolor='white')
print(f"Saved: {OUT_PDF}")
