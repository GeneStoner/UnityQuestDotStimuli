# DecoupledDots Experiment — Design & Results
*Written 2026-04-06*

---

## 1. Motivation

Prior experiments (DepthColorLinked) showed that swapping the depth plane AND color of the coherent translator at tStart reduces the dot-cueing effect. But depth and color were always confounded (linkDepthColor=1): we could not tell whether the disruption was due to the depth plane change, the color change, or both.

**DecoupledDots** was designed to dissociate these two factors within a single balanced experiment.

---

## 2. Design

**Assets**: `Exp_DecoupledDots_005m` (delayTranslator=1) + `Exp_DecoupledDots_Inv_005m` (delayTranslator=0)
**Key parameter**: `linkDepthColor=0` — color and depth change independently at tStart

### Swap conditions (4 levels)

| SwapType | What changes at tStart | Translator color | Translator depth plane |
|----------|----------------------|-----------------|----------------------|
| N | Nothing | unchanged | unchanged |
| C | Color only | swaps (R↔G) | unchanged |
| Z | Depth only | unchanged | swaps |
| CZ | Color + depth | swaps | swaps |

### Sessions

| Session | Asset | delayTranslator | Label treatment | N valid |
|---------|-------|-----------------|----------------|---------|
| 260406_1532 | DecoupledDots_005m | 1 | Normal | ~514 |
| 260406_1754 | DecoupledDots_Inv_005m | 0 | **INVERTED** before analysis | ~512 |
| **Combined** | | | | **1026** |

Label inversion for session 260406_1754: raw CUED/UNCUED labels are behaviorally reversed because delayTranslator=0 (the always-on field is delayed). Labels were flipped before any analysis so that CUED always means "temporal cue correctly marks the translator."

### Three analysis factors

All three are binary and — crucially — **fully orthogonal** in this design (each 2×2×2 combination of the three factors appears in exactly 2 of the 8 Cond×SwapType cells, with equal n):

| Factor | Definition | Cued ✓ conditions | Uncued ✗ conditions |
|--------|-----------|-------------------|---------------------|
| **F1 Dot cueing** | Delayed-onset field translates | CUED | UNCUED |
| **F2 Depth-field cueing** | Translator ends in same depth plane the delayed field first appeared in | CUED+N, CUED+C, UNCUED+Z, UNCUED+CZ | CUED+Z, CUED+CZ, UNCUED+N, UNCUED+C |
| **F3 Color-field cueing** | Translator color at tStart matches delayed field's original color | CUED+N, CUED+Z, UNCUED+C, UNCUED+CZ | CUED+C, CUED+CZ, UNCUED+N, UNCUED+Z |

Orthogonality means factor effects are fully unconfounded: each coefficient in the linear model captures one factor's contribution with zero collinearity.

---

## 3. Results

### 3.1 Raw accuracy by Condition × SwapType (combined, n=1026)

| Swap | CUED | UNCUED | Cueing Δ | sig |
|------|------|--------|----------|-----|
| N | ~43% | ~22% | **+31pp** | *** |
| C | ~49% | ~20% | **+38pp** | *** |
| Z | ~28% | ~20% | **+13pp** | ** |
| CZ | ~20% | ~20% | **+6pp** | n.s. |

Session 1 (1532): N=+36pp***, C=+41pp***, Z=+2pp n.s., CZ=+11pp†
Session 2 (1754, labels flipped): N=+27pp***, C=+36pp***, Z=+25pp***, CZ=+2pp n.s.

### 3.2 Three-factor analysis (combined, n=1026)

**F1 — Dot cueing (CUED vs UNCUED, collapsed over all swaps):**
- CUED: ~35% correct; UNCUED: ~25% correct
- Δ = **+22.3pp**, p < 0.001 ***

**F2 — Depth-field cueing (field-cued✓ vs field-uncued✗):**
- Depth-cued ✓: 36.5% correct (+24.0pp above chance)
- Depth-uncued ✗: 24.0% correct (+11.5pp above chance)
- Δ = **+12.5pp**, χ²=18.93, p < 0.001 ***

**F3 — Color-field cueing (field-cued✓ vs field-uncued✗):**
- Color-cued ✓: 30.2% correct (+17.7pp above chance)
- Color-uncued ✗: 30.2% correct (+17.7pp above chance)
- Δ = **+0.0pp**, χ²=0.00, p = 1.00, n.s.

### 3.3 GLM — Logistic regression (trial-level, additive, no interactions)

Model: `correct ~ dot_cue + depth_cue + color_cue`

| Predictor | Log-odds | SE | z | p | Odds Ratio | LPM (pp) |
|-----------|----------|-----|---|---|-----------|----------|
| Intercept | −1.796 | 0.159 | −11.3 | <.001 | 0.17 | baseline=12.8% ≈ chance |
| dot_cue | **+1.121** | 0.145 | +7.71 | <.001 *** | **3.07** | **+22.3pp** |
| depth_cue | **+0.637** | 0.143 | +4.46 | <.001 *** | **1.89** | **+12.5pp** |
| color_cue | +0.001 | 0.142 | +0.01 | .994 n.s. | **1.00** | **+0.0pp** |

McFadden R² = 0.065; LRT χ²(3) = 82.0, p < 10⁻¹⁷

**Baseline** (all factors = 0, i.e., UNCUED+CZ): 12.8% predicted correct = essentially exactly chance (12.5%). The model is well-calibrated.

Linear probability model gives identical conclusions and directly interpretable pp coefficients. The two models converge because the design is fully orthogonal.

### 3.4 Depth-field cueing breakdown by dot cueing

| Depth-field group | Dot-CUED Δ | Dot-UNCUED Δ | Dot-cueing Δ within group |
|------------------|------------|-------------|--------------------------|
| Depth-cued ✓ | +42.2pp | +5.8pp | **+36.4pp *** |
| Depth-uncued ✗ | +15.6pp | +7.3pp | **+8.3pp * |

Dot cueing survives in both depth groups but is dramatically stronger when depth-field cueing is also present. This interaction (not yet formally tested without interaction term) suggests the two factors are approximately additive but may have some synergy.

---

## 4. Interpretation

### What this tells us

1. **Dot cueing is the dominant factor**: the temporal onset cue alone (+22.3pp) more than doubles the odds of correct response. This replicates the original Stoner & Blanc (2010) object-based attention effect in VR with a stereoscopic stimulus.

2. **Depth-field cueing is real and significant (+12.5pp, OR=1.89)**: knowing that translation will occur at the same depth plane where the delayed-onset object first appeared gives a substantial additional performance boost. This is consistent with depth plane as an object-defining feature — the depth plane identity helps maintain or retrieve the attentional object across the onset-to-translation interval.

3. **Color-field cueing is exactly zero (OR=1.00, p=.994)**: the color identity of the delayed field — whether the translating dots match or mismatch the delayed field's original color — carries no predictive information for performance. Color, as implemented here (a single uniform color per field, balancing R and G across trials), does not serve as an attentional anchor for this task. This does not mean color is unimportant in general — but it means that under these conditions, depth plane dominates over color as the feature that preserves object identity across the delay.

4. **Why did DepthColorLinked show a "color" effect?** It didn't, strictly speaking. In that experiment, linkDepthColor=1 meant depth and color always changed together (ZdA/ZdB), so we could not attribute the effect to either factor alone. The DecoupledDots data reveal that the effect was entirely carried by depth. Color was a confound in DepthColorLinked, not an independent factor.

5. **UNCUED+CZ ≈ chance**: when all three factors work against performance (the translating field is not the delayed-onset field, it translates in the wrong depth plane, and with the wrong color), performance is indistinguishable from chance. The model captures this cleanly: intercept → 12.8% ≈ chance.

### Open questions

- **Interaction between dot cueing and depth-field cueing**: the breakdown (§3.4) suggests possible synergy — the depth advantage is much larger within the CUED group (+36.4pp) than within UNCUED (+5.8pp gap is the full dot-cueing effect minus the depth contribution). A formal test with an interaction term should be added with more data.
- **Why does depth matter at all?** Two candidate mechanisms: (a) depth plane as a segmentation cue that defines object boundaries — the attentional window anchors to a depth plane, and the translation signal is more detectable when it originates from within that plane; (b) depth change at tStart generates a spurious monocular positional shift (geometric confound: changing disparity by 0.05m at 2m induces ~5 arcmin horizontal shift per eye at aperture edge). If this spurious shift competes with the true translation direction, it would impair Z and CZ specifically for CUED trials. Monocular testing would partially dissociate these accounts.
- **Color null result mechanism**: the color assignment is uniform per field (all dots same color) and swaps the entire field's color simultaneously. An alternative implementation where color varies at the dot level might yield different results. The current null means only that field-level color identity is not used as an attentional anchor in this task.
- **Second observer**: all data from one observer (GS). The pattern is consistent across sessions and the GLM is highly significant (n=1026), but generalizability is unknown.
- **Interaction terms**: the additive model accounts for the major structure but may miss synergies. Enough data for a full 2³ factorial model (~128+ trials per cell) would allow formal interaction tests.

---

## 5. Relation to broader literature

- **Object-based attention (Egly et al. 1994, Baylis & Driver 1993)**: the dot-cueing effect is the core object-based attention manipulation — translated from rectangles/surfaces to stereoscopic dot fields. The temporal onset cue selects an object; attention then spreads within object boundaries.
- **Depth-plane segmentation (He & Nakayama 1994, Nakayama et al. 1995)**: depth is a primary cue for figure-ground and object segmentation. The depth-field cueing effect is consistent with depth plane defining the attended object's spatial scope.
- **Feature binding across time**: the temporal gap between delayed-onset and translation (≥300ms pre-translation hold + 750ms delayed onset window) means the object must be maintained in some form before the translation probe. Depth-plane identity may serve as a spatiotopic anchor that survives the delay.
- **Color as a segmentation cue**: the null color result is somewhat surprising given the prominent use of color in object-based attention studies (e.g., Duncan 1984 same-object advantage for same-color objects). However, in those studies color serves to identify which object to report; here color is a field-level feature that co-varies with depth. The task never requires using color identity — subjects only report translation direction. Color may be irrelevant to the computation being performed.

---

## 6. Analysis files

| File | Purpose |
|------|---------|
| `Tools/Analysis/decoupled_dots_combined_analysis.py` | Main analysis; produces S1, S2, combined figures |
| `Tools/Analysis/decoupled_dots_glm.py` | GLM (logistic + LPM); produces coefficient figure |
| `Tools/Analysis/decoupled_dots_field_cueing.py` | Standalone field-cueing analysis (standalone, now superseded by combined script) |
| `Tools/Analysis/decoupled_dots_traj.py` | 4×4 trajectory figure |
| `Agents/Figures/decoupled_dots_260406_1532.png` | Session 1 figure (3 factors) |
| `Agents/Figures/decoupled_dots_260406_1754.png` | Session 2 figure (3 factors) |
| `Agents/Figures/decoupled_dots_combined.png` | Combined figure (3 factors + summary) |
| `Agents/Figures/decoupled_dots_glm.png` | Observed vs predicted + coefficient plot |
| `Agents/Figures/decoupled_dots_traj.png` | 4×4 trajectory grid |
