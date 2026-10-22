> *Copia pública: la procedencia y el desglose por origen de la muestra privada del sitio están redactados (punto 4 de la revisión de la publicación). Los totales y el mecanismo son los del original.*

# Resultado de VE-pre: el eslabón débil de la etapa del verificador (14k, 22-oct-2026)

**PASA.** Las cuatro sondas contestan y no salta ninguna regla de parada: hay línea base, y MMI-12 se puede cerrar sin
falsas alarmas en lo guardado. Todo fue de solo lectura: el juez, IRIS, FHIR, los circuitos y las cajas quedan como estaban.
El guion es `ve/ve_pre.py` (e1, e2 y e3). El detalle por caso está en `privado/ve/pre/`, fuera de git.

## E-VE-4: la línea base, antes de tocar nada

La foto `/tmp/a1b` que se perdió era la copia del perfil privado que se hizo en A1b. La regresión estándar del juez es un
conjunto de pruebas (`RESULTADO-A1B.md`), y se rehízo entera con el juez de `22e57eb`, sin cambios desde `54d0eca`. Queda en
`privado/ve/linea_base/`, en `/datos` y no en `/tmp`.

| Prueba | Resultado | Igual que |
|---|---|---|
| `regresion_perfil.py foto` (2.721 instancias) | sha256 `99ac11be…` | (es la foto nueva) |
| La misma foto, otra vez | CASA | determinista |
| Control: un veredicto cambiado a mano en una copia | PARA (1 motivo) | el comparador ve el cambio |
| `prueba_verificador`, `mcp_verificador --autoprueba` | TODO BIEN | MI4 |
| `prueba_adt` 27, `prueba_oru` 696, `prueba_multitipo` 705, `prueba_mutantes --mutantes` 38, `prueba_arnes` 11 | en verde | MI4 |
| Autopruebas `mapeador_adt` 83, `almacen_adt` 17, `almacen_oru` 345, `acuse_referencia` y `mapeador_oru` | en verde | MI4 |
| Concordancia de A1 | 8.039 hojas y 6.255 iguales; el JSON, idéntico al de git | A1b |
| Seco de los tres circuitos en los dos modos (`comun/seco_ms.py`) y `clasificar_seco.py` | **SIN EXPLICAR 0**: LABADT, 0 diferencias en 3.308 casos por modo; LABORU, CIR-MS-3/4; LABMULTI, CIR-MT1/4 | MS1c |

Los registros de cada prueba llevan su huella en `privado/ve/linea_base/suites.sha256` (`c8c62eef…`).

## E-VE-3: MMI-12 y MMI-19, sin Mirth

Las salidas de los mutantes de Mirth no se guardaron: `mirth/mi3.json` es un resumen. Pero la evidencia de MI3 era
sintética, así que el hueco se reproduce con el constructor de evidencia exacta de `prueba_adt.py`.

- **MMI-12 en adt_fhir.** De las 263 entradas de A1, el acuse acepta 136.
  - Con evidencia exacta salen 136 `correcto` (control positivo).
  - Con el canónico alterado, las 136 dejan de ser `correcto` (control negativo).
  - **Sin `canonico_adt`, salen 136 `correcto`.** El hueco queda reproducido.
- **El mecanismo.** `_mapeador` trata «ninguna sesión trae canónico» como fuera de alcance y pasa la lista vacía
  (`canon = []`).
  - Con la lista vacía, `mapeador_adt.revisar` devuelve `None` y no compara nada.
  - Con un hueco en la lista (`[None]`), en cambio, dice «no hay canónico para este mensaje», y eso da
    `fidelidad/sin_canonico`. Comprobado sobre una entrada de A1.
- **Es más ancho de lo que midió MI3,** porque el mismo camino sirve para adt_a01 y para oru_fhir.
  - **adt_a01 (el circuito congelado):** las 1.847 instancias de la regresión que salen `correcto` con canónico siguen
    `correcto` al quitárselo.
  - **oru_fhir (9 casos del agente):** uno pasa de `fallo_silencioso` a `correcto` al quitarle el canónico. **El hueco
    esconde un fallo real.**
- **MMI-19 no es un hueco del juez, sino del lector.**
  - Con un Encounter de más en `almacen_adt` y PV1-2 = N, el juez lo ve en las 13 entradas aceptadas de A1 que lo
    permiten (`fidelidad/almacen`). Lo que falla es que el lector solo relee por los identificadores del canónico.
  - **10 de esas 13 tienen PV1-19 vacío.** Releer «por los identificadores del mensaje», como dice Q-MI-V-10, no
    bastaría: hay que buscar por el paciente.
  - Va al diseño y toca a los lectores (IRIS y Mirth), no solo al juez.

## E-VE-1: ¿hay evidencias legítimas sin canónico?

El censo cubre la evidencia guardada: las 2.721 instancias de la regresión (2.752 mensajes) y los casos de los agentes,
separados por punto de entrada.
- **En los puntos con mapeador (adt_a01, adt_fhir y oru_fhir), con AA y fila de éxito: 0 sin canónico.** Lo traen los 2.152
  mensajes de la regresión y los 14 de los agentes.
- Los únicos AA sin canónico son de puntos de solo acuse (`adt` 2, `ord` 1), que por contrato no lo tienen (L-MT1).
- **Control:** una evidencia exacta de A1 sin canónico se cuenta con la forma de MMI-12.

**Para el diseño:** exigir el canónico cuando hay AA y fila de éxito, solo en los puntos con mapeador, no da ninguna falsa
alarma en lo guardado. La regla de parada de MMI-12 no salta.

## E-VE-2: el alcance de Q-MS-9

Se miraron los mensajes ADT distintos de A1 y de una muestra privada del sitio: 12.419 por
perfil, sin errores. Un mensaje es **incoherente** si el acuse esperado es AA tolerando PID-8 por S22 y, con evidencia
exacta, el mapeador da `valor_imposible_aceptado` en PID-8.

| Perfil | Origen | Incoherentes |
|---|---|---|
| lab | todos | 0 |
| sitio | muestra privada del sitio | 39 |

- **Entre ellos están los 3 de VER-MS-1 en MS2:** el censo reencuentra lo ya medido.
- **Controles:**
  - MSH-12 vacío con PID-8 = V en el perfil del sitio → sale la incoherencia, con `fallo_silencioso`;
  - con 2.6 escrito → no sale.
- **Los 8 de A1 con S22 en PID-8 no son incoherentes:** su versión escrita es posterior a 2.5, y el acuse y el mapeador
  leen lo mismo.

**Para el diseño:** la incoherencia solo existe con MSH-12 vacío en el perfil del sitio. Unificar la versión cambia como
mucho 39 de 12.419 veredictos, todos ahí.

## Lo que esto deja para VE0 (el encargo a Fable)

1. **MMI-12:** el canónico es obligatorio con AA y fila de éxito en los tres puntos con mapeador (adt_a01, adt_fhir y
   oru_fhir), no solo en adt_fhir. Previsión: 0 cambios en la regresión guardada.
2. **MMI-19:** el contrato del lector tiene que releer también por el paciente, y no solo por el canónico. El juez ya sabe
   juzgarlo.
3. **Q-MS-9:** una sola versión para el acuse y el mapeador. Previsión: hasta 39 cambios, todos en el perfil del sitio con
   MSH-12 vacío.
4. **Q-MI-V-9:** documentar en el contrato la representación del canónico ADT.

Fable recibe estos agregados, como recibía las medidas de MI3 y MS2, pero no los casos ni los corpus de rejuicio (Q-VE-4).

## Desviaciones (DV-VE)

- **DV-VE-1.** E-VE-4 se amplió. La foto perdida no era la regresión, así que la línea base se rehízo con todas las pruebas
  de la regresión estándar de A1b, y no con una sola.
- **DV-VE-2.** E-VE-2 se corrigió dos veces antes de contar, y las dos se vieron porque el resultado no casaba con lo
  medido en MS2:
  - el filtro descartaba una parte de la muestra, que trae el cable en la forma de la evidencia;
  - el primer control usaba una versión escrita 2.6, donde no hay incoherencia. Ese control quedó como negativo y se añadió
    el positivo, con MSH-12 vacío.

  El resultado de arriba se midió después de las dos correcciones.
- **DV-VE-3.** E-VE-1 y E-VE-3 incluyen adt_a01 y oru_fhir, que el ANTES no nombraba (solo adt_fhir).

## Estado

Nada tocado. **Siguiente: VE0**, el diseño de Fable a ciegas de los corpus de rejuicio.
