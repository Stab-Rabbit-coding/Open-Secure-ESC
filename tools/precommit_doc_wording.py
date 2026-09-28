#!/usr/bin/env python3
"""Pre-commit check for CNAF M-3710.7 [REF-MIL-001]-style doc wording.

Enforces (blocking):
  - No ad hoc callout labels (IMPORTANT:, ATTENTION:, NOTICE:, ALERT:) in
    place of WARNING / CAUTION / Note.

Flags (advisory only, non-blocking): "will" used adjacent to mandatory
language ("must", "shall", "required") where "shall" is likely meant, since
CNAF M-3710.7 SS1.6 reserves "will" for futurity, never requirement. This is
a heuristic, not a parser -- it can false-positive on a genuine futurity
statement, so it never fails the commit.

Scope: staged *.md files only. Runs from the repo's pre-commit hook.
"""
import re
import subprocess
import sys

AD_HOC_LABELS = re.compile(
    r"^\s*(?:\*\*)?(IMPORTANT|ATTENTION|NOTICE|ALERT)(?:\*\*)?\s*:", re.IGNORECASE
)
WILL_NEAR_MANDATORY = re.compile(
    r"\bwill\b.{0,40}\b(must|shall|required|mandatory)\b"
    r"|\b(must|shall|required|mandatory)\b.{0,40}\bwill\b",
    re.IGNORECASE,
)


def staged_markdown_files():
    out = subprocess.run(
        ["git", "diff", "--cached", "--name-only", "--diff-filter=ACM"],
        capture_output=True, text=True, check=True,
    ).stdout.splitlines()
    return [f for f in out if f.endswith(".md")]


def check_file(path):
    errors = []
    warnings = []
    try:
        with open(path, encoding="utf-8", errors="replace") as fh:
            lines = fh.readlines()
    except OSError:
        return errors, warnings
    for i, line in enumerate(lines, start=1):
        m = AD_HOC_LABELS.match(line)
        if m:
            errors.append(
                f"{path}:{i}: ad hoc callout label '{m.group(1)}:' -- use "
                "WARNING / CAUTION / Note per REF-MIL-001 SS1.5 instead"
            )
        if WILL_NEAR_MANDATORY.search(line):
            warnings.append(
                f"{path}:{i}: 'will' near mandatory language -- confirm this "
                "is futurity, not a requirement (REF-MIL-001 SS1.6: 'will' "
                "never indicates a degree of requirement; use 'shall')"
            )
    return errors, warnings


def main():
    files = staged_markdown_files()
    all_errors = []
    all_warnings = []
    for f in files:
        errors, warnings = check_file(f)
        all_errors.extend(errors)
        all_warnings.extend(warnings)

    if all_warnings:
        print("doc-wording advisory (REF-MIL-001 SS1.6, not blocking):", file=sys.stderr)
        for w in all_warnings:
            print(f"  {w}", file=sys.stderr)

    if all_errors:
        print("doc-wording check FAILED (REF-MIL-001 SS1.5):", file=sys.stderr)
        for e in all_errors:
            print(f"  {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
