---
artifact_contract: "ce-handoff/v1"
created_at: "2026-11-22T13:49:27Z"
title: "70 A nacelle-64 ESC plan: U1 closed"
summary: "Sprint U1 (setup and baseline) is closed; U2 and U3 are ready and need no envelope."
keywords: ["70a", "nacelle-64", "issue-23", "u1", "sprint-close", "baseline"]
cwd: "/home/user/Open-Secure-ESC"
resume_focus: "Start U2 (bay fit scorer) or U3 (70 A power design); both are independent of the envelope."
repository: "Stab-Rabbit-coding/Open-Secure-ESC"
repo_root_sha: "8406062ebd47"
branch: "claude/70a-esc-sprint-plan-3xkjg7"
head: "3fe025c (before the U1 commit)"
---

## Handoff: U1 closed (2026-11-22)

AI-generated (Claude, Anthropic). Not human-reviewed. Plan:
`docs/plans/2026-11-22-001-feat-70a-nacelle64-esc-sprint-plan.md`.
Draft PR #24.

## Exit-gate result: passed

| Test scenario (plan U1) | Result |
| --- | --- |
| Serenity-UAV harness tests at the pinned commit | 15 passed at `3d23e68`, including `test_model1_golden_unchanged` (−60.51) and `test_skin64_reads_the_near_side` |
| `kicad-cli --version` 9.x; `import kiutils` | 9.0.2; kiutils, scipy, trimesh, rtree, shapely and pytest all import |
| NASA-STD-8739.4A cited | `REFERENCES.md` [69], Change 4, Table 7-1 p. 30, verified against the local PDF |
| `[67]` duplicate logged | `TODO.md` 19.2 (open, needs an owner ruling) |

The baseline record is in `builds/6s/70A/README.md`.

## What changed in U1

- `REFERENCES.md` [69] and `docs/datasheets/nasa-std-87394a_w_change_4.pdf`.
- `builds/6s/70A/README.md` (new): the baseline pin and the bend-radius
  CAUTION.
- SecureControllers `.claude/skills/sprint-close/SKILL.md` (new): the close-out sequence.
- `docs/solutions/developer-experience/doc-wording-check-reads-staged-files-only.md`
  (new learning).
- `TODO.md` §19.1 checked; 19.1.a added.
- Plan rules 6–7 point to `/sprint-close` and the persisted tools.
- Build environment setup script: kiutils, scipy, trimesh, rtree, shapely,
  pytest and markdownlint-cli2 0.22.1. This is unproven until a fresh session
  builds the container.

## Findings to carry forward

- **Issue 23 cites Change 3, and [69] is Change 4.** The Change 3 copy was
  not obtained. TODO 19.1.a: `UNVERIFIED` for the Change 3 Table 7-1 values.
- **Kapton leads.** Table 7-1 sets the minimum bend radius to 10 × OD for
  polyimide insulation, against the 3 × OD that Serenity-UAV's harness
  assumes (`bend_k: 3.0`). U9 shall check every lead's insulation.
- **Callout level (owner decision).** The doc reviewer said WARNING overstates
  the invalid-envelope risk under `AGENTS.md`, which reserves WARNING for
  injury or the destruction of hardware. The owner used WARNING in issue 23,
  so it was kept in the plan and in `builds/6s/70A/README.md`. Open.
- **CI lint is unpinned.** `.github/workflows/lint.yml` installs the latest
  `markdownlint-cli2`. Locally, 0.22.1 is pinned. A future release can fail
  CI on docs that pass locally.
- **Review coverage.** The quick code review (built-in, low effort) reviewed
  the tracked diff only. The new files were read by the step-1 doc reviewer,
  which ran in a separate context.
- **Planning-commit wording gate.** The first plan commit's "wording clean"
  checked nothing, because the script reads staged files only. It was re-run
  correctly in U1 with the plan staged: 0 errors.

## Budgets

No hardware was designed in U1. Mass: none (0 lbm). Loss: none (0 W).
Clearance: none. U3 owns the first loss budget.

## Fragile local state (machine-local)

- `/home/user/stab-rabbit-coding/serenity-uav`: a sparse, shallow clone
  detached at `3d23e68`, with `tools/`, `requirements-dev.txt` and one STL.
  It is lost with the container. Re-clone per `builds/6s/70A/README.md`. Do
  not run `git ls-tree -l` on it: the blob-less clone then fetches every
  blob.

## Next sprint: first read

U2 and U3 are independent. Either can go first.

- **U2 (Moderate):** plan "### U2." section; `docs/tools/isolation_envelope.py`;
  Serenity-UAV `tools/esc80_cooptimize.py` (`bays` output shape) and the G1
  bay list at the pre-fix commit `e8b1299`.
- **U3 (Advanced):** plan "### U3." section;
  `builds/6s/50A/CAN_485_faraday_faceted/README.md`;
  `docs/tools/conductor_sizing.py`; `REFERENCES.md` [46] and [49].
- End the sprint with `/sprint-close <U-ID>`.
