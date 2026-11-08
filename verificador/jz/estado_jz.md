# Estado: las cinco decisiones del arreglo del juez (etapa 37, 7-nov-2026)

Redactado el 7-nov-2026. **A propósito NO incluye la recomendación de nadie.**

## Contexto

La etapa 37 corrige dos conductas que el juez del laboratorio cuenta mal. Las encontró la etapa 36. El ANTES está fijado
(`ANTES-ETAPA-JUEZ.md`).
- **La pregunta:** ¿puede el juez dejar de contar mal las dos conductas cambiando solo los veredictos de esas dos conductas?
- **La regla de parada:** que el rejuicio de lo publicado cambie algo fuera de las dos conductas y no se explique.

Las dos conductas:
- **(1) un valor de una tabla de usuario fuera del mapa de la guía** (PID-8 fuera de la 0001);
- **(2) un recurso que sale de un segmento que la guía no mapea** (en ADT, una Observation de ACC o de PDA en Microsoft).

Un diseño a ciegas propuso el cambio y dejó cinco decisiones abiertas. Los hechos de abajo están medidos sobre la línea base del
rejuicio: 30.118 evidencias guardadas, juzgadas con el juez de hoy. Los recuentos se pueden repetir.

## Hechos comunes

1. **La 0001 de v2.5 es una tabla de usuario con valores sugeridos** (F, M, O, U, A, N): `Ch03.txt:5034-5044`.
   - La `S` sale en un ejemplo del propio v2.5.
   - El mapa de la guía para la 0001 no trae `S`, `X` ni `Z`, y no tiene valor por omisión.
   - `Patient.gender` de FHIR R4 solo admite cuatro códigos (binding `required`).
2. **Las demás tablas de usuario:** el juez da nota de convención cuando un valor queda fuera del mapa de la guía, y no cuenta.
   - Solo la 0001 recibe trato de valor imposible.
   - Las tablas HL7 con binding `required` (0136, 0085…) no son de usuario y no cambian.
3. **La regla del estudio de conversores:** lo que el estándar permite es convención y no cuenta. Las ya declaradas son
   discrepancias que cuentan y que el proyecto sabe.
4. **El estudio y la etapa 36 tienen la conducta (2) como «ya declarada» (M-28):** cuenta, y Microsoft la declara en su salida
   esperada de `ADT-A01-01`.
   - Lo que el juez hace mal en (2) es el porqué y la cita. Dice «sin origen propio en el mensaje», cuando sí lo tiene, y cita una
     hoja de ORU.
5. **La hoja de ADT_A01 de la guía** lista ACC y PDA (y otros 16 segmentos) sin destino (`MSG_ADT_A01.csv:78, 81`). FHIR no
   prohíbe recursos de más.
6. **Las bases de la integración continua** guardan los veredictos y los hallazgos que cuentan; las notas no.
   - Cambiar el juez obliga siempre a rehacerlas.
   - Lo que cambie dentro de ellas, aparte de la huella, se comprueba caso a caso.

## Q-JZ-1. PID-8 fuera de la 0001 cuando el conversor rechaza el mensaje

**Hoy:**
- el juez da por bueno el rechazo de un mensaje con un valor «imposible» («rechazo aceptable», Q-CV-D-7);
- PID-8 fuera de la 0001 está entre esos valores imposibles, con PID-7 (una fecha mal formada) y OBX-5 (un NM que no es número);
- ninguna otra tabla de usuario lo está, así que un rechazo por un valor fuera del mapa de otra tabla de usuario es «rechazo
  incorrecto».

**Medido:**
- Hay 140 rechazos aceptables por PID-8, todos de LinuxForHealth en ADT.
  - En 112, PID-8 = `X` o `Z` es el único motivo.
  - En 28, PID-8 = `S` va con otro: falta el segmento PV1, que también hace aceptable el rechazo.
- En cada una de las dos bases de LinuxForHealth de la integración continua hay 4 de esos casos (1 `X` y 3 `Z`). En el corpus del
  estudio hay otros 4.

**Las opciones:**
- **(a) Se queda.**
  - Los 140 rechazos siguen siendo aceptables, y el cambio solo toca evidencias con Bundle.
  - Con un valor fuera del mapa, el juez admite a la vez convertirlo (convención) y rechazarlo.
  - El ANTES y la etapa 36 midieron la conducta (1) en valores convertidos; la cara de rechazo no se miró.
- **(b) Se quita** (también en VXU y MDM, que lo heredan).
  - Los 112 con `X` o `Z` pasan a «rechazo incorrecto»; los 28 con `S` siguen aceptables porque les falta PV1.
  - En cada base de LinuxForHealth cambian 4 casos más, de «correcto» a «rechazo incorrecto».
  - En el estudio, 4 evidencias de LinuxForHealth cambian de categoría. Sin rejuzgar no se sabe si mueven sus cifras o sus
    rechazos nuevos (hoy 2).
  - La 0001 queda tratada como las demás tablas de usuario.

## Q-JZ-2. El recurso de un segmento sin destino: qué es para el juez

- **(a) Cuenta, con un subtipo nuevo** (`recurso_sin_mapa`).
  - Hecho: el segmento (ACC, PDA). Texto y citas nuevos: la hoja de ADT y v2.5.
  - El rejuicio lo reconoce por el subtipo.
- **(b) Cuenta como «recurso inventado», como hoy,** pero con hecho, texto y citas nuevos.
  - No hay subtipo nuevo.
  - La palabra «inventado» queda para dos cosas: sin origen y con origen que la guía no mapea.
- **(c) Nota «fuera de proyección»** (no cuenta), como la que ya da el juez cuando un conversor saca de más algo que la guía
  proyecta.
  - La etapa 36 dijo que esa nota no le cabe, porque la guía no crea ese recurso.
  - M-28 se vacía y las ya declaradas del estudio pasan de 31 a 30. Lo dicho por el estudio y la 36 se marca como cambiado.
- **(d) Nota de convención** (no cuenta).
  - Lo mismo que (c).
  - Además, las convenciones del estudio pueden pasar de 16 a 17.

**Común a (a) y (b):**
- La clase M-28 del estudio se reconoce hoy por un mecanismo que exige hecho `OBX` y subtipo «recurso inventado»
  (`cv/juzgar_cv2.py:43`).
- Con hecho el segmento, ese mecanismo no casa. Para que M-28 conserve sus casos hace falta un bloque nuevo en `cv/cv3_clases.py`,
  bajo el sello, como el bloque 7 de la etapa 36.
- Sin ese bloque, M-28 se queda sin casos.

## Q-JZ-3. Cómo reconoce el juez que una Observation sale de un segmento sin destino

**Medido:**
- En ADT, todos los «recursos inventados» de la línea base (161 hallazgos) son Observation de Microsoft, y todos en mensajes con
  ACC o PDA. Fuera de ellos, ninguno.
- Por su código son 149 `injury-incident` (de ACC) y 216 de PDA: 72 `death-certificate`, 72 `autopsy` y 72 `coroner`.
- Las 149 de ACC llevan como fecha ACC-1, igual en las 149.
- Las de PDA solo llevan un `Y` o un `N` de la 0136 y la referencia al paciente: ningún otro dato del PDA.

**Las opciones:**
- **(a) Por un dato igual** entre la Observation y el segmento (una fecha, un código, o un texto de tres caracteres o más; los `Y`
  y `N` no valen).
  - Reconoce las 149 de ACC.
  - Las 216 de PDA siguen como «inventadas, sin origen propio»: la conducta (2) se corrige en ACC y no en PDA.
  - Una Observation de verdad inventada no se esconde.
- **(b) Por presencia:** toda Observation de más en un ADT que trae un segmento sin destino se atribuye a ese segmento.
  - Reconoce las 365.
  - Una Observation de verdad inventada, en un mensaje con un segmento sin destino, se escondería. En la línea base no hay ninguna
    así.
- **(c) Por un dato igual y, si no lo hay y el mensaje trae un solo segmento sin destino, por presencia.**
  - Casi todos los mensajes con PDA traen además otros segmentos sin destino (ACC, ARV, DB1, GT1…).
  - Con la lista de Q-JZ-4 (b), (c) da casi lo mismo que (a). Con la de Q-JZ-4 (a), reconoce las de PDA solo en los mensajes sin ACC.
- **(d) Por un dato igual y, si la Observation solo lleva un valor de la 0136 (`Y` o `N`), por un campo de la 0136 con ese mismo
  valor en un segmento sin destino del mensaje.**
  - Reconoce las 365: PDA-3, PDA-6 y PDA-9 son de la 0136, y también ACC-5 y ACC-6.
  - Para las Observation de solo `Y`/`N` se parece a (b): esconde una inventada de solo `Y`/`N` si el mensaje trae un segmento sin
    destino con ese valor.
  - Para las demás, es (a).

## Q-JZ-4. Qué segmentos sin destino reconoce el juez

**Medido:** las Observation de más en ADT salen solo de ACC y de PDA. Los otros segmentos sin destino de los mensajes (ARV, DB1,
GT1, IN2, RF1, DRG, UB1, UB2) no producen ninguna.

**Las opciones:**
- **(a) Solo ACC y PDA,** los dos de la etapa 36.
- **(b) Los 18 que la hoja de ADT_A01 lista sin destino,** cada uno con su línea de la hoja.
  - Con un dato igual, hay más ocasiones de coincidencia de texto (GT1 lleva nombres y direcciones). En la línea base no hay
    ninguna.
- **(c) Los 18 y cualquier segmento que la hoja no lista** (los Z y los de otras versiones).
  - Su legalidad en la estructura no se juzga.

## Q-JZ-5. PID-8 fuera de la 0001 cuando el conversor no da `gender`

**Hoy:**
- el juez no dice nada;
- con un valor fuera del mapa en otra tabla de usuario que el conversor no convierte, tampoco dice nada;
- PID-8 vacío se juzga como ausente.

**Medido:**
- Hay 240 evidencias con Bundle, PID-8 = `S`, `X` o `Z` y sin `gender`, todas del conversor de juguete de la integración continua
  y del conversor del proyecto de ejemplo.
- LinuxForHealth convierte a `unknown` y Microsoft copia el valor. Ni el juguete ni el ejemplo entran en el estudio.

**Las opciones:**
- **(a) Nada, como hoy.** Esas 240 no cambian.
- **(b) Nota de convención** («ausente para 'S'»).
  - Aparecen notas nuevas en las 240.
  - Las bases no cambian, porque no guardan notas, y las cifras del estudio tampoco.
