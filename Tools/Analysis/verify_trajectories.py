#!/usr/bin/env python3
"""
Method A: Verify sidecar trajectory payloads against independently-generated
expected values.  Re-implements BuildEffectiveCondition() logic from
ExpSpecTestPhase.cs in pure Python.

Method C (pseudo-session): Generates trajectory plots for every unique
condition shape in the sidecar, so the experimenter can visually inspect
the complete stimulus space before running subjects.

Usage:
  python3 verify_trajectories.py <sidecar.json>           # verify only
  python3 verify_trajectories.py <sidecar.json> --plots    # verify + generate plots
"""

import sys, os, json, math
import numpy as np

# ── Motion-kind codes (match StimulusConditionsLibrary.MotionKind) ────
CW       = 1   # RotationCW
CCW      = 2   # RotationCCW
LINEAR   = 3
NONCOH   = 4   # NonCoherent

# ── Default spec timing (must match ExperimentSpec asset values) ──────
DEFAULT_SIM_HZ              = 75
DEFAULT_DELAYED_ONSET_MS    = 750.0
DEFAULT_PRE_TRANSLATION_MS  = 300.0
DEFAULT_TRANSLATION_DUR_MS  = 80.0
DEFAULT_POST_TRANSLATION_MS = 400.0


# ══════════════════════════════════════════════════════════════════════
#  TIMING
# ══════════════════════════════════════════════════════════════════════

def ms_to_frames(ms, sim_hz):
    """Match C# Mathf.RoundToInt (banker's rounding via Python round())."""
    return max(1, round(ms / 1000.0 * sim_hz))

def compute_timing(sim_hz=DEFAULT_SIM_HZ,
                   onset_ms=DEFAULT_DELAYED_ONSET_MS,
                   pre_ms=DEFAULT_PRE_TRANSLATION_MS,
                   trans_ms=DEFAULT_TRANSLATION_DUR_MS,
                   post_ms=DEFAULT_POST_TRANSLATION_MS):
    onset  = ms_to_frames(onset_ms, sim_hz)
    pre    = ms_to_frames(pre_ms, sim_hz)
    trans  = ms_to_frames(trans_ms, sim_hz)
    post   = ms_to_frames(post_ms, sim_hz)
    t_start = onset + pre
    t_end   = t_start + trans
    total   = t_end + post
    return onset, t_start, t_end, total


# ══════════════════════════════════════════════════════════════════════
#  FNV-1a 32-bit  (matches CsvLogger.Fnv1a32)
# ══════════════════════════════════════════════════════════════════════

def fnv1a_32(s):
    if not s:
        return 0
    OFFSET = 0x811C9DC5
    PRIME  = 0x01000193
    h = OFFSET
    for b in s.encode("utf-8"):
        h ^= b
        h = (h * PRIME) & 0xFFFFFFFF
    return h

def fnv1a_32_hex(s):
    return f"{fnv1a_32(s):08X}"


# ══════════════════════════════════════════════════════════════════════
#  TRAJECTORY GENERATION  (independent re-implementation of
#  ExpSpecTestPhase.BuildEffectiveCondition)
# ══════════════════════════════════════════════════════════════════════

def generate_trajectory(cond, rot_cfg, delayed_color, swap_type,
                        onset, t_start, t_end, total):
    """
    Return (mk_payload, color_payload) strings in the same format as
    the C# sidecar writer.

    Parameters match the sidecar entry fields.  swap_type is the code
    string ("N", "M", "C", "MC").
    """
    N = total
    is_cued = (cond == "CUED")

    # Rotation config
    a_rot = CW  if rot_cfg == 0 else CCW
    b_rot = CCW if rot_cfg == 0 else CW

    # Delayed / non-delayed colors
    d_col  = delayed_color                               # "R" or "G"
    nd_col = "G" if delayed_color == "R" else "R"

    motion_swap = ("M" in swap_type) if swap_type != "N" else False
    color_swap  = ("C" in swap_type) if swap_type != "N" else False
    dots50_swap = ("D" in swap_type) if swap_type != "N" else False

    mk_rows   = []   # list of [1,1,2,2] int lists
    col_rows  = []   # list of ["R","R","G","G"] string lists

    for f in range(N):
        after_onset = (f >= onset)
        after_swap  = (f >= t_start)

        # ── rotation (may be swapped) ────────────────────────────
        cur_a = b_rot if (motion_swap and after_swap) else a_rot
        cur_b = a_rot if (motion_swap and after_swap) else b_rot

        # ── color (may be swapped) ───────────────────────────────
        if color_swap and after_swap:
            fa_col, fb_col = d_col, nd_col
        else:
            fa_col, fb_col = nd_col, d_col

        # ── field membership (dots50: sub1↔sub3 at tStart) ──────
        if dots50_swap and after_swap:
            # sub0=A, sub1=B, sub2=B, sub3=A
            mk = [cur_a, cur_b, cur_b, cur_a]
            if not after_onset:
                col = [fa_col, "K", "K", fa_col]
            else:
                col = [fa_col, fb_col, fb_col, fa_col]
        else:
            # default: sub0,1=A  sub2,3=B
            mk = [cur_a, cur_a, cur_b, cur_b]
            if not after_onset:
                col = [fa_col, fa_col, "K", "K"]
            else:
                col = [fa_col, fa_col, fb_col, fb_col]

        mk_rows.append(mk)
        col_rows.append(col)

    # ── translation override (applied AFTER rotation, matches C#) ─
    # With dots50: field membership changes translation targets.
    f_start = max(0, t_start)
    f_end   = min(N, t_end)
    for f in range(f_start, f_end):
        if dots50_swap:
            if is_cued:   # Field B={sub2,sub1}: sub2=Linear, sub1=NonCoherent
                mk_rows[f][2] = LINEAR
                mk_rows[f][1] = NONCOH
            else:         # Field A={sub0,sub3}: sub0=Linear, sub3=NonCoherent
                mk_rows[f][0] = LINEAR
                mk_rows[f][3] = NONCOH
        else:
            if is_cued:
                mk_rows[f][2] = LINEAR
                mk_rows[f][3] = NONCOH
            else:
                mk_rows[f][0] = LINEAR
                mk_rows[f][1] = NONCOH

    # ── format as payload strings ─────────────────────────────────
    mk_payload  = ";".join("|".join(str(v) for v in row) for row in mk_rows)
    col_payload = ";".join("|".join(row) for row in col_rows)
    return mk_payload, col_payload


# ══════════════════════════════════════════════════════════════════════
#  VERIFICATION
# ══════════════════════════════════════════════════════════════════════

def verify_sidecar(sidecar_path, do_plots=False):
    with open(sidecar_path, "r", encoding="utf-8") as f:
        sj = json.load(f)

    experiment = sj.get("experiment_name", "(unnamed)")
    entries = sj.get("trajectory_library", {}).get("entries", [])
    n_entries = len(entries)

    print(f"Experiment: {experiment}")
    print(f"Sidecar: {os.path.basename(sidecar_path)}")
    print(f"Trajectory entries: {n_entries}")

    if n_entries == 0:
        print("  No entries to verify.")
        return True

    # Try to read timing from sidecar experiment_spec (v5+)
    exp_spec = sj.get("experiment_spec", {})
    sim_hz    = exp_spec.get("sim_hz", DEFAULT_SIM_HZ)
    onset_ms  = exp_spec.get("delayed_onset_ms", DEFAULT_DELAYED_ONSET_MS)
    pre_ms    = exp_spec.get("pre_translation_ms", DEFAULT_PRE_TRANSLATION_MS)
    trans_ms  = exp_spec.get("translation_duration_ms", DEFAULT_TRANSLATION_DUR_MS)
    has_spec_timing = "sim_hz" in exp_spec

    onset, t_start, t_end, expected_total = compute_timing(sim_hz, onset_ms, pre_ms, trans_ms)

    first_payload = entries[0].get("mk_payload", "")
    actual_total = len(first_payload.split(";")) if first_payload else 0

    if has_spec_timing:
        print(f"\nTiming (from sidecar experiment_spec):")
        print(f"  sim_hz={sim_hz}  onset_ms={onset_ms}  pre_ms={pre_ms}  "
              f"trans_ms={trans_ms}")
    else:
        print(f"\nTiming (from hardcoded defaults — sidecar has no spec timing):")

    print(f"  onset={onset}  tStart={t_start}  tEnd={t_end}  total={expected_total}")
    print(f"  actual payload length (first entry): {actual_total} frames")

    if actual_total != expected_total:
        print(f"  WARNING: frame count mismatch ({actual_total} vs {expected_total})")
        print(f"  Inferring timing from payload content.")
        onset, t_start, t_end, expected_total = infer_timing_from_payload(first_payload, entries[0])
        print(f"  Inferred: onset={onset} tStart={t_start} tEnd={t_end} total={expected_total}")

    # Verify each entry
    n_ok = 0
    n_fail = 0
    failures = []
    unique_shapes = {}  # (cond, rot_cfg, del_col, swap) -> (expected_mk, expected_col, entry)

    for e in entries:
        cond      = e.get("cond", "")
        rot_cfg   = e.get("rot_cfg", 0)
        del_col   = e.get("delayed_field_color", "")
        swap_type = e.get("swap_type", "N")
        stim_key  = e.get("stim_key", "")

        stored_mk    = e.get("mk_payload", "")
        stored_col   = e.get("color_payload", "")
        stored_mk_h  = e.get("mk_hash32", "").upper()
        stored_col_h = e.get("color_hash32", "").upper()

        # Generate expected
        exp_mk, exp_col = generate_trajectory(
            cond, rot_cfg, del_col, swap_type,
            onset, t_start, t_end, expected_total
        )

        # Compare payloads
        mk_match  = (exp_mk == stored_mk)
        col_match = (exp_col == stored_col)

        # Also verify hashes
        exp_mk_h  = fnv1a_32_hex(exp_mk)
        exp_col_h = fnv1a_32_hex(exp_col)
        mk_h_match  = (exp_mk_h == stored_mk_h)
        col_h_match = (exp_col_h == stored_col_h)

        if mk_match and col_match and mk_h_match and col_h_match:
            n_ok += 1
        else:
            n_fail += 1
            failures.append({
                "stim_key": stim_key,
                "mk_payload_match": mk_match,
                "col_payload_match": col_match,
                "mk_hash_match": mk_h_match,
                "col_hash_match": col_h_match,
                "expected_mk_hash": exp_mk_h,
                "stored_mk_hash": stored_mk_h,
                "expected_col_hash": exp_col_h,
                "stored_col_hash": stored_col_h,
            })

        # Collect unique shapes for plotting
        shape_key = (cond, rot_cfg, del_col, swap_type)
        if shape_key not in unique_shapes:
            unique_shapes[shape_key] = (exp_mk, exp_col, e)

    print(f"\nResults:")
    print(f"  Passed: {n_ok}/{n_entries}")
    print(f"  Failed: {n_fail}/{n_entries}")

    if failures:
        print(f"\nFailures:")
        for fail in failures[:10]:  # show first 10
            print(f"  {fail['stim_key']}:")
            if not fail["mk_payload_match"]:
                print(f"    mk_payload MISMATCH")
            if not fail["col_payload_match"]:
                print(f"    color_payload MISMATCH")
            if not fail["mk_hash_match"]:
                print(f"    mk_hash: expected={fail['expected_mk_hash']} stored={fail['stored_mk_hash']}")
            if not fail["col_hash_match"]:
                print(f"    col_hash: expected={fail['expected_col_hash']} stored={fail['stored_col_hash']}")
        if len(failures) > 10:
            print(f"  ... and {len(failures) - 10} more")

    # ── Method C: generate trajectory plots for all unique shapes ──
    if do_plots and unique_shapes:
        plot_all_shapes(unique_shapes, onset, t_start, t_end, expected_total,
                        sidecar_path, experiment)

    return n_fail == 0


def infer_timing_from_payload(mk_payload, entry):
    """Infer onset/tStart/tEnd/total from an actual payload."""
    frames = mk_payload.split(";")
    total = len(frames)

    # Find tStart: first frame with LINEAR (3) or NONCOH (4)
    t_start = total
    t_end = total
    for i, fr in enumerate(frames):
        codes = [int(x) for x in fr.split("|")]
        if LINEAR in codes or NONCOH in codes:
            if i < t_start:
                t_start = i
            t_end = i + 1  # exclusive

    # Find onset: first frame where color payload has non-K for sub2/sub3
    # (we don't have color_payload here, so use the entry)
    col_payload = entry.get("color_payload", "")
    onset = t_start  # default
    if col_payload:
        col_frames = col_payload.split(";")
        for i, fr in enumerate(col_frames):
            parts = fr.split("|")
            if len(parts) >= 4 and parts[2] != "K":
                onset = i
                break

    return onset, t_start, t_end, total


# ══════════════════════════════════════════════════════════════════════
#  PLOTTING (Method C: pseudo-session visual verification)
# ══════════════════════════════════════════════════════════════════════

def parse_payload_to_array(payload, kind="mk"):
    """Convert payload string to numpy array (nFrames, 4)."""
    frames = payload.split(";") if payload else []
    out = []
    for fr in frames:
        subs = fr.split("|")
        if kind == "mk":
            out.append([int(s) if s else 0 for s in subs])
        else:
            out.append([s[0] if s else "K" for s in subs])
    if not out:
        return None
    if kind == "mk":
        return np.array(out, dtype=float)
    return np.array(out, dtype=object)


def plot_motion(ax, mk_arr, onset, t_start, t_end, title="", color_arr=None):
    from matplotlib.lines import Line2D

    nF, nS = mk_arr.shape
    sample_every = max(1, nF // 25)
    sample_frames = list(range(0, nF, sample_every))
    if sample_frames[-1] != nF - 1:
        sample_frames.append(nF - 1)

    cmap = {"R": "#CC3333", "G": "#228B22"}
    specs = [
        {"marker": "o", "filled": True,  "s": 22, "lw": 1.0},
        {"marker": "s", "filled": False, "s": 48, "lw": 1.5},
        {"marker": "^", "filled": True,  "s": 26, "lw": 1.0},
        {"marker": "D", "filled": False, "s": 56, "lw": 1.5},
    ]

    for s in range(nS):
        sp = specs[s % len(specs)]
        ax.plot(np.arange(nF), mk_arr[:, s], color="#D0D0D0", linewidth=0.5, zorder=1)

        xs, ys, cs = [], [], []
        for f in sample_frames:
            if color_arr is not None and f < color_arr.shape[0]:
                c = cmap.get(str(color_arr[f, s]))
                if c is None:
                    continue
            else:
                c = "#666666"
            xs.append(f)
            ys.append(mk_arr[f, s])
            cs.append(c)
        if not xs:
            continue
        if sp["filled"]:
            ax.scatter(xs, ys, marker=sp["marker"], c=cs,
                       edgecolors="none", s=sp["s"], zorder=3 + s)
        else:
            ax.scatter(xs, ys, marker=sp["marker"], facecolors="none",
                       edgecolors=cs, s=sp["s"], linewidths=sp["lw"], zorder=3 + s)

    ax.set_xlabel("frame", fontsize=8)
    ax.set_ylabel("motion kind", fontsize=8)
    ax.set_title(title, fontsize=9)
    ax.set_yticks([1, 2, 3, 4])
    ax.set_yticklabels(["CW rot", "CCW rot", "Trans (coh)", "Trans (noise)"], fontsize=7)
    ax.set_ylim(0.5, 4.5)
    ax.axvspan(t_start, t_end, alpha=0.08, color="blue")
    ax.axvline(onset, ls=":", color="gray", lw=0.8)
    ax.axvline(t_start, ls="--", color="blue", lw=0.8)
    ax.axvline(t_end, ls="--", color="blue", lw=0.8)
    ax.tick_params(axis='both', labelsize=7)

    legend_handles = [
        Line2D([0], [0], marker="o", color="w", markerfacecolor="gray",
               markersize=5, linestyle="None", label="S0 (FieldA)"),
        Line2D([0], [0], marker="s", color="w", markeredgecolor="gray",
               markerfacecolor="none", markersize=6, markeredgewidth=1.5,
               linestyle="None", label="S1 (FieldA)"),
        Line2D([0], [0], marker="^", color="w", markerfacecolor="gray",
               markersize=5, linestyle="None", label="S2 (FieldB)"),
        Line2D([0], [0], marker="D", color="w", markeredgecolor="gray",
               markerfacecolor="none", markersize=6, markeredgewidth=1.5,
               linestyle="None", label="S3 (FieldB)"),
    ]
    ax.legend(handles=legend_handles, loc="upper right", fontsize=6)


def plot_all_shapes(unique_shapes, onset, t_start, t_end, total,
                    sidecar_path, experiment):
    import matplotlib.pyplot as plt

    shapes = sorted(unique_shapes.keys())
    n = len(shapes)
    ncols = min(4, n)
    nrows = math.ceil(n / ncols)

    fig, axes = plt.subplots(nrows, ncols,
                             figsize=(4.5 * ncols, 3.5 * nrows),
                             squeeze=False)

    fig.suptitle(f"Experiment: {experiment} — All {n} unique trajectory shapes\n"
                 f"onset={onset}  tStart={t_start}  tEnd={t_end}  total={total}",
                 fontsize=11, y=0.99)

    for i, key in enumerate(shapes):
        cond, rot_cfg, del_col, swap_type = key
        mk_payload, col_payload, _ = unique_shapes[key]

        mk_arr  = parse_payload_to_array(mk_payload, "mk")
        col_arr = parse_payload_to_array(col_payload, "color")

        rot_label = f"Rot{rot_cfg}"
        a_rot_label = "CW" if rot_cfg == 0 else "CCW"
        b_rot_label = "CCW" if rot_cfg == 0 else "CW"

        title = (f"{cond}  {rot_label}  Del={del_col}  Swap={swap_type}\n"
                 f"A({a_rot_label})  B({b_rot_label})")

        row, col = divmod(i, ncols)
        ax = axes[row][col]
        plot_motion(ax, mk_arr, onset, t_start, t_end, title=title,
                    color_arr=col_arr)

    # Hide unused subplots
    for i in range(n, nrows * ncols):
        row, col = divmod(i, ncols)
        axes[row][col].set_visible(False)

    plt.tight_layout(rect=[0, 0, 1, 0.96])
    out_dir = os.path.dirname(sidecar_path)
    out_name = os.path.basename(sidecar_path).replace(".sidecar.json", "")
    out_path = os.path.join(out_dir, f"{out_name}_verification_plots.png")
    plt.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"\nWrote verification plots: {out_path}")


# ══════════════════════════════════════════════════════════════════════
#  MAIN
# ══════════════════════════════════════════════════════════════════════

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 verify_trajectories.py <sidecar.json> [--plots]")
        sys.exit(1)

    sidecar_path = sys.argv[1]
    do_plots = "--plots" in sys.argv

    if not os.path.isfile(sidecar_path):
        print(f"File not found: {sidecar_path}")
        sys.exit(1)

    ok = verify_sidecar(sidecar_path, do_plots=do_plots)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
