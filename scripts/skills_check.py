#!/usr/bin/env python3
"""
skills_check — validates the repository against the `npx skills` conventions.

The CLI skips a skill whose frontmatter is not valid YAML. It does so silently:
the skill simply never appears in `--list`, and nobody notices until somebody
asks why it did not install. An unquoted colon in the description is enough.

Usage: skills_check.py [root]
"""

import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    sys.exit("PyYAML missing: pip install pyyaml")

# Directories the CLI walks, up to three levels deep.
CONTAINER = "skills"


def check(root: Path) -> list[str]:
    findings: list[str] = []
    container = root / CONTAINER
    if not container.is_dir():
        return [f"{CONTAINER}/ is missing — the CLI would fall back to a recursive search"]

    found: dict[str, Path] = {}
    for p in sorted(container.rglob("SKILL.md")):
        rel = p.relative_to(root)
        depth = len(p.relative_to(container).parts) - 1
        if depth > 2:
            findings.append(f"{rel}: nested {depth} levels below {CONTAINER}/ — the CLI walks at most 2")

        text = p.read_text(encoding="utf-8")
        if not text.startswith("---"):
            findings.append(f"{rel}: no YAML frontmatter")
            continue
        raw = text.split("---", 2)[1]
        try:
            data = yaml.safe_load(raw)
        except Exception as e:
            first = str(e).splitlines()[0]
            findings.append(
                f"{rel}: frontmatter is not valid YAML — {first}. "
                f"The CLI skips this skill without saying so. Quote the description if it contains a colon")
            continue
        if not isinstance(data, dict):
            findings.append(f"{rel}: frontmatter is not a mapping")
            continue
        for field in ("name", "description"):
            if not data.get(field):
                findings.append(f"{rel}: `{field}` is missing — required by the CLI")
        name = data.get("name")
        if name:
            if name != p.parent.name:
                findings.append(f"{rel}: name `{name}` differs from the directory `{p.parent.name}`")
            if name != name.lower() or " " in name:
                findings.append(f"{rel}: name `{name}` must be lowercase without spaces")
            if name in found:
                findings.append(f"{rel}: duplicate name `{name}`, also in {found[name]}")
            found[name] = rel

    if not found:
        findings.append(f"no skill found under {CONTAINER}/")
    return findings


def main() -> int:
    root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
    findings = check(root)
    print(f"\n{'=' * 62}\n  SKILLS CHECK\n{'=' * 62}\n")
    for f in findings:
        print(f"  XX  {f}")
    if not findings:
        n = len(list((root / CONTAINER).rglob("SKILL.md")))
        print(f"  OK  {n} skill(s), all discoverable by `npx skills`\n")
        return 0
    print(f"\n  {len(findings)} finding(s)\n")
    return 1


if __name__ == "__main__":
    sys.exit(main())
