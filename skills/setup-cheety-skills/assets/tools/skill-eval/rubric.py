#!/usr/bin/env python3
"""
rubric — checks issue files against the self-review list in
.claude/skills/issue-erstellen/SKILL.md. Language- and stack-independent:
it inspects the structure of the issue, not the code behind it.

Language note: the word lists below are GERMAN on purpose. Issues in this
project are written in German (see AGENTS.md, "Language"), so the vague-wording
and solution-wording detectors have to match German text. Everything else in
this repository is English.

Usage: rubric.py <issue-directory>
"""
import re
import sys
from pathlib import Path

# German: words that make an acceptance criterion unverifiable.
VAGUE = ["besser", "sinnvoll", "schnell", "sauber", "optimal", "angemessen",
         "performant", "robust", "benutzerfreundlich", "modern", "ordentlich"]

# German: phrasings that describe a solution instead of an observation.
SOLUTION = ["cache einbauen", "index anlegen", "redis", "refactor",
            "umstellen auf", "bibliothek einbauen", "queue umstellen"]

# German section headings, because the issues themselves are German.
SECTIONS = {"problem": "Problem", "criteria": "Akzeptanzkriterien",
            "non_goals": "Nicht-Ziele", "context": "Kontext",
            "questions": "Offene Fragen", "slice": "Slice"}



def section(text, name):
    m = re.search(rf"^##\s+{re.escape(name)}\s*$(.*?)(?=^##\s|\Z)", text, re.M | re.S)
    return m.group(1).strip() if m else ""


def meta(text, k):
    m = re.search(rf"^{k}:\s*(.+)$", text, re.M)
    return m.group(1).strip() if m else ""


directory = Path(sys.argv[1] if len(sys.argv) > 1 else ".")
total = passed = 0
print(f"\n{'=' * 62}\n  RUBRIC - issue-erstellen\n{'=' * 62}")

for path in sorted(directory.glob("*.md")):
    t = path.read_text(encoding="utf-8")
    kind, status, size = meta(t, "typ"), meta(t, "status"), meta(t, "groesse")
    problem = section(t, SECTIONS["problem"])
    criteria = section(t, SECTIONS["criteria"])
    non_goals = section(t, SECTIONS["non_goals"])
    context = section(t, SECTIONS["context"])
    questions = section(t, SECTIONS["questions"])
    special = any(x in status for x in ("blockiert", "abgelehnt", "aufgeteilt"))
    e = {}

    e["R1 problem section present"] = (bool(problem) or special,
                                       "" if problem else "special case")
    hits = [w for w in SOLUTION if w in problem.lower()]
    e["R2 problem states no solution"] = (not hits, ", ".join(hits))
    n_crit = len(re.findall(r"^\s*-\s*\[\s*\]", criteria, re.M))
    e["R3 >=2 acceptance criteria"] = (n_crit >= 2 or special, f"found: {n_crit}")
    vague = [w for w in VAGUE if re.search(rf"\b{w}\b", criteria, re.I)]
    e["R4 criteria are verifiable"] = (not vague, ", ".join(vague))
    n_ng = len(re.findall(r"^\s*-\s+\S", non_goals, re.M))
    e["R5 >=2 non-goals"] = (n_ng >= 2, f"found: {n_ng}")
    has_path = bool(re.search(r"(app|src|database|tests)/[\w/]+", context + t))
    e["R6 context anchor with path"] = (has_path or special,
                                        "" if has_path else "special case")
    e["R7 size S/M or split"] = (
        size in ("S", "M") or "AUFGETEILT" in size or "BLOCKIERT" in size,
        f"size: {size}")

    # R10 — feature issues name their slice. ONLY its presence is checked.
    #
    # An earlier version also tried to detect layer-shaped slice sentences by
    # keyword. It failed on its own example: "ohne die Tabelle haendisch zu
    # fuehren" describes the manual process being replaced, not a database
    # table. Whether a slice is genuinely vertical is a human judgement; a
    # keyword list only produces false positives, and a false positive teaches
    # people to ignore the tool.
    #
    # chore and spike are legitimately horizontal (AGENTS.md 2.5) and are not asked.
    if kind == "feature" and not special:
        slice_text = section(t, SECTIONS["slice"])
        e["R10 slice named"] = (bool(slice_text),
                                "" if slice_text else "## Slice missing")

    if kind == "bug":
        repro = bool(re.search(r"^\s*\d\.\s+\S", problem, re.M))
        stated_missing = any(x in problem.lower() for x in ("liegt nicht vor", "unbekannt"))
        e["R8 reproduction given or asked for"] = (
            repro or (stated_missing and bool(questions)),
            "present" if repro else
            ("correctly asked for" if stated_missing and questions
             else "missing and not asked for"))
        if not repro and stated_missing:
            e["R9 no invented reproduction"] = (True, "")

    ok = sum(1 for v in e.values() if v[0])
    total += len(e)
    passed += ok
    print(f"\n  {path.name}   {ok}/{len(e)}")
    for k, (b, note) in e.items():
        print(f"    {'PASS' if b else 'FAIL'} {k:<34} {note}")

print(f"\n{'-' * 62}\n  Total: {passed}/{total} ({passed / max(total, 1) * 100:.1f} %)\n")
sys.exit(0 if passed == total else 1)
