# VRDots — Quick Reference for Collaborating Labs

*G. Stoner · September 2026*

---

## One-time setup (do once, then skip to "Each session" below)

1. Create a Meta developer account at `developer.oculus.com` and enable **Developer Mode** on the Quest 3 (`Settings → System → Developer Options`).
2. Install **Unity Hub**, then install Unity **6000.2.7f2** with the **Android Build Support** module.
3. Install **Android Debug Bridge (ADB)** — download platform-tools from `developer.android.com/tools/releases/platform-tools` and add to your PATH.
4. Accept the GitHub repository invitation from Gene, then clone:
   ```
   git clone -b wip/quest-pilot https://github.com/GeneStoner/UnityQuestDotStimuli.git
   ```
5. Open the cloned folder in Unity Hub. Wait for asset import to finish (5–20 min first time).
6. Verify: `Edit → Project Settings → Player → Other Settings → Active Input Handling = Both`

---

## Each session — step by step

### 1. Load the experiment

1. Open Unity and load the project.
2. Open scene: `Assets/Scenes/UpToDateScene` (double-click in Project panel).
3. In the **Hierarchy**, search for `TrialBlockManager` and click it.
4. In the **Inspector**, find the **TrialBlockRunner** script component and its **Spec** slot.
5. From `Assets/ExperimentSpecs/`, drag the experiment asset into the **Spec** slot.
   - Gene will tell you which asset to use each session (e.g. `Exp_DensityCompare_HighDens`).
6. **Cmd+S / Ctrl+S** — save the scene. Required before every build.

### 2. Build and deploy

1. Connect the Quest 3 to the computer via USB-C (data cable, not charge-only).
2. **Put on the headset** — accept the *"Allow USB debugging?"* dialog that appears inside.
3. In Unity: `File → Build Settings → Build and Run`.
4. Wait for the build to complete (~2–5 min). The app installs and launches on the Quest automatically.
   - If it doesn't auto-launch, find it under **Unknown Sources** in the Quest App Library.

### 3. Run the session

- The observer puts on the headset. The app opens to a waiting screen.
- **Right trigger**: advance / confirm.
- **Right thumbstick**: report the perceived translation direction (push toward the motion).
- The observer should maintain fixation on the central dot throughout each trial.
- Sessions take **10–20 minutes** depending on the experiment.
- Data saves automatically at the end of each block.

### 4. Pull data and send to Gene

After the session, with the Quest still connected:

```
adb pull /sdcard/Android/data/com.genestoner.vrdptsrebuildX.test/files/ ~/VRDotsData/
```

Each session produces three files (`.tsv`, `.tsv.meta.json`, `.tsv.sidecar.json`). Send all three to Gene at `generstoner@gmail.com`.

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| "No Android device" | Put on headset and accept the USB debugging dialog |
| App not found after build | Check Unknown Sources in App Library |
| Controller input not working | Verify Active Input Handling = "Both" in Project Settings |
| Build fails | Ensure `Cmd+S` was pressed before building |
| Quest not charging/booting | Let it charge for 15 min before connecting for a session |

---

## Contact

Gene Stoner — `generstoner@gmail.com`

Repository: `https://github.com/GeneStoner/UnityQuestDotStimuli` · branch `wip/quest-pilot`
