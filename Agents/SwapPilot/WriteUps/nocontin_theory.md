# NoContinuity: Results and Theoretical Notes
*2026-05-04*

---

## Paradigm

`Exp_NoContinuity_Peak_ColorMotionSwap_v1` — identical to the standard Peak_ColorMotionSwap asset except `replotTranslatingAtTStart = true`. At tStart, only subfields with `MotionKind.Linear` are replotted to new random positions (TrialBlockRunner.cs line 889). The NonCoherent (noise) subfield is **not** replotted and retains its last rotational position. Spatial continuity between the rotating field and the translating group is therefore broken for the coherent sub only.

Conditions: N (no swap) and MC (full-field color+motion swap). MC swap (ExpSpecTestPhase.cs lines 392–397) is applied to **all four subfields simultaneously** — the non-translating rotating field also reverses direction and color at tStart.

---

## Subfield structure at tStart

| | CUED (Field B = delayed translates) | UNCUED (Field A = early translates) |
|---|---|---|
| **Coherent trans. (Linear, REPLOTTED)** | Sub2 | Sub0 |
| **Noise (NonCoherent, NOT replotted)** | Sub3 | Sub1 |
| **Non-source rotating field** | Sub0+Sub1 (Field A) | Sub2+Sub3 (Field B) |

In MC conditions the non-source rotating field reverses direction and color at tStart (one-frame reversal transient). The translating group also takes on the opposite color from its source field.

---

## Results (2 sessions pooled, n=512/condition)

| Condition | % Correct | Projection | R |
|---|---|---|---|
| N CUED | **28.3%** | 0.227 | 0.228 |
| N UNCUED | 19.7% | 0.102 | 0.106 |
| MC CUED | 22.3% | 0.160 | 0.163 |
| MC UNCUED | 22.3% | 0.160 | 0.172 |

Chance = 12.5%. Session-to-session replication: N CUED = +8.2pp* (S1), +9.0pp* (S2), +8.6pp** pooled (WW p=0.001***). MC cueing null in both sessions.

### Within-swap cueing effects
- **N**: Δ=+8.6pp\*\*, WW F=11.6, p=0.001\*\*\*
- **MC**: Δ≈0pp, WW p=0.098† (marginal direction diff, zero amplitude diff)

### Cross-condition comparisons
- **N CUED vs MC UNCUED**: Δ=+6.1pp\*, WW F=22.0, p<0.0001\*\*\*
- **N UNCUED vs MC CUED**: Δ=−2.5pp n.s., WW p=0.50 n.s.

The asymmetry is stark: the two "bad" conditions (N UNCUED and MC CUED) are statistically identical, while N CUED is significantly better than its closest structural analog (MC UNCUED).

---

## What N CUED and MC UNCUED have in common (structural)

After tStart, both have:
- One dot field rotating in the **non-delayed direction** (Field A = CW in N CUED; Field B, now reversed to CW+red, in MC UNCUED)
- A green group translating coherently
- A green group doing NonCoherent random motion

The only physical differences between N CUED and MC UNCUED are:

1. **Which dots are rotating non-delayed-direction**: In N CUED it is Sub0+Sub1, which have been continuously CW since T0 (1050ms). In MC UNCUED it is Sub2+Sub3, which were CCW until one frame before tStart.

2. **One-frame reversal transient**: Sub2+Sub3 switch from CCW to CW at tStart in MC UNCUED, producing a direction-reversal motion transient at exactly the moment translation begins. No such transient in N CUED.

3. **Which dots convey the translating signal**: In N CUED, Field B's dots (the delayed-onset object) are the ones that get replotted and translate. In MC UNCUED, Field A's dots are the ones that translate (replotted as green), while Field B's dots change identity.

---

## Two candidate explanations for why N CUED > MC UNCUED

### A. One-frame reversal transient
The direction reversal of Sub2+Sub3 in MC UNCUED at tStart generates a strong competing motion signal (direction-change transients have high salience in motion processing). This transient coincides exactly with translation onset and could mask or compete with the translation signal. N CUED has no such transient — the non-source field (Field A) continues rotating without interruption.

This is a low-level motion masking account.

### B. Object-level identity / field assignment
Even without dot-level spatial continuity, the visual system may track **field-level objects** — spatiotemporally coherent ensembles defined by color, direction, and onset time. Field B (green, CCW, delayed) constitutes such an object.

In N CUED: at tStart, Field B's dots are replotted and translate. The "Field B object" is now doing something new — translating. The attentional weight accumulated for Field B (via onset cue) transfers to the translating signal. Competition between Field B (translating) and Field A (rotating) is resolved in Field B's favor.

In MC UNCUED: at tStart, the Field B object dissolves — its dots reverse direction and change color (Sub2+Sub3 → CW+red). Simultaneously, Field A's dots appear at new positions looking like Field B (green+translating). The onset-cued attentional weight for "the green CCW thing that appeared late" has no coherent object to land on. Field B-as-object no longer exists in a recognizable form; Field A-as-object has been disguised. The competition is disrupted not because of a motion transient but because the object-level assignment fails.

This is an object-based attention / motion competition account.

---

## Why N UNCUED ≈ MC CUED

Both have: Field A's dots translating (N UNCUED directly; MC CUED as Field B's replotted dots now colored red = Field A's original color). In both cases the onset cue (Field B) and the translating signal are misaligned — either because Field A translates (N UNCUED) or because the translating object has taken on Field A's identity (MC CUED). The near-perfect equivalence (WW p=0.50) suggests the manipulation that matters is field-level identity, not dot-level continuity.

---

## Predictive coding framing (sketch)

The visual system maintains predictions about each motion object's behavior. At tStart, prediction errors arise. The key question is the *nature* of the prediction error:

- **N CUED**: Field B generates a single coherent prediction error (expected CCW rotation → observed coherent translation at new positions). The prediction error is localizable to Field B and interpretable as "Field B has started translating."

- **MC UNCUED**: Field B generates a compound prediction error: direction changes (CCW→CW) AND color changes (green→red) AND new green dots appear translating elsewhere. The error is not cleanly attributable to Field B doing one new thing. Parsing it requires resolving "did Field B change, or did something new appear, or did fields swap?" The onset-cued attentional prior cannot resolve this ambiguity in the ~80ms translation window.

In this framing, the one-frame transient IS the prediction error signal — but its content (multi-feature violation of Field B) is what disrupts attribution rather than its existence per se as a competing motion signal.

---

## Critical experiment to dissociate A vs B

Run **color-only swap** (no motion direction swap) in the MC UNCUED analog:
- Non-source field (Field B in UNCUED): changes color at tStart but does NOT reverse rotation direction
- No one-frame reversal transient
- Translating dots (Field A's, recolored as green) still impersonate Field B

If this recovers performance toward N CUED: the transient is the mechanism (A).  
If performance remains flat like MC UNCUED: field identity / object assignment is the mechanism (B).

The existing `includeColorSwaps` flag could implement this without a new asset.

---

## Open questions

1. Does the residual N cueing at Ap1.65° / lower density survive NoContinuity? (Tests scale-dependence of the field-object mechanism.)
2. Does the NonCoherent noise subfield (Sub3/Sub1, not replotted, stays at source field positions) contribute positively or negatively? It provides spatially continuous dots from the source field doing random motion — possibly a "texture" cue to field identity.
3. Post-translation: all subfields resume rotating in (possibly swapped) directions. Does the post-translation percept show hysteresis toward the expected direction?
