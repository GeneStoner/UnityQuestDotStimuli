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

    // Distinct stimuli = (CUED/UNCUED) × (8 headings) × (rotationConfigFactor) × (delayedColorFactor) × swapFactor
    public override int GetUniqueStimulusCount()
    {
        int condFactor = 2;
        int headingFactor = 8;
        int rotFactor = includeBothRotationConfigs ? 2 : 1;
        int colorFactor = balanceDelayedFieldColor ? 2 : 1;

        int swapFactor = 1;
        if (includeMotionSwaps) swapFactor *= 2;
        if (includeColorSwaps)  swapFactor *= 2;
        if (includeDots50Swaps) swapFactor *= 2;

        return condFactor * headingFactor * rotFactor * colorFactor * swapFactor;
    }

    public override List<PlannedTrial> GetPlannedTrials(System.Random rng)
    {
        var trials = new List<PlannedTrial>(capacity: Mathf.Max(1, GetTargetNumberTrialsEstimate()));

        string[] condIDs = { "CUED", "UNCUED" };
        float[] headings = { 0f, 45f, 90f, 135f, 180f, 225f, 270f, 315f };

        int[] rotCfgs = includeBothRotationConfigs ? new[] { 0, 1 } : new[] { 0 };

        // Build all combinations (power set) of active swap flags
        var activeFlags = new List<int>();
        if (includeMotionSwaps) activeFlags.Add((int)SwapFlags.Motion);
        if (includeColorSwaps)  activeFlags.Add((int)SwapFlags.Color);
        if (includeDots50Swaps) activeFlags.Add((int)SwapFlags.Dots50);

        var swapValues = new List<int> { 0 }; // None always included
        foreach (int flag in activeFlags)
        {
            int count = swapValues.Count;
            for (int i = 0; i < count; i++)
                swapValues.Add(swapValues[i] | flag);
        }

        // This is now the ONLY repetition knob.
        int reps = Mathf.Max(1, repeatsPerStimulus);

        int idx = 0;

        foreach (var condID in condIDs)
        {
            foreach (var h in headings)
            {
                foreach (int rotCfg in rotCfgs)
                {
                    foreach (int swap in swapValues)
                    {
                        if (balanceDelayedFieldColor)
                        {
                            // Two distinct stimuli (DelR, DelG) per (cond × heading × rotCfg × swap)
                            for (int r = 0; r < reps; r++)
                            {
                                trials.Add(MakeTrial(rng, ref idx, condID, h, rotCfg, COLOR_RED, swap));
                                trials.Add(MakeTrial(rng, ref idx, condID, h, rotCfg, COLOR_GREEN, swap));
                            }
                        }
                        else
                        {
                            // One distinct stimulus per (cond × heading × rotCfg × swap)
                            for (int r = 0; r < reps; r++)
                            {
                                trials.Add(MakeTrial(rng, ref idx, condID, h, rotCfg, COLOR_GREEN, swap));
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
                                   int swapFlags = 0)
    {
        var t = new PlannedTrial
        {
            index = idx++,
            conditionID = condID,
            headingDeg = headingDeg,
            rotationConfig = rotationConfig,
            delayedFieldColorCode = delayedColorCode,
            swapFlags = swapFlags
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
        var cond = new CondLib.StimulusCondition
        {
            name = $"Trial_{t.index}_{t.conditionID}_{rotTag}_Del{(t.delayedFieldColorCode == COLOR_RED ? "R" : "G")}_Sw{swapTag}"
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
        Color nonDelayedColor = ColorFromCode(OppositeColorCode(t.delayedFieldColorCode));

        bool motionSwap = (t.swapFlags & (int)SwapFlags.Motion) != 0;
        bool colorSwap  = (t.swapFlags & (int)SwapFlags.Color)  != 0;
        bool dots50Swap = (t.swapFlags & (int)SwapFlags.Dots50) != 0;

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

            // Eye/depth fixed
            for (int s = 0; s < 4; s++)
            {
                cond.subfields[s].eyeByFrame[f]   = CondLib.Eye.Both;
                cond.subfields[s].depthByFrame[f] = CondLib.DepthPlane.Fixation;
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
                if (isCued)  // Field B={sub2,sub1}: sub2=Linear, sub1=NonCoherent
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