// FILE: SquareFixationTarget.cs
// Square bullseye fixation target - sharp edges, no anti-aliasing needed
using UnityEngine;

[ExecuteInEditMode]
public class SquareFixationTarget : MonoBehaviour
{
    [Header("Geometry Source")]
    [Tooltip("If assigned, pulls geometry from ExperimentSpec. Otherwise uses manual values below.")]
    public ExperimentSpec spec;

    [Header("Manual Geometry (used if spec is null)")]
    public float viewDistance_m = 2.0f;
    public float outerSize_deg = 0.6f;
    public float innerSize_deg = 0.3f;
    public float crosshairThickness_deg = 0.12f;

    [Header("Appearance")]
    public Color outerColor = Color.white;
    public Color innerColor = Color.black;
    public Color crosshairColor = Color.black;

    [Header("Options")]
    public bool showCrosshairs = true;

    [Header("Preview Scale (for monitor testing)")]
    [Min(0.1f)]
    public float previewScale = 1f;

    [Header("Z Offsets (smaller = closer to camera)")]
    public float zOuter = 0f;
    public float zInner = -0.0005f;
    public float zCrosshair = -0.001f;

    // Runtime objects
    private GameObject _outerSquare;
    private GameObject _innerSquare;
    private GameObject _hCrosshair;
    private GameObject _vCrosshair;

    private Material _outerMaterial;
    private Material _innerMaterial;
    private Material _crosshairMaterialH;
    private Material _crosshairMaterialV;

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

    void CreateFixation()
    {
        Shader unlitShader = Shader.Find("Universal Render Pipeline/Unlit");
        if (unlitShader == null)
            unlitShader = Shader.Find("Unlit/Color");

        if (unlitShader == null)
        {
            Debug.LogError("[SquareFixationTarget] Could not find Unlit shader!");
            return;
        }

        _outerMaterial = new Material(unlitShader) { name = "OuterMat" };
        _innerMaterial = new Material(unlitShader) { name = "InnerMat" };
        _crosshairMaterialH = new Material(unlitShader) { name = "CrosshairH" };
        _crosshairMaterialV = new Material(unlitShader) { name = "CrosshairV" };

        _outerSquare = CreateQuad("OuterSquare", _outerMaterial);
        _innerSquare = CreateQuad("InnerSquare", _innerMaterial);
        _hCrosshair = CreateQuad("HCrosshair", _crosshairMaterialH);
        _vCrosshair = CreateQuad("VCrosshair", _crosshairMaterialV);

        UpdateFixation();
    }

    void DestroyFixation()
    {
        SafeDestroy(_outerSquare);
        SafeDestroy(_innerSquare);
        SafeDestroy(_hCrosshair);
        SafeDestroy(_vCrosshair);

        SafeDestroy(_outerMaterial);
        SafeDestroy(_innerMaterial);
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

        var col = go.GetComponent<Collider>();
        if (col != null) SafeDestroy(col);

        var renderer = go.GetComponent<MeshRenderer>();
        renderer.sharedMaterial = mat;
        renderer.shadowCastingMode = UnityEngine.Rendering.ShadowCastingMode.Off;
        renderer.receiveShadows = false;

        return go;
    }

    void SetMaterialColor(Material mat, Color color)
    {
        if (mat.HasProperty("_BaseColor"))
            mat.SetColor("_BaseColor", color);
        else
            mat.SetColor("_Color", color);
    }

    void UpdateFixation()
    {
        if (_outerSquare == null || _outerMaterial == null) return;

        // Get geometry values
        float viewDist, outerSz_deg, innerSz_deg, crossThk_deg;

        if (spec != null)
        {
            viewDist = spec.viewDistance_m;
            // Use ring outer diameter for outer square
            float innerDiam_deg = spec.fixationRingInnerRadius_deg * 2f;
            outerSz_deg = innerDiam_deg + spec.fixationRingThickness_deg * 2f;
            // Use dot diameter for inner square
            innerSz_deg = spec.fixationDotRadius_deg * 2f;
            crossThk_deg = spec.fixationCrosshairThickness_deg;
        }
        else
        {
            viewDist = viewDistance_m;
            outerSz_deg = outerSize_deg;
            innerSz_deg = innerSize_deg;
            crossThk_deg = crosshairThickness_deg;
        }

        float mPerDeg = viewDist * Mathf.Deg2Rad;
        float scale = Mathf.Max(0.1f, previewScale);

        float outerSz_m = outerSz_deg * mPerDeg * scale;
        float innerSz_m = innerSz_deg * mPerDeg * scale;
        float crossThk_m = crossThk_deg * mPerDeg * scale;

        // Outer square (white)
        _outerSquare.transform.localPosition = new Vector3(0, 0, zOuter);
        _outerSquare.transform.localScale = new Vector3(outerSz_m, outerSz_m, 1f);
        _outerSquare.transform.localRotation = Quaternion.identity;
        SetMaterialColor(_outerMaterial, outerColor);

        // Inner square (black) - covers center
        _innerSquare.transform.localPosition = new Vector3(0, 0, zInner);
        _innerSquare.transform.localScale = new Vector3(innerSz_m, innerSz_m, 1f);
        _innerSquare.transform.localRotation = Quaternion.identity;
        SetMaterialColor(_innerMaterial, innerColor);

        // Crosshairs
        _hCrosshair.SetActive(showCrosshairs);
        _vCrosshair.SetActive(showCrosshairs);

        if (showCrosshairs)
        {
            // Horizontal crosshair - spans outer size
            _hCrosshair.transform.localPosition = new Vector3(0, 0, zCrosshair);
            _hCrosshair.transform.localScale = new Vector3(outerSz_m, crossThk_m, 1f);
            _hCrosshair.transform.localRotation = Quaternion.identity;
            SetMaterialColor(_crosshairMaterialH, crosshairColor);

            // Vertical crosshair
            _vCrosshair.transform.localPosition = new Vector3(0, 0, zCrosshair);
            _vCrosshair.transform.localScale = new Vector3(crossThk_m, outerSz_m, 1f);
            _vCrosshair.transform.localRotation = Quaternion.identity;
            SetMaterialColor(_crosshairMaterialV, crosshairColor);
        }
    }
}
