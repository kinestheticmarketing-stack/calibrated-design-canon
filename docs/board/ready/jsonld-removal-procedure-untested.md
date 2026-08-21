---
id: jsonld-removal-procedure-untested
owner: architect
type: risk
created: 2026-08-21
priority: 35
---
# The JSON-LD removal ruling is canon-adjacent and has never been exercised

At the 2026-08-21 S-GATE the Director ruled:

> RC-1 step 2 inside a JSON-LD string means REMOVE THE WHOLE PROPERTY OR
> ANSWER OBJECT. Not halt. The block must remain VALID JSON and must still
> parse as valid schema.org. Verify by PARSE, not by grep. If removing the
> property would leave malformed JSON or an invalid block, THEN escalate to
> step 3 and halt that instance.

**It was never exercised.** LGM's 4 target-carrying JSON-LD blocks went 4 -> 0,
but as a **side effect**: FAQ answers are generated from the same source
strings as the prose, so editing the prose removed both surfaces in one edit.
No property or Answer object was ever removed as a distinct action. DCI's
target-carrying blocks at S0 were **0** (its `$400` JSON-LD hits were
installation cost ranges, not rebate claims).

**Zero removals performed. Zero parse-validations run against a
post-removal block.**

## Why this is a risk rather than a curiosity

The procedure now has the authority of a Director ruling and the reliability of
untested code. The first wave that genuinely needs it — a defect that lives in
structured data but NOT in the prose that generates it — will be executing an
unproven procedure under remediation pressure, on the surface AI engines read
most literally.

The generator coupling that made it unnecessary here is not guaranteed: any
hand-authored JSON-LD, or any block whose text diverges from its prose source,
breaks it.

## Proposed — NOT applied
Exercise it once against a scratch copy: plant a defect in an escaped, minified
FAQPage answer, remove the Answer object per the ruling, and prove with
`json.loads` plus a schema.org validity check that the block still parses and
remains valid. Record the transcript so the first real use is the second use.
