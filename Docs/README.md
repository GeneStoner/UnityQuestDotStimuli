# VRDots Documentation
*Index of the experiment docs, how to keep them up to date, and known overlaps. 2026-09-17.*

All current experiment documentation lives in this `Docs/` folder of the repository, as Markdown. These files are the single source: edit them here, and make PDFs or Word files only when sending a copy to someone.

## The docs

| Doc | Focus | Audience |
|---|---|---|
| [handbook.md](handbook.md) | Setup, running an experiment (density series example), making new specs, data files, analysis, where data should live, learning the project with Claude Code | Anyone running experiments |
| [stimulus_verification.md](stimulus_verification.md) | Checking the stimulus is what we intend at three levels (build, rendering, delivery to the eye); blur and pixelation; keeping both sites identical; checklists | Anyone running experiments; co-authors |
| [subject_experimenter_instructions.md](subject_experimenter_instructions.md) | Part 1: the task as explained to observers. Part 2: flicker calibration and running a session | Observers and experimenters |
| [experiment_catalog.md](experiment_catalog.md) | Every experiment run so far: parameters, sessions, results | Co-authors; analysis |
| [psychophysics_limitations_and_mitigations.md](psychophysics_limitations_and_mitigations.md) | Known limits of Unity and Quest 3 for psychophysics (e.g. vergence–accommodation conflict) and what we do about them. Last updated 2026-04-17 | Co-authors |
| [VRDots_rebuild_Notes.md](VRDots_rebuild_Notes.md) | Code architecture notes: how conditions and subfield trajectories are defined | Programmers |

**Background write-ups** (in `Agents/`, not collaborator docs):

| Doc | Focus |
|---|---|
| `Agents/depth_artifacts_writeup.md` | The depth-experiment artifacts found and fixed in April 2026, and which data to exclude |
| `Agents/cueing_effect_ranking.md` | Cueing effects ranked across the clean experiments |
| `Agents/Packaging/rendering_explainer.md` | How dots were rendered in April 2026 and the screen-space approach adopted since |

## How to update

- **Edit in one place.** On GitHub, open the file and click the pencil icon; or edit locally and commit. Git records every change and who made it.
- **Link, don't copy.** Each topic has one home (setup → handbook; stimulus checks → verification; results → catalog). Other docs link to it rather than repeating it.
- **Say what changed** in the commit message, e.g. "handbook: 63-dot spec now 0.12° dots".
- **For changes co-authors should review,** edit on a branch and open a pull request.
- **Update docs with the code.** When a spec, setting or logged field changes, update the doc in the same commit. Claude Code can do this: "Update Docs/ to reflect this change."
- **To share a copy:** `python3 Tools/docs_export.py Docs/handbook.md handbook.docx` makes a compact Word file (opens in Pages). Don’t commit the exports; they go out of date.

## Redundancies and cleanup

**Replaced by the handbook, to be deleted** (their content is merged; they stay in git history):

- `Agents/Packaging/turkey_lab_setup.md` / `.docx`
- `Agents/Packaging/turkey_quickref.md` / `.pdf`
- `Agents/Packaging/lab_transfer_guide.md` (April 2026)
- `Agents/Packaging/data_files_guide.md` / `.pdf`
- `Agents/Packaging/VRDots_Collaborator_Handbook.md` / `.docx` (draft)

**Moved into `Docs/`, old copies to be deleted:**

- `Agents/experiment_asset_catalog.md` / `.docx` → `experiment_catalog.md`
- `Agents/Packaging/subject_experimenter_instructions.md` / `.pdf`
- `Agents/Packaging/VRDots_Stimulus_Verification.md` / `.docx` (draft)

**Overlaps and dated content to review:**

- `Agents/Packaging/collaborator_brief_HK.md` (April 2026): its depth results predate the April artifact fixes and should not be circulated. Its setup section is superseded by the handbook.
- `psychophysics_limitations_and_mitigations.md` overlaps section 3 of `stimulus_verification.md` (display and delivery) and predates the September rendering changes. Merge the parts still true, or mark it historical.
- `rendering_explainer.md` describes the April 2026 sphere rendering; the stimulus now uses screen-space shaders. Keep as history.
- `cueing_effect_ranking.md` and `depth_artifacts_writeup.md` repeat numbers that are also in the catalog; the catalog should be the one place results are updated.
- Stale status files at the repository root: `QUEST_STATUS_2026-01-17.md`, `QUEST_WORK_STATUS_2026-01-15.md`, `NONIUS_STATUS.md`, `todo.md`.
- Older dot size: only the 173-dot density spec uses 0.12° dots; other density specs still use 0.08°.

**Privacy:** this repository is public, and session data files are committed under `Agents/Data/`. Decide whether data belongs in a separate private repository.
