# TOOLING_RUNBOOK.md — canon (shared portfolio infrastructure)

**Added 2026-08-31.** Covers the VPS alerting layer (`ops/`, imported this
same day from `/root/ops/scripts/` on the VPS, previously unversioned) and
the Mac-side monitoring layer (`scripts/monitoring/`, built earlier the same
day). A fresh session should be able to operate both from this file alone.

## Why this lives in canon, not a site repo

These scripts serve all three properties (DCI, GCI, LGM) from one shared
run — they are not any one site's code. `retention_cleanup.js` living only
in the DCI repo, despite covering all three properties' databases, is the
precedent this deliberately does **not** follow (Director ruling,
2026-08-31): a script that started in one property repo because someone had
to put it somewhere is not the same as a script that *belongs* to one
property. Shared infrastructure belongs in canon.

## What lives where

| Component | Location | What it is |
|---|---|---|
| VPS alerting layer (code) | `ops/` in this repo, deployed to `/root/ops/scripts/` on the VPS | The shared alert-sending function and the two checks that call it — see table below |
| VPS alerting layer (runtime state) | `/root/ops/state/` on the VPS only — never in git | Suppression state, audit log, test-mode log. Gitignored (`ops/state/`, `ops/**/*.bak-*`, `ops/**/*.log`) even though nothing currently syncs it into this repo — see [.gitignore](.gitignore) |
| VPS-side systemd timers | `/etc/systemd/system/*.timer` on the VPS only — no copy in any repo (confirmed 2026-08-30, still true) | Schedule the checks in `ops/` |
| Deploy path | `scripts/deploy_ops_to_vps.sh` | The **only** sanctioned way a canon change to `ops/` reaches the VPS |
| Drift check | `scripts/monitoring/ops_drift_check.sh`, wired into `scripts/monitoring/daily_checks.sh` | Alerts if the VPS ever diverges from canon again |
| Mac-side monitoring layer | `scripts/monitoring/` in this repo | Uptime, TLS expiry, deploy drift (per-site), page-200, and ops drift — see below |
| Mac-side scheduling | `~/Library/LaunchAgents/com.vongimbel.r2uptime.plist` and `com.vongimbel.r2daily.plist` — **not in this repo**, local-machine config | Run the checks in `scripts/monitoring/` |

## The VPS alerting layer (`ops/`)

| File | Purpose | Invoked by |
|---|---|---|
| `send_alert.js` | Shared alert-send function: SendGrid, per-(property, check) suppression/recovery state, `ALERT_TEST_MODE` isolation, placeholder-content refusal. State-namespace-isolated between test and real calls since the 2026-08-31 fix (see its own header comment for the incident that caused that). | `stale_site_check.js`, `unhandled_lead_check.js` (direct `node` calls); `send_alert.sh` (bridge, `--force`) |
| `send_alert.sh` | 3-positional-arg bridge to `send_alert.js --force`, for callers that keep their own suppression state and just want an unconditional send. **Not orphaned** — despite having zero callers anywhere under `/root/`, it is the sole path `scripts/monitoring/_mon_lib.sh`'s `send_alert()` uses, invoked over SSH from this Mac. A 2026-08-31 pass on this file nearly deleted it as an orphan based on a VPS-only `grep`; corrected before anything was removed. | `_mon_lib.sh` (in this repo), via `ssh root@74.208.181.10` |
| `test_send_alert.js` | Manual verification harness for `send_alert.js`'s test-mode and placeholder-refusal logic (poisons `@sendgrid/mail` in `require.cache` before `send_alert.js` loads, so a structural bug in the short-circuit throws instead of silently passing). Not scheduled — run by hand when verifying a change to `send_alert.js`. | Nothing automatic — manual only |
| `stale_site_check.js` | Daily: alerts if a property's canary succeeded every day for 7 complete days but zero real leads/pageviews landed in that window. | `stale-site-check.timer` |
| `unhandled_lead_check.js` | Every 15 min: closes any real lead older than 30 days and never delivered as `closed_reason='stale-30d'`, then alerts on any real, undelivered lead older than 15 minutes. | `unhandled-lead-check.timer` |
| `backup_heartbeat_check.sh` | Daily: dead-man switch reading a B2 heartbeat object `db_backup.sh` writes on a fully clean run. Deliberately decoupled scheduler/hour/config from the thing it watches. | `backup-heartbeat-check.timer` |
| `db_backup.sh` | Daily (cron, not systemd): backs up every Postgres database (docker + host clusters) to B2, writes the heartbeat object above. | root's crontab, `30 3 * * *` |

**Not in `ops/`, deliberately out of this pass's scope**: `canary_check.js`,
`browser_canary.js`, `retention_cleanup.js` all live in the DCI repo's own
`ops/` today despite also serving GCI and LGM — the same precedent this
pass's ruling says not to repeat for *new* shared code, but migrating
*already-shipped* shared code out of DCI was not what this pass was asked
to do. A future pass could extend this same import pattern to them.

## Every timer, with its schedule

**VPS (systemd, `America/Denver` — confirmed via `timedatectl` 2026-08-30,
still true; times without an explicit zone suffix in `OnCalendar` are
already local because of that host setting):**

| Timer | Schedule | Runs |
|---|---|---|
| `unhandled-lead-check.timer` | `OnBootSec=5min`, `OnUnitActiveSec=15min` | `ops/unhandled_lead_check.js` |
| `stale-site-check.timer` | daily, 23:00 | `ops/stale_site_check.js` |
| `backup-heartbeat-check.timer` | daily, 09:17 | `ops/backup_heartbeat_check.sh` |

**VPS (cron, `CRON_TZ=America/Denver`):**

| Entry | Schedule | Runs |
|---|---|---|
| `db_backup.sh` | daily, 03:30 | `ops/db_backup.sh` |

**Mac (`launchd`, local machine time):**

| Agent | Schedule | Runs |
|---|---|---|
| `com.vongimbel.r2uptime` | every 600s (10 min), `RunAtLoad=false` | `scripts/monitoring/uptime_check.sh` |
| `com.vongimbel.r2daily` | daily, 07:00 | `scripts/monitoring/daily_checks.sh` → `deploy_drift_check.sh`, `tls_expiry_check.sh`, `page200_check.sh`, `ops_drift_check.sh` |

**Historical note — FIXED 2026-08-31 (lane `uptime-false-alert-fix`).** The
limitation described below was real and did fire: three false "Uptime
recovered" emails for DCI on 2026-08-31 (14:25, 18:21, 19:52), and R1's
investigation of that incident found the same blip hit LGM and GCI too
(their alerts just weren't noticed) — DCI's nginx access log had zero
requests in the ~10-minute window before each false recovery while the
backend itself never restarted (`NRestarts=0`, continuously active), which
is the signature of the *request never leaving this Mac*, not a site
outage. Root cause, read from the code: every check in this directory did
one `curl`/`ssh`, no retry, no local-connectivity check, and wrote/cleared
alert state unconditionally regardless of whether `send_alert` actually
succeeded — a single bad network moment here was, by design, sufficient to
send both a real "down" and a real "recovered" email for a site that was
never down.

Fix, in `_mon_lib.sh`, applied to all five checks in this directory
(`uptime_check.sh`, `deploy_drift_check.sh`, `tls_expiry_check.sh`,
`page200_check.sh`, `ops_drift_check.sh`):
- `check_local_connectivity()` — two independent probes against a stable,
  non-monitored endpoint (raw-IP HTTPS to `1.1.1.1`, plus a normal fetch of
  `cloudflare.com` to exercise DNS specifically). Every check calls this
  once, before touching any per-property state, and skips the whole run
  (zero alerts, zero state writes, one line to stderr) if it fails — a
  result gathered while this Mac can't reach the internet is never
  trusted either way.
- `record_check_failure()` / `record_check_success()` — a per-check/
  per-property consecutive-failure counter (`<check>.<prop>.count` in
  `~/.claude/hooks/monitoring-state/`, separate from the existing
  per-day-suppression `.state` file). `CONSECUTIVE_FAILURE_THRESHOLD=2`:
  a "down" alert only fires on the second consecutive real failure (i.e.
  connectivity gate passed both times), so one bad run — real or a
  connectivity-gate skip — can never alone trigger an alert. Counter only
  increments on a connectivity-gate PASS, so two separate offline blips
  can't add up across a gate skip.
- `should_alert_recovery()` now validates the `.state` file actually holds
  a date `should_alert_failure` wrote it — a stray/malformed/old-format
  file is deleted silently and never treated as "was down," so it can't
  produce a false recovery.
- `handle_check_result()` centralizes all of the above and — the other bug
  R1 found — only calls `record_failure_alert`/`clear_failure_state` when
  `send_alert` actually returned success, so a failed SSH send can no
  longer desync local state from what was actually communicated.

Verified by this pass (R2): simulated total local-connectivity loss (all
HTTPS routed through an unreachable bogus proxy, real network untouched)
produced zero alerts and zero state writes across all five checks, each
logging its one-line SKIPPED notice to stderr and exiting 0. An isolated
threshold/state-integrity test (fake check+prop key, stubbed `send_alert`,
never touches real alert state) confirmed: failure 1 → count=1, no send;
failure 2 → threshold met, alert sent, state written; failure 3 same day →
suppressed; next healthy run → recovery sent, state+count cleared; a
`send_alert` that reports failure never writes state even after 2
failures; a malformed/stray `.state` file self-heals silently instead of
firing a false recovery. All five checks also run manually against the
live, healthy portfolio and stayed silent (one incidental transient
VPS-scp hiccup on `deploy_drift_check.sh`/LGM landed at count=1, no alert —
confirmed LGM's live `index.js` and `public/` are byte-identical to the
repo, not a real drift). Live, real-alert-fires-on-a-genuinely-bad-host
end-to-end proof (actual SSH send, not stubbed) is R3's independent
verification pass, by design — see lane `uptime-false-alert-fix` in
`docs/lanes.md` for its result once landed.

## How to change `ops/` code

1. Edit the file(s) in `ops/` in this repo, in a claimed lane per
   `docs/lanes.md`.
2. Commit.
3. Run `scripts/deploy_ops_to_vps.sh` from this repo. It diffs each of the
   7 tracked files against the VPS by md5, backs up the VPS copy first
   (`<file>.bak-pre-canon-deploy-<date>`, matching the VPS's own existing
   `.bak-*` convention) only for files that actually changed, deploys, and
   verifies the post-deploy md5 matches before reporting success.
4. Push canon.
5. `ops_drift_check.sh` (next `r2daily` run, or run it manually) confirms
   the VPS matches — silent if so.

**There is no other sanctioned path.** A live edit directly on the VPS is
exactly what put this code out of version control before 2026-08-31 — do
that again and `ops_drift_check.sh` will alert, but the point of this
script existing is to make that unnecessary, not merely detectable.

## The drift check

`scripts/monitoring/ops_drift_check.sh`, wired into `daily_checks.sh`
(07:00 daily via `r2daily`), follows the exact pattern
`deploy_drift_check.sh` already established for per-property drift: md5
each of the 7 tracked files in canon's `ops/` against its live VPS copy at
`/root/ops/scripts/`, and use `_mon_lib.sh`'s shared
`should_alert_failure` / `record_failure_alert` / `should_alert_recovery` /
`clear_failure_state` / `send_alert` helpers — same suppression-per-day,
same recovery-on-next-clean-run behavior, same VPS-side sender, as every
other check in this directory. Unlike the per-property checks, this one
directory is shared across all three properties, so there is one check
here, not three; it routes its alert through a single fixed property key
(`denvercoloradoinsulation.com`) purely so `send_alert.js` has a
`from`-address to resolve — the alert body names the drifted file(s), not
a property.

**Silent on match, alerts on mismatch, one recovery notice when fixed** —
proven both directions 2026-08-31 (see the lane's report for the exact
sequence: a real trivial change was introduced, drift alerted, deployed,
drift cleared and recovered, then reverted and deployed again with the
same result both ways).

## Rule 5 — secrets

No file under `ops/` contains a hardcoded credential — confirmed by pattern
search 2026-08-31 (checked again as part of this import; see the lane
report, not reproduced here since Rule 5 forbids restating even a
non-match search in a way that could be mistaken for a value). Every
credential is sourced from an external env file via shell/dotenv
substitution: `SENDGRID_API_KEY` and per-property `.env` files (each
site's own directory), `RESEND_API_KEY`/`ALERT_FROM`/`ALERT_TO` from
`/root/.config/porter-backup/alert.env`, `BACKUP_RO_PASSWORD` and friends
from `/root/ops/.backup.env` — none of these env files are in `ops/`, in
canon, or in any site repo, and none should ever be.
