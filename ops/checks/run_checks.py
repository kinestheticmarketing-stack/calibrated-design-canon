#!/usr/bin/env python3
"""run_checks.py -- the shared BUILD check suite runner (K44).

    python3 ops/checks/run_checks.py --site <site-repo> --manifest <file>
        [--only a,b] [--json PATH] [--public-dir public]
        [--modules-dir DIR] [--fixtures-dir DIR]     # testing only

Order: load manifest -> validate every enabled module's data -> run EVERY
selected module's canary -> only if all canaries fire, run the real checks
-> report. Exit codes: 0 clean, 1 findings, 3 canary failure, 2 config/usage
error; precedence 2 > 3 > 1. See README.md.
"""

from __future__ import annotations

import sys

sys.dont_write_bytecode = True  # never leave __pycache__ in canon or a site

import argparse
import importlib.util
import json
import os
import socket
import traceback
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import checklib as C  # noqa: E402

FORBIDDEN_SOURCE = ("ssh ", "paramiko")
# audit event -> indexes of the path args that must not be inside the site
WRITE_EVENTS = {"os.remove": (0,), "os.rename": (0, 1), "os.replace": (0, 1),
                "os.rmdir": (0,), "os.mkdir": (0,), "os.truncate": (0,),
                "os.chmod": (0,), "os.chown": (0,), "os.utime": (0,),
                "os.symlink": (1,), "os.link": (1,), "shutil.rmtree": (0,),
                "shutil.copyfile": (1,), "shutil.copymode": (1,),
                "shutil.copystat": (1,), "shutil.move": (0, 1)}
REMOTE_BINARIES = {"ssh", "scp", "sftp", "rsync", "curl", "wget", "nc"}


# ---------------------------------------------------------------------------
# Safety guards
# ---------------------------------------------------------------------------

def _no_network(*_a, **_k):
    raise OSError("run_checks: network is blocked for BUILD checks")


class _BlockedSocket(socket.socket):
    def __init__(self, *a, **k):
        _no_network()


def install_guards(protected_roots):
    """Block network in-process and refuse writes under protected_roots.
    Irreversible for the life of the process; called from main() only."""
    socket.socket = _BlockedSocket
    socket.create_connection = _no_network
    roots = [str(Path(r).resolve()) for r in protected_roots]

    def inside(p):
        try:
            if isinstance(p, int):
                return False
            s = os.path.realpath(os.fsdecode(p))
        except Exception:
            return False
        return any(s == r or s.startswith(r + os.sep) for r in roots)

    wflags = os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_APPEND | os.O_TRUNC

    def hook(event, args):
        if event == "open":
            path, mode, flags = (list(args) + [None, None, None])[:3]
            writing = (isinstance(mode, str) and any(c in mode for c in "wax+")) \
                or (isinstance(flags, int) and flags & wflags)
            if writing and inside(path):
                raise PermissionError("run_checks: refusing to write inside "
                                      "the site or fixture: %s" % path)
        elif event in WRITE_EVENTS:
            if any(i < len(args) and isinstance(args[i], (str, bytes, os.PathLike))
                   and inside(args[i]) for i in WRITE_EVENTS[event]):
                raise PermissionError("run_checks: refusing %s inside the "
                                      "site or fixture: %r" % (event, args))
        elif event == "socket.connect":
            _no_network()
        elif event == "subprocess.Popen":
            exe = args[0] if args else ""
            argv = args[1] if len(args) > 1 else None
            first = argv[0] if isinstance(argv, (list, tuple)) and argv else exe
            name = os.path.basename(os.fsdecode(first or "")) if first else ""
            if name in REMOTE_BINARIES:
                raise PermissionError("run_checks: refusing to spawn %s" % name)

    sys.addaudithook(hook)


# ---------------------------------------------------------------------------
# Discovery, manifest, validation
# ---------------------------------------------------------------------------

def discover(modules_dir: Path) -> dict:
    return {p.stem: p for p in sorted(modules_dir.glob("*.py"))
            if not p.stem.startswith("_")}


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location("checks_mod_" + name, path)
    mod = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(mod)
    except Exception as exc:
        raise C.ConfigError("module %s failed to import: %s: %s"
                            % (name, exc.__class__.__name__, exc))
    for attr, typ in (("NAME", str), ("DESCRIPTION", str), ("REQUIRES", dict)):
        if not isinstance(getattr(mod, attr, None), typ):
            raise C.ConfigError("module %s: %s missing or not a %s"
                                % (name, attr, typ.__name__))
    if mod.NAME != name:
        raise C.ConfigError("module %s: NAME is %r, must equal the file stem"
                            % (name, mod.NAME))
    if not callable(getattr(mod, "check", None)):
        raise C.ConfigError("module %s: no check(ctx) function" % name)
    if not isinstance(getattr(mod, "OPTIONS", {}), dict):
        raise C.ConfigError("module %s: OPTIONS must be a dict" % name)
    return mod


def build_context(mod, entry, site_root: Path, public_rel: str, site_name: str,
                  canary: bool) -> C.Context:
    """Validate one module's manifest entry and return its Context.
    Raises ConfigError naming module, key and path."""
    name = mod.NAME
    if not isinstance(entry, dict):
        raise C.ConfigError("module %s: manifest entry must be an object" % name)
    extra = set(entry) - {"data", "options"}
    if extra:
        raise C.ConfigError("module %s: unknown entry field(s) %s"
                            % (name, ", ".join(sorted(extra))))
    data_in = entry.get("data", {}) or {}
    opts_in = entry.get("options", {}) or {}
    if not isinstance(data_in, dict) or not isinstance(opts_in, dict):
        raise C.ConfigError("module %s: data and options must be objects" % name)
    literal = set(getattr(mod, "LITERAL_KEYS", set()) or set())
    optional = set(getattr(mod, "OPTIONAL_KEYS", set()) or set())
    if optional - set(mod.REQUIRES):
        raise C.ConfigError("module %s: OPTIONAL_KEYS not in REQUIRES: %s" % (
            name, ", ".join(sorted(optional - set(mod.REQUIRES)))))
    unknown = set(data_in) - set(mod.REQUIRES)
    if unknown:
        raise C.ConfigError("module %s: unknown data key(s) %s (REQUIRES: %s)"
                            % (name, ", ".join(sorted(unknown)),
                               ", ".join(sorted(mod.REQUIRES)) or "none"))
    defaults = dict(getattr(mod, "OPTIONS", {}) or {})
    unknown = set(opts_in) - set(defaults)
    if unknown:
        raise C.ConfigError("module %s: unknown option(s) %s (OPTIONS: %s)"
                            % (name, ", ".join(sorted(unknown)),
                               ", ".join(sorted(defaults)) or "none"))
    data = {}
    for key, desc in mod.REQUIRES.items():
        if key not in data_in and key in optional:
            data[key] = None
            continue
        if key not in data_in:
            raise C.ConfigError("module %s: required data key %r is missing "
                                "from the manifest (%s)" % (name, key, desc))
        val = data_in[key]
        if key in literal:
            data[key] = val
            continue
        vals = val if isinstance(val, list) else [val]
        paths = []
        for v in vals:
            if not isinstance(v, str) or not v:
                raise C.ConfigError("module %s: data key %r must be a path "
                                    "string, got %r" % (name, key, v))
            p = C.resolve_path(v, site_root)
            if not p.exists():
                raise C.ConfigError("module %s: data key %r path does not "
                                    "exist: %s" % (name, key, p))
            paths.append(p)
        data[key] = paths if isinstance(val, list) else paths[0]
    defaults.update(opts_in)
    return C.Context(site_root=site_root, public_dir=site_root / public_rel,
                     data=data, options=defaults, site_name=site_name,
                     module=name, canary=canary)


def run_one(mod, ctx):
    res = mod.check(ctx)
    if res is None:
        res = []
    if not isinstance(res, list) or not all(isinstance(f, C.Finding) for f in res):
        raise TypeError("check() must return list[Finding], got %r" % type(res))
    return res


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------

def parse_args(argv):
    here = Path(__file__).resolve().parent
    p = argparse.ArgumentParser(prog="run_checks.py",
                                description="Shared BUILD check suite (K44).")
    p.add_argument("--site", required=True, help="path to the site repo")
    p.add_argument("--manifest", required=True, help="manifest JSON")
    p.add_argument("--only", default=None, help="comma list of module names")
    p.add_argument("--json", default=None, help="write a JSON report here "
                   "(must be outside --site)")
    p.add_argument("--public-dir", default=None,
                   help="built output dir, relative to --site "
                        "(default: manifest public_dir, else 'public')")
    p.add_argument("--modules-dir", default=str(here / "modules"),
                   help="TESTING: alternate modules directory")
    p.add_argument("--fixtures-dir", default=None,
                   help="TESTING: alternate fixtures directory (default: "
                        "<modules-dir>/../fixtures)")
    return p.parse_args(argv)


def main(argv=None) -> int:
    try:
        args = parse_args(argv)
    except SystemExit as exc:
        return C.EXIT_CONFIG if exc.code else C.EXIT_CLEAN
    out = print
    try:
        return _main(args, out)
    except C.ConfigError as exc:
        out("CONFIG ERROR: %s" % exc)
        out("RESULT: NOT RUN (exit %d)" % C.EXIT_CONFIG)
        return C.EXIT_CONFIG


def _main(args, out) -> int:
    site = Path(args.site).expanduser().resolve()
    if not site.is_dir():
        raise C.ConfigError("--site is not a directory: %s" % site)
    modules_dir = Path(args.modules_dir).expanduser().resolve()
    fixtures_dir = Path(args.fixtures_dir).expanduser().resolve() \
        if args.fixtures_dir else modules_dir.parent / "fixtures"
    if not modules_dir.is_dir():
        raise C.ConfigError("--modules-dir is not a directory: %s" % modules_dir)

    json_path = None
    if args.json:
        json_path = Path(args.json).expanduser().resolve()
        if json_path == site or site in json_path.parents:
            raise C.ConfigError("--json %s is inside --site %s; the runner "
                                "never writes inside the site" % (json_path, site))

    install_guards([site, fixtures_dir])

    # (a) manifest
    mpath = Path(args.manifest).expanduser().resolve()
    try:
        manifest = json.loads(mpath.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise C.ConfigError("manifest %s unreadable: %s" % (mpath, exc))
    if not isinstance(manifest, dict) or not isinstance(manifest.get("modules"), dict):
        raise C.ConfigError("manifest %s: needs an object with a 'modules' "
                            "object" % mpath)
    extra = set(manifest) - {"site", "public_dir", "modules"}
    if extra:
        raise C.ConfigError("manifest %s: unknown top-level field(s) %s"
                            % (mpath, ", ".join(sorted(extra))))
    site_name = str(manifest.get("site", "") or site.name)
    public_rel = args.public_dir or manifest.get("public_dir") or "public"
    if not (site / public_rel).is_dir():
        raise C.ConfigError("public dir does not exist: %s" % (site / public_rel))

    available = discover(modules_dir)
    for n, path in available.items():   # ANY module, enabled or not
        src = path.read_text(encoding="utf-8", errors="replace")
        for bad in FORBIDDEN_SOURCE:
            if bad in src:
                raise C.ConfigError("module %s (%s) contains forbidden text "
                                    "%r; BUILD checks never reach a server"
                                    % (n, path, bad))
    unknown = sorted(set(manifest["modules"]) - set(available))
    if unknown:
        raise C.ConfigError("manifest names unknown module(s): %s (available: "
                            "%s)" % (", ".join(unknown), ", ".join(available)))
    enabled = [n for n in available if n in manifest["modules"]]
    not_enabled = [n for n in available if n not in manifest["modules"]]
    skipped = []
    if args.only:
        only = [s.strip() for s in args.only.split(",") if s.strip()]
        bad = [n for n in only if n not in manifest["modules"]]
        if bad:
            raise C.ConfigError("--only names module(s) not enabled in the "
                                "manifest: %s" % ", ".join(bad))
        skipped = [n for n in enabled if n not in only]
        enabled = [n for n in enabled if n in only]

    # (b) load + validate every selected module's data
    mods, ctxs = {}, {}
    for n in enabled:
        mods[n] = load_module(n, available[n])
        ctxs[n] = build_context(mods[n], manifest["modules"][n], site,
                                public_rel, site_name, canary=False)

    status, findings, canary_fail, errors = {}, {}, {}, {}

    # (c) canaries, all of them, before any real check
    out("CANARIES (%d)" % len(enabled))
    for n in enabled:
        cdir = fixtures_dir / n / "canary"
        cman = cdir / "manifest.json"
        if not cman.is_file():
            canary_fail[n] = "NO CANARY: %s missing" % cman
        else:
            try:
                centry = json.loads(cman.read_text(encoding="utf-8"))
                cpub = centry.pop("public_dir", "public") \
                    if isinstance(centry, dict) else "public"
                cctx = build_context(mods[n], centry, cdir.resolve(), cpub,
                                     "CANARY", canary=True)
                got = run_one(mods[n], cctx)
                if not got:
                    canary_fail[n] = ("BLIND INSTRUMENT: canary %s returned 0 "
                                      "findings" % cdir)
            except Exception as exc:
                canary_fail[n] = "CANARY ERROR: %s: %s" % (
                    exc.__class__.__name__, exc)
        out("  %-28s %s" % (n, canary_fail.get(n, "FIRED")))

    # (d) real checks
    if canary_fail:
        for n in enabled:
            status[n] = "CANARY FAIL" if n in canary_fail else "NOT RUN (a canary failed)"
    else:
        for n in enabled:
            try:
                findings[n] = run_one(mods[n], ctxs[n])
                status[n] = ("FAIL (%d findings)" % len(findings[n])
                             if findings[n] else "PASS")
            except Exception as exc:
                errors[n] = "%s: %s" % (exc.__class__.__name__, exc)
                status[n] = "ERROR (check crashed; judged nothing)"
                traceback.print_exc(file=sys.stderr)
    for n in skipped:
        status[n] = "SKIPPED (--only)"
    for n in not_enabled:
        status[n] = "NOT ENABLED"

    # (e) report
    out("")
    out("MODULES (%d available)" % len(available))
    for n in available:
        tail = ""
        if n in canary_fail:
            tail = " -- " + canary_fail[n]
        elif n in errors:
            tail = " -- " + errors[n]
        out("  %-28s %s%s" % (n, status[n], tail))
    allf = [f for n in enabled for f in findings.get(n, [])]
    out("")
    out("FINDINGS (%d)" % len(allf))
    for f in allf:
        out("  " + f.line())
    codes = []
    if errors:
        codes.append(C.EXIT_CONFIG)
    if canary_fail:
        codes.append(C.EXIT_CANARY)
    if allf:
        codes.append(C.EXIT_FINDINGS)
    code = C.worst_exit(codes)
    n_pass = sum(1 for n in enabled if status.get(n) == "PASS")
    n_fail = sum(1 for n in enabled if n in findings and findings[n])
    out("")
    out("SUMMARY site=%s modules=%d enabled=%d ran=%d pass=%d fail=%d "
        "error=%d canary_fail=%d skipped=%d not_enabled=%d findings=%d exit=%d"
        % (site_name, len(available), len(enabled) + len(skipped),
           len(findings), n_pass, n_fail, len(errors), len(canary_fail),
           len(skipped), len(not_enabled), len(allf), code))
    if not_enabled:
        out("NOT ENABLED: %s" % ", ".join(not_enabled))

    if json_path:
        report = {"site": site_name, "site_root": str(site), "exit": code,
                  "modules": {n: {"status": status[n],
                                  "detail": canary_fail.get(n) or errors.get(n)}
                              for n in available},
                  "findings": [f.as_dict() for f in allf]}
        json_path.parent.mkdir(parents=True, exist_ok=True)
        json_path.write_text(json.dumps(report, indent=2) + "\n",
                             encoding="utf-8")
    return code


if __name__ == "__main__":
    sys.exit(main())
