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

    [Tooltip("Include 50%% dot-swap trials (sub1↔sub3 exchange field membership at translation onset).")]
    public bool includeDots50Swaps = false;

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
        if (includeDots50Swaps)        swapFactor *= 2;
        if (includeDepthSwaps)         swapFactor *= 2;
        if (includeDepthPartialSwaps)  swapFactor *= 2;
        // ZdA and ZdB are mutually exclusive per trial; enabling both adds 2 conditions (not 3)
        if (includeDepth50ASwaps && includeDepth50BSwaps) swapFactor *= 3;
        else if (includeDepth50ASwaps || includeDepth50BSwaps) swapFactor *= 2;
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
        if (includeDots50Swaps)        activeFlags.Add((int)SwapFlags.Dots50);
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
        t.onsetFrame = MsToFrames(delayedOnset_ms);

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
            // Default: [A, A, B, B]. With dots50 swap at tStart: [A, B, B, A].
            bool sub1isA = !(dots50Swap && afterSwap);
            bool sub3isA =  (dots50Swap && afterSwap);

            // Sub0: always Field A
            cond.subfields[0].motionKindByFrame[f] = curARot;
            cond.subfields[0].colorByFrame[f]   = fieldAColor;
            cond.subfields[0].visibleByFrame[f] = true;

            // Sub1: Field A by default, Field B if dots50 swapped
            cond.subfields[1].motionKindByFrame[f] = sub1isA ? curARot : curBRot;
            if (sub1isA)
            {
                cond.subfields[1].colorByFrame[f]   = fieldAColor;
                cond.subfields[1].visibleByFrame[f] = true;
            }
            else
            {
                cond.subfields[1].colorByFrame[f]   = afterOnset ? fieldBColor : rgbaBlack;
                cond.subfields[1].visibleByFrame[f] = afterOnset;
            }

            // Sub2: always Field B
            cond.subfields[2].motionKindByFrame[f] = curBRot;
            cond.subfields[2].colorByFrame[f]   = afterOnset ? fieldBColor : rgbaBlack;
            cond.subfields[2].visibleByFrame[f] = afterOnset;

            // Sub3: Field B by default, Field A if dots50 swapped
            if (sub3isA)
            {
                cond.subfields[3].motionKindByFrame[f] = curARot;
                cond.subfields[3].colorByFrame[f]   = fieldAColor;
                cond.subfields[3].visibleByFrame[f] = true;
            }
            else
            {
                cond.subfields[3].motionKindByFrame[f] = curBRot;
                cond.subfields[3].colorByFrame[f]   = afterOnset ? fieldBColor : rgbaBlack;
                cond.subfields[3].visibleByFrame[f] = afterOnset;
            }

            // Eye always binocular
            for (int s = 0; s < 4; s++)
                cond.subfields[s].eyeByFrame[f] = CondLib.Eye.Both;

            // Depth planes: follow field membership, swap at tStart if depthSwap
            if (useDepthPlanes)
            {
                CondLib.DepthPlane curADepth = (depthSwap && afterSwap) ? fieldBDepth : fieldADepth;
                CondLib.DepthPlane curBDepth = (depthSwap && afterSwap) ? fieldADepth : fieldBDepth;

                cond.subfields[0].depthByFrame[f] = curADepth;                      // sub0: always Field A
                cond.subfields[1].depthByFrame[f] = sub1isA ? curADepth : curBDepth; // sub1: follows membership
                cond.subfields[2].depthByFrame[f] = curBDepth;                      // sub2: always Field B
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
            if (dots50Swap)
            {
                // Field B={sub2,sub1}: sub2=Linear, sub1=NonCoherent
                if (isCued)
                {
                    cond.subfields[2].motionKindByFrame[f] = CondLib.MotionKind.Linear;
                    cond.subfields[1].motionKindByFrame[f] = CondLib.MotionKind.NonCoherent;
                }
                else  // Field A={sub0,sub3}: sub0=Linear, sub3=NonCoherent
                {
                    cond.subfields[0].motionKindByFrame[f] = CondLib.MotionKind.Linear;
                    cond.subfields[3].motionKindByFrame[f] = CondLib.MotionKind.NonCoherent;
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