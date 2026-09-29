# ontology

## Responsibility

Own **allowed vocabulary and constraints** for the knowledge graph: entity types, relationship types, and Intent-layer isolation rules (Ontology v2.2). Shared rulebook for domains; does not run extraction pipelines or UI.

## Boundaries

| In | Out |
|----|-----|
| Type / relation allowlists, Intent isolation frozensets | LLM extraction implementation → `graph_building/` |
| Mapping helpers (`is_intent_edge`, …) | Client-specific value definitions → `client_value/` |
| | Hygiene algorithms → `graph_hygiene/` |
| | Persistence → `infrastructure/graph_store/` |

**Callers:** `graph_hygiene/` (intent checks), later `graph_building/` / `graph_analytics/` filters. **Must not** import `presentation/` or `application/`.

## Files

| File | Why it lives here |
|------|-------------------|
| `__init__.py` | Re-exports schema facades. |
| `schema.py` | Node/edge vocabulary from `docs/OptimizerGraphOnthologyV2.2.md`; Intent edges isolated from Phase 1–2 computation. |

## Facades

- `NODE_TYPES`, `COMPUTATION_EDGE_TYPES`, `INTENT_EDGE_TYPES`, `ALL_EDGE_TYPES`
- `is_intent_edge(rel_type)`, `is_computation_edge(rel_type)`
- `SERVES_TARGET_TYPES`, `CONFLICT_KINDS`, `ABDUCTION_CONFIDENCE_CEILING`

## Planned files

| File | Why it would live here |
|------|-------------------------|
| `validators.py` | Pure validation over graph documents — no LLM calls. |
