"""
Publication-style summary figure for the Stoner & Blanc (2010)
motion-competition model: architecture (wiring diagram), equations,
and parameter table on a single page.

Outputs: model_diagram.png

Run with:
    /usr/bin/python3 model_diagram.py
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

import parameters as P


# ----------------------------------------------------------------------
# Figure scaffolding
# ----------------------------------------------------------------------

fig = plt.figure(figsize=(11.0, 14.5))
gs = fig.add_gridspec(
    3, 1,
    height_ratios=[1.45, 1.40, 1.50],
    hspace=0.34,
    left=0.05, right=0.97, top=0.96, bottom=0.04,
)

ax_diag = fig.add_subplot(gs[0])
ax_eqs  = fig.add_subplot(gs[1])
ax_pars = fig.add_subplot(gs[2])


# ----------------------------------------------------------------------
# A. Wiring diagram
# ----------------------------------------------------------------------

ax = ax_diag
ax.set_xlim(0, 10)
ax.set_ylim(0, 8)
ax.axis('off')
ax.set_title('A. Motion-competition model architecture',
             fontsize=14, fontweight='bold', loc='left', pad=8)

BOX_FACE = '#F4F1E8'
BOX_EDGE = '#222'
INHIB_COLOR = '#C0392B'
EXCIT_COLOR = '#2E8B57'


def rbox(x, y, w, h, label, fontsize=10):
    """Draw a rounded box with centered multi-line label."""
    box = FancyBboxPatch(
        (x, y), w, h,
        boxstyle="round,pad=0.05,rounding_size=0.15",
        facecolor=BOX_FACE, edgecolor=BOX_EDGE, lw=1.3,
    )
    ax.add_patch(box)
    ax.text(x + w/2, y + h/2, label,
            ha='center', va='center', fontsize=fontsize,
            linespacing=1.4)


def arrow(x0, y0, x1, y1, color='#333', lw=1.6, rad=0.0, label=None,
          label_xy=None, label_color=None, label_fontsize=10,
          label_style='italic'):
    """Draw a straight or arced arrow with optional label."""
    cs = f"arc3,rad={rad}" if rad else "arc3"
    ax.annotate(
        '', xy=(x1, y1), xytext=(x0, y0),
        arrowprops=dict(arrowstyle='-|>', color=color, lw=lw,
                        connectionstyle=cs, shrinkA=0, shrinkB=2,
                        mutation_scale=14),
    )
    if label is not None:
        lx, ly = label_xy if label_xy else ((x0 + x1)/2, (y0 + y1)/2 + 0.25)
        ax.text(lx, ly, label, ha='center', va='center',
                fontsize=label_fontsize, color=label_color or color,
                style=label_style)


# --- Stimulus input labels (left) ---
ax.text(0.55, 6.45, r'$S_1(t)$',           fontsize=13, ha='center', va='center')
ax.text(0.55, 4.45, r'$S_2(t)$',           fontsize=13, ha='center', va='center')
ax.text(0.55, 1.30, r'$C_{\rm trans}(t)$', fontsize=13, ha='center', va='center')

# --- Adapting channel boxes ---
rbox(1.5, 5.65, 2.6, 1.6,
     "Adapting channel 1\n(CW rotation)\nEqs 4, 5")
rbox(1.5, 3.65, 2.6, 1.6,
     "Adapting channel 2\n(CCW rotation)\nEqs 4, 5")

# --- Translation detector box (bigger) ---
rbox(5.7, 4.10, 3.6, 2.40,
     "Translation detector\n(divisive normalization)\nEqs 1–3",
     fontsize=10.5)

# --- Stim → channel arrows ---
arrow(1.0, 6.45, 1.5, 6.45)
arrow(1.0, 4.45, 1.5, 4.45)

# --- Channel R outputs → detector (inhibitory) ---
arrow(4.1, 6.45, 5.7, 5.80, color=INHIB_COLOR, lw=1.8,
      label=r'$R_1$  (inhibitory)', label_xy=(4.95, 6.45),
      label_color=INHIB_COLOR, label_fontsize=10)
arrow(4.1, 4.45, 5.7, 4.80, color=INHIB_COLOR, lw=1.8,
      label=r'$R_2$  (inhibitory)', label_xy=(4.95, 4.45),
      label_color=INHIB_COLOR, label_fontsize=10)

# --- C_trans → detector (excitatory) ---
arrow(1.0, 1.30, 5.7, 4.30, color=EXCIT_COLOR, lw=1.8, rad=-0.25,
      label='excitatory', label_xy=(3.30, 2.30),
      label_color=EXCIT_COLOR, label_fontsize=10)

# --- Output arrow R_TD ---
arrow(9.3, 5.30, 9.95, 5.30)
ax.text(9.97, 5.30, r'$R_{TD}(t)$', fontsize=13, ha='left', va='center',
        fontweight='bold')

# --- Detector internal equation, drawn inside the box ---
ax.text(7.5, 4.95, r"$R_{TD} = \dfrac{K\, E}{E + I + \sigma}$",
        ha='center', va='center', fontsize=12)
ax.text(7.5, 4.30, r"$E = W_{\rm trans}\, C_{\rm trans}$" + ",   "
                   + r"$I = W_{\rm rot}(R_1 + R_2)$",
        ha='center', va='center', fontsize=9.5, color='#555')


# ----------------------------------------------------------------------
# B. Equations
# ----------------------------------------------------------------------

ax = ax_eqs
ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
ax.axis('off')
ax.set_title('B. Model equations', fontsize=14, fontweight='bold',
             loc='left', pad=8)

# Stage 1
ax.text(0.02, 0.94,
        'Stage 1 — adapting rotation channel (one per direction)',
        fontsize=11.5, fontweight='bold')

ax.text(0.08, 0.78,
        r"$\tau\,\dfrac{dR}{dt} \,=\, -R \,+\, N(\,S(t) - W_{\rm adapt}\, I\,)$",
        fontsize=13)
ax.text(0.08, 0.62,
        r"$\tau_{\rm adapt}\,\dfrac{dI}{dt} \,=\, -I \,+\, R$",
        fontsize=13)
ax.text(0.08, 0.46,
        r"$N(x) \,=\, \dfrac{N_{\rm max}\,[x]_+^{\,2}}{\sigma_{NR}^{2} + [x]_+^{\,2}}\,, "
        r"\quad\quad [x]_+ = \max(x,\,0)$",
        fontsize=13)

# Stage 2
ax.text(0.02, 0.28,
        'Stage 2 — translation detector  (divisive normalization)',
        fontsize=11.5, fontweight='bold')

ax.text(0.08, 0.16,
        r"$E \,=\, W_{\rm trans}\, C_{\rm trans}(t)\,, "
        r"\quad\quad I \,=\, W_{\rm rot}\,R_1(t) \,+\, W_{\rm rot}\,R_2(t)$",
        fontsize=13)
ax.text(0.08, 0.04,
        r"$R_{TD}(t) \,=\, \dfrac{K\, E}{E + I + \sigma}$",
        fontsize=13)


# ----------------------------------------------------------------------
# C. Parameter table
# ----------------------------------------------------------------------

ax = ax_pars
ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
ax.axis('off')
ax.set_title('C. Parameters (from Appendix A of Stoner & Blanc, 2010)',
             fontsize=14, fontweight='bold', loc='left', pad=8)

rows = [
    # (symbol, value, units, description)
    (r"$\tau$",              f"{P.TAU:.0f}",            "ms",
     "response time constant"),
    (r"$\tau_{\rm adapt}$",  f"{P.TAU_ADAPT:.0f}",      "ms",
     "adaptation time constant"),
    (r"$W_{\rm adapt}$",     f"{P.W_ADAPT:.2f}",        "—",
     "adaptation strength"),
    (r"$N_{\rm max}$",       f"{P.NR_MAX:.0f}",         "—",
     "Naka–Rushton numerator coefficient"),
    (r"$\sigma_{NR}$",       f"{P.NR_SEMISAT:.0f}",     "—",
     "Naka–Rushton semisaturation"),
    (r"$K$",                 f"{P.K:.0f}",              "—",
     "translation detector max firing rate"),
    (r"$\sigma$",            f"{P.SIGMA:.0f}",          "—",
     "normalization floor (Krekelberg & Albright 2005)"),
    (r"$W_{\rm trans}$",     f"{P.W_TRANS:.0f}",        "—",
     "excitatory weight on the translation input"),
    (r"$W_{\rm rot}$",       f"{P.W_ROT:.0f}",          "—",
     "inhibitory weight on each rotation input"),
    (r"$S_{\rm rot}$",       f"{P.STIM_ROTATION:.0f}",  "—",
     "rotation stimulus value (binary on)"),
    (r"$S_{\rm trans}$",     f"{P.STIM_TRANSLATION:.0f}", "—",
     "translation stimulus value (binary on)"),
]

# Column layout
col_x = [0.04, 0.22, 0.33, 0.43]
col_headers = ['Symbol', 'Value', 'Units', 'Description']
header_y = 0.95
row_height = 0.072

# Header
for x, h in zip(col_x, col_headers):
    ax.text(x, header_y, h, fontsize=11.5, fontweight='bold')
ax.plot([0.03, 0.97], [header_y - 0.025, header_y - 0.025],
        color='black', linewidth=0.7)

# Rows
for i, (sym, val, units, desc) in enumerate(rows):
    y = header_y - 0.025 - (i + 1) * row_height
    ax.text(col_x[0], y, sym,   fontsize=12)
    ax.text(col_x[1], y, val,   fontsize=11)
    ax.text(col_x[2], y, units, fontsize=11)
    ax.text(col_x[3], y, desc,  fontsize=10.5)

# Footnote
ax.text(0.04, 0.02,
        "Stimulus values shown are for Mode 1 (binary on/off, Section 1 of the paper).  "
        "Translation is set to half the rotation value because only ~50% of dots "
        "translate coherently in the experiments.",
        fontsize=9.5, style='italic', color='#555')


# ----------------------------------------------------------------------
# Save
# ----------------------------------------------------------------------

out = 'model_diagram.png'
fig.savefig(out, dpi=180, bbox_inches='tight', facecolor='white')
print(f"Saved {out}")
