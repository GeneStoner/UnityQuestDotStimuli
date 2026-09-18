using UnityEngine;
using UnityEngine.UI;

/// <summary>
/// Shows "Experiment over" in the headset once the last trial is done, so the
/// experimenter can tell a finished session from a stalled one. Without it the
/// display simply goes quiet, which is indistinguishable from a fault.
///
/// Spawns itself after scene load; no scene wiring needed.
/// </summary>
[DisallowMultipleComponent]
public class SessionEndMessage : MonoBehaviour
{
    public string message = "Experiment over";
    public string subMessage = "You can take off the headset";

    private TrialBlockRunner _runner;
    private GameObject _canvasRoot;
    private bool _shown;

    [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.AfterSceneLoad)]
    private static void Spawn()
    {
        var go = new GameObject("SessionEndMessage");
        go.AddComponent<SessionEndMessage>();
        DontDestroyOnLoad(go);
    }

    void Update()
    {
        if (_shown) { FaceCamera(); return; }

        if (_runner == null)
        {
            _runner = FindObjectOfType<TrialBlockRunner>();
            if (_runner == null) return;
        }

        // Only after trials have actually run: Done is also the pre-session state
        if (!_runner.SessionFinished || _runner.TrialIndex == 0) return;

        Build();
        _shown = true;
        Debug.Log("[SessionEndMessage] Session complete: " +
                  $"{_runner.TrialIndex} trials started of {_runner.TrialsCount} planned.");
    }

    private void Build()
    {
        _canvasRoot = new GameObject("SessionEndCanvas");
        _canvasRoot.transform.SetParent(transform, false);

        var canvas = _canvasRoot.AddComponent<Canvas>();
        canvas.renderMode = RenderMode.WorldSpace;
        var rt = canvas.GetComponent<RectTransform>();
        rt.sizeDelta = new Vector2(700f, 220f);
        rt.localScale = Vector3.one * 0.001f;

        AddText(message, 48, new Color(1f, 1f, 1f, 0.9f), 30f);
        AddText(subMessage, 26, new Color(0.75f, 0.75f, 0.75f, 0.9f), -40f);
        FaceCamera();
    }

    private void AddText(string text, int size, Color color, float yOffset)
    {
        var go = new GameObject("Text");
        go.transform.SetParent(_canvasRoot.transform, false);

        var t = go.AddComponent<Text>();
        t.font = Resources.GetBuiltinResource<Font>("LegacyRuntime.ttf");
        t.text = text;
        t.fontSize = size;
        t.color = color;
        t.alignment = TextAnchor.MiddleCenter;

        var rt = t.GetComponent<RectTransform>();
        rt.anchorMin = Vector2.zero;
        rt.anchorMax = Vector2.one;
        rt.offsetMin = new Vector2(0f, yOffset);
        rt.offsetMax = new Vector2(0f, yOffset);
    }

    private void FaceCamera()
    {
        if (_canvasRoot == null) return;
        var cam = Camera.main;
        if (cam == null) return;

        Transform c = cam.transform;
        _canvasRoot.transform.position = c.position + c.forward * 1.5f;
        _canvasRoot.transform.rotation = c.rotation;
    }
}
