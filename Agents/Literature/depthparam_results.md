# DepthParam — Parametric Depth Separation Results
*Created: 2026-04-02. Single session per depth; second sessions planned.*

---

## Design

**Asset family**: `Exp_DepthParam_003m / 005m / 010m / 015m`
**Purpose**: Isolate the effect of depth separation on the Near/Far cueing asymmetry, with color held constant (R/G balanced) and no swap conditions.

### Stimulus parameters
| Parameter | Value |
|-----------|-------|
| View distance | 2.0 m |
| Aperture radius | 3.5° |
| Dot size | 0.08° |
| Dots per field | 63 |
| Rotation speed | 81 °/s |
| Translation speed | 2.26 °/s |
| Translation duration | 80 ms |
| Delayed onset | ~750 ms (frame 56 of 114) |
| Sim rate | 75 Hz |
| Colors | R/G balanced (`balanceDelayedFieldColor=true`) |
| Swap condition | None (pure N) |
| Response | 8-AFC heading (0°–315°, 45° steps); chance = 12.5% |
| Trials per session | 128 (32 per cell) |

### Cells
2 (CUED/UNCUED) × 2 (Near/Far delayed field) × 8 headings × 2 rotations × 1 color rep = 128 trials.

**CUED** = delayed-onset field translates coherently. **UNCUED** = non-delayed field translates.
**Near** / **Far** = depth plane of the delayed-onset (Field B) field.
Near = 1.975m (−0.025m from fixation plane, or −depthOffset), Far = 2.025m (+depthOffset), where depthOffset = half the listed separation.

### What is new relative to prior experiments
- Prior depth sessions (DepthBaseline March 25, DepthSwapCtrl March 30 – April 1) all used 0.05m or 0.10m separation and either R/G or both-red coloring, with swap conditions mixed in.
- DepthParam isolates depth separation parametrically: 0.03, 0.05, 0.10, 0.15m. Pure no-swap. R/G balanced (same color design as DepthBaseline March 25). Allows direct comparison of near reversal as a function of disparity magnitude.

---

## Sessions

| Session | Depth sep | N | Notes |
|---------|-----------|---|-------|
| 260402_0624 | 0.10 m | 128 | Session 1 |
| 260402_0656 | 0.15 m | 128 | Session 1 |
| 260402_0716 | 0.03 m | 128 | Session 1 |
| 260402_0757 | 0.05 m | 128 | Session 1 |

All: observer GS, binocular, nonius lines enabled. Second sessions per depth planned.

---

## Results

### 2×2 by depth (n=32/cell, Wilson 95% CI)

| Cell | 0.03m | 0.05m | 0.10m | 0.15m |
|------|-------|-------|-------|-------|
| CUED Far | 29/32 = **90.6%** *** | 27/32 = **84.4%** *** | 27/32 = **84.4%** *** | 27/32 = **84.4%** *** |
| UNCUED Near | 16/32 = 50.0% n.s. | 22/32 = **68.8%** * | 24/32 = **75.0%** ** | 24/32 = **75.0%** ** |
| CUED Near | 20/32 = 62.5% n.s. | 19/32 = 59.4% n.s. | 17/32 = 53.1% n.s. | 16/32 = 50.0% n.s. |
| UNCUED Far | 14/32 = 43.8% n.s. | 12/32 = 37.5% n.s. | 12/32 = 37.5% n.s. | 9/32 = 28.1% * |

*Significance: vs 12.5% chance level.*

### Cueing effect (CUED − UNCUED) by depth plane

| Depth sep | Near cueing Δ | Far cueing Δ | Overall |
|-----------|--------------|-------------|---------|
| 0.03 m | **+12.5pp** | +46.9pp | +29.7pp |
| 0.05 m | −9.4pp | +46.9pp | +18.8pp |
| 0.10 m | −21.9pp | +46.9pp | +12.5pp |
| 0.15 m | −25.0pp | +56.2pp | +15.6pp |

---

## Key observations

### 1. Far cueing is large and depth-invariant
CUED Far performance is 84–91% across all four depths, already near ceiling at 0.03m. Far cueing Δ is locked at ~+47pp from 0.05–0.15m. The delayed-onset temporal cue combines powerfully with Far depth — they are not in competition.

### 2. Near reversal crosses zero between 0.03m and 0.05m
At 0.03m, Near cueing is weakly positive (+12.5pp, n.s.). By 0.05m it has reversed (−9.4pp). By 0.10m it has saturated (−21.9pp) and does not deepen further at 0.15m. The crossover point is somewhere around 0.035–0.045m separation.

### 3. CUED Near decreases monotonically
62% → 59% → 53% → 50% as depth increases. At 0.15m, the cued translating near-plane dots are at chance. The temporal onset cue provides zero benefit when the delayed field is Near at large disparities.

### 4. UNCUED Near increases monotonically
50% → 69% → 75% → 75%. The non-delayed near-plane dots are *easier* to follow as depth increases, saturating at 75%.

### 5. UNCUED Far decreases monotonically
44% → 38% → 38% → 28%. Far plane dots without the temporal cue become harder as depth increases — possibly because attention is drawn to Far by both depth and cue together, making the absence of the cue more costly.

### 6. The overall cueing effect is misleading
Overall cueing drops from +30pp (0.03m) to +13–19pp (larger separations) because the Near reversal increasingly cancels the Far advantage. The aggregate masks two large bidirectional effects.

---

## Observer introspection

On many trials, translation was clearly seen but exact direction was uncertain. Performance was nonetheless high overall, consistent with the 45°-bin 8-AFC tolerance. Uncertainty appeared subjectively concentrated in CUED Near trials. Observer also reported a sensation resembling "swaps" that — given zero swap conditions in this design — must reflect spontaneous attentional switching between depth planes during the trial.

A separate observation: fixating the fixation point (required for vergence) naturally pulls the attentional spotlight to the fixation depth plane and rearward (Far). Objects in front of fixation (Near) are outside this natural attentional gradient. This may partially explain the Near reversal independent of any depth-plane grouping mechanism — fixation-coupled attentional depth bias may systematically disadvantage Near-plane stimuli.

---

## Open questions for literature agent

1. Is the Near/Far asymmetry in stereoscopic attention a known phenomenon? Does it reverse when fixation is set at Near depth?
2. Is the fixation-depth attentional gradient vergence-driven or disparity-driven?
3. Is the 0.03–0.05m crossover consistent with known disparity detection/segmentation thresholds at 2m viewing distance?
4. Does motion (translation) interact with depth-plane attention differently for near vs. far stimuli (looming vs. recession asymmetry)?
5. Does the literature predict a CUED Near at chance and UNCUED Near at 75% — or is this pattern novel?

---

## What to do next

- Run second session per depth to confirm pattern (n=64/cell)
- If pattern holds: the crossover depth is the key parameter — design a fine-grained session around 0.03–0.05m (e.g., 0.035m, 0.040m, 0.045m)
- Compare DepthParam (R/G) to DepthSwapCtrl N condition (both-red, 0.05m) to assess color contribution
