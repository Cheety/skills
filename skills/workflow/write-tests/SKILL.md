---
name: write-tests
description: Writes tests for a codebase — structure tests for principles, unit tests for pure logic, integration tests against real infrastructure. Stack-neutral; test runner and idioms come from profiles/<stack>/PROFILE.md. Use this skill for any request about tests, coverage, "write tests for X", "how do I test Y", when securing a bug fix, and always as part of implementing a feature. Contains the distinction between useful fakes and worthless mock assertions.
---

# Write tests

**Read first:** `profiles/<stack>/PROFILE.md` for test runner, directories and idioms.

## Ground rule

**The property comes from a human or from the issue. The test is written from it.**

Never produce code and test in one pass without an intermediate check — the test
then gets adjusted to the code and loses exactly the property it exists for: being
an independent statement about the requirement.

## Which kind of test for what

| Level | For what | Cost |
|---|---|---|
| Structure | Principle rules, import boundaries | seconds |
| Unit | Pure logic without infrastructure: state transitions, computation, formatting | milliseconds |
| Integration | The normal case: application logic, routes, jobs | seconds |

Rule of thumb: **if a database is involved, it is an integration test.** A "unit
test" that reimplements persistence to avoid the database only tests the
reimplementation.

**An in-memory database does not replace the real one.** Transaction behaviour,
locking, JSON columns and constraint names all differ. A test against it proves
nothing about production.

## Fakes yes, mocks no

The distinction decides the value of the suite.

**Wanted — doubles at system boundaries:** external HTTP services, mail, queue,
file system, clock. They replace the outside world and still check **behaviour**:
was the right mail triggered to the right address?

**Forbidden — mocks of your own classes with pure call assertions.** The only
assertion is that a method was called. Such tests trace the implementation, break
on every refactor and find no bugs — and they are exactly what a model produces
most eagerly and in the largest quantity.

**Rule of thumb:** if you have to adjust the test after a pure refactor even
though behaviour did not change, it was a bad test.

## Characterization tests — the exception to the red phase

Not every new test belongs to new behaviour. There is a legitimate category that
**must be green** the moment it is written:

- recording a rule the code already satisfies but never asserted (typically
  boundary values such as "from day 15, not on day 14")
- securing a coupling you rely on ("the discount path validates the line items
  because it calls the validating sum function")
- documenting legacy behaviour before restructuring it

**These tests cannot be red by definition.** Filing them as bug fixes and forcing
a red run leads either to an artificially planted bug or to the rule being
quietly skipped.

### The proof runs through a mutation instead

Green alone proves nothing — a tautological test is green too. Therefore:

```
1. Write the test, the run is green
2. BREAK the production logic under test (shift the boundary, remove the check)
3. The run MUST turn red          ← this is the proof
4. Revert the mutation, the run is green again
5. Commit with the title "Doku:"
```

Step 3 does exactly what the red run does otherwise: it shows the test is coupled
to the logic and not trivially true.

`tools/skill-eval/workflow_run.py` checks this automatically when a work item is
marked as a characterization.

## The four cases that are almost always missing

The happy path always gets tested. These four do not — and they are the ones that
occur in production:

1. **Repetition.** Execute the same thing twice. The result must be identical and
   must not produce a second effect.
2. **Precondition violated.** The operation aborts — **and leaves no partial
   state.** That is the real assertion, not the exception being thrown.
3. **Concurrency.** Two calls on the same record. One wins, the other fails cleanly.
4. **The outside world fails.** Timeout on the external service. What is left behind?

## Check state transitions exhaustively

An enumerated type with defined transitions has a small, countable state space.
Check **all** combinations from a data source rather than a hand-picked selection
— with five states that is twenty-five cases in one line of test code.

For open value ranges (parsers, serialization, computation) property-based testing
is the right tool. First candidates are round trips: `decode(encode(x)) == x`.

## Factories and fixtures

States as named construction methods, not attribute lists in the test. That way
the test states intent instead of mechanics, and a new mandatory field changes one
place instead of forty.

## What does not get tested

- Framework behaviour
- Accessors without logic
- Configuration values
- Markup line by line

## Coverage

No target, no CI threshold. Useful application: list untested lines in the domain
and decide about each one. A percentage target reliably produces tests without
assertions — coverage rises, meaning does not.

## Naming

The test name describes behaviour from the system's point of view, not the method.
On failure the name alone should be enough to understand what is broken.
