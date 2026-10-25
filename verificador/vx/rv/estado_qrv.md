# Estado: cinco decisiones de diseño de la etapa 22, las nueve de VXU en las ramas principales (25-oct-2026)

Redactado el 25-oct-2026. **A propósito NO incluye la recomendación de nadie.**

## Contexto

Un laboratorio publicó que un verificador determinista encontró 9 discrepancias nuevas en la conversión de mensajes de vacunación
(VXU^V04) a FHIR, en dos conversores de código abierto: seis en Microsoft FHIR-Converter v7.0 y tres en LinuxForHealth v1.1.0.
Cada una se confirmó con un par de mensajes mínimos: el caso la dispara y el control, casi igual, no. Además, LinuxForHealth
arrastra estado entre mensajes de un mismo proceso (un issue abierto del proyecto lo conoce en parte).

Esta etapa, ya fijada, comprueba si las nueve y el arrastre siguen en la rama principal de cada proyecto y prepara los borradores
de issues para que el autor decida si los abre; no los abre nadie más. Lo fijado no se discute:
- se corren los pares con las versiones fijadas (control) y con las ramas principales, con el mismo juez;
- el control tiene que dar lo mismo que en la etapa anterior, o la diferencia se explica antes de mirar las ramas;
- LinuxForHealth decide mensaje a mensaje, un proceso por mensaje, para que el arrastre no contamine unos pares con otros;
- una discrepancia «sigue» si el juez confirma su par en la rama (el caso sale y el control no), y está «corregida» si el caso
  ya no la da y el campo sale bien;
- se contrasta cada una con los issues y PR del proyecto, abiertos y cerrados, con sus comentarios;
- tope: una sesión.

## Las preguntas

1. **Una de las nueve que en la rama sale «cambiada»:** el hallazgo original ya no sale, pero el juez cuenta otro hallazgo en el
   mismo campo.
   - (a) cuenta como «sigue, con otro síntoma», y el borrador describe el síntoma nuevo;
   - (b) no cuenta como «sigue»: va en una fila aparte, «cambiada, pendiente de contraste», sin borrador;
   - (c) cuenta como corregida.
2. **El borrador de la dosis «.5» que se escribe 5** tiene la misma causa que otro borrador ya escrito para el mismo conversor
   en el estudio anterior (un número con punto inicial en otro campo).
   - (a) un borrador propio;
   - (b) solo un párrafo añadido al borrador anterior;
   - (c) un borrador propio que remite al anterior y, si el anterior se abre antes, se pega como comentario allí.
3. **Una de las nueve ya reportada y cerrada como arreglada, pero cuyo par sigue saliendo en la rama.**
   - (a) un borrador de comentario al issue cerrado, pidiendo reabrirlo, con el par;
   - (b) un borrador de issue nuevo que enlaza el cerrado;
   - (c) solo anotarlo, sin borrador.
4. **La tolerancia del control en el texto del hallazgo:** el veredicto, la categoría y el «sale» son iguales, y solo cambia el
   texto que describe el hallazgo.
   - (a) bloquea hasta que cada diferencia lleve una explicación escrita;
   - (b) el texto no cuenta, como en la comparación de veredictos de la herramienta, y solo se lista;
   - (c) bloquea solo si el texto cambia el valor observado.
5. **¿Se corren también en lote, con la rama de LinuxForHealth, los 50 mensajes de los pares, además de mensaje a mensaje?**
   - (a) sí, como control: se compara con mensaje a mensaje y se declara si difiere (unos 20 segundos);
   - (b) no: la secuencia del arrastre basta, y los pares se deciden solo mensaje a mensaje.
