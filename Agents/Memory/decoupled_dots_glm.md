---
name: DecoupledDots GLM Results
description: Key findings from DecoupledDots GLM analyses — dot cueing, depth-field cueing synergy, and Near/Far asymmetry
type: project
---

## GLM1 — Additive model (n=1026, S1+S2, 2026-04-06)

**Design**: linkDepthColor=0, 4 swap types (N/C/Z/CZ) × CUED/UNCUED, fully orthogonal 2³ factorial.

| Factor | LPM (pp) | OR | p |
|--------|----------|----|---|
| Dot cueing (CUED vs UNCUED) | **+22.3pp** | 3.07 | *** |
| Depth-field cueing (translator in same depth plane as delayed field's first appearance) | **+12.5pp** | 1.89 | *** |
| Color-field cueing (translator color matches delayed field's original color) | **+0.0pp** | 1.00 | n.s. |

Baseline (UNCUED+CZ) = 12.8% ≈ chance. McFadden R² = 0.065.

## GLM2 — Interaction model (n=2051, all 4 sessions, 2026-04-09)

Model: `correct ~ F1 + F2 + F3 + F4 + F1:F2 + F1:F4 + F2:F4`
F4 = translator in Near plane (1=Near). McFadden R² = 0.092.

| Term | AME (pp) | p |
|------|----------|---|
| F1 Dot cueing (main effect) | −5.3 | 0.098 n.s. |
| F2 Depth-field cued (main effect) | −6.1 | 0.057 n.s. |
| F3 Color-field cued | +0.9 | 0.64 n.s. |
| F4 Translator Near | **−15.3** | <.001 *** |
| **F1×F2 Dot × Depth** | **+32.7** | <.001 *** |
| F1×F4 Dot × Trans-depth | **+8.9** | 0.027 * |
| F2×F4 Depth × Trans-depth | **−12.4** | 0.002 ** |

**Key GLM2 findings**:

1. **F1 and F2 are synergistic, not additive.** The +22.3pp and +12.5pp estimates from GLM1 were artefacts of forcing an additive structure onto a synergistic interaction. When an interaction term is included, both main effects collapse to near-zero; the signal concentrates in F1×F2 (+32.7pp).

2. **"Depth swaps disrupt dot cueing" is an equivalent framing.** Z and CZ conditions under CUED trials are exactly F1=1, F2=0: the depth swap moves the translator out of the delayed field's onset depth plane, severing depth-plane continuity. The interaction is bidirectional: same depth swap creates Depth✓ in UNCUED trials (coincidental alignment), producing a symmetric benefit there. This exactly recapitulates ZdA/ZdB dissociation from DepthSwapCtrl.

3. **Translator Near/Far asymmetry (F4) is large and robust: −15pp.** Near is substantially worse. The CUED condition partially offsets this (F1×F4 +8.9pp*); depth cueing does not (F2×F4 −12.4pp**).

**How to apply**: The correct description is that dot cueing and depth-field cueing conjointly drive performance — both must be present. Neither cue works well in isolation. Equivalently: depth swaps specifically and selectively disrupt dot cueing by breaking depth-plane continuity of the attentional object.

**Scripts**: `decoupled_dots_glm.py` (GLM1), `decoupled_dots_glm2.py` (GLM2)
**Literature**: `Agents/Literature/decoupled_dots_results.md` §3.3, §3.6
