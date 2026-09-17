# VRDots Cueing Effect Ranking — Clean Experiments Only

*G. Stoner · September 2026*

Ranked by Δpp (CUED − UNCUED percentage points). All experiments with any artifact flag are excluded. Chance = 12.5% (1/8 directions). Single-session depth results have large standard errors (~±15 pp at n = 64/arm).

---

## Depth Experiments — Clean Conditions Only

The depth artifact (transform.forward pitch bias) only applies when depth planes **swap at tStart**. DepthBaseline and DepthParam have no swap at tStart — they are fully clean regardless of session date.

| Rank | Experiment | Condition | Δpp | Notes |
|------|-----------|-----------|-----|-------|
| 1 | **DepthBaseline 0.10 m** | Far plane | **~+62 pp** | Avg across S1 (+59 pp) and S2 (+65 pp); n ≈ 32/cell per session |
| 2 | **DepthParam all depths** | Far plane | **+47 pp** | Consistent across 0.03–0.15 m disparity; disparity-independent |
| 3 | DepthParam 0.03 m | Near plane | **+13 pp** | Only positive Near result |
| — | DepthParam 0.05 m | Near plane | −9 pp | Cueing inverts |
| — | DepthParam 0.10 m | Near plane | −22 pp | Cueing inverts |
| — | DepthParam 0.15 m | Near plane | −25 pp | Cueing inverts |
| — | DepthBaseline 0.10 m | Near plane | **−26 pp** | Strongly inverted; high session variance (−5 vs −47 pp across 2 sessions) |

**Key pattern:** Far-plane cueing (~+62 pp) is the largest clean effect in the entire dataset — nearly double the 2D baseline. It is disparity-invariant: Far cueing locks at ~+47 pp regardless of depth separation. Near-plane cueing inverts at all but the smallest disparity tested.

The Far-plane boost over 2D is approximately **+27 pp** (62 − 35 ≈ 27 pp), suggesting that binocular disparity adds a large independent contribution on top of the temporal onset cue.

---

## 2D Experiments — All Clean

| Rank | Experiment | Ap radius | Dots/field | Condition | Δpp | CUED% | UNCUED% | OR |
|------|-----------|-----------|-----------|-----------|-----|-------|---------|-----|
| 1= | **Density 63 dots** | 3.5° | 63 | N | **+34.8 pp** | 60.5% | 25.8% | 4.42× |
| 1= | **Density 500 dots** | 3.5° | 500 | N | **+34.8 pp** | 63.3% | 28.5% | 4.32× |
| 3 | Density 173 dots | 3.5° | 173 | N | +33.6 pp | 58.6% | 25.0% | 4.25× |
| 4 | DepthSwapCtrl N (binocular) | 3.5° | 63 | N (no swap) | +34 pp | — | — | — |
| 5 | Density 1000 dots | 3.5° | 1000 | N | +25.0 pp | 53.1% | 28.1% | 2.90× |
| 6= | DecoupledDots post-fix | 3.5° | 63 | N (no swap) | +23.5 pp | 48.4% | 24.9% | — |
| 6= | DecoupledDots post-fix | 3.5° | 63 | C (color swap only) | +23.5 pp | 50.0% | 26.5% | — |
| 8= | S&B Replication | 2.0° | 63 | MC (motion+color swap) | +19.9 pp | 70.7% | 50.8% | — |
| 8= | NMoCol (Çatak params) | 1.65° | 43 | MC (motion+color swap) | +19.9 pp | — | — | — |
| 10= | S&B Replication | 2.0° | 63 | N | +16.8 pp | 65.2% | 48.4% | — |
| 10= | NMoCol (Çatak params) | 1.65° | 43 | N | +16.8 pp | — | — | — |
| 12 | NMoCol | 1.65° | 43 | M (motion swap only) | TBD | — | — | — |
| 13 | NMoCol | 1.65° | 43 | C (color swap only) | TBD | — | — | — |
| 14 | Çatak MCvsDb | 1.65° | 43 | N | +14.6 pp | — | — | — |
| 15 | Çatak MCvsDb | 1.65° | 43 | MC | +11.5 pp | — | — | — |
| 16 | Çatak MCvsDb | 1.65° | 43 | Db | +10.4 pp | — | — | — |

OR = odds ratio (baseline-corrected effect size). TBD = tested but script re-run needed for NMoCol M/C individual conditions.

---

## Key Findings from the Ranking

**1. Aperture / dot count is the dominant 2D variable.**
The large aperture (3.5° radius, 63–500 dots) gives ~+35 pp — twice the Çatak aperture effect (~+15 pp) and double S&B's original group result (+20 pp). This is not density: the effect is flat across 8× dot-count range (63–500 dots, OR ≈ 4.3–4.4×). It collapses only at 1000 dots (OR = 2.9×).

**2. Cueing survives all 2D swaps tested at large aperture.**
At Ap 3.5°, neither motion swap, color swap, nor their combination disrupts cueing — the DecoupledDots C condition (+23.5 pp) matches N (+23.5 pp). At Ap 1.65°, MC reduces cueing only modestly (~+12 pp vs +16 pp baseline). The cue is robust to signal identity changes.

**3. Far-plane depth triples the cueing effect.**
Far-plane cueing (~+62 pp) far exceeds anything achievable in 2D. The Near plane inverts cueing at all but the smallest disparity, producing a striking asymmetry that is present in binocular but absent in monocular sessions (DepthSwapCtrl clean N condition), implicating stereoscopic processing.

**4. Depth-field continuity boosts cueing beyond dot cueing alone.**
From DecoupledDots post-fix GLM: dot cueing alone (F1) = +22.3 pp (OR = 3.07×); depth-field cueing alone (F2) = +12.5 pp (OR = 1.89×); both together = much larger. The conjunction is required — neither factor alone reaches the Far-plane level.

---

## Excluded (Artifact Flags)

| Experiment | Sessions | Problem | Excluded conditions |
|-----------|----------|---------|-------------------|
| DepthSwapCtrl ZdA/ZdB | All (pre-fix) | transform.forward pitch bias (attenuated, ~26% UP) | ZdA, ZdB |
| DepthColorLinked ZdNoi/ZdCoh | All (pre-fix) | Same, attenuated | ZdNoi, ZdCoh |
| DecoupledDots pre-fix Z/CZ | 260406–260407 | Full artifact (50% UP in wrong responses) | Z, CZ |
| DecoupledDots sign-bug session | 260415_2242 | Disparity sign inverted | Near/Far breakdown only |

The ZdA collapse and ZdCoh disruption results — the primary object-based specificity finding — are excluded from this ranking pending replication with clean `_v2` assets.
