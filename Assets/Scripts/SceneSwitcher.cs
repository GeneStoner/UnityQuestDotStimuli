// FILE: SceneSwitcher.cs
//
// Simple scene switcher for Quest. Add to any scene to enable switching.
// Hold RIGHT GRIP for 2 seconds to show menu, then use thumbstick to select.
//
// Controls:
//   Hold RIGHT GRIP (2 sec): Show scene menu
//   Thumbstick UP/DOWN: Select scene
//   TRIGGER: Load selected scene
//   Release GRIP: Cancel menu
//
using UnityEngine;
using UnityEngine.InputSystem;
using UnityEngine.SceneManagement;

public class SceneSwitcher : MonoBehaviour
{
    [Header("Settings")]
    [Tooltip("How long to hold grip to activate menu (seconds).")]
    public float gripHoldTime = 2.0f;

    [Tooltip("Scene names to switch between. Must match Build Settings.")]
    public string[] sceneNames = new string[] { "FlickerCalibration", "UpToDateScene" };

    [Tooltip("Display names for the menu.")]
    public string[] sceneDisplayNames = new string[] { "Flicker Calibration", "Dot Experiment" };

    [Header("XR Input")]
    public InputActionAsset xrInputActions;

    // Input actions
    private InputAction _gripRight;
    private InputAction _thumbstickRight;
    private InputAction _activateRight;

    // State
    private bool _menuVisible = false;
    private int _selectedIndex = 0;
    private float _gripHoldTimer = 0f;
    private bool _gripHeld = false;
    private float _lastThumbstickTime = 0f;
    private const float THUMBSTICK_COOLDOWN = 0.2f;
    private bool _triggerWasPressed = false;
    private float _sceneLoadTime = 0f;
    private const float STARTUP_DELAY = 5.0f;  // Don't activate for first 5 seconds

    void Awake()
    {
        _sceneLoadTime = Time.time;
        SetupInput();
    }

    void OnDestroy()
    {
        CleanupInput();
    }

    private void SetupInput()
    {
        if (xrInputActions == null)
        {
            Debug.Log("[SceneSwitcher] No XR Input Actions assigned. Keyboard only (Tab to toggle menu).");
            return;
        }

        // Right hand
        var rightMap = xrInputActions.FindActionMap("XRI Right", false);
        var rightInteractionMap = xrInputActions.FindActionMap("XRI Right Interaction", false);

        if (rightMap != null)
        {
            _thumbstickRight = rightMap.FindAction("Thumbstick", false);
            _thumbstickRight?.Enable();
        }

        if (rightInteractionMap != null)
        {
            _gripRight = rightInteractionMap.FindAction("Select", false); // Grip is "Select"
            _gripRight?.Enable();

            _activateRight = rightInteractionMap.FindAction("Activate", false); // Trigger
            _activateRight?.Enable();
        }

        if (_gripRight != null)
        {
            Debug.Log("[SceneSwitcher] Input initialized. Hold RIGHT GRIP (2 sec) to show scene menu.");
        }
        else
        {
            Debug.LogWarning("[SceneSwitcher] Could not find grip action. Use Tab key for menu.");
        }
    }

    private void CleanupInput()
    {
        _gripRight?.Disable();
        _thumbstickRight?.Disable();
        _activateRight?.Disable();
    }

    void Update()
    {
        // Don't do anything during startup delay
        if (Time.time - _sceneLoadTime < STARTUP_DELAY)
        {
            return;
        }

        bool rightGrip = _gripRight?.ReadValue<float>() > 0.5f;

        // Check for grip hold to show menu
        if (rightGrip)
        {
            if (!_gripHeld)
            {
                _gripHeld = true;
                _gripHoldTimer = 0f;
            }

            _gripHoldTimer += Time.deltaTime;

            if (_gripHoldTimer >= gripHoldTime && !_menuVisible)
            {
                ShowMenu();
            }
        }
        else
        {
            if (_gripHeld && _menuVisible)
            {
                // Released grip while menu visible - cancel if we haven't selected yet
                // Give a brief grace period after menu appears
                if (_gripHoldTimer < gripHoldTime + 0.5f)
                {
                    HideMenu();
                }
            }
            _gripHeld = false;
            _gripHoldTimer = 0f;
        }

        // Menu navigation
        if (_menuVisible)
        {
            HandleMenuInput();
        }

        // Keyboard fallback
        HandleKeyboardInput();
    }

    private void HandleMenuInput()
    {
        // Thumbstick navigation
        Vector2 thumbstick = _thumbstickRight?.ReadValue<Vector2>() ?? Vector2.zero;

        if (Mathf.Abs(thumbstick.y) > 0.5f && Time.time - _lastThumbstickTime > THUMBSTICK_COOLDOWN)
        {
            if (thumbstick.y > 0)
                _selectedIndex = Mathf.Max(0, _selectedIndex - 1);
            else
                _selectedIndex = Mathf.Min(sceneNames.Length - 1, _selectedIndex + 1);

            _lastThumbstickTime = Time.time;
        }

        // Trigger to select (with edge detection)
        bool triggerPressed = _activateRight?.ReadValue<float>() > 0.5f;
        if (triggerPressed && !_triggerWasPressed)
        {
            LoadSelectedScene();
        }
        _triggerWasPressed = triggerPressed;
    }

    private void HandleKeyboardInput()
    {
        // Tab to toggle menu
        if (Input.GetKeyDown(KeyCode.Tab))
        {
            if (_menuVisible)
                HideMenu();
            else
                ShowMenu();
        }

        if (_menuVisible)
        {
            // Arrow keys to navigate
            if (Input.GetKeyDown(KeyCode.UpArrow))
                _selectedIndex = Mathf.Max(0, _selectedIndex - 1);
            if (Input.GetKeyDown(KeyCode.DownArrow))
                _selectedIndex = Mathf.Min(sceneNames.Length - 1, _selectedIndex + 1);

            // Enter to select
            if (Input.GetKeyDown(KeyCode.Return))
                LoadSelectedScene();

            // Escape to cancel
            if (Input.GetKeyDown(KeyCode.Escape))
                HideMenu();
        }
    }

    private void ShowMenu()
    {
        _menuVisible = true;
        _selectedIndex = 0;

        // Find current scene in list
        string currentScene = SceneManager.GetActiveScene().name;
        for (int i = 0; i < sceneNames.Length; i++)
        {
            if (sceneNames[i] == currentScene)
            {
                _selectedIndex = i;
                break;
            }
        }

        Debug.Log("[SceneSwitcher] Menu opened.");
    }

    private void HideMenu()
    {
        _menuVisible = false;
        Debug.Log("[SceneSwitcher] Menu closed.");
    }

    private void LoadSelectedScene()
    {
        if (_selectedIndex < 0 || _selectedIndex >= sceneNames.Length) return;

        string sceneName = sceneNames[_selectedIndex];
        string currentScene = SceneManager.GetActiveScene().name;

        if (sceneName == currentScene)
        {
            Debug.Log($"[SceneSwitcher] Already in scene: {sceneName}");
            HideMenu();
            return;
        }

        Debug.Log($"[SceneSwitcher] >>> Loading scene via SceneSwitcher: {sceneName} <<<");
        SceneManager.LoadScene(sceneName);
    }

    void OnGUI()
    {
        // Always show grip hold progress when holding grip (before menu appears)
        if (_gripHeld && !_menuVisible && _gripHoldTimer > 0.1f)
        {
            float progress = Mathf.Clamp01(_gripHoldTimer / gripHoldTime);

            GUIStyle progressStyle = new GUIStyle(GUI.skin.label)
            {
                fontSize = 24,
                alignment = TextAnchor.MiddleCenter
            };
            progressStyle.normal.textColor = Color.white;

            float barWidth = 200f;
            float barHeight = 20f;
            float x = (Screen.width - barWidth) / 2f;
            float y = Screen.height - 100f;

            // Background
            GUI.color = new Color(0.2f, 0.2f, 0.2f, 0.8f);
            GUI.DrawTexture(new Rect(x, y, barWidth, barHeight), Texture2D.whiteTexture);

            // Progress fill
            GUI.color = new Color(0.3f, 0.7f, 0.3f, 1f);
            GUI.DrawTexture(new Rect(x, y, barWidth * progress, barHeight), Texture2D.whiteTexture);

            GUI.color = Color.white;
            GUI.Label(new Rect(x, y - 30, barWidth, 25), "Opening menu...", progressStyle);
        }

        if (!_menuVisible) return;

        // Semi-transparent background
        GUI.color = new Color(0, 0, 0, 0.85f);
        GUI.DrawTexture(new Rect(0, 0, Screen.width, Screen.height), Texture2D.whiteTexture);
        GUI.color = Color.white;

        // Menu styling
        GUIStyle titleStyle = new GUIStyle(GUI.skin.label)
        {
            fontSize = 36,
            fontStyle = FontStyle.Bold,
            alignment = TextAnchor.MiddleCenter
        };
        titleStyle.normal.textColor = Color.white;

        GUIStyle itemStyle = new GUIStyle(GUI.skin.label)
        {
            fontSize = 28,
            alignment = TextAnchor.MiddleCenter
        };

        GUIStyle selectedStyle = new GUIStyle(itemStyle);
        selectedStyle.normal.textColor = Color.green;
        selectedStyle.fontStyle = FontStyle.Bold;

        GUIStyle instructStyle = new GUIStyle(GUI.skin.label)
        {
            fontSize = 20,
            alignment = TextAnchor.MiddleCenter
        };
        instructStyle.normal.textColor = Color.gray;

        float centerX = Screen.width / 2f;
        float centerY = Screen.height / 2f;
        float itemHeight = 50f;

        // Title
        GUI.Label(new Rect(centerX - 200, centerY - 150, 400, 50), "SELECT SCENE", titleStyle);

        // Scene list
        for (int i = 0; i < sceneNames.Length; i++)
        {
            string displayName = (i < sceneDisplayNames.Length) ? sceneDisplayNames[i] : sceneNames[i];
            string currentMarker = (sceneNames[i] == SceneManager.GetActiveScene().name) ? " (current)" : "";

            float y = centerY - 50 + (i * itemHeight);
            GUIStyle style = (i == _selectedIndex) ? selectedStyle : itemStyle;
            style.normal.textColor = (i == _selectedIndex) ? Color.green : Color.white;

            string prefix = (i == _selectedIndex) ? "> " : "  ";
            GUI.Label(new Rect(centerX - 250, y, 500, itemHeight), prefix + displayName + currentMarker, style);
        }

        // Instructions
        float instrY = centerY + 100;
        GUI.Label(new Rect(centerX - 300, instrY, 600, 30), "Thumbstick: Navigate | Trigger: Select", instructStyle);
        GUI.Label(new Rect(centerX - 300, instrY + 30, 600, 30), "Release grip: Cancel", instructStyle);
    }
}
