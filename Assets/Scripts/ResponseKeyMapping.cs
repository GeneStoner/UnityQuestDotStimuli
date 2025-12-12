// FILE: ResponseKeyMapping.cs
using UnityEngine;

/// -----------------------------------------------------------------------
///  KEY → RESPONSE MAPPING UTILITIES
///  Central place to define:
///    - which keys map to directions,
///    - which keys confirm,
///    - which keys cancel,
///    - device labeling.
///
///  IMPORTANT:
///  This file deliberately contains *NO* response enums or structs.
///  Shared types (ResponseStatus, TargetResponse) live in ResponseTypes.cs.
/// -----------------------------------------------------------------------
public static class ResponseKeyMapping
{
    // ---------------------------------------------------------
    // Direction Mapping (Up / Right / Down / Left)
    // ---------------------------------------------------------
    // Convention:
    //   0 = Up
    //   1 = Right
    //   2 = Down
    //   3 = Left
    //
    // NOTE:
    //  - TargetResponseController uses this raw mapping.
    //  - TrialBlockRunner may later convert 0..3 into an 8-way
    //    representation if desired.
    // ---------------------------------------------------------
    public static bool TryMapDirection(KeyCode key, out int choiceIndex)
    {
        choiceIndex = -1;

        switch (key)
        {
            // Up
            case KeyCode.UpArrow:
            case KeyCode.W:
            case KeyCode.Keypad8:
                choiceIndex = 0;
                return true;

            // Right
            case KeyCode.RightArrow:
            case KeyCode.D:
            case KeyCode.Keypad6:
                choiceIndex = 1;
                return true;

            // Down
            case KeyCode.DownArrow:
            case KeyCode.S:
            case KeyCode.Keypad2:
                choiceIndex = 2;
                return true;

            // Left
            case KeyCode.LeftArrow:
            case KeyCode.A:
            case KeyCode.Keypad4:
                choiceIndex = 3;
                return true;

            default:
                return false;
        }
    }

    // ---------------------------------------------------------
    // CONFIRM KEYS
    // A direction becomes a *valid response* only after one of these.
    // ---------------------------------------------------------
    public static bool IsConfirmKey(KeyCode key)
    {
        return key == KeyCode.Return
            || key == KeyCode.KeypadEnter
            || key == KeyCode.Space;
    }

    // ---------------------------------------------------------
    // CANCEL KEYS ("do not count this trial")
    // ---------------------------------------------------------
    public static bool IsCancelKey(KeyCode key)
    {
        return key == KeyCode.Delete
            || key == KeyCode.Backspace;
    }

    // ---------------------------------------------------------
    // DEVICE LABEL (simple for now, extendable later)
    // ---------------------------------------------------------
    public static string DeviceForKey(KeyCode key)
    {
        // Later:
        //   - joystick/gamepad
        //   - VR controller
        return "Keyboard";
    }
}