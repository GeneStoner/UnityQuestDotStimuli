#!/usr/bin/env python3
"""
turkey_session_rg.py — Turkey pilot session broken down by field colour.

    python3 turkey_session_rg.py <session.tsv> [out.png]

Panel A: percent correct for CUED and UNCUED, split by the colour of the field
         that translated (the delayed field on CUED trials, the other on UNCUED).
Panel B: the cueing effect (CUED - UNCUED) for each colour.
Panel C: the same split by which field appeared LATE (the cue), as a control.

Error bars are binomial standard errors. Trials confirmed without a direction
(RespDeg -1) are excluded and counted in the caption.
"""

import csv
import math
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

CHANCE = 12.5
RED, GREEN = "#C0392B", "#1E8449"


def load(path):
    rows = []
    with open(path, newline="") as f:
        for r in csv.DictReader(f, delimiter="\t"):
            try:
                resp = float(r["RespDeg"])
                truth = float(r["TransDeg"])
            except (KeyError, ValueError):
                continue
            rows.append({
                "cond": r["Cond"],
                "delayed": r["DelayedFieldColor"],       # field that appeared late
                "answered": resp >= 0,
                "correct": resp == truth,
            })
    return rows


def translating_colour(row):
    """CUED: the delayed field translates. UNCUED: the other one does."""
    if row["cond"] == "CUED":
        return row["delayed"]
    return "G" if row["delayed"] == "R" else "R"


def rate(rows):
    scored = [r for r in rows if r["answered"]]
    if not scored:
        return float("nan"), float("nan"), 0
    n = len(scored)
    p = sum(r["correct"] for r in scored) / n
    return 100 * p, 100 * math.sqrt(p * (1 - p) / n), n


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    tsv = Path(sys.argv[1])
    out = Path(sys.argv[2]) if len(sys.argv) > 2 else tsv.with_suffix(".rg.png")
    rows = load(tsv)
    unanswered = sum(1 for r in rows if not r["answered"])

    fig, axes = plt.subplots(1, 3, figsize=(12.5, 4.2))
    fig.suptitle(f"{tsv.name} — performance by field colour", fontsize=12)

    # ── Panel A: percent correct, by translating field colour ────────────────
    ax = axes[0]
    width = 0.36
    for i, (colour, label, hue) in enumerate((("R", "red field", RED),
                                              ("G", "green field", GREEN))):
        vals, errs, ns = [], [], []
        for cond in ("CUED", "UNCUED"):
            sub = [r for r in rows if r["cond"] == cond and translating_colour(r) == colour]
            p, se, n = rate(sub)
            vals.append(p); errs.append(se); ns.append(n)
        xs = [x + (i - 0.5) * width for x in range(2)]
        ax.bar(xs, vals, width, yerr=errs, capsize=4, color=hue,
               edgecolor="black", linewidth=0.6,
               hatch="" if colour == "R" else "//", label=label)
        for x, v, n in zip(xs, vals, ns):
            ax.text(x, v + 2.0, f"{v:.1f}\nn={n}", ha="center", va="bottom", fontsize=8)

    ax.axhline(CHANCE, ls="--", lw=1, color="0.4")
    ax.text(1.45, CHANCE + 0.8, "chance", fontsize=8, color="0.4", ha="right")
    ax.set_xticks(range(2)); ax.set_xticklabels(["CUED", "UNCUED"])
    ax.set_ylabel("correct (%)"); ax.set_ylim(0, 45)
    ax.set_title("A. Which field translated", fontsize=10, loc="left")
    ax.legend(frameon=False, fontsize=8)

    # ── Panel B: cueing effect per colour ────────────────────────────────────
    ax = axes[1]
    for i, (colour, label, hue) in enumerate((("R", "red", RED), ("G", "green", GREEN))):
        cu = [r for r in rows if r["cond"] == "CUED" and translating_colour(r) == colour]
        un = [r for r in rows if r["cond"] == "UNCUED" and translating_colour(r) == colour]
        p1, e1, _ = rate(cu); p2, e2, _ = rate(un)
        ax.bar(i, p1 - p2, 0.5, yerr=math.hypot(e1, e2), capsize=4, color=hue,
               edgecolor="black", linewidth=0.6, hatch="" if colour == "R" else "//")
        ax.text(i, p1 - p2 + 0.6, f"{p1 - p2:+.1f} pp", ha="center", fontsize=9)
    ax.axhline(0, color="black", lw=0.8)
    ax.set_xticks([0, 1]); ax.set_xticklabels(["red", "green"])
    ax.set_ylabel("cueing effect (pp)"); ax.set_ylim(0, 20)
    ax.set_title("B. Cueing effect, by translating field", fontsize=10, loc="left")

    # ── Panel C: control — split by which field was the cue (appeared late) ──
    ax = axes[2]
    for i, (colour, label, hue) in enumerate((("R", "red late", RED),
                                              ("G", "green late", GREEN))):
        vals, errs = [], []
        for cond in ("CUED", "UNCUED"):
            sub = [r for r in rows if r["cond"] == cond and r["delayed"] == colour]
            p, se, _ = rate(sub)
            vals.append(p); errs.append(se)
        xs = [x + (i - 0.5) * width for x in range(2)]
        ax.bar(xs, vals, width, yerr=errs, capsize=4, color=hue,
               edgecolor="black", linewidth=0.6,
               hatch="" if colour == "R" else "//", label=label)
    ax.axhline(CHANCE, ls="--", lw=1, color="0.4")
    ax.set_xticks(range(2)); ax.set_xticklabels(["CUED", "UNCUED"])
    ax.set_ylabel("correct (%)"); ax.set_ylim(0, 45)
    ax.set_title("C. Which field appeared late", fontsize=10, loc="left")
    ax.legend(frameon=False, fontsize=8)

    fig.text(0.01, 0.01,
             f"{len(rows) - unanswered} answered trials; {unanswered} confirmed without a "
             f"direction (re-queued, excluded). Error bars: binomial SE. Chance = 12.5%.",
             fontsize=8, color="0.35")
    fig.tight_layout(rect=(0, 0.04, 1, 0.94))
    fig.savefig(out, dpi=170)
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
