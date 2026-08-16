# AGENTS.md

**This repository ships an engineering harness. It does not use one.**

Everything the harness consists of lives in exactly one place, because `npx
skills` installs skill directories and cannot reach outside them:

> **`skills/setup-cheety-skills/assets/`**

Its `AGENTS.md` is the canonical rule set. There is deliberately no second copy
at the root — a second copy drifts, and an earlier version of this repository
proved it within a day.

## Working on this repository

| Task | Command |
|---|---|
| Are all skills discoverable? | `python3 scripts/skills_check.py .` |
| What will users see? | `npx skills@latest add ./ --list` |
| Do the rules still hold? | `python3 skills/setup-cheety-skills/assets/tools/arch-check/eval.py --profile laravel --fixtures skills/setup-cheety-skills/assets/stacks/laravel/fixtures` |
| Does an install work end to end? | `node skills/setup-cheety-skills/install.mjs --stack python --target /tmp/probe` |

## Editing rules

- Change a rule → change its fixture in the same commit. A rule without a
  false-positive fixture is not finished.
- Change a `description:` → keep it valid YAML. An unquoted colon makes the CLI
  skip the skill **silently**; it simply stops appearing in `--list`.

## Language

Code, tools, profiles, fixtures, rules, skills and documentation are **English**.
`README.md`, `INSTALL.md`, issues, pull-request text, review comments and commit
subjects are **German**.

## Commit Messages

Do not add a `Co-Authored-By` trailer, a `Claude-Session` line, or any Claude /
Claude Code session link (e.g. `claude.ai` / `claude.com` URLs) to commit
messages.
