# docs

## Responsibility

Hold **human-oriented project documentation**: product intent, structure protocols, architecture summary, and decision records. Informs design; does not replace per-module `src/optimizer/<module>/AGENTS.md` for day-to-day coding.

## Boundaries

| In | Out |
|----|-----|
| PRD, architecture, ADRs, structure protocols, **changelog** | Runnable code → `src/optimizer/` |
| Stable references agents load for big-picture work | Agent routing / facades → `src/optimizer/AGENTS.md` and module AGENTS files |
| | Example-run workflow trace → `workspace/optimizer_restructure/trace/` |
| | Generated run outputs, reports → `data/processed/` or `reports/` (if added) |

**When to load what:** module work → module `AGENTS.md`; product scope → `PRD.md`; one-off structural questions → protocols below; non-obvious choices → `decisions/`.

## Files — why here

| File | Why it lives here |
|------|-------------------|
| `PRD.md` | Optimizer product requirements — source of truth for domains and future capabilities. |
| `CHANGELOG.md` | Approved shipped work (newest first); one entry per completed feature-dev requirement when operator approves. |
| `changelog_rules.md` | When and how agents update `CHANGELOG.md` (see `04_implement` gate). |
| `architecture.md` | Project-level map (goal, domains, workflows). |
| `MWP.md` | Internal workflow protocol reference (load on demand). |
| `ModelWorkspaceProtocol_context.md` | Full protocol spec (load on demand). |
| `code_filestructure_protocol.md` | How to discover domains and scaffold structure (general protocol). |
| `directory_contract_info.md` | Generic directory contracts — inspiration only; module `AGENTS.md` wins for code. |
| `decisions/` | Architecture decision records (`0001-short-title.md`). |
| `AGENTS.md` (this file) | Routing for the docs folder itself. |

**Project agent routing** lives at repo root: `../AGENTS.md`.

## Agent: keep current

Add an ADR in `decisions/` when making a non-obvious structural choice (new domain, storage strategy, test framework change). Update `architecture.md` when module topology or main workflows change materially. After an **approved** `04_implement` run, append to `CHANGELOG.md` per `changelog_rules.md`. Do not paste full PRD or protocols into module AGENTS files.
