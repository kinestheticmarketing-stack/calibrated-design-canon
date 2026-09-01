#!/usr/bin/env node
// /root/ops/scripts/unhandled_lead_check.js — alerts when a REAL (non-canary)
// lead has sat in `leads` for more than 15 minutes with `delivered != true`.
// This is the check that costs real money when it fires: a genuine homeowner
// lead silently dropped. Alert body carries only the lead's date and source
// page -- never name/email/phone.
//
// Stale-30d threshold (2026-08-31, portfolio R3): this check previously had
// no floor -- a lead marked delivered != TRUE alerted forever, every 15
// minutes, indefinitely, with no way to close it out short of deleting the
// row (which we never do). Before alerting, any real lead older than 30 days
// that has never been delivered is now marked closed_reason = 'stale-30d'
// (an additive, nullable column on `leads` in all three repos' ensureSchema())
// and excluded from the alert going forward. The row is NEVER deleted --
// closed_reason is a status marker only, so `SELECT count(*) FROM leads
// WHERE canary = FALSE` is unaffected. A lead under 30 days old that is
// undelivered still alerts exactly as before -- that's the case worth money.
'use strict';
const path = require('path');
const { execFileSync } = require('child_process');

const PROPERTIES = [
  { db: 'insulation', label: 'denvercoloradoinsulation.com' },
  { db: 'longmont_insulation', label: 'longmontcoloradoinsulation.com' },
  { db: 'greeley_insulation', label: 'greeleycoloradoinsulation.com' },
];

// Matches the command-completion tag psql prints after INSERT/UPDATE/DELETE
// (e.g. "UPDATE 3") even in -t (tuples-only) mode when a RETURNING clause is
// present. Filtered out so it's never mistaken for a data row.
const COMMAND_TAG_RE = /^(INSERT \d+ \d+|UPDATE \d+|DELETE \d+|SELECT \d+)$/;

function psql(db, sql) {
  const out = execFileSync(
    'docker',
    ['exec', 'porter-db-1', 'psql', '-U', 'porter', '-d', db, '-t', '-A', '-F', '\t', '-c', sql],
    { encoding: 'utf8' }
  );
  return out
    .trim()
    .split('\n')
    .filter(Boolean)
    .filter((l) => !COMMAND_TAG_RE.test(l))
    .map((l) => l.split('\t'));
}

for (const prop of PROPERTIES) {
  // Step 1: close out anything older than 30 days that was never delivered
  // and isn't already closed. RETURNING lets us log exactly what got closed.
  let closed;
  try {
    closed = psql(
      prop.db,
      `UPDATE leads
         SET closed_reason = 'stale-30d'
       WHERE canary = FALSE AND (delivered IS DISTINCT FROM TRUE)
         AND closed_reason IS NULL
         AND created_at < now() - interval '30 days'
       RETURNING id, created_at, coalesce(source_page, '(not recorded)')`
    );
  } catch (e) {
    console.error(`[unhandled-lead] stale-close UPDATE failed for ${prop.label}:`, e.message);
    closed = [];
  }
  if (closed.length > 0) {
    for (const [id, created, page] of closed) {
      console.log(`[unhandled-lead] ${prop.label}: closed lead #${id} (created ${created}, source: ${page}) as closed_reason='stale-30d' (>30 days, never delivered)`);
    }
  }

  // Step 2: alert on whatever's left -- undelivered, not canary, older than
  // 15 minutes, and not already closed stale. closed_reason IS NULL is
  // belt-and-suspenders here (step 1 already closed anything >30 days old
  // in this same run) but keeps the query correct on its own if step 1 ever
  // fails or the ordering changes.
  let rows;
  try {
    rows = psql(
      prop.db,
      `SELECT created_at, coalesce(source_page, '(not recorded)') FROM leads
       WHERE canary = FALSE AND (delivered IS DISTINCT FROM TRUE)
         AND closed_reason IS NULL
         AND created_at < now() - interval '15 minutes'
       ORDER BY created_at DESC`
    );
  } catch (e) {
    console.error(`[unhandled-lead] query failed for ${prop.label}:`, e.message);
    continue;
  }
  const alertScript = path.join(__dirname, 'send_alert.js');
  if (rows.length === 0) {
    // silent on success -- send_alert.js's own recovery logic is a no-op
    // when there was nothing failing to recover from, so this call is safe
    // to make unconditionally; it only actually sends when a prior failure
    // needs a recovery notice.
    execFileSync('node', [
      alertScript, prop.label,
      'unhandled lead(s) detected', 'recovered', 'unhandled-lead', '--recovery',
    ], { stdio: 'ignore' });
    continue;
  }
  const list = rows.map(([created, page]) => `  - ${created} (source: ${page})`).join('\n');
  const body =
    `${rows.length} real lead(s) on ${prop.label} have been in the database for ` +
    `more than 15 minutes without being marked delivered. This can mean a homeowner's ` +
    `submission was silently lost -- check the notifier and SendGrid delivery for these:\n\n${list}`;
  execFileSync('node', [
    alertScript, prop.label, 'unhandled lead(s) detected', body, 'unhandled-lead',
  ], { stdio: 'inherit' });
}
