"""
analyze_frame0_diag.py
======================
Reads frame0_diag_NNNN.csv files written by StimulusBuilder.DumpFrame0Diagnostics()
and prints a per-subfield depth summary to diagnose the pre-motion "funky" appearance.

Usage:
    adb pull /sdcard/Android/data/com.genestoner.vrdptsrebuildX.test/files/frame0_diag_* /tmp/frame0/
    python analyze_frame0_diag.py /tmp/frame0/frame0_diag_0001.csv [...]
"""

import sys
import os
import csv
import numpy as np
from pathlib import Path


def parse_diag(path):
    params = {}
    rows = []
    with open(path, "r") as f:
        lines = f.readlines()

    # First non-comment line is the header
    header = None
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if line.startswith("#"):
            # Parse param comment: # key=val key=val ...
            for tok in line[1:].split():
                if "=" in tok:
                    k, v = tok.split("=", 1)
                    params[k] = v
            continue
        if header is None:
            header = line.split(",")
            continue
        vals = line.split(",")
        if len(vals) == len(header):
            rows.append(dict(zip(header, vals)))

    return params, rows


def analyze(path):
    params, rows = parse_diag(path)

    print(f"\n{'='*60}")
    print(f"File: {os.path.basename(path)}")
    print(f"Params: {params}")
    print(f"Total dot records: {len(rows)}")
    print()

    # Group by subfield
    by_sf = {}
    for r in rows:
        s = int(r["subfield"])
        by_sf.setdefault(s, []).append(r)

    depth_offset_m = float(params.get("depthOffset_m", 0))

    for s in sorted(by_sf.keys()):
        sf_rows = by_sf[s]
        dp_set  = set(r["depth_plane"] for r in sf_rows)
        z_vals  = np.array([float(r["world_z"]) for r in sf_rows])
        z_off   = np.array([float(r["z_offset_m"]) for r in sf_rows])
        ps_vals = np.array([float(r["persp_scale"]) for r in sf_rows])
        ren_vals = [int(r.get("renderer_enabled", 0)) for r in sf_rows]
        null_vals = [int(r.get("renderer_null", 0)) for r in sf_rows]
        n_visible = sum(ren_vals)
        n_null    = sum(null_vals)

        # halfDispWorld (same for all dots in subfield — show unique values)
        hdw_vals = sorted(set(float(r["half_disp_world"]) for r in sf_rows
                              if "half_disp_world" in r))

        print(f"  Sub{s}: depth_plane={dp_set}  n_dots={len(sf_rows)}  "
              f"n_visible={n_visible}  n_renderer_null={n_null}")
        print(f"         world_z  mean={z_vals.mean():+.6f}  std={z_vals.std():.6f}  "
              f"min={z_vals.min():+.6f}  max={z_vals.max():+.6f}")
        print(f"         z_offset mean={z_off.mean():+.6f}  persp_scale mean={ps_vals.mean():.6f}")
        print(f"         half_disp_world (computed): {[f'{v:+.6f}' for v in hdw_vals]}")

        # Flags
        if z_vals.std() > 1e-4:
            if params.get("useSSShader", "False") == "True":
                print(f"         (world_z std={z_vals.std():.6f} m — expected head tilt in SS mode, not a bug)")
            else:
                print(f"         *** WARNING: high world_z std ({z_vals.std():.6f} m) — classic-mode coplanar issue!")
        if len(dp_set) > 1:
            print(f"         *** WARNING: mixed depth planes in one subfield: {dp_set}")
        if n_null > 0:
            print(f"         *** WARNING: {n_null} null renderers — those dots skip MPB update!")
        if not hdw_vals or hdw_vals == [0.0]:
            print(f"         *** WARNING: halfDispWorld=0 — no disparity being applied!")
        print()

    # Cross-subfield z comparison
    print("  Expected Near z_offset:", -depth_offset_m, " Far z_offset:", +depth_offset_m)
    all_z = {s: np.array([float(r["world_z"]) for r in rows if int(r["subfield"]) == s])
             for s in by_sf}
    pairs = [(s0, s1) for s0 in sorted(all_z) for s1 in sorted(all_z) if s1 > s0]
    for s0, s1 in pairs:
        dz = all_z[s1].mean() - all_z[s0].mean()
        print(f"  world_z mean(sub{s1}) - mean(sub{s0}) = {dz:+.6f} m")


if __name__ == "__main__":
    paths = sys.argv[1:]
    if not paths:
        print("Usage: python analyze_frame0_diag.py <csv_file> [...]")
        sys.exit(1)
    for p in paths:
        analyze(p)
