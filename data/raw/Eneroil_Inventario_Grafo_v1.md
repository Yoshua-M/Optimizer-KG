# Inventario de grafo — Eneroil S.A. de C.V.
*Extracción v1 — sobre Ontología del grafo v2. Julio 2026.*

---

## Nota de origen y alcance

**Fuente:** *Optimizer — Preguntas Iniciales* (entrevista interna, Eneroil S.A. de C.V., junio 2026).

**Naturaleza:** Extracción de **datos reales de cliente**, no simulación. A diferencia del inventario `Energoil_Mexico_Graph_Inventory.md` (datos inventados con misconceptions embebidas y P/C/F/R/V(A) precalculados), aquí **no se asignan puntajes P/C/F/R**. La cuantificación es Capa 3 y requiere primero definir las métricas de valor del cliente; puntuar en esta etapa produciría artefactos, no hallazgos.

**Insumo unilateral:** Este documento es la **ruta interna** (cómo opera la empresa). La **ruta cliente** (investigación JTBD de los clientes de Eneroil) aún no existe — y sin ella no hay nodos `Metric` legítimos (ver sección Metric).

**Conteo de candidatos:**

| Tipo de nodo | Candidatos | Estado |
|---|---|---|
| Activity | 23 | Extraídos del texto |
| Process | 6 operativos (+5 soporte SGC, 3 nombrados) | Parcial |
| Team | 8 | Extraídos |
| Capability | 8 | Inferidos de procesos/roles |
| System | 5 | Extraídos |
| Event | 8 | Extraídos |
| CustomerJourneyStep | 8 | **Inferidos** (interview interna, requieren validación cliente) |
| MetricDriver | 6 | Candidatos (dependen de definir Metric) |
| Metric | 0 confirmados / 3 hipótesis | **Bloqueado** — requiere ruta cliente |

---

## Metric — advertencia estructural

La ontología v2 es explícita: un `Metric` es un **indicador de valor del cliente** derivado de investigación JTBD, **no un KPI interno**. Esta entrevista es interna, así que lo que menciona son KPIs internos, que **no califican como nodo `Metric`**:

- DSO / ciclo de cobro (≤15 días como meta)
- % de cartera vencida (<5% de facturación mensual como meta)
- Flujo de caja proyectado
- Margen por operación
- Indicadores de calidad (genéricos)

Estos son internos y van a la sección "no cubierto por la ontología".

**Hipótesis de métricas de valor del cliente** (candidatas, *pendientes de investigación JTBD sobre los compradores de combustible de Eneroil*):

- **M?-01 — Confiabilidad de entrega:** producto correcto, volumen, destino y fecha según lo pactado.
- **M?-02 — Exactitud y puntualidad de facturación percibida:** el cliente recibe un CFDI correcto y a tiempo (mismo día de entrega en el escenario ideal).
- **M?-03 — Transparencia de cuenta:** el cliente recibe estado de cuenta correcto y puntual, sin disputas.

> Estas se anclan en señales del propio texto ("clientes que disputan facturas o no reciben sus estados de cuenta a tiempo"), pero siguen siendo **hipótesis**. No se deben graficar como `Metric` hasta validarlas con investigación de cliente.

---

## Activity (23)

Flujo demanda → cobro:

| ID | Actividad | Equipo dueño |
|---|---|---|
| ACT-01 | Recepción de solicitud del cliente (WhatsApp / correo / llamada) | Comercial |
| ACT-02 | Obtención y publicación diaria de precios de referencia (Pemex, Valero, Repsol) | Monitoreo y Precios |
| ACT-03 | Elaboración y envío de cotización | Comercial |
| ACT-04 | Confirmación del pedido por el cliente | Comercial |
| ACT-05 | Confirmación de disponibilidad de producto y logística | Planeación |
| ACT-06 | Emisión de Orden de Compra al proveedor (con prepago) | Planeación |
| ACT-07 | Emisión de instrucción de carga al transportista | Planeación |
| ACT-08 | Ejecución de la carga y emisión del BOL | Proveedor (externo) |
| ACT-09 | Registro de la operación en Smartsheet | Compras |
| ACT-10 | Timbrado del CFDI en SAE/ASPEL | Facturación |
| ACT-11 | Envío del CFDI al cliente | Facturación |
| ACT-12 | Seguimiento al pago | Cobranza |
| ACT-13 | Conciliación factura – estado de cuenta bancario – Smartsheet | Cobranza |
| ACT-14 | Registro del pago / saldo en Smartsheet | Cobranza |
| ACT-15 | Contacto al cliente por factura vencida | Cobranza |
| ACT-16 | Generación y envío del estado de cuenta del cliente | Cobranza |
| ACT-17 | Escalamiento a Dirección por cobro vencido | Cobranza / Dirección |

Soporte / cumplimiento:

| ID | Actividad | Equipo dueño |
|---|---|---|
| ACT-18 | Integración del expediente legal por operación (trazabilidad documental) | Calidad / Cumplimiento |
| ACT-19 | Gestión de quejas y no conformidades | Calidad / Cumplimiento |
| ACT-20 | Auditorías internas | Calidad / Cumplimiento |
| ACT-21 | Auditorías a proveedores | Calidad / Cumplimiento |
| ACT-22 | Aprobación de proveedores | Dirección General |
| ACT-23 | Gestión de relación regulatoria y reporte volumétrico (CNE) | Dirección / Cumplimiento |

> **Nota de consolidación:** ACT-02 fusiona obtención + publicación de precios; ACT-03 fusiona cálculo de precio de venta + armado de cotización. Revisar granularidad en el taller de validación.

---

## Process (6 operativos + soporte SGC)

El texto declara **"seis procesos operativos y cinco procesos de soporte del SGC"**.

Operativos:

| ID | Proceso | Actividades |
|---|---|---|
| PRO-01 | Monitoreo y Precios (Obtención y Envío de Precios) | ACT-02 |
| PRO-02 | Cotización al Cliente | ACT-01, ACT-03, ACT-04 |
| PRO-03 | Planeación de la Operación | ACT-05, ACT-06, ACT-07 |
| PRO-04 | Compra y Venta de Combustible | ACT-08, ACT-09 |
| PRO-05 | Facturación | ACT-10, ACT-11 |
| PRO-06 | Cobranza | ACT-12 – ACT-17 |

Soporte (SGC) — solo 3 de 5 nombrados en la entrevista:

| ID | Proceso | Actividades |
|---|---|---|
| PRO-07 | Control / Trazabilidad Documental | ACT-18 |
| PRO-08 | Gestión de Quejas y No Conformidades | ACT-19 |
| PRO-09 | Auditorías internas y a proveedores | ACT-20, ACT-21 |
| PRO-10 | *(sin nombrar)* | — |
| PRO-11 | *(sin nombrar)* | — |

> **Gap del insumo:** faltan 2 procesos de soporte del SGC. Preguntar en la siguiente ronda.

---

## Team (8)

| ID | Equipo |
|---|---|
| TEA-01 | Dirección General |
| TEA-02 | Monitoreo y Precios |
| TEA-03 | Comercial / Ventas |
| TEA-04 | Planeación |
| TEA-05 | Compras |
| TEA-06 | Operaciones / Facturación |
| TEA-07 | Calidad / Cumplimiento |
| TEA-08 | Cobranza *(de facto ejecutada por las mismas personas que Ventas y Facturación — ver gaps)* |

---

## Capability (8)

| ID | Capacidad |
|---|---|
| CAP-01 | Inteligencia de precios de mercado |
| CAP-02 | Cotización comercial |
| CAP-03 | Coordinación logística (cliente – proveedor – transportista) |
| CAP-04 | Abastecimiento de combustible |
| CAP-05 | Facturación electrónica (CFDI) |
| CAP-06 | Gestión de cartera / cobranza |
| CAP-07 | Trazabilidad documental y cumplimiento CNE |
| CAP-08 | Gestión de calidad (SGC) |

---

## System (5)

| ID | Sistema | Uso |
|---|---|---|
| SYS-01 | Smartsheet | Registro de operación, cartera, conciliación |
| SYS-02 | SAE/ASPEL | Timbrado de CFDI |
| SYS-03 | WhatsApp | Canal de solicitud (informal, sin trazabilidad) |
| SYS-04 | Correo electrónico | Solicitud / envío de CFDI |
| SYS-05 | Banca / estado de cuenta bancario | Fuente de conciliación |

> `SYS-01`, `SYS-02` y `SYS-05` **no están integrados** entre sí — punto clave para el análisis de automatización (Capa 5).

---

## Event (8)

| ID | Evento | Rol |
|---|---|---|
| EVT-01 | Solicitud de carga recibida | Demanda |
| EVT-02 | Cotización enviada | Hito |
| EVT-03 | Pedido confirmado por cliente | Hito |
| EVT-04 | Orden de Compra emitida | Hito |
| EVT-05 | Carga ejecutada / BOL emitido | Hito |
| EVT-06 | CFDI timbrado (factura emitida) | Realización parcial de valor |
| EVT-07 | Pago recibido (cobro) | **Realización de valor** |
| EVT-08 | Factura vencida | Excepción / riesgo |

---

## CustomerJourneyStep (8 — inferidos)

Perspectiva del comprador de combustible. **Inferidos de una entrevista interna** — requieren validación con el cliente para ser confiables (la ontología marca CJS como el puente hacia la percepción externa, y aquí esa voz externa no está presente).

| ID | Momento del cliente |
|---|---|
| CJS-01 | Solicita cotización |
| CJS-02 | Recibe y evalúa cotización |
| CJS-03 | Confirma pedido |
| CJS-04 | Recibe la entrega de combustible |
| CJS-05 | Recibe el CFDI |
| CJS-06 | Recibe el estado de cuenta |
| CJS-07 | Paga |
| CJS-08 | Disputa factura / pide ayuda ante error |

---

## MetricDriver (6 candidatos)

Palancas operacionales que el equipo **puede mover** (cumplen el criterio de la ontología: "esto es lo que hacemos", no "así se calcula la métrica"). Quedan **suspendidas hasta definir la Metric** a la que apuntan.

| ID | Driver | Métrica hipotética asociada |
|---|---|---|
| MDR-01 | Puntualidad de emisión de factura (mismo día de entrega) | M?-02 |
| MDR-02 | Exactitud de datos fiscales del cliente (catálogo validado) | M?-02 |
| MDR-03 | Disciplina de seguimiento diario a cartera | M?-03 |
| MDR-04 | Existencia y aplicación de política de crédito y cobranza | M?-03 |
| MDR-05 | Puntualidad de conciliación (diaria antes de 10am) | M?-03 |
| MDR-06 | Grado de integración de sistemas (Smartsheet–SAE/ASPEL–banco) | M?-02, M?-03 |

---

## Relaciones tipificadas (estructurales, extraíbles hoy)

Solo se listan las que el texto soporta sin depender de la definición de `Metric`.

**Team —[PERFORMS]→ Activity:** según la columna "Equipo dueño" de la tabla Activity.

**Activity —[PART_OF]→ Process:** según la columna "Actividades" de la tabla Process.

**Activity —[PRECEDES]→ Activity** (cadena principal demanda→cobro):
`ACT-01 → ACT-03 → ACT-04 → ACT-05 → ACT-06 → ACT-07 → ACT-08 → ACT-09 → ACT-10 → ACT-11 → ACT-12 → ACT-13 → ACT-14`, con rama de excepción `ACT-12 → ACT-15 → ACT-16 → ACT-17`. ACT-02 alimenta a ACT-03.

**Activity —[USES_SYSTEM]→ System:** ACT-09→SYS-01; ACT-10→SYS-02; ACT-13→SYS-01+SYS-05; ACT-14→SYS-01; ACT-01→SYS-03/SYS-04; ACT-11→SYS-04.

**Activity —[INVOLVES_EVENT]→ Event:** ACT-01→EVT-01; ACT-03→EVT-02; ACT-04→EVT-03; ACT-06→EVT-04; ACT-08→EVT-05; ACT-10→EVT-06; ACT-14→EVT-07; ACT-15↔EVT-08.

**Activity —[SUPPORTS]→ Capability** y **Team —[OWNS]→ Process/Capability:** derivables directamente de las tablas anteriores.

**Pendientes (bloqueadas por Metric):** `Activity —[AFFECTS]→ Metric`, `Activity —[AFFECTS]→ MetricDriver`, `MetricDriver —[DRIVES]→ Metric`, `Metric —[HAS_DRIVER]→ MetricDriver`, `Process —[CONTRIBUTES_TO]→ Metric`, `Activity —[TOUCHES]→ CustomerJourneyStep` (esta última extraíble pero débil sin validación del journey).

---

## Información NO cubierta por la ontología

Tres categorías. La distinción importa: no todo lo "faltante" es un hueco del modelo — parte es intencional (se captura como atributo o analítica, no como nodo).

### A. Huecos reales del modelo (entidades que la ontología no representa)

1. **Proveedores y transportistas como entidades.** Pemex / Valero / Repsol (fuentes de precio), el proveedor de combustible, la empresa logística/transportista. **No existe nodo `Supplier` / `LogisticsPartner`.** Para una comercializadora de combustibles esto es central: la dependencia de proveedor y transporte es un eje de riesgo que hoy el grafo no puede modelar. → **Candidato fuerte a extensión de ontología (v3).**
2. **Productos.** Diésel terrestre, diésel marino, gasolina, gasolina premium. No hay nodo `Product`. Relevante si el valor/riesgo varía por producto.
3. **Entidad regulatoria y permisos.** CNE, permiso de comercialización, reporte volumétrico, cambio CRE→CNE. No hay nodo `Regulator` / `Permit` / `Constraint`. El texto lo señala como riesgo doble (financiero + regulatorio) — hoy inexpresable en el grafo.
4. **Segmentos de cliente.** No hay nodo `Customer` / `Segment` (existe `CustomerJourneyStep`, pero no la entidad cliente ni su segmentación).
5. **Artefactos operativos vs. Document/Source.** BOL, CFDI, Orden de Compra, estado de cuenta **fluyen por el proceso** como artefactos; `Document/Source` en la ontología es para **procedencia del conocimiento del grafo** (entrevista, SOP), no para artefactos de negocio. Ambigüedad a resolver.

### B. Se captura como atributo o analítica, NO como nodo (no es hueco)

6. **KPIs internos:** DSO, % cartera vencida, flujo de caja, margen por operación, indicadores de calidad. No son `Metric` (valor de cliente). Viven como contexto/atributo, no como nodos.
7. **Dolor / cuello de botella:** "siempre se atora aquí", el bottleneck de Facturación y Cobranza. Es `B(A)` (Capa 3/5), atributo computado — no nodo.
8. **Reglas temporales / SLA:** factura el mismo día, contacto 24h/3d, escalamiento 7d, conciliación antes de 10am, DSO≤15, cartera<5%. `PRECEDES` da orden, no propiedades de tiempo/umbral. Van como propiedades de actividad/proceso.
9. **Madurez / autoevaluación:** 5/10 actual, ruta a 6/10. Es un score de diagnóstico, no un nodo.
10. **Concentración de conocimiento / mezcla de roles:** "las mismas personas ejecutan Ventas, Facturación y Cobranza"; conocimiento tácito; rotación sin traspaso. Hay `Team`, no persona individual ni el fenómeno de solapamiento. Se detecta como analítica (H-01), no como estructura.

### C. Diagnóstico y prescripción (fuera del alcance descriptivo del grafo)

11. **Causas raíz / factores sistémicos** (Pregunta 5): ausencia de procedimientos formalizados, canales informales sin trazabilidad, falta de catálogo fiscal, ausencia de política de crédito, rotación, carga regulatoria CRE→CNE. No hay nodo "deficiencia" o "factor de riesgo" — es diagnóstico narrativo.
12. **Estado ideal / meta y brecha** (Pregunta 6): la ontología modela el estado **actual**; no hay nodo de estado objetivo ni de gap actual-vs-ideal.
13. **Recomendaciones / intervenciones** (las 3 acciones inmediatas): sin nodo de recomendación.
14. **Condiciones comerciales:** prepago en la OC, límites de crédito, plazos por tipo de cliente. Sin nodo/propiedad dedicada.

---

## No incluido a propósito (siguientes pasos)

Respetando la progresión por capas, este documento **solo** cubre extracción de nodos + gaps. **No** se hizo aún:

- Puntuación P/C/F/R/V(A) (Capa 3) — requiere definir métricas de valor primero.
- Definición de las métricas de valor del cliente (ruta cliente / JTBD) — **bloqueante para todo lo demás**.
- Construcción de Value Streams (demanda→valor).
- Decisión sobre extender la ontología v3 (Supplier / Product / Regulator).

**Recomendación de secuencia:** resolver primero la ruta cliente (métricas de valor de Eneroil), luego decidir la extensión de ontología, y solo después puntuar.
