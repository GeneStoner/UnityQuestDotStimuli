// FILE: ExperimentPlan.cs
using System;
using System.Collections.Generic;
using UnityEngine;
using CondLib = StimulusConditionsLibrary;

[CreateAssetMenu(fileName = "ExperimentPlan",
                 menuName = "Stimuli/Experiment Plan",
                 order = 11)]
public class ExperimentPlan : ScriptableObject
{
    [Serializable]
    public class Entry
    {
        [Tooltip("Index of condition within the StimulusConditionsLibrary (if applicable).")]
        public int conditionIndex = 0;

        [Tooltip("Number of repetitions for this condition.")]
        public int repetitions = 10;
    }

    [Header("Version pin for logging")]
    public string planVersion = "v1";

    [Header("Trial selection")]
    [Tooltip("If true, randomize trial order within a block.")]
    public bool fullyRandomized = true;

    [Header("Entries in this plan")]
    public List<Entry> trials = new List<Entry>();
}