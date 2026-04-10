# Color Null vs. Point-Set Model — Theoretical Conjecture
*Literature agent — 2026-04-06*

---

## The Problem

The basic V1 point-set model (modeling_lit.md §6) treats motion direction, disparity, and color as co-equal feature dimensions. A single dot co-activates direction, depth, and color columns at its retinotopic location. Selection of surface A boosts all three dimensions via mutual excitation within the hypercolumn; feature-level identity spreads across the selected point-set. The model therefore predicts non-zero color-field cueing — if the translator matches the selected surface's color, performance should be better than when it mismatches.

The DecoupledDots data says: OR = 1.00, p = .994. Exact zero.

**The question is whether this kills the model or merely requires refinement.**

Below are four conjectures, arranged from least to most disruptive to the basic model structure.

---

## Conjecture 1 — The Read-Out Bottleneck (No Model Modification Required)

**Claim**: Even if color neurons are boosted within the selected point-set, a boosted color representation has zero leverage on direction-discrimination performance. The task taps the motion read-out, not the color read-out.

**Argument**: The performance measure in VRDots is translation direction (8-AFC). The final decision is made from MT/MST direction-tuned neurons. A boost to the color representation of surface A — blob neurons preferring C_A — does not improve motion detection, because blob neurons do not project to MT (they project to V2 thin stripes → V4 → IT). The boost exists but is inert with respect to the task.

Contrast with depth: disparity-selective neurons in V1 interblobs do project to MT (via V2 thick stripes). A depth boost improves figure-ground segregation at the level of the motion-processing stream — it directly affects the signal-to-noise of the direction discrimination. Color has no analogous shortcut into MT.

**Prediction under this account**: Color field-cueing should produce a behavioral null but a neural signal. An ERP or MEG measure would show enhanced color-area activity (V4 equivalent) for color-matched trials — the boost is there, just invisible to the behavioral read-out. This is testable.

**What this requires**: Nothing. The model is correct; the data reflects the task structure, not the selection mechanism.

**Limitation**: This account predicts the null cleanly but feels somewhat convenient. It also does not explain why the model was thought to predict a behavioral color effect in the first place — if the color read-out has no path to performance, why include color in the model at all? Partly because the Schoenfeld (2003, 2014) data show that color areas ARE activated during surface selection, establishing the neural reality of feature spreading. The model captures something real; the behavioral null reflects a task limitation.

---

## Conjecture 2 — The Selection Signal Is Color-Blind (Minor Model Modification)

**Claim**: The global feature-similarity gain (step 3 of the point-set model) is indexed to motion direction, not to color. Direction-tuned neurons in MT/V1 receive the broadcast; blob neurons do not. Color enters the selected point-set only indirectly, via lateral cross-column coupling that may be weak.

**Argument**: The delayed-onset event is processed by the magnocellular (M) pathway:
- M-cells are broadband — they do not carry chromatic information (sum L+M cone input, are not color-opponent)
- M-cells project to V1 layer 4Cα → layer 4B → MT
- The transient onset drives direction-selective V1 cells in layer 4B and interblobs

The global feature-similarity gain broadcast (Treue & MTT 1999) originates from direction-tuned MT neurons detecting the onset event and sending feedback to V1 neurons preferring the same direction. This feedback targets direction-selective interblob neurons — NOT blob neurons.

Blob neurons (color-selective, weak direction tuning) receive M-cell input only weakly, if at all, and are not part of the initial gain broadcast loop. They would only be boosted by the cross-column coupling within the hypercolumn — which, if weak, would give them negligible additional activation.

**Diagram of the proposed asymmetry**:

```
Onset event → M-cells → layer 4Cα → layer 4B (direction cells)
                                         │
                                   feature-similarity gain broadcast
                                         │
                              ┌──────────┴──────────┐
                              ▼                     ▼
                    V1 Direction column         V1 Disparity column
                    (interblob, 4B)             (interblob, layer 4)
                              │                     │
                         [strong]                [strong]
                              │                     │
                    V1 Color column
                    (blob, NOT directly in gain loop)
                              │
                         [weak — only via cross-column coupling]
```

**What this requires**: A minor modification to the model — the global gain broadcast is direction-indexed (and possibly disparity-indexed), not feature-agnostic. Color neurons are boosted only secondarily via lateral coupling. If that coupling is weak (anatomically motivated by blob/interblob separation), the net color boost is small.

This is not a fundamentally new idea; it is implicit in the model's own step 3: "ALL V1 neurons preferring θ_A get a non-linear gain boost." Blob neurons don't prefer θ_A (they prefer colors, not directions). So strictly read, the model already excludes blobs from the direct gain boost. The cross-column coupling is the only mechanism bringing color along.

**The crucial asymmetry — M-cells carry motion AND disparity, but not color:**

This is the sharpest version of Conjecture 2. The temporal onset drives M-cells (broadband, color-blind). M-cells are:
- Direction-sensitive (feed V1 layer 4B and MT)
- **Binocular** — they carry disparity information (compare L/R eye inputs, project to V1 binocular disparity cells)
- NOT color-opponent (sum L+M cones, do not carry chromatic signal)

Therefore the initial selection signal directly activates neurons tuned to both **local motion direction** and **disparity** at the same time, via the same pathway. Color neurons (P-cell / blob pathway) are not part of this broadcast.

This neatly explains the F2 > F3 asymmetry within the basic model:

```
Onset event → M-cells → V1 layer 4Cα/4B
                             │
                    activates:         does NOT activate:
                    ┌──────────────┐   ┌────────────────┐
                    │ Direction    │   │ Color (blobs)  │
                    │ Disparity    │   │ (P-cell input) │
                    └──────────────┘   └────────────────┘
                    direct activation   indirect at best
                    (same M-pathway)    (cross-column coupling)
```

Under this account, both F1 (dot cueing) and F2 (depth-field cueing) reflect the same direct M-pathway activation. F3 (color-field cueing) requires an additional step — mutual excitation spreading from the activated interblob neurons into blob neurons — which may be weak enough to produce a negligible or zero behavioral effect.

The fact that depth (disparity) and motion are in the same M-pathway channel is probably the primary reason F2 >> F3, not just the blob/interblob anatomy per se. The anatomy is downstream of this: M-cells project to the interblob/4B layers (which are disparity- and direction-tuned), not to blobs.

**This doesn't fully explain the depth vs. color difference** — if mutual excitation in the point-set is sufficient to spread the selection signal through the entire hypercolumn, both depth and color should eventually benefit. The remaining gap between F2 and F3 = 0 may require Conjecture 3 (depth as figure-ground) or Conjecture 4 (asymmetric coupling) to fully close.

**Prediction**: Performance should be worse when the whole FIELD changes color at tStart (because that creates a chromatic transient that directly drives blob neurons, potentially creating a competing selection signal). This would appear as a main effect of color-swap presence (C and CZ worse than N and Z overall), not as an F3 interaction. Look at the raw means in decoupled_dots_results.md: CUED+C = ~49%, CUED+N = ~43%. CUED+C is numerically BETTER, not worse. So color swapping in the CUED condition doesn't hurt — it might even slightly help (though not significantly). This argues against color swap creating a competing selection signal.

---

## Conjecture 3 — Depth Is Functionally Different: It Indexes Figure-Ground, Color Does Not (No Model Modification; Functional Distinction)

**Claim**: The F2 effect (+12.5pp) is not simply "the depth feature being boosted in the point-set." It reflects a fundamentally different mechanism — depth defines the figure-ground relationship at the population level, which directly determines whether the motion signal from the correct surface is extracted cleanly.

**Argument**: Two overlapping dot fields create a two-surface percept because their motion signals are locally unbalanced (Qian et al. 1994; Stoner & Albright 1990). Depth separation is a second, independent source of local imbalance — if dots in Field B are at a different disparity than Field A, V1 binocular neurons differentially respond, helping segment the two fields at the level of local feature processing (not just global attention). When the translator appears in the "right" depth plane (F2 ✓), the local unbalance signal that segments the two fields is maintained; when it appears in the "wrong" depth plane (F2 ✗), the translator has spuriously crossed into the other surface's depth stratum, creating a competing segmentation signal.

Color does not do this. Both fields share the same spatial region (overlapping dot fields), and the color of one field doesn't create a competing local motion-balance signal. Two overlapping dot fields, one red and one green, do not produce a different local motion-unbalance signal than two overlapping same-color fields — the segmentation cue for two-surface transparency is in the motion domain and the disparity domain, not the color domain.

Stated more directly: **depth modulates the quality of the two-surface stimulus representation itself**. Color is a label on top of that representation. When the depth plane identity is violated at tStart (F2 ✗), the surface representation is disrupted. When the color label is violated (F3 ✗), the surface representation is unchanged — just the label changed.

**Prediction**: Same-color experiments (both fields red) should have weaker overall cueing than two-color (red+green), because removing the color difference eliminates one segmentation signal. This is the Theeuwes et al. (1998) prediction: same-color design weakens depth-plane filtering. Mitchell et al. (2003) confirmed cueing survives same-color but they used same-color conditions at a single depth, not the orthogonal design. This is an important experiment VRDots could run — compare overall cueing magnitude between same-color and two-color DepthSwapCtrl conditions. The model predicts attenuation of overall cueing (not F2/F3 selectively) in same-color.

---

## Conjecture 4 — Blob/Interblob Anatomical Asymmetry in the Mutual Excitation Network (Moderate Model Modification)

**Claim**: The mutual excitation within the hypercolumn is not symmetric across all feature dimensions. The connections are stronger within the interblob network (motion ↔ disparity) than across the blob/interblob divide (color ↔ motion or color ↔ disparity). The model therefore needs to be "stream-aware" — not all feature dimensions are equally coupled nodes in the selection network.

**Anatomical basis**:
- **Interblob neurons**: orientation-selective, some direction-selective, disparity-tuned, project to layer 4B and V2 pale/thick stripes → MT dorsal stream
- **Blob neurons**: color-selective, weak/no orientation tuning, project to V2 thin stripes → V4 → IT ventral stream
- **Lateral connections within V1** (Gilbert & Wiesel 1983, 1989): predominantly within-layer, connecting neurons with similar orientation preferences. Interblob-to-interblob horizontal connections are well-documented and span up to ~6mm. Blob-to-interblob cross-connections are less specific and project more sparsely.

If the mutual excitation in the point-set model operates via these horizontal connections, then:
- Direction ↔ Disparity coupling: **strong** (both interblob, similar columnar architecture, both in the gain broadcast loop via M-pathway)
- Color ↔ Direction coupling: **weak** (blob to interblob is a functional boundary; color neurons are not in the direction-preference gradient, so direction-preference-based horizontal connections do not link them efficiently)

This predicts an intermediate color-field cueing effect when both color and depth differ — but empirically, color is zero and depth is +12.5pp. The model predicts F2 > F3, which matches, but F3 = 0 exactly might require the coupling to be functionally zero, not merely weakened.

**What this requires**: Explicit stream-specific topology in the mutual excitation network. The point-set model currently draws a symmetric hypercolumn with equal coupling between direction, color, and depth columns. This should be replaced with an asymmetric topology where direction ↔ disparity connections are strong and direction ↔ color (or disparity ↔ color) connections are absent or weak.

---

## The Drastic Modification — Color Is Not a Node in the Selection Network

If the conjunction of the above arguments holds, the model may require a more fundamental revision:

**Color is a read-out label, not a selection dimension.**

The point-set selection network — the network of mutually excitatory V1 neurons that forms, maintains, and updates the selected surface representation — operates within the motion/disparity subspace. It consists of direction-tuned and disparity-tuned interblob neurons connected by horizontal V1 connections and recurrent MT feedback. This network IS the selection mechanism.

Color (blob neurons) sits *outside* this network as a passive observer. When the selection network activates for surface A, the color that surface A's dots have is incidentally processed in the blobs at the same retinotopic locations, and there is sequential downstream activation (Schoenfeld 2003, 2014) — but this is feature *binding* (what color is the selected object?) not selection *contribution* (does having a color help select?). Color is added to the object representation after the fact, not used to drive or maintain selection.

Concretely:
- Selection is driven by: temporal onset (M-pathway transient) → direction-similarity gain → point-set mutual excitation among direction/disparity neurons
- Color is: passively registered in blob neurons during and after selection, but not a driver of the selection network

**This is a principled modification, not an ad hoc fix.** It reflects the known parallel-pathway organization of V1: the dorsal motion stream (interblobs → MT) handles selection and scene dynamics; the ventral color/object stream (blobs → V4 → IT) handles object recognition and feature binding. The selection mechanism lives in the dorsal stream. Color lives in the ventral stream. They interact at higher levels (the "what" of the selected object is eventually bound), but the selection machinery is exclusively dorsal.

**What this predicts:**
1. F3 = 0 for any color manipulation that doesn't also disrupt the motion/disparity structure (confirmed)
2. Color-only swap (C condition) does not disrupt cueing relative to N — confirmed (CUED+C ≈ CUED+N in DecoupledDots)
3. A pure color-onset cue (without temporal onset transient in the motion/M pathway) should produce weak or absent cueing — testable with a chromatic, isoluminant onset cue
4. **Depth-only swap (Z condition) DOES disrupt cueing** — confirmed, CUED+Z = +13pp vs CUED+N = +31pp
5. Color provides no protection against depth disruption — CZ ≈ Z in terms of cueing loss — partially confirmed in DecoupledDots (CZ = +6pp n.s., close to floor; Z = +13pp**)

**Possible route to color contribution**: If an observer were explicitly instructed to attend to the red surface (endogenous color selection), the ventral stream could be brought into alignment with the selection network via top-down feedback from IT/V4 → V1 blobs. This would give color an active role — but only when used as an endogenous cue, not as a passive field property. This is the endogenous color attention direction to pursue.

---

## Summary Table

| Conjecture | Model modification? | Predicts F3=0 | Key test |
|-----------|--------------------|-----------|----|
| 1. Read-out bottleneck | None | Yes — color is boosted but irrelevant | ERP/MEG: color areas should show cueing modulation despite behavioral null |
| 2. Selection signal is M-pathway (color-blind) | Minor — gain broadcast is direction-indexed | Approximately | Isoluminant onset cue → weak/absent cueing |
| 3. Depth = figure-ground signal; color = label | None (functional distinction) | Yes for color; explains why depth helps | Same-color vs. two-color comparison: overall cueing attenuation, not selective F3 change |
| 4. Blob/interblob asymmetric coupling | Moderate — stream-specific topology | Approximately (F2>>F3) | fMRI: color-area and MT-area modulation during surface selection |
| Drastic: Color is not a selection-network node | Substantial — color is downstream read-out, not driver | Yes, exactly | Endogenous color cue → color contributes when it IS the cue |

The most defensible position is that Conjectures 1 and 3 are simultaneously true (they are not mutually exclusive), giving a clean account of the exact null: color *is* boosted (neural reality; Schoenfeld 2003/2014), but the boost is irrelevant to direction discrimination (no path from blob to MT) AND color doesn't affect figure-ground (no impact on two-surface segmentation quality). The "drastic" framing synthesizes these into a principled stream-level account that the endogenous color attention work can directly test.

---

## DepthColorLinked Confirmation of F3 = 0 in the UNCUED Arm
*Added 2026-04-09*

The DepthColorLinked experiment (4 sessions, n=1024; `linkDepthColor=1`, ZdA+ZdB, Near=Red, Far=Green) provides an additional confirmation that is directly relevant to the M-pathway conjecture above.

In DepthColorLinked, the F2 factor captures continuity of *both* depth and color simultaneously — the two are perfectly confounded. Despite this, the UNCUED arm is flat across both conditions: ZdNoi+UNCUED = 21.9% correct vs. ZdCoh+UNCUED = 23.4% correct (1.5pp, n.s.; F2 main effect AME = −2.2pp, p = .635). When the coherent translator changes depth+color simultaneously (ZdCoh, UNCUED arm) vs. when the background changes depth+color (ZdNoi, UNCUED arm), performance is indistinguishable.

This is consistent with all four conjectures' prediction that **F3 = 0 for the UNCUED arm**, but it is most naturally interpreted under the M-pathway account (Conjecture 2) and the drastic formulation: the onset cue (F1) is necessary to engage the depth-identity mechanism. Without the temporal dot cue, swapping both depth and color of the coherent translator — a maximally disruptive change to both the dorsal-stream (depth) and ventral-stream (color) surface representations — has no measurable effect on performance. The UNCUED observer cannot exploit either depth or color continuity without first being directed to the correct object by the temporal onset transient.

This rules out any account in which color continuity alone — even when paired with depth continuity — provides a task-independent navigational signal for surface tracking. The conjunction (F1 AND depth continuity) is required; color continuity never contributes above zero, even when maximally available and confirmed by the UNCUED data.

The GLM2 result from DecoupledDots (color factor F3 = +0.9pp, p = .994) combined with DepthColorLinked's flat UNCUED arm creates a consistent picture: the point-set model's prediction of non-zero color-field cueing is empirically ruled out at both the within-model (DecoupledDots isolates color) and cross-model (DepthColorLinked maximizes color+depth together) levels.

---

*See also*: `modeling_lit.md §6` (point-set model), `color_cueing_review.md` (behavioral literature), `decoupled_dots_results.md` (data), `depthcolorlinked_results.md` (DepthColorLinked GLM)
