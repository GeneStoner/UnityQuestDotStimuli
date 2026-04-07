#!/usr/bin/env python3
"""
GLM (logistic regression) predicting performance from three additive factors:
  1. Dot cueing     (CUED=1, UNCUED=0)
  2. Depth-field cueing (translator ends in same depth plane as delayed field's first appearance)
  3. Color-field cueing (translator color matches delayed field's original color)

Design is fully orthogonal — each combination of the three binary predictors
maps onto exactly 2 of the 8 (Cond × SwapType) cells, all with equal n.

Models:
  (a) Logistic regression  — trial-level GLM, binomial family (primary)
  (b) Linear probability model (OLS on binary outcome) — coefficients in pp

Sessions:
  260406_1532  DecoupledDots_005m       (delayTranslator=1, labels normal)
  260406_1754  DecoupledDots_Inv_005m   (delayTranslator=0, labels INVERTED)

Output: Agents/Figures/decoupled_dots_glm.png
        prints full model summary to stdout
"""

import csv, math, os
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

DATA_S1 = "/tmp/quest_pull2/files/vr_dots_session_260406_1532.tsv"
DATA_S2 = "/tmp/quest_pull2/files/vr_dots_session_260406_1754.tsv"
OUT     = os.path.expanduser(
    "~/Projects/ObjectBasedAttention/VRDots/Agents/Figures/decoupled_dots_glm.png")

CHANCE = 1/8

DEPTH_FIELD_CUED = {
    'CUED':   {'N': 1, 'C': 1, 'Z': 0, 'CZ': 0},
    'UNCUED': {'N': 0, 'C': 0, 'Z': 1, 'CZ': 1},
}
COLOR_FIELD_CUED = {
    'CUED':   {'N': 1, 'C': 0, 'Z': 1, 'CZ': 0},
    'UNCUED': {'N': 0, 'C': 1, 'Z': 0, 'CZ': 1},
}

# ── Load data ──────────────────────────────────────────────────────────────────
def is_correct(td, rd):
    d = (float(rd) - float(td) + 360) % 360
    return int((360 - d if d > 180 else d) <= 22.5)

def load(path, invert=False):
    with open(path, newline='') as f:
        rows = list(csv.DictReader(f, delimiter='\t'))
    valid = []
    for r in rows:
        if not r.get('TransDeg','').strip() or not r.get('RespDeg','').strip():
            continue
        if r.get('EndKey','') in ('timeout','skip','requeue'):
            continue
        cond = r['Cond']
        if invert:
            cond = 'UNCUED' if cond == 'CUED' else 'CUED'
        swap = r['SwapType']
        if cond not in ('CUED','UNCUED') or swap not in ('N','C','Z','CZ'):
            continue
        valid.append({
            'correct':    is_correct(r['TransDeg'], r['RespDeg']),
            'dot_cue':    1 if cond == 'CUED' else 0,
            'depth_cue':  DEPTH_FIELD_CUED[cond][swap],
            'color_cue':  COLOR_FIELD_CUED[cond][swap],
            'cond':       cond,
            'swap':       swap,
        })
    return valid

trials = load(DATA_S1, invert=False) + load(DATA_S2, invert=True)
df = pd.DataFrame(trials)
print(f"Total trials: {len(df)}   Correct: {df.correct.sum()}   "
      f"Overall accuracy: {df.correct.mean()*100:.1f}%")

# ── Check orthogonality ────────────────────────────────────────────────────────
print("\n── Factor balance (n per cell) ──────────────────────────────────────")
print(df.groupby(['dot_cue','depth_cue','color_cue'])['correct'].agg(['sum','count'])
        .rename(columns={'sum':'k','count':'n'}))

# ── (a) Logistic regression ────────────────────────────────────────────────────
logit_model = smf.logit('correct ~ dot_cue + depth_cue + color_cue', data=df).fit()
print("\n" + "="*70)
print("  LOGISTIC REGRESSION (GLM, binomial)")
print("="*70)
print(logit_model.summary2())

# McFadden R²
ll_null  = logit_model.llnull
ll_model = logit_model.llf
mcfadden = 1 - ll_model / ll_null
print(f"\n  McFadden R²  = {mcfadden:.4f}")
print(f"  Log-Lik null = {ll_null:.2f}   model = {ll_model:.2f}")
print(f"  LRT χ²({logit_model.df_model:.0f})  = {-2*(ll_null-ll_model):.2f}   "
      f"p = {logit_model.llr_pvalue:.6f}")

# Odds ratios
print("\n  Odds Ratios (exp(coef)):")
for name, coef, ci_lo, ci_hi in zip(
        logit_model.params.index,
        logit_model.params.values,
        logit_model.conf_int()[0].values,
        logit_model.conf_int()[1].values):
    print(f"    {name:<20} OR={math.exp(coef):.3f}  "
          f"95%CI=[{math.exp(ci_lo):.3f}, {math.exp(ci_hi):.3f}]")

# ── (b) Linear probability model ──────────────────────────────────────────────
lpm = smf.ols('correct ~ dot_cue + depth_cue + color_cue', data=df).fit()
print("\n" + "="*70)
print("  LINEAR PROBABILITY MODEL (OLS on binary outcome)")
print("  Coefficients in probability units → multiply by 100 for pp")
print("="*70)
print(lpm.summary2())

print("\n  Coefficients in percentage points above chance:")
for name, coef, pval in zip(lpm.params.index, lpm.params.values, lpm.pvalues.values):
    if name == 'Intercept':
        baseline_pp = (coef - CHANCE) * 100
        print(f"    Baseline (all 0s): {coef*100:.1f}%  ({baseline_pp:+.1f}pp above chance)")
    else:
        print(f"    {name:<20} {coef*100:+.1f}pp   (p={pval:.4f})")

# ── Predicted vs observed ──────────────────────────────────────────────────────
cell_labels = []
obs_acc     = []
pred_logit  = []
pred_lpm    = []

for (cond, swap), grp in df.groupby(['cond','swap']):
    row = grp.iloc[0]
    x = {'dot_cue': row.dot_cue, 'depth_cue': row.depth_cue, 'color_cue': row.color_cue}
    obs  = grp.correct.mean()
    p_lo = logit_model.predict(pd.DataFrame([x]))[0]
    p_lp = lpm.predict(pd.DataFrame([x]))[0]
    cell_labels.append(f'{cond}\n+{swap}')
    obs_acc.append(obs)
    pred_logit.append(p_lo)
    pred_lpm.append(p_lp)

# ── Figure ────────────────────────────────────────────────────────────────────
SWAP_ORDER = ['N','C','Z','CZ']
COND_ORDER = ['CUED','UNCUED']
ordered = [(cond, swap) for swap in SWAP_ORDER for cond in COND_ORDER]

obs_ord   = []
logit_ord = []
lpm_ord   = []
lbl_ord   = []
dot_col   = []

for (cond, swap) in ordered:
    grp = df[(df.cond==cond) & (df.swap==swap)]
    row = grp.iloc[0]
    x   = pd.DataFrame([{'dot_cue': row.dot_cue, 'depth_cue': row.depth_cue,
                          'color_cue': row.color_cue}])
    obs_ord.append(grp.correct.mean())
    logit_ord.append(logit_model.predict(x)[0])
    lpm_ord.append(lpm.predict(x)[0])
    lbl_ord.append(f'{swap}\n{"CU" if cond=="CUED" else "UN"}')
    dot_col.append('#1565C0' if cond == 'CUED' else '#E65100')

xs = np.arange(len(ordered))
fig, axes = plt.subplots(1, 2, figsize=(13, 5.5))
fig.patch.set_facecolor('white')
fig.suptitle('DecoupledDots — GLM: Dot + Depth-field + Color-field Cueing\n'
             '(additive logistic regression, no interaction terms; n≈1026)',
             fontsize=11, fontweight='bold', y=1.02)

# Panel A: observed vs predicted (both models)
ax = axes[0]
ax.bar(xs - 0.27, np.array(obs_ord)*100,   0.25, color=dot_col, alpha=0.85, label='Observed', zorder=3)
ax.bar(xs,         np.array(logit_ord)*100, 0.25, color='#555', alpha=0.70, label='Logit predicted', zorder=3)
ax.bar(xs + 0.27,  np.array(lpm_ord)*100,  0.25, color='#999', alpha=0.55, label='LPM predicted',   zorder=3,
       hatch='//')
ax.axhline(CHANCE*100, color='#AAAAAA', lw=0.9, ls='--', zorder=1, label='Chance 12.5%')
ax.set_xticks(xs)
ax.set_xticklabels(lbl_ord, fontsize=7)
ax.set_ylabel('% correct', fontsize=9)
ax.set_ylim(0, 65)
ax.set_title('A.  Observed vs Predicted accuracy\n(colored = CUED/UNCUED, grey = model)',
             fontsize=9, fontweight='bold')
ax.legend(fontsize=7.5, loc='upper right', framealpha=0.9)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

# Bracket labels for swap groups
for si, swap in enumerate(SWAP_ORDER):
    xmid = si*2 + 0.5
    ax.text(xmid, 62, swap, ha='center', fontsize=8.5, fontweight='bold', color='#333')

# Panel B: coefficient plot
ax2 = axes[1]
params  = logit_model.params
ci      = logit_model.conf_int()
pvals   = logit_model.pvalues
terms   = ['dot_cue', 'depth_cue', 'color_cue']
ylabels = ['Dot cueing', 'Depth-field\ncueing', 'Color-field\ncueing']
colors  = ['#1565C0', '#1a6e8b', '#8b5a1a']
ys      = np.arange(len(terms))

for yi, (term, label, col) in enumerate(zip(terms, ylabels, colors)):
    coef  = params[term]
    lo    = ci.loc[term, 0]
    hi    = ci.loc[term, 1]
    pval  = pvals[term]
    s     = '***' if pval<.001 else '**' if pval<.01 else '*' if pval<.05 else '†' if pval<.1 else 'n.s.'
    # LPM coefficient in pp for annotation
    lpm_pp = lpm.params[term]*100

    ax2.errorbar(coef, yi, xerr=[[coef-lo],[hi-coef]],
                 fmt='o', color=col, ms=9, capsize=5, capthick=1.5, lw=2, zorder=4)
    ax2.text(hi + 0.04, yi + 0.08, s, fontsize=10, color=col, va='bottom')
    ax2.text(hi + 0.04, yi - 0.15, f'LPM: {lpm_pp:+.1f}pp', fontsize=7.5, color='#555')

ax2.axvline(0, color='#AAAAAA', lw=1, ls='--', zorder=1)
ax2.set_yticks(ys)
ax2.set_yticklabels(ylabels, fontsize=10)
ax2.set_xlabel('Log-odds coefficient (logistic regression)', fontsize=9)
ax2.set_title('B.  Model coefficients\n(dots = log-odds ± 95% CI; labels = LPM in pp)',
              fontsize=9, fontweight='bold')
ax2.set_xlim(-0.3, 1.8)
ax2.spines['top'].set_visible(False)
ax2.spines['right'].set_visible(False)

# Intercept annotation
intercept_pct = math.exp(params['Intercept']) / (1 + math.exp(params['Intercept'])) * 100
ax2.text(0.02, -0.7,
         f'Intercept: all factors=0 (UNCUED+CZ)\n'
         f'  Logit → {intercept_pct:.1f}% predicted correct\n'
         f'  McFadden R² = {mcfadden:.3f}',
         transform=ax2.transAxes, fontsize=7.5, color='#444',
         va='bottom',
         bbox=dict(boxstyle='round,pad=0.4', fc='#F9F9F9', ec='#CCC', lw=0.8))

plt.tight_layout()
os.makedirs(os.path.dirname(OUT), exist_ok=True)
fig.savefig(OUT, dpi=150, bbox_inches='tight', facecolor='white')
print(f"\nSaved: {OUT}")
