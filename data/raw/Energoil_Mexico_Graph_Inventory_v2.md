# ENERGOIL MÉXICO — Inventario de Nodos y Relaciones v2
## Grafo de Conocimiento | Documento de trabajo para construcción del demo | Junio 2026

---

> **Cambios principales respecto a v1:**
> - Eventos clasificados en dos tipos: **Demanda** (disparan un flujo) y **Entrega de Valor** (materializan el resultado).
> - Actividades etiquetadas con una o más **Áreas Porter** — permite ver contribución por área, no solo por proceso.
> - Equipos redefinidos como las 9 áreas del modelo Porter.
> - Relaciones **PRECEDES cross-proceso** añadidas — el grafo ahora conecta áreas entre sí, eliminando los silos.
> - **Bloque 4** al final: actividades de control/desperdicio para validación del sistema. No ingestar.

---

# BLOQUE 1 — Nodos

---

## 1.1 Metric (6 nodos)

| ID | Nombre de la Métrica | Definición operacional | Necesidad del cliente que representa |
|----|----------------------|------------------------|--------------------------------------|
| M-01 | Tasa de Entrega a Tiempo | % de entregas realizadas dentro del plazo acordado con el cliente | Continuidad operativa del cliente industrial |
| M-02 | Tasa de Cumplimiento de Volumen | % del volumen pedido vs. volumen efectivamente entregado | Confiabilidad del suministro |
| M-03 | Competitividad de Precio vs. Rack | Diferencial promedio entre precio Energoil y precio rack PEMEX terminal | Protección del margen del cliente gasolinero |
| M-04 | Incidentes Regulatorios por Entrega | Número de incidentes CRE / NOM-016 / SCT por cada 100 entregas | Cero interrupciones por cumplimiento |
| M-05 | Días de Crédito Disponibles | Plazo promedio de crédito otorgado a clientes activos | Flexibilidad financiera del cliente autoconsumo |
| M-06 | Tasa de Retención de Clientes | % de clientes que renuevan contrato o continúan comprando al cierre del período | Confianza y relación comercial de largo plazo |

---

## 1.2 MetricDriver (15 nodos)

| ID | Métrica padre | Driver | Descripción / cómo se mide |
|----|---------------|--------|----------------------------|
| MD-01 | M-01 | Disponibilidad de flota de pipas | Nº de unidades disponibles vs. requeridas por ruta y turno |
| MD-02 | M-01 | Tiempo de carga en terminal TAR | Minutos promedio desde llegada a terminal hasta salida con carga |
| MD-03 | M-01 | Eficiencia de ruteo | % de rutas ejecutadas sin retrasos por planeación o tráfico |
| MD-04 | M-01 | Disponibilidad de producto en terminal | Días de inventario disponible en la TAR asignada |
| MD-05 | M-02 | Cobertura de posición de compra | Volumen comprometido con proveedor vs. volumen demandado por clientes |
| MD-06 | M-02 | Índice de merma y diferencia de aforo | Litros perdidos o no entregados por merma, contaminación o aforo |
| MD-07 | M-03 | Costo de adquisición por litro | Precio pagado en terminal + flete de recepción por litro |
| MD-08 | M-03 | Optimización del IEPS | Aprovechamiento de estímulos fiscales y variaciones de IEPS por período |
| MD-09 | M-03 | Eficiencia operativa de distribución | Costo logístico total por litro entregado |
| MD-10 | M-04 | Vigencia de permisos CRE y SCT | Días hasta vencimiento de permisos críticos de transporte y comercialización |
| MD-11 | M-04 | Conformidad NOM-016 del producto | % de muestras de producto que pasan prueba de calidad por lote |
| MD-12 | M-05 | Capital de trabajo disponible | Líneas de crédito activas vs. volumen de compras mensual |
| MD-13 | M-05 | Tasa de recuperación de cartera | % de facturas cobradas dentro del plazo acordado |
| MD-14 | M-06 | Net Promoter Score operativo | Calificación de satisfacción post-entrega por cliente |
| MD-15 | M-06 | Tiempo de respuesta a incidencias | Horas promedio desde reporte de problema hasta resolución |

---

## 1.3 CustomerJourneyStep (8 nodos)

| ID | Nombre del paso | Qué experimenta el cliente en este momento |
|----|-----------------|---------------------------------------------|
| CJS-01 | Prospección y primer contacto | El cliente busca un proveedor alternativo o complementario a PEMEX; evalúa reputación, cobertura y precio |
| CJS-02 | Negociación comercial | El cliente negocia volumen, precio, plazo de crédito y condiciones de entrega con el ejecutivo de cuenta |
| CJS-03 | Onboarding y alta de cuenta | El cliente completa documentación, firma contrato y recibe acceso al portal/sistema de pedidos |
| CJS-04 | Primer pedido y entrega | Momento de verdad: el cliente experimenta por primera vez la logística, puntualidad y calidad del producto |
| CJS-05 | Operación recurrente | Ciclo continuo de pedidos, entregas y facturación; el cliente calibra confiabilidad y servicio |
| CJS-06 | Incidencia o falla de servicio | El cliente reporta un problema (retraso, calidad, volumen); evalúa capacidad de respuesta de Energoil |
| CJS-07 | Revisión comercial periódica | Reunión de seguimiento donde se revisan precios, volúmenes, condiciones de crédito y satisfacción |
| CJS-08 | Renovación o expansión | El cliente decide continuar, ampliar volumen, agregar productos o referir a otro cliente |

---

## 1.4 Process — 8 Macroprocesos (8 nodos)

| ID | Nombre del Proceso | Descripción |
|----|--------------------|-------------|
| P-01 | Inteligencia Comercial de Mercado | Monitoreo continuo de precios rack PEMEX, diferenciales regionales, IEPS, demanda sectorial y movimientos competitivos |
| P-02 | Aseguramiento de Suministro | Negociación y contratación de volúmenes con PEMEX Transformación Industrial y proveedores alternativos de importación |
| P-03 | Financiamiento de Operaciones | Gestión de capital de trabajo, líneas de crédito, factoraje y crédito a clientes para sostener el ciclo compra-entrega-cobro |
| P-04 | Gestión Regulatoria y Compliance | Mantenimiento de permisos CRE, cumplimiento NOM-016, certificaciones SCT/ASEA y gestión de obligaciones fiscales (IEPS) |
| P-05 | Ejecución Logística | Planeación y operación de rutas, gestión de flota de pipas, carga en terminales TAR y entrega en planta o estación del cliente |
| P-06 | Comercialización y Gestión de Clientes | Prospección, negociación, alta de cuenta, gestión de pedidos, facturación y atención al cliente postventa |
| P-07 | Gestión de Riesgos | Identificación, medición y mitigación de riesgos de precio, crédito, operativo (huachicol), regulatorio y de contraparte |
| P-08 | Optimización de Portafolio | Análisis de rentabilidad por producto, cliente y región para reasignar capital y capacidad hacia las oportunidades de mayor margen |

---

## 1.5 Activity (43 nodos)

> Nueva columna **Área(s) Porter**: una o más áreas del modelo de Porter que ejecutan o co-ejecutan esta actividad. Es la base para la atribución cross-área de valor.

| ID | Proceso | Nombre de la Actividad | Área(s) Porter | Frecuencia |
|----|---------|------------------------|----------------|------------|
| A-01 | P-01 | Monitoreo diario de precios rack PEMEX por terminal TAR | Marketing y Ventas | Diaria |
| A-02 | P-01 | Seguimiento de variaciones del IEPS y estímulos fiscales | Marketing y Ventas, Núcleo de Gobernanza | Diaria |
| A-03 | P-01 | Análisis de diferencial de precio por corredor y región | Marketing y Ventas | Semanal |
| A-04 | P-01 | Monitoreo de demanda por sector (minería, transporte, agrícola) | Marketing y Ventas | Semanal |
| A-05 | P-01 | Análisis de movimientos de competidores y nuevas marcas CRE | Marketing y Ventas | Quincenal |
| A-06 | P-02 | Negociación de volumen y precio con PEMEX TI (contrato asociado) | Abastecimiento | Mensual |
| A-07 | P-02 | Gestión de posición de compra y asignación de cupo en TAR | Abastecimiento, Logística Interna | Semanal |
| A-08 | P-02 | Evaluación y contacto con importadores / proveedores alternativos | Abastecimiento | Mensual |
| A-09 | P-02 | Seguimiento de disponibilidad de producto en terminales asignadas | Abastecimiento, Logística Interna | Diaria |
| A-10 | P-02 | Cierre de contratos spot en caso de desabasto o diferencial favorable | Abastecimiento | Según evento |
| A-11 | P-03 | Negociación y renovación de líneas de crédito con bancos | Núcleo de Gobernanza | Trimestral |
| A-12 | P-03 | Evaluación crediticia de nuevos clientes | Núcleo de Gobernanza | Por cliente nuevo |
| A-13 | P-03 | Monitoreo de cartera y gestión de cobranza | Núcleo de Gobernanza | Semanal |
| A-14 | P-03 | Activación de factoraje para acelerar ciclo de cobro | Núcleo de Gobernanza | Según necesidad |
| A-15 | P-03 | Autorización y control de crédito a clientes activos | Núcleo de Gobernanza | Por pedido |
| A-16 | P-04 | Seguimiento de vigencia de permisos CRE de comercialización | Núcleo de Gobernanza | Mensual |
| A-17 | P-04 | Gestión de renovación de permisos SCT para flota de transporte | Núcleo de Gobernanza, Logística Externa | Anual |
| A-18 | P-04 | Control de calidad del producto: muestreo y prueba NOM-016 | Operaciones, Núcleo de Gobernanza | Por lote |
| A-19 | P-04 | Reporte de obligaciones fiscales IEPS ante SAT | Núcleo de Gobernanza | Mensual |
| A-20 | P-04 | Gestión de CURR y obligaciones ASEA de seguridad operativa | Núcleo de Gobernanza, Operaciones | Anual |
| A-21 | P-04 | Atención de verificaciones y auditorías CRE en campo | Núcleo de Gobernanza | Según evento |
| A-22 | P-05 | Planeación y asignación de rutas de entrega por zona | Logística Externa | Diaria |
| A-23 | P-05 | Programación de cargas en terminal TAR (ventanas de carga) | Logística Interna, Logística Externa | Diaria |
| A-24 | P-05 | Supervisión de carga: aforo, sellos y documentación de traslado | Logística Interna, Operaciones | Por carga |
| A-25 | P-05 | Monitoreo GPS de pipas en ruta y gestión de incidencias | Logística Externa, Desarrollo Tecnológico | Tiempo real |
| A-26 | P-05 | Entrega en planta cliente: descarga, aforo y firma de remisión | Logística Externa | Por entrega |
| A-27 | P-05 | Mantenimiento preventivo y correctivo de flota de pipas | Operaciones | Mensual |
| A-28 | P-06 | Prospección y calificación de nuevos clientes industriales y gasolineras | Marketing y Ventas | Continua |
| A-29 | P-06 | Elaboración y negociación de propuesta comercial | Marketing y Ventas | Por prospecto |
| A-30 | P-06 | Alta de cliente: documentación, contrato y apertura en sistema | Marketing y Ventas, Núcleo de Gobernanza | Por cliente nuevo |
| A-31 | P-06 | Recepción y confirmación de pedidos | Marketing y Ventas, Logística Externa | Diaria |
| A-32 | P-06 | Facturación y envío de documentos fiscales al cliente | Núcleo de Gobernanza, Marketing y Ventas | Por entrega |
| A-33 | P-06 | Atención de incidencias y reclamos post-entrega | Servicio Postventa | Según evento |
| A-34 | P-06 | Visita de revisión comercial periódica con cliente clave | Servicio Postventa, Marketing y Ventas | Trimestral |
| A-35 | P-07 | Monitoreo de riesgo de precio: exposición a volatilidad PEMEX/IEPS | Núcleo de Gobernanza | Semanal |
| A-36 | P-07 | Evaluación de riesgo de crédito de cartera activa | Núcleo de Gobernanza | Mensual |
| A-37 | P-07 | Análisis de riesgo de huachicol por ruta y zona de operación | Núcleo de Gobernanza, Logística Externa | Mensual |
| A-38 | P-07 | Gestión de seguros: flota, carga, responsabilidad civil ecológica | Núcleo de Gobernanza | Anual |
| A-39 | P-07 | Monitoreo de cambios regulatorios CRE / SENER / SAT | Núcleo de Gobernanza | Mensual |
| A-40 | P-08 | Análisis de rentabilidad por cliente, producto y corredor | Núcleo de Gobernanza, Marketing y Ventas | Mensual |
| A-41 | P-08 | Revisión de mix de producto y decisión de expansión (diesel, ULSD, gasolina) | Núcleo de Gobernanza | Trimestral |
| A-42 | P-08 | Evaluación de nuevos segmentos o zonas geográficas | Núcleo de Gobernanza, Marketing y Ventas | Trimestral |
| A-43 | P-08 | Reasignación de capacidad logística hacia rutas de mayor margen | Núcleo de Gobernanza, Logística Externa | Mensual |

---

## 1.6 Team (9 nodos — Áreas Porter)

> Los equipos corresponden directamente a las 9 áreas del modelo de Porter. Esto permite atribuir valor y responsabilidad a unidades organizativas comparables entre distintos clientes.

| ID | Área Porter | Rol en Energoil México |
|----|-------------|------------------------|
| T-01 | Núcleo de Gobernanza | Dirección general, finanzas, legal, compliance, riesgos y relaciones regulatorias (CRE, SENER, SAT) |
| T-02 | Gestión de RRHH | Reclutamiento, capacitación y gestión del capital humano operativo y comercial |
| T-03 | Desarrollo Tecnológico | Administración de sistemas (ERP, GPS, portales CRE/SAT), integraciones y datos operativos |
| T-04 | Abastecimiento | Negociación y gestión de contratos con PEMEX TI y proveedores alternativos; administración de cupos TAR |
| T-05 | Logística Interna | Interfaz con terminales TAR: programación de cargas, aforo, sellos y control de inventario en terminal |
| T-06 | Operaciones | Control de calidad NOM-016, mantenimiento de flota de pipas y seguridad operativa ASEA |
| T-07 | Logística Externa | Planeación de rutas, coordinación de entregas, monitoreo GPS y gestión del último kilómetro |
| T-08 | Marketing y Ventas | Inteligencia de mercado, prospección, negociación comercial, gestión de cuentas y pedidos |
| T-09 | Servicio Postventa | Atención de incidencias, revisiones comerciales periódicas y gestión de retención de clientes |

---

## 1.7 Capability (9 nodos — Áreas Porter)

| ID | Capacidad | Descripción para Energoil México |
|----|-----------|----------------------------------|
| CAP-01 | Gobernanza Corporativa | Capacidad de gestionar riesgos, compliance regulatorio, finanzas y dirección estratégica de forma integrada |
| CAP-02 | Gestión de Talento | Capacidad de reclutar, retener y desarrollar el equipo operativo, logístico y comercial |
| CAP-03 | Capacidades Digitales y de Datos | Capacidad de operar sistemas integrados (ERP, GPS, portales regulatorios) y extraer inteligencia operativa |
| CAP-04 | Gestión de Abastecimiento | Capacidad de asegurar volumen competitivo en terminales PEMEX y fuentes alternativas con mínima interrupción |
| CAP-05 | Logística de Recepción y Terminal | Capacidad de gestionar la interfaz con las TAR: cargas, aforo, calidad y documentación en origen |
| CAP-06 | Excelencia Operativa y Calidad | Capacidad de mantener la flota operativa, cumplir NOM-016 y ejecutar sin incidentes de seguridad |
| CAP-07 | Distribución y Entrega | Capacidad de entregar combustible a tiempo, en volumen correcto y con trazabilidad documental completa |
| CAP-08 | Inteligencia Comercial y Ventas | Capacidad de identificar oportunidades de margen, adquirir clientes y gestionar el portafolio comercial |
| CAP-09 | Gestión de Experiencia del Cliente | Capacidad de resolver incidencias, sostener relaciones de largo plazo y convertir clientes en promotores |

---

## 1.8 System (8 nodos)

| ID | Sistema / Herramienta | Función en la operación |
|----|-----------------------|-------------------------|
| S-01 | Portal OPE-CRE | Plataforma oficial para reportes regulatorios, permisos y cumplimiento ante la CRE |
| S-02 | Sistema de Pedidos y Remisiones | Sistema interno de captura de pedidos, generación de remisiones y trazabilidad de entregas |
| S-03 | GPS / Rastreo de Flota | Plataforma de monitoreo satelital de pipas en ruta (posición, alertas, bitácora) |
| S-04 | ERP / Sistema Contable | Sistema de gestión financiera, facturación electrónica CFDI, cobranza y tesorería |
| S-05 | SIMA / PetroIntelligence | Herramienta de inteligencia de mercado para consulta de precios TAR, IEPS y competidores |
| S-06 | Sistema de Control de Calidad | Registro de muestras, resultados de pruebas NOM-016 y trazabilidad de lotes de producto |
| S-07 | Portal SAT / CFDI | Plataforma fiscal para emisión de facturas electrónicas, declaraciones IEPS y reportes SAT |
| S-08 | Sistema de Crédito y Cobranza | Gestión de límites de crédito, vencimientos, alertas de morosidad y factoraje |

---

## 1.9 Event (14 nodos)

> Los eventos se clasifican en dos tipos: **Demanda** — disparan un flujo de actividades — y **Entrega de Valor** — materializan el resultado para el cliente o la organización. Todo Value Stream debe tener al menos un evento de cada tipo como extremos del path.

| ID | Nombre del Evento | Tipo | Qué activa o representa |
|----|-------------------|------|-------------------------|
| EV-D01 | Pedido de combustible recibido | Demanda | El cliente solicita un volumen concreto; dispara el ciclo completo de autorización-logística-entrega |
| EV-D02 | Prospecto calificado identificado | Demanda | El área comercial detecta un cliente potencial con perfil válido; dispara el ciclo de adquisición |
| EV-D03 | Oportunidad de margen detectada en mercado | Demanda | La inteligencia comercial identifica un diferencial rentable; dispara la negociación de suministro |
| EV-D04 | Alerta de vencimiento de permiso CRE/SCT | Demanda | El sistema detecta un permiso próximo a vencer; dispara el proceso de renovación regulatoria |
| EV-D05 | Incidente de servicio reportado por cliente | Demanda | El cliente notifica una falla (retraso, calidad, volumen); dispara el protocolo de atención |
| EV-D06 | Decisión de revisión estratégica de portafolio | Demanda | La dirección activa el ciclo trimestral de evaluación de rentabilidad y reasignación de recursos |
| EV-V01 | Contrato de suministro firmado | Entrega de Valor | Formalización del acuerdo comercial con el cliente; activa el ciclo operativo recurrente |
| EV-V02 | Cupo en terminal TAR asignado | Entrega de Valor | PEMEX TI confirma volumen y ventana de carga; el suministro queda asegurado para el período |
| EV-V03 | Carga completada en terminal | Entrega de Valor | La pipa sale de la TAR con producto sellado, aforado y documentado; la cadena de custodia inicia |
| EV-V04 | Entrega confirmada por cliente | Entrega de Valor | El cliente firma la remisión; el volumen queda recibido y se activa la facturación |
| EV-V05 | Factura CFDI emitida | Entrega de Valor | Se emite el comprobante fiscal; inicia formalmente el plazo de crédito acordado |
| EV-V06 | Cobro recibido | Entrega de Valor | El cliente liquida la factura; el capital se libera para el siguiente ciclo de compra |
| EV-V07 | Renovación o expansión de contrato | Entrega de Valor | El cliente confirma continuidad o amplía volumen; consolida la retención y el valor de largo plazo |
| EV-V08 | Permiso renovado / Auditoría CRE superada | Entrega de Valor | El proceso de compliance concluye exitosamente; la operación queda habilitada sin interrupción |

---

# BLOQUE 2 — Relaciones

---

## 2.1 Activity —[AFFECTS]→ Metric (25 relaciones)

| Actividad | Métrica | Fuerza causal |
|-----------|---------|---------------|
| A-01 | M-03 | Alta: precios rack son la base del diferencial de margen |
| A-02 | M-03 | Alta: IEPS afecta directamente el costo y el margen disponible |
| A-06 | M-02 | Alta: el contrato define el volumen asegurado con el proveedor |
| A-07 | M-02 | Alta: el cupo en TAR determina la disponibilidad real de producto |
| A-07 | M-01 | Media: sin cupo asignado no puede iniciarse la ruta de entrega |
| A-09 | M-01 | Alta: disponibilidad en terminal es prerequisito de entrega puntual |
| A-09 | M-02 | Alta: si no hay producto en TAR, el volumen pedido no puede cumplirse |
| A-12 | M-05 | Alta: la evaluación crediticia define el crédito que se puede otorgar |
| A-13 | M-05 | Media: cobranza eficiente sostiene la capacidad de dar crédito nuevo |
| A-15 | M-05 | Alta: autorización de crédito es el acto concreto de entregar financiamiento |
| A-15 | M-01 | Media: si el crédito no se autoriza, el pedido no avanza a logística |
| A-16 | M-04 | Crítica: permiso CRE vencido detiene toda operación comercial |
| A-17 | M-04 | Alta: SCT vencido inmoviliza pipas y bloquea entregas |
| A-18 | M-04 | Crítica: falla NOM-016 genera incidente regulatorio y retención de producto |
| A-19 | M-04 | Alta: incumplimiento IEPS ante SAT genera multas y posible suspensión |
| A-22 | M-01 | Alta: el ruteo determina directamente la puntualidad de la entrega |
| A-23 | M-01 | Alta: la programación de ventanas de carga es cuello de botella frecuente |
| A-24 | M-04 | Alta: documentación de traslado incorrecta es fuente de incidentes regulatorios |
| A-26 | M-01 | Crítica: la entrega es el evento final que define si se cumplió el plazo |
| A-26 | M-02 | Crítica: la entrega determina el volumen efectivamente recibido por el cliente |
| A-33 | M-06 | Alta: la respuesta a incidencias define la percepción de confiabilidad del cliente |
| A-34 | M-06 | Alta: la revisión periódica es el mecanismo principal de retención de clientes clave |
| A-35 | M-03 | Media: gestión de exposición de precio protege el margen ante volatilidad PEMEX/IEPS |
| A-37 | M-01 | Media: rutas con alto riesgo de huachicol generan desvíos y retrasos |
| A-40 | M-06 | Media: visibilidad de rentabilidad por cliente permite priorizar esfuerzo de retención |

---

## 2.2 Process —[CONTRIBUTES_TO]→ Metric (16 relaciones)

| Proceso | Métrica |
|---------|---------|
| P-01 | M-03 |
| P-01 | M-02 |
| P-02 | M-02 |
| P-02 | M-01 |
| P-03 | M-05 |
| P-03 | M-06 |
| P-04 | M-04 |
| P-05 | M-01 |
| P-05 | M-02 |
| P-06 | M-06 |
| P-06 | M-05 |
| P-06 | M-01 |
| P-07 | M-04 |
| P-07 | M-03 |
| P-08 | M-03 |
| P-08 | M-06 |

---

## 2.3 Activity —[TOUCHES]→ CustomerJourneyStep (11 relaciones)

| Actividad | CustomerJourneyStep |
|-----------|---------------------|
| A-28 | CJS-01 |
| A-29 | CJS-02 |
| A-30 | CJS-03 |
| A-26 | CJS-04 |
| A-31 | CJS-04 |
| A-31 | CJS-05 |
| A-32 | CJS-05 |
| A-33 | CJS-06 |
| A-34 | CJS-07 |
| A-34 | CJS-08 |
| A-26 | CJS-05 |

---

## 2.4 Activity —[PRECEDES]→ Activity

### 2.4.1 Dentro del proceso (intra-proceso) — 28 relaciones

#### P-01 — Inteligencia Comercial
| Origen | Destino |
|--------|---------|
| A-01 | A-02 |
| A-02 | A-03 |
| A-03 | A-04 |
| A-04 | A-05 |

#### P-02 — Aseguramiento de Suministro
| Origen | Destino |
|--------|---------|
| A-06 | A-07 |
| A-07 | A-09 |
| A-09 | A-10 |

#### P-03 — Financiamiento de Operaciones
| Origen | Destino |
|--------|---------|
| A-11 | A-12 |
| A-12 | A-15 |
| A-15 | A-13 |
| A-13 | A-14 |

#### P-04 — Gestión Regulatoria y Compliance
| Origen | Destino |
|--------|---------|
| A-16 | A-17 |
| A-17 | A-18 |
| A-18 | A-19 |
| A-19 | A-20 |
| A-20 | A-21 |

#### P-05 — Ejecución Logística
| Origen | Destino |
|--------|---------|
| A-22 | A-23 |
| A-23 | A-24 |
| A-24 | A-25 |
| A-25 | A-26 |

#### P-06 — Comercialización y Gestión de Clientes
| Origen | Destino |
|--------|---------|
| A-28 | A-29 |
| A-29 | A-30 |
| A-30 | A-31 |
| A-31 | A-32 |
| A-32 | A-33 |
| A-33 | A-34 |

#### P-07 — Gestión de Riesgos
| Origen | Destino |
|--------|---------|
| A-35 | A-36 |
| A-36 | A-37 |
| A-37 | A-38 |
| A-38 | A-39 |

#### P-08 — Optimización de Portafolio
| Origen | Destino |
|--------|---------|
| A-40 | A-41 |
| A-41 | A-42 |
| A-42 | A-43 |

---

### 2.4.2 Entre procesos (cross-proceso) — 16 relaciones

> Estas relaciones son el principal cambio respecto a v1. Conectan áreas que antes operaban en silos y permiten trazar los Value Streams completos de demanda a entrega.

| Origen | Destino | Proceso origen → destino | Lógica de la dependencia |
|--------|---------|--------------------------|--------------------------|
| A-03 | A-06 | P-01 → P-02 | El análisis de diferencial de precio informa cuándo y cuánto negociar con PEMEX TI |
| A-01 | A-35 | P-01 → P-07 | El monitoreo de precio activa el seguimiento de exposición de riesgo de margen |
| A-35 | A-06 | P-07 → P-02 | El riesgo de precio identificado define la urgencia y el volumen a asegurar con proveedores |
| A-39 | A-16 | P-07 → P-04 | Un cambio regulatorio detectado dispara la revisión de vigencia de permisos CRE |
| A-37 | A-22 | P-07 → P-05 | El análisis de rutas con riesgo de huachicol alimenta directamente la planeación de rutas seguras |
| A-07 | A-23 | P-02 → P-05 | Solo cuando el cupo en TAR está asignado puede programarse la ventana de carga |
| A-09 | A-22 | P-02 → P-05 | La verificación de disponibilidad de producto en terminal es prerequisito del ruteo |
| A-18 | A-24 | P-04 → P-05 | El resultado del muestreo NOM-016 debe estar disponible antes de supervisar la carga |
| A-28 | A-12 | P-06 → P-03 | Cuando un prospecto avanza al cierre, se activa su evaluación crediticia |
| A-31 | A-15 | P-06 → P-03 | La recepción de un pedido activo dispara la autorización de crédito para ese despacho |
| A-15 | A-22 | P-03 → P-05 | El crédito debe estar autorizado antes de asignar ruta y pipa para la entrega |
| A-26 | A-32 | P-05 → P-06 | La entrega confirmada (con remisión firmada) es el insumo para generar la factura |
| A-32 | A-13 | P-06 → P-03 | La factura emitida pasa a cobranza para monitoreo de vencimiento y recuperación |
| A-41 | A-06 | P-08 → P-02 | La decisión de mix de producto (más diesel, menos gasolina) ajusta la negociación con PEMEX TI |
| A-43 | A-22 | P-08 → P-05 | La reasignación de capacidad logística redefine qué zonas y rutas se priorizan |
| A-40 | A-28 | P-08 → P-06 | El análisis de rentabilidad por segmento define hacia qué tipos de cliente se enfoca la prospección |

---

## 2.5 Activity —[INVOLVES_EVENT]→ Event (clasificado por rol)

> **Rol "produce"**: la actividad genera o completa este evento de valor.
> **Rol "responde_a"**: la actividad es la primera acción en respuesta a este evento de demanda.

| Actividad | Evento | Rol | Descripción |
|-----------|--------|-----|-------------|
| A-31 | EV-D01 | responde_a | La recepción del pedido es la respuesta operativa al evento de demanda del cliente |
| A-28 | EV-D02 | responde_a | La identificación del prospecto activa el ciclo de propuesta y negociación comercial |
| A-03 | EV-D03 | responde_a | La detección de diferencial rentable activa el análisis que desencadena la negociación de suministro |
| A-16 | EV-D04 | responde_a | La alerta de vencimiento dispara el seguimiento y tramitación de renovación de permiso |
| A-33 | EV-D05 | responde_a | El incidente reportado por el cliente activa el protocolo de atención y resolución |
| A-40 | EV-D06 | responde_a | La decisión de revisión estratégica activa el análisis de rentabilidad por corredor y cliente |
| A-30 | EV-V01 | produce | El alta formal del cliente y la firma del contrato cierran el ciclo de adquisición |
| A-07 | EV-V02 | produce | La gestión de posición concluye cuando PEMEX TI confirma el cupo asignado |
| A-24 | EV-V03 | produce | La supervisión de carga completa produce el evento de carga documentada y sellada |
| A-26 | EV-V04 | produce | La entrega con remisión firmada produce el evento de valor más directo para el cliente |
| A-32 | EV-V05 | produce | La facturación CFDI formaliza el crédito e inicia el plazo de pago |
| A-13 | EV-V06 | produce | El seguimiento de cobranza culmina cuando el cliente liquida la factura |
| A-34 | EV-V07 | produce | La revisión comercial periódica es el espacio donde se consolida o activa la renovación |
| A-21 | EV-V08 | produce | La atención exitosa de la auditoría CRE produce el evento de habilitación regulatoria |

---

## 2.6 Relaciones adicionales de ontología

### Team —[OWNS]→ Process / Capability

| Equipo | Proceso(s) que lidera | Capability que posee |
|--------|-----------------------|----------------------|
| T-01 (Gobernanza) | P-03, P-04, P-07, P-08 | CAP-01 |
| T-02 (RRHH) | — | CAP-02 |
| T-03 (Tecnología) | — | CAP-03 |
| T-04 (Abastecimiento) | P-02 | CAP-04 |
| T-05 (Logística Interna) | — (co-ejecuta P-05) | CAP-05 |
| T-06 (Operaciones) | — (co-ejecuta P-04, P-05) | CAP-06 |
| T-07 (Logística Externa) | P-05 | CAP-07 |
| T-08 (Marketing y Ventas) | P-01, P-06 | CAP-08 |
| T-09 (Servicio Postventa) | — (co-ejecuta P-06) | CAP-09 |

### Activity —[PART_OF]→ Process
Derivado de la columna "Proceso" de la tabla 1.5.

### Activity —[SUPPORTS]→ Capability
| Actividades | Capability |
|-------------|------------|
| A-01 a A-05 | CAP-08 (Inteligencia Comercial y Ventas) |
| A-06 a A-10 | CAP-04 (Gestión de Abastecimiento) |
| A-11 a A-15 | CAP-01 (Gobernanza Corporativa) |
| A-16 a A-21 | CAP-01 (Gobernanza Corporativa) |
| A-22, A-23, A-25, A-26, A-31 | CAP-07 (Distribución y Entrega) |
| A-24, A-27 | CAP-05 (Logística de Recepción) + CAP-06 (Excelencia Operativa) |
| A-28 a A-32, A-34 | CAP-08 (Inteligencia Comercial y Ventas) |
| A-33 | CAP-09 (Gestión de Experiencia del Cliente) |
| A-35 a A-39 | CAP-01 (Gobernanza Corporativa) |
| A-40 a A-43 | CAP-01 (Gobernanza Corporativa) |

### Activity —[USES_SYSTEM]→ System
| Actividades | Sistema |
|-------------|---------|
| A-01, A-02, A-03, A-04 | S-05 (SIMA / PetroIntelligence) |
| A-07, A-09 | S-05 + S-02 (Pedidos y Remisiones) |
| A-16, A-19, A-20, A-21 | S-01 (Portal OPE-CRE) |
| A-18 | S-06 (Control de Calidad) |
| A-19, A-32 | S-07 (Portal SAT / CFDI) |
| A-22, A-23, A-24, A-25, A-26 | S-03 (GPS / Rastreo de Flota) |
| A-31, A-32 | S-02 (Pedidos y Remisiones) |
| A-12, A-13, A-14, A-15 | S-08 (Crédito y Cobranza) |
| A-32, A-13 | S-04 (ERP / Sistema Contable) |

### Metric —[HAS_DRIVER]→ MetricDriver
Derivado de la columna "Métrica padre" de la tabla 1.2.

---

## 2.7 Value Streams — Paths demanda → entrega de valor

> Cada Value Stream es un path de nodos Activity conectados por PRECEDES (intra + cross-proceso) que va de un evento de demanda a un evento de entrega de valor. Son verificación de que el grafo es correcto: si no existe un path conectado, hay un silo no modelado.

| Value Stream | Evento de demanda | Path de actividades | Evento de entrega |
|---|---|---|---|
| VS-01 Entrega de pedido recurrente | EV-D01 | A-31 → A-15 → A-22 → A-23 → A-24 → A-25 → A-26 | EV-V04 |
| VS-02 Ciclo completo pedido-cobro | EV-D01 | A-31 → A-15 → A-22 → A-23 → A-24 → A-25 → A-26 → A-32 → A-13 | EV-V06 |
| VS-03 Adquisición de cliente nuevo | EV-D02 | A-28 → A-29 → A-12 → A-30 | EV-V01 |
| VS-04 Aseguramiento de suministro | EV-D03 | A-03 → A-06 → A-07 | EV-V02 |
| VS-05 Renovación regulatoria | EV-D04 | A-16 → A-17 → A-18 → A-21 | EV-V08 |
| VS-06 Resolución de incidente | EV-D05 | A-33 → A-34 | EV-V07 |
| VS-07 Revisión de portafolio | EV-D06 | A-40 → A-41 → A-43 → A-22 | EV-V04 |

---

# BLOQUE 3 — Guía de cuantificación simulada

---

## 3.1 Fórmulas

```
V(A)           = 0.3·P + 0.4·C + 0.2·F + 0.1·R
B(A,M)         = 0.4·G(A,M) + 0.4·J(A,M) + 0.2·DV(A,M)
Relevance(A,M) = B(A,M) × V(A)
```

**Señales del bridge score B(A,M):**
- `G(A,M)` — evidencia directa en el grafo: ¿existe path Activity→Metric o Activity→Process→Metric?
  - AFFECTS directo: 1.0 × confianza del edge
  - Vía MetricDriver: 0.85 × confianza
  - Vía Process→CONTRIBUTES_TO: 0.70 × confianza
- `J(A,M)` — evidencia del journey: S(CJS,M) del CustomerJourneyStep que toca esta actividad
- `DV(A,M)` — evidencia de driver: ¿afecta un MetricDriver de M? (1.0 directo, 0.5 vía Process)

---

## 3.2 Criterios de asignación P — Posición en el flujo

| Valor P | Criterio para Energoil México |
|---------|-------------------------------|
| 1.0 | Último paso antes de la entrega o el cobro — sin esta actividad el valor no se materializa (A-26 entrega, A-13 cobro, A-30 alta de cliente) |
| 0.75 | Paso gating: su ausencia o retraso bloquea el siguiente eslabón del Value Stream (A-15 crédito, A-07 cupo TAR, A-16 permiso CRE, A-24 carga) |
| 0.5 | Parte del flujo estándar pero no cuello de botella estructural (A-23 programación de carga, A-32 facturación, A-18 muestreo NOM-016) |
| 0.25 | Soporte lejano al evento de valor — habilita condiciones pero no es paso crítico del path (A-27 mantenimiento, A-05 análisis competidores, A-38 seguros) |

---

## 3.3 Criterios de asignación C — Fuerza causal

| Valor C | Criterio para Energoil México |
|---------|-------------------------------|
| 1.0 | Causalidad directa y sin alternativa: si falla, la métrica colapsa de inmediato (permiso CRE vencido = cero operaciones; falla NOM-016 = producto retenido) |
| 0.75 | Causalidad fuerte con evidencia frecuente (retraso en carga TAR → entrega tardía en la mayoría de casos; huachicol en ruta → desvío y retraso confirmado) |
| 0.5 | Causalidad media: influye en combinación con otros factores (ruteo ineficiente + tráfico + disponibilidad de pipa = retraso; ninguno solo es determinante) |
| 0.25 | Causalidad baja o indirecta — rara vez determinante de forma aislada (análisis de competidores, revisión de portafolio trimestral, gestión de seguros) |

---

## 3.4 Criterios de asignación F — Frecuencia

| Valor F | Frecuencia operativa |
|---------|----------------------|
| 1.0 | Diaria o por cada entrega — presente en prácticamente cada operación (monitoreo de precios, ruteo, descarga, facturación, monitoreo GPS) |
| 0.75 | Semanal o por lote — afecta a la mayoría de operaciones del período (gestión de cupo TAR, monitoreo de cartera, análisis de diferencial de precio) |
| 0.5 | Mensual — cubre un subconjunto importante (reporte IEPS, evaluación crediticia, análisis de riesgo de cartera, rentabilidad por corredor) |
| 0.25 | Trimestral, anual o según evento — ocurre esporádicamente (renovación de permisos SCT/ASEA, expansión a nuevas zonas, auditorías CRE, seguros) |

---

## 3.5 Criterios de asignación R — Riesgo

| Valor R | Criterio para Energoil México |
|---------|-------------------------------|
| 1.0 | Riesgo sistémico: la falla detiene toda la operación o genera pérdida de clientes clave (permiso CRE vencido, falla NOM-016 en auditoría, huachicol en ruta principal) |
| 0.75 | Riesgo alto: afecta ingresos relevantes o compromete confianza del cliente (falla de entrega a cliente ancla, morosidad de cuenta grande, incidente SCT en ruta) |
| 0.5 | Riesgo medio: impacta a un segmento o genera reproceso significativo (retraso de ruteo en zona específica, error de facturación, falla de GPS en una pipa) |
| 0.25 | Riesgo bajo: genera ineficiencia o molestia pero rara vez escala (informe tardío, revisión comercial diferida, análisis de competidor omitido) |

---

## 3.6 Tabla de cuantificación por actividad

> Pesos: wP=0.3, wC=0.4, wF=0.2, wR=0.1 | V(A) = 0.3·P + 0.4·C + 0.2·F + 0.1·R

| ID | P | C | F | R | V(A) | Métricas con B > 0 |
|----|---|---|---|---|------|--------------------|
| A-01 | 0.25 | 0.75 | 1.0 | 0.25 | 0.60 | M-03, M-02 |
| A-02 | 0.25 | 0.75 | 1.0 | 0.50 | 0.63 | M-03 |
| A-03 | 0.25 | 0.50 | 0.75 | 0.25 | 0.46 | M-03, M-02 |
| A-04 | 0.25 | 0.50 | 0.75 | 0.25 | 0.46 | M-02 |
| A-05 | 0.25 | 0.25 | 0.50 | 0.25 | 0.33 | M-03 |
| A-06 | 0.75 | 1.0 | 0.50 | 0.75 | 0.80 | M-02 |
| A-07 | 0.75 | 1.0 | 0.75 | 0.75 | 0.85 | M-02, M-01 |
| A-08 | 0.25 | 0.50 | 0.50 | 0.50 | 0.44 | — |
| A-09 | 0.75 | 0.75 | 1.0 | 0.50 | 0.75 | M-01, M-02 |
| A-10 | 0.50 | 0.75 | 0.25 | 0.50 | 0.58 | M-02 |
| A-11 | 0.50 | 0.75 | 0.25 | 0.50 | 0.58 | M-05 |
| A-12 | 0.75 | 0.75 | 0.50 | 0.50 | 0.68 | M-05 |
| A-13 | 0.75 | 0.75 | 0.75 | 0.50 | 0.73 | M-05 |
| A-14 | 0.50 | 0.50 | 0.25 | 0.25 | 0.43 | — |
| A-15 | 0.75 | 1.0 | 0.75 | 0.75 | 0.85 | M-05, M-01 |
| A-16 | 0.75 | 1.0 | 0.50 | 1.0 | 0.83 | M-04 |
| A-17 | 0.75 | 1.0 | 0.25 | 1.0 | 0.78 | M-04 |
| A-18 | 0.50 | 1.0 | 0.75 | 1.0 | 0.80 | M-04 |
| A-19 | 0.50 | 0.75 | 0.50 | 0.75 | 0.65 | M-04 |
| A-20 | 0.25 | 0.75 | 0.25 | 0.75 | 0.55 | — |
| A-21 | 0.50 | 0.75 | 0.25 | 0.75 | 0.63 | M-04 |
| A-22 | 1.0 | 0.75 | 1.0 | 0.50 | 0.80 | M-01 |
| A-23 | 0.75 | 0.75 | 1.0 | 0.75 | 0.78 | M-01 |
| A-24 | 0.75 | 0.75 | 1.0 | 0.75 | 0.78 | M-01, M-04 |
| A-25 | 0.75 | 0.75 | 1.0 | 0.75 | 0.78 | M-01 |
| A-26 | 1.0 | 1.0 | 1.0 | 0.75 | 0.98 | M-01, M-02, M-06 |
| A-27 | 0.25 | 0.50 | 0.50 | 0.75 | 0.48 | — |
| A-28 | 0.25 | 0.50 | 0.75 | 0.25 | 0.44 | M-06 |
| A-29 | 0.50 | 0.75 | 0.50 | 0.25 | 0.58 | M-06, M-05 |
| A-30 | 0.50 | 0.75 | 0.25 | 0.25 | 0.55 | M-06 |
| A-31 | 0.75 | 0.75 | 1.0 | 0.50 | 0.78 | M-01, M-06 |
| A-32 | 0.75 | 0.75 | 1.0 | 0.50 | 0.78 | M-06 |
| A-33 | 0.75 | 1.0 | 0.50 | 0.75 | 0.83 | M-06 |
| A-34 | 0.75 | 0.75 | 0.25 | 0.50 | 0.65 | M-06 |
| A-35 | 0.50 | 0.75 | 0.75 | 0.75 | 0.68 | M-03 |
| A-36 | 0.50 | 0.75 | 0.50 | 0.75 | 0.65 | M-05 |
| A-37 | 0.50 | 0.75 | 0.50 | 1.0 | 0.70 | M-01, M-04 |
| A-38 | 0.25 | 0.50 | 0.25 | 1.0 | 0.48 | — |
| A-39 | 0.25 | 0.75 | 0.50 | 0.75 | 0.58 | M-04 |
| A-40 | 0.25 | 0.50 | 0.50 | 0.25 | 0.40 | M-06, M-03 |
| A-41 | 0.25 | 0.50 | 0.25 | 0.25 | 0.36 | M-03 |
| A-42 | 0.25 | 0.25 | 0.25 | 0.25 | 0.25 | M-06 |
| A-43 | 0.25 | 0.50 | 0.50 | 0.25 | 0.40 | M-01, M-03 |

---

## 3.7 Actividades con V alto y B = 0 en todas las métricas

> Hallazgo estratégico: operativamente críticas, pero sin trazabilidad a ningún valor percibido por el cliente. Se presentan en el demo como "habilitadores silenciosos" para la conversación sobre dónde proteger vs. dónde reducir.

| ID | Actividad | V(A) | Clasificación probable |
|----|-----------|------|------------------------|
| A-08 | Evaluación de proveedores alternativos | 0.44 | Infraestructura de contingencia — clientes no la perciben, pero protege M-02 cuando PEMEX falla |
| A-14 | Activación de factoraje | 0.43 | Mecanismo interno de tesorería invisible al cliente — habilita el crédito pero no lo toca directamente |
| A-20 | Gestión CURR y obligaciones ASEA | 0.55 | Infraestructura regulatoria — sin ella la operación no puede existir, pero ningún cliente la menciona |
| A-27 | Mantenimiento preventivo de flota | 0.48 | Habilitador silencioso — solo visible cuando falla; protege M-01 pero no aparece en el journey |
| A-38 | Gestión de seguros de flota y carga | 0.48 | Infraestructura de riesgo — invisible hasta el incidente; no conecta con ninguna métrica directamente |
| A-41 | Revisión de mix de producto | 0.36 | Decisión interna estratégica sin contacto con el cliente en el corto plazo |
| A-42 | Evaluación de nuevos segmentos | 0.25 | Exploración futura — sin impacto en el ciclo operativo actual ni en el journey existente |

---

## 3.8 Próximos pasos

1. Ingestar nodos del Bloque 1 al sistema Python como objetos estructurados (respetar IDs)
2. Ingestar relaciones del Bloque 2, incluyendo las cross-proceso de la sección 2.4.2
3. Verificar que exista un path PRECEDES conectado para cada Value Stream del cuadro 2.7
4. Cargar valores P, C, F, R de la tabla 3.6 como atributos de nodos Activity
5. Calcular V(A) como atributo computado
6. Calcular B(A,M) para cada par (Activity, Metric) con los signals G, J, DV
7. Calcular Relevance(A,M) = B(A,M) × V(A) y generar ranking por métrica
8. Agregar a nivel Process, Team y Área Porter para narrativa ejecutiva
9. **No ingestar** el Bloque 4 — usarlo solo como conjunto de prueba para validar que el sistema los detecta como B=0 / baja relevancia

---

---
