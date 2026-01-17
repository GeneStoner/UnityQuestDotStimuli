// FILE: MonitorFovCalibrator.cs
using UnityEngine;

[DisallowMultipleComponent]
public class MonitorFovCalibrator : MonoBehaviour
{
    [Tooltip("Visible monitor height in centimeters (measure it).")]
    public float monitorHeightCm = 33.6f;

    [Tooltip("Your eye-to-screen viewing distance in centimeters.")]
    public float viewingDistanceCm = 57.0f;

    [Tooltip("Apply every frame (useful if something else overwrites FOV).")]
    public bool applyContinuously = false;

    void Start() => Apply();
    void Update() { if (applyContinuously) Apply(); }

    void Apply()
    {
        var cam = GetComponent<Camera>();
        if (!cam) return;

        float H = Mathf.Max(1e-3f, monitorHeightCm);
        float d = Mathf.Max(1e-3f, viewingDistanceCm);

        float fovRad = 2f * Mathf.Atan((H * 0.5f) / d);
        cam.fieldOfView = fovRad * Mathf.Rad2Deg;

        Debug.Log($"[MonitorFovCalibrator] Set Camera.fieldOfView={cam.fieldOfView:0.###} deg (H={H}cm, d={d}cm)");
    }
}