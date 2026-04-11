---
name: Stoner & Blanc 2010 — PDF location and key figures
description: Local PDF path and page numbers for figures in the core VRDots paper
type: reference
---

**File**: `/Users/genestoner1/Documents/MATLAB/TurkeyResearchII/exploringmechansimsStonerBlanc.pdf`

Vision Res. 2010 Jan 25; 50(2):229. "Exploring the mechanisms underlying surface-based stimulus selection." Gene R. Stoner & Georgina Blanc.

## Key figure pages

| Figure | Page | Content |
|--------|------|---------|
| Fig 1A | 19 | Conventional depiction — snapshots of dot fields rotating and translating over time (CUED vs UNCUED rows) |
| Fig 1B | 19 | Feature-based depiction — CW/TRANS/CCW tracks over time; green dotted = delayed field, red solid = non-delayed; V-dip = translation; CUED: delayed field dips; UNCUED: non-delayed field dips |
| Fig 2 | 20 | Two-translation design (Valdes-Sosa 2000) — same format |
| Fig 3 | 22 | Motion-competition model responses |
| Fig 4 | 23 | 6 conditions Exp 1: Left=no-motion-swap, Right=motion-swap; Rows A/C=delayed onset CUED/UNCUED, Row E=common onset |
| Fig 5 | 24 | 8 conditions Exp 2 (adds color-swap): same layout + color-swap rows |

## VRDots mapping (from Fig 1B convention)
- Green dotted line (delayed field) → Field B: S2 (coherent) + S3 (noise)
- Red solid line (non-delayed field) → Field A: S0 (coherent) + S1 (noise)
- CUED = delayed dots translate (S2 gets the V-dip)
- UNCUED = non-delayed dots translate (S0 gets the V-dip)
- Fig 1B format is exactly what `gen_hypothetical_traj.py` and `depthparam_trajectories.py` replicate
