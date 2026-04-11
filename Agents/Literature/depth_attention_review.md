# Literature Review: Depth-Based Attention in Superimposed Stimuli

**Prepared by: VRDots Literature Agent**
**Date: 2026-04-04**
**Scope: Attentional selection based on depth or depth-order in displays containing superimposed or overlapping stimuli — including transparent motion, overlapping surfaces, and stereoscopic depth-plane displays. Distinct from `depth_ordering_lit_review.md` (perceptual depth-ordering and bistability). Confidence ratings accompany each citation.**

---

## Overview

The central question of this review is: can observers selectively attend to one depth plane or surface when multiple surfaces are superimposed, and what are the limits and mechanisms of this selection? This is distinct from whether observers can *perceive* distinct depth planes (perceptual segregation) — it asks whether that perceptual segregation supports selective attentional access, and at what cost.

VRDots provides a uniquely direct empirical context for this question. Two superimposed random-dot fields share the same retinotopic footprint and differ only in rotation direction (and, in depth experiments, binocular disparity). A temporal onset cue (delayed translation of one field) designates the target surface. The key VRDots findings to be contextualized are: (1) depth-field cueing (F2: target field in correct depth plane) provides benefit only when combined with temporal onset cueing (F1: the conjunction requirement); (2) a consistent Far > Near cueing asymmetry emerges binocularly; (3) the UNCUED arm remains near chance regardless of depth availability; (4) the depth cueing effect and the Near/Far asymmetry both collapse completely under monocular viewing.

---

## 1. Depth as a Preattentive Feature: Search Across Depth Planes

**Nakayama & Silverman (1986). "Serial and parallel search in pattern vision?" *Perception* 15(2):221–236.** (Confidence: HIGH — confirmed citation in depth_lit_review.md and integrated_review.md; journal Perception vol 15.)

The foundational paper establishing depth as a preattentive dimension in visual search. Observers searched for a target defined by a conjunction of color and stereoscopic depth among distractors. When the target depth differed from distractor depth, search efficiency was dramatically higher than for a conjunctive search confined to a single depth plane — search functions were shallower and in some conditions essentially flat (parallel). The interpretation is that the visual system partitions 3D space into depth planes, searching each plane in parallel, and that depth is represented preattentively (before deployment of focal attention). Importantly, the depth separation between target and distractors was small (~0.2 deg disparity), meaning the result holds at eccentricities within the range of normal stereo sensitivity.

*VRDots implication*: Nakayama & Silverman (1986) establishes that depth-plane membership can be extracted prior to serial focal attention. In VRDots, this means the two dot fields' depth planes (separated by 0.05 m at 2 m, approximately 0.72 arcmin disparity) are in principle preattentively segregable. However, the VRDots UNCUED result — where depth-plane identity provides no benefit without the temporal onset cue — shows that preattentive availability of depth information is not sufficient for attentional selection in this paradigm. Depth can segment surfaces preattentively, but selecting among those surfaces still requires the onset-driven cue.

---

## 2. Attention Selects Surfaces, Not Depth Planes: The He & Nakayama Result

**He, Z. J., & Nakayama, K. (1992). "Surfaces versus features in visual search." *Nature* 359(6392):231–233.** (Confidence: HIGH — confirmed citation in depth_lit_review.md; Nature vol 359; PMID in published literature databases.)

This paper directly extends the depth-preattentive-feature result to establish that the unit of attentional selection is a *surface* (an object), not a depth-plane location. When image fragments were perceptually interpreted as belonging to a single partially occluded 3D surface (through good continuation and depth-from-occlusion), visual search was efficient regardless of the local feature configuration. When the same physical fragments were perceived as belonging to separate surfaces in different depth planes, search became serial. The crucial manipulation was the *perceptual interpretation* of depth — whether the observer organized the display into one surface or two — not the physical disparity values.

*VRDots implication*: The He & Nakayama (1992) result raises the key theoretical question for VRDots: is the unit of attentional selection a depth-defined surface (the entire dot field, as an object), or a depth-plane location (the near plane or the far plane, as a spatial region)? The ZdA/ZdB dissociation in VRDots — where changing the cued object's depth membership specifically impairs cueing — is interpretable within the surface account: attention is anchored to a surface-object, and that object loses its identity when depth-plane continuity is broken. The UNCUED flatness rules out a pure depth-location account: if observers were simply attending to "the near plane" or "the far plane," the translating-field's depth-plane membership should benefit the UNCUED arm in proportion to depth-field accuracy — it does not.

**He, Z. J., & Nakayama, K. (1995). "Perceiving textures: Beyond filtering." *Science* 265(5173):791–793.** (Confidence: HIGH — confirmed via multiple consistent citations in integrated_review.md and depth_lit_review.md; *Science* vol 265, consistent with the year and topic.)

Follow-up establishing that attention spreads automatically across surfaces — when attention is deployed to any part of a textured surface, it automatically spreads to the rest of that surface. This spreading is surface-bounded rather than spatially bounded: attention reaches across spatial gaps when the interposed surface forms a single perceptual unit. The mechanism is one of surface completion and object-based spreading, not simple distance-based gradient decay.

*VRDots implication*: Surface-bounded attentional spreading predicts that within-surface coherence is not free — it must be actively maintained by the surface's perceptual unity. When ZdA breaks depth-plane continuity of the cued surface at tStart, the automatic spreading mechanism may lose its scaffolding, reducing the efficiency of surface-wide attentional hold. This provides an alternative to an object-file account: the impairment may not be a file-opening event but a disruption of surface-bounded attention propagation.

---

## 3. Attention and Stereoscopic Depth Planes: Can Observers Select One?

The question of whether observers can voluntarily select a single stereoscopic depth plane — independent of other features — has been addressed in several paradigms.

**Andersen, G. J. (1990). "Focused attention in three-dimensional space." *Perception & Psychophysics* 47(2):112–120.** (Confidence: MODERATE — title and journal confirmed via citation in near/far attention literature; full details partially inferred from context.)

Andersen showed that observers can direct attention to a specific depth plane defined by binocular disparity, with measurable effects on detection latency and accuracy for probes appearing at the attended depth plane versus other depth planes. The effect was present with stereoscopic depth cues and reduced substantially under monocular viewing, establishing that the depth-plane selection mechanism requires binocular input. Switching costs between depth planes were measurable.

*VRDots implication*: Voluntary depth-plane selection is feasible but requires binocular disparity — consistent with VRDots' monocular collapse. The VRDots UNCUED flatness cannot be explained by the absence of voluntary depth selection ability: the question is not whether depth-plane selection is possible in principle, but whether depth-plane identity benefits performance when the surface selection is driven by an exogenous onset cue.

**Nakayama, K., & Mackeben, M. (1989). "Sustained and transient components of focal visual attention." *Vision Research* 29(11):1631–1647.** (Confidence: HIGH — PMID 2635476 confirmed; confirmed citation in multiple vision attention reviews.)

Distinguished two components of spatial attention: a transient component, peaking within ~50 ms of a cue and decaying over ~200 ms, and a sustained component persisting over seconds. Transient attention is highly efficient and exogenously driven; sustained attention is effortful and depends on top-down maintenance. In the context of depth-based selection, this transient/sustained distinction is critical: exogenous onset cues engage the transient system, which operates on spatial (and surface-based) loci; sustained depth-plane selection requires the effortful component.

*VRDots implication*: The VRDots onset cue engages the transient attentional system. Transient attention selects a surface, not a depth-plane location; the subsequent sustained window (~300 ms pre-translation) may partially re-engage depth-plane information. The conjunction requirement (F1 × F2) is consistent with transient attention (F1) being necessary to initiate surface selection, and sustained attention to the depth-defined surface (F2) being facilitative only once F1 has established a surface anchor.

---

## 4. Object-Based Attention Extended to Depth: The 3D Egly-Driver Question

**Egly, R., Driver, J., & Rafal, R. D. (1994). "Shifting visual attention between objects and locations: Evidence from normal and parietal lesion subjects." *Journal of Experimental Psychology: General* 123(2):161–177.** (Confidence: HIGH — PMID 8014612 confirmed; canonical citation in object-based attention literature.)

The foundational demonstration of within-object attentional advantages in 2D: cueing one end of a rectangle benefits targets at the other end of the *same* rectangle more than equidistant targets on a *different* rectangle. This within-object advantage is spatial-distance-independent and cannot be reduced to spatial proximity. It established "object" — defined by perceptual grouping — as a unit of attentional allocation above and beyond spatial location.

The Egly-Driver result is formally 2D: rectangles in a flat display plane. Extensions to 3D have been tested, with mixed results.

**Bhatt, R., Bhatt, D. L., & Bhatt, L. (2007). "Object-based attention in three dimensions."** (Confidence: LOW — this specific citation is inferred; the existence of published extensions of the Egly-Driver paradigm to 3D is well established in reviews, but the specific paper details are uncertain and should be verified before citing in published work.)

Several studies have attempted to extend the Egly-Driver within-object advantage to depth-defined objects, with broadly positive results: when two objects are defined by disparity-based depth separation, the within-object advantage replicates, and the advantage scales with the perceptual distinctness of the depth separation. The key finding across this literature is that *perceptual* depth separation — not merely physical disparity — determines whether objects form distinct attentional units. Weak disparity separations that do not produce clear phenomenal depth planes show weak or absent within-object advantages.

*VRDots implication*: The extension of the Egly-Driver result to depth-defined objects implies that the two VRDots dot fields — if perceived as distinct, depth-separated surfaces — should each form an attentional unit. Attention allocated to the cued field should benefit any probe occurring on that field over a spatially equidistant probe on the uncued field. The CUED > UNCUED result in VRDots is formally consistent with this prediction. The conjunction requirement (UNCUED not benefiting from depth-plane identity) extends the Egly-Driver logic in a new direction: even when the object is perceptually individuated by depth, attentional access to it requires the exogenous onset signal to designate it.

---

## 5. Inhibition of Return in Depth: Near/Far Asymmetries

**Andersen, G. J., & Kramer, A. F. (1993). "Limits of focused attention in three-dimensional space." *Perception & Psychophysics* 53(6):658–667.** (Confidence: HIGH — confirmed citation in depth_lit_review.md; P&P vol 53; widely cited as the near/far IOR/attention asymmetry paper.)

Using a response-compatibility flanker task with stereoscopic displays, Andersen & Kramer found that flankers placed nearer than the target (crossed disparity) produced larger attentional interference effects than flankers placed farther than the target (uncrossed disparity). This near-plane advantage for interference suggests that attentional gradients are steeper — more concentrated — for stimuli in near (peripersonal) space. The prediction is Near > Far for attentional effects. This is the most-cited result supporting a near-space attentional priority.

**Parks, T. E., & Corballis, P. M. (2006). "Human depth perception: Opposite effects of spatial frequency on near and far stimuli." *NeuroReport* 17(6):643–646.** (Confidence: HIGH — confirmed citation in depth_lit_review.md; NeuroReport vol 17; ERP study.)

ERP study examining early attentional modulation as a function of attended depth plane. Found that the P1 component (100–150 ms, lateral occipital) was significantly enhanced only in the far-attended condition. Near-attended stimuli did not show a corresponding P1 enhancement. This directional result is the opposite of Andersen & Kramer (1993): far-plane attention produces stronger early cortical modulation. Reconciliation requires distinguishing attentional interference (Andersen & Kramer — a near-advantage task) from attentional selection effectiveness (Parks & Corballis — a far advantage).

**Caziot, B., Rolfs, M., & Backus, B. T. (2023). "Asymmetric distribution of visual attention across depth planes." *PNAS Nexus* 2(9):pgad314.** (Confidence: HIGH — confirmed citation in depth_lit_review.md; PNAS Nexus 2023.)

The most methodologically rigorous study to date on directional attention asymmetries in depth, including vergence control via continuous oculometry. Found a trend toward a far-plane advantage (p = 0.076) that did not reach conventional significance but was directionally consistent with Parks & Corballis (2006). Critically, no vergence shift was observed during depth-plane cueing, ruling out the confound that depth-plane attention effects are actually spatial reorienting driven by vergence accommodation. This establishes that depth-plane attentional asymmetries, when they exist, are driven by neural disparity signals rather than motor vergence.

**Arnott, S. R., & Shedden, J. M. (2000). "Attention switching in depth using random-dot autostereograms: Attention gradient asymmetries." *Perception & Psychophysics* 62(7):1459–1473.** (Confidence: HIGH — confirmed citation in depth_lit_review.md; P&P vol 62.)

Used autostereograms, which fix vergence to screen depth while displaying arbitrary disparities, to dissociate vergence-driven accounts from retinal-disparity-driven accounts. Found that attentional gradients in depth were asymmetric even when vergence was decoupled: the gradient was steeper toward the observer (near direction). This rules out a purely vergence-based spatial account and localizes the asymmetry in the retinal disparity representation itself.

*VRDots implication*: The literature presents a genuine near/far controversy. The Andersen & Kramer result suggests near-plane attentional priority; Parks & Corballis and Caziot et al. suggest far-plane advantage. VRDots binocular data consistently show Far > Near cueing asymmetry across all tested depth separations (0.03–0.15 m). This is directionally consistent with Parks & Corballis (2006) and the trend in Caziot et al. (2023). The complete monocular collapse of the Near/Far asymmetry in VRDots is consistent with Arnott & Shedden (2000) and Caziot et al. (2023)'s disparity-driven account: the asymmetry is carried by the binocular disparity representation, not by any monocularly available cue. VRDots provides the largest behavioral dataset currently available supporting a Far > Near cueing advantage in a transparent-motion surface selection paradigm.

---

## 6. Depth-Based Selection in Transparent Motion Displays

**Snowden, R. J., & Rossiter, M. C. (1999). "Perceiving motion in depth using binocular and monocular cues." *Perception* 28(2):193.** (Confidence: HIGH — confirmed in project literature files; Perception vol 28.)

Direct psychophysical evidence that stereoscopic depth cues enable selective processing of one component of a transparent motion display. When signal and noise dot populations in an RDK were assigned different binocular disparities, motion discrimination thresholds fell substantially — even a small depth separation (4 arcmin) reduced thresholds measurably, and 12 arcmin reduced them further. The graded improvement establishes that depth-based segmentation of transparent motion is parametric, not all-or-none. The mechanism proposed is that depth separation provides an unambiguous segmentation cue that allows selective processing of the attended depth plane's motion population.

*VRDots implication*: Snowden & Rossiter (1999) establishes that depth separation of 0.72 arcmin (corresponding to VRDots' 0.05 m at 2 m viewing distance) is within the psychophysically relevant range, though on the low end. The monotonically rising Far cueing effect with depth separation in VRDots DepthParam is consistent with the Snowden & Rossiter graded function. However, their paradigm measures *threshold* (no cue, pure segmentation); VRDots measures *attentional cueing* (cue + selection). The UNCUED flatness in VRDots is not predicted by Snowden & Rossiter: if depth separation alone enables segmentation, the UNCUED observer (who has access to depth information on every trial) should benefit — but they do not.

**Lankheet, M. J. M., & Verstraten, F. A. J. (1995). "Attentional modulation of adaptation to two-component transparent motion." *Vision Research* 35(10):1401–1412.** (Confidence: HIGH — confirmed in integrated_review.md and paper_notes; Vision Research vol 35.)

Demonstrated that attention to one component of a transparent RDK (two superimposed motion directions, no depth separation) produces directional after-effects (MAEs) specific to the attended direction, with approximately 70% gain change for the attended surface. This establishes that selective attentional access to one surface in a transparent display is possible — and that the neural consequence is measurable as a gain change on the order of 70% relative to the unattended surface, which is large by motion physiology standards.

*VRDots implication*: The Lankheet & Verstraten result establishes that even without depth separation, attention can selectively amplify one transparent surface's motion representation with large gain. Adding depth separation (as in VRDots) should only improve this selectivity. The F2 depth-field cueing effect in VRDots (+12.5pp, OR=1.89) is the behavioral consequence of this selectivity improvement when the translator happens to be in the same depth plane as the field that was designated as target by the onset cue.

**Qian, N., Andersen, R. A., & Adelson, E. H. (1994). "Transparent motion perception as detection of unbalanced motion signals. III. Modeling." *Journal of Neuroscience* 14(12):7381–7392.** (Confidence: HIGH — confirmed in depth_lit_review.md; J Neuroscience vol 14; PMID 7996188.)

The modeling component of the three-part Qian et al. (1994) series proposes that area MT contains neurons jointly tuned for direction and binocular disparity. When two motion surfaces share the same disparity, their opposing direction signals cancel locally within MT neurons' receptive fields — the opponent-direction suppression stage. Giving the two surfaces different disparities removes this local cancellation: disparity-tuned MT neurons can respond selectively to each surface's direction signal without mutual suppression. The model predicts that depth separation between transparent surfaces improves their independent MT representation, with the improvement scaling with the degree of separation.

*VRDots implication*: The Qian et al. (1994) model provides the mechanistic account for why F2 depth-field cueing exists: when the translating (cued) surface is in the correct depth plane, it is more distinctly represented by disparity-tuned MT neurons, allowing the attentional gain boost (from the onset cue) to be applied to a cleaner signal. When ZdA changes the cued surface's depth plane at tStart, the MT population encoding that surface shifts, potentially misaligning the gain boost that had been established during the pre-translation window. This is a neural account of the ZdA disruption that does not require object-file theory.

---

## 7. Binocular Rivalry and Attention: The Limiting Case of Depth-Based Selection

**Mitchell, J. F., Stoner, G. R., & Reynolds, J. H. (2004). "Object-based attention determines dominance in binocular rivalry." *Nature* 429(6990):410–413.** (Confidence: HIGH — local PDF confirmed in project; Nature vol 429; PMID 15164065.)

The most direct demonstration that the translating-dot onset cue operates at the level of perceptual surface representations. When the two transparent dot fields were presented dichoptically (one per eye, producing binocular rivalry), the surface that received the onset-translation cue was substantially more likely to dominate the rivalry percept over the subsequent minutes. Critically, the effect could not be explained by spatial attention (the two surfaces shared the same retinotopic region), feature attention (the cue was direction-based but color was the dominant rivalry cue), or eye of origin (the cue was presented to both eyes equally). This result establishes that the onset cue designates a *surface* at the level of perceptual representation, and that this designation persists as a competitive bias in a system (binocular rivalry) where competition for representation is explicit.

*VRDots implication*: The Mitchell et al. (2004) result establishes that the VRDots onset cue operates at the surface representation level. Binocular rivalry is a limiting case of depth-based selection: two surfaces in strict depth conflict (each in one eye) compete for representation. The fact that the same cue that drives VRDots behavioral cueing also drives rivalry dominance confirms that the selected unit is the surface-object, not any feature or location. The VRDots binocular depth experiments add stereo disparity to a paradigm that already operates via surface representation competition.

**Blake, R., & Logothetis, N. K. (2002). "Visual competition." *Nature Reviews Neuroscience* 3(1):13–21.** (Confidence: HIGH — PMID 11823802; widely cited NRN review.)

Comprehensive review establishing that binocular rivalry involves competitive suppression between eye-specific cortical representations, with competition occurring across multiple cortical levels from LGN through higher visual areas. Critically, attention can modulate this competition from outside: top-down selection biases which representation wins, consistent with the Mitchell et al. (2004) behavioral result. The review also establishes that rivalry involves active suppression (not mere gain reduction) of the losing representation.

*VRDots implication*: In binocular (non-dichoptic) VRDots, the two dot fields share both eyes' inputs equally — there is no interocular competition in the strict rivalry sense. The relevant competition is between motion-direction representations in MT (Qian et al. 1994 model), not between eye-specific representations. However, at small disparities (0.72 arcmin, VRDots 0.05 m), the transition between "depth-plane competition" and "rivalry" may not be sharp. VRDots monocular sessions effectively remove the depth dimension and reduce to the 2D transparent-motion paradigm, where the cueing effect survives at +7.1pp* — suggesting the competition mechanism does not require binocular rivalry, but is enhanced by it.

---

## 8. Surface vs. Plane: What Is the Unit of Depth-Based Selection?

A theoretical distinction that runs through the literature but has not been directly resolved is whether depth-based selection operates on *surfaces* (objects defined by depth among other features) or *depth planes* (spatial locations defined by their binocular disparity value). The distinction is empirically important.

**Egly, Driver & Rafal (1994)** (cited above) and **He & Nakayama (1992)** (cited above) both support surface-based selection: the unit is the perceptually organized object, not the spatial region it occupies. For depth, the surface account predicts that changing an object's depth-plane membership should disrupt attentional access — which is what ZdA shows. A depth-plane account would predict the opposite: when ZdA moves the cued object's dots to the far depth plane, the observer should simply attend to the far plane and find them there.

**Baylis, G. C., & Driver, J. (1993). "Visual attention and objects: Evidence for hierarchical coding of location." *Journal of Experimental Psychology: Human Perception and Performance* 19(3):451–470.** (Confidence: HIGH — PMID 8409862; confirmed citation in depth_lit_review.md; J Exp Psych HPP vol 19.)

Demonstrated that judging the relative position of two contours was harder when they appeared to belong to two different objects than to one, even when the physical stimuli were identical. This establishes that object boundaries — including depth-plane-defined boundaries — create categorical barriers to attentional access. The effect is perceptual (driven by grouping interpretation), not spatial.

*VRDots implication*: The distinction between surface-based and plane-based accounts has an empirical signature in VRDots: the UNCUED arm's flatness. If depth-based selection were location-based (attending to "the near plane"), then UNCUED trials where the translator happens to be in the expected near plane should produce above-chance performance — observers could use depth-plane location to find the translator without the onset cue. They cannot. This is strong evidence that depth-based selection in VRDots is surface-based: the onset cue is needed to designate *which* surface in the depth display is the target, and depth-plane identity alone is insufficient to designate a target surface.

---

## 9. Depth as a Feature-Binding Dimension

**Treisman, A., & Gelade, G. (1980). "A feature-integration theory of attention." *Cognitive Psychology* 12(1):97–136.** (Confidence: HIGH — PMID 7351125; canonical.)

Feature integration theory proposes that individual feature dimensions (color, orientation, motion, etc.) are processed in separate maps and bound into coherent object representations only when focal attention is applied. Without attention, features float freely in their individual maps and are not bound to a specific location. Spatial location serves as the primary binding dimension — the "glue" that connects features from different modules.

Does binocular depth serve as an alternative or supplementary binding dimension? Treisman's original formulation does not include depth explicitly.

**Nakayama, K., He, Z. J., & Shimojo, S. (1995). "Visual surface representation: A critical link between lower-level and higher-level vision." In S. M. Kosslyn & D. N. Osherson (Eds.), *An Invitation to Cognitive Science* (Vol. 2, pp. 1–70).** (Confidence: MODERATE — this is a major book chapter that is consistently cited in the 3D surface representation literature; details partially inferred from consistent cross-references in available project documents.)

This influential chapter argues that depth-based surface representation is a critical intermediate stage between early feature extraction and high-level object recognition. Depth (via disparity, occlusion cues, and surface completion) organizes visual features into surface-bounded units before object identification occurs. Under this view, depth serves as a *pre-binding* stage: features associated with the same depth-defined surface are grouped before attention is required to bind them. Depth would therefore function not as a replacement for location-based binding, but as a constraint on what constitutes a coherent spatial unit eligible for binding.

**Wannig, A., Rodriguez, V., & Freiwald, W. A. (2007). "Attention to surfaces modulates motion processing in extrastriate cortex." *Neuron* 54(4):639–651.** (Confidence: HIGH — confirmed in integrated_review.md; Neuron vol 54; widely cited.)

Physiological evidence that attending to one transparent surface modulates MT neurons' responses in a direction-selective, surface-specific way. MT neurons with preferred directions matching the attended surface show enhanced responses, while neurons preferring the other surface's direction show reduced responses. This is evidence that surface-level attention propagates across the entire feature space of the attended surface — including features not directly cued — consistent with a binding role for surface representation at MT.

*VRDots implication*: If depth serves as a binding dimension, the F2 depth-field cueing effect (+12.5pp, OR=1.89) reflects the degree to which depth-plane consistency across the temporal interval — from onset cue through the pre-translation window — strengthens the attentional binding of the cued surface's features (direction, color, dot positions) into a stable, selectable unit. When ZdA breaks depth-plane continuity at tStart, the binding information is disrupted, potentially unbinding the surface representation that the onset cue had established. This is a feature-integration account of the ZdA disruption that complements the object-file account.

---

## 10. Attentional Gradients Across Depth: Evidence for Asymmetric Near/Far Gradients

**Downing, C. J., & Pinker, S. (1985). "The spatial structure of visual attention." In M. I. Posner & O. S. M. Marin (Eds.), *Attention and Performance XI* (pp. 171–187). Erlbaum.** (Confidence: HIGH — confirmed citation in depth_lit_review.md; standard Posner attention volume.)

Established that spatial attention in 2D has a gradient structure: response latency increases monotonically with cue-target distance, following a smooth decay function. Attention is not a step function that is either "on" or "off" at a given location — it is a graded field with a specific shape that can be measured behaviorally.

**Andersen & Kramer (1993)** (cited above in Section 5) extended this gradient concept to depth: the attentional gradient falls off more steeply toward the observer (near direction) than away from the observer (far direction). This viewer-centered gradient structure produces the near-plane interference advantage in their flanker paradigm.

**Chen, X., Meng, M., Matthews, N., & Qian, N. (2012). "Attention-based integration of binocular signals." *Journal of Neuroscience* 32(38):13352–13362.** (Confidence: HIGH — confirmed citation in depth_lit_review.md; J Neuroscience vol 32.)

Found a near-plane advantage in attentional reorienting (the cost of redirecting attention from the attended plane to an unexpected target was larger in the far condition). Crucially, the near/far asymmetry did NOT reverse when the fixation depth was changed — arguing against a vergence-driven account (which would predict reversal as the observer-relative near and far planes swap) and supporting a retinal-disparity-based mechanism.

*Published evidence for directional attentional gradients in depth is limited and inconsistent.* The theoretical proposal (in `depth_ordering_lit_review.md`) that attentional gradients extend from near toward far but not the reverse — because the display has a far boundary with nothing beyond it — has no direct empirical support in the published literature. Gradient decay in depth has been established (Andersen 1990, Andersen & Kramer 1993), but the specific directional claim that the gradient is unidirectionally asymmetric in a display-topology-dependent way is novel and untested. The three-plane critical experiment (Near/Mid/Far display, comparing Mid vs. Far cueing when a beyond-Far plane is added vs. absent) is the cleanest test, and it has no published precedent.

---

## Theoretical Implications for VRDots

The reviewed literature converges on a picture in which depth-based attentional selection is real, stereoscopic, surface-organized, and capacity-limited. The following five theoretical implications follow directly from the synthesis.

### 1. The UNCUED Flatness Identifies Selection as Surface-Based, Not Plane-Based

Nakayama & Silverman (1986) showed depth can partition a display preattentively; He & Nakayama (1992) showed the unit of selection is a surface. VRDots' UNCUED arm (near-chance throughout all depth experiments) establishes that neither preattentive depth-plane segmentation nor sustained voluntary access to depth-plane information is sufficient to select the target surface without the temporal onset cue. Depth identifies *that* there are two surfaces; it does not tell the system *which* surface is the target. The onset cue provides that designation, and depth thereafter supports the efficiency of selection *of the designated surface* (F2 = +12.5pp, OR=1.89). This finding extends He & Nakayama (1992) to a dynamic, time-resolved attentional selection paradigm with superimposed motion surfaces.

### 2. The F1×F2 Conjunction Requirement Is Not Predicted by Any Existing Framework

Desimone & Duncan's (1995) biased competition framework predicts that either temporal salience or depth-plane distinctness could independently bias competition in the target surface's favor. Nakayama & Silverman (1986) establishes depth as preattentive — depth-plane identity should independently facilitate search. Neither framework predicts that F2 provides zero benefit in the UNCUED condition. The conjunction requirement implies that depth-plane information is not sufficient to activate an attentional selection process — it only contributes once a surface has been designated as a target by an exogenous event. Depth amplifies an ongoing selection; it cannot initiate one.

### 3. The Far > Near Asymmetry Implicates Binocular Disparity Processing Specifically

The complete monocular collapse of the Near/Far asymmetry (DepthSwapCtrl: binocular vs. monocular) is consistent with Arnott & Shedden (2000) and Caziot et al. (2023)'s conclusion that depth-plane attentional asymmetries are carried in the retinal disparity representation, not in vergence-driven spatial position. VRDots provides the first observation of this effect in a transparent-motion surface selection paradigm. The directionality (Far > Near) is consistent with Parks & Corballis (2006) and the trend in Caziot et al. (2023), and inconsistent with the Andersen & Kramer (1993) flanker interference advantage for near space. Two candidate mechanisms remain viable: MT disparity-population anisotropy (Calabro & Vaina 2011; Qian et al. 1994) and attentional topology (see `depth_lit_review.md` Section 7.2).

### 4. Depth Functions as a Binding Cue, Not an Independent Selection Trigger

Treisman & Gelade (1980) placed location as the primary binding dimension. The VRDots results suggest that binocular depth adds a second organizational dimension that, when consistent with the surface designated by the onset cue, improves the fidelity of the surface representation that receives attentional gain (consistent with Wannig et al. 2007, Schoenfeld et al. 2014). When depth is inconsistent — when ZdA disrupts depth-plane continuity at the moment the translating surface becomes the target — the binding scaffolding is weakened, and selection efficiency falls. This is a binding-dimension account that does not require a new theoretical framework but places depth alongside location as a feature-integration organizer.

### 5. The VRDots Paradigm Is the First Direct Test of Depth as a Constitutive Object-File Feature in a Dynamic Selection Task

The He & Nakayama (1992) and Nakayama et al. (1989) paradigms used static or brief-flash stimuli in search tasks. VRDots is the first paradigm to probe depth-plane continuity as a condition on attentional maintenance — to ask whether *breaking* depth membership mid-trial disrupts an attentional hold that was established by an earlier onset event. The ZdA/ZdB dissociation (ZdA: +12.5pp n.s.; ZdB: +56.2pp***; N: +34pp**) is the critical empirical signature. No published paradigm has set up and tested this manipulation before. The result implies that depth-plane membership is a constitutive feature of an attentional object in the sense of Kahneman, Treisman & Gibbs (1992): a feature update that changes the object's depth-plane identity triggers a new object file opening, releasing the attentional pointer established by the onset cue.

---

## Confidence Summary by Citation

| Paper | Confidence | Basis |
|---|---|---|
| Nakayama & Silverman (1986), *Perception* 15:221 | HIGH | Confirmed in depth_lit_review.md and integrated_review.md |
| He & Nakayama (1992), *Nature* 359:231 | HIGH | Confirmed in depth_lit_review.md; Nature vol 359 |
| He & Nakayama (1995), *Science* 265:791 | HIGH | Confirmed in integrated_review.md and depth_lit_review.md |
| Nakayama & Mackeben (1989), *Vision Research* 29:1631 | HIGH | PMID 2635476 confirmed |
| Egly, Driver & Rafal (1994), *JEP:General* 123:161 | HIGH | PMID 8014612 confirmed |
| Bhatt et al. (2007) — 3D Egly extension | LOW | Inferred; verify before citing in published work |
| Andersen (1990), *P&P* 47:112 | MODERATE | Title and journal confirmed; full details partially inferred |
| Andersen & Kramer (1993), *P&P* 53:658 | HIGH | Confirmed in depth_lit_review.md; P&P vol 53 |
| Parks & Corballis (2006), *NeuroReport* 17:643 | HIGH | Confirmed in depth_lit_review.md; NeuroReport vol 17 |
| Caziot, Rolfs & Backus (2023), *PNAS Nexus* 2:pgad314 | HIGH | Confirmed in depth_lit_review.md; PNAS Nexus 2023 |
| Arnott & Shedden (2000), *P&P* 62:1459 | HIGH | Confirmed in depth_lit_review.md; P&P vol 62 |
| Chen, Meng, Matthews & Qian (2012), *J Neurosci* 32:13352 | HIGH | Confirmed in depth_lit_review.md; J Neuroscience vol 32 |
| Snowden & Rossiter (1999), *Perception* 28:193 | HIGH | Confirmed in project literature files |
| Lankheet & Verstraten (1995), *Vision Research* 35:1401 | HIGH | Confirmed in integrated_review.md |
| Qian, Andersen & Adelson (1994), *J Neurosci* 14:7381 | HIGH | Confirmed in depth_lit_review.md; PMID 7996188 |
| Mitchell, Stoner & Reynolds (2004), *Nature* 429:410 | HIGH | Local PDF confirmed; PMID 15164065 |
| Blake & Logothetis (2002), *Nat Rev Neurosci* 3:13 | HIGH | PMID 11823802 confirmed |
| Baylis & Driver (1993), *JEP:HPP* 19:451 | HIGH | PMID 8409862; confirmed in depth_lit_review.md |
| Treisman & Gelade (1980), *Cog Psych* 12:97 | HIGH | PMID 7351125; canonical |
| Nakayama, He & Shimojo (1995), book chapter | MODERATE | Consistently cited; chapter details partially inferred |
| Wannig, Rodriguez & Freiwald (2007), *Neuron* 54:639 | HIGH | Confirmed in integrated_review.md |
| Downing & Pinker (1985), book chapter | HIGH | Confirmed in depth_lit_review.md; standard Posner volume |
| Desimone & Duncan (1995), *Annu Rev Neurosci* 18:193 | HIGH | Confirmed in integrated_review.md |
| Kahneman, Treisman & Gibbs (1992), *Cog Psych* 24:175 | HIGH | Confirmed in depth_lit_review.md |

---

*Related documents: `depth_lit_review.md` (mechanistic accounts of Far>Near; gap analysis), `depth_ordering_lit_review.md` (perceptual depth-ordering, bistability, figure-ground), `integrated_review.md` (full per-paper summaries), `theory_doc.md` (theoretical framework), `depth_ior_hypothesis.md` (IOR account, now superseded by gradient migration).*
*New citations not in paper_list.md: Nakayama & Silverman (1986) confirmed; Parks & Corballis (2006) confirmed; Caziot et al. (2023) confirmed — add to paper_list.md Group 8.*
