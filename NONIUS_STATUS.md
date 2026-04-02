# Nonius Lines & Field A Preview — Status & Next Steps

## What's Working

### Field A Preview (Mod 1) ✓
Static first-frame dots (sub0 + sub1) are shown during `WaitingForStart` so the subject can establish vergence before the trial begins. No animation — dots appear at their frame-0 positions, depth, and color. Implemented in `TrialBlockRunner.cs`.

### Binocular Nonius Reference Lines ✓
Two vertical line segments appear above and below the fixation cross. They are rendered binocularly (both eyes see both lines). Implemented in `Fixation_Controller.cs` using `NoniusLine.shader`. Toggle: `showNoniusLines` in Inspector (on the active `SmoothFixation` instance). Parameters: `noniusLength_deg`, `noniusWidth_deg`, `noniusGap_deg`, `noniusColor`.

---

## True Dichoptic Nonius Lines — Limitation & Path Forward

### What we want
Classic nonius lines: top segment visible only to one eye, bottom segment only to the other. When the eyes are properly converged, they appear vertically aligned. Any vergence error produces a visible offset.

### Why it doesn't work yet
Unity's shader system cannot distinguish left-eye vs. right-eye rendering with the Oculus XR Plugin on Android. Specifically:

- **`unity_StereoEyeIndex`** is always `0` in both vertex and fragment shaders — the Oculus driver handles per-eye matrix selection at the GPU/Vulkan level (`gl_ViewIndex` in VK_KHR_multiview), below where Unity's HLSL abstraction can observe it.
- **`cam.stereoActiveEye`** always returns `Mono` from `RenderPipelineManager.beginCameraRendering` — Unity's C# callback does not fire separately per eye; the Oculus compositor handles eye compositing after the fact.
- **`cam.worldToCameraMatrix`** is identical in both per-frame callbacks — no way to distinguish which pass is which.
- **`Camera.stereoTargetEye = Right`** on URP overlay cameras — ignored by the Oculus XR Plugin on Android.
- **STEREO_INSTANCING_ON / STEREO_MULTIVIEW_ON** pragmas — not activated in Multipass mode.

All of these were attempted in **Multipass mode** (`m_StereoRenderingModeAndroid: 0`) and confirmed non-functional via `adb logcat`.

### Current attempt: Multiview mode — UNTESTED ON DEVICE

`OculusSettings.asset` switched from Multipass (0) to **Multiview (2)**. In Multiview, Unity submits both views in a single pass using `GL_OVR_multiview`, which populates `unity_StereoEyeIndex` per-fragment via the multiview extension. The shader now discards fragments where `unity_StereoEyeIndex != _TargetEye`. Top segment → left eye (`_TargetEye=0`), bottom segment → right eye (`_TargetEye=1`).

**Test on Quest before running experiments.** Check: with nonius lines enabled, cover left eye — only bottom line should be visible. Cover right eye — only top line should be visible.

**If Multiview breaks rendering or eye index is still always 0**: revert `m_StereoRenderingModeAndroid` to `0` in `OculusSettings.asset`. The shader's `_TargetEye = -1` binocular path still works in Multipass (old behavior — both eyes see both lines).

### Fallback: OVR Compositor Layers
The guaranteed Meta API. Bypasses Unity's rendering pipeline entirely, injects content per eye into the compositor. Steps:

1. Import **Meta XR All-in-One SDK** (`com.meta.xr.sdk.core`) via Package Manager.
2. Add `OVROverlay` component (Underlay or Overlay type).
3. Assign separate `RenderTexture` per eye; render each nonius segment into its RT each frame.
4. Compositor guarantees monocular delivery.

Non-trivial (separate camera setup, RT management). Use if Multiview attempt fails.

---

## Pending Items

### Mod 3 — Minimum vergence hold (not implemented)
**Design decision needed:** Should there be a minimum time after Field A appears before the subject can trigger the trial, enforced by code? Current plan is behavioral — instruct subjects to press trigger only when nonius lines are aligned. This may be sufficient. If drift is observed in the data, add a 500ms ready-hold in `TrialBlockRunner.WaitingForStart` before accepting trigger input.

### Scene cleanup (not urgent)
- `SmoothFixation` GameObject (under Main Camera) has ~80 vestigial mesh children from the old ring/crosshair approach. Safe to delete the children; the `Fixation_Controller` component on the parent is what's active.
- Inactive `TrialBlockManager` (wrong namespace) — safe to delete.
- Inactive `Fixation_Fancy` under StimulusRoot/Main Camera — safe to delete.
- `Assets/_Recovery/` — Unity crash-recovery files (`0.unity`, `1.unity`, etc.). Safe to delete after verifying the scene.

### Git
Branch `wip/quest-pilot` has several unpushed commits. Run `git push` when next at a stable state.

### Analysis (`analyze_vr_dots_v2.py`)
Depth column support (`by_depth`, `by_cond_x_depth` aggregations) is missing. Backburner — current per-session analyses done manually.

### More Zd sessions
DepthSwap50 (0.05m) attenuation is only 8.9pp and n.s. with current N. Collect additional sessions.

---

## Key Settings Reminder
- Active `Fixation_Controller`: `SmoothFixation` (under Main Camera) — this is what `TrialController.fixation` points to.
- `NoniusLine.shader` is in **Always Included Shaders** (`ProjectSettings/GraphicsSettings.asset`) — required so `Shader.Find()` works in builds.
- Stereo mode: **Multipass** (`m_StereoRenderingModeAndroid: 0` in `OculusSettings.asset`).
