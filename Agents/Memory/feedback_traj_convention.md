---
name: Trajectory figure CUED/UNCUED visual convention
description: CRITICAL rule for all DecoupledDots trajectory figures — CUED and UNCUED panels must be visually identical except during the translation window
type: feedback
---

CUED and UNCUED panels for the same permutation must be **visually identical** in every frame **except during the translation window [T_START, T_END)**. They share the same line colors, line styles, and y-positions in every segment outside the translation window.

**The three segments:**
1. **Pre-onset** (frames 0 to ONSET-1): Field A solid at its rotation level (CW or CCW). Field B dotted is ABSENT (nan/not plotted). — IDENTICAL in CUED and UNCUED.
2. **Onset to tStart** (frames ONSET to T_START-1): Field A solid at its rotation level. Field B dotted at its rotation level (opposite to A). — IDENTICAL in CUED and UNCUED.
3. **Translation window** (frames T_START to T_END-1): CUED → Field B dotted dips to TRANS level; UNCUED → Field A solid dips to TRANS level. — THE ONLY DIFFERENCE.
4. **Post-translation** (frames T_END onward): Both fields back at rotation levels. — IDENTICAL again.

**Line encoding (fixed for all conditions):**
- Field B (delayed onset) = dotted line style (`:`)
- Field A (always-on) = solid line style (`-`)
- Color = actual dot color of that field in the stimulus: Near=Red (#CC3333), Far=Green (#228B22)
- Field B color depends on `b_near` flag for the permutation

**Template:** S&B Fig 5 panels A (CUED) and C (UNCUED) — identical pre-onset, identical onset-to-tStart, only differ at translation window.

**Why:** The user has stated this requirement ~10 times. Any code that makes CUED and UNCUED panels look different OUTSIDE the translation window is wrong. The panels should be "paired" so a viewer can immediately see the single difference.

**How to apply:** When generating code, verify: for the pre-onset segment the only line present is Field A solid. For onset-to-tStart both lines present at same y-values in CUED and UNCUED. Only at T_START do the panels diverge.
