// FILE: VisualAngleRuler.cs
// Visual angle calibration ruler for verifying stimulus sizing
using UnityEngine;
using TMPro;

[ExecuteInEditMode]
public class VisualAngleRuler : MonoBehaviour
{
    [Header("Geometry")]
    [Tooltip("If assigned, uses viewDistance_m from spec")]
    public ExperimentSpec spec;

    [Tooltip("Manual viewing distance if spec is null")]
    public float viewDistance_m = 2.0f;

    [Header("Ruler Settings")]
    [Tooltip("Total span in degrees (e.g., 60 means ±30°)")]
    public float totalSpan_deg = 60f;

    [Tooltip("Major tick interval in degrees")]
    public float majorTickInterval_deg = 10f;

    [Tooltip("Minor tick interval in degrees (0 to disable)")]
    public float minorTickInterval_deg = 5f;

    [Header("Appearance")]
    public float lineThickness_m = 0.002f;
    public float majorTickHeight_m = 0.02f;
    public float minorTickHeight_m = 0.01f;
    public Color rulerColor = Color.white;

    [Header("Labels")]
    public bool showLabels = true;
    public float labelSize = 0.015f;
    public float labelOffset_m = 0.005f;

    [Header("Orientation")]
    public bool horizontal = true;

    [Header("Preview Scale (for monitor testing)")]
    [Min(0.1f)]
    public float previewScale = 1f;

    // Runtime
    private GameObject _lineObject;
    private GameObject _tickContainer;
    private Material _lineMaterial;

    void OnEnable()
    {
        CreateRuler();
    }

    void OnDisable()
    {
        DestroyRuler();
    }

    void OnValidate()
    {
        if (isActiveAndEnabled)
        {
            #if UNITY_EDITOR
            UnityEditor.EditorApplication.delayCall += () =>
            {
                if (this != null && isActiveAndEnabled)
                    UpdateRuler();
            };
            #else
            UpdateRuler();
            #endif
        }
    }

    public void Refresh()
    {
        UpdateRuler();
    }

    void CreateRuler()
    {
        // Create material
        Shader unlitShader = Shader.Find("Universal Render Pipeline/Unlit");
        if (unlitShader == null)
            unlitShader = Shader.Find("Unlit/Color");

        _lineMaterial = new Material(unlitShader);
        _lineMaterial.name = "RulerMat";

        // Container for ticks
        _tickContainer = new GameObject("Ticks");
        _tickContainer.transform.SetParent(transform, false);

        UpdateRuler();
    }

    void DestroyRuler()
    {
        if (_lineObject != null)
            SafeDestroy(_lineObject);
        if (_tickContainer != null)
            SafeDestroy(_tickContainer);
        if (_lineMaterial != null)
            SafeDestroy(_lineMaterial);
    }

    void SafeDestroy(Object obj)
    {
        if (obj == null) return;
        if (Application.isPlaying)
            Destroy(obj);
        else
            DestroyImmediate(obj);
    }

    void UpdateRuler()
    {
        if (_lineMaterial == null) return;

        // Clear existing ticks
        if (_tickContainer != null)
        {
            while (_tickContainer.transform.childCount > 0)
            {
                SafeDestroy(_tickContainer.transform.GetChild(0).gameObject);
            }
        }

        // Get viewing distance
        float viewDist = spec != null ? spec.viewDistance_m : viewDistance_m;
        float mPerDeg = viewDist * Mathf.Deg2Rad;
        float scale = Mathf.Max(0.1f, previewScale);

        // Calculate total length in meters
        float totalLength_m = totalSpan_deg * mPerDeg * scale;
        float halfSpan_deg = totalSpan_deg / 2f;

        // Set material color
        if (_lineMaterial.HasProperty("_BaseColor"))
            _lineMaterial.SetColor("_BaseColor", rulerColor);
        else
            _lineMaterial.SetColor("_Color", rulerColor);

        // Create main line
        if (_lineObject != null)
            SafeDestroy(_lineObject);

        _lineObject = CreateQuad("MainLine", _lineMaterial);

        if (horizontal)
        {
            _lineObject.transform.localScale = new Vector3(totalLength_m, lineThickness_m * scale, 1f);
        }
        else
        {
            _lineObject.transform.localScale = new Vector3(lineThickness_m * scale, totalLength_m, 1f);
        }
        _lineObject.transform.localPosition = Vector3.zero;

        // Create ticks
        // Major ticks
        for (float deg = -halfSpan_deg; deg <= halfSpan_deg + 0.001f; deg += majorTickInterval_deg)
        {
            CreateTick(deg, majorTickHeight_m * scale, mPerDeg * scale, true);
        }

        // Minor ticks
        if (minorTickInterval_deg > 0)
        {
            for (float deg = -halfSpan_deg; deg <= halfSpan_deg + 0.001f; deg += minorTickInterval_deg)
            {
                // Skip if this is also a major tick position
                if (Mathf.Abs(deg % majorTickInterval_deg) > 0.01f)
                {
                    CreateTick(deg, minorTickHeight_m * scale, mPerDeg * scale, false);
                }
            }
        }
    }

    void CreateTick(float deg, float height, float mPerDeg, bool isMajor)
    {
        float pos_m = deg * mPerDeg;

        var tick = CreateQuad($"Tick_{deg:F0}", _lineMaterial);
        tick.transform.SetParent(_tickContainer.transform, false);

        if (horizontal)
        {
            tick.transform.localScale = new Vector3(lineThickness_m * Mathf.Max(0.1f, previewScale), height, 1f);
            tick.transform.localPosition = new Vector3(pos_m, height / 2f, 0);
        }
        else
        {
            tick.transform.localScale = new Vector3(height, lineThickness_m * Mathf.Max(0.1f, previewScale), 1f);
            tick.transform.localPosition = new Vector3(height / 2f, pos_m, 0);
        }

        // Add label for major ticks
        if (isMajor && showLabels)
        {
            CreateLabel(deg, pos_m, height);
        }
    }

    void CreateLabel(float deg, float pos_m, float tickHeight)
    {
        var labelObj = new GameObject($"Label_{deg:F0}");
        labelObj.transform.SetParent(_tickContainer.transform, false);

        var tmp = labelObj.AddComponent<TextMeshPro>();
        tmp.text = $"{deg:F0}°";
        tmp.fontSize = labelSize * 1000f; // TMP uses different scale
        tmp.alignment = TextAlignmentOptions.Center;
        tmp.color = rulerColor;

        // Position below the tick
        float labelY = tickHeight + labelOffset_m * Mathf.Max(0.1f, previewScale);

        if (horizontal)
        {
            labelObj.transform.localPosition = new Vector3(pos_m, labelY + 0.01f, 0);
        }
        else
        {
            labelObj.transform.localPosition = new Vector3(labelY + 0.01f, pos_m, 0);
            labelObj.transform.localRotation = Quaternion.Euler(0, 0, 90);
        }

        // Scale to reasonable size
        labelObj.transform.localScale = Vector3.one * 0.01f * Mathf.Max(0.1f, previewScale);

        // Disable raycast
        tmp.raycastTarget = false;

        // Use RectTransform sizing
        var rt = labelObj.GetComponent<RectTransform>();
        rt.sizeDelta = new Vector2(100, 20);
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
}
