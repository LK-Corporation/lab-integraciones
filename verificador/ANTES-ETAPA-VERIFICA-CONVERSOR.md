> *Copia pública: se quitaron las alusiones al trabajo del autor y a su máquina. El resto es el original del laboratorio.*

# ANTES: etapa 18, «verifica tu conversor en un comando» (E3, FIJADO el 24-oct-2026)

**Fijado en autónomo**, dentro de la hoja de ruta del laboratorio (`HOJA-DE-RUTA.md`, no publicada). Jev eligió esta extensión como la
primera tras la meta (Q-R-5, 0,97; `decision-jev-ruta2.md`, no publicada).

## La pregunta (fija)

> ¿Puede un tercero pasar su conversor HL7 v2 → FHIR por el verificador con **un fichero de adaptador y una orden**, sin
> escribir código, y obtener **el mismo juicio** que obtuvo el laboratorio a mano en el estudio de conversores?

## Punto de partida

- **Pasar un conversor hoy exige escribir código.** El estudio de conversores (14l) lo hizo con un arnés escrito para cada
  conversor (`cv/correr_conversor.py`, con Microsoft y LinuxForHealth metidos en el código), y con tres scripts más:
  - `cv/juzgar_cv2.py`, que juzga;
  - `cv/cv3_clases.py`, que clasifica;
  - `cv/cv3_minimos.py`, que genera los pares mínimos y los juzga.
- **El corpus es público:** las bases A1 y E2 (`a1/`, `bases_adt/`), las ORU que genera `bases_oru.py` y los 68 mensajes
  mínimos que genera `cv/cv3_minimos.py`.
- **El juez juzga una conversión con los puntos `adt_conv` y `oru_conv`**, con la evidencia
  `{mensaje, punto_entrada, conversion: {conversor, salida, perfil_valor}}`.

## Condiciones que no se negocian

1. **El código de terceros solo corre en la caja:** Docker sin red, solo lectura, usuario sin privilegios y sin capacidades.
   La herramienta no ejecuta nada del conversor fuera de ella.
2. **Solo biblioteca estándar de Python.** El adaptador es JSON.
3. **El juez no cambia** para que la herramienta funcione. Si algo del juez estorba, se declara.
4. **Las pruebas, en rojo antes del código**, con un conversor de juguete que no necesita Docker, para que corran en cualquier
   sitio.
5. **El diseño, a ciegas,** por un modelo distinto del que implementa. Solo lee el repo público. Las preguntas de diseño las
   decide Jev con un estado neutro.
6. **Solo terceros públicos**, y nada de material privado en el diseño ni en lo publicado.

## Hecho cuando

- **Un formato de adaptador declarativo** (JSON) y su descripción, con los adaptadores de los dos conversores del estudio.
- **`python3 cv/verificar_conversor.py <adaptador.json> <carpeta de salida>`** hace cuatro cosas:
  - corre el conversor en la caja sobre el corpus público y los pares mínimos;
  - juzga cada salida;
  - clasifica;
  - escribe un informe en Markdown, y su JSON, con las categorías, los mecanismos por clase de las ocho y los pares que se
    reproducen.
- **El control:** con los adaptadores de Microsoft y LinuxForHealth, la herramienta da **exactamente los mismos veredictos**
  que el estudio sobre el mismo corpus, caso por caso, con el mismo juez. Cualquier diferencia se explica.
- **Las pruebas nuevas en verde**, y las de siempre igual.
- **Publicado con la opción B**, con el README que diga cómo usarlo y qué no hace.

## Tope y regla de parada

- **Tope:** dos sesiones.
- **Regla de parada:** si tras dos iteraciones los adaptadores no reproducen los veredictos del estudio:
  - se declara lo que difiere y por qué;
  - la herramienta se publica marcada como «experimental», o no se publica, según decida Jev.

## Fuera de la etapa

- Otros tipos de mensaje (SIU, MDM, VXU…): el juez solo los acusa.
- Ejecutar conversores sin Docker.
- Un servicio web: la herramienta es de línea de órdenes.
- Cambiar el juez.
