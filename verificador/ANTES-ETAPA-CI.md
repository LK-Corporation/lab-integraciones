> *Copia pública: se quitaron las alusiones al autor y a su máquina. El resto es el original del laboratorio.*

# ANTES: etapa 23, el verificador en la integración continua de un conversor (FIJADO el 25-oct-2026)

**Fijado en autónomo**, dentro de la hoja de ruta del laboratorio (`HOJA-DE-RUTA.md`, no publicada). Jev eligió esta etapa
con 0,96 (`decision-jev-ruta6.md`, no publicada); la segunda opción, un cuarto tipo de mensaje, quedó en 0,03, y para ese tipo
prefiere MDM_T02.

## La pregunta (fija)

> ¿Puede un proyecto de conversor HL7 v2 → FHIR pasar su conversor por el verificador en cada cambio, con un flujo reutilizable
> de GitHub Actions, de forma que el cambio falle solo si aparece un hallazgo que no estaba en su línea base?

## Punto de partida (medido)

- **La herramienta de la etapa 18** (`cv/verificar_conversor.py`) pasa un conversor por el juez con un adaptador JSON y una orden.
  - Corre el conversor en una caja de Docker sin red y escribe `juicio.jsonl` e `INFORME.json`.
  - Su control dio los mismos veredictos que el estudio, con los dos conversores, en los 368 casos.
- **Corre en la máquina de quien la lanza.** No hay nada que la corra en cada cambio de un proyecto, ni que distinga un hallazgo
  nuevo de los que el proyecto ya conoce.
- **El repositorio público ya tiene integración continua:** la higiene, en GitHub Actions, con permisos de solo lectura.
- **Los conversores:**
  - LinuxForHealth v1.1.0 es un jar de Maven Central, que se puede montar en el runner como en el estudio;
  - Microsoft se construye desde su código con el SDK de .NET;
  - el conversor de juguete del laboratorio corre sin Docker.
- **Los veredictos de los dos conversores del estudio sobre el corpus público** (las bases ADT, ORU y VXU y los mínimos) están en
  el laboratorio, con el mismo juez.

## Condiciones que no se negocian

1. **Solo terceros públicos.** No se abre nada en los proyectos de los conversores, ni issues ni PR, y no se crean forks ni
   repositorios nuevos. El flujo vive en el repositorio público del laboratorio y se publica con la opción B.
2. **El código de terceros corre en la caja de siempre también en el runner:** Docker sin red, solo lectura, sin privilegios.
   La red solo se usa para traer el conversor, como al construirlo.
3. **Sin secretos y con permisos de solo lectura.** El flujo no escribe en ningún repositorio ni comenta en ningún PR.
4. **El juez no cambia.** La herramienta solo gana lo que haga falta para la línea base, con pruebas en rojo antes.
5. **El aparato se prueba antes de usarlo, y en el sitio donde va a vivir:**
   - **negativo:** el mismo conversor contra su propia línea base pasa;
   - **positivo:** un defecto sembrado en el conversor de juguete hace fallar el flujo, por ese hallazgo y no por otro;
   - **real:** LinuxForHealth v1.1.0, traído en el runner, contra una línea base sacada en el laboratorio, pasa.

## Qué se mide

- **Si el flujo distingue lo nuevo de lo conocido:** con la línea base, el positivo falla y el negativo pasa, en GitHub Actions.
- **Si el resultado del runner es el del laboratorio:** LinuxForHealth v1.1.0 en el runner da los mismos veredictos que en el
  laboratorio, o cada diferencia se explica.
- **Lo que cuesta:** minutos de runner por corrida.

## Previsión (se sella antes de la primera corrida en GitHub Actions)

La probabilidad de que cada control salga a la primera en el runner, y de que el real dé los mismos veredictos que el
laboratorio.

## Hecho cuando

- **El flujo reutilizable y su demostración, publicados,** con los tres controles en verde en GitHub Actions. El positivo verifica
  que el flujo falla.
- **Una guía,** `cv/ci/CI.md`, para que un proyecto lo use en el suyo.
- **Un documento de resultado,** `RESULTADO-CI.md`, con la frase: «Un proyecto puede pasar su conversor por el verificador en cada
  cambio con un flujo reutilizable de GitHub Actions; con el conversor de juguete y LinuxForHealth v1.1.0, el flujo falla solo
  ante un hallazgo que no está en la línea base».

## Tope

**Una sesión.** Si hace falta iterar en el runner, cada nuevo push pasa por la opción B.

## Regla de parada

- **El resultado del runner no es determinista o no cuadra con el del laboratorio, y la diferencia no se explica:** se declara, y
  se publica solo la demostración con el conversor de juguete.

## Fuera de la etapa

- Abrir PR o issues en los proyectos.
- Construir Microsoft en el runner. Se puede describir en la guía, pero no es un control de la etapa.
