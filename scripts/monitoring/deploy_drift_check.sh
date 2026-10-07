#!/usr/bin/env bash
# 2a. Deploy drift: compares live index.js and public/ against the local
# repo (which R2 must run from, since only the Mac has the git checkouts).
# Real file comparison via scp+cmp — never $(curl ...), which strips
# trailing newlines and produced a false mismatch in an earlier incident.
set -uo pipefail
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$DIR/_mon_lib.sh"

if ! check_local_connectivity; then
  echo "$(date -Iseconds) [deploy_drift_check] SKIPPED -- local connectivity check failed, cannot trust results this run" >&2
  exit 0
fi

# --- Failed-copy handling (added 2026-10-07). A copy that fails is not a
# missing site, and it is not "no problem" either. Previously a failed scp
# of public/ left public_live/ empty, so every repo file was reported
# "(missing live)" and a transient ssh/scp failure alerted as deploy drift.
# Now a copy that exits non-zero or brings back zero files adds nothing to
# the drift list, logs one SKIPPED line, and bumps a per-property skip
# counter in STATE_DIR. A run where every copy succeeds resets it to 0.
# UNREACHABLE_THRESHOLD consecutive skipped runs raise a distinct
# "UNREACHABLE" alert through send_alert -- never a drift alert.
UNREACHABLE_THRESHOLD=3

skip_count_path() {
  local prop="$1"
  echo "${STATE_DIR}/deploy_drift.${prop}.skips"
}

log_skip() {
  local prop="$1" what="$2"
  echo "$(date -Iseconds) [deploy_drift_check] SKIPPED $prop -- could not copy live $what" >&2
}

for propline in "${PROPERTIES[@]}"; do
  prop=$(prop_field "$propline" 1)
  repo=$(prop_field "$propline" 3)
  backend=$(prop_field "$propline" 4)
  tmp=$(mktemp -d)
  diffs=()
  skipped=0

  # index.js
  scp -q "${VPS_HOST}:${backend}/index.js" "$tmp/index.js.live" 2>/dev/null
  rc=$?
  if [ "$rc" -ne 0 ] || [ ! -f "$tmp/index.js.live" ]; then
    log_skip "$prop" "index.js"
    skipped=1
  elif ! cmp -s "$tmp/index.js.live" "$repo/index.js"; then
    diffs+=("index.js")
  fi

  # package.json — the other file ops/push-backend.sh ships (added
  # 2026-09-02 alongside push-backend.sh itself, closing the same silent-
  # miss gap index.js had: a dependency-manifest edit committed to the repo
  # but never deployed is invisible without this). node_modules/ itself is
  # deliberately NOT compared here — it's never shipped by push-backend.sh
  # (installing packages is a separate, deliberate, manual step; see
  # TOOLING_RUNBOOK.md), so comparing it would just alert on an expected,
  # permanent difference (a dev machine plus a VPS never carry identical
  # node_modules/ trees) rather than a real drift.
  scp -q "${VPS_HOST}:${backend}/package.json" "$tmp/package.json.live" 2>/dev/null
  rc=$?
  if [ "$rc" -ne 0 ] || [ ! -f "$tmp/package.json.live" ]; then
    log_skip "$prop" "package.json"
    skipped=1
  elif ! cmp -s "$tmp/package.json.live" "$repo/package.json"; then
    diffs+=("package.json")
  fi

  # public/ — compare every file that exists in the repo's public dir
  mkdir -p "$tmp/public_live"
  scp -rq "${VPS_HOST}:${backend}/public/." "$tmp/public_live/" 2>/dev/null
  rc=$?
  if [ "$rc" -ne 0 ] || [ -z "$(find "$tmp/public_live" -type f -print -quit)" ]; then
    log_skip "$prop" "public/"
    skipped=1
  else
    while IFS= read -r -d '' f; do
      rel="${f#"$repo"/public/}"
      if [ ! -f "$tmp/public_live/$rel" ]; then
        diffs+=("public/$rel (missing live)")
      elif ! cmp -s "$f" "$tmp/public_live/$rel"; then
        diffs+=("public/$rel")
      fi
    done < <(find "$repo/public" -type f -print0)
  fi

  rm -rf "$tmp"

  skipfile=$(skip_count_path "$prop")
  if [ "$skipped" -eq 1 ]; then
    skips=0
    if [ -f "$skipfile" ]; then
      skips=$(cat "$skipfile" 2>/dev/null)
      [[ "$skips" =~ ^[0-9]+$ ]] || skips=0
    fi
    skips=$((skips + 1))
    echo "$skips" > "$skipfile"
    # Same once-per-day suppression as every other failure alert, under its
    # own check key so it never shares state with deploy_drift.
    if [ "$skips" -ge "$UNREACHABLE_THRESHOLD" ] && should_alert_failure "deploy_unreachable" "$prop"; then
      if send_alert "$prop" "UNREACHABLE" \
        "deploy_drift_check could not copy live files from the VPS for $prop on $skips consecutive runs, so deploy drift for $prop is currently unchecked. This is a copy (ssh/scp) failure, not drift."; then
        record_failure_alert "deploy_unreachable" "$prop"
      fi
    fi
  else
    echo 0 > "$skipfile"
    clear_failure_state "deploy_unreachable" "$prop"
  fi

  if [ "${#diffs[@]}" -gt 0 ]; then
    handle_check_result "deploy_drift" "$prop" 1 \
      "Deploy drift on $prop: live does not match repo" \
      "The following file(s) differ between what's deployed and what's in the repo for $prop: ${diffs[*]}. This usually means a commit was made but never deployed — the live site is running older or different code than what's checked in." \
      "" ""
  elif [ "$skipped" -eq 0 ]; then
    # Only a run that actually compared everything may report "no drift".
    # A run with a skipped copy and no diffs leaves drift state untouched.
    handle_check_result "deploy_drift" "$prop" 0 "" "" \
      "Deploy drift on $prop: resolved" \
      "Live now matches the repo again for $prop."
  fi
done
