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
| 260401_1313 | 2026-04-01 | Binocular | 51.0% | Session 3; ZdA trend |
| 260401_1349 | 2026-04-01 | Binocular | 44.3% | Session 4; ZdB weak this session |
| 260401_1541 | 2026-04-01 | R-eye (L closed) | 33.9% | Mono R #3; weak session, +5.2pp n.s. |
| 260401_1705 | 2026-04-01 | L-eye (R closed) | 39.6% | Mono L #3; +4.2pp n.s.; ZdA −6.2pp |

All sessions: 192/192 trials completed, 192/192 trajectories verified (mk + color + depth hashes).

**Current n per cell:**
- Binocular: n=128 per swap × cued cell (4 sessions × 32)
- Monocular R-eye: n=96 per cell (3 sessions × 32)
- Monocular L-eye: n=96 per cell (3 sessions × 32)
- All mono pooled: n=192 per cell (6 sessions × 32)

---

## 3. Results

### 3.1 Binocular — swap × cueing (pooled 4 sessions, n=768)

| Swap | CUED | UNCUED | Δ | p |
|------|------|--------|---|---|
| N | 55.5% | 42.2% | +13.3pp | * |
| ZdA | 48.4% | 32.8% | +15.6pp | * |
| ZdB | 55.5% | 35.2% | +20.3pp | ** |

Note: session-to-session variability is large (ZdB ranged from +3pp to +56pp across 4 sessions).

### 3.2 Master summary — three factors

| Factor | Binocular (n=768) | Mono R-eye (n=577) | Mono L-eye (n=576) | All mono (n=1153) |
|--------|-------------------|--------------------|--------------------|-------------------|
| 1. Dot cueing (CUED vs UNCUED) | +16.4pp *** | +8.4pp * | +4.2pp n.s. | +6.3pp * |
| 2. Depth-field cueing (same vs diff plane) | +6.0pp † | +3.6pp n.s. | +7.6pp † | +5.6pp † |
| 3. Depth plane (Far vs Near translation) | +10.7pp ** | −2.2pp n.s. | +1.4pp n.s. | −0.4pp n.s. |

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
