"""
Where the attentional bias enters — Model III vs Model IV of the HC / PS model.

Builds `bias_locus.pdf`. REWRITTEN 2026-08-20 (second pass). The first pass posed
this as an open question with two unnamed "variants" and closed by saying we did
not know which one our code ran. Both halves of that were wrong: the two routes
are the existing Model III / Model IV, they are implemented behind one boolean in
two engines, and the locked operating point runs Model IV. The equations in the
first pass also differed from the code in four places. All of it is corrected
here against hcps_grid.m and toy_color.m, and the numbers come from
pointset/hcps_bias_locus_check.m and pointset/hcps_bias_locus_ablate.m.

No LaTeX, pandoc, reportlab or headless browser on this machine, so the document
is typeset with matplotlib's PDF backend and mathtext. That constrains the maths
to mathtext's subset — keep equations simple, and check every one renders rather
than trusting the string.

Run:  /usr/bin/python3 bias_locus.py
"""

import textwrap
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.patches import Rectangle, Circle, FancyArrowPatch

INK, INK2, MUTED = "#1e1e2a", "#4a4a62", "#8a8a99"
BIAS, POOL, MOTION, COLOUR = "#c0504d", "#c4831f", "#3a6fd8", "#8d5bbf"
RULE = "#ddd9d2"

PAGE = (8.5, 11.0)
L, R = 0.095, 0.905                      # text margins in figure coords


class Page:
    """A page with a top-down text cursor, in figure coordinates."""

    def __init__(self, pdf, running=None):
        self.fig = plt.figure(figsize=PAGE)
        self.pdf = pdf
        self.y = 0.935
        if running:
            self.fig.text(L, 0.962, running, fontsize=8, color=MUTED)
            self.fig.text(R, 0.962, "Stoner lab · object-based attention",
                          fontsize=8, color=MUTED, ha="right")
            self.fig.add_artist(plt.Line2D([L, R], [0.953, 0.953],
                                           color=RULE, lw=0.8))

    def gap(self, dy):
        self.y -= dy

    def h1(self, s):
        self.gap(0.012)
        self.fig.text(L, self.y, s, fontsize=17, fontweight="bold", color=INK,
                      va="top")
        self.gap(0.040)

    def h2(self, s, colour=INK):
        self.gap(0.014)
        self.fig.text(L, self.y, s, fontsize=12.5, fontweight="bold",
                      color=colour, va="top")
        self.gap(0.026)

    def body(self, s, width=92, size=10, colour=INK, indent=0.0):
        for line in textwrap.wrap(" ".join(s.split()), width):
            self.fig.text(L + indent, self.y, line, fontsize=size, color=colour,
                          va="top")
            self.gap(0.0165)
        self.gap(0.006)

    def eq(self, s, note=None, size=13, dy=0.030):
        self.fig.text(0.5, self.y, s, fontsize=size, color=INK, va="top",
                      ha="center")
        self.gap(dy)
        if note:
            self.fig.text(0.5, self.y, note, fontsize=8.5, color=MUTED,
                          va="top", ha="center")
            self.gap(0.020)

    def rule(self):
        self.gap(0.008)
        self.fig.add_artist(plt.Line2D([L, R], [self.y, self.y], color=RULE,
                                       lw=0.8))
        self.gap(0.016)

    def close(self):
        self.pdf.savefig(self.fig)
        plt.close(self.fig)


# ── helpers ──────────────────────────────────────────────────────────────────

CIRCUITRY = ("/Users/genestoner/Library/Mobile Documents/com~apple~CloudDocs/Documents/"
             "MATLAB/TurkeyResearchII/LatestTurkey/ToyModel/fig_model%s_circuitry.png")


def figure_page(pdf, which, title, caption):
    """A full-width circuitry drawing, one model per page."""
    p = Page(pdf, running="Where the attentional bias enters")
    p.h2(title, DRIVE if which == "III" else POOLC)
    p.body(caption)
    img = plt.imread(CIRCUITRY % which)
    h = (R - L) * (img.shape[0] / img.shape[1]) * (PAGE[0] / PAGE[1])
    ax = p.fig.add_axes([L, p.y - h - 0.010, R - L, h])
    ax.imshow(img); ax.axis("off")
    p.gap(h + 0.024)
    return p


def table(page, headers, rows, colx, size=9.5, hsize=9.0):
    """A plain left-aligned table; colx are figure-coordinate x positions."""
    for x, htxt in zip(colx, headers):
        page.fig.text(x, page.y, htxt, fontsize=hsize, color=MUTED, va="top",
                      fontweight="bold")
    page.gap(0.017)
    page.fig.add_artist(plt.Line2D([L, R], [page.y + 0.004, page.y + 0.004],
                                   color=RULE, lw=0.8))
    page.gap(0.004)
    for row in rows:
        for x, cell in zip(colx, row):
            bold = cell.startswith("*")
            page.fig.text(x, page.y, cell.lstrip("*"), fontsize=size,
                          color=INK if bold else INK2, va="top",
                          fontweight="bold" if bold else "normal")
        page.gap(0.0175)
    page.gap(0.008)


DRIVE, POOLC = "#b86b26", "#33578c"


# ── the document ─────────────────────────────────────────────────────────────

def build(out="bias_locus.pdf"):
    with PdfPages(out) as pdf:
        # ═══════════════════════════════════════════════════════ page 1
        p = Page(pdf)
        p.h1("Where the attentional bias enters")
        p.fig.text(L, p.y, "Model III and Model IV of the hypercolumn / point-set model",
                   fontsize=12, color=INK2, va="top")
        p.gap(0.030)
        p.fig.text(L, p.y, "2026-08-20  ·  second pass, rewritten against the code",
                   fontsize=9, color=MUTED, va="top")
        p.gap(0.030)
        p.rule()

        p.h2("The answer, first")
        p.body("""Two versions of the model differ in exactly one respect: where the
            top-down attentional bias is applied. They are not new and they are not
            unnamed. They are Model III (bias on the drive) and Model IV (bias into the
            pool), built and compared on 2026-07-19, and they are implemented behind a
            single boolean, prm.biasInPool.""")
        p.body("""Exactly two engines implement both routes: toy_color.m (two surfaces)
            and pointset/hcps_grid.m (the 121-point-set grid). Every other file that
            mentions the flag is a driver that sets it. The locked operating point sets
            it TRUE — hcps_op.m line 148 — so every published HC/PS number, and every
            figure on the website, is Model IV.""")
        p.body("""The first pass of this note closed by saying the two were not cleanly
            separated in our code and that ps_pointset.py might be running Model III.
            That was a misreading. ps_pointset.py is a different model — motion only,
            two V1 hypercolumns, no colour hypercolumn, global normalization — and its
            FB term is like-to-like MT->V1 stimulus feedback, not the top-down bias.""")

        p.h2("Common scaffolding")
        p.body("""Index a point-set by p, an attribute by a (motion or colour), and a
            channel within an attribute by theta — eight directions, eight hues.""")
        p.eq("$u^{a}_{\\theta}(p,t)$        feedforward stimulus drive to a channel",
             size=11)
        p.eq("$a_{\\theta}$        top-down bias: a graded von Mises bump, $0$ to "
             "biasAmp", size=11)
        p.eq("$S(p,t)$        cooperative pool — ONE per point-set, shared across "
             "attributes", size=11)
        p.eq("$G(p,t) = 1 + \mathrm{CoopL}\, S(p,t)$        the cooperative gain",
             size=11)
        p.gap(0.006)
        p.body("""Both routes then normalize identically. The drive is raised to the
            power n BEFORE it is pooled, over channels and then over space:""")
        p.eq("$R^{a}_{\\theta}(p) \; = \; \dfrac{R_{max}\,[\,D^{a}_{\\theta}(p)\,]^{n}}"
             "{\sigma^{n} + w \sum_{p'} W_{n}(p,p') \sum_{\\theta'} "
             "[\,D^{a}_{\\theta'}(p')\,]^{n}}$", dy=0.070)
        p.body("""The denominator is FLAT across channels — one per point-set per
            attribute — because normKapDir and normKapHue are 0, which makes the featural
            kernel all-ones. That is a parameter, not a structural property. It is also
            WITHIN attribute (featureNorm true), so motion and colour have separate
            denominators. Page 6 shows that this last choice is what makes Model IV's
            headline prediction contingent rather than structural.""")
        p.close()

        # ═══════════════════════════════════════════════════════ page 2
        p = Page(pdf, running="Where the attentional bias enters")
        p.h2("The two routes, in the code's own algebra")
        p.body("""Verbatim from hcps_grid.m lines 222-240 and toy_color.m lines 67-75,
            which agree with each other.""")

        p.h2("Model III — bias on the drive", DRIVE)
        p.body("""The bias joins the cooperative term inside a single gain factor on the
            feedforward drive. The pool integrates the cells' plain responses.""")
        p.eq("$D^{a}_{\\theta} \; = \; u^{a}_{\\theta} \, "
             "(\, 1 + a_{\\theta} + \mathrm{CoopL}\, S \,)$")
        p.eq("$\\tau_{S}\, \dot S \; = \; -S \; + \; \sum_{\\theta} R^{m}_{\\theta} "
             "\; + \; \sum_{\\theta} R^{c}_{\\theta}$", dy=0.052)

        p.h2("Model IV — bias into the pool", POOLC)
        p.body("""The drive carries no bias at all. The bias re-weights what the pool
            neuron sees, and the pool returns one scalar gain to every channel of both
            hypercolumns.""")
        p.eq("$D^{a}_{\\theta} \; = \; u^{a}_{\\theta} \, "
             "(\, 1 + \mathrm{CoopL}\, S \,)$")
        p.eq("$\\tau_{S}\, \dot S \; = \; -S \; + \; \sum_{\\theta} "
             "(\,1 + a_{\\theta}\,) R^{m}_{\\theta} \; + \; \sum_{\\theta} "
             "R^{c}_{\\theta}$", dy=0.052)

        p.rule()
        p.h2("Four corrections to the first pass")
        table(p, ["", "first pass said", "the code does"],
              [["*1", "$D \cdot A \cdot G$, multiplicative", "$u\,(1+a+\mathrm{CoopL}S)$ — ADDITIVE inside one gain"],
               ["*2", "pool integrates $A \cdot D$, the drive", "pool integrates $(1+a)R$, the RESPONSE"],
               ["*3", "a saturating $S()$ on the pool input", "pool input is linear; poolAct sits on its OUTPUT"],
               ["*4", "$A$ is $1{+}\\beta$ on one channel", "$a_{\\theta}$ is a graded von Mises bump over all eight"]],
              colx=[L, L + 0.045, L + 0.315], size=9.5)
        p.body("""Correction 1 matters: the multiplicative form carries a cross-term
            a·CoopL·S that the code does not have, so the first pass's clean "factor A"
            prediction does not follow from what we run. Correction 2 matters for the
            wiring: weighting R rather than D puts Model IV's synapse downstream of the
            divisive normalization, not upstream.""")
        p.close()

        # ═══════════════════════════════════════════════════════ pages 3-4
        figure_page(pdf, "III",
                    "Model III as circuitry — bias on the drive",
                    """One point-set: a motion hypercolumn and a colour hypercolumn
                    sharing one cooperative pool neuron. Every operation in the equations
                    above is drawn as a node. The tuned top-down axon terminates on each
                    motion cell's own summing node, upstream of the cooperative gain, so
                    the attended channel's own response is raised.""").close()
        figure_page(pdf, "IV",
                    "Model IV as circuitry — bias into the pool",
                    """The same drawing, with one thing moved. The identical tuned axon
                    now terminates on each motion cell's afferent to the pool, downstream
                    of the division. The V1 cells themselves are unbiased; only what the
                    pool neuron sees is weighted. Compared with page 3, the hypercolumns,
                    the pool, the normalizer and the afferents are pixel-identical.""").close()

        # ═══════════════════════════════════════════════════════ page 5
        p = Page(pdf, running="Where the attentional bias enters")
        p.h2("What each predicts, and what it measures")
        p.body("""Under Model IV every channel of a point-set is multiplied by the same
            scalar G, so for any channel the cued/uncued ratio is (G_c/G_u)^n divided by
            the ratio of the denominators, and the per-channel drive cancels. If the
            motion and colour denominators move together, the attention index is then
            IDENTICAL for motion and for colour. Under Model III the attended channel
            additionally carries a_theta, so colour can only gain second-hand, through
            the pool.""")
        p.body("""Measured with pointset/hcps_bias_locus_check.m, 8 seeds, reading
            primary (motion DOWN), colour (V4 GREEN) and translation (motion RIGHT).
            Model III and Model IV are shown at MATCHED primary AI in the toy, where
            biasAmp can be bisected; on the grid both run at the locked biasAmp 16, so
            compare the colour/primary RATIO rather than the raw colour number.""")

        p.gap(0.006)
        p.fig.text(L, p.y, "toy_color.m — 2 surfaces, one shared normalizer "
                   "(featureNorm false)", fontsize=10, color=INK, va="top",
                   fontweight="bold")
        p.gap(0.026)
        table(p, ["route", "biasAmp", "primary", "colour", "translation"],
              [["*Model III  on drive", "1.00", "+0.6081", "+0.1022", "+0.2321"],
               ["*Model IV   in pool", "9.63", "+0.6081", "*+0.6081", "+0.4886"]],
              colx=[L, L + 0.20, L + 0.31, L + 0.44, L + 0.57])
        p.body("""Model IV's primary and colour agree to 1.1e-16 — machine epsilon.
            Model III's colour is 16.8% of its primary: a real transfer, but a small
            one.""", indent=0.02, size=9.5)

        p.gap(0.010)
        p.fig.text(L, p.y, "hcps_grid.m — 121 point-sets at the LOCKED operating point "
                   "(featureNorm true)", fontsize=10, color=INK, va="top",
                   fontweight="bold")
        p.gap(0.026)
        table(p, ["route", "primary", "colour", "translation", "colour/primary"],
              [["*Model III  on drive", "+0.9875", "+0.0389", "+0.8141", "3.9%"],
               ["*Model IV   in pool", "+0.1996", "*+0.1996", "+0.2058", "*100.0%"]],
              colx=[L, L + 0.20, L + 0.33, L + 0.46, L + 0.60])
        p.body("""So the separation is not subtle. Model III sends 4% of its motion
            enhancement to colour; Model IV sends all of it. logs/PARAMETERS.md line 61
            says Model III gives "motion enhancement with no colour transfer" — that is
            right to within noise on the grid with a shared normalizer (colour AI
            -0.0005), an understatement at the locked point (3.9%), and wrong at the toy
            scale (16.8%). The qualitative claim holds everywhere; the magnitude is
            regime-dependent and should be quoted with its regime.""", indent=0.02,
               size=9.5)
        p.body("""One regime is unusable and is reported here so it is not tried again:
            with normW = 0 the toy has no denominator, runs away (max response 1e115) and
            saturates every index to +/-1. Pure facilitation needs the normalizer to stay
            bounded — the Model I to Model II lesson.""", indent=0.02, size=9.5)
        p.close()

        # ═══════════════════════════════════════════════════════ page 6
        p = Page(pdf, running="Where the attentional bias enters")
        p.h2("The equality is contingent, not structural")
        p.body("""The first pass claimed that no free parameter can move Model IV off
            primary = colour, and that this is what makes the comparison worth running.
            The website's viewer caption makes the same claim, saying the two indices
            "land on top of each other to three decimals, and that equality IS the
            transfer". At the locked operating point that claim is false as stated.""")
        p.body("""Model IV's equality is exact only when the motion and colour
            denominators move together. With featureNorm FALSE they are literally the
            same variable (hcps_grid.m lines 251-252), so the equality is structural and
            no parameter touches it. With featureNorm TRUE — the locked default — they
            are separate pools, and the equality survives only because the two drive
            profiles happen to have the same shape: ffNorm rescales both to the same
            total, and kappa equals kappaHue equals 2, so their sums of powers coincide.""")
        p.body("""Tested by detuning the hue width alone, everything else held at the
            locked point (pointset/hcps_bias_locus_ablate.m):""")
        p.gap(0.004)
        table(p, ["kappaHue", "primary", "colour", "|primary - colour|",
                  "profile mismatch"],
              [["*2.00  (= kappa)", "+0.199648", "+0.199648", "*2.78e-17", "8.6e-16"],
               ["2.50", "+0.199570", "+0.198723", "8.47e-04", "2.1e-01"],
               ["4.00", "+0.199214", "+0.196691", "2.52e-03", "8.9e-01"],
               ["8.00", "+0.198586", "+0.194135", "4.45e-03", "2.6e+00"]],
              colx=[L, L + 0.19, L + 0.32, L + 0.45, L + 0.66])
        p.body("""The proposed cause and the effect move together: the equality leaves
            machine epsilon exactly when the drive profiles stop matching, and a 25%
            detune costs four orders of magnitude. So kappaHue IS a free parameter that
            moves Model IV off equality. The prediction is still sharp and still worth
            testing — 100% transfer against 4% is not a close call — but it should be
            stated as resting on matched tuning widths, and the viewer caption should be
            corrected.""")

        p.rule()
        p.h2("Where each route is implemented")
        table(p, ["file", "what it is"],
              [["*toy_color.m  67-75", "2 surfaces; origin of the III / IV distinction"],
               ["*hcps_grid.m  222-240", "the 121-point-set grid engine; what the site runs"],
               ["hcps_grid_adapt.m", "same two-site switch (fbSite) for MT->V1 feedback"],
               ["ps_pointset.py", "a DIFFERENT model: motion only, no colour HC"]],
              colx=[L, L + 0.27])
        p.body("""Two drivers already sweep both routes — hcps_bias_route_atop.m and
            hcps_grid_biasout.m — but both run at stale operating points and neither has
            a stored result anywhere in the repo. Do not cite them.""", size=9.5)
        p.body("""Still open: ps_pointset.py's docstring claims an object-based bias on
            hypercolumn B, while its code applies a feature-based bias to both
            hypercolumns. And lib/hcpsDefaults.ts on the website still exports ffFloor
            1e-06 and hash d0ea82, which hcps_op.m superseded on 2026-07-28.""",
               size=9.5)
        p.close()

    print(f"wrote {out}  (6 pages)")


if __name__ == "__main__":
    build()
