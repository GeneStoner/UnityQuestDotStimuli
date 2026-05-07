# Onset-Triggered Competition: A Mechanistic Account of VRDots Cueing

*Draft — 2026-04-23*

---

## 1. The phenomenon to be explained

In the delayed-onset design, two superimposed dot fields rotate in opposite directions. One field is present from trial start (always-on); the other appears 750 ms later (delayed). After 300 ms of joint rotation, one field briefly translates (80 ms, 0.18°). Observers judge translation direction.

**Key findings:**

| Result | Value | Implication |
|---|---|---|
| Basic cueing effect | ~35pp (CUED > UNCUED) | Delayed field has advantage |
| Motion swap (S&B; our MC) | Cueing survives (~25–35pp) | Advantage is not feature-based |
| Color swap | Cueing survives | Advantage is not feature-based |
| MC combined | Cueing reduced (~25pp) | Features matter somewhat at the margin |
| Simultaneous onset | Cueing ~0 | Advantage requires onset asymmetry |
| Density N=63–500 | Cueing flat ~35pp | Advantage scales with density |
| Density N=1000 | Cueing drops to ~25pp (CUED arm drops; UNCUED stable) | Advantage has a density ceiling |
| Depth swap ZdA | Disrupts cueing | Surface continuity matters |
| Depth swap ZdB | Enhances cueing | |

---

## 2. The mechanistic chain

### Step 1 — Onset triggers V1 suppression of the always-on field

At 750 ms, the delayed field appears. Its dots produce luminance transients distributed across all shared receptive fields. This drives broadly-tuned inhibitory interneurons in V1 (Tucker & Fitzpatrick, 2006: "a transient veto") that transiently silence nearby excitatory neurons — including those responding to the ongoing rotation of the always-on field. Magnocellular-channel transient responses further suppress parvocellular sustained responses to the always-on rotation (Breitmeyer & Ganz, 1976).

**Time course:** ~10–50 ms. The suppression is the *trigger*, not the carrier.

### Step 2 — Suppression window enables surface parsing

During the brief suppression window, the always-on field's V1 representation is weakened while the delayed field's onset response is strong. This asymmetry in activation allows the visual system to parse the delayed dots as a distinct perceptual surface — a new transparent layer superimposed on the existing one. Without this initial asymmetry, the two fields are indistinguishable (identical random-dot textures in the same locations, same speed).

The surface representation is the bridge across the 300 ms pre-translation gap. Once established, it does not require ongoing suppression to persist — it is maintained by higher-level surface/object representation mechanisms (area MT, MST, possibly IT for texture identity).

**Key constraint:** This step requires transparent motion perception. If the visual system cannot maintain two distinct surface percepts (e.g., at very high density), the bridge fails.

### Step 3 — Object-based attention allocated to the delayed surface

Abrupt onsets capture spatial attention automatically and rapidly (Yantis & Jonides, 1984, 1988). This attention is directed to the locations of the delayed-field dots at onset — but those locations are distributed across the entire aperture and move as the dots rotate. Attention therefore cannot anchor to fixed spatial positions; it must track the delayed *surface* as an object.

Object-based attention (Mitchell, Stoner, Reynolds, 2003; O'Craven et al., 1999) allocates processing resources to a perceptual surface as a unit. Once the delayed field is parsed as a surface, attention follows that surface through the 300 ms pre-translation rotation, maintaining preferential processing of its dots regardless of their specific locations at any frame.

### Step 4 — Attentional modulation at V1 and MT during translation

Spatial attention is known to modulate V1 responses (Motter, 1993; Luck et al., 1997) and MT direction-selective responses. When translation begins at tStart, the delayed-field dots move coherently in the heading direction while the always-on field continues rotating.

Because attention is allocated to the delayed surface:
- **CUED trials** (delayed field translates): attentional gain on the translating signal; attentional suppression of the rotating noise → high d'
- **UNCUED trials** (always-on field translates): no attentional gain on the translating signal; attentional enhancement of the rotating noise → low d'

The cueing effect is the behavioral expression of this attentional asymmetry at MT.

---

## 3. How the chain accounts for each result

### Basic cueing (~35pp)
Onset → surface parsing → sustained object attention → attentional gain on CUED translation signal, suppression on UNCUED noise. Direct prediction.

### Motion and color swaps (cueing survives)
Surface assignment is established at onset (750 ms) based on which dots appeared then — not on their current motion direction or color. Swapping features at tStart does not reassign dot identity. The attention remains on the delayed surface regardless of what direction it is now rotating. **The surface outlasts its features.** Stoner & Blanc's result is exactly right: the competitive advantage is identity-based, not feature-based.

### MC combined swap (partial reduction, ~25pp)
When both motion direction and color change simultaneously at tStart, the perceptual system faces ambiguity in tracking the delayed surface: its dots now share the motion direction and color of what the always-on field previously had, and vice versa. This does not fully reassign surface identity (cueing survives), but it adds perceptual uncertainty to the surface tracking, partially eroding the attentional advantage.

### Simultaneous onset (cueing ~0)
Without onset asymmetry, no surface is "new." Both fields are parsed simultaneously with equal salience. No attentional capture favors either field. Object-based attention is allocated to neither surface preferentially. CUED ≈ UNCUED.

### Density flat region (N=63–500)
The attentional gain on the translating signal and the attentional suppression of the rotating noise are both proportional to the number of dots. Over a wide density range, the signal-to-noise ratio at each MT RF is approximately constant — more signal but proportionally more noise, with the attentional asymmetry maintaining a constant ratio. Cueing is flat because the mechanism is operating at a fixed advantage per dot-pair.

The onset suppression at Step 1 also scales with density (more dots = larger luminance transient = stronger suppression), so surface parsing remains reliable across this range.

### N=1000 density drop (CUED arm specifically decreases)
At very high density, transparent motion perception begins to degrade. The visual system can no longer maintain two distinct surface percepts — every small RF contains so many dots from both fields that the local motion signals are indistinguishable. The surface parsing at Step 2 becomes noisy: attention is allocated to a poorly-defined surface, and the gain asymmetry at Step 4 is reduced.

Critically, the UNCUED arm remains flat (~28%) because it never had an attentional advantage to lose. Only CUED decreases, as the attentional gain on the translating signal erodes.

### Depth swaps
ZdA (cued dot changes depth plane at tStart): disrupts the perceptual continuity of the delayed surface at the moment of translation, reducing the effective attentional advantage just when it matters.
ZdB (uncued dot changes depth plane): disrupts the always-on surface without disrupting the delayed surface — if anything, the disparity change in the always-on field makes it more perceptually distinct from the delayed field, sharpening the surface segregation and enhancing cueing.

---

## 4. What the model needs to implement

The mechanism has four stages with identifiable parameters:

| Stage | Key parameter | Observable constraint |
|---|---|---|
| V1 onset suppression | Suppression magnitude, time constant | Density scaling of onset response |
| Surface parsing | Parsing reliability as function of density | Where cueing plateau breaks down |
| Attention gain | g (multiplicative enhancement/suppression) | Magnitude of cueing effect (~35pp) |
| MT integration | RF size, coherence threshold | Translation detection baseline |

The density data constrains the surface-parsing stage most directly: the flat plateau from N=63–500 tells us that parsing is reliable in this range; the drop at N=1000 tells us where it begins to fail. N=750 (pending) will locate the transition.

---

## 5. Open questions

1. **What maintains the surface representation across 300 ms?** Feedback from MT/MST back to V1? Sustained attention to a moving texture? This is the deepest gap.

2. **Is the 300 ms pre-translation rotation necessary, or just sufficient?** An SOA manipulation (vary pre-translation duration) would test whether shorter gaps degrade cueing — directly probing Step 2 (surface establishment time).

3. **Does onset suppression persist as a directional signature?** 300 ms of adaptation to the always-on rotation might leave direction-selective cells tuned to that rotation selectively suppressed, even after the onset transient decays. This would be an additional mechanism at Step 4 — not duration-based in S&B's sense (the magnitude of the effect doesn't depend on motion duration), but directionally specific (those particular neurons are suppressed, regardless of which field now drives them).

4. **What is the density limit for transparent motion?** The N=750 session and further psychophysical probing (does observers' explicit percept of two surfaces degrade at N=1000?) would constrain Step 2.

---

*Companion model: `vrdots_competition_model.py`*
