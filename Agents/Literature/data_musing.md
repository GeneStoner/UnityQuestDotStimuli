# VRDots Pilot — A Musing Document
*Last updated: 2026-04-02*

---

## The basic phenomenon

When two overlapping random-dot fields share the same aperture and one field has a delayed onset, the observer is much more likely to correctly report the translation direction of the delayed-onset field. We call this the **temporal onset cueing effect**. It is large (+30–45pp) and robust in the absence of stereo depth, consistent with prior work on object-based attention using overlapping dot surfaces.

The observer does not perceive the dots differently — they report a direction. The cueing effect means: the delayed-onset field's translation direction is reported correctly more often. This is a behavioral index of selective processing, not a statement about dot motion per se.

---

## What adding stereo depth does

Introducing a 0.05m depth separation (Near=1.975m, Far=2.025m) dramatically reshapes the effect — but not uniformly.

**Overall binocular cueing in the no-swap condition drops from ~+33pp to +13pp.** Two explanations are not mutually exclusive: (a) depth complexity increases task difficulty; (b) the Near plane is partially canceling the Far plane advantage in the average. Both are probably true.

**The average conceals a striking dissociation:**
- Far plane: ~+56pp*** — as large as the no-depth baseline
- Near plane: ~+12pp n.s. — essentially flat

At the larger 0.10m separation (DepthBaseline sessions, March 25), the Near plane doesn't just flatten — it **reverses**. UNCUED outperforms CUED by up to −47pp***. The Far plane simultaneously shows +60pp***. These are large, bidirectional effects within the same session.

The reversal scales with depth separation: strong at 0.10m, attenuated at 0.05m, absent monocularly. This strongly implicates genuine disparity processing rather than noise or a monocular cue.

**Tentative interpretation**: Near-plane stimuli carry a default attentional priority — possibly related to looming or binocular prominence. When the *UNCUED* field is at Near depth and translates, its salience overrides the temporal onset cue. Far-plane translation faces no such competition and is enhanced. The temporal cue and near-plane salience are in opposition, and near-plane salience wins at large enough depth separations.

This is not anticipated by prior object-based attention literature and may be a novel finding.

---

## DepthParam — parametric depth separation (2026-04-02)

Four sessions run in a single sitting: 0.03, 0.05, 0.10, 0.15m separation. R/G balanced colors. No swaps. n=32/cell per session. Second sessions planned. Full details in `depthparam_results.md`.

### The cueing effect as a function of depth separation

| Depth sep | Near cueing Δ | Far cueing Δ | Overall |
|-----------|--------------|-------------|---------|
| 0.03 m | **+12.5pp** | +46.9pp | +29.7pp |
| 0.05 m | −9.4pp | +46.9pp | +18.8pp |
| 0.10 m | −21.9pp | +46.9pp | +12.5pp |
| 0.15 m | −25.0pp | +56.2pp | +15.6pp |

### What this tells us

**Far cueing is essentially depth-invariant and large.** CUED Far is 84–91% at all separations. Even at 0.03m — where the depth planes are barely perceptible — Far cueing Δ is already +47pp. The temporal onset cue and Far depth are synergistic and do not require large disparities to interact.

**The Near reversal has a threshold around 0.03–0.05m.** Below this the cueing effect is positive (normal direction). Above it, it reverses, and by 0.10m it has saturated at approximately −22 to −25pp. UNCUED Near performance (no temporal cue, near plane) rises from 50% at 0.03m to 75% at 0.10m and stays there — the near plane without the temporal cue becomes increasingly discriminable as disparity grows.

**CUED Near decreases monotonically to chance.** At 0.15m, the translating near-plane dots with the temporal cue are at exactly 50% — indistinguishable from chance. The temporal cue provides zero benefit for near-plane translation at large disparities.

**The overall effect is misleading.** The aggregate cueing effect (overall Δ) drops from +30pp to +13pp as depth increases, which could be interpreted as depth harming cueing. In reality, Far cueing is unchanged and Near cueing has reversed — the average reflects cancellation of two large bidirectional effects, not a global reduction.

### A second possible mechanism: fixation-depth attentional bias

The observer noted during testing that fixating the fixation cross pulls attention naturally toward the fixation plane and rearward — objects in front of fixation (Near plane) feel unattended by default. This is consistent with known vergence-driven depth attention: the attentional spotlight in depth is asymmetric around the fixation point, extending more readily to far depths than near ones. If true, this provides a second account of the Near reversal that is independent of depth-plane grouping: the near plane is simply in the attentionally suppressed region relative to the fixation plane, and larger disparities push it further into that region.

These two accounts — (1) near-plane salience/looming priority and (2) fixation-coupled attentional depth bias — make different predictions about what happens when fixation distance is manipulated. If the reversal flips when the fixation plane is moved to near depth, account (2) is supported. If it remains tied to absolute near/far regardless of fixation, account (1) is supported. A direct test is feasible.

---

## The color confound — broader than it first appears

Every experiment prior to DepthSwapCtrl — including the no-depth baselines (Jan 2026, March 23) and the DepthBaseline depth sessions (March 25) — used a balanced R/G design: one field red, one field green, counterbalanced across trials (confirmed from TSV `DelayedFieldColor` column). DepthSwapCtrl used both fields red throughout (`balanceDelayedFieldColor=false`).

This means color is a confound in *every* cross-experiment comparison:

- The drop from +33–45pp (no-depth, R/G) to +13pp (DepthSwapCtrl bino N, both red) reflects both the addition of stereo depth **and** the removal of color as a segmentation cue. We cannot attribute the reduction to depth alone.
- The DepthBaseline Near reversal (0.10m, R/G) cannot be straightforwardly compared to DepthSwapCtrl's Near/Far asymmetry (0.05m, both red) — two things changed.

Within DepthSwapCtrl, color is held constant across all conditions, so all ZdA/ZdB/N comparisons, Near/Far contrasts, and binocular/monocular comparisons are internally valid. The problem is only with cross-experiment comparisons.

Color provides an additional segmentation cue for field identity. Without it (DepthSwapCtrl), temporal onset and disparity are the only cues — arguably a cleaner design for the research question. But the earlier large effects (especially the Near reversal at 0.10m) might be partly inflated by color-reinforced segregation. Alternatively, color may not matter much for attentional selection and the effects are primarily driven by onset timing and depth. A direct experiment — same parameters, same depth, same everything, just both-red vs R/G — would answer this.

---

## The depth-swap results

ZdA and ZdB differ only in whether the **coherent translator** changes depth plane at tStart (ZdA: yes; ZdB: no). They are matched for number of dot depth-swaps (2 each) and rotation reversals (2 each).

| Condition | Binocular Δ | Monocular Δ |
|-----------|-------------|-------------|
| N (no swap) | +13pp * | +7pp n.s. |
| ZdA (cued translator changes plane) | +16pp * | +1pp n.s. |
| ZdB (companion changes plane, cued stays) | +20pp ** | +11pp * |

**ZdB > N binocularly**: having the non-coherent companion move INTO the cued plane at tStart *enhances* cueing above the no-swap baseline. This is not disruption — it is enhancement. The most natural account: when the companion leaves its original plane, the cued depth plane becomes more homogeneous (only coherent motion present), sharpening attentional selection. Alternatively, the unattended surface is more effectively suppressed when the two surfaces are clearly segregated.

**ZdA ≈ N binocularly**: cued translator changing planes is costly but the temporal onset advantage survives. The cueing effect is more robust than a strict object-continuity account would predict.

**The monocular dissociation is the key result**: ZdA collapses to +1pp n.s. while ZdB survives at +11pp*. Since the two conditions are identical monocularly except for which dots undergo reversals, the collapse specifically implicates the depth-plane change of the coherent translator. However, a geometric confound exists: in ZdA, the coherent translator undergoes a small positional shift (up to ~5 arcmin) when it changes depth at tStart, because the vergence angle has changed. This spurious spatial displacement could partially contribute to ZdA's monocular collapse, but is unlikely to explain it fully.

---

## What the three-factor analysis says

Marginal chi-square across all 10 sessions:

| Factor | Binocular (n=768) | All mono (n=1153) | Verdict |
|--------|-------------------|-------------------|---------|
| 1. Dot cueing (CUED vs UNCUED) | +16.4pp *** | +6.3pp * | Survives monocularly, attenuated ~60% |
| 2. Depth-field cueing (same vs diff plane) | +6.0pp † | +5.6pp † | Survives monocularly marginally |
| 3. Near/Far (Far vs Near) | +10.7pp ** | −0.4pp n.s. | Entirely stereoscopic |

Factor 3 being entirely absent monocularly is strong evidence it requires genuine disparity, not monocular depth cues. Factors 1 and 2 surviving monocularly (at reduced levels) suggest a non-stereoscopic component — possibly temporal grouping, or rotation reversals in ZdA/ZdB driving Factor 2 indirectly.

---

## Motion and dot swap history (March pre-pilot)

- **Motion swap**: reduces cueing ~50% (+29pp → +16pp n.s.) but does not eliminate it. The cued translator can change motion type mid-trial and the temporal onset advantage partially survives. The cue operates on object identity, not motion feature continuity.
- **Dot50 swap**: no effect (+29pp → +34pp n.s.). Swapping half the dots mid-trial leaves cueing intact. The attentional grouping that supports cueing is more abstract than dot-level identity or spatial layout continuity.

---

## Monocular data: reliability and interpretation

R-eye sessions are weaker overall (35.4% correct) than L-eye (44.3%) and binocular (44.9%). The R-eye shows a cardinal heading deficit (30.8% correct for cardinal vs 39.9% for diagonal), the reverse of binocular and L-eye. Response bias patterns shift substantially and inconsistently across viewing conditions. The most parsimonious account: the response wheel appears rotated or distorted under monocular viewing, perhaps due to IPD geometry or lens distortion when one eye is covered.

This means monocular cueing estimates conflate perceptual signal with response-stage artifacts. The monocular effects are probably conservative — true perceptual signal may be larger than what percent correct captures. A neural measure (ERP) would bypass the response stage entirely.

---

## The ERP thought

If the attentional enhancement operates at the object level, it should boost neural responses to *all* motions of the cued field — not just the coherent translation. In ZdA/ZdB, the rotation reversals of the cued field at tStart should generate a large direction-change VEP (motion-reversal ERP), enhanced CUED > UNCUED, detectable even on incorrect trials. The delayed-onset ERP at frame 56 (Field B appearance) should likewise be enhanced for CUED.

This is appealing because: (a) it bypasses response bias completely; (b) the motion-reversal VEP is a robust, well-localized signal; (c) it would provide evidence of object-level gain even on trials where the subject fails to identify the heading — which is a qualitatively different claim from percent correct. The caveat: if non-coherent and reversal motions are equally enhanced, it complicates what exactly the cueing effect indexes.

---

## Open puzzles worth musing over

1. **Why does the Near plane reverse at large depths?** The looming/salience account is plausible but post-hoc. Is there a cleaner mechanistic story? Does it predict anything about the shape of the reversal curve as depth separation increases?

2. **Why does ZdB enhance above the N baseline?** Companion moving into cued plane should be *disruptive* on a naive account (more motion in the cued plane). Instead it helps. This implies that what matters is the *clarity of the depth-plane boundary*, not the absolute content of the cued plane.

3. **What is depth-field cueing (Factor 2) tracking monocularly?** Without disparity, the "same plane" vs "different plane" distinction is invisible. Yet the effect persists at marginal significance (†). Either the rotation reversals in ZdA/ZdB are carrying this signal, or there is a genuine non-stereoscopic component to depth-field cueing.

4. **Is the ~60% attenuation of dot cueing monocularly real or artifactual?** If response distortion accounts for part of the monocular deficit, the true perceptual attenuation could be smaller. Or there is a genuine stereoscopic component to the dot cueing effect itself.

5. **The color confound revisited**: if we run a parametric depth-separation experiment with both fields red throughout, and the Near reversal curve holds, we have a clean result. If it doesn't — if it requires color redundancy to emerge — that tells us something important about how depth-plane segmentation interacts with color in attentional selection.

6. **n=1 throughout**: the data pattern is coherent and internally consistent across 10 sessions, but all of it is from one observer. Session variance is large (single binocular ZdB sessions range from +3pp to +56pp). The findings could be idiosyncratic. Replication with a second observer is the single most important next step.

---

## Summary of summaries

The temporal onset cue is real, large, and object-level. Adding stereo depth doesn't weaken it — it redirects it. The Far plane gets a huge boost; the Near plane at large depths gets actively reversed. The reversal is the most theoretically interesting finding and the least expected. The depth-swap results show that what matters is the continuity of the cued surface through the depth dimension, with ZdB demonstrating that cleaner segregation actually helps. The experiment is clean enough to be credible; it is small enough (n=1) that every major finding needs replication before anyone bets on it.
