#!/usr/bin/env python3
"""
decoupled_dots_glm_intro.py
----------------------------
Combined GLM analysis — Exp 1 (DecoupledDots) + Exp 2 (DepthColorLinked)
13-page PDF:
  Pages 1–7  : DecoupledDots — intro, factor bars, coefficients, conditional AMEs,
               interpretation, predicted vs observed, F4 Near/Far
  Page  8    : DepthColorLinked — design + predictors
  Pages 9–12 : DepthColorLinked — factor bars, coefficients + conditional AMEs,
               interpretation + key conditions, predicted vs observed
  Page  13   : Cross-experiment synthesis + Far>Near hypothesis

Exp 1: Exp_DecoupledDots_005m + Inv; n=2051; /tmp/quest_pull3/
Exp 2: Exp_DepthColorLinked_005m;   n=1024; /tmp/quest_pull2/
Single observer (GS)

Output:
  Agents/Figures/glm_combined_analysis.pdf
  Agents/SwapPilot/Figures/glm_combined_analysis.pdf
"""

import csv, datetime, math, os, textwrap
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.backends.backend_pdf import PdfPages

try:
    import statsmodels.api as sm
except ImportError:
    raise ImportError('statsmodels required: pip install statsmodels')

DATE_STR = datetime.date.today().strftime('%Y-%m-%d')

# ── Paths ──────────────────────────────────────────────────────────────────────
SESSIONS = [
    ('/tmp/quest_pull3/files/vr_dots_session_260406_1532.tsv', False),
    ('/tmp/quest_pull3/files/vr_dots_session_260406_1754.tsv', True),
    ('/tmp/quest_pull3/files/vr_dots_session_260407_0643.tsv', True),
    ('/tmp/quest_pull3/files/vr_dots_session_260407_0731.tsv', False),
]
SESSION_LABELS = 'S1 (260406_1532) · S2-inv (260406_1754) · S3-inv (260407_0643) · S4 (260407_0731)'
ASSET_LABEL    = 'Exp_DecoupledDots_005m  +  Exp_DecoupledDots_Inv_005m'

BASE    = os.path.normpath(os.path.join(os.path.dirname(__file__), '../../Agents/Figures'))
BASE_SP = os.path.normpath(os.path.join(os.path.dirname(__file__), '../../Agents/SwapPilot/Figures'))
OUT_PDF    = os.path.join(BASE,    'glm_combined_analysis.pdf')
OUT_PDF_SP = os.path.join(BASE_SP, 'glm_combined_analysis.pdf')
CHANCE = 1/8

# ── Stats helpers ──────────────────────────────────────────────────────────────
def is_correct(td, rd):
    d = (float(rd) - float(td) + 360) % 360
    return (360 - d if d > 180 else d) <= 22.5

def wilson_ci(k, n, z=1.96):
    if n == 0: return 0.0, 0.0
    p = k/n; denom = 1 + z**2/n
    c = (p + z**2/(2*n)) / denom
    hw = z * math.sqrt(p*(1-p)/n + z**2/(4*n**2)) / denom
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
                swap    = r['SwapType']
                F1 = 1 if cond == 'CUED' else 0
                F2 = int((cond == 'CUED'   and swap in ('N','C')) or
                         (cond == 'UNCUED' and swap in ('Z','CZ')))
                F3 = int((cond == 'CUED'   and swap in ('N','Z')) or
                         (cond == 'UNCUED' and swap in ('C','CZ')))
                trans_near = b_near if cond == 'CUED' else not b_near
                F4 = 0 if trans_near else 1  # F4=1 = Far, F4=0 = Near
                trials.append(dict(
                    correct=int(is_correct(r['TransDeg'], r['RespDeg'])),
                    F1=F1, F2=F2, F3=F3, F4=F4,
                ))
    return pd.DataFrame(trials)

# ── GLM fitting ────────────────────────────────────────────────────────────────
def fit_glm(df):
    df2 = df.copy()
    df2['F1_F2'] = df2['F1'] * df2['F2']
    df2['F1_F4'] = df2['F1'] * df2['F4']
    df2['F2_F4'] = df2['F2'] * df2['F4']
    predictors = ['F1', 'F2', 'F3', 'F4', 'F1_F2', 'F1_F4', 'F2_F4']
    X = sm.add_constant(df2[predictors].astype(float))
    y = df2['correct'].astype(float)
    model = sm.Logit(y, X).fit(disp=False)
    return model, df2, predictors

DD_IX  = ['F1_F2', 'F1_F4', 'F2_F4']
DCL_IX = ['F1_F2', 'F1_F3', 'F2_F3']

def compute_ame(model, df2, var, predictors, ix_cols=None):
    if ix_cols is None: ix_cols = DD_IX
    d1 = df2.copy(); d0 = df2.copy()
    d1[var] = 1; d0[var] = 0
    for col in ix_cols:
        parts = col.split('_')
        d1[col] = d1[parts[0]] * d1[parts[1]]
        d0[col] = d0[parts[0]] * d0[parts[1]]
    X1 = sm.add_constant(d1[predictors].astype(float), has_constant='add')
    X0 = sm.add_constant(d0[predictors].astype(float), has_constant='add')
    return (model.predict(X1) - model.predict(X0)).mean() * 100

def pstars(p):
    if p < 0.001: return '***'
    if p < 0.010: return '**'
    if p < 0.050: return '*'
    if p < 0.100: return '\u2020'
    return 'n.s.'


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 1 — Text
# ══════════════════════════════════════════════════════════════════════════════
TITLE    = 'GLM Analysis: Logistic Regression'
SUBTITLE = 'Single observer (GS)  \u00b7  n\u202f=\u202f2051 valid trials  \u00b7  4 sessions'
DATASET  = (f'Asset: {ASSET_LABEL}\n'
            f'Sessions: {SESSION_LABELS}')

FACTOR_DEFS = [
    ('F1', 'dot-onset cueing',
     '1\u202f=\u202fdelayed-onset field translates (cued);  0\u202f=\u202fnon-delayed field translates (uncued)'),
    ('F2', 'depth-field cueing',
     '1\u202f=\u202ftranslating field\u2019s depth-plane identity matches the delayed-onset field (depth-cued);  0\u202f=\u202fdepth-uncued'),
    ('F3', 'color-field cueing',
     '1\u202f=\u202ftranslating field\u2019s color identity matches the delayed-onset field (color-cued);  0\u202f=\u202fcolor-uncued'),
    ('F4', 'translator depth plane',
     '1\u202f=\u202fFar;  0\u202f=\u202fNear   [covariate; see rationale]'),
]

MODEL_EQ = ('log-odds(correct)  =  \u03b20'
            '  +  \u03b21\u00b7F1  +  \u03b22\u00b7F2  +  \u03b23\u00b7F3  +  \u03b24\u00b7F4\n'
            '    +  \u03b212\u00b7(F1\u00d7F2)  +  \u03b214\u00b7(F1\u00d7F4)  +  \u03b224\u00b7(F2\u00d7F4)')

PARAS = [
    (
        "Trial-level accuracy (correct/incorrect) was modeled using binary logistic regression. "
        "Three predictors were specified a priori by the experimental design. "
        "F1 (dot-onset cueing) coded whether the field with the delayed onset was the translating "
        "field (1\u202f=\u202fcued, 0\u202f=\u202funcued). "
        "F2 (depth-field cueing) coded whether the translating field\u2019s depth-plane "
        "identity matched that of the delayed-onset field\u2014that is, whether depth-plane "
        "membership tracked the temporal cue "
        "(1\u202f=\u202fdepth-cued, 0\u202f=\u202fdepth-uncued). "
        "F3 (color-field cueing) coded the analogous property for surface color "
        "(1\u202f=\u202fcolor-cued, 0\u202f=\u202fcolor-uncued). "
        "These three factors are fully crossed in the design\u2014their combinations define "
        "the four swap conditions\u2014and no prior observation was required to motivate their inclusion."
    ),
    (
        "F4 (translator depth plane; 1\u202f=\u202fFar, 0\u202f=\u202fNear) was included as "
        "an empirically motivated covariate. "
        "Prior to this experiment, a robust Far\u202f>\u202fNear performance advantage was "
        "observed across independent sessions\u2014parametric depth sweeps across a fourfold "
        "separation range and binocular-vs.-monocular comparisons\u2014establishing a "
        "stereoscopic origin. "
        "Including F4 adjusts for this known source of variance and sharpens the "
        "cueing-factor estimates. "
        "The F4 asymmetry and its interactions are discussed on p.\u202f7."
    ),
    (
        "The model included all four main effects and three interaction terms motivated by "
        "the experimental logic. "
        "F1\u202f\u00d7\u202fF2 tests the central question of the experiment: whether "
        "dot-onset cueing is effective only when the depth-plane identity of the translating "
        "field matches the identity established during the cue interval\u2014that is, whether "
        "temporal and depth-plane cueing operate conjunctively rather than independently. "
        "F1\u202f\u00d7\u202fF4 asks whether the dot-onset cueing benefit is itself "
        "depth-plane specific, operating more effectively at one stereoscopic depth than the other. "
        "F2\u202f\u00d7\u202fF4 asks whether depth-field cueing is depth-plane "
        "specific\u2014whether the attentional advantage conferred by matching depth-plane "
        "identity differs between the near and far planes. "
        "Color (F3) was entered as an additive term only; no interactions involving F3 were "
        "pre-specified, and none are reported. "
        "All predictors are binary (0 or 1). "
        "Coefficients were estimated by maximum likelihood, and effect sizes are reported as "
        "average marginal effects (AMEs) in percentage points, computed by averaging the "
        "predicted change in response probability across the observed distribution of covariates."
    ),
]

def make_text_page():
    fig = plt.figure(figsize=(8.5, 11))
    fig.patch.set_facecolor('white')

    y = 0.945
    lh  = 0.0215
    lhs = 0.017
    gap = 0.026
    W   = 88

    # ── Title & subtitle ──────────────────────────────────────────────────────
    fig.text(0.10, y, TITLE, fontsize=15, fontweight='bold',
             color='#1a1a2e', fontfamily='serif', va='top')
    y -= 0.032
    fig.text(0.10, y, SUBTITLE, fontsize=9.5, color='#555555',
             fontfamily='serif', style='italic', va='top')
    y -= 0.020

    # Horizontal rule
    fig.add_axes([0.10, y, 0.80, 0.001]).set_facecolor('#333333')
    fig.axes[-1].axis('off')
    y -= 0.012

    # Dataset info
    for line in DATASET.split('\n'):
        fig.text(0.10, y, line, fontsize=8.5, color='#444444',
                 fontfamily='monospace', va='top')
        y -= lhs * 1.2
    y -= 0.008

    # Second rule
    fig.add_axes([0.10, y, 0.80, 0.0008]).set_facecolor('#bbbbbb')
    fig.axes[-1].axis('off')
    y -= 0.016

    # ── Predictors header ─────────────────────────────────────────────────────
    fig.text(0.10, y, 'Predictors', fontsize=11, fontweight='bold',
             color='#1a1a2e', fontfamily='serif', va='top')
    y -= lh * 1.4

    for fnum, fname, coding in FACTOR_DEFS:
        # Coloured tag
        ax_b = fig.add_axes([0.10, y - 0.007, 0.030, 0.017])
        ax_b.set_facecolor('#ddeeff')
        for sp in ax_b.spines.values():
            sp.set_edgecolor('#1a3a8b'); sp.set_linewidth(0.8)
        ax_b.set_xticks([]); ax_b.set_yticks([])
        ax_b.text(0.5, 0.5, fnum, ha='center', va='center',
                  fontsize=10, fontweight='bold', color='#1a3a8b',
                  transform=ax_b.transAxes)
        fig.text(0.143, y, fname, fontsize=10.5, fontweight='bold',
                 color='#222222', fontfamily='serif', va='top')
        y -= lh
        fig.text(0.143, y, coding, fontsize=9, color='#555555',
                 fontfamily='serif', style='italic', va='top')
        y -= lhs * 1.9

    y -= 0.004

    # ── Equation — rendered in a dedicated axes for reliable bbox ─────────────
    eq_h = 0.052   # height in figure fraction (two lines at ~10pt on 11-inch page)
    ax_eq = fig.add_axes([0.10, y - eq_h, 0.80, eq_h])
    ax_eq.set_facecolor('#f0f4ff')
    for sp in ax_eq.spines.values():
        sp.set_edgecolor('#1a3a8b'); sp.set_linewidth(0.8)
    ax_eq.set_xticks([]); ax_eq.set_yticks([])
    ax_eq.text(0.5, 0.5, MODEL_EQ, ha='center', va='center',
               fontsize=9.5, fontfamily='monospace', color='#1a3a8b',
               transform=ax_eq.transAxes, linespacing=1.6)
    y -= (eq_h + 0.016)

    # ── Rationale header ──────────────────────────────────────────────────────
    fig.add_axes([0.10, y, 0.80, 0.0008]).set_facecolor('#bbbbbb')
    fig.axes[-1].axis('off')
    y -= 0.016

    fig.text(0.10, y, 'Rationale', fontsize=11, fontweight='bold',
             color='#1a1a2e', fontfamily='serif', va='top')
    y -= lh * 1.5

    # ── Body paragraphs ───────────────────────────────────────────────────────
    for para in PARAS:
        for line in textwrap.wrap(para, width=W):
            fig.text(0.10, y, line, fontsize=9.5, color='#111111',
                     fontfamily='serif', va='top')
            y -= 0.018
        y -= 0.018

    # Cross-reference note
    fig.text(0.10, y - 0.004,
             'Coefficient estimates, AMEs, and conditional AMEs: see pp.\u202f3\u20134.',
             fontsize=8.5, color='#666666', style='italic',
             fontfamily='serif', va='top')

    # Footer
    fname_str = os.path.basename(OUT_PDF_SP)
    fig.text(0.10, 0.028, f'{fname_str}  \u00b7  {DATE_STR}  \u00b7  p.\u202f1/13',
             fontsize=7.5, color='#888888', fontfamily='serif', va='top')
    return fig


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 2 — Factor bar figure (F1–F4)
# ══════════════════════════════════════════════════════════════════════════════
FACTORS = [
    dict(fnum='F1', col='F1',
         vL=1, lblL='Cued',   cL='#333333',
         vR=0, lblR='Uncued', cR='#bbbbbb',
         name='Dot Cueing'),
    dict(fnum='F2', col='F2',
         vL=1, lblL='Cued',   cL='#116688',
         vR=0, lblR='Uncued', cR='#cc7733',
         name='Depth Cueing'),
    dict(fnum='F3', col='F3',
         vL=1, lblL='Cued',   cL='#226622',
         vR=0, lblR='Uncued', cR='#ddaa44',
         name='Color Cueing'),
    dict(fnum='F4', col='F4',
         vL=1, lblL='Far',  cL='#4477bb',
         vR=0, lblR='Near', cR='#993333',
         name='Translator\nDepth Plane'),
]

BAR_W  = 0.28
PAIR_W = 0.72
GAP    = 0.65

def get_positions(factors=None):
    if factors is None: factors = FACTORS
    positions, x = [], 0.0
    for i in range(len(factors)):
        if i > 0: x += GAP
        positions.append((x, x + PAIR_W))
        x += PAIR_W
    return positions

def draw_bars(ax, df, positions, use_lo, factors=None):
    if factors is None: factors = FACTORS
    ylim_max = 80 if not use_lo else 1.5
    ylim_min = 0  if not use_lo else -2.8

    for fi, fspec in enumerate(factors):
        xL, xR = positions[fi]
        col_key = fspec['col']

        for xi, val_filter, lbl, col_c in [
                (xL, fspec['vL'], fspec['lblL'], fspec['cL']),
                (xR, fspec['vR'], fspec['lblR'], fspec['cR'])]:
            sub = df[df[col_key] == val_filter]
            k, n = int(sub['correct'].sum()), len(sub)
            p = k/n
            lo, hi = wilson_ci(k, n)
            if use_lo:
                val = logit(p)
                elo = val - logit(max(lo, 1e-5))
                ehi = logit(min(hi, 1-1e-5)) - val
            else:
                val = p*100
                elo, ehi = val - lo*100, hi*100 - val

            ax.bar(xi, val, width=BAR_W, color=col_c, alpha=0.88,
                   edgecolor='white', zorder=2)
            ax.errorbar(xi, val, yerr=[[elo],[ehi]], fmt='none',
                        ecolor='#333333', elinewidth=1.0, capsize=3, zorder=3)

            # Condition label below bars
            lbl_y = (ylim_min - 4.5 if not use_lo else ylim_min - 0.38)
            ax.text(xi, lbl_y, lbl, ha='center', va='top',
                    fontsize=8.5, clip_on=False)

        # Delta bracket
        subL = df[df[col_key] == fspec['vL']]
        subR = df[df[col_key] == fspec['vR']]
        kL, nL = int(subL['correct'].sum()), len(subL)
        kR, nR = int(subR['correct'].sum()), len(subR)
        pL, pR = kL/nL, kR/nR
        loL, hiL = wilson_ci(kL, nL)
        loR, hiR = wilson_ci(kR, nR)
        if use_lo:
            vLv = logit(pL); vRv = logit(pR)
            eLhi = logit(min(hiL,1-1e-5)) - vLv
            eRhi = logit(min(hiR,1-1e-5)) - vRv
            bkt  = max(vLv + eLhi, vRv + eRhi) + 0.15
            dstr = f'{vLv - vRv:+.2f}'
        else:
            vLv = pL*100; vRv = pR*100
            eLhi = hiL*100 - vLv; eRhi = hiR*100 - vRv
            bkt  = max(vLv + eLhi, vRv + eRhi) + 4
            dstr = f'{vLv - vRv:+.1f} pp'

        ax.annotate('', xy=(xR, bkt), xytext=(xL, bkt),
                    arrowprops=dict(arrowstyle='<->', color='#555555', lw=1.0))
        delta = vLv - vRv
        ax.text((xL+xR)/2, bkt + (0.9 if not use_lo else 0.05),
                dstr, ha='center', va='bottom', fontsize=9, fontweight='bold',
                color='#1a6ab5' if delta > 0 else '#c0392b')

        # F-number and factor name BELOW condition labels (axes-fraction coords)
        xlim_l = -BAR_W*1.5
        xmax   = positions[-1][1] + BAR_W + 0.3
        xlim_r = xmax + 0.7
        cx_ax  = ((xL+xR)/2 - xlim_l) / (xlim_r - xlim_l)
        ax.text(cx_ax, -0.22, fspec['fnum'],
                ha='center', va='top', fontsize=9.5, fontweight='bold',
                color='#1a3a8b', transform=ax.transAxes, clip_on=False,
                bbox=dict(boxstyle='round,pad=0.2', facecolor='#ddeeff',
                          edgecolor='#1a3a8b', lw=0.9))
        ax.text(cx_ax, -0.32, fspec['name'],
                ha='center', va='top', fontsize=8, color='#333333',
                transform=ax.transAxes, clip_on=False)

    # Vertical separators between factors
    xmax = positions[-1][1] + BAR_W + 0.3
    for fi in range(len(factors) - 1):
        sep_x = (positions[fi][1] + positions[fi+1][0]) / 2
        ax.axvline(sep_x, color='#cccccc', lw=1.0, ls='--', zorder=0)

    if not use_lo:
        ax.axhline(CHANCE*100, color='#cc4444', lw=0.9, ls='--', zorder=1)
        ax.set_ylim(ylim_min, ylim_max)
        ax.set_yticks([0, 12.5, 25, 50, 75])
        ax.set_yticklabels(['0','12.5','25','50','75'], fontsize=8)
        ax.set_ylabel('% correct', fontsize=11)
        ax.set_title('% correct', fontsize=11, fontweight='bold', pad=6)
        ax.text(xmax + 0.1, CHANCE*100 + 0.5, 'chance\n(12.5%)',
                fontsize=6.5, color='#cc4444', va='bottom')
    else:
        ax.axhline(CHANCE_LO, color='#cc4444', lw=0.9, ls='--', zorder=1)
        ax.axhline(0.0,       color='#666666', lw=0.7, zorder=1)
        ax.set_ylim(ylim_min, ylim_max)
        ax.set_yticks([-2, CHANCE_LO, -1, 0, 1])
        ax.set_yticklabels(['-2.0','chance\n(\u22121.95)','\u22121.0','0.0\n(50%)','+1.0'],
                           fontsize=8)
        ax.set_ylabel('Log-odds', fontsize=11)
        ax.set_title('Log-odds', fontsize=11, fontweight='bold', pad=6)
        ax.text(xmax + 0.08, CHANCE_LO + 0.04, 'chance\n(\u22121.95)',
                fontsize=6.5, color='#cc4444', va='bottom')
        ax.text(xmax + 0.08, 0.04, '50%\n(0.00)',
                fontsize=6.5, color='#666666', va='bottom')

    ax.set_xlim(-BAR_W*1.5, xmax + 0.7)
    ax.set_xticks([])
    ax.spines[['top','right','bottom']].set_visible(False)
    ax.yaxis.grid(True, lw=0.4, color='#e8e8e8', zorder=0)
    ax.set_axisbelow(True)


def make_bar_page(df):
    fig = plt.figure(figsize=(11, 7))
    fig.patch.set_facecolor('white')

    fig.text(0.5, 0.96,
             'GLM predictors F1\u2013F4  \u2014  performance by factor level',
             ha='center', va='top', fontsize=13, fontweight='bold', color='#1a1a2e')
    fig.text(0.5, 0.915,
             f'{ASSET_LABEL}  \u00b7  n\u202f=\u202f2051  \u00b7  Wilson 95\u202f% CI  \u00b7  '
             '\u0394\u202f=\u202fleft minus right',
             ha='center', va='top', fontsize=8.5, color='#555555', style='italic')

    gs = gridspec.GridSpec(1, 2, figure=fig,
                           left=0.07, right=0.97, bottom=0.30, top=0.87,
                           wspace=0.12)
    ax_pct = fig.add_subplot(gs[0, 0])
    ax_lo  = fig.add_subplot(gs[0, 1])

    positions = get_positions()
    draw_bars(ax_pct, df, positions, use_lo=False)
    draw_bars(ax_lo,  df, positions, use_lo=True)

    fname_str = os.path.basename(OUT_PDF_SP)
    fig.text(0.10, 0.015, f'{fname_str}  \u00b7  {DATE_STR}  \u00b7  p.\u202f2/13',
             fontsize=7.5, color='#888888', va='top')
    return fig


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 3 — Estimated coefficients
# ══════════════════════════════════════════════════════════════════════════════
COEFF_LABELS = {
    'const': '\u03b20  intercept',
    'F1':    'F1  dot cueing',
    'F2':    'F2  depth cueing',
    'F3':    'F3  color cueing',
    'F4':    'F4  translator Far',
    'F1_F2': 'F1 \u00d7 F2',
    'F1_F4': 'F1 \u00d7 F4',
    'F2_F4': 'F2 \u00d7 F4',
}
# Display order (exclude intercept from main panel, show separately)
COEFF_ORDER = ['F1', 'F2', 'F3', 'F4', 'F1_F2', 'F1_F4', 'F2_F4']

# Color by role
COEFF_COLORS = {
    'F1': '#333333', 'F2': '#116688', 'F3': '#226622', 'F4': '#4477bb',
    'F1_F2': '#8833aa', 'F1_F4': '#aa5500', 'F2_F4': '#aa0066',
}

def compute_conditional_ame(model, df2, var, cond_var, cond_val, predictors, ix_cols=None):
    """AME of `var` restricted to trials where `cond_var` == `cond_val`."""
    if ix_cols is None: ix_cols = DD_IX
    sub = df2[df2[cond_var] == cond_val].copy()
    if len(sub) == 0: return float('nan')
    d1 = sub.copy(); d0 = sub.copy()
    d1[var] = 1; d0[var] = 0
    for col in ix_cols:
        parts = col.split('_')
        d1[col] = d1[parts[0]] * d1[parts[1]]
        d0[col] = d0[parts[0]] * d0[parts[1]]
    X1 = sm.add_constant(d1[predictors].astype(float), has_constant='add')
    X0 = sm.add_constant(d0[predictors].astype(float), has_constant='add')
    return (model.predict(X1) - model.predict(X0)).mean() * 100


def make_coeff_page(model, df2, predictors):
    fig = plt.figure(figsize=(11, 8))
    fig.patch.set_facecolor('white')

    fig.text(0.5, 0.965,
             'Estimated GLM coefficients',
             ha='center', va='top', fontsize=13, fontweight='bold', color='#1a1a2e')
    fig.text(0.5, 0.930,
             f'{ASSET_LABEL}  \u00b7  n\u202f=\u202f2051  \u00b7  '
             'logistic regression  \u00b7  maximum likelihood',
             ha='center', va='top', fontsize=8.5, color='#555555', style='italic')

    # Expanded plot area (freed space formerly used by conditional AME panel)
    gs = gridspec.GridSpec(1, 2, figure=fig,
                           left=0.26, right=0.97, bottom=0.14, top=0.87,
                           wspace=0.08)
    ax_lo  = fig.add_subplot(gs[0, 0])
    ax_ame = fig.add_subplot(gs[0, 1])

    n_rows = len(COEFF_ORDER)
    ys = list(range(n_rows - 1, -1, -1))
    ci = model.conf_int()

    # GridSpec spans figure y = 0.14 to 0.87 (range = 0.73)
    # Data ylim = (-0.7, n_rows - 0.3); row_y maps bar position → figure y
    def row_y(y_pos):
        return 0.14 + (y_pos + 0.7) / (n_rows + 0.4) * 0.73

    for i, key in enumerate(COEFF_ORDER):
        y_pos = ys[i]
        coef  = model.params[key]
        cilo  = ci.loc[key, 0]
        cihi  = ci.loc[key, 1]
        pval  = model.pvalues[key]
        stars = pstars(pval)
        col   = COEFF_COLORS.get(key, '#555555')
        is_ix = key in ('F1_F2', 'F1_F4', 'F2_F4')

        # Log-odds panel
        ax_lo.plot([cilo, cihi], [y_pos, y_pos], '-', color=col, lw=2.2, zorder=2)
        ax_lo.plot(coef, y_pos, 'D' if is_ix else 'o', color=col, ms=7, zorder=3)
        ax_lo.text(cihi + 0.06, y_pos,
                   f'{coef:+.2f} [{cilo:+.2f}, {cihi:+.2f}]  {stars}',
                   va='center', fontsize=7.5,
                   color='#111111', fontweight='bold' if stars not in ('n.s.','') else 'normal')

        # AME panel — main effects only; interaction rows point to p. 4
        if not is_ix:
            ame = compute_ame(model, df2, key, predictors)
            bar_col = col if ame >= 0 else '#c0392b'
            ax_ame.barh(y_pos, ame, height=0.45, color=bar_col, alpha=0.82,
                        edgecolor='white', zorder=2)
            ax_ame.text(ame + (0.5 if ame >= 0 else -0.5), y_pos,
                        f'{ame:+.1f} pp',
                        va='center', ha='left' if ame >= 0 else 'right',
                        fontsize=8.5, color='#111111')
        else:
            ax_ame.text(0, y_pos, 'see p.\u202f4',
                        va='center', ha='center', fontsize=7.5,
                        color='#888888', style='italic')

        # Row label aligned to bar position
        fig.text(0.250, row_y(y_pos), COEFF_LABELS.get(key, key),
                 ha='right', va='center', fontsize=9, color=col,
                 fontweight='bold' if is_ix else 'normal')

    # Axis formatting
    for ax, xlabel, title in [
            (ax_lo,  'Log-odds coefficient  (95\u202f% CI)', 'Log-odds'),
            (ax_ame, 'Average Marginal Effect  (pp)', 'AME  (pp)\u2014main effects only')]:
        ax.axvline(0, color='#666666', lw=0.8, zorder=1)
        ax.set_yticks(ys); ax.set_yticklabels([])
        ax.set_ylim(-0.7, n_rows - 0.3)
        ax.set_xlabel(xlabel, fontsize=9)
        ax.set_title(title, fontsize=10, fontweight='bold')
        ax.spines[['top','right']].set_visible(False)
        ax.xaxis.grid(True, lw=0.4, color='#e8e8e8', zorder=0)
        ax.set_axisbelow(True)

    # ── Significance key (compact, bottom-left) ───────────────────────────────
    ax_sig = fig.add_axes([0.26, 0.018, 0.22, 0.10])
    ax_sig.set_facecolor('#fafafa')
    for sp in ax_sig.spines.values():
        sp.set_edgecolor('#cccccc'); sp.set_linewidth(0.7)
    ax_sig.axis('off')
    ax_sig.set_title('Significance key', fontsize=8.5, fontweight='bold', pad=3)
    sig_rows = [
        ('***', 'p < .001'), (' **', 'p < .010'), ('  *', 'p < .050'),
        ('  \u2020', 'p < .100'), ('n.s.', 'p \u2265 .100'),
    ]
    for si, (sym, desc) in enumerate(sig_rows):
        yy = 0.82 - si * 0.175
        ax_sig.text(0.05, yy, sym, ha='left', va='center', fontsize=8.5,
                    fontweight='bold', fontfamily='monospace',
                    color='#1a1a2e', transform=ax_sig.transAxes)
        ax_sig.text(0.38, yy, desc, ha='left', va='center',
                    fontsize=8, color='#333333', transform=ax_sig.transAxes)

    # ── Intercept note ────────────────────────────────────────────────────────
    b0   = model.params['const']
    b0lo = ci.loc['const', 0]; b0hi = ci.loc['const', 1]
    b0p  = model.pvalues['const']
    p_at_zero = 1 / (1 + math.exp(-b0)) * 100
    fig.text(0.50, 0.080,
             f'\u03b20 (intercept) = {b0:+.3f}  [{b0lo:+.3f}, {b0hi:+.3f}]  p\u202f=\u202f{b0p:.4f}',
             ha='left', va='top', fontsize=8, color='#555555', style='italic')
    fig.text(0.50, 0.058,
             f'\u2248\u202f{p_at_zero:.1f}% predicted correct when all predictors\u202f=\u202f0'
             f'  (uncued, depth-uncued, color-uncued, Near translator)',
             ha='left', va='top', fontsize=8, color='#555555', style='italic')

    fname_str = os.path.basename(OUT_PDF_SP)
    fig.text(0.10, 0.008, f'{fname_str}  \u00b7  {DATE_STR}  \u00b7  p.\u202f3/13',
             fontsize=7.5, color='#888888', va='top')
    return fig


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 4 — Conditional AMEs: why F1 and F2 appear non-significant
# ══════════════════════════════════════════════════════════════════════════════

COND_AME_DATA = [
    # (predictor, conditioning var, conditioning val, label, color)
    ('F1', 'F2', 1, 'F1 (dot cueing)\nwhen depth-cued  (F2=1)',   '#333333'),
    ('F1', 'F2', 0, 'F1 (dot cueing)\nwhen depth-uncued  (F2=0)', '#999999'),
    ('F2', 'F1', 1, 'F2 (depth cueing)\nwhen dot-cued  (F1=1)',   '#116688'),
    ('F2', 'F1', 0, 'F2 (depth cueing)\nwhen dot-uncued  (F1=0)', '#88aabb'),
]

def make_cond_ame_page(model, df2, predictors):
    import textwrap as _tw
    fig = plt.figure(figsize=(11, 8))
    fig.patch.set_facecolor('white')

    fig.text(0.5, 0.965,
             'Conditional AMEs: why do F1 and F2 appear non-significant as main effects?',
             ha='center', va='top', fontsize=12, fontweight='bold', color='#1a1a2e')
    fig.text(0.5, 0.930,
             f'{ASSET_LABEL}  \u00b7  n\u202f=\u202f2051',
             ha='center', va='top', fontsize=8.5, color='#555555', style='italic')

    # ── Explanation box ───────────────────────────────────────────────────────
    ix_coef = model.params.get('F1_F2', float('nan'))
    ix_stars = pstars(model.pvalues.get('F1_F2', 1.0))
    expl = (
        'In an interaction model, \u03b21 and \u03b22 estimate conditional effects. '
        '\u03b21 is the effect of F1 (dot cueing) specifically when F2\u202f=\u202f0 '
        '(depth-uncued trials); \u03b22 is the effect of F2 specifically when F1\u202f=\u202f0 '
        '(dot-uncued trials). '
        'Because the temporal onset cue provides little benefit without depth-plane continuity, '
        'and depth-plane continuity provides little benefit without the onset cue, '
        'both of these conditional effects are small and may not reach significance individually. '
        'The full F1\u202f\u00d7\u202fF2 interaction (\u03b212\u202f=\u202f'
        f'{ix_coef:+.3f}, {ix_stars}) captures the extra benefit when both factors are present together. '
        'The chart below shows the AME of F1 and F2 computed separately for each level of the '
        'complementary factor. The difference between the two F1 bars (or the two F2 bars) equals '
        'the interaction coefficient.'
    )

    ax_expl = fig.add_axes([0.07, 0.705, 0.86, 0.200])
    ax_expl.set_facecolor('#f0f4ff')
    for sp in ax_expl.spines.values():
        sp.set_edgecolor('#aabbdd'); sp.set_linewidth(0.8)
    ax_expl.set_xticks([]); ax_expl.set_yticks([])
    y_line = 0.92
    for line in _tw.wrap(expl, width=125):
        ax_expl.text(0.016, y_line, line, ha='left', va='top', fontsize=9.5,
                     color='#1a3a8b', transform=ax_expl.transAxes, linespacing=1.3)
        y_line -= 0.148

    # ── Conditional AME chart ─────────────────────────────────────────────────
    # Chart positioned with generous left margin for tick labels
    ax = fig.add_axes([0.46, 0.10, 0.48, 0.55])
    ax.set_facecolor('#fafafa')
    for sp in ax.spines.values():
        sp.set_edgecolor('#cccccc'); sp.set_linewidth(0.7)
    ax.set_title('Conditional AMEs  (percentage points)',
                 fontsize=11, fontweight='bold', pad=10)

    bar_ys = [3, 2, 1, 0]   # top to bottom: F1|F2=1, F1|F2=0, F2|F1=1, F2|F1=0
    cond_vals = []
    for var, cvar, cval, lbl, col in COND_AME_DATA:
        ame = compute_conditional_ame(model, df2, var, cvar, cval, predictors)
        cond_vals.append(ame)

    for (var, cvar, cval, lbl, col), cy, ame in zip(COND_AME_DATA, bar_ys, cond_vals):
        ax.barh(cy, ame, height=0.6, color=col, alpha=0.85,
                edgecolor='white', zorder=2)
        xoff = 1.2 if ame >= 0 else -1.2
        ax.text(ame + xoff, cy, f'{ame:+.1f}\u202fpp',
                va='center', ha='left' if ame >= 0 else 'right',
                fontsize=11, fontweight='bold', color='#111111')

    # Separator line between F1 and F2 groups
    ax.axhline(1.5, color='#cccccc', lw=1.2, ls='--', zorder=1)

    ax.axvline(0, color='#444444', lw=1.0, zorder=1)
    ax.set_xlim(-8, 62)
    ax.set_ylim(-0.55, 3.55)
    ax.set_yticks([0, 1, 2, 3])
    ax.set_yticklabels([
        'F2 (depth cueing)\nwhen dot-uncued  (F1=0)',
        'F2 (depth cueing)\nwhen dot-cued  (F1=1)',
        'F1 (dot cueing)\nwhen depth-uncued  (F2=0)',
        'F1 (dot cueing)\nwhen depth-cued  (F2=1)',
    ], fontsize=10)
    # Color tick labels to match bars
    tick_colors = ['#88aabb', '#116688', '#999999', '#333333']
    for tick, col in zip(ax.get_yticklabels(), tick_colors):
        tick.set_color(col)
    ax.tick_params(axis='y', length=0, pad=8)
    ax.set_xlabel('Average Marginal Effect (pp)', fontsize=10)
    ax.xaxis.grid(True, lw=0.5, color='#e8e8e8', zorder=0)
    ax.set_axisbelow(True)
    ax.spines[['top', 'right']].set_visible(False)

    # ── Annotation: interaction coefficient ───────────────────────────────────
    fig.text(0.07, 0.595,
             f'The F1\u00d7F2 interaction coefficient is {ix_coef:+.3f}\u202f{ix_stars}',
             ha='left', va='top', fontsize=10.5, fontweight='bold', color='#8833aa')
    interp = (
        'The difference between the top two bars (F1 when F2=1 vs. F2=0) '
        'equals this coefficient directly. '
        'Same for the bottom two bars (F2 when F1=1 vs. F1=0). '
        'Note the asymmetry: F1 when F2=0 is positive (onset cue retains '
        'partial benefit even without depth continuity); '
        'F2 when F1=0 is near zero (depth continuity alone does nothing).'
    )
    y_ann = 0.550
    for line in _tw.wrap(interp, width=42):
        fig.text(0.07, y_ann, line, ha='left', va='top', fontsize=9.5,
                 color='#333333', style='italic')
        y_ann -= 0.038

    fname_str = os.path.basename(OUT_PDF_SP)
    fig.text(0.10, 0.025, f'{fname_str}  \u00b7  {DATE_STR}  \u00b7  p.\u202f4/13',
             fontsize=7.5, color='#888888', va='top')
    return fig


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 4 — Fitted equation with coefficients + interpretation
# ══════════════════════════════════════════════════════════════════════════════

def sigmoid(x):
    return 1 / (1 + math.exp(-x))

def pred_pct(params, F1, F2, F3, F4):
    lo = (params['const']
          + params['F1']*F1 + params['F2']*F2
          + params['F3']*F3 + params['F4']*F4
          + params['F1_F2']*F1*F2
          + params['F1_F4']*F1*F4
          + params['F2_F4']*F2*F4)
    return sigmoid(lo)*100, lo

KEY_CONDITIONS = [
    # label,                                     F1 F2 F3 F4(1=Far)
    ('Uncued · depth-uncued · Near',              0, 0, 0, 0),
    ('Uncued · depth-uncued · Far',               0, 0, 0, 1),
    ('Cued · depth-uncued · Near',                1, 0, 0, 0),
    ('Cued · depth-uncued · Far',                 1, 0, 0, 1),
    ('Cued · depth-cued · Near',                  1, 1, 0, 0),
    ('Cued · depth-cued · Far  \u2605 optimal',   1, 1, 0, 1),
]

INTERP_PARAS = [
    (
        "The fitted equation makes the conjunctive structure of the result explicit. "
        "When the temporal onset cue is present but the translating field\u2019s depth-plane "
        "identity has been disrupted (F1\u202f=\u202f1, F2\u202f=\u202f0), the model predicts "
        "modest performance only marginally above the uncued baseline. "
        "When both the temporal cue and depth-plane continuity are intact "
        "(F1\u202f=\u202f1, F2\u202f=\u202f1), predicted performance is approximately double "
        "that level. The F1\u202f\u00d7\u202fF2 coefficient is large and positive, capturing "
        "a synergistic effect: depth-plane continuity multiplies the gain from the onset cue "
        "rather than adding a fixed increment. "
        "Crucially, the two factors are not symmetric in their individual contributions. "
        "When depth continuity is disrupted but the onset cue is present "
        "(F1\u202f=\u202f1, F2\u202f=\u202f0), the model predicts approximately "
        "+10\u202fpp above the uncued baseline\u2014a partial but real selection benefit. "
        "When the onset cue is absent but depth continuity is intact "
        "(F1\u202f=\u202f0, F2\u202f=\u202f1), the model predicts near chance. "
        "The onset cue is weakly sufficient on its own; "
        "depth-plane continuity is only effective in its presence."
    ),
    (
        "The null result for color (F3\u202f\u2248\u202f0) resolves an ambiguity in earlier "
        "experiments using linked depth and color, where Near was always Red and Far always "
        "Green. In those sessions an apparent color-cueing effect was observed, but the "
        "present design\u2014in which color and depth swap independently\u2014shows that "
        "effect to be entirely a depth confound. Color-field identity does not bind to the "
        "temporal onset cue."
    ),
    (
        "The predicted performance when F1\u202f=\u202f1 and F2\u202f=\u202f0 (temporal cue "
        "present, depth disrupted) provides a natural point of contact with earlier "
        "two-dimensional transparent-surface experiments. In those studies, overlapping "
        "random-dot fields sharing a single depth plane were used; no stereoscopic depth "
        "information was available, and the temporal onset cue operated without any "
        "depth-plane binding. The performance level we observe here under depth disruption "
        "is consistent with that two-dimensional baseline, suggesting that the temporal "
        "onset mechanism is preserved in VR and that the improvement seen with depth "
        "continuity reflects an additional contribution of stereoscopic object identity "
        "rather than a change in the basic cueing mechanism. Depth-plane membership "
        "appears to function as a constitutive feature of the attentional object "
        "representation: its disruption at the moment of translation partially disassembles "
        "the representation that the temporal cue had established."
    ),
    (
        "F4 (translator depth plane; 1\u202f=\u202fFar, 0\u202f=\u202fNear) shows a robust "
        "Far\u202f>\u202fNear advantage of approximately\u202f+15\u202fpp "
        "(p\u202f<\u202f.001). Whether this reflects a Far-plane advantage or a Near-plane "
        "penalty cannot be determined from Near/Far comparisons alone: a flat baseline "
        "(zero disparity) would be needed to locate the asymmetry. "
        "The monocular control sessions are the closest available reference: the "
        "Far\u202f>\u202fNear gap is absent monocularly, suggesting binocular disparity "
        "selectively benefits the Far condition. "
        "The asymmetry also grows with stereoscopic separation rather than shrinking, "
        "which argues against a simple near-plane leakage account (more discriminable "
        "planes should reduce interference, not increase it). "
        "F1\u202f\u00d7\u202fF4 and F2\u202f\u00d7\u202fF4 interactions are shown on "
        "p.\u202f7. Mechanism unresolved."
    ),
]

def make_interpretation_page(model, df2, predictors):
    import textwrap as _tw
    params = model.params
    p  = params

    fig = plt.figure(figsize=(11, 8.5))
    fig.patch.set_facecolor('white')

    fig.text(0.5, 0.968,
             'Fitted equation and interpretation',
             ha='center', va='top', fontsize=13, fontweight='bold', color='#1a1a2e')
    fig.text(0.5, 0.933,
             f'{ASSET_LABEL}  \u00b7  n\u202f=\u202f2051',
             ha='center', va='top', fontsize=8.5, color='#555555', style='italic')

    # ── Fitted equation box ───────────────────────────────────────────────────
    eq_line1 = (f'log-odds(correct)  =  {p["const"]:+.3f}'
                f'  +  {p["F1"]:+.3f}\u00b7F1'
                f'  +  {p["F2"]:+.3f}\u00b7F2'
                f'  +  {p["F3"]:+.3f}\u00b7F3'
                f'  +  {p["F4"]:+.3f}\u00b7F4')
    eq_line2 = (f'    +  {p["F1_F2"]:+.3f}\u00b7(F1\u00d7F2)'
                f'  +  {p["F1_F4"]:+.3f}\u00b7(F1\u00d7F4)'
                f'  +  {p["F2_F4"]:+.3f}\u00b7(F2\u00d7F4)')

    ax_eq = fig.add_axes([0.06, 0.855, 0.88, 0.065])
    ax_eq.set_facecolor('#f0f4ff')
    for sp in ax_eq.spines.values():
        sp.set_edgecolor('#1a3a8b'); sp.set_linewidth(0.8)
    ax_eq.set_xticks([]); ax_eq.set_yticks([])
    ax_eq.text(0.5, 0.75, eq_line1, ha='center', va='center',
               fontsize=9.5, fontfamily='monospace', color='#1a3a8b',
               transform=ax_eq.transAxes)
    ax_eq.text(0.5, 0.20, eq_line2, ha='center', va='center',
               fontsize=9.5, fontfamily='monospace', color='#1a3a8b',
               transform=ax_eq.transAxes)

    # ── Prediction table ──────────────────────────────────────────────────────
    # Taller axes + wider column spacing to prevent overlap
    ax_tbl = fig.add_axes([0.06, 0.22, 0.42, 0.60])
    ax_tbl.axis('off')
    ax_tbl.set_title('Predicted % correct for key conditions  (F3\u202f=\u202f0 throughout)',
                     fontsize=9, fontweight='bold', pad=8, loc='left')

    # Column positions spread across full axes width
    col_headers = ['Condition', 'F1', 'F2', 'F4', 'Log-odds', '% correct']
    col_xs      = [0.0,  0.55, 0.63, 0.71, 0.81, 0.93]
    col_ha      = ['left', 'center', 'center', 'center', 'right', 'right']

    # Header row — leave top 8% for title padding
    HDR_Y = 0.91
    for cx, hdr, ha in zip(col_xs, col_headers, col_ha):
        ax_tbl.text(cx, HDR_Y, hdr, ha=ha, va='top', fontsize=8.5,
                    fontweight='bold', color='#1a1a2e',
                    transform=ax_tbl.transAxes)
    ax_tbl.plot([0, 1], [HDR_Y - 0.04, HDR_Y - 0.04], color='#333333', lw=0.8,
                transform=ax_tbl.transAxes, clip_on=False)

    n_rows = len(KEY_CONDITIONS)
    row_h  = (HDR_Y - 0.08) / n_rows     # even row height leaving bottom margin
    row_colors = ['#f0f4ff', '#ffffff', '#ffffff', '#ddeedd', '#f5e8e8', '#ffffff']

    for ri, (lbl, F1, F2, F3, F4) in enumerate(KEY_CONDITIONS):
        pct, lo = pred_pct(params, F1, F2, F3, F4)
        ry = HDR_Y - 0.06 - ri * row_h   # top of this row
        # Row background
        ax_tbl.add_patch(plt.Rectangle(
            (0, ry - row_h + 0.005), 1.0, row_h - 0.005,
            facecolor=row_colors[ri], transform=ax_tbl.transAxes,
            zorder=0, clip_on=False))
        vals  = [lbl, str(F1), str(F2), str(F4), f'{lo:+.2f}', f'{pct:.1f}%']
        bold  = (ri == 5)  # optimal condition = last row
        for cx, v, ha in zip(col_xs, vals, col_ha):
            ax_tbl.text(cx, ry - 0.005, v, ha=ha, va='top', fontsize=8.5,
                        fontweight='bold' if bold else 'normal',
                        color='#1a3a8b' if bold else '#111111',
                        transform=ax_tbl.transAxes)

    ax_tbl.plot([0, 1], [0.02, 0.02], color='#cccccc', lw=0.6,
                transform=ax_tbl.transAxes, clip_on=False)

    # ── Interpretation prose ──────────────────────────────────────────────────
    y = 0.815; lh = 0.017; gap = 0.016; W = 62
    for para in INTERP_PARAS:
        for line in _tw.wrap(para, width=W):
            fig.text(0.52, y, line, ha='left', va='top',
                     fontsize=9, color='#111111', fontfamily='serif')
            y -= lh
        y -= gap

    fname_str = os.path.basename(OUT_PDF_SP)
    fig.text(0.10, 0.018, f'{fname_str}  \u00b7  {DATE_STR}  \u00b7  p.\u202f5/13',
             fontsize=7.5, color='#888888', va='top')
    return fig


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 6 — Predicted vs Observed
# ══════════════════════════════════════════════════════════════════════════════

# Condition display order: CUED first (blue), then UNCUED (grey-blue)
PRED_OBS_ORDER = [
    ('CUED',   'N',  '#2255aa', 'o',  'CUED+N'),
    ('CUED',   'C',  '#2255aa', 's',  'CUED+C'),
    ('CUED',   'Z',  '#c0392b', 'o',  'CUED+Z'),
    ('CUED',   'CZ', '#c0392b', 's',  'CUED+CZ'),
    ('UNCUED', 'N',  '#7799cc', '^',  'UNCUED+N'),
    ('UNCUED', 'C',  '#7799cc', 'D',  'UNCUED+C'),
    ('UNCUED', 'Z',  '#e08080', '^',  'UNCUED+Z'),
    ('UNCUED', 'CZ', '#e08080', 'D',  'UNCUED+CZ'),
]

# Recover (cond, swap) from (F1, F2, F3)
_SWAP_CUED   = {(1,1):'N', (1,0):'C', (0,1):'Z', (0,0):'CZ'}
_SWAP_UNCUED = {(0,0):'N', (0,1):'C', (1,0):'Z', (1,1):'CZ'}

def _get_cond_swap(row):
    k = (int(row['F2']), int(row['F3']))
    cond = 'CUED' if row['F1'] == 1 else 'UNCUED'
    swap = _SWAP_CUED[k] if row['F1'] == 1 else _SWAP_UNCUED[k]
    return cond, swap

def make_pred_obs_page(model, df2, predictors):
    import textwrap as _tw
    from matplotlib.patches import Patch

    dfw = df2.copy()
    dfw['_pred'] = model.predict()
    cond_swap = dfw.apply(_get_cond_swap, axis=1)
    dfw['_cond'] = [cs[0] for cs in cond_swap]
    dfw['_swap'] = [cs[1] for cs in cond_swap]

    grp  = dfw.groupby(['_cond', '_swap'])
    obs  = grp['correct'].mean() * 100
    pred = grp['_pred'].mean()   * 100
    n    = grp['correct'].count()

    def wci(pct, n_):
        k = round(pct * n_ / 100)
        if n_ == 0: return 0, 0
        p = k / n_; z = 1.96; d = 1 + z**2/n_
        c = (p + z**2/(2*n_)) / d
        hw = z * math.sqrt(p*(1-p)/n_ + z**2/(4*n_**2)) / d
        return (p - (c - hw))*100, ((c+hw) - p)*100

    fig = plt.figure(figsize=(11, 8))
    fig.patch.set_facecolor('white')
    fig.text(0.5, 0.968,
             'Model fit: predicted vs. observed accuracy',
             ha='center', va='top', fontsize=13, fontweight='bold', color='#1a1a2e')
    fig.text(0.5, 0.933,
             f'{ASSET_LABEL}  \u00b7  n\u202f=\u202f2051  \u00b7  8 conditions (swap\u202f\u00d7\u202fcueing)',
             ha='center', va='top', fontsize=8.5, color='#555555', style='italic')

    gs = gridspec.GridSpec(1, 2, figure=fig,
                           left=0.07, right=0.97, bottom=0.18, top=0.88,
                           wspace=0.35)
    ax_sc  = fig.add_subplot(gs[0, 0])
    ax_bar = fig.add_subplot(gs[0, 1])

    # ── Left: scatter observed vs predicted ──────────────────────────────────
    for cond, swap, col, mk, lbl in PRED_OBS_ORDER:
        key = (cond, swap)
        if key not in obs.index: continue
        o = obs[key]; p_ = pred[key]; n_ = n[key]
        elo, ehi = wci(o, n_)
        ax_sc.errorbar(o, p_, xerr=[[elo],[ehi]],
                       fmt=mk, color=col, ms=8, mec='white', mew=0.6,
                       ecolor=col, elinewidth=1, capsize=3, zorder=3)
        ax_sc.annotate(f'{cond[0]}+{swap}', (o, p_),
                       textcoords='offset points', xytext=(5, 3),
                       fontsize=7.5, color=col)

    lo, hi = 10, 70
    ax_sc.plot([lo, hi], [lo, hi], '--', color='#888888', lw=0.9, zorder=1,
               label='Perfect fit (y\u202f=\u202fx)')
    ax_sc.set_xlim(lo, hi); ax_sc.set_ylim(lo, hi)
    ax_sc.set_xlabel('Observed % correct', fontsize=10)
    ax_sc.set_ylabel('Predicted % correct', fontsize=10)
    ax_sc.set_title('Scatter: predicted vs. observed', fontsize=10, fontweight='bold')
    ax_sc.spines[['top','right']].set_visible(False)
    ax_sc.xaxis.grid(True, lw=0.4, color='#e0e0e0', zorder=0)
    ax_sc.yaxis.grid(True, lw=0.4, color='#e0e0e0', zorder=0)
    ax_sc.set_axisbelow(True)
    ax_sc.legend(fontsize=8, loc='upper left', framealpha=0.9)

    # ── Right: side-by-side bars ──────────────────────────────────────────────
    xs = np.arange(len(PRED_OBS_ORDER))
    bw = 0.35
    for i, (cond, swap, col, mk, lbl) in enumerate(PRED_OBS_ORDER):
        key = (cond, swap)
        if key not in obs.index: continue
        o = obs[key]; p_ = pred[key]; n_ = n[key]
        elo, ehi = wci(o, n_)
        ax_bar.bar(xs[i] - bw/2, o,  width=bw, color=col, alpha=0.85, zorder=2)
        ax_bar.bar(xs[i] + bw/2, p_, width=bw, color=col, alpha=0.35,
                   hatch='///', zorder=2)
        ax_bar.errorbar(xs[i] - bw/2, o, yerr=[[elo],[ehi]],
                        fmt='none', ecolor='#333', elinewidth=0.9,
                        capsize=2.5, zorder=3)

    ax_bar.axhline(100/8, color='#cc4444', lw=1.0, ls='--', zorder=1,
                   label='Chance (12.5%)')
    ax_bar.set_xticks(xs)
    ax_bar.set_xticklabels([lbl for *_, lbl in PRED_OBS_ORDER],
                           rotation=40, ha='right', fontsize=8)
    ax_bar.set_ylim(0, 80)
    ax_bar.set_yticks([0, 12.5, 25, 50, 75])
    ax_bar.set_yticklabels(['0', '12.5', '25', '50', '75'], fontsize=8)
    ax_bar.set_ylabel('% correct', fontsize=10)
    ax_bar.set_title('Observed (solid) vs. predicted (hatched)', fontsize=10, fontweight='bold')
    ax_bar.spines[['top','right']].set_visible(False)
    ax_bar.yaxis.grid(True, lw=0.4, color='#e0e0e0', zorder=0)
    ax_bar.set_axisbelow(True)

    # Shared legend
    leg_handles = [
        Patch(facecolor='#555555', alpha=0.85, label='Observed'),
        Patch(facecolor='#555555', alpha=0.35, hatch='///', label='Predicted (model)'),
        Patch(facecolor='#2255aa', label='CUED, depth-cued (N/C)'),
        Patch(facecolor='#c0392b', label='CUED, depth-uncued (Z/CZ)'),
        Patch(facecolor='#7799cc', label='UNCUED, depth-cued (N/C)'),
        Patch(facecolor='#e08080', label='UNCUED, depth-uncued (Z/CZ)'),
    ]
    fig.legend(handles=leg_handles, loc='lower center', ncol=3,
               fontsize=8, bbox_to_anchor=(0.5, 0.00), framealpha=0.9)

    fname_str = os.path.basename(OUT_PDF_SP)
    fig.text(0.10, 0.008, f'{fname_str}  \u00b7  {DATE_STR}  \u00b7  p.\u202f6/13',
             fontsize=7.5, color='#888888', va='top')
    return fig


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 7 — F4: Far > Near asymmetry and its interactions
# ══════════════════════════════════════════════════════════════════════════════

def make_f4_page(model, df2, predictors):
    import textwrap as _tw
    from matplotlib.patches import Patch

    dfw = df2.copy()
    dfw['_pred'] = model.predict()

    # ── Left panel: Near vs Far × CUED/UNCUED ─────────────────────────────────
    # 4 groups: (F1, F4);  F4=1=Far, F4=0=Near
    GROUP_ORDER = [
        (1, 1, '#2255aa', 'CUED · Far'),
        (1, 0, '#88aadd', 'CUED · Near'),
        (0, 1, '#666666', 'UNCUED · Far'),
        (0, 0, '#aaaaaa', 'UNCUED · Near'),
    ]
    grp  = dfw.groupby(['F1', 'F4'])
    obs  = grp['correct'].mean() * 100
    pred = grp['_pred'].mean()   * 100
    n_   = grp['correct'].count()

    def wci(pct, nn):
        k = round(pct * nn / 100)
        if nn == 0: return 0, 0
        p = k / nn; z = 1.96; d = 1 + z**2/nn
        c = (p + z**2/(2*nn)) / d
        hw = z * math.sqrt(p*(1-p)/nn + z**2/(4*nn**2)) / d
        return (p-(c-hw))*100, ((c+hw)-p)*100

    fig = plt.figure(figsize=(11, 8))
    fig.patch.set_facecolor('white')
    fig.text(0.5, 0.968,
             'F4 — Far > Near asymmetry: performance, interactions, and open questions',
             ha='center', va='top', fontsize=12, fontweight='bold', color='#1a1a2e')
    fig.text(0.5, 0.933,
             f'{ASSET_LABEL}  \u00b7  n\u202f=\u202f2051',
             ha='center', va='top', fontsize=8.5, color='#555555', style='italic')

    gs = gridspec.GridSpec(1, 2, figure=fig,
                           left=0.07, right=0.97, bottom=0.18, top=0.87,
                           wspace=0.38)
    ax_bar = fig.add_subplot(gs[0, 0])
    ax_cond = fig.add_subplot(gs[0, 1])

    xs = np.arange(len(GROUP_ORDER))
    bw = 0.35
    for i, (f1, f4, col, lbl) in enumerate(GROUP_ORDER):
        key = (f1, f4)
        if key not in obs.index: continue
        o  = obs[key]; p_ = pred[key]; nn = n_[key]
        elo, ehi = wci(o, nn)
        ax_bar.bar(xs[i] - bw/2, o,  width=bw, color=col, alpha=0.90, zorder=2)
        ax_bar.bar(xs[i] + bw/2, p_, width=bw, color=col, alpha=0.35,
                   hatch='///', zorder=2)
        ax_bar.errorbar(xs[i] - bw/2, o, yerr=[[elo],[ehi]],
                        fmt='none', ecolor='#333', elinewidth=0.9,
                        capsize=2.5, zorder=3)
        # Delta annotation: Far − Near (F4=1 is Far, so compare to F4=0=Near)
        if f4 == 1:
            near_key = (f1, 0)
            if near_key in obs.index:
                delta = o - obs[near_key]
                ax_bar.annotate(f'\u0394={delta:+.1f}pp',
                                xy=(xs[i], max(o, obs[near_key]) + 2),
                                ha='center', fontsize=7.5, color='#2255aa',
                                fontweight='bold')

    ax_bar.axhline(100/8, color='#cc4444', lw=0.9, ls='--', zorder=1,
                   label='Chance (12.5%)')
    ax_bar.set_xticks(xs)
    ax_bar.set_xticklabels([lbl for *_, lbl in GROUP_ORDER],
                           rotation=20, ha='right', fontsize=9)
    ax_bar.set_ylim(0, 80)
    ax_bar.set_yticks([0, 12.5, 25, 50, 75])
    ax_bar.set_yticklabels(['0', '12.5', '25', '50', '75'], fontsize=8)
    ax_bar.set_ylabel('% correct', fontsize=10)
    ax_bar.set_title('Near vs. Far: observed (solid) vs. predicted (hatched)',
                     fontsize=9.5, fontweight='bold')
    ax_bar.spines[['top','right']].set_visible(False)
    ax_bar.yaxis.grid(True, lw=0.4, color='#e0e0e0', zorder=0)
    ax_bar.set_axisbelow(True)
    leg_h = [Patch(facecolor='#555', alpha=0.9, label='Observed'),
             Patch(facecolor='#555', alpha=0.35, hatch='///', label='Predicted')]
    ax_bar.legend(handles=leg_h, fontsize=8, loc='upper right', framealpha=0.9)

    # ── Right panel: F4 main AME + F1×F4 and F2×F4 conditional AMEs ──────────
    # Rows (top to bottom):
    #   F4 main AME (overall Far advantage; F4=1=Far → positive coefficient)
    #   F1 effect | Far (F4=1)
    #   F1 effect | Near (F4=0)
    #   F2 effect | Far (F4=1)
    #   F2 effect | Near (F4=0)
    cond_rows = [
        ('F4_main',  None, None, None, 'F4 overall Far advantage',          '#4477bb'),
        ('F1',       'F4', 1,    None, 'F1 (dot cueing) when Far  (F4=1)', '#333333'),
        ('F1',       'F4', 0,    None, 'F1 (dot cueing) when Near (F4=0)', '#999999'),
        ('F2',       'F4', 1,    None, 'F2 (depth cueing) when Far  (F4=1)', '#116688'),
        ('F2',       'F4', 0,    None, 'F2 (depth cueing) when Near (F4=0)', '#88aabb'),
    ]
    row_ys  = [4, 3, 2, 1, 0]
    row_vals = []
    for var, cvar, cval, _, lbl, col in [(*r,) for r in cond_rows]:
        # unpack 5-tuple: var, cvar, cval, lbl, col
        pass
    # recompute cleanly
    ames = []
    for row in cond_rows:
        var, cvar, cval, _, lbl, col = row
        if var == 'F4_main':
            ames.append(compute_ame(model, df2, 'F4', predictors))
        else:
            ames.append(compute_conditional_ame(model, df2, var, cvar, cval, predictors))

    row_colors_cond = ['#4477bb', '#333333', '#999999', '#116688', '#88aabb']
    row_labels = [r[4] for r in cond_rows]

    ax_cond.set_facecolor('#fafafa')
    for sp in ax_cond.spines.values():
        sp.set_edgecolor('#cccccc'); sp.set_linewidth(0.7)

    for cy, ame, lbl, col in zip(row_ys, ames, row_labels, row_colors_cond):
        ax_cond.barh(cy, ame, height=0.55, color=col, alpha=0.85,
                     edgecolor='white', zorder=2)
        xoff = 1.0 if ame >= 0 else -1.0
        ax_cond.text(ame + xoff, cy, f'{ame:+.1f}\u202fpp',
                     va='center', ha='left' if ame >= 0 else 'right',
                     fontsize=10, fontweight='bold', color='#111111')

    # Separator between F4 main and the conditional rows
    ax_cond.axhline(3.5, color='#cccccc', lw=1.0, ls='--', zorder=1)

    ax_cond.axvline(0, color='#444444', lw=1.0, zorder=1)
    ax_cond.set_xlim(-8, 55)
    ax_cond.set_ylim(-0.55, 4.55)
    ax_cond.set_yticks(row_ys)
    ax_cond.set_yticklabels(row_labels, fontsize=9)
    for tick, col in zip(ax_cond.get_yticklabels(), row_colors_cond):
        tick.set_color(col)
    ax_cond.tick_params(axis='y', length=0, pad=6)
    ax_cond.set_xlabel('Average Marginal Effect (pp)', fontsize=10)
    ax_cond.set_title('F4 main AME and interaction with F1, F2',
                      fontsize=9.5, fontweight='bold')
    ax_cond.xaxis.grid(True, lw=0.5, color='#e8e8e8', zorder=0)
    ax_cond.set_axisbelow(True)
    ax_cond.spines[['top','right']].set_visible(False)

    # ── Footer note ───────────────────────────────────────────────────────────
    note_lines = [
        'Far\u202f>\u202fNear gap is absent under monocular viewing and grows with '
        'stereoscopic separation (0.03\u2013\u202f0.15\u202fm parametric sessions).',
        'The direction of the effect (Far advantage vs. Near penalty) cannot be resolved '
        'without a zero-disparity baseline.',
        'Leakage account predicts the gap should shrink as planes become more discriminable; '
        'it grows instead. SOA manipulation is the planned critical test.',
    ]
    note_y = 0.140
    for nl in note_lines:
        fig.text(0.07, note_y, nl, ha='left', va='top',
                 fontsize=8.5, color='#555555', style='italic')
        note_y -= 0.028

    fname_str = os.path.basename(OUT_PDF_SP)
    fig.text(0.10, 0.025, f'{fname_str}  \u00b7  {DATE_STR}  \u00b7  p.\u202f7/13',
             fontsize=7.5, color='#888888', va='top')
    return fig


# ══════════════════════════════════════════════════════════════════════════════
# EXPERIMENT 2 — DepthColorLinked
# ══════════════════════════════════════════════════════════════════════════════

DCL_SESSIONS_PATHS = [
    '/tmp/quest_pull2/files/vr_dots_session_260404_0940.tsv',
    '/tmp/quest_pull2/files/vr_dots_session_260404_1123.tsv',
    '/tmp/quest_pull2/files/vr_dots_session_260406_1001.tsv',
    '/tmp/quest_pull2/files/vr_dots_session_260406_1034.tsv',
]
DCL_SESSION_LABELS = ('260404_0940 (S1)  ·  260404_1123 (S2)  ·  '
                      '260406_1001 (S3)  ·  260406_1034 (S4)')
DCL_ASSET_LABEL    = 'Exp_DepthColorLinked_005m  (Near=Red, Far=Green; linkDepthColor=1)'

DCL_FACTORS = [
    dict(fnum='F1', col='F1',
         vL=1, lblL='Cued',      cL='#333333',
         vR=0, lblR='Uncued',    cR='#bbbbbb',
         name='Dot Cueing'),
    dict(fnum='F2', col='F2',
         vL=1, lblL='ZdNoi\n(stable)',  cL='#116688',
         vR=0, lblR='ZdCoh\n(swap)',    cR='#cc7733',
         name='Object Depth\nContinuity'),
    dict(fnum='F3', col='F3',
         vL=1, lblL='Far',  cL='#4477bb',
         vR=0, lblR='Near', cR='#993333',
         name='Translator\nDepth Plane'),
]

DCL_COEFF_LABELS = {
    'const': '\u03b20  intercept',
    'F1':    'F1  dot cueing',
    'F2':    'F2  object continuity',
    'F3':    'F3  translator Far',
    'F1_F2': 'F1 \u00d7 F2',
    'F1_F3': 'F1 \u00d7 F3',
    'F2_F3': 'F2 \u00d7 F3',
}
DCL_COEFF_ORDER  = ['F1', 'F2', 'F3', 'F1_F2', 'F1_F3', 'F2_F3']
DCL_COEFF_COLORS = {
    'F1': '#333333', 'F2': '#116688', 'F3': '#4477bb',
    'F1_F2': '#8833aa', 'F1_F3': '#aa5500', 'F2_F3': '#aa0066',
}

DCL_MODEL_EQ = ('log-odds(correct)  =  \u03b20'
                '  +  \u03b21\u00b7F1  +  \u03b22\u00b7F2  +  \u03b23\u00b7F3\n'
                '    +  \u03b212\u00b7(F1\u00d7F2)  +  \u03b213\u00b7(F1\u00d7F3)'
                '  +  \u03b223\u00b7(F2\u00d7F3)')


# ── DCL data loading ───────────────────────────────────────────────────────────
def load_dcl():
    trials = []
    for path in DCL_SESSIONS_PATHS:
        if not os.path.exists(path):
            print(f'DCL: missing {path}'); continue
        with open(path, newline='') as f:
            for r in csv.DictReader(f, delimiter='\t'):
                if (not r.get('TransDeg', '').strip() or
                        not r.get('RespDeg', '').strip() or
                        r.get('EndKey', '') in ('timeout', 'skip', 'requeue')):
                    continue
                cond = r['Cond']
                swap = r['SwapType']   # ZdA or ZdB
                F1 = 1 if cond == 'CUED' else 0
                # F2: translator depth+color continuity intact?
                # CUED+ZdB = translator stays (stable) = ZdNoi → F2=1
                # CUED+ZdA = translator changes          = ZdCoh → F2=0
                coh_stable = ((cond == 'CUED'   and swap == 'ZdB') or
                              (cond == 'UNCUED' and swap == 'ZdA'))
                F2 = 1 if coh_stable else 0
                # F3: translator depth plane — Far=1, Near=0 (consistent with DD F4)
                b_near    = (r['DelayedFieldDepth'] == 'N')
                trans_near = b_near if cond == 'CUED' else not b_near
                F3 = 0 if trans_near else 1
                trials.append(dict(
                    correct=int(is_correct(r['TransDeg'], r['RespDeg'])),
                    F1=F1, F2=F2, F3=F3,
                ))
    return pd.DataFrame(trials)


def fit_dcl_glm(df):
    df2 = df.copy()
    df2['F1_F2'] = df2['F1'] * df2['F2']
    df2['F1_F3'] = df2['F1'] * df2['F3']
    df2['F2_F3'] = df2['F2'] * df2['F3']
    predictors = ['F1', 'F2', 'F3', 'F1_F2', 'F1_F3', 'F2_F3']
    X = sm.add_constant(df2[predictors].astype(float))
    y = df2['correct'].astype(float)
    model = sm.Logit(y, X).fit(disp=False)
    return model, df2, predictors


# ── DCL key conditions ─────────────────────────────────────────────────────────
DCL_KEY_CONDITIONS = [
    ('Uncued · ZdCoh · Near',               0, 0, 0),
    ('Uncued · ZdCoh · Far',                0, 0, 1),
    ('Cued · ZdCoh · Near',                 1, 0, 0),
    ('Cued · ZdCoh · Far',                  1, 0, 1),
    ('Cued · ZdNoi · Near',                 1, 1, 0),
    ('Cued · ZdNoi · Far  \u2605 optimal',  1, 1, 1),
]

def pred_pct_dcl(params, F1, F2, F3):
    lo = (params['const']
          + params['F1']*F1 + params['F2']*F2 + params['F3']*F3
          + params['F1_F2']*F1*F2 + params['F1_F3']*F1*F3 + params['F2_F3']*F2*F3)
    return sigmoid(lo)*100, lo


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 8 — DCL design + predictors
# ══════════════════════════════════════════════════════════════════════════════

DCL_FACTOR_DEFS = [
    ('F1', 'dot-onset cueing',
     '1\u202f=\u202fdelayed-onset field translates (cued);  0\u202f=\u202fnon-delayed field translates (uncued)'),
    ('F2', 'object depth+color continuity',
     '1\u202f=\u202ftranslating field retains its depth+color identity (ZdNoi);  '
     '0\u202f=\u202ftranslating field changes depth+color (ZdCoh)'),
    ('F3', 'translator depth plane',
     '1\u202f=\u202fFar;  0\u202f=\u202fNear   [covariate; same polarity as F4 in Exp\u202f1]'),
]

DCL_PARAS = [
    (
        "Experiment 2 tests whether depth-plane disruption affects the attended object "
        "specifically or the scene as a whole. "
        "Color and depth are always linked (Near\u202f=\u202fRed, Far\u202f=\u202fGreen) "
        "and two swap conditions are used. "
        "In ZdCoh, the coherent translating dots change depth+color at tStart; "
        "in ZdNoi, the incoherent background dots change depth+color. "
        "Critically, both conditions involve the same total amount of depth change in the scene "
        "(50\u202f% of all dots in each case). "
        "Any difference in cueing performance therefore reflects object-specific depth continuity, "
        "not a general scene-disruption effect."
    ),
    (
        "The factor structure mirrors Exp\u202f1. "
        "F1 (dot-onset cueing) is coded identically. "
        "F2 now captures depth+color object continuity jointly "
        "(depth and color cannot be dissociated in this design; "
        "the Exp\u202f1 result establishes that this effect is predominantly depth). "
        "F3 (translator depth plane; 1\u202f=\u202fFar, 0\u202f=\u202fNear) is the same "
        "covariate as F4 in Exp\u202f1. "
        "There is no separate color factor. "
        "Interactions F1\u202f\u00d7\u202fF2, F1\u202f\u00d7\u202fF3, and "
        "F2\u202f\u00d7\u202fF3 are specified by the same experimental logic as Exp\u202f1."
    ),
]

def make_dcl_design_page():
    fig = plt.figure(figsize=(8.5, 11))
    fig.patch.set_facecolor('white')

    y = 0.945; lh = 0.0215; lhs = 0.017

    # Section banner
    ax_b = fig.add_axes([0.08, y - 0.008, 0.84, 0.028])
    ax_b.set_facecolor('#1a3a8b'); ax_b.axis('off')
    ax_b.text(0.5, 0.5, 'EXPERIMENT 2  —  DepthColorLinked',
              ha='center', va='center', fontsize=11, fontweight='bold',
              color='white', transform=ax_b.transAxes)
    y -= 0.042

    fig.text(0.10, y, 'Design and predictors',
             fontsize=14, fontweight='bold', color='#1a1a2e', fontfamily='serif', va='top')
    y -= 0.028
    fig.text(0.10, y,
             f'{DCL_ASSET_LABEL}  \u00b7  n\u202f=\u202f1024  \u00b7  4 sessions',
             fontsize=9, color='#555555', fontfamily='serif', style='italic', va='top')
    y -= 0.018
    fig.add_axes([0.10, y, 0.80, 0.001]).set_facecolor('#333333')
    fig.axes[-1].axis('off')
    y -= 0.012
    for line in DCL_SESSION_LABELS.split('  ·  '):
        fig.text(0.10, y, line.strip(), fontsize=8.5, color='#444444',
                 fontfamily='monospace', va='top')
        y -= lhs * 1.2
    y -= 0.010
    fig.add_axes([0.10, y, 0.80, 0.0008]).set_facecolor('#bbbbbb')
    fig.axes[-1].axis('off')
    y -= 0.018

    fig.text(0.10, y, 'Predictors', fontsize=11, fontweight='bold',
             color='#1a1a2e', fontfamily='serif', va='top')
    y -= lh * 1.4

    for fnum, fname, coding in DCL_FACTOR_DEFS:
        ax_tag = fig.add_axes([0.10, y - 0.007, 0.030, 0.017])
        ax_tag.set_facecolor('#ddeeff')
        for sp in ax_tag.spines.values():
            sp.set_edgecolor('#1a3a8b'); sp.set_linewidth(0.8)
        ax_tag.set_xticks([]); ax_tag.set_yticks([])
        ax_tag.text(0.5, 0.5, fnum, ha='center', va='center',
                    fontsize=10, fontweight='bold', color='#1a3a8b',
                    transform=ax_tag.transAxes)
        fig.text(0.143, y, fname, fontsize=10.5, fontweight='bold',
                 color='#222222', fontfamily='serif', va='top')
        y -= lh
        fig.text(0.143, y, coding, fontsize=9, color='#555555',
                 fontfamily='serif', style='italic', va='top')
        y -= lhs * 1.9

    y -= 0.006
    eq_h = 0.050
    ax_eq = fig.add_axes([0.10, y - eq_h, 0.80, eq_h])
    ax_eq.set_facecolor('#f0f4ff')
    for sp in ax_eq.spines.values():
        sp.set_edgecolor('#1a3a8b'); sp.set_linewidth(0.8)
    ax_eq.set_xticks([]); ax_eq.set_yticks([])
    ax_eq.text(0.5, 0.5, DCL_MODEL_EQ, ha='center', va='center',
               fontsize=9.5, fontfamily='monospace', color='#1a3a8b',
               transform=ax_eq.transAxes, linespacing=1.6)
    y -= (eq_h + 0.018)

    fig.add_axes([0.10, y, 0.80, 0.0008]).set_facecolor('#bbbbbb')
    fig.axes[-1].axis('off')
    y -= 0.018
    fig.text(0.10, y, 'Rationale', fontsize=11, fontweight='bold',
             color='#1a1a2e', fontfamily='serif', va='top')
    y -= lh * 1.5

    for para in DCL_PARAS:
        for line in textwrap.wrap(para, width=88):
            fig.text(0.10, y, line, fontsize=9.5, color='#111111',
                     fontfamily='serif', va='top')
            y -= 0.018
        y -= 0.018

    fname_str = os.path.basename(OUT_PDF_SP)
    fig.text(0.10, 0.028, f'{fname_str}  \u00b7  {DATE_STR}  \u00b7  p.\u202f8/13',
             fontsize=7.5, color='#888888', fontfamily='serif', va='top')
    return fig


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 9 — DCL factor bars
# ══════════════════════════════════════════════════════════════════════════════

def make_dcl_bar_page(df_dcl):
    fig = plt.figure(figsize=(11, 7))
    fig.patch.set_facecolor('white')

    fig.text(0.5, 0.96,
             'Exp\u202f2  GLM predictors F1\u2013F3  \u2014  performance by factor level',
             ha='center', va='top', fontsize=13, fontweight='bold', color='#1a1a2e')
    fig.text(0.5, 0.915,
             f'{DCL_ASSET_LABEL}  \u00b7  n\u202f=\u202f1024  \u00b7  Wilson 95\u202f% CI  \u00b7  '
             '\u0394\u202f=\u202fleft minus right',
             ha='center', va='top', fontsize=8.5, color='#555555', style='italic')

    gs = gridspec.GridSpec(1, 2, figure=fig,
                           left=0.07, right=0.97, bottom=0.30, top=0.87,
                           wspace=0.12)
    ax_pct = fig.add_subplot(gs[0, 0])
    ax_lo  = fig.add_subplot(gs[0, 1])

    positions = get_positions(DCL_FACTORS)
    draw_bars(ax_pct, df_dcl, positions, use_lo=False, factors=DCL_FACTORS)
    draw_bars(ax_lo,  df_dcl, positions, use_lo=True,  factors=DCL_FACTORS)

    fname_str = os.path.basename(OUT_PDF_SP)
    fig.text(0.10, 0.015, f'{fname_str}  \u00b7  {DATE_STR}  \u00b7  p.\u202f9/13',
             fontsize=7.5, color='#888888', va='top')
    return fig


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 10 — DCL coefficients + conditional AMEs (combined)
# ══════════════════════════════════════════════════════════════════════════════

DCL_COND_AME_DATA = [
    ('F1', 'F2', 1, 'F1 (dot cueing)\nwhen ZdNoi  (F2=1)',   '#333333'),
    ('F1', 'F2', 0, 'F1 (dot cueing)\nwhen ZdCoh  (F2=0)',  '#999999'),
    ('F2', 'F1', 1, 'F2 (obj continuity)\nwhen dot-cued  (F1=1)',  '#116688'),
    ('F2', 'F1', 0, 'F2 (obj continuity)\nwhen dot-uncued  (F1=0)', '#88aabb'),
]

def make_dcl_coeff_page(model, df2, predictors):
    fig = plt.figure(figsize=(11, 8))
    fig.patch.set_facecolor('white')

    fig.text(0.5, 0.965, 'Exp\u202f2  Estimated coefficients + Conditional AMEs',
             ha='center', va='top', fontsize=13, fontweight='bold', color='#1a1a2e')
    fig.text(0.5, 0.930,
             f'{DCL_ASSET_LABEL}  \u00b7  n\u202f=\u202f1024  \u00b7  logistic regression',
             ha='center', va='top', fontsize=8.5, color='#555555', style='italic')

    # Left: forest plot (log-odds + AME)
    gs = gridspec.GridSpec(1, 2, figure=fig,
                           left=0.26, right=0.97, bottom=0.14, top=0.87,
                           wspace=0.08)
    ax_lo  = fig.add_subplot(gs[0, 0])
    ax_ame = fig.add_subplot(gs[0, 1])

    n_rows = len(DCL_COEFF_ORDER)
    ys = list(range(n_rows - 1, -1, -1))
    ci = model.conf_int()

    def row_y(y_pos):
        return 0.14 + (y_pos + 0.7) / (n_rows + 0.4) * 0.73

    for i, key in enumerate(DCL_COEFF_ORDER):
        y_pos = ys[i]
        coef  = model.params[key]
        cilo  = ci.loc[key, 0]; cihi = ci.loc[key, 1]
        pval  = model.pvalues[key]
        stars = pstars(pval)
        col   = DCL_COEFF_COLORS.get(key, '#555555')
        is_ix = key in ('F1_F2', 'F1_F3', 'F2_F3')

        ax_lo.plot([cilo, cihi], [y_pos, y_pos], '-', color=col, lw=2.2, zorder=2)
        ax_lo.plot(coef, y_pos, 'D' if is_ix else 'o', color=col, ms=7, zorder=3)
        ax_lo.text(cihi + 0.06, y_pos,
                   f'{coef:+.2f} [{cilo:+.2f}, {cihi:+.2f}]  {stars}',
                   va='center', fontsize=7.5, color='#111111',
                   fontweight='bold' if stars not in ('n.s.', '') else 'normal')

        if not is_ix:
            ame = compute_ame(model, df2, key, predictors, ix_cols=DCL_IX)
            bar_col = col if ame >= 0 else '#c0392b'
            ax_ame.barh(y_pos, ame, height=0.45, color=bar_col, alpha=0.82,
                        edgecolor='white', zorder=2)
            ax_ame.text(ame + (0.5 if ame >= 0 else -0.5), y_pos,
                        f'{ame:+.1f}\u202fpp',
                        va='center', ha='left' if ame >= 0 else 'right',
                        fontsize=8.5, color='#111111')
        else:
            ax_ame.text(0, y_pos, 'cond. AME\u2192', va='center', ha='center',
                        fontsize=7.5, color='#888888', style='italic')

        fig.text(0.250, row_y(y_pos), DCL_COEFF_LABELS.get(key, key),
                 ha='right', va='center', fontsize=9, color=col,
                 fontweight='bold' if is_ix else 'normal')

    for ax, xlabel, title in [
            (ax_lo,  'Log-odds coefficient  (95\u202f% CI)', 'Log-odds'),
            (ax_ame, 'Average Marginal Effect  (pp)', 'AME  (pp)\u2014main effects only')]:
        ax.axvline(0, color='#666666', lw=0.8, zorder=1)
        ax.set_yticks(ys); ax.set_yticklabels([])
        ax.set_ylim(-0.7, n_rows - 0.3)
        ax.set_xlabel(xlabel, fontsize=9)
        ax.set_title(title, fontsize=10, fontweight='bold')
        ax.spines[['top', 'right']].set_visible(False)
        ax.xaxis.grid(True, lw=0.4, color='#e8e8e8', zorder=0)
        ax.set_axisbelow(True)

    # Intercept note
    b0   = model.params['const']
    b0lo = ci.loc['const', 0]; b0hi = ci.loc['const', 1]
    b0p  = model.pvalues['const']
    p0   = 1 / (1 + math.exp(-b0)) * 100
    fig.text(0.26, 0.080,
             f'\u03b20 = {b0:+.3f}  [{b0lo:+.3f}, {b0hi:+.3f}]  p\u202f=\u202f{b0p:.4f}',
             ha='left', va='top', fontsize=8, color='#555555', style='italic')
    fig.text(0.26, 0.058,
             f'\u2248\u202f{p0:.1f}% predicted correct when all predictors\u202f=\u202f0'
             f'  (uncued, ZdCoh, Near translator)',
             ha='left', va='top', fontsize=8, color='#555555', style='italic')

    # Conditional AME inset (bottom-right)
    ix_coef  = model.params.get('F1_F2', float('nan'))
    ix_stars = pstars(model.pvalues.get('F1_F2', 1.0))

    ax_cond = fig.add_axes([0.50, 0.015, 0.46, 0.28])
    ax_cond.set_facecolor('#fafafa')
    for sp in ax_cond.spines.values():
        sp.set_edgecolor('#cccccc'); sp.set_linewidth(0.7)
    ax_cond.set_title(
        f'Conditional AMEs  (F1\u00d7F2\u202f=\u202f{ix_coef:+.2f}\u202f{ix_stars})',
        fontsize=9.5, fontweight='bold', pad=6)

    bar_ys = [3, 2, 1, 0]
    cond_vals = [
        compute_conditional_ame(model, df2, var, cvar, cval, predictors, ix_cols=DCL_IX)
        for var, cvar, cval, lbl, col in DCL_COND_AME_DATA
    ]
    tick_colors = [c for *_, c in DCL_COND_AME_DATA]
    for (var, cvar, cval, lbl, col), cy, ame in zip(DCL_COND_AME_DATA, bar_ys, cond_vals):
        ax_cond.barh(cy, ame, height=0.55, color=col, alpha=0.85, edgecolor='white', zorder=2)
        xoff = 1.0 if ame >= 0 else -1.0
        ax_cond.text(ame + xoff, cy, f'{ame:+.1f}\u202fpp',
                     va='center', ha='left' if ame >= 0 else 'right',
                     fontsize=9.5, fontweight='bold', color='#111111')
    ax_cond.axhline(1.5, color='#cccccc', lw=1.0, ls='--', zorder=1)
    ax_cond.axvline(0, color='#444444', lw=1.0, zorder=1)
    ax_cond.set_xlim(-8, 55)
    ax_cond.set_ylim(-0.55, 3.55)
    ax_cond.set_yticks([0, 1, 2, 3])
    ax_cond.set_yticklabels([
        'F2  when dot-uncued  (F1=0)',
        'F2  when dot-cued  (F1=1)',
        'F1  when ZdCoh  (F2=0)',
        'F1  when ZdNoi  (F2=1)',
    ], fontsize=8.5)
    for tick, col in zip(ax_cond.get_yticklabels(), tick_colors):
        tick.set_color(col)
    ax_cond.tick_params(axis='y', length=0, pad=6)
    ax_cond.set_xlabel('Average Marginal Effect (pp)', fontsize=9)
    ax_cond.xaxis.grid(True, lw=0.4, color='#e8e8e8', zorder=0)
    ax_cond.set_axisbelow(True)
    ax_cond.spines[['top', 'right']].set_visible(False)

    fname_str = os.path.basename(OUT_PDF_SP)
    fig.text(0.10, 0.008, f'{fname_str}  \u00b7  {DATE_STR}  \u00b7  p.\u202f10/13',
             fontsize=7.5, color='#888888', va='top')
    return fig


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 11 — DCL interpretation + fitted equation + key conditions
# ══════════════════════════════════════════════════════════════════════════════

DCL_INTERP_PARAS = [
    (
        "The DepthColorLinked design provides a critical control absent from Exp\u202f1. "
        "Both swap conditions involve the same total depth+color change in the scene: "
        "50\u202f% of all dots change at tStart. "
        "The difference is which 50\u202f%: in ZdCoh, the coherent translating dots change "
        "(disrupting the tracked object\u2019s identity); "
        "in ZdNoi, only the incoherent background dots change. "
        "The disruption is therefore object-specific, not a dose-response to scene change."
    ),
    (
        "The F1\u202f\u00d7\u202fF2 interaction dominates the model, replicating the "
        "structure of Exp\u202f1. "
        "When the translating object\u2019s depth+color identity is disrupted (ZdCoh), "
        "the cueing benefit is substantially reduced but not eliminated: "
        "CUED+ZdCoh remains above the UNCUED arm, consistent with the onset cue "
        "retaining partial selection capability even without object-identity continuity. "
        "The UNCUED arm is flat across ZdNoi and ZdCoh, confirming the asymmetry: "
        "depth+color continuity alone provides no selection advantage\u2014it is only "
        "effective when the temporal onset cue has established an initial object representation."
    ),
    (
        "The F3 (Near/Far) covariate shows the same robust Far\u202f>\u202fNear advantage "
        "observed in Exp\u202f1, here approximately\u202f+21\u202fpp. "
        "Because Near and Far always differ in both disparity and color in this design "
        "(Near=Red, Far=Green), the F3 main effect in Exp\u202f2 cannot be attributed purely "
        "to stereoscopic depth; the Exp\u202f1 color-null result establishes depth as the "
        "driver, but the confound should be noted."
    ),
]

def make_dcl_interp_page(model, df2, predictors):
    params = model.params
    fig = plt.figure(figsize=(11, 8.5))
    fig.patch.set_facecolor('white')

    fig.text(0.5, 0.968, 'Exp\u202f2  Fitted equation and interpretation',
             ha='center', va='top', fontsize=13, fontweight='bold', color='#1a1a2e')
    fig.text(0.5, 0.933, f'{DCL_ASSET_LABEL}  \u00b7  n\u202f=\u202f1024',
             ha='center', va='top', fontsize=8.5, color='#555555', style='italic')

    # Fitted equation box
    p = params
    eq1 = (f'log-odds(correct)  =  {p["const"]:+.3f}'
           f'  +  {p["F1"]:+.3f}\u00b7F1'
           f'  +  {p["F2"]:+.3f}\u00b7F2'
           f'  +  {p["F3"]:+.3f}\u00b7F3')
    eq2 = (f'    +  {p["F1_F2"]:+.3f}\u00b7(F1\u00d7F2)'
           f'  +  {p["F1_F3"]:+.3f}\u00b7(F1\u00d7F3)'
           f'  +  {p["F2_F3"]:+.3f}\u00b7(F2\u00d7F3)')
    ax_eq = fig.add_axes([0.06, 0.855, 0.88, 0.065])
    ax_eq.set_facecolor('#f0f4ff')
    for sp in ax_eq.spines.values():
        sp.set_edgecolor('#1a3a8b'); sp.set_linewidth(0.8)
    ax_eq.set_xticks([]); ax_eq.set_yticks([])
    ax_eq.text(0.5, 0.75, eq1, ha='center', va='center', fontsize=9.5,
               fontfamily='monospace', color='#1a3a8b', transform=ax_eq.transAxes)
    ax_eq.text(0.5, 0.20, eq2, ha='center', va='center', fontsize=9.5,
               fontfamily='monospace', color='#1a3a8b', transform=ax_eq.transAxes)

    # Key conditions table (left)
    ax_tbl = fig.add_axes([0.06, 0.22, 0.42, 0.60])
    ax_tbl.axis('off')
    ax_tbl.set_title('Predicted % correct — key conditions  (F3=0\u202f=\u202fNear, F3=1\u202f=\u202fFar)',
                     fontsize=8.5, fontweight='bold', pad=8, loc='left')

    col_headers = ['Condition', 'F1', 'F2', 'F3', 'Log-odds', '% corr']
    col_xs      = [0.0, 0.55, 0.63, 0.71, 0.81, 0.93]
    col_ha      = ['left', 'center', 'center', 'center', 'right', 'right']
    HDR_Y = 0.91
    for cx, hdr, ha in zip(col_xs, col_headers, col_ha):
        ax_tbl.text(cx, HDR_Y, hdr, ha=ha, va='top', fontsize=8.5,
                    fontweight='bold', color='#1a1a2e', transform=ax_tbl.transAxes)
    ax_tbl.plot([0, 1], [HDR_Y - 0.04, HDR_Y - 0.04], color='#333333', lw=0.8,
                transform=ax_tbl.transAxes, clip_on=False)

    n_rows = len(DCL_KEY_CONDITIONS)
    row_h  = (HDR_Y - 0.08) / n_rows
    row_colors = ['#f0f4ff', '#ffffff', '#ffffff', '#ddeedd', '#f5e8e8', '#ffffff']
    for ri, (lbl, F1, F2, F3) in enumerate(DCL_KEY_CONDITIONS):
        pct, lo = pred_pct_dcl(params, F1, F2, F3)
        ry = HDR_Y - 0.06 - ri * row_h
        ax_tbl.add_patch(plt.Rectangle(
            (0, ry - row_h + 0.005), 1.0, row_h - 0.005,
            facecolor=row_colors[ri], transform=ax_tbl.transAxes,
            zorder=0, clip_on=False))
        vals = [lbl, str(F1), str(F2), str(F3), f'{lo:+.2f}', f'{pct:.1f}%']
        bold = (ri == 5)
        for cx, v, ha in zip(col_xs, vals, col_ha):
            ax_tbl.text(cx, ry - 0.005, v, ha=ha, va='top', fontsize=8.5,
                        fontweight='bold' if bold else 'normal',
                        color='#1a3a8b' if bold else '#111111',
                        transform=ax_tbl.transAxes)
    ax_tbl.plot([0, 1], [0.02, 0.02], color='#cccccc', lw=0.6,
                transform=ax_tbl.transAxes, clip_on=False)

    # Interpretation prose (right)
    y = 0.815; lh = 0.017; gap = 0.016
    for para in DCL_INTERP_PARAS:
        for line in textwrap.wrap(para, width=62):
            fig.text(0.52, y, line, ha='left', va='top',
                     fontsize=9, color='#111111', fontfamily='serif')
            y -= lh
        y -= gap

    fname_str = os.path.basename(OUT_PDF_SP)
    fig.text(0.10, 0.018, f'{fname_str}  \u00b7  {DATE_STR}  \u00b7  p.\u202f11/13',
             fontsize=7.5, color='#888888', va='top')
    return fig


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 12 — DCL predicted vs observed (ZdNoi/ZdCoh × Far/Near)
# ══════════════════════════════════════════════════════════════════════════════

def make_dcl_pred_obs_page(model, df2, predictors):
    from matplotlib.patches import Patch as _Patch
    dfw = df2.copy()
    dfw['_pred'] = model.predict()

    def wci(pct, nn):
        if nn == 0: return 0, 0
        k = round(pct * nn / 100)
        p = k / nn; z = 1.96; d = 1 + z**2/nn
        c = (p + z**2/(2*nn)) / d
        hw = z * math.sqrt(p*(1-p)/nn + z**2/(4*nn**2)) / d
        return (p-(c-hw))*100, ((c+hw)-p)*100

    fig = plt.figure(figsize=(11, 8))
    fig.patch.set_facecolor('white')
    fig.text(0.5, 0.968, 'Exp\u202f2  Model fit: predicted vs. observed',
             ha='center', va='top', fontsize=13, fontweight='bold', color='#1a1a2e')
    fig.text(0.5, 0.933,
             f'{DCL_ASSET_LABEL}  \u00b7  n\u202f=\u202f1024  \u00b7  '
             '2 conditions (ZdNoi/ZdCoh) \u00d7 CUED/UNCUED \u00d7 Far/Near',
             ha='center', va='top', fontsize=8.5, color='#555555', style='italic')

    gs = gridspec.GridSpec(1, 2, figure=fig,
                           left=0.07, right=0.97, bottom=0.18, top=0.87,
                           wspace=0.35)
    ax_sc  = fig.add_subplot(gs[0, 0])
    ax_bar = fig.add_subplot(gs[0, 1])

    # Conditions: (F1, F2, F3) → label
    cond_specs = [
        (1, 1, 1, '#2255aa', 'o',  'ZdNoi+C+Far'),
        (1, 1, 0, '#88aadd', 'o',  'ZdNoi+C+Near'),
        (1, 0, 1, '#c0392b', 'o',  'ZdCoh+C+Far'),
        (1, 0, 0, '#e08080', 'o',  'ZdCoh+C+Near'),
        (0, 1, 1, '#2255aa', '^',  'ZdNoi+U+Far'),
        (0, 1, 0, '#88aadd', '^',  'ZdNoi+U+Near'),
        (0, 0, 1, '#c0392b', '^',  'ZdCoh+U+Far'),
        (0, 0, 0, '#e08080', '^',  'ZdCoh+U+Near'),
    ]

    grp  = dfw.groupby(['F1', 'F2', 'F3'])
    obs  = grp['correct'].mean() * 100
    pred = grp['_pred'].mean()   * 100
    n_   = grp['correct'].count()

    # Scatter
    for f1, f2, f3, col, mk, lbl in cond_specs:
        key = (f1, f2, f3)
        if key not in obs.index: continue
        o = obs[key]; p_ = pred[key]; nn = n_[key]
        elo, ehi = wci(o, nn)
        ax_sc.errorbar(o, p_, xerr=[[elo], [ehi]], fmt=mk,
                       color=col, ms=8, mec='white', mew=0.6,
                       ecolor=col, elinewidth=1, capsize=3, zorder=3)
        ax_sc.annotate(lbl, (o, p_), textcoords='offset points',
                       xytext=(5, 3), fontsize=7, color=col)
    lo, hi = 10, 70
    ax_sc.plot([lo, hi], [lo, hi], '--', color='#888888', lw=0.9, zorder=1)
    ax_sc.set_xlim(lo, hi); ax_sc.set_ylim(lo, hi)
    ax_sc.set_xlabel('Observed % correct', fontsize=10)
    ax_sc.set_ylabel('Predicted % correct', fontsize=10)
    ax_sc.set_title('Scatter: predicted vs. observed', fontsize=10, fontweight='bold')
    ax_sc.spines[['top', 'right']].set_visible(False)
    ax_sc.xaxis.grid(True, lw=0.4, color='#e0e0e0', zorder=0)
    ax_sc.yaxis.grid(True, lw=0.4, color='#e0e0e0', zorder=0)
    ax_sc.set_axisbelow(True)

    # Bar chart: ZdNoi vs ZdCoh panels within one axes, Far/Near color-coded
    bar_groups = [
        # (f2, f1, f3, col, x_offset, label)
        (1, 1, 1, '#2255aa', 0,   'ZdNoi\nC·Far'),
        (1, 1, 0, '#88aadd', 1,   'ZdNoi\nC·Near'),
        (1, 0, 1, '#666666', 2,   'ZdNoi\nU·Far'),
        (1, 0, 0, '#aaaaaa', 3,   'ZdNoi\nU·Near'),
        (0, 1, 1, '#c0392b', 5,   'ZdCoh\nC·Far'),
        (0, 1, 0, '#e08080', 6,   'ZdCoh\nC·Near'),
        (0, 0, 1, '#885544', 7,   'ZdCoh\nU·Far'),
        (0, 0, 0, '#ccaa99', 8,   'ZdCoh\nU·Near'),
    ]
    bw = 0.38
    for f2, f1, f3, col, xi, lbl in bar_groups:
        key = (f1, f2, f3)
        if key not in obs.index: continue
        o  = obs[key]; p_ = pred[key]; nn = n_[key]
        elo, ehi = wci(o, nn)
        ax_bar.bar(xi - bw/2, o,  width=bw, color=col, alpha=0.88, zorder=2)
        ax_bar.bar(xi + bw/2, p_, width=bw, color=col, alpha=0.35, hatch='///', zorder=2)
        ax_bar.errorbar(xi - bw/2, o, yerr=[[elo], [ehi]],
                        fmt='none', ecolor='#333', elinewidth=0.9, capsize=2.5, zorder=3)
    # separator between ZdNoi and ZdCoh groups
    ax_bar.axvline(4.5, color='#cccccc', lw=1.0, ls='--', zorder=1)
    ax_bar.text(2, 73, 'ZdNoi  (translator stable)',
                ha='center', fontsize=8.5, color='#116688', fontweight='bold')
    ax_bar.text(6.5, 73, 'ZdCoh  (translator changes)',
                ha='center', fontsize=8.5, color='#c0392b', fontweight='bold')
    ax_bar.axhline(100/8, color='#cc4444', lw=0.9, ls='--', zorder=1)
    ax_bar.set_xticks([xi for *_, xi, _ in bar_groups])
    ax_bar.set_xticklabels([lbl for *_, lbl in bar_groups], fontsize=7.5)
    ax_bar.set_ylim(0, 80)
    ax_bar.set_yticks([0, 12.5, 25, 50, 75])
    ax_bar.set_yticklabels(['0', '12.5', '25', '50', '75'], fontsize=8)
    ax_bar.set_ylabel('% correct', fontsize=10)
    ax_bar.set_title('Observed (solid) vs. predicted (hatched)', fontsize=10, fontweight='bold')
    ax_bar.spines[['top', 'right']].set_visible(False)
    ax_bar.yaxis.grid(True, lw=0.4, color='#e0e0e0', zorder=0)
    ax_bar.set_axisbelow(True)

    leg = [
        _Patch(facecolor='#555', alpha=0.88, label='Observed'),
        _Patch(facecolor='#555', alpha=0.35, hatch='///', label='Predicted'),
        _Patch(facecolor='#2255aa', label='Far translator'),
        _Patch(facecolor='#993333', label='Near translator'),
    ]
    fig.legend(handles=leg, loc='lower center', ncol=4, fontsize=8,
               bbox_to_anchor=(0.5, 0.00), framealpha=0.9)

    fname_str = os.path.basename(OUT_PDF_SP)
    fig.text(0.10, 0.008, f'{fname_str}  \u00b7  {DATE_STR}  \u00b7  p.\u202f12/13',
             fontsize=7.5, color='#888888', va='top')
    return fig


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 13 — Cross-experiment synthesis
# ══════════════════════════════════════════════════════════════════════════════

SYNTH_PARAS = [
    (
        "Both experiments show the same structural result: the F1\u202f\u00d7\u202fF2 "
        "interaction dominates, and the Far\u202f>\u202fNear asymmetry is large and robust. "
        "The two factors are not symmetric in their independent contributions. "
        "In both experiments, the CUED arm retains a small but positive advantage "
        "even when depth continuity is disrupted (~+10\u202fpp in Exp\u202f1; "
        "see CUED+ZdCoh in Exp\u202f2): the onset cue provides partial surface selection "
        "even without depth-plane binding. "
        "The UNCUED arm is flat regardless of depth continuity in both experiments: "
        "depth-plane identity alone drives no selection. "
        "The onset cue is weakly sufficient on its own; depth continuity is effective "
        "only in its presence. "
        "Neither the magnitude of scene-level depth change nor color-field identity "
        "modulates this asymmetry\u2014what matters is whether the depth identity "
        "of the onset-cued object is preserved at translation onset."
    ),
    (
        "The F1\u202f\u00d7\u202fF2 interaction is larger in Exp\u202f1 (+32.7\u202fpp***) "
        "than Exp\u202f2 (+16.5\u202fpp**). "
        "In Exp\u202f1, 100\u202f% of the coherent translating field changes depth plane "
        "(complete identity disruption); in Exp\u202f2 ZdCoh, only the coherent portion "
        "changes. The difference in magnitude is consistent with partial vs. complete "
        "disruption, though other factors (e.g., Near/Far distribution of disruption) "
        "may also contribute."
    ),
    (
        "The Far\u202f>\u202fNear asymmetry is present in both experiments and is "
        "of similar sign and order of magnitude (Exp\u202f1: +15.3\u202fpp; "
        "Exp\u202f2: +21.4\u202fpp). "
        "The UNCUED Near vs. Far comparison (chart, left) is a direct test of whether "
        "this asymmetry is cue-locked or structural. "
        "If Far\u202f>\u202fNear is present in the UNCUED arm, it is consistent with "
        "a standing fixation-plane attentional bias or a sensory asymmetry in "
        "uncrossed vs. crossed disparity processing. "
        "A full account is developed in fixation_plane_hypothesis.pdf."
    ),
]

def make_synthesis_page(dd_model, dd_df2, dd_pred, dcl_model, dcl_df2, dcl_pred):
    from matplotlib.patches import Patch as _Patch
    fname_str = os.path.basename(OUT_PDF_SP)

    fig = plt.figure(figsize=(11, 8.5))
    fig.patch.set_facecolor('white')
    fig.text(0.5, 0.968, 'Cross-experiment synthesis',
             ha='center', va='top', fontsize=13, fontweight='bold', color='#1a1a2e')
    fig.text(0.5, 0.933,
             'Exp\u202f1 (DecoupledDots, n=2051)  vs.  Exp\u202f2 (DepthColorLinked, n=1024)',
             ha='center', va='top', fontsize=8.5, color='#555555', style='italic')

    # ── Left panel: comparison forest plot ───────────────────────────────────
    ax_f = fig.add_axes([0.07, 0.30, 0.40, 0.58])
    ax_f.set_facecolor('#fafafa')
    for sp in ax_f.spines.values():
        sp.set_edgecolor('#cccccc'); sp.set_linewidth(0.7)
    ax_f.set_title('Key AMEs: Exp\u202f1 vs. Exp\u202f2', fontsize=10, fontweight='bold', pad=8)

    compare_rows = [
        ('F1 (dot cueing)',         'F1',  DD_IX,  DCL_IX,  '#333333'),
        ('F2 (depth continuity)',   'F2',  DD_IX,  DCL_IX,  '#116688'),
        ('F\u2093 (Far\u202f>\u202fNear)', 'F4', DD_IX, None, '#4477bb'),
        ('F1\u202f\u00d7\u202fF2 interaction', None, None, None, '#8833aa'),
    ]

    dd_ames, dcl_ames = [], []
    for label, key, ix_dd, ix_dcl, col in compare_rows:
        if key == 'F4':
            dd_v  = compute_ame(dd_model,  dd_df2,  'F4', dd_pred,  ix_cols=DD_IX)
            dcl_v = compute_ame(dcl_model, dcl_df2, 'F3', dcl_pred, ix_cols=DCL_IX)
        elif key is None:  # interaction — use conditional AME difference
            dd_v  = (compute_conditional_ame(dd_model,  dd_df2,  'F1', 'F2', 1, dd_pred,  DD_IX)
                   - compute_conditional_ame(dd_model,  dd_df2,  'F1', 'F2', 0, dd_pred,  DD_IX))
            dcl_v = (compute_conditional_ame(dcl_model, dcl_df2, 'F1', 'F2', 1, dcl_pred, DCL_IX)
                   - compute_conditional_ame(dcl_model, dcl_df2, 'F1', 'F2', 0, dcl_pred, DCL_IX))
        else:
            dd_v  = compute_ame(dd_model,  dd_df2,  key, dd_pred,  ix_cols=DD_IX)
            dcl_v = compute_ame(dcl_model, dcl_df2, key, dcl_pred, ix_cols=DCL_IX)
        dd_ames.append(dd_v); dcl_ames.append(dcl_v)

    ys = list(range(len(compare_rows) - 1, -1, -1))
    for i, ((label, key, *_, col), y_pos, dd_v, dcl_v) in enumerate(
            zip(compare_rows, ys, dd_ames, dcl_ames)):
        ax_f.plot(dd_v,  y_pos + 0.18, 'o', color=col, ms=10, zorder=3, label='Exp 1' if i==0 else '')
        ax_f.plot(dcl_v, y_pos - 0.18, 's', color=col, ms=10, alpha=0.6, zorder=3, label='Exp 2' if i==0 else '')
        ax_f.text(max(dd_v, dcl_v) + 1.5, y_pos,
                  f'E1: {dd_v:+.1f}pp\nE2: {dcl_v:+.1f}pp',
                  va='center', fontsize=8, color=col)

    ax_f.axvline(0, color='#444444', lw=0.9, zorder=1)
    ax_f.set_yticks(ys)
    ax_f.set_yticklabels([r[0] for r in compare_rows], fontsize=9)
    for tick, (_, _, *_, col) in zip(ax_f.get_yticklabels(), compare_rows):
        tick.set_color(col)
    ax_f.tick_params(axis='y', length=0, pad=6)
    ax_f.set_xlabel('Average Marginal Effect (pp)', fontsize=9)
    ax_f.xaxis.grid(True, lw=0.4, color='#e8e8e8', zorder=0)
    ax_f.set_axisbelow(True)
    ax_f.spines[['top', 'right']].set_visible(False)
    ax_f.legend(loc='lower right', fontsize=8, framealpha=0.9)

    # ── Bottom-left: UNCUED Near vs Far bar (fixation-plane test) ────────────
    ax_unc = fig.add_axes([0.07, 0.06, 0.40, 0.20])
    ax_unc.set_facecolor('#fffaf0')
    for sp in ax_unc.spines.values():
        sp.set_edgecolor('#ddbb88'); sp.set_linewidth(0.7)
    ax_unc.set_title('UNCUED arm: Far vs. Near  [fixation-plane test]',
                     fontsize=8.5, fontweight='bold', color='#7a4400', pad=5)

    def bar_unc(df_, f3_col, x_far, x_near, label_prefix):
        unc = df_[df_['F1'] == 0]
        for xi, fval, col, lbl in [
                (x_far,  1, '#2255aa', f'{label_prefix}\nFar'),
                (x_near, 0, '#993333', f'{label_prefix}\nNear')]:
            sub = unc[unc[f3_col] == fval]
            k = int(sub['correct'].sum()); n = len(sub)
            pct = k/n*100 if n else 0
            lo, hi = wilson_ci(k, n)
            ax_unc.bar(xi, pct, width=0.5, color=col, alpha=0.85, zorder=2)
            ax_unc.errorbar(xi, pct, yerr=[[pct-lo*100], [hi*100-pct]],
                            fmt='none', ecolor='#333', elinewidth=0.9, capsize=3, zorder=3)
            ax_unc.text(xi, pct + 1.5, f'{pct:.1f}%', ha='center', fontsize=7.5, va='bottom')

    bar_unc(dd_df2,  'F4', 0.8, 1.3, 'Exp1')
    bar_unc(dcl_df2, 'F3', 2.3, 2.8, 'Exp2')
    ax_unc.axvline(1.8, color='#cccccc', lw=0.8, ls='--')
    ax_unc.axhline(100/8, color='#cc4444', lw=0.7, ls='--', zorder=1)
    ax_unc.set_xlim(0.4, 3.2)
    ax_unc.set_xticks([1.05, 2.55])
    ax_unc.set_xticklabels(['Exp 1', 'Exp 2'], fontsize=9)
    ax_unc.set_ylabel('% correct', fontsize=8)
    ax_unc.set_ylim(0, 50)
    ax_unc.spines[['top', 'right']].set_visible(False)
    ax_unc.yaxis.grid(True, lw=0.4, color='#e8e8e8', zorder=0)
    ax_unc.set_axisbelow(True)

    # ── Right: synthesis prose ────────────────────────────────────────────────
    y = 0.900; lh = 0.017; gap = 0.018
    for para in SYNTH_PARAS:
        for line in textwrap.wrap(para, width=60):
            fig.text(0.52, y, line, ha='left', va='top',
                     fontsize=9, color='#111111', fontfamily='serif')
            y -= lh
        y -= gap

    fig.text(0.10, 0.018, f'{fname_str}  \u00b7  {DATE_STR}  \u00b7  p.\u202f13/13',
             fontsize=7.5, color='#888888', va='top')
    return fig


# ── Main ───────────────────────────────────────────────────────────────────────
os.makedirs(BASE, exist_ok=True)
os.makedirs(BASE_SP, exist_ok=True)

df = load_all()
print(f'DD valid trials: {len(df)}')
model, df2, predictors = fit_glm(df)
print('DD GLM fitted.')

df_dcl = load_dcl()
print(f'DCL valid trials: {len(df_dcl)}')
if len(df_dcl) > 0:
    dcl_model, dcl_df2, dcl_predictors = fit_dcl_glm(df_dcl)
    print('DCL GLM fitted.')
else:
    dcl_model = dcl_df2 = dcl_predictors = None
    print('DCL data not found — pages 8-13 will be skipped.')

fig1  = make_text_page()
fig2  = make_bar_page(df)
fig3  = make_coeff_page(model, df2, predictors)
fig4  = make_cond_ame_page(model, df2, predictors)
fig5  = make_interpretation_page(model, df2, predictors)
fig6  = make_pred_obs_page(model, df2, predictors)
fig7  = make_f4_page(model, df2, predictors)

figs = [fig1, fig2, fig3, fig4, fig5, fig6, fig7]

if dcl_model is not None:
    fig8  = make_dcl_design_page()
    fig9  = make_dcl_bar_page(df_dcl)
    fig10 = make_dcl_coeff_page(dcl_model, dcl_df2, dcl_predictors)
    fig11 = make_dcl_interp_page(dcl_model, dcl_df2, dcl_predictors)
    fig12 = make_dcl_pred_obs_page(dcl_model, dcl_df2, dcl_predictors)
    fig13 = make_synthesis_page(model, df2, predictors,
                                dcl_model, dcl_df2, dcl_predictors)
    figs += [fig8, fig9, fig10, fig11, fig12, fig13]

for out in [OUT_PDF, OUT_PDF_SP]:
    with PdfPages(out) as pdf:
        for f in figs:
            pdf.savefig(f, bbox_inches='tight')

plt.close('all')
print(f'Saved: {OUT_PDF}')
print(f'Saved: {OUT_PDF_SP}')
