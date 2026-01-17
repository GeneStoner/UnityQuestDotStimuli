using System;
using System.Linq;
using UnityEngine;

public static class StimulusSpecFactory
{
    public static StimulusSpec Make(
        int directionDeg, int sessionSeed, int pairId,
        int nDots, float apertureDeg, float dotSizeDeg)
    {
        var rng = (sessionSeed == 0)
            ? new System.Random(Hash(pairId, directionDeg))
            : new System.Random(Hash(sessionSeed, pairId, directionDeg));

        // Sample independent positions for the two fields at the moment of delayed onset
        Vector2[] trans = new Vector2[nDots];
        Vector2[] stat  = new Vector2[nDots];
        for (int i = 0; i < nDots; i++) trans[i] = SampleInDisk(rng, apertureDeg * 0.5f);
        for (int i = 0; i < nDots; i++) stat[i]  = SampleInDisk(rng, apertureDeg * 0.5f);

        // All dots signal for now (coherence=1). We’ll add actual coherence later.
        int[] signalIdx = Enumerable.Range(0, nDots).ToArray();

        return new StimulusSpec
        {
            pairId = pairId,
            directionDeg = directionDeg,
            coherence = 1f,
            signalIndices = signalIdx,
            transPosAtOnset = trans,
            staticPosAtOnset = stat,
            sessionSeed = sessionSeed,
        };
    }

    static int Hash(params int[] xs) { unchecked { int h = 17; foreach (var x in xs) h = h * 31 + x; return h; } }

    static Vector2 SampleInDisk(System.Random rng, float radiusDeg)
    {
        double u = rng.NextDouble();
        double a = rng.NextDouble() * Math.PI * 2.0;
        float r = (float)(radiusDeg * Math.Sqrt(u));
        return new Vector2(r * (float)Math.Cos(a), r * (float)Math.Sin(a));
    }
}