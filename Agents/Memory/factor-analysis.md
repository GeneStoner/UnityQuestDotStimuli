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

## Results (marginal chi-squares, all sessions verified 192/192)

### Binocular (260330_1853 + 260331_0621, n=384)
| Factor | Level A | Level B | Δ | p |
|--------|---------|---------|---|---|
| 1. Dot cueing | CUED 52.1% | UNCUED 32.3% | +19.8pp | *** |
| 2. Depth-field cueing | same plane 48.4% | diff plane 35.9% | +12.5pp | * |
| 3. Depth field | Far 46.9% | Near 37.5% | +9.4pp | † |

### Monocular (260330_2012, n=193, L eye closed / R eye active — floaters may affect quality)
| Factor | Level A | Level B | Δ | p |
|--------|---------|---------|---|---|
| 1. Dot cueing | CUED 39.6% | UNCUED 26.8% | +12.8pp | † |
| 2. Depth-field cueing | same 37.5% | diff 28.9% | +8.6pp | n.s. |
| 3. Depth field | Far 32.0% | Near 34.4% | −2.4pp | n.s. |

### All sessions combined (n=577)
| Factor | Level A | Level B | Δ | p |
|--------|---------|---------|---|---|
| 1. Dot cueing | CUED 47.9% | UNCUED 30.4% | +17.5pp | *** |
| 2. Depth-field cueing | same 44.8% | diff 33.6% | +11.2pp | ** |
| 3. Depth field | Far 41.9% | Near 36.5% | +5.4pp | n.s. |

## Interpretation

- **Factor 1 (dot cueing)**: strongest and most reliable effect; marginal monocularly
- **Factor 2 (depth-field cueing)**: binocular * → monocular * (survives with n=769 pooled)
- **Factor 3 (depth field absolute)**: binocular †, entirely absent monocularly — purely stereoscopic

## Monocular sessions (as of 2026-03-31)
- R-eye (L closed): 260330_2012 + 260331_1530, n=385
- L-eye (R closed): 260331_1705 + 260331_1734, n=384
- All mono pooled: n=769

## Master summary (binocular n=384 vs all mono n=769)
| Factor | Binocular | All mono |
|--------|-----------|----------|
| 1. Dot cueing (CUED vs UNCUED) | +19.8pp *** | +7.1pp * |
| 2. Depth-field cueing (same vs diff) | +12.5pp * | +7.1pp * |
| 3. Depth plane (Far vs Near) | +9.4pp † | +1.2pp n.s. |

Factors 1 and 2 both survive monocularly. Factor 3 is entirely stereoscopic.

## Logistic regression (binocular)
Dominant terms: `far` (OR=0.15, ***) and `cued:far` (OR=10.4, ***) in swap-type model.
Mechanistic model (`cued × far × ctf`): only `far` (**) and `cued:far` (**) significant — `ctf` adds nothing independent because it's collinear with (swap, far).
