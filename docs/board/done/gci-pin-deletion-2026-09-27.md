---
id: gci-pin-deletion-2026-09-27
owner: orchestrator
type: chore
created: 2026-09-27
retriage: 2026-10-04
size: S
lane: none — see "Lane discipline defect" below
---
# Delete the 13 GCI claim-gate pins whose pages got a real review, not a relocation

**This card is RETROACTIVE and that is itself the finding.** The work landed in
`76c32b4` with no card, no lane, and no Project-Rule entry, after
`closeout-2026-09-27-canon` had already been released. A verification agent
caught it on 2026-09-27. The card is written now so the change is not
invisible to the board, and the defect is recorded rather than tidied away.

## What changed

`ops/claim_gate/config/gci.json` — `R8.pinned_pages` went from **33 entries to
20**. Thirteen were deleted:

    index.html                          insulation-lasalle.html
    insulation-attic-greeley.html       insulation-milliken.html
    insulation-ault.html                insulation-rebate-hub.html
    insulation-blown-in-greeley.html    insulation-removal-greeley.html
    insulation-eaton.html               insulation-spray-foam-greeley.html
    insulation-greeley.html             insulation-windsor.html
    insulation-johnstown.html

## Why deleted rather than re-keyed

GCI's close-out pass rewrote **visible sales copy** on 15 pages to retire
unsourced ranking superlatives. That is an editorial claim correction, not a
relocation, so a real review happened and those pages' review dates moved to
2026-09-27 (GCI `c56893c`). Thirteen of the 15 carried pins.

`pinned_pages_note`'s own closing instruction governs this exact case: *"do not
extend its pin — the pin will already have expired by itself; move the date if
a review actually happened, or re-key with a reason true of the new text."*
Re-keying would assert the old date was still correct despite the change — the
claim the date move ruled false. Each entry's stated reason (*"2026-09-27
HERO-FORM LIFT … zero words added"*) is no longer true of the page's current
text, so keeping it would be dead suppression. Rule 2.

## Why this TIGHTENS the gate rather than loosening it

All 13 pins carried `expected_footer`, and 12 also carried `expected_sitemap` —
assertions, not suppressions. Deleting them wholesale could have removed a live
check. It does not: both keys are read at exactly one site in the entire
portfolio, `claim_gate.py:5495-5496`, guarded by `if base in pinned:` at
`:5493`. They exist to verify a pin still describes reality and are not
independent rules. With the pin gone, the page falls back to R8 part (d)
against git — the **stricter** path — and all 13 pass it on their moved dates.

Independently confirmed by a verification agent that grepped all four repos for
both keys across all file types, and by canon's own
`ADVERSARIAL_READ_2026-09-17.md:2338-2339` (*"expected_sitemap referenced in
code: 0"*).

## Verification

```bash
# 1. Pin count and the deleted set. Returns: 20 ['404.html', 'about.html', 'contact.html']
python3 -c "import json; p=json.load(open('ops/claim_gate/config/gci.json'))['R8']['pinned_pages']; print(len(p), [k for k in ('404.html','about.html','contact.html','privacy.html') if k in p])"

# 2. Every surviving pin is still LIVE, re-derived with the gate's own function.
#    Returns: keyed-live=20 keyed-expired=0 unkeyed=0 missing=0
cd ops/claim_gate && python3 -c "
import sys,os,json,pathlib; sys.path.insert(0,os.getcwd())
import claim_gate as cg
pins=json.load(open('config/gci.json'))['R8']['pinned_pages']
pub=pathlib.Path(os.path.expanduser('~/code/greeleycoloradoinsulation.com/public'))
live=exp=0
for b,v in pins.items():
    got=cg.visible_text_sha256('public/'+b,(pub/b).read_text(encoding='utf-8',errors='replace'))
    live+= got==v.get('visible_text_sha256'); exp+= got!=v.get('visible_text_sha256')
print('keyed-live=%d keyed-expired=%d'%(live,exp))"

# 3. The gate itself passes on the property. Returns: EXIT=0, blocking failures: 0
cd ~/code/greeleycoloradoinsulation.com && ./ops/claim_gate.sh; echo "EXIT=$?"

# 4. expected_footer / expected_sitemap have exactly one code read site, and it is guarded.
grep -rn 'expected_footer\|expected_sitemap' ops/claim_gate/claim_gate.py
```

Measured at GCI HEAD `69009d4` (the tree this config governs): 20 keyed-LIVE, 0
keyed-expired, 0 unkeyed, 0 missing. 20 pinned + 18 unpinned = 38 pages.

**Commit: `76c32b4`.** Follow-up commit correcting this card's own defects and
the note's stale VERIFY: see the lane row and `docs/lanes.md`.

## Lane discipline defect, recorded not hidden

1. `76c32b4` touched `ops/claim_gate/config/gci.json`, which was **outside** the
   declared ownership of `closeout-2026-09-27-canon` (that lane declared
   `METHODS/DESIGN_REVIEW.md`, `METHODS/ARCHITECT_DISCIPLINE.md`,
   `docs/board/ground-truth.md`, `docs/board/**` and `docs/lanes.md`).
2. It landed **after** that lane was released, as did `77f4ba3`.
3. It carried no card until this one.

The work itself is sound and independently verified. The process defect is that
a change deleting 13 gate exemptions entered canon with no board trace. A lane
release is not a licence to keep committing under it, and a commit that widens
scope needs its own claim.
