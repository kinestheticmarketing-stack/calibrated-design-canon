#!/usr/bin/env bash
#
# db_backup.sh — BOX-LEVEL nightly Postgres backup (two independent clusters)
# =============================================================================
# Location: /root/ops/scripts/db_backup.sh
# Log:      /var/log/porterbackup.log   <-- un-hyphenated. The predecessor
#           script at /root/porter/scripts/db_backup.sh documented this as
#           "/var/log/porter-backup.log" in its header, which was WRONG and
#           never matched the live crontab. Do not reintroduce the hyphen.
# Cron:     30 3 * * *  with CRON_TZ=America/Denver (see CRON INSTALL below)
#
# -----------------------------------------------------------------------------
# WHY THIS SCRIPT EXISTS (what changed vs the predecessor)
# -----------------------------------------------------------------------------
# The predecessor discovered databases with a pg_database query executed
# INSIDE `docker compose exec -T db`. That is structurally incapable of
# seeing anything outside the dockerised compose stack, no matter how the
# query is written. This VPS runs a SECOND, entirely separate Postgres:
#
#   docker  porter-db-1        postgres:16, host port 5433, compose service "db"
#                              -> porter, insulation, greeley_insulation
#   host    postgresql@16-main postgres:16, 127.0.0.1:5432, systemd unit
#                              -> totefinders, kinestheticmarketing_com
#
# The host cluster's two databases therefore had NO backup coverage at all.
# This script backs up BOTH clusters in one nightly run, one scheduler, one
# log, one alert path.
#
# -----------------------------------------------------------------------------
# CONNECTION MODEL (verified 2026-08-09 against the live pg_hba.conf)
# -----------------------------------------------------------------------------
#   docker cluster: `docker compose exec -T db pg_dump -U porter ...`
#     Runs inside the container's own trust boundary. No password anywhere on
#     the host. Uses the compose SERVICE name "db", NEVER the generated
#     container name (currently porter-db-1) — that name changes if the repo
#     is renamed or COMPOSE_PROJECT_NAME changes, and a hardcoded container
#     name fails silently.
#
#   host cluster: TCP to 127.0.0.1:5432 as role backup_ro, password auth.
#     NOT the unix socket: pg_hba.conf has `local all all peer`, so a socket
#     connection as backup_ro would require an OS user named backup_ro. The
#     TCP lines are `host all all 127.0.0.1/32 scram-sha-256`, so TCP +
#     password is the only route for a non-OS-backed role. listen_addresses
#     is 'localhost', so this port is not reachable off-box.
#     Credentials live ONLY in /root/ops/.backup.env (mode 0600, root:root).
#
#   backup_ro is deliberately minimal: LOGIN, NOSUPERUSER, NOCREATEDB,
#   NOCREATEROLE, INHERIT, + GRANT pg_read_all_data WITH INHERIT TRUE, +
#   explicit GRANT CONNECT per database (never relying on PUBLIC). It also
#   carries `ALTER ROLE backup_ro SET default_transaction_read_only = on` as
#   a second, independent layer. Proven 2026-08-09: with that soft guard
#   explicitly disabled at connect time via PGOPTIONS, CREATE TABLE and
#   INSERT still fail with "permission denied for schema public" /
#   "permission denied for table ..." — i.e. the denial is grant-level, not
#   merely the read-only session default.
#
#   PG16 GOTCHA, DO NOT REGRESS: `GRANT pg_read_all_data TO backup_ro` records
#   pg_auth_members.inherit_option from the role's rolinherit AT GRANT TIME.
#   Granting while the role is NOINHERIT, then later running
#   `ALTER ROLE backup_ro INHERIT`, does NOT retroactively fix the membership
#   — the grant stays inherit_option=false and every read is denied. The grant
#   must be made (or re-made) as `GRANT pg_read_all_data TO backup_ro WITH
#   INHERIT TRUE`. Verify with:
#     SELECT inherit_option FROM pg_auth_members m
#       JOIN pg_roles r ON r.oid=m.member WHERE r.rolname='backup_ro';
#
# -----------------------------------------------------------------------------
# ROW-LEVEL SECURITY
# -----------------------------------------------------------------------------
# Verified 2026-08-09: ZERO tables with relrowsecurity or relforcerowsecurity
# in either host database, and zero large objects (pg_largeobject_metadata
# empty in both). If RLS is ever introduced, a pg_read_all_data role dumping
# an RLS table silently gets only the rows its policies permit — a SILENT
# PARTIAL BACKUP, the worst failure mode here. If RLS appears, this script
# must add --enable-row-security to the affected pg_dump invocations AND the
# grant design needs re-review (pg_read_all_data does not bypass RLS; only
# BYPASSRLS or superuser does). Re-check with:
#   SELECT count(*) FROM pg_class WHERE relrowsecurity OR relforcerowsecurity;
#
# -----------------------------------------------------------------------------
# FIRST-DISCOVERY BEHAVIOUR (read this before filing a bug)
# -----------------------------------------------------------------------------
# Gap detection asks "did YESTERDAY's dump land in B2?". A database discovered
# for the very first time cannot have one, so the predecessor emitted a false
# [ERROR] GAP alert on the first night of every new database (observed
# 2026-08-07 for greeley_insulation). This script distinguishes the two cases
# by rclone EXIT CODE, never by empty output alone:
#
#   lsf exit nonzero            -> B2 itself is unreachable/erroring. This is a
#                                  REAL failure. Alert. NEVER treated as
#                                  first-discovery.
#   lsf exit 0 + empty listing  -> genuine first discovery. Log it, skip the
#                                  gap check for this database THIS RUN ONLY.
#   lsf exit 0 + files present  -> normal yesterday-check.
#
# Provisioning Longmont, Fort Collins, and Loveland WILL each legitimately
# emit one "new database discovered, no prior backup expected" line. That is
# designed behaviour, not an anomaly.
#
# -----------------------------------------------------------------------------
# CRON INSTALL
# -----------------------------------------------------------------------------
#   crontab -e:
#     CRON_TZ=America/Denver
#     30 3 * * * cd /root/ops && bash scripts/db_backup.sh >> /var/log/porterbackup.log 2>&1
#
#   CRON_TZ on its own line, never inherited — cron's default tz silently
#   shifts the real run time by an hour across DST twice a year.
#
#   This script is NOT its own liveness monitor. A dead cron daemon or a wiped
#   crontab kills the backup AND its ability to complain. That is covered
#   separately by backup_heartbeat_check.sh on a systemd timer (different
#   scheduler, different hour) reading the B2 heartbeat this script writes.
#
# -----------------------------------------------------------------------------
# RESTORE RUNBOOK
# -----------------------------------------------------------------------------
# Restores go into a SCRATCH database, never over a live one.
#
#   docker-cluster database:
#     cd /root/porter
#     docker compose exec -T db psql -U porter -d postgres -c 'CREATE DATABASE <db>_restore_test;'
#     docker compose cp <dump> db:/tmp/r.dump
#     docker compose exec -T db pg_restore -U porter -d <db>_restore_test --no-owner /tmp/r.dump
#     docker compose exec -T db rm -f /tmp/r.dump
#
#   host-cluster database (restore runs as the LOCAL SUPERUSER over the unix
#   socket via peer auth — backup_ro correctly cannot write, and that is the
#   point of the grant design; do not "fix" it by granting backup_ro more):
#     sudo -u postgres psql -c 'CREATE DATABASE <db>_restore_test;'
#     sudo -u postgres pg_restore -d <db>_restore_test --no-owner <dump>
#
#   NEVER pass --create to pg_restore: it derives the target database name
#   from the dump's embedded metadata, defeating the scratch-name isolation.
#
#   Verify per-table row counts, source vs restored — never a single grand
#   total, since two differently-split table sets can sum identically:
#     SELECT relname, n_live_tup FROM pg_stat_user_tables ORDER BY relname;
#   (or an exact count(*) sweep via query_to_xml for authoritative numbers)
#
#   Then DROP the scratch database.
#
#   Retrieving a dump older than the 14-day local retention: B2 versioning is
#   on for this bucket.
#     rclone --b2-versions lsf b2:porter-vps-backups/nightly/<db>/
#     rclone copyto "b2:.../<exact-versioned-name>" ./restore.dump
#   Monthly archives under monthly/<YYYY-MM>/ are never pruned — check there
#   first.
# =============================================================================

set -euo pipefail

# ── Configuration (env-overridable; defaults are production) ─────────────────
PG_SUPERUSER="${PG_SUPERUSER:-porter}"
DOCKER_COMPOSE_DIR="${DOCKER_COMPOSE_DIR:-/root/porter}"
BACKUP_ROOT="${BACKUP_ROOT:-/root/backups/db}"
RCLONE_REMOTE="${RCLONE_REMOTE:-b2:porter-vps-backups}"
NIGHTLY_PREFIX="${NIGHTLY_PREFIX:-nightly}"   # overridden to nightly-dryrun for rehearsals
RETENTION_DAYS="${RETENTION_DAYS:-14}"
ALERT_ENV_FILE="${ALERT_ENV_FILE:-/root/.config/porter-backup/alert.env}"
BACKUP_ENV_FILE="${BACKUP_ENV_FILE:-/root/ops/.backup.env}"
ALERT_DRY_RUN="${ALERT_DRY_RUN:-false}"
GLOBALS_DOW="${GLOBALS_DOW:-7}"               # ISO day-of-week: 7 = Sunday

# Heartbeat path is NAMESPACED BY PREFIX, deliberately. A dry run must never
# be able to satisfy the live dead-man check — otherwise a rehearsal would
# refresh the heartbeat the checker reads and mask a genuinely failing
# production backup for up to the checker's 26h threshold. Live runs
# (NIGHTLY_PREFIX=nightly) write _heartbeat/last_success.json; a rehearsal
# under nightly-dryrun writes _heartbeat-dryrun/last_success.json, which
# nothing watches.
if [ "${NIGHTLY_PREFIX}" = "nightly" ]; then
  HEARTBEAT_PATH="${HEARTBEAT_PATH:-_heartbeat/last_success.json}"
else
  HEARTBEAT_PATH="${HEARTBEAT_PATH:-_heartbeat-${NIGHTLY_PREFIX}/last_success.json}"
fi

TODAY="$(date +%F)"
YESTERDAY="$(date -d yesterday +%F)"
DOW="$(date +%u)"

ERRORS=()

log() { echo "[$(date '+%F %T %Z')] $1"; }

record_error() {
  echo "[ERROR] $1" >&2
  ERRORS+=("$1")
}

# ── Per-database dump-integrity thresholds (bytes) ───────────────────────────
# Basis: 50% of that database's SMALLEST known-good dump, rounded down to a
# round number. A single global floor is useless here — a floor sized for the
# 6 KB insulation database is decorative against the 100 KB
# kinestheticmarketing_com database, which could lose 90% of its content and
# still clear it.
#
# CALIBRATION TRAP — MEASURE AGAINST A FILE, NEVER A PIPE. `pg_dump -Fc`
# writes a SEEKABLE archive when stdout is a regular file (it seeks back to
# record per-block data offsets in the TOC) and a compact streaming form when
# stdout is a pipe. Same data, materially different byte count. Measured
# 2026-08-09 on kinestheticmarketing_com, same connection, back to back:
#     to FILE: 106687      to PIPE: 70041
# This script writes to files, so every threshold below is derived from
# file-output sizes. Sizing a floor from a `pg_dump ... | wc -c` spot check
# yields a floor ~35% too low and a correspondingly blunt integrity check.
#
# Observed known-good FILE sizes as of 2026-08-09 (docker three from B2
# history, which the predecessor also wrote as files; host two from this
# script's first dry run):
#   porter                    51091  -> 25000
#   insulation                 6942  ->  3400
#   greeley_insulation         6260  ->  3100
#   totefinders               56220  -> 28000
#   kinestheticmarketing_com 106687  -> 53000
#   globals (docker cluster)    950  ->   450
#   globals (host cluster)     1586  ->   450  (shared floor; see below)
# Revisit when a database grows materially — a threshold that never moves
# eventually becomes decorative again.
declare -A MIN_BYTES=(
  [porter]=25000
  [insulation]=3400
  [greeley_insulation]=3100
  [totefinders]=28000
  [kinestheticmarketing_com]=53000
)
# Databases with no entry above (Longmont / Fort Collins / Loveland when they
# land) fall back to this. Deliberately low: it exists to catch a zero-length
# or catastrophically truncated dump, NOT to model an unknown database's real
# size. A pg_dump -Fc of a completely empty database is ~700-900 bytes, so 500
# clears an empty schema while still catching genuine truncation. Add a real
# per-database entry above once a few nights of known-good sizes exist.
DEFAULT_MIN_BYTES="${DEFAULT_MIN_BYTES:-500}"
GLOBALS_MIN_BYTES="${GLOBALS_MIN_BYTES:-450}"

min_bytes_for() {
  local db="$1"
  if [[ -v MIN_BYTES[$db] ]]; then
    echo "${MIN_BYTES[$db]}"
  else
    echo "$DEFAULT_MIN_BYTES"
  fi
}

# ── Alerting ─────────────────────────────────────────────────────────────────
# Straight to Resend's API. Independent of the Porter app and of SendGrid
# (which the two insulation site backends use for their own lead mail — a
# different concern with different failure modes; do not consolidate them).
# No dedupe/fingerprint suppression, on purpose: a dedupe layer is exactly
# what turns three weeks of real nightly failures into one email.
send_alert() {
  local subject="$1" body="$2"

  if [ -z "${RESEND_API_KEY:-}" ]; then
    {
      echo "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
      echo "ALERT NOT SENT — no RESEND_API_KEY (missing/incomplete $ALERT_ENV_FILE)."
      echo "Printing it here instead, because this is the only channel left:"
      echo "SUBJECT: $subject"
      echo "$body"
      echo "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
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
      -d "$payload" -o /tmp/porter-backup-alert-response.json 2>/dev/null; then
    log "alert email sent to ${ALERT_TO:-<unset>}"
  else
    {
      echo "ALERT SEND ITSELF FAILED (curl error). Content that would have been sent:"
      echo "SUBJECT: $subject"
      echo "$body"
    } >&2
  fi
  return 0
}

finalize() {
  local rc=$?
  if [ "${#ERRORS[@]}" -gt 0 ]; then
    local body
    body="$(printf '%s\n' "${ERRORS[@]}")"
    send_alert "[VPS backup] ${#ERRORS[@]} issue(s) on $(hostname) — $TODAY" "$body"
    exit 1
  fi
  if [ "$rc" -ne 0 ]; then
    send_alert "[VPS backup] script aborted (exit $rc) on $(hostname) — $TODAY" \
               "db_backup.sh exited $rc with no recorded ERRORS — likely an unguarded failure under set -e. Check /var/log/porterbackup.log."
    exit "$rc"
  fi
  log "backup run completed cleanly for $TODAY"
}
trap finalize EXIT

# ── Setup ────────────────────────────────────────────────────────────────────
if [ -f "$ALERT_ENV_FILE" ]; then
  # shellcheck disable=SC1090
  set -a; . "$ALERT_ENV_FILE"; set +a
else
  {
    echo "###############################################################"
    echo "# ALERT CONFIG MISSING: $ALERT_ENV_FILE not found."
    echo "# Backups below still run. Failures will be visible ONLY in"
    echo "# this log, not emailed, until that file exists."
    echo "###############################################################"
  } >&2
fi

HOST_CREDS_OK=true
if [ -f "$BACKUP_ENV_FILE" ]; then
  # shellcheck disable=SC1090
  set -a; . "$BACKUP_ENV_FILE"; set +a
else
  HOST_CREDS_OK=false
fi

mkdir -p "$BACKUP_ROOT/_globals"

# ── Discovery: docker cluster ────────────────────────────────────────────────
# Failure here must be LOUD. A Porter rebuild that renames the compose project
# breaks this while host discovery keeps working — the run would otherwise
# "succeed" while silently dropping three databases.
DOCKER_DBS=()
discover_docker() {
  local out rc
  out="$(cd "$DOCKER_COMPOSE_DIR" && docker compose exec -T db psql -U "$PG_SUPERUSER" -d postgres -tA -c \
        "SELECT datname FROM pg_database WHERE datname NOT IN ('template0','template1','postgres') ORDER BY datname;" \
        2>/tmp/porter-backup-discovery-docker-err)" && rc=0 || rc=$?
  if [ "$rc" -ne 0 ]; then
    record_error "DISCOVERY FAILED [docker]: pg_database query returned exit $rc. No docker-cluster databases were dumped this run. $(tail -c 400 /tmp/porter-backup-discovery-docker-err 2>/dev/null)"
    return 1
  fi
  mapfile -t DOCKER_DBS < <(printf '%s\n' "$out" | tr -d '\r' | sed '/^$/d')
  if [ "${#DOCKER_DBS[@]}" -eq 0 ]; then
    record_error "DISCOVERY FAILED [docker]: query succeeded but returned zero databases — expected at least porter. Treating as failure, not as an empty cluster."
    return 1
  fi
  log "discovered ${#DOCKER_DBS[@]} database(s) [docker]: ${DOCKER_DBS[*]}"
  return 0
}

# ── Discovery: host cluster ──────────────────────────────────────────────────
HOST_DBS=()
discover_host() {
  if [ "$HOST_CREDS_OK" != true ]; then
    record_error "DISCOVERY FAILED [host]: $BACKUP_ENV_FILE not found — cannot authenticate as backup_ro. No host-cluster databases were dumped this run."
    return 1
  fi
  local out rc
  out="$(PGPASSWORD="${BACKUP_RO_PASSWORD:-}" psql -h "${BACKUP_RO_HOST:-127.0.0.1}" -p "${BACKUP_RO_PORT:-5432}" \
        -U "${BACKUP_RO_USER:-backup_ro}" -d postgres -tA -c \
        "SELECT datname FROM pg_database WHERE datname NOT IN ('template0','template1','postgres') ORDER BY datname;" \
        2>/tmp/porter-backup-discovery-host-err)" && rc=0 || rc=$?
  if [ "$rc" -ne 0 ]; then
    record_error "DISCOVERY FAILED [host]: pg_database query returned exit $rc. No host-cluster databases were dumped this run. $(tail -c 400 /tmp/porter-backup-discovery-host-err 2>/dev/null)"
    return 1
  fi
  mapfile -t HOST_DBS < <(printf '%s\n' "$out" | tr -d '\r' | sed '/^$/d')
  if [ "${#HOST_DBS[@]}" -eq 0 ]; then
    record_error "DISCOVERY FAILED [host]: query succeeded but returned zero databases — expected at least totefinders. Treating as failure, not as an empty cluster."
    return 1
  fi
  log "discovered ${#HOST_DBS[@]} database(s) [host]: ${HOST_DBS[*]}"
  return 0
}

# Independent: one failing must not prevent the other from running.
DOCKER_OK=true; discover_docker || DOCKER_OK=false
HOST_OK=true;   discover_host   || HOST_OK=false

if [ "$DOCKER_OK" != true ] && [ "$HOST_OK" != true ]; then
  record_error "CRITICAL: BOTH discovery passes failed — nothing was backed up this run."
fi

# ── Namespace collision check ────────────────────────────────────────────────
# Both clusters write to nightly/<dbname>/. Identical names in both would
# silently overwrite each other in B2 — one cluster's data masquerading as the
# other's, undetectable at restore time. Hard stop, never an overwrite.
if [ "$DOCKER_OK" = true ] && [ "$HOST_OK" = true ]; then
  COLLISIONS=()
  for d in "${DOCKER_DBS[@]}"; do
    for h in "${HOST_DBS[@]}"; do
      [ "$d" = "$h" ] && COLLISIONS+=("$d")
    done
  done
  if [ "${#COLLISIONS[@]}" -gt 0 ]; then
    record_error "NAMESPACE COLLISION: database name(s) present in BOTH clusters: ${COLLISIONS[*]}. Both would write to ${NIGHTLY_PREFIX}/<name>/ and silently overwrite each other. Refusing to upload anything this run — resolve by renaming or by namespacing the B2 path per instance."
    exit 1
  fi
  log "namespace collision check passed — no database name appears in both clusters"
fi

# ── Gap detection, exit-code-aware ───────────────────────────────────────────
# See FIRST-DISCOVERY BEHAVIOUR in the header. The distinction that matters:
# an rclone failure and an empty listing are NOT the same thing, and conflating
# them turns "B2 is unreachable" into "this must be a new database, carry on".
check_gap() {
  local db="$1" instance="$2" listing rc
  listing="$(rclone lsf "${RCLONE_REMOTE}/${NIGHTLY_PREFIX}/${db}/" 2>/tmp/porter-backup-lsf-err)" && rc=0 || rc=$?
  if [ "$rc" -ne 0 ]; then
    record_error "GAP-CHECK FAILED [${instance}] ${db}: rclone lsf exited ${rc} — B2 unreachable or path errored. NOT treated as a new database. $(tail -c 300 /tmp/porter-backup-lsf-err 2>/dev/null)"
    return 0
  fi
  if [ -z "$listing" ]; then
    log "new database discovered [${instance}]: ${db} — no prior backup expected, gap check skipped this run only"
    return 0
  fi
  if ! printf '%s\n' "$listing" | grep -qx "${db}-${YESTERDAY}.dump"; then
    record_error "GAP [${instance}]: expected ${NIGHTLY_PREFIX}/${db}/${db}-${YESTERDAY}.dump not found in B2 — previous run may have failed or not executed."
  fi
  return 0
}

# NOTE: written as if/fi, NOT `[ cond ] && for ...`. Under `set -e` a false
# test at the head of an && list makes the whole list return non-zero and
# aborts the script — which would silently skip every remaining stage.
if [ "$DOCKER_OK" = true ]; then
  for db in "${DOCKER_DBS[@]}"; do check_gap "$db" docker; done
fi
if [ "$HOST_OK" = true ]; then
  for db in "${HOST_DBS[@]}"; do check_gap "$db" host; done
fi

# ── Dump helpers ─────────────────────────────────────────────────────────────
TODAYS_DUMP_FILES=()
FAILED_ANY=false

verify_and_keep() {
  # $1 tmp file, $2 final path, $3 label for logs, $4 min bytes, $5 instance
  local tmp="$1" final="$2" label="$3" floor="$4" instance="$5" size
  size="$(wc -c < "$tmp")"
  if [ "$size" -lt "$floor" ]; then
    rm -f "$tmp"
    record_error "DUMP TOO SMALL [${instance}] ${label}: ${size} bytes < ${floor} byte floor. NOT uploaded — treating as a truncated/corrupt dump rather than shipping it over a good one."
    FAILED_ANY=true
    return 1
  fi
  mv "$tmp" "$final"
  log "dumped ${label} [${instance}] -> ${final} (${size} bytes, floor ${floor})"
  return 0
}

prune_retention() {
  local dir="$1" pattern="$2"
  local existing=()
  mapfile -t existing < <(find "$dir" -maxdepth 1 -type f -name "$pattern" | sort)
  local excess=$(( ${#existing[@]} - RETENTION_DAYS ))
  if [ "$excess" -gt 0 ]; then
    for ((i = 0; i < excess; i++)); do
      log "pruning old file: ${existing[$i]}"
      rm -f "${existing[$i]}"
    done
  fi
}

# ── Dumps: docker cluster ────────────────────────────────────────────────────
if [ "$DOCKER_OK" = true ]; then
  for db in "${DOCKER_DBS[@]}"; do
    dump_dir="$BACKUP_ROOT/$db"; mkdir -p "$dump_dir"
    dump_file="$dump_dir/${db}-${TODAY}.dump"; tmp_file="${dump_file}.tmp"
    if (cd "$DOCKER_COMPOSE_DIR" && docker compose exec -T db pg_dump -U "$PG_SUPERUSER" -Fc "$db") \
         > "$tmp_file" 2>/tmp/porter-backup-pg_dump-err; then
      if verify_and_keep "$tmp_file" "$dump_file" "$db" "$(min_bytes_for "$db")" docker; then
        TODAYS_DUMP_FILES+=("$dump_file")
      fi
    else
      rm -f "$tmp_file"
      record_error "pg_dump FAILED [docker] '$db': $(tail -c 400 /tmp/porter-backup-pg_dump-err 2>/dev/null)"
      FAILED_ANY=true
    fi
    prune_retention "$dump_dir" "${db}-*.dump"
  done
fi

# ── Dumps: host cluster ──────────────────────────────────────────────────────
if [ "$HOST_OK" = true ]; then
  for db in "${HOST_DBS[@]}"; do
    dump_dir="$BACKUP_ROOT/$db"; mkdir -p "$dump_dir"
    dump_file="$dump_dir/${db}-${TODAY}.dump"; tmp_file="${dump_file}.tmp"
    if PGPASSWORD="${BACKUP_RO_PASSWORD:-}" pg_dump -h "${BACKUP_RO_HOST:-127.0.0.1}" -p "${BACKUP_RO_PORT:-5432}" \
         -U "${BACKUP_RO_USER:-backup_ro}" -Fc "$db" > "$tmp_file" 2>/tmp/porter-backup-pg_dump-err; then
      if verify_and_keep "$tmp_file" "$dump_file" "$db" "$(min_bytes_for "$db")" host; then
        TODAYS_DUMP_FILES+=("$dump_file")
      fi
    else
      rm -f "$tmp_file"
      record_error "pg_dump FAILED [host] '$db': $(tail -c 400 /tmp/porter-backup-pg_dump-err 2>/dev/null)"
      FAILED_ANY=true
    fi
    prune_retention "$dump_dir" "${db}-*.dump"
  done
fi

# ── Globals: weekly, BOTH clusters ───────────────────────────────────────────
# Per-database dumps do NOT capture roles, role memberships, or cluster-wide
# grants. Without these a disaster-recovery restore comes up with tables and
# no one authorised to read them. Weekly rather than nightly because they
# change rarely; the day-of-week test lives inside the nightly run so there is
# exactly one scheduler and one script to reason about.
TODAYS_GLOBALS_FILES=()
if [ "$DOW" = "$GLOBALS_DOW" ]; then
  log "day-of-week ${DOW} matches GLOBALS_DOW ${GLOBALS_DOW} — dumping cluster globals"
  globals_dir="$BACKUP_ROOT/_globals"; mkdir -p "$globals_dir"

  if [ "$DOCKER_OK" = true ]; then
    gf="$globals_dir/globals-docker-${TODAY}.sql"; tf="${gf}.tmp"
    if (cd "$DOCKER_COMPOSE_DIR" && docker compose exec -T db pg_dumpall -U "$PG_SUPERUSER" --globals-only) \
         > "$tf" 2>/tmp/porter-backup-globals-err; then
      if verify_and_keep "$tf" "$gf" "globals-docker" "$GLOBALS_MIN_BYTES" docker; then
        TODAYS_GLOBALS_FILES+=("$gf")
      fi
    else
      rm -f "$tf"
      record_error "pg_dumpall --globals-only FAILED [docker]: $(tail -c 400 /tmp/porter-backup-globals-err 2>/dev/null)"
      FAILED_ANY=true
    fi
  fi

  if [ "$HOST_OK" = true ]; then
    gf="$globals_dir/globals-host-${TODAY}.sql"; tf="${gf}.tmp"
    # NOTE: pg_dumpall --globals-only includes role passwords (SCRAM verifiers)
    # when run as superuser. backup_ro is not superuser, so password hashes are
    # omitted here — roles/memberships/grants still land, which is what a DR
    # restore needs. Do not "fix" this by making backup_ro superuser.
    if PGPASSWORD="${BACKUP_RO_PASSWORD:-}" pg_dumpall -h "${BACKUP_RO_HOST:-127.0.0.1}" -p "${BACKUP_RO_PORT:-5432}" \
         -U "${BACKUP_RO_USER:-backup_ro}" --globals-only > "$tf" 2>/tmp/porter-backup-globals-err; then
      if verify_and_keep "$tf" "$gf" "globals-host" "$GLOBALS_MIN_BYTES" host; then
        TODAYS_GLOBALS_FILES+=("$gf")
      fi
    else
      rm -f "$tf"
      record_error "pg_dumpall --globals-only FAILED [host]: $(tail -c 400 /tmp/porter-backup-globals-err 2>/dev/null)"
      FAILED_ANY=true
    fi
  fi

  prune_retention "$globals_dir" "globals-*.sql"
else
  log "day-of-week ${DOW} != GLOBALS_DOW ${GLOBALS_DOW} — skipping globals this run"
fi

# ── Upload ───────────────────────────────────────────────────────────────────
# sync mirrors local retention (including deletions) into the nightly prefix.
# monthly/ is a separate prefix and is never touched by this sync.
UPLOAD_OK=true
if rclone sync "$BACKUP_ROOT" "${RCLONE_REMOTE}/${NIGHTLY_PREFIX}" --exclude '*.tmp' \
     2>/tmp/porter-backup-rclone-sync-err; then
  log "sync to ${RCLONE_REMOTE}/${NIGHTLY_PREFIX} complete"
else
  record_error "rclone sync to ${RCLONE_REMOTE}/${NIGHTLY_PREFIX} FAILED: $(tail -c 400 /tmp/porter-backup-rclone-sync-err 2>/dev/null)"
  UPLOAD_OK=false
  FAILED_ANY=true
fi

# ── Monthly archive ──────────────────────────────────────────────────────────
# copy, never sync — this prefix is additive and never pruned. Keys on
# "no archive exists for the current month" rather than "day == 01", so a host
# that was down on the 1st, or a mid-month install, still gets its anchor.
# Skipped entirely for dry runs (non-default NIGHTLY_PREFIX) so a rehearsal
# never writes into the real monthly tree.
if [ "$NIGHTLY_PREFIX" = "nightly" ] && [ "$UPLOAD_OK" = true ]; then
  month_tag="$(date +%Y-%m)"
  monthly_remote="${RCLONE_REMOTE}/monthly/${month_tag}"
  existing_monthly="$(rclone lsf "$monthly_remote" 2>/dev/null || true)"
  if [ -z "$existing_monthly" ]; then
    log "first successful run this month — archiving to $monthly_remote"
    for f in "${TODAYS_DUMP_FILES[@]}" "${TODAYS_GLOBALS_FILES[@]}"; do
      if ! rclone copyto "$f" "${monthly_remote}/$(basename "$f")" 2>/tmp/porter-backup-monthly-err; then
        record_error "monthly archive copy FAILED for $(basename "$f"): $(tail -c 300 /tmp/porter-backup-monthly-err 2>/dev/null)"
      fi
    done
  else
    log "monthly archive for $month_tag already present — skipping"
  fi
else
  log "monthly archive skipped (prefix=${NIGHTLY_PREFIX}, upload_ok=${UPLOAD_OK})"
fi

# ── Heartbeat — LAST action, only on a fully clean run ───────────────────────
# This is what the external dead-man checker reads. It must NOT be written if
# anything failed, otherwise a broken backup keeps reporting itself healthy —
# which is the exact failure this whole design exists to prevent.
if [ "${#ERRORS[@]}" -eq 0 ] && [ "$FAILED_ANY" = false ]; then
  hb_tmp="$(mktemp)"
  python3 - "$hb_tmp" "${#DOCKER_DBS[@]}" "${#HOST_DBS[@]}" "$NIGHTLY_PREFIX" <<'PYEOF'
import json, sys, datetime
path, docker_n, host_n, prefix = sys.argv[1:5]
json.dump({
    "last_success_utc": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    "docker_db_count": int(docker_n),
    "host_db_count": int(host_n),
    "total_db_count": int(docker_n) + int(host_n),
    "prefix": prefix,
}, open(path, "w"), indent=2)
PYEOF
  if rclone copyto "$hb_tmp" "${RCLONE_REMOTE}/${HEARTBEAT_PATH}" 2>/tmp/porter-backup-hb-err; then
    log "heartbeat written to ${RCLONE_REMOTE}/${HEARTBEAT_PATH} (docker=${#DOCKER_DBS[@]}, host=${#HOST_DBS[@]})"
  else
    record_error "heartbeat write FAILED: $(tail -c 300 /tmp/porter-backup-hb-err 2>/dev/null)"
  fi
  rm -f "$hb_tmp"
else
  log "heartbeat NOT written — run had failures (errors=${#ERRORS[@]}, failed_any=${FAILED_ANY})"
fi

# finalize() runs via the EXIT trap.
