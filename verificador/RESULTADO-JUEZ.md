# RESULTADO de la etapa 37: los dos fallos del juez de la etapa 36 (8-nov-2026)

> **El juez deja de contar mal las dos conductas de la etapa 36; en el rejuicio de lo publicado cambian 662 evidencias: 660 de
> esas dos conductas, y 2 de una lectura de NK1-15 que el juez ya hacía mal.**
>
> - **Un valor de PID-8 o NK1-15 fuera de la 0001,** que en v2.5 es una tabla de usuario: 499 evidencias.
>   - Si el conversor da un código de FHIR, es una nota de convención, que no cuenta.
>   - Si da otro, cuenta como FHIR inválido.
>   - Si rechaza el mensaje, ese valor ya no justifica el rechazo.
>
>   Cambia lo que cuenta en 195 de ellas: 83 convertidas y 112 rechazos que pasan a incorrectos. En 28 rechazos, que siguen
>   aceptables por otro valor, cambia la lista. En las otras 276 solo cambian notas: son mensajes que no son de v2.5, donde el juez
>   de antes ya lo dejaba en nota de versión.
> - **La Observation de ACC o de PDA en un ADT,** dos segmentos que la guía no mapea: 161 evidencias. Sigue contando, pero como
>   «recurso sin mapa», con el segmento por hecho y la hoja de la guía por cita, y no como «sin origen propio en el mensaje».
> - **Las 2 de la lectura** son muestras VXU de Microsoft, de v2.8. Su NK1-15 es `F^^^M`, un CWE con el código `F`, de la 0001. El
>   juez lee el campo entero, como el IS de v2.5, y no lo encuentra en la tabla: antes y después da una nota de versión, que no cuenta;
>   solo cambia su texto.
>
> Las cifras del estudio de conversores no cambian: 15 nuevas, 31 ya declaradas y 16 convenciones.

La pregunta, fijada antes de medir, está en [`ANTES-ETAPA-JUEZ.md`](ANTES-ETAPA-JUEZ.md); las dos conductas, en
[`RESULTADO-CANDIDATAS.md`](RESULTADO-CANDIDATAS.md).

## Cómo se hizo

| | |
|---|---|
| El diseño | A ciegas, por Fable, antes de escribir código: [`jz/diseno-jz-fable.md`](jz/diseno-jz-fable.md), con su encargo en [`jz/encargo-diseno-jz.md`](jz/encargo-diseno-jz.md) |
| Las decisiones abiertas | A Jev, con estados que llevan los hechos de los dos lados: cinco del arreglo ([`jz/estado_jz.md`](jz/estado_jz.md), [`jz/decision-jev-jz.md`](jz/decision-jev-jz.md)), dos de después de la primera pasada de la revisión a ciegas ([`jz/estado_jz2.md`](jz/estado_jz2.md), [`jz/decision-jev-jz2.md`](jz/decision-jev-jz2.md)) y dos de después de la segunda ([`jz/estado_jz3.md`](jz/estado_jz3.md), [`jz/decision-jev-jz3.md`](jz/decision-jev-jz3.md); Q-JZ-8 salió con confianza 0,19 y se repreguntó con dos hechos que faltaban, [`jz/estado_jz3b.md`](jz/estado_jz3b.md), [`jz/decision-jev-jz3b.md`](jz/decision-jev-jz3b.md)). Los hechos que piden se contaron sobre las evidencias con los guiones de `jz/` (`contar_conductas_jz.py`, `hechos_q_jz.py`, `pid8_ausente_jz.py`, `codigos_inventadas_jz.py` y `ver_obs_sobrantes_jz.py`) |
| Las pruebas, en rojo antes | [`jz/ROJO-JZ.txt`](jz/ROJO-JZ.txt): con el juez de antes caen 15 comprobaciones de conversión y 3 de VXU. [`jz/ROJO-JZ-2.txt`](jz/ROJO-JZ-2.txt): los controles del perfil y de la huella. [`jz/ROJO-JZ-3.txt`](jz/ROJO-JZ-3.txt): la prueba del clasificador, antes de que existiera. [`jz/ROJO-JZ-4.txt`](jz/ROJO-JZ-4.txt): su segunda versión, contra el clasificador de antes (14 caen). [`jz/ROJO-JZ-5.txt`](jz/ROJO-JZ-5.txt): P-CV-32 y la huella de la información, contra el juez de antes del tercer parche. [`jz/ROJO-JZ-6.txt`](jz/ROJO-JZ-6.txt): P-CV-32 con las entradas del texto de versión, contra el de antes del cuarto |
| El arreglo | Cuatro parches del juez ([`jz/parche_juez_jz.py`](jz/parche_juez_jz.py), [`2`](jz/parche_juez_jz2.py), [`3`](jz/parche_juez_jz3.py) y [`4`](jz/parche_juez_jz4.py)) sobre `conversion.py`, `conversion_vxu.py`, `conversion_mdm.py` y `mcp_verificador.py`; y cuatro de las pruebas ([`jz/parche_prueba_jz.py`](jz/parche_prueba_jz.py), [`2`](jz/parche_prueba_jz2.py), [`3`](jz/parche_prueba_jz3.py) y [`4`](jz/parche_prueba_jz4.py)) |
| La previsión | Sellada antes de correr el juez nuevo sobre las evidencias: [`jz/PREVISION-JZ.json`](jz/PREVISION-JZ.json), con su huella en [`jz/SELLO-JZ.txt`](jz/SELLO-JZ.txt). La contó [`jz/prever_jz.py`](jz/prever_jz.py) sobre la línea base del juez de antes, con las reglas de las decisiones |
| El rejuicio | Las 30.118 evidencias guardadas, con el juez de antes y con el nuevo. [`jz/rejuicio_jz.py`](jz/rejuicio_jz.py) pone cada diferencia en una conducta, en la lectura o «fuera» (con su prueba, [`jz/prueba_rejuicio_jz.py`](jz/prueba_rejuicio_jz.py)): [`jz/REJUICIO-JZ.json`](jz/REJUICIO-JZ.json) y [`jz/DESGLOSE-JZ.json`](jz/DESGLOSE-JZ.json). Las evidencias no van al repositorio |
| El control del rejuicio | Siete pasadas, cada una con un defecto sembrado en el juez: [`jz/CONTROL-JZ.json`](jz/CONTROL-JZ.json), y lo que cambia en cada una, [`jz/FIRMAS-CONTROL-JZ.json`](jz/FIRMAS-CONTROL-JZ.json) |
| Las clases del estudio | Con el juez de antes y con el nuevo: [`jz/CLASES-JZ-antes.json`](jz/CLASES-JZ-antes.json) y [`jz/CLASES-JZ-despues.json`](jz/CLASES-JZ-despues.json) |
| La revisión a ciegas | Un lector, en dos pasadas, que es el tope. La primera pidió cambios, con dos bloqueantes: el clasificador daba la conducta por la forma del hallazgo y no por el caso, y el desglose de la conducta 1 decía cosas falsas. La segunda aprobó, con tres menores: lo que el clasificador todavía acepta (Q-JZ-8), el texto de versión del servidor (Q-JZ-9) y dos detalles del desglose. Lo de la segunda está aplicado aquí, y el lector no lo ha visto |
| Las bases de la integración continua | Rehechas con `base_nc.sh`, un guion del laboratorio que llama a [`cv/ci/hacer_bases.py`](cv/ci/hacer_bases.py), y comprobadas contra la previsión con [`jz/comprobar_bases_jz.py`](jz/comprobar_bases_jz.py): [`jz/BASES-JZ.json`](jz/BASES-JZ.json) |

## Conducta 1: un valor de PID-8 o de NK1-15 fuera de la 0001

**Antes:**
- **En un mensaje de v2.5,** el juez lo contaba como «valor imposible convertido», fundido con «FHIR inválido» si el código no era
  de FHIR.
- **En los demás,** ya era una nota de versión (L18), que no cuenta, salvo el FHIR inválido.
- **Un rechazo del mensaje** por ese valor era aceptable.

**La base:** la 0001 de v2.5 es una tabla de usuario con valores sugeridos (Ch03.txt:5032-5044). La guía lleva PID-8 a
`Patient.gender` con su mapa de la 0001 y no dice qué hacer fuera de él. `Patient.gender` de FHIR R4 solo admite cuatro códigos.

**Ahora** (`conversion.py`, `_genero`; `conversion_vxu.py`, lo mismo para NK1-15):

| Lo que hace el conversor | El juez |
|---|---|
| Da un código de `administrative-gender` (`male`, `female`, `other` o `unknown`) | Nota de convención, que no cuenta, con la cita de la 0001. En un mensaje que no es de v2.5, nota de versión |
| Da otro código | FHIR inválido (cuenta), y nada más |
| No da `gender` | Nada (Q-JZ-5) |
| Rechaza el mensaje | El valor ya no está entre los imposibles (Q-JZ-1). Si era lo único que justificaba el rechazo, el rechazo pasa a incorrecto |

El perfil de la guía lo dice en la fila de PID-8. Una minúscula de la 0001 sigue como antes (AMB-CV-1).

**Jev:**
- **Q-JZ-1:** que PID-8 salga de los valores imposibles, 0,67 frente a 0,33, con confianza 0,34.
- **Q-JZ-5:** nada si no hay `gender`, 0,76 frente a 0,24 de una nota, con confianza 0,52.

## Conducta 2: la Observation de ACC o de PDA en un ADT

**Antes:** salía como sobrante «inventado», y el juez la contaba como «sin origen propio en el mensaje», con la cita de una hoja
de ORU. Tiene origen en el mensaje, y la hoja de ADT_A01 de la guía lista ACC y PDA sin destino.

**Ahora:**
- **Cuenta como `recurso_sin_mapa`** (Q-JZ-2), con el segmento por hecho, el dato que comparte y las citas de la hoja
  (`MSG_ADT_A01.csv:78` para ACC y `:81` para PDA) y de v2.5. Sigue contando: en el corpus no cambia ningún veredicto, solo lo que
  dice el hallazgo.
- **Cómo la reconoce** (Q-JZ-3; `conversion.py`, `_origen_sin_mapa`):
  1. si su código es el de un OBX del mensaje, es la de ese OBX;
  2. si no, por un dato igual: una fecha de un campo TS, un código de un CE o un texto de tres caracteres o más;
  3. si solo lleva valores de la 0136 (Y/N), por un campo de la 0136 del segmento que tenga ese valor.

  Lo que no casa con nada sigue como `recurso_inventado`.
- **Solo ACC y PDA** (Q-JZ-4). Los otros 16 segmentos que la hoja lista sin destino no se reconocen.
- **Con ACC y PDA en el mismo mensaje,** una Observation de solo Y/N casa con los dos por la 0136, y su hecho es `ACC/PDA`. Son
  180 de las 365 Observation del rejuicio. El juez no tiene con qué separarlas.
- **Dos riesgos de la regla,** declarados en el límite L-CV-17 (Q-JZ-6). Ninguno se da en el corpus:
  - **por la 0136,** una Observation de solo Y/N que no sale de ACC ni de PDA se da por de ellos si el mensaje trae uno con ese
    valor. Puede ser la de PD1-7, que la guía sí mapea, o una inventada. Ninguna de las 21.553 evidencias de ADT lleva PD1-7;
  - **una de ACC o PDA ya no ocupa el sitio de la de un OBX.** Si el conversor saca la de ACC y no la del OBX, el juez de antes
    la tomaba por la del OBX, que en ADT no se proyecta, y no contaba nada. El nuevo la cuenta sin mapa, y el veredicto puede pasar
    de correcto a fallo silencioso.

**Jev:**
- **Q-JZ-2:** el subtipo nuevo, 0,60 frente a 0,37 de seguir como inventado, con confianza 0,47.
- **Q-JZ-3:** por el dato o por la 0136, 0,82, con confianza 0,76. Esa opción la añadió el estado, porque las Observation de PDA de
  Microsoft solo llevan Y/N.
- **Q-JZ-4:** ACC y PDA, 0,82, con confianza 0,73.
- **Q-JZ-6:** los dos riesgos, en L-CV-17, 0,82, con confianza 0,73.

## El rejuicio

| Corpus (carpeta de las evidencias) | LinuxForHealth, conducta 1 | Microsoft, conducta 1 | Microsoft, conducta 2 |
|---|---:|---:|---:|
| Estudio de conversores y herramienta (`cv`) | 56 | 56 | 27 |
| Generadores (`ga`, etapa 33) | 68 | 68 | 108 |
| Arrastre (`ar`, etapa 21) | 66 | 33 | 24 |
| Integración continua (`ci`, `ci2` y `mant`, etapas 23 a 25) | 88 | 0 | 0 |
| MDM (`mdm`, etapa 26) | 20 | 20 | 0 |
| VXU (`vx`, etapa 20) | 11 | 11 | 1 |
| Candidatas (`ca`, etapa 36) | 1 | 1 | 1 |
| **Total** | **310** | **189** | **161** |

Y las 2 de la lectura de NK1-15, muestras VXU de Microsoft (`vx`).

- **662 diferencias en 30.118 evidencias.** Ninguna «fuera», ninguna con las dos conductas, ninguna evidencia que falte y ningún
  punto de entrada que cambie.
- **Conducta 1:**

  | Lo que había | Lo que hay | Evidencias | Conversor y versión |
  |---|---|---:|---|
  | Valor imposible convertido | Nota de convención | 30 | LinuxForHealth, 2.5 |
  | Valor imposible convertido, fundido con FHIR inválido | FHIR inválido | 53 | Microsoft, 2.5 (36) y sin MSH-12 (17) |
  | Rechazo aceptable | Rechazo incorrecto | 112 | LinuxForHealth, 2.5 (28) y 2.5.1 (84) |
  | Rechazo aceptable | Rechazo aceptable, por otro valor imposible | 28 | LinuxForHealth, sin MSH-12 |
  | Nota de versión | Nota de versión, con otro texto y la cita de la 0001 | 140 | LinuxForHealth, 2.5.1 |
  | FHIR inválido y nota de versión | FHIR inválido | 136 | Microsoft, 2.5.1 |

  Las dos últimas filas no cambian lo que cuenta. A un mensaje sin MSH-12 el juez lo toma por 2.5.
- **Conducta 2:** 89 evidencias con ACC, 12 con PDA y 60 con los dos. Ninguna Observation de esos mensajes se queda como inventada.
- **Los veredictos que cambian:**
  - 112, de correcto a rechazo incorrecto;
  - 83, de fallo silencioso con «aceptado imposible» a fallo silencioso convertido.

  El resto cambia sus hallazgos y no su veredicto.

**Cómo se pone cada diferencia en su sitio** (la segunda versión del clasificador; la primera solo miraba la forma del hallazgo, y la
revisión a ciegas lo vio):
- **Conducta 1:**
  - el valor del mensaje, su componente 1, está fuera del mapa de la guía;
  - lo que sale es valor imposible convertido, FHIR inválido o la nota de versión de antes;
  - lo que entra es FHIR inválido o una nota con la cita de la 0001;
  - en un rechazo, PID-8 estaba en la lista y su valor está fuera del mapa.
- **La lectura** (Q-JZ-7): lo mismo, pero el componente 1 está en la 0001 y el campo entero no. Solo pueden cambiar notas.
- **Conducta 2:**
  - el mensaje trae ACC o PDA;
  - las Observation que salen como inventadas son las que entran sin mapa, más las que se quedan inventadas, por su `fullUrl`;
  - cada una sin mapa nombra segmentos del mensaje, con su hecho, y el dato que cita está en ese campo del mensaje.
- **Lo que no mira** (Q-JZ-8: se dice y no se comprueba):
  - si el código de `gender` de cada nota o FHIR inválido es el del Bundle; eso lo prueban P-CV-29 y P-VX-24;
  - que un FHIR inválido no salga solo. Con las reglas de la etapa, solo sale fundido con «valor imposible convertido»;
  - que el subtipo de la nota que entra, convención o versión, case con la versión de MSH-12;
  - que la Observation sin mapa lleve el dato que cita. El clasificador no ve el Bundle.

  En los datos no pasa ninguna de las tres últimas cosas:
  - ningún FHIR inválido sale solo;
  - las notas de convención entran solo en mensajes 2.5, y las de versión solo en 2.5.1 y 2.8;
  - las 365 Observation sin mapa llevan códigos de ACC o de PDA (149 `injury-incident`, y 72 de cada uno de `death-certificate`,
    `autopsy` y `coroner`).

**El control** siembra un defecto en el juez, uno por pasada. Toda evidencia con el defecto tiene que salir «fuera»:

| Defecto sembrado | Evidencias con el defecto | Salen «fuera» |
|---|---:|---:|
| Un valor distinto en PID-5 | 23.765 | 23.765 |
| Un valor distinto en PID-8 | 23.765 | 23.765 |
| Un valor distinto en RXA-20 | 2.334 | 2.334 |
| Un FHIR inválido en un PID-8 dentro de la 0001 | 22.737 | 22.737 |
| Una nota de convención, con la cita de la 0001, en un PID-8 dentro de la 0001 | 22.737 | 22.737 |
| La Observation de un OBX, dada por de ACC con el ACC-1 del mensaje | 909 | 909 |
| La de ACC dada por de PDA, y al revés | 161 | 161 |

Qué los saca «fuera» lo dice lo que cambia en cada evidencia con el defecto ([`jz/FIRMAS-CONTROL-JZ.json`](jz/FIRMAS-CONTROL-JZ.json),
de [`jz/firmas_control_jz.py`](jz/firmas_control_jz.py)):
- **los tres primeros:** un `valor_distinto`, que no es de ninguna de las dos conductas;
- **los dos de PID-8 dentro de la 0001:** tienen la forma de la conducta 1, y salen por el valor del mensaje, que está en la tabla;
- **el de ACC y PDA cambiados:** tiene la forma de la conducta 2, y sale por el segmento y el campo que cita;
- **el de la Observation de un OBX dada por de ACC:** no tiene la forma de la conducta 2. En sus 909 evidencias desaparece además
  la nota «fuera de proyección» de la Observation del OBX, y sale por eso, no por las reglas de la conducta 2.

## Las cifras del estudio de conversores

**La frase no cambia:** 15 nuevas, 31 ya declaradas, 16 convenciones, 2 rechazos nuevos, 3 dudosas y 368 mensajes, con el juez de
antes y con el nuevo.

- **M-28** (Observation de PDA o de ACC, ya declarada) se reconocía por el hallazgo de antes, «inventado» con hecho OBX.
  - Con el juez nuevo sale «sin mapa», con el segmento por hecho. Por eso `cv/cv3_clases.py` reconoce también ese mecanismo, con el
    bloque 8 del sello de la etapa 33 (`ga/SELLO-GA.txt`).
  - Sin él, M-28 se quedaría sin casos y las ya declaradas pasarían a 30.
- **L-4 suma 4 casos de ADT,** de 92 a 96: `A1-A02-09`, `A1-A11-25`, `A1-A11-29` y `A1-A13-34`. LinuxForHealth los rechaza por el
  tipo de mensaje, y el juez de antes daba el rechazo por aceptable por su PID-8 `X` o `Z`.
- **`cv/RESULTADO-CV3.md` lleva la marca.** `cv/CLASES-CV3.json` no se toca: conserva la huella de su juez.

## Las bases de la integración continua

- **Rehechas con `base_nc.sh`, tres veces:** con el juez de antes de la revisión a ciegas, con el de después de su primera pasada y
  con el final. Entre una y otra solo cambia la huella del juez (`29cd66dc…`, `58fa0df1…` y `4a75a245…`). Lo de abajo es de la
  tercera.
- **Las corridas** ([`jz/BASES-CI-37.json`](jz/BASES-CI-37.json) y [`jz/BASES-JZ-HECHO.txt`](jz/BASES-JZ-HECHO.txt)):
  - en el juguete y en LinuxForHealth en lote, dos corridas iguales byte a byte, y la comparación «igual» contra la base;
  - mensaje a mensaje, la primera corrida está en `BASES-CI-37.json`, y la segunda, su `cmp` y su «igual», en `BASES-JZ-HECHO.txt`;
  - en el juguete, el defecto sembrado sale en los mismos 344 casos que antes.
- **Lo que cambia, frente a lo sellado** ([`jz/BASES-JZ.json`](jz/BASES-JZ.json), contra las bases de antes de la etapa):
  - en las tres, la huella del juez, de `ff9f1087…` a `4a75a245…`;
  - en el juguete, ningún caso;
  - en cada una de las de LinuxForHealth, los 6 casos previstos y nada más:
    - `A1-A02-09`, `A1-A11-25`, `A1-A11-29` y `A1-A13-34` pasan de correcto a rechazo incorrecto, con el rechazo en MSH-9;
    - `cap3-36-A04-completada` y el mínimo `M02-genero-fuera-de-tabla-caso` pierden el hallazgo de PID-8, y su subtipo pasa de
      «convertido y aceptado imposible» a «convertido».
- **La comprobación tiene su control.** Siembra cuatro defectos en cada base de LinuxForHealth y tres en el juguete, que no tiene
  casos previstos. Son un caso no previsto que cambia, uno previsto que no cambia, la huella del corpus que cambia y la del juez que
  no cambia. Cae con cada uno.
- **El proyecto de ejemplo** rehace sus dos bases en el segundo push, con el pin. Lo previsto es que no cambie ningún caso.

## La previsión

| | Previsto | Medido |
|---|---|---|
| Diferencias | 662: 501 de la conducta 1 (310 de LinuxForHealth y 191 de Microsoft) y 161 de la 2 | 662: 499 de la conducta 1 (310 y 189), 161 de la 2 y 2 de la lectura de NK1-15 |
| Rechazos | 140: 112 a incorrectos y 28 aceptables | Lo mismo |
| Fuera, con las dos, faltan, punto que cambia | 0 | 0 |
| El control | Toda evidencia con el defecto, «fuera» | Así, en las siete pasadas (la previsión hablaba de tres) |
| Nuevas, ya declaradas | 15 y 31 (con el bloque 8) | 15 y 31 |
| **Convenciones** | **17: una clave nueva, LinuxForHealth, PID-8, `S`, `X` o `Z` a `unknown`** | **16** |
| L-4 | 92 → 96 | 92 → 96 |
| Bases de la demostración | 6 casos en cada una de LinuxForHealth, ninguno en el juguete | Lo mismo, caso a caso |

- **Falló en las convenciones.** Los mensajes del estudio en los que LinuxForHealth convierte `Z` en `unknown` son de v2.5.1, y dan
  nota de versión, no de convención. Las convenciones del estudio son las notas de convención, así que no entra una clave nueva.
- **Su nota de VXU era falsa.** Decía «en VXU ninguna», y sus 501 contaban ya las 2 de la lectura de NK1-15, que no tienen un valor
  fuera de la 0001.
- **El juez del sello:** `SELLO-JZ.txt` da `f46be6dd…`, la huella de los tres ficheros del juez en d02c0c6
  (`sha256sum conversion.py conversion_vxu.py conversion_mdm.py | sha256sum`). La del servidor, que cubre más ficheros, es otra.
- **Después del sello, el juez cambió tres veces,** y ningún veredicto:
  - el segundo parche quitó un límite, L-CV-18 (`jz/parche_juez_jz2.py`, guardado a las 18:00 del 7-nov); el primer rejuicio que se
    guardó es de las 18:01;
  - el tercero amplió L-CV-17 y puso al día el texto de versión del servidor, el 8-nov, tras la primera pasada de la revisión;
  - el cuarto corrigió ese texto, que el tercero había dejado con L-CV-17 en la entrada de la etapa 14l (Q-JZ-9).

  Con cada juez, el rejuicio dio las mismas 662 diferencias.

## Lo que cambia en lo publicado

- **El juez y sus pruebas.**
  - El perfil de la guía para ADT pasa de 21 a 22 filas, con una para la Observation de un segmento sin destino.
  - Su información lleva S-CV-5 con el subtipo nuevo y el límite L-CV-17, y el texto de versión del servidor tiene una entrada de
    la etapa 37 que los nombra.
  - Cambia su huella.
- **`cv/cv3_clases.py`,** con M-28 y su mecanismo nuevo (bloque 8 del sello de la 33), y la marca en `cv/RESULTADO-CV3.md`.
- **Las tres bases de la demostración,** aquí. En un segundo push, las dos del proyecto de ejemplo y su pin.
- **Lo que no cambia:** los resultados sellados de etapas pasadas y sus JSON, que conservan la huella de su juez. En el
  laboratorio, las líneas base privadas de las pruebas que rejuzgan VXU y MDM se rehicieron con el juez nuevo, cuando el rejuicio
  había explicado cada diferencia.

## Lo que se vio de paso

- **Otro fallo del juez, fuera de la etapa.** En ADT_A01 la guía crea una Observation desde PD1-7, y el juez no la empareja con
  su campo: pasa por una de las de los OBX, por orden, y sin OBX cuenta como inventada.
  - Lo vio el diseño, y el primer arreglo lo declaraba como límite, L-CV-18. El segundo parche lo quitó.
  - Jev decidió después dejarlo aquí y no en el juez (Q-JZ-6).
  - Ninguna evidencia de ADT lleva PD1-7.
- **La lectura de NK1-15:** el juez lee el NK1-15 de v2.8, un CWE, como el IS de v2.5, con sus componentes. Da las 2 de VXU. Jev
  decidió contarlas aparte, explicadas (Q-JZ-7, 0,97, con confianza 0,96).
- **Tres clases del estudio no dan hoy los casos de su JSON publicado,** con el juez de antes y con el nuevo:
  - M-4 tenía 16 en ADT y ahora da 8;
  - M-36 tenía 1 en las muestras y ahora ninguno;
  - L-24 tenía 2 en las muestras y ahora ninguno.

  La frase es la misma. Queda fuera de la etapa.

  *Etapa 38 (8-nov):* la causa está medida en [`RESULTADO-CLASES.md`](RESULTADO-CLASES.md). En M-4, el juez de CV4 y la
  regla de `cv/cv3_clases.py`, que no reconocía su texto: 8 hallazgos sin clase, también en `jz/CLASES-JZ-*.json`. En M-36 y
  L-24, el juez de CV4. Los `jz/CLASES-JZ-*.json` se quedan como se escribieron.

## Las pruebas, en el repositorio publicado

| | Comprobaciones | Pruebas |
|---|---:|---:|
| Conversión (`prueba_conversion.py`) | 146 | 32 |
| VXU (`prueba_conversion_vxu.py`) | 158 | 24 |
| MDM (`prueba_conversion_mdm.py`) | 276 | 27 |
| El clasificador del rejuicio (`jz/prueba_rejuicio_jz.py`) | 33 | |

- **Las nuevas:**
  - P-CV-29: PID-8 fuera de la 0001;
  - P-CV-30: ACC y PDA;
  - P-CV-31: el rechazo;
  - P-CV-32: los riesgos de L-CV-17 y la entrada de la etapa 37 en el texto de versión;
  - P-VX-24: NK1-15 y el rechazo de un VXU.
- **Las que cambian:** P-CV-12 y P-CV-15, y los controles del perfil y de la huella (P-VX-20, P-MD-24 y P-MD-25).

## Cómo se repite

Desde `verificador/`:
- las pruebas: `python3 prueba_conversion.py`, `python3 prueba_conversion_vxu.py`, `python3 prueba_conversion_mdm.py` y
  `python3 jz/prueba_rejuicio_jz.py`;
- el rejuicio, con unas evidencias de la herramienta:
  - con el juez de antes, `python3 md/rejuicio_md.py linea_base <base.jsonl> <carpetas>`;
  - con el nuevo, `python3 jz/rejuicio_jz.py comparar <base.jsonl> <salida.json> <carpetas>`, y `control` con los mismos
    argumentos;
- las clases: `python3 cv/cv3_clases.py <detalle> cv/RESULTADO-CV3-minimos.json <evidencias> <salida.json>`.
