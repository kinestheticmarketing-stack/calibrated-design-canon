"""NEG15 -- CORRECT COPY. The generator string below renders VERBATIM into
page.html in this same fixture directory, where the figure is attributed by a
cited-stat block on the page. Counting it a second time off the generator is
double-counting one claim, which spec R5's src_dup filter exists to prevent.

The vector: the generator string carries MARKUP and an EM DASH inside its
first 48 characters, and the rendered index src_dup probes is built from TXT
-- tags stripped, dashes folded to "-". Comparing a RAW generator byte string
against a NORMALIZED rendered index makes the match structurally impossible,
so the filter could never fire on exactly the restatements it was written for.
Measured on DCI at ba2fc22: six of seven surviving SRC findings were rendered
prose the filter could not see, and 106 SRC probes portfolio-wide never
matched. This fixture FALSE-ALARMS on the unnormalized probe and is clean on
the normalized one.
"""

EAVES_BLOCK = (
    '<p>Homes built before 1990 in this region — see the '
    '<a href="/eaves.html">eaves guide</a> — lose 20-40% of their '
    'attic insulation performance to wind-washing at the eaves.</p>'
)
