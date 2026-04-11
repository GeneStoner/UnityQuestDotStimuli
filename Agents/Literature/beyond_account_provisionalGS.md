# Provisional Account: The "Beyond" Attentional Gradient in Depth and the Far > Near Cueing Asymmetry

**Date:** 2026-04-11
**Status:** PROVISIONAL DRAFT — for review and dispute by GS
**Author:** Literature Agent

---

## Summary

The Far > Near cueing asymmetry in VRDots is consistent with a proposal that attentional gradients in depth are not symmetric: when an observer selects a depth plane, attention spreads preferentially *beyond* the selected surface (further from the observer) rather than in front of it. In a two-plane display, this asymmetry degrades Near-plane selectivity (spillover reaches Far) while leaving Far-plane selectivity intact (nothing lies beyond Far). A secondary account — MT anisotropy across preferred disparities — offers a neurally grounded alternative that does not invoke attentional gradients at all. Both accounts make contact with the data but neither is established. This note lays out the argument, the supporting and opposing evidence, and the critical tests that would distinguish them.

---

## 1. The Core Claim

**Established finding:** In VRDots binocular conditions, cueing performance is substantially better when the target surface is in the Far depth plane than when it is in the Near plane. This is the Far > Near asymmetry.

**Theoretical inference (the beyond account):** Attention deployed to a depth plane does not form a sharp boundary at that plane; it leaks into adjacent depth. The leak is directional: it extends preferentially *away from the observer* (beyond the attended surface) rather than toward the observer. This directional anisotropy has been proposed, though not firmly established, for stereoscopic attention gradients.

**The specific consequence for VRDots:** When the observer attends to the Near plane, some attentional weight flows to the Far plane, reducing the effective selectivity for Near-plane motion. When the observer attends to the Far plane, there is no plane beyond it in the display, so attentional resources stay concentrated there. Far-plane attending is therefore more efficient than Near-plane attending, yielding a higher cueing signal.

This is a clean prediction that follows from the gradient asymmetry premise without requiring any additional assumptions about the stimuli. It does not require Near stimuli to be harder to see, or the planes to be perceptually unequal in any other way.

---

## 2. VRDots Evidence Bearing on the Account

### 2a. The Far > Near asymmetry itself

**Established finding.** The asymmetry is present across multiple experiments:

- DepthBaseline (0.10m, S1): Near = −4.9pp, Far = +59.4pp; DepthBaseline (S2): Near = −46.9pp, Far = +65.1pp
- DepthSwapCtrl (binocular N condition): Near = +20.8pp*, Far = +47.9pp***
- DepthColorLinked combined (n=512): Far > Near by +8.6pp* across sessions
- DepthParam at 0.10m: Near = −21.9pp, Far = +46.9pp; at 0.15m: Near = −25.0pp, Far = +46.9pp

The Far advantage is large and consistent in binocular conditions. This is the primary datum the account must explain. It qualifies as a reliable empirical regularity, not merely a single noisy observation.

### 2b. Monocular collapse

**Established finding.** The Far > Near asymmetry disappears under monocular viewing. Pooled monocular data (n=769, DepthSwapCtrl) show near-zero Near/Far asymmetry (+1.2pp n.s., compared to +9.4pp† binocular). This implicates binocular disparity as the operative variable — a surface that is "Far" relative to fixation only exists as a distinct depth entity when the visual system has disparity information.

**Relation to the beyond account.** The beyond account, as stated, invokes attentional gradients along the depth axis. If depth is represented via disparity, removing disparity (monocular viewing) should eliminate the depth gradient itself. So the monocular collapse is *consistent with* the account — but it is also consistent with any depth-specific account, including the Calabro & Vaina alternative (Section 6). The monocular result does not uniquely support the beyond account; it rules out purely featural or 2D explanations.

### 2c. DepthParam: does the advantage shrink at larger separations?

**Established finding (descriptive).** DepthParam tested four depth separations (0.03, 0.05, 0.10, 0.15m) without any depth swap. Far cueing appears saturated across all depths at ~+47pp. Near cueing is negative at 0.05m and above, and weakly positive at 0.03m. The Far advantage therefore appears maximal at moderate and large separations, with no clear shrinkage as planes become more segregable.

**Tension with the beyond account.** The beyond account predicts that as plane separation increases, attentional spillover from Near to Far should decrease — because the planes become more distinct and the gradient should not reach as far. This predicts the Near cueing deficit should shrink (or the Far advantage should shrink) at larger separations. The DepthParam data do not show this: the Far advantage appears *stable or increasing* across 0.05–0.15m. This is a genuine tension. It could mean: (a) the gradient extends much further than 0.15m and is never reduced within the tested range; (b) the Far advantage arises from a different mechanism; or (c) n is too low per cell (n=32) to detect a parametric trend.

This tension is not a falsification of the account — it is a failure to find the predicted parametric pattern with limited data. But it should be treated as a warning.

### 2d. UNCUED flatness

**Established finding.** UNCUED performance is near chance (12–25%) across Far and Near in most experiments. There is little or no Far > Near asymmetry in UNCUED conditions.

**A weakness of the pure beyond account.** If Far-plane attention is more concentrated because nothing lies beyond it, then any mechanism that directs attention to Far — including the temporal onset cue — should be more efficient for Far. But the account does not clearly predict that UNCUED-Far should be worse than UNCUED-Near, or that UNCUED conditions should be flat. In fact, one might expect that an observer who happens to direct some attention to the Far plane (via spontaneous or residual attention) would show a small Far advantage even without a dot-onset cue. The data do not show this: UNCUED conditions are flat. This suggests that depth-selective attention to Far is not spontaneously engaged — it requires the F1 dot-onset cue to trigger. The beyond account says nothing specific about how depth attention is initiated, only about its spatial properties once active. The UNCUED flatness is not fatal to the account, but it means the account only predicts an asymmetry conditional on the F1 cue triggering depth-selective attention. That is an additional assumption that should be made explicit.

---

## 3. Supporting Evidence from the Broader Literature

### 3a. Parks & Corballis (2006) and Caziot et al. (2023)

**Literature finding.** Parks & Corballis (2006) reported a Far > Near advantage in stereoscopic attention or IOR tasks (precise characterization depends on the paradigm; see depth_attention_review.md for details). Caziot et al. (2023) also report evidence consistent with far-plane selectivity advantages in stereoscopic cueing. These results are consistent with the idea that far-plane attending is more efficient in superimposed stereo displays.

**Caveat.** These are not the same paradigm as VRDots. The generalizability from static spatial cueing to dynamic motion coherence detection is not guaranteed. They are suggestive, not confirmatory.

### 3b. Amodal completion logic (Nakayama, Shimojo & Silverman 1989)

**Literature finding.** Nakayama et al. showed that surfaces perceived to lie behind an occluder receive amodal completion — the visual system treats them as complete even where they are not directly visible. This is a well-established result. It implies that the visual system assigns objects in the "behind" role a special representational status.



**Theoretical inference (extension to transparent displays).** In VRDots, the two dot fields are transparent and fully visible — neither physically occludes the other. However, the visual system may still assign a perceptual depth-ordering (Far behind Near), and the Far surface may be processed under completion-related mechanisms even without actual occlusion. If these mechanisms carry attentional weight toward the far surface, a Far preference in attention would follow.

**Speculative.** The extension from occluded surfaces to fully visible transparent surfaces is not established. Nakayama et al.'s result concerns physically occluded stimuli. Applying it to VRDots requires assuming that transparent superimposition activates the same completion mechanisms, which has not been directly demonstrated. Flag this as speculation.

GS comments: I don't buy that this has much bearing on depth-plane attentional weighting. 


---

## 4. Evidence Against or Complicating the Account

### 4a. Peripersonal space: Near > Far for action and defense

**Literature finding.** A substantial body of work (Làdavas and colleagues; Maravita and colleagues; Fogassi et al.) demonstrates that space near the body — peripersonal space — is neurally privileged. Near-space stimuli evoke faster defensive responses, stronger multisensory integration, and more efficient visuomotor coupling than far-space stimuli. This is the opposite of the beyond account's prediction for general depth attention.


**Evaluation.** The peripersonal literature concerns primarily action-relevant stimuli (threats, objects to reach) at distances from the body measured in centimeters to ~1 meter, with specific body-part reference frames. VRDots stimuli are at 2.0m, well beyond peripersonal space by most definitions, and involve direction discrimination, not reaching or defense. The Near/Far distinction in VRDots (5cm depth offset at 2m) is also qualitatively different from the Near/Far distinction in peripersonal space research (centimeters from the hand vs. arm's length away). The peripersonal literature does not directly contradict the beyond account for this paradigm, but it establishes that Near > Far is the dominant pattern in the broader ecological context. The burden is on the beyond account to explain why transparent stereoscopic displays reverse this.

GS is fixation plane controlled for in these studies?  if not, relevance is marginal and speculative.


### 4b. Looming and approach responses

**Literature finding.** Stimuli that approach the observer (looming) are processed with high priority across species, triggering defensive responding and attentional capture. Near stimuli are ecologically more salient as potential threats.

**Evaluation.** Same caveat as 4a. In VRDots the Near plane is static in depth during the trial (depth separation is constant; the dots translate laterally). The two planes do not differ in looming properties. This argument does not directly apply to the VRDots paradigm.

GS is fixation plane controlled for in these studies?  if not, relevance is marginal and speculative.



### 4c. Andersen & Kramer (1993): Near > Far in IOR

**Literature finding.** Andersen & Kramer (1993) reported a Near > Far advantage in their inhibition-of-return paradigm using stereoscopic displays. This is a direct contradiction of the beyond account if the IOR task is taken as measuring the same attentional selectivity as VRDots cueing.

**Evaluation.** IOR reflects the aftereffects of attention (inhibition at previously attended locations), not the initial deployment of attention. It is not necessarily the same construct as the cueing advantage measured in VRDots, which reflects successful selection during the translation window. A Far > Near advantage in initial selection could coexist with a Near > Far pattern in IOR without contradiction. However, Andersen & Kramer's result is a warning that depth attention is not uniformly Far-biased, and it should not be dismissed.
if not, relevance is marginal and speculative.

GS -- have to look at this study.  

### 4d. Evolutionary/ecological argument

**Theoretical.** The general ecological argument for Near > Far attentional weighting is strong. Objects nearby are more actionable and more dangerous. A visual system that allocated more attentional resources to far depth — at the expense of near depth — would be at a disadvantage in naturalistic environments. The beyond account would need to be a narrow, display-specific phenomenon (see Section 5) rather than a general property of depth attention to be ecologically coherent.

GS -- yes but we are talking about near vs far with regard to an attended plane not near vs far in the absolute.  but def worth weighing

### 4e. DepthParam parametric tension

Covered in Section 2c above. Restated here as an empirical complication: the predicted shrinkage of the Far > Near advantage at large depth separations is not observed in the current data range.

GS -- not sure i followed that: if attention is biased beyond (far depth) then increasing the disparity might actually increase the asymmetry no?
---

## 5. A Possible Reconciliation: Transparency-Specific Beyond Effect

The beyond account may not be a general property of depth attention. Rather, it may be specific to *transparent/superimposed* displays — where one surface is perceptually in front of the other, both fully visible, occupying the same spatial extent.

**The argument.** In transparent stereoscopic displays, the two surfaces are spatially overlapping and must be parsed by the visual system into depth-segregated representations. The far surface occupies the perceptual role of a "behind" object — it is the surface that, in a natural scene, would be partially occluded by the near surface. The visual system's completion machinery may assign the far surface an attentional weight or priority that does not appear in non-overlapping depth displays. In non-superimposed displays (two patches at different depths, separated in the image plane), there is no occlusion relationship, no completion pressure, and no reason for the far surface to carry any special status. In those cases, the peripersonal/looming arguments may dominate and yield Near > Far.

**The specific prediction.** The Far > Near cueing advantage should disappear — or reverse — when the two dot fields are presented at non-overlapping image locations, even if their disparity separation is matched. In that configuration, Far cannot be perceived as "behind" Near because they do not spatially overlap.

A secondary prediction: the advantage should disappear when the two surfaces are presented *sequentially* rather than simultaneously. If Far's advantage depends on being parsed in competition with a simultaneously present Near surface, removing the simultaneity removes the transparency/occlusion framing.

**Evaluation.** This reconciliation is internally coherent. It preserves the Nakayama et al. amodal completion logic, explains why Near > Far dominates in non-transparent depth paradigms, and accommodates the peripersonal literature. It also narrows the scope of the account in a way that makes it more testable. The cost is that it adds a constraint (simultaneity + spatial overlap required) that was not present in the original formulation.

---

## 6. Alternative Account: Calabro & Vaina (2011) — MT Disparity Anisotropy

**Literature finding.** Calabro & Vaina (2011) reported that MT neurons show an anisotropic distribution across preferred disparities: more neurons are tuned to near (crossed) disparities than to far (uncrossed) disparities. If this is correct, then a near-depth motion surface drives more MT neurons, creating more within-area competition for limited response gain. A far-depth motion surface drives fewer neurons, faces less within-area competition, and achieves a more distinct population response.

**Prediction.** Under the Calabro & Vaina account, Far-plane motion should be more legible than Near-plane motion because it faces less neural cross-talk. This does not require any attentional gradient or directional spillover — it is a property of the motion-processing architecture itself. The prediction is that the Far > Near advantage scales with disparity magnitude: larger disparity → more separation between Near and Far populations → less cross-talk → larger Far advantage.

**Relation to VRDots data.** DepthParam is the relevant dataset. Far cueing appears saturated across 0.05–0.15m. Near cueing becomes more negative as depth separation increases (Near cueing: +12.5pp at 0.03m, −9.4pp at 0.05m, −21.9pp at 0.10m, −25.0pp at 0.15m). This pattern — Near getting worse, not better, as planes separate — is *inconsistent* with a simple cross-talk reduction account: if larger separation means less cross-talk between Near and Far MT populations, Near should become more legible as separation increases, not less. The pattern suggests that larger separation actually hurts Near-plane detection, which is more consistent with the spillover/gradient account (more segregated planes means the gradient is more clearly directed away from Near, not less). Alternatively, larger separation may make the two planes perceptually harder to confuse, which would improve Far (saturated) while leaving Near unaffected or even more susceptible to selection errors.

**Status.** The Calabro & Vaina account cannot be cleanly evaluated with current data at this sample size (n=32/cell in DepthParam). It makes a different parametric prediction than the beyond account, and distinguishing them requires adequate power in DepthParam across depths.

---

## 7. Status and Key Tests

Both accounts remain provisional. Neither has been subjected to a definitive test within VRDots.

### Key Test 1: Three-plane display (Near / Mid / Far)

**Design.** Add a middle depth plane (Mid). Run cueing with target in Near, Mid, or Far.

**Beyond account predicts:** Mid-plane cueing < Far-plane cueing (Mid has something beyond it; Far does not). Near-plane cueing < Mid-plane cueing (Near spills most into the display). The performance ordering should be: Near < Mid < Far.

**Calabro & Vaina predicts:** Performance scales with disparity magnitude from fixation, not with the number of planes beyond the attended surface. Near < Mid < Far only if disparity from fixation is the relevant variable — but the shape of the function (linear? step?) distinguishes the two accounts.

**Distinguishing logic.** If Mid is perceptually equidistant from Near and Far in disparity, the two accounts predict the same ordering but differ in the mechanism. To cleanly dissociate: compare Far-plane cueing in a two-plane display (Near+Far) versus a one-plane display (Far only). Beyond account predicts no Far advantage when Near is absent (no spillover target). Calabro & Vaina predicts the same Far performance regardless of whether Near is present.

### Key Test 2: Non-simultaneous / non-overlapping presentation

**Design.** Present the two fields at spatially non-overlapping locations (different apertures at different depths), matched in all other respects to VRDots. If the Far > Near advantage depends on transparency/superimposition, it should attenuate or disappear in non-overlapping conditions.

**Beyond account (transparency-specific version) predicts:** Advantage disappears.
**Beyond account (general version) predicts:** Advantage persists.
**Calabro & Vaina predicts:** Advantage persists (MT anisotropy is not display-configuration-specific).

### Key Test 3: DepthParam with adequate power

**Design.** Run DepthParam at n≥128/cell at each separation (0.03, 0.05, 0.10, 0.15m). Currently n=32/cell is inadequate to evaluate parametric trends.

**Beyond account predicts:** Near deficit should be flat or grow with separation (gradient extends far relative to the tested range); Far should saturate.

**Calabro & Vaina predicts:** Near deficit should *shrink* with separation (less cross-talk at larger disparity). Current data trend goes the wrong direction for Calabro & Vaina — Near becomes more negative as separation increases — but this conclusion requires adequate power.

---

## 8. Summary Assessment

| Criterion | Beyond Account | Calabro & Vaina |
|-----------|---------------|-----------------|
| Accounts for Far > Near | Yes | Yes |
| Predicts monocular collapse | Yes (if depth attention requires disparity) | Yes (if MT disparity tuning requires binocular input) |
| DepthParam Near trend | Consistent (Near worsens as planes separate) | Inconsistent (predicts Near should improve) |
| UNCUED flatness | Silent (requires additional assumption about cue initiation) | Predicts small Far > Near even without cue |
| Requires attentional gradient mechanism | Yes | No |
| Key test | 3-plane display + 1-plane vs 2-plane comparison | DepthParam with adequate power |

**Bottom line.** The beyond account is viable and makes specific predictions that are broadly consistent with the VRDots data. The major tensions are: (a) the UNCUED flatness, which the account handles only by invoking an additional premise (depth attention must be initiated by the F1 cue); and (b) the DepthParam parametric trend, which goes in the direction predicted by beyond but at inadequate power to evaluate parametrically. The Calabro & Vaina account is neurally grounded but its core prediction (Near should improve with separation) runs counter to the descriptive trend in DepthParam. The transparency-specific version of the beyond account is the most parsimonious reconciliation with the broader literature. It should be stated as the working hypothesis, explicitly flagged as provisional, and targeted by the three-plane test.

---

*Generated by Literature Agent, VRDots project. Intended for review and dispute by GS.*
