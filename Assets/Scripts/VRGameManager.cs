
using UnityEngine;

public class VRGameManager : MonoBehaviour
{
    [Header("Stimulus Size Settings")]
    [Tooltip("Desired size of the stimulus in degrees of visual angle.")]
    public float desiredVisualAngleDegrees = 5f;

    [Tooltip("Distance from the viewer (camera) to the stimulus, in meters.")]
    public float stimulusDistance = 3f;

    [Tooltip("Assign the stimulus object you want to resize.")]
    public GameObject stimulusObject;

    void Start()
    {
        ScaleStimulusToDegrees();
    }

    void ScaleStimulusToDegrees()
    {
        if (stimulusObject == null)
        {
            Debug.LogWarning("Stimulus object is null. Cannot scale.");
            return;
        }

        float angleRadians = desiredVisualAngleDegrees * Mathf.Deg2Rad;
        float sizeMeters = 2f * stimulusDistance * Mathf.Tan(angleRadians / 2f);

        stimulusObject.transform.localScale = new Vector3(sizeMeters, sizeMeters, 1f);
        stimulusObject.transform.localPosition = new Vector3(0, 0, stimulusDistance);

        Debug.Log($"Scaled stimulus to {desiredVisualAngleDegrees}° → size {sizeMeters:F3} meters at {stimulusDistance} meters distance.");
    }
}
