---
id: browser-canary
owner: executor
type: feature
created: 2026-08-19
tags: [verify-prod]
---
# Browser-driven canary, portfolio-wide, one weekly timer

`denvercoloradoinsulation.com/ops/browser_canary.js` closes the gap the
daily POST canary cannot see: it never touches a browser, so it cannot
prove a form renders or client JS runs. This one drives real headless
Chrome against each live page, fills the form, waits out the bot-timing
gate honestly, clicks the real submit button, then independently
re-queries Postgres rather than trusting the DOM (three backend branches
silently discard a lead while still answering success). Proven by three
deliberate breakages, each fired and restored, none touching a live
property. First clean run: DCI 22/23, GCI 16/17, **LGM 9/10 — the first
time Longmont's form had ever been shown to work end to end.**

**Verify:**
```
ssh root@74.208.181.10 'systemctl list-timers browser-canary.timer --no-pager'
```
