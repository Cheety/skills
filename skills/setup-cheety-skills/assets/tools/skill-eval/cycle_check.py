#!/usr/bin/env python3
"""
cycle_check — verifies a change's git history against the test-first rules in
.claude/skills/bug-beheben/ and .claude/skills/feature-umsetzen/.

The core of those skills is an ORDER, not a text format. Only the history can
prove it was followed: a test written after the fix does not prove it would
have caught the bug.

Usage: cycle_check.py <repo> --test-command "php tests/run.php" [--first Test: --then Fix:]
"""
import argparse, re, shutil, subprocess, sys, tempfile
from pathlib import Path

ap = argparse.ArgumentParser()
ap.add_argument("repo", type=Path)
ap.add_argument("--test-command", required=True)
ap.add_argument("--test-prefix", default="tests/")
ap.add_argument("--first", default="Test:", help="prefix of the test commit")
ap.add_argument("--then", default="Fix:", help="prefix of the implementation commit (Fix: or Impl:)")
ap.add_argument("--max-lines", type=int, default=10)
a = ap.parse_args()

# Work inside a TEMPORARY CLONE. A verification tool that checks out the
# user's working tree is intrusive — and on failure leaves it on a detached
# HEAD. That is exactly what the first draft did.
_tmp = tempfile.mkdtemp(prefix="bugfix-pruefung-")
_klon = Path(_tmp) / "repo"
subprocess.run(["git", "clone", "--quiet", "--no-hardlinks", str(a.repo.resolve()), str(_klon)],
               check=True, capture_output=True)

def sh(c, **kw):
    return subprocess.run(c, shell=True, cwd=_klon, capture_output=True, text=True, **kw)

log = [l.split(" ", 1) for l in sh("git log --oneline --reverse").stdout.strip().splitlines()]
titel = [t for _, t in log]
sha = {i: h for i, (h, _) in enumerate(log)}

i_test = next((i for i, t in enumerate(titel) if t.startswith(a.first)), None)
i_fix = next((i for i, t in enumerate(titel) if t.startswith(a.then)), None)
if i_test is None or i_fix is None:
    sys.exit(f"no commit pair '{a.first}' / '{a.then}' found.")

p = []
p.append(("test commit precedes implementation commit", i_test < i_fix, f"Test #{i_test}, Fix #{i_fix}"))

d_test = sh(f"git show --name-only --format= {sha[i_test]}").stdout.split()
p.append(("test commit has no production code",
          all(x.startswith(a.test_prefix) for x in d_test), ", ".join(d_test)))

sh(f"git checkout -q {sha[i_test]}")
rot = sh(a.test_command).returncode
p.append(("suite is red at the test commit", rot != 0, f"exit={rot}"))

sh(f"git checkout -q {sha[i_fix]}")
gruen = sh(a.test_command).returncode
p.append(("suite is green at the implementation commit", gruen == 0, f"exit={gruen}"))

d_fix = sh(f"git show --name-only --format= {sha[i_fix]}").stdout.split()
p.append(("implementation changes no tests",
          not any(x.startswith(a.test_prefix) for x in d_fix), ", ".join(d_fix)))

stat = sh(f"git show --shortstat --format= {sha[i_fix]}").stdout.strip()
zeilen = sum(int(x) for x in re.findall(r"(\d+) [id]", stat))
p.append((f"implementation under {a.max_lines} lines", zeilen < a.max_lines, stat))

shutil.rmtree(_tmp, ignore_errors=True)

ok = sum(1 for _, b, _ in p if b)
print(f"\n{'='*62}\n  CYCLE CHECK (test first)\n{'='*62}\n")
for n, b, d in p:
    print(f"  {'PASS' if b else 'FAIL'} {n:<40} {d}")
print(f"\n  {ok}/{len(p)} rules satisfied\n")
sys.exit(0 if ok == len(p) else 1)
