"""
NMoCol figure — N / M / C / MC conditions
SubfieldSwap_CatekExact_NMoCol_v1  ·  Ap 1.65° · 43 dots/field · 80 ms
Exact-match scoring (8AFC, chance = 12.5%)

Layout:
  Row 0: absolute accuracy bars (CUED + UNCUED per condition)
  Row 1: cueing-effect bars
  Row 2: polar response-error distributions (4 conditions × 2 arms = 8 polars)
  Row 3: precision (vector-average projection) bars
"""
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy import stats
from scipy.stats import binom

DATA = '/Users/genestoner1/Projects/ObjectBasedAttention/VRDots/Agents/Data'
OUT  = '/Users/genestoner1/Projects/ObjectBasedAttention/VRDots/Agents/SwapPilot/Figures/nmocol_pooled.png'
OUTPDF = OUT.replace('.png', '.pdf')

SESSIONS = ['260515_0848', '260517_1243', '260517_1322', '260517_1432', '260517_1522']

def load(sess):
    df = pd.read_csv(f'{DATA}/vr_dots_session_{sess}.tsv', sep='\t')
    df = df[df['RespDeg'] >= 0].copy()
    df['Correct'] = (df['RespDeg'] == df['TransDeg']).astype(float)
    df['ErrDeg']  = ((df['RespDeg'] - df['TransDeg'] + 360) % 360).apply(
                        lambda d: d if d <= 180 else d - 360)
    return df

def sig(p):
    if p < 0.001: return '***'
    if p < 0.01:  return '**'
    if p < 0.05:  return '*'
    if p < 0.1:   return '†'
    return 'n.s.'

def cue_stats(df, swap):
    sub = df[df['SwapType'] == swap]
    c = sub[sub['Cond'] == 'CUED']['Correct']
    u = sub[sub['Cond'] == 'UNCUED']['Correct']
    delta = (c.mean() - u.mean()) * 100
    rng = np.random.default_rng(42)
    bd = (rng.choice(c.values, (5000, len(c)), replace=True).mean(1) -
          rng.choice(u.values, (5000, len(u)), replace=True).mean(1)) * 100
    ci_lo, ci_hi = np.percentile(bd, [2.5, 97.5])
    pp = (c.sum() + u.sum()) / (len(c) + len(u))
    se = np.sqrt(pp * (1 - pp) * (1 / len(c) + 1 / len(u)))
    p  = 2 * (1 - stats.norm.cdf(abs((c.mean() - u.mean()) / se)))
    return dict(delta=delta, ci_lo=ci_lo, ci_hi=ci_hi, p=p, sig=sig(p),
                n=len(c)+len(u), cued=c.mean()*100, uncued=u.mean()*100)

def vec_proj(df, swap, cond):
    sub = df[(df['SwapType'] == swap) & (df['Cond'] == cond)]
    err_rad = np.deg2rad(sub['ErrDeg'].values)
    return np.cos(err_rad).mean()

def err_hist(df, swap, cond):
    sub = df[(df['SwapType'] == swap) & (df['Cond'] == cond)]
    err_unsigned = sub['ErrDeg'].values % 360
    bins = np.arange(-22.5, 360, 45)
    counts, _ = np.histogram(err_unsigned, bins=bins)
    centres = np.arange(0, 360, 45)
    return centres, counts / counts.sum()

pool = pd.concat([load(s) for s in SESSIONS], ignore_index=True)

CONDITIONS = [
    ('No Swap',     'N',  '#2ca02c'),
    ('Motion Swap', 'M',  '#1f77b4'),
    ('Color Swap',  'C',  '#9467bd'),
    ('MC Swap',     'MC', '#d62728'),
]
COND_ARMS = ['CUED', 'UNCUED']
ARM_COLS  = {'CUED': '#1a3a8a', 'UNCUED': '#8a2a1a'}
CUED_COL   = '#1a3a8a'
UNCUED_COL = '#8a2a1a'
DIRS_DEG = np.arange(0, 360, 45)
NCONDS = len(CONDITIONS)

# ── Figure layout ─────────────────────────────────────────────────────────────
fig = plt.figure(figsize=(16, 18))
fig.patch.set_facecolor('white')
gs  = fig.add_gridspec(4, NCONDS * 2,
                        height_ratios=[1.2, 1.2, 1.6, 1.0],
                        hspace=0.65, wspace=0.45)

# ── Row 0: absolute accuracy ──────────────────────────────────────────────────
ax_abs = fig.add_subplot(gs[0, NCONDS//2 : NCONDS//2 + NCONDS])
x = np.arange(NCONDS)
w = 0.3
for ai, (arm, arm_col) in enumerate([('CUED', CUED_COL), ('UNCUED', UNCUED_COL)]):
    vals, los, his = [], [], []
    for _, swap, _ in CONDITIONS:
        r = cue_stats(pool, swap)
        pct = r[arm.lower()]
        n_arm = r['n'] // 2
        h_arm = round(pct / 100 * n_arm)
        lo = binom.ppf(0.025, n_arm, pct / 100) / n_arm * 100
        hi = binom.ppf(0.975, n_arm, pct / 100) / n_arm * 100
        vals.append(pct); los.append(pct - lo); his.append(hi - pct)
    offset = (ai - 0.5) * w
    ax_abs.bar(x + offset, vals, w, color=arm_col, alpha=0.82, label=arm,
               yerr=[los, his], capsize=4, error_kw={'lw': 1.2, 'color': '#333'})
    for xi, v in enumerate(vals):
        ax_abs.text(xi + offset, v + his[xi] + 0.5, f'{v:.1f}%',
                    ha='center', va='bottom', fontsize=7.5, color=arm_col)

ax_abs.axhline(12.5, color='#aaa', lw=1, ls='--', label='chance (12.5%)')
ax_abs.set_xticks(x)
ax_abs.set_xticklabels([c[0] for c in CONDITIONS], fontsize=10)
ax_abs.set_ylabel('% Correct', fontsize=10)
ax_abs.set_ylim(0, 90)
ax_abs.set_title(f'Absolute Accuracy  —  {len(SESSIONS)} session(s)', fontsize=11, fontweight='bold')
ax_abs.legend(fontsize=9, framealpha=0.9)
ax_abs.spines['top'].set_visible(False)
ax_abs.spines['right'].set_visible(False)

# ── Row 1: cueing effect bars ─────────────────────────────────────────────────
ax_bar = fig.add_subplot(gs[1, NCONDS//2 : NCONDS//2 + NCONDS])
for xi, (label, swap, color) in enumerate(CONDITIONS):
    r = cue_stats(pool, swap)
    el = r['delta'] - r['ci_lo']
    eh = r['ci_hi'] - r['delta']
    ax_bar.bar(xi, r['delta'], 0.5, color=color, alpha=0.82,
               yerr=[[el], [eh]], capsize=5, error_kw={'lw': 1.4, 'color': '#333'})
    ypos = r['delta'] + (eh + 0.8 if r['delta'] >= 0 else -(el + 0.8))
    va   = 'bottom' if r['delta'] >= 0 else 'top'
    ax_bar.text(xi, ypos, f"{r['delta']:+.1f}pp\n{r['sig']}",
                ha='center', va=va, fontsize=9.5, fontweight='bold', color=color)
    ax_bar.text(xi, -7, f"n={r['n']}", ha='center', va='top', fontsize=8, color='#555')

ax_bar.axhline(0, color='#888', lw=1)
ax_bar.set_xticks(range(NCONDS))
ax_bar.set_xticklabels([c[0] for c in CONDITIONS], fontsize=10)
ax_bar.set_ylabel('Cueing effect (CUED − UNCUED, pp)', fontsize=10)
ax_bar.set_ylim(-10, 40)
ax_bar.set_title('Cueing Effect', fontsize=11, fontweight='bold')
ax_bar.spines['top'].set_visible(False)
ax_bar.spines['right'].set_visible(False)

# ── Row 2: polar error distributions (4 conds × 2 arms = 8 polars) ───────────
for ci, (label, swap, color) in enumerate(CONDITIONS):
    for ai, arm in enumerate(COND_ARMS):
        ax = fig.add_subplot(gs[2, ci * 2 + ai], projection='polar')
        centres, fracs = err_hist(pool, swap, arm)
        theta = np.deg2rad(centres)
        width = np.deg2rad(40)
        arm_col = ARM_COLS[arm]
        ax.bar(theta, fracs, width=width, color=arm_col, alpha=0.78,
               bottom=0.0, align='center')
        # Precision arrow
        proj = vec_proj(pool, swap, arm)
        ax.annotate('', xy=(0, proj), xytext=(0, 0),
                    arrowprops=dict(arrowstyle='->', color='orange', lw=2))
        ax.axhline(1/8, color='#aaa', lw=1, ls='--')
        ax.set_theta_zero_location('N')
        ax.set_theta_direction(-1)
        tick_labels = ['0°\n(correct)', '45°', '90°', '135°', '180°', '−135°', '−90°', '−45°']
        ax.set_xticks(theta)
        ax.set_xticklabels(tick_labels, fontsize=5.5)
        ax.set_yticks([0.125, 0.25, 0.5])
        ax.set_yticklabels(['12.5%', '25%', '50%'], fontsize=5.5)
        ax.set_ylim(0, 0.65)
        ax.set_title(f'{label}\n{arm}\nprec={proj:.3f}',
                     fontsize=7.5, fontweight='bold', color=color, pad=10)

# ── Row 3: precision bars ─────────────────────────────────────────────────────
ax_prec = fig.add_subplot(gs[3, NCONDS//2 : NCONDS//2 + NCONDS])
x = np.arange(NCONDS)
w = 0.3
for ai, arm in enumerate(COND_ARMS):
    projs = [vec_proj(pool, swap, arm) for _, swap, _ in CONDITIONS]
    offset = (ai - 0.5) * w
    ax_prec.bar(x + offset, projs, w, color=ARM_COLS[arm], alpha=0.82, label=arm)
    for xi, v in enumerate(projs):
        ax_prec.text(xi + offset, v + 0.01, f'{v:.3f}',
                     ha='center', va='bottom', fontsize=8, color=ARM_COLS[arm])

ax_prec.axhline(0, color='#888', lw=0.8)
ax_prec.axhline(np.cos(np.deg2rad(DIRS_DEG)).mean(), color='#aaa', lw=1, ls='--',
                label='chance (uniform)')
ax_prec.set_xticks(x)
ax_prec.set_xticklabels([c[0] for c in CONDITIONS], fontsize=10)
ax_prec.set_ylabel('Vector-avg projection\nonto correct direction', fontsize=9)
ax_prec.set_ylim(-0.05, 0.75)
ax_prec.set_title('Precision (vector-average projection)', fontsize=10, fontweight='bold')
ax_prec.legend(fontsize=8, framealpha=0.9)
ax_prec.spines['top'].set_visible(False)
ax_prec.spines['right'].set_visible(False)

fig.suptitle(
    f'VRDots — NMoCol  ·  Ap 1.65° · 43 dots/field · 80 ms · {len(SESSIONS)} session(s)  ·  {", ".join(SESSIONS)}\n'
    'SubfieldSwap_CatekExact_NMoCol_v1  ·  exact-match scoring (8AFC, chance = 12.5%)',
    fontsize=10.5, fontweight='bold', y=1.01)

for out in [OUT, OUTPDF]:
    plt.savefig(out, dpi=160, bbox_inches='tight', facecolor='white')
print(f'Saved: {OUT}')

print('\n=== Results ===')
for label, swap, _ in CONDITIONS:
    r = cue_stats(pool, swap)
    print(f'  {label:15s}: {r["delta"]:+.1f}pp {r["sig"]:5s}  CUED={r["cued"]:.1f}%  UNCUED={r["uncued"]:.1f}%  n={r["n"]}  p={r["p"]:.4f}')
    for arm in COND_ARMS:
        proj = vec_proj(pool, swap, arm)
        print(f'    {arm} precision: {proj:.3f}')
