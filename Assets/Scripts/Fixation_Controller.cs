// FILE: Fixation_Controller.cs
using UnityEngine;

[DisallowMultipleComponent]
public class Fixation_Controller : MonoBehaviour
{
    [Header("Source of truth")]
    public ExperimentSpec spec;

    [Header("Monitor Preview (render-only)")]
    [Min(0.1f)] public float previewScale = 1f;

    [Header("Assign fixation parts (children of this object)")]
    public GameObject fixDot;      // optional
    public GameObject ringOuter;   // Cylinder (disk)
    public GameObject ringInner;   // Cylinder (disk)
    public GameObject hArm;        // Cube
    public GameObject vArm;        // Cube

    [Header("Visibility (script overrides while playing)")]
    public bool showDot = false;
    public bool showRings = true;
    public bool showCross = true;

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
    [Tooltip("Inner circle DIAMETER in degrees (paper: 0.24°).")]
    public float innerDiam_deg = 0.24f;

    [Tooltip("Outer circle DIAMETER in degrees (paper: 0.60°).")]
    public float outerDiam_deg = 0.60f;

    [Header("Crosshair geometry (decoupled from inner circle)")]
    [Tooltip("Crosshair stroke thickness in degrees (independent knob).")]
    public float crossThickness_deg = 0.03f;

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

    void OnEnable() { Apply("OnEnable"); }
    void Start()    { Apply("Start"); }

    void OnValidate()
    {
        if (isActiveAndEnabled)
            ApplySizesAndColorsOnly();
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

        if (Application.isPlaying)
        {
            if (ringOuter) ringOuter.SetActive(showRings);
            if (ringInner) ringInner.SetActive(showRings);
            if (hArm)      hArm.SetActive(showCross);
            if (vArm)      vArm.SetActive(showCross);
            if (fixDot)    fixDot.SetActive(showDot);
        }

        ApplySizesAndColorsOnly();

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
}