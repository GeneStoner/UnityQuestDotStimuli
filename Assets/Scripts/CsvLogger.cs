// FILE: CsvLogger.cs
using System;
using System.IO;
using System.Text;
using System.Collections.Generic;
using UnityEngine;
using CondLib = StimulusConditionsLibrary;

[DisallowMultipleComponent]
public class CsvLogger : MonoBehaviour
{
    [Header("Android/Quest Storage")]
    [Tooltip("On Android/Quest, write to external storage (accessible via ADB) instead of internal app storage.")]
    public bool useExternalStorageOnAndroid = true;

    [Header("Subject (optional but recommended)")]
    public string subjectId = "S000";
    public string subjectNotes = "";
    public int subjectAge = -1;
    public string subjectSex = "";
    public string subjectHandedness = "";

    [Header("Build (optional)")]
    public string applicationVersion = "0.1.4";
    public string gitCommit = "";
    public string gitBranch = "";
    public string experimentVersion = "";

    [Header("Logging controls")]
    [Tooltip("If false (recommended), TSV payload columns for mkrows/colorrows are left empty. Hash columns still logged.")]
    public bool writeTrajectoryPayloads = false;

    // ---------------- internal ----------------
    private string _tsvPath;
    private string _metaPath;

    private StreamWriter _tsv;
    private bool _headerWritten;

    private bool _sessionOpen;
    private bool _metaDirty;

    // --- block/session counts ---
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

    // rotation config (0/1), or -1 if unknown
    private int _curRotCfg = -1;

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

    // per-trial hashes
    private uint _curMkHash32 = 0;
    private uint _curColorHash32 = 0;

    // trial timing / seeds
    private int _curOn = -1, _curTS = -1, _curTE = -1, _curN = -1;
    private int _curSeedA0 = 0, _curSeedA1 = 0, _curSeedB2 = 0, _curSeedB3 = 0;

    // session constants
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

    // Sidecar write guard (once per session/file)
    private bool _sidecarWritten = false;

    void Awake()
    {
        Debug.Log($"[CsvLogger] Awake: useExternalStorageOnAndroid={useExternalStorageOnAndroid}, platform={Application.platform}");
        Debug.Log($"[CsvLogger] persistentDataPath={Application.persistentDataPath}");
    }

    // -------- Trajectory library (64 entries expected) --------
    private struct TrajDef
    {
        public string stimKey;       // stable key for analyzers
        public string cond;
        public int rotCfg;
        public float transDeg;
        public string delayedColor;  // "R" or "G"
        public string mkPayload;
        public string colorPayload;
        public uint mkHash32;
        public uint colorHash32;
    }

    // Keyed by stimKey
    private readonly Dictionary<string, TrajDef> _trajLib = new Dictionary<string, TrajDef>(128);

    // fixed column order
    private static readonly string[] Columns = new[]
    {
        "Trial","Cond","RotCfg","TransDeg",
        "RespDeg","RespIndex","RespDigit","RTf",
        "OnsetFrame","TransStartFrame","TransEndFrame","TotalFrames",
        "SeedA0","SeedA1","SeedB2","SeedB3",
        "DelayedFieldColor","EndKey","Device",
        "MkHash32","ColorHash32",
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

        Debug.Log($"[CsvLogger] BeginSession: platform={_platform}, path={_tsvPath}");

        try
        {
            var dir = Path.GetDirectoryName(_tsvPath);
            if (string.IsNullOrEmpty(dir))
                dir = Application.persistentDataPath;

            Debug.Log($"[CsvLogger] Creating directory: {dir}");
            Directory.CreateDirectory(dir);

            Debug.Log($"[CsvLogger] Opening file for writing: {_tsvPath}");
            _tsv = new StreamWriter(_tsvPath, append: false, encoding: new UTF8Encoding(false));
            _headerWritten = false;

            Debug.Log($"[CsvLogger] File opened successfully: {_tsvPath}");
        }
        catch (Exception e)
        {
            Debug.LogError($"[CsvLogger] FAILED to create session file: {_tsvPath}\nError: {e}");
            _tsv = null;
            _sessionOpen = false;
            throw; // Re-throw so TrialBlockRunner knows logging failed
        }

        ResetTrialState();

        _startedTrials = 0;
        _completedTrials = 0;
        _requeuedTrials = 0;

        _trialOpen = false;
        _sidecarWritten = false;

        // new session file => new trajectory library
        _trajLib.Clear();

        _metaDirty = true;
        _sessionOpen = true;

        WriteHeaderIfNeeded();
        TryWriteMetaJson();
    }

    public void EndSession()
    {
        if (!_sessionOpen) return;

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

            // Verify file exists and log final status
            if (!string.IsNullOrEmpty(_tsvPath) && File.Exists(_tsvPath))
            {
                var fileInfo = new FileInfo(_tsvPath);
                Debug.Log($"[CsvLogger] SESSION COMPLETE: {_completedTrials} trials saved to:\n  {_tsvPath}\n  File size: {fileInfo.Length} bytes");
            }
            else
            {
                Debug.LogError($"[CsvLogger] SESSION ENDED but file not found: {_tsvPath}");
            }
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

        TryFinalizeAbortedTrialRow("BeginTrial");

        _startedTrials++;

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
        _curRotCfg = trial.rotationConfig;

        _curOn = trial.onsetFrame;
        _curTS = trial.translationStartFrame;
        _curTE = trial.translationEndFrame;
        _curN = trial.totalFrames;

        _curSeedA0 = trial.seedA0;
        _curSeedA1 = trial.seedA1;
        _curSeedB2 = trial.seedB2;
        _curSeedB3 = trial.seedB3;

        _curDelayedFieldColor = (trial.delayedFieldColorCode == ExperimentSpec.COLOR_RED) ? "R" : "G";

        _trialOpen = true;
    }

    // Lenient for older callers
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
        _curMotionTypeRows = mkPayload ?? "";
        _curMkHash32 = Fnv1a32(_curMotionTypeRows);
    }

    public void LogColorRows(int trialIndex, string colorPayload)
    {
        _curColorRows = colorPayload ?? "";
        _curColorHash32 = Fnv1a32(_curColorRows);
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

        string mkOut = writeTrajectoryPayloads ? Sanitize(_curMotionTypeRows) : "";
        string colOut = writeTrajectoryPayloads ? Sanitize(_curColorRows) : "";

        string line =
            _curTrialIndex + "\t" +
            _curCond + "\t" +
            _curRotCfg + "\t" +
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
            _curMkHash32.ToString("X8") + "\t" +
            _curColorHash32.ToString("X8") + "\t" +
            mkOut + "\t" +
            colOut;

        try
        {
            _tsv.WriteLine(line);
            _tsv.Flush();

            _completedTrials++;
            _metaDirty = true;

            // Log progress every 10 trials
            if (_completedTrials % 10 == 0 || _completedTrials == 1)
            {
                Debug.Log($"[CsvLogger] Trial {_completedTrials} written to: {_tsvPath}");
            }
        }
        catch (Exception e)
        {
            Debug.LogError($"[CsvLogger] FAILED to write trial {_curTrialIndex}: {e}");
        }

        _trialOpen = false;
    }

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

    // -------- trajectory library API (called by TrialBlockRunner) --------

    public static string MakeStimKey(string cond, int rotCfg, float transDeg, string delayedColor)
    {
        return $"{cond}|Rot{rotCfg}|H{transDeg:0.###}|Del{delayedColor}";
    }

    public void RegisterTrajectoryDefinition(
        string stimKey,
        string cond,
        int rotCfg,
        float transDeg,
        string delayedColor,
        string mkPayload,
        string colorPayload
    )
    {
        if (string.IsNullOrEmpty(stimKey)) return;

        mkPayload = mkPayload ?? "";
        colorPayload = colorPayload ?? "";

        var td = new TrajDef
        {
            stimKey = stimKey,
            cond = cond ?? "",
            rotCfg = rotCfg,
            transDeg = transDeg,
            delayedColor = delayedColor ?? "",
            mkPayload = mkPayload,
            colorPayload = colorPayload,
            mkHash32 = Fnv1a32(mkPayload),
            colorHash32 = Fnv1a32(colorPayload)
        };

        if (!_trajLib.ContainsKey(stimKey))
            _trajLib.Add(stimKey, td);
    }

    // -------- Sidecar (called by TrialBlockRunner) --------

    public void WriteSidecarOnce(
        ExperimentSpec spec,
        StimulusBuilder builder,
        Fixation_Controller fixation,
        List<ExperimentSpec.PlannedTrial> plannedTrials,
        bool monitorPreviewMode,
        float previewScale,
        bool useSeparatePreviewScales,
        float previewDotScale,
        float previewFixationScale,
        float previewApertureScale,
        Camera cam
    )
    {
        if (_sidecarWritten) return;
        if (string.IsNullOrEmpty(_tsvPath))
        {
            Debug.LogWarning("[CsvLogger] WriteSidecarOnce: _tsvPath not set yet.");
            return;
        }

        string sidecarPath = _tsvPath + ".sidecar.json";

        try
        {
            string esc(string s) => (s ?? "")
                .Replace("\\", "\\\\")
                .Replace("\"", "\\\"")
                .Replace("\r", "\\r")
                .Replace("\n", "\\n");

            string f(float x) => float.IsNaN(x)
                ? "null"
                : x.ToString("0.########", System.Globalization.CultureInfo.InvariantCulture);

            int plannedN = (plannedTrials != null) ? plannedTrials.Count : -1;
            int uniqueN = (spec != null) ? spec.GetUniqueStimulusCount() : -1;

            string camName = (cam != null) ? cam.name : "";
            string camProj = (cam != null) ? (cam.orthographic ? "orthographic" : "perspective") : "unknown";

            float fixInnerDeg = float.NaN, fixOuterDeg = float.NaN;
            float zOut = float.NaN, zCross = float.NaN, zIn = float.NaN;
            float fixPreviewScale = float.NaN;

            if (fixation != null)
            {
                fixInnerDeg = fixation.innerDiam_deg;
                fixOuterDeg = fixation.outerDiam_deg;
                zOut = fixation.zOuterRing;
                zCross = fixation.zCross;
                zIn = fixation.zInnerRing;
                fixPreviewScale = fixation.previewScale;
            }

            var sb = new StringBuilder(16384);
            sb.Append("{\n");
            sb.Append("  \"schema_version\": \"vrdots.sidecar.v3\",\n");
            sb.Append("  \"created_iso8601\": \"").Append(esc(DateTimeOffset.Now.ToString("o"))).Append("\",\n");
            sb.Append("  \"data_file\": \"").Append(esc(Path.GetFileName(_tsvPath))).Append("\",\n");
            sb.Append("  \"sidecar_file\": \"").Append(esc(Path.GetFileName(sidecarPath))).Append("\",\n");

            sb.Append("  \"experiment_spec\": {\n");
            sb.Append("    \"spec_name\": \"").Append(esc(spec != null ? spec.name : "")).Append("\",\n");
            sb.Append("    \"unique_stimulus_count\": ").Append(uniqueN).Append(",\n");
            sb.Append("    \"planned_trials\": ").Append(plannedN).Append("\n");
            sb.Append("  },\n");

            sb.Append("  \"calibration_colors\": {\n");
            if (spec != null)
            {
                sb.Append("    \"rgba_red\": [").Append(f(spec.rgbaRed.r)).Append(", ").Append(f(spec.rgbaRed.g)).Append(", ").Append(f(spec.rgbaRed.b)).Append(", ").Append(f(spec.rgbaRed.a)).Append("],\n");
                sb.Append("    \"rgba_green\": [").Append(f(spec.rgbaGreen.r)).Append(", ").Append(f(spec.rgbaGreen.g)).Append(", ").Append(f(spec.rgbaGreen.b)).Append(", ").Append(f(spec.rgbaGreen.a)).Append("]\n");
            }
            else
            {
                sb.Append("    \"rgba_red\": null,\n");
                sb.Append("    \"rgba_green\": null\n");
            }
            sb.Append("  },\n");

            sb.Append("  \"preview\": {\n");
            sb.Append("    \"monitor_preview_mode\": ").Append(monitorPreviewMode ? "true" : "false").Append(",\n");
            sb.Append("    \"preview_scale\": ").Append(f(previewScale)).Append(",\n");
            sb.Append("    \"use_separate_preview_scales\": ").Append(useSeparatePreviewScales ? "true" : "false").Append(",\n");
            sb.Append("    \"preview_dot_scale\": ").Append(f(previewDotScale)).Append(",\n");
            sb.Append("    \"preview_fixation_scale\": ").Append(f(previewFixationScale)).Append(",\n");
            sb.Append("    \"preview_aperture_scale\": ").Append(f(previewApertureScale)).Append("\n");
            sb.Append("  },\n");

            sb.Append("  \"camera\": {\n");
            sb.Append("    \"name\": \"").Append(esc(camName)).Append("\",\n");
            sb.Append("    \"projection\": \"").Append(esc(camProj)).Append("\",\n");
            sb.Append("    \"field_of_view_deg\": ").Append(f(cam != null ? cam.fieldOfView : float.NaN)).Append(",\n");
            sb.Append("    \"orthographic_size\": ").Append(f(cam != null ? cam.orthographicSize : float.NaN)).Append(",\n");
            sb.Append("    \"near_clip\": ").Append(f(cam != null ? cam.nearClipPlane : float.NaN)).Append(",\n");
            sb.Append("    \"far_clip\": ").Append(f(cam != null ? cam.farClipPlane : float.NaN)).Append("\n");
            sb.Append("  },\n");

            sb.Append("  \"stimulus_builder\": {\n");
            sb.Append("    \"dots_per_field\": ").Append(builder != null ? builder.dotsPerField : -1).Append(",\n");
            sb.Append("    \"aperture_diameter_deg\": ").Append(f(builder != null ? builder.apertureDeg : float.NaN)).Append(",\n");
            sb.Append("    \"dot_size_m\": ").Append(f(builder != null ? builder.dotSizeMeters : float.NaN)).Append(",\n");
            sb.Append("    \"respawn_when_out_of_bounds\": ").Append((builder != null && builder.respawnWhenOutOfBounds) ? "true" : "false").Append("\n");
            sb.Append("  },\n");

            sb.Append("  \"fixation\": {\n");
            sb.Append("    \"preview_scale\": ").Append(f(fixPreviewScale)).Append(",\n");
            sb.Append("    \"inner_diameter_deg\": ").Append(f(fixInnerDeg)).Append(",\n");
            sb.Append("    \"outer_diameter_deg\": ").Append(f(fixOuterDeg)).Append(",\n");
            sb.Append("    \"z_outer\": ").Append(f(zOut)).Append(",\n");
            sb.Append("    \"z_cross\": ").Append(f(zCross)).Append(",\n");
            sb.Append("    \"z_inner\": ").Append(f(zIn)).Append("\n");
            sb.Append("  },\n");

            sb.Append("  \"trajectory_library\": {\n");
            sb.Append("    \"write_payloads_in_tsv\": ").Append(writeTrajectoryPayloads ? "true" : "false").Append(",\n");
            sb.Append("    \"hash_algorithm\": \"FNV-1a-32\",\n");
            sb.Append("    \"count\": ").Append(_trajLib.Count).Append(",\n");
            sb.Append("    \"entries\": [\n");

            int k = 0;
            foreach (var kv in _trajLib)
            {
                var td = kv.Value;
                sb.Append("      {\n");
                sb.Append("        \"stim_key\": \"").Append(esc(td.stimKey)).Append("\",\n");
                sb.Append("        \"cond\": \"").Append(esc(td.cond)).Append("\",\n");
                sb.Append("        \"rot_cfg\": ").Append(td.rotCfg).Append(",\n");
                sb.Append("        \"trans_deg\": ").Append(f(td.transDeg)).Append(",\n");
                sb.Append("        \"delayed_field_color\": \"").Append(esc(td.delayedColor)).Append("\",\n");
                sb.Append("        \"mk_hash32\": \"").Append(td.mkHash32.ToString("X8")).Append("\",\n");
                sb.Append("        \"color_hash32\": \"").Append(td.colorHash32.ToString("X8")).Append("\",\n");
                sb.Append("        \"mk_payload\": \"").Append(esc(td.mkPayload)).Append("\",\n");
                sb.Append("        \"color_payload\": \"").Append(esc(td.colorPayload)).Append("\"\n");
                sb.Append("      }");
                k++;
                sb.Append(k < _trajLib.Count ? ",\n" : "\n");
            }

            sb.Append("    ]\n");
            sb.Append("  }\n");
            sb.Append("}\n");

            File.WriteAllText(sidecarPath, sb.ToString(), new UTF8Encoding(false));
            _sidecarWritten = true;

            Debug.Log("[CsvLogger] Wrote sidecar: " + sidecarPath);
        }
        catch (Exception e)
        {
            Debug.LogError("[CsvLogger] WriteSidecarOnce failed: " + e);
        }
    }

    // ---------- Unity lifecycle flush ----------
    private void OnApplicationQuit() { SafeFlushAll("OnApplicationQuit"); }
    private void OnDisable() { SafeFlushAll("OnDisable"); }
    private void OnDestroy() { SafeFlushAll("OnDestroy"); }

    private void SafeFlushAll(string why)
    {
        if (!_sessionOpen) return;

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

        if (_curRtFrames < 0) _curRtFrames = -1;
        if (string.IsNullOrEmpty(_curEndKey)) _curEndKey = "ABORT";
        if (string.IsNullOrEmpty(_curDevice)) _curDevice = why;

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

        _curRotCfg = -1;
        _curDelayedFieldColor = "";

        _curRespDeg = -1f;
        _curRespIndex = -1;
        _curRespDigit = -1;
        _curRtFrames = -1;
        _curEndKey = "";
        _curDevice = "";

        _curMotionTypeRows = "";
        _curColorRows = "";

        _curMkHash32 = 0;
        _curColorHash32 = 0;

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
        string f(float x) => float.IsNaN(x) ? "null" : x.ToString("0.########", System.Globalization.CultureInfo.InvariantCulture);
        string nNullFloat(float? x) => x.HasValue ? f(x.Value) : "null";

        var sb = new StringBuilder(4096);
        sb.Append("{\n");
        sb.Append("  \"schema_version\": \"vrdots.meta.v2\",\n");
        sb.Append("  \"logging\": {\n");
        sb.Append("    \"tsv_delimiter\": \"\\t\",\n");
        sb.Append("    \"write_payloads_in_tsv\": ").Append(writeTrajectoryPayloads ? "true" : "false").Append(",\n");
        sb.Append("    \"hash_algorithm\": \"FNV-1a-32\",\n");
        sb.Append("    \"columns\": [");
        for (int i = 0; i < Columns.Length; i++)
        {
            sb.Append("\"").Append(Columns[i]).Append("\"");
            if (i < Columns.Length - 1) sb.Append(", ");
        }
        sb.Append("]\n");
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

    private string ResolvePath(string path)
    {
        if (string.IsNullOrWhiteSpace(path))
            path = "vr_dots_session.tsv";

        bool hasDir = path.Contains("/") || path.Contains("\\");

        #if UNITY_ANDROID && !UNITY_EDITOR
        // On Android, always use Android-appropriate path regardless of what was passed in
        // This handles the case where outputFileName in Inspector contains a Mac path
        string filename = hasDir ? Path.GetFileName(path) : path;
        string basePath = GetDataPath();
        string resolvedPath = Path.Combine(basePath, filename);
        Debug.Log($"[CsvLogger] ResolvePath: input='{path}' -> Android output='{resolvedPath}'");
        return resolvedPath;
        #else
        if (!hasDir)
        {
            string basePath = GetDataPath();
            return Path.Combine(basePath, path);
        }
        return path;
        #endif
    }

    private string GetDataPath()
    {
        // On Android/Quest, optionally use external storage for easier ADB access
        #if UNITY_ANDROID && !UNITY_EDITOR
        if (useExternalStorageOnAndroid)
        {
            // Use external files directory: /sdcard/Android/data/<package>/files/
            // This is accessible via ADB without root
            string externalPath = GetAndroidExternalFilesDir();
            if (!string.IsNullOrEmpty(externalPath))
            {
                Debug.Log($"[CsvLogger] Using Android external storage: {externalPath}");
                return externalPath;
            }
            Debug.LogWarning("[CsvLogger] Failed to get Android external files dir, falling back to persistentDataPath");
        }
        #endif

        return Application.persistentDataPath;
    }

    #if UNITY_ANDROID && !UNITY_EDITOR
    private static string GetAndroidExternalFilesDir()
    {
        try
        {
            using (var unityPlayer = new AndroidJavaClass("com.unity3d.player.UnityPlayer"))
            using (var activity = unityPlayer.GetStatic<AndroidJavaObject>("currentActivity"))
            using (var externalFilesDir = activity.Call<AndroidJavaObject>("getExternalFilesDir", (string)null))
            {
                if (externalFilesDir != null)
                {
                    return externalFilesDir.Call<string>("getAbsolutePath");
                }
            }
        }
        catch (Exception e)
        {
            Debug.LogError($"[CsvLogger] GetAndroidExternalFilesDir failed: {e}");
        }
        return null;
    }
    #endif

    private static string MakeSessionIdFromPath(string path)
    {
        return Path.GetFileNameWithoutExtension(path) ?? "vr_dots_session";
    }

    private static string Sanitize(string s)
    {
        if (string.IsNullOrEmpty(s)) return "";
        return s.Replace("\t", " ").Replace("\r", " ").Replace("\n", " ");
    }

    private static string F(float x) => x.ToString("0.###", System.Globalization.CultureInfo.InvariantCulture);

    private static float ResponseDirToDeg(string dir)
    {
        switch ((dir ?? "").ToUpperInvariant())
        {
            case "E": return 0f;
            case "NE": return 45f;
            case "N": return 90f;
            case "NW": return 135f;
            case "W": return 180f;
            case "SW": return 225f;
            case "S": return 270f;
            case "SE": return 315f;
            default: return -1f;
        }
    }

    // FNV-1a 32-bit hash over UTF-8 bytes of a string.
    private static uint Fnv1a32(string s)
    {
        if (string.IsNullOrEmpty(s)) return 0;

        unchecked
        {
            const uint offset = 2166136261u;
            const uint prime = 16777619u;
            uint h = offset;

            byte[] bytes = Encoding.UTF8.GetBytes(s);
            for (int i = 0; i < bytes.Length; i++)
            {
                h ^= bytes[i];
                h *= prime;
            }
            return h;
        }
    }
}