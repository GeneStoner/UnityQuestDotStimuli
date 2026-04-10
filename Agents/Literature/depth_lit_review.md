# Depth Experiments: Empirical Literature Review
*Literature Agent — 2026-04-04*
*Prepared for: VRDots depth experiments introduction*

---

## Overview

The VRDots depth experiments address a question that the existing transparent-motion literature has not directly tested: does stereoscopic depth-plane identity become a constitutive component of an attended surface representation, such that disrupting depth-plane continuity at the moment of target onset impairs attentional selection? The relevant empirical literature spans six areas: (1) object-based attention and depth-plane selection, (2) transparent motion perception and surface segregation, (3) disparity tuning in early visual cortex, (4) stereoscopic depth and motion grouping, (5) temporal onset cueing and object files, and (6) near/far attentional asymmetries. This review summarizes the key findings in each area, identifies the specific connection to VRDots, and closes with a gap analysis.

---

## 1. Object-Based Attention and Depth-Plane Selection

### Key Papers

**Nakayama & Silverman (1986)** — *Nature* 320:253
Demonstrated that binocular disparity supports efficient (parallel) visual search when targets are defined by a conjunction of color and depth: observers appear to partition 3D space into depth planes and search each plane rapidly in turn, converting a conjunctive search into an effectively serial-by-plane but parallel-within-plane process. This was among the earliest demonstrations that depth is a preattentive dimension — one that can define a perceptual unit before focal attention is deployed.

**He & Nakayama (1992)** — *Nature* 359:231
Extended the depth-as-preattentive-feature result to show that attention selects surfaces, not raw depth-plane features. When image fragments could be interpreted as belonging to a single partially occluded surface, search was efficient regardless of the local feature configuration; when the same fragments were perceived as belonging to distinct surfaces, search became inefficient. The unit of preattentive selection is the surface, and stereoscopic depth specifies surface boundaries.

**Nakayama, Shimojo & Silverman (1989)** — *Perception* 18:55
Showed that stereoscopic depth aids perceptual grouping and the recognition of partially occluded objects: surface fragments placed behind an occluder (far depth plane) were better recognized than those placed in front (near depth plane), because the far-plane assignment licenses a surface-completion interpretation. Depth-plane assignment constrains perceptual organization from an early stage.

**Baylis & Driver (1993)** — *Journal of Experimental Psychology: HPP* 19:451
Demonstrated a two-object cost in feature comparison: judging the relative position of two contours was harder when they appeared to belong to two different objects than to one, even when the physical displays were identical. The effect was driven by perceptual grouping. This establishes that object boundaries — including those defined by depth — create categorical barriers to within-object attentional access.

*VRDots connection*: The He & Nakayama (1992) result establishes that depth-defined surface membership is a primary determinant of attentional selection, not a secondary label. The VRDots ZdA/ZdB dissociation — in which disrupting the depth-plane identity of the cued object impairs cueing while disrupting the uncued object does not — is a direct behavioral consequence of the same principle: attention is anchored to a depth-defined surface, and that surface loses its identity when depth-plane continuity is broken.

---

## 2. Transparent Motion Perception and Surface Segregation

### Key Papers

**Qian, Andersen & Adelson (1994)** — *Journal of Neuroscience* 14:7357, 7367, 7381
A three-part series (psychophysics, physiology, modeling) establishing that transparent motion perception requires locally unbalanced motion signals. When two opposite motion directions are precisely paired in every local region, the display appears as a single flickering surface (non-transparent). Transparency is restored when the signals are spatially or chromatically unbalanced — or when the two motion populations are separated in binocular disparity. The model proposes a disparity- and spatial-frequency-specific opponent-direction suppression stage in the motion pathway (area MT), where anti-phase motion signals cancel locally when they share the same disparity. Disparity imbalance between the two populations releases this suppression and allows both motion directions to be perceived as distinct surfaces.

**Snowden & Rossiter (1999)** — *Perception* 28:193
Direct psychophysical evidence that stereoscopic depth cues segment motion information in transparent-motion displays. When signal and noise dot populations were given different disparities, motion discrimination thresholds fell substantially relative to when they shared the same disparity. The direction of global motion could be computed separately for depth-segregated surfaces, implying that depth separation enables parallel, independent processing of each motion component.

**Snowden (1999)** — *Current Biology* 9:R346
Review of motion transparency. Emphasizes that the visual system can separately encode two motion directions coexisting at the same retinal location only when they are given sufficient disambiguation by non-motion cues (disparity, spatial frequency, color). Without such cues, the two signals partially cancel or fuse. This establishes the general principle that depth is a segmentation cue that feeds into — rather than merely labeling — the motion computation.

**Stoner, Albright & Ramachandran (1990)** — *Nature* 344:153
(Already integrated in integrated_review.md and theory_doc.md §6.1.) Luminance relationships consistent with physical transparency gate motion coherence. The surface interpretation determines the motion percept, not the reverse — motion processing is non-modular and receives segmentation inputs. Sets the theoretical context within which depth separation in VRDots should operate.

*VRDots connection*: Qian et al. (1994) provides a mechanistic prediction for the depth-field cueing effect (F2): depth-plane separation between the two dot fields increases the local motion imbalance, relaxing opponent-direction suppression in MT and producing cleaner, more distinct motion-surface representations. The ZdA/ZdB results are a direct test of whether disrupting this depth-based segmentation — specifically for the attentional object — impairs selection. The Snowden & Rossiter (1999) result confirms that this segmentation is functionally real and large enough to drive strong threshold changes.

---

## 3. Disparity Tuning in Early Visual Cortex

### Key Papers

**Cumming & DeAngelis (2001)** — *Annual Review of Neuroscience* 24:203
Authoritative review of the physiology of stereopsis. V1 neurons encode a wide range of binocular disparities and serve as the substrate of the disparity energy model: binocular simple cells compute the correlation between left- and right-eye inputs, tuning the cell to a preferred absolute retinal disparity. V1 encodes absolute (not relative) disparity. V2 and higher areas (V3, MT) build relative-disparity representations by comparing V1 inputs, and these are more closely linked to perceived depth judgments. Tuning width broadens with eccentricity. MT neurons show disparity tuning that is linked to both depth perception and motion segmentation, with neurons jointly tuned for velocity and disparity forming the substrate for depth-based motion segregation.

**Qian & Andersen (1997)** — *Vision Research* 37:1683
(Already integrated in modeling_lit.md §4.1.) Physiological model of motion-stereo integration via V1 binocular cells jointly tuned for direction and disparity. MT pools these inputs, enabling velocity × disparity selectivity. When two motion surfaces differ in both direction and depth plane, their MT population representations are more separated — a mechanistic basis for stronger surface-based selection with increasing depth separation.

*VRDots connection*: Cumming & DeAngelis (2001) establishes that V1 encodes absolute disparity, meaning the depth-plane signals in VRDots (0.05 m at 2 m viewing distance ≈ 0.72 arcmin disparity at the fovea) are represented by distinct V1 neuron populations for the near and far dot fields. These populations are the bottom of the Point-Set architecture: V1 neurons jointly tuned for direction and disparity form the point-sets that separate cued from uncued surface representations at the earliest cortical stage. The V1 locus also makes a testable ERP prediction: if depth-plane identity modulates attentional selection at V1, this should appear as a C1 modulation, analogous to the dot-cueing C1 modulation reported by Khoe et al. (2005).

---

## 4. Stereoscopic Depth and Motion Grouping

### Key Papers

**Snowden & Rossiter (1999)** — *Perception* 28:193
(See Section 2 above.) Shows that 4 arcmin of disparity between signal and noise populations reduces coherence thresholds measurably, and 12 arcmin reduces them further. The effect is graded — not a step-function — consistent with a continuous contribution of depth separation to motion surface distinctness.

**Hibbard & Bradshaw (1999)** — *Perception* 28:123
Investigated whether binocular disparity facilitates detection of transparent motion. Found that disparity separation between overlapping motion surfaces improves detection of each surface's direction, with effects emerging at modest disparities. Results support the view that depth separation supplements — but does not replace — direction-based segmentation for transparent surface perception.

**Calabro & Vaina (2011)** — *Journal of Neurophysiology* 105:200 [PubMed ID: 21068268]
Examined motion segmentation performance when noise dots were placed at near vs. far disparities relative to signal dots. A consistent bias was found: near-disparity noise disrupted motion segmentation more than equidistant far-disparity noise. The authors explain this with a computational model using a skewed-normal population distribution of MT preferred disparities, reproducing the elevated thresholds for near-disparity noise. The conclusion is that MT's disparity population is anisotropic — the distribution of preferred disparities is not symmetric around zero — with consequences for the perceptual asymmetry between near and far depth-plane motion segmentation.

*VRDots connection*: The Calabro & Vaina (2011) result is directly relevant to the VRDots Far > Near cueing asymmetry observed in the DepthParam and DepthSwapCtrl sessions (Far: +47–60pp; Near: positive throughout all tested depths, ranging from small values at 0.03 m to moderately sized values at 0.15 m, binocular only). Note: earlier records showing apparently negative Near cueing values (e.g., "Near: −5 to +21pp") reflected the old incorrect labeling convention (using delayed-field depth rather than translating-field depth); with the corrected labeling, Near cueing is positive throughout all tested depth separations (0.03–0.15 m), and the Far > Near gap is a difference in magnitude rather than a sign reversal. The Far > Near gap does not reach significance until the largest combined dataset (DepthColorLinked, n=512, +8.6pp*). If MT's near-disparity-tuned population is denser or more broadly tuned than its far-disparity counterpart, then near-disparity signals produce more cross-talk between the two surfaces — contaminating the near-plane surface's point-set representation with distractor signals and reducing cueing efficiency. The monocular collapse of the Near/Far asymmetry (which is entirely stereoscopic) is consistent with this mechanism: without disparity, MT's anisotropy is irrelevant and the two surfaces compete symmetrically through direction signals alone.

---

## 5. Temporal Onset Cueing and Object Files

### Key Papers

**Yantis & Jonides (1984)** — *Journal of Experimental Psychology: HPP* 10:601
Foundational demonstration that abrupt visual onsets capture attention exogenously and independently of top-down goals. In visual search, a target presented as an abrupt onset was selected first even when other search items were identical in all task-relevant features. The mechanism is the transient response of the magnocellular/Y-cell pathway to a new luminance edge. This capture is not contingent on the target's feature properties — it is driven by the temporal event itself.

**Jonides & Yantis (1988)** — *Perception & Psychophysics* 43:346
Extended the onset-capture result to show that abrupt onsets — specifically, and not other feature changes such as color changes or shape changes — uniquely capture attention without top-down support. Color singletons and luminance steps without abrupt onset do not produce the same automatic capture. The onset event per se is the operative cue.

**Kahneman, Treisman & Gibbs (1992)** — *Cognitive Psychology* 24:175
Introduced the object file framework: when an object appears in the visual field, a temporary episodic object file is opened to hold the object's features. Object files are indexed by spatiotemporal location — not by feature values — so the same file can persist through feature changes as long as spatiotemporal continuity is maintained. Object-specific priming across saccades (the "reviewing" benefit) is mediated by object file retrieval. When spatiotemporal continuity is broken (object disappears and reappears in a new location), a new file is opened and old features are not retrieved.

*VRDots connection*: The delayed onset of dot Field B in VRDots is precisely the kind of abrupt onset that Yantis & Jonides (1984) showed to be uniquely exogenous. When the two fields are both present and rotating, the onset of Field B's translation is a transient event against a stable background — automatically engaging the magnocellular transient pathway and driving an attentional pointer to the translating surface. This is why the dot-cueing effect (F1, +20–22pp) is robust and survives monocularly. The Kahneman et al. (1992) object file framework then describes what happens after the onset event: an object file is opened for the cued surface, indexed by its spatiotemporal onset properties, and subsequently updated with the features of that surface (motion direction, depth plane, color). The ZdA result — in which changing the cued object's depth plane at tStart disrupts cueing — is interpretable within object file theory as a spatiotemporal discontinuity that triggers a new file opening, releasing the attentional hold established by the onset cue.

---

## 6. Near vs. Far Attentional Asymmetries

### Key Papers

**Andersen & Kramer (1993)** — *Perception & Psychophysics* 53:658
The most-cited paper on depth-plane attentional asymmetry. Using a response-compatibility flanker task in a stereoscopic display, found that crossed (near) disparities produced larger distractor interference effects than uncrossed (far) disparities: attention gradients are steeper for stimuli nearer than fixation. This result supports an egocentric attentional gradient in which peripersonal space (near, crossed disparity) has higher attentional priority than extrapersonal space (far, uncrossed disparity). This is the classic "near advantage" result that predicts Near > Far for attentional cueing.

**Parks & Corballis (2006)** — *NeuroReport* 17:643
ERP study examining ERPs while participants attended to near or far depth planes. Found that P1 was enhanced only for the far-attended condition, not the near-attended condition. This viewer-centered gradient model holds that the attentional gradient drops off for depths inside fixation relative to those outside — yielding a Far advantage for ERP modulation. Parks & Corballis directly contradicts the Andersen & Kramer (1993) prediction.

**Caziot, Rolfs & Backus (2023)** — *PNAS Nexus* 2:pgad314
Psychophysical study measuring attention in depth with vergence control (nonius lines and oculometry). Found a directional far advantage trend (p = 0.076) with no vergence shift during depth cueing, providing the strongest current evidence that depth-plane attentional asymmetries are driven by disparity signals rather than by vergence-driven spatial shifts of attention.

**Arnott & Shedden (2000)** — *Perception & Psychophysics* 62:1459
Using autostereograms (which lock vergence to screen depth while displaying arbitrary disparities), found that the attentional gradient remains asymmetric even when vergence is experimentally decoupled from disparity. Supports a disparity-driven rather than vergence-driven account.

**Chen, Meng, Matthews & Qian (2012)** — *Journal of Neuroscience* 32:13352
Near advantage in attentional reorienting, but the near-near asymmetry did NOT reverse when fixation depth was varied — arguing against a vergence-driven account (which would predict reversal) and supporting a retinal-disparity-based mechanism.

*VRDots connection*: The literature shows a genuine, unresolved near/far controversy. Andersen & Kramer (1993) predict Near > Far; Parks & Corballis (2006) and Caziot et al. (2023) predict Far > Near. The VRDots DepthParam and DepthSwapCtrl results (Far: +47–60pp; Near: positive throughout all tested depths, binocularly) consistently support the Far > Near pattern across all four depth separations tested (0.03, 0.05, 0.10, 0.15 m), consistent with Parks & Corballis. Earlier records showing apparently negative Near cueing values were an artifact of the old labeling convention (using delayed-field depth rather than translating-field depth); with the corrected convention, Near cueing is positive throughout all tested separations and the Far > Near asymmetry is a difference in magnitude. The effect reaches significance only in the largest dataset (DepthColorLinked, n=512, +8.6pp*), and the near/far advantage is positive in sign and monotonically present — it does not reverse at any tested separation. Critically, the VRDots Near/Far asymmetry is entirely stereoscopic — it collapses completely under monocular viewing — which is consistent with Arnott & Shedden (2000) and Caziot et al. (2023)'s disparity-driven account. Two mechanistic accounts are candidates for the Far > Near asymmetry and are discussed in full in Section 7 below.

---

## 7. Mechanistic Accounts of the Far > Near Cueing Asymmetry

The robust Far > Near asymmetry in VRDots — present across all tested depth separations binocularly, absent monocularly — requires a mechanistic explanation that is grounded in stereoscopic processing. Two candidate accounts exist. They are not mutually exclusive, and their relative contributions can be dissociated by a targeted experimental manipulation described below.

### 7.1 Neural Cross-Talk Account: MT Disparity-Population Anisotropy (Calabro & Vaina 2011)

**Calabro & Vaina (2011)** — *Journal of Neurophysiology* 105:200 [PubMed ID: 21068268] — reported that near-disparity noise disrupts motion segmentation more than equidistant far-disparity noise. Using a model of MT's disparity-population distribution fit to psychophysical data, the authors concluded that MT's preferred-disparity population is anisotropic: more neurons are tuned to near (crossed) disparities than to far (uncrossed) disparities. As a consequence, near-disparity signals produce more inter-surface cross-talk — the near-plane surface's MT representation overlaps more with that of the far-plane surface — reducing the effective signal for near-plane motion segmentation.

Applied to VRDots: if the near-plane dot field's MT population representation is denser but less selective (because nearby preferred-disparity neurons exist to the other surface's disparity), then selecting the near-plane translating surface requires competing against a noisier background representation. The far-plane surface, by contrast, is represented by a smaller but more selective MT population that has less cross-talk with the near-plane surface. This produces the observed asymmetry: far-plane translation is more distinctly represented and more easily selected regardless of the cue's location.

*Key prediction*: The Calabro & Vaina account predicts that the Far > Near asymmetry scales with absolute disparity magnitude in a way that tracks MT's disparity-tuning functions. Adding a third depth plane beyond Far (at even larger far disparity) should have no effect on the Far advantage relative to Near, because the mechanism is about the representational selectivity of the far-disparity MT population, not about the topology of the display.

*Monocular consistency*: The full collapse of the Near/Far asymmetry under monocular viewing (DepthSwapCtrl binocular vs. monocular) is consistent with this account: without binocular disparity, MT's anisotropy is irrelevant.

### 7.2 Attentional Topology Account: The Far-Boundary Hypothesis

A second account is proposed by the experimenter (GS) on the basis of introspective observation during data collection as a subject, not from published literature. It is presented here as a working hypothesis for empirical evaluation.

The proposal is as follows. Attention in depth is not a point but a gradient — a field of attentional priority that extends around the attended depth plane in all three dimensions, including the depth (Z) dimension. When attention is directed to the Near plane in a two-plane VRDots display, the attentional gradient necessarily extends beyond the Near plane toward Far — the gradient has no boundary to constrain it there, and the Far-plane dots fall within the trailing portion of the near-focused gradient. This results in diluted selectivity for the Near-plane surface: some attentional resource is always allocated to Far-plane dots even when the observer is attempting to attend Near. When attention is directed to the Far plane, the situation is topologically asymmetric: in a two-plane display, there is no plane beyond Far. The attentional gradient has a physical boundary at the far display limit. Far-focused attention therefore concentrates its resources on Far-plane dots without any beyond-far leakage, yielding higher effective selectivity for the Far plane than for the Near plane, even if the absolute attentional force directed at each plane is equal.

This account is distinct from the Calabro & Vaina (2011) account in its locus and mechanism. The cross-talk account is about neural-population representational overlap within MT — a bottom-up, sensory-level mechanism. The attentional topology account is about the asymmetric distribution of attentional resources as a function of display topology — a top-down or at least attentional-level mechanism. Importantly, the topology account predicts that the Far advantage depends not on disparity magnitude per se, but on whether anything lies beyond the attended plane in the display.

*Relationship to prior work on attentional gradients*: The broader attentional gradient literature documents that attention is not a step function but a graded field that extends beyond the focal point, decaying with distance (Downing & Pinker 1985; Eriksen & St. James 1986). Downing & Pinker (1985) showed that response latency increases monotonically with cue-target distance in 2D space, establishing that attention has a spatial gradient with a specific shape. Andersen & Kramer (1993) showed that this gradient structure extends into depth: flanker interference is larger for stimuli nearer than fixation than for stimuli farther than fixation, indicating that the gradient is viewer-centered and steeper in the depth direction toward the observer. Arnott & Shedden (2000) used autostereograms to show that a viewer-centered asymmetric depth gradient — steeper toward the observer, shallower away from the observer — is preserved even when vergence is decoupled from disparity, localizing the gradient structure in the disparity representation. He & Nakayama (1995, *PNAS* 92:11155) demonstrated that attention spreads automatically across surfaces in depth, and that this spread is surface-bounded rather than distance-bounded. Together, this literature establishes that attention in depth is a graded, asymmetric, disparity-organized field — the conceptual precursor to the topology account.

The critical addition of the topology account is the claim that the *display boundary* — the absence of any surface beyond the attended depth — constitutes a hard limit on attentional bleed. This claim has no direct precedent in the published literature. The existing gradient work assumes a smooth decay extending indefinitely away from the focal point; the topology account asserts that the decay is truncated when there is no competing surface to receive spillover resources.

*Key prediction — the three-plane experiment*: The Calabro & Vaina account and the attentional topology account make divergent predictions in a three-plane display (Near / Mid / Far). Under the neural cross-talk account, the Far advantage over Near is determined by MT's disparity-population structure and should be present regardless of whether a farther plane exists: comparing Mid vs. Far cueing in a three-plane display should replicate the Near vs. Far asymmetry in direction, simply with Mid playing the role of Near. Under the attentional topology account, the Far advantage should diminish or disappear when a plane exists beyond Far — because Far is no longer the outermost plane, and its attentional gradient now bleeds into the beyond-Far region just as Near's gradient bleeds into Mid. The critical comparison is Far vs. Mid cueing when a fourth, more-far plane is added versus when it is not: if the Far advantage relative to Mid disappears when a farther plane is added, the topology account is supported; if it remains, the cross-talk account is supported. This constitutes a tractable test that does not require neuroimaging and is compatible with the current VRDots paradigm by straightforward extension to three depth planes.

### 7.3 Summary and Relationship Between Accounts

The two accounts are summarized in the table below.

| Property | Neural Cross-Talk (Calabro & Vaina) | Attentional Topology (GS, introspective) |
|---|---|---|
| Mechanism locus | MT, early sensory | Attentional gradient, top-down |
| Operative variable | Absolute disparity magnitude | Presence/absence of surface beyond attended plane |
| Monocular prediction | Collapses (no disparity) | Collapses (no depth planes) |
| 3-plane prediction | Far advantage vs. Mid ≈ Near advantage vs. Far | Far advantage vs. Mid diminishes if farther plane added |
| Disparity scaling | Tracks MT tuning functions | Tracks perceived depth segregation quality |

Both accounts correctly predict the monocular collapse of the Near/Far asymmetry. They diverge in their three-plane prediction, making the three-plane experiment the critical dissociation test. Neither account can be ruled out by the existing two-plane VRDots data.

---

## 8. Gaps in the Literature

The VRDots paradigm addresses a set of empirical questions that have not been directly tested in any prior published work. The following are the primary gaps:

**Gap 1 — No prior 3D transparent-motion attention paradigm.** The Valdes-Sosa/Mitchell/Reynolds paradigm has always used 2D transparent surfaces (both fields at the same depth plane). VRDots is, to our knowledge, the first implementation of this paradigm with explicit, parametrically varied stereoscopic depth separation. Prior work (Qian et al. 1994; Snowden & Rossiter 1999) measured perceptual thresholds for transparent-motion detection as a function of disparity, but did not use a cuing-and-target design to probe attentional surface selection.

**Gap 2 — No prior test of depth continuity as a constitutive object feature.** The He & Nakayama (1992) and Nakayama et al. (1989) work established that depth defines surface membership, but used static search paradigms. The VRDots ZdA/ZdB manipulation is the first test of whether depth-plane continuity at the moment of target onset is required for an attentional pointer — established 750 ms earlier by a temporal onset cue — to remain anchored to a moving surface. This is a dynamic, time-resolved test of depth as an object-file feature.

**Gap 3 — No prior parametric depth-separation × attentional cueing experiment.** The Snowden & Rossiter (1999) and Hibbard & Bradshaw (1999) studies measured threshold-versus-disparity curves for transparent-motion detection; no published study has measured an attentional cueing effect (CUED vs. UNCUED advantage) as a function of depth separation. The VRDots DepthParam family (0.03–0.15 m) provides the first such dataset and reveals a non-monotone Near/Far pattern that is not predicted by any existing account.

**Gap 4 — The conjunction requirement (F1 × F2) is a new empirical fact.** The GLM interaction result — that depth-field cueing (F2) provides benefit only when combined with temporal onset cueing (F1), and neither alone elevates performance — has no precedent in the object-based attention or depth-perception literatures. The Kahneman et al. (1992) object-file framework predicts that depth can be bound into an object file, but does not predict this specific conjunction requirement. Desimone & Duncan's (1995) biased competition framework predicts that either depth or onset salience could independently bias competition, which is inconsistent with the interaction pattern. The conjunction requirement is an empirically new finding that constrains any model of depth-based surface selection.

**Gap 5 — Far > Near translation asymmetry in surface-based attentional cueing has no published precedent.** Across all four depth separations tested (0.03–0.15 m, binocular viewing), VRDots shows a consistent advantage for cueing the far-plane translator relative to the near-plane translator. This asymmetry is positive in sign throughout and does not reverse at any tested separation; it reaches significance in the largest combined dataset (DepthColorLinked, n=512, +8.6pp*). An earlier framing of this result as a "near-plane cueing reversal" at large disparities (UNCUED Near > CUED Near) was an artifact of simultaneously flipping both cue location and translation depth in a single contrast — a confounded comparison. The corrected analysis (holding translation depth constant and varying only the cue) yields CUED > UNCUED throughout. No prior study in the depth-attention literature has measured an attentional cueing effect (CUED vs. UNCUED advantage) as a function of depth-plane membership in a transparent-motion paradigm. The Far > Near asymmetry is entirely stereoscopic (collapses monocularly), identifying its origin as binocular disparity processing. Two candidate mechanisms — MT cross-talk (Calabro & Vaina 2011) and attentional topology (Section 7) — are currently viable; the three-plane experiment is the critical test.

---

*For cited papers' full bibliographic details, see `paper_notes/paper_list.md` (Groups 7 and 8).*
*New papers to add to paper_list.md: Snowden & Rossiter (1999) Perception 28:193; Hibbard & Bradshaw (1999) Perception 28:123; Calabro & Vaina (2011) J Neurophysiol 105:200; Nakayama et al. (1989) Perception 18:55; He & Nakayama (1992) Nature 359:231; He & Nakayama (1995) PNAS 92:11155; Jonides & Yantis (1988) P&P 43:346; Downing & Pinker (1985) in Posner & Marin (Eds.) Attention and Performance XI; Arnott & Shedden (2000) P&P 62:1459.*
*Revised 2026-04-04: (1) Section 6 VRDots connection corrected — prior framing as "near-reversal" removed, replaced with corrected Far > Near account. (2) Section 7 (Mechanistic Accounts of Far > Near) added. (3) Gap 5 corrected — near-reversal artifact removed, replaced with corrected description of Far > Near asymmetry. (4) Section 8 (formerly Section 7, Gaps) renumbered.*
*Related documents: `depth_experiments_intro.md`, `theory_doc.md §4.3–4.5`, `modeling_lit.md §4.1–4.2`, `historical_comparison.md §5`, `depth_ior_hypothesis.md`.*
