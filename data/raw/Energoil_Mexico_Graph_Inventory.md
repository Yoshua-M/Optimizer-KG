# ENERGOIL MÉXICO — Inventario de Nodos y Relaciones
## Grafo de Conocimiento | Documento de trabajo para construcción del demo | Junio 2026

---

> **Uso de este documento:** Define todos los nodos y relaciones que conformarán el grafo de conocimiento de Energoil México. Los datos son simulados pero construidos con lógica real del sector de distribución y trading de combustibles en México — regulación CRE/NOM-016/ASEA, dinámica de terminales PEMEX (TAR), y segmentos de cliente industrial, gasolinero y autoconsumo.

---

# BLOQUE 1 — Nodos

---

## 1.1 Metric (6 nodos)

Anclas de valor extraídas de las necesidades de los clientes de Energoil. Todo el análisis de relevancia se calcula contra estas métricas.

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

Factores que descomponen cada métrica. Permiten trazar rutas más finas entre actividades y métricas a través de sus drivers.

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

Momentos de la experiencia del cliente de Energoil. Son el puente entre las operaciones internas y el valor percibido por el cliente.

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

Corresponden directamente a los 8 macroprocesos del documento estratégico, adaptados al contexto operativo mexicano.

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

Unidad mínima de trabajo. Aquí se calculan P, C, F, R y se conectan acciones concretas con el valor del negocio.

| ID | Proceso | Nombre de la Actividad | Equipo responsable | Frecuencia |
|----|---------|------------------------|--------------------|------------|
| A-01 | P-01 | Monitoreo diario de precios rack PEMEX por terminal TAR | Trading / Inteligencia | Diaria |
| A-02 | P-01 | Seguimiento de variaciones del IEPS y estímulos fiscales | Trading / Inteligencia | Diaria |
| A-03 | P-01 | Análisis de diferencial de precio por corredor y región | Trading / Inteligencia | Semanal |
| A-04 | P-01 | Monitoreo de demanda por sector (minería, transporte, agrícola) | Trading / Inteligencia | Semanal |
| A-05 | P-01 | Análisis de movimientos de competidores y nuevas marcas CRE | Trading / Inteligencia | Quincenal |
| A-06 | P-02 | Negociación de volumen y precio con PEMEX TI (contrato asociado) | Abastecimiento | Mensual |
| A-07 | P-02 | Gestión de posición de compra y asignación de cupo en TAR | Abastecimiento | Semanal |
| A-08 | P-02 | Evaluación y contacto con importadores / proveedores alternativos | Abastecimiento | Mensual |
| A-09 | P-02 | Seguimiento de disponibilidad de producto en terminales asignadas | Abastecimiento | Diaria |
| A-10 | P-02 | Cierre de contratos spot en caso de desabasto o diferencial favorable | Abastecimiento | Según evento |
| A-11 | P-03 | Negociación y renovación de líneas de crédito con bancos | Finanzas / Tesorería | Trimestral |
| A-12 | P-03 | Evaluación crediticia de nuevos clientes | Finanzas / Tesorería | Por cliente nuevo |
| A-13 | P-03 | Monitoreo de cartera y gestión de cobranza | Finanzas / Tesorería | Semanal |
| A-14 | P-03 | Activación de factoraje para acelerar ciclo de cobro | Finanzas / Tesorería | Según necesidad |
| A-15 | P-03 | Autorización y control de crédito a clientes activos | Finanzas / Tesorería | Por pedido |
| A-16 | P-04 | Seguimiento de vigencia de permisos CRE de comercialización | Compliance / Legal | Mensual |
| A-17 | P-04 | Gestión de renovación de permisos SCT para flota de transporte | Compliance / Legal | Anual |
| A-18 | P-04 | Control de calidad del producto: muestreo y prueba NOM-016 | Compliance / Legal | Por lote |
| A-19 | P-04 | Reporte de obligaciones fiscales IEPS ante SAT | Compliance / Legal | Mensual |
| A-20 | P-04 | Gestión de CURR y obligaciones ASEA de seguridad operativa | Compliance / Legal | Anual |
| A-21 | P-04 | Atención de verificaciones y auditorías CRE en campo | Compliance / Legal | Según evento |
| A-22 | P-05 | Planeación y asignación de rutas de entrega por zona | Logística / Operaciones | Diaria |
| A-23 | P-05 | Programación de cargas en terminal TAR (ventanas de carga) | Logística / Operaciones | Diaria |
| A-24 | P-05 | Supervisión de carga: aforo, sellos y documentación de traslado | Logística / Operaciones | Por carga |
| A-25 | P-05 | Monitoreo GPS de pipas en ruta y gestión de incidencias | Logística / Operaciones | Tiempo real |
| A-26 | P-05 | Entrega en planta cliente: descarga, aforo y firma de remisión | Logística / Operaciones | Por entrega |
| A-27 | P-05 | Mantenimiento preventivo y correctivo de flota de pipas | Logística / Operaciones | Mensual |
| A-28 | P-06 | Prospección y calificación de nuevos clientes industriales y gasolineras | Comercial | Continua |
| A-29 | P-06 | Elaboración y negociación de propuesta comercial | Comercial | Por prospecto |
| A-30 | P-06 | Alta de cliente: documentación, contrato y apertura en sistema | Comercial | Por cliente nuevo |
| A-31 | P-06 | Recepción y confirmación de pedidos | Comercial | Diaria |
| A-32 | P-06 | Facturación y envío de documentos fiscales al cliente | Comercial | Por entrega |
| A-33 | P-06 | Atención de incidencias y reclamos post-entrega | Comercial / Ops | Según evento |
| A-34 | P-06 | Visita de revisión comercial periódica con cliente clave | Comercial | Trimestral |
| A-35 | P-07 | Monitoreo de riesgo de precio: exposición a volatilidad PEMEX/IEPS | Riesgos | Semanal |
| A-36 | P-07 | Evaluación de riesgo de crédito de cartera activa | Riesgos / Finanzas | Mensual |
| A-37 | P-07 | Análisis de riesgo de huachicol por ruta y zona de operación | Riesgos / Logística | Mensual |
| A-38 | P-07 | Gestión de seguros: flota, carga, responsabilidad civil ecológica | Riesgos | Anual |
| A-39 | P-07 | Monitoreo de cambios regulatorios CRE / SENER / SAT | Riesgos / Compliance | Mensual |
| A-40 | P-08 | Análisis de rentabilidad por cliente, producto y corredor | Dirección / Trading | Mensual |
| A-41 | P-08 | Revisión de mix de producto y decisión de expansión (diesel, ULSD, gasolina) | Dirección | Trimestral |
| A-42 | P-08 | Evaluación de nuevos segmentos o zonas geográficas | Dirección | Trimestral |
| A-43 | P-08 | Reasignación de capacidad logística hacia rutas de mayor margen | Dirección / Logística | Mensual |

---

## 1.6 Team (8 nodos)

| ID | Nombre del Equipo | Rol en la operación |
|----|-------------------|---------------------|
| T-01 | Trading / Inteligencia Comercial | Monitorea precios, identifica oportunidades de margen y gestiona posición de compra |
| T-02 | Abastecimiento | Negocia y administra contratos con PEMEX TI y proveedores alternativos |
| T-03 | Finanzas / Tesorería | Gestiona capital de trabajo, crédito a clientes, cobranza y relación bancaria |
| T-04 | Compliance / Legal | Administra permisos CRE, SCT, ASEA, calidad NOM-016 y obligaciones fiscales IEPS |
| T-05 | Logística / Operaciones | Opera la flota de pipas, gestiona rutas, cargas en terminal y entregas al cliente |
| T-06 | Comercial | Prospecta, negocia y gestiona la relación con clientes industriales y gasolineras |
| T-07 | Dirección General / Estrategia | Define la estrategia de portafolio, supervisa rentabilidad y toma decisiones de inversión |
| T-08 | Riesgos | Identifica, mide y mitiga riesgos de precio, crédito, operativo y regulatorio |

---

## 1.7 Capability (8 nodos)

| ID | Nombre de la Capacidad | Descripción |
|----|------------------------|-------------|
| CAP-01 | Inteligencia de Precios y Mercado | Capacidad de monitorear y anticipar movimientos de precio rack, IEPS y demanda sectorial |
| CAP-02 | Gestión de Abastecimiento | Capacidad de asegurar volumen competitivo en terminales PEMEX y fuentes alternativas |
| CAP-03 | Financiamiento Comercial | Capacidad de extender crédito a clientes y sostener el ciclo operativo con capital propio o bancario |
| CAP-04 | Cumplimiento Regulatorio | Capacidad de operar sin interrupciones cumpliendo CRE, NOM-016, SCT y ASEA |
| CAP-05 | Logística de Distribución | Capacidad de entregar combustible a tiempo, en volumen y con trazabilidad documental |
| CAP-06 | Gestión Comercial y de Clientes | Capacidad de adquirir, retener y hacer crecer clientes en segmentos industrial y retail |
| CAP-07 | Gestión de Riesgos Operativos | Capacidad de identificar y mitigar riesgos de precio, crédito, huachicol y regulatorio |
| CAP-08 | Optimización de Portafolio | Capacidad de tomar decisiones de mezcla producto-cliente-región para maximizar margen |

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

## 1.9 Event (8 nodos)

| ID | Nombre del Evento | event_type | Qué activa o representa |
|----|-------------------|------------|-------------------------|
| EV-01 | Contrato de suministro firmado | demand | Formalización del acuerdo comercial con el cliente; activa el ciclo operativo |
| EV-02 | Asignación de cupo en terminal TAR | demand | PEMEX TI confirma volumen y ventana de carga; habilita el abastecimiento |
| EV-03 | Carga completada en terminal | demand | La pipa sale de la TAR con producto sellado, aforado y documentado |
| EV-04 | Entrega confirmada por cliente | value_realization | El cliente firma la remisión; el volumen queda recibido y se activa la factura |
| EV-05 | Factura emitida (CFDI) | value_realization | Se emite el comprobante fiscal; inicia el plazo de crédito acordado |
| EV-06 | Cobro recibido | value_realization | El cliente liquida la factura; el capital se libera para el siguiente ciclo de compra |
| EV-07 | Renovación de contrato o expansión | value_realization | El cliente confirma continuidad o amplía volumen; consolida la retención |
| EV-08 | Incidente de servicio reportado | demand | El cliente reporta falla (retraso, calidad, volumen); activa protocolo de atención |

---

# BLOQUE 2 — Relaciones

---

## 2.1 Activity —[AFFECTS]→ Metric (23 relaciones)

Núcleo del bridge score G(A,M). La columna de fuerza causal es la base para calibrar C.

| Actividad | Métrica | Fuerza causal |
|-----------|---------|---------------|
| A-01 | M-03 | Alta: precios rack son la base del diferencial de margen |
| A-02 | M-03 | Alta: IEPS afecta directamente el costo y el margen disponible |
| A-06 | M-02 | Alta: el contrato define el volumen asegurado con el proveedor |
| A-07 | M-02 | Alta: el cupo en TAR determina la disponibilidad real de producto |
| A-09 | M-01 | Alta: disponibilidad en terminal es prerequisito de entrega puntual |
| A-12 | M-05 | Alta: la evaluación crediticia define el crédito que se puede otorgar |
| A-13 | M-05 | Media: cobranza eficiente sostiene la capacidad de dar crédito nuevo |
| A-15 | M-05 | Alta: autorización de crédito es el acto concreto de entregar financiamiento |
| A-16 | M-04 | Crítica: permiso CRE vencido detiene toda operación comercial |
| A-17 | M-04 | Alta: SCT vencido inmoviliza pipas y bloquea entregas |
| A-18 | M-04 | Crítica: falla NOM-016 genera incidente regulatorio y retención de producto |
| A-19 | M-04 | Alta: incumplimiento IEPS ante SAT genera multas y posible suspensión |
| A-22 | M-01 | Alta: el ruteo determina directamente la puntualidad de la entrega |
| A-23 | M-01 | Alta: la programación de ventanas de carga es cuello de botella frecuente |
| A-24 | M-04 | Alta: documentación de traslado incorrecta es fuente de incidentes regulatorios |
| A-26 | M-01 | Crítica: la entrega es el evento final que define puntualidad |
| A-26 | M-02 | Crítica: la entrega determina el volumen efectivamente recibido por el cliente |
| A-33 | M-06 | Alta: la respuesta a incidencias define la percepción de confiabilidad del cliente |
| A-34 | M-06 | Alta: la revisión periódica es el mecanismo principal de retención de clientes clave |
| A-35 | M-03 | Media: gestión de exposición de precio protege el margen ante volatilidad |
| A-37 | M-01 | Media: rutas con alto riesgo de huachicol generan desvíos y retrasos |
| A-37 | M-04 | Media: incidentes de huachicol pueden generar irregularidades documentales |
| A-40 | M-06 | Media: visibilidad de rentabilidad por cliente permite priorizar retención |

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

Fuente del signal J(A,M) en el bridge score — conectan operaciones internas con momentos de experiencia del cliente.

| Actividad | CustomerJourneyStep |
|-----------|---------------------|
| A-28 | CJS-01 |
| A-29 | CJS-02 |
| A-30 | CJS-03 |
| A-31 | CJS-04 |
| A-31 | CJS-05 |
| A-32 | CJS-05 |
| A-33 | CJS-06 |
| A-34 | CJS-07 |
| A-34 | CJS-08 |
| A-26 | CJS-04 |
| A-26 | CJS-05 |

---

## 2.4 Activity —[PRECEDES]→ Activity (32 relaciones)

Base para calcular P (posición en el flujo) mediante distancia al evento de valor.

### P-01 — Inteligencia Comercial
| Origen | Destino |
|--------|---------|
| A-01 | A-02 |
| A-02 | A-03 |
| A-03 | A-04 |
| A-04 | A-05 |

### P-02 — Aseguramiento de Suministro
| Origen | Destino |
|--------|---------|
| A-06 | A-07 |
| A-07 | A-09 |
| A-09 | A-10 |

### P-03 — Financiamiento de Operaciones
| Origen | Destino |
|--------|---------|
| A-11 | A-12 |
| A-12 | A-15 |
| A-15 | A-13 |
| A-13 | A-14 |

### P-04 — Gestión Regulatoria y Compliance
| Origen | Destino |
|--------|---------|
| A-16 | A-17 |
| A-17 | A-18 |
| A-18 | A-19 |
| A-19 | A-20 |
| A-20 | A-21 |

### P-05 — Ejecución Logística
| Origen | Destino |
|--------|---------|
| A-22 | A-23 |
| A-23 | A-24 |
| A-24 | A-25 |
| A-25 | A-26 |
| A-26 | A-27 |

### P-06 — Comercialización y Gestión de Clientes
| Origen | Destino |
|--------|---------|
| A-28 | A-29 |
| A-29 | A-30 |
| A-30 | A-31 |
| A-31 | A-32 |
| A-32 | A-33 |
| A-33 | A-34 |

### P-07 — Gestión de Riesgos
| Origen | Destino |
|--------|---------|
| A-35 | A-36 |
| A-36 | A-37 |
| A-37 | A-38 |
| A-38 | A-39 |

### P-08 — Optimización de Portafolio
| Origen | Destino |
|--------|---------|
| A-40 | A-41 |
| A-41 | A-42 |
| A-42 | A-43 |

---

## 2.5 Relaciones adicionales de ontología

Las siguientes relaciones completan el grafo. Se derivan directamente de las tablas del Bloque 1.

### Team —[PERFORMS]→ Activity
Cada actividad tiene asignado un equipo responsable principal en la columna "Equipo responsable" de la tabla 1.5.

### Team —[OWNS]→ Process / Capability
| Equipo | Process | Capability |
|--------|---------|------------|
| T-01 | P-01 | CAP-01 |
| T-02 | P-02 | CAP-02 |
| T-03 | P-03 | CAP-03 |
| T-04 | P-04 | CAP-04 |
| T-05 | P-05 | CAP-05 |
| T-06 | P-06 | CAP-06 |
| T-08 | P-07 | CAP-07 |
| T-07 | P-08 | CAP-08 |

### Activity —[PART_OF]→ Process
Derivado directamente de la columna "Proceso" de la tabla 1.5.

### Activity —[SUPPORTS]→ Capability
| Actividades | Capability |
|-------------|------------|
| A-01 a A-05 | CAP-01 |
| A-06 a A-10 | CAP-02 |
| A-11 a A-15 | CAP-03 |
| A-16 a A-21 | CAP-04 |
| A-22 a A-27 | CAP-05 |
| A-28 a A-34 | CAP-06 |
| A-35 a A-39 | CAP-07 |
| A-40 a A-43 | CAP-08 |

### Activity —[USES_SYSTEM]→ System
| Actividades | Sistema |
|-------------|---------|
| A-01, A-02, A-03 | S-05 (SIMA / PetroIntelligence) |
| A-09, A-07 | S-05 (SIMA) + S-02 (Pedidos) |
| A-16, A-19, A-20, A-21 | S-01 (Portal OPE-CRE) |
| A-18 | S-06 (Control de Calidad) |
| A-19, A-32 | S-07 (Portal SAT / CFDI) |
| A-22, A-23, A-24, A-25 | S-03 (GPS / Rastreo) |
| A-31, A-32 | S-02 (Pedidos y Remisiones) |
| A-12, A-13, A-14, A-15 | S-08 (Crédito y Cobranza) |
| A-32, A-13 | S-04 (ERP / Contable) |

### Activity —[INVOLVES_EVENT]→ Event
| Actividad | Evento que activa |
|-----------|-------------------|
| A-30 | EV-01 (Contrato firmado) |
| A-07 | EV-02 (Cupo en TAR asignado) |
| A-24 | EV-03 (Carga completada en terminal) |
| A-26 | EV-04 (Entrega confirmada por cliente) |
| A-32 | EV-05 (Factura emitida CFDI) |
| A-13 | EV-06 (Cobro recibido) |
| A-34 | EV-07 (Renovación o expansión) |
| A-33 | EV-08 (Incidente de servicio reportado) |

### Metric —[HAS_DRIVER]→ MetricDriver
Derivado directamente de la columna "Métrica padre" de la tabla 1.2.

---

# BLOQUE 3 — Guía de cuantificación simulada

---

## 3.1 Fórmulas

```
V(A)          = 0.3·P + 0.4·C + 0.2·F + 0.1·R
B(A,M)        = 0.4·G(A,M) + 0.4·J(A,M) + 0.2·DV(A,M)
Relevance(A,M) = B(A,M) × V(A)
```

**Señales del bridge score B(A,M):**
- `G(A,M)` — evidencia directa en el grafo: ¿existe un path Activity→Metric o Activity→Process→Metric?
- `J(A,M)` — evidencia del journey: ¿toca esta actividad un CustomerJourneyStep vinculado a la métrica M?
- `DV(A,M)` — evidencia de driver: ¿afecta esta actividad a un MetricDriver de M?

---

## 3.2 Criterios de asignación P — Posición en el flujo

| Valor P | Criterio para Energoil México |
|---------|-------------------------------|
| 1.0 | La actividad es el último paso antes de que el cliente reciba el producto o el valor se materialice (entrega confirmada, renovación de contrato) |
| 0.75 | Paso gating: si se retrasa o falla, la entrega o el cobro se bloquea (carga en terminal, autorización de crédito, vigencia de permiso CRE) |
| 0.5 | Parte del flujo estándar pero no cuello de botella estructural (monitoreo de ruta, facturación, muestreo NOM-016) |
| 0.25 | Soporte lejano al evento de valor (mantenimiento de flota, análisis de competidores, revisión de portafolio trimestral) |

---

## 3.3 Criterios de asignación C — Fuerza causal

| Valor C | Criterio para Energoil México |
|---------|-------------------------------|
| 1.0 | Causalidad directa: si esta actividad falla, la métrica cae de forma inmediata y sin alternativa (permiso CRE vencido → cero operaciones) |
| 0.75 | Causalidad fuerte con casos frecuentes (retrasos en carga TAR → entrega tardía; falla NOM-016 → incidente regulatorio en la mayoría de los casos) |
| 0.5 | Causalidad media: influye en combinación con otros factores (ruteo ineficiente contribuye a retrasos junto con tráfico o disponibilidad de pipa) |
| 0.25 | Causalidad baja o indirecta: rara vez determinante solo (análisis de portafolio trimestral sobre margen de un cliente específico) |

---

## 3.4 Criterios de asignación F — Frecuencia

| Valor F | Frecuencia operativa |
|---------|----------------------|
| 1.0 | Diaria o por cada entrega — ocurre en prácticamente cada operación (monitoreo de precios, ruteo, descarga, facturación) |
| 0.75 | Semanal o por lote — afecta a la mayoría de las operaciones del período (gestión de cupo TAR, monitoreo de cartera, análisis de diferencial) |
| 0.5 | Mensual — cubre un subconjunto importante (reporte IEPS, evaluación crediticia, análisis de riesgo de cartera) |
| 0.25 | Trimestral, anual o según evento — ocurre esporádicamente (renovación de permisos SCT/ASEA, expansión a nuevas zonas, auditorías CRE) |

---

## 3.5 Criterios de asignación R — Riesgo

| Valor R | Criterio para Energoil México |
|---------|-------------------------------|
| 1.0 | Riesgo sistémico: falla detiene toda la operación o genera pérdida de clientes clave (permiso CRE vencido, falla NOM-016 en auditoría, huachicol en ruta principal) |
| 0.75 | Riesgo alto: afecta ingresos relevantes o compromete la confianza del cliente (falla de entrega a cliente ancla, morosidad de cuenta grande, incidente SCT) |
| 0.5 | Riesgo medio: impacta a un segmento o genera reproceso significativo (retraso de ruteo en zona, error de facturación, falla de GPS en una pipa) |
| 0.25 | Riesgo bajo: genera ineficiencia o molestia pero rara vez escala (informe de portafolio tardío, revisión comercial diferida) |

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
| A-08 | 0.25 | 0.50 | 0.50 | 0.50 | 0.44 | M-02 |
| A-09 | 0.75 | 0.75 | 1.0 | 0.50 | 0.75 | M-01, M-02 |
| A-10 | 0.50 | 0.75 | 0.25 | 0.50 | 0.58 | M-02 |
| A-11 | 0.50 | 0.75 | 0.25 | 0.50 | 0.58 | M-05 |
| A-12 | 0.75 | 0.75 | 0.50 | 0.50 | 0.68 | M-05 |
| A-13 | 0.75 | 0.75 | 0.75 | 0.50 | 0.73 | M-05 |
| A-14 | 0.50 | 0.50 | 0.25 | 0.25 | 0.43 | M-05 |
| A-15 | 0.75 | 1.0 | 0.75 | 0.75 | 0.85 | M-05 |
| A-16 | 0.75 | 1.0 | 0.50 | 1.0 | 0.83 | M-04 |
| A-17 | 0.75 | 1.0 | 0.25 | 1.0 | 0.78 | M-04 |
| A-18 | 0.50 | 1.0 | 0.75 | 1.0 | 0.80 | M-04 |
| A-19 | 0.50 | 0.75 | 0.50 | 0.75 | 0.65 | M-04 |
| A-20 | 0.25 | 0.75 | 0.25 | 0.75 | 0.55 | M-04 |
| A-21 | 0.50 | 0.75 | 0.25 | 0.75 | 0.63 | M-04 |
| A-22 | 1.0 | 0.75 | 1.0 | 0.50 | 0.80 | M-01 |
| A-23 | 0.75 | 0.75 | 1.0 | 0.75 | 0.78 | M-01 |
| A-24 | 0.75 | 0.75 | 1.0 | 0.75 | 0.78 | M-01, M-04 |
| A-25 | 0.75 | 0.75 | 1.0 | 0.75 | 0.78 | M-01 |
| A-26 | 1.0 | 1.0 | 1.0 | 0.75 | 0.98 | M-01, M-02, M-06 |
| A-27 | 0.25 | 0.50 | 0.50 | 0.75 | 0.48 | M-01 |
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
| A-38 | 0.25 | 0.50 | 0.25 | 1.0 | 0.48 | M-04 |
| A-39 | 0.25 | 0.75 | 0.50 | 0.75 | 0.58 | M-04 |
| A-40 | 0.25 | 0.50 | 0.50 | 0.25 | 0.40 | M-06, M-03 |
| A-41 | 0.25 | 0.50 | 0.25 | 0.25 | 0.36 | M-03 |
| A-42 | 0.25 | 0.25 | 0.25 | 0.25 | 0.25 | M-06 |
| A-43 | 0.25 | 0.50 | 0.50 | 0.25 | 0.40 | M-01, M-03 |

---

## 3.7 Actividades con B = 0 en todas las métricas

Las siguientes actividades tienen V alto pero no tienen path trazable a ninguna métrica de cliente. Se presentan en el demo como **"Actividades críticas sin trazabilidad a valor cliente"** — hallazgo estratégico en sí mismo.

| ID | Actividad | V(A) | Razón probable de B = 0 |
|----|-----------|------|--------------------------|
| A-08 | Evaluación de proveedores alternativos | 0.44 | Actividad de respaldo; clientes no la perciben directamente |
| A-14 | Activación de factoraje | 0.43 | Mecanismo interno de tesorería invisible al cliente |
| A-20 | Gestión CURR y obligaciones ASEA | 0.55 | Infraestructura regulatoria; clientes no la mencionan |
| A-27 | Mantenimiento preventivo de flota | 0.48 | Habilitador silencioso; sólo visible cuando falla |
| A-38 | Gestión de seguros | 0.48 | Infraestructura de riesgo invisible hasta el incidente |
| A-41 | Revisión de mix de producto | 0.36 | Decisión interna estratégica sin contacto con cliente |
| A-42 | Evaluación de nuevas zonas | 0.25 | Exploración futura sin impacto operativo actual |

> **Nota para el demo:** Estas actividades son candidatas a la conversación sobre "¿qué protegemos aunque el cliente no lo vea?" vs. "¿qué podemos reducir o externalizar?".

---

## 3.8 Próximos pasos

1. Ingestar todos los nodos del Bloque 1 al sistema Python como objetos estructurados
2. Ingestar todas las relaciones del Bloque 2 como edges del grafo
3. Cargar los valores P, C, F, R de la tabla 3.6 como atributos de cada nodo Activity
4. Calcular V(A) como atributo computado
5. Calcular B(A,M) para cada par (Activity, Metric) usando los signals G, J y DV
6. Calcular Relevance(A,M) = B(A,M) × V(A) y generar el ranking por métrica
7. Agregar a nivel Process y Team para mostrar contribución relativa en la demo
