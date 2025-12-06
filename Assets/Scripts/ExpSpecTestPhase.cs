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
    [Tooltip("Repetitions per (condition × heading) combo.")]
    public int repetitionsPerConditionPerHeading = 5;

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
                    var t = new PlannedTrial();
                    t.index       = idx++;
                    t.conditionID = condID;
                    t.headingDeg  = h;

                    // Timing in frames
                    t.onsetFrame = MsToFrames(delayedOnset_ms);

                    int preTransFrames    = MsToFrames(preTranslation_ms);
                    int transFrames       = MsToFrames(translationDuration_ms);
                    int postTransMs       = 400; // tail after translation for testing
                    int postTransFrames   = MsToFrames(postTransMs);

                    t.translationStartFrame = t.onsetFrame + preTransFrames;
                    t.translationEndFrame   = t.translationStartFrame + transFrames;
                    t.totalFrames           = t.translationEndFrame + postTransFrames;

                    // RNG seeds per subfield (for reproducible dot layouts)
                    t.seedA0 = rng.Next();
                    t.seedA1 = rng.Next();
                    t.seedB2 = rng.Next();
                    t.seedB3 = rng.Next();

                    trials.Add(t);
                }
            }
        }

        // Shuffle trials
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

    public override CondLib.StimulusCondition BuildEffectiveCondition(PlannedTrial t)
    {
        int N = t.totalFrames;

        var cond = new CondLib.StimulusCondition();
        cond.name = $"Trial_{t.index}_{t.conditionID}";
        cond.timeline.totalFrames = N;
        cond.subfields = new CondLib.SubfieldTracks[4];

        for (int s = 0; s < 4; s++)
        {
            var sf = new CondLib.SubfieldTracks
            {
                motionKindByFrame = new CondLib.MotionKind[N],
                colorByFrame      = new Color[N],
                eyeByFrame        = new CondLib.Eye[N],
                depthByFrame      = new CondLib.DepthPlane[N],
                visibleByFrame    = new bool[N]
            };
            cond.subfields[s] = sf;
        }

        // Convention:
        //  - Subfields 0,1 = Field A (non-delayed)
        //  - Subfields 2,3 = Field B (delayed field)
        // Cued vs uncued:
        //  - CUED: translation (coh + noncoh) is in delayed field B.
        //  - UNCUED: translation (coh + noncoh) is in non-delayed field A.

        bool isCued = t.conditionID == "CUED";

        int onset  = t.onsetFrame;
        int tStart = t.translationStartFrame;
        int tEnd   = t.translationEndFrame; // treat as [tStart, tEnd)

        for (int f = 0; f < N; f++)
        {
            bool afterOnset = f >= onset;

            // ---------- Baseline motion: rotations ----------
            // Field A: CW
            cond.subfields[0].motionKindByFrame[f] = CondLib.MotionKind.RotationCW;
            cond.subfields[1].motionKindByFrame[f] = CondLib.MotionKind.RotationCW;

            // Field B: CCW
            cond.subfields[2].motionKindByFrame[f] = CondLib.MotionKind.RotationCCW;
            cond.subfields[3].motionKindByFrame[f] = CondLib.MotionKind.RotationCCW;

            // ---------- Color & visibility ----------
            // Non-delayed field A: visible & red throughout
            cond.subfields[0].colorByFrame[f]   = rgbaRed;
            cond.subfields[1].colorByFrame[f]   = rgbaRed;
            cond.subfields[0].visibleByFrame[f] = true;
            cond.subfields[1].visibleByFrame[f] = true;

            // Delayed field B:
            if (!afterOnset)
            {
                // Pre-delay: same as background (black), effectively invisible
                cond.subfields[2].colorByFrame[f]   = rgbaBlack;
                cond.subfields[3].colorByFrame[f]   = rgbaBlack;
                cond.subfields[2].visibleByFrame[f] = false;
                cond.subfields[3].visibleByFrame[f] = false;
            }
            else
            {
                // After delayed onset: now "appears" as green
                cond.subfields[2].colorByFrame[f]   = rgbaGreen;
                cond.subfields[3].colorByFrame[f]   = rgbaGreen;
                cond.subfields[2].visibleByFrame[f] = true;
                cond.subfields[3].visibleByFrame[f] = true;
            }

            // Eye/depth fixed for now
            for (int s = 0; s < 4; s++)
            {
                cond.subfields[s].eyeByFrame[f]   = CondLib.Eye.Both;
                cond.subfields[s].depthByFrame[f] = CondLib.DepthPlane.Fixation;
            }
        }

        // ---------- Translation window ----------
        // Implement 50% coherence: one subfield coherent, one non-coherent in the chosen field.
        int fStart = Mathf.Max(0, tStart);
        int fEndClamped = Mathf.Min(N, tEnd);

        for (int f = fStart; f < fEndClamped; f++)
        {
            if (isCued)
            {
                // CUED: translation belongs to delayed field (B = 2,3)
                cond.subfields[2].motionKindByFrame[f] = CondLib.MotionKind.Linear;       // coherent
                cond.subfields[3].motionKindByFrame[f] = CondLib.MotionKind.NonCoherent;  // non-coherent
            }
            else
            {
                // UNCUED: translation belongs to non-delayed field (A = 0,1)
                cond.subfields[0].motionKindByFrame[f] = CondLib.MotionKind.Linear;       // coherent
                cond.subfields[1].motionKindByFrame[f] = CondLib.MotionKind.NonCoherent;  // non-coherent
            }
        }

        return cond;
    }
}