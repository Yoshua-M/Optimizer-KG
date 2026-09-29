# OIL TRADE SIMULATION — Inventario de Nodos y Relaciones v3
## Grafo de Conocimiento | Simulación con misconceptions | Junio 2026

---

> **Misconceptions incorporados:**
> - **M-A** — La empresa invierte en estética y presentación de flota como señal de calidad, aunque ningún cliente industrial lo valora.
> - **M-D** — Capas de aprobación interna para pedidos estándar generan fricción y retraso sin reducir riesgo real.
> - **M-3** — La empresa cree que las visitas comerciales periódicas son el driver principal de retención; los clientes la juzgan por su respuesta en momentos de falla.

---

# BLOQUE 1 — Nodos

---

## 1.1 Metric (5 nodos)

| ID | Nombre de la Métrica | Definición operacional | JTBD del cliente |
|----|----------------------|------------------------|------------------|
| M-01 | Confiabilidad de entrega en ventana comprometida | % de entregas dentro de ±30 min del horario comprometido | El cliente necesita planear su operación alrededor de la entrega |
| M-02 | Tiempo de respuesta ante falla de suministro | Horas desde detección interna de falla hasta notificación al cliente con alternativa | El cliente juzga la relación por lo que pasa cuando algo sale mal |
| M-03 | Exactitud de volumen entregado | % de entregas con diferencia entre pedido y recibido dentro de tolerancia (<0.5%) | El cliente gestiona su propio inventario — una entrega corta fuerza una compra de emergencia |
| M-04 | Costo total de abastecimiento predecible | Costo por litro del período (precio + costo financiero de crédito + overhead administrativo) vs. lo acordado | El cliente necesita precio estable para fijar sus propios precios |
| M-05 | Ausencia de fricción administrativa | Compuesto: tiempo de confirmación de pedido + tasa de errores en factura + incidentes documentales que requirieron intervención del cliente | El cliente quiere que pedir combustible consuma el mínimo de su propio equipo |

---

## 1.2 MetricDriver (13 nodos)

| ID | Métrica padre | Driver | Descripción operacional |
|----|---------------|--------|-------------------------|
| MD-01 | M-01 | Disponibilidad de flota de pipas en turno | Nº de unidades disponibles vs. requeridas por ruta y turno |
| MD-02 | M-01 | Tiempo de carga en terminal TAR | Minutos desde llegada a terminal hasta salida con carga completa |
| MD-03 | M-01 | Precisión de planeación de ruta | Holgura entre tiempo estimado y tiempo real de llegada a sitio cliente |
| MD-04 | M-01 | Disponibilidad de producto en terminal | Días de inventario disponible en TAR asignada |
| MD-05 | M-02 | Tiempo de detección interna de falla | Minutos desde que ocurre la falla hasta que el equipo la identifica y escala |
| MD-06 | M-02 | Disponibilidad de alternativas de suministro | Nº de fuentes o rutas alternativas confirmadas y operativas |
| MD-07 | M-02 | Velocidad de autorización de solución de contingencia | Tiempo desde propuesta de alternativa hasta autorización interna para ejecutarla |
| MD-08 | M-03 | Precisión de aforo en carga | Desviación promedio entre litros aforados al cargar vs. aforados al entregar |
| MD-09 | M-03 | Tasa de incidentes de sello o documentación de traslado | % de cargas con discrepancia documental detectada en sitio del cliente |
| MD-10 | M-04 | Exactitud de facturación | % de facturas emitidas sin error de precio, volumen o condición de crédito |
| MD-11 | M-04 | Estabilidad del precio acordado | Variaciones de precio no comunicadas al cliente con anticipación |
| MD-12 | M-05 | Tiempo de confirmación de pedido | Horas desde recepción hasta envío de confirmación con detalle de entrega |
| MD-13 | M-05 | Tasa de pedidos con intervención manual del cliente | % de pedidos que requirieron gestión adicional del cliente para avanzar |

---

## 1.3 CustomerJourneyStep (7 nodos)

| ID | Nombre del paso | Qué experimenta el cliente |
|----|-----------------|---------------------------|
| CJS-01 | Evaluación de proveedor alternativo a PEMEX | El cliente considera cambiar o añadir un proveedor; evalúa reputación, cobertura y referencias |
| CJS-02 | Negociación y cierre de contrato | El cliente negocia precio, volumen, crédito y condiciones; forma su primera impresión de cómo trabaja la comercializadora |
| CJS-03 | Primer pedido y entrega | Momento de verdad: el cliente experimenta por primera vez el proceso real de pedido y recepción |
| CJS-04 | Operación recurrente de suministro | Ciclo continuo donde el cliente calibra confiabilidad, exactitud y facilidad de operar con la comercializadora |
| CJS-05 | Experiencia de falla o retraso | El cliente enfrenta una interrupción; este momento define si confía en la comercializadora como socio de largo plazo |
| CJS-06 | Revisión comercial periódica | El cliente evalúa el desempeño del período; decide si está satisfecho o empieza a explorar alternativas |
| CJS-07 | Renovación o expansión del contrato | El cliente toma la decisión de continuar, ampliar o terminar la relación |

---

## 1.4 Process (5 nodos)

| ID | Nombre del Proceso | Descripción |
|----|--------------------|-------------|
| P-01 | Gestión de Pedidos y Entregas | Ciclo completo desde recepción del pedido hasta entrega confirmada y facturación |
| P-02 | Atención de Fallas y Contingencias | Detección, evaluación y resolución de interrupciones de suministro con notificación proactiva |
| P-03 | Adquisición de Clientes | Ciclo de prospección, evaluación crediticia, propuesta y contratación de clientes nuevos |
| P-04 | Retención y Renovación de Contratos | Seguimiento de contratos activos, revisión comercial y cierre de renovaciones o expansiones |
| P-05 | Gestión de Crédito Comercial | Evaluación, autorización y ajuste de condiciones crediticias para clientes activos y prospectos |

---

## 1.5 Activity (70 nodos)

| ID | Proceso | Nombre de la Actividad | Área(s) Porter | Frecuencia |
|----|---------|------------------------|----------------|------------|
| A-01 | P-01 | Recepción y registro del pedido del cliente | Marketing y Ventas, Logística Externa | Diaria |
| A-02 | P-01 | Validación del pedido contra contrato activo y condiciones vigentes | Marketing y Ventas, Núcleo de Gobernanza | Diaria |
| A-03 | P-01 | Autorización de crédito para el despacho | Núcleo de Gobernanza | Por pedido |
| A-04 | P-01 | Verificación de disponibilidad de producto en TAR asignada | Abastecimiento, Logística Interna | Diaria |
| A-05 | P-01 | Planeación de ruta con ventana de entrega comprometida | Logística Externa | Diaria |
| A-06 | P-01 | Programación de ventana de carga en terminal TAR | Logística Interna, Logística Externa | Diaria |
| A-07 | P-01 | Muestreo y prueba NOM-016 del lote a cargar | Operaciones, Núcleo de Gobernanza | Por carga |
| A-08 | P-01 | Supervisión de carga: aforo, sellos y documentación de traslado | Logística Interna, Operaciones | Por carga |
| A-09 | P-01 | Asignación de operador y briefing de ruta | Logística Externa, Operaciones | Por entrega |
| A-10 | P-01 | Monitoreo de ruta en tiempo real (GPS y comunicación con operador) | Logística Externa, Desarrollo Tecnológico | Tiempo real |
| A-11 | P-01 | Entrega en sitio cliente: descarga, aforo final y firma de remisión | Logística Externa | Por entrega |
| A-12 | P-01 | Verificación de aforo final y cierre de remisión con volumen real | Logística Externa, Operaciones | Por entrega |
| A-13 | P-01 | Generación de factura CFDI post-entrega con condiciones del contrato | Núcleo de Gobernanza, Marketing y Ventas | Por entrega |
| A-14 | P-01 | Envío de confirmación de pedido al cliente con detalle de entrega | Marketing y Ventas | Por pedido |
| A-15 | P-01 | Envío de estado de cuenta del período sin ajustes pendientes | Núcleo de Gobernanza | Mensual |
| A-16 | P-02 | Detección de falla de suministro activa (TAR, ruta o documentación) | Logística Externa, Abastecimiento | Según evento |
| A-17 | P-02 | Evaluación de opciones de contingencia disponibles | Abastecimiento, Núcleo de Gobernanza | Según evento |
| A-18 | P-02 | Notificación proactiva al cliente con alternativa concreta y tiempo estimado | Marketing y Ventas, Servicio Postventa | Según evento |
| A-19 | P-02 | Coordinación y ejecución de solución alternativa de suministro | Logística Externa, Abastecimiento | Según evento |
| A-20 | P-03 | Calificación y validación del prospecto | Marketing y Ventas | Continua |
| A-21 | P-03 | Evaluación de perfil crediticio del prospecto | Núcleo de Gobernanza | Por prospecto |
| A-22 | P-03 | Elaboración de propuesta comercial personalizada | Marketing y Ventas | Por prospecto |
| A-23 | P-03 | Presentación y negociación de condiciones comerciales | Marketing y Ventas | Por prospecto |
| A-24 | P-03 | Documentación y alta del cliente en sistema | Marketing y Ventas, Núcleo de Gobernanza | Por cliente nuevo |
| A-25 | P-03 | Firma de contrato de suministro | Marketing y Ventas, Núcleo de Gobernanza | Por cliente nuevo |
| A-26 | P-04 | Identificación de contratos próximos a vencer | Servicio Postventa, Núcleo de Gobernanza | Mensual |
| A-27 | P-04 | Revisión del historial operativo del cliente (entregas, incidentes, facturas) | Servicio Postventa | Por cliente |
| A-28 | P-04 | Revisión comercial con cliente: desempeño del período y satisfacción | Servicio Postventa, Marketing y Ventas | Trimestral |
| A-29 | P-04 | Negociación de condiciones de renovación o expansión | Marketing y Ventas | Por contrato |
| A-30 | P-04 | Firma de renovación o expansión de contrato | Marketing y Ventas, Núcleo de Gobernanza | Por contrato |
| A-31 | P-05 | Recepción y registro de solicitud de ajuste de crédito | Núcleo de Gobernanza, Marketing y Ventas | Según evento |
| A-32 | P-05 | Revisión de historial de pagos y comportamiento crediticio del cliente | Núcleo de Gobernanza | Según evento |
| A-33 | P-05 | Autorización o ajuste de condiciones crediticias | Núcleo de Gobernanza | Según evento |
| A-34 | P-05 | Notificación al cliente de condiciones crediticias actualizadas | Marketing y Ventas, Núcleo de Gobernanza | Según evento |
| A-35 | — | Gestión de vigencia y renovación de permisos CRE y SCT | Núcleo de Gobernanza | Mensual |
| A-36 | — | Administración y renovación de líneas de crédito bancarias | Núcleo de Gobernanza | Trimestral |
| A-37 | — | Cierre contable mensual y conciliación de cuentas por cobrar | Núcleo de Gobernanza | Mensual |
| A-38 | — | Gestión y renovación de seguros de flota y carga | Núcleo de Gobernanza | Anual |
| A-39 | — | Definición y actualización de política de crédito comercial | Núcleo de Gobernanza | Semestral |
| A-40 | — | Capacitación operativa y certificación de operadores de pipa | Gestión de RRHH | Según incorporación |
| A-41 | — | Reclutamiento y selección de operadores con licencia federal de materiales peligrosos | Gestión de RRHH | Según vacante |
| A-42 | — | Evaluación de desempeño de operadores y asignación de rutas críticas | Gestión de RRHH, Logística Externa | Trimestral |
| A-43 | — | Administración y mantenimiento del sistema de pedidos y plataforma GPS | Desarrollo Tecnológico | Continua |
| A-44 | — | Mantenimiento y soporte del ERP y portales regulatorios (CRE, SAT) | Desarrollo Tecnológico | Continua |
| A-45 | — | Gestión de integraciones entre GPS, sistema de pedidos y ERP | Desarrollo Tecnológico | Continua |
| A-46 | — | Negociación y contratación de cupo de combustible con PEMEX TI | Abastecimiento | Mensual |
| A-47 | — | Registro y pre-calificación de fuentes alternativas de suministro | Abastecimiento | Trimestral |
| A-48 | — | Seguimiento y conciliación de facturas de proveedores de combustible | Abastecimiento | Mensual |
| A-49 | — | Control de inventario de producto en tránsito entre TAR y clientes | Logística Interna | Diaria |
| A-50 | — | Gestión de diferencias de aforo y reclamaciones ante PEMEX TI | Logística Interna, Abastecimiento | Según evento |
| A-51 | — | Mantenimiento preventivo y correctivo de flota de pipas | Operaciones | Mensual |
| A-52 | — | Gestión de stock de refacciones críticas para flota | Operaciones | Mensual |
| A-53 | — | Gestión de incidentes de seguridad vial y reporte ASEA | Operaciones, Núcleo de Gobernanza | Según evento |
| A-54 | — | Monitoreo de precios rack PEMEX e IEPS por terminal y período | Marketing y Ventas | Diaria |
| A-55 | — | Administración del CRM y base de datos de clientes y prospectos | Marketing y Ventas, Desarrollo Tecnológico | Continua |
| A-56 | — | Análisis de rentabilidad por cliente, producto y corredor | Marketing y Ventas, Núcleo de Gobernanza | Mensual |
| A-57 | — | Seguimiento y cierre formal de incidencias abiertas con clientes | Servicio Postventa | Semanal |
| A-58 | — | Encuesta de satisfacción post-entrega a clientes activos | Servicio Postventa | Mensual |
| A-59 | — | Inspección semanal de presentación y limpieza de flota de pipas | Operaciones, Logística Externa | Semanal |
| A-60 | — | Programa "operador del mes" con criterios de imagen y presentación personal | Gestión de RRHH | Mensual |
| A-61 | — | Diseño y producción periódica de uniformes e imagen corporativa para flota | Gestión de RRHH, Marketing y Ventas | Anual |
| A-62 | — | Proceso de aprobación multinivel para pedidos estándar de clientes activos | Núcleo de Gobernanza | Por pedido |
| A-63 | — | Reunión diaria de liberación de despachos con gerencia | Núcleo de Gobernanza, Logística Externa | Diaria |
| A-64 | — | Generación de reporte diario de pedidos pendientes de autorización para gerencia | Núcleo de Gobernanza | Diaria |
| A-65 | — | Visita de cortesía trimestral al cliente sin agenda operativa | Servicio Postventa, Marketing y Ventas | Trimestral |
| A-66 | — | Elaboración de presentación trimestral de resultados para clientes | Marketing y Ventas | Trimestral |
| A-67 | — | Programa de atenciones y regalos a clientes en fechas especiales | Marketing y Ventas, Servicio Postventa | Según fecha |
| A-68 | — | Elaboración de reporte mensual de desempeño interno para dirección | Núcleo de Gobernanza | Mensual |
| A-69 | — | Actualización manual de bitácora de rutas en hoja de cálculo | Logística Externa | Diaria |
| A-70 | — | Proceso de cotización formal para clientes con contrato marco vigente | Marketing y Ventas | Según evento |

---

## 1.6 Team (9 nodos — Áreas Porter)

| ID | Área Porter | Rol en la operación |
|----|-------------|------------------------|
| T-01 | Núcleo de Gobernanza | Dirección general, finanzas, legal, compliance, riesgos, permisos CRE/SCT y relaciones regulatorias |
| T-02 | Gestión de RRHH | Reclutamiento, certificación, capacitación y evaluación del capital humano operativo y comercial |
| T-03 | Desarrollo Tecnológico | Administración de sistemas (ERP, GPS, portales CRE/SAT), integraciones y soporte técnico |
| T-04 | Abastecimiento | Negociación de cupo con PEMEX TI, proveedores alternativos y conciliación de facturas de suministro |
| T-05 | Logística Interna | Interfaz con terminales TAR: programación de cargas, control de inventario en tránsito y diferencias de aforo |
| T-06 | Operaciones | Control de calidad NOM-016, mantenimiento de flota, gestión de refacciones y seguridad operativa ASEA |
| T-07 | Logística Externa | Planeación de rutas, asignación de operadores, monitoreo GPS y gestión del último kilómetro |
| T-08 | Marketing y Ventas | Inteligencia de mercado, prospección, negociación, gestión de cuentas, CRM y análisis de rentabilidad |
| T-09 | Servicio Postventa | Atención de incidencias, revisiones comerciales, retención y gestión de satisfacción del cliente |

---

## 1.7 Capability (9 nodos — Áreas Porter)

| ID | Capacidad | Descripción para la operación |
|----|-----------|----------------------------------|
| CAP-01 | Gobernanza Corporativa y Gestión Regulatoria | Operar con permisos vigentes, finanzas sanas y gestión de riesgos integrada |
| CAP-02 | Gestión de Talento Operativo | Reclutar, certificar y retener operadores con licencia federal de materiales peligrosos |
| CAP-03 | Capacidades Digitales y Trazabilidad | Operar sistemas integrados que dan visibilidad en tiempo real del ciclo pedido-entrega-cobro |
| CAP-04 | Gestión de Abastecimiento y Suministro | Asegurar volumen competitivo en terminales PEMEX y fuentes alternativas con mínima interrupción |
| CAP-05 | Control de Inventario y Operaciones en Terminal | Gestionar la interfaz TAR con precisión: cargas, aforo, calidad y documentación en origen |
| CAP-06 | Excelencia Operativa y Seguridad de Flota | Mantener la flota disponible y operar sin incidentes de seguridad ni calidad |
| CAP-07 | Distribución y Entrega Confiable | Entregar combustible en la ventana comprometida, en volumen correcto y con trazabilidad completa |
| CAP-08 | Inteligencia Comercial y Gestión de Clientes | Identificar oportunidades, adquirir clientes y gestionar el portafolio comercial con datos |
| CAP-09 | Gestión de Experiencia del Cliente | Resolver incidencias, sostener relaciones de largo plazo y convertir clientes en promotores |

---

## 1.8 System (8 nodos)

| ID | Sistema / Herramienta | Función en la operación |
|----|-----------------------|-------------------------|
| S-01 | Sistema de Pedidos y Remisiones | Captura de pedidos, generación de remisiones y trazabilidad de entregas |
| S-02 | GPS / Plataforma de Rastreo de Flota | Monitoreo satelital de pipas en ruta: posición, alertas y bitácora de ruta |
| S-03 | ERP / Sistema Contable y de Facturación | Gestión financiera, facturación CFDI, cobranza, tesorería y conciliación contable |
| S-04 | Portal OPE-CRE | Plataforma oficial para reportes regulatorios y gestión de permisos ante la CRE |
| S-05 | Portal SAT / CFDI | Emisión de facturas electrónicas, declaraciones de IEPS y reportes fiscales |
| S-06 | Sistema de Control de Calidad NOM-016 | Registro de muestras, resultados de pruebas y trazabilidad de lotes de producto |
| S-07 | CRM / Base de Datos de Clientes | Gestión de cuentas, historial de clientes, pipeline comercial y seguimiento de contratos |
| S-08 | Sistema de Gestión de Mantenimiento | Programación de mantenimiento preventivo, historial de unidades y gestión de refacciones |

---

## 1.9 Event (12 nodos)

| ID | Nombre del Evento | Tipo | Métrica que ancora | Qué representa |
|----|-------------------|------|-------------------|----------------|
| EV-D01 | Pedido de combustible recibido de cliente activo | Demanda | M-01, M-03, M-04, M-05 | El cliente solicita volumen concreto; dispara el ciclo de autorización-logística-entrega |
| EV-D02 | Solicitud de onboarding de cliente nuevo | Demanda | M-01, M-04, M-05 | Prospecto calificado solicita operar; dispara el ciclo de adquisición |
| EV-D03 | Falla de suministro detectada o reportada | Demanda | M-02 | Interrupción activa en el ciclo de entrega; dispara el protocolo de contingencia |
| EV-D04 | Solicitud de ajuste de crédito o condiciones comerciales | Demanda | M-04, M-05 | El cliente solicita revisar condiciones; dispara la revisión crediticia |
| EV-D05 | Contrato próximo a vencer — cliente en riesgo | Demanda | M-01, M-02, M-04 | Vencimiento detectado; dispara el ciclo de retención |
| EV-V01 | Entrega realizada dentro de ventana comprometida | Entrega de Valor | M-01 | El cliente recibió combustible en el horario acordado |
| EV-V02 | Cliente notificado con alternativa antes de afectar su operación | Entrega de Valor | M-02 | La comercializadora respondió a la falla antes de que el cliente lo descubriera |
| EV-V03 | Volumen entregado dentro de tolerancia acordada | Entrega de Valor | M-03 | El cliente recibió exactamente lo que pidió |
| EV-V04 | Período cerrado sin sorpresas en costo para el cliente | Entrega de Valor | M-04 | El cliente cierra su período sin ajustes inesperados |
| EV-V05 | Pedido confirmado y documentado sin intervención del cliente | Entrega de Valor | M-05 | El cliente hizo el pedido y recibió confirmación sin hacer seguimiento |
| EV-V06 | Contrato firmado con cliente nuevo | Entrega de Valor | M-01, M-04, M-05 | Cierre del ciclo de adquisición |
| EV-V07 | Renovación o expansión de contrato confirmada | Entrega de Valor | M-01, M-02, M-04 | El cliente decidió continuar — consolidación de la relación |

---

# BLOQUE 2 — Relaciones

---

## 2.1 Activity —[AFFECTS]→ Metric (28 relaciones)

| Actividad | Métrica | Fuerza causal |
|-----------|---------|---------------|
| A-03 | M-05 | Alta: la velocidad de autorización determina si el cliente recibe confirmación sin tener que llamar |
| A-03 | M-01 | Media: sin crédito autorizado el pedido no avanza a logística — puede romper la ventana comprometida |
| A-04 | M-01 | Alta: sin producto disponible en TAR la ventana comprometida colapsa |
| A-05 | M-01 | Alta: la planeación define si la ventana es alcanzable dado tráfico y distancia real |
| A-06 | M-01 | Alta: la programación de ventana de carga es cuello de botella frecuente para el cumplimiento de horario |
| A-07 | M-03 | Crítica: una falla NOM-016 retiene el lote y afecta el volumen entregable |
| A-08 | M-03 | Alta: el aforo en carga es el origen del volumen — errores aquí se propagan a la entrega |
| A-08 | M-04 | Alta: documentación incorrecta genera discrepancias en factura y sorpresas de costo |
| A-09 | M-01 | Media: el briefing afecta la capacidad del operador de cumplir la ventana con variaciones en ruta |
| A-10 | M-01 | Alta: el monitoreo GPS permite detectar y corregir desvíos antes de que rompan la ventana |
| A-10 | M-02 | Alta: es el mecanismo principal para detectar fallas en ruta antes de que el cliente las sienta |
| A-11 | M-01 | Crítica: define si la ventana se cumplió o no |
| A-11 | M-04 | Alta: errores en remisión generan discrepancias en factura |
| A-12 | M-03 | Crítica: único control antes de cerrar la entrega — define exactitud del volumen |
| A-13 | M-04 | Alta: la factura es el documento que el cliente usa para validar su costo |
| A-13 | M-05 | Alta: una factura con error requiere intervención del cliente — fricción directa |
| A-14 | M-05 | Crítica: la confirmación oportuna es el indicador principal de fricción desde la perspectiva del cliente |
| A-15 | M-04 | Alta: el estado de cuenta sin ajustes valida que el período cerró sin sorpresas |
| A-16 | M-02 | Alta: la velocidad de detección determina el tiempo disponible para preparar una alternativa |
| A-17 | M-02 | Alta: sin opciones evaluadas no puede ofrecerse alternativa real al cliente |
| A-18 | M-02 | Crítica: la notificación proactiva con alternativa es el evento de valor de M-02 |
| A-19 | M-02 | Alta: ejecutar la alternativa cierra el ciclo — si no se ejecuta la notificación no tiene valor |
| A-21 | M-04 | Alta: la evaluación crediticia define las condiciones bajo las que se establece el costo del cliente |
| A-23 | M-04 | Alta: las condiciones negociadas son la referencia contra la que el cliente mide el costo total |
| A-25 | M-05 | Media: un contrato bien estructurado reduce fricción futura — pedidos fluyen sin re-negociar |
| A-28 | M-02 | Media: la revisión comercial permite identificar incidentes y mejorar tiempo de respuesta |
| A-33 | M-04 | Alta: el ajuste modifica directamente el costo financiero del cliente |
| A-34 | M-04 | Alta: notificar claramente los cambios es parte de la predicibilidad de costo |

---

## 2.2 Activity —[AFFECTS]→ MetricDriver (10 relaciones)

> Actividades que mueven una palanca operacional. Con MetricDriver —[DRIVES]→ Metric construyen la ruta indirecta DV(A,M).

| Actividad | MetricDriver | Lógica |
|-----------|-------------|--------|
| A-46 | MD-04 | Negociar cupo con PEMEX TI es lo que mantiene producto disponible en terminal |
| A-47 | MD-06 | Las fuentes alternativas pre-calificadas son la disponibilidad de contingencia |
| A-49 | MD-04 | El control de inventario en tránsito informa la disponibilidad real en TAR |
| A-51 | MD-01 | El mantenimiento preventivo es el principal driver de disponibilidad de flota |
| A-52 | MD-01 | El stock de refacciones determina qué tan rápido una unidad vuelve a estar disponible |
| A-40 | MD-03 | Operadores bien capacitados planean y ejecutan rutas con mayor precisión |
| A-42 | MD-03 | Asignar operadores de mejor desempeño a rutas críticas mejora la precisión |
| A-39 | MD-13 | La política de crédito clara reduce los pedidos que requieren gestión manual adicional |
| A-55 | MD-12 | Un CRM actualizado permite confirmar pedidos más rápido al tener los datos del cliente listos |
| A-57 | MD-05 | El cierre formal de incidencias entrena al equipo a detectar y escalar más rápido la próxima vez |

---

## 2.3 Process —[CONTRIBUTES_TO]→ Metric (12 relaciones)

| Proceso | Métrica |
|---------|---------|
| P-01 | M-01 |
| P-01 | M-03 |
| P-01 | M-04 |
| P-01 | M-05 |
| P-02 | M-02 |
| P-02 | M-01 |
| P-03 | M-04 |
| P-03 | M-05 |
| P-04 | M-02 |
| P-04 | M-04 |
| P-05 | M-04 |
| P-05 | M-05 |

---

## 2.4 Activity —[TOUCHES]→ CustomerJourneyStep (17 relaciones)

| Actividad | CustomerJourneyStep |
|-----------|---------------------|
| A-20 | CJS-01 |
| A-22 | CJS-01 |
| A-23 | CJS-02 |
| A-25 | CJS-02 |
| A-01 | CJS-03 |
| A-14 | CJS-03 |
| A-11 | CJS-03 |
| A-01 | CJS-04 |
| A-11 | CJS-04 |
| A-13 | CJS-04 |
| A-18 | CJS-05 |
| A-19 | CJS-05 |
| A-57 | CJS-05 |
| A-28 | CJS-06 |
| A-58 | CJS-06 |
| A-29 | CJS-07 |
| A-30 | CJS-07 |

---

## 2.5 Activity —[PRECEDES]→ Activity

### 2.5.1 Dentro del proceso — 28 relaciones

#### P-01 — Gestión de Pedidos y Entregas
| Origen | Destino |
|--------|---------|
| A-01 | A-02 |
| A-02 | A-03 |
| A-03 | A-04 |
| A-03 | A-14 |
| A-04 | A-05 |
| A-05 | A-06 |
| A-06 | A-07 |
| A-07 | A-08 |
| A-08 | A-09 |
| A-09 | A-10 |
| A-10 | A-11 |
| A-11 | A-12 |
| A-11 | A-13 |
| A-13 | A-15 |

#### P-02 — Atención de Fallas y Contingencias
| Origen | Destino |
|--------|---------|
| A-16 | A-17 |
| A-17 | A-18 |
| A-18 | A-19 |

#### P-03 — Adquisición de Clientes
| Origen | Destino |
|--------|---------|
| A-20 | A-21 |
| A-21 | A-22 |
| A-22 | A-23 |
| A-23 | A-24 |
| A-24 | A-25 |

#### P-04 — Retención y Renovación
| Origen | Destino |
|--------|---------|
| A-26 | A-27 |
| A-27 | A-28 |
| A-28 | A-29 |
| A-29 | A-30 |

#### P-05 — Gestión de Crédito Comercial
| Origen | Destino |
|--------|---------|
| A-31 | A-32 |
| A-32 | A-33 |
| A-33 | A-34 |

---

### 2.5.2 Entre procesos — value stream (7 relaciones)

| Origen | Destino | Lógica |
|--------|---------|--------|
| A-25 | A-01 | El contrato firmado habilita la recepción de pedidos |
| A-30 | A-01 | El contrato renovado reactiva el ciclo de pedidos |
| A-33 | A-03 | Las condiciones crediticias actualizadas informan la autorización por pedido |
| A-04 | A-16 | Si la TAR no tiene producto disponible, dispara el protocolo de contingencia |
| A-10 | A-16 | Si el GPS detecta incidencia grave en ruta, activa el protocolo de contingencia |
| A-19 | A-06 | La solución alternativa incluye reprogramar una ventana de carga nueva en TAR |
| A-27 | A-28 | La revisión del historial es el insumo directo de la revisión comercial |

---

### 2.5.3 Entre procesos — soporte a value stream (12 relaciones)

| Origen | Destino | Lógica |
|--------|---------|--------|
| A-46 | A-04 | Sin cupo negociado con PEMEX TI no hay producto disponible que verificar en TAR |
| A-49 | A-04 | El control de inventario en tránsito informa qué volumen está realmente libre en TAR |
| A-51 | A-09 | El mantenimiento preventivo determina cuántas unidades están disponibles para asignar |
| A-40 | A-09 | Solo operadores capacitados y certificados pueden ser asignados a rutas |
| A-39 | A-03 | La política de crédito define los criterios que aplica la autorización por pedido |
| A-36 | A-03 | Las líneas de crédito disponibles determinan la capacidad de autorizar despachos |
| A-47 | A-17 | Las fuentes alternativas pre-calificadas son las opciones que evalúa A-17 |
| A-35 | A-07 | Los permisos CRE vigentes son prerequisito para que el muestreo NOM-016 sea válido |
| A-43 | A-01 | El sistema de pedidos debe estar operativo para recibir y registrar órdenes |
| A-43 | A-10 | La plataforma GPS debe estar activa para el monitoreo en tiempo real |
| A-55 | A-01 | El CRM con datos actualizados permite validar al cliente al recibir el pedido |
| A-55 | A-26 | El CRM con fechas de contrato permite identificar los próximos a vencer |

---

### 2.5.4 Actividades que insertan pasos en el value stream (misconceptions) — 4 relaciones

> Estas relaciones representan cómo los misconceptions se materializan en el grafo: actividades que se insertan en el flujo sin agregar valor al cliente.

| Origen | Destino | Lógica |
|--------|---------|--------|
| A-01 | A-64 | Los pedidos recibidos se compilan en el reporte diario de pendientes |
| A-64 | A-63 | El reporte de pendientes alimenta la reunión de liberación de despachos |
| A-63 | A-62 | En la reunión se decide la aprobación formal multilevel |
| A-62 | A-03 | Solo tras la aprobación multinivel procede la autorización de crédito estándar |

---

## 2.6 Activity —[INVOLVES_EVENT]→ Event (12 relaciones)

| Actividad | Evento | Rol | Descripción |
|-----------|--------|-----|-------------|
| A-01 | EV-D01 | responde_a | La recepción del pedido es la primera acción interna ante la demanda |
| A-20 | EV-D02 | responde_a | La calificación del prospecto inicia el ciclo de adquisición |
| A-16 | EV-D03 | responde_a | La detección de falla activa el protocolo de contingencia |
| A-31 | EV-D04 | responde_a | La solicitud de ajuste dispara la revisión de condiciones |
| A-26 | EV-D05 | responde_a | La identificación de vencimiento activa el ciclo de retención |
| A-11 | EV-V01 | produce | La entrega completada en el horario comprometido |
| A-18 | EV-V02 | produce | La notificación con alternativa concreta |
| A-12 | EV-V03 | produce | La verificación de aforo final confirma el volumen dentro de tolerancia |
| A-15 | EV-V04 | produce | El estado de cuenta sin ajustes cierra el período predecible para el cliente |
| A-14 | EV-V05 | produce | La confirmación de pedido sin intervención del cliente |
| A-25 | EV-V06 | produce | La firma del contrato formaliza al cliente nuevo |
| A-30 | EV-V07 | produce | La firma de renovación consolida la retención |

---

## 2.7 Team —[PERFORMS]→ Activity (primary)

| Equipo | Actividades que ejecuta (primario) |
|--------|-----------------------------------|
| T-01 (Gobernanza) | A-03, A-13, A-15, A-17, A-21, A-24, A-25, A-30, A-31, A-32, A-33, A-34, A-35, A-36, A-37, A-38, A-39, A-53, A-62, A-63, A-64, A-68 |
| T-02 (RRHH) | A-40, A-41, A-42, A-60, A-61 |
| T-03 (Tecnología) | A-43, A-44, A-45 |
| T-04 (Abastecimiento) | A-16, A-17, A-19, A-46, A-47, A-48, A-50 |
| T-05 (Logística Interna) | A-06, A-08, A-49 |
| T-06 (Operaciones) | A-07, A-12, A-51, A-52, A-53, A-59 |
| T-07 (Logística Externa) | A-05, A-09, A-10, A-11, A-16, A-19, A-69 |
| T-08 (Marketing y Ventas) | A-01, A-02, A-14, A-20, A-22, A-23, A-29, A-54, A-55, A-56, A-66, A-67, A-70 |
| T-09 (Servicio Postventa) | A-18, A-26, A-27, A-28, A-57, A-58, A-65, A-67 |

---

## 2.8 Team —[OWNS]→ Process / Capability

| Equipo | Proceso | Capability |
|--------|---------|------------|
| T-01 | P-05 | CAP-01 |
| T-02 | — | CAP-02 |
| T-03 | — | CAP-03 |
| T-04 | — | CAP-04 |
| T-05 | — | CAP-05 |
| T-06 | — | CAP-06 |
| T-07 | P-01, P-02 | CAP-07 |
| T-08 | P-03 | CAP-08 |
| T-09 | P-04 | CAP-09 |

---

## 2.9 Activity —[SUPPORTS]→ Capability

| Actividades | Capability |
|-------------|------------|
| A-03, A-13, A-15, A-21, A-35, A-36, A-37, A-38, A-39 | CAP-01 |
| A-40, A-41, A-42 | CAP-02 |
| A-10, A-43, A-44, A-45 | CAP-03 |
| A-04, A-17, A-46, A-47, A-48, A-50 | CAP-04 |
| A-06, A-07, A-08, A-49 | CAP-05 |
| A-07, A-09, A-51, A-52, A-53 | CAP-06 |
| A-05, A-06, A-09, A-10, A-11, A-12, A-19 | CAP-07 |
| A-01, A-02, A-14, A-20, A-22, A-23, A-54, A-55, A-56 | CAP-08 |
| A-18, A-26, A-27, A-28, A-29, A-57, A-58 | CAP-09 |

---

## 2.10 Activity —[USES_SYSTEM]→ System

| Actividad | Sistema(s) |
|-----------|------------|
| A-01 | S-01, S-07 |
| A-02 | S-01, S-07 |
| A-03 | S-03 |
| A-04 | S-01 |
| A-05 | S-02 |
| A-06 | S-01 |
| A-07 | S-06 |
| A-08 | S-01, S-06 |
| A-09 | S-02 |
| A-10 | S-02 |
| A-11 | S-01 |
| A-12 | S-01, S-06 |
| A-13 | S-03, S-05 |
| A-14 | S-01 |
| A-15 | S-03 |
| A-16 | S-01, S-02 |
| A-18 | S-07 |
| A-21 | S-03, S-07 |
| A-22 | S-07 |
| A-24 | S-01, S-07 |
| A-26 | S-07 |
| A-27 | S-07, S-03 |
| A-28 | S-07 |
| A-32 | S-03 |
| A-35 | S-04 |
| A-36 | S-03 |
| A-37 | S-03, S-05 |
| A-43 | S-01, S-02 |
| A-44 | S-03, S-04, S-05 |
| A-46 | S-01 |
| A-48 | S-03 |
| A-51 | S-08 |
| A-52 | S-08 |
| A-55 | S-07 |
| A-56 | S-03, S-07 |
| A-58 | S-07 |
| A-63 | S-01 |
| A-64 | S-01 |

---

# BLOQUE 3 — Cuantificación simulada

---

## 3.1 Fórmulas

```
V(A)           = 0.3·P + 0.4·C + 0.2·F + 0.1·R
B(A,M)         = 0.4·G(A,M) + 0.4·J(A,M) + 0.2·DV(A,M)
Relevance(A,M) = B(A,M) × V(A)
```

---

## 3.2 Value Streams — verificación de conectividad

| VS | Demanda | Path de actividades | Entrega de valor |
|----|---------|---------------------|-----------------|
| VS-01 | EV-D01 | A-01→A-02→A-03→A-04→A-05→A-06→A-07→A-08→A-09→A-10→A-11 | EV-V01 |
| VS-02 | EV-D01 | A-01→A-02→A-03→A-04→A-05→A-06→A-07→A-08→A-09→A-10→A-11→A-12 | EV-V03 |
| VS-03 | EV-D01 | A-01→A-02→A-03→A-14 | EV-V05 |
| VS-04 | EV-D01 | A-01→A-02→A-03→A-04→A-05→A-06→A-07→A-08→A-09→A-10→A-11→A-13→A-15 | EV-V04 |
| VS-05 | EV-D03 | A-16→A-17→A-18 | EV-V02 |
| VS-06 | EV-D02 | A-20→A-21→A-22→A-23→A-24→A-25 | EV-V06 |
| VS-07 | EV-D05 | A-26→A-27→A-28→A-29→A-30 | EV-V07 |
| VS-08 | EV-D04 | A-31→A-32→A-33→A-34 | EV-V04 |

> **Path con misconception M-D activo (estado actual de la organización):**
> VS-01 real: A-01→A-64→A-63→A-62→A-03→A-04→A-05→A-06→A-07→A-08→A-09→A-10→A-11

---

## 3.3 Tabla de cuantificación — todas las actividades

> wP=0.3, wC=0.4, wF=0.2, wR=0.1 | "—" en Métricas con B>0 indica B≈0 (sin conexión trazable a métrica del cliente)

| ID | P | C | F | R | V(A) | Métricas con B > 0 |
|----|---|---|---|---|------|--------------------|
| A-01 | 0.25 | 0.50 | 1.0 | 0.25 | 0.50 | M-05, M-01 |
| A-02 | 0.50 | 0.75 | 1.0 | 0.50 | 0.70 | M-05, M-04 |
| A-03 | 0.75 | 0.75 | 1.0 | 0.75 | 0.80 | M-05, M-01 |
| A-04 | 0.75 | 1.0 | 1.0 | 0.75 | 0.90 | M-01 |
| A-05 | 0.75 | 1.0 | 1.0 | 0.75 | 0.90 | M-01 |
| A-06 | 0.75 | 0.75 | 1.0 | 0.75 | 0.80 | M-01 |
| A-07 | 0.75 | 1.0 | 1.0 | 1.0 | 0.93 | M-03 |
| A-08 | 0.75 | 0.75 | 1.0 | 0.75 | 0.80 | M-03, M-04 |
| A-09 | 0.75 | 0.50 | 1.0 | 0.50 | 0.68 | M-01 |
| A-10 | 0.75 | 0.75 | 1.0 | 0.75 | 0.80 | M-01, M-02 |
| A-11 | 1.0 | 1.0 | 1.0 | 0.75 | 0.98 | M-01, M-04 |
| A-12 | 1.0 | 1.0 | 1.0 | 0.75 | 0.98 | M-03 |
| A-13 | 0.75 | 0.75 | 1.0 | 0.50 | 0.78 | M-04, M-05 |
| A-14 | 0.75 | 0.75 | 1.0 | 0.25 | 0.75 | M-05 |
| A-15 | 0.75 | 0.50 | 0.50 | 0.25 | 0.55 | M-04 |
| A-16 | 0.75 | 1.0 | 0.50 | 1.0 | 0.83 | M-02 |
| A-17 | 0.75 | 1.0 | 0.50 | 0.75 | 0.80 | M-02 |
| A-18 | 1.0 | 1.0 | 0.50 | 1.0 | 0.90 | M-02 |
| A-19 | 1.0 | 1.0 | 0.50 | 1.0 | 0.90 | M-02 |
| A-20 | 0.25 | 0.50 | 0.50 | 0.25 | 0.40 | M-05 |
| A-21 | 0.75 | 0.75 | 0.50 | 0.75 | 0.70 | M-04 |
| A-22 | 0.50 | 0.50 | 0.50 | 0.25 | 0.48 | M-04 (bajo, vía proceso) |
| A-23 | 0.75 | 0.75 | 0.50 | 0.50 | 0.68 | M-04 |
| A-24 | 0.75 | 0.75 | 0.50 | 0.50 | 0.68 | M-05 |
| A-25 | 1.0 | 1.0 | 0.50 | 0.75 | 0.88 | M-05 |
| A-26 | 0.25 | 0.50 | 0.50 | 0.75 | 0.45 | M-02, M-04 (bajo, vía proceso) |
| A-27 | 0.50 | 0.75 | 0.25 | 0.50 | 0.55 | M-02 |
| A-28 | 0.75 | 1.0 | 0.25 | 0.75 | 0.75 | M-02 |
| A-29 | 0.75 | 0.75 | 0.25 | 0.75 | 0.65 | M-04 |
| A-30 | 1.0 | 1.0 | 0.25 | 0.75 | 0.83 | M-01, M-02, M-04 |
| A-31 | 0.25 | 0.50 | 0.25 | 0.25 | 0.35 | M-04, M-05 (bajo, vía proceso) |
| A-32 | 0.50 | 0.75 | 0.25 | 0.50 | 0.55 | M-04 |
| A-33 | 0.75 | 1.0 | 0.25 | 0.75 | 0.78 | M-04 |
| A-34 | 0.75 | 0.75 | 0.25 | 0.50 | 0.63 | M-04 |
| A-35 | 0.75 | 1.0 | 0.25 | 1.0 | 0.78 | — |
| A-36 | 0.75 | 1.0 | 0.25 | 0.75 | 0.75 | — |
| A-37 | 0.50 | 0.50 | 0.50 | 0.25 | 0.48 | — |
| A-38 | 0.25 | 0.50 | 0.25 | 0.75 | 0.40 | — |
| A-39 | 0.75 | 0.75 | 0.25 | 0.50 | 0.63 | M-05 (vía MD-13) |
| A-40 | 0.50 | 0.75 | 0.50 | 0.75 | 0.63 | M-01 (vía MD-03) |
| A-41 | 0.25 | 0.50 | 0.25 | 0.50 | 0.38 | — |
| A-42 | 0.25 | 0.50 | 0.50 | 0.25 | 0.40 | M-01 (vía MD-03) |
| A-43 | 0.75 | 1.0 | 0.50 | 0.75 | 0.80 | — |
| A-44 | 0.75 | 0.75 | 0.50 | 0.75 | 0.70 | — |
| A-45 | 0.75 | 0.75 | 0.25 | 0.75 | 0.65 | — |
| A-46 | 0.75 | 1.0 | 0.75 | 0.75 | 0.85 | M-01 (vía MD-04) |
| A-47 | 0.50 | 0.75 | 0.25 | 0.75 | 0.58 | M-02 (vía MD-06) |
| A-48 | 0.50 | 0.50 | 0.75 | 0.50 | 0.55 | — |
| A-49 | 0.75 | 0.75 | 1.0 | 0.50 | 0.78 | M-01 (vía MD-04) |
| A-50 | 0.50 | 0.75 | 0.50 | 0.50 | 0.60 | — |
| A-51 | 0.75 | 1.0 | 0.50 | 0.75 | 0.80 | M-01 (vía MD-01) |
| A-52 | 0.50 | 0.75 | 0.50 | 0.50 | 0.60 | M-01 (vía MD-01) |
| A-53 | 0.25 | 0.75 | 0.25 | 1.0 | 0.53 | — |
| A-54 | 0.25 | 0.50 | 1.0 | 0.25 | 0.50 | — |
| A-55 | 0.50 | 0.75 | 0.75 | 0.50 | 0.65 | M-05 (vía MD-12) |
| A-56 | 0.25 | 0.50 | 0.50 | 0.25 | 0.40 | — |
| A-57 | 0.50 | 0.75 | 0.50 | 0.50 | 0.60 | M-02 |
| A-58 | 0.25 | 0.50 | 0.50 | 0.25 | 0.40 | — |
| A-59 | 0.25 | 0.25 | 0.75 | 0.25 | 0.35 | — |
| A-60 | 0.25 | 0.25 | 0.50 | 0.25 | 0.30 | — |
| A-61 | 0.25 | 0.25 | 0.25 | 0.25 | 0.25 | — |
| A-62 | 0.75 | 0.50 | 1.0 | 0.50 | 0.68 | — |
| A-63 | 0.50 | 0.50 | 1.0 | 0.50 | 0.60 | — |
| A-64 | 0.25 | 0.25 | 1.0 | 0.25 | 0.40 | — |
| A-65 | 0.25 | 0.25 | 0.50 | 0.25 | 0.30 | — |
| A-66 | 0.25 | 0.25 | 0.25 | 0.25 | 0.25 | — |
| A-67 | 0.25 | 0.25 | 0.25 | 0.25 | 0.25 | — |
| A-68 | 0.25 | 0.25 | 0.50 | 0.25 | 0.30 | — |
| A-69 | 0.25 | 0.25 | 1.0 | 0.25 | 0.40 | — |
| A-70 | 0.50 | 0.25 | 0.75 | 0.25 | 0.43 | — |
