from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Callable

from pyvis.network import Network

from optimizer.infrastructure.visualization.colors import (
    HEATMAP_COLOR_HIGH,
    HEATMAP_COLOR_LOW,
    relevance_heatmap_color,
)

NODE_TYPE_COLORS: dict[str, str] = {
    "Activity": "#4CAF50",
    "Process": "#2196F3",
    "Metric": "#FF9800",
    "Organization": "#9C27B0",
    "Person": "#E91E63",
    "Department": "#00BCD4",
    "Goal": "#FFC107",
    "Capability": "#795548",
    "CustomerJourneyStep": "#AB47BC",
    "MetricDriver": "#FFB74D",
    "Team": "#26A69A",
    "System": "#78909C",
    "Event": "#EF5350",
    "Intent": "#8D6E63",
}

DIM_COLOR = "#555555"
HIGHLIGHT_FALLBACK_COLOR = "#BDBDBD"
PUNTO_CIEGO_LABEL = "punto ciego"

VS_CATEGORY_COLORS: dict[str, str] = {
    "value_stream": "#FFC107",
    "structural_support": "#2196F3",
    "semantic_support": "#42A5F5",
    "waste": "#F44336",
}

VS_BOUNDARY_EVENT_COLOR = "#FFD700"
VS_FLOW_EDGE_COLOR = "#FF9800"
VS_SUPPORT_EDGE_COLOR = "#2196F3"
VS_METRIC_NODE_COLOR = "#66BB6A"
VS_METRIC_DRIVER_NODE_COLOR = "#2E7D32"
VS_METRIC_EDGE_COLOR = "#4CAF50"

GENERATED_NODE_BORDER_COLOR = "#E040FB"
GENERATED_EDGE_COLOR = "#FF9800"
GENERATED_EDGE_DASH_PATTERN = (8, 6)

ACTIVITY_FACTOR_LABELS: dict[str, str] = {
    "p": "Posición",
    "c": "Causalidad",
    "f": "Frecuencia",
    "r": "Riesgo",
    "v": "Valor interno",
}


@dataclass(frozen=True)
class VisualizeOptions:
    color_map: dict[str, str] = field(default_factory=lambda: dict(NODE_TYPE_COLORS))
    relevance_pull_enabled: bool = False
    edge_relevance_map: dict[tuple[str, str], float] = field(default_factory=dict)
    indirect_relevance_map: dict[tuple[str, str], float] = field(default_factory=dict)
    highlight_node_ids: frozenset[str] | None = None
    highlight_edge_keys: frozenset[tuple[str, str, str]] | None = None
    edge_color_overrides: dict[tuple[str, str, str], str] = field(default_factory=dict)
    node_color_overrides: dict[str, str] = field(default_factory=dict)
    node_size_overrides: dict[str, float] = field(default_factory=dict)
    edge_width_overrides: dict[tuple[str, str, str], float] = field(default_factory=dict)
    node_opacity_overrides: dict[str, float] = field(default_factory=dict)
    edge_opacity_overrides: dict[tuple[str, str, str], float] = field(default_factory=dict)
    generated_node_ids: frozenset[str] = frozenset()
    generated_edge_keys: frozenset[tuple[str, str, str]] = frozenset()
    generated_emphasis_active: bool = False
    node_title_builder: Callable | None = None


def _node_display_label(node):
    properties = node.properties or {}
    return properties.get("label") or node.id


def _default_node_title(node) -> str:
    properties = node.properties or {}
    parts: list[str] = []

    if node.type in ("Activity", "Process"):
        display = properties.get("label")
        if display and display != node.id:
            parts.append(f"{node.id} — {display}")
        else:
            parts.append(node.id)
        parts.append(node.type)
    else:
        parts.append(node.type or "Node")

    description = properties.get("description")
    if description:
        parts.append(str(description))

    if node.type == "Activity":
        frequency = properties.get("frequency")
        if frequency:
            parts.append(f"Frecuencia operativa: {frequency}")
        for key in ("p", "c", "f", "r", "v"):
            if key in properties and properties[key] is not None:
                parts.append(f"{ACTIVITY_FACTOR_LABELS[key]}: {properties[key]}")

    if properties.get("generated") is True:
        parts.append("Generado: sí")
        if properties.get("generation_basis"):
            parts.append(f"Base: {properties['generation_basis']}")
    if properties.get("confidence") is not None:
        parts.append(f"Confianza: {properties['confidence']}")
    if properties.get("corroboration") is not None:
        parts.append(f"Corroboración: {properties['corroboration']}")
    if properties.get("informant_distance") is not None:
        parts.append(f"Distancia informante: {properties['informant_distance']}")
    evidence = properties.get("evidence_pointer")
    if evidence:
        parts.append(f"Evidencia: {evidence}")

    return "\n".join(parts)


def _relevance_pull_style(relevance: float) -> dict:
    clamped = max(0.0, min(float(relevance), 1.0))
    return {
        "length": max(20.0, 200.0 * (1.0 - clamped)),
        "width": 1.0 + clamped * 4.0,
        "value": clamped,
    }


def _edge_style(
    source_id: str,
    target_id: str,
    rel_type: str,
    options: VisualizeOptions | None,
) -> dict:
    if options is None or not options.relevance_pull_enabled:
        return {}
    if rel_type.upper() != "AFFECTS":
        return {}

    relevance = options.edge_relevance_map.get((source_id, target_id))
    if relevance is None:
        relevance = options.edge_relevance_map.get((target_id, source_id))
    if relevance is None:
        return {}

    return _relevance_pull_style(relevance)


def _node_color(node_id: str, node_type: str | None, options: VisualizeOptions | None, color_map: dict[str, str]) -> str | None:
    if options is not None and options.node_color_overrides:
        override = options.node_color_overrides.get(node_id)
        if override:
            return override
    if options is not None and options.highlight_node_ids is not None:
        if node_id not in options.highlight_node_ids:
            return DIM_COLOR
    color = color_map.get(node_type or "")
    if color:
        return color
    if (
        options is not None
        and options.highlight_node_ids is not None
        and node_id in options.highlight_node_ids
    ):
        return HIGHLIGHT_FALLBACK_COLOR
    return None


def _edge_dim_kwargs(
    source_id: str,
    target_id: str,
    rel_type: str,
    options: VisualizeOptions | None,
) -> dict:
    if options is None or options.highlight_edge_keys is None:
        return {}
    edge_key = (source_id, target_id, rel_type.upper())
    if edge_key in options.highlight_edge_keys:
        override = options.edge_color_overrides.get(edge_key)
        width_override = options.edge_width_overrides.get(edge_key) if options else None
        if override:
            style: dict = {"color": override}
            if rel_type.upper() == "PRECEDES":
                style["width"] = width_override if width_override is not None else 2.5
            elif rel_type.upper() in ("AFFECTS", "DRIVES"):
                style["width"] = 2.0
            return style
        return {}
    return {"color": DIM_COLOR}


def visualize_graph(graph_documents, options: VisualizeOptions | None = None):
    """
    Visualizes a knowledge graph using PyVis based on the extracted graph documents.

    Args:
        graph_documents (list): A list of GraphDocument objects with nodes and relationships.
        options: Optional styling hooks (colors, relevance pull, tooltips, explain highlight).

    Returns:
        pyvis.network.Network: The visualized network graph object.
    """
    net = Network(
        height="1200px",
        width="100%",
        directed=True,
        notebook=False,
        bgcolor="#222222",
        font_color="white",
        filter_menu=True,
        cdn_resources="remote",
    )

    nodes = graph_documents[0].nodes
    relationships = graph_documents[0].relationships

    node_dict = {node.id: node for node in nodes}
    color_map = (options.color_map if options else None) or NODE_TYPE_COLORS
    title_builder = (
        options.node_title_builder if options else None
    ) or _default_node_title

    valid_edges = []
    for rel in relationships:
        if rel.source.id in node_dict and rel.target.id in node_dict:
            valid_edges.append(rel)

    for node_id, node in node_dict.items():
        node_kwargs = {
            "label": _node_display_label(node),
            "title": title_builder(node),
            "group": node.type,
        }
        if options and options.node_size_overrides:
            size = options.node_size_overrides.get(node_id)
            if size is not None:
                node_kwargs["size"] = size
        color = _node_color(node_id, node.type, options, color_map)
        try:
            net.add_node(node.id, **node_kwargs)
            if color:
                for index, graph_node in enumerate(net.nodes):
                    if graph_node["id"] == node.id:
                        is_generated = (
                            options
                            and options.generated_emphasis_active
                            and node_id in options.generated_node_ids
                        )
                        opacity = None
                        if options and options.node_opacity_overrides:
                            opacity = options.node_opacity_overrides.get(node_id)
                        if is_generated:
                            net.nodes[index]["color"] = {
                                "background": color,
                                "border": GENERATED_NODE_BORDER_COLOR,
                                "highlight": {
                                    "background": color,
                                    "border": "#FFD700",
                                },
                            }
                            net.nodes[index]["borderWidth"] = 2
                        else:
                            net.nodes[index]["color"] = color
                        if opacity is not None:
                            net.nodes[index]["opacity"] = opacity
                        break
        except Exception:
            continue

    for rel in valid_edges:
        edge_kwargs = {
            **_edge_style(rel.source.id, rel.target.id, rel.type, options),
            **_edge_dim_kwargs(rel.source.id, rel.target.id, rel.type, options),
        }
        try:
            net.add_edge(
                rel.source.id,
                rel.target.id,
                label=rel.type.lower(),
                **edge_kwargs,
            )
            if options and options.edge_opacity_overrides:
                edge_key = (rel.source.id, rel.target.id, rel.type.upper())
                opacity = options.edge_opacity_overrides.get(edge_key)
                if opacity is not None:
                    for index, graph_edge in enumerate(net.edges):
                        if (
                            graph_edge["from"] == rel.source.id
                            and graph_edge["to"] == rel.target.id
                        ):
                            existing = graph_edge.get("color")
                            if isinstance(existing, dict):
                                graph_edge["color"]["opacity"] = opacity
                            else:
                                graph_edge["color"] = {"color": existing or DIM_COLOR, "opacity": opacity}
                            net.edges[index] = graph_edge
                            break
            if (
                options
                and options.generated_emphasis_active
                and (rel.source.id, rel.target.id, rel.type.upper())
                in options.generated_edge_keys
            ):
                for index, graph_edge in enumerate(net.edges):
                    if (
                        graph_edge["from"] == rel.source.id
                        and graph_edge["to"] == rel.target.id
                    ):
                        graph_edge["dashes"] = True
                        graph_edge["color"] = GENERATED_EDGE_COLOR
                        net.edges[index] = graph_edge
                        break
        except Exception:
            continue

    if options and options.relevance_pull_enabled and options.indirect_relevance_map:
        for (source_id, target_id), relevance in options.indirect_relevance_map.items():
            if source_id not in node_dict or target_id not in node_dict:
                continue
            edge_kwargs = {
                "dashes": True,
                "label": PUNTO_CIEGO_LABEL,
                **_relevance_pull_style(relevance),
            }
            try:
                net.add_edge(source_id, target_id, **edge_kwargs)
            except Exception:
                continue

    net.set_options(
        """
        {
            "physics": {
                "forceAtlas2Based": {
                    "gravitationalConstant": -100,
                    "centralGravity": 0.01,
                    "springLength": 200,
                    "springConstant": 0.08
                },
                "minVelocity": 0.75,
                "solver": "forceAtlas2Based"
            }
        }
    """
    )

    output_file = "knowledge_graph.html"
    try:
        net.save_graph(output_file)
        print(f"Graph saved to {os.path.abspath(output_file)}")
        return net
    except Exception as e:
        print(f"Error saving graph: {e}")
        return None
