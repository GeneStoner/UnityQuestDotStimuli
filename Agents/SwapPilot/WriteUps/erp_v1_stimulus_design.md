# Stimulus Parameters for Maximizing the Cued vs. Uncued ERP over V1

*G. Stoner · April 2026 · Analysis extending VRDots behavioral parameter study to EEG/ERP design*

---

## 1. What We Are Trying to Measure

The goal is a reliably detectable difference in the scalp ERP, time-locked to the translation onset, between trials where the observer was cued to attend to the translating field (CUED) and trials where they were not (UNCUED). For this difference to be localized to V1 specifically, it must appear in the C1 component: the earliest visual ERP deflection (~50–100 ms post-stimulus), generated in primary visual cortex within the calcarine sulcus, and identifiable by its polarity inversion across the horizontal meridian (positive for upper-field stimuli at Oz, negative for lower-field).

Two questions need to be addressed separately and then jointly: (a) what parameters maximize the *absolute amplitude* of the V1 ERP to the translation event, and (b) what parameters maximize the *proportional modulation* of that response by attentional cueing. These goals can conflict, and the analysis below traces those conflicts explicitly.

---

## 2. The Fundamental Problem: C1 Cancellation

This is the most important issue and must be addressed before optimizing any other parameter, because it affects every stimulus in the current VRDots design.

The C1 is generated in opposite banks of the calcarine sulcus for upper vs. lower visual field stimuli. Because the sulcal geometry means that upper-field generators point approximately opposite to lower-field generators relative to the scalp, their contributions to any given electrode partially or fully cancel when stimuli are distributed across both hemifields symmetrically:

- Upper visual field → inferior bank of calcarine → C1 positive at Oz
- Lower visual field → superior bank of calcarine → C1 negative at Oz

The current VRDots aperture is centered at fixation, distributing dots equally in upper and lower hemifields. The net C1 across a typical session is therefore near zero at all occipital electrodes — not because there is no V1 response, but because equal and opposite generators cancel at the scalp. This is not a weak signal; it is a structurally absent one.

> **Critical limitation of current design for ERP:** A circular aperture centered at fixation will produce a near-zero C1 regardless of all other parameter choices, because upper- and lower-field V1 generators cancel. This must be resolved at the level of stimulus geometry before anything else matters.

### 2.1 Solutions to the cancellation problem

**Option A — Single hemifield aperture.** Move the entire dot field to one visual hemifield — e.g., center the aperture at 3.5° above or below fixation. This eliminates cancellation entirely. The C1 will be large and clearly signed. The cost is that the stimulus is no longer rotationally symmetric around fixation, which changes the spatial relationship between the translation direction and the observer's fovea. The 8AFC response mapping also becomes asymmetric if the aperture is off-axis, though this can be handled analytically.

**Option B — Upper and lower apertures analyzed separately.** Retain the centered aperture but split dot responses by their screen-y position at the time of translation onset, and analyze upper- and lower-field contributions with inverted polarity alignment. This recovers the C1 from the cancellation by sign-flipping one field before averaging. It is analytically valid but requires more trials and introduces complexity in the attribution of translating dots to a hemifield.

**Option C — Off-center fixation.** Place the fixation target at the top or bottom of the aperture so that all dots fall in one hemifield. This creates an asymmetric exclusion zone but is geometrically clean for the C1.

Option A is the cleanest.

> **Primary design requirement for V1 ERP:** The dot field must be confined to a single visual hemifield (upper or lower). A centered circular aperture is incompatible with isolating a C1 response.

---

## 3. Dot Density: A Counterintuitive Inversion

The behavioral analysis established that dot density has no effect on the cueing effect between 1.6 and 5 dots/sq°. The ERP prediction inverts this: for measuring the *neural* cueing difference at V1, lower density is likely better.

The CUED vs. UNCUED ERP difference over V1 reflects the number of V1 neurons activated *exclusively* by the translating (cued) dots at the moment of translation onset. A neuron driven by both a cued and an uncued dot simultaneously generates a response that is not differentially modulated by the cue — it fires regardless of which field is attended, and its contribution cancels in the CUED − UNCUED contrast. Only neurons whose RF contains a cued dot but not an uncued dot (or vice versa) contribute a net difference signal.

At lower density, inter-dot spacing is larger relative to RF diameter, so a higher fraction of RFs contain a dot from at most one field. At higher density, more RFs straddle dots from both fields, the exclusively-cued population shrinks, and the difference signal decreases — even if the absolute ERP amplitude is larger.

```
Useful metric: fraction of RFs containing ≥1 dot from exactly one field
             ≈ exp(−ρ_A · A_RF) · (1 − exp(−ρ_B · A_RF))  +  symmetric term
where ρ_A, ρ_B = dot density per field, A_RF = RF area

This peaks when ρ · A_RF ≈ 0.5, i.e., one dot per two RFs on average.
At VRDots density (1.64/sq°) and RF area for 0.35° diameter: ρ·A_RF ≈ 0.16 — low
At HighDens density (4.5/sq°):                                 ρ·A_RF ≈ 0.43 — higher, closer to peak
```

This analysis suggests that HighDens is actually closer to the optimal density for maximizing the number of exclusively-cued neurons. However, this is only true for a perfect-fixation observer. Fixation imprecision enlarges the effective RF, shifting the effective ρ·A_RF upward — potentially pushing HighDens beyond the optimum for a poor-fixation observer while VRDots remains below it.

A further complication: more dots also means a stronger overall ERP (more V1 neurons active), which improves raw SNR. The optimal density for the ERP difference therefore balances two competing factors: maximizing the fraction of exclusively-field-specific RFs (favors lower density) against maximizing the absolute neural response that the difference is measured against (favors higher density). The peak is likely around ρ·A_RF ≈ 0.3–0.5, corresponding to roughly 3–5 dots/sq° at the eccentricities used — close to the Catek and HighDens values.

> **ERP density optimum:** The behavioral optimum (any density below RF saturation) and the ERP optimum (balance between RF exclusivity and overall signal amplitude) are different. For ERP, the optimal density is higher than for the behavioral task — somewhere near 3–5 dots/sq° at the relevant eccentricities — but this optimum degrades faster with fixation imprecision for higher densities.

---

## 4. Dot Size

The current dot diameter (0.08°) is substantially smaller than V1 RF diameters at the relevant eccentricities (0.2–0.5°). A single dot therefore subtends only a fraction of the RF of a V1 neuron that it drives. Larger dots drive V1 neurons more strongly by stimulating more of their spatial summation area, producing larger membrane potential deflections and higher firing rates, which translate to larger ERP amplitude.

The upper limit on useful dot size is approximately the RF diameter: once the dot exceeds the RF, further enlargement does not increase the response and begins to stimulate adjacent suppressive surrounds. For V1 at 2–3° eccentricity, the summation optimum (classical RF center) is approximately 0.2–0.4°. Current dots at 0.08° are 4–5× below this optimum in linear size — meaning V1 neurons are being driven at perhaps 20–40% of their maximum responsiveness by each dot.

> **Recommendation:** Increase dot diameter from 0.08° to 0.2–0.25° for ERP applications. This should approximately double the V1 ERP amplitude per dot with no additional cost in field mixing (dots remain well within individual RFs).

---

## 5. Contrast and Color

V1 responds to both luminance contrast (L+M cone opponent signals, magnocellular/parvocellular streams) and chromatic contrast. However, for the earliest V1 ERP component the magnocellular (luminance) pathway dominates: magnocellular neurons have faster conduction velocities and lower contrast thresholds, and they drive the C1 disproportionately. Chromatic (isoluminant) stimuli generate C1 responses that are smaller in amplitude and 10–20 ms later in latency.

The current VRDots stimulus uses red and green dots. Neither achieves the maximum luminance contrast available on the display. For ERP, white dots on a black background would drive V1 approximately 2–4× more strongly than current colored dots at the same spatial parameters, and the C1 would be earlier and cleaner.

The cost: color cannot then be used as a field-identity cue. An alternative is to retain color as the identity marker but maximize luminance contrast within each color, or to convey field identity by spatial offset or other non-luminance cues for the ERP paradigm.

> **Design tension:** Color as a field-identity cue and maximum luminance contrast for strong V1 drive are in conflict. For ERP studies where V1 amplitude is the dependent variable, luminance-defined fields (e.g., using dot-size differences or onset-timing alone as the identity cue, with white dots throughout) would be preferred over chromatic labeling.

---

## 6. Aperture Size and Eccentricity for ERP

The behavioral analysis showed that larger apertures (more peripheral dots) suppress UNCUED performance, increasing the behavioral cueing effect. For ERP, the eccentricity argument partially reverses: cortical magnification means that foveal and near-foveal stimuli generate disproportionately large V1 ERP amplitudes because more cortical tissue is devoted to the central visual field. Stimuli at 3° eccentricity activate far less cortical tissue per dot than stimuli at 0.5° eccentricity.

The optimal eccentricity for V1 ERP is therefore lower than the behavioral optimum — closer to the fixation point. The exact optimum depends on the exclusion zone and the single-hemifield constraint, but a range of roughly 1–4° eccentricity is typical for studies targeting C1.

A practical consequence: a smaller aperture (e.g., 4–5° diameter) positioned entirely in the upper or lower hemifield may yield a larger absolute C1 than the current 7° centered aperture — both because dots are at more magnified eccentricities and because the cancellation problem is resolved.

### 6.1 The aperture size trade-off for the ERP difference specifically

- **More dots (larger aperture or higher density) → larger absolute ERP → better SNR for detecting a difference.** This favors a larger aperture.
- **Lower eccentricity → stronger cortical response per dot → stronger absolute ERP per dot.** This favors a smaller, more central aperture.
- **Peripheral eccentricity → suppressed UNCUED → larger behavioral cueing effect, but does this translate to a larger neural cueing effect?** Not necessarily. Behavioral UNCUED suppression reflects inability to use the UNCUED field's signal; the ERP difference reflects the neural enhancement of the CUED field's signal. These are dissociable.

> **For ERP:** A smaller, eccentric aperture placed entirely in one hemifield (e.g., 4° diameter centered at 2–3° above or below fixation) likely produces a larger absolute C1 amplitude per dot than the current 7° centered aperture, due to cortical magnification and the elimination of cancellation. Whether the CUED−UNCUED *modulation* of this larger response is also larger is an open empirical question.

---

## 7. Temporal Parameters

### 7.1 Translation speed and duration

The translation event (80 ms, 2.26°/sec, total displacement ~0.18°) is what the ERP is time-locked to. For a strong V1 motion response, faster and longer-duration translations would drive direction-selective V1 cells more strongly. However, they also increase the proportion of dots that translate outside their originating RF during the response window, reducing the temporal precision of the onset response. A 50–100 ms translation at 3–5°/sec would likely optimize the trade-off between response amplitude and temporal precision for the C1.

### 7.2 Onset asynchrony and ERP overlap

The current 750 ms delay between field A onset and field B onset is long enough that the field-B onset ERP (C1, P1, N1) has decayed before translation onset (which occurs a further 300 ms after field-B onset). This is good for isolating the translation-onset ERP. The temporal structure of the current paradigm is well-suited to ERP in this respect.

### 7.3 Trial rate and averaging requirements

ERP studies typically require 50–200 artifact-free trials per condition for adequate signal averaging. The current paradigm generates 256 CUED and 256 UNCUED trials per session, which is borderline adequate but should be considered a minimum. The inter-trial interval should be at least 1 s to allow ERP baseline recovery.

---

## 8. Fixation Requirements and Artifact Considerations

ERP recordings impose stricter fixation requirements than behavioral-only studies, for two reasons beyond those discussed in the behavioral parameter analysis.

**Saccade artifact.** Any saccade produces a large electro-ocular artifact (step function in the EOG) that contaminates the ERP for 200–400 ms. In the current paradigm, where the critical window is 50–300 ms post-translation-onset, a single microsaccade during this window may require the trial to be rejected. With a standard eye-movement rejection threshold, 20–40% of trials may be lost for typical observers, necessitating substantially more trials.

**Drift-induced spatial smear degrades the C1 specifically.** As established in the behavioral parameter analysis, fixation drift enlarges the effective RF and mixes cued and uncued responses. For the C1 ERP difference, this is even more damaging than for behavior: the behavioral system can integrate across trials and observers, partially averaging out fixation noise, but the single-trial neural response must produce a clean field-specific signal on each trial for the ERP average to reflect genuine attentional modulation rather than noise. Poor fixation therefore degrades the ERP difference more severely than it degrades behavior, and eye-tracking-based trial rejection is essentially mandatory for a clean result.

> **Fixation requirements for ERP:** Eye tracking with online monitoring is required, not optional. Minimum standard: reject trials with any saccade > 0.5° during the [-200, +300] ms window around translation onset, and any drift exceeding 1.0° from fixation at any point during the trial. This will eliminate a substantial fraction of trials; plan for 600–800 trials per condition to yield the required 200+ artifact-free trials.

---

## 9. Integrated Parameter Recommendations

| Parameter | Current VRDots | Behavioral optimum | ERP/V1 optimum | Conflict? |
|---|---|---|---|---|
| Aperture position | Centered at fixation | Centered (symmetric) | Single hemifield (upper or lower) | **Yes — fundamental** |
| Aperture diameter | 7° | ≥ 7° (larger = better behavioral effect) | 4–6° (cortical magnification + hemifield constraint) | **Yes — moderate** |
| Dot density | 1.64/sq° | Indifferent (1.6–5.0/sq°) | 3–5/sq° (balance RF exclusivity vs. amplitude) | No |
| Dot size | 0.08° diam | Indifferent (below RF grain) | 0.2–0.25° (RF summation optimum) | No |
| Dot contrast | Chromatic (R/G) | Chromatic OK (field identity cue) | High luminance (white on black) | **Yes — moderate** |
| Eccentricity range | 1.1–3.5° | As peripheral as possible | 1–4° in one hemifield | Partial |
| Exclusion zone | 1.1° | ≥ 1.0° | ≥ 0.5° from hemifield edge nearest fixation | No |
| Fixation target | Bull's-eye, 0.6° disc | Large, structured | Same, with online eye tracking for trial rejection | No |
| Trials per condition | 256 | 256 adequate | 600–800 pre-rejection (target 200+ clean) | No (just more sessions) |
| Translation speed | 2.26°/sec | Matched to behavioral threshold | 3–5°/sec (stronger V1 motion response) | Partial |

---

## 10. The Most Important Single Change

If only one modification can be made to the current VRDots design for ERP work, it is relocating the aperture to a single hemifield. Every other parameter optimization operates on a signal that is currently near zero at the scalp due to upper/lower cancellation. Increasing dot size, density, or contrast amplifies a signal that is already being recovered; resolving the cancellation creates the signal in the first place.

A practical proposal: retain the 7° diameter aperture but shift its center to 3.5° above fixation (placing all dots in the upper visual field, with the bottom edge of the aperture touching the horizontal meridian). The exclusion zone remains ~1.0–1.1° from fixation, now applied to the nearest aperture edge rather than a centered radius. The C1 polarity at Oz will be consistently positive. All behavioral analyses and trial-counting logic remain identical. The translating field's eccentricity range shifts to approximately 0–7° above fixation (mean ~3.5°), similar to the current behavioral paradigm.

---

## 11. Does Khoe et al. (2005) Contradict the Cancellation Argument?

Khoe, Mitchell, Reynolds & Hillyard (2005, *Vision Research* 45:3004–3014) used transparent superimposed rotating dot surfaces — the same stimulus class as VRDots — centered at fixation, and found a clearly significant early ERP modulation in the C1 latency range (75–110 ms) driven by exogenous cueing of one surface. Several factors reconcile the findings.

### 11.1 The cruciform model is an idealization

Perfect cancellation requires perfect geometric symmetry. Real calcarine sulci are neither perfectly symmetric across individuals nor perfectly cruciform in folding geometry. With enough trials and careful electrode placement, the residual non-cancelled signal — even 10–20% of the full-field amplitude — may reach significance in a well-powered ERP study. This is likely the primary reason Khoe et al. observed a C1-latency effect: cancellation is real but imperfect.

### 11.2 Rotating stimuli are instantaneously asymmetric

A rotating dot surface is not a static pattern. At the moment of the exogenous cue, dots in each field are at specific angular positions. Unless the cue is delivered precisely when the dot distribution is perfectly symmetric across the horizontal meridian — which occurs only twice per revolution — the instantaneous dot distribution is asymmetric. Across trials these asymmetries average toward zero, but not perfectly: if the rotation phase at cue onset is not uniformly randomized, a consistent net imbalance can accumulate in the average.

### 11.3 Object-based attention produces spatially non-uniform V1 gain

When an observer selects one transparent surface over another, the attentional gain applied to the cued surface's dots is not guaranteed to be vertically symmetric — it depends on where those particular dots are at the moment the attentional signal reaches V1. The feedback signal targets neurons whose RFs currently contain a cued dot, and because the cued surface's instantaneous dot positions are distributed unevenly across the vertical meridian at any given moment, the attentional gain modulation in V1 is likewise uneven, leaving a non-cancelled residual in the ERP average.

### 11.4 The C1-latency response may not be exclusively V1

As cautioned by Ales, Yates & Norcia (2010, *NeuroImage* 52:1401–1409), V2 and V3 also produce scalp polarity reversals across the horizontal meridian. Critically, V2 and V3 do not have the same symmetric cruciform geometry as V1: their contributions do not cancel in the same way for a centered stimulus. A centered aperture may produce a near-zero V1 C1 through cruciform cancellation while still producing a net non-zero contribution from V2/V3 at the same latency.

> **Synthesis:** Khoe et al. (2005) does not falsify the cancellation argument — it illustrates that cancellation is probabilistic rather than absolute. The residual C1-latency signal in a centered rotating-surface display likely reflects a combination of: (1) imperfect anatomical cancellation across individuals; (2) instantaneous rotational asymmetry of the dot distribution at cue onset; (3) spatially non-uniform attentional gain on the cued surface; and (4) possible extrastriate contributions not subject to cruciform cancellation. For a well-powered group study, a significant C1-latency effect can be recovered from a centered aperture — but the amplitude will be a fraction of what a single-hemifield placement would produce, and the V1 attribution is less certain.

---

## 12. Steady-State Alternative — and Its Cancellation Problem

One approach with substantially better SNR than transient ERP is frequency-tagging (steady-state visual evoked potential; SSVEP). If the two dot fields are modulated at different temporal frequencies — field A flickering at f₁ (e.g., 8 Hz) and field B at f₂ (e.g., 11 Hz) — the response at each frequency isolates that field's neural representation. Attentional modulation appears as a change in amplitude at the attended field's frequency.

However, a correction is needed: **SSVEP suffers from exactly the same upper/lower cancellation problem as transient C1 ERP.** The scalp potential is generated by the same V1 dipoles with the same geometry; the fact that the analysis is performed in the frequency domain rather than the time domain does not change the underlying source cancellation. The Fourier transform of a near-zero time-domain signal is also near-zero at every frequency, including the tagged frequency. Frequency tagging resolves the problem of *separating the two fields' responses from each other*, but it does not resolve the upper/lower cancellation within each field's response.

What SSVEP does offer: the steady-state signal integrates over many cycles, making it more robust to the trial-by-trial rotational phase asymmetry that allows Khoe-style residual signals to survive averaging. SSVEP may therefore be *less* likely than transient ERP to produce a spurious apparent C1 from asymmetric rotation phase, and correspondingly more honest about what a centered aperture can and cannot provide.

> **Summary:** The single most important design change for V1 ERP is relocating the aperture to a single hemifield. Secondary gains — larger dots (0.2–0.25°), higher luminance contrast, density near 3–5 dots/sq°, eye tracking for trial rejection — each add 20–50% in sensitivity. The Khoe et al. (2005) result shows that a residual C1-latency signal can survive in a centered rotating-surface display, but its amplitude is reduced relative to a hemifield design and its V1 attribution is less certain. SSVEP offers superior SNR but does not escape the cancellation problem and requires hemifield placement for the same reasons.
