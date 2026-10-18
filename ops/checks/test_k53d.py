"""K53d row 8: tests for K53d rows (rvalue_targets_lock rows_from_market,
market pack code_facts.crawl_wall_r, facts registry region, claim gate R3a
JSON-LD reading, embed_callout entity decoding, Exampleton FIXTURE).
Stdlib unittest only; every fixture is built in a tempfile dir and removed on
cleanup. No fixture on disk and no site repo is touched.

Run:  cd ops/checks && PYTHONDONTWRITEBYTECODE=1 python3 -m unittest test_k53d -v
"""

import contextlib
import importlib.util
import io
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
OPS = CHECKS.parent
MODULES = CHECKS / "modules"
FIXTURES = CHECKS / "fixtures"
GENESIS = OPS / "genesis"
EXAMPLETON = GENESIS / "fixtures" / "exampleton"
CLAIM_GATE = OPS / "claim_gate"
ENV = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")

sys.path.insert(0, str(CHECKS))
import checklib as C  # noqa: E402
import run_checks as R  # noqa: E402

sys.path.insert(0, str(CLAIM_GATE))
import test_r3a as G  # noqa: E402  (helpers only; its TestCases stay under G)


def load_path(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


VG = load_path("k53dt_validate_genesis", GENESIS / "validate_genesis.py")
VF = load_path("k53dt_validate_facts", OPS / "facts" / "validate_facts.py")


class TempCase(unittest.TestCase):
    def setUp(self):
        self._td = tempfile.TemporaryDirectory(prefix="k53d_test_")
        self.T = Path(self._td.name).resolve()

    def tearDown(self):
        self._td.cleanup()


def run_module(name, mod_path, site, entry):
    """Load a module and run it exactly as run_checks does (build_context +
    run_one). Returns (findings, captured stdout)."""
    mod = R.load_module(name, mod_path)
    ctx = R.build_context(mod, entry, site, "public", "K53DTEST", canary=False)
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        findings = R.run_one(mod, ctx)
    return findings, buf.getvalue()


# ---------------------------------------------------------------- (a)

RVL = "rvalue_targets_lock"
RVL_FIX = FIXTURES / RVL
SUMMARY_RE = re.compile(r"^rvalue_targets_lock: rows_from_market checked=(\d+) "
                        r"not_applicable=(\d+) \[([^\]]*)\]$", re.M)
FACTS_NO_CRAWL = ("CODE_FACTS = {\n    'testcity': dict(code='a test code', "
                  "ceiling=60, eave=49, floor=38),\n}\n")


class TestA_RowsFromMarket(TempCase):
    def site(self, which, facts_src=None):
        self.n = getattr(self, "n", 0) + 1
        site = self.T / ("%s%d" % (which, self.n))
        shutil.copytree(RVL_FIX / which, site)
        if facts_src is not None:
            (site / "facts.py").write_text(facts_src, encoding="utf-8")
        return site

    def entry(self, site, **opts):
        e = json.loads((site / "manifest.json").read_text(encoding="utf-8"))
        e.setdefault("options", {}).update(opts)
        return e

    def run_rvl(self, site, mod_path=MODULES / (RVL + ".py"), **opts):
        return run_module(RVL, mod_path, site, self.entry(site, **opts))

    def head_module(self):
        """The module as committed at HEAD (pre-K53d), in a temp file."""
        p = subprocess.run(["git", "-C", str(CHECKS), "show",
                            "HEAD:ops/checks/modules/%s.py" % RVL],
                           capture_output=True, text=True, check=True)
        self.assertNotIn("rows_from_market", p.stdout)
        path = self.T / "head_mod" / (RVL + ".py")
        path.parent.mkdir()
        path.write_text(p.stdout, encoding="utf-8")
        return path

    def summary(self, out):
        m = SUMMARY_RE.search(out)
        self.assertIsNotNone(m, out)
        self.assertEqual(len(out.strip().splitlines()), 1, out)
        return int(m.group(1)), int(m.group(2)), m.group(3)

    def test_a1_absent_crawl1_is_not_applicable_counted_and_named(self):
        """(a) rows_from_market on, crawl1 absent: crawl-encap NOT APPLICABLE,
        counted and named in the stdout summary line; no finding for it."""
        site = self.site("clean", FACTS_NO_CRAWL)
        # Make the page's crawl-encap row wrong too: still no finding.
        calc = site / "public" / "calc.html"
        calc.write_text(calc.read_text(encoding="utf-8").replace(
            "R-15 continuous walls', targetMin:15, targetRec:15",
            "R-99 continuous walls', targetMin:99, targetRec:99"), encoding="utf-8")
        findings, out = self.run_rvl(site, rows_from_market=True)
        self.assertEqual(findings, [], [f.message for f in findings])
        self.assertEqual(self.summary(out), (3, 1, "crawl-encap"))
        # A None value is NOT APPLICABLE the same way.
        site2 = self.site("canary", FACTS_NO_CRAWL.replace(
            "floor=38)", "floor=38, crawl1=None)"))
        _f, out2 = self.run_rvl(site2, rows_from_market=True)
        self.assertEqual(self.summary(out2), (3, 1, "crawl-encap"))
        mod = R.load_module(RVL, MODULES / (RVL + ".py"))
        exp, na = mod.expected_rows({"ceiling": 60, "floor": 38}, True)
        self.assertEqual(na, ["crawl-encap"])
        self.assertEqual(list(exp), ["attic", "floor", "crawl-vented"])

    def test_a2_supplied_wrong_row_still_fails_with_option_on(self):
        """(a) rows_from_market on: the canary's wrong attic row still FAILS,
        with crawl1 supplied and with crawl1 absent."""
        for facts in (None, FACTS_NO_CRAWL):
            with self.subTest(crawl1_absent=facts is not None):
                site = self.site("canary", facts)
                findings, out = self.run_rvl(site, rows_from_market=True)
                msgs = [f.message for f in findings]
                self.assertEqual(len(findings), 1, msgs)
                self.assertIn("area 'attic'", msgs[0])
                self.assertIn("'R-49'", msgs[0])
                want = (3, 1, "crawl-encap") if facts else (4, 0, "none")
                self.assertEqual(self.summary(out), want)

    def test_a3_option_off_is_old_behaviour(self):
        """(a) rows_from_market false (default): same findings as the HEAD
        module on canary and clean, no stdout, absent crawl1 -> KeyError."""
        head = self.head_module()
        for which in ("canary", "clean"):
            with self.subTest(fixture=which):
                site = self.site(which)
                new_f, new_out = self.run_rvl(site)
                old_f, old_out = self.run_rvl(site, mod_path=head)
                self.assertEqual(new_out, "")
                self.assertEqual(old_out, "")
                key = [(f.page, f.message, f.quote) for f in new_f]
                self.assertEqual(key, [(f.page, f.message, f.quote) for f in old_f])
                self.assertEqual(len(new_f), 1 if which == "canary" else 0)
                _f, out_explicit = self.run_rvl(site, rows_from_market=False)
                self.assertEqual(out_explicit, "")
        site = self.site("clean", FACTS_NO_CRAWL)
        for path in (MODULES / (RVL + ".py"), head):
            with self.subTest(module=str(path)):
                with self.assertRaises(KeyError):
                    self.run_rvl(site, mod_path=path)


# ---------------------------------------------------------------- (b) (c) (f)

class GenesisCopy(TempCase):
    def setUp(self):
        super().setUp()
        self.root = self.T / "exampleton"
        shutil.copytree(EXAMPLETON, self.root)
        self.intake = self.root / "intake.json"
        self.mp = self.root / "market_pack.json"
        self.registry = self.root / "facts" / "registry.json"

    def load(self, p):
        return json.loads(p.read_text(encoding="utf-8"))

    def save(self, p, data):
        p.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def errors(self):
        return VG.validate(self.intake, self.mp, self.registry)

    def cli(self):
        return subprocess.run([sys.executable, str(GENESIS / "validate_genesis.py"),
                               str(self.intake), str(self.mp), str(self.registry)],
                              capture_output=True, text=True, env=ENV)


class TestB_MarketPackCrawlWall(GenesisCopy):
    def test_b1_crawl_wall_r_validates(self):
        """(b) exampleton market pack with code_facts.crawl_wall_r validates."""
        mp = self.load(self.mp)
        self.assertEqual(mp["code_facts"]["crawl_wall_r"], "R-15")
        self.assertEqual(self.errors(), [])
        self.assertEqual(self.cli().returncode, 0)

    def test_b2_unknown_code_facts_key_rejected(self):
        """(b) an unknown code_facts key ("bogus") is rejected."""
        mp = self.load(self.mp)
        mp["code_facts"]["bogus"] = "R-1"
        self.save(self.mp, mp)
        errs = self.errors()
        self.assertEqual(len(errs), 1, errs)
        self.assertIn("code_facts", errs[0])
        self.assertIn("bogus", errs[0])
        p = self.cli()
        self.assertEqual(p.returncode, 1, p.stdout + p.stderr)

    def test_b3_empty_crawl_wall_r_rejected(self):
        """(b) crawl_wall_r is nonempty like its siblings."""
        mp = self.load(self.mp)
        mp["code_facts"]["crawl_wall_r"] = ""
        self.save(self.mp, mp)
        errs = self.errors()
        self.assertEqual(len(errs), 1, errs)
        self.assertIn("crawl_wall_r", errs[0])


class TestC_FactsRegion(GenesisCopy):
    def with_region(self, region):
        recs = self.load(self.registry)
        recs[0]["region"] = region
        self.save(self.registry, recs)
        return VF.validate(self.registry)

    def test_c1_region_state_co_validates(self):
        """(c) region {"state": "CO"} on a record validates."""
        self.assertEqual(VF.validate(self.registry), [])
        self.assertEqual(self.with_region({"state": "CO"}), [])

    def test_c2_malformed_regions_rejected(self):
        """(c) malformed regions are rejected."""
        bad = [{"state": "COL"}, {"state": "co"}, {}, {"state": "CO", "x": 1},
               {"state": "C"}, {"state": "CO\n"}, {"state": 5}, "CO", None]
        for region in bad:
            with self.subTest(region=region):
                errs = self.with_region(region)
                self.assertGreaterEqual(len(errs), 1, errs)
                self.assertTrue(all("region" in e for e in errs), errs)


SENTINEL = "none named (FIXTURE)"
SAMPLEVILLE = "Sampleville (FIXTURE)"


class TestF_Exampleton(GenesisCopy):
    def test_f1_exampleton_passes_validate_genesis(self):
        """(f) the exampleton FIXTURE passes validate_genesis (exit 0)."""
        self.assertEqual(self.errors(), [])
        p = subprocess.run([sys.executable, str(GENESIS / "validate_genesis.py"),
                            str(EXAMPLETON / "intake.json"),
                            str(EXAMPLETON / "market_pack.json"),
                            str(EXAMPLETON / "facts" / "registry.json")],
                           capture_output=True, text=True, env=ENV)
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertEqual(p.stdout, "")

    def test_f2_sampleville_names_no_utility(self):
        """(f) Sampleville: both utility fields are the sentinel and name no
        company; registry territory utilities empty; absence_reason reads
        exactly "exclusivity not verified" in pack and registry evidence."""
        mp = self.load(EXAMPLETON / "market_pack.json")
        town = [t for t in mp["towns"] if t["name"] == SAMPLEVILLE]
        self.assertEqual(len(town), 1)
        town = town[0]
        self.assertEqual(town["territory_state"], "UNKNOWN")
        self.assertEqual(town["absence_reason"], "exclusivity not verified")
        companies = set()
        for t in mp["towns"]:
            if t["name"] != SAMPLEVILLE:
                companies |= {t["gas_utility"], t["electric_utility"]}
        companies |= {p["operator"] for p in mp["programs"]}
        for field in ("gas_utility", "electric_utility"):
            v = town[field]
            self.assertEqual(v, SENTINEL)
            self.assertNotRegex(v, r"(?i)\b(gas|electric|co\.|co-op|power|energy|utility)\b")
            for c in companies:
                self.assertNotIn(c, v)
        reg = self.load(EXAMPLETON / "facts" / "registry.json")
        hits = [r for r in reg if SAMPLEVILLE in (r.get("territory") or {})]
        self.assertTrue(hits)
        for r in hits:
            terr = r["territory"][SAMPLEVILLE]
            self.assertEqual(terr["gas_utility"], "")
            self.assertEqual(terr["electric_utility"], "")
            ev = r["territory_evidence"][SAMPLEVILLE]
            self.assertEqual(ev["state"], "UNKNOWN")
            self.assertEqual(ev["absence_reason"], "exclusivity not verified")


# ---------------------------------------------------------------- (d)

ARTICLE = {"@context": "https://schema.org", "@type": "Article",
           "headline": "How the federal tax credit works for attic insulation",
           "description": "What the tax credit covers when you insulate an attic.",
           "publisher": {"@type": "Organization", "name": "Example Insulation"},
           "articleBody": ("The federal tax credit covers part of attic insulation "
                           "costs. Ask about the tax credit when you book."),
           # image right after articleBody: "tax credit" sits within T2's
           # money-word window of 1200 and 630, which pre-K53d made 2 R3a hits.
           "image": {"@type": "ImageObject", "url": "https://example.com/a.jpg",
                     "width": 1200, "height": 630}}
LD_STRING = {"@context": "https://schema.org", "@type": "Service",
             "name": "Attic insulation",
             "description": "Xcel pays a $500 rebate for attic insulation."}
LD_OFFER = {"@context": "https://schema.org", "@type": "Service",
            "name": "Attic insulation",
            "offers": {"@type": "Offer", "name": "Attic insulation rebate",
                       "price": 500, "priceCurrency": "USD"}}


def ld_para(obj):
    # Closes the template's <p>, emits the block, reopens a <p>.
    return '</p><script type="application/ld+json">%s</script><p>x' % json.dumps(obj)


class TestD_R3aJsonLd(G.GateCase):
    # G.GateCase: tmp dir + config per test, gate() builds a one-page
    # git-committed site and runs ops/claim_gate/claim_gate.py on it.
    def gate(self, paragraphs, **kw):
        kw.setdefault("allowlist", {"entries": []})
        return super().gate(paragraphs, **kw)

    def test_d1_article_numeric_width_height_no_r3a(self):
        """(d) realistic Article JSON-LD (tax credit text, publisher, ImageObject
        width 1200 / height 630) -> 0 R3a hits."""
        rc, out = self.gate([ld_para(ARTICLE)])
        self.assertR3aClean(rc, out)
        self.assertEqual(G.summary_row(out, "R3a")[0], 0)
        self.assertEqual(G.enumerated(G.section(out, "R3a"))[0], [])
        # The block was read: its two numbers are named as JSON-LD markup.
        self.assertIn("2 T2 raw hit(s) sit on a JSON-LD numeric literal", out)

    def test_d2_ld_string_dollar_rebate_fails(self):
        """(d) JSON-LD STRING "$500 rebate" -> R3a fails."""
        rc, out = self.gate([ld_para(LD_STRING)])
        self.assertR3aFails(rc, out)
        hits, _ = G.enumerated(G.section(out, "R3a"))
        self.assertTrue(any(" T1 " in h and "$500" in h for h in hits), hits)

    def test_d3_offer_numeric_price_with_currency_fails(self):
        """(d) Offer price 500 + priceCurrency USD in a rebate context -> R3a
        FAILS via the JSON-LD currency reading (sub LD$)."""
        rc, out = self.gate([ld_para(LD_OFFER)])
        self.assertR3aFails(rc, out)
        hits, _ = G.enumerated(G.section(out, "R3a"))
        ld = [h for h in hits if " LD$ " in h]
        self.assertEqual(len(ld), 1, hits)
        self.assertIn("price: 500 USD", ld[0])
        self.assertIn("rebate", ld[0].split("trigger:")[1])

    def test_d4_body_dollar_rebate_unchanged(self):
        """(d) body R3a unchanged: a body "$500 rebate" sentence fails."""
        rc, out = self.gate([G.PLANT])
        self.assertR3aFails(rc, out)
        hits, _ = G.enumerated(G.section(out, "R3a"))
        t1 = [h for h in hits if " T1 " in h and "$500" in h]
        self.assertEqual(len(t1), 1, hits)
        self.assertIn(G.PLANT, t1[0])


# ---------------------------------------------------------------- (e)

EC = "embed_callout"
EC_PAGE = """<!DOCTYPE html><html lang="en"><head><title>Calc</title></head><body><main>
<div style="margin:32px 0 0;padding:24px;border:2px solid var(--primary);border-radius:8px;text-align:center">
<p><strong>{heading}</strong></p>
<p>Paste one block of HTML.</p>
<p><a class="btn" href="/embeds.html">{button}</a></p>
</div>
</main></body></html>
"""


class TestE_EmbedCalloutEntities(TempCase):
    def run_ec(self, page_heading, page_button, opt_heading, opt_button):
        site = self.T / "site"
        if site.exists():
            shutil.rmtree(site)
        shutil.copytree(FIXTURES / EC / "clean", site)
        (site / "public" / "good-calculator.html").write_text(
            EC_PAGE.format(heading=page_heading, button=page_button), encoding="utf-8")
        entry = json.loads((site / "manifest.json").read_text(encoding="utf-8"))
        entry["options"].update(heading=opt_heading, button_text=opt_button)
        findings, out = run_module(EC, MODULES / (EC + ".py"), site, entry)
        self.assertEqual(out, "")
        return [f.message for f in findings]

    def test_e1_entity_in_page_matches_plain_option(self):
        """(e) page heading "Quotes &amp; Costs" (and, separately, button
        "Quotes &amp; Costs") matches option "Quotes & Costs": no findings
        from any of the three matchers. (Heading and button are not given the
        same text: DCI counts every raw occurrence of the heading, so a button
        repeating it is 2 headings, before and after K53d.)"""
        self.assertEqual(self.run_ec("Quotes &amp; Costs", "Get the embed code",
                                     "Quotes & Costs", "Get the embed code"), [])
        self.assertEqual(self.run_ec("Take it.", "Quotes &amp; Costs",
                                     "Take it.", "Quotes & Costs"), [])
        self.assertEqual(self.run_ec("Take it.", "Quotes &#38; Costs",
                                     "Take it.", "Quotes & Costs"), [])

    def test_e2_entity_vs_different_words_still_mismatches(self):
        """(e) negative: page "Quotes &amp; Costs" vs option "Quotes and
        Costs" still MISMATCHES (findings from every matcher)."""
        msgs = self.run_ec("Take it.", "Quotes &amp; Costs",
                           "Take it.", "Quotes and Costs")
        for tag in ("[dci]", "[lgm]", "[gci]"):
            self.assertEqual(len([m for m in msgs if m.startswith(tag)]), 1, msgs)
        msgs = self.run_ec("Quotes &amp; Costs", "Get the embed code",
                           "Quotes and Costs", "Get the embed code")
        self.assertEqual(len(msgs), 1, msgs)
        self.assertTrue(msgs[0].startswith("[dci] 0 callout heading(s)"), msgs)


if __name__ == "__main__":
    unittest.main()
