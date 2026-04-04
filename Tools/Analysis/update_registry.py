#!/usr/bin/env python3
"""
update_registry.py — VRDots session registry maintenance tool.

Run after every ADB pull:
    python3 Tools/Analysis/update_registry.py

Auto-fills from TSV data:
    SessionID, Date, Experiment, N_trials, SwapTypes, DelayedFieldColors

Preserves manual fields already in the registry:
    EyeCondition, DepthSep_m, Status, Notes, WriteUps

New sessions are appended with empty manual fields (Status=NEW).
Sessions already in the registry are updated for auto fields only.

Output: Tools/Analysis/sessions_registry.csv  (overwrites in place)
"""

import os, csv, glob

# ── Paths ─────────────────────────────────────────────────────────────────────
DATA_DIR   = os.path.expanduser(
    "~/Library/Application Support/ThatsRandom/VRDotsDataFiles")
REGISTRY   = os.path.join(
    os.path.dirname(__file__), "sessions_registry.csv")

# All TSV files in DATA_DIR and one level deep (handles ADB-pull nested dirs).
def find_tsvs(data_dir):
    seen, paths = set(), []
    for root, dirs, files in os.walk(data_dir):
        depth = root.replace(data_dir, '').count(os.sep)
        if depth > 1:
            dirs[:] = []  # prune deeper traversal
            continue
        for f in sorted(files):
            if f.endswith('.tsv') and not f.endswith('.meta.json'):
                sid = f.replace('vr_dots_session_', '').replace('.tsv', '')
                if sid not in seen:
                    seen.add(sid)
                    paths.append(os.path.join(root, f))
    return sorted(paths)


def parse_tsv(path):
    """Return (experiment, n_trials, swap_types_str, delayed_field_colors_str)."""
    experiment = ''
    swap_set   = set()
    color_set  = set()
    n          = 0
    try:
        with open(path, encoding='utf-8', errors='replace') as f:
            header = None
            for line in f:
                line = line.rstrip('\n')
                if line.startswith('#') or not line.strip():
                    continue
                cols = line.split('\t')
                if header is None:
                    header = {c: i for i, c in enumerate(cols)}
                    continue
                n += 1
                if 'Experiment' in header:
                    experiment = cols[header['Experiment']].strip() or experiment
                if 'SwapType' in header:
                    swap_set.add(cols[header['SwapType']].strip())
                if 'DelayedFieldColor' in header:
                    color_set.add(cols[header['DelayedFieldColor']].strip())
    except Exception as e:
        pass
    swap_str  = '/'.join(sorted(s for s in swap_set  if s)) or ''
    color_str = '/'.join(sorted(c for c in color_set if c)) or ''
    return experiment, n, swap_str, color_str


COLUMNS = [
    'SessionID',
    'Date',
    'Experiment',
    'N_trials',
    'SwapTypes',
    'DelayedFieldColors',
    'DepthSep_m',
    'EyeCondition',
    'Status',
    'Notes',
    'WriteUps',
]

MANUAL_COLS = {'DepthSep_m', 'EyeCondition', 'Status', 'Notes', 'WriteUps'}


def load_registry(path):
    """Return dict[SessionID -> row_dict]. Returns {} if file absent."""
    if not os.path.exists(path):
        return {}
    rows = {}
    with open(path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows[row['SessionID']] = dict(row)
    return rows


def sid_to_date(sid):
    """260323_1534 → 2026-03-23  (handles both YY and YYYYMMDD formats)."""
    part = sid.split('_')[0]
    if len(part) == 6:   # YYMMDD
        return f"20{part[:2]}-{part[2:4]}-{part[4:]}"
    elif len(part) == 8: # YYYYMMDD
        return f"{part[:4]}-{part[4:6]}-{part[6:]}"
    return part


def main():
    existing = load_registry(REGISTRY)
    tsv_paths = find_tsvs(DATA_DIR)

    updated = {}
    new_sids = []

    for path in tsv_paths:
        fname = os.path.basename(path)
        sid = fname.replace('vr_dots_session_', '').replace('.tsv', '')
        experiment, n, swap_str, color_str = parse_tsv(path)

        if sid in existing:
            row = dict(existing[sid])  # start from existing (preserves manual)
        else:
            row = {c: '' for c in COLUMNS}
            row['Status'] = 'NEW'
            new_sids.append(sid)

        # Overwrite auto fields
        row['SessionID']          = sid
        row['Date']               = sid_to_date(sid)
        row['Experiment']         = experiment or row.get('Experiment','')
        row['N_trials']           = str(n)
        row['SwapTypes']          = swap_str  or row.get('SwapTypes','')
        row['DelayedFieldColors'] = color_str or row.get('DelayedFieldColors','')

        updated[sid] = row

    # Preserve any registry rows not on disk (shouldn't happen, but be safe)
    for sid, row in existing.items():
        if sid not in updated:
            updated[sid] = row

    # Sort by SessionID
    sorted_rows = sorted(updated.values(), key=lambda r: r['SessionID'])

    with open(REGISTRY, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=COLUMNS)
        writer.writeheader()
        for row in sorted_rows:
            writer.writerow({c: row.get(c,'') for c in COLUMNS})

    print(f"Registry updated: {len(sorted_rows)} sessions total.")
    if new_sids:
        print(f"  New sessions added ({len(new_sids)}): {', '.join(new_sids)}")
    else:
        print("  No new sessions.")
    print(f"  Saved: {REGISTRY}")


if __name__ == '__main__':
    main()
