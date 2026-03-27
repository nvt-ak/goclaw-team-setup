#!/usr/bin/env bash
set -euo pipefail

# Auto-apply an existing Team Setup OS case as a new case
# and run built-in regenerate + verify scripts.
#
# Usage:
#   bash team-setup-os/scripts/apply-team-template.sh <source_case> <new_case> [team_name]
# Example:
#   bash team-setup-os/scripts/apply-team-template.sh vinaco-it-v1 vinaco-content-v1 vinaco-content-team

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CASES_DIR="$ROOT/cases"

if [[ $# -lt 2 ]]; then
  echo "Usage: $0 <source_case> <new_case> [team_name]"
  exit 1
fi

SRC_CASE="$1"
NEW_CASE="$2"
TEAM_NAME="${3:-}"

SRC_PATH="$CASES_DIR/$SRC_CASE"
DST_PATH="$CASES_DIR/$NEW_CASE"

if [[ ! -d "$SRC_PATH" ]]; then
  echo "ERROR: source case not found: $SRC_PATH"
  exit 1
fi

if [[ -e "$DST_PATH" ]]; then
  echo "ERROR: destination case already exists: $DST_PATH"
  exit 1
fi

echo "[1/5] Copy template case: $SRC_CASE -> $NEW_CASE"
cp -R "$SRC_PATH" "$DST_PATH"

# Clean old verify artifacts to avoid confusion
echo "[2/5] Clean stale verify artifacts"
rm -f "$DST_PATH/docs/VERIFY_TEAM_PACK_REPORT.txt" \
      "$DST_PATH/docs/DIFF_REPORT.md" \
      "$DST_PATH/verify-"*.md \
      "$DST_PATH/verify-"*.json 2>/dev/null || true

# Optional team_name patch in config/team.yaml
if [[ -n "$TEAM_NAME" && -f "$DST_PATH/config/team.yaml" ]]; then
  echo "[3/5] Patch config/team.yaml team_name=$TEAM_NAME"
  python3 - "$DST_PATH/config/team.yaml" "$TEAM_NAME" <<'PY'
import re,sys
p=sys.argv[1]
team_name=sys.argv[2]
s=open(p,'r',encoding='utf-8').read()
if re.search(r'^team_name:\s*', s, flags=re.M):
    s=re.sub(r'^team_name:\s*.*$', f'team_name: {team_name}', s, flags=re.M)
else:
    s=f'team_name: {team_name}\n'+s
open(p,'w',encoding='utf-8').write(s)
print('patched team_name')
PY
else
  echo "[3/5] Skip team_name patch (no team_name provided or config missing)"
fi

# Regenerate per-role settings if tool exists
if [[ -f "$DST_PATH/tools/regenerate_role_settings_v10.py" ]]; then
  echo "[4/5] Run regenerate_role_settings_v10.py"
  python3 "$DST_PATH/tools/regenerate_role_settings_v10.py"
else
  echo "[4/5] Skip regenerate (tool not found)"
fi

# Run verifier if tool exists
if [[ -f "$DST_PATH/scripts/verify-team-pack.py" ]]; then
  echo "[5/5] Run verify-team-pack.py"
  mkdir -p "$DST_PATH/docs"
  python3 "$DST_PATH/scripts/verify-team-pack.py" | tee "$DST_PATH/docs/VERIFY_TEAM_PACK_REPORT.txt"
else
  echo "[5/5] Skip verify (script not found)"
fi

echo

echo "DONE: $DST_PATH"
echo "Next: import/sync this generated case into GoClaw UI (per-agent settings)."
