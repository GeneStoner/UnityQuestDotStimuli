# VRDots DepthSwapCtrl — Running Experimental Status
*Last updated: 2026-04-01*

---

## 1. Experiment Design

**Asset**: `Exp_DepthSwapCtrl` (`DepthSwapCtrl_005m`)
**Version**: 0.2.0, branch `wip/quest-pilot`
**Device**: Meta Quest (binocular or monocular)

### Stimulus parameters
| Parameter | Value |
|-----------|-------|
| View distance | 2.0 m |
| Aperture radius | 3.5° |
| Dot size | 0.08° |
| Dots per field | 63 |
| Depth separation | 0.05 m (Near=1.975m, Far=2.025m) |
| Rotation speed | 81 °/s |
| Translation speed | 2.26 °/s |
| Delayed onset | 750 ms |
| Pre-translation hold | 300 ms |
| Translation duration | 80 ms |
| Sim rate | 75 Hz |
| Colors | Both fields RED (same color; `balanceDelayedFieldColor=false`) |
| Response | 8-AFC heading direction (0°–315° in 45° steps) |
| Trials per session | 192 |

### Trial structure
- **Onset** (frame 56): delayed field (S2/S3) appears; Field A (S0/S1) has been visible since frame 0
- **tStart** (frame 78): swap applied; translation begins
- **tEnd** (frame 84): translation ends; rotation continues

### Swap conditions (N/ZdA/ZdB × CUED/UNCUED × Near/Far × 2 rotations × 8 headings × 1 rep = 192)

| Swap | What happens at tStart | Cued dot depth | Non-coh depth |
|------|------------------------|----------------|---------------|
| N | Nothing | stays in onset plane | stays in onset plane |
| ZdA | S0↔S2 exchange depth | moves to OPPOSITE plane | unchanged |
| ZdB | S1↔S3 exchange depth | stays in onset plane | moves INTO cued plane |

ZdA and ZdB are matched for number of depth swaps (2 dots each) and rotation reversals (2 each). The ONLY difference: whether the coherent (cued) translator changes depth plane.

### Three analysis factors
| Factor | Definition | Levels |
|--------|-----------|--------|
| 1. Dot cueing | Delayed-onset dots translate | CUED vs UNCUED |
| 2. Depth-field cueing | Coherent translator in same plane as delayed-onset field | same vs different |
| 3. Depth plane | Absolute depth of coherent translator | Far vs Near |

Correctness: `TransDeg == RespDeg (mod 360)`. Chance = 12.5% (1/8).

### Fixation / vergence
- Binocular nonius lines: implemented (`showNoniusLines` on `SmoothFixation`) but **not true dichoptic** — both eyes see both segments via Unity renderer
- True dichoptic nonius requires OVR Compositor Layers (Meta XR SDK) — **not yet implemented**
- Field A preview shown static during `WaitingForStart` (frame-0 positions)

---

## 2. Sessions

| Session | Date | Eye | Overall acc | Notes |
|---------|------|-----|-------------|-------|
| 260330_1853 | 2026-03-30 | Binocular | 46.4% | Session 1 |
| 260330_2012 | 2026-03-30 | R-eye (L closed) | 33.2% | Mono R #1; right eye has floaters |
| 260331_0621 | 2026-03-31 | Binocular | 38.0% | Session 2; weaker effects |
| 260331_1530 | 2026-03-31 | R-eye (L closed) | 39.1% | Mono R #2 |
| 260331_1705 | 2026-03-31 | L-eye (R closed) | 45.3% | Mono L #1 |
| 260331_1734 | 2026-03-31 | L-eye (R closed) | 43.2% | Mono L #2 |
| 260401_1313 | 2026-04-01 | Binocular | 51.0% | Session 3; good performance |
| 260401_1349 | 2026-04-01 | Binocular | 44.3% | Session 4 |
| 260401_1541 | 2026-04-01 | Binocular | 33.9% | Session 5; performance collapse — 4th session same day (fatigue) |
| 260401_1705 | 2026-04-01 | Binocular | 39.6% | Session 6; also weak (fatigue) |

All sessions: 192/192 trials completed, 192/192 trajectories verified (mk + color + depth hashes).

**Current n per cell (as of 260401_1705):**
- Binocular: n=192 per swap × cued cell (6 sessions × 32)
- Monocular R-eye: n=64 per cell (2 sessions × 32)
- Monocular L-eye: n=64 per cell (2 sessions × 32)
- All mono pooled: n=128 per cell (4 sessions × 32)

*Note: sessions 260401_1541 and 260401_1705 were originally logged as monocular but confirmed binocular from TSV data — only 4 monocular sessions on record (260330_2012, 260331_1530, 260331_1705, 260331_1734).*

---

## 2b. DepthParam Sessions (2026-04-02)

New experiment family: `Exp_DepthParam_003m/005m/010m/015m`. R/G balanced, no swaps, 128 trials, 32/cell. Purpose: parametric depth separation to map the Near/Far cueing asymmetry. Full results in `depthparam_results.md`.

| Session | Depth | N | Overall | CUED Far | UNCUED Near | CUED Near | UNCUED Far |
|---------|-------|---|---------|----------|-------------|-----------|------------|
| 260402_0716 | 0.03m | 128 | 62.5%** | 90.6%*** | 50.0% n.s. | 62.5% n.s. | 43.8% n.s. |
| 260402_0757 | 0.05m | 128 | 62.5%** | 84.4%*** | 68.8%* | 59.4% n.s. | 37.5% n.s. |
| 260402_0624 | 0.10m | 128 | 62.5%** | 84.4%*** | 75.0%** | 53.1% n.s. | 37.5% n.s. |
| 260402_0656 | 0.15m | 128 | 56.3%* | 84.4%*** | 75.0%** | 50.0% n.s. | 28.1%* |

Near cueing Δ: +12.5pp → −9.4pp → −21.9pp → −25.0pp (crosses zero between 0.03 and 0.05m).
Far cueing Δ: +46.9pp at all depths (saturated).

---

## 3. Results

### 3.1 Binocular — swap × cueing (pooled 6 sessions, n=1152)

| Swap | CUED | UNCUED | Δ | sig |
|------|------|--------|---|-----|
| N | 51.0% | 41.1% | +9.9pp | † |
| ZdA | 42.7% | 31.2% | +11.5pp | * |
| ZdB | 51.6% | 35.4% | +16.1pp | ** |
| **Overall** | **48.4%** | **35.9%** | **+12.5pp** | **\*\*\*** |

Pattern: ZdB > ZdA ≈ N. Session-to-session variance large (individual sessions ranged +5–34pp overall).

### 3.1b Monocular — swap × cueing (pooled 4 sessions, n=769)

| Swap | CUED | UNCUED | Δ | sig |
|------|------|--------|---|-----|
| N | 49.2% | 39.8% | +9.4pp | n.s. |
| ZdA | 35.9% | 35.9% | **+0.0pp** | n.s. |
| ZdB | 46.1% | 34.1% | +12.0pp | * |
| **Overall** | **43.8%** | **36.6%** | **+7.1pp** | **\*** |

**ZdA collapses to 0.0pp monocularly — ZdA effect is entirely stereoscopic.**

### 3.2 Near/Far asymmetry

| | Binocular | Monocular |
|--|-----------|-----------|
| Near cueing | **−5.9pp n.s.** | +1.8pp n.s. |
| Far cueing | **+30.9pp \*\*\*** | +12.5pp * |
| Interaction | **+36.8pp \*\*\*** (z=6.50) | +10.7pp * |

Near inversion (negative cueing) is binocular; absent monocularly. Far dominance is partially monocular, mostly stereoscopic.

### 3.3 Key interpretive points
- **Dot cueing** (factor 1): survives monocularly (*) — temporal onset advantage is not purely stereoscopic; attenuated vs binocular
- **Depth-field cueing** (factor 2): † in all mono pooled (n=1153) and † in L-eye alone (n=576); R-eye sessions weaker (n.s.) — L-eye data more reliable given floaters in R eye. Effect appears to survive monocularly at marginal level.
- **Depth plane / Near vs Far** (factor 3): entirely stereoscopic — absent monocularly in all subgroups
- **ZdB > N binocularly**: cued dot staying in plane AND companion moving into cued plane boosts performance above no-swap baseline
- **ZdA significant binocularly**: cueing reduced relative to ZdB but not eliminated; cued dot moving planes is costly but not catastrophic
- **R-eye sessions weaker overall** (35.4%) vs L-eye (44.3%) — consistent with floaters in R eye; R-eye mono data noisier
- **Session 2 (260331_0621) was anomalous**: near-zero cueing across all conditions; possibly fatigue, vergence instability, or random variation at n=32/cell

### 3.4 Response error analysis

Error distribution (% of trials):

| Error | Binocular | Mono R | Mono L |
|-------|-----------|--------|--------|
| 0° (correct) | 44.9% | 35.4% | 44.3% |
| ±45° (adjacent) | 23.2% | 28.4% | 22.4% |
| ±90° | 10.0% | 11.3% | 12.2% |
| ±135° | 11.3% | 15.9% | 13.5% |
| 180° (opposite) | 10.5% | 8.8% | 7.6% |

- **±45° errors elevated in R-eye mono**: boundary errors increase from 23% to 28% — consistent with a weaker or noisier motion signal landing near category boundaries rather than cleanly in one bin
- **180° errors not elevated monocularly**: axial ambiguity (mis-assigning rotation direction) does not appear to be the primary source of monocular errors
- **Cardinal vs diagonal**: R-eye accuracy is *lower* for cardinal headings (30.8%) than diagonal (39.9%) — the reverse of binocular and L-eye; suggests possible display distortion rotating the effective response wheel under monocular R-eye viewing

### 3.5 Response biases

Substantial direction-specific response biases observed (deviation from flat 12.5%):

| Condition | Over-represented | Under-represented |
|-----------|-----------------|-------------------|
| Binocular | 270° (+6.1pp), 225° (+3.5pp) | 315° (−4.4pp), 135° (−2.7pp) |
| Mono R-eye | 45° (+6.7pp), 90° (+3.6pp) | 180° (−4.2pp), 270° (−3.0pp) |
| Mono L-eye | 90° (+5.2pp), 0° (+3.9pp) | 315° (−4.4pp), 135° (−3.4pp) |

**Key observation**: The bias pattern differs substantially across viewing conditions — and crucially, the binocular default (lower-left: 270°/225°) is *avoided* under R-eye monocular viewing, replaced by an upper-right bias (45°/90°). This shift between conditions is consistent with display distortion rotating the apparent response wheel geometry under monocular viewing rather than a stable perceptual bias.

**Interpretive caution**: The appropriate uncertainty here is high. Bias patterns could reflect display geometry, motor habits, idiosyncratic perceptual priors, or some combination. With n=1 observer and varying session conditions, separating these is not possible from the current data. The main implication is that percent correct conflates perceptual signal strength with response bias, and the monocular "deficit" may partly reflect a response-stage artifact rather than a purely perceptual one. A neural measure (e.g., motion-onset ERP) would bypass the response stage and provide a cleaner index of motion coherence detection.

---

## 4. Open Questions

1. **ZdB enhancement mechanism**: companion moving INTO cued plane boosts cueing above N. Active suppression of unattended surface? Depth-grouping sharpening? Needs parametric follow-up.
2. **ZdA residual cueing**: with n=96/cell, ZdA shows significant cueing (+14.6pp*). Depth-plane change is costly but the basic temporal onset advantage survives. Is the monocular geometric confound (position shift at depth change) part of the ZdA story?
3. **Near/Far asymmetry**: entirely binocular; no theoretical prediction from prior literature. Far > Near consistently. Mechanism unknown.
4. **Depth-field cueing monocular survival**: uncertain with current data. Was * at n=769 mono, n.s. at n=961. Awaiting final L-eye session.
5. **True dichoptic nonius lines**: needed for precise vergence verification.
6. **Single subject (GS)**: all data from one observer. Generalizability unknown.
7. **Display distortion under monocular viewing**: response bias patterns shift substantially across binocular vs R-eye vs L-eye conditions, suggesting the response wheel geometry may appear rotated or distorted when one eye is covered. Mechanism unclear (IPD correction, lens distortion, or other). Needs investigation before monocular data can be fully trusted.
8. **Rotation-induced axis bias**: rotating dot surround may pull perceived translation direction toward the tangential, particularly near heading/rotation congruence boundaries. Not dominant in current error distributions but plausible as a within-trial variance source.
9. **Percent correct as a limited measure**: response biases and potential display distortion mean accuracy conflates perceptual signal with response-stage artifacts. A neural measure would bypass the response stage entirely.
10. **ERP as a measure of enhanced processing — object-level enhancement**: if attentional enhancement operates at the object level, it should boost neural responses to *all* motions of the cued field, not just the coherent translation. Specifically:
    - **Motion-reversal ERP at tStart** (ZdA/ZdB): rotation reversals in the cued field should generate a large, stimulus-locked direction-change response — enhanced if the cued object is preferentially processed. This doesn't require the subject to detect the translation direction at all.
    - **Delayed-onset ERP at frame 56**: motion onset of Field B should be enhanced for CUED vs UNCUED conditions.
    - **Non-coherent motion response**: even the S3 non-coherent dots (part of the cued field in CUED trials) may show enhanced processing.
    - **Implication**: an ERP study could detect attentional enhancement even on trials where the subject fails to identify the heading — completely sidestepping response bias and display distortion problems. The motion-reversal VEP is a particularly robust signal (large amplitude, well-localized in time) and is a natural target.
    - **Caveat**: if non-coherent and reversal motions are equally enhanced, this complicates the interpretation of *what* the cueing effect indexes — it may be object-level gain rather than specifically enhanced coherent motion detection.
11. **Headset comfort and ergonomics**: document best practices for extended VR use — pressure from headset frame and prescription lens insert, neck strain from headset weight, vergence-accommodation dissociation (VAD) and eye strain, session length limits. Relevant for scaling to multi-subject data collection. Assign to Packaging agent when active.

---

## 5. Pending Stimulus/Software Work

| Item | Priority | Status |
|------|----------|--------|
| True dichoptic nonius (OVR Compositor Layers) | High | Not started |
| Minimum pre-trigger vergence hold (Mod 3) | Medium | Not started |
| analyze_vr_dots_v2.py depth column support | Low | Not started |
| Commit wip/quest-pilot | High | Pending |

---

## 6. Analysis Scripts

| Script | Purpose |
|--------|---------|
| `analyze_vr_dots_v2.py` | Standard per-session analysis |
| `plot_results_with_traj.py` | Trajectory + performance combined figure |
| `gen_hypothetical_traj.py` | Reference trajectories for N/ZdA/ZdB |
| `verify_trajectories.py` | Hash verification of mk/color/depth payloads (all sessions 192/192 ✓) |
| `bino_vs_mono_comparison.png` | Key comparison figure (in /tmp/quest_pull2/) |
| `three_factors_bino_vs_mono.png` | 3-factor bar chart (in /tmp/qp4/) |
| `depthswapctrl_all_sessions_bars.png` | Per-session overview (in /tmp/qp4/) |

---

## 7. Data Locations

- **Quest**: `/sdcard/Android/data/com.genestoner.vrdptsrebuildX.test/files/`
- **Mac pull dirs**: `/tmp/quest_pull/`, `/tmp/quest_pull2/`, `/tmp/qp3/`–`/tmp/qp7/` (per-session pulls)
- **Mac local**: `/Users/genestoner1/Library/Application Support/ThatsRandom/VRDotsDataFiles/`
- **ADB pull**: `adb pull /sdcard/Android/data/com.genestoner.vrdptsrebuildX.test/files/ /tmp/qpN/`

---

## 2c. DepthColorLinked Sessions (2026-04-04)

New experiment: `Exp_DepthColorLinked` (`DepthColorLinked_005m`). Two-color design: Near plane = Red (#CC3333), Far plane = Green (#228B22), linked to depth plane via `linkDepthColor=1`. No-swap N condition excluded (`includeNoSwapBaseline=0`). R/G balanced across trials. 256 trials/session: ZdA+ZdB × CUED/UNCUED × Near/Far × 2 RotCfg × 8 headings.

### Stimulus parameters (changes from DepthSwapCtrl)
| Parameter | DepthSwapCtrl | DepthColorLinked |
|-----------|---------------|-----------------|
| Colors | Both red | Near=Red, Far=Green |
| linkDepthColor | — | 1 (color follows depth at T_S) |
| Swap conditions | N + ZdA + ZdB | ZdA + ZdB only |
| Trials/session | 192 | 256 |
| balanceDelayedFieldColor | 0 | 1 |

### Sessions

| Session | Date | N | Overall acc | Notes |
|---------|------|---|-------------|-------|
| 260404_0940 | 2026-04-04 | 256 | 31.2% | Session 1 — strong ZdNoi>>ZdCoh dissociation |
| 260404_1123 | 2026-04-04 | 256 | 33.6% | Session 2 — flatter pattern; UNCUED elevated |
| 260406_1001 | 2026-04-06 | 256 | 27.7% | Session 3 — similar to S2; UNCUED+ZdNoi elevated (Far asymmetry) |

### Factor framing (new 2×2 design)

| Factor | Definition |
|--------|-----------|
| F1 Dot Cueing ✓/✗ | Does the delayed-onset dot field translate? (CUED vs UNCUED) |
| F2 Depth Cueing ✓/✗ | Does translation occur at the depth where the cued field appeared? |

Mapping:
- Depth✓ = CUED+ZdNoi OR UNCUED+ZdCoh (translator at DFD during window)
- Depth✗ = CUED+ZdCoh OR UNCUED+ZdNoi (translator at opp(DFD))

### Results — Combined (n=768, 3 sessions)

*Updated 2026-04-06 to include session 260406_1001.*

| Condition | k | n | % correct | pp > chance | sig |
|-----------|---|---|-----------|-------------|-----|
| CUED + Depth✓ (ZdNoi) | 91 | 192 | 47.4% | +34.9pp | *** |
| CUED + Depth✗ (ZdCoh) | 61 | 192 | 31.8% | +19.3pp | *** |
| UNCUED + Depth✓ (ZdCoh) | 38 | 192 | 19.8% | +7.3pp | ** |
| UNCUED + Depth✗ (ZdNoi) | 46 | 192 | 24.0% | +11.5pp | *** |

**F1 Dot Cueing: +17.7pp *** **
**F2 Depth Cueing: +5.7pp * **

Dot cueing effect split by Depth Cueing:
- Depth✓ conditions: CUED+ZdNoi vs UNCUED+ZdNoi = +23.4pp
- Depth✗ conditions: CUED+ZdCoh vs UNCUED+ZdCoh = +12.0pp
- Difference (~11pp) is the F1×F2 interaction: swapping depth+color costs roughly half the cueing advantage

### Between-session variability

| | Session 1 (260404_0940) | Session 2 (260404_1123) | Session 3 (260406_1001) | Combined |
|--|-----------|-----------|-----------|---------|
| CUED+ZdNoi | +46.9pp *** | +28.1pp *** | +29.7pp *** | +34.9pp *** |
| CUED+ZdCoh | +18.8pp *** | +26.6pp *** | +12.5pp ** | +19.3pp *** |
| UNCUED+ZdCoh | +3.1pp n.s. | +15.6pp *** | +3.1pp n.s. | +7.3pp ** |
| UNCUED+ZdNoi | +6.2pp † | +14.1pp *** | +14.1pp *** | +11.5pp *** |
| F1 Dot Cueing | +28.1pp *** | +12.5pp * | +12.5pp * | +17.7pp *** |
| F2 Depth Cueing | +12.5pp * | +1.6pp n.s. | +3.1pp n.s. | +5.7pp * |

Session 1 had the strongest F2; sessions 2 and 3 are similar to each other and weaker on F2. F1 is consistent across sessions 2 and 3.

### The UNCUED+Depth✗ (ZdNoi) apparent anomaly — resolved

UNCUED+ZdNoi performs at +11.5pp *** rather than near chance. Initial concern: this is the "hardest" cell (non-delayed field translates AND translator is NOT at the delayed field's depth). Breakdown reveals the source:

| Split | k | n | % correct | pp > chance | sig |
|-------|---|---|-----------|-------------|-----|
| DFD=Near (translator=Far) | 32 | 96 | 33.3% | +20.8pp | *** |
| DFD=Far (translator=Near) | 14 | 96 | 14.6% | +2.1pp | n.s. |
| DFC=Green (delayed=Far) | 29 | 96 | 30.2% | +17.7pp | *** |
| DFC=Red (delayed=Near) | 17 | 96 | 17.7% | +5.2pp | † |

**Explanation**: This is not a cueing anomaly — it is the Far > Near translation depth asymmetry (established in DepthParam) bleeding through. In UNCUED+ZdNoi, when DFD=Near the non-delayed (translating) field is at Far depth, and Far translation is intrinsically easier regardless of cueing. When DFD=Far the translating field is Near, and performance is at chance — exactly as expected. The DFC split mirrors this because Near=Red and Far=Green are linked in this experiment. The cell-level average is inflated by the easy DFD=Near sub-cell.

**Implication**: F2 Depth Cueing as computed conflates the depth-plane identity factor with the absolute Far > Near performance asymmetry. A cleaner analysis would compute F2 separately for Far-translating and Near-translating sub-cells, or residualize out translation depth before computing depth cueing effects.

### 90° heading spike in UNCUED+ZdNoi
45.8% correct at 90° (upward) vs 12.5–29% at other headings. Consistent with a known observer heading response bias toward vertical/upward directions, plus a possible perceptual bias toward vertical translation detection. Not specific to this condition — present across conditions to varying degrees.

### Comparison to DepthSwapCtrl (all-red, ZdA+ZdB only, matched)

| Experiment | CUED | UNCUED | Cue effect |
|-----------|------|--------|-----------|
| DepthSwapCtrl (all-red, n=384) | +34.6pp | +20.8pp | +13.8pp *** |
| DepthColorLinked (R/G, n=768) | +27.1pp | +9.4pp | +17.7pp *** |

Larger cueing effect with color is driven by lower UNCUED baseline, not higher CUED. Color differentiation makes UNCUED harder (harder to accidentally track non-cued field). Pattern stable across 3 sessions.

### Main finding
Dot cueing effect is significantly reduced when the translating dots change depth plane AND color simultaneously (ZdCoh vs ZdNoi): +34.9pp vs +19.3pp under CUED. F2 Depth Cueing is significant pooled across 3 sessions (+5.7pp *) but driven primarily by the CUED conditions — UNCUED cells are near chance throughout (once Far > Near asymmetry is accounted for). Color vs depth contributions remain confounded; a color-only swap experiment is needed to dissociate them.

### New code
- `Assets/Scripts/ExpSpecTestPhase.cs`: new fields `linkDepthColor` (bool) and `includeNoSwapBaseline` (bool)
- `Assets/ExperimentSpecs/Exp_DepthColorLinked.asset`: new experiment asset
- `Tools/Analysis/depth_color_linked_fig.py` → `Agents/Figures/depth_color_linked_results.png`
- `Tools/Analysis/depth_color_linked_writeup.py` → `Agents/WriteUps/depth_color_linked_writeup.pdf` (3 pages: design+trajectories, results, interpretation)
- `Tools/Analysis/depth_color_linked_traj.py` → `Agents/Figures/depth_color_linked_traj.png` (frame-by-frame trajectories with R/G depth-color coding)

---

## 2d. DecoupledDots Sessions (2026-04-06 — 2026-04-07)
*Last updated: 2026-04-09*

**Asset**: `Exp_DecoupledDots_005m` (delayTranslator=1) + `Exp_DecoupledDots_Inv_005m` (delayTranslator=0, labels behaviorally inverted before analysis)
**Key change from DepthColorLinked**: `linkDepthColor=0` — color and depth swap independently. Adds full N and C swap conditions.

### Sessions

| Session | Asset | Label inversion | N valid |
|---------|-------|-----------------|---------|
| 260406_1532 | DecoupledDots_005m | Normal | 514 |
| 260406_1754 | DecoupledDots_Inv_005m | **INVERTED** | 512 |
| 260407_0643 | DecoupledDots_Inv_005m | **INVERTED** | 512 |
| 260407_0731 | DecoupledDots_005m | Normal | 513 |
| **Combined S1–S4** | | | **2051** |

**S4 anomaly**: dot cueing only +4.8pp n.s.; elevated UNCUED baseline. Included without exclusion.

### Raw accuracy (S1–S4 combined, n=2051)

| Swap | CUED | UNCUED | Δ | sig |
|------|------|--------|---|-----|
| N | 48.4% | 24.9% | +23.5pp | *** |
| C | 50.0% | 26.5% | +23.5pp | *** |
| Z | 23.4% | 14.4% | +9.0pp | ** |
| CZ | 25.0% | 19.5% | +5.5pp | † |

Z and CZ approximately halve the dot-cueing effect relative to N and C.

### GLM1 — Additive (S1+S2, n=1026)

F1 Dot cueing: **+22.3pp *****, F2 Depth-field cueing: **+12.5pp *****, F3 Color: **+0.0pp n.s.**
Color is null. The DepthColorLinked "color effect" was entirely the depth factor.

### GLM2 — Interaction model (S1–S4, n=2051) — KEY RESULT

Model: `correct ~ F1 + F2 + F3 + F4 + F1:F2 + F1:F4 + F2:F4`

| Term | AME (pp) | p |
|------|----------|---|
| F1 Dot cueing (main) | −5.3 | n.s. |
| F2 Depth-field cued (main) | −6.1 | n.s. |
| F3 Color-field cued | +0.9 | n.s. |
| F4 Translator Near | **−15.3** | *** |
| **F1×F2 Dot × Depth** | **+32.7** | *** |
| F1×F4 Dot × Trans-depth | **+8.9** | * |
| F2×F4 Depth × Trans-depth | **−12.4** | ** |

**The central finding**: F1 and F2 are synergistic — neither does much alone; performance is high only when both are present. Equivalently: depth swaps (Z, CZ) applied to CUED trials disrupt dot cueing by severing depth-plane continuity of the attentional object. This directly recapitulates ZdA (coherent translator changes depth = kills cueing) from DepthSwapCtrl. Translator Near/Far asymmetry (F4 = −15pp ***) is a robust secondary finding.

Full write-up and analysis tables: `Agents/Literature/decoupled_dots_results.md` → `Agents/WriteUps/decoupled_dots_results.pdf`

### Analysis scripts

`decoupled_dots_glm.py`, `decoupled_dots_glm2.py`, `decoupled_dots_combined_analysis.py`, `decoupled_dots_traj.py`, `decoupled_N/C/Z/CZ_traj.py`, `decoupled_dots_N_2x2.py`, `decoupled_dots_field_properties.py`, `decoupled_dots_results_pdf.py`

