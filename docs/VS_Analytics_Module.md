# Módulo de Analíticas — Value Stream Discovery & Graph Rendering
*Optimizer | Junio 2026*

> **Parte 1 (descubrimiento)** fue reemplazada por [`VS_Selection_Protocol.md`](VS_Selection_Protocol.md) (agrupamiento por entrega + árbol de Steiner). **Partes 2–4** de este documento (clasificación y render) siguen vigentes.

---

## Propósito del módulo

Este módulo tiene dos responsabilidades concretas dentro del sistema de analíticas de Optimizer:

1. **Descubrir automáticamente los Value Streams** a partir del grafo de conocimiento, usando Events etiquetados como puntos de demanda y de realización de valor.
2. **Clasificar todos los nodos de actividad** en cuatro categorías visuales para que la interfaz de grafo pueda renderizar el estado operativo completo de la organización de forma legible.

El módulo opera sobre el subgrafo `flow` (nodos `Activity` y `Event`, aristas `PRECEDES`) con scores semánticos de Fase 1 ya calculados (`V(A)`, `B(A,M)`, `Relevance(A,M)`).

---

## Parte 1 — Descubrimiento de Value Streams *(histórico — ver VS_Selection_Protocol.md)*

> La implementación actual usa el protocolo de selección Steiner. El contenido siguiente describe el enfoque anterior (rutas lineales por métrica) y se conserva solo como referencia.

### 1.1 Identificación de pares de eventos

El primer paso es un lookup sobre los nodos de tipo `Event`, no un algoritmo de grafos. Se filtran dos subconjuntos:

- **Eventos de demanda** (`event_type: demand`): marcan el inicio de un Value Stream. Ejemplos: firma de contrato, orden de compra, reporte de incidente.
- **Eventos de realización de valor** (`event_type: value_realization`): marcan el cierre. Ejemplos: renovación, cobro, entrega confirmada, expansión de cuenta.

Para cada métrica M, se forman pares `(demand_event, delivery_event)` que acotan el Value Stream candidato `VS_M`. Si una métrica tiene múltiples eventos de demanda o entrega, se forma un par por cada combinación relevante.

### 1.2 Enumeración de rutas candidatas

Sobre el subgrafo `flow` — que contiene solo nodos `Activity` y aristas `PRECEDES` — se corre:

```python
nx.all_simple_paths(flow_subgraph, source=demand_event, target=delivery_event, cutoff=15)
```

El parámetro `cutoff=15` previene explosión combinatoria en grafos grandes. Esto produce el conjunto completo de rutas simples entre los eventos de borde para la métrica M.

**Librería principal:** `networkx`

### 1.3 Scoring de rutas y selección del Value Stream

No todas las rutas tienen el mismo peso estratégico. Cada ruta candidata se puntúa como:

```
score(path) = Σ Relevance(A, M) para cada A en path / len(path)
```

Es decir, la suma de relevancia de los nodos en la ruta, normalizada por longitud para no favorecer artificialmente rutas largas.

La **ruta de mayor score** se designa como el Value Stream primario `VS_M`. Rutas adicionales con score dentro de un umbral configurable (por ejemplo, ≥ 80% del score máximo) se designan como **Value Streams secundarios** o variantes del mismo flujo.

**Alternativa rápida para grafos grandes:** Si el número de rutas candidatas es muy alto, se puede usar Dijkstra con peso invertido en lugar de enumerar todas las rutas:

```python
nx.dijkstra_path(flow_subgraph, source=demand_event, target=delivery_event,
                 weight=lambda u, v, d: 1 - Relevance(v, M))
```

Esto encuentra directamente la ruta de mayor valor sin enumerar. Se pierde la capacidad de comparar variantes, pero es computacionalmente viable en grafos densos.

La elección entre ambos métodos es configurable por proyecto. Para el demo de Energoil, `all_simple_paths` es adecuado dado el tamaño del grafo (43 actividades).

### 1.4 Output del descubrimiento

Por cada métrica M, el módulo produce:

- **Conjunto VS_M**: lista ordenada de nodos `Activity` que forman el Value Stream primario.
- **Score por nodo**: `Relevance(A, M)` de cada actividad en el VS, usado para el grosor de aristas en la visualización.
- **Variantes**: rutas secundarias, si existen, guardadas como `VS_M_v2`, `VS_M_v3`, etc.
- **Unión de todos los VS**: `VS_union = VS_M1 ∪ VS_M2 ∪ ... ∪ VS_Mn` — el conjunto total de nodos que pertenecen a algún Value Stream, usado como base para clasificar el resto del grafo.

---

## Parte 2 — Clasificación de nodos para rendering

Una vez conocida `VS_union`, todos los nodos `Activity` del grafo se clasifican en cuatro categorías mutuamente excluyentes. La clasificación se aplica en orden estricto: cada nodo se asigna a la primera categoría que aplica y no se reclasifica.

### Orden de clasificación

```
1. Value Stream  →  naranja/amarillo
2. Soporte estructural  →  azul
3. Soporte semántico  →  azul
4. Desperdicio  →  rojo
```

---

### Categoría 1 — Value Stream (naranja/amarillo)

**Definición:** nodo pertenece a `VS_union`.

**Algoritmo:** membresía de conjunto. Sin cómputo de grafo adicional.

```python
vs_nodes = set(VS_union)
```

**Visual:** nodo naranja/amarillo. Aristas entre nodos VS se renderizan coloreadas y con **grosor variable** proporcional a la relevancia acumulada normalizada multi-métrica del nodo destino (véase `VS_Selection_Protocol.md`) — a mayor relevancia, arista más gruesa.

---

### Categoría 2 — Soporte estructural (azul)

**Definición:** nodo que no está en `VS_union` pero es ancestro estructural de al menos un nodo VS en el subgrafo `flow`. Son los habilitadores upstream: no llegan al evento de entrega de valor, pero alimentan actividades que sí lo hacen.

**Algoritmo:**

```python
structural_support = set()
for vs_node in vs_nodes:
    ancestors = nx.ancestors(flow_subgraph, vs_node)
    structural_support.update(ancestors - vs_nodes)
```

**Librería:** `networkx`

**Visual:** nodo azul. Las aristas que conectan un nodo de soporte estructural con un nodo VS se renderizan en azul. Las aristas entre nodos de soporte estructural entre sí se renderizan en gris neutro — son conexiones internas del soporte, no la relación estratégica principal.

---

### Categoría 3 — Soporte semántico (azul)

**Definición:** nodo que no está en `VS_union` ni es ancestro estructural de ningún nodo VS, pero tiene `V(A) > umbral` y `B(A, M) = 0` para todas las métricas M. Son las actividades operativamente críticas pero invisibles al valor del cliente — los "silent enablers" identificados en la analítica 3.5.

Este es el conjunto de mayor interés estratégico dentro de los nodos azules: su ausencia del Value Stream no indica que sean prescindibles, sino que el modelo aún no ha capturado (o no existe) el camino causal hacia una métrica.

**Algoritmo:**

```python
semantic_support = set()
for node in all_activity_nodes - vs_nodes - structural_support:
    v_score = V(node)
    b_scores = [B(node, M) for M in all_metrics]
    if v_score > V_THRESHOLD and all(b == 0 for b in b_scores):
        semantic_support.add(node)
```

El umbral `V_THRESHOLD` es configurable. Valor sugerido: 0.5 (mitad del rango [0,1]).

**Librería:** pandas / lookup sobre Fase 1.

**Visual:** mismo azul que soporte estructural, pero con un marcador visual diferenciador (por ejemplo, borde punteado o ícono de advertencia) para que el analista pueda distinguirlos en el grafo. Las aristas de estos nodos se renderizan en gris — no tienen conexión semántica confirmada con el VS, y destacarlas crearía una falsa impresión de flujo.

---

### Categoría 4 — Desperdicio (rojo)

**Definición:** nodo que no pertenece a ninguna de las tres categorías anteriores. No está en ningún VS, no es ancestro estructural de ningún nodo VS, y no cumple la condición de soporte semántico. Son actividades que no contribuyen al valor del cliente ni habilitan a las que sí lo hacen, al menos dentro del modelo actual del grafo.

**Algoritmo:** residuo de la clasificación.

```python
waste_nodes = all_activity_nodes - vs_nodes - structural_support - semantic_support
```

**Visual:** nodo rojo. Las aristas de estos nodos **no se resaltan** — se renderizan en gris claro o se atenúan. La representación visual de aislamiento es parte del mensaje: un nodo rojo sin aristas visibles hacia el flujo naranja comunica por sí solo que está desconectado del valor. Resaltar sus aristas introduciría ruido y podría sugerir conexión donde no la hay.

---

## Parte 3 — Resumen de algoritmos y librerías

| Paso | Algoritmo | Función | Librería |
|---|---|---|---|
| Descubrimiento VS | Agrupamiento + Steiner | Ver `VS_Selection_Protocol.md` | networkx |
| Clasificar soporte estructural | Ancestros en subgrafo flow | `nx.ancestors(G, node)` | networkx |
| Clasificar soporte semántico | Lookup V(A) y B(A,M) | Condición sobre scores de Fase 1 | pandas |
| Clasificar desperdicio | Residuo de conjuntos | Diferencia de sets | Python built-in |
| Grosor de aristas VS | Peso proporcional a relevancia acumulada normalizada | Atributo de arista en render | Capa de visualización |

---

## Parte 4 — Decisiones de diseño registradas

**Sobre la selección del VS primario:** se eligió scoring por promedio de Relevance (no suma) para evitar que rutas largas con muchos nodos de baja relevancia superen a rutas cortas y precisas. El comportamiento puede invertirse si el contexto del cliente prioriza cobertura sobre intensidad.

**Sobre la dualidad del soporte:** se mantienen dos definiciones de soporte (estructural y semántico) porque identifican fenómenos distintos. El soporte estructural dice "esto está en el camino aunque no midamos su valor". El soporte semántico dice "esto es crítico operativamente pero no lo hemos conectado a ninguna métrica todavía". Fusionarlos en una sola categoría ocultaría esa diferencia, que es un hallazgo estratégico relevante en sí mismo.

**Sobre las aristas de nodos soporte:** se decidió colorear solo las aristas que conectan soporte estructural hacia el VS (azul), no las aristas internas entre nodos de soporte. Colorear todo el subgrafo de soporte aumenta el ruido visual sin añadir información de decisión.

**Sobre las aristas de nodos desperdicio:** se decidió explícitamente no resaltar sus aristas. La representación de aislamiento visual es parte del mensaje. Un nodo rojo con aristas visibles contradice la interpretación de desperdicio.

**Sobre el orden de clasificación:** el orden `VS → soporte estructural → soporte semántico → desperdicio` garantiza que ningún nodo sea reclasificado. Un nodo que califica como ancestro estructural de un VS *y* tiene B=0 alto-V se clasifica como soporte estructural (azul) porque la relación topológica es más fuerte que la ausencia de señal semántica.

---

## Relación con el catálogo de analíticas existente

Este módulo extiende y operacionaliza las analíticas de la Sección 6 del catálogo:

- **6.1** (Descubrimiento automático de VS) — implementado vía `VS_Selection_Protocol.md`.
- **6.2** (Comparación de VS) aplica sobre árboles por grupo, variantes de solapamiento y backbone.
- **3.5** (Relevancia propagada B=0 upstream) es la base conceptual de la categoría de soporte semántico.
- **2.4** (Ruta de mayor valor) es la alternativa Dijkstra del paso 1.3.

La clasificación de nodos producida por este módulo alimenta también:

- **7.1** (Matriz valor-dolor): los nodos VS de alto Relevance + alta fragilidad estructural son candidatos directos a inversión prioritaria.
- **4.2** (Simulación de cascada): las cascadas más significativas parten de nodos VS o de soporte estructural con alta centralidad.
