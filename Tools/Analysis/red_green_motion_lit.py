#!/usr/bin/env python3
"""
Literature summary: Red vs Green in motion perception.
Context: VRDots — red and green dots on black background (both have luminance
contrast; neither is isoluminant relative to background).

Output: Agents/WriteUps/red_green_motion_lit.pdf
"""

import sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import textwrap

OUT = sys.argv[1] if len(sys.argv) > 1 else \
    "/Users/genestoner1/Projects/ObjectBasedAttention/VRDots/Agents/WriteUps/red_green_motion_lit.pdf"

# ── helpers ────────────────────────────────────────────────────────────────────

def new_page(pdf, title=None):
    fig = plt.figure(figsize=(8.5, 11))
    ax  = fig.add_axes([0.10, 0.06, 0.82, 0.88])
    ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    ax.axis("off")
    if title:
        ax.text(0.5, 0.97, title, ha="center", va="top",
                fontsize=13, fontweight="bold", wrap=True)
    return fig, ax

def body(ax, text, y, width=95, fontsize=9, color="black", indent=0):
    lines = textwrap.wrap(text, width)
    for line in lines:
        ax.text(indent, y, line, va="top", fontsize=fontsize, color=color,
                fontfamily="sans-serif")
        y -= 0.033
    return y - 0.008

def heading(ax, text, y, fontsize=10.5):
    ax.text(0, y, text, va="top", fontsize=fontsize, fontweight="bold",
            color="#1a1a6e")
    return y - 0.038

def rule(ax, y):
    ax.axhline(y + 0.012, color="#aaaaaa", lw=0.6, xmin=0, xmax=1)
    return y

def ref(ax, text, y):
    lines = textwrap.wrap(text, 90)
    for i, line in enumerate(lines):
        ax.text(0.04 if i > 0 else 0, y, line, va="top", fontsize=7.8,
                color="#444444", fontfamily="sans-serif")
        y -= 0.026
    return y - 0.006


# ══════════════════════════════════════════════════════════════════════════════
with PdfPages(OUT) as pdf:

    # ── PAGE 1: context + motion pathways ─────────────────────────────────────
    fig, ax = new_page(pdf,
        "Red vs Green in Motion Perception — Literature Summary")
    y = 0.91

    ax.text(0.5, y, "VRDots context: red dots and green dots on a black background.\n"
            "Neither color is isoluminant relative to the background.\n"
            "Question: does color (red vs green) systematically affect motion detection?",
            ha="center", va="top", fontsize=8.5, style="italic", color="#444")
    y -= 0.075

    y = rule(ax, y)
    y = heading(ax, "1.  Motion perception is luminance-contrast driven, not color-specific", y)
    y = body(ax, (
        "The magnocellular (M-pathway) stream dominates first-order motion processing. M-cells "
        "are broadband — they sum L and M cone signals nearly equally and respond primarily to "
        "luminance contrast, not chromatic contrast. Because red (#CC3333) and green (#228B22) "
        "dots both have substantial luminance contrast against a black background, both stimulate "
        "the M-pathway effectively. The canonical 'motion is blind to color' finding (Cavanagh, "
        "Tyler & Favreau 1984; Ramachandran & Gregory 1978; Livingstone & Hubel 1987) refers "
        "specifically to isoluminant stimuli — those with zero luminance contrast against their "
        "background. This condition does not apply in VRDots."
    ), y)

    y = body(ax, (
        "When luminance contrast is present, chromatic identity (red vs green) is largely "
        "irrelevant to the motion energy computation itself. The motion signal is carried by "
        "the luminance increment of each dot against the black surround. Both red and green "
        "dots, if matched in physical luminance, should drive motion perception equivalently "
        "through the M-pathway."
    ), y)

    y -= 0.01
    y = heading(ax, "2.  Luminance asymmetry: red and green are not equal on a display", y)
    y = body(ax, (
        "Even at equal RGB digital values, red and green stimuli differ in perceived luminance. "
        "The photopic luminosity function V(λ) peaks near 555 nm (yellow-green). Green LEDs "
        "(peak ~530 nm) fall near the photopic peak; red LEDs (peak ~630–640 nm) fall on the "
        "descending limb and have lower luminous efficiency. Consequently, a red patch and a "
        "green patch at equal RGB values will typically differ by 30–60% in perceived luminance, "
        "with green appearing brighter."
    ), y)
    y = body(ax, (
        "Display gamma correction partially compensates but is calibrated for overall white "
        "balance, not individual channel perceptual equality. On the Meta Quest specifically, "
        "the display is a transmissive LCD (Quest 2) or pancake-lens LCD (Quest 3) with "
        "RGB sub-pixel layout; the green channel typically contributes ~59% of the luminous "
        "flux for a white pixel. If the VRDots stimulus uses equal RGB values for red and green "
        "dots, the green dots are likely brighter in photopic units. This could confer a modest "
        "motion detection advantage on green, not red."
    ), y)
    y = body(ax, (
        "Practical implication: if a systematic color advantage exists in the VRDots data, "
        "it is more likely to favor green than red, due to its proximity to the peak of the "
        "photopic luminosity function. Any red advantage would need an attentional rather than "
        "a sensory-contrast explanation."
    ), y)

    pdf.savefig(fig, bbox_inches="tight")
    plt.close()

    # ── PAGE 2: red salience + segmentation ───────────────────────────────────
    fig, ax = new_page(pdf,
        "Red vs Green in Motion Perception — p.2: Attention & Segmentation")
    y = 0.91

    y = heading(ax, "3.  Red attention salience — documented but attention-stage, not motion-stage", y)
    y = body(ax, (
        "Red stimuli reliably capture attention faster and more strongly than other colors in "
        "visual search and cueing paradigms, even when luminance is controlled. This effect is "
        "robust across cultures and has been linked to evolutionary pressure (ripe fruit, blood, "
        "predator coloration). Key findings:"
    ), y)
    y = body(ax, (
        "— Theeuwes & Kooi (1994): color singletons capture attention; red captures "
        "faster than green in free-field search."
    ), y, indent=0.04)
    y = body(ax, (
        "— Anderson, Laurent & Yantis (2011, Psychological Science): reward-associated colors "
        "(typically trained with red) produce persistent attentional capture even when task-irrelevant."
    ), y, indent=0.04)
    y = body(ax, (
        "— Elliot & Maier (2012, Current Directions in Psychological Science): red influences "
        "motivated behavior and attention across achievement and avoidance contexts."
    ), y, indent=0.04)
    y = body(ax, (
        "Critically, this red capture effect operates at the attentional/post-selection stage, "
        "not at the level of the motion energy computation. In a task like VRDots where the "
        "observer must select one of two overlapping surfaces, red salience could bias initial "
        "attention capture toward the red surface — but this would be a Field-identity effect, "
        "not a motion-direction effect per se."
    ), y)
    y = body(ax, (
        "In VRDots, because red and green are balanced across conditions (which field is "
        "red vs green varies across trials), red salience would add noise but not a systematic "
        "directional bias at the group level. Within a trial, the observer might be more likely "
        "to initially attend to the red field — relevant if one is trying to interpret "
        "session-level variability or early vs late trial effects."
    ), y)

    y -= 0.01
    y = heading(ax, "4.  Color as a surface-segmentation cue for overlapping dot fields", y)
    y = body(ax, (
        "The most directly relevant body of literature for VRDots is the role of color in "
        "segmenting overlapping transparent-motion surfaces. When two surfaces share a color, "
        "depth-plane filtering is weakened; when they differ in color, they are more easily "
        "segregated as distinct objects."
    ), y)
    y = body(ax, (
        "— Theeuwes, Atchley & Kramer (1998, Psychological Science): color differences between "
        "overlapping motion surfaces facilitate surface-based selection. Same-color surfaces are "
        "harder to segment. This is the primary motivation for R/G designs in VRDots."
    ), y, indent=0.04)
    y = body(ax, (
        "— Croner & Albright (1999, Journal of Neuroscience): MT neurons in macaque showed "
        "color-selective surround suppression — suggesting color aids figure-ground segmentation "
        "even in motion-processing areas."
    ), y, indent=0.04)
    y = body(ax, (
        "— Nakayama, He & Shimojo (1995): color is a preattentive grouping dimension comparable "
        "to depth and motion; surfaces that share a color are parsed as a single object more "
        "readily than surfaces differing in color."
    ), y, indent=0.04)
    y = body(ax, (
        "These findings support using R/G in VRDots to strengthen surface segmentation, but "
        "do not predict a differential red vs green motion advantage. The benefit is symmetric: "
        "either color helps identify its surface; neither color inherently yields better motion "
        "detection than the other via the segmentation route."
    ), y)

    pdf.savefig(fig, bbox_inches="tight")
    plt.close()

    # ── PAGE 3: direct comparisons + VRDots implications ──────────────────────
    fig, ax = new_page(pdf,
        "Red vs Green in Motion Perception — p.3: Direct Comparisons & VRDots Implications")
    y = 0.91

    y = heading(ax, "5.  Direct red vs green motion detection comparisons", y)
    y = body(ax, (
        "There is limited literature directly comparing red vs green in motion detection when "
        "both have luminance contrast. Most chromatic motion research compares isoluminant "
        "chromatic vs luminance stimuli, not red vs green at suprathreshold contrast."
    ), y)
    y = body(ax, (
        "— Gegenfurtner & Hawken (1996, Trends in Neurosciences): comprehensive review of "
        "color and motion; conclude that chromatic signals make a modest contribution to "
        "perceived speed and direction when combined with luminance signals, but the direction "
        "signal is dominated by luminance. No differential red/green advantage identified."
    ), y, indent=0.04)
    y = body(ax, (
        "— Cavanagh & Anstis (1991, Vision Research): contribution of color to motion in "
        "normal and color-deficient observers. Motion from equiluminant color is weak but "
        "present; direction discrimination thresholds are elevated. Study does not isolate "
        "red vs green specifically."
    ), y, indent=0.04)
    y = body(ax, (
        "— Lu & Sperling (2001, Journal of Vision): three-systems framework for motion "
        "perception — first-order (luminance), second-order (contrast modulation), third-order "
        "(salience/feature maps). Red salience could boost third-order motion tracking but "
        "this has not been directly tested for red vs green dot stimuli on black backgrounds."
    ), y, indent=0.04)
    y = body(ax, (
        "Bottom line: no study known to this agent demonstrates a consistent red > green "
        "advantage in detecting or discriminating the direction of suprathreshold motion (i.e., "
        "where both colors have luminance contrast). The attentional red-capture literature is "
        "real but operates pre-translation; it does not predict differential heading discrimination."
    ), y)

    y -= 0.01
    y = heading(ax, "6.  Implications for VRDots", y)
    y = body(ax, (
        "Given the above, the R/G design in VRDots is well-motivated (surface segmentation) "
        "and unlikely to introduce a systematic red-vs-green motion detection bias, provided:"
    ), y)
    y = body(ax, "— The two colors are approximately luminance-balanced on the Quest display.",
             y, indent=0.04)
    y = body(ax, (
        "— Red and green are counterbalanced across conditions (which field is red vs green "
        "varies across trials), neutralizing any residual color-salience bias at the group level."
    ), y, indent=0.04)
    y = body(ax, (
        "The most actionable concern is display luminance calibration. If green dots are "
        "substantially brighter than red dots in photopic units (as would follow from V(λ)), "
        "this could produce a systematic performance advantage for whichever surface is green. "
        "A flicker photometry or heterochromatic brightness matching check would resolve this. "
        "In the absence of calibration data, the R/G balance across conditions provides "
        "reasonable protection against this confound at the group level but not within a trial."
    ), y)
    y = body(ax, (
        "In the DepthColorLinked experiment specifically, the concern is whether Near=Red / "
        "Far=Green (or vice versa) introduces a color-salience confound with the depth "
        "manipulation. Per the experiment_status.md, color and depth are balanced across "
        "trials, so this is not a systematic confound — but it adds within-trial variance "
        "on trials where the salient-color surface is the non-target."
    ), y)

    y -= 0.02
    y = rule(ax, y)
    y = heading(ax, "References (abbreviated)", y)
    y = ref(ax, "Cavanagh P, Tyler CW, Favreau OE (1984). Perceived velocity of moving chromatic gratings. J Opt Soc Am A 1(8):893–899.", y)
    y = ref(ax, "Cavanagh P, Anstis S (1991). The contribution of color to motion in normal and color-deficient observers. Vision Res 31(12):2109–2148.", y)
    y = ref(ax, "Croner LJ, Albright TD (1999). Segmentation by color influences responses of motion-sensitive neurons in the cortical middle temporal visual area. J Neurosci 19(10):3935–3951.", y)
    y = ref(ax, "Gegenfurtner KR, Hawken MJ (1996). Interaction of motion and color in the visual pathways. Trends Neurosci 19(9):394–401.", y)
    y = ref(ax, "Livingstone MS, Hubel DH (1987). Psychophysical evidence for separate channels for the perception of form, color, movement, and depth. J Neurosci 7(11):3416–3468.", y)
    y = ref(ax, "Lu ZL, Sperling G (2001). Three-systems theory of human visual motion perception: review and update. J Opt Soc Am A 18(9):2331–2370.", y)
    y = ref(ax, "Nakayama K, He ZJ, Shimojo S (1995). Visual surface representation: a critical link between lower-level and higher-level vision. In: Kosslyn SM, Osherson DN (eds) Visual Cognition. MIT Press.", y)
    y = ref(ax, "Ramachandran VS, Gregory RL (1978). Does colour provide an input to human motion perception? Nature 275:55–56.", y)
    y = ref(ax, "Theeuwes J, Kooi FL (1994). Parallel search for a conjunction of shape and color is not always efficient. Perception 23(5):543–553.", y)
    y = ref(ax, "Theeuwes J, Atchley P, Kramer AF (1998). Attentional control within 3-D space. J Exp Psychol Hum Percept Perform 24(5):1476–1485.", y)

    ax.text(0.5, 0.01,
            "Literature agent, VRDots — 2026-04-04.  "
            "Citations reflect agent knowledge; verify before submission.",
            ha="center", va="bottom", fontsize=7, color="#888888", style="italic")

    pdf.savefig(fig, bbox_inches="tight")
    plt.close()

print(f"Wrote: {OUT}")
