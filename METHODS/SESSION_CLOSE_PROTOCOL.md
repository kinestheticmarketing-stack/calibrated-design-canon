# SESSION_CLOSE_PROTOCOL.md

*The mechanism that turns "paperwork closes every session" from 
a rule into an executed checklist. Applied by the Architect at 
every session close, without needing to be reminded of specific 
items.*

═══════════════════════════════════════════════════════════════
PURPOSE
═══════════════════════════════════════════════════════════════

The Director's userPreferences require paperwork at every session
close. Historically, this discipline has been fragile — sessions
end without paperwork when the Director gets pulled away, when 
rate limits hit, when sessions run long enough that the close 
isn't obvious. Even when close paperwork runs, items added mid-
session (new canon docs, new ROADMAP entries, new userPreferences 
subsections, new memory edits) frequently get forgotten because 
the Director has to remember them by name.

This protocol closes that gap. When the Director signals close,
the Architect runs the full checklist below. Nothing gets 
forgotten. Nothing requires the Director to remember specific 
items from earlier in the session.

═══════════════════════════════════════════════════════════════
CLOSE TRIGGERS
═══════════════════════════════════════════════════════════════

Any of these mean "run the close protocol now":

- Director says "close it out," "session's done," "let's do 
  the paperwork," or equivalent
- Director says "I'm done" or explicitly indicates end of 
  session
- Kickoff work has landed and Director hasn't opened a new 
  topic within roughly 15-20 minutes
- Rate-limit windows approaching exhaustion (5-hour window 
  above 85% used, or weekly window above 90% used)
- Session hits a natural phase boundary (feature shipped, 
  canon doc committed, project milestone reached) and no new 
  work is pending

The Architect proactively initiates close paperwork when 
triggers fire. Does not wait for the Director to explicitly 
request it. Does not ask permission first.

═══════════════════════════════════════════════════════════════
CLOSE CHECKLIST — ALWAYS RUN, EVERY SESSION
═══════════════════════════════════════════════════════════════

The Architect runs every item on this checklist. Any item that
doesn't apply to the current session gets an explicit "N/A this 
session" — never silently skipped.

## 1. Canon repo state review

- List all commits made during this session with hashes and 
  one-line descriptions
- Confirm all commits pushed to correct remote
- Confirm working tree clean on the correct branch
- If any dirty files remain, identify what they are and where 
  they belong

## 2. ROADMAP.md verification

- List any items added to IN-PROGRESS CANON this session
- List any items moved from IN-PROGRESS to SHIPPED CANON this 
  session
- Confirm entries landed in correct subsections
- Confirm SEQUENCING RATIONALE items added if new priority 
  ordering was locked
- Flag any items surfaced during the session but NOT yet added 
  to ROADMAP — either add them now or explicitly defer with 
  reason

## 3. Canon docs shipped this session

- List every new canon doc created this session with byte 
  count and path
- Confirm each is indexed in README.md
- Confirm each is referenced in ROADMAP.md as shipped (not 
  still listed as in-progress)

## 4. Project canon updates (per-project)

For each project touched this session:

- STATE_OF_PROJECT.md updated with what shipped this session
- PROJECT_LESSONS.md appended if a lesson surfaced worth 
  canonizing
- Any project-specific canon doc updates
- Git commit with clear message

## 5. userPreferences additions

- List any new subsections or rules added to userPreferences 
  this session
- Confirm they're saved (the Director's action, but the 
  Architect confirms the additions in chat so nothing is lost)
- Note if any rules surfaced that SHOULD go in userPreferences 
  but haven't been added yet

## 6. Memory edits made

- List every memory_user_edits action taken this session (add, 
  remove, replace)
- Confirm they landed correctly

## 7. External validations filed

- Note any external research, papers, open-source patterns, 
  or third-party sources referenced this session that should 
  be filed in EXTERNAL_VALIDATION.md
- Add them if not already, or explicitly defer with reason

## 8. Cross-chat handoffs

- List any handoff documents produced for other Architect 
  chats this session
- Confirm each is complete and pasteable
- Note if any expected handoffs are still pending

## 9. Insights surfaced but not yet actioned

- List any conceptual insights, methodology observations, or 
  strategic ideas surfaced this session that haven't yet been 
  captured in canon
- For each, either action now (add to appropriate doc) or 
  explicitly defer with reason and file location for later 
  pickup

## 10. Open loops requiring Director attention

- List anything that needs Director action outside this chat 
  (buy something, sign up for something, decide something, 
  paste something into another chat)
- List anything that will resurface in future sessions 
  requiring Director memory

═══════════════════════════════════════════════════════════════
OUTPUT FORMAT
═══════════════════════════════════════════════════════════════

The Architect produces the close paperwork as a single 
structured message. Sections match the checklist above. 
Items that don't apply get "N/A this session." Nothing gets 
silently skipped.

The Director reviews the paperwork. If anything is missing 
or wrong, Director says so and the Architect corrects.

═══════════════════════════════════════════════════════════════
WHAT GOES IN THE CLOSE MESSAGE
═══════════════════════════════════════════════════════════════

The close message is comprehensive but scannable. Purpose: the
Director sees at a glance what shipped, what's queued, what 
needs their attention, and what's carrying over.

Format template:

```
SESSION CLOSE — [date]

## Commits this session
[list with hashes]

## Canon docs shipped
[list with paths and byte counts]

## ROADMAP updates
[additions, promotions, deferred items]

## Project canon updates
[per project]

## userPreferences additions
[new rules]

## Memory edits
[actions taken]

## External validations
[filed or deferred]

## Handoffs produced
[list]

## Insights surfaced but not actioned
[list with defer rationale]

## Open loops for Director
[list]

## Carrying over to next session
[explicit list, or "nothing"]
```

═══════════════════════════════════════════════════════════════
FAILURE MODES THIS PREVENTS
═══════════════════════════════════════════════════════════════

## Forgotten additions

Session-close paperwork historically only covered what the 
Director explicitly remembered. New canon docs added mid-session 
frequently got forgotten. The checklist requires the Architect 
to enumerate them regardless of Director memory.

## Silent branch drift

Canon repo can drift into inconsistent state across branches 
if commits land on the wrong branch and nobody notices. The 
canon repo state review catches this at every close.

## Uncanonized insights

Real insights surface mid-session that never make it into canon 
because the conversation moves on. The "insights surfaced but 
not actioned" checklist requires either action or explicit 
defer with file location.

## Dropped handoffs

Handoffs to other Architect chats can get forgotten if the 
session ends abruptly. The checklist requires enumeration.

## Rate-limit-triggered abrupt endings

Sessions ending because rate limits hit historically produced 
zero paperwork. The trigger list requires close paperwork to 
run BEFORE the limit hits, not after.

═══════════════════════════════════════════════════════════════
WHAT THIS DOES NOT DO
═══════════════════════════════════════════════════════════════

This protocol does not automate the close paperwork itself.
The Architect still produces the close message manually. The
protocol standardizes WHAT gets included, not who produces it.

Full automation (a scheduled agent that runs close paperwork 
without human intervention) is a future canon addition — see 
NEWSLETTER agent pipeline and future automation work. This 
protocol is the prerequisite discipline that makes future 
automation possible: automation reads structured artifacts, 
and this protocol produces the structured artifacts.

═══════════════════════════════════════════════════════════════
END OF DOCUMENT
═══════════════════════════════════════════════════════════════
