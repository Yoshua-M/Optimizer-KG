# Eneroil (datos reales) v1 — escenario estructural

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
