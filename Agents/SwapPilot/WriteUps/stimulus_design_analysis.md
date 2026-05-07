# VRDots Stimulus Design: Dot Density, Aperture Size, Exclusion Zone, and Fixation Target

*G. Stoner · April 2026 · Based on sessions: VRDots 260421_1541 · Catek 260421_1202 · HighDens 260422_0708 (n = 512 each)*

---

## 1. Background and Motivation

The VRDots paradigm presents two superimposed fields of randomly-positioned dots in a circular aperture. One field (the *cued* field) has a delayed onset; this temporal asymmetry is the putative attentional cue. On each trial the observer reports the translation direction of the coherently-moving subfield. The key dependent variable is the cueing effect: CUED accuracy minus UNCUED accuracy.

Four stimulus parameters jointly determine what the visual system can extract on each trial: dot density, aperture size, the exclusion zone around fixation, and the fixation target itself. These are not independent — they interact through eccentricity-dependent cortical magnification, receptive field (RF) grain, and fixation stability. This document examines each parameter in turn, integrating empirical findings from a three-way density/aperture comparison with a V1 RF sampling model of the cueing mechanism.

---

## 2. Empirical Findings: Three-Way Comparison

Three stimulus configurations were compared within the same observer and paradigm, varying aperture size and dot density:

| Condition | Aperture diam | Dots/field | Density (full-area) | Eccentricity range |
|---|---|---|---|---|
| VRDots | 7° | 63 | 1.64/sq° | 1.1°–3.5° |
| HighDens | 7° | 173 | 4.50/sq° | 1.1°–3.5° |
| Catek | 3.3° | 43 | 5.03/sq° | 0.5°–1.65° |

HighDens was designed specifically to dissociate density from aperture size: it matches Catek's dot density but in the VRDots aperture. Key results:

| Metric | VRDots | HighDens | Catek |
|---|---|---|---|
| CUED accuracy | 60.5% | 58.6% | 67.6% |
| UNCUED accuracy | 25.8% | 25.0% | 42.2% |
| Δpp (cueing effect) | +34.8 pp | +33.6 pp | +25.4 pp |
| Cohen's h | +0.718 | +0.696 | +0.516 |
| R̄ CUED | 0.724 | 0.653 | 0.728 |
| R̄ UNCUED | 0.167 | 0.096 | 0.349 |
| ΔR̄ (C−U) | +0.557 | +0.556 | +0.380 |

> **Core finding:** VRDots and HighDens are statistically indistinguishable across every metric despite a 2.7× difference in dot density. Catek yields a smaller cueing effect, driven entirely by an elevated UNCUED arm (42% vs ~25%). CUED accuracy is comparable across all three conditions. Density, within the range tested, does not modulate the cueing effect. Aperture size (and consequently eccentricity) does.

---

## 3. Dot Density

### 3.1 What the data say

The HighDens condition was the critical test: if density per se suppresses cueing — as earlier comparisons with Catek-like stimuli suggested — then HighDens (4.5/sq°) should yield a smaller effect than VRDots (1.64/sq°). It does not. The cueing effect (Δpp, Cohen's h, ΔR̄) is essentially identical between the two large-aperture conditions. This rules out dot density as an independent driver of cueing magnitude across the range 1.6–5.0 dots/sq°.

### 3.2 Density and the RF sampling model

The hypothesized cueing mechanism relies on V1 RFs differentially sampling cued and uncued dots: if a given RF contains predominantly cued-field dots at the moment of translation, it contributes a clean motion signal; if it contains a mix, the signals partially cancel. The model therefore predicts that cueing degrades when inter-dot spacing falls below RF diameter.

At 2–3° eccentricity, V1 RF diameters are approximately 0.2–0.5°. Average inter-dot spacing at the densities tested is:

```
VRDots:   spacing ≈ 1/√(1.64) ≈ 0.78°  >>  RF diameter
HighDens: spacing ≈ 1/√(4.50) ≈ 0.47°  >>  RF diameter
Catek:    spacing ≈ 1/√(5.53) ≈ 0.43°  >>  RF diameter  (eff. density)
```

In all three conditions, inter-dot spacing substantially exceeds typical V1 RF diameters. The model's saturation regime has not been reached: most RFs contain at most one dot from each field. This explains the null density effect. A secondary compensation exists at higher densities (more total RFs are activated), but this is speculative until densities where inter-dot spacing approaches RF diameter are tested — likely above 10 dots/sq° at these eccentricities.

> **Design recommendation:** Dot density between 1.6 and 5.0 dots/sq° does not modulate the cueing effect in the VRDots aperture. The current value of 1.64/sq° (full-area) is adequate. There is no compelling reason to increase density within the range currently used.

---

## 4. Aperture Size and Eccentricity

### 4.1 Larger aperture yields a larger cueing effect

The Catek aperture (3.3° diameter) yields a smaller cueing effect than the VRDots aperture (7° diameter) at matched density. Since HighDens rules out density as the explanation, the difference must be attributed to the aperture itself — specifically, the eccentricity distribution of the dots it contains.

### 4.2 A counterargument: larger peripheral RFs should impair field segregation

V1 RF diameter scales with eccentricity — approximately doubling for each doubling of eccentricity. At 3° eccentricity, RFs are roughly 0.3–0.5° in diameter; at 1° (Catek mid-range), they are roughly 0.1–0.2°. If the cueing mechanism relies on RFs selectively sampling one field's dots, then *larger* peripheral RFs should be more likely to contain dots from both fields simultaneously, degrading the field-specific signal and thereby *reducing* the cueing effect. On this argument, the smaller Catek aperture with its fine-grain foveal RFs should be the better stimulus.

This argument is internally consistent. The question is whether it applies in the regime currently tested.

### 4.3 Reconciliation: the two arguments target different components of the effect

The cueing effect is CUED − UNCUED. These two arms can be driven by entirely separate mechanisms:

- **RF mixing impairs CUED:** if peripheral RFs contain both cued and uncued dots, the cue's selectivity at the cortical level is reduced, potentially lowering CUED accuracy.
- **Peripheral eccentricity suppresses UNCUED:** at lower acuity, the motion signal from the unattended field is harder to read without attentional guidance, lowering UNCUED accuracy.

The data resolve which is dominant. CUED accuracy is approximately stable across all three conditions (59–68%), while UNCUED varies markedly (25% for VRDots/HighDens, 42% for Catek). The larger cueing effect in the VRDots aperture is driven entirely by UNCUED suppression, not by CUED enhancement. The RF mixing cost to CUED, if it exists, is either absent or masked by some other performance ceiling.

Two possibilities, not mutually exclusive: (1) even at 3° eccentricity the inter-dot spacing (~0.74°) substantially exceeds V1 RF diameter (~0.35°), so most RFs still contain at most one dot from each field; (2) the temporal onset cue may operate at a level above individual V1 RFs (e.g., MT population signals or attentional feedback), making CUED accuracy insensitive to RF-level field segregation.

> **Interpretation:** The larger aperture wins not because it improves the cue's cortical selectivity, but because it places dots in a regime where unaided motion discrimination is harder. The cueing effect is amplified by suppressing UNCUED, not by enhancing CUED. The RF mixing counterargument identifies a real cost that would become decisive at either larger eccentricities or higher densities — but has not yet been reached in the parameter range tested.

### 4.4 The open prediction

If aperture were increased further — pushing dots to 5–8° eccentricity where V1 RFs are 0.6–1.0° in diameter, approaching inter-dot spacing — the RF mixing cost should begin to suppress CUED as well, eventually shrinking the cueing effect from above. Similarly, a density series holding the current aperture fixed and increasing dot count toward RF-diameter-scale spacings would test whether RF mixing selectively suppresses CUED while UNCUED remains at floor.

> **Design recommendation:** The 7° aperture is substantially better than 3.3° in the current regime — UNCUED suppression dominates the effect size. Increasing aperture further is worth testing, with the caveat that at sufficiently large eccentricities the RF mixing cost to CUED will begin to dominate and the effect will shrink. There is likely an optimal aperture where UNCUED is maximally suppressed and CUED has not yet degraded — the current 7° diameter may already be close to this optimum, but this has not been tested directly.

---

## 5. The Exclusion Zone

### 5.1 Purpose

The exclusion zone prevents dots from appearing within a defined radius of the fixation point. Its primary purpose is to avoid foveal stimulation that could drive eye movements or provide a privileged motion signal unrepresentative of the peripheral stimulus. A secondary purpose is to keep the fixation target visible and unoccluded.

### 5.2 Fixation imprecision: retinal shifts are global but neural responses are not

Fixation is never perfect. Typical observers produce a combination of microsaccades (amplitude 0.1°–0.5°, frequency 1–2 Hz) and slow drift (velocity ~0.05–0.3°/sec). Over a trial (~1.2 s from onset to response), cumulative drift amounts to 0.1–0.4° of retinal displacement.

A critical distinction: fixation wobble is a *global retinal shift* — all dots translate together by the same vector, preserving their positions relative to one another. Relative dot-to-dot geometry is therefore unaffected by drift. However, *individual cortical neurons* respond to absolute retinal position, not relative position. When fixation drifts by δ, the entire dot field sweeps across the cortical map: a neuron that was being driven by a cued dot is now driven by whatever happens to be at its RF center in the new gaze position. Over the course of a trial with ongoing drift, each neuron accumulates responses from a sequence of different dots from potentially both fields.

This is *not* temporal low-pass filtering of a fixed stimulus; it is the accumulation of spatially distinct inputs over time due to the stimulus wandering across the RF. The practical consequence is reduced field-specific purity of each neuron's response.

The enlargement of the effective integration area due to drift of amplitude σ can be approximated as:

```
effective RF diameter ≈ √(d_RF² + σ²)

VRDots (d_RF ≈ 0.35°, σ ≈ 0.2°):  effective ≈ 0.40°   (+14% enlargement)
Catek  (d_RF ≈ 0.10°, σ ≈ 0.2°):  effective ≈ 0.22°   (+120% enlargement)
```

The fractional enlargement is far greater at Catek eccentricities. Crucially, the enlarged effective RF at Catek eccentricities (0.22°) is now a substantial fraction of the inter-dot spacing (0.45°), meaning it more often spans the gap between a cued and uncued dot. For VRDots, the enlarged effective RF (0.40°) remains well below the inter-dot spacing (0.74°). Drift therefore more severely degrades field segregation at Catek eccentricities than at VRDots eccentricities — the opposite of what one might naively expect given that Catek has smaller nominal RFs.

**Exclusion zone violation:** Dots nominally just outside the 0.5° Catek exclusion zone can drift across the fovea, placing high-contrast moving stimuli on the highest-acuity region of the retina. The VRDots 1.1° exclusion zone requires more than five times larger drift for the same violation.

> **Caution:** Fixation drift affects Catek worse than VRDots on two independent grounds: (1) it disproportionately enlarges the effective RF relative to inter-dot spacing at low eccentricity, mixing cued and uncued signals more severely; and (2) it more readily violates the exclusion zone, producing spurious foveal stimulation. Both effects elevate UNCUED performance in Catek, potentially accounting for some or all of the apparent eccentricity advantage reported above. These cannot be dissociated from genuine eccentricity effects without concurrent eye tracking.

### 5.3 Optimal exclusion zone sizing

The exclusion zone radius should comfortably exceed the typical fixation error amplitude. Based on typical microsaccade amplitudes (~0.5°) and slow drift accumulated over a trial (~0.3°), a minimum exclusion zone of 0.8° provides a reasonable safety margin. The current VRDots value of 1.1° is conservative and appropriate. Catek's 0.5° zone is likely insufficient, particularly for observers with poorer fixation than the initial observer (GS).

> **Design recommendation:** Maintain the exclusion zone radius at ≥ 1.0° for all future experiments. Do not reduce it to match smaller apertures — the exclusion zone should be set by fixation physiology, not by aperture size. For an aperture as small as 3.3° diameter, a 1.0° exclusion zone would consume 36% of the aperture radius on each side, leaving a narrow annular band of 0.65°. This may not be practical at small aperture sizes, which is a further argument against small apertures.

---

## 6. Fixation Target Design

### 6.1 Design rationale

The fixation target serves two functions: providing a precise spatial reference to stabilize gaze, and minimizing the drive for corrective eye movements caused by target motion or flicker. These functions pull in opposite directions — a very small target is precise but provides a weak gaze-holding signal; a large ring or crosshair provides a strong spatial reference but may itself drive vergence or pursuit if it has structure near the fovea.

The current VRDots bull's-eye design (white filled disc + black crosshairs + white center dot) addresses this tension:

- **Center dot** (0.24° diameter): small, high-contrast, provides the precision fixation anchor on the fovea.
- **Outer disc** (0.6° diameter) with crosshairs: provides a structured surround whose edges activate peripheral V1 orientation-selective cells and help suppress slow drift via a continuous spatial error signal.
- **Black crosshairs on white disc**: high local contrast at the disc edges where most fixation-stabilizing neural activity originates (orientation-tuned cells responding to the disc border).

### 6.2 Why a larger target stabilizes fixation better

Fixation stability depends substantially on the angular size of the reference target. Larger structured targets — particularly those with clearly defined edges at multiple orientations — drive stronger optokinetic and fixation-holding signals. The bull's-eye ring and crosshair provide high-contrast edges at 0° and 90° orientations across a ~0.3° annular band (0.3–0.6° radius), stimulating a broad population of foveal and parafoveal orientation-selective neurons whose sustained activity suppresses drift.

A small dot alone (diameter < 0.1°) can be difficult to fixate steadily because it subtends too few photoreceptors to drive reliable position-error signals.

### 6.3 The scaling problem with small apertures

A stimulus-appropriate fixation target should be scaled in proportion to the aperture so that it does not dominate the display or crowd the dot field. For a 3.3° aperture, a 0.6° fixation disc occupies 18% of the aperture diameter — already prominent. Scaling to 0.47× gives a 0.28° disc and commensurately smaller crosshairs.

The problem is that scaling down the target degrades fixation stability at exactly the aperture size where the exclusion zone is also smaller and drift most damaging. The small Catek aperture thus suffers a compounding disadvantage:

1. Smaller exclusion zone → easier for drift to push dots toward the fovea
2. Smaller fixation target → weaker stabilization signal → more drift
3. Lower eccentricity dots → larger fractional smear from any given drift amplitude

These three factors all act in the same direction and together could account for a substantial portion of the elevated UNCUED performance seen in the Catek condition — independent of any genuine eccentricity advantage.

> **Design recommendation:** Do not scale the fixation target below the current VRDots dimensions (0.6° outer disc, 0.24° center dot, 0.03° crosshair thickness) in future experiments. If a smaller aperture is required, either maintain the full-size target or compensate with a wider exclusion zone. The marginal gain from a proportionally smaller fixation target is not worth the reduction in fixation stability.

---

## 7. Integrated Assessment and Recommendations

| Parameter | Current VRDots | Assessment | Recommendation |
|---|---|---|---|
| Aperture diameter | 7° (r = 3.5°) | Good — peripheral eccentricity suppresses UNCUED, maximizing cueing effect | Maintain or increase; do not reduce below 7° |
| Dot density | 1.64/sq° (full-area) | Adequate — density has no effect up to 4.5/sq°; RF saturation not reached | No change needed; increase only for specific hypotheses |
| Exclusion zone | 1.1° radius | Good — comfortably exceeds microsaccade amplitude; prevents foveal contamination | Maintain ≥ 1.0°; never reduce below 0.8° |
| Fixation outer disc | 0.6° diameter | Good — structured surround stabilizes fixation; does not crowd dot field | Maintain; do not scale with aperture |
| Fixation center dot | 0.24° diameter | Good — precise foveal anchor without encroaching on crosshairs | Maintain |
| Crosshair thickness | 0.03° | Thin enough not to mask dots; thick enough to be visible | Maintain |

### 7.1 Priority concern: eye tracking

The central unresolved confound in the Catek comparison is the impossibility of distinguishing genuine eccentricity effects from drift artifacts without knowing the actual gaze position during each trial. Adding eye tracking — even at modest precision (0.5° RMS, readily achievable with the Quest Pro or an external tracker) — would allow post-hoc exclusion of trials with excessive gaze deviation and direct testing of the eccentricity hypothesis by sorting trials by realized dot eccentricity rather than nominal eccentricity.

### 7.2 The density ceiling experiment

The current data leave open the question of where the RF saturation regime begins. A systematic density series — holding the 7° aperture fixed and varying dots/field from 63 to ~800 (0.5 to ~20 dots/sq°, approaching inter-dot spacings comparable to RF diameters at 2° eccentricity) — would directly test the model's saturation prediction and identify the density at which the cueing effect begins to decline.

### 7.3 Bottom line

The current VRDots stimulus design is well-optimized for the cueing paradigm. The 7° aperture, 1.1° exclusion zone, and bull's-eye fixation target form a coherent design that maximizes the cueing effect (by placing dots in the periphery where UNCUED performance is suppressed), minimizes fixation artifacts (via a generous exclusion zone and a stabilizing fixation target), and provides interpretable data whose key parameters are under experimental control. The Catek-style small aperture, despite its higher published dot density and historical usage, is inferior on all three dimensions for the purposes of measuring object-based attentional cueing.
