# Estado: la clase de la candidata de LinuxForHealth y la clase M-28, tras la revisión a ciegas (7-nov-2026)

Redactado el 7-nov-2026. **A propósito NO incluye la recomendación de nadie.**

## Contexto

La etapa 36 clasifica las 2 candidatas de la etapa 33 como nueva, ya declarada, convención o fallo del juez
(`ANTES-ETAPA-CANDIDATAS.md`). La revisión a ciegas pidió cambios por dos razones.
- **Q-CA-1:** el estado con que Jev decidió la candidata de LinuxForHealth (`ca/estado_ca.md`) solo traía hechos de un lado.
- **M-28:** la candidata de Microsoft resultó ser una clase que el estudio ya tenía.

## Hechos de la candidata de LinuxForHealth (PID-8 = `S` → `Patient.gender` = `unknown`)

1. **El estándar y la guía:**
   - la 0001 de v2.5 es una tabla de usuario con valores sugeridos (F, M, O, U, A, N), y la `S` viene del ejemplo mismo de v2.5;
   - el mapa de la guía para la 0001 no tiene `S` ni valor por omisión, y no dice qué hacer con otro valor;
   - `Patient.gender` de FHIR R4 solo admite cuatro códigos.
2. **El proyecto:** una prueba unitaria de su extractor convierte «ABC», un valor fuera de su mapa, en `unknown`. No hay prueba
   con un mensaje entero ni con la `S`.
3. **La regla del estudio de conversores** (su ANTES, `ANTES-ETAPA-CONVERSORES.md:48-51`): una diferencia que el estándar permite
   es convención y no cuenta. Las ya declaradas son discrepancias que cuentan y que el proyecto sabe.
4. **Las 16 convenciones publicadas del estudio** son notas de nivel convención del juez. Entre ellas, «interpretation y
   maritalStatus fuera del ConceptMap»: valores de otras tablas de usuario fuera del mapa de la guía.
5. **El juez, en cambio,** cuenta esta como «valor imposible convertido».
   - Su perfil de PID-8 dice «fuera de la 0001: ausente».
   - Su función para las demás tablas dice «fuera de la tabla (user-defined), convención».
   - Para PID-8, el juez sigue una regla que no está en la guía.
6. **La revisión adversaria** la dio por «ya declarada, con matices», y dijo que «convención» también era defendible. La revisión a
   ciegas dice que, con las definiciones de la propia etapa, encaja en convención.
7. **Lo que implica cada clase:**
   - **ya declarada:** sería una clase declarada más en la versión 2 (las 31 del estudio pasarían a 32), contada como discrepancia
     con la guía;
   - **convención:** no cuenta. Como el juez la cuenta, el juez se equivoca aquí. No entra en las 16, que son notas del juez;
   - **fallo del juez:** lo mismo que convención, pero dicho como error del juez, que una etapa posterior corregiría. El juez no
     cambia en esta.

## Hechos de M-28 (la candidata de Microsoft)

8. **M-28 ya estaba en el estudio publicado.** Es de Microsoft, con el mismo mecanismo y la misma firma («Observation sin origen
   propio»), y la misma declaración (la salida esperada de `ADT-A01-01`). Es «ya declarada», y en el estudio solo mira las muestras
   de Microsoft (`cv/cv3_clases.py:86`).
9. **En esas muestras ya contaba la Observation de ACC.** En `ADT-A31-01`, que lleva ACC y no PDA, la Observation que cuenta es la
   `injury-incident` de ACC. Su descripción publicada, «Observation de PDA (certificado de defunción, autopsia…) que la guía no
   mapea» (`cv/RESULTADO-CV3.md:167`), se queda corta.
10. **La etapa 33 la vio como candidata** porque los 30 ADT con ACC son del corpus del laboratorio, que M-28 no mira. La clase de
    la candidata de Microsoft es «ya declarada: M-28», no una clase nueva, y las 31 ya declaradas no cambian por ella.
11. **Corregir la descripción de M-28 en el estudio** toca su tabla en `cv/RESULTADO-CV3.md` y el texto de `cv/cv3_clases.py`. Además
    obliga a regenerar la página web del estudio, que se escribe desde esa tabla con sus guardas.

## Las preguntas

**Q-CA-1 (otra vez). La clase de la candidata de LinuxForHealth.**
- (a) Ya declarada.
- (b) Convención.
- (c) Fallo del juez.

**Q-CA-2. La descripción de M-28.**
- (a) Se dice en el resultado de la etapa 36 y en la marca del de la 33; el estudio no se toca.
- (b) También se corrige en el estudio (su tabla, `cv3_clases.py` y la página).
