// FILE: SmoothFixationTarget.cs
// Shader-based fixation target with smooth anti-aliased circles
using UnityEngine;

[ExecuteInEditMode]
public class SmoothFixationTarget : MonoBehaviour
{
    [Header("Geometry Source")]
    [Tooltip("If assigned, pulls geometry from ExperimentSpec. Otherwise uses manual values below.")]
    public ExperimentSpec spec;

    [Header("Manual Geometry (used if spec is null)")]
    public float viewDistance_m = 2.0f;
    public float outerDiameter_deg = 0.6f;
    public float innerDiameter_deg = 0.24f;
    public float crosshairThickness_deg = 0.06f;
    public float centerDotDiameter_deg = 0.15f;

    [Header("Appearance")]
    public Color ringColor = Color.white;
    public Color centerColor = Color.black;
    public Color crosshairColor = Color.black;

    [Header("Options")]
    [Tooltip("Show central dot (covers crosshair intersection)")]
    public bool showCenterDot = true;

    [Tooltip("Show crosshairs")]
    public bool showCrosshairs = true;

    [Header("Preview Scale (for monitor testing)")]
    [Min(0.1f)]
    public float previewScale = 1f;

    [Header("Z Offsets (smaller = closer to camera)")]
    public float zRing = 0f;
    public float zCrosshair = -0.0005f;
    public float zCenterDot = -0.001f;

    [Header("Anti-aliasing")]
    [Range(0.005f, 0.1f)]
    public float edgeSmoothness = 0.03f;

    [Header("Debug")]
    public bool logSizes = false;

    // Runtime objects
    private GameObject _outerRingQuad;
    private GameObject _hCrosshair;
    private GameObject _vCrosshair;
    private GameObject _centerDotQuad;

    private Material _ringMaterial;
    private Material _centerMaterial;
    private Material _crosshairMaterialH;
    private Material _crosshairMaterialV;

    private static readonly int ColorId = Shader.PropertyToID("_Color");
    private static readonly int InnerRadiusId = Shader.PropertyToID("_InnerRadius");
    private static readonly int OuterRadiusId = Shader.PropertyToID("_OuterRadius");
    private static readonly int SmoothnessId = Shader.PropertyToID("_Smoothness");

    void OnEnable()
    {
        CreateFixation();
    }

    void OnDisable()
    {
        DestroyFixation();
    }

    void OnValidate()
    {
        if (isActiveAndEnabled)
        {
            #if UNITY_EDITOR
            UnityEditor.EditorApplication.delayCall += () =>
            {
                if (this != null && isActiveAndEnabled)
                    UpdateFixation();
            };
            #else
            UpdateFixation();
            #endif
        }
    }

    public void Refresh()
    {
        UpdateFixation();
    }

    public void SetPreviewScale(float scale)
    {
        previewScale = Mathf.Max(0.1f, scale);
        UpdateFixation();
    }

    void CreateFixation()
    {
        Shader circleShader = Shader.Find("Custom/SmoothCircle");
        Shader unlitShader = Shader.Find("Universal Render Pipeline/Unlit");

        if (unlitShader == null)
            unlitShader = Shader.Find("Unlit/Color");

        if (circleShader == null)
        {
            Debug.LogError("[SmoothFixationTarget] Could not find Custom/SmoothCircle shader! Make sure SmoothCircle.shader is in Assets/Shaders/");
            return;
        }

        // Circle shader for ring and center dot
        _ringMaterial = new Material(circleShader);
        _ringMaterial.name = "RingMat";

        _centerMaterial = new Material(circleShader);
        _centerMaterial.name = "CenterMat";

        // Simple unlit for crosshairs (rectangles, not circles)
        _crosshairMaterialH = new Material(unlitShader);
        _crosshairMaterialH.name = "CrosshairH";

        _crosshairMaterialV = new Material(unlitShader);
        _crosshairMaterialV.name = "CrosshairV";

        // Create quads
        _outerRingQuad = CreateQuad("OuterRing", _ringMaterial);
        _hCrosshair = CreateQuad("HCrosshair", _crosshairMaterialH);
        _vCrosshair = CreateQuad("VCrosshair", _crosshairMaterialV);
        _centerDotQuad = CreateQuad("CenterDot", _centerMaterial);

        UpdateFixation();
    }

    void DestroyFixation()
    {
        SafeDestroy(_outerRingQuad);
        SafeDestroy(_hCrosshair);
        SafeDestroy(_vCrosshair);
        SafeDestroy(_centerDotQuad);

        SafeDestroy(_ringMaterial);
        SafeDestroy(_centerMaterial);
        SafeDestroy(_crosshairMaterialH);
        SafeDestroy(_crosshairMaterialV);
    }

    void SafeDestroy(Object obj)
    {
        if (obj == null) return;
        if (Application.isPlaying)
            Destroy(obj);
        else
            DestroyImmediate(obj);
    }

    GameObject CreateQuad(string name, Material mat)
    {
        var go = GameObject.CreatePrimitive(PrimitiveType.Quad);
        go.name = name;
        go.transform.SetParent(transform, false);

        // Remove collider
        var col = go.GetComponent<Collider>();
        if (col != null) SafeDestroy(col);

        var renderer = go.GetComponent<MeshRenderer>();
        renderer.sharedMaterial = mat;
        renderer.shadowCastingMode = UnityEngine.Rendering.ShadowCastingMode.Off;
        renderer.receiveShadows = false;

        return go;
    }

    void UpdateFixation()
    {
        if (_outerRingQuad == null || _ringMaterial == null) return;

        // Get geometry values
        float viewDist, outerDiam_deg, innerDiam_deg, crossThk_deg, centerDiam_deg;

        if (spec != null)
        {
            viewDist = spec.viewDistance_m;
            // Outer diameter = inner radius * 2 + thickness * 2
            innerDiam_deg = spec.fixationRingInnerRadius_deg * 2f;
            outerDiam_deg = innerDiam_deg + spec.fixationRingThickness_deg * 2f;
            crossThk_deg = spec.fixationCrosshairThickness_deg;
            centerDiam_deg = spec.fixationDotRadius_deg * 2f;

            if (logSizes)
            {
                Debug.Log($"[SmoothFixation] From spec: outer={outerDiam_deg:F3}° inner={innerDiam_deg:F3}° cross={crossThk_deg:F3}° center={centerDiam_deg:F3}°");
            }
        }
        else
        {
            viewDist = viewDistance_m;
            outerDiam_deg = outerDiameter_deg;
            innerDiam_deg = innerDiameter_deg;
            crossThk_deg = crosshairThickness_deg;
            centerDiam_deg = centerDotDiameter_deg;
        }

        // Convert degrees to meters: size_m = 2 * viewDist * tan(deg/2)
        // For small angles: size_m ≈ viewDist * deg * (π/180)
        float mPerDeg = viewDist * Mathf.Deg2Rad; // simplified for small angles
        float scale = Mathf.Max(0.1f, previewScale);

        float outerDiam_m = outerDiam_deg * mPerDeg * scale;
        float innerDiam_m = innerDiam_deg * mPerDeg * scale;
        float crossThk_m = crossThk_deg * mPerDeg * scale;
        float centerDiam_m = centerDiam_deg * mPerDeg * scale;

        if (logSizes)
        {
            Debug.Log($"[SmoothFixation] Meters: outer={outerDiam_m*1000:F2}mm inner={innerDiam_m*1000:F2}mm cross={crossThk_m*1000:F2}mm center={centerDiam_m*1000:F2}mm");
        }

        // --- Outer Ring (white ring with transparent hole) ---
        _outerRingQuad.transform.localPosition = new Vector3(0, 0, zRing);
        _outerRingQuad.transform.localScale = new Vector3(outerDiam_m, outerDiam_m, 1f);
        _outerRingQuad.transform.localRotation = Quaternion.identity;
        _outerRingQuad.SetActive(true);

        float innerFraction = innerDiam_m / outerDiam_m * 0.5f; // as radius fraction (0-0.5)
        _ringMaterial.SetColor(ColorId, ringColor);
        _ringMaterial.SetFloat(InnerRadiusId, innerFraction);
        _ringMaterial.SetFloat(OuterRadiusId, 0.5f);
        _ringMaterial.SetFloat(SmoothnessId, edgeSmoothness);

        // --- Crosshairs (simple colored quads) ---
        _hCrosshair.SetActive(showCrosshairs);
        _vCrosshair.SetActive(showCrosshairs);

        if (showCrosshairs)
        {
            // Horizontal: spans full width, thin height
            _hCrosshair.transform.localPosition = new Vector3(0, 0, zCrosshair);
            _hCrosshair.transform.localScale = new Vector3(outerDiam_m, crossThk_m, 1f);
            _hCrosshair.transform.localRotation = Quaternion.identity;

            // Vertical: thin width, spans full height
            _vCrosshair.transform.localPosition = new Vector3(0, 0, zCrosshair);
            _vCrosshair.transform.localScale = new Vector3(crossThk_m, outerDiam_m, 1f);
            _vCrosshair.transform.localRotation = Quaternion.identity;

            // Set crosshair colors (URP Unlit uses _BaseColor)
            if (_crosshairMaterialH.HasProperty("_BaseColor"))
            {
                _crosshairMaterialH.SetColor("_BaseColor", crosshairColor);
                _crosshairMaterialV.SetColor("_BaseColor", crosshairColor);
            }
            else
            {
                _crosshairMaterialH.SetColor("_Color", crosshairColor);
                _crosshairMaterialV.SetColor("_Color", crosshairColor);
            }
        }

        // --- Center Dot (filled circle, covers crosshair intersection) ---
        _centerDotQuad.SetActive(showCenterDot);

        if (showCenterDot)
        {
            _centerDotQuad.transform.localPosition = new Vector3(0, 0, zCenterDot);
            _centerDotQuad.transform.localScale = new Vector3(centerDiam_m, centerDiam_m, 1f);
            _centerDotQuad.transform.localRotation = Quaternion.identity;

            // Filled circle: inner radius = 0
            _centerMaterial.SetColor(ColorId, centerColor);
            _centerMaterial.SetFloat(InnerRadiusId, 0f);
            _centerMaterial.SetFloat(OuterRadiusId, 0.5f);
            _centerMaterial.SetFloat(SmoothnessId, edgeSmoothness);
        }
    }
}
