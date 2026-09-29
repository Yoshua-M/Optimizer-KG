## Check 1 — Alcanzabilidad de valor

| Severidad | Nodos | Descripción |
| --- | --- | --- |
| error | PRO-03 (Generación y seguimiento de pedidos (corregido F2 — antes "Planeación de la Operación"; "Planeación" es equipo de la empresa de logística externa)) | Process with CONTRIBUTES_TO has no value_realization event |
| error | PRO-05 (Facturación) | Process with CONTRIBUTES_TO has no value_realization event |
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
