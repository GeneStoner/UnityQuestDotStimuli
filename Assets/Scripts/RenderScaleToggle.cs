using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;
using UnityEngine.UI;
using UnityEngine.XR;

/// <summary>
/// TEST BUILD ONLY (branch test/render-scale).
///
/// Left-controller X button cycles the URP render scale between 1.0 (Meta's
/// default eye buffer, 1680x1760 per eye on Quest 3) and 1.23 (the panel's
/// 2064x2208). Lets the observer A/B the same dots for sharpness.
///
/// Spawns itself after scene load, so no scene edit is needed. The chosen
/// scale, the measured FPS and the eye-texture size are logged once per press:
///     adb logcat -s Unity | grep RenderScale
///
/// NOTE: this writes to the URP asset at runtime. In the editor that dirties
/// Mobile_RPAsset, so the original value is restored on quit.
/// </summary>
[DisallowMultipleComponent]
public class RenderScaleToggle : MonoBehaviour
{
    private static readonly float[] SCALES = { 1.0f, 1.23f };
    private const float LABEL_SECONDS = 2.5f;

    private int _index;
    private float _original = -1f;
    private bool _wasPressed;
    private Text _label;
    private GameObject _canvasRoot;
    private float _hideAt;
    private float _frames;
    private float _elapsed;
    private float _fps;
    private float _logSizeAt = -1f;

    [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.AfterSceneLoad)]
    private static void Spawn()
    {
        var go = new GameObject("RenderScaleToggle");
        go.AddComponent<RenderScaleToggle>();
        DontDestroyOnLoad(go);
    }

    private static UniversalRenderPipelineAsset Asset =>
        (QualitySettings.renderPipeline ?? GraphicsSettings.defaultRenderPipeline) as UniversalRenderPipelineAsset;

    void Start()
    {
        var asset = Asset;
        if (asset == null)
        {
            Debug.LogWarning("[RenderScale] No URP asset found; toggle disabled.");
            enabled = false;
            return;
        }

        _original = asset.renderScale;
        // Start from whichever listed scale is closest to the project's value
        _index = Mathf.Abs(_original - SCALES[1]) < Mathf.Abs(_original - SCALES[0]) ? 1 : 0;
        BuildLabel();
        Apply("startup");
    }

    void Update()
    {
        _frames += 1f;
        _elapsed += Time.unscaledDeltaTime;
        if (_elapsed >= 1f)
        {
            _fps = _frames / _elapsed;
            _frames = 0f;
            _elapsed = 0f;
        }

        bool pressed = XButtonDown();
        if (pressed && !_wasPressed)
        {
            _index = (_index + 1) % SCALES.Length;
            Apply("X button");
        }
        _wasPressed = pressed;

        if (_logSizeAt > 0f && Time.unscaledTime > _logSizeAt)
        {
            _logSizeAt = -1f;
            Debug.Log($"[RenderScale] now at scale {SCALES[_index]:F2}: eye texture " +
                      $"{XRSettings.eyeTextureWidth}x{XRSettings.eyeTextureHeight}, fps {_fps:F1}");
        }

        if (_canvasRoot != null && _canvasRoot.activeSelf && Time.unscaledTime > _hideAt)
            _canvasRoot.SetActive(false);

        FaceCamera();
    }

    void OnApplicationQuit()
    {
        var asset = Asset;
        if (asset != null && _original > 0f) asset.renderScale = _original;
    }

    // ── internals ─────────────────────────────────────────────────────────────

    private static bool XButtonDown()
    {
        var hand = InputDevices.GetDeviceAtXRNode(XRNode.LeftHand);
        return hand.isValid
            && hand.TryGetFeatureValue(CommonUsages.primaryButton, out bool value)
            && value;
    }

    private void Apply(string why)
    {
        var asset = Asset;
        if (asset == null) return;

        float scale = SCALES[_index];
        asset.renderScale = scale;

        Debug.Log($"[RenderScale] scale={scale:F2} ({why}); fps before change {_fps:F1}");
        _logSizeAt = Time.unscaledTime + 1f;   // eye texture resizes on a later frame

        if (_label != null)
        {
            _label.text = $"Render scale {scale:F2}";
            _canvasRoot.SetActive(true);
            _hideAt = Time.unscaledTime + LABEL_SECONDS;
        }
    }

    private void BuildLabel()
    {
        _canvasRoot = new GameObject("RenderScaleLabel");
        _canvasRoot.transform.SetParent(transform, false);

        var canvas = _canvasRoot.AddComponent<Canvas>();
        canvas.renderMode = RenderMode.WorldSpace;
        var rt = canvas.GetComponent<RectTransform>();
        rt.sizeDelta = new Vector2(640f, 120f);
        rt.localScale = Vector3.one * 0.001f;

        var textGo = new GameObject("Text");
        textGo.transform.SetParent(_canvasRoot.transform, false);
        _label = textGo.AddComponent<Text>();
        _label.font = Resources.GetBuiltinResource<Font>("LegacyRuntime.ttf");
        _label.fontSize = 44;
        _label.alignment = TextAnchor.MiddleCenter;
        _label.color = new Color(1f, 1f, 1f, 0.85f);
        var trt = _label.GetComponent<RectTransform>();
        trt.anchorMin = Vector2.zero;
        trt.anchorMax = Vector2.one;
        trt.offsetMin = trt.offsetMax = Vector2.zero;

        _canvasRoot.SetActive(false);
    }

    private void FaceCamera()
    {
        if (_canvasRoot == null || !_canvasRoot.activeSelf) return;
        var cam = Camera.main;
        if (cam == null) return;

        // Below the line of sight, clear of the stimulus aperture
        Transform c = cam.transform;
        _canvasRoot.transform.position = c.position + c.forward * 1.5f - c.up * 0.35f;
        _canvasRoot.transform.rotation = c.rotation;
    }
}
