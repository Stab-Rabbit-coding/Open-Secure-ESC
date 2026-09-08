---
date: 2026-09-07
problem_type: architecture_pattern
category: architecture-patterns
module: docs
component: documentation
severity: medium
applies_when:
  - "A markdown doc in this repo was originally produced by an AI tool outside this repo's own workflow"
  - "A markdown file fails MD041 (first line not a heading) or has an unexplained duplicate H1"
  - "Reviewing any doc for CI cleanup that nobody has read end-to-end recently"
tags:
  - documentation
  - markdown
  - repo-hygiene
  - ci
related_components:
  - docs/OpenSecureESC-Brushed-Specifications.md
  - .github/workflows/lint.yml
---

# A doc that fails MD041 or has a duplicate H1 may be two documents pasted together, not a formatting typo

## Context

Cleaning up a `Markdown lint` CI failure on `docs/OpenSecureESC-Brushed-Specifications.md` started as "fix the reported MD041 (first line isn't a heading)." Making the first line a real `#` heading immediately produced a *new* error — MD025, multiple top-level headings — from a second `# Open-Source Hardware Brushed ESC Platform Architectural & Component Framework` 150 lines later. Reading the file end to end (rather than patching each linter complaint in isolation) showed why: the first ~150 lines were an escaped draft (every markdown special character literally backslash-escaped — `\#\#`, `\*\*`) followed by leftover Python artifacts from whatever tool generated it — a `verified_doc = """..."""` heredoc, `os.path.join(...)`, `f.write(verified_doc)`, `print(f"Re-written verified markdown file to {docs_path}")` — and then, starting at line 151, a second, real, mostly-clean copy of the same document. The committed file was never the intended document; it was a tool's entire working transcript, with the actual output buried partway through.

## Guidance

When a markdown lint failure doesn't make sense as an isolated typo — a first-line-heading violation on a document that clearly has real headings later, a duplicate-H1, or any error whose "obvious" one-line fix immediately produces a different structural error — **read the whole file before patching the reported line.** The specific signals that mean "this is two documents, not one with a typo," worth grepping for directly:

- The document's own title (or a very similar paraphrase of it) appearing more than once
- Every markdown special character backslash-escaped (`\#`, `\*\*`, `\.`, `\-`, `\[`, `\]`) in one stretch of the file and not another — a hallmark of AI-tool output that was never rendered, just pasted as literal text
- Language/tool artifacts that have no business in a design document: `print(...)`, a `with open(...) as f:` block, a heredoc delimiter (`"""`), a `[file-tag: ...]` marker, "Code output" as a literal line

None of these are things a linter rule catches directly — `markdownlint` reports the downstream *symptom* (a missing top-level heading, a duplicate one, a broken list), not the upstream cause (leftover generation transcript). Treat a CI lint failure as a prompt to read the file, not just a line number to patch.

The fix, once recognized, is usually to delete the leftover/garbage copy entirely and keep the real one — not to patch escaping inside content that shouldn't be there at all.

## Why This Matters

A linter fix applied at the reported line, without reading past it, would have "fixed" MD041 by promoting the escaped draft's title to a real heading — leaving the leftover Python transcript and the duplicate real document both still committed, now with the wrong copy structurally valid and the right copy still fighting it for MD025. The lint check would eventually surface that too, on the next unrelated commit that happened to touch heading structure, at which point the actual cause is a commit further removed from the AI session that produced the mess to begin with. Reading the file once, when the CI failure first looks structurally odd rather than typo-shaped, is cheaper than chasing the same defect across two separate lint failures.

## When to Apply

- Any markdown lint failure where the "obvious" fix creates a new lint failure of a different kind.
- Reviewing a doc known to have been originally drafted by an AI tool outside this repo's own `docs/solutions/` or schematic-adjacent workflows, especially if it was pasted in wholesale rather than authored incrementally in this repo.
- As a general habit before trusting any doc's content: a document that reads as two attempts stitched together is a documentation-integrity problem independent of whatever lint rule happened to catch it.

## Related

- `docs/OpenSecureESC-Brushed-Specifications.md` — the document this was found in
- `.github/workflows/lint.yml` — the `Markdown lint` job whose failure surfaced this
