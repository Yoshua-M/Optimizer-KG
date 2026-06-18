# client_value

## Responsibility

Own **client-side value intelligence**: extract and structure what the *client* says about value (metrics, priorities, outcomes) from client interview material per the PRD client path. This is not the organizational process graph; it feeds investment and linkage views later.

## Boundaries

| In | Out |
|----|-----|
| Client-specific prompts, parsers, value entities/metrics | Internal org process/role graph → `graph_building/` |
| Rules and types for “client value snapshot” | Ranking org activities vs metrics → `value_linkage/` |
| Validation hooks with shared ontology types | Ontology definitions → `ontology/` (client_value consumes) |
| | Raw file read → `ingestion/` |
| | LLM client construction → `infrastructure/llm_client/` |
| | UI → `presentation/` |

**Callers (target):** `application/run_client_value_analysis.py`. **Callees:** `infrastructure/llm_client`, optionally `ontology/`.

## Files

| File | Why it lives here |
|------|-------------------|
| `__init__.py` | Package marker until client-value facades exist. |

*(Empty — no client interview processing in repo yet.)*

## Facades (planned)

- `extract_client_metrics(text | NormalizedSource) → ClientValueSnapshot` — main domain entry for client interviews.

## Planned files

| File | Why it would live here |
|------|-------------------------|
| `extractors.py` | LLM prompts and parsing for client value only — separated from org-graph prompts in `graph_building/`. |
| `models.py` | `ClientValueSnapshot`, metric types — client domain vocabulary. |

Link to org graph only through explicit IDs or `value_linkage/` facades; do not embed client-value logic in `graph_building/`.
