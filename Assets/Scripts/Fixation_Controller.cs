// FILE: Fixation_Controller.cs
using UnityEngine;

[DisallowMultipleComponent]
public class Fixation_Controller : MonoBehaviour
{
    [Header("Source of truth")]
    public ExperimentSpec spec;

    [Header("Monitor Preview (render-only)")]
    [Min(0.1f)] public float previewScale = 1f;

    [Header("Rendering Mode")]
    [Tooltip("Use shader-based quads for smooth anti-aliased circles (recommended). If false, uses assigned cylinder GameObjects.")]
    public bool useShaderCircles = true;

    [Header("Shader Circle Settings (when useShaderCircles=true)")]
    [Range(0.005f, 0.1f)]
    public float edgeSmoothness = 0.03f;

    [Header("Assign fixation parts (when useShaderCircles=false)")]
    public GameObject fixDot;      // optional
    public GameObject ringOuter;   // Cylinder (disk)
    public GameObject ringInner;   // Cylinder (disk)
    public GameObject hArm;        // Cube
    public GameObject vArm;        // Cube

    // Shader-created objects (when useShaderCircles=true)
    private GameObject _shaderRingQuad;
    private GameObject _shaderCenterQuad;
    private GameObject _shaderHCross;
    private GameObject _shaderVCross;
    private Material _ringMaterial;
    private Material _centerMaterial;
    private Material _crossMaterialH;
    private Material _crossMaterialV;

    // Nonius line objects (binocular — both eyes see both lines)
    // Note: true dichoptic rendering is not achievable via Unity APIs with the
    // Oculus XR Plugin on Android (stereoTargetEye, unity_StereoEyeIndex, and
    // beginCameraRendering stereoActiveEye are all ignored/unavailable). Lines
    // serve as a binocular fixation reference rather than a vergence error indicator.
    private GameObject _noniusLeft;
    private GameObject _noniusRight;
    private Material _noniusMaterialL;
    private Material _noniusMaterialR;

    private static readonly int ShaderColorId = Shader.PropertyToID("_Color");
    private static readonly int InnerRadiusId = Shader.PropertyToID("_InnerRadius");
    private static readonly int OuterRadiusId = Shader.PropertyToID("_OuterRadius");
    private static readonly int SmoothnessId  = Shader.PropertyToID("_Smoothness");

    [Header("Visibility (script overrides while playing)")]
    public bool showDot = false;
    public bool showRings = true;
    public bool showCross = true;

    [Header("Nonius Lines (dichoptic vergence aid)")]
    [Tooltip("Show dichoptic nonius lines: left eye sees line above fixation, right eye below. " +
             "Horizontal misalignment indicates vergence error. Requires Custom/NoniusLine shader.")]
    public bool showNoniusLines = false;

    [Tooltip("Length of each nonius line in degrees.")]
    [Min(0.05f)] public float noniusLength_deg = 0.40f;

    [Tooltip("Stroke width of each nonius line in degrees.")]
    [Min(0.01f)] public float noniusWidth_deg = 0.06f;

    [Tooltip("Distance from fixation center to the near edge of each nonius line (degrees). " +
             "Should be just outside the bullseye outer ring to avoid overlap.")]
    [Min(0.05f)] public float noniusGap_deg = 0.60f;

    [Tooltip("Color of the nonius lines.")]
    public Color noniusColor = Color.white;

    [Header("Depth ordering (meters, perspective-friendly)")]
    [Tooltip("Use small separations (mm). More negative Z may be closer in your setup—use values that work for you.")]
    public float zOuterRing = -0.0024f; // back
    public float zCross     = -0.0020f; // middle
    public float zInnerRing = -0.0016f; // front
    public float zDot       = -0.0012f; // front-most (optional)

    [Header("Disk / Cross thickness in Z (meters)")]
    [Tooltip("Cylinder height (disk thickness) along its axis.")]
    public float ringDiskThickness_m = 0.0010f;

    [Tooltip("Crosshair cubes must be thin in Z to avoid occluding other parts.")]
    public float crossZThickness_m   = 0.0002f;

    [Header("Cylinder disk normal direction")]
    [Tooltip("If true, disks face +Z (normal +Z). If false, face -Z.")]
    public bool diskNormalIsPlusZ = true;

    [Header("Bullseye diameters (degrees)")]
    [Tooltip("Inner circle DIAMETER in degrees.")]
    public float innerDiam_deg = 0.40f;

    [Tooltip("Outer circle DIAMETER in degrees.")]
    public float outerDiam_deg = 1.00f;

    [Header("Crosshair geometry (decoupled from inner circle)")]
    [Tooltip("Crosshair stroke thickness in degrees (independent knob).")]
    public float crossThickness_deg = 0.12f;

    [Tooltip("Cross half-length scale relative to outer radius. 1.00 reaches edge; 1.02 slightly overshoots to hide ring tips.")]
    public float crossHalfLenScale = 1.00f;

    [Header("Optional consistency check")]
    [Tooltip("If >0, warn if inner circle is too small to cover cross intersection by this fractional slack.")]
    [Min(0f)] public float innerCoversCrossClearanceFrac = 0.10f;

    [Header("Colors")]
    public bool driveColorFromSpec = true;
    public Color overrideFixColor = Color.white;
    public Color holeColor = Color.black;
    public Color crossColor = Color.black;

    [Header("Optional materials (URP/Unlit, Opaque recommended)")]
    public Material ringOuterMaterial;
    public Material ringInnerMaterial;
    public Material crossMaterial;
    public Material dotMaterial; // optional

    [Header("Diagnostics")]
    public bool logOnApply = false;

    private static readonly int BaseColorId = Shader.PropertyToID("_BaseColor");
    private static readonly int ColorId     = Shader.PropertyToID("_Color");
    private MaterialPropertyBlock _mpb;

    void OnEnable()
    {
        if (useShaderCircles)
            CreateShaderObjects();
        Apply("OnEnable");
    }

    void OnDisable()
    {
        DestroyShaderObjects();
    }

    void Start() { Apply("Start"); }

    void OnValidate()
    {
        if (isActiveAndEnabled)
        {
            if (useShaderCircles)
                ApplyShaderCircles();
            else
                ApplySizesAndColorsOnly();
        }
    }

    // Call this from TrialBlockRunner
    public void SetPreviewScaleAndApply(float newScale, string callerTag = "External")
    {
        previewScale = Mathf.Max(0.1f, newScale);
        Apply(callerTag);
    }

    public void Apply(string tag = "Apply")
    {
        if (spec == null)
        {
            Debug.LogWarning($"[Fixation {GetInstanceID()}] ({tag}) No ExperimentSpec assigned.", this);
            return;
        }

        if (useShaderCircles)
        {
            // Shader-based path: use quads with SmoothCircle shader
            if (_shaderRingQuad == null)
                CreateShaderObjects();

            ApplyShaderCircles();
        }
        else
        {
            // Legacy cylinder-based path
            if (Application.isPlaying)
            {
                if (ringOuter) ringOuter.SetActive(showRings);
                if (ringInner) ringInner.SetActive(showRings);
                if (hArm)      hArm.SetActive(showCross);
                if (vArm)      vArm.SetActive(showCross);
                if (fixDot)    fixDot.SetActive(showDot);
            }

            ApplySizesAndColorsOnly();
        }

        if (logOnApply)
            Debug.Log(BuildOneLineLog(tag), this);
    }

    void ApplySizesAndColorsOnly()
    {
        if (spec == null) return;
        if (_mpb == null) _mpb = new MaterialPropertyBlock();

        float mPerDeg = spec.GetMetersPerDegree();
        float s = Mathf.Max(0.1f, previewScale);

        // --- Bullseye meters (truth -> effective) ---
        float innerDiam_m = Mathf.Max(1e-6f, innerDiam_deg * mPerDeg) * s;
        float outerDiam_m = Mathf.Max(1e-6f, outerDiam_deg * mPerDeg) * s;

        // --- Cross derived from outer circle, thickness is independent ---
        float outerRadius_m = 0.5f * outerDiam_m;
        float crossHalfLen_m = outerRadius_m * Mathf.Max(0.1f, crossHalfLenScale);

        float crossThk_m = Mathf.Max(1e-6f, crossThickness_deg * mPerDeg) * s;

        // Optional dot from spec (if enabled)
        float dotDiam_m = Mathf.Max(1e-6f, (2f * spec.fixationDotRadius_deg * mPerDeg)) * s;

        // Reset (pos+rot only)
        ResetPosRot(ringOuter);
        ResetPosRot(ringInner);
        ResetPosRot(hArm);
        ResetPosRot(vArm);
        ResetPosRot(fixDot);

        // Rings (disk stack)
        SetupDiskCylinderInXY(ringOuter, outerDiam_m, zOuterRing);
        SetupDiskCylinderInXY(ringInner, innerDiam_m, zInnerRing);

        // Crosshair (thin Z slab)
        float zThin = Mathf.Max(1e-6f, crossZThickness_m);

        if (hArm)
        {
            hArm.transform.localScale = new Vector3(2f * crossHalfLen_m, crossThk_m, zThin);
            hArm.transform.localPosition = new Vector3(0f, 0f, zCross);
        }
        if (vArm)
        {
            vArm.transform.localScale = new Vector3(crossThk_m, 2f * crossHalfLen_m, zThin);
            vArm.transform.localPosition = new Vector3(0f, 0f, zCross);
        }

        if (fixDot)
        {
            fixDot.transform.localScale = Vector3.one * dotDiam_m;
            fixDot.transform.localPosition = new Vector3(0f, 0f, zDot);
        }

        // Materials
        AssignSharedMaterialIfProvided(ringOuter, ringOuterMaterial);
        AssignSharedMaterialIfProvided(ringInner, ringInnerMaterial);
        AssignSharedMaterialIfProvided(hArm,      crossMaterial);
        AssignSharedMaterialIfProvided(vArm,      crossMaterial);
        AssignSharedMaterialIfProvided(fixDot,    dotMaterial);

        // Colors
        Color fixC = driveColorFromSpec ? spec.fixationColor : overrideFixColor;
        ApplyColorPropertyBlock(ringOuter, fixC);
        ApplyColorPropertyBlock(ringInner, holeColor);
        ApplyColorPropertyBlock(hArm,      crossColor);
        ApplyColorPropertyBlock(vArm,      crossColor);
        ApplyColorPropertyBlock(fixDot,    fixC);

        // Optional consistency warning: does inner cover cross intersection?
        // Intersection diagonal is crossThk*sqrt(2)
        if (innerCoversCrossClearanceFrac > 0f)
        {
            float requiredInner = crossThk_m * 1.41421356f * (1f + innerCoversCrossClearanceFrac);
            if (innerDiam_m < requiredInner)
            {
                Debug.LogWarning(
                    $"[Fixation] Inner circle may be too small to cover cross intersection. " +
                    $"innerDiam_m={innerDiam_m:F6}, required>={requiredInner:F6} (clearanceFrac={innerCoversCrossClearanceFrac:F2})",
                    this
                );
            }
        }
    }

    void SetupDiskCylinderInXY(GameObject go, float diameter, float z)
    {
        if (!go) return;

        float t = Mathf.Max(1e-6f, ringDiskThickness_m);

        // Cylinder axis is +Y. Align axis to ±Z so caps lie in XY.
        Vector3 targetAxis = diskNormalIsPlusZ ? Vector3.forward : Vector3.back;
        go.transform.localRotation = Quaternion.FromToRotation(Vector3.up, targetAxis);

        // X/Z set disk diameter; Y is thickness along cylinder axis
        go.transform.localScale = new Vector3(diameter, t, diameter);
        go.transform.localPosition = new Vector3(0f, 0f, z);
    }

    static void ResetPosRot(GameObject go)
    {
        if (!go) return;
        go.transform.localPosition = Vector3.zero;
        go.transform.localRotation = Quaternion.identity;
    }

    static void AssignSharedMaterialIfProvided(GameObject go, Material mat)
    {
        if (!go || !mat) return;
        var r = go.GetComponent<Renderer>();
        if (!r) return;
        r.sharedMaterial = mat;
        r.enabled = true;
    }

    void ApplyColorPropertyBlock(GameObject go, Color c)
    {
        if (!go) return;
        var r = go.GetComponent<Renderer>();
        if (!r) return;

        _mpb.Clear();

        // Only set properties that exist on the active material
        if (r.sharedMaterial != null)
        {
            if (r.sharedMaterial.HasProperty(BaseColorId)) _mpb.SetColor(BaseColorId, c);
            if (r.sharedMaterial.HasProperty(ColorId))     _mpb.SetColor(ColorId, c);
        }

        r.SetPropertyBlock(_mpb);
        r.enabled = true;
    }

    string BuildOneLineLog(string tag)
    {
        return $"[Fixation {GetInstanceID()}] ({tag}) z(out/cross/in)=({zOuterRing:F4},{zCross:F4},{zInnerRing:F4}) " +
               $"innerDiam_deg={innerDiam_deg:F3} outerDiam_deg={outerDiam_deg:F3} crossThk_deg={crossThickness_deg:F3} crossLenScale={crossHalfLenScale:F3}";
    }

    // ==================== SHADER-BASED CIRCLE METHODS ====================

    void CreateShaderObjects()
    {
        Shader circleShader = Shader.Find("Custom/SmoothCircle");
        Shader unlitShader = Shader.Find("Universal Render Pipeline/Unlit");
        if (unlitShader == null)
            unlitShader = Shader.Find("Unlit/Color");

        if (circleShader == null)
        {
            Debug.LogError("[Fixation_Controller] Custom/SmoothCircle shader not found! Falling back to cylinder mode.");
            useShaderCircles = false;
            return;
        }

        // Ring material (white ring with transparent hole)
        _ringMaterial = new Material(circleShader) { name = "FixRingMat" };

        // Center material (filled circle for inner/hole)
        _centerMaterial = new Material(circleShader) { name = "FixCenterMat" };

        // Crosshair materials (unlit rectangles)
        _crossMaterialH = new Material(unlitShader) { name = "FixCrossH" };
        _crossMaterialV = new Material(unlitShader) { name = "FixCrossV" };

        // Create quads
        _shaderRingQuad = CreateShaderQuad("ShaderRing", _ringMaterial);
        _shaderCenterQuad = CreateShaderQuad("ShaderCenter", _centerMaterial);
        _shaderHCross = CreateShaderQuad("ShaderHCross", _crossMaterialH);
        _shaderVCross = CreateShaderQuad("ShaderVCross", _crossMaterialV);

        // Nonius line quads (binocular reference lines above and below fixation)
        Shader noniusShader = Shader.Find("Custom/NoniusLine");
        if (noniusShader != null)
        {
            _noniusMaterialL = new Material(noniusShader) { name = "NoniusTop"    };
            _noniusMaterialR = new Material(noniusShader) { name = "NoniusBottom" };
            _noniusLeft  = CreateShaderQuad("NoniusTop",    _noniusMaterialL);
            _noniusRight = CreateShaderQuad("NoniusBottom", _noniusMaterialR);
        }
        else
        {
            Debug.LogWarning("[Fixation_Controller] Custom/NoniusLine shader not found. Nonius lines disabled.");
        }

        // Hide old cylinder-based objects if assigned
        if (ringOuter) ringOuter.SetActive(false);
        if (ringInner) ringInner.SetActive(false);
        if (hArm) hArm.SetActive(false);
        if (vArm) vArm.SetActive(false);
        if (fixDot) fixDot.SetActive(false);
    }

    void DestroyShaderObjects()
    {
        SafeDestroyObj(_shaderRingQuad);
        SafeDestroyObj(_shaderCenterQuad);
        SafeDestroyObj(_shaderHCross);
        SafeDestroyObj(_shaderVCross);
        SafeDestroyObj(_ringMaterial);
        SafeDestroyObj(_centerMaterial);
        SafeDestroyObj(_crossMaterialH);
        SafeDestroyObj(_crossMaterialV);

        _shaderRingQuad = null;
        _shaderCenterQuad = null;
        _shaderHCross = null;
        _shaderVCross = null;
        _ringMaterial = null;
        _centerMaterial = null;
        _crossMaterialH = null;
        _crossMaterialV = null;

        SafeDestroyObj(_noniusLeft);
        SafeDestroyObj(_noniusRight);
        SafeDestroyObj(_noniusMaterialL);
        SafeDestroyObj(_noniusMaterialR);
        _noniusLeft = null;
        _noniusRight = null;
        _noniusMaterialL = null;
        _noniusMaterialR = null;
    }

    void SafeDestroyObj(Object obj)
    {
        if (obj == null) return;
        if (Application.isPlaying)
            Destroy(obj);
        else
            DestroyImmediate(obj);
    }

    GameObject CreateShaderQuad(string name, Material mat)
    {
        var go = GameObject.CreatePrimitive(PrimitiveType.Quad);
        go.name = name;
        go.transform.SetParent(transform, false);

        // Remove collider
        var col = go.GetComponent<Collider>();
        if (col != null) SafeDestroyObj(col);

        var renderer = go.GetComponent<MeshRenderer>();
        renderer.sharedMaterial = mat;
        renderer.shadowCastingMode = UnityEngine.Rendering.ShadowCastingMode.Off;
        renderer.receiveShadows = false;

        return go;
    }

    void ApplyShaderCircles()
    {
        if (_shaderRingQuad == null || _ringMaterial == null) return;
        if (spec == null) return;

        float mPerDeg = spec.GetMetersPerDegree();
        float s = Mathf.Max(0.1f, previewScale);

        // Get sizes in meters
        float innerDiam_m = Mathf.Max(1e-6f, innerDiam_deg * mPerDeg) * s;
        float outerDiam_m = Mathf.Max(1e-6f, outerDiam_deg * mPerDeg) * s;
        float crossThk_m = Mathf.Max(1e-6f, crossThickness_deg * mPerDeg) * s;
        float outerRadius_m = 0.5f * outerDiam_m;
        float crossHalfLen_m = outerRadius_m * Mathf.Max(0.1f, crossHalfLenScale);

        // Colors
        Color fixC = driveColorFromSpec ? spec.fixationColor : overrideFixColor;

        // --- Ring (outer white with transparent hole) ---
        _shaderRingQuad.SetActive(showRings);
        _shaderRingQuad.transform.localPosition = new Vector3(0, 0, zOuterRing);
        _shaderRingQuad.transform.localScale = new Vector3(outerDiam_m, outerDiam_m, 1f);
        _shaderRingQuad.transform.localRotation = Quaternion.identity;

        float innerFraction = (innerDiam_m / outerDiam_m) * 0.5f;
        _ringMaterial.SetColor(ShaderColorId, fixC);
        _ringMaterial.SetFloat(InnerRadiusId, innerFraction);
        _ringMaterial.SetFloat(OuterRadiusId, 0.5f);
        _ringMaterial.SetFloat(SmoothnessId, edgeSmoothness);

        // --- Center dot (filled circle, covers crosshair intersection) ---
        _shaderCenterQuad.SetActive(showRings);
        _shaderCenterQuad.transform.localPosition = new Vector3(0, 0, zInnerRing);
        _shaderCenterQuad.transform.localScale = new Vector3(innerDiam_m, innerDiam_m, 1f);
        _shaderCenterQuad.transform.localRotation = Quaternion.identity;

        _centerMaterial.SetColor(ShaderColorId, holeColor);
        _centerMaterial.SetFloat(InnerRadiusId, 0f);
        _centerMaterial.SetFloat(OuterRadiusId, 0.5f);
        _centerMaterial.SetFloat(SmoothnessId, edgeSmoothness);

        // --- Crosshairs ---
        _shaderHCross.SetActive(showCross);
        _shaderVCross.SetActive(showCross);

        if (showCross)
        {
            _shaderHCross.transform.localPosition = new Vector3(0, 0, zCross);
            _shaderHCross.transform.localScale = new Vector3(2f * crossHalfLen_m, crossThk_m, 1f);
            _shaderHCross.transform.localRotation = Quaternion.identity;

            _shaderVCross.transform.localPosition = new Vector3(0, 0, zCross);
            _shaderVCross.transform.localScale = new Vector3(crossThk_m, 2f * crossHalfLen_m, 1f);
            _shaderVCross.transform.localRotation = Quaternion.identity;

            // Set crosshair colors
            if (_crossMaterialH.HasProperty("_BaseColor"))
            {
                _crossMaterialH.SetColor("_BaseColor", crossColor);
                _crossMaterialV.SetColor("_BaseColor", crossColor);
            }
            else
            {
                _crossMaterialH.SetColor("_Color", crossColor);
                _crossMaterialV.SetColor("_Color", crossColor);
            }
        }

        // --- Nonius lines (dichoptic) ---
        bool noniusReady = showNoniusLines && _noniusLeft != null && _noniusRight != null;
        if (_noniusLeft  != null) _noniusLeft.SetActive(noniusReady);
        if (_noniusRight != null) _noniusRight.SetActive(noniusReady);

        if (noniusReady)
        {
            float nLen_m  = Mathf.Max(1e-5f, noniusLength_deg * mPerDeg) * s;
            float nWidth_m = Mathf.Max(1e-5f, noniusWidth_deg  * mPerDeg) * s;
            float nGap_m   = Mathf.Max(0f,    noniusGap_deg    * mPerDeg) * s;

            // Center of each line: gap + half-length above/below fixation center
            float centerY = nGap_m + nLen_m * 0.5f;

            // Left eye: line ABOVE center (positive Y)
            _noniusLeft.transform.localPosition  = new Vector3(0f,  centerY, zCross);
            _noniusLeft.transform.localScale      = new Vector3(nWidth_m, nLen_m, 1f);
            _noniusLeft.transform.localRotation   = Quaternion.identity;
            _noniusMaterialL.SetColor(ShaderColorId, noniusColor);

            // Right eye: line BELOW center (negative Y)
            _noniusRight.transform.localPosition = new Vector3(0f, -centerY, zCross);
            _noniusRight.transform.localScale     = new Vector3(nWidth_m, nLen_m, 1f);
            _noniusRight.transform.localRotation  = Quaternion.identity;
            _noniusMaterialR.SetColor(ShaderColorId, noniusColor);
        }
    }
}