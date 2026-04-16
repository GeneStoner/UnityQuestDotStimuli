# Depth-Swap Motivation — Working Draft

*Pooled from: `depth_experiments_intro.md` §1 + `integrated_review.md` Group 1*
*Purpose: raw material for a short motivating paragraph for the depth-swap experiments*

---

## FROM INTEGRATED_REVIEW — PARADIGM LINEAGE (what we already know)

**Valdes-Sosa, Cobo & Pinilla (1998). Cognition 64:3.**
Established that observers selectively attend to one of two superimposed transparent random-dot surfaces without any spatial separation between them. The same-surface advantage cannot be attributed to spatial attention. Foundational demonstration that the unit of visual selection can be a motion-defined surface, not a location.

**Valdes-Sosa, Cobo & Pinilla (2000). J Exp Psych: HPP 26:488.**
Introduced the delayed-onset translation cue that VRDots directly inherits: one surface briefly translates at display onset (cue), followed by a translation in the same or opposite surface (target). The effect is exogenous — it survives divided-attention conditions and does not require deliberate surface tracking.

**Reynolds, Alborzian & Stoner (2003). Vision Research 43:59.**
A single brief translation is sufficient to engage surface-based attention; the cueing effect is produced by an exogenous mechanism. Selection is rapid and automatic.

**Stoner & Blanc (2010). Vision Research 50:229.**
Directly refuted motion-duration confound accounts: reversing the motion-duration asymmetry did not reverse the cueing advantage. The effect tracks which dots were cued, not which direction had a processing advantage. Also established that selection operates at the spatial scale of individual dots (not just the direction channel), motivating the V1 Point-Set model.

**Valdes-Sosa et al. (2010).**
Ruled out temporal asynchrony as an alternative explanation. The cueing advantage persists under temporal control, confirming it reflects surface identity, not simply timing.

**Mitchell, Stoner & Reynolds (2004). Nature 429:410.**
The same onset-translation cue determines which of two rivalring binocular surfaces dominates perception. The translating-dot cue operates on the level of perceptual surface representations — it selects a surface, not a motion direction or spatial region — and engages genuine perceptual competition, not merely decision-level bias.

**Mitchell, Stoner, Fallah & Reynolds (2003). Vision Research.**
Surface-based cueing persists when both fields have the same color, ruling out color-channel gain as a necessary mechanism. Selection cannot be reduced to any feature dimension that merely distinguishes the two surfaces.

---

## FROM DEPTH_EXPERIMENTS_INTRO §1 — WHY DEPTH? (motivation for the extension)

### What features define the attended surface?

The delayed-onset cueing effect is not reducible to a simple spatial expectancy. The benefit does not arise merely from knowing which side of the display will undergo coherent motion, nor from directing attention to a broad spatial region. Rather, the cue appears to select the specific set of dots that will ultimately translate — a selection that must be spatially fine-grained and distributed across the entire aperture. This dot-specificity implies that the attentional mechanism tracks a structured, distributed object — something more like a surface representation than a spotlight or an orientation of expectancy.

This raises the question of what features define the attended surface. In the baseline paradigm, the two dot fields are distinguished only by their temporal onset asynchrony and, once both are visible, by their opposite rotation directions. The delayed-onset translation cue binds to one field, and that binding evidently persists through the pre-translation delay and into the translation epoch itself. What exactly is being held in memory across this delay? What constitutes the attentional "handle" on the cued surface?

### Depth-plane identity as a candidate

A natural candidate: when two superimposed transparent dot fields are viewed binocularly, they tend to be perceived as occupying different depth planes — one appearing in front of the other. The attentional mechanism that maintains the cued-surface representation across the delay interval may be operating partly on the basis of depth-plane identity — a representation of "the nearer surface" or "the farther surface" rather than (or in addition to) "the surface rotating clockwise" or "the surface composed of specific dot tokens." Under this view, depth-plane membership would function as a grouping signal that supports coherent representation of the cued object across time.

### The key question for depth-swap experiments

If depth-plane membership is a component of the surface representation, this generates a specific question: what happens when that membership is disrupted at the moment of target evaluation? The cued dots were registered as occupying, say, the far depth plane during the delay period; if they are displaced to the near depth plane precisely at the onset of translation, does the attentional pointer follow them, fail to follow them, or update to the vacated plane?

The ZdA/ZdB design provides the critical test. ZdA disrupts depth-plane continuity for the coherent (cued) translating object at tStart; ZdB preserves the cued object's depth identity while displacing the background incoherent dots. The two conditions are matched for the total amount of depth change in the scene — the only difference is *which* dots change. If depth-plane membership is a constitutive feature of the attentional object, ZdA should hurt cueing and ZdB should not; if the effect is due to general scene disruption, both should hurt equally. The UNCUED arm serves as the control: if depth changes help or hurt performance independent of cueing, it should appear there too.

### What introducing stereo depth adds

In the baseline experiment, depth planes are assigned in a semi-arbitrary way on each trial, with no stable stereoscopic signal distinguishing them. Introducing stereoscopic depth via the Meta Quest 3 makes the depth planes explicit, stable, and parametrically variable — allowing a direct test of whether depth-plane membership modulates the cueing effect and, if so, how.

---

## NOTES FOR DRAFTING

- The core logical chain: exogenous cue selects a surface (not a location, not a feature) → the selected surface is held across a delay → depth-plane identity is a candidate feature of the held representation → depth-swap at tStart tests whether depth is constitutive of that representation
- Key contrast to establish upfront: what makes this paradigm special is that attention can't be to a *location* (both surfaces are everywhere) and can't be to a *direction* (not known in advance) — so what IS the attentional handle?
- The ZdA/ZdB matched-disruption logic is the cleanest sentence: same total scene depth change, different object (CUED vs distractor) — any differential effect isolates object-specific depth identity
- ⚠️ Results caveat: ZdA/ZdB and F2 depth-swap disruption results are pre-fix and unconfirmed in clean data. The motivation paragraph can be written based on the logic/design — but don't assert the results as established in any text that will be shared externally.

---

## DRAFT TWO-PARAGRAPH SUMMARY (collaborator-oriented, SfN-abstract style)
## — lightly edited from GS draft; [COMMENTS] inline —

Numerous studies using transparent motion stimuli composed of two counter-rotating random-dot fields have found evidence of what has been characterized as "object-based" or "surface-based" attention (Valdes-Sosa, Cobo & Pinilla, 1998, 2000; Reynolds, Alborzian & Stoner, 2003; Mitchell, Stoner & Reynolds, 2004). In a typical version of this paradigm, two overlapping random-dot fields rotate in opposite directions within a circular aperture; at display onset, one field briefly translates (the "cue"), and after a short delay, either the same (cued) or the opposite (uncued) field translates again — and the observer reports its direction. Performance is substantially higher in the cued condition, an advantage that cannot be attributed to spatial attention or foreknowledge of which direction will appear. Stoner and Blanc (2010) found that these effects cannot be explained by feature-based competition, ruling out existing normalization models. Critically, they found that the performance advantage was specific to the individual dots of the cued dot field. Catak et al. (2022) replicated their overall findings and extended them using ERP, showing that the N1 component was specifically enhanced for the cued surface even when the motion directions of the two fields were swapped mid-trial, further ruling out direction-based accounts. These studies suggest that the visual system somehow "tags" the subset of dots belonging to the cued dot field. Given that this subset is intermixed with other rapidly moving dots, how such tagging might occur is a mystery (though see Stoner & Blanc, 2010; Catak et al., 2022), but one candidate framework follows from the observation that transparent motion stimuli are typically perceived as one surface moving atop another (Stoner, Albright & Ramachandran, 1990; Mamassian & Wallace, 2010). This suggests that perceived depth or depth-order may be an organizing principle underlying the surface-based attention effects observed in these experiments.

In these new experiments, we investigated the role of depth and depth-order by explicitly introducing depth from binocular disparity differences between the two dot fields. On some trials, we switched the depth planes of some or all of the dots at the moment the target translation began, to determine whether depth impacted the performance benefit. Across conditions we found a robust advantage for judging translations occurring in the far depth plane relative to the near depth plane — an asymmetry that was entirely absent under monocular viewing, confirming a stereoscopic origin. In conditions where the depth plane of the cued (translating) field was switched at the moment of translation, we observed [PROVISIONAL: reduction in the cueing benefit — see note below]. A complementary condition in which only the non-cued field changed depth planes — matched for the total amount of depth change in the scene — [PROVISIONAL: did not produce a comparable reduction]. The selectivity of the effect for the cued field's depth identity, rather than general scene-level disruption, is consistent with depth-plane membership functioning as a constitutive feature of the attended surface representation.

---

[COMMENTS FOR POLISHING]

1. PARADIGM DESCRIPTION: The lifted sentence is a reasonable placeholder but could be tightened. Consider whether to mention the 8-AFC direction judgment explicitly (that's the VRDots version) or keep it generic to the broader paradigm.

2. CATAK ET AL. SENTENCE: Currently ends vaguely after "extending them." The completion added here (N1 + direction-swap) is accurate per the paper. You may want to add the behavioral replication sentence more explicitly: "…replicated the behavioral cueing advantage and showed using ERP that N1 amplitude was specifically modulated by surface cuing even under mid-trial feature swaps, ruling out direction-based accounts."

3. DEPTH-ORDER REFS: Stoner et al. 1990 and Mamassian & Wallace 2010 are the strongest citations for the "one surface atop another" observation. Could also add Chopin & Mamassian (2011, J Vision) which shows top-down attention itself biases perceived depth order — a neat reciprocal observation.

4. ⚠️ DEPTH-SWAP RESULTS (second paragraph): The ZdA/ZdB disruption findings are currently marked PROVISIONAL because the pre-fix sessions had a stimulus artifact (spurious upward motion at depth-swap frames) that inflated the apparent disruption. Post-fix data are being collected. Options for the collaborator summary: (a) describe the design and leave the result clause vague ("preliminary results suggest…"), (b) report the pre-fix numbers with a caveat footnote, or (c) omit the quantitative result and frame as ongoing. Recommend (a) for now.

5. FAR > NEAR ASYMMETRY: This is the cleanest new result (artifact-independent, measured from no-swap trials only) and deserves a stronger sentence. The current draft buries it. Consider making it a separate sentence: "Strikingly, the benefit was consistently larger for translations occurring in the far depth plane than the near depth plane, an asymmetry that was entirely absent under monocular viewing and thus requires binocular disparity."

6. SECOND PARAGRAPH ENDING: Currently trails off. Needs a forward-looking sentence — e.g., "Together, these findings suggest that depth-plane identity may be a component of the attentional representation that maintains selection across the cue-to-target delay, though further experiments with artifact-controlled stimuli are underway to characterize the disruption effect."

7. TONE: Currently sits between accessible and technical. For the Turkish collaborators, worth deciding: are they being oriented to the paradigm from scratch, or do they know surface-based attention? If the latter, para 1 can be compressed.

