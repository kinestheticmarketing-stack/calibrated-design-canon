---
title: Citation staleness registry — schema and how to run
---

# Citation staleness watcher

Implementation: `scripts/staleness_watcher.py` (this repo). The full registry
JSON schema and the design rationale (why fingerprints are per-provision, not
per-page; why JS-shell detection matters; what `adoption_state` sources are
for) live in that script's module docstring — read it there, not duplicated
here, so the two can't drift apart.

## Where registries live

One `docs/citation-registry.json` per site repo (DCI, LGM, GCI) — not in this
repo. The schema/engine is shared; the data is property-specific and belongs
next to the property it describes.

## Running it

```bash
python3 scripts/staleness_watcher.py check --registry <site-repo>/docs/citation-registry.json --verbose
```

Exit code 0 = every source UNCHANGED. Exit code 1 = at least one CHANGED or
UNREACHABLE — safe to alert a scheduler on nonzero without parsing output.

Report-only. It never edits a registry file, a page, or a generator. A
CHANGED or UNREACHABLE result is a prompt for a human/future pass to
re-verify and, if warranted, correct the citation — not something this
script applies itself.

## Adding a new source

Use `seed` to compute the fingerprint block for a new entry instead of
hand-hashing:

```bash
python3 scripts/staleness_watcher.py seed --url URL --method regex --pattern 'PATTERN'
python3 scripts/staleness_watcher.py seed --url URL --method anchor --start 'TEXT' --end 'TEXT'
```

It prints a `fingerprint` object (method, pattern/anchors, hash, sample) —
paste that into the registry entry along with `id`, `type`, `url`, `claim`,
`repo`, `pages`, `retrieved`, and optional `notes`.

Extraction runs against the page's tag-stripped, whitespace-normalized text,
not raw HTML — inline markup routinely splits a cited sentence mid-word
(e.g. a hyperlinked term), and matching raw HTML makes a fingerprint brittle
to markup changes that have nothing to do with the cited content.

## Scheduling

Not installed this pass (report-only tool, no cron/launchd unit created).
Recommended command to schedule, once per site repo:

```bash
cd /Users/vongimbel/code/calibrated-design-canon && \
  python3 scripts/staleness_watcher.py check \
    --registry /Users/vongimbel/code/denvercoloradoinsulation.com/docs/citation-registry.json \
    --verbose >> /Users/vongimbel/code/denvercoloradoinsulation.com/docs/citation-registry-log.txt 2>&1
# repeat for longmontcoloradoinsulation.com and greeleycoloradoinsulation.com
```

This is a personal macOS dev machine, not an always-on server — plain
`cron` silently skips runs while the machine is asleep, with no catch-up.
`launchd` with a `StartCalendarInterval` has the same asleep-skip behavior
by default, but is the native mechanism and easier to inspect
(`launchctl list`). Recommended: a `launchd` user agent,
`~/Library/LaunchAgents/com.calibrated.citation-staleness-watcher.plist`,
running weekly (`StartCalendarInterval` with `Weekday: 1, Hour: 9`), one
`ProgramArguments` invocation per repo (three `<dict>` entries, or a thin
wrapper shell script looping over the three repos so the plist only needs
one program entry) with `StandardOutPath`/`StandardErrorPath` pointed at a
log. `RunAtLoad` should be `false` — this is a periodic check, not a
startup task. Weekly, not daily: the failure this exists to catch (a code
adoption, a rebate program revision) moves on a scale of weeks, and a
webscraper hitting a city planning department's server daily is needless
load for no added signal.
