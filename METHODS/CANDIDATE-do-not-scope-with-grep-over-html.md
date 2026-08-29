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
