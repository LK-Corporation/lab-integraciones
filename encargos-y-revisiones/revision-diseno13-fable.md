# Revisión externa del diseño v1 de la Fase 13 — Fable, 22-sep-2026

**Leído:** `encargo_diseno13.md` (con el diseño entero) y `PRE-TEST.md` de la Fase 12. Nada más,
por control de contaminación: no he visto el catálogo, las tablas de casos, el afinado, el agente,
el `triador_regex_v3.py` ni el inductor, que aún no existe. Todo lo que digo sale de esos dos
ficheros y de los números que traen.

---

## 0. Veredicto en cinco líneas

1. **El modo de fallo que la §5 no nombra: el oráculo de mecanicidad es un detector, y el diseño
   estratifica el resultado de los detectores por el resultado de un detector.** «El modelo gana en
   el cuartil no mecánico» se traduce a «el modelo gana donde falla un escritor de reglas
   automático», que ya se sabe desde la Fase 12 (bate al regex v1, +0,557). Es condicionar en el
   desenlace del comparador, disfrazado de covariable. Se destapa la semana 1, sobre A, sin agente.
2. **Q2, tal como está redactada, está vacía con un B declarado.** Todo tipo definido por una
   función de mutación admite una regla estática: la función leída al revés, proyectada sobre la
   traza. La regla actualizada, que ve B, llega al 100 % de lo observable por construcción, igual
   que el v3 llegó en A. El DiD de Q2 sale negativo antes de correr nada. Lo que el diseño llama
   Q2 es un **coste**, no una capacidad.
3. **El DiD de Q1 sale positivo antes de correr nada** si B es novedoso, y la corrección de la
   §5.2 (pedir más tipos hasta que baje el solapamiento) lo infla: selecciona el banco contra el
   comparador. La Fase 12 tuvo un total que escondía; ésta tiene un DiD que fabrica.
4. **N = 30 aguanta el contraste global al límite y no aguanta los cuartiles**, que son «donde
   vive la respuesta». Con 7-8 tipos por cuartil y un brazo binario, el DiD por cuartil lleva un
   intervalo de ±0,4. No mide nada.
5. **Hay una forma mejor con este mismo laboratorio y cuesta una tarde de reescritura** (§7.1):
   curva de exposición del autor de reglas contra el modelo congelado, todo fuera de muestra,
   covariables a priori en vez de cuartiles de inductor, y Q2 reducida a lo único que puede ser.
   Y hay una que cierra la deuda de verdad y es más cara (§7.2): un B que **emerja** en vez de
   **declararse**.

---

## 1. El modo de fallo que la §5 no nombra

### 1.1 El oráculo es un brazo

El diseño usa el inductor para dos cosas: es el **cuarto brazo** («el suelo automático», §4) y es
el **eje de estratificación** («la pregunta se contesta dentro de cada cuartil», §3). Es el mismo
programa. Su salida por tipo —«encuentra regla» / «no la encuentra»— es un resultado de detección.
Agrupar los tipos por ese resultado y preguntar en qué grupo el modelo bate a la regla es preguntar
**si el modelo bate a la regla allí donde un escritor de reglas automático falla.** Hay dos casos y
los dos vienen decididos:

- **El inductor es más flojo que el autor humano de la regla actualizada** (lo probable: un diff
  sintáctico contra una persona con el v3 y B delante). Entonces el «cuartil no mecánico» son
  tipos que el inductor no pilla pero el humano quizá sí. Que el modelo bata ahí a la regla
  **congelada** está garantizado (la congelada vale ≈ 0 en tipos nuevos). Que bata a la
  **actualizada** es imposible en tipos observables (la actualizada vale ≈ 1, §1.2). No hay
  resultado posible que no se supiera antes.
- **El inductor es tan fuerte como el humano.** Entonces «no mecánico» = «tipos donde la regla
  actualizada falla» = condicionar en el fracaso del comparador. «El tratamiento gana en el
  subgrupo donde falló el control» es el artefacto de subgrupo post hoc de manual.

El argumento del panel para el inductor era «no depende de nada mío». Es verdad que no depende del
**autor** de las reglas. Depende de la **tarea** de escribir reglas, que es justo lo que se compara.
Una covariable que es función del desenlace de uno de los brazos no es una covariable.

### 1.2 Q2 está vacía con un B declarado

Q2 pregunta si el modelo detecta «cosas para las que no se puede escribir una regla estática».
Para un tipo definido por una función de mutación, la respuesta es **siempre sí se puede**: la
función de mutación *es* la regla, leída al revés y restringida a lo que la traza expone. El único
«no» es el tipo no observable, donde no detecta nadie (H3 lo confirmó). Es exactamente el
mecanismo por el que el v3 llegó al 100 % de lo observable en A, y no depende de quién escriba la
mutación ni de si la ve o no el adversario congelado: depende de que la regla actualizada **ve B**.

Consecuencias:

- La regla actualizada sobre B observable vale ≈ 1 por construcción. DiD_Q2 < 0 antes de la
  pasada.
- «Detecciones propias del modelo» contra la actualizada (§6, desglose 5, «el número más honesto y
  va en portada») vale **0 por construcción**. Está muerto antes de nacer.
- El revisor que dijo *«actualizo el script y vuelve a ganar»* tenía razón, y la respuesta del
  diseño —medirlo aparte— no cambia que vaya a ganar.

Lo que **sí** varía entre tipos es el **coste** de la regla: un regex sobre un campo, una
comprobación de longitud, un léxico de nombres, una comparación contra la entrada, estado entre
mensajes, un registro externo. Ese coste es el eje real, y el diseño **no lo registra**. Q2 es en
realidad Q3: «¿qué cuesta ponerse al día?». Es una pregunta buena. No es una pregunta de capacidad.

Lo único de Q2 que sobrevive es la **detección a primera ocurrencia**: ¿pilla el modelo, sin haber
visto nunca el tipo, un fallo que nadie le describió? Eso es la nota absoluta del modelo sobre B a
exposición cero, con su tasa de falsas alarmas. **No tiene comparador de reglas**: la congelada no
anticipa por definición y la actualizada ya lo ha visto. Es H4 sobre B, y va sola.

### 1.3 La corrección de la §5.2 selecciona B contra el comparador

```
DiD_Q1 = [ S_m(B) − S_cong(B) ] − [ S_m(A) − S_cong(A) ]
```

El término de A vale ≈ −0,27 (macro por tipo 0,597 − 0,889; en totales −0,244). Luego DiD_Q1 > 0
si y solo si **S_m(B) > S_cong(B) − 0,27**. Y S_cong(B) es, por construcción, el solapamiento con
A: una regla congelada solo pilla tipos nuevos por coincidencia de firma. Tabla:

| solapamiento (= S_cong(B)) | S_m(B) mínimo para que DiD_Q1 > 0 |
|---|---|
| 0,6 | 0,33 |
| 0,4 | 0,13 |
| 0,2 | −0,07 |

Con solapamiento bajo el modelo gana **respirando**. La magnitud de DiD_Q1 es (1 − solapamiento) +
ruido: una medida de la novedad de B, decidida en el paso de selección, reportada como efecto del
modelo. Y el procedimiento de la §5.2 —«si el solapamiento es alto, pedir más tipos»— **empuja el
solapamiento hacia abajo**, o sea, empuja el endpoint hacia arriba. Es el mismo error que ajustar
el banco contra el adversario, con signo contrario al de la Fase 12.

Además «necesitamos N más, sin decir por qué» no es practicable (§3): tras entregar 30 y que le
pidan 10, cualquier autor competente deduce que se han rechazado y cambia de estrategia. La segunda
tanda será sistemáticamente más exótica que la primera: un efecto de lote correlacionado con la
novedad, que es justo la covariable que interesa.

### 1.4 La medida barata de la semana 1

Tres números sobre A, sin agente y sin B:

1. **Concordancia inductor ↔ regex v3, tipo a tipo, sobre A** (los 18 del reservado o los 63
   operadores): κ de Cohen entre «inducible» y «lo cubre el v3». Si κ > 0,6, el estratificador
   **es** el comparador y la §6.2 está muerta tal como está escrita.
2. **Recall del inductor sobre A contra lo que cubre el v3** (16 de 18 observables a 8/8). Si el
   inductor encuentra regla para menos tipos que el v3, «no mecánico» significa «mi inductor es
   flojo» —la duda que el propio encargo plantea— y ahora con número.
3. **Control negativo del endpoint**: la tabla de arriba, extendida a 3×3 (solapamiento ×
   S_m(B)), en la preinscripción. Si no hay ninguna celda plausible en la que DiD_Q1 salga
   negativo, el endpoint no puede fallar y por tanto no es un endpoint. Es el mismo criterio que se
   aplica a un aparato de medida: antes de usarlo, enseñar que puede dar cero.

Y la cara humana del mismo modo de fallo: tras una Fase 12 negativa, **cada mando discrecional del
diseño tiene una dirección que favorece al modelo** —la fuerza del inductor, los puntos de corte de
los cuartiles, la selección de B por solapamiento, `ideal_b`, cuál de los dos DiD es «el
primario»—. La protección de la Fase 12 fue predecir el propio fracaso. La Fase 13 no tiene
equivalente. Hay que escribir ahora, en números, **el resultado que significaría «el modelo tampoco
aporta en tipos nuevos»**, y firmarlo antes de que exista B.

---

## 2. El oráculo de mecanicidad: qué lo rompe al escribirlo

No es una idea bonita imposible. Es una idea bonita que, escrita tal cual, mide otra cosa. Seis
sitios donde se rompe:

1. **Pares contra sueltos.** El inductor aprende de pares (limpia, mutada); los brazos ven **una**
   traza sin gemela limpia. Una regla inducida del diff («el campo X cambió») no es un detector; un
   detector necesita un predicado absoluto («X cumple P / X falta / cuenta = 2»). Los tipos de
   **desplazamiento de valor** —una fecha válida pero equivocada, un identificador plausible pero
   de otro paciente— son trivialmente separables por pares y **no expresables** como regla sobre
   una traza suelta salvo que la traza incluya la entrada. El oráculo por pares los llamará
   «mecánicos» mientras ningún brazo puede pillarlos. Arreglo: el inductor emite predicados sobre
   una traza y se evalúa sobre trazas sueltas; y el diseño dice por escrito si la entrada está en
   la traza, porque de eso depende qué es «regla estática» en este banco.
2. **k = 5 satura cualquier aprendiz.** Cinco positivos y sus cinco gemelas limpias son separables
   por *alguna* característica casi siempre. En muestra, el inductor encontrará «regla» para todo
   tipo observable → todo B es mecánico → la §5.1 dispara por construcción y sería un artefacto.
   Arreglo: dejar-uno-fuera dentro del tipo (regla inducida de 4 casos debe pillar el 5.º) y, más
   duro, dejar-un-tipo-fuera (que es la medida de solapamiento de la §5.2, bien hecha).
3. **El conjunto negativo.** Sin limpios **y** sin los demás tipos como negativos, el discriminador
   «cualquier cosa distinta de mi gemela limpia» es perfecto y dispara en todo. La tasa de falsas
   alarmas del inductor sobre limpios de B se reporta como la de cualquier brazo.
4. **El espacio de hipótesis es el eje.** Diff de tokens / regex por campo / longitud y numérico /
   cruce de campos / léxico: cada peldaño reclasifica tipos. No existe «la mecanicidad»; existe
   «inducible en el peldaño r». Arreglo: la **escalera**, reportada por tipo como el peldaño más
   bajo que lo pilla fuera de muestra. Es un ordinal, es descriptivo, y es el patrón que este
   laboratorio ya usa.
5. **Calibración.** Antes de tocar B, el inductor tiene que reproducir la cobertura del v3 sobre A.
   Si no lo hace, es más flojo que el humano y su «no hay regla» no se interpreta. Es la medida 2
   de la §1.4.
6. **No observable ≠ no mecánico.** Los tipos cuya traza no difiere de la limpia hay que apartarlos
   **antes** de agrupar. Si no, el «cuartil no mecánico» se llena de tipos que nadie puede detectar,
   los dos brazos puntúan 0 ahí, y la conclusión es «el modelo no gana ni donde fallan las reglas»:
   un falso negativo por confusión de etiquetas.

### Lo que sí es implementable y útil

Partir el «oráculo» en cuatro instrumentos que el diseño confunde:

| instrumento | qué mide | cómo | depende de un detector |
|---|---|---|---|
| **observabilidad** | ¿difiere la traza mutada de la limpia? | automático, diff de traza | no |
| **distancia al catálogo** | ¿qué campos/segmentos toca la mutación, y cuánto se solapan con los que tocan los 63 de A? | Jaccard sobre huella de la función de mutación, sin correr nada | no |
| **conocimiento necesario** | estructura/valor; válido/inválido según spec; necesita la entrada; necesita léxico o mundo; necesita estado entre mensajes; necesita contexto externo | rúbrica codificada a ciegas por **dos** personas desde la descripción del tipo, con acuerdo reportado | no |
| **escalera de inducción** | peldaño más bajo en que una regla inducida lo pilla fuera de muestra | inductor calibrado en A | **sí** |

Los tres primeros son covariables legítimas: se calculan antes de que corra ningún brazo y no
dependen de que nadie acierte. El cuarto vale como **descriptor** y como **brazo suelo** (fuera de
muestra), y **nunca como estratificador del primario**. La observabilidad, además, debe **derivar**
`ideal_b` para B por regla (NO_SE aceptable ⇔ traza sin diferencia), en vez de marcarlo a mano
caso a caso.

---

## 3. ¿Correcciones reales o tapadas?

**Q1 frente a Q2 (§2).** Separadas de nombre; comparten B, brazo modelo, puntuador y forma del
DiD. El DiD de Q1 es tautológicamente positivo y el de Q2 tautológicamente negativo (§1). Y Q1
contamina Q2 en el relato: el informe abrirá con «el modelo degrada menos que las reglas
congeladas» —verdadero y vacío— y se leerá como capacidad. La separación es real solo si las dos
preguntas reciben **estadísticos distintos**: Q1 → curva de exposición y coste por unidad de
cobertura; Q2 → detección absoluta a primera ocurrencia con veto de falsas alarmas y sin
comparador de reglas.

**Pendiente frente a cuartiles.** La §2 acepta «medir la pendiente de degradación por distancia al
catálogo». La §6.2 implementa cuartiles de un inductor. **La corrección es nominal.** La pendiente
se implementa así: por tipo, d_t = nota_modelo − nota_regla, contra una covariable continua y libre
de desenlace (distancia Jaccard; rúbrica), N puntos, correlación de rangos con intervalo. Sin
agrupar.

**Solapamiento A↔B (§5.2).** No es practicable como está (§1.3). Y aunque lo fuera, seleccionar B
por solapamiento sesga Q1. Arreglo: sobre-encargar **una vez** (50 tipos), decir la verdad al autor
—«usaremos un subconjunto elegido por un criterio preinscrito que no necesitas conocer»—, y **no
seleccionar por solapamiento**: reportarlo como covariable. Sobre-encargar hace falta de todas
formas, porque el circuito reclasificará como ruidosos o no observables parte de los tipos que el
autor declare silenciosos (§5).

**La regla actualizada ve B.** Es el conjunto de prueba usado como conjunto de entrenamiento del
comparador. En la Fase 12 el adversario en muestra se defendió como **suelo**: solo sube la barra,
conservador. En la Fase 13 es el **comparador del endpoint primario**: el ajuste en muestra sesga
el endpoint, no un suelo. Y el endpoint compara la nota **de prueba** del modelo con la nota **de
entrenamiento** de la regla. Arreglo: el autor ve un subconjunto preinscrito de tipos; todos los
brazos se puntúan sobre el resto.

**Asimetría de información.** El modelo está congelado sobre A; la regla actualizada está ajustada
sobre A ∪ B. El modelo solo «gana» Q2 si pilla un tipo observable para el que una persona, con el
tipo delante, no supo escribir regla. No va a pasar. O se da a los dos brazos la misma exposición
(descripciones de tipos en el prompt ↔ las mismas descripciones al autor, ambos fuera de muestra),
o no se llama capacidad a la comparación.

---

## 4. El endpoint: la trampa propia del DiD

**No está identificado.** Un DiD supone que la brecha modelo−regla sería la misma en B que en A si
B no fuera novedoso (tendencias paralelas). B difiere de A en composición **por construcción**:
otro autor, otra mezcla de observabilidad, otra mezcla de clases. El supuesto falla por diseño; el
DiD mezcla novedad con composición y no separa las dos.

**Q1 positivo por construcción, Q2 negativo por construcción** (§1.2, §1.3). Ninguno de los dos
puede dar el resultado contrario bajo ningún escenario plausible. Un endpoint que no puede fallar
no es un endpoint.

**Escala acotada y no lineal.** Diferencias de diferencias de macros con θ y K sobre conjuntos de
tipos distintos y mezclas distintas no son tamaños de efecto. El modelo mixto que propone la §7 es
mejor que el DiD a mano —pero con 7-8 tipos por estrato y un brazo de resultado bipuntual, sus
supuestos no se sostienen; una prueba pareada por tipo (signo / Wilcoxon) es más honesta y no
necesita nada que no se tenga.

**¿Qué A?** El término de A tiene que ser el reservado (18 tipos), no los 63 ni el desarrollo,
donde la regla y el prompt están en muestra. Debe decirse. Y **la regla actualizada tiene que
correr también sobre A**: las reglas nuevas pueden romper cobertura de A o disparar sobre limpios
de A. S_act(A) − S_cong(A) es el coste de la actualización hecho visible, y el diseño no dice que
se calcule.

**¿Bastan los cinco desgloses?** No:

- El **desglose 2** (DiD por cuartil) es la trampa misma: circular (§1.1) y sin potencia (§5).
- El **desglose 5** (detecciones propias) vale 0 por construcción contra una actualizada en
  muestra (§1.2). Solo tiene sentido contra una regla fuera de muestra.
- Ninguno de los cinco detecta que DiD_Q1 es positivo por construcción. Eso lo detecta el control
  negativo del endpoint (§1.4, medida 3), que no está.
- Los desglos 1, 3 y 4 están bien y se quedan.

**Primario que propongo:** diferencia pareada por tipo, modelo − regla_e, sobre los tipos **no
vistos** por el autor de reglas a exposición e; Wilcoxon/signo sobre N pares; veto por falsas
alarmas; detecciones propias contadas contra regla_e. Reportado para cada e (§7.1).

---

## 5. El tamaño

La tabla de varianzas de la §7 es correcta y su consecuencia («toda la potencia viene de N») es
correcta. El diseño no la lleva hasta los cuartiles. Números:

- **Regla, binaria por tipo.** A p ≈ 0,5 sobre 30 tipos, EE 0,09. Sobre 7-8, EE 0,18.
- **Modelo.** Desviación entre tipos 0,43 → EE 0,08 sobre 30; 0,16 sobre 7-8.
- **Diferencia pareada por tipo**, DE ≈ 0,5 → EE 0,09 sobre 30, IC ±0,18. Wilcoxon con 30
  pares: ~70-75 % de potencia para una ventaja media por tipo de 0,25; ~86 % con N = 40.
- **El DiD** añade el término de A (18 tipos, EE ≈ 0,12): IC ≈ ±0,30. Un DiD de 0,2 es ruido.
- **Cuartiles de 7-8.** Resolución de la nota de la regla: 1/7. IC del DiD por cuartil ≈ ±0,4.
  Potencia para una diferencia de 0,25 entre cuartiles: ~20 %. Y si la nota del inductor es
  bimodal —inducible / no, que es lo que k = 5 va a dar—, dos cuartiles son idénticos y los cortes
  son arbitrarios. **El análisis «que importa» no tiene potencia con ningún N razonable; hay que
  sustituirlo, no agrandarlo.**
- **Pendiente** d_t contra covariable continua: ρ = 0,4 tiene ~60 % de potencia con N = 30, ~75 %
  con 40, ~85 % con 50.
- **k = 5.** Bien para la media por tipo del modelo (EE 0,2); k no compra nada para la regla, de
  acuerdo. Con una salvedad: si las funciones de mutación admiten parámetros (§6, punto sobre
  determinismo), k = 5 no caracteriza un tipo y la tabla hay que rehacerla.
- **Limpios.** «En proporción» no es un número. 0/22 en la Fase 12 acota las falsas alarmas al
  13 % (95 %). Para que el veto muerda: ≥ 60 limpios (cota 5 %), mejor 100 (3 %), **pareados con
  los mensajes base de B** y salidos del mismo generador que A, no aportados por el autor.
- **Sobre-encargar.** El autor declara «silencioso»; el circuito decide. Parte saldrán ruidosos
  (`FALLO_MENSAJE`) y parte no observables. Para acabar con ≥ 30 —mejor 40— silenciosos
  observables, encargar 50.

**Recomendación:** N ≥ 40 tipos silenciosos observables para el primario; cuartiles fuera;
covariables continuas; 50 encargados; ≥ 60 limpios pareados.

---

## 6. Otros agujeros con arreglo barato

- **La clave de B y `ideal_b`: quién y cuándo.** El diseño no lo dice. Debe ser: el autor ciego
  declara la clase esperada por tipo; `comparar.py` la confirma mecánicamente contra lo que el
  circuito hace; los desacuerdos se resuelven por una **regla preinscrita** (el comportamiento
  observado manda) **antes** de que corra ningún brazo; `ideal_b` se deriva por regla de la
  observabilidad, no a mano. Sellado con huella como en la Fase 12 §7, y las 16 autopruebas del
  puntuador re-ejecutadas con la clave de B.
- **Determinismo de las funciones de mutación.** El diseño no dice si el autor puede entregar
  funciones con parámetros libres (qué campo, qué valor, de dónde). Si son deterministas, §1.2
  aplica entera. Si son familias parametrizadas, la regla ya no cubre el tipo de forma binaria
  —cubre instancias—, la varianza intra-tipo de la regla deja de ser 0, la tabla de tamaño cambia,
  y k = 5 tiene que muestrear la familia. Hay que decidirlo y escribirlo. Mi recomendación va en
  §7.1: familias con ≥ 2 parámetros libres, porque es la forma barata de que un B declarado sea
  menos invertible.
- **Arnés en seco sobre B.** Un agente nulo (llama una vez a cada herramienta y devuelve `NO_SE`)
  sobre todos los casos de B, la semana en que llegue. Comprueba que la capa de herramientas
  sobrevive a formas de traza que A nunca produjo (dos mensajes de salida, ninguno, timeout, caída)
  y da el suelo «siempre NO_SE» para B. Si el brazo modelo cae en B por ingeniería —excepciones,
  parseo, la puerta de orden rechazando llamadas—, el DiD lo llamará capacidad.
- **Los mismos bytes para los dos brazos, re-verificado en B.** La Fase 12 lo afirmó para A. Tipos
  de B pueden producir contenido en `log()` que los campos `medido_*` / `can_*` no llevan. Si el
  agente lee texto libre que el regex no parsea, una victoria del modelo en B es una asimetría de
  información. Medida: por caso, tokens en lo que recibe el agente que no están en lo que recibe
  el regex; cero o declarado.
- **Registro de coste del autor de la regla actualizada.** Minutos por tipo, líneas por tipo,
  recursos (léxico, acceso a la entrada, estado). Gratis de recoger y es **el dato de Q1**.
- **Quién es el autor ciego.** Si es un LLM: (a) su prior sobre «qué falla en ADT^A01→Patient» es
  el de cualquier autor competente → solapamiento alto con A es el resultado esperado, no un
  riesgo; (b) si es de la misma familia que el agente, **el autor y el detector comparten prior
  sobre tipos de fallo y el autor de reglas no** — una asimetría a favor del modelo que no tiene
  nada que ver con capacidad. Otra familia, o una persona, y decir cuál.
- **Contexto del autor: «el circuito y el contrato».** Si «circuito» incluye el código de la
  transformación, el autor mutará por ramas del código, que es lo que hizo el autor de A →
  solapamiento. Si incluye la instrumentación del arnés, el autor apuntará a lo que se mide →
  sesgo hacia lo observable y mecánico. Dar: contrato (spec, perfiles, mapeo), mensajes de muestra,
  y una forma de ejecutar un caso. Ni el código ni el arnés.
- **¿El prompt congelado (`89ae1c8d`) enumera tipos de fallo de A?** No lo he visto ni debo. Si lo
  hace, el brazo modelo es «un LLM con el catálogo de A en el prompt» y su degradación en B es el
  mismo fenómeno que el de la regla congelada. Decirlo en el informe en cualquiera de los dos
  casos.
- **El brazo inductor, si induce sobre B y se puntúa sobre B, está en muestra.** Solo fuera de
  muestra.
- **Estrato de fallos reales (§8).** Bien aparte. Pero conviene notar lo que dice de este
  laboratorio: es el **único conjunto de fallos no declarados que existe**, y es el que produjo los
  bugs de verdad. Ver §7.2.

---

## 7. Lo que haría distinto

### 7.1 Reescritura mínima (una tarde), mismo laboratorio, mismo presupuesto

1. **Encargar 50 tipos a ciegas**, contexto = contrato + muestras + ejecutor. El autor declara la
   clase esperada; el circuito adjudica por regla; se quedan los ≥ 40 silenciosos observables.
   **Sin selección por solapamiento.** Pedir familias con ≥ 2 parámetros libres; k = 5 instancias
   muestreadas de la familia.
2. **Partición aleatoria preinscrita de B en bloques.** El autor de reglas (ciego al agente) recibe
   bloques acumulativos: exposición 0 (= v3 congelado), 10 tipos, 20 tipos. Dentro de cada tipo
   visto, ve solo 2 de las 5 instancias. Cada versión del script con huella. Registra coste por
   tipo. Orden aleatorio preinscrito; si hay dos autores, órdenes inversos.
3. **Todos los brazos se puntúan sobre lo no visto** en cada exposición: tipos no vistos (¿anticipa
   la regla tipos nuevos?) e instancias no vistas de tipos vistos (¿generaliza dentro de la
   familia?). Dos números fuera de muestra por exposición. El modelo: **una** pasada, ~200 casos +
   ≥ 60 limpios. El presupuesto de agente es el mismo que el del diseño.
4. **Primario:** diferencia pareada por tipo modelo − regla_e sobre tipos no vistos, e ∈ {0, 10,
   20}; signo/Wilcoxon; veto por falsas alarmas; detecciones propias contra regla_e. La curva
   «nota fuera de muestra de la regla contra tipos vistos» **es** la respuesta a Q1 (coste
   marginal de cobertura); la línea plana del modelo se pone al lado. Si la curva de la regla sube
   deprisa, las reglas generalizan y el modelo sobra; si es plana en el solapamiento, cada tipo
   nuevo cuesta una regla y el modelo tiene un sitio.
5. **Q2, reescrita:** detección absoluta del modelo a exposición 0 sobre tipos observables nuevos,
   con falsas alarmas, y la lista nominal de tipos pillados a primera ocurrencia. Sin comparador de
   reglas; la nota del v3 congelado sobre B se reporta como comprobación de novedad, no se resta.
6. **Covariables libres de desenlace:** observabilidad (automática), distancia Jaccard a A
   (automática), rúbrica de conocimiento (dos codificadores ciegos). d_t contra cada una, con
   correlación de rangos e intervalo. Sin cuartiles.
7. **Inductor:** escalera como descriptor y brazo suelo fuera de muestra; calibrado en A antes de
   ver B; **nunca** estratifica el primario.
8. **El negativo, escrito ahora**, por ejemplo: «si a exposición 0 la ventaja media por tipo del
   modelo sobre el v3 en tipos observables nuevos es < 0,15, o sus falsas alarmas en limpios de B
   superan las del v3, el modelo tampoco aporta en tipos nuevos». Los números que se decidan, pero
   firmados antes de B.

### 7.2 La que cierra la deuda: B por emergencia, no por declaración

Cualquier tipo declarado —por un autor ciego o no— es una función que se puede invertir. Los únicos
fallos de este laboratorio que **no** eran invertibles el primer día son los ocho o diez de la §8, y
salieron de **ejecutar** el sistema, no de escribir operadores. Construir B con ese proceso: una
capa de perturbación que el autor del laboratorio **no controla** —fuzzing a nivel de transporte y
codificación, corpus de mensajes reales con sus irregularidades naturales, carga y concurrencia,
desajustes de versión y de perfil—, ejecutada por una persona externa que **cura** lo que falla en
silencio, lo etiqueta y lo sella. El autor del laboratorio ve B después de la pasada.

Coste: la capa de perturbación (días, no semanas; buena parte es fuzzing de estantería) y el tiempo
de etiquetado del curador externo, con la dificultad real de adjudicar la clase esperada de un
fallo que nadie diseñó. Ganancia: un B cuyos tipos nadie escribió, de modo que «el modelo lo pilla
a primera ocurrencia» significa lo que dice. Si no cabe en esta fase, en la siguiente; pero el
informe de la Fase 13 tiene que decir con estas palabras que **un B declarado contesta coste, no
capacidad.**

### 7.3 Lo que no tocaría

El orden de la §9; la prohibición del agregado de la §6; los desgloses 1, 3 y 4; las detecciones
propias en portada (contra una regla fuera de muestra); el estrato de fallos reales aparte (hasta
§7.2); la varianza medida y no supuesta; «si el autor no puede producir N, eso es un resultado» —
con la salvedad de que es un resultado sobre la **declaración**, no sobre el dominio.

---

## 8. Lista de la semana 1 (sin agente, sin B)

- [ ] Inductor calibrado en A: recall contra la cobertura del v3; κ inductor↔v3 por tipo.
- [ ] Control negativo del endpoint: tabla 3×3 DiD_Q1(solapamiento, S_m(B)). Si ninguna celda es
      negativa, el endpoint se sustituye.
- [ ] Regla de `ideal_b` para B escrita y con huella; regla de adjudicación clase declarada /
      clase observada escrita y con huella.
- [ ] Agente nulo sobre el arnés en A (y sobre B cuando llegue).
- [ ] Script de «mismos bytes» listo.
- [ ] Paquete de contexto del autor: contrato + muestras + ejecutor; ni código ni arnés. Identidad
      del autor y, si es un modelo, su familia, registradas.
- [ ] Plantilla de registro de coste del autor de reglas.
- [ ] Decisión escrita: funciones deterministas o familias parametrizadas.
- [ ] El negativo, en números, firmado.
