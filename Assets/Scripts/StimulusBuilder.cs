// FILE: StimulusBuilder.cs
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
    public Color red = new Color(0.9f, 0.2f, 0.2f, 1f);
    public Color green = new Color(0.2f, 0.85f, 0.2f, 1f);

    [Header("Central exclusion (meters)")]
    [Tooltip("Inner exclusion radius in meters (0 = none). Set from ExperimentSpec.")]
    public float centralExclusionRadiusMeters = 0f;

    [Tooltip("How aggressively to push dots out of the exclusion zone. 1.0 = just outside; >1 adds margin.")]
    public float exclusionPushMargin = 1.002f;

    // ---------- Runtime container ----------
    public class SubfieldRuntime
    {
        public string name;
        public Transform root;
        public List<Transform> dots;
        public Color color;                  // default color
        public Material material;            // shared material for this subfield
        public CondLib.Eye eye;
        public CondLib.DepthPlane plane;
        public CondLib.MotionKind initialMotion;
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

        float R = ApertureRadiusMeters;
        float inner = Mathf.Clamp(centralExclusionRadiusMeters, 0f, R * 0.999f);

        for (int i = 0; i < 4; i++)
        {
            var sf = new SubfieldRuntime
            {
                name = $"Subfield_{i}",
                root = new GameObject($"Subfield_{i}").transform,
                dots = new List<Transform>(Mathf.Max(1, dotsPerField / 2))
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

                var rend = dot.GetComponent<Renderer>();
                if (rend != null)
                    rend.material = sf.material;

                Vector2 p = (inner > 0f)
                    ? UniformAnnulus(rng, inner, R)
                    : UniformDisk(rng, R);

                dot.transform.position =
                    transform.position + transform.right * p.x + transform.up * p.y;

                sf.dots.Add(dot.transform);
            }

            Subfields[i] = sf;
        }

        // Debug: report how many dots we actually built
        int totalDots = 0;
        foreach (var sf in Subfields)
            if (sf != null && sf.dots != null)
                totalDots += sf.dots.Count;

        float Rm = ApertureRadiusMeters;
        Debug.Log(
            $"[StimulusBuilder] Built condition '{cond.name}' " +
            $"dotsPerField={dotsPerField} dotSize_m={dotSizeMeters:0.####} " +
            $"apertureDeg={apertureDeg:0.###} Rm={Rm:0.####} Dm={(2f * Rm):0.####} " +
            $"viewDist_m={viewDistanceMeters:0.###} innerExcl={centralExclusionRadiusMeters:0.####}m"
        );
        Debug.Log($"[StimulusBuilder] Built condition '{cond.name}' with {totalDots} dots total. innerExcl={centralExclusionRadiusMeters:F4}m");
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
            var tracks = cond.subfields[s];
            var runtime = Subfields[s];
            if (runtime == null || runtime.dots == null) continue;

            // Visibility
            bool visible = true;
            if (tracks.visibleByFrame != null && frame < tracks.visibleByFrame.Length)
                visible = tracks.visibleByFrame[frame];

            // Color
            Color col = runtime.color;
            if (tracks.colorByFrame != null && frame < tracks.colorByFrame.Length)
                col = tracks.colorByFrame[frame];

            // Apply to shared material (all dots in subfield)
            if (runtime.material != null)
                runtime.material.color = col;

            // Toggle renderers
            foreach (var t in runtime.dots)
            {
                if (t == null) continue;
                var r = t.GetComponent<Renderer>();
                if (r != null)
                    r.enabled = visible;
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

        float R = ApertureRadiusMeters;
        float r0 = Mathf.Clamp(centralExclusionRadiusMeters, 0f, R * 0.999f);

        foreach (var t in Subfields[subfieldIndex].dots)
        {
            Vector3 local = ToLocalPlane(t.position);
            local = q * local;
            t.position = FromLocalPlane(local);

            WrapIntoDisk(t, R);
            EnforceCentralExclusion(t, r0);
        }
    }

    // Coherent translation: same delta for all dots in subfield
    public void StepTranslation(int subfieldIndex, Vector2 deltaLocalMeters, int frame = -1)
    {
        if (!IsValid(subfieldIndex)) return;

        float R = ApertureRadiusMeters;
        float r0 = Mathf.Clamp(centralExclusionRadiusMeters, 0f, R * 0.999f);

        foreach (var t in Subfields[subfieldIndex].dots)
        {
            Vector3 lp = ToLocalPlane(t.position);
            lp.x += deltaLocalMeters.x;
            lp.y += deltaLocalMeters.y;

            // outer boundary reflect
            Vector2 v = new Vector2(lp.x, lp.y);
            if (v.magnitude > R)
            {
                Vector2 n = v.normalized;
                v -= 2f * n * (v.magnitude - R);
                v *= 0.999f;
                lp.x = v.x;
                lp.y = v.y;
            }

            t.position = FromLocalPlane(lp);

            // inner boundary keep-out
            EnforceCentralExclusion(t, r0);

            if (frame >= 0)
            {
                Vector3 lp2 = ToLocalPlane(t.position);
                trajectoryLog.Add(new TrajectorySample
                {
                    frame = frame,
                    subfieldIndex = subfieldIndex,
                    localPos = new Vector2(lp2.x, lp2.y)
                });
            }
        }
    }

    // Balanced non-coherent translation
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

        float R = ApertureRadiusMeters;
        float r0 = Mathf.Clamp(centralExclusionRadiusMeters, 0f, R * 0.999f);

        int n = dots.Count;
        for (int k = 0; k < n; k++)
        {
            var t = dots[k];
            Vector2 delta = dirs[k % dirs.Length] * stepMeters;

            Vector3 lp = ToLocalPlane(t.position);
            lp.x += delta.x;
            lp.y += delta.y;

            // outer boundary reflect
            Vector2 v = new Vector2(lp.x, lp.y);
            if (v.magnitude > R)
            {
                Vector2 nn = v.normalized;
                v -= 2f * nn * (v.magnitude - R);
                v *= 0.999f;
                lp.x = v.x;
                lp.y = v.y;
            }

            t.position = FromLocalPlane(lp);

            // inner boundary keep-out
            EnforceCentralExclusion(t, r0);

            if (frame >= 0)
            {
                Vector3 lp2 = ToLocalPlane(t.position);
                trajectoryLog.Add(new TrajectorySample
                {
                    frame = frame,
                    subfieldIndex = subfieldIndex,
                    localPos = new Vector2(lp2.x, lp2.y)
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
    static Vector2 UniformDisk(System.Random rng, float R)
    {
        float u = (float)rng.NextDouble();
        float r = R * Mathf.Sqrt(u);
        float th = (float)rng.NextDouble() * (2f * Mathf.PI);
        return new Vector2(r * Mathf.Cos(th), r * Mathf.Sin(th));
    }

    static Vector2 UniformAnnulus(System.Random rng, float rInner, float rOuter)
    {
        float u = (float)rng.NextDouble();
        float th = (float)rng.NextDouble() * (2f * Mathf.PI);
        float r = Mathf.Sqrt(u * (rOuter * rOuter - rInner * rInner) + rInner * rInner);
        return new Vector2(r * Mathf.Cos(th), r * Mathf.Sin(th));
    }

    // Push dot out of the central exclusion zone, if enabled.
    void EnforceCentralExclusion(Transform t, float rInner)
    {
        if (t == null) return;
        if (rInner <= 0f) return;

        Vector3 lp = ToLocalPlane(t.position);
        Vector2 v = new Vector2(lp.x, lp.y);
        float r = v.magnitude;

        if (r >= rInner) return;

        // If exactly at center, pick a deterministic direction.
        Vector2 dir = (r > 1e-9f) ? (v / r) : Vector2.right;

        float target = rInner * Mathf.Max(1.0001f, exclusionPushMargin);
        Vector2 pushed = dir * target;

        lp.x = pushed.x;
        lp.y = pushed.y;
        t.position = FromLocalPlane(lp);
    }

    // Converts a visual angle in degrees to lateral offset (meters) at distance.
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
            m.SetFloat("_Surface", 0f);

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
               + transform.up * localPlane.y;
    }

    void WrapIntoDisk(Transform t, float R)
    {
        Vector3 lp = ToLocalPlane(t.position);
        Vector2 v = new Vector2(lp.x, lp.y);

        if (v.magnitude > R)
        {
            Vector2 n = v.normalized;
            v -= 2f * n * (v.magnitude - R);
            v *= 0.999f;
            lp.x = v.x;
            lp.y = v.y;
            t.position = FromLocalPlane(lp);
        }
    }

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