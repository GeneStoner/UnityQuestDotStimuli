// FILE: CsvLogger.cs
using System;
using System.IO;
using System.Text;
using UnityEngine;
using CondLib = StimulusConditionsLibrary;

[DisallowMultipleComponent]
public class CsvLogger : MonoBehaviour
{
    [Header("Subject (optional but recommended)")]
    public string subjectId = "S000";
    public string subjectNotes = "";
    public int subjectAge = -1;           // optional
    public string subjectSex = "";        // optional
    public string subjectHandedness = ""; // optional

    [Header("Build (optional)")]
    public string applicationVersion = "0.1.4";
    public string gitCommit = "";
    public string gitBranch = "";
    public string experimentVersion = "";

    // ---------------- internal ----------------
    private string _tsvPath;
    private string _metaPath;

    private StreamWriter _tsv;
    private bool _headerWritten;

    private bool _sessionOpen;
    private bool _metaDirty;

    // --- block/session counts (clarified) ---
    // target_number_trials: intended target for this block/session (e.g., repeats-per-stimulus plan)
    // generated_trials: how many trials ExperimentSpec actually generated for this block run
    private int _targetNumberTrials = 0;
    private int _generatedTrials = 0;

    private int _startedTrials = 0;
    private int _completedTrials = 0;
    private int _requeuedTrials = 0;

    private float? _fpsMean = null;
    private float? _fpsStd = null;

    // current trial bookkeeping
    private int _curTrialIndex = -1;
    private string _curCond = "";
    private float _curTransDeg = 0f;

    // delayed-field color (R/G)
    private string _curDelayedFieldColor = "";

    // response stash until EndTrial writes the final row
    private float _curRespDeg = -1f;
    private int _curRespIndex = -1;
    private int _curRespDigit = -1;
    private int _curRtFrames = -1;
    private string _curEndKey = "";
    private string _curDevice = "";

    // payloads (per-frame, per-subfield)
    private string _curMotionTypeRows = "";
    private string _curColorRows = "";

    // trial timing / seeds (from LogTrialRow / BeginTrial)
    private int _curOn = -1, _curTS = -1, _curTE = -1, _curN = -1;
    private int _curSeedA0 = 0, _curSeedA1 = 0, _curSeedB2 = 0, _curSeedB3 = 0;

    // session constants (these come from BeginSession / BeginTrial)
    private string _sessionId = "";
    private string _createdIso = "";
    private string _timezone = "America/Los_Angeles";

    private string _unityVersion = "";
    private string _platform = "";

    private float _viewDistanceM = 0f;
    private float _translationSpeedDegPerSec = 0f;
    private float _rotationSpeedDegPerSec = 0f;

    private float _metersPerDegree = 0f;
    private float _apertureRadiusDeg = 0f;
    private float _dotSizeDeg = 0f;
    private float _dotSizeM = 0f;
    private int _dotsPerField = 0;
    private int _numSubfields = 0;
    private float _simDt = 0f;
    private float _simHz = 0f;

    // Track whether a trial has been started but not yet finalized (row not written).
    private bool _trialOpen = false;

    // fixed column order
    private static readonly string[] Columns = new[]
    {
        "Trial","Cond","TransDeg","RespDeg","RespIndex","RespDigit","RTf",
        "OnsetFrame","TransStartFrame","TransEndFrame","TotalFrames",
        "SeedA0","SeedA1","SeedB2","SeedB3","DelayedFieldColor","EndKey","Device",
        "MotionTypeByFrame_SubfieldCodes","ColorByFrame_SubfieldCodes"
    };

    // ---------- public API (called by TrialBlockRunner) ----------

    public void BeginSession(string path, float translationSpeed_degPerSec, float viewDistance_m)
    {
        if (_sessionOpen) EndSession();

        _translationSpeedDegPerSec = translationSpeed_degPerSec;
        _viewDistanceM = viewDistance_m;

        _unityVersion = Application.unityVersion;
        _platform = Application.platform.ToString();

        _createdIso = DateTimeOffset.Now.ToString("o");
        _sessionId = MakeSessionIdFromPath(path);

        _tsvPath = ResolvePath(path);
        _metaPath = _tsvPath + ".meta.json";

        // Robust directory creation
        var dir = Path.GetDirectoryName(_tsvPath);
        if (string.IsNullOrEmpty(dir))
            dir = Application.persistentDataPath;
        Directory.CreateDirectory(dir);

        _tsv = new StreamWriter(_tsvPath, append: false, encoding: new UTF8Encoding(false));
        _headerWritten = false;

        ResetTrialState();

        // NOTE: do NOT clear _targetNumberTrials/_generatedTrials here, because
        // TrialBlockRunner sets them after BeginSession().
        _startedTrials = 0;
        _completedTrials = 0;
        _requeuedTrials = 0;

        _trialOpen = false;

        _metaDirty = true;
        _sessionOpen = true;

        WriteHeaderIfNeeded();
        TryWriteMetaJson();
    }

    public void EndSession()
    {
        if (!_sessionOpen) return;

        // If a trial was started but never finalized, write an ABORT row so the file is internally consistent.
        TryFinalizeAbortedTrialRow("EndSession");

        try
        {
            _metaDirty = true;
            TryWriteMetaJson();
        }
        catch (Exception e)
        {
            Debug.LogError("[CsvLogger] EndSession meta write failed: " + e);
        }

        try
        {
            _tsv?.Flush();
            _tsv?.Close();
        }
        catch (Exception e)
        {
            Debug.LogError("[CsvLogger] EndSession TSV close failed: " + e);
        }
        finally
        {
            _tsv = null;
            _sessionOpen = false;
        }
    }

    public void BeginTrial(ExperimentSpec.PlannedTrial trial, ExperimentSpec spec, CondLib.StimulusCondition cond)
    {
        if (!_sessionOpen)
        {
            Debug.LogWarning("[CsvLogger] BeginTrial called but session is not open. Did you forget BeginSession()?");
            return;
        }

        // If somehow another trial is still open, finalize it as aborted.
        TryFinalizeAbortedTrialRow("BeginTrial");

        _startedTrials++;

        // Populate session-level stimulus constants from spec.
        if (spec != null)
        {
            _simDt = spec.SimDt;
            _simHz = spec.simHz;

            _apertureRadiusDeg = spec.apertureRadius_deg;
            _dotSizeDeg = spec.dotSize_deg;
            _dotsPerField = spec.dotsPerField;

            _rotationSpeedDegPerSec = spec.rotationSpeed_degPerSec;
            _translationSpeedDegPerSec = spec.translationSpeed_degPerSec;
            _viewDistanceM = spec.viewDistance_m;

            _metersPerDegree = spec.GetMetersPerDegree();
            _dotSizeM = _dotSizeDeg * _metersPerDegree;
        }

        _numSubfields = (cond != null && cond.subfields != null) ? cond.subfields.Length : 0;

        _metaDirty = true;
        TryWriteMetaJson();

        ResetTrialState();

        _curTrialIndex = trial.index;
        _curCond = trial.conditionID ?? "";
        _curTransDeg = trial.headingDeg;
        _curOn = trial.onsetFrame;
        _curTS = trial.translationStartFrame;
        _curTE = trial.translationEndFrame;
        _curN = trial.totalFrames;

        _curSeedA0 = trial.seedA0;
        _curSeedA1 = trial.seedA1;
        _curSeedB2 = trial.seedB2;
        _curSeedB3 = trial.seedB3;

        // delayed-field color (0=red, 1=green)
        _curDelayedFieldColor = (trial.delayedFieldColorCode == ExperimentSpec.COLOR_RED) ? "R" : "G";

        _trialOpen = true;
    }

    // Kept lenient for older callers
    public void LogTrialRow(
        int trialIndex,
        string conditionId,
        float headingDeg,
        int onsetFrame,
        int translationStartFrame,
        int translationEndFrame,
        int totalFrames,
        int seedA0,
        int seedA1,
        int seedB2,
        int seedB3,
        float translationSpeed_degPerSec,
        float viewDistance_m
    )
    {
        _curTrialIndex = trialIndex;
        _curCond = conditionId ?? "";
        _curTransDeg = headingDeg;

        _curOn = onsetFrame;
        _curTS = translationStartFrame;
        _curTE = translationEndFrame;
        _curN = totalFrames;

        _curSeedA0 = seedA0;
        _curSeedA1 = seedA1;
        _curSeedB2 = seedB2;
        _curSeedB3 = seedB3;

        _translationSpeedDegPerSec = translationSpeed_degPerSec;
        _viewDistanceM = viewDistance_m;
        _metaDirty = true;
    }

    public void LogMkRows(int trialIndex, string mkPayload)
    {
        if (trialIndex != _curTrialIndex) { /* tolerate */ }
        _curMotionTypeRows = mkPayload ?? "";
    }

    public void LogColorRows(int trialIndex, string colorPayload)
    {
        if (trialIndex != _curTrialIndex) { /* tolerate */ }
        _curColorRows = colorPayload ?? "";
    }

    public void LogResponse(int respIndex, int respDigit, string respDir, int rtFrames, string endKey, string device)
    {
        _curRespIndex = respIndex;
        _curRespDigit = respDigit;
        _curRtFrames = rtFrames;
        _curEndKey = endKey ?? "";
        _curDevice = device ?? "";
        _curRespDeg = ResponseDirToDeg(respDir);
    }

    public void EndTrial()
    {
        if (!_sessionOpen || _tsv == null) return;
        if (!_trialOpen) return;

        WriteHeaderIfNeeded();

        string line =
            _curTrialIndex + "\t" +
            _curCond + "\t" +
            F(_curTransDeg) + "\t" +
            F(_curRespDeg) + "\t" +
            _curRespIndex + "\t" +
            _curRespDigit + "\t" +
            _curRtFrames + "\t" +
            _curOn + "\t" +
            _curTS + "\t" +
            _curTE + "\t" +
            _curN + "\t" +
            _curSeedA0 + "\t" +
            _curSeedA1 + "\t" +
            _curSeedB2 + "\t" +
            _curSeedB3 + "\t" +
            _curDelayedFieldColor + "\t" +
            Sanitize(_curEndKey) + "\t" +
            Sanitize(_curDevice) + "\t" +
            Sanitize(_curMotionTypeRows) + "\t" +
            Sanitize(_curColorRows);

        _tsv.WriteLine(line);
        _tsv.Flush();

        _completedTrials++;
        _metaDirty = true;

        _trialOpen = false;
    }

    // --- New, explicit setters ---
    public void SetTargetNumberTrials(int n)
    {
        _targetNumberTrials = Mathf.Max(0, n);
        _metaDirty = true;
        if (_sessionOpen) TryWriteMetaJson();
    }

    public void SetGeneratedTrials(int n)
    {
        _generatedTrials = Mathf.Max(0, n);
        _metaDirty = true;
        if (_sessionOpen) TryWriteMetaJson();
    }

    // Back-compat: older code used this name for “planned”.
    // We now treat that as “generated by ExperimentSpec”.
    public void SetPlannedTrials(int n) => SetGeneratedTrials(n);

    public void AddRequeuedTrial()
    {
        _requeuedTrials++;
        _metaDirty = true;
        if (_sessionOpen) TryWriteMetaJson();
    }

    public void SetFpsStats(float mean, float std)
    {
        _fpsMean = mean;
        _fpsStd = std;
        _metaDirty = true;
        if (_sessionOpen) TryWriteMetaJson();
    }

    // ---------- Unity lifecycle flush (critical for “Stop” in editor) ----------

    private void OnApplicationQuit() { SafeFlushAll("OnApplicationQuit"); }
    private void OnDisable() { SafeFlushAll("OnDisable"); }
    private void OnDestroy() { SafeFlushAll("OnDestroy"); }

    private void SafeFlushAll(string why)
    {
        if (!_sessionOpen) return;

        // If we’re being torn down mid-trial, write an ABORT row.
        TryFinalizeAbortedTrialRow(why);

        try
        {
            _metaDirty = true;
            TryWriteMetaJson();
        }
        catch (Exception e)
        {
            Debug.LogError($"[CsvLogger] {why} meta write failed: {e}");
        }

        try { _tsv?.Flush(); } catch { }
        try { _tsv?.Close(); } catch { }

        _tsv = null;
        _sessionOpen = false;
    }

    // ---------- helpers ----------

    private void TryFinalizeAbortedTrialRow(string why)
    {
        if (!_trialOpen) return;
        if (!_sessionOpen || _tsv == null) return;

        // Minimal, safe defaults for an aborted row
        if (_curRtFrames < 0) _curRtFrames = -1;
        if (string.IsNullOrEmpty(_curEndKey)) _curEndKey = "ABORT";
        if (string.IsNullOrEmpty(_curDevice)) _curDevice = why;

        // If payloads aren’t present yet, leave them blank.
        EndTrial();
    }

    private void WriteHeaderIfNeeded()
    {
        if (_headerWritten || _tsv == null) return;
        _tsv.WriteLine(string.Join("\t", Columns));
        _tsv.Flush();
        _headerWritten = true;
        _metaDirty = true;
    }

    private void ResetTrialState()
    {
        _curTrialIndex = -1;
        _curCond = "";
        _curTransDeg = 0f;

        _curDelayedFieldColor = "";

        _curRespDeg = -1f;
        _curRespIndex = -1;
        _curRespDigit = -1;
        _curRtFrames = -1;
        _curEndKey = "";
        _curDevice = "";

        _curMotionTypeRows = "";
        _curColorRows = "";

        _curOn = _curTS = _curTE = _curN = -1;
        _curSeedA0 = _curSeedA1 = _curSeedB2 = _curSeedB3 = 0;
    }

    private void TryWriteMetaJson()
    {
        if (!_metaDirty) return;
        if (string.IsNullOrEmpty(_metaPath)) return;

        string json = BuildMetaJsonString();
        File.WriteAllText(_metaPath, json, new UTF8Encoding(false));
        _metaDirty = false;
    }

    private string BuildMetaJsonString()
    {
        string esc(string s) => (s ?? "")
            .Replace("\\", "\\\\")
            .Replace("\"", "\\\"")
            .Replace("\r", "\\r")
            .Replace("\n", "\\n");

        string f(float x) => float.IsNaN(x) ? "null" : x.ToString("0.########", System.Globalization.CultureInfo.InvariantCulture);
        string nNullFloat(float? x) => x.HasValue ? f(x.Value) : "null";

        var sb = new StringBuilder(8192);
        sb.Append("{\n");
        sb.Append("  \"schema_version\": \"vrdots.meta.v1\",\n");

        sb.Append("  \"subject\": {\n");
        sb.Append($"    \"subject_id\": \"{esc(subjectId)}\",\n");
        sb.Append($"    \"age\": {subjectAge},\n");
        sb.Append($"    \"sex\": \"{esc(subjectSex)}\",\n");
        sb.Append($"    \"handedness\": \"{esc(subjectHandedness)}\",\n");
        sb.Append($"    \"notes\": \"{esc(subjectNotes)}\"\n");
        sb.Append("  },\n");

        sb.Append("  \"session\": {\n");
        sb.Append($"    \"session_id\": \"{esc(_sessionId)}\",\n");
        sb.Append($"    \"created_iso8601\": \"{esc(_createdIso)}\",\n");
        sb.Append($"    \"timezone\": \"{esc(_timezone)}\",\n");
        sb.Append($"    \"data_file\": \"{esc(Path.GetFileName(_tsvPath))}\",\n");
        sb.Append($"    \"meta_file\": \"{esc(Path.GetFileName(_metaPath))}\",\n");
        sb.Append("    \"notes\": \"\"\n");
        sb.Append("  },\n");

        sb.Append("  \"build\": {\n");
        sb.Append($"    \"unity_version\": \"{esc(_unityVersion)}\",\n");
        sb.Append($"    \"platform\": \"{esc(_platform)}\",\n");
        sb.Append($"    \"application_version\": \"{esc(applicationVersion)}\",\n");
        sb.Append($"    \"git_commit\": \"{esc(gitCommit)}\",\n");
        sb.Append($"    \"git_branch\": \"{esc(gitBranch)}\",\n");
        sb.Append($"    \"experiment_version\": \"{esc(experimentVersion)}\"\n");
        sb.Append("  },\n");

        sb.Append("  \"stimulus\": {\n");
        sb.Append($"    \"view_distance_m\": {f(_viewDistanceM)},\n");
        sb.Append($"    \"meters_per_degree\": {f(_metersPerDegree)},\n");
        sb.Append($"    \"aperture_radius_deg\": {f(_apertureRadiusDeg)},\n");
        sb.Append($"    \"dot_size_deg\": {f(_dotSizeDeg)},\n");
        sb.Append($"    \"dot_size_m\": {f(_dotSizeM)},\n");
        sb.Append($"    \"dots_per_field\": {_dotsPerField},\n");
        sb.Append($"    \"num_subfields\": {_numSubfields},\n");
        sb.Append($"    \"sim_dt\": {f(_simDt)},\n");
        sb.Append($"    \"sim_hz\": {f(_simHz)},\n");
        sb.Append($"    \"translation_speed_deg_per_sec\": {f(_translationSpeedDegPerSec)},\n");
        sb.Append($"    \"rotation_speed_deg_per_sec\": {f(_rotationSpeedDegPerSec)},\n");
        sb.Append("    \"heading_convention\": \"0deg=+X (right), 90deg=+Y (up), CCW positive\"\n");
        sb.Append("  },\n");

        // IMPORTANT: these codes reflect the payload you are writing (and are now immune to enum reorder).
        sb.Append("  \"conditions\": {\n");
        sb.Append("    \"motion_type_map\": {\n");
        sb.Append("      \"0\": \"None\",\n");
        sb.Append("      \"1\": \"RotationCW\",\n");
        sb.Append("      \"2\": \"RotationCCW\",\n");
        sb.Append("      \"3\": \"Linear\",\n");
        sb.Append("      \"4\": \"NonCoherent\"\n");
        sb.Append("    },\n");
        sb.Append("    \"color_code_map\": {\n");
        sb.Append("      \"R\": \"Red\",\n");
        sb.Append("      \"G\": \"Green\",\n");
        sb.Append("      \"B\": \"Blue\",\n");
        sb.Append("      \"Y\": \"Yellow\",\n");
        sb.Append("      \"K\": \"Black/Off\"\n");
        sb.Append("    }\n");
        sb.Append("  },\n");

        sb.Append("  \"response\": {\n");
        sb.Append("    \"rt_units\": \"frames\"\n");
        sb.Append("  },\n");

        // logging
        sb.Append("  \"logging\": {\n");
        sb.Append("    \"tsv_delimiter\": \"\\t\",\n");
        sb.Append("    \"missing_int\": -1,\n");
        sb.Append("    \"missing_string\": \"\",\n");

        sb.Append("    \"columns\": [");
        for (int i = 0; i < Columns.Length; i++)
        {
            sb.Append($"\"{Columns[i]}\"");
            if (i < Columns.Length - 1) sb.Append(", ");
        }
        sb.Append("],\n");

        sb.Append("    \"column_descriptions\": {\n");
        sb.Append("      \"Trial\": \"0-based trial index within this session file\",\n");
        sb.Append("      \"Cond\": \"condition identifier (string)\",\n");
        sb.Append("      \"TransDeg\": \"translation heading in degrees (0=right, 90=up, CCW+)\",\n");
        sb.Append("      \"RespDeg\": \"response direction in degrees (same convention); -1 if none\",\n");
        sb.Append("      \"RespIndex\": \"0..7 choice index; -1 if none\",\n");
        sb.Append("      \"RespDigit\": \"keypad digit mapped from RespIndex; -1 if none\",\n");
        sb.Append("      \"RTf\": \"reaction time in simulation frames; -1 if none\",\n");
        sb.Append("      \"OnsetFrame\": \"frame index when delayed field becomes visible (simulation frames)\",\n");
        sb.Append("      \"TransStartFrame\": \"first frame index where translation is applied (inclusive); translation spans [TransStartFrame, TransEndFrame)\",\n");
        sb.Append("      \"TransEndFrame\": \"first frame index where translation is NOT applied (exclusive end)\",\n");
        sb.Append("      \"TotalFrames\": \"stimulus duration in simulation frames\",\n");
        sb.Append("      \"SeedA0\": \"random seed A0 (int32)\",\n");
        sb.Append("      \"SeedA1\": \"random seed A1 (int32)\",\n");
        sb.Append("      \"SeedB2\": \"random seed B2 (int32)\",\n");
        sb.Append("      \"SeedB3\": \"random seed B3 (int32)\",\n");
        sb.Append("      \"DelayedFieldColor\": \"delayed-onset field color after onset (R=Red, G=Green)\",\n");
        sb.Append("      \"EndKey\": \"key that ended response window, or ABORT if session stopped mid-trial\",\n");
        sb.Append("      \"Device\": \"input device label\",\n");
        sb.Append("      \"MotionTypeByFrame_SubfieldCodes\": \"per-frame motion-type codes; frames separated by ';', subfields by '|'\",\n");
        sb.Append("      \"ColorByFrame_SubfieldCodes\": \"per-frame color codes; frames separated by ';', subfields by '|'\"\n");
        sb.Append("    },\n");

        sb.Append("    \"payload_format\": {\n");
        sb.Append("      \"frame_delimiter\": \";\",\n");
        sb.Append("      \"subfield_delimiter\": \"|\",\n");
        sb.Append("      \"num_subfields_source\": \"stimulus.num_subfields\",\n");
        sb.Append("      \"frame_count_source\": \"TotalFrames\",\n");
        sb.Append("      \"frame_rate_hz_source\": \"stimulus.sim_hz\"\n");
        sb.Append("    }\n");

        sb.Append("  },\n");

        sb.Append("  \"stats\": {\n");
        sb.Append($"    \"target_number_trials\": {_targetNumberTrials},\n");
        sb.Append($"    \"generated_trials\": {_generatedTrials},\n");
        sb.Append($"    \"started_trials\": {_startedTrials},\n");
        sb.Append($"    \"completed_trials\": {_completedTrials},\n");
        sb.Append($"    \"requeued_trials\": {_requeuedTrials},\n");
        sb.Append($"    \"measured_fps_mean\": {nNullFloat(_fpsMean)},\n");
        sb.Append($"    \"measured_fps_std\": {nNullFloat(_fpsStd)}\n");
        sb.Append("  }\n");

        sb.Append("}\n");
        return sb.ToString();
    }

    private static string ResolvePath(string path)
    {
        if (string.IsNullOrWhiteSpace(path))
            path = "vr_dots_session.tsv";

        bool hasDir = path.Contains("/") || path.Contains("\\");
        if (!hasDir)
            return Path.Combine(Application.persistentDataPath, path);

        return path;
    }

    private static string MakeSessionIdFromPath(string path)
    {
        string name = Path.GetFileNameWithoutExtension(path) ?? "vr_dots_session";
        return name;
    }

    private static string Sanitize(string s)
    {
        if (string.IsNullOrEmpty(s)) return "";
        return s.Replace("\t", " ").Replace("\r", " ").Replace("\n", " ");
    }

    private static string F(float x)
    {
        return x.ToString("0.###", System.Globalization.CultureInfo.InvariantCulture);
    }

    private static float ResponseDirToDeg(string dir)
    {
        switch ((dir ?? "").ToUpperInvariant())
        {
            case "E":  return 0f;
            case "NE": return 45f;
            case "N":  return 90f;
            case "NW": return 135f;
            case "W":  return 180f;
            case "SW": return 225f;
            case "S":  return 270f;
            case "SE": return 315f;
            default:   return -1f;
        }
    }
}