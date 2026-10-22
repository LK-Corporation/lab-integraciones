# VE1-c: el código de la etapa del verificador (22-oct-2026)

**Hecho, en el orden del diseño** (`ve/diseno-verificador-ve-fable.md` §7): MS9 → M12 → M19 en el juez → M19 en los lectores →
CT. Cada mecanismo tiene su commit, y tras cada uno se pasó `ve/comprobar.sh`: suites y autopruebas, concordancia de A1,
regresión de 2.721 frente a la foto de VE-pre, contrato y `ve/prueba_ve.py`.

| Paso | Commit | Qué cambia | Pruebas que pasan a verde | Lo demás |
|---|---|---|---|---|
| MS9 (S-VE-2) | `e70556c` | `acuse_referencia.py:645`: S22 lee la versión **escrita**; la asumida solo decide la aceptación | P-VE-12, 13 y 13b | igual |
| M12 (S-VE-1) | `928f759` | `verificador._mapeador` recibe los ACK y no pasa la lista vacía cuando se exige un canónico; manejador: sin AA se descarta, con AA y fila de éxito `fidelidad/sin_canonico`, con AA sin fila de éxito una nota (L5); texto de `no_evaluado` en el MCP | P-VE-1, 2, 3 y 3b (P-VE-4, control, sigue igual) | igual |
| M19 en el juez (S-VE-3) | `7bab5d1` | `almacen_adt`: `visitas_por_paciente` (leer, juzgar los nuevos, `almacen_sintetico`); línea de la ficha; descripción del esquema | P-VE-5, 6, 8a-8d y 9 | autoprueba de `almacen_adt`: una cambiada y una añadida (DV-VE-10) |
| M19 en los lectores | `70cc622` | `labadt/adt.py` y `mirth/lector.py`: lectura por los identificadores del mensaje (también sin canónico y con AE/AR), censo antes de enviar y relectura por paciente con `_lastUpdated` | P-VE-11 (unidad, solo lectura) en los dos lectores | igual |
| CT (S-VE-4) | `7f88302` | `mapeador_adt.CONTRATO_CANONICO` (77 campos), `consultar_tabla canonico_adt`, `contratos/generar_contrato.py` y el `.md` generado | autoprueba de cobertura (84); controles negativos comprobados | igual |

**Estado final:**
- `prueba_ve.py` da **21/21**.
- Las suites, en verde: prueba_verificador, MCP, prueba_adt 27, prueba_oru 696, prueba_multitipo 705, prueba_mutantes 38,
  prueba_arnes 11, mapeador_adt **84**, almacen_adt **18**, almacen_oru 345, acuse y mapeador_oru.
- La concordancia de A1, sin cambios.
- La regresión de 2.721, **CASA**.
- El contrato, **IGUAL** a su generación.

## El seco de los tres circuitos, con el juez nuevo

`comun/seco_ms.py` en los dos perfiles y `clasificar_seco.py`: **SIN EXPLICAR 0**.
- **LABADT y LABORU:** sin cambios en ninguno de los dos perfiles. LABADT sigue con 0 diferencias, porque ya contestaba AE 103.
- **LABMULTI, perfil del sitio:** pasa de 480 a **549 diferencias (+69), todas de CIR-MT4**. Las clases que cambian tienen todas
  la firma de MS9, «esperado AE 103, el circuito contesta AA»: adt 120 → 159 (+39), ord 63 → 84 (+21) y siu 18 → 24 (+6). Las
  otras 3 están en clases que el registro no imprime.
  - Las +39 de adt son los mismos 39 mensajes ADT de VE-pre.
  - **MS9 alcanza también a los puntos de solo acuse,** porque S22 es una regla común del acuse. VE-pre y E-VE1-4 solo
    contaron adt_fhir.
  - LABMULTI no valida el contenido (CIR-MT4), así que contesta AA donde ahora se espera AE 103.
  - Va en la previsión de VE2 (DV-VE-13).

## Desviaciones (DV-VE)

- **DV-VE-8.** La nota L-VE-3 («sin relectura por paciente») solo se añade en la evidencia antigua con PV1-2 = N. Con PV1-19
  vacío y visita ya sale la nota L-ADT-19 de siempre, que dice lo mismo. Además, la línea de la ficha solo añade «por paciente
  nuevos/previos» cuando hay `visitas_por_paciente`, para no mover la ficha del resto de la evidencia.
- **DV-VE-9.** Con `_lastUpdated` no hay forma de encontrar los Encounter antiguos del paciente: el servidor no busca por
  paciente.
  - `previos` son los Encounter del paciente tocados en la ventana antes de enviar (el mismo segundo). Una ventana que empieza
    en t0 deja fuera lo anterior por construcción.
  - Por eso no hay limpieza por paciente: no hace falta y no se podría hacer.
  - El censo usa la misma consulta que la lectura (riesgo 1 del diseño).
- **DV-VE-10.** La autoprueba de `almacen_adt` que fijaba «sin PV1-19 → nota, no se juzga» se actualizó a la regla nueva (se
  juzga, sin nota). Se añadió otra que comprueba que la evidencia antigua, sin `visitas_por_paciente`, sigue dando la nota
  L-ADT-19.
- **DV-VE-11.** La guarda de publicación no comprueba todavía que el `.md` del contrato sea igual a su generación. Lo comprueba
  `generar_contrato.py --comprobar`, que va en `ve/comprobar.sh`. Pasarlo a la guarda va con la preparación de la publicación,
  en VE3 (Q-VE-5).
- **DV-VE-12.** P-VE-11 se corrió como prueba unitaria aparte y no está en `prueba_ve.py`, porque lee del FHIR real. P-VE-10, que
  escribe en FHIR, y el piloto A3 van en VE1-d, como dice el diseño.
- **DV-VE-13.** MS9 alcanza a los puntos de solo acuse (+69 diferencias de CIR-MT4 en el seco de LABMULTI en el perfil del
  sitio). Va en la previsión de VE2.

**El circuito congelado (`observar.py`) no se toca:** el censo del lector de IRIS se engancha en el envoltorio de `observar` que
ya tenía LABADT.

**Siguiente: VE1-d.**
- P-VE-10: un Encounter sin identifier escrito a mano contra el FHIR, que el lector tiene que encontrar por el paciente.
- El piloto A3 (10 sondas) con LABADT y el lector nuevo, sin tocar el circuito y volviendo a USER en `finally`.
