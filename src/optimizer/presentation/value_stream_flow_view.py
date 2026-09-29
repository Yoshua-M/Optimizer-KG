from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

import streamlit.components.v1 as components

from optimizer.graph_analytics.value_stream_flow import ValueStreamFlowGraph

_STATIC_DIR = Path(__file__).resolve().parent / "static"
_TEMPLATE_PATH = _STATIC_DIR / "value_stream_flow.html"
_VENDOR_FILES = (
    "cytoscape.min.js",
    "dagre.min.js",
    "cytoscape-dagre.js",
)


@lru_cache(maxsize=1)
def _vendor_script_tags() -> str:
    """Inline vendored JS so Streamlit iframe does not depend on broken CDN paths."""
    tags: list[str] = []
    for filename in _VENDOR_FILES:
        path = _STATIC_DIR / "vendor" / filename
        if not path.is_file():
            raise FileNotFoundError(f"Missing flow diagram vendor script: {path}")
        tags.append(f"<script>\n{path.read_text(encoding='utf-8')}\n</script>")
    return "\n".join(tags)


def _html_template() -> str:
    template = _TEMPLATE_PATH.read_text(encoding="utf-8")
    return template.replace("__VENDOR_SCRIPTS__", _vendor_script_tags())


def render_value_stream_flow_html(
    flow_graph: ValueStreamFlowGraph,
    *,
    height: int = 620,
    generated_opacity: float = 0.2,
) -> None:
    """Embed an interactive Cytoscape+dagre value-stream flow diagram."""
    payload = flow_graph.to_dict()
    payload["generated_opacity"] = max(0.05, min(float(generated_opacity), 1.0))
    payload_json = json.dumps(payload, ensure_ascii=False)
    payload_json = payload_json.replace("</", "<\\/")
    html = _html_template().replace("__FLOW_PAYLOAD_JSON__", payload_json)
    components.html(html, height=height, scrolling=False)
