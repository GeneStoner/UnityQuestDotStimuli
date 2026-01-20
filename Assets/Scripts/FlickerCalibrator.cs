// FILE: FlickerCalibrator.cs
//
// Main controller for heterochromatic flicker photometry (HFP) calibration.
// User adjusts green intensity with thumbstick until flicker is minimized,
// then confirms with trigger to save isoluminance calibration.
//
using UnityEngine;
using UnityEngine.InputSystem;

[DisallowMultipleComponent]
public class FlickerCalibrator : MonoBehaviour
{
    [Header("References")]
    [Tooltip("The FlickerStimulus component that renders the annulus.")]
    public FlickerStimulus stimulus;

    [Tooltip("Optional: Fixation controller for central fixation target.")]
    public Fixation_Controller fixation;

    [Header("Calibration Settings")]
    [Tooltip("Starting red intensity (fixed during calibration).")]
    [Range(0.1f, 1f)]
    public float redIntensity = 0.9f;

    [Tooltip("Starting green intensity (adjustable).")]
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

    // State
    private bool _isCalibrating = true;
    private bool _triggerPressedLastFrame = false;
    private float _lastAdjustmentTime = 0f;
    private const float ADJUSTMENT_COOLDOWN = 0.05f; // 50ms between adjustments

    void Awake()
    {
        SetupXRInput();
    }

    void Start()
    {
        // Load existing calibration as starting point (if any)
        var existing = CalibrationData.Load();
        if (existing != null)
        {
            redIntensity = existing.redIntensity;
            greenIntensity = existing.greenIntensity;
        }

        // Apply initial colors
        UpdateStimulusColors();

        Debug.Log($"[FlickerCalibrator] Started. Green={greenIntensity:F3}. Use thumbstick to adjust, trigger to confirm.");
    }

    void Update()
    {
        if (!_isCalibrating) return;

        HandleInput();
    }

    private void HandleInput()
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

                Debug.Log($"[FlickerCalibrator] Green adjusted to: {greenIntensity:F3}");
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

        // --- Trigger/key to confirm ---
        bool triggerPressed = IsTriggerPressed();
        bool keyConfirm = Input.GetKeyDown(KeyCode.Return) || Input.GetKeyDown(KeyCode.Space);

        if ((triggerPressed && !_triggerPressedLastFrame) || keyConfirm)
        {
            ConfirmCalibration();
        }

        _triggerPressedLastFrame = triggerPressed;

        // --- Reset to default (R key) ---
        if (Input.GetKeyDown(KeyCode.R))
        {
            greenIntensity = 0.5f;
            UpdateStimulusColors();
            Debug.Log("[FlickerCalibrator] Reset to default: Green=0.5");
        }
    }

    private void UpdateStimulusColors()
    {
        if (stimulus != null)
        {
            stimulus.SetRedIntensity(redIntensity);
            stimulus.SetGreenIntensity(greenIntensity);
        }
    }

    private void ConfirmCalibration()
    {
        _isCalibrating = false;

        // Save calibration
        var data = new CalibrationData
        {
            redIntensity = redIntensity,
            greenIntensity = greenIntensity
        };
        data.Save();

        // Stop flicker and show green (or some confirmation)
        if (stimulus != null)
        {
            stimulus.flickerEnabled = false;
            stimulus.ForceColor(false); // Show green
        }

        Debug.Log($"[FlickerCalibrator] Calibration confirmed! Red={redIntensity:F3}, Green={greenIntensity:F3}");
        Debug.Log("[FlickerCalibrator] Calibration saved. Ready for next phase.");

        // Could trigger scene transition here in future
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

    // ============== HUD ==============

    void OnGUI()
    {
        if (!showHUD) return;

        GUIStyle style = new GUIStyle(GUI.skin.label);
        style.fontSize = 24;
        style.normal.textColor = Color.white;

        float y = 20;
        float lineHeight = 30;

        GUI.Label(new Rect(20, y, 600, lineHeight), "FLICKER FUSION CALIBRATION", style);
        y += lineHeight * 1.5f;

        GUI.Label(new Rect(20, y, 600, lineHeight), $"Green Intensity: {greenIntensity:F3}", style);
        y += lineHeight;

        GUI.Label(new Rect(20, y, 600, lineHeight), $"Red Intensity: {redIntensity:F3} (fixed)", style);
        y += lineHeight * 1.5f;

        style.fontSize = 18;

        if (_isCalibrating)
        {
            GUI.Label(new Rect(20, y, 600, lineHeight), "Thumbstick UP/DOWN: Adjust green", style);
            y += lineHeight;
            GUI.Label(new Rect(20, y, 600, lineHeight), "TRIGGER or SPACE: Confirm", style);
            y += lineHeight;
            GUI.Label(new Rect(20, y, 600, lineHeight), "R: Reset to default", style);
            y += lineHeight * 1.5f;

            GUI.Label(new Rect(20, y, 600, lineHeight), "Adjust until flicker is minimized.", style);
        }
        else
        {
            style.normal.textColor = Color.green;
            GUI.Label(new Rect(20, y, 600, lineHeight), "CALIBRATION SAVED!", style);
        }
    }
}
