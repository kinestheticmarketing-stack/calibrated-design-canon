"""svc_pending_import -- every staged `_svc_pending_*.py` fragment must import.

Port of GCI `_svc_pending_import_check.py:main` (run by GCI regen_all.sh:144).
The site check calls importlib.import_module on each fragment and fails on any
exception; the defect it was written for (2026-08-28) was a module-level
`NameError: name 'RETROFIT_SCOPE_P' is not defined`. It also fails when the
glob matches nothing ("a pattern that matches nothing is a check that tests
nothing").

The canon suite never imports or executes site code, so "would it import" is
judged statically with ast, which catches every import-time failure the site
check exists for:
  * SyntaxError in the fragment;
  * a bare name loaded by module-level (import-time) code that is not bound
    before use and is not a builtin  -> NameError;
  * `import M` / `from M import x` where M is not a site-local module, not
    stdlib and not findable on sys.path  -> ModuleNotFoundError;
  * `from M import x` where M is site-local and binds no top-level `x`
    -> ImportError;
  * a site-local module imported at import time that itself fails any of the
    above (analysed recursively, memoised, cycle-safe).
Code inside `try:` blocks that have an except handler is treated as guarded
(its failures are caught), and the `if __name__ == "__main__":` block is not
executed on import. A module that uses `globals()`/`exec`/`eval` at import
time, or star-imports from a module we cannot read, has its undefined-name
test skipped (cannot judge statically; import resolution is still checked).
Runtime-only failures (an exception raised by a called function) are outside
a static port; the site check's own docstring calls import "the floor".
"""

import ast
import builtins
import importlib.util
import sys
from pathlib import Path

NAME = "svc_pending_import"
DESCRIPTION = ("Every _svc_pending_*.py staging fragment would import "
               "(syntax, undefined module-level names, unresolved imports), judged via ast.")
REQUIRES = {}
OPTIONS = {
    # glob relative to the site root (GCI: '_svc_pending_*.py', non-recursive)
    "glob": "_svc_pending_*.py",
    # file names the glob matches that are not fragments (the site check itself)
    "exclude": ["_svc_pending_import_check.py"],
    # dirs (relative to site root) searched for site-local modules; the site
    # check puts its own dir (the repo root) on sys.path
    "search_dirs": ["."],
}

_BUILTINS = set(dir(builtins)) | {
    "__name__", "__file__", "__doc__", "__builtins__", "__spec__",
    "__loader__", "__package__", "__cached__", "__path__", "__annotations__",
}
_DYNAMIC_CALLS = {"globals", "exec", "eval", "vars", "locals"}


def _is_main_guard(test):
    if not isinstance(test, ast.Compare) or len(test.ops) != 1:
        return False
    sides = [test.left] + list(test.comparators)
    has_name = any(isinstance(s, ast.Name) and s.id == "__name__" for s in sides)
    has_main = any(isinstance(s, ast.Constant) and s.value == "__main__" for s in sides)
    return has_name and has_main and isinstance(test.ops[0], ast.Eq)


def _target_names(t):
    if isinstance(t, ast.Name):
        return [t.id]
    if isinstance(t, (ast.Tuple, ast.List)):
        out = []
        for e in t.elts:
            out += _target_names(e)
        return out
    if isinstance(t, ast.Starred):
        return _target_names(t.value)
    return []  # attribute / subscript: binds no name


class _Analyzer:
    """Resolves site-local modules and analyses them, memoised."""

    def __init__(self, site_root, search_dirs):
        self.site_root = site_root
        self.search = [(site_root / d).resolve() for d in search_dirs]
        self.memo = {}      # path -> (problems list, exported names set|None)
        self.active = set()

    def locate(self, dotted):
        parts = dotted.split(".")
        for base in self.search:
            p = base.joinpath(*parts)
            if p.with_suffix(".py").is_file():
                return p.with_suffix(".py")
            if (p / "__init__.py").is_file():
                return p / "__init__.py"
        return None

    def external_ok(self, dotted):
        top = dotted.split(".")[0]
        if top in sys.builtin_module_names or top in getattr(sys, "stdlib_module_names", ()):
            return True
        # Top-level find_spec locates without executing anything.
        try:
            return importlib.util.find_spec(top) is not None
        except (ImportError, ValueError):
            return False

    def label(self, path):
        try:
            return path.relative_to(self.site_root).as_posix()
        except ValueError:
            return str(path)

    def analyse(self, path):
        """Return (problems, exports). problems: list of (lineno, message, quote).
        exports: set of top-level names, or None meaning 'anything' (unknowable)."""
        path = path.resolve()
        if path in self.memo:
            return self.memo[path]
        if path in self.active:          # import cycle: assume fine, Python
            return [], None              # tolerates partial modules for us here
        self.active.add(path)
        try:
            res = _ModuleWalk(self, path).run()
        finally:
            self.active.discard(path)
        self.memo[path] = res
        return res


class _ModuleWalk:
    def __init__(self, an, path):
        self.an = an
        self.path = path
        self.problems = []
        self.bound = set()
        self.exports_unknown = False
        self.lines = []

    # -- helpers -------------------------------------------------------------
    def problem(self, node, msg):
        ln = getattr(node, "lineno", 0)
        quote = self.lines[ln - 1].strip() if 0 < ln <= len(self.lines) else ""
        self.problems.append((ln, msg, quote))

    def run(self):
        try:
            src = self.path.read_text(encoding="utf-8")
            self.lines = src.splitlines()
            tree = ast.parse(src, filename=str(self.path))
        except SyntaxError as e:
            return [(e.lineno or 0, "SyntaxError: %s" % e.msg,
                     (e.text or "").strip())], None
        except (UnicodeDecodeError, ValueError) as e:
            return [(0, "%s: %s" % (type(e).__name__, e), "")], None
        self.future_ann = any(
            isinstance(s, ast.ImportFrom) and s.module == "__future__"
            and any(a.name == "annotations" for a in s.names) for s in tree.body)
        # Dynamic namespace tricks at import time: cannot judge names.
        self.check_names = not self._uses_dynamic(tree)
        self.block(tree.body, guarded=False, scope=None)
        exports = None if self.exports_unknown else set(self.bound)
        if any(isinstance(s, (ast.FunctionDef, ast.AsyncFunctionDef))
               and s.name == "__getattr__" for s in tree.body):
            exports = None
        return self.problems, exports

    def _uses_dynamic(self, tree):
        for n in ast.walk(tree):
            if (isinstance(n, ast.Call) and isinstance(n.func, ast.Name)
                    and n.func.id in _DYNAMIC_CALLS):
                return True
        return False

    def is_bound(self, name, scope):
        if scope is not None and name in scope:
            return True
        return name in self.bound or name in _BUILTINS

    def bind(self, names, scope):
        (scope if scope is not None else self.bound).update(names)

    # -- expressions ---------------------------------------------------------
    def expr(self, node, guarded, scope, local=frozenset()):
        if node is None:
            return
        if isinstance(node, ast.Name):
            if isinstance(node.ctx, ast.Load) and node.id not in local \
                    and not self.is_bound(node.id, scope):
                if self.check_names and not guarded:
                    self.problem(node, "NameError: name %r is not defined" % node.id)
            return
        if isinstance(node, ast.Lambda):
            a = node.args
            for d in list(a.defaults) + [d for d in a.kw_defaults if d]:
                self.expr(d, guarded, scope, local)
            return                                # body runs only when called
        if isinstance(node, (ast.ListComp, ast.SetComp, ast.GeneratorExp, ast.DictComp)):
            inner = set(local)
            for i, gen in enumerate(node.generators):
                # first iterable is evaluated in the enclosing scope
                self.expr(gen.iter, guarded, scope, local if i == 0 else frozenset(inner))
                inner.update(_target_names(gen.target))
                for c in gen.ifs:
                    self.expr(c, guarded, scope, frozenset(inner))
            if isinstance(node, ast.DictComp):
                self.expr(node.key, guarded, scope, frozenset(inner))
                self.expr(node.value, guarded, scope, frozenset(inner))
            else:
                self.expr(node.elt, guarded, scope, frozenset(inner))
            return
        if isinstance(node, ast.NamedExpr):
            self.expr(node.value, guarded, scope, local)
            self.bind([node.target.id], scope)
            return
        for child in ast.iter_child_nodes(node):
            if isinstance(child, ast.expr):
                self.expr(child, guarded, scope, local)
            elif isinstance(child, (ast.keyword, ast.comprehension, ast.arguments,
                                    ast.arg, ast.FormattedValue)):
                for sub in ast.iter_child_nodes(child):
                    if isinstance(sub, ast.expr):
                        self.expr(sub, guarded, scope, local)

    # -- imports -------------------------------------------------------------
    def do_import(self, node, guarded, scope):
        an = self.an
        if isinstance(node, ast.Import):
            for a in node.names:
                self.import_module(node, a.name, guarded)
                self.bind([a.asname or a.name.split(".")[0]], scope)
            return
        # ImportFrom
        if node.module == "__future__":
            return
        if node.level:
            pkg_dir = self.path.parent
            if self.path.name != "__init__.py" and not (pkg_dir / "__init__.py").is_file():
                if not guarded:
                    self.problem(node, "ImportError: attempted relative import "
                                       "with no known parent package")
                self.bind([a.asname or a.name for a in node.names if a.name != "*"], scope)
                return
            base = pkg_dir
            for _ in range(node.level - 1):
                base = base.parent
            target = base.joinpath(*(node.module or "").split(".")) if node.module else base
            loc = (target.with_suffix(".py") if target.with_suffix(".py").is_file()
                   else (target / "__init__.py" if (target / "__init__.py").is_file() else None))
            dotted = None
        else:
            dotted = node.module
            loc = an.locate(dotted)
        exports = None
        if loc is not None:
            probs, exports = an.analyse(loc)
            if probs and not guarded:
                ln, msg, _q = probs[0]
                self.problem(node, "importing %s fails: %s:%s %s"
                             % (node.module or ".", an.label(loc), ln, msg))
        elif dotted is not None:
            if not an.external_ok(dotted) and not guarded:
                self.problem(node, "ModuleNotFoundError: No module named %r"
                             % dotted.split(".")[0])
        else:
            if not guarded:
                self.problem(node, "ImportError: cannot resolve relative import")
        for a in node.names:
            if a.name == "*":
                if exports is None:
                    self.exports_unknown = True
                    self.check_names = False
                else:
                    self.bind({n for n in exports if not n.startswith("_")}, scope)
                continue
            if loc is not None and exports is not None and a.name not in exports \
                    and an.locate((dotted + "." + a.name) if dotted else a.name) is None \
                    and not guarded:
                self.problem(node, "ImportError: cannot import name %r from %r"
                             % (a.name, node.module))
            self.bind([a.asname or a.name], scope)

    def import_module(self, node, dotted, guarded):
        loc = self.an.locate(dotted)
        if loc is not None:
            probs, _ = self.an.analyse(loc)
            if probs and not guarded:
                ln, msg, _q = probs[0]
                self.problem(node, "importing %s fails: %s:%s %s"
                             % (dotted, self.an.label(loc), ln, msg))
        elif not self.an.external_ok(dotted) and not guarded:
            self.problem(node, "ModuleNotFoundError: No module named %r"
                         % dotted.split(".")[0])

    # -- statements ----------------------------------------------------------
    def args_eval(self, args, guarded, scope):
        for d in list(args.defaults) + [d for d in args.kw_defaults if d]:
            self.expr(d, guarded, scope)
        if not self.future_ann:
            for a in args.posonlyargs + args.args + args.kwonlyargs + \
                    [x for x in (args.vararg, args.kwarg) if x]:
                self.expr(a.annotation, guarded, scope)

    def block(self, stmts, guarded, scope):
        for s in stmts:
            self.stmt(s, guarded, scope)

    def stmt(self, s, guarded, scope):
        E = lambda n: self.expr(n, guarded, scope)  # noqa: E731
        if isinstance(s, (ast.Import, ast.ImportFrom)):
            self.do_import(s, guarded, scope)
        elif isinstance(s, (ast.FunctionDef, ast.AsyncFunctionDef)):
            for d in s.decorator_list:
                E(d)
            self.args_eval(s.args, guarded, scope)
            if not self.future_ann:
                E(s.returns)
            self.bind([s.name], scope)
        elif isinstance(s, ast.ClassDef):
            for d in s.decorator_list:
                E(d)
            for b in s.bases:
                E(b)
            for k in s.keywords:
                E(k.value)
            cls_scope = set(scope) if scope is not None else set()
            self.block(s.body, guarded, cls_scope)
            self.bind([s.name], scope)
        elif isinstance(s, ast.Assign):
            E(s.value)
            for t in s.targets:
                self.target(t, guarded, scope)
        elif isinstance(s, ast.AnnAssign):
            E(s.value)
            if not self.future_ann and scope is None:
                E(s.annotation)
            if s.value is not None:
                self.target(s.target, guarded, scope)
        elif isinstance(s, ast.AugAssign):
            if isinstance(s.target, ast.Name):
                self.expr(ast.copy_location(ast.Name(s.target.id, ast.Load()), s.target),
                          guarded, scope)
            E(s.value)
            self.target(s.target, guarded, scope)
        elif isinstance(s, ast.If):
            if _is_main_guard(s.test):
                self.block(s.orelse, guarded, scope)   # body not run on import
                return
            E(s.test)
            self.branches([s.body, s.orelse], guarded, scope)
        elif isinstance(s, (ast.For, ast.AsyncFor)):
            E(s.iter)
            self.target(s.target, guarded, scope)
            self.branches([s.body, s.orelse], guarded, scope)
        elif isinstance(s, ast.While):
            E(s.test)
            self.branches([s.body, s.orelse], guarded, scope)
        elif isinstance(s, (ast.With, ast.AsyncWith)):
            for it in s.items:
                E(it.context_expr)
                if it.optional_vars is not None:
                    self.target(it.optional_vars, guarded, scope)
            self.block(s.body, guarded, scope)
        elif isinstance(s, (ast.Try, getattr(ast, "TryStar", ast.Try))):
            caught = bool(s.handlers)
            self.block(s.body, guarded or caught, scope)
            for h in s.handlers:
                E(h.type)
                if h.name:
                    self.bind([h.name], scope)
                self.block(h.body, guarded, scope)
            self.block(s.orelse, guarded, scope)
            self.block(s.finalbody, guarded, scope)
        elif isinstance(s, getattr(ast, "Match", ())):
            E(s.subject)
            for c in s.cases:
                for n in ast.walk(c.pattern):
                    nm = getattr(n, "name", None)
                    if isinstance(nm, str):
                        self.bind([nm], scope)
                E(c.guard)
            self.branches([c.body for c in s.cases], guarded, scope)
        elif isinstance(s, ast.Delete):
            for t in s.targets:
                if not isinstance(t, ast.Name):
                    self.target(t, guarded, scope)
        elif isinstance(s, (ast.Global, ast.Nonlocal, ast.Pass, ast.Break,
                            ast.Continue)):
            pass
        else:  # Expr, Return, Raise, Assert, ...
            for child in ast.iter_child_nodes(s):
                if isinstance(child, ast.expr):
                    E(child)

    def target(self, t, guarded, scope):
        if isinstance(t, (ast.Attribute, ast.Subscript)):
            self.expr(t.value, guarded, scope)
            if isinstance(t, ast.Subscript):
                self.expr(t.slice, guarded, scope)
        elif isinstance(t, (ast.Tuple, ast.List)):
            for e in t.elts:
                self.target(e, guarded, scope)
        elif isinstance(t, ast.Starred):
            self.target(t.value, guarded, scope)
        self.bind(_target_names(t), scope)

    def branches(self, bodies, guarded, scope):
        # Conditional code: a name bound on any branch counts as bound after
        # (lenient: never flags a name some path defines).
        for b in bodies:
            self.block(b, guarded, scope)


def check(ctx):
    excl = set(ctx.options["exclude"])
    files = sorted(p for p in ctx.site_root.glob(ctx.options["glob"])
                   if p.is_file() and p.name not in excl)
    if not files:
        # Site behaviour: exit 1 with "the pattern is stale or the fragments
        # were merged. Remove this check deliberately."
        return [ctx.finding(ctx.options["glob"],
                            "no files match %r: the pattern is stale or the fragments "
                            "were merged; remove this check deliberately"
                            % ctx.options["glob"])]
    an = _Analyzer(ctx.site_root.resolve(), ctx.options["search_dirs"])
    findings = []
    for f in files:
        label = f.relative_to(ctx.site_root).as_posix()
        problems, _ = an.analyse(f)
        for ln, msg, quote in problems:
            findings.append(ctx.finding(
                label, "%s:%s will not import: %s" % (label, ln, msg), quote))
    return findings
