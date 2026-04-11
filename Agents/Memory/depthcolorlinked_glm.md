---
name: DepthColorLinked GLM Results
description: Key findings from DepthColorLinked GLM — 50% swap pilot, depth+color confounded, object-specific disruption confirmed
type: project
---

## Experiment: Exp_DepthColorLinked_005m

**Design**: linkDepthColor=1. Near=Red, Far=Green (fixed). ZdA and ZdB only — no no-swap baseline.
- ZdA: coherent subfields (S0+S2) change depth+color at tStart
- ZdB: noise subfields (S1+S3) change depth+color at tStart
- Both conditions have 100% depth+color change in scene — matched total disruption
- Difference: ZdA hits the coherent translator; ZdB hits the incoherent background
- **n=1024** (4 sessions: 260404_0940, 260404_1123, 260406_1001, 260406_1034)
- **Data path**: `/tmp/quest_pull2/files/`

## Raw results (pooled Near+Far)

| Condition | CUED | UNCUED | Cueing Δ | sig |
|-----------|------|--------|----------|-----|
| ZdNoi (translator stable = ZdB when CUED) | 47.7% | 21.9% | **+25.8pp** | *** |
| ZdCoh (translator changes = ZdA when CUED) | 30.5% | 23.4% | **+7.0pp** | † |

Disruption: −18.8pp in cueing effect when coherent translator changes depth+color.
UNCUED arm is flat: 21.9% vs 23.4% — depth+color continuity does nothing without dot cue.

## GLM — Logistic with interactions (n=1024, 2026-04-09)

Model: `logit(correct) ~ F1 + F2 + F3 + F1:F2 + F1:F3 + F2:F3`
- F1 = dot cueing (CUED=1)
- F2 = translator depth+color continuity (ZdNoi for relevant cond = 1; confounds depth+color)
- F3 = translator Near (1=Near)
McFadden R² = 0.072; LRT p < 10⁻¹⁷.

| Term | AME (pp) | p |
|------|----------|---|
| F1 Dot cueing | +5.2 | .253 n.s. |
| F2 Depth+Color continuity | −2.2 | .635 n.s. |
| F3 Translator Near | **−21.4** | <.001 *** |
| **F1×F2** | **+16.5** | .003 ** |
| F1×F3 | +5.4 | .346 n.s. |
| F2×F3 | +1.1 | .844 n.s. |

## Comparison to DecoupledDots GLM2

Same qualitative structure: F1×F2 dominates, main effects null, Near penalty large.

| | DepthColorLinked | DecoupledDots |
|--|--|--|
| n | 1024 | 2051 |
| F1×F2 AME | +16.5pp ** | +32.7pp *** |
| Near AME | −21.4pp *** | −15.3pp *** |
| Color factor | confounded with depth | null (+0.9pp n.s.) |

DCL F1×F2 is ~half of DD. Likely because ZdNoi reference in DCL still has background depth change (vs clean N condition in DD). Both show the same mechanism.

## Key mechanistic conclusion

ZdNoi and ZdCoh are matched for total scene depth+color disruption. F2 main effect ≈ 0 means background depth change is irrelevant — even UNCUED observers ignore it. The disruption is specifically about the coherent translator's depth-plane identity. This rules out general scene-disruption and supports object-based depth tracking: attention anchors to the cued object's depth plane as part of its object representation.

DecoupledDots confirms: color is the null factor within this confound. The F2 effect in DCL is entirely attributable to depth.

## New theoretical question raised (2026-04-09)

Does the mechanism require DISPARITY-TUNED NEURONS specifically, or would depth ordering cued by non-disparity means (occlusion, motion parallax) suffice? The Near/Far asymmetry is stereoptic (disappears monocularly). But F2 (depth-plane continuity) partially survived monocular viewing (+7.1pp) in DepthSwapCtrl — though that had no alternative depth cues at 0.05m. A test with perceived depth from monocular cues only would dissociate "3D location tracking" from "object-based disparity representation."

## Scripts and files

- `Tools/Analysis/depthcolorlinked_cueing_figure.py` → `Agents/Figures/depthcolorlinked_cueing.pdf`
- `Tools/Analysis/depthcolorlinked_glm.py` → `Agents/Figures/depthcolorlinked_glm.pdf`
- `Tools/Analysis/depth_color_linked_traj.py` → `Agents/Figures/depth_color_linked_traj.pdf`
- `Agents/Literature/depthcolorlinked_results.md` (full write-up)
- `Agents/WriteUps/depthcolorlinked_results.pdf`
