using TMPro;
using UnityEngine;

public class DirectionalTargetCreator : MonoBehaviour
{
    [Header("Wiring")]
    public Transform ringRoot;               // parent/anchor for the ring; rotation controls ring plane
    public GameObject targetPrefab;          // prefab with a sphere marker (+ optional 3D TextMeshPro label)
    public Transform refCamera;              // Main Camera (for billboarding)

    [Header("Layout")]
    [Min(0f)] public float radius = 1.0f;   // ring size
    public float height = 0.0f;              // vertical offset relative to ringRoot
    public int[] anglesDeg = new int[] { 0, 45, 90, 135, 180, 225, 270, 315 };

    [Header("Angle Controls")]
    public float angleOffsetDeg = 0f;          // shifts where 0° sits around the ring
    public bool degreesIncreaseClockwise = false; // if true, angles go CW instead of CCW

    [Header("Axes / Plane")]
    public bool useRingLocalAxes = true;     // ON: ring uses ringRoot.right/forward/up
    public bool flattenToHorizontal = false; // ON: forces ring onto world-XZ plane

    [Header("Behaviour")]
    public bool clearExistingOnSpawn = true;
    public bool faceCenter = true;           // rotate each target to look at ring center

    [Header("Labels (3D TextMeshPro)")]
    public bool attachLabels = true;
    public Vector3 labelLocalOffset = new Vector3(0f, 0.12f, 0f);
    public bool labelsBillboardToCamera = true;
    public bool labelsFaceCenterIfNotBillboarding = true;
    public bool fixLabelNegativeScale = true;

    // --- Editor helpers ---
    [ContextMenu("Respawn Targets")]
    public void RespawnTargets()
    {
        if (ringRoot == null) ringRoot = transform;
        if (targetPrefab == null)
        {
            Debug.LogError("[DirectionalTargetCreator] Target Prefab is not assigned.");
            return;
        }

        // 1) Clear old
        if (clearExistingOnSpawn)
        {
            for (int i = ringRoot.childCount - 1; i >= 0; i--)
            {
#if UNITY_EDITOR
                if (!Application.isPlaying)
                    DestroyImmediate(ringRoot.GetChild(i).gameObject);
                else
                    Destroy(ringRoot.GetChild(i).gameObject);
#else
                Destroy(ringRoot.GetChild(i).gameObject);
#endif
            }
        }

        // 2) Basis from ringRoot (or world)
        Vector3 up     = useRingLocalAxes ? ringRoot.up      : Vector3.up;
        Vector3 right  = useRingLocalAxes ? ringRoot.right   : Vector3.right;
        Vector3 forward= useRingLocalAxes ? ringRoot.forward : Vector3.forward;

        if (flattenToHorizontal)
        {
            // Project to XZ plane
            Vector3 f = forward; f.y = 0f;
            if (f.sqrMagnitude < 1e-6f) f = Vector3.forward;
            f.Normalize();
            forward = f;
            right   = new Vector3(forward.z, 0f, -forward.x); // 90° to forward on ground plane
            up      = Vector3.up;
        }

        // 3) Spawn around ring
        foreach (int a in anglesDeg)
        {
            float rad = a * Mathf.Deg2Rad;
            float theta = (a + angleOffsetDeg) * Mathf.Deg2Rad;
            if (degreesIncreaseClockwise) theta = -theta;

            Vector3 offset = right   * Mathf.Cos(theta) * radius
               + forward * Mathf.Sin(theta) * radius
               + up * height;

            Vector3 pos = ringRoot.position + offset;

            Quaternion rot = Quaternion.identity;
            if (faceCenter)
                rot = Quaternion.LookRotation((ringRoot.position - pos).normalized, up);

            var go = Instantiate(targetPrefab, pos, rot, ringRoot);
            go.name = $"Target_{a}deg";

            // 4) Label (3D TMP) handling
            if (!attachLabels) continue;

            var tmp3D = go.GetComponentInChildren<TextMeshPro>(true); // 3D, not UGUI
            if (tmp3D != null)
            {
                tmp3D.text = a.ToString() + "°";

                // Try to parent label to a "Marker" child for stable local offset
                Transform marker = FindChildByNameContains(go.transform, "marker");
                if (marker != null && tmp3D.transform.parent != marker)
                {
                    tmp3D.transform.SetParent(marker, worldPositionStays: false);
                    tmp3D.transform.localPosition = Vector3.zero; // start clean
                }

                // Apply local offset (relative to parent—marker if found, else target root)
                tmp3D.transform.localPosition = labelLocalOffset;

                // Orientation: billboard to camera, else face center, else keep target rotation
                if (labelsBillboardToCamera && refCamera != null)
                {
                    tmp3D.transform.rotation =
                        Quaternion.LookRotation(refCamera.forward, Vector3.up);
                }
                else if (labelsFaceCenterIfNotBillboarding)
                {
                    tmp3D.transform.rotation = go.transform.rotation;
                }

                // Ensure positive scale so text doesn't mirror
                if (fixLabelNegativeScale)
                {
                    var s = tmp3D.transform.localScale;
                    tmp3D.transform.localScale =
                        new Vector3(Mathf.Abs(s.x), Mathf.Abs(s.y), Mathf.Abs(s.z));
                }
            }
        }
    }

    [ContextMenu("Clear Targets")]
    public void ClearTargets()
    {
        if (ringRoot == null) ringRoot = transform;
        for (int i = ringRoot.childCount - 1; i >= 0; i--)
        {
#if UNITY_EDITOR
            if (!Application.isPlaying)
                DestroyImmediate(ringRoot.GetChild(i).gameObject);
            else
                Destroy(ringRoot.GetChild(i).gameObject);
#else
            Destroy(ringRoot.GetChild(i).gameObject);
#endif
        }
    }

    // Utility: case-insensitive partial match
    Transform FindChildByNameContains(Transform root, string containsLower)
    {
        containsLower = containsLower.ToLower();
        foreach (Transform t in root.GetComponentsInChildren<Transform>(true))
        {
            if (t == root) continue;
            if (t.name.ToLower().Contains(containsLower))
                return t;
        }
        return null;
    }

#if UNITY_EDITOR
    // Gizmo: ring preview
    void OnDrawGizmosSelected()
    {
        if (ringRoot == null) return;

        Vector3 up     = useRingLocalAxes ? ringRoot.up      : Vector3.up;
        Vector3 right  = useRingLocalAxes ? ringRoot.right   : Vector3.right;
        Vector3 forward= useRingLocalAxes ? ringRoot.forward : Vector3.forward;

        if (flattenToHorizontal)
        {
            Vector3 f = forward; f.y = 0f;
            if (f.sqrMagnitude < 1e-6f) f = Vector3.forward;
            f.Normalize();
            forward = f;
            right   = new Vector3(forward.z, 0f, -forward.x);
            up      = Vector3.up;
        }

        Gizmos.color = new Color(0.2f, 0.8f, 1f, 0.8f);
        int steps = 64;
        Vector3 prev = Vector3.zero;
        for (int i = 0; i <= steps; i++)
        {
            float t = (i / (float)steps) * Mathf.PI * 2f;
            Vector3 p = ringRoot.position
                      + right * Mathf.Cos(t) * radius
                      + forward * Mathf.Sin(t) * radius
                      + up * height;
            if (i > 0) Gizmos.DrawLine(prev, p);
            prev = p;
        }
    }
#endif
}