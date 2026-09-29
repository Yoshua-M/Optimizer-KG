
# BLOQUE 4 — Actividades de control y desperdicio

> **⚠️ ESTE BLOQUE NO SE INGESTA AL SISTEMA.**
> Son actividades reales en muchas organizaciones, pero que no contribuyen al valor del cliente. Se incluyen para verificar que el sistema las clasifique correctamente como B≈0 y las surfacee como candidatas a eliminación o automatización. Son el caso de prueba del hallazgo "alto V, B=0".

---

## 4.1 Nodos de actividades de control (6 nodos)

| ID | Nombre de la Actividad | Área(s) Porter | Frecuencia | Razón de existencia |
|----|------------------------|----------------|------------|---------------------|
| W-01 | Elaboración de reporte mensual de gestión para comité directivo | Núcleo de Gobernanza | Mensual | Requerimiento de gobierno corporativo interno; los datos están disponibles en ERP pero se reensamblan manualmente para presentación |
| W-02 | Reunión semanal de coordinación inter-áreas sin entregable concreto | Núcleo de Gobernanza, múltiples | Semanal | Hábito organizacional de cuando la empresa era más pequeña; hoy es mayormente informativa sin decisiones ni acciones documentadas |
| W-03 | Actualización manual de bitácora de incidentes en hoja de cálculo | Logística Externa, Operaciones | Diaria | Proceso duplicado: la misma información ya queda registrada en el sistema GPS y en el sistema de pedidos; persiste por inercia |
| W-04 | Proceso de solicitud y aprobación de viáticos para visitas comerciales | Núcleo de Gobernanza, Gestión de RRHH | Semanal | Control financiero administrativo; genera fricción al equipo comercial sin impacto en el cliente; podría delegarse con un límite preautorizado |
| W-05 | Validación cruzada manual entre ERP y Portal SAT/CRE | Núcleo de Gobernanza, Desarrollo Tecnológico | Semanal | Falta de integración entre sistemas; debería ser automática pero se hace manualmente por cada ciclo de reporte; candidata directa a automatización |
| W-06 | Generación trimestral de presentación de resultados para socios e inversionistas | Núcleo de Gobernanza | Trimestral | Relación con inversionistas; necesaria para la empresa pero sin vínculo alguno con la operación o el valor percibido por el cliente |

---

## 4.2 Cuantificación de actividades de control

> W-05 es el caso más interesante para el demo: V moderado (hay real esfuerzo y riesgo) pero B=0 — la hace candidata perfecta a "desperdicio con alto costo de oportunidad" si se automatiza.

| ID | P | C | F | R | V(A) | B esperado | Clasificación |
|----|---|---|---|---|------|------------|---------------|
| W-01 | 0.25 | 0.25 | 0.50 | 0.25 | 0.28 | ≈ 0 | Gobernanza interna sin valor cliente |
| W-02 | 0.25 | 0.25 | 0.75 | 0.25 | 0.33 | ≈ 0 | Overhead organizacional |
| W-03 | 0.25 | 0.25 | 1.0 | 0.25 | 0.35 | ≈ 0 | Proceso duplicado — candidato a eliminación |
| W-04 | 0.25 | 0.25 | 0.75 | 0.25 | 0.33 | ≈ 0 | Fricción administrativa |
| W-05 | 0.50 | 0.50 | 0.75 | 0.50 | 0.53 | ≈ 0 | Brecha de integración — candidato a automatización (V alto, B=0) |
| W-06 | 0.25 | 0.25 | 0.25 | 0.25 | 0.25 | ≈ 0 | Relaciones con inversionistas — fuera del ciclo de valor operativo |

---

## 4.3 Relaciones de las actividades de control

> Las actividades de control no tienen PRECEDES hacia actividades del grafo principal ni AFFECTS hacia métricas. Su aislamiento en el grafo es parte de lo que el sistema debe detectar.

### PRECEDES entre actividades de control (internas)
| Origen | Destino | Lógica |
|--------|---------|--------|
| W-03 | W-01 | Los datos de incidentes registrados en la bitácora manual se incluyen en el reporte mensual de gestión |
| W-05 | W-01 | La validación cruzada produce un dato que alimenta el reporte mensual |
| W-01 | W-06 | El reporte mensual se consolida en la presentación trimestral para socios |

### Sin relaciones con métricas
Ninguna actividad W tiene edge AFFECTS → Metric ni TOUCHES → CustomerJourneyStep.
Su B(A,M) = 0 para todas las métricas es el resultado esperado y el hallazgo que el sistema debe reportar.