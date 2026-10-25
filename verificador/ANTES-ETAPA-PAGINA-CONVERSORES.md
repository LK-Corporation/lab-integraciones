> *Copia pública: se quitaron las alusiones a la máquina del autor y a documentos que no se publican. El resto es el original del laboratorio.*

# ANTES: etapa 19, la página del estudio de conversores (E4, FIJADO el 25-oct-2026)

**Fijado en autónomo**, dentro de la hoja de ruta del laboratorio (`HOJA-DE-RUTA.md`, no publicada). Jev eligió esta extensión tras la 18
(página 0,52 frente a 0,42 de un tercer tipo de mensaje, confianza 0,36; `decision-jev-ruta3.md`, no publicada).

## La pregunta (fija)

> ¿Puede quien llega al repositorio entender **en una página web**, sin abrir ningún Markdown, qué encontró el verificador en
> los dos conversores, cómo se buscó, qué no dice y cómo pasar su propio conversor, **con cada cifra igual a la de los
> documentos publicados**?

## Punto de partida

- **La página del primer estudio** (`docs/index.html`, en GitHub Pages) es estática: sin JavaScript, con las fuentes
  autoalojadas. La higiene comprueba dos cosas: que no carga nada externo, y que sus cifras de resultado están en el informe.
- **El estudio de conversores se cuenta en Markdown:** `ARTICULO.md`, `verificador/RESULTADO-CONVERSORES.md`, los
  documentos de cada fase y sus JSON agregados.
- **La herramienta de la etapa 18** está en `verificador/cv/VC.md`, con dos informes de ejemplo.
- **Los Bundles que devolvieron los conversores no son públicos.** Los mensajes mínimos sí: los genera
  `verificador/cv/cv3_minimos.py`. También el texto del juez de cada hallazgo de los pares, en
  `verificador/cv/RESULTADO-CV3-minimos.json`.

## Condiciones que no se negocian

1. **Las reglas de la página del primer estudio:** nada de JavaScript, nada externo, fuentes autoalojadas, claro y oscuro,
   anchura de teléfono, y que se pueda recorrer con el teclado. «Interactiva» quiere decir lo que HTML y CSS dan solos.
2. **Ninguna cifra a mano.** Toda cifra de la página sale de un documento o JSON publicado, y una prueba de higiene nueva lo
   comprueba.
3. **Lo que el estudio no dice va en la página, no detrás de un enlace.**
4. **Sobre los dos proyectos, nada que el estudio no diga ya.** Los textos públicos van sin alusiones al sitio real.
5. **El método de siempre:**
   - el diseño, a ciegas, por un modelo distinto del que implementa, leyendo solo el repositorio público;
   - las preguntas de diseño, para Jev, con un estado neutro;
   - una revisión a ciegas antes de publicar.
6. **Ni el juez ni los documentos del estudio cambian** para que la página funcione.

## Hecho cuando

- **La página está publicada en GitHub Pages,** enlazada desde `docs/index.html` y desde el README principal.
- **La prueba de higiene nueva está en verde:** las cifras de la página son las de los documentos, y no carga nada externo.
- **Se publicó con la opción B.**

## Tope y regla de parada

- **Tope:** una sesión.
- **Regla de parada:** si tras dos iteraciones la revisión a ciegas sigue encontrando una cifra o una afirmación que no
  respaldan los documentos, la página no se publica. Se declara qué no cuadraba.

## Fuera de la etapa

- JavaScript, analítica o cualquier servicio.
- Cambiar el juez, el estudio o sus cifras.
- Los Bundles de los conversores.
- Traducir la página.
