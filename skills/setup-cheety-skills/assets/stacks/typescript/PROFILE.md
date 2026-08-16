# Profile: TypeScript

Makes `AGENTS.md` concrete for this stack. On disagreement this file wins.

## Stack

TypeScript 5.x with `strict: true` · Node 22 · PostgreSQL 16 (in tests too, via
Testcontainers) · Vitest · ESLint with `@typescript-eslint` · Prettier

**Deliberately not used:** `any`, default exports, class inheritance as reuse,
barrel files across layer boundaries.

## Layers

| BOUNDARIES principle | Directory |
|---|---|
| Domain | `src/actions`, `src/domain`, `src/types` |
| Edge | `src/http`, `src/jobs`, `src/cli` |
| Persistence | `src/db`, `src/db/migrations` |

`src/actions` imports neither `express` nor `@prisma/client`. `src/domain` knows
neither outer layer. Dependencies are passed as parameters, not imported.

## Idioms

**Action** — `export async function execute(...)`, named export. Dependencies
(repository, mailer, queue) as parameters. No default export.

**State** — discriminated union instead of boolean fields:

```ts
type Rechnung =
  | { readonly status: 'versendet'; readonly versendetAm: Date }
  | { readonly status: 'mahnung';   readonly gemahntAm: Date };
```

`switch` over the union **without** `default` — the compiler then enforces
exhaustiveness. `switch (true)` used as an if-chain is exempt.

**Money** — `number` with a `Cents` suffix. `amount: number` is a finding,
`amountCents: number` is not.

**DTO** — `readonly` on every field. Types suffixed `Data`, `Dto` or `Input`.

**Job** — `export async function handle(...)` with an idempotency check: an
idempotency key or an early return when the work is already done.

**Transaction** — `enqueue`, `publish`, `emit`, `sendMail` sit **outside**
`$transaction(...)`.

**Errors** — no empty `catch`. Every `.then()` chain has a `.catch()`. Expected
domain errors are named error classes.

**Migration** — `timestamptz`, `nullable`, `down()` present. No `dropColumn` or
`renameColumn` in `up()` without a contract deployment (`@contract` in the header).

## Check chain

```
npx prettier --check .
npx tsc --noEmit
npx eslint .
python3 tools/arch-check/arch_check.py . --profile typescript
python3 tools/arch-check/eval.py --profile typescript
npx vitest run
```

## Automatically enforced — 25 rules

`HYGIENE` STRICT_TYPES (`any`) · TS_IGNORE · DEBUG_OUTPUT · ENV_OUTSIDE_CONFIG
`BOUNDARIES` ACTION_HTTP · ACTION_DB · DOMAIN_PURE · ROUTE_DB
`FORM` ACTION_EXPORT · ACTION_DEFAULT_EXPORT
`STATE` BOOLEAN_FLAGS · SWITCH_DEFAULT · MONEY_NUMBER
`IDEMPOTENCY` HANDLER
`TRANSACTION` SIDE_EFFECT
`IMMUTABILITY` DTO
`ERRORS` SWALLOWED · FLOATING_PROMISE
`MIGRATION` RENAME · DROP · NOT_NULL · TIMEZONE · BULK_UPDATE · DOWN
`TESTS` MOCK_CALL

Definitions and fixtures: `tools/arch-check/profiles/typescript.json`,
`tools/arch-check/fixtures/typescript/`.
