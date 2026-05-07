# Effect Size Metrics for Proportion Data
**VRDots · Density Comparison Analysis · April 2026**

---

## 1. The Problem with Percentage Points

Percentage points (pp) is the most intuitive metric — *CUED% − UNCUED%* — but it has a structural flaw: the scale compresses near 0% and 100%. Equal pp differences do not represent equal underlying effects when overall performance differs.

> **Motivating example:** If UNCUED_VRDots is 50% while UNCUED_Catek is 42%, the "room" above each baseline differs. A +25 pp cueing effect means something different in each case. Log odds and Cohen's *h* both correct for this.

Chance performance on our 8-direction task is 12.5%. The usable scale runs from 12.5% to 100% — 87.5 pp wide. Any comparison of effects across conditions should respect where each condition sits on this scale.

---

## 2. The Candidate Metrics

### 2.1 Percentage Points (pp) — Baseline

**Formula:** `Δpp = p_CUED − p_UNCUED`

**Interpretation:** Absolute shift in proportion correct. The most direct and communicable measure. Report this always — readers expect it. The limitations below are reasons to also report a scale-free metric, not reasons to drop pp.

- **Pro:** Immediately interpretable; maps directly to trial counts; used throughout the literature for this task.
- **Con:** Bounded — a +25 pp effect near the floor (UNCUED ≈ 15%) implies a very different underlying sensitivity change than +25 pp near the middle (UNCUED ≈ 45%).
- **Con:** Cannot be directly compared across conditions with different baselines without adjustment.

---

### 2.2 Cohen's *h* — Arcsine-Stabilized Difference

**Formula:** `h = 2·arcsin(√p_CUED) − 2·arcsin(√p_UNCUED)`

The arcsine (square-root) transformation is the classical variance-stabilizing transformation for proportions. It stretches the scale near 0 and 1 — where binomial variance is smallest — and compresses it near 0.5 — where variance is largest.

- **Pro:** Simple closed-form; no model required; well-validated in the proportions literature; directly comparable across conditions with different baselines.
- **Pro:** Near *p* = 0.5, *h* ≈ pp (no distortion in the most common performance range).
- **Con:** Less intuitive than pp; does not have a direct neurophysiological interpretation.
- **Benchmark:** |*h*| = 0.2 small, 0.5 medium, 0.8 large (Cohen 1988).

---

### 2.3 Log Odds Ratio (LOR) — Scale-Free, Model-Based

**Formula:** `LOR = log[p_C/(1−p_C)] − log[p_U/(1−p_U)]`

The log odds ratio is exactly the coefficient that logistic regression (GLM with logit link) estimates for a binary predictor. It is unbounded, symmetric around 0, and invariant to the baseline probability. Exponentiating gives the *odds ratio* (OR): how many times more likely a correct response is under CUED than UNCUED, holding all else equal.

- **Pro:** Directly aligns with the existing GLM analysis framework — the F1 coefficient is already a LOR. No new model needed.
- **Pro:** Scale-free; unaffected by whether overall performance is 55% or 75%.
- **Pro:** Exponentiated OR has a natural verbal interpretation: "CUED responses were 2.9× more likely to be correct than UNCUED."
- **Con:** Less intuitive for audiences unfamiliar with logistic regression. Requires the caveat that ORs approximate relative risk only when baseline rates are low.

---

### 2.4 Room-to-Ceiling (Normalized Improvement)

**Formula:** `NI = (p_CUED − p_UNCUED) / (1 − p_UNCUED)`

What fraction of the remaining performance headroom above the UNCUED baseline did cueing capture? Bounded [0, 1].

- **Pro:** Intuitive as "efficiency" — how much of the available improvement did cueing deliver?
- **Con:** Does not account for the floor (chance = 12.5%). If UNCUED is near chance, small pp differences look large.
- **Con:** Asymmetric — large NI can result from either a large CUED effect or an unusually depressed UNCUED arm.

---

### 2.5 Room Above Chance (Symmetric Normalization)

**Formula:** `RAC = (p_CUED − p_UNCUED) / (1 − p_chance)` where *p*_chance = 1/8 = 0.125

Normalizes the raw pp effect by the total available scale above chance (0.875). Treats both arms symmetrically and provides a proportion of the theoretically available effect size.

- **Pro:** Uses a principled, task-defined reference; easy to compute; symmetric with respect to both arms.
- **Con:** Does not account for ceiling compression above ~80%; less theoretically grounded than LOR or Cohen's *h*.

---

### 2.6 d' (Signal Detection) — Most Principled, Most Complex

For a multi-alternative forced choice with *M* = 8 options:

```
p_correct = ∫ Φ(x + d')^(M−1) · φ(x) dx    (M = 8)
```

This requires numerical integration (e.g., `scipy.integrate.quad`) to invert. The cueing effect in d' units would be Δd' = d'_CUED − d'_UNCUED.

- **Pro:** Theoretically optimal measure of sensitivity; fully accounts for task structure (8 alternatives, chance = 12.5%); invariant to response criterion.
- **Pro:** Most comparable to the broader psychophysics literature.
- **Con:** Requires numerical computation; assumes equal-variance normal distributions and independent alternatives.
- **Note:** For the range of performance values in our data (40–80%), the approximation `d' ≈ √2 · Φ⁻¹(p)` (from 2AFC) gives a rough but monotone estimate. Full 8AFC d' is ~20–30% larger.

---

## 3. Comparison Table

| Metric | Formula | Scale | Corrects for baseline? | Aligned with GLM? | Complexity |
|---|---|---|---|---|---|
| pp | p_C − p_U | 0–87.5 pp | No | Partial (marginal means) | Trivial |
| Cohen's *h* | 2·arcsin(√p_C) − 2·arcsin(√p_U) | −π to +π | Yes | No | Trivial |
| Log odds ratio | logit(p_C) − logit(p_U) | −∞ to +∞ | Yes | Yes (= F1 coeff) | Trivial |
| Room-to-ceiling | (p_C − p_U)/(1 − p_U) | 0 to 1 | Partially | No | Trivial |
| Room above chance | (p_C − p_U)/(1 − 1/8) | 0 to 1 | Partially | No | Trivial |
| d' (8AFC) | Φ⁻¹ via numerical integration | 0 to ~6 | Yes | Partial | Requires code |

---

## 4. Recommendation for the Density Comparison

> **Primary metric:** Log odds ratio (LOR / OR) from logistic GLM. Already computed by the existing analysis pipeline as the F1 coefficient. Directly comparable across VRDots and Catek sessions regardless of overall accuracy level. Exponentiate for the odds ratio as an interpretable summary.
>
> **Secondary:** Cohen's *h* — simple, well-validated, easy to compute alongside pp with two lines of Python.
>
> **Always report:** Raw pp — readers expect it and it anchors the other measures.
>
> **If overall accuracy differs substantially between conditions:** report all three (pp, *h*, LOR) and note the direction of any discrepancy. Divergence between pp and LOR is itself informative about task dynamics.

---

## 5. Worked Example — Catek Session (n = 512, 2026-04-21)

**Session:** DensityCompare_Catek_v1 · Aperture 3.3° diameter · 43 dots/field · 5.0 dots/sq°

**CUED:** 173/256 = 67.6%  |  **UNCUED:** 108/256 = 42.2%  |  **Chance:** 12.5%

| Metric | Value | Interpretation |
|---|---|---|
| pp | **+25.4 pp** | 67.6 − 42.2 |
| Cohen's *h* | **+0.516** | Medium–large (benchmark: 0.5) |
| Log Odds Ratio | **+1.050** | OR = 2.86× (CUED 2.9× more likely correct) |
| Room-to-ceiling | **43.9%** | of headroom above UNCUED captured |
| Room above chance | **29.0%** | of total available scale above chance |

The VRDots density session (large aperture, 1.6 dots/sq°) will fill the same table when collected. If pp is similar (~25 pp) but LOR and Cohen's *h* are larger, the large-aperture condition has a stronger effect per unit of sensitivity. If all metrics scale proportionally, density may not be the driving variable.

---

## 6. Python Code

```python
import math

def effect_sizes(p_cued, p_uncued, p_chance=1/8):
    pp    = p_cued - p_uncued
    h     = 2*math.asin(math.sqrt(p_cued)) - 2*math.asin(math.sqrt(p_uncued))
    lor   = math.log(p_cued/(1-p_cued)) - math.log(p_uncued/(1-p_uncued))
    nor   = (p_cued - p_uncued) / (1 - p_uncued)
    rac   = (p_cued - p_uncued) / (1 - p_chance)
    return dict(pp=pp, h=h, lor=lor, OR=math.exp(lor), nor=nor, rac=rac)

# Example — Catek session
print(effect_sizes(173/256, 108/256))
```

For d' (8AFC), use `scipy.integrate.quad(lambda x: norm.pdf(x) * norm.cdf(x+d_)**7, -8, 8)` and invert numerically with `scipy.optimize.brentq`. Worth computing for the final write-up but not for exploratory comparisons.
