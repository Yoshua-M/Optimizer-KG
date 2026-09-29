# Inventario de grafo — Eneroil S.A. de C.V.
*Extracción v4 — walkthrough del grafo v3 + transcripción `Eneroil.mp3.txt`. Agosto 2026.*

---

## Nota de origen y alcance

**Fuentes:** (1) *Optimizer — Preguntas Iniciales* (entrevista interna, junio 2026) = inventario v1–v3; (2) transcripción `data/raw/Eneroil.mp3.txt` (walkthrough del fixture v3 con la informante).

**Naturaleza:** Parche de validación sobre v3, no una segunda extracción independiente. Los nodos `generated=true` de v3 que la conversación confirma pasan a `generated=false`. Lo que no encaja se reescribe (dueño, sistema, timing). Lo nuevo se agrega delgado, lado Eneroil; la logística de la empresa hermana queda como stub hasta que lleguen los procedimientos que ofreció.

**No se asignan puntajes P/C/F/R en prosa** — viven en el builder. Métricas MET-01..03 siguen siendo hipótesis (JTBD de compradores pendiente). MET-03 no se promueve: el dolor descrito es conciliación interna, no queja de cliente.

**Conteo (v4):**

| Tipo | Candidatos | vs v3 |
|---|---|---|
| Activity | 36 extraídas + 2 generadas (ACT-30, ACT-31) | +13 extraídas; ACT-24–29 graduadas |
| Process | 9 nombrados | igual (PRO-10/11 siguen sin nombrar) |
| Team | 9 | +Tesorería; TEA-04 relabelado a empresa hermana |
| Capability | 10 | +riesgo cliente, +merma |
| System | 8 | +Excel, WhatsApp ops, Portal Valero; Smartsheet demoted |
| Event | 13 | EVT-09/10 extraídos; +pago parcial, merma, cambio destino |
| CustomerJourneyStep | 8 | CJS-08 reetiquetado a merma |
| MetricDriver | 8 | MDR-01 reescrito; +merma, +constancia fiscal |
| Metric | 0 confirmados / 3 hipótesis | MET-01 gana driver de merma |

---

## Metric — sin cambio de estatus

Siguen **hipótesis** (no JTBD de compradores):

- **MET-01 — Confiabilidad de entrega.** Confirmada como preocupación (ventanas de medianoche, cambio de destino, merma vs robo). Ahora tiene driver MDR-07 (antes coverage gap).
- **MET-02 — CFDI correcto y a tiempo.** Más fuerte: se factura al cargar; fines de semana se atrasa; constancia fiscal puede bloquear el timbrado; complementos de pago.
- **MET-03 — Transparencia del estado de cuenta.** No promover. La conversación habla de conciliación interna (DSO/caja), no de clientes que no reciben estados.

KPIs internos (DSO, cartera vencida, margen/L, merma 1%) no son nodos `Metric`.

---

## Activity

Flujo demanda → cobro (dueños corregidos vs v3):

| ID | Actividad | Equipo dueño |
|---|---|---|
| ACT-01 | Recepción de solicitud del cliente (WhatsApp / correo / llamada) | Comercial |
| ACT-02 | Obtención y publicación de precios de referencia (Pemex semanal vie–vie; Valero diario 17:00; terminales Pisa / Pisayucan / Génova / Puebla; contrato Hexia) | Monitoreo y Precios |
| ACT-03 | Elaboración y envío de cotización (precio + flete + margen; piso 20 ¢/L; a veces a pérdida para no perder al cliente) | Comercial |
| ACT-04 | Confirmación del pedido por el cliente | Comercial |
| ACT-05 | Confirmación de disponibilidad de producto y logística | Empresa hermana — Planeación y operaciones |
| ACT-06 | Emisión de Orden de Compra al proveedor (corte Valero ~9:00) | Compras |
| ACT-07 | Emisión de instrucción de carga al transportista | Empresa hermana — Planeación y operaciones |
| ACT-08 | Ejecución de la carga y emisión del BOL (dispara facturación; volumen a la hora/temperatura, CFDI a 20 °C) | Proveedor (externo) |
| ACT-09 | Registro de la operación en Excel (folio, litros compra/venta, origen, unidad, fecha de cobro) | Operaciones / Facturación |
| ACT-10 | Timbrado del CFDI en SAE/ASPEL (cuando la pipa carga, no al entregar) | Facturación |
| ACT-11 | Envío del CFDI al cliente | Facturación |
| ACT-12 | Seguimiento al pago (crédito típico 3 días) | Cobranza |
| ACT-13 | Conciliación factura – estado de cuenta bancario – Excel (paguitos, FIFO a la más vieja, grupo vs estación) | Cobranza |
| ACT-14 | Registro del pago / saldo en Excel | Cobranza |
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
| ACT-23 | Gestión de relación regulatoria y reporte volumétrico (CNE / SAT) | Dirección / Cumplimiento |

Walkthrough — graduadas de v3 (`generated=false`):

| ID | Actividad | Equipo dueño |
|---|---|---|
| ACT-24 | Ejecución del prepago al proveedor (no liberan producto/crédito hasta que Eneroil paga) | Tesorería |
| ACT-25 | Transporte y entrega del producto al destino (evidencias: BOL firmado, sellos, fotos) | Empresa hermana — Planeación y operaciones |
| ACT-26 | Determinación del costo de transporte para la cotización | Comercial |
| ACT-27 | Obtención del estado de cuenta bancario / fecha de pago | Tesorería |
| ACT-28 | Consulta de disponibilidad de producto al proveedor (verbal / WhatsApp / tope Valero; sin proceso documentado) | Empresa hermana — Planeación y operaciones |
| ACT-29 | Consulta de disponibilidad logística al transportista (verbal, misma handshake) | Empresa hermana — Planeación y operaciones |

Walkthrough — nuevas (lado Eneroil, delgadas):

| ID | Actividad | Equipo dueño |
|---|---|---|
| ACT-32 | Evaluación CRE / KYC del cliente (permiso vs facturado, paraísos fiscales, cuestionario) | Calidad / Cumplimiento |
| ACT-33 | Folio y seguimiento de liberación de crédito del proveedor (Excel: no liberado / previo / liberados) | Operaciones / Facturación |
| ACT-34 | Emisión de complemento de pago (paguitos; lo hace Facturación, no la informante) | Facturación |
| ACT-35 | Emisión de nota de crédito por merma (cubre 1%; la hermana emite NC espejo a Eneroil) | Facturación |
| ACT-36 | Revisión mensual de constancia de situación fiscal | Facturación |
| ACT-38 | Cancelación / reemisión de OC por cambio de destino o unidad (control volumétrico SAT) | Compras |
| ACT-39 | Análisis de merma (stub — persona dedicada en la empresa hermana; tirillas, sellos, fotos) | Empresa hermana — Planeación y operaciones |

> ACT-19 se conserva (SGC) pero la informante: «No hay quejas. Literalmente.» La excepción real es merma → ACT-35. ACT-30 (autorización de fondos) y ACT-31 (identificar vencidas) siguen generados — ver llenado. Nexus es migración prevista, no sistema actual (no nodo).

---

## Process

| ID | Proceso | Actividades |
|---|---|---|
| PRO-01 | Monitoreo y Precios (Obtención y Envío de Precios) | ACT-02 |
| PRO-02 | Cotización al Cliente | ACT-01, ACT-03, ACT-04, ACT-26 |
| PRO-03 | Planeación y operación logística (empresa hermana) | ACT-05, ACT-07, ACT-25, ACT-28, ACT-29, ACT-39 |
| PRO-04 | Compra y Venta de Combustible | ACT-06, ACT-08, ACT-09, ACT-24, ACT-33, ACT-38 |
| PRO-05 | Facturación | ACT-10, ACT-11, ACT-34, ACT-35, ACT-36 |
| PRO-06 | Cobranza | ACT-12, ACT-13, ACT-14, ACT-15, ACT-16, ACT-17, ACT-27 |
| PRO-07 | Control / Trazabilidad Documental | ACT-18, ACT-32 |
| PRO-08 | Gestión de Quejas y No Conformidades | ACT-19 |
| PRO-09 | Auditorías internas y a proveedores | ACT-20, ACT-21 |
| PRO-10 | *(sin nombrar — esperar procedimientos SGC)* | — |
| PRO-11 | *(sin nombrar)* | — |

---

## Team (9)

| ID | Equipo |
|---|---|
| TEA-01 | Dirección General |
| TEA-02 | Monitoreo y Precios |
| TEA-03 | Comercial / Ventas |
| TEA-04 | Empresa hermana — Planeación y operaciones *(externo; Eneroil no puede operar sin este servicio)* |
| TEA-05 | Compras |
| TEA-06 | Operaciones / Facturación |
| TEA-07 | Calidad / Cumplimiento |
| TEA-08 | Cobranza *(de facto las mismas personas que Ventas y Facturación)* |
| TEA-10 | Tesorería *(Isabel; cuentas de todo el grupo)* |

---

## Capability (10)

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
| CAP-09 | Evaluación de riesgo de cliente (CRE / KYC) |
| CAP-10 | Gestión de merma (umbral 1%) |

---

## System (8)

| ID | Sistema | Uso |
|---|---|---|
| SYS-01 | Smartsheet | Mencionado en la entrevista inicial; **no** es el sistema de registro operativo |
| SYS-02 | SAE/ASPEL | Timbrado de CFDI (actual; migración a Nexus prevista, no viva) |
| SYS-03 | WhatsApp | Canal de solicitud (informal) |
| SYS-04 | Correo electrónico | Solicitud / envío de CFDI / comprobantes PDF de pago |
| SYS-05 | Banca / estado de cuenta bancario | Fuente de conciliación (Tesorería) |
| SYS-06 | Excel | Registro de operación: folio, previo, liberados, litros, cobranza |
| SYS-07 | WhatsApp (grupos de operaciones / cupo extra Valero) | Handshake verbal de disponibilidad y liberación |
| SYS-08 | Portal Valero | Precarga, cupos, control volumétrico, documentación de salida |

---

## Event (13)

| ID | Evento | Rol |
|---|---|---|
| EVT-01 | Solicitud de carga recibida | Demanda |
| EVT-02 | Cotización enviada | Hito |
| EVT-03 | Pedido confirmado por cliente | Hito |
| EVT-04 | Orden de Compra emitida | Hito |
| EVT-05 | Carga ejecutada / BOL emitido | Hito **y disparador de facturación** |
| EVT-06 | CFDI timbrado (factura emitida) | Realización parcial de valor |
| EVT-07 | Pago recibido (cobro) | Milestone (acreditado, no conciliado) |
| EVT-08 | Factura vencida | Excepción / riesgo |
| EVT-09 | Entrega confirmada en destino | Realización de valor (física) — empresa hermana |
| EVT-10 | Cobro conciliado (valor asegurado) | **Terminal** |
| EVT-11 | Pago parcial recibido | Excepción / paguitos |
| EVT-12 | Merma fuera de umbral (1%) | Excepción (sustituye «queja» como path real) |
| EVT-13 | Cambio de destino / unidad a media orden | Excepción (control volumétrico) |

---

## CustomerJourneyStep (8 — inferidos)

| ID | Momento del cliente |
|---|---|
| CJS-01 | Solicita cotización |
| CJS-02 | Recibe y evalúa cotización |
| CJS-03 | Confirma pedido |
| CJS-04 | Recibe la entrega de combustible |
| CJS-05 | Recibe el CFDI *(puede preceder la entrega física: se timbra al cargar)* |
| CJS-06 | Recibe el estado de cuenta |
| CJS-07 | Paga |
| CJS-08 | Reclamo por merma / nota de crédito |

---

## MetricDriver (8)

| ID | Driver | Métrica hipotética asociada |
|---|---|---|
| MDR-01 | Puntualidad de emisión de factura **desde la carga** (no desde la entrega; se cae en fines de semana) | M?-02 |
| MDR-02 | Exactitud de datos fiscales del cliente (catálogo validado) | M?-02 |
| MDR-03 | Disciplina de seguimiento diario a cartera | M?-03 *(interno / cobro; no promover)* |
| MDR-04 | Existencia y aplicación de política de crédito y cobranza | M?-03 |
| MDR-05 | Puntualidad de conciliación (diaria antes de 10am) | M?-03 |
| MDR-06 | Grado de integración de sistemas (Excel–SAE/ASPEL–banco) | M?-02, M?-03 |
| MDR-07 | Control de merma (umbral 1% vs merma física vs robo) | M?-01 |
| MDR-08 | Vigencia de constancia de situación fiscal (mensual) | M?-02 |

---

## Relaciones tipificadas (extraíbles hoy)

**Team —[PERFORMS]→ Activity:** columna dueño.

**Activity —[PART_OF]→ Process:** tabla Process.

**Activity —[PRECEDES]→ Activity** (cadena demanda→cobro):
`ACT-01 → ACT-03 → ACT-04 → ACT-05 → ACT-06 → ACT-07 → ACT-08 → ACT-09 → ACT-10 → ACT-11 → ACT-12 → ACT-13 → ACT-14`
Prepago: `ACT-06 → ACT-24 → ACT-33 → ACT-08`. Entrega **en paralelo** a facturación: `ACT-08 → ACT-25` (ya **no** `ACT-25 → ACT-10`). Factura al cargar: `ACT-08 → ACT-10`. Excepción cobranza: `ACT-12 → ACT-15 → ACT-16 → ACT-17`. ACT-02 y ACT-26 alimentan ACT-03. ACT-28/29 → ACT-05. ACT-27 → ACT-13. ACT-32 → ACT-04. ACT-36 → ACT-10. ACT-38 ramifica desde ACT-06.

**Activity —[USES_SYSTEM]→ System:** ACT-01→SYS-03/04; ACT-09/13/14/16/33→SYS-06; ACT-10→SYS-02; ACT-11/16→SYS-04; ACT-13/27→SYS-05; ACT-28→SYS-07/08.

**Activity —[INVOLVES_EVENT]→ Event:** ACT-01→EVT-01; ACT-03→EVT-02; ACT-04→EVT-03; ACT-06→EVT-04; ACT-08→EVT-05; ACT-10→EVT-06; ACT-14→EVT-07; ACT-15↔EVT-08; ACT-25→EVT-09; ACT-13→EVT-10; ACT-34→EVT-11; ACT-35→EVT-12; ACT-38→EVT-13.

---

# Llenado generado (brechas que quedan)

Todo lo anterior es extracción / walkthrough (`generated=false`). De aquí: `generated=true`.

## Paso 1 — cierre estructural mecánico

### SUPPORTS / OWNS

Igual que v3 más: ACT-26→CAP-02; ACT-24/33/38→CAP-04; ACT-25/28/29/39→CAP-03; ACT-27→CAP-06; ACT-32→CAP-09; ACT-34/35/36→CAP-05; ACT-35/39→CAP-10. TEA-04→PRO-03, CAP-03, CAP-10. TEA-07→CAP-09. TEA-10 no posee proceso (feeder a PRO-06).

## Paso 2–5 — lo que se graduó

ACT-24, ACT-25, ACT-26, ACT-27, ACT-28, ACT-29, EVT-09, EVT-10: **ya no son generated**. Cadena de facturación reescrita (carga, no entrega). MET-01..03 siguen abducción `conf≤0.5`. CJS siguen `inferred`. TOUCHES ACT-19→CJS-08 se debilita (`conf=0.25`); ACT-35→CJS-08 `conf=0.75`.

### AFFECTS (nuevos extraídos, still generated flags on abduction metrics)

ACT-10→MDR-01; ACT-36→MDR-08; ACT-35/ACT-39→MDR-07; ACT-05/ACT-25→MET-01; ACT-16→MET-03 (sigue débil). MDR-07→MET-01. MDR-08→MET-02.

## Paso 7 — feeders que siguen generated

| ID | label | conf | flag | dueño |
|---|---|---|---|---|
| ACT-30 | Autorización de liberación de fondos para prepago | 0.5 | tier_bajo | Tesorería (ya no Dirección; dueño aún incierto) |
| ACT-31 | Identificación de facturas vencidas | 0.5 | contested_external | Cobranza |

PRECEDES generated que quedan: ACT-30→ACT-24; ACT-31→ACT-15.

## Paso 6 / 8 — scores

Ver builder. ACT-19 P bajado. ACT-25 ahora tiene C/R (evidencia de entrega). ACT-26–29 ya no `void_on_collapse`. ACT-30 sigue `tier_bajo` simulado. ACT-08, ACT-34, ACT-35, ACT-36, ACT-38 puntuados por el walkthrough.

## Handoff

- Esperar procedimientos SGC + logística de la hermana (PRO-10/11, subgrafo merma completo).
- Sin Supplier / Product / Regulator. Hexia / Valero / Pemex / Atosa = sistemas o equipos externos, no tipos nuevos.
- Ignorar el pitch de Optimizer en la transcripción.
- Nexus = nota, no nodo.
