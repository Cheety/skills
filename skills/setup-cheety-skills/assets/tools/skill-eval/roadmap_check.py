#!/usr/bin/env python3
"""
roadmap_check — checks the milestone plans produced by the `split-spec` skill.

A specification is split into milestones, milestones into issues. The issues go
into the tracker and get closed; the milestone plan stays in the repository,
because it carries the one thing an issue has no field for: what has to be built
before what, and what breaks when that order is violated.

That ordering is exactly what decays. Nobody notices a dangling reference, and a
plan whose milestones are written in an unbuildable order still looks like a
plan. This checker reads the document as a graph and says so.

Language note: the headings it matches are GERMAN, because roadmaps and issues
in this project are German (see AGENTS.md, "Language"). Everything else here is
English.

Usage:
  roadmap_check.py <directory-or-file>    check the roadmaps of this project
  roadmap_check.py --self-test            prove the rules against the fixtures
"""

import re
import sys
from pathlib import Path

HERE = Path(__file__).parent

# German headings, because the artifact is German.
RE_MILESTONE = re.compile(r"^##\s+([A-Z]+\d+)\s*[—–-]\s*(.+?)\s*$")
RE_BLOCKED = re.compile(r"^Blockiert von:\s*(.*)$")
RE_DOD = re.compile(r"^Definition of Done:\s*(.*)$")
RE_COMMENT = re.compile(r"<!--.*?-->")
RE_ID = re.compile(r"\b([A-Z]+\d+)\b")

# "nothing blocks this" — the only accepted ways to say it.
NOTHING = {"—", "–", "-", "keine", "keines", "none", "nichts"}

KINDS = {"bug", "feature", "chore", "spike"}
SIZES = {"s", "m"}


def findings_for(path: Path, text: str) -> list[tuple[int, str, str]]:
    """Returns (line, rule, message). Line numbers are 1-based."""
    out: list[tuple[int, str, str]] = []
    raw = text.splitlines()
    lines = [RE_COMMENT.sub("", z).rstrip() for z in raw]

    # ── frontmatter ─────────────────────────────────────────────────────────
    front: dict[str, tuple[int, str]] = {}
    if lines and lines[0].strip() == "---":
        for i, z in enumerate(lines[1:], 2):
            if z.strip() == "---":
                break
            if ":" in z:
                k, v = z.split(":", 1)
                front[k.strip().lower()] = (i, v.split("#", 1)[0].strip())

    typ_line, typ = front.get("typ", (1, ""))
    if typ != "roadmap":
        out.append((typ_line, "RM_TYP",
                    f"frontmatter `typ` is '{typ or 'missing'}', expected 'roadmap'"))
    quelle_line, quelle = front.get("quelle", (1, ""))
    if not quelle:
        out.append((quelle_line, "RM_QUELLE",
                    "frontmatter `quelle` is empty — a roadmap without its specification "
                    "cannot be checked against the document it came from"))

    # ── milestones ──────────────────────────────────────────────────────────
    stones: list[dict] = []
    for i, z in enumerate(lines, 1):
        if m := RE_MILESTONE.match(z):
            stones.append({"id": m.group(1), "name": m.group(2), "line": i,
                           "blocked": None, "blocked_line": None,
                           "dod": False, "rows": []})
        elif stones:
            cur = stones[-1]
            if m := RE_BLOCKED.match(z):
                cur["blocked"] = m.group(1).strip()
                cur["blocked_line"] = i
            elif m := RE_DOD.match(z):
                cur["dod"] = bool(m.group(1).strip())
            elif z.lstrip().startswith("|"):
                cells = [c.strip() for c in z.split("|")[1:-1]]
                head = [c.lower() for c in cells]
                separator = all(set(c) <= set("-: ") and c for c in cells)
                header = "issue" in head or "typ" in head
                if cells and not separator and not header:
                    cur["rows"].append((i, cells))

    if not stones:
        # File-level findings are reported on the last line: line 1 is the
        # frontmatter fence and cannot carry a fixture marker.
        out.append((len(lines), "RM_NO_MILESTONE",
                    "no milestone found — headings must read `## M0 — Name`"))
        return out

    order: dict[str, int] = {}
    for idx, s in enumerate(stones):
        if s["id"] in order:
            out.append((s["line"], "RM_DUPLICATE_ID",
                        f"milestone id `{s['id']}` was already used in line {stones[order[s['id']]]['line']}"))
        else:
            order[s["id"]] = idx
    known = set(order)

    # ── edges ───────────────────────────────────────────────────────────────
    edges: dict[str, list[str]] = {}
    for s in stones:
        value = s["blocked"]
        if value is None:
            out.append((s["line"], "RM_NO_BLOCKED_BY",
                        f"{s['id']} has no `Blockiert von:` line — write `—` when nothing blocks it, "
                        "an absent line reads as 'not thought about yet'"))
            edges[s["id"]] = []
            continue
        if not value:
            out.append((s["blocked_line"], "RM_NO_BLOCKED_BY",
                        f"{s['id']} has an empty `Blockiert von:` — write `—` when nothing blocks it"))
            edges[s["id"]] = []
            continue
        if value.lower() in NOTHING:
            edges[s["id"]] = []
            continue
        targets = RE_ID.findall(value)
        if not targets:
            out.append((s["blocked_line"], "RM_DANGLING",
                        f"{s['id']}: `Blockiert von: {value}` names no milestone id"))
        edges[s["id"]] = [t for t in targets if t in known]
        for t in targets:
            if t not in known:
                out.append((s["blocked_line"], "RM_DANGLING",
                            f"{s['id']} is blocked by `{t}`, which no milestone declares"))

    # ── cycles ──────────────────────────────────────────────────────────────
    in_cycle: set[str] = set()
    state: dict[str, int] = {}

    def visit(node: str, stack: list[str]) -> None:
        state[node] = 1
        stack.append(node)
        for nxt in edges.get(node, []):
            if state.get(nxt) == 1:
                in_cycle.update(stack[stack.index(nxt):])
            elif not state.get(nxt):
                visit(nxt, stack)
        stack.pop()
        state[node] = 2

    for s in stones:
        if not state.get(s["id"]):
            visit(s["id"], [])

    reported: set[str] = set()
    for s in stones:
        if s["id"] in in_cycle and s["id"] not in reported:
            ring = sorted(in_cycle)
            reported.update(in_cycle)
            out.append((s["blocked_line"] or s["line"], "RM_CYCLE",
                        f"circular dependency between {', '.join(ring)} — no order can satisfy this"))

    # ── declaration order must be a build order ─────────────────────────────
    for s in stones:
        if s["id"] in in_cycle:
            continue
        for t in edges.get(s["id"], []):
            if t in in_cycle or t not in order:
                continue
            if order[t] > order[s["id"]]:
                out.append((s["blocked_line"], "RM_FORWARD_REF",
                            f"{s['id']} is blocked by {t}, which is written further down — "
                            "top to bottom has to be the build order"))

    # ── the backlog rows ────────────────────────────────────────────────────
    for s in stones:
        if not s["dod"]:
            out.append((s["line"], "RM_NO_DOD",
                        f"{s['id']} has no `Definition of Done:` — a milestone without one "
                        "cannot be finished, only abandoned"))
        if not s["rows"]:
            out.append((s["line"], "RM_NO_ISSUES",
                        f"{s['id']} lists no issues — a milestone without a backlog table is a heading"))
        for line, cells in s["rows"]:
            if len(cells) < 4 or not all(cells[:4]):
                out.append((line, "RM_ROW",
                            "backlog row needs four filled columns: Issue, Typ, Groesse, "
                            "Nuetzlich ohne den Rest?"))
                continue
            title, kind, size, useful = cells[0], cells[1].lower(), cells[2].lower(), cells[3].lower()
            if kind not in KINDS:
                out.append((line, "RM_KIND",
                            f"`{cells[1]}` is not a kind — one of {', '.join(sorted(KINDS))}"))
            if size not in SIZES:
                out.append((line, "RM_SIZE",
                            f"`{cells[2]}` is not a size — L is not written but decomposed"))
            # AGENTS.md 2.5: chore and spike are legitimately horizontal, a feature is not.
            if kind == "feature" and (useful.startswith("nein") or useful.startswith("no")):
                out.append((line, "RM_LAYER_SPLIT",
                            f"feature `{title}` is not useful on its own — that is a layer, "
                            "decompose it again or admit it is a chore"))
    return out


def check(paths: list[Path], root: Path) -> int:
    total = 0
    for p in paths:
        text = p.read_text(encoding="utf-8")
        for line, rule, message in sorted(findings_for(p, text)):
            rel = p.relative_to(root) if p.is_relative_to(root) else p
            print(f"{rel}:{line}\t{rule}\t{message}")
            total += 1
    return total


def collect(target: Path) -> list[Path]:
    if target.is_file():
        return [target]
    return sorted(target.rglob("*.md"))


def self_test() -> int:
    root = HERE / "fixtures" / "roadmap"
    if not root.is_dir():
        sys.exit(f"fixtures not found: {root}")

    expected: dict[str, int] = {}
    for p in sorted(root.glob("*.md")):
        for i, z in enumerate(p.read_text(encoding="utf-8").splitlines(), 1):
            # findall, not search: one line may plant two violations.
            for rule in re.findall(r"!!\s+([A-Z_]+)", z):
                expected[f"{p.name}::{rule}::{i}"] = 1

    found: dict[str, int] = {}
    for p in sorted(root.glob("*.md")):
        for line, rule, _ in findings_for(p, p.read_text(encoding="utf-8")):
            found[f"{p.name}::{rule}::{line}"] = 1

    missed = sorted(set(expected) - set(found))
    false_positive = sorted(set(found) - set(expected))
    ok = len(expected) - len(missed)

    print(f"\n{'=' * 62}\n  ROADMAP CHECK — self-test\n{'=' * 62}\n")
    print(f"  planted violations : {len(expected)}")
    print(f"  detected           : {ok}  ({ok / max(len(expected), 1) * 100:.1f} %)")
    print(f"  missed             : {len(missed)}")
    print(f"  false positives    : {len(false_positive)}\n")
    for k in missed:
        print(f"  MISS  {k}")
    for k in false_positive:
        print(f"  FP    {k}")
    if missed or false_positive:
        print("\n  A rule without a clean counter-example is not finished: a false positive\n"
              "  teaches people to bypass the tool, a missing rule does not.\n")
        return 1
    print("  OK  every planted violation found, no false positive\n")
    return 0


def main() -> int:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if "--self-test" in sys.argv:
        return self_test()

    target = Path(args[0] if args else "docs/roadmap").resolve()
    if not target.exists():
        print(f"  --  no roadmap at {target} — nothing to check")
        return 0

    root = target if target.is_dir() else target.parent
    files = collect(target)
    print(f"\n{'=' * 62}\n  ROADMAP CHECK\n{'=' * 62}\n")
    n = check(files, root)
    if n:
        print(f"\n  {n} finding(s) in {len(files)} file(s)\n")
        return 1
    print(f"  OK  {len(files)} roadmap file(s), ordering is buildable\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
