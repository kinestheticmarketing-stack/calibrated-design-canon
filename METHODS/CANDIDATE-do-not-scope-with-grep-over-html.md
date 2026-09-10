# CANDIDATE PRINCIPLE — do not scope content work with grep over rendered HTML

**Drafted 2026-08-24. NOT yet merged into `PROPERTY_GENESIS.md`.** Two
independent instances in a single day.

## The principle

**Grep over rendered HTML CONFIRMS. It does not FIND.**

A grep that returns hits is evidence. **A grep that returns zero is not
evidence of absence** — it is evidence that one string, as typed, did not
appear on one line. Rendered HTML defeats it in at least four ways:

1. **Line wrapping.** Generated markup wraps mid-sentence, so a phrase spanning
   a break matches nothing.
2. **Tags inside the phrase.** `<strong>`, `<a>` and `<em>` sit between the
   words you searched for.
3. **Entity encoding.** `&amp;`, `&mdash;`, `&ldquo;` are not what you typed.
4. **The claim has no literal form.** The defect may be a sentence that encodes
   a false threshold without naming it.

## The two instances, same day

- **D2, R-49.** Greps for `R-49 to R-60`, `R402.1.2` and `R-49 minimum` all
  returned **0** and the class was reported CLOSED. *"post-2010 homes… at or
  near current targets"* was still false against R-60 and contains **no
  R-string at all**. A row agent found it by reading. Separately, a `grep -n`
  enumeration undercounted the same file by ~21 occurrences because output was
  truncated per line.
- **Privacy claim.** A scope pass over three properties returned *"phrase
  absent"* on all three. The sentence — *"Beyond that we collect only what the
  quote form asks for"* — was present on two of them, **wrapped across a line
  break**.

Both would have shipped as "class closed" on the strength of a zero.

## The method instead

1. **Strip tags, unescape entities, collapse whitespace, then search the text.**
2. **To enumerate, parse — do not eyeball `grep -n`.** Truncated output hides
   mid-line occurrences.
3. **For any claim with no fixed literal form, READ.** One page per reader.
4. **Verification must test the CLAIM, not the STRING.** If a verification
   command is a string grep, it proves the string is gone. It does not prove
   the claim is.

## Why this belongs in genesis

Every property in this portfolio is audited by grepping its rendered output.
The method is load-bearing at clone time and at every sweep after. **A new
property inherits the method along with the template.**

## Open question for the Director
Whether to pair this with a required tooling step — a `text-of()` helper in
each repo that emits normalized page text — so the correct method is the
cheapest one. A principle that is more work than the wrong habit loses.

---

## ADDENDUM — 2026-09-10 — FOUR MORE INSTANCES, AND THE COROLLARY THAT MATTERS MORE THAN THE PRINCIPLE

The portfolio-wide rebate-figure strip (Director ruling 2026-09-09; 545 figures
removed across DCI, LGM and GCI) re-proved this principle on all three
properties in a single pass, and surfaced a corollary this file did not have.

### The four instances

A dedicated inventory row (R1) swept all three repos for dollar figures and
produced a line-numbered specification: file, line, rendered text, source of
truth. It was careful, method-aware, and **incomplete on every property**.

- **LGM.** Four figure sites unlisted. R1 documented "six surfaces per measure
  page"; three pages actually had seven.
- **DCI.** Three unlisted lines (`_generate_service_pages.py` 1121, 1141, 1611).
- **GCI.** An entire live data module, `_area_pages.py`, never listed — **17
  live figures across six town pages.** R1's pointer named the wrapper
  generator, not the data it consumes.
- **The one that proves the principle rather than merely illustrating it:**
  LGM's `spray-foam-vs-blown-in-comparator` page carried `$1.16` and `$0.77`
  **even though neither string appears anywhere in that page's generator.** It
  inherited them by naming a shared `CITED_SOURCES` key in `cite_keys=[...]`.
  No string search for the figure could ever have found that page, because the
  figure is not in it. It is in something it points at.

### THE EXTENSION: an inventory produced by grep is not a specification

This is the operational consequence and it is the reason this file should
merge rather than sit as a candidate.

If grep over rendered HTML **confirms but does not find**, then any inventory
built by grep is incomplete *by construction*. Handing that inventory to
downstream rows as their specification propagates the incompleteness into the
work — silently, because each row believes it has a complete map and stops when
it reaches the end of the list.

**What worked instead, and should be the standing pattern:** give every
downstream row a **re-runnable acceptance GATE** — a predicate over the whole
tree, not a list of locations — and tell it explicitly that **the gate is the
specification and the inventory is only a starting point.** Every one of the
three editing rows independently found figures R1 missed, and every one of them
found those figures by running the gate and continuing past the end of the
inventory. A row working the line list alone would have shipped all four
instances above.

**A list enumerates what was found. A gate defines what done means.** Only the
second survives an incomplete search.

### THE COROLLARY: a gate is only as good as its anchor

The gate used on this pass was:

```
/usr/bin/grep -rhoE '\$[0-9][0-9,.]*' public/ --include='*.html' --include='*.txt' \
  --include='*.js' --include='*.json' --include='*.xml' | sort | uniq -c
```

It returned **zero** on DCI and GCI, and every row reported the property clean.
Adversarial verification then found this, live, on a GCI page — inside a
`<script>` comment, in the delivered bytes, in view-source and in what LLM
crawlers read:

> `// CAP/RATE (1550 / 0.75) and money() were DELETED 2026-09-08. They existed`
> `// only to print Atmos's rate and cap in this tool's verdict;`

`1550` is the Atmos attic rebate cap. `0.75` is its rate. **The gate was
`$`-anchored and these are bare digits, so the gate was blind to them by
construction** — exactly the failure this file describes, committed by the very
instrument built to prevent it.

Two lessons, both general:

1. **State your gate's blind spot in the same breath as its result.** "Gate
   returns zero" is not a finding. "Gate returns zero, and the gate is anchored
   on `$`, so it cannot see a figure written as bare digits" is. A zero from an
   anchored instrument is evidence about the anchor, not about the tree.
2. **A removal note that restates the figure it removed re-publishes it.** The
   comment above existed *to document a deletion* and shipped the deleted value
   for two days. When you record what was removed, record the fact and the
   reason, never the numeral.

### A THIRD FAILURE MODE THE SAME PASS SURFACED: deleting a figure is half the job

Adversarial verification found live sentences on two properties still pointing
at figures that no longer exist — grammatical, containing no numeral, therefore
invisible to both the gate and a prose proofread:

- DCI: *"The standard rebate guide covers the base amounts the bonus
  multiplies"* — linking to a page that states *"Per-measure dollar caps are
  deliberately not enumerated on this page."*
- GCI: *"The Atmos figures quoted elsewhere on this site are for the towns
  Atmos serves"* — on a property that now quotes zero Atmos figures.

The class sweep for the DCI case found **seven** inbound promises across **two**
refusing destinations, and **five predated the ruling entirely** — opened by a
2026-08-24 pass that deleted DCI's cost estimator and never revisited what
pointed at it. Pages told readers a calculator *"estimates the project cost"*
while that calculator said it *"does not compute a dollar estimate."* Sixteen
days live, through every audit in between.

**When you remove a figure, the removal is not complete until every sentence
that promised it has been found.** Those sentences do not contain the figure,
so no figure-shaped search will locate them. Search for the PROMISE — "covers
the amounts", "for current amounts see", "the figures are on", "how much" —
against what each destination now actually renders.

### REPORT THE RAW MATCH COUNT NEXT TO THE ADJUDICATED ONE

A refinement the verification row produced, and it corrects how the
coordinator had been reporting its own sweeps in this same pass.

Three independent JS-comment scans across the three properties were reported
as "**0 rebate numerals**." That conclusion was correct. But the instrument
did not match nothing — it fired **153 times** (DCI 150, LGM 2, GCI 1) and
every hit was adjudicated away as a non-rebate numeral: form-page counts,
a commit SHA, R-values, decision-path counts, and LGM's permitted
installed-cost rates.

**A bare `0` conceals that the zero came from judgment applied AFTER the
match, not from the instrument finding nothing.** And a run whose filter
silently dropped a real hit looks identical, on the page, to a clean run.
Reporting "raw 153, adjudicated 0, here is the adjudication" is falsifiable.
Reporting "0" is not.

This is the same lesson as the `$`-anchored gate one level up: the number a
sweep reports is a statement about the instrument as much as about the tree,
and a reader cannot tell the two apart unless both are shown.

**The rule: any sweep reported as zero states its raw match count, its filter,
and what the filter removed.** The null half of a sweep is only auditable if
the cleared items are enumerated.

### One more, for completeness: fixing the string is not fixing the class

GCI's editing row corrected *"the Atmos **amounts** quoted elsewhere"* and
reported the class closed. A variant reading *"the Atmos **figures** quoted
elsewhere"* survived on two pages, each shipping twice — body prose and
`FAQPage` JSON-LD. Canon Rule 8c already governs this; it is recorded here
because the mechanism is specifically a string search standing in for a claim
search, which is this file's subject.
