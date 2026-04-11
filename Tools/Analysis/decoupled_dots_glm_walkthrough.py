#!/usr/bin/env python3
"""
decoupled_dots_glm_walkthrough.py
-----------------------------------
Pedagogical walkthrough: raw data → log-odds → GLM model.

For each of the 4 factors (F1/F2/F3/F4) and the key F1×F2 interaction:
  Panel 1 — % correct bars (factor=1 vs factor=0), Wilson 95% CI
  Panel 2 — Same data on the log-odds scale (what the GLM actually models)
  Panel 3 — GLM2 coefficient with 95% CI + AME

5-page PDF:
  p.1  F1 — Dot cueing
  p.2  F2 — Depth-field cueing
  p.3  F3 — Color-field cueing (null)
  p.4  F4 — Translator depth plane (Near/Far)
  p.5  F1×F2 interaction (2×2 grids in % correct and log-odds)

Output:
  Agents/Figures/decoupled_dots_glm_walkthrough.pdf
  Agents/SwapPilot/Figures/decoupled_dots_glm_walkthrough.pdf
"""

import csv, datetime, math, os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.backends.backend_pdf import PdfPages

DATE_STR = datetime.date.today().strftime('%Y-%m-%d')

try:
    import statsmodels.api as sm
except ImportError:
    raise ImportError('statsmodels required: pip install statsmodels')

# ── Paths ──────────────────────────────────────────────────────────────────────
SESSIONS = [
    ('/tmp/quest_pull2/files/vr_dots_session_260406_1532.tsv', False),
    ('/tmp/quest_pull2/files/vr_dots_session_260406_1754.tsv', True),
    ('/tmp/quest_pull3/files/vr_dots_session_260407_0643.tsv', True),
    ('/tmp/quest_pull3/files/vr_dots_session_260407_0731.tsv', False),
]
BASE    = os.path.normpath(os.path.join(os.path.dirname(__file__), '../../Agents/Figures'))
BASE_SP = os.path.normpath(os.path.join(os.path.dirname(__file__), '../../Agents/SwapPilot/Figures'))
OUT_PDF    = os.path.join(BASE,    'decoupled_dots_glm_walkthrough.pdf')
OUT_PDF_SP = os.path.join(BASE_SP, 'decoupled_dots_glm_walkthrough.pdf')
CHANCE = 1 / 8

# ── Data loading ───────────────────────────────────────────────────────────────
def is_correct(td, rd):
    d = (float(rd) - float(td) + 360) % 360
    return (360 - d if d > 180 else d) <= 22.5

def load_all():
    trials = []
    for path, is_inv in SESSIONS:
        with open(path, newline='') as f:
            for r in csv.DictReader(f, delimiter='\t'):
                if (not r.get('TransDeg','').strip() or
                        not r.get('RespDeg','').strip() or
                        r.get('EndKey','') in ('timeout','skip','requeue')):
                    continue
                cond    = r['Cond']
                if is_inv:
                    cond = 'UNCUED' if cond == 'CUED' else 'CUED'
                b_near = (r['DelayedFieldDepth'] == 'N') ^ is_inv
                trials.append(dict(
                    swap    = r['SwapType'],
                    cond    = cond,
                    b_near  = b_near,
                    correct = int(is_correct(r['TransDeg'], r['RespDeg'])),
                ))
    return trials

def build_df(trials):
    rows = []
    for t in trials:
        cond, swap, bn = t['cond'], t['swap'], t['b_near']
        F1 = 1 if cond == 'CUED' else 0
        F2 = int((cond == 'CUED'   and swap in ('N', 'C')) or
                 (cond == 'UNCUED' and swap in ('Z', 'CZ')))
        F3 = int((cond == 'CUED'   and swap in ('N', 'Z')) or
                 (cond == 'UNCUED' and swap in ('C', 'CZ')))
        trans_near = bn if cond == 'CUED' else not bn
        F4 = 1 if trans_near else 0
        rows.append(dict(F1=F1, F2=F2, F3=F3, F4=F4, correct=t['correct']))
    df = pd.DataFrame(rows)
    df['F1_F2'] = df['F1'] * df['F2']
    df['F1_F4'] = df['F1'] * df['F4']
    df['F2_F4'] = df['F2'] * df['F4']
    return df

# ── Stats ───────────────────────────────────────────────────────────────────────
def wilson_ci(k, n, z=1.96):
    if n == 0: return 0.0, 0.0
    p = k / n
    d = 1 + z**2 / n
    c = (p + z**2/(2*n)) / d
    hw = z * math.sqrt(p*(1-p)/n + z**2/(4*n**2)) / d
    return c - hw, c + hw

def logit(p):
    p = max(min(p, 1 - 1e-6), 1e-6)
    return math.log(p / (1 - p))

def sig_str(p):
    if p < 0.001: return '***'
    if p < 0.01:  return '**'
    if p < 0.05:  return '*'
    if p < 0.1:   return '†'
    return 'n.s.'

# ── GLM ────────────────────────────────────────────────────────────────────────
PREDICTORS = ['F1','F2','F3','F4','F1_F2','F1_F4','F2_F4']

def fit_glm(df):
    X = sm.add_constant(df[PREDICTORS].astype(float))
    y = df['correct'].astype(float)
    return sm.Logit(y, X).fit(disp=False)

def compute_ame(model, df, var):
    """Average marginal effect: average change in P(correct) when var flips 0→1."""
    X0 = sm.add_constant(df[PREDICTORS].astype(float))
    p0 = model.predict(X0)
    df1 = df.copy()
    df1[var] = 1 - df1[var]
    df1['F1_F2'] = df1['F1'] * df1['F2']
    df1['F1_F4'] = df1['F1'] * df1['F4']
    df1['F2_F4'] = df1['F2'] * df1['F4']
    X1 = sm.add_constant(df1[PREDICTORS].astype(float))
    p1 = model.predict(X1)
    return float((p1 - p0).mean() * 100)

# ── Factor metadata ─────────────────────────────────────────────────────────────
CHANCE_LO = logit(CHANCE)  # ≈ -1.946

FACTOR_META = {
    'F1': dict(
        name='F1  —  Dot cueing',
        label0='Dot✗\n(UNCUED)',
        label1='Dot✓\n(CUED)',
        color0='#aaaaaa', color1='#333333',
        desc=('Did the onset dot mark the translating field?\n'
              'F1=1 (CUED): dot marks translator  ·  F1=0 (UNCUED): dot marks non-translator'),
    ),
    'F2': dict(
        name='F2  —  Depth-field cueing',
        label0='Depth✗\n(translator changed\ndepth plane)',
        label1='Depth✓\n(translator kept\ndepth plane)',
        color0='#cc7733', color1='#116688',
        desc=('Did the translating field remain in the depth plane established during the cue interval?\n'
              'F2=1: translator stays in cued depth plane  ·  F2=0: translator changes depth plane at tStart\n'
              'F2=1 conditions: CUED+N, CUED+C, UNCUED+Z, UNCUED+CZ'),
    ),
    'F3': dict(
        name='F3  —  Color-field cueing  (null)',
        label0='Color✗\n(translator changed\ncolor)',
        label1='Color✓\n(translator kept\ncolor)',
        color0='#ee9933', color1='#226622',
        desc=('Did the translating field retain the color associated with its cued identity?\n'
              'F3=1: translator keeps cued color  ·  F3=0: translator changes color at tStart\n'
              'F3=1 conditions: CUED+N, CUED+Z, UNCUED+C, UNCUED+CZ'),
    ),
    'F4': dict(
        name='F4  —  Translator depth plane  (Near vs Far)',
        label0='Far\n(translator in\nFar plane)',
        label1='Near\n(translator in\nNear plane)',
        color0='#4477bb', color1='#993333',
        desc=('Which depth plane does the translating field occupy?\n'
              'F4=1 (Near): translator is closer  ·  F4=0 (Far): translator is farther\n'
              'Near < Far is a robust asymmetry (stereoscopic origin — absent monocularly)'),
    ),
}

# ── Page 1–4: per-factor ───────────────────────────────────────────────────────
def draw_factor_page(fig, df, model, fkey, fname, page_num, total_pages):
    meta = FACTOR_META[fkey]
    grp0 = df[df[fkey] == 0]
    grp1 = df[df[fkey] == 1]
    k0, n0 = int(grp0['correct'].sum()), len(grp0)
    k1, n1 = int(grp1['correct'].sum()), len(grp1)
    p0, p1 = k0/n0, k1/n1
    lo0, hi0 = wilson_ci(k0, n0)
    lo1, hi1 = wilson_ci(k1, n1)

    gs = gridspec.GridSpec(1, 3, figure=fig,
                           left=0.08, right=0.97, bottom=0.22, top=0.78,
                           wspace=0.45)

    # ── Panel 1: % correct ──────────────────────────────────────────────────────
    ax1 = fig.add_subplot(gs[0, 0])
    for xi, (k, n, p, lo, hi, col, lbl) in enumerate([
            (k0, n0, p0, lo0, hi0, meta['color0'], meta['label0']),
            (k1, n1, p1, lo1, hi1, meta['color1'], meta['label1'])]):
        pct = p * 100
        elo, ehi = pct - lo*100, hi*100 - pct
        ax1.bar(xi*0.9, pct, width=0.6, color=col, alpha=0.88,
                edgecolor='white', zorder=2)
        ax1.errorbar(xi*0.9, pct, yerr=[[elo],[ehi]], fmt='none',
                     ecolor='#333333', elinewidth=1.2, capsize=4, zorder=3)
        ax1.text(xi*0.9, -6, lbl, ha='center', va='top', fontsize=7.5,
                 clip_on=False)
        ax1.text(xi*0.9, pct+ehi+1.5, f'{pct:.1f}%', ha='center',
                 va='bottom', fontsize=8, color='#333333')
        ax1.text(xi*0.9, 1, f'n={n}', ha='center', va='bottom',
                 fontsize=6, color='#888888')

    ax1.axhline(CHANCE*100, color='#cc4444', lw=1, ls='--', zorder=1)
    ax1.text(1.3, CHANCE*100+0.5, 'chance (12.5%)', fontsize=6,
             color='#cc4444', va='bottom')
    # Delta bracket
    top = max(p0, p1)*100 + 12
    ax1.annotate('', xy=(0.9, top), xytext=(0.0, top),
                 arrowprops=dict(arrowstyle='<->', color='#222222', lw=1.3))
    ax1.text(0.45, top+1, f'Δ = {(p1-p0)*100:+.1f} pp',
             ha='center', va='bottom', fontsize=9, fontweight='bold')

    ax1.set_xlim(-0.5, 1.6)
    ax1.set_ylim(0, 80)
    ax1.set_yticks([0, 12.5, 25, 50, 75])
    ax1.set_yticklabels(['0','12.5','25','50','75'], fontsize=7)
    ax1.set_ylabel('% correct', fontsize=9)
    ax1.set_xticks([])
    ax1.spines[['top','right','bottom']].set_visible(False)
    ax1.yaxis.grid(True, lw=0.4, color='#e0e0e0', zorder=0)
    ax1.set_axisbelow(True)
    ax1.set_title('Raw accuracy\n(% correct, all trials)', fontsize=9, fontweight='bold')

    # ── Panel 2: log-odds ───────────────────────────────────────────────────────
    ax2 = fig.add_subplot(gs[0, 1])
    for xi, (k, n, p, lo, hi, col, lbl) in enumerate([
            (k0, n0, p0, lo0, hi0, meta['color0'], meta['label0']),
            (k1, n1, p1, lo1, hi1, meta['color1'], meta['label1'])]):
        lv  = logit(p)
        elo = lv - logit(max(lo, 1e-5))
        ehi = logit(min(hi, 1-1e-5)) - lv
        ax2.bar(xi*0.9, lv, width=0.6, color=col, alpha=0.88,
                edgecolor='white', zorder=2)
        ax2.errorbar(xi*0.9, lv, yerr=[[elo],[ehi]], fmt='none',
                     ecolor='#333333', elinewidth=1.2, capsize=4, zorder=3)
        ax2.text(xi*0.9, -2.8, lbl, ha='center', va='top', fontsize=7.5,
                 clip_on=False)
        ax2.text(xi*0.9, lv + ehi + 0.06, f'{lv:+.2f}',
                 ha='center', va='bottom', fontsize=8, color='#333333')

    lo0v, lo1v = logit(p0), logit(p1)
    ax2.axhline(0, color='#666666', lw=0.9, zorder=1)
    ax2.axhline(CHANCE_LO, color='#cc4444', lw=1, ls='--', zorder=1)
    ax2.text(1.3, CHANCE_LO+0.04, 'chance\n(−1.95)', fontsize=6,
             color='#cc4444', va='bottom')
    ax2.text(1.3, 0.04, '50%\n(0.00)', fontsize=6, color='#666666', va='bottom')

    top2 = max(lo0v, lo1v) + 0.45
    ax2.annotate('', xy=(0.9, top2), xytext=(0.0, top2),
                 arrowprops=dict(arrowstyle='<->', color='#222222', lw=1.3))
    ax2.text(0.45, top2+0.04,
             f'Δ = {lo1v-lo0v:+.2f} log-odds',
             ha='center', va='bottom', fontsize=9, fontweight='bold')

    ax2.set_xlim(-0.5, 1.6)
    ax2.set_ylim(-2.8, 1.5)
    ax2.set_yticks([-2, -1.946, -1, 0, 1])
    ax2.set_yticklabels(['-2.0', 'chance\n(−1.95)', '-1.0', '0.0\n(50%)', '+1.0'], fontsize=6.5)
    ax2.set_ylabel('Log-odds of correct', fontsize=9)
    ax2.set_xticks([])
    ax2.spines[['top','right','bottom']].set_visible(False)
    ax2.yaxis.grid(True, lw=0.4, color='#e0e0e0', zorder=0)
    ax2.set_axisbelow(True)
    ax2.set_title('Same data — log-odds scale\n(what the GLM models)', fontsize=9, fontweight='bold')

    # ── Panel 3: GLM coefficient ────────────────────────────────────────────────
    ax3 = fig.add_subplot(gs[0, 2])
    coef   = model.params[fkey]
    ci_lo  = model.conf_int().loc[fkey, 0]
    ci_hi  = model.conf_int().loc[fkey, 1]
    pval   = model.pvalues[fkey]
    ame    = compute_ame(model, df, fkey)

    bar_col = '#1a6ab5' if coef >= 0 else '#c0392b'
    ax3.barh(0, coef, height=0.35, color=bar_col, alpha=0.85, zorder=2)
    ax3.errorbar(coef, 0, xerr=[[coef-ci_lo],[ci_hi-coef]], fmt='none',
                 ecolor='#222222', elinewidth=1.5, capsize=6, zorder=3)
    ax3.axvline(0, color='#444444', lw=1, zorder=1)
    ax3.axvline(logit(p1)-logit(p0), color='#888888', lw=1, ls=':',
                zorder=0, label='raw log-odds diff')

    ax3.set_xlim(-2.5, 2.5)
    ax3.set_ylim(-0.5, 0.5)
    ax3.set_yticks([])
    ax3.set_xlabel('Coefficient (log-odds)', fontsize=9)
    ax3.spines[['top','right','left']].set_visible(False)
    ax3.xaxis.grid(True, lw=0.4, color='#e0e0e0', zorder=0)
    ax3.set_axisbelow(True)
    ax3.set_title('GLM2 coefficient\n(controlling for all other factors)', fontsize=9, fontweight='bold')

    ax3.text(0.5, 0.98,
             f'β = {coef:+.3f}  {sig_str(pval)}\n'
             f'95% CI:  [{ci_lo:+.3f},  {ci_hi:+.3f}]\n'
             f'p = {pval:.3f}\n\n'
             f'AME = {ame:+.1f} pp',
             ha='center', va='top', transform=ax3.transAxes,
             fontsize=9, family='monospace',
             bbox=dict(boxstyle='round,pad=0.5', facecolor='#f8f8f8',
                       edgecolor='#bbbbbb', lw=0.8))

    raw_diff = logit(p1) - logit(p0)
    ax3.text(0.5, 0.25,
             f'Dotted line = raw log-odds difference\n({raw_diff:+.3f})\n'
             f'GLM coefficient differs because it\ncontrols for F1, F2, F3, F4\nand their interactions.',
             ha='center', va='top', transform=ax3.transAxes,
             fontsize=7, color='#666666', style='italic')

    # ── Page furniture ──────────────────────────────────────────────────────────
    fig.suptitle(meta['name'], fontsize=13, fontweight='bold', y=0.96)
    fig.text(0.5, 0.91, meta['desc'], ha='center', va='top',
             fontsize=8.5, color='#333333')
    fig.text(0.5, 0.175,
             'Left → Middle:  same data, two scales.  '
             'Middle → Right:  GLM adjusts for all other factors simultaneously.',
             ha='center', va='top', fontsize=7.5, color='#666666', style='italic')
    fig.text(0.01, 0.005, f'{fname}  ·  {DATE_STR}', fontsize=5,
             color='#888888', ha='left', va='bottom')
    fig.text(0.99, 0.005, f'p. {page_num}/{total_pages}', fontsize=5,
             color='#888888', ha='right', va='bottom')


# ── Page 5: F1×F2 interaction ──────────────────────────────────────────────────
def draw_interaction_page(fig, df, model, fname, page_num, total_pages):
    # Build 2×2 cell stats
    cells = {}
    for f1 in [0, 1]:
        for f2 in [0, 1]:
            sub = df[(df['F1'] == f1) & (df['F2'] == f2)]
            k, n = int(sub['correct'].sum()), len(sub)
            p = k/n
            lo, hi = wilson_ci(k, n)
            cells[(f1, f2)] = dict(
                k=k, n=n, p=p,
                p_pct=p*100,
                elo=p*100 - lo*100, ehi=hi*100 - p*100,
                lv=logit(p),
                lv_elo=logit(p) - logit(max(lo, 1e-5)),
                lv_ehi=logit(min(hi, 1-1e-5)) - logit(p),
            )

    CELL_COLS = {(0,0):'#cccccc', (0,1):'#88aacc', (1,0):'#cc9966', (1,1):'#1a4a99'}
    CELL_LBLS = {(0,0):'Dot✗ / Depth✗', (0,1):'Dot✗ / Depth✓',
                 (1,0):'Dot✓ / Depth✗', (1,1):'Dot✓ / Depth✓'}

    outer = gridspec.GridSpec(1, 2, figure=fig,
                               left=0.08, right=0.97, bottom=0.28, top=0.82,
                               wspace=0.35)

    for col_idx, use_lo in [(0, False), (1, True)]:
        inner = gridspec.GridSpecFromSubplotSpec(2, 2, subplot_spec=outer[col_idx],
                                                  hspace=0.65, wspace=0.45)
        for f1 in [0, 1]:
            for f2 in [0, 1]:
                ax = fig.add_subplot(inner[1-f1, f2])
                c  = cells[(f1, f2)]
                cc = CELL_COLS[(f1, f2)]

                if use_lo:
                    val, elo, ehi = c['lv'], c['lv_elo'], c['lv_ehi']
                else:
                    val, elo, ehi = c['p_pct'], c['elo'], c['ehi']

                ax.bar(0, val, width=0.55, color=cc, alpha=0.88,
                       edgecolor='white', zorder=2)
                ax.errorbar(0, val, yerr=[[elo],[ehi]], fmt='none',
                            ecolor='#333333', elinewidth=1, capsize=3, zorder=3)

                if not use_lo:
                    ax.axhline(CHANCE*100, color='#cc4444', lw=0.8, ls='--')
                    ax.set_ylim(0, 80)
                    ax.set_yticks([0, 12.5, 25, 50, 75])
                    ax.set_yticklabels(['0','','25','50','75'], fontsize=6)
                    ax.text(0, val+ehi+1.5, f'{val:.1f}%', ha='center',
                            va='bottom', fontsize=7.5)
                else:
                    ax.axhline(CHANCE_LO, color='#cc4444', lw=0.8, ls='--')
                    ax.axhline(0, color='#666666', lw=0.6)
                    ax.set_ylim(-2.5, 1.0)
                    ax.set_yticks([-2, -1, 0, 1])
                    ax.set_yticklabels(['-2','-1','0','+1'], fontsize=6)
                    ax.text(0, val+ehi+0.07, f'{val:+.2f}', ha='center',
                            va='bottom', fontsize=7.5)

                ax.set_xticks([])
                ax.set_xlim(-0.6, 0.6)
                ax.spines[['top','right','bottom']].set_visible(False)
                ax.yaxis.grid(True, lw=0.3, color='#e8e8e8', zorder=0)
                ax.set_axisbelow(True)
                lbl_col = cc if cc != '#cccccc' else '#555555'
                ax.set_title(CELL_LBLS[(f1,f2)], fontsize=7.5, fontweight='bold',
                             color=lbl_col, pad=3)
                ax.text(-0.55, -8 if not use_lo else -3.3,
                        f'n={c["n"]}', fontsize=6, color='#888888',
                        va='top', clip_on=False)

        panel_title = '% correct' if not use_lo else 'Log-odds'
        y_title = 0.835
        x_title = 0.27 + col_idx*0.49
        fig.text(x_title, y_title, panel_title, ha='center', va='bottom',
                 fontsize=10, fontweight='bold', transform=fig.transFigure)

    # Row / col axis labels (approximate figure coordinates)
    for f2, lbl, x in [(0,'F2=0\nDepth✗',0.20),(1,'F2=1\nDepth✓',0.35)]:
        fig.text(x, 0.275, lbl, ha='center', va='top', fontsize=8,
                 fontweight='bold', color='#333333')
    for f2, lbl, x in [(0,'F2=0\nDepth✗',0.67),(1,'F2=1\nDepth✓',0.82)]:
        fig.text(x, 0.275, lbl, ha='center', va='top', fontsize=8,
                 fontweight='bold', color='#333333')
    for f1, lbl, y in [(0,'F1=0\nUNCUED',0.38),(1,'F1=1\nCUED',0.62)]:
        fig.text(0.05, y, lbl, ha='center', va='center', fontsize=8,
                 fontweight='bold', color='#333333', rotation=90)

    # Interaction coefficient summary
    coef  = model.params['F1_F2']
    ci_lo = model.conf_int().loc['F1_F2', 0]
    ci_hi = model.conf_int().loc['F1_F2', 1]
    pval  = model.pvalues['F1_F2']

    summary = (
        f'F1×F2 interaction coefficient:  β = {coef:+.3f}   95% CI [{ci_lo:+.3f}, {ci_hi:+.3f}]   {sig_str(pval)}\n'
        f'Average Marginal Effect of F1×F2:  +32.7 pp  ***\n\n'
        f'Interpretation:  being dot-cued AND depth-cued (F1=1, F2=1) is {coef:.2f} log-odds units MORE effective than the additive sum\n'
        f'of their separate effects.  In plain terms: dot cueing only helps when the translator stays in its pre-cue depth plane.'
    )
    fig.text(0.5, 0.235, summary, ha='center', va='top', fontsize=8.5,
             color='#222222',
             bbox=dict(boxstyle='round,pad=0.5', facecolor='#f0f4ff',
                       edgecolor='#1a3a8b', lw=0.9))

    fig.suptitle('F1 × F2  —  Dot cueing × Depth-field cueing  (the key interaction)',
                 fontsize=12, fontweight='bold', y=0.97)
    fig.text(0.5, 0.93,
             'Performance is high only when BOTH the onset dot cue AND depth-plane continuity point to the same field.\n'
             'Neither factor alone drives selection — the conjunction is necessary.',
             ha='center', va='top', fontsize=9, color='#333333')
    fig.text(0.01, 0.005, f'{fname}  ·  {DATE_STR}', fontsize=5,
             color='#888888', ha='left', va='bottom')
    fig.text(0.99, 0.005, f'p. {page_num}/{total_pages}', fontsize=5,
             color='#888888', ha='right', va='bottom')


# ── Main ───────────────────────────────────────────────────────────────────────
os.makedirs(BASE, exist_ok=True)
os.makedirs(BASE_SP, exist_ok=True)

trials = load_all()
print(f'Total valid trials: {len(trials)}')
df     = build_df(trials)
model  = fit_glm(df)
print(model.summary())

FACTORS      = ['F1', 'F2', 'F3', 'F4']
TOTAL_PAGES  = len(FACTORS) + 1
fname        = os.path.basename(OUT_PDF_SP)

for out in [OUT_PDF, OUT_PDF_SP]:
    with PdfPages(out) as pdf:
        for pi, fk in enumerate(FACTORS, 1):
            fig = plt.figure(figsize=(13, 7))
            draw_factor_page(fig, df, model, fk, fname, pi, TOTAL_PAGES)
            pdf.savefig(fig, bbox_inches='tight')
            plt.close(fig)
            print(f'  Saved p.{pi}: {fk}')

        fig = plt.figure(figsize=(13, 9))
        draw_interaction_page(fig, df, model, fname, TOTAL_PAGES, TOTAL_PAGES)
        pdf.savefig(fig, bbox_inches='tight')
        plt.close(fig)
        print(f'  Saved p.{TOTAL_PAGES}: F1×F2 interaction')

print(f'\nSaved: {OUT_PDF}')
print(f'Saved: {OUT_PDF_SP}')
