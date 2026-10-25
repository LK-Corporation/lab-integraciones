> *Copia pública: se quitaron las alusiones a la máquina del autor y a documentos que no se publican. El resto es el original del laboratorio.*

# Encargo PG0: diseño de la página del estudio de conversores (etapa 19)

Diseñas, sin programar, una página web estática. Debe contar a quien llega al repositorio qué encontró un verificador
determinista en dos conversores HL7 v2 → FHIR de código abierto, y cómo pasar su propio conversor por él. Quien la construya
será otro modelo y seguirá tu diseño. Responde en español.

## Dónde mirar

**Lee solo** el repositorio público (este). No leas nada fuera de él, no modifiques nada y no ejecutes red.

**Lo que tienes que entender:**
- **La página que ya existe:** `docs/index.html`, del primer estudio, con sus fuentes en `docs/fonts/`. Mira su estilo, su
  estructura y cómo resume un informe.
- **Las reglas que la vigilan:** `tests/test_repo_hygiene.py`, en especial `test_la_pagina_no_carga_nada_externo` y
  `test_la_pagina_y_el_informe_dicen_las_mismas_cifras`.
- **El estudio de conversores:**
  - `ARTICULO.md`, el artículo;
  - `verificador/RESULTADO-CONVERSORES.md`, el cierre;
  - `verificador/cv/RESULTADO-CV3.md` y `verificador/cv/CLASES-CV3.json`, las discrepancias y su clase;
  - `verificador/cv/RESULTADO-CV3-minimos.json` y `verificador/cv/cv3_minimos.py`, los pares mínimos y su generador;
  - `verificador/cv/RESULTADO-15A.md`, las ramas principales;
  - `verificador/cv/RESULTADO-CV2.json`, las categorías.
- **La herramienta para pasar un conversor propio:** `verificador/cv/VC.md` y sus ejemplos en `verificador/cv/vc/ejemplos/`.
- **El README principal**, por donde entra el lector.

## Las condiciones (no se negocian)

1. **Las mismas reglas que la página del primer estudio:** nada de JavaScript, nada externo, fuentes autoalojadas, claro y
   oscuro, anchura de teléfono y recorrible con el teclado. Si quieres interacción, solo la que dan HTML y CSS.
2. **Ninguna cifra a mano:** toda cifra de la página sale de un documento o JSON publicado. Una prueba de higiene nueva tiene
   que poder comprobarlo.
3. **Lo que el estudio no dice va en la página,** no detrás de un enlace.
4. **Sobre los dos proyectos, nada que el estudio no diga ya.**
5. **Los Bundles de los conversores no son públicos;** los mensajes mínimos y el texto del juez sí.
6. **Ni el juez ni los documentos del estudio cambian.**

## Qué tienes que entregar

Un documento de diseño en Markdown con:
1. **Las decisiones (S-PG-n),** cada una con su porqué en una línea.
2. **La estructura de la página:**
   - cada sección;
   - qué dice;
   - de qué fichero y campo sale cada cifra y cada texto;
   - qué es interactivo y cómo se hace sin JavaScript.
3. **Cómo se construye:**
   - a mano, o generada por un script desde los ficheros públicos;
   - dónde vive y con qué URL;
   - cómo se enlaza desde `docs/index.html` y desde el README.
4. **La prueba de higiene nueva:** qué comprueba exactamente, con su control negativo.
5. **Las pruebas** que demuestran que la página dice lo que dicen los documentos, con su control negativo.
6. **Las preguntas de diseño para Jev (Q-PG-D-n):** solo las que no deciden ni la pregunta ni las condiciones, cada una con sus
   opciones y qué cambia según la respuesta. Tu recomendación, **aparte**.
7. **Los límites (L-PG-n)** y **el plan** por fases, con su «hecho cuando» y su regla de parada. El tope es una sesión.
