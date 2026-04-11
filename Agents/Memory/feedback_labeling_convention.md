---
name: VRDots Near/Far labeling convention
description: User's preferred labeling of depth conditions is by translating field depth, not delayed field depth — critical for correct interpretation of all depth results
type: feedback
---

In VRDots code and TSVs, CUED/UNCUED Near/Far labels refer to the depth of the **delayed (Field B) field**. But the user thinks about conditions in terms of which depth plane the coherent translation occurred in (translating-field depth).

These diverge for UNCUED conditions:
- VRDots "UNCUED Near" = Far translates (Field A = opposite depth)
- VRDots "UNCUED Far" = Near translates

The correct comparison the user wants: hold translating depth constant, vary cueing.
- Far translation: CUED Far vs UNCUED Near (both have Far translation)
- Near translation: CUED Near vs UNCUED Far (both have Near translation)

**Why:** The "Near reversal" (CUED Near < UNCUED Near) was an artifact of comparing two conditions with different translating depths. When translating depth is held constant, CUED > UNCUED at all depths and all swaps — no reversal. The bar figure implementing this correctly is `Agents/Figures/depthparam_by_trans_depth.png`.

**How to apply:** Whenever discussing or plotting Near/Far cueing in depth experiments, always clarify which labeling convention is in use and default to the translating-field-depth framing the user prefers. Never describe a condition as "Near cueing" without being explicit whether that means the cue was near or the translation was near.
