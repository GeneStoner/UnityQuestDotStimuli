"""
parameter_space_table.py
Parameter space grid: Aperture (rows) × Duration (cols).
Each cell shows Small Fix and Large Fix sub-rows with N Δ / MC Δ results.
Green = examined, yellow = not yet run, grey = physically impossible.
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

OUT = "/Users/genestoner1/Projects/ObjectBasedAttention/VRDots/Agents/SwapPilot/Figures"

# ── data ──────────────────────────────────────────────────────────────────────

APERTURES = ["1.65°", "2.0°", "(2.5°)", "3.5°"]
DURATIONS = ["44 ms", "80 ms"]

# (ap, dur, fix) -> result dict or None
# fix: "S" = small, "L" = large
RESULTS = {
    ("1.65°", "80 ms", "S"): dict(n="+23.3***", mc="+11.7*",
                                   asset="SubfieldSwap_CatekExact_v1",
                                   note="Db≡MC  |  4-cond design"),
    ("2.0°",  "44 ms", "S"): dict(n="+16.8***", mc="+19.9***",
                                   asset="StonerBlanc_Replication_v1",
                                   note=""),
    ("3.5°",  "44 ms", "S"): dict(n="+15.6***", mc="+5.1 n.s.",
                                   asset="StonerBlanc_Replication_Ap35_v1",
                                   note=""),
    ("3.5°",  "80 ms", "S"): dict(n="+16.4***", mc="+11.7**",
                                   asset="StonerBlanc_Ap35_80ms_v1",
                                   note="high session variability"),
    ("3.5°",  "44 ms", "L"): dict(n="+24.2***", mc="+5.1 n.s.",
                                   asset="StonerBlanc_Ap35_LargeFix_v1",
                                   note=""),
    ("3.5°",  "80 ms", "L"): dict(n="+37.5***", mc="+10.2*",
                                   asset="DensityCompare_Peak_ColorMotionSwap_v1",
                                   note="density=52/deg²  ⚠"),
}

# Impossible: large fix excl (1.10°) > aperture radius
IMPOSSIBLE = {
    ("1.65°", "S"): False, ("1.65°", "L"): True,   # excl 1.10 > r 0.825
    ("2.0°",  "S"): False, ("2.0°",  "L"): True,   # excl 1.10 > r 1.00
    ("(2.5°)","S"): False, ("(2.5°)","L"): False,  # excl 1.10 < r 1.25 — borderline
    ("3.5°",  "S"): False, ("3.5°",  "L"): False,
}

FIX_LABELS = {"S": "Small fix\ndisc 0.40°  excl 0.40°",
              "L": "Large fix\ndisc 1.80°  excl 1.10°"}

# Excl/Ap ratios
EXCL_AP = {
    ("1.65°", "S"): "E/Ap=0.61", ("1.65°", "L"): "—",
    ("2.0°",  "S"): "E/Ap=0.40", ("2.0°",  "L"): "—",
    ("(2.5°)","S"): "E/Ap=0.32", ("(2.5°)","L"): "E/Ap=0.88",
    ("3.5°",  "S"): "E/Ap=0.23", ("3.5°",  "L"): "E/Ap=0.63",
}

# ── layout ────────────────────────────────────────────────────────────────────

N_AP  = len(APERTURES)   # 4 rows
N_DUR = len(DURATIONS)   # 2 cols
N_FIX = 2                # sub-rows per cell (S, L)

CELL_W = 3.8    # inches per duration column
CELL_H = 1.5    # inches per fix sub-row
LABEL_W = 1.3   # left label column
LABEL_H = 0.5   # top header row
HDR_H   = 0.5

FIG_W = LABEL_W + N_DUR * CELL_W + 0.3
FIG_H = HDR_H + N_AP * N_FIX * CELL_H + 0.5

fig, ax = plt.subplots(figsize=(FIG_W, FIG_H), facecolor="white")
ax.set_xlim(0, FIG_W)
ax.set_ylim(0, FIG_H)
ax.invert_yaxis()
ax.axis("off")
fig.subplots_adjust(left=0.01, right=0.99, top=0.94, bottom=0.06)

C_EXAMINED   = "#d5f0dd"
C_UNEXAMINED = "#fef9e7"
C_IMPOSSIBLE = "#ebebeb"
C_HEADER_AP  = "#2c3e50"
C_HEADER_DUR = "#1a5276"
C_N_BG       = "#b8dfc8"
C_MC_BG      = "#b8d0e8"

def draw_rect(x, y, w, h, fc, ec="#bbb", lw=0.8, zorder=1):
    ax.add_patch(mpatches.FancyBboxPatch(
        (x, y), w, h, boxstyle="square,pad=0",
        fc=fc, ec=ec, lw=lw, zorder=zorder, clip_on=False))

def txt(x, y, s, fs=10, fw="normal", color="#222", ha="center", va="center",
        style="normal", zorder=3):
    ax.text(x, y, s, fontsize=fs, fontweight=fw, color=color,
            ha=ha, va=va, style=style, zorder=zorder,
            linespacing=1.35, clip_on=False)

# ── header row ────────────────────────────────────────────────────────────────

# top-left corner
draw_rect(0, 0, LABEL_W, HDR_H, fc=C_HEADER_AP, ec="#555", lw=1.2)
txt(LABEL_W/2, HDR_H/2, "Aperture\n(diameter)", fs=11, fw="bold",
    color="white")

# duration headers
for ci, dur in enumerate(DURATIONS):
    x = LABEL_W + ci * CELL_W
    draw_rect(x, 0, CELL_W, HDR_H, fc=C_HEADER_DUR, ec="#555", lw=1.2)
    txt(x + CELL_W/2, HDR_H/2, f"Translation duration\n{dur}",
        fs=12, fw="bold", color="white")

# ── aperture row labels ───────────────────────────────────────────────────────

for ri, ap in enumerate(APERTURES):
    y_top = HDR_H + ri * N_FIX * CELL_H
    draw_rect(0, y_top, LABEL_W, N_FIX * CELL_H,
              fc="#34495e" if "(2.5°)" not in ap else "#5d6d7e",
              ec="#555", lw=1.2)
    dots = {"1.65°":"43 dots", "2.0°":"63 dots",
            "(2.5°)":"~98 dots", "3.5°":"192 dots"}[ap]
    density = "20 /deg²"
    label = f"{ap}\n{dots}\n{density}"
    if "(2.5°)" in ap:
        label += "\n(not yet built)"
    txt(LABEL_W/2, y_top + N_FIX * CELL_H / 2, label,
        fs=11, fw="bold", color="white",
        style="italic" if "(2.5°)" in ap else "normal")

# ── cells ─────────────────────────────────────────────────────────────────────

for ri, ap in enumerate(APERTURES):
    for fi, fix in enumerate(["S", "L"]):
        y_cell = HDR_H + (ri * N_FIX + fi) * CELL_H
        imp = IMPOSSIBLE.get((ap, fix), False)
        fix_lbl = FIX_LABELS[fix]
        excl_ap = EXCL_AP.get((ap, fix), "")

        for ci, dur in enumerate(DURATIONS):
            x_cell = LABEL_W + ci * CELL_W
            key = (ap, dur, fix)
            res = RESULTS.get(key)
            examined = res is not None

            bg = C_IMPOSSIBLE if imp else (C_EXAMINED if examined else C_UNEXAMINED)
            draw_rect(x_cell, y_cell, CELL_W, CELL_H,
                      fc=bg, ec="#888", lw=0.9)

            if imp:
                txt(x_cell + CELL_W/2, y_cell + CELL_H/2,
                    "N/A\nexcl. radius > aperture radius",
                    fs=10, color="#999", style="italic")
                continue

            # fix label (left side of cell, only first duration column)
            if ci == 0:
                txt(x_cell + 0.08, y_cell + CELL_H/2,
                    fix_lbl + f"\n{excl_ap}",
                    fs=8.5, color="#555", ha="left", style="italic")

            if not examined:
                txt(x_cell + CELL_W/2 + 0.3, y_cell + CELL_H/2,
                    "not yet run", fs=10, color="#aaa", style="italic")
                continue

            # result boxes
            note = res.get("note", "")
            bx = x_cell + (0.05 if ci == 0 else 0.05)
            bx_offset = 0.55 if ci == 0 else 0.05   # shift right to avoid fix label
            bx = x_cell + bx_offset + 0.10

            # asset name
            asset = res.get("asset", "")
            txt(bx + 0.72, y_cell + 0.10,
                asset, fs=7.5, color="#555", style="italic")

            # N result box
            draw_rect(bx, y_cell + 0.25, 1.45, 0.44,
                      fc=C_N_BG, ec="#7dbc9a", lw=1.0, zorder=2)
            txt(bx + 0.72, y_cell + 0.47,
                f"N    {res['n']} pp", fs=11, fw="bold", color="#1a5c33")

            # MC result box
            draw_rect(bx, y_cell + 0.75, 1.45, 0.44,
                      fc=C_MC_BG, ec="#7a9fc0", lw=1.0, zorder=2)
            txt(bx + 0.72, y_cell + 0.97,
                f"MC  {res['mc']} pp", fs=11, fw="bold", color="#1a3a6b")

            if note:
                txt(bx + 0.72, y_cell + CELL_H - 0.08,
                    note, fs=8, color="#c0392b", style="italic")

# ── legend ────────────────────────────────────────────────────────────────────

leg_y = FIG_H - 0.38
items = [
    (C_EXAMINED,   "Examined"),
    (C_UNEXAMINED, "Not yet run"),
    (C_IMPOSSIBLE, "N/A  (excl. radius ≥ aperture radius)"),
]
xleg = LABEL_W
for fc, lbl in items:
    draw_rect(xleg, leg_y, 0.28, 0.22, fc=fc, ec="#888", lw=0.8)
    txt(xleg + 0.32, leg_y + 0.11, lbl, fs=10, color="#333", ha="left")
    xleg += 2.4

txt(FIG_W/2, FIG_H - 0.12,
    "Density ~20 dots/deg² throughout except DenseCM (52/deg², flagged)  |  "
    "Ap2.5° not built yet  |  CatekExact uses Db swap (≡MC in effect)",
    fs=9, color="#666", style="italic")

fig.suptitle(
    "VRDots — MC/N Cueing Parameter Space\n"
    "Aperture  ×  Translation Duration  ×  Fixation/Exclusion Zone",
    fontsize=14, fontweight="bold", y=0.995, va="top")

fig.savefig(f"{OUT}/parameter_space_table.png", dpi=150,
            bbox_inches="tight", facecolor="white")
fig.savefig(f"{OUT}/parameter_space_table.pdf",
            bbox_inches="tight", facecolor="white")
print("Saved parameter_space_table.png / .pdf")
