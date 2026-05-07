"""
Psychometric threshold analysis using mean resultant length R̄ (circular precision)
instead of proportion correct. R̄ is continuous [0,1], so smoother with sparse data.

R̄(t) = R_max * (1 - exp(-((t/alpha)^beta)))

Threshold extracted at R̄ = R_max * 0.5 (midpoint to asymptote).
Cueing ratio: R = T_UNCUED / T_CUED.
"""
import sys
import warnings
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

SESSIONS = sys.argv[1:] if len(sys.argv) > 1 else [
    '/tmp/quest_pull_apersweep/vr_dots_session_260427_1554.tsv',
    '/tmp/quest_pull_apersweep/vr_dots_session_260427_2007.tsv',
]

CONDITIONS  = ['N', 'D', 'Da', 'Db']
COND_LABELS = {'N':'N (no swap)','D':'D (noise-half)',
               'Da':'Da (coh-half)','Db':'Db (full swap)'}
CUED_COL    = '#1a3a8b'
UNCUED_COL  = '#884400'

# ── Helpers ───────────────────────────────────────────────────────────────────
def mean_R(err_rad):
    return float(abs(np.mean(np.exp(1j * np.asarray(err_rad)))))

def weibull_R(log_t, log_alpha, beta, R_max):
    return R_max * (1 - np.exp(-np.power(10, beta * (log_t - log_alpha))))

def fit_precision_curve(dur_ms, R_vals, n_trials):
    """Fit R̄(t) = R_max*(1-exp(-(t/alpha)^beta)). Returns (log_T50, log_alpha, beta, R_max)."""
    if len(dur_ms) < 4:
        return None
    log_t = np.log10(np.asarray(dur_ms, dtype=float))
    y     = np.asarray(R_vals, dtype=float)
    R_max_init = min(float(np.max(y)) * 1.1, 0.95)
    try:
        with warnings.catch_warnings():
            warnings.simplefilter('ignore')
            popt, _ = curve_fit(
                weibull_R, log_t, y,
                p0=[np.log10(np.median(dur_ms)), 1.5, R_max_init],
                bounds=([-1, 0.3, 0.05], [3, 10, 1.0]),
                maxfev=8000
            )
        log_alpha, beta, R_max = popt
        # Threshold: R̄ = R_max/2  →  solve for log_T
        # R_max/2 = R_max*(1-exp(-(T/alpha)^beta))
        # => 0.5 = 1 - exp(-(T/alpha)^beta)
        # => (T/alpha)^beta = ln(2)
        # => log_T = log_alpha + log10(ln(2))/beta
        log_T = log_alpha + np.log10(np.log(2)) / beta
        return log_T, log_alpha, beta, R_max
    except Exception:
        return None

# ── Load & prep ───────────────────────────────────────────────────────────────
dfs = [pd.read_csv(p, sep='\t') for p in SESSIONS]
df  = pd.concat(dfs, ignore_index=True)
df['correct']  = (df['TransDeg'] == df['RespDeg']).astype(int)
df['err_rad']  = np.deg2rad(((df['RespDeg'] - df['TransDeg'] + 180) % 360) - 180)
mask = df['SwapType'].isin(['Da','Db'])
df.loc[mask,'Cond'] = df.loc[mask,'Cond'].map({'CUED':'UNCUED','UNCUED':'CUED'})
df['dur_bin'] = df['PresentedDurMs'].round(0).astype(int)

print(f"Total trials: {len(df)}")
print(f"Duration bins: {sorted(df['dur_bin'].unique())}")

# ── Compute R̄ per (cond, cue, duration) cell ─────────────────────────────────
cells = {}
for cond in CONDITIONS:
    for cue in ['CUED','UNCUED']:
        sub = df[(df['SwapType']==cond)&(df['Cond']==cue)]
        g   = sub.groupby('dur_bin').apply(
            lambda x: pd.Series({'R': mean_R(x['err_rad']),
                                 'n': len(x),
                                 'acc': x['correct'].mean()}),
            include_groups=False
        ).reset_index()
        g.columns = ['dur_ms','R','n','acc']
        result = fit_precision_curve(g['dur_ms'].values, g['R'].values, g['n'].values)
        cells[(cond,cue)] = dict(grouped=g, fit=result,
                                 T_ms=10**result[0] if result else np.nan,
                                 R_max=result[3] if result else np.nan)

# ── Console table ─────────────────────────────────────────────────────────────
print(f'\n{"Cond":<5} {"T_CUED":>10} {"T_UNCUED":>11} {"R=Tu/Tc":>10} {"Rmax_C":>8} {"Rmax_U":>8}')
print('-'*55)
for cond in CONDITIONS:
    Tc   = cells[(cond,'CUED')]['T_ms']
    Tu   = cells[(cond,'UNCUED')]['T_ms']
    Rmc  = cells[(cond,'CUED')]['R_max']
    Rmu  = cells[(cond,'UNCUED')]['R_max']
    ratio = Tu/Tc if (not np.isnan(Tc) and not np.isnan(Tu) and Tc>0) else np.nan
    print(f"{cond:<5} {Tc:>10.1f}ms {Tu:>10.1f}ms {ratio:>10.3f} {Rmc:>8.3f} {Rmu:>8.3f}")

# ── Figure: 4 rows × 1 col (will become 4 × n_apertures later) ───────────────
t_fine = np.logspace(np.log10(15), np.log10(400), 300)

fig, axes = plt.subplots(4, 1, figsize=(6, 14), sharex=True)
fig.patch.set_facecolor('#f7f7f7')

for ci, cond in enumerate(CONDITIONS):
    ax = axes[ci]
    ax.set_facecolor('white')
    ax.axhline(0, color='gray', ls=':', lw=0.8, alpha=0.4)

    for cue, col in [('CUED', CUED_COL), ('UNCUED', UNCUED_COL)]:
        r = cells[(cond, cue)]
        g = r['grouped']

        # Bootstrap CI per duration bin
        rng = np.random.default_rng(42)
        sub = df[(df['SwapType']==cond)&(df['Cond']==cue)]
        for _, row in g.iterrows():
            d_sub = sub[sub['dur_bin']==int(row['dur_ms'])]['err_rad'].values
            if len(d_sub) < 3:
                continue
            bs = [mean_R(rng.choice(d_sub, len(d_sub), replace=True)) for _ in range(500)]
            lo, hi = np.percentile(bs, [16, 84])  # ±1 SD equivalent
            ax.plot([row['dur_ms'], row['dur_ms']], [lo, hi],
                    color=col, lw=1.2, alpha=0.5, zorder=2)

        ax.scatter(g['dur_ms'], g['R'], s=g['n']*4,
                   color=col, alpha=0.9, zorder=3,
                   label=f'{cue} (n={int(g["n"].sum())})')
        # Connect dots
        ax.plot(g['dur_ms'], g['R'], color=col, lw=1.0, alpha=0.4, zorder=2)

    ax.set_xscale('log')
    ax.set_ylim(-0.05, 1.0)
    ax.set_xlim(15, 400)
    ax.set_ylabel('Mean Resultant Length  R̄', fontsize=9)
    ax.set_title(COND_LABELS[cond], fontsize=10, fontweight='bold')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.legend(fontsize=7, loc='upper left')

axes[-1].set_xlabel('Duration (ms)', fontsize=10)
fig.suptitle('SubfieldSwap Ap35 — Precision (R̄) vs Duration\n'
             'n=1026 (2 sessions). Error bars = ±1 SD bootstrap.',
             fontsize=10, fontweight='bold', y=1.01)
plt.tight_layout()

OUT = '/Users/genestoner1/Projects/ObjectBasedAttention/VRDots/Agents/SwapPilot/Figures/threshold_precision_ap35.png'
plt.savefig(OUT, dpi=160, bbox_inches='tight')
plt.savefig(OUT.replace('.png','.pdf'), bbox_inches='tight')
print(f'\nSaved: {OUT}')
