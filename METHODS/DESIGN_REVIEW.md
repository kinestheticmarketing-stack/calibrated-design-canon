# Design Review

Standing checklist for any page or site before launch or redesign:
portfolio properties, the agency site, and client builds.
Distilled 2026-09-27 from a Director-screened set of six web-design
video transcripts. Paraphrased heuristics only; nothing here is a
citable statistic.

## 1. Five-question homepage audit
1. What is the page's one job? Every CTA serves that single decision.
   Many CTAs are fine; many competing asks are not.
2. Does the first scroll answer: where am I, what do I get, why
   should I care? And does it put the next step there with the least
   friction? For lead-gen, the default is the form inside the hero.
3. Cover the design and read only the words. Does the offer still
   land? If not, the copy is the bottleneck, not the visuals.
4. Could three elements come out of any section without losing
   meaning? If yes, the section is fighting itself.
5. Is it fast, findable (search and AI answers), and maintained as a
   system rather than a finished project?

## 2. Scoring rubric (1–5 each, 15 total)
- Point of view: does it have an identity, or could a competitor's
  logo be swapped in?
- Consistency: do type, spacing, color, components and motion read as
  one system?
- Execution: did anyone make a thoughtful decision about how the
  page works, or were sections just arranged?

## 3. Review order
Offer → proof → assets → effects (gradients, video, motion) →
boring corners (mobile, forms, links, dates, confirmation pages).
A polished page cannot compensate for a form that does not submit.

## 4. Tests
- Swap-the-logo (assets): if an image would look at home on a
  competitor's page, it is not identifying the business. Replace the
  most visible stock first. One custom explanatory diagram beats many
  decorative illustrations.
- Mute-and-remove (video): mute it and ask what information is lost;
  then remove it and ask whether the page got clearer or faster.
  Video must earn its way back in.
- Gradient restraint: if a visitor's first reaction is to the effect
  itself, it is too much.
- Duplicate blocks: no body link block rendered twice on one page.
  Footer navigation is exempt.
- Neglect signals: a stale year, dated claims, broken interactions or
  outdated examples read as an abandoned business. Forms are proven
  end-to-end on a schedule, not assumed.
  'Last updated' publishes the last visible-text change date; 'Last
  reviewed' is never derived.
- Accessibility: WCAG 2.1 AA baseline. Zero serious or critical axe
  violations; AA contrast (4.5:1 body text, 3:1 large text);
  literal alt text; visible keyboard focus; a skip link.
  Run axe at 375px AND 1280px; a single viewport misses overflow-only
  violations. Keyboard checks use sequential Tab; .focus() cannot reach
  visibility:hidden elements and false-fails.
- Long-copy section: when a section reads as one block, split it into its smallest units, group the units by subject, and give each group its own element. Group headings come from the approved copy or go through copy approval; layout never invents them. Do not lower body-text contrast to create hierarchy.

## 5. Directing AI builds
- State one organizing concept before any build. "Make it premium"
  or "make it modern" is not a direction; the model defaults to the
  average of everything it has seen.
- Give one coherent reference set. Many unrelated references produce
  a patchwork of borrowed pieces.
- Prefer an interactive element that solves the visitor's actual
  problem on the page over a section that describes a feature.
  Calculators are this pattern.

## 6. Portfolio constraints (rank-and-rent properties)
- Product-not-people ruling applies: no real-people imagery, no
  stock "team" photos. Those imply a team the site cannot back.
  Point of view comes from assets, diagrams, tools and copy instead.
- Confident statement H1s, not questions. Question-form H2s remain
  a deliberate GEO choice and are unaffected.
- No unsourced superlatives in any H1 or body line.

## 7. Client projects (done-for-you work)
- Intake before any build: "List three websites you like and why"
  and "What sections or features do you want on the homepage, and
  what does the wider site need?"
- Collect every asset (copy, imagery, brand files) before opening the
  editor. Never build on existing-site content without confirming it
  is current.
- Build the homepage first, get sign-off, and lock it as the style
  guide the rest of the site inherits. Cap revision rounds in the
  contract.

## 8. Do not cite
- "Every 1-second delay costs ~7% of conversions": no current
  primary source.
- Universal Analytics-era bounce-rate definitions and benchmarks.
  GA4 defines bounce as non-engaged sessions.
- Agency self-reported lift numbers: anecdote, not evidence.
