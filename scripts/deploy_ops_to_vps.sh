#!/usr/bin/env bash
# scripts/deploy_ops_to_vps.sh — deploys canon's ops/ (the VPS alerting
# layer, imported 2026-08-31 from /root/ops/scripts/) to the VPS.
#
# This is the ONLY sanctioned path from a canon commit to a live change on
# the VPS. Editing /root/ops/scripts/*.js or *.sh directly on the VPS is
# what put this code out of version control in the first place -- do that
# again and ops_drift_check.sh will catch it and alert, but the point of
# this script is to make that unnecessary.
#
# Per-file, not a directory sync: intentionally does NOT rsync/scp the
# whole directory wholesale, so a stray file that only exists on the VPS
# (e.g. someone's ad-hoc debug script) is never silently deleted by a
# deploy, and a stray file that only exists in canon's ops/ is never
# silently pushed without this list naming it first.
set -euo pipefail

VPS_HOST="root@74.208.181.10"
VPS_DIR="/root/ops/scripts"
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOCAL_DIR="$DIR/ops"

FILES=(
  send_alert.js
  send_alert.sh
  test_send_alert.js
  stale_site_check.js
  unhandled_lead_check.js
  backup_heartbeat_check.sh
  db_backup.sh
)

DATE_TAG="$(date +%Y-%m-%d)"
CHANGED=()
UNCHANGED=()

for f in "${FILES[@]}"; do
  local_path="$LOCAL_DIR/$f"
  if [ ! -f "$local_path" ]; then
    echo "ERROR: $local_path does not exist locally -- refusing to deploy an incomplete file list." >&2
    exit 1
  fi

  local_md5="$(md5 -q "$local_path" 2>/dev/null || md5sum "$local_path" | awk '{print $1}')"
  remote_md5="$(ssh "$VPS_HOST" "md5sum ${VPS_DIR}/${f} 2>/dev/null" | awk '{print $1}' || true)"

  if [ "$local_md5" = "$remote_md5" ]; then
    UNCHANGED+=("$f")
    continue
  fi

  # Back up the VPS copy before overwriting, matching this portfolio's
  # established .bak-<reason>-<date> convention -- never overwrite live
  # ops code without a way back.
  if [ -n "$remote_md5" ]; then
    ssh "$VPS_HOST" "cp ${VPS_DIR}/${f} ${VPS_DIR}/${f}.bak-pre-canon-deploy-${DATE_TAG}"
  fi

  scp -q "$local_path" "${VPS_HOST}:${VPS_DIR}/${f}"

  # Preserve the executable bit canon tracks, since scp alone does not
  # reliably carry git's file mode across every environment.
  if [ -x "$local_path" ]; then
    ssh "$VPS_HOST" "chmod 755 ${VPS_DIR}/${f}"
  fi

  new_remote_md5="$(ssh "$VPS_HOST" "md5sum ${VPS_DIR}/${f}" | awk '{print $1}')"
  if [ "$new_remote_md5" != "$local_md5" ]; then
    echo "ERROR: post-deploy md5 mismatch for $f (local=$local_md5, vps=$new_remote_md5) -- deploy did not land cleanly." >&2
    exit 1
  fi

  CHANGED+=("$f")
done

echo "Deployed: ${CHANGED[*]:-(none)}"
echo "Already in sync: ${UNCHANGED[*]:-(none)}"

if [ "${#CHANGED[@]}" -eq 0 ]; then
  echo "Nothing to deploy -- VPS already matches canon."
fi
