# Auditoría de coherencia — protocolo v0.2

## Encabezado

- **Grado de coherencia:** N1=0 N2=0 N3=0 N4=0; evidencia=0 abducción=0; compresión=0.00 (31/0) → N1=3 N2=11 N3=0 N4=17; evidencia=0 abducción=16; compresión=1.94 (31/16)
- **Iteraciones:** 2
- **Ciclo convergió:** no

- **Top situaciones (Sección 1):** 1.1 Actividades sin intención (reparadas) (31); 1.7 Intención sin beneficiario (13); 1.5 Persigue sin llegar (11)
- **Top situaciones (Sección 2):** ninguna con casos
- **Top situaciones (Sección 3):** 3.3 Topología de flujo (ramas y ciclos) (10); 3.4 Candidatos a variante (9); 3.1 Alcanzabilidad de valor (7)

## Sección 1 — Salud de las intenciones

#### 1.1 Actividades sin intención (reparadas)

**Situación.** Actividades que no tenían intención propia ni heredada y recibieron una en esta corrida.

**Por qué importa.** Sin intención no hay *para qué* legible; es defecto del modelo (I1), no de la organización.

**Explicación.** Se detectó por C1. R1 asignó intención al proceso (parsimonia) o a la actividad huérfana. No significa que el propósito sea el real — es abducción hasta validar con evidencia.

**Casos.**

| Actividad | Proceso | Intención asignada | Origen | Base | Evidencia |
| --- | --- | --- | --- | --- | --- |
| Obtención y publicación diaria de precios de referencia (Pemex, Valero, Repsol) (ACT-02) | Monitoreo y Precios (Obtención y Envío de Precios) (PRO-01) | Cumplir propósito de Monitoreo y Precios (Obtención y Envío de Precios) (INT-01) | heredada | abduction | R1 abduction from Process Monitoreo y Precios (Obtención y Envío de Precios) (PRO-01) |
| Recepción de solicitud del cliente (WhatsApp / correo / llamada) (ACT-01) | Cotización al Cliente (PRO-02) | Cumplir propósito de Cotización al Cliente (INT-02) | heredada | abduction | R1 abduction from Process Cotización al Cliente (PRO-02) |
| Elaboración y envío de cotización (ACT-03) | Cotización al Cliente (PRO-02) | Cumplir propósito de Cotización al Cliente (INT-02) | heredada | abduction | R1 abduction from Process Cotización al Cliente (PRO-02) |
| Confirmación del pedido por el cliente (ACT-04) | Cotización al Cliente (PRO-02) | Cumplir propósito de Cotización al Cliente (INT-02) | heredada | abduction | R1 abduction from Process Cotización al Cliente (PRO-02) |
| Confirmación de disponibilidad de producto (ACT-05) | Generación y seguimiento de pedidos (PRO-03) | Cumplir propósito de Generación y seguimiento de pedidos (INT-03) | heredada | abduction | R1 abduction from Process Generación y seguimiento de pedidos (PRO-03) |
| Emisión de Orden de Compra al proveedor (con prepago) (ACT-06) | Generación y seguimiento de pedidos (PRO-03) | Cumplir propósito de Generación y seguimiento de pedidos (INT-03) | heredada | abduction | R1 abduction from Process Generación y seguimiento de pedidos (PRO-03) |
| Envío del pedido/folio a la empresa de logística (ACT-07) | Generación y seguimiento de pedidos (PRO-03) | Cumplir propósito de Generación y seguimiento de pedidos (INT-03) | heredada | abduction | R1 abduction from Process Generación y seguimiento de pedidos (PRO-03) |
| Consulta informal de disponibilidad a la empresa de logística (ACT-28) | Generación y seguimiento de pedidos (PRO-03) | Cumplir propósito de Generación y seguimiento de pedidos (INT-03) | heredada | abduction | R1 abduction from Process Generación y seguimiento de pedidos (PRO-03) |
| Ejecución de la carga y emisión del BOL (ACT-08) | Compra y Venta de Combustible (PRO-04) | Cumplir propósito de Compra y Venta de Combustible (INT-04) | heredada | abduction | R1 abduction from Process Compra y Venta de Combustible (PRO-04) |
| Registro de la operación en Smartsheet (ACT-09) | Compra y Venta de Combustible (PRO-04) | Cumplir propósito de Compra y Venta de Combustible (INT-04) | heredada | abduction | R1 abduction from Process Compra y Venta de Combustible (PRO-04) |
| Timbrado del CFDI en SAE/ASPEL (ACT-10) | Facturación (PRO-05) | Cumplir propósito de Facturación (INT-05) | heredada | abduction | R1 abduction from Process Facturación (PRO-05) |
| Envío del CFDI al cliente (ACT-11) | Facturación (PRO-05) | Cumplir propósito de Facturación (INT-05) | heredada | abduction | R1 abduction from Process Facturación (PRO-05) |
| Seguimiento al pago (ACT-12) | Cobranza (PRO-06) | Cumplir propósito de Cobranza (INT-06) | heredada | abduction | R1 abduction from Process Cobranza (PRO-06) |
| Conciliación factura – estado de cuenta bancario – Smartsheet (ACT-13) | Cobranza (PRO-06) | Cumplir propósito de Cobranza (INT-06) | heredada | abduction | R1 abduction from Process Cobranza (PRO-06) |
| Registro del pago / saldo en Smartsheet (ACT-14) | Cobranza (PRO-06) | Cumplir propósito de Cobranza (INT-06) | heredada | abduction | R1 abduction from Process Cobranza (PRO-06) |
| Contacto al cliente por factura vencida (ACT-15) | Cobranza (PRO-06) | Cumplir propósito de Cobranza (INT-06) | heredada | abduction | R1 abduction from Process Cobranza (PRO-06) |
| Generación y envío del estado de cuenta del cliente (ACT-16) | Cobranza (PRO-06) | Cumplir propósito de Cobranza (INT-06) | heredada | abduction | R1 abduction from Process Cobranza (PRO-06) |
| Escalamiento a Dirección por cobro vencido (ACT-17) | Cobranza (PRO-06) | Cumplir propósito de Cobranza (INT-06) | heredada | abduction | R1 abduction from Process Cobranza (PRO-06) |
| Obtención del estado de cuenta bancario (ACT-27) | Cobranza (PRO-06) | Cumplir propósito de Cobranza (INT-06) | heredada | abduction | R1 abduction from Process Cobranza (PRO-06) |
| Identificación de facturas vencidas (ACT-31) | Cobranza (PRO-06) | Cumplir propósito de Cobranza (INT-06) | heredada | abduction | R1 abduction from Process Cobranza (PRO-06) |
| Integración del expediente legal por operación (trazabilidad documental) (ACT-18) | Control / Trazabilidad Documental (PRO-07) | Cumplir propósito de Control / Trazabilidad Documental (INT-07) | heredada | abduction | R1 abduction from Process Control / Trazabilidad Documental (PRO-07) |
| Gestión de quejas y no conformidades (ACT-19) | Gestión de Quejas y No Conformidades (PRO-08) | Cumplir propósito de Gestión de Quejas y No Conformidades (INT-08) | heredada | abduction | R1 abduction from Process Gestión de Quejas y No Conformidades (PRO-08) |
| Auditorías internas (ACT-20) | Auditorías internas y a proveedores (PRO-09) | Cumplir propósito de Auditorías internas y a proveedores (INT-09) | heredada | abduction | R1 abduction from Process Auditorías internas y a proveedores (PRO-09) |
| Auditorías a proveedores (ACT-21) | Auditorías internas y a proveedores (PRO-09) | Cumplir propósito de Auditorías internas y a proveedores (INT-09) | heredada | abduction | R1 abduction from Process Auditorías internas y a proveedores (PRO-09) |
| Aprobación de proveedores (ACT-22) | — (sin proceso) | Cumplir Aprobación de proveedores (INT-10) | nueva | abduction | R1 abduction from Activity Aprobación de proveedores (ACT-22) — no Process Intent |
| Gestión de relación regulatoria y reporte volumétrico (CNE) (ACT-23) | — (sin proceso) | Cumplir Gestión de relación regulatoria y reporte volumétrico (CNE) (INT-11) | nueva | abduction | R1 abduction from Activity Gestión de relación regulatoria y reporte volumétrico (CNE) (ACT-23) — no Process Intent |
| Ejecución del prepago al proveedor (ACT-24) | — (sin proceso) | Cumplir Ejecución del prepago al proveedor (INT-12) | nueva | abduction | R1 abduction from Activity Ejecución del prepago al proveedor (ACT-24) — no Process Intent |
| Monitoreo del estado de liberación de crédito (ACT-32) | — (sin proceso) | Cumplir Monitoreo del estado de liberación de crédito (INT-13) | nueva | abduction | R1 abduction from Activity Monitoreo del estado de liberación de crédito (ACT-32) — no Process Intent |
| Recepción del BOL de la empresa de logística (ACT-33) | — (sin proceso) | Cumplir Recepción del BOL de la empresa de logística (INT-14) | nueva | abduction | R1 abduction from Activity Recepción del BOL de la empresa de logística (ACT-33) — no Process Intent |
| Determinación del costo de transporte para la cotización (ACT-26) | — (sin proceso) | Cumplir Determinación del costo de transporte para la cotización (INT-15) | nueva | abduction | R1 abduction from Activity Determinación del costo de transporte para la cotización (ACT-26) — no Process Intent |
| Autorización de liberación de fondos para prepago (ACT-30) | — (sin proceso) | Cumplir Autorización de liberación de fondos para prepago (INT-16) | nueva | abduction | R1 abduction from Activity Autorización de liberación de fondos para prepago (ACT-30) — no Process Intent |

#### 1.5 Persigue sin llegar

**Situación.** La intención apunta a una métrica, pero no hay ruta de efecto (`AFFECTS`/driver) hasta ella.

**Por qué importa.** O es hueco de datos (falta arista) o esfuerzo que no entrega — C4 no decide cuál.

**Explicación.** Detectado por C4: Intent.SERVES → M sin efecto de la actividad a M. N3 en la escalera.

**Casos.**

| Actividad | Proceso | Intención | Métrica a la que sirve | Qué ruta falta |
| --- | --- | --- | --- | --- |
| Emisión de Orden de Compra al proveedor (con prepago) (ACT-06) | Generación y seguimiento de pedidos (PRO-03) | Cumplir propósito de Generación y seguimiento de pedidos (INT-03) | Confiabilidad de entrega (producto / volumen / destino / fecha) (MET-01) | AFFECTS o AFFECTS→MetricDriver→DRIVES hacia la métrica |
| Envío del pedido/folio a la empresa de logística (ACT-07) | Generación y seguimiento de pedidos (PRO-03) | Cumplir propósito de Generación y seguimiento de pedidos (INT-03) | Confiabilidad de entrega (producto / volumen / destino / fecha) (MET-01) | AFFECTS o AFFECTS→MetricDriver→DRIVES hacia la métrica |
| Envío del CFDI al cliente (ACT-11) | Facturación (PRO-05) | Cumplir propósito de Facturación (INT-05) | CFDI correcto y a tiempo (MET-02) | AFFECTS o AFFECTS→MetricDriver→DRIVES hacia la métrica |
| Seguimiento al pago (ACT-12) | Cobranza (PRO-06) | Cumplir propósito de Cobranza (INT-06) | Transparencia / exactitud del estado de cuenta (MET-03) | AFFECTS o AFFECTS→MetricDriver→DRIVES hacia la métrica |
| Conciliación factura – estado de cuenta bancario – Smartsheet (ACT-13) | Cobranza (PRO-06) | Cumplir propósito de Cobranza (INT-06) | Transparencia / exactitud del estado de cuenta (MET-03) | AFFECTS o AFFECTS→MetricDriver→DRIVES hacia la métrica |
| Registro del pago / saldo en Smartsheet (ACT-14) | Cobranza (PRO-06) | Cumplir propósito de Cobranza (INT-06) | Transparencia / exactitud del estado de cuenta (MET-03) | AFFECTS o AFFECTS→MetricDriver→DRIVES hacia la métrica |
| Contacto al cliente por factura vencida (ACT-15) | Cobranza (PRO-06) | Cumplir propósito de Cobranza (INT-06) | Transparencia / exactitud del estado de cuenta (MET-03) | AFFECTS o AFFECTS→MetricDriver→DRIVES hacia la métrica |
| Escalamiento a Dirección por cobro vencido (ACT-17) | Cobranza (PRO-06) | Cumplir propósito de Cobranza (INT-06) | Transparencia / exactitud del estado de cuenta (MET-03) | AFFECTS o AFFECTS→MetricDriver→DRIVES hacia la métrica |
| Obtención del estado de cuenta bancario (ACT-27) | Cobranza (PRO-06) | Cumplir propósito de Cobranza (INT-06) | Transparencia / exactitud del estado de cuenta (MET-03) | AFFECTS o AFFECTS→MetricDriver→DRIVES hacia la métrica |
| Consulta informal de disponibilidad a la empresa de logística (ACT-28) | Generación y seguimiento de pedidos (PRO-03) | Cumplir propósito de Generación y seguimiento de pedidos (INT-03) | Confiabilidad de entrega (producto / volumen / destino / fecha) (MET-01) | AFFECTS o AFFECTS→MetricDriver→DRIVES hacia la métrica |
| Identificación de facturas vencidas (ACT-31) | Cobranza (PRO-06) | Cumplir propósito de Cobranza (INT-06) | Transparencia / exactitud del estado de cuenta (MET-03) | AFFECTS o AFFECTS→MetricDriver→DRIVES hacia la métrica |

#### 1.7 Intención sin beneficiario

**Situación.** Existe el *para qué*, pero no el *para quién* (`SERVES` ausente).

**Por qué importa.** Señal de coherencia (ontología): propósito cuyo destinatario no está identificado.

**Explicación.** C1 sobre Intent sin SERVES. R2 solo enlaza cuando hay CONTRIBUTES_TO o efecto claro; si no, queda como hallazgo — no se inventa un beneficiario.

**Casos.**

| Intención | Actividades y procesos que la persiguen |
| --- | --- |
| Cumplir propósito de Monitoreo y Precios (Obtención y Envío de Precios) (INT-01) | Monitoreo y Precios (Obtención y Envío de Precios) (PRO-01) |
| Cumplir propósito de Cotización al Cliente (INT-02) | Cotización al Cliente (PRO-02) |
| Cumplir propósito de Compra y Venta de Combustible (INT-04) | Compra y Venta de Combustible (PRO-04) |
| Cumplir propósito de Control / Trazabilidad Documental (INT-07) | Control / Trazabilidad Documental (PRO-07) |
| Cumplir propósito de Gestión de Quejas y No Conformidades (INT-08) | Gestión de Quejas y No Conformidades (PRO-08) |
| Cumplir propósito de Auditorías internas y a proveedores (INT-09) | Auditorías internas y a proveedores (PRO-09) |
| Cumplir Aprobación de proveedores (INT-10) | Aprobación de proveedores (ACT-22) |
| Cumplir Gestión de relación regulatoria y reporte volumétrico (CNE) (INT-11) | Gestión de relación regulatoria y reporte volumétrico (CNE) (ACT-23) |
| Cumplir Ejecución del prepago al proveedor (INT-12) | Ejecución del prepago al proveedor (ACT-24) |
| Cumplir Monitoreo del estado de liberación de crédito (INT-13) | Monitoreo del estado de liberación de crédito (ACT-32) |
| Cumplir Recepción del BOL de la empresa de logística (INT-14) | Recepción del BOL de la empresa de logística (ACT-33) |
| Cumplir Determinación del costo de transporte para la cotización (INT-15) | Determinación del costo de transporte para la cotización (ACT-26) |
| Cumplir Autorización de liberación de fondos para prepago (INT-16) | Autorización de liberación de fondos para prepago (ACT-30) |

#### 1.9 Dispersión funcional

**Situación.** Perfil de intenciones por proceso/equipo: cliente vs interna vs sin beneficiario.

**Por qué importa.** Define la función de cada parte de la organización y dónde hay conflicto o vacío.

**Explicación.** Agregado por C11. Es diagnóstico, no defecto por sí solo.

**Casos.**

| Equipo o Proceso | Intenciones que persigue | Proporción al cliente / interna / sin beneficiario / en conflicto |
| --- | --- | --- |
| Monitoreo y Precios (Obtención y Envío de Precios) (PRO-01) | — (ver descripción agregada) | Intents=1 client=0 internal=0 no_beneficiary=1 conflict_pairs=0 activities=1 |
| Cotización al Cliente (PRO-02) | — (ver descripción agregada) | Intents=1 client=0 internal=0 no_beneficiary=1 conflict_pairs=0 activities=3 |
| Generación y seguimiento de pedidos (PRO-03) | — (ver descripción agregada) | Intents=1 client=1 internal=0 no_beneficiary=0 conflict_pairs=0 activities=4 |
| Compra y Venta de Combustible (PRO-04) | — (ver descripción agregada) | Intents=1 client=0 internal=0 no_beneficiary=1 conflict_pairs=0 activities=2 |
| Facturación (PRO-05) | — (ver descripción agregada) | Intents=1 client=1 internal=0 no_beneficiary=0 conflict_pairs=0 activities=2 |
| Cobranza (PRO-06) | — (ver descripción agregada) | Intents=1 client=1 internal=0 no_beneficiary=0 conflict_pairs=0 activities=8 |
| Control / Trazabilidad Documental (PRO-07) | — (ver descripción agregada) | Intents=1 client=0 internal=0 no_beneficiary=1 conflict_pairs=0 activities=1 |
| Gestión de Quejas y No Conformidades (PRO-08) | — (ver descripción agregada) | Intents=1 client=0 internal=0 no_beneficiary=1 conflict_pairs=0 activities=1 |
| Auditorías internas y a proveedores (PRO-09) | — (ver descripción agregada) | Intents=1 client=0 internal=0 no_beneficiary=1 conflict_pairs=0 activities=2 |

_Sin casos:_ 1.2 Intención desviada del proceso; 1.3 Intenciones en conflicto; 1.4 Tensión interna; 1.6 Valor que nadie persigue; 1.8 Intenciones fusionadas (eliminadas)

## Sección 2 — Cambios en el grafo

_Sin casos:_ 2.1 Actividades consolidadas; 2.2 Actividades generadas; 2.3 Aristas de efecto añadidas; 2.4 Orden corregido; 2.5 Métricas añadidas; 2.6 Correcciones de esquema

## Sección 3 — Pendientes a resolver

#### 3.1 Alcanzabilidad de valor

**Situación.** Un proceso declara contribución a valor pero no hay terminal alcanzable, o una actividad de ese proceso no llega al evento de realización.

**Por qué importa.** Sin ruta al desenlace de valor, la contribución del proceso es una afirmación sin soporte estructural (coherencia de flujo).

**Explicación.** Chequeo estructural 1 / REALIZES. Puede ser hueco de aristas PRECEDES, falta de Event terminal, o actividad colgando fuera del eje. No implica por sí solo mala intención.

**Casos.**

| Elemento | Proceso o contexto | Qué falla |
| --- | --- | --- |
| Generación y seguimiento de pedidos (PRO-03) | Generación y seguimiento de pedidos (PRO-03) | Process with CONTRIBUTES_TO has no value_realization event (no REALIZES path and no produce INVOLVES_EVENT) |
| Facturación (PRO-05) | Facturación (PRO-05) | Process with CONTRIBUTES_TO has no value_realization event (no REALIZES path and no produce INVOLVES_EVENT) |
| Registro del pago / saldo en Smartsheet (ACT-14) | Cobranza (PRO-06) | Activity cannot reach its process realization event |
| Contacto al cliente por factura vencida (ACT-15) | Cobranza (PRO-06) | Activity cannot reach its process realization event |
| Generación y envío del estado de cuenta del cliente (ACT-16) | Cobranza (PRO-06) | Activity cannot reach its process realization event |
| Escalamiento a Dirección por cobro vencido (ACT-17) | Cobranza (PRO-06) | Activity cannot reach its process realization event |
| Identificación de facturas vencidas (ACT-31) | Cobranza (PRO-06) | Activity cannot reach its process realization event |

#### 3.2 Completitud de flujo

**Situación.** Demandas sin camino a valor, o actividades colgantes (aisladas en PRECEDES).

**Por qué importa.** Fragmentos del grafo no participan del patrón demanda→valor; el mapa operativo está incompleto o roto.

**Explicación.** C6 y chequeo estructural 4. Una actividad aislada puede ser soporte real no enlazado, o basura de extracción.

**Casos.**

| Elemento | Tipo de hueco | Detalle |
| --- | --- | --- |
| Gestión de quejas y no conformidades (ACT-19) | actividad aislada | Activity isolated on PRECEDES |
| Auditorías a proveedores (ACT-21) | actividad aislada | Activity isolated on PRECEDES |

#### 3.3 Topología de flujo (ramas y ciclos)

**Situación.** Ramas que no reconvergen antes del terminal, o ciclos en PRECEDES, o actividad posterior al terminal.

**Por qué importa.** El orden operativo no es un DAG limpio hacia el valor; priorización y P se vuelven ambiguos.

**Explicación.** Chequeo estructural 5 / C7. Reconvergencia ausente no siempre es error (flujos paralelos legítimos); ciclos sí lo son.

**Casos.**

| Elemento(s) | Proceso (si aplica) | Qué se observó |
| --- | --- | --- |
| Elaboración y envío de cotización (ACT-03) | Cotización al Cliente (PRO-02) | Branches do not reconverge before their terminals |
| Confirmación del pedido por el cliente (ACT-04) | Cotización al Cliente (PRO-02) | Branches do not reconverge before their terminals |
| Emisión de Orden de Compra al proveedor (con prepago) (ACT-06) | Generación y seguimiento de pedidos (PRO-03) | Branches do not reconverge before their terminals |
| Ejecución de la carga y emisión del BOL (ACT-08) | Compra y Venta de Combustible (PRO-04) | Branches do not reconverge before their terminals |
| Timbrado del CFDI en SAE/ASPEL (ACT-10) | Facturación (PRO-05) | Branches do not reconverge before their terminals |
| Envío del CFDI al cliente (ACT-11) | Facturación (PRO-05) | Branches do not reconverge before their terminals |
| Conciliación factura – estado de cuenta bancario – Smartsheet (ACT-13) | Cobranza (PRO-06) | Branches do not reconverge before their terminals |
| Registro del pago / saldo en Smartsheet (ACT-14) | Cobranza (PRO-06) | Branches do not reconverge before their terminals |
| Integración del expediente legal por operación (trazabilidad documental) (ACT-18) | Control / Trazabilidad Documental (PRO-07) | Branches do not reconverge before their terminals |
| Recepción del BOL de la empresa de logística (ACT-33) | — (sin proceso) | Branches do not reconverge before their terminals |

#### 3.4 Candidatos a variante

**Situación.** Actividades distintas con la misma intención y vecindario superpuesto — posibles variantes de un mismo esfuerzo.

**Por qué importa.** Candidatos a consolidar (R5 / VARIANT_OF) o a confirmar como trabajo distinto. Pendiente de juicio.

**Explicación.** C9. No se consolidó en esta corrida (R5 diferido; VARIANT_OF aún no en ontología). Solapamiento ≠ identidad.

**Casos.**

| Actividad A | Actividad B | Intención compartida | Proceso(s) | Solapamiento |
| --- | --- | --- | --- | --- |
| Seguimiento al pago (ACT-12) | Registro del pago / saldo en Smartsheet (ACT-14) | Cumplir propósito de Cobranza (INT-06) | Cobranza (PRO-06) · Cobranza (PRO-06) | 0.40 |
| Seguimiento al pago (ACT-12) | Obtención del estado de cuenta bancario (ACT-27) | Cumplir propósito de Cobranza (INT-06) | Cobranza (PRO-06) · Cobranza (PRO-06) | 0.43 |
| Seguimiento al pago (ACT-12) | Identificación de facturas vencidas (ACT-31) | Cumplir propósito de Cobranza (INT-06) | Cobranza (PRO-06) · Cobranza (PRO-06) | 0.43 |
| Registro del pago / saldo en Smartsheet (ACT-14) | Contacto al cliente por factura vencida (ACT-15) | Cumplir propósito de Cobranza (INT-06) | Cobranza (PRO-06) · Cobranza (PRO-06) | 0.40 |
| Registro del pago / saldo en Smartsheet (ACT-14) | Escalamiento a Dirección por cobro vencido (ACT-17) | Cumplir propósito de Cobranza (INT-06) | Cobranza (PRO-06) · Cobranza (PRO-06) | 0.50 |
| Registro del pago / saldo en Smartsheet (ACT-14) | Obtención del estado de cuenta bancario (ACT-27) | Cumplir propósito de Cobranza (INT-06) | Cobranza (PRO-06) · Cobranza (PRO-06) | 0.43 |
| Contacto al cliente por factura vencida (ACT-15) | Escalamiento a Dirección por cobro vencido (ACT-17) | Cumplir propósito de Cobranza (INT-06) | Cobranza (PRO-06) · Cobranza (PRO-06) | 0.50 |
| Obtención del estado de cuenta bancario (ACT-27) | Identificación de facturas vencidas (ACT-31) | Cumplir propósito de Cobranza (INT-06) | Cobranza (PRO-06) · Cobranza (PRO-06) | 0.50 |
| Auditorías internas (ACT-20) | Auditorías a proveedores (ACT-21) | Cumplir propósito de Auditorías internas y a proveedores (INT-09) | Auditorías internas y a proveedores (PRO-09) · Auditorías internas y a proveedores (PRO-09) | 0.75 |
