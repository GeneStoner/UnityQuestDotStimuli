# VRDots Stimulus Verification
*Making sure both labs show the stimulus we intend.*

A stimulus can go wrong at three levels, and each needs its own check:

1. **Definition**: the code, spec asset and project settings that were built.
2. **Rendering**: what the app actually drew, frame by frame.
3. **Delivery**: what reached the observer's eye through the display, lenses and headset fit.

Two labs are showing the same stimulus only when all three levels match. Items marked **(to build)** don't exist yet.

## 1. Definition: build the same thing at both sites

| What must match | How to make it match | How to check it |
|---|---|---|
| Code | Both labs build from the same **tagged commit** (e.g. `stim-v1.0`), never from uncommitted changes | `git describe --tags` and `git status` (must be clean) before building |
| Unity | Exactly **6000.2.7f2** | Unity Hub → Installs |
| Project settings | Keep them in git and never edit them locally: `ProjectSettings/`, `Assets/XR/Settings/OculusSettings.asset`, `Assets/Settings/Mobile_RPAsset.asset` | `git status` shows no changes there |
| Experiment | The same spec asset in the Spec slot | The sidecar's `experiment_spec` block, compared between sites |
| Scene toggles | Use Screen Space Shader and Use Fixed AA Shader both ticked | The sidecar's `stimulus_builder` block |
| Colors | Red/green isoluminance measured for each observer | The sidecar's `calibration_colors` block |

**Checking that two sites match:** compare the sidecar files from one session at each site. Apart from the timestamp, the `experiment_spec`, `stimulus_builder` and `build_date` blocks should be identical. Trials with the same seeds (`SeedA0`–`SeedB3`) produce the same dot trajectories, and `MkHash32` fingerprints each trial's trajectory, so matching hashes mean matching motion.

**(to build)** Log more in the sidecar: git commit hash, Unity version, headset OS build, measured refresh rate, eye-buffer resolution scale, MSAA and foveation level. Today only `build_date` identifies the build.

## 2. Rendering: confirm the app drew the specified stimulus

**Reconstruct the dots from the logged seeds.** The dot positions come from Unity's random number generator. `Agents/SwapPilot/Analysis/dotnet_random.py` reproduces that generator exactly (checked with `verify_rng/`). `reconstruct_animation.py` then rebuilds any trial frame by frame. From the reconstruction, measure:

- dots per field and per subfield
- aperture radius and the dot-free zone around fixation
- rotation and translation speeds (deg/s), translation direction
- onset delay and translation duration (in frames)
- which dots swap color or motion, and when

Each measured value should equal the spec. This checks the stimulus logic, not the display.

**Check the timing on every trial.** The TSV logs `TransStartFrame`, `TransEndFrame`, `PresentedDurFrames` and `PresentedDurMs`. At 90 Hz, one frame is 11.1 ms. An 80 ms translation should last 7 frames (78 ms, the nearest whole frame count; confirm against the spec). Any trial where measured ms ≠ frames × 11.1 had a dropped or late frame.

**Check the refresh rate during the session.** `FrameRateController` requests 90 Hz and logs the actual rate once per second. Watch it live with the headset connected:

`adb logcat -s Unity | grep FrameRateController`

It should report a display rate of 90 Hz and a measured FPS near 90.0 throughout.

**Look at the stimulus directly.** A headset screenshot or recording (Quest menu, or `adb shell screencap`) shows the dot layout and colors. It shows the rendered image before the lenses, so use it for geometry and counts, not for sharpness or brightness.

**(to build)** A script that takes a session's TSV and sidecar and runs all of the above: checks the spec against intended values, flags frame timing errors, and compares one reconstructed trial with the spec.

## 3. Delivery: what reaches the eye

## Blur and pixelation: causes and fixes

| Cause | What to do |
|---|---|
| **Old dot rendering** (before 2026-09-16): 0.08° dots are about 2 pixels wide, with blurry edges and flicker | Use builds from `e061fcf` or later: 0.12° dots, fixed-AA additive shader. The first build the Turkey lab saw had the old rendering |
| **Headset fit**: the lens sweet spot is small | Adjust the head strap until the display is sharpest; set the **IPD wheel** to the observer's IPD; set the eye-relief (lens distance) setting the same way for every session |
| **Dirty or fogged lenses** | Clean with a dry microfiber cloth before each session; let a cold headset warm up |
| **Glasses** | Use the glasses spacer or prescription lens inserts, the same for every session |
| **Render resolution**: Unity's default eye-buffer scale (1.0) renders below the panel's native resolution | Test a higher `XRSettings.eyeTextureResolutionScale` while keeping 90 Hz, then fix the value and log it **(to build)** |
| **Anti-aliasing and foveation** | Keep MSAA 4× (`Mobile_RPAsset`) and foveated rendering and SpaceWarp off (`OculusSettings`). Both are in git; don't change them |
| **Dropped frames** | Check logcat as above; keep the headset charged and cool |

## Luminance and color

- **Isoluminance:** run flicker photometry for every observer and log the result (it goes in the sidecar).
- **Absolute luminance:** measure the red and green dots and the background through the lens with a photometer, at full brightness, and keep the Quest brightness slider the same at both sites. Record the headset's display settings.
- **Headset software:** record the Quest OS version at each site (`adb shell getprop ro.build.version.incremental`). Turn off automatic updates during a study if possible.

## Visual angle

Each dot's visual angle is set in the code from the viewing geometry, so it doesn't depend on the headset. What varies is where the observer's eye sits relative to the lens.

**(to build)** A calibration scene: rings at 1.1° and 3.5° radius, a 1° grid, and red, green and background luminance patches. Observers confirm the rings look sharp and circular, and the photometer is pointed at the patches.

## 4. Protocol for both sites

**Once per stimulus version**

1. Gene tags the commit (e.g. `stim-v1.0`) and announces it.
2. Each site checks out the tag, confirms a clean `git status`, and builds.
3. Each site runs a short reference session, then sends Gene the TSV, sidecar and a headset screenshot.
4. Gene compares the sidecars and runs the timing and reconstruction checks; the version is approved only when both sites match.
5. **Behavioral check:** the standard no-swap session should give a cueing effect of about +30 pp at both sites. A much smaller effect points to a delivery problem (blur, fit, luminance).

**Every session**

- [ ] `git pull`, still on the approved tag, `git status` clean
- [ ] Correct spec in the Spec slot; scene saved; build
- [ ] Lenses clean, headset fitted, IPD set, brightness at the agreed level
- [ ] Observer's flicker calibration present
- [ ] logcat shows 90 Hz
- [ ] After the session: sidecar spec matches the intended spec; timing check passes
