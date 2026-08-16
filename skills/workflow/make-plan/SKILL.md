---
name: make-plan
description: Produces a verifiable implementation plan with affected files, step sequence, stated assumptions and an explicit out-of-scope list, before any code exists. Use this skill as the mandatory first step for every issue, bug fix, refactor and larger change — including when somebody says "just implement X", "build me Y" or "fix that". Code may only be written after a human has confirmed the plan.
---

# Make a plan

**Read first:** `AGENTS.md` and `profiles/<stack>/PROFILE.md`.

## Purpose

A wrong plan costs two minutes. A wrong diff costs an hour of review. This is the
design document at the scale of a single issue and the cheapest place to abandon
a dead end.

**Rule: no code before the plan is confirmed.** Not even "just the beginning".

## Structure of the plan

### 1. The problem as understood (one paragraph)

In your own words, not as a quotation of the issue. Rephrasing exposes
misunderstandings; quoting hides them.

### 2. Assumptions made

**The most important section.** This is where hallucinations become visible
before they are code. List everything the issue does not answer but you need:

```
Assumptions:
- The period is computed in the user's time zone, not UTC   ← uncertain
- `Rechnung::betrag` is stored in cents (read from migration 2024_03_11)
- A job retry of 3 attempts already exists (queue configuration)
```

Mark uncertain assumptions explicitly. With more than two uncertain assumptions:
**abort the plan and ask** instead of building.

### 3. Affected files

Each file with one sentence. New files marked `NEW`.

```
app/Enums/RechnungStatus.php            add case `Mahnung` + transition rule
app/Actions/Rechnung/SendeMahnung.php   NEW — state change + dispatch job
app/Jobs/VersendeMahnungsMail.php       NEW — idempotent via ShouldBeUnique
database/migrations/..._add_mahnung...  NEW — column gemahnt_am, nullable
tests/Feature/Rechnung/MahnungTest.php  NEW — 4 cases (see step 5)
```

If this list grows past about eight entries the issue is too large. Say so and
propose a split.

### 4. Step sequence

Three to ten steps, each runnable and testable on its own. Ordered by "smallest
working step first".

```
1. Add enum case + transition rule, unit test        → green
2. Write migration and run it locally                 → green
3. Action with state change, feature test             → green
4. Job with idempotency guard, feature test with fake → green
5. Wire into the scheduler                            → green
```

Tests run after **every** step. Not at the end — otherwise a failure can no
longer be located.

### 5. Test plan

Which cases, which kind of test. Concrete, not "write tests".

```
Feature: invoice sent 14 days ago      → status Mahnung, job queued
Feature: invoice already paid          → no change, no job
Feature: job executed twice            → one mail only (idempotency)
Unit:    RechnungStatus::darfWechselnZu → all 16 combinations
```

### 6. What I will not touch

Mirrors the issue's non-goals and adds whatever else you noticed while reading.

```
Not touched:
- Existing state-change logic in ErstelleRechnung
- Dunning fees (no acceptance criterion asks for them)
- Configurability of the 14-day period → hard-coded per the non-goals
- No new dependency
```

### 7. Diff estimate

One number. It is compared against the actual diff in review and by
`tools/skill-eval/workflow_run.py`.

```
Estimated: ~180 lines (of which ~90 tests)
```

## What invalidates a plan

Abort and ask instead of delivering a plan when:

- More than two uncertain assumptions are required
- The issue has no acceptance criteria or no non-goals
- The work would need a new dependency
- Authentication, authorization, payments or data migration are affected without
  the issue naming them explicitly
- More than eight files would be touched

## After confirmation

The confirmed plan becomes the working basis. If the implementation deviates —
because something turns out to be wrong while building — **say so first, then
deviate.** A silent deviation makes the plan worthless and surprises the reviewer.
