# Pilot Parameter Search Strategy
## Adaptive Methods for Fast Exploration of Density, Aperture, and Swap Robustness

*Audience: GS (experimenter) + programmer (implementation)*
*Context: Fixed-level % correct sessions are too slow and too insensitive for the current questions. We need a framework that covers more of the parameter space per hour of observer time and gives results that are directly comparable across conditions.*

---

## The Problem We Are Solving

Three puzzles motivate this search:

1. **Density insensitivity.** The cueing effect barely changes from N=63 to N=500, with only a modest drop at N=1000. This is at odds with the implication from motion and color swap studies that the effect is spatially fine-grained. If fine-grained means "sensitive to which specific dots are selected," then crowding the two fields together should disrupt selection. It does not seem to.

2. **Swap effects are not robust across parameters.** Motion swap and color swap effects replicate in some configurations but weaken in others. We do not yet know whether the fragility reflects genuine parameter sensitivity, or whether we are simply at different points on the psychometric function for different conditions — so the fixed 80ms level is more or less informative depending on the condition.

3. **50% swap results are noisy and parameter-sensitive.** Same fundamental issue: without knowing where each condition sits on its own psychometric function, we cannot tell whether two conditions differ in sensitivity or just differ in how our fixed probe duration samples them.

**Core insight.** By measuring a *threshold* (minimum duration to reach criterion performance) rather than % correct at a fixed duration, we get a number that is directly comparable across conditions even when overall task difficulty varies. The cueing advantage becomes a threshold *ratio* (UNCUED threshold / CUED threshold) rather than a percentage point difference. This ratio is interpretable regardless of whether the manipulation also affects overall difficulty.

---

## SECTION 1 — FOR THE EXPERIMENTER (GS)

### What you are trying to find out

For each parameter combination, you want to know:

- **T_CUED**: minimum translation duration for criterion performance in the CUED condition
- **T_UNCUED**: minimum translation duration in the UNCUED condition
- **Cueing ratio R = T_UNCUED / T_CUED**: values above 1.0 mean cuing helps; R ≈ 1.0 means cuing is absent for this parameter set

When you vary density, aperture, or swap type, you want to watch how R changes. If density disrupts cueing, R should decrease toward 1.0 at high densities. If swap type disrupts cueing, R should decrease when a disruptive swap is applied.

This is better than tracking Δpp (percentage point difference) because Δpp is sensitive to where on the psychometric function 80ms happens to land — which varies across conditions. R is not.

### The priority parameter space

Work in this order:

**Tier 1 (do first — 2-3 sessions each):**
1. **Density × CUED/UNCUED baseline.** Density levels to cover: VeryLow (N≈20), Low (N=63), Medium (N=173), Standard (N=500), High (N=750), UltraHigh (N=1000). Fixed aperture. No swaps. Measure R at each density.
   - Key question: does R fall monotonically with density, or is there a threshold density above which it drops?

2. **Aperture size × CUED/UNCUED, fixed density.** Hold N constant (say N=173 or N=500), vary aperture radius: small (3°), standard (7°), large (12°). This changes inter-dot spacing while holding number of dots constant.
   - Key question: does R scale with aperture, or is it aperture-independent?

**Tier 2 (run after Tier 1 shape is clear — 2-3 sessions each):**
3. **Density × swap type.** At 2-3 key density levels (low, medium, high), measure threshold under: no-swap, motion swap, 50% dot swap (Dots50Swap). Compare swap cost (T_CUED_swap / T_CUED_noswap) across density levels.
   - Key question: does the swap cost change with density? If density doesn't affect baseline cueing but does affect swap cost, that's informative about what the swap is disrupting.

4. **Aperture × swap type.** Same logic, but varying aperture instead of density.

**Tier 3 (drill down on interesting findings):**
- Whatever Tier 1 and 2 reveal: if there is a density breakpoint, run more levels around it; if aperture matters, probe the transition region.

### Decision rules for moving on

After each mini-QUEST session (~50 trials per condition), compute rough threshold estimates. Apply these stopping rules:

- **R ≥ 1.5 and stable across 2 sessions**: condition shows cueing; move on, only revisit if needed for precision.
- **R < 1.2 from a single session**: suggestive of cueing loss; run one more session before concluding. If confirmed, this is a priority condition.
- **R is erratic (>30% change between sessions)**: increase trials per condition before concluding anything.

### What "fast and dirty" means in practice

- **Per session: 200–300 trials**, covering 4–6 conditions simultaneously (interleaved).
- **Per condition per session: 40–60 trials** → rough threshold, usable for R estimation.
- **Precision threshold**: 2 sessions per condition (~100 trials pooled) gives SD on log-threshold of ~0.15 log units — good enough for a factor-of-2 difference to be visible.
- **Full precision (for publication)**: 5–6 sessions per condition → SD ~0.08 log units.

A Tier 1 sweep (6 density levels × 2 conditions) requires:
6 × 2 × 50 trials = 600 trials ≈ **3 sessions**
versus the current approach (one full session per condition = 12 sessions minimum for the same coverage).

### Interpreting the density result

Whatever shape the threshold-vs-density curve takes, you can now distinguish two hypotheses:

**Hypothesis A (spatially fine-grained, dot-identity-based):** R decreases monotonically with density because crowding degrades the spatial precision of the attentional tag. Both T_CUED and T_UNCUED rise with density, but CUED rises faster once crowding interferes with dot-level selection.

**Hypothesis B (motion-energy-based, V1 RF scale):** R stays flat until density crosses the point where local-pairing (Qian et al.) disrupts transparency perception. Below that point, the two motion-energy channels are clearly distinguishable regardless of inter-dot spacing. Above it, even the surface percept degrades, so cueing has nothing to work with.

The threshold approach is sensitive enough to tell these apart at pilot scale. Fixed-80ms % correct is not, because as density rises the 80ms level drifts toward floor for both conditions, and the difference shrinks for trivial reasons.

---

## SECTION 2 — FOR THE PROGRAMMER

### What needs to be built

The goal is an adaptive trial runner that, within a single session, maintains separate QUEST staircases for multiple conditions (e.g., CUED and UNCUED at several density levels) and interleaves them randomly across trials.

### Architecture options (in order of implementation effort)

---

#### Option A: Pre-generated trial list (lowest effort, adequate for screening)

**How it works:** Python generates a trial sequence offline before each session using simulated QUEST. Unity reads from a CSV/TSV manifest and runs trials in the specified order. No live adaptation.

**Python (pre-session):**
```python
from psychopy.data import QuestHandler  # or use the quest package
import numpy as np, csv

# One QuestHandler per condition
conditions = {
    'CUED_N173':   QuestHandler(startVal=np.log10(80), startValSd=0.5,
                                pThreshold=0.75, gamma=0.125,
                                nTrials=60, minVal=np.log10(10), maxVal=np.log10(400)),
    'UNCUED_N173': QuestHandler(startVal=np.log10(100), startValSd=0.5,
                                pThreshold=0.75, gamma=0.125,
                                nTrials=60, minVal=np.log10(10), maxVal=np.log10(400)),
    # ... add more conditions
}

# Generate interleaved trial order
trials = []
for cond_name, q in conditions.items():
    for _ in range(q.nTrials):
        trials.append({'condition': cond_name, 'duration_ms': None})

np.random.shuffle(trials)

# Fill in QUEST-suggested durations (simulated, since we don't have responses yet)
# For pre-generation: assign round-robin from each staircase's prior
# Better: use the first QUEST estimate (prior mean) for all trials of that condition
# and update offline after the session (see Option B for live updating)

for t in trials:
    q = conditions[t['condition']]
    raw_dur = 10 ** q._nextIntensity  # current QUEST estimate in log ms
    # Quantize to frame grid (90Hz = 11.11ms per frame)
    frames = max(1, round(raw_dur / 11.11))
    t['duration_ms'] = frames * 11.11
    t['duration_frames'] = frames

# Write manifest
with open('/tmp/trial_manifest.csv', 'w') as f:
    writer = csv.DictWriter(f, fieldnames=['trial_idx', 'condition', 'duration_ms', 'duration_frames'])
    writer.writeheader()
    for i, t in enumerate(trials):
        t['trial_idx'] = i
        writer.writerow(t)
```

**Limitation:** Without live feedback, the staircase cannot update within the session. Durations are fixed to QUEST's prior estimate. This is essentially a very coarse MoCS. Useful for screening; not proper QUEST.

**Unity (reading the manifest):**
Add a `TrialManifestReader.cs` component that reads the CSV at session start and feeds duration values to `TrialBlockRunner` rather than using the ScriptableObject-defined fixed duration. Each trial looks up its `duration_frames` from the manifest by trial index.

---

#### Option B: Live QUEST in C# (moderate effort, proper adaptive)

**How it works:** Implement QUEST directly in Unity C#. After each trial response, the QUEST posterior updates and the next trial for that condition is drawn from the updated estimate.

**C# QUEST implementation sketch:**

```csharp
// QuestHandler.cs
using System;
using UnityEngine;

public class QuestHandler {
    // QUEST operates in log10(intensity) space
    private float[] _pdf;          // posterior PDF over threshold values
    private float[] _x;            // candidate threshold values (log10 ms)
    private float   _beta;         // psychometric function slope
    private float   _gamma;        // guess rate (0.125 for 8-AFC)
    private float   _lambda;       // lapse rate
    private float   _pThreshold;   // target proportion correct (0.75)
    private int     _nTrials;
    private int     _trialsRun;

    public float currentThreshold => _x[ArgMax(_pdf)];  // MAP estimate
    public bool  isDone           => _trialsRun >= _nTrials;

    public QuestHandler(float startVal, float startValSd,
                        float pThreshold = 0.75f, float beta = 2.5f,
                        float gamma = 0.125f, float lambda = 0.02f,
                        int nTrials = 60, float xMin = 1.0f, float xMax = 2.7f,
                        int nBins = 100) {
        _beta = beta; _gamma = gamma; _lambda = lambda;
        _pThreshold = pThreshold; _nTrials = nTrials; _trialsRun = 0;

        // Initialize x grid and Gaussian prior
        _x   = new float[nBins];
        _pdf = new float[nBins];
        float dx = (xMax - xMin) / (nBins - 1);
        for (int i = 0; i < nBins; i++) {
            _x[i]   = xMin + i * dx;
            float z = (_x[i] - startVal) / startValSd;
            _pdf[i] = Mathf.Exp(-0.5f * z * z);
        }
        NormalizePdf();
    }

    // Returns the suggested log10(duration_ms) for the next trial
    public float NextIntensity() {
        // Place trial at current MAP threshold estimate
        return _x[ArgMax(_pdf)];
    }

    // Update posterior given stimulus intensity x and response (1=correct, 0=wrong)
    public void Update(float intensity, int response) {
        for (int i = 0; i < _x.Length; i++) {
            float p = PsychometricFunction(intensity, _x[i]);
            _pdf[i] *= (response == 1) ? p : (1f - p);
        }
        NormalizePdf();
        _trialsRun++;
    }

    // Weibull psychometric function
    private float PsychometricFunction(float x, float threshold) {
        float d  = x - threshold;
        float p  = _gamma + (1f - _gamma - _lambda) *
                   (1f - Mathf.Exp(-Mathf.Pow(10f, _beta * d)));
        return Mathf.Clamp(p, 0.001f, 0.999f);
    }

    public float ThresholdEstimate() => _x[ArgMax(_pdf)];

    public float ThresholdMean() {
        float mean = 0f;
        for (int i = 0; i < _x.Length; i++) mean += _x[i] * _pdf[i];
        return mean;
    }

    private void NormalizePdf() {
        float sum = 0f;
        foreach (float v in _pdf) sum += v;
        for (int i = 0; i < _pdf.Length; i++) _pdf[i] /= sum;
    }

    private int ArgMax(float[] arr) {
        int idx = 0;
        for (int i = 1; i < arr.Length; i++)
            if (arr[i] > arr[idx]) idx = i;
        return idx;
    }
}
```

**Integration into TrialBlockRunner:**

```csharp
// In TrialBlockRunner.cs (additions)

// One QuestHandler per condition slot
private QuestHandler[] _quests;
private string[]       _questConditions;  // e.g. {"CUED_N173", "UNCUED_N173", ...}
private int[]          _questTrialCounts;

void InitQuestMode() {
    _quests = new QuestHandler[] {
        new QuestHandler(startVal: Mathf.Log10(60f),  startValSd: 0.5f, gamma: 0.125f),
        new QuestHandler(startVal: Mathf.Log10(120f), startValSd: 0.5f, gamma: 0.125f),
    };
    _questConditions  = new string[] { "CUED", "UNCUED" };
    _questTrialCounts = new int[]    { 0, 0 };
}

// Called at start of each trial: pick a condition and get duration
(int condIdx, float durationMs) GetNextQuestTrial() {
    // Pick condition: round-robin among non-exhausted staircases
    int condIdx = -1;
    for (int i = 0; i < _quests.Length; i++) {
        if (!_quests[i].isDone) { condIdx = i; break; }
    }
    if (condIdx < 0) return (-1, 0f);  // all done

    float logDur = _quests[condIdx].NextIntensity();
    float rawMs  = Mathf.Pow(10f, logDur);

    // Quantize to frame grid
    float frameMs  = 1000f / Application.targetFrameRate;
    int   frames   = Mathf.Max(1, Mathf.RoundToInt(rawMs / frameMs));
    float quantMs  = frames * frameMs;

    return (condIdx, quantMs);
}

// Called after response received
void OnResponseReceived(int condIdx, float actualDurationMs, bool correct) {
    float logDur = Mathf.Log10(actualDurationMs);
    _quests[condIdx].Update(logDur, correct ? 1 : 0);

    // Log to TSV: include questCondition, requestedDuration, actualDuration, correct
}
```

**Key implementation notes for programmer:**

1. **Log10 space throughout.** QUEST operates in log-intensity space. Durations should be stored and computed as log10(ms). Only convert to linear ms at the moment of quantization and presentation.

2. **Quantize AFTER QUEST, feed back quantized value.** QUEST requests a continuous value; you round to the nearest frame. The value you feed back to `Update()` must be the *quantized* duration (what was actually shown), not the requested value. Otherwise the posterior will drift.

3. **Condition interleaving.** The simplest interleaving strategy for 2 conditions: randomly choose a condition on each trial with probability proportional to remaining trials in each staircase. This keeps the two staircases approximately in sync.

4. **Save QUEST state to TSV.** Each trial row should include: `questCondition`, `questSuggestedDuration_ms`, `presentedDuration_ms`, `presentedDuration_frames`, `correct`, `questThresholdAfterTrial`. This lets Python reconstruct or override the QUEST estimate offline.

5. **Minimum duration clamp.** Set a hard minimum of 1 frame (~11ms at 90Hz). At very short durations, the staircase may request sub-frame values; clamp at 1 frame. Set a maximum of ~20 frames (~220ms) to prevent runaway staircases on UNCUED trials.

6. **Session end: write threshold estimates.** At session end, write a summary row or separate file with the final QUEST threshold estimate (MAP and mean) for each condition.

---

#### Option C: Between-block QUEST (lowest Unity effort, good compromise)

If implementing live QUEST in Unity is too much work right now, a pragmatic middle ground: run **blocks of fixed-duration trials** (e.g., 20 trials per block at one duration level). After each block, Python (running on the Mac, connected via USB or reading from ADB pull) computes a QUEST update and outputs the duration for the next block. You manually enter the next duration into the experiment asset before the next block.

This is not elegant but requires zero new Unity code — you already have the ability to set duration in the ScriptableObject. Each "block" is a mini-session of 20 trials, and you're doing the adaptive step manually between blocks. ~6 blocks per condition (6 × 20 = 120 trials) gives a reasonable threshold estimate.

**Python between-block QUEST updater:**

```python
# between_block_quest.py
# Run this after each ADB pull; it reads the latest TSV and outputs next duration

from psychopy.data import QuestHandler
import pandas as pd, numpy as np, sys

FRAME_MS = 11.11  # 90Hz

def load_latest_block(tsv_path):
    df = pd.read_csv(tsv_path, sep='\t')
    # Filter to most recent block
    return df[df['blockIdx'] == df['blockIdx'].max()]

def snap_to_frame(ms):
    frames = max(1, round(ms / FRAME_MS))
    return frames * FRAME_MS, frames

# Maintain QUEST state in a pickle between blocks
import pickle, os
state_file = '/tmp/quest_state.pkl'

if os.path.exists(state_file):
    with open(state_file, 'rb') as f:
        q = pickle.load(f)
else:
    q = QuestHandler(startVal=np.log10(80), startValSd=0.5,
                     pThreshold=0.75, gamma=0.125,
                     nTrials=120, minVal=np.log10(10), maxVal=np.log10(300))

# Load last block and update
block = load_latest_block(sys.argv[1])
for _, row in block.iterrows():
    q.addResponse(row['correct'], np.log10(row['translationDuration_ms']))

# Get next duration
next_log = q.mean()
next_ms, next_frames = snap_to_frame(10 ** next_log)
print(f"Next duration: {next_ms:.1f} ms ({next_frames} frames) | "
      f"Threshold estimate: {10**next_log:.1f} ms")

with open(state_file, 'wb') as f:
    pickle.dump(q, f)
```

---

### Data format for threshold analysis

Regardless of which option is used, the Python analysis pipeline needs these columns per trial:

| Column | Description |
|---|---|
| `questCondition` | e.g. `CUED_N173`, `UNCUED_N500` |
| `requestedDuration_ms` | What QUEST suggested |
| `presentedDuration_ms` | Quantized value actually shown |
| `presentedDuration_frames` | Integer frame count |
| `correct` | 1/0 |
| `dotDensity_N` | Dot count for this trial |
| `aperture_deg` | Aperture radius in degrees |
| `swapType` | N / MotionSwap / Dots50 / etc. |
| `questThresholdEstimate_ms` | Running MAP estimate after this trial |

### Post-session analysis (Python)

```python
# threshold_analysis.py
import pandas as pd, numpy as np
import psignifit as ps
import matplotlib.pyplot as plt

df = pd.read_csv('session.tsv', sep='\t')

def fit_threshold(trials):
    """Fit Weibull to trials DataFrame; return (threshold_ms, ci_low, ci_high)"""
    durations = trials['presentedDuration_ms'].values
    correct   = trials['correct'].values
    levels    = sorted(set(durations))
    data = np.array([[d, correct[durations==d].sum(), (durations==d).sum()]
                     for d in levels])
    res = ps.psignifit(data, sigmoid='weibull',
                       experiment_type='nAFC', nAFC=8,
                       fixed_params={'lambda': 0.02})
    t75 = res.threshold(0.75)
    ci  = res.confidence_intervals['threshold'][0]  # 95% CI
    return t75, ci[0], ci[1]

# Compute R per density level
results = []
for N in df['dotDensity_N'].unique():
    for swap in df['swapType'].unique():
        cued   = df[(df['dotDensity_N']==N) & (df['swapType']==swap) & (df['questCondition'].str.startswith('CUED'))]
        uncued = df[(df['dotDensity_N']==N) & (df['swapType']==swap) & (df['questCondition'].str.startswith('UNCUED'))]
        if len(cued) < 30 or len(uncued) < 30:
            continue
        t_c, ci_c_lo, ci_c_hi = fit_threshold(cued)
        t_u, ci_u_lo, ci_u_hi = fit_threshold(uncued)
        R = t_u / t_c
        results.append({'N': N, 'swap': swap, 'T_CUED': t_c, 'T_UNCUED': t_u, 'R': R})

res_df = pd.DataFrame(results)
print(res_df.sort_values(['swap', 'N']))

# Plot R vs density
fig, ax = plt.subplots()
for swap, grp in res_df.groupby('swap'):
    ax.plot(grp['N'], grp['R'], marker='o', label=swap)
ax.axhline(1.0, color='k', linestyle='--', alpha=0.4)
ax.set_xscale('log')
ax.set_xlabel('Dot density N')
ax.set_ylabel('Cueing ratio (T_UNCUED / T_CUED)')
ax.legend()
plt.tight_layout()
plt.savefig('cueing_ratio_vs_density.png', dpi=150)
```

---

## Summary Checklist

**Experimenter:**
- [ ] Agree on density levels (suggest: 20, 63, 173, 500, 750, 1000)
- [ ] Agree on aperture sizes (suggest: 3°, 7°, 12°)
- [ ] Set screening criterion (R < 1.2 = flag for replication; R > 1.5 = proceed)
- [ ] Plan session schedule: Tier 1 density sweep first (3 sessions), then aperture (2 sessions)

**Programmer:**
- [ ] Choose implementation option: A (pre-generated), B (live C#), or C (between-block Python)
- [ ] Add `questCondition`, `requestedDuration_ms`, `presentedDuration_frames` columns to TSV output
- [ ] Add variable-duration capability to `TrialBlockRunner` (read duration from manifest or staircase)
- [ ] Implement frame quantization (round to nearest frame, feed back quantized value)
- [ ] Test: verify that very short (1-frame) and long (20-frame) trials present correctly
- [ ] Port `threshold_analysis.py` to canonical analysis directory once tested
