# Ontología del grafo de conocimiento — Optimizer

*Versión 2.2 — Septiembre 2026*

---

## Por qué el grafo está diseñado así

Optimizer parte de una premisa que lo distingue de los sistemas de análisis operativo convencionales: **los KPIs internos de una empresa rara vez miden lo que sus clientes realmente valoran.**

Las métricas tradicionales (ARR, NRR, churn, tiempo de ciclo) son útiles, pero fueron diseñadas para medir el desempeño interno del negocio, no para capturar el valor percibido por el cliente. Una empresa puede tener NRR alto mientras sus clientes sienten que el producto apenas cumple con lo necesario — o viceversa.

Por eso, el punto de partida de Optimizer no son los KPIs existentes. El punto de partida es **la investigación de lo que los clientes realmente necesitan** — sus trabajos por hacer (jobs to be done), las necesidades de sus propios clientes, las restricciones regulatorias o sociales que enfrentan, y los momentos en que sienten que reciben valor real del producto o servicio.

A partir de esa investigación se construyen las **métricas de valor del cliente**: indicadores diseñados específicamente para rastrear si la empresa está entregando lo que sus clientes realmente valoran, no solo lo que la empresa decide medir de sí misma.

Estas métricas son **hipótesis de trabajo**, no verdades establecidas. Son la mejor aproximación posible dado el conocimiento disponible. Su valor está en que:

1. Están ancladas en evidencia real sobre necesidades del cliente, no en convención interna.
2. Son explícitas y auditables — pueden refinarse o refutarse con datos.
3. Crean un puente entre la operación interna y el entorno real donde el cliente vive.

Sin ese puente, el grafo sería solo un mapa de actividades internas sin conexión con el mundo exterior. **El grafo existe para hacer visible esa conexión y cuantificarla.**

---

## Nodos — qué pieza del rompecabezas son

### Activity

La unidad mínima de trabajo ejecutable. Es donde medimos P, C, F y R, y donde conectamos acciones concretas con el valor del negocio. Todo el análisis de Optimizer converge aquí: las actividades son los objetos sobre los que se toman decisiones de inversión, automatización y mejora.

### Process

Agrupa actividades relacionadas bajo una lógica operativa común. Permite analizar valor y cuellos de botella a nivel de proceso — no solo paso a paso — y atribuir contribución a métricas a unidades operativas completas.

### ValueStream

Un subgrafo dirigido y acíclico de nodos `Activity` conectados por relaciones `PRECEDES`, acotado por un `Event` de demanda y un `Event` de realización de valor, con una relación `DRIVES` hacia una `Metric`. No es un nodo — es una estructura que se descubre algorítmicamente sobre el grafo. Representa el camino operativo más relevante entre una demanda del cliente y la entrega de valor.

### Team

Agrupa a quienes ejecutan actividades. Permite atribuir valor (y responsabilidad de mejora) a unidades organizativas reales, y calcular qué proporción de la palanca operativa sobre cada métrica descansa en cada equipo.

### Capability

Expresa "lo que la empresa sabe hacer" (Onboarding, Facturación, Gestión de riesgos, etc.). Sirve para ver qué capacidades sostienen el valor percibido por el cliente y dónde existe déficit de músculo organizacional.

### System

Herramientas y plataformas usadas en las actividades. Indica dónde hay potencial de automatización, dependencias tecnológicas críticas, y oportunidades de integración que impactan directamente el flujo de valor.

### Metric

**Indicador de valor del cliente** — no un KPI interno convencional.

Cada `Metric` en el grafo representa una variable diseñada para medir si la empresa está entregando lo que sus clientes realmente valoran, derivada de investigación sobre sus necesidades reales (jobs to be done, contexto externo, restricciones regulatorias, necesidades de sus propios clientes).

Son el ancla de valor de todo el análisis. Una actividad importa en la medida en que contribuye — directa o indirectamente — a mover estas métricas.

> **Nota epistemológica:** Las métricas son hipótesis de trabajo fundamentadas, no verdades absolutas. Se tratan como establecidas para poder construir el grafo y cuantificar contribuciones — pero están diseñadas para ser revisadas y refinadas conforme se acumula evidencia operativa.

> **v2.2:** además de abducirse desde drivers y lógica de negocio, una `Metric` puede originarse por **promoción de un** `Intent` (ver `Intent —[PROMOTED_TO]→ Metric`).

### Event

Hitos del dominio que marcan momentos discretos en el flujo operativo: inicio de una demanda (ej. *Solicitud de carga recibida*) o realización de valor (ej. *Factura emitida*, *Entrega confirmada por cliente*). Delimitan los Value Streams y anclan el análisis temporal del flujo.

> **v2.1 — Nov 2026:** un `Event` puede declarar explícitamente qué `Metric` realiza, vía la relación `REALIZES` (ver abajo). Antes esto era solo prosa descriptiva ("realización de valor" en el campo de notas del Event); ahora es una arista consultable. Esto cierra el hueco que hacía que las auditorías de coherencia estructural no pudieran derivar, de forma determinista, el evento-terminal de un Process que contribuye a una Metric — tenían que adivinarlo o dejarlo sin resolver.

### CustomerJourneyStep

Momentos de la experiencia del cliente desde su perspectiva: descubre, evalúa, contrata, recibe, usa, pide ayuda, renueva. Son el puente entre los procesos internos y el impacto percibido externamente.

No son opcionales en sentido conceptual — son la capa que conecta la operación interna con la realidad del cliente. Su presencia en el grafo permite detectar qué actividades internas son invisibles al cliente (alto valor estructural, cero contacto con el journey) y cuáles son los momentos críticos de percepción de valor.

### MetricDriver

**Palanca operacional de una métrica de valor** — no una descomposición matemática.

Un `MetricDriver` es una variable que la empresa puede influenciar directamente y que se cree que correlaciona con o causa movimiento en una `Metric`. Es la traducción de la métrica de valor al lenguaje operativo del negocio.

Ejemplo: si la métrica es "densidad de red alcanzada por el cliente", un driver podría ser "contactos importados en el primer día de uso" — algo que el equipo de producto puede medir y sobre lo que puede actuar.

La relación entre un driver y su métrica es una **hipótesis causal o de correlación**, establecida en la fase de alineación estratégica (Capa 0) a partir de investigación y criterio experto. No es una identidad matemática. Diferentes drivers pueden tener diferente nivel de evidencia que los soporte.

> **Para la generación de demos:** Al simular datos del grafo, los MetricDrivers deben reflejar variables que el equipo del cliente realmente puede mover — no descomposiciones contables abstractas. Deben sonar a "esto es lo que hacemos" más que a "así se calcula la métrica".

### Document / Source

Origen de la información que pobló el grafo (entrevista, SOP, informe, taller). Da trazabilidad al modelo y permite volver a la evidencia original al validar o refutar relaciones con el cliente.

### Intent *(v2.2)*

**Propósito de un esfuerzo organizacional** — el *para qué* y *para quién* de una actividad o proceso, independientemente de *cómo* se ejecute y de si efectivamente lo logra.

El grafo ya codificaba el **efecto** de las actividades (`AFFECTS`, `CONTRIBUTES_TO`), pero no su **intención**. Son afirmaciones distintas:

- una actividad puede **perseguir X sin mover X** (esfuerzo real que no entrega — objetivo de mejora o estandarización);
- puede **mover X sin perseguirlo** (efecto colateral);
- puede **servir a un propósito interno** sin ninguna `Metric` de cliente (cumplimiento, cobro, reporte) — hoy eso se ve como "sin ruta a valor" y produce un falso cero.

`Intent` le da a la intención un lugar propio. Su uso principal es **agrupar** actividades por propósito compartido y **detectar esfuerzos contradictorios** en la organización; también sirve para definir la función de cada parte de la organización y como insumo para estandarizar.

Propiedades mínimas:


| Propiedad       | Contenido                                                                                                                            |
| --------------- | ------------------------------------------------------------------------------------------------------------------------------------ |
| `name`          | Formulación normalizada del propósito ("Asegurar entrega en fecha comprometida").                                                    |
| `description`   | Una línea: qué busca lograr y por qué.                                                                                               |
| + esquema común | `generated`, `generation_basis`, `confidence`, `corroboration`, `informant_distance`, `evidence_pointer` (ver Protocolo de llenado). |


El *para quién* se expresa con la arista `SERVES` (cliente vía `Metric`/`CustomerJourneyStep`, organización vía `Event` interno), no como propiedad.

> **No es una** `Metric`**.** Una `Metric` es algo que el cliente experimenta y se cuantifica; un `Intent` es un propósito declarado o inferido de la organización y no lleva puntaje. Solo se convierte en `Metric` mediante promoción explícita.

> **Captura:** la extracción emite una intención en texto libre por actividad; un paso de normalización fusiona sinónimos en nodos `Intent` únicos. Dos actividades con la misma intención apuntan al **mismo** nodo — eso es lo que hace posible el agrupamiento.

---

## Relaciones — para qué usamos cada una

### Team —[PERFORMS]→ Activity

Conecta equipos con las actividades que realmente ejecutan. Base para calcular `s(A,T)` (share de responsabilidad) y para saber qué equipo tiene la palanca operativa en cada tramo del flujo de valor.

### Team —[OWNS]→ Process / Capability

Indica quién es responsable de un proceso o capacidad. Define quién debe liderar las mejoras y quién responde por ese segmento del valor ante la dirección.

### Activity —[PART_OF]→ Process

Sitúa cada actividad dentro de un proceso. Permite agrupar análisis y ver dónde se concentran valor y problemas dentro de cada proceso.

### Activity —[SUPPORTS]→ Capability

Relaciona el trabajo diario con capacidades abstractas. Permite construir mapas de capacidades con su contribución a valor y detectar dónde hay déficit de músculo organizacional.

### Activity —[USES_SYSTEM]→ System

Indica qué sistemas soportan cada actividad. Sirve para localizar oportunidades de automatización, integraciones y cambios de herramienta donde más impactan al valor.

### Activity —[PRECEDES]→ Activity

Marca el orden típico entre actividades. Es la base para reconstruir la secuencia del flujo de valor, calcular P (posición en el flujo) y detectar cuellos de botella estructurales.

### Activity —[AFFECTS]→ Metric

Declara que una actividad influye directamente en una métrica de valor del cliente. Es la relación más directa entre operación y valor — usada para estimar C (fuerza causal) y R (riesgo de impacto).

### Activity —[AFFECTS]→ MetricDriver

Declara que una actividad mueve una palanca operacional. Junto con `MetricDriver —[DRIVES]→ Metric`, construye la ruta indirecta de contribución de valor — fundamental para el signal `DV(A,M)` del bridge score.

### MetricDriver —[DRIVES]→ Metric

Codifica la hipótesis de que mover este driver mueve la métrica de valor del cliente. Es la relación más estratégicamente cargada del grafo: representa el puente entre lo que la empresa puede controlar internamente y lo que el cliente percibe externamente.

> Esta relación debe tratarse como una hipótesis explícita, no como un hecho. En versiones futuras del grafo puede incluir una propiedad de confianza (`confidence`) que refleje la solidez de la evidencia que la soporta.

### Metric —[HAS_DRIVER]→ MetricDriver

Define qué palancas operacionales se asocian a cada métrica de valor. Establece la estructura del driver tree de Capa 0 dentro del grafo.

### Event —[REALIZES]→ Metric *(v2.1 — Nov 2026)*

Declara que este `Event` es el hito que marca la realización (total o parcial) de una `Metric` de valor del cliente. Es la contraparte de `Process —[CONTRIBUTES_TO]→ Metric`: `CONTRIBUTES_TO` dice qué proceso aporta a la métrica; `REALIZES` dice en qué momento discreto del flujo esa entrega efectivamente ocurre.

Se agrega esta relación porque la evidencia de realización ya existía en el grafo — como texto descriptivo en la nota de cada `Event` ("realización de valor", "realización parcial de valor") — pero no como arista consultable. Eso obligaba a cualquier auditoría de coherencia estructural (p. ej. revisar si todas las actividades de un proceso pueden alcanzar el desenlace de valor que ese proceso reclama) a adivinar cuál era el Event-terminal correcto, o dejarlo sin resolver.

Con esta arista, el terminal de un Process se deriva de forma determinista: `Process —[CONTRIBUTES_TO]→ Metric —←[REALIZES]— Event`, y el chequeo de alcanzabilidad usa ese Event como destino en lugar de asumirlo.

> **No usada por Fase 2 (analíticas estructurales).** Ningún subgrafo (`flow`, `bipartite_team`, `bipartite_system`, `causal`, `journey`) ni ninguna de las 28 analíticas del catálogo de `CONTEXTO_ANALITICAS.md` referencian nodos `Event` — hoy `Event` vive fuera de la capa de cómputo estructural. Esta relación es puramente de trazabilidad/coherencia: alimenta auditorías (Check 1 de alcanzabilidad de valor) y consultas humanas, no cambia ningún resultado de las 28 analíticas existentes ni futuras de la "primera ola"/"segunda ola" ya priorizadas.

Puede haber más de un `Event —[REALIZES]→ Metric` cuando la realización es parcial en varios hitos (p. ej. un evento de realización parcial y uno de realización final del mismo flujo de valor).

### Process —[CONTRIBUTES_TO]→ Metric

Resume, a nivel de proceso, su impacto en una métrica de valor. Permite decir "este proceso es crítico para esta métrica" y priorizar procesos completos en la narrativa ejecutiva.

### Activity —[TOUCHES]→ CustomerJourneyStep

Marca qué actividades internas afectan directamente un momento de la experiencia del cliente. Usada para conectar cambios operativos con impacto percibido externamente, y para detectar actividades de alto valor estructural que sin embargo son invisibles al cliente.

### Activity —[INVOLVES_EVENT]→ Event

Relaciona actividades con hitos de negocio. Ayuda a ubicar qué pasos rodean el momento en que se realiza o se inicia el valor (solicitud, entrega, cobro, renovación).

### Activity —[MENTIONED_IN]→ Document / Source

Conecta cada actividad con la fuente donde fue identificada. Da trazabilidad y permite volver a las citas originales al validar el modelo con el cliente.

### Activity / Process —[PURSUES]→ Intent *(v2.2)*

Declara el propósito al que apunta un esfuerzo — **no** que lo logre. Todas las actividades o procesos que apuntan al mismo `Intent` forman un grupo de esfuerzo compartido: si pertenecen a equipos distintos, son candidatos a estandarización; si divergen en su ejecución, son variantes de un mismo esfuerzo.

Una actividad puede perseguir más de un `Intent` cuando realmente sirve a propósitos distintos; no se fuerza unicidad.

### Intent —[SERVES]→ Metric | CustomerJourneyStep | Event *(v2.2)*

Expresa **para quién** es el propósito. Hacia `Metric` o `CustomerJourneyStep`: el propósito llega a la vista del cliente. Hacia un `Event` interno (p. ej. *Cobro asegurado*): el beneficiario es la propia organización. Un `Intent` sin `SERVES` es un propósito cuyo destinatario no está identificado — señal de coherencia, no error de carga.

### Intent —[CONFLICTS_WITH]→ Intent *(v2.2)*

Declara que dos propósitos tiran en direcciones opuestas. Es **simétrica**: se almacena una vez y se lee en ambos sentidos. Lleva la propiedad `conflict_kind`:

- `trade_off` — ambos son legítimos pero compiten por el mismo recurso o desenlace (p. ej. *minimizar inventario* vs *nunca quedar sin existencias*). Hallazgo a hacer visible y arbitrar.
- `opposition` — uno deshace lo que el otro produce (p. ej. *maximizar volumen de venta* vs *minimizar riesgo de crédito* aplicados al mismo cliente sin regla de arbitraje). Hallazgo de desalineación.

Con esta arista, los **esfuerzos contradictorios** son una consulta, no un cálculo: `Activity —[PURSUES]→ Intent —[CONFLICTS_WITH]— Intent ←[PURSUES]— Activity`, con prioridad cuando ambas actividades comparten proceso, equipo o beneficiario.

### Intent —[PROMOTED_TO]→ Metric *(v2.2)*

Registra que una `Metric` se originó por promoción de un `Intent`. El `Intent` **no se elimina**: permanece como trazabilidad del origen de la métrica.

**Regla de promoción** (las tres condiciones):

1. **Llega a la vista del cliente** — el `Intent` `SERVES` a un `CustomerJourneyStep` o a un `Event` visible para el cliente. Un `Intent` que solo sirve a terminales internos **nunca** se promueve (regla de coherencia de `Metric`: debe ser algo que el cliente experimenta).
2. **Está corroborado** — lo persiguen varias actividades, idealmente de distintos equipos o informantes.
3. **No está cubierto** — ninguna `Metric` existente expresa ya ese valor. Si alguna lo hace, el `Intent` se enlaza con `SERVES` a ella en lugar de crear un duplicado.

**Estatus epistemológico:** una métrica promovida sigue siendo *la creencia de la organización* sobre lo que valora el cliente; conserva el techo de abducción (`confidence ≤ 0.5`, `informant_distance=3`). Lo que mejora es `corroboration`.

> **Único punto de entrada al cálculo.** La promoción es el único mecanismo por el cual la capa de intención afecta los números: la `Metric` creada entra al subgrafo `causal` y alimenta G(A,M), B(A,M) y Relevance. Por eso es una **compuerta deliberada** (regla + revisión), nunca automática.

---

## Capa de intención — reglas de aislamiento *(v2.2)*

`Intent` y sus aristas (`PURSUES`, `SERVES`, `CONFLICTS_WITH`, `PROMOTED_TO`) son una **adición**: no modifican ningún nodo, arista ni fórmula existente.

1. **Fuera de Fase 1 y Fase 2.** Ningún subgrafo (`flow`, `bipartite_team`, `bipartite_system`, `causal`, `journey`) ni fórmula (`V(A)`, `B(A,M)`, `Relevance(A,M)`) lee esta capa. Mismo precedente que `REALIZES`: trazabilidad y coherencia, no cómputo.
2. **Los constructores de subgrafos filtran por tipo de arista, nunca "todas las aristas".** Cualquier analítica que opere sobre el grafo completo (grado para 7.2, `common_neighbors` para 7.3, `k_core` para 5.3) contaría estas aristas si no se filtra.
3. **La intención nunca sustituye al efecto.** Un `PURSUES` no crea ni infiere un `AFFECTS`. Si lo hiciera, se filtraría en G(A,M) e inflaría la relevancia con lo que la organización *quiere* que pase.
4. **La promoción es la única excepción** y pasa por compuerta explícita (ver `PROMOTED_TO`).

**Lo que habilita sin tocar los números** — señales de comparación intención vs efecto:

- **Persigue, sin efecto** — `PURSUES` hacia un `Intent` que `SERVES` a M, sin ruta `AFFECTS` a M: vínculo faltante (hueco de datos) o esfuerzo que no entrega (hallazgo). Separa el falso cero del desperdicio real.
- **Efecto, sin intención** — efecto colateral o propósito no declarado.
- **Misma intención, varios equipos** — candidatos a estandarización.
- **Intención agregada por equipo/proceso** — definición funcional de cada parte de la organización.
- **Intención perseguida, sin métrica** — candidata a promoción.
- **Métrica abducida que ninguna intención persigue** — valor que nadie en la organización está intentando entregar, aunque alguna actividad lo mueva por efecto colateral.

---

## Resumen visual de la estructura

```
[Client need / JTBD research]
        ↓
    Metric  ←——[HAS_DRIVER]——  MetricDriver
      ↑    ↖                        ↑
[AFFECTS]  [REALIZES]          [AFFECTS]
      |        \                    |
   Activity ——[PRECEDES]——→ Activity ——[PRECEDES]——→ Activity ——[INVOLVES_EVENT]——→ Event
      |              |                    |
 [PART_OF]    [USES_SYSTEM]         [TOUCHES]
      |              |                    |
   Process        System         CustomerJourneyStep
      |
 [CONTRIBUTES_TO]
      |
    Metric


Capa de intención (v2.2 — fuera del cómputo):

   Activity / Process ——[PURSUES]——→ Intent ——[SERVES]——→ Metric | CustomerJourneyStep | Event
                                       |  \
                         [CONFLICTS_WITH]  [PROMOTED_TO] ——→ Metric   (compuerta explícita)
                                       |
                                     Intent

```

El grafo es value-directed: todo converge hacia las Metrics como ancla de valor del cliente, y todo parte de Activities como unidad mínima de trabajo observable. `Event —[REALIZES]→ Metric` cierra el lado derecho del diagrama: el momento discreto en que esa convergencia efectivamente sucede. La capa de intención corre en paralelo: describe hacia dónde *apunta* cada esfuerzo, para contrastarlo con hacia dónde *llega*.