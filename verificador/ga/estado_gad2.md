# Estado: tres preguntas del diseño de la versión 2 del corpus, otra vez, con los hechos que faltaban (etapa 33, 5-nov-2026)

Redactado el 5-nov-2026. **A propósito NO incluye la recomendación de nadie**, tampoco la del diseñador.

**Por qué se pregunta otra vez:** P2, P6 y P11 (`ga/decision-jev-gad.md`) salieron con confianza de 0,26, 0,28 y 0,13; P11 empató
entre dos opciones. Al buscar qué faltaba aparecieron los hechos marcados con **(nuevo)**. Solo se preguntan esas tres.

## Contexto

- **La etapa 33 arregla los generadores del corpus** en una versión 2, al lado de la 1, que no se toca.
  - El arreglo de ADT cubre el tipo y la tabla de cada campo que escriben los generadores.
  - La herramienta pasa a la versión 2.
  - Lo publicado de la línea de los conversores se rehace comparando, caso a caso, la versión 1 con la 2.
- **Fable diseñó la versión 2 a ciegas** (`ga/diseno-ga-fable.md`).
- **Lo ya decidido de sus preguntas** (`ga/decision-jev-gad.md`):
  - los valores válidos pero fuera de los sugeridos de una tabla de usuario, en familias que por lo demás son válidas, se quedan
    y se anotan (P1, 0,72);
  - `""` en un campo R es error para el comprobador (P3, 0,53);
  - DG1-2 y PR1-2, como B (P4, 0,68);
  - la copia del ejemplo veterinario deja XPN.8 y lo anota (P5, 0,77);
  - el OID de B36 es 2.999 (P7, 0,68);
  - la longitud de componente da aviso (P8, 0,78);
  - `Maria` sin tilde (P9, 0,65);
  - la herramienta pide la versión 2, y la función sigue en la 1 por omisión (P10, 0,97).

## Las preguntas, con sus hechos

**P2. La disposición de PL en PV1-3, 6 y 11:** `^^ICU^001^HOSPITAL^A^B^1^`, con el punto de atención en PL.3 (cama) y el centro
en PL.5 (estado).
- (a) Se queda, porque es válida por tipo (CH02A.txt:3377-3395).
- (b) Se reescribe como `ICU^001^^HOSPITAL^^N` en las 216.
- Hechos:
  - el ejemplo del estándar pone la unidad en PL.1 y el centro en PL.4 (CH02A.txt:3413-3416);
  - PV1-3 está en todas las bases y lo convierten los dos conversores, así que (b) cambia ese campo en los 216 mensajes;
  - el comprobador de tipos no distingue las dos, porque no ve sentido;
  - **(nuevo)** con P1 ya decidido, los campos válidos de las familias válidas no cambian. Con (b), las 144 bases de esas
    familias cambiarían en PV1-3, y la comparación entre las dos versiones tendría ese cambio en todos los casos de ADT;
  - **(nuevo)** las bases guardan en `colocado` los campos que ponen a propósito, PV1-3 entre ellos. Ese campo solo lo escribe
    el generador; ningún script del laboratorio lo lee.

**P6. MSH-10 de los gemelos.**
- (a) El del original con el sufijo `-ISO`.
- (b) El mismo que el original.
- Hechos:
  - MSH-10 «uniquely identifies the message» (CH02.txt:4490-4491);
  - con (b), el gemelo solo difiere del original en el sistema de unidades. Con (a), difiere además en MSH-10, que los
    conversores pueden copiar a la salida;
  - **(nuevo)** ni la herramienta ni el juez de conversiones usan MSH-10. La herramienta nombra cada caso por su fichero;
  - **(nuevo)** según el diseño, los gemelos van en un corpus propio («gemelos») de la misma corrida que sus originales. Con (b),
    la corrida llevaría dos mensajes con el mismo MSH-10;
  - **(nuevo)** LinuxForHealth arrastra estado entre mensajes cuando corre en lote (etapa 20). La etapa 21 midió que ese arrastre
    no cambia ningún veredicto en 436 casos, pero no midió MSH-10 repetidos.

**P11. ROL-2 (tabla 0287, de HL7), que GENADT no escribe.** ROL va en A01, A02, A03, A04, A08, A13 y A31.
- (a) `AD` (añadir) en todos.
- (b) `UC` (sin cambios) en todos.
- (c) `AD` en A01 y A04, y `UC` en los demás eventos.
- (d) `AD` en A01 y A04, y `UP` (actualizar) en los demás eventos.
- Hechos:
  - `AD`, `UC` y `UP` están en la 0287 (CH12.txt:1688-1696);
  - `UC` «is used to signify ... that this particular segment includes no information to be modified» (CH12.txt:1697-1699);
  - ROL-2 «reveals the intent of the message» (CH15.txt:1592-1593);
  - **(nuevo)** la única indicación del capítulo 3 sobre ROL-2 es para A54 (cambio de médico responsable): «Use "UP" in ROL-2»
    (Ch03.txt:3822-3825). Ninguno de los eventos del corpus es A54;
  - con (c) y (d), la lista de lo que cambia depende del evento.
