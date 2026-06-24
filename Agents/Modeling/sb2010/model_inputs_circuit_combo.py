"""
Combined figure — Part A (directional inputs, single aligned column) feeding
Part B (the rotated biased-competition circuit).

Both parts are drawn on ONE axis with ONE coordinate system, so the three
input rows line up EXACTLY with the three Stage-1 channel neurons:

    Up    (CW  rotation, locally upward)   -> R_1   (y = 80)
    Right (coherent translation, rightward)-> R_T   (y = 54)
    Down  (CCW rotation, locally downward) -> R_2   (y = 28)

Single-RF (left) interpretation: an MT hypercolumn whose collective receptive
field sits on the left of the rotating display.  Part A shows the cued,
no-swap directional input over time (the representative trial); a horizontal
arrow carries each direction channel into its neuron.

Run:  /usr/bin/python3 model_inputs_circuit_combo.py
"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, Rectangle

from parameters import T_END, T_TRANS_START, T_TRANS_END
from web_figures import INK, INK2, GRID
from model_schematic_adapting_rot import draw_circuit_rot
from dirinputs_figure_sb4 import channel_occupancy, CW_, TRANS_, CCW_

# y-heights of the circuit's channel neurons (must match draw_circuit_rot)
YROW = {CW_: 80.0, TRANS_: 54.0, CCW_: 28.0}
RLAB = {CW_: "Up", TRANS_: "Right", CCW_: "Down"}

# input-column x-extent (the local time axis), kept left of the circuit
XA0, XA1 = -60.0, -8.0
XC_NEURON = 42.0          # channel-column x in draw_circuit_rot
RIN = 6.5                 # neuron radius in draw_circuit_rot


def _x(t):
    """Map stimulus time -> x within the input column."""
    return XA0 + (t / T_END) * (XA1 - XA0)


def main(out="model_inputs_circuit_combo.png"):
    fig, ax = plt.subplots(figsize=(16.0, 8.0))

    # ---- Part B: rotated circuit, WITHOUT its built-in input arrows --------
    draw_circuit_rot(ax, draw_inputs=False)

    # ---- Part A: directional-input column (cued, no swap) -----------------
    occ = channel_occupancy("CUED", False)

    # translation-window band across the three rows
    xs, xe = _x(T_TRANS_START), _x(T_TRANS_END)
    ax.add_patch(Rectangle((xs, 18.0), max(xe - xs, 0.8), 72.0,
                 facecolor="0.85", edgecolor="none", alpha=0.8, zorder=0))

    # row guides + labels
    for row, y in YROW.items():
        ax.plot([XA0, XA1], [y, y], color=GRID, lw=1.0, zorder=1)
        ax.text(XA0 - 3.0, y, RLAB[row], ha="right", va="center", fontsize=13,
                color=INK)

    # occupancy bars (what each direction channel receives over time)
    for t0, t1, row in occ:
        ax.plot([_x(t0), _x(t1)], [YROW[row], YROW[row]], color=INK, lw=5.0,
                solid_capstyle="butt", zorder=3)

    # local time axis under the column
    ax.plot([XA0, XA1], [12.0, 12.0], color=INK2, lw=1.0, zorder=2)
    for tt in (0, T_END):
        x = _x(tt)
        ax.plot([x, x], [12.0, 10.5], color=INK2, lw=1.0)
        ax.text(x, 9.0, f"{int(tt)}", ha="center", va="top", fontsize=9,
                color=INK2)
    ax.text((XA0 + XA1) / 2.0, 4.5, "time  (ms)", ha="center", va="top",
            fontsize=10, color=INK2)

    # ---- input -> neuron projections (one per row, perfectly horizontal) ---
    for row, y in YROW.items():
        ax.add_patch(FancyArrowPatch((XA1 + 3.0, y),
                     (XC_NEURON - RIN - 1.5, y), arrowstyle="-|>",
                     mutation_scale=13, color=INK, lw=1.7, zorder=2))

    # ---- panel letters + part-A title -------------------------------------
    ax.text(XA0 - 8.0, 97.0, "A", fontsize=17, fontweight="bold", color=INK,
            va="top", ha="left")
    ax.text(18.0, 97.0, "B", fontsize=17, fontweight="bold", color=INK,
            va="top", ha="left")
    ax.text((XA0 + XA1) / 2.0, 94.0, "Directional input\n(cued, no swap)",
            ha="center", va="top", fontsize=10.5, color=INK2)

    # extend xlim left to include the input column (draw_circuit_rot set 0..130)
    ax.set_xlim(XA0 - 12.0, 132.0)

    fig.savefig(out, bbox_inches="tight", pad_inches=0.2, facecolor="white")
    plt.close(fig)
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
