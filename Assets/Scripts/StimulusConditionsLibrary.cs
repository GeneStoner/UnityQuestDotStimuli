// FILE: StimulusConditionsLibrary.cs
using System;
using UnityEngine;

public static class StimulusConditionsLibrary
{
    public enum MotionKind
    {
        None = 0,
        RotationCW = 1,
        RotationCCW = 2,
        Linear = 3,
        NonCoherent = 4
    }

    public enum Eye
    {
        Both = 0,
        Left = 1,
        Right = 2
    }

    public enum DepthPlane
    {
        Fixation = 0,
        Near = 1,
        Far = 2
    }

    [Serializable]
    public struct Timeline
    {
        public int totalFrames;
    }

    [Serializable]
    public class SubfieldTracks
    {
        public MotionKind[] motionKindByFrame;
        public bool[]       visibleByFrame;
        public Color[]      colorByFrame;
        public Eye[]        eyeByFrame;
        public DepthPlane[] depthByFrame;
    }

    [Serializable]
    public class StimulusCondition
    {
        public string name;
        public Timeline timeline;
        public SubfieldTracks[] subfields; // length 4
    }

    // --- Helpers ----------------------------------------------------------

    public static StimulusCondition CreateEmpty(string name, int totalFrames)
    {
        var cond = new StimulusCondition
        {
            name = name,
            timeline = new Timeline { totalFrames = totalFrames },
            subfields = new SubfieldTracks[4]
        };

        for (int s = 0; s < 4; s++)
        {
            cond.subfields[s] = new SubfieldTracks
            {
                motionKindByFrame = new MotionKind[totalFrames],
                visibleByFrame    = new bool[totalFrames],
                colorByFrame      = new Color[totalFrames],
                eyeByFrame        = new Eye[totalFrames],
                depthByFrame      = new DepthPlane[totalFrames]
            };

            // default: invisible, no motion, fixation plane, both eyes
            for (int f = 0; f < totalFrames; f++)
            {
                cond.subfields[s].motionKindByFrame[f] = MotionKind.None;
                cond.subfields[s].visibleByFrame[f]    = false;
                cond.subfields[s].colorByFrame[f]      = Color.black;
                cond.subfields[s].eyeByFrame[f]        = Eye.Both;
                cond.subfields[s].depthByFrame[f]      = DepthPlane.Fixation;
            }
        }

        return cond;
    }
}