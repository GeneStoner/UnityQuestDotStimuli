#!/usr/bin/env python3
"""
decoupled_dots_factor_bars.py
------------------------------
Comprehensive factor overview for Exp_DecoupledDots_005m.
All factors labeled F1–F9; GLM factors (F1,F2,F3,F7) highlighted.

Panels (left: % correct, right: log-odds):
  Panel A  Cueing factors        — F1 dot, F2 depth-field, F3 color-field
  Panel B  Delayed-field props   — F4 depth, F5 color, F6 rotation
  Panel C  Translating-field props — F7 depth (=GLM F4), F8 color, F9 rotation

GLM equation (as fit in decoupled_dots_glm2.py):
  log-odds(correct) = β0 + β1·F1 + β2·F2 + β3·F3 + β7·F7
                       + β12·(F1×F2) + β17·(F1×F7) + β27·(F2×F7)
  All Fn binary (0 or 1).  F1=1:cued  F2=1:depth-kept  F3=1:color-kept  F7=1:Near

† Translating-field rotation = pre-translation rotational identity (dots translate during window).

Output:
  Agents/Figures/decoupled_dots_factor_bars.pdf
  Agents/SwapPilot/Figures/decoupled_dots_factor_bars.pdf
"""

import csv, datetime, math, os
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.backends.backend_pdf import PdfPages

DATE_STR = datetime.date.today().strftime('%Y-%m-%d')

# ── Paths ──────────────────────────────────────────────────────────────────────
SESSIONS = [
    ('/tmp/quest_pull3/files/vr_dots_session_260406_1532.tsv', False),
    ('/tmp/quest_pull3/files/vr_dots_session_260406_1754.tsv', True),
    ('/tmp/quest_pull3/files/vr_dots_session_260407_0643.tsv', True),
    ('/tmp/quest_pull3/files/vr_dots_session_260407_0731.tsv', False),
]
BASE    = os.path.normpath(os.path.join(os.path.dirname(__file__), '../../Agents/Figures'))
BASE_SP = os.path.normpath(os.path.join(os.path.dirname(__file__), '../../Agents/SwapPilot/Figures'))
OUT_PDF    = os.path.join(BASE,    'decoupled_dots_factor_bars.pdf')
OUT_PDF_SP = os.path.join(BASE_SP, 'decoupled_dots_factor_bars.pdf')
CHANCE = 1 / 8

# ── Stats helpers ──────────────────────────────────────────────────────────────
def is_correct(td, rd):
    d = (float(rd) - float(td) + 360) % 360
    return (360 - d if d > 180 else d) <= 22.5

def wilson_ci(k, n, z=1.96):
    if n == 0: return 0.0, 0.0
    p = k / n; d = 1 + z**2/n
    c = (p + z**2/(2*n)) / d
    hw = z * math.sqrt(p*(1-p)/n + z**2/(4*n**2)) / d
    return c - hw, c + hw

def logit(p):
    return math.log(max(min(p, 1-1e-6), 1e-6) / (1 - max(min(p, 1-1e-6), 1e-6)))

CHANCE_LO = logit(CHANCE)

# ── Data loading ───────────────────────────────────────────────────────────────
def load_all():
    trials = []
    for path, is_inv in SESSIONS:
        with open(path, newline='') as f:
            for r in csv.DictReader(f, delimiter='\t'):
                if (not r.get('TransDeg','').strip() or
                        not r.get('RespDeg','').strip() or
                        r.get('EndKey','') in ('timeout','skip','requeue')):
                    continue
                cond = r['Cond']
                if is_inv:
                    cond = 'UNCUED' if cond == 'CUED' else 'CUED'

                b_green = (r['DelayedFieldColor'] == 'G') ^ is_inv
                b_near  = (r['DelayedFieldDepth']  == 'N') ^ is_inv
                b_cw    = (int(r['RotCfg']) == 1)   # RotCfg=1 → Field B=CW
                swap    = r['SwapType']

                # Cueing factors (binary 0/1)
                F1 = 1 if cond == 'CUED' else 0
                F2 = int((cond == 'CUED'   and swap in ('N','C')) or
                         (cond == 'UNCUED' and swap in ('Z','CZ')))
                F3 = int((cond == 'CUED'   and swap in ('N','Z')) or
                         (cond == 'UNCUED' and swap in ('C','CZ')))

                # Delayed field properties (Field B, canonical)
                del_near  = int(b_near)
                del_green = int(b_green)
                del_cw    = int(b_cw)

                # Translating field properties
                if cond == 'CUED':
                    trans_near  = int(b_near)
                    trans_green = int(b_green)
                    trans_cw    = int(b_cw)
                else:
                    trans_near  = int(not b_near)
                    trans_green = int(not b_green)
                    trans_cw    = int(not b_cw)

                trials.append(dict(
                    correct     = int(is_correct(r['TransDeg'], r['RespDeg'])),
                    F1=F1, F2=F2, F3=F3,
                    del_near=del_near, del_green=del_green, del_cw=del_cw,
                    trans_near=trans_near, trans_green=trans_green, trans_cw=trans_cw,
                ))
    return pd.DataFrame(trials)

# ── Factor definitions ─────────────────────────────────────────────────────────
# Each dict: fnum, in_glm, col, vL, lblL, cL, vR, lblR, cR, short_name, coding
#   vL = value of `col` for left bar (positive/better condition)
#   in_glm = True if this factor appears in GLM (gets bold box highlight)

PANEL_A = [  # Cueing factors  (all three in GLM)
    dict(fnum='F1', in_glm=True,
         col='F1',
         vL=1, lblL='Cued',    cL='#333333',
         vR=0, lblR='Uncued',  cR='#bbbbbb',
         short='Dot cueing',
         coding='F1=1: cued, 0: uncued'),
    dict(fnum='F2', in_glm=True,
         col='F2',
         vL=1, lblL='Depth\ncued',   cL='#116688',
         vR=0, lblR='Depth\nuncued', cR='#cc7733',
         short='Depth-field\ncueing',
         coding='F2=1: depth-cued, 0: depth-uncued'),
    dict(fnum='F3', in_glm=True,
         col='F3',
         vL=1, lblL='Color\ncued',   cL='#226622',
         vR=0, lblR='Color\nuncued', cR='#ddaa44',
         short='Color-field\ncueing',
         coding='F3=1: color-cued, 0: color-uncued'),
]

PANEL_B = [  # Delayed-field properties  (none in GLM)
    dict(fnum='F4', in_glm=False,
         col='del_near',
         vL=0, lblL='Del Far',   cL='#4477bb',
         vR=1, lblR='Del Near',  cR='#993333',
         short='Delayed\ndepth',
         coding='F4=1: delayed field Near'),
    dict(fnum='F5', in_glm=False,
         col='del_green',
         vL=0, lblL='Del Red',   cL='#cc3333',
         vR=1, lblR='Del Green', cR='#336633',
         short='Delayed\ncolor',
         coding='F5=1: delayed field Green'),
    dict(fnum='F6', in_glm=False,
         col='del_cw',
         vL=0, lblL='Del CCW',  cL='#885500',
         vR=1, lblR='Del CW',   cR='#555588',
         short='Delayed\nrotation',
         coding='F6=1: delayed field CW'),
]

PANEL_C = [  # Translating-field properties  (F7 in GLM as "F4")
    dict(fnum='F7', in_glm=True,
         col='trans_near',
         vL=0, lblL='Trans Far',  cL='#4477bb',
         vR=1, lblR='Trans Near', cR='#993333',
         short='Trans depth\n(Near penalty)',
         coding='F7=1: trans Near, 0: Far  [GLM F4]'),
    dict(fnum='F8', in_glm=False,
         col='trans_green',
         vL=0, lblL='Trans Red',   cL='#cc3333',
         vR=1, lblR='Trans Green', cR='#336633',
         short='Trans\ncolor',
         coding='F8=1: trans Green'),
    dict(fnum='F9', in_glm=False,
         col='trans_cw',
         vL=0, lblL='Trans CCW',  cL='#885500',
         vR=1, lblR='Trans CW†',  cR='#555588',
         short='Trans\nrotation†',
         coding='F9=1: trans CW (pre-trans identity)'),
]

PANELS = [
    ('A  —  Cueing factors', PANEL_A),
    ('B  —  Delayed-field properties', PANEL_B),
    ('C  —  Translating-field properties', PANEL_C),
]

# GLM as actually fit (decoupled_dots_glm2.py)
# All Fn = 0 or 1 (binary).  F7 here = GLM script's F4 (translator Near/Far).
# Interactions selected a priori: dot×depth, dot×plane, depth×plane.
# Color (F3) entered as additive only — F1×F3, F2×F3 not tested.
GLM_EQ   = ('log-odds(correct)  =  \u03b20  +  \u03b21\u00b7F1  +  \u03b22\u00b7F2  '
            '+  \u03b23\u00b7F3  +  \u03b27\u00b7F7\n'
            '    +  \u03b212\u00b7(F1\u00d7F2)  +  \u03b217\u00b7(F1\u00d7F7)  '
            '+  \u03b227\u00b7(F2\u00d7F7)')
GLM_NOTE = ('Each Fn \u2208 {0, 1}  (binary predictor).  '
            'F1=1: cued \u00b7 F2=1: depth kept \u00b7 F3=1: color kept \u00b7 F7=1: trans Near (Far=0).\n'
            'F4\u2013F6, F8\u2013F9 shown for reference; not in GLM.  '
            'F3 entered additively only (no interaction terms).')

# ── Bar geometry ───────────────────────────────────────────────────────────────
BAR_W    = 0.28
PAIR_W   = 0.68   # x-distance between centres of paired bars
GRPGAP   = 0.52   # gap between factor groups within a panel
PANELGAP = 0.85   # gap between panels

def factor_x_positions(panels):
    """Return list of (xL, xR) per factor, and list of panel separator xs."""
    positions, seps = [], []
    x = 0.0
    for pi, (_, facs) in enumerate(panels):
        if pi > 0:
            seps.append(x + PANELGAP/2)
            x += PANELGAP
        for fi in range(len(facs)):
            if fi > 0:
                x += GRPGAP
            positions.append((x, x + PAIR_W))
            x += PAIR_W
    return positions, seps

def draw_panel(ax, df, panels, positions, seps, use_lo):
    """Draw one axis (% correct or log-odds) with all 9 factor pairs."""
    ylim_max = 80 if not use_lo else 1.5
    ylim_min = 0  if not use_lo else -2.8

    # ── Compute stats and draw bars ────────────────────────────────────────────
    for pidx, (_, facs) in enumerate(panels):
        offset = sum(len(p[1]) for p in panels[:pidx])
        for fi, fspec in enumerate(facs):
            gi = offset + fi
            xL, xR = positions[gi]
            col_key = fspec['col']

            for xi, val_filter, lbl, col_c in [
                    (xL, fspec['vL'], fspec['lblL'], fspec['cL']),
                    (xR, fspec['vR'], fspec['lblR'], fspec['cR'])]:
                sub = df[df[col_key] == val_filter]
                k, n = int(sub['correct'].sum()), len(sub)
                p = k / n
                lo, hi = wilson_ci(k, n)

                if use_lo:
                    val = logit(p)
                    elo = val - logit(max(lo, 1e-5))
                    ehi = logit(min(hi, 1-1e-5)) - val
                else:
                    val = p * 100
                    elo, ehi = val - lo*100, hi*100 - val

                alpha = 0.88 if not use_lo else 0.80
                ax.bar(xi, val, width=BAR_W, color=col_c, alpha=alpha,
                       edgecolor='white', zorder=2)
                ax.errorbar(xi, val, yerr=[[elo],[ehi]], fmt='none',
                            ecolor='#333333', elinewidth=0.9, capsize=2.5, zorder=3)

                # Value label above bar
                vstr = f'{val:.0f}%' if not use_lo else f'{val:+.2f}'
                ax.text(xi, val + ehi + (1.0 if not use_lo else 0.06),
                        vstr, ha='center', va='bottom', fontsize=5.5,
                        color='#444444')

                # Condition label below axis
                label_y = (ylim_min - 3.5 if not use_lo else ylim_min - 0.32)
                ax.text(xi, label_y, lbl,
                        ha='center', va='top', fontsize=6, clip_on=False)

            # ── Delta bracket ──────────────────────────────────────────────────
            subL = df[df[col_key] == fspec['vL']]
            subR = df[df[col_key] == fspec['vR']]
            kL, nL = int(subL['correct'].sum()), len(subL)
            kR, nR = int(subR['correct'].sum()), len(subR)
            pL, pR = kL/nL, kR/nR
            loL, hiL = wilson_ci(kL, nL)
            loR, hiR = wilson_ci(kR, nR)
            if use_lo:
                vLv = logit(pL); vRv = logit(pR)
                eLhi = logit(min(hiL, 1-1e-5)) - vLv
                eRhi = logit(min(hiR, 1-1e-5)) - vRv
                bkt  = max(vLv + eLhi, vRv + eRhi) + 0.14
                dstr = f'{vLv - vRv:+.2f}'
            else:
                vLv = pL*100; vRv = pR*100
                eLhi = hiL*100 - vLv; eRhi = hiR*100 - vRv
                bkt  = max(vLv + eLhi, vRv + eRhi) + 3.5
                dstr = f'{vLv - vRv:+.1f} pp'

            ax.annotate('', xy=(xR, bkt), xytext=(xL, bkt),
                        arrowprops=dict(arrowstyle='<->', color='#555555', lw=0.9))
            delta = vLv - vRv
            ax.text((xL+xR)/2, bkt + (0.7 if not use_lo else 0.04),
                    dstr, ha='center', va='bottom', fontsize=7, fontweight='bold',
                    color='#1a6ab5' if delta > 0 else '#c0392b')

            # ── F-number label (above delta bracket) ──────────────────────────
            fnum_y = (ylim_max - 1 if not use_lo else ylim_max - 0.03)
            cx = (xL + xR) / 2
            in_glm = fspec['in_glm']
            fnum_color  = '#1a3a8b' if in_glm else '#888888'
            fnum_weight = 'bold'    if in_glm else 'normal'
            fnum_bbox = (dict(boxstyle='round,pad=0.2', facecolor='#ddeeff',
                              edgecolor='#1a3a8b', lw=1.0)
                         if in_glm
                         else dict(boxstyle='round,pad=0.2', facecolor='#eeeeee',
                                   edgecolor='#aaaaaa', lw=0.5))
            ax.text(cx, fnum_y, fspec['fnum'],
                    ha='center', va='top', fontsize=8,
                    fontweight=fnum_weight, color=fnum_color,
                    bbox=fnum_bbox, clip_on=False)

            # ── Short factor name just below F-number ──────────────────────────
            fname_y = (ylim_max - 7.5 if not use_lo else ylim_max - 0.19)
            short = fspec['short']
            ax.text(cx, fname_y, short,
                    ha='center', va='top', fontsize=6,
                    color='#333333' if in_glm else '#888888',
                    clip_on=False)

    # ── Panel separator lines ──────────────────────────────────────────────────
    for sx in seps:
        ax.axvline(sx, color='#cccccc', lw=1.0, ls='--', zorder=0)

    # ── Panel header labels ────────────────────────────────────────────────────
    for pidx, (title, facs) in enumerate(panels):
        offset = sum(len(p[1]) for p in panels[:pidx])
        xs = [positions[offset + fi] for fi in range(len(facs))]
        all_x = [x for pair in xs for x in pair]
        cx = (min(all_x) + max(all_x)) / 2
        hdr_y = (ylim_max + 9 if not use_lo else ylim_max + 0.26)
        ax.text(cx, hdr_y, title,
                ha='center', va='bottom', fontsize=8.5, fontweight='bold',
                color='#1a3a8b', style='italic', clip_on=False)

    # ── Reference lines and axis formatting ───────────────────────────────────
    xmax = positions[-1][1] + BAR_W + 0.5
    if not use_lo:
        ax.axhline(CHANCE*100, color='#cc4444', lw=0.8, ls='--', zorder=1)
        ax.set_ylim(ylim_min, ylim_max)
        ax.set_yticks([0, 12.5, 25, 50, 75])
        ax.set_yticklabels(['0','12.5','25','50','75'], fontsize=7)
        ax.set_ylabel('% correct', fontsize=10)
        ax.set_title('Raw accuracy  (% correct)', fontsize=10,
                     fontweight='bold', pad=4)
        ax.text(xmax + 0.1, CHANCE*100 + 0.5, 'chance\n(12.5%)',
                fontsize=5.5, color='#cc4444', va='bottom')
    else:
        ax.axhline(CHANCE_LO, color='#cc4444', lw=0.8, ls='--', zorder=1)
        ax.axhline(0.0,       color='#666666', lw=0.7, ls='-',  zorder=1)
        ax.set_ylim(ylim_min, ylim_max)
        ax.set_yticks([-2, CHANCE_LO, -1, 0, 1])
        ax.set_yticklabels(['-2.0', 'chance\n(\u22121.95)', '\u22121.0', '0.0\n(50%)', '+1.0'],
                           fontsize=7)
        ax.set_ylabel('Log-odds of correct', fontsize=10)
        ax.set_title('Same data — log-odds scale\n(what the GLM models)',
                     fontsize=10, fontweight='bold', pad=4)
        ax.text(xmax + 0.05, CHANCE_LO + 0.04, 'chance\n(\u22121.95)',
                fontsize=5.5, color='#cc4444', va='bottom')
        ax.text(xmax + 0.05, 0.04, '50%\n(0.00)',
                fontsize=5.5, color='#666666', va='bottom')

    ax.set_xlim(-BAR_W*1.5, xmax + 0.8)
    ax.set_xticks([])
    ax.spines[['top','right','bottom']].set_visible(False)
    ax.yaxis.grid(True, lw=0.35, color='#e8e8e8', zorder=0)
    ax.set_axisbelow(True)


# ── Main ───────────────────────────────────────────────────────────────────────
os.makedirs(BASE, exist_ok=True)
os.makedirs(BASE_SP, exist_ok=True)

df = load_all()
print(f'Total valid trials: {len(df)}')

positions, seps = factor_x_positions(PANELS)

fig = plt.figure(figsize=(16, 9))

# ── Figure-level header ────────────────────────────────────────────────────────
fig.text(0.5, 0.985,
         'Exp_DecoupledDots_005m  \u2014  Accuracy by factor  (n\u202f=\u202f2051,  4 sessions)',
         ha='center', va='top', fontsize=12, fontweight='bold')

# ── GLM equation box ──────────────────────────────────────────────────────────
eq_y = 0.948
fig.text(0.5, eq_y, GLM_EQ,
         ha='center', va='top', fontsize=9, family='monospace',
         color='#1a3a8b',
         bbox=dict(boxstyle='round,pad=0.45', facecolor='#f0f4ff',
                   edgecolor='#1a3a8b', lw=0.8))

# ── Binary coding note ────────────────────────────────────────────────────────
note_y = eq_y - 0.085
fig.text(0.5, note_y, GLM_NOTE,
         ha='center', va='top', fontsize=7.5, color='#333333',
         style='italic',
         bbox=dict(boxstyle='round,pad=0.35', facecolor='#fafafa',
                   edgecolor='#cccccc', lw=0.6))

# ── Axes ──────────────────────────────────────────────────────────────────────
gs = gridspec.GridSpec(1, 2, figure=fig,
                       left=0.05, right=0.97, bottom=0.17, top=0.78,
                       wspace=0.10)
ax_pct = fig.add_subplot(gs[0, 0])
ax_lo  = fig.add_subplot(gs[0, 1])

draw_panel(ax_pct, df, PANELS, positions, seps, use_lo=False)
draw_panel(ax_lo,  df, PANELS, positions, seps, use_lo=True)

# ── Legend: GLM vs reference factors ─────────────────────────────────────────
from matplotlib.patches import Patch
legend_elements = [
    Patch(facecolor='#ddeeff', edgecolor='#1a3a8b', lw=1.0,
          label='In GLM  (F1, F2, F3, F7)'),
    Patch(facecolor='#eeeeee', edgecolor='#aaaaaa', lw=0.5,
          label='Reference only  (F4\u2013F6, F8\u2013F9)'),
]
fig.legend(handles=legend_elements, loc='lower center',
           bbox_to_anchor=(0.5, 0.085), ncol=2, fontsize=8,
           framealpha=0.9, edgecolor='#cccccc')

# ── Footnotes ─────────────────────────────────────────────────────────────────
fname = os.path.basename(OUT_PDF_SP)
fig.text(0.5, 0.025,
         '\u2020 F9 translating-field rotation = pre-translation rotational identity of that field'
         '  (during the translation window, dots translate — they do not rotate)',
         ha='center', va='top', fontsize=6.5, color='#555555', style='italic')
fig.text(0.01, 0.005, f'{fname}  \u00b7  {DATE_STR}',
         fontsize=5, color='#888888', ha='left', va='bottom')
fig.text(0.99, 0.005, 'p. 1/1',
         fontsize=5, color='#888888', ha='right', va='bottom')

for out in [OUT_PDF, OUT_PDF_SP]:
    with PdfPages(out) as pdf:
        pdf.savefig(fig, bbox_inches='tight')
plt.close(fig)
print(f'Saved: {OUT_PDF}')
print(f'Saved: {OUT_PDF_SP}')
