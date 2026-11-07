# Estado: las decisiones abiertas del diseño de la etapa 34 (7-nov-2026)

Redactado el 7-nov-2026. **A propósito NO incluye la recomendación de nadie.**

## Contexto

La etapa 34 arregla el ensayo local de los flujos de la integración continua (`cv/ci/ensayo_flujo.py`) para que no dé verde
sobre algo distinto de lo que se va a publicar, sin cambiar lo que da cuando coinciden (`ANTES-ETAPA-ENSAYO.md`).

En la etapa 33, el clon del repositorio público tenía la etapa preparada en el índice, sin commit. El ensayo sacó el
laboratorio con `git archive` del HEAD, que era el commit ya publicado, y dio verde sobre lo viejo. Ensayado sobre una
exportación del índice sin `.git`, probó lo nuevo.

El diseño, a ciegas, es de Fable (`en/diseno-en-fable.md`).
- **Lo que se publica es el árbol del índice.** Un commit fijado que ya está en el repositorio se publica tal cual.
- **El ensayo mira el estado del clon una vez al empezar.**
- **Cada checkout sin `ref`, o con `github.sha`, saca lo que se publica.** Un `ref` que es un commit del clon se sigue sacando
  con `git archive` de ese commit, como hoy.
- **Ocho pruebas nuevas, en rojo antes,** y los dos controles del ANTES.

Quedan ocho decisiones abiertas.

## Hechos que valen para varias

1. **Git, probado por el diseñador en una copia del clon:**
   - `git write-tree` sobre una copia del índice da el árbol de lo preparado sin tocar el índice del clon. Deja un objeto árbol
     colgante en `.git/objects`, que `gc` quita.
   - `git archive` de un árbol funciona como el de un commit y conserva los permisos de ejecución, en 0,05 s para 11 MB. La única
     diferencia es el mtime de los ficheros.
   - En el estado de la etapa 33, el árbol del índice es exactamente el del commit que se publicó después.
2. **La práctica de este laboratorio:**
   - **El primer push de la 33:** se preparó en el índice, se ensayó, se revisó a ciegas y se hizo el commit solo después de la
     decisión de publicar.
   - **El segundo push:** se hizo el commit en local antes de ensayar, para que el pin saliera con `git archive`. Un commit
     local sin push se puede rehacer.
3. **La comprobación de los flujos:** solo exige que `laboratorio_ref` sean 40 hex. Ningún informe que se compare guarda
   `github.sha`; si alguno lo guardara, se vería en el control positivo.
4. **Cuando lo ensayado coincide con lo publicado** (clon limpio o carpeta sin `.git`), el ANTES exige que el ensayo dé lo
   mismo que hoy, informe a informe.
5. **El tope** es una sesión y un lector a ciegas.

## Las preguntas

**Q-EN-1. Con el índice distinto del HEAD.**
- (a) Se ensaya el árbol del índice, y `github.sha` no es un commit. El ensayo sirve antes del commit, como se hizo el primer
  push de la 33.
- (b) Se para con el código 2 y se pide el commit. `github.sha` es siempre un commit de verdad, así que la emulación es más
  fiel. Cada ensayo en rojo obliga a rehacer el commit local o a uno de arreglo.
- (c) Como (b), salvo con una opción explícita (`--indice`) que hace (a). Son dos modos y una opción más que documentar y
  probar.

**Q-EN-2. Con cambios sin `git add` o ficheros sin seguimiento** (los ignorados no entran en ningún caso).
- (a) Se para con el código 2 antes de correr nada, con la lista de rutas. Para ensayar con algo al lado, hay que apartarlo
  (`git stash -u`) o ensayar una exportación del índice.
- (b) Se avisa (en la cabecera, la última línea y `ENSAYO.json`) y se sigue con el índice. El aviso puede perderse: en la 33, la
  única señal fue un texto en una línea.
- (c) Se para solo si las rutas tocan lo que usan los flujos (`verificador/`, `ejemplo-ci/`, `.github/`, `tests/`), y se avisa
  con el resto. Hay que mantener esa lista de rutas.

**Q-EN-3. Cómo se exporta el índice.**
- (a) `git write-tree` sobre una copia del índice y `git archive` del árbol. Es el mismo camino que para los commits, y da un id
  de 40 hex. Deja un objeto colgante en `.git`.
- (b) `git checkout-index -a`. No escribe nada en `.git` y no da ningún id. Son dos caminos de exportación.

**Q-EN-4. Qué vale `github.sha` cuando lo publicado no es un commit.**
- (a) El id del árbol del índice: 40 hex que pasan la comprobación, no resuelven a ningún commit y dicen qué se ensayó.
- (b) Un marcador fijo, como sin `.git`. El registro no distingue dos ensayos de índices distintos.
- (c) El HEAD, con la regla «`ref` igual al HEAD, el índice». En el push del pin, el laboratorio del ejemplo se ensayaría con
  el índice y no con el commit fijado, que es lo que se publica.

**Q-EN-5. Un commit fijado que está en el clon pero no en `origin/main`** (sin push, o un `fetch` pendiente). Está fuera de la
pregunta estricta del ANTES.
- (a) Nada, como hoy. El ensayo da verde y GitHub no podría traer ese commit.
- (b) Un aviso en la línea del checkout, mirando la referencia local de `origin/main`, que sin red puede estar atrasada.
- (c) Parar.

**Q-EN-6. Sin `.git`, un `ref` que no se puede resolver** (el ejemplo y el rojo sobre una exportación).
- (a) Se copia la carpeta, como hoy, con un aviso en la línea. La exportación da lo mismo que hoy (la condición del ANTES), y
  el laboratorio del ejemplo se ensaya con la exportación, no con su commit fijado.
- (b) Se para. La exportación solo serviría para la demo.

**Q-EN-7. Dónde van las pruebas nuevas.**
- (a) En `cv/ci/prueba_ci.py`, como un grupo nuevo al final (`P-EN-n`). El fichero, de 1.235 líneas, crece unas 150.
- (b) En un fichero aparte que `prueba_ci.py` importa. Las ayudas de las pruebas tienen que pasarse o importarse en círculo.

**Q-EN-8. Cómo se comparan los controles** (doce corridas en el negativo).
- (a) Un guion publicado, con su prueba en rojo. Es más código y otra prueba dentro del tope de una sesión.
- (b) `diff -r` entre las carpetas, con lo apartado listado una a una en el resultado. No hay código nuevo, y el resultado lleva
  el diff.
