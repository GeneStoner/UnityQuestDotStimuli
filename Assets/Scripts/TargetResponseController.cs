// FILE: TargetResponseController.cs
//
// Purpose (high-level):
// ---------------------
// Owns the *response targets* and input semantics for a single response window.
//
// TrialBlockRunner drives the sequence of phases:
//   1) Stimulus (dots visible, no targets, no responses yet)
//   2) Targets/Response (dots hidden, targets visible, wait for subject response)
//
// This script is only responsible for Phase 2:
//
//   - When TrialBlockRunner calls BeginResponseWindow(onsetFrame):
//       * Turn the target ring ON.
//       * Start listening for direction + confirm / cancel keys.
//   - Each fixed-step frame, TrialBlockRunner calls:
//       * bool finished = TryStep(currentResponseFrame, out TargetResponse resp);
//       * If finished == true, TrialBlockRunner ends the trial and (optionally) re-queues it.
//
// Input conventions:
//   - Direction keys → map to 0..3 via ResponseKeyMapping.TryMapDirection
//       Up    = 0
//       Right = 1
//       Down  = 2
//       Left  = 3
//   - Confirm keys → Return, KeypadEnter, Space
//   - Cancel keys  → Delete, Backspace
//
// Response semantics:
//   - CONFIRMED: subject chose a direction (0..3) and then pressed confirm.
//   - CANCELED:  subject pressed cancel (Delete/Backspace), regardless of direction.
//   - TIMED OUT: response window exceeded maxResponseFrames (if > 0).
//
// NOTE ON SHARED TYPES:
// ---------------------
// This script intentionally does NOT define ResponseStatus or TargetResponse.
// Those live in ResponseTypes.cs (single source of truth).

using UnityEngine;

[DisallowMultipleComponent]
public class TargetResponseController : MonoBehaviour
{
    // ---------------------------------------------------------------------
    // PUBLIC REFERENCES (wired in Inspector)
    // ---------------------------------------------------------------------

    [Header("Target visuals")]
    [Tooltip("Root GameObject of the response targets (e.g., the ring with 4 or 8 target objects). " +
             "This is simply toggled on/off during the response window.")]
    public GameObject ringRoot;

    [Header("Timing")]
    [Tooltip("Maximum number of response frames to wait after BeginResponseWindow.\n" +
             "If <= 0, there is no timeout and the window only ends on confirm/cancel.")]
    public int maxResponseFrames = 0;

    // ---------------------------------------------------------------------
    // INTERNAL STATE
    // ---------------------------------------------------------------------

    // Is a response window currently active?
    private bool _windowActive = false;

    // The response-frame index at which BeginResponseWindow was called.
    private int _responseOnsetFrame = 0;

    // Latest direction choice (0..3) based on the most recent direction key pressed.
    // -1 means "no valid direction chosen yet".
    private int _lastDirectionChoice = -1;

    // Bookkeeping of the last key/device that *ended* the window.
    // (Mostly useful for debugging; the final response returns its own key/device.)
    private KeyCode _lastKey = KeyCode.None;
    private string  _lastDeviceLabel = "";

    // ---------------------------------------------------------------------
    // PUBLIC API CALLED BY TRIALBLOCKRUNNER
    // ---------------------------------------------------------------------

    /// <summary>
    /// Called exactly once when the stimulus phase ends and we enter
    /// the target/response phase for a given trial.
    ///
    /// Parameters:
    ///   responseOnsetFrame: the response frame index at which we start.
    ///   (TrialBlockRunner typically passes 0, and then increments each TryStep.)
    /// </summary>
    public void BeginResponseWindow(int responseOnsetFrame)
    {
        _windowActive        = true;
        _responseOnsetFrame  = responseOnsetFrame;
        _lastDirectionChoice = -1;
        _lastKey             = KeyCode.None;
        _lastDeviceLabel     = "";

        if (ringRoot != null)
            ringRoot.SetActive(true);
    }

    /// <summary>
    /// Cancel the response window and hide the targets immediately.
    /// Safe to call even if no window is active.
    /// </summary>
    public void StopAndHide()
    {
        _windowActive = false;

        if (ringRoot != null)
            ringRoot.SetActive(false);
    }

    /// <summary>
    /// Called once per *response* frame by TrialBlockRunner during the
    /// Targets/Response phase.
    ///
    /// Parameters:
    ///   currentResponseFrame: 0, 1, 2, ... counting from BeginResponseWindow.
    ///
    /// Returns:
    ///   finished == false:
    ///       - The window is still active; keep calling TryStep on subsequent frames.
    ///
    ///   finished == true:
    ///       - The window has ended (Confirmed / Canceled / TimedOut).
    ///       - 'response' contains the final summary.
    ///       - TrialBlockRunner should now log and move on (and optionally requeue).
    /// </summary>
    public bool TryStep(int currentResponseFrame, out TargetResponse response)
    {
        response = default;

        if (!_windowActive)
            return false; // no active window

        // -------------------------------------------------------------
        // 1) Direction key pressed?
        //    Store most recent direction as candidate; does NOT end window.
        // -------------------------------------------------------------
        if (TryPollDirectionKeyDown(out int choiceIndex, out KeyCode dirKey))
        {
            _lastDirectionChoice = choiceIndex; // 0..3
            _lastKey             = dirKey;
            _lastDeviceLabel     = ResponseKeyMapping.DeviceForKey(dirKey);
        }

        // -------------------------------------------------------------
        // 2) Cancel key pressed? (ALWAYS ends window)
        // -------------------------------------------------------------
        if (TryPollCancelKeyDown(out KeyCode cancelKey))
        {
            response.status      = ResponseStatus.Canceled;
            response.choiceIndex = -1; // "do not count"
            response.rtFrames    = currentResponseFrame - _responseOnsetFrame;
            response.key         = cancelKey;
            response.deviceLabel = ResponseKeyMapping.DeviceForKey(cancelKey);

            StopAndHide();
            return true;
        }

        // -------------------------------------------------------------
        // 3) Confirm key pressed?
        //    Ends window. If no direction was selected, treat as Canceled-like.
        // -------------------------------------------------------------
        if (TryPollConfirmKeyDown(out KeyCode confirmKey))
        {
            response.rtFrames    = currentResponseFrame - _responseOnsetFrame;
            response.key         = confirmKey;
            response.deviceLabel = ResponseKeyMapping.DeviceForKey(confirmKey);

            if (_lastDirectionChoice >= 0)
            {
                response.status      = ResponseStatus.Confirmed;
                response.choiceIndex = _lastDirectionChoice; // 0..3
            }
            else
            {
                // Confirm with no direction: treat as "do not count"
                response.status      = ResponseStatus.Canceled;
                response.choiceIndex = -1;
            }

            StopAndHide();
            return true;
        }

        // -------------------------------------------------------------
        // 4) Timeout?
        // -------------------------------------------------------------
        if (maxResponseFrames > 0 &&
            currentResponseFrame - _responseOnsetFrame >= maxResponseFrames)
        {
            response.status      = ResponseStatus.TimedOut;
            response.choiceIndex = -1;
            response.rtFrames    = maxResponseFrames;
            response.key         = KeyCode.None;
            response.deviceLabel = "Keyboard";

            StopAndHide();
            return true;
        }

        return false; // still waiting
    }

    // ---------------------------------------------------------------------
    // INTERNAL HELPER METHODS: KEY POLLING
    // ---------------------------------------------------------------------

    /// <summary>
    /// Poll for any *direction* key down this frame and map it to 0..3 via ResponseKeyMapping.
    /// Returns true if a direction key was pressed this frame.
    /// </summary>
    private bool TryPollDirectionKeyDown(out int choiceIndex, out KeyCode triggeringKey)
    {
        choiceIndex   = -1;
        triggeringKey = KeyCode.None;

        // Explicit list keeps things predictable.
        KeyCode[] candidates =
        {
            KeyCode.UpArrow,    KeyCode.W,        KeyCode.Keypad8,
            KeyCode.RightArrow, KeyCode.D,        KeyCode.Keypad6,
            KeyCode.DownArrow,  KeyCode.S,        KeyCode.Keypad2,
            KeyCode.LeftArrow,  KeyCode.A,        KeyCode.Keypad4
        };

        foreach (KeyCode key in candidates)
        {
            if (Input.GetKeyDown(key) &&
                ResponseKeyMapping.TryMapDirection(key, out int mappedIndex))
            {
                choiceIndex   = mappedIndex; // 0..3
                triggeringKey = key;
                return true;
            }
        }

        return false;
    }

    /// <summary>
    /// Poll for any *confirm* key down this frame (Return, KeypadEnter, Space).
    /// Returns true if a confirm key was pressed.
    /// </summary>
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

    /// <summary>
    /// Poll for any *cancel* key down this frame (Delete, Backspace).
    /// Returns true if a cancel key was pressed.
    /// </summary>
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
}