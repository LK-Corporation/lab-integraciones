# Estado: la previsión de la etapa 36, antes de correr los pares y el contraste (7-nov-2026)

Redactado el 7-nov-2026. **A propósito NO incluye la recomendación de nadie.**

## Contexto

La etapa 33 dejó dos candidatas sin confirmar. La etapa 36 las clasifica con el método de las etapas 20 y 26: contraste con lo que
el proyecto ya sabe, un par mínimo y una revisión adversaria (`ANTES-ETAPA-CANDIDATAS.md`). Las clases son cuatro:
- **nueva:** una discrepancia con la guía v2-to-FHIR que el proyecto no declara;
- **ya declarada:** el proyecto ya la declara o la sabe;
- **convención:** la guía la permite o no dice nada y la elección es defendible;
- **fallo del juez:** el juez la marca mal.

El ANTES pide sellar, antes de correr nada, la clase más probable de cada una.

## Hechos

1. **Microsoft, en los 30 ADT con ACC:**
   - emite una Observation (código `injury-incident`) que el juez da por recurso sin origen en el mensaje, con una regla que es
     de ORU (MC-ORU-7);
   - sale con ACC y nunca sin ACC;
   - la guía (`v2mappings` 1.0.0) no mapea ACC en ningún sitio, y en ADT las Observation salen de OBX.
2. **LinuxForHealth, con PID-8 = `S`** (un valor del ejemplo mismo de v2.5, para una perra esterilizada):
   - convierte a `gender: unknown`;
   - la tabla 0001 es de usuario: sus valores son sugeridos y un sitio puede tener otros;
   - el mapa de la guía para la 0001 lleva F, M, O, U, A y N, y no `S`;
   - `Patient.gender` de FHIR R4 solo admite cuatro valores.
3. **Aún no se ha hecho ni el contraste ni el par mínimo.** No se sabe si los proyectos declaran estas conductas.
4. **En las etapas 20 y 26,** de las candidatas que llegaron a este punto, la mayoría se confirmaron como nuevas. Hubo alguna que
   la revisión retiró por ser convención o por un dato del estándar que faltaba (la 26 pasó de 5 a 3).

## Las preguntas

**P1. La clase más probable de la candidata de Microsoft (la Observation de ACC):**
- (a) Nueva.
- (b) Ya declarada.
- (c) Convención.
- (d) Fallo del juez.

**P2. La clase más probable de la candidata de LinuxForHealth (`S` → `unknown`):**
- (a) Nueva.
- (b) Ya declarada.
- (c) Convención.
- (d) Fallo del juez.
