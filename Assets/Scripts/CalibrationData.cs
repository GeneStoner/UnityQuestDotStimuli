// FILE: CalibrationData.cs
//
// Stores and retrieves isoluminance calibration results.
// Saved to Application.persistentDataPath for Quest compatibility.
//
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using UnityEngine;

[Serializable]
public class CalibrationData
{
    public float redIntensity = 1.0f;
    public float greenIntensity = 0.5f;  // Average of trials
    public float greenMedian = 0.5f;     // Median of trials
    public float greenStdDev = 0f;       // Standard deviation
    public List<float> trialResults = new List<float>();  // Individual trial values
    public string calibrationDate;
    public string deviceId;
    public int trialCount;

    private const string FILENAME = "isoluminance_calibration.json";

    /// <summary>
    /// Get the full path where calibration data is stored.
    /// </summary>
    public static string GetFilePath()
    {
        return Path.Combine(Application.persistentDataPath, FILENAME);
    }

    /// <summary>
    /// Compute statistics from trial results.
    /// </summary>
    public void ComputeStatistics()
    {
        if (trialResults == null || trialResults.Count == 0) return;

        trialCount = trialResults.Count;

        // Mean
        float sum = 0f;
        foreach (float g in trialResults) sum += g;
        greenIntensity = sum / trialCount;

        // Median
        var sorted = trialResults.OrderBy(x => x).ToList();
        if (trialCount % 2 == 0)
            greenMedian = (sorted[trialCount / 2 - 1] + sorted[trialCount / 2]) / 2f;
        else
            greenMedian = sorted[trialCount / 2];

        // Standard deviation
        float sumSq = 0f;
        foreach (float g in trialResults)
        {
            float diff = g - greenIntensity;
            sumSq += diff * diff;
        }
        greenStdDev = Mathf.Sqrt(sumSq / trialCount);
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
            Debug.Log($"[CalibrationData] Red={redIntensity:F3}, Green(mean)={greenIntensity:F3}, Green(median)={greenMedian:F3}, StdDev={greenStdDev:F3}");
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
            Debug.Log($"[CalibrationData] Loaded: Red={data.redIntensity:F3}, Green(mean)={data.greenIntensity:F3}, Green(median)={data.greenMedian:F3} (from {data.calibrationDate})");
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
    /// Get calibrated colors as Unity Color values (uses mean by default).
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
    /// Get green color using median instead of mean.
    /// </summary>
    public Color GetGreenColorMedian()
    {
        return new Color(0f, greenMedian, 0f, 1f);
    }

    /// <summary>
    /// Create a default calibration (uncalibrated starting point).
    /// </summary>
    public static CalibrationData CreateDefault()
    {
        return new CalibrationData
        {
            redIntensity = 1.0f,
            greenIntensity = 0.5f,
            greenMedian = 0.5f
        };
    }
}
