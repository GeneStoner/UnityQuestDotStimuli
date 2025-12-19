// FILE: ExpSpecTestPhase.cs
using System;
using System.Collections.Generic;
using UnityEngine;
using CondLib = StimulusConditionsLibrary;

[CreateAssetMenu(fileName = "ExpSpecTestPhase",
                 menuName = "Stimuli/Experiment Specs/Test Phase",
                 order = 10)]
public class ExpSpecTestPhase : ExperimentSpec
{
    [Header("Balancing")]
    [Tooltip("Base repetitions per (condition × heading). If balanceDelayedFieldColor is true, total per cell becomes 2× this (one Red-delayed + one Green-delayed per repetition).")]
    [Min(1)]
    public int repetitionsPerConditionPerHeading = 5;

    // We have 2 conditions × 8 headings × (1 or 2 delayed-colors)
    public override int GetUniqueStimulusCount()
    {
        int baseUnique = 2 * 8; // CUED/UNCUED × 8 headings
        int colorFactor = balanceDelayedFieldColor ? 2 : 1;
        return baseUnique * colorFactor;
    }

    public override List<PlannedTrial> GetPlannedTrials(System.Random rng)
    {
        var trials = new List<PlannedTrial>();

        string[] condIDs = { "CUED", "UNCUED" };
        float[] headings = { 0f, 45f, 90f, 135f, 180f, 225f, 270f, 315f };

        int idx = 0;

        foreach (var condID in condIDs)
        {
            foreach (var h in headings)
            {
                for (int r = 0; r < repetitionsPerConditionPerHeading; r++)
                {
                    if (balanceDelayedFieldColor)
                    {
                        // perfect balance per (cond×heading×rep): one R-delayed and one G-delayed
                        trials.Add(MakeTrial(rng, ref idx, condID, h, COLOR_RED));
                        trials.Add(MakeTrial(rng, ref idx, condID, h, COLOR_GREEN));
                    }
                    else
                    {
                        // legacy: delayed field always green
                        trials.Add(MakeTrial(rng, ref idx, condID, h, COLOR_GREEN));
                    }
                }
            }
        }

        // Shuffle
        for (int i = trials.Count - 1; i > 0; i--)
        {
            int j = rng.Next(i + 1);
            (trials[i], trials[j]) = (trials[j], trials[i]);
        }

        // Reindex after shuffle
        for (int i = 0; i < trials.Count; i++)
            trials[i].index = i;

        return trials;
    }

    private PlannedTrial MakeTrial(System.Random rng, ref int idx, string condID, float headingDeg, int delayedColorCode)
    {
        var t = new PlannedTrial
        {
            index = idx++,
            conditionID = condID,
            headingDeg = headingDeg,
            delayedFieldColorCode = delayedColorCode
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

        var cond = new CondLib.StimulusCondition
        {
            name = $"Trial_{t.index}_{t.conditionID}_Del{(t.delayedFieldColorCode == COLOR_RED ? "R" : "G")}"
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

        // delayed field (B) color and opposite for the non-delayed field (A)
        Color delayedColor    = ColorFromCode(t.delayedFieldColorCode);
        Color nonDelayedColor = ColorFromCode(OppositeColorCode(t.delayedFieldColorCode));

        for (int f = 0; f < N; f++)
        {
            bool afterOnset = f >= onset;

            // Baseline rotations
            cond.subfields[0].motionKindByFrame[f] = CondLib.MotionKind.RotationCW;
            cond.subfields[1].motionKindByFrame[f] = CondLib.MotionKind.RotationCW;
            cond.subfields[2].motionKindByFrame[f] = CondLib.MotionKind.RotationCCW;
            cond.subfields[3].motionKindByFrame[f] = CondLib.MotionKind.RotationCCW;

            // Field A (non-delayed): visible always, opposite color
            cond.subfields[0].colorByFrame[f]   = nonDelayedColor;
            cond.subfields[1].colorByFrame[f]   = nonDelayedColor;
            cond.subfields[0].visibleByFrame[f] = true;
            cond.subfields[1].visibleByFrame[f] = true;

            // Field B (delayed): invisible pre-onset, delayedColor post-onset
            if (!afterOnset)
            {
                cond.subfields[2].colorByFrame[f]   = rgbaBlack;
                cond.subfields[3].colorByFrame[f]   = rgbaBlack;
                cond.subfields[2].visibleByFrame[f] = false;
                cond.subfields[3].visibleByFrame[f] = false;
            }
            else
            {
                cond.subfields[2].colorByFrame[f]   = delayedColor;
                cond.subfields[3].colorByFrame[f]   = delayedColor;
                cond.subfields[2].visibleByFrame[f] = true;
                cond.subfields[3].visibleByFrame[f] = true;
            }

            // Eye/depth fixed
            for (int s = 0; s < 4; s++)
            {
                cond.subfields[s].eyeByFrame[f]   = CondLib.Eye.Both;
                cond.subfields[s].depthByFrame[f] = CondLib.DepthPlane.Fixation;
            }
        }

        // Translation window: 50% coherence within selected field
        int fStart = Mathf.Max(0, tStart);
        int fEndClamped = Mathf.Min(N, tEnd);

        for (int f = fStart; f < fEndClamped; f++)
        {
            if (isCued)
            {
                // delayed field (B = 2,3)
                cond.subfields[2].motionKindByFrame[f] = CondLib.MotionKind.Linear;
                cond.subfields[3].motionKindByFrame[f] = CondLib.MotionKind.NonCoherent;
            }
            else
            {
                // non-delayed field (A = 0,1)
                cond.subfields[0].motionKindByFrame[f] = CondLib.MotionKind.Linear;
                cond.subfields[1].motionKindByFrame[f] = CondLib.MotionKind.NonCoherent;
            }
        }

        return cond;
    }
}