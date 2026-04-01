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

All sessions: 192/192 trials completed, 192/192 trajectories verified (mk + color + depth hashes).

**Current n per cell:**
- Binocular: n=128 per swap × cued cell (4 sessions × 32)
- Monocular R-eye: n=64 per cell (2 sessions × 32)
- Monocular L-eye: n=64 per cell (2 sessions × 32)
- All mono pooled: n=128 per cell

---

## 3. Results

### 3.1 Binocular — swap × cueing (pooled 3 sessions, n=576)

| Swap | CUED | UNCUED | Δ | p |
|------|------|--------|---|---|
| N | 54.7% | 41.4% | +13.3pp | * |
| ZdA | 48.4% | 32.8% | +15.6pp | * |
| ZdB | 54.7% | 34.4% | +20.3pp | ** |

Note: session-to-session variability is large (ZdB ranged from +3pp to +56pp across 4 sessions).

### 3.2 Master summary — three factors

| Factor | Binocular (n=768) | All mono (n=769) |
|--------|-------------------|------------------|
| 1. Dot cueing (CUED vs UNCUED) | +16.4pp *** | +7.1pp * |
| 2. Depth-field cueing (same vs diff plane) | +6.0pp † | +7.1pp * |
| 3. Depth plane (Far vs Near translation) | +10.7pp ** | +1.2pp n.s. |

### 3.3 Key interpretive points
- **Dot cueing** (factor 1): attenuated but survives monocularly — temporal onset advantage is not purely stereoscopic
- **Depth-field cueing** (factor 2): survives monocularly (*) — the advantage of translating in the delayed-onset plane has both a stereoscopic and a non-stereoscopic component
- **Depth plane / Near vs Far** (factor 3): entirely stereoscopic — absent monocularly
- **ZdB > N binocularly**: cued dot staying in plane AND companion moving into cued plane boosts performance above no-swap baseline — active depth-grouping benefit, not merely absence of disruption
- **ZdA now significant binocularly** (with n=96/cell): cueing reduced relative to ZdB but not eliminated; cued dot moving planes is costly but not catastrophic
- **Session 2 (260331_0621) was anomalous**: near-zero cueing across all conditions; possibly fatigue, vergence instability, or random variation at n=32/cell

---

## 4. Open Questions

1. **ZdB enhancement mechanism**: companion moving INTO cued plane boosts cueing above N. Active suppression of unattended surface? Depth-grouping sharpening? Needs parametric follow-up.
2. **ZdA residual cueing**: with n=96/cell, ZdA shows significant cueing (+14.6pp*). Depth-plane change is costly but the basic temporal onset advantage survives. Is the monocular geometric confound (position shift at depth change) part of the ZdA story?
3. **Near/Far asymmetry**: entirely binocular; no theoretical prediction from prior literature. Far > Near consistently. Mechanism unknown.
4. **Depth-field cueing monocular survival**: unexpected. Either (a) the translation-plane advantage has a non-stereoscopic component, or (b) the rotation reversals in ZdA/ZdB are driving it monocularly (they're visible without depth).
5. **True dichoptic nonius lines**: needed for precise vergence verification.
6. **Single subject (GS)**: all data from one observer. Generalizability unknown.

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
