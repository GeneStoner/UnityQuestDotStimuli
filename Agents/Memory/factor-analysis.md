---
name: Three-Factor Analysis Framework — DepthSwapCtrl and DepthParam
description: Three-factor framework (dot cueing / depth-field match / translation depth) with condition coding, factor assignments for all 12 conditions, and DepthParam parametric results
type: project
---

## Three Factors

| # | Name | Variable | Definition |
|---|------|----------|------------|
| 1 | Dot cueing | `cued` | Delayed-onset dots translate (CUED=1) vs not (UNCUED=0) |
| 2 | Depth-field cueing | `depth_field_cued` | Coherent translator is in the SAME depth plane as delayed-onset field at trial onset (1) vs different plane (0) |
| 3 | Depth field | `ctf` (cued_trans_far) | Coherent translator is in Far plane (1) vs Near plane (0) during translation |

## Condition Mapping

| Cued | Swap | dfc | ctf | Meaning |
|------|------|-----|-----|---------|
| CUED | N, ZdB | 1 | delay_far | Delayed dots translate AND stay in onset plane |
| CUED | ZdA | 0 | 1-delay_far | Delayed dots translate but moved OUT of onset plane |
| UNCUED | N, ZdB | 0 | 1-delay_far | Non-delayed dots translate in opposite plane |
| UNCUED | ZdA | 1 | delay_far | Non-delayed dots translate, moved INTO delayed-onset plane |

## Coding Logic

```python
# delay_far = int(DelayedFieldDepth == 'F')
# ctf (depth of coherent translator during translation):
if is_cued:
    ctf = (1 - delay_far) if swap == 'ZdA' else delay_far
else:
    ctf = delay_far if swap == 'ZdA' else (1 - delay_far)
# depth_field_cued:
depth_field_cued = int(ctf == delay_far)
```

## Results — Final Pilot (all sessions verified 192/192)

### Master summary (as of 2026-04-01)

| Factor | Binocular (n=768) | Mono R (n=577) | Mono L (n=576) | All mono (n=1153) |
|--------|-------------------|----------------|----------------|-------------------|
| 1. Dot cueing | +16.4pp *** | +8.4pp * | +4.2pp n.s. | +6.3pp * |
| 2. Depth-field cueing | +6.0pp † | +3.6pp n.s. | +7.6pp † | +5.6pp † |
| 3. Far vs Near | +10.7pp ** | −2.2pp n.s. | +1.4pp n.s. | −0.4pp n.s. |

Sessions:
- Binocular: 260330_1853, 260331_0621, 260401_1313, 260401_1349 (4 sessions, n=768)
- Mono R-eye (L closed): 260330_2012, 260331_1530, 260401_1541 (3 sessions, n=577)
- Mono L-eye (R closed): 260331_1705, 260331_1734, 260401_1705 (3 sessions, n=576)

### Binocular by swap condition
| Swap | CUED | UNCUED | Δ | p |
|------|------|--------|---|---|
| N | 55.5% | 42.2% | +13.3pp | * |
| ZdA | 48.4% | 32.8% | +15.6pp | * |
| ZdB | 55.5% | 35.2% | +20.3pp | ** |

### All mono by swap condition
| Swap | CUED | UNCUED | Δ | p |
|------|------|--------|---|---|
| N | 46.9% | 39.6% | +7.3pp | n.s. |
| ZdA | 34.4% | 33.3% | +1.0pp | n.s. |
| ZdB | 45.3% | 34.7% | +10.6pp | * |

## Interpretation

- **Factor 1 (dot cueing)**: strongest; survives monocularly (*) but attenuated (+16pp → +6pp)
- **Factor 2 (depth-field cueing)**: † binocular, † in L-eye mono, † all mono pooled; R-eye sessions noisier (floaters)
- **Factor 3 (Far vs Near)**: ** binocular, entirely absent monocularly — purely stereoscopic
- **ZdA collapses monocularly** (+1pp n.s.); ZdB survives (*) — key dissociation implicating depth-plane change of cued translator specifically
- **ZdB > N binocularly**: depth-grouping benefit, not merely absence of disruption

## Logistic regression (binocular)
Dominant terms: `far` (OR=0.15, ***) and `cued:far` (OR=10.4, ***) in swap-type model.
Mechanistic model (`cued × far × ctf`): only `far` (**) and `cued:far` (**) significant — `ctf` adds nothing independent because it's collinear with (swap, far).

---

## CRITICAL LABELING TRAP (all depth conditions)

"Near/Far" in condition labels refers to the depth of the **delayed (Field B) field**, NOT the translating field.

| VRDots label | What actually translates | F3 |
|---|---|---|
| CUED Near | Near (Field B stays put) | Near |
| **UNCUED Near** | **Far** (Field A = opposite depth) | **Far** |
| CUED Far | Far (Field B stays put) | Far |
| **UNCUED Far** | **Near** (Field A = opposite depth) | **Near** |

The "Near reversal" seen in old analyses (CUED Near < UNCUED Near) was an artifact of comparing across different F3 levels. When F3 is held constant, CUED > UNCUED at all depths and all swaps.

---

## Factor assignments — all 12 N/ZdA/ZdB conditions

Full reference: `Agents/Literature/factor_labeled_trajectories.md`
Visual reference: `Agents/Figures/factor_labeled_trajectories.png`

| Swap | Condition | F1 | F2 | F3 |
|------|-----------|----|----|-----|
| N | CUED Near | CUED | SAME | Near |
| N | UNCUED Near | UNCUED | DIFF | **Far** |
| N | CUED Far | CUED | SAME | Far |
| N | UNCUED Far | UNCUED | DIFF | **Near** |
| ZdA | CUED Near | CUED | **DIFF** | **Far** |
| ZdA | UNCUED Near | UNCUED | **SAME** | **Near** |
| ZdA | CUED Far | CUED | **DIFF** | **Near** |
| ZdA | UNCUED Far | UNCUED | **SAME** | **Far** |
| ZdB | CUED Near | CUED | SAME | Near |
| ZdB | UNCUED Near | UNCUED | DIFF | **Far** |
| ZdB | CUED Far | CUED | SAME | Far |
| ZdB | UNCUED Far | UNCUED | DIFF | **Near** |

**Key**: ZdB has IDENTICAL factor assignments to N (swapping non-coherent companions S1↔S3 doesn't change which coherent dot translates at which depth). ZdA flips both F2 and F3 for every condition (coherent translator S0↔S2 moves to opposite plane).

---

## DepthParam — Parametric depth results (2026-04-02, n=32/cell, single sessions)

Experiment: N condition only, R/G balanced, 4 depth separations. Data file: `Agents/Literature/depthparam_results.md`. Theory: `Agents/Literature/depth_ior_hypothesis.md`.

### Raw 4-cell table (Near/Far = depth of delayed field)
| Cell | 0.03m | 0.05m | 0.10m | 0.15m |
|------|-------|-------|-------|-------|
| CUED Far | 90.6% *** | 84.4% *** | 84.4% *** | 84.4% *** |
| UNCUED Near | 50.0% n.s. | 68.8% * | 75.0% ** | 75.0% ** |
| CUED Near | 62.5% n.s. | 59.4% n.s. | 53.1% n.s. | 50.0% n.s. |
| UNCUED Far | 43.8% n.s. | 37.5% n.s. | 37.5% n.s. | 28.1% * |

### Reframed by translating field depth (F3) — correct comparison
| Translation depth | Cued | Uncued | Cueing Δ |
|---|---|---|---|
| Far (CUED Far vs UNCUED Near) | 84–91% | 50–75% | +9 to +41pp ✓ |
| Near (CUED Near vs UNCUED Far) | 50–62% | 28–44% | +6 to +22pp ✓ |

Both cueing effects are positive at all depths once F3 is held constant.

### Parametric trends
- **Far translation (cued)**: depth-invariant at ~84–91% (ceiling)
- **Far translation (uncued)**: rises with depth 50%→75% (gradient migration progressively complete)
- **Near translation (cued)**: falls with depth 62%→50% (gradient increasingly overrides Near cue)
- **Near translation (uncued)**: falls with depth 44%→28% (Far gradient strengthens, Near depleted)
- **Near cueing crossover**: positive at 0.03m (+12.5pp n.s.) → negative at 0.05m (−9.4pp). Crossover ~0.035–0.045m, maps to stereoacuity threshold at 2m.

### Gradient migration account
Far-biased attention gradient (Parks & Corballis 2006; Caziot et al. 2023) sets Far as default attended depth. Near cue captured but gradient pulls attention back to Far during 293ms delay. At 0.03m gradient is weak → migration incomplete. At 0.05m+ → migration complete by tStart. IOR ruled out: same SOA produces max positive cueing in 2D paradigm (ongoing motion maintains engagement, no blank ISI, so IOR doesn't develop).
