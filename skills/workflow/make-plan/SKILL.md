---
name: make-plan
description: Produces a verifiable implementation plan with affected files, step sequence, stated assumptions and an explicit out-of-scope list, then files the confirmed plan on the issue as the hand-off to implementation. Use this skill as the mandatory first step for every issue, bug fix, refactor and larger change — including when somebody says "just implement X", "build me Y" or "fix that". It ends at the hand-off; the code is written in a separate session with the skill `implement-feature`.
---

# Make a plan

**Plans are written in GERMAN.** This skill file is English; the artifact it
produces is German — see AGENTS.md, "Language". A human confirms the plan, and
they confirm it in the language they discuss the work in.

**Read first:** `AGENTS.md` and `profiles/<stack>/PROFILE.md`.

## Purpose

A wrong plan costs two minutes. A wrong diff costs an hour of review. This is the
design document at the scale of a single issue and the cheapest place to abandon
a dead end.

**This skill ends at the hand-off.** It produces one artifact — the plan — and
files it on the ticket once a human confirms it. The code belongs to the next
session; see *After confirmation* below.

## Structure of the plan

The plan is delivered under these headings, in this order and with these German
names. The sections below explain each one in English; what you write is German.

```
## Problem wie verstanden
## Annahmen
## Betroffene Dateien
## Schrittfolge
## Testplan
## Nicht angefasst
## Slice-Grenze      ← nur bei features
## Diff-Schätzung
```

### 1. The problem as understood (one paragraph)

In your own words, not as a quotation of the issue. Rephrasing exposes
misunderstandings; quoting hides them.

### 2. Assumptions made

**The most important section.** This is where hallucinations become visible
before they are code. List everything the issue does not answer but you need:

```
## Annahmen
- Die Frist wird in der Zeitzone des Nutzers gerechnet, nicht in UTC   ← unsicher
- `Rechnung::betrag` liegt in Cent (aus Migration 2024_03_11 gelesen)
- Ein Job-Retry von 3 Versuchen existiert bereits (Queue-Konfiguration)
```

Mark uncertain assumptions explicitly. With more than two uncertain assumptions:
**abort the plan and ask** instead of building.

### 3. Affected files

Each file with one sentence. New files marked `NEW`.

```
## Betroffene Dateien
app/Enums/RechnungStatus.php            Fall `Mahnung` + Übergangsregel
app/Actions/Rechnung/SendeMahnung.php   NEU — Statuswechsel + Job dispatchen
app/Jobs/VersendeMahnungsMail.php       NEU — idempotent über ShouldBeUnique
database/migrations/..._add_mahnung...  NEU — Spalte gemahnt_am, nullable
tests/Feature/Rechnung/MahnungTest.php  NEU — 4 Fälle (siehe Schritt 5)
```

If this list grows past about eight entries the issue is too large. Say so and
propose a split.

### 4. Step sequence

Three to ten steps, each runnable and testable on its own. Ordered by "smallest
working step first".

```
## Schrittfolge
1. Enum-Fall + Übergangsregel, Unit-Test              → grün
2. Migration schreiben und lokal ausführen            → grün
3. Action mit Statuswechsel, Feature-Test              → grün
4. Job mit Idempotenz-Sperre, Feature-Test mit Fake    → grün
5. In den Scheduler hängen                            → grün
```

Tests run after **every** step. Not at the end — otherwise a failure can no
longer be located.

### 5. Test plan

Which cases, which kind of test. Concrete, not "write tests".

```
## Testplan
Feature: Rechnung vor 14 Tagen versandt  → Status Mahnung, Job in der Queue
Feature: Rechnung bereits bezahlt        → keine Änderung, kein Job
Feature: Job zweimal ausgeführt          → nur eine Mail (Idempotenz)
Unit:    RechnungStatus::darfWechselnZu  → alle 16 Kombinationen
```

### 6. What I will not touch

Mirrors the issue's non-goals and adds whatever else you noticed while reading.

```
## Nicht angefasst
- Bestehende Statuswechsel-Logik in ErstelleRechnung
- Mahngebühren (kein Akzeptanzkriterium verlangt sie)
- Konfigurierbarkeit der 14-Tage-Frist → laut Nicht-Zielen fest kodiert
- Keine neue Abhängigkeit
```

### 6.5 Slice boundary — features only

State plainly whether this plan **completes** the slice or only advances it:

```
## Slice-Grenze
Slice:        #142 — Buchhaltung sieht überfällige Rechnungen
Meilenstein:  M2 — Mahnwesen
Dieser Plan bringt den Slice voran (API + Statuswechsel).
Offen bleibt: Anzeige in der Übersicht -> eigener PR, gleicher Slice.
```

When the issue names a milestone, the plan repeats it — a plan that silently
advances a different milestone than the issue claims is how the build order comes
apart one issue at a time.

If the plan would exceed 400 lines or eight files, **split the pull request, not
the slice**. Cutting the slice by layer to make a PR small enough is the failure
this section exists to prevent — layers fit comfortably under the limit and slices
do not, which is exactly why the pressure points the wrong way. See AGENTS.md §2.5.

## 7. Diff estimate

One number. It is compared against the actual diff in review and by
`tools/skill-eval/workflow_run.py`.

```
## Diff-Schätzung
~180 Zeilen (davon ~90 Tests)
```

## What invalidates a plan

Abort and ask instead of delivering a plan when:

- More than two uncertain assumptions are required
- The issue has no acceptance criteria or no non-goals
- The work would need a new dependency
- Authentication, authorization, payments or data migration are affected without
  the issue naming them explicitly
- More than eight files would be touched

Two of these read differently when the issue came out of a `split-spec` run, and
the difference is not a loophole:

- **A dependency `chore` is not blocked by the dependency rule.** Adding the
  package *is* the issue, the justification is in it, and it was decided at the
  roadmap level rather than in passing (AGENTS.md §2.6). What still aborts is a
  feature that brings a package along with it.
- **`Blockiert von: #131` has to be closed before this plan starts.** Planning
  against an unbuilt precondition produces assumptions about code somebody else
  is still writing. Say so and stop; that is a scheduling answer, not a design one.

## After confirmation — the hand-off

Confirmation buys a hand-off, not a start. Two steps, then this session is over:

1. **Append the confirmed plan to the issue** as a comment, in the format below.
2. **Report where it landed and what runs next:**

```
Plan als Kommentar an #21 angehängt: <Link>
Umsetzung mit: /implement #21
```

The hand-off is done when somebody who was not in this conversation can read the
whole plan on the ticket. Building in the same session skips it and costs both
things the split exists for: the agreement stays in a transcript nobody reopens,
and the context that produced the plan — every file read, every rejected
alternative — becomes implementation context, which is what "one issue, one
session" (AGENTS.md §7) keeps apart.

### The comment format

German, like the issue, under a fixed heading so `implement-feature` finds it
mechanically:

```markdown
## Umsetzungsplan (bestätigt)

Bestätigt am <Datum> von @<Person>.

[der Plan wörtlich, alle Überschriften unverändert:
 Problem wie verstanden · Annahmen · Betroffene Dateien · Schrittfolge ·
 Testplan · Nicht angefasst · Slice-Grenze · Diff-Schätzung]
```

The comment carries the **full** plan — every heading, every line. The next
session trusts what it finds on the ticket, so a summary there and the real plan
in a closed transcript is worse than no plan at all.

Assumptions the conversation confirmed, corrected or dropped go in as confirmed,
with the movement visible:

```markdown
- Die Frist wird in der Zeitzone des Nutzers gerechnet   ← bestätigt, war unsicher
- ~~Der Aktivator liest die Statusdatei beim Start~~     ← verworfen, siehe Diskussion
```

### How it gets there

The repository ships one forge — `.forgejo/`, `.github/` or `.gitlab/` says which
— so post with that forge's CLI (`tea`, `gh`, `glab`) and read its flags from
`--help` rather than from memory. Where no CLI is configured, the route is the
human: output the comment as a fenced block ready to paste and say that it is
still unposted. Reach for a CLI or for the human, never for a hand-rolled API
call with a guessed token — a plan the human knows is unposted is recoverable, a
plan the session reported as filed is not.

Replanning after a rejection appends a **new** comment: the rejected version
stays in the record, and the newest `## Umsetzungsplan (bestätigt)` is the one
that counts.
