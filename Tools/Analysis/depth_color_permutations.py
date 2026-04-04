#!/usr/bin/env python3
"""
depth_color_permutations.py
All trial-type permutations (excluding translation direction) for the
ZdCoh + depth-color experiment, with factor assignments.

Design variables (4 binary = 16 trial types):
  Cond      : CUED | UNCUED
  DFD       : N | F    (DelayedFieldDepth — depth plane of Field B, the delayed field)
  NearColor : R | G    (which color is assigned to the Near plane; Far gets the other)
  RotCfg    : 0 | 1    (0 = Field B delayed CCW; 1 = Field B delayed CW)

Derived analysis variables:
  TransDepth  : depth plane of the translating field  (N | F)
  TransColor  : color of the translating field PRE-swap  (R | G)
  TransRot    : rotation of the translating field  (CW | CCW)
  CuedColor   : color of the DELAYED (onset-cued) field  (R | G)
  CuedRot     : rotation of the delayed field  (CW | CCW)

Factor assignments:
  F1 — Dot-field cueing      : CUED vs UNCUED
  F2 — Translator depth      : Near vs Far    (= TransDepth)
  F3 — Translator color      : R vs G          (= TransColor)
  F4 — Translator rotation   : CW vs CCW       (= TransRot)
  F5 — Cued-field color      : R vs G          (= CuedColor)
       [In CUED trials F5 = F3; in UNCUED trials F5 ≠ F3 — the cued field is the non-translator]
"""

import csv, os
from itertools import product

OUT_CSV = os.path.join(os.path.dirname(__file__),
                       'depth_color_permutations.csv')

# ── Helpers ───────────────────────────────────────────────────────────────────
def opp_color(c): return 'G' if c == 'R' else 'R'
def opp_depth(d): return 'F' if d == 'N' else 'N'

# RotCfg convention (matches VRDots logging):
#   0 → Field A = CW non-delayed, Field B = CCW delayed
#   1 → Field A = CCW non-delayed, Field B = CW  delayed
def delayed_rot(rc):  return 'CCW' if rc == 0 else 'CW'
def nondel_rot(rc):   return 'CW'  if rc == 0 else 'CCW'

# ── Generate rows ──────────────────────────────────────────────────────────────
COLS = ['#','Cond','DFD','NearColor','RotCfg',
        'TransDepth','TransColor','TransRot',
        'CuedColor','CuedRot',
        'F1_Cuing','F2_TransDepth','F3_TransColor','F4_TransRot','F5_CuedColor']

rows = []
n = 0
for cond, dfd, nc, rc in product(['CUED','UNCUED'],['N','F'],['R','G'],[0,1]):
    n += 1
    fc = opp_color(nc)

    # TransDepth: translator = delayed (Field B) in CUED, non-delayed in UNCUED
    trans_dep   = dfd if cond == 'CUED' else opp_depth(dfd)
    trans_color = nc  if trans_dep == 'N' else fc
    trans_rot   = delayed_rot(rc) if cond == 'CUED' else nondel_rot(rc)

    # CuedColor / CuedRot: always about the DELAYED field
    cued_color = nc if dfd == 'N' else fc
    cued_rot   = delayed_rot(rc)

    rows.append({
        '#': n,
        'Cond': cond, 'DFD': dfd, 'NearColor': nc, 'RotCfg': rc,
        'TransDepth': trans_dep, 'TransColor': trans_color,
        'TransRot': trans_rot,
        'CuedColor': cued_color, 'CuedRot': cued_rot,
        'F1_Cuing':      cond,
        'F2_TransDepth': trans_dep,
        'F3_TransColor': trans_color,
        'F4_TransRot':   trans_rot,
        'F5_CuedColor':  cued_color,
    })

# ── Print ──────────────────────────────────────────────────────────────────────
W = 4  # column width
hdr1 = (f"{'#':>3}  {'Cond':<8} {'DFD':>{W}} {'NrClr':>{W}} {'Rc':>{W}}  "
        f"{'TrDep':>{W}} {'TrClr':>{W}} {'TrRot':>6}  "
        f"{'CuClr':>{W}} {'CuRot':>6}  "
        f"F1        F2    F3    F4      F5")
print(hdr1)
print('─'*90)

for r in rows:
    line = (f"{r['#']:>3}  {r['Cond']:<8} {r['DFD']:>{W}} {r['NearColor']:>{W}} {r['RotCfg']:>{W}}  "
            f"{r['TransDepth']:>{W}} {r['TransColor']:>{W}} {r['TransRot']:>6}  "
            f"{r['CuedColor']:>{W}} {r['CuedRot']:>6}  "
            f"{r['F1_Cuing']:<10}{r['F2_TransDepth']:<6}{r['F3_TransColor']:<6}"
            f"{r['F4_TransRot']:<8}{r['F5_CuedColor']}")
    print(line)

# ── Save CSV ───────────────────────────────────────────────────────────────────
with open(OUT_CSV, 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=COLS)
    writer.writeheader()
    writer.writerows(rows)
print(f"\nSaved: {OUT_CSV}")

# ── Factor summary ─────────────────────────────────────────────────────────────
print("""
FACTOR SUMMARY
══════════════════════════════════════════════════════════════════════════════
F1  Dot-field cueing    CUED vs UNCUED
      Classic temporal-onset cueing effect.  Does the delayed field's onset
      asymmetry help the observer track the translation?

F2  Translator depth    Near vs Far
      Is it easier to detect Near or Far translation?  Also tests whether
      depth-plane identity (reinforced by color) helps more at one depth.
      NOTE: in this design, TransDepth and TransColor are ORTHOGONAL
      (each depth is equally often R or G across NearColor counterbalancing),
      so depth and color effects ARE separable within the experiment.

F3  Translator color    Red vs Green  (pre-swap color of translating field)
      Does the pre-swap color of the translator matter?
      Directly tests the red/green cueing asymmetry hypothesis
      (DepthSwapCtrl used all-red and showed reduced overall cueing).

F4  Translator rotation CW vs CCW
      Does rotation direction of the translating field affect detectability?
      Generally expected to be null; included for completeness.

F5  Cued-field color    Red vs Green  (color of the delayed field)
      In CUED trials: same as F3 (cued = translator).
      In UNCUED trials: cued field ≠ translator, so F5 ≠ F3.
      Tests whether the observer's attentional bias toward a particular
      color (from delayed-onset learning) affects UNCUED performance
      and the magnitude of the cueing effect.

──────────────────────────────────────────────────────────────────────────────
FACTORS NOT INDEPENDENTLY ANALYZABLE WITHIN THIS EXPERIMENT ALONE:
  Depth-field cueing (old F2 from DepthSwapCtrl): asks "how much is
  due to depth alone?"  Not separable here because color and depth are
  always co-present.  Requires cross-experiment comparison:
    ZdCoh+color  vs  ZdCoh-all-red  → isolates color contribution
    ZdCoh+color  vs  two-color-baseline  → isolates depth contribution

  Post-swap depth / color: perfectly anti-correlated with F2/F3.

POTENTIAL INTERACTION OF INTEREST:
  F1 × F3  (Cueing × TransColor): does cueing differ for Red vs Green
  translators?  Key test of the red/green asymmetry within this experiment.
══════════════════════════════════════════════════════════════════════════════
""")
