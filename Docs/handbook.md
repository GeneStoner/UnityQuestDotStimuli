# VRDots Handbook
*Setup, running experiments, data, and learning the project with Claude Code.*

VRDots is a Unity app for the Meta Quest 3 that runs Stoner & Blanc–style cueing experiments. Two overlapping red and green dot fields rotate; one field briefly translates, and the observer reports its direction (8 choices, chance 12.5%). The worked example throughout is the no-swap **density series**.

Related docs: [stimulus_verification.md](stimulus_verification.md) (checking the stimulus is what we intend), [subject_experimenter_instructions.md](subject_experimenter_instructions.md) (what to tell observers), [experiment_catalog.md](experiment_catalog.md) (every experiment and its results).

## 1. One-time setup

**Hardware:** a Meta Quest 3, a USB-C cable that carries data (not charge-only), and a Windows or Mac computer.

1. **Get the code.** The repository is public; clone the working branch:
   `git clone -b wip/quest-pilot https://github.com/GeneStoner/UnityQuestDotStimuli.git`
   Cloning (rather than downloading a ZIP) lets you `git pull` updates. To push changes, Gene must add your GitHub account as a collaborator.
2. **Unity.** Install Unity Hub, then Unity **6000.2.7f2** exactly (Installs → Install Editor → Archive tab), with the **Android Build Support** module ticked.
3. **Open the project** in Unity Hub (Add → the cloned folder). The first import takes 5–20 minutes. Packages install automatically from `Packages/manifest.json` (Oculus XR 4.5.2, XR Interaction Toolkit 3.2.1, Input System 1.14.2, URP 17.2.0).
4. **Check one setting:** Edit → Project Settings → Player → Other Settings → Active Input Handling = **Both**. Otherwise the controllers fail silently.
5. **Quest developer mode.** Create a free Meta developer account and organization at developer.oculus.com, then turn on Developer Mode for the headset in the Meta Horizon phone app.
6. **ADB.** Install Android platform-tools (developer.android.com/tools/releases/platform-tools). Connect the Quest, run `adb devices`, and accept "Allow USB debugging" inside the headset.
7. **Switch platform.** File → Build Settings → Android → Switch Platform.
8. **Python (for analysis):** Python 3.9+ and `pip install numpy scipy pandas matplotlib statsmodels`.

Do not change Company Name or Product Name in Project Settings: that changes the app's package name (`com.genestoner.vrdptsrebuildX.test`) and where data is saved.

## 2. Running an experiment

### Each session

1. `git pull` to get the current version (see [stimulus_verification.md](stimulus_verification.md) for using a tagged version across sites).
2. **Open the scene** `Assets/Scenes/UpToDateScene`.
3. **Pick the experiment.** In the Hierarchy, select `TrialBlockManager`. In the Inspector, drag a spec from `Assets/ExperimentSpecs/` into the **Spec** slot of the TrialBlockRunner component.
4. **Check rendering.** On the `StimulusBuilder` component, **Use Screen Space Shader** and **Use Fixed AA Shader** should both be ticked.
   Rendering settings live in `Assets/Settings/Mobile_RPAsset.asset` and must not be changed: render scale **1.23** (the Quest 3 panel resolution) and MSAA **4×**. Each session's sidecar records them in its `display` block.
5. **Save** the scene (Ctrl+S / Cmd+S), then File → Build Settings → **Build and Run** with the Quest connected. The app installs and launches (also listed under Unknown Sources).
6. **Calibrate colors** once per new observer with the FlickerCalibration scene (flicker photometry, 10 settings, saved on the headset).
7. **Run.** The observer starts with the right trigger, fixates the central target, reports direction with the right thumbstick, then presses the trigger twice (lock, then submit). A session is 512 trials, about 15–20 minutes, and paces itself. Observer instructions: [subject_experimenter_instructions.md](subject_experimenter_instructions.md).
8. **Pull the data** (section 3).

### Example: the no-swap density series

Every spec below uses a 3.5° radius aperture with a 1.1° dot-free zone around fixation (34.7 deg² per field) and has no swaps. Density is per field (red or green).

| Spec | Dots per field | Density (dots/deg²) | Dot size |
|---|---|---|---|
| `Exp_DensityCompare_VeryLow` | 20 | 0.6 | 0.08° |
| `Exp_DensityCompare_VRDots` | 63 | 1.8 | 0.08° |
| `Exp_DensityCompare_HighDens` | 173 | 5.0 | 0.12° |
| `Exp_DensityCompare_Peak` | 500 | 14.4 | 0.08° |
| `Exp_DensityCompare_VeryHigh` | 750 | 21.6 | 0.08° |
| `Exp_DensityCompare_UltraHigh` | 1000 | 28.8 | 0.08° |

To run one, put that spec in the Spec slot, save, and Build and Run. The 173-dot spec uses the newer 0.12° dot size; the others have not been updated yet.

### Making a new experiment

All parameters live in the spec asset; no code changes are needed. Select an existing spec in `Assets/ExperimentSpecs/`, duplicate it (Ctrl+D / Cmd+D), rename it, and change fields in the Inspector. Also change `experimentName`, which is what the data files record. Don't edit specs that already have data; make a new one.

If a changed value doesn't seem to take effect, right-click the asset → Reimport; Unity's cache can hold old values.

### Stereo (depth) experiments

- Set the Quest 3's **IPD wheel** to the observer's IPD before every session.
- Run `Exp_DepthCheck_005m` first. If depth performance is at chance, fix IPD and fit before running the main experiment.

### Troubleshooting

| Problem | Fix |
|---|---|
| `adb devices` lists nothing | Use a data-capable cable; put the headset on and accept the debugging prompt |
| Listed as "unauthorized" | Toggle Developer Mode off and on in the Meta Horizon app |
| Controllers do nothing | Active Input Handling must be Both |
| "Waiting for controllers..." in red | Re-pair or charge the controllers |
| Wrong parameters on screen | Scene not saved before building, spec slot empty, or stale cache (Reimport) |
| Stimulus looks blurry | See [stimulus_verification.md](stimulus_verification.md), section 3 |

## 3. Data files and analysis

### The three files

Each session writes three files named by its start time on the headset clock, e.g. `vr_dots_session_260916_1340` = 2026-09-16, 13:40. Keep all three together.

| File | Contents |
|---|---|
| `.tsv` | One row per trial: condition, true and reported direction, response time, seeds |
| `.tsv.sidecar.json` | The full stimulus record: every spec parameter, colors, rendering settings, build date |
| `.tsv.meta.json` | Short summary: experiment name, target and completed trial counts (completed can be one higher when a trial was repeated) |

Pull them with the headset connected:

`adb pull /sdcard/Android/data/com.genestoner.vrdptsrebuildX.test/files/ ~/VRDotsData/`

### Key TSV columns

| Column | Meaning |
|---|---|
| `Trial` | Trial number within the session |
| `Experiment` | Spec identifier, e.g. `DensityCompare_HighDens_v2` |
| `Cond` | `CUED`: the translating field is the one that appeared later. `UNCUED`: it appeared earlier |
| `SwapType` | What swapped at translation onset: `N` = nothing, `CM` = color and motion both swap |
| `TransDeg` | True translation direction (0° right, 90° up; 8 directions, 45° apart) |
| `RespDeg` | Reported direction |
| `RTf` | Response time from translation onset |
| `DelayedFieldColor` | Color of the later field: `R` or `G` |
| `TransStartFrame`, `TransEndFrame`, `PresentedDurMs` | Frame timing, for checking dropped frames |
| `SeedA0`–`SeedB3`, `MkHash32` | Seeds and trajectory fingerprint, for exact replay and checking trial identity |

### Key sidecar fields

The `experiment_spec` block is the authoritative record of the stimulus.

| Field | Example | Meaning |
|---|---|---|
| `spec_name` | `Exp_DensityCompare_HighDens` | Spec asset loaded |
| `dots_per_field` | 173 | Dots per field (red or green) |
| `dot_size_deg` | 0.12 | Dot diameter, degrees |
| `aperture_radius_deg` | 3.5 | Aperture radius, degrees |
| `fixation_exclusion_radius_deg` | 1.1 | Dot-free zone around fixation, degrees |
| `rotation_speed_deg_per_sec` | 81 | Rotation speed |
| `translation_speed_deg_per_sec` | 2.26 | Translation speed |
| `translation_duration_ms` | 80 | Translation duration |
| `delayed_onset_ms` | 750 | Delay between the two fields' onsets |
| `include_no_swap_baseline`, `include_cm_swaps` | true / false | Which trial types were included |

Other blocks: `display` (headset model, render scale, MSAA, eye-texture size, refresh rate — from 2026-09-17), `calibration_colors` (the observer's red and green RGBA values), `stimulus_builder` (`use_fixed_aa_shader`, `dot_blend_mode`: sessions from 2026-09-16 use the fixed shader and additive blending), and `build_date` (which app version ran).

### Analysis

A trial is correct when `TransDeg == RespDeg`. The cueing effect is CUED minus UNCUED percent correct, in percentage points, for each `SwapType`.

```python
import pandas as pd

d = pd.read_csv("vr_dots_session_260916_1340.tsv", sep="\t")
d["correct"] = d["TransDeg"] == d["RespDeg"]
pc = d.groupby(["SwapType", "Cond"])["correct"].mean().unstack() * 100
pc["cueing_pp"] = pc["CUED"] - pc["UNCUED"]
print(pc.round(1))
```

For example, Gene's session 260916_1340 (173 dots, N and CM interleaved) gave +35.5 pp cueing on N trials and +23.0 pp on CM trials. A healthy no-swap session is roughly CUED 60–70%, UNCUED 30–40%.

More scripts: `Tools/Analysis/` (start with `analyze_vr_dots_v2.py`) and `Agents/SwapPilot/Analysis/`. Many have data paths written into them; change those to your own folder.

### Where data should live

Recommended: a **separate private GitHub repository for data**, not this repository (which is public and already large).

- One folder per lab and observer, e.g. `turkey/OBS01/`, holding the raw three-file sets exactly as pulled.
- Never edit raw files; write analysis outputs elsewhere.
- Commit after every session, with the spec name and observer in the message.
- Use observer codes, not names.

## 4. Learning the project with Claude Code

Run Claude Code inside the cloned repository and ask it questions. It reads the actual scripts, specs and notes, so its answers are tied to the code you will run.

**Setup:** install Claude Code (docs.claude.com, under Claude Code; needs a Claude Pro or Max subscription or an Anthropic API key). In a terminal, go to the repository folder and run `claude`. Press Shift+Tab until it shows **plan mode**, so it reads and explains without changing files.

**Where to point it**

| Path | What it holds |
|---|---|
| `Docs/` | These docs |
| `Assets/Scripts/` | Experiment code: trial sequencing (`TrialBlockRunner`), stimulus (`StimulusBuilder`), logging (`CsvLogger`) |
| `Assets/ExperimentSpecs/` | One asset per experiment |
| `Tools/Analysis/`, `Agents/SwapPilot/Analysis/` | Analysis scripts |

**Starter questions**

- "Walk me through one trial from start to response, naming the scripts and functions involved."
- "Compare `Exp_DensityCompare_VRDots` and `Exp_DensityCompare_HighDens`: list every parameter that differs."
- "What exactly happens to the dots at translation onset on a CM swap trial?"
- "Analyze this session file and report percent correct by SwapType and Cond."
- Questions can be in Turkish.

**Cautions**

- Ask it to quote the file and line behind any claim about timing or parameters.
- Don't let it change specs or scripts on the shared branch; make your own branch, and create new specs instead of editing existing ones.
- Gene's working notes are not in the repository, so ask Gene when something looks odd.
