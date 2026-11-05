# Resultado de la etapa 31: las muestras públicas de los proyectos por el validador de IRIS

**De las 225 muestras públicas, IRIS da 0 por válidas, 171 por inválidas y 54 sin decidir; de las 5 nuevas que se apoyan en
muestras, 2 quedan sin ningún mensaje válido: VX-M14 y VX-M15.** Las muestras son de los dos conversores, y se validan contra
v2.5, como las lee el juez.

223 de las 225 declaran en MSH-12 una versión que no es la 2.5: 108 la 2.6, 64 la 2.8 y 44 la 2.5.1, y 7 la 2.3 o la 2.4
(CIFRAS-IVM.json, `versiones_msh12`).
- **MSH-12 queda sin decidir** cuando la versión no está en la tabla 0104 de v2.5, como en la etapa 30 (Q-MV-3). Pasa en 216
  muestras.
- **En 22 de las 54 sin decidir es lo único** (14 de la 2.5.1 y 8 de la 2.6). Si se aceptara la versión declarada, como hace
  el juez (S19), serían válidas.

Contra v2.5:
- 40 son inválidas solo por longitudes que esa versión no admite;
- 131 tienen obligatorios vacíos o fallos de estructura de v2.5.

**Las nuevas.** VX-M14 y VX-M15 tienen su apoyo del laboratorio sin decidir (UCUM), no inválido, y sus muestras son
inválidas.
- **Ninguna de las cinco se apoya solo en muestras inválidas por una regla del estándar.** Todas tienen apoyo del laboratorio.
- **Ninguna regla que invalida sus muestras toca el campo del hallazgo.** Las cinco quedan intactas, como en la 30
  (CRUCE-IVM.json, `estado`; Q-IV-D-6).
- **VX-M14 y VX-M15** llevan la salvedad en su clase (`nota_ivm`). Las clases no cambian.

La pregunta se fijó antes de mirar, en [`ANTES-ETAPA-IVMUESTRAS.md`](ANTES-ETAPA-IVMUESTRAS.md). Es la continuación de la etapa
30 ([`RESULTADO-IRISVAL.md`](RESULTADO-IRISVAL.md)), que dejó las muestras fuera.

## Cómo se hizo

1. **Las muestras:** las 225 de los repositorios públicos de los dos conversores (222 distintas), que junta
   [`ivm/corpus_ivm.py`](ivm/corpus_ivm.py): 65 del estudio de conversores, 85 de VXU y 75 de MDM.
   - El ANTES contaba 229 ficheros. Cuatro son los `MANIFIESTO.txt` de las carpetas de origen, dos de VXU y dos de MDM, que no
     son muestras.
   - No queda fuera ninguna muestra.
2. **Las cuatro decisiones nuevas, de Jev.** Las dos primeras están en
   [`ivm/decision-jev-qmv.md`](ivm/decision-jev-qmv.md), con su estado [`ivm/estado_qmv.md`](ivm/estado_qmv.md) y sus
   preguntas [`ivm/preguntas_qmv.json`](ivm/preguntas_qmv.json):
   - **Q-MV-1:** cada muestra se valida contra v2.5, como el juez, y no contra la versión que declara;
   - **Q-MV-2:** lo que no se puede leer con el texto de v2.5 va aparte y no entra en el veredicto.

   Las otras dos se preguntaron después de las revisiones a ciegas, cada una con su estado y su decisión en `ivm/`:
   - **Q-MV-3** ([`ivm/decision-jev-qmv3.md`](ivm/decision-jev-qmv3.md)): MSH-12 con una versión fuera de la 0104 de v2.5 queda
     sin decidir, como en la 30 (Q-IV-D-11b). Salió 0,56 frente a 0,44 («va aparte»), con una confianza de 0,12.
   - **Q-MV-4** ([`ivm/decision-jev-qmv4.md`](ivm/decision-jev-qmv4.md)): cuando IRIS echa en falta un segmento justo donde hay
     uno que v2.5 no define, el que sobra es ese, y se quita. Es la regla que la 30 tenía para los segmentos Z. Salió 0,87, con
     una confianza de 0,8.

   Las de la etapa 30 se heredan.
3. **El aparato es el de la 30 con la regla de Q-MV-4.** Está en [`ivm/validar_ivm.py`](ivm/validar_ivm.py), que hace
   [`ivm/hacer_validar_ivm.py`](ivm/hacer_validar_ivm.py) desde [`iv/validar_iv.py`](iv/validar_iv.py), que no cambia.
   - **Su control,** [`ivm/control_ivm.py`](ivm/control_ivm.py), da TODO BIEN ([`ivm/CONTROL-IVM.json`](ivm/CONTROL-IVM.json)).
     Es el de la 30 con un mutante más, N-V1: un ARV justo antes del PV1. Da solo el error del ARV, sin campos sin evaluar.
     Con el conductor de la 30, el mismo mutante da el error de PV1 y deja campos sin evaluar; ese control negativo también queda
     en CONTROL-IVM.json.
   - **Sobre los 723 mensajes de la 30,** el conductor nuevo da las mismas filas, byte a byte.
4. **La lectura es la de la 30 con las reglas de Q-MV-2 y Q-MV-3.** Está en [`ivm/lectura_ivm.py`](ivm/lectura_ivm.py), que
   hace [`ivm/hacer_lectura_ivm.py`](ivm/hacer_lectura_ivm.py) desde la de la 30, y en
   [`ivm/LECTURAS-IVM.json`](ivm/LECTURAS-IVM.json). Van aparte:
   - un segmento que v2.5 no define (ARV, PRT, IAR);
   - un campo que su tabla de atributos no trae;
   - una tabla que su índice no trae.
5. **La previsión** ([`ivm/PREVISION-IVM.json`](ivm/PREVISION-IVM.json), la de Jev en
   [`ivm/decision-jev-prevision-ivm.md`](ivm/decision-jev-prevision-ivm.md)) y la lectura se sellaron antes de pasar ninguna
   muestra por IRIS: [`ivm/SELLO-IVM.txt`](ivm/SELLO-IVM.txt).
6. **El cruce y las cifras:** [`ivm/cruce_ivm.py`](ivm/cruce_ivm.py) ([`ivm/CRUCE-IVM.json`](ivm/CRUCE-IVM.json),
   [`ivm/CIFRAS-IVM.json`](ivm/CIFRAS-IVM.json)). Cada nueva suma su apoyo del laboratorio (el de la 30) y el de muestras.

## Lo que dio

| Muestras | Válidas | Inválidas | Sin decidir |
|---|---|---|---|
| Del estudio de conversores (65) | 0 | 57 | 8 |
| De VXU (85) | 0 | 39 | 46 |
| De MDM (75) | 0 | 75 | 0 |
| **Total (225)** | **0** | **171** | **54** |

Por versión declarada (CIFRAS-IVM.json, `veredicto_por_version`):

| MSH-12 | Muestras | Inválidas | Sin decidir |
|---|---|---|---|
| 2.3 | 6 | 5 | 1 |
| 2.4 | 1 | 0 | 1 |
| 2.5 | 2 | 2 | 0 |
| 2.5.1 | 44 | 11 | 33 |
| 2.6 | 108 | 95 | 13 |
| 2.8 | 64 | 58 | 6 |

**Lo que las hace inválidas** (CIFRAS-IVM.json, `invalidas_por_causa`):
- **Por errores:** 658 longitudes, 390 obligatorios y 81 de estructura. Son un mínimo en las muestras con una pasada cortada o
  con campos sin evaluar (abajo).
- **Las de conversores, sobre todo de la 2.8,** pasan longitudes de v2.5 en EVN, PID, PD1, PV1 y PV2.
- **Las de VXU** dejan vacíos obligatorios de v2.5 en RXA (RXA-1, RXA-2, RXA-4, RXA-6) y en ORC-1 y OBX-11. En la 2.5.1 esos
  campos de RXA y ORC-1 también son obligatorios (V251_CH04.txt:1808 y 11163-11168).
- **Las de MDM, casi todas de la 2.6,** dejan vacíos TXA-2, TXA-12, TXA-17, OBR-4, PID-5, OBX-3 y OBX-11, y les falta EVN.

**Las 40 inválidas solo por longitud** (`longitudes_en_las_invalidas_solo_por_longitud`):
- son 31 de la 2.8, 3 de la 2.6, 3 de la 2.5.1, 2 de la 2.5 y 1 de la 2.3;
- de sus 289 errores, 165 son valores con componentes en campos a los que v2.5 da una longitud corta, como EVN-4, PID-2,
  PV1-16, PV1-36, PD1-1, PD1-17, OBX-8 y OBX-18.

El juez aplica a los mensajes de otras versiones las longitudes de v2.5 (limitación L17). El resultado no dice si caben en la
versión que declaran.

**Las 6 de la 2.3:** IRIS no marca su MSH-12, porque la 2.3 está en la 0104 de v2.5. El juez rechaza esa versión (AR 203, S19).

**Lo que queda sin decidir:**
- **MSH-12 en 216 muestras,** las de la 2.5.1, la 2.6 y la 2.8 (Q-MV-3, como en la 30). En 22 es lo único
  (`sin_decidir_solo_por_msh12`).
- **Valores fuera de la lista impresa de una tabla de HL7** (Q-IV-D-11b), sobre todo de la 0396 en PID.
- **La 0399 (país), en 26 muestras.**
  - La 0399 remite a ISO 3166, una tabla externa, y el texto pide la forma de tres letras (CH02.txt:4580-4585).
  - Como en la 30, la lectura da por buenos los valores de tres letras que ha leído (`ESP`, `USA` y `GBR`), y los demás quedan
    sin decidir: tabla externa sin leer.
  - Son `US`, `764`, `999990000`, `JP` y `44`.
- **MSH-9.3 en 40 muestras que nombran una estructura que v2.5 no tiene** (`ADT_A04`, `MDM_T06`…). Se validan con la de la
  0354, y MSH-9.3 queda sin decidir. La muestra entera queda sin decidir solo si nada más la invalida.

**Lo que va aparte:** 42 errores de segmentos que v2.5 no define, en 17 muestras: ARV en 15, PRT en 2 e IAR en 1.

## Las nuevas que se apoyan en muestras

| Nueva | Apoyo del laboratorio (etapa 30) | Muestras | Algún mensaje válido | Estado |
|---|---|---|---|---|
| L-1 | 4 válidos | 3 inválidas por otra regla (2.8 y 2.6) | sí | intacta |
| L-11 | 4 válidos | 3 inválidas por otra regla (2.6 y 2.8) | sí | intacta |
| L-22 | 1 válido | 3 inválidas por otra regla (2.8) | sí | intacta |
| VX-M14 | 1 sin decidir (UCUM) | 1 inválida (RXA-4; 2.6) | no | intacta |
| VX-M15 | 2 sin decidir (UCUM) | 6 inválidas (obligatorios de RXA, ORC-1 y OBX-11, y la longitud de MSH-10; 5 de la 2.6 y 1 de la 2.5.1) | no | intacta |

- **Las muestras de las tres del estudio de conversores** son sus ejemplos con nombre. Su apoyo está marcado como incompleto
  (Q-IV-D-7), y se apoyan también en mensajes del laboratorio válidos.
  - En dos de ellas, de la 2.8, el ARV deja ahora evaluar PV1, donde están los hallazgos de L-1 y L-22.
  - En `lfh-sample_unix` (L-1), la pasada de longitudes se cortó en MSH-2 (abajo), y sus longitudes no se leyeron.
- **VX-M14 y VX-M15** ya llevaban la `nota_iv` de la 30. Ahora llevan además la `nota_ivm` en
  [`vx/CLASES-VX3.json`](vx/CLASES-VX3.json), con [`ivm/parche_clases_ivm.py`](ivm/parche_clases_ivm.py).

## La previsión, frente a lo medido

**Acertó 5 de 10 cantidades selladas** ([`ivm/CIFRAS-IVM.json`](ivm/CIFRAS-IVM.json), clave `prevision`).

Acertaron cinco, y cuatro de ellos dicen poco:
- **Cuatro tenían un intervalo muy ancho.** Las válidas de VXU y de MDM y lo sin decidir tenían más de 50 puntos. Las nuevas sin
  ningún mensaje válido iban de 0 a 5 de 5.
- **Las nuevas sin ningún mensaje válido,** además, se previeron sabiendo por la 30 que VX-M14 y VX-M15 no tenían ninguno en el
  laboratorio.
- **El quinto acierto** es que ninguna nueva queda afectada.

Fallaron cinco:
- **La proporción de válidas, por mucho.** La previsión daba un 30 % en las de conversores, y Jev, entre el 20 y el 50 % en
  total; salió un 0 %. La previsión no contaba con cuántas de las muestras de la 2.8 pasan longitudes de v2.5. Tampoco contaba con
  que MSH-12 quedaría sin decidir: la lectura sellada lo ponía aparte.
- **La proporción de inválidas,** por la misma causa: un 76 %, frente a un máximo del 60 %.
- **Lo que va aparte:** un 7,6 %, frente a un mínimo del 20 %. MSH-12 ya no va aparte (Q-MV-3). Los campos de más que IRIS señala
  en la pasada de repeticiones no cuentan, porque esa pasada no entra en el veredicto (abajo).
- **Jev, en las nuevas:** previó ninguna sin un mensaje válido, y son dos. El estado que leyó
  ([`ivm/estado_prevision_ivm.md`](ivm/estado_prevision_ivm.md)) no decía que en la 30 VX-M14 y VX-M15 ya no tenían ningún mensaje
  válido del laboratorio.

## Lo que pasó por el camino

**Después de la primera corrida,** declarado en el sello:
- **La lectura escribía los veredictos en su mismo fichero de salida,** por una ruta heredada de la 30. Se arregló sin tocar
  ninguna regla.
- **40 muestras declaran en MSH-9.3 una estructura que v2.5 no tiene.** Con esa estructura, IRIS no valida ningún campo («no
  DocType set»), y esas muestras salían válidas sin que nadie las hubiera mirado.
  - Ahora manda la estructura de la 0354, y MSH-9.3 queda sin decidir.
  - Lo decidió quien corre la etapa, sin preguntar a Jev. Se apoya en Q-IV-D-2, que valida con las dos estructuras.
- **44 pasadas de tablas llegaron al tope de 40 vueltas.** Como pide el diseño de la 30, se subió el tope a 200 y se repitió todo.
  Ahora ninguna llega al tope.
- **Una muestra con una pasada sin leer entera no puede salir válida.** En la variante que manda
  (CIFRAS-IVM.json, `pasadas_sin_leer_en_la_variante_que_manda`):
  - 192 muestras dejan sin leer solo la pasada de repeticiones, que no entra en el veredicto (abajo). En 4 de ellas, de VXU,
    las pasadas de obligatorios, longitudes y tablas quedan además rotas (después de la tercera revisión, abajo);
  - 31 se leen enteras;
  - 2 tienen una pasada de longitudes o de estructura cortada por una forma de error que el conductor no reconoce:
    - MSH-2 con cinco caracteres en `lfh-sample_unix`, donde v2.5 define cuatro (CH02.txt:4340 y 4381);
    - un segmento obligatorio dentro de un grupo, en una de VXU.

    Las dos son inválidas por lo que se leyó antes del corte, así que su veredicto no cambia, pero sus errores son un mínimo.

  En total, 234 variantes tienen alguna pasada sin leer (`variantes_con_alguna_pasada_sin_leer`); una muestra puede tener dos.
  Casi todas son la de repeticiones, y 40 son las de MSH-9.3 sin estructura, que no mandan.
- **La búsqueda de las muestras de VXU** por su número de línea casó al principio con dos ficheros para VX-M14. Ahora el nombre
  completo va exacto, y un número suelto tiene que casar con un solo fichero.

**Las cifras de la primera corrida** (62 válidas, 135 inválidas y 28 sin decidir, y las 44 pasadas en el tope) no son el
resultado: tenían esos dos fallos. Están solo en este texto: las filas de esa corrida no se guardaron.

**Después de la segunda revisión a ciegas:**
- **MSH-12.** La lectura sellada ponía aparte MSH-12 con otra versión, por la decisión S19 del juez. Eso no se heredaba de la 30,
  que lo dejaba sin decidir (Q-IV-D-11b). Se preguntó a Jev (Q-MV-3), y queda sin decidir. Las válidas pasan de 22 a 0 y las sin
  decidir, de 32 a 54. Las inválidas no cambian.
- **La 0399.** La lectura de la 30 traía de la forma de tres letras de ISO 3166 solo `ESP`. Ahora trae también `USA` y `GBR`, que
  están en las muestras. Ninguna muestra cambia de veredicto.
- **Las cifras nuevas** (CIFRAS-IVM.json): el veredicto por versión, lo que queda sin decidir solo por MSH-12, y la forma de los
  valores de las inválidas solo por longitud.

**Después de la tercera:**
- **El ARV.** En 14 muestras de ADT de la 2.8, IRIS echaba en falta PV1 justo donde está un ARV, que v2.5 no define. El aparato
  lo tomaba como un error de estructura de PV1, que contaba. Además, en las pasadas de obligatorios, longitudes y tablas, los
  campos de detrás quedaban sin evaluar.
  - Con la regla de Q-MV-4, el ARV se quita y va aparte.
  - Se repitió la corrida: 50 s, con el tope a 200.
  - Ningún veredicto cambia. Las inválidas solo por longitud pasan de 38 a 40, los errores de longitud de 449 a 658, y las
    muestras con campos sin evaluar, de 18 a 4.
- **Las 4 con campos sin evaluar** son de VXU (`muestras_con_campos_sin_evaluar`). En ellas hay un EVN donde la estructura de
  VXU_V04 de v2.5 espera PID.
  - IRIS echa en falta PID. El aparato lo cuenta como error de estructura y cierra la estructura sin insertar nada, como en la
    30, y las pasadas de detrás quedan rotas.
  - EVN lo define v2.5, así que la regla de Q-MV-4 no lo toca.
  - Las cuatro son inválidas.
- **Los veredictos llevan dónde está cada error,** y los componentes de las longitudes se leen ahí. Antes se leían en la primera
  aparición del segmento.
- **El estado de cada nueva, como en la 30,** y la pasada de repeticiones medida (abajo).
- **La pasada de repeticiones se mide en el clon,** donde señala IRIS, como las otras pasadas. Antes se medía en el original, y en
  una muestra, con un segmento quitado delante, se contaban los campos de otro segmento. Las cifras de abajo pasan de 193 a 194 y
  de 175 a 176, con un PV1 más.
- **Los cuatro ficheros que el ANTES contaba de más** son manifiestos, no muestras (arriba).

**El tope del ANTES** («una sesión, sin agentes más allá de una revisión a ciegas») se pasó. La revisión tuvo tres lectores, el
primero y el tercero con dos pasadas.

## Lo que no dice

- **Las muestras son de otras versiones.** Validarlas contra v2.5 dice si son mensajes válidos de v2.5, que es como las lee el
  juez de los estudios: el juez las marcó «fuera de versión» cuando la diferencia venía de ahí. No dice si son válidas en su
  propia versión. El laboratorio tiene el texto de v2.5 y el de v2.5.1; ninguna regla de la 2.6 ni de la 2.8 se lee.
- **Sin decidir no es válido.** Las 22 que solo tienen MSH-12 sin decidir no son válidas de v2.5, y tampoco inválidas.
- **Las 44 muestras de la 2.5.1** se validan también contra v2.5 (Q-MV-1). Lo que la 2.5.1 cambia respecto a la 2.5 cuenta como
  error de v2.5 si el texto de v2.5 lo lee. Q-MV-2 hablaba del texto «de v2.5 o v2.5.1», pero solo se leyó con el de v2.5. El de
  la 2.5.1 se miró solo para los obligatorios de RXA y ORC-1 en VXU.
- **El veredicto de cada muestra** está en el laboratorio (`VEREDICTOS-IVM.jsonl`). Como en la 30, se publican sus agregados, el
  cruce y las cifras (Q-IV-D-10), no las filas. Las muestras están en los repositorios de sus proyectos.
- **Las muestras son de prueba:** los proyectos las escribieron para ejercitar su conversor, no como mensajes completos.
- **La pasada de repeticiones no entra en el veredicto,** como en la 30, donde no dio nada. En las muestras
  (CIFRAS-IVM.json, `pasada_de_repeticiones`):
  - en 194, IRIS dice que un segmento trae más campos de los que permite la estructura;
  - en las 194 es cierto frente a la tabla de atributos de v2.5: MSH en 158, TXA en 14, NTE en 12 y RXA en 5, entre otros;
  - en 176, alguno de esos campos de más lleva valor. Son los campos que Q-MV-2 pondría aparte, y no se cuentan en lo aparte
    porque la pasada se corta en el primero.
- **La frase del «Hecho cuando»** es la primera de este resultado.
- **Lo demás de la etapa 30 vale aquí:** IRIS es un lector, no el estándar, y la lectura la hace quien corre la etapa.
