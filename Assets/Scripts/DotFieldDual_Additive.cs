using UnityEngine;

/// DotFieldDual_Additive
/// ----------------------
/// Minimal renderer for TWO superimposed dot fields using ADDITIVE blending.
/// - No trial state machine, no responses, no timing—just positions + draw
/// - Auto-creates additive materials if none are assigned
/// - Renders both fields with GPU instancing (fast) and shows in Edit mode
///
/// Add this to an empty GameObject located at your stimulus plane. Use
/// transform.right / transform.up as the stimulus axes (x,y).
[DisallowMultipleComponent]
[ExecuteAlways]
public class DotFieldDual_Additive : MonoBehaviour
{
    [Header("Viewing geometry (visual degrees)")]
    [Tooltip("Distance from eye to stimulus plane (meters).")]
    public float viewDistanceMeters = 2.0f;

    [Tooltip("Circular aperture DIAMETER in visual degrees.")]
    public float apertureDeg = 12f;

    [Header("Dots / counts")]
    [Tooltip("Number of dots in Field A")]
    public int dotCountA = 250;

    [Tooltip("Number of dots in Field B")]
    public int dotCountB = 250;

    [Header("Appearance")]
    [Tooltip("Dot size (DIAMETER) in visual degrees (screen-space size scales with distance).")]
    public float dotSizeDeg = 0.12f;

    [Tooltip("Billboard quads to face the main camera.")]
    public bool faceCamera = true;

    [Header("Materials & Colors (Additive)")]
    [Tooltip("If left empty, additive materials are auto-created.")]
    public Material dotMaterial;     // fallback for both (must be additive)
    public Material dotMaterialA;    // optional override (must be additive)
    public Material dotMaterialB;    // optional override (must be additive)

    public bool usePerFieldColors = true;
    public Color fieldAColor = Color.red;
    public Color fieldBColor = Color.green;

    [Header("Rendering")]
    [Tooltip("Unity layer index to draw on (0 = Default).")]
    public int renderLayer = 0;

    [Header("Reproducibility")]
    [Tooltip("Seed for reproducible layouts. Change to re-sample.")]
    public int randomSeed = 12345;

    [Header("Preview")]
    [Tooltip("Draw a faint aperture ring in the Scene view.")]
    public bool drawApertureRing = true;
    public float gizmoDotSize = 0.01f;

    // ---------- internal ----------
    const int MAX_BATCH = 1023;

    Vector2[] _posA, _posB;           // positions (meters, local plane coords)
    Matrix4x4[] _matsA, _matsB;       // per-instance transforms
    Mesh _quad;                       // unit quad mesh
    float _R;                         // aperture radius (meters)
    float _dotSizeM;                  // dot diameter (meters)

    MaterialPropertyBlock _mpbA, _mpbB;
    static readonly int _ColorID     = Shader.PropertyToID("_Color");      // Built-in
    static readonly int _BaseColorID = Shader.PropertyToID("_BaseColor");  // URP/HDRP

    // ---------- Unity ----------
    void OnEnable()
    {
        EnsureSetup();
        RegeneratePositions();
    }

    void OnValidate()
    {
        EnsureSetup();
        RegeneratePositions();
    }

    void Reset()
    {
        EnsureSetup();
        RegeneratePositions();
    }

    void Update()
    {
        if (_posA == null || _posB == null) return;

        // Build transforms for this frame (static; no motion yet)
        BuildMatrices();

        // Pick or create additive materials
        var (matA, matB) = EnsureAdditiveMaterials();

        // Push colors (if requested)
        if (usePerFieldColors)
        {
            ApplyColorToMPB(ref _mpbA, fieldAColor);
            ApplyColorToMPB(ref _mpbB, fieldBColor);
        }
        else
        {
            _mpbA = _mpbB = null;
        }

        // Draw both fields
        if (matA != null && _matsA != null) DrawBatched(matA, _matsA, _matsA.Length, _mpbA);
        if (matB != null && _matsB != null) DrawBatched(matB, _matsB, _matsB.Length, _mpbB);
    }

    void OnDrawGizmosSelected()
    {
        if (!drawApertureRing) return;
        EnsureSetup();

        // Preview dots as tiny spheres (editor visualization only)
        Gizmos.color = new Color(1,1,1,0.25f);
        if (_posA != null)
        {
            Gizmos.color = new Color(fieldAColor.r, fieldAColor.g, fieldAColor.b, 0.6f);
            foreach (var p in _posA)
            {
                var wp = transform.position + transform.right * p.x + transform.up * p.y;
                Gizmos.DrawSphere(wp, gizmoDotSize);
            }
        }
        if (_posB != null)
        {
            Gizmos.color = new Color(fieldBColor.r, fieldBColor.g, fieldBColor.b, 0.6f);
            foreach (var p in _posB)
            {
                var wp = transform.position + transform.right * p.x + transform.up * p.y;
                Gizmos.DrawSphere(wp, gizmoDotSize);
            }
        }

        // Aperture ring
        Gizmos.color = new Color(1,1,1,0.4f);
        const int steps = 64;
        Vector3 prev = transform.position + transform.right * _R;
        for (int i = 1; i <= steps; i++)
        {
            float t = (i / (float)steps) * Mathf.PI * 2f;
            Vector3 curr = transform.position
                + transform.right * (Mathf.Cos(t) * _R)
                + transform.up    * (Mathf.Sin(t) * _R);
            Gizmos.DrawLine(prev, curr);
            prev = curr;
        }
    }

    // ---------- core: positions ----------
    void RegeneratePositions()
    {
        _R        = Mathf.Max(1e-5f, DegToMeters(apertureDeg) * 0.5f);
        _dotSizeM = Mathf.Max(1e-5f, DegToMeters(dotSizeDeg));

        int nA = Mathf.Max(1, dotCountA);
        int nB = Mathf.Max(1, dotCountB);
        _posA = new Vector2[nA];
        _posB = new Vector2[nB];

        var rngA = new System.Random(randomSeed);
        var rngB = new System.Random(randomSeed + 99991);

        for (int i = 0; i < nA; i++) _posA[i] = UniformDisk(rngA, _R);
        for (int i = 0; i < nB; i++) _posB[i] = UniformDisk(rngB, _R);

        _matsA = new Matrix4x4[nA];
        _matsB = new Matrix4x4[nB];
    }

    static Vector2 UniformDisk(System.Random rng, float R)
    {
        // area-uniform: r ~ R*sqrt(U), theta ~ U(0,2π)
        float u  = (float)rng.NextDouble();
        float r  = R * Mathf.Sqrt(u);
        float th = (float)rng.NextDouble() * (2f * Mathf.PI);
        return new Vector2(r * Mathf.Cos(th), r * Mathf.Sin(th));
    }

    // ---------- core: matrices & draw ----------
    void BuildMatrices()
    {
        Quaternion rot = transform.rotation;
        if (faceCamera && Camera.main)
            rot = Quaternion.LookRotation(Camera.main.transform.forward, Vector3.up);

        Vector3 scale = Vector3.one * _dotSizeM;

        for (int i = 0; i < _posA.Length; i++)
        {
            Vector3 wp = transform.position
                       + transform.right * _posA[i].x
                       + transform.up    * _posA[i].y;
            _matsA[i] = Matrix4x4.TRS(wp, rot, scale);
        }
        for (int i = 0; i < _posB.Length; i++)
        {
            Vector3 wp = transform.position
                       + transform.right * _posB[i].x
                       + transform.up    * _posB[i].y;
            _matsB[i] = Matrix4x4.TRS(wp, rot, scale);
        }
    }

    void DrawBatched(Material mat, Matrix4x4[] mats, int count, MaterialPropertyBlock mpb)
    {
        if (mat == null || mats == null || count <= 0) return;

        int drawn = 0;
        while (drawn < count)
        {
            int batch = Mathf.Min(MAX_BATCH, count - drawn);
            Graphics.DrawMeshInstanced(
                GetQuad(), 0, mat,
                mats, batch, mpb,
                UnityEngine.Rendering.ShadowCastingMode.Off,
                false, renderLayer
            );
            drawn += batch;
        }
    }

    // ---------- materials ----------
    (Material, Material) EnsureAdditiveMaterials()
    {
        // Use overrides if present; otherwise fallback to shared dotMaterial
        var matA = dotMaterialA != null ? dotMaterialA : dotMaterial;
        var matB = dotMaterialB != null ? dotMaterialB : dotMaterial;

        // If still null, auto-create additive materials
        if (matA == null || matB == null)
        {
            // Try common additive shaders across pipelines
            Shader add =
                Shader.Find("Particles/Standard Unlit") ??
                Shader.Find("Particles/Unlit") ??
                Shader.Find("Universal Render Pipeline/Particles/Unlit") ??
                Shader.Find("Legacy Shaders/Particles/Additive");

            if (add == null)
            {
                // Fallback to Sprites/Default (NOT additive), warn user
                Debug.LogWarning("[DotFieldDual_Additive] Could not find an additive shader. " +
                                 "Falling back to Sprites/Default (non-additive). Assign an additive material.");
                add = Shader.Find("Sprites/Default");
            }

            if (matA == null)
            {
                matA = new Material(add) { name = "AutoDotMatA_Additive" };
            }
            if (matB == null)
            {
                matB = new Material(add) { name = "AutoDotMatB_Additive" };
            }

            dotMaterialA = matA;
            dotMaterialB = matB;
        }

        if (!matA.enableInstancing) matA.enableInstancing = true;
        if (!matB.enableInstancing) matB.enableInstancing = true;

        return (matA, matB);
    }

    // ---------- utilities ----------
    void EnsureSetup()
    {
        if (_quad == null) _quad = BuildUnitQuad();
        if (_mpbA == null) _mpbA = new MaterialPropertyBlock();
        if (_mpbB == null) _mpbB = new MaterialPropertyBlock();
        ApplyColorToMPB(ref _mpbA, fieldAColor);
        ApplyColorToMPB(ref _mpbB, fieldBColor);
    }

    Mesh GetQuad() => _quad != null ? _quad : (_quad = BuildUnitQuad());

    static Mesh BuildUnitQuad()
    {
        var mesh = new Mesh { name = "UnitQuad(+Z)" };
        mesh.vertices = new Vector3[] {
            new Vector3(-0.5f, -0.5f, 0f),
            new Vector3( 0.5f, -0.5f, 0f),
            new Vector3( 0.5f,  0.5f, 0f),
            new Vector3(-0.5f,  0.5f, 0f),
        };
        mesh.uv = new Vector2[] {
            new Vector2(0f,0f), new Vector2(1f,0f),
            new Vector2(1f,1f), new Vector2(0f,1f)
        };
        mesh.triangles = new int[] { 0,1,2, 0,2,3 };
        mesh.RecalculateNormals();
        return mesh;
    }

    float DegToMeters(float deg)
    {
        // diameter in meters for a given visual angle at viewDistanceMeters
        return 2f * viewDistanceMeters * Mathf.Tan(0.5f * Mathf.Deg2Rad * Mathf.Max(0f, deg));
    }

    static void ApplyColorToMPB(ref MaterialPropertyBlock mpb, Color c)
    {
        if (mpb == null) mpb = new MaterialPropertyBlock();
        // Set both to cover Built-in and URP/HDRP
        mpb.SetColor(_BaseColorID, c);
        mpb.SetColor(_ColorID,     c);
    }
}