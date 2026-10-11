# ops/checks/tests

Stdlib `unittest` tests for `run_checks.py`. Each runner test builds a temp
site, temp test modules and their canary fixtures (removed on cleanup), and
invokes the runner by subprocess with `--modules-dir`/`--fixtures-dir`. No
network, no real site. `test_10` is structural: every file in
`ops/checks/modules/` must have `fixtures/<name>/canary/manifest.json`.

```bash
cd ops/checks && PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v
```
