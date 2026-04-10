# GLM2 Explainer: Logistic Regression, Log-Odds, and the Interaction Model
*Written 2026-04-09*

---

## 1. Why not just use percent correct directly?

The outcome in each trial is binary: either the observer correctly identified the translation direction (1) or did not (0). Percent correct is just the mean of these 0/1 values across trials. It is intuitive and we report it throughout.

The problem with fitting a standard linear regression to a binary outcome is that it can predict probabilities below 0% or above 100%, and the equal-variance assumption is badly violated near floor and ceiling. More fundamentally, the relationship between a predictor and the probability of success is inherently nonlinear: a 10pp increase from 12.5% (chance) to 22.5% reflects a much larger change in underlying signal than a 10pp increase from 45% to 55%.

Logistic regression solves this by modelling a transformation of the probability — the **log-odds** — rather than the probability itself. On the log-odds scale, the model is linear, well-behaved at all probability levels, and gives directly interpretable coefficients.

---

## 2. From probability to odds to log-odds

**Probability** (p): familiar — ranges 0 to 1.

**Odds**: the ratio of success to failure — p / (1 − p).

- p = 0.125 (chance, 1/8 correct) → odds = 0.125/0.875 = **0.143**
- p = 0.25 (25% correct)          → odds = 0.25/0.75  = **0.333**
- p = 0.50 (50% correct)          → odds = 0.50/0.50  = **1.000**
- p = 0.75 (75% correct)          → odds = 0.75/0.25  = **3.000**

Odds range from 0 to ∞. A doubling of the odds means the same proportional improvement in performance regardless of where on the scale you start — it is a multiplicative, not additive, measure.

**Log-odds** (also called the *logit*): the natural logarithm of the odds — log(p / (1 − p)).

- p = 0.125 → log-odds = log(0.143) = **−1.946**
- p = 0.25  → log-odds = log(0.333) = **−1.099**
- p = 0.50  → log-odds = log(1.000) = **0.000**
- p = 0.75  → log-odds = log(3.000) = **+1.099**

Log-odds range from −∞ to +∞, with zero at 50% correct. Negative values mean below 50%; positive values mean above 50%. The logit is symmetric: p=0.25 and p=0.75 are equidistant from 50% on the log-odds scale (±1.099), even though 25% is closer to floor and 75% is closer to ceiling.

**Converting back**: given a log-odds L, the probability is p = 1 / (1 + e^(−L)).

---

## 3. The logistic regression model

Logistic regression assumes the log-odds of a correct response is a linear combination of the predictors:

```
log-odds(correct) = β₀ + β₁·F1 + β₂·F2 + β₃·F3 + β₄·F4
                       + β₅·(F1×F2) + β₆·(F1×F4) + β₇·(F2×F4)
```

The β coefficients are estimated by maximum likelihood — they are the values that make the observed data most probable under the model. This is the linear model the user expected: one coefficient per term, estimated directly from the data.

The four predictors are all binary (0/1):

| Factor | = 1 when | = 0 when |
|--------|----------|----------|
| F1  Dot cueing | Trial is CUED (temporal onset cue marks translator) | UNCUED |
| F2  Depth-field cued | Translator depth plane matches delayed field's onset depth | Mismatch |
| F3  Color-field cued | Translator color matches delayed field's original color | Mismatch |
| F4  Translator Near | Translator occupies the Near depth plane | Far |

F2=1 conditions: CUED+N, CUED+C, UNCUED+Z, UNCUED+CZ.
F2=0 conditions: CUED+Z, CUED+CZ, UNCUED+N, UNCUED+C.
(F3 follows the complementary pattern; F4 depends on b\_near and cond.)

Three interaction terms are included: F1×F2 (dot × depth), F1×F4 (dot × translator depth), F2×F4 (depth × translator depth). These test whether the effect of one factor depends on the level of another.

---

## 4. The estimated coefficients (n = 2051, all 4 sessions)

| Term | β (log-odds) | SE | z | p | Odds ratio |
|------|-------------|-----|---|---|------------|
| Intercept (β₀) | −0.713 | 0.137 | −5.22 | <.001 *** | 0.49 |
| F1  Dot cueing | −0.287 | 0.174 | −1.65 | .098  n.s. | 0.75 |
| F2  Depth-field cued | −0.332 | 0.174 | −1.91 | .057  n.s. | 0.72 |
| F3  Color-field cued | +0.049 | 0.103 | +0.47 | .639  n.s. | 1.05 |
| F4  Translator Near | −0.833 | 0.185 | −4.51 | <.001 *** | 0.43 |
| F1 × F2 | **+1.785** | 0.215 | +8.30 | <.001 *** | **5.96** |
| F1 × F4 | +0.488 | 0.221 | +2.21 | .027  * | 1.63 |
| F2 × F4 | −0.675 | 0.216 | −3.12 | .002  ** | 0.51 |

McFadden pseudo-R² = 0.092. LRT χ²(7) = 228, p < 10⁻⁴⁵.

### Reading the intercept

β₀ = −0.713 is the log-odds of a correct response when **all predictors = 0**: UNCUED, depth anti-cued, color anti-cued, Far plane. Converting: p = 1/(1 + e^0.713) = **0.328**, or about 33%. This is the model's predicted accuracy for the "most anti-cued" Far-plane condition. It is not the overall baseline; it is the specific reference cell.

### Reading a main effect coefficient

β₁ = −0.287 for F1 means: **when F2 = 0, F4 = 0, and all other predictors are at their reference level**, being CUED (F1 = 1 vs 0) changes the log-odds by −0.287. This is a small, non-significant, slightly negative number — surprising if you expected dot cueing to always help.

The reason it is near zero is that this coefficient captures the effect of dot cueing *only in the depth-anti-cued, Far-plane context* (the F2=0, F4=0 reference cell). In that specific context — where the depth cue works against the dot cue — being dot-cued provides little benefit. The large benefit of dot cueing emerges only when depth cueing is also present, which is captured by the interaction term.

### Reading an interaction coefficient

β₅ = +1.785 for F1×F2 means: **the effect of F1 increases by 1.785 log-odds units when F2 = 1**. In other words, being dot-cued is 1.785 log-odds units more effective when depth is also cued than when it is not.

To find the total effect of being simultaneously dot-cued AND depth-cued (vs UNCUED and depth anti-cued), sum the relevant coefficients:

```
Total effect of (F1=1, F2=1) vs (F1=0, F2=0):
  F1 + F2 + F1×F2 = −0.287 + (−0.332) + 1.785 = +1.166 log-odds
```

Converting the reference cell (F1=0, F2=0, F4=0): intercept −0.713 → p ≈ 33%.
Adding 1.166 log-odds: −0.713 + 1.166 = +0.453 → p = 1/(1+e^−0.453) ≈ **61%**.

That shift from 33% to 61% is the full dot+depth cueing benefit, expressed in actual predicted accuracy. It matches what we observe in the raw data for CUED+N and CUED+C.

---

## 5. Why the main effects look negative — the reference cell issue

In a model without interaction terms (GLM1), F1 = +22pp because that coefficient averages over all depth-cueing contexts. In GLM2 with an F1×F2 interaction term, the main effect of F1 is redefined as the effect *at F2 = 0*. Because the reference level (F2 = 0) is the anti-cued context, F1's main effect in GLM2 is the dot-cueing benefit in the worst-case depth scenario — which is near zero.

This is not a contradiction. Both estimates are correct; they answer different questions:

- GLM1 F1 = +22pp: *On average across all depth-cueing contexts, how much does dot cueing help?*
- GLM2 F1 = −5pp (AME): *Averaging the marginal effect of F1 over all observations (which includes the steep interaction slope), what is the average contribution of F1?* This is now small because most of F1's benefit is attributed to the F1×F2 term.
- GLM2 β₁ = −0.287: *At F2 = 0, F4 = 0, how much does F1 help?* This is the conditional coefficient in the specific reference cell.

The additive model (GLM1) was not wrong — it correctly identified which factors matter. But it attributed the joint F1∧F2 benefit to two separate main effects rather than a single synergistic interaction. GLM2 shows that the signal structure is: **dot cueing and depth-field cueing conjointly drive performance, and neither is effective in isolation.**

---

## 6. Average marginal effects (AMEs)

Because the logistic function is nonlinear, the same coefficient produces different probability-scale effects depending on where you are on the curve. Near p = 0.5 (the steepest part), a 1-unit change in log-odds produces a large probability change (~25pp). Near the floor (p ≈ 0.125), the same 1-unit change produces a smaller probability change.

The **average marginal effect (AME)** for a predictor is the average, over all n = 2051 observations, of the derivative of P(correct) with respect to that predictor. For binary predictors, it approximates the average change in predicted probability when that predictor flips from 0 to 1, holding all other predictors at their observed values. The AME is expressed in percentage points.

| Term | AME (pp) | interpretation |
|------|----------|----------------|
| F1  Dot cueing | −5.3 pp | small, n.s., captured by interaction |
| F2  Depth-field cued | −6.1 pp | small, n.s., captured by interaction |
| F3  Color-field cued | +0.9 pp | null |
| F4  Translator Near | **−15.3 pp** | Near plane reliably worse |
| F1 × F2 | **+32.7 pp** | synergistic conjunction |
| F1 × F4 | **+8.9 pp** | dot cueing partly offsets Near penalty |
| F2 × F4 | **−12.4 pp** | depth cueing less effective when Near |

The AME for F1×F2 = +32.7pp means: when both F1 and F2 flip from 0 to 1 simultaneously (i.e., going from UNCUED+depth-anti-cued to CUED+depth-cued), the average predicted probability of a correct response increases by about 33 percentage points. This is the dominant effect in the model.

---

## 7. Summary in plain language

The model asks: can we predict trial-by-trial accuracy from four binary features of the trial (dot cued?, depth cued?, color cued?, Near plane?), including three two-way interactions?

**What we found:**

1. **Dot cueing and depth-field cueing interact synergistically** (+32.7pp, the largest effect). Performance is high only when *both* the dot temporal cue and the depth-plane cue point to the same field. Neither alone does much. This is equivalent to saying: depth swaps (Z, CZ) disrupt dot cueing specifically because they sever depth-plane continuity of the attentional object.

2. **Color is completely null** (AME = +0.9pp, p = .64) across every model specification. The field's color identity provides no information for this task.

3. **Near-plane translation is intrinsically harder** (−15.3pp, p < .001), regardless of cueing. The Far > Near asymmetry is a robust, depth-specific effect (absent in monocular sessions from DepthSwapCtrl).

4. **The additive model (GLM1) was structurally misleading.** It estimated F1 = +22pp and F2 = +12pp as independent contributions. GLM2 shows these were an averaging artefact: the signal is concentrated in the F1×F2 conjunction, and both main effects are near-zero in isolation.

---

## 8. Analysis files

| File | Purpose |
|------|---------|
| `Tools/Analysis/decoupled_dots_glm2.py` | Fits the model; produces forest plot PDF |
| `Agents/Figures/decoupled_dots_glm2.pdf` | Forest plot: log-odds (left) + AME in pp (right) |
| `Agents/Literature/decoupled_dots_results.md` §3.6 | Results table and narrative |
| `Agents/WriteUps/decoupled_dots_results.pdf` | Full rendered write-up |
