"""PLANTED DEFECT (the 2026-08-28 GCI failure): references a _service_pages
constant by bare name with no import preamble -> NameError on import."""

SERVICE = {"slug": "broken", "body": RETROFIT_SCOPE_P}
