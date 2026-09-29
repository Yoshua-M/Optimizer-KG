"""Run CoherenceCheckProtocol cycle on a demo scenario or graph.json."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from optimizer.graph_hygiene.protocol import (
    document_to_graph_json,
    format_protocol_report,
    run_protocol_cycle,
)
from optimizer.graph_hygiene.sanitize_labels import sanitize_graph_document
from optimizer.infrastructure.demo_loader import (
    graph_json_to_graph_documents,
    load_demo_bundle,
    resolve_repo_root,
)


def run_coherence_protocol(
    *,
    scenario_id: str | None = None,
    graph_json: Path | None = None,
    output_path: Path | None = None,
    repaired_graph_path: Path | None = None,
    repo_root: Path | None = None,
    sanitize_labels: bool = True,
    max_iters: int = 5,
    authorize_ontology: bool = False,
) -> str:
    if (scenario_id is None) == (graph_json is None):
        raise ValueError("Pass exactly one of scenario_id or graph_json")
    root = repo_root or resolve_repo_root()
    if scenario_id is not None:
        bundle = load_demo_bundle(scenario_id, repo_root=root)
        document = bundle.graph_documents[0]
        meta = {"scenario_id": scenario_id, "title": bundle.scenario.title}
    else:
        payload = json.loads(Path(graph_json).read_text(encoding="utf-8"))
        document = graph_json_to_graph_documents(payload)[0]
        meta = {k: payload[k] for k in ("scenario_id", "title", "source") if k in payload}

    if sanitize_labels:
        sanitize_graph_document(document)

    result = run_protocol_cycle(
        document, max_iters=max_iters, authorize_ontology=authorize_ontology
    )
    text = format_protocol_report(result)

    if repaired_graph_path is not None and result.document is not None:
        Path(repaired_graph_path).write_text(
            json.dumps(
                document_to_graph_json(
                    result.document,
                    meta={
                        **meta,
                        "meta": {
                            "coherence_protocol": True,
                            "iterations": result.iterations,
                            "converged": result.converged,
                            "authorize_ontology": authorize_ontology,
                        },
                    },
                ),
                ensure_ascii=False,
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )

    if output_path is not None:
        Path(output_path).write_text(text, encoding="utf-8")
    return text


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="CoherenceCheckProtocol cycle + Salidas report.")
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--scenario", help="Demo scenario id")
    source.add_argument("--graph", type=Path, help="Path to graph.json")
    parser.add_argument("-o", "--output", type=Path, help="Write protocol report markdown")
    parser.add_argument(
        "--repaired-graph",
        type=Path,
        help="Write graph.json after repairs",
    )
    parser.add_argument("--max-iters", type=int, default=5)
    parser.add_argument(
        "--authorize-ontology",
        action="store_true",
        help="Allow ontology-layer repairs (R3 intent merges, new Intent/Metric). Topology always runs.",
    )
    args = parser.parse_args(argv)
    text = run_coherence_protocol(
        scenario_id=args.scenario,
        graph_json=args.graph,
        output_path=args.output,
        repaired_graph_path=args.repaired_graph,
        max_iters=args.max_iters,
        authorize_ontology=args.authorize_ontology,
    )
    if args.output is None:
        sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
