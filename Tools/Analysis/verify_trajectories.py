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

# ── Depth plane codes (match StimulusConditionsLibrary.DepthPlane) ───
FIXATION = 0
NEAR     = 1
FAR      = 2

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
    onset   = ms_to_frames(onset_ms, sim_hz)
    pre     = ms_to_frames(pre_ms, sim_hz)
    trans   = ms_to_frames(trans_ms, sim_hz)
    post    = ms_to_frames(post_ms, sim_hz)
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

def parse_swap_flags(swap_type):
    """Parse swap_type string into boolean flags."""
    s = swap_type if swap_type else "N"
    return {
        "motion":   "M"   in s and s != "N",
        "color":    "C"   in s and s != "N",
        "dots50":   "D"   in s and s != "N",
        "depth":    s == "Z" or (s != "N" and "Z" in s and "Zd" not in s and "ZdA" not in s and "ZdB" not in s),
        "depth50":  "Zd"  in s and "ZdA" not in s and "ZdB" not in s,
        "depth50A": "ZdA" in s,
        "depth50B": "ZdB" in s,
    }


def generate_trajectory(cond, rot_cfg, delayed_color, swap_type,
                        onset, t_start, t_end, total,
                        delayed_depth="N", depth_separation_m=0.0,
                        non_delayed_color=None):
    """
    Return (mk_payload, color_payload, depth_payload) strings in the same
    format as the C# sidecar writer.

    delayed_depth: "N" = Near, "F" = Far (or "" if no depth planes)
    depth_separation_m: > 0 enables depth planes
    non_delayed_color: explicit non-delayed field color. If None, inferred
        as the opposite of delayed_color (legacy two-color experiments).
        Pass the same value as delayed_color for same-color experiments.
    """
    N = total
    is_cued = (cond == "CUED")

    # Rotation config
    a_rot = CW  if rot_cfg == 0 else CCW
    b_rot = CCW if rot_cfg == 0 else CW

    # Colors
    d_col  = delayed_color
    if non_delayed_color is not None:
        nd_col = non_delayed_color
    else:
        nd_col = "G" if delayed_color == "R" else "R"

    flags = parse_swap_flags(swap_type)

    # Depth planes
    use_depth = (depth_separation_m > 0.0)
    field_b_depth = NEAR if delayed_depth == "N" else FAR
    field_a_depth = FAR  if field_b_depth == NEAR else NEAR

    mk_rows    = []
    col_rows   = []
    depth_rows = []

    for f in range(N):
        after_onset = (f >= onset)
        after_swap  = (f >= t_start)

        # ── rotation ─────────────────────────────────────────────────
        cur_a = b_rot if (flags["motion"] and after_swap) else a_rot
        cur_b = a_rot if (flags["motion"] and after_swap) else b_rot

        # ── color ────────────────────────────────────────────────────
        if flags["color"] and after_swap:
            fa_col, fb_col = d_col, nd_col
        else:
            fa_col, fb_col = nd_col, d_col

        # ── field membership + motion/color ──────────────────────────
        if flags["dots50"] and after_swap:
            mk  = [cur_a, cur_b, cur_b, cur_a]
            col = ([fa_col, fb_col, fb_col, fa_col] if after_onset
                   else [fa_col, "K", "K", fa_col])
        else:
            mk  = [cur_a, cur_a, cur_b, cur_b]
            col = ([fa_col, fa_col, fb_col, fb_col] if after_onset
                   else [fa_col, fa_col, "K", "K"])

        # ── ZdA/ZdB motion override (rotation follows depth group) ───
        if flags["depth50A"] and after_swap:
            # Near-group (S0,S3)=curARot, Far-group (S1,S2)=curBRot
            mk = [cur_a, cur_b, cur_b, cur_a]
        if flags["depth50B"] and after_swap:
            # Far-group (S0,S3)=curARot, Near-group (S1,S2)=curBRot
            mk = [cur_a, cur_b, cur_b, cur_a]

        mk_rows.append(mk)
        col_rows.append(col)

        # ── depth ────────────────────────────────────────────────────
        if use_depth:
            if flags["depth"] and after_swap:
                # 100% depth swap: all fields exchange planes
                dep = [field_b_depth, field_b_depth, field_a_depth, field_a_depth]
            elif flags["depth50"] and after_swap:
                # Zd (legacy): S0↔S2 exchange
                dep = [field_b_depth, field_a_depth, field_a_depth, field_b_depth]
            elif flags["depth50A"] and after_swap:
                # ZdA: S0→fieldB, S1→fieldA, S2→fieldA, S3→fieldB
                dep = [field_b_depth, field_a_depth, field_a_depth, field_b_depth]
            elif flags["depth50B"] and after_swap:
                # ZdB: S0→fieldA, S1→fieldB, S2→fieldB, S3→fieldA
                dep = [field_a_depth, field_b_depth, field_b_depth, field_a_depth]
            else:
                # Default: S0,S1=fieldA; S2,S3=fieldB
                dep = [field_a_depth, field_a_depth, field_b_depth, field_b_depth]
        else:
            dep = [FIXATION, FIXATION, FIXATION, FIXATION]

        depth_rows.append(dep)

    # ── translation override ──────────────────────────────────────────
    f_start = max(0, t_start)
    f_end   = min(N, t_end)
    for f in range(f_start, f_end):
        if flags["dots50"]:
            if is_cued:
                mk_rows[f][2] = LINEAR;  mk_rows[f][1] = NONCOH
            else:
                mk_rows[f][0] = LINEAR;  mk_rows[f][3] = NONCOH
        elif flags["depth50A"] or flags["depth50B"]:
            # ZdA/ZdB: same translation subfields as plain N
            if is_cued:
                mk_rows[f][2] = LINEAR;  mk_rows[f][1] = NONCOH
            else:
                mk_rows[f][0] = LINEAR;  mk_rows[f][3] = NONCOH
        else:
            if is_cued:
                mk_rows[f][2] = LINEAR;  mk_rows[f][3] = NONCOH
            else:
                mk_rows[f][0] = LINEAR;  mk_rows[f][1] = NONCOH

    # ── format payloads ───────────────────────────────────────────────
    mk_payload    = ";".join("|".join(str(v) for v in row) for row in mk_rows)
    col_payload   = ";".join("|".join(row) for row in col_rows)
    depth_payload = ";".join("|".join(str(v) for v in row) for row in depth_rows)
    return mk_payload, col_payload, depth_payload


# ══════════════════════════════════════════════════════════════════════
#  VERIFICATION
# ══════════════════════════════════════════════════════════════════════

def verify_sidecar(sidecar_path, do_plots=False):
    with open(sidecar_path, "r", encoding="utf-8") as f:
        sj = json.load(f)

    experiment = sj.get("experiment_name", "(unnamed)")
    entries    = sj.get("trajectory_library", {}).get("entries", [])
    n_entries  = len(entries)

    print(f"Experiment: {experiment}")
    print(f"Sidecar: {os.path.basename(sidecar_path)}")
    print(f"Trajectory entries: {n_entries}")

    if n_entries == 0:
        print("  No entries to verify.")
        return True

    # Timing from sidecar
    exp_spec = sj.get("experiment_spec", {})
    sim_hz   = exp_spec.get("sim_hz",                  DEFAULT_SIM_HZ)
    onset_ms = exp_spec.get("delayed_onset_ms",         DEFAULT_DELAYED_ONSET_MS)
    pre_ms   = exp_spec.get("pre_translation_ms",       DEFAULT_PRE_TRANSLATION_MS)
    trans_ms = exp_spec.get("translation_duration_ms",  DEFAULT_TRANSLATION_DUR_MS)
    depth_sep = exp_spec.get("depth_separation_m",      0.0)
    has_spec  = "sim_hz" in exp_spec

    onset, t_start, t_end, expected_total = compute_timing(sim_hz, onset_ms, pre_ms, trans_ms)

    first_payload = entries[0].get("mk_payload", "")
    actual_total  = len(first_payload.split(";")) if first_payload else 0

    src = "from sidecar experiment_spec" if has_spec else "from hardcoded defaults"
    print(f"\nTiming ({src}):")
    print(f"  sim_hz={sim_hz}  onset_ms={onset_ms}  pre_ms={pre_ms}  trans_ms={trans_ms}")
    print(f"  onset={onset}  tStart={t_start}  tEnd={t_end}  total={expected_total}")
    print(f"  depth_separation_m={depth_sep}")
    print(f"  actual payload length (first entry): {actual_total} frames")

    if actual_total != expected_total:
        print(f"  WARNING: frame count mismatch ({actual_total} vs {expected_total})")
        onset, t_start, t_end, expected_total = infer_timing_from_payload(
            first_payload, entries[0])
        print(f"  Inferred: onset={onset} tStart={t_start} tEnd={t_end} total={expected_total}")

    # ── Verify each entry ─────────────────────────────────────────────
    n_ok = 0; n_fail = 0; failures = []
    unique_shapes = {}

    for e in entries:
        cond       = e.get("cond", "")
        rot_cfg    = e.get("rot_cfg", 0)
        del_col    = e.get("delayed_field_color", "")
        del_dep    = e.get("delayed_field_depth", "N")
        swap_type  = e.get("swap_type", "N")
        stim_key   = e.get("stim_key", "")

        stored_mk      = e.get("mk_payload", "")
        stored_col     = e.get("color_payload", "")
        stored_dep     = e.get("depth_payload", "")
        stored_mk_h    = e.get("mk_hash32",    "").upper()
        stored_col_h   = e.get("color_hash32", "").upper()
        stored_dep_h   = e.get("depth_hash32", "").upper()

        # Extract actual non-delayed color from frame 0 of color payload.
        # Pre-onset, S0 always shows the non-delayed field color (S2/S3 are "K").
        nd_col = None
        if stored_col:
            frame0 = stored_col.split(";")[0].split("|")
            if frame0 and frame0[0] not in ("K", ""):
                nd_col = frame0[0]

        exp_mk, exp_col, exp_dep = generate_trajectory(
            cond, rot_cfg, del_col, swap_type,
            onset, t_start, t_end, expected_total,
            delayed_depth=del_dep, depth_separation_m=depth_sep,
            non_delayed_color=nd_col
        )

        mk_ok  = (exp_mk  == stored_mk)
        col_ok = (exp_col == stored_col)
        dep_ok = (exp_dep == stored_dep) if stored_dep else True  # skip if absent

        exp_mk_h  = fnv1a_32_hex(exp_mk)
        exp_col_h = fnv1a_32_hex(exp_col)
        exp_dep_h = fnv1a_32_hex(exp_dep)
        mk_h_ok   = (exp_mk_h  == stored_mk_h)
        col_h_ok  = (exp_col_h == stored_col_h)
        dep_h_ok  = (exp_dep_h == stored_dep_h) if stored_dep_h else True

        if mk_ok and col_ok and dep_ok and mk_h_ok and col_h_ok and dep_h_ok:
            n_ok += 1
        else:
            n_fail += 1
            failures.append({
                "stim_key":      stim_key,
                "mk_ok":         mk_ok and mk_h_ok,
                "col_ok":        col_ok and col_h_ok,
                "dep_ok":        dep_ok and dep_h_ok,
                "exp_mk_h":      exp_mk_h,  "stored_mk_h":  stored_mk_h,
                "exp_col_h":     exp_col_h, "stored_col_h": stored_col_h,
                "exp_dep_h":     exp_dep_h, "stored_dep_h": stored_dep_h,
                # First differing frame for depth (to help diagnose)
                "dep_first_diff": _first_diff_frame(exp_dep, stored_dep),
            })

        shape_key = (cond, rot_cfg, del_col, swap_type, del_dep)
        if shape_key not in unique_shapes:
            unique_shapes[shape_key] = (exp_mk, exp_col, exp_dep, e)

    print(f"\nResults:")
    print(f"  Passed: {n_ok}/{n_entries}")
    print(f"  Failed: {n_fail}/{n_entries}")

    if failures:
        print(f"\nFailures (first 10):")
        for fail in failures[:10]:
            parts = []
            if not fail["mk_ok"]:
                parts.append(f"mk(exp={fail['exp_mk_h']} got={fail['stored_mk_h']})")
            if not fail["col_ok"]:
                parts.append(f"color(exp={fail['exp_col_h']} got={fail['stored_col_h']})")
            if not fail["dep_ok"]:
                fd = fail["dep_first_diff"]
                parts.append(f"depth(exp={fail['exp_dep_h']} got={fail['stored_dep_h']}"
                              f"{', first diff f='+str(fd) if fd is not None else ''})")
            print(f"  {fail['stim_key']}: {', '.join(parts)}")
        if len(failures) > 10:
            print(f"  ... and {len(failures) - 10} more")

    if do_plots and unique_shapes:
        plot_all_shapes(unique_shapes, onset, t_start, t_end, expected_total,
                        sidecar_path, experiment, depth_sep > 0)

    return n_fail == 0


def _first_diff_frame(s1, s2):
    if not s1 or not s2:
        return None
    for i, (a, b) in enumerate(zip(s1.split(";"), s2.split(";"))):
        if a != b:
            return i
    return None


def infer_timing_from_payload(mk_payload, entry):
    frames = mk_payload.split(";")
    total  = len(frames)
    t_start = total; t_end = total
    for i, fr in enumerate(frames):
        codes = [int(x) for x in fr.split("|")]
        if LINEAR in codes or NONCOH in codes:
            if i < t_start: t_start = i
            t_end = i + 1
    col_payload = entry.get("color_payload", "")
    onset = t_start
    if col_payload:
        for i, fr in enumerate(col_payload.split(";")):
            parts = fr.split("|")
            if len(parts) >= 4 and parts[2] != "K":
                onset = i; break
    return onset, t_start, t_end, total


# ══════════════════════════════════════════════════════════════════════
#  PLOTTING (Method C)
# ══════════════════════════════════════════════════════════════════════

def parse_mk_payload(payload):
    if not payload: return None
    out = []
    for fr in payload.split(";"):
        out.append([int(s) if s else 0 for s in fr.split("|")])
    return np.array(out, dtype=float)

def parse_col_payload(payload):
    if not payload: return None
    out = []
    for fr in payload.split(";"):
        out.append([s[0] if s else "K" for s in fr.split("|")])
    return np.array(out, dtype=object)

def parse_dep_payload(payload):
    if not payload: return None
    out = []
    for fr in payload.split(";"):
        out.append([int(s) if s else 0 for s in fr.split("|")])
    return np.array(out, dtype=float)


def plot_shape(axes_row, mk_arr, col_arr, dep_arr,
               onset, t_start, t_end, title, has_depth):
    """Plot one condition shape into a row of 1 or 2 axes."""
    from matplotlib.lines import Line2D

    cmap  = {"R": "#CC3333", "G": "#228B22"}
    specs = [
        {"marker": "o", "filled": True,  "s": 22, "lw": 1.0},
        {"marker": "s", "filled": False, "s": 48, "lw": 1.5},
        {"marker": "^", "filled": True,  "s": 26, "lw": 1.0},
        {"marker": "D", "filled": False, "s": 56, "lw": 1.5},
    ]

    for ax_i, (arr, yticks, ylabels, ylabel) in enumerate([
        (mk_arr,  [1,2,3,4], ["CW","Trans(coh)","Trans(noise)","CCW"], "motion"),
        (dep_arr, [1,2],     ["Near","Far"],                           "depth"),
    ]):
        if ax_i == 1 and not has_depth:
            continue
        ax = axes_row[ax_i]
        if arr is None:
            ax.set_visible(False); continue

        nF, nS = arr.shape
        sample = list(range(0, nF, max(1, nF//25)))
        if sample[-1] != nF-1: sample.append(nF-1)

        for s in range(nS):
            sp = specs[s]
            ax.plot(np.arange(nF), arr[:, s], color="#D8D8D8", lw=0.5, zorder=1)
            xs, ys, cs = [], [], []
            for f in sample:
                if arr[f, s] == 0: continue
                c = cmap.get(str(col_arr[f, s])) if col_arr is not None else "#666666"
                if c is None: continue
                xs.append(f); ys.append(arr[f, s]); cs.append(c)
            if not xs: continue
            if sp["filled"]:
                ax.scatter(xs, ys, marker=sp["marker"], c=cs,
                           edgecolors="none", s=sp["s"], zorder=3+s)
            else:
                ax.scatter(xs, ys, marker=sp["marker"], facecolors="none",
                           edgecolors=cs, s=sp["s"], linewidths=sp["lw"], zorder=3+s)

        ax.axvspan(t_start, t_end, alpha=0.08, color="blue")
        ax.axvline(onset,   ls=":",  color="gray", lw=0.8)
        ax.axvline(t_start, ls="--", color="blue", lw=0.8)
        ax.axvline(t_end,   ls="--", color="blue", lw=0.8)
        ax.set_yticks(yticks)
        ax.set_yticklabels(ylabels, fontsize=7)
        ax.set_ylabel(ylabel, fontsize=8)
        ax.tick_params(axis="both", labelsize=7)
        if ax_i == 0:
            ax.set_ylim(0.5, 4.5)
            ax.set_title(title, fontsize=8, loc="left")
            ax.set_xticklabels([])
            leg = [
                Line2D([0],[0], marker="o", color="w", markerfacecolor="#666",
                       markersize=5, ls="None", label="S0"),
                Line2D([0],[0], marker="s", color="w", markeredgecolor="#666",
                       markerfacecolor="none", markersize=6, markeredgewidth=1.5,
                       ls="None", label="S1"),
                Line2D([0],[0], marker="^", color="w", markerfacecolor="#666",
                       markersize=5, ls="None", label="S2(delayed)"),
                Line2D([0],[0], marker="D", color="w", markeredgecolor="#666",
                       markerfacecolor="none", markersize=6, markeredgewidth=1.5,
                       ls="None", label="S3(delayed)"),
            ]
            ax.legend(handles=leg, loc="upper right", fontsize=6, framealpha=0.7)
        else:
            ax.set_ylim(0.5, 2.5)
            ax.set_xlabel("frame", fontsize=8)


def plot_all_shapes(unique_shapes, onset, t_start, t_end, total,
                    sidecar_path, experiment, has_depth):
    import matplotlib.pyplot as plt
    import matplotlib.gridspec as gridspec

    shapes = sorted(unique_shapes.keys())
    n      = len(shapes)
    n_axes = 2 if has_depth else 1   # rows per condition: motion + depth

    fig = plt.figure(figsize=(16, (2.8 * n_axes + 0.3) * n))
    outer = gridspec.GridSpec(n, 1, hspace=0.55, figure=fig)

    fig.suptitle(
        f"Experiment: {experiment} — All {n} unique trajectory shapes\n"
        f"onset={onset}  tStart={t_start}  tEnd={t_end}  total={total}",
        fontsize=11, y=1.002)

    for i, key in enumerate(shapes):
        cond, rot_cfg, del_col, swap_type, del_dep = key
        mk_p, col_p, dep_p, _ = unique_shapes[key]

        mk_arr  = parse_mk_payload(mk_p)
        col_arr = parse_col_payload(col_p)
        dep_arr = parse_dep_payload(dep_p) if has_depth else None

        inner = gridspec.GridSpecFromSubplotSpec(
            n_axes, 1, subplot_spec=outer[i],
            height_ratios=([3, 1.5] if has_depth else [1]),
            hspace=0.08)
        ax_mk  = fig.add_subplot(inner[0])
        ax_dep = fig.add_subplot(inner[1], sharex=ax_mk) if has_depth else None

        a_label = "CW" if rot_cfg == 0 else "CCW"
        b_label = "CCW" if rot_cfg == 0 else "CW"
        title = (f"{cond}  Rot{rot_cfg}({a_label}/{b_label})  "
                 f"Del={del_col}  Dep={del_dep}  Swap={swap_type}")

        axes_row = [ax_mk] + ([ax_dep] if has_depth else [])
        plot_shape(axes_row, mk_arr, col_arr, dep_arr,
                   onset, t_start, t_end, title, has_depth)

    plt.tight_layout(rect=[0, 0, 1, 0.998])
    out_dir  = os.path.dirname(sidecar_path)
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
    do_plots     = "--plots" in sys.argv

    if not os.path.isfile(sidecar_path):
        print(f"File not found: {sidecar_path}")
        sys.exit(1)

    ok = verify_sidecar(sidecar_path, do_plots=do_plots)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
