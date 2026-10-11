"""ast_preflight -- every generator/shared module (_*.py in the site root)
must compile. Port of the PYGUARD heredoc in regen_all.sh:36-49, byte-identical
in DCI, LGM and GCI: `for f in sorted(glob.glob('_*.py')): ast.parse(...)`,
run from the repo root (regen_all.sh does `cd "$(dirname "$0")"`).

Site code is only parsed with ast.parse, never imported or executed.
"""

import ast

NAME = "ast_preflight"
DESCRIPTION = "Every _*.py generator/shared module in the site root parses (ast.parse)."
REQUIRES = {}
OPTIONS = {
    # glob relative to the site root; the sites use '_*.py' (non-recursive)
    "glob": "_*.py",
}


def check(ctx):
    files = sorted(p for p in ctx.site_root.glob(ctx.options["glob"]) if p.is_file())
    if not files:
        # The site guard would silently pass on zero files; here that would be
        # a vacuous pass, so refuse to judge instead.
        raise RuntimeError("ast_preflight: no files match %r under the site root"
                           % ctx.options["glob"])
    findings = []
    for f in files:
        label = f.relative_to(ctx.site_root).as_posix()
        try:
            src = f.read_text(encoding="utf-8")
            ast.parse(src, filename=label)
        except SyntaxError as e:
            # Same content as the site line: "SYNTAX ERROR  {f}:{lineno}  {msg}"
            findings.append(ctx.finding(
                label, "SYNTAX ERROR %s:%s %s" % (label, e.lineno, e.msg),
                (e.text or "").strip()))
        except (UnicodeDecodeError, ValueError) as e:
            # In the site heredoc these escape uncaught and abort regen_all.sh
            # (set -e): the build fails just the same, so they are findings.
            findings.append(ctx.finding(
                label, "does not compile: %s" % type(e).__name__, str(e)))
    return findings
