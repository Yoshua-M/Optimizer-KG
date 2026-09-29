# Experimento: Eneroil real-data v1 (escenario estructural)

**Estado:** experimental — decisiones pendientes sobre métricas y ontología.  
**Última actualización:** 2026-07-14  
**Escenario demo:** `eneroil_real_v1` (`kind: structural`)

Este documento registra **todos los cambios** introducidos para poder revisarlos, revertirlos o extenderlos cuando se decida el tratamiento definitivo de inventarios reales sin métricas de valor cliente.

---

## Contexto y decisión pendiente

| Pregunta abierta | Opciones en evaluación |
|------------------|------------------------|
| ¿Graficar métricas en inventarios reales? | Mantener solo estructura (actual) vs. añadir nodos `Metric` tras JTBD |
| ¿Puntuar P/C/F/R/V antes de métricas? | No (actual) — el inventario lo bloquea explícitamente |
| ¿Unificar con fixtures Energoil simulados? | Mismo loader/UI con `kind` distinto vs. pipeline separado |

**Fuente de datos:** entrevista interna real (*Optimizer — Preguntas Iniciales*, Eneroil S.A. de C.V., junio 2026).  
**Inventario:** [`data/raw/Eneroil_Inventario_Grafo_v1.md`](../../data/raw/Eneroil_Inventario_Grafo_v1.md)

---

## Resumen de lo implementado

1. Inventario colocado en `data/raw/` junto a los tres Energoil simulados.
2. Builder dedicado que produce fixtures JSON sin métricas ni relevancia.
3. Nuevo escenario en `configs/demo_scenarios.json` con `kind: "structural"`.
4. Contrato `DemoScenario.kind` + degradación de UI para escenarios sin métricas.
5. Colores PyVis para `Team`, `System`, `Event` (beneficia todos los escenarios).
6. Tests de validación del fixture y carga en demo.
7. Entrada en `docs/CHANGELOG.md`.
8. **Fix Flujos de valor:** etiquetas de actividad con nombre (no solo `ACT-NN`) usando nodos del grafo cuando no hay `relevance.json`.

---

## Archivos nuevos

| Archivo | Propósito |
|---------|-----------|
| `data/raw/Eneroil_Inventario_Grafo_v1.md` | Inventario fuente (copia desde Downloads) |
| `scripts/build_eneroil_real_fixtures.py` | Parser + generador de fixtures estructurales |
| `data/processed/demo/eneroil_real_v1/graph.json` | Grafo (75 nodos, 125 relaciones) |
| `data/processed/demo/eneroil_real_v1/metrics.json` | Stub: `metrics: []`, drivers candidatos, hipótesis M?-01/02/03 |
| `data/processed/demo/eneroil_real_v1/relevance.json` | Stub vacío (sin P/C/F/R/V ni matriz) |
| `data/processed/demo/eneroil_real_v1/copy.md` | Texto explicativo del escenario para demo |
| `tests/graph_analytics/test_eneroil_fixture_validation.py` | Validación de conteos, event_type, VS, kind |
| `docs/experiments/eneroil_real_v1_structural.md` | **Este archivo** — bitácora del experimento |

---

## Archivos modificados

| Archivo | Cambio |
|---------|--------|
| `configs/demo_scenarios.json` | Entrada `eneroil_real_v1` con `kind: "structural"` (upsert por builder) |
| `src/optimizer/application/demo_models.py` | Campo `DemoScenario.kind` (default `"value"`) |
| `src/optimizer/infrastructure/demo_loader.py` | Lee `kind` del manifiesto |
| `src/optimizer/presentation/streamlit_demo_app.py` | Banner estructural; Valor/Analíticas condicionales |
| `src/optimizer/presentation/scenario_views.py` | `render_structural_value_tab()` |
| `src/optimizer/presentation/analytics_views.py` | Aviso + etiqueta "no disponible sin métricas" |
| `src/optimizer/infrastructure/visualization/pyvis_graph.py` | Colores `Team` / `System` / `Event` |
| `src/optimizer/application/value_stream_flow.py` | Labels de actividad desde `graph_documents` |
| `src/optimizer/graph_analytics/value_stream_flow.py` | Fallback de label desde propiedades del nodo |
| `tests/application/test_value_stream_flow.py` | Test nombres en flujo para `eneroil_real_v1` |
| `docs/CHANGELOG.md` | Entrada 2026-07-14 |
| `src/optimizer/infrastructure/AGENTS.md` | Documenta `kind` en demo_loader |
| `src/optimizer/presentation/AGENTS.md` | Documenta UI estructural y `render_structural_value_tab` |

---

## Contrato del escenario estructural

### Manifiesto (`configs/demo_scenarios.json`)

```json
{
  "id": "eneroil_real_v1",
  "kind": "structural",
  "paths": {
    "graph": "data/processed/demo/eneroil_real_v1/graph.json",
    "metrics": "data/processed/demo/eneroil_real_v1/metrics.json",
    "relevance": "data/processed/demo/eneroil_real_v1/relevance.json",
    "copy": "data/processed/demo/eneroil_real_v1/copy.md"
  }
}
```

- `metrics` y `relevance` **siguen siendo obligatorios** en disco (contrato del loader), pero pueden estar vacíos.
- Escenarios Energoil existentes no declaran `kind` → default `"value"`.

### Grafo (`graph.json`)

| Tipo | Cantidad | IDs |
|------|----------|-----|
| Activity | 23 | `ACT-01` … `ACT-23` |
| Process | 9 | `PRO-01` … `PRO-09` (PRO-10/11 sin nombrar, omitidos) |
| Team | 8 | `TEA-01` … `TEA-08` |
| Capability | 8 | `CAP-01` … `CAP-08` |
| System | 5 | `SYS-01` … `SYS-05` |
| Event | 8 | `EVT-01` … `EVT-08` |
| CustomerJourneyStep | 8 | `CJS-01` … `CJS-08` (`status: inferred`) |
| MetricDriver | 6 | `MDR-01` … `MDR-06` (`status: candidate`) |
| **Metric** | **0** | — |

**Relaciones emitidas:** `PERFORMS`, `PART_OF`, `PRECEDES`, `USES_SYSTEM`, `INVOLVES_EVENT`, `SUPPORTS` (derivado), `OWNS` (derivado).  
**No emitidas (bloqueadas o débiles):** `AFFECTS→Metric`, `TOUCHES→CJS`, `HAS_DRIVER`, `SIGNALS`.

**Event types:** `EVT-01` demand, `EVT-07` value_realization, resto milestone/exception.  
**PRECEDES sintético** Event↔Activity vía `INVOLVES_EVENT` roles (`produce` / `responde_a`) para descubrir value stream demanda→cobro.

### Métricas (`metrics.json`)

- `metrics: []`
- `metric_drivers`: 6 candidatos con `hypothetical_metric` (M?-02, M?-03)
- `metric_hypotheses`: M?-01, M?-02, M?-03 (no graficadas como nodos)

### Relevancia (`relevance.json`)

- `activities: []`, `matrix: []`, `process_rollups: []`

---

## Comportamiento en la UI (`streamlit run app_demo.py`)

| Pestaña / control | Escenario `value` | Escenario `structural` |
|-------------------|-------------------|------------------------|
| **Grafo** | Completo | Completo (tipos, PyVis, VS panel) |
| **Value streams panel** | Con relevancia acumulada | Topología OK; relevancia = 0 |
| **Flujos de valor (Valor)** | Nombres desde relevance | Nombres desde nodos del grafo (`ACT-NN — nombre`) |
| **Analíticas** | 36 runners | ~20 OK (topológicas); resto "no disponible sin métricas" |
| **Valor (plots)** | Plotly P/C/F/R, matriz | Mensaje explicativo + solo Flujos de valor |
| **Sidebar actividad** | Selector con scores | Oculto (sin activities en relevance) |
| **Mapa de calor / explain** | Disponible | Sin datos de relevancia (controles vacíos) |

---

## Cómo regenerar fixtures

```bash
cd /home/tripleyosh/Desktop/Coding/knowledge-graph-llms
graph_env/bin/python3 scripts/build_eneroil_real_fixtures.py
```

Editar el inventario en `data/raw/Eneroil_Inventario_Grafo_v1.md` y volver a ejecutar el builder.

---

## Tests

```bash
graph_env/bin/python3 -m unittest tests.graph_analytics.test_eneroil_fixture_validation -v
graph_env/bin/python3 -m unittest tests.application.test_value_stream_flow.TestFlowStoryOptions.test_eneroil_real_v1_flow_activities_show_names -v
```

Suite completa: 180 tests (incluye los nuevos).

---

## Changelog de este experimento

| Fecha | Cambio |
|-------|--------|
| 2026-07-14 | Implementación inicial: fixture, `kind`, UI estructural, colores, tests |
| 2026-07-14 | Fix Flujos de valor: nombres de actividad visibles sin `relevance.json` |
| 2026-07-14 | Creación de este archivo de seguimiento |

---

## Próximos pasos posibles (cuando decidan)

1. **Ruta cliente (JTBD):** validar M?-01/02/03 → crear nodos `Metric` + relaciones `AFFECTS` / `HAS_DRIVER`.
2. **Cuantificación:** tabla P/C/F/R/V en inventario → regenerar `relevance.json` → cambiar `kind` a `"value"`.
3. **Ontología v3:** nodos `Supplier`, `Product`, `Regulator` mencionados en el inventario como huecos.
4. **TOUCHES Activity→CJS:** solo tras validación del journey con clientes.
5. **Revertir experimento:** eliminar entrada del manifiesto, carpeta `eneroil_real_v1/`, y revertir `kind` en código si ya no se necesita.

---

## Referencias

- Inventario fuente: `data/raw/Eneroil_Inventario_Grafo_v1.md`
- Builder: `scripts/build_eneroil_real_fixtures.py`
- Changelog producto: `docs/CHANGELOG.md` (entrada 2026-07-14)
- Comparar con fixtures simulados: `scripts/build_energoil_demo_fixtures.py`, escenarios `energoil_mexico*`
