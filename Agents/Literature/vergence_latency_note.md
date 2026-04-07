# Vergence Eye Movements and the 80ms Translation Window
*Literature agent — 2026-04-06*

---

## The Question

The depth-field cueing effect (F2: +12.5pp) could in principle be partly mediated by vergence eye movements — if the eyes are moving toward (or away from) the correct depth plane during the translation window, this might aid detection. Conversely, a depth swap at tStart (Z condition) might trigger vergence in the wrong direction, adding a motor confound. How much do vergence dynamics matter during the 80ms translation?

---

## 1. Vergence Latency

**Classic estimate** (Rashbass & Westheimer 1961): ~160ms latency for reflexive vergence to a disparity step, measured in closed-loop conditions.

**Modern short-latency findings** (Busettini, Masson & Miles 1997; Busettini et al. 2001 *J Neurophysiol* 85:1129): When measured open-loop (before visual feedback can influence the response), the earliest vergence eye movements begin at **70–85ms**. This "short-latency disparity vergence" or "express vergence" is a real phenomenon but represents the very leading edge of the response — the actual eye displacement at 80ms is minimal.

**Practical timecourse**:
- 0–70ms: pure latency period — eyes completely stationary
- 70–85ms: vergence just begins to accelerate (onset range)
- 85–150ms: initial acceleration phase — small but growing displacement
- 150–400ms: main vergence response — peak velocity, substantial displacement
- >400ms: slow tonic adjustment, settles to steady state

**Convergence vs. divergence asymmetry**: Convergence is ~10–15ms faster than divergence and has ~2× higher peak velocity. This asymmetry is consistent across studies.

---

## 2. At tStart: Vergence Is Already in Steady State

By tStart, the stimulus has been present for **1050ms** (750ms delayed onset + 300ms pre-translation). Vergence steady state for a sustained static disparity is achieved in ~200–300ms. With 1050ms of exposure:

- **The eyes are verged to the initial depth configuration at tStart.** Any phasic vergence response to the original disparity step (at stimulus onset) has long since completed and decayed.
- Pre-translation, both fields are static. The observer is stably verged somewhere between the two depth planes (probably near the fixation/screen plane, since the display subtends a small aperture and fixation is maintained on the center point).
- There is no ongoing vergence movement at tStart. The vergence state is frozen.

---

## 3. What Happens at tStart in the Z Condition (Depth Swap)?

At tStart in the Z condition, the translating field instantaneously shifts disparity by ~5.4 arcmin (0.05m at 2m). This is a new disparity step that could trigger vergence.

Timeline after the depth-swap at tStart:

| Time post-tStart | Vergence status |
|-----------------|----------------|
| 0–70ms | Pure latency — eyes stationary |
| 70–80ms | Vergence *just beginning* to accelerate |
| **80ms (translation ends)** | **Eyes have moved negligibly — < 1 arcmin displacement** |
| 80–200ms | Vergence accelerates, peak velocity |
| 200–400ms | Vergence completes, new steady state |

**Conclusion: Vergence is essentially frozen during the entire 80ms translation window.** Whether or not a depth swap occurs at tStart, the eyes are in the same position throughout the translation. The vergence system cannot respond in time.

---

## 4. The 5–6 Arcmin Disparity — Is It Even a Strong Vergence Driver?

The total disparity between the two fields is ~5.4 arcmin (each field is ±2.7 arcmin from fixation disparity). This is relevant because:

**Panum's fusional area**: Typical fusional range at fovea is 30–60 arcmin (Schor & Tyler 1981 *Vision Res* 21:1507). The 5.4 arcmin inter-field disparity is well within the fusional range. Both surfaces are simultaneously fused, not rivalrous. There is no gross vergence error driving a strong phasic response.

**Vergence deadzone**: Disparities well within Panum's area are handled by slow tonic vergence, not fast phasic vergence. The phasic (fast, short-latency) vergence response is primarily driven by large disparity steps exceeding the fusional range. At 5.4 arcmin, any vergence response is likely slow-tonic and operates on timescales of seconds.

**Implication**: Even the long pre-tStart exposure period may not produce complete vergence adjustment to the depth planes, because the disparities are within the fusional range where the visual system handles them perceptually without needing to drive vergence to near-zero error. The eyes may remain verged near the screen plane throughout.

---

## 5. Caziot, Rolfs & Backus (2023) — No Vergence in a Related Paradigm

*(paper_list.md #71 — already integrated)*

Caziot et al. measured vergence continuously (nonius lines + oculometry) while observers oriented attention to depth planes in a VR display. **No vergence shift was detected during depth cueing.** This is the closest existing test to the VRDots scenario and provides direct empirical support that depth-plane attention cuing does not obligatorily drive vergence in a VR paradigm with small disparities.

---

## 6. Interpretation for VRDots

### F2 (Depth-Field Cueing, +12.5pp) Is NOT Vergence-Mediated

Since vergence is frozen during the 80ms translation window regardless of condition, the F2 effect cannot be explained by the eyes moving toward the "correct" depth plane. The effect must be entirely due to **neural disparity processing** — binocular neurons in V1/MT that are already tuned to the pre-established depth planes and that benefit from (or are disrupted by) the translator's depth plane identity.

This supports the **figure-ground account** (Conjecture 3 in color_model_conjecture.md): depth-field cueing works because disparity defines the surface segmentation signal in V1 binocular neurons, and having the translator at the correct depth plane maintains that segmentation signal.

### The Geometric Confound Survives

Even though vergence doesn't move during the 80ms window, the **geometric monocular confound** identified in the DepthSwapCtrl analysis still applies: a disparity change of 0.05m at 2m eccentricity induces a retinal position shift of up to ~5 arcmin per eye (scaling with eccentricity). This shift is instantaneous (it's a geometric property of the stimulus, not a motor response). In the Z condition, the translator gets a spurious retinal displacement at tStart due to the depth change. **This is not a vergence effect — it's a stimulus geometry effect** that is already noted in the open questions. Vergence being frozen means this monocular position shift is NOT canceled by eye movement.

### For the Near/Far Asymmetry

The Far > Near pattern (+12.5pp vergence-irrelevant) cannot be explained by vergence being better adapted to the Far plane. Since both planes are within the fusional range and vergence is at steady state, vergence state at tStart is approximately equal for Near and Far conditions. The Near/Far asymmetry reflects something in the neural processing of crossed vs. uncrossed disparities (Parks & Corballis 2006, Chen et al. 2012) — not vergence motor state.

### Pre-tStart Vergence State

If anything, the observer's resting vergence position (maintained fixation at 2m, small fusional area) means both depth planes are simultaneously fused throughout the pre-translation period. There is no vergence "preference" for Near or Far before tStart — the visual system is simultaneously processing both disparities.

---

## 7. Key Papers

| Paper | Key finding | Relevance |
|-------|------------|-----------|
| **Rashbass & Westheimer (1961)** *JOSA* 51:916 | Classic vergence latency ~160ms (closed-loop) | Establishes lower bound; still holds for slow vergence |
| **Busettini, Masson & Miles (1997)** *Nature* 390:512 | Ultra-short latency vergence ~70–85ms (open-loop) | Tightest constraint: even shortest vergence barely starts at 80ms |
| **Busettini et al. (2001)** *J Neurophysiol* 85:1129 | Short-latency disparity vergence depends on spatial filtering | Confirms ~80ms minimum with minimal early amplitude |
| **Schor & Tyler (1981)** *Vision Res* 21:1507 | Panum's area; fusional range 30–60 arcmin; expands for static stimuli | 5.4 arcmin is well within fusional range → weak phasic vergence driver |
| **Caziot, Rolfs & Backus (2023)** *PNAS Nexus* 2:pgad314 | No vergence shift during depth-plane attention cueing in VR | Direct empirical support: small-disparity VR depth cues don't drive vergence |

---

## Bottom Line

**Vergence does not contaminate the 80ms translation window.** By the time the translation ends, the eyes have moved less than 1 arcmin from their pre-tStart position, regardless of whether a depth swap occurred. The depth-field cueing effect (F2) is entirely a neural disparity effect. The monocular geometric positional shift from depth changes IS present (instantaneous, geometric), but this is a stimulus confound, not a vergence confound — and it is already noted in the open questions as a potential monocular account of Z-condition effects.

*See also*: `open-questions.md` (geometric confound), `depth_ior_hypothesis.md`, `color_model_conjecture.md` (Conjecture 3 — depth as figure-ground)
