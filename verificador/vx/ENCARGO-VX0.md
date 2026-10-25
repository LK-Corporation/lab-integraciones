# Encargo VX0: diseño del juez de conversiones VXU_V04 (etapa 20)

Diseñas, sin programar, la ampliación de un verificador determinista HL7 v2.5 → FHIR R4 a los mensajes de vacunación
**VXU_V04**. Hoy el verificador juzga lo que devuelve un conversor de terceros con ADT y ORU^R01, contra un perfil «guía»
sacado de la guía HL7 v2-to-FHIR. Quien lo programe será otro modelo y seguirá tu diseño. Responde en español.

## Dónde mirar

**Lee solo dentro de esta carpeta.** No uses red, ni ssh, ni git, ni otras rutas del disco. No ejecutes nada.

| Carpeta | Qué hay |
|---|---|
| `ENCARGO-VX0.md` | este encargo |
| `resultados/ANTES-ETAPA-VXU.md` | la pregunta de la etapa, sus condiciones, sus fases y su regla de resultado. **Léelo primero** |
| `resultados/` | el ANTES del estudio de conversores, el diseño que hizo otro modelo para ADT y ORU (`diseno-conversores-fable.md`) y las decisiones que se tomaron sobre él (`decisiones-qcv.md`) |
| `verificador/` | el código del juez: `conversion.py` (el perfil «guía», el lector del Bundle, las ocho clases), `puntos_entrada.py`, `verificador.py`, `mcp_verificador.py`, sus pruebas (`prueba_conversion.py`), `info_verificador.json` (lo que declara) y `esquema_evidencia.json`; y la herramienta `cv/verificar_conversor.py` con sus pruebas |
| `verificador/bases_oru.py` | cómo escribió el laboratorio su corpus sintético de ORU, como ejemplo |
| `estandar/` | HL7 v2.5 (capítulos 2, 2A, 3, 4 y 7 en texto: **el 4 define VXU_V04 en §4.17.6 y RXA, RXR y ORC en §4.14 y §4.5**), FHIR R4 (los perfiles de los recursos que hacen falta) y la guía v2-to-FHIR: sus ConceptMap (`v2mappings/`) y sus hojas CSV (`guia_csv/`, del commit `873b331`, las mismas del estudio, más las de VXU_V04, RXA, RXR, ORC, PD1 y NK1) |

**No hay aquí nada de lo que devuelven los conversores**, ni sus plantillas, ni sus muestras, ni el contraste del estudio
anterior: el perfil tiene que salir del estándar, no de los fallos conocidos de nadie.

## Las condiciones (no se negocian)

1. **El juez no cambia para ganar casos.** Lo nuevo se añade sin tocar lo que ya juzga: **los veredictos de ADT y ORU no
   pueden cambiar.**
2. **Manda el estándar:** HL7 v2 en la versión que declara el mensaje, FHIR R4 y la guía en el commit leído. Lo que la guía
   admite es convención y no cuenta.
3. **Toda regla que cuente lleva su cita:** una fila de una hoja CSV, un ConceptMap o un apartado del estándar.
4. **Las mismas ocho clases** que cambian el significado del dato, y las mismas formas de la evidencia y del veredicto.
5. **Solo la biblioteca estándar de Python.**
6. **El corpus es sintético, en v2.5, escrito desde el estándar.** Cuidado con un riesgo medido en el laboratorio: un corpus
   hecho de mutaciones deja una firma mecánica en cada caso. Que pruebe la guía, no que persiga fallos supuestos.

## Qué tienes que entregar

Un documento de diseño en Markdown con:
1. **E-VX-1 completo:** por cada campo de RXA, RXR, ORC (y de PID, PD1 y NK1, si entran) que llega a FHIR:
   - su destino;
   - su cita (la fila de la hoja y el ConceptMap);
   - qué valor espera el juez;
   - si cuenta o es nota.

   Di qué campos no tienen cita, o la tienen ambigua.
2. **Las decisiones (S-VX-n),** cada una con su porqué en una línea.
3. **El punto de entrada `vxu_conv`:**
   - qué recursos espera y cómo se emparejan con los segmentos (una Immunization por RXA, el Patient por PID, el profesional,
     el fabricante…);
   - qué hace con lo que no cubre;
   - qué recuentos lleva.
4. **El perfil «guía» de VXU:** cada regla, con su clase de las ocho, su nivel y su cita, y las tablas de códigos que necesita
   (0322 a estado, 0162 vía, 0163 sitio, las de la vacuna).
5. **El corpus sintético:**
   - qué bases (unas 40, como las de ORU) y qué ejercita cada una;
   - cómo se genera (`bases_vxu.py`);
   - qué variantes de RXA-20, RXR, ORC, OBX y varias RXA por mensaje.
6. **La forma de la previsión sellada:** qué se predice por conversor antes de correr nada.
7. **Lo que cambia en la herramienta:** hoy decide el punto por MSH-9.1 (ORU → `oru_conv`, lo demás → `adt_conv`). Di cómo
   entra VXU sin que cambie lo de ADT y ORU.
8. **Las pruebas (P-VX-n),** en rojo antes del código y con su control negativo. Entre ellas, la de que ADT y ORU no cambian.
9. **Las preguntas de diseño para Jev (Q-VX-D-n):** solo las que no deciden ni la pregunta ni las condiciones, cada una con
   sus opciones y qué cambia según la respuesta. Tu recomendación, **aparte**.
10. **Los límites (L-VX-n)** y **el plan** por fases (VX1, VX2), con su «hecho cuando» y su regla de parada.
