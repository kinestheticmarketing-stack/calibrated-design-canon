# Check inventory — Kickoff 44, row S1

Date 2026-10-11. Read-only inventory. Site HEADs: DCI `b508cbd`, LGM `c94faeb`, GCI `4063594`.
Paths are relative to each site repo unless they start with `canon:`. Nothing was executed; every row
comes from reading the source.

Classes: **BUILD** = runs on `public/` and source, with no server and no network. **DEPLOY** = needs the
server or a live URL. **SCHEDULED** = a monitor or timer.

## Counts

| Site | BUILD, run by build | BUILD, no build runs it | DEPLOY (no build runs) | SCHEDULED (hosted here) |
|---|---|---|---|---|
| DCI | 26 | 12 | 5 | 2 |
| LGM | 28 | 4 | 5 | 0 |
| GCI | 20 | 10 | 5 | 0 |
| canon (portfolio) | 0 | 2 | 0 | 10 |

How the BUILD-run figure breaks down: DCI = preflight 1 + `_validators` 1 + generator-inline 5 + raster
guard 1 + postbuild 14 + links 1 + duplication 1 + claim gate 1 + superlative 1. LGM = 1+1+10+1+12+1+1+1.
GCI = 1+1+4+1+9 + svc-import 1 + 1+1+1.

## 1. regen_all.sh wiring (what a build runs, in order)

| Step | DCI | LGM | GCI |
|---|---|---|---|
| PYGUARD `ast.parse` of every `_*.py` | regen_all.sh:36-49 | :36-49 | :36-49 (all three identical) |
| Brand raster plus `magick` guard | :120-121 (`_rasterize_brand_assets.sh:25-29`) | :200-206 inline guard, then :207/:210 | :72/:76 |
| `_postbuild_check.py` | :129 | :218 | :132 |
| `_svc_pending_import_check.py` | — | — | :144 |
| `_check_links.py` (internal only) | :144 | :233 | :159 |
| `_intra_similarity_check.py` | :147 | :236 | :162 |
| `ops/claim_gate.sh --brief` | :223 | :252 | :178 |
| `ops/superlative_scan.py public --retired` | :244 | — | — (the script exists but is not wired) |

## 2. Generator-inline guards (BUILD, run inside generators; they stay in the generators)

| Guard | DCI | LGM | GCI |
|---|---|---|---|
| `validate_html_fragment`: balanced-fragment HTML parser that raises `HtmlValidationError` | `_validators.py:99` | same file (only the docstring differs) | same |
| `_assert_no_placeholders`: no raw `__TOKEN__` in legal pages | `_generate_legal_pages.py:51` | :92 | :104 |
| `validate_citation_set`: no duplicate citation KEY or LABEL | `_shared_components.py:3670` | :4914 | absent |
| Embed snippet invariants (anchor is a sibling of the iframe, height, URL) | `_generate_calculator_pages.py:3208` | `_embed_common.py:490` | `_generate_calculator_pages.py:1791` |
| Embed frame invariants (one script, no `src`, inputs) | — | `_embed_common.py:375`, `:578` names-its-tool, `:227` param cap | `_generate_calculator_pages.py:2402` |
| Calculator field and default bounds | `_generate_calculator_pages.py:862` `_assert_fields` | `:103` `_assert_spliced`, `:113` `_assert_core_shared` | — |
| Embed-code page publication invariants | — | `_generate_embed_code_page.py:409` | — |
| og-image text-fit (no clipped strapline) | `_generate_brand_assets.py:155-225` | `:197-359` | `:236` `assert_fits` |
| `_out_guard.resolves_into_public` | — | `_out_guard.py` (inert since 2026-09-21; not counted) | — |
| `_sc_note_guard` | — | — | `_generate_calculator_pages.py:308` (no-op; not counted) |

## 3. `_postbuild_check.py` (BUILD, run by build). `main()` calls DCI 14, LGM 12, GCI 9

DCI main :1113-1129, LGM main :803-817, GCI main :822-832.

| Check | DCI | LGM | GCI | Site data read |
|---|---|---|---|---|
| C1 interactive JS present and `node --check` parses it | :52 | :50 | :49 | filename regex `calculator\|checker\|comparator`; needs `node` |
| C2 placeholder tokens | :163 | :140 | :168 | none (regex constants) |
| C3 duplicate visible citation label | :177 | :150 | :178 | none |
| C4 licence wording near abatement, asbestos or mold | :196 | :169 | :217 | CRED/TOPIC regex, window 25 |
| C5 JSON-LD parses | :231 | :204 | :267 | none |
| C6 speakable `cssSelector` resolves on its page | :555 | :466 | :451 | none |
| C7 citation floor (`cited-stat` count ≥2) | :628 | :515 | :500 | `CITATION_EXEMPT` (4 pages); DCI also `SERVICE_PAGES_AND_HOMEPAGE` (18) ≥3, minus `insulation-removal.html` |
| C8 title ≤60 / meta ≤155 | :690 | :554 | :571 | GCI `LENGTH_EXEMPT={404.html}` |
| C9 scroll region is keyboard-reachable | :824 `check_keyboard_reachability` (also checks `<select>` names) | :652 `check_scrollable_regions` | — | each page's own `<style>` |
| Embed callout, exactly one per calculator page | :876 L1 | :751 `check_embed_callout` | :756 K15(c) | DCI `sc.CALCULATOR_PAGES` + `CALLOUT_HEADING`; LGM 6 hardcoded pages + button href; GCI `sc.CALCULATOR_PAGES` (expects 4) + `CALLOUT_STYLE` |
| Embed frame file exists per calculator slug | :876 L2 | — | — | `sc.CALCULATOR_SLUG_TO_URL` |
| Payback page rate-fed result wiring | :876 L3 | — | — | `sc.CITED_SOURCES['ENERGYSTAR_SEAL_INSULATE_15PCT']`, `energy-savings-payback-calculator.html` |
| L4 health/safety pages carry no `disqualifier` block | :923 | — | — | `sc.HEALTH_SAFETY_PAGES` |
| L5 code-citation lock | :964 | — | — | `L5_SITEWIDE`, `L5_MOVED_PAGES` (7 town pages), `L5_DENVER_PHRASE`, `llms.txt` |
| L6 R-value calculator TARGETS equal CODE_FACTS | :1018 | — | — | `sc.CODE_FACTS['denver']`, `L6_FILES` (page + embed) |
| Retired strings stay retired | :1092 L7 | :711 `check_retired_strings` | :756 K15(a) | `ops/retired_strings.txt` (DCI 465 lines, LGM 97, GCI 91) + `llms.txt` |
| Greeley thank-you clause absent from town pages | — | — | :756 K15(b) | `sc.TOWN_PAGE_FILENAMES` (expects 8), `sc._THANK_YOU_RVALUE_GREELEY` |
| Page dates agree with git | — | :767 `check_page_dates` (runs `_derive_page_dates.py --check`, :168) | — | `sc.PAGE_MODIFIED_ISO`, git history, canon `claim_gate.GitFacts` |
| `--canary` self-proof (not run by build) | :375 (C2, C6, C7-service, C8, C9) | :342 (C2, C6, C8, C9, retired) | :377 (C2, C6, C8) | fixtures inline |

## 4. Other build-run scripts

| Check | DCI | LGM | GCI | Data |
|---|---|---|---|---|
| `_check_links.py` internal `.html` hrefs resolve in `public/` | :42 `check_internal` | :43 | same as LGM (byte-identical except the docstring) | `public/` |
| `_intra_similarity_check.py`: 5-word-shingle Jaccard ≥0.30 between pages in one property fails | identical in all three | | | `THRESHOLD` 0.30, `EXCLUDE` (4 pages), `STRIP_PATTERNS`, boilerplate cutoff 0.25 |
| `ops/claim_gate.sh` → `canon:ops/claim_gate/claim_gate.py` (rules R1-R11; R3 = R3a blocking (once the site's ops/r3a_allowlist.json exists) / R3b report-only) | config `dci.json` | `lgm.json` | `gci.json` | canon configs; wrappers differ only in config name |
| `ops/superlative_scan.py --retired`: retired superlatives across 8 surfaces | :58 `RETIRED_PATTERNS`, :269 main | absent | different implementation, not run (see §5) | `RETIRED_PATTERNS`, `public/llms.txt` |
| `_svc_pending_import_check.py`: every `_svc_pending_*.py` imports | — | — | :31 | glob `_svc_pending_*.py` (9 files) |

## 5. Checks no build runs

BUILD-class:
- `_postbuild_check.py --canary` (DCI, LGM, GCI)
- `_check_links.py --canary` (DCI only, :75)
- `ops/similarity_canary.sh`, which plants a duplicate and requires the gate to fire (DCI, LGM, GCI; identical)
- `ops/claim_gate.sh --canary` (all three; canon `claim_gate.py:7731`)
- `ops/superlative_scan.py public --controls` (DCI :214) and `--list`
- `ops/superlative_scan.py` plus `--self-test` (GCI :230/:295; broad pattern, exits 1 on any hit)
- `_artifact_grep.sh`, which finds sibling-property names, domains, phones, slugs and towns in `public/` (LGM, checking DCI+GCI; GCI, checking DCI with a DRCOG allowlist)
- `_similarity_check.py`: cross-property Jaccard against `../denvercoloradoinsulation.com/public` (GCI only)
- `_derive_page_dates.py --selftest`: the date normaliser's self-test (DCI :323)
- `ops/embed_contract_check.js`: four embed behaviour contracts in local headless Chrome against `public/` (DCI; uses `ops/cdp.js`)
- Embed sizing instruments, which measure but give no pass/fail verdict: `ops/embed_measure.py`, `ops/embed_state_sweep.js`, `ops/embed_cdp_measure.js` (DCI); `ops/embed_height_measure.mjs`, `ops/embed_state_sweep.mjs` (GCI)
- `ops/hooks/commit-msg`: Verify:/Result: trailer re-run. It exists in DCI only, and only DCI sets `core.hooksPath=ops/hooks`. It runs on commit, not on build.
- `smoke_tests/boot_mocked.js`: backend boot with SendGrid mocked (DCI, GCI)
- canon `ops/test_stale_site_check.js`, `ops/test_send_alert.js` (harnesses)

DEPLOY-class. All must run at the deploy hop:
- `ops/functional_proof.sh <domain> <repo>`: live sitemap, robots, every page 200, calculator JS parses (all three; they diverge)
- `ops/live_token_check.sh <host>`: placeholder tokens in served bytes, read from the live sitemap (all three)
- `_check_links.py --check-outbound`: HEAD/GET of external links (all three; network)
- `ops/push-to-staging.sh` preflight: domain allowlist, repo/domain match, minimum HTML count (all three identical)
- `ops/push-backend.sh`: per-file md5 compare and post-deploy md5 verify (all three identical)

SCHEDULED-class. They run where noted:
- `ops/canary_check.js` (DCI-hosted, covers all 3): daily `lead-canary.timer` on the server
- `ops/browser_canary.js` (DCI-hosted): weekly headless lead-path on the server
- canon `scripts/monitoring/uptime_check.sh`: launchd `r2uptime`, every 600 s on the Mac
- canon `scripts/monitoring/daily_checks.sh` (launchd `r2daily`, 07:00) bundles `deploy_drift_check.sh`, `tls_expiry_check.sh`, `page200_check.sh` (wraps each site's `live_token_check.sh`), `ops_drift_check.sh` (a rules-drift check was also bundled until REALM KICKOFF 4b removed it)
- canon `scripts/staleness_watcher.py check`: launchd `citation-staleness-watcher`, Mondays 09:00, via `~/.config/monitoring/staleness_watcher_run.sh`
- canon `ops/stale_site_check.js`, `ops/unhandled_lead_check.js`, `ops/backup_heartbeat_check.sh`: timers on the server
- Not a check, not counted: `ops/retention_cleanup.js` (DCI-hosted daily deletion job)

## 6. Divergence (checks present in 2+ sites that behave differently)

| Check | DCI | LGM | GCI |
|---|---|---|---|
| C2 placeholders | `TOKEN` scans raw HTML; `CALL_SHAPE`/`CITE_BRACKET` scan markup only; `[[` key allows mixed case | every pattern on markup only (script/style stripped); `[[` requires an uppercase key; call shape has `(?<!\$)` | markup only; `[[KEY]]` with optional `:key`; call shape allows at most one dot |
| C4 credentials | scans raw text including JSON-LD; exemption window ±4/5 tokens | same as DCI | strips script/style first; exemption over the full 25-token window; wider `EXEMPT_CRED` (nor/not/n't) |
| C7 citation floor | ≥2 sitewide plus ≥3 on 18 service pages and the homepage | ≥2 only | ≥2 only |
| C8 title/meta | full `html.unescape`; a missing tag is not a failure; meta regex `\s+` | full unescape; a missing tag FAILS; label `TITLE-META` | partial unescape (`_display_len`); a missing tag FAILS; 404 exempt |
| C9 keyboard | DOM parser, CSS comments stripped, also `select-name` | regex/element-span, scroll only | absent |
| Embed callout | heading text + `CALLOUT_RE`; href must exist | 6 hardcoded pages; exact button href | HTMLParser on the border style + button text; href must exist; expects 4 pages |
| Retired strings | 4 surfaces (visible ×2, head, JSON-LD raw+values, decoded source + un-JS) | raw bytes, newlines collapsed only, no entity decode | 3 decoded haystacks + JSON-LD string values |
| `--canary` coverage | C2, C6, C7-service, C8, C9 | C2, C6, C8, C9, retired | C2, C6, C8 |
| `_check_links.py` | `public_dir` injection + `--canary` | no canary | no canary |
| `superlative_scan.py` | adjudicated `RETIRED_PATTERNS`, 8 surfaces, `--retired` gate, wired | absent | broad `PATTERNS` with inclusion exclusions; exits 1 on any hit; not wired |
| `functional_proof.sh` | baseline (412 lines) | adds LOCAL_MODE sitemap-host rewrite (452) | robots Sitemap resolved via `urljoin`/robotparser (419) |
| `live_token_check.sh` | widened (REPLACE_WITH, YOUR_*_HERE, CHANGE_ME) | not widened (hash identical to GCI) | not widened |
| `_artifact_grep.sh` | absent | guards against DCI + GCI (10 checks) | guards against DCI only, DRCOG allowlist |
| `claim_gate.sh` | `dci.json` | `lgm.json` | `gci.json` (config only; same engine) |

## Seen, not touched

- The LGM and GCI `regen_all.sh` claim-gate comments (LGM :243-244, GCI :169-170) still say "DCI is deliberately NOT wired"; that is stale (DCI :223 wires it).
- The `_check_links.py` docstrings say it "does NOT run inside regen_all.sh" in DCI :7-9 and GCI :7-9; that is stale, since both builds run it.
- `live_token_check.sh` in LGM and GCI lacks the 2026-08-20 widening DCI carries, and `page200_check.sh` runs it on schedule.
- LGM `_artifact_grep.sh` header cites a `_similarity_check.py` that LGM does not have.
- GCI `ops/superlative_scan.py` exists and no build or monitor runs it.
- `ops/hooks/commit-msg` exists and is installed only on DCI.
