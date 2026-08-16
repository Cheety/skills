#!/usr/bin/env python3
"""
forge-check — validates the forge configuration of a project.

The harness ships for three forges, and their CI dialects are close enough that
a file copied from one to the next *almost* works. The differences fail
silently, which is why they are checked mechanically:

  Forgejo   `uses: actions/checkout@v4` is prefixed with the instance's
            DEFAULT_ACTIONS_URL and breaks on the next instance.
  GitHub    `uses: https://…` is not resolvable at all, and `runs-on: docker`
            names a runner GitHub does not have.
  GitLab    no Actions syntax whatsoever, one pipeline file, and a job whose
            `stage:` is not declared is never scheduled.

An installed project carries exactly one forge; the source repository carries
all three as installer assets. Both are handled: directories are looked up with
and without their leading dot, because a dot-directory inside a skill payload
would be installed as one.

Usage: forge_check.py [root] [--forge forgejo|github|gitlab]
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    sys.exit("PyYAML missing: pip install pyyaml")

FIELD_TYPES = {"markdown", "input", "textarea", "dropdown", "checkboxes"}
GITHUB_LABELS = {"ubuntu-latest", "ubuntu-22.04", "ubuntu-24.04",
                 "windows-latest", "macos-latest"}
FORGEJO_LABELS = {"docker", "self-hosted", "lxc", "host"}

# Every issue template has to ask for non-goals — the single most effective
# measure against over-engineering. Forgejo and GitHub carry it as a field id,
# GitLab as a heading, because GitLab has no issue forms.
NON_GOAL_ID = "nichtziele"
NON_GOAL_HEADING = "nicht-ziele"


def code_lines(text: str) -> list[tuple[int, str]]:
    """Lines without comments. Without this step every rule fires on prose that
    merely mentions the case — the most common false positive."""
    out = []
    for nr, line in enumerate(text.splitlines(), 1):
        without = re.sub(r"(?<!\S)#.*$", "", line)
        if without.strip():
            out.append((nr, without))
    return out


def load(path: Path, findings: list[str], root: Path):
    try:
        return yaml.safe_load(path.read_text(encoding="utf-8"))
    except Exception as e:
        findings.append(f"{path.relative_to(root)}: invalid YAML — {e}")
        return None


def base_dir(root: Path, name: str) -> Path | None:
    for candidate in (root / f".{name}", root / name):
        if candidate.is_dir():
            return candidate
    return None


# ── Actions-style workflows (Forgejo and GitHub) ────────────────────────────


def check_actions_workflows(base: Path, root: Path, forge: str) -> list[str]:
    findings: list[str] = []
    wf = base / "workflows"
    if not wf.is_dir():
        return [f"{base.name}/workflows/ is missing"]

    for p in sorted(wf.glob("*.y*ml")):
        rel = p.relative_to(root)
        text = p.read_text(encoding="utf-8")
        d = load(p, findings, root)
        if d is None:
            continue

        for nr, line in code_lines(text):
            s = line.strip()
            if s.startswith("- uses:") or s.startswith("uses:"):
                value = s.split("uses:", 1)[1].strip()
                if forge == "forgejo" and not value.startswith(("https://", "./")):
                    findings.append(
                        f"{rel}:{nr}: `uses: {value}` is a shorthand. It is prefixed with the "
                        f"instance's DEFAULT_ACTIONS_URL and is therefore not portable — "
                        f"use the full URL")
                if forge == "github" and value.startswith("https://"):
                    findings.append(
                        f"{rel}:{nr}: `uses: {value}` is Forgejo syntax. GitHub resolves "
                        f"actions as owner/repo@ref and cannot fetch a URL")

            labels = FORGEJO_LABELS if forge == "github" else GITHUB_LABELS
            other = "Forgejo" if forge == "github" else "GitHub"
            for lab in labels:
                if re.search(rf"runs-on:\s*\[?\s*['\"]?{re.escape(lab)}\b", s):
                    hint = ("GitHub offers ubuntu-latest, windows-latest or macos-latest"
                            if forge == "github"
                            else "Forgejo runners usually register as `docker` or with a custom label")
                    findings.append(
                        f"{rel}:{nr}: runner label `{lab}` comes from {other}. {hint}")

        for name, job in (d.get("jobs") or {}).items():
            if "runs-on" not in job:
                findings.append(f"{rel}: job `{name}` has no runs-on")
            if forge == "forgejo":
                findings += check_node_in_container(rel, name, job)
                findings += check_service_ports(rel, name, job)

    return findings


# Images known to carry a node binary. Everything else is assumed not to.
NODE_CAPABLE = ("node", "runner-images", "catthehacker", "act-")


def check_node_in_container(rel: Path, name: str, job: dict) -> list[str]:
    """A JavaScript action needs node *inside the job container*.

    GitHub mounts the runner's own node into the container, so this never comes
    up there. Forgejo does not: the action is started with whatever `node` the
    image provides, and a python/php/golang image provides none. The run then
    dies with `exec: "node": executable file not found in $PATH` — at runtime,
    on a green-looking workflow file.
    """
    image = str(((job.get("container") or {}) if isinstance(job.get("container"), dict)
                 else {"image": job.get("container")}).get("image") or "")
    if not image or any(m in image for m in NODE_CAPABLE):
        return []
    uses = [s["uses"] for s in (job.get("steps") or [])
            if isinstance(s, dict) and s.get("uses") and not str(s["uses"]).startswith("docker://")]
    if not uses:
        return []
    return [f"{rel}: job `{name}` runs in `{image}`, which carries no node, but uses "
            f"the JavaScript action `{uses[0]}`. Forgejo does not provide node inside "
            f"the container — use a node-based image or replace the action with a run step"]


def check_service_ports(rel: Path, name: str, job: dict) -> list[str]:
    """`ports:` on a service publishes it on the *runner host*.

    On GitHub that host is a fresh VM per job, so nobody notices. A Forgejo
    runner is long-lived and runs several jobs at once: the second one to ask
    for 5432 dies before the first step, with

        Bind for 127.0.0.1:6379 failed: port is already allocated

    which reads like a broken runner rather than a workflow bug. The mapping
    buys nothing either — the job container shares a network with the services
    and reaches them by service name on the container port.
    """
    findings = []
    services = job.get("services")
    if not isinstance(services, dict):
        return []
    for svc, spec in services.items():
        if isinstance(spec, dict) and spec.get("ports"):
            findings.append(
                f"{rel}: job `{name}` publishes `ports:` for service `{svc}`. A Forgejo "
                f"runner is a shared host — a second concurrent job fails with `port is "
                f"already allocated`. Drop `ports:` and reach the service by its name")
    return findings


def check_actions_issue_templates(base: Path, root: Path, forge: str) -> list[str]:
    findings: list[str] = []
    # Forgejo reads issue_template/, GitHub reads ISSUE_TEMPLATE/.
    wanted = "issue_template" if forge == "forgejo" else "ISSUE_TEMPLATE"
    it = next((c for c in (base / wanted, base / wanted.lower(), base / wanted.upper())
               if c.is_dir()), None)
    if it is None:
        return [f"{base.name}/{wanted}/ is missing"]
    if it.name != wanted:
        findings.append(
            f"{it.relative_to(root)}: directory is named `{it.name}`, {forge} reads `{wanted}`")

    # Forgejo describes a template with `about:`, GitHub with `description:`.
    key, wrong = ("about", "description") if forge == "forgejo" else ("description", "about")

    for p in sorted(it.glob("*.y*ml")):
        rel = p.relative_to(root)
        d = load(p, findings, root)
        if d is None:
            continue

        if p.stem == "config":
            if "blank_issues_enabled" not in d:
                findings.append(
                    f"{rel}: blank_issues_enabled missing — blank issues stay possible")
            continue

        if wrong in d and key not in d:
            findings.append(f"{rel}: `{wrong}:` is the other forge's syntax; expected `{key}:`")
        if key not in d:
            findings.append(f"{rel}: `{key}:` is missing")

        for field in d.get("body") or []:
            typ = field.get("type")
            if typ not in FIELD_TYPES:
                findings.append(f"{rel}: unknown field type `{typ}`")
            if typ != "markdown" and "id" not in field:
                label = (field.get("attributes") or {}).get("label", "?")
                findings.append(f"{rel}: field `{label}` has no id")

        ids = {f.get("id") for f in (d.get("body") or [])}
        if NON_GOAL_ID not in ids:
            findings.append(
                f"{rel}: no `{NON_GOAL_ID}` field. Non-goals are a required field per "
                f"AGENTS.md and the single most effective measure against over-engineering")

    if not list(it.glob("*.y*ml")):
        findings.append(f"{it.relative_to(root)}: no issue templates")
    return findings


def check_forgejo(root: Path) -> list[str] | None:
    base = base_dir(root, "forgejo")
    if base is None:
        return None
    findings = check_actions_workflows(base, root, "forgejo")
    findings += check_actions_issue_templates(base, root, "forgejo")
    findings += check_pr_template(base / "pull_request_template.md", root)
    return findings


def check_github(root: Path) -> list[str] | None:
    base = base_dir(root, "github")
    if base is None:
        return None
    findings = check_actions_workflows(base, root, "github")
    findings += check_actions_issue_templates(base, root, "github")
    findings += check_pr_template(base / "pull_request_template.md", root)
    return findings


def check_pr_template(pr: Path, root: Path) -> list[str]:
    if not pr.is_file():
        return [f"{pr.relative_to(root)} is missing"]
    if "Stufe-0" not in pr.read_text(encoding="utf-8"):
        return [f"{pr.relative_to(root)} has no stage-0 checklist"]
    return []


# ── GitLab ──────────────────────────────────────────────────────────────────


def check_gitlab(root: Path) -> list[str] | None:
    base = base_dir(root, "gitlab")
    if base is None:
        return None
    findings: list[str] = []

    # Installed: .gitlab-ci.yml at the repository root. As an installer asset the
    # same file lives inside the payload, still carrying the include placeholder.
    entry = next((c for c in (root / ".gitlab-ci.yml", base / "gitlab-ci.yml") if c.is_file()), None)
    if entry is None:
        findings.append(".gitlab-ci.yml is missing — GitLab reads exactly one pipeline file")
    else:
        findings += check_gitlab_pipeline(entry, base, root)

    for name in ("ci", "issue_templates", "merge_request_templates"):
        if not (base / name).is_dir():
            findings.append(f"{base.name}/{name}/ is missing")

    for p in sorted((base / "ci").glob("*.y*ml")) if (base / "ci").is_dir() else []:
        rel = p.relative_to(root)
        d = load(p, findings, root)
        if d is None:
            continue
        findings += check_gitlab_actions_leftovers(p, rel)
        for name, job in d.items():
            if name.startswith(".") or name in {"variables", "workflow", "include",
                                                "stages", "default"}:
                continue
            if not isinstance(job, dict):
                continue
            if "stage" not in job:
                findings.append(
                    f"{rel}: job `{name}` has no stage — it lands in `test` by accident")
            if "script" not in job:
                findings.append(f"{rel}: job `{name}` has no script")

    it = base / "issue_templates"
    for p in sorted(it.glob("*.md")) if it.is_dir() else []:
        if NON_GOAL_HEADING not in p.read_text(encoding="utf-8").lower():
            findings.append(
                f"{p.relative_to(root)}: no `Nicht-Ziele` section. Non-goals are required per "
                f"AGENTS.md and the single most effective measure against over-engineering")
    if it.is_dir() and not list(it.glob("*.md")):
        findings.append(f"{it.relative_to(root)}: no issue templates")

    mr = base / "merge_request_templates"
    if mr.is_dir():
        templates = sorted(mr.glob("*.md"))
        if not templates:
            findings.append(f"{mr.relative_to(root)}: no merge-request template")
        for p in templates:
            findings += check_pr_template(p, root)

    return findings


def check_gitlab_actions_leftovers(path: Path, rel: Path) -> list[str]:
    """A pipeline copied from Actions parses as YAML and then does nothing."""
    findings = []
    for nr, line in code_lines(path.read_text(encoding="utf-8")):
        s = line.strip()
        for token in ("runs-on:", "uses:", "steps:"):
            if s.startswith(token) or s.startswith(f"- {token}"):
                findings.append(
                    f"{rel}:{nr}: `{token}` is Actions syntax. GitLab uses "
                    f"image/script/stage and ignores this key silently")
    return findings


def check_gitlab_pipeline(entry: Path, base: Path, root: Path) -> list[str]:
    findings: list[str] = []
    text = entry.read_text(encoding="utf-8")
    # The asset template still carries the placeholder the installer replaces.
    placeholder = "__STACK_INCLUDE__" in text
    d = load(entry, findings, root) if not placeholder else yaml.safe_load(
        text.replace("__STACK_INCLUDE__", ""))
    if d is None:
        return findings

    rel = entry.relative_to(root)
    stages = d.get("stages") or []
    if not stages:
        findings.append(f"{rel}: no stages declared")

    includes = d.get("include") or []
    if isinstance(includes, dict):
        includes = [includes]
    local_files = []
    for inc in includes:
        if isinstance(inc, dict) and "local" in inc:
            local_files.append(str(inc["local"]))
    if not local_files and not placeholder:
        findings.append(f"{rel}: no `include: local:` — the stack pipeline is never loaded")

    for lf in local_files:
        target = root / lf.lstrip("/")
        if not target.is_file():
            # As an installer asset the paths are still written for the installed
            # layout (.gitlab/ci/…), so resolve them against the payload too.
            alt = base / Path(lf.lstrip("/")).relative_to(Path(lf.lstrip("/")).parts[0])
            if not alt.is_file():
                findings.append(f"{rel}: include `{lf}` points at a file that does not exist")

    # Every stage a job asks for has to be declared, or the job never runs.
    declared = set(stages)
    ci = base / "ci"
    for p in sorted(ci.glob("*.y*ml")) if ci.is_dir() else []:
        job_doc = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
        for name, job in job_doc.items():
            if not isinstance(job, dict) or name.startswith("."):
                continue
            stage = job.get("stage")
            if stage and stage not in declared:
                findings.append(
                    f"{p.relative_to(root)}: job `{name}` uses stage `{stage}`, which "
                    f"{rel} does not declare")
    return findings


# ── entry point ─────────────────────────────────────────────────────────────

CHECKS = {"forgejo": check_forgejo, "github": check_github, "gitlab": check_gitlab}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("root", nargs="?", default=".")
    ap.add_argument("--forge", choices=sorted(CHECKS), default=None,
                    help="check one forge; default: every forge present")
    a = ap.parse_args()
    root = Path(a.root).resolve()

    wanted = [a.forge] if a.forge else list(CHECKS)
    results: dict[str, list[str]] = {}
    for name in wanted:
        found = CHECKS[name](root)
        if found is not None:
            results[name] = found

    print(f"\n{'='*62}\n  FORGE-CHECK\n{'='*62}\n")

    if not results:
        which = a.forge or "forgejo, github or gitlab"
        print(f"  XX  no forge configuration found ({which})\n")
        return 1

    total = 0
    for name, findings in results.items():
        print(f"  ── {name} ──")
        for f in findings:
            print(f"  XX  {f}")
        if not findings:
            print(f"  OK  matches {name} syntax")
        print()
        total += len(findings)

    if total:
        print(f"  {total} finding(s)\n")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
