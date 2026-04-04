# Near/Far Translation Asymmetry: A Depth-Gradient Account
*VRDots — DepthParam results, 2026-04-02*
*Draft for discussion. Revised 2026-04-02 × 3: IOR abandoned; "reversal" artifact corrected; translation-depth framing adopted.*

---

## The finding in one paragraph

A parametric depth-separation experiment (0.03 / 0.05 / 0.10 / 0.15m, no swap conditions, R/G two-color, n=32/cell) reveals a large and robust performance asymmetry by translation depth: Far-plane translation is detected accurately (~75–91%) and Near-plane translation is detected poorly (~28–62%), with this difference growing monotonically with depth separation. The temporal onset cue helps in both cases — CUED always outperforms UNCUED when translation depth is held constant — but the depth of the translating field dominates performance, and the cue contributes a secondary modulation on top of it. The working account: an attentional gradient favoring Far depths sets a high baseline for Far translation detection and a low baseline for Near; the cue provides an additional ~10–22pp benefit at whichever depth it targets. Both the depth asymmetry and its parametric scaling appear novel in the stereoscopic surface-selection literature.

---

## The data

*n = 32/cell per depth. All sessions 2026-04-02, observer GS, binocular, nonius lines on.*
*Near/Far label refers to the depth of the **delayed (cue) field**, not the translating field.*

| Cell | 0.03m | 0.05m | 0.10m | 0.15m | What is being detected |
|------|-------|-------|-------|-------|----------------------|
| CUED Far | **90.6%** | **84.4%** | **84.4%** | **84.4%** | Far translation, Far cued |
| UNCUED Near | 50.0% | **68.8%** | **75.0%** | **75.0%** | Far translation, Near cued |
| CUED Near | 62.5% | 59.4% | 53.1% | 50.0% | Near translation, Near cued |
| UNCUED Far | 43.8% | 37.5% | 37.5% | 28.1% | Near translation, Far cued |

### The right comparison: hold translation depth constant, vary the cue

| Translation depth | Cued | Uncued | Cueing Δ |
|------------------|------|--------|----------|
| **Far** (CUED Far vs. UNCUED Near) | 84–91% | 50–75% | +9 to +41pp |
| **Near** (CUED Near vs. UNCUED Far) | 50–62% | 28–44% | +6 to +22pp |

The cue helps in both cases. The apparent "reversal" in the traditional Near-cueing row (CUED Near minus UNCUED Near = negative) was an artifact of simultaneously flipping both cue location and translation depth — it was never a fair comparison. The correct comparison holds translation depth constant. When it does, CUED > UNCUED throughout.

### What actually varies with depth

| Depth sep | Far translation (cued) | Far translation (uncued) | Near translation (cued) | Near translation (uncued) |
|-----------|----------------------|------------------------|------------------------|--------------------------|
| 0.03m | **90.6%** | 50.0% | 62.5% | 43.8% |
| 0.05m | **84.4%** | **68.8%** | 59.4% | 37.5% |
| 0.10m | **84.4%** | **75.0%** | 53.1% | 37.5% |
| 0.15m | **84.4%** | **75.0%** | 50.0% | 28.1% |

**Far translation (uncued) rises with depth**: 50% → 75%. As depth increases, even a Near cue increasingly fails to hold attention at Near, and Far translation is detected better because attention has migrated there.

**Far translation (cued) is depth-invariant**: ~84–91% at all depths. Far selection is reliable from the smallest disparity tested; performance is ceiling-limited.

**Near translation (cued) falls with depth**: 62% → 50%. As depth increases, even a Near cue is less effective at holding attention at Near against the growing gradient pull toward Far.

**Near translation (uncued) falls with depth**: 44% → 28%. As depth increases, Far selection becomes stronger, and Near — when the cue is at Far — receives progressively less residual attention.

---

## An alternative account: near-object salience

Before the gradient account, one alternative must be addressed. Near-plane dots carry crossed disparity — they are physically closer to the observer than fixation. Crossed disparity is a documented trigger for enhanced salience and reflexive orienting responses (~100ms, largely independent of voluntary attention). On this account, Near is not suppressed by a gradient but is instead over-salient in a way that disrupts sustained selection: the Near cue captures attention but then triggers orienting mechanisms that interfere with holding attention at Near through the 293ms delay.

The gradient and near-object accounts make different predictions at a key juncture. If the fixation target is placed at the current Near depth (1.975m), the gradient account predicts the asymmetry weakens or disappears (gradient re-anchors at fixation). The near-object account predicts the asymmetry persists (crossed disparity sign is unchanged regardless of fixation depth). The fixation manipulation (Prediction 2) dissociates them.

One constraint worth noting: the translation in VRDots is in-plane — dots translate within their depth plane, not toward or away from the observer. There is no dynamic looming signal. The near-object concern is about the static crossed disparity of the Near surface creating a general salience response, not a heading-specific approach signal.

---

## A constraint from the 2D literature

The cue-to-translation interval — approximately 293ms (22 frames at 75Hz, from Field B onset to translation onset) — was chosen because prior work on these transparent-motion stimuli, without depth differences, showed it produces a large positive cueing effect near the maximum observed across a range of durations.

This constrains any mechanistic account: **the same SOA that produces the depth asymmetry here produces maximum positive cueing in 2D.** Any mechanism must be compatible with robust CUED > UNCUED at identical SOA when depth planes are absent.

This rules out inhibition of return (IOR). IOR requires capture followed by disengagement and should suppress the cued location at ~293ms SOA regardless of depth — but 2D data show the opposite. The reason IOR does not develop here: the cued surface is continuously present and moving throughout the delay. Ongoing motion maintains attentional engagement. Classic IOR paradigms use a brief disappearing cue followed by a blank ISI — the opposite of this design.

---

## The proposed account: depth-gradient baseline with cue modulation

### The gradient

Attention in depth is not uniformly distributed. It is anchored at the fixation plane and extends more easily toward Far (at and beyond fixation) than Near (inside fixation). This asymmetric gradient is documented: Parks & Corballis (2006) found P1 ERP enhancement only for far-attended conditions, absent for near-attended; Caziot, Rolfs & Backus (2023) found a directional Far advantage and measured no vergence shift during depth cueing, localizing the effect in the disparity representation rather than the oculomotor system.

### Two roles of the gradient

**1. Sets the baseline performance level by depth plane.**
The gradient makes Far the default attended depth. Far translation is therefore detected from a high-attention starting point; Near translation from a low-attention starting point. This produces the large Far > Near performance gap that is present regardless of cueing and grows with depth separation as the gradient strengthens.

**2. Modulates cue effectiveness.**
A Far cue fires into the high-gain region — attention captures strongly and stays through the delay, reinforced by the gradient. A Near cue fires into the low-gain region — attention is partially captured at Near but the gradient continuously pulls toward Far during the 293ms delay. The result: the Near cue is less effective at holding attention at Near than the Far cue is at holding attention at Far.

This explains why Far-translation cueing is larger than Near-translation cueing at small depths (0.03m: +41pp vs +19pp), and why the uncued Far-translation condition (Near cued, Far translates) improves with depth — as depth increases, the gradient is stronger, migration from Near to Far is more complete, and the Near cue inadvertently provides nearly as much attentional benefit to Far translation as the Far cue itself does (75% vs 84% at 0.10m).

### The migration process

The gradient does not switch on at a threshold — it scales continuously with disparity strength. A stronger gradient drives faster migration from Near to Far. At the fixed 293ms SOA, migration completes only when the gradient is strong enough to overcome the sustaining signal from ongoing Near rotation within that window:

- **0.03m** (≈45 arcsec): gradient present but weak → migration slow → Near cue partially holds attention at Near → Near-cue benefit is real (+19pp for Near translation, +41pp gap for Far translation) but Near-to-Far bleed is incomplete
- **0.05m** (≈75 arcsec): gradient stronger → migration more complete by tStart → Near cue less effective at Near, more benefit bleeds to Far
- **0.10m+**: gradient saturated → migration reliably complete → Near cue provides near-equal benefit to Far translation as Far cue; Near translation cuing still positive but modest

The crossover depth (~0.04m) where Near-cue benefit to Far translation starts approaching Far-cue benefit corresponds approximately to the stereoacuity threshold at 2m viewing distance, which is where depth planes first become perceptually distinct surfaces capable of hosting the gradient asymmetry.

### Why the gradient overrides ongoing Near rotation

In 2D, ongoing rotation holds attention at the cued surface because there is no competing attractor — the gradient is flat and the motion signal is the only sustained engagement signal. In depth with a Near cue, the gradient provides a continuous pull toward Far that is independent of, and concurrent with, the Near motion signal. The question is one of relative strength: can the gradient consistently overcome the sustaining signal within 293ms? At 0.03m the gradient is weak — migration is slow and incomplete. At 0.05m+ the gradient is strong enough that migration completes within the delay. The SOA experiment directly probes this: longer SOA → more migration time → gradient operates even at smaller depths.

### The stochastic migration picture and the CUED/UNCUED Far-translation gap

Both CUED Far and UNCUED Near involve detecting Far translation. They differ in where attention started: CUED Far begins at Far (gradient + cue aligned), UNCUED Near begins at Near (gradient pulls it away). The gap between them reflects how often migration has not fully completed by tStart:

| Depth | CUED Far | UNCUED Near | Gap |
|-------|----------|-------------|-----|
| 0.03m | 91% | 50% | 41pp |
| 0.05m | 84% | 69% | 15pp |
| 0.10m | 84% | 75% | 9pp |
| 0.15m | 84% | 75% | 9pp |

The gap shrinks systematically with depth — stronger gradient → more trials on which migration completes by tStart → UNCUED Near approaches CUED Far. The residual 9pp at 0.10–0.15m is the irreducible cost of starting at the wrong attractor. This gap should also shrink with SOA (more migration time at any given depth), which is a prediction of the SOA experiment.

---

## The same process, two attractors

The unifying picture: the 293ms delay allows attention to fully settle at its gradient-determined resting state.

- **2D**: gradient is flat; attention settles at the cued surface; CUED >> UNCUED. Maximum at this SOA because it is the consolidation time.
- **Depth, Far cued**: gradient and cue aligned; attention settles at Far; strong Far detection, weak Near detection.
- **Depth, Near cued**: gradient opposes cue; attention partially or fully migrates to Far during the delay. At small depths, migration is incomplete — some Near detection, some bleed to Far. At large depths, migration is complete — Near detection is poor, Far detection is good even from a Near-cued starting point.

The prior 2D paradigm and the current depth data are not in conflict. They are the same attentional consolidation process with the same SOA but different gradient landscapes.

---

## What the literature does and does not predict

**Established:**
- Far > Near attentional gradients in stereoscopic viewing (Parks & Corballis 2006; Caziot et al. 2023)
- Gradient is disparity-driven, not vergence-driven (Caziot et al. 2023; Arnott & Shedden 2000)
- Depth is a preattentive grouping dimension (Nakayama & Silverman 1986)
- Depth-plane filtering weakened by same-color design (Theeuwes et al. 1998) — current experiment uses R/G, not a confound here
- 2D paradigm SOA function: cueing peaks at ~293ms, consistent with attentional consolidation time

**Not established / potentially novel:**
- The parametric depth-scaling of the Far > Near translation performance asymmetry in a surface-selection task
- The continuous gradient-strength account: Far-translation uncued performance rising, Near-translation cued performance falling, both monotonically with depth separation
- The crossover between these trends near the stereoacuity threshold
- The stochastic migration framing: CUED Far / UNCUED Near gap shrinking with depth and predicted to shrink with SOA

---

## Predictions

**0. Heading × depth reanalysis of existing data (no new sessions required)**

The Far > Near translation asymmetry should be uniform across the 8 heading directions if it is a depth-plane-level effect. If concentrated in specific headings (e.g., approach-direction), a heading-specific mechanism is implicated. Translation in VRDots is in-plane so no heading is a true looming trajectory — uniform distribution across headings favors depth-plane accounts. Reanalysis: `TransDeg` × `DelayedFieldDepth` from existing TSVs.

**1. SOA manipulation**

At short SOA (~100–150ms), migration has not completed — Near-to-Far migration is minimal, Near cue effectively holds attention at Near, and the Near-translation cueing benefit should be comparable to Far-translation cueing. Far-translation uncued performance should be low (migration hasn't occurred). As SOA lengthens, migration completes progressively: Near-translation cueing benefit decreases (gradient erodes Near-cue effectiveness), Far-translation uncued performance rises (migration brings attention to Far). The SOA at which these cross is an estimate of migration completion time at each depth.

**2. Fixation-depth reversal**

If the fixation target is placed at the current Near plane (1.975m), the gradient should re-anchor — what was Near (inside fixation) is now at fixation, and the gradient should weaken or reverse. The gradient account predicts the Far > Near performance asymmetry weakens or disappears at this fixation depth. The near-object salience account predicts it persists (crossed disparity sign unchanged). This is the critical dissociation experiment.

**3. Fine-grained crossover depth**

A fine-grained depth sweep (0.033 / 0.038 / 0.042 / 0.047m) would locate where Far-translation uncued performance first rises above baseline and where Near-translation cued performance first falls below baseline, and test whether both transitions fall at the stereoacuity threshold for this observer.

**4. UNCUED Near tracking CUED Far with SOA**

At any given depth, UNCUED Near should approach CUED Far performance as SOA lengthens (more migration time → gap closes). At very short SOA, the gap should be maximal (migration hasn't occurred). This provides a within-depth SOA function that directly estimates the distribution of migration completion times.

---

## Open issues

| Issue | Status | Resolution |
|-------|--------|-----------|
| n=32/cell throughout | Provisional — all parametric claims | Second sessions at each depth (priority 1) |
| "Reversal" framing | Corrected — artifact of confounding cue and translation depth | Translation-depth framing adopted throughout |
| Looming vs. gradient | Not yet distinguished | Fixation-depth manipulation (Prediction 2) |
| Gradient overrides rotation — mechanism | Argued by continuous gradient-strength logic; SOA experiment is clean test | SOA manipulation (Prediction 1) |
| Crossover depth location | Currently between 0.03m and 0.05m | Fine-grained sweep after second sessions |

---

*Revised 2026-04-02 (third pass): core framing changed from "Near cueing reversal" to "Far > Near translation asymmetry with positive cueing at both depths." Previous framing was an artifact of comparing CUED Near to UNCUED Near across different translation depths. Programmer critique (programmer_critique_gradient_migration.md) identified this. IOR account abandoned in second pass.*

*Literature agent, 2026-04-02. Based on DepthParam sessions 260402_0624–0757 (n=32/cell). Second sessions pending. Quantitative claims provisional until n=64/cell.*
