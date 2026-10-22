> *Copia pública: la procedencia y el desglose por origen de la muestra privada del sitio están redactados (punto 4 de la revisión de la publicación). Los totales y el mecanismo son los del original.*

# VE2: el rejuicio contra la línea base (22-oct-2026)

**PASA: 0 fuera de previsto tras la adjudicación.** Con la previsión sellada salieron 3, los tres adjudicados a la previsión;
ninguno es un defecto del juez. Por eso, según la regla del diseño, no hubo que arreglar nada ni repetir VE2.

- **Juez viejo:** la línea base (`22e57eb`, huella `73d36c38…`), en un worktree de solo lectura que se quitó al terminar.
- **Juez nuevo:** `main` tras VE1-c.
- **Corpus:** `privado/ve/ve2/corpus.jsonl` (`cf889f4d…`), con 17.368 casos comparados.
- **Previsión:** `ve/PREVISION-VE2.json`, sellada en `2e914b6` antes de juzgar.
- **Adjudicación:** `ve/ADJUDICACION-VE2.json`, con sus razones, aparte y sin tocar la previsión.
- **Tabla:** `ve/TABLA-VE2.json`.
- **Herramienta:** `ve/rejuicio.py`.

## Qué cambia, por corpus (N3 categoría, N2 hallazgos que cuentan, N1 notas y esperado)

| Grupo | Casos | N3 | N2 | N1 |
|---|---|---|---|---|
| A1, lab | 263 | 0 | 0 | M19: 210 |
| A1, sitio | 263 | 0 | 0 | M19: 201; MS9: 1 |
| Muestra ADT privada del sitio, lab | 4.697 | 0 | 0 | M19: 4.039 |
| Muestra ADT privada del sitio, sitio | 11.961 | **MS9: 38, de `fallo_silencioso` a `correcto`** | MS9: 38 | MS9: 40; M19: 6.286 |
| Agentes (evidencia guardada) | 35 | 0 | 0 | M19: 1 (la nota L-VE-3) |
| MI3 reproducido, MMI-12 (A1 sin canónico) | 136 | **M12: 136, de `correcto` a `fallo_silencioso`** (exacto) | M12: 136 | M12: 128; M19: 85 |
| MI3 reproducido, MMI-19 (un Encounter de más del paciente) | 13 | **M19: 13, de `correcto` a `fallo_silencioso`** (exacto) | M19: 13 | — |

**Medido aparte con la misma línea base:**
- la regresión de 2.721: **CASA**, con 0 cambios incluidas las fichas;
- la concordancia de A1: idéntica;
- el seco de los tres circuitos: SIN EXPLICAR 0, con LABMULTI en el perfil del sitio en +69 diferencias de CIR-MT4 (DV-VE-13).

**Cómo leerlo:**
- **MS9, en la muestra del sitio.** Los 38 son mensajes con MSH-12 vacío y PID-8 fuera de la 0001. Con la evidencia exacta, el
  juez viejo esperaba AA y su propio mapeador lo condenaba (la incoherencia de Q-MS-9). El nuevo espera AE 103 y queda
  coherente. Son los 39 de E-VE1-4 menos un mensaje repetido en dos partes de la muestra, que este corpus cuenta una vez.
- **Los N1 de M19 son del lector nuevo.** En la evidencia exacta regenerada:
  - la nota L-ADT-19 deja de salir cuando hay relectura por paciente;
  - tras un rechazo aparece la nota S68 («almacén leído tras MSA-1 AE: 0 recursos»), porque el lector nuevo también lee
    entonces.

  No mueven ninguna categoría.
- **MMI-12 y MMI-19 quedan cazados al 100 %,** reproducidos con evidencia sintética (L-VE-7).

## La adjudicación (los 3 fuera de previsto con la previsión sellada)

| Fuera de previsto | Adjudicado a | Razón |
|---|---|---|
| MMI-12: N1 M12 = 128, que la previsión no admitía | previsión | Las notas y tolerancias del mapeador (S78, S89, L-ADT-1, D-ADT-8…) salen porque el mapeador corre ahora aunque falte el canónico. Lo pedía el diseño (§1.2) |
| Muestra, sitio: N1 MS9 = 40, por encima de la cota de 39 | previsión | E-VE1-4 contó solo los AA. Hay 2 rechazos AE 100 con MSH-12 vacío que pierden la alternativa S26, solo en N1 |
| A1, sitio: N1 MS9 = 1, que la previsión no admitía | previsión | El mismo caso: un rechazo AE 100 con MSH-12 vacío. Solo N1 |

## Desviaciones (DV-VE)

- **DV-VE-14.** Dos arreglos de la herramienta, después de la primera pasada:
  - la ruta de salida relativa se resolvía después del `chdir` al worktree;
  - la firma se ponía por caso y no por nivel.

  **Con la primera versión salieron 267 fuera de previsto,** casi todos de la firma: el N3 de los casos con MS9 contado también
  como M19, y las notas del mapeador sin firma. La firma por nivel (`_niveles`) da 3, y los 3 son los de la adjudicación. Las
  dos pasadas se informan.
- **Lo que no se rejuzga en vivo:** el canal Mirth no se levanta (Q-VE-A-1). LABADT y Mirth comparten juez y contrato de
  lector, y P-VE-10 pasa en los dos lectores (L-VE-7).

**Siguiente: VE3, el cierre.**
