# VRDots To-Do List
*Last updated: 2026-04-01*

---

## Data Collection

- [ ] Run at least 2 more binocular sessions (Near effect at † level; need n≥192/cell to firm up)
- [ ] Run more monocular sessions, both eyes — session variance large at n=64/cell per eye; aim for n≥128/cell per eye
- [ ] Consider dedicated Near vs Far session to confirm Factor 3 asymmetry

---

## Stimulus / Software

### Fixation & Vergence
- [ ] **True dichoptic nonius lines** — try Multiview stereo mode + shader discard (Option A, lower effort) before OVR Compositor Layers (Option B, canonical Meta XR SDK approach)
- [ ] **Minimum pre-trigger vergence hold** (Mod 3) — require stable vergence for N ms before trial starts (not yet designed)
- [ ] **Fixation training stage** (see Catak et al., `Agents/Literature/catak2022_fixation_methods.md`):
  - Implement two-target diagnostic: center target + 0.6° peripheral, both at individually calibrated contrast threshold
  - Key metric: central > peripheral = fixating; losing both or no pattern = non-fixating
  - Three-stage funnel: (1) fixation training → (2) translation discrimination practice → (3) main experiment
  - Expect ~25% of naïve subjects to need extended training or multiple attempts at Stage 1 — build retry tolerance in
  - Note: training measurably improved main-experiment performance in Catak data, so even borderline-passing subjects benefit from longer training blocks

### Trial Structure
- [ ] **Both-field preview during WaitingForStart** — show S2/S3 at frame-0 positions (alongside existing Field A preview) to allow vergence/depth stabilization before onset; delayed field then vanishes at frame 0 as usual
- [ ] **Practice trials** — add `numPracticeTrials` to ExperimentSpec; mark first N trials as `isPractice`; log `is_practice=1` in TSV; exclude from analysis automatically
- [ ] **Matched CUED/UNCUED dot layouts** — use same seed for CUED and UNCUED within each (heading × swap × depth × rotation) tuple so dot positions from delayed onset onward are identical; only which sub-array carries coherent translation differs. Pro: removes chance variation in translation difficulty between CUED and UNCUED. Con (observer exploitation): weak — trials are randomly interleaved and the translation burst is too brief to consciously track. **Deeper problem**: matching is appropriate for N but not cleanly applicable across ZdA/ZdB where swap mechanics act on the dot field itself — applying it selectively to N only would introduce an inconsistency in the noise floor across swap conditions, which could confound the N vs ZdA vs ZdB comparison. Uniform noise across all conditions is preferable to selectively reduced noise in a subset. **Tentative verdict: don't do it.** Keep as a note; revisit only if a clean implementation across all swap types can be designed.

### Gamification (for "wild" / home use)
- [ ] **Stage 1 — Fixation calibration game**: contrast-threshold task with central/peripheral targets; pass/retry gate; maps onto Catak training funnel
- [ ] **Stage 2 — Translation spotting game**: discrimination practice (Catak Stage 2 equivalent); unlock gate to main experiment
- [ ] **Stage 3 — Main cueing experiment**: could frame as "find the hidden motion" game
- [ ] Design retry flow and progress indicators for each gate (~25% of users will need multiple attempts at Stage 1)
- [ ] Coordinate with Packaging agent when ready to distribute

---

## Analysis

- [ ] Update `three_factors_bino_vs_mono.png` and `depthswapctrl_all_sessions_bars.png` after each new session batch
- [ ] Add depth column support to `analyze_vr_dots_v2.py` (backburner — low priority)
- [ ] Consider session-level mixed-effects model once n-per-session is large enough
- [ ] Update `Agents/Literature/experiment_status.md` after each new session

## Visualization (`plot_dot_traces.py`)

- [ ] **Match Unity RNG exactly** — implement Xorshift128 in Python with `session_seed` from sidecar (S0/S1 seed = session_seed, S2/S3 seed = session_seed + 99991) so traces show exact dot layouts from real trials, not representative ones
- [ ] **Multi-panel figure** — extend to 3×2 grid (N/ZdA/ZdB × CUED/UNCUED) as a single script output
- [ ] **Split by depth plane** — optional two-aperture layout (Near | Far) as `--layout split` flag

---

## Literature Agent

- [ ] Work through `Agents/Literature/pending_papers.md` — remaining Stoner and related papers (14 items)
- [ ] Expand `Agents/Literature/modeling_lit.md` with additional computational accounts
- [ ] Update `Agents/Literature/theory_doc.md` Section 4.2 — monocular confound framing now refined by both-eye monocular data
- [ ] Best run in a separate window: invoke as "Literature agent: [question]"

---

## Modeling Agent (Pinned — future)

- [ ] Activate when experimental findings are stable enough to constrain a model
- [ ] Candidate model classes: motion coherence detector with depth-plane weighting, object-based attention (biased competition), Bayesian observer, neural pipeline
- [ ] Model must account for: dot cueing (bino + mono), depth-field cueing (bino + mono), ZdB enhancement, ZdA attenuation, Near/Far asymmetry (bino only)

---

## Admin / Backup

- [ ] After each session batch: copy updated memory files to `Agents/Memory/` and commit+push
- [ ] Save key figure PNGs somewhere permanent (currently only in /tmp/ between sessions — regenerate from committed scripts or copy to `Agents/Figures/`)
- [ ] Session TSV/sidecar data: currently in `~/Library/Application Support/ThatsRandom/VRDotsDataFiles/` (local only) — confirm Time Machine covers this path
- [ ] Commit `wip/quest-pilot` to GitHub at end of each work session

---

## Done ✓

- [x] ZdA and ZdB swap conditions implemented
- [x] `Exp_DepthSwapCtrl` asset (N/ZdA/ZdB, same color, 0.05m depth, 192 trials)
- [x] `verify_trajectories.py` color hash fix (nd_col hardcoded bug → reads from stored payload)
- [x] 192/192 trajectory verification passing for all 8 sessions
- [x] Three-factor analysis framework (dot cueing, depth-field cueing, depth plane Near/Far)
- [x] Binocular vs monocular master summary (n=768 bino, n=769 mono)
- [x] `three_factors_bino_vs_mono.png` and `depthswapctrl_all_sessions_bars.png` generated
- [x] Literature agent scaffolding and initial outputs (`theory_doc.md`, `experiment_status.md`, `pending_papers.md`, `modeling_lit.md`)
- [x] Catak 2022 fixation methods digested (`catak2022_fixation_methods.md`)
- [x] Packaging agent and Modeling agent scopes defined (not yet active)
- [x] All session data consolidated to permanent Mac local folder
- [x] Memory files backed up to `Agents/Memory/` on GitHub
- [x] Nonius lines plan documented (in `.claude/plans/`) — not yet implemented
