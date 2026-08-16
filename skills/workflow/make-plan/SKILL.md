---
name: make-plan
description: Produces a verifiable implementation plan with affected files, step sequence, stated assumptions and an explicit out-of-scope list, before any code exists, and files the confirmed plan on the issue. Use this skill as the mandatory first step for every issue, bug fix, refactor and larger change — including when somebody says "just implement X", "build me Y" or "fix that". This skill never writes code, not even after confirmation; implementation is a separate session with the skill `implement-feature`.
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

**Rule: no code in this skill at all.** Not before the confirmation, and not
after it. Confirmation ends this session's work — see *After confirmation* below.

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

## After confirmation — the plan goes into the ticket, not into code

A confirmation is permission to *record* the plan, not permission to start
building. Two things happen, in this order, and then this session is over:

1. **Append the confirmed plan to the issue** as a comment.
2. **Stop.** Name the next command and write nothing else.

```
Plan als Kommentar an #21 angehängt.
Umsetzung mit: /implement #21
```

Continuing into the implementation in the same session is the failure this
section exists to prevent. It looks efficient and costs the two properties the
split is there for: the plan is only in the transcript, so the next session and
the reviewer cannot read what was agreed; and the context that produced the plan
— every file read while writing it, every rejected alternative — silently becomes
implementation context, which is exactly what "one issue, one session"
(AGENTS.md §7) forbids.

### The comment format

The comment is German, like the issue, and begins with a fixed heading so
`implement-feature` can find it mechanically:

```markdown
## Umsetzungsplan (bestätigt)

Bestätigt am 2026-08-16 von @semyon.

[the plan verbatim, all its headings unchanged:
 Problem wie verstanden · Annahmen · Betroffene Dateien · Schrittfolge ·
 Testplan · Nicht angefasst · Slice-Grenze · Diff-Schätzung]
```

Verbatim means verbatim. Do not summarise the plan for the comment — a shortened
plan in the ticket and a full plan in a closed transcript is worse than no plan,
because the next session trusts the short one.

If assumptions were confirmed, corrected or dropped in the conversation, the
comment carries the **confirmed** version, and the correction is visible:

```markdown
- Die Frist wird in der Zeitzone des Nutzers gerechnet   ← bestätigt, war unsicher
- ~~Der Aktivator liest die Statusdatei beim Start~~     ← verworfen, siehe Diskussion
```

### How it gets there

Whatever the forge offers, in this order:

```bash
tea comment 21 --body-file plan.md          # Forgejo
gh issue comment 21 --body-file plan.md     # GitHub
glab issue note 21 --message "$(cat plan.md)"  # GitLab
```

If no forge CLI is configured, **do not invent an API call with a token you
guessed.** Output the comment as a fenced block ready to paste and say plainly
that it still has to be pasted. An unposted plan that the human knows about is
recoverable; a plan the session believes it filed and did not is not.

Post the plan **once**. Replanning after a rejection appends a new comment rather
than editing the old one — the rejected version is part of the record, and the
newest `## Umsetzungsplan (bestätigt)` comment is the one that counts.

### Then, in the implementation session

The confirmed plan in the ticket is the working basis. If the implementation
deviates — because something turns out to be wrong while building — **say so
first, then deviate**, and note the deviation on the issue. A silent deviation
makes the plan worthless and surprises the reviewer.
