# SEO/GEO Tactic Register — Phase 1 counts

Date: 2026-09-03

The register is the gitignored file `METHODS/seo-geo/sources/_register/REGISTER.tsv` — one row per minted tactic across the nine placed sources (8 tab-separated fields: tactic_id, prefix, source_slug, module_dir, lesson_file, statement, gate, applicability).

**Total tactics: 975** (matches the sum of the "Prefixes in use" ranges in README.md).

## Per source

| source_slug | prefixes | count |
|---|---|---|
| charles-floate-parasite-seo | PAR | 54 |
| glen-allsopp-seo-blueprint-3 | TLB, TKR, TSC, TLO, TEB, TSP, TPB | 221 |
| imwarriortools-steal-ai-overview-rankings | AIO | 80 |
| jesper-nissen-parasite-seo-2025 | JNP | 86 |
| julian-goldie-link-building-mastery | GLB | 101 |
| local-seo-revolution-gbp-next-gen | LSR | 33 |
| luther-landro-local-seo-checklist | LLS | 110 |
| olga-zarr-seo-audit-mastery | OZA | 50 |
| vahe-arabian-publisher-seo | PIN, PTE, PCO, PTA, PPI, PRA, PCD | 240 |
| **Total** | 21 prefixes | **975** |

## Per prefix

| prefix | range | count |
|---|---|---|
| TLB | 01..38 | 38 |
| TKR | 01..29 | 29 |
| TSC | 01..22 | 22 |
| TLO | 01..73 | 73 |
| TEB | 01..14 | 14 |
| TSP | 01..36 | 36 |
| TPB | 01..09 | 9 |
| PIN | 01..03 | 3 |
| PTE | 01..77 | 77 |
| PCO | 01..52 | 52 |
| PTA | 01..30 | 30 |
| PPI | 01..22 | 22 |
| PRA | 01..26 | 26 |
| PCD | 01..30 | 30 |
| PAR | 01..54 | 54 |
| OZA | 01..50 | 50 |
| LLS | 01..110 | 110 |
| GLB | 01..101 | 101 |
| JNP | 01..86 | 86 |
| LSR | 01..33 | 33 |
| AIO | 01..80 | 80 |

All 21 prefixes are contiguous from 01 with zero duplicate IDs; the prefix set equals the README table exactly.

## Gate

| gate | count |
|---|---|
| ADMIT | 834 |
| BLOCKED | 138 |
| FORBIDDEN | 3 |

## Applicability

| applicability | count |
|---|---|
| INTERNAL | 707 |
| EXTERNAL | 208 |
| NOT-APPLICABLE | 60 |

**INTERNAL slice (Phase 2 clustering input): 707 tactics.**

## Line-calls

Count: 75 (all in the statement column).

IDs: PAR-02 PAR-25 PAR-36 PAR-37 PAR-45 PAR-50 TLB-29 TLB-30 TLB-31 TLO-01 TLO-02 TLO-32 TLO-67 TPB-09 AIO-50 AIO-63 JNP-19 JNP-37 JNP-76 JNP-78 JNP-85 JNP-86 GLB-11 GLB-12 GLB-13 GLB-30 GLB-31 GLB-71 GLB-72 GLB-73 GLB-83 GLB-84 GLB-89 LSR-12 LSR-25 LSR-28 LSR-31 LLS-65 LLS-93 LLS-95 LLS-105 OZA-24 OZA-26 OZA-28 OZA-38 PCD-13 PCD-24 PCO-12 PCO-19 PCO-21 PCO-27 PCO-50 PCO-51 PIN-02 PPI-19 PPI-22 PRA-04 PRA-16 PRA-17 PRA-18 PRA-19 PRA-20 PTA-09 PTA-10 PTA-20 PTA-21 PTA-22 PTA-23 PTA-24 PTA-25 PTE-04 PTE-05 PTE-35 PTE-46 PTE-76

## Verification

Run from `METHODS/seo-geo/sources/_register/` (the register is gitignored; these reproduce every count above):

```
R=REGISTER.tsv
echo $(( $(wc -l < $R) - 1 ))                                   # 975 data rows
tail -n +2 $R | cut -f1 | sort | uniq -d                        # empty = no duplicate IDs
tail -n +2 $R | cut -f1 | awk -F- '{c[$1]++; if($2+0>m[$1])m[$1]=$2+0} END{for(p in c)print p, m[p], c[p]}' | sort   # per-prefix max == count
tail -n +2 $R | cut -f3 | sort | uniq -c                        # per-source
tail -n +2 $R | cut -f2 | sort | uniq -c                        # per-prefix
tail -n +2 $R | cut -f7 | sort | uniq -c                        # gate: 834 / 138 / 3
tail -n +2 $R | cut -f8 | sort | uniq -c                        # applicability: 707 / 208 / 60
tail -n +2 $R | awk -F'\t' '$8=="INTERNAL"' | wc -l             # 707 INTERNAL slice
grep -c '\[line-call\]' $R                                      # 75
grep '\[line-call\]' $R | cut -f1 | tr '\n' ' '                 # line-call IDs
awk -F'\t' 'NF!=8' $R                                           # empty = every line has 8 fields
```

Per-row provenance check (975/975 pass): for every row, `sources/<source_slug>/<module_dir>/<lesson_file>` exists and contains the tactic_id as `### <ID>` or `**<ID>`.

Independent spot-read of 12 rows selected with `awk 'BEGIN{srand(20260903)}{print rand()"\t"$0}' | sort -n | head -12` (10 distinct prefixes): **12 FAITHFUL, 0 NOT-FAITHFUL** — every sampled statement is a compression of its lesson section with no added claim, correction, or improvement.
