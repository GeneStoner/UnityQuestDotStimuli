# VRDots Historical Data — Pre-Stereo Comparison
*Last updated: 2026-04-01*

---

## 1. Session Archive Overview

All data in `~/Library/Application Support/ThatsRandom/VRDotsDataFiles/` (341 TSV files).

| Period | Dates | Sessions (n≥50) | Description |
|--------|-------|-----------------|-------------|
| Early dev | Dec 2025 – Jan 2026 | 12 sessions | Pre-stereo VR baseline; parameter exploration |
| Pre-pilot | Mar 23–26, 2026 | 9 sessions | Systematic pre-stereo comparisons; same VR system |
| DepthSwapCtrl pilot | Mar 30 – Apr 1, 2026 | 10 sessions | Current pilot (9 analyzed, 1 incomplete) |

---

## 2. December 2025 – January 2026: Early Development

No depth, no swap types. Variable effects during parameter exploration. Key observations:

| Session | n | CUED | UNCUED | Δ | p | Notes |
|---------|---|------|--------|---|---|-------|
| 251218_1321 | 160 | 56% | 74% | −18pp | * | **Reversed** — likely configuration issue |
| 251218_1633 | 325 | 67% | 59% | +8pp | n.s. | Weak; parameters still in flux |
| 260114_0700 | 256 | 73% | 59% | +14pp | * | Stabilizing |
| 260122_0738 | 64 | 75% | 28% | +47pp | *** | Large effect; params settled |
| 260122_0956 | 64 | 72% | 28% | +44pp | *** | Large effect replicated |

Overall accuracy in this era was high (59–84%) — task likely easier due to longer translation duration, different timing, or other parameter differences vs current paradigm. The early reversed session (251218_1321) and general variability suggest this was genuine parameter exploration, not clean experimentation. By late January 2026, a large and stable cueing effect (+44–47pp***) was established under the final-ish parameters.

**Tentative interpretation**: The large effects in Dec–Jan likely reflect a period when the delayed onset advantage was clear and uncontaminated by depth complexity or swap conditions. These may not be directly comparable to the March data if timing or dot parameters differed.

---

## 3. March 23–26, 2026: Pre-Stereo Systematic Comparisons

Same VR system as DepthSwapCtrl, largely same parameters. Most directly comparable to current pilot.

### 3.1 No-swap baseline (no depth)

| Sessions | n | CUED | UNCUED | Δ | p |
|----------|---|------|--------|---|---|
| 260323_1534+1552+1620 (pooled) | 192 | 61.5% | 28.1% | **+33.3pp** | *** |
| 260324_0716 (N only) | 64 | 53.1% | 25.0% | **+28.1pp** | * |

**Large cueing effect (~30pp) without any depth separation.** This is the no-stereo baseline for the fundamental onset-cueing effect.

### 3.2 Motion swap (M vs N)

| Swap | CUED | UNCUED | Δ | p |
|------|------|--------|---|---|
| N (baseline) | 59.4% | 30.3% | +29.1pp | * |
| M (motion swap) | 46.9% | 31.2% | +15.6pp | n.s. |

Motion swap reduces cueing by roughly half (+29 → +16pp) but doesn't eliminate it. The cued translator changes motion type mid-trial; the temporal onset advantage partially survives.

### 3.3 Dots50 swap (D vs N)

| Swap | CUED | UNCUED | Δ | p |
|------|------|--------|---|---|
| N (baseline) | 56.2% | 27.3% | +29.0pp | * |
| D (50% dots swap) | 59.4% | 25.0% | +34.4pp | ** |

50% dot swap does **not** reduce cueing — if anything it slightly increases it (not significantly). Swapping half the dots has no disruptive effect. This was a key early result establishing that the cueing effect is not simply about dot count or spatial layout continuity.

### 3.4 Depth baseline (no swap, with depth separation)

Both sessions used 0.10 m depth separation (much larger than DepthSwapCtrl's 0.05 m).

| Session | Sep | Overall Δ | Near Δ | Far Δ |
|---------|-----|-----------|--------|-------|
| 260325_1831 | 0.10m | +25.7pp ** | −7.5pp n.s. | +59.4pp *** |
| 260325_1914 | 0.10m | +7.1pp n.s. | **−46.9pp *** | +60.0pp *** |
| 260325_2013 | 0.03m | +16.2pp † | +14.4pp n.s. | +18.2pp n.s. |

**Dramatic Near/Far dissociation at 0.10m**: Far plane consistently shows massive cueing (~+60pp***), while Near plane shows a large *reversal* — UNCUED outperforms CUED. This pattern is striking: when the UNCUED field is at Near depth and translates, it apparently captures attention away from the CUED field, actively reversing the normal cueing advantage.

At 0.03m (barely perceptible depth), the dissociation collapses and both planes show a modest, non-significant positive cueing effect.

### 3.5 DepthBothPlanes (N, 0.10m)

| Plane | CUED | UNCUED | Δ | p |
|-------|------|--------|---|---|
| Near | 68.8% | 34.4% | +34.4pp | ** |
| Far | 59.4% | 18.8% | +40.6pp | *** |

In this experiment both planes show strong positive cueing — opposite of the DepthBaseline Near reversal. The difference is presumably in experimental design (both planes may share delayed-onset properties here) rather than a genuine perceptual change.

### 3.6 DepthSwap50 (Z swap, 0.05m)

| Swap | CUED | UNCUED | Δ | p |
|------|------|--------|---|---|
| N | 47.7% | 35.9% | +11.8pp | n.s. |
| Z (depth swap) | 18.8% | 23.4% | −4.7pp | n.s. |

Overall | 33.3% | 29.7% | +3.6pp | n.s.
Near | 18.8% | 43.8% | **−25.0pp** | **
Far | 47.7% | 15.6% | **+32.1pp** | ***

The Z swap (earlier version, swapping all translated dots to opposite depth) completely eliminates cueing overall. The Near/Far dissociation is preserved and large: Far plane strongly positive, Near plane strongly reversed. This session connects the DepthBaseline Near reversal to the DepthSwapCtrl design.

---

## 4. Comparison: Pre-Stereo vs DepthSwapCtrl

| Condition | Cueing Δ | Comments |
|-----------|----------|----------|
| No-depth baseline (March 23) | **+33pp *** | No stereo, no swap |
| DepthSwapCtrl N binocular | **+13pp * | With stereo depth, 0.05m sep |
| DepthSwapCtrl N all-mono | +7pp n.s. | Monocular, no depth |
| DepthBaseline Far only (0.10m) | **+60pp *** | Far plane, no swap, 0.10m |
| DepthBaseline Near only (0.10m) | **−27pp** (avg) | Near plane — reversal |
| DepthSwapCtrl N Far (bino) | ~+56pp *** | Far plane, 0.05m sep |
| DepthSwapCtrl N Near (bino) | ~+12pp n.s. | Near plane, 0.05m sep |

### Key observations

**1. Adding stereo depth reduces overall cueing**: No-depth baseline ~+30pp; DepthSwapCtrl N binocular +13pp. The reduction could reflect: (a) depth complexity increasing task difficulty; (b) the Near plane reversal partially canceling the Far plane advantage in the overall average; (c) genuine reduction in temporal onset salience when depth is added.

**2. The Near/Far asymmetry is not new**: It was already present — and more extreme — at 0.10m separation. At 0.10m, Near cueing is strongly *negative* (UNCUED captures attention from the Near plane). At 0.05m (DepthSwapCtrl), Near cueing is weak but not reliably negative. The asymmetry scales with depth separation.

**3. The Near reversal is a major theoretical puzzle**: When the UNCUED field is at Near depth, it appears to capture attention more strongly than the temporal onset cue. Near stimuli may have a natural attentional priority (looming, binocular prominence) that overrides the delayed-onset advantage under some conditions. This is consistent with the DepthSwapCtrl Factor 3 result (Far > Near binocularly) but is much more dramatic at larger depth separations.

**4. Motion swap reduces but does not eliminate cueing**: +29pp (N) → +16pp (M). The cued translator can change motion type mid-trial and the onset advantage persists. Informative about the robustness of temporal cueing to mid-trial disruption.

**5. Dot50 swap has no effect**: Swapping half the dots leaves cueing intact (+29pp → +34pp n.s. change). Cueing does not depend on spatial or identity continuity of the dot field through the translation window.

---

## 5. For Literature Agent

**Key empirical facts to situate in the literature:**

1. Large temporal onset cueing effect (~30pp) in no-depth, no-swap baseline — consistent with prior object-based attention literature (overlapping dot fields without depth separation)
2. Adding stereo depth (~0.05m) reduces overall cueing to ~13pp binocularly, but Far plane alone shows ~56pp — cueing is strongly depth-plane dependent
3. Near plane at 0.10m depth separation produces a **reversal** (UNCUED > CUED) — Near translating objects capture attention counter to the temporal cue
4. ZdB > N > ZdA pattern: depth-plane continuity of the cued translator modulates cueing in an ordered way
5. Dot cueing and depth-field cueing (Factors 1 and 2) survive monocularly; Near/Far asymmetry (Factor 3) is entirely stereoscopic
6. Motion swap reduces cueing ~50%; dot identity swap has no effect

**Questions for literature agent:**
- Is there prior work on Near vs Far attentional priority in stereo displays, especially with motion stimuli?
- Does the looming/Near salience literature predict the Near reversal at large depth separations?
- Any prior work on motion cueing with overlapping surfaces where one surface is at Near vs Far disparity?
- Biased competition and depth-plane segmentation: does the literature predict that better-segmented surfaces (larger depth separation) produce stronger reversal?
