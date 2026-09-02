---
id: ported-xcel-content-audit
owner: architect
type: chore
created: 2026-08-21
priority: 45
retriage: 2026-10-02
classification: ARCHITECT
---
**Classification reasoning (2026-09-02):** A technical source-diffing audit (what DCI/LGM inherited from a shared parent) with a single defensible methodology and no rendered-copy decision attached — already correctly `owner: architect`.

# R8 — if an Xcel multiplier could port onto an Atmos property, what else ported?

The porting argument justified widening S1-S3 across all three properties. It
came back **negative** and that result should be recorded rather than allowed
to expire in silence:

- **royalcomforths.com** — LGM only (1 source, 11 rendered). DCI 0, GCI 0.
- **1.5x multiplier** — LGM only (37 source, 17 rendered). DCI 0, GCI 0.
  Ground (c), wrong-utility-on-GCI, is **closed-as-false-with-evidence**.
- **$400 air-sealing rebate figure** — LGM 12 rendered, DCI 33 rendered,
  GCI **0 rendered** (one `#` comment and one unshipped module only).

So no Xcel-attributed content ported onto Atmos. The DCI/LGM overlap on the
$400 figure is shared-parent inheritance, not cross-utility porting.

**Still worth a scheduled pass:** DCI and LGM share a parent architecture, and
the $400 figure demonstrably travelled between them. The open question is not
"did Xcel content reach Atmos" — it did not — but "what else did DCI and LGM
inherit from the same unverifiable source." Out of scope for the 2026-08-21
wave.
