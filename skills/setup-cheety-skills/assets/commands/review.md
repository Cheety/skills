---
description: Review a diff or PR
---

Use the skill `code-review`. Read AGENTS.md first.

To review: $ARGUMENTS
If empty: `git diff main...HEAD`

Work through the skill's checklist in order. Group the result as
werkzeug / blocker / frage / vorschlag / scope, with file and line.
**Review comments are written in German.**

Do not comment on anything the formatter, type checker or principle checker
handles. Close by noting that this is a preliminary pass and does not replace
human approval.
