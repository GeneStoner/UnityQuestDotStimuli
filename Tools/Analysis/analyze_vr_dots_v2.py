#!/usr/bin/env python3
import sys, os, json, math
from collections import Counter
import numpy as np
import matplotlib.pyplot as plt

USAGE = "Usage: python3 analyze_vr_dots_v2.py <path/to/session.tsv>"

# ---------- helpers ----------
def read_tsv(path):
    with open(path, "r", encoding="utf-8-sig") as f:
        lines = [ln.rstrip("\n") for ln in f]

    header = None
    header_idx = -1
    for i, ln in enumerate(lines):
        if not ln.strip():
            continue
        header = ln.split("\t")
        header_idx = i
        break
    if header is None:
        raise RuntimeError("No header found in TSV.")

    rows = []
    for ln in lines[header_idx + 1:]:
        if not ln.strip():
            continue
        parts = ln.split("\t")
        if len(parts) < len(header):
            parts += [""] * (len(header) - len(parts))
        rows.append(dict(zip(header, parts)))
    return header, rows

def try_load_json(path):
    if not os.path.isfile(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def parse_int(x, default=None):
    try:
        return int(x)
    except:
        return default

def parse_float(x, default=None):
    try:
        return float(x)
    except:
        return default

def opp_color(c):
    return "G" if c == "R" else ("R" if c == "G" else "")

def make_key(cond, rotcfg, transdeg, delayed_color):
    # stable key for uniqueness check
    # headings are multiples of 45; store as int degrees
    h = int(round(transdeg)) % 360
    return f"{cond}|Rot{rotcfg}|H{h}|Del{delayed_color}"

def responded(row):
    return parse_int(row.get("RespIndex","-1"), -1) >= 0 and parse_float(row.get("RespDeg","-1"), -1) >= 0

def correct(row):
    td = parse_float(row.get("TransDeg","nan"), float("nan"))
    rd = parse_float(row.get("RespDeg","nan"), float("nan"))
    if math.isnan(td) or math.isnan(rd):
        return False
    return int(round(td)) % 360 == int(round(rd)) % 360

def translating_field_color(row):
    """
    Translation logic (matches your Unity spec):
      CUED   -> delayed field translates -> TranslatingColor = DelayedFieldColor
      UNCUED -> non-delayed translates   -> TranslatingColor = opposite(DelayedFieldColor)
    """
    cond = row.get("Cond","")
    d = row.get("DelayedFieldColor","")
    if cond == "CUED":
        return d
    elif cond == "UNCUED":
        return opp_color(d)
    return ""

def safe_mean(xs):
    xs = [x for x in xs if x is not None and not math.isnan(x)]
    return float(np.mean(xs)) if xs else float("nan")

def safe_std(xs):
    xs = [x for x in xs if x is not None and not math.isnan(x)]
    return float(np.std(xs)) if xs else float("nan")

# ---------- sidecar trajectory parsing ----------
def load_sidecar(sidecar_path):
    sj = try_load_json(sidecar_path)
    if sj is None:
        return None, None

    tl = sj.get("trajectory_library", {})
    entries = tl.get("entries", [])

    # map (mkHash,colorHash) -> entry
    lookup = {}
    for e in entries:
        mk = (e.get("mk_hash32") or "").upper()
        cc = (e.get("color_hash32") or "").upper()
        if mk and cc:
            lookup[(mk, cc)] = e
    return sj, lookup

def parse_payload(payload, kind="mk"):
    """
    payload: "1|1|2|2;1|1|2|2;..."
    returns array shape (nFrames, nSubfields)
      mk: float array
      color: object array of chars
    """
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

def plot_motion_trajectory(ax, mk_arr, title=""):
    """
    mk_arr: (nFrames, nSubfields) float codes
    """
    if mk_arr is None or mk_arr.size == 0:
        ax.set_title(title + " (no data)")
        ax.axis("off")
        return

    nF, nS = mk_arr.shape
    markers = ["o", "s", "^", "D"]  # S0..S3
    markevery = max(1, nF // 25)   # ~25 markers across trace

    for s in range(nS):
        ax.plot(np.arange(nF), mk_arr[:, s],
                label=f"S{s}",
                marker=markers[s % len(markers)],
                markevery=markevery,
                linewidth=1)

    ax.set_xlabel("frame")
    ax.set_ylabel("motion kind")
    ax.set_title(title)

    # MotionKind mapping
    ax.set_yticks([1,2,3,4])
    ax.set_yticklabels(["CW rot", "CCW rot", "Trans (coh)", "Trans (noise)"])
    ax.set_ylim(0.5, 4.5)

# ---------- main analysis ----------
def main():
    if len(sys.argv) < 2:
        print(USAGE)
        sys.exit(1)

    tsv_path = sys.argv[1]
    if not os.path.isfile(tsv_path):
        print("TSV not found:", tsv_path)
        sys.exit(1)

    base, _ = os.path.splitext(tsv_path)
    sidecar_path = tsv_path + ".sidecar.json"
    meta_path = tsv_path + ".meta.json"

    header, rows_raw = read_tsv(tsv_path)
    meta = try_load_json(meta_path)
    sidecar, traj_lookup = load_sidecar(sidecar_path)

    # De-duplicate by Trial index if needed (guards against accidental repeat lines)
    seen_trial = set()
    rows = []
    for r in rows_raw:
        ti = parse_int(r.get("Trial","-1"), -999999)
        if ti in seen_trial:
            continue
        seen_trial.add(ti)
        rows.append(r)

    # annotate rows with derived fields
    for r in rows:
        r["_responded"] = responded(r)
        r["_correct"] = correct(r) if r["_responded"] else False
        r["_TransFieldColor"] = translating_field_color(r)

    # ---- uniqueness ----
    keys = []
    for r in rows:
        cond = r.get("Cond","")
        rot = r.get("RotCfg","")
        rot_i = parse_int(rot, -1)
        td = parse_float(r.get("TransDeg","nan"), float("nan"))
        dcol = r.get("DelayedFieldColor","")
        keys.append(make_key(cond, rot_i, td if not math.isnan(td) else 0.0, dcol))

    key_counts = Counter(keys)
    dupes = {k:v for k,v in key_counts.items() if v > 1}

    # ---- sidecar hash cross-check ----
    matched = missing = nonzero = 0
    if traj_lookup is not None:
        for r in rows:
            mk = (r.get("MkHash32","") or "").upper()
            cc = (r.get("ColorHash32","") or "").upper()
            if not mk or not cc:
                continue
            if mk in ("0","00000000") or cc in ("0","00000000"):
                continue
            nonzero += 1
            if (mk, cc) in traj_lookup:
                matched += 1
            else:
                missing += 1

    # ---- summaries ----
    def summarize(subset_rows, label):
        resp_rows = [r for r in subset_rows if r["_responded"]]
        n = len(subset_rows)
        nr = len(resp_rows)
        cor = sum(1 for r in resp_rows if r["_correct"])
        acc = cor / nr if nr > 0 else float("nan")
        rts = [parse_int(r.get("RTf","-1"), -1) for r in resp_rows]
        rts = [rt for rt in rts if rt is not None and rt >= 0]
        return {
            "label": label,
            "n": n,
            "responded": nr,
            "correct": cor,
            "acc": acc,
            "meanRTf": safe_mean(rts),
            "stdRTf": safe_std(rts)
        }

    all_sum = summarize(rows, "ALL")

    cond_values = sorted(set(r.get("Cond","") for r in rows))
    by_cond = {c: summarize([r for r in rows if r.get("Cond","")==c], c) for c in cond_values}

    by_tfcol = {c: summarize([r for r in rows if r["_TransFieldColor"]==c], f"TransFieldColor={c}") for c in ["R","G"]}

    by_both = {}
    for cond in ["CUED","UNCUED"]:
        for tfc in ["R","G"]:
            ss = [r for r in rows if r.get("Cond","")==cond and r["_TransFieldColor"]==tfc]
            by_both[(cond,tfc)] = summarize(ss, f"{cond} TransFieldColor={tfc}")

    cont_delayed = Counter((r.get("Cond",""), r.get("DelayedFieldColor","")) for r in rows)
    cont_trans = Counter((r.get("Cond",""), r.get("_TransFieldColor","")) for r in rows)

    # ---- write summary files ----
    summary = {
        "files": {
            "tsv": os.path.abspath(tsv_path),
            "meta": os.path.abspath(meta_path) if meta else None,
            "sidecar": os.path.abspath(sidecar_path) if sidecar else None
        },
        "counts": {
            "n_trials_raw": len(rows_raw),
            "n_trials_used": len(rows),
            "unique_keys": len(key_counts),
            "duplicates_in_keyspace": dupes
        },
        "hash_crosscheck": {
            "have_sidecar": sidecar is not None,
            "traj_entries_count": (sidecar.get("trajectory_library",{}).get("count") if sidecar else None),
            "nonzero_hash_trials": nonzero,
            "matched": matched,
            "missing": missing
        },
        "summary": {
            "ALL": all_sum,
            "by_cond": by_cond,
            "by_trans_field_color": by_tfcol,
            "by_cond_x_trans_field_color": {f"{k[0]}_{k[1]}": v for k,v in by_both.items()},
            "contingency_cond_x_delayed_color": {f"{k[0]}_{k[1]}": v for k,v in cont_delayed.items()},
            "contingency_cond_x_translating_field_color": {f"{k[0]}_{k[1]}": v for k,v in cont_trans.items()}
        },
        "meta_file_contents": meta
    }

    txt_path = base + "_summary.txt"
    json_path = base + "_summary.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    def fmt_s(s):
        acc = s["acc"]
        acc_s = f"{acc:.3f}" if not math.isnan(acc) else "nan"
        mrt = s["meanRTf"]
        mrt_s = f"{mrt:.2f}" if not math.isnan(mrt) else "nan"
        return f'{s["label"]}: n={s["n"]} responded={s["responded"]} correct={s["correct"]} acc={acc_s} meanRTf={mrt_s}'

    lines = []
    lines.append(f"Loaded TSV: {os.path.basename(tsv_path)} trials_used={len(rows)} (raw_lines={len(rows_raw)})")
    lines.append(f"Loaded meta: {os.path.basename(meta_path) if meta else '(none)'}")
    lines.append(f"Loaded sidecar: {os.path.basename(sidecar_path) if sidecar else '(none)'} traj_entries={sidecar.get('trajectory_library',{}).get('count') if sidecar else None}")
    lines.append("")
    lines.append("Uniqueness check (Cond×RotCfg×TransDeg×DelayedFieldColor):")
    lines.append(f"  unique keys: {len(key_counts)}")
    lines.append(f"  duplicates (keyspace): {len(dupes)}")
    lines.append("")
    lines.append("Trajectory library cross-check (hash pairs):")
    lines.append(f"  trials w/ nonzero hashes: {nonzero}")
    lines.append(f"  matched: {matched}")
    lines.append(f"  missing: {missing}")
    lines.append("")
    lines.append("Performance:")
    lines.append("  " + fmt_s(all_sum))
    for k in sorted(by_cond.keys()):
        lines.append("  " + fmt_s(by_cond[k]))
    lines.append("")
    for k in ["R","G"]:
        lines.append("  " + fmt_s(by_tfcol[k]))
    lines.append("")
    for (cond,tfc), s in by_both.items():
        lines.append("  " + fmt_s(s))
    lines.append("")
    lines.append("Contingency Cond×DelayedFieldColor:")
    for k,v in sorted(cont_delayed.items()):
        lines.append(f"  {k[0]} Delayed={k[1]}: {v}")
    lines.append("Contingency Cond×TranslatingFieldColor:")
    for k,v in sorted(cont_trans.items()):
        lines.append(f"  {k[0]} TransField={k[1]}: {v}")

    with open(txt_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    # ---- plots ----
    plots_path = base + "_plots.png"
    traj_path = base + "_trajectory_examples.png"

    # Plot 1: accuracy bars
    labels = ["ALL","CUED","UNCUED","Trans=R","Trans=G","CUED+R","CUED+G","UNCUED+R","UNCUED+G"]
    accs = [
        all_sum["acc"],
        by_cond.get("CUED", {"acc": float("nan")})["acc"],
        by_cond.get("UNCUED", {"acc": float("nan")})["acc"],
        by_tfcol["R"]["acc"],
        by_tfcol["G"]["acc"],
        by_both[("CUED","R")]["acc"],
        by_both[("CUED","G")]["acc"],
        by_both[("UNCUED","R")]["acc"],
        by_both[("UNCUED","G")]["acc"],
    ]

    # Plot 2: RT distributions by TransFieldColor
    rts_R = [parse_int(r.get("RTf","-1"), -1) for r in rows if r["_responded"] and r["_TransFieldColor"]=="R"]
    rts_G = [parse_int(r.get("RTf","-1"), -1) for r in rows if r["_responded"] and r["_TransFieldColor"]=="G"]
    rts_R = [rt for rt in rts_R if rt is not None and rt >= 0]
    rts_G = [rt for rt in rts_G if rt is not None and rt >= 0]

    plt.figure(figsize=(12,7))
    ax1 = plt.subplot(2,1,1)
    ax1.bar(np.arange(len(labels)), accs)
    ax1.set_ylim(0,1)
    ax1.set_xticks(np.arange(len(labels)))
    ax1.set_xticklabels(labels, rotation=30, ha="right")
    ax1.set_ylabel("accuracy")
    ax1.set_title("Accuracy summaries")

    ax2 = plt.subplot(2,1,2)
    max_rt = max(rts_R + rts_G + [1])
    bins = np.arange(0, max_rt + 10, 5)
    ax2.hist(rts_R, bins=bins, alpha=0.6, label="TransFieldColor=R")
    ax2.hist(rts_G, bins=bins, alpha=0.6, label="TransFieldColor=G")
    ax2.set_xlabel("RT (frames)")
    ax2.set_ylabel("count")
    ax2.legend()
    ax2.set_title("RT distributions by translating field color")

    plt.tight_layout()
    plt.savefig(plots_path, dpi=200)
    plt.close()

    # ---- trajectory examples (from sidecar) ----
    if traj_lookup is not None and matched > 0:
        # pick a few representative unique hash pairs from this file
        seen_pairs = []
        for r in rows:
            mk = (r.get("MkHash32","") or "").upper()
            cc = (r.get("ColorHash32","") or "").upper()
            if not mk or not cc or mk in ("0","00000000") or cc in ("0","00000000"):
                continue
            if (mk,cc) in traj_lookup:
                if all(p[0]!=mk or p[1]!=cc for p in seen_pairs):
                    seen_pairs.append((mk,cc,r))
            if len(seen_pairs) >= 6:
                break

        n = len(seen_pairs)
        ncols = 2
        nrows = int(math.ceil(n/ncols))
        plt.figure(figsize=(14, 3.8*nrows))

        for i,(mk,cc,r) in enumerate(seen_pairs):
            e = traj_lookup[(mk,cc)]
            mk_payload = e.get("mk_payload","")
            mk_arr = parse_payload(mk_payload, "mk")

            try:
                h = int(round(float(r.get("TransDeg","0")))) % 360
            except:
                h = 0

            title = (
                f'{r.get("Cond","")} Rot{r.get("RotCfg","")} H{h} '
                f'Del{r.get("DelayedFieldColor","")}\n'
                f'mk={mk} col={cc}'
            )

            ax = plt.subplot(nrows, ncols, i+1)
            plot_motion_trajectory(ax, mk_arr, title=title)
            if i == 0:
                ax.legend(loc="upper right", fontsize=8)

        plt.tight_layout()
        plt.savefig(traj_path, dpi=200)
        plt.close()

    out_list = [txt_path, json_path, plots_path]
    if traj_lookup is not None and matched > 0:
        out_list.append(traj_path)

    print("Wrote:")
    for p in out_list:
        print(" ", p)

if __name__ == "__main__":
    main()