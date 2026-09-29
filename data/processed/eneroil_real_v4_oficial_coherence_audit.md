## Check 1 — Alcanzabilidad de valor

| Severidad | Nodos | Descripción |
| --- | --- | --- |
| error | PRO-03 (Generación y seguimiento de pedidos) | Process with CONTRIBUTES_TO has no value_realization event (no REALIZES path and no produce INVOLVES_EVENT) |
| error | PRO-05 (Facturación) | Process with CONTRIBUTES_TO has no value_realization event (no REALIZES path and no produce INVOLVES_EVENT) |
| error | ACT-14 (Registro del pago / saldo en Smartsheet) | Activity cannot reach its process realization event |
| error | ACT-15 (Contacto al cliente por factura vencida) | Activity cannot reach its process realization event |
| error | ACT-16 (Generación y envío del estado de cuenta del cliente) | Activity cannot reach its process realization event |
| error | ACT-17 (Escalamiento a Dirección por cobro vencido) | Activity cannot reach its process realization event |
| error | ACT-31 (Identificación de facturas vencidas) | Activity cannot reach its process realization event |

## Check 4 — Activities completamente desconectadas

| Severidad | Nodos | Descripción |
| --- | --- | --- |
| revisar | ACT-19 (Gestión de quejas y no conformidades) | Activity isolated on PRECEDES |
| revisar | ACT-21 (Auditorías a proveedores) | Activity isolated on PRECEDES |

## Check 5 — Ramas sin reconvergencia

| Severidad | Nodos | Descripción |
| --- | --- | --- |
| revisar | ACT-03 (Elaboración y envío de cotización) | Branches do not reconverge before their terminals |
| revisar | ACT-04 (Confirmación del pedido por el cliente) | Branches do not reconverge before their terminals |
| revisar | ACT-06 (Emisión de Orden de Compra al proveedor (con prepago)) | Branches do not reconverge before their terminals |
| revisar | ACT-08 (Ejecución de la carga y emisión del BOL) | Branches do not reconverge before their terminals |
| revisar | ACT-10 (Timbrado del CFDI en SAE/ASPEL) | Branches do not reconverge before their terminals |
| revisar | ACT-11 (Envío del CFDI al cliente) | Branches do not reconverge before their terminals |
| revisar | ACT-13 (Conciliación factura – estado de cuenta bancario – Smartsheet) | Branches do not reconverge before their terminals |
| revisar | ACT-14 (Registro del pago / saldo en Smartsheet) | Branches do not reconverge before their terminals |
| revisar | ACT-18 (Integración del expediente legal por operación (trazabilidad documental)) | Branches do not reconverge before their terminals |
| revisar | ACT-33 (Recepción del BOL de la empresa de logística) | Branches do not reconverge before their terminals |

## C1 — Cobertura de intención

| Severidad | Nodos | Descripción |
| --- | --- | --- |
| error | ACT-01 (Recepción de solicitud del cliente (WhatsApp / correo / llamada)) | Activity has no Intent (own PURSUES or inherited via Process) |
| error | ACT-02 (Obtención y publicación diaria de precios de referencia (Pemex, Valero, Repsol)) | Activity has no Intent (own PURSUES or inherited via Process) |
| error | ACT-03 (Elaboración y envío de cotización) | Activity has no Intent (own PURSUES or inherited via Process) |
| error | ACT-04 (Confirmación del pedido por el cliente) | Activity has no Intent (own PURSUES or inherited via Process) |
| error | ACT-05 (Confirmación de disponibilidad de producto) | Activity has no Intent (own PURSUES or inherited via Process) |
| error | ACT-06 (Emisión de Orden de Compra al proveedor (con prepago)) | Activity has no Intent (own PURSUES or inherited via Process) |
| error | ACT-07 (Envío del pedido/folio a la empresa de logística) | Activity has no Intent (own PURSUES or inherited via Process) |
| error | ACT-08 (Ejecución de la carga y emisión del BOL) | Activity has no Intent (own PURSUES or inherited via Process) |
| error | ACT-09 (Registro de la operación en Smartsheet) | Activity has no Intent (own PURSUES or inherited via Process) |
| error | ACT-10 (Timbrado del CFDI en SAE/ASPEL) | Activity has no Intent (own PURSUES or inherited via Process) |
| error | ACT-11 (Envío del CFDI al cliente) | Activity has no Intent (own PURSUES or inherited via Process) |
| error | ACT-12 (Seguimiento al pago) | Activity has no Intent (own PURSUES or inherited via Process) |
| error | ACT-13 (Conciliación factura – estado de cuenta bancario – Smartsheet) | Activity has no Intent (own PURSUES or inherited via Process) |
| error | ACT-14 (Registro del pago / saldo en Smartsheet) | Activity has no Intent (own PURSUES or inherited via Process) |
| error | ACT-15 (Contacto al cliente por factura vencida) | Activity has no Intent (own PURSUES or inherited via Process) |
| error | ACT-16 (Generación y envío del estado de cuenta del cliente) | Activity has no Intent (own PURSUES or inherited via Process) |
| error | ACT-17 (Escalamiento a Dirección por cobro vencido) | Activity has no Intent (own PURSUES or inherited via Process) |
| error | ACT-18 (Integración del expediente legal por operación (trazabilidad documental)) | Activity has no Intent (own PURSUES or inherited via Process) |
| error | ACT-19 (Gestión de quejas y no conformidades) | Activity has no Intent (own PURSUES or inherited via Process) |
| error | ACT-20 (Auditorías internas) | Activity has no Intent (own PURSUES or inherited via Process) |
| error | ACT-21 (Auditorías a proveedores) | Activity has no Intent (own PURSUES or inherited via Process) |
| error | ACT-22 (Aprobación de proveedores) | Activity has no Intent (own PURSUES or inherited via Process) |
| error | ACT-23 (Gestión de relación regulatoria y reporte volumétrico (CNE)) | Activity has no Intent (own PURSUES or inherited via Process) |
| error | ACT-24 (Ejecución del prepago al proveedor) | Activity has no Intent (own PURSUES or inherited via Process) |
| error | ACT-32 (Monitoreo del estado de liberación de crédito) | Activity has no Intent (own PURSUES or inherited via Process) |
| error | ACT-33 (Recepción del BOL de la empresa de logística) | Activity has no Intent (own PURSUES or inherited via Process) |
| error | ACT-26 (Determinación del costo de transporte para la cotización) | Activity has no Intent (own PURSUES or inherited via Process) |
| error | ACT-27 (Obtención del estado de cuenta bancario) | Activity has no Intent (own PURSUES or inherited via Process) |
| error | ACT-28 (Consulta informal de disponibilidad a la empresa de logística) | Activity has no Intent (own PURSUES or inherited via Process) |
| error | ACT-30 (Autorización de liberación de fondos para prepago) | Activity has no Intent (own PURSUES or inherited via Process) |
| error | ACT-31 (Identificación de facturas vencidas) | Activity has no Intent (own PURSUES or inherited via Process) |

## C3 — Nivel en la escalera

| Severidad | Nodos | Descripción |
| --- | --- | --- |
| info |  | No activities on ladder N1–N4 (none have Intent yet) |

## C4 — Alineación intención–efecto

| Severidad | Nodos | Descripción |
| --- | --- | --- |
| revisar | ACT-05 (Confirmación de disponibilidad de producto), MET-01 (Confiabilidad de entrega (producto / volumen / destino / fecha)) | Has effect on Metric but no Intent that SERVES it |
| revisar | ACT-10 (Timbrado del CFDI en SAE/ASPEL), MET-02 (CFDI correcto y a tiempo) | Has effect on Metric but no Intent that SERVES it |
| revisar | ACT-16 (Generación y envío del estado de cuenta del cliente), MET-03 (Transparencia / exactitud del estado de cuenta) | Has effect on Metric but no Intent that SERVES it |
| revisar | MET-01 (Confiabilidad de entrega (producto / volumen / destino / fecha)) | Metric that nobody pursues (no Intent.SERVES) |
| revisar | MET-02 (CFDI correcto y a tiempo) | Metric that nobody pursues (no Intent.SERVES) |
| revisar | MET-03 (Transparencia / exactitud del estado de cuenta) | Metric that nobody pursues (no Intent.SERVES) |
