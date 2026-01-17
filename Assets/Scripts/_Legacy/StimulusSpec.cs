using UnityEngine;

public enum Field { A, B }

public struct StimulusSpec
{
    public int pairId;
    public int directionDeg;
    public float coherence;             // future: fraction of signal dots
    public int[] signalIndices;         // which dot indices are “signal” (move along dir)
    public Vector2[] transPosAtOnset;   // positions at delayed onset for translating field
    public Vector2[] staticPosAtOnset;  // positions at delayed onset for static field
    public int sessionSeed;
}