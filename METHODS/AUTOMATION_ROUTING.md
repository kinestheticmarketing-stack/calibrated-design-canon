# Automation Routing — Deterministic Before Agentic

Status: canon method. Adopted 2026-09-21 by Director.
Source: distilled from Nate Herk, "Codex beginner to pro" course (2026), chapters on scheduled tasks and Trigger.dev hosting. Adapted to the Calibrated Stack VPS.

## The rule
Every automation is placed on the LOWEST rung of the ladder that its job permits. Moving up a rung requires a stated reason: a step whose count, order, or tool choice cannot be known in advance.

## The ladder
Rung 0 — Deterministic script. Fixed inputs, fixed steps, fixed outputs. No model call. Example: a form posts, a notification with placeholders goes to a hard-coded destination.
Rung 1 — Deterministic script with bounded AI steps. The pipeline order is fixed; one or more steps call a model once for a judgment task (summarize, draft, classify). The model never chooses destinations, tools, or whether a step runs.
Rung 2 — Full agent loop. The agent decides how many times to research, which tools to call, and when it is done. Reserved for jobs where the path is genuinely unknown until it is walked.

Test for any automation: "If I drew this as boxes and arrows, does the same drawing hold every run?" Yes = Rung 0 or 1. No = Rung 2.

## Why
- Drift. An agent re-interprets its instruction every run. The source reported a scheduled agent routine that, after about a month, began posting to wrong channels. Rebuilt as a script with hard-coded channel and message IDs, it cannot drift.
- Cost. A scheduled task inside an agent chat surface spends subscription or API budget on every run, including runs that need no judgment.
- Verifiability. Rung 0-1 outputs are checkable against fixed expectations. Rung 2 outputs need a judge.

## Build requirements (all rungs)
1. Destinations are hard-coded in code: channel IDs, recipient addresses, file paths, endpoints. No agent ever selects a destination.
2. Secrets live in environment files outside source control, never in the repo, never in chat.
3. Idempotency guard: a run that would duplicate an already-delivered output skips and logs why.
4. Kill switch: an ENABLED env flag, default false. It flips true only after a hosted proof run delivers correctly to the real destination.
5. Hosted proof before enable: the job is proven on the machine it will run on, not only locally. Verify at the real destination, not by the job's own exit status.
6. Cost ceiling per run on any rung with model calls, enforced in code.

## Hosting
- Rung 0-1 jobs run on the VPS as scripts under systemd timers or cron, logging to a known path. No third-party scheduler is required; the VPS already provides this.
- Rung 2 jobs run where the agent harness runs. Prefer a subscription-backed surface for low-volume jobs; move to API-billed hosting only when volume or programmatic triggering requires it.
- Chat-surface scheduled tasks are for Rung 2 work only. A Rung 0-1 job found running as a chat scheduled task is migrated to the VPS.

## Relationship to AGENT_ARCHITECTURE
Each project's AGENT_ARCHITECTURE.md carries a specialist rung table classifying every specialist under this ladder. A specialist's rung changes only with a stated reason recorded in that table.
