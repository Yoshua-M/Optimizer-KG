# Eneroil (datos reales) v2 — AI enhanced

Escenario experimental con **llenado generado** sobre la extracción real v1.
Los nodos/aristas con `generated=true` cierran brechas ontológicas con
confianza explícita; el sistema compone V(A) y analíticas Fase-2 al cargar.

## Caveats

- Métricas MET-01..03 son **abducciones** (confianza ≤ 0.5), pendientes JTBD.
- Dimensiones P/C/F/R incluyen confianza por celda; F mayormente null.
- Use **Mapa de confianza** en Grafo para ver certidumbre rojo→azul.
- Elementos generados aparecen semitransparentes por defecto.

Fuente: `data/raw/Eneroil_Inventario_Grafo_v2(filled).md`
