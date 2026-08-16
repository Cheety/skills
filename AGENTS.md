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
| Do the roadmap rules still hold? | `python3 skills/setup-cheety-skills/assets/tools/skill-eval/roadmap_check.py --self-test` |
| Does an install work end to end? | `node skills/setup-cheety-skills/install.mjs --stack python --target /tmp/probe` |

## Editing rules

- Change a rule → change its fixture in the same commit. A rule without a
  false-positive fixture is not finished.
- Change a `description:` → keep it valid YAML. An unquoted colon makes the CLI
  skip the skill **silently**; it simply stops appearing in `--list`.

## Working style

- **Read before writing.** An existing file is read before it is changed. No
  re-reading as long as nothing has changed.
- **Thorough in thinking, brief in output.** The analysis may be long, the answer
  must not be.
- Files above 100 KB are skipped unless they are genuinely needed.
- No flattering openers, no closing small talk. No praise for the question.
- **Do not guess.** APIs, versions, flags, commit SHAs and package names are
  backed by reading code or docs before they are claimed. A plausible invention
  costs more than a look at `package.json`, a `SKILL.md` frontmatter block or the
  script itself under `scripts/` or `skills/setup-cheety-skills/assets/tools/`.

## Comments

The code says *what* it does. Comments say *why*. They are needed for domain
logic, complex algorithms, workarounds for foreign bugs and deliberately
unidiomatic passages. Comments are written **at the same time** as the code or
the refactoring, not afterwards.

- **Explain intent and context.** The overarching reason for a decision belongs
  in the file, especially where the implementation looks wrong at first glance.
  The rule checker is full of such places: a rule that matches raw source instead
  of stripped source says why in one line.
- **Document workarounds.** Anyone steering around an obscure bug, a forge
  quirk or a limit of a foreign library writes down why exactly these lines
  exist. Otherwise the next refactoring optimises them away by accident.
- **No redundancy.** `# increment i` is not a comment, it is noise.
- **Do not comment bad code, decompose it.** If a block is too complicated to be
  readable without an explanation, it first belongs in smaller, named functions.

Docstrings are explicitly wanted and do **not** count as comments in the sense of
this rule: Python docstrings on modules, classes and functions, JSDoc on the
installer's exported functions. The stack profiles state the equivalent for the
code they generate (PHPDoc in PHP, TSDoc in TypeScript).

## Language

**The instruction is English. The artifact is German.**

Code, tools, profiles, fixtures, rules, skills and documentation are **English**
— including every `SKILL.md`, whatever language the output it describes is in.
`README.md`, `INSTALL.md`, issues, milestone plans, implementation plans,
pull-request text, review comments and commit subjects are **German**.

A skill that produces a German artifact says so in one line under its title and
shows its examples in German. The canonical wording of the rule lives in
`skills/setup-cheety-skills/assets/AGENTS.md` § 0.

### Form (all files)

- **Identifiers and comments are English**, in every file. Prose meant for the
  team stays German where the table above says so: commit subjects are German
  behind the fixed English prefixes `Test:`, `Impl:`, `Fix:`, `Doku:`. The line
  runs along the kind of text, not along the taste of the session.
- **No em dashes and no emojis**, in no file: not in code, not in comments, not
  in documentation, not in commit messages. The replacement is a plain hyphen
  with spaces, a comma, a colon or a rewritten sentence.

## Commit Messages

Do not add a `Co-Authored-By` trailer, a `Claude-Session` line, or any Claude /
Claude Code session link (e.g. `claude.ai` / `claude.com` URLs) to commit
messages.
