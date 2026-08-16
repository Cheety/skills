---
name: code-review
description: Reviews a diff or pull request — scope, layer boundaries, error behaviour, state modelling, test quality, over-engineering. Language-independent. Use this skill for requests such as "review this", "look at the PR", "does this look right", "what do you think of this code", and as a pre-review before opening a PR. The result is always a preliminary pass and never replaces human approval.
---

# Code review

**Read first:** `AGENTS.md` (principles) and `profiles/<stack>/PROFILE.md`
(idioms, automatically enforced rules).

**Review comments are written in GERMAN** — see AGENTS.md, "Language".

## Up front: this pass is preliminary

An LLM review finds forgotten cases, typos and rule violations. It **never**
counts as the human approval. Say so in the result if it could otherwise be
mistaken for final.

Likewise: a model reviewing its own code reliably likes it. If the diff comes from
the same session, this review is weaker than one with fresh context. Say that too.

## What is not checked here

Formatting, import order, naming conventions with one right answer, obvious type
errors. Formatter, type checker and the principle checker handle those. **Every
comment about a space is a tooling failure, not a review finding.**

Review time is reserved for judgement, not pattern matching.

### Tool findings: one line, with rule ids

When the review runs **before** CI, violations of the principle rules are still
useful — but they cost no prose. Collapse them into one line and name the rule id:

```
## werkzeug (blockt ohnehin in CI)
- :9 BOUNDARY_ACTION_HTTP · :10 BOUNDARY_ACTION_FACADE · :13 FORM_ACTION_FINAL
  :15 FORM_ACTION_HANDLE · :25 DEBUG_OUTPUT
```

The rule id serves two purposes: the author immediately sees what CI blocks hard
and what is a judgement call, and the findings become machine-comparable — a
review that misses a known violation stands out.

**Conversely, mark every finding no tool can produce** as such. Those findings are
what justifies the review. If they cluster in one area, that is a hint a rule is
missing — see "Adding a rule" in `AGENTS.md`.

## Checklist, in this order

### 1. Scope — the most important question

Does the PR solve the issue, and **only** that?

- What is in the diff that no acceptance criterion mentions?
- Was a non-goal violated?
- Is the diff more than twice the estimate from the plan? Then it needs explaining.

For every non-obvious block: **which acceptance criterion asks for this?** No
answer → it should be removed. That is the single highest-yield review question.

### 2. Boundaries

- Does the domain import from edge or persistence? (The principle checker should
  catch it — if not, a rule is missing)
- Is application logic sitting in the edge layer, the persistence model, a
  template or a migration?
- Is the edge code longer than the profile allows, or does it call more than one
  use case?
- New dependency without its own issue?

### 3. Error behaviour and concurrency

The area where generated code is most reliably weak, because it works in the happy
path.

- Is the same record read and written without a lock under concurrent calls?
- Is a new job idempotent? What happens on a second delivery?
- Is an event or job triggered **inside** a transaction? On rollback the recipient
  then acts on a state that never existed.
- Does a job carry an object instead of an identifier?
- Is there a `try/catch` that only logs and carries on?
- What happens on a timeout of the external service? Is partial state left behind?

### 4. State model

- New boolean columns that together describe a status? → require an enumerated type
- Exhaustive check over an enumerated type **with** a catch-all arm? → a new case
  then lands there silently instead of breaking compilation
- Is a state change performed without checking its precondition?

### 5. Tests

- Does the new test fail **without** the change? (For a bug fix: does the separate
  test commit exist before the fix?)
- Does the test check behaviour or implementation? Mock-call assertions are rejected.
- Is only the happy path tested? The error path and repetition are almost always missing.
- Was an **existing** test changed? Then the PR description must justify it —
  otherwise send it back. Without this rule the suite is quietly adjusted over
  months to whatever the code currently does.

### 6. Database

- Is the migration backwards compatible? Is a column added and used in the same deployment?
- Is `down()` present and actually reversing?
- New query inside a loop without eager loading? (N+1)
- Index for new filter or sort columns?

### 7. Comprehensibility

Not "is it clever", but: **will the reason explain itself in six months?**

If a block needs a comment to be understandable, first check whether a rename or
an enumerated type makes the comment unnecessary.

## Output format

Grouped by how binding it is, with file and line. Comments in German:

```markdown
## werkzeug (blockt ohnehin in CI)
- :9 BOUNDARY_CONTROLLER_DB · :11 FORM_CONTROLLER_FINAL · :35 ENV_OUTSIDE_CONFIG

## blocker (Urteil erforderlich)
- `app/Jobs/VersendeMahnungsMail.php:34` — Der Job prüft nicht, ob die Mahnung
  bereits versendet wurde. Bei doppelter Zustellung geht die Mail zweimal raus.
  **Vom Prüfer nicht erkennbar.**

## frage
- `app/Actions/Rechnung/SendeMahnung.php:15` — Warum `firstOrFail` statt
  `lockForUpdate`? Zwei gleichzeitige Aufrufe können beide durchlaufen.

## vorschlag
- `app/Enums/RechnungStatus.php:28` — `match` hat einen `default`-Zweig.

## scope
- `app/Support/DateHelper.php` — neu angelegt, nur an einer Stelle benutzt.
  Welches Akzeptanzkriterium verlangt die Extraktion? Rule of three.
```

Prefixes: `blocker` blocks the merge · `frage` asks for an explanation ·
`vorschlag` does not block · `scope` concerns extent rather than correctness.

## Procedural limits

| Rule | Value |
|---|---|
| Maximum diff size | 400 lines. Beyond that: require a split |
| Turnaround | under 4 working hours |
| Reviewers | 1 normally |
| 2 reviewers for | auth, payments, data migration, public API, delete operations |

## Tone

Questions rather than instructions for design decisions, clear statements for
defects. The author has context the diff does not show — a question surfaces it,
an instruction runs it over.
