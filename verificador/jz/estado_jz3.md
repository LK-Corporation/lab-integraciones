# Estado: dos decisiones de la etapa 37 tras la segunda pasada de la revisión a ciegas (8-nov-2026)

Redactado el 8-nov-2026. **A propósito NO incluye la recomendación de nadie.**

## Contexto

La etapa 37 arregla dos fallos del juez que encontró la etapa 36.
- El rejuicio da 662 diferencias: 499 de la conducta 1, 161 de la 2 y 2 de una lectura de NK1-15. Ninguna sale «fuera».
- Un clasificador pone cada diferencia en su sitio, con un control que siembra siete defectos en el juez.

El lector a ciegas hizo sus dos pasadas, que son el tope de la etapa. La segunda **aprobó**, con tres menores. Uno es de texto y del
desglose, y se arregla sin más. Los otros dos piden una decisión.

**Hecho común:** el tope de dos pasadas está gastado. Lo que se cambie ahora se publica sin que el lector lo vea.

## Q-JZ-8. Lo que el clasificador del rejuicio todavía acepta

**Medido por el lector:** el clasificador da por de una conducta tres cambios que no lo son.
- **(i)** PID-8 = `X`, el conversor copia `X`, y desaparece un FHIR inválido solo: da conducta 1. Con las reglas de la etapa nunca es
  legítimo, porque el FHIR inválido solo sale fundido con «valor imposible convertido». Se ve sin abrir el Bundle.
- **(ii)** Entra una nota de versión, con la cita de la 0001, en un mensaje de v2.5: da conducta 1. No compara el subtipo de la nota
  con la versión de MSH-12.
- **(iii)** Una Observation inventada que el juez da por de ACC, citando un ACC-1 que el mensaje trae: da conducta 2. El clasificador
  no ve el Bundle, así que no comprueba que la Observation lleve el dato citado.

**También medido por el lector:**
- **El control no lo demuestra.** De sus siete pasadas, la de «la Observation de un OBX, dada por de ACC» saca sus 909 evidencias
  «fuera» porque desaparece una nota de la Observation del OBX, no por las reglas de la conducta 2. El resultado dice que esa
  pasada «tiene forma de conducta», y eso no vale para ella.
- **En los datos no pasa ninguno de los tres casos:**
  - ningún FHIR inválido sale solo;
  - las notas de convención entran solo en mensajes 2.5, y las de versión solo en 2.5.1 y 2.8;
  - las 365 Observation llevan códigos de ACC o de PDA.

  El rejuicio daría lo mismo con cualquier opción.
- **Su propuesta:** cualquiera de las dos primeras opciones. Del texto dice que «son dos frases».

**Las opciones:**
- **(a) Texto.** «Lo que no mira» dice los tres casos, y la frase del control se corrige: dice qué saca «fuera» cada pasada.
- **(b) Dos comprobaciones más y texto.**
  - El clasificador comprueba (i) y (ii), con su prueba en rojo antes, y se repiten el rejuicio y el control (segundos).
  - (iii) va en «Lo que no mira», y la frase del control se corrige.
- **(c) Las tres comprobaciones.**
  - Como (b), y además (iii): el clasificador recibe el Bundle y mira que la Observation lleve el dato citado.
  - El control gana una pasada que ejerza esa regla.

## Q-JZ-9. El texto de versión del servidor

**Medido:**
- **El error es de esta etapa.** El tercer parche del juez cambió «L-CV-1..16» por «L-CV-1..17» dentro de la entrada de la etapa 14l
  del texto de versión que sirve el servidor. L-CV-17 es de la 37, así que el texto atribuye a la 14l un límite que no es suyo.
- **La prueba no lo vio.** P-CV-32 solo buscaba la cadena «L-CV-1..17».
- **Arreglarlo es tocar el juez:**
  - la huella cambia por tercera vez y las tres bases de la demostración se rehacen (unos 50 minutos);
  - la huella del README y del manifiesto se pone al día;
  - P-CV-32 se endurece, con su rojo antes;
  - ningún veredicto cambia, y el rejuicio y las bases se comprueban otra vez.
- **Dejarlo:** el juez publicado sirve ese texto, y el resultado lo declara.

**Las opciones:**
- **(a) Arreglarlo:** una entrada de la etapa 37 en el texto de versión, con L-CV-17, y la de la 14l otra vez con «L-CV-1..16».
- **(b) Dejarlo y declararlo** en el resultado.
