using System.Collections.Generic;
using UnityEngine;

/// <summary>
/// QUEST Bayesian adaptive psychophysical staircase.
/// Watson & Pelli (1983), Perception & Psychophysics 33(2), 113-120.
///
/// Works in log10 space. Call NextLog() to get the suggested stimulus level
/// for the next trial, then Update(levelLog, correct) after the response.
///
/// Designed for duration thresholds but works for any log-scaled parameter.
/// </summary>
public class QuestStaircase
{
    // ── Public estimates (updated after every trial) ──────────────────────────
    public float MeanLog   { get; private set; }          // posterior mean  (log10 units)
    public float ModeLog   { get; private set; }          // posterior mode  (log10 units)
    public float SdLog     { get; private set; }          // posterior SD    (log10 units)
    public float MeanLinear => Mathf.Pow(10f, MeanLog);  // posterior mean  (linear units)
    public int   TrialCount { get; private set; }

    // ── Psychometric parameters ───────────────────────────────────────────────
    private readonly float _beta;     // slope of Weibull (>0; typically 1.5–3.5)
    private readonly float _delta;    // lapse rate (fraction of random responses; ~0.01–0.05)
    private readonly float _gamma;    // guessing rate (1/k for k-AFC; 1/8 for 8AFC)

    // ── Stimulus range ────────────────────────────────────────────────────────
    private readonly float _xMinLog;
    private readonly float _xMaxLog;

    // ── Grid and log-posterior ────────────────────────────────────────────────
    private readonly float[] _tGrid;    // candidate threshold values (log10 units)
    private readonly float[] _logPdf;   // unnormalised log-posterior
    private readonly int     _nGrid;

    // ── Trial history ─────────────────────────────────────────────────────────
    public List<float> LevelsUsedLog { get; } = new List<float>();
    public List<bool>  Responses     { get; } = new List<bool>();

    // ── Constructor ───────────────────────────────────────────────────────────

    /// <param name="tGuessLog">Prior mean threshold in log10 units (e.g. log10(80) ≈ 1.90).</param>
    /// <param name="tGuessSd"> Prior SD in log10 units (e.g. 0.4 ≈ factor-of-2.5 uncertainty).</param>
    /// <param name="beta">     Weibull slope (default 2.0).</param>
    /// <param name="delta">    Lapse rate (default 0.02).</param>
    /// <param name="gamma">    Guessing rate: 1/8 for 8AFC (default 0.125).</param>
    /// <param name="xMinLog">  Minimum testable level in log10 units (default log10(15) ≈ 1.18).</param>
    /// <param name="xMaxLog">  Maximum testable level in log10 units (default log10(400) ≈ 2.60).</param>
    /// <param name="nGrid">    Grid resolution (default 200).</param>
    public QuestStaircase(
        float tGuessLog,
        float tGuessSd,
        float beta    = 2.0f,
        float delta   = 0.02f,
        float gamma   = 0.125f,
        float xMinLog = 1.176f,   // log10(15 ms)
        float xMaxLog = 2.602f,   // log10(400 ms)
        int   nGrid   = 200)
    {
        _beta    = beta;
        _delta   = delta;
        _gamma   = gamma;
        _xMinLog = xMinLog;
        _xMaxLog = xMaxLog;
        _nGrid   = nGrid;

        // Build evenly-spaced threshold grid in log10 space
        _tGrid  = new float[_nGrid];
        _logPdf = new float[_nGrid];

        for (int i = 0; i < _nGrid; i++)
        {
            _tGrid[i]  = xMinLog + (xMaxLog - xMinLog) * i / (_nGrid - 1);
            // Gaussian prior: log p(T) = -0.5 * ((T - tGuessLog) / tGuessSd)^2
            float d     = (_tGrid[i] - tGuessLog) / tGuessSd;
            _logPdf[i] = -0.5f * d * d;
        }

        Recompute();
    }

    // ── API ───────────────────────────────────────────────────────────────────

    /// <summary>
    /// Suggested stimulus level for the next trial (posterior mean, clamped to range).
    /// Returns log10 units.
    /// </summary>
    public float NextLog() => Mathf.Clamp(MeanLog, _xMinLog, _xMaxLog);

    /// <summary>Suggested stimulus level in linear units (e.g. milliseconds).</summary>
    public float NextLinear() => Mathf.Pow(10f, NextLog());

    /// <summary>
    /// Update the posterior after one trial.
    /// </summary>
    /// <param name="levelLog">Stimulus level actually used, in log10 units.</param>
    /// <param name="correct"> Whether the observer responded correctly.</param>
    public void Update(float levelLog, bool correct)
    {
        TrialCount++;
        LevelsUsedLog.Add(levelLog);
        Responses.Add(correct);

        // Bayesian update: for each candidate threshold T, compute log-likelihood
        // of this response given the psychometric function, then add to log-pdf.
        for (int i = 0; i < _nGrid; i++)
        {
            float p    = Psychometric(levelLog, _tGrid[i]);
            // Guard against log(0) with small epsilon
            float logL = correct
                ? Mathf.Log(Mathf.Max(p,        1e-6f))
                : Mathf.Log(Mathf.Max(1f - p,   1e-6f));
            _logPdf[i] += logL;
        }

        Recompute();
    }

    // ── Internals ─────────────────────────────────────────────────────────────

    /// <summary>
    /// Weibull psychometric function.
    /// P(correct | stimulus=x, threshold=T) in log10 space.
    /// </summary>
    private float Psychometric(float x, float T)
    {
        // Weibull CDF on log axis:
        // P = gamma + (1 - gamma - delta) * (1 - exp(-10^(beta*(x - T))))
        float exponent = _beta * (x - T);
        // Clamp exponent to avoid overflow in Pow
        exponent = Mathf.Clamp(exponent, -10f, 6f);
        float weibull = 1f - Mathf.Exp(-Mathf.Pow(10f, exponent));
        return _gamma + (1f - _gamma - _delta) * weibull;
    }

    /// <summary>Recompute posterior moments from the current log-pdf.</summary>
    private void Recompute()
    {
        // Numerically stable normalisation: shift by max before exponentiating
        float maxLog = _logPdf[0];
        for (int i = 1; i < _nGrid; i++)
            if (_logPdf[i] > maxLog) maxLog = _logPdf[i];

        // Convert to normalised pdf
        float sum     = 0f;
        float modeVal = -1f;
        int   modeIdx = 0;

        float[] pdf = new float[_nGrid];
        for (int i = 0; i < _nGrid; i++)
        {
            pdf[i] = Mathf.Exp(_logPdf[i] - maxLog);
            sum   += pdf[i];
            if (pdf[i] > modeVal) { modeVal = pdf[i]; modeIdx = i; }
        }

        // Posterior mean and variance
        float mean = 0f, variance = 0f;
        for (int i = 0; i < _nGrid; i++)
        {
            pdf[i] /= sum;
            mean   += pdf[i] * _tGrid[i];
        }
        for (int i = 0; i < _nGrid; i++)
        {
            float d  = _tGrid[i] - mean;
            variance += pdf[i] * d * d;
        }

        MeanLog = mean;
        ModeLog = _tGrid[modeIdx];
        SdLog   = Mathf.Sqrt(variance);
    }
}
