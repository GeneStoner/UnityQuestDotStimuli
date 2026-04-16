# Literature Survey: Depth, Depth-Order, and Selective Attention in Transparent Motion / Superimposed Stimuli

**Compiled:** 2026-04-13 (revised post-artifact fix)
**Sources surveyed:** All VRDots literature agent files plus `decoupled_dots_results.md`, `depthcolorlinked_results.md`, `bothfar_results.md`, `depth_ior_hypothesis.md`, `beyond_account_provisional.md`, `color_model_conjecture.md`, `theory_doc.md`, `integrated_review.md`, `modeling_lit.md`, `pending_papers.md`, `paper_notes/paper_list.md`.

> **⚠️ REVISION NOTE (2026-04-13):** A Unity stimulus artifact was discovered and fixed (commit 5c4c95a). The artifact produced a ~19°/sec upward motion impulse at every depth-swap frame — 8.2× the translation signal — in all sessions using Z, CZ, ZdA, ZdB, and ZdNoi/ZdCoh conditions. The first clean post-fix session (260413_1846, n=512, DecoupledDots_005m_v2) yields F2 = +6.2pp n.s. (was +12.5pp***) and F1×F2 = +7.8pp n.s. (was +32.7pp***). The VRDots empirical sections below are updated accordingly. Sections A–C (external literature) are unchanged.

---

## A. External Papers with Direct Evidence that Depth/Depth-Order Influences Attention in Transparent Motion or Superimposed Stimuli

**A1. Snowden & Rossiter (1999). "Perceiving motion in depth using binocular and monocular cues." Perception 28:193.**
Confidence: HIGH. When signal and noise dot populations in a transparent RDK are assigned different binocular disparities, motion discrimination thresholds fall substantially — graded, not step-function. Depth provides an unambiguous segmentation cue allowing selective processing of the attended depth plane.
VRDots note: Directly supports the hypothesis that depth should help surface selection. However, their paradigm measures threshold with no explicit cue; VRDots UNCUED flatness (depth available but providing no benefit without the onset cue) is not predicted by Snowden & Rossiter.

**A2. Lankheet & Verstraten (1995). "Attentional modulation of adaptation to two-component transparent motion." Vision Research 35(10):1401–1412.**
Confidence: HIGH. Attention to one component of a transparent RDK produces directional MAEs specific to the attended direction (≈70% gain change), even without depth separation.
VRDots note: Establishes that attention can selectively amplify one transparent surface's motion representation even without depth. Depth separation should only improve this selectivity.

**A3. Chopin & Mamassian (2011). "Usefulness influences visual appearance in motion transparency depth rivalry." Journal of Vision 11(7):18. PMID 21705461.**
Confidence: HIGH. Task-relevant surfaces in transparent motion rivalry are more frequently reported as "in front" — perceived depth order is modulated by top-down attention.
VRDots note: In zero-disparity VRDots baseline, the cued (delayed-onset) surface may be spontaneously perceived as nearer due to attentional salience.

**A4. Qian, Andersen & Adelson (1994). "Transparent motion perception as detection of unbalanced motion signals." Journal of Neuroscience 14:7357. PMID 7996188.**
Confidence: HIGH. Transparent motion requires locally unbalanced motion signals. Disparity imbalance (depth-plane separation between populations) additionally supports transparency by removing local opponent-direction cancellation at MT. MT neurons are jointly tuned for direction and disparity; giving two surfaces different disparities separates their MT representations.
VRDots note: Provides the primary mechanistic prediction for why depth should help surface-based selection. The ZdA depth-swap reduces the disparity-based imbalance that supports the cued surface as a distinct unit — *if* F2 proves real in clean data.

**A5. Hibbard & Bradshaw (1999). Perception 28:123.**
Confidence: HIGH. Binocular disparity separation between overlapping motion surfaces improves direction detection; effects emerge at modest disparities.

**A6. Calabro & Vaina (2011). "Population anisotropy in area MT explains a perceptual difference between near and far disparity motion segmentation." Journal of Neurophysiology 105:200. PMID 21068268.**
Confidence: HIGH (PubMed ID confirmed). Near-disparity noise disrupts motion segmentation more than equidistant far-disparity noise. MT's preferred-disparity population is anisotropic: more neurons tuned to near (crossed) disparities → more inter-surface cross-talk at Near → reduced selectivity.
VRDots note: Directly relevant to the VRDots Far > Near cueing asymmetry (F4), which is artifact-independent (measured in the N condition). The MT anisotropy account is one of two candidate mechanisms for F4.

**A7. Mitchell, Stoner & Reynolds (2004). "Object-based attention determines dominance in binocular rivalry." Nature 429:410. PMID 15164065.**
Confidence: HIGH (local PDF confirmed). The onset-translation cue substantially increases the probability that the cued surface dominates binocular rivalry. Establishes that the onset cue designates a surface at the level of perceptual representation.
VRDots note: The same onset-cue paradigm underlies VRDots. Adding stereo disparity tests whether depth-plane identity strengthens or disrupts this surface designation.

**A8. Wannig, Rodriguez & Freiwald (2007). "Attention to surfaces modulates motion processing in extrastriate cortex." Neuron 54(4):639–651.**
Confidence: HIGH. MT neurons in non-human primates respond more strongly to the attended transparent surface's direction, in a direction-selective, surface-specific way.

---

## B. External Papers with Indirect/Related Evidence (Depth in Other Attention Paradigms, Near/Far Asymmetries)

**B1. Nakayama & Silverman (1986). Perception 15(2):221–236.**
Depth is a preattentive dimension; search in a display where target differs in stereoscopic depth from distractors is essentially parallel. VRDots note: UNCUED flatness shows preattentive depth availability is not sufficient for attentional selection without the onset cue.

**B2. He & Nakayama (1992). "Surfaces versus features in visual search." Nature 359:231.**
The unit of attentional selection is a surface (object), not a depth-plane location. Perceptual interpretation of depth determines efficiency. VRDots note: The ZdA/ZdB dissociation, if confirmed in clean data, would directly instantiate this logic.

**B3. He & Nakayama (1995). Perceiving textures. Science 265:791.**
Attention spreads automatically across surfaces — surface-bounded, not spatially bounded. VRDots note: ZdA would break the scaffolding for automatic attentional spread across the cued surface.

**B4. Nakayama, Shimojo & Silverman (1989). Perception 18(1):55. PMID 2771595.**
Binocular disparity provides a powerful perceptual grouping cue; disparity immediately and categorically resolves depth order in otherwise ambiguous transparent displays.

**B5. Andersen & Kramer (1993). Perception & Psychophysics 53(6):658.**
Flanker interference is larger for stimuli nearer than the target — near-space attentional priority. Directly CONTRADICTS VRDots Far > Near cueing asymmetry. The discrepancy may reflect task differences (attentional interference vs. surface selection).

**B6. Parks & Corballis (2006). NeuroReport 17(6):643.**
ERP: P1 component enhanced only in far-attended condition. Directionally consistent with VRDots Far > Near asymmetry. May distinguish: attentional interference (near advantage) vs. attentional selection effectiveness (far advantage).

**B7. Caziot, Rolfs & Backus (2023). "Asymmetric distribution of visual attention across depth planes." PNAS Nexus 2(9):pgad314.**
Confidence: HIGH. Far-plane advantage trend (p = 0.076), directionally consistent with VRDots F4. Critically: no vergence shift during depth-plane cueing — asymmetry is neural, not motor. Methodologically most rigorous study to date.

**B8. Arnott & Shedden (2000). Perception & Psychophysics 62(7):1459.**
Attentional gradients in depth remain asymmetric even when vergence is decoupled (autostereograms). Asymmetry is localized in the retinal disparity representation, not vergence — consistent with VRDots monocular collapse of F4.

**B9. Chen, Meng, Matthews & Qian (2012). Journal of Neuroscience 32(38):13352.**
Near-plane advantage in attentional reorienting; asymmetry does not reverse with fixation depth, supporting retinal-disparity locus. Direction opposite to VRDots F4 — near vs. far advantage may depend on task type.

**B10. Andersen (1990). Perception & Psychophysics 47(2):112.**
Voluntary depth-plane selection measurable (detection latency/accuracy) with binocular depth cues; reduced substantially under monocular viewing. Consistent with VRDots F4 monocular collapse.

**B11. Egly, Driver & Rafal (1994). Journal of Experimental Psychology: General 123(2):161. PMID 8014612.**
Within-object attentional advantages are spatial-distance-independent; extend to depth-defined objects. VRDots CUED > UNCUED is formally consistent; the conjunction requirement (UNCUED does not benefit from depth) extends the Egly-Driver logic.

**B12. Baylis & Driver (1993). Journal of Experimental Psychology: HPP 19(3):451. PMID 8409862.**
Object boundaries — including depth-plane-defined boundaries — create categorical barriers to attentional access.

**B13. Downing & Pinker (1985). In Attention and Performance XI.**
Attention is a graded field with gradient structure extending into depth (combined with Andersen & Kramer 1993).

**B14. Natsukawa et al. (2015). Human Brain Mapping 36(10):3922. PMC6869142.**
fMRI/MEG: depth-order determination in transparent motion recruits bilateral IPS, right LO, ACC; MEG time course: 216–405 ms. Depth-order assignment is complete ≥200 ms before the 1000ms+ pre-translation window in VRDots — no timing confound.

**B15. Mamassian & Wallace (2010). Journal of Vision 10(13). PMID 21149310.**
Transparent motion depth preferences are idiosyncratic, stable, and direction-biased (rightward/downward). Color coding slows depth-order reversals. VRDots note: In zero-disparity baseline, depth ordering may be idiosyncratic; stereo disparity is the most reliable override.

**B16. Hwang & Schütz (2020). Journal of Vision 20(12):3. PMID 33156337.**
Transparent motion and dichoptic rivalry depth preferences are uncorrelated — different computational mechanisms.

**B17. Stoner, Albright & Ramachandran (1990). Nature 344:153. PMID 2308632.**
Intersection luminance consistent with physical transparency determines perceived depth ordering in plaids. VRDots uses discrete dots — depth-order assignment is more ambiguous in zero-disparity conditions.

**B18. Stoner & Albright (1998). Vision Research 38:387. PMID 9536362.**
Higher-contrast components perceived as "in front." VRDots color conditions: residual luminance contrast differences may introduce non-arbitrary depth ordering.

**B19. Madelain, Herman, Harwood & Wallman (2012). Journal of Vision. PMID 22205685.**
Surfaces adapted to current direction, or with more dots, tend to be perceived behind. VRDots: both fields rotate at matched speed — speed cannot drive depth-ordering biases.

**B20. Nakayama & Mackeben (1989). Vision Research 29(11):1631. PMID 2635476.**
Two attentional components: transient (exogenously driven, peaks ≤50ms) and sustained (effortful, top-down). The onset cue engages the transient system.

**B21. Cumming & DeAngelis (2001). Annual Review of Neuroscience 24:203.**
V1 encodes absolute disparities; MT neurons are jointly tuned for velocity and disparity, forming the substrate for depth-based motion segregation.

**B22. Qian & Andersen (1997). Vision Research 37:1683.**
V1 binocular cells jointly tuned for direction and disparity; MT pools these, enabling direction × disparity selectivity. Two surfaces differing in both direction and depth have more separated MT population representations.

**B23. Blake & Logothetis (2002). Nature Reviews Neuroscience 3(1):13. PMID 11823802.**
Binocular rivalry involves active suppression across multiple cortical levels; top-down attention biases which representation wins.

**B24. Bi-stable depth ordering of moving gratings (2009). Journal of Vision. PMID 19146253.**
Spatial frequency ratio has a stronger effect on perceived depth than speed ratio, and can override stereo disparity cues when sufficiently large.

**B25. Solé Puig et al. (2013). PLOS ONE 8:e52955.**
Confidence: LOW-MODERATE. Vergence microsaccades track attended depth but do not predict RT — vergence tracks attention, does not drive it.

**B26. Theeuwes, Atchley & Kramer (1998). In Visual Attention (Parasuraman, ed.).**
Depth-plane filtering is feature-contingent; same-color stimuli reduce effectiveness of depth-plane filtering. Predicts weaker F2 in same-color VRDots conditions.

**B27. Maringelli et al. (2001). Psychological Science 12:214.**
Confidence: LOW-MODERATE. In VR environments without a virtual body, attention is directed outward (far) — potentially a VR-specific account of Far > Near asymmetry.

**B28. Jänig et al. (2025). Venue TBD.**
Confidence: LOW (near-contemporaneous). ERPs in a two-depth-plane stereoscopic RDK paradigm — described as nearest published VRDots analog. Should be retrieved.

**B29. Khoe, Mitchell, Reynolds & Hillyard (2005). Vision Research 45:3004.**
ERP during translating-dot paradigm: C1 (75–110ms) and N1 (160–210ms) enhanced for attended surface. Surface-based selection modulates earliest cortical stages via feedback.

**B30. Khoe et al. (2008). Journal of Vision 8(3):18. PMID 18484824.**
ERP under dichoptic rivalry: P1 enhanced for same-surface probes under rivalry; absent monocularly. VRDots note: Behavioral monocular cueing survival (+7.1pp*) may recruit a different, later mechanism.

**B31. Kahneman, Treisman & Gibbs (1992). "Object files." Cognitive Psychology 24:175.**
Object files are indexed by spatiotemporal continuity; feature discontinuities trigger new file opening. ZdA depth switch may constitute such a discontinuity — *if* F2 proves real in clean data.

---

## C. Theoretical Proposals and Speculations

**C1. Attentional Topology / Far-Boundary Hypothesis (GS, introspective).**
When attention is directed to the Near plane, the attentional gradient necessarily extends toward Far (nothing bounds it there). When directed to Far, the gradient is concentrated on Far dots alone. BothFar UNCUED reversal argues against this as the *primary* mechanism for the structural Far > Near baseline. May contribute an additive secondary component.

**C2. Fixation-Plane Hypothesis / Minimum Vergence Demand Account (GS and programming agent, 2026-04-11).**
UNCUED arm defaults to the plane with minimum absolute disparity from fixation (least vergence demand), independent of cueing. Explains both standard Far > Near (Far = uncrossed = less strain for esophoric GS) and BothFar UNCUED reversal (Less-Far = smaller absolute disparity wins). Partially supported by BothFar data. Second observer with normal vergence is the critical test.

**C3. Depth-Gradient Baseline with Cue Modulation (Gradient Migration) Account.**
Attention in depth is anchored at fixation and extends more easily toward Far. Far cue fires into high-gain region; Near cue fires into low-gain region and gradient continuously pulls toward Far during the delay ("gradient migration"). SOA manipulation and fixation-depth reversal are the critical tests.

**C4. V1 Point-Set Model Extension to Depth (Stoner 2010/2018 SfN; Catak et al. 2022).**
V1 neurons jointly tuned for direction and disparity form point-sets that separate cued from uncued surface representations. ZdA disrupts the cued surface's depth-column coherence; ZdB disrupts the distractor's. Critically predicts F2 >> F3: M-pathway carries both direction and disparity signals but not color, so depth is directly in the selection loop and color is not. Status: The prediction F2 >> F3 is supported by the color null (F3 = 0, clean), but the F2 magnitude itself is now unconfirmed pending clean data.

**C5. Spontaneous Depth-Order Assignment as Parallel Mechanism in Zero-Disparity Baseline.**
In zero-disparity baseline, the delayed-onset (cued) field may be spontaneously perceived as nearer. Partially consistent with F1 but contradicted by the Far > Near cueing asymmetry (if cued = near spontaneously, Far-delayed trials should suffer a conflict cost — opposite observed).

**C6. Feature-Integration / Object-File Account of Depth-Plane Disruption.**
Depth serves as a binding dimension; depth-plane consistency across the cue-to-translation interval binds the cued surface's features into a stable, selectable unit. ZdA breaks this binding — consistent with Kahneman et al. (1992) object-file interpretation. Awaits clean empirical support from ZdA replication.

**C7. Surface-Based vs. Depth-Plane-Based Distinction.**
UNCUED arm flatness argues against depth-plane location as the selection unit: if observers were simply attending to "the near plane," UNCUED trials in the expected plane should produce above-chance performance. They do not — consistent with surface-based (not location-based) depth selection.

**C8. M-Pathway Conjecture: Why F2 >> F3 (Color Null).**
Onset transient drives M-cells (motion + disparity, not chromatic). Feature-similarity gain broadcast from MT activates neurons tuned for both direction and disparity, but not blob (color) neurons. Color cells are boosted only secondarily via weak lateral coupling. This correctly predicted F3 = 0 from first principles, independent of the depth-swap artifact. The prediction is confirmed by the C condition analysis (artifact-free), making this the cleanest mechanistic contribution of DecoupledDots.

---

## D. VRDots Empirical Findings Relevant to Depth-Attention

> **Artifact status key:**
> ✓ = artifact-independent (not involving depth-swap frames; reliable)
> ⚠ = artifact-contaminated (pre-fix data; one clean post-fix session; provisionally unconfirmed)
> ⚠⚠ = artifact-contaminated and no clean replication yet

---

**D1. ✓ F1: Dot cueing effect. +27.3pp*** (post-fix, n=512); +22.3pp*** (pre-fix, n=2051).**
The temporal onset cue (delayed-onset brightening of one surface's dots) produces large, robust increases in translation direction accuracy. This is the foundational result and is entirely artifact-independent (no depth swap involved in how F1 is measured). The effect is large, bilaterally confirmed across multiple sessions, and survives monocular viewing (+7.1pp*).
Type: ✓ Confirmed.

**D2. ✓ F3: Color-field cueing = zero. OR = 1.00, p = .994 (DecoupledDots, n=2051).**
The C (color-swap only) condition does not reduce cueing relative to N (no swap). This is artifact-independent because C condition has no depth swap — no upward jerk is introduced. Confirmed across all 4 DecoupledDots sessions.
Type: ✓ Confirmed (most rigorous null in VRDots).

**D3. ✓ F4: Far > Near cueing asymmetry. Robust, entirely stereoscopic.**
Measured exclusively from the N (no swap) condition — no depth swap, no artifact. Across all binocular depth separations (0.03, 0.05, 0.10, 0.15 m): Far cueing consistently exceeds Near cueing. DecoupledDots GLM2: Translator Near = −15.3pp, z = −4.51, p < .001. DepthColorLinked GLM: Translator Near = −21.4pp, z = −4.12, p < .001. DepthParam (n=32/cell): Far cueing ~84–91% CUED across depths; Near cueing degrades monotonically. Entirely absent monocularly (binocular = +9.4pp†; monocular = +1.2pp n.s.).
Two candidate mechanisms: (i) MT disparity-population anisotropy (Calabro & Vaina 2011); (ii) vergence-comfort/minimum-disparity structural bias (C2 above). Critical test: second observer with normal vergence.
Type: ✓ Confirmed.

**D4. ✓ F1: Monocular collapse of Near/Far asymmetry but survival of dot cueing.**
From N condition (artifact-free): dot cueing binocular = +19.8pp*** → monocular = +7.1pp* (attenuated but survives). Near/Far asymmetry: binocular = +9.4pp† → monocular = +1.2pp n.s. (completely collapses). Two separable components: monocular surface-selection component (motion coherence + temporal onset) and binocular component tied to disparity-defined depth-plane identity.
Type: ✓ Confirmed.

**D5. ✓ UNCUED arm flatness for depth conditions.**
In both DepthColorLinked and DecoupledDots, UNCUED performance is near chance and flat across depth conditions regardless of depth-plane continuity. This holds robustly: UNCUED+ZdNoi = 21.9% vs. UNCUED+ZdCoh = 23.4% (1.5pp, n.s.); all UNCUED cells cluster near 12.5% baseline in DecoupledDots. Note: because the artifact specifically introduced a spurious upward motion signal at depth-swap frames, if anything it would inflate UNCUED performance on depth-swap trials, making the UNCUED flatness even more conservative (the true UNCUED flatness is at least as strong as pre-fix data showed). Depth-plane identity cannot initiate attentional selection — the onset cue is necessary.
Type: ✓ Confirmed (artifact-robust, possibly conservative estimate of flatness).

**D6. ⚠ F2: Depth-field cueing effect. Pre-fix: +12.5pp***. Post-fix: +6.2pp n.s.**
*Pre-fix (DecoupledDots, n=2051):* Logistic regression depth-field cueing AME = +12.5pp, z = 4.46, p < .001, OR = 1.89. Appeared to confirm that depth-plane continuity benefits attentional selection.
*Post-fix (DecoupledDots_005m_v2, n=512):* F2 = +6.2pp n.s. The previously significant result is absent in the first clean session. The upward-motion artifact specifically punished CUED+Z trials (where the depth swap coincides with the translation onset), artificially inflating the apparent cost of a depth swap. Once removed, depth-plane continuity shows at most a modest, currently non-significant benefit.
*Current status:* UNCONFIRMED. One more clean session (v2 asset) needed. Do not cite the pre-fix F2 as a clean result.
Type: ⚠ Provisional / unconfirmed.

**D7. ⚠ F1×F2 conjunction requirement. Pre-fix: +32.7pp*** (DecoupledDots), +16.5pp** (DepthColorLinked). Post-fix: +7.8pp n.s.**
*Pre-fix:* GLM2 with interaction terms (DecoupledDots, n=2051): F1×F2 AME = +32.7pp, p < 10^-17 — this was the headline finding, suggesting depth-plane continuity is required in conjunction with the onset cue. DepthColorLinked (n=1024): F1×F2 = +16.5pp, p = .003, independently replicated.
*Post-fix:* F1×F2 = +7.8pp n.s. The conjunction requirement — that depth matters only when combined with the onset cue — is not demonstrated in clean data. Both DecoupledDots instances and the DepthColorLinked data are pre-fix.
*Current status:* UNCONFIRMED. This was the most theoretically important finding. It is now the most urgent replication target.
Type: ⚠⚠ Unconfirmed; requires clean replication.

**D8. ⚠ ZdA/ZdB dissociation: cued-object depth disruption kills cueing; distractor depth disruption enhances it.**
*Pre-fix (DepthSwapCtrl, n=384):* N = +34pp**; ZdA = +12pp n.s. (abolished); ZdB = +56pp*** (enhanced). ZdA and ZdB were matched for dot count swapping depth — the difference was specifically whether the *coherent translating group* changed depth. DepthColorLinked confirmed the same direction: ZdNoi (translator stays in plane) vs. ZdCoh (translator changes plane) showed 18.8pp reduction.
*Artifact status:* DepthSwapCtrl used a "different but partially afflicted" asset. ZdA/ZdB results carry unknown artifact contamination. DepthColorLinked ZdNoi/ZdCoh results are also pre-fix.
*Current status:* UNCONFIRMED. The ZdA/ZdB directional pattern is the most theoretically informative dissociation in VRDots (object-specific vs. scene-level disruption). Needs clean replication with v2 asset and 50% swap structure.
Type: ⚠⚠ Unconfirmed; requires clean replication with post-fix asset.

**D9. ✓/⚠ BothFar experiment: UNCUED reversal (Less-Far > More-Far); F1×F4 dissociation.**
*Session:* 260411_1225, n=512, pre-fix asset. When both fields are placed behind fixation (+0.05m and +0.10m uncrossed):
UNCUED arm: favors Less-Far (+11.5pp*** Less-Far vs. −0.8pp n.s. More-Far; Δ = +12.3pp*) — reversed relative to standard N/F paradigm.
CUED arm: maintains More-Far ≥ Less-Far preference (same direction as standard Far > Near).
F1×F4 interaction = +17.8pp, exposing two previously confounded mechanisms: (structural) UNCUED defaults to minimum-vergence plane; (attentional) CUED preferentially selects the more extreme plane.
*Artifact note:* BothFar was run pre-fix; F2 result in BothFar (depth-swap disruption ~17pp in CUED arm) is suspect. However, the UNCUED reversal finding derives from the *N* condition (no depth swap) — it is artifact-independent. The F1×F4 dissociation similarly derives from N condition.
Type: ✓ UNCUED reversal and F1×F4 dissociation are confirmed. F2 estimate from BothFar is ⚠ suspect.

---

## E. Null Results or Counter-Evidence

**E1. Andersen & Kramer (1993): Near > Far attentional interference — opposite to VRDots F4.**
Near-space attentional priority in flanker interference. Contradicts VRDots Far > Near cueing asymmetry. Possible resolution: attentional interference (near advantage) vs. attentional selection effectiveness (far advantage).

**E2. Chen, Meng, Matthews & Qian (2012): Near advantage in attentional reorienting — opposite direction.**
Another near-advantage result; task differences may explain the discrepancy with VRDots F4.

**E3. ✓ Color-field cueing (F3) = exactly zero: OR = 1.00, p = .994.**
Artifact-independent (C condition has no depth swap). The most rigorous null in VRDots — color does not contribute to surface-based selection in this paradigm. Directly supports C8 (M-pathway conjecture).

**E4. ✓ UNCUED arm flatness for F2 (depth continuity): depth does not help UNCUED observers even when fully available.**
Even when depth-plane continuity is perfectly preserved throughout the trial (N condition), UNCUED performance is at chance. Argues against any model in which depth preattentively segments the display in a task-useful way without a prior designation event.

**E5. Caziot et al. (2023): far advantage trend marginal (p = 0.076).**
The most rigorous external study of depth-plane attention asymmetries does not reach conventional significance, though directionally consistent with VRDots F4.

**E6. BothFar UNCUED arm: does NOT favor More-Far (more uncrossed) — reverses expectation.**
Rules out a simple "more uncrossed disparity = better" account of the structural Near/Far asymmetry. The minimum-vergence-demand account (C2) accommodates both the standard Far > Near and the BothFar Less-Far > More-Far.

**E7. ⚠→✓ F2 (depth-field cueing) collapses post artifact fix: +12.5pp*** → +6.2pp n.s.**
Previously considered a positive result; now a null. This is the most significant change in the VRDots result set. The previously headline finding — that depth-plane continuity is required for sustained attentional selection — is currently unconfirmed in clean data. One clean session (n=512) is insufficient to rule out a small real effect, but the point estimate is +6.2pp, well short of the originally reported +12.5pp.

---

## F. Papers Listed as Pending/To-Read That Are Likely Relevant

**F1. Calabro & Vaina (2011). Journal of Neurophysiology 105:200. PMID 21068268.** HIGH PRIORITY. Primary candidate for MT disparity-population anisotropy account of the (confirmed) F4 asymmetry. Full text not yet read.

**F2. Neri, Bridge & Heeger (2004). Journal of Neuroscience.** fMRI of absolute vs. relative disparity in V1–V3/MT — relevant to whether F4 reflects absolute or relative disparity processing.

**F3. Uka & DeAngelis (2006). Journal of Neuroscience.** Causal role of MT disparity signals — relevant if ZdA/ZdB effects (when confirmed) are mediated through MT disparity rather than surface-identity mechanisms.

**F4. Tse et al. (2005). Journal of Vision.** Motion-in-depth from IOVD — relevant to whether depth-plane transitions in ZdA/ZdB create unintended motion-in-depth signals.

**F5. Jänig et al. (2025). Venue TBD.** HIGH — nearest published analog to VRDots. Motion-onset ERP in stereoscopic transparent-motion display. Should be retrieved and fully integrated.

**F6. Roelfsema, Lamme & Spekreijse (1998). Nature 395:376.** HIGH PRIORITY. V1 neurons track attended object contours — foundational for the Point-Set model. Note: paradigm uses spatially extended contours, not intermixed dot fields.

**F7. Maringelli et al. (2001). Psychological Science 12:214.** VR-specific: no virtual body → attention directed outward (far). Potentially accounts for VRDots F4 as a VR-context effect rather than a general depth-attention asymmetry.

**F8. Theeuwes, Atchley & Kramer (1998).** Depth-plane filtering is feature-contingent; same-color stimuli reduce effectiveness. Predicts weaker F2 in same-color conditions (testable once F2 is confirmed in clean data).

**F9. Solé Puig et al. (2013). PLOS ONE 8:e52955.** Vergence microsaccades track attended depth but do not predict RT — vergence tracks attention, does not drive it.

**F10. Lee & Maunsell (2010). J Neurosci 30:3058.** HIGH PRIORITY. Attentional modulation of MT neurons with multiple stimuli in receptive fields — the VRDots two-surface scenario exactly.

---

## Summary of Key Cross-Cutting Points

**What the external literature establishes:**

1. Depth separation between overlapping motion surfaces improves motion discrimination thresholds (Snowden & Rossiter 1999; Hibbard & Bradshaw 1999) and should reduce the cross-talk between surface representations in MT (Qian et al. 1994; Qian & Andersen 1997). These results predict that depth should help surface-based attention — an expectation that the VRDots F2 result was designed to test.

2. The onset-cue paradigm (from Valdes-Sosa through Mitchell et al. 2004) establishes that surface-level attentional selection is triggered by exogenous onset events and operates on full surface representations, not local motion features. VRDots extends this paradigm into stereo depth.

3. Near vs. Far attentional asymmetries are contested in the literature: flanker interference paradigms show Near > Far (Andersen & Kramer 1993; Chen et al. 2012); attentional selection paradigms tend to show Far ≥ Near (Parks & Corballis 2006; Caziot et al. 2023). The VRDots Far > Near asymmetry (F4) is consistent with the latter and is the most methodologically rigorous behavioral result in this direction.

4. Depth-order assignment in transparent motion takes 200–400 ms (Natsukawa et al. 2015), well within the >1000 ms pre-translation window in VRDots — timing is not a confound.

**What VRDots currently contributes (confirmed findings):**

1. **Robust exogenous cueing of transparent motion surfaces** (+27pp*** post-fix, artifact-independent). The temporal onset cue produces large, reliable increases in translation direction accuracy in a two-surface transparent motion display with or without stereoscopic depth. This is the foundational paradigmatic result.

2. **Color null: F3 = exactly zero** (artifact-independent). Color-plane continuity is completely uninformative for surface-based selection, despite color being an equally visible surface feature. This is strong, artifact-free support for C8 (M-pathway conjecture): the selection mechanism operates on M-pathway signals (motion + disparity) and is blind to chromatic surface labels.

3. **Far > Near cueing asymmetry, entirely stereoscopic** (artifact-independent; from N condition only). Consistent across all four depth separations tested binocularly. Absent monocularly. Two competing accounts remain viable: MT disparity-population anisotropy (Calabro & Vaina 2011) and vergence-comfort/minimum-disparity structural bias. Dissociation requires second observer with normal vergence.

4. **BothFar UNCUED reversal and F1×F4 dissociation** (UNCUED/structural arm is artifact-independent; F2 estimate suspect). The structural (UNCUED) and attentional (CUED) depth-plane preferences pull in opposite directions in BothFar, revealing two previously confounded mechanisms. The minimum-vergence-demand rule explains both the standard Far > Near (UNCUED) and the BothFar Less-Far > More-Far (UNCUED).

5. **UNCUED arm flatness**: depth-plane identity — even when fully available throughout a trial — provides zero benefit without the onset cue. Consistent across all depth experiments. Argues against preattentive depth segregation as a selection trigger. This result survives the artifact correction (artifact would have inflated, not deflated, UNCUED performance on swap trials, making flatness conservative).

**What VRDots does NOT yet reliably demonstrate (pending clean replication):**

1. **F2 depth-field cueing**: Pre-fix estimate +12.5pp*** collapses to +6.2pp n.s. in the first clean session. Currently unconfirmed. One more clean DecoupledDots_v2 session is the immediate priority.

2. **F1×F2 conjunction requirement**: Pre-fix estimate +32.7pp*** (DecoupledDots) collapses to +7.8pp n.s. This was the headline theoretical finding — that depth contributes only in conjunction with an onset cue, not independently. Currently unconfirmed. The theoretically critical claim that depth-plane identity is a constitutive feature of the attentional selection pointer awaits clean replication.

3. **ZdA/ZdB object-specific disruption**: The pre-fix finding that disrupting the *cued* object's depth membership specifically abolishes cueing (ZdA) while disrupting the distractor's enhances it (ZdB) is the most theoretically precise result in VRDots. Currently unconfirmed due to artifact contamination. Requires replication with post-fix assets at 50% swap rates.

**The provisional post-fix story:**

If F2 and F1×F2 do not recover to significance with more data, the VRDots contribution shifts from "depth-plane identity is required for sustained attentional selection" to a narrower but still novel set of findings: (1) robust surface-based selection from motion alone, (2) a Far > Near structural asymmetry that is entirely stereoscopic and structurally dissociable from attentional effects, and (3) a minimum-vergence-demand rule governing automatic (unattended) depth-plane weighting. These are meaningful, but the depth-object-continuity story that was previously the centerpiece awaits clean confirmation.

If F2 recovers at modest magnitude with more data — plausible given the +6.2pp point estimate — the story would be: depth contributes to selection but the effect is smaller than the pre-fix data suggested (~6pp, not 12pp), and the artifact-inflated +32.7pp conjunction was a methodological artifact, not a fundamental property of depth-based attentional selection.

**The VRDots project is, to the literature agents' knowledge, the first implementation of the Valdes-Sosa/Mitchell surface-selection paradigm with parametrically varied stereoscopic depth separation.** The critical question — whether depth-plane continuity is required to maintain an attentional pointer established by an earlier onset event — has no published precedent. The answer, once obtained in artifact-free data, will be novel regardless of direction.
