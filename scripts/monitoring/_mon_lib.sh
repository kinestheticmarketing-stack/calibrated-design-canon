#!/usr/bin/env bash
# Shared config + helpers for R2's monitoring checks (deploy drift, uptime,
# TLS expiry, every-page-200). Assumed alert interface, pending R4's actual
# implementation: a script /root/ops/scripts/send_alert.sh on the VPS,
# invoked as:
#   send_alert.sh <property_key> "<subject>" "<body>"
# R2 stubs this locally (STUB_SEND_ALERT below) only so these checks are
# testable end-to-end before R4 lands the real one. R4 should replace the
# stub with the real sender; R2's checks don't need to change to pick it up
# — they just SSH-invoke the same path/interface either way.

set -uo pipefail

VPS_HOST="root@74.208.181.10"
STATE_DIR="${HOME}/.claude/hooks/monitoring-state"
mkdir -p "$STATE_DIR"

# property_key | live_homepage_url | local_repo_path | live_backend_dir
# (pipe-delimited deliberately -- the URL field itself contains colons, which
# broke an earlier colon-delimited version of this file: cut -d: on a field
# containing "https://..." silently split the URL apart too.)
PROPERTIES=(
  "dci|https://denvercoloradoinsulation.com|/Users/vongimbel/code/denvercoloradoinsulation.com|/root/denvercoloradoinsulation.com"
  "lgm|https://longmontcoloradoinsulation.com|/Users/vongimbel/code/longmontcoloradoinsulation.com|/root/longmontcoloradoinsulation.com"
  "gci|https://greeleycoloradoinsulation.com|/Users/vongimbel/code/greeleycoloradoinsulation.com|/root/greeleycoloradoinsulation.com"
)

prop_field() {
  # prop_field "<propline>" <index 1-4>
  echo "$1" | cut -d'|' -f"$2"
}

# --- Suppression: one alert per failure-key per day, then a recovery notice
# on the next healthy run after a failure was recorded. State file per
# check+property, holding the date of the last alert sent (empty = healthy).
check_state_path() {
  local check="$1" prop="$2"
  echo "${STATE_DIR}/${check}.${prop}.state"
}

# Returns 0 (true) if we should send a NEW failure alert right now.
should_alert_failure() {
  local check="$1" prop="$2"
  local f; f=$(check_state_path "$check" "$prop")
  local today; today=$(date +%F)
  if [ -f "$f" ] && [ "$(cat "$f" 2>/dev/null)" = "$today" ]; then
    return 1 # already alerted today for this failure
  fi
  return 0
}

record_failure_alert() {
  local check="$1" prop="$2"
  date +%F > "$(check_state_path "$check" "$prop")"
}

# Returns 0 (true) if a recovery notice should fire (state file exists,
# meaning we'd previously alerted a failure that hasn't been cleared yet).
should_alert_recovery() {
  local check="$1" prop="$2"
  [ -f "$(check_state_path "$check" "$prop")" ]
}

clear_failure_state() {
  local check="$1" prop="$2"
  rm -f "$(check_state_path "$check" "$prop")"
}

send_alert() {
  # send_alert <property_key> <subject> <body>
  local prop="$1" subject="$2" body="$3"
  ssh "$VPS_HOST" "/root/ops/scripts/send_alert.sh '$prop' '$subject' '$body'" 2>&1
}
