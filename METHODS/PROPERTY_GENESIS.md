# PROPERTY_GENESIS.md

*A method-level specification under [Calibrated Vibe Coding](../CVC.md).*
*Source-of-truth checklist for standing up a new lead-gen property from
an existing control property, across the full sequence from market
research to live engine registration.*

Cross-references: `denvercoloradoinsulation.com/WEBSITE_ARCHITECTURE.md`
(infrastructure-sequenced setup checklist, the first version of this
document), `greeleycoloradoinsulation.com/WEBSITE_ARCHITECTURE.md`
(content-integrity-sequenced replication checklist, the second),
`greeleycoloradoinsulation.com/DEPLOYMENT_RUNBOOK.md` (the first
execution-verified provisioning record either property has produced),
[ARCHITECT_DISCIPLINE.md](ARCHITECT_DISCIPLINE.md) (workflow discipline
for the roles named below).

---

## Why this document exists

Two properties now exist. Each wrote its own genesis checklist, and each
checklist is right about the thing its author had just been burned by.

DCI's checklist is **infrastructure-sequenced** — 20 steps, domain to
contractor pitch, written by someone standing up hosting for the first
time. It has no market-verification step at all, because DCI's market
research happened informally, before the checklist existed to record it.

Greeley's checklist is **content-integrity-sequenced** — six steps,
written in hindsight after a real near-miss (see Phase 1 below): market
facts do not transfer between properties, and the failure is silent
until a rebate page ships wrong numbers. It says almost nothing about
infrastructure, because by the time it was written, `DEPLOYMENT_RUNBOOK.md`
existed as a separate document for that.

Following only DCI's checklist reproduces Greeley's near-miss at the next
property. Following only Greeley's checklist leaves a Director staring at
a blank VPS with no ordered path to a live site. This document merges
both, in the order a Director and Executor actually need them, and adds
the sections neither predecessor had reason to write yet.

**Roles used below:** Director makes market-fact and scope calls;
Executor runs commands and writes code. Either role can be filled by a
human or an agent; the document doesn't assume which.

---

## PHASE 0 — CLOCK CHECK

Do this before writing a single dated artifact — a commit, a
`STATE_OF_PROJECT.md` entry, a citation retrieval date, anything with a
timestamp a future audit will trust.

**Verify the local machine's timezone matches the VPS's timezone** (or at
minimum, matches the *intended* wall-clock date for the market you're
building). Run:

```bash
date                              # local machine
ssh root@<vps-ip> 'date'          # VPS
```

If they disagree by more than a few minutes, fix the local clock's
timezone before proceeding. A misconfigured local timezone silently
forward-dates every provenance record written that session — this
happened on 2026-08-10, when a Mac set to Asia/Manila (UTC+8) forward-dated
an entire day's commits across both existing properties to 2026-08-11
while the work happened 2026-08-10 Denver time. It was caught only
because commit author timestamps (which git derives independently of the
hand-typed date strings in the file bodies) disagreed with the prose. A
genesis wave produces many dated firsts in one sitting — first commit,
first citation retrieval, first `STATE_OF_PROJECT.md` snapshot — so a
clock error here contaminates more surface area than it would on an
ordinary day.

---

## PHASE 1 — MARKET VERIFICATION (before any code)

This is Greeley's checklist item 2, expanded. It is the highest-leverage
step in this entire document — a wrong answer here invalidates content
work done downstream, and wrong rebate copy is a False Claim risk, not
just a rewrite.

**Do this before writing a single line of niche-specific copy, before
running a single generator, before touching `COPY_VOICE.md`.**

1. **Identify the electric provider and the gas provider separately.**
   They are not the same company by default, and their programs do not
   transfer. Denver: Xcel for both. Greeley: Atmos gas, electric
   unresolved (see below). Longmont's research surfaced a third shape:
   Longmont Power & Communications (municipal electric) plus Xcel gas.
   Assume nothing carries over from the control property's utility
   structure.

2. **Check for municipal utilities on the city's own site.** A
   municipal or member-cooperative utility (an LPC, a REA) will not
   appear in an investor-owned utility's service-territory map, because
   it is a different entity serving a carved-out area within or
   adjacent to the IOU's territory. If you only check Xcel's or Atmos's
   map, a municipal utility's customers are invisible to your research
   and you will misattribute their utility. Greeley hit a milder version
   of this: the Colorado Energy Office's GIS layers showed *overlapping*
   Xcel and Poudre Valley REA polygons at every Greeley test point, and
   PVREA's own territory page named the county without naming the city
   — the result was `NOT SETTLED — do not name one`, and the property
   ships with electric rebates absent rather than guessed.

3. **Verify each surrounding town independently.** A candidate service
   area spanning several towns can span several *different* utility
   pairs. Do not assume the anchor city's utility pair holds for its
   suburbs. Longmont's candidate area spans four different utility
   pairs across the towns under consideration. Greeley confirmed gas
   service for only three of nine candidate towns
   (`ATMOS_CONFIRMED_TOWNS`: Greeley, Evans, Eaton) and explicitly does
   not assert Atmos service for the other six without a primary source.

4. **Establish the rebate program structure, not just the amounts.**
   Amounts change quarterly; structure is architectural. Determine
   which shape applies:
   - **Percentage-with-cap, per category** (Atmos/Greeley: 75% of cost
     up to a flat dollar cap, different cap per insulation category —
     attic, wall, crawlspace, floor, rim joist — plus a flat-dollar
     air-sealing line item).
   - **Flat-rate-with-cap** (a fixed dollar amount regardless of
     project cost, up to a ceiling).
   - **Per-square-foot.**
   - **A stack of conditional programs**, where eligibility for one
     program depends on completing another within a time window
     (DCI/Xcel: a base rebate, plus a Whole Home Efficiency Bonus that
     requires 3 qualifying measures within 2 years, plus a Combo Bonus,
     plus an income-qualified IQ tier, each with its own eligibility
     gate).

   The structure determines whether the new property can reuse an
   existing rebate-checker's branching logic or needs its own. A
   percentage-with-cap-per-category structure and a conditional-stack
   structure are not the same math, and porting one property's
   calculator constants onto the other's structure produces numbers
   that are wrong in a way spot-checking a few outputs will not catch
   (see Phase 3, wrong-parent risk points).

5. **Identify the program administrator.** It may not be the utility
   itself. Longmont's electric rebates are delivered by **Efficiency
   Works**, a third-party consortium administrator — a citation source
   *type* neither DCI nor Greeley has had to model before (DCI cites
   Xcel's own pages directly; Greeley cites Atmos's own pages directly,
   plus EFI as Xcel's *contracted fulfillment administrator* for the
   one Xcel-adjacent disclosure it carries). When the administrator is a
   third party, the authoritative program terms may live on the
   administrator's site and never appear on the utility's own
   consumer-facing pages at all.
   ~~Greeley already hit a version of this with EFI: the blower-door
   NACH50 threshold for Xcel's program is published only on
   `poweredbyefi.org`, never on `xcelenergy.com`.~~
   **[SUPERSEDED 2026-08-24 — this worked example is false in both of its
   claims. Xcel does not state the requirement in NACH50, and the
   threshold *is* published on `xcelenergy.com`, on Xcel's own first-party
   rebate sheet. See the correction note at the end of this phase. The
   general point this example was attached to still stands — a
   third-party administrator's site can carry terms the utility's own
   pages omit — but EFI/Xcel is not a demonstration of it, and Longmont's
   Efficiency Works administrator must be checked on its own evidence,
   not on this precedent.]**
   Check every surface a claim could render on before concluding a
   number is unsourceable.

6. **Verify the blower-door metric and threshold from a primary
   source, per utility.** Metrics are utility-specific, not
   niche-specific, and they do not convert 1:1.
   ~~Xcel states its requirement in **NACH50** (normalized air changes
   per hour at 50 pascals).~~
   **[SUPERSEDED 2026-08-24 — Xcel states its requirement in `CFM 50`,
   verbatim `20% Reduction in CFM 50`. See the correction note at the end
   of this phase.]**
   Atmos states its requirement in **CFM(50)** (cubic feet per minute at
   50 pascals). NACH50 (normalized air changes per hour at 50 pascals)
   and CFM50 are both air-leakage metrics; neither converts trivially to
   the other, and "20% reduction" on one utility is not evidence of "20%
   reduction" on another. **Never carry one market's metric into another
   market's copy** — this is a locked rule in both existing properties'
   `COPY_VOICE.md` files and should be treated as load-bearing, not
   stylistic. **The rule is unchanged by the 2026-08-24 correction; only
   its illustration was wrong.** Note also that Xcel and Atmos landing on
   the *same* metric is a coincidence of these two markets, not a
   portfolio fact — treat it exactly as Phase 1 item 8 treats Denver and
   Greeley sharing Climate Zone 5B: a lucky match at genesis N is not an
   assumption at genesis N+1.

   **Verify which rebate row the threshold attaches to, too.** A
   blower-door threshold is not automatically a condition on the whole
   weatherization offer. On Xcel's residential rebate sheet the `20%
   Reduction in CFM 50` requirement attaches to the **air sealing** row
   only; the **insulation** rebates are qualified by post-job R-value,
   not by leakage reduction. Copy that binds the threshold to "the
   insulation and air sealing rebate" as a single unit states a
   requirement the utility does not impose on insulation, and is a false
   claim even when the number itself is right. Record metric, threshold,
   *and* the specific rebate row each one governs.

7. **Verify federal and state program status fresh, at genesis time,**
   not by inheriting the control property's most recent quarterly
   check. Programs terminate. Section 25C (the federal residential
   energy-efficiency tax credit) terminated for property placed in
   service after 2025-12-31 — live at DCI's genesis, dead by Greeley's
   and dead for Longmont. Colorado's HEAR program closed for the Front
   Range region on 2026-04-28. A program note copied forward from the
   control property's `COPY_VOICE.md` is a claim about *that
   property's* verification date, not a current fact.

8. **Verify the IECC climate zone from a primary source**, never by
   assuming it matches the control property. Denver and Greeley happen
   to share Climate Zone 5B, which made this step invisible at Greeley's
   genesis — it looked like nothing needed checking. That is exactly
   the condition under which an unverified assumption survives
   undetected into a document like this one. Check it explicitly every
   time; do not let a lucky match at genesis N become an assumption at
   genesis N+1.

**CORRECTION — 2026-08-24 — Xcel blower-door metric (supersedes the
NACH50 wording in items 5 and 6 above).**

The Xcel worked example used in items 5 and 6 was verified against Xcel's
own first-party document today and found false in both of its claims. The
original wording is left in place above, struck and bracketed, so the
error stays legible; read it as superseded by this note.

- **Document:** `24-02-205 CO Res Rebate Summary Information Sheet.pdf`,
  served from Xcel's own `xcelenergy.com` staticfiles host — a
  first-party utility surface, not an administrator's.
- **Retrieval:** fetched live on 2026-08-24, HTTP 200, text extracted
  with `pdftotext`.
- **What it says, verbatim:** `20% Reduction in CFM 50` — CFM 50, with a
  space. The string `NACH` **appears nowhere in the document.**
- **Therefore:** (a) Xcel does **not** state its requirement in NACH50;
  it states it in **CFM50**. (b) The threshold is **not** "published only
  on `poweredbyefi.org`" — it is published on `xcelenergy.com`, on
  Xcel's own sheet.
- **Scope of the requirement:** the `20% Reduction in CFM 50` line
  qualifies the **air sealing** rebate row. Xcel's **insulation** rebates
  are qualified by post-job R-value, not by leakage reduction. The two
  are separate rows with separate qualifying conditions, and a genesis
  instruction that binds the blower-door threshold to "the insulation and
  air sealing rebate" as one unit would seed a false claim at the next
  property. Item 6 above now says so explicitly.
- **Corroboration:** this matches the 2026-08-10 CFM50 correction already
  recorded in the DCI repo at `COPY_VOICE.md:152` and
  `_shared_components.py:256-278`. DCI's shipped copy was corrected; this
  canon document was not, and stayed stale for two weeks. The canon was
  the wrong surface, not the property.

**What survives unchanged:** the locked rule itself — *verify the
blower-door metric and threshold from a primary source, per utility;
never carry one market's metric into another market's copy.* Nothing in
this correction weakens it. The rule is, if anything, better evidenced
now than before, because **the rule was broken by its own illustration**:
a canon document teaching per-utility primary-source verification carried
an unverified, second-hand metric for one utility, and asserted a
negative about a first-party surface ("never on `xcelenergy.com`") that
nobody had checked. A worked example is a claim and needs a citation like
any other claim. Cite the document, quote the string, and date the fetch.

**Still open (not fixed by this row):** `NACH50` remains in
`METHODS/RECEIPTS.md` and `RETROSPECTIVES/2026-08-10-citation-integrity.md`.
Those are historical-record surfaces and need their own supersession
pass; they are not corrected here.

**Reconciliation note:** DCI's 20-step checklist has no equivalent to
this phase — market facts are swapped as checklist item 11
("Update COPY_VOICE.md with niche-specific facts"), sequenced *after*
domain purchase, DNS, VPS provisioning, database setup, SendGrid,
Twilio, and systemd (items 1–9). Followed literally, that order commits
real infrastructure spend and irreversible naming decisions before
checking whether the market's rebate structure is even representable in
the existing architecture. This document breaks that ordering
deliberately: Phase 1 gates all niche-specific *content* work, but not
infrastructure provisioning, which does not depend on market facts and
can proceed in parallel (see Phase 5's parallelism note, itself drawn
from `DEPLOYMENT_RUNBOOK.md`'s explicit "run j and k in parallel with
content work" instruction).

6. **Check the domain's prior life before writing any copy.** Query
   `web.archive.org/cdx/search/cdx?url={domain}&matchType=domain&output=json`
   and run `whois` on the apex. Record the result **even when it is clean** —
   a recorded clean result is what closes the question; an unrecorded one
   leaves it open forever. Note that WebFetch is blocked from
   `web.archive.org`; use `curl`.

   This is not hypothetical. `denvercoloradoinsulation.com` is a
   **re-registered expired domain**: WHOIS Creation Date 2026-05-01, but 43
   Wayback captures from 2011 of a prior site — Bestway Insulation, a Denver
   insulation contractor in the same vertical and the same metro. Fifteen
   years dormant in between. That was discovered on 2026-08-18, months after
   launch, by an audit looking for something else. It is benign — legitimate
   contractor content, no spam footprint, all captures HTTP 200, and fifteen
   years decays any signal in either direction — but nobody knew, and until
   somebody checked, no ranking anomaly on that property could have been
   confidently attributed to anything.

   Longmont and Greeley both return **zero captures** and were registered
   2026-08-05: genuinely fresh domains, now recorded as such.

   Record in `STATE_OF_PROJECT.md`: capture count and date span, what the
   prior site was if any, WHOIS Creation Date, and an explicit
   benign/not-benign judgement. If prior use is found, note that checking for
   surviving legacy inbound links requires backlink tooling and is
   BLOCKED-BY-BUILD-ORDER under Pattern 11 — flag it for the post-build-order
   phase rather than skipping it silently.

7. **`COPY_VOICE.md` is authored in this phase, not later.** The market facts
   verified in steps 1-5 are written into a locked, dated fact set before any
   generator references it. Longmont shipped with **seven** live code
   references to a `COPY_VOICE.md` that did not exist — two of them backing
   hard-fail contract clauses (the atomic-answer word band and the
   determiner-uniqueness rule) — and authoring it retroactively cost a full
   ledger row four waves later. Written here it costs one session and no
   reference is ever dangling.

---

## PHASE 2 — PARENT SELECTION

A new property does not fork wholesale from one control property. State
the rule and apply it explicitly, in writing, before cloning anything:

> **Fork the file-and-architecture shape from the property with the
> better clone mechanics for the parts that don't touch market content.
> Take named overrides from whichever property's utility/rebate
> structure actually matches the new market**, per Phase 1's findings.

This is a deliberate two-source fork, not a single-parent clone. Name
the source for each half in the new property's `WEBSITE_ARCHITECTURE.md`
lineage table (the pattern Greeley's document establishes) so a future
genesis wave can audit which half came from where.

**Known divergences between the two current parents**, as of this
writing:

| Has it | DCI | Greeley |
|---|---|---|
| `_artifact_grep.sh` (rendered-output leakage gate) | No | Yes |
| Derived `areaServed`/`FOOTER_CITIES` from one registry (no drift) | No — three independent hand-maintained lists of different lengths | Yes |
| `DEPLOYMENT_RUNBOOK.md` (execution-verified provisioning record) | No | Yes |
| `process_steps` data wired into `jsonld_howto()` | Yes — called per service page | No — defined, never called (Director-copy-gated, not a bug) |
| Multi-program conditional rebate-checker branching (JS `programs.push()` per eligibility rule) | Yes — built for Xcel's stacked-program structure | No — Atmos's flat percentage-with-cap-per-category structure doesn't need it |
| Phone-number substitution reachable from a single constant | No — a raw-string JS block hard-codes the literal in two error paths, invisible to the constant swap | Yes — fixed here via a `__PHONE_DISPLAY__` placeholder + module-level assert |

For a market with a single-utility conditional-program stack (DCI's
shape), fork the calculator branching logic from DCI even if forking
everything else from Greeley. For a market with Greeley's flat
percentage-with-cap shape, the reverse. Do not assume the newer property
is uniformly the better parent — Greeley is architecturally cleaner in
several respects (see table) but structurally cannot represent DCI's
conditional-stack rebate math without rebuilding it, because Greeley
never needed to build it.

---

## PHASE 3 — WRONG-PARENT RISK POINTS

These are the specific files where cloning from the architecturally
wrong parent produces **silently wrong output** — code that runs, that
generates a page, that looks plausible, and states an incorrect number
or claim with no error at any stage:

- **`ALIVE_REBATES` / the rebate-constants module.** A value swap
  (new dollar amounts, same shape) is not sufficient if the new market's
  program is structured differently from the parent's — a
  percentage-with-cap value dropped into a flat-rate-with-cap template
  computes a different, wrong number, and nothing about the generator
  run signals an error.
- **`CITED_SOURCES` utility keys.** Keyed by administrator/utility
  identity. Cloning the control's keys and relabeling them is not the
  same as building keys for the new market's actual administrator — see
  Phase 1 item 5's Efficiency Works case, where the citation *source
  type* itself differs from either existing property's pattern.
- **The calculator's rebate-math constants and branching shape.** See
  Phase 2's table. A conditional-stack calculator forked onto a
  flat-percentage market will offer bonuses that don't exist there; a
  flat-percentage calculator forked onto a conditional-stack market will
  under-report what the customer actually qualifies for.
- **The rebate-checker's branching shape** specifically — `if`/`push`
  eligibility logic is architecture, not content. Swapping the strings
  inside an existing branch is safe; adding a new eligibility rule that
  the parent's control-flow was never built to express is not a value
  swap, it's a rebuild.
- **`ENTITY_DESCRIPTION`, `organization_schema()`, `person_schema()`,
  `jsonld_service()`.** Name, area served, and `knowsAbout` are all
  market-specific and must be rebuilt, not swapped-and-forgotten — a
  stale `knowsAbout` list is a schema claim about expertise the new
  property doesn't yet substantiate with content.
- **Any rebate-hub generator.** If the parent's rebate hub was built
  to explain a program stack (DCI's Power Ahead Colorado gating logic,
  keyed off DRCOG membership) and the new market has no equivalent
  gated program, the hub either needs a genuinely new structure or needs
  to not exist yet. Do not force-fit a hub page around a program
  structure the new market doesn't have.

**The general rule:** if the *architecture* differs between candidate
parents for a given file, a value swap is insufficient — treat it as a
rebuild-from-scratch item (Greeley's `WEBSITE_ARCHITECTURE.md` calls
this category "Rebuilt from scratch for this market" and lists it
explicitly; do the same in the new property's lineage table).

---

## PHASE 4 — LOCAL SCAFFOLD

1. **`.gitignore` first commit, before any source file.** Greeley's
   checklist item 1. Do this before anything else touches the local
   repo, including the market-verification research if that research
   produces local files (CSV pulls, API responses) that shouldn't ship.
2. Decide the fork per Phase 2; clone the chosen file-and-architecture
   shape into `~/code/{niche}-{city}/`.
3. Swap the identity constants that must be distinct per property
   regardless of parent choice: `SITE_BASE` (domain), phone number
   (verify the swap is reachable from a single constant — see Phase 2's
   table on the raw-string JS bug), sender domain, database name and
   user, and the intended port (checked live, not assumed — see Phase
   5's port note).
4. `env.template` filename: no leading dot. A dotted template filename
   (`.env.template`) collides with the secret-exclusion rule in
   `.gitignore` and gets silently swallowed, requiring a negation carved
   into the secret block to recover. Name it `env.template` from the
   start and the negation rule is never needed.
5. **PORT THE BRAND ASSETS. The clone copies code and skips assets.**
   Cloning a parent brings its generators, its templates, and its
   `<head>` — every one of which *references* image files that do not
   come with it. Nothing in the toolchain fails: generators run clean,
   MD5 manifests match, the deploy verifies, and the site serves 200 on
   every page. The nav renders a broken image and the first person to
   find out is whoever opens a browser.

   **Evidence: this has now shipped broken twice.** Greeley launched
   with no logo and was fixed after the fact; Longmont launched the
   same way and was fixed on 2026-08-12. Two for two on every property
   cloned to date. It is not a per-property oversight — it is what the
   clone step does by construction, and it will do it to Fort Collins
   and Loveland unless this step runs.

   Do this in the scaffold phase, **before Phase 6 content build**, so
   no page is ever generated against assets that don't exist:

   1. **Enumerate from the parent's rendered HTML, not from its
      directory listing.** The authoritative list is what the markup
      asks for — grep every `src=`, `href=`, and `url()` in the
      parent's generated pages, plus the absolute URLs in `og:image`
      and `twitter:image`, which a root-relative grep misses.
   2. **Port each one.** Byte-copy anything generic (the mark-only
      favicons transfer untouched — verify with matching MD5s).
   3. **Adapt property-specific text and nothing else.** Where an SVG
      carries a city name, change the city name — same typeface, same
      colors, same dimensions, same layout. Confirm a longer city name
      still fits the `viewBox` rather than assuming it does.
   4. **Match the filenames the HTML actually references.** A
      correctly-made logo at the wrong filename is still a broken
      image.
   5. **Verify every reference resolves before generating any page.**

   **An asset carrying rendered marketing copy or factual claims is not
   portable and must not be faked.** The `og-image` is the known case:
   the parent's contains a tagline, a utility name, and a local
   building-code claim. Swapping the city name into it produces a brand
   asset asserting the wrong utility and an unverified code adoption —
   silently plausible and wrong, which is worse than the 404 it
   replaces. Route it to whoever owns copy and record it as a declared
   gap under Phase 9 rather than authoring it inside a port.

9. **Output paths derive from the script's own location, never from a
   hardcoded home-relative string.** Use
   `os.path.dirname(os.path.abspath(__file__))` as the root; never
   `os.path.expanduser('~/code/{property}/public')`.

   This is a **portfolio-wide inherited defect**, not a one-property mistake:
   Denver has 12 such assignments, Longmont 10, Greeley 16 across 14 files —
   **38 assignments in 36 files**. Every generator in the portfolio writes to
   a fixed absolute path regardless of the directory it is invoked from, and
   `_similarity_check.py` additionally hardcodes a **sibling** property's
   path. A read-only sweep once wrote into a live repo exactly this way and
   came out clean only because regen is deterministic — the accidental write
   reproduced byte-identical output. That was luck, not safety.

   **A new property clones whatever pattern the parent has.** If the parent is
   not fixed first, the new property inherits 10-16 fresh instances on day one.

10. **`STATE_OF_PROJECT.md` opens with the genesis itself as its first dated
    entry, and every later wave appends in the same commit as the work it
    describes.** The property-history record is half of the audit-intake
    artifact (see the standing rulings near the end of this document); a
    history with holes supplies wrong context to the next audit. All three
    current properties self-declare undocumented waves, which is why that
    tactic scores APPLIED-UNTRACKED rather than APPLIED portfolio-wide.

11. **Ship `_postbuild_check.py` with the first regen, canary-proven.** Five
    validators — `check_interactive_js`, `check_placeholders`,
    `check_duplicate_labels`, `check_credentials`, `check_jsonld` — wired into
    `regen_all.sh` and each proven by injecting a violation, confirming the
    check raises and refuses to write, then restoring. Identical in all three
    current properties, but each arrived by retrofit after a defect shipped.
    At genesis it is a file copy.

---

## PHASE 5 — INFRASTRUCTURE PROVISIONING

This phase can run **in parallel with Phase 6** (content build) once
Phase 2's parent decision is made — infrastructure provisioning does not
depend on market facts, only on the domain name and property identity
being decided. `DEPLOYMENT_RUNBOOK.md`'s own execution record for
Greeley made this explicit: SendGrid setup and VPS provisioning ran
alongside content work because neither blocked the other. Do not
serialize infrastructure ahead of content by default, as DCI's flat
20-step list implies by ordering — only serialize the specific steps
that have a real dependency (certbot needs DNS to have propagated;
`.env` needs the SendGrid key from step 1 below).

1. **Buy domain; set DNS A record → VPS IP.**
2. **Check live port availability on the VPS before writing a number
   into anything.** Do not assume the next sequential port from the
   control property. Greeley's `env.template`, `index.js`, and
   `STATE_OF_PROJECT.md` all specified port 3002 by the DCI-style
   "increment from the last one" convention — and 3002 was already
   occupied by an unrelated service on the shared host. The number is
   written into five places that must move together (`env.template`,
   `index.js` fallback, the systemd unit, the nginx config,
   `STATE_OF_PROJECT.md`); if the live check comes back occupied,
   **halt and report** rather than picking a replacement unilaterally —
   the replacement has to be right the first time across all five
   files.
3. **Provision the VPS directory:** `/root/{property}/public/`.
4. **Copy the backend** (`index.js`, `package.json`) from the chosen
   parent; install dependencies; verify every required module resolves
   before moving on.
5. **Create the database and user**, isolated from every other
   property's database, in the shared Postgres container if one exists
   on the host. Generate the password before writing the `.env` file,
   not during.
6. **Apply the receipt-trail schema** (the DDL both properties ship,
   e.g. `lead_submissions_log.sql`) directly against the new database,
   even though the app also creates it at boot — surfacing a schema
   problem here is cheaper than surfacing it on the first real lead.
7. **SendGrid: new scoped API key, separate from every other
   property's key.** Never reuse a key across properties — a compromised
   or revoked key on one property must not be able to take down another.
   Scope it to Mail Send only; nothing else needs to be reachable with
   this credential.
8. **SendGrid: authenticate the sending domain**, add the resulting
   DNS records (typically 2 DKIM CNAMEs, 1 return-path CNAME, 1 DMARC
   TXT, plus 2 more if link branding is enabled). Confirm via `dig`
   from the local machine before checking SendGrid's own verification
   UI — this isolates a DNS propagation problem from a SendGrid
   configuration problem. **Do not add a root-domain SPF TXT record**
   unless inbound-email forwarding is actually configured for this
   property (see item 12) — a second SPF record on a domain that
   already has one is a hard authentication failure, not a harmless
   duplicate.
9. **Populate `.env`** with the DB credentials, the SendGrid key, and
   generated admin/health/salt secrets. `chmod 600` — the file holds a
   live mail credential and a database password. Do not put
   local-research-only credentials (e.g., a Census API key used for
   ACS housing-age pulls) into the VPS `.env` — if the running app never
   reads it, it doesn't belong on the server.
10. **Create and start the systemd service**, modeled on the chosen
    parent's live unit (read it directly off the host with
    `systemctl cat`, don't reconstruct it from memory or from the
    parent's docs, which can drift from what's actually deployed).
11. **nginx + certbot, in the order certbot actually requires:** a
    plain port-80 vhost first (certbot needs it to answer the ACME
    challenge), then certbot to obtain the certificate and rewrite the
    vhost with `listen 443 ssl` and the redirect, then — as a third,
    separate pass — HSTS and a `www`→apex redirect split into its own
    `443` server block if the parent property canonicalizes to the
    apex. Treat this as three passes, not the one line DCI's checklist
    implies ("set up nginx config + certbot"); certbot's own rewrite
    behavior does not add HSTS or split `www` out on its own, and adding
    those by hand-editing a certbot-managed file requires a backup
    written first, to a directory *outside* `sites-enabled/` (a stray
    backup copy left inside `sites-enabled/` gets loaded by nginx too
    and produces conflicting-server-name warnings).
12. **Decide whether inbound email forwarding is needed** (e.g.
    Improvmx) for this property specifically — don't carry it forward
    automatically because the control property has it. Greeley
    deliberately has none.
13. **Check what else the host is actually running before assuming a
    provisioning mechanism.** A host can have a control-panel tool
    installed (Plesk, cPanel, etc.) that manages only a subset of the
    sites on it, with the rest hand-managed. Greeley's provisioning
    found Plesk installed and managing exactly one unrelated domain on
    the shared host, while all eleven others — including both
    insulation properties — were hand-written nginx + certbot, which
    Plesk's own config merely `include`s. Provisioning through the
    control-panel tool by default would have put the new property on a
    different serving topology than its siblings. Check the live host
    state; don't assume the tool that's installed is the tool that's
    used.

12. **Create the Search Console and Bing Webmaster properties the day the
    domain resolves — before content authoring finishes, not after launch.**
    Verify GSC by DNS TXT, submit the sitemap, import into Bing. **Record the
    registration date in `STATE_OF_PROJECT.md` at the moment of
    registration.**

    **This is the highest-value item in this phase and its cost of delay is
    unrecoverable.** Search Console does not backfill: data from before
    verification does not exist and cannot be retrieved. Greeley verified on
    launch day (2026-08-06, DNS TXT transcript on file) and is simply waiting
    for data to accrue. Longmont launched 2026-08-12 with its runbook reading
    "Search Console and Bing verification — NOT DONE," and every day between
    launch and registration is a permanently missing day of history. Denver,
    verified longest, is the only property that can run the entire drop- and
    performance-diagnosis block at all.

    Record the date. Two of three current properties cannot say when they
    registered, because nobody wrote it down.

    Console properties are **instrumentation of a site you already own** and
    are explicitly **not** external SEO — Pattern 11's build-order block does
    not apply to them. It applies to GBP, link building, directory submission
    and paid rank tooling.

13. **Every collection source ships with its read surface in the same wave.**
    No source is installed collecting until something can read it.

    All three current properties have a `pageviews` table that has collected
    since 2026-08-12 and a query surface that is still an open queue item. A
    source nothing reads has not been verified to collect and is
    indistinguishable from a broken one. Three properties have been accruing
    data for weeks that nobody can confirm is arriving. The read is trivial to
    add later; the unverified interval is not recoverable.

    Minimum read surface: collection liveness (row count, most recent
    timestamp, time since), views per path per day, views per path all time,
    and the join to `leads.source_page` for conversion per page. Ship it as
    `ops/pageview_queries.sql` alongside `ops/canary_check.js`.

14. **Read the indexing report the day the console verifies.** Not at first
    harvest. Indexing data needs no accrual; **performance data does.**
    Greeley conflated the two — it verified 2026-08-06, deferred everything to
    a harvest scheduled Oct-Nov 2026, and recorded its 30-page URL submission
    as "not independently re-verified — recorded as reported." Whether those
    30 pages actually indexed has been answerable since launch day and, at the
    time of writing, twelve of its pages sit crawled-currently-not-indexed.
    Splitting the two reads is free and closes a two-month blind spot.

---

## PHASE 6 — CONTENT BUILD

Gated entirely on Phase 1's findings. Do not start this phase until
market verification is complete and the parent decision (Phase 2) is
made.

1. Clone the chosen architecture shape (Phase 2); rebuild content from
   scratch under the anti-duplication mandate — content is never a
   value-swap of the parent's prose, even where the underlying
   architecture is unchanged.
2. **Run the artifact-leakage grep against rendered output before the
   first content commit.** This is Greeley's `_artifact_grep.sh` —
   scoped to `public/` only (source docs and lineage tables are exempt
   by design, since they must name the control property to document
   the lineage), checking for the control property's name, domain,
   phone number, slug convention, elevation framing, and suburb names.
   Any allowlist exception (e.g., a real third-party organization's
   proper noun that happens to contain a control-market place name)
   must be Director-granted and recorded inline in the script, not
   silently added.
3. **Run the outbound-link checker against the parent's `CITED_SOURCES`
   before cloning them**, so known-dead citations are not propagated to
   the new property on day one. A citation that died on the control
   property dies identically on a clone that inherits the same URL.
4. **Similarity-score every re-skinned page against its counterpart**
   on the parent property; rewrite until it clears the floor. A page
   that reads as a value-swap of the parent's prose is a duplication
   risk even when every fact in it is correct for the new market.
5. **Hard separation rules, ported unchanged from Greeley:** no
   cross-links between sibling properties in either direction; no
   shared runtime constants (each repo imports nothing from any
   other); the lineage relationship is documented in
   `WEBSITE_ARCHITECTURE.md` and `STATE_OF_PROJECT.md` only, never in
   rendered output.

6. **Read the live SERP for each target term before the page is written, and
   record the read.** Top-3 results, what they are, and a competition
   assessment of that set — recorded in-repo, gating the term.

   Denver is the only property that has done this and it did so
   **retroactively**: the vermiculite-removal page exists because a Search
   Console query read found REMOVAL-intent demand (24 queries, 873
   impressions, avg pos ~70) landing on an IDENTIFICATION-intent page that had
   already shipped. That is a page-shaped correction to a mistake a
   five-minute pre-authoring SERP read would have prevented. Longmont and
   Greeley author from house convention and have not paid this cost yet only
   because neither has the data to reveal it.

   This step also prevents the failure Phase 7 catches downstream: authoring
   two pages against the same head term.

---

## PHASE 7 — PRE-LAUNCH VERIFICATION

Every check below is something one of the two existing properties
learned by shipping the mistake first. Run all of them before the first
production deploy, not a sample.

- **Title uniqueness across every page.** Greeley shipped a duplicate
  `<title>` between the homepage and its primary money page — same
  string, both pages, on the market's head term — and it survived
  undetected until a dedicated SEO-corpus audit found it. A single grep
  for duplicate `<title>` content across the full page set catches
  this in seconds; run it as a standing gate, not a one-time audit
  finding.
- **Every asset reference in the rendered HTML resolves to an existing
  file.** Extract every `src=`, `href=`, and `url()` target from the
  full generated page set — plus the absolute `og:image` and
  `twitter:image` URLs, which a root-relative grep silently skips — and
  confirm each one exists on disk, then again live after deploy with a
  status check per URL. **This has shipped broken twice** (Greeley and
  Longmont both launched with no logo; see Phase 4 item 5). Every other
  gate in this list passes while it is broken: the generators are
  deterministic, the manifests match, every page returns 200. A missing
  image is invisible to all of them because the *page* is fine — only
  the thing it points at is absent. This is the check that catches it,
  and it belongs at both the scaffold gate and here.
- **Every function the parent invokes has a call site here, or a
  written deferral reason.** Greeley cloned `jsonld_howto()` and never
  wired it in — not a bug, because wiring it requires `process_steps`
  copy authored per service first, but it needs a recorded,
  Director-visible deferral reason (`STATE_OF_PROJECT.md`, gated on
  copy work), not silence. An unwired inherited function with no
  deferral note reads identically to a genesis mistake until someone
  checks.
- **Run the outbound-link checker against the parent's `CITED_SOURCES`
  before cloning** (restated from Phase 6 — it belongs at both the
  content-build gate and the pre-launch gate, since new dead links can
  accumulate between the two).
- **Artifact-leakage grep before the first content commit** (restated
  from Phase 6, same reason).
- **Similarity-score every re-skinned page** (restated from Phase 6).
- **Two-run MD5 determinism.** Run every generator twice and diff the
  output; a non-deterministic generator (one that embeds a generation
  timestamp, or iterates a dict in insertion-order-dependent ways) will
  produce byte-different HTML on identical inputs, and that difference
  is invisible until someone diffs two runs deliberately.
  `sitemap.xml`'s `<lastmod>` is the one intentional exception — it
  reflects a truthful content-review date, not the regeneration date,
  and should never be regeneration-timestamped either.
- **Live verification of engine registration, not just marking it
  done.** Google Search Console verification, Bing Webmaster Tools
  verification, and IndexNow key deployment are each a *claim* until
  checked against the live host: curl the IndexNow key file's public
  URL and confirm it echoes the key; confirm GSC's HTML verification
  tag actually shipped in the generated `<head>` (it must go into the
  generator, never hand-edited into a rendered file, or the next
  regeneration erases it silently); confirm the sitemap submission
  actually registered in each console's UI rather than trusting that
  the submission command exited zero.
- **Bash, not zsh, for any deploy step that word-splits a file list.**
  zsh does not word-split a newline-separated variable the way bash
  does; an unquoted file-list variable reaches `scp` as a single
  malformed filename and the deploy silently half-completes. This is a
  real incident on the control property. Wrap the deploy command in
  `bash -c '...'` explicitly rather than relying on the operator's
  default shell, and capture `scp`'s exit status directly — never
  through a pipe, which makes `$?` report the pipe's last command
  instead of `scp`'s actual result.
- **Verify deploy by MD5 manifest, not by watching the transfer
  complete.** A partial `scp` can leave the server serving stale files
  while every individual command appeared to succeed. Diff a local and
  remote MD5 manifest of every deployed file before considering the
  deploy done.
- **Run the `site:` sweep at launch and fix its cadence.** Query
  `site:{domain}` against the full page set, record the result in-repo, and
  set the cadence (per wave, or per N new pages).

  This has been flagged since 2026-08-10, re-affirmed, and is **still unrun on
  all three properties** — the portfolio's longest-standing open gap. The
  pre-publish cannibalization gate that does exist is title-level only and
  self-declares that it "does not catch body-level topical overlap." A cadence
  set at genesis is kept; one added later competes with work that feels more
  urgent every wave.

  **Run the internal near-duplicate check in the same pass.** The portfolio
  ships a shingle-based similarity instrument (`_similarity_check.py`, PASS
  strictly below 0.30) that exists on **one** property and has only ever
  compared that property against its parent. Pointed inward at the same
  threshold, every property fails: Denver 107 page-pairs at or above 0.30
  (105 of them suburb-vs-suburb, max 0.456), Longmont 21, Greeley 6. The gate
  that would have caught this exists, works, and had only ever been aimed at
  the one comparison that passes. Ship it measuring **both** directions.
- **Every audit artifact opens with a declaration block.** Type, purpose,
  scope, instrument, date, structure:

      > **AUDIT TYPE:** health | quick-win | drop-diagnosis | strategy | corpus-alignment | remediation
      > **PURPOSE:** the concrete question this audit answers
      > **SCOPE:** what was examined, and what was deliberately excluded
      > **INSTRUMENT:** what did the examining
      > **DATE:** YYYY-MM-DD
      > **STRUCTURE:** why the sections are ordered as they are

  Thirteen audit artifacts exist across the three current properties and
  **none** carries one. Nine of the thirteen portfolio-wide gaps found by the
  2026-08-18 corpus audit reduce to this single absence: the portfolio has
  excellent per-defect **gates** and no declared **audits**. A gate fires
  continuously and automatically; an audit declares what it is and can
  therefore be judged complete or incomplete.

  Audits typed `health` or `drop-diagnosis` order their technical findings by
  pipeline stage — **crawl → render → index → rank** — with each stage a
  heading even when empty. An empty stage is itself a finding: it means that
  stage was not examined.

  What this does **not** close: a whole-site manual read still has to be
  performed. The convention ensures that when one happens it is recognisable
  as an audit; it is not evidence that one happened.

---

## PHASE 8 — FUNCTIONAL PROOF (LAUNCH GATE)

Every check in this document up to this point verifies **the artifact
that was written**. Not one of them verifies that the page **functions**.
That distinction is not academic. Three Greeley calculator pages once
shipped with their tool JavaScript missing entirely, and passed
`regen_all.sh` at exit 0, two-run MD5 determinism, a full deploy manifest
match, and 12 of 13 live spot-checks — because a file whose JS is gone is
still a byte-identical, deterministically-generated,
successfully-transferred file. Every gate in Phase 7 was doing exactly
what it was built to do; none of them was built to press the button. The repair is on
the record: `greeleycoloradoinsulation.com` commit `20dcfe0`, "Fix:
restore calculator tool JS lost in the rebate-note guard rewrite",
followed by `e3d7243`, which added a post-build functional gate so the
same loss cannot ship silently again.

This phase cannot live inside Phase 7. Most of it **requires a deployed
site**: status codes, the `www`→apex redirect, and a real database
round-trip have no local equivalent, and simulating them locally would
re-create the exact class of error this phase exists to catch. It is the
gate between *deployed* and *declared live*. **A property is not live
until it passes**, and the launch record states the result in measured
numbers, not checkmarks. The proof pass run on 2026-08-19 across the
three live properties was the first thing in this portfolio's history to
test function rather than form.

- **Every URL in the sitemap returns 200, fetched from production.** The
  sitemap is generated from the generator's own page registry, so a page
  that was renamed, never transferred, or written to a path nginx does
  not serve still appears in it, correctly formed and confidently wrong.
  No earlier gate closes this loop: the MD5 manifest diffs the files that
  *were* deployed against the local build, which is silent about a URL
  the sitemap promises and the deploy never produced. The sitemap is a
  set of claims about the live host; only the live host can answer them.
- **Every internal link on every page resolves; zero 404s, counted as
  instances and as distinct targets.** A local link checker resolves
  hrefs against the build tree on disk, where a target either exists or
  doesn't. Production adds two failure modes the build tree cannot
  express — a file that was never transferred, and a path convention
  (trailing slash, extensionless URL, case) that the server resolves
  differently than the filesystem did. Report both numbers: total link
  instances checked and the count of distinct targets they resolve to.
  One 404 on a target linked from every page is a different-sized defect
  than one 404 linked once, and only the paired counts distinguish them.
- **Every calculator loads, ships parseable JavaScript, and binds its
  listeners — proven from production by `ops/functional_proof.sh` CHECK 3:
  the page returns 200, every inline script parses under `node --check`,
  and `addEventListener > 0`.** That is exactly what the launch gate
  proves, and no more: it does not press the button. The stronger claim —
  **each calculator produces a figure on default inputs, with that figure
  recorded** — is the browser canary's job
  (`denvercoloradoinsulation.com/ops/browser_canary.js`, weekly systemd
  timer on the VPS, all three properties, DCI commit `3254647`): it drives
  real Chrome to each tool page, clicks the tool's own button, reads the
  result the page's JS wrote into the DOM, and records it in the journal
  and as one JSON `figures` line, which the launch record cites. A tool
  whose default inputs are deliberately empty is recorded as `needs-input`,
  not as a figure, and the launch record says which. This is the check the
  Greeley incident demands, and it is the reason "the page returned 200"
  and "the page works" must be recorded as two different claims: the gate
  above proves the first, the canary's recorded figure proves the second.
  The absence of a console error is not a result; a tool whose script
  never loaded throws nothing at all, because there is no code present to
  fail. Recording the computed number is what makes the check falsifiable
  — it converts the tool from something that was looked at into something
  that was *run*, and it gives the next wave a value to regress against
  when the rebate constants change. Phase 7's determinism and manifest
  gates cannot reach either claim: they compare bytes, and the byte-level
  truth about those three pages was that they were perfect copies of files
  with the tool missing. (Wording aligned to the gate 2026-09-03, Option 2
  of `docs/board/done/phase8-calculator-criterion-unmet.md`.)
  **Identify tool pages structurally, never by slug.** The first
  implementation of this gate matched slugs against
  `calculator|quiz|comparator|checker|payback|r-value` and reported 16
  calculators where there are 14: `r-value-altitude-denver` and
  `r-value-altitude-greeley` are educational pages whose slug happens to
  contain `r-value`. The test that actually separates them is whether the
  page carries its own input controls **outside** the lead-capture form —
  a real calculator has them (7 inputs and 3 selects on the Denver
  r-value tool), an educational page has none. A launch record that
  overcounts its own tools is the same failure this phase exists to
  prevent, one level up: a number that was never checked against the
  thing it claims to describe.
- **Every form renders and its submit path reaches the database, proven
  by re-querying for the row.** Never accept the DOM success state as
  evidence. The backend returns success on discard branches, so **the DOM
  lies**: a green thank-you panel is a claim the front end makes about a
  request it dispatched, not a claim about a row that exists. The whole
  property's economic purpose is the lead path, and it is the one path
  where the visible signal and the actual outcome are decoupled by
  design. Proof is a `SELECT` run after the panel has already rendered,
  returning the specific row with its id and its mail-send result. The
  daily lead canary (see the standing ruling on OZA-39) is the ongoing
  form of this check; this is its first execution, at launch, before
  anyone is invited to the site.
- **Every JSON-LD block on every page parses, counted.** The post-build
  `check_jsonld` validator runs against the local build; what a consumer
  parses is what the host serves. Count the blocks and count the pages
  carrying them, then reconcile the difference — a page legitimately
  carrying no JSON-LD (a 404 page) and a page whose schema silently
  failed to emit are indistinguishable without the count. A schema block
  is machine-read by exactly the audiences this property is built for,
  and it is never rendered to a human who could notice it broke.
- **No page contains an unsubstituted placeholder token — checked
  against the served bytes from production, not the local build
  output.** `check_placeholders` proves the *new* build is clean. It says
  nothing about a stale file left on the server by an earlier partial
  deploy, which serves its old tokens indefinitely while every local gate
  passes on a build that never arrived. Greeley's `__PHONE_DISPLAY__`
  case (Phase 2's table) is the shape of the underlying defect; fetching
  the served bytes is the only version of the check that cannot be
  satisfied by a file the visitor will never receive.
- **`www` 301s to apex on every host.** Phase 5 item 11 warns that
  certbot's own rewrite adds neither HSTS nor a `www` split; the redirect
  is a third, hand-authored pass, which is precisely the kind of edit
  that gets verified by re-reading the config file. `nginx -t` proves the
  config parses, not that it redirects, and a config that loads cleanly
  while sending `www` to the same 200 the apex serves is a duplicate-host
  problem no local artifact can show you. Curl it and read the status
  line and the `Location` header.

**The 2026-08-19 proof pass, across the three live properties**, as the
reference shape for what a launch record should contain:

- **151 sitemap URLs** (72 DCI + 46 LGM + 33 GCI), all 200. This is 151,
  **not 154**. The portfolio has 154 pages; each property's `404.html` is
  correctly excluded from its own sitemap. A future genesis must expect
  **sitemap count = page count minus one** and treat an exact match as
  the anomaly worth investigating.
- **9,257 internal link instances** resolving across **151 distinct
  targets**, zero 404s.
- **14 calculators** (6 DCI + 4 LGM + 4 GCI), all parsing and binding
  listeners.
- **1,024 JSON-LD blocks** across 151 pages, zero parse failures. The 3
  pages carrying none are the three 404 pages — which is the reconciliation
  the count exists to make.
- **0 unsubstituted tokens** across 151 served URLs.
- **3 of 3 hosts** 301 `www`→apex.
- **Forms: 3 of 3 proven end-to-end to the database** — DCI lead id 24,
  GCI 18, LGM 11 — each with `sendgrid_result` `"accepted: HTTP 202"`,
  and each confirmed by an independent Postgres query issued *after* the
  DOM had already shown success.

**The gate is executable.** It ships as `ops/functional_proof.sh`, taking
a domain and a repo path and exiting nonzero on any failure, so it can be
chained ahead of a launch declaration the same way the build and test
gates are chained. **A gate never shown to fail is not a gate.**
Negative-control it the way `_postbuild_check.py`'s five validators were
canary-proven at genesis (Phase 4 item 11): break one thing deliberately
— unlink a sitemap URL, blank a calculator's script, point a form at a
dead endpoint — confirm the script exits nonzero and names the specific
failure, then restore. A functional gate that has only ever printed
success is indistinguishable from one that cannot fail, and that is the
same epistemic hole the three green Greeley calculators sat in. The
general form of that hole — the check that does run, exits clean, and
still cannot see the thing it certifies — is *What a green gate does
not prove*, below, which also records the open question of whether this
phase's calculator criterion is met by the gate that claims to satisfy
it.

---

## PHASE 9 — KNOWN-INHERITED GAPS DECLARATION

Some gaps are portfolio-level, not genesis-fixable — they exist because
no property in the portfolio has done the underlying work yet, not
because this specific genesis skipped a step. **Pre-declare these in the
new property's `STATE_OF_PROJECT.md` at genesis time**, sourced from
whatever the most recent cross-property alignment audit found, rather
than paying for a full corpus audit to rediscover the same known set on
day one. As of this writing, the declared set is:

1. **The `site:` cannibalization sweep has never been run** on any
   property in the portfolio.
2. **No SERP-read gate before content production** — pages are
   structured from house convention, not from the live ranking set for
   the target term.
3. **No hero/linkable content asset** on any property.
4. **No keyword / content-gap / decay tracker** — no committed in-repo
   tracker or repeatable sweep procedure exists yet anywhere in the
   portfolio.
5. **No named human author** — this is a Director-level decision (a
   real spokesperson, a bio page, `author` on Article schema nodes) that
   gates identically across every property and should be made once, not
   re-litigated at each genesis.
6. **No internal near-duplicate measurement.** The similarity instrument
   compares against the parent property only; no property measures its own
   pages against each other. Measured 2026-08-18: Denver 107 pairs at or above
   0.30, Longmont 21, Greeley 6.
7. **The first-party pageview counter has no read surface** on any property —
   it has collected since 2026-08-12 and nothing queries it.
8. **No property reads its Search Console indexing report as a cadence.**
9. **Generator output paths are hardcoded home-relative** on all three
   properties — 38 assignments across 36 files.
10. **No audit artifact carries a type/purpose declaration** — 13 of 13.

Pre-declaring this set at genesis is the corpus practice "review past audits
and reports," implemented ahead of time rather than after. It is the only
audit practice scored strictly satisfied on all three current properties.
Keep it.

If a genesis wave's own research surfaces a *new* portfolio-level gap
not on this list, add it here for the next genesis rather than only
recording it in the new property's own `STATE_OF_PROJECT.md` — this list
is the point of continuity between genesis waves.

---

## What a green gate does not prove

Phase 8 ends on a sentence this section exists to generalize: *a gate
never shown to fail is not a gate.* That rule covers the check that
cannot fire. It does not cover the check that fires, exits clean, and
was never able to see the thing it certified.

Over 2026-08-20 and 2026-08-21, during the rebate-figure remediation
wave across the three properties, the running tally reached **seven
blind instruments in two days** — instruments that reported clean, or
governed behavior, while never examining what they claimed to govern: a
duplication gate whose exclusion list named exactly the pages the
duplication lives on; a Search Console check that measured a
verification tag's presence and never its value; a `FORCE_STEP` guard
placed below its own `require('puppeteer-core')`, so on any host
without that dependency it exited before it ran; a documented citation
floor with no counter in any repo; a rendered sentence gated on the
shape of a citation list; a presence check that counted pages while
pages were losing two-thirds of their occurrences; and a ledger that
reconciles files against a scope bar written in pages. Two more from
the same two days were carded separately and belong to the same class:
a schema gate that parses JSON and cannot ask whether the JSON is true,
and a verification built from the same needle as the edit it was
verifying. Every one of them was correctly implemented. Every one of
them ran. Several had canaries.

**The organizing idea: an instrument answers a narrower question than
the claim that gets made from its result, and the blind spot is exactly
the gap between the two sentences.** The similarity gate proves *"no
two non-excluded pages score above the floor"* and was cited for
*"authored duplication is zero."* `check_jsonld` proves *"every block
is well-formed JSON"* and was cited for *"the structured data is
sound."* V3 proved *"the string `$400 for air sealing` does not appear"*
and was cited for *"the false figure is gone."* Nothing in those pairs
is a bug. The defect is the substitution of the second sentence for the
first.

**The diagnostic is mechanical, and it is one line of writing.** Before
an instrument's result is allowed to close anything, write down, *in
the instrument's own units*, the sentence it actually proves. Then
write the sentence being claimed. If they differ, the difference is
what ships broken. Every rule below is a place that gap opens: in the
**corpus** the instrument reads, in the **unit** it counts, in the
**predicate** it tests, in the **provenance** of the instrument itself,
and in the case where there is no instrument at all.

This is the companion to `ARCHITECT_DISCIPLINE.md` PATTERN 14 (*a check
that passes its own test can still be blind*), not a restatement of it.
Pattern 14 is about the check that never runs in the real path, and
about verification that inspects an artifact rather than its behavior.
These twelve rules are about the check that does run, is reachable, is
honest about its own result, and still cannot see the thing it
certifies.

Figures below are dated. Where the wave's original measurement was
re-run against the live repos on 2026-08-25 before promotion, both
numbers are given — per rule 9, and per the correction at the end of
Phase 1: a worked example is a claim and needs a citation like any
other claim.

---

**Where the gap opens, first: in the CORPUS the instrument reads.**

1. **An exclusion list is scoped to the question the gate was built
   for. Cited for a different question, it excludes exactly the
   evidence.** `_intra_similarity_check.py:67` reads
   `EXCLUDE = {'404.html', 'privacy.html', 'contact.html',
   'about.html'}` — **byte-identical in all three property repos**
   (re-verified 2026-08-25). Those four are the pages ported
   near-verbatim between siblings. The gate skips them, then reports
   zero.

   The exclusion is defensible for *intra-property* scoring: a privacy
   page and a contact page should not flag as duplicates of each other.
   It is exactly backwards for *cross-property* scoring, which is the
   risk this portfolio actually carries — three geo-cloned sites in one
   vertical. The gate was built for one question and cited as answering
   the other.

   Measured on authored content with chrome stripped, 2026-08-20:
   `privacy.html` shared a **726-word identical run** with both
   siblings (1046 / 1031 / 989 words). Re-measured 2026-08-25, after
   the privacy pages were rewritten in a later wave: DCI↔GCI **1001
   words** of 1321 / 1264, DCI↔LGM 256. The number moved; the blindness
   did not.

   **The blast radius is the part that matters.** "Authored duplication
   is ZERO on all three properties" was asserted repeatedly, including
   in `docs/board/ground-truth.md` on all three properties during the
   corpus re-score wave. That claim was true of the non-excluded pages
   and was never true of the corpus. Every verdict resting on the
   instrument is affected: DCI and GCI both scored two audit tactics
   APPLIED from it and both are now RETRACTED; LGM scored NOT-APPLIED
   because that agent had stopped trusting the gate — the only correct
   duplication verdict on the board, correct for the right reason.

   **Rule:** split the exclusion by axis. Keep it for the
   intra-property run; include the four in the cross-property run and
   treat a high score there as expected-and-accepted or as a finding —
   but **measure it**, and let the number be visible rather than
   absent. Canary it: plant a known duplicate pair inside an excluded
   file and confirm the cross-property run reports it. The current gate
   reports zero.

   **Correction owed elsewhere in this document:** Phase 9 item 6
   declares "no internal near-duplicate measurement" as a
   portfolio-level inherited gap, and Phase 7 says the shingle
   instrument "exists on one property." Both predate
   `_intra_similarity_check.py`, which exists on **all three** (the
   parent-comparison `_similarity_check.py` is GCI-only — verified
   2026-08-25). The honest statement of the gap is not that intra
   measurement is absent; it is that it ships on every property and is
   blind on the four pages that carry the duplication. Phase 9 item 6
   needs its own supersession pass and does not get one here.

2. **A verification SET must contain at least one instrument whose
   scope is the COMPLEMENT of the change set, measured at occurrence
   level against a pre-change snapshot.** The load-bearing fact from
   the 2026-08-21 wave: V4, V8, V9, V10 and V11 all answer *"what
   happened to the thing we meant to change."* Not one answers *"what
   happened to everything else."* A verification set composed entirely
   of target-scoped instruments **cannot see collateral damage no
   matter how many instruments are added** — which is why V4 through
   V11 all passed while two separate collateral losses were live, and
   why one complement-scoped diff found both.

   Removal work is where this binds hardest, but it is **not
   removal-specific**: any edit whose blast radius is wider than its
   intent has the same hole. At a genesis this is the rule that governs
   the first sweeping regeneration — a constant swap or a template edit
   touches every page, and every gate in Phase 7 is pointed at the
   pages you meant to change.

---

**Second: in the UNIT the instrument counts.**

3. **A presence check must assert the QUANTITY it protects, not merely
   non-zero presence.** V4 was added specifically to catch content
   vanishing beside a removal target. It reported `CFM50 S0=17 now=17
   OK` on all three properties. At that moment three LGM area pages had
   lost two-thirds of their occurrences — `insulation-lafayette` 5→3,
   `insulation-louisville` 3→1, `insulation-niwot` 3→1, with
   "participating contractor" and "reduced tier" dropping in the same
   proportions on the same pages. No page fell to zero, so no page left
   the *contains-the-anchor* set, so V4 saw 17 both times and passed.
   It was blind to exactly the failure it was built for. The loss was
   caught instead by an occurrence-level sentence-inventory diff the
   Auditor demanded *after the count in the report failed to move.*

   If the risk is partial loss, page-level membership is the wrong
   unit: count occurrences, compare against the pre-change snapshot,
   and fail on any decrease that is not an enumerated target.

   **Corollary, and the reason this recurs:** an instrument added to
   catch a specific failure must be **canary-proved against that
   failure**, not against its own happy path. V4 had a positive canary
   — delete an anchor entirely, prove it flags — and none for partial
   loss, which is the case it existed for.

   **Rules 2 and 3 are one failure seen from two sides and must not be
   collapsed.** Rule 3 is about the INSTRUMENT: a single check must
   assert the quantity it protects. Rule 2 is about the SET: the
   collection must cover the complement of the change. Sharpening V4 to
   occurrence level would have caught the CFM50 loss and still would
   not have caught a loss in content nobody thought to register as an
   anchor — that needs rule 2. A complement-scoped diff at SET
   granularity (which is what shipped first) misses partial drops —
   that needs rule 3. **Fixing either alone leaves a live hole.**

4. **Where the unit of permission and the unit of prohibition differ
   and the mapping is one-to-many, the gate must derive the mapping.**
   The 2026-08-21 kickoff's OUT OF SCOPE list read *"DO NOT TOUCH: the
   two LGM doorway pages (lafayette 37.1%, niwot 39.3%)."* R2's edits
   changed both pages. V9 reported "LGM 27 files, every rendering
   instance accounted for" and did not halt — **correctly**, because
   the S-GATE ledger is file-scoped and listed `_area_pages.py`, which
   renders both of those pages among others. No file was unlisted, so
   V9's halt condition never fired.

   The defect is not a missed halt. It is that **the ledger silently
   superseded the kickoff's own page-scoped scope bar and the Final
   Report never said so.** V9 answers "was every changed FILE on the
   ledger"; the bar asks "was any forbidden PAGE changed." Different
   questions over different units. A file-scoped permission grants
   page-scoped access it was never asked to grant. (`git show 00b2d56
   --name-only` on LGM shows both pages; the ledger named
   `_area_pages.py`.) Content impact was neutral — both pages carried
   only the legitimate change, restored byte-identical — which is the
   point: the finding is about the instrument, not the outcome.

   This is not portfolio-specific. It holds for any build where
   permission and prohibition are expressed in different units with a
   one-to-many mapping between them: source file to rendered page,
   template to instance, migration to row, config to environment. A
   generator-driven property is the one-to-many case by construction,
   which is why it belongs in this document.

   **Rule:** when a scope bar names units of type B and the ledger
   authorizes units of type A, the gate derives the A→B mapping and
   either marks the covering A units no-touch, or records explicitly
   that the bar is superseded and has the Director rule on it at the
   gate. **Silence is not a ruling.**

---

**Third: in the PREDICATE the instrument tests.**

5. **Validate schema as TRUE OF THE PAGE, not merely parseable.**
   `check_jsonld` confirms every structured-data block is well-formed
   JSON. It structurally cannot know whether the block's claims match
   the document. LGM ships `SpeakableSpecification.cssSelector` naming
   `.quick-facts` on `public/index.html` and `public/resources.html`
   where the markup count is **zero** — selector 1 / markup 0 on both,
   re-verified 2026-08-25 and still live. The JSON parses perfectly, so
   the gate is green. GCI is 1 / 1 by luck of authoring, not by gate.

   DCI shipped the identical defect, found it only by hand-running
   Google's Schema.org validator, fixed it, and added `check_speakable`
   so that class fails the build. **DCI has six postbuild validators;
   LGM and GCI have five** — `grep -c "def check_"` returns 6 / 5 / 5
   and `check_speakable` exists only on DCI, re-verified 2026-08-25.
   The hardening did not propagate, which is its own genesis lesson:
   Phase 2's lineage table records what was forked at genesis, not what
   the parent fixed afterwards. A fix landed on one sibling is not a
   fix landed on the portfolio.

   **Rule:** for every assertion a schema block makes about the
   document — a selector, an image URL, a price, a `dateModified` —
   assert the referent exists. This **extends** Phase 8's "every
   JSON-LD block on every page parses, counted"; it does not retire it.
   Parseability and truth are two claims and need two checks. Canary
   the new one by planting a selector that matches nothing and
   confirming the build reds.

6. **A conditional that governs whether PROSE renders must read a fact
   about the subject, never the membership or shape of a citation
   list.** This is the subtype that is not a check at all: rendered
   copy silently gated on a data-structure side effect. LGM's
   `_generate_service_pages.py` read

   ```python
   xcel_relevant = any('XCEL' in k for k in rebate_cite_keys)
   ```

   which made *"is this page Xcel-relevant"* and *"does this page cite
   Xcel"* the same question. They are not: the first is a fact about
   the market's utility structure, the second an artifact of which
   citation keys survive an edit. Removing one false citation flipped
   the flag on 4 pages and deleted the wayfinding sentence pointing
   readers at Xcel's own live page — the honest sentence, and exactly
   what must survive when a stale figure is removed.

   Decoupled 2026-08-21 to `xcel_relevant =
   bool(service.get('xcel_applicable')) or
   _asserts_xcel_applies(service)`, with the old line preserved as a
   comment directly above it, and proven immune: stripping a different
   `XCEL`-prefixed key from 8 services on a scratch copy left the
   sentence rendering on all 13 pages. **`ew_relevant` on the next line
   is still the raw pattern** (`any('EFFICIENCY_WORKS' in k for k in
   rebate_cite_keys)`, re-verified 2026-08-25) — reported rather than
   changed, because no `EFFICIENCY_WORKS` key was disturbed by that
   wave. DCI and GCI have zero instances; it is LGM-only.

   **Rule:** citation bookkeeping may decide whether a *citation*
   renders. It must never decide whether a *sentence* does. At a
   genesis, audit every generator conditional that wraps prose and ask
   which fact it is standing in for.

7. **A skipped check is not a passed check.** `ops/functional_proof.sh`
   gives two different answers to what a skip scores. At `:215-217`,
   when `node` is unavailable, check 3 is skipped and recorded **FAIL**
   with its reasoning stated in the message itself — *"a skipped check
   is a hole in the gate, not a pass."* At `:365`, in LOCAL_MODE, check
   7 (`www`→apex) is skipped and recorded **PASS**. Both cannot be
   right, and the script has already written down which one is.
   (Verified in the DCI copy, 2026-08-25: the two branches still
   disagree.)

   The practical risk is a LOCAL_MODE run reporting **7/7 PASS** having
   executed six checks — precisely the "green means nothing" failure
   this gate exists to prevent, and a launch record that overstates its
   own coverage.

   **Rule:** a third outcome. `SKIP` is neither PASS nor FAIL, prints
   distinctly, and the summary states `N passed / M skipped` rather
   than folding skips into either bucket. Exit non-zero only on real
   failures, but never let a skip read as coverage.

---

**Fourth: in the PROVENANCE of the instrument itself.**

8. **A verification instrument must be constructed INDEPENDENTLY of the
   edit instrument. Derive the check from the target CONCEPT, never
   from the edit's matcher.** This was the wave's worst defect and it
   survived six Auditor gates. R3 removed the false `$400` air-sealing
   figure using the needle `$400 for air sealing`. V3 then verified the
   removal **using the same needle** and reported `DCI $400 = 0`.

   That result was true of the needle and false of the figure.
   `xcel-insulation-rebate-guide-denver.html` phrased it *"…attic
   insulation at 30% of project cost up to $500, wall insulation at 30%
   up to $350, and air sealing at 30% up to $400"* — a complete,
   correct enumeration carrying the false figure in a phrasing the
   needle never matched. It was live through every prior gate and every
   gate reported clean, because the check inherited the edit's blind
   spot exactly. **A check constructed from the edit's own matcher is
   not measuring the world; it is measuring the edit's assumptions back
   to itself and returning them as confirmation.**

   No other instrument could reach it either, and the reasons are worth
   keeping: the complement-scoped occurrence diff hunts content that
   *decreased*, and this content never changed; the positive-presence
   check asserts anchors *survive*, and this survived — that was the
   problem; ledger reconciliation checks *changed files*, and the file
   was never changed. The defect lived in the complement of the change
   set **and did not move**, which makes it invisible to a diff by
   construction.

   Derived from the concept instead — *"a dollar figure asserted as a
   rebate amount"*, so sweep bare `$400`, `$500` and `$350` in any
   phrasing and classify each occurrence as rebate-figure or cost-range
   — the same corpus that had reported `0` reported **9 surviving
   figure instances on DCI**, including three malformed sentences the
   removals themselves had produced. Re-run 2026-08-25: the sweep
   prints 21 instances and every one is the tail of a `$200-$500` or
   `$100-$500` cost range, because the range guard only looks *forward*
   of the match. Zero rebate-asserted figures survive; the removal
   holds — and the concept-derived instrument needs the same
   granularity discipline it teaches.

   **Corollary:** the edit's matcher and the check's matcher should be
   written by different reasoning, ideally at different times. An
   instrument authored immediately after an edit, by the reasoning that
   produced it, is co-extensive with that edit's blast radius.

9. **A claim about an instrument's reach must travel with its
   demonstration, in the same breath — and a principle derived from a
   genuine finding is not thereby true.** Not a canary run at some
   point before; a proof attached to the claim in the sentence that
   makes it, **because the claim is what gets believed downstream.**
   Three times in one wave an instrument's reach was overstated: V4 was
   called adequate (it counted pages); the sentence-inventory diff was
   called occurrence-level when it was a SET difference (proven blind —
   `before=3, after=1, set-difference returns False`); and D3 was
   asserted clean with no demonstration, in the same section that
   cleared it — it passed when finally canaried, but the claim had
   already been believed for a full turn on no evidence. **Every one of
   those corrections came from being asked for the INVOCATION rather
   than the CONCLUSION.**

   The harder half is about the lesson rather than the instrument. In
   the same wave a general principle was drafted from a real finding,
   correctly diagnosed, competently investigated — and **retracted as
   false**, because the model that supposedly failed had predicted 7
   and the true post-repair answer was 7. It was one turn from being
   written into canon. **The test is not whether the investigation was
   rigorous. The test is whether the CORRECTED STATE MATCHES THE
   MODEL'S PREDICTION**, and operationally, *a number that should have
   moved and did not is the signal.* The wrong lesson survived a
   competent investigation and died the moment someone asked why the
   count was still 8 after the fix that should have made it 7.

   **Rule for review:** when a wave proposes a new general principle,
   require the post-remediation measurement that the principle
   predicts. A principle whose predicted state was never measured is a
   hypothesis wearing a conclusion's clothes. This section was written
   under that rule: every figure above that could be re-measured was
   re-measured on 2026-08-25 before promotion, and two of them had
   moved.

---

**Fifth: where there is no instrument at all.**

10. **A documented standard with no validator is not a standard. It is
    a preference.** The seven blind instruments above are the visible
    half of the problem; the invisible half is the standard nothing
    ever checked. From the same two days:

    - **The GSC verification check** measured the *presence* of a
      `google-site-verification` tag, never its validity. A
      `REPLACE_WITH_…` placeholder served in production and scored as
      verified. (Phase 7's own bullet — "confirm GSC's HTML
      verification tag actually shipped in the generated `<head>`" — is
      satisfied by a placeholder as written, and should be read as
      requiring the value, not the tag.)
    - **The FORCE_STEP guard** sat below `require('puppeteer-core')`,
      so on any host without that dependency it exited at
      MODULE_NOT_FOUND and never ran. **A non-zero exit for the wrong
      reason is indistinguishable from success.**
    - **The citation floor.** `COPY_VOICE.md:104` on LGM (`:66` on GCI)
      documents 2-3 external citations per page.
      `validate_citation_set` checks duplicate keys and duplicate
      labels only. **No count check exists in any repo** — re-verified
      2026-08-25: the only length comparisons in all three copies are
      the duplicate tests.

    **Rule:** every standard stated in prose names the validator that
    enforces it, or is explicitly marked UNENFORCED. A standard whose
    enforcement cannot be pointed at is a preference. And each
    validator carries a canary result proving it fails when it should —
    a check that has only ever printed success is indistinguishable
    from one that cannot fail.

    **A live instance inside this document.** Phase 8 requires that
    every calculator "produce a correct figure on default inputs — with
    that figure written into the launch record," and argues explicitly
    that recording the number is what makes the check falsifiable.
    `ops/functional_proof.sh` CHECK 3 proves the page returns 200, that
    its inline JS parses under `node --check`, and that
    `addEventListener > 0`. **It never runs a calculation and never
    records a figure.** So the shipped gate satisfies the weaker of the
    two claims Phase 8 says must be kept separate: it proves "the page
    returned 200," not "the page works." This is not a regression — the
    gate was always this. The defect is that Phase 8 asserts a
    criterion the gate does not implement, so a genesis reading Phase 8
    would believe its calculators were proven functional when only
    their syntax was. Two honest options, Architect's call: implement
    it (drive each calculator headlessly, read the computed figure out
    of the DOM, write it into the launch record — at the cost of a
    browser dependency in a script that is currently pure fetch+parse),
    or weaken Phase 8's wording to what the gate proves and move the
    figure-recording requirement to the browser canary, which already
    drives real Chrome. **Do not close it by quietly editing Phase 8 to
    match the code** — that is the direction that loses information.
    Tracked at `docs/board/ready/phase8-calculator-criterion-unmet.md`
    and deliberately left open here.
    **Resolved 2026-09-03 via Option 2:** PHASE 8's bullet now claims
    exactly what `functional_proof.sh` proves, and the
    figure-on-default-inputs requirement, with the figure recorded,
    relocated to `ops/browser_canary.js` (DCI commit `3254647`, proven in
    the real execution path the same day — 14 tool pages across three
    properties, figures in `journalctl -u browser-canary.service`); card
    closed at `docs/board/done/phase8-calculator-criterion-unmet.md`. This
    paragraph stays as the record of the defect and of how it was closed.

11. **A procedure with the authority of a ruling and no execution is
    untested code.** At the 2026-08-21 S-GATE the Director ruled that a
    removal target inside a JSON-LD string means removing the whole
    property or Answer object — not halting; that the block must remain
    valid JSON and still parse as valid schema.org; that this is
    verified **by parse, not by grep**; and that if removal would leave
    malformed JSON or an invalid block, the instance escalates and
    halts.

    **It was never exercised.** LGM's 4 target-carrying JSON-LD blocks
    went 4→0, but as a *side effect*: FAQ answers are generated from
    the same source strings as the prose, so editing the prose removed
    both surfaces in one edit. No property or Answer object was ever
    removed as a distinct action. DCI's target-carrying blocks at S0
    were 0. **Zero removals performed; zero parse-validations run
    against a post-removal block.**

    The procedure now has the authority of a Director ruling and the
    reliability of untested code. The first wave that genuinely needs
    it — a defect living in structured data but *not* in the prose that
    generates it — will run an unproven procedure under remediation
    pressure, on the surface AI engines read most literally. The
    generator coupling that made it unnecessary is not guaranteed: any
    hand-authored JSON-LD, or any block whose text diverges from its
    prose source, breaks it.

    **Rule:** a canon-adjacent procedure gets exercised once against a
    scratch copy before it is needed — here, plant a defect in an
    escaped, minified FAQPage answer, remove the Answer object per the
    ruling, prove with `json.loads` plus a schema.org validity check
    that the block still parses, and record the transcript. **So that
    the first real use is the second use.**

12. **Grammar is not truth: removing a false member from a true set
    creates a false set.** The most generalizable finding of the wave,
    and the one no instrument in the portfolio could have caught,
    because nothing evaluated meaning. R3 removed `$400 for air
    sealing` from enumerations reading *"pays 30% of project cost, up
    to $500 for attic insulation, $350 for wall insulation, **and $400
    for air sealing**."* The figure was false — Xcel's own sheet states
    $200. But **air sealing is a covered measure**: the program is
    literally named the *Xcel Energy Insulation and **Air Sealing**
    Rebate*, recorded 2026-08-21 as 72 DCI pages carrying 296 surviving
    mentions tying air sealing to rebate eligibility. (A looser
    `grep -c "air sealing"` on 2026-08-25 returns 71 pages and 881
    occurrences — a different measure, quoted only to show the fact did
    not go anywhere.)

    So the corrected sentence enumerated **two** covered measures where
    **three** exist. It read perfectly. Every grammar check passed.
    **And it asserted, by omission, that air sealing is not covered —
    which is also false.** Two instances refuted themselves inside a
    single sentence: `insulation-duct-sealing.html` — *"…up to $500 for
    attic insulation and $350 for wall insulation, by check after
    application, and its named measures are insulation and air
    sealing"*; `insulation-radiant-barrier.html` — *"…caps of $500 for
    attic insulation and $350 for wall insulation — and a radiant
    barrier is not one of the measures it names."* The second had been
    cleared one turn earlier as "no meaning added," on a check of the
    anaphor's grammar. The grammar was fine. The enumeration was a lie.

    **Why every instrument was green:** each of them hunts content that
    *disappeared*. A truncated enumeration is content that **remained**
    and became false by losing a neighbour — invisible to occurrence
    diffs, presence checks, ledger reconciliation and grammatical
    certification alike.

    **Rule:** after any removal, the containing sentence is evaluated
    for what it now **ASSERTS**, not merely whether it reads. If
    removal leaves a different claim, remove the whole claim. If
    removal drops a member from an enumeration that is still a member,
    the enumeration now lies by omission and the instance **HALTS**.

    **The remedy is the shape to copy.** Director ruling: drop the
    enumeration, keep the program. Not "restore the true figure" — $200
    is unsourced in-repo exactly as $400 was, so that fixes an
    unsourced-figure violation by committing another. Not "a separate
    cap for air sealing" — a phrase no source supports. **Dissolve the
    truncation rather than completing it: with no enumeration there is
    no omission.** What shipped is the claim the repo can support — the
    program exists, pays 30% of project cost against per-measure caps,
    by check after application. Verified 2026-08-25 on DCI:
    `grep -rn 'up to \$500 for attic insulation, \$350' public/*.html`
    returns nothing.

---

**What this binds at a genesis.** Every gate installed in Phases 4, 6,
7 and 8 gets the two sentences of the diagnostic written into the
launch record beside its result — what the instrument proves in its own
units, and what is being claimed from it. A new property inherits its
parents' gates *and their blind spots*, byte-identical, which is how one
`EXCLUDE` line reached three repos and how `check_speakable` reached
only one.

**Still open as of 2026-08-25, carried rather than closed** — each is a
live instance of a rule above, and none is fixed by promoting these
rules: the `EXCLUDE` blindness on all three properties (rule 1) and the
unqualified "zero authored duplication" line in three
`ground-truth.md` files; Phase 9 item 6's superseded wording (rule 1);
`check_speakable` on DCI only, with LGM's two live selector defects
(rule 5); `ew_relevant` on LGM (rule 6); the two skip policies in
`functional_proof.sh` (rule 7); Phase 8's calculator criterion versus
CHECK 3 (rule 10); and the unexercised JSON-LD removal procedure
(rule 11).

---

## What `DEPLOYMENT_RUNBOOK.md` adds that no checklist format captures

Both checklists above are pre-execution documents — ordered intentions.
Greeley's `DEPLOYMENT_RUNBOOK.md` is the first **execution-verified
record** either property has produced, and it earns a permanent place in
this document for three things no checklist format can carry:

- **Live-host findings that contradicted the plan going in** — the
  occupied port, the Plesk-vs-hand-managed-nginx question, an
  environment variable the kickoff assumed was configurable that turned
  out to be hardcoded in `index.js`. A checklist written before
  touching the host cannot know these; a runbook written *during*
  provisioning, with each fact traced to a live command's output, can.
- **A verified-state table with dated evidence**, not a checkbox — port
  number, service status with a start timestamp, TLS certificate serial
  and expiry, exact deployed file count, live HTTP probe results. This
  is what makes the runbook usable for the *next* redeploy on the same
  host, not just the first one.
- **Explicit non-blocking parallelism** ("run j and k in parallel with
  content work — they do not depend on Wave B") that a flat numbered
  checklist cannot express without either a false serial dependency or
  a separate diagram.

A genesis wave should produce a runbook of this shape as it executes
Phase 5 and Phase 7 above — not instead of following this checklist, but
as the dated, host-verified record of *how* this genesis's version of
those phases actually went, for the redeploy after this one.

---

## Standing rulings on two recurring audit tactics

Two tactics in the Zarr audit corpus recur on every owned property and were
left UNRESOLVED through two audit passes, because neither has an obvious
answer on a rank-and-rent property with no client. Both were settled
2026-08-18. They are recorded here so each genesis inherits the ruling rather
than re-litigating it.

**The client questionnaire (OZA-32).** Zarr states the purpose himself: *"the
client-needs/history dimension the site-side tools can't see."* The tactic is
about data a crawl cannot infer, not about the existence of a client. On an
owned property it is satisfied by a maintained **pair**: a locked market-fact
set (`COPY_VOICE.md`, Phase 1 step 7) plus a current property-history record
(`STATE_OF_PROJECT.md`, Phase 4 step 10). Scored satisfied when both exist and
the history covers recent waves; scored satisfied-but-untracked when the fact
set is current and the history has holes. It is never not-applicable merely
because there is no client — the rank-and-rent operator *is* the client, and
the intake becomes a maintained record instead of an interview.

**Verify critical tools are collecting (OZA-39).** Zarr scopes this himself:
*"Critical sources vary by site (GA, GSC, Bing usually; Merchant Feed for
e-commerce)."* "Critical" is a per-site determination made by the auditor, not
a fixed requirement for analytics. For this portfolio the critical set is
**Search Console, Bing Webmaster, the first-party pageview counter, and the
lead path**. Google Analytics and Microsoft Clarity are excluded by the locked
no-third-party-tracking policy and are **not scored as gaps** — scoring them
would import a tracking policy the corpus does not require and this portfolio
has deliberately rejected. What scores is **verification, not existence**: a
source that collects but is never read has not been verified, and an active
canary (the lead path's daily `lead-canary.timer`) is the strongest available
evidence.

---

## What this document is NOT

This is a checklist, not a substitute for judgment. Every phase above
assumes the Director and Executor read the *reasoning* attached to each
item, not just the imperative — several items exist specifically because
a literal reading of an earlier checklist ("swap the amounts," "set up
nginx config + certbot," "pick the next port") produced a real, shipped
defect the reasoning would have caught.

**Phase 1's findings can invalidate every later phase.** If market
verification turns up a rebate structure that fits neither existing
parent's architecture — a genuinely novel program shape, not a
value-level variant of one already modeled — the build is larger than a
clone, and no later phase in this document should be started on the
assumption that it's a half-day technical setup. Say so, in writing, in
the new property's kickoff, before Phase 2's parent-selection decision
gets made on a false premise.

---

*This document is a synthesis of two prior genesis checklists as of
2026-08-10 (DCI's `WEBSITE_ARCHITECTURE.md` setup checklist,
Greeley's `WEBSITE_ARCHITECTURE.md` replication checklist and
`DEPLOYMENT_RUNBOOK.md`). It should be updated the same way its sources
were: by the next genesis wave recording what this version missed.*
