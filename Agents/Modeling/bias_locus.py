"""
Where the attentional bias enters — two variants of the HC / PS model.

Builds `bias_locus.pdf`: a short technical note stating the two versions of the
hypercolumn / point-set model that differ ONLY in where the top-down bias is
applied, with the equations for each and the measurement that separates them.

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


# ── the wiring comparison ────────────────────────────────────────────────────

def _variant(ax, x0, bias_to_pool, n, subtitle):
    """One point-set, with the bias arriving either at a channel or at the pool.

    The pool sits at the TOP so that NEITHER bias arrow has to cross a
    hypercolumn on its way in: variant 1 drops onto a motion channel, variant 2
    drops onto the pool, and the only thing that differs between the two panels
    is where that red arrow lands. An earlier layout put the pool at the bottom
    and variant 1's arrow speared straight through the colour HC, which read as
    the bias touching colour -- the exact opposite of the claim.
    """
    W, H = 44.0, 40.0
    ax.add_patch(Rectangle((x0, 6), W, H, fill=False, edgecolor=POOL, lw=1.6,
                           zorder=1))
    ax.text(x0 + W / 2, 68.0, f"Variant {n}", ha="center", va="bottom",
            fontsize=12.5, fontweight="bold", color=INK)
    ax.text(x0 + W / 2, 63.5, subtitle, ha="center", va="bottom",
            fontsize=9.5, color=MUTED)
    ax.text(x0 + 2.5, 44.0, "point-set  $p$", fontsize=8.5, color=POOL, va="top")

    cw, gap = 3.4, 0.9
    rows = ((26.0, MOTION, "motion HC"), (14.0, COLOUR, "colour HC"))
    for yy, col, lab in rows:
        ax.text(x0 + 3.0, yy + 4.8, lab, fontsize=8.5, color=col, va="bottom")
        for k in range(8):
            hot = (not bias_to_pool) and lab.startswith("motion") and k == 5
            ax.add_patch(Rectangle((x0 + 3.0 + k * (cw + gap), yy), cw, 4.0,
                                   facecolor=BIAS if hot else "#f2f1ee",
                                   edgecolor=col, lw=0.8, zorder=3))

    ex, ey = x0 + W - 9.0, 40.0
    ax.add_patch(Circle((ex, ey), 4.6, facecolor="white", edgecolor=POOL,
                        lw=1.8, zorder=4))
    ax.text(ex, ey, "$E$", ha="center", va="center", fontsize=11, color=POOL,
            zorder=5)

    # the pool returns ONE gain to every channel of both hypercolumns
    for yy, _, _ in rows:
        ax.add_patch(FancyArrowPatch((ex - 2.0, ey - 4.4), (x0 + 38.0, yy + 2.0),
                                     arrowstyle="-|>", mutation_scale=9,
                                     color=POOL, lw=1.0, alpha=0.85,
                                     connectionstyle="arc3,rad=-0.30", zorder=2))
    ax.text(x0 + W / 2, 9.5, "$G = 1+\\lambda E$  to every channel", fontsize=9,
            color=POOL, ha="center")

    tip = ((ex, ey + 5.2) if bias_to_pool
           else (x0 + 3.0 + 5 * (cw + gap) + cw / 2, 30.4))
    tail = (tip[0], 56.0)
    ax.add_patch(FancyArrowPatch(tail, tip, arrowstyle="-|>", mutation_scale=13,
                                 color=BIAS, lw=2.0, zorder=6))
    ax.text(tail[0], 57.5, "$A$", ha="center", va="bottom", fontsize=12,
            color=BIAS, fontweight="bold")


def wiring_figure(page):
    ax = page.fig.add_axes([L, page.y - 0.310, R - L, 0.300])
    ax.set_xlim(0, 108); ax.set_ylim(0, 74)
    ax.set_aspect("equal"); ax.axis("off")
    _variant(ax, 4, False, 1, "bias on the CHANNEL")
    _variant(ax, 60, True, 2, "bias into the POOL")
    page.gap(0.325)


# ── the document ─────────────────────────────────────────────────────────────

def build(out="bias_locus.pdf"):
    with PdfPages(out) as pdf:
        # ---- page 1
        p = Page(pdf)
        p.h1("Where the attentional bias enters")
        p.fig.text(L, p.y, "Two variants of the hypercolumn / point-set model",
                   fontsize=12, color=INK2, va="top")
        p.gap(0.030)
        p.fig.text(L, p.y, "2026-08-20", fontsize=9, color=MUTED, va="top")
        p.gap(0.030)
        p.rule()

        p.body("""Two versions of the basic hypercolumn / point-set model are on the
            table. They share their architecture completely — a point-set holding a
            motion hypercolumn and a colour hypercolumn, a single cooperative pool per
            point-set that is shared across attributes, and divisive normalization that
            is within attribute and flat across channels. They differ in exactly one
            respect: where the top-down attentional bias is applied.""")
        p.body("""That single difference decides whether attending to one feature
            enhances the other attributes of the same surface by the SAME amount, or by
            a strictly smaller one. It is therefore the difference the data can see.""")

        p.h2("Common scaffolding")
        p.body("""Index a point-set by p, an attribute by a (motion or colour), and a
            channel within an attribute by theta — eight directions, eight hues.""")
        p.eq("$D^{a}_{\\theta}(p,t)$        feedforward stimulus drive to a channel",
             size=11)
        p.eq("$A^{a}_{\\theta}$        top-down bias:  $1+\\beta$ on the attended "
             "channel, $1$ elsewhere", size=11)
        p.eq("$E(p,t)$        cooperative pool — ONE per point-set, shared across "
             "attributes", size=11)
        p.eq("$G(p,t) = 1 + \\lambda\\, E(p,t)$        the cooperative gain", size=11)
        p.gap(0.006)
        p.body("""Both variants then normalize and rectify identically. Writing the
            numerator of a channel as P:""")
        p.eq("$N^{a}(p,t) \\; = \\; \\sum_{p'} w(p,p') \\, \\sum_{\\theta} "
             "P^{a}_{\\theta}(p',t)$",
             "within attribute, across space", dy=0.055)
        p.eq("$R^{a}_{\\theta}(p,t) \\; = \\; \\dfrac{[\\,P^{a}_{\\theta}(p,t)\\,]^{2}}"
             "{\\sigma^{2} + N^{a}(p,t)}$", dy=0.062)
        p.body("""The denominator being FLAT across channels — one per point-set per
            attribute — is load-bearing. Were normalization per-channel, each channel's
            denominator would track its own numerator and the shared gain would divide
            straight back out.""")
        p.close()

        # ---- page 2
        p = Page(pdf, running="Where the attentional bias enters")
        p.h2("The one structural difference")
        p.body("""Everything above is common. The variants differ only in which arrow
            the bias A travels along:""")
        wiring_figure(p)
        p.rule()

        p.h2("Variant 1 — bias on the channel", BIAS)
        p.body("""The bias multiplies the stimulus drive of the attended channel
            directly. That channel is then enhanced twice — once by the bias, and again
            by the pool gain it helped create — while every other channel in the
            point-set is enhanced only by the pool gain.""")
        p.eq("$P^{a}_{\\theta} \\; = \\; D^{a}_{\\theta} \\cdot A^{a}_{\\theta} "
             "\\cdot G$")
        p.eq("$\\tau_{E}\\, dE/dt \\; = \\; -E \\; + \\; S\\left( \\sum_{a} "
             "\\sum_{\\theta} P^{a}_{\\theta} \\right)$",
             "$S$ = saturating nonlinearity", dy=0.052)

        p.h2("Variant 2 — bias into the pool", BIAS)
        p.body("""The bias appears only in what drives the pool. It therefore selects
            which point-sets acquire a strong pool, but once the pool has settled it
            returns one gain, applied identically to every channel the point-set
            holds.""")
        p.eq("$P^{a}_{\\theta} \\; = \\; D^{a}_{\\theta} \\cdot G$")
        p.eq("$\\tau_{E}\\, dE/dt \\; = \\; -E \\; + \\; S\\left( \\sum_{a} "
             "\\sum_{\\theta} A^{a}_{\\theta} \\, D^{a}_{\\theta} \\right)$", dy=0.052)
        p.close()

        # ---- page 3
        p = Page(pdf, running="Where the attentional bias enters")
        p.h2("What each predicts")
        p.body("""Compare a point-set carrying the attended feature (cued, gain
            $G_c$) against one that does not (uncued, gain $G_u$). Because the
            normalization denominator is flat across channels, the gain does not cancel,
            and the response ratio for a channel is:""")
        p.gap(0.008)
        p.fig.text(L + 0.03, p.y, "Variant 1", fontsize=10.5, fontweight="bold",
                   color=BIAS, va="top")
        p.gap(0.026)
        p.eq("attended channel:   $R_{c}/R_{u} \\; \\propto \\; "
             "\\left( A \\, G_{c}/G_{u} \\right)^{2}$", size=12, dy=0.036)
        p.eq("every other channel:   $R_{c}/R_{u} \\; \\propto \\; "
             "\\left( G_{c}/G_{u} \\right)^{2}$", size=12, dy=0.036)
        p.body("""Transfer to colour, and to the translation that arrives later, is
            carried entirely by the pool term. It is real, but strictly smaller than the
            primary attended feature's enhancement, by the factor A.""", indent=0.03)
        p.gap(0.010)
        p.fig.text(L + 0.03, p.y, "Variant 2", fontsize=10.5, fontweight="bold",
                   color=BIAS, va="top")
        p.gap(0.026)
        p.eq("every channel:   $R_{c}/R_{u} \\; \\propto \\; "
             "\\left( G_{c}/G_{u} \\right)^{2}$", size=12, dy=0.036)
        p.body("""Identical for the attended direction, for colour, and for the
            translation. Selection is anchored to the point-set, not to the feature.""",
               indent=0.03)

        p.rule()
        p.h2("The measurement that separates them")
        p.body("""Take the ratio of the colour index to the primary index within a
            cued point-set. Variant 2 predicts the two coincide; Variant 1 predicts
            colour sits below primary by a factor set by beta. No free parameter can
            move Variant 2 off equality — the equality is structural, which is what
            makes the comparison worth running.""")

        p.rule()
        p.h2("Open — to settle before either is reported")
        p.body("""The two variants are not yet cleanly separated in our own code, and
            the question is which one we are actually running.""")
        p.body("""The site's schematic (components/HCPSFlow.tsx) states that the bias
            "enters the pool, not the channels, which is why it cannot stay confined to
            the attribute that was cued". That is Variant 2, explicitly.""", indent=0.02)
        p.body("""But ps_pointset.py's engine reads
            PSP = K x FB(like-to-like MT->V1) x Coop(1 + CoopL x E) / Norm.
            A like-to-like feedback term is channel-specific, which puts it in the
            position of A in Variant 1.""", indent=0.02)
        p.body("""Whether those are the same model described twice, or two different
            models, has not been checked. It determines which set of equations above
            describes the results we have.""", indent=0.02)
        p.close()

    print(f"wrote {out}  (3 pages)")


if __name__ == "__main__":
    build()
