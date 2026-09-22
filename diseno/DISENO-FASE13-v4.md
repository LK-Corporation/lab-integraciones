# Fase 13 — Diseño, v4 (22-sep-2026). **Dos etapas: B0 falsa, y solo entonces A mide**

**Estado: BORRADOR. No se ejecuta la primera semilla de B0 hasta firmar 🧑 la §5 y sellar la §4.2.**

Escrita con las cinco revisiones de la ronda B, con la **medida** del prior (`E1E2E3.md`) y con la
respuesta de GPT a la pregunta «¿qué hacer?» (`revision-quehacer-gpt.md`).

**Lo que cambia, en una frase: la Fase 13 deja de ser una fase y pasa a ser dos.** Antes de pagar
curador, adjudicación masiva y pasada confirmatoria hay que **falsar barato** que exista la clase
que la fase mide. Si no existe, no hay fase, y eso es el resultado.

Convención: 📏 sale de una medida, 🔍 de una revisión externa, 🧑 lo decide Víctor.

---

## 1. Qué obliga a partirla en dos

La v3 arregló el endpoint. Pero una quinta revisión metió un eje nuevo, y **ese eje se midió**.

Respecto al **bundle** —la evidencia que recibe un brazo—, un fallo cae en una de estas clases. Las
etiquetas son las que GPT impuso, porque las primeras sobreafirmaban:

| | qué demuestra |
|---|---|
| **C1** | hay al menos una regla **derivada del contrato** que lo cubre |
| **C2** | hay al menos una regla que lo cubre, pero **solo tras conocer el catálogo** |
| **C3** | **ninguna regla disponible lo cubre**, y el agente sí. Es la clase que justifica la fase |
| **O0** | no observable con el bundle: no lo detecta nadie, y una nota ahí sería fuga |

📏 **Medido sobre los 456 casos de desarrollo, clase de fallo silencioso: C1 = 8, C2 = 8, C3 = 0,
O0 = 2.** Cero operadores donde el agente detecte y ningún juego de reglas lo haga. Y de paso, tres
operadores que las reglas cubren a 8/8 y el agente falla del todo, dos de ellos con solo el
contrato.

**Lo que ese cero significa, y no más:**

- 🔍 **no es probabilidad cero.** La cota superior unilateral al 95 % es `1 − 0,05^(1/18) ≈ 15,3 %`,
  y eso **suponiendo** los 18 operadores independientes y representativos, que es falso: hay familias
  enteras correlacionadas. La cota real es peor, y el análisis tiene que ir **por familia o
  mecanismo**, no por operador;
- 🔍 **el proxy es flojo y su sesgo va a favor de la conclusión.** `v3-invariante` mide «qué cubrió
  *este* autor usando solo el contrato», no «es expresable como predicado del contrato»: mezcla
  expresabilidad con que se te ocurra, tiempo, habilidad y sesgo de disponibilidad. Conocer A sesga
  **contra** C3;
- 📏 **está medido sobre A**, un banco de mutaciones declarativas, o sea el terreno más favorable
  posible a las reglas. **Es el prior, no la respuesta.**

**Consecuencia, y es la decisión de diseño de esta v4:** con este prior es irracional pagar la fase
completa, y es prematuro cerrar —cerrar ahora confundiría «A no contiene C3 observada» con «no hay
C3 en fallos emergentes»—. **Se parte en dos, y la primera mitad existe para falsar.**

---

## 2. Las dos etapas

| | **B0 — falsación** | **A — medición** |
|---|---|---|
| para qué | ¿existe **un solo** tipo C3 reproducible, emergente y con la evidencia dentro del bundle? | medir cuánto aporta el agente sobre B |
| qué cuesta | la capa, un piloto, y una miniadjudicación sobre los candidatos | curador externo, adjudicación masiva, ~72 tipos, pasada confirmatoria |
| quién | puede hacerlo el autor del laboratorio, con la separación mínima de la §4.9 | exige curador ciego y preinscripción |
| qué puede afirmar | que se observaron —o no— candidatos compatibles con C3 | la pregunta de la fase |
| si sale mal | **la fase no se monta, y eso es el resultado** | — |

🔍 **B0 no es «la Fase 13 barata».** Es un estudio de factibilidad y falsación, y se llama así en
todo lo que se publique. Con el mismo autor escribiendo capa, relaciones y análisis, sin
preinscripción ni conjunto reservado, **da señal de escalado, no conclusión limpia**.

---

## 3. La pregunta de B0, escrita para poder salir que no

> ¿Aparece **al menos un tipo reproducible**, no preespecificado individualmente, cuya evidencia
> discriminante esté **dentro del bundle**, que el agente detecte bajo el criterio predefinido, y
> que **no cubran dos autores de reglas independientes** limitados al contrato, a la misma interfaz
> y al mismo presupuesto?

🔍 Nótese lo que **no** pregunta: no pregunta si el fallo es «inexpresable». Eso no se puede
demostrar barato ni probablemente nunca. Lo que se mide es **cobertura bajo lenguaje `L`, interfaz
`I`, presupuesto `T`, exposición `e` y acceso informativo `K`**, todos preinscritos, y entonces lo
afirmable es: *«no fue cubierto por dos implementaciones independientes del sistema de reglas
especificado, dentro del presupuesto declarado»*. Eso sí es una definición experimental defendible.

---

## 4. B0, pieza a pieza

### 4.1 El bundle, ya definido y con huella

📏 Leído del arnés y verificado contra los 327 payloads reales (`E1E2E3.md` §1):

- **`mensaje`**: el HL7 tal como llegó por el cable, un segmento por línea.
- **`traza`**: **recorrido** (`Ens.MessageHeader`: origen → destino, clase, estado, marca de error),
  el **canónico** producido por la transformación —ocho campos de `Lab.HL7.Msg.PatientRequest`— y el
  **ACK** entero.
- **`log`**: el Event Log de la sesión, con el tiempo **relativo** al primer apunte.

**Y lo que no está, que es lo que decide qué es O0:** el recurso FHIR realmente escrito —lo que se
ve es el canónico **intermedio**—, el estado del almacén, la configuración del circuito, nada de
otra sesión, y las marcas de tiempo absolutas. Las duraciones sí se conservan.

🔍 **Principio operativo que resuelve varias cosas a la vez:** si el adjudicador necesita **más que
el bundle** para decidir, el tipo es **O0 para todos los brazos**, y sale del primario.

🔍 **Y el bundle tiene que ser idéntico para todos los brazos.** Si el agente necesita algo que no
está —por ejemplo consultar estado en vivo, que a la hora de puntuar ya no es el de la ejecución—,
ese algo **entra en el bundle para todos** o el tipo es O0 para todos.

### 4.2 El manifiesto, sellado antes de la primera semilla

Con huella y fecha verificable. Contiene:

1. familias, parámetros, rangos, distribuciones y **presupuesto `E`** de ejecuciones;
2. semillas, con partición **`piloto` / `confirmatorio` disjunta**;
3. plazos y definiciones de caída, cuelgue, «nunca se escribió», fuera de orden y duplicado;
4. **la definición canónica de tipo** (§4.6) y su algoritmo de deduplicación;
5. política de reproducción: **r = 5** intentos por candidato;
6. las relaciones metamórficas completas y los predicados de la vía (a), **escritos y sellados**;
7. la rúbrica de adjudicación y el esquema de salida;
8. versión y pruebas del **puntuador**, ya auditado (§8, auditoría B);
9. las dos reglas de decisión de la §5, con sus números;
10. la regla de parada.

🔍 **La cláusula que lo hace valer:** *el piloto no puede entrenar la distribución que se puntúa.* Si
la capa se toca después del piloto, es **capa nueva con huella nueva**, el piloto se repite, el
bloque anterior deja de valer para inferencia, y **se publica el salto en tasa de silenciosos entre
las dos capas**. El número de iteraciones de la capa se publica.

### 4.3 Las vías de entrada, y ninguna se funde con otra

Cada una publica **su proporción y su tasa de falsos positivos por separado**. Un fallo hallado por
varias **cuenta para todas**, y se publica la matriz vía × tipo: si no, la proporción es manipulable.

| vía | qué ve | de quién es la firma |
|---|---|---|
| **(a) anomalía operacional** | caídas, cuelgues, resets, acuses ausentes, recursos que nunca se escriben, proceso fuera de orden | 🔍 **mía, y la v3 se equivocaba al decir que no**: es una lista de síntomas que escribo yo, y «recurso que debía escribirse» o «el orden esperado» ya necesitan el contrato. Además parte de lo que recoge **es la propia perturbación** — un reset inyectado *es* un reset |
| **(b) invariante metamórfica** | violaciones de invariancias del estándar y del contrato | mía, la del contrato. Ver §4.4 |
| **(c) inspección humana sobre muestra** | cualquier cosa, incluido el silencio | del adjudicador |
| **(d) validadores de tercero** | 🔍 el **validador oficial de FHIR** (`validator_cli`, requiere java, no instalado) sobre el recurso **realmente escrito** contra el perfil, y un **validador de conformidad v2** sobre el acuse. 🧑 Es el primer peldaño; el mapeador de referencia desde `estandares/v2mappings/` solo si este no encuentra nada (§11.5) | del **estándar tal cual**, no de una lectura del estándar. Su autor nunca vio el prompt ni A. Cubre lo estructural, no lo semántico del mapeo. **Coste: horas** |
| **(e) determinismo y replay** | la misma entrada dos veces; el mismo lote en dos órdenes; la misma entrada antes y después de un reinicio | **ninguna**: no necesita contrato ni cláusula. Dos salidas distintas para la misma entrada son un candidato. Es el oráculo natural de «carga y entorno», donde salieron 4 de los 10 — **y además fabrica `k`** (§4.7) |
| **(f) conciliación en masa** | los PID de entrada contra la tabla de `Patient` del almacén, en bloque | diferencial a nivel de conjunto. 🔍 Es como apareció el fallo de los acentos |
| **(g) control positivo** | 🔍 si alguno de los diez fallos conocidos **sigue** en el circuito congelado, la capa reproduce su disparador y las demás vías tienen que verlo | **«el oráculo ve X de los diez» es la única medida de recall que no cuesta un curador.** Los diez van luego a su estrato aparte igualmente |

🔍 **Y hay que enterrar un argumento de la v2 y la v3:** «la cuota de (a) prueba que B no es solo el
contrato leído al revés» es **falso**. (a) y (b) cubren conjuntos casi disjuntos, y (a) es **ciega a
todos los silenciosos**, que son el objeto de la fase. La vía sin sesgo era también la vía sin
señal.

### 4.4 Las relaciones metamórficas: dos autores, y uno ciego al prompt

🔍 **La v3 cegaba al autor respecto a la capa. La ligadura que importa es otra: respecto al
prompt.** Las relaciones las escribiría quien afinó 17.136 caracteres durante un mes, y ese prompt
casi seguro **nombra** las invariantes que su autor aprendió a mirar —desescapado, normalización,
coherencia acuse/recurso, repeticiones—. Entonces la vía (b) no imprime la firma del contrato:
imprime **la firma de la lectura del contrato que ya está en el prompt**, y el primario mediría
recuerdo del prompt. Sellar «antes de correr» no lo evita: es antes de correr, pero **después del
mes**.

- **un segundo autor, ciego al prompt**, escribe su conjunto solo con estándar y contrato;
- se publica el **solapamiento entre los dos conjuntos**, y se sella la unión;
- **cada relación lleva su cláusula.** Una relación sin cláusula es opinión del autor —o sea un
  operador declarado— y se aparta;
- **tabla de solapamiento relación ↔ prompt**, de coste cero: para cada relación, la cláusula que
  cita y el pasaje del prompt que pide esa misma comprobación, o «ninguno». Si la mayoría tiene
  pasaje, la vía (b) está contaminada **antes de que exista B**;
- con esa tabla, el análisis se estratifica por **«invariante nombrada en el prompt / no nombrada»**,
  y el **prompt genérico es el control natural**: si el afinado solo gana en las nombradas, el mes
  compró una lista de comprobación.

🔍 **Diagnóstico de si (b) es emergencia o disfraz:** cuántos **tipos distintos** viola cada
relación. Una invariante que captura **1** tipo es un operador disfrazado; una que captura **5** es
emergencia real. **Si la mediana es 1, la vía (b) es la v1 con una capa encima.**

### 4.5 La adjudicación

🔍 La v3 decía que la rúbrica **y el `ideal_b`** se sellan antes de curar, y eso es imposible: el
`ideal_b` de cada caso no existe hasta descubrir el caso. Se separa:

| pieza | cuándo |
|---|---|
| **rúbrica y esquema de salida** | sellados **antes** de ejecutar |
| **instanciación de `ideal_b` por caso** | tras congelar candidatos, por adjudicadores **ciegos al brazo** |
| **puntuador** | probado, auditado y sellado antes, sin acceso a las decisiones de adjudicación |

🔍 **El adjudicador trabaja sobre el mismo bundle que ven los brazos, sin las relaciones y sin la
etiqueta de perturbación.** Ambas se le revelan **después** del veredicto, para el descriptor. Si no,
la vía (c) —la única insesgada— pasa a ser (b) con cara humana, y «tipo» tiende a ser igual a
«perturbación».

🔍 **Y la regla de rigor de la v3 se corrige, porque vaciaba la clase que la fase necesita.** Decía
que un candidato entra solo si el adjudicador señala la cláusula; pero **cláusula + bundle es un
predicado**, así que esa regla empuja a C1 por construcción y manda C3, si existe, al cajón de
disputados. **El cajón de disputados deja de ser descarte y pasa a ser estrato puntuado**, y se
publica.

### 4.6 «Tipo», que si no se define no hay N

🔍 El primario es macro por tipo y la v3 hablaba de «tipos genuinamente distintos» sin dar la
relación de equivalencia. Si dos perturbaciones disparan el mismo bug, ¿uno o dos tipos? Si una
dispara dos bugs, ¿uno o dos? Hoy lo decidiría el adjudicador sobre la marcha, y **N sería
manipulable**.

> **tipo = (cláusula incumplida, síntoma observable, mecanismo sospechado)**, sellado en la rúbrica.
> **La familia de perturbación es descriptor, nunca clave.**

🔍 **Y la κ que hace falta no es la de fallo/limpio: es la de la asignación de tipo**, entre dos
codificadores, sobre los candidatos del piloto. **Si la κ de tipo es baja, N no existe.** (La κ de
fallo/limpio con prevalencia del 1 % es degenerada —ambos dicen «limpio» el 99 % de las veces—, así
que se calcula sobre el **conjunto enriquecido**: aciertos de las vías más una muestra limpia, y se
publica con la prevalencia.)

### 4.7 Los limpios de B, el adversario de rareza, y `k`

🔍 **B es rara por construcción**, y eso puede regalar el resultado. Transporte, codificación y
gramática producen entradas distinguibles del corpus limpio por **rasgos de superficie**; carga y
entorno deja huella en los tiempos; el corpus real es la única familia sin ese confundente. Un
detector —agente o regla— que diga «fallo» cuando la entrada es **rara** puntúa alto sin haber
detectado nada.

- **los limpios de B son entradas perturbadas que el sistema manejó conforme al contrato**,
  emparejadas por familia con los fallos. Si salen del corpus sin perturbar, «raro ⇒ fallo» gana;
📏 **Y una leccion que sale de medir la propia vía (d), que vale para todo el diseño:** el primer
control de discriminación que se corrió comparó **acuses de fallo contra acuses limpios** y dio una
diferencia que **no era detección**: los limpios no llevan segmento `ERR`, así que cualquier hallazgo
sobre el `ERR` separa los dos grupos sin entender nada. Es **F6 dentro del propio oráculo**.
**Un control de discriminación compara correcto contra incorrecto en la misma estructura, no fallo
contra limpio.** Se aplica igual al adversario de rareza de aquí abajo.

- **el adversario de rareza**, que es el principio de esta casa aplicado otra vez —el adversario
  mecánico se escribe antes que el agente—: un clasificador trivial de rasgos de superficie
  (validez del marco, fracción de bytes no ASCII, desviación del número de segmentos, MSH-12,
  longitud). **Su AUC separando fallo de limpio es el número. Por encima de ~0,8 el banco es un
  detector de fuzzing**, y se dice así;
- **techo absoluto de falsas alarmas**, preinscrito **además** del relativo: el relativo al `v3`
  congelado es laxo si el `v3` también dispara sobre entradas raras;
- **localización en la respuesta**: el veredicto lleva segmento/campo o elemento del recurso, y el
  puntuador lo compara mecánicamente con el del adjudicador. **La detección con localización
  equivocada se cuenta aparte.**

🔍 **`k` por replay, no por recurrencia.** El `k` emergente será de cola pesada hacia el singleton:
lo raro aparece una vez, y apartar los singletons dejaría el primario sobre los fallos regulares,
que son los ruidosos. La forma honesta de subir `k` sin declarar nada es **replicar cada candidato
`r` veces con la misma perturbación y el contexto irrelevante variado** (MSH-10, paciente);
`k` = reproducciones; lo que no reproduce va al estrato «no reproducible». **Y hace falta `k` ≥ 4**:
con `k` = 2 el autor de reglas ve las dos instancias y no hay fuera de muestra; con 3 es cara o
cruz.

### 4.8 El criterio de detección, y por qué el 25 % no era un nulo

🔍 **Aritmética, no opinión.** Con un agente que dispara con probabilidad `q` sobre cualquier
instancia, la probabilidad de que un tipo salga «detectado» **por mayoría simple** es
`P(Bin(k,q) ≥ ⌈k/2⌉)`. Con `q` = 0,30: `k` = 2 → **0,51**; `k` = 3 → 0,22; `k` = 4 → 0,35;
`k` = 5 → 0,16. **Un B dominado por tipos de k = 2 y un agente que dispara sobre el 30 % de las
entradas raras pasa el 25 % con ruido puro**, y el veto relativo al `v3` no lo para si el `v3`
también dispara sobre lo raro.

- **«detectado» = mayoría estricta** (k = 2 → 2/2; k = 3 → 2/3; k = 4 → 3/4);
- se publica la **macro nula bajo `q̂`** —la tasa de disparo del agente sobre los limpios
  perturbados— con la distribución empírica de `k`;
- el negativo es **«no supera el nulo por permutación de veredictos entre instancias al 5 %»**, y el
  25 % queda como **suelo absoluto adicional**;
- si el agente es estocástico, `r` corridas por instancia con voto mayoritario, y se publican las
  `r`.

**Todo esto se preinscribe como procedimiento; el número sale de los datos.**

### 4.9 El residuo, bajo recursos fijados y con dos autores

No «lo que no cubre una regla estática» —incapacidad metafísica e inverificable— sino:

> tipos no cubiertos bajo **lenguaje `L`**, **interfaz `I`**, **presupuesto `T`**, **exposición `e`**
> y **acceso informativo `K`**, todos preinscritos.

1. `L` definido formalmente: regex, extracción HL7, condiciones sobre canónico/ACK/log, agregados
   temporales permitidos, reglas de secuencia;
2. `I` **idéntica a la del agente** (auditoría A de la §8);
3. presupuesto por tipo y total: tiempo, número de reglas, número de instancias vistas;
4. 🔍 **dos autores independientes** que **no hayan visto A, el catálogo, el prompt afinado ni los
   resultados de la Fase 12**, trabajando sobre **tipos anonimizados**;
5. cada autor emite por tipo una de tres salidas: **regla candidata**, **abstención razonada con
   código de motivo**, o **«no reproducible»**;
6. las reglas se ejecutan **automáticamente** sobre las instancias retenidas (el autor ve las
   permitidas; se puntúa sobre el resto);
7. se publican cobertura, falsas alarmas, **coste** y **desacuerdo entre los dos autores**.

🔍 **Registrar la familia del autor de reglas**, como la del adjudicador: si comparte familia con el
agente, declarará «no cubrible» lo que su familia no entiende, que es lo que el agente tampoco
entiende, y el residuo pasa a ser **la lista de puntos ciegos del agente**. Si es un modelo, se
**replica** con `n` semillas: si el residuo cambia entre corridas, es ruido, y la κ sale gratis.

### 4.10 Separación mínima de roles

Aunque B0 no tenga curador completo, hace falta al menos:

- quien escribe las relaciones **no ve la capa** — y el segundo autor **no ve el prompt**;
- quien evalúa candidatos **no ve las salidas por brazo**;
- **dos adjudicadores ciegos entre sí** para los candidatos C3 y una muestra de negativos y
  disputados;
- **dos autores independientes de reglas** para los candidatos C3.

🔍 **Si esta separación no se puede pagar o conseguir, B0 sigue siendo útil internamente, pero no se
presenta como evidencia de C3.**

---

## 5. Las dos puertas, firmadas antes de abrirlas 🧑

### Escalar de B0 a A

Se monta la fase completa **solo si** B0 produce:

1. **≥ 3 tipos candidatos C3 distintos** — distintos de **mecanismo**, no tres instancias del mismo;
2. reproducidos en **`k` ≥ 3** instancias cada uno;
3. repartidos en **≥ 2 familias** de perturbación;
4. con la evidencia **necesaria y suficiente dentro del bundle**, verificada por adjudicación ciega;
5. detectados por el agente bajo el criterio de la §4.8;
6. **no cubiertos por los dos autores de reglas independientes** de la §4.9;
7. y con una proyección conservadora, **escrita como ecuación y no como impresión**, de que el
   presupuesto confirmatorio alcanza `N_bajo`:

```
   lambda_C3_inferior  x  E_confirmatorio  >=  N_bajo
```

donde `lambda_C3_inferior` es un límite inferior **preinscrito** de la tasa de tipos C3 por
ejecución o por candidato adjudicado, según la unidad que se fije, y **`N_bajo` = 32** 🧑, que sale
de aceptar una semianchura de ±15 puntos sobre una tasa de detección por tipo cerca del 25 %
(§11.1). El límite y el presupuesto se **calculan** tras el piloto; la regla está firmada antes.

### Cerrar tras B0

Se cierra si, agotado el presupuesto `E` de B0:

- **no hay ningún C3 validado**; o
- los únicos aparentes se explican por **fallo del puntuador**, **información no común entre
  brazos**, **fuga desde el prompt o desde A**, **evidencia fuera del bundle**, o **cobertura por un
  autor independiente dentro del presupuesto**; o
- B0 **no produce suficientes silenciosos o tipos reproducibles** para que A pueda alcanzar
  `N_bajo`.

🔍 **Cerrar es dejar de pagar, no haber contestado, y hay que escribirlo con esas palabras.**
Las dos cosas son distintas y el diseño las confundía. Preguntadas por separado a un modelo de
decisión calibrada: **«dejar de invertir en esta línea sería razonable» 0,87**, frente a **«la pregunta
quedaría contestada» 0,06**. Y sobre cómo redactar esta regla, eligió la económica explícita con
**confianza 1** y cero en las otras tres.

🔍 **Corolario estructural, medido en 0,90: B0 es una puerta de un solo sentido.** Puede justificar
**escalar**; por su diseño —sin preinscripción, sin reservado, sin curador ciego— no puede justificar
**concluir**. Lo que sostiene no es una conclusión, es un límite de gasto.

Por tanto el resultado de cerrar **no es «el agente no sirve»** ni «la clase no existe». Es, y se
publica así, en dos frases que van juntas:

> Bajo esta arquitectura, esta interfaz de evidencia y esta distribución de perturbaciones, no se
> encontró la clase que justificaría una comparación confirmatoria costosa, **y se deja de invertir
> en ella. La pregunta sigue abierta**, y lo que la contestaría es un B con curación independiente,
> preinscripción y conjunto reservado, que es lo que no se ha pagado.

---

## 6. Lo que B0 no podrá afirmar, aunque salga limpia

Escrito aquí para no tener que discutirlo después:

- que el agente detecta fallos que **nunca vio**;
- que tiene **exposición cero** a arquetipos de A;
- que **supera a las reglas** en una población representativa;
- una **tasa precisa** de ventaja;
- **generalidad** a otros circuitos, estándares o implementaciones;
- que C3 es **intrínsecamente no expresable**;
- que un resultado positivo **no depende** de la distribución de perturbaciones diseñada;
- que el hallazgo sería **reproducible** sin pasada confirmatoria con curación y conjunto reservado.

**Lo máximo afirmable:** *bajo una distribución de perturbaciones sellada y un protocolo de
exploración declarado, se observaron —o no se observaron— tipos candidatos reproducibles compatibles
con la definición operacional de C3.*

---

## 7. A — lo que B0 desbloquea

Si B0 pasa la puerta, se monta la fase completa **tal como la describe la v3**, con estos cambios ya
incorporados: el primario sobre todo B con veto (no sobre el residuo), el residuo medido bajo
`L/I/T/e/K` con dos autores, los tres prompts —afinado, **contrato reconstruido** y genérico—, el
manifiesto sellado, el puntuador clavado y auditado, el tipo canónico sellado, y el tamaño como
regla y no como número.

📏 **La aritmética, con la precisión ya decidida:** aceptada una semianchura de **±15 puntos**
sobre una tasa de detección por tipo cerca del 25 %, hacen falta **`N_bajo` = 32 tipos
aproximadamente independientes** (§11.1). Con dependencia fuerte entre tipos hay que abandonar el
intervalo binomial simple e ir a **bootstrap por familia o mecanismo**, que es además lo que impide
contar como 32 observaciones lo que son unas pocas familias.

🧑 **El modo del primario es el agente con herramientas** (§11.7), y **los tres prompts se corren en
ese modo**: afinado, contrato reconstruido y genérico, una pasada cada uno. Así las cifras nuevas
son comparables con el +0,629 del reservado, y el modo techo queda donde estaba, como diagnóstico.

---

## 8. Cómo fracasaría B0, y qué lo destapa

**Las auditorías van antes que la capa**, y ninguna encarga nada.

**Auditoría A · interfaz común de evidencia.** Agente, `v3` congelado y autores de reglas reciben
**exactamente lo mismo**, salvo que la diferencia sea el objeto explícito de estudio. Sin esto, un
candidato C3 puede ser solo una diferencia de instrumentos.

**Auditoría B · el puntuador.** 🔍 Decide qué es detección y qué es falsa alarma, viene calibrado
contra A, y sus 16 autopruebas están escritas contra el vocabulario de A: un tipo de B que no
encaje en las tres clases obliga a un mapeo que decide el autor. **Muestra estratificada** —
positivos, limpios, silenciosos, ACK erróneos, disputados y casos donde agente y reglas discrepan—,
**juez humano ciego al brazo y con orden aleatorizado**, y **sensibilidad y especificidad por
estrato, no acuerdo global**: 🔍 *un 90 % global engaña si casi todo son negativos fáciles*.

**Auditoría C · validez de la propia medida del prior.** Definición C1 contractual frente a C2 de
catálogo; procedencia y diff de `v3-invariante` y `v3-completo`; igualdad de interfaces; puntuador
en las discrepancias.

**F1 · la capa solo produce ruido.** Piloto de humo de **50 ejecuciones** con 2-3 relaciones
críticas, antes de tener la capa entera. Después el piloto completo.

**F2 · todo B sale de la misma familia.** 🔍 Y la regla del 60 % de la v3 **no arregla nada por
declararla**: pasa a ser **regla de interpretación**. La macro global no se usa como afirmación de
generalidad si una familia domina; hace falta un mínimo de familias con un mínimo de tipos para un
resultado transversal, **o se declara que el alcance es solo la familia dominante**.

**F3 · el oráculo imprime su firma.** §4.3 y §4.4, con la mediana de tipos-por-invariante.

**F4 · contaminación semántica con A.** 🔍 Excluir los diez **por identidad** no basta: B puede dar
**variantes del mismo arquetipo** —mismo mecanismo con otro disparador, misma invariante en otro
campo, mismo patrón `AA`/recurso—. **Para B0 no bloquea**, porque B0 no promete exposición cero.
**Para A es indispensable** y va antes de cualquier afirmación de novedad semántica.

**F5 · el adjudicador no es ciego.** §4.5.

**F6 · B es rara por construcción.** §4.7, con el AUC del adversario de rareza.

**F7 · «tipo» indefinido.** §4.6, con la κ de tipo.

**F8 · 🧑 el que no sé ver.** La v1, la v2 y la v3 cayeron las tres por aquí. **Esta v4 vuelve al
panel antes de sellar el manifiesto.**

### Y las siete condiciones que invalidarían el prior medido 🔍

Las tres primeras lo invalidan; las otras cuatro lo debilitan y obligan a reetiquetar:

1. `v3-invariante` usa, directa o indirectamente, conocimiento no contenido en contrato y bundle;
2. reglas y agente **no reciben la misma evidencia**, o el agente la recibe por el prompt, el estado
   oculto, el orden, los metadatos o las herramientas;
3. la concordancia del puntuador con jueces ciegos **cae del 90 % en los estratos relevantes**;
4. se cuentan **18 operadores correlacionados** como 18 observaciones independientes;
5. se etiqueta como C1 contractual algo cubierto solo por una regla informada por catálogo;
6. no se demuestra, por revisión o ablación, que la señal discriminante **esté en el bundle**;
7. una **segunda implementación independiente** de reglas de contrato revela cobertura muy distinta
   de `v3-invariante`.

---

## 9. El orden

```
 0. AUDITORIAS, sin capa y sin agente
    A. interfaz comun de evidencia
    B. puntuador: estratificado, juez ciego, sensibilidad y especificidad POR ESTRATO
    C. validez de la medida del prior (C1 vs C2, procedencia de v3-invariante)
 1. RELACIONES por dos autores, uno ciego al PROMPT, con clausula cada una
    + tabla de solapamiento relacion <-> prompt
    + validadores de tercero (d) y determinismo/replay (e) montados
 2. MANIFIESTO sellado: capa, semillas piloto/confirmatorio, tipo canonico, r=5,
    k_min, rubrica, puntuador, LAS DOS PUERTAS DE LA §5 y la regla de parada
 3. piloto de humo: 50 ejecuciones, 2-3 relaciones criticas   <- mata F1 barato
 4. PILOTO COMPLETO (~300 ejec., semillas disjuntas)
    -> tasa base, distribucion por familia y por via, AUC del adversario de rareza,
       control positivo con los diez, y una hora de capa sin oraculos
 5. miniadjudicacion ciega + DOS AUTORES DE REGLAS sobre los candidatos C3
 6. LA PUERTA. Si no pasa: se cierra, y el resultado es el de la §5
 --------------------------------------------------- nada encargado hasta aqui
 7. solo si pasa: auditoria completa de contaminacion A<->B y del prompt afinado
 8. curacion a ciegas, congelar, preinscribir, sellar
 9. UNA pasada
```

🔍 **Lo que cambia respecto a la v3, y es la respuesta de GPT a la pregunta que se le hizo:** la
auditoría de contaminación semántica **ya no bloquea B0**, porque B0 no promete exposición cero. **Sí
bloquea cualquier paso a A y cualquier afirmación fuerte sobre novedad.**

---

## 10. Lo que se hereda y lo que decae

**Se hereda:** el circuito congelado con sus 27 pruebas, el arnés, las clases del agente,
`comparar.py`, la maquinaria de sellado, la matriz de observabilidad, el banco de adversarios, los
tres triadores, y **el bundle ya definido y verificado**. El **puntuador se hereda bajo auditoría**.

**Decae de la v3:**

- la regla de rigor «solo entra si el adjudicador señala la cláusula», que vaciaba C3;
- «la cuota de (a) prueba algo sobre el sesgo de (b)»;
- ceguera del autor de relaciones **solo** respecto a la capa;
- el 25 % como nulo, y la mayoría simple como criterio de «detectado»;
- `k` por recurrencia, y apartar singletons como única defensa;
- «(c) acota lo que (a) y (b) dejan fuera» — 🔍 **con tasa base del 1 %, (c) uniforme no puede
  acotar el recall de (b) a ningún `n` asequible.** Lo que sí puede: **precisión** sobre sus propios
  aciertos (bastan ~50), la κ sobre el conjunto enriquecido, y publicar la cota `3/n` **con esas
  palabras: cota, no estimación**;
- la regla del 60 % como declaración;
- las etiquetas E1/E2 del informe del prior, sustituidas por C1/C2/C3/O0.

---

## 11. Decidido 🧑 el 22-sep

Las siete se cerraron el mismo día, antes de sellar nada. Cada una con lo que arrastra.

**1 · La precisión mínima: ±15 puntos, luego `N_bajo` = 32.** Para una tasa de detección por tipo
cerca del 25 %, `N = 1,96² × 0,25 × 0,75 / 0,15² ≈ 32` tipos aproximadamente independientes. Es el
punto donde la fase sigue siendo alcanzable y el intervalo todavía dice algo; por debajo empieza a
cubrir a la vez el negativo y un positivo trivial. 🔍 Coincide por otro camino con el cálculo de
potencia de la quinta revisión, que para distinguir 0,25 de 0,50 a una cola con potencia 0,80 pide
unos 21 tipos. **`lambda_C3_inferior` y el presupuesto `E` salen de la aritmética tras el piloto**
(§9 paso 4b), pero la **regla** ya está firmada aquí y no se toca después.

**2 · Los autores: modelos nuevos, en sesiones limpias.** Con paquete de contexto sellado —contrato,
estándar, documentación del bundle e instancias **anonimizadas**— y **familia registrada**. Permite
replicar con varias semillas, y de ahí sale la κ sin coste. **Su límite, declarado:** no se puede
garantizar que no conozcan HL7 por entrenamiento, así que su cobertura es cota superior de lo que
cubriría un integrador sin ese conocimiento.

> ⚠️ **Los cinco revisores del panel quedaron quemados para estos papeles**, y el autor del
> laboratorio también. El encargo de la ronda B les enseñó los resultados de la Fase 12 enteros —la
> escalera, el 16 de 18, la medida del prior—, y el requisito es no haberlos visto. Quien escriba
> relaciones, reglas o adjudique tiene que venir de fuera de todo lo anterior.

**3 · Los adjudicadores: lo mismo**, dos modelos nuevos ciegos entre sí. 🔍 Aquí el reproche que
pesaba sobre los autores de reglas —que el modelo sepa HL7 de fábrica— deja de ser un defecto y pasa
a ser lo que hace falta para juzgar contra el estándar. La κ que importa es la de **asignación de
tipo** (§4.6), y se saca replicando.

**4 · Acceso controlado: sí al puntuador y al prompt, no al catálogo.** Se puede entregar a un
tercero el puntuador con su `ideal_b` y sus desacuerdos, y el prompt afinado con su partición
trazable entre contrato, procedimiento y material derivado de A. **El catálogo A no sale**: el repo
es privado a propósito porque lleva dentro la clave del banco, y enseñarla es irreversible.

> **Lo que eso cuesta, y se escribe aquí:** la auditoría del puntuador (§8, B) y la del prompt se
> pueden hacer enteras. La de **solapamiento semántico A ↔ B** (§8, F4) **no**, porque necesita el
> catálogo. Por tanto **«exposición cero» no se podrá afirmar nunca en esta fase**, y el cero del
> prior se publica como **hallazgo limitado, no como clausura**. Las dos cosas quedan dichas en el
> informe con esas palabras.

**5 · Vía (d): el validador oficial de FHIR primero.** Instalar java y el `validator_cli` oficial, y
validar contra el perfil el recurso `Patient` **realmente escrito** —que los oráculos sí pueden
leer, aunque los brazos no—, más un validador de conformidad v2 sobre el acuse. Horas de trabajo y
**firma del estándar tal cual**, no de una lectura mía. Cubre lo estructural, no lo semántico del
mapeo. 📏 En disco ya están `estandares/v2mappings/` —el IG normativo v2-to-FHIR, legible por
máquina— y la especificación R4; **no había java ni ningún jar**; se instalaron el mismo día (java 21 y `validator_cli` v6.10.4, 192 MB, fuera del repo). El
mapeador de referencia desde el IG queda como segundo peldaño.

> ⚠️ **MEDIDO EL MISMO DÍA, Y MATIZA ESTA DECISIÓN.** Con la predicción sellada antes de instalar
> nada (`PRE-VIA-D.md`, `7c2e6779`), el validador oficial se corrió sobre los recursos `Patient`
> **realmente escritos**: **0 de 3** fallos vistos, y **la misma única advertencia `dom-6` en los
> dieciséis recursos**, fallos y limpios por igual —1,00 contra 1,00 por caso—. **La mitad FHIR de
> la vía (d) es ciega al fallo silencioso.** Detalle en `VIA-D-RESULTADO.md`.
>
> (d) se decidió porque aportaba **un oráculo cuya firma no es la mía**; medido, esta mitad aporta
> un oráculo que **no ve nada**, y no es lo mismo. Queda en pie **la mitad v2**, el validador de
> conformidad sobre el **acuse**, que es el que podría ver los otros tres fallos vivos —el `CE` en
> modo original, el `AE` que no llega y el 4xx contestado `AR` con `ERR-3=102`—, y esos sí son no
> conformidades de verdad y no de tipo de dato. **Es la próxima medida, y es barata.** Si tampoco ve
> nada, la conclusión honesta es que **ninguna vía ve el silencio sin firma propia**, y eso se
> escribe en el informe en vez de pagar el mapeador fingiendo que es un tercero.
>
> ⚠️ **LA MITAD v2 TAMBIÉN SE MIDIÓ, Y TAMPOCO VE NADA** (`VIA-D-V2-RESULTADO.md`, predicción
> sellada `f7c897ac`). Con `hl7apy` 1.3.5 y su control negativo pasado: **0 de 2**, y además **uno
> de los tres fallos ni siquiera es recuperable** —el `MSA|CE` del FailureTimeout no deja acuse
> almacenado, solo una línea de log—. El control que decide comparó cada acuse con su variante
> **corregida** (`101`→`100`, `102`→`207`): **6 de 6 idénticos**. El comprobador dice lo mismo con
> el código bueno que con el malo.
>
> **Conclusión de las dos mitades, y la razón transfiere:** *un oráculo de estantería comprueba que
> el mensaje esté bien formado y que sus códigos existan; un fallo silencioso es un valor válido en
> la situación equivocada.* **El oráculo independiente que la vía (d) prometía no existe con
> herramientas de estantería en este circuito.** O se paga el mapeador de referencia **declarando
> que la firma es mía** —misma categoría que `v3-invariante`—, o se escribe que aquí no hay oráculo
> ajeno. Lo que ya no se puede decir es que (d) aporte una firma que no sea la mía.

**6 · El control positivo (vía g) se activa, y hay cinco.** 📏 Comprobado contra los payloads
medidos del circuito congelado, no contra la bitácora: siguen vivos **el acuse `CE` no conforme y el
`AE` que no llega**, **la entrada sin desescapar** (`Ferrándiz\S\Soler` llega literal al canónico,
con `AA` y `HTTP 201`), **el 4xx de FHIR contestado `AR` con `ERR-3=102`**, **`MAXREP=10` descartando
el `MR` de la repetición 11** (el canónico pone el primer `PI`) y **`PV1` antes de `PID` contestando
101 con PID-3 lleno**. El de los acentos se arregló en la Fase 11bis, el del código 404/401 parece
arreglado, y los dos restantes son del aparato y no del circuito. La capa tiene que reproducir esos
cinco disparadores y las vías (a), (b), (d) y (e) tienen que verlos: **«el oráculo ve X de cinco» es
la única medida de recall que no cuesta un curador**. Van luego a su estrato aparte igualmente.

**7 · El modo del primario: el agente con herramientas.** Es lo que la pregunta del laboratorio dice
—un modelo local que llama a herramientas— y el modo techo fue un diagnóstico, no el producto. 📏 El
desajuste era real: `brazo_B` es el agente con herramientas (lleva columnas de llamadas y vueltas; el
reservado registra `qwen3-coder:30b`, T = 0, 8 iteraciones, huella `89ae1c8d`) y dio **+0,642 /
+0,629**, mientras que la comparación de prompts del paso 29 es **modo techo**, +0,787 contra +0,615.
**Los tres prompts se corren con herramientas**, una pasada cada uno, y así las cifras nuevas son
comparables con el +0,629 del reservado.

---

## 12. Lo que sigue abierto, y no es 🧑

- `lambda_C3_inferior` y `E`, que **no se deciden: se calculan** tras el piloto (§9 paso 4b) con la
  regla ya firmada en la §11.1.
- Quiénes son, en concreto, los modelos nuevos de los papeles 2 y 3 — la **decisión** está tomada
  (modelos nuevos en sesión limpia con familia registrada); falta elegirlos y registrarlos en el
  manifiesto.
