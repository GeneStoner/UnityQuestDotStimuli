#!/usr/bin/env python3
"""
depthcolorlinked_glm.py
-----------------------
Logistic regression on DepthColorLinked (ZdA/ZdB, Near=Red, Far=Green)
data — 4 sessions, n=1024 trials.

Factors (all binary, coded 0/1):
  F1  Dot cueing          : CUED=1, UNCUED=0
  F2  Depth+Color cued    : translator stays in onset plane (ZdNoi for CUED)=1
                            translator changes plane (ZdCoh for CUED)=0
  F3  Translator Near     : Near=1, Far=0

Model:
  logit(correct) = β₀ + β₁F1 + β₂F2 + β₃F3
                      + β₄(F1×F2) + β₅(F1×F3) + β₆(F2×F3)

Note: F2 captures depth+color object continuity jointly (confounded in this
design — both always swap together). Cannot separate depth vs color here.

Sessions: 260404_0940, 260404_1123, 260406_1001, 260406_1034  (n=1024)
Output: Agents/Figures/depthcolorlinked_glm.pdf
"""

import csv, math, os, datetime
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.backends.backend_pdf import PdfPages
import statsmodels.formula.api as smf
from statsmodels.stats.proportion import proportion_confint

DATE_STR = datetime.date.today().strftime('%Y-%m-%d')

BASE    = os.path.normpath(os.path.join(os.path.dirname(__file__), '../../Agents/Figures'))
OUT_PDF = os.path.join(BASE, 'depthcolorlinked_glm.pdf')
PULL2   = '/tmp/quest_pull2/files'

SESSIONS = [
    f'{PULL2}/vr_dots_session_260404_0940.tsv',
    f'{PULL2}/vr_dots_session_260404_1123.tsv',
    f'{PULL2}/vr_dots_session_260406_1001.tsv',
    f'{PULL2}/vr_dots_session_260406_1034.tsv',
]

CHANCE = 1 / 8

def is_correct(td, rd):
    d = (float(rd) - float(td) + 360) % 360
    return int((360 - d if d > 180 else d) <= 22.5)

# ── Load data ──────────────────────────────────────────────────────────────────
rows = []
for path in SESSIONS:
    if not os.path.exists(path):
        print(f'Missing: {path}'); continue
    with open(path, newline='') as f:
        for r in csv.DictReader(f, delimiter='\t'):
            if (not r.get('TransDeg','').strip() or
                    not r.get('RespDeg','').strip() or
                    r.get('EndKey','') in ('timeout','skip','requeue')):
                continue

            cond = r['Cond']
            swap = r['SwapType']   # ZdA or ZdB

            # F1: dot cueing
            f1 = 1 if cond == 'CUED' else 0

            # F2: depth+color object continuity for the TRANSLATOR
            # ZdNoi for CUED = translator stays in onset plane (ZdB when CUED)
            # ZdCoh for CUED = translator changes plane (ZdA when CUED)
            # Equivalently: F2=1 when translator is in its original depth+color plane
            coh_translator = ((cond == 'CUED'   and swap == 'ZdB') or
                              (cond == 'UNCUED' and swap == 'ZdA'))
            f2 = 1 if coh_translator else 0

            # F3: translator Near (1) vs Far (0)
            b_near = (r['DelayedFieldDepth'] == 'N')
            trans_near = b_near if cond == 'CUED' else not b_near
            f3 = 1 if trans_near else 0

            correct = is_correct(r['TransDeg'], r['RespDeg'])
            rows.append({'F1': f1, 'F2': f2, 'F3': f3, 'correct': correct})

df = pd.DataFrame(rows)
print(f'n = {len(df)} trials loaded')

# ── Fit GLM ───────────────────────────────────────────────────────────────────
model = smf.logit('correct ~ F1 + F2 + F3 + F1:F2 + F1:F3 + F2:F3', data=df).fit()
print(model.summary())

# ── Average Marginal Effects ───────────────────────────────────────────────────
ame = model.get_margeff()
print(ame.summary())

# ── Extract coefficients ───────────────────────────────────────────────────────
params  = model.params
bse     = model.bse
tvals   = model.tvalues
pvals   = model.pvalues
conf    = model.conf_int()

term_map = {
    'Intercept':   'Intercept (β₀)',
    'F1':          'F1  Dot cueing',
    'F2':          'F2  Depth+Color cued',
    'F3':          'F3  Translator Near',
    'F1:F2':       'F1 × F2',
    'F1:F3':       'F1 × F3',
    'F2:F3':       'F2 × F3',
}

def sig(p):
    if p < 0.001: return '***'
    if p < 0.01:  return '**'
    if p < 0.05:  return '*'
    if p < 0.10:  return '†'
    return 'n.s.'

print('\n--- Coefficients ---')
for k, label in term_map.items():
    if k not in params: continue
    b = params[k]; se = bse[k]; z = tvals[k]; p = pvals[k]
    or_ = math.exp(b)
    print(f'{label:30s}  β={b:+.3f}  SE={se:.3f}  z={z:+.2f}  p={p:.3f} {sig(p):5s}  OR={or_:.2f}')

# ── AME table ─────────────────────────────────────────────────────────────────
ame_df = ame.summary_frame()
print('\n--- AMEs (pp) ---')
for idx in ame_df.index:
    dy = ame_df.loc[idx, 'dy/dx'] * 100
    pz = ame_df.loc[idx, 'Pr(>|z|)']
    print(f'{idx:30s}  AME={dy:+.1f}pp  p={pz:.3f} {sig(pz)}')

# ── Figure ─────────────────────────────────────────────────────────────────────
# Page 1: Forest plot (log-odds left, AME pp right)

PLOT_TERMS = ['F1', 'F2', 'F3', 'F1:F2', 'F1:F3', 'F2:F3']
PLOT_LABELS = [
    'F1  Dot cueing',
    'F2  Depth+Color\n     cued',
    'F3  Translator\n     Near',
    'F1 × F2\n(dot × depth+col)',
    'F1 × F3\n(dot × Near)',
    'F2 × F3\n(depth+col × Near)',
]
COLORS = ['#2c5f8a','#1a6b1a','#884400','#c0392b','#6b2a8a','#8a6b1a']

fig1, axes = plt.subplots(1, 2, figsize=(11, 5))
fig1.suptitle(
    'DepthColorLinked GLM  ·  logit(correct) ~ F1+F2+F3+F1:F2+F1:F3+F2:F3\n'
    f'n={len(df)} trials  ·  4 sessions',
    fontsize=10, fontweight='bold', y=0.99)

ys = np.arange(len(PLOT_TERMS))

# Left: log-odds coefficients
ax = axes[0]
for i, (term, lbl, col) in enumerate(zip(PLOT_TERMS, PLOT_LABELS, COLORS)):
    if term not in params: continue
    b = params[term]
    lo = conf.loc[term, 0]
    hi = conf.loc[term, 1]
    p  = pvals[term]
    ax.errorbar(b, i, xerr=[[b-lo],[hi-b]],
                fmt='o', color=col, markersize=6, elinewidth=1.5, capsize=4, zorder=3)
    star = sig(p)
    ax.text(hi + 0.05, i, star, va='center', fontsize=8, color=col, fontweight='bold')

ax.axvline(0, color='#333', lw=0.8, ls='--', zorder=1)
ax.set_yticks(ys)
ax.set_yticklabels(PLOT_LABELS, fontsize=8)
ax.set_xlabel('Log-odds coefficient (95% CI)', fontsize=9)
ax.set_title('Log-odds coefficients', fontsize=9, fontweight='bold')
ax.spines[['top','right']].set_visible(False)
ax.yaxis.grid(True, lw=0.3, color='#e0e0e0')
ax.set_axisbelow(True)

# Right: AME in pp
ax2 = axes[1]
ame_df = ame.summary_frame()
for i, (term, lbl, col) in enumerate(zip(PLOT_TERMS, PLOT_LABELS, COLORS)):
    # AME index names: F1, F2, F3, F1:F2 → statsmodels uses 'F1:F2'
    idx = term
    if idx not in ame_df.index: continue
    dy   = ame_df.loc[idx, 'dy/dx'] * 100
    se_a = ame_df.loc[idx, 'Std. Err.'] * 100
    p    = ame_df.loc[idx, 'Pr(>|z|)']
    ax2.errorbar(dy, i, xerr=[[1.96*se_a],[1.96*se_a]],
                 fmt='o', color=col, markersize=6, elinewidth=1.5, capsize=4, zorder=3)
    ax2.text(dy + 1.0*np.sign(dy) + (2 if dy >= 0 else -2), i,
             sig(p), va='center', fontsize=8, color=col, fontweight='bold')

ax2.axvline(0, color='#333', lw=0.8, ls='--', zorder=1)
ax2.axvline(0, color='#cc4444', lw=0.6, ls=':', alpha=0)  # dummy
ax2.set_yticks(ys)
ax2.set_yticklabels([''] * len(ys))
ax2.set_xlabel('Average Marginal Effect (pp, 95% CI)', fontsize=9)
ax2.set_title('Average Marginal Effects', fontsize=9, fontweight='bold')
ax2.spines[['top','right']].set_visible(False)
ax2.yaxis.grid(True, lw=0.3, color='#e0e0e0')
ax2.set_axisbelow(True)

plt.tight_layout(rect=[0, 0, 1, 0.94])

# ── Page 2: Predicted vs Observed ─────────────────────────────────────────────
df['fitted'] = model.predict()
df['F2_label'] = df['F2'].map({1:'ZdNoi (Depth✓)', 0:'ZdCoh (Depth✗)'})
df['F1_label'] = df['F1'].map({1:'CUED', 0:'UNCUED'})
df['F3_label'] = df['F3'].map({1:'Near', 0:'Far'})

fig2, axes2 = plt.subplots(1, 2, figsize=(10, 5), sharey=True)
fig2.suptitle('Predicted vs Observed accuracy — DepthColorLinked',
              fontsize=10, fontweight='bold', y=0.99)

def wilson_ci(k, n, z=1.96):
    if n == 0: return 0.0, 0.0
    p = k/n; d = 1 + z**2/n
    c = (p + z**2/(2*n)) / d
    hw = z * math.sqrt(p*(1-p)/n + z**2/(4*n**2)) / d
    return c - hw, c + hw

x_labels = ['Far\nCUED', 'Near\nCUED', 'Far\nUNCUED', 'Near\nUNCUED']
conditions = [(1,0,'CUED','Far'), (1,1,'CUED','Near'),
              (0,0,'UNCUED','Far'), (0,1,'UNCUED','Near')]
PANEL_TITLES = ['ZdNoi  (translator stays in plane)', 'ZdCoh  (translator changes plane)']
F2_VALS = [1, 0]
PANEL_COLS = ['#1a6b1a', '#c0392b']

for pi, (f2val, ptitle, pcol) in enumerate(zip(F2_VALS, PANEL_TITLES, PANEL_COLS)):
    ax = axes2[pi]
    sub = df[df['F2'] == f2val]
    xs = np.arange(4)

    obs_pcts, obs_los, obs_his = [], [], []
    pred_pcts = []

    for f1val, f3val, cl, dl in conditions:
        cell = sub[(sub['F1'] == f1val) & (sub['F3'] == f3val)]
        k = cell['correct'].sum(); n = len(cell)
        pct = k/n*100 if n else 0
        lo, hi = wilson_ci(k, n)
        obs_pcts.append(pct)
        obs_los.append(pct - lo*100)
        obs_his.append(hi*100 - pct)
        pred_pcts.append(cell['fitted'].mean()*100 if n else 0)

    bar_cols = ['#44aa88','#8844aa','#44aa88','#8844aa']
    edge_cols = ['#2c5f8a','#2c5f8a','#aaaaaa','#aaaaaa']

    bars = ax.bar(xs - 0.17, obs_pcts, width=0.3,
                  color=bar_cols, alpha=0.85, zorder=2,
                  edgecolor=edge_cols, linewidth=1.2, label='Observed')
    ax.errorbar(xs - 0.17, obs_pcts,
                yerr=[obs_los, obs_his],
                fmt='none', ecolor='#222', elinewidth=1, capsize=3, zorder=3)
    ax.bar(xs + 0.17, pred_pcts, width=0.3,
           color=bar_cols, alpha=0.4, zorder=2,
           edgecolor=edge_cols, linewidth=0.8, linestyle='--', label='Predicted')

    ax.axhline(CHANCE*100, color='#cc4444', lw=0.9, ls='--', zorder=1)
    ax.axvline(1.5, color='#cccccc', lw=0.8, ls='--')
    ax.set_xticks(xs)
    ax.set_xticklabels(x_labels, fontsize=8)
    ax.set_ylim(0, 80)
    ax.set_yticks([0, 12.5, 25, 50, 75])
    ax.yaxis.grid(True, lw=0.4, color='#e0e0e0', zorder=0)
    ax.set_axisbelow(True)
    ax.spines[['top','right']].set_visible(False)
    ax.set_title(ptitle, fontsize=9, fontweight='bold', color=pcol, pad=6)
    if pi == 0:
        ax.set_ylabel('% correct', fontsize=9)
        ax.legend(fontsize=7.5, loc='upper right', framealpha=0.8)

handles = [
    mpatches.Patch(facecolor='#44aa88', label='Far translator'),
    mpatches.Patch(facecolor='#8844aa', label='Near translator'),
    mpatches.Patch(facecolor='none', edgecolor='#2c5f8a', lw=1.2, label='CUED'),
    mpatches.Patch(facecolor='none', edgecolor='#aaaaaa', lw=1.2, label='UNCUED'),
]
fig2.legend(handles=handles, loc='lower center', fontsize=7.5, ncol=4,
            bbox_to_anchor=(0.5, 0.01), framealpha=0.9)
plt.tight_layout(rect=[0, 0.08, 1, 0.94])

fig1.text(0.01, 0.005, f'{os.path.basename(OUT_PDF)}  ·  {DATE_STR}', fontsize=5, color='#888888', ha='left', va='bottom')
fig1.text(0.99, 0.005, f'p. 1/2', fontsize=5, color='#888888', ha='right', va='bottom')
fig2.text(0.01, 0.005, f'{os.path.basename(OUT_PDF)}  ·  {DATE_STR}', fontsize=5, color='#888888', ha='left', va='bottom')
fig2.text(0.99, 0.005, f'p. 2/2', fontsize=5, color='#888888', ha='right', va='bottom')

# ── Save PDF ───────────────────────────────────────────────────────────────────
os.makedirs(BASE, exist_ok=True)
with PdfPages(OUT_PDF) as pdf:
    pdf.savefig(fig1, bbox_inches='tight')
    pdf.savefig(fig2, bbox_inches='tight')
plt.close('all')
print(f'\nSaved: {OUT_PDF}')
