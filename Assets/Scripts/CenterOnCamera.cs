using UnityEngine;

public class CenterOnCamera : MonoBehaviour
{
    public float distanceMeters = 2.0f;
    public float verticalOffsetMeters = -0.25f;
    public bool alignYawOnly = true;

    [Header("Follow behavior")]
    public bool followCameraContinuously = true; // NEW: keep stimulus locked in front

    void Start()
    {
        PositionToCamera();
    }

    void Update()
    {
        if (followCameraContinuously)
            PositionToCamera();
    }

    void PositionToCamera()
    {
        var cam = Camera.main;
        if (!cam) return;

        // Place forward of HMD
        transform.position = cam.transform.position + cam.transform.forward * distanceMeters;
        // Vertical nudge
        transform.position += new Vector3(0f, verticalOffsetMeters, 0f);

        // Orientation
        if (alignYawOnly)
        {
            var fwd = cam.transform.forward; fwd.y = 0f;
            if (fwd.sqrMagnitude < 1e-6f) fwd = cam.transform.forward;
            transform.rotation = Quaternion.LookRotation(fwd, Vector3.up);
        }
        else
        {
            transform.rotation = cam.transform.rotation;
        }
    }
}