# Optimizer — Analíticas del Grafo por Área de Porter

> Catálogo de análisis disponibles organizados por área operativa. Para cada análisis se incluye: descripción técnica para el equipo de implementación, mensaje al ejecutivo para la interfaz, subáreas beneficiadas, setup del grafo y librería.

---

## Convención de setup

Todas las analíticas asumen que el grafo ya tiene nodos Activity con atributos P, C, F, R, V(A) y aristas tipificadas según la ontología. La biblioteca principal es `networkx`. Complementos: `scipy/numpy` para álgebra lineal, `pgmpy` para inferencia causal, `python-louvain` para detección de comunidades.

---

## Actividades de soporte

---

### Núcleo de gobernanza

---

**G-01 — Detección de actividades de gobernanza dominantes**

Identifica qué actividades de gobernanza actúan como dominadores de todos los value streams: toda ruta de demanda a valor las atraviesa obligatoriamente.

*Qué significa para esta área:* Revela cuáles controles de gobernanza (aprobación legal, validación de riesgo, autorización financiera) son no eludibles operativamente — no por diseño, sino por topología del grafo.

> **💬 Mensaje al ejecutivo**
> *Qué descubrimos:* Identificamos qué actividades de dirección, control o cumplimiento son pasos que absolutamente toda la operación debe atravesar — sin excepción y sin alternativa. No porque alguien lo decidió en un manual, sino porque así está estructurado el trabajo real de la organización.
> *Por qué funciona:* Trazamos todos los caminos posibles desde que llega una demanda hasta que se entrega valor al cliente. Los pasos que aparecen en el 100% de esos caminos son los dominantes. Si uno de ellos falla, no hay ruta alterna: la operación se detiene.

**Subáreas beneficiadas:** Dirección general · Gestión de riesgos · Asuntos legales · Calidad corporativa

- **Setup:** Subgrafo Activity/PRECEDES de todo el grafo. Añadir super-source conectado a todos los Eventos de demanda. Etiquetar actividades de gobernanza con atributo `area='gobernanza'`.
- **Función:** `nx.immediate_dominators(G, source)` → filtrar resultados por `area='gobernanza'`
- **Librería:** `networkx`

> **🎨 Visualización en interfaz — ✅ Resaltado genérico**
> Resalta los nodos Activity de gobernanza que son dominadores. Color sólido de alerta para distinguirlos del resto del grafo. El resto del grafo se atenúa.
> *Elementos resaltados: Nodos Activity (gobernanza dominante)*

---

**G-02 — Puntaje de riesgo estructural de controles**

Combina betweenness centrality + condición de punto de articulación para cada actividad de gobernanza, generando un puntaje de fragilidad institucional.

*Qué significa para esta área:* Si un control regulatorio o de riesgo tiene betweenness alto Y es punto de articulación, su falla no solo detiene su proceso — desconecta el grafo completo.

> **💬 Mensaje al ejecutivo**
> *Qué descubrimos:* Calculamos cuáles de sus controles de gobernanza son los más frágiles en términos de impacto: no los que fallan más seguido, sino los que si fallan una sola vez generan el mayor daño aguas abajo en toda la organización.
> *Por qué funciona:* Medimos cuántos flujos operativos pasan por cada control y si existe alguna ruta alternativa que los evite. Un control que concentra muchos flujos y no tiene alternativa es estructuralmente frágil — no importa qué tan robusto parezca en papel.

**Subáreas beneficiadas:** Gestión de riesgos · Compliance · Calidad corporativa · Finanzas y contabilidad

- **Setup:** Subgrafo Activity/PRECEDES completo. Calcular betweenness. Calcular puntos de articulación en versión no dirigida. Cruzar ambos resultados para actividades de gobernanza.
- **Función:** `nx.betweenness_centrality(G)` + `nx.articulation_points(G.to_undirected())`
- **Librería:** `networkx`

> **🎨 Visualización en interfaz — ✅ Resaltado con gradiente**
> Nodos de gobernanza coloreados en gradiente según su puntaje de fragilidad (verde → rojo). Las aristas donde son puntos de articulación se resaltan en rojo.
> *Elementos resaltados: Nodos Activity + aristas críticas*

---

**G-03 — Simulación de cascada por falla regulatoria**

Dada una actividad de compliance o riesgo que falla, recalcula qué Métricas pierden cobertura upstream.

*Qué significa para esta área:* Cuantifica el costo operativo de un fallo de gobernanza en términos de métricas de valor cliente afectadas, no solo en términos de multas o sanciones.

> **💬 Mensaje al ejecutivo**
> *Qué descubrimos:* Simulamos qué pasaría si un control regulatorio o de cumplimiento específico dejara de funcionar. El resultado muestra exactamente qué indicadores de valor para sus clientes quedarían desprotegidos como consecuencia directa.
> *Por qué funciona:* Seguimos hacia adelante todas las actividades que dependen del control que falló, y vemos cuáles métricas de cliente ya no tienen ninguna actividad interna que las sostenga. Es como retirar una pieza del engranaje y ver qué ruedas dejan de girar.

**Subáreas beneficiadas:** Gestión de riesgos · Asuntos legales · Relaciones institucionales · Dirección general

- **Setup:** Grafo completo con aristas AFFECTS y CONTRIBUTES_TO. Remover temporalmente la actividad degradada. Recalcular `nx.ancestors(G, metric_node)` para cada Metric.
- **Función:** `nx.ancestors(G, node)` antes y después de remoción. Diferencia = actividades que pierden trazabilidad.
- **Librería:** `networkx`

> **🎨 Visualización en interfaz — 🔀 Resaltado en cascada**
> Dos capas: nodos directamente amenazados (rojo fuerte) y nodos Metric que pierden cobertura (naranja punteado). Las aristas que conectan ambas capas se resaltan para mostrar la ruta de impacto.
> *Elementos resaltados: Nodos Activity afectados + nodos Metric desconectados*

---

**G-04 — Conjunto mínimo de controles para continuidad**

El subconjunto más pequeño de actividades de gobernanza que garantiza al menos un camino desde cada Evento de demanda hasta cada Evento de valor.

*Qué significa para esta área:* Define el presupuesto mínimo de gobernanza que no puede recortarse sin comprometer los value streams.

> **💬 Mensaje al ejecutivo**
> *Qué descubrimos:* Identificamos el conjunto más pequeño posible de controles y actividades de dirección que, si se mantienen funcionando, garantizan que la operación pueda seguir entregando valor a los clientes aunque todo lo demás falle.
> *Por qué funciona:* Buscamos el "corte mínimo" del grafo: el menor número de puntos que, si se eliminan, desconectan completamente la demanda del cliente de su entrega de valor. Ese conjunto es el núcleo de gobernanza no negociable.

**Subáreas beneficiadas:** Dirección general · Gestión de riesgos · Finanzas y contabilidad · Asuntos legales

- **Setup:** Grafo Activity/PRECEDES con super-source y super-sink. Restringir el corte a nodos etiquetados como gobernanza.
- **Función:** `nx.minimum_node_cut(G, s=super_source, t=super_sink)`
- **Librería:** `networkx`

> **🎨 Visualización en interfaz — ✅ Resaltado genérico**
> Resalta el conjunto mínimo de nodos de gobernanza en color distintivo. Todo lo demás se atenúa significativamente para que el ejecutivo vea claramente el núcleo no negociable.
> *Elementos resaltados: Nodos Activity (conjunto mínimo)*

---

### Gestión de RRHH

---

**H-01 — Mapa de concentración de conocimiento crítico**

Para cada Team, suma el V(A) de todas las actividades que ejecuta exclusivamente. Alta concentración = riesgo de knowledge hoarding.

*Qué significa para esta área:* Identifica dónde el conocimiento operativo crítico está concentrado en un solo equipo o persona — insumo para planes de sucesión y capacitación cruzada.

> **💬 Mensaje al ejecutivo**
> *Qué descubrimos:* Encontramos qué equipos o roles concentran actividades de alto valor que nadie más en la organización sabe hacer. Estas son las personas o áreas cuya salida generaría el mayor impacto operativo inmediato.
> *Por qué funciona:* Revisamos qué actividades tienen un único equipo responsable y cuánto valor aportan esas actividades a los clientes. Donde la combinación es "alta importancia + un solo responsable", hay un riesgo de dependencia de personas que la organización generalmente no tiene documentado.

**Subáreas beneficiadas:** Reclutamiento y selección · Capacitación · Cultura organizacional · Evaluación del desempeño

- **Setup:** Subgrafo bipartito Team–Activity con aristas PERFORMS. Filtrar actividades con exactamente 1 Team responsable y V(A) alto.
- **Función:** `nx.bipartite.degree_centrality(B, activity_nodes)` + filtro por exclusividad
- **Librería:** `networkx`

> **🎨 Visualización en interfaz — ✅ Resaltado con gradiente**
> Nodos Team coloreados por índice de concentración (mayor concentración = color más intenso). Al hacer clic en un Team, se resaltan las actividades exclusivas asociadas y su V(A).
> *Elementos resaltados: Nodos Team + nodos Activity exclusivos*

---

**H-02 — Simulación de impacto por pérdida de equipo**

Eliminar un nodo Team y recalcular qué Actividades quedan sin ejecutor y qué Métricas pierden cobertura.

*Qué significa para esta área:* Cuantifica el impacto de perder un equipo completo en términos de valor cliente expuesto.

> **💬 Mensaje al ejecutivo**
> *Qué descubrimos:* Simulamos qué pasaría si un equipo completo dejara de estar disponible — por rotación, reestructura o ausencia — y medimos qué indicadores de valor para sus clientes quedarían sin respaldo operativo.
> *Por qué funciona:* Retiramos del mapa de operaciones todas las actividades que ese equipo ejecuta y observamos qué métricas de cliente ya no tienen ningún proceso que las sostenga. Traduce el riesgo de talento a un número de negocio concreto.

**Subáreas beneficiadas:** Reclutamiento y selección · Compensación y beneficios · Capacitación · Cultura organizacional

- **Setup:** Grafo completo. Remover Team node y todas sus aristas PERFORMS. Recalcular reachability de Metrics desde Eventos de demanda.
- **Función:** `G.remove_node(team)` + `nx.ancestors(G, metric_node)` para cada métrica
- **Librería:** `networkx`

> **🎨 Visualización en interfaz — 🔀 Resaltado en cascada**
> Dos capas: actividades sin ejecutor tras la remoción del equipo (gris vacío) y métricas que pierden cobertura (naranja). Muestra visualmente qué queda huérfano.
> *Elementos resaltados: Nodos Activity huérfanos + nodos Metric expuestos*

---

**H-03 — Equipos puente entre value streams**

Detecta qué equipos aparecen como ejecutores de actividades críticas en más de un value stream.

*Qué significa para esta área:* Los equipos puente son los que más fricción sufren cuando se reorganiza la empresa y los primeros candidatos a centros de excelencia compartidos.

> **💬 Mensaje al ejecutivo**
> *Qué descubrimos:* Identificamos qué equipos están sirviendo como puente entre distintos flujos de valor de la organización — los que sin ellos, diferentes partes de la operación perderían coordinación entre sí.
> *Por qué funciona:* Medimos cuántos flujos operativos distintos dependen de cada equipo para conectarse entre sí. Los equipos que aparecen en más cruces son los conectores reales de la organización, independientemente de cómo esté dibujado el organigrama.

**Subáreas beneficiadas:** Cultura organizacional · Evaluación del desempeño · Relaciones laborales · Capacitación

- **Setup:** Proyección del grafo bipartito Team–Activity sobre nodos Team, con peso = número de value streams en los que aparece el equipo. Calcular betweenness en esta proyección.
- **Función:** `nx.bipartite.projected_graph(B, team_nodes)` + `nx.betweenness_centrality(proj)`
- **Librería:** `networkx`

> **🎨 Visualización en interfaz — ✅ Resaltado con gradiente**
> Nodos Team coloreados por su betweenness en la proyección bipartita. Los equipos puente aparecen más grandes y con color más intenso; las aristas que los conectan a múltiples value streams se resaltan.
> *Elementos resaltados: Nodos Team + aristas cross-stream*

---

**H-04 — Valor Shapley de capacidades de RRHH**

Atribución justa del valor que aporta cada Capability de RRHH a cada Métrica, considerando interacciones entre capacidades.

*Qué significa para esta área:* Responde qué capacidades de gestión de personas tienen impacto real en las métricas de negocio, más allá de la intuición.

> **💬 Mensaje al ejecutivo**
> *Qué descubrimos:* Calculamos cuánto contribuye cada capacidad del área de personas — onboarding, capacitación, evaluación, retención — al desempeño real de los indicadores de cliente, tomando en cuenta que muchas capacidades trabajan juntas y es difícil separar su contribución individual.
> *Por qué funciona:* Probamos matemáticamente todas las combinaciones posibles de capacidades y medimos qué diferencia hace cada una cuando se suma o se retira del grupo. El resultado es la contribución marginal justa de cada capacidad, sin sesgo por correlación.

**Subáreas beneficiadas:** Capacitación · Onboarding · Compensación y beneficios · Evaluación del desempeño

- **Setup:** Función característica v(S) = suma de Relevance(A,M) de actividades ejecutadas por equipos cuya capability pertenece a la coalición S. Iterar sobre todas las coaliciones de Capabilities de RRHH.
- **Función:** Implementación propia con `itertools.combinations` sobre Capability nodes de RRHH
- **Librería:** `itertools` + `networkx`

> **🎨 Visualización en interfaz — 📊 Representación especial**
> No apto para resaltado de grafo. Representación como gráfico de barras horizontales: una barra por Capability de RRHH, longitud = valor Shapley sobre la métrica seleccionada. Mostrar como panel lateral.
> *Elementos resaltados: Panel lateral — gráfico de barras de atribución*

---

### Desarrollo tecnológico

---

**T-01 — Criticidad tecnológica por sistema**

Para cada nodo System, suma el V(A) de todas las actividades que dependen de él. Produce un ranking de criticidad tecnológica.

*Qué significa para esta área:* Identifica qué sistemas son más críticos para el valor cliente — no por número de usuarios ni costo de licencia, sino por cuánta operación de alto valor sostienen.

> **💬 Mensaje al ejecutivo**
> *Qué descubrimos:* Ordenamos todos sus sistemas y herramientas tecnológicas según cuánto valor real soportan — no según cuánto cuestan o cuánta gente los usa, sino según qué tan importantes son las actividades operativas que dependen de ellos.
> *Por qué funciona:* Sumamos el valor de todas las actividades críticas que usan cada sistema. Un sistema que sostiene muchas actividades de alto impacto para el cliente recibe una puntuación alta, aunque sea una herramienta sencilla o antigua.

**Subáreas beneficiadas:** Arquitectura de sistemas · I+D · Gestión de datos · Soporte técnico

- **Setup:** Subgrafo bipartito Activity–System con aristas USES_SYSTEM y atributo V(A) en cada Activity. Sumar V(A) por System.
- **Función:** `nx.bipartite.weighted_projected_graph(B, system_nodes)` + suma de pesos
- **Librería:** `networkx`

> **🎨 Visualización en interfaz — ✅ Resaltado con gradiente**
> Nodos System coloreados en gradiente por su puntaje de criticidad tecnológica. Al hover, tooltip con lista de actividades dependientes y su V(A) acumulado.
> *Elementos resaltados: Nodos System (gradiente de criticidad)*

---

**T-02 — Detección de dependencias tecnológicas únicas**

Identifica sistemas que son la única tecnología que sostiene una o más actividades de alto valor — sin respaldo ni alternativa.

*Qué significa para esta área:* Revela los sistemas cuya caída no tiene redundancia operativa. Riesgo de concentración tecnológica que merece inversión en respaldo.

> **💬 Mensaje al ejecutivo**
> *Qué descubrimos:* Encontramos qué sistemas tecnológicos son un punto único de falla: actividades críticas para sus clientes que dependen exclusivamente de esa herramienta y quedarían completamente paralizadas si el sistema falla, sin ninguna alternativa disponible.
> *Por qué funciona:* Verificamos, para cada actividad importante, si existe más de un sistema que pueda soportarla. Cuando hay una sola herramienta disponible y la actividad es crítica, cualquier interrupción tecnológica se convierte directamente en un problema para el cliente.

**Subáreas beneficiadas:** Arquitectura de sistemas · Ciberseguridad · Soporte técnico · Gestión de datos

- **Setup:** Grafo bipartito Activity–System. Buscar Systems que son el único nodo System conectado a Activities con V(A) por encima de umbral.
- **Función:** Filtro sobre `G.neighbors(system_node)` — actividades sin Sistema alternativo conectado
- **Librería:** `networkx`

> **🎨 Visualización en interfaz — ✅ Resaltado genérico**
> Resalta en rojo los nodos System sin alternativa conectada a actividades de alto V. Las aristas USES_SYSTEM hacia esas actividades se muestran como línea punteada roja para indicar dependencia única.
> *Elementos resaltados: Nodos System críticos + aristas USES_SYSTEM únicas*

---

**T-03 — Mapa de oportunidades de automatización**

Combina frecuencia alta + sistema existente + baja complejidad de inputs para producir un ranking de ROI potencial de automatización por actividad.

*Qué significa para esta área:* Produce una lista priorizada de actividades donde la automatización tiene mayor retorno, respaldada por estructura del grafo.

> **💬 Mensaje al ejecutivo**
> *Qué descubrimos:* Identificamos qué actividades de su operación tienen el mayor potencial de ser automatizadas con el menor riesgo y el mayor retorno: las que se repiten mucho, ya están soportadas por algún sistema digital y no requieren decisiones complejas para ejecutarse.
> *Por qué funciona:* Combinamos tres señales del mapa de operaciones: qué tan frecuente es la actividad, si ya tiene soporte tecnológico, y qué tan simple es su estructura de inputs. Las actividades que puntúan alto en los tres criterios son las más directamente automatizables.

**Subáreas beneficiadas:** Software · IA y analytics · Arquitectura de sistemas · Gestión de datos

- **Setup:** Nodos Activity con atributos F, presencia de arista USES_SYSTEM, conteo de tipos de aristas entrantes. Normalizar y combinar en score.
- **Función:** Cálculo sobre atributos + `G.in_degree(node)` por tipo de arista
- **Librería:** `networkx` + `pandas`

> **🎨 Visualización en interfaz — ✅ Resaltado con gradiente**
> Nodos Activity coloreados por puntaje de automatización (gris bajo → azul eléctrico alto). Filtrables por umbral con un slider. Los que ya tienen arista USES_SYSTEM aparecen con icono de sistema.
> *Elementos resaltados: Nodos Activity (gradiente de automatización)*

---

**T-04 — Factores latentes tecnología–valor (SVD)**

Descomposición de la matriz Sistema×Métrica para revelar qué clusters de sistemas co-impulsan qué grupos de métricas.

*Qué significa para esta área:* Identifica pilas tecnológicas de valor — grupos de sistemas que trabajan juntos para sostener grupos de métricas de cliente.

> **💬 Mensaje al ejecutivo**
> *Qué descubrimos:* Descubrimos agrupaciones naturales entre sus sistemas tecnológicos y los resultados que más importan a sus clientes — qué conjunto de herramientas trabaja unido para sostener cada tipo de valor que entrega su organización.
> *Por qué funciona:* Construimos una tabla que relaciona cada sistema con cada indicador de cliente y buscamos los patrones ocultos de co-ocurrencia. Es similar a cómo un análisis de datos de ventas puede revelar qué productos se compran juntos — aquí aplicamos la misma lógica a tecnología y valor.

**Subáreas beneficiadas:** Arquitectura de sistemas · I+D · IA y analytics · Gestión de datos

- **Setup:** Construir matriz System×Metric con valores = suma de Relevance(A,M) para actividades con USES_SYSTEM→S y AFFECTS→M. Aplicar SVD truncada con k=3.
- **Función:** `scipy.sparse.linalg.svds(matrix, k=3)`
- **Librería:** `scipy`

> **🎨 Visualización en interfaz — 📊 Representación especial**
> No apto para resaltado de grafo. Representación como heatmap Sistema×Métrica con clusters coloreados por factor latente. Opción secundaria: resaltar en el grafo el cluster de mayor factor con un color por grupo.
> *Elementos resaltados: Heatmap lateral + resaltado opcional de clusters en grafo*

---

### Abastecimiento

---

**A-01 — Índice de concentración de suministro**

Mide cuántas actividades críticas dependen de un solo proveedor sin alternativa estructural.

*Qué significa para esta área:* Cuantifica el riesgo de concentración desde la perspectiva del grafo: no cuántos proveedores hay en el contrato, sino cuántas actividades de alto valor dependen de uno solo.

> **💬 Mensaje al ejecutivo**
> *Qué descubrimos:* Calculamos qué proveedores concentran la mayor dependencia operativa — no por el volumen de compra que representan, sino por cuántas de sus actividades críticas quedarían sin suministro si ese proveedor fallara y no hubiera ninguno que lo reemplazara.
> *Por qué funciona:* Contamos cuántas actividades importantes del proceso dependen de cada proveedor y si existen alternativas conectadas. Un proveedor con muchas actividades críticas a su cargo y sin sustituto en el mapa es un riesgo de concentración que el contrato solo no resuelve.

**Subáreas beneficiadas:** Riesgo de suministro · Sourcing estratégico · Gestión de proveedores · Compras operativas

- **Setup:** Añadir nodos Proveedor al grafo con aristas SUPPLIES→Activity. Calcular in-degree de actividades desde nodos proveedor. Cruzar con V(A).
- **Función:** `nx.in_degree_centrality(G)` filtrado a actividades de abastecimiento
- **Librería:** `networkx`

> **🎨 Visualización en interfaz — ✅ Resaltado con gradiente**
> Nodos Proveedor coloreados por índice de concentración. Al seleccionar uno, se resaltan las actividades que dependen exclusivamente de él, con su V(A) visible en cada nodo.
> *Elementos resaltados: Nodos Proveedor + nodos Activity dependientes*

---

**A-02 — Throughput máximo de la cadena de suministro**

Dado F(A) como capacidad de cada actividad de abastecimiento, calcula el flujo máximo desde proveedores hasta operaciones.

*Qué significa para esta área:* Identifica el cuello de botella de capacidad: qué actividad de abastecimiento limita el flujo total hacia operaciones.

> **💬 Mensaje al ejecutivo**
> *Qué descubrimos:* Calculamos el volumen máximo que puede mover su cadena de suministro antes de saturarse — y el punto exacto donde está la restricción que frena todo lo demás.
> *Por qué funciona:* Modelamos cada actividad de abastecimiento como una tubería con cierta capacidad máxima. Luego calculamos cuánto puede fluir a través de toda la red. La tubería más estrecha determina el límite del sistema completo, igual que en una cadena física.

**Subáreas beneficiadas:** Compras operativas · Riesgo de suministro · Sourcing estratégico · Negociación y contratos

- **Setup:** Subgrafo Proveedor→Activity(abastecimiento)→Activity(operaciones) con capacidad = F(A). Super-source conectado a todos los proveedores.
- **Función:** `nx.maximum_flow(G, super_source, operations_sink, capacity='F')`
- **Librería:** `networkx`

> **🎨 Visualización en interfaz — 🌊 Flujo en aristas**
> Resalta aristas del flujo con grosor proporcional a la capacidad F(A). La arista del corte mínimo aparece en rojo grueso con etiqueta de capacidad. Requiere representación especial de aristas con valor numérico.
> *Elementos resaltados: Aristas de flujo (grosor = capacidad) + arista de corte mínimo*

---

**A-03 — Simulación de falla de proveedor**

Eliminar un nodo proveedor y recalcular qué actividades quedan sin input y qué métricas pierden cobertura.

*Qué significa para esta área:* Traduce el riesgo de suministro a impacto en métricas de valor cliente de forma cuantitativa.

> **💬 Mensaje al ejecutivo**
> *Qué descubrimos:* Simulamos qué pasaría si un proveedor específico dejara de operar de un día para otro y medimos exactamente qué indicadores de valor para sus clientes se verían afectados y en qué magnitud.
> *Por qué funciona:* Retiramos al proveedor del mapa operativo y observamos qué actividades quedan sin insumo y, como consecuencia, qué métricas de cliente pierden el proceso que las sostenía. Es un ejercicio de "¿y si?" ejecutado sobre el modelo real de la operación.

**Subáreas beneficiadas:** Riesgo de suministro · Sourcing estratégico · Gestión de proveedores · Negociación y contratos

- **Setup:** Grafo completo con nodos proveedor. Remover nodo proveedor y sus aristas. Recalcular reachability de Metrics.
- **Función:** `G.remove_node(proveedor)` + `nx.ancestors(G, metric_node)`
- **Librería:** `networkx`

> **🎨 Visualización en interfaz — 🔀 Resaltado en cascada**
> Igual que G-03 pero con nodo Proveedor como origen. Muestra nodo removido en gris tachado, actividades huérfanas en naranja y métricas desconectadas en rojo.
> *Elementos resaltados: Nodo Proveedor removido + actividades huérfanas + métricas expuestas*

---

**A-04 — Clusters de abastecimiento estratégico vs. operativo**

Detecta agrupaciones naturales de proveedores según su posición en el grafo: estratégicos (alto V, múltiples procesos) vs. operativos (bajo V, un proceso).

*Qué significa para esta área:* Distingue empíricamente qué proveedores merecen gestión estratégica vs. compras transaccionales, basado en su posición en el grafo y no en el volumen de compra.

> **💬 Mensaje al ejecutivo**
> *Qué descubrimos:* Clasificamos automáticamente a sus proveedores en grupos naturales según el rol real que juegan en su operación — cuáles son verdaderamente estratégicos porque sostienen actividades críticas en múltiples procesos, y cuáles son simplemente operativos porque cubren necesidades puntuales de bajo impacto.
> *Por qué funciona:* El mapa operativo revela patrones de agrupación entre proveedores y las actividades que soportan. Los proveedores que aparecen conectados a las mismas actividades críticas forman clusters naturales que indican afinidad estratégica — independientemente de la categoría de compra en el ERP.

**Subáreas beneficiadas:** Sourcing estratégico · Gestión de proveedores · Negociación y contratos · ESG

- **Setup:** Subgrafo bipartito Proveedor–Activity con peso = V(A). Proyectar sobre proveedores y aplicar detección de comunidades.
- **Función:** `community.best_partition(G)` sobre la proyección Proveedor
- **Librería:** `python-louvain`

> **🎨 Visualización en interfaz — ✅ Resaltado por cluster**
> Nodos Proveedor y Activity coloreados por membresía de cluster (un color por comunidad). Permite al ejecutivo ver visualmente qué proveedores trabajan juntos en el mismo ámbito operativo.
> *Elementos resaltados: Nodos Proveedor + Activity coloreados por cluster*

---

## Actividades primarias

---

### Logística interna

---

**LI-01 — Ruta crítica interna**

La secuencia más larga de actividades dependientes desde recepción de insumos hasta disponibilidad para producción.

*Qué significa para esta área:* Identifica el piso estructural del tiempo de preparación interna — la duración mínima irreducible independientemente de la eficiencia del equipo.

> **💬 Mensaje al ejecutivo**
> *Qué descubrimos:* Identificamos la cadena de pasos internos que determina cuánto tiempo mínimo tarda un insumo en estar disponible para producción — el límite que ninguna mejora de eficiencia puede superar sin rediseñar la secuencia completa.
> *Por qué funciona:* Calculamos el camino más largo de actividades encadenadas donde cada una debe esperar a que termine la anterior. Esa cadena es el cuello de botella temporal del proceso: optimizar cualquier actividad fuera de ella no reduce el tiempo total.

**Subáreas beneficiadas:** Recepción de materiales · Almacenamiento · Control de inventarios · Manejo de materiales

- **Setup:** Subgrafo Activity/PRECEDES de logística interna con duración como atributo de arista. Source = recepción. Sink = primera actividad de operaciones.
- **Función:** `nx.dag_longest_path(G, weight='duracion')`
- **Librería:** `networkx`

> **🎨 Visualización en interfaz — 🔀 Camino ordenado**
> Resalta la secuencia ordenada de nodos Activity de la ruta crítica con flechas gruesas y numeración de pasos. Las aristas de la ruta se colorean en gradiente tiempo (claro al inicio, oscuro al final).
> *Elementos resaltados: Camino ordenado Activity → Activity con numeración*

---

**LI-02 — Cuellos de botella en flujo de materiales**

Betweenness centrality en logística interna — qué actividades intermedias concentran más el flujo de materiales.

*Qué significa para esta área:* Revela dónde el inventario se acumula estructuralmente — no por falta de espacio físico, sino porque esa actividad es el paso por el que todo debe pasar.

> **💬 Mensaje al ejecutivo**
> *Qué descubrimos:* Encontramos exactamente en qué punto del proceso interno de materiales se produce el mayor atasco estructural: la actividad por la que todo pasa y que, si se satura, detiene todo lo que viene después.
> *Por qué funciona:* Contamos cuántas rutas posibles de flujo de materiales pasan por cada actividad. La que acumula más rutas es el cuello de botella real — no porque sea lenta, sino porque todo depende de que funcione sin interrupción.

**Subáreas beneficiadas:** Almacenamiento · Control de inventarios · Manejo de materiales · Recepción de materiales

- **Setup:** Subgrafo Activity/PRECEDES filtrado a actividades de logística interna.
- **Función:** `nx.betweenness_centrality(G, normalized=True)`
- **Librería:** `networkx`

> **🎨 Visualización en interfaz — ✅ Resaltado con gradiente**
> Nodos Activity de logística interna coloreados en gradiente por betweenness. El nodo de mayor betweenness aparece con halo de alerta. Opción de filtrar el resto del grafo para ver solo esta área.
> *Elementos resaltados: Nodos Activity (gradiente betweenness)*

---

**LI-03 — Puntos únicos de falla en recepción**

Actividades o handoffs cuya eliminación desconecta el flujo de materiales de las actividades de producción.

*Qué significa para esta área:* Identifica qué pasos de recepción o almacenamiento, si fallan, detienen toda la operación downstream sin alternativa.

> **💬 Mensaje al ejecutivo**
> *Qué descubrimos:* Encontramos qué pasos del proceso de recepción y manejo interno de materiales, si fallan una sola vez, interrumpen completamente el flujo hacia producción sin que haya ningún camino alternativo disponible.
> *Por qué funciona:* Buscamos los pasos que funcionan como "llaves": si se bloquean, cortan el flujo completo. Son los candidatos más urgentes a tener un procedimiento de respaldo o redundancia, porque su falla no puede absorberse de ninguna otra forma.

**Subáreas beneficiadas:** Recepción de materiales · Almacenamiento · Devoluciones a proveedor · Control de inventarios

- **Setup:** Subgrafo no dirigido de logística interna. Calcular puntos de articulación y bridge edges.
- **Función:** `nx.articulation_points(G.to_undirected())` + `nx.bridges(G.to_undirected())`
- **Librería:** `networkx`

> **🎨 Visualización en interfaz — ✅ Resaltado genérico**
> Puntos de articulación resaltados con ícono de advertencia. Bridge edges mostradas como línea roja discontinua. Al hacer clic, muestra qué parte del grafo quedaría desconectada si ese punto falla.
> *Elementos resaltados: Nodos articulación + aristas bridge en rojo*

---

### Operaciones

---

**O-01 — Ruta crítica de producción**

La secuencia de actividades de operaciones que determina el tiempo mínimo de ciclo productivo.

*Qué significa para esta área:* Separa las actividades que realmente limitan la velocidad de producción de las que simplemente ocurren en paralelo sin impacto en el tiempo total.

> **💬 Mensaje al ejecutivo**
> *Qué descubrimos:* Encontramos la secuencia exacta de pasos productivos que determina cuánto tiempo mínimo tarda su operación en generar valor — la cadena que ninguna optimización puede acortar sin cambiar el orden o la naturaleza de los pasos.
> *Por qué funciona:* Identificamos todos los pasos que deben ocurrir en serie (uno espera al otro) y calculamos cuál secuencia es la más larga. Esa es la ruta crítica: cualquier mejora fuera de ella no reduce el tiempo total de producción.

**Subáreas beneficiadas:** Producción / servicio · Planeación de producción · Mejora continua · Planta y facilidades

- **Setup:** Subgrafo Activity/PRECEDES de operaciones con duración como atributo. Source = primer paso de transformación. Sink = entrega a logística externa.
- **Función:** `nx.dag_longest_path(G, weight='duracion')`
- **Librería:** `networkx`

> **🎨 Visualización en interfaz — 🔀 Camino ordenado**
> Secuencia ordenada de la ruta crítica productiva con flechas y duración acumulada por tramo. Actividades fuera de la ruta aparecen atenuadas para contrastar con la ruta crítica.
> *Elementos resaltados: Camino ordenado con duraciones acumuladas*

---

**O-02 — Centralidad de controles de calidad**

Betweenness centrality en operaciones para actividades de control de calidad — cuáles son estructuralmente centrales para el flujo productivo.

*Qué significa para esta área:* Identifica dónde un control de calidad debe mejorarse en velocidad para no convertirse en restricción de throughput, sin reducir su rigor.

> **💬 Mensaje al ejecutivo**
> *Qué descubrimos:* Detectamos qué controles de calidad están funcionando también como cuellos de botella del proceso productivo: son rigurosos en lo que verifican, pero su posición en el flujo hace que todo deba esperar por ellos.
> *Por qué funciona:* Medimos cuántas rutas del proceso productivo pasan por cada control de calidad. Los que concentran más rutas son los que mayor impacto tienen en la velocidad — no solo en la calidad. Ahí la inversión es en agilidad del control, no en rigor.

**Subáreas beneficiadas:** Control de calidad · Producción / servicio · Mejora continua · Planeación de producción

- **Setup:** Subgrafo Activity/PRECEDES de operaciones. Etiquetar actividades de calidad. Calcular betweenness y filtrar.
- **Función:** `nx.betweenness_centrality(G)` → filtrar por etiqueta `tipo='control_calidad'`
- **Librería:** `networkx`

> **🎨 Visualización en interfaz — ✅ Resaltado con gradiente**
> Nodos Activity de control de calidad coloreados por betweenness. Los de mayor centralidad aparecen más grandes. Tooltip con número de rutas productivas que pasan por ese control.
> *Elementos resaltados: Nodos calidad (tamaño + color por centralidad)*

---

**O-03 — Riesgo bayesiano de falla de calidad por degradación de mantenimiento**

Dado que una actividad de mantenimiento se degrada, probabilidad de que la siguiente actividad de control de calidad detecte una no conformidad.

*Qué significa para esta área:* Cuantifica la relación causal entre inversión en mantenimiento y resultados de calidad.

> **💬 Mensaje al ejecutivo**
> *Qué descubrimos:* Calculamos qué tan probable es que un problema de calidad aparezca si se descuida el mantenimiento de un equipo o proceso específico — expresado como una probabilidad concreta, no como una intuición.
> *Por qué funciona:* Construimos un modelo de causa y efecto entre actividades de mantenimiento y controles de calidad, calibrado con la información de impacto que ya tiene el grafo. Luego simulamos el escenario de degradación y calculamos la probabilidad resultante, como un modelo de riesgo actuarial aplicado a la operación.

**Subáreas beneficiadas:** Mantenimiento · Control de calidad · Planeación de producción · Mejora continua

- **Setup:** Red bayesiana con nodos de mantenimiento y calidad. CPTs calibradas con C scores del grafo. Inferencia con eliminación de variables.
- **Función:** `pgmpy.inference.VariableElimination(model).query(['calidad'], evidence={'mantenimiento': 'degradado'})`
- **Librería:** `pgmpy`

> **🎨 Visualización en interfaz — 📊 Representación especial**
> No apto para resaltado puro. Widget de probabilidad: barra de progreso o gauge que muestra P(falla calidad | mantenimiento degradado). Se ancla visualmente sobre el nodo Metric o Activity afectado en el grafo.
> *Elementos resaltados: Gauge de probabilidad sobre nodo afectado en el grafo*

---

**O-04 — Núcleo operativo irreducible**

El conjunto mínimo de actividades de operaciones densamente interconectadas que no puede desmantelarse sin colapsar el proceso productivo.

*Qué significa para esta área:* Define qué actividades de operaciones nunca deben tercerizarse, automatizarse sin respaldo o reducirse por presupuesto.

> **💬 Mensaje al ejecutivo**
> *Qué descubrimos:* Identificamos el corazón operativo de su empresa: el conjunto mínimo de actividades productivas que están tan interconectadas entre sí que eliminar cualquiera de ellas desestabiliza a todas las demás. Todo lo que queda fuera de este núcleo es flexible; lo que está dentro, no.
> *Por qué funciona:* Buscamos el grupo de actividades donde cada una está conectada directamente a al menos otras tres del mismo grupo. Ese nivel de interconexión crea una red tan densa que no puede simplificarse sin que se rompa — es el indicador más confiable del núcleo productivo real.

**Subáreas beneficiadas:** Producción / servicio · Planeación de producción · Mantenimiento · Mejora continua

- **Setup:** Subgrafo no dirigido de actividades de operaciones conectadas por PRECEDES.
- **Función:** `nx.k_core(G, k=3)`
- **Librería:** `networkx`

> **🎨 Visualización en interfaz — ✅ Resaltado genérico**
> El k-core resaltado en color sólido diferenciado. Las actividades fuera del núcleo aparecen en gris muy tenue. Contraste visual claro entre núcleo no negociable y periferia flexible.
> *Elementos resaltados: Nodos k-core (color sólido) vs. periferia (gris tenue)*

---

### Logística externa

---

**LE-01 — Techo de throughput de entrega por segmento**

Flujo máximo desde despacho hasta entrega confirmada, con F(A) como capacidad, separado por segmento de cliente.

*Qué significa para esta área:* Revela cuántas entregas puede manejar el sistema logístico antes de saturarse y en qué punto está la restricción vinculante.

> **💬 Mensaje al ejecutivo**
> *Qué descubrimos:* Calculamos cuántas entregas puede absorber su sistema logístico por segmento de cliente antes de colapsar — y el paso exacto que está limitando esa capacidad máxima.
> *Por qué funciona:* Modelamos cada actividad de distribución como una tubería con capacidad limitada. Al calcular cuánto puede fluir a través de toda la red para cada tipo de cliente, encontramos dónde está el cuello que frena el crecimiento del volumen de entregas.

**Subáreas beneficiadas:** Transporte y distribución · Gestión de entregas · Gestión de pedidos · Socios logísticos

- **Setup:** Subgrafo Activity/PRECEDES de logística externa con capacidad = F(A). Separar por segmento. Super-source = despacho. Sink = EV-04.
- **Función:** `nx.maximum_flow(G, source, sink, capacity='F')`
- **Librería:** `networkx`

> **🎨 Visualización en interfaz — 🌊 Flujo en aristas**
> Igual que A-02: aristas con grosor proporcional a capacidad F(A) por segmento. Selector de segmento (industrial / gasolinera / autoconsumo) para cambiar qué subgrafo se visualiza. Arista de corte en rojo.
> *Elementos resaltados: Aristas de flujo por segmento + arista de corte mínimo*

---

**LE-02 — Ruta de mayor valor por eficiencia de entrega**

El camino desde confirmación de pedido hasta entrega que maximiza V(A) acumulado por salto.

*Qué significa para esta área:* Identifica qué actividades logísticas agregan más valor por unidad de tiempo e indica qué pasos actuales son candidatos a eliminación o paralelización.

> **💬 Mensaje al ejecutivo**
> *Qué descubrimos:* Encontramos la secuencia de actividades logísticas que genera el mayor valor para el cliente por cada paso que se da — la ruta más eficiente en términos de impacto, no solo de velocidad.
> *Por qué funciona:* Asignamos a cada paso logístico su valor de contribución al cliente y calculamos cuál camino acumula más valor por salto. Si la ruta óptima difiere del proceso actual, los pasos que sobran son candidatos concretos a rediseñar.

**Subáreas beneficiadas:** Gestión de entregas · Transporte y distribución · Socios logísticos · Logística inversa

- **Setup:** Subgrafo Activity/PRECEDES de logística externa. Peso de arista = 1 - V(destino).
- **Función:** `nx.dijkstra_path(G, source, target, weight='costo')`
- **Librería:** `networkx`

> **🎨 Visualización en interfaz — 🔀 Camino ordenado**
> Ruta de mayor valor resaltada con flechas y V(A) acumulado visible en cada nodo. Las actividades fuera de la ruta óptima aparecen atenuadas con etiqueta '¿necesario?'.
> *Elementos resaltados: Camino óptimo con V(A) acumulado + actividades fuera de ruta etiquetadas*

---

**LE-03 — Cobertura de momentos del cliente por actividades logísticas**

Para cada CustomerJourneyStep de operación recurrente, qué actividades de logística externa lo cubren y con qué Relevance.

*Qué significa para esta área:* Identifica qué momentos de la experiencia del cliente tienen respaldo operativo logístico y cuáles ocurren sin proceso interno que los sostenga.

> **💬 Mensaje al ejecutivo**
> *Qué descubrimos:* Mapeamos qué momentos clave de la experiencia de sus clientes — cuando reciben su primera entrega, cuando evalúan si el servicio es confiable — tienen actividades logísticas reales que los atienden, y cuáles quedan sin respaldo operativo.
> *Por qué funciona:* Cruzamos el mapa de la experiencia del cliente con el mapa de actividades logísticas y medimos qué tan bien cubierto está cada momento. Un momento del cliente sin actividad interna que lo soporte es un riesgo de experiencia invisible para la organización.

**Subáreas beneficiadas:** Gestión de entregas · Gestión de pedidos · Socios logísticos · Logística inversa

- **Setup:** Subgrafo Activity–CustomerJourneyStep con aristas TOUCHES, filtrado a logística externa. Cruzar con Relevance(A, M-01) y Relevance(A, M-02).
- **Función:** `nx.bipartite.degree_centrality(B, cjs_nodes)` sobre subgrafo filtrado
- **Librería:** `networkx`

> **🎨 Visualización en interfaz — ✅ Resaltado bipartito**
> Resalta aristas TOUCHES entre actividades logísticas y CustomerJourneySteps. Color de arista = Relevance(A,M). Los CJS sin ninguna actividad conectada aparecen con ícono de alerta de cobertura vacía.
> *Elementos resaltados: Aristas TOUCHES coloreadas por Relevance + CJS sin cobertura marcados*

---

**LE-04 — Socios logísticos críticos sin sustituto**

Identifica qué socios logísticos, si fallan, no pueden ser reemplazados por ningún otro socio en la red actual.

*Qué significa para esta área:* Determina qué socios logísticos no tienen sustituto estructural — candidatos urgentes a contratos de respaldo o desarrollo de alternativas.

> **💬 Mensaje al ejecutivo**
> *Qué descubrimos:* Identificamos qué socios de transporte o distribución son un punto único de falla en su red logística: si uno de ellos falla, no hay ningún otro socio disponible en el mapa actual que pueda absorber esa función.
> *Por qué funciona:* Revisamos si cada socio logístico tiene equivalentes en la red que puedan cubrir las mismas rutas o actividades. Cuando no existe ningún sustituto conectado, cualquier interrupción de ese socio se traduce directamente en incumplimiento al cliente.

**Subáreas beneficiadas:** Socios logísticos · Transporte y distribución · Gestión de entregas · Logística inversa

- **Setup:** Añadir nodos SocioLogístico al grafo con aristas EJECUTA→Activity(transporte). Calcular puntos de articulación incluyendo estos nodos.
- **Función:** `nx.articulation_points(G.to_undirected())` → filtrar por tipo SocioLogístico
- **Librería:** `networkx`

> **🎨 Visualización en interfaz — ✅ Resaltado genérico**
> Nodos SocioLogístico sin sustituto resaltados en rojo. Las aristas hacia sus actividades dependientes aparecen en rojo punteado. Nodos con alternativa disponible aparecen en verde para contraste.
> *Elementos resaltados: Nodos socios críticos (rojo) vs. con alternativa (verde)*

---

### Marketing y ventas

---

**MV-01 — Flujo del pipeline comercial**

Todos los caminos desde actividades de prospección hasta la firma de contrato — qué secuencias de actividades comerciales convierten.

*Qué significa para esta área:* Identifica los caminos de conversión reales en el grafo vs. los que el equipo comercial cree que usa.

> **💬 Mensaje al ejecutivo**
> *Qué descubrimos:* Mapeamos todas las rutas posibles que sigue la operación comercial desde que se identifica un prospecto hasta que firma un contrato — incluyendo caminos cortos que podrían acortar el ciclo de ventas y que quizás no están siendo aprovechados.
> *Por qué funciona:* Rastreamos en el mapa operativo todos los caminos que conectan el primer contacto con el cliente con el cierre comercial. Los caminos más cortos que existen estructuralmente pero que no se usan sistemáticamente son oportunidades concretas de acelerar el ciclo de ventas.

**Subáreas beneficiadas:** Fuerza de ventas · KAM – clientes clave · Canales comerciales · Investigación de mercado

- **Setup:** Subgrafo Activity/PRECEDES + TOUCHES→CJS de marketing y ventas. Source = actividades que tocan CJS-01. Sink = actividad que activa EV-01.
- **Función:** `nx.all_simple_paths(G, source, target, cutoff=8)`
- **Librería:** `networkx`

> **🎨 Visualización en interfaz — 🔀 Camino ordenado**
> Muestra todos los caminos de conversión encontrados superpuestos en el grafo, con un selector para filtrar por longitud o por tasa de conversión estimada. El camino más corto aparece resaltado por defecto.
> *Elementos resaltados: Múltiples caminos superpuestos con selector de ruta*

---

**MV-02 — Actividades comerciales con mayor cobertura de journey**

Qué actividades de ventas tocan el mayor número de CustomerJourneySteps distintos.

*Qué significa para esta área:* Identifica los pasos de ventas con mayor alcance experiencial — los más relevantes para estandarizar o capacitar primero.

> **💬 Mensaje al ejecutivo**
> *Qué descubrimos:* Encontramos qué actividades del proceso comercial tienen el mayor impacto sobre la experiencia total del cliente — los pasos que, bien ejecutados, mejoran simultáneamente múltiples momentos de la relación con el cliente.
> *Por qué funciona:* Contamos cuántos momentos distintos de la experiencia del cliente toca cada actividad comercial. Las que aparecen en más momentos son las de mayor palanca para la satisfacción general — no solo para una etapa del proceso.

**Subáreas beneficiadas:** Fuerza de ventas · KAM – clientes clave · Gestión de producto · Canales comerciales

- **Setup:** Subgrafo Activity–CustomerJourneyStep filtrado a actividades de marketing y ventas. Calcular degree de cada actividad.
- **Función:** `nx.bipartite.degree_centrality(B, activity_nodes)`
- **Librería:** `networkx`

> **🎨 Visualización en interfaz — ✅ Resaltado con gradiente**
> Nodos Activity de ventas coloreados por número de CJS que tocan. Los de mayor cobertura aparecen más grandes. Al seleccionar uno, se resaltan los CJS conectados.
> *Elementos resaltados: Nodos Activity (tamaño + color por cobertura de journey)*

---

**MV-03 — Relevancia de actividades KAM sobre retención**

Relevance(A, M-06) para todas las actividades etiquetadas como KAM — cuáles tienen mayor impacto en la tasa de retención.

*Qué significa para esta área:* Prioriza qué actividades del equipo de cuentas clave defender, estandarizar o automatizar para proteger la retención.

> **💬 Mensaje al ejecutivo**
> *Qué descubrimos:* Calculamos cuáles actividades específicas del equipo de cuentas clave tienen el mayor impacto real en que sus clientes más importantes decidan renovar — y cuáles, aunque se ejecutan, tienen un impacto mucho menor del que se asume.
> *Por qué funciona:* Cruzamos el mapa de actividades KAM con el modelo de valor del cliente. El resultado muestra cuánto mueve cada actividad el indicador de retención, combinando la evidencia de entrevistas con clientes y la posición de la actividad en el flujo operativo.

**Subáreas beneficiadas:** KAM – clientes clave · Fuerza de ventas · Posicionamiento · Gestión de producto

- **Setup:** Filtrar actividades con etiqueta `area='KAM'`. Recuperar Relevance(A, M-06) calculado previamente.
- **Función:** Lookup directo en matriz de relevance scores
- **Librería:** `pandas`

> **🎨 Visualización en interfaz — ✅ Resaltado con gradiente**
> Nodos Activity de KAM coloreados por Relevance(A, M-06). Gradiente claro-oscuro. Al seleccionar una actividad, muestra desglose de su B(A,M) y V(A) en panel lateral.
> *Elementos resaltados: Nodos KAM (gradiente Relevance sobre M-06)*

---

**MV-04 — Validación de independencia de iniciativas comerciales**

Verifica si dos iniciativas comerciales propuestas atacan rutas causales independientes o redundantes.

*Qué significa para esta área:* Evita invertir en dos iniciativas que comparten la misma causa raíz y tienen retorno decreciente cuando se ejecutan juntas.

> **💬 Mensaje al ejecutivo**
> *Qué descubrimos:* Verificamos si dos iniciativas comerciales que se están considerando simultáneamente realmente atacan problemas distintos, o si en el fondo comparten la misma causa y ejecutarlas juntas produce mucho menos que la suma de sus partes.
> *Por qué funciona:* Trazamos los caminos causales de cada iniciativa en el mapa operativo y verificamos si se superponen. Cuando dos iniciativas comparten una causa raíz común, resolver esa causa primero es más eficiente que ejecutar ambas en paralelo.

**Subáreas beneficiadas:** Fuerza de ventas · KAM – clientes clave · Gestión de producto · Canales comerciales

- **Setup:** Red bayesiana con actividades de marketing y ventas. Consultar trails activos entre pares de actividades objetivo.
- **Función:** `model.active_trail_nodes({'A28'}, observed=['A30'])`
- **Librería:** `pgmpy`

> **🎨 Visualización en interfaz — 📊 Representación especial**
> Parcialmente apto. Resalta en el grafo las dos actividades bajo análisis y colorea en amarillo los nodos intermedios compartidos (causa común). Panel lateral explica si son dependientes o independientes.
> *Elementos resaltados: Nodos objetivo + causa común resaltada + panel de veredicto*

---

### Servicio postventa

---

**PV-01 — Ruta crítica de resolución de incidentes**

El camino más largo desde el reporte de un incidente hasta su resolución — el tiempo mínimo estructural de resolución.

*Qué significa para esta área:* Separa el tiempo de resolución mejorable con capacitación del tiempo que no puede reducirse sin rediseñar el proceso.

> **💬 Mensaje al ejecutivo**
> *Qué descubrimos:* Encontramos el tiempo mínimo que structuralmente tarda su organización en resolver un incidente de servicio — el límite por debajo del cual ninguna cantidad de entrenamiento o personal adicional puede bajar sin cambiar la secuencia del proceso.
> *Por qué funciona:* Calculamos la cadena más larga de pasos de atención que deben ocurrir en serie para resolver un problema. Esa cadena define el piso de tiempo de resolución. Si el SLA prometido al cliente está por debajo de ese piso, el proceso necesita rediseñarse, no solo ejecutarse más rápido.

**Subáreas beneficiadas:** Atención al cliente · Soporte técnico · Garantías y reparaciones · Contratos de mantenimiento

- **Setup:** Subgrafo Activity/PRECEDES de postventa. Source = actividad que activa EV-08. Sink = actividad de cierre. Duración como atributo de arista.
- **Función:** `nx.dag_longest_path(G, weight='duracion')`
- **Librería:** `networkx`

> **🎨 Visualización en interfaz — 🔀 Camino ordenado**
> Ruta crítica de resolución resaltada con numeración de pasos y duración acumulada. SLA del cliente mostrado como línea de referencia sobre el tiempo total. Si la ruta supera el SLA, la última arista aparece en rojo.
> *Elementos resaltados: Camino ordenado con duración vs. SLA del cliente*

---

**PV-02 — Cuellos de botella en escalación**

Betweenness centrality en el subgrafo de postventa — qué actividades concentran todas las escalaciones.

*Qué significa para esta área:* Identifica dónde se acumulan los tickets no por volumen sino por estructura del proceso — el candidato número uno a rediseño para reducir tiempo de respuesta.

> **💬 Mensaje al ejecutivo**
> *Qué descubrimos:* Identificamos en qué punto del proceso de atención y escalación se concentra la mayor congestión — el paso por el que deben pasar prácticamente todos los casos que se complican, creando el mayor retraso en la resolución.
> *Por qué funciona:* Medimos cuántos caminos distintos de escalación convergen en cada actividad de atención. La que acumula más convergencias es el cuello de botella estructural del servicio — no porque sea ineficiente, sino porque todo lo redirigen hacia ella.

**Subáreas beneficiadas:** Atención al cliente · Soporte técnico · Satisfacción y NPS · Contratos de mantenimiento

- **Setup:** Subgrafo Activity/PRECEDES de postventa incluyendo aristas de escalación entre atención y soporte técnico.
- **Función:** `nx.betweenness_centrality(G, normalized=True)`
- **Librería:** `networkx`

> **🎨 Visualización en interfaz — ✅ Resaltado con gradiente**
> Nodos Activity de postventa coloreados por betweenness. El nodo de mayor betweenness — el cuello de escalación — aparece con halo pulsante de alerta.
> *Elementos resaltados: Nodos Activity postventa (gradiente + halo en máximo betweenness)*

---

**PV-03 — Riesgo bayesiano de churn por degradación del servicio**

Dado que el tiempo de respuesta a incidentes se degrada, probabilidad de impacto sobre la tasa de retención.

*Qué significa para esta área:* Cuantifica la relación causal entre calidad del servicio postventa y retención — convierte el argumento cualitativo en una probabilidad accionable.

> **💬 Mensaje al ejecutivo**
> *Qué descubrimos:* Calculamos con qué probabilidad una degradación en la calidad de respuesta a incidentes se traduce en pérdida de clientes — no como suposición, sino como resultado de modelar la relación causal real entre servicio y retención en su operación.
> *Por qué funciona:* Construimos un modelo probabilístico basado en las relaciones causales del mapa operativo y lo calibramos con los datos de impacto que ya tiene el grafo. El resultado es una probabilidad concreta que conecta la inversión en servicio postventa con su efecto directo en retención.

**Subáreas beneficiadas:** Atención al cliente · Satisfacción y NPS · Éxito del cliente · Contratos de mantenimiento

- **Setup:** Red bayesiana con actividades de postventa y nodo Metric M-06. CPTs calibradas con C scores y Relevance(A, M-06).
- **Función:** `pgmpy.inference.VariableElimination(model).query(['M06'], evidence={'A33': 'degradada'})`
- **Librería:** `pgmpy`

> **🎨 Visualización en interfaz — 📊 Representación especial**
> No apto para resaltado puro. Gauge de probabilidad sobre el nodo M-06 en el grafo, con flecha indicando dirección del cambio (degradación → aumento de riesgo). Se puede mostrar inline sobre el nodo.
> *Elementos resaltados: Gauge de probabilidad de churn anclado al nodo M-06*

---

**PV-04 — Cobertura de momentos críticos del journey por postventa**

Para los CustomerJourneySteps de incidencia, revisión y renovación, qué actividades de postventa los cubren y con qué Relevance sobre retención.

*Qué significa para esta área:* Revela si los momentos más críticos del journey tienen actividades internas bien definidas que los atienden, o si ocurren sin proceso que los soporte.

> **💬 Mensaje al ejecutivo**
> *Qué descubrimos:* Verificamos si los momentos más sensibles de la relación con su cliente — cuando reportan un problema, cuando se hace la revisión periódica y cuando deciden si renovar — tienen actividades internas concretas que los atienden, o si suceden sin que la organización haga algo específico para gestionarlos.
> *Por qué funciona:* Cruzamos los momentos del journey del cliente con el mapa de actividades de postventa y medimos qué tan bien cubierto está cada uno. Un momento crítico del cliente sin actividad interna asignada es una brecha de servicio que probablemente nadie ha documentado como tal.

**Subáreas beneficiadas:** Satisfacción y NPS · Éxito del cliente · Atención al cliente · Contratos de mantenimiento

- **Setup:** Subgrafo Activity–CustomerJourneyStep filtrado a CJS-06, CJS-07, CJS-08 y actividades de postventa. Cruzar con Relevance(A, M-06).
- **Función:** `nx.bipartite.degree_centrality(B, cjs_nodes)` + lookup de relevance
- **Librería:** `networkx` + `pandas`

> **🎨 Visualización en interfaz — ✅ Resaltado bipartito**
> Igual que LE-03: aristas TOUCHES hacia CJS-06, CJS-07, CJS-08 coloreadas por Relevance. CJS sin cobertura de postventa marcados con ícono de brecha. Panel lateral con tabla de cobertura por momento.
> *Elementos resaltados: Aristas TOUCHES coloreadas + CJS críticos sin cobertura marcados*

---

**PV-05 — Propagación de valor upstream desde éxito del cliente**

Las actividades de customer success heredan relevancia propagada desde los CustomerJourneySteps de renovación hacia atrás por la cadena de PRECEDES.

*Qué significa para esta área:* Evita que las actividades de customer success sean invisibles en el análisis de valor por no aparecer explícitamente en entrevistas — su contribución a retención se vuelve medible.

> **💬 Mensaje al ejecutivo**
> *Qué descubrimos:* Calculamos el valor que generan actividades de adopción y acompañamiento al cliente que normalmente son invisibles en los análisis convencionales — porque los clientes no las mencionan directamente pero son las que preparan el terreno para que el cliente renueve.
> *Por qué funciona:* Partimos del resultado que más importa — la renovación del cliente — y seguimos hacia atrás en el mapa operativo asignando una fracción del valor a cada actividad que contribuyó a llegar ahí. Las actividades de éxito del cliente aparecen así con un valor derivado que refleja su contribución real aunque sea indirecta.

**Subáreas beneficiadas:** Éxito del cliente · Satisfacción y NPS · Puesta en marcha · Atención al cliente

- **Setup:** Grafo completo con aristas TOUCHES→CJS-08 y Relevance(A, M-06) en actividades de renovación. Propagar hacia atrás por PRECEDES con factor de decaimiento por salto (ej. 0.7).
- **Función:** Iteración sobre `nx.predecessors(G, node)` con decaimiento acumulado
- **Librería:** `networkx` + implementación propia del walk

> **🎨 Visualización en interfaz — ✅ Resaltado con gradiente**
> Nodos Activity de customer success coloreados por relevancia propagada (de transparente a sólido según score heredado). Permite ver visualmente cuánto 'valor invisible' lleva cada actividad de acompañamiento.
> *Elementos resaltados: Nodos Activity (gradiente de relevancia propagada, de invisible a sólido)*

