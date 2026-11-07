# Estado: el alcance de la etapa 33, arreglar los generadores del corpus; segunda vez, con los hechos que faltaban (5-nov-2026)

Redactado el 5-nov-2026. **A propósito NO incluye la recomendación de nadie.**

**Por qué se pregunta otra vez:** Q-GA-2, Q-GA-5 y Q-GA-6 salieron con confianza de 0,13, 0,24 y 0,14. Al buscar qué faltaba
aparecieron los hechos de la sección 8, que el primer estado no traía. Solo se preguntan esas tres; las otras cuatro están en la
sección 9.

## Contexto

- Jev eligió la etapa 33 (`decision-jev-ruta17.md`, 0,51; confianza 0,39): arreglar los generadores del corpus para que sus
  mensajes sean válidos en v2.5 y rehacer lo que dependa de ellos.
- El autor prefiere la opción parecida a producción y la que cierra deuda. Pidió seguir en autónomo y revisa después lo
  publicado. La regla de parada global es el 20-nov (quedan 15 días).
- El cupo de agentes es compartido con el trabajo del autor. Las corridas mecánicas casi no gastan agentes; lo que gasta es
  diseñar a ciegas y revisar.

## Hechos

### 1. Los 94 que la etapa 30 dio por inválidos, por origen

- **72 son del generador de ADT** (GENADT, `bases_adt/gen_adt.py`), de las familias `completo`, `nulos` y `opcionales` (24 cada
  una).
  - Escribe cada segmento opcional con dos a cinco campos fijos, sin sus R: ROL-2, ROL-4, OBX-3, OBX-11, DG1-1, DG1-6, PR1-5,
    NK1-1, AL1-1, GT1-1 y GT1-3.
  - La familia `completo` también los deja vacíos. Ninguna familia existe para eso.
- **8 bases A1 dejan PV1-2 vacío a propósito.** Ejercitan S95, la tolerancia del perfil del sitio a PV1-2 vacío
  (`a1/gen_bases_a1.py:4`).
- **1 par mínimo** (L17) lleva PID-30 = `NO` a propósito.
- **7 son los ejemplos del capítulo 3 de v2.5** (`a1/ejemplos_cap3.json`).
  - Son fragmentos del texto del estándar: les faltan EVN, PV1 o PID, campos de MSH y, en 4, PID-5.
  - Están publicados. Ninguna de las 27 nuevas publicadas se apoya en ellos.
- **6 son de MDM:** la base B36 (`bases_mdm.py`) en T02 y en sus cinco eventos (etapa 28).
  - TXA-12 trae EI.2 a EI.4 a propósito («assigner/system») y pasa el LEN 30.
  - En T06 y T10 lo pasa también TXA-13, que la 28 forma con TXA-12 y «-PADRE».

### 2. Los 352 que la etapa 30 dejó sin decidir

- **200, por TXA-3 = `TEXT` en MDM** (Q-IV-D-12). En v2.5 no tiene arreglo:
  - TXA-3 es condicional, «required whenever the message contains content as presented in one or more OBX segments»
    (CH09.txt:888-890), y todo MDM_T02 del corpus lleva OBX;
  - su LEN es 2 (CH09.txt:825);
  - la 0191 da `TEXT` para texto «HL7 V2.3.1 and later», y `TX`, «HL7 V2.2 only» (CH09.txt:892-903).

  Con la lectura de Q-IV-D-12, ningún MDM_T02 con contenido en OBX puede ser válido en v2.5. MD-L5 y MD-M5 seguirán sin apoyo
  válido, se haga lo que se haga.
- **141, por la tabla 0396 (sistema de codificación)**, en ORU, VXU y sus pares: UCUM en OBX-6 y RXA-7, y SCT en SPM-4 y RXR-2.
  - La 0396 impresa de v2.5 no trae UCUM ni SCT. Trae ISO+, ANS+, SNM, SNM3 y los locales «99zzz» o «L» (AppendixA.txt:5681,
    5684, 5742, 5779 y 5781).
  - Q-IV-D-11 decidió que un valor fuera de la lista impresa de una tabla de HL7 queda sin decidir, porque el texto permite
    extender esas tablas (CH02.txt:563-564).
- **8, por MSH-12 = `2.5.1`** en las bases A1, a propósito (su familia 5).
- **3, por OBX-2 y OBX-11** en ORU.

### 3. Las 14 nuevas publicadas sin ningún apoyo válido (de 27)

- **12 lo están solo por la 0396, y ninguna trata de unidades:**
  - M-23 (ORU sin PID), M-24 (NM «.5») y L-18 (OBX-11 «D»): UCUM en OBX-6 de su base de ORU y de su par mínimo;
  - las nueve de VXU (VX-M7, M8, M10, M12, M14, M15, L6, L8 y L9): UCUM en RXA-7.
- **2, MD-L5 y MD-M5, por TXA-3** (hecho 2).
- **M-18 tiene 3 apoyos inválidos,** que son bases de GENADT (A02-016 a 018), y 1 válido.

### 4. Las unidades en v2.5

- **A favor de ISO+:**
  - el sistema por omisión es ISO+: «We designate this coding system as ISO+» (CH07.txt:2916-2924);
  - «We strongly encourage observation producers to use ISO+ abbreviated units exclusively» (CH07.txt:2931);
  - los corpus declaran MSH-12 = 2.5, y una base de VXU ya lleva `mL^^ISO+`.
- **En contra:**
  - el mismo pasaje «permit[s] the use of other code systems ... and locally defined codes» (CH07.txt:2931-2933);
  - UCUM es lo que espera FHIR R4 en Quantity.system, y lo que usa la guía v2-to-FHIR. También lo usan los mensajes reales de
    VXU, cuya guía de implementación es de v2.5.1;
  - cambiar el sistema cambia lo que reciben los conversores en el campo de unidades. Su salida para las unidades cambiará, y
    el juez puede dar ahí diferencias nuevas;
  - las unidades en uso son mL, mg/dL, mmol/L, 10\*3/uL, mg/L, g/dL, [drp] y Cel. Su abreviatura ISO+ hay que buscarla en el
    texto de v2.5, y la gota ([drp]) puede no tenerla.

### 5. Los tipos de dato

- **IRIS no ve los tipos de dato** ni la obligatoriedad de los componentes (RESULTADO-IRISVAL.md, «Lo que no dice»), y el
  aparato de la 30 tampoco.
- **GENADT escribe valores que no son de su tipo,** y la 30 no los marca:
  - GT1-2 es CX y lleva un nombre; GT1-3 es XPN, obligatorio, y lleva una dirección (CH06.txt:2420-2424);
  - PR1-2 es IS y lleva «PR1» (CH06.txt:1975); UB1-2 es NM y lleva «B» (CH06.txt:5778).
- **Comprobar los tipos necesita un instrumento que no existe.** En la etapa 29, para VXU y ORU, lo hicieron auditores a ciegas,
  con agentes.

### 6. Lo que lee estos corpus, y lo que costaría rehacerlo

- **La herramienta** (`cv/verificar_conversor.py`, etapa 18) usa este corpus como su corpus `lab`.
  - Si cambia, cambia su huella, y con ella las bases de `demo-ci` (unos 50 minutos por juego, `base_nc.sh`) y el pin del
    ejemplo.
- **El estudio de conversores** (14l, `cv/corpus_cv2.py`): 263 ADT, 40 ORU y sus pares mínimos.
  - Una corrida en lote de los dos conversores tarda unos 21 s (RESULTADO-ARRASTRE.md:37). El juez es el publicado.
- **VXU (etapa 20) y MDM (etapas 26 y 28),** con sus bases y sus pares.
- **El arrastre (etapa 21):** 436 casos mensaje a mensaje, unos 29 minutos.
- **La línea del circuito de IRIS y del verificador** (la etapa ADT y la 14k).
  - Son la concordancia con el oráculo congelado (`a1/concordancia_adt.py`) y el rejuicio por corpus (`ve/rejuicio.py`, A1 en
    el perfil del laboratorio y en el del sitio).
  - No se ha medido cuánto cuesta.
- **La validación de la 30** (`iv/`): minutos.
- **Los documentos publicados dicen «lo que se puede repetir con lo publicado».** Nombran los scripts que leen estos ficheros, y
  las huellas que dan (el corpus del estudio de conversores, `aa83359a…`).

### 7. Lo que se sabe del efecto

- **La 30 mostró que ninguna nueva se apoya solo en mensajes inválidos.**
- **Rellenar campos que los conversores convierten cambia su salida,** y el juez puede dar diferencias nuevas en esos segmentos.
  En ADT son ROL, NK1, AL1, DG1, PR1, GT1 y OBX.
- **GENADT usa un generador de azar con semilla.** Si los valores nuevos son fijos y no sacan números del azar, el resto de cada
  mensaje sale igual byte a byte, y cada diferencia se puede atribuir al arreglo.

### 8. Los hechos que el primer estado no traía

- **Sobre las unidades (Q-GA-2):**
  - el código v2-0396 de FHIR R4 trae ISO+ y UCUM (`estandares/fhir-r4/…/v2-0396.cs.canonical.json`);
  - ninguno de los dos conversores trae una correspondencia de ISO+ a una URL de sistema. Los dos la traen para UCUM: LinuxForHealth
    en `CodingSystemMapping.yml:291`, y Microsoft en `CodeSystem/CodeSystem.json`;
  - por eso, con (b), el sistema de la cantidad saldrá distinto en todos los mensajes de ORU y VXU con unidades, y cualquier
    diferencia que dé ahí el juez sería de todos ellos. Con (c) solo la llevarían las copias, y ninguna de las 12 trata de
    unidades;
  - con (c), los generadores de ORU y VXU no cambian en las unidades, y unos 141 mensajes de esos corpus siguen sin decidir. UCUM
    no es inválido según Q-IV-D-11, solo queda sin decidir.
- **Sobre qué se rehace (Q-GA-5):**
  - la línea del circuito de IRIS no necesita IRIS. La concordancia corre el oráculo congelado en la caja frente a
    `mapeador_adt.py`, y el rejuicio fabrica en Python la evidencia que daría el circuito (`ve/rejuicio.py:80-125`). Ninguna de
    las dos se ha cronometrado;
  - pero la concordancia exige adjudicar con cita cada desacuerdo entre el oráculo y el mapeador. Los campos nuevos de ROL, NK1,
    AL1, DG1, PR1, GT1 y OBX pueden darlos;
  - el corpus del rejuicio mezcla A1 con baterías privadas, y uno de sus dos perfiles, el del sitio, es privado. De eso solo se
    publican agregados;
  - con Q-GA-4 = «al lado», la herramienta pasa al corpus nuevo, así que la herramienta y la CI se rehacen con cualquiera de las
    tres opciones;
  - «las demás cuentas de los estudios» son, en el de conversores, las 31 ya declaradas que ve y las 16 convenciones; en VXU, las
    cuentas sobre 125 mensajes, y en MDM, las de sus 40 bases en cinco eventos.
- **Sobre los inválidos a propósito (Q-GA-6):**
  - L17 es el par mínimo de L-25, que el estudio clasificó como «no cambia el sentido»: LinuxForHealth recibe PID-30 = `NO`,
    fuera de la 0136, y da `deceasedBoolean: false` (`cv/CLASES-CV3.json`). Lo mismo, en Microsoft, es la M-35 ya declarada;
  - las 8 bases A1 con PV1-2 vacío ejercitan S95 en el perfil del sitio del verificador;
  - ver qué hace un conversor con una entrada imposible es parte de lo que mide la herramienta: tiene una clase,
    «valor_imposible_convertido» (`cv/verificar_conversor.py:54`);
  - el diseño de las bases de MDM (etapa 26) ya separó los imposibles: «los imposibles van a las pruebas P-MD, no aquí»
    (`bases_mdm.py:6`).

### 9. Lo ya decidido (primera pregunta, `ga/decision-jev-ga.md`)

- **Q-GA-1, con tipos** (0,73): el arreglo de ADT cubre también los tipos y tablas de cada campo que escriben los generadores.
- **Q-GA-3, los dos** (0,59): los 7 ejemplos del capítulo 3 se quedan como están, y se añaden copias completadas.
- **Q-GA-4, al lado** (0,92): una versión nueva del corpus junto a la vieja.
- **Q-GA-7, candidatas** (0,68): las diferencias nuevas se anotan sin confirmarlas en esta etapa.

## Las preguntas

- **Q-GA-2, las unidades de ORU y VXU** (tabla 0396):
  - (a) se quedan en UCUM;
  - (b) los generadores de ORU y VXU, y los pares mínimos de las 12, pasan a ISO+ (o a ANS+ o local, donde ISO+ no tenga la
    unidad);
  - (c) las bases se quedan en UCUM, y solo para el apoyo de las 12 se añade una copia con ISO+.
- **Q-GA-5, qué se rehace:**
  - (a) todo lo que lee estos corpus (hecho 6);
  - (b) la línea de los conversores (la herramienta y la CI, los estudios 14l, VXU y MDM, y la 30), y la del circuito de IRIS se
    declara como no rehecha;
  - (c) solo la 30, el apoyo de las 27 nuevas (si cada una se reproduce en un mensaje válido) y la herramienta con la CI; las
    demás cuentas de los estudios se declaran como no rehechas.
- **Q-GA-6, los inválidos a propósito** (8 de A1 con PV1-2 vacío y L17):
  - (a) se quedan, marcados en la lista del corpus como inválidos a propósito;
  - (b) salen a un juego aparte, fuera del corpus que se da por válido.
