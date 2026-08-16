# Profile: Laravel

Makes `AGENTS.md` concrete for this stack. On disagreement this file wins.

## Stack

PHP 8.3+ (`declare(strict_types=1)` everywhere) · Laravel 11 · PostgreSQL 16
(in tests too) · Redis + Horizon · Pest 3 · PHPStan + Larastan level 8 · Laravel Pint

**Deliberately not used:** repository pattern on top of Eloquent, container
bindings without a second implementation, generic `BaseService` classes.

## Layers

| BOUNDARIES principle | Directory |
|---|---|
| Domain | `app/Actions`, `app/Enums`, `app/Data`, `app/Support` |
| Edge | `app/Http`, `app/Jobs`, `app/Console` |
| Persistence | `app/Models`, `database` |

`app/Actions` imports nothing from `App\Http`. `app/Models` imports nothing from
`App\Actions`.

## Idioms

**Action** — `final readonly`, one `handle()` method, input is a DTO. Facades only
`DB` and `Log`; inject everything else. Transactions live here and nowhere else.

**Controller** — around 15 lines at most, exactly one action call, no conditionals.

**State** — `enum` with `erlaubteFolgezustaende()` and `darfWechselnZu()`. `match`
without `default`. State changes go through an action using `lockForUpdate()` and
a precondition check.

**Job** — `final`, `implements ShouldQueue, ShouldBeUnique`, carries an id, checks
inside `handle()` whether the work is already done. `dispatch` sits **outside** the
transaction.

**Model** — relations, casts, scopes, `$fillable`. No `$guarded = []`. In
`AppServiceProvider::boot()`: `Model::shouldBeStrict(! app()->isProduction())`.

**Migration** — `nullable()`, `timestampTz()`, `down()` present and executed
locally. Index on large tables with `CONCURRENTLY` and
`public $withinTransaction = false`.

## Check chain

```
vendor/bin/pint --test
vendor/bin/phpstan analyse
python3 tools/arch-check/arch_check.py . --profile laravel
python3 tools/arch-check/eval.py --profile laravel
vendor/bin/pest
```

## Automatically enforced — 29 rules

`HYGIENE` STRICT_TYPES · DEBUG_OUTPUT · ENV_OUTSIDE_CONFIG
`BOUNDARIES` ACTION_HTTP · ACTION_FACADE · MODEL_LOGIC · SUPPORT_PURE · ENUM_PURE · CONTROLLER_DB
`FORM` ACTION_FINAL · ACTION_HANDLE · CONTROLLER_FINAL · JOB_FINAL
`STATE` MASS_ASSIGNMENT · MATCH_DEFAULT · MONEY_FLOAT
`IDEMPOTENCY` JOB · JOB_MODEL
`TRANSACTION` DISPATCH
`IMMUTABILITY` DATA
`MIGRATION` RENAME · DROP · NOT_NULL · TIMEZONE · BULK_UPDATE · DOWN
`ERRORS` SWALLOWED · SUPPRESSED
`TESTS` MOCK_CALL

Definitions and fixtures: `tools/arch-check/profiles/laravel.json`,
`tools/arch-check/fixtures/laravel/`.
