#!/usr/bin/env python3
"""Build Eneroil (real interview data, no metrics) structural demo fixtures.

Source inventory: data/raw/Eneroil_Inventario_Grafo_v1.md — a real-client
extraction (interview) with NO Metric nodes and NO P/C/F/R/V quantification.
The scenario is registered with kind="structural" so the demo UI can disable
metric-dependent features.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = REPO_ROOT / "configs/demo_scenarios.json"
INVENTORY_PATH = REPO_ROOT / "data/raw/Eneroil_Inventario_Grafo_v1.md"
OUT_DIR = REPO_ROOT / "data/processed/demo/eneroil_real_v1"

SCENARIO_ID = "eneroil_real_v1"
SCENARIO_TITLE = "Eneroil (datos reales) v1"
SCENARIO_DESCRIPTION = (
    "Experimental: inventario extraído de entrevista interna real — grafo "
    "estructural sin métricas de valor (Capa 3 pendiente de investigación JTBD)"
)
GRAPH_TITLE = "Eneroil S.A. de C.V. — extracción real v1 (sin métricas)"

# Owner label (Activity table "Equipo dueño" column) → Team node ids.
# "Proveedor (externo)" is an external actor with no Team node — no PERFORMS.
TEAM_IDS_BY_OWNER_LABEL: dict[str, tuple[str, ...]] = {
    "Comercial": ("TEA-03",),
    "Monitoreo y Precios": ("TEA-02",),
    "Planeación": ("TEA-04",),
    "Compras": ("TEA-05",),
    "Facturación": ("TEA-06",),
    "Cobranza": ("TEA-08",),
    "Cobranza / Dirección": ("TEA-08", "TEA-01"),
    "Calidad / Cumplimiento": ("TEA-07",),
    "Dirección General": ("TEA-01",),
    "Dirección / Cumplimiento": ("TEA-01", "TEA-07"),
    "Proveedor (externo)": (),
}

# PRECEDES: main demanda→cobro chain + exception branch + price feed (from
# "Relaciones tipificadas" prose in the inventory).
PRECEDES_MAIN_CHAIN = [
    "ACT-01", "ACT-03", "ACT-04", "ACT-05", "ACT-06", "ACT-07", "ACT-08",
    "ACT-09", "ACT-10", "ACT-11", "ACT-12", "ACT-13", "ACT-14",
]
PRECEDES_EXTRA = [
    ("ACT-02", "ACT-03"),
    ("ACT-12", "ACT-15"),
    ("ACT-15", "ACT-16"),
    ("ACT-16", "ACT-17"),
]

USES_SYSTEM = [
    ("ACT-01", "SYS-03"),
    ("ACT-01", "SYS-04"),
    ("ACT-09", "SYS-01"),
    ("ACT-10", "SYS-02"),
    ("ACT-11", "SYS-04"),
    ("ACT-13", "SYS-01"),
    ("ACT-13", "SYS-05"),
    ("ACT-14", "SYS-01"),
]

# (activity, event, role): "responde_a" = event triggers activity,
# "produce" = activity emits event. Used for synthetic Event↔Activity PRECEDES.
INVOLVES_EVENT = [
    ("ACT-01", "EVT-01", "responde_a"),
    ("ACT-03", "EVT-02", "produce"),
    ("ACT-04", "EVT-03", "produce"),
    ("ACT-06", "EVT-04", "produce"),
    ("ACT-08", "EVT-05", "produce"),
    ("ACT-10", "EVT-06", "produce"),
    ("ACT-14", "EVT-07", "produce"),
    ("ACT-15", "EVT-08", "responde_a"),
]

EVENT_TYPES = {
    "EVT-01": "demand",
    "EVT-02": "milestone",
    "EVT-03": "milestone",
    "EVT-04": "milestone",
    "EVT-05": "milestone",
    "EVT-06": "milestone",  # realización parcial de valor (CFDI timbrado)
    "EVT-07": "value_realization",
    "EVT-08": "exception",
}

# Activity —[SUPPORTS]→ Capability, derived from the inventory tables
# ("derivables directamente de las tablas anteriores").
SUPPORTS_BY_CAPABILITY: dict[str, list[str]] = {
    "CAP-01": ["ACT-02"],
    "CAP-02": ["ACT-01", "ACT-03", "ACT-04"],
    "CAP-03": ["ACT-05", "ACT-07"],
    "CAP-04": ["ACT-06", "ACT-08", "ACT-09"],
    "CAP-05": ["ACT-10", "ACT-11"],
    "CAP-06": ["ACT-12", "ACT-13", "ACT-14", "ACT-15", "ACT-16", "ACT-17"],
    "CAP-07": ["ACT-18", "ACT-23"],
    "CAP-08": ["ACT-19", "ACT-20", "ACT-21", "ACT-22"],
}

# Team —[OWNS]→ Process / Capability, derived from process/capability tables.
OWNS = [
    ("TEA-02", "PRO-01"), ("TEA-02", "CAP-01"),
    ("TEA-03", "PRO-02"), ("TEA-03", "CAP-02"),
    ("TEA-04", "PRO-03"), ("TEA-04", "CAP-03"),
    ("TEA-05", "PRO-04"), ("TEA-05", "CAP-04"),
    ("TEA-06", "PRO-05"), ("TEA-06", "CAP-05"),
    ("TEA-08", "PRO-06"), ("TEA-08", "CAP-06"),
    ("TEA-07", "PRO-07"), ("TEA-07", "PRO-08"), ("TEA-07", "PRO-09"),
    ("TEA-07", "CAP-07"), ("TEA-07", "CAP-08"),
]

# Metric hypotheses (NOT graphed as Metric nodes — pending JTBD validation).
METRIC_HYPOTHESES = [
    {
        "id": "M?-01",
        "name": "Confiabilidad de entrega",
        "definition": (
            "Producto correcto, volumen, destino y fecha según lo pactado."
        ),
    },
    {
        "id": "M?-02",
        "name": "Exactitud y puntualidad de facturación percibida",
        "definition": (
            "El cliente recibe un CFDI correcto y a tiempo "
            "(mismo día de entrega en el escenario ideal)."
        ),
    },
    {
        "id": "M?-03",
        "name": "Transparencia de cuenta",
        "definition": (
            "El cliente recibe estado de cuenta correcto y puntual, sin disputas."
        ),
    },
]


def section(md: str, header_prefix: str) -> str:
    pattern = re.compile(rf"^## {re.escape(header_prefix)}", re.MULTILINE)
    match = pattern.search(md)
    if not match:
        raise ValueError(f"Inventory section not found: ## {header_prefix}")
    start = match.end()
    nxt = re.search(r"^## ", md[start:], re.MULTILINE)
    return md[start : start + nxt.start()] if nxt else md[start:]


def parse_table_rows(section_text: str, id_pattern: str) -> list[list[str]]:
    """Return table rows whose first cell matches *id_pattern* (skips headers)."""
    id_re = re.compile(id_pattern)
    rows: list[list[str]] = []
    for line in section_text.splitlines():
        line = line.strip()
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if cells and id_re.fullmatch(cells[0]):
            rows.append(cells)
    return rows


def strip_markdown(text: str) -> str:
    return re.sub(r"\*+", "", text).strip()


def expand_activity_spec(spec: str) -> list[str]:
    """Expand 'ACT-01, ACT-03' and 'ACT-12 – ACT-17' specs into id lists."""
    ids: list[str] = []
    range_match = re.match(r"ACT-(\d+)\s*[–—-]\s*ACT-(\d+)", spec.strip())
    if range_match:
        start, end = int(range_match.group(1)), int(range_match.group(2))
        return [f"ACT-{i:02d}" for i in range(start, end + 1)]
    for part in re.split(r",\s*", spec.strip()):
        id_match = re.match(r"(ACT-\d+)", part.strip())
        if id_match:
            ids.append(id_match.group(1))
    return ids


def upsert_manifest(entry: dict) -> None:
    if CONFIG_PATH.is_file():
        data = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    else:
        data = {"scenarios": []}
    scenarios = [s for s in data.get("scenarios", []) if s.get("id") != entry["id"]]
    scenarios.append(entry)
    data["scenarios"] = sorted(scenarios, key=lambda s: s["id"])
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    CONFIG_PATH.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def build() -> None:
    md = INVENTORY_PATH.read_text(encoding="utf-8")

    nodes: list[dict] = []
    relationships: list[dict] = []

    def add_node(nid: str, ntype: str, label: str, **props: object) -> None:
        nodes.append(
            {
                "id": nid,
                "type": ntype,
                "label": label,
                "properties": {k: v for k, v in props.items() if v is not None},
            }
        )

    def add_rel(
        source: str,
        target: str,
        rtype: str,
        *,
        synthetic: bool = False,
        derived: bool = False,
        **props: object,
    ) -> None:
        properties = {k: v for k, v in props.items() if v is not None}
        if synthetic:
            properties["synthetic"] = True
        if derived:
            properties["derived"] = True
        relationships.append(
            {
                "source": source,
                "target": target,
                "type": rtype,
                "properties": properties,
            }
        )

    # --- Process (named only; PRO-10/PRO-11 are unnamed placeholders) ---
    process_by_activity: dict[str, str] = {}
    part_of: list[tuple[str, str]] = []
    for row in parse_table_rows(section(md, "Process"), r"PRO-\d+"):
        pid, name, activities_cell = row[0], strip_markdown(row[1]), row[2]
        if not name or "sin nombrar" in name.lower():
            continue
        add_node(pid, "Process", name)
        for aid in expand_activity_spec(activities_cell):
            process_by_activity[aid] = pid
            part_of.append((aid, pid))

    # --- Activity ---
    activity_ids: list[str] = []
    performs: list[tuple[str, str]] = []
    for row in parse_table_rows(section(md, "Activity"), r"ACT-\d+"):
        aid, name, owner_label = row[0], row[1], strip_markdown(row[2])
        activity_ids.append(aid)
        team_ids = TEAM_IDS_BY_OWNER_LABEL.get(owner_label)
        if team_ids is None:
            raise ValueError(f"{aid}: unmapped owner label {owner_label!r}")
        add_node(
            aid,
            "Activity",
            name,
            process_id=process_by_activity.get(aid),
            team_label=owner_label,
            external_owner=True if not team_ids else None,
        )
        for team_id in team_ids:
            performs.append((team_id, aid))

    for aid, pid in part_of:
        add_rel(aid, pid, "PART_OF")
    for team_id, aid in performs:
        add_rel(team_id, aid, "PERFORMS")

    # --- Team / Capability / System ---
    for row in parse_table_rows(section(md, "Team"), r"TEA-\d+"):
        add_node(row[0], "Team", strip_markdown(row[1].split("*(")[0]))
    for row in parse_table_rows(section(md, "Capability"), r"CAP-\d+"):
        add_node(row[0], "Capability", row[1])
    for row in parse_table_rows(section(md, "System"), r"SYS-\d+"):
        add_node(row[0], "System", row[1], function=row[2])

    # --- Event ---
    for row in parse_table_rows(section(md, "Event"), r"EVT-\d+"):
        eid, name, role = row[0], row[1], strip_markdown(row[2])
        add_node(eid, "Event", name, description=role, event_type=EVENT_TYPES[eid])

    # --- CustomerJourneyStep (inferred from internal interview) ---
    for row in parse_table_rows(section(md, "CustomerJourneyStep"), r"CJS-\d+"):
        add_node(row[0], "CustomerJourneyStep", row[1], status="inferred")

    # --- MetricDriver candidates (suspended: no Metric nodes yet) ---
    metric_drivers: list[dict] = []
    for row in parse_table_rows(section(md, "MetricDriver"), r"MDR-\d+"):
        did, name, hypothetical = row[0], row[1], row[2]
        metric_drivers.append(
            {
                "id": did,
                "parent_metric_id": None,
                "name": name,
                "description": "",
                "status": "candidate",
                "hypothetical_metric": hypothetical,
            }
        )
        add_node(
            did,
            "MetricDriver",
            name,
            status="candidate",
            hypothetical_metric=hypothetical,
        )

    # --- PRECEDES ---
    precedes_edges: set[tuple[str, str]] = set()
    for left, right in zip(PRECEDES_MAIN_CHAIN, PRECEDES_MAIN_CHAIN[1:]):
        precedes_edges.add((left, right))
        add_rel(left, right, "PRECEDES")
    for left, right in PRECEDES_EXTRA:
        precedes_edges.add((left, right))
        add_rel(left, right, "PRECEDES")

    # --- USES_SYSTEM ---
    for aid, sid in USES_SYSTEM:
        add_rel(aid, sid, "USES_SYSTEM")

    # --- INVOLVES_EVENT + synthetic Event↔Activity PRECEDES (VS discovery) ---
    for aid, eid, role in INVOLVES_EVENT:
        add_rel(aid, eid, "INVOLVES_EVENT", event_role=role)
        if role == "responde_a":
            precedes_edges.add((eid, aid))
            add_rel(eid, aid, "PRECEDES", synthetic=True)
        elif role == "produce":
            precedes_edges.add((aid, eid))
            add_rel(aid, eid, "PRECEDES", synthetic=True)

    # --- SUPPORTS / OWNS (derived) ---
    for cap_id, act_ids in SUPPORTS_BY_CAPABILITY.items():
        for aid in act_ids:
            add_rel(aid, cap_id, "SUPPORTS", derived=True)
    for team_id, owned_id in OWNS:
        add_rel(team_id, owned_id, "OWNS", derived=True)

    _validate(nodes, relationships, precedes_edges)

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    graph_doc = {
        "scenario_id": SCENARIO_ID,
        "title": GRAPH_TITLE,
        "source": str(INVENTORY_PATH.relative_to(REPO_ROOT)),
        "meta": {
            "kind": "structural",
            "source_nature": "real_interview_extraction",
            "metrics_available": False,
            "note": (
                "Extracción de entrevista interna real (Eneroil, junio 2026). "
                "Sin nodos Metric ni cuantificación P/C/F/R/V — la definición de "
                "métricas de valor requiere primero la ruta cliente (JTBD)."
            ),
            "synthetic_event_precedes": True,
            "synthetic_event_precedes_note": (
                "Event↔Activity PRECEDES derivado de INVOLVES_EVENT event_role "
                "para descubrimiento de value streams."
            ),
            "node_count": len(nodes),
            "relationship_count": len(relationships),
        },
        "nodes": nodes,
        "relationships": relationships,
    }

    metrics_doc = {
        "scenario_id": SCENARIO_ID,
        "metrics": [],
        "metric_drivers": metric_drivers,
        "metric_hypotheses": METRIC_HYPOTHESES,
        "note": (
            "Sin métricas confirmadas: la entrevista es interna y sus KPIs "
            "(DSO, cartera vencida) no califican como Metric de valor cliente. "
            "Las hipótesis M?-01/02/03 requieren validación JTBD."
        ),
    }

    relevance_doc = {
        "scenario_id": SCENARIO_ID,
        "activities": [],
        "matrix": [],
        "process_rollups": [],
        "rankings_by_metric": {},
        "strategic_b_zero": [],
        "note": (
            "Sin cuantificación P/C/F/R/V(A) ni relevancia B×V: puntuar antes de "
            "definir métricas de valor produciría artefactos, no hallazgos."
        ),
    }

    (OUT_DIR / "graph.json").write_text(
        json.dumps(graph_doc, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (OUT_DIR / "metrics.json").write_text(
        json.dumps(metrics_doc, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (OUT_DIR / "relevance.json").write_text(
        json.dumps(relevance_doc, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (OUT_DIR / "copy.md").write_text(_demo_copy(), encoding="utf-8")

    rel_prefix = f"data/processed/demo/{SCENARIO_ID}"
    upsert_manifest(
        {
            "id": SCENARIO_ID,
            "title": SCENARIO_TITLE,
            "description": SCENARIO_DESCRIPTION,
            "kind": "structural",
            "paths": {
                "graph": f"{rel_prefix}/graph.json",
                "metrics": f"{rel_prefix}/metrics.json",
                "relevance": f"{rel_prefix}/relevance.json",
                "copy": f"{rel_prefix}/copy.md",
            },
        }
    )

    print(f"Wrote {OUT_DIR}/graph.json ({len(nodes)} nodes, {len(relationships)} rels)")
    print(f"Wrote {OUT_DIR}/metrics.json (0 metrics, {len(metric_drivers)} driver candidates)")
    print(f"Wrote {OUT_DIR}/relevance.json (empty — sin cuantificación)")
    print(f"Updated manifest entry: {SCENARIO_ID} (kind=structural)")


def _validate(
    nodes: list[dict],
    relationships: list[dict],
    precedes_edges: set[tuple[str, str]],
) -> None:
    node_ids = {node["id"] for node in nodes}
    dangling = [
        (rel["source"], rel["target"], rel["type"])
        for rel in relationships
        if rel["source"] not in node_ids or rel["target"] not in node_ids
    ]
    if dangling:
        raise ValueError(f"Dangling relationship endpoints: {dangling}")

    expected_counts = {
        "Activity": 23,
        "Process": 9,
        "Team": 8,
        "Capability": 8,
        "System": 5,
        "Event": 8,
        "CustomerJourneyStep": 8,
        "MetricDriver": 6,
    }
    actual: dict[str, int] = {}
    for node in nodes:
        actual[node["type"]] = actual.get(node["type"], 0) + 1
    if actual != expected_counts:
        raise ValueError(f"Node counts mismatch: expected {expected_counts}, got {actual}")

    # The demanda→cobro value stream must be walkable: EVT-01 → … → EVT-07.
    chain = ["EVT-01", *PRECEDES_MAIN_CHAIN, "EVT-07"]
    for left, right in zip(chain, chain[1:]):
        if (left, right) not in precedes_edges:
            raise ValueError(f"Missing PRECEDES for value stream: {left} → {right}")


def _demo_copy() -> str:
    return """# Eneroil (datos reales) v1 — escenario estructural

## Qué es este escenario

**Experimento con datos reales de cliente.** A diferencia de los escenarios
Energoil (simulados, con misconceptions embebidas y puntajes P/C/F/R/V
precalculados), este grafo proviene de una **entrevista interna real**
(*Optimizer — Preguntas Iniciales*, Eneroil S.A. de C.V., junio 2026).

## Por qué no hay métricas

La ontología define `Metric` como un **indicador de valor del cliente**
derivado de investigación JTBD — no un KPI interno. La entrevista es interna,
así que sus indicadores (DSO, % cartera vencida, flujo de caja) no califican.
Existen 3 hipótesis de métrica (confiabilidad de entrega, facturación
percibida, transparencia de cuenta) **pendientes de validación con clientes**.

Consecuencias en la UI:

- **Grafo** — completamente funcional (tipos, filtros, value streams).
- **Analíticas** — solo las estructurales dan resultados; las que dependen de
  métricas aparecen como no disponibles.
- **Valor** — sin puntajes P/C/F/R/V ni relevancia B×V; solo el flujo
  demanda→entrega es visible.

## Contenido del grafo

23 actividades, 9 procesos nombrados, 8 equipos, 8 capacidades, 5 sistemas,
8 eventos y 8 pasos de journey (inferidos, requieren validación cliente).
Los 6 `MetricDriver` son candidatos suspendidos hasta definir las métricas.

## Datos

Extracción real v1 sobre Ontología del grafo v2. Fuente:
`data/raw/Eneroil_Inventario_Grafo_v1.md`.
"""


if __name__ == "__main__":
    build()
