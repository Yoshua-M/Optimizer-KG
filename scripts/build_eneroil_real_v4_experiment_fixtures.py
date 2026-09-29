#!/usr/bin/env python3
"""Build Eneroil real-data v4 experiment (walkthrough-validated) demo fixtures.

Source: data/raw/Eneroil_Inventario_Grafo_v4 (experiment).md — v3 plus transcript
validation (Eneroil.mp3.txt). Scenario kind ai_enhanced.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = REPO_ROOT / "configs/demo_scenarios.json"
INVENTORY_PATH = REPO_ROOT / "data/raw/Eneroil_Inventario_Grafo_v4 (experiment).md"
OUT_DIR = REPO_ROOT / "data/processed/demo/eneroil_real_v4_experiment"

SCENARIO_ID = "eneroil_real_v4_experiment"
SCENARIO_TITLE = "Eneroil (datos reales) v4 — experiment"
SCENARIO_DESCRIPTION = (
    "Experimental: inventario real v3 validado con transcripción del walkthrough: "
    "feeders ACT-24–29 extraídos, facturación al cargar (no al entregar), "
    "empresa hermana de logística, Tesorería, Excel, path de merma."
)
GRAPH_TITLE = "Eneroil S.A. de C.V. — extracción real v4 experiment (walkthrough)"

TEAM_IDS_BY_OWNER_LABEL: dict[str, tuple[str, ...]] = {
    "Comercial": ("TEA-03",),
    "Monitoreo y Precios": ("TEA-02",),
    "Planeación": ("TEA-04",),
    "Empresa hermana — Planeación y operaciones": ("TEA-04",),
    "Compras": ("TEA-05",),
    "Facturación": ("TEA-06",),
    "Operaciones / Facturación": ("TEA-06",),
    "Cobranza": ("TEA-08",),
    "Cobranza / Dirección": ("TEA-08", "TEA-01"),
    "Calidad / Cumplimiento": ("TEA-07",),
    "Dirección General": ("TEA-01",),
    "Dirección / Cumplimiento": ("TEA-01", "TEA-07"),
    "Tesorería": ("TEA-10",),
    "Proveedor (externo)": (),
}

PRECEDES_MAIN_CHAIN = [
    "ACT-01", "ACT-03", "ACT-04", "ACT-05", "ACT-06", "ACT-07", "ACT-08",
    "ACT-09", "ACT-10", "ACT-11", "ACT-12", "ACT-13", "ACT-14",
]
PRECEDES_EXTRA = [
    ("ACT-02", "ACT-03"),
    ("ACT-12", "ACT-15"),
    ("ACT-15", "ACT-16"),
    ("ACT-16", "ACT-17"),
    ("ACT-06", "ACT-24"),
    ("ACT-24", "ACT-33"),
    ("ACT-33", "ACT-08"),
    ("ACT-08", "ACT-25"),
    ("ACT-08", "ACT-10"),
    ("ACT-26", "ACT-03"),
    ("ACT-27", "ACT-13"),
    ("ACT-28", "ACT-05"),
    ("ACT-29", "ACT-05"),
    ("ACT-32", "ACT-04"),
    ("ACT-36", "ACT-10"),
    ("ACT-06", "ACT-38"),
]
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
    ("ACT-30", "ACT-24", "logical", 0.5),
    ("ACT-31", "ACT-15", "logical", 0.5),
]

USES_SYSTEM_EXTRACTED = [
    ("ACT-01", "SYS-03"),
    ("ACT-01", "SYS-04"),
    ("ACT-09", "SYS-06"),
    ("ACT-10", "SYS-02"),
    ("ACT-11", "SYS-04"),
    ("ACT-13", "SYS-06"),
    ("ACT-13", "SYS-05"),
    ("ACT-14", "SYS-06"),
    ("ACT-16", "SYS-06"),
    ("ACT-16", "SYS-04"),
    ("ACT-27", "SYS-05"),
    ("ACT-28", "SYS-07"),
    ("ACT-28", "SYS-08"),
    ("ACT-33", "SYS-06"),
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
    ("ACT-25", "EVT-09", "produce"),
    ("ACT-13", "EVT-10", "produce"),
    ("ACT-34", "EVT-11", "responde_a"),
    ("ACT-35", "EVT-12", "responde_a"),
    ("ACT-38", "EVT-13", "produce"),
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
    "EVT-11": "exception",
    "EVT-12": "exception",
    "EVT-13": "exception",
}

SUPPORTS_GENERATED = [
    (("ACT-01", "ACT-03", "ACT-04", "ACT-26"), "CAP-02", 1.0, "evidence"),
    (("ACT-02",), "CAP-01", 1.0, "evidence"),
    (("ACT-05", "ACT-07", "ACT-25", "ACT-28", "ACT-29", "ACT-39"), "CAP-03", 1.0, "evidence"),
    (("ACT-06", "ACT-22", "ACT-24", "ACT-33", "ACT-38"), "CAP-04", 1.0, "evidence"),
    (("ACT-08",), "CAP-04", 0.5, "evidence"),
    (("ACT-09",), "CAP-07", 0.75, "evidence"),
    (("ACT-10", "ACT-11", "ACT-34", "ACT-35", "ACT-36"), "CAP-05", 1.0, "evidence"),
    (("ACT-12", "ACT-13", "ACT-14", "ACT-15", "ACT-16", "ACT-17", "ACT-27"), "CAP-06", 1.0, "evidence"),
    (("ACT-18", "ACT-23"), "CAP-07", 1.0, "evidence"),
    (("ACT-19", "ACT-20", "ACT-21"), "CAP-08", 1.0, "evidence"),
    (("ACT-32",), "CAP-09", 1.0, "evidence"),
    (("ACT-35", "ACT-39"), "CAP-10", 1.0, "evidence"),
]

OWNS_PROCESS = [
    ("TEA-02", "PRO-01", 1.0),
    ("TEA-03", "PRO-02", 1.0),
    ("TEA-04", "PRO-03", 1.0),
    ("TEA-05", "PRO-04", 0.75),
    ("TEA-06", "PRO-05", 1.0),
    ("TEA-08", "PRO-06", 1.0),
    ("TEA-07", "PRO-07", 1.0),
    ("TEA-07", "PRO-08", 1.0),
    ("TEA-07", "PRO-09", 1.0),
]

OWNS_CAPABILITY = [
    ("TEA-02", "CAP-01"), ("TEA-03", "CAP-02"), ("TEA-04", "CAP-03"),
    ("TEA-04", "CAP-10"), ("TEA-05", "CAP-04"), ("TEA-06", "CAP-05"),
    ("TEA-08", "CAP-06"), ("TEA-07", "CAP-07"), ("TEA-07", "CAP-08"),
    ("TEA-07", "CAP-09"),
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
    ("MDR-07", "MET-01"),
    ("MDR-08", "MET-02"),
]

AFFECTS_DRIVER = [
    ("ACT-10", "MDR-01", 0.75),
    ("ACT-13", "MDR-05", 0.75),
    ("ACT-12", "MDR-03", 0.75),
    ("ACT-36", "MDR-08", 0.75),
    ("ACT-35", "MDR-07", 0.75),
    ("ACT-39", "MDR-07", 0.75),
]

AFFECTS_METRIC = [
    ("ACT-05", "MET-01", 0.5),
    ("ACT-25", "MET-01", 0.5),
    ("ACT-16", "MET-03", 0.5),
]

CONTRIBUTES = [
    ("PRO-05", "MET-02", 0.5),
    ("PRO-06", "MET-03", 0.5),
    ("PRO-03", "MET-01", 0.5),
]

TOUCHES = [
    ("ACT-01", "CJS-01", 0.75),
    ("ACT-03", "CJS-02", 0.75),
    ("ACT-04", "CJS-03", 0.75),
    ("ACT-25", "CJS-04", 0.75),
    ("ACT-11", "CJS-05", 0.75),
    ("ACT-16", "CJS-06", 0.75),
    ("ACT-19", "CJS-08", 0.25),
    ("ACT-35", "CJS-08", 0.75),
]

SCORED_ACTIVITIES = [
    ("ACT-01", 0.25, 0.75, 0.25, 0.5, 0.25, 0.5, 1.0, 0.5),
    ("ACT-03", 0.25, 0.75, 0.5, 0.5, 0.5, 0.5, 1.0, 0.5),
    ("ACT-05", 0.5, 0.75, 0.5, 0.5, 0.5, 0.5, None, None),
    ("ACT-08", 0.75, 0.75, 0.75, 0.75, 1.0, 0.75, 1.0, 0.5),
    ("ACT-10", 0.75, 0.75, 1.0, 0.75, 1.0, 0.75, 1.0, 0.5),
    ("ACT-11", 0.75, 0.5, 0.75, 0.5, 0.5, 0.5, 1.0, 0.5),
    ("ACT-12", 0.75, 0.5, 0.75, 0.75, 0.75, 0.75, None, None),
    ("ACT-13", 1.0, 0.75, 0.75, 0.75, 0.75, 0.75, None, None),
    ("ACT-15", 0.75, 0.5, 0.5, 0.5, 0.5, 0.5, None, None),
    ("ACT-16", 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, None, None),
    ("ACT-17", 1.0, 0.5, 0.5, 0.5, 0.75, 0.5, None, None),
    ("ACT-19", 0.25, 0.75, 0.25, 0.5, 0.25, 0.5, None, None),
    ("ACT-24", 0.5, 0.75, 0.75, 0.75, 0.75, 0.75, 1.0, 0.5),
    ("ACT-25", 0.75, 0.75, 0.75, 0.75, 0.75, 0.75, None, None),
    ("ACT-26", 0.25, 0.75, 0.5, 0.75, 0.5, 0.75, 1.0, 0.5),
    ("ACT-27", 0.75, 0.75, 0.75, 0.75, 0.75, 0.75, 1.0, 0.5),
    ("ACT-28", 0.5, 0.75, 0.5, 0.75, 0.75, 0.75, 1.0, 0.5),
    ("ACT-29", 0.5, 0.75, 0.5, 0.75, 0.5, 0.75, 1.0, 0.5),
    ("ACT-30", 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.75, 0.5, "tier_bajo", "simulated"),
    ("ACT-31", 0.75, 0.5, 0.75, 0.5, 0.75, 0.5, 0.75, 0.5, "void_on_collapse", "simulated"),
    ("ACT-34", 0.75, 0.75, 0.75, 0.75, 0.5, 0.5, 1.0, 0.5),
    ("ACT-35", 0.75, 0.75, 0.75, 0.75, 0.75, 0.75, None, None),
    ("ACT-36", 0.75, 0.75, 1.0, 0.75, 0.75, 0.75, 1.0, 0.5),
    ("ACT-38", 0.75, 0.75, 0.75, 0.75, 0.75, 0.75, 1.0, 0.5),
]

FEEDER_ACTIVITIES = [
    {
        "id": "ACT-30",
        "name": "Autorización de liberación de fondos para prepago",
        "confidence": 0.5,
        "evidence_pointer": (
            "prepago (ACT-24) exige fondos; dueño Tesorería vs Dirección aún incierto"
        ),
        "fill_flag": "tier_bajo",
        "team_id": "TEA-10",
        "team_confidence": 0.5,
        "process_id": None,
    },
    {
        "id": "ACT-31",
        "name": "Identificación de facturas vencidas",
        "confidence": 0.5,
        "evidence_pointer": (
            '"contacto por vencida" (ACT-15) + crédito típico 3 días'
        ),
        "fill_flag": "contested_external",
        "team_id": "TEA-08",
        "team_confidence": 0.5,
        "process_id": "PRO-06",
        "process_confidence": 0.75,
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


def _is_external_owner(owner_label: str, team_ids: tuple[str, ...]) -> bool:
    if not team_ids:
        return True
    lower = owner_label.lower()
    return "hermana" in lower or "externo" in lower


def build() -> None:
    md = INVENTORY_PATH.read_text(encoding="utf-8")
    nodes: list[dict] = []
    relationships: list[dict] = []
    activity_meta: dict[str, dict] = {}

    def add_node(nid: str, ntype: str, label: str, *, generated: bool = False, **props: object) -> None:
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
        team_ids = TEAM_IDS_BY_OWNER_LABEL.get(owner_label)
        if team_ids is None:
            raise ValueError(f"{aid}: unmapped owner label {owner_label!r}")
        activity_meta[aid] = {
            "name": name,
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
            external_owner=_is_external_owner(owner_label, team_ids) or None,
        )
        for team_id in team_ids:
            add_rel(team_id, aid, "PERFORMS", generated=False)

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
        label = strip_markdown(raw_label.split("*(")[0])
        extra: dict[str, object] = {}
        if "hermana" in label.lower() or "externo" in raw_label.lower():
            extra["external"] = True
        add_node(row[0], "Team", label, generated=False, **extra)
    for row in parse_table_rows(section(md, "Capability"), r"CAP-\d+"):
        add_node(row[0], "Capability", row[1], generated=False)
    for row in parse_table_rows(section(md, "System"), r"SYS-\d+"):
        add_node(row[0], "System", row[1], generated=False, function=row[2])

    for row in parse_table_rows(section(md, "Event"), r"EVT-\d+"):
        eid, name, role = row[0], row[1], strip_markdown(row[2])
        add_node(eid, "Event", name, generated=False, description=role, event_type=EVENT_TYPES[eid])

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

    for entry in INVOLVES_EVENT:
        aid, eid, role = entry[0], entry[1], entry[2]
        add_rel(aid, eid, "INVOLVES_EVENT", generated=False, event_role=role)
        if role == "responde_a":
            precedes_edges.add((eid, aid))
            add_rel(eid, aid, "PRECEDES", generated=True, synthetic=True)
        elif role == "produce":
            precedes_edges.add((aid, eid))
            add_rel(aid, eid, "PRECEDES", generated=True, synthetic=True)

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
    for aid, cjs, conf in TOUCHES:
        add_rel(
            aid,
            cjs,
            "TOUCHES",
            generated=True,
            generation_basis="evidence",
            confidence=conf,
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
            "source_nature": "real_interview_plus_walkthrough_validation",
            "metrics_available": True,
            "generated_fill": True,
            "walkthrough_v4": True,
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
        "ACT-33", "ACT-08", "ACT-10", "ACT-11", "ACT-12", "ACT-13", "EVT-10",
    ]
    for left, right in zip(chain, chain[1:]):
        if (left, right) not in precedes_edges:
            raise ValueError(f"Missing value path edge: {left} → {right}")

    if ("ACT-25", "ACT-10") in precedes_edges:
        raise ValueError("v4 must not gate invoicing on delivery: ACT-25 → ACT-10")

    feeder_ids = {f["id"] for f in FEEDER_ACTIVITIES}
    present = {node["id"] for node in nodes if node["id"] in feeder_ids}
    if present != feeder_ids:
        raise ValueError(f"Missing feeder activities: {feeder_ids - present}")

    for left, right, _basis, _conf in PRECEDES_FEEDERS:
        if (left, right) not in precedes_edges:
            raise ValueError(f"Missing feeder PRECEDES: {left} → {right}")


def _demo_copy() -> str:
    return """# Eneroil (datos reales) v4 — experiment

Parche experimental sobre v3 con la transcripción del walkthrough (`Eneroil.mp3.txt`):
feeders ACT-24–29 **extraídos** (ya no generated), facturación al **cargar**
(no al entregar), planeación/ops en la **empresa hermana**, Tesorería
(Isabel), Excel como sistema de registro, excepción real = **merma**.

## Caveats

- Métricas MET-01..03 siguen **abducciones** (confianza ≤ 0.5), pendientes JTBD.
- MET-03 no se promueve: el dolor es conciliación interna, no queja de cliente.
- ACT-30/31 siguen generated (`tier_bajo` / `contested_external`).
- Subgrafo logístico de la hermana y PRO-10/11: stub, esperando procedimientos.
- Sin nodos Supplier/Product/Regulator. Nexus = migración prevista, no nodo.
- Use **Mapa de confianza** en Grafo para ver certidumbre rojo→azul.

Fuente: `data/raw/Eneroil_Inventario_Grafo_v4 (experiment).md`
"""


if __name__ == "__main__":
    build()
