# Factor-Labeled Trajectories: All Depth Conditions
*VRDots — DepthSwapCtrl (N/ZdA/ZdB) + DepthParam*
*Literature agent, 2026-04-02. For verification of factor assignments.*

---

## Setup and conventions

### Subfields
| Subfield | Field | Role | Default depth | Default rotation |
|----------|-------|------|---------------|-----------------|
| S0 | FieldA (non-delayed) | Coherent translator | Far | CW |
| S1 | FieldA (non-delayed) | Non-coherent (noise) | Far | CW |
| S2 | FieldB (delayed) | Coherent translator | Near | CCW |
| S3 | FieldB (delayed) | Non-coherent (noise) | Near | CCW |

FieldB appears at frame 56 (delayed onset). Translation occurs frames 78–83 (tStart–tEnd). "Near/Far" in condition labels refers to the depth of the **delayed field (FieldB)**, not the translating field.

The tables below show two configuration families:
- **Config-Near**: FieldB at Near, FieldA at Far (as in gen_hypothetical_traj.py)
- **Config-Far**: FieldB at Far, FieldA at Near (the mirror case)

### Three factors
- **F1 (dot cueing)**: Did the DELAYED dots (FieldB, S2/S3) translate? CUED = yes; UNCUED = no
- **F2 (depth-field cueing)**: Did translation occur in the SAME depth plane as the delayed onset field? SAME = yes; DIFFERENT = no
- **F3 (translation depth)**: Which depth plane actually translated? Near or Far — independent of cueing

### Timeline phases
| Phase | Frames | What happens |
|-------|--------|-------------|
| Pre-onset | 0–55 | Only FieldA (S0,S1) active |
| Delay | 56–77 | Both fields rotating; no translation |
| **Translation** | **78–83** | **Coherent translation + noise companions** |
| Post | 84–113 | Back to rotation only |

---

## N — No swap

The coherent translators (S0 and S2) stay in their original depth planes throughout. Swap has no effect; depth planes never change. DepthParam conditions are identical to N (just different depth separations).

---

### N — CUED Near
*Config-Near: FieldB=Near (S2,S3), FieldA=Far (S0,S1)*

| Phase | S0 (FA-coh) | S1 (FA-noncoh) | S2 (FB-coh) | S3 (FB-noncoh) |
|-------|-------------|----------------|-------------|----------------|
| Pre-onset | CW @ Far | CW @ Far | — | — |
| Delay | CW @ Far | CW @ Far | CCW @ Near | CCW @ Near |
| **Translation** | **CW @ Far** | **CW @ Far** | **→ Trans @ Near** | **Noise @ Near** |
| Post | CW @ Far | CW @ Far | CCW @ Near | CCW @ Near |

**S2 (the delayed coherent dot) translates at Near.**

| Factor | Assignment | Reason |
|--------|-----------|--------|
| **F1** | **CUED** | Delayed dots (S2/S3) translate |
| **F2** | **SAME** | Translation at Near = FieldB's depth |
| **F3** | **Near** | Translation occurs in Near plane |

---

### N — UNCUED Near
*Config-Near: FieldB=Near (S2,S3), FieldA=Far (S0,S1)*

| Phase | S0 (FA-coh) | S1 (FA-noncoh) | S2 (FB-coh) | S3 (FB-noncoh) |
|-------|-------------|----------------|-------------|----------------|
| Pre-onset | CW @ Far | CW @ Far | — | — |
| Delay | CW @ Far | CW @ Far | CCW @ Near | CCW @ Near |
| **Translation** | **→ Trans @ Far** | **Noise @ Far** | **CCW @ Near** | **CCW @ Near** |
| Post | CW @ Far | CW @ Far | CCW @ Near | CCW @ Near |

**S0 (the non-delayed coherent dot) translates at Far.**

| Factor | Assignment | Reason |
|--------|-----------|--------|
| **F1** | **UNCUED** | Non-delayed dots (S0/S1) translate |
| **F2** | **DIFFERENT** | Translation at Far ≠ FieldB's depth (Near) |
| **F3** | **Far** | Translation occurs in Far plane |

> **Key label trap**: This condition is called "UNCUED Near" — Near refers to the DELAYED field, not where translation happens. Translation is at Far. F3=Far despite the "Near" label.

---

### N — CUED Far
*Config-Far: FieldB=Far (S2,S3), FieldA=Near (S0,S1)*

| Phase | S0 (FA-coh) | S1 (FA-noncoh) | S2 (FB-coh) | S3 (FB-noncoh) |
|-------|-------------|----------------|-------------|----------------|
| Pre-onset | CW @ Near | CW @ Near | — | — |
| Delay | CW @ Near | CW @ Near | CCW @ Far | CCW @ Far |
| **Translation** | **CW @ Near** | **CW @ Near** | **→ Trans @ Far** | **Noise @ Far** |
| Post | CW @ Near | CW @ Near | CCW @ Far | CCW @ Far |

**S2 translates at Far.**

| Factor | Assignment | Reason |
|--------|-----------|--------|
| **F1** | **CUED** | Delayed dots (S2/S3) translate |
| **F2** | **SAME** | Translation at Far = FieldB's depth |
| **F3** | **Far** | Translation occurs in Far plane |

---

### N — UNCUED Far
*Config-Far: FieldB=Far (S2,S3), FieldA=Near (S0,S1)*

| Phase | S0 (FA-coh) | S1 (FA-noncoh) | S2 (FB-coh) | S3 (FB-noncoh) |
|-------|-------------|----------------|-------------|----------------|
| Pre-onset | CW @ Near | CW @ Near | — | — |
| Delay | CW @ Near | CW @ Near | CCW @ Far | CCW @ Far |
| **Translation** | **→ Trans @ Near** | **Noise @ Near** | **CCW @ Far** | **CCW @ Far** |
| Post | CW @ Near | CW @ Near | CCW @ Far | CCW @ Far |

**S0 translates at Near.**

| Factor | Assignment | Reason |
|--------|-----------|--------|
| **F1** | **UNCUED** | Non-delayed dots (S0/S1) translate |
| **F2** | **DIFFERENT** | Translation at Near ≠ FieldB's depth (Far) |
| **F3** | **Near** | Translation occurs in Near plane |

> **Key label trap**: This condition is called "UNCUED Far" — Far refers to the DELAYED field. Translation is at Near. F3=Near despite the "Far" label.

---

### N — Factor summary

| Condition | F1 | F2 | F3 |
|-----------|----|----|-----|
| CUED Near | CUED | SAME | Near |
| UNCUED Near | UNCUED | DIFFERENT | **Far** ← not Near! |
| CUED Far | CUED | SAME | Far |
| UNCUED Far | UNCUED | DIFFERENT | **Near** ← not Far! |

**Pattern**: In N, F2 is always SAME for CUED and DIFFERENT for UNCUED. F3 always matches the CUED condition's label, and is the OPPOSITE of the label for UNCUED conditions. These are consequences of no swap: the translating field and the delayed field are always the same field (CUED) or different fields (UNCUED).

---

## ZdA — S0↔S2 depth swap

At tStart (frame 78), S0 and S2 exchange depth planes. S0 (originally Far) moves to Near; S2 (originally Near) moves to Far. Rotation groups reorganize: Near-group (S0,S3) rotates CW; Far-group (S1,S2) rotates CCW.

**Effect on factor assignments**: The coherent translator is always displaced into the OPPOSITE depth plane from where it started. This flips both F2 and F3 relative to N for every condition.

---

### ZdA — CUED Near
*Config-Near: FieldB=Near initially (S2,S3), FieldA=Far initially (S0,S1)*
*At tStart: S0→Near, S2→Far*

| Phase | S0 (FA-coh) | S1 (FA-noncoh) | S2 (FB-coh) | S3 (FB-noncoh) |
|-------|-------------|----------------|-------------|----------------|
| Pre-onset | CW @ Far | CW @ Far | — | — |
| Delay | CW @ Far | CW @ Far | CCW @ Near | CCW @ Near |
| **Translation** | **CW @ Near** | **Noise @ Far** | **→ Trans @ Far** | **CW @ Near** |
| Post | CW @ Near | CCW @ Far | CCW @ Far | CW @ Near |

**S2 (delayed coherent) has moved to Far and translates there. S1 serves as the noise companion at Far.**

| Factor | Assignment | Reason |
|--------|-----------|--------|
| **F1** | **CUED** | Delayed dots (S2/S3) translate (S2 translates) |
| **F2** | **DIFFERENT** | Translation at Far ≠ FieldB's original depth (Near) |
| **F3** | **Far** | Translation occurs in Far plane |

> **Counterintuitive**: This is CUED but F2=DIFFERENT. The cued dot moved OUT of the cued depth plane before translating.

---

### ZdA — UNCUED Near
*Config-Near: FieldB=Near initially, FieldA=Far initially*
*At tStart: S0→Near, S2→Far*

| Phase | S0 (FA-coh) | S1 (FA-noncoh) | S2 (FB-coh) | S3 (FB-noncoh) |
|-------|-------------|----------------|-------------|----------------|
| Pre-onset | CW @ Far | CW @ Far | — | — |
| Delay | CW @ Far | CW @ Far | CCW @ Near | CCW @ Near |
| **Translation** | **→ Trans @ Near** | **CCW @ Far** | **CCW @ Far** | **Noise @ Near** |
| Post | CW @ Near | CCW @ Far | CCW @ Far | CW @ Near |

**S0 (non-delayed coherent) has moved to Near and translates there. S3 serves as the noise companion at Near.**

| Factor | Assignment | Reason |
|--------|-----------|--------|
| **F1** | **UNCUED** | Non-delayed dots (S0/S1) translate (S0 translates) |
| **F2** | **SAME** | Translation at Near = FieldB's original depth (Near) |
| **F3** | **Near** | Translation occurs in Near plane |

> **Counterintuitive**: This is UNCUED but F2=SAME. The non-delayed translator moved INTO the cued depth plane (Near), so translation now occurs at the same depth as the delayed field's onset.

---

### ZdA — CUED Far
*Config-Far: FieldB=Far initially (S2,S3), FieldA=Near initially (S0,S1)*
*At tStart: S0→Far (from Near), S2→Near (from Far)*

| Phase | S0 (FA-coh) | S1 (FA-noncoh) | S2 (FB-coh) | S3 (FB-noncoh) |
|-------|-------------|----------------|-------------|----------------|
| Pre-onset | CW @ Near | CW @ Near | — | — |
| Delay | CW @ Near | CW @ Near | CCW @ Far | CCW @ Far |
| **Translation** | **CW @ Far** | **Noise @ Near** | **→ Trans @ Near** | **CW @ Far** |
| Post | CW @ Far | CCW @ Near | CCW @ Near | CW @ Far |

**S2 (delayed coherent) has moved to Near and translates there.**

| Factor | Assignment | Reason |
|--------|-----------|--------|
| **F1** | **CUED** | Delayed dots (S2/S3) translate |
| **F2** | **DIFFERENT** | Translation at Near ≠ FieldB's original depth (Far) |
| **F3** | **Near** | Translation occurs in Near plane |

---

### ZdA — UNCUED Far
*Config-Far: FieldB=Far initially, FieldA=Near initially*
*At tStart: S0→Far (from Near), S2→Near (from Far)*

| Phase | S0 (FA-coh) | S1 (FA-noncoh) | S2 (FB-coh) | S3 (FB-noncoh) |
|-------|-------------|----------------|-------------|----------------|
| Pre-onset | CW @ Near | CW @ Near | — | — |
| Delay | CW @ Near | CW @ Near | CCW @ Far | CCW @ Far |
| **Translation** | **→ Trans @ Far** | **CCW @ Near** | **CCW @ Near** | **Noise @ Far** |
| Post | CW @ Far | CCW @ Near | CCW @ Near | CW @ Far |

**S0 (non-delayed coherent) has moved to Far and translates there.**

| Factor | Assignment | Reason |
|--------|-----------|--------|
| **F1** | **UNCUED** | Non-delayed dots (S0/S1) translate |
| **F2** | **SAME** | Translation at Far = FieldB's original depth (Far) |
| **F3** | **Far** | Translation occurs in Far plane |

---

### ZdA — Factor summary

| Condition | F1 | F2 | F3 |
|-----------|----|----|-----|
| CUED Near | CUED | **DIFFERENT** | **Far** |
| UNCUED Near | UNCUED | **SAME** | **Near** |
| CUED Far | CUED | **DIFFERENT** | **Near** |
| UNCUED Far | UNCUED | **SAME** | **Far** |

**Pattern**: ZdA completely flips F2 relative to N (CUED→DIFFERENT, UNCUED→SAME) and completely flips F3 (CUED Near→Far translation, UNCUED Near→Near translation). This is why ZdA kills the cueing effect: it makes the CUED trial behave like an UNCUED trial in terms of depth-plane targeting.

---

## ZdB — S1↔S3 depth swap

At tStart (frame 78), S1 and S3 exchange depth planes. S1 (originally Far, non-coherent) moves to Near; S3 (originally Near, non-coherent) moves to Far. **The coherent translators (S0 and S2) do NOT change depth planes.**

**Effect on factor assignments**: Because the coherent translators stay put, F1, F2, and F3 are all identical to N. The only change is that the non-coherent noise companions switch planes — disrupting depth-plane grouping signals without changing which dot translates where.

---

### ZdB — CUED Near
*Config-Near: FieldB=Near (S2,S3), FieldA=Far (S0,S1)*
*At tStart: S1→Near, S3→Far (non-coherent dots only)*

| Phase | S0 (FA-coh) | S1 (FA-noncoh) | S2 (FB-coh) | S3 (FB-noncoh) |
|-------|-------------|----------------|-------------|----------------|
| Pre-onset | CW @ Far | CW @ Far | — | — |
| Delay | CW @ Far | CW @ Far | CCW @ Near | CCW @ Near |
| **Translation** | **CW @ Far** | **Noise @ Near** | **→ Trans @ Near** | **CW @ Far** |
| Post | CW @ Far | CCW @ Near | CCW @ Near | CW @ Far |

**S2 translates at Near. S1 has moved to Near and serves as noise companion. S3 has moved to Far.**

| Factor | Assignment | Reason |
|--------|-----------|--------|
| **F1** | **CUED** | Delayed dots (S2/S3) translate (S2 translates) |
| **F2** | **SAME** | Translation at Near = FieldB's original depth (Near) |
| **F3** | **Near** | Translation occurs in Near plane |

> **Same as N CUED Near**: F1=CUED, F2=SAME, F3=Near. The swap of non-coherent companions doesn't change the factor logic.

---

### ZdB — UNCUED Near
*Config-Near: FieldB=Near, FieldA=Far*
*At tStart: S1→Near, S3→Far*

| Phase | S0 (FA-coh) | S1 (FA-noncoh) | S2 (FB-coh) | S3 (FB-noncoh) |
|-------|-------------|----------------|-------------|----------------|
| Pre-onset | CW @ Far | CW @ Far | — | — |
| Delay | CW @ Far | CW @ Far | CCW @ Near | CCW @ Near |
| **Translation** | **→ Trans @ Far** | **CCW @ Near** | **CCW @ Near** | **Noise @ Far** |
| Post | CW @ Far | CCW @ Near | CCW @ Near | CW @ Far |

**S0 translates at Far. S3 has moved to Far and serves as noise companion. S1 has moved to Near.**

| Factor | Assignment | Reason |
|--------|-----------|--------|
| **F1** | **UNCUED** | Non-delayed dots (S0/S1) translate (S0 translates) |
| **F2** | **DIFFERENT** | Translation at Far ≠ FieldB's depth (Near) |
| **F3** | **Far** | Translation occurs in Far plane |

> **Same as N UNCUED Near**: F1=UNCUED, F2=DIFFERENT, F3=Far.

---

### ZdB — CUED Far
*Config-Far: FieldB=Far (S2,S3), FieldA=Near (S0,S1)*
*At tStart: S1→Far, S3→Near*

| Phase | S0 (FA-coh) | S1 (FA-noncoh) | S2 (FB-coh) | S3 (FB-noncoh) |
|-------|-------------|----------------|-------------|----------------|
| Pre-onset | CW @ Near | CW @ Near | — | — |
| Delay | CW @ Near | CW @ Near | CCW @ Far | CCW @ Far |
| **Translation** | **CW @ Near** | **Noise @ Far** | **→ Trans @ Far** | **CW @ Near** |
| Post | CW @ Near | CCW @ Far | CCW @ Far | CW @ Near |

**S2 translates at Far. S1 has moved to Far and serves as noise companion. S3 has moved to Near.**

| Factor | Assignment | Reason |
|--------|-----------|--------|
| **F1** | **CUED** | Delayed dots (S2/S3) translate |
| **F2** | **SAME** | Translation at Far = FieldB's depth (Far) |
| **F3** | **Far** | Translation occurs in Far plane |

---

### ZdB — UNCUED Far
*Config-Far: FieldB=Far, FieldA=Near*
*At tStart: S1→Far, S3→Near*

| Phase | S0 (FA-coh) | S1 (FA-noncoh) | S2 (FB-coh) | S3 (FB-noncoh) |
|-------|-------------|----------------|-------------|----------------|
| Pre-onset | CW @ Near | CW @ Near | — | — |
| Delay | CW @ Near | CW @ Near | CCW @ Far | CCW @ Far |
| **Translation** | **→ Trans @ Near** | **CCW @ Far** | **CCW @ Far** | **Noise @ Near** |
| Post | CW @ Near | CCW @ Far | CCW @ Far | CW @ Near |

**S0 translates at Near. S3 has moved to Near and serves as noise companion.**

| Factor | Assignment | Reason |
|--------|-----------|--------|
| **F1** | **UNCUED** | Non-delayed dots (S0/S1) translate |
| **F2** | **DIFFERENT** | Translation at Near ≠ FieldB's depth (Far) |
| **F3** | **Near** | Translation occurs in Near plane |

---

### ZdB — Factor summary

| Condition | F1 | F2 | F3 |
|-----------|----|----|-----|
| CUED Near | CUED | SAME | Near |
| UNCUED Near | UNCUED | DIFFERENT | Far |
| CUED Far | CUED | SAME | Far |
| UNCUED Far | UNCUED | DIFFERENT | Near |

**Pattern**: Identical to N in all three factors. ZdB only moves the non-coherent companions across depth planes — this disrupts depth-plane grouping (a potential confound) without altering which dot translates at which depth. The F1/F2/F3 labels are the same as N.

---

## Master factor table: all 12 conditions

| Swap | Condition | F1 | F2 | F3 | What actually translates |
|------|-----------|----|----|-----|--------------------------|
| **N** | CUED Near | CUED | SAME | Near | S2 @ Near |
| **N** | UNCUED Near | UNCUED | DIFFERENT | **Far** | S0 @ Far |
| **N** | CUED Far | CUED | SAME | Far | S2 @ Far |
| **N** | UNCUED Far | UNCUED | DIFFERENT | **Near** | S0 @ Near |
| **ZdA** | CUED Near | CUED | **DIFFERENT** | **Far** | S2 @ Far (swapped out of Near) |
| **ZdA** | UNCUED Near | UNCUED | **SAME** | **Near** | S0 @ Near (swapped into Near) |
| **ZdA** | CUED Far | CUED | **DIFFERENT** | **Near** | S2 @ Near (swapped out of Far) |
| **ZdA** | UNCUED Far | UNCUED | **SAME** | **Far** | S0 @ Far (swapped into Far) |
| **ZdB** | CUED Near | CUED | SAME | Near | S2 @ Near (unchanged) |
| **ZdB** | UNCUED Near | UNCUED | DIFFERENT | **Far** | S0 @ Far (unchanged) |
| **ZdB** | CUED Far | CUED | SAME | Far | S2 @ Far (unchanged) |
| **ZdB** | UNCUED Far | UNCUED | DIFFERENT | **Near** | S0 @ Near (unchanged) |

**Bold** = entries that differ from the naive expectation based on condition label alone.

---

## Factor-level aggregations (DepthSwapCtrl binocular)

From this table, the three factors can be aggregated by pooling across rows:

**F1 (dot cueing):** CUED = {N-CN, N-CF, ZdA-CN, ZdA-CF, ZdB-CN, ZdB-CF}; UNCUED = {N-UN, N-UF, ZdA-UN, ZdA-UF, ZdB-UN, ZdB-UF}

**F2 (depth-field cueing):** SAME = {N-CN, N-CF, **ZdA-UN, ZdA-UF**, ZdB-CN, ZdB-CF}; DIFFERENT = {N-UN, N-UF, **ZdA-CN, ZdA-CF**, ZdB-UN, ZdB-UF}

Note F2 flips for ZdA: ZdA UNCUED contributes to SAME (not DIFFERENT as you might expect), and ZdA CUED contributes to DIFFERENT.

**F3 (translation depth):** Near = {N-CN, N-UF, ZdA-UN, ZdA-CF, ZdB-CN, ZdB-UF}; Far = {N-UN, N-CF, ZdA-CN, ZdA-UF, ZdB-UN, ZdB-CF}

Within both the SAME set and the DIFFERENT set, Near and Far occur in equal numbers (3 Near + 3 Far each), so F3 is orthogonal to F2. Same applies for F3 vs F1.

---

## DepthParam — Factor assignments

DepthParam uses the N (no swap) condition only, at four depth separations (0.03 / 0.05 / 0.10 / 0.15m). Factor assignments are identical to N above; only the disparity magnitude varies. The parametric depth effect is entirely a modulation of F3 (Near vs Far translation depth) and how the gradient strength affects F1 (cue benefit) at each F3 level.

| DepthParam condition | F1 | F2 | F3 |
|---------------------|----|----|-----|
| CUED Far (all depths) | CUED | SAME | Far |
| UNCUED Near (all depths) | UNCUED | DIFFERENT | **Far** |
| CUED Near (all depths) | CUED | SAME | Near |
| UNCUED Far (all depths) | UNCUED | DIFFERENT | **Near** |

The labels "CUED Far" and "UNCUED Near" both have F3=Far (both involve Far translation). The labels "CUED Near" and "UNCUED Far" both have F3=Near (both involve Near translation). Holding F3 constant and comparing F1 (CUED vs UNCUED) gives the cueing effect at each translation depth — the correct comparison that avoids the confound documented in depth_ior_hypothesis.md.

---

## Common labeling confusions

1. **"UNCUED Near" does NOT mean Near translation.** It means the delayed field is Near, which means the NON-delayed field (FieldA, Far) translates. F3=Far.

2. **"UNCUED Far" does NOT mean Far translation.** Delayed field is Far, non-delayed translates at Near. F3=Near.

3. **ZdA CUED conditions have F2=DIFFERENT.** The cued dot (S2) moved out of the delayed field's depth plane before translating. Being "CUED" (F1) does not guarantee "SAME" (F2) when ZdA swaps have occurred.

4. **ZdA UNCUED conditions have F2=SAME.** The non-delayed dot (S0) moved INTO the delayed field's depth plane. Being "UNCUED" (F1) does not guarantee "DIFFERENT" (F2) under ZdA.

5. **ZdB has no effect on factor assignments.** The swap of non-coherent companions (S1↔S3) changes depth-plane grouping signals but not which coherent translator is active at which depth. Every ZdB factor label is identical to N.

---

*Factor assignments derived from gen_hypothetical_traj.py build() function and depthparam_results.md design. Cross-check: master table has 6 CUED + 6 UNCUED = F1 balanced; 6 SAME + 6 DIFFERENT = F2 balanced; 6 Near + 6 Far = F3 balanced. All factors are orthogonal across the 12-condition set.*
