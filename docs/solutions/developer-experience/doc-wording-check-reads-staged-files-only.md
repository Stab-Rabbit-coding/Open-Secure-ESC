---
date: 2026-11-22
problem_type: developer_experience
category: developer-experience
module: tools
component: tooling
severity: medium
applies_when:
  - "Running tools/precommit_doc_wording.py by hand, outside a git pre-commit hook"
  - "Passing file paths to tools/precommit_doc_wording.py"
  - "Reporting a doc-wording gate as passed before a commit"
tags:
  - doc-wording
  - pre-commit
  - verification
  - silent-pass
  - cnaf-3710
related_components:
  - tools/precommit_doc_wording.py
  - "SecureControllers: .claude/skills/sprint-close/SKILL.md"
---

# The doc-wording check reads staged files only

## Context

`tools/precommit_doc_wording.py` enforces the `AGENTS.md` §4a wording rules
(shall/should/may/will and the callout labels). On 2026-11-22 it was run as
`python3 tools/precommit_doc_wording.py <file> ...` on a new plan and on
`TODO.md`, before either file was staged. It exited 0 with no output, and
"wording clean" was reported for the plan commit. That result covered nothing.

## Guidance

The script ignores its command-line arguments. `main()` calls
`staged_markdown_files()` (`tools/precommit_doc_wording.py:31`), which lists
only `git diff --cached --name-only --diff-filter=ACM` paths ending in `.md`.
An unstaged doc is never read. A run with nothing staged exits 0 because it
checked no file.

Stage first, then run:

```bash
git add <changed docs>
python3 tools/precommit_doc_wording.py
```

The `--diff-filter=ACM` filter also skips renamed files (`R`). Stage a moved
doc as an add, or check it another way.

## Why This Matters

A gate that passes on empty input is a silent pass, and a silent pass reads
the same as a real one. Here a WARNING/CAUTION or "will"-for-"shall" error in
an unstaged doc would reach a commit with a "clean" claim next to it. The
same trap applies to any staged-only hook that is run by hand.

## When to Apply

- A sprint close-out or review runs the wording gate by hand
  (SecureControllers `.claude/skills/sprint-close/SKILL.md` states the stage-first order).
- A result reads "clean" and no one can name the file the check read.

## Examples

Before: `python3 tools/precommit_doc_wording.py docs/plans/plan.md` on an
unstaged file. It exits 0, and nothing was checked.

After: `git add docs/plans/plan.md && python3 tools/precommit_doc_wording.py`.
The script reads the staged plan and reports any violation.

## Related

- `docs/solutions/architecture-patterns/measurement-harness-must-be-audited.md`
  covers the same failure in a placement-scoring harness: a check that is not
  audited can report clean on nothing.
