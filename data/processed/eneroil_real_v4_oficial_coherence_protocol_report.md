# Auditoría de coherencia — protocolo v0.3

## Encabezado

- **Grado de coherencia:** N1=0 N2=0 N3=0 N4=0; evidencia=0 abducción=0; compresión=0.00 (31/0) → N1=3 N2=11 N3=12 N4=5; evidencia=0 abducción=7; compresión=4.43 (31/7)
- **Iteraciones:** 3
- **Ciclo convergió:** sí

- **Top situaciones (Sección 1):** 1.1 Actividades sin intención (reparadas) (31); 1.5 Persigue sin llegar (23); 1.8 Intenciones fusionadas (eliminadas) (9)
- **Top situaciones (Sección 2):** 2.7 Reparaciones topológicas (resumen) (20); 2.9 Renombres de claridad / pares no-variante (15); 2.8 Bifurcaciones resueltas (11)
- **Top situaciones (Sección 3):** 3.1 Completitud de flujo (1); 3.2 Topología de flujo (ramas irresolubles) (1)

## Sección 1 — Salud de las intenciones

#### 1.1 Actividades sin intención (reparadas)

**Situación.** Actividades que no tenían intención propia ni heredada y recibieron una en esta corrida.

**Por qué importa.** Sin intención no hay *para qué* legible; es defecto del modelo (I1), no de la organización.

**Explicación.** Se detectó por C1. R1 asignó intención al proceso (parsimonia) o a la actividad huérfana. No significa que el propósito sea el real — es abducción hasta validar con evidencia.

**Casos.**

| Actividad | Proceso | Intención asignada | Origen | Base | Evidencia |
| --- | --- | --- | --- | --- | --- |
| Obtención y publicación diaria de precios de referencia (Pemex, Valero, Repsol) (ACT-02) | Monitoreo y Precios (Obtención y Envío de Precios) (PRO-01) | Cumplir propósito de Generación y seguimiento de pedidos (INT-03) | heredada | abduction | R1 abduction from Process Monitoreo y Precios (Obtención y Envío de Precios) (PRO-01) |
| Recepción de solicitud del cliente (WhatsApp / correo / llamada) (ACT-01) | Cotización al Cliente (PRO-02) | Cumplir propósito de Generación y seguimiento de pedidos (INT-03) | heredada | abduction | R1 abduction from Process Cotización al Cliente (PRO-02) |
| Elaboración y envío de cotización (ACT-03) | Cotización al Cliente (PRO-02) | Cumplir propósito de Generación y seguimiento de pedidos (INT-03) | heredada | abduction | R1 abduction from Process Cotización al Cliente (PRO-02) |
| Confirmación del pedido por el cliente (ACT-04) | Cotización al Cliente (PRO-02) | Cumplir propósito de Generación y seguimiento de pedidos (INT-03) | heredada | abduction | R1 abduction from Process Cotización al Cliente (PRO-02) |
| Confirmación de disponibilidad de producto (ACT-05) | Generación y seguimiento de pedidos (PRO-03) | Cumplir propósito de Generación y seguimiento de pedidos (INT-03) | heredada | abduction | R1 abduction from Process Generación y seguimiento de pedidos (PRO-03) |
| Emisión de Orden de Compra al proveedor (con prepago) (ACT-06) | Generación y seguimiento de pedidos (PRO-03) | Cumplir propósito de Generación y seguimiento de pedidos (INT-03) | heredada | abduction | R1 abduction from Process Generación y seguimiento de pedidos (PRO-03) |
| Envío del pedido/folio a la empresa de logística (ACT-07) | Generación y seguimiento de pedidos (PRO-03) | Cumplir propósito de Generación y seguimiento de pedidos (INT-03) | heredada | abduction | R1 abduction from Process Generación y seguimiento de pedidos (PRO-03) |
| Consulta informal de disponibilidad a la empresa de logística (ACT-28) | Generación y seguimiento de pedidos (PRO-03) | Cumplir propósito de Generación y seguimiento de pedidos (INT-03) | heredada | abduction | R1 abduction from Process Generación y seguimiento de pedidos (PRO-03) |
| Ejecución de la carga y emisión del BOL (ACT-08) | Compra y Venta de Combustible (PRO-04) | Cumplir propósito de Facturación (INT-05) | heredada | abduction | R1 abduction from Process Compra y Venta de Combustible (PRO-04) |
| Registro de la operación en Smartsheet (ACT-09) | Compra y Venta de Combustible (PRO-04) | Cumplir propósito de Facturación (INT-05) | heredada | abduction | R1 abduction from Process Compra y Venta de Combustible (PRO-04) |
| Timbrado del CFDI en SAE/ASPEL (ACT-10) | Facturación (PRO-05) | Cumplir propósito de Facturación (INT-05) | heredada | abduction | R1 abduction from Process Facturación (PRO-05) |
| Envío del CFDI al cliente (ACT-11) | Facturación (PRO-05) | Cumplir propósito de Facturación (INT-05) | heredada | abduction | R1 abduction from Process Facturación (PRO-05) |
| Seguimiento diario a cartera (pagos pendientes) (ACT-12) | Cobranza (PRO-06) | Cumplir propósito de Cobranza (INT-06) | heredada | abduction | R1 abduction from Process Cobranza (PRO-06) |
| Conciliación factura – estado de cuenta bancario – Smartsheet (ACT-13) | Cobranza (PRO-06) | Cumplir propósito de Cobranza (INT-06) | heredada | abduction | R1 abduction from Process Cobranza (PRO-06) |
| Registro del pago / saldo en Smartsheet (ACT-14) | Cobranza (PRO-06) | Cumplir propósito de Cobranza (INT-06) | heredada | abduction | R1 abduction from Process Cobranza (PRO-06) |
| Contacto al cliente por cartera vencida (ACT-15) | Cobranza (PRO-06) | Cumplir propósito de Cobranza (INT-06) | heredada | abduction | R1 abduction from Process Cobranza (PRO-06) |
| Generación y envío del estado de cuenta del cliente (ACT-16) | Cobranza (PRO-06) | Cumplir propósito de Cobranza (INT-06) | heredada | abduction | R1 abduction from Process Cobranza (PRO-06) |
| Escalamiento a Dirección por cobro vencido (ACT-17) | Cobranza (PRO-06) | Cumplir propósito de Cobranza (INT-06) | heredada | abduction | R1 abduction from Process Cobranza (PRO-06) |
| Obtención del estado de cuenta bancario (ACT-27) | Cobranza (PRO-06) | Cumplir propósito de Cobranza (INT-06) | heredada | abduction | R1 abduction from Process Cobranza (PRO-06) |
| Identificación de cartera vencida (ACT-31) | Cobranza (PRO-06) | Cumplir propósito de Cobranza (INT-06) | heredada | abduction | R1 abduction from Process Cobranza (PRO-06) |
| Integración del expediente legal por operación (trazabilidad documental) (ACT-18) | Control / Trazabilidad Documental (PRO-07) | Cumplir propósito de Control / Trazabilidad Documental (INT-07) | heredada | abduction | R1 abduction from Process Control / Trazabilidad Documental (PRO-07) |
| Gestión de quejas y no conformidades (ACT-19) | Gestión de Quejas y No Conformidades (PRO-08) | Cumplir propósito de Gestión de Quejas y No Conformidades (INT-08) | heredada | abduction | R1 abduction from Process Gestión de Quejas y No Conformidades (PRO-08) |
| Auditoría interna (SGC) (ACT-20) | Auditorías internas y a proveedores (PRO-09) | Cumplir propósito de Auditorías internas y a proveedores (INT-09) | heredada | abduction | R1 abduction from Process Auditorías internas y a proveedores (PRO-09) |
| Auditoría a proveedores (ACT-21) | Auditorías internas y a proveedores (PRO-09) | Cumplir propósito de Auditorías internas y a proveedores (INT-09) | heredada | abduction | R1 abduction from Process Auditorías internas y a proveedores (PRO-09) |
| Aprobación de proveedores (ACT-22) | — (sin proceso) | Cumplir propósito de Generación y seguimiento de pedidos (INT-03) | nueva | abduction | R1 abduction from Activity Aprobación de proveedores (ACT-22) — no Process Intent |
| Gestión de relación regulatoria y reporte volumétrico (CNE) (ACT-23) | — (sin proceso) | Cumplir Gestión de relación regulatoria y reporte volumétrico (CNE) (INT-11) | nueva | abduction | R1 abduction from Activity Gestión de relación regulatoria y reporte volumétrico (CNE) (ACT-23) — no Process Intent |
| Ejecución del prepago al proveedor (ACT-24) | — (sin proceso) | Cumplir propósito de Generación y seguimiento de pedidos (INT-03) | nueva | abduction | R1 abduction from Activity Ejecución del prepago al proveedor (ACT-24) — no Process Intent |
| Monitoreo del estado de liberación de crédito (ACT-32) | — (sin proceso) | Cumplir propósito de Generación y seguimiento de pedidos (INT-03) | nueva | abduction | R1 abduction from Activity Monitoreo del estado de liberación de crédito (ACT-32) — no Process Intent |
| Recepción del BOL de la empresa de logística (ACT-33) | — (sin proceso) | Cumplir propósito de Facturación (INT-05) | nueva | abduction | R1 abduction from Activity Recepción del BOL de la empresa de logística (ACT-33) — no Process Intent |
| Determinación del costo de transporte para la cotización (ACT-26) | — (sin proceso) | Cumplir propósito de Generación y seguimiento de pedidos (INT-03) | nueva | abduction | R1 abduction from Activity Determinación del costo de transporte para la cotización (ACT-26) — no Process Intent |
| Autorización de liberación de fondos para prepago (ACT-30) | — (sin proceso) | Cumplir propósito de Generación y seguimiento de pedidos (INT-03) | nueva | abduction | R1 abduction from Activity Autorización de liberación de fondos para prepago (ACT-30) — no Process Intent |

#### 1.5 Persigue sin llegar

**Situación.** La intención apunta a una métrica, pero no hay ruta de efecto (`AFFECTS`/driver) hasta ella.

**Por qué importa.** O es hueco de datos (falta arista) o esfuerzo que no entrega — C4 no decide cuál. Por ahora solo se reporta; no se inventan `AFFECTS` automáticamente.

**Explicación.** Detectado por C4: Intent.SERVES → M sin efecto de la actividad a M. N3 en la escalera. El peso en relevancia se calibrará más adelante.

**Casos.**

| Actividad | Proceso | Intención | Métrica a la que sirve | Qué ruta falta |
| --- | --- | --- | --- | --- |
| Recepción de solicitud del cliente (WhatsApp / correo / llamada) (ACT-01) | Cotización al Cliente (PRO-02) | Cumplir propósito de Generación y seguimiento de pedidos (INT-03) | Confiabilidad de entrega (producto / volumen / destino / fecha) (MET-01) | AFFECTS o AFFECTS→MetricDriver→DRIVES hacia la métrica |
| Obtención y publicación diaria de precios de referencia (Pemex, Valero, Repsol) (ACT-02) | Monitoreo y Precios (Obtención y Envío de Precios) (PRO-01) | Cumplir propósito de Generación y seguimiento de pedidos (INT-03) | Confiabilidad de entrega (producto / volumen / destino / fecha) (MET-01) | AFFECTS o AFFECTS→MetricDriver→DRIVES hacia la métrica |
| Elaboración y envío de cotización (ACT-03) | Cotización al Cliente (PRO-02) | Cumplir propósito de Generación y seguimiento de pedidos (INT-03) | Confiabilidad de entrega (producto / volumen / destino / fecha) (MET-01) | AFFECTS o AFFECTS→MetricDriver→DRIVES hacia la métrica |
| Confirmación del pedido por el cliente (ACT-04) | Cotización al Cliente (PRO-02) | Cumplir propósito de Generación y seguimiento de pedidos (INT-03) | Confiabilidad de entrega (producto / volumen / destino / fecha) (MET-01) | AFFECTS o AFFECTS→MetricDriver→DRIVES hacia la métrica |
| Emisión de Orden de Compra al proveedor (con prepago) (ACT-06) | Generación y seguimiento de pedidos (PRO-03) | Cumplir propósito de Generación y seguimiento de pedidos (INT-03) | Confiabilidad de entrega (producto / volumen / destino / fecha) (MET-01) | AFFECTS o AFFECTS→MetricDriver→DRIVES hacia la métrica |
| Envío del pedido/folio a la empresa de logística (ACT-07) | Generación y seguimiento de pedidos (PRO-03) | Cumplir propósito de Generación y seguimiento de pedidos (INT-03) | Confiabilidad de entrega (producto / volumen / destino / fecha) (MET-01) | AFFECTS o AFFECTS→MetricDriver→DRIVES hacia la métrica |
| Ejecución de la carga y emisión del BOL (ACT-08) | Compra y Venta de Combustible (PRO-04) | Cumplir propósito de Facturación (INT-05) | CFDI correcto y a tiempo (MET-02) | AFFECTS o AFFECTS→MetricDriver→DRIVES hacia la métrica |
| Registro de la operación en Smartsheet (ACT-09) | Compra y Venta de Combustible (PRO-04) | Cumplir propósito de Facturación (INT-05) | CFDI correcto y a tiempo (MET-02) | AFFECTS o AFFECTS→MetricDriver→DRIVES hacia la métrica |
| Envío del CFDI al cliente (ACT-11) | Facturación (PRO-05) | Cumplir propósito de Facturación (INT-05) | CFDI correcto y a tiempo (MET-02) | AFFECTS o AFFECTS→MetricDriver→DRIVES hacia la métrica |
| Seguimiento diario a cartera (pagos pendientes) (ACT-12) | Cobranza (PRO-06) | Cumplir propósito de Cobranza (INT-06) | Transparencia / exactitud del estado de cuenta (MET-03) | AFFECTS o AFFECTS→MetricDriver→DRIVES hacia la métrica |
| Conciliación factura – estado de cuenta bancario – Smartsheet (ACT-13) | Cobranza (PRO-06) | Cumplir propósito de Cobranza (INT-06) | Transparencia / exactitud del estado de cuenta (MET-03) | AFFECTS o AFFECTS→MetricDriver→DRIVES hacia la métrica |
| Registro del pago / saldo en Smartsheet (ACT-14) | Cobranza (PRO-06) | Cumplir propósito de Cobranza (INT-06) | Transparencia / exactitud del estado de cuenta (MET-03) | AFFECTS o AFFECTS→MetricDriver→DRIVES hacia la métrica |
| Contacto al cliente por cartera vencida (ACT-15) | Cobranza (PRO-06) | Cumplir propósito de Cobranza (INT-06) | Transparencia / exactitud del estado de cuenta (MET-03) | AFFECTS o AFFECTS→MetricDriver→DRIVES hacia la métrica |
| Escalamiento a Dirección por cobro vencido (ACT-17) | Cobranza (PRO-06) | Cumplir propósito de Cobranza (INT-06) | Transparencia / exactitud del estado de cuenta (MET-03) | AFFECTS o AFFECTS→MetricDriver→DRIVES hacia la métrica |
| Aprobación de proveedores (ACT-22) | — (sin proceso) | Cumplir propósito de Generación y seguimiento de pedidos (INT-03) | Confiabilidad de entrega (producto / volumen / destino / fecha) (MET-01) | AFFECTS o AFFECTS→MetricDriver→DRIVES hacia la métrica |
| Ejecución del prepago al proveedor (ACT-24) | — (sin proceso) | Cumplir propósito de Generación y seguimiento de pedidos (INT-03) | Confiabilidad de entrega (producto / volumen / destino / fecha) (MET-01) | AFFECTS o AFFECTS→MetricDriver→DRIVES hacia la métrica |
| Monitoreo del estado de liberación de crédito (ACT-32) | — (sin proceso) | Cumplir propósito de Generación y seguimiento de pedidos (INT-03) | Confiabilidad de entrega (producto / volumen / destino / fecha) (MET-01) | AFFECTS o AFFECTS→MetricDriver→DRIVES hacia la métrica |
| Recepción del BOL de la empresa de logística (ACT-33) | — (sin proceso) | Cumplir propósito de Facturación (INT-05) | CFDI correcto y a tiempo (MET-02) | AFFECTS o AFFECTS→MetricDriver→DRIVES hacia la métrica |
| Determinación del costo de transporte para la cotización (ACT-26) | — (sin proceso) | Cumplir propósito de Generación y seguimiento de pedidos (INT-03) | Confiabilidad de entrega (producto / volumen / destino / fecha) (MET-01) | AFFECTS o AFFECTS→MetricDriver→DRIVES hacia la métrica |
| Obtención del estado de cuenta bancario (ACT-27) | Cobranza (PRO-06) | Cumplir propósito de Cobranza (INT-06) | Transparencia / exactitud del estado de cuenta (MET-03) | AFFECTS o AFFECTS→MetricDriver→DRIVES hacia la métrica |
| Consulta informal de disponibilidad a la empresa de logística (ACT-28) | Generación y seguimiento de pedidos (PRO-03) | Cumplir propósito de Generación y seguimiento de pedidos (INT-03) | Confiabilidad de entrega (producto / volumen / destino / fecha) (MET-01) | AFFECTS o AFFECTS→MetricDriver→DRIVES hacia la métrica |
| Autorización de liberación de fondos para prepago (ACT-30) | — (sin proceso) | Cumplir propósito de Generación y seguimiento de pedidos (INT-03) | Confiabilidad de entrega (producto / volumen / destino / fecha) (MET-01) | AFFECTS o AFFECTS→MetricDriver→DRIVES hacia la métrica |
| Identificación de cartera vencida (ACT-31) | Cobranza (PRO-06) | Cumplir propósito de Cobranza (INT-06) | Transparencia / exactitud del estado de cuenta (MET-03) | AFFECTS o AFFECTS→MetricDriver→DRIVES hacia la métrica |

#### 1.7 Intención sin beneficiario

**Situación.** Existe el *para qué*, pero no el *para quién* (`SERVES` ausente).

**Por qué importa.** Señal de coherencia (ontología): propósito cuyo destinatario no está identificado.

**Explicación.** C1 sobre Intent sin SERVES. R2 solo enlaza cuando hay CONTRIBUTES_TO o efecto claro; si no, queda como hallazgo — no se inventa un beneficiario. Candidatos medio-a-fin (R3) se listan en la columna de propuesta.

**Casos.**

| Intención | Actividades y procesos que la persiguen | ¿Propuesta merge medio-a-fin? |
| --- | --- | --- |
| Cumplir propósito de Control / Trazabilidad Documental (INT-07) | Control / Trazabilidad Documental (PRO-07) | — (conservar / SERVES interno pendiente) |
| Cumplir propósito de Gestión de Quejas y No Conformidades (INT-08) | Gestión de Quejas y No Conformidades (PRO-08) | — (conservar / SERVES interno pendiente) |
| Cumplir propósito de Auditorías internas y a proveedores (INT-09) | Auditorías internas y a proveedores (PRO-09) | — (conservar / SERVES interno pendiente) |
| Cumplir Gestión de relación regulatoria y reporte volumétrico (CNE) (INT-11) | Gestión de relación regulatoria y reporte volumétrico (CNE) (ACT-23) | — (conservar / SERVES interno pendiente) |

#### 1.8 Intenciones fusionadas (eliminadas)

**Situación.** Intenciones equivalentes o medio-a-fin colapsadas en una canónica (única eliminación permitida).

**Por qué importa.** Compresión de intenciones: menos nodos, mismo propósito compartido.

**Explicación.** R3 means-to-end / equivalencia — requiere autorización ontológica de la corrida.

**Casos.**

| Intención eliminada | Intención canónica | Actividades reasignadas con su proceso | Evidencia de equivalencia o medio-a-fin |
| --- | --- | --- | --- |
| — (INT-01) | Cumplir propósito de Generación y seguimiento de pedidos (INT-03) | Monitoreo y Precios (Obtención y Envío de Precios) (PRO-01); Cotización al Cliente (PRO-02); Generación y seguimiento de pedidos (PRO-03); Aprobación de proveedores (ACT-22); Ejecución del prepago al proveedor (ACT-24); Monitoreo del estado de liberación de crédito (ACT-32); Determinación del costo de transporte para la cotización (ACT-26); Autorización de liberación de fondos para prepago (ACT-30) | R3 means-to-end: ACT-02 PRECEDES…→ ACT-05 pursues INT-03 |
| — (INT-02) | Cumplir propósito de Generación y seguimiento de pedidos (INT-03) | Monitoreo y Precios (Obtención y Envío de Precios) (PRO-01); Cotización al Cliente (PRO-02); Generación y seguimiento de pedidos (PRO-03); Aprobación de proveedores (ACT-22); Ejecución del prepago al proveedor (ACT-24); Monitoreo del estado de liberación de crédito (ACT-32); Determinación del costo de transporte para la cotización (ACT-26); Autorización de liberación de fondos para prepago (ACT-30) | R3 means-to-end: ACT-01 PRECEDES…→ ACT-05 pursues INT-03 |
| — (INT-04) | Cumplir propósito de Facturación (INT-05) | Compra y Venta de Combustible (PRO-04); Facturación (PRO-05); Recepción del BOL de la empresa de logística (ACT-33) | R3 means-to-end: ACT-09 PRECEDES…→ ACT-11 pursues INT-05 |
| — (INT-10) | Cumplir propósito de Generación y seguimiento de pedidos (INT-03) | Monitoreo y Precios (Obtención y Envío de Precios) (PRO-01); Cotización al Cliente (PRO-02); Generación y seguimiento de pedidos (PRO-03); Aprobación de proveedores (ACT-22); Ejecución del prepago al proveedor (ACT-24); Monitoreo del estado de liberación de crédito (ACT-32); Determinación del costo de transporte para la cotización (ACT-26); Autorización de liberación de fondos para prepago (ACT-30) | R3 means-to-end: ACT-22 PRECEDES…→ ACT-07 pursues INT-03 |
| — (INT-12) | Cumplir propósito de Generación y seguimiento de pedidos (INT-03) | Monitoreo y Precios (Obtención y Envío de Precios) (PRO-01); Cotización al Cliente (PRO-02); Generación y seguimiento de pedidos (PRO-03); Aprobación de proveedores (ACT-22); Ejecución del prepago al proveedor (ACT-24); Monitoreo del estado de liberación de crédito (ACT-32); Determinación del costo de transporte para la cotización (ACT-26); Autorización de liberación de fondos para prepago (ACT-30) | R3 means-to-end: ACT-24 PRECEDES…→ ACT-07 pursues INT-03 |
| — (INT-13) | Cumplir propósito de Generación y seguimiento de pedidos (INT-03) | Monitoreo y Precios (Obtención y Envío de Precios) (PRO-01); Cotización al Cliente (PRO-02); Generación y seguimiento de pedidos (PRO-03); Aprobación de proveedores (ACT-22); Ejecución del prepago al proveedor (ACT-24); Monitoreo del estado de liberación de crédito (ACT-32); Determinación del costo de transporte para la cotización (ACT-26); Autorización de liberación de fondos para prepago (ACT-30) | R3 means-to-end: ACT-32 PRECEDES…→ ACT-07 pursues INT-03 |
| — (INT-14) | Cumplir propósito de Facturación (INT-05) | Compra y Venta de Combustible (PRO-04); Facturación (PRO-05); Recepción del BOL de la empresa de logística (ACT-33) | R3 means-to-end: ACT-33 PRECEDES…→ ACT-11 pursues INT-05 |
| — (INT-15) | Cumplir propósito de Generación y seguimiento de pedidos (INT-03) | Monitoreo y Precios (Obtención y Envío de Precios) (PRO-01); Cotización al Cliente (PRO-02); Generación y seguimiento de pedidos (PRO-03); Aprobación de proveedores (ACT-22); Ejecución del prepago al proveedor (ACT-24); Monitoreo del estado de liberación de crédito (ACT-32); Determinación del costo de transporte para la cotización (ACT-26); Autorización de liberación de fondos para prepago (ACT-30) | R3 means-to-end: ACT-26 PRECEDES…→ ACT-05 pursues INT-03 |
| — (INT-16) | Cumplir propósito de Generación y seguimiento de pedidos (INT-03) | Monitoreo y Precios (Obtención y Envío de Precios) (PRO-01); Cotización al Cliente (PRO-02); Generación y seguimiento de pedidos (PRO-03); Aprobación de proveedores (ACT-22); Ejecución del prepago al proveedor (ACT-24); Monitoreo del estado de liberación de crédito (ACT-32); Determinación del costo de transporte para la cotización (ACT-26); Autorización de liberación de fondos para prepago (ACT-30) | R3 means-to-end: ACT-30 PRECEDES…→ ACT-07 pursues INT-03 |

#### 1.9 Dispersión funcional

**Situación.** Perfil de intenciones por proceso/equipo: cliente vs interna vs sin beneficiario.

**Por qué importa.** Define la función de cada parte de la organización y dónde hay conflicto o vacío.

**Explicación.** Agregado por C11. Es diagnóstico, no defecto por sí solo.

**Casos.**

| Equipo o Proceso | Intenciones que persigue | Proporción al cliente / interna / sin beneficiario / en conflicto |
| --- | --- | --- |
| Monitoreo y Precios (Obtención y Envío de Precios) (PRO-01) | — (ver descripción agregada) | Intents=1 client=1 internal=0 no_beneficiary=0 conflict_pairs=0 activities=1 |
| Cotización al Cliente (PRO-02) | — (ver descripción agregada) | Intents=1 client=1 internal=0 no_beneficiary=0 conflict_pairs=0 activities=3 |
| Generación y seguimiento de pedidos (PRO-03) | — (ver descripción agregada) | Intents=1 client=1 internal=0 no_beneficiary=0 conflict_pairs=0 activities=4 |
| Compra y Venta de Combustible (PRO-04) | — (ver descripción agregada) | Intents=1 client=1 internal=0 no_beneficiary=0 conflict_pairs=0 activities=2 |
| Facturación (PRO-05) | — (ver descripción agregada) | Intents=1 client=1 internal=0 no_beneficiary=0 conflict_pairs=0 activities=2 |
| Cobranza (PRO-06) | — (ver descripción agregada) | Intents=1 client=1 internal=0 no_beneficiary=0 conflict_pairs=0 activities=8 |
| Control / Trazabilidad Documental (PRO-07) | — (ver descripción agregada) | Intents=1 client=0 internal=0 no_beneficiary=1 conflict_pairs=0 activities=1 |
| Gestión de Quejas y No Conformidades (PRO-08) | — (ver descripción agregada) | Intents=1 client=0 internal=0 no_beneficiary=1 conflict_pairs=0 activities=1 |
| Auditorías internas y a proveedores (PRO-09) | — (ver descripción agregada) | Intents=1 client=0 internal=0 no_beneficiary=1 conflict_pairs=0 activities=2 |

_Sin casos:_ 1.2 Intención desviada del proceso; 1.3 Intenciones en conflicto; 1.4 Tensión interna; 1.6 Valor que nadie persigue

## Sección 2 — Cambios en el grafo

#### 2.4 Orden / alcanzabilidad corregida

**Situación.** Cambios en `PRECEDES` / `REALIZES` / `INVOLVES_EVENT` para terminales de valor.

**Por qué importa.** Corrige alcanzabilidad mecánica (check 1 / C5–C7) sin cambiar el vocabulario ontológico.

**Explicación.** R6 topología — aplicada automáticamente y reportada.

**Casos.**

| Actividades u eventos involucrados | Proceso | Qué cambió | Evento terminal | Métrica |
| --- | --- | --- | --- | --- |
| Entrega confirmada en destino (EVT-09) · Confiabilidad de entrega (producto / volumen / destino / fecha) (MET-01) | — (sin proceso) | REALIZES EVT-09 → MET-01 | Entrega confirmada en destino (EVT-09) | Confiabilidad de entrega (producto / volumen / destino / fecha) (MET-01) |
| CFDI timbrado (factura emitida) (EVT-06) · CFDI correcto y a tiempo (MET-02) | — (sin proceso) | REALIZES EVT-06 → MET-02 | CFDI timbrado (factura emitida) (EVT-06) | CFDI correcto y a tiempo (MET-02) |
| Envío del CFDI al cliente (ACT-11) · CFDI timbrado (factura emitida) (EVT-06) | Facturación (PRO-05) | PRECEDES ACT-11 → EVT-06 | CFDI timbrado (factura emitida) (EVT-06) | — |
| Cobro conciliado (valor asegurado) (EVT-10) · Transparencia / exactitud del estado de cuenta (MET-03) | — (sin proceso) | REALIZES EVT-10 → MET-03 | Cobro conciliado (valor asegurado) (EVT-10) | Transparencia / exactitud del estado de cuenta (MET-03) |
| Registro del pago / saldo en Smartsheet (ACT-14) · Cobro conciliado (valor asegurado) (EVT-10) | Cobranza (PRO-06) | PRECEDES ACT-14 → EVT-10 | Cobro conciliado (valor asegurado) (EVT-10) | — |
| Contacto al cliente por cartera vencida (ACT-15) · Cobro conciliado (valor asegurado) (EVT-10) | Cobranza (PRO-06) | PRECEDES ACT-15 → EVT-10 | Cobro conciliado (valor asegurado) (EVT-10) | — |
| Generación y envío del estado de cuenta del cliente (ACT-16) · Cobro conciliado (valor asegurado) (EVT-10) | Cobranza (PRO-06) | PRECEDES ACT-16 → EVT-10 | Cobro conciliado (valor asegurado) (EVT-10) | — |
| Escalamiento a Dirección por cobro vencido (ACT-17) · Cobro conciliado (valor asegurado) (EVT-10) | Cobranza (PRO-06) | PRECEDES ACT-17 → EVT-10 | Cobro conciliado (valor asegurado) (EVT-10) | — |
| Auditoría interna (SGC) (ACT-20) · Auditoría a proveedores (ACT-21) | Auditorías internas y a proveedores (PRO-09) | PRECEDES ACT-20 → ACT-21 | Auditoría a proveedores (ACT-21) | — |

#### 2.7 Reparaciones topológicas (resumen)

**Situación.** Aristas de instancia añadidas en la corrida (ningún tipo ontológico nuevo).

**Por qué importa.** Transparencia de lo que R6 cambió automáticamente.

**Explicación.** Derivado de reparaciones R6.

**Casos.**

| Arista / cambio | Evidencia |
| --- | --- |
| REALIZES EVT-09 → MET-01 | R6 topology: PRO-03 CONTRIBUTES_TO MET-01; wire EVT-09 REALIZES MET-01 |
| REALIZES EVT-06 → MET-02 | R6 topology: PRO-05 CONTRIBUTES_TO MET-02; wire EVT-06 REALIZES MET-02 |
| PRECEDES ACT-11 → EVT-06 | R6 reachability: ACT-11 → EVT-06 for PRO-05/MET-02 |
| REALIZES EVT-10 → MET-03 | R6 topology: PRO-06 CONTRIBUTES_TO MET-03; wire EVT-10 REALIZES MET-03 |
| PRECEDES ACT-14 → EVT-10 | R6 reachability: ACT-14 → EVT-10 for PRO-06/MET-03 |
| PRECEDES ACT-15 → EVT-10 | R6 reachability: ACT-15 → EVT-10 for PRO-06/MET-03 |
| PRECEDES ACT-16 → EVT-10 | R6 reachability: ACT-16 → EVT-10 for PRO-06/MET-03 |
| PRECEDES ACT-17 → EVT-10 | R6 reachability: ACT-17 → EVT-10 for PRO-06/MET-03 |
| PRECEDES ACT-20 → ACT-21 | R6 hanging: ACT-20 → ACT-21 within PRO-09 |
| branch: hito Event en paralelo (continuación + emisión) | R6 branch accepted (parallel_milestone): ACT-03 → [ACT-04, EVT-02] |
| branch: hito Event en paralelo (continuación + emisión) | R6 branch accepted (parallel_milestone): ACT-04 → [ACT-05, EVT-03] |
| branch: hito Event en paralelo (continuación + emisión) | R6 branch accepted (parallel_milestone): ACT-06 → [ACT-07, ACT-24, ACT-09, ACT-18, EVT-04] |
| branch: hito Event en paralelo (continuación + emisión) | R6 branch accepted (parallel_milestone): ACT-08 → [ACT-09, ACT-18, ACT-33, EVT-05] |
| branch: hito Event en paralelo (continuación + emisión) | R6 branch accepted (parallel_milestone): ACT-10 → [ACT-11, ACT-13, EVT-06] |
| branch: hito Event en paralelo (continuación + emisión) | R6 branch accepted (parallel_milestone): ACT-11 → [ACT-12, ACT-18, EVT-06] |
| branch: hito Event en paralelo (continuación + emisión) | R6 branch accepted (parallel_milestone): ACT-13 → [ACT-14, EVT-10] |
| branch: hito Event en paralelo (continuación + emisión) | R6 branch accepted (parallel_milestone): ACT-14 → [ACT-16, EVT-07, EVT-10] |
| branch: hito Event en paralelo (continuación + emisión) | R6 branch accepted (parallel_milestone): ACT-15 → [ACT-16, EVT-10] |
| branch: hito Event en paralelo (continuación + emisión) | R6 branch accepted (parallel_milestone): ACT-16 → [ACT-17, EVT-10] |
| branch: hito Event en paralelo (continuación + emisión) | R6 branch accepted (parallel_milestone): ACT-33 → [ACT-10, EVT-09] |

#### 2.8 Bifurcaciones resueltas

**Situación.** Forks `PRECEDES` sin reconvergencia intermedia clasificados como aceptables (o unidos).

**Por qué importa.** Evita alarmas por hitos en paralelo o ramas de excepción; solo lo irresoluble va a Sección 3.

**Explicación.** R6 branch: hito Event paralelo, Event+Activity, o sinks compartidos.

**Casos.**

| Nodo horquilla | Sucesores | Resolución | Evidencia |
| --- | --- | --- | --- |
| Elaboración y envío de cotización (ACT-03) | Confirmación del pedido por el cliente (ACT-04), Cotización enviada (EVT-02) | hito Event en paralelo (continuación + emisión) | R6 branch accepted (parallel_milestone): ACT-03 → [ACT-04, EVT-02] |
| Confirmación del pedido por el cliente (ACT-04) | Confirmación de disponibilidad de producto (ACT-05), Pedido confirmado por cliente (EVT-03) | hito Event en paralelo (continuación + emisión) | R6 branch accepted (parallel_milestone): ACT-04 → [ACT-05, EVT-03] |
| Emisión de Orden de Compra al proveedor (con prepago) (ACT-06) | Envío del pedido/folio a la empresa de logística (ACT-07), Ejecución del prepago al proveedor (ACT-24), Registro de la operación en Smartsheet (ACT-09), Integración del expediente legal por operación (trazabilidad documental) (ACT-18) | hito Event en paralelo (continuación + emisión) | R6 branch accepted (parallel_milestone): ACT-06 → [ACT-07, ACT-24, ACT-09, ACT-18, EVT-04] |
| Ejecución de la carga y emisión del BOL (ACT-08) | Registro de la operación en Smartsheet (ACT-09), Integración del expediente legal por operación (trazabilidad documental) (ACT-18), Recepción del BOL de la empresa de logística (ACT-33), Carga ejecutada / BOL emitido (EVT-05) | hito Event en paralelo (continuación + emisión) | R6 branch accepted (parallel_milestone): ACT-08 → [ACT-09, ACT-18, ACT-33, EVT-05] |
| Timbrado del CFDI en SAE/ASPEL (ACT-10) | Envío del CFDI al cliente (ACT-11), Conciliación factura – estado de cuenta bancario – Smartsheet (ACT-13), CFDI timbrado (factura emitida) (EVT-06) | hito Event en paralelo (continuación + emisión) | R6 branch accepted (parallel_milestone): ACT-10 → [ACT-11, ACT-13, EVT-06] |
| Envío del CFDI al cliente (ACT-11) | Seguimiento diario a cartera (pagos pendientes) (ACT-12), Integración del expediente legal por operación (trazabilidad documental) (ACT-18), CFDI timbrado (factura emitida) (EVT-06) | hito Event en paralelo (continuación + emisión) | R6 branch accepted (parallel_milestone): ACT-11 → [ACT-12, ACT-18, EVT-06] |
| Conciliación factura – estado de cuenta bancario – Smartsheet (ACT-13) | Registro del pago / saldo en Smartsheet (ACT-14), Cobro conciliado (valor asegurado) (EVT-10) | hito Event en paralelo (continuación + emisión) | R6 branch accepted (parallel_milestone): ACT-13 → [ACT-14, EVT-10] |
| Registro del pago / saldo en Smartsheet (ACT-14) | Generación y envío del estado de cuenta del cliente (ACT-16), Pago recibido (cobro) (EVT-07), Cobro conciliado (valor asegurado) (EVT-10) | hito Event en paralelo (continuación + emisión) | R6 branch accepted (parallel_milestone): ACT-14 → [ACT-16, EVT-07, EVT-10] |
| Contacto al cliente por cartera vencida (ACT-15) | Generación y envío del estado de cuenta del cliente (ACT-16), Cobro conciliado (valor asegurado) (EVT-10) | hito Event en paralelo (continuación + emisión) | R6 branch accepted (parallel_milestone): ACT-15 → [ACT-16, EVT-10] |
| Generación y envío del estado de cuenta del cliente (ACT-16) | Escalamiento a Dirección por cobro vencido (ACT-17), Cobro conciliado (valor asegurado) (EVT-10) | hito Event en paralelo (continuación + emisión) | R6 branch accepted (parallel_milestone): ACT-16 → [ACT-17, EVT-10] |
| Recepción del BOL de la empresa de logística (ACT-33) | Timbrado del CFDI en SAE/ASPEL (ACT-10), Entrega confirmada en destino (EVT-09) | hito Event en paralelo (continuación + emisión) | R6 branch accepted (parallel_milestone): ACT-33 → [ACT-10, EVT-09] |

#### 2.9 Renombres de claridad / pares no-variante

**Situación.** Actividades renombradas para no confundir pasos hermanos, o pares descartados como variantes.

**Por qué importa.** Reduce falsos candidatos C9; lo aún ambiguo queda en Sección 3.

**Explicación.** R5 claridad (rename) o R5 distinct (secuenciales / roles distintos).

**Casos.**

| Elementos | Cambio o veredicto | Motivo |
| --- | --- | --- |
| Seguimiento diario a cartera (pagos pendientes) (ACT-12) | Seguimiento al pago → Seguimiento diario a cartera (pagos pendientes) | R5 clarity rename: distinguir de contacto/escalamiento por vencida |
| Contacto al cliente por cartera vencida (ACT-15) | Contacto al cliente por factura vencida → Contacto al cliente por cartera vencida | R5 clarity rename: alinear con cartera vencida (no solo una factura) |
| Auditoría interna (SGC) (ACT-20) | Auditorías internas → Auditoría interna (SGC) | R5 clarity rename: distinguir de auditoría a proveedores |
| Auditoría a proveedores (ACT-21) | Auditorías a proveedores → Auditoría a proveedores | R5 clarity rename: singular claro vs auditoría interna |
| Identificación de cartera vencida (ACT-31) | Identificación de facturas vencidas → Identificación de cartera vencida | R5 clarity rename: aclarar precursor de contacto por vencida |
| Seguimiento diario a cartera (pagos pendientes) (ACT-12) · Obtención del estado de cuenta bancario (ACT-27) | no son variantes | roles distintos (follow vs bank_stmt) |
| Seguimiento diario a cartera (pagos pendientes) (ACT-12) · Identificación de cartera vencida (ACT-31) | no son variantes | roles distintos (follow vs overdue) |
| Registro del pago / saldo en Smartsheet (ACT-14) · Contacto al cliente por cartera vencida (ACT-15) | no son variantes | roles distintos (register vs overdue) |
| Registro del pago / saldo en Smartsheet (ACT-14) · Escalamiento a Dirección por cobro vencido (ACT-17) | no son variantes | hay PRECEDES entre ellas — pasos del flujo, no variantes |
| Contacto al cliente por cartera vencida (ACT-15) · Escalamiento a Dirección por cobro vencido (ACT-17) | no son variantes | hay PRECEDES entre ellas — pasos del flujo, no variantes |
| Obtención del estado de cuenta bancario (ACT-27) · Identificación de cartera vencida (ACT-31) | no son variantes | roles distintos (bank_stmt vs overdue) |
| Auditoría interna (SGC) (ACT-20) · Auditoría a proveedores (ACT-21) | no son variantes | hay PRECEDES entre ellas — pasos del flujo, no variantes |
| Envío del pedido/folio a la empresa de logística (ACT-07) · Ejecución del prepago al proveedor (ACT-24) | no son variantes | hay PRECEDES entre ellas — pasos del flujo, no variantes |
| Aprobación de proveedores (ACT-22) · Autorización de liberación de fondos para prepago (ACT-30) | no son variantes | roles distintos (approve_sup vs prepay) |
| Autorización de liberación de fondos para prepago (ACT-30) · Monitoreo del estado de liberación de crédito (ACT-32) | no son variantes | hay PRECEDES entre ellas — pasos del flujo, no variantes |

_Sin casos:_ 2.1 Actividades consolidadas; 2.2 Actividades generadas; 2.3 Aristas de efecto añadidas; 2.5 Métricas añadidas; 2.6 Correcciones de esquema

## Sección 3 — Pendientes a resolver

#### 3.1 Completitud de flujo

**Situación.** Demandas sin camino a valor, o actividades colgantes (aisladas en PRECEDES).

**Por qué importa.** Fragmentos del grafo no participan del patrón demanda→valor; el mapa operativo está incompleto o roto.

**Explicación.** C6 y chequeo estructural 4. Una actividad aislada puede ser soporte real no enlazado, o basura de extracción.

**Casos.**

| Elemento | Tipo de hueco | Detalle |
| --- | --- | --- |
| Gestión de quejas y no conformidades (ACT-19) | actividad aislada | Activity isolated on PRECEDES |

#### 3.2 Topología de flujo (ramas irresolubles)

**Situación.** Forks `PRECEDES` que no reconvergen y no encajan en hito paralelo / excepción / sinks compartidos.

**Por qué importa.** Aquí sí hay ambigüedad de orden hacia el valor; priorización y P pueden fallar.

**Explicación.** Check 5 tras filtro R6. Los forks aceptados están en Sección 2.8.

**Casos.**

| Elemento(s) | Proceso (si aplica) | Qué se observó |
| --- | --- | --- |
| Integración del expediente legal por operación (trazabilidad documental) (ACT-18) | Control / Trazabilidad Documental (PRO-07) | Branches do not reconverge before their terminals |
