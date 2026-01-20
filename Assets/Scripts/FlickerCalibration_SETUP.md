# Flicker Calibration Scene Setup

Instructions for creating the FlickerCalibration scene in Unity Editor.

---

## Quick Setup (5 minutes)

### 1. Create New Scene

1. File → New Scene → Basic (Built-in)
2. Save As: `Assets/Scenes/FlickerCalibration.unity`

### 2. Set Up Camera

1. Select `Main Camera`
2. Set Position: `(0, 0, 0)`
3. Set Clear Flags: `Solid Color`
4. Set Background: `Black (0, 0, 0)`
5. For VR: Add `TrackedPoseDriver` component (XR Origin setup if using XR Interaction Toolkit)

### 3. Create Flicker Stimulus

1. Create Empty GameObject: `FlickerAnnulus`
2. Position: `(0, 0, 2)` — 2 meters in front of camera
3. Add Component: `Mesh Filter`
4. Add Component: `Mesh Renderer`
5. Add Component: `FlickerStimulus` (script)
6. Configure FlickerStimulus:
   - Inner Radius Deg: `0.5`
   - Outer Radius Deg: `2.0`
   - View Distance Meters: `2.0`
   - Flicker Rate Hz: `20`
   - Color A (Red): `(0.9, 0, 0, 1)`
   - Color B (Green): `(0, 0.5, 0, 1)`

### 4. Create Calibrator Controller

1. Create Empty GameObject: `FlickerCalibrator`
2. Add Component: `FlickerCalibrator` (script)
3. Drag `FlickerAnnulus` → `Stimulus` field
4. Assign XR Input Actions: Drag `XRI Default Input Actions` asset
5. (Optional) Create and assign a `Fixation_Controller` for central fixation

### 5. (Optional) Add Fixation Target

1. Duplicate from main scene or create new:
   - Create Empty: `FixationTarget`
   - Position: `(0, 0, 2)`
   - Add `Fixation_Controller` component
2. Drag to `FlickerCalibrator` → `Fixation` field

### 6. Build Settings

1. File → Build Settings
2. Add `FlickerCalibration` scene to build
3. Ensure it's listed (can set as scene index 0 for testing)

---

## Hierarchy Structure

```
FlickerCalibration (Scene)
├── Main Camera (or XR Origin)
├── FlickerAnnulus
│   ├── MeshFilter
│   ├── MeshRenderer
│   └── FlickerStimulus
├── FlickerCalibrator
│   └── FlickerCalibrator (script)
├── FixationTarget (optional)
│   └── Fixation_Controller
└── Directional Light (optional, for visibility)
```

---

## Component Settings Reference

### FlickerStimulus

| Property | Value | Notes |
|----------|-------|-------|
| Inner Radius Deg | 0.5 | Hole for fixation |
| Outer Radius Deg | 2.0 | Match main experiment aperture |
| View Distance Meters | 2.0 | Match ExperimentSpec |
| Flicker Rate Hz | 20 | Standard HFP rate (15-25 typical) |
| Edge Smoothness | 0.01 | Anti-aliasing |

### FlickerCalibrator

| Property | Value | Notes |
|----------|-------|-------|
| Red Intensity | 0.9 | Fixed reference |
| Green Intensity | 0.5 | Starting point (adjustable) |
| Green Min | 0.1 | Lower bound |
| Green Max | 1.0 | Upper bound |
| Adjustment Step | 0.01 | Per thumbstick tick |
| Thumbstick Deadzone | 0.3 | Ignore small movements |
| Adjustment Hand | Right | Which thumbstick to use |
| Confirm Hand | Either | Which trigger confirms |

---

## Testing

### In Editor (Keyboard)

1. Play the scene
2. Use Up/Down arrows to adjust green intensity
3. Press Space or Return to confirm
4. Press R to reset
5. Check Console for saved calibration path

### On Quest

1. Build and Run to Quest
2. Use right thumbstick up/down
3. Press either trigger to confirm
4. Pull calibration file via ADB:
   ```bash
   adb pull /storage/emulated/0/Android/data/com.genestoner.vrdptsrebuildX.test/files/isoluminance_calibration.json
   ```

---

## Integration with Main Experiment

After calibration, the main experiment should load the calibration:

```csharp
// In TrialBlockRunner.Awake() or Start():
var cal = CalibrationData.Load();
if (cal != null)
{
    // Override ExperimentSpec colors with calibrated values
    spec.rgbaRed = cal.GetRedColor();
    spec.rgbaGreen = cal.GetGreenColor();
    Debug.Log($"[TrialBlockRunner] Using calibrated colors: R={cal.redIntensity}, G={cal.greenIntensity}");
}
```

---

## Troubleshooting

### Annulus not visible
- Check FlickerAnnulus position (should be at viewing distance)
- Verify SmoothCircle shader is in project
- Check material is assigned

### Flicker too fast/slow
- Adjust `Flicker Rate Hz` (lower = slower, easier to perceive)

### XR input not working
- Verify `XRI Default Input Actions` is assigned
- Check XR Plugin Management is configured
- Ensure controllers are connected

### Calibration not saving
- Check Console for error messages
- Verify `Application.persistentDataPath` is writable
- On Quest: ensure app has storage permissions

---

*Created: 2026-01-19*
