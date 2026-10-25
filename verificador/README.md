# El verificador: un juez determinista para circuitos de integración HL7 v2.5 → FHIR R4

Es el juez que usan los dos estudios del agente ([`../piloto-agente/`](../piloto-agente/)), publicado con su código el
22-oct-2026. Desde el 24-oct juzga también conversores HL7 v2 → FHIR de terceros contra la guía HL7 v2-to-FHIR (desde el 25-oct, también
los mensajes de vacunación VXU^V04), y cualquiera puede pasar el suyo con un adaptador y una orden (abajo).
Recibe la evidencia de un caso:
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
- cinco de solo acuse: `adt`, `oru`, `siu`, `ord` y `mdm`;
- tres de solo transformación, `adt_conv`, `oru_conv` y `vxu_conv`: juzgan el Bundle que devuelve un conversor contra el
  perfil «guía» de [`conversion.py`](conversion.py) y, en VXU, de [`conversion_vxu.py`](conversion_vxu.py).

**Se sirve por MCP** (`mcp_verificador.py`, servidor 1.3) con seis herramientas: `verificar_caso`, `ficha_experto`,
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
| `python3 prueba_conversion.py` | `PRUEBAS CONVERSIÓN: TODO BIEN (116 comprobaciones, 28 pruebas)` |
| `python3 conversion.py --autoprueba` | `AUTOPRUEBA DE conversion: TODO BIEN` |
| `python3 cv/prueba_vc.py` | `PRUEBAS VC: TODO BIEN (152 comprobaciones, 26 pruebas)` |

Sin los perfiles privados (abajo), `prueba_adt.py` salta la prueba que depende de ellos (S95). Y la P58 del MCP espera 3
casos en vez de 6, porque el corpus de la fase 13 tampoco está aquí.

## Verifica tu conversor en un comando (etapa 18, 24-oct-2026)

**Cualquiera puede pasar su conversor HL7 v2 → FHIR R4 por el verificador** con un fichero de adaptador JSON y una orden, sin
escribir código:

```bash
python3 cv/verificar_conversor.py <adaptador.json> <carpeta de salida> --artefactos <carpeta con el conversor>
```

La herramienta hace cinco cosas:
1. corre el conversor en una caja de Docker sin red, de solo lectura, sin privilegios ni capacidades;
2. escribe una evidencia por mensaje sobre el corpus público y la juzga con el mismo juez, sin tocarlo;
3. agrega por las ocho clases que cambian el significado del dato;
4. evalúa los pares mínimos del estudio;
5. escribe `INFORME.md` e `INFORME.json`.

**Lo que no puede saber va antes de los resultados:** si el proyecto del conversor ya tenía declarada cada discrepancia. Ese
contraste lo hace una persona; hasta entonces, cada mecanismo sale como «sin_contraste».

**El control:** con los adaptadores de Microsoft y LinuxForHealth
([`cv/adaptadores/`](cv/adaptadores/)), da los mismos veredictos que el estudio en los 368 casos de cada conversor, caso por caso y con el juez final del
estudio, el de CV4: 0 diferencias. Los pares mínimos también coinciden. La comparación caso por caso se hizo en la
máquina del laboratorio, con un detalle que no es público; lo que se puede repetir desde aquí está en
[`cv/vc/CONTROL-VC.md`](cv/vc/CONTROL-VC.md).

- **Lo que se publica de la etapa:**
  - el resultado, en [`cv/VC.md`](cv/VC.md), y el control, en [`cv/vc/CONTROL-VC.md`](cv/vc/CONTROL-VC.md);
  - el diseño a ciegas, en [`cv/vc/diseno-vc-fable.md`](cv/vc/diseno-vc-fable.md);
  - las nueve decisiones de Jev, en [`cv/vc/decision-jev-qvc.md`](cv/vc/decision-jev-qvc.md);
  - la pregunta y sus condiciones, en [`ANTES-ETAPA-VERIFICA-CONVERSOR.md`](ANTES-ETAPA-VERIFICA-CONVERSOR.md);
  - dos informes de ejemplo, en [`cv/vc/ejemplos/`](cv/vc/ejemplos/).
- **Las pruebas** ([`cv/prueba_vc.py`](cv/prueba_vc.py)) corren sin Docker, con un conversor de juguete.
- **Lo que no hace:**
  - no descarga nada;
  - solo admite programas de línea de órdenes que lean y escriban ficheros;
  - solo juzga ADT de los ocho eventos y ORU^R01.

## La página del estudio (etapa 19, 25-oct-2026)

El estudio de conversores y la herramienta tienen su página web, para leerlo en el navegador:
[lk-corporation.github.io/lab-integraciones/conversores](https://lk-corporation.github.io/lab-integraciones/conversores/).
- **Qué lleva:** cada discrepancia con su registro, su cita y su par de mensajes mínimos, con el disparador marcado.
- **Cómo se comprueba:** no lleva ninguna cifra escrita a mano. La escribe `codigo/hacer_pagina_conversores.py` desde los
  ficheros de esta carpeta, y cada cifra declara su fuente en un atributo. La prueba de higiene resuelve cada fuente, busca
  cifras sueltas y comprueba que la página es la que genera el guion.
- **Dónde está el resto:** cómo se hizo y qué no hace, en [`cv/pg/PG.md`](cv/pg/PG.md).

## La etapa de VXU (20, 25-oct-2026)

> El verificador encuentra **9 discrepancias nuevas y confirmadas en VXU_V04 en 2 de 2 conversores, sobre 125 mensajes
> públicos**; además ve **26 de las ya declaradas**, y **5 diferencias son convención**.

**Lo mismo, en vacunación.**
- **Los conversores y la caja:** los mismos del estudio de conversores.
- **El punto de entrada:** `vxu_conv`, con el perfil «guía» de Immunization en [`conversion_vxu.py`](conversion_vxu.py).
- **El corpus:** 40 bases sintéticas válidas en v2.5 ([`bases_vxu.py`](bases_vxu.py), con su huella fijada) y 85 muestras de
  los proyectos.
- **El método, el mismo:**
  - el diseño a ciegas y las decisiones de Jev;
  - las pruebas en rojo antes del código;
  - la previsión sellada antes de juzgar;
  - el contraste con lo que declara cada proyecto;
  - una revisión adversaria que tumbó 1 de 23 hallazgos y corrigió el perfil;
  - un par de mensajes mínimos por discrepancia.
- **ADT y ORU no cambian:** el rejuicio de las 1.008 evidencias del estudio de conversores da 0 diferencias.

| Fase | Documentos |
|---|---|
| Antes | [`ANTES-ETAPA-VXU.md`](ANTES-ETAPA-VXU.md), [`vx/VX-PRE.md`](vx/VX-PRE.md) |
| VX0: el diseño a ciegas y las decisiones | [`vx/ENCARGO-VX0.md`](vx/ENCARGO-VX0.md), [`vx/diseno-vx-fable.md`](vx/diseno-vx-fable.md), [`vx/decisiones-qvx.md`](vx/decisiones-qvx.md), [`vx/decision-jev-qvx.md`](vx/decision-jev-qvx.md) |
| VX1: el juez, con las pruebas en rojo antes | [`vx/VX1.md`](vx/VX1.md), [`prueba_conversion_vxu.py`](prueba_conversion_vxu.py) |
| VX2: el corpus, la previsión sellada y las corridas | [`vx/prevision-vxu.json`](vx/prevision-vxu.json), [`vx/VX2.md`](vx/VX2.md) |
| VX3: contraste, clase, pares mínimos y revisión adversaria | [`vx/VX3.md`](vx/VX3.md), [`vx/CLASES-VX3.json`](vx/CLASES-VX3.json), [`vx/RESULTADO-VX3-minimos.json`](vx/RESULTADO-VX3-minimos.json), [`cv/cv3_minimos_vxu.py`](cv/cv3_minimos_vxu.py) |
| El resultado, con la frase | [`RESULTADO-VXU.md`](RESULTADO-VXU.md) |

## El arrastre de estado (21, 25-oct-2026)

> **Convertidos mensaje a mensaje, los 436 casos del estudio dan los mismos veredictos que en lote.** Lo publicado del estudio
> de conversores no cambia.

**Por qué se comprobó.** En la etapa de VXU, LinuxForHealth arrastró estado entre mensajes del mismo proceso: tras un fabricante
sin código, los mensajes siguientes salieron sin fabricante (F7 en [`vx/VX2.md`](vx/VX2.md)). El estudio de conversores lo había
corrido en lote, un proceso por carpeta.
- **El aparato:** un segundo adaptador,
  [`cv/adaptadores/linuxforhealth-mensaje.json`](cv/adaptadores/linuxforhealth-mensaje.json), con el mismo conversor y la
  misma huella y un proceso por mensaje; dos corridas de cada modo y el mismo juez.
- **Los controles, antes de mirar el resultado:** la secuencia VL11 y las 23 diferencias de F7 en el corpus VXU salen; dos
  corridas del mismo modo dan los mismos veredictos (0 diferencias en lote y 0 mensaje a mensaje).
- **El método, el de siempre:** el diseño a ciegas, las decisiones de Jev, las pruebas en rojo antes del código y la previsión
  sellada antes de correr.
- **Lo que no ve:** lo que el juez no mira (se comparan veredictos; el Bundle crudo solo sirvió para medir el ruido), un
  arrastre que coincida con un defecto propio del mensaje, otro orden del lote, un servicio de larga vida o un disparador que
  no esté en el corpus.

| Fase | Documentos |
|---|---|
| Antes | [`ANTES-ETAPA-ARRASTRE.md`](ANTES-ETAPA-ARRASTRE.md) |
| El diseño a ciegas y las decisiones | [`cv/ar/ENCARGO-AR0.md`](cv/ar/ENCARGO-AR0.md), [`cv/ar/diseno-ar-fable.md`](cv/ar/diseno-ar-fable.md), [`cv/ar/decisiones-qar.md`](cv/ar/decisiones-qar.md), [`cv/ar/estado_qar.md`](cv/ar/estado_qar.md), [`cv/ar/decision-jev-qar.md`](cv/ar/decision-jev-qar.md) |
| El código, con las pruebas en rojo antes | [`cv/ar/prueba_ar.py`](cv/ar/prueba_ar.py), [`cv/ar/arrastre.py`](cv/ar/arrastre.py), [`cv/ar/control_ar.py`](cv/ar/control_ar.py) |
| La previsión sellada | [`cv/ar/PREVISION-AR.md`](cv/ar/PREVISION-AR.md), [`cv/ar/PREVISION-AR.json`](cv/ar/PREVISION-AR.json), [`cv/ar/SELLO-AR.txt`](cv/ar/SELLO-AR.txt), [`cv/ar/estado_prevision_ar.md`](cv/ar/estado_prevision_ar.md), [`cv/ar/decision-jev-prevision-ar.md`](cv/ar/decision-jev-prevision-ar.md), [`cv/ar/prevision-cuerpo.json`](cv/ar/prevision-cuerpo.json), [`cv/ar/sellar_prevision.py`](cv/ar/sellar_prevision.py) |
| Los controles y la comparación | [`cv/ar/POSITIVO-AR.json`](cv/ar/POSITIVO-AR.json), [`cv/ar/RUIDO-AR.json`](cv/ar/RUIDO-AR.json), [`cv/ar/COMPARACION-AR.json`](cv/ar/COMPARACION-AR.json), [`cv/ar/COMPARACION-AR-primer-paso9.json`](cv/ar/COMPARACION-AR-primer-paso9.json), [`cv/ar/ADJUDICACION-AR.json`](cv/ar/ADJUDICACION-AR.json), [`cv/ar/CONTROL-AR.json`](cv/ar/CONTROL-AR.json) |
| Las cifras, con un solo juez | [`cv/ar/CIFRAS-AR.json`](cv/ar/CIFRAS-AR.json), [`cv/ar/CLASES-AR-lote.json`](cv/ar/CLASES-AR-lote.json), [`cv/ar/CLASES-AR-mensaje.json`](cv/ar/CLASES-AR-mensaje.json), [`cv/ar/minimos-AR-lote.json`](cv/ar/minimos-AR-lote.json), [`cv/ar/minimos-AR-mensaje.json`](cv/ar/minimos-AR-mensaje.json) |
| El resultado, con la frase | [`RESULTADO-ARRASTRE.md`](RESULTADO-ARRASTRE.md) |

## Las nueve de VXU en las ramas principales (22, 25-oct-2026)

> **De las 9 nuevas de VXU, siguen 9 en la rama principal de su conversor (Microsoft 6 de 6, LinuxForHealth 3 de 3); el
> arrastre de estado sigue en `master`.** Ninguna estaba reportada en su proyecto.

**Lo mismo que se hizo con las 15 de ADT y ORU** (`cv/RESULTADO-15A.md`), ahora con las de vacunación.
- **El aparato:** tres adaptadores de rama ([`cv/adaptadores/microsoft-main.json`](cv/adaptadores/microsoft-main.json),
  [`cv/adaptadores/linuxforhealth-main.json`](cv/adaptadores/linuxforhealth-main.json) y
  [`cv/adaptadores/linuxforhealth-main-mensaje.json`](cv/adaptadores/linuxforhealth-main-mensaje.json)), los pares mínimos de
  la etapa de VXU y el mismo juez. LinuxForHealth se decide mensaje a mensaje.
- **El control, antes de mirar las ramas:** con las versiones fijadas, los 26 dan exactamente lo de la etapa de VXU, y en lote
  y mensaje a mensaje lo mismo: los pares de entonces no estaban contaminados por el arrastre.
- **Las ramas:** ninguna avanzó desde el 24-oct; en los 26, la rama da lo mismo que la versión fijada.
- **El contraste:** todos los issues y PR de los dos proyectos, con sus comentarios. Dos de las nueve tienen un PR cerrado
  relacionado.
- **Los borradores de issues** quedan en la cola del autor y no se publican.

| Fase | Documentos |
|---|---|
| Antes | [`ANTES-ETAPA-RAMAS-VXU.md`](ANTES-ETAPA-RAMAS-VXU.md) |
| El diseño a ciegas y las decisiones | [`vx/rv/ENCARGO-RV0.md`](vx/rv/ENCARGO-RV0.md), [`vx/rv/diseno-rv-fable.md`](vx/rv/diseno-rv-fable.md), [`vx/rv/decisiones-qrv.md`](vx/rv/decisiones-qrv.md), [`vx/rv/estado_qrv.md`](vx/rv/estado_qrv.md), [`vx/rv/decision-jev-qrv.md`](vx/rv/decision-jev-qrv.md) |
| El código, con las pruebas en rojo antes | [`vx/rv/prueba_rv.py`](vx/rv/prueba_rv.py), [`vx/rv/ramas_vxu.py`](vx/rv/ramas_vxu.py), [`vx/rv/completar_ramas.py`](vx/rv/completar_ramas.py), [`vx/rv/decidir_contraste.py`](vx/rv/decidir_contraste.py) |
| La previsión sellada | [`vx/rv/PREVISION-RV.md`](vx/rv/PREVISION-RV.md), [`vx/rv/PREVISION-RV.json`](vx/rv/PREVISION-RV.json), [`vx/rv/SELLO-RV.txt`](vx/rv/SELLO-RV.txt), [`vx/rv/estado_prevision_rv.md`](vx/rv/estado_prevision_rv.md), [`vx/rv/decision-jev-prevision-rv.md`](vx/rv/decision-jev-prevision-rv.md), [`vx/rv/prevision-cuerpo-rv.json`](vx/rv/prevision-cuerpo-rv.json), [`vx/rv/sellar_prevision_rv.py`](vx/rv/sellar_prevision_rv.py) |
| El control, las ramas y las corridas | [`vx/rv/IDENTIDADES-RV.json`](vx/rv/IDENTIDADES-RV.json), [`vx/rv/CONTROL-RV.json`](vx/rv/CONTROL-RV.json), [`vx/rv/RAMAS-RV.json`](vx/rv/RAMAS-RV.json), [`vx/rv/RESULTADO-RV-minimos-fijada-lote.json`](vx/rv/RESULTADO-RV-minimos-fijada-lote.json), [`vx/rv/RESULTADO-RV-minimos-fijada-mensaje.json`](vx/rv/RESULTADO-RV-minimos-fijada-mensaje.json), [`vx/rv/RESULTADO-RV-minimos-main.json`](vx/rv/RESULTADO-RV-minimos-main.json), [`vx/rv/SECUENCIA-RV.json`](vx/rv/SECUENCIA-RV.json), [`vx/rv/CORRIDAS-RV.json`](vx/rv/CORRIDAS-RV.json) |
| El estado y el contraste | [`vx/rv/ESTADO-RV.json`](vx/rv/ESTADO-RV.json), [`vx/rv/CONTRASTE-RV.json`](vx/rv/CONTRASTE-RV.json) |
| El resultado, con la frase | [`RESULTADO-RAMAS-VXU.md`](RESULTADO-RAMAS-VXU.md) |

## El estudio de conversores (14l, 23-24 oct-2026)

> El verificador encuentra **15 discrepancias nuevas y confirmadas en 2 de 2 conversores, sobre 368 mensajes públicos**;
> además ve **31 de las ya declaradas**, y **16 diferencias son convención**.

**Los conversores:** Microsoft FHIR-Converter v7.0, construido desde su código, y LinuxForHealth hl7v2-fhir-converter
v1.1.0, el jar que publica en Maven Central. La rama principal de los dos se construyó después desde su código (15a). Todos
corren en una caja sin red, de solo lectura y sin privilegios.

**Lo que no es:** una certificación. Es lo que ve un juez con sus decisiones declaradas, en ADT y ORU^R01 y en esas
versiones.

**Lo esperado** sale de la guía oficial HL7 v2-to-FHIR: sus mapas, que el juez lleva generados del paquete, y sus hojas
CSV, que se citan por fila.

**Una discrepancia cuenta como nueva y confirmada** si cumple cuatro condiciones:
- tiene su cita;
- cambia el significado del dato;
- no aparece en ninguna salida esperada, prueba, documentación ni issue del proyecto;
- se reproduce con un par de mensajes mínimos: el caso y su control.

Una revisión adversaria tumbó 10 de las 25 candidatas antes de contarlas. En la rama principal de cada proyecto siguen
14 de las 15; la otra la corrigió LinuxForHealth después de la versión juzgada.

| Fase | Documento |
|---|---|
| La pregunta, «hecho cuando», el tope y la regla de portfolio, escritos antes | [`ANTES-ETAPA-CONVERSORES.md`](ANTES-ETAPA-CONVERSORES.md) |
| CV-pre: ¿coinciden los elementos del juez con la guía?, y las muestras de los proyectos | [`RESULTADO-CV-PRE.md`](RESULTADO-CV-PRE.md) |
| CV0: el diseño a ciegas, por un modelo distinto del que implementa, y las decisiones | [`cv/ENCARGO-CV0.md`](cv/ENCARGO-CV0.md), [`cv/diseno-conversores-fable.md`](cv/diseno-conversores-fable.md), [`cv/decisiones-qcv.md`](cv/decisiones-qcv.md), [`cv/decision-jev-qcv.md`](cv/decision-jev-qcv.md) |
| CV1: los conversores aislados, las pruebas en rojo y el código | [`cv/CV1.md`](cv/CV1.md) |
| CV2: la previsión sellada y el juicio | [`cv/PREVISION-CV2.md`](cv/PREVISION-CV2.md), [`cv/SELLO-CV2.txt`](cv/SELLO-CV2.txt), [`cv/RESULTADO-CV2.md`](cv/RESULTADO-CV2.md) |
| CV3: cada discrepancia frente a lo que declara el proyecto, los pares mínimos y la revisión adversaria | [`cv/RESULTADO-CV3.md`](cv/RESULTADO-CV3.md), [`cv/decision-jev-qcv-cv3.md`](cv/decision-jev-qcv-cv3.md) |
| 15a: las 15 en la rama principal de cada conversor | [`cv/RESULTADO-15A.md`](cv/RESULTADO-15A.md) |
| El resultado, con la frase | [`RESULTADO-CONVERSORES.md`](RESULTADO-CONVERSORES.md) |

Los scripts y los agregados (`.json`) están en [`cv/`](cv/).

**Para reproducirlo hacen falta cuatro cosas de fuera:**
- **Docker,** para la caja.
- **Los dos conversores:** Microsoft, construido desde su código; LinuxForHealth, su jar de Maven Central
  (`cv/lfh/pom.xml`); y sus ramas principales, desde su código. Cómo se hace está en `cv/CV1.md` y `cv/RESULTADO-15A.md`.
- **Las muestras públicas de los proyectos,** de sus repositorios.
- **El paquete `hl7.fhir.uv.v2mappings` 1.0.0,** para regenerar los mapas con `cv/extraer_mapas.py`.

**Lo que ya está aquí:**
- el corpus del laboratorio: las bases A1 y E2, y las ORU que regenera `bases_oru.py`;
- los 68 mensajes mínimos, que salen de `python3 cv/cv3_minimos.py escribir <carpeta>`.

**El arnés:** `cv/correr_conversor.py` corre un conversor sobre una carpeta, `cv/juzgar_cv2.py` juzga y `cv/cv3_clases.py`
clasifica.

## La etapa del verificador (14k, 22-oct-2026): cerrar los huecos medidos del juez

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
- **Por eso la huella del juez publicado es otra.** El fichero entra en la huella, así que la del juez publicado es `0dd3ae5c…`
  y la del laboratorio `40bbc3ef…`. Las dos están en el manifiesto, con la huella del original. Los otros 14 ficheros de la
  huella son idénticos.
- **`adjudicacion.py` es un extracto.** Solo lleva `cable()`, la única función que usa el juez. El módulo entero es de la fase
  13 y lleva material de la clave del banco. No entra en la huella.
- **Siete documentos de la etapa llevan una parte redactada:** seis `.md`, marcados en su primera línea, y
  `ve/ADJUDICACION-VE2.json`. Los totales y el mecanismo son los del original.
- **Cuatro documentos del estudio de conversores llevan una parte redactada,** marcados en su primera línea: se quitaron
  las alusiones al trabajo del autor y la cola de lo que solo él decide.
- **Dos documentos de la etapa de VXU llevan una parte redactada,** marcados en su primera línea: `ANTES-ETAPA-VXU.md` y
  `RESULTADO-VXU.md`.
- **Tres documentos de la etapa del arrastre llevan una parte redactada,** marcados en su primera línea:
  `ANTES-ETAPA-ARRASTRE.md`, `cv/ar/ENCARGO-AR0.md` y `cv/ar/diseno-ar-fable.md`. Y `cv/ar/CONTROL-AR.json` va sin la ruta
  de los artefactos ni el commit del sello, como dice su `_nota`.
- **Tres documentos de la etapa de las ramas llevan una parte redactada,** marcados en su primera línea:
  `ANTES-ETAPA-RAMAS-VXU.md`, `vx/rv/ENCARGO-RV0.md` y `vx/rv/diseno-rv-fable.md`.
- **El juez publicado no lleva el corte C19 del laboratorio.** Es una línea de trabajo aparte, que pasa a tablas de datos la
  decisión del acuse y la disposición, equivalente byte a byte. `verificador.py` y `acuse_referencia.py` van como en la
  publicación anterior. La cabecera de `MANIFIESTO.txt` da las dos huellas.
- **Las bases ORU no viajan.** Las regenera `bases_oru.py`; se comprobó que salen iguales byte a byte.
- **Los mensajes mínimos de conversores tampoco.** Los regenera `cv/cv3_minimos.py escribir <carpeta>`; se comprobó que
  salen iguales byte a byte.
- **Las bases y los pares mínimos de VXU tampoco.**
  - Las bases las escribe `bases_vxu.py`, y su autoprueba comprueba la huella del conjunto.
  - Los pares, `cv/cv3_minimos_vxu.py escribir <carpeta>`, y su secuencia, `secuencias <carpeta>`.

## Lo que no está

- **Los perfiles privados.** El código los busca en `../privado/perfiles` (o donde diga `LAB_PERFILES`); sin ellos juzga
  con el perfil del laboratorio.
- **Los circuitos y sus lectores:** las clases de IRIS, los canales de Mirth y los programas que sacan la evidencia de cada
  motor.
- **Los corpus de los rejuicios y la evidencia guardada.** De VE2 están las tablas agregadas, no los casos.
- **De conversores:**
  - los conversores: se obtienen como dicen `cv/CV1.md` y `cv/RESULTADO-15A.md`;
  - los resultados intermedios y los scripts de una sola fase que los documentos citan: `cv/CV-PRE-E1.json`,
    `cv/CV-PRE-E2.json`, `cv/RESULTADO-CV2-pasada0.json`, `cv/RESULTADO-CV3-rejuicio1.json` y `-rejuicio2.json`,
    `cv/RESULTADO-CV4-rejuicio.json`, `cv/RESULTADO-15A-minimos-fijada.json`, `cv/preguntas_qcv.json`, `cv/parche_cv1.py`,
    `cv/cv1d.py`, `ve/comprobar.sh`, `prueba_multitipo.py` y la guarda de publicación que importa `cv/caja_cv0.py`;
  - lo que devolvieron y el detalle por caso: están los agregados de `cv/`;
  - las hojas CSV de la guía, que están en `HL7/v2-to-fhir`, commit `873b331`;
  - las muestras de los proyectos, que están en sus repositorios.
- **De VXU:**
  - las evidencias y los juicios por caso: están los agregados de `vx/`;
  - las muestras de los proyectos, en sus repositorios. Las de LinuxForHealth son literales de sus pruebas Java;
  - las hojas CSV de la guía que trae `vx/traer_guia_vxu.py`;
  - los parches con que se aplicó cada cambio en el laboratorio;
  - `prueba_multitipo.py`.
- **Del arrastre:**
  - los juicios, las evidencias y los Bundles de las cuatro corridas: están los agregados de `cv/ar/`;
  - los scripts de una sola vez: el parche del conversor de juguete y el que trajo los resultados.
- **De las ramas de VXU:**
  - los borradores de issues, que son del autor y hablan en su nombre;
  - el volcado de issues y comentarios de los proyectos, que está en sus repositorios;
  - los artefactos de las ramas, las evidencias y los juicios por caso: están los agregados de `vx/rv/`;
  - el script que trajo los resultados.
- **Los documentos de las etapas anteriores.** Los de esta etapa los citan (`RESULTADO-A1.md`, `RESULTADO-MIRTH.md`…), como
  citan rutas del repositorio de trabajo (`privado/…`) que no están aquí.

El material de HL7 que sí está, y qué licencia lo cubre, se explica en [`../LICENSE.md`](../LICENSE.md).
