# Protocolo de descubrimiento de Value Streams — Agrupamiento y árboles
*Optimizer | Junio 2026*

> Este documento reemplaza la versión previa basada en emparejamiento 1:1 de eventos. El emparejamiento 1:1 no se descarta: ahora es el caso degenerado de este método sobre un grafo incompleto (ver sección "Caso degenerado").

---

## Regla

Una **historia económica** — un grupo de eventos cuyas rutas operativas convergen — produce **exactamente un Value Stream**, representado como un **árbol** (no una ruta lineal) que conecta todos los eventos del grupo a través de las actividades de mayor relevancia acumulada.

El árbol permite capturar flujos multi-ancla: por ejemplo, una rama de margen y una rama de demanda de cliente que convergen en el mismo punto antes de la entrega. Esa convergencia es la representación real de "así es como el negocio genera valor", no solo "así se entrega el producto".

---

## Pipeline completo

```
Grafo → Agrupar eventos → Árbol de Steiner por grupo →
Unión de árboles + conteo de solapamiento → Clasificación de nodos → Render
```

Las dos primeras etapas (agrupar, construir árbol) son lo nuevo de este documento. De la unión en adelante, se aplica lo ya definido en `VS_Analytics_Module.md`.

---

## Parte 1 — Agrupamiento automático de eventos

El objetivo es descubrir, sin etiquetado manual, qué eventos pertenecen a la misma historia económica. La estructura del grafo ya contiene esa información: los eventos se conectan a actividades vía `INVOLVES_EVENT`, y las actividades se encadenan vía `PRECEDES`. Si las rutas de varios eventos convergen, pertenecen juntos.

### 1.1 Método base — anclaje por evento de entrega

Por cada evento de realización de valor, se camina hacia atrás en el subgrafo `flow` y se recogen todos los eventos (de demanda o precondición) que son ancestros. Esos eventos comparten destino, luego comparten historia.

```python
import networkx as nx
from itertools import combinations

def group_by_delivery_anchor(G, flow_subgraph):
    """
    Un grupo por cada evento de realización de valor.
    El grupo contiene ese evento más todos los eventos ancestros
    (demanda / precondición) alcanzables en el subgrafo flow.
    """
    delivery_events = [
        n for n, d in G.nodes(data=True)
        if d.get('event_type') == 'value_realization'
    ]

    groups = []
    for delivery in delivery_events:
        ancestors = nx.ancestors(flow_subgraph, delivery)
        anchor_events = [
            n for n in ancestors
            if G.nodes[n].get('node_type') == 'Event'
            and G.nodes[n].get('event_type') != 'value_realization'
        ]
        group = set(anchor_events) | {delivery}
        groups.append(group)

    return groups
```

Este método es **robusto a grafos incompletos**: solo requiere alcanzabilidad hacia un evento, no que dos rutas se crucen. Es el baseline por defecto.

### 1.2 Segunda pasada — fusión por cruce de rutas (opcional)

Dos grupos pueden pertenecer en realidad a la misma historia si sus rutas se cruzan en alguna actividad, aunque tengan distinto evento de entrega. Esta pasada fusiona grupos cuyos conjuntos de actividades ancestras se solapan.

```python
def merge_crossing_groups(groups, G, flow_subgraph, overlap_threshold=0.30):
    """
    Fusiona grupos cuyas actividades ancestras se solapan por encima
    de un umbral (fracción del grupo más pequeño). Controlado por umbral
    para evitar el colapso a un solo grupo gigante en grafos densos.
    """
    # Conjunto de actividades ancestras por grupo
    group_acts = []
    for group in groups:
        acts = set()
        for ev in group:
            if G.nodes[ev].get('event_type') == 'value_realization':
                acts |= {
                    a for a in nx.ancestors(flow_subgraph, ev)
                    if G.nodes[a].get('node_type') == 'Activity'
                }
        group_acts.append(acts)

    # Meta-grafo: une grupos cuyo solapamiento supera el umbral
    meta = nx.Graph()
    meta.add_nodes_from(range(len(groups)))
    for i, j in combinations(range(len(groups)), 2):
        inter = group_acts[i] & group_acts[j]
        smaller = min(len(group_acts[i]), len(group_acts[j])) or 1
        if len(inter) / smaller >= overlap_threshold:
            meta.add_edge(i, j)

    # Cada componente conexa del meta-grafo = grupo fusionado
    merged = []
    for component in nx.connected_components(meta):
        union_group = set()
        for idx in component:
            union_group |= groups[idx]
        merged.append(union_group)

    return merged
```

**Advertencia de sobre-fusión.** En un grafo bien conectado con una espina dorsal compartida, fusionar por cualquier solapamiento colapsa todo a un solo grupo gigante — lo que reintroduce el problema del "árbol único enorme" que queríamos evitar. Por eso la fusión está controlada por `overlap_threshold`. Con umbral alto, solo se fusionan grupos que comparten una porción sustancial de su flujo. Para el demo se recomienda empezar con el baseline (1.1) sin fusión, y activar la segunda pasada solo de forma diagnóstica para ver qué grupos se unirían.

### 1.3 Caso degenerado — grafo incompleto

Si el grafo es muy disperso (faltan aristas `PRECEDES`, eventos sin ancestros compartidos), ningún grupo crece más allá de un evento de demanda y su evento de entrega. El resultado es un conjunto de pares aislados — exactamente el emparejamiento 1:1 del protocolo anterior.

Esto **no es un modo especial ni un fallback**: es el mismo algoritmo produciendo su salida mínima sobre un grafo pobre. La propiedad importante es que el método es consciente de la calidad del grafo por construcción:

> A medida que el grafo se completa — más aristas `PRECEDES`, más eventos etiquetados, más actividades conectadas — los grupos crecen naturalmente, los troncos emergen y el insight se profundiza. No se cambia el algoritmo; se le alimenta un mejor grafo y produce salida más rica.

Esto convierte la **completitud del grafo en una métrica explicable para el cliente**: "hoy tu grafo produce X grupos de tamaño promedio Y; al completar conexiones faltantes, estos grupos se fusionarán y el tronco se hará más claro". Es un argumento concreto a favor del trabajo continuo de refinamiento del inventario del grafo.

---

## Parte 2 — Construcción del Value Stream como árbol de Steiner

Dado un grupo de eventos, el Value Stream es el árbol de menor costo que conecta todos esos eventos a través del subgrafo `flow`, donde el costo de cada arista es inverso a la relevancia acumulada multi-métrica del nodo destino. El árbol "quiere" pasar por actividades de alta relevancia.

### 2.1 Relevancia acumulada multi-métrica con normalización por métrica

**Decisión clave:** las métricas se normalizan individualmente a [0,1] antes de sumar. Sin esto, una métrica con magnitudes de relevancia altas domina la suma y el "backbone multi-métrica" sería en realidad el backbone de esa sola métrica disfrazado. La normalización garantiza que cada métrica pese igual.

```python
def cumulative_relevance_normalized(relevance, all_metrics, activities):
    """
    Normaliza la relevancia de cada métrica a [0,1] (min-max) y luego suma.
    Rango del resultado por actividad: [0, len(all_metrics)].
    """
    cum = {a: 0.0 for a in activities}
    for M in all_metrics:
        vals = {a: relevance.get((a, M), 0.0) for a in activities}
        mx = max(vals.values()) or 1.0
        for a in activities:
            cum[a] += vals[a] / mx
    return cum
```

### 2.2 Asignación de costos a las aristas

```python
def set_edge_costs(flow_subgraph, cum_relevance):
    """
    Costo de arista (u,v) = 1 - relevancia_normalizada(v) / max.
    Aristas hacia nodos de alta relevancia tienen costo bajo.
    """
    max_cum = max(cum_relevance.values()) or 1.0
    for u, v in flow_subgraph.edges:
        norm = cum_relevance.get(v, 0.0) / max_cum
        flow_subgraph[u][v]['vs_cost'] = 1.0 - norm
```

### 2.3 Árbol de Steiner por grupo

```python
from networkx.algorithms.approximation import steiner_tree

def build_vs_tree(group, flow_subgraph):
    """
    Árbol de Steiner que conecta todos los eventos del grupo.
    networkx implementa Steiner sobre grafos NO dirigidos, así que se
    trabaja sobre la versión no dirigida y luego se recupera la dirección
    original de cada arista para el render.
    """
    terminals = [n for n in group if n in flow_subgraph]
    if len(terminals) < 2:
        return None  # grupo sin suficientes anclas conectables

    undirected = flow_subgraph.to_undirected()
    tree_undirected = steiner_tree(undirected, terminals, weight='vs_cost')

    # Recuperar dirección original (el subgrafo flow es un DAG de PRECEDES)
    tree = nx.DiGraph()
    tree.add_nodes_from(tree_undirected.nodes(data=True))
    for u, v in tree_undirected.edges:
        if flow_subgraph.has_edge(u, v):
            tree.add_edge(u, v)
        elif flow_subgraph.has_edge(v, u):
            tree.add_edge(v, u)

    return tree
```

**Nota sobre direccionalidad.** `nx.algorithms.approximation.steiner_tree` opera sobre grafos no dirigidos. Como el subgrafo `flow` es un DAG de relaciones `PRECEDES`, la estructura de conexión que encuentra Steiner es correcta; solo se restaura la dirección de cada arista desde el grafo original para el render. Si en el futuro se requiere un árbol dirigido estricto (arborescencia), habría que implementar un Steiner dirigido, que no está en el core de networkx — no es necesario para el demo.

### 2.4 Sobre la frontera de Pareto

En la formulación anterior (rutas lineales), la frontera de Pareto servía para elegir entre rutas candidatas. En la formulación de árbol, el árbol de Steiner queda determinado por el grupo de terminales y los pesos de arista — la relevancia acumulada ya está embebida en los costos, no se aplica como score posterior.

Por tanto, **la frontera de Pareto deja de ser parte del camino principal** y pasa a ser una herramienta diagnóstica opcional: si se generan árboles alternativos (por ejemplo, con distintos subconjuntos de terminales o distintas configuraciones de peso), se pueden comparar en el plano relevancia-vs-tamaño para entender el trade-off. Pero el pipeline por defecto no la requiere.

---

## Parte 3 — Unión de árboles y backbone

Se construye un árbol por grupo. Luego se superponen todos y se cuenta, por nodo y por arista, en cuántos árboles aparece. Ese conteo de solapamiento es el indicador de infraestructura compartida: un nodo usado por muchos árboles es estructuralmente crítico para múltiples historias de valor.

```python
def union_and_overlap(trees):
    """
    Superpone todos los árboles VS. Devuelve el grafo unión y los
    conteos de solapamiento por nodo y por arista.
    """
    node_overlap = {}
    edge_overlap = {}
    union = nx.DiGraph()

    for tree in trees:
        if tree is None:
            continue
        for n in tree.nodes:
            node_overlap[n] = node_overlap.get(n, 0) + 1
        for u, v in tree.edges:
            edge_overlap[(u, v)] = edge_overlap.get((u, v), 0) + 1
        union = nx.compose(union, tree)

    return union, node_overlap, edge_overlap


def identify_backbone(node_overlap, min_overlap=2):
    """
    Backbone = nodos presentes en al menos `min_overlap` árboles.
    Es lo que sostiene el negocio a través de múltiples historias de valor.
    """
    return {n for n, count in node_overlap.items() if count >= min_overlap}
```

El **backbone** responde directamente a la pregunta del cliente: *qué está sosteniendo el negocio, para poder reforzarlo y escalar carga manteniendo la calidad*. Cada nodo del backbone trae un número (en cuántas historias de valor participa) que justifica la inversión.

---

## Parte 4 — De la unión a la clasificación y el render

`VS_union` para el render es el conjunto de nodos de la unión de árboles:

```python
vs_union = set(union.nodes)
```

De aquí en adelante aplica **sin cambios** lo definido en `VS_Analytics_Module.md`:

- **Clasificación de nodos** en orden: VS (naranja) → soporte estructural (azul) → soporte semántico (azul punteado) → desperdicio (rojo).
- **Render de aristas**: VS con grosor variable según relevancia; soporte estructural→VS en azul; aristas de desperdicio atenuadas.
- El **conteo de solapamiento** de la Parte 3 se puede mapear adicionalmente al grosor o intensidad de color de los nodos del backbone.

---

## Pipeline ensamblado

```python
def discover_value_streams(G, flow_subgraph, relevance, all_metrics,
                           merge_crossing=False, overlap_threshold=0.30,
                           backbone_min_overlap=2):
    # 1. Agrupar
    groups = group_by_delivery_anchor(G, flow_subgraph)
    if merge_crossing:
        groups = merge_crossing_groups(groups, G, flow_subgraph, overlap_threshold)

    # 2. Costos de arista (relevancia acumulada normalizada por métrica)
    activities = [n for n, d in flow_subgraph.nodes(data=True)]
    cum = cumulative_relevance_normalized(relevance, all_metrics, activities)
    set_edge_costs(flow_subgraph, cum)

    # 3. Árbol por grupo
    trees = [build_vs_tree(group, flow_subgraph) for group in groups]

    # 4. Unión, solapamiento, backbone
    union, node_overlap, edge_overlap = union_and_overlap(trees)
    backbone = identify_backbone(node_overlap, backbone_min_overlap)

    return {
        'groups': groups,
        'trees': trees,
        'union': union,
        'vs_union': set(union.nodes),
        'node_overlap': node_overlap,
        'edge_overlap': edge_overlap,
        'backbone': backbone,
        'group_count': len(groups),
        'avg_group_size': sum(len(g) for g in groups) / len(groups) if groups else 0
    }
```

`group_count` y `avg_group_size` son las métricas de calidad del grafo mencionadas en 1.3 — sirven para mostrar al cliente cómo madura el modelo conforme se completa el grafo.

---

## Decisiones de diseño registradas

**Árbol en lugar de ruta.** Se eligió el árbol de Steiner porque el negocio (caso Energoil) tiene preconditiones económicas múltiples — margen, suministro, demanda de cliente — que deben converger para que el valor se realice. Una ruta lineal solo captura un afluente; el árbol captura la confluencia, que es la descripción real de cómo se genera valor.

**Agrupamiento automático por anclaje de entrega.** Se eligió como baseline porque es robusto a grafos incompletos y no requiere etiquetado manual de qué eventos van juntos. La fusión por cruce de rutas es una segunda pasada opcional y controlada por umbral, por el riesgo de sobre-fusión en grafos densos.

**Normalización por métrica antes de sumar.** Necesaria para que el backbone multi-métrica trate todas las métricas por igual y no quede dominado por la métrica de mayor magnitud de relevancia.

**El emparejamiento 1:1 es el caso degenerado, no un método aparte.** El mismo algoritmo produce pares aislados sobre un grafo pobre y troncos ricos sobre un grafo completo. Esto hace que la completitud del grafo sea una métrica explicable de madurez del modelo.

**Pareto pasa a ser diagnóstico.** Con la formulación de árbol, la relevancia acumulada vive en los pesos de arista; la frontera de Pareto ya no es parte del camino principal y se reserva para comparar árboles alternativos.

**El conteo de solapamiento es el output estratégico.** Responde "qué sostiene el negocio" con un número por nodo, preservando a la vez las historias por grupo y el poder discriminante de la clasificación naranja/azul/rojo.
