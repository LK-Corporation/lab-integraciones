# Estado: decisiones de diseño de la ampliación del piloto del agente (Q-AMP-2..10)

Redactado el 13-oct-2026. **A propósito NO incluye la recomendación de nadie.**

## Contexto

Un piloto comparó un agente con modelo con una referencia determinista sin modelo (REF). Las dos localizan y arreglan fallos
de circuitos de integración HL7 v2.5 → FHIR R4, guiadas por el veredicto de un verificador determinista (el juez).

- **Resultado del piloto** (11 casos reales):
  - el agente localiza 10/11 y la referencia 6/11;
  - McNemar 5 a 1, p = 0,22: «indeterminado» según la regla preinscrita (Δ ≥ 0,20 y p < 0,10 para «aporta»);
  - la ventaja está en fallos históricos de un circuito (5/5 frente a 1/5); en fallos vivos empatan.
- **La ampliación.** El responsable decidió ampliar el corpus después de ver ese resultado, con unos 6 casos nuevos:
  - 1 histórico, de un commit de cierre de deuda;
  - 5 fallos vivos declarados por el propio verificador como deudas de los circuitos.
- **Rasgos de los casos nuevos:**
  - **Deudas por decisión.** Algunos son decisiones conscientes de quien construyó el circuito: el juez los cuenta como fallo,
    pero el circuito los hace adrede. Ejemplos: un circuito de varios tipos que no comprueba la versión porque así se decidió;
    otro que lee como UTF-8 lo que llega en latin-1.
  - **Pistas.** El fichero que recibe el agente (`verificador.json`) y algunos comentarios del código nombran la deuda y su
    causa en 4 de los 6. El agente y el modelo de contraste (DeepSeek) los leen; REF no.
  - **Un caso que el juez quizá no acepta nunca.** El arreglo correcto de un caso es no mandar acuse cuando el emisor pide «sin
    acuse» (MSH-15/16 = NE). El juez quizá no da `correcto` sin acuse: lo cuenta como fallo de entorno.
- **Saldo del brazo DeepSeek:** unos 0,45 USD, que dan unas 4 tiradas.

## Las decisiones

- **Q-AMP-2 (el caso NE).** Si el juez no puede dar `correcto` a «sin acuse», el caso no se puede arreglar, por construcción.
  Opciones:
  - retirarlo como límite del juez y del perfil, declarado;
  - arreglar el verificador antes del sello y volver a medir. El juez de la ampliación sería entonces distinto del juez del
    piloto.
- **Q-AMP-3 (la guarda de versión que falta, decisión declarada con confianza baja).** Opciones:
  - cuenta como caso, y las negaciones razonadas («no hay fallo») se reportan aparte;
  - solo como control.
- **Q-AMP-4 (las pistas).** ¿Se recortan de `verificador.json` los cuatro paréntesis que nombran la deuda y su causa?
  - **No recortar:** el fichero queda idéntico al del piloto, las pistas se listan y una sensibilidad las quita del análisis. El
    agente y DeepSeek leen la causa en 4 de 6 casos y REF no.
  - **Recortar:** la caja deja de ser idéntica a la del piloto, y se recorta mirando el corpus.
- **Q-AMP-5 (el análisis tras ampliar habiendo visto p).** Opciones:
  - **(B) Combinación de dos etapas** (inverso-normal, pesos √11 y √n₂, α = 0,05 a una cola). Para «aporta», los casos nuevos
    tienen que dar 3 a favor y 0 en contra, 5/1, 7/2 u 8/3.
  - **(A) Solo los casos nuevos, como réplica independiente.** «Aporta» exige 5/0 con unos 6-8 casos: casi siempre saldrá
    «indeterminado».
  - **(C) Todo junto,** como si fuera un solo estudio. El p sale optimista por la parada opcional.
- **Q-AMP-6 (disparadores construidos para H).** Si el banco de mensajes no tiene al menos 3 que fallen por el defecto
  histórico, opciones:
  - construir disparadores, escritos antes de mirar el arreglo;
  - usar solo el banco, como en el piloto. En el piloto, dos H se retiraron con 0 disparadores.
- **Q-AMP-7 (DeepSeek con 0,45 USD).** Opciones:
  - correr unas 4 tiradas, descriptivo, y declarar lo no medido;
  - no correr DeepSeek en la ampliación.
- **Q-AMP-8 (dos candidatos con la misma unidad de código como verdad).** Opciones:
  - fundirlos en un caso con dos grupos de disparadores;
  - dejarlos como dos casos.
- **Q-AMP-9 (los caracteres de control en un caso de validación de contenido).** Opciones:
  - dejarlos fuera de sus disparadores: solo fecha inválida y sexo fuera de tabla;
  - incluirlos como un tercer grupo. Es más realista, pero el arreglo exige más comprobaciones y casi seguro nadie lo logra.
- **Q-AMP-10 (UTF-8 frente a latin-1, decisión declarada; el arreglo conforme exige detectar el juego de caracteres).**
  Opciones:
  - cuenta para localizar y arreglar;
  - cuenta solo para localizar, y el arreglo se calcula sin él.
