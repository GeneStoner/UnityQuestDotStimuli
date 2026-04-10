# Literature Review: Perceptual Depth-Ordering in Transparent Motion Displays

**Prepared by: VRDots Literature Agent**
**Date: 2026-04-09**
**Scope: Papers bearing on perceived depth order in superimposed random-dot motion displays, without explicit disparity cues unless noted. Confidence ratings accompany each citation.**

---

## 1. Perceptual Depth Ordering in Transparent Motion: What Determines Which Surface Appears In Front?

The most direct body of work on this question comes from a group of studies on what has been named "motion transparency depth rivalry" — the phenomenon that two superimposed random-dot fields moving in opposite directions produce a percept of two transparent surfaces, but the depth ordering of those surfaces (which one appears in front) is not specified by the stimulus and is therefore ambiguous. This rivalry is genuinely bistable: depth-order reversals occur spontaneously during prolonged viewing, in a manner qualitatively analogous to binocular rivalry.

**Mamassian & Wallace (2010). "Sustained directional biases in motion transparency." *Journal of Vision* 10(13).** (Confidence: HIGH — confirmed via PubMed PMID 21149310.)
The key characterization paper for depth-order bias in transparent motion. Mamassian and Wallace measured depth-order preferences across 34 naive observers and found two results of fundamental importance. First, nearly every observer showed a strong, consistent directional bias — one motion direction was reliably perceived in front on most trials. Second, the preferred direction was almost always either rightward or downward across observers, suggesting a weak ecological bias toward lower or rightward motion being "in front" (possibly reflecting ground-plane or optic-flow statistics). The bias was idiosyncratic, stable across days, and dependent on the orientation of the display. Importantly, no consistent relationship was found between perceiving the faster or slower surface in front — speed alone is not the operative variable.
*VRDots implication*: In the VRDots baseline (no stereo depth), the two rotating fields are unlikely to spontaneously assume a consistent depth order on every trial. Observers may perceive depth ordering idiosyncratically, and this perceived ordering may be direction-biased. The cued field's perceived depth order — and whether it is consistent with or opposed to the observer's natural directional bias — could modulate the baseline cueing effect without any explicit stereo manipulation. This has not been controlled for in VRDots and should be assessed empirically via intermixed depth-order probe trials.

**Chopin & Mamassian (2011). "Usefulness influences visual appearance in motion transparency depth rivalry." *Journal of Vision* 11(7):18.** (Confidence: HIGH — confirmed via PubMed PMID 21705461.)
A top-down modulation result: when one of the two transparent surfaces contained a visual search target, observers more often reported that surface as being in front, even though depth order was arbitrarily assigned by the display. Task usefulness shifted idiosyncratic depth-order preferences. This demonstrates that perceived depth order is not a purely bottom-up, fixed percept — it is sensitive to attentional and task-strategic factors.
*VRDots implication*: The CUED surface in VRDots may be systematically more likely to be perceived as in front due to its attentional salience (onset translation cue). A causal loop may exist: attention biases depth order, and perceived depth order in turn may reinforce attentional selection. This could amplify the cueing effect in zero-disparity conditions in ways that are confounded with stereo depth effects.

**Hwang & Schütz (2020). "Idiosyncratic preferences in transparent motion and binocular rivalry are dissociable." *Journal of Vision* 20(12):3.** (Confidence: HIGH — confirmed via PubMed PMID 33156337, PMC7671871.)
A comprehensive dissociation study: directional preferences in transparent motion depth rivalry and contrast-polarity preferences in binocular rivalry were not correlated across observers. Transparent motion and dichoptic rivalry are governed by different computational mechanisms despite superficial similarity.
*VRDots implication*: VRDots binocular sessions drive both mechanisms simultaneously (both fields presented to both eyes with explicit disparity). Adding disparity should shift the operative mechanism from transparent-motion depth-rivalry (direction-driven, idiosyncratic) toward binocular disparity (more consistent and stimulus-driven), increasing per-trial reliability of depth-order perception.

---

## 2. Figure-Ground in Random Dot Kinematograms

**Braddick (1997). "Local and global representations of velocity: Transparency, opponency, and global direction perception."** (Confidence: MODERATE — cited consistently in the motion transparency literature; venue details partially inferred.)
Key principle: in RDKs, there is no inherent figure/ground assignment when two populations are equal in number, speed, and contrast. Figure/ground assignment is determined by asymmetries in any of these variables. Without disambiguating cues, depth ordering in a transparent RDK is genuinely ambiguous at the neural level.

**Snowden (1999). "Single units and perception: A critique of some recent attempts." *Current Biology* 9:R346 (review of motion transparency).** (Confidence: HIGH — confirmed in project literature files.)
Without disambiguating cues, two motion directions coexisting at the same retinal location partially cancel or fuse in the motion pathway. Assignment of one population as "figure" is facilitated by non-motion cues including color, spatial frequency, contrast, and disparity.

**Madelain, Herman, Harwood & Wallman (2012). "Motion transparency: depth ordering and smooth pursuit eye movements." *Journal of Vision*.** (Confidence: HIGH — PubMed PMID 22205685 confirmed.)
Direct investigation of depth-ordering determinants in transparent motion. Key findings: (1) surfaces with more dots tend to be perceived in the back; (2) surfaces adapted to the current direction are perceived in the back; (3) slower-moving surfaces tend to be perceived in the back (inverting the naive expectation); (4) surfaces moving in the direction of ongoing smooth pursuit tend to be perceived in the back.
*VRDots implication*: In VRDots, both surfaces rotate at matched speed, so speed cannot drive depth-ordering biases. However, adaptation effects could accumulate across trials, potentially biasing which field appears in front in ways unrelated to stereo depth.

---

## 3. Stoner & Albright: Luminance, Transparency, and Depth Order

**Stoner, Albright & Ramachandran (1990). "Transparency and coherence in human motion perception." *Nature* 344:153.** (Confidence: HIGH — local PDF confirmed in project; PMID 2308632.)
The foundational paper establishing that intersection luminance in overlapping gratings determines whether the percept is coherent or transparent. When intersection luminance is consistent with physical transparency (photometric constraint satisfied), two gratings slide past each other and a spontaneous depth ordering is perceived. The depth-ordering is governed by the transparency constraint: the grating that "acts as the occluder" is perceived as in front.
*VRDots implication*: VRDots uses discrete dots rather than gratings, removing the intersection luminance constraint. This makes depth-order assignment more ambiguous in zero-disparity conditions — less photometric information is available to constrain which field appears in front.

**Stoner & Albright (1998). "Luminance contrast affects motion coherency in plaid patterns by acting as a depth-from-occlusion cue." *Vision Research* 38:387–401.** (Confidence: HIGH — PubMed PMID 9536362.)
Quantitative follow-up establishing that higher-contrast components are assigned as "in front" — a heuristic consistent with higher contrast correlating with nearer objects in natural scenes.
*VRDots implication*: In VRDots color conditions (red vs. green), residual luminance contrast differences may introduce a non-arbitrary depth-from-occlusion cue, potentially creating a consistent depth ordering even without stereo disparity.

---

## 4. Nakayama, Shimojo & Silverman (1989): Disparity Resolves Depth Order

**Nakayama, Shimojo & Silverman (1989). "Stereoscopic depth: its relation to image segmentation, grouping, and the recognition of occluded objects." *Perception* 18(1):55–68.** (Confidence: HIGH — PubMed PMID 2771595.)
Disparity assignment at borders designates one surface as "intrinsic" and another as occluded, providing a powerful perceptual grouping cue that influences surface completion and object recognition. Adding binocular disparity to a previously ambiguous transparent display immediately and categorically resolves depth order: the far-plane surface is perceptually "behind" the near-plane surface, with stable, consistent, per-trial assignment.
*VRDots implication*: Adding stereo depth to VRDots should not merely modify the cueing effect quantitatively but should qualitatively change the reliability of depth-plane identity as a feature of the attentional object. In binocular VRDots, the observer "knows" which field is near and which is far on every trial — a perceptual ground truth not available in 2D transparent motion paradigms.

---

## 5. Disparity and Depth-Order Assignment: Immediate Resolution

**Snowden & Rossiter (1999). "Perceiving motion in depth using binocular and monocular cues." *Perception* 28:193.** (Confidence: HIGH — confirmed in project literature files.)
Adding disparity separation between signal and noise dot populations in a transparent RDK substantially reduces direction-discrimination thresholds. The mechanism is that disparity provides an unambiguous segmentation cue resolving depth ordering reliably and per-trial, allowing selective attention to the attended surface.
*VRDots implication*: Stereo disparity in VRDots (0.05 m at 2 m viewing distance, ~2–3 arcmin) shifts the task from ambiguous depth-rivalry to per-trial resolved depth ordering, qualitatively changing the information available to the attentional system.

**Bi-stable depth ordering of superimposed moving gratings (2009). *Journal of Vision*.** (Confidence: HIGH — PubMed PMID 19146253 confirmed.)
Spatial frequency ratio had a stronger effect on perceived depth than speed ratio, and could override stereoscopic disparity cues when the ratio was sufficiently large. The fraction of dominance time was a graded function of the cue ratio.
*VRDots implication*: In VRDots rotating fields, dot populations are matched in spatial frequency, density, and dot size. Zero-disparity depth ordering is therefore maximally ambiguous, with individual directional biases dominating. Stereo disparity is the most reliable way to impose consistent depth ordering.

---

## 6. Neural Correlates of Depth-Order Assignment

**Natsukawa, Ichikawa, Nakauchi & Matsuda (2015). "Cortical activation associated with determination of depth order during transparent motion perception." *Human Brain Mapping* 36(10):3922–3934.** (Confidence: HIGH — PMC6869142 confirmed.)
Simultaneous fMRI/MEG study of depth-order determination in transparent motion. Key findings: depth-order determination specifically recruited bilateral intraparietal sulcus (IPS), right lateral occipital (LO), and anterior cingulate cortex (ACC). The MEG time course localized activity to the 216–405 ms window after stimulus onset. Depth-order assignment in transparent motion is not automatic or early — it recruits dorsal-stream and executive areas and takes 200–400 ms.
*VRDots implication*: Depth-order assignment has ample time to complete (200–400 ms per Natsukawa et al.) well before the translation onset. The depth planes in VRDots are present from trial onset: Field A (the non-delayed field) is visible from the very beginning of the trial, and Field B (the delayed field) appears after an onset delay. The total pre-translation interval — from trial onset to translation onset — is determined primarily by the ~750 ms delay period plus any additional pre-translation window, giving well over 1000 ms for depth-order processing. Even for the delayed field alone, by the time it appears and becomes the object of depth-order assignment, substantial time remains before translation onset. In zero-disparity baseline conditions where spontaneous assignment is bistable, depth-order assignment should still reach a consistent per-trial resolution well within the available window; the Natsukawa et al. timing concern does not constitute a confound given the generous temporal margins of the VRDots design.

---

## 7. Spontaneous Depth-Order Reversals: Stability and Timescale

Based on Mamassian & Wallace (2010) and related work:
- **Timescale**: Depth-order reversals in transparent motion rivalry occur on timescales of seconds. Within a single VRDots trial (1530 ms total), a spontaneous reversal is unlikely but possible in zero-disparity conditions.
- **Within-observer consistency**: Individual directional biases are strong (>70% in most observers) and stable across days. Within-individual, zero-disparity depth ordering is highly consistent but idiosyncratic.
- **Color coding slows reversals**: Giving all dots of one surface the same color significantly slowed the rate of depth-order reversals (Mamassian & Wallace 2010). The red/green color separation in DepthColorLinked may itself stabilize perceived depth ordering independent of disparity — a potential partial confound: color separation may improve performance partly by stabilizing depth order, not only by providing a color-based grouping cue.

---

## 8. Attention and Depth Order: The Attentional Topology Hypothesis

Beyond the Chopin & Mamassian (2011) top-down modulation result, a distinct mechanistic hypothesis about the Far > Near cueing asymmetry has been proposed by experimenter GS based on introspection during data collection:

**Attentional gradient / topology account**: When attention is directed to the Near-plane surface, the attentional gradient naturally extends beyond it toward Far — unavoidably including some Far-plane dots and diluting selectivity for the cued Near-plane dots. When attention is directed to the Far-plane surface, there is nothing further in the display, so attentional resources are more concentrated on the Far-plane dots alone. This predicts a Far > Near cueing advantage that depends on display topology (whether anything lies beyond the attended plane) rather than on disparity magnitude per se.

This account is a theoretical proposal by the experimenter (GS), originating from introspective observation during data collection, and is consistent with the general finding that attention can be directed to depth-defined surfaces (Nakayama & Silverman 1986; He & Nakayama 1992). However, the specific directional claim — that attentional gradients extend from near toward far but not the reverse — has no direct empirical support in the published literature. It is a hypothesis, not an established finding. The account contrasts with the Calabro & Vaina (2011) neural cross-talk account (MT disparity-population anisotropy predicts more near-disparity cross-talk). Note: Downing & Pinker (1985) concerns 2D spatial attention shifting (Posner paradigm) and does not address depth; He & Nakayama (1995) concerns perceptual completion across occluding surfaces and does not demonstrate directional attentional gradients in depth. Neither provides direct support for the topology account's directional claim.

**Tension with DepthParam data**: The attentional topology account predicts that the Far > Near gap should *shrink* as depth separation increases. Larger disparity creates stronger perceptual segregation between the two planes, which should reduce gradient spillover from the Near-attending gradient into the Far plane — thereby narrowing the Far > Near advantage. However, the DepthParam data (0.03 m → 0.15 m) show that the Far > Near gap is not clearly consistent with this prediction: if anything, the gap does not shrink at larger separations. This tension does not rule out the topology account — gradient-migration dynamics that scale with disparity may dominate the parametric pattern, with the topology contribution isolable only at shorter SOAs or in the three-plane design — but the tension must be acknowledged as the primary current weakness of the account as a standalone mechanism.

**Critical dissociation experiment**: A three-plane display (Near / Mid / Far) where cueing is to the Mid plane vs. the Far plane. Under the topology account, Mid-plane cueing should be impaired relative to Far-plane cueing (Mid has something beyond it; Far does not). Under the Calabro & Vaina account, Mid should show intermediate performance based on its disparity value. This experiment is feasible in VRDots and has no published precedent.

---

## Key Gaps and VRDots Relevance

**Gap 1 — No published measurement of depth-order reliability in zero-disparity transparent RDKs.**
No study has systematically quantified — with confidence intervals — the fraction of trials on which each dot field is perceived as "in front" in a rotating, superimposed RDK with matched parameters (speed, density, dot size, luminance). VRDots could address this directly via intermixed depth-order probe trials.

**Gap 2 — No study has coupled depth-order bias to the cueing effect.**
Neither Chopin & Mamassian (2011) nor related work asks whether the observer's spontaneous depth-order assignment predicts or modulates the cueing effect magnitude. VRDots can test this directly.

**Gap 3 — No published study has used depth-plane continuity disruption as an attentional probe.**
The ZdA/ZdB manipulation — changing depth-plane membership of specific dots at the moment of the attentional target's onset — is novel. No prior study has asked whether disrupting depth-plane continuity mid-trial impairs performance on a direction-discrimination task.

**Gap 4 — No prior parametric depth-separation × attentional cueing experiment.**
VRDots DepthParam (0.03–0.15 m) provides the first dataset measuring an attentional cueing effect as a function of depth separation. The consistent Far > Near cueing advantage and its complete monocular collapse are empirically new findings.

**Gap 5 — The F1 × F2 conjunction requirement is unpredicted by any existing framework.**
Depth-field cueing (F2) provides benefit only when combined with temporal onset cueing (F1). The UNCUED arm remains near chance throughout all depth experiments despite full access to depth-plane information. No existing model predicts this conjunction requirement.

**Gap 6 — The attentional topology hypothesis (Far boundary advantage) is new and untested.**
The three-plane critical experiment has no published precedent and is uniquely feasible in VRDots.

---

## 9. Implications for VRDots: Does Spontaneous Depth Ordering Explain the Key Findings?

*Added 2026-04-04. Theoretical/speculative analysis — not empirically confirmed.*

A recurring question in interpreting the VRDots baseline cueing effect is whether the onset cue operates purely through temporal tagging — the delayed field is selected because it appeared later and was therefore bound to the attentional pointer — or whether perceived depth ordering of the two fields plays a parallel role, even in zero-disparity conditions. The work of Chopin & Mamassian (2011) raises the possibility that the attended surface in VRDots is not merely more recently onset but is also more likely to be spontaneously perceived as the nearer, figure-like surface. In zero-disparity transparent motion, the field that carries attentional salience — because it constitutes the task-relevant target-bearing surface — is more often reported as appearing in front (Chopin & Mamassian, 2011, PMID 21705461). Additionally, figure-ground principles suggest that the delayed-onset field, which appears abruptly against the background of the continuously present non-delayed field, should be perceived as figure-like; figures are conventionally perceived in front of grounds. If both of these factors consistently assign the delayed (cued) field to the spontaneously near-perceived stratum, then the attentional advantage for the cued field in zero-disparity conditions may be partly driven by a depth-order/figure-ground route, operating in parallel with and independently of the temporal onset signal.

**This hypothesis is partially consistent with the F1 dot cueing effect.** The CUED field is the delayed field — the spontaneously near-perceived, figure-like surface — and the UNCUED field is the non-delayed, ground-like surface. Even setting aside temporal onset information, an observer who uses spontaneous depth-order assignment to select the "near" surface would perform well on CUED trials and poorly on UNCUED trials, simply because the near-perceived field happens to be the delayed one more often than not. This predicts CUED > UNCUED in zero-disparity conditions through a depth-order route, producing a cueing effect that looks behaviorally identical to the temporal onset effect but has partially different mechanistic origins. Importantly, this account does not replace the temporal onset account — both could operate simultaneously, with the spontaneous depth-order bias providing a parallel boost to cueing in zero-disparity conditions.

**The spontaneous depth-ordering hypothesis is in direct conflict with the Far > Near cueing asymmetry.** If the delayed field is spontaneously perceived as near regardless of the stereoscopic depth assignment, then trials in which the delayed field is assigned to the Far depth plane (by disparity) involve a conflict: the spontaneous percept says near, the disparity signal says far. A hypothesis-consistent prediction would be that this conflict imposes a cost, reducing performance on Far-delayed trials relative to Near-delayed trials. But the empirical result is precisely the opposite: Far-plane cueing is substantially stronger than Near-plane cueing across all tested conditions, reaching significance at n=512 in the DepthColorLinked dataset (+8.6pp*). This implies either that disparity immediately and completely overrides the spontaneous depth-order bias with zero residual cost — consistent with Nakayama, Shimojo & Silverman (1989), who showed that binocular disparity provides a categorical, per-trial resolution of depth order that dominates over other cues — or that the Far > Near advantage operates at a level (MT cross-talk, attentional topology) that does not interact with the spontaneous depth-order signal at all. Either interpretation places the Far > Near asymmetry as a genuinely stereoscopic effect, not explicable by any account that appeals to spontaneous depth-order assignment of the delayed field.

**The spontaneous depth-ordering hypothesis is also insufficient to account for the F1×F2 conjunction.** The defining empirical feature of the depth experiments is not the main effects of dot cueing (F1) or depth-field cueing (F2) in isolation, but their conjunction: depth-plane identity provides measurable benefit only in CUED trials, while the UNCUED arm remains near chance across all depth conditions throughout. If spontaneous depth-order assignment provided any useful grouping signal — assigning the translating field to the perceptually near stratum — then observers should benefit from this assignment even on UNCUED trials, where depth information is fully available throughout the trial. They do not: UNCUED performance is uniformly flat regardless of whether the translating field is assigned to the near or far depth plane, and regardless of whether depth is determined by stereoscopic disparity or only by spontaneous assignment. The UNCUED flatness is therefore more stringent evidence than the spontaneous depth-order hypothesis predicts. Depth-plane identity — whether arriving from stereoscopic cues or from spontaneous figural assignment — does not drive attentional selection in the absence of the F1 temporal onset signal. The onset cue is necessary, not merely helpful.

**The key theoretical implication** is that baseline (zero-disparity) and stereoscopic cueing effects may share the F1 temporal onset route but have partially different secondary mechanisms. In zero-disparity conditions, the spontaneous depth-order assignment (delayed = near = figure) may provide an additional, parallel boost to the cueing effect. In stereoscopic conditions, this spontaneous signal is overridden by disparity (Nakayama et al., 1989), and the performance asymmetry reflects the stereoscopic mechanism (MT cross-talk or attentional topology) rather than figural salience. A direct test of this account would require probe trials measuring spontaneous depth-order perception on no-stereo baseline trials — and correlating the probability of reporting the delayed field as "in front" with the magnitude of the cueing effect across observers and sessions. If the spontaneous depth-order hypothesis contributes to F1, the correlation should be positive and reliable.

---

## Confidence Summary by Citation

| Paper | Confidence | Basis |
|---|---|---|
| Mamassian & Wallace (2010), *J Vision* 10(13) | HIGH | PubMed PMID 21149310 confirmed |
| Chopin & Mamassian (2011), *J Vision* 11(7):18 | HIGH | PubMed PMID 21705461 confirmed |
| Hwang & Schütz (2020), *J Vision* 20(12):3 | HIGH | PubMed PMID 33156337, PMC7671871 confirmed |
| Stoner, Albright & Ramachandran (1990), *Nature* 344:153 | HIGH | Local PDF confirmed in project |
| Stoner & Albright (1998), *Vision Research* 38:387 | HIGH | PubMed PMID 9536362 confirmed |
| Nakayama, Shimojo & Silverman (1989), *Perception* 18:55 | HIGH | PubMed PMID 2771595 confirmed |
| Snowden & Rossiter (1999), *Perception* 28:193 | HIGH | Confirmed in project literature files |
| Bi-stable gratings, *J Vision* (2009) | HIGH | PubMed PMID 19146253 confirmed |
| Madelain et al. (2012), *J Vision* | HIGH | PubMed PMID 22205685 confirmed |
| Natsukawa et al. (2015), *Hum Brain Mapping* 36(10):3922 | HIGH | PMC6869142 confirmed |
| Vallortigara & Bressan (1991/1994), *Vision Research* | MODERATE | Title confirmed; some details inferred |
| Braddick (1997) | MODERATE | Cited consistently; venue details partially inferred |
| Snowden (1999), *Current Biology* 9:R346 | HIGH | Confirmed in project literature files |
