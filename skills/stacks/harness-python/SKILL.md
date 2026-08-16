---
name: harness-python
description: The Python stack profile for the engineering harness — how the eight principles map onto actions, dataclasses, queue handlers and migrations, and which 20 rules the checker enforces. Use this skill when working in a Python repository that has the harness installed, when writing or reviewing Python against the principles, or when a rule with a BOUNDARY_, STATE_, ERROR_ or MIGRATION_ prefix fires and you need to know what it means.
---

# Python profile

Concretises `AGENTS.md` for this stack. Where the two disagree, this file wins.

## Layers

| Principle BOUNDARIES | Directory |
|---|---|
| Domain | `src/actions`, `src/domain`, `src/types` |
| Edge | `src/http`, `src/jobs`, `src/cli` |
| Persistence | `src/db`, `src/db/migrations` |

`src/actions` imports neither a web framework nor a database driver.
`src/domain` knows neither outer layer.

## Idioms

**Action** — a module-level `execute(...)` function. Dependencies as
parameters, not imported. No global client objects.

**State** — a transition table plus a guard function that raises on an unknown
state instead of returning `False`. A typo in a status must not be
indistinguishable from a business rule.

**DTO** — `@dataclass(frozen=True)`. Types in `src/types/`.

**Money** — integer in cents, name ending in `_cent`. `amount: float` is a
finding.

**Job** — `handle(...)` or `process(...)` with an idempotency check before any
side effect.

**Errors** — no bare `except:`, no `except X: pass`. Expected domain failures are
named exceptions, not `None` returns.

**Migration** — `up()` adds, `down()` removes. `nullable=True` or a default on
every new column, `typ="timestamptz"` for timestamps, no bulk update inside the
migration.

## Check chain

```bash
ruff format --check .
ruff check .
mypy src
python3 tools/arch-check/arch_check.py . --profile python
python3 tools/arch-check/eval.py --profile python
pytest
```

## Enforced automatically — 20 rules

`HYGIENE` DEBUG_OUTPUT · TYPE_IGNORE · ENV_OUTSIDE_CONFIG
`BOUNDARIES` ACTION_HTTP · ACTION_DB · DOMAIN_PURE
`STATE` MUTABLE_DEFAULT · MONEY_FLOAT
`ERRORS` BARE_EXCEPT · SWALLOWED · `IMMUTABILITY` DTO
`IDEMPOTENCY` HANDLER · `TRANSACTION` SIDE_EFFECT
`MIGRATION` RENAME · DROP · NOT_NULL · TIMEZONE · BULK_UPDATE · DOWN
`TESTS` MOCK_CALL

A caution from building this profile: it originally shipped **without** the
MIGRATION and IDEMPOTENCY rules and reported "0 findings" across a service that
had both a queue and migrations. Run `arch_check.py . --profile python
--coverage` after any change to the profile.

Definition: `tools/arch-check/profiles/python.json`.
