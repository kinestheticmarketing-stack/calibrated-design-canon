#!/usr/bin/env bash
#
# backup_heartbeat_check.sh — EXTERNAL dead-man switch for db_backup.sh
# =============================================================================
# Location: /root/ops/scripts/backup_heartbeat_check.sh
# Trigger:  systemd timer backup-heartbeat-check.timer (NOT cron)
#
# -----------------------------------------------------------------------------
# WHY THIS EXISTS AND WHY IT IS DELIBERATELY DECOUPLED
# -----------------------------------------------------------------------------
# A backup script cannot be its own liveness monitor. If cron is dead, the
# crontab is wiped, or the host is off at 03:30, db_backup.sh does not run —
# and therefore also does not alert about not running. Its internal gap-check
# only ever fires from INSIDE a run that did happen.
#
# So this checker shares as little as possible with the thing it watches:
#
#   different scheduler   systemd timer, not cron. A dead cron daemon or a
#                         `crontab -r` cannot silence this.
#   different hour        09:17 local, not 03:30. Not adjacent to the backup
#                         window, so a hung backup is observed rather than
#                         raced.
#   no shared config      does not read /root/ops/.backup.env, does not read
#                         the backup log, does not touch the crontab, does not
#                         source anything db_backup.sh writes except the one
#                         heartbeat object in B2 — which is the whole point.
#                         It reads its OWN alert credentials from the same
#                         Resend env file (a shared credential, not shared
#                         control flow).
#
# The single coupling is intentional: B2 heartbeat object written by
# db_backup.sh as its LAST action, and ONLY on a fully clean run. If any
# database failed, no heartbeat is written, so a partially-broken backup goes
# stale here rather than reporting itself healthy.
#
# THRESHOLD: 26 hours. The backup runs every 24h; 26 gives a 2-hour grace for
# a slow run, DST shift, or a late start, without letting a genuinely missed
# night pass unnoticed. A missed run trips this the following morning.
#
# ALERTING: Resend, matching db_backup.sh. NOT SendGrid — SendGrid on this box
# belongs to the two insulation site backends for lead mail; keeping ops
# alerting on a separate provider means a SendGrid outage or key revocation
# cannot blind the backup monitoring at the same time.
#
# EXIT CODES: 0 = heartbeat fresh. 1 = stale/missing/unreadable (alert sent).
# =============================================================================

set -uo pipefail

RCLONE_REMOTE="${RCLONE_REMOTE:-b2:porter-vps-backups}"
HEARTBEAT_PATH="${HEARTBEAT_PATH:-_heartbeat/last_success.json}"
MAX_AGE_HOURS="${MAX_AGE_HOURS:-26}"
ALERT_ENV_FILE="${ALERT_ENV_FILE:-/root/.config/porter-backup/alert.env}"
ALERT_DRY_RUN="${ALERT_DRY_RUN:-false}"

log() { echo "[$(date '+%F %T %Z')] $1"; }

if [ -f "$ALERT_ENV_FILE" ]; then
  # shellcheck disable=SC1090
  set -a; . "$ALERT_ENV_FILE"; set +a
fi

send_alert() {
  local subject="$1" body="$2"
  if [ -z "${RESEND_API_KEY:-}" ]; then
    {
      echo "ALERT NOT SENT — no RESEND_API_KEY. Printing instead:"
      echo "SUBJECT: $subject"
      echo "$body"
    } >&2
    return 0
  fi
  local payload
  payload="$(python3 - "$subject" "$body" "${ALERT_FROM:-alerts@talktoporter.com}" "${ALERT_TO:-}" <<'PYEOF'
import json, sys
subject, body, from_addr, to_addr = sys.argv[1:5]
print(json.dumps({"from": from_addr, "to": [to_addr], "subject": subject, "text": body}))
PYEOF
)"
  if [ "$ALERT_DRY_RUN" = "true" ]; then
    log "ALERT_DRY_RUN=true — not sending. Subject would be: $subject"
    return 0
  fi
  if curl -sS -X POST https://api.resend.com/emails \
      -H "Authorization: Bearer $RESEND_API_KEY" \
      -H "Content-Type: application/json" \
      -d "$payload" -o /tmp/backup-heartbeat-alert-response.json 2>/dev/null; then
    log "alert email sent to ${ALERT_TO:-<unset>}"
  else
    echo "ALERT SEND FAILED (curl). Subject: $subject" >&2
  fi
  return 0
}

alarm() {
  local reason="$1"
  log "ALARM: $reason"
  send_alert "[VPS backup] DEAD-MAN ALARM on $(hostname)" \
"Backup heartbeat check FAILED.

Reason:    $reason
Heartbeat: ${RCLONE_REMOTE}/${HEARTBEAT_PATH}
Threshold: ${MAX_AGE_HOURS}h
Checked:   $(date -u '+%F %T UTC')

The nightly backup has not reported a fully-successful run within the
threshold. Either it did not run (cron dead / crontab changed / host down),
or it ran and something failed — db_backup.sh deliberately does NOT write a
heartbeat when any database fails.

Check: journalctl -u backup-heartbeat-check.service --since '-2d'
       tail -100 /var/log/porterbackup.log
       crontab -l"
  exit 1
}

# ── Fetch heartbeat ──────────────────────────────────────────────────────────
tmp="$(mktemp)"
trap 'rm -f "$tmp"' EXIT

if ! rclone copyto "${RCLONE_REMOTE}/${HEARTBEAT_PATH}" "$tmp" 2>/tmp/heartbeat-fetch-err; then
  alarm "heartbeat object could not be read from B2 (rclone copyto failed). This means either the object is missing entirely — no successful backup has ever written one — or B2/rclone is broken. $(tail -c 300 /tmp/heartbeat-fetch-err 2>/dev/null)"
fi

if [ ! -s "$tmp" ]; then
  alarm "heartbeat object is empty (0 bytes)."
fi

# ── Parse + age ──────────────────────────────────────────────────────────────
# Age is computed from the timestamp INSIDE the object, not from B2 file
# mtime: mtime reflects when the object was uploaded, which a re-upload or a
# sync could refresh without a backup having actually succeeded.
AGE_OUTPUT="$(python3 - "$tmp" "$MAX_AGE_HOURS" <<'PYEOF'
import json, sys, datetime
path, max_age_h = sys.argv[1], float(sys.argv[2])
try:
    d = json.load(open(path))
except Exception as e:
    print(f"PARSE_ERROR|heartbeat is not valid JSON: {e}")
    sys.exit(0)
ts = d.get("last_success_utc")
if not ts:
    print("PARSE_ERROR|heartbeat JSON has no last_success_utc field")
    sys.exit(0)
try:
    when = datetime.datetime.strptime(ts, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=datetime.timezone.utc)
except Exception as e:
    print(f"PARSE_ERROR|unparseable last_success_utc {ts!r}: {e}")
    sys.exit(0)
now = datetime.datetime.now(datetime.timezone.utc)
age_h = (now - when).total_seconds() / 3600.0
status = "STALE" if age_h > max_age_h else "FRESH"
print(f"{status}|{age_h:.2f}|{ts}|docker={d.get('docker_db_count')}|host={d.get('host_db_count')}|total={d.get('total_db_count')}|prefix={d.get('prefix')}")
PYEOF
)"

STATUS="${AGE_OUTPUT%%|*}"
DETAIL="${AGE_OUTPUT#*|}"

case "$STATUS" in
  PARSE_ERROR) alarm "$DETAIL" ;;
  STALE)
    AGE_H="${DETAIL%%|*}"
    alarm "heartbeat is STALE — last successful backup was ${AGE_H}h ago, threshold ${MAX_AGE_HOURS}h. Details: ${DETAIL}"
    ;;
  FRESH)
    log "heartbeat OK — ${DETAIL}"
    exit 0
    ;;
  *) alarm "unexpected checker output: ${AGE_OUTPUT}" ;;
esac
