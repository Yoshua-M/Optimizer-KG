"""Declarative Optimizer graph ontology (v2.2 Intent layer).

Source of truth for vocabulary: docs/OptimizerGraphOnthologyV2.2.md.
Intent edges are isolated from Phase 1/2 analytics computation.
"""

from __future__ import annotations

# Core node types (pre–Intent)
NODE_TYPES: frozenset[str] = frozenset(
    {
        "Activity",
        "Process",
        "Team",
        "Capability",
        "System",
        "Metric",
        "Event",
        "CustomerJourneyStep",
        "MetricDriver",
        "Document",
        "Source",
        "Intent",  # v2.2
    }
)

# Relationship types used by value computation / flow (Phase 1–2)
COMPUTATION_EDGE_TYPES: frozenset[str] = frozenset(
    {
        "PERFORMS",
        "OWNS",
        "PART_OF",
        "SUPPORTS",
        "USES_SYSTEM",
        "PRECEDES",
        "AFFECTS",
        "DRIVES",
        "HAS_DRIVER",
        "CONTRIBUTES_TO",
        "TOUCHES",
        "INVOLVES_EVENT",
        "MENTIONED_IN",
        "REALIZES",  # v2.1 — coherence/trazabilidad; not read by catalog analytics
    }
)

# v2.2 Intent layer — never feeds V/B/Relevance or subgraph builders
INTENT_EDGE_TYPES: frozenset[str] = frozenset(
    {
        "PURSUES",
        "SERVES",
        "CONFLICTS_WITH",
        "PROMOTED_TO",
    }
)

INTENT_NODE_TYPE = "Intent"

# Protocol-only until folded into ontology doc (CoherenceCheckProtocol)
PROTOCOL_PENDING_EDGE_TYPES: frozenset[str] = frozenset({"VARIANT_OF"})

ALL_EDGE_TYPES: frozenset[str] = (
    COMPUTATION_EDGE_TYPES | INTENT_EDGE_TYPES | PROTOCOL_PENDING_EDGE_TYPES
)

SERVES_TARGET_TYPES: frozenset[str] = frozenset(
    {"Metric", "CustomerJourneyStep", "Event"}
)

CONFLICT_KINDS: frozenset[str] = frozenset({"trade_off", "opposition"})

# Intent generation_basis values (protocol calibration)
INTENT_BASIS_EVIDENCE = "evidence"
INTENT_BASIS_ABDUCTION = "abduction"
ABDUCTION_CONFIDENCE_CEILING = 0.5


def is_intent_edge(rel_type: str) -> bool:
    return rel_type.upper() in INTENT_EDGE_TYPES


def is_computation_edge(rel_type: str) -> bool:
    return rel_type.upper() in COMPUTATION_EDGE_TYPES
