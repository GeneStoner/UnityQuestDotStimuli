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

    [Tooltip("Generate fixation target as a single runtime PNG sprite (recommended for Quest). " +
             "Uses Custom/FixationSprite shader (Queue=Overlay+20, ZTest Always) so target always " +
             "appears in front of dots. Ignored when useShaderCircles=false.")]
    public bool usePNGSprite = true;

    [Tooltip("Use analytical SDF shader (Custom/FixationSpriteSDF) instead of a pre-baked texture. " +
             "Resolution-independent — crisp at any size. Requires fixationSDFShaderAsset to be assigned. " +
             "ROLLBACK: uncheck this to revert to texture mode (fixationSpriteShaderAsset + spriteTexSize).")]
    public bool useSDFShader = false;

    [Tooltip("Direct reference to Custom/FixationSpriteSDF shader (SDF mode). " +
             "Drag FixationSpriteSDF.shader here.")]
    public Shader fixationSDFShaderAsset;

    [Tooltip("Resolution of the generated sprite texture (texture mode only, ignored in SDF mode). " +
             "512 is recommended; higher = smoother edges at large sizes.")]
    [Range(64, 512)]
    public int spriteTexSize = 256;

    [Tooltip("Direct reference to Custom/FixationSprite shader (texture mode). Drag FixationSprite.shader here. " +
             "When assigned, Unity auto-bundles the shader in builds (more reliable than Shader.Find).")]
    public Shader fixationSpriteShaderAsset;

    [Header("Shader Circle Settings (when useShaderCircles=true)")]
    [Range(0.005f, 0.1f)]
    public float edgeSmoothness = 0.03f;

    [Header("Assign fixation parts (when useShaderCircles=false)")]
    public GameObject fixDot;      // optional
    public GameObject ringOuter;   // Cylinder (disk)
    public GameObject ringInner;   // Cylinder (disk)
    public GameObject hArm;        // Cube
    public GameObject vArm;        // Cube

    // Geometry-created objects (when useShaderCircles=true)
    // Ring and center use procedural circle meshes — correct by construction,
    // no UV-space distance computation that could appear oval at small sizes in VR.
    // Cross arms stay as flat quads (rectangles are fine as-is).
    private GameObject _ringObj;       // annulus mesh
    private GameObject _centerObj;     // filled circle mesh (covers cross intersection)
    private GameObject _shaderHCross;
    private GameObject _shaderVCross;
    private Material _ringMaterial;
    private Material _centerMaterial;
    private Material _crossMaterialH;
    private Material _crossMaterialV;

    // PNG Sprite mode — single quad with runtime-generated RGBA texture.
    // Renders in Queue=Overlay+20 (after dots at Overlay+10), ZTest Always.
    // Avoids all procedural-mesh / shader-circle complexity.
    private GameObject _spriteObj;
    private Material   _spriteMaterial;
    private Texture2D  _spriteTexture;

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
    [Tooltip("Outer disc DIAMETER in degrees.")]
    public float outerDiam_deg = 1.00f;

    [Tooltip("In PNG sprite mode: center dot DIAMETER in degrees (white dot over crosshair intersection). " +
             "In procedural mesh mode: inner ring diameter.")]
    public float innerDiam_deg = 0.30f;

    [Header("Crosshair geometry (decoupled from inner circle)")]
    [Tooltip("Crosshair stroke thickness in degrees (independent knob).")]
    public float crossThickness_deg = 0.12f;

    [Tooltip("SDF mode only: how far the cross tips extend beyond the disc edge, in degrees. " +
             "Small value (e.g. 0.10) creates a visible stub of the cross just outside the white disc. " +
             "0 = arms end exactly at disc edge (clipped). Ignored in texture mode.")]
    [Min(0f)]
    public float crossOvershoot_deg = 0.10f;

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
            // In PNG sprite mode _ringObj is null by design; check _spriteObj too.
            if (_ringObj == null && _spriteObj == null)
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
        float s = Mathf.Max(0.1f, previewScale) * (spec != null && spec.fixationScaleFactor > 0f ? spec.fixationScaleFactor : 1f);

        float effOuterDiam_deg = outerDiam_deg;
        float effInnerDiam_deg = innerDiam_deg;
        float effCrossThk_deg  = crossThickness_deg;

        // --- Bullseye meters (truth -> effective) ---
        float innerDiam_m = Mathf.Max(1e-6f, effInnerDiam_deg * mPerDeg) * s;
        float outerDiam_m = Mathf.Max(1e-6f, effOuterDiam_deg * mPerDeg) * s;

        // --- Cross derived from outer circle, thickness is independent ---
        float outerRadius_m = 0.5f * outerDiam_m;
        float crossHalfLen_m = outerRadius_m * Mathf.Max(0.1f, crossHalfLenScale);

        float crossThk_m = Mathf.Max(1e-6f, effCrossThk_deg * mPerDeg) * s;

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

    // ==================== CIRCLE / CROSSHAIR GEOMETRY METHODS ====================

    void CreateShaderObjects()
    {
        // Hide old cylinder-based objects if assigned
        if (ringOuter) ringOuter.SetActive(false);
        if (ringInner) ringInner.SetActive(false);
        if (hArm) hArm.SetActive(false);
        if (vArm) vArm.SetActive(false);
        if (fixDot) fixDot.SetActive(false);

        // Nonius lines — shared between both rendering modes
        Shader noniusShader = Shader.Find("Custom/NoniusLine");
        if (noniusShader != null)
        {
            _noniusMaterialL = new Material(noniusShader) { name = "NoniusTop"    };
            _noniusMaterialR = new Material(noniusShader) { name = "NoniusBottom" };
            _noniusMaterialL.SetInt("_TargetEye", 0);  // top segment → left eye only
            _noniusMaterialR.SetInt("_TargetEye", 1);  // bottom segment → right eye only
            _noniusLeft  = CreateShaderQuad("NoniusTop",    _noniusMaterialL);
            _noniusRight = CreateShaderQuad("NoniusBottom", _noniusMaterialR);
        }
        else
        {
            Debug.LogWarning("[Fixation_Controller] Custom/NoniusLine shader not found. Nonius lines disabled.");
        }

        if (usePNGSprite)
        {
            // SDF path: analytical shader, no texture — resolution-independent.
            // Texture path: pre-baked RGBA texture, resolution limited by spriteTexSize.
            // Both use Queue=Overlay+20, ZTest Always — always on top of dots (Overlay+10).
            Shader spriteShader = null;

            if (useSDFShader)
            {
                spriteShader = fixationSDFShaderAsset != null
                    ? fixationSDFShaderAsset
                    : Shader.Find("Custom/FixationSpriteSDF");
                if (spriteShader == null)
                    Debug.LogWarning("[Fixation_Controller] Custom/FixationSpriteSDF not found. " +
                                     "Assign FixationSpriteSDF.shader to fixationSDFShaderAsset. " +
                                     "Falling back to texture mode.");
            }

            if (spriteShader == null)
            {
                // Texture mode (also SDF fallback)
                spriteShader = fixationSpriteShaderAsset != null
                    ? fixationSpriteShaderAsset
                    : Shader.Find("Custom/FixationSprite");
            }

            if (spriteShader == null)
            {
                Debug.LogError("[Fixation_Controller] No fixation sprite shader found! " +
                               "Assign FixationSprite.shader or FixationSpriteSDF.shader. " +
                               "Falling back to procedural mesh mode.");
                usePNGSprite = false;
                // fall through to procedural mesh path below
            }
            else
            {
                _spriteMaterial = new Material(spriteShader) { name = "FixSpriteMat" };
                _spriteObj = CreateShaderQuad("FixSprite", _spriteMaterial);
                return; // sprite mode set up; nonius already created above
            }
        }

        // Procedural mesh path (fallback when usePNGSprite=false or shader not found)
        Shader unlitShader = Shader.Find("Universal Render Pipeline/Unlit");
        if (unlitShader == null)
            unlitShader = Shader.Find("Unlit/Color");
        if (unlitShader == null)
        {
            Debug.LogError("[Fixation_Controller] No Unlit shader found! Falling back to cylinder mode.");
            useShaderCircles = false;
            return;
        }

        // Ring and center use Unlit — shape is correct by geometry, no shader math needed.
        _ringMaterial   = new Material(unlitShader) { name = "FixRingMat" };
        _centerMaterial = new Material(unlitShader) { name = "FixCenterMat" };
        _crossMaterialH = new Material(unlitShader) { name = "FixCrossH" };
        _crossMaterialV = new Material(unlitShader) { name = "FixCrossV" };

        // Procedural circle meshes for ring and center.
        _ringObj   = CreateMeshObject("Ring",   _ringMaterial);
        _centerObj = CreateMeshObject("Center", _centerMaterial);
        // Cross arms stay as flat quads (rectangles are correct by construction).
        _shaderHCross = CreateShaderQuad("HCross", _crossMaterialH);
        _shaderVCross = CreateShaderQuad("VCross", _crossMaterialV);
    }

    void DestroyShaderObjects()
    {
        // PNG sprite mode objects
        SafeDestroyObj(_spriteObj);
        SafeDestroyObj(_spriteMaterial);
        SafeDestroyObj(_spriteTexture);
        _spriteObj = null;
        _spriteMaterial = null;
        _spriteTexture = null;

        // Procedural mesh mode objects
        SafeDestroyObj(_ringObj);
        SafeDestroyObj(_centerObj);
        SafeDestroyObj(_shaderHCross);
        SafeDestroyObj(_shaderVCross);
        SafeDestroyObj(_ringMaterial);
        SafeDestroyObj(_centerMaterial);
        SafeDestroyObj(_crossMaterialH);
        SafeDestroyObj(_crossMaterialV);

        _ringObj = null;
        _centerObj = null;
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
        go.hideFlags = HideFlags.HideAndDontSave;
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
        if (spec == null) return;

        if (usePNGSprite)
        {
            ApplySpriteMode();
            ApplyNoniusLines();
            return;
        }

        if (_ringObj == null || _ringMaterial == null) return;

        float mPerDeg = spec.GetMetersPerDegree();
        float s = Mathf.Max(0.1f, previewScale) * (spec != null && spec.fixationScaleFactor > 0f ? spec.fixationScaleFactor : 1f);

        float outerDiam_m = Mathf.Max(1e-6f, outerDiam_deg * mPerDeg) * s;
        float innerDiam_m = Mathf.Max(1e-6f, innerDiam_deg * mPerDeg) * s;
        float crossThk_m  = Mathf.Max(1e-6f, crossThickness_deg * mPerDeg) * s;
        float outerRadius_m  = 0.5f * outerDiam_m;
        float crossHalfLen_m = outerRadius_m * Mathf.Max(0.1f, crossHalfLenScale);

        Color fixC = driveColorFromSpec ? spec.fixationColor : overrideFixColor;

        // --- Ring (procedural annulus mesh, scaled to physical size) ---
        // Mesh vertices are at unit radius (0.5 outer). Scale object → physical size.
        // innerFrac is the inner/outer ratio for the mesh.
        _ringObj.SetActive(showRings);
        float innerFrac = Mathf.Clamp01(innerDiam_m / outerDiam_m);
        RebuildRingMesh(_ringObj.GetComponent<MeshFilter>(), innerFrac * 0.5f, 0.5f);
        _ringObj.transform.localPosition = new Vector3(0, 0, zOuterRing);
        _ringObj.transform.localScale    = new Vector3(outerDiam_m, outerDiam_m, 1f);
        _ringObj.transform.localRotation = Quaternion.identity;
        SetUnlitColor(_ringMaterial, fixC);

        // --- Center filled circle (covers cross intersection, black hole) ---
        _centerObj.SetActive(showRings);
        RebuildFilledCircleMesh(_centerObj.GetComponent<MeshFilter>(), 0.5f);
        _centerObj.transform.localPosition = new Vector3(0, 0, zInnerRing);
        _centerObj.transform.localScale    = new Vector3(innerDiam_m, innerDiam_m, 1f);
        _centerObj.transform.localRotation = Quaternion.identity;
        SetUnlitColor(_centerMaterial, holeColor);

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

        ApplyNoniusLines();
    }

    // ==================== PNG SPRITE MODE ====================

    void ApplySpriteMode()
    {
        if (_spriteObj == null || _spriteMaterial == null) return;

        if (useSDFShader && _spriteMaterial.shader.name == "Custom/FixationSpriteSDF")
        {
            ApplySDFMode();
            return;
        }

        // --- Texture mode ---
        float mPerDeg = spec.GetMetersPerDegree();
        float s = Mathf.Max(0.1f, previewScale) * (spec != null && spec.fixationScaleFactor > 0f ? spec.fixationScaleFactor : 1f);

        float outerDiam_m = Mathf.Max(1e-6f, outerDiam_deg * mPerDeg) * s;

        // Regenerate texture whenever Apply() is called (covers Inspector changes).
        SafeDestroyObj(_spriteTexture);
        _spriteTexture = GenerateFixationTexture(mPerDeg, s);
        _spriteMaterial.mainTexture = _spriteTexture;

        // Quad = outer disc diameter; crosshairs are clipped inside, nothing outside.
        _spriteObj.transform.localPosition = new Vector3(0f, 0f, zOuterRing);
        _spriteObj.transform.localScale    = new Vector3(outerDiam_m, outerDiam_m, 1f);
        _spriteObj.transform.localRotation = Quaternion.identity;
        _spriteObj.SetActive(true);
    }

    void ApplySDFMode()
    {
        // SDF mode: no texture — geometry is computed analytically in the fragment shader.
        // Parameters are passed as normalized ratios (UV half-space: 0=center, 0.5=disc edge).
        if (_spriteObj == null || _spriteMaterial == null) return;

        float mPerDeg = spec.GetMetersPerDegree();
        float s = Mathf.Max(0.1f, previewScale) * (spec != null && spec.fixationScaleFactor > 0f ? spec.fixationScaleFactor : 1f);

        float outerDiam_m   = Mathf.Max(1e-6f, outerDiam_deg * mPerDeg) * s;
        float outerDiam_deg_eff = Mathf.Max(1e-6f, outerDiam_deg);

        // Normalized: outer disc radius = 0.5 (fills quad edge-to-edge).
        // All other values scale relative to that.
        float crossHalfWNorm    = 0.5f * crossThickness_deg / outerDiam_deg_eff;
        float dotRadiusNorm     = 0.5f * innerDiam_deg       / outerDiam_deg_eff;
        float crossOvershootNorm = 0.5f * Mathf.Max(0f, crossOvershoot_deg) / outerDiam_deg_eff;

        Color fixC = driveColorFromSpec ? spec.fixationColor : overrideFixColor;

        _spriteMaterial.SetFloat("_CrossHalfWNorm",    crossHalfWNorm);
        _spriteMaterial.SetFloat("_DotRadiusNorm",     dotRadiusNorm);
        _spriteMaterial.SetFloat("_CrossOvershootNorm", crossOvershootNorm);
        _spriteMaterial.SetColor("_FixColor",           fixC);
        _spriteMaterial.SetColor("_CrossColor",         crossColor);

        // Free any stale texture from a previous texture-mode run
        SafeDestroyObj(_spriteTexture);
        _spriteTexture = null;

        _spriteObj.transform.localPosition = new Vector3(0f, 0f, zOuterRing);
        _spriteObj.transform.localScale    = new Vector3(outerDiam_m, outerDiam_m, 1f);
        _spriteObj.transform.localRotation = Quaternion.identity;
        _spriteObj.SetActive(true);
    }

    // Generates an RGBA32 Texture2D containing the full fixation bulls-eye.
    // Layout (UV origin at bottom-left, center at (0.5, 0.5)):
    //   - White annulus (fixC):  innerR_m ≤ r ≤ outerR_m
    //   - Black crosshairs:      |wx| ≤ crossHalfW_m  OR  |wy| ≤ crossHalfW_m
    //   - Black center disc:     r ≤ innerR_m  (covers cross intersection)
    //   - Transparent elsewhere (corners of quad, hole between arms outside inner disc)
    //
    // The quad world-size = 2 × crossHalfLen_m, so crosshair arms reach exactly the
    // outer ring edge (crossHalfLenScale=1.0) or slightly beyond (>1.0).
    // Generates an RGBA32 Texture2D with the CCP-style fixation target:
    //
    //   Layer 1 (bottom): White filled disc, radius = outerR_m
    //   Layer 2:          Black crosshairs clipped to disc (|wx|<crossHalfW OR |wy|<crossHalfW)
    //   Layer 3 (top):    Small white center dot, radius = innerR_m  (innerDiam_deg repurposed)
    //
    // Quad world-size = outerDiam_m (crosshairs end at disc edge, nothing outside).
    Texture2D GenerateFixationTexture(float mPerDeg, float s)
    {
        int texSize = Mathf.Max(64, spriteTexSize);

        float outerR_m     = 0.5f * Mathf.Max(1e-6f, outerDiam_deg      * mPerDeg) * s;
        float centerDotR_m = 0.5f * Mathf.Max(1e-6f, innerDiam_deg      * mPerDeg) * s; // center dot
        float crossHalfW_m = 0.5f * Mathf.Max(1e-6f, crossThickness_deg * mPerDeg) * s;

        // Quad covers exactly the disc diameter — crosshairs are clipped inside it.
        float quadHalf = outerR_m;
        float pixM = 2f * quadHalf / texSize;
        float aaR  = pixM * 1.5f;   // anti-alias radius (1.5 pixels)

        Color fixC = driveColorFromSpec ? spec.fixationColor : overrideFixColor;

        var pixels = new Color32[texSize * texSize];

        for (int py = 0; py < texSize; py++)
        {
            for (int px = 0; px < texSize; px++)
            {
                float wx = (px + 0.5f - texSize * 0.5f) * pixM;
                float wy = (py + 0.5f - texSize * 0.5f) * pixM;
                float r  = Mathf.Sqrt(wx * wx + wy * wy);

                // Layer 1: white filled disc
                float discAlpha = 0f;
                if (showRings)
                    discAlpha = 1f - Mathf.Clamp01((r - (outerR_m - aaR)) / (2f * aaR));

                // Layer 2: black crosshairs, clipped to disc boundary
                float crossAlpha = 0f;
                if (showCross && discAlpha > 0f)
                {
                    float hFade = 1f - Mathf.Clamp01((Mathf.Abs(wy) - (crossHalfW_m - aaR)) / (2f * aaR));
                    float vFade = 1f - Mathf.Clamp01((Mathf.Abs(wx) - (crossHalfW_m - aaR)) / (2f * aaR));
                    crossAlpha  = Mathf.Max(hFade, vFade) * discAlpha;
                }

                // Layer 3: small white center dot
                float dotAlpha = 0f;
                if (showRings)
                    dotAlpha = 1f - Mathf.Clamp01((r - (centerDotR_m - aaR)) / (2f * aaR));

                // --- Porter-Duff "over": disc → crosshairs → center dot ---
                float rF = 0f, gF = 0f, bF = 0f, aF = 0f;

                // Layer 1: disc (fixC = white)
                if (discAlpha > 0f)
                {
                    rF = fixC.r; gF = fixC.g; bF = fixC.b; aF = discAlpha;
                }

                // Layer 2: crosshairs (crossColor = black) over disc
                if (crossAlpha > 0f)
                {
                    float aOut = crossAlpha + aF * (1f - crossAlpha);
                    if (aOut > 1e-6f)
                    {
                        rF = (crossColor.r * crossAlpha + rF * aF * (1f - crossAlpha)) / aOut;
                        gF = (crossColor.g * crossAlpha + gF * aF * (1f - crossAlpha)) / aOut;
                        bF = (crossColor.b * crossAlpha + bF * aF * (1f - crossAlpha)) / aOut;
                    }
                    aF = aOut;
                }

                // Layer 3: center dot (fixC = white) over crosshairs
                if (dotAlpha > 0f)
                {
                    float aOut = dotAlpha + aF * (1f - dotAlpha);
                    if (aOut > 1e-6f)
                    {
                        rF = (fixC.r * dotAlpha + rF * aF * (1f - dotAlpha)) / aOut;
                        gF = (fixC.g * dotAlpha + gF * aF * (1f - dotAlpha)) / aOut;
                        bF = (fixC.b * dotAlpha + bF * aF * (1f - dotAlpha)) / aOut;
                    }
                    aF = aOut;
                }

                pixels[py * texSize + px] = new Color32(
                    (byte)Mathf.RoundToInt(Mathf.Clamp01(rF) * 255f),
                    (byte)Mathf.RoundToInt(Mathf.Clamp01(gF) * 255f),
                    (byte)Mathf.RoundToInt(Mathf.Clamp01(bF) * 255f),
                    (byte)Mathf.RoundToInt(Mathf.Clamp01(aF) * 255f)
                );
            }
        }

        var tex = new Texture2D(texSize, texSize, TextureFormat.RGBA32, false);
        tex.name       = "FixationSpriteTex";
        tex.filterMode = FilterMode.Bilinear;
        tex.wrapMode   = TextureWrapMode.Clamp;
        tex.SetPixels32(pixels);
        tex.Apply();
        return tex;
    }

    // ==================== NONIUS LINE HELPERS ====================

    void ApplyNoniusLines()
    {
        if (spec == null) return;
        float mPerDeg = spec.GetMetersPerDegree();
        float s = Mathf.Max(0.1f, previewScale) * (spec != null && spec.fixationScaleFactor > 0f ? spec.fixationScaleFactor : 1f);

        bool noniusReady = showNoniusLines && _noniusLeft != null && _noniusRight != null;
        if (_noniusLeft  != null) _noniusLeft.SetActive(noniusReady);
        if (_noniusRight != null) _noniusRight.SetActive(noniusReady);

        if (!noniusReady) return;

        float nLen_m   = Mathf.Max(1e-5f, noniusLength_deg * mPerDeg) * s;
        float nWidth_m = Mathf.Max(1e-5f, noniusWidth_deg  * mPerDeg) * s;
        float nGap_m   = Mathf.Max(0f,    noniusGap_deg    * mPerDeg) * s;

        float centerY = nGap_m + nLen_m * 0.5f;

        _noniusLeft.transform.localPosition  = new Vector3(0f,  centerY, zCross);
        _noniusLeft.transform.localScale      = new Vector3(nWidth_m, nLen_m, 1f);
        _noniusLeft.transform.localRotation   = Quaternion.identity;
        _noniusMaterialL.SetColor(ShaderColorId, noniusColor);

        _noniusRight.transform.localPosition = new Vector3(0f, -centerY, zCross);
        _noniusRight.transform.localScale     = new Vector3(nWidth_m, nLen_m, 1f);
        _noniusRight.transform.localRotation  = Quaternion.identity;
        _noniusMaterialR.SetColor(ShaderColorId, noniusColor);
    }

    // ==================== PROCEDURAL CIRCLE MESH HELPERS ====================

    // Creates a GameObject with MeshFilter + MeshRenderer, parented here, hidden from hierarchy.
    GameObject CreateMeshObject(string name, Material mat)
    {
        var go = new GameObject(name);
        go.hideFlags = HideFlags.HideAndDontSave;
        go.transform.SetParent(transform, false);
        go.AddComponent<MeshFilter>();
        var mr = go.AddComponent<MeshRenderer>();
        mr.sharedMaterial = mat;
        mr.shadowCastingMode = UnityEngine.Rendering.ShadowCastingMode.Off;
        mr.receiveShadows = false;
        return go;
    }

    // Rebuilds the MeshFilter with an annulus (ring) mesh.
    // innerR and outerR are in local units; the object is then scaled to physical size.
    // 128 segments gives a smooth circle at any size used in this experiment.
    static void RebuildRingMesh(MeshFilter mf, float innerR, float outerR, int segments = 128)
    {
        Mesh mesh = mf.sharedMesh;
        if (mesh == null)
        {
            mesh = new Mesh { name = "FixRing" };
            mf.sharedMesh = mesh;
        }

        int verts = segments * 2;
        var positions = new Vector3[verts];
        var uvs       = new Vector2[verts];
        var tris      = new int[segments * 6];

        for (int i = 0; i < segments; i++)
        {
            float a = (float)i / segments * Mathf.PI * 2f;
            float c = Mathf.Cos(a), s = Mathf.Sin(a);
            positions[i * 2]     = new Vector3(c * innerR, s * innerR, 0f);
            positions[i * 2 + 1] = new Vector3(c * outerR, s * outerR, 0f);
            uvs[i * 2]     = new Vector2(c * 0.5f + 0.5f, s * 0.5f + 0.5f);
            uvs[i * 2 + 1] = new Vector2(c * 0.5f + 0.5f, s * 0.5f + 0.5f);

            int j = i * 6;
            int a0 =  i * 2,        b0 =  i * 2 + 1;
            int a1 = ((i + 1) % segments) * 2,
                b1 = ((i + 1) % segments) * 2 + 1;
            tris[j]     = a0; tris[j + 1] = b0; tris[j + 2] = b1;
            tris[j + 3] = a0; tris[j + 4] = b1; tris[j + 5] = a1;
        }

        mesh.Clear();
        mesh.vertices  = positions;
        mesh.uv        = uvs;
        mesh.triangles = tris;
        mesh.RecalculateNormals();
    }

    // Rebuilds the MeshFilter with a filled circle (fan of triangles).
    static void RebuildFilledCircleMesh(MeshFilter mf, float radius, int segments = 128)
    {
        Mesh mesh = mf.sharedMesh;
        if (mesh == null)
        {
            mesh = new Mesh { name = "FixCenter" };
            mf.sharedMesh = mesh;
        }

        var positions = new Vector3[segments + 1];
        var uvs       = new Vector2[segments + 1];
        var tris      = new int[segments * 3];

        positions[0] = Vector3.zero;
        uvs[0]       = new Vector2(0.5f, 0.5f);

        for (int i = 0; i < segments; i++)
        {
            float a = (float)i / segments * Mathf.PI * 2f;
            float c = Mathf.Cos(a), s = Mathf.Sin(a);
            positions[i + 1] = new Vector3(c * radius, s * radius, 0f);
            uvs[i + 1]       = new Vector2(c * 0.5f + 0.5f, s * 0.5f + 0.5f);

            tris[i * 3]     = 0;
            tris[i * 3 + 1] = i + 1;
            tris[i * 3 + 2] = (i + 1) % segments + 1;
        }

        mesh.Clear();
        mesh.vertices  = positions;
        mesh.uv        = uvs;
        mesh.triangles = tris;
        mesh.RecalculateNormals();
    }

    // Sets the main color on an Unlit material, handling both URP and legacy property names.
    static void SetUnlitColor(Material mat, Color color)
    {
        if (mat == null) return;
        if (mat.HasProperty("_BaseColor")) mat.SetColor("_BaseColor", color);
        if (mat.HasProperty("_Color"))     mat.SetColor("_Color",     color);
    }
}