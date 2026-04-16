# Planar Position vs. Depth from Binocular Disparity: A Note on Scale

The stimulus displays two depth planes, defined by binocular disparity. It is worth distinguishing this signal from the planar (x-y) position of the dots, because while both ultimately arise from retinal position, they operate at very different scales. Planar position is the mean lateral location of a dot's projection across the two eyes — the coarse coordinate that places a dot in one region of the visual field versus another. Depth from disparity, by contrast, is encoded by the *difference* in lateral position between the left- and right-eye images of the same dot.

For the depth separation used here (Δ*z* = 5 cm at a viewing distance of *D* ≈ 2 m, with an interpupillary distance of ~63 mm), this disparity is approximately:

> η = IPD × Δ*z* / *D*² ≈ 63 × 50 / 2000² mm ≈ 0.8 × 10⁻³ rad ≈ **2.7 arcmin**

The mean nearest-neighbor distance between dots within a subfield, by contrast, is roughly **60–90 arcmin** — more than an order of magnitude larger. In other words, the binocular disparity signal that encodes which depth plane a dot belongs to consists of retinal position shifts that are ~3% of the average inter-dot spacing.

These two signals — coarse planar location and fine inter-ocular disparity — are therefore effectively orthogonal: disparity provides depth-plane identity while contributing negligibly to the planar position signal that drives the motion percept.
