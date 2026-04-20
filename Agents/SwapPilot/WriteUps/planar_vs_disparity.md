# Planar Position vs. Depth from Binocular Disparity: A Note on Scale

The stimulus displays two depth planes, defined by binocular disparity. It is worth distinguishing this signal from the planar (x-y) position of the dots, because while both ultimately arise from retinal position, they operate at very different scales. Planar position is the mean lateral location of a dot's projection across the two eyes — the coarse coordinate that places a dot in one region of the visual field versus another. Depth from disparity, by contrast, is encoded by the *difference* in lateral position between the left- and right-eye images of the same dot.

For the depth separation used here (Δ*z* = 5 cm at a viewing distance of *D* ≈ 2 m, with an interpupillary distance of ~63 mm), this disparity is approximately:

> η = IPD × Δ*z* / *D*² ≈ 63 × 50 / 2000² mm ≈ 0.8 × 10⁻³ rad ≈ **2.7 arcmin**

The mean nearest-neighbor distance between dots within a subfield, by contrast, is roughly **60–90 arcmin** — more than an order of magnitude larger. In other words, the binocular disparity signal that encodes which depth plane a dot belongs to consists of retinal position shifts that are ~3% of the average inter-dot spacing.

These two signals — coarse planar location and fine inter-ocular disparity — are therefore effectively orthogonal: disparity provides depth-plane identity while contributing negligibly to the planar position signal that drives the motion percept.



Here's how it maps onto V1 RFs:

  Planar position (coarse x-y) is encoded by the retinotopic location of V1 RFs — a dot's mean binocular projection
  falls on a particular patch of cortex. The inter-dot spacing of ~60–90 arcmin is several times larger than a typical
  V1 RF (~5–20 arcmin at the eccentricities used), so planar position is unambiguously resolved spatially across the
  cortical map.

  Depth from disparity (fine inter-ocular shift) is encoded within a single V1 RF by the relative phase or position
  offset between the left- and right-eye drive. The 2.7 arcmin disparity is well within the operating range of V1
  disparity-tuned neurons (roughly ±10–15 arcmin for the near-to-mid-field). Importantly, that 2.7 arcmin shift is far
  below the inter-dot spacing, so the two signals don't compete: a V1 neuron at a given retinotopic locus responds to
  the dot that fell on its RF based on planar position, and its disparity tuning then reports which depth plane that dot
   occupies.

  The practical upshot: depth-plane identity and motion-direction signal are segregated at the level of the V1 RF
  itself. Planar translation shifts activation across the cortical map; depth assignment is a property of the binocular
  computation within each RF. Any interaction between them (e.g., your F1×F2 effects) must emerge downstream, where
  signals from disparity-tuned V1 neurons are pooled into object representations.

