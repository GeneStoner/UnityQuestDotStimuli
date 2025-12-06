using System.Collections.Generic;
using System.Text;
using UnityEngine;
using CondLib = StimulusConditionsLibrary;

[DisallowMultipleComponent]
public class TrialBlockRunner : MonoBehaviour
{
    [Header("References")]
    public ExperimentSpec    spec;
    public StimulusBuilder   builder;
    public CsvLogger         csvLogger;
    public StimDebugHUD      hud;      // optional, can be null

    [Header("Control")]
    public bool autoStartOnPlay = true;
    public bool loopBlock       = false;

    private List<ExperimentSpec.PlannedTrial> _trials;
    private int   _trialIdx    = -1;
    private float _accum;
    private float _simDt;
    private int   _frameInTrial;

    private CondLib.StimulusCondition   _currentCond;
    private ExperimentSpec.PlannedTrial _currentTrial;
    private System.Random               _rng;

    // For mkrows / colorrows payload accumulation
    private StringBuilder _mkPayloadBuilder;
    private StringBuilder _colorPayloadBuilder;

    // ---------------------------------------------------------------------
    void Awake()
    {
        if (spec == null || builder == null)
        {
            Debug.LogError("[TrialBlockRunner] Assign 'spec' and 'builder' in inspector.");
            enabled = false;
            return;
        }

        _simDt = spec.SimDt;
        _rng   = new System.Random(1234567);
    }

    void Start()
    {
        Debug.Log("[TrialBlockRunner] Start() on GameObject: " + gameObject.name);
        Debug.Log("[TrialBlockRunner] autoStartOnPlay = " + autoStartOnPlay);

        Debug.Log("[TrialBlockRunner] Ref check: " +
                  $"spec={(spec ? spec.name : "NULL")}, " +
                  $"builder={(builder ? builder.name : "NULL")}, " +
                  $"csvLogger={(csvLogger ? csvLogger.name : "NULL")}, " +
                  $"hud={(hud ? hud.name : "NULL")}");

        if (autoStartOnPlay)
        {
            BeginBlock();
        }
    }

    // ---------------------------------------------------------------------
    public void BeginBlock()
    {
        Debug.Log("[TrialBlockRunner] BeginBlock()");

        _trials = spec.GetPlannedTrials(_rng);
        if (_trials == null || _trials.Count == 0)
        {
            Debug.LogError("[TrialBlockRunner] No trials generated.");
            enabled = false;
            return;
        }

        _trialIdx = -1;

        if (csvLogger != null)
        {
            Debug.Log("[TrialBlockRunner] Calling CsvLogger.BeginSession()");
            csvLogger.BeginSession(spec, _trials);
        }

        if (hud != null)
        {
            Debug.Log("[TrialBlockRunner] Binding HUD.");
            hud.Bind(this);
        }

        NextTrial();
    }

    void NextTrial()
    {
        _trialIdx++;

        if (_trialIdx >= _trials.Count)
        {
            if (csvLogger != null)
            {
                Debug.Log("[TrialBlockRunner] Ending session in CsvLogger.");
                csvLogger.EndSession();
            }

            if (loopBlock)
            {
                Debug.Log("[TrialBlockRunner] Block complete, looping.");
                _trialIdx = -1;
                NextTrial();
            }
            else
            {
                Debug.Log("[TrialBlockRunner] Block complete, disabling TrialBlockRunner.");
                enabled = false;
            }
            return;
        }

        _currentTrial = _trials[_trialIdx];
        _currentCond  = spec.BuildEffectiveCondition(_currentTrial);
        _frameInTrial = 0;
        _accum        = 0f;

        // reset mk/color payload builders for this trial
        _mkPayloadBuilder    = new StringBuilder();
        _colorPayloadBuilder = new StringBuilder();

        // Configure builder from spec
        builder.viewDistanceMeters = spec.viewDistance_m;
        builder.apertureDeg        = spec.apertureRadius_deg * 2f; // radius -> diameter
        builder.dotSizeMeters      = spec.dotSize_deg * spec.GetMetersPerDegree();
        builder.dotsPerField       = spec.dotsPerField;
        builder.randomSeed         = _currentTrial.seedA0;

        builder.BuildFromCondition(_currentCond);

        if (csvLogger != null)
        {
            Debug.Log("[TrialBlockRunner] Calling CsvLogger.BeginTrial()");
            csvLogger.BeginTrial(_currentTrial, spec, _currentCond);
        }

        Debug.Log($"[TrialBlockRunner] Trial {_trialIdx + 1}/{_trials.Count}: " +
                  $"{_currentTrial.conditionID}, heading={_currentTrial.headingDeg}°, " +
                  $"frames={_currentTrial.totalFrames}");
    }

    void Update()
    {
        _accum += Time.deltaTime;
        while (_accum >= _simDt)
        {
            _accum -= _simDt;
            SimStep();
        }

        if (hud != null)
            hud.Tick();
    }

    void SimStep()
    {
        if (_currentCond == null) return;

        int N = _currentTrial.totalFrames;

        // If we've run off the end for any reason, end trial and advance
        if (_frameInTrial < 0 || _frameInTrial >= N)
        {
            EndCurrentTrialAndAdvance();
            return;
        }

        // On the FIRST frame of this trial, write the summary CSV row
        if (_frameInTrial == 0 && csvLogger != null)
        {
            Debug.Log("[TrialBlockRunner] Calling CsvLogger.LogTrialRow()");
            csvLogger.LogTrialRow(
                _currentTrial.index,
                _currentTrial.conditionID,
                _currentTrial.headingDeg,
                _currentTrial.onsetFrame,
                _currentTrial.translationStartFrame,
                _currentTrial.translationEndFrame,
                _currentTrial.totalFrames,
                _currentTrial.seedA0,
                _currentTrial.seedA1,
                _currentTrial.seedB2,
                _currentTrial.seedB3
            );
        }

        // Apply color & visibility for this frame
        builder.ApplyAppearance(_currentCond, _frameInTrial);

        float dt           = _simDt;
        float metersPerDeg = spec.GetMetersPerDegree();

        // Step each subfield according to its MotionKind
        for (int i = 0; i < builder.Subfields.Length; i++)
        {
            var mk = _currentCond.subfields[i].motionKindByFrame[_frameInTrial];

            switch (mk)
            {
                case CondLib.MotionKind.RotationCW:
                    builder.StepRotation(i, spec.rotationSpeed_degPerSec, dt, -1);
                    break;

                case CondLib.MotionKind.RotationCCW:
                    builder.StepRotation(i, spec.rotationSpeed_degPerSec, dt, +1);
                    break;

                case CondLib.MotionKind.Linear:
                {
                    float th        = _currentTrial.headingDeg * Mathf.Deg2Rad;
                    float speed_mps = spec.translationSpeed_degPerSec * metersPerDeg;
                    Vector2 d       = new Vector2(Mathf.Cos(th), Mathf.Sin(th)) * (speed_mps * dt);
                    builder.StepTranslation(i, d, _frameInTrial);
                    break;
                }

                case CondLib.MotionKind.NonCoherent:
                {
                    builder.StepNonCoherentBalanced(
                        i,
                        spec.translationSpeed_degPerSec,
                        dt,
                        metersPerDeg,
                        _frameInTrial
                    );
                    break;
                }

                case CondLib.MotionKind.None:
                default:
                    break;
            }
        }

        // --- Accumulate mkrows / colorrows payload for this frame ---
        if (csvLogger != null && _currentCond.subfields != null)
        {
            int subCount = _currentCond.subfields.Length;
            int[] mkCodes      = new int[subCount];
            string[] colorCodes = new string[subCount];

            for (int i = 0; i < subCount; i++)
            {
                var sf = _currentCond.subfields[i];

                // Motion kind as integer code
                if (sf.motionKindByFrame != null && _frameInTrial < sf.motionKindByFrame.Length)
                    mkCodes[i] = (int)sf.motionKindByFrame[_frameInTrial];
                else
                    mkCodes[i] = 0;

                // Color as single-letter code
                if (sf.colorByFrame != null && _frameInTrial < sf.colorByFrame.Length)
                {
                    Color c = sf.colorByFrame[_frameInTrial];
                    colorCodes[i] = EncodeColorLetter(c);
                }
                else
                {
                    colorCodes[i] = "K";   // treat missing as "black"/off
                }
            }

            if (_mkPayloadBuilder.Length > 0) _mkPayloadBuilder.Append(";");
            _mkPayloadBuilder.Append(string.Join("|", mkCodes));

            if (_colorPayloadBuilder.Length > 0) _colorPayloadBuilder.Append(";");
            _colorPayloadBuilder.Append(string.Join("|", colorCodes));
        }

        // Advance frame
        _frameInTrial++;

        // If we just finished the last valid frame, end trial and advance
        if (_frameInTrial >= _currentTrial.totalFrames)
        {
            EndCurrentTrialAndAdvance();
        }
    }

    private void EndCurrentTrialAndAdvance()
    {
        if (csvLogger != null)
        {
            // Flush mkrows/colorrows once per trial
            if (_mkPayloadBuilder != null && _mkPayloadBuilder.Length > 0)
                csvLogger.LogMkRows(_currentTrial.index, _mkPayloadBuilder.ToString());

            if (_colorPayloadBuilder != null && _colorPayloadBuilder.Length > 0)
                csvLogger.LogColorRows(_currentTrial.index, _colorPayloadBuilder.ToString());

            csvLogger.EndTrial();
        }

        NextTrial();
    }

    // --- Helper: map Color → single-letter code ---
    private string EncodeColorLetter(Color c)
    {
        // Near-black or transparent → "K"
        if (c.a < 0.5f || (c.r < 0.05f && c.g < 0.05f && c.b < 0.05f))
            return "K";

        // Dominant channel heuristics
        if (c.r >= c.g && c.r >= c.b) return "R";
        if (c.g >= c.r && c.g >= c.b) return "G";
        if (c.b >= c.r && c.b >= c.g) return "B";

        // Fallback
        return "Y";
    }

    // HUD accessors
    public int   TrialIndex   => _trialIdx;
    public int   TrialsCount  => _trials?.Count ?? 0;
    public int   FrameInTrial => _frameInTrial;
    public float SimHz        => spec.simHz;
    public ExperimentSpec.PlannedTrial CurrentTrial => _currentTrial;
}