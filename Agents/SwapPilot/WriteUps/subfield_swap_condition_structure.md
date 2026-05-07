# SubfieldSwap Condition Structure (N = no-swap baseline)

## Setup

The experiment has one fixed structural asymmetry: **one field always has a delayed onset** (`delayTranslator=1` in asset). Call that field the **delayed field**; the other is the **always-on field**.

Three binary variables are counterbalanced across trials:

| Variable | Values | Controls |
|---|---|---|
| `rotConfig` | 0 or 1 | Which rotation direction the delayed field gets |
| `delayedFieldColor` | Red or Green | Color of delayed field (balanced by `balanceDelayedFieldColor=1`) |
| `isCued` | true or false | Whether delayed field translates (CUED) or always-on field translates (UNCUED) |

Translation direction (8 directions, k%8) is also balanced within each trial type.

---

## The 8 conditions (fixed translation direction; N = no-swap)

Written in terms of **observable stimulus properties only** — Field A/B labels suppressed.

| # | Translator rotation | Translator color | Translator onset | Other-field rotation | Other-field color | Code label |
|---|---|---|---|---|---|---|
| 1 | CCW | Red | **delayed** | CW | Green | CUED |
| 2 | CW | Green | **always-on** | CCW | Red | UNCUED |
| 3 | CCW | Green | **delayed** | CW | Red | CUED |
| 4 | CW | Red | **always-on** | CCW | Green | UNCUED |
| 5 | CW | Red | **delayed** | CCW | Green | CUED |
| 6 | CCW | Green | **always-on** | CW | Red | UNCUED |
| 7 | CW | Green | **delayed** | CCW | Red | CUED |
| 8 | CCW | Red | **always-on** | CW | Green | UNCUED |

All 8 conditions are present in the current experiment.

---

## Natural CUED / UNCUED pairs

Pairs where the two fields are **identical in rotation and color**; only which field had delayed onset differs. Everything visible after delayed onset is held constant within a pair.

| Pair | CUED trial | UNCUED trial | Translator | Other field |
|---|---|---|---|---|
| A | #1 | #8 | CCW Red | CW Green |
| B | #5 | #4 | CW Red | CCW Green |
| C | #3 | #6 | CCW Green | CW Red |
| D | #7 | #2 | CW Green | CCW Red |

These pairs are useful for illustration but the analysis does not need to use them explicitly (see below).

---

## How the analysis works

**CUED accuracy** = % correct pooled over all `isCued=true` trials (conditions #1, 3, 5, 7) across all 8 translation directions.

**UNCUED accuracy** = % correct pooled over all `isCued=false` trials (conditions #2, 4, 6, 8) across all 8 translation directions.

This is correct and unconfounded because:
- Within CUED trials: CW and CCW translators appear equally; Red and Green translators appear equally.
- Within UNCUED trials: same balance.
- So rotation direction and color cannot drive a CUED vs UNCUED difference.

The pair structure confirms *why* the pooled comparison is clean: each CUED trial has a matched UNCUED trial (its pair partner) with identical post-onset stimulus. But the pairs do not need to be analyzed separately — pooling achieves the same balance automatically.

---

## Why the Field A / B distinction doesn't matter

"Field A" and "Field B" are internal code labels. What matters perceptually is:

- **Rotation direction** of each field (CW vs CCW)
- **Color** of each field (Red vs Green)
- **Onset timing** of each field (always-on vs delayed)
- **Whether a field translates** at tStart

With `rotConfig` and `delayedFieldColor` both balanced, the delayed field takes each combination of (CW/CCW) × (Red/Green) equally often. Field B being structurally fixed as the delayed field is implementation detail only; the resulting stimulus set is fully symmetric with respect to observable properties.

---

## What WOULD be missing (for completeness)

The `delayTranslator=1` constraint means **always-on field = Field A** always. The experiment does not run conditions where Field A is delayed and Field B is always-on. However, since color and rotation are fully counterbalanced within the existing structure, **this omission does not create a stimulus confound** — every observable (rotation, color, onset timing, translation) is balanced. Adding `delayTranslator=false` conditions would double trial count without changing the inferential logic.

---

## Swap conditions (D and Da)

The same 8-condition structure repeats for D (Dots50 swap: Sub1↔Sub3 at tStart) and Da (Dots50A swap: Sub0↔Sub2 at tStart). The swap changes which subfield's dots physically join which rotating stream after tStart, but the CUED/UNCUED balance and the pooled-vs-paired analysis logic are identical.
