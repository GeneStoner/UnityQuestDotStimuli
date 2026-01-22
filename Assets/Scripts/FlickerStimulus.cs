// FILE: FlickerStimulus.cs
//
// Renders a flickering annulus for heterochromatic flicker photometry (HFP).
// Uses SmoothCircle shader with inner/outer radius for the ring shape.
//
using UnityEngine;

[RequireComponent(typeof(MeshRenderer))]
[RequireComponent(typeof(MeshFilter))]
public class FlickerStimulus : MonoBehaviour
{
    [Header("Geometry (visual angle)")]
    [Tooltip("Inner radius of annulus in degrees of visual angle.")]
    public float innerRadiusDeg = 0.5f;

    [Tooltip("Outer radius of annulus in degrees of visual angle.")]
    public float outerRadiusDeg = 2.0f;

    [Tooltip("Viewing distance in meters (for visual angle calculation).")]
    public float viewDistanceMeters = 2.0f;

    [Header("Flicker Settings")]
    [Tooltip("Flicker rate in Hz (cycles per second). 15-25 Hz typical for HFP.")]
    [Range(5f, 60f)]
    public float flickerRateHz = 20f;

    [Tooltip("If true, flicker is active. If false, shows current color statically.")]
    public bool flickerEnabled = true;

    [Header("Colors")]
    public Color colorA = new Color(1.0f, 0f, 0f, 1f);  // Red (max intensity)
    public Color colorB = new Color(0f, 0.5f, 0f, 1f);  // Green (adjustable)

    [Header("Shader Settings")]
    [Tooltip("Edge smoothness for anti-aliasing.")]
    [Range(0.001f, 0.1f)]
    public float edgeSmoothness = 0.01f;

    // Runtime
    private Material _material;
    private MeshRenderer _renderer;
    private bool _showingColorA = true;
    private float _lastFlipTime;

    // Shader property IDs (cached for performance)
    private static readonly int ColorProp = Shader.PropertyToID("_Color");
    private static readonly int InnerRadiusProp = Shader.PropertyToID("_InnerRadius");
    private static readonly int OuterRadiusProp = Shader.PropertyToID("_OuterRadius");
    private static readonly int SmoothnessProp = Shader.PropertyToID("_Smoothness");

    void Awake()
    {
        _renderer = GetComponent<MeshRenderer>();
        SetupMaterial();
        SetupGeometry();
    }

    void Start()
    {
        _lastFlipTime = Time.time;
        UpdateShaderProperties();
    }

    void Update()
    {
        if (!flickerEnabled) return;

        float halfPeriod = 0.5f / flickerRateHz;

        if (Time.time - _lastFlipTime >= halfPeriod)
        {
            _showingColorA = !_showingColorA;
            _material.SetColor(ColorProp, _showingColorA ? colorA : colorB);
            _lastFlipTime = Time.time;
        }
    }

    /// <summary>
    /// Set up the material using SmoothCircle shader.
    /// </summary>
    private void SetupMaterial()
    {
        Shader shader = Shader.Find("Custom/SmoothCircle");
        if (shader == null)
        {
            Debug.LogError("[FlickerStimulus] Could not find Custom/SmoothCircle shader!");
            shader = Shader.Find("Unlit/Color");
        }

        _material = new Material(shader);
        _renderer.material = _material;
    }

    /// <summary>
    /// Set up quad geometry sized for the visual angle.
    /// </summary>
    private void SetupGeometry()
    {
        // Ensure we have a quad mesh
        MeshFilter mf = GetComponent<MeshFilter>();
        if (mf.sharedMesh == null || mf.sharedMesh.name != "Quad")
        {
            // Create a simple quad if not already present
            mf.mesh = CreateQuadMesh();
        }

        // Scale quad to cover the outer radius in visual angle
        // Visual angle to size: size = 2 * distance * tan(angle/2)
        // For small angles: size ≈ distance * angle_radians
        float outerRadiusRad = outerRadiusDeg * Mathf.Deg2Rad;
        float quadSize = 2f * viewDistanceMeters * Mathf.Tan(outerRadiusRad);

        // Quad needs to be large enough that outer radius (0.5 in UV) maps to actual size
        // Since UV outer radius is at 0.5 from center, quad width = 2 * outerSize
        transform.localScale = new Vector3(quadSize, quadSize, 1f);
    }

    /// <summary>
    /// Call after changing geometry properties at runtime to refresh the display.
    /// </summary>
    public void RefreshGeometry()
    {
        SetupGeometry();
        UpdateShaderProperties();
    }

    /// <summary>
    /// Update shader properties (call after changing radii).
    /// </summary>
    public void UpdateShaderProperties()
    {
        if (_material == null) return;

        // Convert degree radii to UV space (0-0.5 range)
        // Inner/outer as fraction of the quad (which spans the outer radius)
        float innerUV = (innerRadiusDeg / outerRadiusDeg) * 0.5f;
        float outerUV = 0.5f;  // Outer edge at UV boundary

        _material.SetFloat(InnerRadiusProp, innerUV);
        _material.SetFloat(OuterRadiusProp, outerUV);
        _material.SetFloat(SmoothnessProp, edgeSmoothness);
        _material.SetColor(ColorProp, _showingColorA ? colorA : colorB);
    }

    /// <summary>
    /// Set colors for flicker.
    /// </summary>
    public void SetColors(Color red, Color green)
    {
        colorA = red;
        colorB = green;
        if (_material != null)
        {
            _material.SetColor(ColorProp, _showingColorA ? colorA : colorB);
        }
    }

    /// <summary>
    /// Set the green intensity (for calibration adjustment).
    /// </summary>
    public void SetGreenIntensity(float intensity)
    {
        colorB = new Color(0f, intensity, 0f, 1f);
    }

    /// <summary>
    /// Set the red intensity.
    /// </summary>
    public void SetRedIntensity(float intensity)
    {
        colorA = new Color(intensity, 0f, 0f, 1f);
    }

    /// <summary>
    /// Get current green intensity.
    /// </summary>
    public float GetGreenIntensity()
    {
        return colorB.g;
    }

    /// <summary>
    /// Create a simple quad mesh.
    /// </summary>
    private Mesh CreateQuadMesh()
    {
        Mesh mesh = new Mesh();
        mesh.name = "FlickerQuad";

        mesh.vertices = new Vector3[]
        {
            new Vector3(-0.5f, -0.5f, 0),
            new Vector3( 0.5f, -0.5f, 0),
            new Vector3( 0.5f,  0.5f, 0),
            new Vector3(-0.5f,  0.5f, 0)
        };

        mesh.uv = new Vector2[]
        {
            new Vector2(0, 0),
            new Vector2(1, 0),
            new Vector2(1, 1),
            new Vector2(0, 1)
        };

        mesh.triangles = new int[] { 0, 2, 1, 0, 3, 2 };
        mesh.RecalculateNormals();

        return mesh;
    }

    /// <summary>
    /// Force show a specific color (for debugging).
    /// </summary>
    public void ForceColor(bool showColorA)
    {
        _showingColorA = showColorA;
        if (_material != null)
        {
            _material.SetColor(ColorProp, _showingColorA ? colorA : colorB);
        }
    }

    void OnValidate()
    {
        // Update when Inspector values change
        if (_material != null)
        {
            SetupGeometry();
            UpdateShaderProperties();
        }
    }

    void OnDestroy()
    {
        if (_material != null)
        {
            Destroy(_material);
        }
    }
}
