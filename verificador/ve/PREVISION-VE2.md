> *Copia pública: la procedencia y el desglose por origen de la muestra privada del sitio están redactados (punto 4 de la revisión de la publicación). Los totales y el mecanismo son los del original.*

# Previsión de VE2, sellada antes de juzgar (22-oct-2026)

Se hace como dice el diseño §6. **El juez viejo** es el del commit de la línea base (`22e57eb`, huella `73d36c38…`), en un
worktree de solo lectura. **El nuevo** es el de `main` tras VE1-c. El corpus está fijado en `privado/ve/ve2/corpus.jsonl`
(sha256 `cf889f4d…`):

- **A1:** las 263 entradas.
- **Una muestra ADT privada del sitio:** los mensajes distintos.
- **Las 35 evidencias guardadas de los agentes.**

La evidencia exacta se regenera con cada juez, tal como la leería su lector (Q-VE-3). La previsión que cuenta es la de
`ve/PREVISION-VE2.json`; este texto la explica.

**Fuera de previsto:**
- cualquier diferencia sin la firma de un mecanismo;
- un mecanismo que la previsión no admite en ese grupo;
- un recuento por encima de su cota, o distinto del exacto.

| Grupo | N3 (categoría) | N2 (hallazgos que cuentan) | N1 (notas, esperado) | De dónde sale la cota |
|---|---|---|---|---|
| A1, lab | 0 | 0 | M19, sin cota | La evidencia exacta lleva canónico, así que M12 da 0. El lector nuevo relee también tras un rechazo (nota S68) y por paciente: la nota L-ADT-19 de las 86 entradas con PV1-19 vacío deja de salir |
| A1, sitio | 0 | 0 | M19, sin cota | Como en lab. En A1, MS9 da 0: las 8 entradas con S22 tienen la versión escrita (E-VE-2, E-VE1-4) |
| Muestra, lab | 0 | 0 | M19, sin cota | En lab no hay versión asumida, así que MS9 da 0 |
| Muestra, sitio | MS9 ≤ 39 | MS9 ≤ 39 | MS9 ≤ 39 y M19, sin cota | Los 39 de E-VE1-4. Con la evidencia exacta, el juez viejo espera AA y su mapeador lo condena; el nuevo espera AE 103 |
| Agentes (35) | 0 | 0 | M19 ≤ 1 | Evidencia guardada, sin `visitas_por_paciente`: solo la nota L-VE-3 en el caso adt_fhir con PV1-2 = N (E-VE1-3, DV-VE-8) |
| MMI-12 (A1 aceptadas, lab, sin canónico) | M12 = 136 | M12 = 136 | M19, sin cota | Las 136 de E-VE-3 pasan de `correcto` a `fallo_silencioso` |
| MMI-19 (A1 aceptadas con PV1-2 = N, un Encounter de más del paciente) | M19 = 13 | M19 = 13 | M19, sin cota | Las 13 de E-VE-3 |

## Lo que se midió antes de sellar, y no es ciego

- **La regresión de 2.721:** CASA en cada paso de VE1-c (`ve/comprobar.sh`), con 0 cambios en todo lo que guarda la foto,
  fichas incluidas.
- **La concordancia de A1:** idéntica.
- **El seco de los tres circuitos:** SIN EXPLICAR 0, con LABMULTI en el perfil del sitio en +69 diferencias de CIR-MT4. Es MS9
  en los puntos de solo acuse (DV-VE-13). Se vio en VE1-c, antes de esta previsión, y así se declara.
