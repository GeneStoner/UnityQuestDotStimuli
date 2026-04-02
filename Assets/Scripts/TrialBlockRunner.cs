// FILE: TrialBlockRunner.cs
//
// PARAMETER AUTHORITY:
// --------------------
// ExperimentSpec (ScriptableObject) is the SOURCE OF TRUTH for experiment parameters:
//   - viewDistance_m, apertureRadius_deg, dotSize_deg, dotsPerField
//   - rotation/translation speeds, fixation geometry, colors
//
// This script's Inspector fields are for:
//   - References to scene objects (spec, builder, fixation, csvLogger, etc.)
//   - Preview scaling (monitorPreviewMode, previewScale) - render-only, does NOT change truth
//   - Runtime control (startKey, maxResponseFrames, looping, logging options)
//
// At trial start, ExperimentSpec values are copied to StimulusBuilder and other components.
// Changing values in ExperimentSpec asset will affect the experiment.
// Changing preview scales here only affects monitor visibility, not the actual stimulus.
//
using System;
using System.Collections.Generic;
using System.Text;
using UnityEngine;
using UnityEngine.InputSystem;
using CondLib = StimulusConditionsLibrary;

[DisallowMultipleComponent]
public class TrialBlockRunner : MonoBehaviour
{
    [Header("References")]
    public ExperimentSpec spec;
    public StimulusBuilder builder;

    [Tooltip("Drag the Fixation_Controller component here (the one actually used in the scene).")]
    public Fixation_Controller fixation;

    public CsvLogger csvLogger;
    public StimDebugHUD hud;
    public TargetResponseController targetResponseController;

    [Tooltip("Optional: Shows animated spot in direction of subject's response")]
    public DirectionalFeedbackSpot directionalFeedback;

    [Header("Control")]
    public bool autoStartOnPlay = true;
    public bool loopBlock = false;

    [Header("Monitor Preview (render-only, does NOT change spec truth)")]
    public bool monitorPreviewMode = false;

    [Tooltip("Single uniform multiplier applied to aperture, dot size, and fixation geometry for monitor visibility.")]
    [Min(0.1f)] public float previewScale = 1f;

    [Tooltip("If enabled, allows separate scalars (advanced). If false, previewScale is used for everything.")]
    public bool useSeparatePreviewScales = false;

    [Tooltip("Scales dot diameter (meters) for monitor visibility. 1 = true size.")]
    [Min(0.1f)] public float previewDotScale = 1f;

    [Tooltip("Scales fixation geometry (meters) for monitor visibility. 1 = true size.")]
    [Min(0.1f)] public float previewFixationScale = 1f;

    [Tooltip("Scales aperture diameter (degrees) for monitor visibility. 1 = true size.")]
    [Min(0.1f)] public float previewApertureScale = 1f;

    [Header("Diagnostics")]
    public bool logRealizedGeometryEachTrial = true;

    [Header("Field A Preview")]
    [Tooltip("If true, show BOTH fields (sub0–sub3) static at frame-0 positions and correct depth during WaitingForStart, " +
             "so vergence is established before trial onset. Field B remains hidden until its normal delayed onset.")]
    public bool showFieldAPreview = true;

    [Header("Trial start / response")]
    public KeyCode startKey = KeyCode.Space;

    [Tooltip("Max frames to wait for response (0 = unlimited). Synced to TargetResponseController at trial start.")]
    public int maxResponseFrames = 0;

    [Header("XR Controller Input")]
    [Tooltip("Input Action Asset containing XR controller bindings (e.g., XRI Default Input Actions).")]
    public InputActionAsset xrInputActions;

    [Tooltip("Use right-hand trigger to start trials and confirm responses.")]
    public bool useRightHandTrigger = true;

    [Tooltip("Use left-hand trigger to start trials and confirm responses.")]
    public bool useLeftHandTrigger = true;

    [Header("Logging")]
    public string outputFileName = "Dots.tsv";
    public bool appendDateTimeToFilename = true;

    // ----------------- internal state -----------------
    private List<ExperimentSpec.PlannedTrial> _allPlannedTrials;
    private List<ExperimentSpec.PlannedTrial> _trialQueue;

    // XR input actions
    private InputAction _activateLeft;
    private InputAction _activateRight;
    private bool _xrTriggerPressedThisFrame;

    private int _startedTrialCount = 0;
    private float _accum;
    private float _simDt;

    private ExperimentSpec.PlannedTrial _currentTrial;
    private CondLib.StimulusCondition _currentCond;

    private int _frameInStimulus;
    private System.Random _rng;
    private int _sessionSeed;

    private StringBuilder _mkPayloadBuilder;
    private StringBuilder _colorPayloadBuilder;
    private StringBuilder _depthPayloadBuilder;

    private enum TrialPhase { WaitingForStart, Stimulus, TargetsResponse, Done }
    private TrialPhase _phase = TrialPhase.Done;

    private int _responseFrameIndex = 0;

    void Awake()
    {
        if (spec == null || builder == null)
        {
            Debug.LogError("[TrialBlockRunner] Assign 'spec' and 'builder' in inspector.", this);
            enabled = false;
            return;
        }

        // Load isoluminance calibration if available
        LoadCalibrationColors();

        _simDt = spec.SimDt;
        _sessionSeed = Environment.TickCount;
        _rng = new System.Random(_sessionSeed);
        Debug.Log($"[TrialBlockRunner] Session seed: {_sessionSeed}");

        // Setup XR input actions
        SetupXRInput();

        Debug.Log($"[TBR {GetInstanceID()}] Awake. fixationRef={(fixation ? fixation.GetInstanceID() : -1)}", this);
    }

    /// <summary>
    /// Load isoluminance calibration from flicker fusion and apply to ExperimentSpec colors.
    /// </summary>
    private void LoadCalibrationColors()
    {
        var cal = CalibrationData.Load();
        if (cal != null)
        {
            // Apply calibrated pure red and green (no cross-channel contamination)
            spec.rgbaRed = cal.GetRedColor();
            spec.rgbaGreen = cal.GetGreenColor();
            Debug.Log($"[TrialBlockRunner] Applied calibration: Red={cal.redIntensity:F3}, Green={cal.greenIntensity:F3} (mean from {cal.trialCount} trials)");
        }
        else
        {
            Debug.Log("[TrialBlockRunner] No calibration found. Using default ExperimentSpec colors.");
        }
    }

    void OnDestroy()
    {
        CleanupXRInput();
    }

    void OnDisable()
    {
        // Disable XR actions when component is disabled
        if (_activateLeft != null) _activateLeft.Disable();
        if (_activateRight != null) _activateRight.Disable();
    }

    void OnEnable()
    {
        // Re-enable XR actions when component is enabled
        if (_activateLeft != null) _activateLeft.Enable();
        if (_activateRight != null) _activateRight.Enable();
    }

    private void SetupXRInput()
    {
        if (xrInputActions == null)
        {
            Debug.Log("[TrialBlockRunner] No XR Input Actions assigned. XR controller input disabled.");
            return;
        }

        // Activate action is in the Interaction maps (XRI Left Interaction / XRI Right Interaction)
        var leftInteractionMap = xrInputActions.FindActionMap("XRI Left Interaction", false);
        var rightInteractionMap = xrInputActions.FindActionMap("XRI Right Interaction", false);

        if (leftInteractionMap != null && useLeftHandTrigger)
        {
            _activateLeft = leftInteractionMap.FindAction("Activate", false);
            if (_activateLeft != null)
            {
                _activateLeft.Enable();
                _activateLeft.performed += OnXRTriggerPressed;
                Debug.Log("[TrialBlockRunner] Left hand trigger (Activate) bound.");
            }
        }

        if (rightInteractionMap != null && useRightHandTrigger)
        {
            _activateRight = rightInteractionMap.FindAction("Activate", false);
            if (_activateRight != null)
            {
                _activateRight.Enable();
                _activateRight.performed += OnXRTriggerPressed;
                Debug.Log("[TrialBlockRunner] Right hand trigger (Activate) bound.");
            }
        }

        if (_activateLeft == null && _activateRight == null)
        {
            Debug.LogWarning("[TrialBlockRunner] Could not find 'Activate' action in XR Input Actions. " +
                           "Ensure 'XRI Left Interaction' and 'XRI Right Interaction' action maps exist.");
        }
    }

    private void CleanupXRInput()
    {
        if (_activateLeft != null)
        {
            _activateLeft.performed -= OnXRTriggerPressed;
            _activateLeft.Disable();
            _activateLeft = null;
        }

        if (_activateRight != null)
        {
            _activateRight.performed -= OnXRTriggerPressed;
            _activateRight.Disable();
            _activateRight = null;
        }
    }

    private void OnXRTriggerPressed(InputAction.CallbackContext context)
    {
        _xrTriggerPressedThisFrame = true;
        Debug.Log("[TrialBlockRunner] *** TRIGGER *** Build 2026-03-30");
    }

    void Start()
    {
        if (targetResponseController != null)
            targetResponseController.maxResponseFrames = maxResponseFrames;

        if (autoStartOnPlay)
            BeginBlock();
    }

    public void BeginBlock()
    {
        string expName = string.IsNullOrWhiteSpace(spec.experimentName) ? "(unnamed)" : spec.experimentName;
        Debug.Log($"[TrialBlockRunner] ========================================");
        Debug.Log($"[TrialBlockRunner]  EXPERIMENT: {expName}");
        Debug.Log($"[TrialBlockRunner]  Spec asset: {spec.name}");
        Debug.Log($"[TrialBlockRunner]  Unique stimuli: {spec.GetUniqueStimulusCount()}");
        if (spec.depthSeparation_m > 0f)
            Debug.Log($"[TrialBlockRunner]  DEPTH: separation={spec.depthSeparation_m:F3}m, balanced={spec.balanceDelayedFieldDepth}");
        Debug.Log($"[TrialBlockRunner] ========================================");
        _allPlannedTrials = spec.GetPlannedTrials(_rng);

        if (_allPlannedTrials == null || _allPlannedTrials.Count == 0)
        {
            Debug.LogError("[TrialBlockRunner] No trials generated by ExperimentSpec.", this);
            enabled = false;
            return;
        }

        _trialQueue = new List<ExperimentSpec.PlannedTrial>(_allPlannedTrials);
        _startedTrialCount = 0;

        // Precompute counts for this block run
        int targetN = spec.GetTargetNumberTrialsEstimate();
        int generatedN = _allPlannedTrials.Count;

        Debug.Log($"[TrialBlockRunner] StartLoop: csvLogger={(csvLogger != null ? "assigned" : "NULL")}, targetN={targetN}, generatedN={generatedN}");

        // ── Condition summary: log all factor levels from actual planned trials ──
        LogConditionSummary(_allPlannedTrials);

        if (csvLogger != null)
        {
            try
            {
                string path = BuildSessionPathSimple();
                Debug.Log($"[TrialBlockRunner] Calling BeginSession with path: {path}");
                csvLogger.BeginSession(path, spec.translationSpeed_degPerSec, spec.viewDistance_m, spec.experimentName);

                // Set counts AFTER BeginSession so meta writes reflect them immediately
                csvLogger.SetTargetNumberTrials(targetN);
                csvLogger.SetGeneratedTrials(generatedN);

                // Build 64-entry trajectory library INSIDE CsvLogger (for sidecar + analyzers)
                BuildAndRegisterTrajectoryLibrary(_allPlannedTrials);

                // ---- SIDE CAR: write ONCE per session ----
                try
                {
                    var cam = Camera.main;
                    csvLogger.WriteSidecarOnce(
                        spec,
                        builder,
                        fixation,
                        _allPlannedTrials,
                        monitorPreviewMode,
                        previewScale,
                        useSeparatePreviewScales,
                        previewDotScale,
                        previewFixationScale,
                        previewApertureScale,
                        cam,
                        _sessionSeed
                    );
                }
                catch (Exception e)
                {
                    Debug.LogError("[TrialBlockRunner] Sidecar write failed: " + e, this);
                }
            }
            catch (Exception e)
            {
                Debug.LogError("[TrialBlockRunner] CsvLogger.BeginSession failed - logging disabled for this session: " + e, this);
                csvLogger = null; // Disable logging but allow trials to continue
            }
        }
        else
        {
            Debug.LogWarning("[TrialBlockRunner] csvLogger is NOT assigned! No data will be logged. Please assign CsvLogger in Inspector.");
        }

        if (hud != null)
            hud.Bind(this);

        NextTrial();
    }

    /// <summary>
    /// Logs a human-readable summary of all experimental conditions in the Unity console.
    /// Tallies factor levels from the actual planned trials so the experimenter can confirm
    /// the design before running subjects.
    /// </summary>
    private void LogConditionSummary(List<ExperimentSpec.PlannedTrial> planned)
    {
        if (planned == null || planned.Count == 0) return;

        var conditions = new HashSet<string>();
        var rotCfgs = new HashSet<int>();
        var headings = new SortedSet<float>();
        var delColors = new HashSet<string>();
        var delDepths = new HashSet<string>();
        var swapTypes = new HashSet<string>();
        var swapCounts = new Dictionary<string, int>();
        var condCounts = new Dictionary<string, int>();

        foreach (var t in planned)
        {
            string cond = t.conditionID ?? "";
            string delCol = (t.delayedFieldColorCode == ExperimentSpec.COLOR_RED) ? "R" : "G";
            string delDp = (t.delayedFieldDepthCode == ExperimentSpec.DEPTH_NEAR) ? "Near" : "Far";
            string swap = ExperimentSpec.SwapFlagsToCode(t.swapFlags);

            conditions.Add(cond);
            rotCfgs.Add(t.rotationConfig);
            headings.Add(t.headingDeg);
            delColors.Add(delCol);
            delDepths.Add(delDp);
            swapTypes.Add(swap);

            if (!swapCounts.ContainsKey(swap)) swapCounts[swap] = 0;
            swapCounts[swap]++;

            string condSwap = $"{cond}+Sw{swap}";
            if (!condCounts.ContainsKey(condSwap)) condCounts[condSwap] = 0;
            condCounts[condSwap]++;
        }

        var sb = new StringBuilder();
        sb.AppendLine("[TrialBlockRunner] ── CONDITION SUMMARY ──");
        sb.AppendLine($"  Total trials: {planned.Count}");
        sb.AppendLine($"  Conditions: {string.Join(", ", conditions)}");
        sb.AppendLine($"  RotConfigs: {string.Join(", ", rotCfgs)}");
        sb.AppendLine($"  Headings: {string.Join(", ", headings)}");
        sb.AppendLine($"  DelayedFieldColors: {string.Join(", ", delColors)}");
        sb.AppendLine($"  DelayedFieldDepths: {string.Join(", ", delDepths)}");
        sb.AppendLine($"  SwapTypes: {string.Join(", ", swapTypes)}");
        sb.AppendLine("  Trials per swap type:");
        foreach (var kv in swapCounts)
            sb.AppendLine($"    Swap={kv.Key}: {kv.Value}");
        sb.AppendLine("  Trials per condition × swap:");
        foreach (var kv in condCounts)
            sb.AppendLine($"    {kv.Key}: {kv.Value}");
        sb.Append("[TrialBlockRunner] ── END CONDITION SUMMARY ──");

        Debug.Log(sb.ToString());
    }

    /// <summary>
    /// Registers ONE intended trajectory definition per unique stimulus identity
    /// into CsvLogger's internal trajectory library. CsvLogger then writes it into the sidecar.
    /// </summary>
    private void BuildAndRegisterTrajectoryLibrary(List<ExperimentSpec.PlannedTrial> planned)
    {
        if (csvLogger == null || spec == null || planned == null) return;

        // One representative trial per unique stimulus identity.
        var seen = new HashSet<string>();

        foreach (var t in planned)
        {
            string cond = t.conditionID ?? "";
            string delCol = (t.delayedFieldColorCode == ExperimentSpec.COLOR_RED) ? "R" : "G";
            string delDepth = (t.delayedFieldDepthCode == ExperimentSpec.DEPTH_NEAR) ? "N" : "F";
            int rotCfg = t.rotationConfig;
            float heading = t.headingDeg;
            string swapCode = ExperimentSpec.SwapFlagsToCode(t.swapFlags);

            string stimKey = CsvLogger.MakeStimKey(cond, rotCfg, heading, delCol, swapCode, delDepth);
            if (!seen.Add(stimKey))
                continue;

            // Build intended condition (source of truth for trajectories)
            CondLib.StimulusCondition c = spec.BuildEffectiveCondition(t);
            int N = c.timeline.totalFrames;
            int subCount = (c.subfields != null) ? c.subfields.Length : 0;

            var mk = new StringBuilder(N * 8);
            var col = new StringBuilder(N * 8);
            var dp = new StringBuilder(N * 8);

            for (int f = 0; f < N; f++)
            {
                int[] mkCodes = new int[subCount];
                string[] colCodes = new string[subCount];
                int[] dpCodes = new int[subCount];

                for (int s = 0; s < subCount; s++)
                {
                    var sf = c.subfields[s];

                    mkCodes[s] = (sf.motionKindByFrame != null && f < sf.motionKindByFrame.Length)
                        ? (int)sf.motionKindByFrame[f]
                        : 0;

                    Color cc = (sf.colorByFrame != null && f < sf.colorByFrame.Length)
                        ? sf.colorByFrame[f]
                        : Color.black;

                    colCodes[s] = EncodeColorLetter(cc);

                    dpCodes[s] = (sf.depthByFrame != null && f < sf.depthByFrame.Length)
                        ? (int)sf.depthByFrame[f]
                        : 0;
                }

                if (mk.Length > 0) mk.Append(";");
                mk.Append(string.Join("|", mkCodes));

                if (col.Length > 0) col.Append(";");
                col.Append(string.Join("|", colCodes));

                if (dp.Length > 0) dp.Append(";");
                dp.Append(string.Join("|", dpCodes));
            }

            csvLogger.RegisterTrajectoryDefinition(
                stimKey,
                cond,
                rotCfg,
                heading,
                delCol,
                mk.ToString(),
                col.ToString(),
                swapCode,
                delDepth,
                dp.ToString()
            );
        }
    }

    private string BuildSessionPathSimple()
    {
        string baseName = string.IsNullOrWhiteSpace(outputFileName) ? "Dots.tsv" : outputFileName.Trim();

        if (!appendDateTimeToFilename)
            return baseName;

        // YYMMDD_HHMM (no seconds, 2-digit year)
        string stamp = DateTime.Now.ToString("yyMMdd_HHmm");

        int dot = baseName.LastIndexOf('.');
        if (dot > 0)
        {
            string name = baseName.Substring(0, dot);
            string ext = baseName.Substring(dot);
            return name + "_" + stamp + ext;
        }
        return baseName + "_" + stamp;
    }

    private void NextTrial()
    {
        if (_trialQueue == null || _trialQueue.Count == 0)
        {
            if (csvLogger != null)
                csvLogger.EndSession();

            if (loopBlock)
            {
                _trialQueue = new List<ExperimentSpec.PlannedTrial>(_allPlannedTrials);
                _startedTrialCount = 0;

                if (csvLogger != null)
                {
                    string path = BuildSessionPathSimple();
                    csvLogger.BeginSession(path, spec.translationSpeed_degPerSec, spec.viewDistance_m, spec.experimentName);

                    int loopTargetN = spec.GetTargetNumberTrialsEstimate();
                    int loopGeneratedN = (_allPlannedTrials != null) ? _allPlannedTrials.Count : 0;

                    csvLogger.SetTargetNumberTrials(loopTargetN);
                    csvLogger.SetGeneratedTrials(loopGeneratedN);

                    BuildAndRegisterTrajectoryLibrary(_allPlannedTrials);

                    try
                    {
                        var cam = Camera.main;
                        csvLogger.WriteSidecarOnce(
                            spec,
                            builder,
                            fixation,
                            _allPlannedTrials,
                            monitorPreviewMode,
                            previewScale,
                            useSeparatePreviewScales,
                            previewDotScale,
                            previewFixationScale,
                            previewApertureScale,
                            cam,
                            _sessionSeed
                        );
                    }
                    catch (Exception e)
                    {
                        Debug.LogError("[TrialBlockRunner] Sidecar write failed (loop): " + e, this);
                    }
                }

                NextTrial();
                return;
            }

            _phase = TrialPhase.Done;
            enabled = false;
            return;
        }

        _currentTrial = _trialQueue[0];
        _trialQueue.RemoveAt(0);
        _currentCond = spec.BuildEffectiveCondition(_currentTrial);


        _frameInStimulus = 0;
        _accum = 0f;
        _responseFrameIndex = 0;
        _phase = TrialPhase.WaitingForStart;
        _startedTrialCount++;

        _mkPayloadBuilder = new StringBuilder();
        _colorPayloadBuilder = new StringBuilder();
        _depthPayloadBuilder = new StringBuilder();

        // ---------------- Spec truth ----------------
        float mPerDeg = spec.GetMetersPerDegree();
        float apDeg_truth = spec.apertureRadius_deg * 2f;
        float dotDiam_m_truth = spec.dotSize_deg * mPerDeg;

        // ---------------- Preview scalars ----------------
        float dotScale = 1f;
        float apScale = 1f;
        float fixScale = 1f;

        if (monitorPreviewMode)
        {
            float uni = Mathf.Max(0.1f, previewScale);

            if (!useSeparatePreviewScales)
            {
                dotScale = uni;
                apScale = uni;
                fixScale = uni;
            }
            else
            {
                dotScale = Mathf.Max(0.1f, previewDotScale);
                apScale = Mathf.Max(0.1f, previewApertureScale);
                fixScale = Mathf.Max(0.1f, previewFixationScale);
            }
        }

        // ---------------- Builder setup (REALIZED render geometry) ----------------
        builder.viewDistanceMeters = spec.viewDistance_m;
        builder.apertureDeg = apDeg_truth * apScale;
        builder.dotSizeMeters = dotDiam_m_truth * dotScale;
        builder.dotsPerField = spec.dotsPerField;
        builder.randomSeed = _currentTrial.seedA0;
        builder.exclusionRadiusMeters = spec.fixationExclusionRadius_deg * mPerDeg;
        builder.depthOffset_m = spec.depthSeparation_m;

        // ---------------- Fixation preview scaling ----------------
        if (fixation != null)
        {
            fixation.spec = spec;
            fixation.SetPreviewScaleAndApply(fixScale, "TBR.NextTrial");
            Debug.Log($"[TBR {GetInstanceID()}] Set fixation {fixation.GetInstanceID()} previewScale={fixScale:F2}", this);
        }
        else
        {
            Debug.LogWarning($"[TBR {GetInstanceID()}] fixation ref is NULL. Drag Fixation_Controller into the slot.", this);
        }

        builder.BuildFromCondition(_currentCond);
        builder.SetDotsActive(false);

        // Show both fields (sub0–sub3) at frame-0 positions during WaitingForStart so
        // the observer can fuse both depth planes before triggering the trial.
        // Sub2/sub3 (Field B) vanish at trial onset (frame 0) as usual.
        if (showFieldAPreview)
        {
            builder.SetSubfieldActive(0, true);
            builder.SetSubfieldActive(1, true);
            builder.SetSubfieldActive(2, true);
            builder.SetSubfieldActive(3, true);
            builder.ApplyAppearance(_currentCond, 0);
            builder.ApplyDepthOffsets(_currentCond, 0);
        }

        // ---------------- One-line realized geometry log ----------------
        if (logRealizedGeometryEachTrial)
        {
            float apDiam_m_truth = 2f * spec.viewDistance_m * Mathf.Tan(Mathf.Deg2Rad * spec.apertureRadius_deg);

            float apDeg_real = builder.apertureDeg;
            float dotDiam_m_real = builder.dotSizeMeters;

            Debug.Log(
                $"[GEOM] spec='{spec.name}' viewDist_m={spec.viewDistance_m} mPerDeg={mPerDeg:F6} " +
                $"TRUTH apDiam_deg={apDeg_truth:F3} apDiam_m={apDiam_m_truth:F4} dotDiam_m={dotDiam_m_truth:F6} " +
                $"REAL apDiam_deg={apDeg_real:F3} dotDiam_m={dotDiam_m_real:F6} " +
                $"previewMode={monitorPreviewMode} apScale={apScale:F2} dotScale={dotScale:F2} fixScale={fixScale:F2}",
                this
            );
        }

        if (targetResponseController != null)
        {
            targetResponseController.StopAndHide();
            targetResponseController.maxResponseFrames = maxResponseFrames;
        }

        if (csvLogger != null)
            csvLogger.BeginTrial(_currentTrial, spec, _currentCond);
    }

    void Update()
    {
        if (_currentCond == null || _phase == TrialPhase.Done)
        {
            _xrTriggerPressedThisFrame = false;
            return;
        }

        if (_phase == TrialPhase.WaitingForStart)
        {
            // Check for keyboard OR XR trigger to start trial
            bool startTrialInput = Input.GetKeyDown(startKey) || _xrTriggerPressedThisFrame;
            _xrTriggerPressedThisFrame = false; // Consume the input

            if (startTrialInput)
            {
                _phase = TrialPhase.Stimulus;
                _accum = 0f; // don't carry preview accumulation into first stimulus step
                builder.SetDotsActive(true);
                Debug.Log("[TrialBlockRunner] Trial started!");
            }
            // Field A is shown static at frame-0 positions (set in NextTrial).
            // No per-frame update needed during WaitingForStart.

            if (hud != null) hud.Tick();
            return;
        }

        _xrTriggerPressedThisFrame = false; // Clear any unconsumed XR input

        _accum += Time.deltaTime;
        while (_accum >= _simDt)
        {
            _accum -= _simDt;
            SimStep();
        }

        if (hud != null) hud.Tick();
    }

    private void SimStep()
    {
        if (_phase == TrialPhase.Stimulus) SimStepStimulus();
        else if (_phase == TrialPhase.TargetsResponse) SimStepTargetsResponse();
    }

    private void SimStepStimulus()
    {
        int N = _currentTrial.totalFrames;
        if (_frameInStimulus < 0 || _frameInStimulus >= N)
        {
            EnterTargetsPhase();
            return;
        }

        // Log the fixed columns ONCE per trial (frame 0)
        if (_frameInStimulus == 0 && csvLogger != null)
        {
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
                _currentTrial.seedB3,
                spec.translationSpeed_degPerSec,
                spec.viewDistance_m
            );
        }

        builder.ApplyAppearance(_currentCond, _frameInStimulus);

        float dt = _simDt;
        float metersPerDeg = spec.GetMetersPerDegree();

        for (int i = 0; i < builder.Subfields.Length; i++)
        {
            var mk = _currentCond.subfields[i].motionKindByFrame[_frameInStimulus];

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
                        float th = _currentTrial.headingDeg * Mathf.Deg2Rad;
                        float speed_mps = spec.translationSpeed_degPerSec * metersPerDeg;
                        Vector2 d = new Vector2(Mathf.Cos(th), Mathf.Sin(th)) * (speed_mps * dt);
                        builder.StepTranslation(i, d, _frameInStimulus);
                        break;
                    }

                case CondLib.MotionKind.NonCoherent:
                    builder.StepNonCoherentBalanced(i, spec.translationSpeed_degPerSec, dt, metersPerDeg, _frameInStimulus);
                    break;

                default:
                    break;
            }
        }

        // Apply stereo depth offsets AFTER motion stepping
        builder.ApplyDepthOffsets(_currentCond, _frameInStimulus);

        // Accumulate mkrows + colorrows + depthrows into single TSV fields
        if (_currentCond.subfields != null)
        {
            int subCount = _currentCond.subfields.Length;
            int[] mkCodes = new int[subCount];
            string[] colorCodes = new string[subCount];
            int[] depthCodes = new int[subCount];

            for (int i = 0; i < subCount; i++)
            {
                var sf = _currentCond.subfields[i];

                mkCodes[i] = (sf.motionKindByFrame != null && _frameInStimulus < sf.motionKindByFrame.Length)
                    ? (int)sf.motionKindByFrame[_frameInStimulus]
                    : 0;

                if (sf.colorByFrame != null && _frameInStimulus < sf.colorByFrame.Length)
                    colorCodes[i] = EncodeColorLetter(sf.colorByFrame[_frameInStimulus]);
                else
                    colorCodes[i] = "K";

                depthCodes[i] = (sf.depthByFrame != null && _frameInStimulus < sf.depthByFrame.Length)
                    ? (int)sf.depthByFrame[_frameInStimulus]
                    : 0;
            }

            if (_mkPayloadBuilder.Length > 0) _mkPayloadBuilder.Append(";");
            _mkPayloadBuilder.Append(string.Join("|", mkCodes));

            if (_colorPayloadBuilder.Length > 0) _colorPayloadBuilder.Append(";");
            _colorPayloadBuilder.Append(string.Join("|", colorCodes));

            if (_depthPayloadBuilder.Length > 0) _depthPayloadBuilder.Append(";");
            _depthPayloadBuilder.Append(string.Join("|", depthCodes));
        }

        _frameInStimulus++;

        if (_frameInStimulus >= _currentTrial.totalFrames)
            EnterTargetsPhase();
    }

    private void EnterTargetsPhase()
    {
        builder.SetDotsActive(false);
        _phase = TrialPhase.TargetsResponse;
        _responseFrameIndex = 0;

        if (targetResponseController != null)
        {
            targetResponseController.BeginResponseWindow(0);

            // Start real-time tracking for directional feedback
            if (directionalFeedback != null)
                directionalFeedback.BeginTracking();
        }
        else
            FinalizeTrialAndAdvance_NoResponse();
    }

    private void SimStepTargetsResponse()
    {
        if (targetResponseController == null)
        {
            FinalizeTrialAndAdvance_NoResponse();
            return;
        }

        bool finished = targetResponseController.TryStep(_responseFrameIndex, out TargetResponse resp);
        _responseFrameIndex++;

        if (!finished)
            return;

        bool requeue = (resp.status == ResponseStatus.Canceled || resp.status == ResponseStatus.TimedOut);
        if (resp.status == ResponseStatus.Confirmed) requeue = false;

        // End real-time tracking when response window closes
        if (directionalFeedback != null)
        {
            directionalFeedback.EndTracking();
        }

        FinalizeTrialAndAdvance_WithResponse(resp, requeue);
    }

    /// <summary>
    /// Method B audit: compare runtime-built payload hashes against registered trajectory.
    /// </summary>
    private void AuditTrajectory()
    {
        if (csvLogger == null || _currentTrial == null) return;
        if (_mkPayloadBuilder == null || _colorPayloadBuilder == null) return;

        string cond     = _currentTrial.conditionID ?? "";
        string delCol   = (_currentTrial.delayedFieldColorCode == ExperimentSpec.COLOR_RED) ? "R" : "G";
        string delDepth = (_currentTrial.delayedFieldDepthCode == ExperimentSpec.DEPTH_NEAR) ? "N" : "F";
        string swapCode = ExperimentSpec.SwapFlagsToCode(_currentTrial.swapFlags);
        string stimKey  = CsvLogger.MakeStimKey(cond, _currentTrial.rotationConfig,
                                                 _currentTrial.headingDeg, delCol, swapCode, delDepth);

        csvLogger.VerifyTrialTrajectory(stimKey,
                                         _mkPayloadBuilder.ToString(),
                                         _colorPayloadBuilder.ToString(),
                                         _depthPayloadBuilder != null ? _depthPayloadBuilder.ToString() : "");
    }

    private void FinalizeTrialAndAdvance_NoResponse()
    {
        if (csvLogger != null)
        {
            if (_mkPayloadBuilder.Length > 0)
                csvLogger.LogMkRows(_currentTrial.index, _mkPayloadBuilder.ToString());

            if (_colorPayloadBuilder.Length > 0)
                csvLogger.LogColorRows(_currentTrial.index, _colorPayloadBuilder.ToString());

            if (_depthPayloadBuilder != null && _depthPayloadBuilder.Length > 0)
                csvLogger.LogDepthRows(_currentTrial.index, _depthPayloadBuilder.ToString());

            AuditTrajectory();

            csvLogger.LogResponse(-1, -1, "", -1, "", "Keyboard");
            csvLogger.EndTrial();
        }

        csvLogger?.AddRequeuedTrial();
        RequeueTrial(_currentTrial);

        _phase = TrialPhase.Done;
        NextTrial();
    }

    /// <summary>
    /// Insert trial at a random position in the remaining queue (never position 0,
    /// to avoid an immediate repeat of the same stimulus).
    /// </summary>
    private void RequeueTrial(ExperimentSpec.PlannedTrial trial)
    {
        if (_trialQueue == null) _trialQueue = new List<ExperimentSpec.PlannedTrial>();
        int insertAt = (_trialQueue.Count > 0) ? _rng.Next(1, _trialQueue.Count + 1) : 0;
        _trialQueue.Insert(insertAt, trial);
    }

    private void FinalizeTrialAndAdvance_WithResponse(TargetResponse resp, bool requeue)
    {
        if (csvLogger != null)
        {
            if (_mkPayloadBuilder.Length > 0)
                csvLogger.LogMkRows(_currentTrial.index, _mkPayloadBuilder.ToString());

            if (_colorPayloadBuilder.Length > 0)
                csvLogger.LogColorRows(_currentTrial.index, _colorPayloadBuilder.ToString());

            if (_depthPayloadBuilder != null && _depthPayloadBuilder.Length > 0)
                csvLogger.LogDepthRows(_currentTrial.index, _depthPayloadBuilder.ToString());

            AuditTrajectory();

            int responseIndex = (resp.status == ResponseStatus.Confirmed) ? resp.choiceIndex : -1;
            int rtFrames = resp.rtFrames;
            string endKey = (resp.key == KeyCode.None) ? "" : resp.key.ToString();
            string device = string.IsNullOrEmpty(resp.deviceLabel) ? "Keyboard" : resp.deviceLabel;

            MapChoiceToDigitAndDir(responseIndex, out int responseDigit, out string responseDir);

            csvLogger.LogResponse(responseIndex, responseDigit, responseDir, rtFrames, endKey, device);
            csvLogger.EndTrial();
        }

        if (requeue)
        {
            csvLogger?.AddRequeuedTrial();
            RequeueTrial(_currentTrial);
        }

        _phase = TrialPhase.Done;
        NextTrial();
    }

    private static void MapChoiceToDigitAndDir(int responseIndex, out int digit, out string dir)
    {
        switch (responseIndex)
        {
            case 0: digit = 8; dir = "N";  break;
            case 1: digit = 9; dir = "NE"; break;
            case 2: digit = 6; dir = "E";  break;
            case 3: digit = 3; dir = "SE"; break;
            case 4: digit = 2; dir = "S";  break;
            case 5: digit = 1; dir = "SW"; break;
            case 6: digit = 4; dir = "W";  break;
            case 7: digit = 7; dir = "NW"; break;
            default: digit = -1; dir = ""; break;
        }
    }

    private static string EncodeColorLetter(Color c)
    {
        if (c.a < 0.5f || (c.r < 0.05f && c.g < 0.05f && c.b < 0.05f))
            return "K";

        if (c.r >= c.g && c.r >= c.b) return "R";
        if (c.g >= c.r && c.g >= c.b) return "G";
        if (c.b >= c.r && c.b >= c.g) return "B";
        return "Y";
    }

    // HUD read-only accessors
    public int TrialIndex => _startedTrialCount;
    public int TrialsCount => (_allPlannedTrials != null) ? _allPlannedTrials.Count : 0;
    public int FrameInTrial => _frameInStimulus;
    public float SimHz => (spec != null) ? spec.simHz : 0f;
    public ExperimentSpec.PlannedTrial CurrentTrial => _currentTrial;
}