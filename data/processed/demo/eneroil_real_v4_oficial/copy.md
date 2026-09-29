# Eneroil (datos reales) v4 — oficial

Inventario oficial (F2): mismo llenado que v3 con Paso 9 — ACT-25 y ACT-29
retirados, TEA-04 (Planeación) no es de Eneroil, ACT-32/33 extraídos,
facturación tras recepción del BOL (ACT-33 → ACT-10). Nodos/aristas con
`generated=true` cierran brechas con confianza explícita.

## Caveats

- Métricas MET-01..03 son **abducciones** (confianza ≤ 0.5), pendientes JTBD.
- MET-01 es dependencia estructural externa: Eneroil no ejecuta la entrega.
- ACT-05/06/07/26/28/32/33 sin `PERFORMS` (equipo Eneroil no resuelto).
- ACT-28 confirmado informal (`informal_no_documentado`); ya no `void_on_collapse`.
- CJS-04 sin `TOUCHES` interno (entrega = empresa de logística externa).
- Use **Mapa de confianza** en Grafo para ver certidumbre rojo→azul.

Fuente: `data/raw/Eneroil_Inventario_Grafo_v4 (oficial).md`
