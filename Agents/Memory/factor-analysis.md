---
name: DepthSwapCtrl Factor Analysis Framework
description: Three-factor marginal chi-square and logistic regression framework for DepthSwapCtrl data, with condition coding
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
