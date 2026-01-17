# VR Dots Quest Project Status
**Date:** 2026-01-17
**Branch:** `wip/quest-pilot`
**Last Commit:** `24ad698` - Fix Quest data logging

---

## Current State: WORKING

Quest data logging is now fully functional. A 64-trial session completed successfully with:
- **Overall accuracy:** 76.2%
- **CUED:** 84.4% | **UNCUED:** 67.7%
- **Red translating:** 93.8% | **Green translating:** 58.1%

Data files are saved to Quest external storage and can be pulled via ADB.

---

## Key Paths

### On Mac (Development Machine)

| Purpose | Path |
|---------|------|
| Unity Project | `/Users/genestoner1/UnityProjectsLocal/VRDptsRebuild/` |
| C# Scripts | `/Users/genestoner1/UnityProjectsLocal/VRDptsRebuild/Assets/Scripts/` |
| Analysis Scripts | `/Users/genestoner1/UnityProjectsLocal/VRDptsRebuild/Tools/Analysis/` |
| Mac Session Data | `/Users/genestoner1/Library/Application Support/ThatsRandom/VRDotsDataFiles/` |
| Navigation Tools | `/Users/genestoner1/UnityProjectsLocal/VRDptsRebuild/Tools/` |

### On Quest (Android)

| Purpose | Path |
|---------|------|
| App Data (ADB accessible) | `/storage/emulated/0/Android/data/com.genestoner.vrdptsrebuildX.test/files/` |
| App Package Name | `com.genestoner.vrdptsrebuildX.test` |

---

## Navigation Scripts (Double-click to run)

Located in `Tools/` folder:

| Script | Purpose |
|--------|---------|
| `goto_project.command` | Opens Unity project folder in Finder |
| `goto_computer_data.command` | Opens Mac data folder in Finder |
| `goto_quest_data.command` | Lists Quest data files via ADB in Terminal |

---

## Common ADB Commands

```bash
# List Quest data files
adb shell ls -la /storage/emulated/0/Android/data/com.genestoner.vrdptsrebuildX.test/files/

# Pull all Quest data to current directory
adb pull /storage/emulated/0/Android/data/com.genestoner.vrdptsrebuildX.test/files/ .

# Pull specific session
adb pull /storage/emulated/0/Android/data/com.genestoner.vrdptsrebuildX.test/files/vr_dots_session_YYMMDD_HHMM.tsv .

# View Unity logs in real-time
adb logcat -s Unity:V

# Clear log buffer before testing
adb logcat -c

# Check if Quest is connected
adb devices
```

---

## Analysis Workflow

```bash
# 1. Pull data from Quest
adb pull /storage/emulated/0/Android/data/com.genestoner.vrdptsrebuildX.test/files/ "/Users/genestoner1/Library/Application Support/ThatsRandom/VRDotsDataFiles/"

# 2. Run analysis (generates _summary.txt, _summary.json, _plots.png, _trajectory_examples.png)
cd /Users/genestoner1/UnityProjectsLocal/VRDptsRebuild/Tools/Analysis
python3 analyze_vr_dots_v2.py "/Users/genestoner1/Library/Application Support/ThatsRandom/VRDotsDataFiles/vr_dots_session_YYMMDD_HHMM.tsv"
```

---

## Key Scripts and Their Roles

| Script | Role | Notes |
|--------|------|-------|
| `TrialBlockRunner.cs` | Main experiment controller | Manages trial flow, calls CsvLogger |
| `CsvLogger.cs` | Data logging | Writes TSV, meta.json, sidecar.json |
| `ExperimentSpec.cs` | Trial generation | ScriptableObject defining conditions |
| `ExpSpecTestPhase.asset` | Current experiment config | Instance of ExperimentSpec |
| `StimulusConditionsLibrary.cs` | Condition definitions | CUED/UNCUED, rotation configs |
| `DotFieldBuilder.cs` | Stimulus rendering | Creates/animates dot fields |
| `FixationController.cs` | Fixation target | Shader-based fixation cross |

---

## Data File Formats

Each session produces 3 files:

| File | Content |
|------|---------|
| `*.tsv` | Trial-by-trial data (tab-separated) |
| `*.tsv.meta.json` | Session metadata, stats, schema info |
| `*.tsv.sidecar.json` | Full stimulus definitions, trajectory library |

### TSV Columns
```
Trial, Cond, RotCfg, TransDeg, RespDeg, RespIndex, RespDigit, RTf,
OnsetFrame, TransStartFrame, TransEndFrame, TotalFrames,
SeedA0, SeedA1, SeedB2, SeedB3, DelayedFieldColor, EndKey, Device,
MkHash32, ColorHash32, MotionTypeByFrame_SubfieldCodes, ColorByFrame_SubfieldCodes
```

### Response Codes
- `RespDeg=-1, RespIndex=-1, RespDigit=-1`: No valid directional response (trial requeued)
- `EndKey=""`: Normal trial end
- `EndKey="ABORT"`: App quit mid-trial
- `EndKey="TIMEOUT"`: Response window expired

---

## Known Issues / TODO

### 1. Fixation Target (Priority: High)
- Current fixation cross may not be optimally visible
- Need to adjust: size, color, contrast, depth positioning

### 2. Parameter Source Confusion (Priority: Medium)
- `ExpSpecTestPhase.asset` (ScriptableObject) defines experiment parameters
- `TrialBlockRunner` Inspector may have duplicate/override fields
- Some Inspector changes may have no effect if code reads from asset
- **Action:** Audit which parameters are authoritative; consolidate to single source

### 3. Debug Logging Cleanup (Priority: Low)
- `TrialBlockRunner.cs:194` has temporary build stamp: `"*** TRIGGER *** Build 2026-01-17"`
- Can revert to cleaner message once debugging complete

---

## Code Quality Assessment

### Redundancy Issues

1. **Path Configuration**
   - `outputFileName` in TrialBlockRunner Inspector can contain full Mac paths
   - CsvLogger now strips path on Android, but this is a workaround
   - **Better:** Use just filename in Inspector, let CsvLogger handle platform paths

2. **Parameter Duplication**
   - ExperimentSpec asset vs TrialBlockRunner Inspector fields
   - Some timing/display params may exist in both places
   - **Risk:** Confusing which value is actually used

3. **Condition Library**
   - `StimulusConditionsLibrary.cs` has hardcoded condition definitions
   - Tightly coupled to ExperimentSpec trial generation
   - Works, but inflexible for new experiment types

### Architecture Observations

**Good:**
- Clean separation: TrialBlockRunner (flow) → DotFieldBuilder (rendering) → CsvLogger (data)
- Sidecar.json captures full stimulus definitions for reproducibility
- Hash-based trajectory verification in analysis

**Could Improve:**
- Trial state machine is implicit (booleans + coroutines)
- Consider explicit state enum for clearer flow
- Response handling mixed into Update() loop

### File Organization

```
Assets/Scripts/
├── TrialBlockRunner.cs      # 400+ lines - could split trial logic vs input handling
├── CsvLogger.cs             # 800+ lines - acceptable for logging complexity
├── ExperimentSpec.cs        # Trial generation
├── DotFieldBuilder.cs       # Rendering
├── FixationController.cs    # Fixation
├── StimulusConditionsLibrary.cs  # Condition defs
└── [other support scripts]
```

**Suggestion:** Consider grouping into subfolders:
- `Scripts/Core/` - TrialBlockRunner, ExperimentSpec
- `Scripts/Logging/` - CsvLogger
- `Scripts/Stimulus/` - DotFieldBuilder, FixationController
- `Scripts/Input/` - XR input handling (currently in TrialBlockRunner)

---

## Git Status

```
Branch: wip/quest-pilot
Ahead of origin by 6 commits (not pushed)

Recent commits:
24ad698 Fix Quest data logging by using Android external storage path
5b5d56e Add Quest work status handoff document
1db8ec7 Fix delayed onset visibility and improve directional feedback
843b41f Add real-time directional feedback spot for response tracking
c9a3995 Add shader-based fixation system with visual angle ruler
```

---

## Quick Reference Card

```bash
# === QUEST DATA WORKFLOW ===
# Pull latest data
adb pull /storage/emulated/0/Android/data/com.genestoner.vrdptsrebuildX.test/files/ ~/Desktop/quest_data/

# Analyze most recent session
python3 ~/UnityProjectsLocal/VRDptsRebuild/Tools/Analysis/analyze_vr_dots_v2.py <path_to_tsv>

# === DEBUGGING ===
# Watch Unity logs
adb logcat -s Unity:V

# Clear and watch
adb logcat -c && adb logcat -s Unity:V

# === BUILD ===
# Unity: File > Build And Run (Ctrl+B / Cmd+B)
# Or: Build Settings > Build And Run

# === GIT ===
git status
git log --oneline -5
git push origin wip/quest-pilot
```
