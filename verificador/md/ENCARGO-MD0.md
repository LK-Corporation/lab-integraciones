# Encargo MD0: diseño del juez de conversiones MDM_T02 (etapa 26)

Diseñas, sin programar, la ampliación de un verificador determinista HL7 v2.5 → FHIR R4 a los mensajes de documentos clínicos
**MDM_T02** (notificación de un documento original con su contenido). Hoy el verificador juzga lo que devuelve un conversor de
terceros con ADT, ORU^R01 y VXU^V04, contra un perfil «guía» sacado de la guía HL7 v2-to-FHIR. Quien lo programe será otro
modelo y seguirá tu diseño. Responde en español.

## Dónde mirar

**Lee solo dentro de esta carpeta.** No uses red, ni ssh, ni git, ni otras rutas del disco. No ejecutes nada.

| Carpeta | Qué hay |
|---|---|
| `ENCARGO-MD0.md` | este encargo |
| `resultados/ANTES-ETAPA-MDM.md` | la pregunta de la etapa, sus condiciones, sus fases y su regla de resultado. **Léelo primero** |
| `resultados/` | el ANTES del estudio de conversores y el diseño de ADT y ORU (`diseno-conversores-fable.md`, con `decisiones-qcv.md`); y el precedente más cercano, la ampliación a VXU: su ANTES, su diseño (`diseno-vx-fable.md`) y sus decisiones (`decisiones-qvx.md`) |
| `verificador/` | el código del juez: `conversion.py` (el perfil «guía», el lector del Bundle, las ocho clases y los puntos `adt_conv`, `oru_conv` y `vxu_conv`), `puntos_entrada.py`, `verificador.py`, `mcp_verificador.py`, sus pruebas (`prueba_conversion.py`), `info_verificador.json` (lo que declara) y `esquema_evidencia.json`; y la herramienta `cv/verificar_conversor.py` con sus pruebas |
| `verificador/bases_oru.py`, `verificador/bases_vxu.py` | cómo escribió el laboratorio sus corpus sintéticos de ORU y de VXU, como ejemplo |
| `estandar/` | HL7 v2.5 (capítulos 2, 2A, 3, 4, 7 y 9 en texto: **el 9 define MDM_T02 en §9.5.2 y TXA en §9.6.1, con las tablas 0270 a 0273**; el 4, ORC y OBR; el 7, OBX), FHIR R4 (los perfiles de los recursos y los ValueSet de `DocumentReference`) y la guía v2-to-FHIR: sus ConceptMap (`v2mappings/`) y sus hojas CSV (`guia_csv/`, del commit `873b331`: las del estudio y las de MDM_T02, TXA, OBX y NTE hacia `DocumentReference`, TXA y EVN hacia `Provenance`, ORC y OBR hacia `ServiceRequest`, y ED y RP) |

**No hay aquí nada de lo que devuelven los conversores**, ni sus plantillas, ni sus muestras, ni el contraste de los estudios
anteriores: el perfil tiene que salir del estándar, no de los fallos conocidos de nadie.

## Las condiciones (no se negocian)

1. **El juez no cambia para ganar casos.** Lo nuevo se añade sin tocar lo que ya juzga: **los veredictos de ADT, ORU y VXU no
   pueden cambiar.**
2. **Manda el estándar:** HL7 v2 en la versión que declara el mensaje, FHIR R4 y la guía en el commit leído. Lo que la guía
   admite es convención y no cuenta.
3. **Toda regla que cuente lleva su cita:** una fila de una hoja CSV, un ConceptMap o un apartado del estándar.
4. **Las mismas ocho clases** que cambian el significado del dato, y las mismas formas de la evidencia y del veredicto.
5. **Solo la biblioteca estándar de Python.**
6. **El corpus es sintético, en v2.5, escrito desde el estándar.** Cuidado con un riesgo medido en el laboratorio: un corpus
   hecho de mutaciones deja una firma mecánica en cada caso. Que pruebe la guía, no que persiga fallos supuestos.
7. **El contenido del documento no se juzga por lo que dice:** se juzga cómo se lleva (tipo de dato, codificación, tipo MIME,
   que llegue entero), no se decodifica ni se lee RTF o PDF.

## Qué tienes que entregar

Un documento de diseño en Markdown con:
1. **E-MD-1 completo:** por cada campo de TXA, OBX (con sus OBX-2 posibles: TX, FT, ED, RP y los demás) y NTE que llega a
   `DocumentReference`, y de PID, PV1, EVN, ORC y OBR si entran:
   - su destino;
   - su cita (la fila de la hoja y el ConceptMap);
   - qué valor espera el juez;
   - si cuenta o es nota.

   Di qué campos no tienen cita, o la tienen ambigua. En particular, TXA-2 y TXA-17 no traen mapa de vocabulario en las
   hojas: di qué espera el juez y con qué cita.
2. **Las decisiones (S-MD-n),** cada una con su porqué en una línea.
3. **El punto de entrada `mdm_conv`:**
   - qué recursos espera y cómo se emparejan con los segmentos (un `DocumentReference` por TXA con el contenido de sus OBX, el
     Patient por PID, el Encounter por PV1, los profesionales de TXA-5, TXA-9, TXA-10 y TXA-11, el `ServiceRequest` por grupo
     de orden…);
   - qué hace con lo que no cubre;
   - qué recuentos lleva.
4. **El perfil «guía» de MDM:** cada regla, con su clase de las ocho, su nivel y su cita, y las tablas de códigos que necesita
   (0270 tipo de documento, 0271 estado de compleción, 0272 confidencialidad, 0273 disponibilidad, 0191 tipo de dato
   referenciado, y su paso a los códigos de FHIR).
5. **El corpus sintético:**
   - qué bases (unas 40, como las de ORU y VXU) y qué ejercita cada una;
   - cómo se genera (`bases_mdm.py`);
   - qué variantes de OBX-2 y de contenido (texto en varias líneas, FT con formato, ED en Base64, RP), de TXA-17 y TXA-19, con
     y sin grupo de orden, y varios OBX por documento.
6. **La forma de la previsión sellada:** qué se predice por conversor antes de correr nada.
7. **Lo que cambia en la herramienta:** hoy decide el punto por MSH-9.1 (ORU → `oru_conv`, VXU → `vxu_conv`, lo demás →
   `adt_conv`). Di cómo entra MDM sin que cambie lo de ADT, ORU y VXU, y qué pasa con los eventos MDM que no son T02.
8. **Las pruebas (P-MD-n),** en rojo antes del código y con su control negativo. Entre ellas, la de que ADT, ORU y VXU no
   cambian.
9. **Las preguntas de diseño para Jev (Q-MD-D-n):** solo las que no deciden ni la pregunta ni las condiciones, cada una con
   sus opciones y qué cambia según la respuesta. Tu recomendación, **aparte**.
10. **Los límites (L-MD-n)** y **el plan** por fases (MD1, MD2), con su «hecho cuando» y su regla de parada.
