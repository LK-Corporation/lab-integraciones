# Fase 13 — Diseño, v3 (22-sep-2026). B por emergencia, con el endpoint arreglado

**Estado: BORRADOR. No se monta nada hasta firmar 🧑 y hasta que el paso 0 —la auditoría de
contaminación y simetría— salga limpio.**

Escrita con las cuatro revisiones externas de la segunda ronda delante (`revision-diseno13b-*.md`:
Gemini, Opus, GPT y DeepSeek, sobre `encargo_diseno13b.md`).

**Lo que cambia, en una frase: el primario de la v2 estaba roto, y era la rotura de la v1 por otra
puerta.** Los cuatro revisores abrieron por ahí antes de contestar nada.

Convención: 📏 sale de una medida, 🔍 de una revisión externa, 🧑 lo decide Víctor.

---

## 1. La rotura que mató a la v2, y por qué es la misma de siempre

La v2 ponía como primario **la nota del agente sobre el residuo**: el subconjunto que el autor de la
regla actualizada declarara no poder cubrir con una regla estática.

🔍 **Los cuatro, por separado:** el residuo está definido por **la incapacidad del brazo
comparador**. Medir al agente ahí es preguntar *«¿gana el modelo donde pierden las reglas?»* con el
conjunto **definido** como «donde pierden las reglas». Es condicionar en el desenlace del
comparador — literalmente la rotura 1 de la v1, la que declaré muerta, reintroducida por la puerta
del endpoint.

Y encima por **declaración**, que añade un sesgo de incentivos que la v1 no tenía:

- 🔍 un autor terco o hábil declara residuo **cero** y el denominador desaparece;
- 🔍 un autor perezoso lo declara **enorme** y el agente parece un genio;
- 🔍 si el autor es **un modelo**, empeora en los cuatro informes: no se rinde nunca, produce una
  regla hiperespecífica sobreajustada a lo que ve, y su «no cubrible» significa «no se me ocurrió»
  —que correlaciona con la capacidad del modelo generador, no con la estructura del fallo.

**La declaración se sustituye por medida.** Es la misma cura que la Fase 12 aplicó a su total, y la
que la v2 aplicó al residuo sin darse cuenta de que lo dejaba a medias.

---

## 2. La pregunta, con el alcance corregido

🔍 GPT separa tres cosas que la v2 confundía:

1. **fallo emergente**: nadie escribió *esa manifestación concreta*;
2. **distribución de descubrimiento diseñada**: alguien eligió las perturbaciones, los parámetros,
   los presupuestos, las relaciones, los plazos y el criterio de entrada;
3. **fallo desconocido para el agente**: el agente no recibió información semánticamente
   equivalente durante su afinado.

**La emergencia resuelve parcialmente (1). No demuestra (3). Y deja (2) entera como sesgo.** Por
tanto la v2 prometía de más. Lo defendible es esto, y se escribe así en el informe:

> **¿Detecta el modelo congelado un fallo *no preespecificado individualmente*, descubierto bajo
> una *distribución de perturbaciones preinscrita*, con una tasa de falsas alarmas que no lo
> invalide?**

Para poder añadir «y que el agente nunca vio nada equivalente» hace falta **el paso 0** (§9). Sin
él, esa frase no se escribe.

---

## 3. Por qué sigue habiendo fase

Los únicos fallos de este laboratorio que **no** eran invertibles el primer día son los diez de la
bitácora, y ninguno salió de escribir operadores: salieron de **ejecutar el sistema** —mandando
mensajes, apagando FHIR, rompiendo una credencial, mandando ocho seguidos, reiniciando a mitad—.
Cinco de los diez son **silenciosos**: acusan `AA`, escriben algo, y lo escrito está mal.

🔍 DeepSeek corrige un supuesto de la v2 que hay que decir en voz alta: **«emergente» no implica «no
invertible»**. Un fallo no diseñado, una vez curado y con su traza delante, es un tipo definido por
sus rasgos observables; si la evidencia discriminante está en la traza, se le puede escribir una
regla *a posteriori*. **La emergencia no elimina la invertibilidad: la hace incierta.** Y eso basta,
porque convierte en **dato medido** lo que en la v1 era cierto por construcción.

---

## 4. Cómo se produce B

Cinco familias de perturbación sobre el circuito congelado (MLLP → ADT^A01 → FHIR Patient):
**transporte**, **codificación**, **gramática y perfil**, **carga y entorno**, **corpus real**.
Todas con sus parámetros, rangos y semillas dentro del manifiesto sellado (§5).

### 4.1 Las vías de entrada, ahora cinco, y ninguna se funde con otra

Para meter un fallo en B hay que **saber que es un fallo**, y **todo oráculo imprime su firma**. Se
declaran cinco vías; cada una publica **su proporción y su tasa de falsos positivos por separado**,
y **no se funden**.

| vía | qué ve | de quién es la firma |
|---|---|---|
| **(a) anomalía operacional** | caídas, cuelgues, resets, excepciones, acuses que no llegan, recursos que nunca se escriben, proceso fuera de orden | de nadie: no hay oráculo |
| **(b) invariante metamórfica** | violaciones de invariancias sacadas del estándar y del contrato | **mía** (la del contrato) |
| **(c) inspección humana sobre muestra** | cualquier cosa, incluido el silencio | del curador |
| **(d) diferencial contra implementación de referencia** | divergencia del `Patient` producido por el circuito y por un mapeador independiente (HAPI / LinuxForHealth) | **del mapeador de referencia — independiente de todos los brazos** |
| **(e) postcondición contractual por intervención causal** | provocar condiciones cuyo resultado el contrato especifica (rotar credencial → 401, apagar FHIR → `AE`, MSH-10 duplicado → rechazo) y comprobar el efecto | mía, y es la más declarada de todas |

🔍 **La (d) la proponen Gemini y Opus por separado, y es la que faltaba:** es la única que ve
**silencios sin imprimir firma mía**. Su límite, declarado: solo ve fallos donde la referencia
acierta y el circuito no; los bugs compartidos quedan invisibles. La (e) la propone DeepSeek.

🔍 **Y hay que corregir un argumento de la v2 que es falso.** Escribí que la cuota de (a) prueba que
B no es solo el contrato leído al revés. **No prueba nada:** (a) y (b) cubren conjuntos **casi
disjuntos**. (a) recoge ruido por definición y es **ciega a todos los silenciosos**, que son el
objeto de la fase. Una cuota alta de (a) solo prueba que hubo mucho ruido. La vía sin sesgo era
también la vía sin señal.

🔍 **Contabilidad de vías, o la proporción es manipulable** (DeepSeek): un fallo hallado por varias
vías **cuenta para todas**, y se publica la matriz vía × tipo, no un reparto.

### 4.2 Las invariantes no las escribe quien diseña la capa

🔍 DeepSeek: si las relaciones metamórficas las escribe la misma persona que diseñó la capa —y la
capa está en la §4 del documento, visible antes de redactarlas—, la distinción entre «invariante» y
«operador leído al revés» es **de intención, no de efecto**. Por tanto:

- las relaciones las escribe **quien no ve la capa**, o se derivan del estándar versionado con una
  herramienta independiente;
- se **sellan con huella antes** de que corra nada.

🔍 **Y hay una medida que dice si la vía (b) es emergencia o disfraz** (Opus), barata y decisiva:
**cuántos tipos distintos de B viola cada relación metamórfica.** Una invariante que captura **1**
tipo es un operador disfrazado; una que captura **5** es emergencia real —una invariante es más
pobre que un operador, no dice el mecanismo, y por eso captura una clase más ancha que la que nadie
enumeró—. **Si la mediana de tipos-por-invariante es 1, la vía (b) es la v1 con una capa encima.**

### 4.3 La adjudicación, con la contradicción temporal resuelta

🔍 GPT: la v2 decía que «la regla de adjudicación **y el `ideal_b`** se sellan antes de curar», y eso
es imposible: el `ideal_b` de cada caso no existe hasta descubrir el caso. Se separa en tres:

| pieza | cuándo |
|---|---|
| **rúbrica de adjudicación y esquema de salida** | sellados **antes** de ejecutar |
| **instanciación de `ideal_b` por caso** | tras congelar candidatos, por adjudicadores **ciegos a todos los brazos** |
| **puntuador** | probado y sellado **antes**, sin acceso a las decisiones de adjudicación ni capacidad de reinterpretar etiquetas |

Lo demás se mantiene: un candidato entra en B solo si el curador puede **señalar la cláusula** que
incumple; si no, va al cajón de **disputados**, que se reporta fuera del primario. **κ entre dos
codificadores ciegos entre sí**; si el acuerdo es bajo, las etiquetas no son datos.

📏 **Y la vía (c) tiene que tener tamaño, que la v2 no le puso.** Con tasa base de silenciosos del
1 %: **299 ejecuciones** para un 95 % de probabilidad de ver *uno* (una muestra de 200 solo da
86,6 %), **~380** para estimar la tasa a ±1 %, y **~1.000 adjudicaciones** para observar unos diez
silenciosos — **×2 por la κ, o sea ~2.000 adjudicaciones humanas**. El tamaño de (c) **se calcula
con la tasa base del piloto** (§9 paso 4b), no se deja en «muestra aleatoria». Sin eso, F1 no está
cerrado: está disfrazado.

---

## 5. El manifiesto sellado, que es lo que impide que la capa sea un brazo

🔍 **La rotura F7** (Opus y GPT, por separado): la v2 ponía el piloto y la tanda sobre **la misma
capa**, escrita por mí, y F1/F2 **autorizaban a cambiarla** si el piloto salía mal. Yo conozco el
agente —lo afiné un mes—, conozco los diez fallos, y sé que la ventaja histórica del afinado se
concentra en el silencioso. Afinar la capa hacia «produce banco silencioso» es **seleccionar el
generador hacia el territorio donde el agente ya demostró fuerza**. Es la rotura de la v1 movida del
autor de tipos al **autor de la capa**.

**Antes del piloto se sella un `MANIFIESTO.md` con huella**, y contiene:

1. familias, parámetros, rangos, distribuciones y **presupuesto E de ejecuciones confirmatorias**;
2. semillas, o mecanismo verificable de generación de semillas, **con partición `pilot` /
   `confirmatorio` por semillas disjuntas**;
3. plazos y definiciones de caída, cuelgue, «nunca se escribió», fuera de orden y duplicado;
4. **la definición canónica de tipo** —cláusula incumplida, familia, mecanismo causal reproducible,
   firma de salida— y su algoritmo de deduplicación. 🔍 Si «tipo genuinamente distinto» se ajusta
   tras ver B, **N es manipulable**;
5. política de reproducción: **r = 5** reintentos por candidato;
6. las relaciones metamórficas completas (§4.2);
7. la rúbrica de adjudicación;
8. versión y pruebas del puntuador;
9. la regla de parada, y **el negativo como regla** (§8).

**Y la cláusula que lo hace valer:** *el piloto no puede entrenar la distribución que se puntúa.* Si
la capa se toca después del piloto, es **capa v2 con huella nueva**, el piloto se repite, el bloque
anterior deja de valer para inferencia confirmatoria, y **se publica el salto en tasa de
silenciosos entre las dos capas**. Si sube mucho, la afiné hacia el desenlace.

🔍 Coste de todo esto: una huella y una línea de protocolo. **Cero ejecuciones.**

---

## 6. Los brazos

| brazo | qué es |
|---|---|
| **agente congelado, prompt afinado** | el de la Fase 12, 17.136 caracteres, con huella |
| **prompt de contrato reconstruido** | escrito **desde el contrato y el estándar**, por quien no ve el afinado ni A |
| **prompt genérico** | los 1.174 caracteres del paso 29, misma pregunta binaria byte a byte |
| **v3 congelado** | `triador_regex_v3.py` sin tocar — **comprobación de novedad**, no se resta |
| **v3 actualizado** | reglas escritas viendo B bajo el protocolo de recursos fijados (§7.1) |
| **inductor** | suelo automático, calibrado en A antes de ver B. **Nunca estratifica** |

🔍 **El argumento de simetría de la v2 es falso, y los cuatro lo dicen.** Sostenía que el prompt
afinado es el brazo justo porque lo que compró el mes fue el contrato, y el autor de reglas también
lo recibe. Pero:

- 📏 la ventaja del afinado se concentra **exactamente en fallo silencioso** (−0,229 → +0,500),
  que es la clase que B está diseñado para sobrerrepresentar. **El argumento de simetría es válido
  para el promedio y falso para la cola** — y la cola es el primario;
- 🔍 un contrato ADT^A01→Patient cabe en unos 3.000 caracteres. Los otros 14.000 son heurísticas,
  ejemplos y patrones de traza **derivados de A**;
- 🔍 la simetría real no se consigue dándole «un prompt» al autor de reglas, sino **la información
  operacional equivalente**: el mismo contrato, **la misma interfaz de evidencia**, las mismas
  relaciones observables, el mismo acceso a estado, a pares metamórficos y a secuencias.

**Por eso el brazo del medio.** `afinado − contrato reconstruido` es la parte que **no** es el
contrato. Si esa diferencia persiste en B, no se puede atribuir al contrato y se llama por su
nombre.

🔍 **Regla preinscrita** (DeepSeek): si la ventaja del afinado en B se concentra en tipos
emparentados con arquetipos de A, **se declara contaminación y el primario pasa al genérico**.

---

## 7. El endpoint

**Primario: detección del agente congelado sobre TODO B curado**, macro por tipo, a exposición
cero, **con veto**: más falsas alarmas que el `v3` congelado sobre los limpios de B invalida la
ventaja aunque el número salga alto.

🔍 **La pregunta la contesta la conjunción de tres números al lado, ninguno definido por el
desenlace de otro** (Opus):

> el agente detecta **X %** de B · de B, el **Y %** resultó no alcanzable por el `v3` puesto al día
> bajo recursos fijados · el agente detecta **Z %** de ese Y.

**Portada: X con su veto.** Y y Z van al lado, como descriptores.

### 7.1 El residuo, medido y bajo recursos fijados

🔍 GPT da la definición que lo hace publicable y honesto. No es «lo que no cubre una regla
estática» —eso es una incapacidad metafísica e inverificable— sino:

> tipos no cubiertos por un autor de reglas bajo **lenguaje L**, **interfaz de evidencia I**,
> **presupuesto T**, **exposición e** y **criterio de éxito C**, todos preinscritos.

Protocolo:

1. lenguaje de reglas permitido, definido formalmente;
2. **interfaz de evidencia igualada con la del agente** (§8, auditoría A);
3. presupuesto por tipo y total;
4. el autor emite, **por cada tipo**, una de tres salidas: **regla candidata**, **abstención
   razonada con código de motivo**, o **«no reproducible»**;
5. la regla se ejecuta **automáticamente** contra el hold-out de instancias (ve 2 de las k, se
   puntúa sobre el resto);
6. se mide cobertura, falsas alarmas y **tiempo**;
7. abstenciones y reglas fallidas se publican **por separado**.

Lo que se publica es «**residuo frente a este sistema de reglas, esta interfaz y este
presupuesto**». 🔍 Registrar la **familia del autor de reglas** igual que la del curador: si comparte
familia con el agente, el residuo mide andamiaje entre dos instancias del mismo modelo.

🔍 **Si el residuo sale vacío, es un resultado publicable y fuerte** (Opus): dice que la emergencia
produjo fallos que las reglas alcanzan. No es el caso de la v1 —allí el vacío estaba garantizado
*por construcción*—; aquí el vacío está **medido**. Lo que sí sería un banco que no contesta es el
caso simétrico: residuo = todo B, porque entonces las invariantes eran tan específicas que el `v3`
no alcanza ninguna → lo diagnostica la mediana de tipos-por-invariante (§4.2).

### 7.2 Los limpios de B, que la v2 no definía

🔍 GPT: «limpios de B» no aparece definido en ninguna parte, así que **el veto se estaría estimando
sobre otra población** y puede ser irrelevante. Los negativos se generan **bajo las mismas familias
y condiciones operacionales** que B: entradas válidas, perturbaciones semánticamente equivalentes,
recuperaciones esperadas, rechazos correctos, y errores de transporte correctamente manejados.

### 7.3 Lo demás, al lado y nunca agregado

1. `v3` congelado sobre B, crudo y tipo a tipo: cuánto de B resultó ser firma vieja.
2. **Detecciones propias** del agente contra el `v3` actualizado fuera de muestra.
   📏 En la Fase 12 fue 1 de 55 y ni siquiera era una detección.
3. Los tres prompts por clase, y la diferencia `afinado − contrato reconstruido`.
4. Coste por tipo del autor de reglas.
5. La matriz vía × tipo, y la distribución de tipos-por-invariante.

🔍 **Regla anti-Fase-12, intacta:** ningún número agregado sobre limpios + silenciosos aparece en el
resumen.

### 7.4 Los mandos, clavados

🔍 Cada mando discrecional tiene una dirección que favorece al modelo. La v2 clavaba seis y **se
dejó fuera el puntuador**, que es el que decide qué es detección y qué es falsa alarma.

| mando | cómo queda clavado |
|---|---|
| **el puntuador** | 🔍 **F8.** Congelado con huella y **auditado antes de curar** (§8, auditoría B) |
| la capa de perturbación | sellada en el `MANIFIESTO` **antes** del piloto (§5) |
| la definición canónica de tipo | en el `MANIFIESTO`, antes de ver B |
| las invariantes | escritas por quien no ve la capa, selladas antes de correr |
| qué entra en B | el curador, ciego a todos los brazos |
| el residuo | medido bajo recursos fijados, no declarado |
| cuál es el primario | escrito en esta §7 |
| el prompt | congelado con huella, y con el brazo de contrato reconstruido al lado |
| «detección propia» | **la mitad o más** de las instancias del tipo |
| la contabilidad de vías | un fallo cuenta para todas las vías que lo ven |

---

## 8. Cómo fracasaría ESTA fase

Las auditorías del paso 0 y las medidas del piloto no encargan nada.

**F10 · Contaminación semántica con A — 🔍 y GPT sostiene que es la que más probablemente mata la
fase, por delante del piloto.** F4 excluye los diez conocidos **por identidad**, y eso no basta: B
puede producir **variantes del mismo arquetipo** —mismo mecanismo causal con otro disparador, misma
invariante en otro campo HL7, mismo patrón `AA`/recurso, mismo fallo de estado con otra carga—.
**Auditoría C:** matriz sellada de «arquetipos presentes en A» contra «mecanismos que puede producir
B». Si no se puede construir esa matriz, **«exposición cero» no se puede defender** y la frase no se
escribe.

**F7 · Contaminación por selección del generador.** §5. Sellado del manifiesto antes del piloto.

**F8 · El puntuador no está clavado.** 🔍 DeepSeek y GPT. Viene calibrado contra A y comparte
historia con el agente afinado: no hay independencia entre el instrumento y el objeto medido.
**Auditoría B:** congelarlo con huella, publicarlo, y pasarlo por un juego adversario nuevo con
**juez humano ciego al brazo y con orden aleatorizado**, sobre casos derivados **solo del contrato**
por un tercero. **Si la concordancia baja del 90 %, no vale para B.**

**F9 · El fuzzer satura la infraestructura antes de tocar la semántica.** 🔍 Gemini: el grueso de lo
que sale de fuzzear MLLP/TCP son plazos agotados, resets y memoria. **Medida:** una hora de capa
**sin oráculos**, contando solo clases de error de red. Si más del 90 % son caídas de
infraestructura, B es un test de estrés y no un banco, y te ahorras el curador.

**F1 · La capa no produce silenciosos.** Piloto de humo de **50 ejecuciones** con 2-3 relaciones
críticas (🔍 DeepSeek: mata F1 sin esperar a tener la capa entera), y después el piloto completo.

**F2 · Todo B sale de la misma familia.** 🔍 **Y la regla del 60 % de la v2 no arregla nada por
declararla** (GPT): es un umbral narrativo. Se convierte en **regla de interpretación**: la macro
global no se usa como afirmación de generalidad si una familia domina; hace falta un mínimo de
familias con un mínimo de tipos para un resultado transversal, **o se declara que el alcance es solo
la familia dominante**.

**F3 · El oráculo imprime su firma.** §4.1 y §4.2, con el argumento falso de la v2 corregido y la
mediana de tipos-por-invariante como diagnóstico.

**F4 · Los diez conocidos.** Sellados y en estrato aparte. **Insuficiente por sí solo** — ver F10.

**F5 · El curador no es ciego.** Paquete de contexto sellado: contrato, estándar, ejecutor y
relaciones. Ni A, ni el agente, ni el `v3`, ni el puntuador. Identidad y familia registradas.

**F6 · 🧑 El que no sé ver.** La v1 y la v2 cayeron las dos por aquí. **Esta v3 vuelve al panel.**

---

## 9. El tamaño: se firma la regla, no el número

🔍 Los cuatro: firmar el 25 % antes de conocer N y la escala es firmar un umbral sobre una escala
desconocida. Lo que se preinscribe:

- **presupuesto E** de ejecuciones confirmatorias, y partición `pilot` / `confirmatorio` por
  semillas disjuntas;
- **definición canónica de tipo**, sellada (§5.4);
- **r = 5** reintentos de reproducción por candidato;
- **k_min = 3** instancias reproducidas para que un tipo entre en el análisis por tipo; los de
  k < 3, solo descriptivos;
- **N_min deducido de una precisión mínima aceptable**, no de la conveniencia;
- una **tabla N → decisión** firmada antes del piloto: N ≥ N_alto, el primario se publica como
  primario; N_bajo ≤ N < N_alto, se publica con intervalo y **etiqueta de baja potencia**;
  N < N_bajo, **descriptivo, y «la capa no produce banco» es el resultado**.

📏 **La aritmética, que conviene mirar antes de ilusionarse.** Para una tasa de detección por tipo
cerca del 25 % y una semianchura de ±10 puntos, hacen falta del orden de

```
N = 1.96^2 x 0.25 x 0.75 / 0.10^2  ~  72 tipos aproximadamente independientes
```

Eso está **muy por encima** de los 30 de la v1, y probablemente por encima de lo que la capa
produzca. 🔍 Con dependencia fuerte entre tipos hay que abandonar el intervalo binomial simple y ir
a bootstrap por familia o mecanismo. **Si la capa no llega, el análisis es descriptivo** — y eso es
un resultado sobre el proceso, dicho con esas palabras y no rebajando N en silencio.

**El negativo se desdobla** 🔍: **la regla** se firma en el paso 2 (manifiesto); **la aritmética**
—qué número de tipos corresponde a ese umbral— se calcula tras el paso 4, cuando existe la tasa
base. Firmar antes el número era firmar sobre nada.

---

## 10. El orden

🔍 GPT mueve el primer puesto: **lo que más probablemente mata la fase no es el piloto, es la
auditoría de contaminación.** Si el prompt lleva conocimiento semántico de A que reaparece en B, una
tasa alta del agente no contesta la pregunta aunque B produzca muchos silenciosos y muchos tipos.

```
 0. AUDITORIAS, sin capa y sin agente          <- lo que mas probablemente mata la fase
    A. interfaz comun de evidencia: agente, v3 congelado y v3 actualizado reciben
       LO MISMO, salvo que la diferencia sea el objeto de estudio
    B. puntuador: congelado, publicado, contra juez ciego. <90% de acuerdo -> no vale
    C. contaminacion semantica: matriz arquetipos de A <-> mecanismos que puede dar B
       + particion del prompt afinado (contrato / procedimiento / derivado de A)
 1. relaciones metamorficas, por QUIEN NO DISENA LA CAPA, y selladas
 2. MANIFIESTO sellado con huella: capa, semillas, tipo canonico, k_min, regla de
    parada, y el NEGATIVO COMO REGLA
 3. piloto de humo: 50 ejecuciones, 2-3 relaciones criticas   <- mata F1 barato
 4. piloto completo (~300 ejec., semillas disjuntas) -> tasa base, distribucion por
    familia y por via, y una hora de capa sin oraculos para F9
    4b. aritmetica del negativo y tamano de muestra de (c), DERIVADOS de la tasa base
 5. oraculo diferencial contra referencia      <- la unica via que ve silencio sin firma mia
 6. inductor calibrado en A (descriptor y suelo; se puede posponer)
 7. adjudicacion: rubrica sellada, kappa entre dos codificadores
 --------------------------------------------- hasta aqui, nada encargado
 8. curacion a ciegas
 9. congelar, preinscribir, sellar
10. UNA pasada
```

**Nunca más un mes de trabajo antes de saber si el banco puede contestar la pregunta.**

---

## 11. Lo que se hereda y lo que decae

**Se hereda:** el circuito congelado con su huella y sus 27 pruebas, el arnés (`Datos`,
`HerrA/B/C`), las clases del agente, `comparar.py`, la maquinaria de sellado, la matriz de
observabilidad, el banco de adversarios y los tres triadores. El **puntuador se hereda bajo
auditoría** (F8), no tal cual.

**Decae de la v1:** el oráculo de mecanicidad como estratificador, el DiD como primario, los
cuartiles, Q1/Q2 como par, N = 30 / k = 5.

**Decae de la v2:** el residuo **declarado** como primario; el argumento de que la cuota de (a)
prueba algo sobre el sesgo de (b); el argumento de simetría del prompt afinado; la regla del 60 %
como declaración; el número del negativo firmado antes de conocer la escala; y «`ideal_b` sellado
antes de curar», que era imposible.

---

## 12. Abierto 🧑

1. **La precisión mínima aceptable**, de la que sale N_min. La aritmética dice ~72 tipos para ±10
   puntos; si se acepta peor precisión, baja. **Es la decisión que más condiciona si la fase existe.**
2. **Quién escribe las relaciones metamórficas**, que ya no puedo ser yo.
3. **Quién cura** B, y **quién escribe la regla actualizada**, con sus familias registradas.
4. **Presupuesto E** de ejecuciones, y presupuesto de adjudicación humana para la vía (c) — que con
   tasa base del 1 % son miles, no decenas.
5. **Qué implementación de referencia** para la vía (d).
6. Si las **auditorías del paso 0** las hace un tercero con acceso controlado a A, al prompt y al
   puntuador. 🔍 Dos revisores lo pidieron explícitamente y dijeron para qué; sin ellas, «exposición
   cero» no se puede defender.
7. Si el **estrato de los diez conocidos** se corre igualmente como descriptivo.
