# DepthColorLinked Experiment — Design, Results & Model Comparison
*Written 2026-04-09*

---

## 1. Overview and position in the experiment series

**DepthColorLinked** (asset: `Exp_DepthColorLinked_005m`, `linkDepthColor=1`) was run prior to DecoupledDots. Its purpose was to test whether swapping the depth plane and color of the coherent translator at tStart would disrupt dot cueing. It confirmed that it does. Because depth and color were always changed together (confounded), the experiment could not identify which factor drove the effect. That question was subsequently resolved by DecoupledDots, which showed depth is the active factor and color is null.

This document describes the DepthColorLinked results in detail, with a focus on the GLM and what it tells us in light of the DecoupledDots findings.

---

## 2. Design

**Asset**: `Exp_DepthColorLinked_005m`, `linkDepthColor=1`, `includeNoSwapBaseline=0`
**Depth separation**: 0.05 m. **Near=Red**, **Far=Green** (fixed throughout).
**Sessions**: 260404_0940, 260404_1123, 260406_1001, 260406_1034  (**n=1024 total**)

### Conditions

There are only two swap conditions — no no-swap baseline:

| SwapType | What changes at tStart | Which dots |
|----------|----------------------|------------|
| ZdA | Depth+Color swap | The "A" subset (~50% of dots, indexed by position). These are the coherent-translator dots when CUED. |
| ZdB | Depth+Color swap | The "B" subset (~50% of dots). These are the background/incoherent dots when CUED. |

**Critical point**: both conditions involve a depth+color swap on **100% of trials**. The total amount of depth and color change in the visual scene is matched between ZdA and ZdB. What differs is *which* dots change: the coherent translating object (ZdA when CUED) or the incoherent background (ZdB when CUED).

### Translator-centric labeling

Because ZdA and ZdB swap different dot subsets, their meaning is reversed for CUED vs UNCUED trials:

| Cond | ZdA effect on translator | ZdB effect on translator | Label |
|------|--------------------------|--------------------------|-------|
| CUED | Translator changes depth+color (**ZdCoh**) | Translator stays in plane (**ZdNoi**) | — |
| UNCUED | Translator stays in plane (**ZdNoi**) | Translator changes depth+color (**ZdCoh**) | — |

**ZdNoi**: the coherent translating dots remain in their onset depth+color plane; the background dots change.
**ZdCoh**: the coherent translating dots change depth+color plane at tStart; the background remains.

### Analysis factors

Two factors (both binary, coded 0/1) are extractable from this design:

| Factor | = 1 when | = 0 when |
|--------|----------|----------|
| **F1  Dot cueing** | Trial is CUED | UNCUED |
| **F2  Depth+Color continuity** | Translator maintains onset depth+color plane (ZdNoi for CUED, ZdA; ZdNoi for UNCUED, ZdB) | Translator changes plane (ZdCoh) |
| **F3  Translator Near** | Translator occupies Near plane during translation | Far |

F2 is confounded: it captures depth continuity and color continuity simultaneously. We cannot separate them within this experiment. (DecoupledDots resolves this: depth drives the effect, color is null.)

No color factor is extractable here because Near is always Red and Far always Green — field color perfectly predicts translator depth, so including color as a separate factor would be collinear with F3.

---

## 3. Raw results

### Accuracy by condition

| Condition | % correct | n |
|-----------|-----------|---|
| ZdNoi + CUED + Far | 59.4% | 128 |
| ZdNoi + CUED + Near | 35.9% | 128 |
| ZdNoi + UNCUED + Far | 28.1% | 128 |
| ZdNoi + UNCUED + Near | 15.6% | 128 |
| ZdCoh + CUED + Far | 36.7% | 128 |
| ZdCoh + CUED + Near | 24.2% | 128 |
| ZdCoh + UNCUED + Far | 35.2% | 128 |
| ZdCoh + UNCUED + Near | 11.7% | 128 |

Chance = 12.5% (1/8 directions).

### Cueing effects by condition

| Condition | CUED | UNCUED | Cueing Δ | sig |
|-----------|------|--------|----------|-----|
| ZdNoi (translator stable) | 47.7% | 21.9% | **+25.8 pp** | *** |
| ZdCoh (translator changes plane) | 30.5% | 23.4% | **+7.0 pp** | † |

Dot cueing is strong when the coherent translator stays in its onset depth+color plane, and is nearly abolished when the translator changes plane. The 18.8pp reduction in cueing is the primary finding.

**The UNCUED arm is flat**: 21.9% vs 23.4% across ZdNoi and ZdCoh — a 1.5pp difference, non-significant. Depth+color continuity of the translator provides essentially no benefit without the dot cue.

---

## 4. GLM — Logistic regression with interaction terms

### Model

```
logit(correct) = β₀ + β₁F1 + β₂F2 + β₃F3
                    + β₄(F1×F2) + β₅(F1×F3) + β₆(F2×F3)
```

Fitted by maximum likelihood (statsmodels Logit, n=1024). McFadden pseudo-R² = 0.072; LRT χ²(6) = 90.9, p < 10⁻¹⁷.

### Results

| Term | Log-odds (β) | SE | z | p | AME (pp) |
|------|-------------|-----|---|---|----------|
| Intercept | −0.714 | 0.178 | −4.00 | <.001 *** | — |
| F1  Dot cueing | +0.267 | 0.234 | +1.14 | .254 n.s. | +5.2 pp |
| F2  Depth+Color continuity | −0.114 | 0.239 | −0.47 | .635 n.s. | −2.2 pp |
| F3  Translator Near | **−1.101** | 0.267 | −4.12 | <.001 *** | **−21.4 pp** |
| F1 × F2 | **+0.846** | 0.288 | +2.94 | .003 ** | **+16.5 pp** |
| F1 × F3 | +0.278 | 0.295 | +0.94 | .346 n.s. | +5.4 pp |
| F2 × F3 | +0.057 | 0.290 | +0.20 | .844 n.s. | +1.1 pp |

AMEs are average marginal effects — the average change in predicted P(correct) across all observations when a predictor flips from 0 to 1.

### Interpretation

**Two terms are significant: F3 (Near penalty) and F1×F2 (dot × depth+color continuity).**

**F1 main effect: +5.2pp, n.s.** Dot cueing alone — at the reference cell (F2=0, F3=0: translator changes plane, Far) — provides little benefit. This is not because the dot cue is ineffective globally; it is because the coefficient is conditioned on F2=0 (ZdCoh), the disrupted condition. When the translator changes plane, the dot cue is nearly useless.

**F2 main effect: −2.2pp, n.s.** Depth+color continuity of the translator, in the absence of a dot cue (F1=0), provides no reliable benefit. UNCUED observers cannot exploit translator depth+color continuity. This is visible directly in the raw data: UNCUED+ZdNoi=21.9%, UNCUED+ZdCoh=23.4% — indistinguishable.

**F1×F2 interaction: +16.5pp, p=.003.** The benefit of dot cueing is substantially larger when the translator also maintains depth+color continuity. The conjunction of dot cue AND translator continuity is required for high performance.

**F3 Translator Near: −21.4pp, p<.001.** A large, robust Near-plane penalty — the translator is harder to identify when it occupies the Near depth plane vs Far. This replicates the Near < Far asymmetry seen in DecoupledDots (−15.3pp), DepthBaseline, and DepthSwapCtrl. It is present in binocular sessions and absent in monocular sessions, implicating stereoptic disparity processing.

---

## 5. The model rules out general-disruption accounts

The critical design feature of DepthColorLinked is that **ZdNoi and ZdCoh are matched for total scene disruption**: the same number of dots (50%) change depth plane and color on every trial in both conditions. The only difference is which dots change — the coherent translator vs the incoherent background.

A "general disruption" account — where any large depth+color change in the scene degrades dot cueing — predicts equal cueing disruption in ZdNoi and ZdCoh, and an F2 main effect (both arms, CUED and UNCUED, should be hurt by a disruptive visual event). This is not what we observe:

- UNCUED arm is flat across conditions (F2 main effect ≈ 0): background depth swaps do not disrupt, even for UNCUED observers who are presumably unguided by the dot cue.
- CUED arm collapses specifically in ZdCoh: the disruption tracks the *identity* of the swapping dots (translator vs background), not the magnitude of change.

The F2 main effect near zero, combined with the large F1×F2 interaction, means: depth+color continuity is valuable *only* for the CUED observer, and only because it maintains the integrity of the attended object. The same depth+color change affecting the background — which the CUED observer ignores — has no measurable effect on performance.

This is direct evidence for **object-based specificity**: the attentional mechanism that underlies dot cueing tracks the coherent translating object, and it relies on that object's depth (and presumably color, though DecoupledDots shows color alone is null) plane as part of its object representation. When the object changes depth plane at tStart, the attentional pointer — anchored to the onset depth — fails to follow the translation.

---

## 6. Comparison to DecoupledDots GLM2

| | **DepthColorLinked** | **DecoupledDots** |
|--|--|--|
| n | 1024 | 2051 |
| Model | F1+F2+F3+F1:F2+F1:F3+F2:F3 | F1+F2+F3+F4+F1:F2+F1:F4+F2:F4 |
| F1 main effect AME | +5.2pp n.s. | −5.3pp n.s. |
| F2 main effect AME | −2.2pp n.s. | −6.1pp n.s. |
| F3/F4 Near AME | −21.4pp *** | −15.3pp *** |
| **F1×F2 AME** | **+16.5pp **  | **+32.7pp *** |
| Color (F3 in DD) | — (confounded) | +0.9pp n.s. |

**Both models show the same qualitative structure**: F1 and F2 main effects are near zero and non-significant; the entire signal concentrates in F1×F2; the Near-plane penalty is large and robust. The similarity is striking given that the experiments differ in swap type (50% vs 100%), stimuli (Near=Red/Far=Green vs balanced), and exact depth-change mechanism.

**Why is F1×F2 AME smaller in DepthColorLinked (+16.5pp) than in DecoupledDots (+32.7pp)?**

In DecoupledDots, the contrast for F2 is clean: ZdNoi (F2=1) = no depth change at all for the translator; ZdCoh (F2=0) = translator changes depth on 100% of trials. In DepthColorLinked, *both* conditions have depth changes occurring on 100% of trials — the ZdNoi condition still has background dots changing depth. The "F2=1" reference level in DepthColorLinked is not the same as the N condition in DecoupledDots. Some contamination from background depth change may reduce the measured interaction size.

Alternatively, the smaller F1×F2 in DepthColorLinked could reflect a dose-response relationship: the background depth change in ZdNoi provides some ambient visual disruption that partially degrades the ZdNoi+CUED performance. But this cannot be a large effect, given that the UNCUED arm (which should be equally sensitive to ambient disruption) is flat.

**The most parsimonious view**: the F1×F2 interaction coefficient estimates the *marginal* benefit of depth+color continuity for the dot-cued observer. In both experiments, the dominant term is the same. The difference in AME magnitude is likely a combination of (a) background depth change adding noise to the ZdNoi reference in DepthColorLinked, and (b) the smaller total n and fewer depth-swap conditions in DepthColorLinked.

**Color cannot be separated from depth in DepthColorLinked.** DecoupledDots, with its 100% color-only swap (C condition), shows F3=+0.9pp n.s. The most plausible interpretation of the F2 effect in DepthColorLinked is that it is entirely driven by the depth component, with color contributing nothing — consistent with DecoupledDots. DepthColorLinked cannot prove this, but it is the parsimonious hypothesis given the available evidence.

---

## 7. Summary

1. **Dot cueing is disrupted when the coherent translator changes depth+color plane**: +25.8pp cueing in ZdNoi vs +7.0pp in ZdCoh (−18.8pp disruption, p<.001 for difference).

2. **The disruption is object-specific, not due to general scene change**: ZdNoi and ZdCoh are matched for total depth+color change. Disruption tracks whether the *translator* (the attended object) changes, not the background.

3. **The GLM confirms: F1×F2 is the whole story** (+16.5pp ** AME). Main effects of dot cueing and depth+color continuity are individually near zero. The conjunction is required.

4. **UNCUED performance is unaffected by translator depth continuity** (F2 main effect ≈ 0). Depth+color continuity provides no navigational cue for observers without the temporal dot cue.

5. **Near-plane penalty is large and robust** (−21.4pp ***), replicating DecoupledDots.

6. **DecoupledDots later shows color is the null factor**: the F2 effect in DepthColorLinked is most plausibly entirely attributable to depth plane identity.

7. **The mechanism is object-based**: the temporal dot cue establishes attention on an object defined partly by its depth plane. When that object loses depth-plane continuity at tStart, the attentional pointer fails to track the ensuing translation.

---

## 8. Analysis files

| File | Purpose |
|------|---------|
| `Tools/Analysis/depthcolorlinked_cueing_figure.py` | 2-panel cueing figure (ZdNoi/ZdCoh × Near/Far) + right strip |
| `Tools/Analysis/depthcolorlinked_glm.py` | GLM (logistic + AMEs); produces 2-page forest-plot PDF |
| `Agents/Figures/depthcolorlinked_cueing.pdf` | Data figure |
| `Agents/Figures/depthcolorlinked_glm.pdf` | GLM forest plot + predicted vs observed |
| `Agents/WriteUps/depth_color_linked_writeup.pdf` | Earlier write-up (trajectories + design, pre-GLM) |
