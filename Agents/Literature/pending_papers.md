# Pending Papers — Future Literature Sessions

Papers from the Stoner lab list not yet integrated into `theory_doc.md`. All are approved for pursuit in a future literature session.

## STATUS (updated 2026-03-31)
Items 1–6 have been integrated into `theory_doc.md` § 6. Item 7 (Stoner/Carney/Shadlen) was not located — see note below.
Three venue errors in this file were corrected during that session (see table at bottom).

---

~~1. **Stoner & Albright (1992) Nature** — INTEGRATED (theory_doc.md §6.2)~~

~~2. **Stoner & Albright (1993) *Journal of Cognitive Neuroscience*** — INTEGRATED (theory_doc.md §6.3)~~
*(Was listed as Neuron — corrected to J Cognitive Neuroscience)*

~~3. **Stoner & Albright (1996) *Vision Research*** — INTEGRATED (theory_doc.md §6.4)~~
*(Was listed as Nature — corrected to Vision Research)*

~~4. **Stoner, Albright & Ramachandran (1990) Nature** — INTEGRATED (theory_doc.md §6.1)~~

~~5. **Stoner & Albright (1998) Vision Research** — INTEGRATED with caveat (theory_doc.md §6.5)~~
*(Could not confirm specific VR paper; Dobkins, Stoner & Albright 1998 JOSA-A used as proxy — verify)*

~~6. **Albright & Stoner (2002) *Annual Review of Neuroscience*** — INTEGRATED (theory_doc.md §6.6)~~
*(Was listed as PNAS — corrected to Annual Review of Neuroscience)*

7. **Stoner, Carney & Shadlen (various)** — NOT LOCATED. Web search did not return a specific paper with these three authors on depth/disparity in MT. Needs a specific citation. Potentially relevant nearby paper: **PubMed ID 21068268** — "Population anisotropy in area MT explains a perceptual difference between near and far disparity motion segmentation" — retrieve and review as substitute or companion.

8. **Reynolds, Chelazzi & Desimone (1999) J Neurosci** — "Competitive mechanisms subserve attention in macaque areas V2 and V4." Biased-competition framework: the selection mechanism the translational onset cue recruits; theoretical backbone for the dot cueing effect.

11. **Treue & Martinez-Trujillo (1999) Nature** — "Feature-based attention influences motion processing gain in macaque visual cortex." Feature-similarity gain model; predicts that attending a motion direction boosts gain for all stimuli moving in that direction, relevant to how the translational cue propagates across the surface.

12. **Carandini & Heeger (2012) Nature Reviews Neuroscience** — "Normalization as a canonical neural computation." Normalization model predicts how attended surface gain change interacts with the unattended surface response; relevant to ZdA/ZdB gain-change interpretations.

13. **Born & Bradley (2005) Annual Review of Neuroscience** — "Structure and function of visual area MT." Comprehensive MT review; necessary background for Wannig et al. (2007) and Lankheet & Verstraten (1995) citations already in theory doc.

14. **Tse, Martinez-Conde et al. (2005) J Vision** — "Seeing motion in depth using inter-ocular velocity differences." Motion-in-depth from IOVD (not just changing disparity); relevant if depth-plane transitions in ZdA/ZdB create unintended motion-in-depth signals.

15. **Cumming & DeAngelis (2001) Annual Review of Neuroscience** — "The physiology of stereopsis." V1 and MT disparity tuning; establishes the neural substrate for the depth-plane signals VRDots uses and informs what 0.05m at 2m means in disparity units.

16. **Neri, Bridge & Heeger (2004) J Neurosci** — "Stereoscopic processing of absolute and relative disparity in human visual cortex." fMRI: absolute vs. relative disparity in V1–V3/MT; relevant to whether the Near/Far asymmetry in VRDots reflects absolute disparity processing differences.

18. **Uka & DeAngelis (2006) J Neurosci** — "Linking neural activity and perception: Binocular disparity and the relative contributions of parietal and inferotemporal cortices." Causal role of MT disparity signals; relevant to whether the ZdA/ZdB depth-swap effects could be mediated through MT disparity rather than surface-identity mechanisms.

---

## From Doostani et al. (2023) reference list — added 2026-04-01

### Tier 1 — HIGH PRIORITY (object/surface-based attention, MT + multiple stimuli)

**43. Roelfsema, Lamme & Spekreijse (1998) *Nature* 395:376–381** — "Object-based attention in the primary visual cortex of the macaque monkey." V1 neurons track attended object contours; direct neural evidence for object-based selection at V1. Foundational empirical support for the V1 Point-Set model — the paper most directly showing that object identity modulates V1 responses. **Retrieve and integrate into modeling_lit.md §6 and theory_doc.md.** ⚠️ *Paradigm note*: the "objects" here are spatially extended contours (curve-tracing task), not spatially intermixed dot fields. The V1 modulation may reflect contour-based spatial spreading rather than the sub-RF dot-identity mechanism needed for VRDots. Assess whether the mechanism is the same or analogous.

**44. O'Craven, Downing & Kanwisher (1999) *Nature* 401:584–587** — "fMRI evidence for objects as the units of attentional selection." Two overlapping objects moving in different directions: attending one selectively activates its category-selective cortex. The closest object-recognition analog to our transparent-motion paradigm (overlapping + different motions + object-level selection). **Retrieve and integrate into theory_doc.md §2.** ⚠️ *Paradigm note*: the discriminating signal here is category identity (face vs. house), read out by category-selective areas (FFA, PPA) with large RFs. This is mechanistically different from dot-field selection, which has no categorical identity and requires sub-RF spatial resolution. The result shows objects are units of selection at a high level; VRDots asks whether the *same* unit-of-selection logic operates at V1 dot scale.

**49. Lee & Maunsell (2010) *J Neurosci* 30:3058–3066** — "Attentional modulation of MT neurons with single or multiple stimuli in their receptive fields." Electrophysiology companion to Lee & Maunsell (2009); tests normalization model predictions in MT with one vs. two stimuli in the RF — the VRDots two-surface scenario exactly. **Retrieve and integrate into modeling_lit.md §2.1.**

**53. Ni & Maunsell (2019) *J Neurosci* 39:5493–5505** — "Neuronal effects of spatial and feature attention differ due to normalization." Directly addresses whether the normalization mechanism differs between spatial and feature-based attention — VRDots' exogenous cue recruits both. **Retrieve and integrate into modeling_lit.md §2.**

**55. Herrmann, Montaser-Kouhsari, Carrasco & Heeger (2010) *Nature Neuroscience* 13:1554–1559** — "When size matters: attention affects performance by contrast or response gain." Behavioral psychophysics test of Reynolds & Heeger (2009) attention-field-size predictions. Determines which gain type VRDots' cue should produce given stimulus and attention field geometry. **Retrieve and integrate into modeling_lit.md §2.0.**

### Tier 2 — Normalization × attention (integrate when modeling section is expanded)

**42. Moran & Desimone (1985) *Science* 229:782–784** — Foundational gating paper; selective attention gates V4 responses.

**45. Cook & Maunsell (2002) *J Neurosci* 22:1994–2004** — MT and VIP attention modulation; behavioral + neural in macaque.

**46. Martínez-Trujillo & Treue (2002) *Neuron* 35:365–370** — MT attention strength depends on contrast; extends Treue & MTT.

**47. Treue & Martínez-Trujillo (1999) *Nature* 399:575–579** — Feature-similarity gain in MT (also in earlier pending list).

**48. Womelsdorf et al. (2006) *Nature Neuroscience* 9:1156–1160** — MT RF shifts with spatial attention.

**50. Heuer & Britten (2002) *J Neurophysiol* 88:3398–3408** — Contrast dependence of MT normalization.

**51. Ni, Ray & Maunsell (2012) *Neuron* 73:803–813** — Sizes of attention modulations.

**52. Ni & Maunsell (2017) *J Neurophysiol* 118:1903–1913** — Spatially uniform normalization explains attention variance.

**54. Bloem & Ling (2019) *Nature Communications* 10:5660** — Normalization governs attention in human fMRI.

**56. Herrmann, Heeger & Carrasco (2012) *Vision Research* 47:10–20** — Feature attention = response gain.

**57. Schwedhelm, Krishna & Treue (2016) *PLOS Computational Biology* 12:e1005225** — Extended normalization for feature attention; coherence gain relevant to motion coherence in VRDots.

**58. Itthipuripat et al. (2014) *J Neurosci* 34:112–123** — Spatial scope → gain type; EEG/ERP.

**59. Denison, Carrasco & Heeger (2021) *Nature Human Behaviour* 5:1674–1685** — Dynamic normalization model of temporal attention.

**60. Busse, Wade & Carandini (2009) *Neuron* 64:931–942** — Population coding of concurrent stimuli.

**61. Serences & Boynton (2007) *Neuron* 55:301–312** — Feature attention without direct stimulation; global gain.

**62. Reddy, Kanwisher & VanRullen (2009) *PNAS* 106:21447–21452** — Biased competition in multi-voxel object representations.

**63. Rubin, Van Hooser & Miller (2015) *Neuron* 85:402–417** — Stabilized supralinear network; circuit basis for V1 recurrent dynamics.

**64. Aqil, Knapen & Dumoulin (2021) *PNAS* 118:e2108713118** — Normalization across human visual hierarchy.

**65. Boynton (2009) *Vision Research* 49:1129–1143** — Framework for attention effects on visual responses.

---

*Note: Numbering follows paper_list.md. Papers integrated into theory_doc.md or modeling_lit.md are not repeated here.*
