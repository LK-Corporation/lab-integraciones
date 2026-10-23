# El verificador: un juez determinista para circuitos de integración HL7 v2.5 → FHIR R4

Es el juez que usan los dos estudios del agente ([`../piloto-agente/`](../piloto-agente/)), publicado con su código el
22-oct-2026. Recibe la evidencia de un caso:
- el mensaje HL7 v2.5 que se envió;
- el acuse que devolvió el circuito;
- lo que el circuito dejó: su registro, el canónico y lo que escribió en FHIR.

Con eso dice si el circuito hizo lo que manda el estándar. No usa ningún modelo, solo la biblioteca estándar de Python, y da
siempre la misma respuesta a la misma evidencia.

**Lo que devuelve**, en tres niveles:
- **N3, el veredicto:** `correcto`, `fallo_silencioso`, `acuse_incorrecto`, `ambos`, `fallo_entorno`, `indeterminado` o
  `sin_intercambio`.
- **N2, los hallazgos que lo sostienen:** cada uno con su cita al estándar o a una decisión declarada (`S-n`).
- **N1, las notas:** lo que no cambia el veredicto pero conviene leer, con sus límites declarados (`L-n`).

**Los puntos de entrada:**
- tres con mapeador: `adt_a01`, `adt_fhir` y `oru_fhir`, donde se compara también lo escrito;
- cinco de solo acuse: `adt`, `oru`, `siu`, `ord` y `mdm`.

**Se sirve por MCP** (`mcp_verificador.py`, servidor 1.1) con seis herramientas: `verificar_caso`, `ficha_experto`,
`acuse_esperado`, `comparar_canonico`, `consultar_tabla` e `info_verificador`. La última lleva las decisiones declaradas, los
supuestos, los límites, las desviaciones y las preguntas que siguen abiertas.

## Correrlo

Hace falta Python 3 (se probó con 3.12) y nada más. Desde esta carpeta:

```bash
python3 bases_oru.py
```

Escribe las 40 bases ORU sintéticas que usa `prueba_oru.py`, en `bases_oru/` y `bases_oru.jsonl`. Después, cada una de estas
debe terminar en verde:

| Orden | Termina con |
|---|---|
| `python3 prueba_verificador.py` | `AUTOPRUEBA DEL VERIFICADOR: TODO BIEN` |
| `python3 mcp_verificador.py --autoprueba` | `AUTOPRUEBA DE mcp_verificador: TODO BIEN` |
| `python3 prueba_adt.py` | `TODO BIEN (26 comprobaciones)` |
| `python3 prueba_oru.py` | `TODO BIEN (696 comprobaciones)` |
| `python3 mapeador_adt.py --autoprueba` | `AUTOPRUEBA OK 84` |
| `python3 almacen_adt.py --autoprueba` | `TODO BIEN (18 comprobaciones)` |
| `python3 almacen_oru.py --autoprueba` | `TODO BIEN (345 comprobaciones)` |
| `python3 acuse_referencia.py --autoprueba` | `AUTOPRUEBA DE acuse_referencia: TODO BIEN` |
| `python3 contratos/generar_contrato.py --comprobar` | `contrato_canonico_adt.md: IGUAL a la generación` |
| `python3 ve/prueba_ve.py` | `PRUEBAS VE (despues): TODO BIEN (21 pruebas, 7 controles)` |

Sin los perfiles privados (abajo), `prueba_adt.py` salta la prueba que depende de ellos (S95). Y la P58 del MCP espera 3
casos en vez de 6, porque el corpus de la fase 13 tampoco está aquí.

## La última etapa (14k, 22-oct-2026): cerrar los huecos medidos del juez

La etapa de Mirth había dejado medidos dos puntos ciegos del juez. Con fallos sembrados en el circuito, uno mordía 128 veces
sin que el juez cazara ninguna, y el otro 14. Quedaban además una contradicción con la versión de HL7 y un contrato del canónico
que no documentaba su representación. La etapa los cierra:
- **Un AA sin canónico ya no pasa por bueno (S104).** Con AA y una fila de éxito en el registro, que falte el canónico es
  `fallo_silencioso` en los tres puntos con mapeador. Así se cazan las 136 entradas de A1 sin canónico.
- **La relectura del FHIR va también por paciente (S106).** Los lectores releían solo por el canónico. Ahora releen por los
  identificadores del mensaje y por el paciente, con una ventana de `_lastUpdated`, porque el FHIR de IRIS no admite
  `subject:identifier`. Se cazan los 13 casos de A1.
- **El acuse y los mapeadores leen la misma versión, la escrita en MSH-12 (S105).**
- **El contrato del canónico ADT sale del código que lee el juez (S107):** [`contratos/contrato_canonico_adt.md`](contratos/contrato_canonico_adt.md),
  77 campos con su valor y su cita.

**Rejuicio de los 17.368 casos guardados con el juez nuevo:** 0 fuera de lo previsto tras la adjudicación, y 3 con la previsión
sellada, los tres de la previsión. El resultado: [`RESULTADO-ETAPA-VERIFICADOR.md`](RESULTADO-ETAPA-VERIFICADOR.md).

| Fase | Documento |
|---|---|
| El alcance, «hecho cuando» y topes | [`ANTES-ETAPA-VERIFICADOR.md`](ANTES-ETAPA-VERIFICADOR.md) |
| VE-pre: la línea base rehecha y el primer punto ciego reproducido | [`RESULTADO-VE-PRE.md`](RESULTADO-VE-PRE.md) |
| VE0: el diseño, a ciegas, por un modelo distinto del que implementa, y las decisiones | [`ve/diseno-verificador-ve-fable.md`](ve/diseno-verificador-ve-fable.md), [`ve/decisiones-qve.md`](ve/decisiones-qve.md), [`ve/decision-jev-qve.md`](ve/decision-jev-qve.md) |
| VE1: sondas, pruebas en rojo, código y comprobación en vivo | [`ve/SONDAS-VE1A.md`](ve/SONDAS-VE1A.md), [`ve/PRUEBAS-VE1B.md`](ve/PRUEBAS-VE1B.md), [`ve/CODIGO-VE1C.md`](ve/CODIGO-VE1C.md), [`ve/VIVO-VE1D.md`](ve/VIVO-VE1D.md) |
| VE2: la previsión sellada, el rejuicio y su adjudicación | [`ve/PREVISION-VE2.md`](ve/PREVISION-VE2.md), [`ve/RESULTADO-VE2.md`](ve/RESULTADO-VE2.md), y sus `.json` en [`ve/`](ve/) |
| El resultado | [`RESULTADO-ETAPA-VERIFICADOR.md`](RESULTADO-ETAPA-VERIFICADOR.md) |

## En qué difiere de la copia del laboratorio

Todo lo de esta carpeta es **byte a byte** lo del repositorio de trabajo, salvo lo que dice esta lista y salvo este README y
[`MANIFIESTO.txt`](MANIFIESTO.txt), que son de la publicación. El manifiesto lleva la huella de cada fichero tal como se
publica.
- **`medida/encargo_medida.md` es un extracto.** En el laboratorio, ese fichero es un encargo de la fase 13 que lleva el
  capítulo 2 de HL7 v2.5 entero, y su texto no se puede redistribuir. Aquí solo quedan las filas de las tres tablas que el juez
  lee de él (0003, 0004 y 0211). Se comprobó que el juez lee del extracto exactamente las mismas: 285, 9 y 21 valores.
- **Por eso la huella del juez publicado es otra.** El fichero entra en la huella, así que la del juez publicado es `a2ee87fd…`
  y la del laboratorio `b9788fab…`. Las dos están en el manifiesto, con la huella del original. Los otros 13 ficheros de la
  huella son idénticos.
- **`adjudicacion.py` es un extracto.** Solo lleva `cable()`, la única función que usa el juez. El módulo entero es de la fase
  13 y lleva material de la clave del banco. No entra en la huella.
- **Siete documentos de la etapa llevan una parte redactada:** seis `.md`, marcados en su primera línea, y
  `ve/ADJUDICACION-VE2.json`. Los totales y el mecanismo son los del original.
- **Las bases ORU no viajan.** Las regenera `bases_oru.py`; se comprobó que salen iguales byte a byte.

## Lo que no está

- **Los perfiles privados.** El código los busca en `../privado/perfiles` (o donde diga `LAB_PERFILES`); sin ellos juzga
  con el perfil del laboratorio.
- **Los circuitos y sus lectores:** las clases de IRIS, los canales de Mirth y los programas que sacan la evidencia de cada
  motor.
- **Los corpus de los rejuicios y la evidencia guardada.** De VE2 están las tablas agregadas, no los casos.
- **Los documentos de las etapas anteriores.** Los de esta etapa los citan (`RESULTADO-A1.md`, `RESULTADO-MIRTH.md`…), como
  citan rutas del repositorio de trabajo (`privado/…`) que no están aquí.

El material de HL7 que sí está, y qué licencia lo cubre, se explica en [`../LICENSE.md`](../LICENSE.md).
