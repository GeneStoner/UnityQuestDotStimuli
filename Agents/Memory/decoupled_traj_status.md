---
name: DecoupledDots trajectory & trace figure status
description: Current state of all schematic trajectory, dot trace, and per-condition performance figures for Exp_DecoupledDots_005m; open issues for next session
type: project
---

## Schematic trajectory figures (time-series) — ALL COMPLETE
4 swap conditions, each a 4-page PDF (2 rows/page), 16 permutations as 8 CUED/UNCUED pairs.
- `Tools/Analysis/decoupled_N_traj.py` → `Agents/Figures/decoupled_N_all_perms.pdf` ✓
- `Tools/Analysis/decoupled_C_traj.py` → `Agents/Figures/decoupled_C_all_perms.pdf` ✓
- `Tools/Analysis/decoupled_Z_traj.py` → `Agents/Figures/decoupled_Z_all_perms.pdf` ✓
- `Tools/Analysis/decoupled_CZ_traj.py` → `Agents/Figures/decoupled_CZ_all_perms.pdf` ✓

Also: `Tools/Analysis/decoupled_dots_traj.py` → `Agents/Figures/decoupled_dots_traj.png`
(4×4 summary: rows=N/C/Z/CZ, cols=CUED-Near/CUED-Far/UNCUED-Near/UNCUED-Far)

## Dot trace figures (physical x-y dot paths) — ALL COMPLETE
4 swap conditions, each a 4-page PDF. Shows all 4 subfields as dot clouds.
- `Tools/Analysis/decoupled_N_traces.py` → `Agents/Figures/decoupled_N_traces.pdf` ✓
- `Tools/Analysis/decoupled_C_traces.py` → `Agents/Figures/decoupled_C_traces.pdf` ✓
- `Tools/Analysis/decoupled_Z_traces.py` → `Agents/Figures/decoupled_Z_traces.pdf` ✓
- `Tools/Analysis/decoupled_CZ_traces.py` → `Agents/Figures/decoupled_CZ_traces.pdf` ✓

### Dot trace figure parameters
- N_DOTS=30 per subfield, RNG_SEED=42, SHOW_FRAMES=[72,74,76,78,80,82,84,86,88]
- Alpha-weighted: early frames faint → later frames opaque
- Filled circles = Near depth plane; Open circles = Far depth plane
- Small gray arrow = translation heading direction
- Color swaps at T_START for C and CZ; fill swaps at T_START for Z and CZ
- Peri-translation interval subtitle on every figure

### Incoherent dot motion (CONFIRMED from Unity StimulusBuilder.cs)
Outside translation window: ALL 4 subfields (S0/S1/S2/S3) rotate together — coherent and incoherent visually identical.
During translation window ONLY:
- Coherent half → `MotionKind.Linear` (heading direction, same speed)
- Incoherent half → `MotionKind.NonCoherent`: same speed, each dot gets one of 8 balanced fixed directions by `dot_index % 8` (N/NE/E/SE/S/SW/W/NW). NOT random repositioning.
Only ONE incoherent subfield fans out per condition: S3 if CUED, S1 if UNCUED.

### Peri-translation interval (all trace figures)
Pre 72–77 (80 ms) · Trans 78–83 (80 ms) · Post 84–89 (80 ms) · 75 Hz · every other frame shown · T₀ = frame 78 (1040 ms post-onset)

## Per-condition performance figure — WORKING, UNDER REVIEW
`Tools/Analysis/decoupled_dots_per_condition.py` → `Agents/Figures/decoupled_dots_per_condition.pdf`
- 4 pages, one per swap condition (N/C/Z/CZ)
- Each page: 2×2 grid; each sub-plot = one stimulus page (2 condition rows)
- Each sub-plot: 4 bars — CUED left pair + UNCUED right pair, spatially matching stimulus figure layout
- One bar per unique condition (no averaging). Dark gray=CUED, light gray=UNCUED. Wilson 95% CI. Chance at 12.5%.
- 4 sessions pooled (2051 valid trials). S2+S3 use invert_cond=True (Inv asset).
- b_green = (DelayedFieldColor=='G') XOR is_inv; b_near = (DelayedFieldDepth=='N') XOR is_inv

**Why:** Raw per-condition performance before factor analysis.
**Next:** Factor-level breakdowns; check S1/S2 vs S3/S4 for anomalies; Near vs Far breakdown.

## DepthColorLinked trajectory figure — DONE (2026-04-09)

`Tools/Analysis/depth_color_linked_traj.py` → `Agents/Figures/depth_color_linked_traj.pdf`
- 2 rows (ZdNoi top, ZdCoh bottom) × 4 cols (Dot✓✗ × Near/Far) — mirrors DecoupledDots layout
- 4 subfield symbols: filled/open circle (Field A coh/noise) + filled/open triangle (Field B coh/noise)
- T(c) and T(n) at separate y-levels on motion axis — field splitting is visible
- `Dot✓/✗  Depth✓/✗  Color✓/✗` title boxes (Color = Depth here, shown for explicit comparison)
- Small info box at T_START: translator Color/Dir/Depth; separate box at ONSET: Field B onset attrs
- Color = depth plane at that frame (Red=Near, Green=Far)

## OPEN ISSUES — resolve at start of next session

### Issue 1: Row label convention — RESOLVED (2026-04-09)
Using translator-centric framing throughout all figures. Labels describe the translating field's properties. This is consistent within each row across CUED/UNCUED panels.
Row labels like "Grn/CW/Far" currently describe the **pre-swap TRANSLATOR's** properties.
- CUED panels: delayed field = translator → label matches both (coincidental)
- UNCUED panels: translator ≠ delayed field → label = translator only; delayed field = complementary (e.g., Red/CCW/Near)
- User observed that labels look like delayed field labels (true for CUED only)
**Decision needed:** Keep translator framing (consistent within each row across CUED/UNCUED) or switch to delayed field framing (consistent within CUED column only)?
**Why it matters:** Color/depth cueing analysis is about translator-at-translation vs delayed field's original properties. Labeling should be unambiguous.

### Issue 2: CZ depth track visual invariance (UNRESOLVED — fix or document)
In `decoupled_CZ_all_perms.pdf`, depth sub-track appears visually unchanged at T_START.
**Root cause:** CZ swaps both color and depth simultaneously. This leaves the color-coded depth configuration invariant: e.g., Red stays at Near and Green stays at Far before AND after T_START (via different fields). Z-only correctly shows lines crossing.
**Options:**
  a) Use field identity (A/B, shown as dash pattern) for depth track coloring → crossing visible
  b) Add T_START marker/annotation indicating swap occurred
  c) Leave as-is and document (CZ is genuinely invariant from color-coded-depth perspective)
**Not yet resolved.**

### Issue 3: Pairing convention (CRITICAL — document clearly)
Each ROWS entry pairs two DIFFERENT permutations:
- CUED entry: (rot_cfg=1, b_green=True, b_near=False) for "Grn/CW/Far"
- UNCUED entry: (rot_cfg=0, b_green=False, b_near=True) for "Grn/CW/Far"
These are complementary permutations that show the same post-onset physical track.
Do NOT confuse with averaging CUED/UNCUED of the same permutation.

## Style conventions (ALL APPROVED)
- Title: `"Unity Asset: Exp_DecoupledDots_005m · <condition> · <type> · Heading = 0°"`
- Subtitle: peri-translation interval line (fontsize=7, color='#444444', y=0.965)
- No superimposed text of any kind
- Green = always dotted (:), Red = always solid (-) in schematic figures
- PDF: 4 pages, 2 rows/page, letter size (8.5×11")
