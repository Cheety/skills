# AGENTS.md — project rules

This file is handed to **every** LLM session as context and doubles as the
onboarding document for humans. One document, two audiences.

It is **stack-neutral**. What applies in *this* project — directory names, idioms,
tooling — lives in the profile:

> **Active profile: `profiles/<stack>/PROFILE.md`**
> On disagreement the profile wins, because it is more concrete. On genuine
> conflict: ask, do not decide.

---

## 0. Language

**The instruction is English. The artifact is German.** That one sentence
decides every case below.

| Artifact | Language |
|---|---|
| Code, tools, profiles, fixtures, rules, skills, this file | **English** |
| `README.md` | **German** |
| **Issues, milestone plans (`docs/roadmap/`), implementation plans, pull-request descriptions, review comments** | **German** |
| Commit subjects | **German**, with the fixed English prefixes `Test:`, `Impl:`, `Fix:`, `Doku:` |

Everything the team discusses work in is German. Everything the harness is built
from is English, so it stays portable and readable to contributors who do not
speak German.

Wherever a tool or a skill *touches* a German artifact, German appears inside
English on purpose and is not an oversight: `tools/skill-eval/rubric.py` and
`tools/skill-eval/roadmap_check.py` match German wording and German headings
because the files they check are German, and the workflow skills show German
example output inside English prose.

The commit prefixes stay English because `tools/skill-eval/cycle_check.py`
matches them, and because they encode the phase of the cycle rather than the
content of the change.

---

## 1. The three sentences

1. **No code without an issue.** No issue without verifiable acceptance criteria
   and explicit non-goals.
2. **The human owns the specification and the approval.** The model owns the draft.
3. **Whoever opens a pull request is the author** — regardless of who typed the
   characters. "The model wrote that" is not a valid answer in review.

Everything below is machinery that makes those three sentences enforceable.

---

## 2. The eight principles

Each principle is language-independent. *How* it is checked is decided by the
profile — every rule there carries the principle it belongs to.

### BOUNDARIES — dependencies point one way

Three layers, and the middle one does not know the outer ones:

```
Edge  ─────►  Domain  ◄─────  Persistence
(HTTP, CLI,   (application     (database,
 queue)        logic)           external services)
```

The domain imports **nothing** from edge or persistence. The gain is not database
swappability — that practically never happens — but testability: core logic runs
in milliseconds without a server, a container or framework boot time.

*The profile decides:* which directories map to which layer.

### STATE — make illegal states unrepresentable

No status is expressed through several independent boolean fields. Four flags
produce sixteen combinations of which perhaps three are valid; the other thirteen
are latent bugs that somebody eventually creates.

States are enumerated types with defined transitions. An exhaustive branch over
all cases has **no** catch-all arm — otherwise a new case lands there silently
instead of breaking compilation.

Monetary amounts are integers in the smallest unit, never floating point.

### IDEMPOTENCY — every delivery can repeat

Queues and HTTP retries deliver at least once, and more than once under load.
"Exactly once" over a network is not practically achievable.

Every asynchronous handler must therefore be protected against double execution:
an idempotency key, a precondition with a state check, or a unique column. Not
by hope.

Asynchronous jobs carry **identifiers, not objects**. A serialized object is
already stale by the time it is processed.

### TRANSACTION — side effects only after the commit

If a job, an event or an email is triggered **inside** a transaction, a rollback
leaves the recipient reacting to a state that never existed.

Where the write and the publish genuinely have to be atomic: an outbox table in
the same transaction, read by a separate process.

### IMMUTABILITY — data is replaced, not mutated

Data-transfer objects are immutable. Concurrency becomes harmless, and "did
anything change?" becomes a reference comparison.

### MIGRATION — expand, migrate, contract

During a deployment the old and the new application version run **simultaneously**
against the same schema. Every migration must work with both.

Never rename, drop or retype in one step. New columns are nullable or have a
default. Bulk updates run as a separate batched script, not inside the migration.
Timestamps carry a time zone. Every migration is reversible.

### ERRORS — fail loudly, not silently

No empty catch block. No catch block that only logs and carries on. No unhandled
rejected promise. Expected domain errors are named exceptions, not null returns.

### HYGIENE — what never belongs in production

No debug output. No environment variables outside the configuration layer — with
a cached configuration they silently return the default. No suppressed type check
without a comment carrying an issue number.

---

## 2.5 Slices and pull requests

A slice is a **shippable step**: after it, somebody can do something they could
not do before. It cuts through every layer it needs — schema, domain, edge, UI —
and it is useful on its own. Splitting along technical layers ("migration",
"model", "controller", "frontend") is forbidden, because none of those parts is
useful alone and the integration surprises all arrive at the end.

Every feature issue therefore answers one question, in the `## Slice` section:

> **What can a user do afterwards that they could not do before?**

If the honest answer is "nothing yet, this is groundwork", the issue is not a
feature. It is a `chore` or a `spike`, and that is a legitimate thing to be.

### A slice is not a pull request

This distinction matters more than it sounds, because without it the size limits
below quietly push work back into layer splits.

| Unit | What it measures | Bounded by |
|---|---|---|
| **Slice** | value and planning | usefulness on its own |
| **Pull request** | review | 400 lines, 8 files |

A full-stack slice regularly exceeds 400 lines. That is not a rule violation and
not a reason to cut the slice horizontally. It means the slice ships as **several
pull requests**: API behind a flag, then the UI, then removing the flag. What
ships together does not have to be reviewed together.

Each pull request names the slice it belongs to. The slice is done when its
`## Slice` sentence is true in production, not when the last PR merges.

**Under time pressure the tempting move is the wrong one:** layers fit under 400
lines comfortably, slices do not. If you find yourself cutting by layer to make a
PR small enough, split the PR instead of the slice.

### Work that is legitimately horizontal

Not everything is a slice, and pretending otherwise produces theatre:

- migrations, backfills, indexes
- dependency upgrades
- observability and logging
- spikes

These are `chore` or `spike` issues. They carry no `## Slice` section, and the
rubric does not ask them for one.

---

## 2.6 Above the slice — milestones

An undertaking that arrives as a **document** — an architecture paper, a concept,
a phase plan — is not an issue and does not become one by being split. It gets a
milestone plan first:

```
Spec  ──►  Milestone  ──►  Issue  ──►  Pull request
```

Skipping the middle step is the common failure and it is invisible for weeks. The
issues come out fine; what is lost is the **ordering** — which system has to
exist before which, and what breaks when that order is violated. An issue has no
field for that. `Verwandt: #142` is a hyperlink, not a constraint.

| Level | Answers | Bounded by | Lives in |
|---|---|---|---|
| **Spec** | what are we building | nothing | `docs/specs/` |
| **Milestone** | in which order, and what blocks what | a Definition of Done | `docs/roadmap/` |
| **Issue** | what do I do in this session | `S` or `M` | the tracker |
| **Pull request** | what gets reviewed together | 400 lines, 8 files | the forge |

The milestone plan is a **file in the repository**, not an issue: issues get
closed, and the build order has to still be readable in month four. It is checked
mechanically — dangling references, cycles, and milestones written in an order
nobody could build in:

```bash
python3 tools/skill-eval/roadmap_check.py docs/roadmap
```

A milestone is not a slice. It is a container with an ordering, and it may be
entirely horizontal — the slice question is asked one level down, of the issues
inside it. Two rules follow from that and both matter:

- **Every new dependency gets its own `chore` issue** in the earliest milestone
  that needs it (§5). Decided once, at the front — otherwise the plan step
  refuses twenty issues in a row for the same reason and people start ignoring it.
- **Issues are written for the current milestone only.** Issues for milestone 8
  anchor on paths that do not exist yet, and they are written against a design
  the early milestones exist to disprove.

---

## 3. Tests

**The human states the property, the model writes the test.** Never both in one
pass without an intermediate check — otherwise the test gets adjusted to the code
rather than the other way round.

### For bugs, in this order

1. Write a test that exposes the bug
2. Run it and watch it **fail** — reproduction proven
3. **Commit that test on its own**
4. Implement the fix
5. Test is green — the fix is proven

Step 3 is the one most often skipped and it carries most of the value.

### Kinds of test

| Level | For what |
|---|---|
| Structure | Principle rules. Run in seconds, prevent decay |
| Unit | Pure logic without infrastructure |
| Integration | The normal case. **Real database**, real routing |

**Forbidden:** tests whose only assertion is that a double was called. They trace
the implementation, break on every refactor and find no bugs.

**Allowed and wanted:** fakes at system boundaries — external HTTP services, mail,
queue. That replaces the outside world while still checking behaviour.

**An in-memory database does not replace the real one.** Transaction behaviour,
locking, JSON columns and constraint names all differ.

### Coverage

No target, no CI threshold. Useful application: list untested lines in the domain
and decide about each one. A percentage target reliably produces tests without
assertions.

---

## 4. Rules belong in tooling

**A rule that is not enforced automatically decays within months.**

In this order:

1. What the **language** can enforce → types, enums, immutability
2. What the **type checker** can enforce
3. What the **principle checker** can enforce → `tools/arch-check`
4. What the **formatter** can enforce
5. What **CI** can check
6. Only the remainder belongs in prose

The automatically enforced rules of the active profile are listed in its
`PROFILE.md`. If the same prose violation comes up three times in review:
**automate the rule instead of repeating it louder.**

### Adding a rule

1. Rule as data in `tools/arch-check/profiles/<stack>.json`
2. Violation in `tools/arch-check/fixtures/<stack>/`, marker `!! RULE_ID`
3. Add clean code that **looks like** a violation
4. `tools/arch-check/eval.py` — must pass

Step 3 is the important one. A rule without a false-positive test is not
finished: a false positive makes people bypass the tool. A missing rule does not.

### Adding a stack

A new profile, nothing else. The engine knows no language. It needs file
extensions, comment and string syntax, layer mapping, rules. Template:
`tools/arch-check/profiles/_template.json`.

**One lesson from the rewrite:** first check whether your language's signal lives
in code, in comments or in string literals. In PHP an import is code
(`use App\Http\...`), in TypeScript the path sits inside a string
(`from '@prisma/client'`), and in pragmas such as `@ts-ignore` it is inside a
comment. Rules therefore set `"source": "raw"` whenever the signal lives outside
plain code.

**Declare, do not omit.** A principle a stack genuinely lacks goes into
`not_applicable`. A profile that simply has no rule for a principle reports
"0 findings" — indistinguishable from a clean codebase.

---

## 5. Prose rules — outstanding debt

Not yet automated:

- No new dependency without its own issue and a justification
- No interface with a single implementation (test doubles at system boundaries excepted)
- No configuration option without a second real consumer
- No inheritance hierarchy deeper than one level
- No change to existing tests in the same PR as a behaviour change
- Rule of three: abstract on the third identical case, not before

---

## 6. Definition of done

- [ ] All acceptance criteria ticked and individually confirmed in the PR
- [ ] A test exists that fails **without** this change
- [ ] Full check chain green locally (format, types, principles, tests)
- [ ] Migration compatible with the old **and** the new code version, `down` run locally
- [ ] Documentation and changelog updated for externally visible changes
- [ ] Unfinished work behind a feature flag with an expiry date and a cleanup issue
- [ ] New behaviour emits a structured log or a metric
- [ ] PR references the issue and closes it on merge

---

## 7. Working practice

**Plan before implementation, and hand it off in writing.** Skill `make-plan`
ends at the hand-off: the confirmed plan becomes a comment on the issue, headed
`## Umsetzungsplan (bestätigt)`. That comment — not a transcript — is what the
implementation session reads. Planning and building are two sessions.

**One issue, one session.** Context from issue A produces wrong patterns in issue B.

**Three-attempts rule.** If the same approach fails three times: new session,
better context, possibly a human. Models dig in and produce more workarounds with
every further attempt.

**Facts are looked up, decisions are asked.** Digging out how the code behaves is
the model's job; choosing between workable designs is the human's, and `make-plan`
puts those in one round before it writes anything. A question costs a minute. An
invented requirement costs a review round and then lives on in the code.

**Not touched without explicit human instruction:** authentication, authorization,
payment handling, data migrations, configuration structure, CI, this file.
