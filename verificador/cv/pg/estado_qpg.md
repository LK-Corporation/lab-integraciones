# Estado: seis decisiones de diseño de la página del estudio de conversores (25-oct-2026)

Redactado el 25-oct-2026. **A propósito NO incluye la recomendación de nadie**, tampoco la del diseñador.

## Contexto

Se va a publicar una página web estática, en GitHub Pages, que cuenta un estudio ya publicado: un verificador determinista
juzgó dos conversores HL7 v2 → FHIR de código abierto. La página cuenta también cómo pasar un conversor propio por el mismo
juez.

**Las condiciones fijas:**
- nada de JavaScript ni de recursos externos;
- ninguna cifra escrita a mano: un guion genera la página desde los ficheros públicos y unas guardas lo comprueban;
- lo que el estudio no dice va en la página;
- sobre los dos proyectos, nada que el estudio no diga.

La página del primer estudio, ya publicada, sigue las mismas reglas. El diseño lo hizo otro modelo, a ciegas, y deja abiertas
estas seis preguntas.

## Hechos

- **La sección central** son las 15 discrepancias confirmadas, una tarjeta por discrepancia. Cada tarjeta lleva lo que
  registró el estudio, la cita de la guía, su par de mensajes mínimos (caso y control, con el disparador marcado) y lo que
  dijo el juez.
- **Lo que hay en los ficheros públicos:** el texto de las 31 discrepancias que los proyectos ya tenían declaradas y el de las
  10 candidatas que tumbó una revisión adversaria.
- **Los veredictos de cada par mínimo:** el fichero público los tiene para los dos conversores.
  - Tres pares escritos para un conversor reproducen también el mecanismo en el otro.
  - Un límite declarado dice que un par que se reproduce en el otro conversor no lo convierte en una discrepancia
    contrastada con su proyecto.
- **Las categorías del estudio por conversor y familia de mensaje** están en una tabla publicada, con el rango previsto antes
  de correr nada. Salieron fuera del rango en varios casos.
- **La página del primer estudio no se ha tocado desde que se publicó.**
- **Un filtro sin JavaScript** se hace con botones de opción y CSS. Oculta tarjetas con `display: none`, y una tarjeta oculta
  no la encuentra la búsqueda del navegador. Hay que probarlo con teclado y lector de pantalla.

## Las preguntas

1. **El título de la página.**
   - (a) «Un juez que no se fía del conversor».
   - (b) «Lo que vio un juez en dos conversores».
   - (c) «Quince discrepancias con cita». Lleva una cifra en letras, así que tendría que ir con su fuente dentro del título.
2. **Las 31 ya declaradas y las 10 que cayeron.**
   - (a) Sus listas completas, en desplegables: unas 41 filas con texto de los proyectos, todo ya público.
   - (b) Solo las cifras, cinco ejemplos y un enlace al documento.
3. **En cada par mínimo, ¿los veredictos de qué conversores?**
   - (a) Los de los dos.
   - (b) Solo el del conversor para el que se escribió.
4. **La comparación con lo previsto.**
   - (a) Una figura de barras apiladas, cuyas etiquetas son las celdas literales de la tabla.
   - (b) Solo la tabla.
5. **El enlace desde la página del primer estudio.**
   - (a) Solo en su párrafo final.
   - (b) También una línea bajo su cabecera, que toca el cuerpo de una página que no ha cambiado desde su publicación.
6. **El filtro por conversor sobre las 15 tarjetas.**
   - (a) Ninguno.
   - (b) Un filtro con botones de opción y CSS.
