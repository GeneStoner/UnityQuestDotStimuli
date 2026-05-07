# V1 RF Sampling Model — Analysis, Critique, and Empirical Implications
*VRDots density & aperture comparison · April 2026*

> We built a V1 RF-sampling model to predict how dot density, aperture size, and exclusion zone interact to produce the cueing effect. The model makes concrete predictions that are partially wrong in instructive ways. Working through the discrepancy reveals a confound — eccentricity-dependent motion discriminability — that is more fundamental than any model parameter, and points to specific experiments needed to disentangle these factors.

**Contents**
1. The model: what C is and how it is computed
2. Two versions: total count vs fraction of pure RFs
3. Mixed RFs and information theory
4. Temporal integration: the model's most fundamental omission
5. Empirical results: what the data actually show
6. The obvious confound: eccentricity-dependent motion discriminability
7. What the model gets right and what it misses
8. A revised three-factor architecture
9. Proposed experiments
10. Implications for stimulus design
11. Summary

---

## 1. The Model: What C Is and How It Is Computed

The model asks: how many V1 neurons are positioned to carry unambiguous information about which dot field occupies their receptive field? A neuron that receives input from both fields carries mixed (ambiguous) information; one with input from neither is silent. Only a neuron driven exclusively by one field carries a clean field-identity signal.

### Building blocks

**RF size** grows linearly with eccentricity (Hubel & Wiesel; Dow et al. 1981):
```
d_RF(r) = 0.05 + 0.08·r  degrees
A_RF(r) = π·(d_RF/2)²
```
At 1°: A_RF ≈ 0.013 sq°. At 3°: A_RF ≈ 0.066 sq° — a 5× increase.

**Cortical magnification** (Schwartz 1980; Horton & Hoyt 1991):
```
M(r) = 8.0 / (1 + r/0.3)  mm/deg
```
M²/A_RF gives V1 neuron density (neurons per retinal deg²): 2516/sq° at 0.5°, falling to 2.9/sq° at 3°. An 870× drop over 2.5°.

**Dots per field per RF** (Poisson occupancy):
```
λ(r) = ρ · A_RF(r)
```
where ρ is dot density (dots/field/sq°). Under Poisson placement, the probability an RF receives dots from *exactly one* field — making it a pure, field-selective neuron — is:
```
S(λ) = 2·(1 − e^{−λ})·e^{−λ}
```
This peaks at λ = ln 2 ≈ 0.693. Below the peak: most RFs are empty (too sparse). Above the peak: most RFs receive both fields (too dense). At the peak: maximum fraction of RFs see exactly one field.

---

## 2. Two Versions: Total Count vs Fraction of Pure RFs

### Version A — Total count (original model)
```
C_count = ∫ [M(r)²/A_RF(r)] · S(λ(r)) · 2π·r  dr
```
Weights each eccentricity by neural density. This asks: how many field-selective V1 neurons exist in total across the aperture? Because M²/A_RF drops 870× from 0.5° to 3°, the integral is completely dominated by the innermost eccentricities.

### Version B — Fraction of pure RFs (retinal area weighted)
```
C_frac = ∫ S(λ(r)) · 2π·r  dr  /  π(r_apt² − r_excl²)
```
Drops the neural density weight; every patch of retina counts equally per unit area. This asks: across the whole aperture, what fraction of RFs are field-selective?

### Results

| Stimulus | r_excl | r_apt | ρ (/sq°) | C_count (norm) | C_frac | % pure RFs | % mixed RFs | % empty RFs |
|---|---|---|---|---|---|---|---|---|
| VRDots | 1.10° | 3.50° | 1.82 | 0.427 | 0.1598 | 16.0% | 0.9% | 83.1% |
| **HighDens** | 1.10° | 3.50° | 4.99 | **0.975** | **0.3342** | **33.4%** | 5.6% | 61.0% |
| **Catek** | 0.50° | 1.65° | 5.53 | **1.000** | 0.1597 | 16.0% | 0.9% | 83.2% |

> **Critical divergence between the two versions.** In C_count, Catek wins (1.000) and VRDots is a distant second (0.427) — the foveal magnification advantage completely drives the result. In C_frac, HighDens wins (0.334) and VRDots ≈ Catek are *identical* (0.1598 vs 0.1597) to four decimal places. Catek has the same fraction of pure RFs as VRDots because its higher dot density is exactly offset by its smaller RFs at lower eccentricities — λ ≈ 0.08 in both cases at their respective mid-eccentricities.

The fraction version predicts **HighDens >> VRDots ≈ Catek**, which is substantially closer to the empirical data. Whether to use C_count or C_frac is a genuine theoretical question: C_count is appropriate if more cortical neurons straightforwardly mean more behavioral signal; C_frac is appropriate if the attentional readout normalizes for cortical magnification (as perceptual thresholds largely do). Given that downstream areas (MT, parietal, FEF) have large RFs and integrate over wide V1 populations, C_frac is probably the more behaviourally relevant version.

**All three stimuli are on the rising limb of S(λ).** The peak is at λ = 0.693; at their mid-eccentricities, VRDots has λ = 0.078, HighDens λ = 0.215, Catek λ = 0.080. Every stimulus is deeply under-saturating V1 RFs — 61–83% of all RFs receive zero dots from either field and contribute nothing. This means increasing density would increase predicted signal for any of them. We are nowhere near the "too dense" failure mode.

---

## 3. Mixed RFs and Information Theory

Even if we accept C_frac as the right measure, there is a subtler issue: the model assigns zero information value to mixed RFs and full value to pure RFs. This is an approximation. In a population code with an optimal readout, each neuron's contribution is proportional to its Fisher information about field identity, not a binary pure/mixed label.

For a neuron with Poisson inputs from both fields independently at rate λ each:
- **Pure RF** (one field, zero from other): maximum Fisher information — response unambiguously identifies which field is present.
- **Mixed RF** (both fields): lower Fisher information, but nonzero. Its firing rate reflects the sum of both fields' dot counts. With two fields, the response is higher on average than with one field, but more variable. The signal-to-noise for field identity is reduced.
- **Empty RF**: zero Fisher information, zero response — contributes nothing regardless of readout strategy.

At our stimulus densities the mixed RF correction is numerically small: only 0.9–5.6% of RFs are mixed (vs 16–33% pure). Accounting for mixed RFs as partial-information neurons would shift C_frac upward by a few percent for HighDens and barely at all for VRDots and Catek. It would not change the ranking.

**The empty RF problem is the dominant issue.** At 61–83% empty, the vast majority of V1 neurons in the aperture contribute nothing. The information-theoretic priority is not minimizing the mixed fraction — it is getting dots *into* RFs at all. This is the same conclusion as the S(λ) analysis: we are on the rising limb, and the main limiting factor is dot sparsity relative to RF size, not inter-field contamination.

> An optimal readout would also make use of the spatial pattern of which RFs are active, not just a pooled count of pure neurons. Two fields translating in different directions produce different spatial activation patterns even in nominally mixed RFs — direction selectivity provides an additional segregation cue that is entirely absent from the current model.

---

## 4. Temporal Integration: The Model's Most Fundamental Omission

The static RF model treats neurons as instantaneous point detectors. Real V1 neurons integrate over 50–100ms; direction-selective neurons in V1 and MT build their motion responses over even longer windows, since direction must be inferred from displacement across multiple frames. This temporal integration compounds the spatial smearing from RF size and fundamentally changes the analysis.

### Temporal smearing during the translation window

The translation lasts 80ms and the dots move at 2.26°/s, giving a total displacement per dot of:
```
d_trans = 2.26°/s × 0.080s = 0.181°
```
At mid-eccentricity, d_RF ≈ 0.234°. Each dot sweeps **0.77 RF diameters** during the translation. The neuron integrates over this sweep, so its effective spatial footprint is smeared into an ellipse along the direction of motion:
```
A_RF_eff ≈ A_RF_static × (1 + d_trans / d_RF)  ≈  A_RF_static × 1.77
```
The effective λ — the expected number of dots per field that influence a neuron during the integration window — is therefore roughly **1.77× the static λ**:

| Stimulus | λ static | λ effective (×1.77) | S(λ_static) | S(λ_eff) | Position on curve |
|---|---|---|---|---|---|
| VRDots N=63 | 0.078 | 0.138 | 0.143 | 0.241 | rising limb |
| HighDens N=173 | 0.215 | 0.380 | 0.339 | **0.471** | approaching peak |
| **Peak N=500** | 0.620 | **1.097** | 0.495 | 0.333 | **past the peak** |

Temporal integration shifts the effective optimum to a lower density (~9/sq° vs ~16/sq° in the static model). More importantly, **Peak (N=500, ρ=14.4/sq°) is now on the declining limb** of S(λ_eff). This is consistent with the empirical finding that Peak does not outperform HighDens despite a 2.9× density increase — the temporal model predicts HighDens is near the effective optimum and Peak has already declined.

### The deeper issue: "predominantly" vs binary pure/mixed

Even the temporally-corrected S(λ_eff) still asks a binary question: over the integration window, did a neuron receive input from one field or both? For the direction-discrimination task, what matters is whether the neuron's response is *predominantly shaped* by one field's motion direction — a much weaker and more realistic criterion than "exactly one field."

Consider a neuron that receives one dot from the coherently translating field A and one dot from the randomly moving field B during the integration window. In the static or temporal model this neuron is "mixed" and its contribution is discounted. But field A's dot produces a directionally coherent drive (it moves consistently in one direction), while field B's dot produces a random, incoherent drive. The neuron's net directional response still predominantly reflects field A. It votes for the correct direction in the population, albeit noisily. It is not wasted.

The neurons that genuinely cannot contribute are those where field B produces comparable *directional* drive to field A — which requires not just that B's dots enter the RF, but that they do so with sustained, coherent directionality. In a random-motion field, this is unlikely for any individual neuron. The result is that the effective "field-selective" population is larger than either the static or temporally-smeared binary model predicts.

### Implication: the plateau is broader than the model predicts

The transition from the rising limb to the declining limb of S(λ) is sharp in the static model and somewhat less sharp in the temporal model. Under the "predominantly one field" criterion it becomes even broader — because neurons with unequal input from both fields contribute partial, directionally biased signal rather than zero. This predicts a wide, flat plateau in the density psychometric function rather than a sharp peak, which is exactly what the data show: VRDots (ρ=1.82), HighDens (ρ=4.99), and Peak (ρ=14.4) all produce Δpp ≈ +34pp with essentially no trend.

> **What the flat density curve implies about the readout mechanism.** Strong cueing effects despite high temporal mixing suggest the downstream attentional readout exploits the full population code — including directional tuning and temporal dynamics — not merely the binary field identity of individual neurons. The system appears robust to high within-neuron field mixing as long as there is sufficient population-level directional coherence from one field. This motivates the addition of direction-selective V1/MT neurons to any future version of the model, replacing the field-identity-only framework.

---

## 5. Empirical Results: What the Data Actually Show

Three sessions run on the same observer (GS), one per stimulus type.

| Metric | VRDots (7°, 1.82/sq°) | Catek (3.3°, 5.53/sq°) | HighDens (7°, 4.99/sq°) |
|---|---|---|---|
| CUED accuracy | 60.5% | **67.6%** | 58.6% |
| UNCUED accuracy | 25.8% | **42.2%** | 25.0% |
| Δpp (CUED−UNCUED) | **+34.8 pp** | +25.4 pp | **+33.6 pp** |
| Cohen's h | **0.718** | 0.516 | **0.696** |
| Odds ratio | **4.42×** | 2.86× | **4.25×** |
| R̄ CUED | 0.724 | 0.728 | 0.653 |
| R̄ UNCUED | 0.167 | **0.349** | 0.096 |
| ΔR̄ (C−U) | **+0.557** | +0.380 | **+0.556** |

Key observations:
1. Catek has the **highest CUED accuracy** (67.6% vs 60.5% and 58.6%).
2. Catek has a dramatically **higher UNCUED accuracy** (42.2% vs ~25%).
3. Catek's cueing effect (Δpp, h, OR, ΔR̄) is **smallest** of the three.
4. Catek UNCUED R̄ = 0.349 vs 0.167 / 0.096: errors are much more concentrated near 0° in the uncued condition — the observer is approximately right even without the attentional cue.
5. VRDots and HighDens are nearly identical on every effect-size metric despite a 2.7× density difference.

The model predictions (C_frac: HighDens >> VRDots ≈ Catek) match point 5 qualitatively but miss points 1–4 entirely. The model has nothing to say about why Catek's UNCUED performance is so elevated — and that turns out to be the central story.

### Density parametric results: VRDots geometry, N=63 / 173 / 500

Three sessions run on the same observer with identical aperture (7°, r_excl=1.1°), varying only N (hence ρ):

| Stimulus | N (dots/field) | ρ_eff (/sq°) | CUED | UNCUED | Δpp | Cohen's h | R̄ CUED | R̄ UNCUED |
|---|---|---|---|---|---|---|---|---|
| VRDots | 63 | 1.82 | 60.5% | 25.8% | **+34.8pp** | 0.718 | 0.724 | 0.167 |
| HighDens | 173 | 4.99 | 58.6% | 25.0% | +33.6pp | 0.696 | 0.653 | 0.096 |
| Peak | 500 | 14.4 | 63.3% | 28.5% | **+34.8pp** | 0.713 | 0.708 | 0.205 |

The cueing effect is **completely flat** across an 8× density range (ρ = 1.82 to 14.4/sq°, N = 63 to 500). Δpp = +34.8pp for both VRDots and Peak; HighDens is barely below at +33.6pp. Cohen's h and OR are similarly stable. R̄ UNCUED shows a non-monotonic pattern: dipping at HighDens (0.096) and recovering at Peak (0.205), suggesting session-to-session variability may be larger than any true density effect on the UNCUED arm.

This flat curve is the central empirical constraint on the model. The static RF model predicts a monotonic rise toward ρ_opt ≈ 16/sq°. The temporally-corrected model predicts Peak is already past the effective peak (λ_eff = 1.097 vs optimum 0.693). Neither version predicts a flat plateau from ρ = 1.82 to 14.4. The most parsimonious interpretation is that the "predominantly one field" population criterion creates a broad, shallow optimum that the tested range sits within entirely.

### Simultaneous-onset control results

Two full simultaneous-onset sessions (n=513 each, DecoupledDots_005m_Simult_v2) were run. Both fields appear at the same time; CUED/UNCUED labels are preserved but there is no onset cue.

| Condition | CUED | UNCUED | Δpp | z |
|---|---|---|---|---|
| Simult S1 (260417_1018) | 48.4% | 41.4% | +7.0pp | — |
| Simult S2 (260417_1115) | 44.1% | 41.4% | +2.7pp | — |
| **Pooled (n=1024)** | **46.3%** | **41.4%** | **+4.9pp** | **1.574 (n.s.)** |
| VRDots delayed (reference) | 60.5% | 25.8% | +34.8pp | — |

The pooled simultaneous Δpp = +4.9pp is not significant (z = 1.57, p ≈ 0.115). **The onset cue accounts for all of the 34.8pp cueing effect.** There is no detectable residual from other field-identity cues (motion, color, or depth) at this sample size. The simultaneous UNCUED (~41%) also provides the true motion-discriminability floor — what can be achieved with full voluntary attention on the correct field but no onset advantage. The regular UNCUED (~26%) sits ~15pp below this floor, representing the pure attentional misdirection cost of the delayed onset cue.

---

## 6. The Obvious Confound: Eccentricity-Dependent Motion Discriminability

The most parsimonious explanation for the Catek pattern is one that has nothing to do with attention or RF segregation: **all Catek dots are within 1.65° of fixation**, in the foveal and parafoveal zone where coherent motion direction is intrinsically easier to discriminate than in the periphery.

### Why eccentricity affects UNCUED performance

In the UNCUED condition the observer must report the direction of the *early-onset* field (field A) while exogenous attention has been captured by the *late-onset* field (field B). The difficulty has two sources:

1. **Attentional misdirection:** attention is on the wrong field, reducing processing resources for the correct one.
2. **Peripheral motion discrimination:** the correct field's dots are at eccentricities where direction discrimination requires dedicated attention more critically than near the fovea.

For VRDots/HighDens (dots at 1.1–3.5°), factor (2) strongly penalises UNCUED performance: at 2–3° eccentricity, coherent motion direction is hard to discriminate without focused attention. R̄ ≈ 0.10–0.17 indicates near-random responses. For Catek (dots at 0.5–1.65°), the correct field's motion is discriminable even with degraded attention because parafoveal acuity is much higher. R̄ = 0.349 indicates systematic, approximately correct responses.

### This makes the Δpp comparison across apertures uninterpretable as an attention effect

The cueing effect (Δpp = CUED − UNCUED) conflates two things:
- The true attentional benefit on CUED trials
- The attentional cost on UNCUED trials, which depends on baseline discriminability at the relevant eccentricity

If Catek's UNCUED floor is elevated by ~16 pp due to better peripheral acuity alone, then a Δpp of +25.4 pp for Catek might reflect the same underlying attentional effect as +34.8 pp for VRDots. The log odds ratio (4.42× vs 2.86×) partially accounts for this, but even LOR does not fully correct for floor effects when baseline performance varies across conditions.

> **Catek's smaller Δpp should not be interpreted as weaker attentional cueing.** It may instead reflect higher baseline discriminability from foveal dot placement. The appropriate reference for each aperture is its own simultaneous-onset baseline, not a shared chance level.

### Additional confound: fixation target size in the Catek session

The Catek session (260421_1202) used the VRDots fixation target (outer disc 0.6°, arms extending 0.6° radius) without scaling. This is proportionally much larger relative to a 3.3° aperture than to a 7° aperture, and the crosshair arms physically enter the 0.5° exclusion zone — partially overlapping with the dot region. Some foveal-adjacent dots may have been masked. A corrected Catek session with `fixationScaleFactor = 0.47` (now implemented in the asset) is required before any cross-aperture comparison is meaningful.

---

## 7. What the Model Gets Right and What It Misses

**What the model captures correctly:**
- All three stimuli are on the rising limb of S(λ) — increasing density improves RF segregation for any of them.
- VRDots ≈ Catek on segregation quality (fraction version), HighDens is substantially better — consistent with VRDots and HighDens performing similarly while HighDens might be expected to be somewhat better.
- The optimal density is far above any tested stimulus (~10–50/sq° depending on eccentricity), so no tested stimulus is "too dense."
- Larger apertures give more total signal (more annular area), provided density is maintained.

**What the model misses:**
- **Onset cue strength:** scales with N_dots, not with ρ alone. Catek (43 dots) has ~0.7× the onset energy of VRDots (63) and ~0.25× HighDens (173).
- **Coherent motion discriminability:** the task requires reporting motion direction; this is easier near the fovea (eccentricity effect) and easier with more dots (N effect).
- **UNCUED floor:** the model has no concept of performance without the cue, so it cannot predict how the floor varies with aperture placement.
- **Direction selectivity:** MT neurons carry motion-direction information beyond what field-identity alone captures; not modeled.
- **Fixation confounds:** wobble σ and target masking near the exclusion zone.

---

## 8. A Revised Three-Factor Architecture

A more complete model should have multiplicative factors for three separable processes:

```
C_full = C_segregation  ×  f_onset(N)  ×  f_motion(N, r_excl, r_apt)
```

Where:
- **C_segregation:** the fraction-version integral above — the quality of V1-level field segregation. Predicts HighDens > VRDots ≈ Catek.
- **f_onset(N):** onset salience as a function of total dot count N. A saturating function, e.g. N/(N + N_half), with N_half ≈ 20–40 (unknown; needs parametric measurement). This factor heavily penalises Catek (N=43) relative to HighDens (N=173).
- **f_motion(N, r_excl, r_apt):** direction-discrimination quality for the coherent field, accounting for eccentricity and dot count. This factor is higher for Catek (foveal) and for HighDens (more dots). It captures the UNCUED floor and is the term most conspicuously absent from the current model.

Critically, f_motion also determines the *UNCUED baseline* — performance without any attentional benefit. The true attentional effect should be expressed relative to this baseline, not to chance (1/8). Only then can cueing effects be meaningfully compared across aperture sizes that differ in eccentricity.

---

## 9. Proposed Experiments

### Experiment 1 — Simultaneous-onset control, per aperture [Priority: HIGH]

**Rationale.** The UNCUED condition with delayed onset confounds attention misdirection with eccentricity-dependent discriminability. A simultaneous-onset version (both fields appear together, no onset cue) removes the attentional misdirection and measures the true baseline discriminability floor for each aperture. The attentional cueing effect should then be expressed as Δpp relative to this baseline, not relative to chance.

**Design.** Run simultaneous-onset blocks for each of the three aperture/density configurations using the existing `Exp_DecoupledDots_005m_Simult.asset` logic. Predict: simultaneous-onset accuracy will be substantially higher for Catek (foveal) than for VRDots/HighDens (peripheral), confirming the eccentricity hypothesis.

**Key measure.** Δpp_corrected = CUED − simultaneous_onset_accuracy. If this equalises across stimuli, the eccentricity hypothesis is confirmed. If Catek still shows less benefit, onset cue strength or RF segregation is implicated.

### Experiment 2 — Corrected Catek session [Priority: HIGH, prerequisite]

**Rationale.** The existing Catek session (260421_1202) used an unscaled fixation target whose crosshair arms physically entered the dot region. Any Catek comparison is potentially confounded by fixation-target masking of foveal-adjacent dots.

**Design.** Run a new Catek session using the corrected asset (`fixationScaleFactor = 0.47`, outer disc 0.28°, arms to 0.28° radius). Also verify that the exclusion zone (0.5°) provides adequate margin around the arms. Compare CUED, UNCUED, and R̄ with the original session to estimate the masking cost.

### Experiment 3 — Parametric N sweep at fixed ρ [Priority: MEDIUM]

**Rationale.** The model predicts that ρ (density per unit area) is the relevant variable for RF segregation, not N (total dot count). But onset salience and motion discriminability depend on N independently. Holding aperture and ρ fixed while varying N (by changing aperture annular width) would isolate the N effect.

**Design.** Fix ρ = 1.82/sq° (VRDots density) and vary N by adjusting r_apt: e.g. N ≈ 20, 40, 63, 100, 160. This changes the outer radius from ~2.1° to ~5.6° while holding the dot density constant. Measures: CUED, UNCUED, Δpp, and onset detection latency if available. Predicts: Δpp will increase with N up to a plateau where onset salience saturates, identifying N_half empirically.

### Experiment 4 — Parametric ρ sweep at fixed N and aperture [Priority: MEDIUM]

**Rationale.** The RF model predicts a maximum at λ = ln 2, which requires ρ ≈ 10–50/sq° depending on eccentricity — far above anything tested. Are we truly on the rising limb, and does the model's peak exist behaviourally?

**Design.** Fix aperture at 7° and N = 63, vary ρ by adjusting the annular placement region. Alternatively fix N and aperture and vary ρ by changing exclusion zone r_excl. Run four ρ values spanning the rising limb: ~0.5, 1.82, 5.0, 10.0/sq°. Predicts: Δpp will increase across this range if we are below the peak. If Δpp plateaus or decreases at the highest densities, the peak has been bracketed.

*Note: HighDens (ρ ≈ 5.0) already provides one point above VRDots (ρ ≈ 1.82) with no clear drop in effect size, consistent with both being below the peak. This experiment adds the extreme upper end.*

### Experiment 5 — Eccentricity band isolation [Priority: LOWER]

**Rationale.** The model predicts the optimal eccentricity band is the innermost accessible region (due to cortical magnification). Empirically, Catek samples 0.5–1.65° while VRDots samples 1.1–3.5°. A 1.1–1.65° annulus with VRDots density and a 1.65–3.5° annulus at matching density would directly test whether the inner band contributes more cueing signal per dot.

**Design.** Three conditions: inner annulus (1.1–1.65°, N ≈ 16), outer annulus (1.65–3.5°, N ≈ 47), full annulus (1.1–3.5°, N = 63). Equate total N as closely as possible by adjusting ρ. Measures: Δpp and simultaneous-onset baseline per condition. This experiment directly tests the cortical magnification assumption — the strong prediction of C_count — against the eccentricity discriminability account.

---

## 10. Implications for Stimulus Design

| Parameter | Model recommendation | Empirical constraint | Working recommendation |
|---|---|---|---|
| **Dot density ρ** | Increase — all stimuli are below ρ_opt. C_frac rises monotonically toward 10–50/sq° depending on eccentricity. | VRDots (1.82) ≈ HighDens (5.0) in effect size despite 2.7× density difference. Diminishing returns may set in early. | Current HighDens density (5/sq°) is reasonable. Test up to 10/sq° (Exp 4) before increasing further. |
| **N dots per field** | Model treats N as irrelevant given ρ. Incorrect: N independently determines onset salience and motion signal. | VRDots (63) ≈ HighDens (173) in cueing effect. N=43 (Catek) may be at or near the onset floor. | Keep N ≥ 60 per field. Do not reduce N below ~50 when changing aperture. Determine N_half empirically (Exp 3). |
| **Aperture size** | Larger is better per C_count (more neurons). Neutral in C_frac (more area but same S(λ) at same ρ). | 7° performs well empirically. Catek (3.3°) has higher CUED but compressed Δpp — confounded with eccentricity. | 7° is a good default. Do not reduce below 5° without adding a simultaneous-onset control to separate eccentricity from attention (Exp 1). |
| **Exclusion zone r_excl** | C_count strongly favours small r_excl (1.1° blocks foveal magnification benefit). C_frac is neutral. | Cannot determine from current data: Catek confounds r_excl with r_apt, N, and fixation target size. | Run corrected Catek session (Exp 2) first. Do not reduce r_excl without ensuring fixation arms fit within exclusion zone with margin. |
| **Eccentricity of stimulus** | Not modeled — model is agnostic to placement, only aperture geometry matters. | Foveal placement substantially elevates UNCUED floor (Catek data). Makes Δpp smaller even if true attention effect is equal. | For measuring cueing effects: avoid the foveal zone unless simultaneous-onset baseline is measured per condition. For ERP: hemifield placement may be required (C1 cancellation). |
| **Fixation target** | Not modeled. | Unscaled target in Catek session contaminated dot-region. Fixation wobble enlarges effective RF. | Scale target proportionally to aperture. Implement fixationScaleFactor per asset. Ensure crosshair arm radius < r_excl − 0.2°. |

---

## 11. Summary

1. **C as a fraction of pure RFs** (not a total count) predicts HighDens >> VRDots ≈ Catek — closer to the empirical result than the cortical-magnification-weighted total count, which wrongly predicts Catek best.

2. **All three stimuli are deeply underpopulated in the static model** (61–83% empty RFs). Empty RFs do not dilute the signal — they are silent. What matters is the count and quality of *activated* neurons, of which ~90–96% are pure field-selective in the sparse regime. The emptiness problem is real only in the sense that denser stimuli activate more neurons and produce stronger onset transients.

3. **Temporal integration fundamentally changes the λ estimates.** During the 80ms translation window, each dot sweeps ~0.77 RF diameters, enlarging the effective RF area by ~1.77×. This raises effective λ across all stimuli and shifts the effective ρ_opt from ~16/sq° to ~9/sq°. Critically, Peak (N=500, ρ=14.4/sq°) is *past* the effective peak (λ_eff = 1.097 vs optimum 0.693) in the temporally-corrected model — consistent with it not outperforming HighDens. Beyond the temporal smearing correction, the binary pure/mixed criterion overstates field contamination: neurons receiving mixed input but dominated by one field's coherent directional drive still contribute usefully to the population code. This produces a broad plateau rather than a sharp optimum, matching the flat empirical density curve.

4. **The cueing effect is flat across an 8× density range.** VRDots (ρ=1.82/sq°), HighDens (ρ=4.99/sq°), and Peak (ρ=14.4/sq°) all produce Δpp ≈ +34pp, Cohen's h ≈ 0.70–0.72. No density effect is detectable. This is inconsistent with the static rising-limb prediction but consistent with the broad-plateau prediction of the temporally-corrected model with a "predominantly one field" readout criterion.

5. **The onset cue accounts for all of the cueing effect.** Simultaneous-onset control (n=1024 pooled): Δpp = +4.9pp, z = 1.57, p ≈ 0.115 — not significant. Without the delayed onset, there is no detectable cueing effect. The baseline discriminability floor (simultaneous-onset UNCUED ≈ 41%) is ~15pp above the regular UNCUED (~26%), quantifying the pure attentional misdirection cost.

6. **The model's most important omission is the UNCUED floor.** Catek UNCUED = 42.2% vs ~25% for VRDots/HighDens — entirely explained by eccentricity-dependent motion discriminability (foveal dots are more discriminable without attention), not by any cueing mechanism. Δpp comparisons across aperture sizes are uninterpretable without a simultaneous-onset baseline for each condition.

7. **The Catek session is additionally confounded** by an unscaled fixation target. A corrected session (fixationScaleFactor = 0.47) is required before any cross-aperture conclusions.

8. **Practical status:** the VRDots geometry (7°, r_excl=1.1°, N≥63) reliably produces large cueing effects (Δpp ≈ +35pp, h ≈ 0.71) across a wide density range. Increasing density beyond VRDots does not improve and may slightly decrease the effect at very high density (temporal mixing past the effective peak). The VRDots parameters are near-optimal for the current paradigm and should not be changed without a specific parametric justification.

---

*Generated April 2026 — VRDots project. Model code: `/tmp/v1_rf_model.py`. Figure: `/tmp/v1_rf_model.png`. Density comparison: `/tmp/density_compare3_analysis.py`.*
