# Flicker Calibration Scene Setup

Heterochromatic flicker photometry (HFP) calibration for isoluminance estimation.
Runs 20 trials (configurable), averages results to determine green intensity that matches red at 1.0.

---

## Controls Reference

### During Calibration

| Action | Keyboard | Quest Controller |
|--------|----------|------------------|
| Start first trial | Space / Return | Either trigger |
| Increase green | Up Arrow / Keypad+ | Right thumbstick UP |
| Decrease green | Down Arrow / Keypad- | Right thumbstick DOWN |
| Confirm trial | Space / Return | Either trigger |
| Reset current trial | R | — |
| Start next trial | Space / Return | Either trigger |

### Workflow
1. Scene loads → "Press TRIGGER or SPACE to start"
2. Trial begins → Flicker starts, adjust green until flicker minimized
3. Confirm → Trial recorded, flicker stops
4. Repeat for all 20 trials
5. Results averaged and saved to `isoluminance_calibration.json`

---

## Quick Setup

### 1. Create New Scene

1. File → New Scene → Basic (Built-in)
2. Save As: `Assets/FlickerCalibration.unity`

### 2. Set Up XR Rig

For Quest:
1. Delete default Main Camera
2. Add XR Origin (XR → XR Origin (VR))
3. Ensure XR Plugin Management is configured for Oculus

### 3. Create Flicker Stimulus

1. Create Empty GameObject: `FlickerAnnulus`
2. Position: `(0, 0, 2)` — 2 meters in front of camera
3. Add Component: `Mesh Filter`
4. Add Component: `Mesh Renderer`
5. Add Component: `FlickerStimulus` (script)

### 4. Create Calibrator Controller

1. Create Empty GameObject: `FlickerCalibrator`
2. Add Component: `FlickerCalibrator` (script)
3. Configure references:
   - **Stimulus**: Drag `FlickerAnnulus`
   - **Experiment Spec**: Drag `ExpSpecTestPhase.asset` (to match main experiment aperture)
   - **XR Input Actions**: Drag `XRI Default Input Actions` asset
   - **Fixation** (optional): See step 5

### 5. (Recommended) Add Fixation Target

1. Create Empty GameObject: `FixationTarget`
2. Position: `(0, 0, 2)` — same distance as stimulus
3. Add Component: `Fixation_Controller`
4. Assign `ExpSpecTestPhase.asset` to its `Spec` field
5. Drag `FixationTarget` to FlickerCalibrator → `Fixation` field

### 6. Build Settings

1. File → Build Settings
2. Add `FlickerCalibration` scene to build
3. Set as scene 0 for standalone calibration, or load from main menu

---

## Hierarchy Structure

```
FlickerCalibration (Scene)
├── XR Origin
│   └── Camera Offset
│       └── Main Camera
├── FlickerAnnulus
│   ├── MeshFilter
│   ├── MeshRenderer
│   └── FlickerStimulus
├── FlickerCalibrator
│   └── FlickerCalibrator (script)
├── FixationTarget
│   └── Fixation_Controller
└── Directional Light (optional)
```

---

## Component Settings Reference

### FlickerStimulus

| Property | Default | Notes |
|----------|---------|-------|
| Inner Radius Deg | 0.5 | Hole for fixation (auto-set from spec) |
| Outer Radius Deg | 2.0 | Matches aperture (auto-set from spec) |
| View Distance Meters | 2.0 | Auto-set from ExperimentSpec |
| Flicker Rate Hz | 20 | Standard HFP rate (15-25 typical) |
| Color A (Red) | (1, 0, 0, 1) | **Fixed at max intensity** |
| Color B (Green) | (0, 0.5, 0, 1) | Adjustable during calibration |

### FlickerCalibrator

| Property | Default | Notes |
|----------|---------|-------|
| **Number Of Trials** | 20 | Trials before averaging |
| Randomize Starting Value | true | Random green each trial |
| Red Intensity | 1.0 | **Fixed at maximum** |
| Green Intensity | 0.5 | Starting point |
| Green Min | 0.1 | Lower bound |
| Green Max | 1.0 | Upper bound |
| Adjustment Step | 0.01 | Per thumbstick tick |
| Thumbstick Deadzone | 0.3 | Ignore small movements |
| Adjustment Hand | Right | Which thumbstick |
| Confirm Hand | Either | Which trigger |
| Show HUD | true | On-screen instructions |

---

## Testing

### In Editor (Keyboard)

1. Play the scene
2. Press Space to start first trial
3. Use Up/Down arrows to adjust green intensity
4. Press Space to confirm when flicker is minimized
5. Repeat for all 20 trials
6. Check Console for results and saved path

### On Quest

1. Build and Run to Quest
2. Press either trigger to start
3. Use right thumbstick up/down to adjust
4. Press trigger to confirm each trial
5. After 20 trials, calibration saves automatically

### Retrieve Calibration Data

```bash
# Pull calibration file from Quest
adb pull /storage/emulated/0/Android/data/com.genestoner.vrdptsrebuildX.test/files/isoluminance_calibration.json ~/Desktop/

# View contents
cat ~/Desktop/isoluminance_calibration.json
```

---

## Integration with Main Experiment

After calibration, the main experiment can load the calibration:

```csharp
// In TrialBlockRunner.Awake() or Start():
var cal = CalibrationData.Load();
if (cal != null)
{
    // Override ExperimentSpec colors with calibrated values
    spec.rgbaRed = cal.GetRedColor();
    spec.rgbaGreen = cal.GetGreenColor();
    Debug.Log($"Using calibrated isoluminance: R={cal.redIntensity}, G={cal.greenIntensity}");
}
```

---

## Output Format

### Console Output (after all trials)

```
[FlickerCalibrator] === CALIBRATION COMPLETE ===
[FlickerCalibrator] Trials: 20
[FlickerCalibrator] Average Green: 0.4523
[FlickerCalibrator] Std Dev: 0.0341
[FlickerCalibrator] Individual results: 0.412, 0.478, 0.445, ...
[CalibrationData] Saved to: /path/to/isoluminance_calibration.json
```

### JSON File

```json
{
    "redIntensity": 1.0,
    "greenIntensity": 0.4523,
    "calibrationDate": "2026-01-20 14:32:15",
    "deviceId": "abc123..."
}
```

---

## Troubleshooting

### Annulus not visible
- Check FlickerAnnulus position (Z should match viewing distance)
- Verify `Custom/SmoothCircle` shader exists in project
- Check MeshRenderer has material assigned

### Flicker too fast/slow
- Adjust `Flicker Rate Hz` on FlickerStimulus (lower = slower)
- 15-20 Hz is typical for HFP

### XR input not working
- Verify `XRI Default Input Actions` asset is assigned
- Check XR Plugin Management → Oculus is enabled
- Ensure controllers are connected and tracked

### Fixation not showing
- Verify Fixation_Controller has ExperimentSpec assigned
- Check `useShaderCircles` is true
- Ensure `Custom/SmoothCircle` shader is available

### Calibration not saving
- Check Console for error messages
- On Quest: verify app has storage permissions
- Check `Application.persistentDataPath` is writable

---

*Updated: 2026-01-20*
