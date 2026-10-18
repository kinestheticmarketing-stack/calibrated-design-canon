# Module template

Copy these three files, replace `my_check` everywhere, and make the canary
plant the exact defect your module exists to catch.

## 1. `ops/checks/modules/my_check.py`

```python
"""my_check -- one line on what it catches. Source: <site file:function per site>."""

import re

from checklib import Finding  # ctx.finding(...) builds one for you

NAME = "my_check"                      # must equal the file stem
DESCRIPTION = "One line: what defect this catches."
REQUIRES = {                           # manifest data keys; {} if none
    "retired": "path to the retired-strings list (relative to site root)",
    "threshold": "literal: integer cap",
}
LITERAL_KEYS = {"threshold"}           # REQUIRES keys that are values, not paths
# OPTIONAL_KEYS = {"threshold"}        # optional: REQUIRES keys a manifest may omit
OPTIONS = {"include_llms_txt": True}   # defaults; manifest options override


def check(ctx):
    findings = []
    words = [w.strip() for w in ctx.read_text(ctx.data["retired"]).splitlines()
             if w.strip() and not w.startswith("#")]
    for page in ctx.iter_html():                  # sorted public/**/*.html
        text = ctx.visible_text(ctx.read_text(page))
        for w in words:
            m = re.search(r"[^.]*" + re.escape(w) + r"[^.]*\.?", text)
            if m:
                findings.append(ctx.finding(page, "retired string %r" % w,
                                            m.group(0)))
    return findings
```

Rules: no network, no writes, no `ssh `/`paramiko` text anywhere in the file
(even in comments: the runner refuses to run). Return `[]` when clean. Raise
only when the module cannot judge; a crash in a real run exits 2.
`OPTIONAL_KEYS` must be a subset of `REQUIRES` (else a config error); an
optional key the manifest omits reaches `check()` as `ctx.data[key] is None`,
so handle `None`; when present it is resolved like any other key (path, or
literal if in `LITERAL_KEYS`). Unknown data keys and options stay config errors.

## 2. `ops/checks/fixtures/my_check/canary/` (a mini site root)

```
fixtures/my_check/canary/
  manifest.json
  retired.txt                 # data the fixture needs, paths relative to here
  public/index.html           # contains the planted defect
```

`public/index.html`:

```html
<!DOCTYPE html><html lang="en"><head><title>Canary</title></head>
<body><p>We are the best insulation contractor in Denver.</p></body></html>
```

`retired.txt`:

```
best insulation contractor
```

## 3. `ops/checks/fixtures/my_check/canary/manifest.json`

```json
{
  "data": {"retired": "retired.txt", "threshold": 3},
  "options": {}
}
```

Optional `"public_dir"` (default `"public"`). The canary passes when `check()`
returns at least one finding. Prove it is a real control: remove the planted
defect and confirm the runner reports `BLIND INSTRUMENT` (exit 3).

## 4. Site manifest entry

```json
"my_check": {"data": {"retired": "ops/retired_strings.txt", "threshold": 3}, "options": {}}
```

Run just your module:

```bash
python3 ops/checks/run_checks.py --site ~/code/denvercoloradoinsulation.com \
    --manifest <manifest.json> --only my_check
```
