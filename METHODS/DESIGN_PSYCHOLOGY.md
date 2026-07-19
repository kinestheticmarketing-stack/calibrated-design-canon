# DESIGN_PSYCHOLOGY.md

*A method-level specification under [Calibrated Vibe Coding](../CVC.md).*
*Source-of-truth document for design-psychology principles across every
web property built under the Calibrated Stack — DCI, Don's Garage
Automotive and Transmission, the Kinesthetic Marketing funnel, every
Porter tenant site, and whatever gets built next.*

═══════════════════════════════════════════════════════════════
THE META-PRINCIPLE
═══════════════════════════════════════════════════════════════

There is no neutral design. Every page a visitor lands on runs
psychology on them — a blank, unconsidered template makes choices
about comfort, attention, and trust just as surely as a deliberately
built one does, it just makes those choices by accident. The only
real option a builder has is whether the psychology running on a
visitor's brain is deliberate or accidental. This document exists so
it's deliberate.

The seven principles below are not tricks. They are long-studied,
well-established observations about how human brains actually decide
under uncertainty, translated into things a builder can check against
a live page. Used honestly, they remove friction between a real
visitor and a real answer to what they came looking for. Used
dishonestly, they become the dark-pattern playbook that gives
persuasive design its bad name. The distinction matters because the
same brain these principles describe is also very good at noticing
when it's been played, and it punishes the site that did it by
leaving and not coming back. Applied with respect for the visitor, the
honest version of every principle here outperforms the manipulative
version over any time horizon longer than a single session — trust
compounds, and so does its absence.

Run this file's checklists against every page before it ships: DCI,
Don's Garage, the Kinesthetic Marketing funnel, every Porter tenant
site, and anything built after it.

═══════════════════════════════════════════════════════════════
1. JAKOB'S LAW — visitors bring the whole internet with them
═══════════════════════════════════════════════════════════════

**The principle.** A visitor has spent years on other websites before
they ever land on yours, and their brain arrives pre-loaded with firm,
mostly unconscious expectations about how a page works — the logo
goes home, the cart lives top-right, the obvious button at the bottom
of a form is the one that submits it. Those expectations were built
by every site the visitor has ever used, not by yours, and yours gets
judged against all of them at once, whether that's fair or not.

**Where sites break it.** A page breaks an invisible convention to
look distinctive or "on brand" — navigation in an unfamiliar spot, a
logo that doesn't link home, a checkout or contact flow that doesn't
move the way every comparable flow the visitor has ever completed
moves. The visitor doesn't consciously think "this violates
convention." They register a half-second of friction, and that
half-second reads as something being wrong, even when nothing about
the actual offer changed.

**The practice.** Spend originality on the idea and the craft — the
offer, the copy, the character of the brand. Spend none of it on the
mechanics. Navigation goes where navigation goes. Forms behave like
forms everywhere else on the internet already taught the visitor to
expect. Boring mechanics are what let an original idea actually land.

**Audit checklist:**
- Does the logo link to the homepage, from every page, every time?
- Is primary navigation exactly where every comparable site already
  puts it?
- Does the form, checkout, or contact flow match a shape the visitor
  already knows, rather than a novel shape invented for this site?
- Would a first-time visitor need to stop and figure out how anything
  on the page works?

═══════════════════════════════════════════════════════════════
2. FITTS'S LAW — make the right choice the easy choice
═══════════════════════════════════════════════════════════════

**The principle.** How long it takes someone to hit a target is a
function of the target's size and its distance from where the
person's hand already is. On a page, that means the effort required
to complete an action is a measurable, physical quantity, and it
scales directly with how big the thing is and where it sits — most
unforgivingly under a moving thumb on a phone.

**Where sites break it.** The one action that actually matters to the
business — the button that moves things forward — gets sized and
placed the same as five lower-stakes links sitting around it, or it
sits at the far edge of a one-handed mobile thumb's natural reach. The
visitor doesn't refuse to act; they simply don't reach for the thing
that costs more effort to reach than everything competing with it.

**The practice.** The single most important action on any page has to
be the physically easiest thing on that page to do, especially on a
phone held in one hand. Everything competing with it should visibly
cost more effort to use.

**Audit checklist:**
- Is the primary CTA visually and physically larger than any
  competing link near it?
- On mobile, does the primary CTA sit inside the natural thumb arc,
  not a corner that forces a hand shift?
- Run an actual one-handed thumb test on a phone — can the primary
  action be hit without repositioning the hand?
- Is the primary CTA ever crowded by other same-size, same-weight
  elements competing for the same tap?

═══════════════════════════════════════════════════════════════
3. SOCIAL PROOF AT THE POINT OF DOUBT
═══════════════════════════════════════════════════════════════

**The principle.** Evidence that other people already trust something
changes behavior — but only when it shows up at the exact moment a
visitor is actually uncertain. Proof warehoused on a testimonials page
nobody visits does almost nothing; the same proof sitting beside the
specific doubt it answers does most of the work.

**Where sites break it.** All of a site's proof lives in one place —
a "Reviews" tab, a testimonials section — disconnected from the
pricing table, the signup form, or the CTA where the visitor is
actually deciding whether to trust this business enough to act.

**The practice.** Walk the page as a skeptical stranger and mark every
point where a reasonable person would hesitate — "does this work for
someone like me," "is this actually safe," "will anyone answer if I
reach out." Put a specific piece of evidence in the visitor's eyeline
at each of those exact moments, not three scrolls or a page away.

**Audit checklist:**
- Is there proof directly next to every CTA, pricing table, and form,
  not filed on a separate page?
- Is the proof specific — a number, a name, a before/after — rather
  than generic praise?
- Does each piece of proof answer a doubt a visitor would actually
  have at that spot on the page?
- Is there a real hesitation point anywhere on the page with no proof
  near it at all?

═══════════════════════════════════════════════════════════════
4. AUTHORITY NEXT TO THE ASK
═══════════════════════════════════════════════════════════════

**The principle.** A real credential, certification, recognizable
client, press mention, or a founder's genuine background lends
credibility — and that credibility bleeds into everything placed near
it. This only runs in the site's favor when the signal is real and a
visitor could verify it if they tried; a hollow badge that doesn't
survive a second look costs more trust than it buys.

**Where sites break it.** Real authority signals exist somewhere on
the site but sit buried on an About page nobody clicks, several steps
from the actual decision point — or the signals on display are
decorative, unverifiable badges present purely for the visual weight
of looking official.

**The practice.** Put verifiable authority — certifications,
recognizable clients, press, a founder's actual track record —
directly beside the point where the visitor decides whether to act,
not filed away on a separate page.

**Audit checklist:**
- Is at least one real authority signal visible in the same eyeline as
  the primary ask?
- Can every authority signal on the page survive a visitor actually
  checking it?
- Are there any badges or seals on the page that are decorative rather
  than verifiable?
- Is the founder's or business's real, relevant background surfaced
  near the decision point rather than buried?

═══════════════════════════════════════════════════════════════
5. SMART DEFAULTS — the pre-selected option is a decision made for them
═══════════════════════════════════════════════════════════════

**The principle.** Most people keep whatever is already selected for
them. A default is never neutral — it's a decision the builder made on
the visitor's behalf, dressed up as the visitor simply not having
changed anything.

**Where sites break it.** A default gets set to whatever benefits the
business most in the moment — a pre-ticked upsell, a pre-selected
higher tier, a pre-checked box that opts someone into marketing
contact they never asked for — rather than whatever the business
would honestly recommend to a friend standing in the visitor's shoes.

**The practice.** Every pre-selected option on the site has to survive
one test: is this the choice you would honestly tell a friend to
make? If it isn't, it doesn't get to be the default, regardless of
what it does for a conversion number.

**Audit checklist:**
- List every pre-selected or pre-checked option on the site.
- For each one: would you tell a friend in the visitor's position to
  keep it as-is?
- Are there any pre-ticked boxes that add cost or opt into anything
  the visitor didn't explicitly choose?
- Does changing or unchecking a default take more effort than leaving
  it — and if so, why?

═══════════════════════════════════════════════════════════════
6. THE DECOY EFFECT — value is judged by comparison
═══════════════════════════════════════════════════════════════

**The principle.** People rarely judge an option's worth in isolation;
they judge it against whatever else is sitting next to it. Given three
prices, most visitors don't calculate value from scratch — they pick
whichever one looks like the best deal relative to its neighbors. That
makes the arrangement of a pricing or tier table a design decision in
its own right, not a neutral list.

**Where sites break it.** Tiers get listed in whatever order they were
built, with no thought to what each one makes the others look like —
or a deliberately crippled "decoy" tier gets planted purely to make
another option look better by comparison, obviously enough that a
sharp visitor spots the trick and starts distrusting the rest of the
page along with it.

**The practice.** Arrange tiers so the option you'd genuinely
recommend most people take is also the one whose value is easiest to
see next to its real neighbors — because the comparison is honest, not
because a strawman was placed beside it. *(This overlaps offer-stack
architecture; fold in a cross-reference to dr-canon once that file
stands up.)*

**Audit checklist:**
- Are tiers ordered and priced on purpose, with a specific tier meant
  to read as the obvious best value?
- Does the recommended tier's advantage come from real differences in
  what's included, not an artificially crippled neighbor?
- Would a sharp, skeptical visitor comparing all tiers side-by-side
  feel informed rather than steered?
- Is there any tier on the page that exists for no reason other than
  making another tier look better?

═══════════════════════════════════════════════════════════════
7. THE PRATFALL EFFECT — a visible flaw makes everything else believable
═══════════════════════════════════════════════════════════════

**The principle.** A source that presents as flawless reads to the
brain as unreal, and unreal keeps the guard up. A credible, minor,
honestly-stated imperfection does the opposite — it signals that
nothing here is staged, which makes every other claim on the page
easier to believe.

**Where sites break it.** Every review is five stars, every case study
is an unqualified win, and the pricing page never says who the product
is actually wrong for. The page reads as curated rather than honest,
and a skeptical visitor's guard never comes down.

**The practice.** Show the real review average, threes and fours
included, not a filtered highlight reel. State an actual limitation
somewhere visible. Put "who this isn't for" on the pricing or offer
page as a genuine disqualifier, not a humble-brag dressed as one.
*(The disqualification move is also a direct-response technique; fold
in a cross-reference to dr-canon once that file stands up.)*

**Audit checklist:**
- Is at least one honestly-stated limitation visible somewhere on the
  page?
- Does the review presentation include anything less than a perfect
  score, or does it read as filtered?
- Is there a stated "who this is not for" on the pricing or offer
  surface?
- If a critical review or a mistake is shown, is how it was handled
  shown alongside it?

═══════════════════════════════════════════════════════════════
RUNNING THE AUDIT
═══════════════════════════════════════════════════════════════

Run all seven checklists as a single pass against any live page, in
the order they're written above — which is also, roughly, the order a
visitor's own brain moves through them: comfort (Jakob's Law), action
(Fitts's Law), safety (social proof), deference (authority), momentum
(smart defaults), decision (the decoy effect), belief (the pratfall
effect).

A page that "feels off" for no describable reason is usually one or
more of these seven violated invisibly — the visitor can't name why,
but their brain can feel it. A page that "feels right" is usually all
seven quietly aligned at once. Running the checklist above is how to
find out which is true before a visitor has to.

═══════════════════════════════════════════════════════════════
END OF DOCUMENT
═══════════════════════════════════════════════════════════════
