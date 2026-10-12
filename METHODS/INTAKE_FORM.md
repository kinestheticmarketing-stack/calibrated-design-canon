# INTAKE_FORM.md — the Director's form for a new property

*A method-level specification under [Calibrated Vibe Coding](../CVC.md).*
*One form per property, filled by the Director before any build starts.
Research fills the other half, the market pack; the Director fills this.*

The form mirrors `ops/genesis/intake.schema.json` field for field, in
schema order. Check a filled form, its market pack and its facts registry
together from the property repo, with the path to canon:
`python3 ops/genesis/validate_genesis.py ops/intake.json ops/market_pack.json facts/registry.json`
(run as `<canon>/ops/genesis/validate_genesis.py`; exit 0 valid, 1 invalid,
2 unreadable).

---

## Fields

All twelve fields are required. A field that may be empty says so.
Examples are the Exampleton FIXTURE values; Exampleton is not a real
business.

1. **`property_code`** — three uppercase letters naming the property.
   Example: `"EXT"`.
   Why: the system names the property's lanes, files and facts keys with
   it, and tells it apart from its siblings by it.

2. **`domain`** — the lowercase hostname the site is served from, no
   scheme, no path.
   Example: `"exampletoninsulation.example"`.
   Why: canonical URLs, the sitemap and schema markup are all built on it.

3. **`display_name`** — the business name as visitors see it.
   Example: `"Exampleton Insulation (FIXTURE)"`.
   Why: rendered in page titles, headers and structured data.

4. **`city`** — the business's home city.
   Example: `"Exampleton (FIXTURE)"`.
   Why: local copy, the address block and market research are anchored on
   it.

5. **`state`** — two-letter uppercase state code.
   Example: `"CO"`.
   Why: decides which energy code, utilities and programs research looks
   at.

6. **`service_area_towns`** — the towns the property will serve, each
   named once. May be empty, which means "research decides".
   Example: `["Exampleton (FIXTURE)", "North Exampleton (FIXTURE)", "Sampleville (FIXTURE)"]`.
   Why: one town page is built per entry, and the validator requires each
   listed town to appear in the market pack.

7. **`services`** — what the contractor actually does, as slugs from the
   portfolio's shared list. At least one, each named once. Only these
   service pages, and only these navigation entries, get built; list a
   service the contractor does not perform and the site promises work no
   one will do.
   Example: `["attic", "air-sealing", "blown-in", "energy-audit"]`.
   Why: the build generates service pages and navigation from this list
   and nothing else.
   The 27 allowed slugs:
   - `air-sealing` — Air Sealing
   - `attic` — Attic Insulation
   - `basement` — Basement Insulation
   - `blower-door-test` — Blower Door Testing
   - `blown-in` — Blown-In Insulation
   - `builders-contractors` — Insulation for Builders and Contractors
   - `cathedral-ceiling` — Cathedral Ceiling Insulation
   - `cellulose` — Cellulose Insulation
   - `crawl-space` — Crawl Space Insulation
   - `dense-pack-cellulose` — Dense-Pack Cellulose Insulation
   - `duct` — Duct Insulation
   - `duct-sealing` — Duct Sealing and Insulation
   - `energy-audit` — Energy Audit
   - `fiberglass-batt` — Fiberglass Batt Insulation
   - `garage` — Garage Insulation
   - `hybrid-flash-batt` — Hybrid Insulation
   - `knob-and-tube` — Knob-and-Tube Safe Insulation
   - `new-construction` — New Construction Insulation
   - `radiant-barrier` — Radiant Barrier Installation
   - `removal` — Insulation Removal
   - `rim-joist` — Rim Joist Insulation
   - `rodent-damaged` — Rodent-Damaged Insulation Replacement
   - `rodent-remediation` — Rodent-Damaged Insulation Replacement
   - `spray-foam` — Spray Foam Insulation
   - `vermiculite-abatement` — Vermiculite Insulation Abatement
   - `vermiculite-asbestos-removal` — Vermiculite / Asbestos Insulation Removal
   - `wall` — Wall Insulation

   The list is the union of the slugs the three existing properties use,
   kept as-is; `rodent-damaged` and `rodent-remediation` share a plain
   name.

8. **`tracking_phone`** — the public call-tracking number, in E.164 form
   (`+`, country code, number, no spaces).
   Example: `"+15555550123"`.
   Why: rendered on every page and in every click-to-call link, so calls
   are attributed to this property. Buying it is a Director step (below).

9. **`lead_destination`** — where submitted leads are delivered.
   Addresses and numbers only.
   - **`emails`** — at least one address that receives every lead.
     Example: `["leads-fixture@example.invalid"]`.
     Why: with no address, a lead has nowhere to go and is dropped.
   - **`sms`** — E.164 numbers that get a text alert per lead. May be
     empty when no text alert is wanted.
     Example: `["+15555550124"]`.
     Why: a text reaches the contractor faster than an inbox does.

10. **`sibling_properties`** — the property codes of the other portfolio
    properties. May be empty; must not include this property's own code
    (the validator rejects that).
    Example: `["DCI", "LGM", "GCI"]`.
    Why: the system uses it to avoid cross-property duplicate content and
    to share canon between siblings.

11. **`industry_pack`** — the industry content pack to build from. One
    value is allowed today.
    Example: `"insulation"`.
    Why: selects the page templates, service vocabulary and research
    checklists.

12. **`launch_notes`** — free text for the launch session. May be empty.
    No secrets.
    Example: `"FIXTURE property for canon tests; not a real business."`
    Why: handed to the builder as context the other fields cannot carry.

The form has no other fields. The schema rejects any extra field, which is
also what keeps a price, a dollar figure or a stray credential off it.

---

## No secrets on this form

No API key, token, password or SID goes in any field, including
`launch_notes`. The validator walks every string on the form and the
market pack and rejects any value shaped like a secret (a private-key
block, a provider key prefix, a long hex or base64 run), one error per
value. Secrets belong on the server environment only; see step C below.

---

## Only the Director can do these

Four steps need the Director's own accounts. No session can do them, and
none is authorized by a card moving columns.

**A. Buy the tracking number**

1. Sign in to the portfolio's call-tracking provider account.
2. Buy a new number, choosing a local number for the property's `city`
   (a local area code, not toll-free).
3. Point it at the contractor's real line in the provider's settings.
4. Record the number in E.164 form in `tracking_phone`.

**B. Create or verify the sending email**

1. In the email provider, start domain sender verification (domain
   authentication) for the property's `domain`.
2. The provider lists the DNS records it needs. Add each one, exactly as
   given, at the domain's DNS host.
3. Wait for DNS to propagate, then run the provider's verification check
   until the domain shows verified.
4. Send one test message from the verified sender to an address in
   `lead_destination.emails` and confirm it arrives.

**C. Put secrets on the server environment, never in a repo**

1. The secrets are: the email provider's API key, and the SMS provider's
   credentials (account identifier, auth token, sending number), when
   `lead_destination.sms` is non-empty.
2. They go in the server's environment file for this property, and
   nowhere else: not on this form, not in any repo, not in a card, not in
   a chat.
3. The Executor-run deploy process writes them there; the Director
   supplies the values to that process directly, at deploy time.
4. After deploy, confirm the site sends a test lead end to end (Phase 8
   of [PROPERTY_GENESIS.md](PROPERTY_GENESIS.md)).

**D. Verify Search Console after launch**

1. In Search Console, add the property's `domain` as a domain property.
2. Verify it with the DNS TXT record Search Console gives you, added at
   the domain's DNS host.
3. Once verified, submit the sitemap (`https://<domain>/sitemap.xml`).

---

## Where the filled form lives

A filled form lives in the new property's PRIVATE site repo, at
`ops/intake.json`, never in canon. It carries the real lead addresses and
numbers; canon is public.

The only intake in canon is the Exampleton FIXTURE at
`ops/genesis/fixtures/exampleton/intake.json`, which is entirely fictional.

Verify: `python3 ops/genesis/validate_genesis.py ops/genesis/fixtures/exampleton/intake.json ops/genesis/fixtures/exampleton/market_pack.json ops/genesis/fixtures/exampleton/facts/registry.json` -> exit 0.
