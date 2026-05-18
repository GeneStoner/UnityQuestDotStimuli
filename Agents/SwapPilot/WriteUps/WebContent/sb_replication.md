# Replicating Stoner & Blanc (2010) in Virtual Reality

## Background and Motivation

A central question in visual neuroscience is whether the brain selectively processes entire perceptual surfaces — coherent regions of the visual scene defined by common motion, color, or depth — rather than processing individual features or spatial locations in isolation. The transparent-motion paradigm introduced by Valdes-Sosa et al. (2000) has become a key tool for probing this question. In this paradigm, two superimposed dot fields rotate in opposite directions, and a brief translation of one field is embedded among the rotations. Observers must report the direction of the translation. The critical manipulation is whether the translating field was "cued" by a delayed onset relative to the other field. Across many studies, translations of the cued (delayed-onset) field are judged more accurately than translations of the uncued field — a performance asymmetry taken as evidence that attention tracks perceptual surfaces rather than locations or features.

[Stoner & Blanc (2010)](https://doi.org/10.1016/j.visres.2009.11.015) made an important contribution to this literature by testing a motion-competition alternative to the surface-based account. Their alternative proposed that the performance asymmetry arises not from surface-based attention but from differential adaptation of motion-selective neurons: the rotation competing with a cued translation is older (more adapted) than the rotation competing with an uncued translation, so the cued translation faces less suppression and is thus more detectable. Stoner & Blanc tested this by introducing "motion swaps" — reversals of the non-translating field's rotation direction at the moment of translation — which, under the motion-competition account, should have reversed the performance asymmetry. Crucially, motion swaps did not reverse the asymmetry, and neither did color swaps designed to probe a related color-duration confound. These results strongly favor surface-based selection as the underlying mechanism.

We sought to replicate Stoner & Blanc's core findings using a virtual reality implementation of the transparent-motion paradigm. This serves two purposes. First, replicating established psychophysical effects in a VR headset validates our experimental apparatus and confirms that the stimulus, rendered on a head-mounted display rather than a conventional monitor, produces the expected perceptual phenomena. Second, the VR platform opens new avenues for extending this work — including manipulation of binocular disparity to separate the two dot fields in depth, variation of stimulus parameters across a broader range, and eventual neuroimaging with concurrent EEG or fMRI — that would be difficult or impossible with conventional displays.

---

## Methods

### Stimulus

Two circular fields of randomly distributed dots were superimposed at the center of the display, identical in configuration to Stoner & Blanc. The two fields rotated in opposite directions (clockwise and counterclockwise) about the fixation point. One field was rendered in red, the other in green; colors were equiluminant as determined by heterochromatic flicker photometry prior to testing. A brief translation of one field was embedded within the rotation sequence; observers reported the direction of the translation by selecting one of eight directions (45° increments) on a controller.

Each field consisted of 63 dots occupying a circular aperture of 2.0° radius (4.0° diameter), giving a dot density of approximately 5 dots/deg²/field — matching Stoner & Blanc's reported density of 5 dots/deg². Individual dots subtended 0.08° of visual angle. Both fields rotated at 81°/sec. Translation speed was 2.26°/sec. Within each field, 50% of dots translated coherently in the stimulus direction; the remaining dots moved in random directions (noise dots), consistent with the partial-coherence design of Stoner & Blanc (who used 40–55% coherence, varied randomly).

### Trial timeline

Each trial began with a 750-ms period during which only one dot field was present and rotating (the "delayed-onset" field had not yet appeared). The second field then appeared and both rotated together for 300 ms. Following this dual-rotation period, either the delayed-onset field translated briefly ("cued" trial) or the always-on field translated ("uncued" trial). Translation duration was 44 ms (~4 frames at 90 Hz; Stoner & Blanc used 40 ms, 3 frames at 75 Hz). A 500-ms post-translation rotation period followed before the observer responded.

### Swap conditions

We tested two conditions:

- **N (no swap):** The standard delayed-onset design. No features are altered at translation onset. The cued field is defined solely by its delayed onset.
- **MC (motion + color swap):** At the onset of translation, the non-translating field reverses its rotation direction (motion swap) and both fields exchange colors (color swap). This is the most stringent test of surface-based selection: if the performance asymmetry is driven by surface identity rather than motion history or color duration, it should survive this combined manipulation.

### Apparatus

Stimuli were rendered in Unity and displayed on a Meta Quest 3 VR headset at 90 Hz. The observer was seated and wore the headset comfortably. Virtual viewing distance was set to 2 m. A fixation target (bull's-eye + crosshair, 0.4° radius) was displayed at the center of the field throughout each trial. Responses were made via the Quest controller trigger.

### Observer

One observer (G.S., the author) completed two full sessions of each condition (~512 trials per session, 1024 trials total). The observer was fully informed of the experimental design. Data from a single well-practiced observer should be interpreted as a proof-of-concept replication rather than a group-level result; extension to naïve observers is planned.

### Differences from Stoner & Blanc

| Parameter | Stoner & Blanc (2010) | VRDots |
|---|---|---|
| Display | CRT monitor, 75 Hz | Meta Quest 3 VR headset, 90 Hz |
| Viewing | Chin/forehead rest, 57 cm | Head-mounted, ~2 m virtual |
| Translation duration | 40 ms (3 frames @ 75 Hz) | 44 ms (4 frames @ 90 Hz) |
| Dot size | 0.03° (1 pixel) | 0.08° |
| Coherence | 40–55% (random) | 50% (fixed) |
| Observers | 11 naïve (Exp. 1), 9 (Exp. 2) | 1 (author, pilot) |
| Swap conditions | Motion-only; color-only; combined | N; combined motion+color (MC) |
| Response | Numeric keypad | VR controller |

The aperture size (r = 2.0°), dot density (~5 dots/deg²), rotation speed (81°/sec), translation speed (2.26°/sec), delayed onset (750 ms), and 8-AFC direction judgment were all matched to Stoner & Blanc.

---

## Results

Results are expressed as the cueing effect: percent correct on cued trials minus percent correct on uncued trials (Δpp). A positive value indicates better performance when the delayed-onset field translates. Chance performance is 12.5% (1/8 directions). Error bars are 95% binomial confidence intervals.

### No-swap condition (N)

Translations of the delayed-onset (cued) field were judged more accurately than translations of the always-on (uncued) field:

**CUED: 65.2%  ·  UNCUED: 48.4%  ·  Δ = +16.8 pp  (95% CI ±8.6,  p < 0.001,  n = 512 trials)**

This replicates the core finding of Stoner & Blanc: delayed onset confers a robust performance advantage, consistent with surface-based attentional selection.

### Motion + color swap condition (MC)

When the non-translating field reversed rotation direction and both fields exchanged colors at translation onset, the cueing advantage was preserved and, if anything, slightly larger:

**CUED: 70.7%  ·  UNCUED: 50.8%  ·  Δ = +19.9 pp  (95% CI ±8.5,  p < 0.001,  n = 512 trials)**

The cueing advantage survived the combined motion and color swap. This replicates the key result of Stoner & Blanc: the performance asymmetry is not driven by motion history (adaptation) or color duration, but reflects selection of the surface defined by delayed onset.

---

## Summary

| Condition | CUED | UNCUED | Δ (pp) | 95% CI | Sig. |
|---|---|---|---|---|---|
| N  (no swap) | 65.2% | 48.4% | +16.8 | ±8.6 | *** |
| MC (motion+color swap) | 70.7% | 50.8% | +19.9 | ±8.5 | *** |

The magnitude of our cueing effects (≈ +17 to +20 pp) is comparable to those reported by Stoner & Blanc using conventional CRT-based stimuli. The replication confirms that the transparent-motion paradigm, implemented in a VR headset, yields robust surface-based selection effects consistent with the established literature. These findings establish our VR platform as a valid tool for extending this line of research.

---

*Stoner GR & Blanc G (2010). Exploring the mechanisms underlying surface-based stimulus selection. Vision Research, 50(2):229–238. doi:10.1016/j.visres.2009.11.015*
