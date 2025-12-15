// FILE: TrialBlockRunner.cs
//
// Purpose: Run a block of trials defined by ExperimentSpec.
//
// BIG-PICTURE FLOW PER BLOCK
// --------------------------
// 1) BeginBlock:
//      - Ask ExperimentSpec to generate a list of PlannedTrial objects.
//      - Push them into a queue (_trialQueue) that we draw from sequentially.
// 2) For each trial:
//      (a) Fixation-only, waiting for startKey.
//      (b) Stimulus: dots visible and moving for totalFrames simulation frames,
//          while we accumulate mkrows/colorrows payload.
//      (c) Targets/Response: dot fields hidden; targets on; TargetResponseController
//          waits for a direction + confirm OR cancel OR timeout.
//      (d) Logging + advance:
//          - ALWAYS write mkrows and colorrows for the stimulus we just showed.
//          - If response is CONFIRMED: log choice/RT/key/device and DO NOT requeue trial.
//          - If response is CANCELED or TIMED OUT: log choiceIndex = -1, then
//            re-enqueue the trial at the END of the queue so it comes back later,
//            not immediately.
// 3) When the queue is empty:
//      - End CSV session.
//      - Either stop, or (if loopBlock is true) regenerate a new queue and keep going.
//

using System.Collections.Generic;
using System.Text;
using UnityEngine;
using CondLib = StimulusConditionsLibrary;

[DisallowMultipleComponent]
public class TrialBlockRunner : MonoBehaviour
{
    // ---------------------------------------------------------------------
    // PUBLIC REFERENCES (wired in Inspector)
    // ---------------------------------------------------------------------
    [Header("References")]
    [Tooltip("Defines the trial list and how to build effective stimulus conditions.")]
    public ExperimentSpec spec;

    [Tooltip("Responsible for creating and updating dot subfields each frame.")]
    public StimulusBuilder builder;

    [Tooltip("Handles CSV output, column layout, and file I/O.")]
    public CsvLogger csvLogger;

    [Tooltip("Optional HUD to display trial index, frame, etc. during debugging.")]
    public StimDebugHUD hud;

    [Tooltip("Controls the response targets and keyboard input semantics.")]
    public TargetResponseController targetResponseController;

    // ---------------------------------------------------------------------
    // CONTROL FLAGS
    // ---------------------------------------------------------------------
    [Header("Control")]
    [Tooltip("If true, block starts automatically on Play.")]
    public bool autoStartOnPlay = true;

    [Tooltip("If true, when the trial queue is empty, regenerate a fresh block and continue.")]
    public bool loopBlock = false;

    [Header("Trial start / response")]
    [Tooltip("Key that starts each trial after fixation is visible.")]
    public KeyCode startKey = KeyCode.Space;

    [Tooltip("Maximum number of frames to allow a response after targets appear.\n" +
             "0 or negative means 'never time out' from the perspective of this script.\n" +
             "Note: This is forwarded into TargetResponseController.maxResponseFrames.")]
    public int maxResponseFrames = 0;

    // ---------------------------------------------------------------------
    // INTERNAL STATE: BLOCK & TRIAL QUEUE
    // ---------------------------------------------------------------------

    // All planned trials for this block (static definition from the spec).
    private List<ExperimentSpec.PlannedTrial> _allPlannedTrials;

    // Dynamic queue of trials still to be run (and re-run if canceled/timed-out).
    private Queue<ExperimentSpec.PlannedTrial> _trialQueue;

    // Index of how many trials have been *started* in this block (for HUD/debug).
    private int _startedTrialCount = 0;

    // Simulation timing
    private float _accum;   // how much real time has accumulated since last sim step
    private float _simDt;   // fixed simulation dt (seconds per frame) from spec

    // Current trial and condition
    private ExperimentSpec.PlannedTrial _currentTrial;
    private CondLib.StimulusCondition   _currentCond;

    // Trial-relative frame index for the STIMULUS phase only.
    // IMPORTANT: This is NOT used for RT in response window.
    private int _frameInStimulus;

    // Random source (passed into spec for trial shuffling, seeding, etc.).
    private System.Random _rng;

    // mkrows / colorrows payload accumulation for the current trial
    private StringBuilder _mkPayloadBuilder;
    private StringBuilder _colorPayloadBuilder;

    // ---------------------------------------------------------------------
    // TRIAL PHASE STATE MACHINE
    // ---------------------------------------------------------------------
    // Big-picture phases for a single trial:
    //   WaitingForStart  → Stimulus → TargetsResponse → Done (then NextTrial)
    private enum TrialPhase
    {
        WaitingForStart = 0,
        Stimulus,
        TargetsResponse,
        Done
    }

    private TrialPhase _phase = TrialPhase.Done;

    // Response-window bookkeeping:
    //   We count response frames separately from stimulus frames.
    //   This keeps RT in frames decoupled from how long the stimulus ran.
    private int _responseFrameIndex = 0;
    private TargetResponse _lastResponse;

    // ---------------------------------------------------------------------
    // UNITY LIFECYCLE
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
                  $"hud={(hud ? hud.name : "NULL")}, " +
                  $"targetResponseController={(targetResponseController ? targetResponseController.name : "NULL")}");

        if (targetResponseController == null)
        {
            Debug.LogWarning("[TrialBlockRunner] No TargetResponseController assigned. " +
                             "Trials will run, but no valid responses will be collected.");
        }
        else
        {
            // Keep the response controller aware of the configured max.
            targetResponseController.maxResponseFrames = maxResponseFrames;
        }

        if (autoStartOnPlay)
        {
            BeginBlock();
        }
    }

    // ---------------------------------------------------------------------
    // BLOCK MANAGEMENT
    // ---------------------------------------------------------------------
    /// <summary>
    /// Called once to start a new block of trials.
    /// Fetches planned trials from the ExperimentSpec and initializes the queue.
    /// </summary>
    public void BeginBlock()
    {
        Debug.Log("[TrialBlockRunner] BeginBlock()");

        _allPlannedTrials = spec.GetPlannedTrials(_rng);
        if (_allPlannedTrials == null || _allPlannedTrials.Count == 0)
        {
            Debug.LogError("[TrialBlockRunner] No trials generated by ExperimentSpec.");
            enabled = false;
            return;
        }

        // Build a fresh queue from the planned trials
        _trialQueue = new Queue<ExperimentSpec.PlannedTrial>(_allPlannedTrials);
        _startedTrialCount = 0;

        if (csvLogger != null)
        {
            Debug.Log("[TrialBlockRunner] Calling CsvLogger.BeginSession()");
            csvLogger.BeginSession(spec, _allPlannedTrials);
        }

        if (hud != null)
        {
            Debug.Log("[TrialBlockRunner] Binding HUD.");
            hud.Bind(this);
        }

        NextTrial();
    }

    /// <summary>
    /// Move to the next trial in the queue, or end/loop the block if queue is empty.
    /// </summary>
    private void NextTrial()
    {
        // If queue is empty, we're at the end of the block (for now).
        if (_trialQueue == null || _trialQueue.Count == 0)
        {
            if (csvLogger != null)
            {
                Debug.Log("[TrialBlockRunner] Ending session in CsvLogger.");
                csvLogger.EndSession();
            }

            if (loopBlock)
            {
                Debug.Log("[TrialBlockRunner] Block complete; regenerating queue and looping.");

                _trialQueue = new Queue<ExperimentSpec.PlannedTrial>(_allPlannedTrials);
                _startedTrialCount = 0;

                if (csvLogger != null)
                {
                    // NOTE: if you want distinct files per loop, you could adjust here.
                    csvLogger.BeginSession(spec, _allPlannedTrials);
                }

                NextTrial();
            }
            else
            {
                Debug.Log("[TrialBlockRunner] Block complete, disabling TrialBlockRunner.");
                _phase = TrialPhase.Done;
                enabled = false;
            }

            return;
        }

        // Dequeue the next trial and set up its effective condition.
        _currentTrial = _trialQueue.Dequeue();
        _currentCond  = spec.BuildEffectiveCondition(_currentTrial);
        _frameInStimulus = 0;
        _accum           = 0f;
        _responseFrameIndex = 0;
        _lastResponse = default;
        _phase = TrialPhase.WaitingForStart;
        _startedTrialCount++;

        // Reset mk/color payload builders.
        _mkPayloadBuilder    = new StringBuilder();
        _colorPayloadBuilder = new StringBuilder();

        // Configure builder from spec and this trial
        builder.viewDistanceMeters = spec.viewDistance_m;
        builder.apertureDeg        = spec.apertureRadius_deg * 2f; // radius → diameter
        builder.dotSizeMeters      = spec.dotSize_deg * spec.GetMetersPerDegree();
        builder.dotsPerField       = spec.dotsPerField;
        builder.randomSeed         = _currentTrial.seedA0;

        // Build subfields/dots for this condition.
        builder.BuildFromCondition(_currentCond);

        // Hide dots until the trial actually starts (fixation-only period).
        builder.SetDotsActive(false);

        // Make sure targets are hidden at trial start.
        if (targetResponseController != null)
        {
            targetResponseController.StopAndHide();
            targetResponseController.maxResponseFrames = maxResponseFrames;
        }

        // Inform the csvLogger that a new trial is about to run.
        if (csvLogger != null)
        {
            Debug.Log("[TrialBlockRunner] Calling CsvLogger.BeginTrial()");
            csvLogger.BeginTrial(_currentTrial, spec, _currentCond);
        }

        Debug.Log($"[TrialBlockRunner] Starting trial {_startedTrialCount} " +
                  $"(planned index={_currentTrial.index}, conditionID={_currentTrial.conditionID}, " +
                  $"heading={_currentTrial.headingDeg}°, frames={_currentTrial.totalFrames})");

        // We are now in "fixation-only, waiting for start key" state.
    }

    // ---------------------------------------------------------------------
    // MAIN UPDATE LOOP
    // ---------------------------------------------------------------------
    void Update()
    {
        if (_currentCond == null || _phase == TrialPhase.Done)
            return;

        // Phase 1: FIXATION-ONLY, WAITING FOR START KEY
        if (_phase == TrialPhase.WaitingForStart)
        {
            if (Input.GetKeyDown(startKey))
            {
                // Transition: start key pressed → Stimulus phase.
                _phase = TrialPhase.Stimulus;

                // Make the dot fields visible now that the trial starts.
                builder.SetDotsActive(true);

                Debug.Log($"[TrialBlockRunner] Trial {_currentTrial.index} started by key {startKey}.");
            }

            if (hud != null)
                hud.Tick();

            // No motion / no frame stepping until trial is started.
            return;
        }

        // Phases 2 & 3: Stimulus and Targets/Response both run on the fixed-step sim.
        _accum += Time.deltaTime;
        while (_accum >= _simDt)
        {
            _accum -= _simDt;
            SimStep();
        }

        if (hud != null)
            hud.Tick();
    }

    // ---------------------------------------------------------------------
    // FIXED-STEP SIMULATION
    // ---------------------------------------------------------------------
    private void SimStep()
    {
        if (_currentCond == null) return;

        switch (_phase)
        {
            case TrialPhase.Stimulus:
                SimStepStimulus();
                break;

            case TrialPhase.TargetsResponse:
                SimStepTargetsResponse();
                break;

            default:
                // WaitingForStart / Done should never call SimStep.
                break;
        }
    }

    // ---------------------------------------------------------------------
    // PHASE 2: STIMULUS
    // ---------------------------------------------------------------------
    private void SimStepStimulus()
    {
        int N = _currentTrial.totalFrames;

        // Safety clamp: if we somehow overshoot, transition to targets/response.
        if (_frameInStimulus < 0 || _frameInStimulus >= N)
        {
            EnterTargetsPhase();
            return;
        }

        // On the FIRST simulation frame of this trial, write the summary trial info
        // into the logger (but do not flush the row yet).
        if (_frameInStimulus == 0 && csvLogger != null)
        {
            Debug.Log("[TrialBlockRunner] Calling CsvLogger.LogTrialRow() at frame 0.");
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
                spec.translationSpeed_degPerSec,  // pass speed
                spec.viewDistance_m               // pass view distance
            );
        }

        // Apply color & visibility for this frame
        builder.ApplyAppearance(_currentCond, _frameInStimulus);

        float dt           = _simDt;
        float metersPerDeg = spec.GetMetersPerDegree();

        // Step each subfield according to its MotionKind
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
                    float th        = _currentTrial.headingDeg * Mathf.Deg2Rad;
                    float speed_mps = spec.translationSpeed_degPerSec * metersPerDeg;
                    Vector2 d       = new Vector2(Mathf.Cos(th), Mathf.Sin(th)) * (speed_mps * dt);
                    builder.StepTranslation(i, d, _frameInStimulus);
                    break;
                }

                case CondLib.MotionKind.NonCoherent:
                {
                    builder.StepNonCoherentBalanced(
                        i,
                        spec.translationSpeed_degPerSec,
                        dt,
                        metersPerDeg,
                        _frameInStimulus
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
            int[]    mkCodes    = new int[subCount];
            string[] colorCodes = new string[subCount];

            for (int i = 0; i < subCount; i++)
            {
                var sf = _currentCond.subfields[i];

                // Motion kind as integer code
                if (sf.motionKindByFrame != null && _frameInStimulus < sf.motionKindByFrame.Length)
                    mkCodes[i] = (int)sf.motionKindByFrame[_frameInStimulus];
                else
                    mkCodes[i] = 0;

                // Color as single-letter code
                if (sf.colorByFrame != null && _frameInStimulus < sf.colorByFrame.Length)
                {
                    Color c = sf.colorByFrame[_frameInStimulus];
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

        // Advance stimulus frame
        _frameInStimulus++;

        // If we just finished the last valid frame, transition to targets/response.
        if (_frameInStimulus >= _currentTrial.totalFrames)
        {
            EnterTargetsPhase();
        }
    }

    // ---------------------------------------------------------------------
    // PHASE 3: TARGETS / RESPONSE
    // ---------------------------------------------------------------------
    /// <summary>
    /// Called once when we leave the stimulus phase and enter the targets/response window.
    /// </summary>
    private void EnterTargetsPhase()
    {
        // Hide the dots so only the targets remain visible during response.
        builder.SetDotsActive(false);

        _phase = TrialPhase.TargetsResponse;
        _responseFrameIndex = 0;
        _lastResponse = default;

        if (targetResponseController != null)
        {
            // Start the response window. We use "response frame 0" here;
            // TargetResponseController will track RT as currentFrame - onsetFrame.
            targetResponseController.BeginResponseWindow(0);
        }
        else
        {
            Debug.LogWarning("[TrialBlockRunner] EnterTargetsPhase called but no TargetResponseController assigned. " +
                             "Ending trial immediately with no valid response.");
            // No response controller → immediately finalize as "no response".
            FinalizeTrialAndAdvance_NoResponse();
        }
    }

    /// <summary>
    /// One fixed-step "frame" of the response window.
    /// We ask TargetResponseController whether the window is finished
    /// (confirmed, canceled, or timed out).
    /// </summary>
    private void SimStepTargetsResponse()
    {
        if (targetResponseController == null)
        {
            // Already handled by EnterTargetsPhase fallback, but guard anyway.
            FinalizeTrialAndAdvance_NoResponse();
            return;
        }

        // Each sim step, we advance the response-frame counter and ask the controller.
        bool finished = targetResponseController.TryStep(_responseFrameIndex, out TargetResponse resp);
        _responseFrameIndex++;

        if (!finished)
            return; // Still waiting for direction + confirm / cancel / timeout.

        // We now have a final TargetResponse.
        _lastResponse = resp;

        switch (resp.status)
        {
            case ResponseStatus.Confirmed:
                FinalizeTrialAndAdvance_WithResponse(resp, requeue: false);
                break;

            case ResponseStatus.Canceled:
            case ResponseStatus.TimedOut:
                // "Do not count this trial" → log with choiceIndex = -1 but requeue.
                FinalizeTrialAndAdvance_WithResponse(resp, requeue: true);
                break;

            default:
                // Should not happen, but treat as "no response".
                FinalizeTrialAndAdvance_NoResponse();
                break;
        }
    }

    // ---------------------------------------------------------------------
    // PHASE 4: LOGGING + ADVANCE
    // ---------------------------------------------------------------------
    /// <summary>
    /// Fallback: trial ended but we have no response system.
    /// We log mkrows/colorrows and a response of (-1, -1, "", ""),
    /// then advance to the next trial without requeue.
    /// </summary>
    private void FinalizeTrialAndAdvance_NoResponse()
    {
        // Attach mkrows / colorrows payload for this trial.
        if (csvLogger != null)
        {
            if (_mkPayloadBuilder != null && _mkPayloadBuilder.Length > 0)
                csvLogger.LogMkRows(_currentTrial.index, _mkPayloadBuilder.ToString());

            if (_colorPayloadBuilder != null && _colorPayloadBuilder.Length > 0)
                csvLogger.LogColorRows(_currentTrial.index, _colorPayloadBuilder.ToString());

            // Log a "no response" row.
            csvLogger.LogResponse(
                -1,         // choiceIndex
                -1,         // rtFrames
                "",         // responseKey
                ""          // deviceName
            );

            csvLogger.EndTrial();
        }

        _phase = TrialPhase.Done;
        NextTrial();
    }

    /// <summary>
    /// Normal path: we have a TargetResponse from the controller.
    /// - Always logs mkrows and colorrows for the stimulus we just showed.
    /// - Logs response fields depending on status:
    ///     * Confirmed: actual choiceIndex, RT, key, device.
    ///     * Canceled/TimedOut: choiceIndex = -1, but we still log key/RT for diagnostics.
    /// - If requeue == true (canceled/timedout), we enqueue this same trial
    ///   at the end of the queue so the subject will see it again later.
    /// </summary>
    private void FinalizeTrialAndAdvance_WithResponse(TargetResponse resp, bool requeue)
    {
        // 1) Attach mkrows / colorrows payload for this trial.
        if (csvLogger != null)
        {
            if (_mkPayloadBuilder != null && _mkPayloadBuilder.Length > 0)
                csvLogger.LogMkRows(_currentTrial.index, _mkPayloadBuilder.ToString());

            if (_colorPayloadBuilder != null && _colorPayloadBuilder.Length > 0)
                csvLogger.LogColorRows(_currentTrial.index, _colorPayloadBuilder.ToString());
        }

        // 2) Decide how to encode the response in the CSV.
        int    choiceIndex = (resp.status == ResponseStatus.Confirmed) ? resp.choiceIndex : -1;
        int    rtFrames    = resp.rtFrames;
        string keyName     = (resp.key == KeyCode.None) ? "" : resp.key.ToString();
        string deviceName  = string.IsNullOrEmpty(resp.deviceLabel) ? "Keyboard" : resp.deviceLabel;

        if (csvLogger != null)
        {
            csvLogger.LogResponse(
                choiceIndex,
                rtFrames,
                keyName,
                deviceName
            );

            // 3) End the trial in the logger (write the CSV row).
            csvLogger.EndTrial();
        }

        // 4) If this trial was canceled or timed out, requeue it at the END
        //    so the subject will see it again later, not immediately.
        if (requeue)
        {
            Debug.Log($"[TrialBlockRunner] Trial {_currentTrial.index} " +
                      $"status={resp.status}, requeueing for later.");
            if (_trialQueue == null)
                _trialQueue = new Queue<ExperimentSpec.PlannedTrial>();

            _trialQueue.Enqueue(_currentTrial);
        }

        // 5) Advance to the next trial.
        _phase = TrialPhase.Done;
        NextTrial();
    }

    // ---------------------------------------------------------------------
    // HELPER: map Color → single-letter code for mkrows/colorrows
    // ---------------------------------------------------------------------
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

    // ---------------------------------------------------------------------
    // HUD ACCESSORS (read-only)
    // ---------------------------------------------------------------------
    public int   TrialIndex   => _startedTrialCount;
    public int   TrialsCount  => _allPlannedTrials?.Count ?? 0;
    public int   FrameInTrial => _frameInStimulus;
    public float SimHz        => spec.simHz;
    public ExperimentSpec.PlannedTrial CurrentTrial => _currentTrial;
}
