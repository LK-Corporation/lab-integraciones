# Estado: Q-CR-5 otra vez, con el estado neutral (7-nov-2026)

Redactado el 7-nov-2026. **A propósito NO incluye la recomendación de nadie.**

## Por qué se pregunta otra vez

Jev decidió `Q-CR-5` dos veces («solo después», confianza 0,12 y 0,18) con un estado (`cr/estado_cr.md`) cuya opción (a) decía
«Solo después, como fija el ANTES». La revisión a ciegas lo ha señalado: el ANTES pregunta por la comprobación de después del push,
pero no dice nada de un modo de antes, ni lo prohíbe. Aquella frase inclinaba la pregunta.

## Contexto

La etapa 35 añade `cv/ci/comprobar_publicado.py`, una orden local de después del push. Lee del remoto el commit publicado y compara
su árbol con el que dice cada `ENSAYO.json` del ensayo. Pasa (0) si coinciden y cae (1) con las rutas que difieren. La pregunta
del ANTES y sus controles son de después del push; la comprobación de después es obligatoria en cualquier caso, porque solo el
remoto dice qué se publicó.

## Hechos

1. **El ANTES** pregunta: «Después del push, ¿se puede comprobar que el árbol publicado es el que se ensayó…?». No dice nada de
   antes del push.
2. **Un modo `--local`** compararía el árbol del HEAD del clon con los `ENSAYO.json`, sin red, justo antes de `git push`.
   - Evita un push malo, en vez de solo verlo después.
   - No sustituye a la comprobación de después.
   - Cuesta una opción más, una rama en el código (de dónde sale el commit) y una prueba más, en una etapa con tope de una sesión.
3. **Lo que ya hay:**
   - la comprobación está escrita sin ese modo;
   - la revisión a ciegas ha pedido otros cambios: pruebas de que se lee el remoto, robustez ante entradas raras y pruebas de
     comportamientos sin probar;
   - el código va a cambiar en cualquier caso, y los controles se repetirán.
4. **Sin el modo `--local`,** lo mismo se puede hacer con un remoto de prueba. Es lo que hacen los controles, y cuesta un clon.

## La pregunta

**Q-CR-5. La comprobación antes del push.**
- (a) Solo la de después del push.
- (b) También un modo `--local`, sobre el HEAD del clon y sin red, para correrlo justo antes del push.
