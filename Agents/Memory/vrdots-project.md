# VRDots Project — Full Reference

## Overview
Object-based attention experiment on Meta Quest 3, replicating and extending
Stoner & Blanc (2010, Vision Research). Two overlapping rotating dot fields
(red/green), one with delayed onset. At translation onset, one field translates
briefly. Subject reports translation direction (8-AFC). Cueing effect: better
performance when the delayed-onset field translates (CUED) vs non-delayed (UNCUED).

## Repository
- **URL**: https://github.com/GeneStoner/UnityQuestDotStimuli.git
- **Branch**: `wip/quest-pilot`
- **Other branches**: main, rescue/from-stash, wip/analysis-and-iso-lum, wip/monitor-calibration

### Commits (wip/quest-pilot) — 9 total, 5 pushed
Pushed:
1. `417e6b2` — Add fixation exclusion zone for dot spawning
2. `63e2a77` — Add option to skip flicker calibration when data exists
3. `8bbdde7` — Fix exclusion radius (0.5→1.1deg), skip menu auto-fire (2s delay), add subject ID
4. `645510b` — Randomize trial order per session (Environment.TickCount seed), log seed
5. `f82e3cc` — Add version to data files and lower response deadzone (0.5→0.3)

Unpushed:
6. `8150123` — Add swap conditions, trajectory verification, and response improvements
7. `6ec5dda` — Remove build artifacts from tracking and update .gitignore
8. `c9995ed` — Add 50% dot swap condition (sub1↔sub3 field membership exchange)
9. `65bed96` — Log condition summary at block start for experimenter review

---

## Architecture (Unity C#)

### Core Pipeline
```
ExperimentSpec (ScriptableObject, source of truth for all params)
  └─ ExpSpecTestPhase (concrete: generates PlannedTrials, builds conditions)
       └─ TrialBlockRunner (orchestrates: spec → builder → logger)
            ├─ StimulusBuilder (dot geometry, motion stepping, boundary respawns)
            ├─ CsvLogger (TSV + meta JSON + sidecar JSON)
            ├─ TargetResponseController (thumbstick + trigger input)
            └─ DirectionalFeedbackSpot (visual response feedback)
```

### Other Components
- `StimulusConditionsLibrary` (CondLib) — MotionKind enum (RotationCW=1, RotationCCW=2, Linear=3, NonCoherent=4), SubfieldTracks struct
- `FlickerCalibrator` + `FlickerCalibrationUI` — heterochromatic flicker photometry
- `SceneSwitcher` — grip-hold menu for scene selection on Quest
- `Fixation_Controller` — fixation target rendering

### Key Script Locations
All under `/Users/genestoner1/Projects/ObjectBasedAttention/VRDots/Assets/Scripts/`

---

## Stimulus Design

### Condition Space
- 2 conditions: **CUED** (delayed field translates) / **UNCUED** (non-delayed translates)
- 8 headings: 0°, 45°, 90°, 135°, 180°, 225°, 270°, 315°
- 2 rotation configs: Rot0 (A=CW, B=CCW), Rot1 (A=CCW, B=CW)
- 2 delayed field colors: R, G (balanced)
- Swap types: None(N), Motion(M), Color(C), Dots50(D), and combinations

**Base (no swaps)**: 2 × 8 × 2 × 2 = **64 unique stimuli**
**With one swap flag**: × 2 = **128**
**With two swap flags**: × 4 = **256**
**With three swap flags**: × 8 = **512**

### Subfield Structure
- Field A (non-delayed): sub0, sub1
- Field B (delayed): sub2, sub3
- Each field has ~dotsPerField dots split across 2 subfields
- Translation = 50% coherence: one subfield Linear, other NonCoherent
- Dots50 swap: sub1↔sub3 exchange field membership at tStart

### Timing (from .asset files, 75Hz sim clock)
| Parameter | ms | Frames |
|-----------|-----|--------|
| Delayed onset | 750 | 56 |
| Pre-translation | 300 | 22 |
| Translation | 80 | 6 |
| Post-translation | 400 | 30 |
| **Total** | **1530** | **114** |

### Kinematics
- Rotation: 81 deg/sec
- Translation: 2.26 deg/sec
- Aperture radius: 3.5 deg (7 deg diameter)
- Dot size: 0.08 deg
- Dots per field: 63
- View distance: 2.0 m

### Swap Conditions
See [swap-conditions.md](swap-conditions.md) for full implementation details.
- **SwapFlags**: `[Flags] enum` — None=0, Motion=1, Color=2, Dots50=4, Depth=8, Depth50=16
- **Motion swap (M)**: rotation directions exchange at tStart
- **Color swap (C)**: field colors exchange at tStart
- **Dots50 swap (D)**: sub1↔sub3 exchange field membership at tStart
- **Depth swap (Z)**: depth planes exchange at tStart (100%)
- **Depth50 swap (Zd)**: S0↔S2 swap depth planes; color follows plane; translation stays on delayed dots
- Power-set generation for all combinations
- Inspector toggles: `includeMotionSwaps`, `includeColorSwaps`, `includeDots50Swaps`, `includeDepthSwaps`, `includeDepthPartialSwaps`
- **Key principle**: CUED always = delayed dots (sub2, sub3) translate, regardless of depth plane

### Depth System
- `depthSeparation_m`: half-separation in meters (fields placed ±depthSeparation_m from fixation plane)
- `balanceDelayedFieldDepth`: if true, generates trials for both Delayed=Near and Delayed=Far (doubles trial count)
- Near = −depthSeparation_m along transform.forward, Far = +depthSeparation_m (verified in Quest)
- `StimulusBuilder.ApplyDepthOffsets()`: called after motion step each frame, projects to local XY then adds Z offset (idempotent)
- TSV columns added: `DelayedFieldDepth` (N/F), `DepthHash32`, `DepthByFrame_SubfieldCodes`
- Sidecar schema: v5, adds `depth_payload`, `depth_hash32`, `delayed_field_depth`, `depth_separation_m`
- `depthSeparation_m = 0` → all Fixation plane, backward compatible with old assets

### Experiment Assets
Located in `Assets/ExperimentSpecs/`:
| Asset | experimentName | depthSep | balanceDepth | Swaps | Trials |
|-------|---------------|----------|--------------|-------|--------|
| Exp_Baseline | Baseline | 0 | — | none | 64 |
| Exp_MotionSwap | MotionSwap | 0 | — | Motion | 128 |
| Exp_AllSwaps | AllSwaps | 0 | — | Motion+Color | 256 |
| Exp_Dots50Swap | Dots50Swap | 0 | — | Dots50 | 128 |
| Exp_DepthCheck_005m | DepthCheck_005m_DelayedNear | 0.05m | false | none | 64 |
| Exp_DepthBaseline | DepthBaseline | 0.10m | true | none | 128 |
| Exp_DepthBothPlanes | DepthBothPlanes | 0.10m | true | none | 128 (same plane control) |
| Exp_DepthSwap | DepthSwap | 0.10m | true | Depth(Z) | 256 |
| Exp_DepthSwap50 | DepthSwap50_005m | 0.05m | true | Depth50(Zd) | 256 |

To switch: drag desired asset into TrialBlockRunner's `spec` slot in Inspector.
User preference: do NOT mix different swap levels in same experiment.

### Cursor-Jump Fix
- **Hysteresis** (`hysteresisAngleDeg = 33`): once direction latched, must exceed 33° from sector center to switch
- **Two-stage confirm** (`twoStageConfirm = true`): first trigger locks (spot → yellow), second confirms; `lockMinFrames = 10` prevents double-tap
- XR only (keyboard bypasses)
- **Important**: must wire `responseController` reference in DirectionalFeedbackSpot Inspector

### Condition Summary Utility
- `TrialBlockRunner.LogConditionSummary()` — logs all factor levels and trial counts to Unity console at block start
- Shows: conditions, rotConfigs, headings, delayedColors, swapTypes
- Shows trial counts per swap type and per condition×swap
- Lets experimenter verify design before running subjects

---

## Data Files

### Per-Session Files
Naming: `vr_dots_session_DDMMYY_HHMM.*`
Location (Quest): `/sdcard/Android/data/com.genestoner.vrdptsrebuildX.test/files/`
Location (Mac): `/Users/genestoner1/Library/Application Support/ThatsRandom/VRDotsDataFiles/`

| File | Description |
|------|-------------|
| `.tsv` | One row per trial. Columns: Trial, Experiment, Cond, RotCfg, TransDeg, RespDeg, RespIndex, RespDigit, RTf, OnsetFrame, TransStartFrame, TransEndFrame, TotalFrames, SeedA0-SeedB3, DelayedFieldColor, **DelayedFieldDepth**, SwapType, EndKey, Device, MkHash32, ColorHash32, **DepthHash32**, MotionTypeByFrame_SubfieldCodes, ColorByFrame_SubfieldCodes, **DepthByFrame_SubfieldCodes** |
| `.tsv.meta.json` | Schema v3. application_version, experiment_name, column list, session stats |
| `.tsv.sidecar.json` | **Schema v5**. Full config dump + trajectory library. experiment_spec section includes all timing/kinematics params. Each trajectory entry: stim_key, hashes, mk_payload, color_payload, **depth_payload**, **depth_hash32**, swap_type, **delayed_field_depth**, **depth_separation_m** |

**DelayedFieldDepth** values: `N` = Near, `F` = Far (single char). `depthSeparation_m = 0` → column present but all values are `N` (Fixation plane).

### Payload Format
- Motion kind: `"1|1|2|2;1|1|2|2;..."` — semicolons separate frames, pipes separate subfields
- Color: `"R|R|G|G;R|R|G|G;..."` — same structure
- Hashed with FNV-1a-32 for cross-checking

### Analysis Outputs (per session)
| File | Description |
|------|-------------|
| `_summary.txt` | Human-readable performance summary |
| `_summary.json` | Machine-readable summary with all aggregations |
| `_plots.png` | Accuracy bars + RT histograms |
| `_trajectory_examples.png` | 6 example trials with colored markers per subfield |
| `_verification_plots.png` | All unique trajectory shapes (from verify_trajectories.py) |

---

## Analysis & Verification Tools

All in `/Users/genestoner1/Projects/ObjectBasedAttention/VRDots/Tools/Analysis/`
See [verification-system.md](verification-system.md) for Methods A/B/C details.

### analyze_vr_dots_v2.py
```
python3 analyze_vr_dots_v2.py <tsv_path>
```
- Auto-loads .meta.json and .sidecar.json companions
- Uniqueness check, hash cross-check, performance summaries
- Aggregations: ALL, by_cond, by_trans_field_color, by_cond_x_trans_field_color, by_swap, by_cond_x_swap
- Outputs: _summary.txt, _summary.json, _plots.png, _trajectory_examples.png
- Backward compat: handles missing SwapType/Experiment columns
- **TODO**: add depth column support (by_depth, by_cond_x_depth aggregations)

### analyze_depth_combined.py *(new 2026-03-25)*
```
python3 analyze_depth_combined.py session1.tsv [session2.tsv ...]
```
- Pools multiple DepthBaseline sessions
- 2×2 accuracy table (Cond × DelayedFieldDepth)
- z-tests for main effect Cond, main effect Depth, Cond×Depth interaction
- Interaction formula: z = (delta_Far − delta_Near) / pooled SE
- Outputs per-session + pooled plots and stats text
- Uses stdlib only (no scipy); normal CDF via math.erf

### verify_trajectories.py
```
python3 verify_trajectories.py <sidecar.json> [--plots]
```
- Method A (hash verification) + Method C (visual plots)
- Supports all swap types: N, M, C, D, MC, MD, CD, MCD

### generate_reference_trajectories.py
```
python3 generate_reference_trajectories.py [output_path.png]
```
- Schematic diagrams: N, M, D, Z, Zd, DZ — all 6 conditions
- Dual-panel layout: top = motion type (CW→Trans coh→Trans noise→CCW), bottom = depth plane
- Delayed onset depicted: sub2/sub3 invisible before ONSET frame
- Zd: S0↔S2 depth swap; color follows plane; translation on delayed dots

### Plot Style (unified across all 3 scripts)
- Colored scatter markers: R→"#CC3333", G→"#228B22", K→skip
- S0=filled circles (s=22), S1=unfilled squares (s=48, lw=1.5)
- S2=filled triangles (s=26), S3=unfilled diamonds (s=56, lw=1.5)
- Phase markers + translation window shading

---

## Runtime Verification (Method B)

Built into C# code, always-on:
- `CsvLogger.VerifyTrialTrajectory()` — compares per-trial runtime payload hash against pre-registered trajectory library
- `TrialBlockRunner.AuditTrajectory()` — called at end of every trial in both finalize paths
- Logs `Debug.LogError` (red in Unity console) on any hash mismatch
- Zero runtime cost (one FNV hash per trial)

---

## Pilot Results

### Session 260323_1534 (pre-v0.2.0, Baseline, 64 trials)
- CUED: 65.6%, UNCUED: 15.6% — strong cueing effect (50.0pp)
- CUED+Red: 81.2%, CUED+Green: 50.0%

### Session 260324_0716 (v0.2.0, Baseline, 64 trials)
- CUED: 53.1%, UNCUED: 25.0% — cueing effect 28.1pp
- 25% adjacent-direction errors (cursor-jump) → led to hysteresis fix

### Session 260324_1010 (v0.2.0, MotionSwap, 128 trials)
- CUED No-Swap: 59.4%, CUED Motion-Swap: 46.9%
- UNCUED No-Swap: 32.3%, UNCUED Motion-Swap: 31.2%
- Cueing effect: No-Swap 27.1pp → Motion-Swap 15.7pp (swap reduces cueing)
- 1 requeued trial, 1 timeout

### Session 260325_1039 (v0.2.0, Dots50Swap, 128 trials)
- ALL: 41.7% (n=128, 127 responded)
- CUED: 57.8%, UNCUED: 25.4% — cueing effect 32.4pp
- Swap=D: 42.2%, Swap=N: 41.3% — no effect of dots50 swap
- CUED+D: 59.4%, UNCUED+D: 25.0% → D cueing 34.4pp
- CUED+N: 56.2%, UNCUED+N: 25.8% → N cueing 30.4pp
- 128/128 verified (Method A)

### Sessions 260325_1831 & 260325_1914 (DepthBaseline, 0.10m, 128 trials each)
- **Striking Cond×Depth interaction, replicated across both sessions**
- Pooled (N=254): CUED Near=27.0%, CUED Far=79.4%, UNCUED Near=53.1%, UNCUED Far=17.2%
- Near cueing: −26.1pp (z=−3.00, p=.003); Far cueing: +62.2pp (z=7.01, p<.0001)
- Interaction: z=8.12, p<.0001 — delta_Far − delta_Near = +88.3pp
- Sidecar verified: 128/128 depth assignments correct, no stimulus/analysis bug
- Interpretation: at 0.10m disparity, depth-plane salience overrides motion-based grouping

### Session 260325_2013 (DepthBaseline, 0.03m — first session at this separation)
- Depth was barely perceptible (occasionally clear on some trials)
- CUED=43.5%, UNCUED=27.0%, overall cueing +16.6pp (p=.053 trending)
- Near: +13.7pp n.s., Far: +19.4pp n.s. — interaction z=0.34, completely flat
- **Dose-response confirmed**: same code/design, only depthSeparation_m changed → effect scales with disparity
- This rules out artifact; finding at 0.10m is genuine depth×cueing interaction

### Session 260326_1649 (DepthSwap50_005m, 0.05m, 256 trials)
- **N=251** (5 warmup discarded). SwapTypes: N (no-swap) and Zd (50% depth swap)
- Note: first run had inverted CUED definition for Zd (translation assigned to depth plane, not
  delayed dots). Results reinterpreted post-hoc by flipping CUED↔UNCUED labels for Zd trials.
- **Overall**: CUED=66.1%, UNCUED=25.8%, Δ=+40.3pp (z=6.41 ***)
- **No-swap (N)**: CUED=76.6%, UNCUED=31.7%, Δ=+44.8pp (z=5.07 ***)
- **50% depth swap (Zd)**: CUED=55.6%, UNCUED=19.7%, Δ=+35.9pp (z=4.12 ***)
- **Swap attenuation**: 8.9pp, z=0.79, n.s. — Zd barely affects cueing
- **Depth breakdown (N trials)**: Near=+33.3pp (**), Far=+56.2pp (***) — both positive, no reversal
- **Depth breakdown (Zd trials)**: Near=+21.6pp (n.s.), Far=+49.7pp (***) — similar pattern
- **Interpretation**: At 0.05m, cueing follows delayed dots regardless of depth plane. Object-based
  (retinal position) not depth-plane tracking. No Near/Far sign reversal (unlike 0.10m).

### Cross-Session Pattern
- 100% motion swap: reduces cueing (27.1pp → 15.7pp) — attention disrupted
- 50% dot swap: does NOT reduce cueing (30.4pp → 34.4pp) — partial swap goes unnoticed
- Consistent with Stoner & Blanc (2010) prediction
- Depth 0.03m: interaction vanishes — barely visible
- Depth 0.05m: both planes positive (Near=+33pp **, Far=+56pp ***) — sweet spot; no reversal
- Depth 0.10m: massive Near/Far reversal (Near=−26pp, Far=+62pp) — depth dominates
- Depth50 Zd 0.05m: cueing survives (+35.9pp ***), attenuation n.s. → retinal-position story holds
- **Overall narrative**: retinal location of delayed onset drives cueing. Depth plane modulates
  strength (Far > Near trend) but does not override spatial grouping except at very large disparities.
