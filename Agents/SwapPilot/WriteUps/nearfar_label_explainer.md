# Near/Far Label Explainer — DecoupledDots_005m_v2
*GS + Claude, 2026-04-13*

---

## The Short Version

In all performance figures, **Near/Far refers to the depth plane of the delayed field at trial onset** — i.e., where the to-be-translated field sits *before* tStart, during the cue period. In the **N condition** (no swap), this is also where the translator ends up during translation, so the label is unambiguous. In the **Z condition** (depth swap), the translator **jumps to the opposite plane at tStart**, so the Near/Far label is **inverted relative to where the actual translation happens**. A similar inversion affects the UNCUED arm across all conditions.

---

## The Design Reminder

Each trial has:
- **Field B** (delayed, appears second): the temporal cue. In CUED trials this is the translator; in UNCUED trials this is the rotator.
- **Field A** (non-delayed, appears first): always the opposite role.
- The TSV column **`DelayedFieldDepth`** records Field B's depth plane at trial onset.

Two depth planes: **Near** (closer, crossed disparity) and **Far** (farther, uncrossed disparity). In standard trials (no swap), Field A and Field B occupy opposite planes.

---

## N Condition — Labels are straightforward

| Label | CUED arm | UNCUED arm |
|-------|----------|------------|
| **Near** | Temporal cue (Field B) in Near → **translator in Near throughout** | Field B (rotator) in Near → **translator (Field A) in Far** |
| **Far**  | Temporal cue (Field B) in Far  → **translator in Far throughout**  | Field B (rotator) in Far  → **translator (Field A) in Near** |

Note: even in N, the UNCUED label is inverted relative to the translator. "UNCUED Near" = translator is actually in Far.

---

## Z Condition — Both the swap AND the cue-role inversion stack up

In Z, both fields **swap depth planes at tStart**. So:

| Label (DelayedFieldDepth) | Before tStart | After tStart (during translation) |
|--------------------------|---------------|------------------------------------|
| **"Near"** (Field B starts Near) | Translator (CUED) in Near, rotator in Far | **Translator jumps to Far**, rotator jumps to Near |
| **"Far"**  (Field B starts Far)  | Translator (CUED) in Far, rotator in Near | **Translator jumps to Near**, rotator jumps to Far |

**So for CUED Z:**
- **"CUED Z Near"** = temporal cue occurred in Near, but translation happens in **Far** → 97% accuracy
- **"CUED Z Far"**  = temporal cue occurred in Far, but translation happens in **Near** → 50% accuracy

The label describes where the cued field was *when you saw the onset cue*, not where it goes when it starts moving. The cue and the translation are in opposite depth planes in Z. The observer correctly learns which field to follow via the temporal cue, but then that field jumps to the other depth plane.

---

## Does the Data Make Sense?

Yes. The data are interpretable once you track where the translator *actually translates*:

| Condition | Translator translates in | CUED accuracy |
|-----------|--------------------------|---------------|
| N "Near"  | Near                     | 43.8%         |
| N "Far"   | Far                      | 75.0%         |
| Z "Near"  | **Far** (post-swap)      | **97%**       |
| Z "Far"   | **Near** (post-swap)     | 50.0%         |

The pattern is fully consistent: **Far translation → better CUED performance**, Near translation → worse, regardless of condition or which depth plane the cue appeared in. The Z condition just re-indexes which label maps to which translation plane.

The Z "Near" ceiling (97%) likely reflects the combination of:
1. Far translation (intrinsically easier)
2. A salient depth-change transient at tStart that further highlights the cued field

---

## UNCUED Arm — Label is always inverted relative to translator

In UNCUED, the temporal cue marks Field B (the rotator). Field A is the translator. The `DelayedFieldDepth` column records Field B's depth, which is the **opposite** of the translator's depth.

| UNCUED label | Rotator depth | **Translator depth** | UNCUED accuracy (N cond) |
|--------------|--------------|----------------------|--------------------------|
| "Near"       | Near         | **Far**              | 56.2%                    |
| "Far"        | Far          | **Near**             | 15.6%                    |

The "UNCUED Near > Far" pattern we have been reporting is actually **translator Far > Near** — the same direction as CUED. Once re-labeled correctly:

- CUED: Far (75%) > Near (44%) → Far−Near = **+31pp**
- UNCUED (translator-centric): Far (56%) > Near (16%) → Far−Near = **+40pp**

Both arms show Far > Near for the *translating* field. The "UNCUED prefers Near / minimum vergence demand" story was based on misread labels.

---

## What This Changes

**Unchanged findings:**
- F1 (temporal dot cueing) is unaffected — it compares CUED vs UNCUED accuracy and doesn't depend on Near/Far labels.
- F2 (depth field cueing, N vs Z) is unaffected — it compares depth-consistent vs depth-inconsistent conditions.
- F3 (color cueing) is unaffected.
- The artifact story (F1×F2 collapse post-fix) is unaffected.

**Revised interpretation:**
- Near/Far performance asymmetry: both CUED and UNCUED arms show **Far > Near for the translator**. This is a perceptual/discriminability effect of the far depth plane (or possibly a vergence-related effect), not an attentional gradient that differs between the two arms.
- The previous "minimum vergence demand" account for UNCUED was premature — it rested on treating the delayed-field depth label as the translator depth in UNCUED trials, which is backwards.

---

## Action Items

1. All **performance figures** that show Near/Far by CUED/UNCUED arm should re-label the UNCUED arm: swap Near↔Far for UNCUED bars. The CUED arm is unaffected.
2. All **Z condition** Near/Far bars should be annotated or re-labeled to reflect the translation-phase depth, not the cue-phase depth. The simplest fix: use "Translation in Near" / "Translation in Far" as the axis labels for Z/CZ conditions.
3. The **trajectory figures** are already translator-centric and do not need changes.
4. Update the **observer_gs_vergence.md** and **factor-analysis.md** memory files to reflect the revised Near/Far interpretation.
