#!/usr/bin/env node
// /root/ops/scripts/test_stale_site_check.js — verification harness for the
// 2026-09-06 state-transition-alerting rewrite of stale_site_check.js.
// Mirrors ops/test_send_alert.js's house style: comments explain WHY each
// case exists, not just what it does.
//
// Unlike test_send_alert.js, every case here runs in ONE process (not one
// process per case via `node test_stale_site_check.js <case>`). That
// harness's per-process-plus-require.cache-poison design exists because
// send_alert.js's real-send path (SendGrid) is a genuine hazard if reached
// accidentally, and poisoning require.cache only works cleanly once per
// process. stale_site_check.js has no such hazard: decideStreakTransition()
// never requires anything network- or SendGrid-adjacent, and this harness
// never lets it call the real send_alert.js at all (see next paragraph) --
// so there is nothing here that a poisoned require.cache would be
// protecting against, and running every case in one process lets the
// SEQUENCING case (below) share one fabricated state file across multiple
// simulated nights, which is the actual point of that case.
//
// invokeAlert is ALWAYS a capturing fake in this harness, never the real
// send_alert.js (with or without ALERT_TEST_MODE) -- deliberately, for two
// independent reasons: (1) send_alert.js's real-send path resolves
// per-property node_modules under /root/<property>.com/ on the VPS, which
// do not exist in this checkout, so invoking it for real here would fail
// for reasons unrelated to the logic under test; (2) decideStreakTransition
// is specifically designed (this pass's refactor) to take invokeAlert as a
// parameter precisely so tests do not need a real or test-mode send_alert.js
// at all -- capturing the call args IS the assertion surface for whether an
// alert would have fired, which is everything this rewrite needed to prove.
//
// State directory: every state file this harness reads or writes lives
// under a fresh os.tmpdir() scratch directory (STALE_SITE_STATE_DIR is
// never set to /root/ops/state, and this harness never even reads that env
// var -- statePathFor() is called directly with an explicit scratch dir
// argument), so a run of this harness can never touch real VPS state.
'use strict';
const fs = require('fs');
const os = require('os');
const path = require('path');
const assert = require('assert');

const {
  statePathFor,
  loadStreakState,
  shiftDateString,
  daysBetweenDateStrings,
  decideStreakTransition,
} = require('./stale_site_check.js');

const scratchDir = fs.mkdtempSync(path.join(os.tmpdir(), 'stale-site-check-test-'));

let passCount = 0;
function check(label, cond) {
  if (!cond) {
    console.error(`FAIL: ${label}`);
    process.exitCode = 1;
  } else {
    passCount++;
    console.log(`PASS: ${label}`);
  }
}

// Fabricated day-bucketed activity rows, in the same "date|count" shape
// psqlDataRows() returns from real queries.
const NO_ACTIVITY = [];
const HEALTHY_LEADS = ['2026-08-30|1'];
const HEALTHY_PAGEVIEWS = ['2026-08-29|2', '2026-08-30|3'];

// =====================================================================
// Case 1: single-property timeline, sequencing under test. Four
// consecutive simulated nights against ONE fabricated property state
// file, asserting the FULL entry -> continuing x2 -> recovery arc in
// order -- this is what actually distinguishes state-transition alerting
// from the old nightly-re-alert defect, so isolated single-call tests
// would not be enough proof by themselves.
// =====================================================================
console.log('\n--- Case 1: single-property timeline sequencing ---');
{
  const label = 'timelinepropertytest.example';
  const statePath = statePathFor('timeline_test_prop', scratchDir);
  const calls = [];
  const invokeAlert = (call) => calls.push(call);
  const threshold = 7;

  // Night 1 (2026-09-01): healthy, no prior streak (no state file exists
  // yet) -> expect a true no-op. This also exercises the "missing state
  // file" default-safe path (see stale_site_check.js's loadStreakState:
  // a read/parse failure returns inStreak:false, never a crash).
  {
    const result = decideStreakTransition({
      label,
      isStale: false,
      today: '2026-09-01',
      streakDaysThreshold: threshold,
      leadsDaysWithActivity: HEALTHY_LEADS,
      pageviewsDaysWithActivity: HEALTHY_PAGEVIEWS,
      statePath,
      invokeAlert,
    });
    check('night 1 (healthy, no prior streak): action is "none"', result.action === 'none');
    check('night 1: zero alert calls', calls.length === 0);
    check('night 1: state still reads not-in-streak (no file written)', loadStreakState(statePath).inStreak === false);
  }

  // Night 2 (2026-09-02): newly qualifies as stale -> ENTRY. Exactly one
  // alert, and the streak start date must be the first day of the
  // detected zero window (today - threshold), NOT the run date itself.
  {
    const result = decideStreakTransition({
      label,
      isStale: true,
      today: '2026-09-02',
      streakDaysThreshold: threshold,
      leadsDaysWithActivity: NO_ACTIVITY,
      pageviewsDaysWithActivity: NO_ACTIVITY,
      statePath,
      invokeAlert,
    });
    const expectedSince = shiftDateString('2026-09-02', -threshold);
    check('night 2 (newly stale): action is "entry"', result.action === 'entry');
    check('night 2: exactly one alert call total', calls.length === 1);
    check('night 2: alert is non-recovery', calls[0].isRecovery === false);
    check('night 2: recorded since date is today-minus-threshold, not the run date', result.since === expectedSince);
    const state = loadStreakState(statePath);
    check('night 2: state now in-streak', state.inStreak === true);
    check('night 2: state since matches window start', state.since === expectedSince);
  }

  // Nights 3 and 4 (2026-09-03, 2026-09-04): still stale, streak already
  // recorded -> CONTINUING, silent both times. Zero additional alert
  // calls after either night, and state (in particular `since`) must not
  // change.
  for (const today of ['2026-09-03', '2026-09-04']) {
    const beforeState = loadStreakState(statePath);
    const result = decideStreakTransition({
      label,
      isStale: true,
      today,
      streakDaysThreshold: threshold,
      leadsDaysWithActivity: NO_ACTIVITY,
      pageviewsDaysWithActivity: NO_ACTIVITY,
      statePath,
      invokeAlert,
    });
    check(`night ${today} (continuing streak): action is "continuing"`, result.action === 'continuing');
    check(`night ${today}: alert call count unchanged at 1`, calls.length === 1);
    const afterState = loadStreakState(statePath);
    check(`night ${today}: state unchanged (same since date)`, afterState.since === beforeState.since);
    check(`night ${today}: state still in-streak`, afterState.inStreak === true);
  }

  // Night 5 (2026-09-05): traffic returns -> RECOVERY. Exactly one more
  // alert (total 2), body must name the duration, the start date, and the
  // concrete returned-traffic figures (day counts AND totals, not just
  // "some traffic returned"), and state must clear.
  {
    const returnedLeads = ['2026-09-01|2', '2026-09-03|1']; // 2 days, 3 leads total
    const returnedPageviews = ['2026-09-01|5', '2026-09-02|3', '2026-09-03|4']; // 3 days, 12 pageviews total
    const priorSince = loadStreakState(statePath).since;
    const result = decideStreakTransition({
      label,
      isStale: false,
      today: '2026-09-05',
      streakDaysThreshold: threshold,
      leadsDaysWithActivity: returnedLeads,
      pageviewsDaysWithActivity: returnedPageviews,
      statePath,
      invokeAlert,
    });
    const expectedDuration = daysBetweenDateStrings(priorSince, '2026-09-05');
    check('night 5 (recovery): action is "recovery"', result.action === 'recovery');
    check('night 5: exactly one additional alert call (2 total)', calls.length === 2);
    check('night 5: alert is a recovery alert', calls[1].isRecovery === true);
    const body = calls[1].body;
    check('night 5: body names the streak start date', body.includes(priorSince));
    check('night 5: body names the duration in days', body.includes(String(expectedDuration)));
    check('night 5: body names lead-activity day count (2)', body.includes('2 day(s) had lead activity'));
    check('night 5: body names lead total (3)', body.includes('3 real lead(s) total'));
    check('night 5: body names pageview-activity day count (3)', body.includes('3 day(s) had pageview activity'));
    check('night 5: body names pageview total (12)', body.includes('12 pageview(s) total'));
    const state = loadStreakState(statePath);
    check('night 5: state cleared (not in streak)', state.inStreak === false);
    check('night 5: state since cleared to null', state.since === null);
  }
}

// =====================================================================
// Case 2: property independence. One property (GCI-shaped) is ALREADY
// mid-streak; a second (DCI-shaped) is healthy and newly qualifies as
// stale in the SAME pass. Each must use its own state file/key, so GCI's
// in-progress streak must never suppress or otherwise affect DCI's entry,
// and DCI's entry must never touch GCI's state. This is one of the
// kickoff's four required transitions ("a second property entering a
// streak fires independently").
// =====================================================================
console.log('\n--- Case 2: property independence (GCI continuing, DCI entering, same pass) ---');
{
  const gciLabel = 'greeleycoloradoinsulation.com';
  const dciLabel = 'denvercoloradoinsulation.com';
  const gciStatePath = statePathFor('greeley_insulation', scratchDir);
  const dciStatePath = statePathFor('insulation', scratchDir);

  // Seed GCI as already mid-streak (independent of Case 1's state file --
  // different path, different db key).
  fs.mkdirSync(path.dirname(gciStatePath), { recursive: true });
  fs.writeFileSync(gciStatePath, JSON.stringify({ inStreak: true, since: '2026-08-28', lastAlerted: '2026-08-28' }));
  // DCI has no state file at all -- exercising the same missing-file ->
  // not-in-streak default as Case 1's night 1, on a different property.

  const calls = [];
  const invokeAlert = (call) => calls.push(call);
  const today = '2026-09-06';
  const threshold = 7;

  const gciResult = decideStreakTransition({
    label: gciLabel,
    isStale: true, // GCI's real production state as of this kickoff
    today,
    streakDaysThreshold: threshold,
    leadsDaysWithActivity: NO_ACTIVITY,
    pageviewsDaysWithActivity: NO_ACTIVITY,
    statePath: gciStatePath,
    invokeAlert,
  });
  const dciResult = decideStreakTransition({
    label: dciLabel,
    isStale: true, // newly qualifies in this same pass
    today,
    streakDaysThreshold: threshold,
    leadsDaysWithActivity: NO_ACTIVITY,
    pageviewsDaysWithActivity: NO_ACTIVITY,
    statePath: dciStatePath,
    invokeAlert,
  });

  check('GCI (already in streak): action is "continuing"', gciResult.action === 'continuing');
  check('DCI (newly stale, same pass): action is "entry"', dciResult.action === 'entry');
  check('exactly one alert call total across both properties', calls.length === 1);
  check('the one alert call is for DCI, not GCI', calls[0].label === dciLabel);
  check('GCI state unchanged (still since 2026-08-28)', loadStreakState(gciStatePath).since === '2026-08-28');
  check('DCI state now in-streak on its OWN file', loadStreakState(dciStatePath).inStreak === true);
  check(
    'GCI and DCI state files are distinct paths',
    gciStatePath !== dciStatePath
  );
}

console.log(`\n${passCount} assertion(s) passed.`);
if (process.exitCode) {
  console.error('\nONE OR MORE ASSERTIONS FAILED.');
} else {
  console.log('\nALL ASSERTIONS PASSED.');
}

// Best-effort scratch cleanup -- not load-bearing for the test result.
try {
  fs.rmSync(scratchDir, { recursive: true, force: true });
} catch (_) {
  // ignore
}
