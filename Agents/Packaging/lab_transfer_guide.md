# VRDots Lab Transfer Guide
*Prepared 2026-04-09 · Single observer pilot stage · Unity 6000.2.7f2*

This document covers what needs to happen on both ends to get a new lab running the VRDots paradigm. It assumes the receiving lab has a Meta Quest headset and a Windows or Mac computer capable of building to Android, but no prior familiarity with the codebase.

---

## Part 1 — What you (GS) need to do before handing off

### 1.1 Repo access

The project lives at `https://github.com/GeneStoner/UnityQuestDotStimuli.git` on branch `wip/quest-pilot`.

- **If sharing privately**: add the collaborator's GitHub username in Settings → Collaborators. They clone with `git clone -b wip/quest-pilot https://github.com/GeneStoner/UnityQuestDotStimuli.git`
- **If sharing publicly**: make the repo public (currently assumed private). Consider stripping any personal notes from commit history first.
- **Commit everything clean before sharing** — a collaborator who clones a repo with diverged state is likely to spend an hour debugging phantom warnings.

### 1.2 Ensure the build can be reproduced from scratch

The receiving lab will need to build the APK themselves (see Part 2). Before handing off:

1. Delete your local `Library/` folder and confirm the project re-imports cleanly in Unity 6000.2.7f2. This catches any asset that depends on local-only state.
2. Do a fresh Android build (`File → Build Settings → Android → Build`) and confirm the APK installs and runs on your Quest. This is the smoke test.
3. Note the exact build target in `Build Settings`:
   - Platform: Android
   - Texture Compression: ASTC
   - Target API level: confirm it matches Quest's Android version (typically API 29 or higher)
   - Company Name / App Name in `Project Settings → Player` — warn the collaborator if they change this, the app ID changes and old data will not be visible to the new build.

### 1.3 Document the Inspector dependencies

Several components require manual wiring in the Unity Inspector that is not captured in version control in a portable way:

- **`DirectionalFeedbackSpot`**: needs a `responseController` reference set in the Inspector on the relevant GameObject.
- **`SmoothFixation`** (under Main Camera): `showNoniusLines` toggle; confirm this is set to the desired default.
- **`NoniusLine.shader`**: must be in `Project Settings → Graphics → Always Included Shaders`. Confirm this survives a fresh import. If not, add it manually after import and document the step explicitly.
- **Active Input Handling** (`Project Settings → Player → Other Settings`): must be set to **"Both"** (not "New Input System" only). This is a known footgun — the project uses both legacy `Input` and the new Input System; setting "New Input System" only causes silent input failures.

Create a one-page "Inspector checklist" or add these to a `SETUP.md` in the repo root before sharing.

### 1.4 Experiment configuration

All experiment parameters are stored as ScriptableObject assets in `Assets/ExperimentSpecs/`. The active experiment is selected at runtime by dragging the desired asset into the Inspector. Currently available assets:

| Asset | Purpose |
|-------|---------|
| `Exp_DecoupledDots_005m` | Main swap pilot (N/C/Z/CZ, 0.05m depth, no inv) |
| `Exp_DecoupledDots_Inv_005m` | Inverted version of above (label inversion) |
| `Exp_DepthColorLinked` | 50% swap, linked depth+color |
| `Exp_DepthSwapCtrl` | All-red, ZdA/ZdB only, 0.05m |
| `Exp_DepthParam_003m/005m/010m/015m` | Parametric depth sweep |
| `Exp_DepthCheck_005m` | Brief observer screening — verifies 0.05m depth perception before main experiment |
| `Exp_Baseline` | No depth, no swap — 2D baseline |

Collaborators can run any of these without touching code. If they want to design new conditions, they create a new ScriptableObject asset from the `ExperimentSpec` type (right-click in Project window → Create → Experiment Spec). Walk them through the key parameters:
- `depthOffset_m`: depth separation in meters (Near = −offset along forward, Far = +offset)
- `swapFlags`: bitmask (None=0, Color=2, Depth=8, Depth50A=32, Depth50B=64, etc.)
- `linkDepthColor`: whether color assignment tracks depth plane
- `balanceDelayedFieldColor`, `translationDuration_ms`, `nTrialsPerCondition`, etc.

**Gotcha**: Unity's Library cache can hold stale ScriptableObject values after Reimport. If parameter changes don't seem to take effect, code-level overrides are more reliable than asset-only changes. Warn collaborators to test this.

### 1.5 Data output and analysis pipeline

- Data writes to `/sdcard/Android/data/com.genestoner.vrdptsrebuildX.test/files/` on the Quest.
- Pull with ADB: `adb pull /sdcard/Android/data/com.genestoner.vrdptsrebuildX.test/files/ /tmp/quest_pull/`
- Each session produces a TSV file. Key columns: `SessionID`, `TrialNum`, `DelayedFieldDepth`, `DelayedFieldColor`, `SwapType`, `TransDeg`, `Response`, `Correct`, `RT_ms`, plus condition-specific columns.
- Analysis scripts live in `Tools/Analysis/` (~40 Python scripts). The canonical set for the swap pilot is in `Agents/SwapPilot/Analysis/`.
- The main entry point for a new collaborator is probably `analyze_vr_dots_v2.py` (general-purpose) or the experiment-specific scripts in `Agents/SwapPilot/Analysis/`.
- **Data path is hardcoded** in most scripts (`/tmp/quest_pull/files/`). Collaborators will need to update this or symlink. Consider parameterizing the data path before sharing.

### 1.6 Nice-to-have before sharing

- [ ] Write a top-level `SETUP.md` in the repo root (Inspector checklist, ADB pull command, data path note)
- [ ] Tag the current working commit as `v0.2.0-pilot` for reference
- [ ] Verify `Library/` is in `.gitignore` (it should be — never committed — but confirm)
- [ ] Strip any hardcoded personal paths from analysis scripts, or document them clearly
- [ ] Decide whether to share the analysis scripts separately (cleaner) or point collaborators to the repo

---

## Part 2 — What the receiving lab needs

### 2.1 Hardware

- **Meta Quest headset**: Quest 2, Quest 3, or Quest Pro. Quest 3 preferred (better display, higher resolution, inside-out tracking). Quest 2 is fine for pilot work.
  - The paradigm uses stereoscopic depth at ~2.5 arcmin disparity at 2m (0.05m separation). Quest 2 and 3 both support this comfortably; Quest 1 is end-of-life and untested.
  - **Quest Pro** has eye-tracking and a substantially higher-quality display but may have different interpupillary distance handling. Test vergence carefully.
- **USB-C cable** with data transfer capability (not charge-only) for ADB. Most USB-C cables work; a cable known to pass data is important.
- A Windows or Mac computer for Unity development and ADB access.

### 2.2 Meta developer setup

Before any build can be sideloaded:

1. Create a **Meta developer account** at `developer.oculus.com` (free, requires Meta account).
2. Create an **Organization** in the developer portal (required even for personal use).
3. On the Quest headset: `Settings → System → Developer Options → USB Connection Dialog → MTP or PTP` and toggle **Developer Mode on**. (This requires the Meta Horizon phone app linked to the same developer account.)
   - If ADB shows "unauthorized": toggle Developer Mode off, then on again in the Meta Horizon app — this re-initializes the ADB authorization.
4. On the computer: install **Android Debug Bridge (ADB)**. Easiest via Android Studio (includes ADB automatically) or via the standalone platform-tools package from developer.android.com.
5. Verify with `adb devices` — the Quest should appear as a device (authorize on headset when prompted).

### 2.3 Unity setup

1. Install **Unity Hub** from `unity.com/unity-hub`.
2. Install **Unity 6000.2.7f2** (exact version required — Unity projects are not forward/backward compatible). In Unity Hub: Installs → Install Editor → "Archive" tab → find 6000.2.7f2. 
   - During installation, add the **Android Build Support** module (includes NDK and JDK). This is not installed by default.
3. Open the project: Unity Hub → Add → point to the cloned repo folder. Unity will import assets on first open (5–20 minutes).
4. Confirm packages resolve automatically via the Package Manager. All dependencies are declared in `Packages/manifest.json` and will be fetched from the Unity registry. No manual package installation needed.
5. Key packages that should appear in the Package Manager after import:
   - `com.unity.xr.oculus` 4.5.2 (Meta/Oculus XR Plugin)
   - `com.unity.xr.interaction.toolkit` 3.2.1
   - `com.unity.inputsystem` 1.14.2
   - URP 17.2.0

### 2.4 Build and deploy

1. `File → Build Settings → Android → Switch Platform` (first time only — takes a few minutes).
2. Connect Quest via USB-C. Confirm `adb devices` shows the device.
3. In Build Settings: `Build and Run` — Unity builds the APK and installs it on the connected Quest.
4. On first launch: put on the headset and confirm the app appears in the Unknown Sources section of the App Library.

### 2.5 Running an experiment

1. Select the desired experiment asset (ScriptableObject) by dragging it into the relevant Inspector slot on the Experiment Manager GameObject in the scene.
2. Put on the headset. The app opens to a waiting state.
3. Trigger = right-hand controller trigger to advance; thumbstick to respond. Thumbstick deadzone must be set appropriately — if too high, responses cancel silently (check `thumbstickDeadzone` in the Inspector).
4. Data saves automatically to the Quest's internal storage at the end of each session.
5. Pull data with ADB: `adb pull /sdcard/Android/data/com.genestoner.vrdptsrebuildX.test/files/ <local_destination>`

### 2.6 Analysis

- Python 3.9+, with: `numpy`, `scipy`, `pandas`, `matplotlib`, `statsmodels` (for GLM scripts).
- Install with: `pip install numpy scipy pandas matplotlib statsmodels`
- Clone or copy the `Tools/Analysis/` scripts. Update hardcoded data paths in each script to point to where you pulled the data.
- Entry point: `decoupled_dots_combined_analysis.py` for the main swap pilot, or `analyze_vr_dots_v2.py` for general session analysis.

### 2.7 Stereo vision check

This paradigm relies on stereoscopic depth perception. Before collecting pilot data:

1. Confirm the observer can perceive the binocular nonius lines (toggle `showNoniusLines` on the `SmoothFixation` component). The nonius lines should appear aligned when fixation is correct and vergence is on target.
2. Run `Exp_DepthCheck_005m` — a brief check session that verifies the observer can perceive the 0.05m depth difference. If performance is at chance on depth discrimination, the depth separation may need to increase for that observer, or there is a display/IPD issue.
3. IPD setting on the Quest must be adjusted to the observer. Quest 2 has a physical IPD adjustment (three positions). Quest 3 has continuous motorized IPD. Incorrect IPD causes vergence mismatch that can make depth cues unreliable or cause discomfort.

---

## Open items before first transfer

- [ ] Decide: source project (requires Unity) vs. pre-built APK (easier to deploy, no build step, but analysis still needs ADB + Python)
- [ ] Hardcoded app package name (`com.genestoner.vrdptsrebuildX.test`) — collaborator should leave this unchanged so data paths and analysis scripts work out of the box, or both sides need to coordinate a rename
- [ ] Decide whether to share a stable `main` branch snapshot vs. the active `wip/quest-pilot` branch
- [ ] Data path parameterization in analysis scripts (currently hardcoded to `/tmp/quest_pull/`)
