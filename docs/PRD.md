# Product Requirements Document

## 1. Problem & Objective

- Organizations struggle to see which internal activities and processes actually deliver value to clients; leaders lack a clear, evidence-based picture for investment decisions.
- Build **Optimizer** to trace value streams by mapping client-perceived value metrics against internal activities and processes represented in a knowledge graph.
- Outcome for v1: identify the most valuable activities and processes, show end-to-end dependencies, and quantify each activity’s relevance to client value so executives can prioritize where to invest (people, standardization, automation, QA).

## 2. Users & Context

- Primary users: directors and executives responsible for allocating budget, headcount, and operational improvements.
- User goal: decide where to invest so client-perceived value increases and ROI is defensible.
- Context: strategic planning and operational review, after client and internal interview material has been collected.
- Secondary stakeholders: analysts or operators who ingest interview documents and review graph quality before executives consume rankings and process views.

## 3. Scope (In / Out)

### In Scope

- Ingest text documents and interview transcriptions (internal organization interviews and client interviews).
- **Client path**: analyze client interviews with an LLM to extract value signals and condense them into a defined set of value metrics (business language with a mathematical representation).
- **Internal path**: extract entities and relationships from internal interviews and materialize them in a knowledge graph using the existing ontology.
- **Bridge**: quantify activity and process relevance to value streams; rank/classify by contribution to extracted metrics using factors such as graph position, dependency impact, failure risk, and activity frequency within a process.
- Produce a knowledge graph stored in **Neo4j Aura**.
- Present results and graph construction with enough **explainability** for users to understand how entities, relationships, and scores were derived.
- Graph hygiene: deduplicate entities, prune weak or duplicate edges, and surface conflicting perspectives from multiple interview sources.

### Out of Scope

- Natural-language querying of the graph or a chatbot over Neo4j (planned soon after v1).
- Business logic encoded in the graph for simulation, strategy planning, or digital-company identity use cases beyond v1 value-stream analysis.
- Making Neo4j actively useful as a query surface in v1 (persistence only; query logic comes later).
- Sentiment analysis as a dedicated pipeline in v1 (LLM extraction only; sentiment may be added later).
- Running the graph or analysis fully local/offline (v1 depends on cloud Neo4j Aura).
- `[MISSING]` — authentication, multi-tenant organization model, and deployment topology.

## 4. Core Behavior

- User uploads client interview transcriptions → system extracts value-related signals with an LLM → system produces a consolidated set of value metrics.
- User uploads internal interview transcriptions and related text → system extracts entities and relationships → system maps them to the existing ontology → system writes/updates the knowledge graph in Neo4j Aura.
- System links internal activities and processes to client value metrics → system quantifies each activity’s impact and ranks processes by distance/contribution to those metrics → system presents the most valuable activities, process dependencies, and end-to-end flows.
- System detects duplicate entities and redundant or weak relationships → system prunes or consolidates where confidence rules allow → system flags contradictory relationships arising from different interview perspectives.
- User reviews explainable views of graph construction and scoring → user uses ranked activities/processes to inform investment decisions (staffing, standardization, automation, QA).

## 5. Success Criteria

- Executives can identify the highest-value activities and processes tied to client-perceived value, with visible end-to-end process dependencies.
- Each ranked activity/process includes quantified relevance and enough descriptive context to support an investment decision.
- The knowledge graph in Neo4j Aura reflects the ontology, with materially reduced duplicate entities and pruned low-confidence edges compared to raw extraction output.
- Conflicting or ambiguous relationships from multiple interviewees are visible rather than silently merged into a misleading graph.
- Users can trace how key graph elements and scores were produced (explainability), not only see final rankings.
- Failure signals: unusable graph (heavy duplication, contradictions hidden, or low confidence), rankings that cannot be explained, or extraction/quantification accuracy too weak to trust for decisions.

## 6. Constraints & Assumptions

**Constraints**

- v1 must use **Neo4j Aura** as the graph database (cloud-hosted).
- An **existing ontology** defines allowed entities and relationships for the knowledge graph.
- Primary unstructured input is **text documents and interview transcriptions**.
- v1 client-value extraction uses **LLM analysis** (not a separate sentiment pipeline).
- **Accuracy and graph quality** are first-class requirements: extraction, deduplication, pruning, and conflict handling directly affect product value.
- The UI must support **explainability** of graph building and quantification, not only final dashboards.
- v1 stores the graph in Neo4j but does **not** yet expose rich query/chat behavior over stored business logic.

**Assumptions**

- Sufficient interview and document material exists to extract both client value metrics and internal process structure.
- The existing ontology is adequate for representing activities, processes, dependencies, and their linkage to value metrics in v1.
- Multiple internal interviewees may describe the same work differently; perspective variance is expected and must be handled explicitly.
- Duplicate entities across documents can reinforce confidence when aligned; misaligned duplicates indicate extraction or modeling error.
- Future versions will reuse this knowledge graph for simulations, strategy, and a queryable digital identity of the company.

## 7. Risks & Unknowns

- `[UNCLEAR: metric formula]` — exact mathematical definition and weighting of client value metrics and activity quantification formulas.
- `[UNCLEAR: pruning rules]` — precise thresholds and rules for edge pruning, entity deduplication, and conflict resolution.
- `[UNCLEAR: UI scope]` — depth of explainability views vs. summary dashboards in v1.
- `[MISSING]` — non-functional targets (latency, document volume limits, concurrent users).
- `[MISSING]` — supported document formats, languages, and ingestion workflow.
- Risk: automatic extraction produces duplicate entities or wrong relationships, degrading rankings and executive trust.
- Risk: contradictory interview perspectives are flattened incorrectly, hiding real organizational disagreement.
- Risk: quantification logic is opaque despite explainability requirements, limiting decision usefulness.
- Risk: Neo4j is populated in v1 before query logic exists, creating a schema/ modeling burden for the near-term chatbot phase.
