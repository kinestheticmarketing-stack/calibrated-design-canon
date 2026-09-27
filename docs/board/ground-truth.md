# Ground truth (supersedes any older session context)

These decisions are settled. If your context disagrees, your context is stale.

- **This is the portfolio-level board.** It carries decisions and defects
  that span properties. Property-specific work lives on that property's own
  `docs/board/` — DCI, Longmont, Greeley each have one. Do not duplicate a
  single-property item here; cross-reference it instead.
- **Three live properties, one in-progress fourth.** DCI (control, Xcel
  gas+electric, Denver metro), Longmont (Xcel gas + Longmont Power &
  Communications electric via Efficiency Works — never described as
  stacking), Greeley (Atmos gas, electric unresolved). Fort Collins is the
  next genesis, not yet started.
- **2026-08-19 — `_postbuild_check.py` runs exactly 5 validators**, not six.
  `check_interactive_js`, `check_placeholders`, `check_duplicate_labels`,
  `check_credentials`, `check_jsonld`. RECEIPTS.md carried "six" for a full
  day after a kickoff-supplied figure was never checked against the code —
  corrected `66b6336`. Any future reference to "the validator layer" cites
  five.
- **2026-08-19 — a figure asserted in a kickoff is not a verified figure.**
  Standing rule, `CANON_QUEUE.md`. The validator-count error is the
  motivating incident; do not re-litigate it, apply the rule.
- **2026-08-19 — a Done board card is not done without a verification
  command and a commit hash.** Same rule, ported to all four boards. See
  `conventions.md`'s Project Rule section for the four dated incidents.
- **2026-08-19 — the client-questionnaire and critical-tools-collecting Zarr
  rulings are canon**, recorded in `METHODS/PROPERTY_GENESIS.md`'s standing
  rulings section. Do not re-litigate either on a future property.
- **2026-08-19 — the browser canary is portfolio infrastructure**, one
  script (`denvercoloradoinsulation.com/ops/browser_canary.js`) covering all
  three properties from one weekly systemd timer, closing what the daily
  POST canary structurally cannot see (form render, client JS execution).
- **Standing — Pattern 11 (Build Order Law).** External SEO — GBP, link
  building, directory submission, paid rank tooling — is blocked until
  internal SEO is at 100%. Search Console and Bing Webmaster registration
  are explicitly not external SEO.
- **Standing — Pattern 13.** Kickoffs open with a unit ledger; declared
  agent count must equal ledger row count; two-or-more independent units
  with no fan-out and no `NON-PARALLELIZABLE` clause is an automatic
  CRITICAL under Auditor Dimension U6.
- **Standing — Pattern 14 (2026-08-17).** A validator is not installed
  until shown to fire in the real execution path. Verification that
  inspects a written artifact cannot see whether the artifact functions.
- **Standing ruling — 2026-09-02 — NO NAMED SPOKESPERSON ON RANK-AND-RENT
  PROPERTIES. STANDING, SCOPED.** Scope: the rank-and-rent
  lead-gen portfolio only — DCI, LGM, GCI, and any future property built
  on the same model. These sites are deliberately neutral: leads route to
  a contractor partner who must be switchable on a dime, so no page may
  carry a human byline, persona, or named author. Publisher-level
  attribution only. This ruling does NOT apply to the Director's other
  ventures — agency work, SaaS, or any property with a real operating
  business behind it. Those are separate and unaffected. Within the
  rank-and-rent scope this is settled and not revisited. It closes the
  AI-content supervision disclosure question, Vahe PCO-02, and the
  author-identity gap. Recorded portfolio-wide, same ruling, same
  wording: `denvercoloradoinsulation.com/docs/board/ground-truth.md`,
  `longmontcoloradoinsulation.com/docs/board/ground-truth.md`,
  `greeleycoloradoinsulation.com/docs/board/ground-truth.md`. This is the
  canon home for the ruling; the property files cross-reference back here.
- **Standing ruling — 2026-09-27 — "LAST UPDATED" PUBLISHES THE LAST
  VISIBLE-TEXT CHANGE DATE; "LAST REVIEWED" IS NEVER DERIVED.** A
  modification date is computable from the artifact. A review date is a
  claim about a human act, and no instrument can produce one — the claim
  gate spec says exactly that of its own R8: *"Whether a review actually
  happened. A date is a claim about a human act. The gate can prove a date
  is impossible or contradicted; it cannot prove a review occurred."* So a
  footer may publish the date the page's VISIBLE TEXT last changed,
  computed; it may publish a review date only where a review actually
  happened, asserted by whoever did it. Markup-only and JSON-LD-only
  commits move neither, which is why R8 part (d) compares visible text
  rather than raw lines. Not hypothetical: R8 catches only dates that are
  too OLD, so batch-stamping a newer one is the cheapest way to green, and
  on DCI at `ea6c86a` 73 of 75 pages published a 2026-09-27 review date of
  which **39 had no visible-text change that day**. Verify:
  `grep -n "A date is a claim about a human act" ops/claim_gate/RULES_SPEC.md`
  → line 2991, and
  `grep -n "73 of 75 pages publish a 2026-09-27" ops/claim_gate/RULES_SPEC.md`
  → line 3005. Also recorded as a review criterion in
  `METHODS/DESIGN_REVIEW.md` §4 (Neglect signals).
