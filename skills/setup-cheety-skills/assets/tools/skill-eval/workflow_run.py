#!/usr/bin/env python3
"""
workflow_run — runs the full harness cycle for a project and verifies every
step mechanically.

Per work item:
  SCAFFOLD → commit "Geruest:"       (features only)
  RED      → tests run and MUST fail; EVERY new test must be red
  COMMIT   → "Test:"
  GREEN    → implementation, tests MUST pass
  COMMIT   → "Impl:" or "Fix:"
  CHECKER  → arch_check against the profile, 0 findings

Every project's test runner honours the same output contract:
  "OK <name>" or "XX <name>" per test, exit code 0 when green.
That contract makes the tautology check ("every new test must be red")
automatable across languages; it used to be a manual step.

Language note: this tool is English. The issue content inside each project's
spec.py is German on purpose — issues are written in German (AGENTS.md).
"""

from __future__ import annotations

import argparse
import importlib.util
import re
import shutil
import subprocess
import sys
from pathlib import Path

HIER = Path(__file__).parent
WURZEL = HIER.parent.parent


def sh(cmd: str, cwd: Path) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)


def test_names(ausgabe: str) -> dict[str, bool]:
    """Contract: 'OK <name>' = pass, 'XX <name>' = fail."""
    results: dict[str, bool] = {}
    for zeile in ausgabe.splitlines():
        if m := re.match(r"\s*(OK|XX)\s+(.+?)\s*$", zeile):
            results[m.group(2)] = m.group(1) == "OK"
    return results


def apply_edits(repo: Path, edits: list) -> None:
    for file, anchor, replacement in edits:
        p = repo / file
        if anchor == "@create":
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(replacement, encoding="utf-8")
        elif anchor is None:
            with p.open("a", encoding="utf-8") as f:
                f.write(replacement)
        else:
            s = p.read_text(encoding="utf-8")
            if anchor not in s:
                raise RuntimeError(f"anchor text not found in {file}: {anchor[:60]!r}")
            p.write_text(s.replace(anchor, replacement, 1), encoding="utf-8")


def render_issue(item: dict) -> str:
    """Renders the issue file.

    The spec keys are English (tooling); the rendered issue is German,
    because issues are ticket content — see AGENTS.md, "Language".
    """
    lines = ["---", f"id: {item['id']}", f"typ: {item['issue_type']}",
         f"groesse: {item.get('size', 'S')}", "status: bereit", "---", "",
         f"# {item['title']}", "", "## Problem", "",
         item["problem"].replace("\\n", "\n"), "",
         "## Akzeptanzkriterien", ""]
    lines += [f"- [ ] {k}" for k in item["criteria"]]
    lines += ["", "## Nicht-Ziele", ""]
    lines += [f"- {n}" for n in item["non_goals"]]
    lines += ["", "## Kontext", "", item["context"], ""]
    if item.get("questions"):
        lines += ["## Offene Fragen", ""] + [f"- [ ] {f}" for f in item["questions"]] + [""]
    return "\n".join(lines)


def run_project(spec_path: Path, issue_dir: Path) -> tuple[int, int, list[str]]:
    spec = importlib.util.spec_from_file_location("spec", spec_path)
    modul = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modul)
    P = modul.PROJECT

    repo = spec_path.parent / "repo"
    if repo.exists():
        shutil.rmtree(repo)
    repo.mkdir(parents=True)
    sh("git init -q && git config user.email t@t && git config user.name T", repo)
    apply_edits(repo, P["base"])
    sh("git add -A && git commit -qm 'Basis'", repo)

    r = sh(P["test_command"], repo)
    if r.returncode != 0:
        return 0, 0, [f"{P['name']}: baseline suite is not green — aborting\n{r.stdout}{r.stderr}"]
    # Exit code 0 alone is not enough: a runner that dies silently also reports
    # 0 and produces zero results. An empty suite is not green, it is broken —
    # and it would make every following red check worthless.
    if not test_names(r.stdout):
        return 0, 0, [f"{P['name']}: baseline suite produced zero test results "
                      f"(output contract violated or runner dies silently)\n{r.stdout}{r.stderr}"]

    passed = total = 0
    failures: list[str] = []
    issue_dir.mkdir(parents=True, exist_ok=True)

    for item in P["items"]:
        before = set(test_names(sh(P["test_command"], repo).stdout))
        sha_vor = sh("git rev-parse HEAD", repo).stdout.strip()
        tag = {"bugfix": "Fix:", "characterization": "Doku:"}.get(item["type"], "Impl:")
        checks: list[tuple[str, bool, str]] = []

        (issue_dir / f"{item['id']}.md").write_text(render_issue(item), encoding="utf-8")

        if item.get("scaffold"):
            apply_edits(repo, item["scaffold"])
            sh(f"git add -A && git commit -qm 'Scaffold: {item['title']} ({item['id']})'", repo)

        # -- RED / CHARACTERIZATION --
        apply_edits(repo, item["test"])
        rot = sh(P["test_command"], repo)
        resultsse = test_names(rot.stdout)
        new_tests = {k: v for k, v in resultsse.items() if k not in before}
        checks.append(("new tests present", len(new_tests) > 0, f"{len(new_tests)}"))

        if item.get("characterization"):
            # A test that records already-correct behaviour CANNOT be red. The proof
            # runs through a mutation instead: break the production logic and the
            # test must turn red. Without that proof it may be tautological.
            checks.append(("all new tests green (characterization)",
                               all(new_tests.values()), ", ".join(k for k, v in new_tests.items() if not v)))
            backup = {d: (repo / d).read_text() for d, _, _ in item["mutation"]}
            apply_edits(repo, item["mutation"])
            mut = sh(P["test_command"], repo)
            mut_replacemente = {k: v for k, v in test_names(mut.stdout).items() if k in new_tests}
            checks.append(("mutation proof: test turns red",
                               mut.returncode != 0 and not all(mut_replacemente.values()),
                               ", ".join(k for k, v in mut_replacemente.items() if v) or "ok"))
            for d, inhalt in backup.items():
                (repo / d).write_text(inhalt)
        else:
            checks.append(("suite is red", rot.returncode != 0, f"exit={rot.returncode}"))
            gruen_obwohl_leer = [k for k, v in new_tests.items() if v]
            checks.append(("every new test is red (no tautology)",
                               not gruen_obwohl_leer, ", ".join(gruen_obwohl_leer)))
            checks.append(("no missing-symbol error in the red run",
                               not re.search(r"not found|undefined (method|function)|Cannot find|error TS2304|cannot find symbol",
                                             rot.stdout + rot.stderr, re.I), ""))

        commit_tag = "Doku:" if item.get("characterization") else "Test:"
        sh(f"git add -A && git commit -qm '{commit_tag} {item['title']} ({item['id']})'", repo)
        test_fileen = sh("git show --name-only --format= HEAD", repo).stdout.split()
        checks.append(("test commit has no production code",
                           all(d.startswith(P["test_prefix"]) for d in test_fileen),
                           ", ".join(test_fileen)))

        # -- GREEN --
        # A characterization item has no implementation phase: the Doku commit is
        # the entire contribution. An empty Impl commit would only distort the
        # history and point the next check at the test commit.
        if not item.get("characterization"):
            apply_edits(repo, item.get("impl", []))
            gr = sh(P["test_command"], repo)
            checks.append(("suite is green", gr.returncode == 0, f"exit={gr.returncode}"))
            sh(f"git add -A && git commit -qm '{tag} {item['title']} ({item['id']})'", repo)
            impl_fileen = sh("git show --name-only --format= HEAD", repo).stdout.split()
            checks.append(("implementation changes no tests",
                               not any(d.startswith(P["test_prefix"]) for d in impl_fileen),
                               ", ".join(impl_fileen)))

            # Diff budget from AGENTS.md: the estimate comes from the plan. A factor
            # above 2 requires an explanation, it is not automatically wrong —
            # the driver surfaces the deviation rather than judging it.
            if (estimate := item.get("estimated_lines")):
                span = f"{sha_vor}..HEAD" if sha_vor else "HEAD"
                stat = sh(f"git diff --shortstat {span}", repo).stdout
                actual = sum(int(x) for x in re.findall(r"(\d+) [id]", stat)) or 0
                checks.append((f"diff within budget (estimated {estimate})",
                                   actual <= estimate * 2,
                                   f"actual {actual} lines, factor {actual/max(estimate,1):.1f}"))
                checks.append(("at most 8 files touched",
                                   len(set(test_fileen) | set(impl_fileen)) <= 8,
                                   f"{len(set(test_fileen) | set(impl_fileen))} file(s)"))

        # -- CHECKER --
        # ABSOLUTE path. With a relative path and a cwd set, the checker inspects a
        # directory that does not exist, finds zero files and reports exit 0 —
        # a silent all-clear across every work item.
        a = sh(f"{sys.executable} {WURZEL}/tools/arch-check/arch_check.py {repo.resolve()} "
               f"--profile {P['profile']}", repo)
        scanned = 0
        if m := re.search(r"(\d+) file\(s\)", a.stderr):
            scanned = int(m.group(1))
        checks.append(("checker actually saw files", scanned > 0, f"{scanned} file(s)"))
        checks.append(("checker reports no findings", a.returncode == 0,
                           a.stdout.strip().splitlines()[0] if a.stdout.strip() else ""))

        ok = sum(1 for _, b, _ in checks if b)
        total += len(checks)
        passed += ok
        status = "OK " if ok == len(checks) else "XX "
        print(f"  {status} {item['id']:<10} {item['type']:<12} {ok}/{len(checks)}  {item['title'][:44]}")
        for n, b, d in checks:
            if not b:
                zeile = f"      → {n}: {d}"
                print(zeile)
                failures.append(f"{P['name']}/{item['id']}: {n} — {d}")

    return passed, total, failures


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("projects", nargs="+", type=Path)
    ap.add_argument("--issues", type=Path, default=HIER / "results" / "issues-run")
    a = ap.parse_args()

    gb = gg = 0
    alle: list[str] = []
    for pfad in a.projects:
        spec = pfad / "spec.py" if pfad.is_dir() else pfad
        print(f"\n── {spec.parent.name} " + "─" * (54 - len(spec.parent.name)))
        b, g, f = run_project(spec, a.issues / spec.parent.name)
        gb += b
        gg += g
        alle += f

    print(f"\n{'='*62}")
    print(f"  {gb}/{gg} checks passed ({gb/max(gg,1)*100:.1f} %)")
    if alle:
        print(f"\n  {len(alle)} failure(s):")
        for f in alle:
            print(f"    - {f}")
    print()
    return 0 if gb == gg else 1


if __name__ == "__main__":
    sys.exit(main())
