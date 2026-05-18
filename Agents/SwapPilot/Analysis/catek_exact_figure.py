import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy import stats

DATA = '/Users/genestoner1/Projects/ObjectBasedAttention/VRDots/Agents/Data'
OUT  = '/tmp/catek_exact_results.png'

# ── load ──────────────────────────────────────────────────────────────────────
def load(sess):
    df = pd.read_csv(f'{DATA}/vr_dots_session_{sess}.tsv', sep='\t')
    df['Correct'] = (df["RespDeg"] == df["TransDeg"]).astype(float)
    # flip Db labels (onset-cued field = non-translating in Db)
    m = df['SwapType'] == 'Db'
    df.loc[m, 'Cond'] = df.loc[m, 'Cond'].map({'CUED':'UNCUED','UNCUED':'CUED'})
    return df

ce1  = load('260427_0707')   # CatekExact session 1
ce2  = load('260427_1003')   # CatekExact session 2
ndb  = load('260427_1217')   # CatekExact_NDb
ce12 = pd.concat([ce1, ce2], ignore_index=True)
all3 = pd.concat([ce1, ce2, ndb], ignore_index=True)

# ── stats helpers ─────────────────────────────────────────────────────────────
def cue_delta(df, swap):
    sub = df[df['SwapType'] == swap]
    if sub.empty: return None
    c = sub[sub['Cond']=='CUED']['Correct']
    u = sub[sub['Cond']=='UNCUED']['Correct']
    if len(c)==0 or len(u)==0: return None
    delta = (c.mean() - u.mean()) * 100
    # bootstrap 95% CI on delta
    rng = np.random.default_rng(42)
    n_boot = 5000
    bc = rng.choice(c.values, (n_boot, len(c)), replace=True).mean(axis=1)
    bu = rng.choice(u.values, (n_boot, len(u)), replace=True).mean(axis=1)
    bd = (bc - bu) * 100
    ci_lo, ci_hi = np.percentile(bd, [2.5, 97.5])
    # two-prop z-test
    nc, hc = len(c), c.sum()
    nu, hu = len(u), u.sum()
    pp = (hc+hu)/(nc+nu)
    se = np.sqrt(pp*(1-pp)*(1/nc+1/nu))
    z  = (c.mean()-u.mean())/se if se>0 else 0
    p  = 2*(1-stats.norm.cdf(abs(z)))
    return dict(delta=delta, ci_lo=ci_lo, ci_hi=ci_hi, p=p,
                nc=nc, nu=nu, cued=c.mean()*100, uncued=u.mean()*100)

def sig(p):
    if p<0.001: return '***'
    if p<0.01:  return '**'
    if p<0.05:  return '*'
    if p<0.1:   return '†'
    return 'n.s.'

SWAPS = ['N','D','Da','Db']
COLORS = {'N':'#2ca02c','D':'#9467bd','Da':'#ff7f0e','Db':'#d62728'}
LABELS = {'N':'N\n(no swap)','D':'D\n(Dots50)','Da':'Da\n(subfield A)','Db':'Db\n(subfield B)'}

DATASETS = [
    ('CatekExact  sessions 1 & 2\n(260427_0707 + 260427_1003)', ce12, ['N','D','Da','Db']),
    ('CatekExact_NDb  session 3\n(260427_1217)', ndb, ['N','Db']),
    ('Combined  (all 3 sessions)\nNDb contributes N & Db only', all3, ['N','D','Da','Db']),
]

fig, axes = plt.subplots(1, 3, figsize=(14, 5.5), sharey=True)
fig.patch.set_facecolor('white')

for ax, (title, df, swaps) in zip(axes, DATASETS):
    xs = np.arange(len(swaps))
    for xi, sw in enumerate(swaps):
        r = cue_delta(df, sw)
        if r is None:
            continue
        color = COLORS[sw]
        err_lo = r['delta'] - r['ci_lo']
        err_hi = r['ci_hi'] - r['delta']
        ax.bar(xi, r['delta'], 0.55, color=color, alpha=0.82,
               yerr=[[err_lo],[err_hi]], capsize=5,
               error_kw={'lw':1.4, 'color':'#333'})
        stars = sig(r['p'])
        yoff = err_hi + 0.8 if r['delta'] >= 0 else -(err_lo + 0.8)
        va = 'bottom' if r['delta'] >= 0 else 'top'
        ax.text(xi, r['delta'] + (err_hi+1.2 if r['delta']>=0 else -(err_lo+1.2)),
                f"{r['delta']:+.1f}pp\n{stars}",
                ha='center', va=va, fontsize=8.5, fontweight='bold', color=color)
        # trial count
        ax.text(xi, -28, f"n={r['nc']+r['nu']}", ha='center', va='top',
                fontsize=7, color='#555')

    ax.axhline(0, color='#888', lw=1)
    ax.set_xticks(xs)
    ax.set_xticklabels([LABELS[s] for s in swaps], fontsize=9)
    ax.set_title(title, fontsize=9.5, fontweight='bold', pad=8)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.set_ylim(-32, 42)

axes[0].set_ylabel('Cueing effect  (CUED − UNCUED, pp)', fontsize=10)
fig.suptitle('CatekExact  —  Ap 1.65° radius · 43 dots/field · 80 ms translation  '
             '[Db labels corrected; chance = 12.5%]',
             fontsize=11, fontweight='bold', y=1.01)
plt.tight_layout()
plt.savefig(OUT, dpi=160, bbox_inches='tight', facecolor='white')
print(f'Saved: {OUT}')

# print summary table
print('\n=== Summary ===')
for title, df, swaps in DATASETS:
    print(f'\n{title}')
    for sw in swaps:
        r = cue_delta(df, sw)
        if r:
            print(f'  {sw}: {r["delta"]:+.1f}pp {sig(r["p"])}  '
                  f'(CUED={r["cued"]:.1f}% UNCUED={r["uncued"]:.1f}%  n={r["nc"]+r["nu"]}  p={r["p"]:.4f})')
