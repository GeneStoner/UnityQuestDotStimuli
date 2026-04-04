#!/usr/bin/env bash
# vrdots_pull.sh — ADB pull Quest data + auto-update session registry
#
# Usage:
#   bash Tools/Analysis/vrdots_pull.sh
#
# From anywhere, use the absolute path:
#   bash ~/Projects/ObjectBasedAttention/VRDots/Tools/Analysis/vrdots_pull.sh

set -euo pipefail

QUEST_PATH="/sdcard/Android/data/com.genestoner.vrdptsrebuildX.test/files/"
LOCAL_PATH="$HOME/Library/Application Support/ThatsRandom/VRDotsDataFiles/"
REGISTRY_SCRIPT="$HOME/Projects/ObjectBasedAttention/VRDots/Tools/Analysis/update_registry.py"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  VRDots ADB Pull + Registry Update"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# ── Check ADB device ──────────────────────────────────────────────────────────
echo ""
echo "Checking ADB device..."
if ! adb devices | grep -q "device$"; then
    echo ""
    echo "  ✗ No ADB device found."
    echo "    Make sure Quest is connected and Developer Mode is enabled."
    echo "    (Toggle Developer Mode off/on in Meta Horizon app if unauthorized)"
    echo ""
    echo "  Skipping pull. Running registry update on existing files only."
    echo ""
else
    DEVICE=$(adb devices | grep "device$" | head -1 | awk '{print $1}')
    echo "  ✓ Device: $DEVICE"
    echo ""
    echo "Pulling data from Quest..."
    adb pull "$QUEST_PATH" "$LOCAL_PATH"
    echo ""
    echo "  ✓ Pull complete."
fi

# ── Update registry ───────────────────────────────────────────────────────────
echo ""
echo "Updating session registry..."
python3 "$REGISTRY_SCRIPT"

# ── Show NEW sessions that need manual annotation ─────────────────────────────
echo ""
python3 - <<'PYEOF'
import csv, os

REGISTRY = os.path.expanduser(
    "~/Projects/ObjectBasedAttention/VRDots/Tools/Analysis/sessions_registry.csv")

with open(REGISTRY, newline='', encoding='utf-8') as f:
    rows = list(csv.DictReader(f))

new_rows = [r for r in rows if r['Status'] == 'NEW']

if new_rows:
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"  ⚠️  ACTION REQUIRED: {len(new_rows)} new session(s) need annotation")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print()
    print(f"  {'SessionID':<18} {'Experiment':<22} {'N':>5} {'SwapTypes':<14} {'Colors'}")
    print(f"  {'─'*18} {'─'*22} {'─'*5} {'─'*14} {'─'*6}")
    for r in new_rows:
        print(f"  {r['SessionID']:<18} {r['Experiment']:<22} {r['N_trials']:>5} {r['SwapTypes']:<14} {r['DelayedFieldColors']}")
    print()
    print("  Fill in EyeCondition, DepthSep_m, Status, Notes, WriteUps:")
    print("  open ~/Projects/ObjectBasedAttention/VRDots/Tools/Analysis/sessions_registry.csv")
    print()
else:
    print("  ✓ No new sessions — registry is up to date.")

# Also flag Active sessions with no WriteUps entry
missing_writeup = [r for r in rows
                   if r['Status'] == 'Active' and not r['WriteUps'].strip()]
if missing_writeup:
    print()
    print(f"  ⚠️  {len(missing_writeup)} Active session(s) have no WriteUp assigned:")
    for r in missing_writeup:
        print(f"    {r['SessionID']}  {r['Experiment']}")
PYEOF

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Done."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
