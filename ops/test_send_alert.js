#!/usr/bin/env node
// /root/ops/scripts/test_send_alert.js — verification harness for the
// ALERT_TEST_MODE (4a) and placeholder-refusal (4b) additions to
// send_alert.js, added 2026-08-31. Each case runs in its OWN process (via
// `node test_send_alert.js <case>`) so a poisoned @sendgrid/mail module can
// be seeded into Node's require.cache BEFORE send_alert.js is required --
// if send_alert.js's real-send path is ever reached, the poison module
// throws instead of silently doing nothing, so a structural bug in the
// test-mode / placeholder short-circuit would be caught, not masked.
//
// Cases:
//   node test_send_alert.js test-mode        -- ALERT_TEST_MODE=1, genuine content
//   node test_send_alert.js placeholder       -- placeholder content, test mode NOT set
//   node test_send_alert.js real-content-dry  -- genuine content, test mode NOT set,
//                                                  sgMail mocked (never touches the network)
'use strict';
const path = require('path');
const fs = require('fs');

const propDir = '/root/greeleycoloradoinsulation.com';
const sgMailEntry = path.join(propDir, 'node_modules', '@sendgrid', 'mail');
const sgPath = require.resolve(sgMailEntry);

const kase = process.argv[2];
if (!kase) {
  console.error('usage: test_send_alert.js <test-mode|placeholder|real-content-dry>');
  process.exit(2);
}

function seedPoisonSendgrid() {
  require.cache[sgPath] = {
    id: sgPath,
    filename: sgPath,
    loaded: true,
    exports: {
      setApiKey() {
        throw new Error('POISON: sgMail.setApiKey() was called -- real-send path was reached unexpectedly');
      },
      send() {
        throw new Error('POISON: sgMail.send() was called -- real-send path was reached unexpectedly');
      },
    },
  };
}

function seedCapturingSendgrid(captureFile) {
  require.cache[sgPath] = {
    id: sgPath,
    filename: sgPath,
    loaded: true,
    exports: {
      setApiKey() {},
      send(msg) {
        fs.writeFileSync(captureFile, JSON.stringify({ mocked: true, ts: new Date().toISOString(), msg }, null, 2));
        return Promise.resolve([{ statusCode: 202 }]);
      },
    },
  };
}

function runSendAlert(argv) {
  process.argv = ['node', '/root/ops/scripts/send_alert.js', ...argv];
  require('/root/ops/scripts/send_alert.js');
}

if (kase === 'test-mode') {
  seedPoisonSendgrid(); // if reached, throws -- proves test mode never touches SendGrid
  process.env.ALERT_TEST_MODE = '1';
  runSendAlert([
    'greeleycoloradoinsulation',
    'harness verification: unhandled-lead-check test-mode run',
    'This is a real-looking body used only to verify ALERT_TEST_MODE=1 logs instead of sending.',
    'harness-test-mode-check',
  ]);
  console.log('TEST-MODE CASE: completed with no exception -- poison sgMail was never invoked.');
} else if (kase === 'placeholder') {
  seedPoisonSendgrid(); // belt-and-braces: placeholder check runs before require() anyway
  delete process.env.ALERT_TEST_MODE;
  try {
    runSendAlert([
      'greeleycoloradoinsulation',
      'x-test-bridge-key -- --dummy',
      'placeholder',
      'harness-placeholder-check',
    ]);
    console.log('PLACEHOLDER CASE: did not exit -- UNEXPECTED (should have called process.exit(1)).');
  } catch (err) {
    console.error('PLACEHOLDER CASE: threw unexpectedly:', err.message);
    process.exitCode = 1;
  }
} else if (kase === 'real-content-dry') {
  const captureFile = '/root/ops/state/test-real-content-dry-capture.json';
  try { fs.unlinkSync(captureFile); } catch (_) {}
  seedCapturingSendgrid(captureFile);
  delete process.env.ALERT_TEST_MODE;
  runSendAlert([
    'greeleycoloradoinsulation',
    'harness verification: the lead-path canary test succeeded, this is genuine content',
    'Real alert body: 3 unhandled leads have been pending delivery for 22 minutes. ' +
      'This deliberately contains the word "test" mid-sentence to prove the safety-net guard ' +
      'does not false-positive on real copy.',
    'harness-real-content-check',
  ]);
  // send_alert.js's real path is a Promise chain (.then/.catch); give it a
  // beat to resolve before checking whether the mock captured a send.
  setTimeout(() => {
    if (fs.existsSync(captureFile)) {
      console.log('REAL-CONTENT CASE: mock sgMail.send() WAS called (this is the one case that would ' +
        'actually send in production). Captured payload:');
      console.log(fs.readFileSync(captureFile, 'utf8'));
    } else {
      console.error('REAL-CONTENT CASE: mock sgMail.send() was NOT called -- UNEXPECTED.');
      process.exitCode = 1;
    }
  }, 500);
} else {
  console.error('unknown case:', kase);
  process.exit(2);
}
