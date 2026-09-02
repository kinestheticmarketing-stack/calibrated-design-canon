# FINAL REPORT

This pass was asked to replace Rule 9 in `calibrated-design-canon` entirely — not merge, not append — because the version that landed earlier today (commit `0965057`) said what a Final Report must contain but nothing about how it opens, who it is written for, or what it must not contain, and the first report delivered under it complied on paper while still failing: no headline, and a closing item that assessed the report's own rule-compliance instead of reporting a decision made during the work. The pass deleted the old Rule 9 from every file that carried it, inserted the new text verbatim in its place, updated the auditor scoring docs and the orchestrator cross-references to match the new lettering, swept the rest of the repository for any other weak or partial restatement of the reporting rule, and verified all of it independently against the pushed `main` branch rather than trusting each stage's own self-report. The outcome: the new Rule 9 is live at `METHODS/ARCHITECT_DISCIPLINE.md` and `METHODS/HANDOFF_TEMPLATE.md`, byte-identical between them and confirmed byte-identical against the raw GitHub copy twice, independently, by two different verification passes; the old Rule 9 text survives in exactly one place in the whole repository, a historical retrospective that has itself now been marked superseded; Rules 1 through 8 are unmodified; every cross-reference resolves; and the three live client sites and their three repos are untouched.

a. The OLD Rule 9 text, verbatim, as deleted from `METHODS/ARCHITECT_DISCIPLINE.md` and `METHODS/HANDOFF_TEMPLATE.md` (both files carried an identical copy):

```
RULE 9 — THE FINAL REPORT IS THE COMPLETE RECORD.

9a. EVERY ARTIFACT APPEARS IN THE REPORT, VERBATIM AND IN FULL.
    Page copy, replacement strings, config, findings documents,
    proposed schema. If the Director would need to scroll up,
    open a file, or run another command to read it, the report
    is DEFECTIVE.
9b. NEVER A POINTER. "See above," "reproduced in R2's report,"
    "in the committed file," "omitted here for length" — each
    is a defect. Length is not a reason. The report is long
    because the work was.
9c. THE REPORT STARTS AT ITEM (a). No preamble, no status line,
    no narrative lead-in about which row finished last. The
    lettered items ARE the report.
9d. ONE REPORT, AT THE END. Findings scattered across subagent
    output do not survive the session. The orchestrator's final
    report carries everything, in its own words, in full.
9e. ANYTHING THAT MUST SURVIVE THE SESSION IS ALSO WRITTEN TO A
    FILE AND COMMITTED. Report and file, both, never one or the
    other. A draft that exists only in a report dies when the
    session is cleared — that has already happened once and
    cost a full re-drafting pass.
9f. THE ARCHITECT WRITES REPORT ITEMS WITH NO ESCAPE HATCH. An
    item phrased "X verbatim, OR Y" invites a pointer. An item
    phrased "if applicable" invites omission. Name the artifact
    and require it in full. A kickoff that gives the Executor a
    way to satisfy the letter with a reference is the
    Architect's defect, not the Executor's.
9g. A NULL RESULT IS AN ARTIFACT. When a pass recommends
    against building something, the reasoning appears in full,
    to the same standard as a draft would. A negative finding
    reported thinly is worth less than the work that produced
    it.
```

b. The NEW Rule 9 text, verbatim, as it now reads on `main` in both `METHODS/ARCHITECT_DISCIPLINE.md` and `METHODS/HANDOFF_TEMPLATE.md`, at line 287 in each, immediately after Rule 8's closing line:

```
RULE 9 — THE FINAL REPORT. WRITTEN FOR SOMEONE WHO KNOWS
NOTHING. NEVER A POINTER. NEVER A DEFECT THE DIRECTOR HAS TO
CATCH.

9a. IT OPENS WITH A HEADLINE. The literal words FINAL REPORT on
    their own line. Everything the pass produced appears UNDER
    that headline. Nothing above it, nothing outside it.
9b. ONE REPORT, WRITTEN ONCE, AT THE END, BY THE ORCHESTRATOR,
    IN ITS OWN WORDS. Commentary earlier in the session is not
    reporting. A subagent's output is not the report. Findings
    scattered through a session die with the session.
9c. WRITTEN FOR A READER WITH NO CONTEXT. Assume they have
    never seen this project, did not read the kickoff, and
    cannot scroll up. Under the headline, before the lettered
    items, state in plain prose: what this pass was asked to
    do, what it actually did, and what the outcome was. Then
    the lettered items.
9d. EVERY ARTIFACT IN FULL, VERBATIM, INSIDE THE REPORT. Page
    copy, drafts, findings documents, quoted sources, measured
    counts, commit SHAs, file paths. If the reader would have
    to open a file, run a command, or scroll up to see it, the
    report FAILED.
9e. NEVER A POINTER. "See above," "reproduced in R2's report,"
    "in the committed file," "omitted here for length,"
    "detailed elsewhere" — each one is a DEFECT. Length is
    never a reason. The report is long because the work was.
9f. NO META-COMMENTARY. Do not describe the report. Do not
    assess how well the rules were followed. Do not narrate
    your own diligence, coordination, or dispatch difficulties
    unless they changed the work's outcome. Report the WORK,
    not the reporting.
9g. EVERY ROW'S WORK APPEARS, whether or not it produced an
    artifact. A row that found nothing states what it looked
    for and what it found. A NULL RESULT IS AN ARTIFACT and
    gets the same full treatment as a draft would.
9h. ANYTHING THAT MUST SURVIVE THE SESSION IS ALSO WRITTEN TO A
    FILE AND COMMITTED. Report and file, both, never one or the
    other. A draft that exists only in a report dies when the
    session is cleared — that has already happened and cost a
    full re-drafting pass.
9i. THE ARCHITECT WRITES REPORT ITEMS WITH NO ESCAPE HATCH. An
    item phrased "X verbatim, OR Y" invites a pointer. "If
    applicable" invites omission. "Anything else worth noting"
    invites commentary. Name the artifact, require it in full,
    and require decisions rather than reflections. A kickoff
    that lets the Executor satisfy the letter with a reference
    is the Architect's defect, not the Executor's.
```

c. Every file changed, and the change in each, quoted in full.

`METHODS/ARCHITECT_DISCIPLINE.md` — the old Rule 9 block (item a above) deleted in its entirety, the new Rule 9 block (item b above) inserted in the identical position.

`METHODS/HANDOFF_TEMPLATE.md` — same delete-and-replace as above, plus two further corrections in the same file. The "VERBATIM RULES NOTICE" preamble's rule-name list changed from:

```
sub-points 8a-8d; Rule 9 — the final report is the complete
record, including sub-points 9a-9g). They are never summarized,
```

to:

```
sub-points 8a-8d; Rule 9 — the final report, written for someone
who knows nothing, never a pointer, including sub-points 9a-9i).
They are never summarized, paraphrased, or shortened when this
template is used. A fresh
```

And the "OUTPUT FORMAT" section's `## Rules` placeholder instruction changed from:

```
[verbatim block, required in full — see RULE 9 (METHODS/ARCHITECT_DISCIPLINE.md):
the final report is the complete record, and "see METHODS/ARCHITECT_DISCIPLINE.md
opening — paste that first" is exactly the pointer 9b forbids. Copy the rules text
in, do not point at it.]
```

to:

```
[verbatim block, required in full — see RULE 9 (METHODS/ARCHITECT_DISCIPLINE.md):
the final report is written for someone who knows nothing, and "see
METHODS/ARCHITECT_DISCIPLINE.md opening — paste that first" is exactly the pointer
9e forbids. Copy the rules text in, do not point at it.]
```

`METHODS/AUDITOR_PROTOCOL.md` — the two Rule-9 FAIL conditions changed from:

```
  - Phrases a report item with an escape hatch — "X verbatim, OR
    Y," "if applicable," or any wording that lets a pointer
    satisfy the letter instead of requiring the content in full
    (Rule 9f).
  - Delivers a Final Report that references an artifact instead
    of containing it — verbatim and in full — inside the report
    itself: "see above," "reproduced in R2's report," "in the
    committed file," "omitted here for length," or any equivalent
    pointer (Rule 9a, 9b).
```

to four conditions:

```
  - Phrases a report item with an escape hatch — "X verbatim, OR
    Y," "if applicable," "anything else worth noting," or any
    other wording that lets a pointer or a reflection satisfy the
    letter instead of requiring the artifact and a decision in
    full (Rule 9i).
  - Delivers a Final Report that references an artifact instead
    of containing it — verbatim and in full — inside the report
    itself: "see above," "reproduced in R2's report," "in the
    committed file," "omitted here for length," "detailed
    elsewhere," or any equivalent pointer (Rule 9e).
  - Delivers a Final Report with no literal "FINAL REPORT"
    headline on its own line, or with any content appearing above
    it or outside it (Rule 9a).
  - Delivers a Final Report containing self-assessment or
    meta-commentary about the report itself — describing how well
    the rules were followed, or narrating dispatch or coordination
    difficulties that did not change the work's outcome — instead
    of reporting the work (Rule 9f).
```

`METHODS/AUDITOR_PRIMING_TEMPLATE.md` — the same two-to-four expansion, worded to match this file's "FAIL if..." bullet style:

```
  - FAIL if a report item is phrased with an escape hatch — "X
    verbatim, OR Y," "if applicable," "anything else worth
    noting," or any other wording that lets a pointer or a
    reflection satisfy the letter instead of requiring the
    artifact and a decision in full (Rule 9i).
  - FAIL if a Final Report references an artifact instead of
    containing it — verbatim and in full — inside the report
    itself: "see above," "reproduced in R2's report," "in the
    committed file," "omitted here for length," "detailed
    elsewhere," or any equivalent pointer (Rule 9e).
  - FAIL if a Final Report has no literal "FINAL REPORT" headline
    on its own line, or has any content appearing above it or
    outside it (Rule 9a).
  - FAIL if a Final Report contains self-assessment or
    meta-commentary about the report itself — describing how well
    the rules were followed, or narrating dispatch or coordination
    difficulties that did not change the work's outcome — instead
    of reporting the work (Rule 9f).
```

`docs/orchestrator-role.md`, line 264-266, changed from:

```
6. **What to report**: what shipped, what did not, gate exit codes. See RULE 9
   (`METHODS/ARCHITECT_DISCIPLINE.md`) — the final report is the complete
   record; do not weaken or restate this rule here. Every artifact named
```

to:

```
6. **What to report**: what shipped, what did not, gate exit codes. See RULE 9
   (`METHODS/ARCHITECT_DISCIPLINE.md`) in full; do not weaken or restate this
   rule here. Every artifact named
```

`docs/orchestrator-dispatch-template.md`, line 70-71, changed from:

```
See RULE 9 (`METHODS/ARCHITECT_DISCIPLINE.md`) — the final report is the
complete record; do not weaken or restate this rule here. Every item below
```

to:

```
See RULE 9 (`METHODS/ARCHITECT_DISCIPLINE.md`) in full; do not weaken or
restate this rule here. Every item below
```

`METHODS/the-calibrated-stack.md`, under `### Verification`, changed from:

```
- Final Report sections in every kickoff, lettered (a, b, c) for
  consistency.
```

to:

```
- Final Report: See RULE 9 (`METHODS/ARCHITECT_DISCIPLINE.md`) in
  full; do not weaken or restate this rule here.
```

`RETROSPECTIVES/2026-09-02-rule-9-landing-verification.md` — a superseded marker added at the top, stating that the file verified the first, since-replaced Rule 9, that its cited sub-point letters (9b, 9e) are now wrong against current canon, and pointing to this file for the replacement's own record. The historical body text below the marker was left unedited.

d. Every escape-hatch phrasing found in the sweep, its file and line, and its replacement, quoted in full. The sweep found exactly one hit beyond what was already fixed while replacing Rule 9 itself: `METHODS/the-calibrated-stack.md`, under `### Verification` (originally two lines, unnumbered in the source). Original text, verbatim: `- Final Report sections in every kickoff, lettered (a, b, c) for consistency.` Replacement, verbatim: `- Final Report: See RULE 9 (`METHODS/ARCHITECT_DISCIPLINE.md`) in full; do not weaken or restate this rule here.` No other file in the repository's 416 markdown files contained an escape-hatch or pointer phrasing describing report format outside of: the two files carrying Rule 9's own text (`ARCHITECT_DISCIPLINE.md`, `HANDOFF_TEMPLATE.md`), the two auditor scoring files quoting Rule 9's sub-points as FAIL conditions (`AUDITOR_PROTOCOL.md`, `AUDITOR_PRIMING_TEMPLATE.md`), the two files carrying the headline-agnostic pointer (`docs/orchestrator-role.md`, `docs/orchestrator-dispatch-template.md`), third-party course-extraction content under `METHODS/seo-geo/sources/` using "verbatim" and "reproduced" for copyright/privacy redaction of licensed material (a different subject entirely), and historical, already-completed retrospective and board-card records describing what a past pass did or omitted, not a standing rule.

e. Character-for-character verification result, per file. `METHODS/ARCHITECT_DISCIPLINE.md`: fetched from `https://raw.githubusercontent.com/kinestheticmarketing-stack/calibrated-design-canon/main/METHODS/ARCHITECT_DISCIPLINE.md`, Rule 9 block extracted and diffed against the exact replacement text — `diff` exit 0, `cmp` exit 0, zero output, run independently twice (once during the replacement pass, once during verification). `METHODS/HANDOFF_TEMPLATE.md`: same raw fetch, same result — `diff` exit 0, `cmp` exit 0, zero output, twice. `METHODS/AUDITOR_PROTOCOL.md`: fetched raw, all four cited sub-points (9i, 9e, 9a, 9f) confirmed matching the new rule's actual lettering and content. `METHODS/AUDITOR_PRIMING_TEMPLATE.md`: same, all four sub-points confirmed. `docs/orchestrator-role.md` and `docs/orchestrator-dispatch-template.md`: fetched raw, both confirmed to contain no restated old-rule wording (no "the final report is the complete record" string in either). `METHODS/the-calibrated-stack.md`: fetched raw, pointer confirmed present and correctly worded.

f. Confirmation of where the old Rule 9 text exists in the repository. A repository-wide, case-insensitive search for the string "THE FINAL REPORT IS THE COMPLETE RECORD" returns exactly one file: `RETROSPECTIVES/2026-09-02-rule-9-landing-verification.md`, where it appears twice — once in that file's opening paragraph and once inside a quoted before/after diff documenting what an earlier sweep replaced. That file is a historical record, not live canon; nothing else in the repository references, cites, or points to it as an authority, confirmed by a separate repository-wide search for references to that filename. As of this pass, that file additionally carries an explicit marker stating it describes a superseded version of the rule and directing a reader to this file and to live canon instead. A separate search for the old rule's sub-point range, the literal string "9a-9g", returns zero matches anywhere in the repository, live or historical.

g. Rules 1 through 8 in `METHODS/ARCHITECT_DISCIPLINE.md` are unmodified. Read directly, in full: Rule 1 (EFFICIENCY), sub-points 1a through 1m plus its closing test; Rule 2 (NO DEAD ANYTHING); Rule 3 (NEVER WRITE THE DIRECTOR AN scp COMMAND); Rule 4 (ANSWER HIS QUESTION FIRST); Rule 5 (NEVER SURFACE A SECRET), sub-points 5a through 5g; Rule 6 (LOOK IT UP), sub-points 6a through 6f; Rule 7 (PAPERWORK FIRES ON STATE CHANGE), sub-points 7a through 7f; Rule 8 (A PROCESS STEP DONE CORRECTLY CAN STILL LEAVE THE REAL PROBLEM STANDING), sub-points 8a through 8d including its five-step recovery procedure. Every rule reads as a complete, non-truncated unit with no broken sub-point sequence. Every commit touching this file today was checked individually for deletion lines against Rules 1-8: the Rule 8 merge commit added content only, the first Rule 9 addition added content only, the Rule 9 replacement commit's 27 deletion lines fall entirely within the old Rule 9 block and none touch Rules 1-8, and the sweep commit does not touch this file at all.

h. Commit SHAs, pushed, confirmed via `git log` against `origin/main`. In order: `9befe811a9b94a8f15c297e2d1671c5a0ecf63df` (an earlier pass's merge reconciling Rule 8 into the rule sequence, not part of this replacement pass but the state it started from) → `0965057875ba33695c5bfd9f78f92ad55ccd0920` (the first, since-replaced Rule 9 landing) → `d06614006152fff497bf2214c9ef0b4f65580289` (an earlier sweep against that first version) → `098254a56dca47db815d242f24d30675ddf45483` (the retrospective now marked superseded) → `352249b1b9a2254b8297233d6727a32e9be9339e` (the full Rule 9 replacement — old text deleted, new text inserted, in `ARCHITECT_DISCIPLINE.md`, `HANDOFF_TEMPLATE.md`, `AUDITOR_PROTOCOL.md`, `AUDITOR_PRIMING_TEMPLATE.md`, `docs/orchestrator-role.md`, `docs/orchestrator-dispatch-template.md`) → `2c2813de4d83bae0fe62116a1319b4d9b66afa50` (the sweep against the new version, `METHODS/the-calibrated-stack.md`) → `6e84274528e1dbb0e94ef8e171fc0b43e44b1c0d` (the superseded marker added to the earlier retrospective). Local `main` and `origin/main` resolve to the identical final SHA after a fresh `git fetch origin main`; `git status` reports a clean working tree.

i. Every decision made during this pass that changed what shipped, and why. The replacement was executed as a full delete-and-replace rather than a merge of old and new text, because two versions of a rule sitting in the same document is how the weaker one wins — a reader who found either version first would have a different, contradictory understanding of what the rule requires. The auditor scoring documents' FAIL conditions were expanded from two to four rather than simply renumbered, because the old rule had no headline requirement and no meta-commentary prohibition for the scoring documents to encode — renumbering alone would have silently dropped enforcement of the two most consequential parts of the new rule. The cross-reference pointers in `docs/orchestrator-role.md`, `docs/orchestrator-dispatch-template.md`, and `METHODS/the-calibrated-stack.md` were rewritten to be headline-agnostic ("See RULE 9 ... in full") rather than restating any specific wording, because the prior pointers had restated the old rule's exact headline as settled fact, which became false the moment the headline changed — a pointer that names the rule without quoting it cannot go stale the same way again. The earlier retrospective file was marked superseded rather than deleted or rewritten, because it is a genuine historical record of what a prior version of the rule said and how it was verified at the time, and Rule 9's own standard for artifacts is that they survive in full, not that inconvenient history gets erased — but it was marked, because an unmarked stale document citing wrong sub-point letters as if current is exactly the kind of defect a reader should not have to catch themselves.
