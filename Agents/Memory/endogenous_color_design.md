---
name: Endogenous Color Experiment Design
description: Recommended protocol for testing endogenous color attention in VRDots; Design B as primary; analysis bridge to existing metrics
type: project
---

## Motivation
DecoupledDots showed F3 (color-field cueing) = +0.0pp under exogenous onset conditions. But the Hillyard lab (Schoenfeld 2014) shows that when color is *endogenously attended*, the cascade reverses — color cortex activates first. The question: does color matter for VRDots if the observer explicitly attends to it?

## Key theoretical prediction
M-pathway carries motion+disparity but NOT color → exogenous onset cue enters via M-pathway → F2 (depth) > F3 (color) structurally. But endogenous attention can index color via the P/blob pathway (V4). If endogenous color attention matters, we should see a CUED>UNCUED effect when "cued" = "matches attended color."

## Design B (primary recommended protocol)
Block instruction: "Attend to the RED surface" (or GREEN — counterbalanced)

| Trial type | Which field translates | Label | ~n/session |
|-----------|----------------------|-------|------------|
| VALID | Red field translates | Color-CUED | 256 |
| INVALID | Green field translates | Color-UNCUED | 256 |

- 50/50 validity within each block → equal power on CUED and UNCUED
- 512 trials/session = 4 attend-red + 4 attend-green blocks × 64 trials/block
- Onset: **simultaneous** (remove exogenous confound) — verify two-surface percept survives first (Step 0)
- Optional booster: colored fixation cross throughout block to reinforce attentional set
- Swap conditions: start with N (no swap) to establish endogenous cueing effect first

## Why 50/50 not 100% validity
- 100% validity = no UNCUED trials → cannot measure cueing effect (Design A problem)
- 75% validity = ~64 invalid trials/256 → low power on UNCUED arm
- 50/50 = equal power; strong endogenous set still maintained by block instruction + colored fixation

## Step 0 before running Design B
Verify simultaneous-onset two-surface percept. Remove delayed onset; show both fields simultaneously rotating; confirm observer can identify translation in correct field. This is NOT obvious — the temporal onset cue may be necessary for the percept.

## Recommended sequence
1. Step 0: Baseline with simultaneous onset, no swap, measure accuracy
2. Design B: Block instruction + simultaneous onset + N condition
3. Design C: Restore delayed onset + block instruction → 2×2 factorial (exogenous × endogenous)
4. Design D: Simultaneous onset + block + C/Z swaps → test which swap disrupts endogenous more

## Analysis
- Primary metric: CUED% − UNCUED% (= pp, same scale as existing VRDots metrics)
- OR for cross-paradigm comparison (especially if baseline differs from delayed-onset ~12.5%)
- d' = z(P_correct) + 1.09 for 8-AFC
- GLM: `correct ~ color_endogenous` or `correct ~ onset_cue + color_endogenous + onset_cue:color_endogenous`
- Cross-paradigm: compare OR(endogenous color) vs OR(exogenous depth) = 1.89

## Prediction
- If endogenous color matters: Color-CUED > Color-UNCUED (F_endo_color > 0)
- If not: Color-CUED ≈ Color-UNCUED (same F3=0 null replicates with endogenous manipulation)
- The interaction (Design C): if endogenous adds on top of exogenous → OR multiplies; if gating → only one channel wins

## Full design doc
`Agents/Literature/endogenous_color_summary_and_design.md` — contains all designs (B, B+, C, D) plus analysis section

**Why this matters**: Distinguishes whether color is absent from the selection network entirely (drastic model modification) vs. absent only from the exogenous/M-pathway channel but accessible via endogenous/P-pathway.
