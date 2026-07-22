# SEO/GEO Methodology

*A methodology section under [Calibrated Vibe Coding](../../CVC.md).*
*Universal, vertical-agnostic, audit-checklist-compatible.*

This section contains the canon-level methodology for SEO (Search Engine Optimization) and GEO (Generative Engine Optimization for AI search engines: ChatGPT, Claude, Perplexity, Google AI Overviews) applied across all Calibrated Stack projects.

## Status

**Build phase:** Phase 1 — source-organized extraction.

The methodology is being built incrementally from primary sources (paid courses, practitioner research, canonical documentation). Source-organized extraction comes first; tactic-organized synthesis comes after.

## Structure

### Synthesis docs (canon-level, top-of-section)
- `SEO_GEO_PLAYBOOK.md` — the canonical playbook (in development)
- `SEO_GEO_AUDIT_DIMENSIONS.md` — running index of audit dimensions
- `SEO_GEO_TOOLS_AND_TECHNIQUES.md` — implementation toolkit
- `SEO_GEO_PRINCIPLES.md` — operational discipline
- `SEO_GEO_SOURCES.md` — source tier tracking
- `SEO_GEO_GRAY_HAT_REFERENCE.md` — gray-hat tactics, documented honestly
- `SEO_GEO_TACTICS_STATUS_TRACKER.md` — living document, durability of each tactic

### Source extractions (reference layer)
- `sources/[course-name]/` — one subdirectory per course
- Each course has `EXTRACTION_LOG.md` indexing what's been extracted
- Each lesson gets its own file with structured extraction

### Implementation assets (per-module, running/executable)
- `link-building/SUPER_100.md` — the Module 2 (Link Building) dream-list: a reusable 13-category template, seeded per property. First instance populated for Kinesthetic Marketing.
- `keyword-research/KEYWORD_TOOL_EXTRACTION_PLAN.md` — the Module 2+3 tool-gated work banked into one executable checklist, split by free (Ahrefs Webmaster Tools) vs. paid-blitz (Ahrefs Starter / SE Ranking / Semrush) tooling tiers.

## Three-layer architecture

This section runs three layers, deliberately kept separate:

1. **`sources/` — per-author raw extraction.** One folder per course/author (`sources/{author-slug-course-slug}/`). Each source has its own update cycle, its own credibility trail, and its own tactic-ID prefix. Sources are **never merged across authors** — when a claim goes stale or turns out wrong, attribution has to survive so the right course can be re-checked. This layer is gitignored and local-only (paid course material); it never gets committed, never goes public, never ships free.
2. **`SEO_GEO_PLAYBOOK.md` — the distilled do-this layer.** Sources merge into practice here. This is where cross-author agreement gets consolidated into a single directive, disagreement gets surfaced honestly, and each directive carries an evidence tier traceable back to its source tactic ID.
3. **The eventual SKILL — execution layer.** Built FROM the playbook, never directly from raw sources. The playbook is the only layer a skill is allowed to read from; this keeps the skill's directives auditable back through one hop instead of N raw courses.

Read direction only flows sources → playbook → skill. Nothing downstream edits an upstream layer.

## Intake procedure (new course)

1. Course files (PDFs, video transcripts, docs) land in `~/Downloads` temporarily. This is a **staging area only** — nothing there is the permanent record.
2. Claude Code extracts each lesson into `sources/{author-slug-course-slug}/{module-dir}/lesson-NN-{slug}.md`, following the extraction schema below.
3. The extracted `.md` file is the permanent record, not the source PDF/transcript. Once extracted, the Downloads copy can be discarded — the repo copy is authoritative.
4. Each module folder closes with a `_MODULE_ROLLUP.md`; each source root carries one `EXTRACTION_LOG.md` indexing every module, every lesson, every tactic-ID range, and any known gaps.
5. `sources/` stays gitignored throughout — verify with `git check-ignore` before and after any placement pass.

## Extraction schema

This is the convention the existing folders (Glen Allsopp's SEO Blueprint 3, Vahe Arabian's Publisher SEO course) already implement — documented here, not invented:

- **Per-module folders.** One directory per course module (e.g. `on-site-blueprint/`, `technical-seo/`), matching the course's own module structure.
- **Per-lesson files.** One `.md` file per lesson, named `lesson-NN-{slug}.md`, each following a fixed section order:
  `SOURCE · TYPE · LENGTH · CORE CONCEPT · TACTICS · FRAMEWORKS · SPECIFIC NUMBERS / THRESHOLDS · TEMPLATES / SCRIPTS / PROMPTS · EXAMPLES / CASE STUDIES · CONTRARIAN CLAIMS · QUOTES WORTH KEEPING · EVIDENCE TIER · CURRENCY · RISK · POTENTIALLY OUTDATED · OPEN QUESTIONS RAISED · FOR THE PLAYBOOK TRACKER`
  (17 headings; three of the headings contain `/` as part of the heading text, not as a separator between headings.) Non-lesson reference material (glossaries, tool records) uses a lighter TOOL/REFERENCE variant of the same schema.
- **`_MODULE_ROLLUP.md` per module.** Written at module close: index of the module's lessons, tactic-ID range, and a synthesis/closeout note. `grep -c '^## '` on a rollup should return 5.
- **`EXTRACTION_LOG.md` at source root.** One per source. Tracks a course-overview table (module, dir, tactic-ID prefix, status) plus one detailed table per module (lesson, IDs, file, status). Append-only — closed modules are never rewritten, only added to.

## Tactic-ID convention

Every source gets a unique prefix so an audit verdict stays traceable to its author forever — a `GAP` or `ALIGNED` call always resolves back to one course, one lesson, one tactic. IDs within a prefix are minted append-only (never renumbered, even across mint-order-vs-lesson-order mismatches) and must stay contiguous with zero duplicates within that prefix.

**Prefixes in use** (check this list before minting a new one — a collision breaks traceability):

| Prefix | Source | Meaning | Range in use |
|--------|--------|---------|--------------|
| TLB | Glen Allsopp — SEO Blueprint 3 | Link Building Blueprint | TLB-01..38 |
| TKR | Glen Allsopp — SEO Blueprint 3 | Keyword Research Blueprint | TKR-01..29 |
| TSC | Glen Allsopp — SEO Blueprint 3 | Super Content Blueprint | TSC-01..22 |
| TLO | Glen Allsopp — SEO Blueprint 3 | Local SEO Blueprint | TLO-01..73 |
| TEB | Glen Allsopp — SEO Blueprint 3 | Experts Blueprint | TEB-01..14 |
| TSP | Glen Allsopp — SEO Blueprint 3 | Superpixels | TSP-01..36 |
| TPB | Glen Allsopp — SEO Blueprint 3 | SEO Blueprint 3 Playbook | TPB-01..09 (partial source — see Known gaps) |
| PIN | Vahe Arabian — Publisher SEO | Introduction | PIN-01..03 |
| PTE | Vahe Arabian — Publisher SEO | Technical SEO | PTE-01..77 |
| PCO | Vahe Arabian — Publisher SEO | Content SEO | PCO-01..52 |
| PTA | Vahe Arabian — Publisher SEO | Tactics | PTA-01..30 |
| PPI | Vahe Arabian — Publisher SEO | Practical Implementation | PPI-01..22 |
| PRA | Vahe Arabian — Publisher SEO | Reporting & Analytics | PRA-01..26 |
| PCD | Vahe Arabian — Publisher SEO | Content Distribution | PCD-01..30 |

Glen's On-Site Blueprint (58 lessons) and Audits Blueprint (13 audits) mint no tactic IDs of their own — On-Site content is folded into the tactic prefixes above via cross-reference, and Audits synthesizes existing tactics rather than minting new ones. seo-jesus-one-page-websites-2025 has no prefix minted yet (see Known gaps — extraction not present on disk).

Next available prefix for a new source: pick two letters not in the table above, unique to that author. Do not reuse a prefix across sources even if a course is later found to be the "same" material re-packaged.

## Audit usage

How a site audit consumes this layer (the consolidated one-kickoff method proven this cycle):

1. One kickoff, all modules of a source (or all sources relevant to the audit's scope) in a single pass.
2. Read every module's `_MODULE_ROLLUP.md` first for the synthesis view, then the individual lesson files for tactic-level detail.
3. Every tactic gets a verdict: **ALIGNED** / **GAP** / **N/A** / **CANNOT-VERIFY** — never left unverdicted.
4. Consolidate into one report per audit, not one report per source — a merged do-next queue across all sources in scope, with Auditor-gated items (GRAY/FORBIDDEN risk tactics requiring sign-off before use) flagged explicitly.
5. Verdicts cite the tactic ID (e.g. "GAP — TLO-53, local SEO audit checklist not run") so the finding traces back to its source lesson without re-deriving it.

## Refresh cadence

- **Sources get re-extracted when the course itself updates** (new lessons, revised modules). The source's `EXTRACTION_LOG.md` gets a new entry; existing tactic IDs are never renumbered, new ones append.
- **The playbook re-distills deltas**, not the whole source, when a source updates — only the changed tactics need re-synthesis.
- **The skill inherits** from the playbook on its own release cycle, not on every source update.
- SEO/GEO is not static — engine algorithm changes, deprecated rich-result types, and platform sunsets (see the M7/PCD currency correction on FAQ/How-to rich results, `sources/vahe-arabian-publisher-seo/EXTRACTION_LOG.md`) mean a **periodic refresh pass is expected**, not a one-time extraction. Treat every source as due for a currency check on a regular cadence, not just when the underlying course itself is revised.

## Known gaps

- **Glen Allsopp — SEO Blueprint 3 Playbook module (TPB).** Only the intro video and "State of SEO 2024" report page were supplied (TPB-01..09). Eight further Playbook report pages were never provided: Two Goliath Secrets, Goliath List Building, Goliaths Plan Their Year, Content Creation Mindset, Utilise Trending Bars, Focus on Link Velocity, Screenshot the SERPs, Analyse Footer Links. This is a documented partial-source gap, not a stalled extraction — re-open the Playbook module and resume minting from **TPB-10** if/when those pages are obtained. Full detail: `sources/glen-allsopp-seo-blueprint-3/EXTRACTION_LOG.md`.
- **seo-jesus-one-page-websites-2025.** Module folders exist (`intro/`, `01-finding-emds/`, `02-launching-sites/`, `03-niche-selection/`, `04-link-building/`) but contain zero files — no lesson `.md` files, no `_MODULE_ROLLUP.md`, no `EXTRACTION_LOG.md`, no tactic-ID prefix minted. `SEO_GEO_SOURCES.md` previously stated "13 lessons already extracted," which does not match the current working tree on any branch (confirmed via `git log --all` — the path has no history anywhere, and `sources/` is correctly gitignored so this isn't a git-visibility issue). Either the extraction was done in an environment whose files never made it into this repo checkout, or it was never actually run. **Not audit-ready.** Needs Director decision: re-run the extraction from the original course material, or confirm the "13 lessons" claim was aspirational and update tracking accordingly.

## Build philosophy

Three commitments shape this section:

1. **Honest about uncertainty.** When sources disagree, the disagreement is surfaced. The playbook takes a position, explains the reasoning, and points to alternatives. Operators decide for their context.

2. **Conservative by default, aggressive paths documented.** Where tactics carry real risk, the playbook leans conservative but documents the higher-leverage alternative honestly. Risk is named concretely. Operators make their own choice with full information.

3. **Real evidence, no fabrication.** No fake reviews. No fake AggregateRating. No fake testimonials. No fake schema entities. No invented quotes. The substance discipline of the Calibrated Stack applies absolutely.

## Phase 2 (future)

After source-organized extraction is substantially complete, the section will be restructured into tactic-organized canon. Each tactic gets its own file with cross-references to every source that taught it. The `sources/` directory becomes archival reference; the tactic tree becomes primary navigation.

See `SEO_GEO_PRINCIPLES.md` for the operational rules. See `SEO_GEO_PLAYBOOK.md` for the canon directives.
