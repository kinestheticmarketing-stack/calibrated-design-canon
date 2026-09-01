#!/usr/bin/env bash
# ops_drift_check.sh — does the VPS's /root/ops/scripts/ match canon's ops/?
# Same defect class deploy_drift_check.sh already guards against for each
# property's index.js/public/ (the five-day-undeployed-notifier shape: a
# commit lands in canon but nothing ever pushes it live, and the gap goes
# unnoticed) -- this is that same check, one directory over, for the shared
# alerting layer instead of a site.
#
# Not per-property: this is a single shared directory, not one per site, so
# there is one "prop" here, not three. Reuses _mon_lib.sh's send_alert /
# should_alert_failure / should_alert_recovery machinery via a fixed
# property key so it routes through the same suppression/recovery state and
# the same VPS-side sender as every other check in this directory.
set -uo pipefail
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$DIR/_mon_lib.sh"

if ! check_local_connectivity; then
  echo "$(date -Iseconds) [ops_drift_check] SKIPPED -- local connectivity check failed, cannot trust results this run" >&2
  exit 0
fi

CANON_OPS_DIR="$(cd "$DIR/../../ops" && pwd)"
VPS_OPS_DIR="/root/ops/scripts"
ALERT_PROP="denvercoloradoinsulation.com" # routing key only -- this check is
  # about the shared ops layer, not any one property, but send_alert()
  # requires a property key to resolve a from-address/SendGrid config on the
  # VPS side. Picked arbitrarily (first in PROPERTIES); the alert body names
  # the file(s), not a property.

FILES=(
  send_alert.js
  send_alert.sh
  test_send_alert.js
  stale_site_check.js
  unhandled_lead_check.js
  backup_heartbeat_check.sh
  db_backup.sh
)

diffs=()
for f in "${FILES[@]}"; do
  local_path="$CANON_OPS_DIR/$f"
  if [ ! -f "$local_path" ]; then
    diffs+=("$f (missing from canon ops/)")
    continue
  fi
  remote_md5="$(ssh root@74.208.181.10 "md5sum ${VPS_OPS_DIR}/${f} 2>/dev/null" | awk '{print $1}')"
  if [ -z "$remote_md5" ]; then
    diffs+=("$f (could not read live copy)")
    continue
  fi
  local_md5="$(md5 -q "$local_path" 2>/dev/null || md5sum "$local_path" | awk '{print $1}')"
  if [ "$local_md5" != "$remote_md5" ]; then
    diffs+=("$f")
  fi
done

if [ "${#diffs[@]}" -gt 0 ]; then
  handle_check_result "ops_drift" "$ALERT_PROP" 1 \
    "Ops layer drift: VPS does not match canon" \
    "The following file(s) in /root/ops/scripts/ on the VPS differ from canon's ops/: ${diffs[*]}. This usually means a live edit was made directly on the VPS and never brought back into canon, or a canon change was never deployed with scripts/deploy_ops_to_vps.sh. Run that script from canon to reconcile, after checking which side is correct." \
    "" ""
else
  handle_check_result "ops_drift" "$ALERT_PROP" 0 "" "" \
    "Ops layer drift: resolved" \
    "The VPS's /root/ops/scripts/ now matches canon's ops/ again."
fi
