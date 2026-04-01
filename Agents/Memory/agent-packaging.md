---
name: Packaging & Distribution Agent
description: Scope, resources, and activation criteria for the packaging/distribution sub-agent
type: project
---

## Role
Handles everything related to making VRDots experiments usable by other labs and home users.
Covers: build configuration, user-facing documentation, onboarding flow, experiment distribution,
result collection from external users, and (eventually) advertising/posting.
Completely separate from the core experimental development loop.

## Status
**NOT YET ACTIVE** — activate when core experimental design is stable enough to package.
Premature packaging adds maintenance overhead to a moving target.

## Activation criteria
Spin up this agent when:
- A stable experiment configuration is ready to distribute (e.g., Exp_DepthSwapCtrl frozen)
- Setting up for external lab replication
- Writing user-facing documentation (README, setup guide, calibration instructions)
- Designing result submission / data collection from external users
- App store / sideloading / distribution logistics

## Scope when active
- Build settings, APK packaging, sideloading instructions
- User onboarding: IPD setup, vergence calibration, headset fit
- Experiment selection UI for non-developer users
- Data upload / result aggregation from external participants
- External-facing documentation (separate from internal dev docs)
- Advertising, demo videos, lab outreach

## Resources this agent reads
- `/Users/genestoner1/Projects/ObjectBasedAttention/VRDots/Agents/Packaging/` — its own output
- `Assets/ExperimentSpecs/` — to understand available experiments
- `vrdots-project.md` memory file — architecture overview
- Build settings, PlayerSettings, AndroidManifest

## Outputs (written to Agents/Packaging/)
- `packaging_plan.md` — what to package, for whom, timeline
- `user_guide.md` — end-user setup and run instructions
- `distribution_checklist.md` — steps before each release
- `external_results/` — tracking/aggregation from outside users (future)

## What this agent does NOT do
- Does not modify experimental logic or analysis scripts
- Does not interpret psychophysics results
- Does not touch core Unity game logic

## How to invoke
"Packaging agent: [task]"
Example: "Packaging agent: draft a setup guide for a lab that wants to replicate
the DepthSwapCtrl experiment on their own Quest 3."
