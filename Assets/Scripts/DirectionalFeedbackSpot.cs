// FILE: DirectionalFeedbackSpot.cs
// Animates a spot from center outward to show the direction of subject's response
using UnityEngine;
using UnityEngine.InputSystem;

public class DirectionalFeedbackSpot : MonoBehaviour
{
    [Header("Geometry")]
    [Tooltip("Viewing distance for degree-to-meter conversion")]
    public float viewDistance_m = 2.0f;

    [Tooltip("If assigned, uses viewDistance_m from spec")]
    public ExperimentSpec spec;

    [Header("Spot Appearance")]
    [Tooltip("Diameter of the feedback spot in degrees")]
    public float spotDiameter_deg = 0.3f;

    public Color spotColor = Color.white;

    [Header("Animation")]
    [Tooltip("How far the spot travels from center (degrees)")]
    public float travelDistance_deg = 10f;

    [Tooltip("Duration of the animation in seconds")]
    public float animationDuration_s = 0.4f;

    [Tooltip("Easing: 0 = linear, 1 = ease out (decelerate)")]
    [Range(0f, 1f)]
    public float easeOut = 0.5f;

    [Header("Audio Feedback")]
    [Tooltip("If true, generates a procedural click sound (no audio file needed)")]
    public bool useProceduralClick = true;

    [Tooltip("Audio clip to play when spot crosses threshold (only used if useProceduralClick is false)")]
    public AudioClip clickSound;

    [Tooltip("Distance from center (degrees) at which to play click")]
    public float clickThreshold_deg = 8f;

    [Tooltip("Volume of the click sound")]
    [Range(0f, 1f)]
    public float clickVolume = 0.5f;

    [Tooltip("Frequency of procedural click in Hz")]
    public float clickFrequency = 1000f;

    [Tooltip("Duration of procedural click in seconds")]
    public float clickDuration = 0.05f;

    [Header("Preview Scale (for monitor testing)")]
    [Min(0.1f)]
    public float previewScale = 1f;

    [Header("XR Input (for real-time tracking)")]
    [Tooltip("Input Action Asset for XR controller bindings")]
    public InputActionAsset xrInputActions;

    [Tooltip("Thumbstick deadzone")]
    [Range(0.1f, 0.9f)]
    public float thumbstickDeadzone = 0.3f;

    // Runtime
    private GameObject _spotQuad;
    private Material _spotMaterial;
    private AudioSource _audioSource;

    private bool _isAnimating = false;
    private float _animationStartTime;
    private Vector2 _direction;
    private bool _clickPlayed;

    // Real-time tracking mode
    private bool _isTracking = false;
    private bool _clickPlayedThisWindow = false;

    // XR Input
    private InputAction _thumbstickLeft;
    private InputAction _thumbstickRight;

    private static readonly int ColorId = Shader.PropertyToID("_Color");
    private static readonly int InnerRadiusId = Shader.PropertyToID("_InnerRadius");
    private static readonly int OuterRadiusId = Shader.PropertyToID("_OuterRadius");
    private static readonly int SmoothnessId = Shader.PropertyToID("_Smoothness");

    // 8-way direction vectors (matching choiceIndex convention)
    // 0=Up, 1=UpRight, 2=Right, 3=DownRight, 4=Down, 5=DownLeft, 6=Left, 7=UpLeft
    private static readonly Vector2[] DirectionVectors = new Vector2[]
    {
        new Vector2(0, 1),           // 0: Up
        new Vector2(0.707f, 0.707f), // 1: UpRight
        new Vector2(1, 0),           // 2: Right
        new Vector2(0.707f, -0.707f),// 3: DownRight
        new Vector2(0, -1),          // 4: Down
        new Vector2(-0.707f, -0.707f),// 5: DownLeft
        new Vector2(-1, 0),          // 6: Left
        new Vector2(-0.707f, 0.707f) // 7: UpLeft
    };

    void Awake()
    {
        CreateSpot();
        SetupAudio();
        SetupXRInput();
    }

    void OnDestroy()
    {
        if (_spotQuad != null)
            SafeDestroy(_spotQuad);
        if (_spotMaterial != null)
            SafeDestroy(_spotMaterial);
        CleanupXRInput();
    }

    void OnEnable()
    {
        if (_thumbstickLeft != null) _thumbstickLeft.Enable();
        if (_thumbstickRight != null) _thumbstickRight.Enable();
    }

    void OnDisable()
    {
        if (_thumbstickLeft != null) _thumbstickLeft.Disable();
        if (_thumbstickRight != null) _thumbstickRight.Disable();
    }

    void Update()
    {
        // Real-time tracking mode - read thumbstick and update position
        if (_isTracking)
        {
            Vector2 thumbstick = GetThumbstickValue();
            UpdateTracking(thumbstick, thumbstickDeadzone);
            return;
        }

        if (!_isAnimating) return;

        float elapsed = Time.time - _animationStartTime;
        float t = Mathf.Clamp01(elapsed / animationDuration_s);

        // Apply easing
        float easedT = Mathf.Lerp(t, 1f - Mathf.Pow(1f - t, 2f), easeOut);

        // Calculate current position
        float currentDistance_deg = easedT * travelDistance_deg;
        UpdateSpotPosition(currentDistance_deg);

        // Check for click threshold
        if (!_clickPlayed && currentDistance_deg >= clickThreshold_deg)
        {
            PlayClick();
            _clickPlayed = true;
        }

        // End animation
        if (t >= 1f)
        {
            _isAnimating = false;
            _spotQuad.SetActive(false);
        }
    }

    /// <summary>
    /// Show feedback for the given direction choice (0-7) - animated version (post-response)
    /// </summary>
    public void ShowFeedback(int choiceIndex)
    {
        if (choiceIndex < 0 || choiceIndex > 7)
        {
            Debug.LogWarning($"[DirectionalFeedbackSpot] Invalid choiceIndex: {choiceIndex}");
            return;
        }

        _direction = DirectionVectors[choiceIndex];
        _animationStartTime = Time.time;
        _isAnimating = true;
        _clickPlayed = false;

        // Start at center
        UpdateSpotPosition(0f);
        _spotQuad.SetActive(true);
    }

    /// <summary>
    /// Begin real-time tracking mode (call when response window opens)
    /// </summary>
    public void BeginTracking()
    {
        _isTracking = true;
        _isAnimating = false;
        _clickPlayedThisWindow = false;

        if (_spotQuad != null)
        {
            UpdateSpotPosition(0f);
            _spotQuad.SetActive(true);
        }
    }

    /// <summary>
    /// Update spot position based on thumbstick input (call each frame during response window)
    /// </summary>
    /// <param name="thumbstick">Raw thumbstick Vector2 (-1 to 1 on each axis)</param>
    /// <param name="deadzone">Thumbstick deadzone (magnitude below this = center)</param>
    public void UpdateTracking(Vector2 thumbstick, float deadzone = 0.2f)
    {
        if (!_isTracking || _spotQuad == null) return;

        float magnitude = thumbstick.magnitude;

        if (magnitude < deadzone)
        {
            // Below deadzone - hide or show at center
            UpdateSpotPositionDirect(Vector2.zero, 0f);
            _spotQuad.SetActive(false);
            return;
        }

        _spotQuad.SetActive(true);

        // Normalize direction
        Vector2 direction = thumbstick.normalized;

        // Map magnitude (deadzone to 1) → (0 to travelDistance)
        float normalizedMag = Mathf.InverseLerp(deadzone, 1f, magnitude);
        float distance_deg = normalizedMag * travelDistance_deg;

        UpdateSpotPositionDirect(direction, distance_deg);

        // Play click when crossing threshold (only once per window)
        if (!_clickPlayedThisWindow && distance_deg >= clickThreshold_deg)
        {
            PlayClick();
            _clickPlayedThisWindow = true;
        }
        // Reset click if they pull back below threshold
        else if (_clickPlayedThisWindow && distance_deg < clickThreshold_deg * 0.8f)
        {
            _clickPlayedThisWindow = false;
        }
    }

    /// <summary>
    /// End tracking mode (call when response window closes)
    /// </summary>
    public void EndTracking()
    {
        _isTracking = false;
        if (_spotQuad != null)
            _spotQuad.SetActive(false);
    }

    /// <summary>
    /// Immediately hide the feedback spot
    /// </summary>
    public void Hide()
    {
        _isAnimating = false;
        _isTracking = false;
        if (_spotQuad != null)
            _spotQuad.SetActive(false);
    }

    void UpdateSpotPositionDirect(Vector2 direction, float distance_deg)
    {
        if (_spotQuad == null) return;

        float viewDist = spec != null ? spec.viewDistance_m : viewDistance_m;
        float mPerDeg = viewDist * Mathf.Deg2Rad;
        float scale = Mathf.Max(0.1f, previewScale);

        // Spot size
        float spotSize_m = spotDiameter_deg * mPerDeg * scale;
        _spotQuad.transform.localScale = new Vector3(spotSize_m, spotSize_m, 1f);

        // Position
        float distance_m = distance_deg * mPerDeg * scale;
        Vector3 pos = new Vector3(
            direction.x * distance_m,
            direction.y * distance_m,
            -0.001f
        );
        _spotQuad.transform.localPosition = pos;

        _spotMaterial.SetColor(ColorId, spotColor);
    }

    void CreateSpot()
    {
        Shader circleShader = Shader.Find("Custom/SmoothCircle");
        if (circleShader == null)
        {
            Debug.LogError("[DirectionalFeedbackSpot] Custom/SmoothCircle shader not found!");
            return;
        }

        _spotMaterial = new Material(circleShader) { name = "FeedbackSpotMat" };

        _spotQuad = GameObject.CreatePrimitive(PrimitiveType.Quad);
        _spotQuad.name = "FeedbackSpot";
        _spotQuad.transform.SetParent(transform, false);

        // Remove collider
        var col = _spotQuad.GetComponent<Collider>();
        if (col != null) SafeDestroy(col);

        var renderer = _spotQuad.GetComponent<MeshRenderer>();
        renderer.sharedMaterial = _spotMaterial;
        renderer.shadowCastingMode = UnityEngine.Rendering.ShadowCastingMode.Off;
        renderer.receiveShadows = false;

        // Configure as filled circle
        _spotMaterial.SetColor(ColorId, spotColor);
        _spotMaterial.SetFloat(InnerRadiusId, 0f);
        _spotMaterial.SetFloat(OuterRadiusId, 0.5f);
        _spotMaterial.SetFloat(SmoothnessId, 0.03f);

        _spotQuad.SetActive(false);
    }

    void SetupAudio()
    {
        _audioSource = gameObject.AddComponent<AudioSource>();
        _audioSource.playOnAwake = false;
        _audioSource.spatialBlend = 0f; // 2D sound

        // Generate procedural click if enabled
        if (useProceduralClick)
        {
            clickSound = GenerateClickSound();
        }
    }

    AudioClip GenerateClickSound()
    {
        int sampleRate = 44100;
        int sampleCount = Mathf.RoundToInt(clickDuration * sampleRate);

        float[] samples = new float[sampleCount];

        for (int i = 0; i < sampleCount; i++)
        {
            float t = (float)i / sampleRate;

            // Sine wave at click frequency
            float wave = Mathf.Sin(2f * Mathf.PI * clickFrequency * t);

            // Envelope: quick attack, exponential decay for a nice "tick"
            float envelope = Mathf.Exp(-t * 60f); // Fast decay

            // Add a bit of higher harmonic for "click" character
            float harmonic = Mathf.Sin(2f * Mathf.PI * clickFrequency * 2.5f * t) * 0.3f;

            samples[i] = (wave + harmonic) * envelope;
        }

        AudioClip clip = AudioClip.Create("ProceduralClick", sampleCount, 1, sampleRate, false);
        clip.SetData(samples, 0);

        return clip;
    }

    void UpdateSpotPosition(float distance_deg)
    {
        if (_spotQuad == null) return;

        float viewDist = spec != null ? spec.viewDistance_m : viewDistance_m;
        float mPerDeg = viewDist * Mathf.Deg2Rad;
        float scale = Mathf.Max(0.1f, previewScale);

        // Spot size
        float spotSize_m = spotDiameter_deg * mPerDeg * scale;
        _spotQuad.transform.localScale = new Vector3(spotSize_m, spotSize_m, 1f);

        // Position based on direction and current distance
        float distance_m = distance_deg * mPerDeg * scale;
        Vector3 pos = new Vector3(
            _direction.x * distance_m,
            _direction.y * distance_m,
            -0.001f // Slightly in front
        );
        _spotQuad.transform.localPosition = pos;

        // Update color in case it changed
        _spotMaterial.SetColor(ColorId, spotColor);
    }

    void PlayClick()
    {
        if (clickSound != null && _audioSource != null)
        {
            _audioSource.PlayOneShot(clickSound, clickVolume);
        }
    }

    void SetupXRInput()
    {
        if (xrInputActions == null) return;

        var leftMap = xrInputActions.FindActionMap("XRI Left", false);
        var rightMap = xrInputActions.FindActionMap("XRI Right", false);

        if (leftMap != null)
        {
            _thumbstickLeft = leftMap.FindAction("Thumbstick", false);
            if (_thumbstickLeft != null)
                _thumbstickLeft.Enable();
        }

        if (rightMap != null)
        {
            _thumbstickRight = rightMap.FindAction("Thumbstick", false);
            if (_thumbstickRight != null)
                _thumbstickRight.Enable();
        }
    }

    void CleanupXRInput()
    {
        if (_thumbstickLeft != null) _thumbstickLeft.Disable();
        if (_thumbstickRight != null) _thumbstickRight.Disable();
    }

    Vector2 GetThumbstickValue()
    {
        Vector2 result = Vector2.zero;

        // Get the larger magnitude from either hand
        if (_thumbstickLeft != null)
        {
            Vector2 left = _thumbstickLeft.ReadValue<Vector2>();
            if (left.magnitude > result.magnitude)
                result = left;
        }

        if (_thumbstickRight != null)
        {
            Vector2 right = _thumbstickRight.ReadValue<Vector2>();
            if (right.magnitude > result.magnitude)
                result = right;
        }

        return result;
    }

    void SafeDestroy(Object obj)
    {
        if (obj == null) return;
        if (Application.isPlaying)
            Destroy(obj);
        else
            DestroyImmediate(obj);
    }
}
