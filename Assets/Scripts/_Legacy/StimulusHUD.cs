#if false
using TMPro;
using UnityEngine;

[ExecuteAlways]
public class StimulusHUD : MonoBehaviour
{
    [Header("References")]
    public DotFieldDual dot;
    public TextMeshProUGUI textUI;

    [Header("Visibility")]
    public bool showWhileStopped = true;
    public bool showWhileRunning = true;

    [Header("Follow Camera")]
    public bool followHead = true;                          // keep HUD in front of the HMD
    public Transform followCamera;                          // auto-assigns Main Camera if null
    public Vector3 localOffset = new Vector3(0f, -0.25f, 0.7f); // relative to HMD (meters)

    [Header("Scale")]
    public bool lockScaleToHudScale = true;                 // force a constant world-space size
    [Tooltip("World-space scale for the Canvas transform (smaller number = smaller in VR).")]
    public float hudScale = 0.0016f;                        // ~nice size; tweak 0.001–0.003

    [Header("Formatting")]
    public bool multiline = true;                           // split " | " into separate lines
    public bool uppercase = false;                          // shouty mode, off by default
    public string prefix = "";                              // optional prefix, e.g. "[DEBUG] "
    public string suffix = "";                              // optional suffix

    void Reset()
    {
        if (dot == null) dot = FindAnyObjectByType<DotFieldDual>();
        if (followCamera == null && Camera.main) followCamera = Camera.main.transform;
        if (textUI == null) textUI = GetComponentInChildren<TextMeshProUGUI>(true);
    }

    void LateUpdate()
    {
        if (dot == null || textUI == null) return;

        // Follow head pose
        if (followHead && followCamera != null)
        {
            transform.position = followCamera.TransformPoint(localOffset);
            transform.rotation = Quaternion.LookRotation(followCamera.forward, Vector3.up);

            // Keep scale stable and non-mirrored
            if (lockScaleToHudScale)
            {
                float s = Mathf.Max(1e-5f, hudScale);
                transform.localScale = new Vector3(s, s, s);
            }
            else
            {
                var s = transform.localScale;
                transform.localScale = new Vector3(Mathf.Abs(s.x), Mathf.Abs(s.y), Mathf.Abs(s.z));
            }
        }

        // Visibility
        bool running = dot.TrialRunning;
        bool visible = (running && showWhileRunning) || (!running && showWhileStopped);
        if (textUI.gameObject.activeSelf != visible)
            textUI.gameObject.SetActive(visible);

        // Content
        if (visible)
        {
            string tag = dot.GetStimulusTag();         // e.g., "A:red,CW | B:grn,CCW | delay:B 0.50s | trans:A 045°"
            textUI.text = FormatTag(tag);
        }
    }

    string FormatTag(string s)
    {
        if (string.IsNullOrEmpty(s)) return "";
        if (multiline) s = s.Replace(" | ", "\n");
        if (uppercase) s = s.ToUpperInvariant();
        if (!string.IsNullOrEmpty(prefix)) s = prefix + s;
        if (!string.IsNullOrEmpty(suffix)) s = s + suffix;
        return s;
    }
}
#endif