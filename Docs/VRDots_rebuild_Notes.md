1. Core Architecture Overview

1.1 StimulusConditionsLibrary.cs

Role: Defines abstract stimulus conditions and per-subfield attribute trajectories.

Key ideas:
	•	Four subfields per condition: indices 0–3.
	•	Subfields are just subfields; “field A/B” is not hard-coded, it’s emergent from their attributes.
	•	Each subfield has:
	•	motionKindByFrame (array): None, RotationCW, RotationCCW, CoherentTranslation, NonCoherentTranslation per frame.
	•	colorByFrame (array): Red / Green / etc.
	•	eyeByFrame (array): Left / Right (future: stereo-specific).
	•	depthByFrame (array): Fixation, Near, Far (future: disparity).
	•	visibleByFrame (array): controls delayed onset / on-off.
	•	All arrays indexed by frame, length = timeline.totalFrames.
	•	Conditions are stimulus blueprints, not trial sequences.
	•	Predefined helpers (e.g. cued/uncued) live here or in a helper region, but specifics can be adjusted.

Status:
	•	Structurally in place.
	•	Used by ExpSpecTestPhase + TrialBlockRunner to drive actual motion/color/visibility.
	•	We’ve moved away from ad-hoc “pulse” flags toward explicit per-frame motion kinds.

⸻

1.2 ExperimentSpec.cs

Role: Defines experiment-level constants & trial plan generation.

Includes:
	•	Geometry & timing:
	•	simHz (e.g. 75)
	•	viewDistance_m
	•	apertureRadius_deg, dotSize_deg
	•	rotationSpeed_degPerSec
	•	translationSpeed_degPerSec
	•	translationDuration_ms, delayedOnset_ms, preTranslation_ms
	•	dotsPerField
	•	GetMetersPerDegree()
	•	PlannedTrial:
	•	index, conditionID
	•	headingDeg
	•	onsetFrame, translationStartFrame, translationEndFrame, totalFrames
	•	random seeds for subfields (for reproducible dot layouts).
	•	GetPlannedTrials(Random rng):
	•	Returns a balanced list of trials (e.g. cued / uncued × 8 headings).
	•	Uses library conditions as templates, but directions per trial handled here.

Status:
	•	ExpSpecTestPhase ScriptableObject created as initial concrete spec to mimic Stoner & Blanc logic.
	•	Used by TrialBlockRunner and CsvLogger.

⸻

1.3 StimulusBuilder.cs

Role: The stimulus factory & mover.

Responsibilities:
	•	Owns SubfieldRuntime:
	•	root transform
	•	dots list (Transforms)
	•	color, eye, depth, initialMotion (for reference)
	•	Builds subfields from a condition:
	•	Creates 4 Subfield_* child objects under StimulusRoot.
	•	Spawns dotsPerField / 2 dots per subfield.
	•	Places them uniformly in circular aperture using degrees→meters conversion:
	•	apertureDeg (diameter) → ApertureRadiusMeters.
	•	Provides motion operations:
	•	StepRotation(subfieldIndex, degPerSec, dt, dirSign)
	•	StepTranslation(subfieldIndex, deltaLocalMeters, frame = -1)
	•	StepTranslationBalanced / StepNonCoherentBalanced for non-coherent motion variants.
	•	Logs optional trajectories:
	•	List<TrajectorySample> with frame, subfieldIndex, localPos.

Status:
	•	Confirmed working in Editor:
	•	Dots are visible in Game view.
	•	Rotation & translation ops are callable.
	•	Debug line added:
	•	Logs total dots built per condition when BuildFromCondition is called (Editor & device).

⸻

1.4 TrialBlockRunner.cs

Role: Drives trial sequences and per-frame animation; replaces the old monolithic TrialRunner.

Responsibilities:
	•	On Start() (if autoStartOnPlay):
	•	Requests trials from ExperimentSpec (GetPlannedTrials).
	•	Starts first trial (BeginBlock → NextTrial).
	•	For each trial:
	•	Picks condition (e.g. cued vs uncued).
	•	Calls StimulusBuilder.BuildFromCondition.
	•	Applies per-frame behavior in Update or SimStep:
	•	Evaluates condition’s attribute arrays at current frame.
	•	Calls StepRotation, StepTranslation, non-coherent motion as appropriate.
	•	Manages timing via simFrame (frame counter) & simHz, not random deltaTime.
	•	Coordinates:
	•	CsvLogger (BeginTrial / EndTrial hooks).
	•	StimDebugHUD (shows trial index, heading, timing).

Status:
	•	Runs correctly in Editor.
	•	Logs Trial X/Y and builds conditions.
	•	Needs confirmed execution path on device (Quest) — see “Open Issues”.

⸻

1.5 CsvLogger.cs

Role: Writes session + trial metadata to CSV.

Logs:
	•	Session header:
	•	device info, app version
	•	all ExperimentSpec constants (Hz, geometry, speeds, durations, dotsPerField, etc.)
	•	Per trial:
	•	trialIndex, conditionID, headingDeg
	•	frame indices (onset, translation start/end, totalFrames)
	•	seeds per subfield.

Optional:
	•	Compact per-frame MotionKind rows (if enabled).

Status:
	•	Working in Editor.
	•	File path: Application.persistentDataPath.
	•	Critical for being able to reconstruct stimuli exactly offline.

⸻

1.6 StimDebugHUD.cs

Role: On-screen debug overlay.
	•	Shows:
	•	current trial index / total
	•	condition
	•	heading
	•	frame / totalFrames
	•	key timing info (translation window etc.)

Status:
	•	Attached to TrialController.
	•	Verified in Editor.

⸻

1.7 FrameRateController.cs

Role: Tries to keep a stable target FPS for deterministic timing on desktop.
	•	Disables vSync.
	•	Sets Application.targetFrameRate.
	•	Logs measured FPS every second.

Status:
	•	Working.
	•	On Quest: actual frame rate managed by device; still harmless as monitor.

⸻

2. Current Functional Status

What we know:
	1.	Editor / Game View
	•	uptodatescene:
	•	Contains XR Origin (VR) with Main Camera.
	•	Contains StimulusRoot with StimulusBuilder.
	•	Contains TrialController with TrialBlockRunner, CsvLogger, StimDebugHUD.
	•	With StimulusRoot under Main Camera at (0,0,2):
	•	Dots are visible.
	•	Motion appears.
	•	Trial logs print: [TrialBlockRunner] Trial 1/160: ....
	•	So: core stimulus pipeline is working in-editor.
	2.	On Quest (headset)
	•	App builds & launches.
	•	Only fixation (purple) is clearly visible; no obvious dots.
	•	We have not yet confirmed (via device logs) that:
	•	TrialBlockRunner.Start() is running, and
	•	StimulusBuilder.BuildFromCondition is executing in the deployed player.
	•	Likely causes (to be verified, not assumed):
	•	Startup scene mismatch or missing objects in that scene.
	•	Old harness (VRDotsHandler / legacy objects) still active.
	•	Stimulus exists but too small/low-contrast/additive to notice in HMD.

⸻

3. Open Issues / To-Do (Concise)
	1.	Confirm execution on Quest
	•	Check device logs (Development Build) for:
	•	[TrialBlockRunner] Start() autoStartOnPlay = true
	•	[StimulusBuilder] Built condition '...' with XXX dots total.
	•	If absent → scene / wiring / script not in build.
	•	If present → dots exist; debug visibility.
	2.	Headset Visibility
	•	Temporarily:
	•	Use much larger apertureRadius_deg, dotSize_deg, dotsPerField.
	•	Use solid, high-contrast unlit material (white) instead of subtle additive.
	•	Verify big obvious dot patch is visible in HMD.
	•	Then dial back to Stoner & Blanc values.
	3.	Legacy System Cleanup
	•	Identify & disable:
	•	VRDotsHandler
	•	old ExperimentManager
	•	broken StimulusHUD references
	•	Ensure no duplicate stimulus logic is competing.
	4.	Condition Library Finalization
	•	Encode proper cued/uncued designs as named conditions:
	•	delayed vs undelayed,
	•	rotations CW/CCW,
	•	which subfield(s) translate coherently vs non-coherently.
	•	Match Stoner & Blanc scheme:
	•	~50% coherence via 1 coherent subfield + 1 non-coherent per field.
	•	8 directions balanced across trials.
	5.	Trial Flow & Response Integration
	•	Hook in response collection (button/trigger) into TrialBlockRunner.
	•	Log responses next to each trial entry in CsvLogger.
	•	Add trial advance rules (e.g., wait for response vs fixed ISI).
	6.	Documentation & Hygiene
	•	Remove or quarantine vestigial scripts once the new path is trusted.
	•	Keep this document near the project (e.g., /Docs/VRDots_Rebuild_Notes.md).

⸻

If you drop this into a .md file in the repo, we can use it as the stable reference point next time we dive in.