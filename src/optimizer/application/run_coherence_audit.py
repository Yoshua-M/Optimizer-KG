"""Load any demo fixture or graph.json and emit a coherence report. Read-only."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from optimizer.graph_hygiene import (
    audit_coherence,
    format_coherence_report,
    sanitize_graph_document,
)
from optimizer.infrastructure.demo_loader import (
    graph_json_to_graph_documents,
    load_demo_bundle,
    resolve_repo_root,
)


def run_coherence_audit(
    *,
    scenario_id: str | None = None,
    graph_json: Path | None = None,
    output_path: Path | None = None,
    repo_root: Path | None = None,
    sanitize_labels: bool = True,
) -> str:
    if (scenario_id is None) == (graph_json is None):
        raise ValueError("Pass exactly one of scenario_id or graph_json")
    if scenario_id is not None:
        bundle = load_demo_bundle(scenario_id, repo_root=repo_root or resolve_repo_root())
        document = bundle.graph_documents[0]
    else:
        payload = json.loads(Path(graph_json).read_text(encoding="utf-8"))
        document = graph_json_to_graph_documents(payload)[0]
    if sanitize_labels:
        sanitize_graph_document(document)
    text = format_coherence_report(audit_coherence(document), document)
    if output_path is not None:
        Path(output_path).write_text(text, encoding="utf-8")
    return text


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Graph coherence audit (read-only).")
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--scenario", help="Demo scenario id from configs/demo_scenarios.json")
    source.add_argument("--graph", type=Path, help="Path to graph.json")
    parser.add_argument("-o", "--output", type=Path, help="Write markdown here (else stdout)")
    args = parser.parse_args(argv)
    text = run_coherence_audit(
        scenario_id=args.scenario,
        graph_json=args.graph,
        output_path=args.output,
    )
    if args.output is None:
        sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
