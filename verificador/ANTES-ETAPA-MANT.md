> *Copia pública: se quitaron las alusiones al autor y a su máquina. El resto es el original del laboratorio.*

# ANTES: etapa 25, el mantenimiento del flujo de integración continua (FIJADO el 31-oct-2026)

**Fijado en autónomo**, dentro de la hoja de ruta del laboratorio (`HOJA-DE-RUTA.md`, no publicada). Jev eligió esta etapa con 0,46
(`decision-jev-ruta8.md`, no publicada);
la segunda opción, un cuarto tipo de mensaje, quedó en 0,36, y para ese tipo sigue prefiriendo MDM_T02.

## La pregunta (fija)

> Al subir las acciones de los flujos a versiones que corren en Node.js 24, y el pin del proyecto de ejemplo al commit que las
> trae, ¿siguen los controles de las etapas 23 y 24 dando lo mismo, con los mismos informes byte a byte, y sin el aviso de Node.js
> 20?

## Punto de partida (medido)

- **Los flujos de las etapas 23 y 24 están publicados y en verde:** la demo, el proyecto de ejemplo, el run en rojo a mano y el
  PR. Las cuatro acciones (`checkout`, `setup-python`, `upload-artifact` y `download-artifact`) están fijadas por commit en
  `ACCIONES-CI.json`, a las versiones v4.4.0, v5.6.0, v4.6.2 y v4.3.0.
- **GitHub ya avisa** en cada corrida de que esas acciones van en Node.js 20 y las fuerza a correr en Node.js 24. `ubuntu-latest`
  pasa a Ubuntu 26; los jobs ya corrieron en `ubuntu-26.04`.
- **Las versiones mayores que hay hoy** (`git ls-remote`, 31-oct): checkout v5, v6 y v7; setup-python v6 y v7; upload-artifact v5,
  v6 y v7; download-artifact v6, v7 y v8.
- **El proyecto de ejemplo llama al flujo fijado a `5183b4e`.** Para que use las acciones nuevas hay que subir ese pin en dos
  pushes: uno con el flujo nuevo y otro con el pin.
- **Lo que no puede cambiar:**
  - los `INFORME.json` de la demo, iguales a la corrida 1 de la etapa 23;
  - las bases del ejemplo, sus 349 y 6 casos y el defecto en 164;
  - la conducta del rojo.

## Condiciones que no se negocian

1. **Lo de siempre:**
   - el juez no cambia;
   - el código de terceros va en la caja;
   - sin secretos y con permisos de solo lectura;
   - nada en los proyectos de los conversores;
   - cada push por la opción B.
2. **Cada acción, fijada por commit y cruzada con la API,** como en la etapa 24. El registro va en `ACCIONES-CI.json`.
3. **Cada cambio de los flujos, con su prueba en rojo antes.** Las guardas de la etapa 24 (P-CI-16 y 17) siguen valiendo.
4. **Antes de fijar una versión mayor, se leen sus notas de versión** y se dice qué cambia para estos flujos. Un cambio de
   conducta se prueba en el ensayo o se declara.

## Qué se mide

- **Que nada cambie:** los controles de la demo, del ejemplo y del rojo dan lo mismo que en la etapa 24 (los informes y las
  comprobaciones de fuera), con las acciones nuevas.
- **Que el aviso desaparezca:** las corridas no llevan la anotación de Node.js 20.
- **Lo que cuesta:** pushes y minutos.

## Previsión (se sella antes del primer push)

La probabilidad de que cada flujo salga igual a la primera con las acciones nuevas, y cuántos pushes harán falta.

## Hecho cuando

- **Publicado y en el runner:**
  - las cuatro acciones en versiones con Node.js 24, fijadas y cruzadas;
  - la demo, el ejemplo con su pin subido y el rojo a mano, dando lo mismo;
  - las corridas sin el aviso de Node.js 20.
- **Un documento de resultado,** `RESULTADO-MANT.md`, con la frase: «Con las acciones en Node.js 24 y el ejemplo fijado a su
  nuevo commit, los controles de las etapas 23 y 24 dan lo mismo, con los mismos informes byte a byte».

## Tope

**Una sesión.** Cada push pasa por la opción B.

## Regla de parada

- **Una acción nueva cambia un resultado y no se explica:** se declara, se queda en la versión anterior que funciona, y se
  publica lo que sí.

## Fuera de la etapa

- Cambiar el juez, la herramienta o los conversores.
- Otro proveedor de CI.
- Dependabot u otra automatización que abra PR.
