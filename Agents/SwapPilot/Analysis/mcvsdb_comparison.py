"""
MC vs Db comparison — SubfieldSwap_MCvsDb_Ap165_v1
=====================================================
Tests whether MC (same-dot feature swap) and Db (full membership swap) produce
identical psychophysical results, as predicted by their pixel-identical visual
displays at the 1.65° aperture.

SwapType strings in TSV:
  MC  → Motion(1)+Color(2)=3  — same physical dots; rotation reverses, colors swap
  Db  → Dots50(4)+Dots50A(128)=132 — full membership reversal; visually identical to MC

Label convention:
  MC: raw CUED/UNCUED labels are correct (onset-cued field FieldB translates throughout)
  Db: CUED/UNCUED labels are FLIPPED before analysis (onset-cued field FieldB now has
      always-on dots S0 translating after tStart; raw 'CUED' = dot-UNCUED)

Usage:
  python mcvsdb_comparison.py [tsv_path ...]
  If no paths given, scans DATA_DIR for SubfieldSwap_MCvsDb_Ap165_v1 sessions.
"""

import sys
import glob
import math
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy import stats

# ── config ────────────────────────────────────────────────────────────────────
DATA_DIR   = '/tmp/quest_pull_mcvsdb/files/'
EXPERIMENT = 'SubfieldSwap_MCvsDb_Ap165_v1'
OUT_FIG    = ('/Users/genestoner1/Projects/ObjectBasedAttention/VRDots/'
              'Agents/SwapPilot/Figures/mcvsdb_comparison.png')
OUT_PDF    = OUT_FIG.replace('.png', '.pdf')
CHANCE     = 100 / 8   # 12.5% (8 directions)

# ── helpers ───────────────────────────────────────────────────────────────────
def wilson_ci(hits, n, z=1.96):
    p = hits / n if n > 0 else 0.5
    denom = 1 + z**2 / n
    centre = (p + z**2 / (2*n)) / denom
    half = z * math.sqrt(p*(1-p)/n + z**2/(4*n**2)) / denom
    return (centre - half) * 100, (centre + half) * 100

def boot_delta_ci(nc, hc, nu, hu, n_boot=10000, seed=42):
    rng = np.random.default_rng(seed)
    pc_boot = rng.binomial(nc, hc/nc, n_boot) / nc
    pu_boot = rng.binomial(nu, hu/nu, n_boot) / nu
    deltas = (pc_boot - pu_boot) * 100
    return np.percentile(deltas, 2.5), np.percentile(deltas, 97.5)

def fisher_p(hc, nc, hu, nu):
    table = [[hc, nc - hc], [hu, nu - hu]]
    _, p = stats.fisher_exact(table)
    return p

def sig_stars(p):
    if p < 0.001: return '***'
    if p < 0.01:  return '**'
    if p < 0.05:  return '*'
    return 'n.s.'

# ── load data ─────────────────────────────────────────────────────────────────
if len(sys.argv) > 1:
    paths = sys.argv[1:]
else:
    paths = sorted(glob.glob(DATA_DIR + 'vr_dots_session_*.tsv'))

frames = []
for p in paths:
    try:
        df = pd.read_csv(p, sep='\t')
    except Exception as e:
        print(f'[SKIP] {p}: {e}')
        continue
    mask = df['Experiment'].str.contains(EXPERIMENT, na=False)
    if mask.any():
        frames.append(df[mask])
        print(f'Loaded {mask.sum()} rows from {p}')

if not frames:
    print(f'No {EXPERIMENT} data found. Check DATA_DIR or pass TSV paths as arguments.')
    sys.exit(1)

df = pd.concat(frames, ignore_index=True)
df['correct'] = (df['RespDeg'] == df['TransDeg']).astype(float)

print(f'\nTotal rows: {len(df)}')
print(f'SwapTypes:  {sorted(df["SwapType"].unique())}')
print(f'Cond:       {sorted(df["Cond"].unique())}')

# ── Db label flip ─────────────────────────────────────────────────────────────
db_mask = df['SwapType'] == 'Db'
df.loc[db_mask, 'Cond'] = df.loc[db_mask, 'Cond'].map({'CUED': 'UNCUED', 'UNCUED': 'CUED'})
print(f'Db rows relabeled: {db_mask.sum()}')

# ── per-condition stats ────────────────────────────────────────────────────────
CONDITIONS = ['MC', 'Db']
COND_LABELS = {
    'MC': 'MC\n(same dots; features swap)',
    'Db': 'Db\n(full membership swap)',
}
COLORS = {'MC': '#1a6eb5', 'Db': '#b54a1a'}

stats_out = {}
for sw in CONDITIONS:
    sub = df[df['SwapType'] == sw]
    if sub.empty:
        print(f'[WARN] No rows for SwapType={sw}')
        continue
    for cond in ['CUED', 'UNCUED']:
        arm = sub[sub['Cond'] == cond]
        n   = len(arm)
        h   = int(arm['correct'].sum())
        p   = h / n if n > 0 else np.nan
        lo, hi = wilson_ci(h, n) if n > 0 else (np.nan, np.nan)
        stats_out[(sw, cond)] = dict(n=n, h=h, pct=p*100, lo=lo, hi=hi)

    # cueing effect
    c = stats_out.get((sw, 'CUED'),   {})
    u = stats_out.get((sw, 'UNCUED'), {})
    if c and u and c['n'] > 0 and u['n'] > 0:
        delta = c['pct'] - u['pct']
        ci_lo, ci_hi = boot_delta_ci(c['n'], c['h'], u['n'], u['h'])
        p_val = fisher_p(c['h'], c['n'], u['h'], u['n'])
        stats_out[(sw, 'delta')] = dict(delta=delta, ci_lo=ci_lo, ci_hi=ci_hi,
                                        p=p_val, stars=sig_stars(p_val))

# ── print summary ──────────────────────────────────────────────────────────────
print('\n--- Per-condition summary ---')
for sw in CONDITIONS:
    for cond in ['CUED', 'UNCUED']:
        r = stats_out.get((sw, cond))
        if r:
            print(f'  {sw} {cond:6s}: {r["pct"]:5.1f}%  n={r["n"]}  '
                  f'95%CI [{r["lo"]:.1f}, {r["hi"]:.1f}]')
    d = stats_out.get((sw, 'delta'))
    if d:
        print(f'  {sw} Δpp:    {d["delta"]:+.1f}pp  '
              f'boot95 [{d["ci_lo"]:+.1f}, {d["ci_hi"]:+.1f}]  '
              f'p={d["p"]:.4f} {d["stars"]}')
    print()

# MC vs Db cueing effect difference (are they equal?)
dMC = stats_out.get(('MC', 'delta'), {})
dDb = stats_out.get(('Db', 'delta'), {})
if dMC and dDb:
    diff = dMC['delta'] - dDb['delta']
    print(f'MC Δpp − Db Δpp = {diff:+.1f}pp  '
          f'(prediction: ≈ 0 if stimuli identical)')

# ── Figure ────────────────────────────────────────────────────────────────────
n_sessions = len(frames)
n_total    = len(df)

fig, axes = plt.subplots(1, 2, figsize=(12, 5.5))
fig.patch.set_facecolor('white')

# ── Left panel: accuracy bars ──────────────────────────────────────────────────
ax = axes[0]
x = np.arange(len(CONDITIONS))
w = 0.30
cued_col   = '#223388'
uncued_col = '#883322'

for ci, (arm_label, arm_col) in enumerate([('CUED', cued_col), ('UNCUED', uncued_col)]):
    vals, los, his = [], [], []
    for sw in CONDITIONS:
        r = stats_out.get((sw, arm_label), {})
        vals.append(r.get('pct', np.nan))
        pct = r.get('pct', 50)
        lo, hi = r.get('lo', pct), r.get('hi', pct)
        los.append(pct - lo)
        his.append(hi - pct)
    offset = (ci - 0.5) * w
    ax.bar(x + offset, vals, w, color=arm_col, alpha=0.82, label=arm_label,
           yerr=[los, his], capsize=4, error_kw={'lw': 1.2})
    for xi, v in enumerate(vals):
        if not np.isnan(v):
            ax.text(xi + offset, v + his[xi] + 1.5, f'{v:.1f}%',
                    ha='center', va='bottom', fontsize=7.5, color=arm_col)

ax.axhline(CHANCE, color='#AAAAAA', lw=1.2, ls='--', label='chance (12.5%)')
ax.set_xticks(x)
ax.set_xticklabels([COND_LABELS[s] for s in CONDITIONS], fontsize=9.5)
ax.set_ylabel('% Correct', fontsize=10)
ax.set_ylim(0, 100)
ax.set_title('Accuracy by Condition', fontsize=11, fontweight='bold')
ax.legend(fontsize=9, framealpha=0.9)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

# ── Right panel: cueing effect ─────────────────────────────────────────────────
ax2 = axes[1]
deltas, lo_errs, hi_errs, bar_colors, annots = [], [], [], [], []
for sw in CONDITIONS:
    d = stats_out.get((sw, 'delta'), {})
    delta  = d.get('delta', np.nan)
    ci_lo  = d.get('ci_lo', delta)
    ci_hi  = d.get('ci_hi', delta)
    stars  = d.get('stars', '')
    deltas.append(delta)
    lo_errs.append(delta - ci_lo if not np.isnan(delta) else 0)
    hi_errs.append(ci_hi - delta if not np.isnan(delta) else 0)
    bar_colors.append(COLORS[sw])
    annots.append(f'{delta:+.1f}pp\n{stars}' if not np.isnan(delta) else '')

bars2 = ax2.bar(x, deltas, 0.45, color=bar_colors, alpha=0.85,
                yerr=[lo_errs, hi_errs], capsize=5,
                error_kw={'lw': 1.4})
ax2.axhline(0, color='#888888', lw=1)

for xi, (v, hi, ann) in enumerate(zip(deltas, hi_errs, annots)):
    if not np.isnan(v) and ann:
        yoff = hi + 1.5 if v >= 0 else -(lo_errs[xi] + 1.5)
        va   = 'bottom' if v >= 0 else 'top'
        ax2.text(xi, v + yoff if v >= 0 else v + yoff, ann,
                 ha='center', va=va, fontsize=9, fontweight='bold',
                 color=bar_colors[xi])

ax2.set_xticks(x)
ax2.set_xticklabels([COND_LABELS[s] for s in CONDITIONS], fontsize=9.5)
ax2.set_ylabel('Cueing effect (CUED − UNCUED, pp)', fontsize=10)
ax2.set_title('Cueing Effect: MC vs Db', fontsize=11, fontweight='bold')
ax2.spines['top'].set_visible(False)
ax2.spines['right'].set_visible(False)

# Annotation: prediction
ax2.text(0.5, 0.97,
         'Prediction: MC ≈ Db if stimuli are pixel-identical',
         ha='center', va='top', transform=ax2.transAxes,
         fontsize=8.5, style='italic', color='#444444')

title_str = (f'MC vs Db  |  {EXPERIMENT}  |  '
             f'n={n_total} trials  ({n_sessions} session{"s" if n_sessions!=1 else ""})\n'
             f'Aperture 1.65°, 43 dots/field, 80ms translation  '
             f'[Db CUED/UNCUED corrected]')
fig.suptitle(title_str, fontsize=10.5, fontweight='bold', y=1.02)
plt.tight_layout()

for out in [OUT_FIG, OUT_PDF]:
    plt.savefig(out, dpi=160, bbox_inches='tight', facecolor='white')
    print(f'Saved: {out}')
