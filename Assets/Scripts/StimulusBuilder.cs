// FILE: StimulusBuilder.cs
//
// RECEIVES values from TrialBlockRunner at trial start.
// Do not edit these Inspector fields to change experiment parameters.
// Edit ExperimentSpec asset (e.g., ExpSpecTestPhase.asset) instead.
//
using System.Collections.Generic;
using System.IO;
using System.Text;
using UnityEngine;
using CondLib = StimulusConditionsLibrary;

[DisallowMultipleComponent]
public class StimulusBuilder : MonoBehaviour
{
    [Header("Viewing")]
    [Tooltip("Viewing distance in meters.")]
    public float viewDistanceMeters = 2.0f;

    [Tooltip("Aperture DIAMETER in degrees of visual angle.")]
    public float apertureDeg = 4f;

    [Header("Dot layout")]
    [Tooltip("Dots per perceptual FIELD (so ~dotsPerField/2 per subfield).")]
    public int dotsPerField = 100;

    [Tooltip("Dot size in meters. Typically set by ExperimentSpec via deg→m.")]
    public float dotSizeMeters = 0.02f;

    [Header("Fallback colors (used only if condition doesn't override)")]
    public Color red   = new Color(0.9f, 0.2f, 0.2f, 1f);
    public Color green = new Color(0.2f, 0.85f, 0.2f, 1f);

    [Header("Aperture boundary handling")]
    [Tooltip("If true, dots that leave the aperture are respawned uniformly inside. If false, they are reflected (edge-biased over time).")]
    public bool respawnWhenOutOfBounds = true;

    // ---------- Runtime container ----------
    public class SubfieldRuntime
    {
        public string name;
        public Transform root;
        public List<Transform> dots;
        public Color color;                  // default color
        public Material material;            // shared material for this subfield

        // NEW: deterministic seed base for respawns
        public int seedBase;

        // Authoritative 2D local position per dot (meters on the stimulus plane,
        // no depth offset, no perspective scale). Updated only by motion steps.
        // ApplyDepthOffsets reads this instead of ToLocalPlane(dot.position) so
        // that perspective scaling never accumulates across frames.
        public Vector2[] trajectoryPos;

        // Cached renderer references — populated in BuildFromCondition so that
        // ApplyScreenSpaceDots never calls GetComponent() per frame.
        public List<Renderer> renderers;

        // Cached material references (one per dot, same order as renderers).
        // Storing these explicitly avoids any sharedMaterial getter ambiguity.
        public List<Material> materials;
    }

    public SubfieldRuntime[] Subfields { get; private set; } = new SubfieldRuntime[4];


    [Tooltip("Base random seed; used to seed subfield RNGs.")]
    public int randomSeed = 12345;

    // ---------- Trajectory logging ----------
    public struct TrajectorySample
    {
        public int frame;          // simulation frame index
        public int subfieldIndex;
        public Vector2 localPos;   // (x,y) in local plane, meters
    }

    public List<TrajectorySample> trajectoryLog = new List<TrajectorySample>();

    [HideInInspector] public float exclusionRadiusMeters = 0f;
    [HideInInspector] public float depthOffset_m = 0f;
    [HideInInspector] public float depthBias_m = 0f;

    [Header("Screen-space rendering (Solution A)")]
    [Tooltip("When true, renders dots directly in screen space using DotScreenSpace shader. " +
             "Eliminates world-space axis-alignment and perspective-accumulation artifacts. " +
             "Toggle off to revert to the classic world-space sphere path instantly.")]
    public bool useScreenSpaceShader = false;

    [Tooltip("Inter-pupillary distance in meters used to compute binocular disparity. " +
             "Default 0.063 m (average adult). Only used when useScreenSpaceShader = true.")]
    public float ipdMeters = 0.063f;

    // Last condition/frame passed to ApplyScreenSpaceDots so that RefreshRotation
    // can re-apply NDC positions during the WaitingForStart preview loop.
    private CondLib.StimulusCondition _lastSSCond;
    private int _lastSSFrame = 0;

    // One-shot diagnostic flag: reset each BuildFromCondition, fires first
    // ApplyScreenSpaceDots call so key shader params are visible in logcat.
    private bool _ssDiagPending;

    float ApertureRadiusMeters => DegToMeters(apertureDeg * 0.5f, viewDistanceMeters);

    // ========================================================================
    // Refresh rotation at trigger press (guaranteed-stable tracking)
    // ========================================================================
    /// <summary>
    /// Recomputes transform.rotation from the current camera position and
    /// rebuilds all dot world positions from their stored trajectoryPos.
    ///
    /// Call this when the user presses the trigger to start a trial
    /// (WaitingForStart → Stimulus transition in TrialBlockRunner). By
    /// that moment the user has been wearing the headset long enough for
    /// XR tracking to fully stabilize — even after mid-session re-donning.
    ///
    /// BuildFromCondition() also sets the rotation, but it fires during
    /// the ITI when tracking may still be recovering after re-donning.
    /// This second call, at trigger press, corrects any residual error.
    /// Depth offsets are reapplied automatically on the first SimStep.
    /// </summary>
    public void RefreshRotation()
    {
        // Enforce viewing distance: builder must be exactly viewDistanceMeters in front of
        // the camera (local Z). This corrects any scene-default or stale override each frame.
        if (viewDistanceMeters > 0f)
            transform.localPosition = new Vector3(0f, 0f, viewDistanceMeters);

        if (Camera.main != null)
        {
            Vector3 dir = (transform.position - Camera.main.transform.position).normalized;
            if (dir.sqrMagnitude > 0.5f)
                transform.rotation = Quaternion.LookRotation(dir, Vector3.up);
        }

        // Rebuild flat dot positions from trajectoryPos with updated transform.
        if (Subfields == null) return;
        foreach (var sf in Subfields)
        {
            if (sf == null || sf.dots == null || sf.trajectoryPos == null) continue;
            for (int k = 0; k < sf.dots.Count && k < sf.trajectoryPos.Length; k++)
            {
                if (sf.dots[k] == null) continue;
                sf.dots[k].position = FromLocalPlane(
                    new Vector3(sf.trajectoryPos[k].x, sf.trajectoryPos[k].y, 0f));
            }
        }

        // In screen-space mode the NDC positions also need refreshing so the
        // WaitingForStart preview stays correct after every RefreshRotation call.
        if (useScreenSpaceShader && _lastSSCond != null)
            ApplyScreenSpaceDots(_lastSSCond, _lastSSFrame);
    }

    // ========================================================================
    // Build geometry from condition (dot positions & default materials)
    // ========================================================================
    public void BuildFromCondition(CondLib.StimulusCondition cond)
    {
        // Enforce viewing distance before computing rotation direction.
        if (viewDistanceMeters > 0f)
            transform.localPosition = new Vector3(0f, 0f, viewDistanceMeters);

        // Set rotation at trial setup as a first-pass estimate. A second,
        // more reliable call happens at trigger press via RefreshRotation().
        if (Camera.main != null)
        {
            Vector3 dir = (transform.position - Camera.main.transform.position).normalized;
            if (dir.sqrMagnitude > 0.5f)
                transform.rotation = Quaternion.LookRotation(dir, Vector3.up);
        }

        ClearChildren();

        if (cond.subfields == null || cond.subfields.Length < 4)
        {
            Debug.LogError("StimulusBuilder: condition.subfields invalid.");
            Subfields = new SubfieldRuntime[4];
            return;
        }

        System.Random rngA = new System.Random(randomSeed);
        System.Random rngB = new System.Random(randomSeed + 99991);

        Subfields = new SubfieldRuntime[4];

        for (int i = 0; i < 4; i++)
        {
            var sf = new SubfieldRuntime
            {
                name = $"Subfield_{i}",
                root = new GameObject($"Subfield_{i}").transform,
                dots = new List<Transform>(Mathf.Max(1, dotsPerField / 2)),
                seedBase = (i < 2) ? (randomSeed + i * 1000003) : (randomSeed + 99991 + i * 1000003)
            };
            sf.root.SetParent(transform, false);

            // Fallback color if condition doesn't override
            sf.color = (i < 2) ? red : green;

            // Shared material per subfield
            sf.material = MakeAdditiveMaterial(sf.color);

            int count = Mathf.Max(1, dotsPerField / 2);
            System.Random rng = (i < 2) ? rngA : rngB;

            sf.trajectoryPos = new Vector2[count];
            sf.renderers     = new List<Renderer>(count);
            sf.materials     = new List<Material>(count);

            for (int d = 0; d < count; d++)
            {
                // Screen-space path uses Quads (UV 0-1 needed for circle shader).
                // Classic path uses Spheres. Both are invisible until enabled by ApplyAppearance.
                var dot = useScreenSpaceShader
                    ? GameObject.CreatePrimitive(PrimitiveType.Quad)
                    : GameObject.CreatePrimitive(PrimitiveType.Sphere);
                dot.name = $"dot_{d}";
                dot.transform.SetParent(sf.root, false);
                dot.transform.localScale = Vector3.one * dotSizeMeters;

                var r = dot.GetComponent<Renderer>();
                Material dotMat = null;
                if (r != null)
                {
                    dotMat = useScreenSpaceShader
                        ? MakeScreenSpaceMaterial(sf.color)
                        : MakeAdditiveMaterial(sf.color);
                    r.sharedMaterial = dotMat; // assign directly; avoids Unity auto-instance copy
                    r.enabled = false; // Start hidden; ApplyAppearance will enable as needed
                }

                Vector2 p = UniformAnnulus(rng, ApertureRadiusMeters, exclusionRadiusMeters);
                dot.transform.position =
                    transform.position + transform.right * p.x + transform.up * p.y;

                sf.dots.Add(dot.transform);
                sf.renderers.Add(r);      // cache — may be null if Renderer missing
                sf.materials.Add(dotMat); // cache material for zero-ambiguity writes
                sf.trajectoryPos[d] = p;
            }

            Subfields[i] = sf;
        }

        int totalDots = 0;
        foreach (var sf in Subfields)
            if (sf != null && sf.dots != null)
                totalDots += sf.dots.Count;

        _ssDiagPending = true; // fire diagnostic on first ApplyScreenSpaceDots call
        Debug.Log($"[StimulusBuilder] Built condition '{cond.name}' with {totalDots} dots total.");
    }

    // ========================================================================
    // Per-frame appearance from attribute trajectories
    // ========================================================================
    public void ApplyAppearance(CondLib.StimulusCondition cond, int frame)
    {
        if (cond == null || cond.subfields == null || Subfields == null) return;
        if (frame < 0 || frame >= cond.timeline.totalFrames) return;

        int count = Mathf.Min(Subfields.Length, cond.subfields.Length);

        for (int s = 0; s < count; s++)
        {
            var tracks  = cond.subfields[s];
            var runtime = Subfields[s];
            if (runtime == null || runtime.dots == null) continue;

            bool visible = true;
            if (tracks.visibleByFrame != null && frame < tracks.visibleByFrame.Length)
                visible = tracks.visibleByFrame[frame];

            Color col = runtime.color;
            if (tracks.colorByFrame != null && frame < tracks.colorByFrame.Length)
                col = tracks.colorByFrame[frame];

            // Update each dot's cached material directly (zero-ambiguity path).
            if (runtime.materials != null)
            {
                for (int k = 0; k < runtime.materials.Count; k++)
                    if (runtime.materials[k] != null)
                        runtime.materials[k].color = col;
            }

            // Enable/disable renderers per visibleByFrame.
            if (runtime.renderers != null)
            {
                for (int k = 0; k < runtime.renderers.Count; k++)
                    if (runtime.renderers[k] != null)
                        runtime.renderers[k].enabled = visible;
            }
        }
    }

    // ========================================================================
    // Stereo depth offset — call AFTER motion stepping each frame
    // ========================================================================
    /// <summary>
    /// Shift dots along the viewing axis based on their depth plane assignment.
    /// Must be called after all motion stepping for the frame, since motion steps
    /// reset dot positions to the fixation plane (Z=0 in local coords).
    /// </summary>
    public void ApplyDepthOffsets(CondLib.StimulusCondition cond, int frame)
    {
        // Screen-space path: disparity is applied in the shader via MaterialPropertyBlock.
        // The classic world-space z-offset is not used.
        if (useScreenSpaceShader)
        {
            ApplyScreenSpaceDots(cond, frame);
            return;
        }

        if (cond == null || Subfields == null || (depthOffset_m == 0f && depthBias_m == 0f)) return;
        if (frame < 0 || frame >= cond.timeline.totalFrames) return;

        int count = Mathf.Min(Subfields.Length, cond.subfields.Length);
        for (int s = 0; s < count; s++)
        {
            if (Subfields[s] == null || Subfields[s].dots == null) continue;
            var tracks = cond.subfields[s];
            if (tracks.depthByFrame == null || frame >= tracks.depthByFrame.Length) continue;

            var dp = tracks.depthByFrame[frame];
            float z = depthBias_m;
            if (dp == CondLib.DepthPlane.Near) z += -depthOffset_m;
            else if (dp == CondLib.DepthPlane.Far) z += depthOffset_m;
            else z = 0f; // Fixation plane: no offset
            if (z == 0f) continue;

            // Depth axis is transform.forward — perpendicular to the stimulus
            // plane by definition, so depth offsets never leak into the lateral
            // (right/up) coordinates read by StepTranslation.
            Vector3 zVec = transform.forward * z;

            // Perspective scale: keeps each dot's cyclopean angular position
            // constant when depth changes. Reads from trajectoryPos (the
            // authoritative unscaled 2D position) so scaling never accumulates
            // across frames regardless of how many times ApplyDepthOffsets runs.
            float perspScale = (viewDistanceMeters + z) / viewDistanceMeters;

            var tpos = Subfields[s].trajectoryPos;
            if (tpos == null) continue;

            var dotList = Subfields[s].dots;
            for (int k = 0; k < dotList.Count; k++)
            {
                var dot = dotList[k];
                if (dot == null) continue;
                dot.position = FromLocalPlane(new Vector3(
                    tpos[k].x * perspScale,
                    tpos[k].y * perspScale,
                    0f)) + zVec;
            }
        }
    }

    // ========================================================================
    // Frame-0 diagnostic dump
    // ========================================================================
    /// <summary>
    /// Writes a CSV snapshot of every dot's state at frame 0 (the WaitingForStart
    /// preview). Call once per trial start, AFTER ApplyDepthOffsets(_currentCond, 0).
    /// Saved to Application.persistentDataPath/frame0_diag_&lt;trialIndex&gt;.csv so it
    /// can be retrieved with adb pull.
    ///
    /// Columns: subfield, dot, depth_plane, traj_x_m, traj_y_m,
    ///          world_x, world_y, world_z, z_offset_m, persp_scale,
    ///          renderer_enabled
    /// </summary>
    public void DumpFrame0Diagnostics(CondLib.StimulusCondition cond, int trialIndex)
    {
        if (cond == null || Subfields == null) return;

        var sb = new StringBuilder();
        sb.AppendLine(
            "subfield,dot,depth_plane,traj_x_m,traj_y_m," +
            "world_x,world_y,world_z,z_offset_m,persp_scale," +
            "half_disp_world,renderer_enabled,renderer_null");

        // Header comment line with global params
        sb.AppendLine(
            $"# depthOffset_m={depthOffset_m:F6} depthBias_m={depthBias_m:F6}" +
            $" viewDist={viewDistanceMeters:F3} ipd={ipdMeters:F4}" +
            $" useSSShader={useScreenSpaceShader} condName={cond.name}");

        int sfCount = Mathf.Min(Subfields.Length, cond.subfields != null ? cond.subfields.Length : 0);

        for (int s = 0; s < sfCount; s++)
        {
            var sf = Subfields[s];
            if (sf == null || sf.dots == null || sf.trajectoryPos == null) continue;

            var tracks = cond.subfields[s];

            // Depth plane and derived values at frame 0
            string dpLabel = "?";
            float zOffset = 0f;
            float perspScale = 1f;
            float halfDispWorld = 0f;
            if (tracks.depthByFrame != null && tracks.depthByFrame.Length > 0)
            {
                var dp = tracks.depthByFrame[0];
                dpLabel = dp.ToString();
                float dz = depthBias_m;
                if      (dp == CondLib.DepthPlane.Near) dz += -depthOffset_m;
                else if (dp == CondLib.DepthPlane.Far)  dz += depthOffset_m;
                else    dz = 0f;
                zOffset    = dz;
                perspScale = (viewDistanceMeters + dz) / viewDistanceMeters;
                // Matches ApplyScreenSpaceDots formula exactly.
                halfDispWorld = -(ipdMeters * dz / (2f * viewDistanceMeters));
            }

            int dotCount = Mathf.Min(sf.dots.Count, sf.trajectoryPos.Length);
            for (int k = 0; k < dotCount; k++)
            {
                var dotT = sf.dots[k];
                if (dotT == null) continue;

                Vector2 tp = sf.trajectoryPos[k];
                Vector3 wp = dotT.position;

                bool rEnabled = false;
                bool rNull = true;
                if (sf.renderers != null && k < sf.renderers.Count)
                {
                    rNull    = sf.renderers[k] == null;
                    rEnabled = !rNull && sf.renderers[k].enabled;
                }

                sb.AppendLine(
                    $"{s},{k},{dpLabel}," +
                    $"{tp.x:F6},{tp.y:F6}," +
                    $"{wp.x:F6},{wp.y:F6},{wp.z:F6}," +
                    $"{zOffset:F6},{perspScale:F6}," +
                    $"{halfDispWorld:F6},{(rEnabled ? 1 : 0)},{(rNull ? 1 : 0)}");
            }
        }

        string path = Path.Combine(
            Application.persistentDataPath,
            $"frame0_diag_{trialIndex:D4}.csv");

        try
        {
            File.WriteAllText(path, sb.ToString());
            Debug.Log($"[StimulusBuilder] Frame-0 diagnostic saved: {path}");
        }
        catch (System.Exception e)
        {
            Debug.LogError($"[StimulusBuilder] Failed to save frame-0 diagnostic: {e.Message}");
        }
    }

    // ========================================================================
    // Screen-space rendering (Solution A)
    // ========================================================================
    /// <summary>
    /// Computes the cyclopean NDC position and binocular disparity for each dot
    /// and pushes the values to each dot's renderer via MaterialPropertyBlock.
    /// Called every frame instead of (and from) ApplyDepthOffsets when
    /// useScreenSpaceShader = true.  TrialBlockRunner requires no changes.
    ///
    /// Coordinate derivation:
    ///   World centre   = FromLocalPlane(trajectoryPos[k])   (fixation plane)
    ///   Billboard axes = transform.right / transform.up     (passed to shader)
    ///   Half size      = dotSizeMeters / 2                  (world metres)
    ///   Half disparity = IPD × Δz / (2 × viewDist)         (world metres)
    ///                    positive = uncrossed/Far, left eye +, right eye −
    ///   Projection     = TransformWorldToHClip in shader     (per-eye correct)
    /// </summary>
    private void ApplyScreenSpaceDots(CondLib.StimulusCondition cond, int frame)
    {
        if (cond == null || Subfields == null) return;
        if (Camera.main == null) return;

        // Store so RefreshRotation can re-apply during WaitingForStart.
        _lastSSCond  = cond;
        _lastSSFrame = frame;

        // Stimulus plane axes — passed to shader so it can build billboard corners
        // in world space without any axis-alignment constraint on the camera.
        Vector4 rightDir = transform.right;
        Vector4 upDir    = transform.up;
        float   halfSize = dotSizeMeters * 0.5f;

        int sfCount = Mathf.Min(Subfields.Length,
                                cond.subfields == null ? 0 : cond.subfields.Length);

        // One-shot diagnostic: fire on first call after each BuildFromCondition.
        bool logThis = _ssDiagPending;
        if (logThis) _ssDiagPending = false;

        var diagSB = logThis ? new System.Text.StringBuilder() : null;
        if (logThis)
            diagSB.Append($"[SSDots] FIRST CALL cond={cond.name} frame={frame} " +
                          $"depthOff={depthOffset_m:F4} bias={depthBias_m:F4} " +
                          $"ipd={ipdMeters:F4} viewDist={viewDistanceMeters:F4}\n" +
                          $"  rightDir={rightDir}  upDir={upDir}  halfSize={halfSize:F5}\n");

        for (int s = 0; s < sfCount; s++)
        {
            var sf = Subfields[s];
            if (sf == null || sf.dots == null || sf.trajectoryPos == null
                           || sf.renderers == null || sf.materials == null) continue;

            // Depth plane → Δz (metres from fixation, same sign logic as ApplyDepthOffsets).
            float Δz = 0f;
            var tracks = cond.subfields[s];
            if (tracks.depthByFrame != null && frame >= 0
                                            && frame < tracks.depthByFrame.Length)
            {
                var dp = tracks.depthByFrame[frame];
                if      (dp == CondLib.DepthPlane.Near) Δz = depthBias_m - depthOffset_m;
                else if (dp == CondLib.DepthPlane.Far)  Δz = depthBias_m + depthOffset_m;
            }

            // Per-eye world-space shift that creates the correct binocular disparity.
            //
            //   For depth D + Δz vs. fixation at D, relative disparity ≈ IPD × Δz / D²
            //   This maps to a world-space shift per eye of: IPD × Δz / (2 × D)
            //
            // Near (Δz < 0) → halfDisp < 0 before negation → after negation positive
            //   Left eye (eyeSign=+1) shifts RIGHT  = crossed / Near disparity ✓
            //   Right eye (eyeSign=−1) shifts LEFT
            // Far (Δz > 0) → halfDisp negative after negation
            //   Left eye shifts LEFT = uncrossed / Far disparity ✓
            float halfDispWorld = -(ipdMeters * Δz / (2f * viewDistanceMeters));

            if (logThis)
                diagSB.Append($"  sub{s}: Δz={Δz:F4} halfDispWorld={halfDispWorld:F6} " +
                              $"nDots={sf.dots.Count} ren0={sf.renderers[0]?.enabled} " +
                              $"mat0={(sf.materials.Count > 0 ? sf.materials[0]?.name : "null")}\n");

            int dotCount = Mathf.Min(sf.dots.Count,
                           Mathf.Min(sf.trajectoryPos.Length, sf.materials.Count));
            for (int k = 0; k < dotCount; k++)
            {
                var dot = sf.dots[k];
                var mat = sf.materials[k];
                if (dot == null || mat == null) continue;

                // Dot centre in world space at the fixation plane.
                Vector3 worldCenter = FromLocalPlane(
                    new Vector3(sf.trajectoryPos[k].x, sf.trajectoryPos[k].y, 0f));

                // Update GameObject position so Unity's frustum culler places the
                // dot in view when it should be (world ≈ render position).
                dot.position = worldCenter;

                // Write directly to the cached per-dot material.
                // The shader's CBuffer is named DotPerRenderer (not UnityPerMaterial),
                // which makes it NOT SRP Batcher compatible. Unity therefore uses the
                // legacy per-draw-call path: properties are uploaded fresh every frame,
                // no stale-CBuffer issues for static WaitingForStart renderers.
                mat.SetVector("_WorldCenter",        new Vector4(worldCenter.x,
                                                                  worldCenter.y,
                                                                  worldCenter.z, 0f));
                mat.SetVector("_RightDir",           rightDir);
                mat.SetVector("_UpDir",              upDir);
                mat.SetFloat ("_HalfSizeMeters",     halfSize);
                mat.SetFloat ("_HalfDisparityWorld", halfDispWorld);

                if (logThis && k == 0)
                    diagSB.Append($"    dot0 worldCenter={worldCenter}\n");
            }
        }

        if (logThis)
        {
            // Write to file (not Debug.Log) so it survives logcat buffer overflow.
            // Pull with: adb pull .../files/ss_diag.txt /tmp/ss_diag.txt
            try
            {
                string diagPath = System.IO.Path.Combine(
                    Application.persistentDataPath, "ss_diag.txt");
                bool append = System.IO.File.Exists(diagPath);
                System.IO.File.AppendAllText(diagPath,
                    $"--- trial (append mode) ---\n{diagSB}\n");
                Debug.Log($"[SSDots] Diagnostic appended to {diagPath}");
            }
            catch (System.Exception e)
            {
                Debug.LogWarning($"[SSDots] Could not write diagnostic: {e.Message}");
            }
        }
    }

    /// <summary>
    /// Creates a material using the DotScreenSpace shader for screen-space rendering.
    /// Falls back to MakeAdditiveMaterial if the shader is not found.
    /// </summary>
    Material MakeScreenSpaceMaterial(Color c)
    {
        Shader sh = Shader.Find("Custom/DotScreenSpace");
        if (sh == null)
        {
            Debug.LogWarning("[StimulusBuilder] DotScreenSpace shader not found — " +
                             "falling back to additive material. " +
                             "Ensure 'Assets/Shaders/DotScreenSpace.shader' is in the project.");
            return MakeAdditiveMaterial(c);
        }

        var m = new Material(sh);
        m.SetColor("_Color", c);
        return m;
    }

    // ========================================================================
    // Motion steps
    // ========================================================================
    public void StepRotation(int subfieldIndex, float degPerSec, float dt, int dirSign)
    {
        if (!IsValid(subfieldIndex)) return;

        float ang = degPerSec * dt * Mathf.Sign(dirSign == 0 ? 1 : dirSign);
        Quaternion q = Quaternion.AngleAxis(ang, transform.forward);

        var dots = Subfields[subfieldIndex].dots;
        var tpos = Subfields[subfieldIndex].trajectoryPos;
        for (int k = 0; k < dots.Count; k++)
        {
            var t = dots[k];
            Vector2 tp = tpos[k];
            Vector3 local = q * new Vector3(tp.x, tp.y, 0f);
            HandleOutOfBounds(subfieldIndex, k, ref local, frame: -1);
            tpos[k] = new Vector2(local.x, local.y);
            t.position = FromLocalPlane(local);
        }
    }

    public void StepTranslation(int subfieldIndex, Vector2 deltaLocalMeters, int frame = -1)
    {
        if (!IsValid(subfieldIndex)) return;

        var dots = Subfields[subfieldIndex].dots;
        var tpos = Subfields[subfieldIndex].trajectoryPos;
        for (int k = 0; k < dots.Count; k++)
        {
            var t = dots[k];

            Vector2 tp = tpos[k];
            Vector3 lp = new Vector3(tp.x + deltaLocalMeters.x, tp.y + deltaLocalMeters.y, 0f);

            HandleOutOfBounds(subfieldIndex, k, ref lp, frame);

            tpos[k] = new Vector2(lp.x, lp.y);
            t.position = FromLocalPlane(lp);

            if (frame >= 0)
            {
                trajectoryLog.Add(new TrajectorySample
                {
                    frame = frame,
                    subfieldIndex = subfieldIndex,
                    localPos = new Vector2(lp.x, lp.y)
                });
            }
        }
    }

    public void StepTranslationBalanced(int subfieldIndex, float stepMeters, int frame = -1)
    {
        if (!IsValid(subfieldIndex)) return;

        var dots = Subfields[subfieldIndex].dots;
        if (dots == null || dots.Count == 0) return;

        Vector2[] dirs =
        {
            new Vector2( 1, 0),
            new Vector2( 1, 1).normalized,
            new Vector2( 0, 1),
            new Vector2(-1, 1).normalized,
            new Vector2(-1, 0),
            new Vector2(-1,-1).normalized,
            new Vector2( 0,-1),
            new Vector2( 1,-1).normalized
        };

        var tpos = Subfields[subfieldIndex].trajectoryPos;
        for (int k = 0; k < dots.Count; k++)
        {
            var t = dots[k];
            Vector2 delta = dirs[k % dirs.Length] * stepMeters;

            Vector2 tp = tpos[k];
            Vector3 lp = new Vector3(tp.x + delta.x, tp.y + delta.y, 0f);

            HandleOutOfBounds(subfieldIndex, k, ref lp, frame);

            tpos[k] = new Vector2(lp.x, lp.y);
            t.position = FromLocalPlane(lp);

            if (frame >= 0)
            {
                trajectoryLog.Add(new TrajectorySample
                {
                    frame = frame,
                    subfieldIndex = subfieldIndex,
                    localPos = new Vector2(lp.x, lp.y)
                });
            }
        }
    }

    public void StepNonCoherentBalanced(int subfieldIndex,
                                        float speedDegPerSec,
                                        float dt,
                                        float metersPerDeg,
                                        int frame = -1)
    {
        if (!IsValid(subfieldIndex)) return;
        float stepMeters = speedDegPerSec * metersPerDeg * dt;
        StepTranslationBalanced(subfieldIndex, stepMeters, frame);
    }

    // ========================================================================
    // Helpers
    // ========================================================================
    void HandleOutOfBounds(int subfieldIndex, int dotIndex, ref Vector3 lp, int frame)
    {
        float R = ApertureRadiusMeters;
        Vector2 v = new Vector2(lp.x, lp.y);

        bool outsideAperture  = v.magnitude > R;
        bool insideExclusion  = exclusionRadiusMeters > 0f && v.magnitude < exclusionRadiusMeters;
        if (!outsideAperture && !insideExclusion) return;

        if (!respawnWhenOutOfBounds)
        {
            // old behavior: reflect -> edge bias over time
            Vector2 n = v.normalized;
            v -= 2f * n * (v.magnitude - R);
            v *= 0.999f;
            lp.x = v.x;
            lp.y = v.y;
            return;
        }

        // NEW behavior: respawn uniformly in disk, deterministically.
        int seed = Hash(Subfields[subfieldIndex].seedBase, dotIndex, frame);
        System.Random rng = new System.Random(seed);

        Vector2 p = UniformAnnulus(rng, R, exclusionRadiusMeters);
        lp.x = p.x;
        lp.y = p.y;
    }

    static int Hash(int seedBase, int dotIndex, int frame)
    {
        unchecked
        {
            int h = 17;
            h = h * 31 + seedBase;
            h = h * 31 + dotIndex;
            h = h * 31 + frame;
            // Avoid zero seed degeneracy in some RNGs
            if (h == 0) h = 1;
            return h;
        }
    }

    static Vector2 UniformDisk(System.Random rng, float R)
    {
        float u  = (float)rng.NextDouble();
        float r  = R * Mathf.Sqrt(u);
        float th = (float)rng.NextDouble() * (2f * Mathf.PI);
        return new Vector2(r * Mathf.Cos(th), r * Mathf.Sin(th));
    }

    /// <summary>
    /// Sample uniformly from an annulus (ring) with inner radius R_in and outer radius R_out.
    /// Falls back to UniformDisk when R_in &lt;= 0 or R_in &gt;= R_out.
    /// </summary>
    static Vector2 UniformAnnulus(System.Random rng, float R_out, float R_in)
    {
        if (R_in <= 0f || R_in >= R_out)
            return UniformDisk(rng, R_out);

        float u  = (float)rng.NextDouble();
        float r  = Mathf.Sqrt(u * (R_out * R_out - R_in * R_in) + R_in * R_in);
        float th = (float)rng.NextDouble() * (2f * Mathf.PI);
        return new Vector2(r * Mathf.Cos(th), r * Mathf.Sin(th));
    }

    /// <summary>
    /// Randomly reposition all dots in a subfield (uniform annulus), using a deterministic
    /// seed offset that is distinct from normal out-of-bounds respawn seeds.
    /// Call once at translation onset to remove dot-identity continuity.
    /// </summary>
    public void ReplotSubfield(int subfieldIndex, int frame)
    {
        if (!IsValid(subfieldIndex)) return;
        var sf = Subfields[subfieldIndex];
        int count = sf.trajectoryPos.Length;
        for (int d = 0; d < count; d++)
        {
            // Use a large prime offset on frame so these seeds never collide with
            // HandleOutOfBounds seeds (which use the raw frame value).
            int seed = Hash(sf.seedBase, d, frame + 7919983);
            System.Random rng = new System.Random(seed);
            Vector2 p = UniformAnnulus(rng, ApertureRadiusMeters, exclusionRadiusMeters);
            sf.trajectoryPos[d] = p;
        }
    }

    static float DegToMeters(float angleDeg, float viewDistMeters)
    {
        return viewDistMeters * Mathf.Tan(angleDeg * Mathf.Deg2Rad);
    }

    Material MakeAdditiveMaterial(Color c)
    {
        Shader sh =
            Shader.Find("Universal Render Pipeline/Lit")
            ?? Shader.Find("Universal Render Pipeline/Unlit")
            ?? Shader.Find("Standard")
            ?? Shader.Find("Unlit/Color");

        var m = new Material(sh);

        if (m.HasProperty("_BaseColor"))
            m.SetColor("_BaseColor", c);
        if (m.HasProperty("_Color"))
            m.SetColor("_Color", c);

        if (m.HasProperty("_Surface"))
            m.SetFloat("_Surface", 0f); // Opaque

        m.DisableKeyword("_ALPHATEST_ON");
        m.DisableKeyword("_ALPHABLEND_ON");
        m.DisableKeyword("_ALPHAPREMULTIPLY_ON");
        m.renderQueue = (int)UnityEngine.Rendering.RenderQueue.Geometry;

        return m;
    }

    Vector3 ToLocalPlane(Vector3 worldPos)
    {
        Vector3 p = worldPos - transform.position;
        return new Vector3(
            Vector3.Dot(p, transform.right),
            Vector3.Dot(p, transform.up),
            0f
        );
    }

    Vector3 FromLocalPlane(Vector3 localPlane)
    {
        return transform.position
               + transform.right * localPlane.x
               + transform.up    * localPlane.y;
    }

    /// <summary>
    /// Enable/disable all dot subfields as a group (used by TrialBlockRunner).
    /// </summary>
    public void SetDotsActive(bool active)
    {
        if (Subfields == null) return;

        for (int i = 0; i < Subfields.Length; i++)
        {
            var sf = Subfields[i];
            if (sf == null || sf.root == null)
                continue;

            sf.root.gameObject.SetActive(active);
        }
    }

    /// <summary>
    /// Enable/disable a single subfield by index (used for Field A preview during WaitingForStart).
    /// </summary>
    public void SetSubfieldActive(int index, bool active)
    {
        if (Subfields == null || index < 0 || index >= Subfields.Length) return;
        var sf = Subfields[index];
        if (sf == null || sf.root == null) return;
        sf.root.gameObject.SetActive(active);
    }

    /// <summary>
    /// Force all dot renderers in a subfield to enabled=true, overriding visibleByFrame.
    /// Used in the preview state so Field B dots are visible even though frame-0 marks them hidden.
    /// </summary>
    public void ForceSubfieldRendererEnabled(int index)
    {
        if (Subfields == null || index < 0 || index >= Subfields.Length) return;
        var sf = Subfields[index];
        if (sf == null || sf.dots == null) return;
        foreach (var t in sf.dots)
        {
            if (t == null) continue;
            var r = t.GetComponent<Renderer>();
            if (r != null) r.enabled = true;
        }
    }

    private bool IsValid(int i)
    {
        return Subfields != null
               && i >= 0
               && i < Subfields.Length
               && Subfields[i] != null
               && Subfields[i].dots != null;
    }

    // Only delete Subfield_* children, keep other children (fixation, etc.)
    void ClearChildren()
    {
        var toKill = new List<GameObject>();

        foreach (Transform c in transform)
        {
            if (c.name.StartsWith("Subfield_"))
                toKill.Add(c.gameObject);
        }

        foreach (var g in toKill)
        {
#if UNITY_EDITOR
            if (!Application.isPlaying)
                DestroyImmediate(g);
            else
                Destroy(g);
#else
            Destroy(g);
#endif
        }
    }
}