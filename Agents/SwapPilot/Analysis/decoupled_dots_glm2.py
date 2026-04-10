#!/usr/bin/env python3
"""
decoupled_dots_glm2.py
-----------------------
Logistic regression predicting trial-level accuracy from 4 factors + 3 interactions.

  correct ~ F1 + F2 + F3 + F4 + F1:F2 + F1:F4 + F2:F4

  F1: Dot cueing         1 = CUED (Field B is translator),  0 = UNCUED
  F2: Depth-field cued   1 = translator depth matches delayed-field onset depth
                         (Depth✓: CUED+N, CUED+C, UNCUED+Z, UNCUED+CZ)
  F3: Color-field cued   1 = translator color matches delayed-field onset color
                         (Color✓: CUED+N, CUED+Z, UNCUED+C, UNCUED+CZ)
  F4: Translator Near    1 = Near plane,  0 = Far plane
                         (expect negative coefficient: Near < Far)

Interaction terms:
  F1:F2  Dot × Depth cueing  — prior residual evidence for negative interaction
  F1:F4  Dot × Translator depth
  F2:F4  Depth cueing × Translator depth

Output:
  Console  — full statsmodels Logit summary + average marginal effects table
  PDF      — forest plot: log-odds coefficients (left) and AMEs in pp (right)
             Agents/Figures/decoupled_dots_glm2.pdf
"""

import csv, math, os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

try:
    import statsmodels.api as sm
except ImportError:
    raise ImportError("statsmodels required: pip install statsmodels")

# ── Paths ──────────────────────────────────────────────────────────────────────
SESSIONS = [
    ("/tmp/quest_pull2/files/vr_dots_session_260406_1532.tsv", False),
    ("/tmp/quest_pull2/files/vr_dots_session_260406_1754.tsv", True),
    ("/tmp/quest_pull3/files/vr_dots_session_260407_0643.tsv", True),
    ("/tmp/quest_pull3/files/vr_dots_session_260407_0731.tsv", False),
]
BASE    = os.path.normpath(os.path.join(os.path.dirname(__file__), '../../Agents/Figures'))
OUT_PDF = os.path.join(BASE, 'decoupled_dots_glm2.pdf')

# ── Data loading ───────────────────────────────────────────────────────────────
def is_correct(td, rd):
    d = (float(rd) - float(td) + 360) % 360
    return (360 - d if d > 180 else d) <= 22.5

def load_all():
    trials = []
    for path, is_inv in SESSIONS:
        with open(path, newline='') as f:
            for r in csv.DictReader(f, delimiter='\t'):
                if (not r.get('TransDeg', '').strip() or
                        not r.get('RespDeg', '').strip() or
                        r.get('EndKey', '') in ('timeout', 'skip', 'requeue')):
                    continue
                cond = r['Cond']
                if is_inv:
                    cond = 'UNCUED' if cond == 'CUED' else 'CUED'
                b_green = (r['DelayedFieldColor'] == 'G') ^ is_inv
                b_near  = (r['DelayedFieldDepth']  == 'N') ^ is_inv
                trials.append(dict(
                    swap    = r['SwapType'],
                    cond    = cond,
                    b_green = b_green,
                    b_near  = b_near,
                    correct = int(is_correct(r['TransDeg'], r['RespDeg'])),
                ))
    return trials

# ── Design matrix ──────────────────────────────────────────────────────────────
def build_dataframe(trials):
    rows = []
    for t in trials:
        cond  = t['cond']
        swap  = t['swap']
        bn    = t['b_near']

        F1 = 1 if cond == 'CUED' else 0

        F2 = int((cond == 'CUED'   and swap in ('N', 'C')) or
                 (cond == 'UNCUED' and swap in ('Z', 'CZ')))

        F3 = int((cond == 'CUED'   and swap in ('N', 'Z')) or
                 (cond == 'UNCUED' and swap in ('C', 'CZ')))

        # Translator depth: CUED → B translates (b_near); UNCUED → A translates (!b_near)
        trans_near = bn if cond == 'CUED' else not bn
        F4 = 1 if trans_near else 0   # 1=Near, expect negative coeff

        rows.append(dict(F1=F1, F2=F2, F3=F3, F4=F4, correct=t['correct']))

    df = pd.DataFrame(rows)
    df['F1_F2'] = df['F1'] * df['F2']
    df['F1_F4'] = df['F1'] * df['F4']
    df['F2_F4'] = df['F2'] * df['F4']
    return df

# ── Fit model ──────────────────────────────────────────────────────────────────
def fit_model(df):
    predictors = ['F1', 'F2', 'F3', 'F4', 'F1_F2', 'F1_F4', 'F2_F4']
    X = sm.add_constant(df[predictors].astype(float))
    y = df['correct'].astype(float)
    model = sm.Logit(y, X).fit(disp=False)
    return model, predictors

# ── Figure ─────────────────────────────────────────────────────────────────────
TERM_LABELS = {
    'const': 'Intercept',
    'F1':    'F1  Dot cueing',
    'F2':    'F2  Depth-field cued',
    'F3':    'F3  Color-field cued',
    'F4':    'F4  Translator Near',
    'F1_F2': 'F1 × F2  Dot × Depth',
    'F1_F4': 'F1 × F4  Dot × Trans-depth',
    'F2_F4': 'F2 × F4  Depth × Trans-depth',
}

def pval_str(p):
    if p < 0.001: return '***'
    if p < 0.01:  return '**'
    if p < 0.05:  return '*'
    return 'n.s.'

def coef_color(coef, pval):
    if pval >= 0.05:   return '#999999'
    return '#1a6ab5' if coef > 0 else '#c0392b'

def build_figure(model, ame_result, figsize=(11, 6)):
    terms    = list(model.params.index)
    coefs    = model.params.values
    cis      = model.conf_int().values       # shape (n, 2)
    pvals    = model.pvalues.values

    # AME values (skip intercept — not in AME output)
    ame_params = ame_result.margeff
    ame_se     = ame_result.margeff_se
    ame_pvals  = ame_result.pvalues
    ame_terms  = list(ame_result.summary_frame().index)

    fig, (ax_logit, ax_ame) = plt.subplots(1, 2, figsize=figsize)
    fig.suptitle(
        'Exp_DecoupledDots_005m  ·  Logistic GLM  ·  '
        'correct ~ F1+F2+F3+F4+F1:F2+F1:F4+F2:F4  ·  n=2051 trials',
        fontsize=9, fontweight='bold', y=1.01)

    # ── Left panel: log-odds coefficients ─────────────────────────────────────
    n = len(terms)
    y_pos = np.arange(n)
    for i, (term, coef, ci, pv) in enumerate(zip(terms, coefs, cis, pvals)):
        col = coef_color(coef, pv)
        ax_logit.barh(i, coef, color=col, alpha=0.75, height=0.55, zorder=2)
        ax_logit.errorbar(coef, i,
                          xerr=[[coef - ci[0]], [ci[1] - coef]],
                          fmt='none', ecolor='#333333', elinewidth=1,
                          capsize=3, zorder=3)
        label = TERM_LABELS.get(term, term)
        ax_logit.text(-0.02, i, label, ha='right', va='center',
                      fontsize=7.5, transform=ax_logit.get_yaxis_transform())
        ax_logit.text(ci[1] + 0.02, i,
                      f'{coef:+.3f}  {pval_str(pv)}',
                      ha='left', va='center', fontsize=6.5, color=col)

    ax_logit.axvline(0, color='#333333', lw=0.8, ls='--')
    ax_logit.set_yticks([])
    ax_logit.set_xlabel('Log-odds coefficient  (95% CI)', fontsize=8)
    ax_logit.set_title('Log-odds scale', fontsize=9, fontweight='bold')
    ax_logit.spines[['top', 'right', 'left']].set_visible(False)
    ax_logit.yaxis.grid(False)
    ax_logit.set_ylim(-0.7, n - 0.3)

    # ── Right panel: average marginal effects in pp ────────────────────────────
    n_ame = len(ame_terms)
    z95 = 1.96
    for i, (term, ame, se, pv) in enumerate(
            zip(ame_terms, ame_params, ame_se, ame_pvals)):
        col = coef_color(ame, pv)
        ame_pp = ame * 100
        se_pp  = se  * 100
        ax_ame.barh(i, ame_pp, color=col, alpha=0.75, height=0.55, zorder=2)
        ax_ame.errorbar(ame_pp, i,
                        xerr=[[z95*se_pp], [z95*se_pp]],
                        fmt='none', ecolor='#333333', elinewidth=1,
                        capsize=3, zorder=3)
        label = TERM_LABELS.get(term, term)
        ax_ame.text(-0.2, i, label, ha='right', va='center',
                    fontsize=7.5, transform=ax_ame.get_yaxis_transform())
        ax_ame.text(ame_pp + (z95*se_pp) + 0.3, i,
                    f'{ame_pp:+.1f} pp  {pval_str(pv)}',
                    ha='left', va='center', fontsize=6.5, color=col)

    ax_ame.axvline(0, color='#333333', lw=0.8, ls='--')
    ax_ame.set_yticks([])
    ax_ame.set_xlabel('Average marginal effect  (pp, ±95% CI)', fontsize=8)
    ax_ame.set_title('Probability scale (pp)', fontsize=9, fontweight='bold')
    ax_ame.spines[['top', 'right', 'left']].set_visible(False)
    ax_ame.set_ylim(-0.7, n_ame - 0.3)

    # Shared legend
    from matplotlib.patches import Patch
    handles = [
        Patch(facecolor='#1a6ab5', alpha=0.75, label='Positive, p<0.05'),
        Patch(facecolor='#c0392b', alpha=0.75, label='Negative, p<0.05'),
        Patch(facecolor='#999999', alpha=0.75, label='n.s. (p≥0.05)'),
    ]
    fig.legend(handles=handles, loc='lower center', ncol=3,
               fontsize=7, bbox_to_anchor=(0.5, -0.04), framealpha=0.9)

    fig.subplots_adjust(left=0.28, right=0.97, bottom=0.12, top=0.92, wspace=0.55)
    return fig

# ── Predicted vs Observed figure ───────────────────────────────────────────────
COND_ORDER = [
    ('CUED',   'N',  '#2255aa', 'o',  'CUED+N'),
    ('CUED',   'C',  '#2255aa', 's',  'CUED+C'),
    ('CUED',   'Z',  '#c0392b', 'o',  'CUED+Z'),
    ('CUED',   'CZ', '#c0392b', 's',  'CUED+CZ'),
    ('UNCUED', 'N',  '#7799cc', '^',  'UNCUED+N'),
    ('UNCUED', 'C',  '#7799cc', 'D',  'UNCUED+C'),
    ('UNCUED', 'Z',  '#e08080', '^',  'UNCUED+Z'),
    ('UNCUED', 'CZ', '#e08080', 'D',  'UNCUED+CZ'),
]

def build_pred_obs_figure(df, model, figsize=(8, 7)):
    # Attach fitted probabilities to df
    df = df.copy()
    df['_pred'] = model.predict()

    # Also reconstruct (cond, swap) from F1/F2/F3 for each trial
    # F1=cond, swap determined by F2+F3 combination:
    #   F2=1,F3=1 → N;  F2=1,F3=0 → C;  F2=0,F3=1 → Z;  F2=0,F3=0 → CZ
    # (for CUED; for UNCUED the mapping is inverted — but F2/F3 encode
    #  the cueing alignment, so the swap label needs the original cond)
    # Easier: re-join from the original trials list via index
    # We stored swap in build_dataframe so re-add it here
    df['_cond'] = df['F1'].map({1: 'CUED', 0: 'UNCUED'})
    # Recover swap from F2/F3 (valid for CUED; for UNCUED the F2/F3
    # definitions flip but the (F2,F3) pair still uniquely identifies swap)
    swap_from_f2f3 = {
        (1, 1): ('CUED', 'N'),   (1, 0): ('CUED', 'C'),
        (0, 1): ('CUED', 'Z'),   (0, 0): ('CUED', 'CZ'),
    }
    # For UNCUED the (F2,F3) → swap mapping is different:
    #   UNCUED+N  → F2=0,F3=0;  UNCUED+C  → F2=0,F3=1
    #   UNCUED+Z  → F2=1,F3=0;  UNCUED+CZ → F2=1,F3=1
    swap_uncued = {(0,0):'N', (0,1):'C', (1,0):'Z', (1,1):'CZ'}
    swap_cued   = {(1,1):'N', (1,0):'C', (0,1):'Z', (0,0):'CZ'}

    def get_swap(row):
        k = (int(row['F2']), int(row['F3']))
        return swap_cued[k] if row['F1'] == 1 else swap_uncued[k]

    df['_swap'] = df.apply(get_swap, axis=1)

    # Aggregate by (cond, swap)
    grp = df.groupby(['_cond', '_swap'])
    obs  = grp['correct'].mean() * 100
    pred = grp['_pred'].mean()   * 100
    n    = grp['correct'].count()

    # Wilson CI for observed
    def wci(k_frac, n_):
        k = round(k_frac * n_ / 100)
        if n_ == 0: return 0, 0
        p = k / n_; z = 1.96; d = 1 + z**2/n_
        c = (p + z**2/(2*n_)) / d
        hw = z * math.sqrt(p*(1-p)/n_ + z**2/(4*n_**2)) / d
        return (p - (c - hw)) * 100, ((c + hw) - p) * 100

    # ── Figure ────────────────────────────────────────────────────────────────
    fig, (ax_sc, ax_bar) = plt.subplots(1, 2, figsize=figsize)
    fig.suptitle(
        'GLM2 — Predicted vs Observed  ·  Exp_DecoupledDots_005m  ·  n=2051',
        fontsize=10, fontweight='bold', y=1.01)

    # Left: scatter observed (x) vs predicted (y)
    for cond, swap, col, mk, lbl in COND_ORDER:
        key = (cond, swap)
        if key not in obs.index: continue
        o = obs[key]; p_ = pred[key]; n_ = n[key]
        elo, ehi = wci(o, n_)
        ax_sc.errorbar(o, p_, xerr=[[elo],[ehi]],
                       fmt=mk, color=col, ms=8, mec='white', mew=0.6,
                       ecolor=col, elinewidth=1, capsize=3, zorder=3,
                       label=lbl)
        # Offset label slightly
        ax_sc.annotate(swap, (o, p_), textcoords='offset points',
                       xytext=(5, 3), fontsize=7, color=col)

    lo, hi = 10, 65
    ax_sc.plot([lo, hi], [lo, hi], '--', color='#888888', lw=0.9, zorder=1,
               label='Perfect fit')
    ax_sc.set_xlim(lo, hi); ax_sc.set_ylim(lo, hi)
    ax_sc.set_xlabel('Observed % correct', fontsize=9)
    ax_sc.set_ylabel('Predicted % correct  (model)', fontsize=9)
    ax_sc.set_title('Predicted vs Observed', fontsize=9, fontweight='bold')
    ax_sc.spines[['top','right']].set_visible(False)
    ax_sc.yaxis.grid(True, lw=0.4, color='#e0e0e0', zorder=0)
    ax_sc.xaxis.grid(True, lw=0.4, color='#e0e0e0', zorder=0)
    ax_sc.set_axisbelow(True)
    ax_sc.legend(fontsize=6.5, loc='upper left', framealpha=0.9)

    # Right: side-by-side observed & predicted bars per condition
    xs = np.arange(len(COND_ORDER))
    bw = 0.35
    for i, (cond, swap, col, mk, lbl) in enumerate(COND_ORDER):
        key = (cond, swap)
        if key not in obs.index: continue
        o = obs[key]; p_ = pred[key]; n_ = n[key]
        elo, ehi = wci(o, n_)
        ax_bar.bar(xs[i] - bw/2, o,  width=bw, color=col, alpha=0.85,
                   zorder=2, label='Observed' if i == 0 else '')
        ax_bar.bar(xs[i] + bw/2, p_, width=bw, color=col, alpha=0.35,
                   zorder=2, hatch='///',
                   label='Predicted' if i == 0 else '')
        ax_bar.errorbar(xs[i] - bw/2, o, yerr=[[elo],[ehi]],
                        fmt='none', ecolor='#333', elinewidth=0.9,
                        capsize=2.5, zorder=3)

    ax_bar.axhline(100/8, color='#cc4444', lw=0.9, ls='--', zorder=1,
                   label='Chance (12.5%)')
    ax_bar.set_xticks(xs)
    ax_bar.set_xticklabels([lbl for *_, lbl in COND_ORDER],
                           rotation=40, ha='right', fontsize=7)
    ax_bar.set_ylim(0, 75)
    ax_bar.set_yticks([0, 12.5, 25, 50, 75])
    ax_bar.set_yticklabels(['0','12.5','25','50','75'], fontsize=7)
    ax_bar.set_ylabel('% correct', fontsize=9)
    ax_bar.set_title('Observed (solid) vs Predicted (hatched)', fontsize=9, fontweight='bold')
    ax_bar.spines[['top','right']].set_visible(False)
    ax_bar.yaxis.grid(True, lw=0.4, color='#e0e0e0', zorder=0)
    ax_bar.set_axisbelow(True)

    from matplotlib.patches import Patch
    leg_handles = [
        Patch(facecolor='#555555', alpha=0.85, label='Observed'),
        Patch(facecolor='#555555', alpha=0.35, hatch='///', label='Predicted (model)'),
        Patch(facecolor='#2255aa', label='CUED (blue tones)'),
        Patch(facecolor='#c0392b', label='CUED+depth-swap (red tones)'),
        Patch(facecolor='#7799cc', label='UNCUED (blue tones)'),
        Patch(facecolor='#e08080', label='UNCUED+depth-swap (red tones)'),
    ]
    fig.legend(handles=leg_handles, loc='lower center', ncol=3,
               fontsize=7, bbox_to_anchor=(0.5, -0.06), framealpha=0.9)

    fig.subplots_adjust(left=0.10, right=0.97, bottom=0.28, top=0.93, wspace=0.38)
    return fig


# ── Main ───────────────────────────────────────────────────────────────────────
os.makedirs(BASE, exist_ok=True)
trials = load_all()
print(f'Total valid trials: {len(trials)}')

df = build_dataframe(trials)
print(f'\nFactor means (should be ~0.5 each):')
for col in ['F1','F2','F3','F4']:
    print(f'  {col}: {df[col].mean():.4f}')

model, predictors = fit_model(df)
print('\n' + '='*70)
print(model.summary())

print('\n' + '='*70)
print('Average Marginal Effects:')
ame = model.get_margeff()
print(ame.summary())

fig = build_figure(model, ame)
fig2 = build_pred_obs_figure(df, model)
with PdfPages(OUT_PDF) as pdf:
    pdf.savefig(fig,  bbox_inches='tight')
    pdf.savefig(fig2, bbox_inches='tight')
plt.close(fig)
plt.close(fig2)
print(f'\nSaved: {OUT_PDF}')
