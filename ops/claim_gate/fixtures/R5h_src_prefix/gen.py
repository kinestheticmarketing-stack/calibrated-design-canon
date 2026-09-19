"""R5h -- THE 48-CHARACTER PREFIX PROBE, AS A CONTROL.

src_dup used to probe the rendered index with only the FIRST 48 NORMALIZED
CHARACTERS of a generator sentence. Two generator strings sharing that prefix
were indistinguishable to it, so a string whose OPENING matched rendered prose
was cleared no matter what it went on to assert.

The string below opens with page.html's real, attributed settling sentence and
then adds a figure that renders NOWHERE and is sourced by nothing. Under the
prefix probe this fixture is CLEAN -- the silent miss. Under the full-sentence
probe it FIRES. This docstring is not a surface.
"""

SETTLING_BLOCK = (
    '<p>Loose-fill cellulose settles 10 to 20 percent over its functional '
    'life; rebate paperwork cuts your bill by 47% in the first year.</p>'
)
