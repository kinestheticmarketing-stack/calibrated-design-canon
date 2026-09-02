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
| Rules pipeline (code) | `~/.claude/hooks/sync_rules_from_canon.sh` — **not in this repo**, local-machine config | Regenerates `~/.claude/context/rules.md` from this repo's `METHODS/ARCHITECT_DISCIPLINE.md` (Rules 1-9 block) plus `~/.claude/CLAUDE.md`'s kickoff-decomposition section, every session, before `~/.claude/hooks/h01_session_start.sh` injects it |
| Rules pipeline drift check | `scripts/monitoring/rules_drift_check.sh`, wired into `scripts/monitoring/daily_checks.sh` | Alerts if `rules.md` ever diverges from canon's `ARCHITECT_DISCIPLINE.md`, or if the local canon checkout falls behind `origin/main` |
| Mac-side monitoring layer | `scripts/monitoring/` in this repo | Uptime, TLS expiry, deploy drift (per-site), page-200, ops drift, and rules drift — see below |
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
| `com.vongimbel.r2daily` | daily, 07:00 | `scripts/monitoring/daily_checks.sh` → `deploy_drift_check.sh`, `tls_expiry_check.sh`, `page200_check.sh`, `ops_drift_check.sh`, `rules_drift_check.sh` |

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

## The backend-code deploy pipeline (`ops/push-backend.sh`, per site repo)

**Gap found and fixed 2026-09-02.** Each property's `ops/push-to-staging.sh`
(site repo) + `/root/deploy.sh` (VPS) two-hop pipeline only ever syncs
`public/`. The VPS's running `index.js` for all three properties had always
been whatever was last hand-`scp`'d there, completely independent of what
was committed in each repo — discovered when a committed `/contact` route
fix went through the full `public/`-only pipeline successfully and still
404'd live, because the pipeline never touched the actual running backend.
That specific incident was fixed by hand, outside any pipeline
(`index.js.bak-pre-contact-route-20260902*` on the VPS is that manual fix's
backup trail). This section documents the general fix: a real pipeline for
backend code, going forward.

**What ships now, per property, and how:**

| What | Mechanism | Where |
|---|---|---|
| `public/` (many files, `--delete` matters) | `ops/push-to-staging.sh <domain>` (repo → VPS staging) then `ssh root@74.208.181.10 '/root/deploy.sh <domain>'` (VPS staging → VPS live) | Each site repo's own `ops/` |
| `index.js`, `package.json` (fixed two-file list, no `--delete`, no staging hop) | `ops/push-backend.sh <domain>` — straight to the VPS live directory | Each site repo's own `ops/`, identical copy in DCI/GCI/LGM (confirmed byte-identical across all three 2026-09-02), same per-property-copy convention `push-to-staging.sh` already uses |

**Why `push-backend.sh` doesn't reuse the `public/` two-hop shape:**
`public/` is dozens of files where `--delete` matters (a retired page must
vanish live) and a staging look-before-mirror step earns its keep. Backend
code here is a fixed two-file allowlist — `--delete` is meaningless on a
named-file list, and the equivalent "look before you leap" property comes
from a per-file md5 diff (nothing touches the VPS unless it actually
changed) plus a mandatory `node --check` syntax gate before any restart.
Modeled directly on `scripts/deploy_ops_to_vps.sh`'s per-file
backup+scp+md5-verify pattern instead — that script's shape fits a small
fixed file list going straight to a live path, which is exactly this
problem; `push-to-staging.sh`'s shape does not.

**What `push-backend.sh <domain> [--dry-run]` does, per file (`index.js`,
`package.json`):**
1. Refuses outright if its own fixed file list ever contains `.env` or any
   other name on an explicit denylist — checked before anything else runs,
   so a future edit to the file list can't silently start shipping secrets
   (Rule 5 territory: shipping the `.env` FILE isn't quite "reading a
   secret's value," but is treated with the same seriousness).
2. `md5` (local) vs `md5sum` (VPS) each file — skips it entirely if they
   already match. No needless restarts on a no-op run.
3. For `index.js` only, if it differs: `node --check` on the local file
   first. A broken file must never overwrite a running service. (Verified
   this actually catches a broken file, not just assumed the flag works:
   `node --check` on a deliberately truncated fixture exits 1 with a
   `SyntaxError`; on a valid file it exits 0.)
4. Backs up the VPS copy before overwriting — `<file>.bak-pre-deploy-<full
   timestamp>`, this portfolio's established `.bak-<reason>-<date>`
   convention, same as `deploy_ops_to_vps.sh`.
5. `scp`s the file over, then re-`md5sum`s the VPS copy and refuses (exits
   nonzero, already-written backup still in place) if it doesn't match the
   local file exactly.
6. Restarts `<domain>.service` via `systemctl restart` **only if `index.js`
   was in the changed set** — a `package.json`-only change never restarts
   anything, since `node_modules/` isn't touched by this script and the
   running process already has whatever it loaded at last start. Confirms
   `systemctl is-active` after restarting and fails loudly if it isn't.

**What this deliberately still does NOT ship, and why:**
- **`.env` / any secrets file** — never, by explicit denylist (see step 1
  above), not merely by omission from an inclusion list.
- **`node_modules/`** — confirmed 2026-09-02: every package all three
  properties' `index.js` actually `require()`s (`express`, `pg`, `dotenv`,
  `express-rate-limit`, `@sendgrid/mail`) was already installed on the VPS
  at a version satisfying that property's own `package.json` semver range —
  no missing dependency, no live risk today. Installing packages is a
  separate, materially riskier, network-dependent operation (can fail
  non-atomically mid-install, needs VPS internet egress, isn't reversible
  by a simple file restore) that this script deliberately does not
  automate. If a future `index.js` adds a genuinely new dependency,
  `npm install <pkg>` on the VPS stays a manual, deliberate step — this
  script only keeps `index.js` and `package.json` themselves in sync with
  the repo. (One real, harmless finding from the same 2026-09-02 audit: the
  VPS's DCI `package.json` had accumulated a `puppeteer-core` entry — and a
  matching installed package — never present in the DCI repo's own
  `package.json`; not required by `index.js`'s `require()` list, so
  orphaned but inert. `push-backend.sh`'s `package.json` sync overwrites the
  VPS's manifest text to match the repo exactly; it does not touch
  `node_modules/`, so the orphaned package is simply no longer *declared*,
  not uninstalled.)
- **Any other per-repo `ops/` script** (`functional_proof.sh`,
  `live_token_check.sh`, `similarity_canary.sh`, plus DCI-only
  `browser_canary.js`/`canary_check.js`/`retention_cleanup.js`) — none of
  these are `require()`d by any property's `index.js` at runtime (confirmed
  by reading each `index.js`'s requires directly), so none is a deploy gap
  in the sense this pipeline closes. DCI's canary scripts already have a
  live VPS copy (deployed by hand at some point — VPS-side `.bak.<date>`
  files use a different naming convention than this pipeline's
  `.bak-pre-deploy-<timestamp>`, evidence of an earlier ad hoc `scp`); GCI's
  and LGM's equivalents have never been deployed to the VPS at all. Neither
  gap blocks the running Express service, so both are out of this pass's
  scope — flagged here for whoever picks up VPS-side canary tooling next.
- **The systemd unit files themselves**
  (`/etc/systemd/system/<domain>.service`) — not version-controlled in any
  repo, not touched by any deploy pipeline, set up once per property at
  initial VPS provisioning. `greeleycoloradoinsulation.com.service` is
  structurally different from DCI's/LGM's (no `Type=simple`/`User=root`, no
  `docker.service` dependency, `Restart=always` vs `on-failure`,
  `--env-file=.env` on the `ExecStart` line instead of `dotenv` doing it in
  code) — a pre-existing inconsistency, not something this pass introduced
  or needed to resolve to ship `index.js`/`package.json` correctly.

**How to deploy a backend change, going forward:**
```bash
cd <site-repo>                                    # DCI, GCI, or LGM
bash ops/push-backend.sh <full-domain> --dry-run   # inspect the plan first
bash ops/push-backend.sh <full-domain>             # backs up, syntax-checks
                                                    # index.js, deploys,
                                                    # md5-verifies, restarts
                                                    # only if index.js changed
```

**Live-proven 2026-09-02** (lane `backend-deploy-pipeline-gci`, full detail
in GCI's `docs/lanes.md`): closed real, pre-existing `package.json` drift on
all three properties (a `scripts`-field mismatch on all three, plus DCI's
orphaned `puppeteer-core` entry) with zero restarts (`index.js` unchanged on
that run, confirmed by `ActiveEnterTimestamp` unchanged before/after on
GCI/DCI/LGM). Then, on GCI only, a trivial one-line comment added to
`index.js`, deployed for real (backup written, `node --check` passed,
`scp`+md5-verify passed, `systemctl restart` fired, `is-active` confirmed,
clean `journalctl` boot, live homepage `200`), then reverted to the exact
original file (confirmed byte-identical to the pre-change committed
`index.js` via `git diff` before redeploying) and deployed again through the
same mechanism — final live `index.js` md5 matches the original committed
file exactly, service healthy, homepage `200`. GCI ends this pass
byte-identical to how it started on `index.js`; `package.json` on all three
properties is now a deliberate, permanent sync (real drift closed, not a
test artifact).

## The extended deploy-drift check

`scripts/monitoring/deploy_drift_check.sh` (per-property, wired into
`daily_checks.sh`, 07:00 daily via `r2daily`) already compared live
`index.js` and `public/` against each property's repo — it did **not** yet
know about `package.json`, the second file `push-backend.sh` ships. Extended
2026-09-02 with the identical `scp`+`cmp` pattern already used for
`index.js` (fetch the live copy, `cmp -s` against the repo, append to
`diffs` on mismatch or missing), through the same `_mon_lib.sh`
`handle_check_result`/`send_alert` machinery every check in this directory
uses — same per-property consecutive-failure counting
(`CONSECUTIVE_FAILURE_THRESHOLD=2`), same per-day suppression, same
recovery-on-next-clean-run, same VPS-side sender (`send_alert.sh` →
`send_alert.js` → `DIRECTOR_ALERT_EMAIL`), never a new alert channel.
`node_modules/` is deliberately NOT compared — it's never shipped by
`push-backend.sh` (see above), so comparing it would alert on an expected,
permanent difference between a dev machine and the VPS, not a real drift.

**Verified live, 2026-09-02, before the fix above:** the extended check
correctly detected the real `package.json` drift then still live on DCI and
LGM (failure count went to 1 for each — below the 2-run alert threshold, by
design, so no alert fired on a single run) while reporting GCI clean (GCI's
`package.json` had already been synced). After deploying the fix to DCI and
LGM, a re-run left zero drift-check state files for any property — fully
clean across all three.

## The rules pipeline (`~/.claude/context/rules.md`)

**Gap found and fixed 2026-09-02.** `~/.claude/context/rules.md` — the file
`~/.claude/hooks/h01_session_start.sh`'s `SessionStart` hook tells every
Claude Code session to load — was copied from this file's Rules 1-9 block
once, early on, and never kept in sync. It held only Rules 1-4 (plus the
kickoff-decomposition block sourced from `~/.claude/CLAUDE.md`). Rules 5
(secrets), 6 (look-it-up), 7 (this paperwork rule), 8 (process-vs-problem),
and 9 (the Final Report rule) had been added to this file's Rules 1-9 block
and never once reached any session on this machine. Rule 1's own copy had
also drifted: canon's 1m had grown a trailing cross-reference sentence
("RULE 6 COVERS THE GUESSING SIDE OF THIS IN FULL...") that rules.md's copy
lacked.

**Fix — two pieces, mirroring the `ops/` pattern above:**

| Component | Location | What it is |
|---|---|---|
| Sync script | `~/.claude/hooks/sync_rules_from_canon.sh` — **not in this repo**, local-machine config | Regenerates `~/.claude/context/rules.md` from this file's Rules 1-9 block (everything above the `# ARCHITECT_DISCIPLINE.md` header, located by grep, never hardcoded) plus `~/.claude/CLAUDE.md`'s kickoff-decomposition section. Idempotent (no-op, no write, no backup file if content is already byte-identical); backs up the prior `rules.md` to `rules.md.bak-pre-sync-<date>` only when it actually changes something; fails loudly (stderr + exit 1) and leaves the existing `rules.md` completely untouched if canon's file is missing/unreadable or its expected structure isn't found. Deliberately never runs `git pull` — a `SessionStart` hook must not perform a network git operation that could hang or conflict; catching a stale local canon checkout is `rules_drift_check.sh`'s job below. |
| Hook wiring | `~/.claude/hooks/h01_session_start.sh` | Calls the sync script as its first step, before reading and injecting `rules.md`, so the file can never be stale at the moment it's loaded. On a sync failure it logs a `WARN` to `~/.claude/hooks/hook.log` and falls through to whatever `rules.md` already holds (last-known-good) — a session is never left with zero rules loaded. |
| Drift check | `scripts/monitoring/rules_drift_check.sh`, wired into `daily_checks.sh` (07:00 daily via `r2daily`) | Two checks in one: (1) is the local canon checkout behind `origin/main` (`git fetch` + `git rev-list --count HEAD..origin/main`); (2) does `~/.claude/context/rules.md` still contain canon's current Rules 1-9 text verbatim, independently re-derived from `ARCHITECT_DISCIPLINE.md` using the same header-boundary logic as the sync script (a separate re-implementation, so this check can catch the sync script itself being broken or bypassed, not just canon having moved). Routes through the same `_mon_lib.sh` `handle_check_result`/`send_alert` machinery as every other check here — same per-day suppression, same recovery-on-clean-run, same VPS-side sender (`send_alert.js` → `DIRECTOR_ALERT_EMAIL`), never a new alert channel. |

**Why a session-start regenerate instead of a git hook or a manual step:**
`~/.claude` is not a git repo (no post-merge/post-checkout hook is available
there), and a manual "remember to sync" step is exactly the failure mode
that produced the four-rules gap in the first place. Regenerating at the
top of every `SessionStart` means the file cannot be stale at the moment
it's read, at the cost of one cheap idempotent script run per session.

**Verified both directions, 2026-09-02:** a canary run of
`rules_drift_check.sh` against a deliberately corrupted `rules.md` (RULE 9
stripped) registered a consecutive-failure count of 1 (below the
shared 2-run alert threshold, by design — see the false-alert fix above);
restoring the correct `rules.md` and re-running cleared the count and
returned to silent/clean. A separate canary of the sync script itself
(pointed at a nonexistent canon file) failed loudly, left the real
`rules.md` byte-for-byte untouched, and — invoked exactly as `h01`'s
`SessionStart` hook would invoke it, via stdin JSON — produced a logged
`WARN` in `hook.log` while the hook still completed successfully and
injected the existing (correct) `rules.md` pointer, proving the fallback
path.

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
