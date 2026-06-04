# Feature-Based Attention and Transparent Motion: A Mini Review
*Prepared 2026-05-26*

---

## Scientific Review

### Introduction

Transparent motion paradigms — two randomly intermixed dot populations moving in different directions, occupying the same spatial region — present the visual system with a fundamental selection problem. Early work established that attention in these displays is *object-based*: it selects entire coherent surfaces rather than spatial locations (Valdes-Sosa et al., 1998, 2000). But the question of *how* attention finds and latches onto a surface has prompted a parallel line of inquiry into the role of feature-based mechanisms. Can attending to a color or motion direction selectively boost an interleaved surface defined by that feature? Is object-based selection in transparent motion downstream of, or independent from, feature-based selection? The evidence reviewed here suggests the two mechanisms cooperate: feature-based attention provides the attentional handle that initiates surface selection, but the selection that results is object-level and persists beyond the feature that triggered it.

### Feature-Based Attention as a Global Gain Mechanism

Feature-based attention operates fundamentally differently from spatial attention: rather than enhancing a circumscribed region of the visual field, it modulates processing of a particular feature value (e.g., a motion direction or color) across the *entire* visual field simultaneously. Treue & Martinez-Trujillo (1999) demonstrated this in macaque area MT: directing a monkey's attention to a motion direction outside a neuron's receptive field produced multiplicative gain changes in that neuron, scaled by the similarity between the attended direction and the neuron's preferred direction — the *feature similarity gain model*. Saenz, Buracas & Boynton (2002, 2003) confirmed the same principle in human fMRI and psychophysics: attending to a color or direction at one location enhanced processing of spatially remote stimuli sharing that feature. Martinez-Trujillo & Treue (2004) extended the model further, showing that the population-level effect is not merely a gain boost but a sharpening: neurons tuned to the attended direction are enhanced while those tuned to the opposite direction are suppressed, increasing selectivity. Maunsell & Treue (2006) synthesized this literature into a framework in which spatial and feature-based attention operate in parallel, with multiplicative gains that combine at the level of individual neurons.

The relevance to transparent motion is direct: because feature-based attention spreads globally, attending to the color or direction of motion that defines one surface would, in principle, simultaneously boost all elements sharing that feature — which is exactly the dot population comprising that surface. Feature-based gain thus provides a plausible computational mechanism by which an interleaved surface could be selectively enhanced without any spatial selection at all.

### Color as an Attentional Handle for Surface Selection

The classic transparent motion paradigms of Valdes-Sosa, Bobes, Rodriguez & Pinilla (1998) used color to distinguish surfaces — observers attended to a "red" or "green" dot field — and demonstrated that attending to one surface suppressed P1 and N1 ERP responses to events on the other, even though both surfaces occupied the same spatial location. The behavioral analog (Valdes-Sosa et al., 1998, 2000) showed robust accuracy advantages for the cued surface and a ~500 ms switching cost for re-selecting the other surface. In both cases, color served as the attentional cue. Could the entire effect be explained by color-channel gain — boosting all red elements globally, for instance?

Fallah, Stoner & Reynolds (2007) showed in macaque V4 that competitive color selection operates when two color-defined surfaces overlap in a neuron's receptive field: the attended color's representation is enhanced through biased competition. This would propagate color-selective gain to motion processing downstream in MT. Wannig, Rodriguez & Freiwald (2007) recorded directly from MT during transparent motion viewing and found that attending to one surface enhanced MT responses to that surface's motion — but crucially, this modulation persisted *even in conditions without differential color between the surfaces*, ruling out color-channel gain as the sole mechanism and implicating surface-level selection. Alais & Blake (1999) showed complementary psychophysical evidence using motion aftereffects: voluntarily attending to one motion direction in a transparent display selectively strengthened adaptation of that direction, confirming that attention boosts the attended surface's motion representation rather than just its color.

### Dissociating Feature-Based from Object-Based Selection

A decisive line of evidence comes from *feature-swap* experiments, which ask whether attention follows the feature label or the physical dot population when the two are put in conflict. Stoner & Blanc (2010) showed that when color and motion direction are exchanged between the two surfaces mid-trial, cueing effects follow the physical dot identity (the object file), not the feature. An observer cued to the "red, leftward" surface before the swap attends the surface that was red-and-leftward — now green-and-rightward — because spatiotemporal dot continuity defines the object, not the current feature values. Catak, Özkan, Kafaligonul & Stoner (2022) extended this to the neural level: N1 ERP enhancement tracked the physical surface through the feature swap, confirming that the neural attention signal is object-level rather than feature-level.

Khoe, Mitchell, Reynolds & Hillyard (2005) established the same point exogenously: early ERP modulations (C1 and N1) to probe events on the cued surface survived conditions in which both surfaces were the same color, ruling out color-channel gain as necessary. Ciaramitaro et al. (2011) found via fMRI that object-based surface attention propagates all the way back into V1 — an area with no known mechanism for color-based surface segmentation — consistent with feedback carrying a surface identity signal rather than a feature-based signal.

Blaser, Pylyshyn & Holcombe (2000) provided the most general demonstration: two spatially superimposed objects that were *identical in location* but differed in continuously varying feature trajectories could be independently tracked. Within-object dual-task costs were near zero; across-object costs were large, even though no spatial selection was possible. This "tracking through feature space" result establishes that the visual system maintains object-level representations that persist as features change — the mechanism underlying feature-swap immunity.

### The Cooperative Account

The preponderance of evidence favors a two-stage model. In the first stage, feature-based attention provides the initial handle: color or direction of motion preferentially boosts one interleaved population via the feature similarity gain mechanism (Treue & Martinez-Trujillo, 1999; Saenz et al., 2002). This gives surface selection a foothold. In the second stage, the visual system uses spatiotemporal coherence — the common-fate grouping of boosted elements — to construct or consolidate an object-level representation (the object file; Kahneman, Treisman & Gibbs, 1992), and attention then propagates across all features of that object. Stoner (2007) articulated this interactive view explicitly, noting that color operates as an attentional *handle* without determining the scope of selection: whatever is selected by color is selected as an object, not as a color.

This account explains why color facilitates but is not necessary for surface selection (Wannig et al., 2007; Khoe et al., 2005), why feature swaps do not disrupt cueing (Stoner & Blanc, 2010; Catak et al., 2022), and why the switching cost between surfaces (~500 ms; Valdes-Sosa et al., 2000) far exceeds what would be expected from a simple feature-channel reweighting. Feature-based attention bootstraps object-based selection; it does not replace it.

### Open Questions

It remains unclear whether motion direction itself — rather than color — can serve as the attentional handle in fully color-matched transparent displays, and whether the relative contributions of feature-based and object-based mechanisms vary with the number of surfaces, their feature separations, or the mode of attention (exogenous vs. endogenous). Felisberti & Zanker (2005) showed that voluntary attention to a motion direction gates which surface reaches conscious awareness in transparent motion, but whether this operates through feature-similarity gain or through a higher-level grouping mechanism is unresolved. These questions bear directly on the degree to which surface selection in VRDots-style paradigms can be explained by purely feature-based accounts.

---

## Bullet-Point Summary with References

### Feature-based attention as a global, feature-selective gain mechanism
- Treue & Martinez-Trujillo (1999): attending a motion direction outside a neuron's RF produces multiplicative gain in MT scaled by feature similarity — the feature similarity gain model; operates across the entire visual field.
- Saenz, Buracas & Boynton (2002): fMRI shows attending a direction or color at one location enhances cortical processing (including MT+) of the matching feature at remote, unattended locations.
- Saenz et al. (2003): psychophysical dual-task confirms global feature pooling; monitoring two stimuli sharing a feature is easier than monitoring two stimuli with different features.
- Martinez-Trujillo & Treue (2004): feature attention not only boosts preferred-direction neurons but suppresses opposite-direction neurons — sharpening the population direction tuning curve and increasing selectivity.
- Maunsell & Treue (2006): review synthesizing the location-independent nature of feature-based attention throughout visual cortex; spatial and feature attention combine multiplicatively.

### Color as an attentional handle in transparent motion
- Valdes-Sosa, Bobes et al. (1998): color-coded surfaces used; endogenous attention to one surface suppresses P1/N1 ERPs to the other — first neural evidence of surface-level selection in transparent motion, using color as the cue.
- Valdes-Sosa, Cobo & Pinilla (1998, 2000): behavioral paradigm; color-defined surface cueing yields robust accuracy advantage and ~500 ms cross-surface switching cost — far exceeding simple feature-channel reweighting.
- Fallah, Stoner & Reynolds (2007): macaque V4 neurons show competitive color-selective enhancement when two color-coded surfaces overlap in a receptive field — early color selection via biased competition feeds into downstream motion processing.
- Wannig, Rodriguez & Freiwald (2007): MT modulation by surface attention persists even without differential color between surfaces — color facilitates but is not necessary; underlying mechanism is surface-level.
- Alais & Blake (1999): selective voluntary attention to one motion direction in a transparent display strengthens the subsequent motion aftereffect for that direction — direct psychophysical evidence of direction-selective neural boosting of an attended surface.

### Dissociating feature-based from object-based selection
- Khoe, Mitchell, Reynolds & Hillyard (2005): exogenous cueing effects on C1 and N1 ERPs survive same-color condition — color-channel gain is not necessary; selection is surface-level.
- Stoner & Blanc (2010): feature swaps mid-trial (color and direction exchanged between surfaces) do not disrupt cueing — attention follows the physical dot population (the object file), not the feature label.
- Catak et al. (2022): N1 ERP tracks the attended surface through feature swaps — neural attention signal is object-level, not feature-level; also establishes fine spatial scale.
- Ciaramitaro et al. (2011): surface-based attention propagates to V1 in fMRI — feedback signal carries object identity, not a simple feature-channel gain that could originate in V1 itself.
- Blaser, Pylyshyn & Holcombe (2000): two spatially superimposed objects with continuously varying features can be independently tracked; within-object dual-task costs near zero, across-object costs large — objects, not features or locations, are the primary units of selection.

### The cooperative / two-stage account
- Stoner (2007, *Trends in Cognitive Sciences*): color operates as an attentional handle that initiates selection, but selection propagates to the whole object — feature-based and object-based mechanisms interact, not compete.
- Felisberti & Zanker (2005): voluntary attention to a motion direction selectively gates which transparent surface reaches conscious awareness — direction-based feature attention influences surface-level perception.
- Wannig et al. (2007): even color-matched surface attention modulates MT — feature handle is not required once object representation is activated.
- O'Craven, Downing & Kanwisher (1999): attending any attribute of an object (motion, shape, color) boosts the whole object representation in fMRI — feature-access triggers object-level selection.

---

## References

Alais, D. & Blake, R. (1999). Neural strength of visual attention gauged by motion adaptation. *Nature Neuroscience*, 2, 1015–1018.

Blaser, E., Pylyshyn, Z.W. & Holcombe, A.O. (2000). Tracking an object through feature space. *Nature*, 408, 196–199.

Catak, E.N., Özkan, M., Kafaligonul, H. & Stoner, G.R. (2022). Behavioral and ERP evidence that object-based attention utilizes fine-grained spatial mechanisms. *Cortex*, 151, 89–104.

Ciaramitaro, V.M., Mitchell, J.F., Stoner, G.R., Reynolds, J.H. & Boynton, G.M. (2011). Object-based attention to one of two superimposed surfaces alters responses in human early visual cortex. *Journal of Neurophysiology*, 105, 1258–1265.

Fallah, M., Stoner, G.R. & Reynolds, J.H. (2007). Stimulus-specific competitive selection in macaque extrastriate visual area V4. *Proceedings of the National Academy of Sciences*, 104, 4165–4169.

Kahneman, D., Treisman, A. & Gibbs, B.J. (1992). The reviewing of object files: object-specific integration of information. *Cognitive Psychology*, 24, 175–219.

Khoe, W., Mitchell, J.F., Reynolds, J.H. & Hillyard, S.A. (2005). Exogenous attentional selection of transparent superimposed surfaces modulates early event-related potentials. *Vision Research*, 45, 3004–3014.

Martinez-Trujillo, J.C. & Treue, S. (2004). Feature-based attention increases the selectivity of population responses in primate visual cortex. *Current Biology*, 14, 744–751.

Maunsell, J.H.R. & Treue, S. (2006). Feature-based attention in visual cortex. *Trends in Neurosciences*, 29, 317–322.

O'Craven, K.M., Downing, P.E. & Kanwisher, N. (1999). fMRI evidence for objects as the units of attentional selection. *Nature*, 401, 584–587.

Saenz, M., Buracas, G.T. & Boynton, G.M. (2002). Global effects of feature-based attention in human visual cortex. *Nature Neuroscience*, 5, 631–632.

Saenz, M., Buracas, G.T. & Boynton, G.M. (2003). Global feature-based attention for motion and color. *Vision Research*, 43, 629–637.

Felisberti, F.M. & Zanker, J.M. (2005). Attention modulates perception of transparent motion. *Vision Research*, 45, 2587–2599.

Stoner, G.R. (2007). Visual attention: of features and transparent surfaces. *Trends in Cognitive Sciences*, 11, 438–443.

Stoner, G.R. & Blanc, G. (2010). Exploring the mechanisms underlying surface-based stimulus selection. *Vision Research*, 50, 229–241.

Treue, S. & Martinez-Trujillo, J.C. (1999). Feature-based attention influences motion processing gain in macaque visual cortex. *Nature*, 399, 575–579.

Valdes-Sosa, M., Bobes, M.A., Rodriguez, V. & Pinilla, T. (1998). Switching attention without shifting the spotlight: object-based attentional modulation of brain potentials. *Journal of Cognitive Neuroscience*, 10, 137–151.

Valdes-Sosa, M., Cobo, A. & Pinilla, T. (1998). Transparent motion and object-based attention. *Cognition*, 66, B13–B23.

Valdes-Sosa, M., Cobo, A. & Pinilla, T. (2000). Attention to object files defined by transparent motion. *Journal of Experimental Psychology: Human Perception and Performance*, 26, 488–505.

Wannig, A., Rodriguez, V. & Freiwald, W.A. (2007). Attention to surfaces modulates motion processing in extrastriate area MT. *Neuron*, 54, 639–651.
