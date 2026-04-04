#!/usr/bin/env python3
"""
Baseline experiment write-up figure.
All elements positioned explicitly in figure coordinates to prevent overlap.
Saved to: Agents/WriteUps/baseline_writeup.png
"""

import csv, math, os, textwrap
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
    "~/Projects/ObjectBasedAttention/VRDots/Agents/WriteUps/baseline_writeup.png")

SESSIONS = [
    ("260323_1534", "Session 1  (260323_1534)\npre-v0.2.0"),
    ("260324_0716", "Session 2  (260324_0716)\nv0.2.0  [cursor-jump]"),
]

# ── Figure dimensions ─────────────────────────────────────────────────────────
FIG_W, FIG_H = 14, 22          # inches
DPI = 150
LMAR, RMAR = 0.05, 0.95        # left / right margins (figure fractions)
TXT_W = RMAR - LMAR

# Line height in figure-fraction units for body text at 8.2 pt, linespacing 1.55
_lh_px   = 8.2 / 72 * DPI * 1.55   # px per body line
LINE_H   = _lh_px / (FIG_H * DPI)  # figure fraction per body line
WRAP_W   = 168                       # characters per line

# ── Typography helpers ────────────────────────────────────────────────────────
def put_text(fig, x, y, text, fontsize=8.2, color='#222222',
             ha='left', va='top', bold=False, linespacing=1.55, **kw):
    """Place text and return (y_bottom) — y of the last pixel."""
    lines = textwrap.wrap(text, width=WRAP_W) if '\n' not in text else text.split('\n')
    rendered = '\n'.join(lines)
    fig.text(x, y, rendered, ha=ha, va=va, fontsize=fontsize, color=color,
             linespacing=linespacing,
             fontweight='bold' if bold else 'normal', **kw)
    h = len(lines) * (fontsize / 72 * DPI * linespacing) / (FIG_H * DPI)
    return y - h

def section_heading(fig, y, text, color='#1a3a6b'):
    """Centered bold section heading. Returns y_bottom."""
    fig.text(0.50, y, text, ha='center', va='top', fontsize=11,
             fontweight='bold', color=color)
    h = (11 / 72 * DPI * 1.2) / (FIG_H * DPI)
    return y - h

def para_heading(fig, y, text, color='#1a3a6b'):
    """Left-aligned paragraph heading. Returns y_bottom."""
    fig.text(LMAR, y, text, ha='left', va='top', fontsize=9.5,
             fontweight='bold', color=color)
    h = (9.5 / 72 * DPI * 1.4) / (FIG_H * DPI)
    return y - h

# ── Timing / colours ──────────────────────────────────────────────────────────
T_A=0.00; T_B=0.490; T_S=0.686; T_E=0.739; T_TOT=1.00
CW=2.0; TRANS=1.0; CCW=0.0; CHANCE=1/8
C_RED='#CC3333'; C_GREEN='#228B22'; C_TRANS='#CCCCCC'; C_FRAME='#333333'
LW=2.0

# ── Stats ─────────────────────────────────────────────────────────────────────
def normal_cdf(x):
    return 0.5*(1+math.erf(x/math.sqrt(2)))

def z_test(k1,n1,k2,n2):
    p1=k1/n1; p2=k2/n2; pp=(k1+k2)/(n1+n2)
    se=math.sqrt(max(pp*(1-pp)*(1/n1+1/n2),1e-12))
    return (p1-p2)/se, 1-normal_cdf((p1-p2)/se)

def wilson_ci(k,n,z=1.96):
    p=k/n; d=1+z**2/n; c=(p+z**2/(2*n))/d
    hw=z*math.sqrt(p*(1-p)/n+z**2/(4*n**2))/d
    return c-hw, c+hw

def stars(p):
    return '***' if p<.001 else '**' if p<.01 else '*' if p<.05 else '†' if p<.1 else 'n.s.'

# ── Data ──────────────────────────────────────────────────────────────────────
def load_session(sid):
    with open(os.path.join(DATA_DIR,f"vr_dots_session_{sid}.tsv"),newline='') as f:
        return list(csv.DictReader(f,delimiter='\t'))

def is_correct(td,rd):
    d=(float(rd)-float(td)+360)%360
    return (360-d if d>180 else d)<=22.5

def analyze(rows):
    cnt={}
    for r in rows:
        if r.get('EndKey','response') in ('timeout','skip','requeue'): continue
        cond=r['Cond']; dc=r['DelayedFieldColor']
        tc=dc if cond=='CUED' else ('G' if dc=='R' else 'R')
        td=r.get('TransDeg',''); rd=r.get('RespDeg','')
        if not td or not rd: continue
        key=(cond,tc)
        if key not in cnt: cnt[key]=[0,0]
        cnt[key][0]+=int(is_correct(td,rd)); cnt[key][1]+=1
    return cnt

# ── Trajectory drawing ────────────────────────────────────────────────────────
def traj_arrays(is_cued,rot0):
    ar=CW if rot0 else CCW; br=CCW if rot0 else CW
    if is_cued:
        return (np.array([T_A,T_TOT]),np.array([ar,ar]),
                np.array([T_B,T_S,T_S,T_E,T_E,T_TOT]),
                np.array([br,br,TRANS,TRANS,br,br]))
    else:
        return (np.array([T_A,T_S,T_S,T_E,T_E,T_TOT]),
                np.array([ar,ar,TRANS,TRANS,ar,ar]),
                np.array([T_B,T_TOT]),np.array([br,br]))

def setup_traj_ax(ax,show_labels=False):
    ax.set_xlim(T_A-.01,T_TOT+.01); ax.set_ylim(-.45,2.7)
    ax.set_xticks([]); ax.set_yticks([CCW,TRANS,CW])
    ax.set_yticklabels(['CCW','TRANS','CW'],fontsize=7)
    ax.tick_params(axis='y',length=2,pad=1)
    ax.axvspan(T_S,T_E,color=C_TRANS,alpha=0.7,zorder=1)
    ax.axvline(T_B,color='#AAAAAA',lw=0.8,ls='--',zorder=2)
    for sp in ax.spines.values():
        sp.set_visible(True); sp.set_linewidth(0.8); sp.set_edgecolor(C_FRAME)
    if show_labels:
        for x,lbl in [((T_A+T_B)/2,'A only'),((T_B+T_S)/2,'A + B'),((T_S+T_E)/2,'T')]:
            ax.text(x,2.62,lbl,ha='center',va='top',fontsize=6.5,
                    color='#888888',style='italic')

def draw_traj(ax,is_cued,rot0,ca,cb):
    tA,vA,tB,vB=traj_arrays(is_cued,rot0)
    ax.plot(tA,vA,color=ca,lw=LW,ls='-',solid_capstyle='round',zorder=3)
    ax.plot(tB,vB,color=cb,lw=LW,ls='--',dashes=(6,3),zorder=3)

PANELS=[
    (0,0,True, False,C_RED,  C_GREEN),
    (1,0,False,True, C_GREEN,C_RED),
    (0,1,True, False,C_GREEN,C_RED),
    (1,1,False,True, C_RED,  C_GREEN),
    (0,2,True, True, C_RED,  C_GREEN),
    (1,2,False,False,C_GREEN,C_RED),
    (0,3,True, True, C_GREEN,C_RED),
    (1,3,False,False,C_RED,  C_GREEN),
]
COL_TITLES=[
    'Green trans.\n(CW → ↓)',
    'Red trans.\n(CW → ↓)',
    'Green trans.\n(CCW → ↑)',
    'Red trans.\n(CCW → ↑)',
]

# ── Write-up text ─────────────────────────────────────────────────────────────
INTRO = (
    "Two baseline sessions were collected to establish the delayed-onset cueing "
    "effect in the Meta Quest 3 VR environment. Stimuli consisted of two "
    "superimposed, oppositely rotating dot fields (one red, one green; ~63 dots "
    "each, 81°/s, aperture radius 3.5°) presented on a flat fronto-parallel "
    "plane at 2.0 m with zero stereo depth separation. One field had a delayed "
    "onset of 750 ms (Field B, dashed lines), establishing a temporal onset "
    "asymmetry that serves as the implicit cue. After a 300 ms rotation period "
    "following Field B onset, one field translated briefly (80 ms, ~2.26°/s) in "
    "one of 8 equally spaced directions (0–315°, step 45°). On CUED trials the "
    "delayed-onset field (Field B) translated; on UNCUED trials the non-delayed "
    "field (Field A) translated. Subjects reported the translation direction via "
    "thumbstick (8-AFC). All 8 stimulus permutations shown in the figure above "
    "were presented (2 rotation configs × 2 delayed-field colors × CUED/UNCUED), "
    "balanced across 8 translation headings, giving 64 trials per session. "
    "No swap manipulations were applied in these sessions."
)

FINDINGS_1 = (
    "Session 1 (260323_1534, pre-v0.2.0) yielded a strong cueing effect: "
    "CUED = 65.6%, UNCUED = 15.6%, Δ = +50.0 pp. A pronounced red-field "
    "advantage was present — accuracy was substantially higher when the red "
    "field translated than when the green field did, regardless of cueing "
    "status (CUED+Red = 81.2% vs. CUED+Green = 50.0%; UNCUED+Red = 25.0% "
    "vs. UNCUED+Green = 6.2%). This asymmetry most likely reflects imperfect "
    "iso-luminance equating: the heterochromatic flicker photometry calibration "
    "may not have fully equalised the perceptual salience of the two dot fields, "
    "leaving the red field physically more detectable. This session predates the "
    "v0.2.0 software version and should be treated as a preliminary observation."
)

FINDINGS_2 = (
    "Session 2 (260324_0716, v0.2.0) showed a reduced cueing effect: "
    "CUED = 53.1%, UNCUED = 25.0%, Δ = +28.1 pp. The red/green accuracy "
    "asymmetry was partially reversed relative to Session 1 (CUED+Red = 43.8%, "
    "CUED+Green = 62.5%), a pattern not yet explained — it may reflect sampling "
    "noise at n = 16/cell or an interaction with the cursor-jump artifact "
    "described below. Despite these caveats, the cueing effect itself is robust "
    "and directionally consistent across both sessions, confirming that the "
    "delayed-onset manipulation produces reliable attentional cueing in the "
    "VR environment."
)

ISSUES_1 = (
    "Software version v0.2.0 refers to the first formally version-stamped Quest "
    "build on the wip/quest-pilot branch. It introduced five changes relative to "
    "the pre-v0.2.0 build used in Session 1: (1) a subject-ID field and version "
    "number embedded in all data files, enabling post-hoc identification of which "
    "software generated a given dataset; (2) a 2-second delay before the response "
    "scene accepts thumbstick input, preventing the skip menu from auto-firing "
    "when the trigger remained held during a scene transition; (3) a corrected "
    "fixation-exclusion radius for dot spawning (0.5° → 1.1°), matching the "
    "physical extent of the crosshair arms; (4) randomised trial order seeded "
    "with the system tick count and logged per session for reproducibility; and "
    "(5) a lowered thumbstick deadzone threshold (0.5 → 0.3 normalised units), "
    "reducing the effort required to register a directional response."
)

ISSUES_2 = (
    "Cursor-jump artifact (Session 2 only): the Quest thumbstick controller "
    "occasionally snapped the response cursor to an adjacent 45° direction "
    "sector without intentional user movement. Because each of the 8 AFC "
    "sectors spans 45°, a single snap produced a scored error even when the "
    "subject's intended direction was correct. The effect was identified "
    "post-hoc from the distribution of response errors, approximately 25% "
    "of which were adjacent-sector (off-by-45°) responses — too frequent "
    "to be perceptual. The fix — thumbstick hysteresis (once a sector is "
    "latched, a >33° deflection from its centre is required to switch) plus "
    "two-stage confirmation (first trigger press locks the cursor to yellow; "
    "second press confirms and records) — was implemented in the subsequent "
    "software commit and has been active in all sessions since. Sessions 1 "
    "and 2 are the only contaminated baseline records in this dataset."
)

# ─────────────────────────────────────────────────────────────────────────────
# BUILD FIGURE — explicit coordinate layout
# ─────────────────────────────────────────────────────────────────────────────
fig = plt.figure(figsize=(FIG_W, FIG_H))
fig.patch.set_facecolor('white')

# Current y cursor (starts near top)
y = 0.975

# ── Title ─────────────────────────────────────────────────────────────────────
fig.text(0.50, y,
    'VRDots — Baseline Experiment: No Depth, No Swap',
    ha='center', va='top', fontsize=15, fontweight='bold', color='#111111')
y -= (15/72*DPI*1.3)/(FIG_H*DPI)   # advance by title height
y -= 0.008                           # gap

# ── Intro paragraph ───────────────────────────────────────────────────────────
intro_lines = textwrap.wrap(INTRO, width=WRAP_W)
fig.text(LMAR, y, '\n'.join(intro_lines),
    ha='left', va='top', fontsize=8.5, color='#222222', linespacing=1.55)
y -= len(intro_lines) * (8.5/72*DPI*1.55)/(FIG_H*DPI)
y -= 0.018   # gap before section heading

# ── "Stimulus Conditions" section heading ─────────────────────────────────────
fig.text(0.50, y, 'Stimulus Conditions',
    ha='center', va='top', fontsize=11, fontweight='bold', color='#1a3a6b')
y -= (11/72*DPI*1.3)/(FIG_H*DPI)
y -= 0.006   # gap before column titles (which appear inside panel top padding)

# ── Trajectory panels ─────────────────────────────────────────────────────────
TRAJ_H = 0.220    # height for the 2-row trajectory grid
traj_top = y
traj_bot = traj_top - TRAJ_H

traj_gs = gridspec.GridSpec(2, 4,
    top=traj_top, bottom=traj_bot,
    left=LMAR, right=RMAR,
    hspace=0.38, wspace=0.22)

for row,col,is_cued,rot0,ca,cb in PANELS:
    ax = fig.add_subplot(traj_gs[row,col])
    setup_traj_ax(ax, show_labels=(row==0 and col==0))
    draw_traj(ax, is_cued, rot0, ca, cb)
    if row==0:
        ax.set_title(COL_TITLES[col], fontsize=8, fontweight='bold', pad=4)
    if col==0:
        ax.set_ylabel('CUED' if is_cued else 'UNCUED',
                      fontsize=9, fontweight='bold', labelpad=4)

y = traj_bot - 0.010   # gap after trajectory panels

# ── Trajectory legend ─────────────────────────────────────────────────────────
TLEG_H = 0.026
ax_tleg = fig.add_axes([LMAR, y - TLEG_H, TXT_W, TLEG_H])
ax_tleg.axis('off')
tleg_handles = [
    mlines.Line2D([],[],color='#555555',lw=2,ls='-',
                  label='Field A — non-delayed (solid)'),
    mlines.Line2D([],[],color='#555555',lw=2,ls='--',dashes=(6,3),
                  label='Field B — delayed onset (dashed)'),
    mlines.Line2D([],[],color=C_RED,  lw=3, label='Red dot field'),
    mlines.Line2D([],[],color=C_GREEN,lw=3, label='Green dot field'),
    mpatches.Patch(facecolor=C_TRANS,alpha=0.8,edgecolor='#888888',
                   label='Translation window'),
]
ax_tleg.legend(handles=tleg_handles, loc='center', ncol=5, fontsize=8,
               frameon=True, framealpha=0.9, edgecolor='#CCCCCC')
y -= (TLEG_H + 0.016)

# ── "Results" section heading ─────────────────────────────────────────────────
fig.text(0.50, y, 'Results',
    ha='center', va='top', fontsize=11, fontweight='bold', color='#1a3a6b')
y -= (11/72*DPI*1.3)/(FIG_H*DPI)
y -= 0.008

# ── Bar graphs ────────────────────────────────────────────────────────────────
BAR_H = 0.210
bar_top = y
bar_bot = bar_top - BAR_H

bar_gs = gridspec.GridSpec(1, 2,
    top=bar_top, bottom=bar_bot,
    left=LMAR+0.02, right=RMAR-0.02,
    wspace=0.40)

for si,(sess_id,sess_label) in enumerate(SESSIONS):
    cnt=analyze(load_session(sess_id))
    cc_r=cnt.get(('CUED',  'R'),[0,1]); cc_g=cnt.get(('CUED',  'G'),[0,1])
    cu_r=cnt.get(('UNCUED','R'),[0,1]); cu_g=cnt.get(('UNCUED','G'),[0,1])
    ck=cc_r[0]+cc_g[0]; cn=cc_r[1]+cc_g[1]
    uk=cu_r[0]+cu_g[0]; un=cu_r[1]+cu_g[1]
    zv,pv=z_test(ck,cn,uk,un); delta=ck/cn - uk/un

    xs=[0.00,0.65,1.75,2.40]
    groups=[cc_r,cc_g,cu_r,cu_g]
    accs=[g[0]/g[1] for g in groups]
    cis=[wilson_ci(*g) for g in groups]
    bcolors=[C_RED,C_GREEN,C_RED,C_GREEN]
    hatch=['','','///','///']
    xlabels=['Red\ntrans.','Green\ntrans.','Red\ntrans.','Green\ntrans.']

    ax=fig.add_subplot(bar_gs[0,si])
    for xi,ac,(lo,hi),bc,ht,g in zip(xs,accs,cis,bcolors,hatch,groups):
        ax.bar(xi,ac,width=0.58,color=bc,alpha=0.82,hatch=ht,
               edgecolor='#333333',linewidth=0.8,zorder=3)
        ax.errorbar(xi,ac,yerr=[[ac-lo],[hi-ac]],
                    fmt='none',color='#222222',capsize=4,lw=1.5,zorder=4)
        ax.text(xi,ac+0.035,f'{g[0]}/{g[1]}',
                ha='center',fontsize=7,color='#333333')

    ax.axhline(CHANCE,color='#999999',ls='--',lw=1.0,zorder=2)
    ax.text(2.78,CHANCE+0.012,'chance\n(12.5%)',fontsize=7,
            color='#999999',va='bottom')

    mid_c=(xs[0]+xs[1])/2; mid_u=(xs[2]+xs[3])/2
    yb=max(accs)+0.14
    ax.annotate('',xy=(mid_u,yb),xytext=(mid_c,yb),
                arrowprops=dict(arrowstyle='-',color='#444444',lw=1.2))
    ax.text((mid_c+mid_u)/2, yb+0.025,
            f'Δ = +{delta*100:.1f} pp   {stars(pv)}',
            ha='center',va='bottom',fontsize=9.5,fontweight='bold',color='#111111')
    ax.text((mid_c+mid_u)/2, yb+0.095,
            f'z = {zv:.2f},  p = {pv:.3f}  (one-tailed)',
            ha='center',va='bottom',fontsize=7.5,color='#555555')

    ax.text((xs[0]+xs[1])/2,-0.10,'CUED',ha='center',fontsize=10,
            fontweight='bold',transform=ax.get_xaxis_transform())
    ax.text((xs[2]+xs[3])/2,-0.10,'UNCUED',ha='center',fontsize=10,
            fontweight='bold',transform=ax.get_xaxis_transform())
    ax.axvline(1.20,color='#DDDDDD',lw=1.0,zorder=1)
    ax.set_xlim(-0.42,3.08); ax.set_ylim(0,1.10)
    ax.set_xticks(xs); ax.set_xticklabels(xlabels,fontsize=8.5)
    ax.set_yticks([0,.25,.50,.75,1.0])
    ax.set_yticklabels(['0%','25%','50%','75%','100%'],fontsize=8.5)
    if si==0: ax.set_ylabel('Accuracy (%)',fontsize=9)
    ax.set_title(sess_label,fontsize=9.5,fontweight='bold',pad=10)
    ax.spines[['top','right']].set_visible(False)
    ax.tick_params(axis='x',length=0)

y = bar_bot - 0.012

# ── Bar legend ────────────────────────────────────────────────────────────────
BLEG_H = 0.024
ax_bleg = fig.add_axes([LMAR, y - BLEG_H, TXT_W, BLEG_H])
ax_bleg.axis('off')
bleg_handles = [
    mpatches.Patch(facecolor=C_RED,  alpha=0.82,edgecolor='#333333',
                   label='Red field translates'),
    mpatches.Patch(facecolor=C_GREEN,alpha=0.82,edgecolor='#333333',
                   label='Green field translates'),
    mpatches.Patch(facecolor='white',hatch='///',edgecolor='#333333',
                   label='UNCUED trials (hatched)'),
    mlines.Line2D([],[],color='#222222',lw=1.5,marker='|',markersize=6,
                  label='Wilson 95% CI'),
]
ax_bleg.legend(handles=bleg_handles, loc='center', ncol=4, fontsize=8.5,
               frameon=True, framealpha=0.9, edgecolor='#CCCCCC')
y -= (BLEG_H + 0.022)

# ── Narrative text ────────────────────────────────────────────────────────────
# Findings
fig.text(LMAR, y, 'Findings',
    ha='left', va='top', fontsize=10, fontweight='bold', color='#1a3a6b')
y -= (10/72*DPI*1.4)/(FIG_H*DPI) + 0.004

for para in [FINDINGS_1, FINDINGS_2]:
    lines = textwrap.wrap(para, width=WRAP_W)
    fig.text(LMAR, y, '\n'.join(lines),
        ha='left', va='top', fontsize=8.2, color='#222222', linespacing=1.55)
    y -= len(lines) * (8.2/72*DPI*1.55)/(FIG_H*DPI)
    y -= 0.010   # paragraph gap

y -= 0.012   # section gap

# Issues
fig.text(LMAR, y, 'Software version and known artifacts',
    ha='left', va='top', fontsize=10, fontweight='bold', color='#6b1a1a')
y -= (10/72*DPI*1.4)/(FIG_H*DPI) + 0.004

for para in [ISSUES_1, ISSUES_2]:
    lines = textwrap.wrap(para, width=WRAP_W)
    fig.text(LMAR, y, '\n'.join(lines),
        ha='left', va='top', fontsize=8.2, color='#222222', linespacing=1.55)
    y -= len(lines) * (8.2/72*DPI*1.55)/(FIG_H*DPI)
    y -= 0.010

print(f"Bottom of last text block: y = {y:.3f}  (should be > 0.02)")

fig.savefig(OUT_PATH, dpi=DPI, bbox_inches='tight', facecolor='white')
print(f"Saved: {OUT_PATH}")
