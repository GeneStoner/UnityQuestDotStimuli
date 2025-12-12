// FILE: CsvLogger.cs
// Purpose: Session / trial CSV logging for VR dots experiment.
// - One row per trial (TAB-separated, .csv extension is fine)
// - Includes trial meta, global params, response fields, mkrows, colorrows
//
// DROP-IN UPDATE:
//  - Adds a safe output directory override (exact path you provided)
//  - Sanitizes mkrows/colorrows (and other string cells) to prevent tabs/newlines
//    from exploding into hundreds of columns in the TSV.
//
// NOTE:
//  - This does NOT change how TrialBlockRunner builds mkrows/colorrows;
//    it just guarantees they stay in ONE COLUMN each.

using System;
using System.IO;
using System.Text;
using System.Collections.Generic;
using UnityEngine;

public class CsvLogger : MonoBehaviour
{
    [Header("Debug")]
    public bool debugLog = true;

    [Header("Output folder (optional override)")]
    [Tooltip("If set, CsvLogger writes sessions here instead of Application.persistentDataPath/VRDotsSessions.\n" +
             "Example: /Users/genestoner1/Library/Application Support/ThatsRandom/VRDotsDataFiles")]
    public string overrideOutputDir = "";

    private string       _filePath;
    private StreamWriter _writer;
    private bool         _headerWritten = false;

    // --- Global / session-level params -------------------------------------
    private float _sessionTranslationSpeed_degPerSec = float.NaN;
    private float _sessionViewDistance_m             = float.NaN;

    // --- Per-trial buffer (one row) ----------------------------------------
    private bool   _trialActive = false;

    // trial identity + timing
    private int    _trialIndex;
    private string _conditionID;
    private float  _headingDeg;
    private int    _onsetFrame;
    private int    _transStartFrame;
    private int    _transEndFrame;
    private int    _totalFrames;

    // seeds
    private int _seedA0;
    private int _seedA1;
    private int _seedB2;
    private int _seedB3;

    // viewing / motion (usually constant across session)
    private float _translationSpeed_degPerSec;
    private float _viewDistance_m;

    // response fields
    private int    _responseChoiceIndex;
    private int    _responseRT_frames;
    private string _responseKey;
    private string _responseDevice;

    // payload strings accumulated by TrialBlockRunner
    private string _mkrows;
    private string _colorrows;

    // ------------------------------------------------------------------------
    void Awake()
    {
        string dir = GetOutputDirectory();
        EnsureDirectory(dir);

        string ts   = DateTime.Now.ToString("yyyyMMdd_HHmmss");
        string name = $"vr_dots_session_{ts}.csv";
        _filePath = Path.Combine(dir, name);

        // UTF8 without BOM
        _writer = new StreamWriter(
            _filePath,
            false,
            new UTF8Encoding(encoderShouldEmitUTF8Identifier: false)
        );

        if (debugLog)
        {
            Debug.Log($"[CsvLogger] Logging to: {_filePath}");
        }
    }

    void OnDestroy()
    {
        CloseWriter();
    }

    private void CloseWriter()
    {
        if (_writer != null)
        {
            _writer.Flush();
            _writer.Dispose();
            _writer = null;
        }
    }

    private string GetOutputDirectory()
    {
        // If user provided an override path, use it verbatim.
        if (!string.IsNullOrWhiteSpace(overrideOutputDir))
        {
            return overrideOutputDir.Trim();
        }

        // Default: Application.persistentDataPath/VRDotsSessions
        return Path.Combine(Application.persistentDataPath, "VRDotsSessions");
    }

    private static void EnsureDirectory(string dir)
    {
        if (string.IsNullOrWhiteSpace(dir)) return;
        if (!Directory.Exists(dir)) Directory.CreateDirectory(dir);
    }

    // Force strings to remain a single TSV cell (no tabs/newlines).
    private static string SanitizeCell(string s)
    {
        if (string.IsNullOrEmpty(s)) return "";
        return s.Replace("\t", " ")
                .Replace("\r", " ")
                .Replace("\n", " ");
    }

    // ------------------------------------------------------------------------
    // Session-level entry point
    // ------------------------------------------------------------------------
    public void BeginSession(ExperimentSpec spec, List<ExperimentSpec.PlannedTrial> trials)
    {
        if (spec != null)
        {
            _sessionTranslationSpeed_degPerSec = spec.translationSpeed_degPerSec;
            _sessionViewDistance_m             = spec.viewDistance_m;
        }

        WriteHeaderIfNeeded();

        // Optional params line for quick inspection.
        if (_writer != null)
        {
            string paramLine =
                $"# params translationSpeed_degPerSec={_sessionTranslationSpeed_degPerSec} " +
                $"viewDistance_m={_sessionViewDistance_m}";
            _writer.WriteLine(paramLine);
            _writer.Flush();
        }

        if (debugLog)
        {
            Debug.Log("[CsvLogger] BeginSession() header + params written");
        }
    }

    private void WriteHeaderIfNeeded()
    {
        if (_writer == null || _headerWritten)
            return;

        string[] cols = new[]
        {
            "trialIndex",
            "conditionID",
            "headingDeg",
            "onsetFrame",
            "transStartFrame",
            "transEndFrame",
            "totalFrames",
            "seedA0",
            "seedA1",
            "seedB2",
            "seedB3",
            "translationSpeed_degPerSec",
            "viewDistance_m",
            "responseChoiceIndex",
            "responseRT_frames",
            "responseKey",
            "responseDevice",
            "mkrows",
            "colorrows"
        };

        string header = string.Join("\t", cols);
        _writer.WriteLine(header);
        _writer.Flush();
        _headerWritten = true;

        if (debugLog)
        {
            Debug.Log("[CsvLogger] Header written");
        }
    }

    // ------------------------------------------------------------------------
    // Per-trial lifecycle
    // ------------------------------------------------------------------------
    public void BeginTrial(ExperimentSpec.PlannedTrial trial,
                           ExperimentSpec             spec,
                           StimulusConditionsLibrary.StimulusCondition cond)
    {
        _trialActive = true;

        // Initialize sentinel values
        _trialIndex      = -1;
        _conditionID     = "";
        _headingDeg      = float.NaN;
        _onsetFrame      = -1;
        _transStartFrame = -1;
        _transEndFrame   = -1;
        _totalFrames     = -1;

        _seedA0 = _seedA1 = _seedB2 = _seedB3 = 0;

        _translationSpeed_degPerSec = float.IsNaN(_sessionTranslationSpeed_degPerSec)
                                      ? 0f : _sessionTranslationSpeed_degPerSec;
        _viewDistance_m             = float.IsNaN(_sessionViewDistance_m)
                                      ? 0f : _sessionViewDistance_m;

        _responseChoiceIndex = -1;
        _responseRT_frames   = -1;
        _responseKey         = "";
        _responseDevice      = "";

        _mkrows    = "";
        _colorrows = "";

        if (debugLog)
        {
            Debug.Log($"[CsvLogger] BeginTrial() trialIndex={trial.index}, condID={trial.conditionID}");
        }
    }

    public void LogTrialRow(int trialIndex,
                            string conditionID,
                            float headingDeg,
                            int onsetFrame,
                            int transStartFrame,
                            int transEndFrame,
                            int totalFrames,
                            int seedA0,
                            int seedA1,
                            int seedB2,
                            int seedB3,
                            float translationSpeed_degPerSec,
                            float viewDistance_m)
    {
        if (!_trialActive) return;

        _trialIndex      = trialIndex;
        _conditionID     = conditionID ?? "";
        _headingDeg      = headingDeg;
        _onsetFrame      = onsetFrame;
        _transStartFrame = transStartFrame;
        _transEndFrame   = transEndFrame;
        _totalFrames     = totalFrames;

        _seedA0 = seedA0;
        _seedA1 = seedA1;
        _seedB2 = seedB2;
        _seedB3 = seedB3;

        _translationSpeed_degPerSec = translationSpeed_degPerSec;
        _viewDistance_m             = viewDistance_m;

        if (debugLog)
        {
            Debug.Log($"[CsvLogger] LogTrialRow called for trial {trialIndex}");
        }
    }

    public void LogMkRows(int trialIndex, string mkPayload)
    {
        if (!_trialActive) return;
        _mkrows = mkPayload ?? "";
    }

    public void LogColorRows(int trialIndex, string colorPayload)
    {
        if (!_trialActive) return;
        _colorrows = colorPayload ?? "";
    }

    public void LogResponse(int choiceIndex,
                            int rtFrames,
                            string keyName,
                            string deviceName)
    {
        if (!_trialActive) return;

        _responseChoiceIndex = choiceIndex;
        _responseRT_frames   = rtFrames;
        _responseKey         = keyName    ?? "";
        _responseDevice      = deviceName ?? "";

        if (debugLog)
        {
            Debug.Log($"[CsvLogger] LogResponse trial={_trialIndex} " +
                      $"choice={choiceIndex}, RT(fr)={rtFrames}, key={_responseKey}, dev={_responseDevice}");
        }
    }

    public void EndTrial()
    {
        if (!_trialActive || _writer == null)
            return;

        // Sanitize string cells so payloads can't break TSV structure.
        string[] cols = new[]
        {
            _trialIndex.ToString(),
            SanitizeCell(_conditionID),
            _headingDeg.ToString("G4"),
            _onsetFrame.ToString(),
            _transStartFrame.ToString(),
            _transEndFrame.ToString(),
            _totalFrames.ToString(),
            _seedA0.ToString(),
            _seedA1.ToString(),
            _seedB2.ToString(),
            _seedB3.ToString(),
            _translationSpeed_degPerSec.ToString("G4"),
            _viewDistance_m.ToString("G4"),
            _responseChoiceIndex.ToString(),
            _responseRT_frames.ToString(),
            SanitizeCell(_responseKey),
            SanitizeCell(_responseDevice),
            SanitizeCell(_mkrows),
            SanitizeCell(_colorrows)
        };

        string line = string.Join("\t", cols);
        _writer.WriteLine(line);
        _writer.Flush();

        if (debugLog)
        {
            Debug.Log($"[CsvLogger] EndTrial() row written for trialIndex={_trialIndex}");
        }

        _trialActive = false;
    }

    public void EndSession()
    {
        if (debugLog)
        {
            Debug.Log("[CsvLogger] EndSession()");
        }
        // File stays open until OnDestroy.
    }
}