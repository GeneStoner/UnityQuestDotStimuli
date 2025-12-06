// FILE: CsvLogger.cs
using System;
using System.IO;
using System.Text;
using UnityEngine;

/// <summary>
/// CSV logger for VR Dots experiments.
///
/// Writes:
///   - one header row
///   - one "# params" row (for analysis script)
///   - one per-trial summary row
///   - one "# mkrows" line per trial (motionKind trajectories)
///   - one "# colorrows" line per trial (color trajectories)
/// </summary>
public class CsvLogger : MonoBehaviour
{
    [Header("File Settings")]
    public string filePrefix = "vr_dots_session";
    public bool appendTimestamp = true;

    [Header("Stimulus Parameters (for analysis)")]
    // These values are written into:
    //   (1) A "# params ..." line
    //   (2) Per-trial columns
    public float translationSpeed_degPerSec = 10f;
    public float viewDistance_m = 1f;

    private string fullPath;
    private StreamWriter writer;
    private bool headerWritten = false;

    // ------------------------------------------------------------
    // Unity lifecycle
    // ------------------------------------------------------------
    private void Awake()
    {
        Debug.Log("[CsvLogger] Awake() on " + gameObject.name);

        string timestamp = appendTimestamp
            ? DateTime.UtcNow.ToString("yyyyMMdd_HHmmss")
            : "";

        string fname = appendTimestamp
            ? $"{filePrefix}_{timestamp}.csv"
            : $"{filePrefix}.csv";

        fullPath = Path.Combine(Application.persistentDataPath, fname);

        try
        {
            writer = new StreamWriter(fullPath, false, Encoding.UTF8);
            Debug.Log($"[CsvLogger] Logging to: {fullPath}");
        }
        catch (Exception e)
        {
            Debug.LogError($"[CsvLogger] Could not open file: {e}");
            writer = null;
        }
    }

    private void OnApplicationQuit()
    {
        Close();
    }

    public void Close()
    {
        if (writer != null)
        {
            writer.Flush();
            writer.Close();
            writer = null;
        }
    }

    // ------------------------------------------------------------
    // Header + params + per-trial summary
    // ------------------------------------------------------------
    public void WriteHeader()
    {
        if (writer == null || headerWritten)
            return;

        // IMPORTANT: column names match your Python analysis:
        // "transStartFrame" / "transEndFrame" + translation speed + viewing distance
        string header =
            "trialIndex," +
            "conditionID," +
            "headingDeg," +
            "onsetFrame," +
            "transStartFrame," +
            "transEndFrame," +
            "totalFrames," +
            "seedA0," +
            "seedA1," +
            "seedB2," +
            "seedB3," +
            "translationSpeed_degPerSec," +
            "viewDistance_m";

        writer.WriteLine(header);

        // NEW: params line that analyze_vr_dots_simple.py parses
        // Example:
        //   # params translationSpeed_degPerSec=10.0 viewDistance_m=1.0
        string paramLine =
            "# params " +
            $"translationSpeed_degPerSec={translationSpeed_degPerSec} " +
            $"viewDistance_m={viewDistance_m}";

        writer.WriteLine(paramLine);

        writer.Flush();
        headerWritten = true;
        Debug.Log("[CsvLogger] Header + params written");
    }

    /// <summary>
    /// Writes a single per-trial summary row.
    /// </summary>
    public void LogTrialRow(
        int trialIndex,
        string conditionID,
        float headingDeg,
        int onsetFrame,
        int transStartFrame,
        int transEndFrame,
        int totalFrames,
        int seedA0,
        int seedA1,
        int seedB2,
        int seedB3)
    {
        if (writer == null)
            return;

        if (!headerWritten)
            WriteHeader();

        Debug.Log($"[CsvLogger] LogTrialRow called for trial {trialIndex}");

        string row =
            $"{trialIndex}," +
            $"{conditionID}," +
            $"{headingDeg:F1}," +
            $"{onsetFrame}," +
            $"{transStartFrame}," +
            $"{transEndFrame}," +
            $"{totalFrames}," +
            $"{seedA0}," +
            $"{seedA1}," +
            $"{seedB2}," +
            $"{seedB3}," +
            $"{translationSpeed_degPerSec}," +
            $"{viewDistance_m}";

        writer.WriteLine(row);
        writer.Flush();
    }

    // ------------------------------------------------------------
    // Trajectory logging (mkrows / colorrows)
    // ------------------------------------------------------------
    public void LogMkRows(int trialIndex, string payload)
    {
        if (writer == null)
            return;

        // Example:
        //   # mkrows 0 1|1|2|2;1|1|2|2;...
        writer.WriteLine($"# mkrows {trialIndex} {payload}");
        writer.Flush();
    }

    public void LogColorRows(int trialIndex, string payload)
    {
        if (writer == null)
            return;

        // Example:
        //   # colorrows 0 R|R|K|K;R|R|K|K;...
        writer.WriteLine($"# colorrows {trialIndex} {payload}");
        writer.Flush();
    }

    // ------------------------------------------------------------
    // Backward compatibility stubs for TrialBlockRunner
    // ------------------------------------------------------------
    public void BeginSession(params object[] args) { }
    public void EndSession(params object[] args)   { }
    public void BeginTrial(params object[] args)   { }
    public void EndTrial(params object[] args)     { }
}