# ADR 0001 — Value stream discovery via delivery-anchored Steiner trees

**Status:** Accepted  
**Date:** 2026-06-15

## Context

The first VS implementation (`analitics` / ga-05) discovered one linear path per metric by enumerating `all_simple_paths` between demand and value-realization events and scoring paths with average `Relevance(A,M)`.

Product documentation (`VS_Selection_Protocol.md`) defines a richer model: economic stories are groups of events anchored by delivery, connected as **trees** (not single paths) via approximate Steiner trees on the `flow` subgraph, with multi-metric normalized relevance on edge costs and a **backbone** from cross-story overlap.

## Decision

1. Replace per-metric path discovery with **delivery-anchored event grouping** + **Steiner tree** per group (`networkx.algorithms.approximation.steiner_tree` on the delivery connected component).
2. Score edges with **cumulative relevance** after per-metric min-max normalization (equal weight per metric).
3. Expose **group-centric** outputs: `ValueStreamTree`, `node_overlap`, `backbone`, `group_count`, `avg_group_size`.
4. UI focus key changes from `metric_id` to `delivery_event_id`; focus highlights all metrics linked via AFFECTS from visible activities.
5. Keep **classification** (VS → structural → semantic → waste) unchanged; only `vs_union` sourcing changes.
6. Optional `merge_crossing_groups` remains off by default (diagnostic only).

## Consequences

- **Breaking:** `ValueStreamResult` / `streams` / `primary_path` removed; `GraphFilter.value_stream_focus_metric_id` → `value_stream_focus_delivery_id`.
- **Positive:** Convergent multi-anchor flows (margin + demand) render as trees; backbone surfaces shared infrastructure with overlap counts.
- **Degenerate case:** Sparse graphs still yield isolated demand→delivery pairs (same algorithm, minimal groups).
- **Tests:** `tests/graph_analytics/test_value_streams.py` rewritten; fixtures extended for convergence and backbone cases.

## References

- [`docs/VS_Selection_Protocol.md`](../VS_Selection_Protocol.md)
- [`docs/VS_Analytics_Module.md`](../VS_Analytics_Module.md) (Part 2+ classification)
- [`src/optimizer/graph_analytics/value_streams.py`](../../src/optimizer/graph_analytics/value_streams.py)
