---
name: harness-laravel
description: The Laravel stack profile for the engineering harness — how the eight principles map onto actions, enums, jobs, models and migrations, and which 29 rules the checker enforces. Use this skill when working in a Laravel or PHP repository that has the harness installed, when writing or reviewing Laravel code against the principles, or when a rule with a BOUNDARY_, STATE_, IDEMPOTENCY_ or MIGRATION_ prefix fires and you need to know what it means.
---

# Laravel profile

Concretises `AGENTS.md` for this stack. Where the two disagree, this file wins,
because it is the more specific one. Where they genuinely conflict: ask.

## Layers

| Principle BOUNDARIES | Directory |
|---|---|
| Domain | `app/Actions`, `app/Enums`, `app/Data`, `app/Support` |
| Edge | `app/Http`, `app/Jobs`, `app/Console` |
| Persistence | `app/Models`, `database` |

`app/Actions` imports nothing from `App\Http`. `app/Models` imports nothing from
`App\Actions`.

## Idioms

**Action** — `final readonly`, one `handle()` method, input is a DTO. Facades
only `DB` and `Log`; inject everything else. Transactions live here and nowhere
else.

**Controller** — about 15 lines, exactly one action call, no branching.

**State** — `enum` with `allowedTransitions()` and `canTransitionTo()`. `match`
without `default`. Transitions go through an action that takes `lockForUpdate()`
and checks the precondition.

**Job** — `final`, `implements ShouldQueue, ShouldBeUnique`, carries an id,
checks inside `handle()` whether the work is already done. `dispatch` sits
**outside** the transaction.

**Model** — relations, casts, scopes, `$fillable`. Never `$guarded = []`. In
`AppServiceProvider::boot()`: `Model::shouldBeStrict(! app()->isProduction())`.

**Migration** — `nullable()`, `timestampTz()`, a `down()` that you have actually
run. Index large tables with `CONCURRENTLY` and `public $withinTransaction = false`.

## Check chain

```bash
vendor/bin/pint --test
vendor/bin/phpstan analyse
python3 tools/arch-check/arch_check.py . --profile laravel
python3 tools/arch-check/eval.py --profile laravel
vendor/bin/pest
```

## Enforced automatically — 29 rules

`HYGIENE` STRICT_TYPES · DEBUG_OUTPUT · ENV_OUTSIDE_CONFIG
`BOUNDARIES` ACTION_HTTP · ACTION_FACADE · MODEL_LOGIC · SUPPORT_PURE · ENUM_PURE · CONTROLLER_DB
`FORM` ACTION_FINAL · ACTION_HANDLE · CONTROLLER_FINAL · JOB_FINAL · DATA_IMMUTABLE
`STATE` MASS_ASSIGNMENT · MATCH_DEFAULT · MONEY_FLOAT
`IDEMPOTENCY` JOB · JOB_MODEL
`TRANSACTION` DISPATCH
`ERRORS` SWALLOWED · SUPPRESSED
`MIGRATION` RENAME · DROP · NOT_NULL · TIMEZONE · BULK_UPDATE · DOWN
`TESTS` MOCK_CALL

Definition: `tools/arch-check/profiles/laravel.json`.
Fixtures: `tools/arch-check/fixtures/laravel/` — every rule has a planted
violation *and* clean code that looks like one.
