# ontology

## Responsibility

Own **allowed vocabulary and constraints** for the knowledge graph: entity types, relationship types, mapping rules, and validation hooks used when building or cleaning the org graph. Shared rulebook for domains; does not run extraction pipelines or UI.

## Boundaries

| In | Out |
|----|-----|
| Type/ relation allowlists, validation functions | LLM extraction implementation → `graph_building/` |
| Mapping external labels → canonical types | Client-specific value definitions → `client_value/` (may consume shared types) |
| | Hygiene algorithms → `graph_hygiene/` |
| | Persistence → `infrastructure/graph_store/` |

**Callers:** `graph_building/` (during extract/merge), `graph_hygiene/`, `client_value/` (subset). **Must not** import `presentation/` or `application/`.

## Files

| File | Why it lives here |
|------|-------------------|
| `__init__.py` | Package marker until ontology API exists. |

*(Empty — PRD ontology section not implemented.)*

## Facades (planned)

- `validate_graph_document(doc) → ValidationResult` — reject or flag non-conformant nodes/edges.
- `canonicalize_type(label) → str` — map free-text types to ontology ids.

## Planned files

| File | Why it would live here |
|------|-------------------------|
| `schema.py` | Allowed types/relations and metadata (PRD §6). |
| `validators.py` | Pure validation over graph documents — no LLM calls. |

`graph_building/` calls validators after extraction or before merge; keep ontology **declarative** where possible.
