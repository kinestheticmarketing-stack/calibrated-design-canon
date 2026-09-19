"""Control fixture for R5's SRC surface: a generator module that holds BOTH
prose and a stylesheet, the way every generator in this portfolio does.

src_artifact() emits every tokenize-joined string run of 12+ characters, so
both of the constants below become claim surfaces. Only ONE of them is prose.
This docstring is skipped by src_string_runs() and is not a surface.
"""

PANEL_CSS = (
    "/* Honeypot row. Kept off-screen rather than display:none so a screen "
    "reader can still reduce nothing. */ "
    ".form-row--cw { position: absolute; left: -9999px; top: 0; width: 1px; "
    "height: 1px; overflow: hidden; } "
    ".meter { width: 100%; height: 8px; border-radius: 4px; background: "
    "#eee; } "
    ".meter__fill { width: 50%; height: 100%; background: var(--primary); "
    "transition: width 240ms ease; } "
    ".meter--empty .meter__fill { width: 0%; opacity: 0.5; }"
)

BODY_HTML = (
    "<p>Air sealing typically delivers a 35% bill reduction on Denver homes "
    "that already have adequate attic insulation.</p>"
)


def render(slug):
    return "<style>" + PANEL_CSS + "</style>" + BODY_HTML
