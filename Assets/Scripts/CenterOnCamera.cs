using UnityEngine;

public class CenterOnCamera : MonoBehaviour
{
    [Header("Camera source (recommended)")]
    [Tooltip("Assign your XR camera here (the one under XR Origin/Camera Offset). If null, falls back to Camera.main.")]
    public Camera targetCamera;

    [Header("Placement")]
    public float distanceMeters = 2.0f;
    public float verticalOffsetMeters = -0.25f;
    public bool alignYawOnly = true;

    [Header("Follow behavior")]
    public bool followCameraContinuously = true;

    [Header("Debug")]
    public bool logOnceOnStart = true;

    private bool _logged = false;

    void Start()
    {
        PositionToCamera();
        LogDebugOnce("Start");
    }

    void Update()
    {
        if (followCameraContinuously)
        {
            PositionToCamera();
            LogDebugOnce("Update");
        }
    }

    void PositionToCamera()
    {
        var cam = targetCamera != null ? targetCamera : Camera.main;
        if (!cam) return;

        // Place forward of HMD
        transform.position = cam.transform.position + cam.transform.forward * distanceMeters;

        // Vertical nudge (world up)
        transform.position += new Vector3(0f, verticalOffsetMeters, 0f);

        // Orientation
        if (alignYawOnly)
        {
            var fwd = cam.transform.forward;
            fwd.y = 0f;
            if (fwd.sqrMagnitude < 1e-6f) fwd = cam.transform.forward;
            transform.rotation = Quaternion.LookRotation(fwd.normalized, Vector3.up);
        }
        else
        {
            transform.rotation = cam.transform.rotation;
        }
    }

    void LogDebugOnce(string when)
    {
        if (!logOnceOnStart || _logged) return;

        var cam = targetCamera != null ? targetCamera : Camera.main;
        if (!cam) return;

        // ---- Build parent-chain strings (to find where scaling sneaks in) ----
        string Chain(Transform t)
        {
            if (t == null) return "<null>";
            string s = "";
            int guard = 0;
            while (t != null && guard++ < 32)
            {
                s += $"{t.name}[local={Fmt(t.localScale)} lossy={Fmt(t.lossyScale)}] ";
                t = t.parent;
                if (t != null) s += "<- ";
            }
            return s;
        }

        Debug.Log(
            $"[CenterOnCamera] ({when}) cam='{cam.name}' tag='{cam.tag}' " +
            $"camLocal={Fmt(cam.transform.localScale)} camLossy={Fmt(cam.transform.lossyScale)} " +
            $"stimPos={transform.position} stimLocal={Fmt(transform.localScale)} stimLossy={Fmt(transform.lossyScale)} " +
            $"dist={distanceMeters} vOff={verticalOffsetMeters}\n" +
            $"  Cam chain:  {Chain(cam.transform)}\n" +
            $"  Stim chain: {Chain(transform)}"
        );

        _logged = true;
    }

    static string Fmt(Vector3 v) => $"({v.x:0.###},{v.y:0.###},{v.z:0.###})";
}