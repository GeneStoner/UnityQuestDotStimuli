#!/usr/bin/env python3
"""
trans_plane_color_fig.py
Three independent effects in DepthColorLinked_005m (n=512):
  1. Dot cueing (CUED > UNCUED)
  2. TransPlane: Far > Near (~+8.6pp*)
  3. TransColor: Red > Green (~+10.2pp*)
Effects 2 and 3 are OPPOSITE to the Near=Red / Far=Green linking rule.

Output: Agents/Figures/trans_plane_color.png
"""

import csv, collections, os, math, textwrap
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.ticker
import matplotlib.patches as mpatches

DATA_DIR = os.path.expanduser('~/Library/Application Support/ThatsRandom/VRDotsDataFiles')
OUT_PATH = os.path.expanduser(
    '~/Projects/ObjectBasedAttention/VRDots/Agents/Figures/trans_plane_color.png')
SESSIONS = ['260404_0940', '260404_1123']
CHANCE = 1/8

# ── Stats ──────────────────────────────────────────────────────────────────────
def normal_cdf(x): return 0.5*(1+math.erf(x/math.sqrt(2)))
def z_test(k1,n1,k2,n2):
    p1,p2=k1/n1,k2/n2; pp=(k1+k2)/(n1+n2)
    se=math.sqrt(max(pp*(1-pp)*(1/n1+1/n2),1e-12))
    z=(p1-p2)/se; return z,2*(1-normal_cdf(abs(z)))
def z_vs_chance(k,n):
    p=k/n; se=math.sqrt(max(CHANCE*(1-CHANCE)/n,1e-12))
    z=(p-CHANCE)/se; return z,1-normal_cdf(z)
def wilson_ci(k,n,z=1.96):
    p=k/n; d=1+z**2/n; c=(p+z**2/(2*n))/d
    hw=z*math.sqrt(p*(1-p)/n+z**2/(4*n**2))/d
    return (c-hw-CHANCE)*100,(c+hw-CHANCE)*100
def pp(k,n): return (k/n-CHANCE)*100 if n>0 else 0.0
def stars(p): return '***' if p<.001 else '**' if p<.01 else '*' if p<.05 else '†' if p<.1 else 'n.s.'

def is_correct(td,rd):
    d=(float(rd)-float(td)+360)%360; return (360-d if d>180 else d)<=22.5
def depth_cue_yes(cond,swap): return (cond=='CUED') != (swap=='ZdA')
def trans_depth(cond,swap,dfd):
    return dfd if depth_cue_yes(cond,swap) else ('F' if dfd=='N' else 'N')
def trans_color(cond,swap,dfd,dfc):
    tdep = trans_depth(cond,swap,dfd)
    return dfc if tdep==dfd else ('G' if dfc=='R' else 'R')

# ── Load ───────────────────────────────────────────────────────────────────────
cnt = collections.defaultdict(lambda:[0,0])
for sid in SESSIONS:
    path = os.path.join(DATA_DIR, 'vr_dots_session_{}.tsv'.format(sid))
    for r in csv.DictReader(open(path), delimiter='\t'):
        if r.get('EndKey','') in ('timeout','skip','requeue'): continue
        td=r.get('TransDeg',''); rd=r.get('RespDeg','')
        if not td or not rd: continue
        cond=r['Cond']; swap=r['SwapType']
        dfd=r['DelayedFieldDepth']; dfc=r['DelayedFieldColor']
        corr=int(is_correct(td,rd))
        tp = trans_depth(cond,swap,dfd)
        tc = trans_color(cond,swap,dfd,dfc)

        for key in [
            (cond, tp, tc),
            ('ALL', tp, tc),
            ('ALL', tp, 'ALL'),
            ('ALL', 'ALL', tc),
            (cond, 'ALL', 'ALL'),
        ]:
            cnt[key][0] += corr
            cnt[key][1] += 1

def get(cond='ALL', tp='ALL', tc='ALL'):
    k,n = cnt[(cond,tp,tc)]
    return dict(k=k, n=n, pp=pp(k,n), ci=wilson_ci(k,n))

# ── Colors ────────────────────────────────────────────────────────────────────
C_FAR   = '#1a3a8b'
C_NEAR  = '#888888'
C_RED   = '#CC3333'
C_GRN   = '#228B22'
C_CUED  = '#1a3a8b'
C_UNCUED= '#aa2222'

# ── Figure ────────────────────────────────────────────────────────────────────
fig = plt.figure(figsize=(14, 8))
fig.patch.set_facecolor('white')

fig.text(0.5, 0.983,
    'DepthColorLinked_005m: Three independent effects on translation detection  (n=512)',
    ha='center', va='top', fontsize=12, fontweight='bold', color='#111')
fig.text(0.5, 0.960,
    'Error bars = 95% Wilson CI  ·  Significance = two-tailed z-test  ·  '
    'Near=Red / Far=Green linking rule: depth and color effects go in OPPOSITE directions',
    ha='center', va='top', fontsize=8, color='#555')

gs = gridspec.GridSpec(1, 4, left=0.06, right=0.98, top=0.88, bottom=0.20,
                       wspace=0.42)

def draw_bars(ax, items, width=0.38, ylim=(-10,65)):
    """items: list of (x, k, n, color, label)"""
    tops = []
    for (x, k, n, c, lbl) in items:
        pv = pp(k,n); lo,hi = wilson_ci(k,n)
        ax.bar(x, pv, width, color=c, zorder=3, edgecolor='white', linewidth=0.5)
        ax.errorbar(x, pv, yerr=[[pv-lo],[hi-pv]], fmt='none',
                    color='#333', capsize=3, capthick=1, lw=1, zorder=4)
        _,p = z_vs_chance(k,n)
        ax.text(x, pv+(hi-pv)+1.2, stars(p), ha='center', va='bottom',
                fontsize=8, color='#333')
        tops.append(pv+(hi-pv))
    ax.axhline(0, color='#888', lw=0.8, ls='--', zorder=2)
    ax.set_ylim(*ylim)
    ax.spines['top'].set_visible(False); ax.spines['right'].set_visible(False)
    ax.yaxis.set_minor_locator(matplotlib.ticker.MultipleLocator(5))
    ax.grid(axis='y', which='minor', lw=0.3, alpha=0.35, zorder=0)
    ax.grid(axis='y', which='major', lw=0.5, alpha=0.45, zorder=0)
    ax.tick_params(labelsize=8)
    return tops

def bracket(ax, x1, x2, y, label, color='#444'):
    ax.plot([x1,x1,x2,x2],[y-1.2,y,y,y-1.2], color='#666', lw=0.9)
    ax.text((x1+x2)/2, y+0.6, label, ha='center', va='bottom',
            fontsize=7.5, color=color, fontweight='bold')

# ─── Panel A: Cueing effect ───────────────────────────────────────────────────
ax0 = fig.add_subplot(gs[0,0])
dc = get('CUED');   du = get('UNCUED')
tops = draw_bars(ax0, [
    (0.3, dc['k'], dc['n'], C_CUED,   'CUED'),
    (0.8, du['k'], du['n'], C_UNCUED, 'UNCUED'),
])
_,pcue = z_test(dc['k'],dc['n'], du['k'],du['n'])
diff = dc['pp']-du['pp']
bracket(ax0, 0.3, 0.8, max(tops)+3,
        'Δ={:+.0f}pp {}'.format(diff, stars(pcue)), color=C_CUED)
ax0.set_xticks([0.3, 0.8])
ax0.set_xticklabels(['CUED\n(delayed field\ntranslates)', 'UNCUED\n(other field\ntranslates)'],
                    fontsize=7.5)
ax0.set_xlim(0.0, 1.1)
ax0.set_ylabel('pp above chance (1/8)', fontsize=8)
ax0.set_title('A.  Effect 1: Dot cueing\n(n=256 each)', fontsize=9, fontweight='bold', pad=4)

# ─── Panel B: TransPlane effect ───────────────────────────────────────────────
ax1 = fig.add_subplot(gs[0,1])
df = get(tp='F');  dn = get(tp='N')
tops = draw_bars(ax1, [
    (0.3, df['k'], df['n'], C_FAR,  'Trans=Far'),
    (0.8, dn['k'], dn['n'], C_NEAR, 'Trans=Near'),
])
_,ptp = z_test(df['k'],df['n'], dn['k'],dn['n'])
diff = df['pp']-dn['pp']
bracket(ax1, 0.3, 0.8, max(tops)+3,
        'Δ={:+.0f}pp {}'.format(diff, stars(ptp)), color=C_FAR)
ax1.set_xticks([0.3, 0.8])
ax1.set_xticklabels(['Far\ntranslator', 'Near\ntranslator'], fontsize=8)
ax1.set_xlim(0.0, 1.1)
ax1.set_title('B.  Effect 2: Translator depth\n(n=256 each)', fontsize=9, fontweight='bold', pad=4)
ax1.text(0.55, -7.5, '(balanced: Far/Near × Red/Green independent)', ha='center',
         fontsize=7, color='#777', style='italic')

# ─── Panel C: TransColor effect ───────────────────────────────────────────────
ax2 = fig.add_subplot(gs[0,2])
dr = get(tc='R');  dg = get(tc='G')
tops = draw_bars(ax2, [
    (0.3, dr['k'], dr['n'], C_RED, 'Trans=Red'),
    (0.8, dg['k'], dg['n'], C_GRN, 'Trans=Green'),
])
_,ptc = z_test(dr['k'],dr['n'], dg['k'],dg['n'])
diff = dr['pp']-dg['pp']
bracket(ax2, 0.3, 0.8, max(tops)+3,
        'Δ={:+.0f}pp {}'.format(diff, stars(ptc)), color=C_RED)
ax2.set_xticks([0.3, 0.8])
ax2.set_xticklabels(['Red\ntranslator', 'Green\ntranslator'], fontsize=8)
ax2.set_xlim(0.0, 1.1)
ax2.set_title('C.  Effect 3: Translator color\n(n=256 each)', fontsize=9, fontweight='bold', pad=4)
ax2.text(0.55, -7.5, '(balanced: Red/Green × Near/Far independent)', ha='center',
         fontsize=7, color='#777', style='italic')

# ─── Panel D: TransPlane × TransColor 2×2 ────────────────────────────────────
ax3 = fig.add_subplot(gs[0,3])

# 4 bars: Far-Red, Far-Green, Near-Red, Near-Green
xs = [0.18, 0.52, 0.88, 1.22]
combos = [('F','R'), ('F','G'), ('N','R'), ('N','G')]
cols   = [C_FAR, C_FAR, C_NEAR, C_NEAR]
alphas = [1.0, 0.55, 1.0, 0.55]
xlbls  = ['Far\nRed', 'Far\nGrn', 'Near\nRed', 'Near\nGrn']
tops = []
for x,(tp,tc),c,alp,lbl in zip(xs,combos,cols,alphas,xlbls):
    d = get(tp=tp, tc=tc)
    pv = d['pp']; lo,hi = d['ci']
    ax3.bar(x, pv, 0.28, color=c, alpha=alp, zorder=3,
            edgecolor='white', linewidth=0.5)
    ax3.errorbar(x, pv, yerr=[[pv-lo],[hi-pv]], fmt='none',
                 color='#333', capsize=3, capthick=1, lw=1, zorder=4)
    _,p = z_vs_chance(d['k'],d['n'])
    ax3.text(x, pv+(hi-pv)+1.2, stars(p), ha='center', va='bottom',
             fontsize=7.5, color='#333')
    # color stripe on bar to show color
    stripe_c = C_RED if tc=='R' else C_GRN
    ax3.bar(x, min(pv, 4), 0.28, bottom=max(0,pv-4),
            color=stripe_c, alpha=0.6, zorder=4)
    tops.append(pv+(hi-pv))

ax3.axhline(0, color='#888', lw=0.8, ls='--', zorder=2)
ax3.set_xticks(xs)
ax3.set_xticklabels(xlbls, fontsize=7.5)
ax3.set_xlim(-0.05, 1.45)
ax3.set_ylim(-10, 65)
ax3.set_title('D.  TransPlane × TransColor\n(n=128 each)', fontsize=9, fontweight='bold', pad=4)
ax3.spines['top'].set_visible(False); ax3.spines['right'].set_visible(False)
ax3.yaxis.set_minor_locator(matplotlib.ticker.MultipleLocator(5))
ax3.grid(axis='y', which='minor', lw=0.3, alpha=0.35, zorder=0)
ax3.grid(axis='y', which='major', lw=0.5, alpha=0.45, zorder=0)
ax3.tick_params(labelsize=7.5)

# Depth effect bracket (Far vs Near, within red)
_,p_fr_nr = z_test(cnt[('ALL','F','R')][0],cnt[('ALL','F','R')][1],
                   cnt[('ALL','N','R')][0],cnt[('ALL','N','R')][1])
bracket(ax3, xs[0], xs[2], max(tops[:1]+tops[2:3])+4,
        'Far>Near {}'.format(stars(p_fr_nr)), color=C_FAR)

# Color effect bracket (Red vs Green, within Far)
_,p_fr_fg = z_test(cnt[('ALL','F','R')][0],cnt[('ALL','F','R')][1],
                   cnt[('ALL','F','G')][0],cnt[('ALL','F','G')][1])
bracket(ax3, xs[0], xs[1], tops[0]+3,
        'Red>Grn {}'.format(stars(p_fr_fg)), color=C_RED)

p_far  = mpatches.Patch(color=C_FAR,  label='Far translator')
p_near = mpatches.Patch(color=C_NEAR, label='Near translator')
ax3.legend(handles=[p_far,p_near], fontsize=7, loc='upper right', framealpha=0.85)

# ─── Caption ──────────────────────────────────────────────────────────────────
caption = (
    "THREE INDEPENDENT EFFECTS.  "
    "Effect 1 (Dot cueing, +20.3pp***): performance is better when the delayed-onset (cued) field translates — the main cueing effect.  "
    "Effect 2 (Translator depth, +8.6pp*): Far-plane translator is easier to detect than Near-plane, regardless of cueing or color.  "
    "Effect 3 (Translator color, +10.2pp*): Red translator is easier to detect than Green, regardless of cueing or depth.  "
    "Design is fully balanced (n=32 in each DFD × DFC × COND × SWAP cell): depth and color effects are orthogonal and independently estimable.  "
    "Needs replication at higher n — each marginal comparison is n=256, each 2×2 cell is n=128."
)
ax_txt = fig.add_axes([0.04, 0.01, 0.93, 0.14])
ax_txt.axis('off')
lines = textwrap.wrap(caption, width=190)
for li, line in enumerate(lines[:3]):
    ax_txt.text(0, 1.0-li*0.35, line, transform=ax_txt.transAxes,
                ha='left', va='top', fontsize=7, color='#222',
                fontfamily='monospace')

os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
fig.savefig(OUT_PATH, dpi=150, bbox_inches='tight', facecolor='white')
print('Saved: {}'.format(OUT_PATH))
