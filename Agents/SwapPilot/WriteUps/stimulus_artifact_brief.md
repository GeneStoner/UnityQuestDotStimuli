# Stimulus Artifact Investigation Brief
*For Opus deep-dive — 2026-04-13*

---

## Purpose

This document briefs a new analysis session on the state of stimulus verification for the VRDots experiment. One systematic artifact has already been found and fixed (the depth-swap upward-motion artifact — see Section 2). The task is to do a **comprehensive, general audit** of all possible stimulus artifacts, with particular focus on three open questions raised by the observer (Section 4).

---

## 1. Experiment Overview (brief)

Two overlapping dot fields (Field A: non-delayed, Field B: delayed onset) rotate over a fixation point. At translation onset, one field translates for 80ms. Subject reports direction (8-AFC). The "cueing" effect: better performance when the delayed-onset field translates (CUED) vs non-delayed (UNCUED). The critical manipulation is **which depth plane** each field occupies (Near = −0.05m, Far = +0.05m from fixation along the viewing axis) and whether/how depth-plane membership changes at tStart.

- View distance: 2.0m; aperture: 3.5° radius; dot size: 0.08°; 63 dots/field
- Simulation clock: 75 Hz; translation: 2.26°/sec for 80ms (6 frames)
- Depth separation: 0.05m (default); disparity ≈ 2.5 arcmin at 0.05m/2m for 63mm IPD

Key data files: `/tmp/quest_pull3/files/` (DecoupledDots, n=2051), `/tmp/quest_pull2/files/` (DepthColorLinked, n=1024), `/tmp/quest_pull4/files/` (BothFar, n=512)

---

## 1b. Additional proposed fixes — NOT YET IMPLEMENTED OR VERIFIED *

Four further code changes were drafted on 2026-04-13, implemented, and then **reverted** after it was recognized the session data they produced could not serve as a clean verification. Full details in `depth_swap_artifact_writeup.md` Section 7:

- **7a** * Perspective correction in `ApplyDepthOffsets` — scale local XY at depth-change frames by `(viewDist + z_new)/(viewDist + z_old)` to eliminate radial "pop"
- **7b** * `AlignStimulusBuilderAxis()` — alternative to Saturday's fix; aligns `transform.forward` at startup rather than using `Camera.main.transform.forward` at runtime
- **7c** * Depth-corrected translation speed — adjust `metersPerDeg` by actual plane viewing distance (±2.5% effect)
- **7d** * `balanceDelayedFieldColor` vs `linkDepthColor` gate change in `ExpSpecTestPhase.cs` — logic review needed

None of these should be re-introduced until (a) Saturday's fix is verified clean via a fresh session, and (b) each item is individually analyzed.

---

## 2. Known Artifact — Already Fixed

**The transform.forward bug** (full write-up: `depth_swap_artifact_writeup.md`):

`StimulusBuilder.ApplyDepthOffsets()` applied the ±depthOffset_m displacement along `transform.forward` (StimulusBuilder's world-space axis) instead of `Camera.main.transform.forward`. With a ~5° pitch misalignment, a depth-plane swap of 0.10m at tStart produced a one-frame upward screen-space impulse of ~0.25° ≈ 19°/sec, vs the 2.26°/sec translation signal (8.2× ratio per frame).

**Signature**: UP (90°) direction accounted for ~50% of all wrong responses in Z/CZ conditions, vs ~4–6% in N/C. Present across all sessions, both rotation configs, both depth planes.

**Fix**: One line in `StimulusBuilder.ApplyDepthOffsets()` — now uses `Camera.main.transform.forward`.

**Data exclusion**: TSV files whose `experimentName` does NOT contain `_v2` are pre-fix. Z/CZ rows from those files should not be used for quantitative depth-swap analysis. N/C rows from pre-fix files are clean.

**Key figures**:
- `Agents/SwapPilot/Figures/depth_swap_artifact.pdf` — UP bias quantification (3-page)
- `Agents/SwapPilot/Figures/decoupled_stereo_traces.pdf` — stereo-projected traces pre-fix (jump visible) vs post-fix (clean)
- `Agents/SwapPilot/Figures/stereo_trace_artifact_demo.pdf` — 3-panel demo

---

## 3. Verification Pipeline — State and Gaps

### What exists
- **Method A** (`verify_trajectories.py`): Re-implements C# `BuildEffectiveCondition()` in Python. Hashes expected mk_payload + color_payload, compares against sidecar. Verified 128/128 MotionSwap, 128/128 Dots50Swap, 64/64 Baseline. **Does NOT cover depth** (depth_payload not independently re-implemented).
- **Method B** (runtime C# audit): Every trial, FNV hash of runtime payload vs sidecar. Always on. Catches playback errors but not design errors in the spec.
- **Method C** (`verify_trajectories.py --plots`): Visual plots of all unique trajectory shapes. Shows 2D local-space XY; depth represented symbolically. **Critical gap**: does not show screen-space positions; does not invoke `ApplyDepthOffsets`.
- **Method D** (`stereo_trace_artifact_demo.py`, `decoupled_stereo_traces.py`): NEW (2026-04-11). Computes perspective projection per eye including depth offset. Shows pre-fix vs post-fix. **This is the method that would have caught the transform.forward bug immediately.**
- **Method E** (response direction monitor, `depth_swap_artifact_analysis.py`): Post-session wrong-response direction distribution. Flags if any direction >15% of wrong responses. **Should be run after every session.**

### The failure
Methods A–C all passed throughout the pre-fix data collection. The bug was invisible to them because:
- Methods A/B verify logical trajectory design (which subfield does what), not physical screen-space output
- Method C shows local XY positions; `ApplyDepthOffsets` is never called in the simulation
- The bug lived entirely in the physical rendering layer, below what any existing check examined

**Lesson**: We had no check on what the observer's eyes actually see. Method D fills this gap for depth-related artifacts; Method E provides a behavioral early-warning signal.

### What Method D does NOT yet cover
- Rendering artifacts (dot size variation with depth, contrast changes)
- Frame-timing jitter (missed frames, dropped frames on Quest)
- Dot respawn behavior at aperture boundary: when a dot exits and re-enters, does it get the correct depth assignment?
- Eye-specific rendering on the Quest (left vs right eye timing offsets, lens distortion)

---

## 4. Open Investigation Questions

### 4a. General audit: are there other stimulus artifacts?

The transform.forward bug was found by chance (observer report). A systematic audit should examine:

1. **`StimulusBuilder.cs` in full** — all coordinate transformations, all calls that use `transform.*` rather than camera-aligned coordinates, any frame-order dependencies (does `ApplyDepthOffsets` execute before or after the position update? before or after dot respawn?).

2. **Dot respawn behavior** — when a dot crosses the aperture boundary, it is respawned at a new position. Is the new dot assigned the correct depth plane and color? Is there a one-frame flash at the wrong depth?

3. **Frame-zero preview** — Field A (sub0+sub1) is shown static at frame-0 positions during `WaitingForStart`. Is the depth offset applied correctly during this preview?

4. **Depth offset during rotation** — `ApplyDepthOffsets` is called every frame including during pure rotation (before tStart). Does the constant application every frame interact with the rotation in any way that could produce a visible cue?

5. **Swap timing** — at tStart (frame 78), depth planes are exchanged. Is this swap applied atomically in a single frame, or is there a one-frame transition state? Check `StimulusBuilder`'s swap logic carefully.

6. **Color/depth link** — in `DepthColorLinked` experiments, color follows depth plane. Does the color swap and depth swap happen on the same frame? A one-frame desynchrony would create a spurious trial state.

### 4b. Is the Near vs Far cueing asymmetry a stimulus artifact?

**Observer's question**: Could Unity somehow render one depth plane's translations as more difficult to perceive — independently of genuine depth perception?

This is a critical question because the Far > Near asymmetry is a key finding (Far cueing consistently larger; Near cueing sometimes negative). If it has a stimulus origin, the finding is wrong.

**Mechanisms to audit:**

1. **Constant positional offset from residual `transform.forward` pitch** (pre-fix only):
   Even in N (no swap) conditions, `ApplyDepthOffsets` was called every frame. With 5° pitch:
   - Near (z = −0.05m): `y_bias = −0.05 × sin(5°) ≈ −0.0044m` → Near field shifted DOWN ~0.13°
   - Far (z = +0.05m): `y_bias = +0.05 × sin(5°) ≈ +0.0044m` → Far field shifted UP ~0.13°
   
   This is a STATIC offset (constant each frame) so it produces no illusory motion — but it means the two fields are spatially offset ~0.26° vertically on screen. Could a systematic vertical separation between fields affect which field is more "salient" as a translation cue? This is worth computing and plotting.

2. **Post-fix residual**: The fix uses `Camera.main.transform.forward`. Is the camera truly aligned with the HMD's optical axes? If there is any residual pitch/roll in `Camera.main`, a smaller version of the same effect would persist. This should be verified by examining the Quest's camera transform conventions.

3. **Dot size and density with depth**: Dots at Far (+0.05m) are rendered at slightly greater distance (2.05m vs 2.00m). Their projected angular size is ~2.5% smaller. If dot conspicuity scales with angular size, Far dots are very slightly less visible. This is a negligible effect (~0.002° dot size change) but should be quantified.

4. **Vergence demand asymmetry** (observer-specific): GS has documented esophoria (prism glasses, not worn in VR). Crossed disparity (Near plane) imposes vergence demand in the direction of GS's habitual deviation, while uncrossed (Far plane) is easier to maintain. This is a perceptual confound, not a stimulus artifact, but it is observer-specific and should be flagged prominently.

5. **`balanceDelayedFieldDepth` assignment**: Verify that the Near/Far assignment across trials is truly balanced. In the data, do we see equal trial counts for Delayed=Near and Delayed=Far? Check the TSV `DelayedFieldDepth` column distributions.

6. **Translation magnitude by depth**: The translation is applied in angular units (2.26 deg/sec). But the dots exist in a 3D space. Does the translation move dots by the same angular amount regardless of depth plane? In other words, is the 2.26°/sec specified at the viewing distance of the dot (accounting for depth), or at the nominal view distance? If translation is computed in local XY meters and then projected, dots at Far (2.05m) will have slightly smaller angular translation than dots at Near (1.95m) for the same local displacement. Quantify this difference.

### 4c. Is depth loss on some trials a stimulus issue?

**Observer's report**: On some portions of some trials — especially those involving depth swaps — the red and green dots did not appear to be separated in depth. The depth separation appeared to collapse temporarily.

**Possible stimulus causes:**

1. **Frame-order bug in depth assignment during swap**: At tStart, the depth plane swap is applied. If there is a single frame where dots are rendered at z=0 (fixation plane) — e.g., because the swap flag is set before or after `ApplyDepthOffsets` is called — this would produce one frame of zero disparity, effectively a depth "blink." Check the exact frame order: `StepRotation` → `StepTranslation` → `ApplyDepthOffsets` → `Render`. Is the swap applied before or after the depth offset computation?

2. **Dot respawn at neutral depth**: As noted above, newly respawned dots may not immediately get the correct depth assignment. If many dots respawn simultaneously (e.g., after a direction change), you could briefly lose depth separation.

3. **Near=−z and Far=+z sign check**: Verify the sign convention in `ApplyDepthOffsets`. Near = `−depthOffset_m` (toward viewer) and Far = `+depthOffset_m` (away from viewer). If the sign is ever inverted (e.g., a conditional branch that produces Near>0), both fields would briefly appear at the same depth. Check all code paths.

4. **`bothFieldsSamePlane` flag**: The experiment spec has a `bothFieldsSamePlane` field. Verify this is `false` in all experimental assets and that it is not accidentally set true in any code path.

5. **Depth offset early-return condition**: `ApplyDepthOffsets` returns early if `(depthOffset_m == 0f && depthBias_m == 0f)`. Could `depthOffset_m` ever be zero mid-trial through some unexpected code path?

6. **Perceptual alternative**: Vergence adaptation during a long trial could reduce perceived depth. This would be perceptual, not stimulus. But confirming the stimulus is correct allows ruling this in as the explanation.

---

## 5. Code Locations

All scripts in `Assets/Scripts/`:
- `StimulusBuilder.cs` — core stimulus code; `ApplyDepthOffsets()` is the locus of the known bug
- `ExperimentSpec.cs` / `ExpSpecTestPhase.cs` — parameter definitions; `depthSeparation_m`, `depthBias_m`, `bothFieldsSamePlane`, `balanceDelayedFieldDepth`
- `TrialBlockRunner.cs` — wires spec parameters to builder; check `builder.depthOffset_m = spec.depthSeparation_m` and `builder.depthBias_m = spec.depthBias_m`
- `CondLib.cs` (`StimulusConditionsLibrary`) — `DepthPlane` enum (Near, Far, Fixation), `SubfieldTracks`

Analysis tools in `Tools/Analysis/`:
- `decoupled_stereo_traces.py` — stereo projection simulation (Method D); use as template for any new artifact check
- `depth_swap_artifact_analysis.py` — response direction monitor (Method E)
- `stereo_trace_artifact_demo.py` — 3-panel demo

---

## 6. Suggested Audit Approach

1. Read `StimulusBuilder.cs` in full, tracing the frame-by-frame call order
2. For each concern in Section 4, produce either: (a) a mathematical argument that the effect is negligible, or (b) a simulation/figure showing the effect
3. For 4a: check all `transform.*` usages in `StimulusBuilder.cs`; check respawn logic; check swap atomicity
4. For 4b item 1: extend `decoupled_stereo_traces.py` to plot N-condition centroid Y positions for Near vs Far fields (should be symmetric offsets of equal magnitude)
5. For 4b item 6: compute `angular_translation = local_translation_m / z_world` for Near and Far separately; quantify the difference
6. For 4c: trace the exact call order at tStart; identify any frame where depth assignment could be incorrect

---

## 7. What a Clean Bill of Health Looks Like

After the audit, we want to be able to say:
- All `transform.*` usages in `ApplyDepthOffsets` are eliminated; camera-aligned axis confirmed
- Dot respawn correctly assigns depth plane; no frame of incorrect depth on respawn
- Depth swap is atomic (applied in one frame, before rendering that frame)
- N-condition Near/Far translation magnitude difference is quantified and ≤ 1% of signal
- N-condition positional offset from any residual pitch is quantified and symmetric
- `DelayedFieldDepth` trial counts are balanced (verified in TSV data)
- `bothFieldsSamePlane=false` confirmed in all experimental assets
- Far > Near asymmetry is not explained by any of the above stimulus factors
