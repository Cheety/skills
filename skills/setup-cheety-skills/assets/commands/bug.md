---
description: Fix a bug — reproduce, failing test, then fix
---

Use the skill `fix-bug`. Read AGENTS.md first.

Bug description: $ARGUMENTS

Keep the order: reproduce, locate the cause, write a failing test, commit that
test alone, then fix. Do not start with the fix.

Ask "why" twice before assuming a cause. If you cannot explain how the faulty
state arises, you have not found the cause.
