// FILE: ExperimentSpec.cs
using System;
using System.Collections.Generic;
using UnityEngine;
using CondLib = StimulusConditionsLibrary;

// Abstract base for experiment-level parameters & block generation.
// Owns: simulation clock, viewing geometry, dot layout, kinematics.
// Does NOT hard-code specific conditions; those live in concrete subclasses
// (e.g., ExpSpecTestPhase) via BuildEffectiveCondition.

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

    [Header("Dot Layout")]
    [Tooltip("Dots per perceptual FIELD (so ~dotsPerField/2 per subfield).")]
    public int dotsPerField = 200;

    [Header("Color Palette")]
    public Color rgbaRed   = new Color(0.9f, 0.2f, 0.2f, 1f);
    public Color rgbaGreen = new Color(0.2f, 0.85f, 0.2f, 1f);
    public Color rgbaBlack = new Color(0f, 0f, 0f, 1f);

    [Serializable]
    public class PlannedTrial
    {
        public int    index;                 // 0..N-1
        public string conditionID;           // "CUED", "UNCUED", etc.
        public float  headingDeg;            // one of 8 directions

        // Key frames (simulation frame indices)
        public int onsetFrame;               // when delayed field appears
        public int translationStartFrame;    // start of translation window
        public int translationEndFrame;      // end (exclusive)
        public int totalFrames;              // full trial duration

        // Random seeds for subfields, to reconstruct dot layouts
        public int seedA0;
        public int seedA1;
        public int seedB2;
        public int seedB3;
    }

    // ---------- Helpers ----------

    public float SimDt => 1f / Mathf.Max(1, simHz);

    public int MsToFrames(float ms)
    {
        return Mathf.Max(1, Mathf.RoundToInt((ms / 1000f) * simHz));
    }

    // Meters per degree at this viewing distance
    public float GetMetersPerDegree()
    {
        return viewDistance_m * Mathf.Tan(Mathf.Deg2Rad * 1f);
    }

    // ---------- Abstract API ----------

    /// Return a fully specified, balanced trial list for a block.
    public abstract List<PlannedTrial> GetPlannedTrials(System.Random rng);

    /// For a given trial, build the per-frame 4-subfield condition.
    /// Concrete specs (e.g., ExpSpecTestPhase) encode cued vs uncued, etc.
    public abstract CondLib.StimulusCondition BuildEffectiveCondition(PlannedTrial trial);
}