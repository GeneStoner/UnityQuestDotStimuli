// FILE: ResponseTypes.cs
//
// Single source of truth for shared response types used by:
//  - TrialBlockRunner
//  - TargetResponseController
//
// Keep these in the global namespace (no namespace block)
// so all your existing scripts can see them without edits.

using UnityEngine;

/// <summary>
/// Status of the response window when it ends.
/// </summary>
public enum ResponseStatus
{
    None = 0,
    Confirmed,
    Canceled,
    TimedOut
}

/// <summary>
/// Final response summary returned to TrialBlockRunner when the response window finishes.
/// </summary>
public struct TargetResponse
{
    public ResponseStatus status;   // Confirmed / Canceled / TimedOut / None
    public int      choiceIndex;    // 0..7 (or 0..3 depending on mapping), -1 if none
    public int      rtFrames;       // RT in frames from response-window start
    public KeyCode  key;            // key that confirmed/canceled (or None)
    public string   deviceLabel;    // e.g., "Keyboard"
}