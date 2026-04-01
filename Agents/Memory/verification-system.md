# Verification System

## Method A — Python Reference Comparison (verify_trajectories.py)
- Location: `Tools/Analysis/verify_trajectories.py`
- Re-implements `BuildEffectiveCondition()` in pure Python, independently of C#
- For each sidecar trajectory entry: generates expected mk_payload + color_payload, computes FNV-1a-32 hashes, compares against stored values
- Reads timing from sidecar `experiment_spec` section when available; falls back to defaults (80ms translation); last resort: infers from payload content
- Supports all swap types: N, M, C, MC, D (and combinations)
- Results to date: 128/128 MotionSwap, 128/128 Dots50Swap, 64/64 Baseline — all passed

## Method B — Runtime C# Audit (always-on)
- `CsvLogger.VerifyTrialTrajectory(stimKey, mkPayload, colorPayload)` — looks up registered trajectory, computes runtime hash, compares
- `TrialBlockRunner.AuditTrajectory()` — called in both `FinalizeTrialAndAdvance_NoResponse()` and `FinalizeTrialAndAdvance_WithResponse()` before `EndTrial()`
- Logs `Debug.LogError` (red in Unity console) on mismatch
- Zero cost: one FNV-1a-32 hash per trial

## Method C — Visual Pseudo-Session (verify_trajectories.py --plots)
- Generates trajectory plots for ALL unique (cond, rotCfg, delColor, swap) shapes
- Single-row layout with colored scatter markers per subfield
- Marker specs: S0=filled circles (s=22), S1=unfilled squares (s=48, lw=1.5), S2=filled triangles (s=26), S3=unfilled diamonds (s=56, lw=1.5)
- Color map: R→"#CC3333", G→"#228B22", K→skip (invisible)
- Includes phase markers (onset, tStart, tEnd) and translation window shading
- Same marker style used across all 3 Python scripts (analyze, verify, generate_reference)

## Reference Trajectory Diagrams (generate_reference_trajectories.py)
- Location: `Tools/Analysis/generate_reference_trajectories.py`
- Generates schematic diagrams from design spec (not from data)
- Shows No-Swap (N), Motion-Swap 100% (M), 50% Dot-Swap (D)
- Uses actual timing: onset=56, tStart=78, tEnd=84, total=114 (75Hz, 80ms translation)
- Canonical trial: CUED, Rot0 (A=CW, B=CCW), DelayedFieldColor=R

## Output Locations
All in `/Users/genestoner1/Library/Application Support/ThatsRandom/VRDotsDataFiles/`:
- `reference_trajectories.png` — schematic diagrams (N, M, D)
- `vr_dots_session_*_verification_plots.png` — per-session all-shapes verification
- `vr_dots_session_*_trajectory_examples.png` — per-session 6 balanced examples

## FNV-1a-32 Hash
- Used for trajectory cross-checking between sidecar (planned) and TSV (runtime)
- Implementation: CsvLogger.Fnv1a32() in C#, fnv1a_32() in Python
- Offset basis: 0x811C9DC5, Prime: 0x01000193
- Operates on UTF-8 bytes of payload string
