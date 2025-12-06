using UnityEngine;

public class FrameRateController : MonoBehaviour
{
    [Tooltip("Target frame rate (fps). Use 0 or -1 to remove cap.")]
    public int targetFPS = 60;

    // For monitoring
    private float _frameCount = 0f;
    private float _timeElapsed = 0f;

    void Awake()
    {
        // Disable VSync so targetFrameRate takes effect
        QualitySettings.vSyncCount = 0;
        Application.targetFrameRate = targetFPS > 0 ? targetFPS : -1;

        Debug.Log($"[FrameRateController] targetFrameRate = {Application.targetFrameRate}");
    }

    void Update()
    {
        _frameCount += 1f;
        _timeElapsed += Time.unscaledDeltaTime;

        // Every second, log the measured frame rate and reset counters
        if (_timeElapsed >= 1f)
        {
            float fps = _frameCount / _timeElapsed;
            Debug.Log($"[FrameRateController] Measured FPS = {fps:F1}");
            _frameCount = 0f;
            _timeElapsed = 0f;
        }
    }
}