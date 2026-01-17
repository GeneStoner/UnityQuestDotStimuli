// FILE: StimulusBuilder.cs
//
// RECEIVES values from TrialBlockRunner at trial start.
// Do not edit these Inspector fields to change experiment parameters.
// Edit ExperimentSpec asset (e.g., ExpSpecTestPhase.asset) instead.
//
using System.Collections.Generic;
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

    float ApertureRadiusMeters => DegToMeters(apertureDeg * 0.5f, viewDistanceMeters);

    // ========================================================================
    // Build geometry from condition (dot positions & default materials)
    // ========================================================================
    public void BuildFromCondition(CondLib.StimulusCondition cond)
    {
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

            for (int d = 0; d < count; d++)
            {
                var dot = GameObject.CreatePrimitive(PrimitiveType.Sphere);
                dot.name = $"dot_{d}";
                dot.transform.SetParent(sf.root, false);
                dot.transform.localScale = Vector3.one * dotSizeMeters;

                var r = dot.GetComponent<Renderer>();
                if (r != null)
                {
                    r.material = sf.material;
                    r.enabled = false; // Start hidden; ApplyConditionFrame will enable as needed
                }

                Vector2 p = UniformDisk(rng, ApertureRadiusMeters);
                dot.transform.position =
                    transform.position + transform.right * p.x + transform.up * p.y;

                sf.dots.Add(dot.transform);
            }

            Subfields[i] = sf;
        }

        int totalDots = 0;
        foreach (var sf in Subfields)
            if (sf != null && sf.dots != null)
                totalDots += sf.dots.Count;

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

            if (runtime.material != null)
                runtime.material.color = col;

            foreach (var t in runtime.dots)
            {
                if (t == null) continue;
                var r = t.GetComponent<Renderer>();
                if (r != null)
                    r.enabled = visible; // respect visibleByFrame setting
            }
        }
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
        for (int k = 0; k < dots.Count; k++)
        {
            var t = dots[k];
            Vector3 local = ToLocalPlane(t.position);
            local = q * local;
            t.position = FromLocalPlane(local);

            HandleOutOfBounds(subfieldIndex, k, ref local, frame: -1);
            t.position = FromLocalPlane(local);
        }
    }

    public void StepTranslation(int subfieldIndex, Vector2 deltaLocalMeters, int frame = -1)
    {
        if (!IsValid(subfieldIndex)) return;

        var dots = Subfields[subfieldIndex].dots;
        for (int k = 0; k < dots.Count; k++)
        {
            var t = dots[k];

            Vector3 lp = ToLocalPlane(t.position);
            lp.x += deltaLocalMeters.x;
            lp.y += deltaLocalMeters.y;

            HandleOutOfBounds(subfieldIndex, k, ref lp, frame);

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

        for (int k = 0; k < dots.Count; k++)
        {
            var t = dots[k];
            Vector2 delta = dirs[k % dirs.Length] * stepMeters;

            Vector3 lp = ToLocalPlane(t.position);
            lp.x += delta.x;
            lp.y += delta.y;

            HandleOutOfBounds(subfieldIndex, k, ref lp, frame);

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

        if (v.magnitude <= R) return;

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

        Vector2 p = UniformDisk(rng, R);
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