# value_linkage

## Responsibility

Own the **bridge between organizational graph and value evidence**: link activities/processes in the org graph to client/value metrics, quantify relevance, and support ranking for investment decisions (PRD “bridge”). Uses outputs from `graph_building/` and `client_value/`; does not build either graph from scratch.

## Boundaries

| In | Out |
|----|-----|
| Linking rules, scores, ranked activity lists | Org extraction/merge → `graph_building/` |
| Metrics alignment and quantified relevance | Client interview parsing → `client_value/` |
| | Hygiene dedup/prune → `graph_hygiene/` |
| | LLM client setup → `infrastructure/llm_client/` |
| | Reports/HTML export → `infrastructure/` or `presentation/` |

**Callers:** `application/run_value_linkage.py` (planned). **Callees:** `graph_building/` (graph access), `client_value/` (metric snapshots), optional `ontology/`.

## Files

| File | Why it lives here |
|------|-------------------|
| `__init__.py` | Package marker until linkage facades exist. |

*(Empty — PRD bridge not implemented.)*

## Facades (planned)

- `link_and_rank(org_graph, client_value_snapshot) → RankedActivities` — main domain entry for investment views.

## Planned files

| File | Why it would live here |
|------|-------------------------|
| `linkers.py` | Map graph nodes/edges to metric dimensions. |
| `ranking.py` | Scoring and sort policies for activities/processes. |
| `models.py` | `RankedActivities`, relevance scores — linkage vocabulary only. |

Keep **one org graph** from `graph_building/`; attach value via explicit IDs or facades, not duplicate graph storage here.
