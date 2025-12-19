// FILE: ResponseTypes.cs
// Purpose: shared response data types (NO input mapping logic in here).
//
// IMPORTANT:
// - Do NOT define ResponseKeyMapping in this file.
// - ResponseKeyMapping must live only in ResponseKeyMapping.cs

using UnityEngine;

public enum ResponseStatus
{
    Confirmed,
    Canceled,
    TimedOut
}

[System.Serializable]
public struct TargetResponse
{
    public ResponseStatus status;

    // 0..7 when Confirmed, -1 otherwise
    public int choiceIndex;

    // Frames from response-window onset to the ENDING key (confirm/cancel) or timeout.
    public int rtFrames;

    // Direction-selection key last pressed (Keypad7 etc). None if never selected.
    public KeyCode selectionKey;

    // Confirm key used (Return/Space/KeypadEnter). None if canceled/timeout.
    public KeyCode confirmKey;

    // Backward-compat: ending key (confirm/cancel). None on timeout.
    public KeyCode key;

    // "Keyboard" for now; later controller labeling.
    public string deviceLabel;
}