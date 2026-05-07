using System.Collections.Generic;
using UnityEngine;
using UnityEngine.InputSystem;
using UnityEngine.UI;

/// <summary>
/// Runtime experiment asset selector. Shows a World Space Canvas menu before any session
/// starts, letting the experimenter pick which ExperimentSpec to run without rebuilding.
///
/// Setup:
///   1. Add this component to any GameObject in the scene.
///   2. Optionally assign 'runner' and 'xrInputActions' in Inspector — if left null,
///      they are auto-discovered at runtime.
///   3. Populate 'specs[]' with all ExperimentSpec assets you want in the menu.
///   4. Set runner.autoStartOnPlay = false (or leave it — Awake() forces it off).
///   5. On Quest: left or right thumbstick (up/down) to navigate, trigger to confirm.
///      On desktop: arrow keys / W-S to navigate, Enter/Space to confirm.
/// </summary>
[DefaultExecutionOrder(-100)]   // Awake() must run before TrialBlockRunner.Awake()
public class ExperimentSelector : MonoBehaviour
{
    [Header("References (auto-discovered if left null)")]
    public TrialBlockRunner runner;
    public InputActionAsset xrInputActions;

    [Header("Experiment specs (populate in Inspector)")]
    public ExperimentSpec[] specs;

    // ── Layout constants ──────────────────────────────────────────────────────
    private const float HUD_DIST       = 1.4f;    // metres in front of camera
    private const float CANVAS_PX_W    = 740f;
    private const float CANVAS_PX_H    = 560f;
    private const float WORLD_SCALE    = 0.001f;  // 1 px = 1 mm
    private const int   VISIBLE_ROWS   = 8;       // rows shown at once
    private const int   HEADER_FONT    = 24;
    private const int   ITEM_FONT      = 18;
    private const int   FOOTER_FONT    = 14;
    private const int   DIAG_FONT      = 12;
    private const float ROW_HEIGHT_PX  = 42f;

    // ── State ─────────────────────────────────────────────────────────────────
    private int  _selected  = 0;
    private int  _scrollTop = 0;
    private bool _launched  = false;

    // ── Input ─────────────────────────────────────────────────────────────────
    private InputAction _thumbLeft;
    private InputAction _thumbRight;
    private InputAction _triggerLeft;
    private InputAction _triggerRight;

    private float _thumbCooldown = 0f;
    private const float THUMB_REPEAT_DELAY = 0.4f;
    private const float THUMB_REPEAT_RATE  = 0.15f;
    private bool  _thumbHeld = false;

    // ── UI objects ────────────────────────────────────────────────────────────
    private GameObject _canvasRoot;
    private Text       _headerText;
    private Text[]     _rowTexts;
    private Text       _footerText;
    private Text       _diagText;     // on-screen diagnostics so we don't need logcat

    // ── Colours ───────────────────────────────────────────────────────────────
    private static readonly Color COL_SELECTED = new Color(1.0f, 0.85f, 0.1f);
    private static readonly Color COL_NORMAL   = new Color(0.88f, 0.88f, 0.88f);
    private static readonly Color COL_HEADER   = Color.white;
    private static readonly Color COL_FOOTER   = new Color(0.65f, 0.65f, 0.65f);
    private static readonly Color COL_DIAG_OK  = new Color(0.4f, 1.0f, 0.4f);
    private static readonly Color COL_DIAG_ERR = new Color(1.0f, 0.4f, 0.4f);
    private static readonly Color COL_BG       = new Color(0f, 0f, 0f, 0.80f);

    // ─────────────────────────────────────────────────────────────────────────

    void Awake()
    {
        // Auto-discover runner if not assigned in Inspector
        if (runner == null)
        {
            runner = FindObjectOfType<TrialBlockRunner>();
            if (runner != null)
                Debug.Log("[ExperimentSelector] Auto-found TrialBlockRunner: " + runner.name);
        }

        // Prevent auto-start before selection
        if (runner != null && runner.autoStartOnPlay)
        {
            runner.autoStartOnPlay = false;
            Debug.Log("[ExperimentSelector] Disabled runner.autoStartOnPlay.");
        }

        // Auto-discover InputActionAsset from runner if not assigned
        if (xrInputActions == null && runner != null)
        {
            // Try to get it from the runner's serialized field via reflection (safe fallback)
            var field = typeof(TrialBlockRunner).GetField("xrInputActions",
                System.Reflection.BindingFlags.Public | System.Reflection.BindingFlags.Instance);
            if (field != null)
                xrInputActions = field.GetValue(runner) as InputActionAsset;

            if (xrInputActions != null)
                Debug.Log("[ExperimentSelector] Auto-found InputActionAsset from runner.");
        }
    }

    void Start()
    {
        // If no specs provided, skip menu and launch immediately
        if (specs == null || specs.Length == 0)
        {
            Debug.LogWarning("[ExperimentSelector] No specs assigned — launching immediately.");
            Launch();
            return;
        }

        _selected  = 0;
        _scrollTop = 0;

        BuildUI();
        BindInput();
        Refresh();
    }

    void OnDestroy() => UnbindInput();

    // ── Update: navigate and confirm ──────────────────────────────────────────

    void Update()
    {
        if (_launched) return;
        if (_canvasRoot == null || !_canvasRoot.activeSelf) return;

        int delta = 0;

        // Keyboard fallback
        if (Input.GetKeyDown(KeyCode.UpArrow) || Input.GetKeyDown(KeyCode.W))
            delta = -1;
        else if (Input.GetKeyDown(KeyCode.DownArrow) || Input.GetKeyDown(KeyCode.S))
            delta = 1;

        if (Input.GetKeyDown(KeyCode.Return) || Input.GetKeyDown(KeyCode.Space))
            Confirm();

        // Thumbstick with auto-repeat
        Vector2 thumb = GetThumbstick();
        if (Mathf.Abs(thumb.y) > 0.5f)
        {
            if (!_thumbHeld)
            {
                delta          = thumb.y > 0 ? -1 : 1;
                _thumbHeld     = true;
                _thumbCooldown = THUMB_REPEAT_DELAY;
            }
            else
            {
                _thumbCooldown -= Time.deltaTime;
                if (_thumbCooldown <= 0f)
                {
                    delta          = thumb.y > 0 ? -1 : 1;
                    _thumbCooldown = THUMB_REPEAT_RATE;
                }
            }
        }
        else
        {
            _thumbHeld     = false;
            _thumbCooldown = 0f;
        }

        if (delta != 0)
        {
            _selected = Mathf.Clamp(_selected + delta, 0, specs.Length - 1);
            if (_selected < _scrollTop)
                _scrollTop = _selected;
            else if (_selected >= _scrollTop + VISIBLE_ROWS)
                _scrollTop = _selected - VISIBLE_ROWS + 1;
            Refresh();
        }
    }

    // ── Build World Space Canvas ──────────────────────────────────────────────

    void BuildUI()
    {
        // Find camera robustly — Camera.main may be null in XR rigs
        Camera cam = Camera.main;
        if (cam == null) cam = FindObjectOfType<Camera>();
        Transform camT = (cam != null) ? cam.transform : transform;

        _canvasRoot = new GameObject("ExperimentSelector_Canvas");
        _canvasRoot.transform.SetParent(camT, worldPositionStays: false);
        _canvasRoot.transform.localPosition = new Vector3(0f, 0f, HUD_DIST);
        _canvasRoot.transform.localRotation = Quaternion.identity;
        _canvasRoot.transform.localScale    = Vector3.one * WORLD_SCALE;

        var canvas = _canvasRoot.AddComponent<Canvas>();
        canvas.renderMode   = RenderMode.WorldSpace;
        canvas.sortingOrder = 200;

        var rt = _canvasRoot.GetComponent<RectTransform>();
        rt.sizeDelta = new Vector2(CANVAS_PX_W, CANVAS_PX_H);

        // Background panel
        MakeImage(_canvasRoot, "BG", Vector2.zero, Vector2.one, Vector2.zero, Vector2.zero, COL_BG);

        float contentH = CANVAS_PX_H - 20f;
        float headerH  = 50f;
        float footerH  = 30f;
        float diagH    = 60f;
        float listH    = contentH - headerH - footerH - diagH - 20f;

        // Header
        _headerText = MakeText(_canvasRoot, "Header",
            new Vector2(0f, 0f), new Vector2(1f, 1f),
            new Vector2(10f, contentH - headerH),
            new Vector2(-10f, -(CANVAS_PX_H - headerH - 10f)),
            HEADER_FONT, FontStyle.Bold, COL_HEADER, TextAnchor.MiddleCenter);

        // List rows
        _rowTexts = new Text[VISIBLE_ROWS];
        float rowTop = contentH - headerH - 8f;
        for (int i = 0; i < VISIBLE_ROWS; i++)
        {
            float yMin = rowTop - (i + 1) * ROW_HEIGHT_PX;
            float yMax = rowTop - i * ROW_HEIGHT_PX;
            _rowTexts[i] = MakeText(_canvasRoot, $"Row{i}",
                new Vector2(0f, 0f), new Vector2(1f, 1f),
                new Vector2(20f, yMin),
                new Vector2(-20f, -CANVAS_PX_H + yMax),
                ITEM_FONT, FontStyle.Normal, COL_NORMAL, TextAnchor.MiddleLeft);
        }

        // Footer (navigation hints)
        _footerText = MakeText(_canvasRoot, "Footer",
            new Vector2(0f, 0f), new Vector2(1f, 1f),
            new Vector2(10f, diagH + 4f),
            new Vector2(-10f, -(CANVAS_PX_H - footerH - diagH)),
            FOOTER_FONT, FontStyle.Normal, COL_FOOTER, TextAnchor.MiddleCenter);

        // Diagnostics band at the very bottom
        _diagText = MakeText(_canvasRoot, "Diag",
            new Vector2(0f, 0f), new Vector2(1f, 1f),
            new Vector2(10f, 4f),
            new Vector2(-10f, -(CANVAS_PX_H - diagH)),
            DIAG_FONT, FontStyle.Normal, COL_DIAG_OK, TextAnchor.UpperLeft);

        RefreshDiag();
    }

    // Populate the diagnostics line so we can see in the headset what was found
    void RefreshDiag()
    {
        if (_diagText == null) return;

        bool runnerOk  = runner != null;
        bool inputOk   = xrInputActions != null;
        bool thumbLOk  = _thumbLeft  != null;
        bool thumbROk  = _thumbRight != null;
        bool trigLOk   = _triggerLeft  != null;
        bool trigROk   = _triggerRight != null;

        string line1 = $"runner:{YN(runnerOk)}  xrActions:{YN(inputOk)}  specs:{(specs != null ? specs.Length : 0)}";
        string line2 = $"thumbL:{YN(thumbLOk)} thumbR:{YN(thumbROk)} trigL:{YN(trigLOk)} trigR:{YN(trigROk)}";

        _diagText.text  = line1 + "\n" + line2;
        _diagText.color = (runnerOk && (thumbLOk || thumbROk || trigLOk || trigROk))
            ? COL_DIAG_OK : COL_DIAG_ERR;
    }

    static string YN(bool v) => v ? "Y" : "N";

    void Refresh()
    {
        if (_headerText == null) return;

        _headerText.text = $"Select Experiment  ({_selected + 1} / {specs.Length})";

        for (int i = 0; i < VISIBLE_ROWS; i++)
        {
            int idx = _scrollTop + i;
            if (_rowTexts[i] == null) continue;

            if (idx >= specs.Length)
            {
                _rowTexts[i].text  = "";
                _rowTexts[i].color = COL_NORMAL;
                continue;
            }

            var s = specs[idx];
            string label = (s != null) ? (s.experimentName ?? s.name) : "(null)";

            if (s is ExpSpecTestPhase ep && ep.useQuestAdaptive)
                label += "  [QUEST]";

            bool isSel = (idx == _selected);
            _rowTexts[i].text      = isSel ? $"▶  {label}" : $"    {label}";
            _rowTexts[i].color     = isSel ? COL_SELECTED : COL_NORMAL;
            _rowTexts[i].fontStyle = isSel ? FontStyle.Bold : FontStyle.Normal;
        }

        bool canUp   = _scrollTop > 0;
        bool canDown = (_scrollTop + VISIBLE_ROWS) < specs.Length;
        string arrows = (canUp ? "▲  " : "      ")
            + "thumbstick: navigate  |  trigger: confirm"
            + (canDown ? "  ▼" : "");
        if (_footerText != null) _footerText.text = arrows;
    }

    // ── Confirm selection ─────────────────────────────────────────────────────

    void Confirm()
    {
        if (_launched) return;
        if (specs == null || _selected >= specs.Length || specs[_selected] == null)
        {
            Debug.LogWarning("[ExperimentSelector] Selection invalid.");
            return;
        }

        var chosen = specs[_selected];
        Debug.Log($"[ExperimentSelector] Selected: {chosen.experimentName ?? chosen.name}");

        if (_canvasRoot != null) _canvasRoot.SetActive(false);
        Launch(chosen);
    }

    void Launch(ExperimentSpec chosenSpec = null)
    {
        _launched = true;

        if (runner == null)
        {
            Debug.LogError("[ExperimentSelector] runner not found — cannot launch.");
            return;
        }
        if (chosenSpec != null)
            runner.spec = chosenSpec;

        runner.BeginBlock();
        UnbindInput();
    }

    // ── Input binding ─────────────────────────────────────────────────────────

    void BindInput()
    {
        if (xrInputActions == null)
        {
            Debug.LogWarning("[ExperimentSelector] xrInputActions not found — XR input disabled; use keyboard (↑↓ / Enter).");
            RefreshDiag();
            return;
        }

        // Thumbstick is in "XRI Left" / "XRI Right" (movement maps).
        // Activate (trigger) is in "XRI Left Interaction" / "XRI Right Interaction".
        var leftMov  = xrInputActions.FindActionMap("XRI Left",              throwIfNotFound: false);
        var rightMov = xrInputActions.FindActionMap("XRI Right",             throwIfNotFound: false);
        var leftInt  = xrInputActions.FindActionMap("XRI Left Interaction",  throwIfNotFound: false);
        var rightInt = xrInputActions.FindActionMap("XRI Right Interaction", throwIfNotFound: false);

        leftMov?.Enable();
        rightMov?.Enable();
        leftInt?.Enable();
        rightInt?.Enable();

        _thumbLeft    = leftMov?.FindAction("Thumbstick", throwIfNotFound: false);
        _thumbRight   = rightMov?.FindAction("Thumbstick", throwIfNotFound: false);
        _triggerLeft  = leftInt?.FindAction("Activate",   throwIfNotFound: false);
        _triggerRight = rightInt?.FindAction("Activate",  throwIfNotFound: false);

        _thumbLeft?.Enable();
        _thumbRight?.Enable();

        if (_triggerLeft  != null) { _triggerLeft.Enable();  _triggerLeft.performed  += OnTrigger; }
        if (_triggerRight != null) { _triggerRight.Enable(); _triggerRight.performed += OnTrigger; }

        Debug.Log($"[ExperimentSelector] Input bound — " +
                  $"leftMov={leftMov != null} rightMov={rightMov != null} " +
                  $"leftInt={leftInt != null} rightInt={rightInt != null} | " +
                  $"thumbL={_thumbLeft != null} thumbR={_thumbRight != null} " +
                  $"trigL={_triggerLeft != null} trigR={_triggerRight != null}");

        // Last-resort: enable entire asset and use qualified path lookup
        if (_thumbLeft == null && _thumbRight == null && _triggerLeft == null && _triggerRight == null)
        {
            Debug.LogWarning("[ExperimentSelector] No actions found — enabling entire asset, retrying with path lookup.");
            xrInputActions.Enable();
            _thumbLeft    = xrInputActions.FindAction("XRI Left/Thumbstick",            false);
            _thumbRight   = xrInputActions.FindAction("XRI Right/Thumbstick",           false);
            _triggerLeft  = xrInputActions.FindAction("XRI Left Interaction/Activate",  false);
            _triggerRight = xrInputActions.FindAction("XRI Right Interaction/Activate", false);
            _thumbLeft?.Enable();  _thumbRight?.Enable();
            if (_triggerLeft  != null) { _triggerLeft.Enable();  _triggerLeft.performed  += OnTrigger; }
            if (_triggerRight != null) { _triggerRight.Enable(); _triggerRight.performed += OnTrigger; }
            Debug.Log($"[ExperimentSelector] Retry — thumbL={_thumbLeft != null} thumbR={_thumbRight != null} " +
                      $"trigL={_triggerLeft != null} trigR={_triggerRight != null}");
        }

        RefreshDiag();
    }

    void UnbindInput()
    {
        // Only remove callbacks — NEVER call Disable() on any of these actions.
        // TrialBlockRunner subscribes to Activate, TargetResponseController subscribes
        // to Thumbstick (same action objects). Disabling here would kill their input.
        if (_triggerLeft  != null) _triggerLeft.performed  -= OnTrigger;
        if (_triggerRight != null) _triggerRight.performed -= OnTrigger;
        _thumbLeft = _thumbRight = _triggerLeft = _triggerRight = null;
    }

    void OnTrigger(InputAction.CallbackContext ctx) => Confirm();

    Vector2 GetThumbstick()
    {
        Vector2 l = _thumbLeft  != null ? _thumbLeft.ReadValue<Vector2>()  : Vector2.zero;
        Vector2 r = _thumbRight != null ? _thumbRight.ReadValue<Vector2>() : Vector2.zero;
        return (l.sqrMagnitude >= r.sqrMagnitude) ? l : r;
    }

    // ── UI helpers ────────────────────────────────────────────────────────────

    static Text MakeText(GameObject parent, string goName,
                         Vector2 anchorMin, Vector2 anchorMax,
                         Vector2 offsetMin, Vector2 offsetMax,
                         int fontSize, FontStyle style, Color color, TextAnchor align)
    {
        var go = new GameObject(goName);
        go.transform.SetParent(parent.transform, worldPositionStays: false);
        var rt = go.AddComponent<RectTransform>();
        rt.anchorMin = anchorMin;
        rt.anchorMax = anchorMax;
        rt.offsetMin = offsetMin;
        rt.offsetMax = offsetMax;
        var t = go.AddComponent<Text>();
        t.font               = Resources.GetBuiltinResource<Font>("LegacyRuntime.ttf");
        t.fontSize           = fontSize;
        t.fontStyle          = style;
        t.color              = color;
        t.alignment          = align;
        t.supportRichText    = false;
        t.horizontalOverflow = HorizontalWrapMode.Overflow;
        t.verticalOverflow   = VerticalWrapMode.Overflow;
        return t;
    }

    static void MakeImage(GameObject parent, string goName,
                          Vector2 anchorMin, Vector2 anchorMax,
                          Vector2 offsetMin, Vector2 offsetMax, Color color)
    {
        var go = new GameObject(goName);
        go.transform.SetParent(parent.transform, worldPositionStays: false);
        var rt = go.AddComponent<RectTransform>();
        rt.anchorMin = anchorMin;
        rt.anchorMax = anchorMax;
        rt.offsetMin = offsetMin;
        rt.offsetMax = offsetMax;
        go.AddComponent<Image>().color = color;
    }
}
