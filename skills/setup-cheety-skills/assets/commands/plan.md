---
description: Produce an implementation plan for an issue and file it on the ticket — no code
---

Use the skill `make-plan`. Read AGENTS.md first.

Issue: $ARGUMENTS

Write **no code** — not before the confirmation and not after it. Deliver only
the plan, with every section the skill names. Mark uncertain assumptions
explicitly. With more than two uncertain assumptions: abort and ask.

Once the plan is confirmed, append it to the issue as a comment headed
`## Umsetzungsplan (bestätigt)`, verbatim, then **stop** and name the next
command: `/implement $ARGUMENTS`. Do not start implementing in this session.

If no forge CLI is available, output the comment ready to paste and say that it
still has to be pasted.

**The plan is written in German** — see AGENTS.md, "Language".
