


## Bridge Quantification Protocol

### Step 1 — Populate the metric layer from client interviews

The LLM processes client interview transcripts and produces:

- A set of **Metric** nodes (NRR, TTV, Perceived Reliability, etc.)
- A set of **MetricDriver** nodes per metric (e.g., NRR → expansion ARR, churn, contraction)
- A set of **CustomerJourneyStep** nodes (onboarding experience, support moment, renewal conversation, etc.)
- For each CustomerJourneyStep: a **signal strength score S ∈ [0,1]** — how frequently and intensely clients associate that moment with that metric

This is purely from the client side. The output is a scored bipartite graph: `CustomerJourneyStep —[SIGNALS]→ Metric` with weight S.

---

### Step 2 — Populate the internal graph from internal interviews

Standard extraction per the working plan: activities, processes, teams, systems, relationships. This gives you all the internal ontology nodes and edges, including:

- `Activity —[AFFECTS]→ Metric` (extracted when interviewees explicitly mention a metric)
- `Activity —[TOUCHES]→ CustomerJourneyStep` (extracted when interviewees describe client-facing moments)
- `Process —[CONTRIBUTES_TO]→ Metric` (extracted at process level)
- `Activity —[PRECEDES]→ Activity` (for flow reconstruction and P calculation)

Each extracted edge gets a **confidence score** based on how many sources mention it and how explicitly.

---

### Step 3 — Score the bridge edges

This is the core of the protocol. For each `(Activity, Metric)` pair, you compute a **Bridge Score B(A, M)** from three independent signals that already exist in the graph:

**Signal 1 — Direct graph evidence `G(A, M)` [0,1]**

Does the graph already contain a path from A to M? Score based on path type:

| Path type | Score |
|---|---|
| `Activity —[AFFECTS]→ Metric` (direct, extracted) | 1.0 × edge confidence |
| `Activity —[PART_OF]→ Process —[CONTRIBUTES_TO]→ Metric` | 0.7 × edge confidence |
| `Activity —[AFFECTS]→ Metric` via `MetricDriver` | 0.85 × edge confidence |
| No path found | 0 |

**Signal 2 — Client journey evidence `J(A, M)` [0,1]**

Does this activity touch a CustomerJourneyStep that clients associate with metric M?

```
J(A, M) = max over all journey steps K where:
  Activity —[TOUCHES]→ K  AND  K —[SIGNALS]→ M
  of: S(K, M)   ← the client signal strength from Step 1
```

If the activity doesn't touch any journey step linked to M, J = 0.

**Signal 3 — Driver path evidence `DV(A, M)` [0,1]**

Does the activity affect a MetricDriver of M?

```
DV(A, M) = 1.0 if Activity —[AFFECTS]→ MetricDriver —[HAS_DRIVER]→ M
           0.5 if Activity —[PART_OF]→ Process that affects a driver of M
           0   otherwise
```

**Combined Bridge Score:**

```
B(A, M) = w₁·G(A,M) + w₂·J(A,M) + w₃·DV(A,M)
```

Suggested starting weights: `w₁=0.4, w₂=0.4, w₃=0.2`

The weights reflect that direct graph evidence and client-side evidence are equally important, and driver-path evidence is a useful but weaker signal.

---

### Step 4 — Compute final activity relevance to metric

Combine the Bridge Score with the internal criticality score V(A) from the working plan:

```
Relevance(A, M) = B(A, M) × V(A)
```

Where `V(A) = 0.3·P + 0.4·C + 0.2·F + 0.1·R` as already defined.

This multiplication means: an activity needs to be both a genuine bridge to the client metric *and* operationally critical to rank high. Either alone is insufficient.

---

### Step 5 — Roll up to process level

```
Relevance(Process, M) = Σ [Relevance(A, M)] for all A —[PART_OF]→ Process
```

Normalized so all processes for metric M sum to 1, giving **relative contribution percentages** — which is exactly what executives need for investment decisions.

---

### What this gives you end to end

```
Client interviews
    ↓ LLM extraction
CustomerJourneyStep nodes + S scores
    ↓
J(A,M) signal ──────────────────────────┐
                                        ↓
Internal interviews                  B(A,M) × V(A) = Relevance(A,M)
    ↓ LLM extraction                    ↑
Graph edges (AFFECTS, CONTRIBUTES_TO) ──┘
    ↓
G(A,M) + DV(A,M) signals
```

---

### The one operationally critical rule

**Every Activity node needs at least one of these three edges to produce a non-zero bridge score:**
- `—[AFFECTS]→ Metric or MetricDriver`
- `—[TOUCHES]→ CustomerJourneyStep`
- `—[PART_OF]→ Process —[CONTRIBUTES_TO]→ Metric`

Activities with none of these edges get B=0 for all metrics, meaning they're invisible to the value analysis regardless of how high their V score is. So graph hygiene on these specific edge types is the most important quality gate in the whole pipeline. If an activity has a high V but B=0, that's actually a useful signal too — it means "this is operationally critical but we can't trace it to any client value yet", which is worth surfacing explicitly rather than hiding.

---

