// FILE: FlickerCalibrationUI.cs
//
// World Space UI for FlickerCalibrator that works in VR.
// Creates a Canvas with TextMeshPro at runtime, positioned in front of camera.
//
using UnityEngine;
using TMPro;

public class FlickerCalibrationUI : MonoBehaviour
{
    [Header("References")]
    public FlickerCalibrator calibrator;
    public Transform cameraTransform;  // Usually the main camera or XR camera

    [Header("UI Settings")]
    public float distanceFromCamera = 2.0f;
    public float verticalOffset = 0.4f;  // How far above center to place UI (in meters)
    public float canvasWidth = 1.0f;
    public float canvasHeight = 0.4f;
    public float fontSize = 0.05f;
    public Color textColor = Color.white;
    public Color highlightColor = Color.green;

    // Runtime created objects
    private Canvas _canvas;
    private TextMeshProUGUI _textDisplay;
    private RectTransform _canvasRect;

    void Start()
    {
        // Find camera if not assigned
        if (cameraTransform == null)
        {
            Camera cam = Camera.main;
            if (cam != null)
                cameraTransform = cam.transform;
        }

        // Find calibrator if not assigned
        if (calibrator == null)
            calibrator = FindObjectOfType<FlickerCalibrator>();

        if (calibrator == null)
        {
            Debug.LogError("[FlickerCalibrationUI] No FlickerCalibrator found!");
            enabled = false;
            return;
        }

        CreateWorldSpaceUI();
    }

    void CreateWorldSpaceUI()
    {
        // Create Canvas GameObject
        GameObject canvasGO = new GameObject("FlickerCalibrationCanvas");
        canvasGO.transform.SetParent(transform);

        _canvas = canvasGO.AddComponent<Canvas>();
        _canvas.renderMode = RenderMode.WorldSpace;

        // Add CanvasScaler for consistent sizing
        var scaler = canvasGO.AddComponent<UnityEngine.UI.CanvasScaler>();
        scaler.dynamicPixelsPerUnit = 100;

        // Setup RectTransform
        _canvasRect = canvasGO.GetComponent<RectTransform>();
        _canvasRect.sizeDelta = new Vector2(canvasWidth * 1000, canvasHeight * 1000);  // In canvas units
        _canvasRect.localScale = new Vector3(0.001f, 0.001f, 0.001f);  // Scale down to world units

        // Create background panel (semi-transparent)
        GameObject bgGO = new GameObject("Background");
        bgGO.transform.SetParent(canvasGO.transform, false);
        var bgRect = bgGO.AddComponent<RectTransform>();
        bgRect.anchorMin = Vector2.zero;
        bgRect.anchorMax = Vector2.one;
        bgRect.offsetMin = Vector2.zero;
        bgRect.offsetMax = Vector2.zero;
        var bgImage = bgGO.AddComponent<UnityEngine.UI.Image>();
        bgImage.color = new Color(0, 0, 0, 0.7f);

        // Create TextMeshPro text
        GameObject textGO = new GameObject("Text");
        textGO.transform.SetParent(canvasGO.transform, false);
        var textRect = textGO.AddComponent<RectTransform>();
        textRect.anchorMin = new Vector2(0.05f, 0.05f);
        textRect.anchorMax = new Vector2(0.95f, 0.95f);
        textRect.offsetMin = Vector2.zero;
        textRect.offsetMax = Vector2.zero;

        _textDisplay = textGO.AddComponent<TextMeshProUGUI>();
        _textDisplay.fontSize = fontSize * 1000;  // Scale for canvas
        _textDisplay.color = textColor;
        _textDisplay.alignment = TextAlignmentOptions.TopLeft;
        _textDisplay.enableWordWrapping = true;
        _textDisplay.text = "Initializing...";

        Debug.Log("[FlickerCalibrationUI] World Space UI created.");
    }

    void LateUpdate()
    {
        if (_canvas == null || calibrator == null) return;

        var state = calibrator.GetState();

        // Hide UI during trials (Adjusting=1, BetweenTrials=2)
        bool shouldShow = (state == 0 || state == 3);  // WaitingToStart or AllDone
        _canvas.gameObject.SetActive(shouldShow);

        if (!shouldShow) return;

        // Position canvas in front of camera, ABOVE center
        if (cameraTransform != null)
        {
            Vector3 forward = cameraTransform.forward;
            Vector3 targetPos = cameraTransform.position + forward * distanceFromCamera;
            targetPos += Vector3.up * verticalOffset;  // Move above stimulus
            _canvasRect.position = targetPos;
            _canvasRect.rotation = Quaternion.LookRotation(_canvasRect.position - cameraTransform.position);
        }

        // Update text based on calibrator state
        UpdateDisplayText();
    }

    void UpdateDisplayText()
    {
        if (_textDisplay == null) return;

        string text = "";
        var state = calibrator.GetState();
        int totalTrials = calibrator.GetTotalTrials();

        switch (state)
        {
            case 0:  // WaitingToStart
                text += "<size=120%><b>FLICKER FUSION CALIBRATION</b></size>\n\n";
                text += $"{totalTrials} trials\n\n";
                text += "Thumbstick UP/DOWN: Adjust green\n";
                text += "TRIGGER: Confirm each trial\n\n";
                text += "<color=#00FF00>Press TRIGGER to begin</color>";
                break;

            case 3:  // AllDone
                var results = calibrator.GetResults();
                int trialCount = calibrator.GetCurrentTrial();
                text += "<size=120%><b>CALIBRATION COMPLETE</b></size>\n\n";
                text += $"Trials: {trialCount}\n";
                text += $"<color=#00FF00>Mean:   {results.mean:F4}</color>\n";
                text += $"<color=#00FF00>Median: {results.median:F4}</color>\n";
                text += $"Std Dev: {results.stdDev:F4}\n\n";

                if (calibrator.IsMenuReady())
                {
                    int selection = calibrator.GetMenuSelection();
                    string[] items = { "Start Main Experiment", "Redo Calibration", "Quit" };
                    for (int i = 0; i < items.Length; i++)
                    {
                        if (i == selection)
                            text += $"<color=#00FF00>> {items[i]}</color>\n";
                        else
                            text += $"  {items[i]}\n";
                    }
                    text += "\n<color=#AAAAAA>Thumbstick: Select | Trigger: Confirm</color>";
                }
                else
                {
                    text += "<color=#AAAAAA>Loading menu...</color>";
                }
                break;
        }

        _textDisplay.text = text;
    }

    void OnDestroy()
    {
        if (_canvas != null)
            Destroy(_canvas.gameObject);
    }
}
