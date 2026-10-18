# ops/checks — the shared BUILD check suite (Kickoff 44)

One suite of BUILD checks for all three properties (DCI, LGM, GCI), replacing
the per-site copies inventoried in [`INVENTORY.md`](INVENTORY.md). A BUILD
check reads `public/` and source only: no server, no network, no ssh.
**DEPLOY and SCHEDULED checks are not here** — see INVENTORY.md for where they
live. Python 3 stdlib only.

## Usage

```bash
python3 ops/checks/run_checks.py --site ~/code/denvercoloradoinsulation.com \
    --manifest <manifest.json> [--only a,b] [--json /tmp/report.json] [--public-dir public]
```

| Flag | Effect |
|---|---|
| `--site` | site repo root (required) |
| `--manifest` | manifest JSON (required) |
| `--only a,b` | run only these modules; each must be enabled in the manifest. The others are reported `SKIPPED (--only)` |
| `--json PATH` | also write a JSON report. **Refused (exit 2) if PATH is inside `--site`** |
| `--public-dir` | built output dir relative to `--site`; overrides manifest `public_dir` (default `public`) |
| `--modules-dir DIR` | **testing only**: load modules from DIR instead of `ops/checks/modules/` |
| `--fixtures-dir DIR` | **testing only**: canary fixtures from DIR (default `<modules-dir>/../fixtures`) |

Order of a run:

1. Load the manifest. A module name not present in `modules/` is a config error.
2. For every selected module: import it, verify every `REQUIRES` key not in
   `OPTIONAL_KEYS` is in the manifest and every path exists; unknown data keys
   or options are errors too. Any failure stops the run, naming module, key and
   path.
3. Run **every** selected module's canary before any real check. Missing
   fixture = `NO CANARY`; zero findings = `BLIND INSTRUMENT`; an exception =
   `CANARY ERROR`. If any canary fails, no real check runs.
4. Run the real checks.
5. Report: one status line per module in `modules/` — `PASS`, `FAIL (n
   findings)`, `ERROR`, `CANARY FAIL`, `SKIPPED (--only)` or `NOT ENABLED`
   (modules absent from the manifest are listed and counted, never silent);
   then findings one per line as `page | module | quote [message]`; then a
   `SUMMARY` line with counts and the exit code.

## Exit codes

Constants in `checklib.py` (`EXIT_*`). Precedence when several apply: **2 > 3 > 1**.

| Code | Constant | Meaning |
|---|---|---|
| 0 | `EXIT_CLEAN` | every canary fired, every real check ran, no findings |
| 1 | `EXIT_FINDINGS` | at least one real check returned findings |
| 2 | `EXIT_CONFIG` | config/usage error: bad manifest, unknown module, missing data key or path, unknown option, `--json` inside the site, a module source containing forbidden text, or a real check that **crashed** (it judged nothing, so it can never read as a pass) |
| 3 | `EXIT_CANARY` | canary failure: `NO CANARY`, `BLIND INSTRUMENT`, or a canary that raised |

## Manifest format

One manifest per site (row 3 of K44 owns where they live).

```json
{
  "site": "DCI",
  "public_dir": "public",
  "modules": {
    "claim_gate": {
      "data":    {"config": "canon:ops/claim_gate/config/dci.json"},
      "options": {}
    }
  }
}
```

A module is enabled by being listed under `modules`. Path values in `data` are
resolved as: `canon:<path>` → relative to the canon repo root; absolute → as
is; anything else → relative to the site root. A value may be a list of such
paths. Keys the module lists in `LITERAL_KEYS` are passed through unchanged
(strings, numbers, lists) and get no existence check.

**K50 (2026-10-12), optional keys:** a module may declare `OPTIONAL_KEYS`
(set, a subset of `REQUIRES`; a key outside `REQUIRES` is a CONFIG ERROR). An
optional key absent from the manifest reaches the module as `None`; a
required key absent from the manifest stays a CONFIG ERROR (exit 2).
`superlative_scan` declares `patterns` optional (absent = the canon default
list).

## Module contract (how to add a module)

Copy [`MODULE_TEMPLATE.md`](MODULE_TEMPLATE.md). In short:

- `ops/checks/modules/<name>.py` exposes `NAME` (= file stem), `DESCRIPTION`,
  `REQUIRES` (dict data key → one-line description), optional `LITERAL_KEYS`
  (set), optional `OPTIONS` (dict of defaults), and `def check(ctx) -> list[Finding]`.
- `ctx` is a `checklib.Context`: `site_root`, `public_dir`, `data` (resolved),
  `options` (defaults overlaid with manifest), `site_name`, `module`, and
  helpers `iter_html()`, `read_text(path)`, `visible_text(html)`,
  `resolve(value)`, `rel(path)`, `finding(page, message, quote)`.
- `checklib.Finding(module, page, message, quote)`: `page` relative to the
  public dir (or site root); `quote` at most one sentence, collapsed and
  truncated to 200 chars.
- Canary: `ops/checks/fixtures/<name>/canary/` is a mini site root (its own
  `public/` etc.) with `manifest.json` = `{"data": {...}, "options": {...}}`
  (optional `"public_dir"`), data paths relative to the fixture. It must make
  `check()` return **≥ 1** finding. Plant the defect the module exists to catch;
  a canary that passes because of an unrelated config artefact is not a control.
- Module files starting with `_` are ignored by discovery.

## Safety guarantees

- **No writes inside `--site`** (or inside the fixtures dir): a Python audit
  hook refuses write-mode opens and remove/rename/mkdir/chmod/copy-destination
  events under those roots, for the runner and every module in-process.
  `--json` inside the site is refused up front. `sys.dont_write_bytecode` is
  set, so no `__pycache__` is left anywhere.
- **No network in-process**: `socket.socket` and `socket.create_connection`
  are replaced with functions that raise, and the `socket.connect` audit event
  raises. Spawning `ssh`, `scp`, `sftp`, `rsync`, `curl`, `wget` or `nc` is
  refused. Subprocesses that a module runs (for example `claim_gate.py`) are
  not covered by in-process hooks; such modules must be reviewed.
- **Refuse to run** (exit 2) if the source of ANY file in `modules/` contains
  `ssh ` or `paramiko`, enabled or not.

## The claim_gate adapter

`modules/claim_gate.py` runs canon `ops/claim_gate/claim_gate.py --config
<data.config> --repo <site> --brief` by subprocess with
`PYTHONDONTWRITEBYTECODE=1`. claim_gate.py writes nothing except an explicit
`--report` path, and the adapter never passes one. Exit 1 becomes one finding
per blocking rule whose SUMMARY row is `FAIL` (page `public/`; for the per-hit
enumeration run, from the canon root, `python3 ops/claim_gate/claim_gate.py
--config <config> --repo <site>`). Exit 2 means the gate could not judge and
surfaces as a module `ERROR` (run exit 2).

**K47 (2026-10-12), claim_gate:** the finding message names the direct command
above for the hits instead of the site wrapper.

Its canary (`fixtures/claim_gate/canary/`) is claim_gate's own
`R1_fabricated_quotation.html` fixture as `public/index.html`, run against a
`config.json` that extends canon `dci.json` with `min_artifacts`/`expected_html`
of 1 and `R6.label_chains` emptied (so DCI's calculator-chain registration does
not fire on a one-page fixture). It yields R1 and R7 FAIL rows; the same config
on a clean one-page twin yields 0 findings (BLIND INSTRUMENT), so the control is
the planted page, not the config. Because claim_gate requires `git ls-files
public/` to agree with the tree, the canary sets option `git_snapshot: true`:
the fixture is copied to a temp dir, `git init` + one local commit, and the gate
runs on the copy.

**Known gap — report-only claim gate rules are not surfaced.** The adapter
turns only BLOCKING claim gate failures into findings. R3 (uncited figure /
adjudication) and R11 are report-only: R11 is `blocking=False`
(`ops/claim_gate/claim_gate.py:7649`) and R3 was demoted by measurement
(68.1% false positives, `ops/claim_gate/config/common.json:1154`). So the
suite does NOT fail on an unsourced rebate dollar figure planted in DCI body
copy: K44's reader planted "Xcel pays a $1,200 rebate for attic insulation."
in `public/air-sealing.html`, R3's adjudication count rose 23 -> 24, the gate
still returned PASS, and the suite exited 0. Closing this is a claim gate rule
change (out of scope for K44, which may not change the gate's rules); it is
recorded in `PROOF_2026-10.md` as adoption input. **K45 (2026-10-11) closed it
for enforced sites:** R3 is now split, and R3a (a rebate amount in the same
sentence as a rebate trigger or program name, e.g. that planted sentence) is
BLOCKING once the site's `ops/r3a_allowlist.json` exists, so its FAIL row
reaches this adapter and the suite exits 1. Without that file R3a reports
`NOT ENFORCED` and the gap above still holds; R3b (the rest of R3) stays
report-only.

**K53d (2026-10-18), claim_gate R3a JSON-LD:** on the JSON-LD surface R3a reads string values as before but not numeric or boolean values, except a numeric `price`/`minPrice`/`maxPrice`/`lowPrice`/`highPrice`/`amount`/`value` with a `priceCurrency` or `currency` sibling, read as a currency figure (sub `LD$`). Body text and other surfaces are unchanged; numeric JSON-LD T2 hits stay in R3b raw. Verify: `cd ops/checks && python3 -m unittest test_k53d`

## Divergence: strictest choice

| check | DCI | LGM | GCI | chosen | why |
|---|---|---|---|---|---|
| artifact_grep | absent | guards DCI + GCI: name/domain/phone, -denver/-greeley href slugs, 5,280/mile-high + Greeley elevations, both town lists, Atmos, unverified Xcel IQ/Combo/Power Ahead; Weld County INFO only; public/*.html + sitemap + robots, grep -oiE | guards DCI only: name/domain/phone, -denver slug, 5,280/mile-high, DCI towns (no Highland/Golden), Xcel incl. WHE, bare 'denver' except DRCOG allowlist | every site guards BOTH siblings with the same four sibling rules (identity, href slug, elevation, towns; widest town list); LGM keeps Atmos + Xcel rules and adds GCI's bare 'denver' rule (no allowlist); GCI keeps its Xcel + DRCOG-allowlisted 'denver' rules and adds the LGM sibling rules; DCI wired against LGM + GCI; recursive scan; all strings in manifest option `rules` | strictest = superset of both sites' rules applied everywhere; Weld County INFO never failed in source so not ported. Calibration: 0 findings on DCI, LGM, GCI scratch copies (both site scripts also PASS today) |
| citation_floor | >=2 `cited-stat` on every top-level page except 404/about/contact/privacy; plus >=3 on index.html + 17 service pages (hardcoded SERVICE_PAGES_AND_HOMEPAGE, insulation-removal.html exempt per ground-truth) | >=2 sitewide floor only (same exemptions) | >=2 sitewide floor only (same exemptions) | DCI's two-tier floor on all three sites; service set read from each site's own `_shared_components.py:SERVICE_PAGES` (ast.literal_eval) + `index.html`, DCI keeps `service_floor_exempt: [insulation-removal.html]` as an option | strictest (superset of findings); derived DCI set == DCI's hardcoded 18 (verified). New findings: LGM 5 (index + 4 service pages at 2), GCI 3 (3 service pages at 2); DCI 0 |
| claim_gate R3a (K45) | `R3.r3a_allowlist_path` / `R3.r3a_programs_path` = `ops/r3a_allowlist.json` / `ops/r3a_programs.json` (`dci.json`) | same keys and paths (`lgm.json`) | same keys and paths (`gci.json`) | one rule, read through this module's claim_gate adapter (summary regex `R\d+\w*` matches `R3a`): BLOCKS when the site's allowlist file exists (even `{"entries": []}`) -- an unallowlisted hit is a FAIL row, the gate exits 1, the suite exits 1 (`EXIT_FINDINGS`, never `EXIT_CANARY`); when the file is absent it reports every hit with `R3A NOT ENFORCED: no allowlist at <path> (<n> hits)`, verdict NOT ENFORCED (never PASS), exit unaffected; an allowlist entry missing `reason`/`ruling` is a config error (gate exit 2) | the allowlist is the per-site adoption switch, so enforcement is identical everywhere once each site's adoption box creates its file; R3b (R3's other hits) stays report-only on all three |
| embed_callout | sc.CALCULATOR_PAGES; heading count ==1 AND `CALLOUT_RE` (div style > strong heading > `a.btn` "Get the embed code") ==1; href must start `/` and exist in public/ | 6 hardcoded pages (superset of its sc.CALCULATOR_PAGES 4); exactly 1 `border:2px solid var(--primary)` div whose element span contains the button with a fixed href; no existence check | sc.CALCULATOR_PAGES, expects 4; html.parser: exactly 1 bordered div containing `a.btn` with text "Get the embed code"; every href (query/fragment stripped) must exist in public/ | union: all three matchers on every page; page list from data (LGM: its 6-page list); href pinned via option `button_href` where the site has one href (LGM, GCI), resolution always checked; `expected_page_count` option (GCI 4) | the matchers are not comparable (each accepts markup another rejects), so a page must pass all three; DCI keeps per-page hrefs (no pin) because its generator emits different embed_href per calculator |
| internal_links | check_internal: href="/x.html" and bare "/" must resolve in top-level public/*.html; plus public_dir injection + --canary self-test | same judging logic; no injection, no canary | same as LGM (no injection, no canary) | identical judging logic (all three); canary supplied by runner fixture (DCI's plant: dead link + good pages) | divergence is test scaffolding only, not judging; the fixture canary gives all three DCI's self-test, so the union is the strictest |
| keyboard_reachability | HTMLParser walk: scroll classes from comment-stripped `<style>` (every class in selector), reachable if wrapper has any tabindex/contenteditable or a focusable descendant tag; plus SELECT-NO-NAME | regex: first class of each `<style>` rule with overflow auto/scroll, depth-counted element span, reachable only if wrapper tabindex is non-negative or a focusable-tag regex matches inside (hidden inputs excluded); no select check | absent | union: a page/class flagged by either detector is a finding, plus DCI's SELECT-NO-NAME | strictness not comparable (DCI sees more selector classes and names selects; LGM rejects tabindex="-1" and hidden inputs as escapes), so the union flags a superset of both; 0 findings on DCI, LGM and GCI scratch copies |
| placeholders | base TOKEN over raw HTML (script/style included); CALL_SHAPE + CITE_BRACKET over markup only | base TOKEN + `[[A-Z…:…]]` + `(?<!\$){call(...)}` all over markup only | base TOKEN + `[[TOKEN(:KEY)?]]` + `{id(.id)?(...)}` all over markup only | base TOKEN over raw HTML (DCI); union of all three sites' bracket and call regexes over markup only | raw scope is a strict superset of markup-only; the bracket/call regexes are not comparable, so all are applied (union); 0 findings on all three scratch copies |
| retired_strings | 4 surfaces, entity-decoded + whitespace-collapsed: visible text (script/style stripped, tags->space and ->nothing), title/meta content, JSON-LD (JS-unescaped raw block + string values), whole decoded source (+JS-unescaped); entries collapsed; llms.txt collapsed raw | raw undecoded bytes with newlines collapsed only; entries uncollapsed (rstrip only), comment = '#' at column 0 | 3 haystacks entity-decoded + collapsed (decoded source with scripts kept, tags->nothing, tags->space) + JSON-LD string values (regex allows attrs); applied to llms.txt too | union of all surfaces; each entry tested raw and collapsed; LGM comment rule; recursive public/ scan | Surfaces are not nested (LGM raw catches undecoded entities DCI/GCI miss; DCI JS-unescape catches what LGM/GCI miss), so strictness is not comparable: union. Calibration: 0 findings on all three scratch copies. GCI check_k15_lock (b)/(c) are not this module. |
| superlative_scan | `ops/superlative_scan.py public --retired`, run by build (regen_all.sh:244): adjudicated `RETIRED_PATTERNS` (one regex, 13 alternations) over 8 surfaces via HTMLParser (skips noscript/svg text; META = every named meta; TW from name or property); top-level public/*.html + llms.txt | absent | `ops/superlative_scan.py` (not wired into build): broad `PATTERNS` net (10 regexes incl. `best`, `most`, any `-est` word) over 8 surfaces via regexes (body keeps noscript/svg/title text; META = name="description*" only); exits 1 on any raw hit; its "exclusions" are a human inclusion test, not code | each site's own pattern set read from its own file (`patterns` + `patterns_var`, ast, no import); BOTH extractors run on every page and hits unioned per (page, surface, match) taking the larger count; whitespace-collapsed haystacks; recursive public/ | extractors are not comparable (each sees text the other drops), so union. Pattern sets are site facts, so each site keeps its own: DCI 0 findings (= its build gate); GCI 721 findings, identical to its own script's RAW_HITS=721 (410 body, 287 JSON-LD, 9 llms, 5 meta, 5 og, 5 twitter; 522 of them `most`) -- GCI's net was never a gate and fails today. Enabling it for GCI turns an unwired net into a build failure: Director decision (or GCI adopts an adjudicated retired list). LGM has no data (hint null); for information DCI's list on LGM = 0, GCI's net on LGM = 386 |
| title_meta_length | 60/155 cap, html.unescape length; missing title/meta silent; meta regex `<meta\s+name="description"\s+content="(.*?)"`; no exemption | 60/155 cap, html.unescape length; missing title/meta fails; meta regex `<meta name="description" content="(.*?)">`; no exemption | 60/155 cap, length after reversing only &quot; &gt; &lt; &amp;; missing title/meta fails; LGM meta regex; exempts 404.html | missing tag fails; length = max(html.unescape, GCI partial-reverse); meta present if either regex matches, longest capture judged; no 404 exemption (option exempt_basenames, default empty); recursive scan | strictest on each axis: GCI's partial reverse never counts shorter than html.unescape so max() is the superset; either-regex match plus longest capture flags a superset; exemptions only remove findings. Calibration: 0 findings on all three sites with no exemption |
| credential_proximity | narrow exemption, raw page | narrow exemption, raw page | script/style stripped, wider exemption window and regex | NOT BUILT — BLOCKED | guard hook H14 refuses every write to a path containing "credential"; the sites keep their own check until a kickoff names the module path |
| postbuild_canary | `--canary` covers DCI's check set | `--canary` covers LGM's check set | `--canary` covers GCI's check set | REPLACED — not a module | every module now carries its own planted canary, run before any real check (S3); a per-site canary list that drifts with the site is no longer needed |
| superlative_controls | `--controls` with DCI plant strings | absent | `--self-test` with GCI plant strings | REPLACED — not a module | superseded by `fixtures/superlative_scan/canary/` (body + meta plants), run before every real check |

Also not modules, for the same reason: `links_canary`, `similarity_canary`, `page_date_normaliser_selftest` (no divergence; each is replaced by its module's fixture canary).

**K47 (2026-10-12), superlative_scan:** the scan always runs the shared default
list `ops/checks/superlative_default.py` (`RETIRED_PATTERNS`, byte-copied from
DCI). A site `patterns` file is ADDED to it (union, deduplicated), never a
replacement; an empty patterns list does not disable the scan. `"patterns":
null` or `""` means default only, and the key may be omitted (K50).

**K47 (2026-10-12), cross_property_similarity:** a relative `peer_public` that
stays inside the site's own checkout resolves within that checkout; one that
leaves it (e.g. `../denvercoloradoinsulation.com/public`) resolves against the
site's MAIN checkout root (parent of `git rev-parse --path-format=absolute
--git-common-dir`), so the suite runs from a site worktree and the module
canary reads its own worktree's fixture; an absolute path is used as given. A
missing peer is a CONFIG ERROR (exit 2).

**K53d (2026-10-18), rvalue_targets_lock:** option `rows_from_market` (default `false` = unchanged). When true, a row whose source market fact (ceiling→attic; floor→floor, crawl-vented; crawl1→crawl-encap) is absent or `None` in the facts dict generated from the property's market pack is NOT APPLICABLE (counted, never PASS or FAIL); every run with the option on prints `rvalue_targets_lock: rows_from_market checked=<n> not_applicable=<k> [<names>|none]`. Supplied rows are checked as before; canary unchanged. Verify: `cd ops/checks && python3 -m unittest test_k53d`

**K53d (2026-10-18), embed_callout:** heading and button text are compared after `html.unescape` on both sides (`Quotes &amp; Costs` matches `Quotes & Costs`); this widens matching by entity decoding only. Verify: `cd ops/checks && python3 -m unittest test_k53d`

## Facts registry modules (K50, 2026-10-12)

Six modules read a property's facts registry. Each one is **NOT ENABLED**
unless a site manifest names it, and is never auto-added: no generator or
"enable all" helper may add a `facts_*` module; enabling one is always an
explicit manifest entry.

- `facts_schema`: the registry is not a valid registry, one finding per
  validator error (registry validity, the substrate the other five read).
- `facts_review_due`: a record past its `next_review` date (K02).
- `facts_quote_snapshot`: a quote absent from its stored snapshot, a
  fingerprint that does not match the quote, or a missing snapshot (K03,
  script half).
- `facts_citation_registry`: a `cited-stat` link whose URL is no record's
  `source.url`, or whose record was retrieved 93+ days ago (K04).
- `facts_pages_coverage`: a claim missing where listed or rendered where
  unlisted; a quote or paraphrase rendered against its `quote.mode` (K08,
  K19).
- `facts_caveat_distance`: a claim rendered without its hedge within
  `max_words`, or a listed page missing the safety caveat (K22).

**Registry.** `facts/registry.json` in the site repo: a JSON array of
records, validated by `ops/facts/schema.json` via
`python3 ops/facts/validate_facts.py <registry.json>` (exit 0 valid / 1
invalid / 2 unreadable). Stored source text lives at
`facts/snapshots/<key>.txt`. An unreadable registry makes any `facts_*`
module raise (run exit 2); the other five skip malformed fields silently and
leave them to `facts_schema`.

**K53d (2026-10-18), facts region:** optional record field `region` = `{"state": <two-letter uppercase code, ^[A-Z]{2}\Z>}`; `validate_facts` checks shape only. The enforcing consumer is the site-engine build (K53c A8), and `facts_pages_coverage` only if a later box teaches it region; optional and validated does not mean enforced. `territory` is unchanged. Verify: `cd ops/checks && python3 -m unittest test_k53d`

**K53d (2026-10-18), market pack crawl_wall_r:** `ops/genesis/market_pack.schema.json` adds optional `code_facts.crawl_wall_r`, backed by `code_facts.facts_keys` like the other code facts. Verify: `cd ops/checks && python3 -m unittest test_k53d`

**Enabling.** One manifest entry per module. Five take only the registry:

```json
"facts_review_due": {
  "data": {"facts_registry": "facts/registry.json"},
  "options": {}
}
```

`facts_quote_snapshot` also takes the snapshots directory:

```json
"facts_quote_snapshot": {
  "data": {"facts_registry": "facts/registry.json",
           "facts_snapshots": "facts/snapshots"},
  "options": {}
}
```

`facts_review_due` and `facts_citation_registry` accept `options.today`
(`"YYYY-MM-DD"`), for tests only; the default (`null`) is the UTC date at
run time.

**Fingerprint and quote rules.** `retrieved.fingerprint` = sha256 of the
normalized `quote.text`. The normalizer is retired_strings' decoded-surface
pipeline `_collapse(_unjs(html.unescape(t)))`, exposed as
`validate_facts.normalize` (imported, not copied). `quote.text` is always
the source's own words. Mode `quote`: the page renders it inside quotation
marks equal to `quote.text`. Mode `paraphrase`: the page must not render
`quote.text` inside quotation marks.

facts_citation_registry and facts_review_due fail the build when a property misses its quarterly re-verification (day 93 / next_review), by design.

**Fixture and tests.** `ops/checks/fixtures/facts/` (a clean property plus
one variant per module); each module also keeps its own canary under
`fixtures/<module>/canary/`. Run:

```bash
cd ops/checks && PYTHONDONTWRITEBYTECODE=1 python3 -m unittest test_facts -v
```
