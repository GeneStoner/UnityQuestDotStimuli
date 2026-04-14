#!/usr/bin/env python3
"""
session_260413_analysis.py

Factor analysis for session 260413_1406 (DecoupledDots_005m_v2, n=512).

Factors:
  F1  Dot cueing:       CUED vs UNCUED
  F2  Depth disruption: N vs Z (in CUED arm)
  F3  Color:            N vs C (in CUED arm)
  F4  Near vs Far:      DelayedFieldDepth (translating field depth)

Also reports response direction bias on wrong trials by condition.
"""

import csv, math, os
import numpy as np
from scipy.stats import chi2_contingency

DATA = "/tmp/quest_pull12/vr_dots_session_260413_1406.tsv"

# ── Stats helpers ──────────────────────────────────────────────────────────────

def is_correct(td, rd):
    d = (float(rd) - float(td) + 360) % 360
    return (360 - d if d > 180 else d) <= 22.5

def pct(k, n):
    return k / n * 100 if n > 0 else float('nan')

def chi2_p(k1, n1, k2, n2):
    if n1 == 0 or n2 == 0:
        return float('nan'), float('nan')
    table = [[k1, n1 - k1], [k2, n2 - k2]]
    chi2v, pval, _, _ = chi2_contingency(table, correction=False)
    return chi2v, pval

def stars(p):
    if math.isnan(p): return '?'
    return ('***' if p < .001 else '**' if p < .01 else '*' if p < .05
            else '†' if p < .1 else 'n.s.')

# ── Load ───────────────────────────────────────────────────────────────────────

rows = []
with open(DATA, newline='') as f:
    for r in csv.DictReader(f, delimiter='\t'):
        if not r.get('TransDeg','').strip() or not r.get('RespDeg','').strip():
            continue
        if r.get('EndKey','') in ('timeout','skip','requeue'):
            continue
        cond  = r['Cond']
        swap  = r['SwapType']
        depth = r['DelayedFieldDepth']   # N or F (translating field depth)
        td    = float(r['TransDeg'])
        rd    = float(r['RespDeg'])
        corr  = int(is_correct(td, rd))
        rows.append(dict(cond=cond, swap=swap, depth=depth,
                         td=td, rd=rd, correct=corr))

print(f"Session: 260413_1406   n={len(rows)}")
print(f"Experiment: DecoupledDots_005m_v2")
print()

# ── Factor summaries ───────────────────────────────────────────────────────────

def cell(filt):
    sub = [r for r in rows if filt(r)]
    k = sum(r['correct'] for r in sub)
    n = len(sub)
    return k, n

print("="*60)
print("FACTOR RESULTS")
print("="*60)

# F1: Dot cueing
k_cn, n_cn = cell(lambda r: r['cond']=='CUED'   and r['swap']=='N')
k_un, n_un = cell(lambda r: r['cond']=='UNCUED' and r['swap']=='N')
chi2v, pval = chi2_p(k_cn, n_cn, k_un, n_un)
print(f"\nF1  Dot cueing (N condition only)")
print(f"    CUED_N  = {pct(k_cn,n_cn):.1f}%  (k={k_cn}, n={n_cn})")
print(f"    UNCUED_N= {pct(k_un,n_un):.1f}%  (k={k_un}, n={n_un})")
print(f"    Δ = {pct(k_cn,n_cn)-pct(k_un,n_un):+.1f}pp  χ²={chi2v:.2f}  p={pval:.4f}  {stars(pval)}")

# F2: Depth disruption (CUED arm: N vs Z)
k_cz, n_cz = cell(lambda r: r['cond']=='CUED' and r['swap']=='Z')
chi2v, pval = chi2_p(k_cn, n_cn, k_cz, n_cz)
print(f"\nF2  Depth disruption (CUED arm: N vs Z)")
print(f"    CUED_N  = {pct(k_cn,n_cn):.1f}%  (k={k_cn}, n={n_cn})")
print(f"    CUED_Z  = {pct(k_cz,n_cz):.1f}%  (k={k_cz}, n={n_cz})")
print(f"    Δ = {pct(k_cn,n_cn)-pct(k_cz,n_cz):+.1f}pp  χ²={chi2v:.2f}  p={pval:.4f}  {stars(pval)}")

# F3: Color (CUED arm: N vs C)
k_cc, n_cc = cell(lambda r: r['cond']=='CUED' and r['swap']=='C')
chi2v, pval = chi2_p(k_cn, n_cn, k_cc, n_cc)
print(f"\nF3  Color (CUED arm: N vs C)")
print(f"    CUED_N  = {pct(k_cn,n_cn):.1f}%  (k={k_cn}, n={n_cn})")
print(f"    CUED_C  = {pct(k_cc,n_cc):.1f}%  (k={k_cc}, n={n_cc})")
print(f"    Δ = {pct(k_cn,n_cn)-pct(k_cc,n_cc):+.1f}pp  χ²={chi2v:.2f}  p={pval:.4f}  {stars(pval)}")

# F4: Near vs Far (N condition, both arms)
k_far, n_far = cell(lambda r: r['swap']=='N' and r['depth']=='F')
k_near, n_near = cell(lambda r: r['swap']=='N' and r['depth']=='N')
chi2v, pval = chi2_p(k_far, n_far, k_near, n_near)
print(f"\nF4  Near vs Far (N condition, both arms)")
print(f"    Far  = {pct(k_far,n_far):.1f}%   (k={k_far}, n={n_far})")
print(f"    Near = {pct(k_near,n_near):.1f}%  (k={k_near}, n={n_near})")
print(f"    Δ = {pct(k_far,n_far)-pct(k_near,n_near):+.1f}pp  χ²={chi2v:.2f}  p={pval:.4f}  {stars(pval)}")

# F1×F2 interaction
k_uz, n_uz = cell(lambda r: r['cond']=='UNCUED' and r['swap']=='Z')
f1_n  = pct(k_cn,n_cn) - pct(k_un,n_un)
f1_z  = pct(k_cz,n_cz) - pct(k_uz,n_uz)
print(f"\nF1×F2 interaction")
print(f"    Dot-cueing effect in N:  {f1_n:+.1f}pp")
print(f"    Dot-cueing effect in Z:  {f1_z:+.1f}pp")
print(f"    Interaction:             {f1_n - f1_z:+.1f}pp")

# ── Full condition × depth table ───────────────────────────────────────────────

print()
print("="*60)
print("FULL CONDITION × DEPTH TABLE")
print("="*60)
print(f"\n{'Cond':<8} {'Swap':<5} {'Depth':<6} {'%corr':>7} {'k':>4} {'n':>4}")
print("-"*38)
for cond in ['CUED','UNCUED']:
    for swap in ['N','C','Z','CZ']:
        for depth in ['N','F']:
            k, n = cell(lambda r, c=cond, s=swap, d=depth:
                        r['cond']==c and r['swap']==s and r['depth']==d)
            if n == 0: continue
            print(f"  {cond:<8} {swap:<5} {'Near' if depth=='N' else 'Far':<6} "
                  f"{pct(k,n):>6.1f}%  {k:>3}  {n:>3}")

# ── Response direction bias on wrong trials ───────────────────────────────────

print()
print("="*60)
print("RESPONSE DIRECTION BIAS ON WRONG TRIALS")
print("(expected ~14.3% per direction for uniform 7-direction distribution)")
print("="*60)

for cond in ['CUED','UNCUED']:
    print(f"\n  {cond}:")
    for swap in ['N','C','Z','CZ']:
        sub = [r for r in rows if r['cond']==cond and r['swap']==swap and r['correct']==0]
        if len(sub) < 3:
            continue
        up90   = sum(1 for r in sub if round(r['rd']/45)*45 % 360 == 90)  / len(sub)
        down270= sum(1 for r in sub if round(r['rd']/45)*45 % 360 == 270) / len(sub)
        acc_all = cell(lambda r, c=cond, s=swap: r['cond']==c and r['swap']==s)
        print(f"    {swap:<3}  n_wrong={len(sub):>3}  acc={pct(*acc_all):>5.1f}%  "
              f"wrong→90°(up)={up90:.1%}  wrong→270°(dn)={down270:.1%}")

    # Also by depth for Z
    print(f"\n  {cond} Z, by depth:")
    for depth in ['N','F']:
        sub = [r for r in rows if r['cond']==cond and r['swap']=='Z'
               and r['depth']==depth and r['correct']==0]
        if len(sub) < 3: continue
        up90 = sum(1 for r in sub if round(r['rd']/45)*45 % 360 == 90) / len(sub)
        label = 'Near' if depth=='N' else 'Far'
        print(f"    Z {label}  n_wrong={len(sub):>3}  wrong→90°(up)={up90:.1%}")
