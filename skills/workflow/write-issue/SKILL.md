---
name: write-issue
description: Turns a vague observation, idea or bug report into a complete, actionable issue with acceptance criteria and non-goals. Use this skill whenever somebody describes a bug, wants a feature, says "we should really...", "can you make a ticket for that", "this is broken" or similar — even when the words issue or ticket never appear. Also use it when splitting an oversized issue, and to recognise when the input is not one issue at all but a whole specification — it then routes to `split-spec` instead of writing one. Do not use it when a finished issue already exists and only needs implementing.
---

# Write an issue

**Issues are written in GERMAN.** This skill file is English; the artifact it
produces is German — see AGENTS.md, "Language". Section headings must be
`## Slice
[Feature-Issues: ein Satz. Was kann ein Nutzer danach tun, was vorher nicht ging?
Bei chore und spike entfällt dieser Abschnitt.]

## Problem`, `## Akzeptanzkriterien`, `## Nicht-Ziele`, `## Kontext`,
`## Offene Fragen`, because `tools/skill-eval/rubric.py` checks them.

## Why this is the most important step

An issue that a new colleague could not implement without asking questions will
be implemented **wrongly and confidently** by a model. Humans ask when something
is unclear. Models fill gaps with plausible assumptions. Every gap in the issue
becomes an invented requirement in the code.

The time spent here comes back threefold in review.

## First: is this one issue, or a specification?

Decide this before anything else, because the two need different artifacts and
the wrong one is expensive in a way that is not visible for weeks.

Count the signals. **Two or more, and this is not an issue** — invoke `split-spec`
and stop here:

| Signal | What it looks like |
|---|---|
| It arrives as a document | a file, a table of contents, numbered top-level sections |
| It names systems, not behaviour | three or more capabilities that different people could build in different weeks |
| It carries an ordering | phases, a dependency graph, "erst X, dann Y", "Implementierungsreihenfolge" |
| The slice sentence needs "und" twice | or comes out as "die Plattform existiert dann" |
| One split is not enough | the parts of the first cut are each still `L` |

### The dividing line, when it is close

An `L` feature and a specification both get split, so the count above can feel
arbitrary at the edge. The question that separates them:

> **Do the parts have to be built in a particular order, and does something break
> if they are not?**

If the parts can be built in any order, it is a normal split — a table of
sub-issues, right here, per *Special cases in the output format*. If the order
carries the risk, the order is the artifact, and it needs a roadmap that outlives
the issues. That is `split-spec`.

### Two ways to get this wrong

**Writing one enormous issue "and splitting it later".** Later never has the
context this conversation has. The document is in front of you now.

**Splitting a spec straight into eighty issues.** It looks like progress and it
loses the ordering, which was the most expensive thing in the document. There is
a level between spec and issue and it is not optional.

When only *part* of the input is a spec — somebody describes a bug and attaches
the architecture document as background — write the issue. The spec is `Kontext`,
not the subject.

## Procedure

### 1. Separate observation from solution

The most common mistake is an issue that already contains the solution. The
actual cause then never gets examined.

| Not this | But this |
|---|---|
| "Invalidate the cache in `RechnungController`" | "After saving, the list shows stale values for a few seconds" |
| "Add an index on `orders.created_at`" | "The order list takes over 4 s for customers with more than 10,000 orders" |

If the person already names a solution: record it under *Kontext*, not under
*Problem*.

### 2. Ask for what is missing

Ask exactly the questions you would otherwise have to answer yourself — at most
three at a time. Typical gaps:

- Bugs: reproduction steps, expected vs. actual, environment, since when
- Features: who uses this? what happens on failure? what is the smallest useful scope?
- Always: what should explicitly **not** happen?

Do not guess. An issue with an open question beats one with an invented answer.

### 3. Determine kind and size

| Kind | Required field |
|---|---|
| `bug` | numbered reproduction steps |
| `feature` | acceptance criteria |
| `chore` | justification for doing it now |
| `spike` | question + time budget + result format, **never** production code |

Size: `S` under 100 diff lines, `M` under 400, `L` must be split.

**An `L` issue is not written, it is decomposed.** Split into slices — shippable
steps, each with its own answer to the slice question — not along technical
layers. "Migration", "model", "controller", "frontend" is the
wrong split — none of those parts is useful on its own. Right: "create invoice
(draft only)", "send invoice", "record payment".

### 4. Name the slice — feature issues only

One sentence, in a `## Slice` section:

> **What can a user do afterwards that they could not do before?**

```
## Slice
Die Buchhaltung sieht überfällige Rechnungen in der Übersicht, ohne die
Tabelle händisch zu führen.
```

This is the strongest filter against speculative work there is — stronger than
the non-goals list, because it fails loudly. If the honest answer is "nothing
yet, this is groundwork", the issue is not a feature: make it a `chore` or a
`spike`. Both are legitimate; a feature that ships nothing usable is not.

**A slice cuts through every layer it needs** — schema, domain, edge, UI. Do not
cut along layers. "Migration", "model", "controller", "frontend" is the wrong
split; none of those is useful alone.

**Do not force the slice to fit into one pull request.** A full-stack slice
regularly exceeds the 400-line review limit. That is expected: the slice ships as
several PRs (API behind a flag, then UI, then flag removal). Splitting the *PR*
is right; splitting the *slice* by layer to make it small is the mistake this
section exists to prevent.

`chore` and `spike` issues carry no `## Slice` section — see AGENTS.md §2.5 for
the work that is legitimately horizontal.

**The rubric only checks that the section exists, not that the slice is really
vertical.** That is deliberate. An earlier version tried to detect layer-shaped
sentences by keyword and failed on its own example: *"ohne die Tabelle händisch
zu führen"* describes the manual process being replaced, not a database table.
Verticality is a judgement call — the machine can insist the question is asked,
not that the answer is good.

### 5. Write the acceptance criteria

Every line must be answerable with yes or no, without discussion.

```
Bad:   - [ ] Die Performance ist besser
Good:  - [ ] Die Übersicht lädt bei 10.000 Bestellungen in unter 500 ms (p95)

Bad:   - [ ] Fehler werden sinnvoll behandelt
Good:  - [ ] Bei nicht erreichbarem Zahlungsdienst bleibt die Bestellung in
             Status `Ausstehend` und der Job wird dreimal wiederholt
```

### 6. Write the non-goals — required field

This is the single most effective measure against over-engineering and the only
place where "just do that too while you're in there" is forbidden in writing.

Good starting point: what would a diligent model build here in addition?

```
## Nicht-Ziele
- Keine Konfigurierbarkeit der Frist — der Wert 14 Tage wird fest kodiert
- Keine Umstellung der bestehenden `Rechnung`-Statusspalte (→ #142)
- Keine Mehrsprachigkeit der neuen Texte
- Kein Caching — erst wenn gemessen zu langsam
```

An empty non-goals section means: not thought through yet. Ask.

### 7. Set context anchors

Name concrete paths. Without them the implementation session searches the whole
repository and copies the wrong pattern.

```
## Kontext
Betroffen:     app/Actions/Rechnung/, app/Enums/RechnungStatus.php
Stil-Vorbild:  app/Actions/Rechnung/ErstelleRechnung.php
Verwandt:      #128 (dort wurde der Statuswechsel eingeführt)
Blockiert von: #131 (der Statuswechsel muss vorher existieren)
```

`Verwandt` and `Blockiert von` are different claims and the difference matters:
one is a hyperlink, the other is a constraint. `Verwandt` may be ignored;
`Blockiert von` means starting earlier produces a merge conflict, a second
half-implementation, or a migration that has to be undone. Leave the line out
when nothing blocks — do not write `Blockiert von: —` to fill it.

Issues that came out of a `split-spec` run also carry the milestone they belong
to, so the ordering survives the trip into the tracker:

```
Meilenstein:   M5 — Linked Accounts + Modul Discord Login
```

**Greenfield: `Stil-Vorbild` may be empty, and then it says so.** Before the
first code exists there is no exemplar, and inventing a path is worse than
admitting there is none — the next session will open it and find nothing, or
worse, find something unrelated and copy it.

```
Stil-Vorbild:  keins — dies ist das Vorbild für alles Weitere
```

`Betroffen:` still names paths, even paths that do not exist yet.

## Special cases in the output format

Three outcomes are not a normal issue but still need a file — otherwise the
decision is lost and the same request returns in two weeks.

**Split (was `L`).** Instead of problem and acceptance criteria: a table of the
sub-issues with size and a column "useful without the rest?". A part that answers
no is cut along a technical layer and must be decomposed again.

This is the one-level split, for a single oversized issue. If the parts have to
be built in a particular order, this file is the wrong artifact — go back to
*First: is this one issue, or a specification?* and use `split-spec`.

**Rejected in this form.** Why the scope is not workable, plus the open questions
whose answers would produce a workable one.

**Blocked on questions.** Provisional acceptance criteria are allowed and must be
marked as provisional. Do not invent anything to make the file look complete.

**Non-goals stay mandatory in all three cases.** They carry the most value
precisely here: they record what is deliberately *not* being built and answer
"why isn't that in there" without another discussion.

## Output format

```markdown
---
id: NNNN
typ: bug | feature | chore | spike
groesse: S | M
status: bereit
---

# Titel

## Problem
[Beobachtung, keine Lösung. Bei Bugs: nummerierte Reproduktion,
erwartet vs. tatsächlich, Umgebung.]

## Akzeptanzkriterien
- [ ] ...
- [ ] ...

## Nicht-Ziele
- ...

## Kontext
Meilenstein:   ...   ← nur nach einem split-spec-Lauf
Betroffen:     ...
Stil-Vorbild:  ...
Verwandt:      #...
Blockiert von: #...   ← nur wenn etwas blockiert

## Offene Fragen
- [ ] ...   ← muss vor Umsetzungsbeginn geklärt sein
```

## Self-check before handing over

- [ ] Was this really one issue, rather than a specification? (fewer than two
      signals from the table at the top)
- [ ] Does *Problem* really contain only the observation?
- [ ] Is every acceptance criterion answerable yes/no?
- [ ] Are there at least two non-goals?
- [ ] For a feature: does `## Slice` name something a user can do afterwards,
      rather than a layer that was built?
- [ ] Is the size `S` or `M`?
- [ ] Could somebody start from this without today's conversation?

If the last question is a no, context is missing from the issue — not from the
reader's head.
