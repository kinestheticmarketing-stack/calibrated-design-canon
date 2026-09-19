"""Control fixture for R2 on the SRC surface: a generator module holding a
script bundle AND prose.

The bundle's developer COMMENT records a wrong-utility bug that was already
fixed. The prose below it still makes the wrong-utility claim for real. A rule
that reads the bundle as prose condemns the repair note; a rule that reads only
the prose condemns the claim. This docstring is not a surface.
"""

CHECKER_JS = (
    "(function () { 'use strict'; "
    "var go = document.getElementById('rc-go'); if (!go) { return; } "
    "var out = document.getElementById('rc-out'); "
    "// CORRECTED 2026-09-08: these branches used to return an Atmos-attributed "
    "// verdict computed from build era alone. The tool never asks which town "
    "// the visitor is in, and Atmos does not serve three of the nine towns "
    "// this site covers - so a Severance visitor completed this checker and "
    "// was told they clear the Atmos threshold, which is a wrong-utility "
    "// claim. Do NOT re-attribute this to a named payer. "
    "go.addEventListener('click', function () { "
    "out.innerHTML = '<p>Ask your own gas utility for its current terms.</p>'; "
    "out.classList.add('is-visible'); }); }());"
)

INTRO_HTML = (
    "<p>Atmos Energy is the natural gas utility for most locations in "
    "Severance, and its residential rebate is the one to ask about.</p>"
)


def render(slug):
    return INTRO_HTML + "<script>" + CHECKER_JS + "</script>"
