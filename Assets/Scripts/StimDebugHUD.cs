using UnityEngine;
using UnityEngine.UI;

[DisallowMultipleComponent]
public class StimDebugHUD : MonoBehaviour
{
    public TrialBlockRunner runner;
    public Text uiText; // optional, if using uGUI

    public void Bind(TrialBlockRunner r)
    {
        runner = r;
    }

    void OnGUI()
    {
        if (runner == null) return;
        var t = runner.CurrentTrial;

        string msg = $"Trial {runner.TrialIndex + 1} / {runner.TrialsCount}\n";
        msg += $"Cond: {t.conditionID}\n";
        msg += $"Heading: {t.headingDeg:F1} deg\n";
        msg += $"Frame: {runner.FrameInTrial} / {t.totalFrames}\n";
        msg += $"Trans: {t.translationStartFrame}-{t.translationEndFrame}\n";
        msg += $"simHz: {runner.SimHz:F1}";

        // Draw simple overlay
        GUI.Label(new Rect(10, 10, 400, 120), msg);

        if (uiText != null)
            uiText.text = msg;
    }

    public void Tick() { /* called by runner.Update; no-op for now */ }
}