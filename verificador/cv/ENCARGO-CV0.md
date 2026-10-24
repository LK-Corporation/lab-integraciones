# Encargo CV0: el verificador ante conversores HL7 v2 → FHIR de terceros (etapa 14l)

Eres el diseñador, como en tus diseños anteriores del verificador: ADT, ORU y la etapa 14k
(`resultados/diseno-adt-fable.md`, `resultados/diseno-oru-fable.md`, `resultados/diseno-verificador-ve-fable.md`). Otro
(Claude) implementará tu diseño tal cual. Declarará cada desviación (DV-CV-n) y escribirá la previsión **antes** de juzgar
ningún conversor.

## Reglas de trabajo

- **Lee solo dentro de esta carpeta.** No uses red, ni ssh, ni git, ni otras rutas del disco. No ejecutes nada.
- **Estás a ciegas de lo que devuelven los conversores, a propósito.** No tienes sus plantillas, ni sus salidas, ni sus
  salidas esperadas, ni sus issues. No intentes reconstruirlos ni recordarlos: el perfil se diseña desde el estándar, no para
  casar con lo que hace un conversor concreto.
- **Manda el estándar:**
  - HL7 v2 en la versión que declara el mensaje (aquí tienes v2.5: caps. 2, 2A, 3 y 7);
  - FHIR R4: las definiciones de Bundle, Patient, Encounter, Observation y DiagnosticReport;
  - **la guía v2-to-FHIR**: sus ConceptMap, del paquete 1.0.0, y sus hojas CSV, del commit `873b331`.

  Las S-n del laboratorio **no cuentan contra un tercero**: son decisiones de un sitio, no del estándar.
- **Donde no decidan ni el estándar ni la guía, no decidas en silencio.** Escribe una pregunta con tu recomendación, la
  alternativa y qué cambia según la respuesta:
  - **Q-CV-D-n** si es de diseño (para Jev);
  - **Q-CV-A-n** si es de alcance.
- **Escribe el diseño en `diseno-conversores-fable.md`, en esta carpeta.** Puede acabar en el repositorio público, así que no
  lleva credenciales, ni nombres de máquinas, personas o empresas privadas, ni alusiones a un sitio real, ni datos de
  pacientes. Puede nombrar los dos conversores y la guía.

Al terminar, devuelve un resumen de 15 líneas como máximo:
- las secciones;
- cada pieza nueva, en una frase;
- la previsión por conversor y familia;
- el número de Q-CV-D y de Q-CV-A;
- los 3 riesgos que más te preocupan.

## Qué hay en la carpeta

| Ruta | Qué es |
|---|---|
| `resultados/ANTES-ETAPA-CONVERSORES.md` | **Léelo primero.** La pregunta fija, las condiciones que no se negocian, las Q-CV-1..5 ya decididas, las fases, el «hecho cuando», el tope y la regla de pieza de portfolio |
| `resultados/RESULTADO-CV-PRE.md` | **Lo segundo.** El eslabón débil medido: elementos alineados con la guía, el valor esperado de ADT sin cita, las 6 filas de convención de ORU, las muestras públicas y la pregunta de la 0354 de v2.8 |
| `resultados/CV-PRE-E1.json` | Por cada fila de la proyección del juez, su clase y las filas de la guía que la cubren (tipo de datos, vocabulario, condición) |
| `resultados/diseno-adt-fable.md`, `resultados/diseno-oru-fable.md`, `resultados/diseno-oru-v11-fable.md`, `resultados/diseno-verificador-ve-fable.md` | Tus diseños anteriores: el contrato de `adt_fhir` y `oru_fhir`, sus almacenes y la etapa 14k |
| `verificador/` | El juez entero (los ficheros de su huella) y sus pruebas. Incluye `info_verificador.json` (S-n, L-n, preguntas pendientes) y `esquema_evidencia.json` |
| `contratos/contrato_canonico_adt.md` | El contrato del canónico ADT, generado desde el código: 77 campos con su valor y su cita |
| `estandar/hl7v25_*.txt` | HL7 v2.5: caps. 2, 2A (tipos de datos), 3 (ADT) y 7 (observaciones) |
| `estandar/v2mappings/` | Los ConceptMap de la guía v2-to-FHIR (paquete 1.0.0): segmentos, tipos de datos y tablas |
| `estandar/guia_csv/` | Las hojas CSV de la guía, del commit `873b331`: PID, PV1, OBX, OBR y los mensajes ADT_A01 y ORU_R01 |
| `estandar/fhir_r4/` | Las StructureDefinition de FHIR R4 de Bundle, Patient, Encounter, Observation y DiagnosticReport |

## Qué debe contener el diseño

1. **El punto de entrada de solo transformación.** Un conversor recibe un mensaje y devuelve un Bundle, o un error. No hay
   MLLP, ni ACK, ni log, ni canónico. Hay que decidir:
   - la forma de la evidencia;
   - qué reglas del juez aplican y cuáles no;
   - qué pasa con un mensaje que el juez no aceptaría: estructura fuera de la 0354, versión, evento fuera de alcance;
   - qué categorías y hallazgos da.
2. **El lector de la salida.** De un Bundle a los recursos que el juez proyecta: Patient, Encounter, Observation y
   DiagnosticReport. Los recursos de un conversor no llevan los identificadores propios del laboratorio, así que hay que
   decir cómo se emparejan con lo esperado (PID-3, PV1-19, el orden de OBR y OBX, las referencias internas del Bundle). Tú
   dices el contrato; Claude lo implementa.
3. **El perfil «guía».** Por cada elemento proyectado, el valor esperado según los ConceptMap de la guía:
   - en ADT, los tipos de datos CX, XPN, XAD, XTN, PL y XCN, y los vocabularios de las tablas 0001, 0002, 0004, 0007, 0069
     y 0112;
   - en ORU, lo que ya cita `[M]`, apartando las 6 filas de convención del laboratorio.

   Dónde la guía admite más de una representación, eso es **convención** y no cuenta. Cómo se cita cada hallazgo.
4. **Cuándo una diferencia «cambia el significado del dato».** Hace falta una definición operativa, porque la regla de
   portfolio la usa: valor distinto, dato perdido, dato inventado, código mal mapeado, recurso duplicado… Frente a forma: orden,
   identificadores generados, extensiones, metadatos. Y cómo se clasifica cada discrepancia: nueva, ya declarada o
   convención.
5. **La versión.** Los conversores declaran plantillas para v2.8 y el corpus está en v2.5. Hay que decir qué hace el juez
   con la diferencia de versiones, y qué hacer con la pregunta de MSH-9.3 (`ADT_A04`… frente a la 0354 de v2.5).
6. **Las pruebas en rojo antes del código (P-CV-n).** Con evidencia sintética y sin conversores, que comprueben cada pieza:
   punto de entrada, lector, perfil y clasificación. Cada una con su control negativo.
7. **La previsión** por conversor y familia (ADT, ORU), hecha a ciegas. No hace falta acertar: hace falta que esté escrita
   antes.
8. **El plan CV1-CV4**, con «hecho cuando», regla de parada y tope por fase. El total de la etapa son cuatro sesiones hasta el
   20-nov, y CV-pre ya gastó parte de la primera. E-CV-3 (que cada conversor corra aislado) es lo primero de CV1.
