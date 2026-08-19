#!/usr/bin/env python3
"""STANDING CHECK for the shared stimulus panel.

mt_rf_figure.png and ps_two_rf_figure.png are supposed to show the SAME
stimulus, drawn by the one draw_stimulus() in ps_stimulus_common. This locates
the aperture circle in each, confirms the two are rendered at the same scale,
and diffs the panels.

The only difference blobs >= 60 px may be the two V1 RF circles, their leader
and their label -- everything else must cancel. A scale mismatch here is what
tight_layout used to cause (one figure 8% larger than the other), which is why
the margins are pinned with subplots_adjust.

    python3 check_stimulus_panels.py
"""
import sys
import numpy as np
from PIL import Image
from scipy import ndimage

MIN_BLOB = 60


def aperture_bbox(path):
    """Bounding box of the aperture circle: darkest ring in the left half.

    Half, not a third: the stimulus panel is a larger fraction of the narrower
    two-panel figure, and a third clips its circle -- which reads as a bogus
    scale mismatch.
    """
    im = np.asarray(Image.open(path).convert("L")).astype(float)
    left = im[:, : im.shape[1] // 2]
    # Threshold on the RIM's ink only. The palette is INK 31, INK2 (leaders) 77,
    # the dots and rotation arcs 108-113 against a 250 ground, so 60 takes the
    # aperture rim and nothing else. A looser cut lets the arcs and dots merge
    # into one sprawling blob whose "width" is meaningless -- which is exactly
    # how this reported a bogus scale mismatch once the arcs moved inside.
    dark = left < 60
    # the aperture rim is the largest dark connected component in that third
    lab, n = ndimage.label(dark)
    if n == 0:
        sys.exit(f"{path}: no dark pixels found in the left third")
    sizes = ndimage.sum(dark, lab, range(1, n + 1))
    rim = (np.argmax(sizes) + 1)
    ys, xs = np.where(lab == rim)

    # Measure the diameter VERTICALLY. The MT RF disc is placed with its outer
    # edge ON the aperture rim (MT_ECC = APERTURE - MT_R) and is drawn over it,
    # so it eats the rightmost rim pixels -- by a different amount in each
    # figure, since the panels differ in width. Top and bottom are untouched, and
    # the leftmost point is clean, so height is the true diameter and xmin + h/2
    # the true centre.
    bb = (xs.min(), xs.max(), ys.min(), ys.max())
    diam = float(bb[3] - bb[2])
    if not 0.96 < (bb[1] - bb[0]) / diam <= 1.01:
        sys.exit(f"{path}: largest INK blob is not the round aperture "
                 f"(w/h {(bb[1] - bb[0]) / diam:.3f}) -- detection is off")
    cx, cy = float(bb[0]) + diam / 2.0, (bb[2] + bb[3]) / 2.0
    return im, diam, cx, cy


def main():
    a_im, a_d, a_cx, a_cy = aperture_bbox("mt_rf_figure.png")
    b_im, b_d, b_cx, b_cy = aperture_bbox("ps_two_rf_figure.png")

    print(f"aperture diameter   mt_rf {a_d:.1f} px   ps_two_rf {b_d:.1f} px"
          f"   ratio {a_d / b_d:.4f}")
    if abs(a_d / b_d - 1) > 0.005:
        print("  !! SCALE MISMATCH -- the two panels are not the same size")
        return 1

    # crop a common window around the aperture, generous enough to take in the
    # arcs on the left and the RF labels on the right
    # Wide horizontally -- the "Area MT RF" and "Area V1 RFs" labels sit well
    # outside the rim -- but only just past the rim vertically: the panel titles
    # and the figure footers sit above and below and differ between the two
    # figures by design. Keep py small; it is measured in units of the aperture
    # diameter, which changes whenever the axis padding does.
    px, py = int(round(a_d * 0.42)), int(round(a_d * 0.03))
    hx, hy = int(a_d / 2) + px, int(a_d / 2) + py
    def crop(im, cx, cy):
        x0, y0 = int(round(cx)) - hx, int(round(cy)) - hy
        return im[max(y0, 0):y0 + 2 * hy, max(x0, 0):x0 + 2 * hx]
    A, B = crop(a_im, a_cx, a_cy), crop(b_im, b_cx, b_cy)
    h = min(A.shape[0], B.shape[0]); w = min(A.shape[1], B.shape[1])
    A, B = A[:h, :w], B[:h, :w]

    diff = np.abs(A - B) > 40
    lab, n = ndimage.label(diff)
    sizes = ndimage.sum(diff, lab, range(1, n + 1))
    big = [(int(s), ndimage.center_of_mass(diff, lab, i + 1))
           for i, s in enumerate(sizes) if s >= MIN_BLOB]
    big.sort(reverse=True)

    print(f"crop {w}x{h}px   differing pixels {int(diff.sum())}"
          f"   blobs >= {MIN_BLOB}px: {len(big)}")
    for s, (cy, cx) in big:
        print(f"    {s:6d} px  at  x {cx:6.0f}  y {cy:6.0f}")
    # Verdict. Everything that may legitimately differ -- the two V1 RF
    # circles, their leader, their label -- lives to the RIGHT of the aperture
    # centre. A blob on the left half means the shared drawing diverged: the
    # rotation arcs, the legend, or the dots themselves.
    stray = [(s_, c) for s_, c in big if c[1] < hx]
    if stray:
        print("\nFAIL: %d difference blob(s) on the LEFT, where the two panels"
              " must agree:" % len(stray))
        for s_, (cy_, cx_) in stray:
            print(f"    {s_:6d} px  at  x {cx_:6.0f}  y {cy_:6.0f}")
        return 1
    print("\nPASS: every difference is the V1 RF circles, their leader and"
          " their label, all right of centre.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
