using System.Text;
using UnityEngine;
using Unity.XR.Oculus;

/// <summary>
/// Requests the display refresh rate and verifies it took effect.
///
/// The request used to be made once in Awake(), which can run before the XR
/// display is ready: it then failed silently and the headset stayed at its
/// default rate (72 Hz on Quest). We now retry for a few seconds and log the
/// rate actually in force. CsvLogger writes it to the sidecar's display block.
/// </summary>
public class FrameRateController : MonoBehaviour
{
    [Tooltip("Target display refresh rate (Hz). Quest 3 supports 72, 80, 90, 120.")]
    public int targetFPS = 90;

    [Tooltip("How long to keep retrying the request after startup (seconds).")]
    public float retryWindowSeconds = 10f;

    [Tooltip("Keep re-requesting whenever the display drifts off the target rate.")]
    public bool enforceThroughoutSession = true;

    /// <summary>Rate the display reports now, or NaN if unavailable.</summary>
    public static float ActualRefreshRateHz { get; private set; } = float.NaN;

    /// <summary>True once the display reports the requested rate.</summary>
    public static bool RefreshRateConfirmed { get; private set; }

    private float _frameCount;
    private float _timeElapsed;
    private float _retryDeadline;
    private float _nextRetry;
    private int _reassertCount;

    void Awake()
    {
        // Lock CPU and GPU to sustained high to prevent thermal throttling mid-session.
        Performance.TrySetCPULevel(4);
        Performance.TrySetGPULevel(4);

        QualitySettings.vSyncCount = 0;
        Application.targetFrameRate = targetFPS;   // fallback for non-Quest platforms

        _retryDeadline = Time.unscaledTime + retryWindowSeconds;
        LogAvailableRates();
        TryApply("Awake");
    }

    void Update()
    {
        // Keep asking until the display agrees, or the retry window closes
        if (!RefreshRateConfirmed && Time.unscaledTime < _retryDeadline && Time.unscaledTime >= _nextRetry)
        {
            _nextRetry = Time.unscaledTime + 0.5f;
            TryApply("retry");
        }

        // The runtime can accept 90 Hz at startup and then drop back to the
        // headset default a second later (seen on Quest 3, Horizon OS). One
        // request is therefore not enough: re-assert whenever it drifts off.
        if (enforceThroughoutSession && Time.unscaledTime >= _nextRetry
            && Performance.TryGetDisplayRefreshRate(out float rateNow)
            && Mathf.Abs(rateNow - targetFPS) > 0.5f)
        {
            _nextRetry = Time.unscaledTime + 1f;
            _reassertCount++;
            RefreshRateConfirmed = false;
            TryApply($"re-assert #{_reassertCount}");
        }

        _frameCount += 1f;
        _timeElapsed += Time.unscaledDeltaTime;

        if (_timeElapsed >= 1f)
        {
            float fps = _frameCount / _timeElapsed;
            if (Performance.TryGetDisplayRefreshRate(out float now)) ActualRefreshRateHz = now;

            // A measured rate below the display rate means dropped frames: the sim
            // advances on a time accumulator, so simulated frames go undisplayed.
            string warn = (!float.IsNaN(ActualRefreshRateHz) && fps < ActualRefreshRateHz - 3f)
                ? "  DROPPING FRAMES" : "";
            Debug.Log($"[FrameRateController] Measured FPS = {fps:F1}; display = {ActualRefreshRateHz:F1} Hz{warn}");

            _frameCount = 0f;
            _timeElapsed = 0f;
        }
    }

    private void TryApply(string why)
    {
        bool requested = Performance.TrySetDisplayRefreshRate(targetFPS);

        if (Performance.TryGetDisplayRefreshRate(out float actual))
        {
            ActualRefreshRateHz = actual;
            RefreshRateConfirmed = Mathf.Abs(actual - targetFPS) < 0.5f;
            Debug.Log($"[FrameRateController] {why}: display = {actual} Hz " +
                      $"(requested {targetFPS}, accepted={requested}, confirmed={RefreshRateConfirmed})");
            if (!RefreshRateConfirmed && Time.unscaledTime >= _retryDeadline)
                Debug.LogWarning($"[FrameRateController] Display stayed at {actual} Hz, not {targetFPS} Hz. " +
                                 "Frame-count durations in the data assume the spec's simHz.");
        }
        else
        {
            Debug.Log($"[FrameRateController] {why}: rate query unavailable " +
                      $"(targetFrameRate = {Application.targetFrameRate})");
        }
    }

    private static void LogAvailableRates()
    {
        float[] rates;
        if (!Performance.TryGetAvailableDisplayRefreshRates(out rates) || rates == null) return;

        var sb = new StringBuilder();
        for (int i = 0; i < rates.Length; i++)
        {
            if (i > 0) sb.Append(", ");
            sb.Append(rates[i].ToString("0.#"));
        }
        Debug.Log($"[FrameRateController] Available refresh rates: {sb}");
    }
}
