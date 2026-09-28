#!/usr/bin/env bash
# Bundles the heavier, less time-sensitive checks into one daily run:
# deploy drift (~40s, scp's public/ per property), TLS expiry (safety net,
# certbot already renews automatically), every-page-200 (~38s, wraps
# ops/live_token_check.sh), ops drift (added 2026-08-31, ~5s, one
# directory not per-property -- does canon's ops/ match the VPS's
# /root/ops/scripts/, the shared alerting layer this whole monitoring
# directory depends on), and rules drift (added 2026-09-02, ~2s, one file
# pair not per-property -- does ~/.claude/context/rules.md still match
# canon's METHODS/ARCHITECT_DISCIPLINE.md, and is the local canon checkout
# itself current with origin/main). Uptime is scheduled separately, far
# more frequently, since it's cheap (a handful of curls) and time-sensitive
# in a way these five aren't.
#
# EXIT SEMANTICS (added 2026-09-28). This parent used to invoke the five
# children and check none of their exit codes. Without `set -e` that means
# its status was simply the LAST child's -- rules_drift_check.sh's -- so any
# failure in the first four was reported as success. Measured, not assumed:
# with children 1 and 4 stubbed to exit 3 and 7, the previous version exited
# 0 and printed nothing. (In the all-five-fail case it happened to exit 1,
# inherited from the last child, which is luck rather than a signal, and it
# still named no child.) That stopped being hypothetical when the VPS
# address moved to runtime resolution (scripts/lib/vps_host.sh): _mon_lib.sh
# now does `resolve_vps_addr || exit 1`, so if $VPS_ADDR is unset AND
# ~/.claude/hooks/h04_wrong_ssh_host.sh is moved or renamed, every child
# exits 1 immediately and the whole sweep stops without alerting -- the
# children never get far enough to send anything. Now: every failed child is
# named on stderr (-> r2daily.err.log) and the parent exits 1, so launchd's
# `last exit code` for com.vongimbel.r2daily is a real signal.
#
# RUN ALL, THEN FAIL -- deliberately not `set -e`. `-e` would abort the
# sweep at the first non-zero child, so one broken check would hide the
# state of every check after it, which is the opposite of what a monitoring
# sweep is for. The children are independent of each other (each sources
# _mon_lib.sh itself and keeps its own state), so there is nothing to gain
# by stopping early. Exit codes are therefore checked explicitly below.
#
# SKIPPED IS NOT FAILED: each child's local-connectivity gate prints
# "SKIPPED" to stderr and then `exit 0` on purpose -- a run this Mac can't
# trust is not a run that failed. Because that path already exits 0 it is
# never counted here, which is the intended behaviour. Likewise a child that
# *finds* drift still exits 0: it has done its job and alerted. A non-zero
# child here means the check machinery itself broke.
set -uo pipefail
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

CHECKS=(
  deploy_drift_check.sh
  tls_expiry_check.sh
  page200_check.sh
  ops_drift_check.sh
  rules_drift_check.sh
)

failed=()
for check in "${CHECKS[@]}"; do
  # Run, then read $? on the next line. Never `if ! "$DIR/$check"; then rc=$?`
  # -- inside that branch $? is the status of the negation (always 0), not
  # the child's, which would report every failure as "exit 0".
  "$DIR/$check"
  rc=$?
  if [ "$rc" -ne 0 ]; then
    failed+=("$check (exit $rc)")
  fi
done

if [ "${#failed[@]}" -gt 0 ]; then
  # Name every one of them, not a count: "3 checks failed" in an err log is
  # nearly as useless as silence.
  echo "$(date -Iseconds) [daily_checks] FAILED -- ${#failed[@]} of ${#CHECKS[@]} check(s) exited non-zero:" >&2
  for f in "${failed[@]}"; do
    echo "$(date -Iseconds) [daily_checks]   FAILED: $f" >&2
  done
  exit 1
fi

exit 0
