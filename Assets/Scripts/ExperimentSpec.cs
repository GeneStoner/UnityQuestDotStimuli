// FILE: ExperimentSpec.cs
//
// SOURCE OF TRUTH for experiment parameters.
// ------------------------------------
// All stimulus geometry, timing, and kinematic parameters are defined here.
// TrialBlockRunner reads from this asset and copies values to StimulusBuilder,
// Fixation_Controller, and other components at trial start.
//
// To change experiment parameters: Edit the ExperimentSpec asset (e.g., ExpSpecTestPhase.asset)
// Inspector fields on TrialBlockRunner are for preview scaling and runtime control only.
//
using System;
using System.Collections.Generic;
using UnityEngine;
using CondLib = StimulusConditionsLibrary;

public abstract class ExperimentSpec : ScriptableObject
{
    [Header("Experiment Identity")]
    [Tooltip("Short name for this experiment (e.g., 'Baseline', 'MotionSwap'). Logged in TSV, meta, and sidecar.")]
    public string experimentName = "";

    [Header("Simulation Clock (decoupled from display refresh)")]
    [Tooltip("Simulation steps per second (e.g., 75 to approximate S&B timing).")]
    public int simHz = 75;

    [Header("Viewing Geometry (degrees)")]
    [Tooltip("Viewing distance in meters.")]
    public float viewDistance_m = 2.0f;

    [Tooltip("Aperture RADIUS in degrees of visual angle (2° → 4° diameter).")]
    public float apertureRadius_deg = 2.0f;

    [Tooltip("Dot size in degrees (DIAMETER).")]
    public float dotSize_deg = 0.03f;

    [Header("Kinematics (degrees)")]
    [Tooltip("Rotation speed in deg/sec for CW/CCW rotation.")]
    public float rotationSpeed_degPerSec = 81f;

    [Tooltip("Translation speed in deg/sec for coherent / non-coherent motion.")]
    public float translationSpeed_degPerSec = 2.26f;

    [Tooltip("Duration of the translation window (ms).")]
    public float translationDuration_ms = 80f;

    [Tooltip("Onset delay (ms) for the second (cued) field.")]
    public float delayedOnset_ms = 750f;

    [Tooltip("Pre-translation gap (ms) after second field onset, before translation.")]
    public float preTranslation_ms = 300f;

    [Header("Block / Balancing")]
    [Tooltip("How many repeats per unique stimulus (condition × heading × etc.) to generate. " +
             "NOTE: individual ExperimentSpec subclasses may use their own repetition knobs; " +
             "this is used only for target-number estimates unless the subclass uses it explicitly.")]
    [Min(1)]
    public int repeatsPerStimulus = 2;

    [Tooltip("If true: delayed-onset field color is exactly balanced Red vs Green across generated trials.")]
    public bool balanceDelayedFieldColor = true;

    [Tooltip("If true: delayed-onset field depth is exactly balanced Near vs Far across generated trials.")]
    public bool balanceDelayedFieldDepth = false;

    [Tooltip("If true: BOTH dot fields are placed in the same depth plane (Near or Far), rather than opposite planes. Use with balanceDelayedFieldDepth to run equal numbers of BothNear and BothFar trials within one session.")]
    public bool bothFieldsSamePlane = false;

    [Header("Stereo Depth")]
    [Tooltip("Depth offset in meters from fixation plane. Each field is offset ±this amount along the viewing axis. 0 = no depth separation (all dots at fixation plane). Near = toward viewer, Far = away from viewer.")]
    public float depthSeparation_m = 0f;

    [Tooltip("Bias added to both depth planes along the viewing axis (positive = away from viewer). " +
             "Use to place both fields on the same side of fixation. " +
             "E.g. depthSeparation_m=0.025, depthBias_m=0.075 → planes at +0.05m and +0.10m (both behind fixation).")]
    public float depthBias_m = 0f;

    [Header("Dot Layout")]
    [Tooltip("Dots per perceptual FIELD (so ~dotsPerField/2 per subfield).")]
    public int dotsPerField = 200;

    // ================= FIXATION (degrees of visual angle) =================

    public enum FixationStyle
    {
        Dot,
        BullsEye,
        BullsEyePlusCrosshair,
        Crosshair
    }

    [Header("Fixation Target (degrees)")]
    public FixationStyle fixationStyle = FixationStyle.BullsEyePlusCrosshair;

    [Tooltip("Fixation color (applies to all parts unless overridden).")]
    public Color fixationColor = Color.white;

    [Tooltip("Fixation dot RADIUS in degrees.")]
    public float fixationDotRadius_deg = 0.05f;   // ~0.1° diameter default

    [Tooltip("Inner radius of bullseye ring (degrees).")]
    public float fixationRingInnerRadius_deg = 0.15f;

    [Tooltip("Ring thickness (degrees).")]
    public float fixationRingThickness_deg = 0.03f;

    [Tooltip("Crosshair arm HALF-length (degrees).")]
    public float fixationCrosshairArmLength_deg = 0.25f;

    [Tooltip("Crosshair stroke thickness (degrees).")]
    public float fixationCrosshairThickness_deg = 0.03f;

    [Tooltip("Exclusion zone RADIUS around fixation (degrees). Dots will not spawn within this radius.")]
    public float fixationExclusionRadius_deg = 1.1f;

    //temmp color fudging to get closer to red/green isoluminance
    // [Header("Color Palette")]

    public Color rgbaRed = new Color(0.9f, 0.2f, 0.2f, 1f);
    public Color rgbaGreen = new Color(0.2f, 0.45f, 0.2f, 1f);
    //public Color rgbaRed = new Color(0.9f, 0.2f, 0.2f, 1f);
   // public Color rgbaGreen = new Color(0.2f, 0.85f, 0.2f, 1f);
    public Color rgbaBlack = new Color(0f, 0f, 0f, 1f);

    // ---- Color coding for balancing ----
    public const int COLOR_RED = 0;
    public const int COLOR_GREEN = 1;

    // ---- Depth coding for balancing ----
    public const int DEPTH_NEAR = 0;
    public const int DEPTH_FAR = 1;

    protected Color ColorFromCode(int code) => (code == COLOR_RED) ? rgbaRed : rgbaGreen;
    protected int OppositeColorCode(int code) => (code == COLOR_RED) ? COLOR_GREEN : COLOR_RED;

    // ---- Swap conditions (Stoner & Blanc 2010) ----
    [Flags]
    public enum SwapFlags
    {
        None    = 0,
        Motion  = 1 << 0,   // rotation directions swap at tStart
        Color   = 1 << 1,   // field colors swap at tStart
        Dots50  = 1 << 2,   // 50% of dots swap field membership (sub1↔sub3)
        Depth   = 1 << 3,   // depth planes swap at tStart (100%)
        Depth50  = 1 << 4,  // S0↔S2 swap depth planes at tStart (50%); color follows plane (legacy)
        Depth50A = 1 << 5,  // S0↔S2 swap; both translators same plane (Far); cued dot moves plane
        Depth50B = 1 << 6,  // S1↔S3 swap; both translators same plane (Near); cued dot stays in plane
    }

    public static string SwapFlagsToCode(int flags)
    {
        if (flags == 0) return "N";
        var parts = new List<string>();
        if ((flags & (int)SwapFlags.Motion)   != 0) parts.Add("M");
        if ((flags & (int)SwapFlags.Color)    != 0) parts.Add("C");
        if ((flags & (int)SwapFlags.Dots50)   != 0) parts.Add("D");
        if ((flags & (int)SwapFlags.Depth)    != 0) parts.Add("Z");
        if ((flags & (int)SwapFlags.Depth50)  != 0) parts.Add("Zd");
        if ((flags & (int)SwapFlags.Depth50A) != 0) parts.Add("ZdA");
        if ((flags & (int)SwapFlags.Depth50B) != 0) parts.Add("ZdB");
        return string.Join("", parts);
    }

    [Serializable]
    public class PlannedTrial
    {
        public int index;                 // 0..N-1
        public string conditionID;           // "CUED", "UNCUED", etc.
        public float headingDeg;            // one of 8 directions

        // NEW: rotation configuration axis (0/1)
        // 0 = A: (0,1)=CW and (2,3)=CCW
        // 1 = B: (0,1)=CCW and (2,3)=CW
        public int rotationConfig = 0;

        // Timing window semantics: [translationStartFrame, translationEndFrame)
        public int onsetFrame;
        public int translationStartFrame;    // inclusive
        public int translationEndFrame;      // exclusive
        public int totalFrames;

        // Random seeds for subfields
        public int seedA0;
        public int seedA1;
        public int seedB2;
        public int seedB3;

        // which color is the DELAYED-ONSET field (field B) AFTER onset.
        // 0 = red, 1 = green.
        public int delayedFieldColorCode;

        // Swap condition at translation onset (cast of SwapFlags).
        public int swapFlags = 0;

        // which depth plane is the DELAYED-ONSET field (field B).
        // 0 = Near, 1 = Far.
        public int delayedFieldDepthCode;
    }

    // ---------- Helpers ----------
    public float SimDt => 1f / Mathf.Max(1, simHz);

    public int MsToFrames(float ms)
    {
        // round to nearest; minimum 1 frame for any positive duration
        return Mathf.Max(1, Mathf.RoundToInt((ms / 1000f) * Mathf.Max(1, simHz)));
    }

    /// <summary>
    /// Exact meters per 1 degree at viewDistance_m (small-angle approx not used).
    /// </summary>
    public float GetMetersPerDegree()
    {
        float d = Mathf.Max(1e-6f, viewDistance_m);
        return d * Mathf.Tan(Mathf.Deg2Rad * 1f);
    }

    // ---------- Abstract API ----------
    public abstract List<PlannedTrial> GetPlannedTrials(System.Random rng);
    public abstract CondLib.StimulusCondition BuildEffectiveCondition(PlannedTrial trial);

    /// <summary>
    /// Return the number of *distinct* stimuli (unique identities) implied by this spec.
    /// Subclasses should override with the correct combinatorics for their trial generation.
    /// </summary>
    public virtual int GetUniqueStimulusCount() { return 0; }

    /// <summary>
    /// Estimate of intended number of trials for a block/session.
    /// This is used for meta bookkeeping only. Actual trials are GetPlannedTrials().Count.
    /// </summary>
    public int GetTargetNumberTrialsEstimate()
    {
        int unique = GetUniqueStimulusCount();

        // If subclass doesn't implement it, fall back to 0 to avoid misleading meta.
        if (unique <= 0) return 0;

        // Default estimate uses repeatsPerStimulus. Subclasses may ignore repeatsPerStimulus
        // in GetPlannedTrials() and use their own repetition knob; that's fine—this is a target.
        return Mathf.Max(1, repeatsPerStimulus) * unique;
    }
}