// FILE: ResponseKeyMapping.cs
using UnityEngine;

/// -----------------------------------------------------------------------
///  KEY → RESPONSE MAPPING UTILITIES
/// -----------------------------------------------------------------------
public static class ResponseKeyMapping
{
    // Direction Mapping
    public static bool TryMapDirection(KeyCode key, out int choiceIndex)
    {
        choiceIndex = -1;

        // 8-way numeric keypad
        switch (key)
        {
            case KeyCode.Keypad8: choiceIndex = 0; return true; // N
            case KeyCode.Keypad9: choiceIndex = 1; return true; // NE
            case KeyCode.Keypad6: choiceIndex = 2; return true; // E
            case KeyCode.Keypad3: choiceIndex = 3; return true; // SE
            case KeyCode.Keypad2: choiceIndex = 4; return true; // S
            case KeyCode.Keypad1: choiceIndex = 5; return true; // SW
            case KeyCode.Keypad4: choiceIndex = 6; return true; // W
            case KeyCode.Keypad7: choiceIndex = 7; return true; // NW
        }

        // Optional 4-way fallback (arrows + WASD map to cardinals only)
        switch (key)
        {
            case KeyCode.UpArrow:
            case KeyCode.W:
                choiceIndex = 0; return true; // N

            case KeyCode.RightArrow:
            case KeyCode.D:
                choiceIndex = 2; return true; // E

            case KeyCode.DownArrow:
            case KeyCode.S:
                choiceIndex = 4; return true; // S

            case KeyCode.LeftArrow:
            case KeyCode.A:
                choiceIndex = 6; return true; // W
        }

        return false;
    }

    // CONFIRM KEYS
    public static bool IsConfirmKey(KeyCode key)
    {
        return key == KeyCode.Return
            || key == KeyCode.KeypadEnter
            || key == KeyCode.Space;
    }

    // CANCEL KEYS
    public static bool IsCancelKey(KeyCode key)
    {
        return key == KeyCode.Delete
            || key == KeyCode.Backspace;
    }

    // DEVICE LABEL
    public static string DeviceForKey(KeyCode key)
    {
        return "Keyboard";
    }

    // Helpers for analysis / logging
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

    public static string ChoiceIndexToDirectionLabel(int choiceIndex)
    {
        switch (choiceIndex)
        {
            case 0: return "N";
            case 1: return "NE";
            case 2: return "E";
            case 3: return "SE";
            case 4: return "S";
            case 5: return "SW";
            case 6: return "W";
            case 7: return "NW";
            default: return "";
        }
    }

    public static bool TryKeyToKeypadDigit(KeyCode key, out int digit)
    {
        digit = -1;
        if (!TryMapDirection(key, out int choiceIndex)) return false;

        digit = ChoiceIndexToKeypadDigit(choiceIndex);
        return digit > 0;
    }

    public static bool TryKeyToDirectionLabel(KeyCode key, out string label)
    {
        label = "";
        if (!TryMapDirection(key, out int choiceIndex)) return false;

        label = ChoiceIndexToDirectionLabel(choiceIndex);
        return !string.IsNullOrEmpty(label);
    }
}