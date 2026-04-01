# VRDots Project Working Document

See linked files for full details:
- [vrdots-project.md](vrdots-project.md) — architecture, stimulus design, data formats, pilot results
- [swap-conditions.md](swap-conditions.md) — all swap implementations (Motion, Color, Dots50, Depth Z, Depth50 Zd, ZdA, ZdB)
- [verification-system.md](verification-system.md) — Methods A/B/C for trajectory verification
- [open-questions.md](open-questions.md) — open empirical questions and pending design decisions
- [factor-analysis.md](factor-analysis.md) — 3-factor chi-square framework: dot cueing, depth-field cueing, depth field (Near/Far)
- [agent-literature.md](agent-literature.md) — Literature/Theory agent: scope, activation, outputs → `VRDots/Agents/Literature/`
- [agent-packaging.md](agent-packaging.md) — Packaging agent: scope, activation (NOT YET ACTIVE), outputs → `VRDots/Agents/Packaging/`
- [agent-modeling.md](agent-modeling.md) — Modeling agent: PINNED, computational model of VRDots stimuli/behavior (future)

## Quick Reference
- **Project**: `/Users/genestoner1/Projects/ObjectBasedAttention/VRDots/`
- **Repo**: `https://github.com/GeneStoner/UnityQuestDotStimuli.git`
- **Branch**: `wip/quest-pilot` (uncommitted changes as of 2026-03-30)
- **Version**: 0.2.0
- **Data (Quest)**: `/sdcard/Android/data/com.genestoner.vrdptsrebuildX.test/files/`
- **Data (Mac)**: `/Users/genestoner1/Library/Application Support/ThatsRandom/VRDotsDataFiles/`
- **Analysis**: `VRDots/Tools/Analysis/` (7 Python scripts)
- **Unity Input**: Must use "Both" (Active Input Handling) — code uses legacy Input + new Input System
- **ADB pull**: `adb pull /sdcard/Android/data/com.genestoner.vrdptsrebuildX.test/files/ /tmp/quest_pull/`

## Current Status (2026-03-30)
- **NEW**: ZdA and ZdB swap conditions implemented (SwapFlags.Depth50A=32, Depth50B=64)
- **NEW**: `Exp_DepthSwapCtrl` asset — N/ZdA/ZdB, both fields red, 0.05m depth, 192 trials
- **NEW**: `plot_results_with_traj.py` — combined trajectory + performance figure
- **NEW**: `gen_hypothetical_traj.py` — 6-panel reference trajectories for ZdA/ZdB
- **NEW**: `DepthSwapCtrl_results_summary.md` — full results/conjecture writeup
- SwapFlags enum: None=0, Motion=1, Color=2, Dots50=4, Depth=8, Depth50=16, Depth50A=32, Depth50B=64
- Same-color experiments: use `balanceDelayedFieldColor=false` + COLOR_RED trials; `nonDelayedColor` forced = `delayedColor` in code to bypass Library cache issues with rgbaGreen
- **TODO**: triple-check ZdA/ZdB stimulus correctness; right-eye-closed monocular session; more sessions

## Nonius Lines & Vergence (added 2026-03-27)
- **Binocular nonius lines**: working on Quest — toggle `showNoniusLines` on `SmoothFixation`
- **True dichoptic NOT possible** via Unity shader APIs with Oculus XR Plugin on Android
- **Path to dichoptic**: OVR Compositor Layers (Meta XR SDK) — deferred
- **Field A preview**: sub0+sub1 shown static at frame-0 during WaitingForStart
- **NoniusLine.shader** in Always Included Shaders (required for Quest builds)
- **Active Fixation_Controller**: `SmoothFixation` under Main Camera

## Pilot Results Summary
| Session | Experiment | depthSep | Overall Cueing | Near Cueing | Far Cueing | Notes |
|---------|-----------|----------|---------------|-------------|------------|-------|
| 260323_1534 | Baseline | — | 50.0pp | — | — | Pre-v0.2.0 |
| 260324_0716 | Baseline | — | 28.1pp | — | — | Cursor-jump issues |
| 260324_1010 | MotionSwap | — | 27.1pp→15.7pp | — | — | 100% swap reduces cueing |
| 260325_1039 | Dots50Swap | — | 30.4pp→34.4pp | — | — | 50% swap does NOT reduce cueing |
| 260325_1831 | DepthBaseline | 0.10m | +27.5pp | −4.9pp | +59.4pp | Depth planes clear |
| 260325_1914 | DepthBaseline | 0.10m | +8.6pp | −46.9pp | +65.1pp | Depth planes clear |
| 260325_2013 | DepthBaseline | 0.03m | +16.6pp | +13.7pp | +19.4pp | Depth barely perceptible |
| 260326_1649 | DepthSwap50_005m | 0.05m | +40.3pp | +28pp (est) | +53pp (est) | Zd: +35.9pp; N: +44.8pp |
| 260330_1853 | DepthSwapCtrl_005m | 0.05m | +34.3pp | +20.8pp* | +47.9pp*** | N=+34pp**, ZdA=+12pp n.s., ZdB=+56pp*** |
| 260330_2012 | DepthSwapCtrl_005m | 0.05m | +12.2pp | +16.4pp n.s. | +8.3pp n.s. | **Monocular, L eye closed / R eye active** |
| 260331_0621 | DepthSwapCtrl_005m | 0.05m | — | — | — | Binocular session 2 |
| 260331_1530 | DepthSwapCtrl_005m | 0.05m | — | — | — | **Monocular R-eye #2, L eye closed / R eye active** |
| 260331_1705 | DepthSwapCtrl_005m | 0.05m | — | — | — | **Monocular L-eye #1, R eye closed / L eye active** |
| 260331_1734 | DepthSwapCtrl_005m | 0.05m | — | — | — | **Monocular L-eye #2, R eye closed / L eye active** |

## Key Findings (DepthSwapCtrl, 2026-03-30)
- **ZdA kills cueing**: +12.5pp n.s. (vs N=+34pp**). Cued dot changes depth plane at tStart.
- **ZdB enhances cueing**: +56.2pp***. Cued dot stays in plane; only non-coh changes depth.
- **ZdA/ZdB are matched for disruption count** — difference is specifically whether COHERENT translator changes plane
- **Far > Near** (binocular N): Far=+56pp**, Near=+12pp n.s. N-Far collapses monocularly → stereoscopic in origin
- **Monocular sessions**: 2× R-eye (L closed, n=385) + 2× L-eye (R closed, n=384) = n=769 pooled
- **Master summary** (bino n=384 vs all mono n=769):
  - Dot cueing: +19.8pp*** bino → +7.1pp* mono (attenuated but survives)
  - Depth-field cueing: +12.5pp* bino → +7.1pp* mono (survives with larger n)
  - Near/Far: +9.4pp† bino → +1.2pp n.s. mono (entirely stereoscopic)
- L-eye sessions have higher overall accuracy (44%) than R-eye (36%) — floaters in R eye visible
- Session-to-session variance in monocular cueing is large at n=192; need more data
- **Geometric confound**: depth change of 0.05m at 2m induces positional shift of 0–5 arcmin per eye (scales with eccentricity), up to 49% of translation distance at aperture edge. In ZdA, coherent translator gets this spurious shift; in ZdB only the non-coh does. Both depth-plane grouping and monocular confound accounts are viable — need R-eye test to dissociate.

## Key Gotchas
- ADB unauthorized: toggle Developer Mode off/on in Meta Horizon phone app
- thumbstickDeadzone too high -> silent canceled responses
- Skip menu auto-fires if no input delay (trigger held from scene transition)
- Fixation crosshair arms extend to 1.0deg, exclusion radius must be >= 1.1deg
- Swap toggles default false — must use correct experiment asset
- DirectionalFeedbackSpot needs responseController ref in Inspector
- Translation is 80ms (set in assets), code default was 40ms (now fixed)
- Near = −depthOffset_m along transform.forward, Far = +depthOffset_m (verified in Quest)
- CUED = delayed dots translate (NOT depth plane) — easy to confuse when implementing new swaps
- Unity Library cache can hold stale ScriptableObject values — Reimport may not fix; code-level override preferred
- `balanceDelayedFieldColor=false` path now uses COLOR_RED trials and forces nonDelayedColor=delayedColor
