---
name: write-migration
description: Writes database migrations that can be rolled out without downtime or data loss — expand/migrate/contract, safe column changes, batched backfills, indexes without table locks. Language-independent. Use this skill for every schema change, that is for "new column", "alter table", "write a migration", "rename a field", "add an index", and for every feature that needs new data fields. Migrations are hard to reverse; extra care applies.
---

# Write a migration

**Read first:** `profiles/<stack>/PROFILE.md` for the migration tool and its
idioms. The rules below hold regardless — they follow from the deployment
sequence, not from the tool.

## Why this skill has its own rules

A migration is the one part of the system where a rollback is not enough: the code
can be rolled back, deleted data cannot. And during a deployment the old and the
new application version run **simultaneously** against the same schema for
seconds or minutes.

Every migration must therefore work with **both** code versions.

## Ground rule: expand — migrate — contract

Never in one step. Always across three deployments.

```
Deploy 1 — Expand
  Add the new column, nullable or with a default.
  New code writes to OLD and NEW, reads from OLD.
  Old code keeps running unchanged.

Deploy 2 — Migrate
  Backfill existing rows in batches.
  Code reads from NEW, still writes to both.

Deploy 3 — Contract
  Drop the old column. Write only to NEW.
  Only once deploy 2 is demonstrably live everywhere.
```

For a purely additive column that no old code knows about, one deployment is
enough. For anything that renames, drops or retypes, the three-step applies
without exception.

## Forbidden inside a single migration

| Operation | Why | Instead |
|---|---|---|
| Rename a column | old code accesses the old name during the deployment | new column, backfill, drop the old one later |
| Drop a column | old code still writes to it | contract step, its own later deployment |
| Add `NOT NULL` without a default | existing rows violate it immediately | nullable, backfill, then `NOT NULL` |
| Change a column type | locks the table, may truncate data | new column, backfill, switch over |
| Bulk `UPDATE` in `up()` | locks the table for the duration of the migration | separate batched command or job |

## Additive migration (the normal case)

- New columns nullable, or with a default
- Time stamps **with** a time zone — otherwise the zone is silently lost
- `down()` actually reverses and has been **run locally**, not merely written

## Index without a table lock

A plain `CREATE INDEX` locks writes on the whole table. On large tables that is an
outage. Use the concurrent variant your database offers — and note that it usually
cannot run inside a transaction, which the migration tool must be told.

## Backfill in batches

Never inside the migration. A bulk `UPDATE` over millions of rows locks the table
and stalls the deployment.

- Iterate by primary key, not by a moving filter window — otherwise rows are
  skipped when the filter condition changes during the run
- Suppress events and timestamps: a backfill is not a domain change
- Make it repeatable: a second run must break nothing

## Foreign keys and delete behaviour

Choose the delete behaviour deliberately. Cascading deletion is convenient and
deletes more than anybody expected. Restricting is the safe default: it fails
loudly instead of deleting quietly.

## Checklist before the PR

- [ ] Does the schema work with **both** the old and the new code version?
- [ ] Nothing renamed, dropped or retyped that is still in use?
- [ ] Is `down()` written **and executed locally**?
- [ ] New column nullable or with a default?
- [ ] No bulk `UPDATE` inside the migration itself?
- [ ] Concurrent index creation on large tables, outside a transaction?
- [ ] Foreign key delete behaviour chosen deliberately?
- [ ] Dry run of the migration inspected (the profile names the command)?
- [ ] For a contract step: is the previous deployment demonstrably live everywhere?

## What a human must decide

Migrations are among the non-delegable areas in `AGENTS.md`. Produce the proposal
and the plan, but:

- The contract step (dropping a column) is never executed without explicit human
  agreement
- For tables above roughly a million rows, estimate and state the runtime first
- If you are unsure whether a column is still read: **do not drop it, ask**
