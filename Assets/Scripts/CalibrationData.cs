// FILE: CalibrationData.cs
//
// Stores and retrieves isoluminance calibration results.
// Saved to Application.persistentDataPath for Quest compatibility.
//
using System;
using System.IO;
using UnityEngine;

[Serializable]
public class CalibrationData
{
    public float redIntensity = 0.9f;
    public float greenIntensity = 0.5f;
    public string calibrationDate;
    public string deviceId;

    private const string FILENAME = "isoluminance_calibration.json";

    /// <summary>
    /// Get the full path where calibration data is stored.
    /// </summary>
    public static string GetFilePath()
    {
        return Path.Combine(Application.persistentDataPath, FILENAME);
    }

    /// <summary>
    /// Save this calibration to disk.
    /// </summary>
    public void Save()
    {
        calibrationDate = DateTime.Now.ToString("yyyy-MM-dd HH:mm:ss");
        deviceId = SystemInfo.deviceUniqueIdentifier;

        string json = JsonUtility.ToJson(this, prettyPrint: true);
        string path = GetFilePath();

        try
        {
            File.WriteAllText(path, json);
            Debug.Log($"[CalibrationData] Saved to: {path}");
            Debug.Log($"[CalibrationData] Red={redIntensity:F3}, Green={greenIntensity:F3}");
        }
        catch (Exception e)
        {
            Debug.LogError($"[CalibrationData] Failed to save: {e.Message}");
        }
    }

    /// <summary>
    /// Load calibration from disk. Returns null if no calibration exists.
    /// </summary>
    public static CalibrationData Load()
    {
        string path = GetFilePath();

        if (!File.Exists(path))
        {
            Debug.Log($"[CalibrationData] No calibration file found at: {path}");
            return null;
        }

        try
        {
            string json = File.ReadAllText(path);
            var data = JsonUtility.FromJson<CalibrationData>(json);
            Debug.Log($"[CalibrationData] Loaded: Red={data.redIntensity:F3}, Green={data.greenIntensity:F3} (from {data.calibrationDate})");
            return data;
        }
        catch (Exception e)
        {
            Debug.LogError($"[CalibrationData] Failed to load: {e.Message}");
            return null;
        }
    }

    /// <summary>
    /// Check if a calibration file exists.
    /// </summary>
    public static bool Exists()
    {
        return File.Exists(GetFilePath());
    }

    /// <summary>
    /// Get calibrated colors as Unity Color values.
    /// </summary>
    public Color GetRedColor()
    {
        return new Color(redIntensity, 0f, 0f, 1f);
    }

    public Color GetGreenColor()
    {
        return new Color(0f, greenIntensity, 0f, 1f);
    }

    /// <summary>
    /// Create a default calibration (uncalibrated starting point).
    /// </summary>
    public static CalibrationData CreateDefault()
    {
        return new CalibrationData
        {
            redIntensity = 0.9f,
            greenIntensity = 0.5f
        };
    }
}
