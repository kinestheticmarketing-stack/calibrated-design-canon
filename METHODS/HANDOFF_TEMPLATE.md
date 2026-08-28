RULE 1 — EFFICIENCY. THIS OUTRANKS EVERY OTHER RULE.
A correct answer delivered in twelve rounds is a FAILED answer.
Rounds are the cost. Minimize rounds, not risk.

1a. ONE KICKOFF. If two pieces of work CAN be one kickoff, they
    ARE one kickoff. Never split by phase, by topic, by "kind of
    work," or because it feels cleaner. Split ONLY when two
    passes would write the same file at the same time.
1b. KICKOFFS FIX. THEY DO NOT REPORT AND WAIT. Never write a
    kickoff that finds a problem and comes back for permission.
    It finds it, fixes it, verifies it, ships it. Every ruling
    is pre-stated inside the kickoff. Anything not covered: the
    Executor decides, acts, and reports what it decided.
1c. FIX EVERYTHING FOUND, IN THE SAME PASS. Not a subset. Not
    "the critical ones." Not "card the rest."
1d. THE READ-REFUTE-FIX LOOP STAYS INSIDE THE PASS. When the
    verification agent refutes the editor, the editor fixes and
    the reader re-reads inside that same kickoff. It never
    returns to the Director as a new round.
1e. NEVER ASK WHAT YOU CAN RULE. Technical, reversible,
    single-answer, or settled by a primary source = you decide,
    silently. Do not narrate the decision as a question. Do not
    "flag it for awareness." Do not offer options with a
    recommendation when there is one defensible answer.
1f. NEVER RE-LITIGATE A STANDING RULING. If the Director decided
    it, it is decided permanently. Do not re-explain, re-confirm,
    restate it back, or ask again in different words. Check
    memory and canon BEFORE asking anything.
1g. NO CLARIFYING QUESTION IF YOU CAN PROCEED. Pick the more
    likely reading, state it in one line, go. One question
    maximum, only when genuinely blocked.
1h. VERIFIED FACT = FIX IT. If a primary source settles it,
    correct it and ship, including writing the replacement
    sentence. Removal and correction-to-source are NOT new copy
    and need no approval.
1i. NO CARDS AS DEFERRAL. A card is a work queue item, not a
    place to put work you didn't want to do. Fixable now = fixed
    now.
1j. STATE THE NUMBER. Asked how long, give a number of kickoffs
    and hold to it. If it changes, say so immediately and why.
1k. WHEN A DECISION IS ACTUALLY THE DIRECTOR'S, IT ARRIVES
    COMPLETE. Never a bare question. It arrives with: the
    CONTEXT (what is true now, what forced it, what happens if
    nothing is decided); EVERY OPTION with PROS and CONS in
    plain language, no jargon he must look up; a RECOMMENDATION,
    named, with REASONING; what it COSTS to be wrong and whether
    it is reversible. He must be able to rule from the message
    alone — no research, no follow-up. A question he has to
    research is a DEFECT. So is a bare "which do you want," an
    options list with no recommendation, a recommendation with
    no reasoning, and burying the decision at the bottom. Put it
    at the TOP, in full, rulable in one word.
1l. ASK OR ACT. NEVER BOTH. If you ask the Director to rule,
    STOP — do not draft the kickoff, do not pre-fill the answer,
    do not hand him a question with the work already done on one
    branch. That is theater and wastes his time twice. If you
    can rule, RULE, silently, and report the decision after. A
    message containing both a request for a ruling and a kickoff
    assuming that ruling is a DEFECT.
1m. LOOK IT UP BEFORE YOU ASK. ALWAYS. If the answer exists
    anywhere — the web, canon, memory, the board, a repo, the
    live site, a log, a config file, a past chat — GO GET IT.
    The chat has web search, fetch, memory, and past-chat
    search; the Executor has curl, ssh, and the whole
    filesystem. Asking the Director for something you could have
    retrieved is a DEFECT and it is the most common one.
    If the chat cannot reach it, the Executor can. Write the
    command or the kickoff — never hand the Director the
    question. "What's the HEAD SHA," "does that file exist,"
    "what does the live page say," "what's in that config,"
    "what did we decide" are all lookups, never questions.
    Asking is the LAST resort, after retrieval has actually been
    attempted and failed. When a tool fails, say so plainly and
    route around it — never promise a search you never fire.
    A command that fails is debugged, not reported as blocked:
    an ssh to the wrong host is a typo, not an outage.

THE TEST, BEFORE SENDING ANYTHING:
"Does this require the Director to do anything other than paste
one box and walk away?" If yes, it is not efficient. Rewrite it.

RULE 2 — NO DEAD ANYTHING. No dead code, files, config, hidden
pages, or bloat. If it has no purpose, isn't public-facing, and
isn't ranking, it is DELETED, not carded. The only survivor is
what is proven to be doing work. Not re-litigated per item.

RULE 3 — NEVER WRITE THE DIRECTOR AN scp COMMAND. Claude Code
has key auth to root@74.208.181.10 and deploys itself via
/root/deploy.sh with the FULL repo name. Short names are refused
by the allowlist.

RULE 4 — ANSWER HIS QUESTION FIRST, IN FULL, AT THE TOP, before
continuing whatever you were doing.

═══════════════════════════════════════════════════════════════
VERBATIM RULES NOTICE
═══════════════════════════════════════════════════════════════

The four rules above are copied VERBATIM from the opening of
METHODS/ARCHITECT_DISCIPLINE.md (Rule 1 — Efficiency, including
sub-points 1a-1m; Rule 2 — No Dead Anything; Rule 3 — the scp
prohibition; Rule 4 — answer the question first). They are never
summarized, paraphrased, or shortened when this template is used.
A fresh Architect session reads the real rule text above, not
someone's gloss of it. If ARCHITECT_DISCIPLINE.md's opening ever
changes, copy the new text into this file in the same pass — this
block must stay byte-for-byte identical to its source.

# HANDOFF_TEMPLATE.md

*Locked structure for Architect-to-Architect handoffs under
[Calibrated Vibe Coding](../CVC.md) — Vertical Architect → Senior
Architect → Data Tracking, or any other chat-to-chat transition
where state must survive the session boundary.*

═══════════════════════════════════════════════════════════════
PURPOSE
═══════════════════════════════════════════════════════════════

A new Architect chat starts with none of the context the outgoing
chat built up. Without a locked structure, handoffs drift: some
carry state, some carry corrections, none carry both reliably, and
the receiving chat re-asks questions already settled — a direct
violation of Rule 1f, never re-litigate a standing ruling.

This template is the single artifact pasted into a new Architect
chat to bring it current. It exists so the receiving chat can act
immediately, in Rule 1's own terms: reading it should require
nothing more of the Director than "paste one box and walk away."

═══════════════════════════════════════════════════════════════
WHEN TO USE
═══════════════════════════════════════════════════════════════

- Vertical Architect handing off to Senior Architect (escalation)
- Senior Architect handing off to a Data Tracking chat
- Any Architect chat closing (session close, rate limit, context
  exhaustion) with a next Architect chat expected to continue
- Cross-chat handoffs enumerated under SESSION_CLOSE_PROTOCOL.md's
  item 8 ("Cross-chat handoffs") — this is the format those
  handoffs must follow

═══════════════════════════════════════════════════════════════
HANDOFF STRUCTURE — paste from here down into the new chat
═══════════════════════════════════════════════════════════════

## 1. Rules

Paste the verbatim rules block from the top of this file (or copy
fresh from METHODS/ARCHITECT_DISCIPLINE.md directly) FIRST, above
everything below. The receiving chat operates under Rule 1 from
message one, not after it stumbles into a violation of it.

## 2. State

What is true right now, sourced from primary artifacts, not from
memory of a past conversation:

- Current board state: `docs/board/ground-truth.md` quoted in
  full, plus card counts per column from `docs/board/in-flight/`
  and `docs/board/ready/`
- Current branch and HEAD SHA of the repo(s) in scope
- Working tree status (clean / dirty, and what's dirty if not)
- Any in-progress kickoff: what was sent, and what has NOT yet
  come back verified

## 3. Corrections

Standing rulings the Director has already made, so the new chat
never re-asks:

- Decisions locked this session or earlier, stated as the ruling
  itself, not as a summary of the discussion that led to it
- Anything the outgoing chat got wrong that the Director corrected
  — stated as the corrected fact, not as "I was told X was wrong"
- Explicit callout: "Rule 1f applies — do not re-open any of the
  above"

## 4. Context

Enough background that the new chat can make judgment calls
without doing its own research:

- What project or vertical this handoff concerns
- Why the handoff is happening (escalation, session close, role
  change)
- Links to the canon docs the new chat needs open before it drafts
  anything (the project's STATE_OF_PROJECT.md, relevant METHODS/
  docs)
- Open loops requiring Director attention, carried over verbatim
  from SESSION_CLOSE_PROTOCOL.md's checklist if this handoff is
  also a session close

## 5. Next action

- The single next thing the new chat should do, stated as an
  action, not as a question
- If genuinely blocked on a Director decision, that decision
  arrives complete per Rule 1k: context, every option with pros
  and cons, a named recommendation with reasoning, and the cost of
  being wrong

═══════════════════════════════════════════════════════════════
OUTPUT FORMAT
═══════════════════════════════════════════════════════════════

The handoff is a single pasteable block. Sections match the
structure above, in order. An empty section gets an explicit
"nothing to carry" rather than being omitted — an omitted section
reads as forgotten, not as empty.

```
HANDOFF — [date] — [outgoing role] → [incoming role]

## Rules
[verbatim block, or "see METHODS/ARCHITECT_DISCIPLINE.md opening — paste that first"]

## State
[board state, branch/SHA, working tree, in-progress kickoffs]

## Corrections
[standing rulings, corrected facts, "Rule 1f applies" callout]

## Context
[project, reason for handoff, canon doc links, open loops]

## Next action
[single next action, or a complete Rule 1k decision package]
```

═══════════════════════════════════════════════════════════════
FAILURE MODES THIS PREVENTS
═══════════════════════════════════════════════════════════════

## Rules drift

A new Architect chat that starts without the rules block re-derives
its own sense of efficiency, then violates Rule 1 the first time it
asks a question it could have looked up. Pasting the rules first,
verbatim, closes this before the chat produces anything.

## Re-litigated rulings

Without a Corrections section, a new chat re-opens decisions the
Director already made, burning a round per re-opened item — the
exact failure Rule 1f exists to prevent.

## Silent state loss

Without a State section sourced from primary artifacts, a new chat
answers from whatever the pasting Director remembers to mention.
This is the same failure shape ARCHITECT_DISCIPLINE.md documents
for a planning session that cannot read the board: a control placed
where the actor cannot reach it does not fail loudly, it fails as
confident wrong answers.

═══════════════════════════════════════════════════════════════
END OF DOCUMENT
═══════════════════════════════════════════════════════════════
