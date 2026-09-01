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
'use strict';
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

  const alertScript = path.join(__dirname, 'send_alert.js');
  const isStale =
    canaryOkDays.length === STALE_DAYS_THRESHOLD &&
    leadsDaysWithActivity.length === 0 &&
    pageviewsDaysWithActivity.length === 0;

  if (!isStale) {
    execFileSync('node', [
      alertScript, prop.label, `no human traffic for ${STALE_DAYS_THRESHOLD}+ days`, 'recovered', 'stale-site', '--recovery',
    ], { stdio: 'ignore' });
    continue;
  }

  const body =
    `${prop.label}'s automated lead-path canary succeeded every day for the last ${STALE_DAYS_THRESHOLD} ` +
    `complete days (the submission path works), but zero real leads and zero real pageviews were recorded ` +
    `on any of those ${STALE_DAYS_THRESHOLD} days. For a brand-new site like this, the most likely explanation ` +
    `is simply that it doesn't have much organic/search traffic yet, not a technical failure -- these are new ` +
    `sites still building search visibility, not established sites that suddenly went dark. A DNS, CDN, or ` +
    `search-visibility check is worth doing as a secondary step, mainly if this pattern is unusual compared to ` +
    `the property's own recent traffic history rather than the default explanation.`;
  execFileSync('node', [
    alertScript, prop.label, `no human traffic for ${STALE_DAYS_THRESHOLD}+ days`, body, 'stale-site',
  ], { stdio: 'inherit' });
}
