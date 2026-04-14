# VRDots Rendering: How It Works Now, and How to Do It Better
*For a Unity newcomer — no prior graphics programming assumed*
*GS + Claude, 2026-04-14*

---

## Part 1 — How the stimulus is currently rendered

### The basic idea: dots are real 3D objects

Every dot in the display is a standard Unity **GameObject** — specifically a sphere primitive — placed somewhere in 3D world space. Unity's job is to figure out where each sphere appears on screen given the camera's position, orientation, and lens. This happens automatically through a process called **perspective projection**.

```
World space (3D)          Camera projects         Screen (2D pixels)
  dot at (x, y, z)   ──────────────────────────►   pixel at (px, py)
```

In VR, Unity runs this process **twice per frame** — once for the left eye camera and once for the right eye camera — with the cameras separated by the inter-pupillary distance (~63 mm). The slight difference between the two rendered images is what creates the stereo depth illusion.

### How StimulusBuilder places the dots

The `StimulusBuilder` component sits at a fixed location in the scene — 2 meters in front of the starting head position. It maintains a flat, invisible **stimulus plane** that faces the camera (like a board held up in front of you).

For each dot, the code works in **local 2D coordinates** — a position `(x, y)` measured in meters on the stimulus plane, with the origin at the plane's centre:

```
    transform.up  ▲
                  │   dot at (x, y) meters
                  │      ●
        ──────────┼──────────► transform.right
                  │
                  │       (plane faces camera via transform.forward)
```

To convert that 2D position to a real 3D world position, the code does:

```csharp
// FromLocalPlane():
worldPos = transform.position
         + transform.right * x
         + transform.up    * y;
```

For dots that should appear at a different depth (Near or Far plane), the code adds an offset along the **optical axis** (transform.forward) and also scales x and y slightly to preserve the dot's angular position under perspective:

```csharp
float perspScale = (viewDistance + z) / viewDistance;
worldPos = FromLocalPlane(new Vector3(x * perspScale, y * perspScale, 0))
         + transform.forward * z;
```

This `perspScale` step is what keeps a dot at (x, y) looking like it's at the same visual angle whether it's in the Near or Far plane — without it, the Far dots would drift outward and the Near dots inward.

### What the camera does automatically

Once the dots are placed in world space, Unity's **camera pipeline** takes over:

1. **Vertex shader**: transforms each sphere vertex from world space into the camera's coordinate system, then into **clip space** (a normalised coordinate system that the GPU understands)
2. **Perspective divide**: divides x and y by z, which is what makes distant objects appear smaller
3. **Rasterisation**: turns the projected triangles into coloured pixels on screen
4. **Stereo rendering**: the whole process repeats for the right eye at a slightly different camera position

The developer never writes any of this — it is completely automatic in Unity with the XR plugin active.

### What goes wrong — and why we're here

The current approach has two sources of fragility:

**Problem 1 — The optical axis must match `transform.forward` exactly.**
`FromLocalPlane` decomposes world positions along `transform.right` and `transform.up`. If the depth offset is applied along any other axis (even slightly), it leaks into the x/y coordinates that `StepTranslation` reads back next frame, causing the dots to drift laterally on every frame. For this reason, `transform.rotation` must point directly at the camera. We set it once per trial in `BuildFromCondition()` (after XR tracking is guaranteed stable). If the rotation is even slightly wrong, you get the upward jerk artifact.

**Problem 2 — Perspective scaling must be managed manually.**
Because we want dots to stay at a fixed visual angle when they change depth planes (at tStart in the Z condition), we apply `perspScale` ourselves. This has to be done carefully from authoritative `trajectoryPos` coordinates — if it is applied to world positions read back from the scene, the scaling accumulates across frames and the dots explode outward.

**Both problems arise because we are trying to control a perspective camera while fighting its natural behaviour.** The camera wants to scale things with depth; we're manually undoing that. The camera needs a specific axis relationship; we have to maintain it by hand.

---

## Part 2 — A better approach: bypassing perspective entirely

There are two distinct problems to solve:

1. **Perspective-free dot rendering** — dots should appear at a fixed visual angle regardless of their depth plane
2. **True dichoptic rendering** — sending completely different images to the left and right eyes

These can be solved independently or together.

---

### Solution A — Shader-based screen-space dots

Instead of placing sphere GameObjects in 3D, you draw dots **directly in screen space** — at a fixed pixel position — and add depth (disparity) by shifting the dot's position in opposite directions for the left and right eyes.

#### How a screen-space dot shader works

A **shader** is a small program that runs on the GPU. Instead of the vertex shader transforming a 3D position into screen space (with perspective), you write the vertex shader to output clip-space coordinates directly:

```hlsl
// Pseudocode — vertex shader
float2 screenPos = dotCenter_screenspace;   // set by CPU, in NDC [-1,+1]
float  disparity  = dotDepth_pixels;        // positive = Far, negative = Near

// Shift opposite directions per eye
float eyeSign = unity_StereoEyeIndex == 0 ? -1.0 : +1.0;   // left=-1, right=+1
screenPos.x += eyeSign * disparity * 0.5;

output.position = float4(screenPos, 0, 1);  // w=1 → no perspective divide
```

The key line is `output.position = float4(screenPos, 0, 1)` — by setting `w = 1` and `z = 0`, the GPU's perspective divide (`x/w, y/w`) has no effect, and the dot appears at exactly the screen position you specified, regardless of any world-space depth.

Disparity (the horizontal shift between eyes) creates the perceived depth without using the camera's perspective at all.

#### What the CPU side looks like

```csharp
// In C# (MonoBehaviour):
// Convert desired visual angle to screen pixels:
float dotX_px = angleDeg * Screen.width / cameraFOV_deg;

// Compute disparity from desired depth:
// For a dot at physical depth D from the observer, and IPD in meters:
// disparity_m = IPD * (1/screenDistance - 1/D)
// disparity_px = disparity_m / screenWidth_m * Screen.width
float disparity_px = IPD_m * (1f/screenDist - 1f/dotDepth) / screenWidth_m * Screen.width;

// Pass to material:
mat.SetVector("_DotCenter", new Vector2(dotX_px, dotY_px));
mat.SetFloat("_Disparity", disparity_px);
```

#### What this buys you

| Property | Current approach | Shader approach |
|----------|-----------------|-----------------|
| Dot size with depth | Scales with perspective (must manually undo) | Fixed — you set it directly |
| Depth offset axis | Must match transform.forward exactly | Disparity is just a pixel shift — no axis issue |
| Head movement sensitivity | Rotates with transform → must recompute per trial | Screen-space — immune to head rotation |
| Complexity | Simple C# but fragile axis geometry | More complex setup but robust once written |
| Portability | Works with any Unity camera | Requires shader authoring |

The trajectory position system (`trajectoryPos[]`) and all the motion logic (`StepTranslation`, `StepRotation`, etc.) can be kept exactly as-is — they output 2D local coordinates in meters, which you convert to screen pixels and pass to the shader. The rendering layer is swapped underneath without changing the experiment logic.

---

### Solution B — OVR Compositor Layers (true dichoptic display)

This is the Meta-specific path to sending **completely different images to each eye**. It bypasses Unity's rendering pipeline and composites directly at the display compositor level.

#### Why Unity's normal stereo rendering is not truly dichoptic

In standard Unity VR rendering, the scene is rendered twice — once from the left camera, once from the right. But **both cameras look at the same scene**. You cannot make a single GameObjcet visible to only one eye using standard Unity APIs (Unity's layer-based culling masks exist but are unreliable across XR backends and don't work at the compositor level).

What you actually want for true dichoptic display is to feed two independent images directly to the compositor — the software that sits between Unity and the headset display hardware.

#### What OVR Compositor Layers are

Meta's XR SDK (available via the Meta XR SDK package in Unity) exposes a class called `OVROverlay` (or `OVRPassthroughLayer` for passthrough, but the same principle). An `OVROverlay` lets you submit a `RenderTexture` that is composited onto the display **after** Unity finishes rendering, at the hardware level.

Crucially, you can specify **left eye only** or **right eye only** for each overlay.

#### A minimal dichoptic setup in Unity

```csharp
// 1. Create two RenderTextures (one per eye)
RenderTexture leftEyeTex  = new RenderTexture(1024, 1024, 0);
RenderTexture rightEyeTex = new RenderTexture(1024, 1024, 0);

// 2. Add an OVROverlay component to a GameObject
OVROverlay overlay = gameObject.AddComponent<OVROverlay>();
overlay.textures = new Texture[] { leftEyeTex, rightEyeTex };
overlay.currentOverlayShape = OVROverlay.OverlayShape.Quad;
overlay.currentOverlayType  = OVROverlay.OverlayType.Overlay;

// 3. At runtime, draw whatever you want into each RenderTexture
//    using Graphics.Blit(), a secondary camera, or CPU pixel writes
Graphics.Blit(myLeftImage,  leftEyeTex);
Graphics.Blit(myRightImage, rightEyeTex);
```

The Quest compositor then places the two textures on the display at the specified world-space position, but with completely independent content per eye.

#### What "arbitrary images per eye" means in practice

With this setup you can:

- Show a **Gabor patch to the left eye and noise to the right eye** (classic binocular rivalry)
- Show **monocular probe stimuli** to one eye while the other sees the normal display
- Implement **dichoptic masking** experiments
- Show **different dot fields** to each eye without any stereo crosstalk

The images can be generated by a secondary Unity camera rendering an off-screen scene, or they can be pixel arrays written directly from C# (slow but possible for simple stimuli), or they can be pre-baked textures.

#### Limitations

- Requires the **Meta XR SDK** package (not the default Unity XR plugin)
- The overlay quad must be placed in world space — its *position* is common to both eyes (the content differs, not the quad position)
- Resolution is limited by `RenderTexture` size and the overlay's world-space size
- Latency is identical to normal rendering — this is not a timing hack
- Cannot currently do this with the standard `UnityEngine.XR` or `OpenXR` backends alone

---

## Part 3 — What we should actually do for VRDots

### Near-term (next experiment block): stay with GameObjects, keep current fixes

The current code is working correctly after the per-trial rotation fix. The `trajectoryPos` architecture cleanly separates motion logic from rendering. For the DecoupledDots and ZdA/ZdB experiments, the current approach is adequate.

### Medium-term: shader-based dots

The right architectural move is to replace the sphere GameObjects with a single quad per subfield rendered by a custom shader that:
1. Takes `trajectoryPos[]` as input (a `ComputeBuffer`)
2. Renders each dot at its exact screen-space angular position
3. Applies disparity for depth rather than world-space z-offset
4. Is immune to head rotation, perspective accumulation, and axis alignment issues

This ports directly — the motion logic, subfield structure, and experiment spec system all stay intact. Only `BuildFromCondition`, `ApplyDepthOffsets`, and the `FromLocalPlane`/`ToLocalPlane` helpers are replaced.

### Long-term: OVR Compositor Layers for dichoptic

If the science requires sending truly different images to each eye — monocular probes, binocular rivalry stimuli, or dichoptic masking — the OVR Compositor Layer path is the right one. It requires adopting the Meta XR SDK and learning the overlay API, but it is the only path to genuine dichoptic display on Quest hardware.

---

## Glossary (for the true newcomer)

| Term | Plain English |
|------|---------------|
| **World space** | The 3D coordinate system the whole scene lives in. Unity units ≈ metres. |
| **Screen space / clip space** | The 2D coordinate system of the final rendered image. Ranges from −1 to +1 in x and y. |
| **Perspective projection** | The mathematical transform that makes far objects look smaller, the way real eyes and cameras work. |
| **Shader** | A small program that runs on the GPU. A *vertex shader* transforms 3D positions; a *fragment shader* colours pixels. |
| **RenderTexture** | A texture that Unity can draw into at runtime, as if it were a screen. |
| **Disparity** | The horizontal pixel offset between the left-eye and right-eye versions of the same object. Larger disparity = stronger depth sensation. |
| **IPD** | Inter-pupillary distance — the distance between your eyes (~63 mm for most adults). Determines how much disparity corresponds to a given physical depth. |
| **Compositor** | The hardware/software layer between the rendering engine and the physical display. On Quest, Meta's compositor handles lens distortion, reprojection, and layer compositing. |
| **Dichoptic** | Showing different images to each eye independently. Requires compositor-level control; cannot be achieved with standard Unity per-GameObject visibility. |
