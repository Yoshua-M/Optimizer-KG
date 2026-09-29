# graph_hygiene

## Responsibility

Own **quality operations on an existing organizational graph**: structural coherence (checks 1–7), Intent-layer protocol checks C1–C14, deterministic repairs (R1/R2 Intent; R6 topology auto; R3 means-to-end when authorized), protocol cycle + Salidas report, and label sanitization. Does not re-extract from raw text (see `ontology/` for vocabulary).

## Boundaries

| In | Out |
|----|-----|
| Topology / Intent checks; Intent merges when authorized; topology wiring always | Initial LLM extraction → `graph_building/` |
| Move evidence notes out of display labels into `evidence_pointer` | Neo4j persistence → `infrastructure/graph_store/` |
| | UI → `presentation/` |
| | Load fixture / write report → `application/run_coherence_*.py` |

**Callers:** `application/run_coherence_audit.py`, `application/run_coherence_protocol.py`. **Callees:** LangChain `GraphDocument`, `ontology.schema`.

## Files

| File | Why it lives here |
|------|-------------------|
| `__init__.py` | Facade exports. |
| `coherence.py` | Structural checks 1–7 + branch-fork classification (acceptable vs pending). |
| `intent_checks.py` | Protocol C1–C4. |
| `protocol.py` | C5–C14, R1–R3/R6 repairs (topology auto; ontology gated), cycle, Salidas report. |
| `sanitize_labels.py` | Evidence notes out of display names. |

## Facades

- `audit_coherence` / `audit_intent_coherence` / `format_coherence_report`
- `run_protocol_cycle(document, authorize_ontology=False) → ProtocolResult`
- `format_protocol_report(result) → str`
- `propose_r3_means_to_end` / `repair_topology` / `repair_r3_means_to_end`
- `sanitize_graph_document` / `split_label_evidence`
