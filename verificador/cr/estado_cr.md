# Estado: las decisiones abiertas del diseño de la etapa 35 (7-nov-2026)

Redactado el 7-nov-2026. **A propósito NO incluye la recomendación de nadie.**

## Contexto

La etapa 35 quiere comprobar, después del push, que el árbol publicado es el que se ensayó: que la comprobación caiga cuando no
lo es y pase cuando lo es (`ANTES-ETAPA-CIRCULO.md`).

Desde la etapa 34, el ensayo local guarda en `ENSAYO.json` el árbol que ensayó (`clon.arbol`). Un push lleva tres ensayos, uno
por flujo: la demo, el ejemplo y el rojo.

En la 34, la demo se ensayó sobre el árbol publicado. El ejemplo y el rojo se ensayaron sobre uno anterior, que difería en textos,
y nada lo comprobó antes del push.

El diseño, a ciegas, es de Fable (`cr/diseno-cr-fable.md`). Propone una orden nueva, `cv/ci/comprobar_publicado.py`:
- lee el commit que el remoto tiene (`git ls-remote`, solo lectura);
- saca su árbol;
- lo compara con el `clon.arbol` de cada `ENSAYO.json`.

Compara árboles, no commits. Lista las rutas que difieren, porque el árbol ensayado sigue en el clon. Sale con 0 si cierra el
círculo, con 1 si no y con 2 si no pudo comprobar. Quedan siete decisiones abiertas.

## Hechos que valen para varias

1. **Git, probado por el diseñador:**
   - con un ensayo sobre el índice, un commit y un push, el árbol publicado es el ensayado;
   - un `git add` de más o un `commit --amend` con cambios dan otro árbol;
   - un amend que solo cambia el mensaje da el mismo árbol;
   - `git merge-tree --write-tree` predice el árbol de una fusión.
2. **Los flujos de GitHub no ven el ensayo.** Lo único que podría ver un trabajo en GitHub es algo escrito en el commit (un
   *trailer* en el mensaje), que es una afirmación, no una comprobación. Firmar está fuera de la etapa.
3. **Las condiciones del ANTES:**
   - lo que ya está en verde sigue en verde;
   - sin secretos ni permisos nuevos;
   - un lector a ciegas;
   - una sesión.
4. **En la práctica del laboratorio** se ensayan siempre los tres flujos antes de cada push, con los mismos jobs: la demo con
   pruebas, negativo y positivo; el ejemplo con los suyos; el rojo con los suyos. El rojo solo corre a mano en GitHub.
5. **Los dos PR del repositorio** se fusionaron por *squash*: el árbol fusionado es el de la rama si `main` no avanzó.

## Las preguntas

**Q-CR-1. Dónde vive la comprobación.**
- (a) Una orden local después del push, y nada en GitHub. Ve los `ENSAYO.json` y lista las diferencias; los flujos no cambian.
  Corre solo si se corre, y su registro es local.
- (b) La orden local más un testigo en GitHub. La orden escribe en el mensaje del commit una línea `Ensayado: <árbol>`, y un
  flujo nuevo la compara con el árbol del commit.
  - GitHub cae si no coinciden.
  - Con un commit sin esa línea (un tercero, un fork) solo puede avisar, salvo que se limite al repositorio propio.
  - Es una afirmación sin firma, un flujo más que mantener, y no se puede ensayar con el ensayo local.
- (c) Solo el testigo de GitHub. Nada compara con los `ENSAYO.json`, y «ningún ensayo» no se distingue de «sin la línea». El
  control con un remoto local no se puede hacer.

**Q-CR-2. Qué flujos tienen que estar ensayados para que pase.**
- (a) Siempre los tres. Un push sin ensayo del rojo cae, aunque el rojo solo corra a mano. No hay lógica de rutas.
- (b) Los que GitHub dispararía con ese push, según los filtros `paths:` de cada flujo, y el rojo como aviso. Hay que emular
  esos filtros: un error ahí es un verde falso. Un push que solo toca la raíz no exige ensayo.
- (c) Los que se den, con un aviso por cada uno que falte. «Ningún ensayo» nunca cae.

**Q-CR-3. Un ensayo sobre un árbol distinto del publicado.**
- (a) Cae siempre, con las rutas que difieren y la orden para re-ensayar. Un texto tocado después del ensayo obliga a
  re-ensayar los tres flujos.
- (b) Pasa con aviso si todas las rutas distintas quedan fuera de los filtros `paths:` del flujo, y cae si alguna cae dentro.
  Hay que emular los filtros. En el caso de la 34 habría caído igual, porque los textos estaban en `verificador/`.

**Q-CR-4. Un ensayo en rojo sobre el árbol publicado.**
- (a) Cae: el círculo exige un ensayo verde, no solo el mismo árbol.
- (b) Solo compara árboles y avisa.

**Q-CR-5. La comprobación antes del push.**
- (a) Solo después, como fija el ANTES. Detecta, pero no evita.
- (b) También con una opción `--local` sobre el HEAD del clon, sin red, justo antes del push. Es una opción más con su prueba;
  evita el push malo, y el «después» sigue siendo obligatorio.

**Q-CR-6. Dónde queda el registro del caso real** (la comprobación del push de la propia etapa).
- (a) En un segundo commit, con `cr/PUBLICADO-PUSH.json` y su línea en el resultado. Son dos pushes, como en las etapas 23, 24 y
  25, y tres ensayos más para un commit con un JSON.
- (b) Un solo push. El registro se guarda fuera del repositorio público y el resultado lo cita por su contenido, así que el
  «hecho cuando» se apoya en algo que no está publicado.

**Q-CR-7. Qué jobs tiene que haber ensayado cada flujo.**
- (a) Cualquiera: basta con que haya alguno. Un ensayo de solo `pruebas` de la demo cierra el círculo de la demo.
- (b) Una lista mínima fija por flujo, la que ya se ensaya. Un ensayo a medias no cierra el círculo, y la tabla hay que tocarla
  si cambian los jobs.
