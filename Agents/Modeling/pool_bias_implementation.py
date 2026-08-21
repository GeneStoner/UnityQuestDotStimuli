"""
Implementing the pool bias — what the anatomy allows.

Builds `pool_bias_implementation.pdf`. Companion to bias_locus.pdf, which settled WHICH
model we run (Model IV, bias into the pool). This one asks the next question, GS's:
what circuitry would actually implement it, how many neurons, and is it realistic?

Reuses the Page typesetting helpers from bias_locus.py (same directory), so the two
documents share a look. Equations are matplotlib mathtext -- keep them simple and CHECK
every one renders rather than trusting the string (\\bigl, \\underline, \\theta-after-a-
non-raw-quote have all bitten already).

Run:  /usr/bin/python3 pool_bias_implementation.py
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from bias_locus import Page, PAGE, L, R, INK, INK2, MUTED, RULE, BIAS, POOL

DRIVE, POOLC, GOOD, BAD = "#b86b26", "#33578c", "#2f7a3f", "#a33028"
FIG = ("/Users/genestoner/Library/Mobile Documents/com~apple~CloudDocs/Documents/MATLAB/"
       "TurkeyResearchII/LatestTurkey/ToyModel/fig_modelIVD_profile.png")


def table(page, headers, rows, colx, size=9.5, hsize=9.0):
    for x, h in zip(colx, headers):
        page.fig.text(x, page.y, h, fontsize=hsize, color=MUTED, va="top", fontweight="bold")
    page.gap(0.017)
    page.fig.add_artist(plt.Line2D([L, R], [page.y + 0.004, page.y + 0.004], color=RULE, lw=0.8))
    page.gap(0.005)
    for row in rows:
        for x, cell in zip(colx, row):
            col, txt = INK2, cell
            if cell.startswith("*"):  col, txt = INK,  cell[1:]
            if cell.startswith("+"):  col, txt = GOOD, cell[1:]
            if cell.startswith("-"):  col, txt = BAD,  cell[1:]
            page.fig.text(x, page.y, txt, fontsize=size, color=col, va="top",
                          fontweight="bold" if cell.startswith(("*", "+")) else "normal")
        page.gap(0.0178)
    page.gap(0.008)


def ref(page, tag, text):
    page.fig.text(L, page.y, tag, fontsize=9, color=POOLC, va="top", fontweight="bold")
    for i, line in enumerate(text):
        page.fig.text(L + 0.055, page.y, line, fontsize=9, color=INK2, va="top")
        page.gap(0.0165)
    page.gap(0.006)


def build(out="pool_bias_implementation.pdf"):
    with PdfPages(out) as pdf:
        # ═══════════════════════════════════════════════ page 1
        p = Page(pdf)
        p.h1("Implementing the pool bias")
        p.fig.text(L, p.y, "What circuitry Model IV would need, and what the anatomy allows",
                   fontsize=12, color=INK2, va="top")
        p.gap(0.030)
        p.fig.text(L, p.y, "2026-08-20  ·  companion to bias_locus.pdf", fontsize=9,
                   color=MUTED, va="top")
        p.gap(0.030)
        p.rule()

        p.h2("The question")
        p.body("""bias_locus.pdf settled which model we run: Model IV, the bias into the pool.
            The pool neuron integrates the attention-weighted responses of its point-set,""")
        p.eq(r"$\tau_S\,\dot S \; = \; -S \; + \; \sum_{\theta}\,(\,1+a_{\theta}\,)\,R_{\theta}$",
             dy=0.052)
        p.body("""while the cells' own drive carries no bias at all. Read literally that says
            each V1 cell's synapse onto the pool is individually weighted by a direction-tuned
            top-down signal. That is a strong anatomical claim, and it is the one GS questioned:
            it would need a synapse type that may not exist.""")
        p.body("""Three further things make the literal reading hard. The weighting must be
            PATHWAY-SPECIFIC, because the same V1 cell also projects to MT and V4 and Model IV
            needs that copy left alone. It must be SYNAPSE-SPECIFIC, picking out one terminal
            among those converging on a single pool neuron. And it must be RE-ADDRESSABLE, since
            the attended direction changes from trial to trial.""")

        p.h2("Four ways it could be built")
        table(p, ["implementation", "cells / point-set", "what it needs"],
              [["*Model III (for comparison)", "17", "tuned feedback onto V1 dendrites"],
               ["-IV, axo-axonic on terminals", "17", "a synapse type not evidenced in cortex"],
               ["IV, match-cell bank", "25", "a parallel tuned population"],
               ["+IV, dendritic gating of the pool cell", "+17", "+feedback onto the POOL cell's dendrites"]],
              colx=[L, L + 0.34, L + 0.50])
        p.body("""Counts are per point-set for motion plus colour, with one pool neuron shared
            across attributes; multiply by 121 for the locked grid. The recommendation is the
            last row, and the rest of this note is the evidence for it.""")
        p.close()

        # ═══════════════════════════════════════════════ page 2
        p = Page(pdf, running="Implementing the pool bias")
        p.h2("What the anatomy says")

        p.h2("Feedback lands on dendrites, and acts branch by branch", POOLC)
        ref(p, "[1]", [
            "Cortico-cortical feedback engages active dendrites in visual cortex.",
            "Nature 2023 (LM to V1, mouse; all-optical connectivity mapping).",
            "nature.com/articles/s41586-023-06007-6"])
        p.body("""\"A substantial proportion of feedback inputs innervate pyramidal cell apical
            dendrites in layer 1.\" Individual feedback-recipient SPINES were identified on
            apical tufts. The effect is branch-specific: stimulating the feedback input
            \"preferentially enhanced calcium signals in the branch containing the activated
            spine relative to the reference branch.\" There is no mention of feedback contacting
            axons or axon terminals.""", indent=0.02)

        p.h2("Cortical axo-axonic synapses exist, but gate the WHOLE output", BAD)
        ref(p, "[2]", [
            "Theory of axo-axonic inhibition. PLOS Comput Biol 2025.",
            "Specific and comprehensive genetic targeting reveals brain-wide distribution",
            "and synaptic input patterns of GABAergic axo-axonic interneurons. 2024."])
        p.body("""The axon initial segment \"harbors GABA-A receptors contacted by interneurons,
            most of which are axo-axonic (chandelier) cells\" -- about 60% of the synapses on the
            proximal axon of mouse visual cortical cells. They are GABAergic, local, and control
            ACTION POTENTIAL INITIATION. That is decisive against the literal reading: modulating
            the initial segment gates everything the cell sends, so it cannot weight the pool's
            copy while sparing the MT / V4 copy.""", indent=0.02)

        p.h2("Presynaptic modulation of cortical terminals is real but diffuse", BAD)
        ref(p, "[3]", [
            "Pre- and postsynaptic activation of GABA-B receptors modulates principal cell",
            "excitation in the piriform cortex. 2018."])
        p.body("""Presynaptic GABA-B receptors do sit on intracortical glutamatergic terminals
            and do reduce excitatory input. But they are engaged HETEROSYNAPTICALLY, by spillover
            -- diffuse, and inhibitory. Nothing here is a tuned, terminal-selective,
            trial-by-trial re-addressable projection.""", indent=0.02)

        p.h2("Dendrites order their inputs by tuning", GOOD)
        ref(p, "[4]", [
            "Wilson, Whitney, Scholl & Fitzpatrick. Orientation selectivity and the functional",
            "clustering of synaptic inputs in primary visual cortex. Nat Neurosci 2016.",
            "nature.com/articles/nn.4323"])
        p.body("""Dendritic spines cluster according to orientation preference; the degree of
            clustering on a single neuron PREDICTS its somatic orientation selectivity, and
            branches carrying co-tuned clusters show more local dendritic calcium events. So a
            dendritic tree can carry its afferents in tuning order.""", indent=0.02)
        p.close()

        # ═══════════════════════════════════════════════ page 3
        p = Page(pdf, running="Implementing the pool bias")
        p.h2("The implementation the anatomy allows")
        p.body("""Put [1] and [4] together. Model IV needs the pool's copy of the response
            weighted and the read-out's copy untouched. PATHWAY SPECIFICITY IS FREE ON THE
            POSTSYNAPTIC SIDE: modulate the pool neuron's dendrite and the V1 cell is never
            touched at all, so its projection to MT and V4 is unaffected by construction.""")
        p.body("""If the V1-to-pool synapses are arranged on the pool cell's tree in tuning order
            -- which [4] says dendrites do -- then an ordinary layer-1 feedback axon running
            through that tree, making en-passant synapses branch by branch with strength
            proportional to the attention profile, computes""")
        p.eq(r"$\sum_{\theta}\,a_{\theta}\,R_{\theta}$", dy=0.048)
        p.body("""which added to the plain sum the pool already takes gives exactly the Model IV
            pool input. No axo-axonic synapse. No parallel population. No extra neurons, and the
            synapse type is the one [1] documents, branch specificity included.""")
        p.gap(0.008)
        img = plt.imread(FIG)
        h = (R - L) * (img.shape[0] / img.shape[1]) * (PAGE[0] / PAGE[1])
        ax = p.fig.add_axes([L, p.y - h - 0.010, R - L, h]); ax.imshow(img); ax.axis("off")
        p.gap(h + 0.026)
        p.body("""Figure: fig_modelIVD_profile.png, from ToyModel/fig_bias_profile.py IVD.
            The gain column is flat -- attention is absent from it -- and the tuned feedback axon
            instead runs down the pool cell's dendritic field, its bouton on each branch scaled
            by the model's own bias profile.""", size=9)

        p.close()

        # ═══════════════════════════════════════════════ page 4
        p = Page(pdf, running="Implementing the pool bias")
        p.h2("What this rests on, and what is NOT established", BAD)
        p.body("""The NEGATIVE half of the argument is well supported. [2] and [3] between them
            say that the only cortical machinery for modulating a cell's axonal output either
            gates the entire output (the initial segment) or is diffuse and inhibitory
            (presynaptic receptors on terminals). Nothing found supports a tuned,
            terminal-selective, trial-by-trial re-addressable modulation, so the literal reading
            of Model IV should be set aside.""", size=9.5)
        p.body("""The POSITIVE proposal is SUGGESTIVE, not established. It rests on two steps
            that the cited work does not actually demonstrate:""", size=9.5)
        p.body("""(a) that the pool cell's afferents are arranged on its tree IN TUNING ORDER.
            [4] shows spines CLUSTER by orientation preference and that the degree of clustering
            predicts somatic selectivity. Clustering is not the same thing as a systematic
            one-channel-per-branch map, which is what the figure draws. On this point the figure
            is schematic, and deliberately so.""", size=9.5, indent=0.025)
        p.body("""(b) that feedback can select branches BY THE TUNING OF THE INPUTS THEY CARRY.
            [1] gives branch-specific feedback effects, but its organising variable is
            RETINOTOPIC rather than featural -- so on its own evidence it does not supply
            feature-selective branch targeting. This is the weakest link in the proposal, and it
            is the same assumption flagged overleaf.""", size=9.5, indent=0.025)
        p.body("""Two further limits worth stating plainly. The cooperative pool neuron is a
            MODEL CONSTRUCT: no cell type has been identified with its properties. And the search
            behind this note was a handful of targeted queries on 2026-08-20, not a systematic
            review -- primate EM work on feedback synaptic targets was not retrieved, and nothing
            here rests on it.""", size=9.5)
        p.close()

        # ═══════════════════════════════════════════════ page 5
        p = Page(pdf, running="Implementing the pool bias")
        p.h2("What this costs, and what it does not settle")
        p.body("""The dendritic version costs exactly what Model III costs -- 17 neurons per
            point-set, 2057 on the locked grid -- so the choice between the two routes is no
            longer a choice about how much machinery the brain must find. That reverses the
            earlier reading, on which Model IV looked roughly one and a half times as expensive.
            What separates them now is only WHERE the same tuned feedback lands: on the V1
            cells' dendrites (III), or on the pool cell's (IV).""")

        p.h2("An assumption BOTH models make, and [1] does not support", BAD)
        p.body("""The feedback in [1] is organised RETINOTOPICALLY, not by feature: a relatively
            suppressive centre and a relatively facilitating surround, indexed by position in
            visual space rather than by the stimulus. Model III and Model IV both assume a
            DIRECTION-TUNED top-down signal, and that study does not supply one. It is mouse
            LM-to-V1 and a single paper, and primate feature-similarity gain implies
            feature-specific top-down signals exist somewhere -- but the tuned bias should be
            carried as an assumption, not as an established fact.""")

        p.h2("The physiological test, already measured in the model", GOOD)
        p.body("""Whichever implementation is used, the two routes differ in a way single units
            can see. Cued/uncued response ratio per direction channel, within one point-set:""")
        table(p, ["", "within one point-set", "pooled across point-sets"],
              [["*Model III", "spread ~28,000x", "27,026x"],
               ["*Model IV", "median 1.03", "1.84x"]],
              colx=[L, L + 0.16, L + 0.46])
        p.body("""Model III suppresses the non-preferred channels to 0.006 of their uncued rate
            while boosting the preferred one 159-fold; Model IV multiplies the whole column by
            one number. Near-uniform modulation across a hypercolumn versus strong tuning is the
            cleanest discriminator we have, and unlike the colour index it does not depend on the
            read-out stage. Scripts: hcps_modtuning_check.m, hcps_modtuning_percell.m.""")
        p.body("""Model IV's within-column modulation is not EXACTLY flat -- median spread 1.031
            rather than 1.000 -- and that is the cells' own leaky integration, not a breach of
            the one-scalar structure: R lags D, so channels whose drive has a different time
            course integrate different stretches of the gain trajectory. Confirmed by ablation
            (hcps_flatness_ablate.m): at tau 0.15 the spread is 1.000000 to all printed digits,
            while shrinking the pool's tau_E instead barely moves it.""")

        p.rule()
        p.h2("References")
        for tag, txt in [
            ("[1]", "Cortico-cortical feedback engages active dendrites in visual cortex. Nature, 2023."),
            ("[2]", "Theory of axo-axonic inhibition. PLOS Computational Biology, 2025.  ·  Genetic"),
            ("  ", "targeting of GABAergic axo-axonic interneurons: brain-wide distribution, 2024."),
            ("[3]", "Pre- and postsynaptic activation of GABA-B receptors modulates principal cell"),
            ("  ", "excitation in the piriform cortex, 2018."),
            ("[4]", "Wilson, Whitney, Scholl & Fitzpatrick. Orientation selectivity and the functional"),
            ("  ", "clustering of synaptic inputs in primary visual cortex. Nature Neuroscience, 2016.")]:
            p.fig.text(L, p.y, tag, fontsize=9, color=POOLC, va="top", fontweight="bold")
            p.fig.text(L + 0.048, p.y, txt, fontsize=9, color=INK2, va="top")
            p.gap(0.0168)
        p.gap(0.010)
        p.body("""Searched 2026-08-20; full notes with URLs in the project memory file
            feedback-synapse-targets-lit.md. These are the sources the claims above rest on --
            anything not attributed here is model measurement, not literature.""", size=9)
        p.close()

    print(f"wrote {out}  (5 pages)")


if __name__ == "__main__":
    build()
