# graph_hygiene

## Responsibility

Own **quality operations on an existing organizational graph**: deduplication, pruning low-value nodes/edges, and resolving conflicts after `graph_building` has produced a graph document. Improves trust and clarity of the single org graph; does not re-extract from raw text or define ontology types.

## Boundaries

| In | Out |
|----|-----|
| Dedup, merge-collapse, conflict resolution rules | Initial LLM extraction → `graph_building/` |
| Hygiene passes over in-memory / graph documents | Neo4j persistence → `infrastructure/graph_store/` |
| Facade `clean_graph(doc) → doc` (names TBD) | Client metrics → `client_value/` |
| | UI for hygiene review → `presentation/` |
| | Workflow trigger → `application/run_hygiene_pass.py` |

**Callers:** `application/` (planned). **Callees:** `graph_building/` graph types/API, optional `ontology/` for rule checks.

## Files

| File | Why it lives here |
|------|-------------------|
| `__init__.py` | Package marker until hygiene facades exist. |

*(Empty — PRD hygiene not implemented.)*

## Facades (planned)

- `run_hygiene_pass(graph_documents) → graph_documents` — apply configured hygiene pipeline.

## Planned files

| File | Why it would live here |
|------|-------------------------|
| `dedup.py` | Entity/edge deduplication strategies. |
| `prune.py` | Remove noise by policy (degree, type, confidence). |
| `conflicts.py` | Detect and resolve contradictory assertions. |

Operate on **graph documents** from `graph_building/`; return same shape for downstream `value_linkage/`.
