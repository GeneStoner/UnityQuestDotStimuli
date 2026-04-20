#!/usr/bin/env python3
"""
analyze_260415_2242.py

Analysis of session 260415_2242 — first full session with Solution A
(screen-space shader, DotScreenSpace.shader).  DecoupledDots_005m_v2, n=512.

Sections:
  1. Overall accuracy by swap × cond
  2. UP-bias check: direction of wrong responses in Z vs N
  3. Near/Far breakdown
  4. Comparison to prior clean sessions (260413_2051, 260414_0922 Q3+Q4)
  5. Figure: 4-row bar chart (N/C/Z/CZ × CUED/UNCUED) + UP bias panel

Output: Agents/SwapPilot/Figures/decoupled_260415_2242.png
"""

import csv, math, os
import numpy as np
import matplotlib
matplotlib.use('Agg')
matplotlib.rcParams['pdf.fonttype'] = 42
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from scipy.stats import chi2_contingency

SESSION   = '/tmp/quest_pull8/files/vr_dots_session_260415_2242.tsv'
PRIOR_SESSIONS = [
    ('/tmp/quest_pull7/files/vr_dots_session_260413_2051.tsv', None),
    ('/tmp/quest_pull7/files/vr_dots_session_260414_0922.tsv', 263),
]

OUT = os.path.normpath(os.path.join(
    os.path.dirname(__file__),
    '../../Agents/SwapPilot/Figures/decoupled_260415_2242.png'))
os.makedirs(os.path.dirname(OUT), exist_ok=True)

CHANCE = 1/8
SWAPS  = ['N', 'C', 'Z', 'CZ']

# ── Helpers ────────────────────────────────────────────────────────────────────

def is_correct(td, rd):
    d = (float(rd) - float(td) + 360) % 360
    return (360 - d if d > 180 else d) <= 22.5

def resp_dir(td, rd):
    """Return response direction as compass: N/NE/E/SE/S/SW/W/NW."""
    d = (float(rd) + 360) % 360
    idx = int((d + 22.5) / 45) % 8
    return ['E','NE','N','NW','W','SW','S','SE'][idx]

def pct(k, n): return k/n*100 if n > 0 else float('nan')

def wilson_ci(k, n, z=1.96):
    if n == 0: return 0.0, 0.0
    p = k/n; denom = 1 + z**2/n
    c  = (p + z**2/(2*n)) / denom
    hw = z * math.sqrt(p*(1-p)/n + z**2/(4*n**2)) / denom
    return (c-hw)*100, (c+hw)*100

def chi2_p(k1, n1, k2, n2):
    if n1==0 or n2==0: return float('nan')
    try:
        _, pv, _, _ = chi2_contingency([[k1,n1-k1],[k2,n2-k2]], correction=False)
        return pv
    except Exception:
        return float('nan')

def stars(p):
    if p is None or (isinstance(p,float) and math.isnan(p)): return ''
    return '***' if p<.001 else '**' if p<.01 else '*' if p<.05 else '†' if p<.1 else 'n.s.'

def stars_vs_chance(k, n):
    if n == 0: return ''
    z = (k/n - CHANCE) / math.sqrt(CHANCE*(1-CHANCE)/n)
    from math import erf, sqrt
    pv = 2*(0.5*(1+erf(-abs(z)/sqrt(2))))
    return stars(pv)

# ── Load session ───────────────────────────────────────────────────────────────

def load(path, min_trial=None):
    rows = []
    trial_num = 0
    with open(path, newline='') as f:
        for r in csv.DictReader(f, delimiter='\t'):
            if not r.get('TransDeg','').strip() or not r.get('RespDeg','').strip(): continue
            if r.get('EndKey','') in ('timeout','skip','requeue'): continue
            trial_num += 1
            if min_trial and trial_num < min_trial: continue
            correct = is_correct(r['TransDeg'], r['RespDeg'])
            rows.append(dict(
                cond    = r['Cond'],
                swap    = r['SwapType'],
                correct = int(correct),
                resp_dir = resp_dir(r['TransDeg'], r['RespDeg']),
                trans_deg = float(r['TransDeg']),
                near    = r.get('DelayedFieldDepth','') == 'N',
                is_inv  = '_Inv' in r.get('Experiment','') or (
                              r.get('DelayedFieldDepth','') in ('N','F') and
                              int(r.get('RotCfg','0')) >= 2),
            ))
    return rows

# Disparity sign was inverted in this session (shader bug fixed 2026-04-16).
# DelayedFieldDepth='N' was rendered with uncrossed (Far) disparity and vice versa.
# Correct by flipping the near label for the main session only.
rows = load(SESSION)
for r in rows:
    r['near'] = not r['near']
n_total   = len(rows)

# Prior combined clean
prior_rows = []
for path, min_t in PRIOR_SESSIONS:
    prior_rows += load(path, min_t)
n_prior = len(prior_rows)

print(f"\nSession 260415_2242: n={n_total} valid trials")
print(f"Prior clean combined: n={n_prior}")

# ── 1. Accuracy by swap × cond ─────────────────────────────────────────────────

print("\n── Accuracy by swap × cond ──────────────────────────────────────────")
print(f"{'Cell':15s}  {'k/n':>8s}  {'%':>6s}  {'95% CI':>15s}  {'vs chance':>10s}")

results = {}
for swap in SWAPS:
    for cond in ['CUED','UNCUED']:
        sub  = [r for r in rows if r['swap']==swap and r['cond']==cond]
        k, n = sum(r['correct'] for r in sub), len(sub)
        lo, hi = wilson_ci(k, n)
        s = stars_vs_chance(k, n)
        key = (swap, cond)
        results[key] = (k, n)
        print(f"  {swap+' '+cond:13s}  {k:3d}/{n:<3d}  {pct(k,n):6.1f}%"
              f"  [{lo:5.1f}, {hi:5.1f}]  {s:>10s}")

print()
for swap in SWAPS:
    kc, nc = results[(swap,'CUED')]
    ku, nu = results[(swap,'UNCUED')]
    delta  = pct(kc,nc) - pct(ku,nu)
    pv     = chi2_p(kc, nc, ku, nu)
    print(f"  {swap} cueing: {delta:+.1f}pp  {stars(pv)}")

# ── 2. UP bias in wrong responses ──────────────────────────────────────────────

print("\n── UP bias in wrong responses ────────────────────────────────────────")
for swap in ['N','Z']:
    wrong = [r for r in rows if r['swap']==swap and r['correct']==0]
    n_wrong = len(wrong)
    n_up    = sum(1 for r in wrong if r['resp_dir'] == 'N')
    up_pct  = pct(n_up, n_wrong)
    print(f"  {swap}: {n_up}/{n_wrong} wrong responses = UP  ({up_pct:.1f}%)"
          f"  [chance = {100/8:.1f}%]")

# ── 3. Near / Far breakdown ────────────────────────────────────────────────────

print("\n── Near / Far breakdown (N condition only) ───────────────────────────")
for depth_label, is_near in [('Near', True), ('Far', False)]:
    for cond in ['CUED','UNCUED']:
        sub = [r for r in rows
               if r['swap']=='N' and r['cond']==cond and r['near']==is_near]
        k, n = sum(r['correct'] for r in sub), len(sub)
        lo, hi = wilson_ci(k, n)
        s = stars_vs_chance(k, n)
        print(f"  N {cond} {depth_label}: {k}/{n} = {pct(k,n):.1f}%"
              f"  [{lo:.1f}, {hi:.1f}]  {s}")

# ── 4. Comparison to prior clean sessions ─────────────────────────────────────

print("\n── Comparison: 260415_2242 vs prior clean (n=762) ───────────────────")
print(f"{'Cell':15s}  {'New %':>8s}  {'Prior %':>8s}  {'Δ':>6s}")
for swap in SWAPS:
    for cond in ['CUED','UNCUED']:
        k_new, n_new   = results[(swap, cond)]
        sub_p = [r for r in prior_rows if r['swap']==swap and r['cond']==cond]
        k_p, n_p = sum(r['correct'] for r in sub_p), len(sub_p)
        diff = pct(k_new, n_new) - pct(k_p, n_p)
        print(f"  {swap+' '+cond:13s}  {pct(k_new,n_new):6.1f}%   "
              f"{pct(k_p,n_p):6.1f}%   {diff:+5.1f}pp")

# ── 5. Figure ─────────────────────────────────────────────────────────────────

C_CUED   = '#1a3a8b'
C_UNCUED = '#884400'
SWAP_COLORS = {'N':'#444444','C':'#CC6600','Z':'#116688','CZ':'#553388'}

fig = plt.figure(figsize=(11, 8))
fig.patch.set_facecolor('white')
fig.suptitle(
    f'DecoupledDots_005m_v2 · Session 260415_2242 · Solution A (screen-space shader)\n'
    f'n={n_total} valid trials  ·  Wilson 95% CI  ·  χ² vs chance',
    fontsize=10, fontweight='bold', y=0.99)

outer = gridspec.GridSpec(1, 2, wspace=0.35, left=0.08, right=0.97,
                          top=0.90, bottom=0.10)

# ── Left panel: accuracy bars ─────────────────────────────────────────────────
ax = fig.add_subplot(outer[0])

xs_cued   = np.array([0, 2, 4, 6], dtype=float)
xs_uncued = xs_cued + 0.8

for i, swap in enumerate(SWAPS):
    for xs, cond, cc in [(xs_cued, 'CUED', C_CUED), (xs_uncued, 'UNCUED', C_UNCUED)]:
        k, n = results[(swap, cond)]
        p = pct(k, n)
        lo, hi = wilson_ci(k, n)
        ax.bar(xs[i], p, 0.75, color=cc, alpha=0.85, zorder=3, edgecolor='white', lw=0.5)
        ax.errorbar(xs[i], p, yerr=[[p-lo],[hi-p]],
                    fmt='none', color='#222', capsize=4, capthick=1.1, lw=1.2, zorder=4)
        s = stars_vs_chance(k, n)
        ax.text(xs[i], hi+1.2, s, ha='center', va='bottom', fontsize=9,
                fontweight='bold', color='#111')
        ax.text(xs[i], 3, f'n={n}', ha='center', va='bottom',
                fontsize=6.5, color='white', fontweight='bold')

    # cueing bracket
    kc, nc = results[(swap,'CUED')]
    ku, nu = results[(swap,'UNCUED')]
    delta  = pct(kc,nc) - pct(ku,nu)
    pv     = chi2_p(kc, nc, ku, nu)
    xm     = xs_cued[i] + 0.4
    yb     = max(wilson_ci(kc,nc)[1], wilson_ci(ku,nu)[1]) + 4.5
    ax.plot([xs_cued[i], xs_cued[i], xs_uncued[i], xs_uncued[i]],
            [yb-1, yb, yb, yb-1], color='#333', lw=0.9)
    ax.text(xm, yb+0.5, f'Δ={delta:+.1f}pp {stars(pv)}',
            ha='center', va='bottom', fontsize=8, fontweight='bold')

ax.axhline(CHANCE*100, color='#999', lw=1.0, ls='--', zorder=1)
ax.text(6.9, CHANCE*100+0.8, 'Chance', fontsize=7.5, color='#999', va='bottom')
ax.set_xticks(xs_cued + 0.4)
ax.set_xticklabels(SWAPS, fontsize=11)
ax.set_ylabel('Accuracy (%)', fontsize=10)
ax.set_ylim(0, 95)
ax.set_xlim(-0.5, 7.6)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.set_title('Accuracy by swap condition', fontsize=9, pad=6)

from matplotlib.patches import Patch
ax.legend(handles=[Patch(color=C_CUED, label='CUED'),
                   Patch(color=C_UNCUED, label='UNCUED')],
          fontsize=8, frameon=False, loc='upper right')

# ── Right panel: UP bias + comparison ────────────────────────────────────────
ax2 = fig.add_subplot(outer[1])

# UP bias: % of wrong responses that were "up" for N and Z
up_data = []
for swap in SWAPS:
    wrong  = [r for r in rows if r['swap']==swap and r['correct']==0]
    n_w    = len(wrong)
    n_up   = sum(1 for r in wrong if r['resp_dir']=='N')
    up_data.append((swap, n_up, n_w))

xs_up = np.arange(len(SWAPS))
colors_up = [SWAP_COLORS[s] for s in SWAPS]
for i, (swap, n_up, n_w) in enumerate(up_data):
    p  = pct(n_up, n_w)
    lo, hi = wilson_ci(n_up, n_w)
    ax2.bar(xs_up[i], p, 0.6, color=colors_up[i], alpha=0.80, zorder=3,
            edgecolor='white', lw=0.5)
    ax2.errorbar(xs_up[i], p, yerr=[[p-lo],[hi-p]],
                 fmt='none', color='#222', capsize=4, capthick=1.1, lw=1.2, zorder=4)
    ax2.text(xs_up[i], 3, f'{n_up}/{n_w}', ha='center', va='bottom',
             fontsize=7, color='white', fontweight='bold')

ax2.axhline(100/8, color='#999', lw=1.2, ls='--', zorder=1, label='Chance (12.5%)')
ax2.set_xticks(xs_up)
ax2.set_xticklabels(SWAPS, fontsize=11)
ax2.set_ylabel('% of wrong responses = UP', fontsize=9)
ax2.set_ylim(0, 60)
ax2.set_title('UP bias in wrong responses\n(chance = 12.5%)', fontsize=9, pad=6)
ax2.spines['top'].set_visible(False)
ax2.spines['right'].set_visible(False)
ax2.text(3.45, 100/8+1, 'Chance', fontsize=7.5, color='#999', va='bottom')

# Annotate prior Z UP bias for comparison
ax2.annotate('Pre-fix Z UP bias\n~37–50%', xy=(2, 44), fontsize=7,
             color='#cc0000', style='italic',
             arrowprops=dict(arrowstyle='->', color='#cc0000', lw=0.8),
             xytext=(2.7, 50))

fig.text(0.5, 0.02,
         f'Solution A (screen-space shader) · Session 260415_2242 · n={n_total}'
         f'  ·  Prior clean: 260413_2051 + 260414_0922 Q3+Q4 (n={n_prior})',
         ha='center', fontsize=7.5, color='#555')

plt.savefig(OUT, dpi=150, bbox_inches='tight', facecolor='white')
print(f'\nSaved: {OUT}')
