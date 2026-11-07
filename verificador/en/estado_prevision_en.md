# Estado: la previsión de la etapa 34, antes de correr los controles (7-nov-2026)

Redactado el 7-nov-2026. **A propósito NO incluye la recomendación de nadie.**

## Contexto

La etapa 34 arregla el ensayo local de la integración continua (`cv/ci/ensayo_flujo.py`) para que emule los checkouts con lo que
se publica: el índice del clon, o el HEAD si coinciden. Con cambios sin `git add` o ficheros sin seguimiento, no ensaya nada.
El ANTES pide sellar, antes de correr los controles con el arreglo, la probabilidad de dos cosas:
- que el control negativo dé lo mismo byte a byte a la primera;
- que el positivo deje de dar verde sobre lo viejo.

## Hechos

1. **El arreglo está escrito y sus pruebas pasan.**
   - Son ocho pruebas nuevas sobre repositorios de git mínimos, sin Docker.
   - Antes del arreglo daban 21 comprobaciones en rojo, con todos sus controles en verde.
   - Con el arreglo, el juego entero de la CI da TODO BIEN: 185 comprobaciones, 39 pruebas.
   - Las de la herramienta siguen igual (154).
2. **El control negativo** son doce corridas: dos estados (un clon limpio en `74a6a99` y su exportación sin `.git`), tres flujos
   (la demo sin el trabajo real, el ejemplo y el rojo) y dos versiones del ensayo (la de hoy y la arreglada). Las dos versiones
   corren con la misma carpeta de trabajo, y se comparan con `diff -r`.
3. **Lo que cambia en el clon limpio:**
   - Los checkouts con `ref` (el del laboratorio en la demo, y el commit fijado del ejemplo) hacen la misma orden que hoy.
   - El checkout sin `ref` pasa de copiar el árbol de trabajo a `git archive` del HEAD. El contenido es el mismo salvo los
     ignorados y la fecha de modificación de los ficheros.
   - En la exportación sin `.git`, todo se copia como hoy.
4. **Lo que el diseño no pudo comprobar:** si los informes llevan fechas, horas o duraciones, y si la fecha de modificación de los
   ficheros llega a algún informe.
5. **El control positivo** es el estado de la etapa 33: el HEAD en `371937c`, y el índice y el árbol de trabajo en `54e8b9f`.
   - Hoy, ahí, el ensayo saca el laboratorio del HEAD y da verde con lo viejo.
   - Con el arreglo, en las pruebas mínimas, saca el índice.
   - Se decide con tres hechos: la línea del checkout, el informe distinto del de hoy en ese estado, y el informe igual al de hoy
     sobre un clon limpio en `54e8b9f`.
6. **La estimación del diseñador:** 0,95 el positivo, 0,7 el negativo byte a byte a la primera.
7. **En etapas anteriores,** las corridas de la herramienta dieron informes iguales byte a byte entre dos corridas con el mismo
   conversor. Para Microsoft no siempre: algunos de sus errores llevan identificadores aleatorios. Estos controles solo usan el
   conversor de juguete y el del proyecto de ejemplo.

## Las preguntas

**P1. ¿Qué probabilidad hay de que el control negativo dé lo mismo, informe a informe, a la primera?**
- (a) Alta: 0,9 o más.
- (b) Media: de 0,6 a 0,9.
- (c) Baja: menos de 0,6.

**P2. ¿Qué probabilidad hay de que el control positivo deje de dar verde sobre lo viejo?**
- (a) Alta: 0,9 o más.
- (b) Media: de 0,6 a 0,9.
- (c) Baja: menos de 0,6.
