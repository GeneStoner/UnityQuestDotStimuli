"""Generate a self-contained HTML summary of the mtae project (base64-embedded figures)."""
import base64, os
HERE = os.path.dirname(os.path.abspath(__file__)); FIGS = os.path.join(HERE, "figs")


def img(name, w="100%"):
    with open(os.path.join(FIGS, name), "rb") as f:
        b = base64.b64encode(f.read()).decode()
    return f'<img style="width:{w};border-radius:6px;border:1px solid #2a2f3a" src="data:image/png;base64,{b}">'


SECTIONS = [
    ("1. A plain autoencoder reconstructs transparent motion — and truly uses motion",
     "recon_examples.png",
     "Trained across thousands of random two-surface translating dot clips, tested on unseen seeds: "
     "reconstruction is near-perfect (2.4% variance unexplained). The temporal-scramble control "
     "(<b>scramble.png</b>) proved it isn't per-frame copying — shuffling frame order makes reconstruction "
     "<b>6.5× worse</b>, so the bottleneck learned a smooth-motion code."),
    ("2. Motion is genuinely in the latent (scramble control)",
     "scramble.png",
     "Ordered reconstruction (row 2) is crisp; scrambled reconstruction (row 4) is smeared/ghosted. "
     "The model compresses via a smooth-motion prior (position + velocity), not five independent frames."),
    ("3. NEGATIVE: a distributed recurrent AE gives only WEAK attention",
     "headA_cueing.png",
     "A recurrent V1↔MT autoencoder (feedforward + feedback + lateral) denoises well (structure corr "
     "0.83–0.87), but clamping a surface's MT band barely biases V1: cueing peaks at only "
     "<b>~+0.10</b>, and the cue-A vs cue-B reconstructions are nearly identical. Reconstruction alone "
     "does <b>not</b> buy object-based selection — because reconstructing both surfaces together never "
     "requires the code to be <i>separable</i> into one surface."),
    ("4. POSITIVE: an object-FACTORED (slot) code gives selection FOR FREE",
     "slot_separated.png",
     "Two slots competing to explain the scene by common-fate velocity (each slot = a direction profile × "
     "a density map). Reading out <b>one slot</b> recovers <b>one surface</b> — selectivity <b>~1.0</b> for "
     "well-separated directions — with <b>no attention training and no cue</b>. slot→A matches surface A at "
     "its direction, slot→B matches surface B. Factorization, not attention training, was the missing "
     "ingredient — a concrete refinement of Cavanagh's claim."),
    ("5. Robust to non-separable, noisy motion",
     "slot_stress.png",
     "Breaking exact separability (each dot given its own jittered direction) degrades factoring "
     "<b>gracefully</b>, not catastrophically: selectivity 1.0 → 0.81 (30° jitter) → 0.45 (60°). It only "
     "fails when within-surface spread approaches between-surface separation — a genuine information "
     "limit, not a model flaw."),
]

ROWS = [
    ("Plain AE reconstruction (held-out)", "2.4% var. unexplained", "recon.py"),
    ("Motion used? (temporal scramble)", "6.5× worse when shuffled", "scramble_test.py"),
    ("Recurrent scaffold stability", "converges, gain 0.5–4.0", "recurrent_scaffold.py"),
    ("Structured feedback leverage", "reshapes V1 12–90%", "leverage_check.py"),
    ("Distributed recurrent AE — cueing", "~+0.10 (weak)", "head_a_recon.py"),
    ("Slot AE — one-slot readout selectivity", "+0.77 (up to ~1.0)", "slot_ae.py"),
    ("Selectivity vs separation", "0.08 (10°) → ~1.0 (90–180°)", "slot_probe.py"),
    ("Robustness to direction jitter", "1.0 → 0.81 (30°) → 0.45 (60°)", "stress_slot.py"),
    ("Rotation (flow-slot)", "fails; needs MST-like/iterative", "flow_slot.py"),
]

cards = "\n".join(
    f'<section><h2>{t}</h2>{img(fig)}<p>{cap}</p></section>' for t, fig, cap in SECTIONS)
rows = "\n".join(
    f'<tr><td>{a}</td><td class="num">{b}</td><td class="mono">{c}</td></tr>' for a, b, c in ROWS)

HTML = f"""<!doctype html><html><head><meta charset="utf-8"><title>MT-AE project — accomplishments</title>
<style>
 body{{margin:0;background:#0d1117;color:#c9d1d9;font:16px/1.6 -apple-system,Segoe UI,Roboto,sans-serif}}
 .wrap{{max-width:900px;margin:0 auto;padding:40px 24px 80px}}
 h1{{font-size:30px;margin:0 0 4px}} .sub{{color:#8b949e;margin:0 0 28px}}
 .thesis{{background:#161b22;border:1px solid #30363d;border-left:4px solid #3fb950;
   border-radius:8px;padding:18px 22px;margin:0 0 34px;font-size:18px}}
 .thesis b{{color:#3fb950}}
 section{{background:#161b22;border:1px solid #21262d;border-radius:10px;padding:20px 22px;margin:0 0 24px}}
 h2{{font-size:19px;margin:0 0 14px;color:#e6edf3}}
 section p{{margin:14px 0 0;color:#adbac7}}
 table{{width:100%;border-collapse:collapse;margin-top:8px;font-size:15px}}
 td{{padding:9px 10px;border-bottom:1px solid #21262d}} tr:last-child td{{border-bottom:none}}
 .num{{color:#58a6ff;text-align:right;white-space:nowrap}} .mono{{font-family:ui-monospace,monospace;color:#8b949e;font-size:13px}}
 b{{color:#e6edf3}} i{{color:#d2a8ff}}
 .next{{background:#161b22;border:1px solid #30363d;border-left:4px solid #d29922;border-radius:8px;padding:16px 20px}}
 .next h2{{color:#d29922}}
</style></head><body><div class="wrap">
<h1>MT autoencoder — object-based attention in transparent motion</h1>
<p class="sub">Translation-domain summary · 2026-07-07 · <span class="mono">VRDots/ToyModel/mtae/</span></p>
<div class="thesis">Cavanagh's "object-based attention emerges <b>for free</b> from autoencoding" holds
<b>only if the code is object-factored</b>. A plain distributed autoencoder reconstructs beautifully but
gives weak selection (~0.10); give the bottleneck object structure (slots) and selection appears for free
(~1.0). <b>Factorization, not attention training, is the missing ingredient.</b></div>
{cards}
<section><h2>Results at a glance</h2>
<table>{rows}</table></section>
<div class="next"><h2>Open in the translation domain</h2>
<p>Fold slots into the recurrent V1↔MT scaffold (in progress) · head B on the <i>swap</i> cueing effect
(not basic cueing — that falls out of normalization) · connect to behavioral data (density knob).
Rotation is the frontier: needs MST-like complex-motion templates or iterative flow-consistency routing.</p></div>
</div></body></html>"""

out = os.path.join(HERE, "accomplishments.html")
with open(out, "w") as f:
    f.write(HTML)
print("wrote", out)
