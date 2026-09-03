#!/usr/bin/env bash
# rules_drift_check.sh — does ~/.claude/context/rules.md still match what
# canon's METHODS/ARCHITECT_DISCIPLINE.md currently says, and is the LOCAL
# canon checkout itself current with origin/main?
#
# Same defect class as ops_drift_check.sh and deploy_drift_check.sh (a
# generator/source-of-truth diverges from what's actually loaded/deployed,
# and the gap goes unnoticed) -- this is that same check for the rules
# pipeline: ~/.claude/hooks/h01_session_start.sh -> sync_rules_from_canon.sh
# -> ~/.claude/context/rules.md.
#
# Two independent things can go wrong and both are checked here:
#   1. This Mac's LOCAL canon clone is behind origin/main (someone edited
#      canon on GitHub or another machine and this clone never pulled it) --
#      sync_rules_from_canon.sh deliberately never git-pulls (a SessionStart
#      hook must not perform a network git op), so if the local checkout is
#      stale, every session silently loads stale rules from a checkout that
#      LOOKS local-correct but isn't the current source of truth.
#   2. rules.md's content has drifted from what the LOCAL canon checkout's
#      ARCHITECT_DISCIPLINE.md currently says -- i.e. the sync mechanism
#      itself is broken, stale-cached, or was bypassed (rules.md hand-edited,
#      sync script deleted/broken, h01 hook disabled, etc).
#
# Not per-property: this is a single shared file pair, not one per site, so
# there is one "prop" here, matching ops_drift_check.sh's shape. Reuses
# _mon_lib.sh's send_alert / handle_check_result machinery via a fixed
# property key so it routes through the SAME suppression/recovery state and
# the SAME VPS-side sender (send_alert.js -> DIRECTOR_ALERT_EMAIL) as every
# other check in this directory -- never a new alert channel.
set -uo pipefail
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$DIR/_mon_lib.sh"

if ! check_local_connectivity; then
  echo "$(date -Iseconds) [rules_drift_check] SKIPPED -- local connectivity check failed, cannot trust results this run" >&2
  exit 0
fi

CANON_DIR="$(cd "$DIR/../.." && pwd)"
CANON_FILE="$CANON_DIR/METHODS/ARCHITECT_DISCIPLINE.md"
RULES_FILE="$HOME/.claude/context/rules.md"
SYNC_SCRIPT="$HOME/.claude/hooks/sync_rules_from_canon.sh"
ALERT_PROP="denvercoloradoinsulation.com" # routing key only, matching
  # ops_drift_check.sh's convention -- this check is about the shared rules
  # pipeline, not any one property, but send_alert() requires a property key
  # to resolve a from-address/SendGrid config on the VPS side.

diffs=()

# --- 1. Is the local canon clone behind origin/main? -----------------------
if [ -d "$CANON_DIR/.git" ]; then
  (cd "$CANON_DIR" && git fetch origin main --quiet 2>/dev/null)
  BEHIND="$(cd "$CANON_DIR" && git rev-list --count HEAD..origin/main 2>/dev/null)"
  if [ -z "$BEHIND" ]; then
    diffs+=("could not determine local-canon-vs-origin/main status (git rev-list failed)")
  elif [ "$BEHIND" -gt 0 ]; then
    diffs+=("local canon checkout is $BEHIND commit(s) behind origin/main -- run 'git pull' in $CANON_DIR")
  fi
else
  diffs+=("$CANON_DIR is not a git checkout -- cannot verify it against origin/main")
fi

# --- 2. Does rules.md match what the local canon file currently says? ------
if [ ! -x "$SYNC_SCRIPT" ]; then
  diffs+=("$SYNC_SCRIPT missing or not executable -- rules.md sync mechanism is broken")
elif [ ! -f "$CANON_FILE" ]; then
  diffs+=("$CANON_FILE missing -- cannot verify rules.md against it")
elif [ ! -f "$RULES_FILE" ]; then
  diffs+=("$RULES_FILE does not exist -- no rules are being loaded into any session")
else
  # Independently re-derive the expected rules block straight from canon,
  # using the same header-boundary logic sync_rules_from_canon.sh uses, and
  # compare it to what's actually sitting in rules.md right now. This is
  # deliberately a SEPARATE re-implementation (not a call into the sync
  # script) so this check can catch the sync script itself being broken or
  # bypassed, not just canon having moved out from under a healthy sync.
  HEADER_LINE="$(grep -n '^# ARCHITECT_DISCIPLINE\.md$' "$CANON_FILE" | head -1 | cut -d: -f1)"
  if [ -z "$HEADER_LINE" ]; then
    diffs+=("could not find '# ARCHITECT_DISCIPLINE.md' header in $CANON_FILE -- canon structure changed unexpectedly")
  else
    RULES_END=$((HEADER_LINE - 2))
    EXPECTED_RULES_BLOCK="$(sed -n "1,${RULES_END}p" "$CANON_FILE")"
    # Highest-numbered "RULE N" header in the canon file -- derived, never
    # hardcoded, so adding a Rule 12 to canon can never leave this check
    # silently testing for a stale count.
    LAST_RULE="$(grep -oE '^RULE [0-9]+' "$CANON_FILE" | awk '{print $2}' | sort -n | tail -1)"
    if [ -z "$LAST_RULE" ]; then
      diffs+=("could not find any '^RULE N' header in $CANON_FILE -- canon structure changed unexpectedly")
    fi
    if ! grep -qF -- "$EXPECTED_RULES_BLOCK" "$RULES_FILE"; then
      diffs+=("rules.md does not contain canon's current Rules 1-${LAST_RULE:-?} text verbatim -- sync is stale or was bypassed")
    fi
    if [ -n "$LAST_RULE" ] && ! grep -q "^RULE ${LAST_RULE} " "$RULES_FILE"; then
      diffs+=("rules.md is missing RULE ${LAST_RULE} (canon's newest rule)")
    fi
  fi
fi

if [ "${#diffs[@]}" -gt 0 ]; then
  handle_check_result "rules_drift" "$ALERT_PROP" 1 \
    "Rules pipeline drift: rules.md does not match canon" \
    "The canon-to-rules.md sync has drifted: ${diffs[*]}. This means SessionStart hooks may be injecting stale or incomplete rules into every Claude Code session. Check $CANON_DIR (git status/git pull) and re-run $SYNC_SCRIPT by hand, then re-run this check." \
    "" ""
else
  handle_check_result "rules_drift" "$ALERT_PROP" 0 "" "" \
    "Rules pipeline drift: resolved" \
    "$RULES_FILE now matches canon's current ARCHITECT_DISCIPLINE.md again, and the local canon checkout is current with origin/main."
fi
