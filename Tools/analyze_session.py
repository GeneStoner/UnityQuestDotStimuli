#!/usr/bin/env python3
"""
analyze_session.py — check and summarize one VRDots session.

    python3 Tools/analyze_session.py path/to/vr_dots_session_YYMMDD_HHMM.tsv

Prints three blocks:

  1. STIMULUS CHECK   what the headset actually did (from the .sidecar.json)
  2. TIMING CHECK     measured translation duration and dropped frames
  3. RESULTS          percent correct and the cueing effect, by swap type

Only needs Python 3.9+ (no packages). Trials where the observer confirmed
without choosing a direction are logged with RespDeg -1 and re-queued later;
they are excluded from percent correct and reported separately.
"""

import csv
import json
import math
import sys
from collections import defaultdict
from pathlib import Path

CHANCE = 12.5  # 8 alternatives

EXPECTED = {
    "device_model": "Oculus Quest 3",
    "refresh_rate_hz": 90,
    "refresh_rate_confirmed": True,
    "render_scale": 1.23,
    "msaa_samples": 4,
}


def pct(rows):
    """Percent correct over rows that carry a response."""
    scored = [r for r in rows if r["resp"] >= 0]
    if not scored:
        return float("nan"), 0
    hits = sum(1 for r in scored if r["resp"] == r["truth"])
    return 100.0 * hits / len(scored), len(scored)


def chi2_2x2(a, b, c, d):
    """a/b = hits/total group 1, c/d = group 2. Returns chi-square or None."""
    A, B, C, D = a, b - a, c, d - c
    n = A + B + C + D
    denom = (A + B) * (C + D) * (A + C) * (B + D)
    if denom == 0:
        return None
    return n * (A * D - B * C) ** 2 / denom


def stars(chi):
    if chi is None:
        return ""
    for thresh, mark in ((10.83, "***"), (6.63, "**"), (3.84, "*")):
        if chi >= thresh:
            return mark
    return "n.s."


def load(tsv_path):
    rows = []
    with open(tsv_path, newline="") as f:
        for r in csv.DictReader(f, delimiter="\t"):
            def num(key, default=float("nan")):
                try:
                    return float(r[key])
                except (KeyError, TypeError, ValueError):
                    return default
            rows.append({
                "cond": r.get("Cond", ""),
                "swap": r.get("SwapType", "") or "N",
                "colour": r.get("DelayedFieldColor", ""),
                "truth": num("TransDeg"),
                "resp": num("RespDeg", -1),
                "dur": num("TransDurMsMeasured", -1),
                "frames": num("TransRenderedFrames", -1),
                "gap": num("MaxFrameGapMs", -1),
                "trans_gap": num("TransMaxFrameGapMs", -1),
                "late": num("StimLateFrames", -1),
                "experiment": r.get("Experiment", ""),
            })
    return rows


def stimulus_check(tsv_path):
    side = Path(str(tsv_path) + ".sidecar.json")
    if not side.exists():
        print("  no .sidecar.json beside the TSV — cannot verify the stimulus")
        return
    d = json.loads(side.read_text())
    disp, spec = d.get("display", {}), d.get("experiment_spec", {})

    if not disp:
        print("  sidecar has no 'display' block: built before 2026-09-17, "
              "so the refresh rate and render scale were not recorded")
    for key, want in EXPECTED.items():
        got = disp.get(key, "missing")
        ok = "OK " if got == want else "!! "
        print(f"  {ok}{key:24s} {got}   (expected {want})")

    print(f"     eye_texture_px           {disp.get('eye_texture_px', '?')}")
    print(f"     build_date               {d.get('build_date', '?')}")
    for key in ("spec_name", "dots_per_field", "dot_size_deg", "aperture_radius_deg",
                "translation_duration_ms", "delayed_onset_ms", "include_cm_swaps"):
        print(f"     {key:24s} {spec.get(key, '?')}")


def timing_check(rows):
    def med(key):
        vals = sorted(r[key] for r in rows if r[key] >= 0)
        return vals[len(vals) // 2] if vals else float("nan")

    if all(r["dur"] < 0 for r in rows):
        print("  no measured-timing columns: session recorded before 2026-09-17")
        return

    frames = [r["frames"] for r in rows if r["frames"] >= 0]
    odd = sum(1 for f in frames if f != med("frames"))
    stalls = sum(1 for r in rows if r["trans_gap"] > 16.7)
    late = sum(1 for r in rows if r["late"] > 0)

    print(f"  translation duration   median {med('dur'):.1f} ms")
    print(f"  frames shown           median {med('frames'):.0f}"
          f"   ({odd} trial(s) differed)")
    print(f"  worst gap in trial     median {med('gap'):.1f} ms")
    print(f"  stall inside the translation window (>16.7 ms): {stalls} of {len(rows)} trials")
    print(f"  trials with a late frame anywhere in the stimulus: {late} of {len(rows)}")


def results(rows):
    unanswered = sum(1 for r in rows if r["resp"] < 0)
    print(f"  trials logged {len(rows)}   with a response {len(rows) - unanswered}"
          f"   unanswered and re-queued {unanswered}")
    print(f"  chance is {CHANCE}%\n")

    by_swap = defaultdict(list)
    for r in rows:
        by_swap[r["swap"]].append(r)

    print(f"  {'swap':6s} {'CUED':>16s} {'UNCUED':>16s} {'cueing':>12s}")
    for swap in sorted(by_swap):
        cu = [r for r in by_swap[swap] if r["cond"] == "CUED"]
        un = [r for r in by_swap[swap] if r["cond"] == "UNCUED"]
        p_cu, n_cu = pct(cu)
        p_un, n_un = pct(un)
        chi = chi2_2x2(round(p_cu * n_cu / 100), n_cu, round(p_un * n_un / 100), n_un)
        print(f"  {swap:6s} {p_cu:8.1f}% (n={n_cu:3d}) {p_un:8.1f}% (n={n_un:3d})"
              f" {p_cu - p_un:+8.1f} pp {stars(chi)}")

    # Which field translated: the delayed one on CUED trials, the other on UNCUED
    print()
    for colour, label in (("R", "red"), ("G", "green")):
        sub = [r for r in rows
               if (r["colour"] == colour) == (r["cond"] == "CUED")]
        p, n = pct(sub)
        print(f"  translating field {label:5s} {p:5.1f}% correct (n={n})")

    # How wrong are the errors?
    errs = [abs((r["truth"] - r["resp"] + 180) % 360 - 180)
            for r in rows if r["resp"] >= 0]
    if errs:
        near = 100.0 * sum(1 for e in errs if e <= 45) / len(errs)
        print(f"\n  responses within 45 deg of the true direction: {near:.0f}%"
              "   (adjacent-direction errors, not random guessing, if high)")


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    tsv = Path(sys.argv[1]).expanduser()
    rows = load(tsv)
    if not rows:
        sys.exit(f"no trials in {tsv}")

    print(f"\n=== {tsv.name}   {rows[0]['experiment']} ===")
    print("\n1. STIMULUS CHECK")
    stimulus_check(tsv)
    print("\n2. TIMING CHECK")
    timing_check(rows)
    print("\n3. RESULTS")
    results(rows)
    print()


if __name__ == "__main__":
    main()
