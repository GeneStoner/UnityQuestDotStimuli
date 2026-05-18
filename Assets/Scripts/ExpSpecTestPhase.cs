// FILE: ExpSpecTestPhase.cs
using System;
using System.Collections.Generic;
using UnityEngine;
using CondLib = StimulusConditionsLibrary;

[CreateAssetMenu(
    fileName = "ExpSpecTestPhase",
    menuName = "Stimuli/Experiment Specs/Test Phase",
    order = 10)]
public class ExpSpecTestPhase : ExperimentSpec
{
    [Header("Rotation configuration")]
    [Tooltip("If true, include BOTH rotation configurations (A and B). If false, use only config A.")]
    public bool includeBothRotationConfigs = true;

    [Header("Swap conditions (Stoner & Blanc 2010)")]
    [Tooltip("Include motion-swap trials (rotation directions swap at translation onset).")]
    public bool includeMotionSwaps = false;

    [Tooltip("Include color-swap trials (field colors swap at translation onset).")]
    public bool includeColorSwaps = false;

    [Tooltip("Include combined color+motion swap trials (CM) without generating C or M alone. " +
             "Use when you only want the full conjunctive swap. Ignored if both includeMotionSwaps " +
             "and includeColorSwaps are true (CM is already in the power set).")]
    public bool includeCMSwaps = false;

    [Tooltip("Include 50%% dot-swap trials (sub1↔sub3 noise-half exchange at translation onset — preserves coherent translator identity).")]
    public bool includeDots50Swaps = false;

    [Tooltip("Include 50%% coherent-half swap trials (sub0↔sub2 exchange field membership at tStart — inverts which field is the coherent translator).")]
    public bool includeDots50ASwaps = false;

    [Tooltip("Include full dot-swap trials (sub0↔sub2 AND sub1↔sub3 simultaneously — all dots exchange field membership, analogous to Stoner & Blanc color+motion swap).")]
    public bool includeDots50BothSwaps = false;

    [Tooltip("Include depth-swap trials (depth planes swap at translation onset).")]
    public bool includeDepthSwaps = false;

    [Tooltip("Include 50% depth-swap trials (S0↔S2 exchange depth planes at tStart; color follows plane membership).")]
    public bool includeDepthPartialSwaps = false;

    [Tooltip("Include ZdA trials (S0↔S2 depth swap; both translators in Far; cued dot moves plane). Mutually exclusive with ZdB per trial.")]
    public bool includeDepth50ASwaps = false;

    [Tooltip("Include ZdB trials (S1↔S3 depth swap; both translators in Near; cued dot stays in plane). Mutually exclusive with ZdA per trial.")]
    public bool includeDepth50BSwaps = false;

    [Tooltip("When false, the no-swap baseline condition (swapFlags=0) is excluded from trial generation. " +
             "Default true for backward compatibility.")]
    public bool includeNoSwapBaseline = true;

    [Tooltip("When true, dot colors follow depth-plane assignment: Near=rgbaRed, Far=rgbaGreen " +
             "(determined per trial by delayedFieldColorCode + DFD). Colors change at tStart when " +
             "subfields swap depth planes under ZdA/ZdB. Requires balanceDelayedFieldColor=true.")]
    public bool linkDepthColor = false;

    [Tooltip("When true (default), the translating field (Sub2+Sub3, Field B) has the delayed onset — " +
             "the temporal cue correctly identifies the translator (Dots✓). " +
             "When false, the rotating field (Sub0+Sub1, Field A) has the delayed onset — " +
             "the temporal cue points to the rotator, not the translator (Dots✗, converse conditions).")]
    public bool delayTranslator = true;

    [Header("Dot continuity removal")]
    [Tooltip("When true, coherently translating dots (MotionKind.Linear subfields) are randomly " +
             "repositioned at the first frame of translation. Removes dot-identity continuity " +
             "between the rotation and translation phases. One frame of coherent translation " +
             "motion is lost (dots appear at new random positions on that frame, then move " +
             "coherently from frame+1 onward). Non-translating and noise subfields are unaffected.")]
    public bool replotTranslatingAtTStart = false;

    [Tooltip("When true, the rotating (non-translating) dot field's subfields are randomly " +
             "repositioned at the first frame of translation. Removes dot-identity continuity " +
             "for the competitor field across the transition. " +
             "MotionKind.RotationCW and RotationCCW subfields are replotted; Linear and NonCoherent are unaffected.")]
    public bool replotNonTranslatingAtTStart = false;

    [Header("Variable translation duration (MoCS)")]
    [Tooltip("If non-empty, each trial randomly samples one of these durations (ms) instead of " +
             "the fixed translationDuration_ms. Values are quantized to the frame grid at runtime. " +
             "Leave empty to use the fixed duration as before. Ignored when useQuestAdaptive=true.")]
    public float[] translationDurations_ms = new float[0];

    [Header("QUEST adaptive duration")]
    [Tooltip("If true, duration is chosen adaptively by a per-(condition,cue) QUEST staircase " +
             "instead of sampling from translationDurations_ms or the fixed duration.")]
    public bool useQuestAdaptive = false;

    [Tooltip("QUEST prior: initial threshold guess in ms (log-centre of prior).")]
    public float questTGuessMs = 80f;

    [Tooltip("QUEST prior: SD in log10 units (0.4 ≈ factor-of-2.5 uncertainty; 0.6 ≈ factor-of-4).")]
    public float questTGuessSd = 0.4f;

    [Tooltip("Weibull slope beta (1.5–3.0 typical for duration tasks).")]
    public float questBeta = 2.0f;

    [Tooltip("Lapse rate delta (probability of random response regardless of stimulus; ~0.02).")]
    public float questDelta = 0.02f;

    [Tooltip("Minimum testable duration in ms (should be ≤ shortest perceptible translation).")]
    public float questXMinMs = 15f;

    [Tooltip("Maximum testable duration in ms (should be ≥ longest needed to reach ceiling).")]
    public float questXMaxMs = 400f;

    /// <summary>
    /// Sample a translation duration in frames for one trial (MoCS / fixed mode only).
    /// For QUEST mode, TrialBlockRunner queries the staircase directly.
    /// </summary>
    public int SampleTranslationDurationFrames(System.Random rng)
    {
        if (translationDurations_ms != null && translationDurations_ms.Length > 0)
        {
            float ms = translationDurations_ms[rng.Next(translationDurations_ms.Length)];
            return MsToFrames(ms);
        }
        return MsToFrames(translationDuration_ms);
    }

    /// <summary>Maximum translation frames across the testable range (used to set totalFrames).</summary>
    public int MaxTranslationFrames()
    {
        if (useQuestAdaptive)
            return MsToFrames(questXMaxMs);

        int maxF = MsToFrames(translationDuration_ms);
        if (translationDurations_ms != null)
            foreach (float d in translationDurations_ms)
                maxF = Mathf.Max(maxF, MsToFrames(d));
        return maxF;
    }

    // Distinct stimuli = (CUED/UNCUED) × (8 headings) × (rotationConfigFactor) × (delayedColorFactor) × swapFactor
    public override int GetUniqueStimulusCount()
    {
        int condFactor = 2;
        int headingFactor = 8;
        int rotFactor = includeBothRotationConfigs ? 2 : 1;
        int colorFactor = balanceDelayedFieldColor ? 2 : 1;

        int depthFactor = balanceDelayedFieldDepth ? 2 : 1;

        int swapFactor = 1;
        if (includeMotionSwaps)        swapFactor *= 2;
        if (includeColorSwaps)         swapFactor *= 2;
        // Dots50 (noise-half) and Dots50A (coherent-half) are mutually exclusive per trial,
        // unless includeDots50BothSwaps is also set (which adds the combined DDa condition).
        int dotConditions = (includeDots50Swaps ? 1 : 0) + (includeDots50ASwaps ? 1 : 0)
                          + (includeDots50BothSwaps ? 1 : 0);
        if (dotConditions > 0) swapFactor *= (1 + dotConditions);
        if (includeDepthSwaps)         swapFactor *= 2;
        if (includeDepthPartialSwaps)  swapFactor *= 2;
        // ZdA and ZdB are mutually exclusive per trial; enabling both adds 2 conditions (not 3)
        if (includeDepth50ASwaps && includeDepth50BSwaps) swapFactor *= 3;
        else if (includeDepth50ASwaps || includeDepth50BSwaps) swapFactor *= 2;
        // CM swap adds one condition if CM is not already in the power set
        if (includeCMSwaps && !(includeMotionSwaps && includeColorSwaps)) swapFactor += 1;
        // Remove the no-swap baseline if excluded
        if (!includeNoSwapBaseline && swapFactor > 1) swapFactor -= 1;

        return condFactor * headingFactor * rotFactor * colorFactor * depthFactor * swapFactor;
    }

    public override List<PlannedTrial> GetPlannedTrials(System.Random rng)
    {
        var trials = new List<PlannedTrial>(capacity: Mathf.Max(1, GetTargetNumberTrialsEstimate()));

        string[] condIDs = { "CUED", "UNCUED" };
        float[] headings = { 0f, 45f, 90f, 135f, 180f, 225f, 270f, 315f };

        int[] rotCfgs = includeBothRotationConfigs ? new[] { 0, 1 } : new[] { 0 };

        // Build all combinations (power set) of active swap flags
        var activeFlags = new List<int>();
        if (includeMotionSwaps)        activeFlags.Add((int)SwapFlags.Motion);
        if (includeColorSwaps)         activeFlags.Add((int)SwapFlags.Color);
        if (includeDots50Swaps || includeDots50BothSwaps)  activeFlags.Add((int)SwapFlags.Dots50);
        if (includeDots50ASwaps || includeDots50BothSwaps) activeFlags.Add((int)SwapFlags.Dots50A);
        if (includeDepthSwaps)         activeFlags.Add((int)SwapFlags.Depth);
        if (includeDepthPartialSwaps)  activeFlags.Add((int)SwapFlags.Depth50);
        if (includeDepth50ASwaps)      activeFlags.Add((int)SwapFlags.Depth50A);
        if (includeDepth50BSwaps)      activeFlags.Add((int)SwapFlags.Depth50B);

        var swapValues = new List<int> { 0 }; // None always included
        foreach (int flag in activeFlags)
        {
            int count = swapValues.Count;
            for (int i = 0; i < count; i++)
                swapValues.Add(swapValues[i] | flag);
        }

        // ZdA and ZdB are mutually exclusive: remove any trial that has both set
        int bothAB = (int)SwapFlags.Depth50A | (int)SwapFlags.Depth50B;
        swapValues.RemoveAll(v => (v & bothAB) == bothAB);
        // D and Da combined: keep only if includeDots50BothSwaps; remove individual conditions
        // that were added solely as scaffolding for the combined case.
        int bothDots = (int)SwapFlags.Dots50 | (int)SwapFlags.Dots50A;
        if (!includeDots50BothSwaps)
            swapValues.RemoveAll(v => (v & bothDots) == bothDots);
        if (!includeDots50Swaps)
            swapValues.RemoveAll(v => (v & bothDots) == (int)SwapFlags.Dots50
                                   && (v & (int)SwapFlags.Dots50A) == 0);
        if (!includeDots50ASwaps)
            swapValues.RemoveAll(v => (v & bothDots) == (int)SwapFlags.Dots50A
                                   && (v & (int)SwapFlags.Dots50) == 0);
        // Add CM directly if not already present (e.g. when individual C/M are not enabled)
        if (includeCMSwaps) {
            int cmValue = (int)SwapFlags.Motion | (int)SwapFlags.Color;
            if (!swapValues.Contains(cmValue))
                swapValues.Add(cmValue);
        }
        // Optionally exclude the no-swap baseline
        if (!includeNoSwapBaseline)
            swapValues.Remove(0);

        // This is now the ONLY repetition knob.
        int reps = Mathf.Max(1, repeatsPerStimulus);

        int[] depthValues = balanceDelayedFieldDepth
            ? new[] { DEPTH_NEAR, DEPTH_FAR }
            : new[] { DEPTH_NEAR };

        int idx = 0;

        foreach (var condID in condIDs)
        {
            foreach (var h in headings)
            {
                foreach (int rotCfg in rotCfgs)
                {
                    foreach (int swap in swapValues)
                    {
                        foreach (int depth in depthValues)
                        {
                            if (balanceDelayedFieldColor)
                            {
                                for (int r = 0; r < reps; r++)
                                {
                                    trials.Add(MakeTrial(rng, ref idx, condID, h, rotCfg, COLOR_RED, swap, depth));
                                    trials.Add(MakeTrial(rng, ref idx, condID, h, rotCfg, COLOR_GREEN, swap, depth));
                                }
                            }
                            else
                            {
                                for (int r = 0; r < reps; r++)
                                {
                                    trials.Add(MakeTrial(rng, ref idx, condID, h, rotCfg, COLOR_RED, swap, depth));
                                }
                            }
                        }
                    }
                }
            }
        }

        // Shuffle (deterministic given rng)
        for (int i = trials.Count - 1; i > 0; i--)
        {
            int j = rng.Next(i + 1);
            (trials[i], trials[j]) = (trials[j], trials[i]);
        }

        // Assign lateral shift directions (balanced ±1, randomised order)
        if (lateralShiftDeg > 0f)
        {
            int half = trials.Count / 2;
            var dirs = new int[trials.Count];
            for (int i = 0; i < half; i++)      dirs[i] = +1;
            for (int i = half; i < trials.Count; i++) dirs[i] = -1;
            // Fisher-Yates shuffle
            for (int i = dirs.Length - 1; i > 0; i--)
            {
                int j = rng.Next(i + 1);
                int tmp = dirs[i]; dirs[i] = dirs[j]; dirs[j] = tmp;
            }
            for (int i = 0; i < trials.Count; i++)
                trials[i].lateralShiftDir = dirs[i];
        }

        // Reindex after shuffle so Trial column is contiguous
        for (int i = 0; i < trials.Count; i++)
            trials[i].index = i;

        return trials;
    }

    private PlannedTrial MakeTrial(System.Random rng,
                                   ref int idx,
                                   string condID,
                                   float headingDeg,
                                   int rotationConfig,
                                   int delayedColorCode,
                                   int swapFlags = 0,
                                   int delayedDepthCode = 0)
    {
        var t = new PlannedTrial
        {
            index = idx++,
            conditionID = condID,
            headingDeg = headingDeg,
            rotationConfig = rotationConfig,
            delayedFieldColorCode = delayedColorCode,
            swapFlags = swapFlags,
            delayedFieldDepthCode = delayedDepthCode
        };

        // Timing in frames
        // Use 0 directly when delayedOnset_ms==0 — MsToFrames has a Max(1,...) floor
        // that would otherwise produce onsetFrame=1, hiding Field B at the preview frame.
        t.onsetFrame = (delayedOnset_ms <= 0f) ? 0 : MsToFrames(delayedOnset_ms);

        int preTransFrames  = MsToFrames(preTranslation_ms);
        int transFrames     = MsToFrames(translationDuration_ms);
        int postTransFrames = MsToFrames(400f);

        t.translationStartFrame = t.onsetFrame + preTransFrames;
        t.translationEndFrame   = t.translationStartFrame + transFrames; // exclusive
        t.totalFrames           = t.translationEndFrame + postTransFrames;

        // Seeds
        t.seedA0 = rng.Next();
        t.seedA1 = rng.Next();
        t.seedB2 = rng.Next();
        t.seedB3 = rng.Next();

        return t;
    }

    public override CondLib.StimulusCondition BuildEffectiveCondition(PlannedTrial t)
    {
        int N = t.totalFrames;

        string rotTag = (t.rotationConfig == 0) ? "RotA" : "RotB";
        string swapTag = SwapFlagsToCode(t.swapFlags);
        string depthTag = (t.delayedFieldDepthCode == DEPTH_NEAR) ? "N" : "F";
        var cond = new CondLib.StimulusCondition
        {
            name = $"Trial_{t.index}_{t.conditionID}_{rotTag}_Del{(t.delayedFieldColorCode == COLOR_RED ? "R" : "G")}_Dp{depthTag}_Sw{swapTag}"
        };

        cond.timeline.totalFrames = N;
        cond.subfields = new CondLib.SubfieldTracks[4];

        for (int s = 0; s < 4; s++)
        {
            cond.subfields[s] = new CondLib.SubfieldTracks
            {
                motionKindByFrame = new CondLib.MotionKind[N],
                colorByFrame      = new Color[N],
                eyeByFrame        = new CondLib.Eye[N],
                depthByFrame      = new CondLib.DepthPlane[N],
                visibleByFrame    = new bool[N]
            };
        }

        bool isCued = t.conditionID == "CUED";

        int onset  = t.onsetFrame;
        int tStart = t.translationStartFrame;
        int tEnd   = t.translationEndFrame; // [tStart, tEnd)

        Color delayedColor    = ColorFromCode(t.delayedFieldColorCode);
        // When not balancing colors, both fields use the same color (bypasses any stale rgbaGreen cache)
        Color nonDelayedColor = balanceDelayedFieldColor
            ? ColorFromCode(OppositeColorCode(t.delayedFieldColorCode))
            : delayedColor;

        bool motionSwap   = (t.swapFlags & (int)SwapFlags.Motion)   != 0;
        bool colorSwap    = (t.swapFlags & (int)SwapFlags.Color)    != 0;
        bool dots50Swap   = (t.swapFlags & (int)SwapFlags.Dots50)   != 0;
        bool dots50ASwap  = (t.swapFlags & (int)SwapFlags.Dots50A)  != 0;
        bool depthSwap    = (t.swapFlags & (int)SwapFlags.Depth)    != 0;
        bool depth50Swap  = (t.swapFlags & (int)SwapFlags.Depth50)  != 0;
        bool depth50ASwap = (t.swapFlags & (int)SwapFlags.Depth50A) != 0;
        bool depth50BSwap = (t.swapFlags & (int)SwapFlags.Depth50B) != 0;

        // Depth planes: by default delayed field (B) and non-delayed (A) get opposite planes.
        // If bothFieldsSamePlane, both fields share the same plane (DelayedFieldDepth codes which one).
        bool useDepthPlanes = (depthSeparation_m > 0f);
        CondLib.DepthPlane fieldBDepth = (t.delayedFieldDepthCode == DEPTH_NEAR)
            ? CondLib.DepthPlane.Near : CondLib.DepthPlane.Far;
        CondLib.DepthPlane fieldADepth = bothFieldsSamePlane
            ? fieldBDepth
            : ((fieldBDepth == CondLib.DepthPlane.Near) ? CondLib.DepthPlane.Far : CondLib.DepthPlane.Near);

        // Rotation assignment depends on rotationConfig
        CondLib.MotionKind aRot = (t.rotationConfig == 0) ? CondLib.MotionKind.RotationCW  : CondLib.MotionKind.RotationCCW;
        CondLib.MotionKind bRot = (t.rotationConfig == 0) ? CondLib.MotionKind.RotationCCW : CondLib.MotionKind.RotationCW;

        for (int f = 0; f < N; f++)
        {
            bool afterOnset = f >= onset;
            bool afterSwap  = f >= tStart;

            // Rotation: swap directions at tStart if motionSwap
            CondLib.MotionKind curARot = (motionSwap && afterSwap) ? bRot : aRot;
            CondLib.MotionKind curBRot = (motionSwap && afterSwap) ? aRot : bRot;

            // Colors: swap at tStart if colorSwap
            Color fieldAColor = (colorSwap && afterSwap) ? delayedColor    : nonDelayedColor;
            Color fieldBColor = (colorSwap && afterSwap) ? nonDelayedColor : delayedColor;

            // Field membership per subfield.
            // Default: [A, A, B, B].
            // Dots50  (noise-half swap)    at tStart: sub1↔sub3 → [A, B, B, A]
            // Dots50A (coherent-half swap) at tStart: sub0↔sub2 → [B, A, A, B]
            bool sub0isA = !(dots50ASwap && afterSwap);   // Sub0 in Field A unless Dots50A swapped
            bool sub1isA = !(dots50Swap  && afterSwap);   // Sub1 in Field A unless Dots50  swapped
            bool sub2isB = !(dots50ASwap && afterSwap);   // Sub2 in Field B unless Dots50A swapped
            bool sub3isA =  (dots50Swap  && afterSwap);   // Sub3 in Field A only when Dots50 swapped

            // Which field carries the delayed onset?
            // delayTranslator=true  (default): Field B (Sub2+Sub3) hidden before onset — Dots✓
            // delayTranslator=false (converse): Field A (Sub0+Sub1) hidden before onset — Dots✗
            bool aVisible = delayTranslator ? true       : afterOnset;
            bool bVisible = delayTranslator ? afterOnset : true;
            Color aHiddenColor = delayTranslator ? fieldAColor : (afterOnset ? fieldAColor : rgbaBlack);
            Color bHiddenColor = delayTranslator ? (afterOnset ? fieldBColor : rgbaBlack) : fieldBColor;

            // Sub0: Field A by default, Field B if Dots50A swapped
            if (sub0isA)
            {
                cond.subfields[0].motionKindByFrame[f] = curARot;
                cond.subfields[0].colorByFrame[f]   = aHiddenColor;
                cond.subfields[0].visibleByFrame[f] = aVisible;
            }
            else
            {
                cond.subfields[0].motionKindByFrame[f] = curBRot;
                cond.subfields[0].colorByFrame[f]   = bHiddenColor;
                cond.subfields[0].visibleByFrame[f] = bVisible;
            }

            // Sub1: Field A by default, Field B if dots50 swapped
            cond.subfields[1].motionKindByFrame[f] = sub1isA ? curARot : curBRot;
            if (sub1isA)
            {
                cond.subfields[1].colorByFrame[f]   = aHiddenColor;
                cond.subfields[1].visibleByFrame[f] = aVisible;
            }
            else
            {
                cond.subfields[1].colorByFrame[f]   = bHiddenColor;
                cond.subfields[1].visibleByFrame[f] = bVisible;
            }

            // Sub2: Field B by default, Field A if Dots50A swapped
            if (sub2isB)
            {
                cond.subfields[2].motionKindByFrame[f] = curBRot;
                cond.subfields[2].colorByFrame[f]   = bHiddenColor;
                cond.subfields[2].visibleByFrame[f] = bVisible;
            }
            else
            {
                cond.subfields[2].motionKindByFrame[f] = curARot;
                cond.subfields[2].colorByFrame[f]   = aHiddenColor;
                cond.subfields[2].visibleByFrame[f] = aVisible;
            }

            // Sub3: Field B by default, Field A if dots50 swapped
            if (sub3isA)
            {
                cond.subfields[3].motionKindByFrame[f] = curARot;
                cond.subfields[3].colorByFrame[f]   = aHiddenColor;
                cond.subfields[3].visibleByFrame[f] = aVisible;
            }
            else
            {
                cond.subfields[3].motionKindByFrame[f] = curBRot;
                cond.subfields[3].colorByFrame[f]   = bHiddenColor;
                cond.subfields[3].visibleByFrame[f] = bVisible;
            }

            // Eye always binocular
            for (int s = 0; s < 4; s++)
                cond.subfields[s].eyeByFrame[f] = CondLib.Eye.Both;

            // Depth planes: follow field membership, swap at tStart if depthSwap
            if (useDepthPlanes)
            {
                CondLib.DepthPlane curADepth = (depthSwap && afterSwap) ? fieldBDepth : fieldADepth;
                CondLib.DepthPlane curBDepth = (depthSwap && afterSwap) ? fieldADepth : fieldBDepth;

                cond.subfields[0].depthByFrame[f] = sub0isA ? curADepth : curBDepth; // sub0: follows membership
                cond.subfields[1].depthByFrame[f] = sub1isA ? curADepth : curBDepth; // sub1: follows membership
                cond.subfields[2].depthByFrame[f] = sub2isB ? curBDepth : curADepth; // sub2: follows membership
                cond.subfields[3].depthByFrame[f] = sub3isA ? curADepth : curBDepth; // sub3: follows membership
            }
            else
            {
                for (int s = 0; s < 4; s++)
                    cond.subfields[s].depthByFrame[f] = CondLib.DepthPlane.Fixation;
            }

            // ── Zd (50% depth swap): S0↔S2 exchange depth planes at tStart ──────────
            // Near-group (S0,S3 at fieldBDepth): rotation=curARot, color=nonDelayedColor
            // Far-group  (S1,S2 at fieldADepth): rotation=curBRot, color=delayedColor
            if (depth50Swap && afterSwap)
            {
                // Rotation follows depth-plane group
                cond.subfields[0].motionKindByFrame[f] = curARot;
                cond.subfields[1].motionKindByFrame[f] = curBRot;  // reversed
                cond.subfields[2].motionKindByFrame[f] = curBRot;
                cond.subfields[3].motionKindByFrame[f] = curARot;  // reversed

                // Color follows depth-plane group (sub2/sub3 maintain visibility gating)
                cond.subfields[1].colorByFrame[f] = delayedColor;
                cond.subfields[3].colorByFrame[f] = afterOnset ? nonDelayedColor : rgbaBlack;

                // Depth: S0→fieldBDepth, S2→fieldADepth; S1 stays fieldADepth, S3 stays fieldBDepth
                if (useDepthPlanes)
                {
                    cond.subfields[0].depthByFrame[f] = fieldBDepth;
                    cond.subfields[1].depthByFrame[f] = fieldADepth;
                    cond.subfields[2].depthByFrame[f] = fieldADepth;
                    cond.subfields[3].depthByFrame[f] = fieldBDepth;
                }
            }

            // ── ZdA: S0↔S2 depth swap; both translators land in fieldADepth (Far) ──
            // Cued dot (S2) moves from fieldBDepth→fieldADepth.
            // Near-group (S0,S3): rotation=curARot. Far-group (S1,S2): rotation=curBRot.
            // Translation: CUED→S2(Coh,Far)+S1(NonCoh,Far); UNCUED→S0(Coh,Near)+S3(NonCoh,Near).
            if (depth50ASwap && afterSwap)
            {
                cond.subfields[0].motionKindByFrame[f] = curARot;
                cond.subfields[1].motionKindByFrame[f] = curBRot;  // reversed
                cond.subfields[2].motionKindByFrame[f] = curBRot;
                cond.subfields[3].motionKindByFrame[f] = curARot;  // reversed

                if (useDepthPlanes)
                {
                    cond.subfields[0].depthByFrame[f] = fieldBDepth; // S0: Far→Near
                    cond.subfields[1].depthByFrame[f] = fieldADepth; // S1: stays Far
                    cond.subfields[2].depthByFrame[f] = fieldADepth; // S2: Near→Far
                    cond.subfields[3].depthByFrame[f] = fieldBDepth; // S3: stays Near
                }

                // When depth-color is linked, colors follow depth-plane assignment after swap.
                // S0→fieldBDepth (delayedColor), S1 stays fieldADepth (nonDelayedColor),
                // S2→fieldADepth (nonDelayedColor), S3 stays fieldBDepth (delayedColor).
                if (linkDepthColor)
                {
                    cond.subfields[0].colorByFrame[f] = delayedColor;
                    cond.subfields[1].colorByFrame[f] = nonDelayedColor;
                    cond.subfields[2].colorByFrame[f] = afterOnset ? nonDelayedColor : rgbaBlack;
                    cond.subfields[3].colorByFrame[f] = afterOnset ? delayedColor    : rgbaBlack;
                }
            }

            // ── ZdB: S1↔S3 depth swap; both translators stay in fieldBDepth (Near) ──
            // Cued dot (S2) stays in fieldBDepth (Near).
            // Near-group (S1,S2): rotation=curBRot. Far-group (S0,S3): rotation=curARot.
            // Translation: CUED→S2(Coh,Near)+S1(NonCoh,Near); UNCUED→S0(Coh,Far)+S3(NonCoh,Far).
            if (depth50BSwap && afterSwap)
            {
                cond.subfields[0].motionKindByFrame[f] = curARot;   // stays Far
                cond.subfields[1].motionKindByFrame[f] = curBRot;   // reversed (Far→Near)
                cond.subfields[2].motionKindByFrame[f] = curBRot;   // stays Near
                cond.subfields[3].motionKindByFrame[f] = curARot;   // reversed (Near→Far)

                if (useDepthPlanes)
                {
                    cond.subfields[0].depthByFrame[f] = fieldADepth; // S0: stays Far
                    cond.subfields[1].depthByFrame[f] = fieldBDepth; // S1: Far→Near
                    cond.subfields[2].depthByFrame[f] = fieldBDepth; // S2: stays Near
                    cond.subfields[3].depthByFrame[f] = fieldADepth; // S3: Near→Far
                }

                // When depth-color is linked, colors follow depth-plane assignment after swap.
                // S0 stays fieldADepth (nonDelayedColor), S1→fieldBDepth (delayedColor),
                // S2 stays fieldBDepth (delayedColor), S3→fieldADepth (nonDelayedColor).
                if (linkDepthColor)
                {
                    cond.subfields[0].colorByFrame[f] = nonDelayedColor;
                    cond.subfields[1].colorByFrame[f] = delayedColor;
                    cond.subfields[2].colorByFrame[f] = afterOnset ? delayedColor    : rgbaBlack;
                    cond.subfields[3].colorByFrame[f] = afterOnset ? nonDelayedColor : rgbaBlack;
                }
            }
        }

        // Translation window: coherent/non-coherent within translating field.
        // With dots50 swap, field membership changes: A={sub0,sub3}, B={sub2,sub1}.
        // Original member → Linear, swapped-in member → NonCoherent.
        int fStart = Mathf.Max(0, tStart);
        int fEndClamped = Mathf.Min(N, tEnd);

        for (int f = fStart; f < fEndClamped; f++)
        {
            if (dots50Swap && dots50ASwap)
            {
                // Db: full dot-swap — both D and Da simultaneously. All subfields change field.
                // After tStart: FieldB={sub0,sub1}, FieldA={sub2,sub3}.
                // CUED (FieldB translates): sub0 (coh→FieldB)=Linear, sub1 (noise→FieldB)=NonCoherent.
                // UNCUED (FieldA translates): sub2 (coh→FieldA)=Linear, sub3 (noise→FieldA)=NonCoherent.
                if (isCued)
                {
                    cond.subfields[0].motionKindByFrame[f] = CondLib.MotionKind.Linear;
                    cond.subfields[1].motionKindByFrame[f] = CondLib.MotionKind.NonCoherent;
                }
                else
                {
                    cond.subfields[2].motionKindByFrame[f] = CondLib.MotionKind.Linear;
                    cond.subfields[3].motionKindByFrame[f] = CondLib.MotionKind.NonCoherent;
                }
            }
            else if (dots50Swap)
            {
                // Field B={sub2,sub1}: sub2 original→Linear, sub1 swapped-in→NonCoherent
                if (isCued)
                {
                    cond.subfields[2].motionKindByFrame[f] = CondLib.MotionKind.Linear;
                    cond.subfields[1].motionKindByFrame[f] = CondLib.MotionKind.NonCoherent;
                }
                else  // Field A={sub0,sub3}: sub0 original→Linear, sub3 swapped-in→NonCoherent
                {
                    cond.subfields[0].motionKindByFrame[f] = CondLib.MotionKind.Linear;
                    cond.subfields[3].motionKindByFrame[f] = CondLib.MotionKind.NonCoherent;
                }
            }
            else if (dots50ASwap)
            {
                // Coherent-half swap: Field B={sub0,sub3}, Field A={sub2,sub1} after tStart.
                // Sub0 (swapped-in from A's coherent half) inherits coherent role; sub3 (original B noise) = NonCoherent.
                // Sub2 (swapped-in from B's coherent half) inherits coherent role; sub1 (original A noise) = NonCoherent.
                if (isCued)
                {
                    cond.subfields[0].motionKindByFrame[f] = CondLib.MotionKind.Linear;
                    cond.subfields[3].motionKindByFrame[f] = CondLib.MotionKind.NonCoherent;
                }
                else  // Field A={sub2,sub1}: sub2 swapped-in coherent→Linear, sub1 original noise→NonCoherent
                {
                    cond.subfields[2].motionKindByFrame[f] = CondLib.MotionKind.Linear;
                    cond.subfields[1].motionKindByFrame[f] = CondLib.MotionKind.NonCoherent;
                }
            }
            else if (depth50ASwap || depth50BSwap)
            {
                // ZdA: translators are Far-group (S1,S2). ZdB: translators are Near-group (S1,S2).
                // In both cases the same subfields translate: S2(coh) and S1(noncoh) for CUED,
                // S0(coh) and S3(noncoh) for UNCUED. Depth plane differs between ZdA and ZdB
                // but is already set correctly in the per-frame loop above.
                if (isCued)
                {
                    cond.subfields[2].motionKindByFrame[f] = CondLib.MotionKind.Linear;
                    cond.subfields[1].motionKindByFrame[f] = CondLib.MotionKind.NonCoherent;
                }
                else
                {
                    cond.subfields[0].motionKindByFrame[f] = CondLib.MotionKind.Linear;
                    cond.subfields[3].motionKindByFrame[f] = CondLib.MotionKind.NonCoherent;
                }
            }
            else
            {
                if (isCued)
                {
                    cond.subfields[2].motionKindByFrame[f] = CondLib.MotionKind.Linear;
                    cond.subfields[3].motionKindByFrame[f] = CondLib.MotionKind.NonCoherent;
                }
                else
                {
                    cond.subfields[0].motionKindByFrame[f] = CondLib.MotionKind.Linear;
                    cond.subfields[1].motionKindByFrame[f] = CondLib.MotionKind.NonCoherent;
                }
            }
        }

        return cond;
    }
}