#!/usr/bin/env python3
"""
arch-check — a language-agnostic rule checker.

The engine knows no language and no framework. It loads a profile
(profiles/<stack>.json) that declares three things:

  1. what comments and string literals look like in that language
  2. which paths belong to which layer
  3. the rules, as data rather than code

Supporting a new language means writing a profile. Nothing here changes.

Usage:  arch_check.py <project-root> --profile <name> [--profile-file <path>]
Output: FILE:LINE<TAB>RULE<TAB>PRINCIPLE<TAB>message
Exit 1 when there are findings.

Language note: tools, profiles and fixtures are written in English. Issues and
pull-request descriptions are written in German — see AGENTS.md, "Language".
"""

from __future__ import annotations

import argparse
import fnmatch
import json
import re
import sys
from pathlib import Path

# The eight principles from AGENTS.md. A profile that neither covers one of
# them nor declares it not_applicable reports "0 findings" — indistinguishable
# from a clean codebase. The coverage report exists to close that silent gap.
PRINCIPLES = ["BOUNDARIES", "STATE", "IDEMPOTENCY", "TRANSACTION",
              "IMMUTABILITY", "MIGRATION", "ERRORS", "HYGIENE"]


# ─────────────────────────────────────────────────────────────────────────────
# Source preparation
# ─────────────────────────────────────────────────────────────────────────────


def strip_code(text: str, language: dict) -> list[str]:
    """
    Remove comments and string contents while preserving the line structure.

    Without this step every rule fires on prose that merely mentions
    console.log() or dump() — by far the most common false positive.
    """
    line_comment = language.get("line_comment", ["//"])
    block = [tuple(b) for b in language.get("block_comment", [["/*", "*/"]])]
    quotes = language.get("strings", ["'", '"'])

    out: list[str] = []
    i, n = 0, len(text)
    line: list[str] = []
    in_block: tuple[str, str] | None = None
    in_string: str | None = None

    while i < n:
        c = text[i]

        if c == "\n":
            out.append("".join(line))
            line = []
            i += 1
            continue

        if in_block:
            if text.startswith(in_block[1], i):
                i += len(in_block[1])
                in_block = None
            else:
                i += 1
            continue

        if in_string:
            if c == "\\":
                i += 2
                continue
            if text.startswith(in_string, i):
                i += len(in_string)
                in_string = None
            else:
                i += 1
            continue

        hit = False
        for open_, close_ in block:
            if text.startswith(open_, i):
                in_block = (open_, close_)
                i += len(open_)
                hit = True
                break
        if hit:
            continue

        for marker in line_comment:
            if text.startswith(marker, i):
                while i < n and text[i] != "\n":
                    i += 1
                hit = True
                break
        if hit:
            continue

        for q in quotes:
            if text.startswith(q, i):
                in_string = q
                i += len(q)
                line.append(q + q)  # empty string as a placeholder
                hit = True
                break
        if hit:
            continue

        line.append(c)
        i += 1

    out.append("".join(line))
    return out


class SourceFile:
    def __init__(self, path: Path, relative: str, language: dict):
        self.path = path
        self.relative = relative
        self.raw = path.read_text(encoding="utf-8", errors="replace")
        self.lines = strip_code(self.raw, language)
        # Raw lines stay available: in some languages the signal lives in the
        # string literal (TypeScript import paths) or in the comment
        # (@ts-ignore and similar pragmas). Rules pick their source explicitly.
        self.raw_lines = self.raw.splitlines()

    def scope(self, start: str | None, end: str | None,
              source: str = "code") -> list[tuple[int, str]]:
        """Lines of a named block, e.g. only the up() body of a migration."""
        base = self.raw_lines if source == "raw" else self.lines
        pairs = list(enumerate(base, start=1))
        if not start:
            return pairs
        first = None
        for nr, z in pairs:
            if re.search(start, z):
                first = nr
                break
        if first is None:
            return []
        last = len(base) + 1
        if end:
            for nr, z in pairs:
                if nr > first and re.search(end, z):
                    last = nr
                    break
        return [(nr, z) for nr, z in pairs if first <= nr < last]


# ─────────────────────────────────────────────────────────────────────────────
# Rule evaluation
# ─────────────────────────────────────────────────────────────────────────────


def applies(f: SourceFile, rule: dict) -> bool:
    include = rule.get("applies_to", ["**/*"])
    exclude = rule.get("excludes", [])
    if not any(fnmatch.fnmatch(f.relative, m) for m in include):
        return False
    if any(fnmatch.fnmatch(f.relative, m) for m in exclude):
        return False
    if (skip := rule.get("skip_file_if")) and re.search(skip, f.raw):
        return False
    return True


def check(f: SourceFile, rule: dict) -> list[tuple[int, str]]:
    kind = rule.get("kind", "forbidden")
    pattern = rule.get("pattern", "")
    message = rule.get("message", rule.get("description", ""))
    allowed = set(rule.get("except_values", []))
    source = rule.get("source", "code")
    lines = f.scope(rule.get("scope_from"), rule.get("scope_to"), source)
    window = rule.get("window", 0)
    anchor = rule.get("anchor")
    findings: list[tuple[int, str]] = []

    def text_from(idx: int) -> str:
        """
        Current line plus following lines — for rules whose statement spans
        several lines (e.g. .then without .catch).

        window = "statement" reaches to the end of the statement. A fixed line
        window is useless here: one blank line shifts it and the rule fires
        where it has no business firing.

        Caveat: "statement" ends at a semicolon and is therefore only usable in
        languages that have one. In Python and similar, use a single-line check
        or a fixed window.
        """
        if window == "statement":
            parts = []
            for _, z in lines[idx:idx + 20]:
                parts.append(z)
                if ";" in z:
                    break
            return " ".join(parts)
        if isinstance(window, int) and window > 0:
            return " ".join(z for _, z in lines[idx:idx + window + 1])
        return lines[idx][1]

    if kind == "forbidden":
        for idx, (nr, own_line) in enumerate(lines):
            # The anchor must sit on THIS line. The window only inspects the
            # surroundings; it never locates the finding.
            if anchor and not re.search(anchor, own_line):
                continue
            z = text_from(idx)
            m = re.search(pattern, z)
            if not m:
                continue
            if allowed and m.groups() and m.group(1) in allowed:
                continue
            captured = m.group(1) if m.groups() else ""
            findings.append((nr, message.replace("{0}", captured)))
            if rule.get("first_only", True):
                break

    elif kind == "required":
        if not any(re.search(pattern, z) for _, z in lines):
            findings.append((1, message))

    elif kind == "conditional":
        # If `condition` matches, `pattern` must appear as well.
        condition = rule["condition"]
        if any(re.search(condition, z) for _, z in lines):
            if not any(re.search(pattern, z) for _, z in lines):
                at = next((nr for nr, z in lines if re.search(condition, z)), 1)
                findings.append((at, message))

    elif kind == "in_block":
        # `pattern` must not appear inside a block opened by `block_start`.
        start = rule["block_start"]
        bracket = rule.get("bracket", "(")
        closing = {"(": ")", "{": "}"}[bracket]
        open_block = False
        depth = 0
        for nr, z in lines:
            if not open_block and re.search(start, z):
                if (ig := rule.get("block_ignore")) and re.search(ig, z):
                    continue
                open_block = True
                depth = z.count(bracket) - z.count(closing)
                continue
            if not open_block:
                continue
            depth += z.count(bracket) - z.count(closing)
            if re.search(pattern, z):
                findings.append((nr, message))
                open_block = False
                continue
            if depth <= 0:
                open_block = False

    return findings


# ─────────────────────────────────────────────────────────────────────────────


def coverage(profile: dict) -> tuple[list[str], list[str], list[str]]:
    covered = {r.get("principle") for r in profile["rules"]}
    declared = set(profile.get("not_applicable", []))
    missing = [p for p in PRINCIPLES if p not in covered and p not in declared]
    return sorted(covered & set(PRINCIPLES)), sorted(declared), missing


def load_profile(name: str, file: Path | None) -> dict:
    # Two layouts are supported: profiles/<name>.json next to this file (what the
    # installer writes into a project) and ../../stacks/<name>/<name>.json (the
    # source layout inside the skill directory). One source of truth, two shapes.
    here = Path(__file__).parent
    path = file or next(
        (c for c in (here / "profiles" / f"{name}.json",
                     here.parents[1] / "stacks" / name / f"{name}.json") if c.exists()),
        here / "profiles" / f"{name}.json",
    )
    if not path.exists():
        sys.exit(f"profile not found: {path}")
    profile = json.loads(path.read_text(encoding="utf-8"))
    for parent in profile.get("inherits", []):
        base = load_profile(parent, None)
        profile["rules"] = base.get("rules", []) + profile.get("rules", [])
        for k, v in base.items():
            profile.setdefault(k, v)
    return profile


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("root")
    ap.add_argument("--profile", required=True)
    ap.add_argument("--profile-file", type=Path, default=None)
    ap.add_argument("--quiet", action="store_true")
    ap.add_argument("--coverage", action="store_true",
                    help="report principle coverage only")
    args = ap.parse_args()

    profile = load_profile(args.profile, args.profile_file)
    covered, declared, missing = coverage(profile)
    if args.coverage:
        print(f"profile '{profile['name']}' — principle coverage")
        print(f"  covered        : {', '.join(covered)}")
        print(f"  not applicable : {', '.join(declared) or '—'}")
        print(f"  NO RULE AT ALL : {', '.join(missing) or '—'}")
        return 1 if missing else 0

    language = profile.get("language", {})
    extensions = tuple(profile.get("extensions", [".php"]))
    ignore = profile.get("ignore", ["**/node_modules/**", "**/vendor/**", "**/tools/**"])

    root = Path(args.root).resolve()
    files = []
    for p in sorted(root.rglob("*")):
        if not p.is_file() or not p.name.endswith(extensions):
            continue
        rel = str(p.relative_to(root))
        if any(fnmatch.fnmatch(rel, m) for m in ignore):
            continue
        files.append(SourceFile(p, rel, language))

    findings = []
    for f in files:
        for rule in profile["rules"]:
            if not applies(f, rule):
                continue
            for nr, message in check(f, rule):
                findings.append((f.relative, nr, rule["id"],
                                 rule.get("principle", "-"), message))

    findings.sort(key=lambda b: (b[0], b[1]))
    for rel, nr, rid, principle, message in findings:
        print(f"{rel}:{nr}\t{rid}\t{principle}\t{message}")

    if not args.quiet:
        print(f"\n{len(files)} file(s), {len(findings)} finding(s), "
              f"{len(profile['rules'])} rule(s), profile '{profile['name']}'.",
              file=sys.stderr)
        if missing:
            print(f"WARNING: principle(s) with no rule at all: {', '.join(missing)}. "
                  f"'0 findings' says nothing about them.", file=sys.stderr)
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
