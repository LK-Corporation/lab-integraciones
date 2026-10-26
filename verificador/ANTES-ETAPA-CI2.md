> *Copia pública: se quitaron las alusiones al autor y a su máquina. El resto es el original del laboratorio.*

# ANTES: etapa 24, lo abierto de la integración continua (FIJADO el 26-oct-2026)

**Fijado en autónomo**, dentro de la hoja de ruta del laboratorio (`HOJA-DE-RUTA.md`, no publicada). Jev eligió esta etapa con 0,61
(`decision-jev-ruta7.md`, no publicada);
la segunda opción, un cuarto tipo de mensaje, quedó en 0,28, y para ese tipo sigue prefiriendo MDM_T02.

## La pregunta (fija)

> Llamado como lo llamaría un tercero (por referencia remota fijada a un commit, con su adaptador, su línea base y su corpus, en
> el modo `pasa`), ¿pasa el flujo cuando no hay nada nuevo y pone el cambio en rojo, con su resumen, cuando aparece un hallazgo
> nuevo? ¿Y aguanta las cuatro observaciones de endurecimiento de la revisión a ciegas de la etapa 23?

## Punto de partida (medido)

- **El flujo reutilizable de la etapa 23** (`.github/workflows/verificador-conversor.yml`) y su demostración (`demo-ci.yml`)
  están publicados. Los tres controles salieron en verde en GitHub Actions al primer push y a mano mensaje a mensaje, con los
  informes del runner iguales byte a byte a los del laboratorio (`verificador/RESULTADO-CI.md`).
- **Lo que no se recorrió en el runner** (`RESULTADO-CI.md`, «Lo que no dice»):
  - la llamada desde fuera, `uses: LK-Corporation/lab-integraciones/…@<commit>`, con `proyecto/ci/…` y un `preparar` propio;
    la demo usa `uses: ./…`, con todo bajo `lab/`;
  - el modo `esperar: pasa`, que es el que usaría un proyecto;
  - las entradas `corpus`, `sin_corpus_lab`, `opciones` y `artefacto_completo`;
  - el evento `pull_request`;
  - el camino en que el job se pone rojo: el positivo falla dentro del flujo, pero el job sale en verde porque es lo que espera.
- **Las cuatro observaciones de la revisión a ciegas que no se hicieron:**
  1. las entradas se interpolan con `${{ }}` dentro de `run:`, y no por variables de entorno;
  2. las acciones van por etiqueta (`@v4`), no fijadas por SHA;
  3. `laboratorio_ref` vale `main` por omisión, así que quien fije `uses:@sha` y lo olvide corre el código de `main`;
  4. la demo nombra el repositorio del laboratorio a mano, y en un fork no funcionaría.

## Condiciones que no se negocian

1. **Ni repositorios nuevos ni forks.** La llamada «de tercero» se hace desde el propio repositorio del laboratorio, con la forma
   remota, y con un proyecto de ejemplo dentro del repositorio: su adaptador, su línea base y su corpus sintético. Un repositorio
   aparte que llame al flujo queda en la cola del autor.
2. **Nada en los proyectos de los conversores,** ni issues ni PR.
3. **Lo de siempre:**
   - el código de terceros, en la caja de siempre;
   - sin secretos y con permisos de solo lectura;
   - el juez no cambia;
   - cada cambio del flujo, con su prueba en rojo antes.
4. **Si se rompe la compatibilidad con la etapa 23** (por ejemplo, `laboratorio_ref` obligatoria), se dice en `CI.md` y en el
   resultado. La demostración sigue en verde.
5. **Un run en rojo a propósito** solo puede correr a mano, nunca en cada push. Tiene que haber un job que compruebe, desde fuera,
   que falló por el hallazgo esperado y que dejó su resumen.

## Qué se mide

- **Si la forma remota funciona:** el flujo llamado por `owner/repo/…@<commit>` con un proyecto de ejemplo, en modo `pasa`, pasa
  contra su base. Con un hallazgo nuevo en un caso de la base, el job queda en rojo, con el resumen en la página.
- **Si las entradas del proyecto llegan:** `corpus` con mensajes propios, `opciones` y `artefacto_completo` cambian lo que deben,
  y nada más.
- **Si el endurecimiento no rompe nada:** los controles de la etapa 23 siguen en verde, con los mismos informes byte a byte.
- **Lo que cuesta:** minutos de runner.

## Previsión (se sella antes del primer push)

La probabilidad de que cada control nuevo salga a la primera en el runner, y cuántos pushes harán falta.

## Hecho cuando

- **Publicado y en el runner:**
  - el proyecto de ejemplo y su llamada por la forma remota, en verde;
  - el run en rojo a propósito, comprobado desde fuera;
  - los cuatro endurecimientos, con sus pruebas.
- **`CI.md` al día,** incluido lo que cambia para quien ya lo usaba.
- **Un documento de resultado,** `RESULTADO-CI2.md`, con la frase: «Llamado como lo llamaría un tercero, por referencia remota
  fijada a un commit y con su adaptador, su base y su corpus, el flujo pasa cuando no hay nada nuevo y pone el cambio en rojo, con
  su resumen, cuando aparece un hallazgo nuevo».

## Tope

**Una sesión.** Cada push pasa por la opción B.

## Regla de parada

- **La forma remota no funciona, o el run en rojo no deja lo que tiene que dejar, y no se explica:** se declara y se publican
  solo los endurecimientos.

## Fuera de la etapa

- Crear un repositorio aparte o un fork.
- Abrir PR o issues en los proyectos de los conversores.
- Otro sistema de CI que no sea GitHub Actions.
- Construir Microsoft en el runner.
