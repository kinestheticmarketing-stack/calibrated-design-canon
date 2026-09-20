"""R4 control: a stacking assertion inside a script bundle's string literal.

The module holds a STYLESHEET and a SCRIPT BUNDLE. The stylesheet is not a
proposition surface and must be removed through a NAMED, COUNTED filter. The
claim assigned to el.innerHTML inside the bundle IS a proposition -- the
rendered page reads exactly that literal out of the same bytes -- and must
FIRE.
This docstring is not a surface.
"""

PANEL_CSS = (
    '/* Panel chrome. Kept in the generator so one edit reaches every page. */ .panel { margin: 0; padding: 18px 22px; border-radius: 8px; } .panel__bar { width: 100%; height: 8px; background: #eee; } .panel__fill { width: 50%; height: 100%; transition: width 240ms; } .panel--empty .panel__fill { width: 0%; opacity: 0.5; }'
)

PANEL_JS = (
    "(function () { 'use strict'; var el = document.getElementById('panel-out'); if (!el) { return; } el.innerHTML = '<p>The Whole Home Efficiency Bonus stacks on top of the Xcel Insulation and Air Sealing Rebate on the same job.</p>'; el.classList.add('is-visible'); }());"
)

def render(slug):
    return "<style>" + PANEL_CSS + "</style>" + \
           "<script>" + PANEL_JS + "</script>"
