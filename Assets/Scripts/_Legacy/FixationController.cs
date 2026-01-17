// FILE: FixationController.cs
using UnityEngine;

[DisallowMultipleComponent]
public class FixationController : MonoBehaviour
{
    [Header("Render placement")]
    [Tooltip("Distance in front of the camera (meters) ONLY if this object is DIRECTLY parented to a Camera.")]
    public float fixationDistance_m = 1.0f;

    [Tooltip("Force all fixation parts to this layer (-1 = don't force).")]
    public int forceLayer = 0; // Default

    [Header("Optional: assign explicitly (else found/created by name)")]
    public GameObject fixDot;
    public GameObject fixRing;
    public GameObject fixHArm;
    public GameObject fixVArm;

    private int _lastSig = int.MinValue;

    public void ConfigureFromSpec(ExperimentSpec spec)
    {
        Debug.Log("[FixationController] ConfigureFromSpec CALLED", this);

        if (spec == null) return;

        EnsureChildrenExist();

        int sig = ComputeSig(spec);
        if (sig == _lastSig) return;
        _lastSig = sig;

        // IMPORTANT: only treat as "camera parented" if the IMMEDIATE parent has a Camera.
        bool directParentIsCamera = (transform.parent != null && transform.parent.GetComponent<Camera>() != null);

        // If directly under camera: push forward so we’re not clipped.
        // If under StimulusRoot: stay at local origin (StimulusRoot already places the stimulus).
        transform.localPosition = directParentIsCamera
            ? new Vector3(0f, 0f, Mathf.Max(0.05f, fixationDistance_m))
            : Vector3.zero;

        transform.localRotation = Quaternion.identity;

        if (forceLayer >= 0)
            SetLayerRecursively(gameObject, forceLayer);

        // ---- Toggle visibility by style ----
        bool showDot = false, showRing = false, showCross = false;

        switch (spec.fixationStyle)
        {
            case ExperimentSpec.FixationStyle.Dot:
                showDot = true;
                break;

            case ExperimentSpec.FixationStyle.BullsEye:
                showDot = true;
                showRing = true;
                break;

            case ExperimentSpec.FixationStyle.BullsEyePlusCrosshair:
                showDot = true;
                showRing = true;
                showCross = true;
                break;

            case ExperimentSpec.FixationStyle.Crosshair:
                showCross = true;
                break;

            default:
                showDot = true;
                break;
        }

        if (fixDot  != null) fixDot.SetActive(showDot);
        if (fixRing != null) fixRing.SetActive(showRing);
        if (fixHArm != null) fixHArm.SetActive(showCross);
        if (fixVArm != null) fixVArm.SetActive(showCross);

        // ---- Sizes ----
        float mPerDeg = spec.GetMetersPerDegree();

        float dotDiam_m = Mathf.Max(1e-4f, 2f * spec.fixationDotRadius_deg * mPerDeg);
        SetUniformScale(fixDot, dotDiam_m);

        float rIn_m  = Mathf.Max(0f, spec.fixationRingInnerRadius_deg) * mPerDeg;
        float t_m    = Mathf.Max(1e-4f, spec.fixationRingThickness_deg) * mPerDeg;
        float rOut_m = rIn_m + t_m;

        if (fixRing != null)
        {
            // Cylinder axis is Y by default; rotate so it faces camera
            fixRing.transform.localRotation = Quaternion.Euler(90f, 0f, 0f);
            fixRing.transform.localScale = new Vector3(2f * rOut_m, 2f * rOut_m, t_m);
        }

        float armHalfLen_m = Mathf.Max(1e-4f, spec.fixationCrosshairArmLength_deg) * mPerDeg;
        float armThick_m   = Mathf.Max(1e-4f, spec.fixationCrosshairThickness_deg) * mPerDeg;

        if (fixHArm != null)
            fixHArm.transform.localScale = new Vector3(2f * armHalfLen_m, armThick_m, armThick_m);

        if (fixVArm != null)
            fixVArm.transform.localScale = new Vector3(armThick_m, 2f * armHalfLen_m, armThick_m);

        // ---- Color ----
        ApplyUnlitColor(fixDot,  spec.fixationColor);
        ApplyUnlitColor(fixRing, spec.fixationColor);
        ApplyUnlitColor(fixHArm, spec.fixationColor);
        ApplyUnlitColor(fixVArm, spec.fixationColor);

        EnableRenderer(fixDot);
        EnableRenderer(fixRing);
        EnableRenderer(fixHArm);
        EnableRenderer(fixVArm);

        Debug.Log($"[FixationController] Applied style={spec.fixationStyle} directParentIsCamera={directParentIsCamera} localPos={transform.localPosition} viewDist={spec.viewDistance_m} mPerDeg={mPerDeg} dotDiam_m={dotDiam_m}", this);
    }

    private void EnsureChildrenExist()
    {
        if (fixDot == null)  fixDot  = FindOrCreateChild("FixDot",  PrimitiveType.Sphere);
        if (fixRing == null) fixRing = FindOrCreateChild("FixRing", PrimitiveType.Cylinder);
        if (fixHArm == null) fixHArm = FindOrCreateChild("FixHArm", PrimitiveType.Cube);
        if (fixVArm == null) fixVArm = FindOrCreateChild("FixVArm", PrimitiveType.Cube);

        if (fixDot  != null) fixDot.transform.localPosition  = Vector3.zero;
        if (fixRing != null) fixRing.transform.localPosition = Vector3.zero;
        if (fixHArm != null) fixHArm.transform.localPosition = Vector3.zero;
        if (fixVArm != null) fixVArm.transform.localPosition = Vector3.zero;
    }

    private GameObject FindOrCreateChild(string childName, PrimitiveType prim)
    {
        Transform t = transform.Find(childName);
        if (t != null) return t.gameObject;

        var go = GameObject.CreatePrimitive(prim);
        go.name = childName;
        go.transform.SetParent(transform, false);
        return go;
    }

    private static void SetUniformScale(GameObject go, float s)
    {
        if (go == null) return;
        go.transform.localScale = new Vector3(s, s, s);
    }

    private static void EnableRenderer(GameObject go)
    {
        if (go == null) return;
        var r = go.GetComponent<Renderer>();
        if (r != null) r.enabled = true;
    }

    private static void ApplyUnlitColor(GameObject go, Color c)
    {
        if (go == null) return;
        var r = go.GetComponent<Renderer>();
        if (r == null) return;

        Shader sh =
            Shader.Find("Universal Render Pipeline/Unlit")
            ?? Shader.Find("Unlit/Color")
            ?? Shader.Find("Standard");

        if (sh == null) return;

        var m = new Material(sh);
        if (m.HasProperty("_BaseColor")) m.SetColor("_BaseColor", c);
        if (m.HasProperty("_Color"))     m.SetColor("_Color", c);

        if (m.HasProperty("_EmissionColor"))
        {
            m.EnableKeyword("_EMISSION");
            m.SetColor("_EmissionColor", c);
        }

        r.material = m;
    }

    private static void SetLayerRecursively(GameObject go, int layer)
    {
        if (go == null) return;
        go.layer = layer;
        foreach (Transform c in go.transform)
            SetLayerRecursively(c.gameObject, layer);
    }

    private static int ComputeSig(ExperimentSpec s)
    {
        unchecked
        {
            int h = 17;
            h = h * 31 + (int)s.fixationStyle;
            h = h * 31 + s.fixationDotRadius_deg.GetHashCode();
            h = h * 31 + s.fixationRingInnerRadius_deg.GetHashCode();
            h = h * 31 + s.fixationRingThickness_deg.GetHashCode();
            h = h * 31 + s.fixationCrosshairArmLength_deg.GetHashCode();
            h = h * 31 + s.fixationCrosshairThickness_deg.GetHashCode();
            h = h * 31 + s.fixationColor.GetHashCode();
            h = h * 31 + s.viewDistance_m.GetHashCode();
            return h;
        }
    }
}