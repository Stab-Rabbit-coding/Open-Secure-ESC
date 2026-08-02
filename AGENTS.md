# AGENTS.md — Governance Rules for Human & AI Contributors

This file is binding on every contributor (human or AI agent) working in this
repository. It governs technical claims, design decisions, and documentation
in a safety-relevant hardware project (motor speed control + hardware root of
trust). Violating these rules is a defect, not a style issue.

## 1. Mandatory Rules

### 1.1 Strict conformity to verified, authoritative standards

- Every technical claim, part selection, protocol implementation, and design
  decision MUST conform to a verified, authoritative source: the component
  manufacturer's own datasheet/errata, the official standards body (IEEE,
  ISO, TIA/EIA, IEC, DoD/MIL, TCG, etc.), or a primary regulatory text.
- "Authoritative" excludes: forum posts, blogs, AI-generated summaries,
  Wikipedia, marketing pages, and unverified mirrors — these may be used to
  *locate* a primary source but never *cited in place of one*.
- If no authoritative source can be found or accessed, the claim MUST be
  marked `UNVERIFIED` (see §3) instead of asserted as fact.

### 1.2 IEEE-formatted citations in REFERENCES.md

- Every cited standard, datasheet, specification, regulation, or external
  claim used anywhere in this repo (code comments, docs, schematics notes,
  commit messages describing a design rationale) MUST have a corresponding
  entry in `REFERENCES.md`, formatted per IEEE reference style.
- Each entry MUST carry a stable citation tag (e.g. `[3]`) used consistently
  at the point of use (README, code comment, schematic annotation, etc.) and
  in `REFERENCES.md`.

### 1.3 No fabrication or assumption

- No reference, specification, standard revision, part number, electrical
  parameter, or design decision will ever be fabricated, guessed, inferred
  from training data without verification, or "assumed to probably be
  correct."
- If a value cannot be confirmed against a primary source, it is written as
  `UNVERIFIED — needs primary source` and tracked in `TODO.md`. It is never
  silently filled in with a plausible-sounding number.
- This applies equally to AI agents: do not answer from memory when a
  verifiable primary source is required. Fetch and cite it, or flag it as
  unverified.

## 2. Citation Workflow

1. Locate the primary source (manufacturer site, standards body catalog,
   official government/DoD repository).
2. Record in `REFERENCES.md`, IEEE format, with ALL of:
   - Author/organization
   - Title (document name)
   - Document ID / standard number and revision (if published)
   - Verified source URL
   - Chapter, section, page, and/or paragraph the claim relies on
   - Date accessed
3. If any of the above fields cannot be verified (e.g., a document is
   paywalled and only the catalog page, not chapter/page, is accessible),
   the entry must say so explicitly (`section/page: not verified —
   document not accessible without purchase`) rather than omit or guess.
4. Add/reuse the citation tag at every point of use in the repo.
5. Never renumber or repurpose an existing tag for a different source.

## 3. Marking Unverified Content

Use this exact marker anywhere a claim, spec, or decision cannot yet be
traced to a primary source:

```text
UNVERIFIED — needs primary source (see TODO.md)
```

Do not merge design files, firmware, or documentation that assert
`UNVERIFIED` content as if it were settled, and do not remove the marker
until a real citation replaces it.

## 4. Design Decisions

Every non-trivial design decision (component selection, protocol choice,
EMI hardening tier, control-loop topology) must record *why* in terms of a
cited requirement or standard — not preference or convention. If a decision
is a judgment call with no governing standard, say so explicitly rather than
implying one exists.

## 5. Review Checklist (apply before merging any change)

- [ ] Every new technical claim traces to an authoritative source
- [ ] Every citation used in-repo has a matching `REFERENCES.md` entry
- [ ] Every `REFERENCES.md` entry has URL + section/page/paragraph + date
      accessed, or an explicit note on why a field is unverifiable
- [ ] No invented document IDs, revisions, page numbers, or electrical values
- [ ] Any gap is marked `UNVERIFIED` and logged in `TODO.md`, not guessed
