---
name: harness-typescript
description: The TypeScript stack profile for the engineering harness — how the eight principles map onto actions, discriminated unions, queue handlers and migrations, and which 25 rules the checker enforces. Use this skill when working in a TypeScript or Node repository that has the harness installed, when writing or reviewing TypeScript against the principles, or when a rule with a BOUNDARY_, STATE_, ERROR_ or MIGRATION_ prefix fires and you need to know what it means.
---

# TypeScript profile

Concretises `AGENTS.md` for this stack. Where the two disagree, this file wins.

## Layers

| Principle BOUNDARIES | Directory |
|---|---|
| Domain | `src/actions`, `src/domain`, `src/types` |
| Edge | `src/http`, `src/jobs`, `src/cli` |
| Persistence | `src/db`, `src/db/migrations` |

`src/actions` imports neither `express` nor `@prisma/client`. `src/domain` knows
neither outer layer. Dependencies arrive as parameters, not as imports.

## Idioms

**Action** — `export async function execute(...)`, a named export.
Dependencies (repository, mailer, queue) as parameters. No default export.

**State** — a discriminated union instead of boolean fields:

```ts
type Invoice =
  | { readonly status: 'sent';     readonly sentAt: Date }
  | { readonly status: 'reminded'; readonly remindedAt: Date };
```

`switch` over the union **without** `default` — then the compiler enforces
exhaustiveness. `switch (true)` as an if-chain is exempt.

**Money** — `number` with a `Cents` suffix. `amount: number` is a finding,
`amountCents: number` is not.

**DTO** — `readonly` on every field. Type names end in `Data`, `Dto` or `Input`.

**Job** — `export async function handle(...)` with an idempotency check: an
idempotency key, or an early return when the work is already done.

**Transaction** — `enqueue`, `publish`, `emit`, `sendMail` sit **outside**
`$transaction(...)`.

**Errors** — no empty `catch`. Every `.then()` chain has a `.catch()`.

**Migration** — `timestamptz`, `nullable`, a `down()`. No `dropColumn` or
`renameColumn` in `up()` without a contract deploy (`@contract` in the header).

## Check chain

```bash
npx prettier --check .
npx tsc --noEmit
npx eslint .
python3 tools/arch-check/arch_check.py . --profile typescript
python3 tools/arch-check/eval.py --profile typescript
npx vitest run
```

## Enforced automatically — 25 rules

`HYGIENE` STRICT_TYPES (`any`) · TS_IGNORE · DEBUG_OUTPUT · ENV_OUTSIDE_CONFIG
`BOUNDARIES` ACTION_HTTP · ACTION_DB · DOMAIN_PURE · ROUTE_DB
`FORM` ACTION_EXPORT · ACTION_DEFAULT_EXPORT
`STATE` BOOLEAN_FLAGS · SWITCH_DEFAULT · MONEY_NUMBER
`IDEMPOTENCY` HANDLER · `TRANSACTION` SIDE_EFFECT · `IMMUTABILITY` DTO
`ERRORS` SWALLOWED · FLOATING_PROMISE
`MIGRATION` RENAME · DROP · NOT_NULL · TIMEZONE · BULK_UPDATE · DOWN
`TESTS` MOCK_CALL

One detail worth knowing: in ES modules a missing import kills the **whole test
file**, so a red run produces zero results rather than red tests. That is why the
scaffold step is mandatory here even for a one-line bug fix — see the
`implement-feature` skill.

Definition: `tools/arch-check/profiles/typescript.json`.
