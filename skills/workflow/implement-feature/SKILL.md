---
name: implement-feature
description: Implements a feature issue in code — strictly along the acceptance criteria and without extra abstraction, working from the confirmed plan filed on the issue. Stack-neutral; the concrete idioms come from profiles/<stack>/PROFILE.md. Use this skill for every implementation of new behaviour, that is whenever a confirmed plan exists or somebody says "build the feature", "implement issue #X", "add X", regardless of language or framework. Contains the countermeasures against over-engineering and the test-first cycle.
---

# Implement a feature

**Read first, in this order:** `AGENTS.md` (principles) →
`profiles/<stack>/PROFILE.md` (directories, idioms, check chain) → the style
reference file named in the plan.

Without the reference file you are guessing the house style. The profile
describes it, the file demonstrates it.

## Precondition — the confirmed plan comes from the issue

Read the issue and its comments. The plan is the newest comment beginning with
`## Umsetzungsplan (bestätigt)`, filed there by `make-plan`.

**No such comment: stop.** Say that the plan is missing and point to `/plan #X`.
Do not reconstruct the plan from the acceptance criteria — that is planning, it
happens without a human confirming it, and the confirmation is the whole point
(AGENTS.md §1). A plan pasted into the chat instead is acceptable *only* if the
human pastes it in this session; then say so in the PR, because the ticket has no
record of it.

The plan's `Betroffene Dateien`, `Schrittfolge` and `Testplan` are what you
implement. Where the plan and the acceptance criteria disagree, the criteria win
and the disagreement gets named out loud before you build anything.

## The core sentence

> Implement exactly the acceptance criteria. Nothing beyond them.

No extra error handling for impossible states. No extension points. No
configuration options. No new abstraction layers. No new dependencies.

That reads as excessive and is not. Without this explicit block you reliably get
factories, interfaces with one implementation and switches nobody asked for.

## Order — test first

```
1. SCAFFOLD  Types, states, signatures. Bodies throw "not implemented".
2. RED       Skill `write-tests`: one test per acceptance criterion.
             The run MUST fail — and fail on the assertion.
3. COMMIT    Tests only, message starts with "Test:".
4. GREEN     Implement until the tests pass. No test changes.
5. COMMIT    Message starts with "Impl:".
```

### Why test first — the reason differs from the human case

For humans TDD is mostly a design method. Here it solves a narrower problem:
**when code and test come out of the same pass, the test gets adjusted to the
code** — losing exactly the property it exists for. A test that was already red
before an implementation existed cannot be that.

Second effect: a test written before the implementation **cannot** reference
implementation details, because none exist. It necessarily describes behaviour.
That is the most effective antidote to the mock-call assertions models otherwise
produce in bulk.

### Two worthless red phases

Both must be ruled out before the test commit:

**(a) The test fails because the symbol is missing.** "Class not found", "cannot
resolve module", syntax error. That proves only that the file is absent, nothing
about the assertion. Hence the scaffold comes before the red run.

**(b) The test is green although nothing is implemented.** The more dangerous
case, because it does not stand out. It arises from tautologies — for instance
asserting that a not-yet-existing state permits no transition: trivially true
while the state is unknown, and true afterwards for an entirely different reason.

> **Every new test must be red in the red phase.** If one is green it is either
> tautological or does not belong to this change. Both get resolved before the
> commit.

Exactly one exception: **characterization tests** that record already-correct
behaviour. They are green from the start and are proven by a mutation rather than
by a red run — see skill `write-tests`. They are committed with `Doku:`, not with
`Test:`.

This check is automatable as soon as the test runner honours a simple output
contract — one line per test, `OK <name>` or `XX <name>`.
`tools/skill-eval/workflow_run.py` reads which tests are new and reports every
one that is already green. The contract takes a few lines in any language and is
what keeps this rule from depending on somebody looking closely.

### How far a missing symbol reaches

What matters is not the language but **when** the missing symbol is resolved:

| Resolution | Effect | Examples |
|---|---|---|
| **At call time** | only the affected test fails, the rest still runs | PHP method call, Python attribute access |
| **At import time** | **the whole test file aborts** — zero results instead of red tests | `import { X }` in ES modules, `from m import X` in Python |
| **At compile time** | nothing runs at all | Java, Go, Rust, TypeScript via `tsc` |

The same language behaves differently: in Python a missing module attribute is
harmless, a missing `from … import …` at the top of the file is fatal.

**As soon as a test imports a new symbol, the scaffold is committed first** — even
for a bug fix that seemingly changes one line.

Warning sign: **zero new test results** instead of red ones. Looking only at the
exit code, that passes for a successful red run — but the run was empty.

> An empty suite is not green, it is broken. The output contract makes that
> difference visible mechanically; the exit code alone does not.

### What is not built test-first

Rigid TDD at every level produces exactly the brittle tests this skill exists to
prevent:

| Test-first | Not test-first |
|---|---|
| Application logic, one test per acceptance criterion | Migrations |
| State transitions | Wiring, registration, schedulers |
| Pure computation and formatting | Output formats without logic |
| Idempotency and error paths | Exploring unfamiliar third-party APIs (→ `spike`) |

**Granularity:** tests are written against the **outermost stable interface** of
the change — the use case, not its internal helpers. A test per internal function
freezes the structure and breaks on every refactor even though behaviour did not
change. The internal design stays free; that is what makes the tests durable.

### When tests cannot be executed

If the red run is impossible in this environment, the first effect remains (the
test does not get adjusted to the code) and the second one is lost: **without an
observed red run, "the test covers the requirement" is a claim.** Note that in
the PR explicitly rather than skipping it silently.

### Then

Inside the green phase, work from the inside out: types and states, migration,
persistence, application logic, asynchronous work, edge, wiring. Run the check
chain from the profile after **every** step.

### Proof

`tools/skill-eval/cycle_check.py` reads the git history and evidences the
sequence: test commit before implementation commit, test commit without
production code, suite red at the test commit, green at the implementation
commit, no retroactive test changes.

## The seven places where generated code fails

They all work in the happy path. That is precisely why they only surface in
production.

1. **State as a boolean combination.** Use an enumerated type with defined
   transitions and an exhaustive check **without** a catch-all arm.
2. **State change without a lock.** Two concurrent calls read the same record,
   both see the precondition satisfied, both write. Read under a lock, check the
   precondition *after*.
3. **Side effect inside the transaction.** On rollback the recipient reacts to a
   state that never existed. The trigger goes after the commit.
4. **Missing idempotency.** The queue delivers at least once, more under load.
   Check at the start whether the work is already done and return without effect.
5. **Object instead of identifier in the job.** The serialized object is stale by
   the time it is processed.
6. **Money as floating point.** Integer in the smallest unit, with a telling suffix.
7. **Swallowed errors.** Empty catch, or one that only logs and carries on.
   Unhandled rejected promises. Expected domain errors are named exceptions.

## Over-engineering: the countermeasures

Check **while** writing, not afterwards:

| Temptation | Rule |
|---|---|
| Add an interface | Only on the second real implementation |
| Make a value configurable | Only on the second real consumer. Otherwise hard-code it |
| Abstract the third occurrence | Rule of three — with two duplicates it stays duplicated |
| Wrap everything in a catch | Only where a domain error is handled. Otherwise let it through |
| Introduce a base class | No. One inheritance level at most |
| Add a dependency | Its own issue, otherwise no |
| "Prepare for later" | No. The later case looks different from what you imagined |

**The question for every line whose purpose is not obvious:**

> Which acceptance criterion asks for this?

No answer → delete it before opening the PR.

## Before opening the PR

- [ ] Full check chain from the profile is green
- [ ] Every acceptance criterion verified individually, not skimmed
- [ ] Diff size within the estimate from the plan
- [ ] Everything removed that no criterion asks for
- [ ] Checked whether existing code already did this
- [ ] I could explain every decision without looking at the code

The last line is not rhetorical. Whoever cannot tick it does not open a PR —
otherwise the reviewer assesses code that nobody understood on the authoring side.
