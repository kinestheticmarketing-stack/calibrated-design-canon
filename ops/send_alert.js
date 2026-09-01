#!/usr/bin/env node
// /root/ops/scripts/send_alert.js — shared monitoring alert function.
// Usage: node send_alert.js <property> <subject-fragment> <body-text> [check-name] [--recovery] [--force] [--test-mode]
//
// Convention, matching ops/canary_check.js exactly:
//   - Recipient is DIRECTOR_ALERT_EMAIL only (config, never hardcoded to a
//     lead-routing/contractor address). Falls back to LEAD_NOTIFY_EMAIL's
//     established value if DIRECTOR_ALERT_EMAIL is unset, since that value
//     already IS the Director's own address in every existing property.
//   - One alert per (property, check-name) per calendar day: suppressed via
//     a state file in /root/ops/state/, until the check recovers, then one
//     recovery notice is sent and the state file is cleared.
//   - Silent on success is the CALLER's responsibility (this script only
//     ever sends when explicitly invoked to report a failure or recovery).
//   - --force: skip this script's own suppression check and always send.
//     For callers (e.g. send_alert.sh, the 3-arg bridge some checks use)
//     that already implement their own per-day suppression/recovery state
//     and just want an unconditional send when they decide to call this.
//     State is still recorded either way, so --force and non---force calls
//     for the same (property, check-name) interoperate safely.
//
// ALERT_TEST_MODE=1 (env var) — added 2026-08-31 after three test sends
// landed in the Director's REAL inbox, one with subject
// "x-test-bridge-key -- --dummy" -- a literal placeholder string that
// nothing caught. When ALERT_TEST_MODE=1:
//   - sgMail.send() is NEVER called, and the @sendgrid/mail module is never
//     even required -- there is no code path from test mode to a real send.
//   - The would-be alert (property, subject, body, timestamp, and the
//     suppression/recovery decision) is appended as one JSON line to
//     /root/ops/state/test-alerts.log instead.
//   - The SAME suppression-state file this script's real path writes is
//     still written, so test-mode calls genuinely exercise (and can prove
//     out) the suppression/recovery logic other checks (stale_site_check.js,
//     unhandled_lead_check.js) depend on -- test mode is a substitute for
//     the SendGrid call only, not for the rest of this script's behavior.
//   - An env var (not a CLI flag) was chosen as the primary mechanism so it
//     propagates through BOTH entry points -- direct send_alert.js calls
//     AND the send_alert.sh bridge (which hardcodes --force) -- without
//     either needing to know about it or pass anything through. A
//     --test-mode CLI flag is also accepted, filtered the same way
//     --recovery/--force already are, for symmetry / direct-call
//     convenience. Strict '1' equality (matching
//     ops/canary_check.js's CANARY_FORCE_VERIFY_FAIL convention): an
//     unrecognized truthy-ish value (e.g. ALERT_TEST_MODE=true) must NOT
//     silently fall through to a real send.
//
// Placeholder-content refusal (4b) — a SECOND, independent safety net, in
// EVERY mode, regardless of ALERT_TEST_MODE: if the subject fragment or
// body text is placeholder-shaped (see placeholderReason() below), this
// script refuses to send, logs why to stderr, and exits non-zero. This is
// what would have caught "x-test-bridge-key -- --dummy" even if whoever
// triggered it had forgotten to set ALERT_TEST_MODE.
'use strict';
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

const args = process.argv
  .slice(2)
  .filter((a) => a !== '--recovery' && a !== '--force' && a !== '--test-mode');
const isRecovery = process.argv.includes('--recovery');
const force = process.argv.includes('--force');
const isTestMode = process.env.ALERT_TEST_MODE === '1' || process.argv.includes('--test-mode');
const [property, subjectFragment, bodyText, checkNameArg] = args;
if (!property || !subjectFragment || !bodyText) {
  console.error(
    'usage: send_alert.js <property> <subject-fragment> <body-text> [check-name] [--recovery] [--test-mode]'
  );
  process.exit(1);
}

// --- 4b: refuse obviously placeholder-shaped content, in ANY mode ---
//
// Pattern design, and why each is safe against false-positiving on real
// alert copy (e.g. "the lead-path canary test succeeded" must NOT match):
//
//   EXACT-match checks (the field, once trimmed, IS ENTIRELY the token --
//   not a substring test, so embedding the word in a real sentence never
//   trips it):
//     "test"      -- the whole subject/body is nothing but that one word.
//                     Real alert text is never JUST "test" end to end; it's
//                     always embedded ("...canary test succeeded"), which
//                     `lower === 'test'` does not match.
//     "body text" -- the literal placeholder name from this script's own
//                     usage string, <body-text>, passed through verbatim
//                     instead of real content. No legitimate alert body is
//                     ever the two words "Body text" and nothing else.
//
//   SUBSTRING checks (synthetic-looking enough that no real alert would
//   ever contain them incidentally, so substring matching is safe here):
//     "--dummy"     -- a CLI placeholder-flag literal.
//     "x-test-"     -- the marker prefix from the actual incident
//                       ("x-test-bridge-key"); a generic synthetic-id
//                       marker template, not English prose.
//     "placeholder" -- the word itself; ops alert copy describes real
//                       failures (leads, canaries, stale sites) and never
//                       needs to say "placeholder".
//     "lorem ipsum" -- classic filler text, never appears in real copy.
//
//   WORD-BOUNDARY, CASE-SENSITIVE check (a standalone ALL-CAPS "TEST" token,
//   not embedded in a longer word, added after a live example surfaced
//   during this fix's own verification: a real send with subject "ALERT:
//   greeleycoloradoinsulation.com -- TEST -- TLS routing fix verification
//   (ignore, not a real incident)" reached the Director's inbox. That is
//   not the same shape as a substring match on "test" -- it is "TEST" used
//   as a standalone, capitalized marker/tag, exactly the way TODO/FIXME/XXX
//   are conventionally written. `/\bTEST\b/` (no `i` flag) matches that
//   shape but does NOT match "the lead-path canary test succeeded", because
//   that "test" is lowercase, sitting inside an ordinary English sentence.
//   Real alert copy from this portfolio's checks is always ordinary
//   sentence-case prose; nothing in unhandled_lead_check.js,
//   stale_site_check.js, or canary_check.js ever emits a bare uppercase
//   "TEST" token, so this cannot false-positive against them.
//
//   Deliberately NOT included: a case-insensitive /test/i match anywhere in
//   the string. That is exactly the pattern that would false-positive on
//   real copy like "the lead-path canary test succeeded" -- scoped out on
//   purpose; the case-sensitive word-boundary check above is the targeted
//   replacement that catches the real leaked shape without that cost.
function placeholderReason(field, label) {
  if (!field) return null;
  const trimmed = String(field).trim();
  const lower = trimmed.toLowerCase();
  if (lower === 'test') return `${label} is exactly the placeholder token "test"`;
  if (lower === 'body text')
    return `${label} is exactly "Body text", this script's own <body-text> usage placeholder`;
  if (/--dummy\b/i.test(trimmed)) return `${label} contains the "--dummy" placeholder-flag marker`;
  if (/x-test-/i.test(trimmed)) return `${label} contains the "x-test-" synthetic marker prefix`;
  if (/placeholder/i.test(trimmed)) return `${label} contains the word "placeholder"`;
  if (/lorem ipsum/i.test(trimmed)) return `${label} contains "lorem ipsum" filler text`;
  if (/\bTEST\b/.test(trimmed))
    return `${label} contains a standalone ALL-CAPS "TEST" marker token`;
  return null;
}

const placeholderBlockReason =
  placeholderReason(subjectFragment, 'subject') || placeholderReason(bodyText, 'body');
if (placeholderBlockReason) {
  console.error('[alert] REFUSING to send: ' + placeholderBlockReason + '.');
  console.error(
    '[alert] This looks like placeholder/test content reaching a call that was not marked as a test ' +
      '(ALERT_TEST_MODE was not set to "1"). If this is deliberate test traffic, set ALERT_TEST_MODE=1.'
  );
  console.error(
    '[alert] property=' +
      property +
      ' subjectFragment=' +
      JSON.stringify(subjectFragment) +
      ' bodyText=' +
      JSON.stringify(bodyText)
  );
  process.exit(1);
}

const DIRECTOR_ALERT_EMAIL =
  process.env.DIRECTOR_ALERT_EMAIL || process.env.LEAD_NOTIFY_EMAIL || 'kinestheticmarketing@gmail.com';

const propDirs = {
  denvercoloradoinsulation: { dir: '/root/denvercoloradoinsulation.com', from: 'leads@denvercoloradoinsulation.com' },
  longmontcoloradoinsulation: { dir: '/root/longmontcoloradoinsulation.com', from: 'leads@longmontcoloradoinsulation.com' },
  greeleycoloradoinsulation: { dir: '/root/greeleycoloradoinsulation.com', from: 'leads@greeleycoloradoinsulation.com' },
};
const matched = Object.entries(propDirs).find(([k]) => property.includes(k));
const propConfig = matched ? matched[1] : propDirs.denvercoloradoinsulation;
const envDir = propConfig.dir;

const checkKey = checkNameArg || subjectFragment;

// --- State-namespace isolation (added 2026-08-31, R1/R2/R3 monitoring-fix
// pass) --- Root cause of that pass's incident: prior to this change, the
// state-file key was sha1(property + '::' + checkKey) with NO dependence on
// isTestMode, so a test-mode call made with a REAL property string and a REAL
// checkKey (e.g. testing send_alert.js directly against
// 'denvercoloradoinsulation.com'/'unhandled-lead' instead of the harness's
// deliberately-nonsense test keys) wrote 'failing'/'recovered' into the EXACT
// SAME file the real unhandled_lead_check.js / stale_site_check.js timers
// read on their next run. Both of those callers invoke send_alert.js with
// --recovery unconditionally on every healthy run (by design -- see their own
// comments), relying entirely on this file's gating to make that safe. Once a
// test call (or any other stray writer) plants a false 'failing' status, the
// very next real 15-minute run finds status==='failing', concludes a genuine
// recovery notice is due, and sends a real "RECOVERED:" email to the Director
// for a failure that never happened -- confirmed live: the real
// denvercoloradoinsulation.com::unhandled-lead state file showed a
// 'recovered' transition with zero corresponding entry anywhere in that
// service's journal (which DOES capture the real failure-path console output
// via stdio:'inherit' -- only the unconditional recovery calls use
// stdio:'ignore'), timed inside the same few minutes as this file's own
// ALERT_TEST_MODE development/verification work.
//
// Fix: fold isTestMode into the hash input so a test-mode call's state file
// can NEVER collide with a real call's, regardless of what property/checkKey
// strings either one passes -- test isolation for the STATE STORE, not just
// for the SendGrid call. This is the same fix for both incidents in this
// pass: it stops a stray test write from ever contaminating real gating
// (R1/R2's state bug) and it closes the gap in R3's test isolation, which
// stopped fake EMAILS from reaching the real inbox but never stopped fake
// STATE from reaching the real state store.
const stateNamespace = isTestMode ? 'TEST' : 'REAL';
const stateFile = path.join(
  '/root/ops/state',
  crypto.createHash('sha1').update(stateNamespace + '::' + property + '::' + checkKey).digest('hex') + '.json'
);

// America/Denver, not UTC -- matches the convention the rest of this
// portfolio's checks were deliberately fixed to use (see stale_site_check.js's
// own history note on the identical class of bug). new Date().toISOString()
// rolls over at UTC midnight, which is 18:00 MDT / 17:00 MST -- any alert
// after that clock time would have been dated "tomorrow," splitting one
// calendar day's dedup window in two.
function denverDateString(d) {
  return new Intl.DateTimeFormat('en-CA', { timeZone: 'America/Denver' }).format(d); // en-CA -> YYYY-MM-DD
}
const today = denverDateString(new Date());

let prior = null;
try {
  prior = JSON.parse(fs.readFileSync(stateFile, 'utf8'));
} catch (_) {
  // no prior state, treat as first occurrence -- healthy/unknown, not down
}

// --- Audit log (added 2026-08-31) --- Every decision this script makes,
// unconditionally, regardless of the caller's stdio settings. Root problem
// this closes: unhandled_lead_check.js's and stale_site_check.js's healthy-
// path recovery calls use stdio:'ignore' by design ("silent on success"), so
// prior to this the journal had NO record of what this script decided on
// that path -- during this pass's own investigation, that made it impossible
// to confirm from logs alone whether a given recovery call actually sent,
// was suppressed, or ran in test mode. This does not change any send/
// suppress decision; it only makes every decision traceable after the fact.
const AUDIT_LOG_PATH = '/root/ops/state/alert-audit.log';
function auditLog(decision, extra) {
  try {
    fs.mkdirSync('/root/ops/state', { recursive: true });
    fs.appendFileSync(
      AUDIT_LOG_PATH,
      JSON.stringify({
        ts: new Date().toISOString(),
        property,
        checkKey,
        isRecovery,
        force,
        isTestMode,
        decision,
        priorStatus: prior ? prior.status : null,
        ...extra,
      }) + '\n'
    );
  } catch (_) {
    // audit logging must never take down the actual alert decision
  }
}

if (!force) {
  if (!isRecovery && prior && prior.date === today && prior.status === 'failing') {
    auditLog('suppressed-already-alerted-today');
    process.exit(0); // already alerted today for this exact failure, suppress
  }
  if (isRecovery && (!prior || prior.status !== 'failing')) {
    auditLog('suppressed-nothing-to-recover');
    process.exit(0); // nothing to recover from, don't send a spurious recovery notice
  }
}

const subject = isRecovery
  ? 'RECOVERED: ' + property + ' -- ' + subjectFragment
  : 'ALERT: ' + property + ' -- ' + subjectFragment;

if (isTestMode) {
  // Test mode never reaches SendGrid or the Director's real inbox: no
  // @sendgrid/mail require, no sgMail.send() call anywhere on this path.
  // Instead, log the would-be alert and still record the same
  // suppression/recovery state a real send would have, so test-mode calls
  // are genuinely useful for exercising the OTHER checks' suppression/
  // recovery logic end to end.
  const testLogPath = '/root/ops/state/test-alerts.log';
  const entry = {
    ts: new Date().toISOString(),
    property,
    subject,
    body: bodyText,
    checkKey,
    isRecovery,
    force,
    wouldSendTo: DIRECTOR_ALERT_EMAIL,
    from: propConfig.from,
  };
  try {
    fs.mkdirSync('/root/ops/state', { recursive: true });
    fs.appendFileSync(testLogPath, JSON.stringify(entry) + '\n');
    fs.writeFileSync(stateFile, JSON.stringify({ date: today, status: isRecovery ? 'recovered' : 'failing' }));
  } catch (err) {
    console.error('[alert][test-mode] failed to write test log/state:', err && err.message);
    auditLog('test-mode-log-failed', { error: err && err.message });
    process.exit(1);
  }
  auditLog('test-mode-logged');
  console.log('[alert][test-mode] NOT sent (ALERT_TEST_MODE) -- logged to ' + testLogPath + ':', subject);
  return; // top-level return is valid: Node wraps each module in a function.
}

// --- real send path (only reached when ALERT_TEST_MODE is not set) ---
require(path.join(envDir, 'node_modules', 'dotenv')).config({ path: path.join(envDir, '.env') });
const sgMail = require(path.join(envDir, 'node_modules', '@sendgrid', 'mail'));

if (!process.env.SENDGRID_API_KEY) {
  console.error('[alert] SENDGRID_API_KEY not set -- cannot send alert for', property, subjectFragment);
  process.exit(1);
}
sgMail.setApiKey(process.env.SENDGRID_API_KEY);

sgMail
  .send({
    to: DIRECTOR_ALERT_EMAIL,
    from: propConfig.from,
    subject,
    text: bodyText,
  })
  .then(() => {
    fs.mkdirSync('/root/ops/state', { recursive: true });
    fs.writeFileSync(stateFile, JSON.stringify({ date: today, status: isRecovery ? 'recovered' : 'failing' }));
    auditLog('sent');
    console.log('[alert] sent:', subject);
  })
  .catch((err) => {
    console.error('[alert] SendGrid send failed:', err && err.message);
    auditLog('send-failed', { error: err && err.message });
    process.exit(1);
  });
