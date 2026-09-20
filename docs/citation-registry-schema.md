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

## What CANNOT be registered (added 2026-09-07)

Read this before adding a source. Two whole classes of source are
unwatchable today, and registering one does not merely fail — it can
silently disable the check for every other source in that registry.

**1. PDFs.** `scripts/staleness_watcher.py` has **no PDF text-extraction
branch.** `fetch()`/`normalize()` are HTML-oriented — they strip tags and
decode the response bytes as text. A PDF's content streams are
Flate-compressed, so a literal search over them can never match, and **any
PDF-hosted source will report CHANGED forever.** Under the weekly schedule
recommended below that is an alert every Monday indefinitely, which is how a
watcher gets switched off. **Do not register a PDF source until that branch
exists.** Building it is known, needed, unstarted work; it was explicitly
ruled out of scope for the 2026-09-07 pass that wrote this section.

**2. JS-shell pages.** `seed` refuses them by design. Seeding against
`https://co.my.xcelenergy.com/s/residential/home-rebates/insulation-air-sealing`
(a Salesforce SPA) on 2026-09-07 returned, verbatim:

```
UNREACHABLE (JS shell): visible text after stripping tags is only 58 chars (floor 300)
```

### Why you cannot just set `fingerprint` to null

Established empirically 2026-09-07 against a scratch registry:

- `check_source()` reads `entry["fingerprint"]` **unconditionally**
  (`staleness_watcher.py:183`, `:193`), and `cmd_check()` has **no per-entry
  `try`/`except`**.
- Inside `sources[]`, `"fingerprint": null` raises
  `TypeError: 'NoneType' object is not subscriptable`.
- Inside `sources[]`, omitting `fingerprint` raises
  `KeyError: 'fingerprint'`.
- **Either aborts the ENTIRE run at that entry, so every source after it goes
  unchecked**, and it presents as a crash rather than as a stale citation.

There is currently **no supported way to register an un-fingerprintable
source inside `sources[]`.**

### The sanctioned pattern: a top-level `unwatchable_sources` array

Put such an entry in a **new top-level `unwatchable_sources` array**, a
sibling of `sources`:

```json
{
  "sources": [ ... ],
  "unwatchable_sources": [
    {
      "id": "EXAMPLE_ID",
      "type": "document",
      "url": "https://example.com/stable-wayfinding-page",
      "claim": "...",
      "repo": "examplesite.com",
      "pages": ["page-that-cites-it.html"],
      "retrieved": "2026-09-07",
      "watchable": false,
      "fingerprint": null,
      "notes": "NOT WATCHABLE BY scripts/staleness_watcher.py — this placement is LOAD-BEARING, see below. Reason it cannot be fingerprinted, both paths tested: ..."
    }
  ]
}
```

`cmd_check()` reads `registry.get("sources", [])`
(`staleness_watcher.py:209`) and **never iterates `unwatchable_sources`**, so
the entry cannot crash the run, while surviving as documentation next to the
property it describes instead of as a comment in an unrelated file.

State in the entry's own `notes` that the placement is **load-bearing, not
stylistic**, so a future tidy-up pass does not "normalize" it back into
`sources` and disable the registry.

In use as of 2026-09-07: `XCEL_CO_REBATE_SUMMARY_25_12_215` in both
`denvercoloradoinsulation.com/docs/citation-registry.json` and
`longmontcoloradoinsulation.com/docs/citation-registry.json`. Both registries
check clean afterwards — DCI 11 sources, LGM 13 sources, exit 0 each.

> **RENAMED 2026-09-20 — `XCEL_CO_REBATE_SUMMARY_25_12_215` NO LONGER EXISTS IN
> ANY REGISTRY.** The sentence above is left as the dated 2026-09-07 record it
> is, but do not follow that id: it embedded the print code `25-12-215`, which
> could not be retrieved from any first-party Xcel source and is **withdrawn**,
> and the id fed that code into the claim gate's `R7.current_replacements` via
> `repl_cfg.setdefault`, so the gate printed a print code nobody in this
> portfolio has ever confirmed. **The entry is now
> `XCEL_CO_RESIDENTIAL_REBATE_SUMMARY_2025_2026`**, which names the document by
> title, effective date and publisher — three attributes that are verifiable —
> and by no print code at all.
>
> **Measured 2026-09-20 across all three property registries, raw count and
> filter both, because the raw count alone is misleading here.** Raw
> `/usr/bin/grep -c 'XCEL_CO_REBATE_SUMMARY_25_12_215'` gives **DCI 0, LGM 0,
> GCI 3** — and *none* of GCI's three is a live key. All three sit inside
> `identifier_status` **prose that quotes the old id in order to retire it**
> (*"the old value, `XCEL_CO_REBATE_SUMMARY_25_12_215`, resolved to nothing
> here either"*), which is the same convention this canon uses for every
> retracted string. **As a KEY the old id occurs 0 times in all three: 0
> entry `id` fields and 0 `superseded_by.id` fields.** A bare `grep -c` on this
> file is an occurrence count, not a key count, and would report the rename
> incomplete when it is complete.
>
> `XCEL_CO_RESIDENTIAL_REBATE_SUMMARY_2025_2026` is present in DCI (11 sources
> / 6 `unwatchable_sources`) and LGM (13 / 5). **GCI (16 / 5) has no entry with
> that id**, and that is a *recorded* gap, not an oversight: GCI's Xcel
> tombstones name it in `superseded_by.id` while no such entry exists in that
> file. That dangling reference predates the rename — the old value resolved to
> nothing on GCI either — and GCI `1bc625c` left it deliberately rather than
> invent a current-source entry on a property whose pages assert nothing about
> that source.
>
> **Verify (keys, not occurrences):**
> ```bash
> for r in denvercoloradoinsulation.com longmontcoloradoinsulation.com greeleycoloradoinsulation.com; do
>   python3 - ~/code/$r/docs/citation-registry.json <<'PY'
> import json,sys
> d=json.load(open(sys.argv[1]))
> e=[x for b in ('sources','unwatchable_sources') for x in (d.get(b) or [])]
> old='XCEL_CO_REBATE_SUMMARY_25_12_215'; new='XCEL_CO_RESIDENTIAL_REBATE_SUMMARY_2025_2026'
> print('entries=%d  old-as-id=%d  old-as-superseded_by=%d  new-as-id=%d' % (
>     len(e),
>     sum(x.get('id')==old for x in e),
>     sum((x.get('superseded_by') or {}).get('id')==old for x in e),
>     sum(x.get('id')==new for x in e)))
> PY
> done
> # DCI entries=17 old-as-id=0 old-as-superseded_by=0 new-as-id=1
> # LGM entries=18 old-as-id=0 old-as-superseded_by=0 new-as-id=1
> # GCI entries=21 old-as-id=0 old-as-superseded_by=0 new-as-id=0   <- the recorded gap
> ```
Operational detail and the full failure-mode record are in this repo's
[`TOOLING_RUNBOOK.md`](../TOOLING_RUNBOOK.md), section "The citation
staleness watcher".

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
