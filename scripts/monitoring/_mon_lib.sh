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

# launchd LaunchAgents run with a bare PATH (/usr/bin:/bin:/usr/sbin:/sbin --
# confirmed via `launchctl print gui/$(id -u)/com.vongimbel.r2daily`), which
# does not include Homebrew's /opt/homebrew/bin. GNU `timeout` (used by
# tls_expiry_check.sh to bound the openssl s_client handshake) only exists
# there -- under the bare launchd PATH it's "command not found" (exit 127),
# the openssl pipeline never runs, enddate comes back empty, and the check
# alerts a false "could not read certificate" even though the cert is fine.
# Reproduced directly: `env -i PATH=/usr/bin:/bin:/usr/sbin:/sbin bash -c
# "timeout 5 echo hi"` -> "timeout: command not found". Prepending Homebrew's
# bin dirs here (sourced by every check) fixes this for all of them.
export PATH="/opt/homebrew/bin:/usr/local/bin:${PATH}"

VPS_HOST="root@74.208.181.10"
STATE_DIR="${HOME}/.claude/hooks/monitoring-state"
mkdir -p "$STATE_DIR"

# property_key | live_homepage_url | local_repo_path | live_backend_dir
# (pipe-delimited deliberately -- the URL field itself contains colons, which
# broke an earlier colon-delimited version of this file: cut -d: on a field
# containing "https://..." silently split the URL apart too.)
#
# property_key is the FULL domain label (matching what stale_site_check.js /
# unhandled_lead_check.js already pass on the VPS), not a short code. VPS-side
# send_alert.js resolves the mail-sending property config via
# `property.includes(k)` against keys like "denvercoloradoinsulation" -- a
# short key like "dci" never matches any of them, so every alert from these
# checks was silently falling through to send_alert.js's DCI default
# (propDirs.denvercoloradoinsulation), meaning a GCI or LGM failure would
# alert using DCI's SendGrid `from` address/env. The full label makes the
# substring match succeed and routes to the right property.
PROPERTIES=(
  "denvercoloradoinsulation.com|https://denvercoloradoinsulation.com|/Users/vongimbel/code/denvercoloradoinsulation.com|/root/denvercoloradoinsulation.com"
  "longmontcoloradoinsulation.com|https://longmontcoloradoinsulation.com|/Users/vongimbel/code/longmontcoloradoinsulation.com|/root/longmontcoloradoinsulation.com"
  "greeleycoloradoinsulation.com|https://greeleycoloradoinsulation.com|/Users/vongimbel/code/greeleycoloradoinsulation.com|/root/greeleycoloradoinsulation.com"
)

prop_field() {
  # prop_field "<propline>" <index 1-4>
  echo "$1" | cut -d'|' -f"$2"
}

# --- Local-connectivity gate. 2026-08-31: a single curl/ssh failure from
# this Mac used to be trusted as a real site-side signal, so a Wi-Fi drop,
# sleep/wake, or VPN toggle produced a real "down" email and a real
# "recovered" email for sites that were never actually down (all three
# properties fired the same day from one shared blip -- see
# TOOLING_RUNBOOK.md). Every check must call this ONCE per run, before
# touching any per-property failure state, and skip the whole run (no
# alerts, no state writes) if it fails -- a result gathered while this
# Mac itself can't reach the internet cannot be trusted either way.
# Two independent probes, both against a stable endpoint that is never
# one of the monitored properties: a raw-IP HTTPS reach (Cloudflare's
# 1.1.1.1, sidesteps DNS so a DNS-only outage doesn't get missed by using
# an IP that still resolves through some other path) and a normal
# domain fetch (exercises DNS resolution specifically, so a DNS-only
# outage -- routing fine, resolver dead -- still fails this gate even
# though the raw-IP probe alone would pass).
check_local_connectivity() {
  curl -s -o /dev/null --max-time 5 "https://1.1.1.1/cdn-cgi/trace" \
    && curl -s -o /dev/null --max-time 5 "https://cloudflare.com"
}

# --- Suppression: one alert per failure-key per day, then a recovery notice
# on the next healthy run after a failure was recorded. State file per
# check+property, holding the date of the last alert sent (empty = healthy).
check_state_path() {
  local check="$1" prop="$2"
  echo "${STATE_DIR}/${check}.${prop}.state"
}

# --- Consecutive-failure counter, separate from the alert-suppression
# state above. A failure only reaches should_alert_failure's gate once it
# has happened CONSECUTIVE_FAILURE_THRESHOLD times in a row, each time
# with check_local_connectivity passing -- a single bad run (real or a
# connectivity-gate skip) can never alone produce a "down" email.
CONSECUTIVE_FAILURE_THRESHOLD=2

failure_count_path() {
  local check="$1" prop="$2"
  echo "${STATE_DIR}/${check}.${prop}.count"
}

# Increments and returns this check+property's consecutive-failure count.
# Only call after check_local_connectivity has already passed for this run
# -- incrementing on a connectivity-gate skip would let two separate,
# unrelated Mac-offline blips add up to a false "down" alert once the
# network returns, which is the exact failure mode this counter exists to
# prevent.
record_check_failure() {
  local check="$1" prop="$2"
  local f; f=$(failure_count_path "$check" "$prop")
  local n=0
  if [ -f "$f" ]; then
    n=$(cat "$f" 2>/dev/null)
    [[ "$n" =~ ^[0-9]+$ ]] || n=0
  fi
  n=$((n + 1))
  echo "$n" > "$f"
  echo "$n"
}

record_check_success() {
  local check="$1" prop="$2"
  rm -f "$(failure_count_path "$check" "$prop")"
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

# Returns 0 (true) if a recovery notice should fire: a state file exists
# AND it holds a value should_alert_failure actually wrote (a YYYY-MM-DD
# date), meaning a "down" alert was genuinely dispatched and not yet
# cleared. A stray/malformed/old-format state file is NOT treated as "was
# down" -- it's removed silently here (self-healing) so it can never
# produce a false recovery notice for a failure that was never actually
# communicated.
should_alert_recovery() {
  local check="$1" prop="$2"
  local f; f=$(check_state_path "$check" "$prop")
  [ -f "$f" ] || return 1
  local content; content=$(cat "$f" 2>/dev/null)
  if [[ "$content" =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}$ ]]; then
    return 0
  fi
  rm -f "$f"
  return 1
}

clear_failure_state() {
  local check="$1" prop="$2"
  rm -f "$(check_state_path "$check" "$prop")"
}

send_alert() {
  # send_alert <property_key> <subject> <body>
  local prop="$1" subject="$2" body="$3"
  # printf %q shell-quotes each arg for safe re-parsing by the remote bash --
  # naive '$var' wrapping breaks (and silently drops the whole alert with a
  # remote "unexpected EOF" parse error) the moment any arg contains an
  # apostrophe, which several of these subject/body strings do (e.g.
  # "$prop's homepage check failed..."). Confirmed in
  # ~/.claude/hooks/monitoring-state/r2uptime.log: repeated
  # "bash: -c: line 1: unexpected EOF while looking for matching `''" entries
  # from exactly this.
  ssh "$VPS_HOST" "/root/ops/scripts/send_alert.sh $(printf '%q' "$prop") $(printf '%q' "$subject") $(printf '%q' "$body")" 2>&1
}

# --- Centralizes the failure/recovery decision every check in this
# directory makes: consecutive-failure counting, per-day suppression, and
# -- the other bug R1 found -- never writing/clearing failure state unless
# send_alert actually succeeded (previously state updated unconditionally
# right after send_alert was invoked, so a failed SSH send could silently
# desync state from what was actually communicated).
# handle_check_result <check> <prop> <is_failure 0|1> <fail_subject> <fail_body> <recover_subject> <recover_body>
# Caller must have already confirmed check_local_connectivity for this run
# before calling this for a failure case (is_failure=1).
handle_check_result() {
  local check="$1" prop="$2" is_failure="$3" fail_subject="$4" fail_body="$5" recover_subject="$6" recover_body="$7"
  if [ "$is_failure" -eq 1 ]; then
    local n; n=$(record_check_failure "$check" "$prop")
    if [ "$n" -ge "$CONSECUTIVE_FAILURE_THRESHOLD" ] && should_alert_failure "$check" "$prop"; then
      if send_alert "$prop" "$fail_subject" "$fail_body"; then
        record_failure_alert "$check" "$prop"
      fi
    fi
  else
    record_check_success "$check" "$prop"
    if should_alert_recovery "$check" "$prop"; then
      if send_alert "$prop" "$recover_subject" "$recover_body"; then
        clear_failure_state "$check" "$prop"
      fi
    fi
  fi
}
