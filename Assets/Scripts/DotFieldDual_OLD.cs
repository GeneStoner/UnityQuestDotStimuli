using UnityEngine;
using UnityEngine.Events;
using Stim; // uses the pure core (DotFieldCore)

[DisallowMultipleComponent]
public class DotFieldDual_OLD : MonoBehaviour
{
    // -------- Minimal state/compatibility (used by HUD/Runner) --------
    public enum Phase { IdlePrepared, Playing, Response }
    [SerializeField] Phase _phase = Phase.IdlePrepared;
    public bool TrialRunning => _phase == Phase.Playing;

    public string GetStimulusTag()
    {
        string delayed = delayFieldB ? "B" : "A";
        string pulse   = translationHitsDelayed ? delayed : (delayed == "A" ? "B" : "A");
        return $"dir:{translationDirectionDeg:000}° | delay:{delayed} {onsetDelayB:0.00}s | pulse:{pulse} | dur:{translationDurationSec:0.###}s";
    }

    // ---- Legacy fields some scripts read for logging (values are placeholders) ----
    [Header("Legacy / Trial info (read-only for now)")]
    public float translationDirectionDeg = 0f;
    public float translationStartSec = 0.60f;
    public float translationDurationSec = 0.10f;
    public float translationSpeedDegPerSec = 8f;
    public bool  delayFieldB = true;
    public float onsetDelayB = 0.5f;
    public bool  translationHitsDelayed = true;
    public int   rotationDirA = +1;
    public int   rotationDirB = -1;
    public int   confirmedSelectionDeg = -1;

    // ---- Legacy shims to satisfy existing callers (Runner/HUD) ----
    [Header("Legacy shims (for existing scripts)")]
    public bool randomizeEachTrial = false; // not used here, but present so callers compile

    // UnityEvents exist so old Inspector hooks don’t explode (no-ops here)
    public UnityEvent OnTrialStarted;
    public UnityEvent OnTrialEnded;
    public UnityEvent OnResponse;
    public UnityEvent OnNullTrial;

    // ---------------- Viewing & dots (actual stimulus knobs) ----------------
    [Header("Viewing geometry")]
    public float viewDistanceMeters = 2.0f;
    public float apertureDeg = 12f;

    [Header("Population")]
    public int dotCountA = 250;
    public int dotCountB = 250;
    public int randomSeed = 12345;

    [Header("Appearance")]
    public float dotSizeDeg = 0.12f;
    public bool  faceCamera = true;
    public Material dotMaterial;     // fallback for both
    public Material dotMaterialA;    // optional override A
    public Material dotMaterialB;    // optional override B
    public bool usePerFieldColors = true;
    public Color fieldAColor = Color.red;
    public Color fieldBColor = Color.green;
    public int   renderLayer = 0;

    // ---------------- Internal: core + rendering caches ----------------
    DotFieldCore _core = new DotFieldCore();
    Mesh _quad;
    Matrix4x4[] _matsA, _matsB;
    MaterialPropertyBlock _mpbA, _mpbB;
    static readonly int _ColorID     = Shader.PropertyToID("_Color");
    static readonly int _BaseColorID = Shader.PropertyToID("_BaseColor");
    const int MAX_BATCH = 1023;

    // ---------------- Unity lifecycle ----------------
    void Awake()      { EnsureSetup(); RebuildLayout(); }
    void OnValidate() { EnsureSetup(); RebuildLayout(); }
    void Reset()      { EnsureSetup(); RebuildLayout(); }

    void Update()
    {
        // Build TRS matrices from core positions
        BuildMatrices();

        // Choose materials and apply colors if needed
        var (matA, matB) = EnsureMaterials();
        if (usePerFieldColors) { ApplyColorToMPB(_mpbA, fieldAColor); ApplyColorToMPB(_mpbB, fieldBColor); }
        else { _mpbA = _mpbB = null; }

        // Draw
        if (matA != null && _matsA != null) DrawBatched(matA, _matsA, _matsA.Length, _mpbA);
        if (matB != null && _matsB != null) DrawBatched(matB, _matsB, _matsB.Length, _mpbB);
    }

    // ---------------- Public hooks (keep old Runner happy) ----------------
    public void PrepareNextTrial()
    {
        // For now this simply regenerates layouts. No timing/phase logic here.
        RebuildLayout();
        _phase = Phase.IdlePrepared;
    }

    // Overload to satisfy calls like PrepareNextTrial(randomize: randomizeEachTrial)
    public void PrepareNextTrial(bool randomize) => PrepareNextTrial();

    // ---------------- Private helpers ----------------
    void RebuildLayout()
    {
        _core.Configure(apertureDeg, viewDistanceMeters, dotCountA, dotCountB, randomSeed, translationSpeedDegPerSec);
        _core.GeneratePositions();
        _matsA = new Matrix4x4[_core.PosA.Length];
        _matsB = new Matrix4x4[_core.PosB.Length];
    }

    void BuildMatrices()
    {
        Quaternion rot = transform.rotation;
        if (faceCamera && Camera.main)
            rot = Quaternion.LookRotation(Camera.main.transform.forward, Vector3.up);

        Vector3 scale = Vector3.one * DotFieldCore.DegToMeters(dotSizeDeg, viewDistanceMeters);

        for (int i = 0; i < _core.PosA.Length; i++)
        {
            Vector3 wp = transform.position
                       + transform.right * _core.PosA[i].x
                       + transform.up    * _core.PosA[i].y;
            _matsA[i] = Matrix4x4.TRS(wp, rot, scale);
        }
        for (int i = 0; i < _core.PosB.Length; i++)
        {
            Vector3 wp = transform.position
                       + transform.right * _core.PosB[i].x
                       + transform.up    * _core.PosB[i].y;
            _matsB[i] = Matrix4x4.TRS(wp, rot, scale);
        }
    }

    (Material, Material) EnsureMaterials()
    {
        if (dotMaterialA == null && dotMaterialB == null && dotMaterial == null)
        {
            var sh = Shader.Find("Sprites/Default");
            if (sh == null) sh = Shader.Find("Universal Render Pipeline/Unlit");
            if (sh != null)
            {
                dotMaterial = new Material(sh) { name = "AutoDotMaterial", enableInstancing = true };
            }
        }
        var matA = dotMaterialA != null ? dotMaterialA : dotMaterial;
        var matB = dotMaterialB != null ? dotMaterialB : dotMaterial;
        if (matA != null) matA.enableInstancing = true;
        if (matB != null) matB.enableInstancing = true;
        return (matA, matB);
    }

    void DrawBatched(Material mat, Matrix4x4[] mats, int count, MaterialPropertyBlock mpb)
    {
        if (mat == null || mats == null || count <= 0) return;
        int drawn = 0;
        Mesh quad = GetQuad();
        while (drawn < count)
        {
            int batch = Mathf.Min(MAX_BATCH, count - drawn);
            Graphics.DrawMeshInstanced(quad, 0, mat, mats, batch, mpb,
                UnityEngine.Rendering.ShadowCastingMode.Off, false, renderLayer);
            drawn += batch;
        }
    }

    void EnsureSetup()
    {
        if (_quad == null) _quad = BuildUnitQuad();
        if (_mpbA == null) _mpbA = new MaterialPropertyBlock();
        if (_mpbB == null) _mpbB = new MaterialPropertyBlock();
        ApplyColorToMPB(_mpbA, fieldAColor);
        ApplyColorToMPB(_mpbB, fieldBColor);
    }

    Mesh GetQuad() => _quad != null ? _quad : (_quad = BuildUnitQuad());

    Mesh BuildUnitQuad()
    {
        var mesh = new Mesh { name = "UnitQuad(+Z)" };
        mesh.vertices = new Vector3[]
        {
            new Vector3(-0.5f, -0.5f, 0f),
            new Vector3( 0.5f, -0.5f, 0f),
            new Vector3( 0.5f,  0.5f, 0f),
            new Vector3(-0.5f,  0.5f, 0f),
        };
        mesh.uv = new Vector2[] { new(0,0), new(1,0), new(1,1), new(0,1) };
        mesh.triangles = new int[] { 0,1,2, 0,2,3 };
        mesh.RecalculateNormals();
        return mesh;
    }

    void ApplyColorToMPB(MaterialPropertyBlock mpb, Color c)
    {
        if (mpb == null) return;
        mpb.SetColor(_BaseColorID, c); // URP/HDRP
        mpb.SetColor(_ColorID,     c); // Built-in
    }
}