using UnityEngine;

public class BillboardLabel : MonoBehaviour
{
    void LateUpdate()
    {
        var cam = Camera.main;
        if (!cam) return;

        // Face camera fully (pitch + yaw)
        transform.LookAt(cam.transform.position, Vector3.up);
        // Flip so text faces camera (TextMesh forward points -Z)
        transform.Rotate(0f, 180f, 0f, Space.Self);
    }
}