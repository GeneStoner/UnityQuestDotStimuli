// FILE: ExperimentSpec.cs
using System;
using System.Collections.Generic;
using UnityEngine;
using CondLib = StimulusConditionsLibrary;

public abstract class ExperimentSpec : ScriptableObject
{
    [Header("Simulation Clock (decoupled from display refresh)")]
    [Tooltip("Simulation steps per second (e.g., 75 to approximate S&B timing).")]
    public int simHz = 75;

    [Header("Viewing Geometry (degrees)")]
    [Tooltip("Viewing distance in meters.")]
    public float viewDistance_m = 2.0f;

    [Tooltip("Aperture RADIUS in degrees of visual angle (2° → 4° diameter).")]
    public float apertureRadius_deg = 2.0f;

    [Tooltip("Dot size in degrees.")]
    public float dotSize_deg = 0.03f;

    [Header("Kinematics (degrees)")]
    [Tooltip("Rotation speed in deg/sec for CW/CCW rotation.")]
    public float rotationSpeed_degPerSec = 81f;

    [Tooltip("Translation speed in deg/sec for coherent / non-coherent motion.")]
    public float translationSpeed_degPerSec = 2.26f;

    [Tooltip("Duration of the translation window (ms).")]
    public float translationDuration_ms = 40f;

    [Tooltip("Onset delay (ms) for the second (cued) field.")]
    public float delayedOnset_ms = 750f;

    [Tooltip("Pre-translation gap (ms) after second field onset, before translation.")]
    public float preTranslation_ms = 300f;

    [Header("Block / Balancing")]
    [Tooltip("How many repeats per unique stimulus (condition × heading × etc.) to generate. Keep low for pilots.")]
    [Min(1)]
    public int repeatsPerStimulus = 2;

    [Tooltip("If true: delayed-onset field color is exactly balanced Red vs Green across generated trials.")]
    public bool balanceDelayedFieldColor = true;

    [Header("Dot Layout")]
    [Tooltip("Dots per perceptual FIELD (so ~dotsPerField/2 per subfield).")]
    public int dotsPerField = 200;

    [Header("Color Palette")]
    public Color rgbaRed   = new Color(0.9f, 0.2f, 0.2f, 1f);
    public Color rgbaGreen = new Color(0.2f, 0.85f, 0.2f, 1f);
    public Color rgbaBlack = new Color(0f, 0f, 0f, 1f);

    // =========================================================================
    // Fixation + Central Exclusion
    // =========================================================================

    // IMPORTANT: include CrosshairOnly for backward compatibility with earlier scripts
    // that referenced ExperimentSpec.FixationStyle.CrosshairOnly.
    public enum FixationStyle
    {
        Dot,
        BullsEye,
        Crosshair,
        CrosshairOnly,          // alias/back-compat; treat same as Crosshair
        BullsEyePlusCrosshair
    }

    [Header("Fixation + Central Exclusion (degrees)")]
    [Tooltip("Exclude dots within this radius around fixation (deg). 0 = none.")]
    [Min(0f)]
    public float centralExclusionRadius_deg = 0.0f;

    [Header("Fixation (degrees)")]
    public FixationStyle fixationStyle = FixationStyle.BullsEyePlusCrosshair;

    [Tooltip("Center dot radius (deg).")]
    [Min(0f)]
    public float fixationDotRadius_deg = 0.05f;

    [Tooltip("Bull's-eye ring INNER radius (deg).")]
    [Min(0f)]
    public float fixationRingInnerRadius_deg = 0.15f;

    [Tooltip("Bull's-eye ring thickness (deg). Outer radius = inner + thickness.")]
    [Min(0f)]
    public float fixationRingThickness_deg = 0.03f;

    [Tooltip("Crosshair arm length from center to tip (deg).")]
    [Min(0f)]
    public float fixationCrosshairArmLength_deg = 0.25f;

    [Tooltip("Crosshair stroke thickness (deg).")]
    [Min(0f)]
    public float fixationCrosshairThickness_deg = 0.03f;

    [Tooltip("Fixation color (ERP-style recommendation: white).")]
    public Color fixationColor = Color.white;

    // Optional desktop display geometry (used later for deg->px mapping)
    [Header("Desktop Display Geometry (optional; for deg → px)")]
    [Tooltip("Physical screen width in meters (measure once).")]
    [Min(0f)]
    public float screenWidth_m = 0.0f;

    [Tooltip("Horizontal pixel resolution (0 = use Screen.width at runtime).")]
    public int screenResX = 0;

    /// <summary>Ring OUTER radius (deg) = inner radius + thickness.</summary>
    public float FixationRingOuterRadius_deg => Mathf.Max(0f, fixationRingInnerRadius_deg + fixationRingThickness_deg);

    // =========================================================================
    // Color coding for balancing
    // =========================================================================
    public const int COLOR_RED = 0;
    public const int COLOR_GREEN = 1;

    protected Color ColorFromCode(int code)
    {
        return (code == COLOR_RED) ? rgbaRed : rgbaGreen;
    }

    protected int OppositeColorCode(int code)
    {
        return (code == COLOR_RED) ? COLOR_GREEN : COLOR_RED;
    }

    [Serializable]
    public class PlannedTrial
    {
        public int index;                 // 0..N-1
        public string conditionID;        // "CUED", "UNCUED", etc.
        public float headingDeg;          // one of 8 directions

        // Timing window semantics: [translationStartFrame, translationEndFrame)
        public int onsetFrame;
        public int translationStartFrame; // inclusive
        public int translationEndFrame;   // exclusive
        public int totalFrames;

        // Random seeds for subfields
        public int seedA0;
        public int seedA1;
        public int seedB2;
        public int seedB3;

        // which color is the DELAYED-ONSET field (field B) AFTER onset.
        // 0 = red, 1 = green.
        public int delayedFieldColorCode;
    }

    // =========================================================================
    // Helpers
    // =========================================================================
    public float SimDt => 1f / Mathf.Max(1, simHz);

    public int MsToFrames(float ms)
    {
        return Mathf.Max(1, Mathf.RoundToInt((ms / 1000f) * simHz));
    }

    public float GetMetersPerDegree()
    {
        return viewDistance_m * Mathf.Tan(Mathf.Deg2Rad * 1f);
    }

    /// <summary>
    /// Optional: compute pixels/degree for desktop when you set screenWidth_m.
    /// If screenWidth_m or screenResX are unset, returns 0 (caller should fallback).
    /// </summary>
    public float PixelsPerDegree()
    {
        if (screenWidth_m <= 1e-6f) return 0f;
        int resX = (screenResX > 0) ? screenResX : Screen.width;
        if (resX <= 0) return 0f;

        float mPerDeg = GetMetersPerDegree();
        float pxPerMeter = resX / screenWidth_m;
        return mPerDeg * pxPerMeter;
    }

    // =========================================================================
    // Abstract API
    // =========================================================================
    public abstract List<PlannedTrial> GetPlannedTrials(System.Random rng);
    public abstract CondLib.StimulusCondition BuildEffectiveCondition(PlannedTrial trial);

    public virtual int GetUniqueStimulusCount() { return 0; }

    public int GetTargetNumberTrialsEstimate()
    {
        int unique = GetUniqueStimulusCount();
        if (unique <= 0) return 0;
        return Mathf.Max(1, repeatsPerStimulus) * unique;
    }
}