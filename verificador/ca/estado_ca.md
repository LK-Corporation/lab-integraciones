# Estado: la clase de la candidata de LinuxForHealth, tras la revisión adversaria (7-nov-2026)

Redactado el 7-nov-2026. **A propósito NO incluye la recomendación de nadie.**

## Contexto

La etapa 36 clasifica las 2 candidatas de la 33 como nueva, ya declarada, convención o fallo del juez (`ANTES-ETAPA-CANDIDATAS.md`).
Las definiciones de dos de esas clases:
- **ya declarada:** el proyecto ya declara la conducta o la sabe;
- **convención:** la guía la permite o no dice nada y la elección es defendible.

La de Microsoft (ACC → Observation `injury-incident`) quedó como ya declarada. La revisión adversaria la sostiene: la declaran una
salida esperada publicada, su prueba y la documentación del proyecto.

## Hechos de la candidata de LinuxForHealth (PID-8 = `S` → `Patient.gender` = `unknown`)

1. **El par mínimo:** con `S`, `unknown`; con `F`, `female`; con `U`, `unknown`.
2. **La guía no dice nada de `S`.**
   - El mapa de la 0001 de la guía lleva F, M, O, U, A y N, sin valor por omisión.
   - La 0001 de v2.5 es de usuario, y la `S` viene del ejemplo mismo de v2.5.
   - `Patient.gender` de FHIR R4 solo admite cuatro valores.
3. **Lo que tiene el proyecto:**
   - una prueba unitaria del extractor que el proyecto usa para PID-8. Aplica a «ABC», un valor fuera de su mapa, y espera
     `unknown`. Existe en la v1.1.0 y en la rama principal;
   - no hay ninguna prueba con un mensaje entero ni con la `S`;
   - la documentación no lo dice, y no hay ningún issue ni PR sobre esto.
4. **La revisión adversaria** dice que se sostiene «ya declarada», con un matiz: la declaración es débil. Si se exige una declaración
   con un mensaje entero, la clase sería convención.
5. **Con cualquiera de las dos clases, no es una discrepancia nueva.**
   - Lo que cambia es cómo se cuenta: ya declarada es lo que el proyecto sabe; convención, lo que la guía deja abierto.
   - En las etapas 20 y 26 se usó «ya declarada» cuando lo declaraba una salida esperada o una prueba.

## La pregunta

**Q-CA-1. La clase de la candidata de LinuxForHealth.**
- (a) Ya declarada: el proyecto la sabe por su prueba del extractor.
- (b) Convención: la guía no dice nada y la prueba del proyecto es solo del extractor.
