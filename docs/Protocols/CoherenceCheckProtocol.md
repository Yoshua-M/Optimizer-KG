# Protocolo de auditoría de coherencia

*General — reproducible para cualquier caso. v0.3: topología automática; ontología con autorización; fusión medio-a-fin.*

---

## Propósito

Verificar que el grafo sea un **patrón con propósito del esfuerzo organizacional**: cada esfuerzo tiene un *para qué* y un *para quién* legibles, está conectado al valor tan alto como la evidencia permite, las tensiones están localizadas y cada afirmación es tan fuerte como su sustento.

La auditoría **no** busca que el grafo sea una imagen fiel de la realidad. Busca que el patrón sea coherente, **reparar** donde el modelo falla (generando elementos de ontología), **exponer** donde la organización misma es incoherente y **preguntar** lo que el grafo no puede decidir.

Se ejecuta sobre el grafo ya llenado (Protocolo de llenado, Pasos 1–6). Es un **ciclo**: el chequeo estructural va primero y se repite hasta que el grafo sea coherente según la definición técnica de abajo.

---

## Principios

1. **Toda actividad tiene intención.** Si hay trabajo, hay propósito, aunque nadie lo declare. Una `Activity` sin intención (propia o heredada) es un **defecto del grafo** y se repara. La intención puede chocar con la dirección de la organización; eso se registra, no se corrige.
2. **La intención es el piso, no la meta.** Existe porque no todas las actividades logran conectarse a una `Metric`. El ciclo busca subir cada actividad lo más alto posible en la escalera de conexión al valor (ver abajo).
3. **Parsimonia de intenciones.** Por defecto la intención vive en el `Process` y sus actividades la heredan. Una actividad declara intención propia solo cuando no encaja con la del proceso. Antes de crear una intención se consulta el inventario: **reusar antes que crear**.
4. **Menos intenciones es avance.** Detectar que más actividades comparten un propósito es uno de los objetivos de la auditoría. Pero la compresión es **señal, no objetivo**: nunca se fusionan intenciones con propósito distinto ni intenciones en `CONFLICTS_WITH`.
5. **La intención es la llave de consolidación.** Descripciones divergentes con la misma intención se consolidan en una actividad canónica con variantes; con intención distinta son actividades distintas.
6. **Nada se borra, con una excepción.** La extracción original es inmutable (`generated=false`); consolidar actividades crea una canónica y enlaza las originales. La **única** excepción es la fusión de intenciones: la intención fusionada se elimina y sus aristas pasan a la canónica. Toda eliminación se **reporta**.
7. **El juicio escribe aristas; el cálculo las lee.** Las decisiones semánticas (LLM + evidencia) quedan como nodos o aristas; los chequeos estructurales son consultas deterministas sobre ellos.
8. **Métricas: fit primero.** Una métrica se añade solo si ninguna del inventario encaja; se añade con evidencia y **se reporta** como métrica añadida.
9. **Defecto se repara; hallazgo se expone; residuo se pregunta.**
10. **Topología vs ontología.** Las **reparaciones topológicas** (mismos tipos de nodo/arista: `PRECEDES`, `INVOLVES_EVENT`, `REALIZES`, unir colgantes, hacer alcanzable el terminal de valor) se **aplican automáticamente** cuando restauran coherencia y **siempre se reportan** (Sección 2). Las **reparaciones de ontología** (tipos nuevos, métricas nuevas, fusión/eliminación de `Intent`, `VARIANT_OF`, promoción Intent→Metric, o cualquier cambio al vocabulario) **requieren autorización explícita antes de ejecutarse**; sin ella solo se proponen en el reporte.

---

## Escalera de conexión al valor *(solo auditoría — no entra al cálculo)*

Cada actividad queda en el nivel más alto que alcanza:


| Nivel  | Conexión             | Ruta                                                                   |
| ------ | -------------------- | ---------------------------------------------------------------------- |
| **N1** | Métrica              | `AFFECTS` directa o vía `MetricDriver`                                 |
| **N2** | Métrica vía proceso  | `PART_OF` → `CONTRIBUTES_TO`                                           |
| **N3** | Intención de soporte | Su intención `SERVES` a una `Metric`, sin arista de efecto             |
| **N4** | Solo intención       | Propósito extraído, sin enlace a `Metric` (interno o sin beneficiario) |


N3 y N4 no alteran `Relevance(A,M)`: una actividad en N3 conserva relevancia 0. La escalera es un diagnóstico, no un puntaje.

---

## Adiciones de ontología que requiere *(pendientes de incorporar a la Ontología v2.2)*

- **Invariante:** toda `Activity` tiene intención, propia (`PURSUES`) o heredada (su `Process` —[PURSUES]→ `Intent`).
- **Varias intenciones por actividad:** permitido. Orden de asignación: la del proceso → las del inventario → una nueva. Cada intención adicional lleva su propio `evidence_pointer`.
- `Activity —[VARIANT_OF]→ Activity` (variante → canónica). Propiedades: `divergence` (`quién` | `cómo` | `orden` | `sistema` | `granularidad`), fuente e informante. Las variantes quedan fuera de los subgrafos de Fase 1 y Fase 2.
- **Calibración de** `Intent`**:** `basis=evidence` si la fuente declara el propósito; `basis=abduction` si se infiere del esfuerzo. Techo, no compuerta: abducida con `confidence ≤ 0.5`, nunca se descarta.

---

## Definición técnica de coherencia (criterio de paro)

El grafo es **coherente** cuando se cumplen todos los invariantes:

- **I1 · Intención total:** toda actividad tiene intención, propia o heredada.
- **I2 · Ubicación en la escalera:** toda actividad tiene nivel N1–N4.
- **I3 · Integridad estructural:** sin ciclos en `PRECEDES`, esquema válido, `s(A,T)` suma 1, variantes fuera de los subgrafos.
- **I4 · Sin banderas sin clasificar:** toda bandera es defecto reparado, hallazgo o residuo.
- **I5 · Punto fijo:** una corrida completa no produce reparaciones ni fusiones de intenciones nuevas.

**Guarda de no convergencia:** si una iteración no reduce el número de defectos, el ciclo para; los defectos restantes pasan a residuo como *no convergentes*.

**Grado de coherencia** (comparable entre corridas y entre grafos):

- distribución de actividades en N1–N4;
- proporción de intenciones por evidencia vs abducidas;
- **compresión de intenciones**: actividades por intención (debe subir entre corridas).

---

## El ciclo

**0. Cargar** el grafo, el inventario de intenciones y el inventario de métricas.

**1. Chequeo estructural** *(cálculo — siempre primero)*


| ID  | Chequeo                            | Qué calcula                                                                                                                                                                     |
| --- | ---------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| C1  | Cobertura de intención             | Actividades sin intención propia ni heredada; `Intent` sin `SERVES`                                                                                                             |
| C2  | Desviación de intención            | Actividades cuya intención propia difiere de la de su proceso                                                                                                                   |
| C3  | Nivel en la escalera               | Asigna N1–N4 a cada actividad por existencia de rutas                                                                                                                           |
| C4  | Alineación intención–efecto        | Persigue M sin ruta de efecto a M · efecto sin intención · métrica que nadie persigue                                                                                           |
| C5  | Alcanzabilidad de propósito        | Actividad cuya intención sirve al `Event` E: ¿llega a E por `PRECEDES`?                                                                                                         |
| C6  | Completitud de flujo               | Demandas sin ruta a valor; fragmentos; actividades colgantes                                                                                                                    |
| C7  | Ajuste de rol (mecánico)           | Ciclos en `PRECEDES`; actividades posteriores a su terminal; prior P vs proximidad calculada                                                                                    |
| C8  | Exposición de conflictos           | Pares de actividades con intenciones en conflicto (priorizados por proceso, equipo, beneficiario o sistema compartido) · actividades que persiguen dos intenciones en conflicto |
| C9  | Candidatos a variante              | Actividades de distintas fuentes con misma intención y vecindario superpuesto                                                                                                   |
| C10 | Candidatos a fusión de intenciones | Intenciones con formulación similar, mismo `SERVES` y actividades superpuestas                                                                                                  |
| C11 | Perfil funcional                   | Por equipo y proceso: intenciones perseguidas, proporción al cliente / interna / sin beneficiario / en conflicto                                                                |
| C12 | Calibración                        | Top N de relevancia sustentado en aristas `confidence ≤ 0.5` o `corroboration = 1`; aristas críticas con una sola mención                                                       |
| C13 | Integridad de esquema              | Propiedades obligatorias, tipos de arista permitidos, `s(A,T)`, exclusión de variantes                                                                                          |
| C14 | Estabilidad y compresión           | Contra la corrida anterior: cambio en banderas y top N; cambios fuera del vecindario de lo actualizado; compresión de intenciones                                               |


**2. ¿Coherente?** Si se cumplen I1–I5 → termina.

**3. Triage** *(LLM + evidencia)*: cada bandera se clasifica como **defecto** (incoherencia del modelo), **hallazgo** (incoherencia de la organización) o **residuo** (indecidible desde el grafo → pregunta de validación).

**4. Reparación**


### Política de qué se puede aplicar solo

| Clase | Ejemplos | Ejecución |
| ----- | -------- | --------- |
| **Topología** | `PRECEDES`, `INVOLVES_EVENT`, `REALIZES`, alcanzar terminal, enlazar colgantes, **clasificar/aceptar forks 3.2** (hito en paralelo, rama de excepción, paralelo al mismo sink) | Automática; **reportar** resueltos en Sección 2; solo irresolubles en Sección 3 |
| **Claridad de nombres** | Renombrar actividades para distinguir pasos del mismo Intent (anti-falso-variante) | Automática cuando hay regla de claridad; **reportar**; pares aún ambiguos → Sección 3 |
| **Ontología / capa Intent** | Fusionar/eliminar `Intent`, nuevo tipo o `Metric`, `VARIANT_OF`, `PROMOTED_TO`, `AFFECTS` inventados | Solo con **autorización explícita**; si no, proponer en Sección 3 |

- **R1 · Asignar intención:** orden proceso → inventario → nueva. Se admiten intenciones defensivas o inerciales; nunca se inventa un propósito favorable donde la evidencia sugiere uno defensivo. *(Ontología — requiere autorización si crea `Intent` nuevos; la primera corrida de un grafo sin Intent suele autorizarse como bootstrap.)*
- **R2 · Beneficiario:** enlazar `SERVES` a Metric / Journey / Event existente. Crear Event interno nuevo solo con autorización. Si no hay destino, hallazgo (1.7).
- **R3 · Fusionar intenciones** *(autorización requerida)* — dos vías:
  1. **Equivalencia** (formulación similar, mismo `SERVES`, perseguidores solapados).
  2. **Medio-a-fin (means-to-end):** si la intención A solo habilita realizar la intención B en el mismo camino de valor (p. ej. actividades de A `PRECEDES` hacia actividades que persiguen B, o A es feeder del proceso de B), **fusionar A → B**. Si el propósito es ortogonal (cumplimiento, quejas, auditoría vs comercial), **conservar** A y darle `SERVES` propio cuando exista destino. Nunca fusionar intenciones en `CONFLICTS_WITH`.
- **R4 · Decidir conflictos:** `CONFLICTS_WITH` — autorización / juicio.
- **R5 · Consolidar variantes:** `VARIANT_OF` — autorización. **Antes** de proponer consolidación: (a) si hay `PRECEDES` entre el par o roles léxicos distintos (p. ej. seguimiento vs vencida vs escalamiento), **no son variantes** — resolver como distintos y reportar; (b) si el nombre confunde, **renombrar** con regla de claridad y reportar (2.9). Solo queda en Sección 3 lo aún ambiguo.
- **R6 · Topología y escalera:** terminals `REALIZES`, `PRECEDES` de alcanzabilidad, colgantes. **Forks sin reconvergencia (check 5):** intentar resolver — aceptar hito Event en paralelo, fork Event+Activity (continuación vs terminal/excepción), o brazos que comparten sinks finales; si aplica, unir con `PRECEDES` al terminal común. Reportar cada caso resuelto (2.8). **Solo** los forks que no encajan en esos patrones quedan en Sección 3. **No** inventar `AFFECTS` para 1.5.
- **R7 · Métricas:** añadir Metric — autorización (ontología).

**5. Volver al paso 1.**

---

## Reporte

El reporte **explica situaciones**, no vuelca registros. Su lector debe entender qué pasa, por qué importa y dónde, sin consultar el grafo.

### Reglas de legibilidad

1. **Nunca un ID solo.** Todo elemento se escribe `Nombre (ID)`. Los IDs son para el sistema; el nombre es para el lector.
2. **Cada caso trae su contexto completo.** Cada situación define sus **campos de contexto**: la cadena de elementos sin la cual el caso no se entiende (p. ej. actividad → proceso → intención → métrica). Un caso con un campo vacío se muestra con "—" y el motivo, nunca omitiendo el campo.
3. **Solo situaciones con casos.** Las que no tienen casos se listan en una sola línea al final de su sección.
4. **Orden por importancia** dentro de cada sección, según el número de casos y su cercanía a métricas.

### Formato de cada situación

1. **Situación** — nombre y una línea que la describe.
2. **Por qué importa** — qué implica para la organización o para la coherencia del grafo.
3. **Explicación** — qué significa, cómo se detectó y qué *no* significa (p. ej. si puede ser hueco de datos o hallazgo real).
4. **Casos** — tabla con los campos de contexto de la situación, una fila por caso.

### Encabezado

Grado de coherencia antes → después (N1–N4, evidencia vs abducción, compresión de intenciones), número de iteraciones, si el ciclo convergió, y las 3 situaciones más importantes de cada sección (1, 2 y 3).

### Sección 1 — Salud de las intenciones

Todo lo que tiene que ver con cómo están creadas, asignadas y relacionadas las intenciones.


| Situación                                 | Campos de contexto por caso                                                                                                           |
| ----------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------- |
| 1.1 Actividades sin intención (reparadas) | Actividad · Proceso · Intención asignada · Origen (heredada / inventario / nueva) · Base (evidencia / abducción) · Evidencia          |
| 1.2 Intención desviada del proceso        | Actividad · Proceso · Intención del proceso · Intención de la actividad · A quién sirve cada una                                      |
| 1.3 Intenciones en conflicto              | Intención A · Intención B · Tipo (trade-off / oposición) · Actividades de cada lado con su proceso y equipo · Beneficiario compartido |
| 1.4 Tensión interna                       | Actividad · Proceso · Equipo · Las dos intenciones en conflicto                                                                       |
| 1.5 Persigue sin llegar                   | Actividad · Proceso · Intención · Métrica a la que sirve · Qué ruta falta · *(solo reporte por ahora — no auto-`AFFECTS`)* |
| 1.6 Valor que nadie persigue              | Métrica · Actividades que la mueven por efecto, con su proceso                                                                        |
| 1.7 Intención sin beneficiario            | Intención · Actividades y procesos que la persiguen · ¿Propuesta merge medio-a-fin? / ¿SERVES candidato?                          |
| 1.8 Intenciones fusionadas (eliminadas)   | Intención eliminada · Intención canónica · Actividades reasignadas con su proceso · Evidencia de equivalencia o medio-a-fin         |
| 1.9 Dispersión funcional                  | Equipo o Proceso · Intenciones que persigue · Proporción al cliente / interna / sin beneficiario / en conflicto                       |


### Sección 2 — Cambios en el grafo

Lo que la auditoría cambió en el grafo, **excluyendo intenciones** (ya cubiertas en la Sección 1). Cada situación indica en su "Por qué importa" qué condición de coherencia (I1–I5, escalera) restablece.


| Situación                      | Campos de contexto por caso                                                                                                                      |
| ------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------ |
| 2.1 Actividades consolidadas   | Actividad canónica · Variantes (nombre, fuente, informante) · En qué difieren · Proceso · Equipos · `PERFORMS` disputado y su efecto en `s(A,T)` |
| 2.2 Actividades generadas      | Actividad · Proceso · Entre qué actividades se insertó · Qué flujo cerró (hacia qué evento) · Base                                               |
| 2.3 Aristas de efecto añadidas | Actividad · Proceso · Métrica · Nivel antes → después · Evidencia                                                                                |
| 2.4 Orden / alcanzabilidad corregida | Actividades u eventos involucrados · Proceso · Qué cambió (`PRECEDES` / `REALIZES` / `INVOLVES_EVENT`) · Evento terminal · Métrica |
| 2.5 Métricas añadidas          | Métrica · Origen · Actividades y procesos que la sostienen · Evidencia · Por qué ninguna existente encajaba                                      |
| 2.6 Correcciones de esquema    | Elemento · Qué se corrigió                                                                                                                       |
| 2.7 Reparaciones topológicas (resumen) | Lista corta de aristas/nodos de instancia añadidos en la corrida (todos reportados; ninguno es tipo ontológico nuevo)                    |
| 2.8 Bifurcaciones resueltas    | Nodo horquilla · Sucesores · Resolución (hito paralelo / excepción / sinks compartidos / join) · Evidencia                                      |
| 2.9 Renombres de claridad      | Actividad · Nombre anterior · Nombre nuevo · Motivo (anti-confusión / distinguir de hermana)                                                     |


### Sección 3 — Pendientes a resolver

Hallazgos y residuos que el ciclo **dejó sin reparar** y que **no** caben en la Sección 1 ni 2. En particular:

- **Forks (ex-3.x topología de ramas):** solo los que **no** se pudieron clasificar ni unir (R6).
- **Candidatos a variante:** solo pares aún ambiguos tras renombre/clasificación como distintos (R5 claridad). No listar lo ya resuelto en 2.8 / 2.9.

Misma plantilla de situación (Situación / Por qué importa / Explicación / Casos). Los **campos de contexto los define cada situación** según lo que el caso necesita para entenderse — no hay catálogo cerrado de columnas. La corrida numera solo las que tienen casos (`3.1`, `3.2`, …), ordenadas por importancia (número de casos y cercanía a métricas). Las situaciones de esta sección sin casos **no** se listan (a diferencia de las Secciones 1 y 2).

---

## Herramientas a implementar

- **Módulo de cálculo sobre el grafo** (C1–C14): existencia y alcanzabilidad de rutas, conectividad, ciclos, similitud de vecindario, agregación, comparación de rankings.
- **Módulos de juicio LLM** (triage, R1–R5, R7): emiten elementos con el esquema común y `evidence_pointer`; consultan los inventarios de intenciones y métricas antes de crear.
- **Escritor del inventario:** agrega elementos generados sin sobrescribir la extracción original.
- **Controlador del ciclo:** evalúa I1–I5 y la guarda de no convergencia.
- **Comparador de corridas** (C14) y **generador de reporte** (Reporte: arma cada situación con sus campos de contexto y resuelve cada ID a `Nombre (ID)`; Sección 3 agrupa pendientes no cubiertos por 1–2).

