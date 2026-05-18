import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy import stats

DATA = '/Users/genestoner1/Projects/ObjectBasedAttention/VRDots/Agents/Data'
OUT  = '/tmp/catek_noswap_mc.png'

def load(sess):
    df = pd.read_csv(f'{DATA}/vr_dots_session_{sess}.tsv', sep='\t')
    df['Correct'] = (df['RespDeg'] == df['TransDeg']).astype(float)
    m = df['SwapType'] == 'Db'
    df.loc[m, 'Cond'] = df.loc[m, 'Cond'].map({'CUED':'UNCUED','UNCUED':'CUED'})
    return df

all3 = pd.concat([load(s) for s in ['260427_0707','260427_1003','260427_1217']],
                 ignore_index=True)

def cue_stats(df, swap):
    sub = df[df['SwapType'] == swap]
    c   = sub[sub['Cond']=='CUED']['Correct']
    u   = sub[sub['Cond']=='UNCUED']['Correct']
    delta = (c.mean() - u.mean()) * 100
    rng = np.random.default_rng(42)
    bd  = (rng.choice(c.values,(5000,len(c)),replace=True).mean(1) -
           rng.choice(u.values,(5000,len(u)),replace=True).mean(1)) * 100
    ci_lo, ci_hi = np.percentile(bd, [2.5, 97.5])
    pp = (c.sum()+u.sum())/(len(c)+len(u))
    se = np.sqrt(pp*(1-pp)*(1/len(c)+1/len(u)))
    p  = 2*(1-stats.norm.cdf(abs((c.mean()-u.mean())/se)))
    return dict(delta=delta, ci_lo=ci_lo, ci_hi=ci_hi, p=p,
                n=len(c)+len(u), nc=len(c), nu=len(u),
                cued=c.mean()*100, uncued=u.mean()*100)

def sig(p):
    if p<0.001: return '***'
    if p<0.01:  return '**'
    if p<0.05:  return '*'
    if p<0.1:   return '†'
    return 'n.s.'

rN  = cue_stats(all3, 'N')
rDb = cue_stats(all3, 'Db')

CONDITIONS = [
    ('No Swap',           rN,  '#2ca02c'),
    ('Motion/Color Swap', rDb, '#d62728'),
]

fig, ax = plt.subplots(figsize=(5, 5))
fig.patch.set_facecolor('white')

CHANCE = 12.5
xs = np.arange(len(CONDITIONS))

for xi, (label, r, color) in enumerate(CONDITIONS):
    err_lo = r['delta'] - r['ci_lo']
    err_hi = r['ci_hi'] - r['delta']
    ax.bar(xi, r['delta'], 0.5, color=color, alpha=0.82,
           yerr=[[err_lo],[err_hi]], capsize=6,
           error_kw={'lw':1.5, 'color':'#333'})
    stars = sig(r['p'])
    yann  = r['delta'] + err_hi + 0.8
    ax.text(xi, yann, f"{r['delta']:+.1f} pp\n{stars}",
            ha='center', va='bottom', fontsize=10, fontweight='bold', color=color)
    ax.text(xi, -3.5, f"n = {r['n']}", ha='center', va='top', fontsize=8.5, color='#444')

ax.axhline(0, color='#888', lw=1)
ax.set_xticks(xs)
ax.set_xticklabels([c[0] for c in CONDITIONS], fontsize=11)
ax.set_ylabel('Cueing effect  (CUED − UNCUED, pp)', fontsize=10)
ax.set_ylim(-7, 35)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.set_title('VRDots — Catek Replication\nAp 1.65° · 43 dots/field · 80 ms  (3 sessions)',
             fontsize=10.5, fontweight='bold', pad=10)

plt.tight_layout()
plt.savefig(OUT, dpi=160, bbox_inches='tight', facecolor='white')
print(f'Saved: {OUT}')
print(f"\nNo Swap:           {rN['delta']:+.1f}pp {sig(rN['p'])}  "
      f"(CUED={rN['cued']:.1f}%  UNCUED={rN['uncued']:.1f}%  n={rN['n']}  p={rN['p']:.4f})")
print(f"Motion/Color Swap: {rDb['delta']:+.1f}pp {sig(rDb['p'])}  "
      f"(CUED={rDb['cued']:.1f}%  UNCUED={rDb['uncued']:.1f}%  n={rDb['n']}  p={rDb['p']:.4f})")
