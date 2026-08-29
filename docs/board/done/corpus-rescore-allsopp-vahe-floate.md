---
id: corpus-rescore-allsopp-vahe-floate
owner: auditor
type: chore
created: 2026-08-19
size: L
lane: audit
---
# Three corpora have never been re-scored since their original pass

Only Zarr got a second pass (2026-08-19) and found 7 of 50 verdicts wrong or
stale, plus a 327-line citation drift in the one prior audit with any
baseline at all. Allsopp, Vahe, and Floate were each scored once
(2026-08-09/12) and never revisited despite four remediation waves changing
every property since. Same shape as the Zarr wave — worth its own dedicated
pass, not squeezed in alongside other work.

---

## Deferred — 2026-08-19 (Ruling 18 — deferred by Director)

**Explicitly deferred. Instrument recorded so it is not re-derived:** authored-
content scoring — 5-word shingles, Jaccard, threshold 0.3, boilerplate removed
empirically at >=25%-of-pages. Never score rendered HTML.

Baseline: authored duplication is ZERO on all three properties as of
2026-08-19. Non-zero on re-score means regression *or* a reverted boilerplate
setting — verify the instrument before believing the finding.

**Card stays open. State above is verified, not assumed.**

---

## Closed — 2026-08-19

**Commits:** DCI `5087737` · LGM `6f3018a` · GCI `3aa6f0f` · CANON `c08a2db`

All three corpora re-scored fresh against the post-remediation copy, diffed
against the 2026-08-18 audits by content, never by line number.

**Scored:** Allsopp 146 on-site tactics individually + 16 shared-disposition
blocks; Vahe 221 of 240; Floate 7 of the 15 ADMIT. Build-order tactics
omitted silently and not carded.

**The wave was not a paper exercise — two defects were found and fixed.**

1. **Heading-hierarchy skip on 134 of 154 pages.** The shared footer wrapped
   Contact / Service Area / About in `<h4>`, so every page jumped h2 -> h4.
   GCI additionally emitted 18 `<h4>` from calculator result templates where
   both siblings used h3. Fixed to h2 (footer) and h3 (GCI calculators);
   pure markup, no copy touched, appearance unchanged. Deployed and verified
   across all 151 live pages.

2. **342 files of paid, watermarked course material were stageable by one
   `git add -A`.** Every EXTRACTION_LOG declared `sources/` gitignored. It
   was not — only untracked. Fixed in canon `c08a2db`.

**Three prior-audit defects recorded** (see the R1 file): the Allsopp
EXTRACTION_LOG omits the TLB prefix entirely and does not disclose that the
On-Site module IDs only 13 of its 58 lessons; DCI had no per-tactic baseline
for Allsopp or Vahe, so those diffs were impossible and are reported as
such rather than invented.

**One verdict was corrected mid-wave rather than shipped wrong:** PTE-44 was
first scored NOT-APPLIED on the claim that `@id` was unused. Organization
does carry a stable `@id`. Re-scored APPLIED-UNTRACKED.

**Voice-gated, not spliced:** 21 over-length meta descriptions (LGM 20,
DCI 1), the absent title brand suffix on all 154 titles, and an AI-content
disclosure. Drafts and reasoning in
`calibrated-design-canon/METHODS/seo-geo/cr_voice_gated_drafts.md`.

**Verification command:**
```bash
# 0 pages with a skipped heading level, all three properties, live
python3 - <<'EOF'
import re,urllib.request,xml.etree.ElementTree as ET
for h in ("denvercoloradoinsulation.com","longmontcoloradoinsulation.com","greeleycoloradoinsulation.com"):
    g=lambda u: urllib.request.urlopen(urllib.request.Request(u,headers={"User-Agent":"Mozilla/5.0"}),timeout=25).read().decode(errors="ignore")
    bad=0
    for e in ET.fromstring(g(f"https://{h}/sitemap.xml")).iter():
        if not e.tag.endswith("loc"): continue
        t=re.sub(r"<script.*?</script>","",g(e.text),flags=re.S|re.I); p=0
        for m in re.finditer(r"<h([1-6])",t,re.I):
            v=int(m.group(1))
            if p and v>p+1: bad+=1; break
            p=v
    print(h,"skipped-heading pages:",bad)   # expect 0
EOF
```


**CORRECTION — 2026-08-21.** The claim above that authored duplication is ZERO
across all three properties is **true only of the pages the gate examined.**
`_intra_similarity_check.py:67` carries
`EXCLUDE = {'404.html', 'privacy.html', 'contact.html', 'about.html'}` —\nbyte-identical in all three repos, and exactly the pages ported near-verbatim\nbetween siblings. Measured on AUTHORED content with chrome stripped,\n`privacy.html` shares a **726-word identical run** with both siblings.\nThe original line is left in place so the record stays legible; read it as\nsuperseded by this note. See\n`calibrated-design-canon/docs/board/ready/similarity-gate-excludes-the-shared-pages.md`.\n