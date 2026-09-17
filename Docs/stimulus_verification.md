# VRDots Stimulus Verification
*Making sure both labs show the stimulus we intend.*

A stimulus can go wrong at three levels, and each needs its own check:

1. **Definition**: the code, spec asset and project settings that were built.
2. **Rendering**: what the app actually drew, frame by frame.
3. **Delivery**: what reached the observer's eye through the display, lenses and headset fit.

Two labs are showing the same stimulus only when all three levels match. Items marked **(to build)** don't exist yet; references are at the end.

## The headset: Meta Quest 3

Both sites use the **Meta Quest 3** (not the Quest 3S or Quest Pro, which are different headsets). Confirm at each site with `adb shell getprop ro.product.model`.

| Property | Quest 3 | What it means for VRDots |
|---|---|---|
| Display | Two LCD panels, 2064 × 2208 pixels per eye, about 25 pixels per degree; no local dimming [1] | Dot luminance does not depend on other screen content (the Quest Pro's local dimming would) |
| Refresh rate | 72, 90 or 120 Hz [1] | We run at 90 Hz (11.1 ms per frame). 120 Hz (8.3 ms) is possible but changes every frame count, so both sites must use the same rate for a whole study |
| Render resolution | Meta's default render scale of 1.0 gives 1680 × 1760 per eye, below the panel; raising it to the panel's resolution (about 1.23) "provides a significant increase in image clarity" [2] | **VRDots uses 1.23** (set 2026-09-17 after an A/B test in the headset; sharper, not dramatically). Sessions before that date rendered at 1.0 and were upsampled |
| Setting render scale | In URP, `UniversalRenderPipelineAsset.renderScale`; `XRSettings.eyeTextureResolutionScale` is for the Built-in pipeline [2] | VRDots uses URP: the value is `m_RenderScale` in `Assets/Settings/Mobile_RPAsset.asset` |
| Dynamic resolution | Optional; changes render resolution with GPU load; enabled through `OVRManager` [3] | VRDots does not use `OVRManager`, so resolution is fixed. Keep it that way |
| Lenses | Pancake lenses, about 110° horizontal field of view [1] | Image quality and luminance are best at the lens center; our stimulus is within 3.5° of center |
| IPD | Wheel adjusts lens spacing continuously, 58–70 mm [4] | Set it for each observer; record the value |
| Eye relief | Buttons beside the lenses move the facial interface nearer or farther [5] | Use the same setting for every session of an observer; record it |

## 1. Definition: build the same thing at both sites

| What must match | How to make it match | How to check it |
|---|---|---|
| Code | Both labs build from the same **tagged commit** (e.g. `stim-v1.0`), never from uncommitted changes | `git describe --tags` and `git status` (must be clean) before building |
| Unity | Exactly **6000.2.7f2** | Unity Hub → Installs |
| Project settings | Keep them in git and never edit them locally: `ProjectSettings/`, `Assets/XR/Settings/OculusSettings.asset`, `Assets/Settings/Mobile_RPAsset.asset` | `git status` shows no changes there |
| Experiment | The same spec asset in the Spec slot | The sidecar's `experiment_spec` block, compared between sites |
| Scene toggles | Use Screen Space Shader and Use Fixed AA Shader both ticked | The sidecar's `stimulus_builder` block |
| Render settings | `m_RenderScale: 1.23` and `m_MSAA: 4` in `Assets/Settings/Mobile_RPAsset.asset`, 90 Hz | The sidecar's `display` block: `render_scale`, `msaa_samples`, `eye_texture_px`, `refresh_rate_hz`, `device_model` |
| Colors | Red/green isoluminance measured for each observer | The sidecar's `calibration_colors` block |

**Checking that two sites match:** compare the sidecar files from one session at each site. Apart from the timestamp, the `experiment_spec`, `stimulus_builder` and `build_date` blocks should be identical. Trials with the same seeds (`SeedA0`–`SeedB3`) produce the same dot trajectories, and `MkHash32` fingerprints each trial's trajectory, so matching hashes mean matching motion.

The sidecar's `display` block records the headset model, render scale, MSAA, eye-texture size and refresh rate from 2026-09-17 on. **(to build)** Also log the git commit hash, Unity version, headset OS build and foveation level. Today only `build_date` identifies the build.

## 2. Rendering: confirm the app drew the specified stimulus

**Reconstruct the dots from the logged seeds.** The dot positions come from Unity's random number generator. `Agents/SwapPilot/Analysis/dotnet_random.py` reproduces that generator exactly (checked with `verify_rng/`). `reconstruct_animation.py` then rebuilds any trial frame by frame. From the reconstruction, measure:

- dots per field and per subfield
- aperture radius and the dot-free zone around fixation
- rotation and translation speeds (deg/s), translation direction
- onset delay and translation duration (in frames)
- which dots swap color or motion, and when

Each measured value should equal the spec. This checks the stimulus logic, not the display.

**Check the timing on every trial.** The TSV logs `TransStartFrame`, `TransEndFrame`, `PresentedDurFrames` and `PresentedDurMs`. At 90 Hz, one frame is 11.1 ms, so an 80 ms translation lasts 7 frames (78 ms).

⚠️ **`PresentedDurMs` is not measured.** It is the frame count multiplied by the spec's `simHz` (90), so it always reads as if the stimulus ran at 90 Hz. Since 2026-09-17 three measured columns sit beside it:

| Column | Meaning | Expected |
|---|---|---|
| `TransDurMsMeasured` | Wall-clock time from the first to the last translation frame | Within a frame or two of `PresentedDurMs` |
| `TransRenderedFrames` | Rendered frames actually shown across that window | Equal to `PresentedDurFrames` when the display keeps up; fewer means simulated frames were never displayed |
| `MaxFrameGapMs` | Longest gap between rendered frames in the trial | Near the display period (11.1 ms at 90 Hz); a large value is a hitch |

**What a dropped frame does here.** The stimulus advances on a time accumulator (`_accum += Time.deltaTime`), not one step per rendered frame, so dropped frames do **not** stretch the stimulus: the motion keeps correct real-world timing, but some simulated frames are never shown. At a 72 Hz display with `simHz` 90, roughly one simulated frame in five is skipped. Brief stimuli are then displayed more coarsely than intended, which is a reason to fix the rate, not to discard the timing.

**Also confirm the display rate.** The sidecar's `display` block records `refresh_rate_hz` and `refresh_rate_confirmed`. If `refresh_rate_confirmed` is false the headset ran at another rate (72 Hz is the Quest default). Known cause of a mid-session drop from 90 to 72 Hz: the tracking cameras losing confidence in a dim room, so keep room lighting constant and documented.

**Check the refresh rate during the session.** `FrameRateController` requests 90 Hz and logs the actual rate once per second. Watch it live with the headset connected:

`adb logcat -s Unity | grep FrameRateController`

It should report a display rate of 90 Hz and a measured FPS near 90.0 throughout.

**Log frame performance with OVR Metrics Tool.** Meta's free OVR Metrics Tool [12] (install from the Meta Store) shows frame rate, stale (late) frames, screen tears and CPU/GPU throttling as an overlay in the headset. Its Report Mode saves a CSV for a whole session. Run it for the reference session of each stimulus version and keep the report: it should show 90 fps and no stale frames during trials.

**Measure true timing with a photodiode (once per stimulus version).** Frame counts and logs show what the app intended, not when light actually left the lens. The standard check is a photodiode held against the lens, recorded with an oscilloscope or a microcontroller (e.g. an Arduino). Use a test build that flashes a white patch where the photodiode sits, synchronized with a trial event (e.g. translation onset). Measure:

- **Duration:** the light trace is modulated at the refresh rate, so count frame cycles: a 7-frame event should span 7 cycles (78 ms at 90 Hz).
- **Latency:** delay from the logged event to the light, and its trial-to-trial jitter.
- **Dropped frames:** any missing or doubled cycle.

Published VR timing studies found stimulus durations accurate but software timestamps unreliable, and visual latencies of around 18 ms or more on earlier headsets [8–10]. We found no published photodiode timing study of the Quest 3, so latency must be measured rather than assumed. **(to build)** the photodiode test build.

**Look at the stimulus directly.** A headset screenshot or recording (Quest menu, or `adb shell screencap`) shows the dot layout and colors. It shows the rendered image before the lenses, so use it for geometry and counts, not for sharpness or brightness.

**(to build)** A script that takes a session's TSV and sidecar and runs all of the above: checks the spec against intended values, flags frame timing errors, and compares one reconstructed trial with the spec.

## 3. Delivery: what reaches the eye

### Blur and pixelation: causes and fixes

| Cause | What to do |
|---|---|
| **Old dot rendering** (before 2026-09-16): 0.08° dots are about 2 pixels wide, with blurry edges and flicker | Use builds from `e061fcf` or later: 0.12° dots, fixed-AA additive shader. The first build the Turkey lab saw had the old rendering |
| **Headset fit**: the lens sweet spot is small | Adjust the head strap until the display is sharpest; set the **IPD wheel** to the observer's IPD [4]; set **eye relief** with the buttons beside the lenses the same way for every session [5] |
| **Dirty or fogged lenses** | Clean with a dry microfiber cloth before each session; let a cold headset warm up |
| **Glasses** | Use the glasses spacer or prescription lens inserts, the same for every session |
| **Render resolution**: at render scale 1.0 the Quest 3 renders below panel resolution and upsamples [2] | Keep `m_RenderScale: 1.23` in `Assets/Settings/Mobile_RPAsset.asset` (both sites). The sidecar's `display` block records what was used; confirm 90 Hz holds in OVR Metrics Tool |
| **Anti-aliasing and foveation** | Keep MSAA 4× (`Mobile_RPAsset`) and foveated rendering and SpaceWarp off (`OculusSettings`). Both are in git; don't change them |
| **Dropped frames** | Check logcat as above; keep the headset charged and cool |

### Luminance and color

**Isoluminance** is set for each observer by flicker photometry and logged in the sidecar. It makes red and green equally bright for that observer but says nothing about absolute luminance, so measure that too (once per stimulus version, at each site).

**How to measure.**

- **Instrument:** a spectroradiometer (best: gives luminance, chromaticity and spectrum) or a spot photometer / colorimeter.
- **Placement:** where the eye would be, behind the lens, looking straight through its center, with a **pupil-sized aperture** (about 3–4 mm) in front of the instrument. In a study of Quest 2, HTC Vive and Pico Neo 3, a handheld luminance meter overestimated luminance at every level compared with a spectroradiometer, and luminance fell substantially 30° from center [11]. One Unity calibration study validated spot-photometer readings with a photodiode mounted behind pinhole "pupils" in a mannequin head [6]. We found no published photometric characterization of the Quest 3, so these measurements are ours to make.
- **Conditions:** headset brightness slider at the agreed level (record it), headset warmed up for 15 minutes, room dark.

**What to measure** (use a calibration scene with large uniform patches, **(to build)**):

| Property | Test | Why it matters for VRDots |
|---|---|---|
| Luminance of red dot, green dot, background | Patches rendered with the exact dot colors | Report cd/m² in the methods; compare sites |
| Linearity | Gray patches at 8–10 RGB levels | Unity's color handling and the display's gamma decide how RGB maps to light |
| Additivity | Red, green, and red + green overlapping | Our dots use additive blending; overlaps must equal the sum |
| Chromaticity | CIE xy of red and green | Checks the colors match across sites |
| Uniformity | Patch at center and at 3.5° eccentricity | Luminance falls off away from the lens center in HMDs; our aperture is 3.5° radius |
| Stability | Same patch at start and end of 30 minutes | Warm-up and thermal drift |

**Unity settings that change luminance.** Tonemapping, color grading, bloom and auto-exposure all alter output light. Published calibration work found default engine post-processing makes luminance non-linear and non-additive [6, 7]. In VRDots, post-processing is **off on the scene's cameras** (`m_RenderPostProcessing: 0`) and the project uses linear color space; keep both, even though the default URP volume profile contains tonemapping.

**Headset software:** record the Quest OS version at each site (`adb shell getprop ro.build.version.incremental`). Turn off automatic updates during a study if possible.

### Visual angle

Each dot's visual angle is set in the code from the viewing geometry, so it doesn't depend on the headset. What varies is where the observer's eye sits relative to the lens, and lens distortion away from the center. Check it two ways:

- **Through-the-lens photograph:** put a camera with a known field of view at the eye position and photograph a rendered 1° grid and rings at 1.1° and 3.5° radius. Measure the ring radii in the photo in degrees.
- **Observer check:** observers confirm the rings look sharp and circular and the grid looks evenly spaced.

**(to build)** A calibration scene: rings at 1.1° and 3.5° radius, a 1° grid, a photodiode flash patch, and red, green, gray and background luminance patches.

## 4. Protocol for both sites

**Once per stimulus version**

1. Gene tags the commit (e.g. `stim-v1.0`) and announces it.
2. Each site checks out the tag, confirms a clean `git status`, and builds.
3. Each site runs a short reference session, then sends Gene the TSV, sidecar and a headset screenshot.
4. Each site runs the physical measurements with the calibration scene: luminance and chromaticity table, photodiode timing, through-the-lens photo of the grid, and an OVR Metrics Tool report.
5. Gene compares the sidecars and measurements and runs the timing and reconstruction checks; the version is approved only when both sites match.
6. **Behavioral check:** the standard no-swap session should give a cueing effect of about +30 pp at both sites. A much smaller effect points to a delivery problem (blur, fit, luminance).

**Every session**

- [ ] `git pull`, still on the approved tag, `git status` clean
- [ ] Correct spec in the Spec slot; scene saved; build
- [ ] Sidecar `display` block: render scale 1.23, 90 Hz, expected eye texture (about 2064 × 2208)
- [ ] Lenses clean, headset fitted, IPD wheel and eye relief set and recorded, brightness at the agreed level
- [ ] Observer's flicker calibration present
- [ ] logcat shows 90 Hz
- [ ] After the session: sidecar spec matches the intended spec; timing check passes

## References

1. UploadVR. Quest 3 specs, compared to Quest 2 and Apple Vision Pro. https://www.uploadvr.com/quest-3-specs/
2. Meta. Render scale (Meta Horizon OS developer documentation, Unity). https://developers.meta.com/horizon/documentation/unity/os-render-scale/
3. Meta. Dynamic resolution (Unity). https://developers.meta.com/horizon/documentation/unity/dynamic-resolution-unity/
4. Meta Quest Help. Learn about IPD and lens spacing on Meta Quest. https://www.meta.com/help/quest/261777072346131/
5. Meta Quest Help. Adjust Meta Quest headset fit and feel. https://www.meta.com/help/quest/427255709332571/
6. Murray, R. F., Patel, K. Y., & Wiedenmann, E. S. (2022). Luminance calibration of virtual reality displays in Unity. *Journal of Vision*, 22(13), 1. https://doi.org/10.1167/jov.22.13.1
7. Zaman, N., Sarker, P., & Tavakkoli, A. (2023). Calibration of head mounted displays for vision research with virtual reality. *Journal of Vision*, 23(6), 7. https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10278547/
8. Accuracy and precision of visual and auditory stimulus presentation in virtual reality in Python 2 and 3 environments for human behavior research. *Behavior Research Methods*. https://www.ncbi.nlm.nih.gov/pmc/articles/PMC9046309/
9. Wiesing, M., Fink, G. R., & Weidner, R. (2020). Accuracy and precision of stimulus timing and reaction times with Unreal Engine and SteamVR. *PLOS One*. https://www.ncbi.nlm.nih.gov/pmc/articles/PMC7141612/
10. Temporal precision and accuracy of audio-visual stimuli in mixed reality systems. *PLOS One*. https://journals.plos.org/plosone/article?id=10.1371%2Fjournal.pone.0295817
11. Luminance and thresholding limitations of virtual reality headsets for visual field testing. *PLOS One*. https://journals.plos.org/plosone/article?id=10.1371%2Fjournal.pone.0332795
12. Meta. Monitor performance with OVR Metrics Tool (Unity). https://developers.meta.com/horizon/documentation/unity/ts-ovrmetricstool/

Further reading: Murray, R. F. A model of the Unity High Definition Render Pipeline, with applications to flat-panel and head-mounted display characterization, *Journal of Vision* (https://pmc.ncbi.nlm.nih.gov/articles/PMC13112491/); Colour calibration of a head mounted display for colour vision research using virtual reality, *SN Computer Science* (https://www.ncbi.nlm.nih.gov/pmc/articles/PMC8551135/).
