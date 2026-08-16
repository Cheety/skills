---
description: Produce an implementation plan for an issue and hand it off on the ticket
---

Use the skill `make-plan`. Read AGENTS.md first.

Issue: $ARGUMENTS

Deliver the plan with every section the skill names, and mark uncertain
assumptions. With more than two uncertain assumptions: abort and ask.

Once a human confirms it, the plan goes onto the ticket as a comment headed
`## Umsetzungsplan (bestätigt)` and this session ends there — the hand-off, not
the build. Name `/implement $ARGUMENTS` as the next command.

**The plan is written in German** — see AGENTS.md, "Language".
