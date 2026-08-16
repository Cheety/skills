# Profile: Python

Makes `AGENTS.md` concrete for this stack. On disagreement this file wins.

## Stack

Python 3.12 · type hints everywhere, `mypy --strict` · PostgreSQL 16 (in tests
too) · Ruff for formatting and linting

**Deliberately not used:** mutable default arguments, bare `except`, dynamic
attribute assembly, `from x import *`.

## Layers

| BOUNDARIES principle | Directory |
|---|---|
| Domain | `src/actions`, `src/domain`, `src/typen` |
| Edge | `src/http`, `src/jobs`, `src/cli` |
| Persistence | `src/db`, `src/db/migrations` |

`src/actions` imports neither a web framework nor a database driver.
`src/domain` knows neither outer layer.

## Idioms

**Action** — `def execute(...)` with dependencies as parameters.

**State** — `Enum` or `Literal` union with an explicit transition table.
Exhaustive `match` without `case _`.

**Money** — `int` with a `_cent` suffix. `betrag: float` is a finding.

**DTO** — `@dataclass(frozen=True)`.

**Job** — `def handle(...)` with an idempotency check before any effect.

**Migration** — `up()` only adds, `down()` reverses. Time stamps `timestamptz`,
new columns `nullable=True` or with a default.

## Check chain

```
ruff format --check .
ruff check .
mypy --strict src
python3 tools/arch-check/arch_check.py . --profile python
python3 tools/arch-check/eval.py --profile python
python3 -m pytest
```

## Automatically enforced — 20 rules

`HYGIENE` DEBUG_OUTPUT · TYPE_IGNORE · ENV_OUTSIDE_CONFIG
`BOUNDARIES` ACTION_HTTP · ACTION_DB · DOMAIN_PURE
`STATE` MUTABLE_DEFAULT · MONEY_FLOAT
`IDEMPOTENCY` HANDLER
`TRANSACTION` SIDE_EFFECT
`IMMUTABILITY` DTO
`ERRORS` BARE_EXCEPT · SWALLOWED
`MIGRATION` RENAME · DROP · NOT_NULL · TIMEZONE · BULK_UPDATE · DOWN
`TESTS` MOCK_CALL

Definitions and fixtures: `tools/arch-check/profiles/python.json`,
`tools/arch-check/fixtures/python/`.
