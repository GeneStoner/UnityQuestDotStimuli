# Quest VR Pilot Work Status

**Date:** January 15, 2026
**Branch:** `wip/quest-pilot`
**Latest commit:** `1db8ec7` - "Fix delayed onset visibility and improve directional feedback"

---

## Summary

This document tracks the Quest VR implementation progress for the transparent motion psychophysics experiment.

---

## 1. Script Changes Made for Quest Controller Input

### New Files Created:
| File | Purpose |
|------|---------|
| `Assets/Scripts/DirectionalFeedbackSpot.cs` | Real-time thumbstick tracking spot that shows subject's directional response |
| `Assets/Scripts/SmoothFixationTarget.cs` | Shader-based fixation with anti-aliased circles (alternative to cylinder-based) |
| `Assets/Scripts/SquareFixationTarget.cs` | Square bullseye fallback if circles still look bad |
| `Assets/Scripts/VisualAngleRuler.cs` | Calibration ruler showing degree tick marks |
| `Assets/Shaders/SmoothCircle.shader` | Anti-aliased circle shader using `fwidth()` for screen-space AA |

### Modified Files:
| File | Changes |
|------|---------|
| `Assets/Scripts/TrialBlockRunner.cs` | Added `DirectionalFeedbackSpot` integration - calls `BeginTracking()` on response window open, `EndTracking()` on close |
| `Assets/Scripts/Fixation_Controller.cs` | Added `useShaderCircles` toggle (default true) - creates shader-based quads instead of cylinder primitives |
| `Assets/Scripts/StimulusBuilder.cs` | **Fixed visibility bug** - `visibleByFrame` was read but never applied; dots now start with renderer disabled |
| `Assets/Scripts/ExpSpecTestPhase.asset` | Updated: aperture 3.5° (7° diameter), dot size 0.08°, fixation outer 1°, crosshair 0.12° thick |
| `Assets/Settings/Mobile_RPAsset.asset` | MSAA 4x (was 1), render scale 1.0 (was 0.8) |
| `ProjectSettings/GraphicsSettings.asset` | Added SmoothCircle shader to always-included shaders |

---

## 2. What's Currently Working

- **Directional feedback spot**: Tracks thumbstick in real-time during response window
  - Snaps to 8 directions (45° increments)
  - Distance locks at maximum reached, but direction can still change
  - Procedural click sound plays when crossing 8° threshold
  - Hides when response confirmed/canceled

- **Delayed onset**: Now properly hides delayed dot field until onset time
  - Fixed bug where `visibleByFrame` was ignored
  - Dots start with renderer disabled

- **Stimulus sizing**: 7° aperture diameter, 0.08° dot size verified with visual angle ruler

- **XR input**: Thumbstick and trigger bindings working via XRI Default Input Actions

---

## 3. What Needs Attention / Potential Issues

### Fixation Circles Still Pixelated
- User reported circles still look "more square than circular"
- Added shader-based approach with `fwidth()` anti-aliasing
- `Fixation_Controller.useShaderCircles = true` should use new approach
- **May need further investigation** - could be render resolution, foveated rendering, or other Quest settings

### Dot Colors
- Currently using original values: red (0.9, 0.2, 0.2), green (0.2, 0.85, 0.2)
- User mentioned may need to adjust luminances (especially green downward)
- Pure max-luminance colors (1,0,0) and (0,1,0) were tried but reverted

### Variable Naming Issue
- **Note:** No specific variable naming issue was identified in the recent session. If this refers to earlier work, that context may have been lost in summarization.

---

## 4. Next Steps to Investigate

1. **Test delayed onset fix** - Verify delayed dots are truly invisible before onset

2. **Fixation appearance** - If still pixelated:
   - Check if `useShaderCircles` is enabled on the Fixation_Controller in scene
   - Try increasing `edgeSmoothness` parameter
   - Consider render scale > 1.0 (supersampling) at performance cost

3. **Dot luminance calibration** - May need to reduce green to match red perceptually

4. **Click sound** - Currently procedural; may want to adjust frequency/duration for better feedback

---

## 5. Key Component Setup

### DirectionalFeedbackSpot
On the GameObject with this component:
- `Spec` → drag `Assets/Scripts/ExpSpecTestPhase.asset`
- `XR Input Actions` → drag `Assets/Samples/XR Interaction Toolkit/3.1.2/Starter Assets/XRI Default Input Actions.inputactions`
- `Use Procedural Click` → checked (generates click sound automatically)

### TrialBlockRunner
- `Directional Feedback` → drag the DirectionalFeedbackSpot GameObject

### Fixation_Controller
- `Use Shader Circles` → checked (uses quads + SmoothCircle shader)
- `Spec` → assign ExperimentSpec
- Leave cylinder references (ringOuter, ringInner, etc.) unassigned when using shader mode

---

## 6. Commit History (Recent)

```
1db8ec7 Fix delayed onset visibility and improve directional feedback
843b41f Add real-time directional feedback spot for response tracking
c9a3995 Add shader-based fixation system with visual angle ruler
10fd56f Add Quest controller input support for trials
```

---

## 7. Files to Review if Issues Persist

- `StimulusBuilder.cs:156-162` - Visibility application loop
- `Fixation_Controller.cs:380-447` - Shader circle creation and update
- `DirectionalFeedbackSpot.cs:211-257` - Thumbstick tracking logic
- `ExpSpecTestPhase.cs:174-187` - Delayed onset color/visibility setup
