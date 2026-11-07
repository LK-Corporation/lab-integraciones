> *Copia pública: las rutas de la máquina del laboratorio van cambiadas por las relativas a su raíz, su nombre por «la máquina del laboratorio» y la carpeta de trabajo del diseñador por `<carpeta de trabajo>`; las carpetas temporales (`/tmp/…`) y el resto van literales.*

Eres el diseñador a ciegas de una etapa de un laboratorio de integración sanitaria (HL7 v2 → FHIR). Tu trabajo es DISEÑAR, no
programar ni publicar nada. Escribe en español.

## Contexto

El laboratorio publica en GitHub un verificador de conversores con su integración continua: un flujo reutilizable
(`verificador-conversor.yml`), una demostración (`demo-ci.yml`), un proyecto de ejemplo que llama al flujo fijado a un commit
(`ejemplo-ci.yml`) y un run en rojo a propósito (`rojo-ci.yml`). Antes de cada push se ensayan los flujos en la máquina del
laboratorio con `cv/ci/ensayo_flujo.py`, que emula los pasos `run:` y los checkouts.

El ensayo ha dado verde sobre algo distinto de lo que se iba a publicar. La pregunta, las condiciones, los controles y el «hecho
cuando» están fijados en el ANTES (abajo) y no se discuten. Tu trabajo es diseñar el arreglo.

## Lo que puedes leer (en la máquina del laboratorio, desde la herramienta Bash, SOLO LECTURA)

- `fase12/ANTES-ETAPA-ENSAYO.md`: la pregunta y lo fijado. Empieza por aquí.
- `fase12/cv/ci/ensayo_flujo.py`, entero: el ensayo de hoy.
- `fase12/cv/ci/prueba_ci.py`: el juego de pruebas de la CI, para ver cómo se escriben y cómo se
  cuentan las pruebas (no hace falta leerlo entero).
- `fase12/cv/ci/CI.md`: la guía de la CI, en particular lo que dice del ensayo.
- En el clon del repositorio público `publicacion/` (limpio):
  - `.github/workflows/*.yml`, los flujos que se ensayan;
  - `git log`, `git show` y `git status`, solo para leer.

**NO leas nada más.** En particular, ni `RESULTADO-*`, ni `ga/`, ni `privado/`, ni ninguna nota de cómo se descubrió el
fallo más allá de lo que dice el ANTES. No corras nada que escriba fuera de `/tmp/disenador34/`, ni Docker, ni el ensayo sobre
el clon público. Si quieres probar cómo se comporta git (por ejemplo, `git write-tree`, `git archive` de un árbol o `git status
--porcelain`), hazlo en una copia tuya: `cp -r publicacion /tmp/disenador34/clon`.

## Lo que tienes que entregar: un documento de diseño

Escríbelo con la herramienta Write en
`<carpeta de trabajo>\en\diseno-en-fable.md`.
Va a publicarse. No pongas rutas de la máquina; usa las relativas a la raíz del repositorio o a `verificador/`.

Tiene que decir:

1. **Qué es «lo que se publica»** para cada checkout que el ensayo emula, y qué hace el ensayo en cada estado del clon:
   - el índice distinto del HEAD;
   - cambios sin `git add`;
   - ficheros sin seguimiento o ignorados;
   - un clon limpio;
   - una carpeta sin `.git`.
   Para cada caso: parar, avisar o ensayar otra cosa (y cuál), con sus razones. Ten en cuenta los checkouts con `ref` (un commit
   fijado que ya está publicado, como el del ejemplo) y el que usa `github.sha`.
2. **Las decisiones que dejes abiertas,** numeradas `Q-EN-n`, con sus opciones escritas en neutro y lo que cada una implica. Las
   decidirá otro (Jev); no escribas cuál prefieres dentro de la pregunta, sí puedes dar tu recomendación aparte y con su porqué.
3. **El cambio en el código,** a nivel de funciones: qué cambia en `ensayo_flujo.py`, qué imprime y con qué código de salida.
4. **Las pruebas, en rojo antes** (`P-EN-n`): qué monta cada una, qué da con el ensayo de hoy (en rojo) y qué con el arreglo.
   Dónde van, y cómo corren en el trabajo `pruebas` de la demo sin Docker ni red.
5. **Los dos controles del ANTES, exactos:** cómo se monta cada uno, qué se compara y cómo se decide «lo mismo, informe a
   informe». Lo que puede variar entre dos corridas iguales (horas, rutas temporales) y cómo se aparta sin esconder nada.
6. **Lo que cambia en la guía** (`CI.md`): qué frases.
7. **Los riesgos:** qué puede romper el arreglo en los flujos que ya están en verde, y qué no puede ver el ensayo aunque se
   arregle.

Sé concreto y no especules: lo que no hayas podido comprobar, dilo. Al terminar, contesta con un resumen de diez líneas como
mucho y la lista de las `Q-EN-n`.
