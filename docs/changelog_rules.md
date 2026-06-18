# Changelog — maintenance rules

Human-readable **development history** for Optimizer. The log lives at [`CHANGELOG.md`](CHANGELOG.md).

## Purpose

- Record **shipped** work from completed feature-dev (or equivalent) runs.
- Give operators and agents a single place to see **what changed**, **when**, and **where to read more** (intake, spec, done artifacts).
- Complement — not replace — `<req>_done.md`, ADRs, and git history.

## When to update

Update `docs/CHANGELOG.md` **at the end of `04_implement`** when **all** of the following hold:

1. `<req>_done.md` exists under `workflows/feature_dev/stages/04_implement/output/`.
2. Overall status in that file is **`complete`**, or **`partial`** with **explicit operator approval** to record what shipped.
3. The operator has **accepted** the outcome (same bar as advancing past the `04_implement` gate in `workflows/feature_dev/AGENTS.md`).

**Do not** add an entry when:

- Status is **`blocked`** and nothing was merged to the host repo.
- The run was abandoned or superseded before approval.
- Only planning artifacts exist (intake/spec/tests) with no approved implementation.

If a requirement is **reopened** and ships again, **append a new dated subsection** under the same requirement heading (do not silently rewrite old entries).

## Who updates

- The agent (or human) that **finishes `04_implement`** for that requirement.
- Same turn as writing or finalizing `<req>_done.md`, unless the operator asks to defer the changelog entry.

## Entry format

- **Newest first** — add entries at the top of `CHANGELOG.md`, below the header and maintenance link.
- **One block per approved workflow completion** (requirement id = input file stem, e.g. `demo` from `demo.md`).

Each entry **must** include:

| Field | Content |
|-------|---------|
| **Date** | ISO date (`YYYY-MM-DD`) of approval / done record |
| **Requirement** | Short title + id (link to `workflows/feature_dev/inputs/<req>.md` if present) |
| **Summary** | 1–3 sentences: user-visible outcome |
| **Changes** | Bullet list of notable host-repo changes (modules, entrypoints, tests) |
| **Refs** | Links to `<req>_done.md`, and optionally intake/spec |

Optional: `change_id` table condensed from done log; follow-ups; breaking changes callout.

## Style

- Write for **humans** (complete sentences); not commit-message fragments.
- **Past tense** for shipped work (“Added…”, “Implemented…”).
- No secrets, API keys, or client-confidential detail.
- Keep each entry **scannable** — prefer bullets over long prose.

## What not to put here

- Line-by-line diffs (use git).
- Full PRD or spec text (link instead).
- Unapproved `[PROPOSED]` / draft intake content.
- ADR-level rationale — use `docs/decisions/`; changelog may **link** to an ADR.

## Agents — checklist (`04_implement`)

Before closing a feature-dev run:

1. Write or update `<req>_done.md`.
2. If status is approved `complete` or approved `partial`, add a matching section to `docs/CHANGELOG.md` per this file.
3. Do **not** update root `AGENTS.md` for every entry — routing is already in `docs/AGENTS.md` and `04_implement/AGENTS.md`.
