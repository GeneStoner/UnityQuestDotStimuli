# Far > Near Cueing Asymmetry: Revised Account

**Date:** 2026-04-11 (revised from original 2026-04-11 draft)
**Status:** PROVISIONAL — for review and dispute by GS
**Supersedes:** Original "beyond account" draft; incorporates fixation_plane_hypothesis.pdf (programming agent, 2026-04-11)

---

## Summary

**Observer-specificity flag**: All Far > Near findings should be treated as potentially observer-specific until a second observer with normal vergence replicates the asymmetry. Observer GS has clinically documented esophoria (prism-corrected glasses, not worn in VR), providing a specific sensory mechanism for the Far > Near asymmetry that is entirely independent of attentional or general neural-population accounts. See Section 2b for full discussion.

The Far > Near cueing asymmetry in VRDots is now better understood as having a **structural, trial-independent component** — present in both CUED and UNCUED arms — rather than being primarily a cue-locked attentional effect. The fixation-plane hypothesis (GS/programming agent, 2026-04-11) offers the more parsimonious account: the fixation plane functions as a persistent depth anchor, and attentional weight (or sensory quality) is preferentially extended toward objects at greater depth than fixation. This is present on every trial regardless of which field was cued. A cue-locked "beyond the attended object" mechanism may additionally contribute but is not the primary driver.

---

## 1. The Key Diagnostic: Far > Near in the UNCUED Arm

**This is the decisive datum.** If the Far advantage were purely cue-locked — arising only when the observer attends to a depth plane and attention spills beyond it — the UNCUED arm should show no Far > Near effect. Without an onset cue designating a depth plane, there is no attended plane to extend from.

**Observed data (existing sessions):**

| Experiment | CUED Far−Near | UNCUED Far−Near | F1×F4 interaction |
|---|---|---|---|
| DepthSwapCtrl (bino, n=192/arm) | +8.3pp n.s. | +10.4pp n.s. | ~0 (UNCUED slightly larger) |
| DepthColorLinked (n=128/arm) | +11.7pp† | +5.5pp n.s. | small positive |

**Interpretation:** Far > Near is present in UNCUED in both experiments. The F1×F4 interaction is near zero — the onset cue does not substantially amplify the Far advantage. This pattern:

- **Falsifies** the purely cue-locked "beyond the attended plane" account as the sole mechanism
- **Supports** a structural, trial-independent Far bias (fixation-plane or sensory)
- Is consistent with both attentional and sensory versions of the fixation-plane hypothesis

**Correction of earlier error.** The original draft described "UNCUED flatness" as a weakness of the beyond account. This was a category error. The UNCUED arm IS flat for F2 (depth-field cueing — whether the translating field matches the delayed field's depth), but NOT for F4 (Near vs Far depth plane of the translator). These are different factors. The F4 Far advantage in UNCUED is positive and consistent across experiments.

---

## 2. The Fixation-Plane Hypothesis (Primary Account)

**Core claim** (GS/programming agent, 2026-04-11): In stereoscopic VR, the fixation cross is rendered at a specific virtual depth. The two dot fields flank this depth: the Near field carries crossed disparity, the Far field carries uncrossed disparity. Attentional weight — or perceptual signal quality — is preferentially extended *behind* the fixation plane (toward Far) on every trial, regardless of cueing. This produces a standing Far advantage that is structural, not cue-locked.

**Why this is the better primary account:**
- Predicts Far > Near in UNCUED ✓
- Predicts near-zero F1×F4 interaction ✓ (or a small positive interaction if the onset-cue mechanism adds to it)
- Predicts monocular collapse (disparity required for crossed/uncrossed distinction) ✓
- Does not require any "attended object" logic or trial-by-trial cue processing

**Two sub-versions:**

### 2a. Attentional version
The fixation point functions as an attentional anchor in depth. Attention extends preferentially behind the fixation plane — toward far-tuned space — just as it may extend behind an attended object. This is a structural property of how depth-attention is organized around the fixation point in stereoscopic viewing.

### 2b. Sensory/physiological versions (cannot yet be ruled out)
Two purely sensory accounts make the same predictions:

1. **Vergence-comfort confound:** Uncrossed disparity (Far) is more stably fused than crossed disparity (Near) in VR, especially given the vergence-accommodation conflict inherent to VR displays. Far dots may simply be cleaner perceptually, independently of any attentional mechanism.

2. **Neural population asymmetry:** In V1 and MT, far-tuned (uncrossed disparity) neurons may be somewhat more numerous or higher signal-to-noise than near-tuned neurons at moderate disparities (consistent with Calabro & Vaina 2011 framework). If the Far field drives a more reliable neural response, direction discrimination would be easier there without any attentional mechanism.

Observer GS has a clinically documented tendency toward esophoria (over-convergence) and wears prism-corrected glasses, which are not worn during VR sessions. This provides a specific observer-level mechanism for the vergence-comfort confound: crossed disparity (Near plane) requires convergence relative to fixation, which may be perceptually unstable for an esophoric observer whose uncorrected vergence system is already under strain. Uncrossed disparity (Far plane) requires divergence — the direction prism correction facilitates — and may be more stably fused. The entire Far > Near asymmetry could in principle reflect this individual sensory difference rather than any attentional or general neural-population mechanism. This makes the second-observer experiment the single highest priority before drawing general conclusions about depth attention from the Far > Near asymmetry.

Neither sensory account can be ruled out with current data. The fixation-plane label covers all three sub-versions until dissociation experiments distinguish them.

---

## 3. The Cue-Locked "Beyond the Attended Object" Mechanism (Secondary Account)

**Core claim** (prior discussion): When the observer attends to a depth plane via the onset cue, attentional weight extends preferentially beyond that plane (further from observer). In a two-plane display, this dilutes Near-plane selectivity (spillover to Far) and concentrates Far-plane selectivity (nothing beyond).

**Current status:** The near-zero F1×F4 interaction means this mechanism, if present, contributes minimally beyond the standing fixation-plane bias. It cannot be ruled out — the small positive F1×F4 in DepthColorLinked (+11.7pp CUED vs +5.5pp UNCUED) is weakly consistent with an additive cue-locked component. But it is not the primary driver.

**The additive structure** (from fixation_plane_hypothesis.pdf):
- CUED·Far: fixation-plane + onset-cue both favour Far → maximum advantage
- UNCUED·Far: fixation-plane alone → moderate advantage
- CUED·Near: onset-cue favours Near, fixation-plane favours Far → partial opposition → intermediate
- UNCUED·Near: neither mechanism → worst performance

This ordering is observed in DepthColorLinked: CUED·Far (+35.9pp) > CUED·Near (+24.2pp) ≈ UNCUED·Far (+12.5pp) > UNCUED·Near (+7.0pp). Broadly consistent, though cells are underpowered.

---

## 4. What Remains of the "Beyond" Logic

The directionality claim — that attention/bias extends *behind* the fixation plane rather than *in front* — still requires explanation. Three accounts:

1. **Attentional topology** (original beyond account): The visual system deploys attention asymmetrically in depth, extending more weight toward far space. Ecological motivation is weak (near space is generally more actionable), so this likely requires a transparency/superimposition-specific framing (see Section 5).

2. **Vergence dynamics:** VR fixation at 2m means uncrossed disparities (Far) are closer to the resting vergence posture. The visual system may "reach" more easily toward Far because vergence is less strained there.

3. **Neural architecture:** If far-tuned disparity units have higher baseline sensitivity (Calabro & Vaina 2011), the system naturally "sees more" at Far independently of where attention is directed.

**Important:** points 2 and 3 do not require any attentional mechanism. If one of them is correct, this is entirely a sensory story, not an attentional one. This distinction matters for what the finding tells us about depth-based attention.

---

## 5. Complications for the Attentional Interpretation

### 5a. Peripersonal space and looming
Near > Far dominates in many naturalistic contexts (peripersonal space, looming/approach responses). However, these involve action-relevant stimuli at centimeter scales; VRDots operates at 2m with a 5cm depth offset in depth-discrimination context. The peripersonal literature does not directly contradict the fixation-plane account — but it establishes that Far-bias is not a general property of depth attention. It must be specific to stereoscopic, superimposed displays, or to displays flanking a fixation point.

### 5b. Andersen & Kramer (1993): Near > Far in IOR
Near > Far IOR would contradict an attentional version of the fixation-plane hypothesis, since IOR should reflect the aftereffects of attentional deployment. However, IOR and the VRDots cueing effect measure different constructs. They can dissociate without contradiction.

### 5c. DepthParam parametric trend
Near cueing becomes more negative as depth separation increases (Near: +12.5pp at 0.03m → −9.4pp at 0.05m → −21.9pp at 0.10m → −25.0pp at 0.15m). If the fixation-plane bias is sensory/vergence-based, it should strengthen with disparity magnitude — consistent with this trend. The Calabro & Vaina cross-talk account predicts the opposite (Near should improve as planes separate, since cross-talk decreases). The data therefore run *counter* to the Calabro & Vaina account and are at least directionally consistent with a fixation-plane or structural account. (Underpowered: n=32/cell.)

---

## 6. Critical Tests

### Test 1: F1×F4 in GLM with full DecoupledDots dataset [can do now]
The GLM2 F1×F4 term directly quantifies whether the Far advantage is amplified by the onset cue. Near-zero → fixation/sensory mechanism dominant. Positive → additive cue-locked component. This is available in existing data.

### Test 2: Fixation-depth manipulation [new experiment, clean causal test]
Render the fixation cross at Near-plane depth for one block, Far-plane depth for another. Everything else unchanged.
- Fixation-plane hypothesis predicts: Far advantage should *weaken* when fixation moves to Far depth (Far is no longer behind fixation — it IS at fixation). May reverse when fixation moves beyond Far.
- Cue-locked beyond account predicts: no change (onset cue determines the attentional plane, not fixation).
- Sensory/vergence account predicts: the advantage should track uncrossed vs crossed disparity relative to the new fixation distance, potentially reversing.

This is the cleanest available causal test. Can be implemented as an extra parameter in DepthSwapCtrl (no new experiment spec required).

### Test 3: SOA manipulation [already planned]
At very short SOA, the onset-cue attentional representation has not matured. If the Far advantage is structural (fixation-plane), it should be present at all SOAs including near-zero. If it requires cue maturation, it should be absent at short SOA. Crossing SOA × Near/Far decomposes the two contributions.

### Test 4: DepthParam with adequate power [n≥128/cell]
Currently n=32/cell is insufficient to evaluate the parametric shape. The question is whether Near cueing continues to worsen at 0.15m+ or plateaus. If the structural/vergence account is right, the Near deficit should grow monotonically with disparity (more vergence strain at larger crossed disparity). If the Calabro & Vaina account is right, Near should improve at large disparities (less cross-talk).

---

## 7. Summary Assessment

| Criterion | Fixation-plane / sensory | Cue-locked beyond-account |
|---|---|---|
| Far > Near in UNCUED | **Predicted ✓** | Not predicted ✗ |
| Near-zero F1×F4 interaction | **Predicted ✓** | Predicts positive F1×F4 ✗ |
| Monocular collapse | Predicted ✓ | Predicted ✓ |
| DepthParam Near worsens with separation | Consistent ✓ | Inconsistent (Calabro & Vaina version) |
| Requires attentional mechanism | Not necessarily | Yes |
| Key test | Fixation-depth manipulation | SOA manipulation |

**Bottom line.** The fixation-plane hypothesis — in either its attentional or sensory sub-versions — is the better primary account of the Far > Near asymmetry. The cue-locked "beyond the attended plane" mechanism may contribute additively but is not the primary driver. The most important immediate action is to extract the F1×F4 GLM coefficient from the existing DecoupledDots data. The most important new experiment is the fixation-depth manipulation.

---

*Revised by Literature Agent incorporating fixation_plane_hypothesis.pdf (GS/programming agent, 2026-04-11) and UNCUED Near/Far data analysis. Original beyond-account draft superseded.*
