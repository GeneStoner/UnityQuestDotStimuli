# Interpolation in Moving Random Dot Patterns: Studies and Evidence
*Prepared 2026-05-28*

Evidence comes from several distinct but converging angles. Organized below by theme.
PMIDs given where confirmed by search; items marked ⚠️ need independent verification.

---

## 1. Spatiotemporal Filter Models — Motion Detection as Integration

The most fundamental sense in which RDKs involve interpolation: direction-selective motion detectors are spatiotemporal filters that integrate the image over a volume in (x, y, t) space. They do not compare two instantaneous frames; they "fill in" between discrete dot positions across their passband.

**Watson, A.B. & Ahumada, A.J. (1985).** Model of human visual-motion sensing. *Journal of the Optical Society of America A*, 2, 322–342.
The foundational linear spatiotemporal filter model of motion detection. Filters integrate over a spatiotemporal extent — not a snapshot — and the model correctly predicts performance on apparent motion and drifting stimuli. Perceived motion from discrete dot positions arises from this continuous spatiotemporal integration. DOI: 10.1364/JOSAA.2.000322

**Adelson, E.H. & Bergen, J.R. (1985).** Spatiotemporal energy models for the perception of motion. *Journal of the Optical Society of America A*, 2, 284–299. [PMID: 3973762]
A moving image is an oriented pattern in (x, y, t) space; velocity = spatiotemporal orientation. The motion energy signal is an integral over a spatiotemporal volume — the detector explicitly fills in the trajectory between frames. Remains the dominant low-level motion model; predicts that discrete dot positions will be interpolated whenever they fall within the filter's passband.

**Burr, D.C. & Ross, J. (1982).** Contrast sensitivity at high velocities. *Vision Research*, 22, 479–484. [PMID: 7112947]
Peak spatial-frequency sensitivity slides with velocity, maintaining ~10 Hz temporal sensitivity. A "sliding window" consequence of spatiotemporal filter tuning: the filter samples the trajectory, not a frame. Sets constraints on which spatial frequencies in a dot pattern drive smooth motion versus strobed/aliased percepts.

**Watson, A.B., Ahumada, A.J. & Farrell, J.E. (1986).** Window of visibility: a psychophysical theory of fidelity in time-sampled visual motion displays. *Journal of the Optical Society of America A*, 3, 300–307.
Derives the frame rate above which temporal sampling is perceptually invisible (smooth interpolation). Below the threshold, aliased copies fall inside the window of visibility and strobing is seen. For random dot stimuli, this defines the regime in which the visual system seamlessly interpolates between dot-position updates. DOI: 10.1364/JOSAA.3.000300

---

## 2. Motion Streaks — Spatial Interpolation of Fast-Moving Dots

When a dot moves fast enough, temporal integration within the visual system smears it into an oriented spatial trace — a "streak" — aligned with the direction of travel. Orientation-tuned V1 cells read direction from this spatial interpolant, providing a second coding channel alongside pure motion-energy detectors.

**Geisler, W.S. (1999).** Motion streaks provide a spatial code for motion direction. *Nature*, 400, 65–69. [PMID: 10403249]
Orientation-masking with random dot kinematograms: direction discrimination is selectively impaired by noise oriented *parallel* to the motion direction, proving that V1 orientation-selective cells read out the streak signal. Fast-moving dots leave a spatial interpolant encoding direction — complementing and resolving ambiguities in pure motion-energy detectors.

**Geisler, W.S., Albrecht, D.G., Crane, A.M. & Stern, L. (2001).** Motion direction signals in the primary visual cortex of cat and monkey. *Visual Neuroscience*, 18, 501–516.
Neurophysiological confirmation: V1 neurons respond more strongly when the direction of travel is parallel to their preferred orientation. For fast stimuli, preferred direction and preferred orientation align — the direct neural substrate for streak-based spatial interpolation of motion direction. ⚠️ Verify PMID independently.

**Krekelberg, B., Dannenberg, S., Hoffmann, K.P., Bremmer, F. & Ross, J. (2003).** Neural correlates of implied motion. *Nature*, 424, 674–677.
Static images implying motion (photographs showing blur streaks) activate direction-selective MT/V5 in humans (fMRI). Orientation-based spatial interpolation of motion streaks recruits the same cortical motion machinery as real motion. DOI: 10.1038/nature01852

---

## 3. Limits of Spatial Interpolation — Psychophysical Measurements

**Burr, D.C. (1979).** Acuity for apparent vernier offset. *Vision Research*, 19, 835–837. [PMID: 483604]
A bar moves in discrete spatial steps; if upper and lower halves are presented at slightly different times, the bar appears spatially offset. Acuity for detecting this illusory vernier offset is nearly as fine as for a real static offset. The visual system interpolates intermediate positions the stimulus never actually occupied — incompatible with frame-by-frame comparison, requires spatiotemporal integration along the trajectory.

**Burr, D.C. (1980).** Motion smear. *Nature*, 284, 164–165. [PMID: 7360241]
Moving objects produce far less perceived smear than the retinal streak would predict. Integration along the spatiotemporal trajectory both produces the motion signal and "deblurs" the image. Motion detectors perform temporal interpolation as a functional consequence of their filter architecture.

**Morgan, M.J. & Watt, R.J. (1983).** On the failure of spatiotemporal interpolation: a filtering model. *Vision Research*, 23, 997–1004. [PMID: 6649445]
Measures limits of interpolation using a vernier-in-motion paradigm. Interpolation is fully efficient (100% of static sensitivity) when inter-station spacing is less than ~3–4 arcmin; efficiency declines sharply beyond that. Provides the critical spatial limits on how far the visual system can bridge discrete dot positions — a direct constraint on apparent motion in RDKs.

---

## 4. Apparent Motion — Active Trajectory Construction

When a dot jumps from A to B, the visual system constructs an interpolated trajectory. The choice of path is not arbitrary — it is constrained by physical plausibility, featural similarity, and biological knowledge.

**Ramachandran, V.S. & Anstis, S.M. (1983).** Perceptual organization in moving displays. *Nature*, 304, 529–531.
Ambiguous four-dot apparent motion: the visual system uses feature similarity (color, luminance, size) to constrain correspondence — deciding which dot "goes where" and thus determining the interpolated path. Trajectory interpolation is tied to object identity. ⚠️ Verify PMID independently.

**Shepard, R.N. & Zare, S.L. (1983).** Path-guided apparent motion. *Science*, 220, 632–634.
Apparent motion follows a physically constrained path (around a barrier or along a curve) even though no signal is present along that path. The visual system constructs an interpolated trajectory consistent with physical constraints, not just the shortest Euclidean displacement — implying an internal model that fills in paths rather than relying solely on input signals. ⚠️ Verify PMID independently.

**Shiffrar, M. & Freyd, J.J. (1990).** Apparent motion of the human body. *Psychological Science*, 1, 257–264.
At short SOAs, apparent motion of body photographs follows the geometrically shortest path even if it passes through the body (violating anatomy). At longer SOAs, the system switches to the biomechanically possible path. Active, knowledge-guided spatial interpolation — not passive frame matching.

**Shiffrar, M. & Freyd, J.J. (1993).** Timing and apparent motion path choice with human body photographs. *Psychological Science*, 4, 379–384.
Systematic replication establishing the time-course. Rules out iconic memory or neural persistence — implicates higher-order shape/motion constraints in trajectory construction.

---

## 5. Representational Momentum — Dynamic Representations Extrapolate Paths

**Freyd, J.J. & Finke, R.A. (1984).** Representational momentum. *Journal of Experimental Psychology: Learning, Memory, and Cognition*, 10, 126–132.
Probes for the final position of a rotating implied-motion sequence are systematically misidentified when displaced slightly forward along the trajectory. Memory for moving objects is displaced in the direction of motion — the representation continues moving under inertia. The visual system routinely builds a dynamic model that extrapolates position along the motion path.

**Freyd, J.J. & Finke, R.A. (1985).** A velocity effect for representational momentum. *Journal of Experimental Psychology: Learning, Memory, and Cognition*, 11, 601–607.
Forward displacement in memory scales with implied velocity — rules out response bias, supports internalization of motion dynamics. The visual system extrapolates positions along the trajectory even without perceptual input.

**Freyd, J.J. (1987).** Dynamic mental representations. *Psychological Review*, 94, 427–438. [PMID: 3317470]
Review formalizing the framework: mental representations preserve trajectory, not just snapshots. The representation evolves over time in the direction of the last-known motion — the theoretical unification of representational momentum, path choice, and perceptual interpolation.

---

## 6. Flash-Lag and Motion Extrapolation — Interpolation Forward in Time

**Nijhawan, R. (1994).** Motion extrapolation in catching. *Nature*, 370, 256–257. [PMID: 8035873]
A moving rod appears spatially ahead of an aligned flash because the visual system projects the moving object's position forward in time to compensate for neural transmission delays (~100 ms). Motion perception is not instantaneous — it involves predictive spatial interpolation of future position from the recent trajectory.

**Berry, M.J., Brivanlou, I.H., Jordan, T.A. & Meister, M. (1999).** Anticipation of moving stimuli by the retina. *Nature*, 398, 334–338. [PMID: 10192333]
Retinal ganglion cell activity leads a moving bar — firing anticipates the object's position rather than lagging behind phototransduction delays. Predictive motion extrapolation begins at the retina, before any cortical processing. The earliest known neural locus of trajectory interpolation in the visual system.

**Hogendoorn, H. (2020).** Motion extrapolation in visual processing: lessons from 25 years of flash-lag debate. *Journal of Neuroscience*, 40, 5698–5705. [PMID: 32699152]
Review concluding that predictive motion extrapolation is a real and separable component of the flash-lag effect. Early extrapolation signals localize to V1/V2, consistent with interpolation occurring at the earliest cortical stages. Directly relevant to dot stimuli: individual dot trajectories trigger the same extrapolation machinery.

---

## 7. Anorthoscopic Perception — Temporal-to-Spatial Integration

**Parks, T.E. (1965).** Post-retinal visual storage. *American Journal of Psychology*, 78, 145–147.
A figure moved behind a narrow slit is perceived as an integrated spatial whole even though only a sliver is visible at any moment. Cannot be explained by retinal smear (slit too narrow) — requires "post-retinal" accumulation of sequentially presented local samples. A paradigmatic case of the visual system performing temporal-to-spatial interpolation: reconstructing spatial extent from a time-series of local position samples. ⚠️ Not PubMed indexed (psychology journal); verify via library.

**Morgan, M.J., Findlay, J.M. & Watt, R.J. (1982).** Aperture viewing: a review and a synthesis. *Quarterly Journal of Experimental Psychology*, 34A, 211–233.
Confirms that anorthoscopic perception depends on genuine spatiotemporal integration, not eye movements. Integration occurs over a window of several hundred milliseconds. Anchors the mechanistic interpretation of Parks (1965) as active neural interpolation of position across time.

---

## 8. Motion Correspondence — Interpolating Identity Across Frames

**Ullman, S. (1979).** *The Interpretation of Visual Motion.* MIT Press. (also Proceedings of the Royal Society B, 203, 405–426.)
Foundational computational treatment of the correspondence problem: which dot in frame N+1 matches which in frame N? The minimal-mapping solution assigns costs based on spatial proximity and a rigidity constraint — the system selects correspondences minimizing spatial displacement, then interpolates positions smoothly between frames. Sets the stage for all coherence threshold work.

**Dawson, M.R.W. (1991).** The how and why of what went where in apparent motion: modeling solutions to the motion correspondence problem. *Psychological Review*, 98, 569–603. [PMID: 1961774]
Comprehensive computational model of correspondence in apparent motion: nearest neighbor (minimize displacement — the interpolation heuristic), relative velocity (favor smooth trajectories), and element integrity (preserve dot identity). Predicts human correspondence choices across random dot cinematogram configurations. Nearest-neighbor constraint = the visual system's prior that dots travel along the shortest interpolated path.

**Todd, J.T. (1982).** Visual information about rigid and nonrigid motion: a geometric analysis. *Journal of Experimental Psychology: Human Perception and Performance*, 8, 238–252.
Two-frame information is sufficient to determine rigid 3D motion from four point correspondences. Psychophysically confirms observers are sensitive to these constraints — interpolated displacement vectors between frames directly support global 3D structure recovery. Interpolation and structure-from-motion are tightly coupled. ⚠️ Verify PMID independently.

---

## 9. Aperture Problem — Spatial Interpolation Resolves Local Ambiguity

**Adelson, E.H. & Movshon, J.A. (1982).** Phenomenal coherence of moving visual patterns. *Nature*, 300, 523–525. [PMID: 7144903]
Two superimposed gratings cohere into a single object with a unique velocity — the "intersection of constraints" solution. The global direction is the velocity consistent with both locally ambiguous signals. The visual system spatially interpolates across locally uncertain velocity measurements to reconstruct a single unambiguous global motion — the canonical local-to-global integration.

**Nakayama, K. & Silverman, G.H. (1988a,b).** The aperture problem — I & II. *Vision Research*, 28, 739–746 and 747–753. [PMIDs: 3227650, 3227651]
Part I: local motion along contours is inherently ambiguous. Part II: unambiguous velocity signals at line terminators are "broadcast" along the contour via spatial interpolation, overriding interior aperture ambiguity. A direct mechanism for spatial interpolation of motion signals across position.

---

## 10. Attention-Based Tracking — High-Level Trajectory Interpolation

**Cavanagh, P. (1992).** Attention-based motion perception. *Science*, 257, 1563–1565. [PMID: 1523411]
At equiluminance, color-defined gratings are invisible to the low-level motion system yet perceivable when attention tracks individual elements. A high-level motion system computes displacement by tracking spatial position changes across frames — interpolating individual dot trajectories even when low-level motion energy is absent. For RDKs, this system interpolates dot positions across frames via spatiotemporal correspondence without local energy signals.

**Whitney, D. & Cavanagh, P. (2000).** Motion distorts visual space: shifting the perceived position of remote stationary objects. *Nature Neuroscience*, 3, 954–959.
A stationary flash near a moving pattern is perceived as displaced in the direction of motion (flash-drag effect). This position shift is registered in early visual cortex, indicating that trajectory interpolation and spatial extrapolation based on motion are implemented at V1/V2 — before object representations are constructed. ⚠️ Verify PMID independently.

**Watamaniuk, S.N.J. & Duchon, A. (1992).** The human visual system averages speed information. *Vision Research*, 32, 931–941.
Speed perception from random dot kinematograms involves spatiotemporal pooling across many dots and frames over hundreds of milliseconds and several degrees. Smooth trajectory perception for discrete dot stimuli arises from active spatiotemporal pooling — the visual system builds a running trajectory estimate by interpolating across the discrete position samples in each frame. ⚠️ Verify PMID independently.

---

## 11. Glass Patterns — Static Analog of Spatial Interpolation

The static analog: a random dot array superimposed on a slightly transformed copy of itself yields a global oriented percept — circular swirls, radial streaks — from dot-pair offsets alone. The same V1 orientation-selective filters that read motion streaks read Glass pattern structure.

**Glass, L. (1969).** Moiré effect from random dots. *Nature*, 223, 578–580. [PMID: 5799528]
Global oriented structure perceived from local dot-pair offsets — the visual system computes local autocorrelations via orientation-selective detectors and pools globally. Pure spatial interpolation: oriented percept "read out" from spatial offsets between discrete dots, exactly as motion direction is read from temporal offsets in kinematograms.

**Dakin, S.C. (1997).** The detection of structure in Glass patterns: psychophysics and computational models. *Vision Research*, 37, 2227–2246. [PMID: 9578905]
Oriented spatial filtering (V1-like) accounts for human Glass-pattern sensitivity — unifying spatial interpolation in static Glass patterns with spatiotemporal interpolation in motion. Provides quantitative bridge between Glass (1969) and the Adelson–Bergen energy-model framework.

**Wilson, H.R., Wilkinson, F. & Asaad, W. (1997).** Concentric orientation summation in human form vision. *Vision Research*, 37, 2325–2330. [PMID: 9381668]
Orientation signals from Glass pattern dipoles are pooled linearly over large spatial extents by a "second stage" (V4-type neurons). Directly analogous to the global motion pooling stage that interpolates local velocity signals in random dot kinematograms — same two-stage (local interpolation → global pooling) architecture.

---

## 12. Kinetic Interpolation — Named as a Perceptual Process

**Kellman, P.J. & Shipley, T.F. (1991).** A theory of visual interpolation in object perception. *Cognitive Psychology*, 23, 141–221. [PMID: 2055000]
The most thorough treatment of visual interpolation as a general perceptual mechanism, unified for static (illusory contour, amodal completion) and kinetic (motion-based) cases. Key concept: *spatiotemporal relatability* — edge fragments get connected when they are geometrically alignable and have compatible velocities. This paper explicitly named "kinetic interpolation" as a perceptual process obeying the same geometric constraints as static completion. Directly relevant to VRDots: the translation window is precisely a kinetic occlusion event, and surface identity across a swap is determined by spatiotemporal relatability.

---

## 13. Predictive Coding — Cortical Hierarchy Interpolates Future States

**Rao, R.P.N. & Ballard, D.H. (1999).** Predictive coding in the visual cortex: a functional interpretation of some extra-classical receptive-field effects. *Nature Neuroscience*, 2, 79–87. [PMID: 10195184]
Each level of visual cortex predicts the activity of the level below; only prediction errors propagate upward. Motion interpolation follows naturally: higher levels predict next-frame dot positions from current trajectory, and only the unpredicted component (e.g., a translation onset) drives a strong response. Predicts that an unexpected position change (motion swap) generates a large prediction error — consistent with disruption effects in feature-swap conditions.

---

## Summary by Type of Interpolation

| Type | Papers |
|---|---|
| Spatiotemporal filter (detector-level) | Watson & Ahumada (1985); Adelson & Bergen (1985); Burr & Ross (1982); Watson et al. (1986) |
| Spatial (motion streaks) | Geisler (1999); Geisler et al. (2001); Krekelberg et al. (2003) |
| Limits of spatial interpolation | Burr (1979, 1980); Morgan & Watt (1983) |
| Trajectory construction (apparent motion) | Ramachandran & Anstis (1983); Shepard & Zare (1983); Shiffrar & Freyd (1990, 1993) |
| Dynamic/extrapolative representations | Freyd & Finke (1984, 1985); Freyd (1987) |
| Forward-in-time extrapolation | Nijhawan (1994); Berry et al. (1999); Hogendoorn (2020) |
| Temporal-to-spatial (anorthoscopic) | Parks (1965); Morgan et al. (1982) |
| Correspondence (dot identity across frames) | Ullman (1979); Dawson (1991); Todd (1982) |
| Aperture resolution (spatial) | Adelson & Movshon (1982); Nakayama & Silverman (1988a,b) |
| Attention-based tracking | Cavanagh (1992); Whitney & Cavanagh (2000); Watamaniuk & Duchon (1992) |
| Static analog (Glass patterns) | Glass (1969); Dakin (1997); Wilson et al. (1997) |
| Named kinetic interpolation | Kellman & Shipley (1991) |
| Predictive coding framework | Rao & Ballard (1999) |

---

## Items Flagged for Independent Verification (no PMID confirmed)
- Ramachandran & Anstis (1983) *Nature* 304, 529–531
- Shepard & Zare (1983) *Science* 220, 632–634
- Shiffrar & Freyd (1990) *Psychological Science* 1, 257–264
- Shiffrar & Freyd (1993) *Psychological Science* 4, 379–384
- Geisler et al. (2001) *Visual Neuroscience* 18, 501–516
- Krekelberg et al. (2003) *Nature* 424, 674–677
- Parks (1965) *American Journal of Psychology* 78, 145–147 (not PubMed indexed)
- Morgan, Findlay & Watt (1982) *QJEP* 34A, 211–233 (not PubMed indexed)
- Todd (1982) *JEP:HPP* 8, 238–252
- Whitney & Cavanagh (2000) *Nature Neuroscience* 3, 954–959
- Watamaniuk & Duchon (1992) *Vision Research* 32, 931–941
