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
   consumer-facing pages at all — Greeley already hit a version of this
   with EFI: the blower-door NACH50 threshold for Xcel's program is
   published only on `poweredbyefi.org`, never on `xcelenergy.com`.
   Check every surface a claim could render on before concluding a
   number is unsourceable.

6. **Verify the blower-door metric and threshold from a primary
   source, per utility.** Metrics are utility-specific, not
   niche-specific, and they do not convert 1:1. Xcel states its
   requirement in **NACH50** (normalized air changes per hour at 50
   pascals). Atmos states its requirement in **CFM(50)** (cubic feet
   per minute at 50 pascals). Both are air-leakage metrics; neither
   converts trivially to the other, and "20% reduction" on one utility
   is not evidence of "20% reduction" on another. **Never carry one
   market's metric into another market's copy** — this is a locked rule
   in both existing properties' `COPY_VOICE.md` files and should be
   treated as load-bearing, not stylistic.

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
   gap under Phase 8 rather than authoring it inside a port.

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

---

## PHASE 8 — KNOWN-INHERITED GAPS DECLARATION

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

If a genesis wave's own research surfaces a *new* portfolio-level gap
not on this list, add it here for the next genesis rather than only
recording it in the new property's own `STATE_OF_PROJECT.md` — this list
is the point of continuity between genesis waves.

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
