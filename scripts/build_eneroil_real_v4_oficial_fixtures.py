#!/usr/bin/env python3
"""Build Eneroil real-data v4 oficial (F2-reconciled) demo fixtures.

Source: data/raw/Eneroil_Inventario_Grafo_v4 (oficial).md — v3 fill protocol
plus Paso 9 F2 (retirar ACT-25/29/TEA-04; extraer ACT-32/33). Scenario kind
ai_enhanced.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from optimizer.graph_hygiene.sanitize_labels import split_label_evidence

REPO_ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = REPO_ROOT / "configs/demo_scenarios.json"
INVENTORY_PATH = REPO_ROOT / "data/raw/Eneroil_Inventario_Grafo_v4 (oficial).md"
OUT_DIR = REPO_ROOT / "data/processed/demo/eneroil_real_v4_oficial"

SCENARIO_ID = "eneroil_real_v4_oficial"
SCENARIO_TITLE = "Eneroil (datos reales) v4 — oficial"
SCENARIO_DESCRIPTION = (
    "Inventario oficial F2: v3 más reconciliación (retirar entrega externa "
    "ACT-25, TEA-04 y ACT-29; extraer ACT-32/33; facturación tras recepción "
    "del BOL). Métricas abducidas; P/C/F/R de actividades generadas."
)
GRAPH_TITLE = "Eneroil S.A. de C.V. — extracción real v4 (oficial)"

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


def owner_team_ids(owner_label: str) -> tuple[str, ...]:
    if owner_label.startswith("∅") or "pendiente" in owner_label.lower():
        return ()
    team_ids = TEAM_IDS_BY_OWNER_LABEL.get(owner_label)
    if team_ids is None:
        raise ValueError(f"unmapped owner label {owner_label!r}")
    return team_ids

PRECEDES_MAIN_CHAIN = [
    "ACT-01", "ACT-03", "ACT-04", "ACT-05", "ACT-06", "ACT-07", "ACT-08",
    "ACT-09", "ACT-10", "ACT-11", "ACT-12", "ACT-13", "ACT-14",
]
PRECEDES_GENERATED = [
    ("ACT-06", "ACT-24"),
    ("ACT-24", "ACT-08"),
]
PRECEDES_EXTRA = [
    ("ACT-02", "ACT-03"),
    ("ACT-12", "ACT-15"),
    ("ACT-15", "ACT-16"),
    ("ACT-16", "ACT-17"),
]
# Paso 7 input edges (ACT-02→ACT-03 already in PRECEDES_EXTRA as extracted).
PRECEDES_FEEDERS = [
    ("ACT-22", "ACT-06", "evidence", 0.75),
    ("ACT-06", "ACT-09", "logical", 0.5),
    ("ACT-09", "ACT-13", "evidence", 1.0),
    ("ACT-10", "ACT-13", "evidence", 1.0),
    ("ACT-14", "ACT-16", "logical", 0.75),
    ("ACT-11", "ACT-18", "evidence", 0.75),
    ("ACT-06", "ACT-18", "evidence", 0.75),
    ("ACT-08", "ACT-18", "evidence", 0.75),
    ("ACT-18", "ACT-20", "logical", 0.5),
    ("ACT-18", "ACT-23", "logical", 0.5),
    ("ACT-26", "ACT-03", "logical", 0.5),
    ("ACT-27", "ACT-13", "logical", 0.5),
    ("ACT-28", "ACT-05", "logical", 0.5),
    ("ACT-30", "ACT-24", "logical", 0.5),
    ("ACT-31", "ACT-15", "logical", 0.5),
    ("ACT-24", "ACT-32", "evidence", 0.75),
    ("ACT-32", "ACT-07", "evidence", 0.75),
    ("ACT-08", "ACT-33", "evidence", 0.75),
    ("ACT-33", "ACT-10", "evidence", 0.75),
]

USES_SYSTEM_EXTRACTED = [
    ("ACT-01", "SYS-03"),
    ("ACT-01", "SYS-04"),
    ("ACT-09", "SYS-01"),
    ("ACT-10", "SYS-02"),
    ("ACT-11", "SYS-04"),
    ("ACT-13", "SYS-01"),
    ("ACT-13", "SYS-05"),
    ("ACT-14", "SYS-01"),
]
USES_SYSTEM_GENERATED = [
    ("ACT-16", "SYS-01", 0.75, "logical"),
    ("ACT-16", "SYS-04", 0.75, "logical"),
]

INVOLVES_EVENT = [
    ("ACT-01", "EVT-01", "responde_a"),
    ("ACT-03", "EVT-02", "produce"),
    ("ACT-04", "EVT-03", "produce"),
    ("ACT-06", "EVT-04", "produce"),
    ("ACT-08", "EVT-05", "produce"),
    ("ACT-10", "EVT-06", "produce"),
    ("ACT-14", "EVT-07", "produce"),
    ("ACT-15", "EVT-08", "responde_a"),
    ("ACT-33", "EVT-09", "produce", 0.75, "evidence"),
    ("ACT-13", "EVT-10", "produce", 0.75, "evidence"),
]

EVENT_TYPES = {
    "EVT-01": "demand",
    "EVT-02": "milestone",
    "EVT-03": "milestone",
    "EVT-04": "milestone",
    "EVT-05": "milestone",
    "EVT-06": "milestone",
    "EVT-07": "milestone",
    "EVT-08": "exception",
    "EVT-09": "value_realization",
    "EVT-10": "value_realization",
}

SUPPORTS_GENERATED = [
    (("ACT-01", "ACT-03", "ACT-04"), "CAP-02", 1.0, "evidence"),
    (("ACT-02",), "CAP-01", 1.0, "evidence"),
    (("ACT-05", "ACT-07"), "CAP-03", 1.0, "evidence"),
    (("ACT-06", "ACT-22"), "CAP-04", 1.0, "evidence"),
    (("ACT-08",), "CAP-04", 0.5, "evidence"),
    (("ACT-09",), "CAP-07", 0.75, "evidence"),
    (("ACT-10", "ACT-11"), "CAP-05", 1.0, "evidence"),
    (("ACT-12", "ACT-13", "ACT-14", "ACT-15", "ACT-16", "ACT-17"), "CAP-06", 1.0, "evidence"),
    (("ACT-18", "ACT-23"), "CAP-07", 1.0, "evidence"),
    (("ACT-19", "ACT-20", "ACT-21"), "CAP-08", 1.0, "evidence"),
]

OWNS_PROCESS = [
    ("TEA-02", "PRO-01", 1.0),
    ("TEA-03", "PRO-02", 1.0),
    ("TEA-05", "PRO-04", 0.75),
    ("TEA-06", "PRO-05", 1.0),
    ("TEA-08", "PRO-06", 1.0),
    ("TEA-07", "PRO-07", 1.0),
    ("TEA-07", "PRO-08", 1.0),
    ("TEA-07", "PRO-09", 1.0),
]

OWNS_CAPABILITY = [
    ("TEA-02", "CAP-01"), ("TEA-03", "CAP-02"),
    ("TEA-05", "CAP-04"), ("TEA-06", "CAP-05"), ("TEA-08", "CAP-06"),
    ("TEA-07", "CAP-07"), ("TEA-07", "CAP-08"),
]

METRICS = [
    {
        "id": "MET-01",
        "name": "Confiabilidad de entrega (producto / volumen / destino / fecha)",
        "definition": "Producto correcto, volumen, destino y fecha según lo pactado.",
        "client_need": "Recibir lo acordado en destino y fecha.",
        "confidence": 0.5,
        "generated": True,
        "generation_basis": "abduction",
        "informant_distance": 3,
    },
    {
        "id": "MET-02",
        "name": "CFDI correcto y a tiempo",
        "definition": "CFDI correcto y oportuno para contabilidad/IVA del cliente.",
        "client_need": "Facturación percibida exacta y puntual.",
        "confidence": 0.5,
        "generated": True,
        "generation_basis": "abduction",
        "informant_distance": 3,
    },
    {
        "id": "MET-03",
        "name": "Transparencia / exactitud del estado de cuenta",
        "definition": "Estado de cuenta correcto y puntual, sin disputas.",
        "client_need": "Claridad de cuenta y saldos.",
        "confidence": 0.5,
        "generated": True,
        "generation_basis": "abduction",
        "informant_distance": 3,
    },
]

DRIVES = [
    ("MDR-01", "MET-02"),
    ("MDR-02", "MET-02"),
    ("MDR-06", "MET-02"),
    ("MDR-06", "MET-03"),
]

AFFECTS_DRIVER = [
    ("ACT-10", "MDR-01", 0.75),
    ("ACT-13", "MDR-05", 0.75),
    ("ACT-12", "MDR-03", 0.75),
]

AFFECTS_METRIC = [
    ("ACT-05", "MET-01", 0.5),
    ("ACT-16", "MET-03", 0.5),
]

CONTRIBUTES = [
    ("PRO-05", "MET-02", 0.5),
    ("PRO-06", "MET-03", 0.5),
    ("PRO-03", "MET-01", 0.5),
]

TOUCHES = [
    ("ACT-01", "CJS-01"),
    ("ACT-03", "CJS-02"),
    ("ACT-04", "CJS-03"),
    ("ACT-11", "CJS-05"),
    ("ACT-16", "CJS-06"),
    ("ACT-19", "CJS-08"),
]

# Paso 6 + Paso 8. Optional trailing: score_flag, crf_basis (C/R/F provenance).
SCORED_ACTIVITIES = [
    ("ACT-01", 0.25, 0.75, 0.25, 0.5, 0.25, 0.5, 1.0, 0.5),
    ("ACT-03", 0.25, 0.75, 0.5, 0.5, 0.5, 0.5, 1.0, 0.5),
    ("ACT-05", 0.5, 0.75, 0.5, 0.5, 0.5, 0.5, None, None),
    ("ACT-10", 0.75, 0.75, 1.0, 0.75, 1.0, 0.75, 1.0, 0.5),
    ("ACT-11", 0.75, 0.5, 0.75, 0.5, 0.5, 0.5, 1.0, 0.5),
    ("ACT-12", 0.75, 0.5, 0.75, 0.75, 0.75, 0.75, None, None),
    ("ACT-13", 1.0, 0.75, 0.75, 0.75, 0.75, 0.75, None, None),
    ("ACT-15", 0.75, 0.5, 0.5, 0.5, 0.5, 0.5, None, None),
    ("ACT-16", 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, None, None),
    ("ACT-17", 1.0, 0.5, 0.5, 0.5, 0.75, 0.5, None, None),
    ("ACT-24", 0.5, 0.75, 0.75, 0.75, 0.75, 0.75, 1.0, 0.5),
    ("ACT-26", 0.25, 0.5, 0.5, 0.5, 0.5, 0.5, 1.0, 0.5, "void_on_collapse", "simulated"),
    ("ACT-27", 0.75, 0.5, 0.75, 0.5, 0.75, 0.5, 1.0, 0.5, "void_on_collapse", "simulated"),
    ("ACT-28", 0.5, 0.75, 0.5, 0.5, 0.75, 0.5, 1.0, 0.5),
    ("ACT-30", 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.75, 0.5, "tier_bajo", "simulated"),
    ("ACT-31", 0.75, 0.5, 0.75, 0.5, 0.75, 0.5, 0.75, 0.5, "void_on_collapse", "simulated"),
    ("ACT-32", 0.5, 0.75, 0.5, 0.5, 0.5, 0.5, None, None),
    ("ACT-33", 0.75, 0.75, 0.5, 0.5, 0.5, 0.5, None, None),
]

# Paso 7 — feeders (no PERFORMS / PART_OF where inventory leaves them empty).
FEEDER_ACTIVITIES = [
    {
        "id": "ACT-26",
        "name": "Determinación del costo de transporte para la cotización",
        "confidence": 0.5,
        "evidence_pointer": (
            'cotización entrega precio a un "destino" (P3) ⇒ componente de flete previo'
        ),
        "fill_flag": "contested_external",
        "team_id": None,
        "process_id": None,
    },
    {
        "id": "ACT-27",
        "name": "Obtención del estado de cuenta bancario",
        "confidence": 0.5,
        "evidence_pointer": (
            '"conciliar contra el estado de cuenta bancario" (P3) ⇒ obtenerlo primero'
        ),
        "fill_flag": "contested_external",
        "team_id": "TEA-08",
        "team_confidence": 0.5,
        "process_id": "PRO-06",
        "process_confidence": 0.75,
    },
    {
        "id": "ACT-28",
        "name": "Consulta informal de disponibilidad a la empresa de logística",
        "confidence": 0.75,
        "evidence_pointer": (
            'F2: "de hecho, sí, pero... no hay 1 [proceso] en específico... '
            'el feeling en la operación es muy rápida y directa"'
        ),
        "fill_flag": "informal_no_documentado",
        "team_id": None,
        "process_id": "PRO-03",
        "process_confidence": 0.75,
    },
    {
        "id": "ACT-30",
        "name": "Autorización de liberación de fondos para prepago",
        "confidence": 0.5,
        "evidence_pointer": (
            '"OC con prepago" (P3) vía ACT-24 ⇒ fondos liberados'
        ),
        "fill_flag": "tier_bajo",
        "team_id": "TEA-01",
        "team_confidence": 0.5,
        "process_id": None,
    },
    {
        "id": "ACT-31",
        "name": "Identificación de facturas vencidas",
        "confidence": 0.5,
        "evidence_pointer": (
            '"contacto por vencida" (ACT-15) exige saber que venció'
        ),
        "fill_flag": "contested_external",
        "team_id": "TEA-08",
        "team_confidence": 0.5,
        "process_id": "PRO-06",
        "process_confidence": 0.75,
    },
]


F2_EXTRACTED_ACTIVITIES = [
    {
        "id": "ACT-32",
        "name": "Monitoreo del estado de liberación de crédito",
        "confidence": 0.75,
        "evidence_pointer": 'F2: "yo aquí veo si me liberaron, si no me liberaron"',
    },
    {
        "id": "ACT-33",
        "name": "Recepción del BOL de la empresa de logística",
        "confidence": 0.75,
        "evidence_pointer": (
            'F2: "manda el BOL, la orden de compra, la información..."'
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


def clean_node_label(raw: str) -> tuple[str, str | None]:
    """Display name without inventory evidence notes; note → evidence_pointer."""
    return split_label_evidence(strip_markdown(raw))


def expand_activity_spec(spec: str) -> list[str]:
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
    activity_meta: dict[str, dict] = {}

    def add_node(
        nid: str,
        ntype: str,
        label: str,
        *,
        generated: bool = False,
        evidence_pointer: str | None = None,
        **props: object,
    ) -> None:
        clean, note = clean_node_label(label)
        label = clean
        if note:
            evidence_pointer = (
                f"{evidence_pointer}; {note}" if evidence_pointer else note
            )
        if evidence_pointer is not None:
            props = {**props, "evidence_pointer": evidence_pointer}
        properties = {"generated": generated, **{k: v for k, v in props.items() if v is not None}}
        if not generated and "generated" in properties:
            properties["generated"] = False
        nodes.append({"id": nid, "type": ntype, "label": label, "properties": properties})

    def add_rel(
        source: str,
        target: str,
        rtype: str,
        *,
        generated: bool = False,
        synthetic: bool = False,
        **props: object,
    ) -> None:
        properties = {k: v for k, v in props.items() if v is not None}
        properties["generated"] = generated
        if synthetic:
            properties["synthetic"] = True
        relationships.append(
            {"source": source, "target": target, "type": rtype, "properties": properties}
        )

    process_by_activity: dict[str, str] = {}
    for row in parse_table_rows(section(md, "Process"), r"PRO-\d+"):
        pid, name, activities_cell = row[0], strip_markdown(row[1]), row[2]
        if not name or "sin nombrar" in name.lower():
            continue
        add_node(pid, "Process", name, generated=False)
        for aid in expand_activity_spec(activities_cell):
            process_by_activity[aid] = pid
            add_rel(aid, pid, "PART_OF", generated=False)

    for row in parse_table_rows(section(md, "Activity"), r"ACT-\d+"):
        aid, name, owner_label = row[0], row[1], strip_markdown(row[2])
        team_ids = owner_team_ids(owner_label)
        clean_name, _ = clean_node_label(name)
        activity_meta[aid] = {
            "name": clean_name,
            "process_id": process_by_activity.get(aid, ""),
            "owner": owner_label,
        }
        add_node(
            aid,
            "Activity",
            name,
            generated=False,
            process_id=process_by_activity.get(aid),
            team_label=owner_label,
            external_owner=True if "externo" in owner_label.lower() else None,
        )
        for team_id in team_ids:
            add_rel(team_id, aid, "PERFORMS", generated=False)

    add_node(
        "ACT-24",
        "Activity",
        "Ejecución del prepago al proveedor",
        generated=True,
        generation_basis="logical",
        confidence=0.75,
        corroboration=2,
        informant_distance=1,
    )
    activity_meta["ACT-24"] = {
        "name": "Ejecución del prepago al proveedor",
        "process_id": "",
        "owner": "",
    }
    for extracted in F2_EXTRACTED_ACTIVITIES:
        aid = extracted["id"]
        add_node(
            aid,
            "Activity",
            extracted["name"],
            generated=False,
            generation_basis="evidence",
            confidence=extracted["confidence"],
            informant_distance=1,
            evidence_pointer=extracted["evidence_pointer"],
        )
        activity_meta[aid] = {
            "name": extracted["name"],
            "process_id": "",
            "owner": "",
        }

    for feeder in FEEDER_ACTIVITIES:
        aid = feeder["id"]
        process_id = feeder.get("process_id")
        add_node(
            aid,
            "Activity",
            feeder["name"],
            generated=True,
            generation_basis="logical",
            confidence=feeder["confidence"],
            corroboration=2,
            informant_distance=1,
            evidence_pointer=feeder["evidence_pointer"],
            fill_flag=feeder["fill_flag"],
            process_id=process_id,
        )
        activity_meta[aid] = {
            "name": feeder["name"],
            "process_id": process_id or "",
            "owner": "",
        }
        team_id = feeder.get("team_id")
        if team_id:
            add_rel(
                team_id,
                aid,
                "PERFORMS",
                generated=True,
                confidence=feeder.get("team_confidence", 0.5),
                generation_basis="logical",
                informant_distance=1,
            )
        if process_id:
            add_rel(
                aid,
                process_id,
                "PART_OF",
                generated=True,
                confidence=feeder.get("process_confidence", 0.75),
                generation_basis="logical",
                informant_distance=1,
            )

    for row in parse_table_rows(section(md, "Team"), r"TEA-\d+"):
        raw_label = row[1]
        if "retirado" in raw_label.lower():
            continue
        add_node(row[0], "Team", strip_markdown(raw_label.split("*(")[0]), generated=False)
    for row in parse_table_rows(section(md, "Capability"), r"CAP-\d+"):
        add_node(row[0], "Capability", row[1], generated=False)
    for row in parse_table_rows(section(md, "System"), r"SYS-\d+"):
        add_node(row[0], "System", row[1], generated=False, function=row[2])

    for row in parse_table_rows(section(md, "Event"), r"EVT-\d+"):
        eid, name, role = row[0], row[1], strip_markdown(row[2])
        add_node(eid, "Event", name, generated=False, description=role, event_type=EVENT_TYPES[eid])

    add_node(
        "EVT-09",
        "Event",
        "Entrega confirmada en destino",
        generated=True,
        generation_basis="evidence",
        confidence=0.75,
        corroboration=2,
        informant_distance=1,
        event_type="value_realization",
        description="realización de valor (física)",
    )
    add_node(
        "EVT-10",
        "Event",
        "Cobro conciliado (valor asegurado)",
        generated=True,
        generation_basis="evidence",
        confidence=0.75,
        informant_distance=1,
        event_type="value_realization",
        description="terminal — cobro conciliado",
    )

    for node in nodes:
        if node["id"] == "EVT-07":
            node["properties"]["event_type"] = "milestone"
            node["properties"]["note"] = "Pago acreditado; ya no es terminal de valor."

    for row in parse_table_rows(section(md, "CustomerJourneyStep"), r"CJS-\d+"):
        add_node(row[0], "CustomerJourneyStep", row[1], generated=False, status="inferred")

    for row in parse_table_rows(section(md, "MetricDriver"), r"MDR-\d+"):
        did, name, hypothetical = row[0], row[1], row[2]
        add_node(
            did,
            "MetricDriver",
            name,
            generated=False,
            status="candidate",
            hypothetical_metric=hypothetical,
        )

    for metric in METRICS:
        add_node(
            metric["id"],
            "Metric",
            metric["name"],
            generated=True,
            generation_basis=metric["generation_basis"],
            confidence=metric["confidence"],
            informant_distance=metric["informant_distance"],
            definition=metric["definition"],
        )

    precedes_edges: set[tuple[str, str]] = set()
    for left, right in zip(PRECEDES_MAIN_CHAIN, PRECEDES_MAIN_CHAIN[1:]):
        precedes_edges.add((left, right))
        add_rel(left, right, "PRECEDES", generated=False)
    for left, right in PRECEDES_EXTRA:
        precedes_edges.add((left, right))
        add_rel(left, right, "PRECEDES", generated=False)
    for left, right in PRECEDES_GENERATED:
        precedes_edges.add((left, right))
        add_rel(left, right, "PRECEDES", generated=True, generation_basis="logical", confidence=0.75)
    for left, right, basis, conf in PRECEDES_FEEDERS:
        precedes_edges.add((left, right))
        add_rel(
            left,
            right,
            "PRECEDES",
            generated=True,
            generation_basis=basis,
            confidence=conf,
            informant_distance=1,
        )

    for aid, sid in USES_SYSTEM_EXTRACTED:
        add_rel(aid, sid, "USES_SYSTEM", generated=False)
    for aid, sid, conf, basis in USES_SYSTEM_GENERATED:
        add_rel(aid, sid, "USES_SYSTEM", generated=True, confidence=conf, generation_basis=basis)

    for entry in INVOLVES_EVENT:
        aid, eid, role = entry[0], entry[1], entry[2]
        extra = {}
        gen = False
        if len(entry) > 3:
            extra["confidence"] = entry[3]
            extra["generation_basis"] = entry[4]
            gen = True
        add_rel(aid, eid, "INVOLVES_EVENT", generated=gen, event_role=role, **extra)
        if role == "responde_a":
            precedes_edges.add((eid, aid))
            add_rel(eid, aid, "PRECEDES", generated=gen or True, synthetic=True, **extra)
        elif role == "produce":
            precedes_edges.add((aid, eid))
            add_rel(aid, eid, "PRECEDES", generated=gen or True, synthetic=True, **extra)

    for acts, cap, conf, basis in SUPPORTS_GENERATED:
        for aid in acts:
            add_rel(aid, cap, "SUPPORTS", generated=True, confidence=conf, generation_basis=basis)

    for team, proc, conf in OWNS_PROCESS:
        add_rel(team, proc, "OWNS", generated=True, confidence=conf, informant_distance=1)
    for team, cap in OWNS_CAPABILITY:
        add_rel(team, cap, "OWNS", generated=True, confidence=1.0, informant_distance=1)

    for driver, metric in DRIVES:
        add_rel(
            driver,
            metric,
            "DRIVES",
            generated=True,
            generation_basis="abduction",
            confidence=0.5,
            informant_distance=3,
        )

    for aid, driver, conf in AFFECTS_DRIVER:
        add_rel(
            aid,
            driver,
            "AFFECTS",
            generated=True,
            generation_basis="evidence",
            confidence=conf,
            informant_distance=1,
        )
    for aid, metric, conf in AFFECTS_METRIC:
        add_rel(
            aid,
            metric,
            "AFFECTS",
            generated=True,
            generation_basis="abduction",
            confidence=conf,
            informant_distance=2,
        )
    for proc, metric, conf in CONTRIBUTES:
        add_rel(
            proc,
            metric,
            "CONTRIBUTES_TO",
            generated=True,
            generation_basis="abduction",
            confidence=conf,
            informant_distance=2,
        )
    for aid, cjs in TOUCHES:
        add_rel(
            aid,
            cjs,
            "TOUCHES",
            generated=True,
            generation_basis="evidence",
            confidence=0.75,
            informant_distance=2,
        )

    _validate(nodes, relationships, precedes_edges)

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    graph_doc = {
        "scenario_id": SCENARIO_ID,
        "title": GRAPH_TITLE,
        "source": str(INVENTORY_PATH.relative_to(REPO_ROOT)),
        "meta": {
            "kind": "ai_enhanced",
            "source_nature": "real_interview_extraction_plus_generated_fill_f2",
            "metrics_available": True,
            "generated_fill": True,
            "paso_7_feeders": True,
            "paso_9_f2": True,
            "synthetic_event_precedes": True,
            "node_count": len(nodes),
            "relationship_count": len(relationships),
        },
        "nodes": nodes,
        "relationships": relationships,
    }

    metrics_doc = {
        "scenario_id": SCENARIO_ID,
        "metrics": [
            {
                "id": m["id"],
                "name": m["name"],
                "definition": m["definition"],
                "client_need": m["client_need"],
            }
            for m in METRICS
        ],
        "metric_drivers": [
            {
                "id": node["id"],
                "parent_metric_id": None,
                "name": node["label"],
                "description": "",
                "status": "linked",
            }
            for node in nodes
            if node["type"] == "MetricDriver"
        ],
    }

    relevance_activities = []
    for row in SCORED_ACTIVITIES:
        aid = row[0]
        meta = activity_meta.get(aid, {"name": aid, "process_id": ""})
        entry: dict = {
            "activity_id": aid,
            "activity_name": meta["name"],
            "process_id": meta.get("process_id", ""),
            "p": row[1],
            "p_confidence": row[2],
            "c": row[3],
            "c_confidence": row[4],
            "r": row[5],
            "r_confidence": row[6],
        }
        if row[7] is not None:
            entry["f"] = row[7]
            entry["f_confidence"] = row[8]
        if len(row) > 9 and row[9]:
            entry["score_flag"] = row[9]
        if len(row) > 10 and row[10]:
            # Paso 8: C/R/F filled in simulation mode for contested/tier_bajo feeders.
            entry["c_basis"] = row[10]
            entry["r_basis"] = row[10]
            if "f" in entry:
                entry["f_basis"] = row[10]
        relevance_activities.append(entry)

    relevance_doc = {
        "scenario_id": SCENARIO_ID,
        "compose_at_runtime": True,
        "formulas": {
            "v": "0.3*P + 0.4*C + 0.2*F + 0.1*R (reweight null dims)",
            "b": "0.4*G + 0.4*J + 0.2*DV",
            "relevance": "B * V",
        },
        "activities": relevance_activities,
        "matrix": [],
        "process_rollups": [],
        "rankings_by_metric": {},
        "strategic_b_zero": [],
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
            "kind": "ai_enhanced",
            "paths": {
                "graph": f"{rel_prefix}/graph.json",
                "metrics": f"{rel_prefix}/metrics.json",
                "relevance": f"{rel_prefix}/relevance.json",
                "copy": f"{rel_prefix}/copy.md",
            },
        }
    )

    print(f"Wrote {OUT_DIR}/graph.json ({len(nodes)} nodes, {len(relationships)} rels)")
    print(f"Updated manifest: {SCENARIO_ID} (kind=ai_enhanced)")


def _validate(
    nodes: list[dict],
    relationships: list[dict],
    precedes_edges: set[tuple[str, str]],
) -> None:
    node_ids = {node["id"] for node in nodes}
    for rel in relationships:
        if rel["source"] not in node_ids or rel["target"] not in node_ids:
            raise ValueError(f"Dangling edge: {rel}")

    chain = [
        "EVT-01", "ACT-01", "ACT-03", "ACT-04", "ACT-05", "ACT-06", "ACT-24",
        "ACT-08", "ACT-33", "ACT-10", "ACT-11", "ACT-12", "ACT-13", "EVT-10",
    ]
    for left, right in zip(chain, chain[1:]):
        if (left, right) not in precedes_edges:
            raise ValueError(f"Missing value path edge: {left} → {right}")

    if {"ACT-25", "ACT-29", "TEA-04"} & node_ids:
        raise ValueError("F2 retired nodes must be absent: ACT-25, ACT-29, TEA-04")
    if ("ACT-25", "ACT-10") in precedes_edges:
        raise ValueError("v4 oficial must not gate invoicing on delivery: ACT-25 → ACT-10")
    for extracted in F2_EXTRACTED_ACTIVITIES:
        if extracted["id"] not in node_ids:
            raise ValueError(f"Missing F2 extracted activity: {extracted['id']}")

    feeder_ids = {f["id"] for f in FEEDER_ACTIVITIES}
    present = {node["id"] for node in nodes if node["id"] in feeder_ids}
    if present != feeder_ids:
        raise ValueError(f"Missing feeder activities: {feeder_ids - present}")

    for left, right, _basis, _conf in PRECEDES_FEEDERS:
        if (left, right) not in precedes_edges:
            raise ValueError(f"Missing feeder PRECEDES: {left} → {right}")


def _demo_copy() -> str:
    return """# Eneroil (datos reales) v4 — oficial

Inventario oficial (F2): mismo llenado que v3 con Paso 9 — ACT-25 y ACT-29
retirados, TEA-04 (Planeación) no es de Eneroil, ACT-32/33 extraídos,
facturación tras recepción del BOL (ACT-33 → ACT-10). Nodos/aristas con
`generated=true` cierran brechas con confianza explícita.

## Caveats

- Métricas MET-01..03 son **abducciones** (confianza ≤ 0.5), pendientes JTBD.
- MET-01 es dependencia estructural externa: Eneroil no ejecuta la entrega.
- ACT-05/06/07/26/28/32/33 sin `PERFORMS` (equipo Eneroil no resuelto).
- ACT-28 confirmado informal (`informal_no_documentado`); ya no `void_on_collapse`.
- CJS-04 sin `TOUCHES` interno (entrega = empresa de logística externa).
- Use **Mapa de confianza** en Grafo para ver certidumbre rojo→azul.

Fuente: `data/raw/Eneroil_Inventario_Grafo_v4 (oficial).md`
"""


if __name__ == "__main__":
    build()
