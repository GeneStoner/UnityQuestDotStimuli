#!/usr/bin/env python3
"""
trans_plane_fig.py
Demonstrates that the Near/Far performance advantage tracks the TRANSLATING
field's depth plane (TransPlane), NOT the delayed field's starting plane (DFD).

2×2 design: CUED/UNCUED × TransPlane (Near/Far)
    CUED:   translator = delayed field  →  TransPlane = DFD
    UNCUED: translator = non-delayed field →  TransPlane = opp(DFD)

Output: Agents/Figures/trans_plane_2x2.png
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

DATA_DIR = os.path.expanduser('~/Library/Application Support/ThatsRandom/VRDotsDataFiles')
OUT_PATH = os.path.expanduser(
    '~/Projects/ObjectBasedAttention/VRDots/Agents/Figures/trans_plane_2x2.png')
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

# ── Load data ─────────────────────────────────────────────────────────────────
# TransPlane = depth of the TRANSLATING field
#   CUED:   delayed field translates → TransPlane = DFD
#   UNCUED: non-delayed field translates → TransPlane = opp(DFD)
cnt = collections.defaultdict(lambda:[0,0])

for sid in SESSIONS:
    path = os.path.join(DATA_DIR, 'vr_dots_session_{}.tsv'.format(sid))
    for r in csv.DictReader(open(path), delimiter='\t'):
        if r.get('EndKey','') in ('timeout','skip','requeue'): continue
        td = r.get('TransDeg',''); rd = r.get('RespDeg','')
        if not td or not rd: continue
        cond  = r['Cond']
        dfd   = r['DelayedFieldDepth']
        corr  = int(is_correct(td,rd))

        # TransPlane: CUED→same as DFD; UNCUED→opposite
        if cond == 'CUED':
            trans_plane = dfd
        else:
            trans_plane = 'F' if dfd == 'N' else 'N'

        cnt[(cond, trans_plane)][0] += corr
        cnt[(cond, trans_plane)][1] += 1
        cnt[('ALL',  trans_plane)][0] += corr
        cnt[('ALL',  trans_plane)][1] += 1
        cnt[(cond,   'ALL')][0] += corr
        cnt[(cond,   'ALL')][1] += 1

# ── Derived numbers ───────────────────────────────────────────────────────────
cells = {}
for cond in ['CUED','UNCUED']:
    for tp in ['N','F']:
        k,n = cnt[(cond,tp)]
        cells[(cond,tp)] = dict(k=k,n=n,pp=pp(k,n),ci=wilson_ci(k,n))

# Marginals
marg_cond = {}
for cond in ['CUED','UNCUED']:
    k,n = cnt[(cond,'ALL')]
    marg_cond[cond] = dict(k=k,n=n,pp=pp(k,n),ci=wilson_ci(k,n))
marg_tp = {}
for tp in ['N','F']:
    k,n = cnt[('ALL',tp)]
    marg_tp[tp] = dict(k=k,n=n,pp=pp(k,n),ci=wilson_ci(k,n))

# Effect magnitudes
cue_effect  = marg_cond['CUED']['pp']  - marg_cond['UNCUED']['pp']
tp_effect   = marg_tp['F']['pp']       - marg_tp['N']['pp']
zcue,pcue   = z_test(cnt[('CUED','ALL')][0],   cnt[('CUED','ALL')][1],
                     cnt[('UNCUED','ALL')][0],  cnt[('UNCUED','ALL')][1])
ztp,ptp     = z_test(cnt[('ALL','F')][0],      cnt[('ALL','F')][1],
                     cnt[('ALL','N')][0],       cnt[('ALL','N')][1])

# Interaction: Far advantage in CUED vs UNCUED
far_adv_cued   = cells[('CUED','F')]['pp']   - cells[('CUED','N')]['pp']
far_adv_uncued = cells[('UNCUED','F')]['pp'] - cells[('UNCUED','N')]['pp']

print("=== 2x2: CUED/UNCUED x TransPlane ===")
for cond in ['CUED','UNCUED']:
    for tp in ['N','F']:
        d = cells[(cond,tp)]
        lo,hi = d['ci']
        _,p = z_vs_chance(d['k'],d['n'])
        print(f"  {cond:6s} Trans={'Near' if tp=='N' else 'Far ':4s}  "
              f"k={d['k']:3d} n={d['n']:3d}  {d['pp']:+6.1f}pp  "
              f"[{lo:+5.1f},{hi:+5.1f}]  {stars(p)}")
print(f"\nCueing effect:  {cue_effect:+.1f}pp  {stars(pcue)}")
print(f"TransPlane Far effect: {tp_effect:+.1f}pp  {stars(ptp)}")
print(f"Far advantage in CUED:   {far_adv_cued:+.1f}pp")
print(f"Far advantage in UNCUED: {far_adv_uncued:+.1f}pp")

# ── Colors ────────────────────────────────────────────────────────────────────
C_FAR_GRN  = '#228B22'   # Far=Green translator
C_NEAR_RED = '#CC3333'   # Near=Red translator
C_CUED     = '#1a3a8b'
C_UNCUED   = '#aa2222'
C_ANNOT    = '#333333'

# ── Figure ────────────────────────────────────────────────────────────────────
fig = plt.figure(figsize=(13,8))
fig.patch.set_facecolor('white')

fig.text(0.5, 0.978,
    'Translation-plane depth drives performance — not delayed-field starting plane',
    ha='center', va='top', fontsize=13, fontweight='bold', color='#111')
fig.text(0.5, 0.952,
    'DepthColorLinked_005m  ·  n=512 (sessions 260404_0940+1123)  ·  '
    'Near=Red, Far=Green  ·  Error bars = 95% Wilson CI',
    ha='center', va='top', fontsize=8.5, color='#555')

gs = gridspec.GridSpec(1, 3, left=0.07, right=0.97, top=0.88, bottom=0.18,
                       wspace=0.42)

# ─── Panel A: 2×2 main bar chart ──────────────────────────────────────────────
ax = fig.add_subplot(gs[0,0])

x_cued, x_uncued = 0.4, 1.4
w = 0.30

data_order = [
    ('CUED',   'N', x_cued   - w/2 - 0.02, C_NEAR_RED),
    ('CUED',   'F', x_cued   + w/2 + 0.02, C_FAR_GRN),
    ('UNCUED', 'N', x_uncued - w/2 - 0.02, C_NEAR_RED),
    ('UNCUED', 'F', x_uncued + w/2 + 0.02, C_FAR_GRN),
]

bar_tops = {}
for (cond, tp, x, c) in data_order:
    d = cells[(cond,tp)]
    pv = d['pp']; lo,hi = d['ci']
    ax.bar(x, pv, w, color=c, zorder=3, edgecolor='white', linewidth=0.5)
    ax.errorbar(x, pv, yerr=[[pv-lo],[hi-pv]], fmt='none',
                color='#333', capsize=3, capthick=1, lw=1, zorder=4)
    _,p = z_vs_chance(d['k'],d['n'])
    ax.text(x, pv + (hi-pv) + 1.5, stars(p), ha='center', va='bottom',
            fontsize=7.5, color='#333')
    bar_tops[(cond,tp)] = pv + (hi-pv)

ax.axhline(0, color='#888', lw=0.8, ls='--', zorder=2)

# Bracket: Far vs Near within CUED
y_br = max(bar_tops[('CUED','N')], bar_tops[('CUED','F')]) + 3.5
ax.plot([x_cued-w/2-0.02]*2 + [x_cued+w/2+0.02]*2,
        [y_br-1.5, y_br, y_br, y_br-1.5], color='#555', lw=0.9)
_,p_far_cued = z_test(cnt[('CUED','F')][0], cnt[('CUED','F')][1],
                      cnt[('CUED','N')][0], cnt[('CUED','N')][1])
ax.text(x_cued, y_br+0.5,
        'Far−Near={:+.0f}pp {}'.format(far_adv_cued, stars(p_far_cued/2)),
        ha='center', va='bottom', fontsize=7, color='#333')

# Bracket: Far vs Near within UNCUED
y_br2 = max(bar_tops[('UNCUED','N')], bar_tops[('UNCUED','F')]) + 3.5
ax.plot([x_uncued-w/2-0.02]*2 + [x_uncued+w/2+0.02]*2,
        [y_br2-1.5, y_br2, y_br2, y_br2-1.5], color='#555', lw=0.9)
_,p_far_uncued = z_test(cnt[('UNCUED','F')][0], cnt[('UNCUED','F')][1],
                        cnt[('UNCUED','N')][0], cnt[('UNCUED','N')][1])
ax.text(x_uncued, y_br2+0.5,
        'Far−Near={:+.0f}pp {}'.format(far_adv_uncued, stars(p_far_uncued/2)),
        ha='center', va='bottom', fontsize=7, color='#333')

ax.set_xticks([x_cued, x_uncued])
ax.set_xticklabels(['CUED\n(delayed field\ntranslates)', 'UNCUED\n(other field\ntranslates)'],
                   fontsize=8)
ax.set_xlim(0.0, 1.9)
ax.set_ylim(-12, 80)
ax.set_ylabel('pp above chance (1/8)', fontsize=8.5)
ax.set_title('A.  CUED/UNCUED × Translating-plane depth', fontsize=9, fontweight='bold', pad=5)
ax.spines['top'].set_visible(False); ax.spines['right'].set_visible(False)
ax.yaxis.set_minor_locator(matplotlib.ticker.MultipleLocator(5))
ax.grid(axis='y', which='minor', lw=0.3, alpha=0.35, zorder=0)
ax.grid(axis='y', which='major', lw=0.5, alpha=0.45, zorder=0)
ax.tick_params(labelsize=7.5)

p_near = mpatches.Patch(color=C_NEAR_RED, label='Trans=Near (Red)')
p_far  = mpatches.Patch(color=C_FAR_GRN,  label='Trans=Far (Green)')
ax.legend(handles=[p_far, p_near], fontsize=7.5, loc='upper right',
          framealpha=0.85, edgecolor='#ccc')

# ─── Panel B: Marginal means ──────────────────────────────────────────────────
ax2 = fig.add_subplot(gs[0,1])

# Cueing marginal (left) and TransPlane marginal (right)
xs   = [0.25, 0.75, 1.35, 1.85]
vals = [marg_cond['CUED']['pp'], marg_cond['UNCUED']['pp'],
        marg_tp['F']['pp'],      marg_tp['N']['pp']]
cis  = [marg_cond['CUED']['ci'], marg_cond['UNCUED']['ci'],
        marg_tp['F']['ci'],      marg_tp['N']['ci']]
ks   = [cnt[('CUED','ALL')][0],   cnt[('UNCUED','ALL')][0],
        cnt[('ALL','F')][0],      cnt[('ALL','N')][0]]
ns   = [cnt[('CUED','ALL')][1],   cnt[('UNCUED','ALL')][1],
        cnt[('ALL','F')][1],      cnt[('ALL','N')][1]]
cols = [C_CUED, C_UNCUED, C_FAR_GRN, C_NEAR_RED]
lbls = ['CUED', 'UNCUED', 'Trans=Far\n(Green)', 'Trans=Near\n(Red)']

bar_tops2 = []
for x,pv,(lo,hi),k,n,c in zip(xs,vals,cis,ks,ns,cols):
    ax2.bar(x, pv, 0.30, color=c, zorder=3, edgecolor='white', linewidth=0.5)
    ax2.errorbar(x, pv, yerr=[[pv-lo],[hi-pv]], fmt='none',
                 color='#333', capsize=3, capthick=1, lw=1, zorder=4)
    _,p = z_vs_chance(k,n)
    ax2.text(x, pv+(hi-pv)+1.2, stars(p), ha='center', va='bottom',
             fontsize=7.5, color='#333')
    bar_tops2.append(pv+(hi-pv))

# Cue-effect bracket
y_br = max(bar_tops2[:2]) + 3.5
ax2.plot([xs[0]]*2+[xs[1]]*2, [y_br-1.5,y_br,y_br,y_br-1.5], color='#555', lw=0.9)
ax2.text((xs[0]+xs[1])/2, y_br+0.5,
         'Δ={:+.0f}pp {}'.format(cue_effect, stars(pcue)),
         ha='center', va='bottom', fontsize=7, color=C_CUED, fontweight='bold')

# TransPlane effect bracket
y_br2 = max(bar_tops2[2:]) + 3.5
ax2.plot([xs[2]]*2+[xs[3]]*2, [y_br2-1.5,y_br2,y_br2,y_br2-1.5], color='#555', lw=0.9)
ax2.text((xs[2]+xs[3])/2, y_br2+0.5,
         'Δ={:+.0f}pp {}'.format(tp_effect, stars(ptp)),
         ha='center', va='bottom', fontsize=7, color=C_FAR_GRN, fontweight='bold')

ax2.axhline(0, color='#888', lw=0.8, ls='--', zorder=2)
ax2.axvline(1.05, color='#aaa', lw=0.8, ls=':', zorder=1)
ax2.set_xticks(xs)
ax2.set_xticklabels(lbls, fontsize=7.5)
ax2.set_xlim(-0.05, 2.15)
ax2.set_ylim(-12, 80)
ax2.set_title('B.  Marginal effects\n(each n=256)', fontsize=9, fontweight='bold', pad=5)
ax2.spines['top'].set_visible(False); ax2.spines['right'].set_visible(False)
ax2.yaxis.set_minor_locator(matplotlib.ticker.MultipleLocator(5))
ax2.grid(axis='y', which='minor', lw=0.3, alpha=0.35, zorder=0)
ax2.grid(axis='y', which='major', lw=0.5, alpha=0.45, zorder=0)
ax2.tick_params(labelsize=7.5)
ax2.text(0.5,  -8.5, 'Onset cue\n(which field translates)', ha='center',
         fontsize=7, color='#555', style='italic')
ax2.text(1.6,  -8.5, 'Depth of\ntranslating field', ha='center',
         fontsize=7, color='#555', style='italic')

# ─── Panel C: Design explanation diagram ─────────────────────────────────────
ax3 = fig.add_subplot(gs[0,2])
ax3.set_xlim(0,10); ax3.set_ylim(0,10)
ax3.axis('off')
ax3.set_title('C.  Why DFD ≠ TransPlane in UNCUED', fontsize=9, fontweight='bold', pad=5)

# Draw 2×2 table explaining the confound
row_h = 1.8; col_w = 2.2
x0, y0 = 0.5, 8.0
headers = ['DFD=Near', 'DFD=Far']
row_labels = ['CUED', 'UNCUED']

for ci, hdr in enumerate(headers):
    ax3.text(x0 + col_w*(ci+0.5)+0.5, y0+0.4, hdr, ha='center', va='center',
             fontsize=8.5, fontweight='bold',
             color=C_NEAR_RED if ci==0 else C_FAR_GRN)

for ri, rl in enumerate(row_labels):
    ax3.text(x0-0.1, y0 - row_h*(ri+0.5), rl, ha='right', va='center',
             fontsize=8.5, fontweight='bold',
             color=C_CUED if ri==0 else C_UNCUED)

# Cell content
cell_info = {
    (0,0): ('Trans=Near', C_NEAR_RED, '+18.8pp***'),
    (0,1): ('Trans=Far',  C_FAR_GRN,  '+41.4pp***'),
    (1,0): ('Trans=Far',  C_FAR_GRN,  '+18.8pp***'),
    (1,1): ('Trans=Near', C_NEAR_RED, '+0.8pp n.s.'),
}

for ri in range(2):
    for ci in range(2):
        cx = x0 + col_w*(ci+0.5) + 0.5
        cy = y0 - row_h*(ri+0.5)
        fc = '#eaf4ea' if cell_info[(ri,ci)][1]==C_FAR_GRN else '#faeaea'
        rect = mpatches.FancyBboxPatch((cx-0.9, cy-0.65), 1.8, 1.3,
               boxstyle='round,pad=0.05', facecolor=fc,
               edgecolor=cell_info[(ri,ci)][1], linewidth=1.5, zorder=2)
        ax3.add_patch(rect)
        ax3.text(cx, cy+0.25, cell_info[(ri,ci)][0], ha='center', va='center',
                 fontsize=8, fontweight='bold', color=cell_info[(ri,ci)][1], zorder=3)
        ax3.text(cx, cy-0.25, cell_info[(ri,ci)][2], ha='center', va='center',
                 fontsize=7.5, color='#333', zorder=3)

# Grid lines
for ri in range(3):
    ax3.plot([x0+0.5, x0+col_w*2+0.5], [y0-row_h*ri]*2, color='#ccc', lw=0.8)
for ci in range(3):
    ax3.plot([x0+col_w*ci+0.5]*2, [y0, y0-row_h*2], color='#ccc', lw=0.8)

# Arrows/annotations
ax3.annotate('', xy=(x0+col_w*0.5+0.5, y0-row_h*1.5),
             xytext=(x0+col_w*1.5+0.5, y0-row_h*0.5),
             arrowprops=dict(arrowstyle='->', color='#888', lw=1.2),
             annotation_clip=False)
ax3.text(5.1, 5.2, 'Far always\nbetter', ha='center', va='center',
         fontsize=7, color='#555', style='italic',
         rotation=35)

# Explanation text
note = (
    "In CUED trials: delayed field translates\n"
    "→ TransPlane = DFD\n\n"
    "In UNCUED trials: non-delayed field translates\n"
    "→ TransPlane = opposite of DFD\n\n"
    "Far-plane translator wins in both rows.\n"
    "Performance follows the TRANSLATOR,\nnot the DFD."
)
ax3.text(5.0, 3.2, note, ha='center', va='center', fontsize=7.5,
         color='#222', linespacing=1.5,
         bbox=dict(boxstyle='round,pad=0.4', facecolor='#f5f5f5',
                   edgecolor='#bbb', linewidth=1.0))

# ─── Bottom caption ───────────────────────────────────────────────────────────
caption = (
    "KEY FINDING: The Far-plane advantage tracks which depth plane is TRANSLATING, not which plane the cued (delayed-onset) dots started in (DFD).  "
    "In CUED trials the delayed field translates (TransPlane=DFD); in UNCUED trials the non-delayed field translates (TransPlane=opp(DFD)).  "
    "Far-plane translation yields better performance in both cases (+22.6pp in CUED, +18.0pp in UNCUED).  "
    "Two independent additive effects: dot-onset cueing (~+20pp***) and Far-plane translation (~+20pp***).  "
    "Far=Green and Near=Red are fully confounded here — depth vs color cannot be separated within this experiment."
)
ax_txt = fig.add_axes([0.04, 0.01, 0.93, 0.13])
ax_txt.axis('off')
import textwrap
lines = textwrap.wrap(caption, width=185)
for li, line in enumerate(lines[:3]):
    ax_txt.text(0, 1.0-li*0.35, line, transform=ax_txt.transAxes,
                ha='left', va='top', fontsize=7, color='#222',
                fontfamily='monospace')

os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
fig.savefig(OUT_PATH, dpi=150, bbox_inches='tight', facecolor='white')
print('Saved: {}'.format(OUT_PATH))
