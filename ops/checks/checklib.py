"""checklib -- the module contract for the shared BUILD check suite (K44).

A check module is ops/checks/modules/<name>.py and exposes:

    NAME = "<name>"                  # must equal the file stem
    DESCRIPTION = "one line"
    REQUIRES = {"key": "one-line description"}   # manifest data keys
    LITERAL_KEYS = {"key"}           # optional: REQUIRES keys that are literal
                                     # values, not paths (no existence check)
    OPTIONAL_KEYS = {"key"}          # optional: REQUIRES keys a manifest may
                                     # omit (then data[key] is None)
    OPTIONS = {"opt": default}       # optional: option defaults
    def check(ctx) -> list[Finding]

Every module has a canary: ops/checks/fixtures/<name>/canary/ is a mini site
root (with its own public/ as needed) plus canary/manifest.json holding
{"data": {...}, "options": {...}} for that fixture. The canary passes when
check() on the fixture returns >= 1 Finding. See README.md / MODULE_TEMPLATE.md.

Stdlib only. Imported by run_checks.py and by every module.
"""

from __future__ import annotations

import html as _html
import re
from dataclasses import dataclass, field
from html.parser import HTMLParser
from pathlib import Path

# ---------------------------------------------------------------------------
# Exit codes. Precedence when several apply: 2 > 3 > 1 > 0.
# ---------------------------------------------------------------------------
EXIT_CLEAN = 0      # every enabled module ran, its canary fired, no findings
EXIT_FINDINGS = 1   # at least one real check returned findings
EXIT_CONFIG = 2     # config/usage error: bad manifest, unknown module, missing
                    # data key or path, unsafe --json, forbidden module source,
                    # or a real check that crashed (it judged nothing)
EXIT_CANARY = 3     # canary failure: NO CANARY, BLIND INSTRUMENT, canary crash

EXIT_PRECEDENCE = (EXIT_CONFIG, EXIT_CANARY, EXIT_FINDINGS, EXIT_CLEAN)

CANON_ROOT = Path(__file__).resolve().parents[2]
CHECKS_DIR = Path(__file__).resolve().parent
QUOTE_MAX = 200


def worst_exit(codes) -> int:
    codes = set(codes)
    for c in EXIT_PRECEDENCE:
        if c in codes:
            return c
    return EXIT_CLEAN


def _one_line(s: str) -> str:
    return re.sub(r"\s+", " ", str(s or "")).strip()


@dataclass
class Finding:
    """One defect. page = path relative to the public dir (or site root if the
    file is outside public/). quote = the offending text, at most one sentence;
    whitespace is collapsed and it is truncated to 200 chars."""
    module: str
    page: str
    message: str
    quote: str = ""

    def __post_init__(self):
        self.page = _one_line(self.page) or "(site)"
        self.message = _one_line(self.message)
        q = _one_line(self.quote)
        if len(q) > QUOTE_MAX:
            q = q[:QUOTE_MAX - 3] + "..."
        self.quote = q

    def line(self) -> str:
        """`page | module | quote`; the message is appended in brackets when
        it adds something the quote does not say."""
        q = self.quote or self.message
        tail = " [%s]" % self.message if self.message and self.message != q else ""
        return "%s | %s | %s%s" % (self.page, self.module, q, tail)

    def as_dict(self) -> dict:
        return {"module": self.module, "page": self.page,
                "message": self.message, "quote": self.quote}


class ConfigError(Exception):
    """Raised for anything that makes a run untrustworthy before it starts."""


def resolve_path(value, site_root: Path) -> Path:
    """Resolve a manifest path value.
    'canon:<rel>' -> relative to the canon repo root; absolute -> as is;
    anything else -> relative to site_root."""
    s = str(value)
    if s.startswith("canon:"):
        return (CANON_ROOT / s[len("canon:"):]).resolve()
    p = Path(s).expanduser()
    return p.resolve() if p.is_absolute() else (site_root / p).resolve()


class _TextExtractor(HTMLParser):
    SKIP = {"script", "style", "template", "noscript"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts = []
        self.depth = 0

    def handle_starttag(self, tag, attrs):
        if tag in self.SKIP:
            self.depth += 1
        self.parts.append(" ")

    def handle_endtag(self, tag):
        if tag in self.SKIP and self.depth:
            self.depth -= 1
        self.parts.append(" ")

    def handle_data(self, data):
        if not self.depth:
            self.parts.append(data)


@dataclass
class Context:
    """What check(ctx) receives. Treat it as read-only.

    site_root  Path of the site repo (or of the canary fixture)
    public_dir Path of the built output (site_root / manifest public_dir)
    data       REQUIRES key -> resolved Path (or list of Paths); LITERAL_KEYS
               keep their manifest value unchanged
    options    module OPTIONS defaults overlaid with the manifest options
    site_name  manifest "site" (e.g. "DCI"); "CANARY" when running a canary
    module     the module NAME (handy for building Findings)
    canary     True on the canary run. Modules must NOT branch on it.
    """
    site_root: Path
    public_dir: Path
    data: dict = field(default_factory=dict)
    options: dict = field(default_factory=dict)
    site_name: str = ""
    module: str = ""
    canary: bool = False

    def resolve(self, value) -> Path:
        """Resolve a path value the same way manifest data is resolved."""
        return resolve_path(value, self.site_root)

    def iter_html(self, root: Path | None = None):
        """Sorted *.html files under public_dir (or root), recursively."""
        base = Path(root) if root else self.public_dir
        return sorted(p for p in base.rglob("*.html") if p.is_file())

    @staticmethod
    def read_text(path) -> str:
        return Path(path).read_text(encoding="utf-8", errors="replace")

    @staticmethod
    def visible_text(html_src: str) -> str:
        """Text a reader sees: script/style/template/noscript bodies and all
        tags removed, entities unescaped, whitespace collapsed."""
        p = _TextExtractor()
        p.feed(html_src)
        p.close()
        return _one_line(_html.unescape("".join(p.parts)))

    def rel(self, path) -> str:
        """Page label for a Finding: relative to public_dir, else site_root."""
        p = Path(path).resolve()
        for base in (self.public_dir.resolve(), self.site_root.resolve()):
            try:
                return p.relative_to(base).as_posix()
            except ValueError:
                pass
        return str(path)

    def finding(self, page, message, quote="") -> Finding:
        """Shorthand: Finding(self.module, rel(page) if a Path, ...)."""
        pg = self.rel(page) if isinstance(page, Path) else str(page)
        return Finding(self.module, pg, message, quote)
