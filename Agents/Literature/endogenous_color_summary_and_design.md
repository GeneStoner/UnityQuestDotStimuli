# Endogenous Color Attention: Summary and Experimental Designs
*Literature agent — 2026-04-06*

---

## Part 1 — Summary

### The Color Story in Three Acts

**Act 1 — Exogenous null (DecoupledDots).**
With a temporal onset cue, color-field cueing = +0.0pp (OR=1.00, p=.994, n=1026). The onset event drives the M-pathway (color-blind), entering the V1 point-set network at the direction/disparity end. Color is activated secondarily, ~60ms after motion (Schoenfeld 2014), as a downstream consequence of surface selection — not a driver of it. Boosted color cortex has no path back to the direction-discrimination read-out (read-out bottleneck). The contingent-capture framework (Folk et al. 1992) independently predicts this: color is outside the task-relevant attentional set when the cue is an onset transient.

**Act 2 — The Schoenfeld reversal (endogenous).**
When observers voluntarily attend to the color-defined surface in the transparent-motion paradigm (Schoenfeld et al. 2014, *Nature Neuroscience*), the MEG activation sequence completely reverses: color-selective cortex fires first (~150ms), motion cortex follows ~60ms later. The inter-module gap is identical (~60ms) in both directions. The model explanation: the cascade direction depends on the *entry point* of the attentional signal into the mutual excitation network. Top-down color instruction → color-indexed feature-similarity gain (Saenz et al. 2002) → blob/V4 neurons first → cross-column propagation → direction columns. Because the cascade now terminates at direction columns — the read-out — a behavioral effect is predicted. The exogenous failure and endogenous success are two sides of the same coin.

**Act 3 — The experiment.**
If color-based endogenous attention can select a transparent surface, the direction-discrimination cueing effect should be recoverable without any onset transient — using color as the sole selection cue. Expected magnitude: smaller than the +22pp exogenous effect (blob→interblob propagation is slower and weaker than the direct M-pathway signal), probably +5–15pp, requiring ~256+ trials/condition. The Saenz et al. (2002/2003) result says color and motion feature-similarity gain are quantitatively equal when attention is endogenous — so the magnitude should be detectable.

### Key Model Insight

The point-set model requires **one asymmetry** to account for all the data: the exogenous selection signal enters the network via the M-pathway, which is direction/disparity-indexed, not color-indexed. Everything else follows:

| | Exogenous onset | Endogenous color |
|---|---|---|
| Entry point | Direction/disparity columns (M-pathway) | Color columns (top-down feature-similarity gain) |
| First module activated | Motion cortex (~150ms) | Color cortex (~150ms) |
| Second module (+60ms) | Color cortex | Motion cortex |
| Read-out reaches MT? | Yes (direct) | Yes (via cross-column propagation) |
| Behavioral effect? | +22pp *** | Predicted +5–15pp |
| Color-field cueing (F3)? | 0.0pp | N/A — color IS the cue |

The model does not need to say mutual excitation is absent for color — only that it is not the *initial* recipient of the exogenous signal. Endogenous attention can bypass this constraint entirely because top-down feedback is feature-agnostic.

---

## Part 2 — Experimental Designs

### The Core Problem

The naive version — "tell the observer to attend to the red surface and remove the onset cue" — fails because color validity is missing. Without a predictive relationship between color and the upcoming translation, color carries no information and there is no incentive for color-based attention to improve performance. And the simplest block design (Design A, 75% validity) compounds the problem: at 75% you get only 25% invalid trials, giving roughly 64 invalid trials per 256-trial session. The *entire* VRDots paradigm is built on the CUED − UNCUED contrast; without an adequately powered UNCUED analog, the endogenous result is incommensurable with the existing data.

The right frame: **valid trials = Color-CUED; invalid trials = Color-UNCUED**. These must be balanced enough to yield comparable power on both cells.

---

### Design B — Block Instruction, Balanced Valid/Invalid (Start Here)

**Closest precedents**: Motter (1994) block-level color instruction; Valdes-Sosa et al. (1998) sustained surface attention; Anllo-Vento & Hillyard (1996) feature attention on top of sustained set.

#### Core Logic

Keep block-level instruction — the observer is told which color surface to attend for an entire block, maximizing sustained endogenous set strength. Within each block, set validity to **50/50**: the instructed color translates on exactly half the trials, the other color on the other half. The observer doesn't know trial-by-trial which will occur, but maintains a steady attentional set for the instructed color throughout. Valid/invalid is the test; the block instruction is the cue.

```
Block instruction: "Attend to the RED surface throughout this block"

VALID trial:   [750ms rotation] → [red surface translates 80ms] → [response]  = Color-CUED
INVALID trial: [750ms rotation] → [green surface translates 80ms] → [response] = Color-UNCUED

Color cueing effect = VALID% − INVALID%    [directly comparable to CUED% − UNCUED%]
```

#### Stimulus Parameters

| Parameter | Value | Notes |
|-----------|-------|-------|
| Surface onset | **Simultaneous** — both fields appear together | Removes exogenous onset confound; the delayed onset IS an exogenous cue and will override color instruction |
| Pre-rotation | 750ms | Matches existing VRDots; sufficient for endogenous attention to engage (needs ~300ms) |
| Translation | 80ms, same kinematics and speed | Direct continuity with existing data |
| Response | 8-AFC, same as current | Direction judgment |
| Depth separation | 0.05m | Keep depth structure present; balance Near/Far across color |
| Colors | Red / Green | Same as current; balance delayed-field color across trial factors |
| Validity | 50/50 within block | Equal power on Color-CUED and Color-UNCUED |

**Simultaneous onset risk**: The delayed onset may help parse the two-surface percept. Run a simultaneous-onset N-only session first (no instruction, no validity, just report direction). If baseline is well above chance (~25–35% correct, chance = 12.5%), the percept is adequate. If near chance, consider a minimal **100ms SOA** between the two field onsets — long enough to parse surfaces, too short for exogenous onset cueing to operate (onset cueing requires >150ms to generate a selection signal; see vergence_latency_note.md for timescales).

#### Block and Trial Structure

- **Block types**: Attend-Red and Attend-Green, alternated across the session
- **Trials per block**: 64 (32 valid, 32 invalid; 4 headings × 2 rot-configs × 2 depth assignments × 2 conditions = 32 per cell)
- **Blocks per session**: 4 Attend-Red + 4 Attend-Green = **512 trials/session**
- **Valid cell n**: 256; **Invalid cell n**: 256 — equal power

#### The CUED/UNCUED Analog Is Exact

| VRDots exogenous | Endogenous Design B |
|---|---|
| CUED (delayed-onset field translates) | VALID (instructed-color surface translates) |
| UNCUED (non-delayed field translates) | INVALID (non-instructed surface translates) |
| Cueing effect = CUED% − UNCUED% | Color-cueing effect = VALID% − INVALID% |
| Baseline: UNCUED % correct | Baseline: INVALID % correct |

Both are measured in pp on the same 8-AFC task against the same 12.5% chance floor. Direct comparison is valid once OR is used to control for any baseline difference between simultaneous-onset and delayed-onset designs (see §Part 3 analysis).

#### Optional Booster: Trial-Level Pre-Cue

If the 50/50 block effect is present but small, add a **pre-trial colored fixation change** (100ms color change on fixation cross, occurring 500ms before surface onset) that is always congruent with the block instruction. This reinforces the trial-level color set just before stimulus onset (Anllo-Vento 1996) without adding new information. A slight version: make the fixation cross colored throughout the block (red or green) — a constant reminder of the attentional set at zero cost.

---

### Design B+ — Trial-Level Pre-Cue with Independent Validity

Once Design B establishes the basic effect, add a trial-level color pre-cue with **independent validity** decoupled from the block instruction. This separates sustained endogenous set (block-level) from trial-specific expectation (pre-cue).

- Pre-cue: 200ms colored ring at fixation, 500ms before surface onset
- Pre-cue validity: 75% (pre-cue color matches which surface translates on 75% of trials)
- Pre-cue validity is independent of block instruction
- Analysis: pre-cue-valid% − pre-cue-invalid%, within block-instruction condition
- Total cue-to-translation SOA: 500 + 300 = 800ms — well beyond the ~300ms endogenous attention onset

The trial-level effect tells you how much additional benefit comes from a trial-specific prediction on top of the sustained block set. The difference between Design B (block-only) and B+ (block + pre-cue) estimates the incremental value of trial-level color prediction.

Minimum n: ~600 trials/session at 75% pre-cue validity → ~150 pre-cue-invalid per session. Two sessions → n~300 per invalid cell. Feasible but burdensome; run only if the block-level effect in Design B is significant.

---

### Design C — Exogenous + Endogenous Combined (Tests Additivity)

Once the basic endogenous color effect is established, the most theoretically important experiment is whether exogenous onset and endogenous color are **additive, subadditive, or superadditive**.

**Structure**: Restore the delayed onset (exogenous cue), and layer endogenous color attention on top via block instruction. Creates a 2×2 factorial:

| | Color-VALID | Color-INVALID |
|---|---|---|
| **Onset-CUED** | Both cues agree → largest | Cues conflict → intermediate |
| **Onset-UNCUED** | Cues conflict → intermediate | Both cues against → smallest |

**If additive**: onset and color contribute independent pp increments — two separate pathways. Supports the two-entry-point model.

**If subadditive**: the two cues partially share capacity or converge on the same neural population — the mechanisms overlap.

**If superadditive**: color attention pre-boosts the blob columns of the correct surface; when the onset fires and propagates through mutual excitation, it finds those columns already elevated — amplified cascade. This would be the strongest evidence for the point-set mutual excitation model.

Trial budget: 4 cells × 128 trials = 512 trials/session. Feasible.

---

### Design D — Swap-Disruption Double Dissociation (Mechanistic Test)

The definitive model test. Simultaneous onset + block color instruction (Design B) + C and Z swap conditions.

**Logic**: Exogenous cueing enters via direction/disparity columns → disrupted by depth swaps (Z), not color swaps (C). Endogenous color cueing enters via blob/color columns → should be disrupted by color swaps (C), less disrupted by depth swaps (Z). A Mode × Swap interaction would directly validate the two-entry-point architecture.

**Conditions (2 modes × 3 swaps)**:

| | **N** | **C** (color swap at tStart) | **Z** (depth swap at tStart) |
|---|---|---|---|
| **Exogenous** (DecoupledDots data) | CUED+N: ~43% | CUED+C: ~49% | CUED+Z: ~28% |
| **Endogenous** (Design D) | VALID: ? | **predicted ↓↓** | **predicted < exo disruption** |

The exogenous row is already filled in from DecoupledDots raw means. Design D fills in the endogenous row. If C is more disruptive and Z is less disruptive in the endogenous condition, the double dissociation is complete.

Trial budget: 3 swaps × 2 (valid/invalid) × 32 base = 192 trials per block; 4 blocks = 768 trials per session. Plan 2 sessions.

---

### Recommended Sequence

| Step | Design | Goal | Est. sessions |
|------|--------|------|--------------|
| 0 | Simultaneous-onset baseline (no instruction, no validity) | Verify two-surface percept survives | 1 |
| 1 | **Design B** — block instruction, 50/50, N only | Establish basic endogenous color cueing effect | 2–3 |
| 2 | **Design C** — restore onset + block instruction, 2×2 | Test additivity of exogenous + endogenous | 1–2 |
| 3 | **Design D** — simultaneous onset + block + C/Z swaps | Swap-disruption double dissociation | 2–3 |
| 4 | **Design B+** — add trial-level pre-cue | Trial-level dynamics (if B+ effect is needed) | 2 |

---

## Part 3 — Analysis: Connecting to Existing VRDots Metrics

### 3.1 Primary Behavioral Metric: pp Accuracy (Direct Continuity)

The existing VRDots analysis reports accuracy as percentage correct and computes cueing effects in **pp**: CUED% − UNCUED%. Design B produces the identical metric: VALID% − INVALID%. Both are measured on the same 8-AFC direction task against the same 12.5% chance floor.

**No transformation required for direct comparison at the pp level.** A color-endogenous effect of +8pp is on exactly the same scale as the exogenous depth-field cueing effect of +12.5pp.

### 3.2 Odds Ratios for Cross-Baseline Comparison

The simultaneous-onset baseline accuracy will likely differ from the delayed-onset baseline (the two-surface percept may be weaker, pushing overall accuracy lower). Raw pp effects will therefore be smaller not because the selection mechanism is weaker, but because the task is harder. Odds ratios correct for this:

```
OR_endogenous = odds(correct | valid) / odds(correct | invalid)
```

This is the same OR reported in the DecoupledDots GLM (dot_cue OR = 3.07; depth_cue OR = 1.89; color_cue OR = 1.00). The endogenous color OR can be directly compared to those values regardless of baseline differences. For any comparison between endogenous and exogenous effect sizes, **use OR, not pp**.

### 3.3 GLM: Same Logistic Regression Framework

DecoupledDots GLM:
```
correct ~ dot_cue + depth_cue + color_cue
```

Design B GLM (endogenous, simple):
```
correct ~ color_endogenous   [color_endogenous = 1 if valid, 0 if invalid]
```

Design B with depth breakdown:
```
correct ~ color_endogenous * depth_field
```

Design C (additivity test):
```
correct ~ onset_cue + color_endogenous + onset_cue:color_endogenous
```

The interaction coefficient in Design C tests additivity. Positive = superadditive; near-zero = additive; negative = subadditive. Same chi-square / LRT framework as existing analyses.

### 3.4 Signal Detection: d′ for Hillyard-Style Comparison

Hillyard lab papers report d′ or ERP amplitudes, not raw accuracy. Convert for comparability:

For the 8-AFC task, under equal-variance Gaussian SDT:
```
d′ = z(P_correct) − z(1/8)
   = z(P_correct) + 1.09    [since z(0.125) ≈ −1.09]
```

where z(·) is the inverse normal CDF. This gives a sensitivity measure independent of response bias and normalizes for the simultaneous-onset difficulty change.

**Cueing effect in d′**: d′(valid) − d′(invalid). This directly parallels the N1 amplitude difference for attended vs. unattended surfaces in Khoe et al. (2005). Catak et al. (2022) established the behavioral N1 correlation in the exogenous paradigm — the endogenous design should replicate and extend this.

**Practical note**: The existing DecoupledDots data can also be expressed in d′ to establish the baseline for comparison before running any endogenous sessions.

### 3.5 ERP Targets (If Recording Is Added)

If electrophysiology is added, the specific components to target and their predicted pattern:

| Component | Window | Scalp | Exogenous prediction | Endogenous color prediction |
|-----------|--------|-------|----------------------|-----------------------------|
| **C1** | 75–110ms | Medial occipital | Present (M-pathway onset) | **Absent** — no transient onset event |
| **N1** | 160–210ms | Lateral occipital-parietal | Present, modulated by cueing (Khoe 2005) | Present but later-onset, different distribution |
| **Selection Negativity (Nd)** | 150–350ms | Feature-specific | Dorsal (motion/parietal; Anllo-Vento 1996) | **Ventral (color/inferior occipital-temporal)** |
| **P300** | 300–500ms | Parietal | Tracks accuracy | Tracks accuracy |

**The key prediction**: endogenous color instruction should produce an **inferior occipital-temporal selection negativity** — the ventral Nd that Anllo-Vento & Hillyard (1996) showed for color attention — rather than the dorsal N1 that Khoe et al. (2005) reported for exogenous onset cueing. This ventral/dorsal dissociation is the ERP signature of blob-pathway vs. interblob-pathway entry into the selection network.

If MEG is used, the Schoenfeld (2014) reversal should be directly observable: color cortex activating before motion cortex in the endogenous condition, reversed relative to any exogenous comparison run in the same session.

### 3.6 Depth Breakdown: Does Near/Far Asymmetry Change?

The exogenous VRDots data show Far > Near (+9.4pp† binocular, driven by stereoscopic mechanism). This asymmetry likely reflects disparity processing in the dorsal stream. If endogenous color selection enters via the ventral stream, the prediction is:

- **Endogenous color**: reduced or absent Near/Far asymmetry — the ventral (blob→V4) stream is less strongly modulated by disparity asymmetry than the dorsal stream
- **Exogenous onset**: preserves Far > Near — same dorsal mechanism as in existing data

This is a secondary prediction of the two-entry-point model and can be tested by including `depth_field` as a factor in the Design B GLM.

### 3.7 Complete Comparison Table

| Metric | Exogenous (DecoupledDots) | Endogenous (Design B) | Comparable? |
|--------|--------------------------|----------------------|-------------|
| Primary effect (pp) | CUED% − UNCUED% = +22.3pp | VALID% − INVALID% | Direct pp comparison |
| Effect size (OR) | dot_cue OR = 3.07 | color_endogenous OR | Baseline-agnostic; preferred for cross-paradigm |
| Sensitivity (d′) | Computable from existing data | Native to endogenous design | Normalizes difficulty change |
| Depth modulation | Far > Near (+9.4pp†) | Predicted reduced Near/Far | Qualitative prediction |
| ERP: early | C1 at 75–110ms (dorsal) | No C1; later Nd | Qualitative dissociation |
| ERP: selection | N1 dorsal (Khoe 2005) | Predicted Nd ventral (Anllo-Vento 1996) | Scalp-distribution dissociation |
| Feature cascade | Motion first → color +60ms | Color first → motion +60ms | Direct Schoenfeld 2014 replication |
| Additivity with onset | N/A | Testable in Design C | Mechanistic |
| Swap disruption profile | Z disrupts, C does not | C disrupts, Z less so | Double dissociation (Design D) |

---

*See also*: `endogenous_color_hillyard.md` (literature and model), `color_cueing_review.md` (exogenous null), `color_model_conjecture.md` (model theory), `decoupled_dots_results.md` (exogenous baseline)
