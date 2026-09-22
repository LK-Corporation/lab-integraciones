# Revisión externa del diseño v2 de la Fase 13 — Fable, 22-sep-2026

**Leído:** `encargo_diseno13b.md` y nada más, por control de contaminación.

## Veredicto en cinco líneas

1. **La v2 repara la producción de B y reincide en la rotura 1 de la v1 en el endpoint:** el residuo declarado es «¿dónde gana el modelo cuando el escritor de reglas se rinde?», que es condicionar en el desenlace del comparador con una persona en el lugar del oráculo de mecanicidad. La propia §1 lo prohíbe.
2. **El argumento de §2 que «rescata la fase» no la rescata:** lo que impide que la regla actualizada valga ≈1 (estado entre mensajes, concurrencia, evidencia fuera de la traza) ciega igual al agente. La fase solo se rescata si existe una clase «evidencia en la traza pero no expresable como regla», que el diseño ni nombra ni mide; los diez fallos de §2 dan un prior de cero para esa clase.
3. **Séptimo modo de fallo: el canal de autor compartido.** Las mismas manos escriben las invariantes que definen «fallo silencioso» en B, el prompt que dice al agente qué buscar, el piloto que ajusta la capa y el puntuador. B(b) puede ser la lista de comprobación del prompt con otro nombre. Se destapa hoy, sin ejecutar nada.
4. **Dos mandos sin clavar dejan el primario indefinido:** qué es un «tipo» en B (de ello dependen N y la macro) y de dónde salen los limpios de B (sin limpios perturbados, «la entrada es rara» es una estrategia ganadora que el veto no ve).
5. **La emergencia es viable para producir B y para la pregunta de §3; no lo es para hacer que el residuo sea no trivial.** Cambio mínimo: el primario de §3 se queda, el residuo baja a descriptivo con su κ y su contraparte medida, y las comprobaciones de coste cero de §6 de este informe se adelantan al piloto.

---

## 0. Antes que nada: los errores de razonamiento

### 0.1 El residuo es la rotura 1 de la v1 con una persona dentro

§1, rotura 1: «Agrupar los tipos por "¿se le puede inducir una regla?" y preguntar dónde gana el modelo es condicionar en el desenlace del comparador.»

§6, punto 1: el autor de la regla actualizada entrega «la lista de tipos que declara no poder cubrir con una regla estática», y «la nota del agente sobre ese subconjunto va en portada».

Es la misma operación: agrupar los tipos por «¿se puede escribir una regla?» y preguntar dónde gana el modelo. Ha cambiado el oráculo (de inductor automático a declaración humana), no la estructura. Lo que parece distinguirlas —la declaración se hace antes de puntuar al agente y por alguien que no lo ve— evita seleccionar sobre el desenlace del agente, pero no evita seleccionar sobre el desenlace *predicho* del comparador. Y el argumento de fondo de la v1 no era formal sino sustantivo: donde las reglas fallan porque la evidencia no es observable, el modelo falla también, y el estrato sale decidido de antemano. Ese argumento se traslada intacto (0.2).

No digo que la pregunta sea ilegítima: digo que está condicionada a que exista una clase de fallos que el diseño no ha demostrado, y que la v2 la pone en portada antes de comprobarlo, con los mismos vicios que la §1 identificó (denominador elegido por una parte, sin clase de regla, sin acuerdo entre jueces). Consecuencia inmediata: el diseño tiene dos «preguntas de la fase» —§3 primer párrafo (detección a exposición cero) y §3 último párrafo / §6 (el residuo)— y dos números en portada. Bajo preinscripción hay un primario. El de §3 es defendible; el residuo, como está, no.

### 0.2 Lo que «rescata la fase» en §2 no la rescata

Llamo **bundle** al paquete de evidencia que un brazo recibe para una instancia (traza MLLP, acuse, recurso FHIR, log). El diseño no lo define; hace falta (§6). Partición de B por dónde vive la evidencia discriminante:

- **E1** — en el bundle y expresable como predicado determinista a partir del contrato. La regla actualizada vale ≈1 una vez visto el tipo. Peor aún: una sola regla —una implementación de referencia del contrato más un `diff` entre el recurso esperado y el producido— cubre *todo* E1 de una vez, presente y futuro.
- **E2** — en el bundle, pero no expresable como predicado. La única clase donde «las reglas no llegan y el modelo sí» es posible.
- **E3** — fuera del bundle (estado entre mensajes, concurrencia, temporización, consultas en vivo). Nadie lo detecta desde el bundle. Una nota distinta de cero del agente aquí no es capacidad: es fuga o asimetría de herramientas.

§2 cita fenómenos E3 —«estado entre mensajes», «solo bajo concurrencia», «evidencia que no está en la traza»— como la razón de que la actualizada ya no valga ≈1. Es verdad y es irrelevante: E3 no rescata la fase, infla el residuo con tipos en los que el agente saca cero por construcción. El rescate exige E2 ≠ ∅, y nada en el diseño lo argumenta ni lo mide.

Prior barato con lo que hay en el encargo: clasificar los diez de §2 con esta lente. Mi lectura, a confirmar con el bundle sellado: #1, #2, #3, #5, #6, #7 y #8 son E1 (código de acuse, secuencia literal, 404/401, timeout, ERR-3, repetición 11, orden de segmentos: todo predicado sobre entrada y salida); #4 es E1 si el reset queda en el bundle y E3 si no; #9 es **E0**, invisible en la traza para cualquiera (dos bugs que se cancelaban); #10 es E3 (ajustes aceptados y no aplicados). **Cero E2 entre los únicos fallos emergentes que este laboratorio ha producido.**

Y la propia §4.2 empuja B hacia E1: un candidato entra solo si el curador «señala la cláusula». Cláusula + bundle = predicado. E2, si existe, vive en el cajón de disputados, que §4.2 saca del primario. La regla de rigor vacía la clase que la fase necesita.

Un tercer error, del mismo tipo: «Su sesgo está acotado y medido: +0,705». Ese número es reglas-solo-contrato **sobre A**, donde el oráculo era el catálogo; mide que saber el contrato no es saber el catálogo. Sobre B(b) el oráculo *es* el contrato, así que las mismas reglas pueden valer ≈1. El sesgo de (b) se mide corriendo `v3-invariante` (o el `diff` de referencia) sobre los aciertos (b) del piloto, no citando A.

---

## 1. El séptimo modo de fallo

**F7 · El canal de autor compartido: una persona en cuatro puntos de la cadena de medida.** Ningún artefacto lleva el sesgo; lo lleva la misma cabeza escribiendo artefactos distintos que luego se comparan entre sí. Por eso no se ve desde dentro.

**Toma 1, la letal: relaciones ↔ prompt.** Las relaciones metamórficas las escribe quien afinó el prompt un mes contra A, y ese prompt de 17.136 caracteres casi seguro *nombra* las invariantes que su autor aprendió a mirar: desescapado, normalización, coherencia acuse/recurso, repeticiones. F3 teme que (b) imprima la firma **del contrato**; el modo que falta es que (b) imprima la firma **de la lectura del contrato que ya está en el prompt**. Si las relaciones selladas son en lo esencial las comprobaciones que el prompt ya pide, B(b) es «lo que al agente se le dijo que buscara» y el primario mide recuerdo del prompt, no capacidad. Sellar «antes de correr nada» no lo evita: es antes de correr, pero después del mes. F4 aparta los diez fallos concretos, no las *generalizaciones* de los diez que viven a la vez en el prompt y en las relaciones (el #2 enseña «comprueba el desescapado en cualquier campo»; una relación de escapes y un tipo nuevo de escape en otro campo caen dentro sin coincidir con el #2).

*Lo destapa hoy, a coste cero:* una tabla de solapamiento relación ↔ prompt. Para cada relación sellada: la cláusula del estándar o del contrato que cita, y el pasaje del prompt que pide esa misma comprobación (o «ninguno»). Si la mayoría tiene pasaje, el primario sobre B(b) está contaminado antes de existir B. Con la tabla, el primario se estratifica por «invariante nombrada en el prompt / no nombrada», y el brazo genérico es el control natural: si el afinado solo gana al genérico en las nombradas, el mes compró una lista de comprobación.

*Cambio mínimo:* un segundo autor de relaciones, ciego al prompt, escribe su conjunto solo con estándar y contrato; se publica el solapamiento entre los dos conjuntos y con el prompt; se sella la unión. Cada relación lleva su cláusula: una relación sin cláusula es opinión del autor, es decir, un operador declarado, y se aparta.

**Toma 2: el piloto y la capa.** El autor corre el piloto, ve qué familias producen silenciosos bajo *sus* relaciones y «cambia la capa» si no llega al 2 %. Iterar la capa hasta que produzca silenciosos según (b) selecciona B hacia las relaciones: es la rotura 3 de la v1 (seleccionar el banco) en otro sitio. *Cambio mínimo:* configuración y semillas de la capa selladas antes del piloto; cada cambio posterior, escrito y justificado; el número de iteraciones se publica.

**Toma 3: el puntuador.** Con 16 autopruebas escritas contra el vocabulario de A (tres clases, `ideal_b`), un tipo de B que no encaje en las tres clases obliga a un mapeo que decide el autor: un mando que no está en la tabla de §6. *Lo destapa:* una segunda lectura ciega de las salidas del agente sobre una muestra del piloto, κ entre puntuador y lector. *Cambio mínimo:* que la respuesta binaria lleve una **localización** (segmento/campo o elemento del recurso) que el puntuador compara mecánicamente con la del curador; la detección con localización equivocada se cuenta aparte (véase F8, por qué importa).

**Toma 4: el paquete del curador.** Lleva las relaciones y «el ejecutor». Con las relaciones en la mano, el curador de (c) adjudica la muestra contra ellas, y (c) —la única vía «insesgada»— pasa a ser (b) con cara humana. Si «el ejecutor» le enseña qué perturbación se aplicó a cada ejecución, tipo tiende a ser igual a perturbación (F9). *Cambio mínimo:* el curador adjudica fallo/limpio y cláusula **sobre el mismo bundle que ven los brazos**, sin relaciones ni etiqueta de perturbación; ambas se le revelan después del veredicto, para el descriptor. Principio único que resuelve varias cosas: si el curador necesita más que el bundle para decidir, el tipo es E3 para todos los brazos.

Dos modos más, de la misma lectura, que dejan el primario indefinido:

**F8 · B es rara por construcción y «raro» se detecta sin entender el fallo.** Tres familias (transporte, codificación, gramática) producen entradas distinguibles del corpus limpio por rasgos de superficie; carga y entorno deja huella en la traza (tiempos, resets) más que en el mensaje; el corpus real es la única sin este confundente. Un detector —agente o regla— que diga «fallo» cuando la entrada es rara puntúa alto en B-fallo sin haber detectado nada. El veto de falsas alarmas solo lo ve si **los limpios de B son entradas perturbadas que el sistema manejó conforme al contrato**, emparejadas por familia con los fallos; el diseño no dice de dónde salen los limpios de B, y si salen del corpus sin perturbar, «raro ⇒ fallo» gana. Afecta igual al autor de la regla actualizada (cubre «todo» con reglas de rareza que pasan el fuera-de-muestra intra-tipo) y por tanto al residuo.
*Lo destapa, sobre el piloto, sin curador:* el adversario mecánico de B, que como principio se escribe antes que el agente: un clasificador trivial de rasgos de superficie (validez del marco, fracción de bytes no ASCII, desviación del número de segmentos, MSH-12, longitud). Su AUC separando B-fallo de B-limpio es el número; por encima de ~0,8 el banco es un detector de fuzzing.
*Cambio mínimo:* limpios de B de la misma distribución perturbada, por familia; techo absoluto de falsas alarmas preinscrito además del relativo (el relativo a `v3` congelado es laxo si `v3` también dispara sobre entradas raras); localización en la respuesta (toma 3).

**F9 · «Tipo» no está definido, luego N no es un número.** El primario es macro por tipo y §8 habla de «tipos genuinamente distintos», pero no hay relación de equivalencia. Si dos perturbaciones disparan el mismo bug (NFD y escapes garabatean el nombre por el mismo camino), ¿uno o dos tipos? Si una perturbación dispara dos bugs, ¿uno o dos? La respuesta fija N, k y la macro, y hoy la fija el curador sobre la marcha.
*Cambio mínimo:* tipo = (cláusula incumplida, síntoma observable, mecanismo sospechado), sellado en la regla de adjudicación; la familia de perturbación es descriptor, nunca clave.
*Lo destapa:* κ entre dos codificadores sobre la **asignación de tipo** de los candidatos del piloto, no solo sobre fallo/limpio. Si el κ de tipo es bajo, N no existe.

---

## 2. ¿Emergencia, o el contrato con otro nombre?

La emergencia es una propiedad del **descubrimiento**, no del fallo: los diez de §2 no eran invertibles el primer día porque nadie los buscaba; en cuanto alguien los mira con una cláusula en la mano, son predicados. Eso es exactamente lo que necesita la pregunta de §3 (nadie se lo describió al agente) y exactamente lo que no sirve al residuo (una vez curado con cláusula, todo es invertible).

**Vía (b).** La transformación T de una relación metamórfica es un operador; la relación añade el oráculo f(x) = f(T(x)). La diferencia con A es que el fallo no está garantizado: se aplica T y el sistema puede pasar. Pero en cuanto falla, el tipo es «el sistema viola R bajo T» y su firma es la huella de T en la entrada más la discrepancia en la salida: invertible, exactamente como un operador leído al revés. La distinción que sí es real: el espacio de T viene de un catálogo de *equivalencias* del estándar, no de un catálogo de *fallos*, y se esperaba que el sistema pasara. Eso vale para la exposición cero y vale cero para el residuo. Respuesta a «¿basta publicar la proporción?»: no. La proporción es un descriptor; la prueba de que B(b) no es el contrato leído al revés es **la cobertura de los aciertos (b) del piloto por reglas solo-contrato** (`v3-invariante` si parsea y normaliza; si es solo regex, el `diff` de referencia). Cobertura ≈ 1 ⇒ F3 confirmado antes de contratar. Cobertura claramente < 1 con la evidencia en el bundle ⇒ existe E2 y me equivoco: entonces la fase merece el curador y el residuo puede subir a portada con el protocolo de §3 de este informe.

**Vía (a).** «Sin oráculo y por tanto sin sesgo» es falso dos veces. Primero, (a) es una lista de síntomas escrita por el autor —caídas, resets, «recurso que nunca se escribe», «fuera de orden»—, es decir, predicados genéricos; los dos últimos necesitan el contrato (qué recurso debía escribirse, qué orden se esperaba). Segundo, parte de lo que (a) recoge es la propia perturbación (un reset inyectado *es* un reset), no un fallo del sistema; separar «síntoma esperable de la perturbación» de «mal comportamiento» exige el contrato. Y sí tiene el problema contrario que teme el encargo: (a) es por construcción la clase ruidosa, trivial para cualquier brazo (la actualizada la cubre con «sin acuse ⇒ fallo»), así que su cuota infla la macro sin informar sobre capacidad. La cuota de (a) no prueba nada sobre F3, al contrario de lo que dice §7. *Cambio mínimo:* (a) se escribe como predicados explícitos y se sella junto con (b); el primario se reporta por vía; se comprueba si el `v3` congelado ya dispara sobre los aciertos (a) (firma vieja).

**Vía (c), con números.** Con tasa base de silenciosos p = 1 % y n adjudicaciones uniformes: P(0 silenciosos) = 0,99ⁿ, que es 13 % con n = 200 y 5 % con n = 300. Estimar p con semianchura relativa del 50 % al 95 % pide n ≈ 1,96²·(1−p)/(p·0,25) ≈ 1.500. Pero (c) no tiene que estimar p: tiene que acotar lo que (a)+(b) **dejan fuera**. Si (b) captura el 80 % de los silenciosos, la tasa de silenciosos-no-vistos es 0,2 %: 0,6 casos esperados en 300 adjudicaciones. Con cero hallazgos, la regla del tres da una cota superior de 3/n = 1 % sobre ejecuciones, vacua cuando la tasa base es 1 %. **A tasa base del 1 %, (c) uniforme no puede acotar el recall de (b) a ningún n asequible.** Lo que sí puede: medir la *precisión* de (a) y (b) sobre sus propios aciertos (50 aciertos bastan), dar el κ, y publicar la cota 3/n con esas palabras («cota, no estimación»). El diseño debe decir esto en vez de «acota lo que (a) y (b) se dejan fuera». Dos detalles: κ sobre fallo/limpio con prevalencia del 1 % es degenerado (ambos codificadores dicen «limpio» el 99 % de las veces), así que se calcula sobre el conjunto enriquecido —aciertos de (a)/(b) más una muestra limpia— y se publica con la prevalencia. Y el curador de (c) sin relaciones (F7, toma 4).

**Cuarta vía, y más.**
- **(d) Oráculos de tercero.** El validador oficial de FHIR sobre el `Patient` producido, contra el perfil; un validador de conformidad v2 sobre el acuse. Su autor no es el del laboratorio, nunca vio el prompt ni A, y su firma es la del estándar tal cual, no la de una lectura del estándar. Cubren violaciones estructurales, no semánticas de mapeo; es justo la parte de F7 que ningún sellado arregla. Coste: horas.
- **(e) Determinismo y replay.** La misma entrada dos veces; el mismo lote en dos órdenes; la misma entrada antes y después de un reinicio. No necesita contrato ni cláusula: dos salidas distintas para la misma entrada son un candidato. Es el oráculo natural de «carga y entorno», donde salieron 4 de los 10, y además fabrica k sin diseñar nada (§5).
- **(f) Control positivo del aparato.** Si alguno de los diez sigue presente en el circuito congelado (no lo sé; lo pido), la capa debe reproducir su disparador y (a)+(b)+(d)+(e) deben verlo. «El oráculo ve X de los diez conocidos» es la única medida de recall que no cuesta un curador. Los diez van luego al estrato F4 igualmente.
- **(g) Conciliación en masa.** Los PID de entrada contra la tabla de `Patient` del almacén, en bloque: oráculo diferencial a nivel de conjunto de datos, y es como apareció el #9.

---

## 3. El residuo

**Qué acota la declaración sin filtrar nada.** El diseño ya tiene los dos brazos que sirven de control; falta cablearlos:

1. **Suelo contra el exceso.** El inductor, calibrado en A antes de ver B, se corre sobre todo tipo declarado «no cubrible». Si lo cubre, la declaración es falsa y se publica como tal. No estratifica el primario: acota una secundaria, que es lo que §5 permite.
2. **Fuera de muestra contra el defecto.** Todo tipo declarado «cubierto» se puntúa fuera de muestra; los que quedan en el suelo son cobertura falsa. Se publica el **residuo medido** (tipos con nota fuera de muestra ≤ suelo) junto al **residuo declarado**, y la matriz de confusión entre ambos. Declarado ≠ medido es un hallazgo sobre el autor, no sobre B.
3. **κ del residuo.** El residuo es una etiqueta y necesita acuerdo: dos autores de reglas independientes, o uno más un declarante ciego. Sin κ, el residuo es una opinión con N.
4. **Clasificación obligatoria por evidencia.** Cada entrada del residuo se declara R1, «la evidencia no está en el bundle» (el curador lo verifica; va a E3, fuera de portada, y sirve de **control negativo**: una detección del agente en R1 es fuga o asimetría, no capacidad), o R2, «la evidencia está en el bundle y no sé escribir un predicado, porque…». Solo R2 dice algo sobre capacidad, y es la clase que 0.2 predice vacía.
5. **Clase de regla sellada.** «Regla estática» sin clase es infalsable. Lenguaje, bibliotecas (¿parsea HL7? ¿normaliza Unicode? ¿lee el recurso FHIR? ¿mantiene estado?), tiempo T. El residuo se publica como «no cubierto en T bajo la clase C», nunca como «no cubrible».

**Si el autor es un modelo.** La estructura no cambia; cambian dos cosas. (i) Se puede **replicar**: n corridas de la declaración con semillas distintas; si el residuo cambia entre corridas, es ruido, y el κ sale gratis. (ii) **Familia**: un autor de la familia del agente declara «no cubrible» lo que su familia no entiende, que es lo que el agente tampoco entiende; el residuo pasa a ser la lista de puntos ciegos del agente y la nota de portada sale negativa por construcción. Familia distinta o persona, y en todo caso registrada: F5 lo dice para el curador y falta decirlo para el autor de reglas y para los dos codificadores del κ. Ventaja de un modelo: se le da el mismo arnés que al agente y la simetría de evidencia queda resuelta por construcción.

**Su trampa propia.** El total de la Fase 12 escondía el detalle por tipo; el DiD de la v1 seleccionaba el banco. El residuo de la v2 es **un denominador elegido por una parte de la comparación, sin clase de regla, con N pequeño dentro y contaminado por E3**. Cuatro caras: la portada depende de cuánto se rinda el autor; N₁ (§5) no se le aplica y puede ser una nota sobre dos tipos; E3 lo pone a cero por construcción, y un cero-que-no-es-cero se lee como éxito cuando es fuga; y como el autor trabaja con tiempo T, «no cubrible» es «no cubierto en T»: coste otra vez, que es lo que la v1 no podía contestar.

**Si sale vacío.** Es publicable y es útil: «sobre un B emergente de N tipos, todo tipo curado fue cubierto con la clase C en tiempo T, con nota fuera de muestra X». Es el resultado de la Fase 12 sobre un banco al que no se puede acusar de favorecer a las reglas, y el primario de §3 no lo toca. «Banco que no puede contestar» es F1 o F2, no un residuo vacío, y ambos se detectan en el piloto. Lo que no puede ocurrir es un residuo declarado vacío con mala cobertura fuera de muestra: eso es defecto de declaración, y el residuo medido lo atrapa.

---

## 4. El brazo del prompt afinado

**La evidencia de simetría es dentro de muestra.** El afinado se afinó contra A y gana en la clase silenciosa de A (−0,229 → +0,500). Eso no dice que los 17.136 caracteres sean «el contrato»; dice que son el contrato *más lo que A enseñó*. **Descomposición, una hora, sin ejecutar nada:** caracteres del prompt por origen — (i) cláusulas del contrato o del estándar; (ii) lecciones trazables a operadores de A o a los diez; (iii) ejemplos few-shot (¿de A?); (iv) procedimiento, formato y herramientas. Todo (ii) y (iii) no es el contrato: en B es fuga si B se solapa con ello, y lastre si no (anclaje a fallos con forma de A; forzar tipos nuevos en las tres clases).

**El brazo barato que decide:** un tercer prompt, *solo-contrato* = genérico + (i). Tres prompts sobre B: genérico (1.174), solo-contrato, afinado (17.136). Solo-contrato ≈ afinado ⇒ el mes compró el contrato, y la afirmación de §5 queda verificada. Afinado > solo-contrato ⇒ lo que sobra viene de (ii)/(iii), y se separa fuga de habilidad transferible con la estratificación «nombrada en el prompt / no nombrada» de F7.

**Desajuste de modo.** Los números de la simetría son en «modo techo» (+0,787 contra +0,615); el primario es «el de la Fase 12», que si es el agente con herramientas puntuó +0,642. Si es así, la comparación genérico/afinado se hizo en una configuración distinta de la que se va a puntuar. O se corren los dos prompts en el modo del primario, o se declara que el primario es el modo techo. Lo pido abajo.

**Simetría de evidencia con las reglas.** El autor de la regla ve B y la traza; el agente con herramientas puede consultar estado en vivo, que a la hora de puntuar ya no es el de la ejecución (FHIR ha vuelto, el contenedor se reinició). Asimetría en las dos direcciones. Mismo bundle sellado para todos los brazos; si el agente necesita algo fuera del bundle, ese algo entra en el bundle para todos o el tipo es E3 para todos.

**Lastre, medible en el piloto sin curador:** tasa de disparo de cada prompt sobre limpios sin perturbar y sobre limpios perturbados, por familia. Las salidas se guardan selladas y no las ve quien escribe la regla de adjudicación hasta que esté sellada; si no, el curado se contamina con la conducta del agente.

---

## 5. El tamaño

**La regla que lo cierra: preinscribir la función, no el número.** Antes del piloto se fijan dos anclajes —el nulo (25 %) y una alternativa X % que el autor considera «interesante», por ejemplo 50 %— y N₁ se deriva: con detección por tipo binaria, distinguir 0,25 de 0,50 a una cola, α = 0,05, potencia 0,80, da N₁ ≈ 21 tipos; un IC del 95 % de semianchura 0,15 en torno a 0,5 pide ≈ 43. La única discreción es X, y se ejerce **antes** de ver el piloto. Hoy §9 pone el negativo en números (paso 6) después del piloto (paso 2) y de la distribución (paso 3): «antes de que exista B» se cumple en la letra, no en el espíritu, porque el piloto ya enseña cuántos tipos habrá. Mover 5 y 6 delante de 2; sellar la configuración y las semillas de la capa antes del piloto; fijar ahora el presupuesto de ejecuciones (§11.5) como regla de parada de la capa, sin reanudarla después de ver al agente. Y decidir ahora si las ejecuciones del piloto entran en B: solo pueden entrar si la regla de adjudicación estaba sellada antes del piloto, que es lo que este orden garantiza.

**El agujero más grande: 25 % no es un nulo.** Con un agente que dispara con probabilidad q en cualquier instancia, P(tipo «detectado» | k) = P(Bin(k, q) ≥ ⌈k/2⌉). Con q = 0,30: k = 2 → 0,51; k = 3 → 0,22; k = 4 → 0,35; k = 5 → 0,16. Un B dominado por tipos con k = 2 y un agente que dispara sobre el 30 % de las entradas raras **pasa el 25 % con ruido puro**, y el veto relativo al `v3` congelado no lo para si `v3` también dispara sobre entradas raras. *Cambio mínimo:* «detectado» = mayoría estricta (k = 2 → 2/2, k = 3 → 2/3, k = 4 → 3/4); se publica la macro nula bajo q̂ (tasa de disparo del agente sobre los limpios perturbados) con la distribución empírica de k; el negativo es «no supera el nulo por permutación de veredictos entre instancias al 5 %», y el 25 % queda como suelo absoluto adicional. Todo se preinscribe como procedimiento; el número sale de los datos.

**k por replay, no por recurrencia.** El k emergente será de cola pesada hacia el singleton: lo raro aparece una vez. §8 ya aparta los singletons, lo que deja el primario sobre los fallos regulares, que son los ruidosos. La forma honesta de subir k sin declarar nada: **replicar** cada candidato r veces con la misma perturbación y el contexto irrelevante variado (MSH-10, paciente); k = reproducciones; lo que no reproduce va a un estrato «no reproducible». Lo mismo arregla el punto 4 de §6: con k = 2 el autor ve las dos instancias y no hay fuera de muestra; con k = 3 es cara o cruz; hace falta k ≥ 4.

**Varianza del agente.** La intra-tipo de 0,057 de la Fase 12 no es despreciable con k = 2–3. Si el agente es estocástico, preinscribir r corridas por instancia con voto mayoritario y publicar las r: sigue siendo un protocolo y una pasada.

**N₁ vale también para el subconjunto del residuo**, o la nota de portada será sobre dos tipos.

---

## 6. Lo barato que falta o que sobra

**Falta**, todo a coste cero o sobre el piloto:

| paso | qué | cuándo |
|---|---|---|
| 0a | **Bundle** idéntico para todos los brazos, definido y sellado | hoy |
| 0b | **Tipo** = (cláusula, síntoma, mecanismo), sellado; familia como descriptor | hoy |
| 0c | **Limpios de B** de la misma distribución perturbada, emparejados por familia | hoy |
| 0d | **Clase de regla** C y tiempo T del autor de la actualizada | hoy |
| 0e | Anclajes del negativo, N₁ derivado, mayoría estricta, nulo por permutación | hoy, antes del piloto |
| 0f | **Clasificar los diez** de §2 en E1/E2/E3 con el bundle de 0a | hoy, una hora |
| 0g | **Descomponer el prompt** por origen; tabla relación ↔ prompt | hoy, una hora |
| 1' | Relaciones por dos autores, uno ciego al prompt, con cláusula cada una; oráculos de tercero (d); determinismo/replay (e) | antes del piloto |
| 2' | Sellar configuración y semillas de la capa; contar iteraciones | antes del piloto |
| 3' | Sobre el piloto: AUC del adversario de rareza; cobertura de los aciertos (b) por solo-contrato; control positivo con los diez si siguen presentes; κ de tipo; disparo por prompt sobre limpios | piloto |

**Sobra:** nada que quitar. El paso 4 (inductor) está fuera del camino crítico y puede ir después del 6; el κ del paso 5 solo se puede calcular con candidatos del piloto, así que su sitio es 3'.

**El que más probablemente la mata, y sí se adelanta al primer puesto:** que todos los silenciosos del piloto sean E1 —cubiertos por el `diff` de referencia— y el residuo salga vacío, dejando el diseño tal como está sin número en portada. Su prueba definitiva necesita el piloto (3'), pero su **prior** se obtiene hoy con 0f: si los diez son E1/E3, se reescribe §6 antes de montar la capa, no después de pagar al curador. Segundo: F8, el AUC de rareza (3'). Tercero: F9, el κ de tipo. Los tres son anteriores a contratar a nadie, que era la condición del encargo.

---

## Lo que pido, y para qué

1. **Configuración exacta del «agente congelado»** (con herramientas o modo techo; qué recibe, byte a byte) y **el bundle de cada brazo** — para juzgar la simetría de evidencia, el desajuste de modo (§4) y qué cae en E3.
2. **Qué emite el agente** (binario; clase; texto con localización) y **qué compara el puntuador** — para saber si el puntuador es un mando (una clase forzada sobre tipos nuevos lo es) y si «detección por la razón equivocada» cuenta.
3. **Qué es `ideal_b`** (plantilla por clase o valor por instancia) — si es por instancia, el orden de §9 («antes de curar») es imposible.
4. **Cuáles de los diez de §2 siguen en el circuito congelado** — si alguno sigue, es control positivo del oráculo (2f); si todos están arreglados, el estrato F4 está vacío por construcción y la preocupación real es solo el prompt.
5. **Recuento de caracteres del prompt por origen** (contrato / lecciones de A / lecciones de los diez / few-shot / procedimiento), no el prompt — para §4 y F7.
6. **Si los 326 ficheros reales se usaron en A o en el afinado** — contaminación de la familia «corpus real», que es la única sin el confundente de rareza y por tanto la más valiosa.
7. **La nota del agente sobre los dos operadores que `v3` falló en la Fase 12** — §1 dice que «el modelo gana donde falla el escritor automático» ya se sabía; con esos dos números se sabe si se sabía o si se refutó.
8. **Qué puede `v3-invariante`** (solo regex, o parsea y normaliza) — para leer su cobertura de los aciertos (b) como prueba de F3 o solo como cota inferior.
9. **La escala de la nota** (qué significa +0,875; cómo penaliza las falsas alarmas) — para el nulo de §5.

---

## Cambios mínimos, en una tabla

| rotura | cambio mínimo |
|---|---|
| 0.1 residuo = rotura 1 de la v1 | primario único: §3 a exposición cero; residuo a descriptivo con κ, residuo medido y clasificación R1/R2; sube a portada solo si el piloto muestra E2 ≠ ∅ |
| 0.2 E3 no rescata; E2 sin evidencia | clasificar los diez hoy; cobertura solo-contrato de los aciertos (b) del piloto; cajón de disputados como estrato secundario puntuado |
| F7 autor compartido | segundo autor de relaciones ciego al prompt; cláusula por relación; tabla de solapamiento; estratificar por «nombrada en el prompt»; capa sellada con semillas; κ puntuador/lector; curador sobre el bundle sin relaciones ni etiqueta de perturbación |
| F8 rareza | limpios de B perturbados por familia; AUC del adversario de rareza; techo absoluto de FA; localización en la respuesta |
| F9 tipo indefinido | tipo = (cláusula, síntoma, mecanismo); κ de tipo |
| (a) no es sin oráculo | predicados explícitos sellados; primario por vía; `v3` congelado sobre aciertos (a) |
| (c) no acota al 1 % | precisión sobre aciertos + cota 3/n con esas palabras; curador (c) sin relaciones; κ sobre conjunto enriquecido |
| 25 % no es nulo | mayoría estricta; nulo por permutación bajo q̂; N₁ derivado de anclajes fijados antes del piloto |
| k emergente | replay r veces con contexto irrelevante variado; estrato «no reproducible»; r corridas del agente si es estocástico |
| orden §9 | 5 y 6 delante de 2; presupuesto de ejecuciones como regla de parada; iteraciones contadas |
