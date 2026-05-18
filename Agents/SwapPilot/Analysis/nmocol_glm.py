"""
NMoCol 2³ Factor Analysis — OLS linear probability model
Sessions: SubfieldSwap_CatekExact_NMoCol_v1 (Ap1.65° radius, 43 dots/field)

Factors (±1 sum coding):
  F1: onset dot cue        +1=CUED (delayed field translates)  -1=UNCUED
  F2: color on translating +1=delayed color                    -1=non-delayed color
  F3: competing rotation   +1=non-delayed direction            -1=delayed direction

Factor assignment:
  N  CUED:  F1=+1 F2=+1 F3=+1    N  UNCUED: F1=-1 F2=-1 F3=-1
  M  CUED:  F1=+1 F2=+1 F3=-1    M  UNCUED: F1=-1 F2=-1 F3=+1
  C  CUED:  F1=+1 F2=-1 F3=+1    C  UNCUED: F1=-1 F2=+1 F3=-1
  MC CUED:  F1=+1 F2=-1 F3=-1    MC UNCUED: F1=-1 F2=+1 F3=+1

Coefficient interpretation: β × 2 × 100 = full effect in pp (±1 range = 2 units).
"""

import pandas as pd
import numpy as np
from scipy import stats
import statsmodels.formula.api as smf
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

DATA = '/Users/genestoner1/Projects/ObjectBasedAttention/VRDots/Agents/Data'
OUT  = '/Users/genestoner1/Projects/ObjectBasedAttention/VRDots/Agents/SwapPilot/Figures/nmocol_glm.png'
SESSIONS = ['260515_0848', '260517_1243', '260517_1322', '260517_1432', '260517_1522']

# ── Load ───────────────────────────────────────────────────────────────────────
dfs = []
for sess in SESSIONS:
    df = pd.read_csv(f'{DATA}/vr_dots_session_{sess}.tsv', sep='\t')
    df = df[df['RespDeg'] >= 0].copy()
    df['Session'] = sess
    df['Correct'] = (df['RespDeg'] == df['TransDeg']).astype(float)
    dfs.append(df)
df = pd.concat(dfs, ignore_index=True)
df = df[df['SwapType'].isin(['N', 'M', 'C', 'MC'])].copy()

# ── Factor coding ──────────────────────────────────────────────────────────────
df['F1'] = df['Cond'].map({'CUED': 1.0, 'UNCUED': -1.0})

no_color_swap  = df['SwapType'].isin(['N', 'M'])
no_motion_swap = df['SwapType'].isin(['N', 'C'])

df['F2'] = np.where(
    (no_color_swap  & (df['Cond'] == 'CUED')) | (~no_color_swap  & (df['Cond'] == 'UNCUED')),
    1.0, -1.0)

df['F3'] = np.where(
    (no_motion_swap & (df['Cond'] == 'CUED')) | (~no_motion_swap & (df['Cond'] == 'UNCUED')),
    1.0, -1.0)

# ── Verify cell assignments ────────────────────────────────────────────────────
print("Factor assignment verification:")
print(f"{'Cond':4s} {'Cue':7s}  F1  F2  F3   n     acc%")
for swap in ['N', 'M', 'C', 'MC']:
    for cond in ['CUED', 'UNCUED']:
        s = df[(df['SwapType'] == swap) & (df['Cond'] == cond)]
        f1, f2, f3 = int(s['F1'].iloc[0]), int(s['F2'].iloc[0]), int(s['F3'].iloc[0])
        print(f"{swap:4s} {cond:7s}  {f1:+d}  {f2:+d}  {f3:+d}  {len(s):4d}  {s['Correct'].mean()*100:.1f}%")

# ── OLS — full factorial model ────────────────────────────────────────────────
formula = 'Correct ~ F1 + F2 + F3 + F1:F2 + F1:F3 + F2:F3 + F1:F2:F3'
model = smf.ols(formula, data=df).fit()

TERMS = ['Intercept', 'F1', 'F2', 'F3', 'F1:F2', 'F1:F3', 'F2:F3', 'F1:F2:F3']
LABELS = {
    'Intercept': 'Grand mean',
    'F1':        'F1: onset dot cue',
    'F2':        'F2: color identity',
    'F3':        'F3: competing rotation',
    'F1:F2':     'F1 × F2',
    'F1:F3':     'F1 × F3',
    'F2:F3':     'F2 × F3',
    'F1:F2:F3':  'F1 × F2 × F3',
}

def sig(p):
    if p < 0.001: return '***'
    if p < 0.01:  return '**'
    if p < 0.05:  return '*'
    if p < 0.1:   return '†'
    return 'n.s.'

print(f"\n=== OLS Factor Analysis (n={len(df)} trials, {len(SESSIONS)} sessions) ===")
print(f"{'Term':20s}  {'β×2 (pp)':>9}  {'95% CI':>18}  {'p':>8}  {'sig':>5}")
print("─" * 70)
rows = []
for term in TERMS:
    b   = model.params[term]
    ci  = model.conf_int().loc[term]
    p   = model.pvalues[term]
    eff = b * 2 * 100          # full effect in pp (±1 coding → ×2)
    clo = ci[0] * 2 * 100
    chi = ci[1] * 2 * 100
    s   = sig(p)
    rows.append((term, eff, clo, chi, p, s))
    if term == 'Intercept':
        print(f"{'Grand mean':20s}  {b*100:>8.1f}%  {'':>18}  {'':>8}")
        print("─" * 70)
    else:
        print(f"{LABELS[term]:20s}  {eff:>+8.2f}pp  [{clo:+6.2f}, {chi:+6.2f}]  {p:>8.4f}  {s:>5}")

# ── Figure ────────────────────────────────────────────────────────────────────
effect_terms = [t for t in TERMS if t != 'Intercept']
effs  = [r[1] for r in rows if r[0] != 'Intercept']
clos  = [r[2] for r in rows if r[0] != 'Intercept']
chis  = [r[3] for r in rows if r[0] != 'Intercept']
pvals = [r[4] for r in rows if r[0] != 'Intercept']
sigs  = [r[5] for r in rows if r[0] != 'Intercept']

colors = []
for t, p in zip(effect_terms, pvals):
    if   p < 0.001: colors.append('#1a5276')
    elif p < 0.01:  colors.append('#2874a6')
    elif p < 0.05:  colors.append('#5dade2')
    elif p < 0.1:   colors.append('#aed6f1')
    else:           colors.append('#d5d8dc')

fig, ax = plt.subplots(figsize=(8, 5))
fig.patch.set_facecolor('#1a1a2e')
ax.set_facecolor('#1a1a2e')

y = np.arange(len(effect_terms))
errs_lo = [abs(e - c) for e, c in zip(effs, clos)]
errs_hi = [abs(c - e) for c, e in zip(chis, effs)]
bars = ax.barh(y, effs, xerr=[errs_lo, errs_hi], color=colors,
               ecolor='#aaa', capsize=4, height=0.55)

ax.axvline(0, color='#888', lw=1, ls='--')
ax.set_yticks(y)
ax.set_yticklabels([LABELS[t] for t in effect_terms], color='white', fontsize=10)
ax.set_xlabel('Effect size (pp)', color='white', fontsize=10)
ax.tick_params(colors='white')
for spine in ax.spines.values():
    spine.set_edgecolor('#555')

# significance labels
for i, (eff, s, p) in enumerate(zip(effs, sigs, pvals)):
    x = eff + (errs_hi[i] + 1) * np.sign(eff) if eff != 0 else 1
    ax.text(x, i, s, va='center', ha='left' if eff >= 0 else 'right',
            color='white', fontsize=9, fontweight='bold')

ax.set_title(
    f'NMoCol 2³ Factor Analysis  ·  {len(SESSIONS)} sessions  ·  n={len(df)} trials\n'
    f'Ap1.65° radius  ·  43 dots/field  ·  SubfieldSwap_CatekExact_NMoCol_v1',
    color='white', fontsize=9, pad=8)

plt.tight_layout()
plt.savefig(OUT, dpi=150, bbox_inches='tight', facecolor=fig.get_facecolor())
print(f"\nSaved: {OUT}")
