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

# Llenado generado (brechas)

**Este archivo es un artefacto de ingesta.** El sistema lo lee **solo** para materializar el grafo, así que contiene **únicamente nodos y relaciones** con sus flags — no triage, ni razonamiento, ni preguntas de refinamiento. El método (barrido, lecturas en competencia, `collapse_predictor`, criterios) vive en `Protocolo_Llenado_Grafo_v1.md`, no aquí.

Todo lo anterior es extracción directa (`generated=false`). De aquí en adelante son elementos **generados** (`generated=true`) con: `generation_basis`, `confidence`, `corroboration`, `informant_distance`, `evidence_pointer`.

## Paso 1 — cierre estructural mecánico

*`generated=true` · `informant_distance=1` en todo el paso. 42 relaciones.*

### SUPPORTS (Activity → Capability)

| Activity | Capability | conf | basis |
|---|---|---|---|
| ACT-01, ACT-03, ACT-04 | CAP-02 Cotización comercial | 1.0 | evidence |
| ACT-02 | CAP-01 Inteligencia de precios | 1.0 | evidence |
| ACT-05, ACT-07 | CAP-03 Coordinación logística | 1.0 | evidence |
| ACT-06, ACT-22 | CAP-04 Abastecimiento | 1.0 | evidence |
| ACT-08 | CAP-04 Abastecimiento | 0.5 | evidence |
| ACT-09 | CAP-07 Trazabilidad y cumplimiento | 0.75 | evidence |
| ACT-10, ACT-11 | CAP-05 Facturación electrónica | 1.0 | evidence |
| ACT-12–ACT-17 | CAP-06 Gestión de cartera | 1.0 | evidence |
| ACT-18, ACT-23 | CAP-07 Trazabilidad y cumplimiento | 1.0 | evidence |
| ACT-19, ACT-20, ACT-21 | CAP-08 Gestión de calidad | 1.0 | evidence |

### OWNS (Team → Process)

| Team | Process | conf |
|---|---|---|
| TEA-02 | PRO-01 | 1.0 |
| TEA-03 | PRO-02 | 1.0 |
| TEA-04 | PRO-03 | 1.0 |
| TEA-05 | PRO-04 | 0.75 |
| TEA-06 | PRO-05 | 1.0 |
| TEA-08 | PRO-06 | 1.0 |
| TEA-07 | PRO-07, PRO-08, PRO-09 | 1.0 |

### OWNS (Team → Capability)

TEA-02→CAP-01 · TEA-03→CAP-02 · TEA-04→CAP-03 · TEA-05→CAP-04 · TEA-06→CAP-05 · TEA-08→CAP-06 · TEA-07→CAP-07, CAP-08 — todos `conf=1.0`.

### USES_SYSTEM (cierres omitidos)

| Activity | System | conf | basis |
|---|---|---|---|
| ACT-16 | SYS-01 Smartsheet | 0.75 | logical |
| ACT-16 | SYS-04 Correo | 0.75 | logical |

## Paso 2 — compleción de flujo

*`informant_distance=1` en todo el paso. Nuevos: 2 Activity, 1 Event, 4 PRECEDES, 1 INVOLVES_EVENT.*

### Activity (nuevas)

| ID | Activity | basis | conf | corrob | pointer |
|---|---|---|---|---|---|
| ACT-24 | Ejecución del prepago al proveedor | logical | 0.75 | 2 | ACT-06 "OC al proveedor con prepago" + la carga (ACT-08) ocurre ⇒ el proveedor no libera sin el pago |
| ACT-25 | Transporte y entrega del producto al destino | logical | 0.75 | 2 | cliente indica "destino" (P3) + se factura "el mismo día de la entrega" (P6) ⇒ la entrega ocurre entre carga y facturación |

### Event (nuevo)

| ID | Event | rol | basis | conf | corrob | pointer |
|---|---|---|---|---|---|---|
| EVT-09 | Entrega confirmada en destino | realización de valor (física) | evidence | 0.75 | 2 | "de que la carga fue entregada" (P2); "el mismo día de la entrega" (P6) |

### PRECEDES (nuevas)

| Desde | Hacia | basis | conf |
|---|---|---|---|
| ACT-06 | ACT-24 | logical | 0.75 |
| ACT-24 | ACT-08 | logical | 0.75 |
| ACT-08 | ACT-25 | logical | 0.75 |
| ACT-25 | ACT-10 | logical | 0.75 |

### INVOLVES_EVENT (nueva)

| Activity | Event | basis | conf |
|---|---|---|---|
| ACT-25 | EVT-09 | evidence | 0.75 |

## Paso 3 — métricas de valor del cliente (abducción)

*Capa de métricas: `basis=abduction`, `informant_distance=3`, `confidence ≤ 0.5` (techo, no gate) — las conjeturas más blandas del grafo, todas visibles. Eventos del eje: `basis=evidence`, `dist=1`, confianza normal.*

### Metric (nuevas — abducción)

| ID | Metric | client-facing | divergence | conf | drivers | pointer |
|---|---|---|---|---|---|---|
| MET-01 | Confiabilidad de entrega (producto / volumen / destino / fecha) | sí | **coverage (nivel-driver)** — sin driver, pero con actividades de fulfillment (ACT-05, ACT-25, EVT-09) | 0.5 | — | emergida de lógica de negocio, no de un driver: el comprador de combustible valora recibir lo correcto en destino y fecha. La cadena de entrega existe pero **ningún proxy la vigila** — invisibilidad, no incapacidad. Candidata a `AFFECTS` desde ACT-05 / ACT-25 en Paso 4 |
| MET-02 | CFDI correcto y a tiempo | sí | — | 0.5 | MDR-01, MDR-02, MDR-06 | MDR-01 (factura mismo día) + MDR-02 (datos fiscales) ⇒ creen que el valor está en un CFDI correcto y oportuno; el cliente lo necesita para su contabilidad/IVA |
| MET-03 | Transparencia / exactitud del estado de cuenta | sí | **motive** — sus drivers sirven al terminal de cobro, no a esta métrica | 0.5 | MDR-06 | "clientes que… no reciben sus estados de cuenta a tiempo" (P2/P9) |

### DRIVES (MetricDriver → Metric — abducción, conf 0.5)

*(par `HAS_DRIVER` inverso implícito)*

| MetricDriver | → Metric |
|---|---|
| MDR-01 | MET-02 |
| MDR-02 | MET-02 |
| MDR-06 | MET-02, MET-03 |

Sin `DRIVES`: MDR-03, MDR-04, MDR-05 (divergencia `motive` — sirven al terminal de cobro, no a un `Metric`).

### Eje de valor (eventos)

| Evento | rol | basis | conf |
|---|---|---|---|
| EVT-01 | demanda (frontera) | extraído | — |
| EVT-09 | realización de valor — el cliente recibe | Paso 2 | 0.75 |
| EVT-10 | **terminal — cobro conciliado (valor asegurado)** | evidence | 0.75 |

EVT-07 "pago recibido" → **rol: milestone** (pago acreditado, no conciliado); ya no es terminal.

### INVOLVES_EVENT (nueva)

| Activity | Event | basis | conf |
|---|---|---|---|
| ACT-13 | EVT-10 | evidence | 0.75 |

## Paso 4 — aristas operación → valor

### AFFECTS (Activity → MetricDriver) — `basis=evidence`, `dist=1`

| Activity | → MetricDriver | conf | nota |
|---|---|---|---|
| ACT-10 | MDR-01 (puntualidad de factura) | 0.75 | el timbrado es lo que fija la puntualidad |
| ACT-13 | MDR-05 (puntualidad de conciliación) | 0.75 | la conciliación es lo que el driver mide |
| ACT-12 | MDR-03 (disciplina de seguimiento) | 0.75 | el seguimiento al pago mueve la disciplina de cartera |

**Drivers sin actividad** (estado deseado, no palanca actual — gaps que la organización ya identificó): **MDR-02** (catálogo fiscal validado), **MDR-04** (política de crédito), **MDR-06** (integración de sistemas). Sin `AFFECTS`; insumo de diagnóstico, no hueco a forzar.

### AFFECTS (Activity → Metric) — directa, solo sin driver intermedio · `basis=abduction`, `dist=2`, conf ≤ 0.5

| Activity | → Metric | conf | nota |
|---|---|---|---|
| ACT-05 | MET-01 | 0.5 | confirmar disponibilidad+logística habilita entrega confiable |
| ACT-25 | MET-01 | 0.5 | el acto de entrega mismo |
| ACT-16 | MET-03 | 0.5 | generar/enviar el estado de cuenta es lo que el cliente experimenta |

### CONTRIBUTES_TO (Process → Metric) — `basis=abduction`, `dist=2`, conf ≤ 0.5

| Process | → Metric | conf |
|---|---|---|
| PRO-05 Facturación | MET-02 | 0.5 |
| PRO-06 Cobranza | MET-03 | 0.5 |
| PRO-03 Planeación | MET-01 | 0.5 |

## Paso 5 — enlace de journey

### CustomerJourneyStep (refinados) — `dist=3`

| ID | Momento | basis | conf | valor |
|---|---|---|---|---|
| CJS-01 | Solicita cotización | evidence | 0.75 | — |
| CJS-02 | Recibe y evalúa cotización | abduction | 0.5 | — |
| CJS-03 | Confirma pedido | evidence | 0.75 | — |
| CJS-04 | Recibe la entrega de combustible | evidence | 0.75 | **MET-01** |
| CJS-05 | Recibe el CFDI | evidence | 0.75 | **MET-02** |
| CJS-06 | Recibe el estado de cuenta | evidence | 0.75 | **MET-03** |
| CJS-07 | Paga | evidence | 0.75 | — |
| CJS-08 | Disputa factura / pide ayuda | evidence | 0.75 | — |

### TOUCHES (Activity → CJS) — `dist=2`, `basis=evidence`, conf 0.75

| Activity | → CJS |
|---|---|
| ACT-01 | CJS-01 |
| ACT-03 | CJS-02 |
| ACT-04 | CJS-03 |
| ACT-25 | CJS-04 |
| ACT-11 | CJS-05 |
| ACT-16 | CJS-06 |
| ACT-19 | CJS-08 |

**CJS-07 (Paga)** sin `TOUCHES` interno fuerte: es acción del cliente hacia el banco; su lado interno es asegurar el efectivo (EVT-10), no un artefacto que la operación le entregue. Vacío esperado, no hueco.

## Paso 6 — dimensiones de evaluación (P, C, F, R)

*Celdas como `valor·conf`. **P** = prior semántico Fase-1 (`dist=1`); la proximidad topológica la computa el sistema (Fase-2) y su divergencia con P es señal de validación cruzada. **C, R** = `basis=evidence`, `dist=2`. **F** = requiere datos de volumen; solo gruesa por universalidad, si no `null`. `V(A)` lo compone el sistema, no este inventario.*

| Activity | P (prior) | C | R | F |
|---|---|---|---|---|
| ACT-01 Recepción solicitud | 0.25·0.75 | 0.25·0.5 | 0.25·0.5 | 1.0·0.5 |
| ACT-03 Cotización | 0.25·0.75 | 0.5·0.5 | 0.5·0.5 | 1.0·0.5 |
| ACT-05 Disponibilidad | 0.5·0.75 | 0.5·0.5 | 0.5·0.5 | null |
| ACT-10 Timbrado CFDI | 0.75·0.75 | 1.0·0.75 | 1.0·0.75 | 1.0·0.5 |
| ACT-11 Envío CFDI | 0.75·0.5 | 0.75·0.5 | 0.5·0.5 | 1.0·0.5 |
| ACT-12 Seguimiento pago | 0.75·0.5 | 0.75·0.75 | 0.75·0.75 | null |
| ACT-13 Conciliación | 1.0·0.75 | 0.75·0.75 | 0.75·0.75 | null |
| ACT-15 Contacto vencida | 0.75·0.5 | 0.5·0.5 | 0.5·0.5 | null |
| ACT-16 Estado de cuenta | 0.5·0.5 | 0.5·0.5 | 0.5·0.5 | null |
| ACT-17 Escalamiento | 1.0·0.5 | 0.5·0.5 | 0.75·0.5 | null |
| ACT-25 Transporte/entrega | 0.75·0.75 | **null** | **null** | null |

## Paso 7 — feeders inter-área y aristas de insumo

### Nodos generados (feeders) · `basis=logical`, `dist=1`, `corrob=2`

| ID | label | conf | evidence_pointer | flag |
|---|---|---|---|---|
| ACT-26 | Determinación del costo de transporte para la cotización | 0.5 | cotización entrega precio a un "destino" (P3) ⇒ componente de flete previo | contested_external |
| ACT-27 | Obtención del estado de cuenta bancario | 0.5 | "conciliar contra el estado de cuenta bancario" (P3) ⇒ obtenerlo primero | contested_external |
| ACT-28 | Consulta de disponibilidad de producto al proveedor | 0.5 | "confirma disponibilidad de producto" (P3) ⇒ consulta previa | contested_external |
| ACT-29 | Consulta de disponibilidad logística al transportista | 0.5 | "confirma disponibilidad de… logística" (P3) ⇒ consulta previa | contested_external |
| ACT-30 | Autorización de liberación de fondos para prepago | 0.5 | "OC con prepago" (P3) vía ACT-24 ⇒ fondos liberados | tier_bajo (ancla ACT-24 generado) |
| ACT-31 | Identificación de facturas vencidas | 0.5 | "contacto por vencida" (ACT-15) exige saber que venció | contested_external |

### Relaciones generadas — PERFORMS (Team → Activity)

| Team | Activity | conf |
|---|---|---|
| Cobranza (TEA-08) | ACT-27 | 0.5 |
| Planeación (TEA-04) | ACT-28 | 0.75 |
| Planeación (TEA-04) | ACT-29 | 0.75 |
| Dirección (TEA-01) | ACT-30 | 0.5 |
| Cobranza (TEA-08) | ACT-31 | 0.5 |

*(ACT-26 sin PERFORMS — área no atribuible.)*

### Relaciones generadas — PART_OF (Activity → Process)

| Activity | Process | conf |
|---|---|---|
| ACT-27 | PRO-06 | 0.75 |
| ACT-28 | PRO-03 | 0.75 |
| ACT-29 | PRO-03 | 0.75 |
| ACT-31 | PRO-06 | 0.75 |

*(ACT-26, ACT-30 sin PART_OF.)*

### Relaciones generadas — PRECEDES (aristas de insumo)

| Desde | Hacia | basis | conf |
|---|---|---|---|
| ACT-02 | ACT-03 | evidence | 0.75 |
| ACT-22 | ACT-06 | evidence | 0.75 |
| ACT-06 | ACT-09 | logical | 0.5 |
| ACT-09 | ACT-13 | evidence | 1.0 |
| ACT-10 | ACT-13 | evidence | 1.0 |
| ACT-14 | ACT-16 | logical | 0.75 |
| ACT-11 | ACT-18 | evidence | 0.75 |
| ACT-06 | ACT-18 | evidence | 0.75 |
| ACT-08 | ACT-18 | evidence | 0.75 |
| ACT-18 | ACT-20 | logical | 0.5 |
| ACT-18 | ACT-23 | logical | 0.5 |
| ACT-26 | ACT-03 | logical | 0.5 |
| ACT-27 | ACT-13 | logical | 0.5 |
| ACT-28 | ACT-05 | logical | 0.5 |
| ACT-29 | ACT-05 | logical | 0.5 |
| ACT-30 | ACT-24 | logical | 0.5 |
| ACT-31 | ACT-15 | logical | 0.5 |

---

## Paso 8 — evaluación de actividades generadas

*Dimensiones ≤ conf del nodo. `contested_external` / `tier_bajo`: P es prior real; C/R/F completados en **modo simulación** (`basis=simulated`, no evidencia) para ejercitar el sistema — score entero `void_on_collapse`. Celdas `valor·conf`.*

| Activity | P (prior) | C | R | F | flag |
|---|---|---|---|---|---|
| ACT-24 Prepago | 0.5·0.75 | 0.75·0.75 | 0.75·0.75 | 1.0·0.5 | — |
| ACT-26 Costo transporte | 0.25·0.5 | 0.5·0.5 | 0.5·0.5 | 1.0·0.5 | void_on_collapse |
| ACT-27 Estado de cuenta | 0.75·0.5 | 0.75·0.5 | 0.75·0.5 | 1.0·0.5 | void_on_collapse |
| ACT-28 Disponibilidad producto | 0.5·0.5 | 0.5·0.5 | 0.75·0.5 | 1.0·0.5 | void_on_collapse |
| ACT-29 Disponibilidad logística | 0.5·0.5 | 0.5·0.5 | 0.5·0.5 | 1.0·0.5 | void_on_collapse |
| ACT-30 Autorización fondos | 0.5·0.5 | 0.5·0.5 | 0.5·0.5 | 0.75·0.5 | tier_bajo |
| ACT-31 Identificación vencidas | 0.75·0.5 | 0.75·0.5 | 0.75·0.5 | 0.75·0.5 | void_on_collapse |

---

## Handoff — fuera de este proceso de llenado

El llenado (Pasos 1–6) está completo. Lo que sigue **no** es llenado; lo computan capas independientes sobre el grafo ya poblado:

- **Sistema (Python / NetworkX):** `V(A)`, proximidad Fase-2, leverage, coherencia estructural, `refinement_priority`. Nunca los escribe la extracción.
- **Capa de síntomas / ruta cliente (JTBD):** validación de las métricas abducidas (MET-01–03) y sus divergencias contra comportamiento real del cliente.
- **Decisión de ontología v3:** Supplier / Product / Regulator — fuera de alcance (ontología fija).

Todo lo generado lleva `generated=true` + flags; lo extraído directo queda `generated=false`.
