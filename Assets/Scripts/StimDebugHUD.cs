using UnityEngine;
using UnityEngine.UI;

/// <summary>
/// VR-compatible HUD: World Space Canvas parented to the camera.
/// Replaces OnGUI (which doesn't render on Quest).
/// Shows experiment name + build date always; trial debug info during trials.
/// </summary>
[DisallowMultipleComponent]
public class StimDebugHUD : MonoBehaviour
{
    public TrialBlockRunner runner;

    // World-space HUD geometry
    private const float HUD_DIST      = 1.5f;    // metres in front of camera
    private const float HUD_VERT_OFF  = 0.12f;   // metres above camera centre (keeps it out of main stimulus FOV)
    private const float CANVAS_PX_W   = 640f;
    private const float CANVAS_PX_H   = 200f;
    private const float WORLD_SCALE   = 0.001f;  // 1 canvas-px = 1 mm → 640px = 0.64 m wide

    private Text _bannerText;
    private Text _debugText;
    private GameObject _canvasRoot;
    private bool _dismissed;   // once stimulus starts, HUD is gone for the session

    // ── Public API ────────────────────────────────────────────────────────────

    public void Bind(TrialBlockRunner r) { runner = r; }
    public void Tick() { }   // called by runner; no-op (we use Update)

    // ── Lifecycle ─────────────────────────────────────────────────────────────

    void Start()
    {
        Transform cam = Camera.main != null ? Camera.main.transform : transform;
        BuildCanvas(cam);
    }

    void Update()
    {
        if (_canvasRoot == null) return;

        // Latch: once stimulus starts for the first time, dismiss permanently
        if (!_dismissed && runner != null && !runner.HudVisible)
            _dismissed = true;

        bool visible = !_dismissed;
        _canvasRoot.SetActive(visible);

        if (!visible || _bannerText == null) return;

        // Banner: experiment name + build date
        _bannerText.text = $"{runner.ExperimentName}\nBuild: {BuildInfo.BUILD_DATE}";

        // Debug row: trial details while waiting for trigger
        if (_debugText == null) return;
        var t = runner.CurrentTrial;
        _debugText.text = (t == null)
            ? "Ready — press trigger to begin"
            : $"Trial {runner.TrialIndex + 1}/{runner.TrialsCount}  " +
              $"Cond: {t.conditionID}  Heading: {t.headingDeg:F1}°";
    }

    // ── Canvas construction ───────────────────────────────────────────────────

    void BuildCanvas(Transform cam)
    {
        // Root canvas object, parented to camera so it stays fixed in view
        var root = new GameObject("StimDebugHUD_Canvas");
        _canvasRoot = root;
        root.transform.SetParent(cam, worldPositionStays: false);
        root.transform.localPosition = new Vector3(0f, HUD_VERT_OFF, HUD_DIST);
        root.transform.localRotation = Quaternion.identity;
        root.transform.localScale    = Vector3.one * WORLD_SCALE;

        var canvas = root.AddComponent<Canvas>();
        canvas.renderMode   = RenderMode.WorldSpace;
        canvas.sortingOrder = 100;

        var rt = root.GetComponent<RectTransform>();
        rt.sizeDelta = new Vector2(CANVAS_PX_W, CANVAS_PX_H);

        // Semi-transparent dark background panel
        var bg = new GameObject("Background");
        bg.transform.SetParent(root.transform, worldPositionStays: false);
        var bgRt = bg.AddComponent<RectTransform>();
        bgRt.anchorMin = Vector2.zero;
        bgRt.anchorMax = Vector2.one;
        bgRt.offsetMin = Vector2.zero;
        bgRt.offsetMax = Vector2.zero;
        var img = bg.AddComponent<Image>();
        img.color = new Color(0f, 0f, 0f, 0.55f);

        // Banner: experiment name + build date (large, centred, top ~55% of canvas)
        _bannerText = MakeText(root,
            name:      "BannerText",
            anchorMin: new Vector2(0f, 0.45f),
            anchorMax: Vector2.one,
            fontSize:  26,
            style:     FontStyle.Bold,
            color:     Color.white,
            align:     TextAnchor.MiddleCenter);

        // Debug info: trial details (small, left-aligned, bottom ~45% of canvas)
        _debugText = MakeText(root,
            name:      "DebugText",
            anchorMin: Vector2.zero,
            anchorMax: new Vector2(1f, 0.45f),
            fontSize:  16,
            style:     FontStyle.Normal,
            color:     new Color(0.9f, 0.9f, 0.7f),
            align:     TextAnchor.MiddleLeft);
    }

    static Text MakeText(GameObject parent, string name,
                         Vector2 anchorMin, Vector2 anchorMax,
                         int fontSize, FontStyle style, Color color, TextAnchor align)
    {
        var go = new GameObject(name);
        go.transform.SetParent(parent.transform, worldPositionStays: false);

        var rt = go.AddComponent<RectTransform>();
        rt.anchorMin    = anchorMin;
        rt.anchorMax    = anchorMax;
        rt.offsetMin    = new Vector2(8f, 4f);
        rt.offsetMax    = new Vector2(-8f, -4f);

        var t = go.AddComponent<Text>();
        t.font           = Resources.GetBuiltinResource<Font>("LegacyRuntime.ttf");
        t.fontSize       = fontSize;
        t.fontStyle      = style;
        t.color          = color;
        t.alignment      = align;
        t.supportRichText = false;
        t.horizontalOverflow = HorizontalWrapMode.Wrap;
        t.verticalOverflow   = VerticalWrapMode.Overflow;
        return t;
    }
}
