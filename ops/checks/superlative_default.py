"""Shared default list of retired ranking superlatives for ops/checks/modules/superlative_scan.py.

Copied byte-identical from DCI ops/superlative_scan.py RETIRED_PATTERNS, K47, 2026-10-12.
Contents are site-adjudicated; do not edit here without the same adjudication.
"""
import re

RETIRED_PATTERNS = re.compile(
    r"highest[- ]leverage"
    r"|biggest return"
    r"|smallest area,"
    r"|more air per square foot than anywhere"
    r"|cheapest dollar-per-comfort"
    r"|comfort-per-dollar"
    r"|most wind-resistant (?:solution|insulation option)"
    r"|single best (?:thing|starting condition)"
    r"|largest (?:of any (?:suburb|neighborhood)|single comfort upgrade|comfort gap)"
    r"|most efficient retrofit candidates"
    r"|comfort improvement after upgrade is the most dramatic"
    r"|highest[- ]roi|highest[- ]return|isn.t sexy"
    # Added 2026-09-28, lane harness-hardening-2026-09-28 row R2. This one is
    # NOT a superlative about an offering — it ranks a GEOGRAPHY, which is why
    # the standing inclusion test in COPY_VOICE.md explicitly did not reach it
    # and parked it instead. It is enforced here anyway, on the separate
    # ground that the claim is UNSOURCEABLE AS A NATIONAL RANKING: no primary
    # source publishes a state-by-state residential-radon leaderboard. EPA's
    # instrument is the Map of Radon Zones, which classifies COUNTIES (built
    # 1993 to flag areas of POTENTIAL, not to rank states), and CDPHE
    # publishes Colorado's own share while saying nothing about other states.
    # The admission criterion above is "only add strings that have been RULED
    # OUT"; ruled out for want of any possible primary source IS ruled out,
    # so this entry is correctly admitted and stays.
    #
    # CORRECTED 2026-09-28, row R3: this comment previously recorded the claim
    # as "RETRIEVED AND REFUTED", citing Wyoming's 5.1 pCi/L average. That was
    # WRONG and self-defeating — the same EPA Region 8 release puts COLORADO's
    # average at 6.4 pCi/L, HIGHER than Wyoming's, and states "Half of all
    # homes in Colorado have high radon levels" (retrieved 2026-09-28, HTTP
    # 200, browser UA: epa.gov/newsreleases/epa-encourages-rocky-mountain-
    # and-great-plains-region-residents-test-your-nest-and). Nothing refutes
    # the direction of the claim. Only the comparative national RANK is
    # unsourceable. Do not re-derive this; see COPY_VOICE.md's radon record.
    #
    # It was replaced on both pages by the figure CDPHE publishes, now also
    # corroborated by EPA (EPA_R8_RADON_COLORADO). The pattern deliberately
    # omits "in the country" so a reworded rank
    # ("highest residential radon levels of any state") still trips it.
    r"|highest residential radon",
    re.IGNORECASE,
)
