"""K50 row 10: tests for the facts registry (validate_facts.py) and the six
facts_* suite modules, driven against ops/checks/fixtures/facts/. Stdlib
unittest only; every site is a temp copy of fixtures/facts/clean (removed in
tearDown). The fixture on disk is never modified.

Dates: TODAY is fixed below. Every record's dates in the temp copy are
rewritten relative to TODAY (retrieved.date = TODAY-10, status.as_of =
TODAY-10, next_review = TODAY+80), then a variant's "dates" offsets are
applied, and the manifest pins `today` for facts_review_due and
facts_citation_registry. So these tests cannot age.

Run:  cd ops/checks && PYTHONDONTWRITEBYTECODE=1 python3 -m unittest test_facts -v
"""

import datetime
import hashlib
import html
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.dont_write_bytecode = True
os.environ["PYTHONDONTWRITEBYTECODE"] = "1"

CHECKS = Path(__file__).resolve().parent
MODULES = CHECKS / "modules"
RUNNER = CHECKS / "run_checks.py"
FIXTURE = CHECKS / "fixtures" / "facts"
CLEAN = FIXTURE / "clean"
VARIANTS = FIXTURE / "variants"
VALIDATOR = CHECKS.parent / "facts" / "validate_facts.py"
sys.path.insert(0, str(CHECKS))
import checklib as C  # noqa: E402

TODAY = datetime.date(2026, 10, 12)
FACTS_MODULES = ["facts_schema", "facts_review_due", "facts_quote_snapshot",
                 "facts_pages_coverage", "facts_citation_registry",
                 "facts_caveat_distance"]
TODAY_MODULES = ("facts_review_due", "facts_citation_registry")
ENV = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")


def load_path(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def load_module(name):
    return load_path("k50t_" + name, MODULES / (name + ".py"))


def day(offset):
    return (TODAY + datetime.timedelta(days=offset)).isoformat()


def set_dotted(rec, dotted, value):
    parts = dotted.split(".")
    d = rec
    for p in parts[:-1]:
        d = d[p]
    d[parts[-1]] = value


class FactsCase(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="k50_facts_test_")).resolve()
        self.site = self.tmp / "site"

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    # -- builders -----------------------------------------------------------
    def build(self, variant=None, dates=None):
        """Temp copy of clean/, optional overlay of variants/<variant>/, dates
        rewritten relative to TODAY, then offsets from variant.json "dates"
        and from `dates` ({key: {field.path: offset}}) applied. Returns the
        variant.json dict (or {})."""
        shutil.copytree(CLEAN, self.site)
        vj = {}
        if variant:
            vdir = VARIANTS / variant
            vj = json.loads((vdir / "variant.json").read_text(encoding="utf-8"))
            for src in sorted(vdir.rglob("*")):
                if src.is_file() and src.name != "variant.json":
                    dst = self.site / src.relative_to(vdir)
                    dst.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copyfile(src, dst)
        reg = self.site / "facts" / "registry.json"
        records = json.loads(reg.read_text(encoding="utf-8"))
        for rec in records:
            if not isinstance(rec, dict):
                continue
            if isinstance(rec.get("retrieved"), dict):
                rec["retrieved"]["date"] = day(-10)
            if isinstance(rec.get("status"), dict):
                rec["status"]["as_of"] = day(-10)
            if "next_review" in rec:
                rec["next_review"] = day(80)
        offsets = {}
        for src in (vj.get("dates") or {}, dates or {}):
            for key, fields in src.items():
                offsets.setdefault(key, {}).update(fields)
        for rec in records:
            if isinstance(rec, dict) and rec.get("key") in offsets:
                for path, off in offsets[rec["key"]].items():
                    set_dotted(rec, path, day(off))
        reg.write_text(json.dumps(records, indent=2, ensure_ascii=False) + "\n",
                       encoding="utf-8")
        self.write_manifest()
        return vj

    def write_manifest(self, modules=None):
        man = json.loads((CLEAN / "manifest.json").read_text(encoding="utf-8"))
        if modules is not None:
            man["modules"] = modules
        for n in TODAY_MODULES:
            if n in man["modules"]:
                man["modules"][n].setdefault("options", {})["today"] = TODAY.isoformat()
        (self.site / "manifest.json").write_text(json.dumps(man, indent=1),
                                                 encoding="utf-8")

    def run_runner(self, *extra):
        rep = self.tmp / "report.json"   # outside the site
        if rep.exists():
            rep.unlink()
        cmd = [sys.executable, "-B", str(RUNNER), "--site", str(self.site),
               "--manifest", str(self.site / "manifest.json"),
               "--json", str(rep)] + list(extra)
        p = subprocess.run(cmd, capture_output=True, text=True, env=ENV, timeout=120)
        report = json.loads(rep.read_text(encoding="utf-8")) if rep.exists() else None
        return p.returncode, p.stdout + p.stderr, report

    def by_module(self, report):
        counts = {}
        for f in report["findings"]:
            counts[f["module"]] = counts.get(f["module"], 0) + 1
        return counts

    def ctx(self, name):
        mod = load_module(name)
        man = json.loads((self.site / "manifest.json").read_text(encoding="utf-8"))
        entry = man["modules"][name]
        data = {k: C.resolve_path(v, self.site) for k, v in entry["data"].items()}
        opts = dict(getattr(mod, "OPTIONS", {}) or {})
        opts.update(entry.get("options") or {})
        return mod, C.Context(site_root=self.site, public_dir=self.site / "public",
                              data=data, options=opts, site_name="K50TEST",
                              module=mod.NAME)


class TestRunner(FactsCase):
    def test_clean_all_six_modules_pass(self):
        self.build()
        code, out, report = self.run_runner()
        self.assertEqual(code, 0, out)
        m = re.search(r"^SUMMARY .*\bfindings=(\d+) exit=(\d+)", out, re.M)
        self.assertIsNotNone(m, out)
        self.assertEqual((m.group(1), m.group(2)), ("0", "0"), out)
        self.assertIn("FINDINGS (0)", out)
        for n in FACTS_MODULES:
            self.assertRegex(out, r"(?m)^\s+%s\s+FIRED\s*$" % n)
            self.assertRegex(out, r"(?m)^\s+%s\s+PASS\s*$" % n)
            self.assertEqual(report["modules"][n]["status"], "PASS", out)
        self.assertEqual(report["findings"], [], out)

    def test_not_auto_enabled(self):
        self.build()
        self.write_manifest(modules={})
        code, out, report = self.run_runner()
        self.assertEqual(code, 0, out)
        m = re.search(r"^SUMMARY .*\benabled=(\d+) .*\bnot_enabled=(\d+)", out, re.M)
        self.assertIsNotNone(m, out)
        self.assertEqual(m.group(1), "0", out)
        ne = re.search(r"^NOT ENABLED: (.*)$", out, re.M)
        self.assertIsNotNone(ne, out)
        listed = [s.strip() for s in ne.group(1).split(",")]
        for n in FACTS_MODULES:
            self.assertIn(n, listed)
            self.assertRegex(out, r"(?m)^\s+%s\s+NOT ENABLED\s*$" % n)
            self.assertEqual(report["modules"][n]["status"], "NOT ENABLED")
        self.assertNotRegex(out, r"(?m)^\s+facts_\w+\s+FIRED")


class TestVariants(FactsCase):
    def check_variant(self, module):
        vj = self.build(variant=module)
        self.assertEqual(vj["module"], module)
        code, out, report = self.run_runner("--only", module)
        self.assertIsNotNone(report, out)
        got = self.by_module(report).get(module, 0)
        self.assertEqual(got, vj["expected"], out)
        self.assertEqual(len(report["findings"]), got, out)
        self.assertIn("FINDINGS (%d)" % vj["expected"], out)
        self.assertEqual(code, 1, out)
        self.assertEqual(report["modules"][module]["status"],
                         "FAIL (%d findings)" % vj["expected"], out)

    def test_variant_facts_schema(self):
        self.check_variant("facts_schema")

    def test_variant_facts_review_due(self):
        self.check_variant("facts_review_due")

    def test_variant_facts_quote_snapshot(self):
        self.check_variant("facts_quote_snapshot")

    def test_variant_facts_pages_coverage(self):
        self.check_variant("facts_pages_coverage")

    def test_variant_facts_citation_registry(self):
        self.check_variant("facts_citation_registry")

    def test_variant_facts_caveat_distance(self):
        self.check_variant("facts_caveat_distance")


class TestValidator(FactsCase):
    def cli(self, path):
        p = subprocess.run([sys.executable, "-B", str(VALIDATOR), str(path)],
                           capture_output=True, text=True, env=ENV, timeout=60)
        return p.returncode, p.stdout, p.stderr

    def test_validator_cli(self):
        code, out, err = self.cli(CLEAN / "facts" / "registry.json")
        self.assertEqual(code, 0, out + err)
        self.assertEqual(out.strip(), "", out)
        code, out, err = self.cli(VARIANTS / "facts_schema" / "facts" / "registry.json")
        self.assertEqual(code, 1, out + err)
        lines = [ln for ln in out.splitlines() if ln.strip()]
        self.assertEqual(len(lines), 3, out)
        bad = self.tmp / "notjson.json"
        bad.write_text("{not json", encoding="utf-8")
        code, out, err = self.cli(bad)
        self.assertEqual(code, 2, out + err)

    def test_fingerprint_uses_retired_strings_normalizer(self):
        vf = load_path("k50t_validate_facts", VALIDATOR)
        rs = load_module("retired_strings")
        samples = [
            "up to 20% on heating &amp; cooling costs",
            "R-49 \\u2014 attic &mdash; zone 5",
            "  spaced\t\tout \n\n text  ",
            "it\\'s &#8220;quoted\\&#8221; and \\\"escaped\\\"",
            "plain",
        ]
        for s in samples:
            with self.subTest(s=s):
                want = rs._collapse(rs._unjs(html.unescape(s)))
                self.assertEqual(vf.normalize(s), want)
                self.assertEqual(vf.fingerprint(s),
                                 hashlib.sha256(want.encode("utf-8")).hexdigest())
        self.assertEqual(vf.normalize("a\\u2014b"), "a—b")
        self.assertEqual(vf.normalize("a &amp;  b"), "a & b")


class TestBoundaries(FactsCase):
    def test_review_due_boundary(self):
        for off, want in ((0, 0), (-1, 1)):
            with self.subTest(next_review=off):
                if self.site.exists():
                    shutil.rmtree(self.site)
                self.build(dates={"spray-foam-air-leakage": {"next_review": off}})
                mod, ctx = self.ctx("facts_review_due")
                self.assertEqual(len(mod.check(ctx)), want)

    def test_citation_boundary(self):
        for off, want in ((-92, 0), (-93, 1)):
            with self.subTest(retrieved=off):
                if self.site.exists():
                    shutil.rmtree(self.site)
                self.build(dates={"nfr-gas-attic-rebate": {"retrieved.date": off}})
                mod, ctx = self.ctx("facts_citation_registry")
                self.assertEqual(len(mod.check(ctx)), want)


if __name__ == "__main__":
    unittest.main()
