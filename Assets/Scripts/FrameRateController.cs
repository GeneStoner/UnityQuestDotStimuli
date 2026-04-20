using UnityEngine;
using Unity.XR.Oculus;

public class FrameRateController : MonoBehaviour
{
    [Tooltip("Target display refresh rate (Hz). Quest 3 supports 72, 90, 120.")]
    public int targetFPS = 90;

    // For monitoring
    private float _frameCount = 0f;
    private float _timeElapsed = 0f;

    void Awake()
    {
        // Lock CPU and GPU to sustained high to prevent thermal throttling mid-session.
        Performance.TrySetCPULevel(4);
        Performance.TrySetGPULevel(4);

        // Set display refresh rate via Oculus API (authoritative for Quest hardware).
        // Application.targetFrameRate is set as a fallback for non-Quest platforms.
        bool rateSet = Performance.TrySetDisplayRefreshRate(targetFPS);
        QualitySettings.vSyncCount = 0;
        Application.targetFrameRate = targetFPS;

        if (Performance.TryGetDisplayRefreshRate(out float actualRate))
            Debug.Log($"[FrameRateController] Display refresh rate = {actualRate} Hz (requested {targetFPS}, set={rateSet})");
        else
            Debug.Log($"[FrameRateController] targetFrameRate = {Application.targetFrameRate} (OVR rate query unavailable)");
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