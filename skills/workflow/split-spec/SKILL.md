---
name: split-spec
description: Turns an architecture document, a concept paper or a roadmap into a milestone plan plus the issues for the first milestone only. Use this skill when somebody hands over a whole undertaking rather than a single change — a spec, a design document, "here is the architecture, make tickets", a numbered phase plan, or anything naming several systems and their build order. `write-issue` routes here on its own when its input turns out to be a specification. Do not use it for a single feature or bug, however large.
---

# Split a specification

**Roadmap and issues are written in GERMAN.** This skill file is English; the
artifacts it produces are German — see AGENTS.md, "Language". The roadmap
headings are `Blockiert von:`, `Definition of Done:` and the backlog table,
because `tools/skill-eval/roadmap_check.py` checks them.

## Why this is its own step

A specification answers "what are we building". An issue answers "what do I do
in the next session". Between them sits the question neither of them asks:
**in which order, and what breaks if you get the order wrong.**

That question has no home in an issue. `## Kontext` carries `Verwandt: #142`,
which is a hyperlink, not a constraint. So when a 700-line spec is chopped
directly into eighty issues, the ordering — the most expensive knowledge in the
document, usually the part somebody thought hardest about — evaporates on the
way into the tracker. Six weeks later somebody implements the polling integration
before the queue system exists, and the reason it was written down is now the
reason nobody can find it.

The roadmap is where that knowledge lives, and it is a **file in the repository**,
not an issue. Issues get closed. The build order has to still be readable in
month four.

## The four levels

| Level | Answers | Bounded by | Lives in |
|---|---|---|---|
| **Spec** | what are we building | nothing | `docs/specs/` |
| **Milestone** | in which order, and what blocks what | a Definition of Done | `docs/roadmap/` |
| **Issue** | what do I do in this session | `S` or `M` | the tracker |
| **Pull request** | what gets reviewed together | 400 lines, 8 files | the forge |

**Spec → issue directly is the mistake this skill exists to prevent.** One level
of splitting is never enough for a document of this size: the first cut produces
parts that are each still `L`, and a model that has been told to produce issues
will produce eighty of them anyway, in whatever shape makes the count come out.

## Procedure

### 1. Find the ordering, or produce it

Read the spec for its **order**, not its content. Many specs already carry one —
a phase list, a dependency graph, a "first this, then that" section. Use it; the
author knew things you do not.

If there is no ordering, that is the first thing to write, and it needs two
criteria, not one:

1. **Technical dependency** — what cannot be built before what
2. **Cost of being wrong** — data model, registries, anything other code will
   shape itself around

Expensive-to-change goes early. Purely additive work — observability, an API
layer, further notification channels — goes late, because it never blocks
anything and it is the first thing to be cut when time runs out.

### 2. Cut into milestones

Five to fifteen. Fewer means the milestones are still specs; more means they are
issues wearing a hat.

A milestone is **not** a slice. It is a container with an ordering and a
Definition of Done. The slice question is asked one level down, of the issues
inside it.

### 3. Horizontal milestones are allowed. Horizontal features are not

This is the distinction that decides whether the split is honest.

Groundwork is real work: tooling, persistence conventions, a queue system, an
architecture test. None of it lets a user do anything new, and pretending
otherwise produces slice sentences like *"Der Nutzer profitiert von einer
stabilen Datenbasis"*, which is theatre. AGENTS.md §2.5 names this work
explicitly: those milestones consist of `chore` and `spike` issues, and neither
carries a `## Slice` section.

What stays forbidden is a **feature** issue cut along a layer. Inside a milestone
that ships behaviour, every `feature` row answers "useful without the rest?" with
yes. A row that answers no is a layer and must be decomposed again — or it was a
chore all along and should say so.

The mechanical form of that rule: `roadmap_check.py` rejects `nein` in the last
column for `feature` rows and permits it for `chore` and `spike`.

### 4. Pull the dependencies forward

Every new package gets its **own `chore` issue**, placed in the earliest
milestone that needs it. AGENTS.md §5: no new dependency without its own issue
and a justification.

Skipping this step is what makes the next twenty planning sessions abort.
`make-plan` refuses to plan an issue that would introduce a dependency
(`make-plan`, *What invalidates a plan*) — correctly, but if every second issue
in the roadmap silently brings a package with it, that rule fires twenty times in
a row and somebody starts ignoring it. Decide the dependencies once, in their own
issues, at the front.

The same applies to whatever the spec touches that AGENTS.md §7 protects —
authentication, authorization, payment handling, data migration. If a milestone
needs it, the milestone says so, and the issue names it. Then the plan does not
have to guess whether it was intended.

### 5. Write the roadmap file

One file per spec, at `docs/roadmap/<name>.md`. Format below. Check it:

```bash
python3 tools/skill-eval/roadmap_check.py docs/roadmap
```

The checker enforces the part that decays: that every `Blockiert von:` points at
a milestone that exists, that there is no cycle, and that the milestones are
**written in an order you can build in** — a milestone never depends on one
further down the page. Reading top to bottom has to be the build order, because
that is the only way anybody will read it.

### 6. Write the issues for the first milestone only

Not for all of them. Two reasons, and the second is the stronger one:

- Issues for milestone 8 are written against a codebase that does not exist. The
  `Kontext` anchors point at paths nobody has created, and every one of them is a
  guess that a later session will follow confidently.
- The whole point of the early milestones is to find out that the design was
  wrong somewhere. If the tracker already holds seventy issues when that happens,
  correcting them costs more than writing them did, so they get implemented
  instead.

The remaining milestones stay as **backlog rows** in the roadmap. A row is one
line; an issue is a contract. Turn the next milestone's rows into issues when the
previous one is done, by handing each row to `write-issue`.

### 7. Greenfield has no style exemplar — say so

For the first milestones, `Stil-Vorbild:` cannot be filled in, because there is
no code yet. Write that down instead of inventing a path:

```
## Kontext
Meilenstein:   M1 — Persistenz-Konventionen
Blockiert von: #3 (Projektgeruest)
Betroffen:     app/Models/BaseModel.php (neu), database/migrations/
Stil-Vorbild:  keins — dies ist das Vorbild fuer alles Weitere
```

`Betroffen:` still names target paths, even when they do not exist. The rubric
wants a path (`R6`), and more importantly the next session needs to know where
the file belongs rather than deciding for itself.

## Output format — the roadmap

```markdown
---
typ: roadmap
quelle: docs/specs/core-systeme.md
status: aktiv
---

# Core-Systeme

[Zwei Saetze: Worum geht es, und woran ist die Reihenfolge ausgerichtet.]

## M0 — Fundament & Tooling

Blockiert von: —
Definition of Done: Ein leeres Beispielmodul laesst sich erzeugen, die CI erfasst
es, und der Architektur-Test schlaegt bei einem absichtlich gesetzten
Cross-Import fehl.

| Issue | Typ | Groesse | Nuetzlich ohne den Rest? |
|---|---|---|---|
| Projektgeruest mit Docker, Redis, Datenbank | chore | M | nein — Vorarbeit, siehe AGENTS §2.5 |
| Architektur-Test gegen modulaebergreifende Imports | chore | S | ja — greift ab dem ersten Modul |

## M1 — Persistenz-Konventionen

Blockiert von: M0
Definition of Done: ...

| Issue | Typ | Groesse | Nuetzlich ohne den Rest? |
|---|---|---|---|
| ... | ... | ... | ... |
```

`Blockiert von: —` means "nothing", and is the only allowed way to say it. An
empty line reads as "not thought about yet", and the checker treats it that way.

## What this skill does not produce

- **No issue for the roadmap itself.** It is a document, it is reviewed in a
  pull request like any other file, and it changes when the plan changes.
- **No estimates in time.** `S` and `M` are diff sizes. A milestone has no size
  at all; it has a Definition of Done.
- **No implementation order inside a milestone.** That is what the issues'
  `Blockiert von:` is for, and it is decided when they are written, not now.

## Self-check before handing over

- [ ] Does every milestone have a Definition of Done that somebody could test?
- [ ] Does `roadmap_check.py` pass?
- [ ] Does every new dependency have its own `chore` row, in the milestone that
      first needs it?
- [ ] Does every `feature` row answer "useful without the rest?" with yes?
- [ ] Are issues written for the **first** milestone only?
- [ ] Would somebody who never read the spec build it in the right order from
      this file alone?

If the last question is a no, the reasoning stayed in the spec. Move the
sentences that carry it — especially the ones about what breaks when the order is
violated — into the milestone they belong to.
