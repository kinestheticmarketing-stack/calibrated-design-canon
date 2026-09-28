---
id: canon-is-public-and-publishes-the-production-vps-address
owner: director
type: decision
created: 2026-09-28
retriage: 2026-10-12
size: S
severity: medium
classification: DIRECTOR
---
# DIRECTOR: canon is a public repo and it publishes the production VPS address

**Unblocking action (exactly one): the Director rules on which of the three
options below to take.** Nothing is pending repo-side; every fact on this card
was measured on 2026-09-28 with the commands shown.

## Running the commands on this card

Every command below uses `$VPS` rather than the literal address, because this
card lives in the public repo it is about and spelling the address out here
would add four more published occurrences to the seventeen it reports. Set it
first from a non-published source — the address is in this repo's
`TOOLING_RUNBOOK.md` (already published, which is part of the problem) and in
`~/.claude/hooks/h04_wrong_ssh_host.sh` (not published):

```bash
VPS="$(grep -oE '[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+' ~/.claude/hooks/h04_wrong_ssh_host.sh | head -1)"
```

## What is true now

`calibrated-design-canon` is a **PUBLIC** GitHub repository. The three property
repos are private.

```
$ gh repo view kinestheticmarketing-stack/calibrated-design-canon --json visibility,isPrivate
{"isPrivate":false,"visibility":"PUBLIC"}
```

The production VPS address appears in **11 tracked files, 17 occurrences**, all
on `origin/main`:

```
$ git grep -c "$VPS" -- .
docs/lanes.md:4
scripts/monitoring/deploy_drift_check.sh:3
TOOLING_RUNBOOK.md:2
scripts/monitoring/ops_drift_check.sh:1
scripts/monitoring/_mon_lib.sh:1
scripts/deploy_ops_to_vps.sh:1
METHODS/HANDOFF_TEMPLATE.md:1
METHODS/ARCHITECT_DISCIPLINE.md:1
docs/board/done/phase8-calculator-criterion-unmet.md:1
docs/board/done/browser-canary.md:1
CANON_QUEUE.md:1
```

It is not merely committed, it is **served to anyone on the internet**, proven
by an unauthenticated fetch from the CDN rather than from the local checkout:

```
$ curl -sS -o /tmp/pub_lanes.md -w 'http=%{http_code} bytes=%{size_download}\n' \
    https://raw.githubusercontent.com/kinestheticmarketing-stack/calibrated-design-canon/main/docs/lanes.md
http=200 bytes=169445
$ grep -c "$VPS" /tmp/pub_lanes.md
4
```

Most of those occurrences sit next to `ssh root@` in a command line, so the
published text states the host, the login user, and that key-based root SSH is
configured for it. `METHODS/ARCHITECT_DISCIPLINE.md`'s Rule 3 says so outright.

**This predates the 2026-09-28 pass and was not introduced by it.** The eleven
commits pushed that day added zero occurrences:

```
$ git diff 4c76593..HEAD -- . | grep -c "^[+].*$VPS"
0
$ git grep -l "$VPS" 4c76593 -- | wc -l
11
```

**No credential is exposed.** A name-level scan (canon Rule 5b — test for the
name, never the value) across all tracked canon files returns zero files for
every pattern tried: `BEGIN ... PRIVATE KEY`, `ghp_`/`github_pat_`, `AKIA`,
`sk-ant-`, `SG.`, `xox[baprs]-`. An IP address is not a credential. What is
exposed is an attack surface, not a key.

## Why this is the Director's and not the Architect's

Canon's public visibility is **deliberate design**, not an oversight:
`METHODS/AUDITOR_PROTOCOL.md:242` routes external auditors to
`raw.githubusercontent.com/.../calibrated-design-canon/main/METHODS/AUDITOR_PRIMING_TEMPLATE.md`,
`METHODS/the-calibrated-stack.md:119` states "GitHub-first", and
`METHODS/GIVE_FIRST_DISCIPLINE.md` treats publishing canon as the point of the
artifact. So this is not a technical slip with one right answer (Rule 1e); it is
a risk-acceptance tradeoff against a deliberate publishing strategy. Rule 10g
was applied and this card survives it.

## The options, with what each costs

**Option 1 — Accept and do nothing.** The address is already indexed by whatever
has crawled the repo; scrubbing HEAD does not unpublish history. Cost if wrong:
the host is trivially discoverable for port-scanning and SSH brute-force. Note
root SSH is key-only, which is the mitigating fact. Reversible: n/a.

**Option 2 — Scrub HEAD, keep canon public.** Replace the literal address with a
placeholder or a hostname in the 11 files, keep the real value in
`~/.claude/` or an untracked local config. Reduces discoverability for anyone
reading the repo today; does NOT remove it from git history, so it is partial by
construction. Cost: one pass, plus the ongoing discipline of not reintroducing
it. Reversible: yes.

**Option 3 — Make canon private.** Fully closes it, and breaks the external
auditor flow that `AUDITOR_PROTOCOL.md` depends on, plus the GIVE_FIRST
publishing strategy. Cost: the give-first strategy is the thing being given up.
Reversible: yes, but re-publishing re-exposes.

**RECOMMENDATION: Option 2.** It is the only one that reduces exposure without
surrendering the publishing strategy canon exists for, and it is cheap and
reversible. Its known limitation — history retains the address — is real but
does not argue for Option 1, because the marginal reader of this repo reads HEAD,
not the reflog. Option 3 should be reserved for the case where the Director
decides the give-first strategy is not worth an exposed host at all.

A fourth option, rewriting git history to purge the address, is NOT recommended
and is not offered: it requires a force-push, which this portfolio forbids, and
it would break every published `raw.githubusercontent` URL that
`AUDITOR_PROTOCOL.md` hands to external auditors.

## One occurrence this pass DID add, disclosed rather than hidden

The first version of this card spelled the address out four times. That was
caught before anything was pushed and replaced with `$VPS` above, so the card's
own file adds **zero** occurrences. But the commit that created it,
`6ce922f`, carries the literal address once in its message, and that message
cannot be corrected: the commit is no longer `HEAD`, three later commits sit on
top of it, and amending it would mean rewriting history — which this pass is
explicitly forbidden to do. So the net effect of this pass on the exposure is
**+1 occurrence, in a commit message**, against the 17 already in tracked files.
Disclosed here because a card arguing an address is over-published should not
quietly be the thing that publishes it again.

## Source

Found by the adversarial verification reader of the 2026-09-28
`harness-hardening-2026-09-28` pass, while verifying row R3's pushes. R3 flagged
`docs/lanes.md` only; the reader measured the true scope at 11 files, and the
orchestrator confirmed every figure on this card independently before writing it.

## Closed

Closed by Director ruling 2026-09-28: risk accepted. Canon publicly shows the
production VPS address (also published by DNS for the property domains), the
deploy script path, the root login pattern, the backup directory, and the
command allowlist shape. Mitigation: ssh is key-only. Canon stays public so
it remains fetchable from chat.

**Verification:**

```bash
grep -A5 "^## Closed" docs/board/done/canon-is-public-and-publishes-the-production-vps-address.md
```

Commit: `002ca34` (row R1, lane `close-down-rev2-2026-09-28`)
