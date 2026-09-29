# optimizer — where to work

Load **this file** to choose a module. Load **`<module>/AGENTS.md`** before editing that module.

**Before writing any change here (or in `tests/`, `configs/`, `scripts/`),** read `docs/Protocols/GENERATION-SIGNALS (1).md` and use this module’s `AGENTS.md` as the declared scope. Root `AGENTS.md` states the same rule.

## Routing — new or moved code

| You are implementing… | Go to |
|------------------------|--------|
| Streamlit layout, upload UI, embed HTML | `presentation/` |
| A product workflow (steps, call order, return to UI/CLI) | `application/` |
| Org graph from text: extract, merge, graph model | `graph_building/` |
| Prompt/chain spikes, compare alternatives | `experiments/` → promote to `graph_building/` |
| LLM client, PyVis, Neo4j, config, file I/O | `infrastructure/` |
| Read interviews/docs into normalized inputs | `ingestion/` |
| Client interview → client value metrics | `client_value/` |
| Dedup, prune, conflicts on org graph | `graph_hygiene/` |
| Rank/link activities to metrics | `value_linkage/` |
| Graph analytics, value streams, Porter catalog | `graph_analytics/` |
| Allowed types/relations, validation | `ontology/` |
| Non-UI CLI entry | `cli.py` (delegates to `application/`) |
| Data files (raw / interim / processed) | `data/` — see `data/AGENTS.md` |
| Regression tests for a module | `tests/<module>/` — see `tests/AGENTS.md` |
| PRD, architecture, ADRs, structure protocols | `docs/` — see `docs/AGENTS.md` |

**Default graph UI path:** root `app.py` → `presentation/` → `application/` → `graph_building/` + `infrastructure/`. Do not route production UI through `experiments/`.

**PRD-shaped pipeline (later):** `ingestion` → `graph_building` (+ `ontology`) → `graph_hygiene` → `value_linkage` / `client_value`.

## Cross-module flow (orientation only)

```text
app.py → presentation → application → graph_building → infrastructure
                              ↘ ingestion, client_value, … (future)
```

Details and facades live in each module’s `AGENTS.md`, not here.

## What belongs in AGENTS.md files

**This file (package):** routing table, cross-module flow sketch, rules below. No per-file facades, no implementation detail, no “status” columns.

**`<module>/AGENTS.md`:** one **precise responsibility** for the module; **per-file** notes (what the file is for, why that code lives there); **facades** this module exposes; **import boundaries** (callers/callees). Update in the same PR as code changes.

**Repo support dirs:** `data/AGENTS.md`, `tests/AGENTS.md`, `docs/AGENTS.md` — same idea: responsibility, boundaries, what lives where; tests AGENTS.md may include the unittest discover command.

**Never put in any AGENTS.md:** full PRD, long protocol copies, duplicate of another module’s facades.

## Agent: keep AGENTS.md current

When you change a module, update **its** `AGENTS.md` if you add/remove/rename a file, move code across modules, or change a public entrypoint. Update **this file** only if routing rules or the table above change (new module, new default path).

If AGENTS.md and code disagree, fix AGENTS.md in the same change.
