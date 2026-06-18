#!/usr/bin/env python3
"""Build Energoil México demo JSON fixtures from Graph Inventory markdown."""

from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = REPO_ROOT / "configs/demo_scenarios.json"

BRIDGE_W = (0.4, 0.4, 0.2)  # G, J, DV

TEAM_BY_LABEL_V1 = {
    "Trading / Inteligencia": "T-01",
    "Abastecimiento": "T-02",
    "Finanzas / Tesorería": "T-03",
    "Compliance / Legal": "T-04",
    "Logística / Operaciones": "T-05",
    "Comercial": "T-06",
    "Comercial / Ops": "T-06",
    "Riesgos": "T-08",
    "Riesgos / Finanzas": "T-08",
    "Riesgos / Logística": "T-08",
    "Dirección / Trading": "T-07",
    "Dirección": "T-07",
    "Dirección / Logística": "T-07",
}

PORTER_TEAM_BY_LABEL = {
    "Núcleo de Gobernanza": "T-01",
    "Gestión de RRHH": "T-02",
    "Desarrollo Tecnológico": "T-03",
    "Abastecimiento": "T-04",
    "Logística Interna": "T-05",
    "Operaciones": "T-06",
    "Logística Externa": "T-07",
    "Marketing y Ventas": "T-08",
    "Servicio Postventa": "T-09",
}

CAPABILITY_RANGES_V1 = [
    (range(1, 6), "CAP-01"),
    (range(6, 11), "CAP-02"),
    (range(11, 16), "CAP-03"),
    (range(16, 22), "CAP-04"),
    (range(22, 28), "CAP-05"),
    (range(28, 35), "CAP-06"),
    (range(35, 40), "CAP-07"),
    (range(40, 44), "CAP-08"),
]

SYNTHETIC_SIGNALS: list[tuple[str, str, float, str]] = [
    ("CJS-01", "M-03", 0.75, "Cliente evalúa precio vs rack en prospección"),
    ("CJS-01", "M-06", 0.55, "Reputación y confianza inicial"),
    ("CJS-02", "M-03", 0.85, "Negociación de precio y margen"),
    ("CJS-02", "M-05", 0.80, "Plazo de crédito en negociación"),
    ("CJS-02", "M-02", 0.50, "Compromiso de volumen"),
    ("CJS-03", "M-05", 0.60, "Condiciones comerciales al alta"),
    ("CJS-03", "M-06", 0.50, "Experiencia de onboarding"),
    ("CJS-04", "M-01", 0.95, "Primera entrega — puntualidad"),
    ("CJS-04", "M-02", 0.90, "Primer pedido — volumen recibido"),
    ("CJS-04", "M-04", 0.70, "Calidad y documentación en primer entrega"),
    ("CJS-05", "M-01", 0.90, "Operación recurrente — entregas a tiempo"),
    ("CJS-05", "M-02", 0.85, "Cumplimiento de volumen en ciclo"),
    ("CJS-05", "M-06", 0.80, "Confianza en operación continua"),
    ("CJS-05", "M-05", 0.55, "Crédito en ciclo recurrente"),
    ("CJS-06", "M-01", 0.70, "Incidencia afecta percepción de puntualidad"),
    ("CJS-06", "M-02", 0.65, "Incidencia de volumen/calidad"),
    ("CJS-06", "M-04", 0.75, "Riesgo regulatorio ante falla"),
    ("CJS-06", "M-06", 0.85, "Respuesta a incidencia y retención"),
    ("CJS-07", "M-03", 0.70, "Revisión de precios"),
    ("CJS-07", "M-05", 0.75, "Revisión de crédito"),
    ("CJS-07", "M-06", 0.80, "Satisfacción en revisión"),
    ("CJS-07", "M-02", 0.60, "Volúmenes en revisión"),
    ("CJS-08", "M-06", 0.95, "Renovación — retención"),
    ("CJS-08", "M-03", 0.65, "Renegociación de condiciones"),
    ("CJS-08", "M-05", 0.50, "Crédito en renovación"),
]

EVENT_TYPES_V1: dict[str, str] = {
    "EV-01": "demand",
    "EV-02": "demand",
    "EV-03": "demand",
    "EV-04": "value_realization",
    "EV-05": "value_realization",
    "EV-06": "value_realization",
    "EV-07": "value_realization",
    "EV-08": "demand",
}

EVENT_TYPE_MAP = {
    "demanda": "demand",
    "entrega de valor": "value_realization",
}

B_ZERO_REASONS = {
    "A-08": "Actividad de respaldo; clientes no la perciben directamente",
    "A-14": "Mecanismo interno de tesorería invisible al cliente",
    "A-20": "Infraestructura regulatoria; clientes no la mencionan",
    "A-27": "Habilitador silencioso; sólo visible cuando falla",
    "A-38": "Infraestructura de riesgo invisible hasta el incidente",
    "A-41": "Decisión interna estratégica sin contacto con cliente",
    "A-42": "Exploración futura sin impacto operativo actual",
}

VALUE_STREAMS_V2: list[tuple[str, str, list[str], str]] = [
    ("VS-01", "EV-D01", ["A-31", "A-15", "A-22", "A-23", "A-24", "A-25", "A-26"], "EV-V04"),
    ("VS-02", "EV-D01", ["A-31", "A-15", "A-22", "A-23", "A-24", "A-25", "A-26", "A-32", "A-13"], "EV-V06"),
    ("VS-03", "EV-D02", ["A-28", "A-29", "A-12", "A-30"], "EV-V01"),
    ("VS-04", "EV-D03", ["A-03", "A-06", "A-07"], "EV-V02"),
    ("VS-05", "EV-D04", ["A-16", "A-17", "A-18", "A-21"], "EV-V08"),
    ("VS-06", "EV-D05", ["A-33", "A-34"], "EV-V07"),
    ("VS-07", "EV-D06", ["A-40", "A-41", "A-43", "A-22"], "EV-V04"),
]


@dataclass(frozen=True)
class VersionConfig:
    version: str
    scenario_id: str
    inventory_path: Path
    out_dir: Path
    title: str
    graph_title: str
    description: str
    copy_fn: str


VERSIONS: dict[str, VersionConfig] = {
    "v1": VersionConfig(
        version="v1",
        scenario_id="energoil_mexico",
        inventory_path=REPO_ROOT / "data/raw/Energoil_Mexico_Graph_Inventory.md",
        out_dir=REPO_ROOT / "data/processed/demo/energoil_mexico",
        title="Energoil México",
        graph_title="Energoil México — distribución de combustibles",
        description="Demo: grafo operativo + métricas de valor cliente (datos simulados)",
        copy_fn="v1",
    ),
    "v2": VersionConfig(
        version="v2",
        scenario_id="energoil_mexico_v2",
        inventory_path=REPO_ROOT / "data/raw/Energoil_Mexico_Graph_Inventory_v2.md",
        out_dir=REPO_ROOT / "data/processed/demo/energoil_mexico_v2",
        title="Energoil México v2",
        graph_title="Energoil México v2 — Porter areas & value streams",
        description="Demo v2: áreas Porter, eventos Demanda/Entrega de Valor, PRECEDES cross-proceso",
        copy_fn="v2",
    ),
}


def parse_table_rows(section_text: str) -> list[list[str]]:
    rows: list[list[str]] = []
    skip_headers = {
        "ID",
        "Actividad",
        "Origen",
        "Proceso",
        "Value Stream",
        "Equipo",
        "Actividades",
    }
    for line in section_text.splitlines():
        line = line.strip()
        if not line.startswith("|") or line.startswith("|----") or "---|" in line:
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if cells and cells[0] in skip_headers:
            continue
        rows.append(cells)
    return rows


def section(md: str, header_prefix: str) -> str:
    pattern = re.compile(rf"^## {re.escape(header_prefix)}", re.MULTILINE)
    m = pattern.search(md)
    if not m:
        return ""
    start = m.end()
    nxt = re.search(r"^## ", md[start:], re.MULTILINE)
    return md[start : start + nxt.start()] if nxt else md[start:]


def subsection(md: str, header: str) -> str:
    pattern = re.compile(rf"^### {re.escape(header)}\s*$", re.MULTILINE)
    m = pattern.search(md)
    if not m:
        return ""
    start = m.end()
    nxt = re.search(r"^### |^## ", md[start:], re.MULTILINE)
    return md[start : start + nxt.start()] if nxt else md[start:]


def causal_confidence(strength_cell: str) -> tuple[float, str]:
    text = strength_cell.strip()
    low = text.lower()
    if low.startswith("crítica"):
        return 1.0, text
    if low.startswith("alta"):
        return 0.85, text
    if low.startswith("media"):
        return 0.5, text
    return 0.5, text


def activity_num(aid: str) -> int:
    return int(aid.split("-")[1])


def expand_activity_spec(spec: str) -> list[str]:
    ids: list[str] = []
    for part in re.split(r",\s*", spec.strip()):
        part = part.strip()
        if not part:
            continue
        range_match = re.match(r"A-(\d+)\s+a\s+A-(\d+)", part)
        if range_match:
            start, end = int(range_match.group(1)), int(range_match.group(2))
            ids.extend(f"A-{i:02d}" for i in range(start, end + 1))
            continue
        id_match = re.match(r"(A-\d+)", part)
        if id_match:
            ids.append(id_match.group(1))
    return ids


def parse_cap_ids(cell: str) -> list[str]:
    return re.findall(r"CAP-\d+", cell)


def parse_system_ids(cell: str) -> list[str]:
    return re.findall(r"S-\d+", cell)


def parse_process_ids(cell: str) -> list[str]:
    if not cell or cell.strip().startswith("—"):
        return []
    return re.findall(r"P-\d+", cell)


def parse_team_id(cell: str) -> str:
    match = re.match(r"(T-\d+)", cell.strip())
    return match.group(1) if match else cell.strip()


def parse_porter_areas(cell: str) -> list[str]:
    return [area.strip() for area in cell.split(",") if area.strip()]


def team_id_for_porter_area(area: str) -> str:
    return PORTER_TEAM_BY_LABEL.get(area, "T-01")


def _capability_for_activity_v1(aid: str) -> list[str]:
    n = activity_num(aid)
    for r, cap in CAPABILITY_RANGES_V1:
        if n in r:
            return [cap]
    return []


def _add_uses_system_v1(add_rel_fn) -> None:
    mapping = [
        (["A-01", "A-02", "A-03"], "S-05"),
        (["A-09", "A-07"], "S-05"),
        (["A-09", "A-07"], "S-02"),
        (["A-16", "A-19", "A-20", "A-21"], "S-01"),
        (["A-18"], "S-06"),
        (["A-19", "A-32"], "S-07"),
        (["A-22", "A-23", "A-24", "A-25"], "S-03"),
        (["A-31", "A-32"], "S-02"),
        (["A-12", "A-13", "A-14", "A-15"], "S-08"),
        (["A-32", "A-13"], "S-04"),
    ]
    seen: set[tuple[str, str]] = set()
    for acts, sys in mapping:
        for activity_id in acts:
            key = (activity_id, sys)
            if key not in seen:
                seen.add(key)
                add_rel_fn(activity_id, sys, "USES_SYSTEM")


def _add_supports_v2(md: str, add_rel_fn) -> None:
    supports_sec = subsection(
        section(md, "2.6 Relaciones adicionales de ontología"),
        "Activity —[SUPPORTS]→ Capability",
    )
    seen: set[tuple[str, str]] = set()
    for row in parse_table_rows(supports_sec):
        if len(row) < 2:
            continue
        activity_spec, cap_cell = row[0], row[1]
        for activity_id in expand_activity_spec(activity_spec):
            for cap_id in parse_cap_ids(cap_cell):
                key = (activity_id, cap_id)
                if key not in seen:
                    seen.add(key)
                    add_rel_fn(activity_id, cap_id, "SUPPORTS")


def _add_uses_system_v2(md: str, add_rel_fn) -> None:
    uses_sec = subsection(
        section(md, "2.6 Relaciones adicionales de ontología"),
        "Activity —[USES_SYSTEM]→ System",
    )
    seen: set[tuple[str, str]] = set()
    for row in parse_table_rows(uses_sec):
        if len(row) < 2:
            continue
        activity_spec, system_cell = row[0], row[1]
        for activity_id in expand_activity_spec(activity_spec):
            for system_id in parse_system_ids(system_cell):
                key = (activity_id, system_id)
                if key not in seen:
                    seen.add(key)
                    add_rel_fn(activity_id, system_id, "USES_SYSTEM")


def _add_owns_v2(md: str, add_rel_fn) -> None:
    owns_sec = subsection(
        section(md, "2.6 Relaciones adicionales de ontología"),
        "Team —[OWNS]→ Process / Capability",
    )
    for row in parse_table_rows(owns_sec):
        if len(row) < 3:
            continue
        team_id = parse_team_id(row[0])
        for process_id in parse_process_ids(row[1]):
            add_rel_fn(team_id, process_id, "OWNS")
        for cap_id in parse_cap_ids(row[2]):
            add_rel_fn(team_id, cap_id, "OWNS")


def _parse_event_type(raw: str, event_id: str, *, version: str) -> str | None:
    if version == "v1":
        if raw in ("demand", "value_realization"):
            return raw
        return EVENT_TYPES_V1.get(event_id)
    normalized = raw.strip().lower()
    return EVENT_TYPE_MAP.get(normalized)


def _supplement_precedes_from_value_streams(
    add_rel_fn,
    precedes: set[tuple[str, str]],
) -> None:
    """Add §2.7 path segments missing from parsed inventory PRECEDES."""
    for _vs_id, demand_event, activity_path, value_event in VALUE_STREAMS_V2:
        chain = [demand_event, *activity_path, value_event]
        for left, right in zip(chain, chain[1:]):
            if (left, right) not in precedes:
                add_rel_fn(left, right, "PRECEDES", synthetic=True)
                precedes.add((left, right))


def _validate_value_streams_v2(precedes: set[tuple[str, str]]) -> None:
    def has_edge(source: str, target: str) -> bool:
        return (source, target) in precedes

    for vs_id, demand_event, activity_path, value_event in VALUE_STREAMS_V2:
        if not has_edge(demand_event, activity_path[0]):
            raise ValueError(
                f"{vs_id}: missing PRECEDES {demand_event} → {activity_path[0]}"
            )
        for left, right in zip(activity_path, activity_path[1:]):
            if not has_edge(left, right):
                raise ValueError(f"{vs_id}: missing PRECEDES {left} → {right}")
        if not has_edge(activity_path[-1], value_event):
            raise ValueError(
                f"{vs_id}: missing PRECEDES {activity_path[-1]} → {value_event}"
            )


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


def build(cfg: VersionConfig) -> None:
    md = cfg.inventory_path.read_text(encoding="utf-8")
    nodes: list[dict] = []
    relationships: list[dict] = []
    metrics: list[dict] = []
    metric_drivers: list[dict] = []
    activities: dict[str, dict] = {}
    precedes_edges: set[tuple[str, str]] = set()

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
        **props: object,
    ) -> None:
        rel = {
            "source": source,
            "target": target,
            "type": rtype,
            "properties": {k: v for k, v in props.items() if v is not None},
        }
        if synthetic:
            rel["properties"]["synthetic"] = True
        relationships.append(rel)
        if rtype == "PRECEDES":
            precedes_edges.add((source, target))

    # --- Metrics ---
    for row in parse_table_rows(section(md, "1.1 Metric (6 nodos)")):
        mid, name, definition, client_need = row[0], row[1], row[2], row[3]
        metrics.append(
            {
                "id": mid,
                "name": name,
                "definition": definition,
                "client_need": client_need,
            }
        )
        add_node(mid, "Metric", name, definition=definition, client_need=client_need)

    metric_ids = {m["id"] for m in metrics}

    # --- Metric drivers ---
    driver_parent: dict[str, str] = {}
    for row in parse_table_rows(section(md, "1.2 MetricDriver (15 nodos)")):
        did, parent, name, desc = row[0], row[1], row[2], row[3]
        driver_parent[did] = parent
        metric_drivers.append(
            {"id": did, "parent_metric_id": parent, "name": name, "description": desc}
        )
        add_node(did, "MetricDriver", name, parent_metric_id=parent, description=desc)
        add_rel(parent, did, "HAS_DRIVER")

    # --- Customer journey ---
    for row in parse_table_rows(section(md, "1.3 CustomerJourneyStep (8 nodos)")):
        cid, name, experience = row[0], row[1], row[2]
        add_node(cid, "CustomerJourneyStep", name, experience=experience)

    for cjs, metric, strength, justification in SYNTHETIC_SIGNALS:
        add_rel(
            cjs,
            metric,
            "SIGNALS",
            synthetic=True,
            strength=round(strength, 4),
            justification=justification,
        )

    # --- Process ---
    for row in parse_table_rows(section(md, "1.4 Process — 8 Macroprocesos (8 nodos)")):
        pid, name, desc = row[0], row[1], row[2]
        add_node(pid, "Process", name, description=desc)

    # --- Activities ---
    activity_rows = parse_table_rows(section(md, "1.5 Activity (43 nodos)"))
    for row in activity_rows:
        aid, process_id, name, area_cell, frequency = (
            row[0],
            row[1],
            row[2],
            row[3],
            row[4],
        )
        if cfg.version == "v2":
            porter_areas = parse_porter_areas(area_cell)
            primary_area = porter_areas[0] if porter_areas else area_cell
            team_id = team_id_for_porter_area(primary_area)
            area_text = ", ".join(area.lower() for area in porter_areas)
            activities[aid] = {
                "id": aid,
                "name": name,
                "process_id": process_id,
                "team_id": team_id,
                "frequency": frequency,
                "porter_areas": porter_areas,
            }
            add_node(
                aid,
                "Activity",
                name,
                process_id=process_id,
                porter_areas=porter_areas,
                area=area_text,
                team_id=team_id,
                team_label=primary_area,
                frequency=frequency,
            )
            add_rel(aid, process_id, "PART_OF")
            for area in porter_areas:
                add_rel(team_id_for_porter_area(area), aid, "PERFORMS")
        else:
            team_label = area_cell
            team_id = TEAM_BY_LABEL_V1.get(team_label, "T-07")
            activities[aid] = {
                "id": aid,
                "name": name,
                "process_id": process_id,
                "team_id": team_id,
                "frequency": frequency,
            }
            add_node(
                aid,
                "Activity",
                name,
                process_id=process_id,
                team_label=team_label,
                frequency=frequency,
            )
            add_rel(aid, process_id, "PART_OF")
            add_rel(team_id, aid, "PERFORMS")
            for cap_id in _capability_for_activity_v1(aid):
                add_rel(aid, cap_id, "SUPPORTS")

    # --- Team, Capability, System, Event ---
    team_header = "1.6 Team (9 nodos" if cfg.version == "v2" else "1.6 Team (8 nodos"
    cap_header = "1.7 Capability (9 nodos" if cfg.version == "v2" else "1.7 Capability (8 nodos"
    event_header = "1.9 Event (14 nodos" if cfg.version == "v2" else "1.9 Event (8 nodos"

    for row in parse_table_rows(section(md, team_header)):
        add_node(row[0], "Team", row[1], role=row[2])
    for row in parse_table_rows(section(md, cap_header)):
        add_node(row[0], "Capability", row[1], description=row[2])
    for row in parse_table_rows(section(md, "1.8 System (8 nodos)")):
        add_node(row[0], "System", row[1], function=row[2])
    for row in parse_table_rows(section(md, event_header)):
        eid, name = row[0], row[1]
        if cfg.version == "v2":
            event_type_raw, description = row[2], row[3]
            event_type = _parse_event_type(event_type_raw, eid, version=cfg.version)
        elif len(row) >= 4:
            event_type = _parse_event_type(row[2], eid, version=cfg.version)
            description = row[3]
        else:
            event_type = EVENT_TYPES_V1.get(eid)
            description = row[2]
        add_node(
            eid,
            "Event",
            name,
            description=description,
            event_type=event_type,
        )

    # Team OWNS process/capability
    if cfg.version == "v2":
        _add_owns_v2(md, add_rel)
    else:
        owns = parse_table_rows(
            section(md, "2.5 Relaciones adicionales de ontología")
            .split("### Team —[OWNS]→ Process / Capability")[1]
            .split("###")[0]
        )
        for row in owns:
            if len(row) >= 3:
                add_rel(row[0], row[1], "OWNS")
                add_rel(row[0], row[2], "OWNS")

    # AFFECTS Activity -> Metric
    affects_header = (
        "2.1 Activity —[AFFECTS]→ Metric (25 relaciones)"
        if cfg.version == "v2"
        else "2.1 Activity —[AFFECTS]→ Metric (23 relaciones)"
    )
    affects_conf: dict[tuple[str, str], float] = {}
    for row in parse_table_rows(section(md, affects_header)):
        aid, mid, strength_cell = row[0], row[1], row[2]
        conf, justification = causal_confidence(strength_cell)
        affects_conf[(aid, mid)] = conf
        add_rel(
            aid,
            mid,
            "AFFECTS",
            confidence=conf,
            justification=justification,
        )
        for did, parent in driver_parent.items():
            if parent == mid:
                add_rel(
                    aid,
                    did,
                    "AFFECTS",
                    confidence=0.5,
                    synthetic=True,
                    justification=f"Inferido: actividad afecta métrica {mid}",
                )

    # Process CONTRIBUTES_TO Metric
    process_metric: set[tuple[str, str]] = set()
    for row in parse_table_rows(
        section(md, "2.2 Process —[CONTRIBUTES_TO]→ Metric (16 relaciones)")
    ):
        process_metric.add((row[0], row[1]))
        add_rel(row[0], row[1], "CONTRIBUTES_TO", confidence=0.85)

    # TOUCHES
    touches: set[tuple[str, str]] = set()
    for row in parse_table_rows(
        section(md, "2.3 Activity —[TOUCHES]→ CustomerJourneyStep (11 relaciones)")
    ):
        touches.add((row[0], row[1]))
        add_rel(row[0], row[1], "TOUCHES")

    # PRECEDES (intra- and cross-process tables)
    precedes_sec = section(md, "2.4 Activity —[PRECEDES]→ Activity")
    for row in parse_table_rows(precedes_sec):
        if len(row) >= 2 and row[0].startswith("A-") and row[1].startswith("A-"):
            add_rel(row[0], row[1], "PRECEDES")

    # USES_SYSTEM / SUPPORTS (v2)
    if cfg.version == "v2":
        _add_supports_v2(md, add_rel)
        _add_uses_system_v2(md, add_rel)
    else:
        _add_uses_system_v1(add_rel)

    # INVOLVES_EVENT
    if cfg.version == "v2":
        inv_sec = section(md, "2.5 Activity —[INVOLVES_EVENT]→ Event")
        for row in parse_table_rows(inv_sec):
            if len(row) < 3:
                continue
            activity_id, event_id, event_role = row[0], row[1], row[2]
            add_rel(activity_id, event_id, "INVOLVES_EVENT", event_role=event_role)
            if event_role == "responde_a":
                add_rel(event_id, activity_id, "PRECEDES", synthetic=True)
            elif event_role == "produce":
                add_rel(activity_id, event_id, "PRECEDES", synthetic=True)
    else:
        inv = (
            section(md, "2.5 Relaciones adicionales de ontología")
            .split("### Activity —[INVOLVES_EVENT]→ Event")[1]
            .split("###")[0]
        )
        for row in parse_table_rows(inv):
            if len(row) >= 2:
                add_rel(row[0], row[1].split()[0], "INVOLVES_EVENT")

    if cfg.version == "v2":
        _supplement_precedes_from_value_streams(add_rel, precedes_edges)
        _validate_value_streams_v2(precedes_edges)

    # Activity quantification §3.6
    quant_sec = section(md, "3.6 Tabla de cuantificación por actividad")
    for row in parse_table_rows(quant_sec):
        if not row or not row[0].startswith("A-"):
            continue
        aid = row[0]
        p, c, f, r, v = (
            float(row[1]),
            float(row[2]),
            float(row[3]),
            float(row[4]),
            float(row[5]),
        )
        metrics_with_b = [m.strip() for m in row[6].split(",") if m.strip() and m.strip() != "—"]
        activities[aid].update(
            {
                "p": p,
                "c": c,
                "f": f,
                "r": r,
                "v": round(v, 4),
                "metrics_with_b_hint": metrics_with_b,
            }
        )
        for node in nodes:
            if node["id"] == aid:
                node["properties"].update({"p": p, "c": c, "f": f, "r": r, "v": round(v, 4)})

    # Build indexes for bridge scoring
    signals: dict[tuple[str, str], float] = {}
    for cjs, metric, strength, _ in SYNTHETIC_SIGNALS:
        signals[(cjs, metric)] = strength

    activity_ids = sorted(activities.keys(), key=activity_num)
    scores_by_activity: list[dict] = []
    matrix: list[dict] = []

    for aid in activity_ids:
        act = activities[aid]
        v = act["v"]
        row_scores = []
        for mid in sorted(metric_ids):
            g = _g_score(aid, mid, affects_conf, activities, process_metric)
            j = _j_score(aid, mid, touches, signals)
            dv = _dv_score(aid, mid, affects_conf, driver_parent)
            b = round(BRIDGE_W[0] * g + BRIDGE_W[1] * j + BRIDGE_W[2] * dv, 4)
            rel = round(b * v, 4)
            if aid in B_ZERO_REASONS:
                continue
            if b > 0 or rel > 0:
                row_scores.append(
                    {
                        "metric_id": mid,
                        "g": round(g, 4),
                        "j": round(j, 4),
                        "dv": round(dv, 4),
                        "b": b,
                        "relevance": rel,
                    }
                )
                matrix.append(
                    {
                        "activity_id": aid,
                        "activity_name": act["name"],
                        "metric_id": mid,
                        "relevance": rel,
                        "b": b,
                        "v": v,
                    }
                )

        strategic_b_zero = aid in B_ZERO_REASONS
        if strategic_b_zero:
            row_scores = []
        else:
            row_scores = [s for s in row_scores if s["b"] > 0]

        scores_by_activity.append(
            {
                "activity_id": aid,
                "activity_name": act["name"],
                "process_id": act["process_id"],
                "team_id": act["team_id"],
                "p": act["p"],
                "c": act["c"],
                "f": act["f"],
                "r": act["r"],
                "v": v,
                "scores": row_scores,
                "b_zero_all_metrics": strategic_b_zero or (len(row_scores) == 0),
                "b_zero_reason": B_ZERO_REASONS.get(aid),
                "strategic_b_zero": strategic_b_zero,
            }
        )

    by_metric: dict[str, float] = defaultdict(float)
    for cell in matrix:
        by_metric[cell["metric_id"]] += cell["relevance"]
    for cell in matrix:
        total = by_metric[cell["metric_id"]]
        cell["pct_contribution"] = round(cell["relevance"] / total, 4) if total > 0 else 0.0
    for act_row in scores_by_activity:
        for score in act_row["scores"]:
            total = by_metric[score["metric_id"]]
            score["pct_contribution"] = (
                round(score["relevance"] / total, 4) if total > 0 else 0.0
            )

    process_rollups: list[dict] = []
    for pid in sorted({a["process_id"] for a in activities.values()}):
        for mid in sorted(metric_ids):
            total_rel = sum(
                cell["relevance"]
                for cell in matrix
                if cell["metric_id"] == mid
                and activities[cell["activity_id"]]["process_id"] == pid
            )
            if total_rel > 0:
                process_rollups.append(
                    {
                        "process_id": pid,
                        "metric_id": mid,
                        "relevance_sum": round(total_rel, 4),
                    }
                )
    for pr in process_rollups:
        total = by_metric[pr["metric_id"]]
        pr["pct_contribution"] = round(pr["relevance_sum"] / total, 4) if total > 0 else 0.0

    cfg.out_dir.mkdir(parents=True, exist_ok=True)

    graph_meta = {
        "synthetic_signals": True,
        "synthetic_note": "CJS—[SIGNALS]→Metric strengths not in inventory; added for J(A,M) per bridge protocol.",
        "inferred_driver_affects": True,
        "node_count": len(nodes),
        "relationship_count": len(relationships),
    }
    if cfg.version == "v2":
        graph_meta["inventory_version"] = "v2"
        graph_meta["synthetic_event_precedes"] = True
        graph_meta["synthetic_event_precedes_note"] = (
            "Event↔Activity PRECEDES derived from INVOLVES_EVENT event_role for VS discovery."
        )

    graph_doc = {
        "scenario_id": cfg.scenario_id,
        "title": cfg.graph_title,
        "source": str(cfg.inventory_path.relative_to(REPO_ROOT)),
        "meta": graph_meta,
        "nodes": nodes,
        "relationships": relationships,
    }

    metrics_doc = {
        "scenario_id": cfg.scenario_id,
        "metrics": metrics,
        "metric_drivers": metric_drivers,
    }

    relevance_doc = {
        "scenario_id": cfg.scenario_id,
        "formulas": {
            "v": "0.3*P + 0.4*C + 0.2*F + 0.1*R",
            "b": "0.4*G + 0.4*J + 0.2*DV",
            "relevance": "B * V",
        },
        "activities": scores_by_activity,
        "matrix": matrix,
        "process_rollups": process_rollups,
        "rankings_by_metric": _rankings(matrix, metrics),
    }

    copy_md = _demo_copy_v2() if cfg.version == "v2" else _demo_copy_v1()

    (cfg.out_dir / "graph.json").write_text(
        json.dumps(graph_doc, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (cfg.out_dir / "metrics.json").write_text(
        json.dumps(metrics_doc, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (cfg.out_dir / "relevance.json").write_text(
        json.dumps(relevance_doc, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (cfg.out_dir / "copy.md").write_text(copy_md, encoding="utf-8")

    rel_prefix = f"data/processed/demo/{cfg.scenario_id}"
    upsert_manifest(
        {
            "id": cfg.scenario_id,
            "title": cfg.title,
            "description": cfg.description,
            "paths": {
                "graph": f"{rel_prefix}/graph.json",
                "metrics": f"{rel_prefix}/metrics.json",
                "relevance": f"{rel_prefix}/relevance.json",
                "copy": f"{rel_prefix}/copy.md",
            },
        }
    )

    print(f"Wrote {cfg.out_dir}/graph.json ({len(nodes)} nodes, {len(relationships)} rels)")
    print(f"Wrote {cfg.out_dir}/metrics.json ({len(metrics)} metrics)")
    print(f"Wrote {cfg.out_dir}/relevance.json ({len(matrix)} matrix cells)")
    print(f"Updated manifest entry: {cfg.scenario_id}")


def _g_score(
    aid: str,
    mid: str,
    affects_conf: dict[tuple[str, str], float],
    activities: dict[str, dict],
    process_metric: set[tuple[str, str]],
) -> float:
    g = 0.0
    if (aid, mid) in affects_conf:
        g = max(g, 1.0 * affects_conf[(aid, mid)])
    pid = activities[aid]["process_id"]
    if (pid, mid) in process_metric:
        g = max(g, 0.7 * 0.85)
    return g


def _j_score(
    aid: str,
    mid: str,
    touches: set[tuple[str, str]],
    signals: dict[tuple[str, str], float],
) -> float:
    best = 0.0
    for a, cjs in touches:
        if a != aid:
            continue
        s = signals.get((cjs, mid), 0.0)
        best = max(best, s)
    return best


def _dv_score(
    aid: str,
    mid: str,
    affects_conf: dict[tuple[str, str], float],
    driver_parent: dict[str, str],
) -> float:
    for (a, did), conf in list(affects_conf.items()):
        if a == aid and did.startswith("MD-") and driver_parent.get(did) == mid:
            return 1.0 * conf
    return 0.0


def _rankings(matrix: list[dict], metrics: list[dict]) -> dict[str, list[dict]]:
    by_m: dict[str, list[dict]] = defaultdict(list)
    for cell in matrix:
        by_m[cell["metric_id"]].append(cell)
    names = {m["id"]: m["name"] for m in metrics}
    out = {}
    for mid, rows in by_m.items():
        rows.sort(key=lambda x: x["relevance"], reverse=True)
        out[mid] = [
            {
                "rank": i + 1,
                "activity_id": r["activity_id"],
                "activity_name": r["activity_name"],
                "relevance": r["relevance"],
                "pct_contribution": r["pct_contribution"],
                "metric_name": names.get(mid, mid),
            }
            for i, r in enumerate(rows[:15])
        ]
    return out


def _demo_copy_v1() -> str:
    return """# Energoil México — demo Optimizer

## Para qué sirve esta herramienta

Optimizer conecta **operaciones internas** (actividades, procesos, equipos) con **métricas de valor percibido por el cliente**, para que dirección priorice inversión en personas, procesos, sistemas y cumplimiento con un ROI defendible.

## Cómo leer el grafo

- **Métricas (M-*)** — anclas de valor del cliente (entrega a tiempo, volumen, precio, compliance, crédito, retención).
- **Actividades (A-*)** — trabajo operativo donde se invierte tiempo y recursos.
- **Pasos de journey (CJS-*)** — momentos que el cliente vive y asocia con valor.

## Cómo leer la matriz de relevancia

Cada celda es **Relevancia = B × V**, donde **V** captura criticidad operativa (posición, causalidad, frecuencia, riesgo) y **B** la evidencia de puente hacia la métrica (grafo, journey, drivers).

Actividades con **V alto y B = 0** son hallazgos: críticas internamente pero sin trazabilidad a valor cliente — candidatas a conectar, automatizar o depriorizar.

## Datos

Escenario simulado para demo comercial. Fuente: inventario Energoil México v1 (junio 2026).
"""


def _demo_copy_v2() -> str:
    return """# Energoil México v2 — demo Optimizer

## Para qué sirve esta herramienta

Optimizer conecta **operaciones internas** (actividades, procesos, equipos) con **métricas de valor percibido por el cliente**, para que dirección priorice inversión en personas, procesos, sistemas y cumplimiento con un ROI defendible.

## Qué hay de nuevo en v2

- **Áreas Porter** — cada actividad está etiquetada con una o más áreas del modelo Porter (9 equipos).
- **Eventos Demanda / Entrega de Valor** — 14 eventos clasificados como disparadores de flujo o materialización de valor.
- **PRECEDES cross-proceso** — el grafo conecta áreas entre sí; los Value Streams atraviesan procesos completos.

## Cómo leer el grafo

- **Métricas (M-*)** — anclas de valor del cliente.
- **Actividades (A-*)** — trabajo operativo; propiedad `porter_areas` indica responsabilidad cross-área.
- **Eventos (EV-D* / EV-V*)** — demanda (inicio de flujo) vs entrega de valor (cierre).
- **Pasos de journey (CJS-*)** — momentos que el cliente vive y asocia con valor.

## Cómo leer la matriz de relevancia

Cada celda es **Relevancia = B × V**. Actividades con **V alto y B = 0** son habilitadores silenciosos — críticas internamente pero sin trazabilidad directa a valor cliente.

## Datos

Escenario simulado para demo comercial. Fuente: inventario Energoil México v2 (junio 2026).
"""


def main() -> None:
    parser = argparse.ArgumentParser(description="Build Energoil demo JSON fixtures.")
    parser.add_argument(
        "--version",
        choices=sorted(VERSIONS.keys()),
        default="v1",
        help="Inventory version to build (default: v1)",
    )
    args = parser.parse_args()
    build(VERSIONS[args.version])


if __name__ == "__main__":
    main()
