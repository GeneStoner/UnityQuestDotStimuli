// FILE: TargetResponseController.cs
//
// Owns the response targets + input semantics for a single response window.
//
// Response semantics:
//   - CONFIRMED: subject chose a direction (choiceIndex) and then pressed confirm.
//   - CANCELED:  subject pressed cancel OR confirmed without a direction.
//   - TIMED OUT: response window exceeded maxResponseFrames (if > 0).
//
// choiceIndex convention (8-way, keypad-centric):
//   0=Up(8), 1=UpRight(9), 2=Right(6), 3=DownRight(3),
//   4=Down(2), 5=DownLeft(1), 6=Left(4), 7=UpLeft(7)

using UnityEngine;
using UnityEngine.InputSystem;

[DisallowMultipleComponent]
public class TargetResponseController : MonoBehaviour
{
    [Header("Target visuals")]
    [Tooltip("Root GameObject of the response targets (e.g., the ring with 4 or 8 target objects). " +
             "This is simply toggled on/off during the response window.")]
    public GameObject ringRoot;

    [Header("Timing")]
    [Tooltip("Maximum number of response frames to wait after BeginResponseWindow.\n" +
             "If <= 0, there is no timeout and the window only ends on confirm/cancel.\n" +
             "NOTE: This is synced from TrialBlockRunner.maxResponseFrames at trial start.")]
    public int maxResponseFrames = 0;

    [Header("XR Controller Input")]
    [Tooltip("Input Action Asset containing XR controller bindings (e.g., XRI Default Input Actions).")]
    public InputActionAsset xrInputActions;

    [Tooltip("Thumbstick deadzone - stick must exceed this magnitude to register direction.")]
    [Range(0.1f, 0.9f)]
    public float thumbstickDeadzone = 0.5f;

    [Tooltip("Which hand's thumbstick to use for direction selection.")]
    public XRHandSelection directionHand = XRHandSelection.Right;

    [Tooltip("Which hand's trigger to use for confirm.")]
    public XRHandSelection confirmHand = XRHandSelection.Either;

    public enum XRHandSelection { Left, Right, Either }

    // XR input actions
    private InputAction _thumbstickLeft;
    private InputAction _thumbstickRight;
    private InputAction _activateLeft;
    private InputAction _activateRight;
    private bool _xrConfirmPressedThisFrame;

    // Is a response window currently active?
    private bool _windowActive = false;

    // The response-frame index at which BeginResponseWindow was called.
    private int _responseOnsetFrame = 0;

    // Latest direction choice (0..7). -1 means "no valid direction chosen yet".
    private int _lastDirectionChoice = -1;

    // Key pressed to select direction (Keypad7 etc). None means "no direction yet".
    private KeyCode _lastSelectionKey = KeyCode.None;

    // Key pressed to confirm/cancel (Return/Delete/etc), for bookkeeping.
    private KeyCode _lastEndKey = KeyCode.None;

    // Track if XR was used for this response (for device labeling)
    private bool _usedXRForDirection = false;

    void Awake()
    {
        SetupXRInput();
    }

    void OnDestroy()
    {
        CleanupXRInput();
    }

    void OnDisable()
    {
        if (_thumbstickLeft != null) _thumbstickLeft.Disable();
        if (_thumbstickRight != null) _thumbstickRight.Disable();
        if (_activateLeft != null) _activateLeft.Disable();
        if (_activateRight != null) _activateRight.Disable();
    }

    void OnEnable()
    {
        if (_thumbstickLeft != null) _thumbstickLeft.Enable();
        if (_thumbstickRight != null) _thumbstickRight.Enable();
        if (_activateLeft != null) _activateLeft.Enable();
        if (_activateRight != null) _activateRight.Enable();
    }

    private void SetupXRInput()
    {
        if (xrInputActions == null)
        {
            Debug.Log("[TargetResponseController] No XR Input Actions assigned. XR controller input disabled.");
            return;
        }

        // LEFT HAND: Thumbstick is in "XRI Left", Activate is in "XRI Left Interaction"
        var leftBaseMap = xrInputActions.FindActionMap("XRI Left", false);
        var leftInteractionMap = xrInputActions.FindActionMap("XRI Left Interaction", false);

        if (leftBaseMap != null)
        {
            // Thumbstick for direction (in base map)
            _thumbstickLeft = leftBaseMap.FindAction("Thumbstick", false);
            if (_thumbstickLeft != null)
            {
                _thumbstickLeft.Enable();
                Debug.Log("[TargetResponseController] Left thumbstick bound.");
            }
        }

        if (leftInteractionMap != null)
        {
            // Trigger for confirm (in interaction map)
            _activateLeft = leftInteractionMap.FindAction("Activate", false);
            if (_activateLeft != null)
            {
                _activateLeft.Enable();
                _activateLeft.performed += OnXRConfirmPressed;
                Debug.Log("[TargetResponseController] Left trigger (Activate) bound for confirm.");
            }
        }

        // RIGHT HAND: Thumbstick is in "XRI Right", Activate is in "XRI Right Interaction"
        var rightBaseMap = xrInputActions.FindActionMap("XRI Right", false);
        var rightInteractionMap = xrInputActions.FindActionMap("XRI Right Interaction", false);

        if (rightBaseMap != null)
        {
            // Thumbstick for direction (in base map)
            _thumbstickRight = rightBaseMap.FindAction("Thumbstick", false);
            if (_thumbstickRight != null)
            {
                _thumbstickRight.Enable();
                Debug.Log("[TargetResponseController] Right thumbstick bound.");
            }
        }

        if (rightInteractionMap != null)
        {
            // Trigger for confirm (in interaction map)
            _activateRight = rightInteractionMap.FindAction("Activate", false);
            if (_activateRight != null)
            {
                _activateRight.Enable();
                _activateRight.performed += OnXRConfirmPressed;
                Debug.Log("[TargetResponseController] Right trigger (Activate) bound for confirm.");
            }
        }
    }

    private void CleanupXRInput()
    {
        if (_activateLeft != null)
        {
            _activateLeft.performed -= OnXRConfirmPressed;
            _activateLeft.Disable();
        }
        if (_activateRight != null)
        {
            _activateRight.performed -= OnXRConfirmPressed;
            _activateRight.Disable();
        }
        if (_thumbstickLeft != null) _thumbstickLeft.Disable();
        if (_thumbstickRight != null) _thumbstickRight.Disable();
    }

    private void OnXRConfirmPressed(InputAction.CallbackContext context)
    {
        if (!_windowActive) return;

        // Check which hand based on settings
        bool isLeftHand = context.action == _activateLeft;
        bool isRightHand = context.action == _activateRight;

        if (confirmHand == XRHandSelection.Left && !isLeftHand) return;
        if (confirmHand == XRHandSelection.Right && !isRightHand) return;

        _xrConfirmPressedThisFrame = true;
        Debug.Log($"[TargetResponseController] XR Confirm pressed ({(isLeftHand ? "Left" : "Right")} hand)!");
    }

    /// <summary>
    /// Polls the XR thumbstick and converts to 8-way direction (0..7).
    /// Returns true if a valid direction is detected above deadzone.
    /// </summary>
    private bool TryPollXRThumbstickDirection(out int choiceIndex)
    {
        choiceIndex = -1;

        Vector2 stick = Vector2.zero;

        // Get thumbstick value based on hand selection
        if (directionHand == XRHandSelection.Left || directionHand == XRHandSelection.Either)
        {
            if (_thumbstickLeft != null)
            {
                Vector2 leftStick = _thumbstickLeft.ReadValue<Vector2>();
                if (leftStick.magnitude > stick.magnitude)
                    stick = leftStick;
            }
        }

        if (directionHand == XRHandSelection.Right || directionHand == XRHandSelection.Either)
        {
            if (_thumbstickRight != null)
            {
                Vector2 rightStick = _thumbstickRight.ReadValue<Vector2>();
                if (rightStick.magnitude > stick.magnitude)
                    stick = rightStick;
            }
        }

        // Check deadzone
        if (stick.magnitude < thumbstickDeadzone)
            return false;

        // Convert angle to 8-way direction
        // Angle 0 = right (+X), 90 = up (+Y)
        float angle = Mathf.Atan2(stick.y, stick.x) * Mathf.Rad2Deg;
        if (angle < 0) angle += 360f;

        // Map angle to choiceIndex (0=Up, 1=UpRight, 2=Right, etc.)
        // Each sector is 45 degrees, offset by 22.5 degrees
        // Up (90°) = 0, UpRight (45°) = 1, Right (0°) = 2, etc.
        //
        // choiceIndex mapping: 0=Up(8), 1=UpRight(9), 2=Right(6), 3=DownRight(3),
        //                      4=Down(2), 5=DownLeft(1), 6=Left(4), 7=UpLeft(7)

        // Normalize angle to start from Up and go clockwise
        float adjustedAngle = (90f - angle + 360f) % 360f;  // 0° = Up, clockwise positive
        int sector = Mathf.FloorToInt((adjustedAngle + 22.5f) / 45f) % 8;

        choiceIndex = sector;
        return true;
    }

    public void BeginResponseWindow(int responseOnsetFrame)
    {
        _windowActive         = true;
        _responseOnsetFrame   = responseOnsetFrame;

        _lastDirectionChoice  = -1;
        _lastSelectionKey     = KeyCode.None;
        _lastEndKey           = KeyCode.None;
        _usedXRForDirection   = false;
        _xrConfirmPressedThisFrame = false;

        if (ringRoot != null)
            ringRoot.SetActive(true);
    }

    public void StopAndHide()
    {
        _windowActive = false;

        if (ringRoot != null)
            ringRoot.SetActive(false);
    }

    public bool TryStep(int currentResponseFrame, out TargetResponse response)
    {
        response = default;

        if (!_windowActive)
        {
            _xrConfirmPressedThisFrame = false;
            return false;
        }

        // 1a) Keyboard direction key pressed? latch candidate; does NOT end window.
        if (TryPollDirectionKeyDown(out int choiceIndex, out KeyCode dirKey))
        {
            _lastDirectionChoice = choiceIndex;  // 0..7
            _lastSelectionKey    = dirKey;       // Keypad7/UpArrow/etc
            _usedXRForDirection  = false;
        }

        // 1b) XR thumbstick direction? latch candidate; does NOT end window.
        if (TryPollXRThumbstickDirection(out int xrChoiceIndex))
        {
            _lastDirectionChoice = xrChoiceIndex;  // 0..7
            _lastSelectionKey    = KeyCode.None;   // No key for XR
            _usedXRForDirection  = true;
        }

        // 2) Cancel key pressed? ALWAYS ends window. (No XR cancel for now)
        if (TryPollCancelKeyDown(out KeyCode cancelKey))
        {
            _lastEndKey = cancelKey;

            response.status       = ResponseStatus.Canceled;
            response.choiceIndex  = -1;
            response.rtFrames     = currentResponseFrame - _responseOnsetFrame;

            response.selectionKey = _lastSelectionKey;
            response.confirmKey   = KeyCode.None;

            // Maintain backward-compat: "key" is the ending key (cancel here).
            response.key          = cancelKey;
            response.deviceLabel  = ResponseKeyMapping.DeviceForKey(cancelKey);

            _xrConfirmPressedThisFrame = false;
            StopAndHide();
            return true;
        }

        // 3) Confirm: keyboard OR XR trigger. Ends window. If no direction, cancel-like.
        bool xrConfirm = _xrConfirmPressedThisFrame;
        _xrConfirmPressedThisFrame = false; // Consume XR input

        bool keyboardConfirm = TryPollConfirmKeyDown(out KeyCode confirmKey);

        if (keyboardConfirm || xrConfirm)
        {
            _lastEndKey = keyboardConfirm ? confirmKey : KeyCode.None;

            response.rtFrames     = currentResponseFrame - _responseOnsetFrame;

            response.selectionKey = _lastSelectionKey;
            response.confirmKey   = keyboardConfirm ? confirmKey : KeyCode.None;

            // Maintain backward-compat: "key" is the ending key.
            response.key          = keyboardConfirm ? confirmKey : KeyCode.None;

            // Device label: XR Controller if used XR for direction OR confirm
            if (_usedXRForDirection || xrConfirm)
                response.deviceLabel = "XR Controller";
            else if (keyboardConfirm)
                response.deviceLabel = ResponseKeyMapping.DeviceForKey(confirmKey);
            else
                response.deviceLabel = "Unknown";

            if (_lastDirectionChoice >= 0)
            {
                response.status     = ResponseStatus.Confirmed;
                response.choiceIndex = _lastDirectionChoice; // 0..7
            }
            else
            {
                response.status     = ResponseStatus.Canceled;
                response.choiceIndex = -1;
            }

            StopAndHide();
            return true;
        }

        // 4) Timeout?
        if (maxResponseFrames > 0 &&
            currentResponseFrame - _responseOnsetFrame >= maxResponseFrames)
        {
            response.status       = ResponseStatus.TimedOut;
            response.choiceIndex  = -1;
            response.rtFrames     = maxResponseFrames;

            response.selectionKey = _lastSelectionKey;
            response.confirmKey   = KeyCode.None;

            response.key          = KeyCode.None;
            response.deviceLabel  = _usedXRForDirection ? "XR Controller" : "Keyboard";

            StopAndHide();
            return true;
        }

        return false;
    }

    // ---------------------------------------------------------------------
    // INTERNAL HELPERS
    // ---------------------------------------------------------------------

    private bool TryPollDirectionKeyDown(out int choiceIndex, out KeyCode triggeringKey)
    {
        choiceIndex   = -1;
        triggeringKey = KeyCode.None;

        // Include ALL keypad 8-way keys + optional arrow/WASD fallback.
        KeyCode[] candidates =
        {
            // 8-way numeric keypad
            KeyCode.Keypad8, KeyCode.Keypad9, KeyCode.Keypad6, KeyCode.Keypad3,
            KeyCode.Keypad2, KeyCode.Keypad1, KeyCode.Keypad4, KeyCode.Keypad7,

            // optional 4-way fallback (maps to cardinals in ResponseKeyMapping)
            KeyCode.UpArrow, KeyCode.RightArrow, KeyCode.DownArrow, KeyCode.LeftArrow,
            KeyCode.W, KeyCode.D, KeyCode.S, KeyCode.A
        };

        foreach (KeyCode key in candidates)
        {
            if (Input.GetKeyDown(key) &&
                ResponseKeyMapping.TryMapDirection(key, out int mappedIndex))
            {
                choiceIndex   = mappedIndex; // 0..7
                triggeringKey = key;
                return true;
            }
        }

        return false;
    }

    private bool TryPollConfirmKeyDown(out KeyCode confirmKey)
    {
        KeyCode[] candidates =
        {
            KeyCode.Return,
            KeyCode.KeypadEnter,
            KeyCode.Space
        };

        foreach (KeyCode key in candidates)
        {
            if (Input.GetKeyDown(key) && ResponseKeyMapping.IsConfirmKey(key))
            {
                confirmKey = key;
                return true;
            }
        }

        confirmKey = KeyCode.None;
        return false;
    }

    private bool TryPollCancelKeyDown(out KeyCode cancelKey)
    {
        KeyCode[] candidates =
        {
            KeyCode.Delete,
            KeyCode.Backspace
        };

        foreach (KeyCode key in candidates)
        {
            if (Input.GetKeyDown(key) && ResponseKeyMapping.IsCancelKey(key))
            {
                cancelKey = key;
                return true;
            }
        }

        cancelKey = KeyCode.None;
        return false;
    }

    // ---------------------------------------------------------------------
    // Optional helper: choiceIndex (0..7) → keypad digit you expect (7,8,9,4,6,1,2,3)
    // ---------------------------------------------------------------------
    public static int ChoiceIndexToKeypadDigit(int choiceIndex)
    {
        switch (choiceIndex)
        {
            case 0: return 8;
            case 1: return 9;
            case 2: return 6;
            case 3: return 3;
            case 4: return 2;
            case 5: return 1;
            case 6: return 4;
            case 7: return 7;
            default: return -1;
        }
    }
}