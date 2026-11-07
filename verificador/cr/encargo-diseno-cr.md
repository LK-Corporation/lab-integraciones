> *Copia pública: las rutas de la máquina del laboratorio van cambiadas por las relativas a su raíz, su nombre por «la máquina del laboratorio», los nombres de sus cuadernos por «los cuadernos del laboratorio» y la carpeta de trabajo del diseñador por `<carpeta de trabajo>`; las carpetas temporales (`/tmp/…`) y el resto van literales.*

Eres el diseñador a ciegas de una etapa de un laboratorio de integración sanitaria (HL7 v2 → FHIR). Tu trabajo es DISEÑAR, no
programar ni publicar nada. Escribe en español.

## Contexto

El laboratorio publica en GitHub un verificador de conversores con su integración continua:
- un flujo reutilizable (`verificador-conversor.yml`);
- una demostración (`demo-ci.yml`);
- un proyecto de ejemplo que llama al flujo fijado a un commit (`ejemplo-ci.yml`);
- un run en rojo a propósito (`rojo-ci.yml`);
- la higiene (`higiene.yml`).

Antes de cada push, los flujos se ensayan en la máquina del laboratorio con `cv/ci/ensayo_flujo.py`. Desde la etapa anterior, el
ensayo emula los checkouts con lo que se publica (el árbol del índice del clon, o el HEAD si coinciden) y guarda en `ENSAYO.json`,
en la clave `clon`, qué ensayó.

Nada comprueba después que el commit publicado tenga el árbol ensayado. La pregunta, las condiciones, los controles y el «hecho
cuando» están fijados en el ANTES (abajo) y no se discuten. Tu trabajo es diseñar cómo se comprueba.

## Lo que puedes leer (en la máquina del laboratorio, desde la herramienta Bash, SOLO LECTURA)

- `fase12/ANTES-ETAPA-CIRCULO.md`: la pregunta y lo fijado. Empieza por aquí.
- `fase12/cv/ci/ensayo_flujo.py`: el ensayo, y en particular lo que escribe en `ENSAYO.json`.
- `fase12/cv/ci/prueba_ci.py`: el juego de pruebas de la CI (las `P-EN-n` son las del ensayo y montan
  repositorios de git mínimos). No hace falta leerlo entero.
- `fase12/cv/ci/CI.md`: la guía de la CI, en particular «Antes de cada push: el ensayo local».
- `fase12/en/diseno-en-fable.md`: el diseño de la etapa anterior, solo si te hace falta.
- En el clon del repositorio público `publicacion/` (limpio):
  - `.github/workflows/*.yml`, los flujos;
  - `git log`, `git show` y `git status`, solo para leer.

**NO leas nada más.** En particular, ni `RESULTADO-*`, ni `privado/`, ni los cuadernos del laboratorio. No corras
nada que escriba fuera de `/tmp/disenador35/`, ni Docker, ni el ensayo sobre el clon público, y no hagas push a ningún sitio. Si
quieres probar git, hazlo en copias tuyas bajo `/tmp/disenador35/`; puedes crear allí un repositorio vacío (`git init --bare`) que
haga de remoto.

## Lo que tienes que entregar: un documento de diseño

Escríbelo con la herramienta Write en
`<carpeta de trabajo>\cr\diseno-cr-fable.md`.
Va a publicarse. No pongas rutas de la máquina; usa las relativas a la raíz del repositorio o a `verificador/`.

Tiene que decir:

1. **Dónde vive la comprobación y cuándo corre.** Por ejemplo, una orden local después del push, un trabajo en GitHub, o las dos
   cosas. Di cómo llega a ella lo que se ensayó (el `ENSAYO.json` local, algo en el commit o en su mensaje, otra cosa) y con qué
   se compara.
2. **Qué hace en cada caso:**
   - publicado igual que lo ensayado;
   - un `git add` de más después del ensayo;
   - un `commit --amend`;
   - un ensayo sobre otra copia;
   - ningún ensayo;
   - un ensayo de la demo y otro del ejemplo sobre árboles distintos (en la etapa anterior, el ejemplo y el rojo se ensayaron sobre
     un árbol anterior al publicado, que difería en textos);
   - un push de varios commits;
   - un PR.

   Para cada uno, si pasa, cae o avisa, y por qué.
3. **Las decisiones que dejes abiertas,** numeradas `Q-CR-n`, con sus opciones escritas en neutro y lo que implica cada una. Las
   decide otro (Jev): no pongas tu preferencia dentro de la pregunta. Sí puedes dar aparte tu recomendación, con su porqué.
4. **El cambio en el código,** a nivel de funciones y ficheros: qué se añade o cambia, qué imprime y con qué código de salida.
5. **Las pruebas, en rojo antes** (`P-CR-n`): qué monta cada una, qué da antes del cambio y qué después. Dónde van, y cómo corren
   en el trabajo `pruebas` de la demo sin Docker ni red.
6. **Los controles del ANTES, exactos:**
   - el positivo, con un `git add` de más y con un `commit --amend`, y el negativo, publicados en un repositorio de prueba local
     que hace de remoto;
   - el caso real, el push de la propia etapa;
   - qué se compara y cómo se decide.
7. **Lo que cambia en la guía** (`CI.md`): qué frases.
8. **Los riesgos:** qué puede romper en los flujos que ya están en verde, y qué no puede ver la comprobación.

Sé concreto y no especules: lo que no hayas podido comprobar, dilo. Al terminar, contesta con un resumen de diez líneas como mucho
y la lista de las `Q-CR-n`.
