---
description: Split a specification into milestones and the first milestone's issues
---

Use the skill `split-spec`. Read AGENTS.md first, section 2.6.

Specification: $ARGUMENTS

Produce the milestone plan under `docs/roadmap/`, then check it:

```bash
python3 tools/skill-eval/roadmap_check.py docs/roadmap
```

Write issues for the **first** milestone only. The remaining milestones stay as
backlog rows — issues written against a codebase that does not exist yet anchor
on invented paths.

**Roadmap and issues are written in German** — see AGENTS.md, "Language".
