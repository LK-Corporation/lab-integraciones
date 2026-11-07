# Estado: las preguntas que deja abiertas el diseño de la versión 2 del corpus (etapa 33, 5-nov-2026)

Redactado el 5-nov-2026. **A propósito NO incluye la recomendación de nadie**, tampoco la del diseñador.

## Contexto

- **La etapa 33 arregla los generadores del corpus** en una versión 2, al lado de la 1, que no se toca. El ANTES es
  `ANTES-ETAPA-GENERADORES.md`; las decisiones de alcance están en `ga/decision-jev-ga.md` y `ga2`.
  - El arreglo de ADT cubre el tipo y la tabla de cada campo que escriben los generadores.
  - La herramienta pasa a la versión 2, y lo sellado sigue leyendo la 1.
  - Los inválidos a propósito se quedan marcados.
- **Fable diseñó la versión 2 a ciegas** (`ga/diseno-ga-fable.md`), desde el texto de v2.5 y el código de los generadores, sin ver
  conversores, juez ni resultados.
  - En GENADT, además de los obligatorios vacíos que dio la 30, encontró errores de tipo que IRIS no ve: GT1-2, UB1-2, ACC-1
    (`1` en un TS) y PV1-37 (nueve componentes en un DLD de dos).
  - Diseñó un comprobador de tipos con su tabla de mutantes.
- **Las citas del diseño que entran aquí** se han comprobado en el texto.
- Las tablas de usuario traen valores «sugeridos». El texto recomienda usarlos «where applicable», y dice que «may, however, be
  redefined locally» (CH02.txt:555-559).

## Las preguntas, con sus hechos

**P1. Valores fuera de los sugeridos de una tabla de usuario, en familias que por lo demás son válidas.** Son EVN-4 = `00` (0062)
y PL.6 = `A` (0305) en PV1-3 en las 216 bases, y PV1-14 = `A` (0023) en `completo`.
- (a) Se cambian en la versión 2 a un valor sugerido (`01`, `N`, `1`).
- (b) Se quedan, y la lista del corpus los anota como avisos conocidos.
- Hechos:
  - el alcance de Q-GA-1 dice «el tipo y la tabla de cada campo»;
  - son constantes y no tocan el azar;
  - pero no son inválidos (CH02.txt:558-559). La opción (a) cambia campos en las 144 bases de las seis familias que la 30 y el
    diseño dan por válidas, y esos campos los leen los conversores.

**P2. La disposición de PL en PV1-3, 6 y 11:** `^^ICU^001^HOSPITAL^A^B^1^`, con el punto de atención en PL.3 (cama) y el centro
en PL.5 (estado).
- (a) Se queda, porque es válida por tipo (CH02A.txt:3377-3395).
- (b) Se reescribe como `ICU^001^^HOSPITAL^^N` en las 216.
- Hechos:
  - el ejemplo del estándar pone la unidad en PL.1 y el centro en PL.4 (CH02A.txt:3413-3416);
  - PV1-3 está en todas las bases y lo convierten los dos conversores. (b) cambia ese campo en los 216 mensajes;
  - el comprobador de tipos no distingue las dos, porque no ve sentido.

**P3. `""` en un campo obligatorio.**
- (a) Aviso.
- (b) Error.
- (c) Nada, porque es un valor presente.
- Hechos:
  - «Except where noted, HL7 data fields may take on the null value» (CH02.txt:390-392);
  - el ejemplo de borrado en modo instantánea manda un DG1 con todos los campos a `""`, también DG1-1 y DG1-6, que son R
    (CH02.txt:2051-2062);
  - R es «required» (CH02.txt:464), y `""` no está en ninguna tabla ni cumple ningún formato;
  - IRIS no da por ausente un `""` en un campo R. En la 30 marcó 24 `""` como fuera de tabla, y la lectura no los contó, porque
    el nulo no es un valor de tabla (`iv/lectura_iv.py:110-115`);
  - la versión 2 no pone `""` en ningún campo R con ninguna de las tres. La pregunta decide qué dice el comprobador.

**P4. DG1-2 y PR1-2, «(B) R» en la tabla de atributos** (CH06.txt:1532, 1976).
- (a) La versión 2 los valora (`I9`, `L`), y el comprobador los trata como B: no los exige.
- (b) El comprobador los exige, como R.
- Hechos:
  - sus definiciones dicen «retained for backward compatibility only» (CH06.txt:1570-1573, 2005-2006);
  - B es «left in for backward compatibility» (CH02.txt:476-478);
  - IRIS no marcó DG1-2 ausente.

**P5. XPN.8 = `D` en PID-5 del ejemplo veterinario del capítulo 3** (cap3-36, Ch03.txt:10867), en su copia completada.
- (a) La copia mueve `D` a XPN.7, donde `D` es «Display Name» en la 0200 (CH02A.txt:6454-6459).
- (b) La copia lo deja y lo anota como error conocido.
- Hechos:
  - la 0465 (XPN.8) solo trae `A`, `I` y `P` (CH02A.txt:3761-3765);
  - el original no se toca con ninguna de las dos;
  - la copia se decidió como «completada con lo mínimo para ser válida» (Q-GA-3), no como corregida.

**P6. MSH-10 de los gemelos.**
- (a) El del original con el sufijo `-ISO`.
- (b) El mismo que el original.
- Hechos:
  - MSH-10 «uniquely identifies the message» (CH02.txt:4490-4491), y los gemelos van en el mismo corpus que sus originales;
  - con (b), el gemelo solo difiere del original en el sistema de unidades;
  - con (a), difiere además en MSH-10, que los conversores pueden copiar a la salida.

**P7. El OID de B36.** TXA-12 pasa de 36 a 23 caracteres, y TXA-13 de 42 a 29.
- (a) `DOC0036^CSSYN^2.999^ISO`, con 2.999, el arco de ejemplos de la norma de OID de la ITU (X.660). Es un dato ajeno a v2.5.
- (b) `DOC36^CSSYN^2.999.36^ISO`, que deja TXA-13 en 30 justos y rompe el patrón `DOC%04d` de las 40 bases.
- Hechos: v2.5 solo pide un OID en EI.3 con EI.4 = `ISO` (CH02A.txt:2344) y 30 caracteres en TXA-12 y TXA-13 (CH09.txt:834-835).

**P8. La longitud de un componente que pasa la de su tabla de tipo** (HD.1 de 26 caracteres en MSH-4 de cap3-37; CX.2 = `LAST`
en GT1-2 de la versión 1).
- (a) Aviso.
- (b) Error.
- Hechos:
  - «For version 2.5 and higher, the optionality, table references, and lengths of data type components are supplied in
    component tables» (CH02.txt:484-485);
  - el texto llama normativa a la longitud del campo (CH02.txt:426-427), y no dice lo mismo de la del componente;
  - la 30 contó como error la longitud del campo.

**P9. `María`, con tilde, en una base A1 con MSH-18 vacío.**
- (a) `Maria`.
- (b) Se declara MSH-18 (tabla 0211) y se deja la tilde.
- Hechos:
  - con MSH-18 vacío rige el ASCII de 7 bits (CH02.txt:4599-4602), así que la tilde es un error;
  - la familia de esa base ejercita subcomponentes del nombre, XAD.7 y XTN, no los juegos de caracteres;
  - con (b) cambia MSH-18 en esa base, que lo leen los conversores. Hay mensajes reales que mandan tildes declarando MSH-18.

**P10. Cómo elige versión la función que junta el corpus** (`generar_corpus`).
- (a) La función pasa a la versión 2 por omisión, y los llamadores sellados se cambian para pedir la 1.
- (b) La función sigue en la 1 por omisión, y la herramienta (su línea de órdenes) pide la 2.
- Hechos:
  - hay nueve llamadores con el corpus del laboratorio, además de la propia herramienta:
    - la validación de la 30 (`iv/corpus_iv.py`);
    - los controles de las etapas 18 y 21 (`cv/vc/control_vc.py`, `cv/ar/control_ar.py`);
    - dos pruebas de conversión (`prueba_conversion_vxu.py` y `prueba_conversion_mdm.py`);
    - las pruebas de la herramienta (`cv/prueba_vc.py`), que corre la CI;
    - la receta del ejemplo de la CI (`ejemplo-ci/ci/hacer_base.sh`);
  - con (a) cambian los bytes de scripts sellados, y los sellos guardan sus huellas;
  - con (b) no cambian, y lo que deba usar la 2 fuera de la herramienta tiene que pedirla.

**P11. ROL-2 (tabla 0287, de HL7), que GENADT no escribe.**
- (a) `AD` (añadir) en todos.
- (b) `UC` (sin cambios) en todos.
- (c) `AD` en A01 y A04, y `UC` en los demás eventos.
- Hechos:
  - los dos valores están en la 0287 (CH12.txt:1688-1696);
  - `UC` «is used to signify ... that this particular segment includes no information to be modified» (CH12.txt:1697-1699);
  - (c) hace que la lista de lo que cambia dependa del evento.
