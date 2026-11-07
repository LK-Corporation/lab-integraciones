# Estado: la previsión de la etapa 35, antes de correr los controles (7-nov-2026)

Redactado el 7-nov-2026. **A propósito NO incluye la recomendación de nadie.**

## Contexto

La etapa 35 añade una comprobación de después del push, `cv/ci/comprobar_publicado.py`. Lee del remoto el commit publicado, saca
su árbol y lo compara con el árbol que cada `ENSAYO.json` dice haber ensayado. El ANTES pide sellar, antes de correr los
controles, la probabilidad de dos cosas:
- que los controles salgan a la primera: el positivo cae en sus dos casos y el negativo pasa;
- que el push de la propia etapa pase la comprobación a la primera.

## Hechos

1. **La comprobación está escrita y sus doce pruebas pasan,** a la primera.
   - Montan repositorios de git mínimos con un remoto vacío al lado, sin Docker ni red.
   - Antes de escribir la comprobación caían las doce.
   - Con ella, el juego entero de la CI da TODO BIEN en una exportación del público: 234 comprobaciones, 53 pruebas.
2. **Los controles** se hacen sobre un remoto de prueba local, nunca en el público.
   - **El estado ensayado:** un cambio real en la guía de la CI, añadido al índice, y los tres flujos ensayados una vez sobre ese
     índice.
   - **Desde ahí, tres pushes al remoto de prueba:**
     - el commit tal cual: el negativo, que tiene que pasar;
     - un fichero de más añadido después del ensayo: tiene que caer, con esa ruta;
     - un `commit --amend` con un cambio: tiene que caer, con esa ruta.
3. **Lo que decide cada control** es la igualdad de dos identificadores de árbol de git, de 40 hex. Las pruebas cazaron ya, sobre
   repositorios mínimos, los mismos casos.
4. **El push de la propia etapa:**
   - se ensayan los tres flujos sobre el índice con todo lo de la etapa, se hace el commit y el push, y se comprueba;
   - en la etapa 34 se tocaron textos después de ensayar el ejemplo y el rojo, y su comprobación habría caído. Es justo lo que esta
     etapa mide.
5. **La estimación del diseñador:** 0,95 los controles, 0,8 el push de la etapa a la primera.

## Las preguntas

**P1. ¿Qué probabilidad hay de que los controles salgan a la primera** (los dos positivos caen y el negativo pasa)?
- (a) Alta: 0,9 o más.
- (b) Media: de 0,6 a 0,9.
- (c) Baja: menos de 0,6.

**P2. ¿Qué probabilidad hay de que el push de la etapa pase la comprobación a la primera?**
- (a) Alta: 0,9 o más.
- (b) Media: de 0,6 a 0,9.
- (c) Baja: menos de 0,6.
