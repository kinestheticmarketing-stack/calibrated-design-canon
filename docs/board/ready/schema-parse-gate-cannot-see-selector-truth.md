---
id: schema-parse-gate-cannot-see-selector-truth
owner: architect
type: defect
created: 2026-08-20
priority: 15
---
# A JSON-LD parse gate cannot tell whether the schema is TRUE of the page

`check_jsonld` confirms every structured-data block is well-formed JSON. It
structurally cannot know whether the block's claims match the document.

**Live instance, LGM, unfixed** (remediation is a separate ruling):

| page | `quick-facts` in speakable JSON-LD | actual `.quick-facts` markup |
|---|---|---|
| `public/index.html` | 1 | **0** |
| `public/resources.html` | 1 | **0** |

The property ships `SpeakableSpecification.cssSelector` naming an element that
does not exist. The JSON parses perfectly, so the gate is green.

DCI shipped the identical defect, found it only by running Google's Schema.org
validator by hand, fixed it, and added `check_speakable` (C6) so that class
fails the build. **DCI now has six postbuild validators; LGM and GCI have
five.** The hardening did not propagate.

GCI is clean by luck of authoring, not by gate: selector 1 / markup 1.

## The general rule this is an instance of

Validate schema as **true of the page**, not merely parseable. Any assertion a
schema block makes about the document — a selector, an image URL, a price, a
`dateModified` — is checkable against the document, and a gate that only parses
will pass all of them while they are false.

## Proposed fix — NOT applied here
Port DCI's `check_speakable` to LGM and GCI, then generalize: for each schema
assertion that names something in the DOM, assert the referent exists. Canary
per B10 — plant a selector matching nothing and confirm the build reds.

## Verification command
```bash
cd /Users/vongimbel/code/longmontcoloradoinsulation.com
python3 - <<'PY'
import re
for p in ('public/index.html','public/resources.html'):
    t=open(p,errors='ignore').read()
    sel=sum(1 for b in re.findall(r'application/ld\+json[^>]*>(.*?)</script>',t,re.S) if 'quick-facts' in b)
    body=re.sub(r'<(script|style)\b.*?</\1>','',t,flags=re.S|re.I)
    print(p,'selector',sel,'markup',len(re.findall(r'class="[^"]*quick-facts',body)))
PY
# expect: selector 1, markup 0 on both — the defect
grep -c "def check_" ../denvercoloradoinsulation.com/_postbuild_check.py   # 6
grep -c "def check_" _postbuild_check.py                                   # 5
```
