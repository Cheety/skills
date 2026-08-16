---
name: fix-bug
description: "Fixes bugs following the order reproduce, failing test, separate commit, fix. Language-independent. Use this skill whenever something does not work, a bug is reported, a test is red, a stack trace shows up, or somebody says 'this is broken', 'fix it', 'why doesn't X work'. Prevents the two most common failure modes: treating the symptom instead of the cause, and tests written after the fix that would never have caught it."
---

# Fix a bug

## Procedure — mandatory, in this order

```
1. Reproduce               no reproduction, no fix
2. Locate the cause        not the symptom
3. Write a test that exposes the bug
4. Run it → it FAILS                      ← reproduction proven
5. Commit that test ALONE
6. Implement the fix
7. Run it → green                          ← fix proven
8. Run the rest of the suite → nothing broken
```

**Step 5 is skipped most often and carries most of the value.** A test written
after the fix does not prove it would have caught the bug. The separate commit
makes the reproduction verifiable in the history.

## Step 1 — reproduce

No reproduction, no fix. If it is missing, that is the question to ask, not the
start of a search.

Needed: input, expected behaviour, actual behaviour, environment, frequency.

For "only happens sometimes", the pattern matters more than the code: time of day,
user group, data volume, concurrency, cache state, queue delay. Almost every
sporadic bug comes from one of these corners, regardless of language or framework:

| Pattern | Typical cause |
|---|---|
| Only under load | race condition without a lock, duplicate job delivery |
| Only for some users | missing relation, null in an unchecked field, permissions |
| Only after a deployment | cached configuration, env var outside the config layer |
| Only with large data volumes | N+1, missing index, timeout, memory |
| Only in production | time zone, queue driver, debug switch, cache driver |
| Only the second time | missing idempotency |

## Step 2 — cause, not symptom

Ask "why" at least twice.

```
Symptom:  the customer is dunned twice
Why?      the job ran twice
Why?      the queue redelivered after a timeout
Cause:    the job is not idempotent
```

The fix belongs at that point — a precondition check inside the job — not a lock
flag in the controller that suppresses the second call. The controller was never
the problem.

**Warning sign for symptom treatment:** the fix adds a condition that catches a
state instead of explaining how that state could arise. If you cannot say how the
state arises, you have not found the cause.

## Step 3 — the test

It must sit at the level of the cause, not of the symptom. It checks behaviour,
not implementation, and would still hold if the fix were later done differently.

**Run it before the fix and confirm that it fails — and fails for the right
reason.** A test that is red because of a typo proves nothing. See also
`implement-feature`, "Two worthless red phases": a test that is *green* before the
fix is just as worthless.

## Step 4 — the fix

- As small as possible. A bug-fix PR changes nothing unrelated to the bug.
- No refactoring in the same PR. If something ugly surfaces while fixing: its own issue.
- No adjusting existing tests. If the fix turns an existing test red, that is a
  finding, not an obstacle — it evidently described the wrong behaviour. That
  belongs in the PR description, explicitly justified.

## Step 5 — afterwards

- [ ] Does the same cause exist elsewhere? (Other jobs without idempotency?)
- [ ] Can a rule rule this out in future? Then add a principle rule or a type-checker
      rule instead of only fixing
- [ ] Does the affected path emit enough logs to see this faster next time?

The third point is the bridge to observability: a bug that was hard to find
indicates missing observability, not just a programming mistake.

## Proof rather than assertion

The order above is the core of this skill — and it is **mechanically checkable**.
`tools/skill-eval/cycle_check.py` reads the git history and checks six things:

1. The `Test:` commit precedes the `Fix:` commit
2. The test commit contains **no** production code
3. Checked out at the test commit, the suite is **red** — reproduction proven
4. At the fix commit it is **green** — fix proven
5. The fix changes **no existing tests**
6. The fix is minimal

Point 3 is the actual proof. Without it, "I wrote the test first" is a claim.
Commit titles therefore start with `Test:` and `Fix:`.

## What does not happen

- No fix without a reproduction
- No fix without a previously failing test
- No test adjustment without justification in the PR
- No refactoring in a bug-fix PR
- No `try/catch` that merely swallows the error
- No disabling a warning to make it go away — the warning is the finding
