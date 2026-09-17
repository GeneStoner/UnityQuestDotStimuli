# VRDots — Collaborator Setup Guide
*Gene Stoner · September 2026*

This document covers everything needed to get the VRDots experiment running in a new lab. It is divided into two parts: what Gene does before the handoff, and what the collaborating lab needs to do on their end.

---

## Part 1 — What Gene does before sharing

### 1.1 Give repo access

The project is hosted at:

```
https://github.com/GeneStoner/UnityQuestDotStimuli
```

Branch: `wip/quest-pilot`

Add the collaborator's GitHub username via **Settings → Collaborators → Add people**. They will receive an email invitation to accept.

### 1.2 Confirm the build is clean

Before the collaborator clones and tries to build, run through this checklist:

- [ ] All relevant changes committed and pushed to `wip/quest-pilot`
- [ ] Delete the local `Library/` folder and confirm the project re-imports cleanly in Unity 6000.2.7f2 (catches any asset that depends on local-only state)
- [ ] Do a fresh `Build and Run` to Quest and confirm the app launches and runs correctly
- [ ] Confirm `Library/` is in `.gitignore` (it is — but worth verifying it was never accidentally committed)

### 1.3 Send the collaborator this document

Share this file plus the list of experiment assets in section 2.6 below, indicating which ones are relevant for their session.

---

## Part 2 — What the collaborating lab needs to do

### 2.1 Hardware checklist

You will need:

- **Meta Quest 3** headset ✓ (you have this)
- **USB-C cable** that supports data transfer (not charge-only). Most USB-C cables work; if `adb devices` shows nothing, try a different cable.
- **Windows or Mac computer** for building the Unity app and pulling data

### 2.2 Meta developer account setup

This is required once per lab. It allows sideloading apps onto the Quest.

1. Create a **Meta developer account** at `developer.oculus.com` (free; requires a Meta/Facebook account).
2. Create an **Organization** in the developer portal — this is required even for personal/research use. Any name works.
3. On the Quest headset: `Settings → System → Developer Options` → toggle **Developer Mode on**.
   - This step requires the **Meta Horizon** phone app linked to the same developer account.
4. On the computer: install **Android Debug Bridge (ADB)**.
   - Easiest option: download the standalone **platform-tools** package from `developer.android.com/tools/releases/platform-tools` and add it to your PATH.
   - Alternative: install Android Studio — ADB is included automatically.
5. Connect the Quest to the computer via USB-C. Run `adb devices`. The headset should appear; **authorize it on the headset** when prompted (a dialog will appear inside the headset asking to allow USB debugging).
   - If it shows "unauthorized": toggle Developer Mode off then back on in the Meta Horizon app to reset the ADB authorization.

### 2.3 Unity setup

**Important: the exact Unity version is required. Unity projects are not forward/backward compatible.**

1. Install **Unity Hub** from `unity.com/unity-hub`.
2. Open Unity Hub → Installs → **Install Editor** → click the **Archive** tab → search for `6000.2.7f2` and install it.
   - During installation, tick **Android Build Support** (this also installs NDK and JDK — required for Quest builds). It is not installed by default.
3. Once installed, open Unity Hub → **Add** → navigate to the cloned project folder and open it.
   - Unity will import assets on first open. This takes 5–20 minutes. Let it finish before doing anything.
4. All package dependencies are declared in `Packages/manifest.json` and download automatically from the Unity registry. No manual package installation is needed.

**One critical setting to verify after first open:**
`Edit → Project Settings → Player → Other Settings → Active Input Handling` must be set to **"Both"**.
If it is set to "New Input System" only, controller input will fail silently.

### 2.4 Clone the project

Once Gene has added you as a collaborator on GitHub:

```
git clone -b wip/quest-pilot https://github.com/GeneStoner/UnityQuestDotStimuli.git
```

Then open the cloned folder in Unity Hub as described in 2.3 above.

### 2.5 Build and deploy to the Quest

1. In Unity: `File → Build Settings → Android → Switch Platform` (first time only; takes a few minutes).
2. Connect the Quest via USB-C. Confirm the headset is visible: `adb devices` should list it.
3. In Build Settings: click **Build and Run**. Unity will compile and install the app directly on the Quest.
4. Put on the headset. The app appears under **Unknown Sources** in the App Library. Launch it.

The app package name is `com.genestoner.vrdptsrebuildX.test`. **Do not change the Company Name or App Name in Project Settings** — doing so changes the package name and the data files will no longer be accessible to the new build.

### 2.6 Selecting an experiment

All experiment parameters are stored as configuration assets in `Assets/ExperimentSpecs/`. No code changes are needed to switch between experiments — you select the experiment by dragging the desired asset into the Inspector.

**How to select an experiment:**
1. In the Unity Editor, open the scene `UpToDateScene` (in `Assets/Scenes/`).
2. In the Hierarchy, find the **TrialBlockRunner** GameObject.
3. In the Inspector, drag the desired experiment asset from the `Assets/ExperimentSpecs/` folder into the **Spec** slot.
4. Build and Run again.

**Available experiments (relevant subset):**

| Asset name | What it runs |
|------------|-------------|
| `Exp_Baseline` | No depth, no swap — 2D pilot (64 trials) |
| `Exp_StonerBlanc_Replication` | Replication of Stoner & Blanc (2010) |
| `Exp_SubfieldSwap_CatekExact` | Replication of Catak et al. (2022) |
| `Exp_DepthCheck_005m` | Quick stereo screening — verify observer can perceive 0.05m depth |
| `Exp_DepthSwapCtrl` | Core stereo swap experiment (ZdA/ZdB, both-red, 0.05m) |
| `Exp_DecoupledDots_005m` | Color vs depth decoupled factorial (N/C/Z/CZ, 0.05m) |
| `Exp_DepthColorLinked` | Depth + color linked, 50% swap (ZdA/ZdB) |
| `Exp_DepthParam_003m` | Parametric depth: 0.03m separation |
| `Exp_DepthParam_005m` | Parametric depth: 0.05m separation |
| `Exp_DepthParam_010m` | Parametric depth: 0.10m separation |
| `Exp_DepthParam_015m` | Parametric depth: 0.15m separation |

Gene will indicate which asset(s) to run for each session.

### 2.7 IPD calibration (important for stereo experiments)

The Quest 3 has continuous motorized IPD adjustment. Before running any stereo experiment, set the IPD to match the observer:

- Go to `Settings → Physical Setup → Eye Distance (IPD)` on the Quest and adjust the slider until the image appears sharp and comfortable.
- Incorrect IPD causes vergence mismatch, which can make depth cues unreliable and cause eye strain.

### 2.8 Running a session

1. Select the experiment asset (2.6 above), build and run.
2. The app opens to a waiting state. The observer puts on the headset.
3. **Controls:**
   - Right-hand controller **trigger**: advance through screens / confirm selection
   - Right-hand controller **thumbstick**: report the perceived translation direction (push in the direction of motion)
4. A fixation dot is shown at the center of the display throughout the trial. The observer should maintain fixation on it.
5. Data saves automatically to the Quest's internal storage at the end of each block.
6. Sessions typically take 10–20 minutes depending on the experiment.

**Before each stereo session**, run `Exp_DepthCheck_005m` to verify the observer can perceive the depth separation. If performance is at chance on this check, adjust IPD and retry before proceeding to the main experiment.

### 2.9 Pulling data from the Quest

After each session, copy the data files to the computer:

```
adb pull /sdcard/Android/data/com.genestoner.vrdptsrebuildX.test/files/ /path/to/local/folder/
```

Replace `/path/to/local/folder/` with wherever you want the data on your machine (e.g. `C:\VRDots\Data\` on Windows or `~/VRDotsData/` on Mac).

Each session produces:
- A `.tsv` file — one row per trial, all behavioral data
- A `.tsv.meta.json` — session metadata
- A `.tsv.sidecar.json` — full stimulus configuration and trajectory library

Send all three files to Gene after each session.

### 2.10 Analysis (optional — Gene will handle centrally)

If you want to run local quality checks:

1. Install Python 3.9+ and the required packages:
   ```
   pip install numpy scipy pandas matplotlib statsmodels
   ```
2. The analysis scripts are in `Tools/Analysis/` and `Agents/SwapPilot/Analysis/` in the project folder.
3. Entry point for a quick per-session summary:
   ```
   python3 analyze_vr_dots_v2.py path/to/session.tsv
   ```
   This produces a summary text file, a performance plot, and a trajectory plot.
4. **Note**: most scripts have the data path hardcoded to `/tmp/quest_pull/files/`. Update this to wherever you pulled the data.

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `adb devices` shows nothing | Check cable (must support data, not charge-only); re-authorize in headset |
| `adb devices` shows "unauthorized" | Toggle Developer Mode off then on in the Meta Horizon app |
| App not found on Quest after build | Check Unknown Sources in App Library; ensure same Meta account used |
| Controller input not working | Verify Active Input Handling = "Both" in Project Settings → Player |
| Parameters don't match the selected asset | Reimport the asset (right-click in Project → Reimport); Library cache can hold stale values |
| Depth not perceptible | Adjust IPD on the headset; run `Exp_DepthCheck_005m` |

---

## Contact

Gene Stoner — generstoner@gmail.com / 858-342-7733

Repository: `https://github.com/GeneStoner/UnityQuestDotStimuli` (branch: `wip/quest-pilot`)
