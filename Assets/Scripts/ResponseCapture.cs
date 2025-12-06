// FILE: ResponseCapture.cs
using UnityEngine;

/// <summary>
/// Captures a single 8-way direction response per trial (keyboard only).
///
/// Idea:
///   - 8 keys mapped to 8 directions (indices 0..7).
///   - TrialBlockRunner tells us:
///       BeginTrial(trialIndex, responseStartFrame)
///       NoteFrame(frameIndex) once per frame
///       EndTrial(), then GetResponse(...) at the end.
///
/// This component does *not* know what the actual heading degrees are.
/// It only reports:
///   - choiceIndex (0..7, or -1 for no response)
///   - RT in frames, measured from responseStartFrame
///   - which KeyCode was pressed (for debugging).
///
/// Default mapping (you can change these in the Inspector):
///   index 0 -> KeyCode.Alpha1
///   index 1 -> KeyCode.Alpha2
///   ...
///   index 7 -> KeyCode.Alpha8
/// </summary>
public class ResponseCapture : MonoBehaviour
{
    [Header("Keys used for 8-way direction responses (index 0..7)")]
    public KeyCode[] directionKeys = new KeyCode[8]
    {
        KeyCode.Alpha1,
        KeyCode.Alpha2,
        KeyCode.Alpha3,
        KeyCode.Alpha4,
        KeyCode.Alpha5,
        KeyCode.Alpha6,
        KeyCode.Alpha7,
        KeyCode.Alpha8
    };

    [Header("Debug")]
    [Tooltip("Log responses to the Unity Console when they occur.")]
    public bool debugLogResponses = true;

    // --- internal state ----------------------------------------------------
    private bool _isTrialActive = false;

    private int _currentTrialIndex = -1;
    private int _responseStartFrame = 0;  // first frame at which responses are counted

    private int _respChoiceIndex = -1;    // 0..7 or -1 (no response)
    private int _respFrame = -1;          // absolute frame index of response
    private KeyCode _respKey = KeyCode.None;

    /// <summary>
    /// Call at the start of a trial.
    /// </summary>
    public void BeginTrial(int trialIndex, int responseStartFrame)
    {
        _currentTrialIndex  = trialIndex;
        _responseStartFrame = responseStartFrame;

        _respChoiceIndex = -1;
        _respFrame       = -1;
        _respKey         = KeyCode.None;
        _isTrialActive   = true;

        if (debugLogResponses)
        {
            Debug.Log($"[ResponseCapture] BeginTrial: trial={trialIndex}, responseStartFrame={responseStartFrame}");
        }
    }

    /// <summary>
    /// Call once per frame during the trial.
    /// </summary>
    public void NoteFrame(int frameIndex)
    {
        if (!_isTrialActive)
            return;

        // Do not accept responses before the window opens.
        if (frameIndex < _responseStartFrame)
            return;

        // Already have a response? Then ignore further keys.
        if (_respChoiceIndex >= 0)
            return;

        // Scan all 8 direction keys.
        for (int i = 0; i < directionKeys.Length; i++)
        {
            var key = directionKeys[i];
            if (Input.GetKeyDown(key))
            {
                RecordResponse(i, key, frameIndex);
                break;
            }
        }
    }

    /// <summary>
    /// Optional call at the end of the trial (for logging / clean up).
    /// </summary>
    public void EndTrial()
    {
        if (debugLogResponses)
        {
            Debug.Log(
                $"[ResponseCapture] EndTrial: trial={_currentTrialIndex}, " +
                $"choiceIndex={_respChoiceIndex}, key={_respKey}, frame={_respFrame}"
            );
        }

        _isTrialActive = false;
    }

    /// <summary>
    /// Retrieve the response for the latest trial.
    /// If no response: choiceIndex = -1, respRT_frames = -1, respKey = KeyCode.None.
    /// </summary>
    public void GetResponse(out int choiceIndex, out int respRT_frames, out KeyCode respKey)
    {
        choiceIndex = _respChoiceIndex;
        respKey     = _respKey;

        if (_respFrame < 0)
        {
            respRT_frames = -1;
        }
        else
        {
            respRT_frames = _respFrame - _responseStartFrame;
        }
    }

    /// <summary>
    /// Allows the trial to be aborted (e.g., if start key is hit again).
    /// Clears any recorded response.
    /// </summary>
    public void AbortTrial()
    {
        if (debugLogResponses)
        {
            Debug.Log($"[ResponseCapture] AbortTrial: trial={_currentTrialIndex}");
        }

        _isTrialActive    = false;
        _respChoiceIndex  = -1;
        _respFrame        = -1;
        _respKey          = KeyCode.None;
        _currentTrialIndex = -1;
    }

    // --- internal helper ---------------------------------------------------
    private void RecordResponse(int choiceIndex, KeyCode key, int frameIndex)
    {
        _respChoiceIndex = choiceIndex;
        _respFrame       = frameIndex;
        _respKey         = key;

        if (debugLogResponses)
        {
            Debug.Log(
                $"[ResponseCapture] Response recorded: trial={_currentTrialIndex}, " +
                $"choiceIndex={choiceIndex}, key={key}, frame={frameIndex}"
            );
        }
    }
}