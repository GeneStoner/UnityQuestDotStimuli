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

[DisallowMultipleComponent]
public class TargetResponseController : MonoBehaviour
{
    [Header("Target visuals")]
    [Tooltip("Root GameObject of the response targets (e.g., the ring with 4 or 8 target objects). " +
             "This is simply toggled on/off during the response window.")]
    public GameObject ringRoot;

    [Header("Timing")]
    [Tooltip("Maximum number of response frames to wait after BeginResponseWindow.\n" +
             "If <= 0, there is no timeout and the window only ends on confirm/cancel.")]
    public int maxResponseFrames = 0;

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

    public void BeginResponseWindow(int responseOnsetFrame)
    {
        _windowActive         = true;
        _responseOnsetFrame   = responseOnsetFrame;

        _lastDirectionChoice  = -1;
        _lastSelectionKey     = KeyCode.None;
        _lastEndKey           = KeyCode.None;

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
            return false;

        // 1) Direction key pressed? latch candidate; does NOT end window.
        if (TryPollDirectionKeyDown(out int choiceIndex, out KeyCode dirKey))
        {
            _lastDirectionChoice = choiceIndex;  // 0..7
            _lastSelectionKey    = dirKey;       // Keypad7/UpArrow/etc
        }

        // 2) Cancel key pressed? ALWAYS ends window.
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

            StopAndHide();
            return true;
        }

        // 3) Confirm key pressed? Ends window. If no direction, cancel-like.
        if (TryPollConfirmKeyDown(out KeyCode confirmKey))
        {
            _lastEndKey = confirmKey;

            response.rtFrames     = currentResponseFrame - _responseOnsetFrame;

            response.selectionKey = _lastSelectionKey;
            response.confirmKey   = confirmKey;

            // Maintain backward-compat: "key" is the ending key (confirm here).
            response.key          = confirmKey;
            response.deviceLabel  = ResponseKeyMapping.DeviceForKey(confirmKey);

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
            response.deviceLabel  = "Keyboard";

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