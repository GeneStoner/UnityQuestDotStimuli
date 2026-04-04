#!/usr/bin/env python3
"""
depth_color_biases_fig.py
Near/Far translation bias and Red/Green color bias in DepthColorLinked_005m.
Combined sessions 260404_0940 + 260404_1123 (n=512).

Output: Agents/Figures/depth_color_biases.png
"""

import csv, collections, os, math
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.ticker
import matplotlib.patches as mpatches
import matplotlib.lines as mlines
import textwrap

DATA_DIR = os.path.expanduser('~/Library/Application Support/ThatsRandom/VRDotsDataFiles')
OUT_PATH = os.path.expanduser(
    '~/Projects/ObjectBasedAttention/VRDots/Agents/Figures/depth_color_biases.png')
SESSIONS = ['260404_0940', '260404_1123']
CHANCE = 1/8

# ── Stats ─────────────────────────────────────────────────────────────────────
def normal_cdf(x): return 0.5*(1+math.erf(x/math.sqrt(2)))
def z_test(k1,n1,k2,n2):
    p1,p2=k1/n1,k2/n2; pp=(k1+k2)/(n1+n2)
    se=math.sqrt(max(pp*(1-pp)*(1/n1+1/n2),1e-12))
    z=(p1-p2)/se; return z,1-normal_cdf(z)
def wilson_ci(k,n,z=1.96):
    p=k/n; d=1+z**2/n; c=(p+z**2/(2*n))/d
    hw=z*math.sqrt(p*(1-p)/n+z**2/(4*n**2))/d
    return (c-hw-CHANCE)*100,(c+hw-CHANCE)*100
def stars(p): return '***' if p<.001 else '**' if p<.01 else '*' if p<.05 else '†' if p<.1 else 'n.s.'
def pp(k,n): return (k/n-CHANCE)*100 if n>0 else 0.0

# ── Colors ────────────────────────────────────────────────────────────────────
C_NEAR   = '#CC3333';  C_FAR    = '#228B22'
C_DEP_Y  = '#1a3a8b';  C_DEP_N  = '#aa2222'
C_DOT_Y  = '#1a6b1a';  C_DOT_N  = '#666666'
C_RED_T  = '#CC3333';  C_GRN_T  = '#228B22'

# ── Data loading ──────────────────────────────────────────────────────────────
def is_correct(td,rd):
    d=(float(rd)-float(td)+360)%360; return (360-d if d>180 else d)<=22.5
def depth_cue_yes(cond,swap): return (cond=='CUED') != (swap=='ZdA')
def trans_depth(cond,swap,dfd):
    return dfd if depth_cue_yes(cond,swap) else ('F' if dfd=='N' else 'N')
def trans_color(cond,swap,dfd,dfc):
    tdep=trans_depth(cond,swap,dfd)
    return dfc if tdep==dfd else ('G' if dfc=='R' else 'R')

cnt = collections.defaultdict(lambda:[0,0])
for sid in SESSIONS:
    path=os.path.join(DATA_DIR,'vr_dots_session_{}.tsv'.format(sid))
    for r in csv.DictReader(open(path),delimiter='\t'):
        if r.get('EndKey','') in ('timeout','skip','requeue'): continue
        td=r.get('TransDeg',''); rd=r.get('RespDeg','')
        if not td or not rd: continue
        cond=r['Cond']; swap=r['SwapType']
        dfd=r['DelayedFieldDepth']; dfc=r['DelayedFieldColor']
        corr=int(is_correct(td,rd))
        dep_cue='YES' if depth_cue_yes(cond,swap) else 'NO'
        tdep=trans_depth(cond,swap,dfd)
        tclr=trans_color(cond,swap,dfd,dfc)
        for key in [
            (cond,dep_cue,'tdep',tdep),(cond,dep_cue,'tclr',tclr),
            ('ALL','ALL','tdep',tdep),  ('ALL','ALL','tclr',tclr),
        ]:
            cnt[key][0]+=corr; cnt[key][1]+=1

def get(cond,dep,fac,val):
    return cnt.get((cond,dep,fac,val),[0,1])

# ── Figure ────────────────────────────────────────────────────────────────────
fig = plt.figure(figsize=(14,10))
fig.patch.set_facecolor('white')

fig.text(0.5,0.978,
    'DepthColorLinked_005m — Near/Far and Red/Green Biases  (n=512, sessions 260404_0940+1123)',
    ha='center',va='top',fontsize=12,fontweight='bold',color='#111')
fig.text(0.5,0.956,
    'Translating-field-depth convention throughout  ·  Error bars = 95% Wilson CI  ·  '
    'Significance brackets = Near vs Far (or Red vs Green) within each cell',
    ha='center',va='top',fontsize=8,color='#555')

gs = gridspec.GridSpec(2,3,top=0.92,bottom=0.30,
                       left=0.07,right=0.97,hspace=0.52,wspace=0.38)

CELLS = [
    ('CUED','YES','CUED\nDepth✓\n(ZdNoi)',C_DEP_Y,1.0),
    ('CUED','NO', 'CUED\nDepth✗\n(ZdCoh)',C_DEP_N,1.0),
    ('ALL', 'ALL','ALL\nconditions', '#555555',0.85),
    ('UNCUED','YES','UNCUED\nDepth✓\n(ZdCoh)',C_DEP_Y,0.55),
    ('UNCUED','NO', 'UNCUED\nDepth✗\n(ZdNoi)',C_DEP_N,0.55),
]
CELL_POSITIONS = [(0,0),(0,1),(0,2),(1,0),(1,1)]

def draw_pair(ax, x1, x2, k1, n1, k2, n2, c1, c2, width=0.38, alpha=1.0):
    """Draw two bars and CI, return (pp1, pp2, sig)."""
    for xi, (k,n,c) in enumerate([(k1,n1,c1),(k2,n2,c2)]):
        x = x1 if xi==0 else x2
        pv = pp(k,n)
        lo,hi = wilson_ci(k,n)
        ax.bar(x,pv,width,color=c,alpha=alpha,zorder=3,
               edgecolor='white',linewidth=0.5)
        ax.errorbar(x,pv,yerr=[[pv-lo],[hi-pv]],fmt='none',
                    color='#333',capsize=3,capthick=1,lw=1,zorder=4)
    _,p = z_test(k1,n1,k2,n2)
    return pp(k1,n1),pp(k2,n2),p

def sig_bracket(ax, x1, x2, y_top, p, extra=1.5):
    y = y_top + extra
    ax.plot([x1,x1,x2,x2],[y-1,y,y,y-1],color='#555',lw=0.8)
    ax.text((x1+x2)/2,y+0.5,stars(p),ha='center',va='bottom',
            fontsize=7.5,color='#333')

def style_ax(ax, title, col, ylim=(-15,65)):
    ax.axhline(0,color='#888',lw=0.8,ls='--',zorder=2)
    ax.set_ylim(*ylim)
    ax.set_title(title,fontsize=8.5,fontweight='bold',pad=3,color=col)
    ax.spines['top'].set_visible(False); ax.spines['right'].set_visible(False)
    ax.yaxis.set_minor_locator(matplotlib.ticker.MultipleLocator(5))
    ax.grid(axis='y',which='minor',lw=0.3,alpha=0.35,zorder=0)
    ax.grid(axis='y',which='major',lw=0.5,alpha=0.45,zorder=0)
    ax.tick_params(labelsize=7)

# ── NEAR/FAR panels (top row = CUED, bottom row = UNCUED, col 2 = ALL) ────────
for (cond,dep,lbl,col,alp),(ri,ci) in zip(CELLS,CELL_POSITIONS):
    ax = fig.add_subplot(gs[ri,ci])
    kn=get(cond,dep,'tdep','N'); kf=get(cond,dep,'tdep','F')
    pn,pf,p = draw_pair(ax,0,0.55,kn[0],kn[1],kf[0],kf[1],
                        C_NEAR,C_FAR,alpha=alp)
    ymax = max(pn + (wilson_ci(kn[0],kn[1])[1]-pn),
               pf + (wilson_ci(kf[0],kf[1])[1]-pf)) if kn[1]>0 and kf[1]>0 else 30
    sig_bracket(ax,0,0.55,ymax,p)
    diff = pf-pn
    ax.text(0.275,-13.5,'Far−Near={:+.1f}pp'.format(diff),
            ha='center',fontsize=7,color='#333',style='italic')
    ax.set_xticks([0,0.55])
    ax.set_xticklabels(['Near\n(Red)','Far\n(Green)'],fontsize=7.5)
    if ci==0: ax.set_ylabel('pp above chance',fontsize=7.5)
    style_ax(ax,lbl,col)

# ── RED/GREEN panels ───────────────────────────────────────────────────────────
# Separate 1×5 strip below main panels
gs2 = gridspec.GridSpec(1,5,top=0.27,bottom=0.08,
                        left=0.07,right=0.97,wspace=0.35)

for pi,(cond,dep,lbl,col,alp) in enumerate(CELLS):
    ax = fig.add_subplot(gs2[0,pi])
    kr=get(cond,dep,'tclr','R'); kg=get(cond,dep,'tclr','G')
    pr,pg,p = draw_pair(ax,0,0.55,kr[0],kr[1],kg[0],kg[1],
                        C_RED_T,C_GRN_T,alpha=alp)
    ymax = max(pr + (wilson_ci(kr[0],kr[1])[1]-pr),
               pg + (wilson_ci(kg[0],kg[1])[1]-pg)) if kr[1]>0 and kg[1]>0 else 30
    sig_bracket(ax,0,0.55,ymax,p)
    diff = pg-pr
    ax.text(0.275,-13.5,'Grn−Red={:+.1f}pp'.format(diff),
            ha='center',fontsize=7,color='#333',style='italic')
    ax.set_xticks([0,0.55])
    ax.set_xticklabels(['Red\ntrans','Green\ntrans'],fontsize=7.5)
    if pi==0: ax.set_ylabel('pp above chance',fontsize=7.5)
    style_ax(ax,lbl,col)

# ── Row labels ────────────────────────────────────────────────────────────────
fig.text(0.005,0.76,'Near vs Far\ntranslation',ha='left',va='center',
         fontsize=9,fontweight='bold',color='#333',rotation=90)
fig.text(0.005,0.175,'Red vs Green\ntranslator',ha='left',va='center',
         fontsize=9,fontweight='bold',color='#333',rotation=90)

# Divider
fig.add_artist(plt.Line2D([0.04,0.98],[0.295,0.295],
    transform=fig.transFigure,color='#AAAAAA',lw=1.2,ls='--'))

# ── Conjecture text box ────────────────────────────────────────────────────────
ax_txt = fig.add_axes([0.07,0.008,0.90,0.058])
ax_txt.axis('off')

conj = (
    "NEAR/FAR:  Far > Near overall (+8.6pp*), but the direction FLIPS across conditions. "
    "CUED+ZdNoi (Depth✓): Far=+55pp vs Near=+20pp (+34pp***, huge).  "
    "CUED+ZdCoh (Depth✗): Near=+28pp vs Far=+17pp (reversed, n.s.).  "
    "Conjecture: Far advantage is specifically a 'translation-at-far-plane' advantage — "
    "when the translator retains its depth identity (ZdNoi), the Far plane provides a stronger "
    "grouping/segregation signal (consistent with DepthSwapCtrl). When the translator changes "
    "planes (ZdCoh), the near/far signal is disrupted and the advantage reverses or disappears. "
    "This rules out a simple 'far objects are easier to track' account — depth-identity coherence "
    "is the modulating variable.\n"
    "RED/GREEN:  Consistent Red > Green trend (~8–16pp) across all cells, but none significant at n=64/cell. "
    "Red translator advantage is present whether or not depth cuing matches (Depth✓ and Depth✗ alike). "
    "Conjecture: Red may carry a salience or attentional weighting advantage in this display "
    "(consistent with reports that all-red DepthSwapCtrl showed reduced cueing — if red is "
    "already salient it may reduce the signal-to-noise of the onset cue). "
    "Alternatively, observer GS has idiosyncratic red sensitivity. Needs replication."
)

# Word-wrap into two lines
lines = textwrap.wrap(conj, width=195)
for li, line in enumerate(lines[:3]):
    ax_txt.text(0, 1.0 - li*0.38, line, transform=ax_txt.transAxes,
                ha='left', va='top', fontsize=6.8, color='#222',
                fontfamily='monospace')

os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
fig.savefig(OUT_PATH, dpi=150, bbox_inches='tight', facecolor='white')
print('Saved: {}'.format(OUT_PATH))
