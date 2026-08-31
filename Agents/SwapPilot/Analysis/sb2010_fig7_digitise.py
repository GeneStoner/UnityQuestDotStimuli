"""
sb2010_fig7_digitise.py

Digitise Figure 7 of Stoner & Blanc (2010) -- the four swap conditions, cued and
uncued percent correct -- from the scanned page image on the website.

WHY. S&B's own per-condition accuracies appear nowhere in the project. Only the
cueing effect ("approximately 35 pp" in prose) and the VRDots replication at S&B
parameters were on record. The model paper needs S&B's cued/uncued values to put
the model beside them, so they are measured here rather than eyeballed.

METHOD. The bars are flat grey (151,150,148) on white, and the x-axis labels
0,10,...,100 sit below each panel. Both are found programmatically:
  * bar right edge  = last column where >60% of the band's rows are grey
  * axis calibration = least-squares fit of label-cluster centres against value,
    using 0..90 only. The 3-digit "100" label's centre is offset by its extra
    glyph and pulls the fit; including it inflates the residual from 0.3 to 3.6
    units. Excluding it, both panels agree on 2.883 px/unit.

ACCURACY. Calibration residual <= 0.4 units; bar-edge quantisation +/- 1 px =
0.35 units. So roughly +/- 1 percentage point.

CROSS-CHECKS THAT PASS. All four cueing effects come out positive (S&B report
p < 0.001 for all four). Motion-swap cueing exceeds no-swap, the same ordering
the VRDots replication shows (+16.8 -> +19.9 pp). Both panels' fitted zero lands
within ~1.5 px of the bars' own left edge.

  python3 sb2010_fig7_digitise.py [path/to/fig7.png]
"""
import sys
import numpy as np
from PIL import Image

FIG = sys.argv[1] if len(sys.argv) > 1 else \
    "/Users/genestoner/Sites/open-perception/public/figures/sb2010/fig7.png"

BAR_RGB   = (151, 150, 148)   # the grey of the mean bars
BANDS     = [(168, 214), (228, 274), (357, 403), (418, 464)]   # cued/uncued row pairs
LABEL_ROWS = (468, 500)       # the axis-label text strip
PANEL_SPLIT = 690             # x dividing the two panels

# panel letters are S&B's own condition labels (their Fig. 5 / Fig. 7)
ROWS = [("no swap",       0, 1, 'L', "A/C"),
        ("motion swap",   0, 1, 'R', "D/B"),
        ("colour swap",   2, 3, 'L', "E/G"),
        ("motion+colour", 2, 3, 'R', "H/F")]


def clusters(xs, gap=10):
    out, cur = [], [xs[0]]
    for x in xs[1:]:
        if x - cur[-1] <= gap:
            cur.append(x)
        else:
            out.append(cur); cur = [x]
    out.append(cur)
    return out


def calibrate(label_clusters, name):
    """px-per-unit and the x of 0, from the 0..90 labels."""
    use = label_clusters[:10]
    ctr = np.array([(c[0] + c[-1]) / 2 for c in use])
    val = np.arange(10) * 10.0
    m, b = np.polyfit(val, ctr, 1)
    resid = np.abs(ctr - (m * val + b)).max()
    print(f"  {name}: {m:.4f} px/unit, x(0) = {b:.2f}, max residual "
          f"{resid:.2f} px = {resid/m:.2f} units")
    assert resid / m < 1.0, "calibration residual too large -- check label clustering"
    return m, b


def right_edge(grey, y0, y1, xlo, xhi):
    band = grey[y0:y1 + 1, xlo:xhi]
    cols = np.where(band.sum(axis=0) > 0.6 * (y1 - y0 + 1))[0]
    return xlo + cols.max()


def main():
    a = np.array(Image.open(FIG).convert('RGB')).astype(int)
    grey = np.abs(a - np.array(BAR_RGB)).max(axis=2) < 12
    dark = a.max(axis=2) < 120

    strip = dark[LABEL_ROWS[0]:LABEL_ROWS[1]].sum(axis=0)
    xs = [x for x in range(a.shape[1]) if strip[x] >= 4]
    cl = clusters(xs)
    left  = [c for c in cl if c[-1] <  PANEL_SPLIT]
    right = [c for c in cl if c[0]  >= PANEL_SPLIT]

    print("axis calibration (0..90 labels; the 3-digit '100' is excluded):")
    mL, bL = calibrate(left,  "left ")
    mR, bR = calibrate(right, "right")

    print(f"\n{'condition':<16}{'S&B panels':<12}{'cued':>7}{'uncued':>8}{'cueing':>9}")
    res = {}
    for lab, ic, iu, side, letters in ROWS:
        xlo, xhi, m, b = (360, PANEL_SPLIT, mL, bL) if side == 'L' \
                    else (PANEL_SPLIT + 5, 1010, mR, bR)
        c = (right_edge(grey, *BANDS[ic], xlo, xhi) - b) / m
        u = (right_edge(grey, *BANDS[iu], xlo, xhi) - b) / m
        res[lab] = (round(c, 1), round(u, 1))
        print(f"{lab:<16}{letters:<12}{c:>7.1f}{u:>8.1f}{c-u:>+9.1f}")

    assert all(c > u for c, u in res.values()), \
        "every condition must show cued > uncued -- S&B report p<0.001 for all four"
    print(f"\n  accuracy ~ +/-1 pp (calibration <=0.4 units, bar edge +/-{1/mL:.2f} units)")
    print("  chance = 12.5%")
    return res


if __name__ == "__main__":
    main()
