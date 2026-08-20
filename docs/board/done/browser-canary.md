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

---

## Correction — 2026-08-20

**"none touching a live property" (lines 17-18) is wrong as written.** Left in
place so the card's history stays legible; read it as superseded here.

Driving real headless Chrome against the **live** page is the mechanism, so
every run — forced-fault runs included — contacted live properties, and the
clean runs created real rows (DCI 22/23, GCI 16/17, LGM 9/10). The 2026-08-20
negative-control work (`denvercoloradoinsulation.com` commits `802b69f`,
`01f69e5`) created more.

What holds is the weaker, true claim: **no live property was poisoned.** Every
row canary work created is correctly flagged `canary=true`; no unflagged test
data was written and no real lead was altered.

Same correction applied to `denvercoloradoinsulation.com`'s
`docs/board/done/browser-canary-shipped.md` and to its `STATE_OF_PROJECT.md`.
