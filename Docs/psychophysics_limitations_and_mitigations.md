# Psychophysical Experiment Limitations: Unity + Quest 3
### VRDots Project — Status as of 2026-04-17

This document covers known limitations of using Unity and the Meta Quest 3 for controlled psychophysical experiments, our current status on each, and what (if anything) we are doing or should do about it. It draws on the project's PDF review (VR_Psychophysics_Limitations_Unity_Quest.pdf), the current codebase audit, and project-specific findings.

---

## 1. Vergence–Accommodation Conflict (VAC)

### The issue
Quest 3 (and all current consumer HMDs) presents images at a fixed focal distance (~1.3–2 m optical) while binocular disparity can simulate any depth. The mismatch between where the eyes verge (simulated depth) and where they accommodate (fixed focal plane) causes:
- Systematic underestimation of perceived depth, especially at near distances
- Increased vergence variability, degrading stereoacuity
- Visual fatigue in long sessions

### Impact on VRDots
The VAC is the most fundamental and least fixable hardware limitation for our depth manipulation. The Near/Far asymmetry we observe (UNCUED prefers Far/uncrossed) likely has a VAC component: the Far plane (simulated behind fixation, uncrossed disparity) is closer to the accommodation optimum at 1.5 m than the Near plane (simulated in front of fixation, crossed disparity). This makes depth perception at the Far plane more stable and consistent. This confound cannot be fully eliminated with current hardware.

**Important exception:** Our primary motion cue (dot translation direction) does not rely on disparity or vergence. The attentional cueing effect (CUED > UNCUED) is measured through motion direction judgments and is largely VAC-immune. The Near/Far structural effect is where VAC applies.

### Current status
- View distance = 1.5 m — at the minimum recommended comfort threshold
- Depth separation = 0.05 m — small separation means disparity differences are modest; relative comparison is less distorted than absolute
- No per-observer geometric depth correction

### Decision
**Accept VAC as a structural limitation for the depth manipulation.** Note it as a caveat in any interpretation of Near/Far asymmetry. Future directions could include varying simulated depth (e.g., stimuli at 2 m, 3 m) to characterize the VAC contribution to the asymmetry. No code changes needed now.

---

## 2. IPD Calibration and Angular Subtense

### The issue
Stimuli are specified in degrees of visual angle and converted to meters using the nominal `viewDistance_m`. The actual angular subtense on the retina depends on each observer's IPD relative to the lens centers. An uncorrected IPD mismatch of ~5 mm at 1.5 m view distance produces a ~5% error in disparity magnitude, and a scale error in all angular size computations.

For observers with non-standard optics (e.g., GS: esophoria + prism glasses), the effective vergence resting point differs further from the nominal calibration.

### Current status
- `viewDistance_m = 1.5` is used for all visual angle calculations
- `Camera.main.stereoSeparation` is not set per observer — uses Unity default (63 mm)
- Quest 3 has a physical IPD slider (58–68 mm range) but observers are not currently instructed to adjust it
- No session-start calibration stimulus

### What to do — protocol additions
1. **Before each session:** Have observer adjust the Quest 3 IPD slider until the fixation and dot aperture are maximally sharp. Record the slider setting in session notes.
2. **Set camera stereo separation:** At session start, set `Camera.main.stereoSeparation` to the measured/adjusted IPD in meters. A simple session-start screen asking the observer to enter IPD would allow automatic correction. For now, hardcode per observer in the runner or add an IPD field to the experiment spec.
3. **Calibration stimulus (future):** Present a circle specified to subtend a known angle (e.g., 5°) at session start and confirm size matches a physical reference.

### Priority
Medium. Implement IPD-based `stereoSeparation` before adding new observers. The existing GS data has a consistent (if slightly wrong) IPD assumption throughout, so internal comparisons are valid.

---

## 3. Temporal Precision — Onset Jitter and Timestamp Accuracy

### The issue
Unity's `Time.time` is a CPU clock that does not synchronize to actual photon emission. The VR display pipeline predicts head pose before rendering, creating a gap between Unity's notion of "now" and when pixels actually appear. Published studies report onset jitter of ±11 ms uncalibrated. For an 80 ms translation window, this is ~14% of the event duration.

### Current status
- Trial timing is **frame-counted**, not clock-dependent — this is the correct approach for precise stimulus control. Translation onset, offset, and response windows are specified in frames, not milliseconds.
- Frame counting means the stimulus itself is temporally precise (within one frame period), regardless of `Time.time` drift.
- Logged response timestamps use Unity CPU time — less reliable for RT measurement, acceptable for two-alternative forced choice (we do not analyze RTs).
- `FrameRateController` uses `Application.targetFrameRate` (CPU-side request), not `OVRPlugin.displayFrequency` (GPU/display-side lock). The display Hz is set separately by Quest runtime.
- No `OVRPlugin.GetTimeInSeconds()` logging currently.
- No external photodiode calibration.

### Assessment
For our paradigm — frame-counted discrete events, TAFC with no RT analysis — temporal precision is **adequate**. The critical events (translation onset, translation offset) land on specific frames by construction. The ±11 ms jitter applies mainly to onset *latency relative to the external world*, which matters for reaction time studies but not for our within-trial direction judgment task.

### What to do
- **No urgent action required** for the current paradigm.
- Future: if we add RT-sensitive measures, log `OVRPlugin.GetTimeInSeconds()` alongside frame counts.
- Consider explicitly setting display frequency via `OVRManager` (see §4 below).

---

## 4. Display Refresh Rate: 75 Hz vs. 90 Hz vs. 120 Hz

### The issue
Quest 3 natively supports **72, 90, and 120 Hz** — not 75 Hz. Our spec field `simHz: 75` is used internally for frame count conversions (e.g., 80 ms → N frames), but it does not control the actual display rate. The display rate is set by Quest runtime or explicitly via `OVRPlugin`.

The `FrameRateController` script currently sets `targetFPS = 60` by default via `Application.targetFrameRate`. This is a CPU-side hint only. For Quest, the actual display rate should be set via `OVRManager.display.displayFrequency` or `OVRPlugin.systemDisplayFrequency`.

**Current situation:** The effective display rate on Quest is likely 72 Hz (Quest's default lowest rate), not 75 Hz. All frame-count-to-ms conversions in the code assume 75 Hz and are therefore ~4% off (13.33 ms/frame at 75 Hz vs. 13.89 ms/frame at 72 Hz). For an 80 ms window: we calculate 6 frames at 75 Hz = 80 ms, but at 72 Hz 6 frames = 83.3 ms.

### Recommendation: move to 90 Hz

| Rate | Frame period | 80 ms window | Notes |
|------|-------------|--------------|-------|
| 72 Hz | 13.89 ms | 5.76 frames (≈6) | Current likely actual rate; ~4% error vs. spec |
| 75 Hz | 13.33 ms | 6.00 frames | What code assumes; not a native Quest rate |
| 90 Hz | 11.11 ms | 7.20 frames (≈7) | Native Quest 3 rate; better temporal grain |
| 120 Hz | 8.33 ms | 9.60 frames (≈10) | Best temporal resolution; higher GPU budget |

90 Hz is the best balance for our stimuli:
- Native Quest 3 rate — display and Unity are synchronized
- 11.1 ms per frame = finer temporal grain than 72 Hz (13.9 ms)
- 80 ms translation = 7.2 frames → round to 7 frames (77.8 ms) or 8 (88.9 ms)
- Well within Quest 3's performance budget for dot stimuli
- 120 Hz is better still but tightens the frame budget and may require adjusting all ms→frame conversions

**To implement 90 Hz:**
1. Add to experiment initialization: `OVRPlugin.systemDisplayFrequency = 90f;`
2. Update `simHz` in all experiment assets from 75 → 90
3. Recompute `preTranslation_ms` and `translationDuration_ms` to give clean frame counts at 90 Hz

This is a meaningful improvement and worth doing before the next observer.

---

## 5. Luminance and Color Pipeline

### The issue
Non-linear gamma, HDR tonemapping, and post-processing can alter the luminance of rendered stimuli in ways not visible in shader color values. For dot luminance (motion by luminance contrast), color swaps (red vs. green equiluminant), and HFP calibration, the pipeline must be linear and unmodified.

### Current status — settings audit

| Setting | Required | Current | Status |
|---------|----------|---------|--------|
| Color Space | Linear | Linear (`m_ActiveColorSpace: 1`) | ✅ |
| Post-processing on camera | Off | Off (`m_RenderPostProcessing: 0`) | ✅ |
| Volume GameObjects in scene | None | None found | ✅ |
| HDR in URP asset (Mobile) | Off | **On** (`m_SupportsHDR: 1`) | ⚠️ |
| Adaptive Performance | Off | **On** (`m_UseAdaptivePerformance: 1`) | ⚠️ |
| MSAA (Mobile/Quest) | 4x | 4x (`m_MSAA: 4`) | ✅ |
| Screen Space AO (PC renderer) | Off | Present in PC renderer | N/A (Android not affected) |

**HDR enabled in URP asset:** Even with no post-processing volume, enabling HDR in the URP asset uses a 16-bit HDR color buffer internally. On Quest, this is then tonemapped to the display's color space. For dot stimuli (bright dots on dark background), the risk of nonlinearity is low at the luminance levels we use, but it is a potential issue for HFP where equiluminance is critical. **Recommend disabling HDR in `Mobile_RPAsset.asset`.**

**Adaptive Performance enabled:** Meta's Adaptive Performance framework can dynamically lower render scale or CPU/GPU clocks to maintain framerate. This introduces variability in rendering quality across trials — exactly what we want to avoid. **Recommend disabling in `Mobile_RPAsset.asset`.**

### Luminance validation (needed before HFP calibration is trusted)
The FlickerCalibration scene provides HFP-based equiluminance measurement. Before relying on it:
1. Disable HDR in the URP Mobile asset (see above)
2. Verify the flicker stimulus is rendering at the correct depth (done: 1.5 m, 2026-04-17)
3. Ideally validate dot luminance with a photometer reading through the Quest 3 lens, given known blue-channel nonlinearities in LC displays

---

## 6. Frame Drops and Asynchronous SpaceWarp (ASW)

### The issue
When Unity misses a frame deadline, Quest's ASW reprojects the last rendered frame to the current head pose. For dot motion stimuli, a dropped frame creates a visible velocity discontinuity — a spurious jump. This is distinct from the jerk artifact we fixed (which was a code bug); ASW drops are hardware/runtime events outside our control.

### Current status
- Dot stimuli are computationally trivial (shader-rendered quads, no physics, no shadow casting). Frame budget is not a concern at current complexity.
- No explicit CPU/GPU performance level locking (`OVRPlugin.suggestedCpuPerfLevel`)
- No per-trial frametime logging or dropped-frame detection
- The UP-bias artifact we investigated (2026-04-11 through 2026-04-14) was a code bug, not ASW — confirmed by the fix

### What to do
1. **Add performance level locking** at experiment start:
   ```csharp
   OVRPlugin.suggestedCpuPerfLevel = OVRPlugin.ProcessorPerformanceLevel.SustainedHigh;
   OVRPlugin.suggestedGpuPerfLevel = OVRPlugin.ProcessorPerformanceLevel.SustainedHigh;
   ```
   This prevents thermal throttling from causing mid-session frame drops.
2. **Future:** log per-trial frametime and flag/exclude dropped-frame trials. Low priority given stimulus simplicity.

---

## 7. Observer-Specific Factors

### The issue
Individual differences in vergence, accommodation, IPD, and ocular dominance all affect the stimulus as actually perceived, independent of the software specification.

### GS-specific notes
- Esophoria + prism glasses: resting vergence is biased toward crossed (near) position. This is consistent with the Far > Near preference in UNCUED trials (minimum vergence demand at Far plane). See `observer_gs_vergence.md`.
- The session 260415_2242 disparity sign bug (Near/Far labels inverted) was detected by the behavioral asymmetry being reversed — a useful sanity check.
- Right eye has floaters — R-eye monocular sessions show lower accuracy (~36%) than L-eye sessions (~44%).

### Protocol for new observers
1. Record IPD (Quest slider position + optometrist value if available)
2. Set `Camera.main.stereoSeparation` to measured IPD
3. Run a short practice block (20–30 trials) before data collection
4. Note any reports of diplopia, discomfort, or difficulty perceiving depth planes

---

## 8. Rendering Architecture — Shader-Based vs. Mesh-Based Stimuli

### Current status
VRDots uses custom GLSL shaders (SmoothCircle, NoniusLine) for dot rendering. This is the correct approach: GPU-rendered shader primitives avoid CPU-side geometry update bottlenecks and produce anti-aliased, smooth edges at any size.

The jerk artifact (2026-04-13 fix) was in the CPU-side position update logic, not the shader. Post-fix, the rendering architecture is sound.

### Outstanding item
The `Fixation_Controller` script creates child GameObjects at runtime (shader quads for ring, crosshair, nonius lines). These previously accumulated in scene files because they lacked `HideFlags.HideAndDontSave`. **Fixed 2026-04-17:** `HideFlags.HideAndDontSave` added to `CreateShaderQuad()`. Scene files cleaned of 177 (FlickerCalibration) and 441 (UpToDateScene) accumulated ghost objects.

---

---

## Reviewer Concerns: Status and Responses

### Observer sample size
Not yet an issue — additional observers are in progress. All current data are from one observer (GS, who is also the experimenter) and are treated as pilot data establishing the paradigm and effect sizes. Planned: minimum 3 naive observers before any submission.

### Fixation compliance (no eye tracking)
Quest 3 does not have an eye tracker. Fixation compliance is enforced structurally (fixation crosshair + exclusion radius of 1.1°) and will be verified indirectly in training sessions: we will include trials with fixation-dependent targets (stimuli whose detection requires accurate fixation) as an ongoing behavioral measure of fixation quality. This will be documented in the methods.

### Luminance equiluminance calibration
HFP calibration has been run and applied for the current observer (GS). Calibrated red and green intensities are loaded from disk at session start (`CalibrationData.Load()`) and applied to `spec.rgbaRed` and `spec.rgbaGreen` in `TrialBlockRunner.Awake()`.

**Flicker stimulus vs. dot aperture size:** The FlickerCalibration annulus (0.5°–2° radius) is smaller than and shaped differently from the dot aperture (3.5° radius, filled). For equiluminance calibration this is not a material concern — the calibration targets the luminance channel response to red vs. green, which is independent of spatial arrangement. The Quest 3 LCD has no local dimming at this spatial scale that would make the two sizes behave differently.

**Recalibration after 90 Hz change:** LCD panel gamma and luminance output can be refresh-rate-dependent. Moving from ~72 Hz to 90 Hz may alter the effective luminance of the stimulus colors. A recalibration session at 90 Hz should be run before continuing data collection.

### Monocular confound for depth-field cueing (F2)
The monocular sessions (2026-03-30 to 2026-03-31) were run before the stimulus artifact fix (2026-04-13). The apparent survival of the depth-field cueing effect (F2) under monocular viewing is attributable to the expansion artifact: incorrect perspective accumulation caused dots to visibly expand/contract at the depth-swap frame, providing a spurious monocular signal. Post-fix, no monocular replication has been run. Accept as artifact-driven; post-fix monocular sessions are pending.

### Multiple comparisons
The GLM framework (GLM1/GLM2, chi-square on trial counts) naturally handles the main analysis as a single model with interaction terms, reducing the multiple comparison burden. For post-hoc condition-by-condition comparisons, a pre-specified correction (Bonferroni or FDR) will be applied and reported. The distinction between confirmatory (pre-registered) and exploratory comparisons will be explicit in the methods.

### Response bias
Not a concern for percent correct in a balanced TAFC design. Because translation directions are counterbalanced (roughly 50% left / 50% right across conditions), a systematic directional response bias raises accuracy on half the trials and lowers it equally on the other half, netting zero effect on percent correct. Bias affects the criterion parameter in SDT but not sensitivity (d'), and percent correct maps to d'. No correction needed.

### Learning and practice effects across sessions
GS has accumulated extensive experience across many sessions spanning months. Performance has been non-stationary: early sessions included cursor-jump issues, artifact-contaminated stimuli, and paradigm changes. Clean post-fix data (2026-04-13 onward) represent a more stable performance regime. For naive observers, session-order effects will be explicitly examined by comparing performance across successive sessions within observer. Extended practice on unambiguous motion stimuli (clearly coherent translation, high signal-to-noise) will be conducted before data collection to ensure observers are attending and able to report accurately.

---

## Summary: Action Items

| Priority | Item | Status |
|----------|------|--------|
| Medium | IPD calibration protocol + set `stereoSeparation` per observer | Protocol addition |
| Medium | Luminance validation with photometer through lens | Future |
| Low | Log `OVRPlugin.GetTimeInSeconds()` for RT-sensitive future work | Future |
| Low | Flag dropped frames per trial | Future |
| Accepted | VAC for Near/Far depth manipulation | Noted as caveat |
| Done ✅ | Linear color space | Confirmed |
| Done ✅ | Post-processing disabled | Confirmed |
| Done ✅ | Disable HDR in `Mobile_RPAsset.asset` | 2026-04-17 |
| Done ✅ | Disable Adaptive Performance in `Mobile_RPAsset.asset` | 2026-04-17 |
| Done ✅ | CPU/GPU performance level locking (`Performance.TrySetCPULevel/GPULevel(4)`) | 2026-04-17 |
| Done ✅ | Move display to 90 Hz (`Performance.TrySetDisplayRefreshRate(90)`) | 2026-04-17 |
| Done ✅ | `simHz` updated 75→90 in all 20 experiment spec assets | 2026-04-17 |
| Done ✅ | `preTranslation_ms` updated 1050→1073 in Simult asset (90 Hz timing match) | 2026-04-17 |
| Done ✅ | FlickerCalibration depth fix (1.5 m) | 2026-04-17 |
| Done ✅ | HideFlags fix for Fixation_Controller shader quads | 2026-04-17 |
| Done ✅ | Scene ghost object cleanup (FlickerCalibration, UpToDateScene) | 2026-04-17 |

## Implementation Notes (2026-04-17)

### 90 Hz migration
`FrameRateController.cs` now uses `Unity.XR.Oculus.Performance.TrySetDisplayRefreshRate(90f)` (the authoritative Quest API) in addition to `Application.targetFrameRate = 90` as a fallback. CPU and GPU are locked to level 4 (SustainedHigh) at startup via `Performance.TrySetCPULevel(4)` and `Performance.TrySetGPULevel(4)`.

Frame count arithmetic at 90 Hz for core parameters:
- `translationDuration_ms: 80` → 7 frames (77.8 ms; was 6 frames at 75 Hz)
- `delayedOnset_ms: 80` → 7 frames (77.8 ms; was 6 frames at 75 Hz)
- `preTranslation_ms: 1000` → 90 frames (1000 ms; unchanged)
- Simult `preTranslation_ms: 1073` → 97 frames = translationStart matches standard (onset frame 7 + 90 preTranslation frames)

All 20 experiment spec assets updated. Existing TSV data files are unaffected (they record events by frame count, not simHz).

### HDR and Adaptive Performance
Both disabled in `Assets/Settings/Mobile_RPAsset.asset` (`m_SupportsHDR: 0`, `m_UseAdaptivePerformance: 0`, `m_PrefilterHDROutput: 0`). The rendering pipeline now uses a standard 8-bit LDR color buffer, consistent with linear color space and no tonemapping.

---

## Additional Potential Issues (for future review)

The following are known or plausible concerns that have not been fully resolved and should be addressed as the project matures toward publication.

1. **Recalibration after 90 Hz change.** The HFP equiluminance calibration was performed at the prior display rate (~72 Hz). LCD luminance output is potentially refresh-rate-dependent. A new calibration session at 90 Hz should be run before collecting further data. Affects color swap conditions and any luminance-contrast claims.

2. **No head stabilization.** The observer wears the headset freely with no chin rest or head mount. Head movements during trials are compensated by the headset's tracking, but residual jitter in the rendered stimulus position relative to the retina is possible. This is standard for VR psychophysics and generally accepted, but should be noted in the methods.

3. **Dot size near pixel resolution limit.** Individual dots are specified at 0.08° diameter. At 1.5 m viewing distance and Quest 3's ~20 PPD (pixels per degree) effective resolution, this is ~1.6 pixels per dot diameter. The SmoothCircle shader provides sub-pixel anti-aliasing, but dots are at the edge of the display's spatial resolution. This limits how precisely dot size can be controlled and may introduce rendering variability across dot eccentricities. Relevant if dot size is a parameter in future experiments.

4. **Stereo rendering mode affects shader availability.** The project uses Single-Pass stereo (`m_StereoRenderingPath: 0`). The NoniusLine shader uses `unity_StereoEyeIndex` to render dichoptically, which requires Multiview mode. In Single-Pass, both eyes see both nonius lines — they function as binocular fixation aids rather than true vergence error indicators. This is documented in the code but is a limitation of the nonius line design.

5. **Chromatic aberration of VR optics.** Quest 3 lenses have residual chromatic aberration after Unity's lens correction mesh. Red and green stimuli may be laterally displaced by slightly different amounts in the periphery, creating a color-dependent positional artifact. This is most relevant for the color swap conditions and the flicker calibration. Magnitude is likely small (<1 arcmin at the aperture edge) but has not been measured.

6. **Post-fix data volume.** The artifact-clean dataset (post 2026-04-13) contains ~762 trials from one observer. While effect sizes are robust for the main cueing effect, cell sizes for interaction analyses (e.g., Near×Cued×SwapType) are modest (~32 trials/cell). Confidence intervals are wide for higher-order effects. This is a pilot limitation and will be addressed with additional observers and sessions.

7. **Cross-session stimulus consistency.** Experiment parameters are specified in asset files but some scene-level settings (fixation geometry, camera position, rendering pipeline settings) can drift if scene files are edited. The 2026-04-17 cleanup (ghost object removal, depth fixes) changed the FlickerCalibration scene substantially. A protocol checklist confirming key parameter values at the start of each session is recommended.
