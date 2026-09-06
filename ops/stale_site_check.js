#!/usr/bin/env node
// /root/ops/scripts/stale_site_check.js — alerts if a run of consecutive,
// COMPLETE calendar days (America/Denver) passes where the daily
// lead-canary succeeded every one of those days (proving the submission
// path works) but zero real leads and zero real pageviews were recorded on
// EVERY one of those days. That pattern means the site is technically up
// and functioning, but unreachable by actual humans -- a different,
// quieter failure mode than downtime. Runs once daily at 23:00
// America/Denver, after the day that just ended (yesterday, relative to
// run time) is fully closed out and the lead-canary has had a chance to
// run for it.
//
// --- History / why this looks the way it does (2026-08-31 revision) ---
//   - Originally checked `current_date` (i.e. TODAY, as of whenever the
//     cron fired) instead of a complete prior day. At ~5-6 pageviews/day
//     portfolio-wide, a partial-day window reads zero most days purely
//     from timing, independent of real traffic health. Fixed by requiring
//     COMPLETE days only (the window below never includes today).
//   - Also found: Postgres's session timezone defaults to UTC
//     (`SHOW timezone` -> Etc/UTC) while the VPS itself runs
//     America/Denver (`timedatectl` -> America/Denver). Since
//     pageviews.viewed_at / leads.created_at / lead_submissions_log.created_at
//     are all `timestamp with time zone`, casting to `::date` under a UTC
//     session silently bucketed rows into UTC calendar days -- given the
//     23:00 MDT run time (05:00 UTC the next day), that meant the "today"
//     window covered only ~5 hours of actual Denver-local time (roughly
//     6pm-11pm), not a day at all. Fixed by opening every query with
//     `SET timezone='America/Denver'` so day boundaries match the VPS's
//     actual clock and the business's actual days.
//   - Threshold: was a single day at zero. Picked STALE_DAYS_THRESHOLD from
//     real data (queried 45 days of pageview history per property on
//     2026-08-31). All three properties are brand-new, low-traffic sites
//     (roughly 1-4 pageviews/day, some days more, many days one or zero).
//     greeley_insulation had a genuine 3-CONSECUTIVE-complete-zero-day run
//     (Aug 15-17) in its short history that was normal low-traffic
//     variance, not an outage -- and was in the middle of another 3+ day
//     gap (Aug 28-30) as of this writing. A same-order-of-magnitude
//     threshold (e.g. 2-3 days) would already have false-alarmed on
//     ordinary traffic noise for this property. STALE_DAYS_THRESHOLD=7 (a
//     full week of complete days, all individually zero) gives >2x margin
//     over the largest gap actually observed in the data, while still
//     surfacing a genuine silent failure within about a week of it
//     starting. Each of the N days is checked individually (GROUP BY date,
//     row-count comparisons below) -- a script that summed N days and
//     checked the sum would let partial-traffic days mask a problem, or
//     vice versa, which is not equivalent and not what's implemented here.
//   - Alert body: previously led with "worth checking for a DNS, CDN, or
//     search-visibility problem rather than a code/server outage", which
//     presumes a technical failure. At this traffic volume, on sites this
//     new, the far more likely explanation for a zero-traffic stretch --
//     even a real multi-day one -- is simply that the site doesn't have
//     much organic traffic yet. Reworded to lead with that and treat a
//     DNS/CDN check as a secondary step, only worth it if the pattern is
//     unusual for that property's own recent history.
//
// --- 2026-09-06 revision: nightly re-alerting -> state-transition alerting ---
//   The isStale computation above was and remains CORRECT (Director
//   ruling): a property can genuinely have zero human visitors for 7+
//   straight days while its canary keeps proving the submission path
//   works, and that is worth surfacing. The DEFECT was cadence, not
//   correctness: this script runs once a night, and every night the
//   streak continued it re-sent the IDENTICAL alert, because
//   send_alert.js's own suppression is keyed on calendar date ("already
//   alerted TODAY?") and a new night is always a new "today" -- a no-op
//   gate for a once-daily caller. Fixed by giving this script its OWN
//   per-property streak state (independent of send_alert.js's internal
//   per-day state, which is still written as a side effect but no longer
//   read as a gate for this check): a JSON file per property under
//   /root/ops/state/ recording whether that property is currently inside
//   a qualifying streak and the Denver date it began. Alerts now fire
//   exactly twice per real event -- once on ENTRY (the night the 7-day
//   zero window first completes) and once on RECOVERY (the first night
//   real traffic reappears) -- and stay silent every night in between,
//   however long the streak runs. Every call into send_alert.js now
//   passes --force, since this script's own transition-gate is the sole
//   authority on whether tonight's run should send anything; depending on
//   send_alert.js's per-day gate as well would be redundant at best and
//   silently wrong at worst (it would even let a same-day duplicate CLI
//   invocation slip through unsuppressed on the entry/recovery nights,
//   since --force skips that gate entirely by design -- acceptable here
//   because this script only ever calls send_alert.js once per property
//   per run, and at most once per night).
'use strict';
const fs = require('fs');
const path = require('path');
const { execFileSync } = require('child_process');

const PROPERTIES = [
  { db: 'insulation', label: 'denvercoloradoinsulation.com' },
  { db: 'longmont_insulation', label: 'longmontcoloradoinsulation.com' },
  { db: 'greeley_insulation', label: 'greeleycoloradoinsulation.com' },
];

// Consecutive complete zero-traffic days (America/Denver) required before
// alerting. See history note above for how this number was picked.
const STALE_DAYS_THRESHOLD = 7;

// Runs `sql` (which may itself be several ;-separated statements) inside a
// psql session pinned to America/Denver, and returns the data rows (lines
// containing '|') from the LAST statement's tuples-only output. Filters
// out non-data lines (e.g. the "SET" command tag psql prints for the
// timezone statement).
function psqlDataRows(db, sql) {
  const out = execFileSync(
    'docker',
    ['exec', 'porter-db-1', 'psql', '-U', 'porter', '-d', db, '-t', '-A', '-c', `SET timezone='America/Denver'; ${sql}`],
    { encoding: 'utf8' }
  );
  return out
    .split('\n')
    .map((l) => l.trim())
    .filter((l) => l.includes('|'));
}

// Window is the last STALE_DAYS_THRESHOLD COMPLETE days -- i.e. it never
// includes today, only fully-closed Denver calendar days ending yesterday.
const WINDOW_WHERE = (col) =>
  `${col}::date >= current_date - interval '${STALE_DAYS_THRESHOLD} days' AND ${col}::date < current_date`;

// --- Denver calendar-date helpers (matching send_alert.js's own convention:
// America/Denver, not UTC, and not the VPS's ambient tz assumption, so this
// keeps working correctly even if that ever changes) ---
function denverDateString(d) {
  return new Intl.DateTimeFormat('en-CA', { timeZone: 'America/Denver' }).format(d); // en-CA -> YYYY-MM-DD
}

// Pure calendar-date arithmetic on a YYYY-MM-DD string -- deliberately NOT
// timezone-aware (parses/formats as UTC internally) because at this point
// we already have a Denver-local date STRING; shifting it by N days is a
// calendar operation, not a moment-in-time conversion, so re-involving a
// timezone here would be a category error, not extra correctness.
function shiftDateString(dateStr, days) {
  const d = new Date(dateStr + 'T00:00:00Z');
  d.setUTCDate(d.getUTCDate() + days);
  return d.toISOString().slice(0, 10);
}

function daysBetweenDateStrings(startStr, endStr) {
  const start = new Date(startStr + 'T00:00:00Z');
  const end = new Date(endStr + 'T00:00:00Z');
  return Math.round((end - start) / 86400000);
}

// psqlDataRows rows are "date|count" strings; sums the count column across
// all rows (used for the recovery notice's concrete traffic figures).
function sumCounts(rows) {
  return rows.reduce((sum, row) => {
    const n = parseInt(row.split('|')[1], 10);
    return sum + (Number.isFinite(n) ? n : 0);
  }, 0);
}

// --- Per-property streak state ---
// One JSON file per property, keyed by the property's `db` value (stable,
// dot-free, already unique -- unlike `label`, which contains dots). Lives
// under /root/ops/state/, the existing convention for this portfolio's
// runtime alerting state (gitignored, VPS-only -- see TOOLING_RUNBOOK.md).
// Overridable via STALE_SITE_STATE_DIR so tests never touch real state.
function stateDirFor() {
  return process.env.STALE_SITE_STATE_DIR || '/root/ops/state';
}

function statePathFor(dbKey, stateDir) {
  return path.join(stateDir || stateDirFor(), `stale-site-streak-${dbKey}.json`);
}

// Missing or unparseable state file -> "not in streak", never a crash. This
// is the deliberate safe default: a freshly-initialized or corrupted state
// file must never itself be mistaken for an active streak.
function loadStreakState(statePath) {
  try {
    const raw = JSON.parse(fs.readFileSync(statePath, 'utf8'));
    return { inStreak: !!raw.inStreak, since: raw.since || null, lastAlerted: raw.lastAlerted || null };
  } catch (_) {
    return { inStreak: false, since: null, lastAlerted: null };
  }
}

function saveStreakState(statePath, state) {
  fs.mkdirSync(path.dirname(statePath), { recursive: true });
  fs.writeFileSync(statePath, JSON.stringify(state, null, 2));
}

// The testable core: given isStale, the day-bucketed activity rows, a state
// file path, and an alert-invoker function, decides whether tonight's run
// for ONE property is an ENTRY, a CONTINUING (silent) night, a RECOVERY, or
// a quiet no-op -- and performs exactly that action. Takes no dependency on
// Postgres or the real send_alert.js call, so it can be exercised directly
// with fabricated inputs and a capturing invokeAlert.
//
// invokeAlert({ label, isRecovery, subjectFragment, body }) is the sole
// side-effecting call this function makes when it decides to send.
function decideStreakTransition({
  label,
  isStale,
  today,
  streakDaysThreshold,
  leadsDaysWithActivity,
  pageviewsDaysWithActivity,
  statePath,
  invokeAlert,
}) {
  const prior = loadStreakState(statePath);

  if (isStale) {
    if (prior.inStreak) {
      // CONTINUING: already alerted on entry, streak hasn't broken yet.
      // Deliberately silent -- no send_alert.js call at all. Logged so a
      // silent night has an explanation somewhere in the journal.
      console.log(
        `[stale-site] ${label}: still in zero-traffic streak since ${prior.since} -- ` +
          `suppressing repeat alert by design (state-transition alerting, not a bug).`
      );
      return { action: 'continuing', since: prior.since };
    }
    // ENTRY: streak just started as of tonight's run. The streak's start
    // date is the first day of the currently-detected zero window (today
    // minus the threshold), not the run date -- matching WINDOW_WHERE's own
    // date arithmetic.
    const since = shiftDateString(today, -streakDaysThreshold);
    const body =
      `${label}'s automated lead-path canary succeeded every day for the last ${streakDaysThreshold} ` +
      `complete days (the submission path works), but zero real leads and zero real pageviews were recorded ` +
      `on any of those ${streakDaysThreshold} days. For a brand-new site like this, the most likely explanation ` +
      `is simply that it doesn't have much organic/search traffic yet, not a technical failure -- these are new ` +
      `sites still building search visibility, not established sites that suddenly went dark. A DNS, CDN, or ` +
      `search-visibility check is worth doing as a secondary step, mainly if this pattern is unusual compared to ` +
      `the property's own recent traffic history rather than the default explanation. This is a one-time entry ` +
      `notice for this streak (began ${since}); it will stay silent while the streak continues and send exactly ` +
      `one recovery notice when real traffic returns.`;
    invokeAlert({
      label,
      isRecovery: false,
      subjectFragment: `no human traffic for ${streakDaysThreshold}+ days`,
      body,
    });
    saveStreakState(statePath, { inStreak: true, since, lastAlerted: today });
    return { action: 'entry', since };
  }

  if (!prior.inStreak) {
    // Healthy, and no streak was ever in progress -- nothing to do, nothing
    // to send. (Behavior change from the old unconditional recovery call:
    // now the caller itself is the gate, so a no-op stays a true no-op.)
    return { action: 'none' };
  }

  // RECOVERY: a streak was in progress and tonight it's no longer stale.
  const durationDays = daysBetweenDateStrings(prior.since, today);
  const leadDayCount = leadsDaysWithActivity.length;
  const pageviewDayCount = pageviewsDaysWithActivity.length;
  const leadTotal = sumCounts(leadsDaysWithActivity);
  const pageviewTotal = sumCounts(pageviewsDaysWithActivity);
  const body =
    `${label}'s zero-human-traffic streak has ended. It began ${prior.since} and ran ${durationDays} ` +
    `complete day(s) before recovering. In the current ${streakDaysThreshold}-day window, real traffic ` +
    `returned: ${leadDayCount} day(s) had lead activity (${leadTotal} real lead(s) total), and ` +
    `${pageviewDayCount} day(s) had pageview activity (${pageviewTotal} pageview(s) total).`;
  invokeAlert({
    label,
    isRecovery: true,
    subjectFragment: `no human traffic for ${streakDaysThreshold}+ days`,
    body,
  });
  saveStreakState(statePath, { inStreak: false, since: null, lastAlerted: today });
  return { action: 'recovery', since: prior.since, durationDays };
}

// Real alert-invoker: the only place this file shells out to send_alert.js.
// Always --force, since decideStreakTransition is now the sole authority on
// whether to send -- see the 2026-09-06 revision note at the top of this
// file for why depending on send_alert.js's own per-day gate as well would
// be redundant/wrong for a once-daily caller.
function realInvokeAlert({ label, isRecovery, subjectFragment, body }) {
  const alertScript = path.join(__dirname, 'send_alert.js');
  const args = [alertScript, label, subjectFragment, body, 'stale-site'];
  if (isRecovery) args.push('--recovery');
  args.push('--force');
  execFileSync('node', args, { stdio: 'inherit' });
}

// Real path: queries Postgres for each property, then hands the results to
// decideStreakTransition with the real state dir and the real alert
// invoker. Only runs when this file is executed directly (`node
// stale_site_check.js`), not when required by a test harness.
function main() {
  const stateDir = stateDirFor();
  const today = denverDateString(new Date());

  for (const prop of PROPERTIES) {
    let canaryOkDays, leadsDaysWithActivity, pageviewsDaysWithActivity;
    try {
      // One row per distinct day the canary succeeded in the window --
      // must equal STALE_DAYS_THRESHOLD (every single day covered) for the
      // "site is technically up throughout" precondition to hold.
      canaryOkDays = psqlDataRows(
        prop.db,
        `SELECT created_at::date, count(*) FROM lead_submissions_log
           WHERE canary = TRUE AND sendgrid_result LIKE 'accepted:%' AND ${WINDOW_WHERE('created_at')}
           GROUP BY 1 ORDER BY 1;`
      );
      // Any row here means at least one real lead landed on that day --
      // for a stale alert we need ZERO rows across the whole window.
      leadsDaysWithActivity = psqlDataRows(
        prop.db,
        `SELECT created_at::date, count(*) FROM leads
           WHERE canary = FALSE AND ${WINDOW_WHERE('created_at')}
           GROUP BY 1 ORDER BY 1;`
      );
      pageviewsDaysWithActivity = psqlDataRows(
        prop.db,
        `SELECT viewed_at::date, count(*) FROM pageviews
           WHERE ${WINDOW_WHERE('viewed_at')}
           GROUP BY 1 ORDER BY 1;`
      );
    } catch (e) {
      console.error(`[stale-site] query failed for ${prop.label}:`, e.message);
      continue;
    }

    const isStale =
      canaryOkDays.length === STALE_DAYS_THRESHOLD &&
      leadsDaysWithActivity.length === 0 &&
      pageviewsDaysWithActivity.length === 0;

    decideStreakTransition({
      label: prop.label,
      isStale,
      today,
      streakDaysThreshold: STALE_DAYS_THRESHOLD,
      leadsDaysWithActivity,
      pageviewsDaysWithActivity,
      statePath: statePathFor(prop.db, stateDir),
      invokeAlert: realInvokeAlert,
    });
  }
}

if (require.main === module) {
  main();
}

module.exports = {
  PROPERTIES,
  STALE_DAYS_THRESHOLD,
  WINDOW_WHERE,
  denverDateString,
  shiftDateString,
  daysBetweenDateStrings,
  sumCounts,
  statePathFor,
  loadStreakState,
  saveStreakState,
  decideStreakTransition,
  realInvokeAlert,
  main,
};
