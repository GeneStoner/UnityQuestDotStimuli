# Factor group membership — DecoupledDots conditions
*Reference for interpreting factor performance figure bars*

## The 8 conditions and their factor assignments

| Condition | Dot | Depth | Color |
|-----------|-----|-------|-------|
| CUED+N    | ✓   | ✓     | ✓     |
| CUED+C    | ✓   | ✓     | ✗     |
| CUED+Z    | ✓   | ✗     | ✓     |
| CUED+CZ   | ✓   | ✗     | ✗     |
| UNCUED+N  | ✗   | ✗     | ✗     |
| UNCUED+C  | ✗   | ✗     | ✓     |
| UNCUED+Z  | ✗   | ✓     | ✗     |
| UNCUED+CZ | ✗   | ✓     | ✓     |

---

## Panels A–C: cued ✓ vs cued ✗ arms for each factor

### A. Dot cueing
| Bar | Conditions | Mix |
|-----|-----------|-----|
| Dot✓ (CUED) | CUED+N, CUED+C, CUED+Z, CUED+CZ | 50% Depth✓, 50% Color✓ |
| Dot✗ (UNCUED) | UNCUED+N, UNCUED+C, UNCUED+Z, UNCUED+CZ | 50% Depth✓, 50% Color✓ |

### B. Depth-field cueing
| Bar | Conditions | Mix |
|-----|-----------|-----|
| Depth✓ | CUED+N, CUED+C, UNCUED+Z, UNCUED+CZ | 50% Dot✓, 50% Color✓ |
| Depth✗ | CUED+Z, CUED+CZ, UNCUED+N, UNCUED+C | 50% Dot✓, 50% Color✓ |

### C. Color-field cueing
| Bar | Conditions | Mix |
|-----|-----------|-----|
| Color✓ | CUED+N, CUED+Z, UNCUED+C, UNCUED+CZ | 50% Dot✓, 50% Depth✓ |
| Color✗ | CUED+C, CUED+CZ, UNCUED+N, UNCUED+Z | 50% Dot✓, 50% Depth✓ |

**Note**: All three factors are perfectly balanced within each arm of every other factor (orthogonal design). This is why the GLM coefficients are unconfounded.

---

## Panels D–F: pairwise comparisons of cued arms

### D. Dot-cued ✓ vs Depth-cued ✓
| Bar | Conditions | Dot mix | Depth mix |
|-----|-----------|---------|-----------|
| Dot✓ | CUED+N, CUED+C, CUED+Z, CUED+CZ | 100% Dot✓ | 50% Depth✓ |
| Depth✓ | CUED+N, CUED+C, UNCUED+Z, UNCUED+CZ | 50% Dot✓ | 100% Depth✓ |

Expected gap (additive model) = ½(F1 − F2) = ½(22.3 − 12.5) = **4.9pp**
Observed ≈ 3.6pp. Gap is SMALL because F2 is large — Depth✓ group is boosted toward Dot✓ level.

### E. Dot-cued ✓ vs Color-cued ✓
| Bar | Conditions | Dot mix | Depth mix | Color mix |
|-----|-----------|---------|-----------|-----------|
| Dot✓ | CUED+N, CUED+C, CUED+Z, CUED+CZ | 100% Dot✓ | 50% Depth✓ | 50% Color✓ |
| Color✓ | CUED+N, CUED+Z, UNCUED+C, UNCUED+CZ | 50% Dot✓ | 50% Depth✓ | 100% Color✓ |

Expected gap (additive model) = ½F1 = **11.2pp**
Observed ≈ 7.3pp. Gap exists entirely because Color✓ group is only 50% Dot✓. Color cueing itself adds nothing (F3=0).

### F. Depth-cued ✓ vs Color-cued ✓
| Bar | Conditions | Dot mix | Depth mix |
|-----|-----------|---------|-----------|
| Depth✓ | CUED+N, CUED+C, UNCUED+Z, UNCUED+CZ | 50% Dot✓ | 100% Depth✓ |
| Color✓ | CUED+N, CUED+Z, UNCUED+C, UNCUED+CZ | 50% Dot✓ | 50% Depth✓ |

Expected gap (additive model) = ½F2 = **6.25pp**
Observed ≈ 3.6pp. Depth✓ wins because it contains 100% Depth✓ vs only 50% in Color✓.

---

## Interaction evidence (residuals from additive model, B≈12.8%)

| Condition | Additive prediction | Observed (S1+S2) | Residual |
|-----------|--------------------|--------------------|----------|
| CUED+N    | 47.6% | ~43% | −4.6pp |
| CUED+C    | 47.6% | ~49% | +1.4pp |
| CUED+Z    | 35.1% | ~28% | **−7.1pp** |
| CUED+CZ   | 35.1% | ~20% | **−15.1pp** |
| UNCUED+N  | 12.8% | ~22% | +9.2pp |
| UNCUED+C  | 12.8% | ~20% | +7.2pp |
| UNCUED+Z  | 25.3% | ~20% | −5.3pp |
| UNCUED+CZ | 25.3% | ~20% | −5.3pp |

Key: CUED+Z and CUED+CZ fall **below** additive prediction → negative Dot×Depth interaction.
Depth swap suppresses dot cueing beyond the additive cost of losing F2.
Color swap alone (C) shows no interaction.
