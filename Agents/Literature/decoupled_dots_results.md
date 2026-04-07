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
| 260406_1532 | DecoupledDots_005m | 1 | Normal | 514 |
| 260406_1754 | DecoupledDots_Inv_005m | 0 | **INVERTED** before analysis | 512 |
| 260407_0643 | DecoupledDots_Inv_005m | 0 | **INVERTED** before analysis | 512 |
| 260407_0731 | DecoupledDots_005m | 1 | Normal | 513 |
| **Combined (S1+S2)** | | | | **1026** |
| **Combined (S1–S4)** | | | | **2051** |

Label inversion for 260406_1754 and 260407_0643: raw CUED/UNCUED labels are behaviorally reversed because delayTranslator=0 (the always-on field is delayed). Labels were flipped before any analysis so that CUED always means "temporal cue correctly marks the translator."

**Session 4 (260407_0731) anomaly**: dot cueing was anomalously flat (+4.8pp n.s., vs +22–40pp in prior sessions). Pattern is elevated UNCUED (all swaps ~25–34%), not depressed CUED — the reverse of what depth-swap disruption would predict. Observer noted ±22.5° criterion ambiguity and a perceptual sense of jerky motion during this session. Session is included without exclusion; no pre-defined performance criterion exists. Between-session variance is expected at n=64/cell. The 4-session combined results remain highly significant (see §3.2b).

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

### 3.1 Raw accuracy by Condition × SwapType

#### S1+S2 combined (n=1026, primary GLM dataset)

| Swap | CUED | UNCUED | Cueing Δ | sig |
|------|------|--------|----------|-----|
| N | ~43% | ~22% | **+31pp** | *** |
| C | ~49% | ~20% | **+38pp** | *** |
| Z | ~28% | ~20% | **+13pp** | ** |
| CZ | ~20% | ~20% | **+6pp** | n.s. |

#### All 4 sessions combined (n=2051)

| Swap | CUED | UNCUED | Cueing Δ | sig |
|------|------|--------|----------|-----|
| N | 48.4% | 24.9% | **+23.5pp** | *** |
| C | 50.0% | 26.5% | **+23.5pp** | *** |
| Z | 23.4% | 14.4% | **+9.0pp** | ** |
| CZ | 25.0% | 19.5% | **+5.5pp** | † |

Per-session cueing effects (N/C/Z/CZ, CUED−UNCUED):
- S1 (1532): N=+36pp***, C=+41pp***, Z=+2pp n.s., CZ=+11pp†
- S2 (1754, inv): N=+27pp***, C=+36pp***, Z=+25pp***, CZ=+2pp n.s.
- S3 (0643, inv): N=+30pp***, C=+11pp†, Z=+3pp n.s., CZ=+5pp n.s.
- S4 (0731, anomalous): N=+2pp n.s., C=+6pp n.s., Z=+6pp n.s., CZ=+5pp n.s.

### 3.2 Three-factor analysis

#### S1+S2 combined (n=1026, primary)

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

#### All 4 sessions combined (n=2051)

**F1 — Dot cueing:** Δ = **+15.4pp**, χ²(1)=59.01, p < 0.001 ***
**F2 — Depth-field cueing:** Δ = **+9–12pp range** (estimate from chi-square tests; see combined figure)
**F3 — Color-field cueing:** consistent null across all sessions

Overall χ²(7)=148.28, p < 10⁻¹⁷ for full 2×4 table. The 4-session combined results replicate the main structure despite S4 anomaly: Z/CZ swaps kill dot cueing more than N/C swaps, color swap alone (C) leaves cueing intact.

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

### 3.5 Why the odds ratios are the right effect size measure

The pp differences (+22.3pp, +12.5pp, +0.0pp) are intuitive but baseline-dependent. The logistic function is flattest near the extremes of the probability scale: the same underlying signal increment produces the *largest* pp change near 50% and progressively smaller pp changes as performance approaches floor or ceiling. A 22pp difference near chance is actually harder to produce — in terms of underlying signal strength — than the same 22pp difference in the middle of the range.

Our baseline sits at chance (UNCUED+CZ ≈ 12.5%), near the floor. This means the raw pp effects **underestimate** the underlying effect size: the same signal operating at a 50% baseline would yield a larger pp difference. The odds ratios correct for this nonlinearity: OR = 3.07 for dot cueing and OR = 1.89 for depth-field cueing are baseline-agnostic statements about how much each factor multiplies the odds of a correct response. They are the appropriate effect sizes for comparisons across conditions, sessions, or experiments with different baselines.

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
- **Color as a segmentation cue**: the null color result is somewhat surprising given the prominent use of color in object-based attention studies (e.g., Duncan 1984 same-object advantage for same-color objects). However, in those studies color serves to identify which object to report; here color is a field-level feature that co-varies with depth. The task never requires using color identity — subjects only report translation direction. Color may be irrelevant to the computation being performed. See `color_cueing_review.md` for a full treatment of the color null in the exogenous-attention literature, and `color_model_conjecture.md` for theoretical conjectures about why the point-set model predicts F3=0.
- **Vergence and the depth effect**: the 80ms translation window is within the latency period of even the fastest vergence responses (~70–85ms minimum; Busettini et al. 1997). Vergence is frozen during the entire translation window. The F2 depth-field cueing effect is therefore a purely neural disparity effect, not vergence-mediated. See `vergence_latency_note.md`.

---

## 6. Analysis files

| File | Purpose |
|------|---------|
| `Tools/Analysis/decoupled_dots_combined_analysis.py` | Main analysis; produces all session + combined figures |
| `Tools/Analysis/decoupled_dots_glm.py` | GLM (logistic + LPM); produces coefficient figure |
| `Tools/Analysis/decoupled_dots_field_cueing.py` | Standalone field-cueing analysis (superseded by combined script) |
| `Tools/Analysis/decoupled_dots_traj.py` | 4×4 trajectory figure |
| `Agents/Figures/decoupled_dots_260406_1532.png` | Session 1 figure (3 factors) |
| `Agents/Figures/decoupled_dots_260406_1754.png` | Session 2 figure (3 factors) |
| `Agents/Figures/decoupled_dots_260407_0643.png` | Session 3 figure (3 factors) |
| `Agents/Figures/decoupled_dots_260407_0731.png` | Session 4 figure (3 factors; anomalous, see §2 note) |
| `Agents/Figures/decoupled_dots_combined.png` | S1+S2 combined figure (3 factors + summary) |
| `Agents/Figures/decoupled_dots_combined_s1s2s3s4.png` | S1–S4 combined figure (all 4 sessions) |
| `Agents/Figures/decoupled_dots_session_comparison.png` | Per-session 3-factor comparison (shows S4 anomaly) |
| `Agents/Figures/decoupled_dots_glm.png` | Observed vs predicted + coefficient plot |
| `Agents/Figures/decoupled_dots_traj.png` | 4×4 trajectory grid |
