# Eneroil (datos reales) v3 — AI enhanced extended

Escenario experimental: mismo llenado que v2 más **Paso 7** (feeders
inter-área ACT-26–31 y aristas de insumo) y **Paso 8** (P/C/F/R de
actividades generadas, con C/R/F en modo simulación donde aplica).
Nodos/aristas con `generated=true` cierran brechas con confianza
explícita; el sistema compone V(A) y analíticas Fase-2 al cargar.

## Caveats

- Métricas MET-01..03 son **abducciones** (confianza ≤ 0.5), pendientes JTBD.
- Feeders llevan `fill_flag` (`contested_external` / `tier_bajo`); ACT-26 sin
  dueño de equipo; ACT-26/ACT-30 sin `PART_OF` — intencional en el inventario.
- Scores Paso 8: varios feeders marcan `score_flag=void_on_collapse`; C/R/F
  llevan `*_basis=simulated` (ejercicio de sistema, no evidencia).
- Sin nodos Supplier/Product/Regulator (fuera de ontología actual).
- Use **Mapa de confianza** en Grafo para ver certidumbre rojo→azul.
- Elementos generados aparecen semitransparentes por defecto.

Fuente: `data/raw/Eneroil_Inventario_Grafo_v3 (extended).md`
