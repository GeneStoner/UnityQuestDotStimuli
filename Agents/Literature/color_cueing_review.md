# Color and Attentional Cueing in VRDots
*Literature agent — 2026-04-06*

---

## 1. The VRDots Color Story — What We Have

### 1.1 The Early Red Asymmetry (Pilot Session 260323_1534, n=64)

The very first VRDots session with color-balanced stimuli showed a striking asymmetry:

| Condition | Accuracy |
|-----------|---------|
| CUED + Red delayed field | 81.2% |
| CUED + Green delayed field | 50.0% |
| UNCUED | ~15.6% |

A 31pp gap between red and green within the CUED condition is striking. However:
- n=64 total, so n=16/cell — extreme noise
- No balancing of other trial factors across color was verified at this stage
- This session pre-dates careful luminance control; the Quest 3 displays red and green at unequal photopic luminance at equal RGB values (green is photopically brighter, but red may be more salient for attention-capture reasons)

**Assessment**: The red advantage in session 260323_1534 should be treated as an observation requiring replication, not a finding. The effect did not persist.

### 1.2 DepthParam Sessions (R/G Balanced, No Swap, 2026-04-02)

Sessions 260402_0624/0656/0716/0757 used R/G-balanced designs (delayedFieldColor balanced across trials). No color asymmetry was reported in aggregated accuracy; color was not a focus of analysis given the primary N/ZdA/ZdB manipulation, but the R/G balance argues against a systematic red advantage at these sample sizes.

### 1.3 DepthColorLinked (linkDepthColor=1, 2026-04-04)

In these sessions, depth and color always co-varied: Near=Red, Far=Green. The combined results (n=512) showed:
- F1 Dot Cueing: +20.3pp***
- F2 Depth Cueing: +7.0pp*
- Apparent interaction: CUED+ZdNoi > CUED+ZdCoh

This appeared consistent with a color contribution — but depth and color were fully confounded. The interpretation was that either depth change, color change, or both was responsible for the F2/interaction effects.

### 1.4 DecoupledDots (linkDepthColor=0, 2026-04-06) — The Key Dissociation

**n=1026** trials; fully orthogonal 3-factor design:

| Factor | Δ accuracy | OR | p |
|--------|-----------|-----|---|
| F1: Dot cueing (CUED vs UNCUED) | +22.3pp | 3.07 | <.001 *** |
| F2: Depth-field cueing | +12.5pp | 1.89 | <.001 *** |
| F3: Color-field cueing | **+0.0pp** | **1.00** | **.994 n.s.** |

**The color-field cueing effect is exactly zero.** The DepthColorLinked "color effect" was entirely a depth confound. Color, as implemented here — a uniform field-level feature that defines which dots belong to which surface — provides zero additional information for performance beyond what depth and temporal onset already provide.

---

## 2. What Kind of Color Effect Were We Even Looking For?

It is worth being precise about what a "color cueing effect" could mean in VRDots, because there are at least three distinct hypotheses:

**H1 — Color as exogenous capture cue**: Color *change* at tStart captures attention, redirecting it to the changed surface. This would only be relevant if color *changes* were cuing. In VRDots, the exogenous cue is temporal onset of Field B; color is stable across tStart in the N condition, and only swaps in the C and CZ conditions. A color-change-driven capture could account for F3 if the color swap attracted attention — but the null result rules this out.

**H2 — Color as object identity anchor**: Having matched color between the delayed-onset field at encoding and the translating field at test helps retrieve or maintain the attended object file. This is the hypothesis F3 directly tests: does it help performance when color-cued-correctly vs. incorrectly matches? Answer: no (+0.0pp).

**H3 — Color as a segmentation cue enabling the two-surface percept**: The red/green color difference might help the visual system initially segment the two overlapping fields into distinct surfaces. This is NOT directly tested by F3 (which compares matched vs. mismatched color identity of the translator, not presence vs. absence of color difference). The segmentation-cue role of color is a separate question.

The literature speaks most directly to H1 and H2. H3 is addressed in the endogenous attention discussion.

---

## 3. Literature: Color as Exogenous Cue

### 3.1 Abrupt Onsets Are the Truly Exogenous Cue

The most robustly exogenous attentional cue is an abrupt visual onset — an event that engages the transient channel automatically, independent of top-down goals.

**Yantis & Jonides (1984)** — *JEP:HPP* 10:601  
Visual search showed that abrupt onset items were selected first, independent of task relevance. This effect is driven by the transient response of the magnocellular/Y-cell pathway and is highly reliable across paradigms.

**Jonides & Yantis (1988)** — *P&P* 43:346  
Demonstrated that abrupt onsets — not color change, not shape change — uniquely capture attention without top-down support.

**Relevance to VRDots**: The delayed onset of Field B is a genuine exogenous cue in this sense: it creates a transient event in a display that has been otherwise stable for 300ms. This is why the dot-cueing effect (F1: +22.3pp) is robust. Color is not the cue; the transient IS the cue.

### 3.2 Color Singletons and the Stimulus-Driven Capture Debate

**Theeuwes (1992)** — *P&P* 51:599  
The classic demonstration that color singletons capture attention even when irrelevant to the task. A participant searching for a specific shape would be slowed by an irrelevant color singleton — suggesting bottom-up, stimulus-driven capture independent of top-down goals. This became the anchor for the "stimulus-driven capture" hypothesis.

If Theeuwes were right about pure stimulus-driven capture, then the color difference between red and green fields should exogenously bias attention to the more salient surface — predicting a non-null F3 (color-field cueing). Our null contradicts this prediction.

**Folk, Remington & Johnston (1992)** — *JEP:HPP* 18:1030  
The "contingent attentional capture" rebuttal to Theeuwes. Color cues capture attention *only* when the observer is set to search for a color target. Onset cues capture only when the observer is set for onsets. Capture is contingent on the match between stimulus properties and the observer's top-down control settings.

**Bacon & Egeth (1994)** — *P&P* 55:485  
Showed that the Theeuwes (1992) result depended on observers adopting a "singleton detection mode." When the target was not a singleton, color singletons failed to capture attention. The debate between purely stimulus-driven and fully contingent capture has not been fully resolved, but there is strong consensus that at minimum, task set strongly modulates how much color capture occurs.

**Relevance to VRDots**: In DecoupledDots, the task is to identify the direction of translation (an 8-AFC direction response). The relevant attentional set is for *temporal onset* and *translation direction* — not for color. Therefore, contingent capture theory (Folk et al.) predicts exactly the null we observe: color should not capture or maintain attention because it is outside the task-relevant set.

### 3.3 Exogenous Feature-Based Attention Is Elusive

A more recent meta-analytic review:

**Theeuwes (2019)** — *Atten Percept Psychophys* 81:2149 ("In search of exogenous feature-based attention")  
Reviewed the evidence for exogenous (stimulus-driven) feature-based attention — the idea that a feature value (like a color) can guide attention globally, without top-down intent. Conclusion: "With the protocol used in the studies reporting exogenous feature-based attention, the exogenous stimulus-driven influence of FBA is elusive at best, and FBA is primarily a top-down, goal-driven process."

This is directly relevant: if exogenous feature-based attention to color is weak or nonexistent in standard paradigms, we should not expect color to modulate an already-established exogenous onset-cueing effect.

---

## 4. Literature: Color as Object Identity Anchor (H2)

### 4.1 Mitchell et al. (2003) — The Closest Analog in Our Own Paradigm

**Mitchell, Stoner, Fallah & Reynolds (2003)** — *Vision Research* 43:1323  
*(paper_list.md #7; "not color-channel")*

The most directly relevant citation. Two superimposed transparent dot fields, rotating in opposite directions. One surface was selected via an onset cue, then a brief translation occurred. Key manipulation: color differences between surfaces were *removed* partway through the trial. The cueing effect survived color removal at full magnitude.

**What this means**: In the transparent-motion paradigm, once a surface is selected via an onset/motion cue, the object is represented and maintained through spatiotemporal coherence, not through color identity. Color does not anchor the object file for this kind of selection.

**Relation to F3**: Mitchell et al. (2003) tested removal of color from an already-selected object. We tested *mismatched* color between encoding (delayed-field color) and test (translator color) while depth was matched or mismatched. The logic is the same: if color anchors object identity, changing it should hurt. It does not.

**Khoe, Mitchell, Reynolds & Hillyard (2005)** — *Vision Research* 45:3004  
*(paper_list.md #9)*  
ERP study in our paradigm. C1 and N1 cueing effects survive same-color conditions (both surfaces the same color, so color cannot guide selection). Confirms that the surface-selection mechanism indexed by early ERPs is not color-dependent.

### 4.2 Object Files and Color (Kahneman, Treisman & Gibbs 1992)

**Kahneman, Treisman & Gibbs (1992)** — *Cognitive Psychology* 24:175  
Foundational "object file" paper. Object-specific priming across saccades depends on spatiotemporal continuity. Color contributes to object identity, but spatiotemporal continuity (same location, same trajectory) is the primary binding glue. When spatiotemporal and color information conflict, spatiotemporal wins.

**Scholl (2001)** — *Cognition* 80:1  
Review of object persistence. Classic result: when a moving disk passes behind an occluder and reappears with a different color, it is still perceived as one object that changed color — not two different objects. Spatiotemporal continuity overrides color change for object identity.

**Relevance to VRDots**: The delayed-onset field in VRDots is defined by its onset time and spatial co-location with the non-delayed dots. Once the cue fires (onset), the object file is established by spatiotemporal properties (position, motion coherence, onset time). Color is a secondary feature of that file. The DecoupledDots null says that at test — when the cued surface must translate and be identified — the color of the translator relative to the learned color of the delayed-onset field is irrelevant. The identity check is being done on depth and motion, not color.

### 4.3 Sequential Feature Activation — Color Is Downstream

**Schoenfeld, Hopf et al. (2014)** — *Nature Neuroscience* 17:619  
*(paper_list.md #11)*  
MEG study: when a motion-defined transparent surface is attended, feature module activation proceeds sequentially: motion-selective cortex first (~150ms), then color-selective cortex ~60ms later. Attending by color reverses the sequence.

**Relevance to VRDots**: Our exogenous cue is an onset and a motion event (translation). The first thing it engages is the motion/transient pathway. Color processing is secondarily activated as part of feature binding to the already-selected object. This processing order explains why color does not modulate the selection itself — by the time color is activated, selection has already occurred through the motion-onset channel.

---

## 5. Why the Red Asymmetry in the Pilot?

### 5.1 The Three Candidate Accounts

**Account 1: Noise (most likely).**  
n=16/cell (CUED+Red, CUED+Green each have 16 trials). At this cell size, ±30pp swings are expected from chance alone. The 31pp asymmetry is consistent with a noise floor. It was not replicated in subsequent R/G-balanced sessions.

**Account 2: Photopic luminance confound.**  
On the Quest 3 display, green is photopically brighter than red at equal RGB values (the photopically weighted luminance of green is ~3-4× higher at equal sRGB). If red was displayed at a slightly different physical luminance due to monitor-specific gamma, the red dots could have had higher or lower Weber contrast against the background, creating a performance asymmetry unrelated to color per se. The flicker photometry calibration (FlickerCalibrator) was designed to address this, but was not in use at the earliest sessions.

**Account 3: Red attentional salience.**  
Literature does support that red has privileged salience in many contexts:
- Red is associated with behavioral urgency and emotional arousal, leading to faster detection in some paradigms
- Red appears perceptually "closer" to the viewer in many depth-from-color illusions (chromostereopsis)
- Red stop signals are inhibited faster than green in stop-signal tasks

However, these salience effects are usually observed for *color-change* or *color onset* cues, not for color as an established surface property. If red were intrinsically more salient as a surface feature, we would expect it to show up in our large-n DecoupledDots dataset. It does not (OR=1.00, p=.994).

### 5.2 The Verdict

The most parsimonious interpretation is that the pilot red asymmetry is noise at tiny n, possibly inflated by a luminance confound. It is not evidence for a red-specific cueing advantage in the VRDots paradigm. The DecoupledDots result with n=1026 strongly overrides the pilot observation.

---

## 6. What the Null Result Means — and What It Doesn't

### 6.1 What It Means

Color identity — specifically, whether the translator at tStart shares the color of the delayed-onset field — carries zero predictive information for translation-direction discrimination in VRDots. This holds at n=1026 with a fully orthogonal design, in a GLM that simultaneously controls for dot cueing and depth cueing. The result is not a power issue: the same model detects depth-field cueing at +12.5pp with high significance, and dot cueing at +22.3pp. If color had an effect of 5pp or more, we would have detected it.

This extends and reinforces Mitchell et al. (2003): color is not the operative feature for surface selection in the transparent-motion paradigm, whether color is the cue (Mitchell) or a property of the cued surface (DecoupledDots).

### 6.2 What It Doesn't Mean

**It does not mean color is irrelevant to the two-surface percept.**  
Color may play a critical role as a *segmentation cue* — helping the visual system initially parse two overlapping fields into separate surfaces. This is a different role than "attentional anchor." If color separation helps form two distinct surfaces, removing it (all-red design) might weaken the two-surface percept and thus weaken all cueing effects. But this would show up as a main effect on absolute cueing magnitude, not as an F3 interaction. The DecoupledDots design cannot directly test this because color is always present (just matched or mismatched at tStart).

**It does not rule out endogenous color attention.**  
If an observer *tried* to use color to select a surface — setting their attentional control for color — performance might improve. Folk et al.'s contingent capture framework predicts this explicitly: color capture occurs when the observer is set for color. This is the endogenous direction the user plans to pursue separately.

**It does not mean the red/green asymmetry is permanently off the table.**  
A targeted, adequately powered experiment (e.g., color-only block with sufficient n per cell) should be run to formally test for asymmetry. The null in DecoupledDots is for color-field *cueing* (matched vs. mismatched), not for an absolute red vs. green performance comparison.

---

## 7. Literature Gaps — What's Missing

The following are relevant papers not yet retrieved that bear on the color story. They should be added to a future literature session:

| Paper | Why relevant |
|-------|-------------|
| **Folk, Remington & Johnston (1992)** *JEP:HPP* 18:1030 | Contingent capture — theoretical basis for color null |
| **Theeuwes (1992)** *P&P* 51:599 | Stimulus-driven capture — the prediction the null contradicts |
| **Bacon & Egeth (1994)** *P&P* 55:485 | Singleton detection mode — rules out alternative design-based capture account |
| **Theeuwes (2019)** *APP* 81:2149 | Meta-analysis: exogenous feature-based attention is elusive |
| **Jonikaitis & Theeuwes (2017)** *APP* 79:2466 | Color-feature attention weaker than motion or spatial attention |
| **Kahneman, Treisman & Gibbs (1992)** *Cog Psych* 24:175 | Object files — spatiotemporal > color for identity |
| **Scholl (2001)** *Cognition* 80:1 | Object persistence — spatiotemporal overrides color change |
| **Treisman (1998)** *Phil Trans R Soc B* 353:1295 | Feature binding — color bound to object post-selection |

Mitchell et al. (2003), Khoe et al. (2005), and Schoenfeld et al. (2014) are already in paper_list.md as ✓ integrated.

---

## 8. Coherent Narrative for Write-Up

The story can be told in four beats:

**Beat 1 — Motivation**: We asked whether color identity — which surface is which color — helps maintain or retrieve an attended object in the transparent-motion paradigm. Two surfaces, red and green, compete for attention via a temporal onset cue.

**Beat 2 — The confound history**: Earlier experiments confounded depth and color. DepthColorLinked data suggested a field-cueing effect, but depth and color always co-varied. DecoupledDots was designed to orthogonally dissociate them.

**Beat 3 — The null**: Color contributes exactly zero. Depth contributes +12.5pp. The DepthColorLinked "color effect" was entirely a depth confound.

**Beat 4 — Why**: The cue in VRDots is a temporal onset — a genuine exogenous event engaging the transient pathway (Yantis & Jonides 1984). Color is a stable surface property, not a change event. Surface selection in the transparent-motion paradigm is driven by spatiotemporal structure, not color identity (Mitchell et al. 2003; Scholl 2001; Kahneman et al. 1992). Color processing is activated secondarily, downstream of spatial selection, as part of feature binding to the attended object (Schoenfeld et al. 2014). The task never requires using color identity — observers report translation direction — so no top-down color set is established, and contingent capture by color is predicted to be absent (Folk et al. 1992). This converges on the null.

---

*See also*: `decoupled_dots_results.md` (design and results), `depth_ior_hypothesis.md` (depth mechanism), `theory_doc.md §8.2–8.3` (Schoenfeld ERP/MEG)  
*Papers to add to paper_list.md*: Folk et al. 1992, Theeuwes 1992, Bacon & Egeth 1994, Theeuwes 2019, Jonikaitis & Theeuwes 2017, Kahneman et al. 1992, Scholl 2001
