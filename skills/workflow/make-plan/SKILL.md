---
name: make-plan
description: Produces a verifiable implementation plan with affected files, step sequence, stated assumptions and an explicit out-of-scope list, before any code exists. Use this skill as the mandatory first step for every issue, bug fix, refactor and larger change — including when somebody says "just implement X", "build me Y" or "fix that". Code may only be written after a human has confirmed the plan.
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

**Rule: no code before the plan is confirmed.** Not even "just the beginning".

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

## After confirmation

The confirmed plan becomes the working basis. If the implementation deviates —
because something turns out to be wrong while building — **say so first, then
deviate.** A silent deviation makes the plan worthless and surprises the reviewer.
