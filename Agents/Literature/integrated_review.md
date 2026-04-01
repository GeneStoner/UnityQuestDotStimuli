# VRDots — Integrated Literature Review
**Created**: 2026-04-01
**Maintainer**: Literature Agent
**Update policy**: Part I (paper summaries) — stable; update only for errors. Part II (integrated synthesis) — update when new papers are integrated or theoretical framing shifts. Part III (ongoing experiments) — update after each experimental session or interpretive revision.

---

# PART I — Per-Paper Summaries

Organized by subject group. All 39 currently integrated references. Bold = local PDF confirmed.

---

## Group 1: VRDots Paradigm Direct Lineage

**1. Valdes-Sosa, Cobo & Pinilla (1998). *Cognition* 64:3.**
Established that observers selectively attend to one of two superimposed transparent random-dot surfaces without any spatial separation between them. Accuracy for detecting a property change on a target surface was substantially higher when a prior event (probe) occurred on the same surface versus the other surface — a same-surface advantage that cannot be attributed to spatial attention. Foundational demonstration that the unit of visual selection can be a motion-defined surface, not a location.

**2. Valdes-Sosa, Cobo & Pinilla (2000). *Journal of Experimental Psychology: Human Perception and Performance* 26:488.**
Introduced the delayed-onset translation cue that VRDots directly inherits: one surface briefly translates at display onset (cue), followed by a translation in the same or opposite surface (target). Showed the effect is exogenous — it survives divided-attention conditions and does not require deliberate surface tracking. Established the cue-target paradigm logic: the onset translation is a surface cue, and subsequent detection on the cued surface is facilitated.

**3. Reynolds, Alborzian & Stoner (2003). *Vision Research* 43:59.**
Demonstrated that a single brief translation (not a prolonged motion event) is sufficient to engage surface-based attention and that the cueing effect is produced by an exogenous mechanism. Confirmed the exogenous nature of the cue and its ability to drive selective surface processing with minimal temporal investment.

**4. Stoner & Blanc (2010). *Vision Research* 50:229.** ✓ PDF
Directly refuted the motion-duration confound account of surface cueing: reversing the motion-duration asymmetry between surfaces (so the distractor had longer motion history) did not reverse the cueing advantage. This is the key disproof of pure adaptation/normalization accounts — the effect tracks which dots were cued, not which direction had a processing advantage. Also established that selection operates at the spatial scale of individual dots (not just the direction channel), motivating the V1 Point-Set model.

**5. Valdes-Sosa et al. (2010).**
Ruled out temporal asynchrony as an alternative explanation of the cueing effect by equating temporal intervals between cue and target while varying whether cue and target occurred on the same or different surfaces. The cueing advantage persists under temporal control, confirming it reflects surface identity and not simply timing.

**6. Mitchell, Stoner & Reynolds (2004). *Nature* 429:410.** ✓ PDF
Showed that the same onset-translation cue paradigm determines which of two rivalring binocular surfaces dominates perception. Cueing one surface increases its predominance in rivalry. This established that the translating-dot cue operates on the level of perceptual surface representations — it selects a surface, not a motion direction or spatial region — and that the mechanism engages genuine perceptual competition, not merely decision-level bias.

**7. Mitchell, Stoner, Fallah & Reynolds (2003). *Vision Research*.**
Demonstrated that surface-based cueing persists when both transparent fields have the same color, ruling out color-channel selection as the mechanism. If selection were accomplished by modulating input to the color channel representing the cued surface, removing color differences should abolish the effect. It does not. Selection operates on motion-coherent surface identity, not on any feature dimension that distinguishes the two surfaces per se.

---

## Group 2: ERP and Neural Correlates

**8. Valdes-Sosa, Bobes et al. (1998). *Journal of Cognitive Neuroscience* 10:137.**
First electrophysiological evidence that surface switching in transparent-motion displays modulates early ERP components (P1), even without spatial shifts of attention. The P1 modulation is non-spatial in origin, consistent with surface-level selection rather than spatial allocation of attention.

**9. Khoe, Mitchell, Reynolds & Hillyard (2005). *Vision Research* 45:3004.** ✓ PDF (= HillyardReynoldsOurParadigmEEG.pdf, duplicate)
Recorded ERPs during the translating-dot paradigm and found that C1 (75–110ms) and N1 (160–210ms) components are enhanced for the attended surface relative to the unattended surface. C1 enhancement implicates V1/V2, establishing that surface-based selection modulates the earliest cortical stages via feedback. The effect survives same-color conditions, consistent with Mitchell et al. (2003). Surface selection is rapid, established within ~100ms of the onset cue.

**10. Schoenfeld, Tempelmann et al. (2003). *PNAS* 100:11806.** ✓ PDF
Combined ERP and fMRI to show that when a transparent surface is attended, the irrelevant color feature of that surface is automatically activated in fusiform cortex within ~150ms of motion onset. This is the neural evidence for feature spreading: attending to a surface's motion direction automatically and rapidly activates the surface's color representation, consistent with integrated object-based selection. Key evidence for the V1 Point-Set model's prediction that direction-column selection spreads to co-active color columns.

**11. Schoenfeld, Hopf et al. (2014). *Nature Neuroscience* 17:619.** ✓ PDF
MEG study showing that attending to a motion-defined transparent surface produces a sequential cascade of feature-module activation: motion areas activate first, color areas ~60ms later. The temporal gap and ordering are consistent with feedforward propagation of the attentional signal through the feature processing hierarchy, initiated at the motion-processing stage. This is the most direct evidence for the time course of feature spreading from an attended surface.

**12. Ciaramitaro, Mitchell, Stoner, Reynolds & Boynton (2011). *Journal of Neurophysiology*.**
fMRI study showing that attending to one of two superimposed translating-dot surfaces enhances BOLD responses in V1–V3, co-localized with the shared retinotopic footprint of both surfaces. Demonstrates that surface-based attention has its cortical locus in early visual areas, not only in MT or higher areas. Most direct neural evidence that the VRDots paradigm engages genuine surface-selective early cortical processing.

**13. Catak, Özkan, Kafaligonul & Stoner (2022). *Cortex* 151:89.** ✓ PDF
Conducted behavioral and ERP study using feature-swap conditions (swapping direction or color of the two surfaces mid-trial) and showed that N1 ERP is modulated by cueing even under these feature-swap conditions, ruling out feature-based explanations. N1 amplitude correlated with behavioral cueing effects. Also contains the published description of the V1 Point-Set model (§4.2, §4.7), attributing the surface-specificity of cueing to dot-level spatial identity enforced by recurrent excitatory connections within V1 direction columns.

**14. Rodríguez & Valdés-Sosa (2006). *Brain Research* 1072:110.** ✓ PDF
Reported an attentional blink between transparent surfaces: N200 is suppressed for probes occurring on a different surface within ~500ms of a cued-surface event, reflecting the time cost of switching attentional hold between surfaces. Source modeling localized the effect to extrastriate areas (MT+), implicating motion-processing cortex as the locus of inter-surface competition. Consistent with surface selection operating at MT and with the ~500ms inter-surface interference cost measured behaviorally by Pinilla et al. (2001).

---

## Group 3: Object-Based Attention Theory

**15. Desimone & Duncan (1995). *Annual Review of Neuroscience* 18:193.**
Proposed the biased competition framework: multiple stimuli simultaneously activate competing neural representations; top-down attention and bottom-up salience bias competition in favor of one stimulus, which then wins enhanced representation while competitors are suppressed. The foundational theoretical account of why onset transients (like VRDots' translating dots) capture attention and drive surface selection via a salience-biasing mechanism.

**16. Duncan, Humphreys & Ward (1997). *Current Opinion in Neurobiology* 7:255.** ✓ PDF
Extended biased competition to multiple feature-processing modules (integrated competition): once a stimulus wins competition in one feature module (e.g., motion), winning signals propagate via inter-areal excitatory connections to all modules representing the same object (color, shape, depth). Provides a framework for feature spreading in attended transparent surfaces — attending to motion direction automatically boosts color and depth representations for the same surface via inter-module excitation.

**17. Blaser, Pylyshyn & Holcombe (2000). *Nature*.**
Demonstrated that observers can track a conjunction of features (color + shape) belonging to a single moving object through feature space without any spatial cues — maintaining an "object file" for a spatially overlapping object defined by feature coherence. Establishes that VRDots surfaces are likely represented as discrete object files, and that depth-plane information may be bound into the surface's object file as an additional feature dimension.

**18. Cavanagh et al. (2002). *Acta Psychologica*.**
Measured dual-task costs for monitoring events within a single transparent surface versus events on two different surfaces. Within-surface dual-task cost was near zero; across-surface cost was large and capacity-limited. Implies that the attended surface functions as a single attentional unit — monitoring multiple aspects of one surface is nearly free, but monitoring two surfaces requires switching.

**19. Pinilla, Cobo, Torres & Valdes-Sosa (2001). *Vision Research*.**
Quantified the behavioral cost of switching attention between two transparent surfaces at approximately 500ms. Cross-surface interference occurs when a target event follows a different-surface event within this window. Provides the temporal scale of surface-level attentional engagement and the switching cost that observers incur when attention is misdirected by the cue (UNCUED trials in VRDots).

**20. Iani et al. (2012). *Journal of Vision*.**
Replicated and parametrically extended the within-/across-surface cost finding, confirming that the boundary between within- and across-surface processing is categorical rather than graded. The step-function structure of selection is consistent with surface identity being represented as a discrete unit, not as a graded feature-similarity score.

---

## Group 4: Stoner Lab Surface Segmentation

**21. Stoner, Albright & Ramachandran (1990). *Nature* 344:153.**
Showed that whether a superimposed plaid displays coherent (pattern) or transparent (component) motion depends on intersection luminance: luminance consistent with physical transparency destroys coherent motion and produces two perceived transparent surfaces. Demonstrated that the motion system incorporates surface-interpretation cues, not just motion energy. Foundational for understanding why VRDots' two rotating fields are perceived as distinct surfaces rather than a single ambiguous motion display.

**22. Stoner & Albright (1992). *Nature* 358:412.**
Electrophysiology in macaque MT showing that direction tuning shifts depending on whether plaid stimuli are perceived as coherent or transparent. When stimuli are perceptually transparent, MT neurons respond to component directions rather than the pattern direction. MT activity tracks the surface percept, not the physical stimulus, establishing MT as the neural site where surface coherence is represented and where translating-dot signals are read out in VRDots.

**23. Stoner & Albright (1993). *Journal of Cognitive Neuroscience* 5:129.** ⚠️ venue corrected from Neuron
Argued that motion processing is non-modular: image segmentation cues (surface boundaries, transparency) feed directly into motion grouping. Demonstrates that depth-plane identity, as a segmentation cue, could modulate motion surface processing constitutively — not as a post-hoc tag — consistent with VRDots' depth-field cueing being a within-surface coherence effect rather than a separate grouping step.

**24. Stoner & Albright (1996). *Vision Research* 36:1291.** ⚠️ venue corrected from Nature
Mapped the full psychophysical dose-response curve from coherent to transparent plaid motion as intersection luminance departs from the transparency prediction. The dose-response logic extends to VRDots' depth-separation dimension: cueing effects are stronger at 0.10m depth separation (clear segmentation) than at 0.05m (moderate), and absent at 0.03m (barely perceptible), consistent with a graded segmentation-strength signal.

**25. Dobkins, Stoner & Albright (1998). *Journal of the Optical Society of America A* 15:1986.** ⚠️ proxy citation
Work from the Stoner lab period establishing that smooth pursuit tracks the perceptually dominant surface in transparent motion. Pursuit eye movements are a behavioral readout of the same surface-level representation that drives perceptual cueing effects. Methodological note for VRDots: brief pursuit responses to the 80ms translation cue could produce retinal motion asymmetries between CUED and UNCUED conditions, particularly if translation direction differs across Near/Far depth planes.

**26. Albright & Stoner (2002). *Annual Review of Neuroscience* 25:339.** ⚠️ venue corrected from PNAS
Comprehensive review arguing that contextual influences — stimuli surrounding the classical RF, temporal history, global scene properties like surface identity — shape cortical responses from V1 through MT. Frames contextual modulation as the mechanism by which local measurements are embedded in a global scene interpretation. Provides theoretical vocabulary for VRDots' depth-field cueing: depth-plane context shapes MT's surface representation constitutively; ZdA/ZdB directly manipulate this context at target onset.

---

## Group 5: MT Physiology

**27. Lankheet & Verstraten (1995). *Vision Research*.**
Showed that attending to one component of a transparent RDK shifts the motion aftereffect (MAE) toward the attended direction by approximately 70%. Demonstrated that selective attention to a transparent surface modulates the gain of motion-selective processing during perception, not merely at a post-perceptual decision stage. Implies VRDots cueing effects reflect genuine modulation of MT-level representations.

**28. Felisberti & Zanker (2005). *Vision Research*.**
Direction-discrimination thresholds are lower for the attended component of two overlapping RDKs. Extends Lankheet & Verstraten's MAE result to a direct sensitivity measure: surface-based attention improves direction discrimination, not just shifts adaptation. Consistent with the Lee & Maunsell model's prediction of enhanced MT signal for the attended direction.

**29. Wannig, Rodriguez & Freiwald (2007). *Neuron*.**
Showed in macaque MT that single neurons respond more strongly to the direction of an attended transparent surface than to the unattended surface's direction, when both directions drive the same RF simultaneously. Direct neural evidence for surface-selective gain modulation in MT — the attended surface's MT representation is enhanced, the distractor's is suppressed. Establishes that VRDots cueing effects have a cellular-level MT correlate consistent with the Lee & Maunsell normalization model.

**30. Kohn & Movshon (2004). *Nature Neuroscience* 7:764.** ✓ PDF
Showed that adaptation in MT narrows direction-tuning bandwidth and shifts preferred direction attractively toward the adapter, through a mechanism distinct from V1 adaptation (which only shifts preferred direction repulsively). MT adaptation could produce aftereffects that systematically bias CUED vs. UNCUED direction judgments — a potential confound in VRDots. The 80ms translation duration and short cue-to-target intervals limit MT adaptation effects, but the direction of any residual bias would be toward the cued direction, potentially contributing to (not opposing) the cueing advantage.

---

## Group 6: Computational and Modeling Papers

**31. Simoncelli & Heeger (1998). *Vision Research* 38:743.**
Two-stage feedforward model (V1 → MT) with divisive normalization at both stages. V1 performs spatiotemporal energy filtering; MT pools V1 outputs to achieve velocity tuning. Normalization at MT means the two surfaces in a transparent display compete via mutual suppression in the normalization pool. Establishes the normalization architecture within which attention effects (Reynolds & Heeger; Lee & Maunsell) operate.

**32. Weiss, Simoncelli & Adelson (2002). *Nature Neuroscience* 5:598.**
Bayesian observer model in which velocity estimates are derived from a likelihood (image measurements) combined with a prior favoring slow speeds. Explains motion illusions as rational inference under uncertainty. The slow-speed prior predicts speed underestimation for both VRDots surfaces equally; not directly relevant to the cueing effect but relevant to interpreting direction-discrimination difficulty and potential speed-bias confounds.

**33. Qian, Andersen & Adelson (1994). *Journal of Neuroscience* 14:7357.**
Transparent motion perception requires locally unbalanced motion signals: when two directions are precisely balanced at every spatial location, transparency fails. Disparity imbalance is an additional source of transparency support, predicting that depth-plane separation in VRDots should strengthen the two-surface percept and facilitate surface-based cueing. Provides the most direct computational basis for VRDots' depth-field cueing effect.

**34. Reynolds & Heeger (2009). *Neuron* 61:168.**
The normalization model of attention: R = (E × A)/(σ + S), where A is an attention field (Gaussian over space/features) that modulates the excitatory drive, while S is a normalization pool. Response gain vs. contrast gain depends on attention field width relative to stimulus size. Provides the MT-level gain mechanism for VRDots cueing but cannot alone explain dot-field specificity (both surfaces share the same spatial locations). Requires V1 Point-Set input to impose surface specificity on the attention field.

**35. Lee & Maunsell (2009). *PLOS One* 4:e4651.**
Normalization model combining feature-similarity gain g(θ, θ_att) in both numerator and denominator: R(θ) = [g·E(θ)] / [σ + Σ g·E(φ)]. Attending direction θ_att boosts the cued direction and simultaneously reduces normalization weight from the opponent direction — a double suppression. Tested in MT with two competing directions in the RF (the VRDots analog). Predicts UNCUED accuracy falls below a neutral (no-cue) baseline; this is an untested VRDots prediction.

**36. Carandini & Heeger (2012). *Nature Reviews Neuroscience* 13:51.**
Proposes normalization as a canonical computation across cortex, operating with area-specific normalization pool definitions. Provides the general framework within which depth-tuned normalization pools (relevant to ZdA/ZdB effects) operate: if MT normalization pools have any depth selectivity, depth-plane shifts should modulate competitive suppression between surfaces.

**37. Qian & Andersen (1997). *Vision Research* 37:1683.**
Physiological model of motion-stereo integration via V1 binocular cells jointly tuned for direction and disparity. MT pools these V1 inputs, enabling direction × disparity representation. Predicts that depth-plane separation creates non-overlapping MT populations for the two surfaces, explaining depth-field cueing as enhanced MT channel distinctiveness; ZdA disrupts, ZdB enhances this separation at target onset.

**38. Stoner (2010/2018). Society for Neuroscience abstract.** ⚠️ date uncertain; verify
V1 "point-set" as the unit of object-based selection: a set of V1 neurons sharing retinotopic location and direction preference, linked by recurrent excitatory connections within the direction column. Global feature-similarity gain from MT/MST provides broad directional amplification; local recurrent excitation within V1 hypercolumns imposes dot-level spatial specificity. Extends to color and depth (disparity) hypercolumns. Only model that predicts cueing survives feature swaps and duration-confound reversal (Stoner & Blanc 2010).

**39. Doostani, Hossein-Zadeh & Vaziri-Pashkam (2023). *eLife* 12:e75726.**
Human fMRI study testing three models (weighted sum, weighted average, normalization) for predicting BOLD responses to superimposed objects during object-based attention. Normalization wins at every level from V1 through higher object areas. Attention modulates the excitatory drive E within the normalization framework. Most direct human neuroimaging validation of normalization as the mechanism of object-based attention; the superimposed-body+house design is the object-category analog of VRDots' two transparent dot fields.

---

# PART II — Integrated Theoretical Summary

*Focus: object-based attention in transparent-motion stimuli. Update this section as new papers are integrated or framing shifts.*
**Last updated**: 2026-04-01

---

## 0. Caveat: "Object-Based Attention" Is Not a Unitary Phenomenon

The term *object-based attention* covers a range of experimental situations that may differ in mechanism, in what counts as an "object," and in which cortical stages are critical. This distinction is important throughout this document and for interpreting any new study cited as "object-based attention."

**Major paradigm classes and their likely mechanisms:**

| Paradigm | Defining feature | Likely mechanism | Spatial scale |
|----------|-----------------|-----------------|---------------|
| Extended-object cueing (Egly et al. 1994 rectangle paradigm) | Cue spreads within a bounded spatial region (e.g., a rectangle) | Spatial spread of attention within RF-sized regions; may not require feature-based grouping | Coarse; within-RF or across-RF |
| Feature-conjunction tracking (Blaser et al. 2000) | Observer tracks a feature conjunction moving through feature space; no spatial boundary | Object-file maintenance via feature binding | None — purely feature space |
| Category-level superimposition (O'Craven et al. 1999) | Two high-level objects (face + house) superimposed at the same location, moving in different directions | Category-selective areas (EBA, PPA) provide the discriminating signal; normalization between category-tuned populations | Coarse; category-area RF scale |
| Motion-coherent dot-field selection (Valdes-Sosa paradigm; VRDots) | Two spatially *intermixed* dot fields, each defined only by common motion direction; no spatial boundary, no categorical identity | Must operate at dot scale (below MT RF); V1 Point-Set recurrent excitation is the proposed mechanism | Fine; sub-RF, dot-level |
| Binocular rivalry (Mitchell et al. 2004) | Two rivaling images, one per eye; cue determines which monocular image dominates | Interocular competition; may involve both early (V1) and later (IT/frontal) stages | Eye-specific; V1 ocular dominance columns |

**Key distinctions relevant to VRDots:**

1. **Spatial boundary vs. no boundary**: Extended-object paradigms (rectangles, faces+houses moving to different locations) allow spatial attention to partially accomplish selection. Dot-field paradigms do not — both surfaces occupy the same spatial region. This means mechanisms that rely on spatial gradients (e.g., standard normalization with spatially defined attention fields) are insufficient for dot-field selection.

2. **RF scale mismatch**: In the O'Craven et al. (1999) paradigm, category-selective areas (EBA, PPA) have large RFs that encompass the whole display, but they are *category-tuned* — they can discriminate face from house without spatial separation. In the dot-field paradigm, neither motion direction nor spatial location is a reliable discriminator at the RF scale of MT, and there is no categorical identity to invoke. The V1 Point-Set model is proposed specifically for this case.

3. **Whether the Stoner/VRDots mechanism generalizes**: The V1 Point-Set model was developed for motion-coherent dot fields. It is an open question whether the same recurrent-excitation-within-hypercolumn mechanism accounts for extended-object advantages, category-level superimposition effects, or binocular rivalry. Each may have a different primary locus and mechanism.

**Implication for reading the literature**: When a study reports an "object-based attention" effect, ask: (a) what defines the object boundaries in that paradigm? (b) could spatial attention account for it? (c) is there a feature-swap or dot-level control that rules out direction-channel or category-level accounts? Only a subset of studies — primarily Stoner & Blanc (2010) and Catak et al. (2022) — meet the strict criteria for dot-field specificity that VRDots is designed to probe.

---

## 1. The Paradigm and What It Measures

The transparent-motion object-based attention paradigm (Valdes-Sosa et al. 1998, 2000) presents two superimposed random-dot kinematograms moving in opposite directions, creating the percept of two transparent surfaces occupying identical retinal locations. A brief onset translation of one surface (the cue) is followed by a second translation (the target) in either the same (CUED) or the opposite (UNCUED) surface. The cueing effect — CUED minus UNCUED accuracy — measures the selectivity of attentional engagement with the cued surface.

The paradigm is specifically designed to isolate surface-based from location-based attention: since both surfaces share all retinal locations, spatial attention cannot account for the cueing advantage. The advantage must reflect selection of a perceptual unit defined by common motion — a transparent surface functioning as an attentional object.

## 2. What Is Selected

The evidence converges on a surface-level unit of selection:

- **Not location**: Both surfaces share all spatial locations; spatial attention predicts no advantage (Valdes-Sosa et al. 1998).
- **Not a direction channel**: Feature-swap conditions (swapping direction labels between surfaces) do not transfer the cueing advantage to the new direction of the cued surface — selection follows the dots, not the direction (Stoner & Blanc 2010; Catak et al. 2022).
- **Not color-channel**: Same-color conditions preserve the cueing advantage (Mitchell et al. 2003).
- **Not temporal position**: Temporal asynchrony control rules out timing as the explanation (Valdes-Sosa et al. 2010).
- **Not duration of motion**: Reversing the motion-duration asymmetry does not reverse the cueing advantage (Stoner & Blanc 2010).

The unit of selection is the dot group as a coherent surface object — identified by shared motion coherence and spatial co-membership, tracked across feature changes, and apparently capable of incorporating depth-plane membership (see VRDots results, Part III).

## 3. Neural Substrate

Surface-based attention in the transparent-motion paradigm has a well-characterized neural cascade:

**Early cortex (V1–V3)**: C1 (75–110ms) enhancement for attended surfaces (Khoe et al. 2005); BOLD enhancement in V1–V3 (Ciaramitaro et al. 2011). Surface selection modulates the earliest cortical stages via feedback from higher areas.

**Feature spreading**: Color representation of the attended surface is activated in fusiform within ~150ms of motion onset (Schoenfeld et al. 2003); MEG shows a sequential cascade with motion areas first, color areas ~60ms later (Schoenfeld et al. 2014). The attended surface's features are automatically integrated across processing modules.

**MT/MST**: MT neurons respond more strongly to the direction of the attended surface (Wannig et al. 2007). Attending to a surface direction shifts MAE (Lankheet & Verstraten 1995) and lowers direction-discrimination thresholds (Felisberti & Zanker 2005). MT is the site where direction-tuned surface representations are formed and where attention gain is implemented.

**Inter-surface competition**: Attentional blink between surfaces, with N200 suppression for same-surface probes within ~500ms, sourced to MT+ (Rodríguez & Valdés-Sosa 2006). Switching between surfaces incurs a ~500ms behavioral cost (Pinilla et al. 2001). Surface-level attentional engagement is maintained across time and resists cross-surface interference.

## 4. Theoretical Accounts — Where They Succeed and Fail

**Biased competition (Desimone & Duncan 1995)**: The onset translation is a bottom-up salience event that biases competition in favor of the cued surface. Correct in direction for basic cueing, cross-surface blink, and ZdB enhancement (distractor withdraws from competition). Does not predict feature-swap survival or duration-confound failure.

**Integrated competition (Duncan et al. 1997)**: Winning in the motion module propagates to all feature modules for the same object. Accounts for feature spreading (Schoenfeld 2003, 2014) and provides vocabulary for depth-plane features being bound into the surface object. Operates at inter-areal scale, not at the V1 dot level.

**Normalization models (Reynolds & Heeger 2009; Lee & Maunsell 2009; Carandini & Heeger 2012)**: Provide the MT-level gain mechanism. Lee & Maunsell most specifically: feature-similarity gain in both numerator and denominator predicts both enhancement of cued direction and suppression of distractor direction below unattended baseline. Validated in human fMRI (Doostani et al. 2023). Cannot explain dot-field specificity: both surfaces share spatial locations, so a spatially or directionally defined attention field cannot distinguish them at the MT scale.

**V1 Point-Set model (Stoner 2010/2018; Stoner & Blanc 2010; described in Catak et al. 2022)**: Operates at V1 spatial scale (RFs small enough to resolve individual dots). Recurrent excitatory connections within V1 direction columns amplify the cued surface's signal at dot level. A global feature-similarity gain from MT/MST provides the broad directional amplification; the local V1 mechanism imposes spatial specificity on that gain. **Only model that predicts feature-swap survival and duration-confound failure.** Extends naturally to color and depth (disparity) hypercolumns, accounting for feature spreading and depth-field cueing. Complementary to (not competing with) normalization models: V1 Point-Sets provide the surface-specific input; MT normalization amplifies it.

## 5. Key Empirical Discriminators

| Result | Implication |
|--------|-------------|
| Feature-swap survival (Catak 2022; Stoner & Blanc 2010) | Selection is by dot spatial identity, not feature value — rules out direction-channel and color-channel accounts |
| Duration-confound failure (Stoner & Blanc 2010) | Selection is not duration-dependent — rules out pure normalization/adaptation accounts |
| C1 modulation at 75–110ms (Khoe et al. 2005) | Selection signal reaches V1 within ~100ms of cue onset — consistent with fast feedback |
| Feature spreading in 150ms / 60ms cascade (Schoenfeld 2003, 2014) | Selection propagates across feature modules in temporal sequence — consistent with feedforward spread from V1 point-sets |
| UNCUED below baseline (predicted by Lee & Maunsell) | **Untested in VRDots** — requires a neutral/no-cue baseline condition |

## 6. Open Questions in the Literature

1. **How does the V1 Point-Set signal enter the normalization computation?** The two accounts are complementary but the mechanistic handoff is unspecified.
2. **Are disparity columns in V1 organized in a way that supports depth-plane point-sets?** This is the key structural assumption of the depth-field cueing extension.
3. **What is the time course of depth-plane surface selection?** The 75–110ms C1 effect is for motion-defined surfaces; whether depth adds an earlier or later component is unknown.
4. **Is the ~500ms surface-switch cost modulated by depth-plane separation?** Pinilla et al. measured this for motion-only surfaces; depth could accelerate or slow switching.
5. **Does the Stoner model extend to non-motion objects?** Doostani et al. (2023) show normalization accounts for body/house superposition — the V1 mechanism would need to invoke orientation columns rather than direction columns.

---

# PART III — Ongoing VRDots Experiments: Pilot Results and Tentative Interpretations

*Update after each session or major interpretive revision.*
**Last updated**: 2026-04-01

---

## 1. VRDots Paradigm Overview

VRDots (v0.2.0) is a VR implementation of the translating-dot surface-selection paradigm on the Meta Quest. Two overlapping random-dot fields rotate in opposite directions (CW and CCW), creating two transparent surfaces. Each field occupies a distinct stereoscopic depth plane (Near vs. Far), separated by a small disparity (0.05m at 2m viewing distance in current experiments ≈ 0.72 arcmin).

One field (the Delayed field) begins translating ~80ms after the other (the Non-Delayed field). The observer reports the direction of the delayed translation (left/right). The cueing effect is the accuracy difference between trials where the target (second) translation occurs in the same field as the delayed onset (CUED) versus the opposite field (UNCUED).

**Swap conditions** manipulate which dots, features, or depth-plane assignments change at tStart (target onset):
- **N**: No swap — control condition
- **ZdA**: Cued (delayed) dot group changes depth plane at tStart
- **ZdB**: Non-cued (distractor) dot group changes depth plane at tStart

---

## 2. Three-Factor Analytic Framework

VRDots results are decomposed into three orthogonal factors using chi-square analysis:

| Factor | Contrast | Question |
|--------|----------|---------|
| **1. Dot cueing** | (CUED − UNCUED), collapsed across depth fields | Does the onset cue improve selection of the cued surface? |
| **2. Depth-field cueing** | Near-field performance vs. Far-field performance within cued trials | Does sharing a depth plane with the delayed field boost performance? |
| **3. Near/Far** | Near overall vs. Far overall | Is there an asymmetry between the two depth planes independent of cueing? |

---

## 3. Session Summary

| Session | Condition | depthSep | Dot Cueing | Depth-Field Cueing | Near/Far | Notes |
|---------|-----------|----------|-----------|-------------------|----------|-------|
| 260323_1534 | Baseline | — | +50.0pp | — | — | Pre-v0.2.0 |
| 260324_0716 | Baseline | — | +28.1pp | — | — | Cursor-jump issues |
| 260324_1010 | MotionSwap | — | +27.1→+15.7pp | — | — | 100% swap reduces cueing |
| 260325_1039 | Dots50Swap | — | +30.4→+34.4pp | — | — | 50% swap does NOT reduce |
| 260325_1831 | DepthBaseline | 0.10m | +27.5pp | — | Far +59.4pp, Near −4.9pp | Depth planes clear |
| 260325_1914 | DepthBaseline | 0.10m | +8.6pp | — | Far +65.1pp, Near −46.9pp | Depth planes clear |
| 260325_2013 | DepthBaseline | 0.03m | +16.6pp | — | Near +13.7pp, Far +19.4pp | Depth barely perceptible |
| 260326_1649 | DepthSwap50_005m | 0.05m | +40.3pp | — | Near +28pp, Far +53pp (est) | Zd: +35.9pp; N: +44.8pp |
| 260330_1853 | DepthSwapCtrl_005m | 0.05m | +34.3pp | +20.8pp* | Far +47.9pp***, Near +20.8pp* | N=+34pp**, ZdA=+12pp n.s., ZdB=+56pp*** |
| 260330_2012 | DepthSwapCtrl_005m | 0.05m | +12.2pp | — | Near/Far both n.s. | **Monocular: L eye closed, R eye active** — floater confound |
| 260331_0621 | DepthSwapCtrl_005m | 0.05m | — | — | — | Binocular session 2 |
| 260331_1530 | DepthSwapCtrl_005m | 0.05m | — | — | — | **Monocular R-eye #2, L closed** |
| 260331_1705 | DepthSwapCtrl_005m | 0.05m | — | — | — | **Monocular L-eye #1, R closed** |
| 260331_1734 | DepthSwapCtrl_005m | 0.05m | — | — | — | **Monocular L-eye #2, R closed** |

---

## 4. Key Findings (DepthSwapCtrl, as of 2026-04-01)

**Master summary — binocular (n=384) vs. all monocular (n=769 pooled, 2× R-eye + 2× L-eye):**

| Factor | Binocular | Monocular | Interpretation |
|--------|-----------|-----------|----------------|
| Dot cueing (Factor 1) | +19.8pp*** | +7.1pp* | Survives monocularly — motion-based |
| Depth-field cueing (Factor 2) | +12.5pp* | +7.1pp* | Survives with larger n — partially stereoscopic |
| Near/Far (Factor 3) | +9.4pp† | +1.2pp n.s. | Entirely stereoscopic — collapses monocularly |

**ZdA vs. ZdB dissociation (binocular):**
- N (no swap): +34pp**
- ZdA (cued dots change depth at tStart): +12pp n.s. — cueing abolished
- ZdB (distractor dots change depth at tStart): +56pp*** — cueing enhanced

ZdA and ZdB are matched for the number of dots changing depth (disruption count equated). The difference is specifically whether the coherent translating (target-bearing) dot group changes depth. ZdA kills cueing; ZdB enhances it.

**Far > Near asymmetry (binocular):**
- Far-plane trials: +47.9pp***
- Near-plane trials: +20.8pp*
- Asymmetry collapses completely in monocular sessions → entirely stereoscopic in origin

**Monocular notes:**
- R-eye sessions (L closed): higher accuracy overall (~36%) with floaters in R eye visible — potential confound
- L-eye sessions (R closed): higher accuracy (~44%) — fewer floaters
- Session-to-session variance is large at n=192; pooled monocular n=769

---

## 5. Tentative Interpretations

**ZdA/ZdB dissociation** is the most theoretically significant finding. Two viable accounts:

*Surface-identity account*: Depth-plane membership is incorporated into the V1 Point-Set (via disparity columns). ZdA disrupts the cued surface's depth-column coherence at target onset, weakening recurrent excitation. ZdB disrupts the distractor's depth-column coherence, reducing its competition with the cued surface. Predicts the effect is stereoscopic (requires binocular disparity computation).

*Monocular geometric confound account*: A depth change of 0.05m at 2m produces a monocular positional shift per eye that scales with eccentricity (0–5 arcmin; up to ~49% of translation distance at aperture edge). In ZdA, the target-bearing dots get this spurious positional shift; in ZdB, only the distractor does. The positional shift could directly impair direction discrimination for ZdA dots monocularly, without any surface-identity mechanism.

**Critical test**: The monocular sessions were designed to dissociate these accounts. If ZdA/ZdB survive monocularly (with floater confound removed), that would implicate the monocular positional shift. If they collapse monocularly, that supports a stereoscopic surface-identity account. Full monocular analysis pending (sessions 260331 not yet fully analyzed as of 2026-04-01).

**Far > Near asymmetry**: Best candidate is MT population anisotropy (PubMed 21068268) — if MT has fewer but more sharply tuned far-disparity neurons, the far surface is more distinctly represented, boosting depth-field cueing for far-plane targets. Alternatively, perceptual asymmetry (far planes easier to segment from optical infinity background). Monocular collapse confirms stereoscopic origin but does not discriminate between MT anisotropy and perceptual accounts.

---

## 6. Pending Analyses and Next Experiments

- Full analysis of 260331 sessions (binocular session 2 + 4 monocular sessions)
- Verify ZdA/ZdB survive or collapse monocularly (key dissociation)
- Verify L-eye vs. R-eye asymmetry (floater confound assessment)
- Triple-check ZdA/ZdB stimulus correctness (depth change timing, which dots affected)
- Retrieve and integrate PubMed 21068268 (MT anisotropy — key for Far > Near account)
- Additional binocular sessions for power
- Consider parametric depth-swap (varying % of dots changing depth) to test categorical vs. graded disruption account

---

*End of document. Parts II and III are living sections — update as new data, analyses, or papers arrive.*
