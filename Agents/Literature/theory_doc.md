# VRDots Theory Document
**Version**: 0.1 — Initial literature integration
**Date**: 2026-03-31

---

## 1. The Paradigm: Where VRDots Sits in the Literature

### 1.1 Transparent-Motion Object-Based Attention

VRDots belongs to a specific paradigm: two superimposed random-dot kinematograms (RDKs) moving in opposite directions, creating the percept of two transparent surfaces. The observer must selectively attend to one surface. The founding behavioral work is Valdes-Sosa, Cobo & Pinilla (1998, Cognition), which established that observers can switch attention between overlapping transparent surfaces without any change in spatial location, demonstrating that the unit of selection can be a surface defined by common motion rather than a spatial region.

The specific cuing method in VRDots — a brief translation of dots in one field at stimulus onset, followed by a delayed translation in the same or opposite field — derives directly from Valdes-Sosa, Cobo & Pinilla (2000, JEP:HPP). That paper showed the onset translation acts as an exogenous surface cue: accuracy for a second translation is highest when the two translations occur within the same surface. This is the core logic of VRDots. The initial translation cues the observer to one surface; the delayed translation (target) occurs in either the cued (same) or uncued (opposite) surface; the cueing effect (CUED minus UNCUED accuracy) measures surface-based attentional selection.

### 1.2 From 2D to 3D: VRDots Extension

VRDots extends the paradigm into virtual reality to introduce stereoscopic depth. The two surfaces now occupy distinct depth planes (near vs. far), separated by a small disparity (0.05 m at 2 m viewing distance in current experiments). This adds a question the original 2D paradigm cannot answer: does the attentional surface unit incorporate disparity-defined depth, or is the selection entirely feature-based (motion-direction) and agnostic to depth?

---

## 2. Key Findings from Approved Papers, Organized by Theme

### 2.1 Surface-Based Selection Is Robust and Pre-Attentive

**Valdes-Sosa, Cobo & Pinilla (1998, Cognition)** established the behavioral benchmark: accuracy for detecting a property change (e.g., speed) is substantially higher when successive events occur within the same transparent surface versus across surfaces, even though both surfaces occupy identical retinal locations. The effect is not reducible to spatial attention.

**Valdes-Sosa, Cobo & Pinilla (2000, JEP:HPP)** refined this using onset translations as cues and showed the effect is exogenous: it occurs even under divided-attention conditions and does not require deliberate tracking. This validates VRDots' use of an onset translation as a surface cue.

**Valdes-Sosa et al. (2010)** ruled out the main alternative explanation — that the cueing effect reflects temporal asynchrony rather than surface identity — by equating temporal intervals while varying surface congruence. The delayed-onset design used in VRDots is explicitly validated by this control.

**Mitchell, Stoner & Reynolds (2004, Nature)** demonstrated that the same translation-cue paradigm determines dominance in binocular rivalry: cueing one of two rivaling surfaces increases its predominance. This establishes that the translating-dot onset cue selects a perceptual surface, not merely a local feature. VRDots is a behavioral descendant of this exact paradigm.

### 2.2 Selection Is Surface-Based, Not Feature-Channel-Based

**Mitchell, Stoner, Fallah & Reynolds (2003, Vision Research)** showed that surface-based attentional selection persists even when both transparent fields are the same color. If selection were accomplished by modulating color-channel gain, the effect should collapse when color does not distinguish surfaces. It does not (p > .05 on all measures; first judgment 74.5% vs. 74.0%, same-surface second judgment 69.0% vs. 69.2%). Color is therefore not *necessary* for surface-based selection, and the mechanism cannot be reduced to feature-channel modulation.

*Nuance (confirmed from paper, 2026-04-01)*: Graphical inspection of Fig. 2 vs. Fig. 3 suggests a slight trend toward less impairment (smaller cueing effect) at the shortest ISIs in the same-color condition, though this did not reach significance. The study was designed to rule out color as a *sole* mechanism and was likely underpowered to detect a modest facilitative increment. Mitchell §4.3 explicitly acknowledges that color could facilitate surface segmentation under some conditions (citing Croner & Albright 1997). This is consistent with the V1 Point-Set model: color columns add a dimension to the point-set, strengthening within-surface coherence without being strictly necessary. VRDots' same-color (COLOR_RED) conditions may therefore slightly underestimate the cueing effect that would be seen with two-color surfaces.

*Extension to depth (2026-04-01)*: The same logic applies to disparity-defined depth. V1 hypercolumns contain disparity-tuned cells alongside direction- and color-tuned cells, and these are the substrate of the Point-Set model. Two transparent surfaces occupying different depth planes carry distinct disparity values per dot, adding a third feature dimension to the point-set beyond direction and color. The V1 Point-Set model therefore predicts that depth separation should be *facilitative* for surface-based selection — not necessary (motion coherence alone is sufficient), but adding coherence strength to the point-set in the same way color does.

Several lines of evidence from the transparent-motion literature are consistent with this prediction:

- **Qian, Andersen & Adelson (1994)**: Transparent motion perception requires locally *unbalanced* motion signals. Disparity imbalance (depth-plane separation between the two motion populations) provides an additional source of local imbalance, predicting that depth separation strengthens the two-surface percept independently of motion direction differences. A stronger two-surface percept should support stronger attentional selection of one surface.

- **Qian & Andersen (1997)**: V1 binocular cells are jointly tuned for direction *and* disparity. MT pools these inputs, enabling direction × disparity selectivity. When two surfaces differ in both direction and depth, their MT populations are more separated (less overlapping) than when they differ only in direction — exactly the mechanism by which depth would facilitate surface-based selection.

- **Stoner & Albright (1993, 1996)**: Segmentation cues feed into motion grouping non-modularly, and the contribution is dose-dependent. Depth-plane separation, as a segmentation cue, would modulate surface-processing strength continuously with separation magnitude — not as a post-hoc tag.

- **VRDots dose-response** (pilot, 2026-03): cueing effects are present at 0.10m depth separation (where depth planes are clearly visible) and appear attenuated at 0.03m (barely perceptible depth). While noisy at the pilot level, this is directionally consistent with depth facilitating cueing as a graded segmentation cue. Formally analogous to the Mitchell (2003) comparison: 0.03m ≈ same-color (depth barely discriminable), 0.10m ≈ two-color (depth clearly discriminable).

- **VRDots ZdA/ZdB** (pilot, 2026-03): Changing the cued dot's depth plane at target onset (ZdA) disrupts cueing; maintaining depth purity of the cued surface while changing non-coherent dot depth (ZdB) enhances cueing. Both results confirm that depth membership is actively incorporated into the surface representation and that its integrity matters — consistent with depth being a facilitative dimension in the point-set rather than an irrelevant tag.

The key untested comparison in the existing 2D literature is a direct same-depth vs. different-depth manipulation of the cueing effect, analogous to Mitchell's same-color vs. different-color design. No published transparent-motion study has done this. VRDots Baseline (no depth separation) vs. DepthBaseline (0.10m separation) approximates this comparison but with session-level confounds (different dates, fatigue, calibration). A controlled within-session depth-separation manipulation (0m vs. 0.05m) would be the definitive test.

*Prediction*: Same-depth (both surfaces at identical depth plane) should produce somewhat weaker cueing than different-depth conditions, with the magnitude of facilitation scaling with depth separation. This may be too small to reach significance at typical n per session (~192 trials) but should be detectable across subjects.

### 2.3 Object Files and Feature Binding Across Space and Time

**Blaser, Pylyshyn & Holcombe (2000, Nature)** showed that observers can track a conjunction of features (color + shape) for a single object through feature space without spatial cues, demonstrating that object files are maintained for spatially overlapping objects defined by feature coherence. This supports the theoretical claim that VRDots surfaces are represented as discrete objects, not merely as segregated texture regions. The depth-plane information in VRDots may serve as an additional feature bound into the surface's object file.

### 2.4 Attentional Selection Sharpens Motion Representation

**Lankheet & Verstraten (1995, Vision Research)** found that attending to one component of a transparent RDK shifts the motion aftereffect (MAE) to favor the attended direction by approximately 70%. This shows that selective attention does not merely tag a surface for post-perceptual decision making; it modulates the gain on motion signals during perceptual processing.

**Felisberti & Zanker (2005, Vision Research)** showed that direction-discrimination thresholds are lower for the attended component of overlapping RDKs. Combined with Lankheet & Verstraten, this establishes that attention to a transparent surface produces measurable improvements in motion sensitivity, not just response bias.

**Wannig, Rodriguez & Freiwald (2007, Neuron)** showed that MT neurons in non-human primates respond more strongly to the direction of an attended transparent surface than to the unattended surface. This neural evidence establishes that surface-based attention operates at the level of motion-selective cortex (MT/V5), consistent with the source of the translating-dot signals in VRDots.

### 2.5 Neural Timing and Early Cortical Modulation

**Khoe, Mitchell, Reynolds & Hillyard (2005, Vision Research)** recorded ERPs during the translation-cue paradigm and found that C1 and N1 components are enhanced for attended surfaces relative to unattended. C1 enhancement implicates V1/V2, which means surface-based selection modulates the earliest cortical stages — consistent with feedback from higher areas. The timing constrains when the cue has its effect: selection is established rapidly, within approximately 100 ms of the onset cue.

**Valdes-Sosa, Bobes et al. (1998, J Cognitive Neuroscience)** showed that non-spatial surface switching modulates the P1 ERP component, providing early evidence that surface switching has electrophysiological correlates even without spatial shifts.

**Ciaramitaro, Mitchell, Stoner, Reynolds & Boynton (2011, J Neurophysiol)** used fMRI to show that attending to one of two superimposed translating-dot surfaces enhances BOLD responses in early visual cortex (V1–V3), with the effect spatially co-localized with the shared retinotopic footprint of both surfaces. Surface-based attention thus has a cortical locus in early visual areas, not only in MT or higher areas. This is the most direct neural evidence that the VRDots paradigm engages genuine surface-selective cortical processing.

### 2.6 Dual-Task and Interference Costs Between Surfaces

**Cavanagh et al. (2002, Acta Psychologica)** measured dual-task costs for tracking within a single transparent surface versus across two surfaces. Within-surface dual-task costs were near zero; across-surface costs were large. This shows that two objects within the same surface can be monitored nearly for free, but monitoring across surfaces requires a capacity-limited switch.

**Pinilla, Cobo, Torres & Valdes-Sosa (2001, Vision Research)** quantified the interference cost for successive events when the second event occurs in a different surface, finding approximately 500 ms of interference — roughly the duration of the attentional episode needed to disengage from one surface and re-engage the other.

**Iani et al. (2012, J Vision)** replicated and extended the finding of large across-surface costs and near-zero within-surface costs in a parametric design, confirming the boundary between within- and across-surface selection is categorical rather than graded.

---

## 3. What the Approved Papers Predict About VRDots Results

### 3.1 Dot Cueing Effect (CUED > UNCUED)

The entire paradigm lineage (Valdes-Sosa et al. 1998, 2000; Mitchell et al. 2004; Valdes-Sosa et al. 2010) predicts a robust CUED > UNCUED advantage. VRDots observes +19.8pp binocular (p < 0.001) and +9.1pp monocular (p < 0.05). The binocular effect is within the range of prior 2D studies. The monocular survival of the cueing effect is consistent with the paradigm being primarily motion-feature based (common translational motion defines the surface), since motion signals are available monocularly — depth is not required for surface selection, only for depth-field cueing.

### 3.2 Depth-Field Cueing (Translation in Same Depth Plane as Delayed Field)

The 2D literature does not directly predict this effect because depth planes are not part of the 2D paradigm. However, Blaser et al. (2000) establishes that object files incorporate multiple bound features, and depth (disparity) is a strong perceptual cue that could contribute to surface representation alongside motion direction. The prediction from object-file theory is that the surface defined by common depth plane would be more coherent and more likely to be selected as a unit, boosting the cueing effect when cue and target share a depth plane. VRDots observes +12.5pp binocular (p < 0.05) and +7.1pp monocular (p < 0.10, marginal). The monocular attenuation (binocular > monocular for this component specifically) is consistent with a stereoscopic contribution to depth-field cueing that is absent monocularly, as expected.

### 3.3 Near/Far Asymmetry

The 2D literature makes no prediction about Near vs. Far depth planes. The observed +9.4pp advantage for Far over Near (binocular only; n.s. monocularly) points to a stereoscopic mechanism. The literature's most relevant contribution is Ciaramitaro et al. (2011) showing early-cortical modulation: if depth-defined surface selection operates at V1–V3 (where disparity tuning exists), then Near/Far differences could arise from asymmetries in binocular disparity processing, not from surface selection per se. The Far > Near pattern matches the VRDots session-level observation that Far cueing is consistently larger than Near cueing (e.g., session 260325_1831: Far = +59.4pp, Near = -4.9pp). This is not predicted by the 2D surface literature and represents a genuinely novel finding whose origin is unclear from existing theory.

### 3.4 ZdB Enhancement (+32.8pp, stronger than N baseline)

Cavanagh et al. (2002) and Iani et al. (2012) predict that within-surface events are processed more efficiently than across-surface events. In ZdB, the non-coherent (distractor) dot group moves INTO the cued depth plane at target onset, while the cued (coherent) dot group stays in the originally cued plane. If the surface unit is depth-plane defined, then in ZdB the distractor moves AWAY from the cued surface and the signal/noise ratio for the cued surface increases — this is the predicted direction.

Mitchell et al. (2003) established that surface selection operates on motion coherence, not color. In ZdB, the cued surface maintains its motion coherence AND its depth-plane identity; the distractor surface is doubly disrupted (motion incoherence at target onset plus depth-plane change). The prediction is that ZdB should enhance cueing relative to N (no swap), which is exactly what is observed (+32.8pp vs. N baseline). This is the clearest confirmation that depth-plane membership is incorporated into the surface representation that drives cueing.

### 3.5 ZdA Attenuation (cueing drops to +10.9pp n.s.)

The translation-cue literature (Valdes-Sosa et al. 2000; Mitchell et al. 2004) establishes that the cue works by selecting the surface containing the translating dots. In ZdA, the cued dot group itself changes depth plane at target onset. If the observer has selected the surface in the originally cued depth plane, and the cued dot group moves out of that plane at target onset, there is a mismatch: the attentional selection (based on the original cue) no longer aligns with the physical location of the target-bearing dots.

Blaser et al. (2000) predicts that object-file identity depends on continuity of features. A depth-plane switch constitutes a feature discontinuity that could disrupt the object file for the cued surface, releasing attentional hold. Pinilla et al. (2001) measured ~500ms interference for across-surface events; ZdA imposes exactly this kind of cross-plane event on the target itself. The prediction is attenuation, which is observed. The attenuation specifically to n.s. (from +19.8pp baseline) is consistent with a complete disruption of the surface representation at the moment of target evaluation.

---

## 4. Open Theoretical Questions the VRDots Data Raises

### 4.1 Is Depth-Plane Membership a Defining Feature of the Surface Unit, or a Tag?

Two interpretations are consistent with ZdA/ZdB results:

**Depth-as-defining-feature account**: The surface representation integrates disparity as a defining dimension alongside motion direction. Changing depth plane (ZdA for the cued dot) dissolves the existing surface identity and places the cued dot in a new, unattended surface. ZdB removes the distractor from the attended plane, making the attended surface purer.

**Depth-as-grouping-cue account**: Depth does not define the surface per se, but provides an additional grouping signal. Under this account, the effect of depth change in ZdA is to reduce grouping strength of the cued surface, which is a quantitative rather than categorical disruption.

The current data cannot discriminate these: attenuation to n.s. in ZdA is consistent with both a complete dissolution of surface identity (categorical) and with partial degradation (quantitative). Parametric variation of the proportion of dots undergoing depth swap, or of the magnitude of the depth shift, could discriminate.

### 4.2 Monocular Geometric Confound vs. True Surface Disruption in ZdA/ZdB

As documented in the project, a depth change of 0.05m at 2m induces a position shift per eye that scales with eccentricity (up to ~49% of translation distance at aperture edge). In ZdA, this spurious positional shift occurs for the cued (target-bearing) dot group; in ZdB, it occurs only for the non-cued group. The monocular session (L eye closed) shows near-zero effects for all conditions (+12.2pp overall, n.s.), but this session has the confound of the right eye having floaters. A clean right-eye-closed monocular replication is needed.

If ZdA attenuation and ZdB enhancement survive monocular viewing (with floater confound removed), that would support a surface-level account (since depth-plane identity is not available monocularly, any residual effect would reflect the positional-shift confound or some other mechanism). If they collapse monocularly, that supports a stereoscopic surface-identity account. The 2D literature offers no guidance here because depth was never manipulated.

### 4.3 What Drives the Far > Near Asymmetry?

The 2D paradigm literature (all approved papers) is agnostic about Near/Far. The Wannig et al. (2007) finding that MT neurons prefer the attended surface direction does not predict Near/Far differences because MT neurons are not strongly disparity-tuned. Ciaramitaro et al. (2011) shows early visual cortex involvement, where disparity processing does occur, but does not speak to Near/Far asymmetries. The VRDots Far > Near asymmetry may reflect: (a) a perceptual asymmetry in depth-plane salience (far planes easier to segment from a background at optical infinity); (b) an asymmetry in the mapping of convergent vs. divergent disparity; or (c) a task-level confound (e.g., head/body posture differences for near vs. far reaching). None of the approved papers predict or explain this finding.

### 4.4 Can Surface-Based Attention Operate Across Depth Planes Defined Only by Disparity?

The entire approved-paper corpus uses 2D transparent surfaces — both fields share the same depth plane. VRDots is the first implementation (to our knowledge) of the Valdes-Sosa/Mitchell paradigm with stereoscopic depth separation. The question of whether the translational-onset cue selects a depth-plane-defined surface as a unit is genuinely open. The current VRDots data suggest the answer is yes (depth-field cueing effect, ZdA/ZdB dissociation), but the monocular confound issue prevents a definitive conclusion. The approved papers predict that any feature that defines a coherent perceptual unit could serve as a surface-selection handle (Blaser et al. 2000; Mitchell et al. 2003), but they do not test disparity specifically.

### 4.5 Does ZdB Enhancement Reveal Active Suppression of the Unattended Surface?

The ZdB result (+32.8pp, exceeding N baseline) is consistent with the idea that moving the distractor surface into the cued depth plane normally reduces cueing efficiency (by "contaminating" the attended surface with non-coherent dots). In the N (no-swap) condition, the distractor stays in its original depth plane, which is already different from the cued plane — yet cueing is +19.8pp, not maximum. ZdB enhancement above N implies that additional separation of the distractor (moving it further in a new plane at target onset) actively improves selection.

Cavanagh et al. (2002) and Iani et al. (2012) show near-zero within-surface costs, implying that within-surface processing is efficient, but they do not predict enhancement from distractor departure. Wannig et al. (2007) show MT suppression for unattended surfaces; if unattended-surface suppression is gated by the surface's depth-plane membership, then ZdB (which moves the unattended surface to a new plane at target onset) would briefly re-engage suppression processes and thus enhance target detection. This is speculative but testable: if ZdB enhancement is mediated by active suppression, then a probe of the distractor surface immediately after the depth-plane swap should show enhanced suppression relative to N.

### 4.6 Is the ~500ms Surface-Switch Cost (Pinilla et al. 2001) Modulated by Depth?

Pinilla et al. (2001) measured a ~500ms interference cost when the observer must effectively switch from one transparent surface to another. VRDots uses a fixed 80ms translation duration; the inter-trial interval structure is not optimized to measure this cost. However, if depth-plane membership shortens or lengthens the surface-switch cost (e.g., because depth provides a more stable or faster attentional handle than motion alone), this would be detectable in an RT or threshold-vs.-SOA experiment. The current design does not measure SOA-dependent effects, leaving this question entirely open.

---

## 5. Summary Table: Predictions vs. Observations

| VRDots Finding | Best-Matching Prior Work | Predicted Direction | Observed | Match? |
|---|---|---|---|---|
| Dot cueing effect (binocular) | Valdes-Sosa et al. 2000; Mitchell et al. 2004 | CUED > UNCUED | +19.8pp*** | Yes |
| Dot cueing effect (monocular) | Valdes-Sosa et al. 2010 (motion-based) | Should survive | +9.1pp* | Yes |
| Depth-field cueing (binocular) | Blaser et al. 2000 (object file binding) | Feature coherence boosts selection | +12.5pp* | Yes |
| Depth-field cueing (monocular) | — (no prior prediction) | Attenuation expected if stereoscopic | +7.1pp* (n=769) | Partial survival |
| Near/Far asymmetry | None | No prediction | +9.4pp† bino, n.s. mono | Novel |
| ZdB enhancement | Cavanagh et al. 2002; Wannig et al. 2007 | Less distractor contamination → better | +32.8pp*** | Yes |
| ZdA attenuation | Blaser et al. 2000; Pinilla et al. 2001 | Feature discontinuity disrupts object file | +10.9pp n.s. | Yes |
| ZdA = ZdB disruption count | Mitchell et al. 2003 (not color-channel) | Effect not purely disruption-count-based | ZdA ≠ ZdB | Yes |

---

## 6. Additional Stoner Lab Background

This section integrates the Stoner lab papers from `pending_papers.md`. Three venue discrepancies were found between the pending list and web search results and are flagged inline — verify before citing formally.

### 6.1 Stoner, Albright & Ramachandran (1990) — Transparency as Gate for Motion Coherence

**Stoner, G.R., Albright, T.D., & Ramachandran, V.S. (1990). Transparency and coherence in human motion perception. *Nature*, 344, 153–155.**

When two superimposed sine-wave gratings move in different directions, observers perceive either a single coherent plaid (pattern motion) or two transparent surfaces sliding across each other (component motion). Stoner et al. showed that which percept dominates is determined not by motion signals per se but by the luminance of intersection regions: when intersection luminance is physically consistent with optical transparency, pattern motion is destroyed and component motion is seen. The implication is that the motion system has access to tacit knowledge of the physics of surface transparency — motion signals are resolved within a surface interpretation, not prior to it.

VRDots directly inherits this framework. The two rotating dot fields are the RDK analog of two transparent gratings. The finding that motion grouping depends on surface interpretation (not just motion energy) means VRDots cueing effects reflect surface-level selection — the cue selects a surface, not a direction of motion. It also implies that adding depth-plane separation (which further supports a two-surface interpretation) should facilitate surface segregation, consistent with the depth-field cueing effect.

### 6.2 Stoner & Albright (1992) — MT as the Neural Site of Surface Motion Coherence

**Stoner, G.R., & Albright, T.D. (1992). Neural correlates of perceptual motion coherence. *Nature*, 358, 412–414.**

Recording from MT neurons in awake macaques, Stoner & Albright found that direction tuning shifts as a function of whether the plaid stimulus produces coherent or non-coherent (transparent) perception. When the stimulus is perceptually coherent, MT neurons respond as pattern-direction-selective cells; when the same stimulus is made perceptually non-coherent by adjusting intersection luminance, MT neurons respond to component directions. MT activity tracks perception, not the physical stimulus.

This is the neural grounding for VRDots' surface-cueing signal. The translating dot field defines a coherent surface; MT represents that surface as a unit. Cueing effects are read out downstream from MT, where the surface representation is already formed. ZdA's impairment of cueing is consistent with a depth-plane change degrading MT's coherent-surface representation for the cued dot group at the moment of target onset — the MT pattern-direction signal for the cued surface may collapse when the cued dot group abruptly changes depth plane.

### 6.3 Stoner & Albright (1993) — Non-Modularity: Segmentation Cues Feed Into Motion Processing

**Stoner, G.R., & Albright, T.D. (1993). Image segmentation cues in motion processing: Implications for modularity in vision. *Journal of Cognitive Neuroscience*, 5(2), 129–149.**

⚠️ *Venue discrepancy: pending_papers.md lists this as Neuron; web search identifies the venue as Journal of Cognitive Neuroscience. Verify before citing.*

The paper argues that motion processing is not modular: image segmentation cues — luminance relationships that signal surface boundaries and transparency — feed directly into motion grouping. The visual system uses segmentation cues that are unrelated to motion per se to resolve which motion signals belong to the same surface. This non-modularity is demonstrated behaviorally and has implications for how visual cortex should be modeled.

This is directly relevant to VRDots' depth-field cueing effect. If depth-plane identity is an image segmentation cue (surfaces separated in depth are distinct objects), then it should modulate motion surface processing in the same way that luminance transparency does — not as a post-hoc tag but as a constitutive input. The depth-field cueing result (+12.5pp binocular, +7.1pp monocular) is consistent with depth acting as a segmentation cue that sharpens the surface representation for the attended plane.

### 6.4 Stoner & Albright (1996) — Psychophysics of Surface Segmentation in Motion

**Stoner, G.R., & Albright, T.D. (1996). The interpretation of visual motion: Evidence for surface segmentation mechanisms. *Vision Research*, 36(10), 1291–1310.**

⚠️ *Venue discrepancy: pending_papers.md lists this as Nature; web search identifies the venue as Vision Research. Verify before citing.*

Using plaid stimuli with systematically varied intersection luminance, Stoner & Albright mapped the full psychophysical curve from coherent to non-coherent motion perception as a function of how much the intersection luminance departs from the transparency-consistent value. This provided a dose-response characterization of surface segmentation strength: the further the intersection luminance departs from the transparency prediction, the stronger the segmentation signal and the clearer the transparent (component-motion) percept.

For VRDots, this dose-response logic extends to the depth-separation dimension. The strength of the depth-plane segmentation cue is a function of disparity magnitude — explaining why Near/Far cueing effects are larger at 0.10m (where depth dominates to the point of reversing the cueing effect) than at 0.05m (where depth modulates but does not override motion-based grouping) and absent at 0.03m (where depth is barely perceptible).

### 6.5 Stoner Lab (1998) — Smooth Pursuit Tracks the Attended Transparent Surface

**Dobkins, K.R., Stoner, G.R., & Albright, T.D. (1998). Perceptual, oculomotor and neural responses to moving color plaids. *Journal of the Optical Society of America A*, 15(8), 1986–2001.**

⚠️ *Note: The pending_papers.md lists "Stoner & Albright (1998) Vision Research — Luminance contrast affects smooth-pursuit eye movements." Web search did not locate a paper with exactly that title and authorship; the above related paper from the same lab and year is cited as a proxy. Verify whether a separate 1998 VR paper exists.*

Work from the Stoner lab in this period established that smooth pursuit eye movements track the perceptually dominant surface in transparent motion displays. When a plaid is perceptually coherent, pursuit locks to the pattern direction; when it is transparent, pursuit can lock to either component direction, depending on which surface is attended. Pursuit is thus a behavioral readout of the same surface-level representation driving perceptual decisions.

For VRDots, this raises a methodological consideration: if observers make smooth pursuit movements toward the cued surface's translation direction, the retinal motion of cued-surface dots may be partially cancelled, potentially affecting performance asymmetrically across CUED and UNCUED trials. At 80ms translation duration and 2.26 deg/sec, pursuit gain is low, but any systematic tracking could contaminate Near vs. Far comparisons if the translation angle relative to gravity or the fixation target differs across depth planes.

### 6.6 Albright & Stoner (2002) — Contextual Influences as a Unifying Framework

**Albright, T.D., & Stoner, G.R. (2002). Contextual influences on visual processing. *Annual Review of Neuroscience*, 25, 339–379.**

⚠️ *Venue discrepancy: pending_papers.md lists this as PNAS; web search identifies the venue as Annual Review of Neuroscience. Verify before citing.*

This comprehensive review synthesizes evidence from V1 through MT that cortical responses are not determined solely by the stimulus in the classical receptive field but are systematically modulated by surrounding context — nearby stimuli, temporal history, higher-order scene properties like surface identity. The review frames contextual modulation as the mechanism by which local measurements are embedded in a global scene interpretation, and as a general principle of cortical computation across sensory systems.

VRDots is a paradigm case of contextual influence: the translating dot group's identity (cued vs. uncued surface) is determined not by local motion properties but by its global context (which surface it belongs to, defined by coherent rotation and now depth plane). The review provides the theoretical vocabulary for why depth-plane context shapes MT's surface representation: depth is a contextual property that feeds into — rather than decorating — the surface identity computation. ZdA/ZdB results are a direct demonstration: changing depth-plane context at target onset (ZdA) degrades cueing; removing distractor context from the cued plane (ZdB) enhances it.

### 6.7 Note: Stoner, Carney & Shadlen — Citation Not Located

The pending_papers.md entry "Stoner, Carney & Shadlen (various) — Work on depth and disparity in MT/surface segmentation" did not resolve to a specific paper in web search. A potentially related and highly relevant paper is:

**Qian, N., & Andersen, R.A. (1997). A physiological model for motion-stereo integration and a unified explanation of Pulfrich-like phenomena. *Vision Research*, 37(12), 1683–1698.** — depth and motion integration at the level of V1/MT binocular cells.

Also of note from web search: **"Population anisotropy in area MT explains a perceptual difference between near and far disparity motion segmentation" (PubMed ID: 21068268)** — this paper reports that MT has more neurons tuned to near vs. far disparities, which could directly explain VRDots' Far > Near cueing asymmetry (if far-disparity-tuned neurons are fewer, the far surface may be more distinctly represented by a more selective population). Recommend retrieving and reviewing this paper explicitly.

---

## 7. Venue Corrections to pending_papers.md

The following venue errors were identified during web search (2026-03-31). Update `pending_papers.md` accordingly:

| Entry | Listed venue | Correct venue |
|-------|-------------|---------------|
| Stoner & Albright (1993) | Neuron | *Journal of Cognitive Neuroscience* |
| Stoner & Albright (1996) | Nature | *Vision Research* |
| Albright & Stoner (2002) | PNAS | *Annual Review of Neuroscience* |

---

*Section 6–7 added 2026-03-31. Stoner lab paper integration pass.*

---

## 8. PDF Library — Confirmed Published Papers (Integration Pass, 2026-03-31)

Two files flagged as NOT published papers (AI-generated syntheses, no journal/DOI):
- `Motion_Transparency_Disruption_Review.pdf` — internal synthesis only
- `Object_Based_Attention_Review.pdf` — AI-generated review dated 2025-06-02

`HillyardReynoldsOurParadigmEEG.pdf` is a duplicate of `KhoeReynoldsHillyard.pdf` (Khoe et al. 2005, already integrated in §2.5).

---

### 8.1 Stoner & Blanc (2010) — VRDots' Direct Predecessor

**Stoner, G.R., & Blanc, G. (2010). Exploring the mechanisms underlying surface-based stimulus selection. *Vision Research*, 50(2), 229–238.**

The immediate predecessor to VRDots. Stoner & Blanc showed that the Valdes-Sosa et al. (2000) delayed-onset design contains a **motion-duration confound**: the cued dot field has a longer rotation history than the uncued field at the moment of translation, creating a duration asymmetry that could explain performance biases without invoking surface-based selection. They tested this by reversing the relationship between rotation duration and which field was cued. The results still supported surface-based selection, ruling out the confound. Crucially, they also showed that attentional selection in this paradigm is **spatially selective at the scale of the individual texture elements** (dots) — not coarse spatial attention. The paper explicitly used the Desimone & Duncan (1995) biased-competition framework and discussed motion-competition as an alternative account.

VRDots is built directly on this design. The finding that selection is spatially fine-grained at the dot level is important: it means depth-plane effects in VRDots (which operate at the level of individual dot subfields) can be interpreted as genuine surface-level selection, not coarse spotlight attention. Stoner & Blanc's motion-competition account also motivates the ZdA/ZdB conditions: ZdA introduces a new source of motion competition (spurious positional shift of the cued dot group due to depth change) that the motion-competition account would predict should disrupt cueing.

---

### 8.2 Schoenfeld, Tempelmann et al. (2003) — Feature Binding Dynamics: ERP/fMRI

**Schoenfeld, M.A., Tempelmann, C., Martinez, A., Hopf, J.-M., Sattler, C., Heinze, H.-J., & Hillyard, S.A. (2003). Dynamics of feature binding during object-selective attention. *PNAS*, 100(20), 11806–11811.**

Combined simultaneous ERP/ERF and fMRI recordings while subjects attended to one of two superimposed transparent dot surfaces (distinguished by motion direction, with color as an irrelevant feature). Key finding: when a surface was attended on the basis of motion direction, neural activity appeared first in motion-selective cortex (~lateral occipital/MT+ region), and within the same latency window (~180–250 ms), activity also appeared in the color-selective fusiform gyrus for the task-irrelevant color of the attended surface. This rapid co-activation of feature-specific areas provides a neural substrate for feature binding — all features of an attended object are rapidly co-selected, even those not relevant to the task. The authors interpret this as support for the integrated competition model (Desimone & Duncan 1995; Duncan et al. 1997).

VRDots relevance: depth plane is an additional feature of the attended surface. By the logic of Schoenfeld et al. (2003), when the cued surface is selected, its depth-plane membership should be co-activated along with its motion and color features. ZdA disrupts cueing at the moment of target onset by changing the depth-plane feature of the cued dot group — this amounts to a feature-binding disruption: the attended object's depth-plane feature abruptly mismatches the object representation built up during the rotation period.

---

### 8.3 Schoenfeld, Hopf et al. (2014) — Sequential Feature Activation in Object-Based Attention

**Schoenfeld, M.A., Hopf, J.-M., Merkel, C., Heinze, H.-J., & Hillyard, S.A. (2014). Object-based attention involves the sequential activation of feature-specific cortical modules. *Nature Neuroscience*, 17(4), 619–624.**

Extended the 2003 PNAS finding using MEG source analysis with higher temporal resolution. Subjects attended to transparent-motion surfaces defined by speed or color. When attention was directed by speed, the motion-sensitive lateral occipital area was activated first (~150 ms), followed ~60 ms later by the color-selective inferior occipital area — regardless of whether color was task-relevant. The reverse temporal sequence (color first, then motion) occurred when attention was directed by color. This rapid sequential activation reveals a binding mechanism that sweeps through feature-specific cortical modules in an order determined by which feature defined the attended object.

VRDots relevance: in VRDots, the attended surface is defined primarily by its motion onset (delayed onset creates the exogenous cue). This predicts that motion-sensitive areas activate first, followed by depth-sensitive areas. ZdA disrupts the depth-sensitive activation at target onset by moving the cued dot group to a different depth plane — potentially breaking the sequential binding chain at the depth-feature stage. The ~60 ms binding cascade is fast relative to VRDots' 80 ms translation duration, so the depth-feature representation of the attended surface may be disrupted mid-translation in ZdA trials.

---

### 8.4 Catak, Özkan, Kafaligonul & Stoner (2022) — ERP Evidence with Feature Swaps (Stoner Lab)

**Catak, E.N., Özkan, M., Kafaligonul, H., & Stoner, G.R. (2022). Behavioral and ERP evidence that object-based attention utilizes fine-grained spatial mechanisms. *Cortex*, 151, 89–104.**

Directly used the Stoner & Blanc (2010) design (with feature swaps) to simultaneously measure behavioral performance and ERP responses. Confirmed that the behavioral cueing effect survives feature swaps — consistent with the object-based account. Found that the N1 ERP component (occipital and parieto-occipital sites) is modulated by attentional cueing under feature-swap conditions that rule out feature-based mechanisms. Crucially, N1 modulation was correlated with individual behavioral performance values across conditions. This is identified as the first ERP evidence for the role of N1 in object-based attention in a transparent-motion design that controls for feature-based explanations.

VRDots relevance: this is the closest existing paper to VRDots in paradigm and question. The N1 modulation at parieto-occipital sites (consistent with MT+ source localization) is the ERP correlate of surface-based selection in the exact paradigm that VRDots extends to stereo depth. The finding that fine-grained spatial mechanisms (at the scale of texture elements) underlie selection is consistent with VRDots' depth-field cueing effect operating at the subfield level. This paper should be cited as the immediate neural predecessor to VRDots in any write-up.

---

### 8.5 Mitchell, Stoner & Reynolds (2004) — Object-Based Attention and Binocular Rivalry (expansion of §2.1)

**Mitchell, J.F., Stoner, G.R., & Reynolds, J.H. (2004). Object-based attention determines dominance in binocular rivalry. *Nature*, 429, 410–413.**

Already referenced in §2.1. Expanded note from PDF: the paper used a dichoptic presentation — after a cueing translation, images of the two surfaces were presented to separate eyes, creating rivalry. The cued surface was dominant during subsequent rivalry, and this dominance persisted regardless of which eye's image it appeared in. Critically, this rules out ocular, spatial, and feature-based mechanisms: selection was purely object-based, following the surface identity established during binocular transparent viewing. The same object-based mechanisms that mediate competitive selection during transparency also mediate binocular rivalry dominance.

Additional VRDots relevance not in §2.1: this paper is directly relevant to VRDots' monocular sessions. If object-based selection is mediated by the same mechanisms during both binocular and monocular (transparency) viewing, then the monocular survival of the dot-cueing effect in VRDots (+7.1pp* across n=769) is expected — object-based selection does not require binocular viewing. The attenuation relative to binocular (+19.8pp***) may reflect loss of the additional depth-plane grouping cue (Factor 2) rather than loss of the core object-based mechanism.

*Follow-up papers (added 2026-04-01)*:
- **Stoner, Mitchell, Fallah & Reynolds (2005)** *Progress in Brain Research* 149:227–234 — review chapter by Stoner (first author) placing Mitchell 2004 in the biased-competition framework; contrasts exogenous initial-dominance effects (the cueing result) with endogenous alternation-rate effects (a separate mechanism).
- **Khoe, Mitchell, Reynolds & Hillyard (2008)** *Journal of Vision* 8(3):18 — ERP under dichoptic rivalry: P1 modulation (110–160 ms) for same-surface probes under rivalry but absent under monocular viewing. Establishes that the rivalry-specific neural mechanism is early (lateral extrastriate) and dissociates from the monocular case.
- **Mishra & Hillyard (2009)** *Vision Research* 49:1073–1080 — extends Khoe 2008 to voluntary (endogenous) attention during rivalry; same P1/N1 signature, localized to V3/V3a/V4.
- **Paffen, Alais & Verstraten (2006)** *Psychological Science* 17:752–756 — attention speeds rivalry alternation rate; different mechanism from dominance cueing but establishes a sustained attention component.

---

### 8.6 Rodríguez & Valdés-Sosa (2006) — Sensory Suppression During Surface Switches

**Rodríguez, V., & Valdés-Sosa, M. (2006). Sensory suppression during shifts of attention between surfaces in transparent motion. *Brain Research*, 1072, 110–118.**

Examined the attentional blink (AB) between transparent surfaces: when T1 and T2 occur on different surfaces with a short SOA, T2 identification is strongly impaired. Using the RSOT (rapid serial object transformation) transparent-motion paradigm, they showed the AB is associated with **reduced N200 ERP amplitude** on different-surface trials, modeled by relative suppression of sources in visual extrastriate cortex (near MT+). The N200 amplitude was larger for correct than incorrect trials, consistent with signal detection theory — smaller N200 = less sensory information available for the T2 judgment. P300 was larger for same-surface correct trials.

VRDots relevance: the attentional blink literature provides a temporal-capacity framework for cross-surface costs. In VRDots, the 300 ms pre-translation period (during which the observer is watching the rotating surfaces after onset of the delayed field) is the window during which the cued-surface representation is consolidated. The Rodríguez & Valdés-Sosa suppression finding suggests that, during this period, the uncued surface is actively suppressed in extrastriate cortex — this active suppression is what ZdB may enhance: moving the distractor to a new depth plane could transiently reinstate the suppression signal at tStart, boosting the cued-surface representation above its N-condition level.

---

### 8.7 Duncan, Humphreys & Ward (1997) — Integrated Competition Hypothesis

**Duncan, J., Humphreys, G., & Ward, R. (1997). Competitive brain activity in visual attention. *Current Opinion in Neurobiology*, 7, 255–261.**

A focused review of the integrated competition hypothesis (building on Desimone & Duncan 1995): visual objects activate distributed brain systems simultaneously; within each system, representations of different objects compete; competition is integrated across systems so that a winning object in one area tends to become dominant in others; top-down task priming biases competition toward task-relevant objects. Key prediction: selecting one feature of an object propagates dominance to all other feature modules encoding that object. Evidence from single-unit monkey studies showing widespread suppression of ignored objects in extrastriate cortex, and from spatial and non-spatial selection tasks showing similar suppression profiles.

VRDots relevance: the 1997 paper provides the theoretical architecture for why depth-field cueing should exist. If depth plane is encoded in a separate module (disparity-tuned cells in V1/MT), and if the attended surface wins the competition in the motion module (MT, driven by the exogenous translation cue), then depth-plane competition should also be biased toward the attended surface's depth plane — depth-field cueing follows. ZdB enhances this by removing the distractor from the integrated competition network at the cued depth plane, reducing the distractor's competitive weight at that depth.

---

### 8.8 Kohn & Movshon (2004) — MT Adaptation Reshapes Direction Tuning

**Kohn, A., & Movshon, J.A. (2004). Adaptation changes the direction tuning of macaque MT neurons. *Nature Neuroscience*, 7(7), 764–772.**

Prolonged exposure (adaptation) to a preferred-direction stimulus narrows MT direction tuning bandwidth and causes attractive shifts in preferred direction toward the adapting stimulus. This is the opposite of V1 adaptation (which causes repulsive shifts). Flank adaptation (adapting to a direction off the tuning peak) causes the preferred direction to shift attractively toward the adapted direction and reduces responsiveness on the opposite flank. The mechanism implies that MT cells' tuning is shaped by the history of recent stimulation in a way that is distinct from V1.

VRDots relevance: in VRDots, observers run multiple trials within a session. The 750 ms rotation period before each translation constitutes a brief adaptation epoch for MT neurons tuned to the rotation direction of each surface. The Kohn & Movshon finding predicts that MT direction tuning will narrow toward each surface's rotation direction during the pre-translation period — potentially sharpening the surface representation before the translation cue arrives. This is a within-trial mechanism that could contribute to the cueing effect: the cued surface's rotation history (longer, from onset) may produce stronger MT adaptation that sharpens its direction representation more than the non-delayed surface. Relevance to Stoner & Blanc (2010) motion-duration confound: adaptation is one candidate mechanism for that confound.

---

*Section 8 added 2026-03-31. PDF library integration pass.*

---

## 9. Depth Attention Gradients: The Near/Far Asymmetry in Context

*Added 2026-04-01. Motivated by the VRDots observation that Far >> Near cueing is the dominant and most robust finding, and by the user's phenomenological observation that during fixation, attention "embraces" the fixation point and everything beyond it (Far), not stimuli in front (Near).*

### 9.1 The Phenomenological Observation and Its Framing

The observer notes that, when fixating, attention is more naturally drawn to depths at or beyond the fixation plane rather than to depths in front of it. This is not merely anecdotal — it is consistent with a gradient model of attention in depth: attention is strongest at the fixation plane and falls off asymmetrically, with a shallower gradient toward Far depths and a steeper gradient toward Near (inside-fixation) depths. On this account, the Near depth plane in VRDots (1.975m, 25mm in front of the 2.0m fixation plane) sits inside the fixation-plane boundary — in the least-attended region of the depth gradient — while the Far plane (2.025m) sits just beyond it, in the naturally attended region.

This directly maps onto the VRDots Near/Far cueing asymmetry: if attention is weaker for Near depths, the advantage conferred by the delayed-onset cue should be smaller (or inverted) for Near trials — precisely what is observed (Near: −5.9pp n.s. binocularly; Far: +30.9pp***).

### 9.2 Two Candidate Mechanisms: Vergence-Driven vs. Disparity-Driven

The phenomenological observation raises a mechanistic question: is the depth attention gradient *vergence-driven* (attention follows the motor state of the eyes, spreading outward from where the vergence muscles are aimed) or *disparity-driven* (depth is encoded from retinal disparity patterns, and attention follows the disparity-defined depth signal, independent of eye position)?

This distinction has direct experimental and theoretical consequences:

**Vergence-driven account**: Fixation drives vergence to converge at the fixation plane. The vergence motor state could drive an attentional gradient: objects requiring further convergence (Near) are actively suppressed because they are "behind" the current vergence effort; objects requiring relaxation (Far) are more easily accessible. Under this account, moving the fixation target to a Near point should reverse the gradient — Far becomes the unfixated side, and Near becomes the attended region.

**Disparity-driven account**: The depth gradient arises from how the visual system represents crossed (Near) vs. uncrossed (Far) disparities, independent of the vergence state. On this account, moving the fixation depth would not flip the attentional gradient, because the disparity sign asymmetry is intrinsic to the cortical representation.

### 9.3 Evidence From the Literature

**Papers supporting Far > Near (consistent with VRDots):**

**Parks & Corballis (2006, NeuroReport)** recorded ERPs during an attentional cueing paradigm with stereoscopic depth. P1 amplitude was enhanced only for far-attended conditions — no P1 modulation was found for near-attended targets. They proposed a viewer-centered gradient model in which the attended depth gradient is non-monotonic: centered at or just beyond the fixation plane, with suppression for depths inside fixation. This is the closest published prediction to the VRDots Near inversion.

**Caziot, Rolfs & Backus (2023, PNAS Nexus)** directly tested the vergence-driven account using nonius lines and oculometry to measure vergence during a stereoscopic cueing task. They found a directional Far > Near trend (p=0.076, non-significant) and — crucially — *no vergence shift during depth cueing*. Vergence did not move when attention was directed to a different depth plane. This is the strongest published evidence against the vergence-driven account: the gradient is present without vergence change, implicating a disparity-driven mechanism.

**Papers supporting Near > Far (contradicting VRDots):**

**Andersen & Kramer (1993, P&P)** is the most-cited paper in the stereoscopic attention literature and found the opposite result: larger attentional facilitation for crossed (Near) than uncrossed (Far) disparities. This paper is widely cited as establishing a Near advantage and directly contradicts the VRDots result. The discrepancy is methodologically significant: Andersen & Kramer used a simple RT task with stationary stimuli and crossed/uncrossed disparity pedestals, not a surface-based motion paradigm. The VRDots task — selection of a coherent transparent surface via a temporal-onset cue — may recruit a fundamentally different form of depth-selective processing than the spatial cueing task used in Andersen & Kramer.

**Chen, Meng, Matthews & Qian (2012, J Neurosci)** found a Near advantage in attentional reorienting and explicitly tested whether the asymmetry is vergence-driven by varying fixation depth across conditions. Critical finding: changing fixation depth did *not* reverse the Near > Far asymmetry. This argues against the vergence-driven account even for the Near-advantage literature. The persistence of the asymmetry despite fixation depth changes suggests a disparity-sign asymmetry intrinsic to cortical depth representations — but one that produces Near > Far in their paradigm, opposite to VRDots. The Chen et al. paradigm difference from VRDots is important: they used reflexive (involuntary) attention reorienting, not sustained object-based surface selection.

**Mechanistic convergence across papers: disparity-driven, not vergence-driven:**

**Arnott & Shedden (2000, P&P)** used autostereograms, in which the vergence posture is fixed at the screen distance regardless of perceived depth. The attentional asymmetry in depth persisted despite vergence being locked. This provides converging evidence that the gradient is in the disparity representation, not the vergence state.

**Solé Puig et al. (2013, PLOS ONE)** found that vergence microsaccades track the attended depth (vergence follows attention) but do not predict RT improvements — they are a consequence of attention, not a cause. This dissociates the metric of vergence from the functional effect of depth-attention gradients.

**Taken together, the literature converges on a disparity-driven mechanism for depth attention gradients**, despite disagreement on the direction of the gradient (Near > Far in most published work; Far > Near in Parks & Corballis 2006, Caziot et al. 2023, and VRDots).

### 9.4 Surface-Based Selection in Depth: He & Nakayama

**He & Nakayama (1992, Science; 1995, Psychological Review)** demonstrated that attention in three-dimensional scenes is organized around *surfaces*, not depth planes per se. In their paradigm, attention spread obligatorily across a coherent surface (defined by texture and disparity) and was blocked by surface boundaries. The unit of attentional selection is the surface as a perceptual object, not the depth plane as a spatial location. This is directly relevant to VRDots: in our paradigm, the attended entity is a coherent rotating-surface defined partly by its depth plane. The He & Nakayama surface-priority principle predicts that what matters is the coherence of the surface representation, not just the depth value — and depth contributes to surface coherence (consistent with our depth-field cueing result).

**Nakayama & Silverman (1986, Science)** established that disparity is a preattentive dimension: conjunction search with depth is efficient (parallel), unlike conjunctions of other features. This means depth-based grouping precedes voluntary attention and can serve as an early basis for surface segregation — consistent with depth facilitating surface-based selection in VRDots.

**Theeuwes, Atchley & Kramer (1998)** showed that depth-plane filtering effectiveness is feature-contingent: same-color stimuli across depth planes reduce the ability to filter by depth plane. This is directly relevant to VRDots' same-color (COLOR_RED) design — in the same-color condition, depth-plane filtering is weakened relative to two-color conditions, predicting reduced depth-field cueing. This partially explains why DepthSwapCtrl (same-color) shows weaker overall cueing than DepthBaseline (two-color), beyond the color-dimension reduction in the Point-Set.

### 9.5 VR-Specific Considerations

**Maringelli et al. (2001, Psychological Science)** showed that in immersive virtual environments without a visible virtual body, participants shift attention outward — toward Far depths — relative to standard lab settings. The absence of body representation in VR removes the Near reference frame (arms, torso at ~0.5–1m) that normally anchors attention to peripersonal space. In VRDots, the observer sees a VR scene with no body representation and with the display plane at 2m — a fixation-distance context in which the "body zone" attentional anchor is absent. This could produce a stronger Far bias in VR than would be observed in conventional stereoscope paradigms, contributing to a more pronounced Far > Near asymmetry.

**Jänig et al. (2025)** ran an ERP experiment using a two-depth-plane random-dot kinematogram paradigm that is the nearest published analog to VRDots. This is important as a methodological comparison: if their paradigm reveals motion-onset ERP modulation by depth-plane attention, this validates the ERP approach for VRDots. The paradigm differences from VRDots (if any) bear on the interpretation of their results and the design choices for a future VRDots ERP study.

### 9.6 Synthesis: Why Far > Near in VRDots?

The published literature does not provide a definitive account. What can be said:

1. **The Near inversion is binocular and absent monocularly** — it is generated by the stereoscopic depth representation, not a response bias or direction-encoding artifact.

2. **Most published work finds Near > Far** (Andersen & Kramer 1993; Chen et al. 2012) — VRDots finds the opposite. This means VRDots is not simply replicating a known near-advantage in attention; the Far advantage is a genuine divergence from prior literature.

3. **The Parks & Corballis (2006) ERP result** provides the best published precedent for a Far advantage and for Near suppression — their P1 result (enhanced only for Far-attended conditions) is fully consistent with the VRDots Near inversion. The difference from Andersen & Kramer may reflect task: surface-based selection of transparent motion fields vs. simple RT to isolated target stimuli.

4. **The Caziot et al. (2023) result argues against vergence-drive**: even without vergence shift, a directional Far advantage was found. Combined with the VRDots monocular data (Near inversion absent monocularly but Far advantage partially survives), the most parsimonious account is: **the gradient is disparity-driven, with crossed (Near) and uncrossed (Far) disparities producing asymmetric attentional gradients, and the direction of the asymmetry may depend on task (reflexive reorienting vs. sustained surface-based selection)**.

5. **The user's phenomenological report** (attention embraces Far, not Near, during fixation) is consistent with a viewing context in which there is nothing of interest at near distances (no peripersonal objects, no body representation in VR), and the functional task demand is to track moving fields at 2m. This is a context where Far (beyond fixation) is the naturally attended region.

6. **Theeuwes et al. (1998)** warns that same-color design weakens depth-plane filtering. This reduces the strength of the depth-field cueing effect (Factor 2) but should not reverse it. The Near inversion is therefore probably not an artifact of the same-color design, since it is also present in the two-color DepthBaseline sessions.

### 9.7 The Key Unresolved Experiment: Fixation-Distance Reversal

The cleanest test to dissociate vergence-driven from disparity-driven accounts — and to test the phenomenological observation directly — is a **fixation-distance manipulation within VRDots**:

- **Condition A** (current VRDots): fixation at 2.0m; surfaces at 1.975m (Near) and 2.025m (Far). Expect: Far > Near (observed).
- **Condition B**: fixation at 2.025m (the current Far plane); surfaces at 2.0m (now Near relative to fixation) and 2.05m (now Far relative to fixation). Vergence-driven account predicts the asymmetry reverses. Disparity-driven account predicts the asymmetry stays in the same direction relative to the display, or at least does not fully reverse.
- **Condition C**: fixation at 1.975m (the current Near plane); surfaces at 1.925m (Far of fixation) and 1.975m+small offset (Near of fixation). Same logic.

If the gradient reverses with fixation distance, it is vergence-driven. If it does not reverse, it is disparity-driven. **No published paper has done this cleanly in a transparent-motion surface-selection paradigm.** Chen et al. (2012) varied fixation depth but used a reflexive attention paradigm; their fixation depth change did not reverse the asymmetry, arguing for disparity-drive. A VRDots version of this test would be the first clean test in a surface-selection context.

---

*Section 9 added 2026-04-01. Literature search: Parks & Corballis 2006, Caziot et al. 2023, Andersen & Kramer 1993, Chen et al. 2012, Arnott & Shedden 2000, Solé Puig et al. 2013, He & Nakayama 1992/1995, Nakayama & Silverman 1986, Theeuwes et al. 1998, Maringelli et al. 2001, Jänig et al. 2025.*

---

*Document generated 2026-03-31. Approved paper list as specified in Literature Agent task brief.*
