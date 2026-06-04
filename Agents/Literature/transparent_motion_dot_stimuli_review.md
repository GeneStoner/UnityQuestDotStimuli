# Transparent Motion and Moving-Dot Stimuli as Probes of Visual Processing
*A brief scientific review with annotated reference list*
*Prepared 2026-05-19*

---

## Scientific Review

### 1. Random-Dot Stimuli: Stripping Vision Down to Essentials

Random-dot kinematograms (RDKs), introduced by Julesz (1971) and characterized by Braddick (1974), were designed to eliminate all monocular figural cues and force the visual system to construct percepts exclusively from spatiotemporal relationships among elements. A field of identically appearing dots — each ambiguous in isolation — carries no locally interpretable structure; meaning is generated only at the level of the ensemble. This design makes RDKs uniquely powerful probes: whatever the observer perceives must be constructed by integrating signals across space and time, not read off any single feature.

The system handles this remarkably well. Britten et al. (1992) showed that the primate visual area MT encodes directional coherence with sensitivity matching the psychophysical observer, and that trial-by-trial fluctuations in MT firing predict perceptual choices — demonstrating a direct link between population-level neural activity and conscious motion percepts. Lesions of MT dramatically elevate coherence thresholds (Newsome & Paré, 1988), confirming the area as the critical site for local-to-global motion integration. This work established that a distributed neural computation — not a local feature detector — underlies even the simplest perceptual decision about a dot field.

### 2. Two Surfaces at the Same Retinal Location

The most revealing manipulation is superposition: place two dot populations at the same spatial location, each moving in a different direction. Each local region of the retina receives input from both surfaces simultaneously, and neither surface has exclusive claim to any spatial position. Yet human observers, under appropriate conditions, perceive two distinct coherent surfaces sliding through each other — a phenomenon known as *transparent motion* (Adelson & Movshon, 1982; Nakayama & Silverman, 1988).

This percept demands that the visual system solve a combinatorial problem: it must partition interleaved signals into mutually exclusive surface representations and impose a coherent velocity estimate on each. Qian et al. (1994) showed that the system fails when opposing motion signals are perfectly spatially balanced (no local predominance), producing a non-transparent flicker — revealing that segmentation depends on spatial inhomogeneity in directional signals. Snowden et al. (1991) demonstrated that MT neurons are suppressed when two directions are simultaneously present in their receptive field, providing a physiological mechanism: opponent-direction inhibition within MT resolves the transparency decision and segregates surface representations in population activity.

The rules governing which signals are grouped together are not purely motional. Stoner, Albright & Ramachandran (1990) and Stoner & Albright (1992, 1993) showed that the *interpretation* of motion — coherent vs. transparent — is controlled by luminance relationships that the visual system treats as evidence for occlusion or physical transparency. When the intersecting regions of two overlapping gratings have luminances consistent with a transparent material, the surfaces slide apart perceptually; when the same luminance values are inconsistent with transparency, the gratings cohere into a single surface. The visual system's motion computations are thus not informationally encapsulated: surface-level inference actively gates low-level motion integration, challenging strict modularity in visual processing.

### 3. Objects from Patterns: Gestalt and the Law of Common Fate

The classic Gestalt principle of *common fate* (Wertheimer, 1923) holds that elements sharing the same direction and speed of motion group perceptually into a single object or surface. Random-dot transparent motion is this principle made extreme: shared motion trajectory is the *only* basis for grouping, since the dots are individually identical, randomly positioned, and intermixed across surfaces. The visual system succeeds nonetheless, demonstrating that common fate operates as a powerful, low-threshold grouping mechanism.

Johansson's (1973) point-light biological motion displays extend this principle to hierarchical structure: twelve dots attached to human joints, filmed in darkness, immediately and unambiguously yield the percept of a walking person. The local motion of each dot contributes simultaneously to multiple levels of structure (limb rotation, body translation, whole-figure locomotion), and the visual system performs an implicit vector decomposition to recover all levels in parallel. No static frame contains any recognizable shape. The percept arises entirely from the spatiotemporal pattern — a further demonstration that the visual system can construct complex, meaningful objects from moving dots when no static form information is available (Blake & Shiffrar, 2007).

### 4. Component-Invariant Object Identity: Surviving What Changes

A profound feature of visual object representations is their resistance to change in the components that constitute them. Kahneman, Treisman & Gibbs (1992) proposed the *object-file* framework: the visual system maintains temporary episodic representations (object files) linked to persisting objects via spatiotemporal continuity. Feature information is retrieved from, and written into, these files. The critical implication for dot stimuli is that the identity of a surface — as tracked by the object-file system — is anchored to the spatiotemporal envelope of the object, not to the specific elements currently occupying it. Pylyshyn & Storm (1988) demonstrated that observers can track up to five independently moving identical objects purely by spatiotemporal indexing (FINST theory), without any feature information to distinguish them. Scholl & Pylyshyn (1999) showed that tracking survives occlusion but not deletion/onset, confirming that the continuity criterion is spatiotemporal rather than featural.

In the transparent-motion paradigm this is made experimentally tractable by introducing *feature swaps*. Stoner & Blanc (2010) showed that when the color or motion direction of the two superimposed surfaces is exchanged mid-trial, attentional cueing effects follow the physical dot population — the tracked object — rather than the feature label. An observer cued to the "red" surface before the swap continues to attend the surface that was red (even after it becomes green), because the object file, indexed by dot identity and spatiotemporal continuity, survives the feature change. This is among the cleanest demonstrations in the literature that the *unit of attentional selection is an object defined by physical continuity*, not by any fixed feature or location.

### 5. Object-Based Attention: Selecting Surfaces, Not Locations

Transparent motion allows spatial attention theory to be directly challenged: two surfaces occupy the same space, so spatial attention cannot in principle select one without also engaging the other. Valdes-Sosa, Cobo & Pinilla (1998, 2000) introduced the delayed-onset paradigm in which one surface briefly translates (the cue event) before the response judgment; observers showed a robust accuracy advantage for the translating surface, demonstrating surface-level — not location-level — attentional selection. The cross-surface switching cost (~500 ms) reported by Valdes-Sosa et al. (2000) is consistent with the time required to disengage one object file and re-engage another, rather than to shift a spatial spotlight.

The neural substrate of this competition is provided by the biased-competition framework (Desimone & Duncan, 1995). When multiple stimuli fall within a neuron's receptive field, their representations mutually suppress each other. Top-down signals — or bottom-up salient events such as a surface onset — bias the competition in favor of one stimulus. Moran & Desimone (1985) first demonstrated this competitive gating physiologically in V4/IT; Reynolds, Chelazzi & Desimone (1999) confirmed the mechanism in V2 and V4 with quantitative predictions about response magnitude under competition. In the transparent-motion context, the two surfaces are the competing stimuli, and the onset cue biases competition in favor of the cued surface across the entire population of neurons representing that region of visual space — explaining why the benefit generalizes across all features of the attended surface.

Catak et al. (2022) extended these findings electrophysiologically, showing that N1 ERP components are modulated by cueing in transparent-motion paradigms even when motion or color is swapped mid-trial, ruling out feature-based explanations and confirming that the attentional enhancement tracks the object rather than the feature.

### 6. Broader Significance and Limitations

Moving-dot stimuli expose the visual system's solutions to four fundamental computational problems simultaneously: (i) local motion integration into global velocity estimates, (ii) signal segmentation at motion boundaries, (iii) surface segmentation when boundaries are absent and populations overlap spatially, and (iv) object identity maintenance through feature change. No static stimulus addresses all four. The transparent-motion paradigm specifically dissociates spatial from object-based selection — impossible with non-overlapping stimuli — while the deliberate replacement of dots provides a controlled manipulation of component-identity continuity.

Limitations are also informative. Qian et al.'s (1994) demonstration that perfectly balanced opposing signals destroy transparency shows that surface perception is not a matter of detecting two directions but of detecting *spatially coherent* directional subsets — the visual system's segmentation mechanism has a specific signature. The aperture problem literature (Adelson & Movshon, 1982; Nakayama & Silverman, 1988) shows that local motion measurements are inherently ambiguous, and the system's resolution of that ambiguity via surface-level grouping is a principled computational choice with measurable failure modes.

Together, these properties make transparent motion dot stimuli among the most informative tools available for probing the architecture of object-based visual processing.

---

## Bullet-Point Summary with References

### Random-dot kinematograms as visual probes
- Julesz (1971) introduced random-dot stimuli to eliminate monocular figural cues; any percept must be built from spatiotemporal integration across elements — nothing is interpretable locally.
- Braddick (1974) characterized the short-range motion process using RDKs, showing that coherent motion is detected within a defined displacement range and is monocular, implicating early cortical processing.
- Newsome & Paré (1988) showed MT lesions selectively elevate RDK coherence thresholds, establishing MT as the neural locus for global motion integration from dot fields.
- Britten et al. (1992, 1993) demonstrated that individual MT neurons approach psychophysical threshold on RDK direction discrimination; trial-by-trial fluctuations in MT firing predict behavioral choices (choice probability > 0.5), causally linking MT activity to motion percepts.

### Transparent motion: two surfaces at one retinal location
- Adelson & Movshon (1982) showed that two superimposed gratings are perceived as a single coherent surface or two transparent sliding surfaces depending on low-level cues — the first systematic study of motion transparency.
- Stoner, Albright & Ramachandran (1990) demonstrated that perceived luminance relationships consistent with physical transparency (X-junctions) cause surfaces to be seen as transparent, linking perceptual inference about surface properties to motion segmentation.
- Stoner & Albright (1992, 1993) extended this to MT physiology: neural responses tracked perceptual interpretation (coherent vs. transparent), showing that surface-level inference gates motion integration — challenging strict modularity.
- Nakayama & Silverman (1988) showed how motion ambiguity at boundaries is resolved by spatial integration, laying groundwork for understanding how competing motion signals at the same location are partitioned into surfaces.
- Qian, Andersen & Adelson (1994) showed that perfectly spatially balanced opposing motions destroy the transparency percept, revealing that the visual system segments surfaces by detecting *local dominance* of a directional signal, not merely the presence of two directions.
- Snowden et al. (1991) demonstrated that MT neurons are suppressed when two directions co-occur in their receptive field — opponent-direction inhibition provides the neural mechanism for motion surface segmentation.

### Gestalt grouping: common fate and object formation from motion
- Wertheimer (1923) formulated the law of common fate: elements with the same motion trajectory group into a single perceptual unit. RDK transparent motion is this principle's limiting case — motion is the *only* available grouping cue.
- Wagemans et al. (2012) review confirms common fate as a robust, quantifiable grouping mechanism with measurable neural correlates.
- Johansson (1973) showed that 10–12 dots attached to human joints, filmed in darkness, immediately yield the percept of a walking person — demonstrating that the visual system constructs complex, hierarchically structured objects from moving dots alone, with no static form information.
- Blake & Shiffrar (2007) review shows biological motion perception implicates STS and dual form/motion pathways, extending common-fate object formation to the level of person and action recognition.

### Object identity surviving component replacement
- Kahneman, Treisman & Gibbs (1992) proposed the *object-file* framework: episodic representations linked to persisting spatiotemporal objects accumulate feature information; the file, not the feature, is the unit of selection. Identity survives feature change as long as spatiotemporal continuity is maintained.
- Pylyshyn & Storm (1988) showed observers can track 4–5 of 10 identical moving objects without feature information (FINST theory), confirming pre-attentive spatiotemporal indexing independent of feature identity.
- Scholl & Pylyshyn (1999) showed tracking survives occlusion but not sudden deletion/onset — the continuity criterion is spatiotemporal, not featural, establishing the mechanism by which dot-identity survives surface-level manipulations.
- Noles, Scholl & Mitroff (2005) showed object files persist through interruptions for several hundred milliseconds before decaying — quantifying the temporal window within which component changes are tolerated without destroying identity.
- Mitroff, Scholl & Wynn (2004) showed that when a tracked object splits, one inheritor inherits the original file (the trajectory-continuous one), demonstrating that object identity is governed by spatiotemporal trajectory even during structural change.

### Object-based attention in transparent motion
- Valdes-Sosa, Cobo & Pinilla (1998) introduced the transparent-motion cueing paradigm: a translating surface (cue) improved direction discrimination on the *same surface*, with no location-based explanation possible since both surfaces occupy the same space.
- Valdes-Sosa, Cobo & Pinilla (2000) showed cross-surface attention switching costs ~500 ms, consistent with object-file disengagement rather than spatial spotlight movement.
- Reynolds, Alborzian & Stoner (2003) confirmed exogenous cueing by a single surface translation is sufficient for robust object-based attentional selection.
- Stoner & Blanc (2010) showed that feature swaps (exchanging the color or motion direction of the two surfaces mid-trial) do not disrupt attention: the effect follows the physical dot population (the object file), not the feature label — definitively ruling out feature-based attention as the mechanism.
- Catak et al. (2022) extended findings to ERP: N1 components are modulated by cueing even after feature swaps, confirming that neural attentional enhancement tracks the object rather than the feature, and directly linking behavioral and neural levels of analysis.
- Mitchell, Stoner & Reynolds (2004, *Nature*) demonstrated the same object-based selection mechanism in binocular rivalry: attentional cueing of one perceptual object — defined by coherent motion — biased rivalry dominance in its favor, showing the principle generalizes from transparent-motion to interocular competition.

### Neural mechanisms: biased competition
- Moran & Desimone (1985) demonstrated competitive gating in V4/IT: when two stimuli competed within a receptive field, the unattended stimulus was suppressed — the first physiological evidence for object-level competitive selection.
- Desimone & Duncan (1995) synthesized this into the biased-competition framework: multiple stimuli mutually suppress each other in RF-overlapping neurons; attention biases this competition by boosting the selected stimulus' drive. This replaces the spatial spotlight with an emergent population-level selection, applicable to object-based selection when surfaces overlap spatially.
- Reynolds, Chelazzi & Desimone (1999) confirmed the biased-competition mechanism in V2 and V4 with quantitative predictions: response under competition is intermediate between the two stimuli presented alone, and attention shifts it toward the attended-alone response.
- Duncan (1984) provided the behavioral foundation: dual-task costs within a single object are near zero; across objects they are large — the original demonstration that selection operates on objects rather than spatial locations.

### Limitations and diagnostic uses
- The coherence threshold (Newsome & Paré, 1988; Britten et al., 1992) is a sensitive assay of motion area function: psychophysical elevation of threshold can localize processing deficits to MT-level integration rather than earlier (contrast sensitivity) or later (decision) stages.
- The transparency breakdown under balanced opposing signals (Qian et al., 1994) reveals that surface segmentation relies on detecting local directional dominance — a specific computational signature with diagnostic value for understanding segmentation failures.
- The feature-swap manipulation (Stoner & Blanc, 2010; Catak et al., 2022) provides a direct behavioral dissociation between feature-based and object-based attention: any manipulation that drives the attentional effect to follow features rather than dot identity would constitute evidence against object files and for feature-based selection.
- The aperture problem literature (Adelson & Movshon, 1982; Nakayama & Silverman, 1988) shows that the same dots that define coherent surfaces create fundamentally ambiguous local signals; the visual system's resolution of this ambiguity is principled but subject to specific failure modes (plaid coherence vs. transparency), making transparent motion a precise tool for mapping the boundaries of surface-level inference.

---

## References

Adelson, E.H. & Movshon, J.A. (1982). Phenomenal coherence of moving visual patterns. *Nature*, 300, 523–525.

Blake, R. & Shiffrar, M. (2007). Perception of human motion. *Annual Review of Psychology*, 58, 47–73.

Braddick, O.J. (1974). A short-range process in apparent motion. *Vision Research*, 14, 519–527.

Britten, K.H., Shadlen, M.N., Newsome, W.T. & Movshon, J.A. (1992). The analysis of visual motion: a comparison of neuronal and psychophysical performance. *Journal of Neuroscience*, 12, 4745–4767.

Britten, K.H., Newsome, W.T., Shadlen, M.N., Celebrini, S. & Movshon, J.A. (1996). A relationship between behavioral choice and the visual responses of neurons in macaque MT. *Visual Neuroscience*, 13, 87–100.

Catak, E.N., Özkan, M., Kafaligonul, H. & Stoner, G.R. (2022). Behavioral and ERP evidence that object-based attention utilizes fine-grained spatial mechanisms. *Cortex*, 151, 89–104.

Desimone, R. & Duncan, J. (1995). Neural mechanisms of selective visual attention. *Annual Review of Neuroscience*, 18, 193–222.

Duncan, J. (1984). Selective attention and the organization of visual information. *Journal of Experimental Psychology: General*, 113, 501–517.

Johansson, G. (1973). Visual perception of biological motion and a model for its analysis. *Perception & Psychophysics*, 14, 201–211.

Julesz, B. (1971). *Foundations of Cyclopean Perception.* MIT Press.

Kahneman, D. & Treisman, A. (1984). Changing views of attention and automaticity. In R. Parasuraman & D.R. Davies (Eds.), *Varieties of Attention* (pp. 29–61). Academic Press.

Kahneman, D., Treisman, A. & Gibbs, B.J. (1992). The reviewing of object files: object-specific integration of information. *Cognitive Psychology*, 24, 175–219.

Mitroff, S.R., Scholl, B.J. & Wynn, K. (2004). Divide and conquer: how object files adapt when a persisting object splits into two. *Psychological Science*, 15, 420–425.

Mitchell, J.F., Stoner, G.R. & Reynolds, J.H. (2004). Object-based attention determines dominance in binocular rivalry. *Nature*, 429, 410–413.

Moran, J. & Desimone, R. (1985). Selective attention gates visual processing in the extrastriate cortex. *Science*, 229, 782–784.

Nakayama, K. & Silverman, G.H. (1988). The aperture problem — I & II. *Vision Research*, 28, 739–753.

Newsome, W.T. & Paré, E.B. (1988). A selective impairment of motion perception following lesions of MT. *Journal of Neuroscience*, 8, 2201–2211.

Noles, N.S., Scholl, B.J. & Mitroff, S.R. (2005). The persistence of object-file representations. *Perception & Psychophysics*, 67, 324–334.

Pylyshyn, Z.W. & Storm, R.W. (1988). Tracking multiple independent targets: evidence for a parallel tracking mechanism. *Spatial Vision*, 3, 179–197.

Qian, N., Andersen, R.A. & Adelson, E.H. (1994). Transparent motion perception as detection of unbalanced motion signals. *Journal of Neuroscience*, 14, 7357–7366.

Reynolds, J.H., Alborzian, S. & Stoner, G.R. (2003). Exogenously cued attention triggers competitive selection of surfaces. *Vision Research*, 43, 59–66.

Reynolds, J.H., Chelazzi, L. & Desimone, R. (1999). Competitive mechanisms subserve attention in macaque areas V2 and V4. *Journal of Neuroscience*, 19, 1736–1753.

Scholl, B.J. & Pylyshyn, Z.W. (1999). Tracking multiple items through occlusion: clues to visual objecthood. *Cognitive Psychology*, 38, 259–290.

Snowden, R.J., Treue, S., Erickson, R.G. & Andersen, R.A. (1991). The response of area MT and V1 neurons to transparent motion. *Journal of Neuroscience*, 11, 2768–2785.

Stoner, G.R. & Albright, T.D. (1992). Neural correlates of perceptual motion coherence. *Nature*, 358, 412–414.

Stoner, G.R. & Albright, T.D. (1993). Image segmentation cues in motion processing: implications for modularity. *Journal of Cognitive Neuroscience*, 5, 129–149.

Stoner, G.R., Albright, T.D. & Ramachandran, V.S. (1990). Transparency and coherence in human motion perception. *Nature*, 344, 153–155.

Stoner, G.R. & Blanc, C. (2010). Object-based attention in transparent motion. *Vision Research*, 50, 229–239.

Valdes-Sosa, M., Cobo, A. & Pinilla, T. (1998). Transparent motion and object-based attention. *Cognition*, 66, B13–B23.

Valdes-Sosa, M., Cobo, A. & Pinilla, T. (2000). Attention to object files defined by transparent motion. *Journal of Experimental Psychology: Human Perception and Performance*, 26, 488–505.

Wagemans, J., Elder, J.H., Kubovy, M., Palmer, S.E., Peterson, M.A., Singh, M. & von der Heydt, R. (2012). A century of Gestalt psychology in visual perception. *Psychological Bulletin*, 138, 1172–1217.

Wertheimer, M. (1923). Untersuchungen zur Lehre von der Gestalt. *Psychologische Forschung*, 4, 301–350.
