// FILE: FlickerCalibrator.cs
//
// Main controller for heterochromatic flicker photometry (HFP) calibration.
// Runs multiple trials where user adjusts green intensity until flicker is minimized.
// Averages results across trials to estimate isoluminance point.
//
// Controls:
//   Start trial:     Trigger (XR) or Space/Return (keyboard)
//   Adjust green:    Thumbstick Y-axis (XR) or Up/Down arrows (keyboard)
//   Confirm trial:   Trigger (XR) or Space/Return (keyboard)
//   Reset current:   R key
//
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.InputSystem;

[DisallowMultipleComponent]
public class FlickerCalibrator : MonoBehaviour
{
    [Header("References")]
    [Tooltip("The FlickerStimulus component that renders the annulus.")]
    public FlickerStimulus stimulus;

    [Tooltip("Optional: ExperimentSpec to read aperture size from.")]
    public ExperimentSpec experimentSpec;

    [Tooltip("Optional: Fixation controller for central fixation target.")]
    public Fixation_Controller fixation;

    [Header("Trial Settings")]
    [Tooltip("Number of calibration trials to run before averaging.")]
    [Range(1, 50)]
    public int numberOfTrials = 10;

    [Tooltip("Randomize starting green intensity each trial (within range).")]
    public bool randomizeStartingValue = true;

    [Header("Calibration Settings")]
    [Tooltip("Red intensity (fixed at maximum for reference).")]
    [Range(0.5f, 1f)]
    public float redIntensity = 1.0f;

    [Tooltip("Starting green intensity (adjustable). Randomized if randomizeStartingValue is true.")]
    [Range(0.1f, 1f)]
    public float greenIntensity = 0.5f;

    [Tooltip("Minimum green intensity allowed.")]
    [Range(0.05f, 0.5f)]
    public float greenMin = 0.1f;

    [Tooltip("Maximum green intensity allowed.")]
    [Range(0.5f, 1f)]
    public float greenMax = 1.0f;

    [Tooltip("Adjustment step per thumbstick input.")]
    [Range(0.001f, 0.05f)]
    public float adjustmentStep = 0.01f;

    [Tooltip("Thumbstick deadzone for adjustment input.")]
    [Range(0.1f, 0.9f)]
    public float thumbstickDeadzone = 0.3f;

    [Header("XR Controller Input")]
    [Tooltip("Input Action Asset containing XR controller bindings.")]
    public InputActionAsset xrInputActions;

    [Tooltip("Which hand's thumbstick to use for adjustment.")]
    public HandSelection adjustmentHand = HandSelection.Right;

    [Tooltip("Which hand's trigger to use for confirm.")]
    public HandSelection confirmHand = HandSelection.Either;

    public enum HandSelection { Left, Right, Either }

    [Header("UI")]
    [Tooltip("Show on-screen instructions and current value.")]
    public bool showHUD = true;

    // XR input
    private InputAction _thumbstickLeft;
    private InputAction _thumbstickRight;
    private InputAction _activateLeft;
    private InputAction _activateRight;

    // Trial state
    private enum State { WaitingToStart, Adjusting, BetweenTrials, AllDone }
    private State _state = State.WaitingToStart;
    private int _currentTrial = 0;
    private List<float> _trialResults = new List<float>();
    private float _averageGreen = 0f;
    private float _greenMedian = 0f;
    private float _greenStdDev = 0f;

    // End menu
    private int _endMenuSelection = 0;  // 0=Main Experiment, 1=Redo Calibration, 2=Quit
    private float _endMenuReadyTime = 0f;  // Time when menu becomes responsive
    private const float END_MENU_DELAY = 2.0f;  // 2 second delay before menu accepts input

    // Input state
    private bool _triggerPressedLastFrame = false;
    private float _lastAdjustmentTime = 0f;
    private const float ADJUSTMENT_COOLDOWN = 0.05f; // 50ms between adjustments

    // RNG for randomizing start values
    private System.Random _rng;

    void Awake()
    {
        _rng = new System.Random();
        SetupXRInput();
    }

    void Start()
    {
        // FORCE showHUD to true
        showHUD = true;
        Debug.Log($"[FlickerCalibrator] showHUD forced to TRUE");

        // FORCE red intensity to 1.0 (max) regardless of Inspector value
        redIntensity = 1.0f;
        Debug.Log($"[FlickerCalibrator] redIntensity forced to 1.0");

        // DEBUG: Log and enforce trial count
        Debug.Log($"[FlickerCalibrator] Inspector numberOfTrials = {numberOfTrials}");
        if (numberOfTrials > 10)
        {
            Debug.LogWarning($"[FlickerCalibrator] Forcing numberOfTrials from {numberOfTrials} to 10");
            numberOfTrials = 10;
        }

        // Apply stimulus size from ExperimentSpec if assigned
        ApplyStimulusSizeFromSpec();

        // Setup fixation target
        SetupFixation();

        // Apply initial colors (flicker disabled until trial starts)
        if (stimulus != null)
        {
            stimulus.SetRedIntensity(redIntensity);
            stimulus.SetGreenIntensity(greenIntensity);
            stimulus.flickerEnabled = false;
        }

        Debug.Log($"[FlickerCalibrator] Ready. {numberOfTrials} trials planned. showHUD={showHUD}");
        Debug.Log("[FlickerCalibrator] Press TRIGGER or SPACE to start first trial.");
    }

    void Update()
    {
        HandleInput();
    }

    private void HandleInput()
    {
        bool triggerPressed = IsTriggerPressed();
        bool keyConfirm = Input.GetKeyDown(KeyCode.Return) || Input.GetKeyDown(KeyCode.Space);
        bool confirmPressed = (triggerPressed && !_triggerPressedLastFrame) || keyConfirm;

        switch (_state)
        {
            case State.WaitingToStart:
                if (confirmPressed)
                {
                    StartNextTrial();
                }
                break;

            case State.Adjusting:
                HandleAdjustmentInput();
                if (confirmPressed)
                {
                    ConfirmCurrentTrial();
                }
                break;

            case State.BetweenTrials:
                if (confirmPressed)
                {
                    StartNextTrial();
                }
                break;

            case State.AllDone:
                // End menu navigation
                HandleEndMenuInput();
                break;
        }

        _triggerPressedLastFrame = triggerPressed;
    }

    private void HandleAdjustmentInput()
    {
        // --- Thumbstick adjustment ---
        Vector2 thumbstick = GetThumbstickValue();

        if (Mathf.Abs(thumbstick.y) > thumbstickDeadzone)
        {
            if (Time.time - _lastAdjustmentTime > ADJUSTMENT_COOLDOWN)
            {
                float delta = thumbstick.y > 0 ? adjustmentStep : -adjustmentStep;
                greenIntensity = Mathf.Clamp(greenIntensity + delta, greenMin, greenMax);
                UpdateStimulusColors();
                _lastAdjustmentTime = Time.time;
            }
        }

        // --- Keyboard fallback (up/down arrows, +/-) ---
        if (Input.GetKey(KeyCode.UpArrow) || Input.GetKey(KeyCode.KeypadPlus))
        {
            if (Time.time - _lastAdjustmentTime > ADJUSTMENT_COOLDOWN)
            {
                greenIntensity = Mathf.Clamp(greenIntensity + adjustmentStep, greenMin, greenMax);
                UpdateStimulusColors();
                _lastAdjustmentTime = Time.time;
            }
        }
        else if (Input.GetKey(KeyCode.DownArrow) || Input.GetKey(KeyCode.KeypadMinus))
        {
            if (Time.time - _lastAdjustmentTime > ADJUSTMENT_COOLDOWN)
            {
                greenIntensity = Mathf.Clamp(greenIntensity - adjustmentStep, greenMin, greenMax);
                UpdateStimulusColors();
                _lastAdjustmentTime = Time.time;
            }
        }

        // --- Reset to random starting value (R key) ---
        if (Input.GetKeyDown(KeyCode.R))
        {
            greenIntensity = GetRandomStartingGreen();
            UpdateStimulusColors();
            Debug.Log($"[FlickerCalibrator] Reset trial to: Green={greenIntensity:F3}");
        }
    }

    private void HandleEndMenuInput()
    {
        // Wait for delay before accepting any input
        if (Time.time < _endMenuReadyTime)
        {
            return;
        }

        // Thumbstick navigation
        Vector2 thumbstick = GetThumbstickValue();
        if (Mathf.Abs(thumbstick.y) > thumbstickDeadzone)
        {
            if (Time.time - _lastAdjustmentTime > 0.2f)  // Slower repeat for menu
            {
                if (thumbstick.y > 0)
                    _endMenuSelection = Mathf.Max(0, _endMenuSelection - 1);
                else
                    _endMenuSelection = Mathf.Min(2, _endMenuSelection + 1);
                _lastAdjustmentTime = Time.time;
            }
        }

        // Keyboard navigation
        if (Input.GetKeyDown(KeyCode.UpArrow))
            _endMenuSelection = Mathf.Max(0, _endMenuSelection - 1);
        if (Input.GetKeyDown(KeyCode.DownArrow))
            _endMenuSelection = Mathf.Min(2, _endMenuSelection + 1);

        // Trigger/key to select (only if trigger was released first)
        bool triggerPressed = IsTriggerPressed();
        bool keyConfirm = Input.GetKeyDown(KeyCode.Return) || Input.GetKeyDown(KeyCode.Space);

        if ((triggerPressed && !_triggerPressedLastFrame) || keyConfirm)
        {
            ExecuteEndMenuSelection();
        }
    }

    private void ExecuteEndMenuSelection()
    {
        Debug.Log($"[FlickerCalibrator] ExecuteEndMenuSelection called! selection={_endMenuSelection}");

        switch (_endMenuSelection)
        {
            case 0:  // Start Main Experiment
                Debug.Log("[FlickerCalibrator] >>> Loading main experiment via FlickerCalibrator menu <<<");
                UnityEngine.SceneManagement.SceneManager.LoadScene("UpToDateScene");
                break;

            case 1:  // Redo Calibration
                Debug.Log("[FlickerCalibrator] Restarting calibration...");
                _currentTrial = 0;
                _trialResults.Clear();
                _state = State.WaitingToStart;
                if (stimulus != null)
                {
                    stimulus.gameObject.SetActive(false);
                }
                break;

            case 2:  // Quit
                Debug.Log("[FlickerCalibrator] Quitting application...");
                Application.Quit();
                #if UNITY_EDITOR
                UnityEditor.EditorApplication.isPlaying = false;
                #endif
                break;
        }
    }

    private void StartNextTrial()
    {
        _currentTrial++;

        // Randomize starting green if enabled
        if (randomizeStartingValue)
        {
            greenIntensity = GetRandomStartingGreen();
        }

        // Show and enable flicker
        if (stimulus != null)
        {
            stimulus.gameObject.SetActive(true);
            stimulus.flickerEnabled = true;
            UpdateStimulusColors();
        }

        _state = State.Adjusting;
        Debug.Log($"[FlickerCalibrator] Trial {_currentTrial}/{numberOfTrials} started. Green={greenIntensity:F3}");
    }

    private void ConfirmCurrentTrial()
    {
        // Record this trial's result
        _trialResults.Add(greenIntensity);
        Debug.Log($"[FlickerCalibrator] Trial {_currentTrial}/{numberOfTrials} confirmed: Green={greenIntensity:F3}");

        // Hide stimulus between trials - show only fixation
        if (stimulus != null)
        {
            stimulus.flickerEnabled = false;
            stimulus.gameObject.SetActive(false);
        }

        if (_currentTrial >= numberOfTrials)
        {
            // All trials complete - compute average and save
            FinishCalibration();
        }
        else
        {
            _state = State.BetweenTrials;
            Debug.Log("[FlickerCalibrator] Press TRIGGER or SPACE for next trial.");
        }
    }

    private void FinishCalibration()
    {
        // Save calibration with all trial data
        var data = new CalibrationData
        {
            redIntensity = redIntensity,
            trialResults = new List<float>(_trialResults)
        };
        data.ComputeStatistics();  // Computes mean, median, stddev
        data.Save();

        _averageGreen = data.greenIntensity;
        _greenMedian = data.greenMedian;
        _greenStdDev = data.greenStdDev;

        Debug.Log($"[FlickerCalibrator] === CALIBRATION COMPLETE ===");
        Debug.Log($"[FlickerCalibrator] Trials: {data.trialCount}");
        Debug.Log($"[FlickerCalibrator] Green (mean): {data.greenIntensity:F4}");
        Debug.Log($"[FlickerCalibrator] Green (median): {data.greenMedian:F4}");
        Debug.Log($"[FlickerCalibrator] Std Dev: {data.greenStdDev:F4}");
        Debug.Log($"[FlickerCalibrator] Individual results: {string.Join(", ", _trialResults.ConvertAll(g => g.ToString("F3")))}");

        _state = State.AllDone;
        _endMenuSelection = 0;  // Default to "Start Main Experiment"
        _endMenuReadyTime = Time.time + END_MENU_DELAY;  // Delay before accepting input

        Debug.Log($"[FlickerCalibrator] State changed to AllDone. showHUD={showHUD}. Menu ready in {END_MENU_DELAY}s");

        // Hide flicker stimulus, show only fixation
        if (stimulus != null)
        {
            stimulus.gameObject.SetActive(false);
            Debug.Log("[FlickerCalibrator] Stimulus hidden.");
        }

        // Ensure fixation is visible
        if (fixation != null)
        {
            fixation.gameObject.SetActive(true);
            Debug.Log("[FlickerCalibrator] Fixation shown.");
        }
    }

    private float GetRandomStartingGreen()
    {
        // Random value between greenMin and greenMax
        float range = greenMax - greenMin;
        return greenMin + (float)_rng.NextDouble() * range;
    }

    private void UpdateStimulusColors()
    {
        if (stimulus != null)
        {
            stimulus.SetRedIntensity(redIntensity);
            stimulus.SetGreenIntensity(greenIntensity);
        }
    }

    private void ApplyStimulusSizeFromSpec()
    {
        if (experimentSpec == null)
        {
            Debug.LogWarning("[FlickerCalibrator] ExperimentSpec not assigned! Using default stimulus size.");
            return;
        }
        if (stimulus == null)
        {
            Debug.LogWarning("[FlickerCalibrator] Stimulus not assigned!");
            return;
        }

        // Match aperture size from ExperimentSpec
        stimulus.outerRadiusDeg = experimentSpec.apertureRadius_deg;
        stimulus.viewDistanceMeters = experimentSpec.viewDistance_m;

        // Inner radius: small hole for fixation (match fixation outer ring roughly)
        // Use a fraction of aperture for the inner hole
        stimulus.innerRadiusDeg = experimentSpec.apertureRadius_deg * 0.15f; // 15% of aperture as hole

        // Refresh geometry after changing size values
        stimulus.RefreshGeometry();

        Debug.Log($"[FlickerCalibrator] Stimulus size from ExperimentSpec '{experimentSpec.name}': outer={stimulus.outerRadiusDeg}°, inner={stimulus.innerRadiusDeg}°, viewDist={stimulus.viewDistanceMeters}m");
        Debug.Log($"[FlickerCalibrator] Stimulus localScale after refresh: {stimulus.transform.localScale}");
    }

    private void SetupFixation()
    {
        if (fixation == null) return;

        // Assign the same ExperimentSpec if available
        if (experimentSpec != null && fixation.spec == null)
        {
            fixation.spec = experimentSpec;
        }

        // Apply fixation settings
        fixation.Apply("FlickerCalibrator.SetupFixation");
        Debug.Log("[FlickerCalibrator] Fixation target configured.");
    }

    // ============== XR Input Setup ==============

    private void SetupXRInput()
    {
        if (xrInputActions == null)
        {
            Debug.Log("[FlickerCalibrator] No XR Input Actions assigned. Using keyboard only.");
            return;
        }

        // LEFT HAND
        var leftBaseMap = xrInputActions.FindActionMap("XRI Left", false);
        var leftInteractionMap = xrInputActions.FindActionMap("XRI Left Interaction", false);

        if (leftBaseMap != null)
        {
            _thumbstickLeft = leftBaseMap.FindAction("Thumbstick", false);
            _thumbstickLeft?.Enable();
        }
        if (leftInteractionMap != null)
        {
            _activateLeft = leftInteractionMap.FindAction("Activate", false);
            _activateLeft?.Enable();
        }

        // RIGHT HAND
        var rightBaseMap = xrInputActions.FindActionMap("XRI Right", false);
        var rightInteractionMap = xrInputActions.FindActionMap("XRI Right Interaction", false);

        if (rightBaseMap != null)
        {
            _thumbstickRight = rightBaseMap.FindAction("Thumbstick", false);
            _thumbstickRight?.Enable();
        }
        if (rightInteractionMap != null)
        {
            _activateRight = rightInteractionMap.FindAction("Activate", false);
            _activateRight?.Enable();
        }

        Debug.Log("[FlickerCalibrator] XR input initialized.");
    }

    private Vector2 GetThumbstickValue()
    {
        Vector2 result = Vector2.zero;

        switch (adjustmentHand)
        {
            case HandSelection.Left:
                if (_thumbstickLeft != null)
                    result = _thumbstickLeft.ReadValue<Vector2>();
                break;

            case HandSelection.Right:
                if (_thumbstickRight != null)
                    result = _thumbstickRight.ReadValue<Vector2>();
                break;

            case HandSelection.Either:
                Vector2 left = _thumbstickLeft?.ReadValue<Vector2>() ?? Vector2.zero;
                Vector2 right = _thumbstickRight?.ReadValue<Vector2>() ?? Vector2.zero;
                result = left.magnitude > right.magnitude ? left : right;
                break;
        }

        return result;
    }

    private bool IsTriggerPressed()
    {
        bool leftPressed = _activateLeft?.ReadValue<float>() > 0.5f;
        bool rightPressed = _activateRight?.ReadValue<float>() > 0.5f;

        switch (confirmHand)
        {
            case HandSelection.Left:
                return leftPressed;
            case HandSelection.Right:
                return rightPressed;
            case HandSelection.Either:
            default:
                return leftPressed || rightPressed;
        }
    }

    void OnDestroy()
    {
        _thumbstickLeft?.Disable();
        _thumbstickRight?.Disable();
        _activateLeft?.Disable();
        _activateRight?.Disable();
    }

    // ============== Public Accessors for UI ==============

    public int GetState() => (int)_state;
    public int GetCurrentTrial() => _currentTrial;
    public int GetTotalTrials() => numberOfTrials;
    public float GetGreenIntensity() => greenIntensity;
    public float GetRedIntensity() => redIntensity;
    public int GetMenuSelection() => _endMenuSelection;
    public bool IsMenuReady() => _state == State.AllDone && Time.time >= _endMenuReadyTime;

    public (float mean, float median, float stdDev) GetResults()
    {
        return (_averageGreen, _greenMedian, _greenStdDev);
    }

    // ============== HUD (legacy, doesn't work in VR) ==============

    void OnGUI()
    {
        if (!showHUD) return;

        // VR-friendly: larger text, centered
        float scale = Screen.height / 1000f;  // Scale based on screen height
        int baseFontSize = Mathf.RoundToInt(36 * scale);

        GUIStyle titleStyle = new GUIStyle(GUI.skin.label);
        titleStyle.fontSize = Mathf.RoundToInt(baseFontSize * 1.2f);
        titleStyle.normal.textColor = Color.white;
        titleStyle.fontStyle = FontStyle.Bold;
        titleStyle.alignment = TextAnchor.MiddleCenter;

        GUIStyle valueStyle = new GUIStyle(GUI.skin.label);
        valueStyle.fontSize = baseFontSize;
        valueStyle.normal.textColor = Color.white;
        valueStyle.alignment = TextAnchor.MiddleCenter;

        GUIStyle instructStyle = new GUIStyle(GUI.skin.label);
        instructStyle.fontSize = Mathf.RoundToInt(baseFontSize * 0.8f);
        instructStyle.normal.textColor = Color.gray;
        instructStyle.alignment = TextAnchor.MiddleCenter;

        GUIStyle resultStyle = new GUIStyle(GUI.skin.label);
        resultStyle.fontSize = baseFontSize;
        resultStyle.normal.textColor = Color.green;
        resultStyle.alignment = TextAnchor.MiddleCenter;

        float centerX = Screen.width / 2f;
        float labelWidth = Screen.width * 0.8f;
        float labelX = centerX - labelWidth / 2f;
        float y = Screen.height * 0.15f;
        float lineHeight = baseFontSize * 1.4f;

        GUI.Label(new Rect(labelX, y, labelWidth, lineHeight), "FLICKER FUSION CALIBRATION", titleStyle);
        y += lineHeight * 1.5f;

        GUI.Label(new Rect(labelX, y, labelWidth, lineHeight), $"Trial: {_currentTrial} / {numberOfTrials}", valueStyle);
        y += lineHeight;

        GUI.Label(new Rect(labelX, y, labelWidth, lineHeight), $"Green Intensity: {greenIntensity:F3}", valueStyle);
        y += lineHeight;

        GUI.Label(new Rect(labelX, y, labelWidth, lineHeight), $"Red Intensity: {redIntensity:F3} (fixed)", valueStyle);
        y += lineHeight * 1.5f;

        switch (_state)
        {
            case State.WaitingToStart:
                GUI.Label(new Rect(labelX, y, labelWidth, lineHeight), "Press TRIGGER or SPACE to start", instructStyle);
                break;

            case State.Adjusting:
                GUI.Label(new Rect(labelX, y, labelWidth, lineHeight), "Thumbstick UP/DOWN: Adjust green", instructStyle);
                y += lineHeight;
                GUI.Label(new Rect(labelX, y, labelWidth, lineHeight), "TRIGGER: Confirm this trial", instructStyle);
                y += lineHeight * 1.5f;
                GUI.Label(new Rect(labelX, y, labelWidth, lineHeight), "Minimize the flicker.", instructStyle);
                break;

            case State.BetweenTrials:
                GUI.Label(new Rect(labelX, y, labelWidth, lineHeight), $"Trial {_currentTrial} recorded: {_trialResults[_trialResults.Count - 1]:F3}", valueStyle);
                y += lineHeight;
                GUI.Label(new Rect(labelX, y, labelWidth, lineHeight), "Press TRIGGER for next trial", instructStyle);
                break;

            case State.AllDone:
                // Results
                GUI.Label(new Rect(labelX, y, labelWidth, lineHeight), "=== CALIBRATION COMPLETE ===", resultStyle);
                y += lineHeight * 1.2f;
                GUI.Label(new Rect(labelX, y, labelWidth, lineHeight), $"Trials: {_trialResults.Count}", valueStyle);
                y += lineHeight;
                GUI.Label(new Rect(labelX, y, labelWidth, lineHeight), $"Green (mean):   {_averageGreen:F4}", resultStyle);
                y += lineHeight;
                GUI.Label(new Rect(labelX, y, labelWidth, lineHeight), $"Green (median): {_greenMedian:F4}", resultStyle);
                y += lineHeight;
                GUI.Label(new Rect(labelX, y, labelWidth, lineHeight), $"Std Dev:        {_greenStdDev:F4}", valueStyle);
                y += lineHeight * 1.5f;

                // Check if still in delay period
                float timeRemaining = _endMenuReadyTime - Time.time;
                if (timeRemaining > 0)
                {
                    GUI.Label(new Rect(labelX, y, labelWidth, lineHeight), "Calibration saved. Loading menu...", instructStyle);
                }
                else
                {
                    // Menu
                    string[] menuItems = { "Start Main Experiment", "Redo Calibration", "Quit" };
                    for (int i = 0; i < menuItems.Length; i++)
                    {
                        GUIStyle menuStyle = (i == _endMenuSelection) ? resultStyle : valueStyle;
                        string prefix = (i == _endMenuSelection) ? "> " : "  ";
                        GUI.Label(new Rect(labelX, y, labelWidth, lineHeight), prefix + menuItems[i], menuStyle);
                        y += lineHeight;
                    }
                    y += lineHeight * 0.5f;
                    GUI.Label(new Rect(labelX, y, labelWidth, lineHeight), "Thumbstick: Select | Trigger: Confirm", instructStyle);
                }
                break;
        }
    }
}
