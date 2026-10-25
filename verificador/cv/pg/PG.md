# Etapa 19: la página del estudio de conversores (25-oct-2026)

**Hecho.** El estudio de conversores y la herramienta para pasar un conversor propio tienen su página web:
[lk-corporation.github.io/lab-integraciones/conversores](https://lk-corporation.github.io/lab-integraciones/conversores/). Es
estática: sin JavaScript, sin nada externo y con las fuentes de la primera página. **No lleva ninguna cifra escrita a mano.**

La pregunta y sus condiciones están en [`../../ANTES-ETAPA-PAGINA-CONVERSORES.md`](../../ANTES-ETAPA-PAGINA-CONVERSORES.md).

## Cómo está hecha

- **La escribe un guion,** `codigo/hacer_pagina_conversores.py`, con solo la biblioteca estándar y desde los ficheros
  publicados del estudio. Cada cifra, cada texto del juez, cada cita y cada mensaje mínimo va en un elemento con su fuente
  declarada en `data-fuente`:
  - un puntero a un JSON (`json:verificador/cv/CLASES-CV3.json#frase.N_nuevas_confirmadas`);
  - un patrón sobre un Markdown (`md:`), que tiene que casar una sola vez;
  - una celda de una tabla (`tabla:`);
  - un par de `cv3_minimos.py` (`hl7:`).

  El guion resuelve cada fuente al escribir, y para si una no resuelve. La prosa de enlace vive en el guion y no lleva cifras.
- **La comprueban las guardas de `tests/test_repo_hygiene.py`,** que resuelven las fuentes con su propio código, sin importar
  el guion. Cuatro son nuevas y llevan su control negativo, que rompe la página a propósito y exige que la guarda lo vea:
  - la página es byte a byte la que genera el guion;
  - las 502 fuentes resuelven, coinciden con lo que se muestra y no dejan Markdown sin convertir;
  - no queda ninguna cifra ni palabra-número fuera de una fuente, salvo identificadores como PV1-3 o ORU^R01, y salvo «dos»,
    «un» y «una», que no se vigilan (L-PG-6);
  - hay una tarjeta por cada una de las 15 nuevas, en su orden, y lo que la página dice de la rama principal cuadra con los
    pares.

  Además, una guarda nueva comprueba que las dos páginas son accesibles sin JavaScript. La que ya vigilaba que no cargaran nada
  externo mira ahora también los atributos `on…=` y los enlaces `javascript:`.
- **Lo interactivo es HTML y CSS:** cada discrepancia se despliega con su registro, su cita y su par mínimo, con el disparador
  marcado. Un filtro por conversor, hecho con botones de opción y CSS, oculta las tarjetas del otro.

## Cómo se decidió

- **El diseño, a ciegas:** lo escribió otro modelo (Claude Fable 5.1), leyendo solo el repositorio público
  ([`ENCARGO-PG0.md`](ENCARGO-PG0.md), [`diseno-pg-fable.md`](diseno-pg-fable.md)).
- **Seis preguntas de diseño, decididas por Jev** con un estado neutro, sin la recomendación del diseñador
  ([`estado_qpg.md`](estado_qpg.md), [`decision-jev-qpg.md`](decision-jev-qpg.md)). En cinco de las seis, Jev eligió otra
  opción que la que recomendaba el diseñador; solo coinciden en el enlace:

| Q | Decisión de Jev | Confianza |
|---|---|---|
| Q-PG-D-1, el título | «Lo que vio un juez en dos conversores» | 0,80 |
| Q-PG-D-2, las 31 declaradas y las 10 caídas | solo las cifras, cinco ejemplos y un enlace | 0,38 |
| Q-PG-D-3, los veredictos de cada par | solo el del conversor para el que se escribió | 0,04 |
| Q-PG-D-4, la comparación con lo previsto | la tabla, sin figura | 0,48 |
| Q-PG-D-5, el enlace desde la primera página | solo en su párrafo final | 0,20 |
| Q-PG-D-6, el filtro por conversor | sí, con botones de opción y CSS | 0,78 |

- **Las guardas, en rojo antes que la página:** fallaron las 8 que dependen de ella porque no existía. En su primera corrida
  sobre la página cazaron tres cosas:
  - dos palabras-número en la prosa;
  - las cifras del nombre de un proyecto;
  - un fallo de la propia guarda.

## Desviaciones del diseño (DV-PG-n)

| Id | Qué | Por qué |
|---|---|---|
| DV-PG-1 | El resumen dice «De las 15, 5 son de Microsoft y 10 de LinuxForHealth, y 7 son fuertes» | el diseño decía «7 son fuertes: 5 en Microsoft y 10 en LinuxForHealth», que mezcla dos cuentas: 5 y 10 son las 15 por conversor, no las 7 fuertes |
| DV-PG-2 | Los números de sección los pone un contador de CSS | escritos en el HTML serían cifras sueltas |
| DV-PG-3 | Las cifras van en `<span class="cifra">`, no en `<data>` | es lo que usa la primera página |
| DV-PG-4 | La lista de identificadores admite además nombres de segmento (PV1, GT1), el nombre `hl7v2-fhir-converter` y «CC BY 4.0» | son nombres, no cantidades |
| DV-PG-5 | El disparador se marca comparando las líneas sin MSH-10 | el caso y el control llevan distinto identificador de mensaje, y sin esto la línea MSH salía marcada en todos los pares |
| DV-PG-6 | La guarda de mensajes mira solo los `<pre class="hl7">` | la orden de la herramienta también va en un `<pre>` con fuente |
| DV-PG-7 | Cada matiz de la revisión va en su tarjeta, con su fuente | la primera versión los resumía en una línea y perdía el de M-18; además, generalizaba a L-19 lo que el estudio dice solo de L-12 (revisión a ciegas) |
| DV-PG-8 | Los documentos de la etapa van en `verificador/cv/pg/` | junto a los de la etapa 18 (`cv/vc/`), del mismo estudio |
| DV-PG-9 | La guarda de enlaces relativos no mira dentro de los bloques de código cercados de los Markdown | el diseño trae como ejemplo un trozo de README y de HTML con enlaces que en su carpeta no resuelven. Un enlace roto dentro de un bloque de código ya no se ve; fuera de ellos, sí |
| DV-PG-10 | Cambios de la revisión a ciegas, además del 7: los `**` sin convertir en «Lo que esto no dice», que la guarda de fuentes no veía (ahora sí, con su control negativo); el par mínimo dice qué hallazgo busca y si sale en el caso y en el control; las versiones, anidadas bajo «no es una certificación»; el índice sin números; la clase de «débil» sin tilde; el contraste de las etiquetas; la fuente propia del total en «2 de 2»; dos límites más de la herramienta (L-VC-9 y L-VC-14); una línea por paso del método; los rechazos, sin la cita cruda del Bundle | el revisor dejó dos bloqueantes y quince mejoras; se aplicaron todas |

## Lo que no hace

Los límites L-PG-1..12 están en el diseño. Los que más pesan:
- **La prosa de enlace no se verifica mecánicamente:** solo las cifras, los textos con fuente y los mensajes. La miró una
  revisión a ciegas (L-PG-1).
- **La asociación de cada discrepancia con su frase del artículo es una tabla a mano del guion.** La guarda comprueba que la
  frase está en el artículo, no que esté junto a la discrepancia correcta (L-PG-2).
- **Al ocultar tarjetas, el filtro las saca también de la búsqueda del navegador** (Q-PG-D-6).
- **Sin JavaScript no hay** botón de tema, ni copiar un mensaje, ni abrir todos los desplegables para imprimir (L-PG-3).
