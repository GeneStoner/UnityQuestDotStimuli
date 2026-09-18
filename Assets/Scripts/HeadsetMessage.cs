using UnityEngine;
using UnityEngine.UI;

/// <summary>
/// Brief message shown in front of the observer, e.g. when a trial is skipped.
/// Static entry point so any script can call it without scene wiring:
///
///     HeadsetMessage.Show("Trial skipped - it will be repeated", 2f);
///
/// Nothing is drawn unless something asks for a message.
/// </summary>
[DisallowMultipleComponent]
public class HeadsetMessage : MonoBehaviour
{
    private static HeadsetMessage _instance;

    private GameObject _canvasRoot;
    private Text _text;
    private float _hideAt;

    public static void Show(string message, float seconds = 2f)
    {
        if (_instance == null)
        {
            var go = new GameObject("HeadsetMessage");
            DontDestroyOnLoad(go);
            _instance = go.AddComponent<HeadsetMessage>();
            _instance.Build();
        }
        _instance.Display(message, seconds);
    }

    private void Build()
    {
        _canvasRoot = new GameObject("HeadsetMessageCanvas");
        _canvasRoot.transform.SetParent(transform, false);

        var canvas = _canvasRoot.AddComponent<Canvas>();
        canvas.renderMode = RenderMode.WorldSpace;
        var rt = canvas.GetComponent<RectTransform>();
        rt.sizeDelta = new Vector2(760f, 140f);
        rt.localScale = Vector3.one * 0.001f;

        var textGo = new GameObject("Text");
        textGo.transform.SetParent(_canvasRoot.transform, false);
        _text = textGo.AddComponent<Text>();
        _text.font = Resources.GetBuiltinResource<Font>("LegacyRuntime.ttf");
        _text.fontSize = 34;
        _text.alignment = TextAnchor.MiddleCenter;
        _text.color = new Color(1f, 0.85f, 0.4f, 0.9f);   // amber: not part of the stimulus
        var trt = _text.GetComponent<RectTransform>();
        trt.anchorMin = Vector2.zero;
        trt.anchorMax = Vector2.one;
        trt.offsetMin = trt.offsetMax = Vector2.zero;

        _canvasRoot.SetActive(false);
    }

    private void Display(string message, float seconds)
    {
        if (_text == null) return;
        _text.text = message;
        _hideAt = Time.unscaledTime + seconds;
        _canvasRoot.SetActive(true);
        Place();
    }

    void Update()
    {
        if (_canvasRoot == null || !_canvasRoot.activeSelf) return;
        if (Time.unscaledTime > _hideAt) { _canvasRoot.SetActive(false); return; }
        Place();
    }

    private void Place()
    {
        var cam = Camera.main;
        if (cam == null) return;
        Transform c = cam.transform;
        // Below the stimulus aperture, clear of the dots
        _canvasRoot.transform.position = c.position + c.forward * 1.5f - c.up * 0.30f;
        _canvasRoot.transform.rotation = c.rotation;
    }
}
