#!/usr/bin/env python3
"""
eval — measures a profile against its fixture project.

Every line carrying "!! RULE_ID" is a planted violation and MUST be found.
Every finding without a matching marker is a false positive.

The second number matters more: a false positive teaches people to bypass the
tool. A missing rule does not.

Usage: eval.py --profile <name> [--fixtures <path>]
"""
import argparse
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).parent

ap = argparse.ArgumentParser()
ap.add_argument("--profile", required=True)
ap.add_argument("--fixtures", type=Path, default=None)
a = ap.parse_args()

root = (a.fixtures or HERE / "fixtures" / a.profile).resolve()
if not root.exists():
    sys.exit(f"fixtures not found: {root}")

expected = {}
for p in sorted(root.rglob("*")):
    if not p.is_file():
        continue
    try:
        text = p.read_text(encoding="utf-8", errors="replace")
    except Exception:
        continue
    rel = str(p.relative_to(root))
    for i, z in enumerate(text.splitlines(), 1):
        if mm := re.search(r"!!\s+([A-Z_]+)", z):
            expected[f"{rel}::{mm.group(1)}"] = i

r = subprocess.run(
    [sys.executable, str(HERE / "arch_check.py"), str(root), "--profile", a.profile, "--quiet"],
    capture_output=True, text=True)

found = {}
for z in r.stdout.splitlines():
    if mm := re.match(r"^(.+):(\d+)\t([A-Z_]+)\t", z):
        found[f"{mm.group(1)}::{mm.group(3)}"] = int(mm.group(2))

missed = {k: v for k, v in expected.items() if k not in found}
false_positive = {k: v for k, v in found.items() if k not in expected}
ok = len(expected) - len(missed)

print(f"\n{'=' * 62}\n  EVAL — profile '{a.profile}'\n{'=' * 62}\n")
print(f"  planted violations : {len(expected)}")
print(f"  detected           : {ok}  ({ok / max(len(expected), 1) * 100:.1f} %)")
print(f"  missed             : {len(missed)}")
print(f"  false positives    : {len(false_positive)}\n")

for title, group in (("MISSED (rule absent)", missed),
                     ("FALSE POSITIVE (rule too broad)", false_positive)):
    if group:
        print(f"  -- {title} {'-' * max(0, 38 - len(title))}")
        for k, v in sorted(group.items()):
            d, rid = k.rsplit("::", 1)
            print(f"     {rid:<28} {d}:{v}")
        print()

if not missed and not false_positive:
    print("  PASS\n")
    sys.exit(0)
print("  FAIL\n")
sys.exit(1)
