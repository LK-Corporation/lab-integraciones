# Revisión del diseño de la Fase 13 — Fable, 22-sep-2026

**Qué he leído:** `encargo_fase13.md` y `PRE-TEST.md` (v3, 22-sep). **Qué no he leído:** el catálogo, la
clave, las tablas de casos, `afinado/*`, `desarrollo/*`, `agente/*`, ni ninguna medición caso a caso.
Donde necesito un dato que no tengo, lo digo y no lo supongo (anexo A).

**Resumen en cinco líneas.**

1. La pregunta es la buena en espíritu y mal formulada en la letra: el modelo no «generaliza» porque no
   aprendió A; lo que se mide es **cuánto de la capacidad del agente era específica del prompt afinado
   contra A** y **cuánto de la victoria del script era conocer el catálogo**. Las dos cosas se pueden
   medir, y una de ellas **sin construir B**, en la primera semana.
2. El modo de fallo más probable no es que el autor ciego escriba tipos «mecánicos»: es que escriba
   **tipos que ya están en A con otro nombre**, porque ve el mismo contrato del que salió A. El segundo
   es que B sea nuevo pero **inobservable** por las tres herramientas, y «los dos se hunden» se lea como
   un resultado sobre el modelo cuando es un resultado sobre la observabilidad.
3. Hay un tercero que produciría un **falso positivo a favor del modelo** y que nadie celebraría con
   cuidado: el adversario lee columnas `medido_*`/`can_*` y el agente lee texto crudo. Si B perturba algo
   que ninguna columna mide, el script «se hunde» por el sensor, no por las reglas.
4. Los tres se destapan con una misma medida barata, ex ante y sellada: **clasificar cada tipo de B en
   cuatro clases (misma invariante / relación no comprobada / semántico / inobservable) antes de que
   corra ningún brazo**, con un piloto de 3–5 tipos en la primera semana y una regla de parada escrita.
5. El endpoint primario es la **tabla de discordancia por tipo** (agente-sí/script-no contra
   script-sí/agente-no), con un test de signos, acompañada **inseparablemente** de las falsas alarmas
   sobre gemelos benignos. Ningún escalar agregado como titular.

---

## 1. La pregunta

### 1.1 Lo que está mal en «¿generaliza el modelo a tipos no vistos?»

«Generalizar» importa un marco de aprendizaje automático que aquí no aplica. `qwen3-coder:30b` no vio
A en entrenamiento; lo que se desarrolló contra A fue el **prompt** (`afinado/`). El agente es
*modelo + prompt afinado*, y la Fase 12 no separó las dos partes. Así que la pregunta real tiene dos
mitades, y conviene escribirlas por separado porque tienen respuestas distintas y medidas distintas:

- **(a) Especificidad del prompt.** ¿Cuánta de la detección del agente en A (10 de 18) depende de que
  el prompt fue afinado mirando A? Se mide con un **brazo de prompt genérico** («eres integrador
  HL7/FHIR; di si esta traza produjo el Patient correcto») corrido sobre el mismo reservado de A. No
  hace falta B. Si el prompt genérico saca 8–10 de 18, la capacidad es prior del modelo y la Fase 13
  tiene sentido. Si saca 2 de 18, el agente es un sistema de reglas escrito en lenguaje natural, y en
  B «los dos se hunden» es el resultado esperado, no un hallazgo.
- **(b) Cobertura de las reglas.** ¿Cuánta de la victoria del script (16 de 18) depende de conocer el
  catálogo? La propia Fase 12 lo dice: «ganó porque el conjunto está cerrado y el autor lo conoce
  entero». Eso convierte a `regex v3` en un **techo con oráculo**, no en el comparador que un
  integrador tendría de verdad. El comparador realista es el script que un integrador escribiría **a
  priori**, con el contrato y sin el catálogo.

### 1.2 La formulación operativa que propongo

> Sobre tipos de fallo que no estaban en el catálogo y que son observables por las tres herramientas,
> **¿qué detecta cada brazo congelado contra A, con qué falsas alarmas sobre gemelos benignos, y cuánto
> cuesta que las reglas los alcancen?**

Tres números, no uno: detecciones por tipo, falsas alarmas por tipo, y coste de actualización (horas y
reglas para que v4 alcance B). El tercero es el que le importa a quien decide si desplegar un modelo:
el valor del modelo, si existe, es **la detección durante el intervalo entre que aparece un fallo nuevo
y alguien escribe su regla**. Sin medir el intervalo, «el modelo generaliza» no vale nada operativo.

### 1.3 Una pregunta mejor que el montaje ya permite, sin B

**«¿Bate el agente a las reglas que un integrador escribiría a priori?»** Es la pregunta que la Fase 12
quiso contestar y no pudo, porque su único adversario fuerte sabía la respuesta. Se contesta con un
brazo nuevo y barato, **`reglas-ciegas`**: una persona que ve el circuito y el contrato pero **no** el
catálogo ni los datos escribe el triador mecánico que escribiría en producción, en un tiempo acotado
(dos días). Se sella y se corre sobre el reservado de A.

- Si `reglas-ciegas` saca ~8 de 18 y el agente 10 de 18, la conclusión de la Fase 12 cambia de signo
  sin tocar el corpus: el agente perdió contra un oráculo, no contra un integrador.
- Si `reglas-ciegas` saca 14 de 18, la Fase 12 se confirma y B es la única salida.

Versión pobre si no hay una segunda persona: **`v3-invariante`**, el propio v3 con las reglas
clasificadas como «firma del catálogo» apagadas y solo las «invariantes del contrato» (HL7 PID-3 =
Patient.identifier, etc.) encendidas. La clasificación la hace el autor de v3 y se sella **antes** de
que exista B. Es menos limpia porque el clasificador está contaminado, pero es gratis y además sirve
para la atribución por regla del §3.

**Recomendación:** B sigue siendo necesario, pero los dos brazos anteriores (prompt genérico,
reglas-ciegas o v3-invariante) se corren **en la semana 1 sobre A**, porque cada uno cambia la
interpretación de B y cuestan un día.

### 1.4 Condiciones para que la Fase 13 sea contestable con este laboratorio

Es contestable **si y solo si** se cumplen cuatro condiciones, todas verificables antes de correr nada:

| condición | si no se cumple, el resultado se lee como… |
|---|---|
| C1. Cada tipo de B está **adjudicado como observable** por las tres herramientas, por alguien que no es su autor | «los dos se hunden» = «nadie puede», no «el modelo no generaliza» |
| C2. Cada tipo de B está **auditado contra A**: idéntico / variante / nuevo, sellado | «el script aguanta» = «B era A», no «las reglas generalizan» |
| C3. Los dos brazos leen **la misma información** (mismo sensor, sellado, corrido sin cambios sobre B) | «el script se hunde» = «al sensor le falta una columna» |
| C4. B lleva **gemelos benignos** que tocan el mismo sitio sin producir fallo | «el agente aguanta» = «el agente marca todo lo raro» (la trampa de agregación de la 12, al revés) |

Sin C1–C4 la fase no es contestable, y lo diría ahora: el diseño del encargo tiene C2 a medias (el
autor no ve A, pero nadie audita lo que entrega contra A) y no tiene C1, C3 ni C4.

### 1.5 Lo que no va a contestar salga como salga

Un modelo, una temperatura, un circuito, uno o dos autores. La conclusión defendible es «para este
agente y estos tipos escritos por estas personas». Lo único que compra generalidad es **el marco de
muestreo de B** (§2.3): tipos sacados de incidentes reales documentados y no de la imaginación de un
autor. Un segundo modelo local como brazo es barato y convierte «este modelo» en «esta clase de
herramienta»; lo pongo como opcional, no como requisito.

---

## 2. Cómo fracasaría esta fase, y qué medida barata lo destaparía antes

La Fase 12 falló por un defecto **de construcción del corpus** que ningún número del corpus podía
enseñar: hizo falta un instrumento nuevo (el adversario fuerte). La Fase 13 ya tiene el instrumento;
el riesgo se ha movido entero a **la construcción de B** y a **la equivalencia de lo que ven los dos
brazos**. Ordeno por probabilidad × invisibilidad, no por gravedad.

| # | modo de fallo | por qué sería invisible hasta el final | medida barata que lo destapa | cuándo |
|---|---|---|---|---|
| F1 | **B es A con otro nombre.** El autor ve el contrato; A salió del contrato; dos personas que enumeran el mismo contrato perturban los mismos campos | Las notas de B se parecen a las de A y se lee como «las reglas generalizan» | **Auditoría de solapamiento** ex ante: alguien con A en la mano (no el autor) mapea cada tipo de B al operador de A más cercano: *idéntico / variante / nuevo*. Sellado antes de correr | piloto, semana 1; después con cada entrega |
| F2 | **B es nuevo pero inobservable** por HL7 crudo + recorrido/acuse + log (estado previo, entorno, semántica sin rastro) | «Los dos se hunden» se publica como «el modelo tampoco generaliza» | **Adjudicación de observabilidad** ex ante, como la matriz del 21-sep: una persona distinta del autor, con solo las tres salidas de un caso, señala dónde está la evidencia. Si no la encuentra, el tipo va al estrato «no identificable», fuera del primario | antes de correr ningún brazo |
| F3 | **Sensor asimétrico.** v3 lee `medido_*`, `can_*` y un contador; el agente lee texto crudo. Si B perturba algo que ninguna columna mide, v3 está ciego **por sensor**, no por regla | Produce el resultado que todos quieren ver («el script se hunde, el modelo aguanta») y nadie lo mira dos veces | Para cada caso de B, **comparar su vector `medido_*` con el de su gemelo**: idénticos = «invisible al sensor», estrato aparte. Y verificar que `medido_*` lo produce un script sellado sobre las tres salidas, **no el generador** (si lo produce el generador, v3 lee metadatos del mutador) | semana 1, medio día |
| F4 | **La clave de B está mal.** El autor cree que su mutación produce un fallo silencioso; el circuito la rechaza con `AE` (es `FALLO_MENSAJE`), o la normaliza (es `SIN_PROBLEMA`), o la función tiene un bug | Los brazos «fallan» contra una clave equivocada: la salida barata que la 12 cerró con `comparar.py` | **`comparar-B`**: correr cada caso por el circuito, comparar acuse y Patient con el gemelo, adjudicar la clase por procedimiento sellado, **no por la intención del autor**. Desacuerdo = cuarentena, nunca reetiquetado a mano después | antes de correr ningún brazo |
| F5 | **El agente es un sistema de reglas escrito en el prompt.** Si el prompt afinado enumera qué comprobar, la «detección» de B mide el solape entre esa lista y B | Se atribuye al modelo lo que hace el prompt | **Auditoría del prompt** (contar tipos enumerados) y **brazo de prompt genérico** sobre el reservado de A (§1.1). Se sella cuál de los dos agentes es el primario **antes** de que exista B | día 1–2 |
| F6 | **El autor ciego escribe tipos igual de mecánicos**, o sobrecorrige hacia tipos inobservables | Es el que el encargo ya ve; se resuelve sin filtrarle la respuesta: §2.3 | — |
| F7 | **Trampa de agregación al revés:** un brazo «aguanta» en B porque marca como fallo cualquier cosa rara en la zona mutada | El mismo mecanismo que escondió el hallazgo de la 12, en dirección contraria | **Gemelos benignos** por tipo (misma función, parámetro benigno, mismo locus, resultado correcto) + techo de falsas alarmas preinscrito por brazo + los 22 limpios de A dentro de la tanda B como regresión | diseño; corre con la tanda |
| F8 | **Pseudo-replicación:** contar casos como independientes cuando la unidad es el tipo, y un autor como si fuera una población | Da significancia con N pequeño y se publica | Unidad = tipo, siempre (§4). Dos autores mínimo. Test de signos sobre tipos discordantes, no McNemar sobre casos | diseño |
| F9 | **Estocasticidad:** «el agente aguanta» es una tanda con suerte | Nadie repite porque la 12 prohibió «correr dos veces y quedarse con la mejor» | Tres pasadas, **las tres se publican**, la primera es la primaria por preinscripción. No es elegir la mejor | corre con la tanda |
| F10 | **Fuga por personas.** Si el «autor ciego» es el autor del laboratorio con otro sombrero, o ha leído los informes de la 12 (que describen al adversario), no hay ceguera | Nadie lo escribe | Registro publicado de roles y de documentos entregados a cada persona. Canal de preguntas del autor por escrito y publicado íntegro. Autor de v3, afinador del prompt y autor de B son **tres personas**, o la fase lo declara | día 1 |
| F11 | **Rendimiento de tipos.** De cada 10 encargados, X no pasan C1–C4. Si X es 6, de 20 quedan 8 y no hay potencia | Se descubre con el presupuesto de autoría gastado | El **piloto** de 3–5 tipos mide el rendimiento antes de encargar 40 (§7) | semana 1 |
| F12 | **El puntuador no cubre B.** Sus 16 autopruebas son de las situaciones de A; B puede producir otras (fallo de mensaje *y* silencioso; traza incompleta) | Se ve en los resultados, tarde | Una autoprueba nueva por cada situación que aparezca en el piloto, antes de la tanda | semana 1 |
| F13 | **Mensajes base distintos.** Si el autor escribe sus propios HL7 base, los brazos reaccionan a la distribución de mensajes, no al tipo | Confunde «tipo nuevo» con «hospital nuevo» | Las mutaciones de B se aplican **al mismo pozo de mensajes base de A** (o a un corte reservado de él), entregado por la interfaz del arnés | diseño |

### 2.1 Los tres que más me preocupan, en orden

**F1 (B es A) y F2 (B inobservable) son los dos extremos del mismo eje**, y el diseño actual no mide
en qué punto del eje cae cada tipo. Sin eso, ninguna de las tres salidas del encargo es interpretable:

- «el script aguanta» solo es «las reglas generalizan» si B no es A (C2);
- «los dos se hunden» solo es «el modelo no generaliza» si B es observable (C1);
- «el script se hunde y el modelo aguanta» solo es «valor del modelo» si el sensor es el mismo (C3) y
  las falsas alarmas están acotadas (C4).

**F3 (sensor) es el que produciría un falso positivo con aplausos.** La frase del PRE-TEST «lo que el
circuito hizo, que es exactamente lo que el agente ve» es una afirmación de equivalencia de
información que la 12 no necesitó verificar, porque el que leía menos ganó (conservador). En la 13 esa
asimetría deja de ser conservadora: se vuelve la explicación alternativa más barata del resultado
deseado. Hay que definir el adversario congelado como **sensor + reglas**, sellar los dos, y reportar
B partido por «visible al sensor / invisible al sensor».

### 2.2 La medida única que destapa F1, F2 y F3 a la vez: la clasificación ex ante en cuatro clases

Antes de que corra ningún brazo, una persona con acceso a A y a las reglas de v3 (no el autor de B, no
quien corre la tanda) clasifica **cada tipo de B** y lo sella:

| clase | definición | predicción preinscrita |
|---|---|---|
| **(i) misma invariante, causa nueva** | rompe una relación HL7↔FHIR que una regla de v3 ya cruza (p. ej. PID-5 ≠ `name`), aunque llegue por otro camino | v3 lo detecta; el agente como en A. Replica la 12 |
| **(ii) relación no comprobada** | hay discrepancia en la traza, pero en un campo o relación que v3 no cruza | v3 falla **por cobertura**; el agente puede acertar si lee de verdad. **Aquí vive la pregunta** |
| **(iii) semántico** | HL7 y FHIR coherentes entre sí y bien formados; el resultado es incorrecto solo con conocimiento del contrato o del dominio (sistema de identificador equivocado, código válido pero erróneo, zona horaria, tabla de mapeo) | v3 falla; solo un prior de dominio lo detecta. **Aquí se justifica o no un modelo** |
| **(iv) inobservable** | no deja rastro en las tres herramientas (estado previo, entorno sin log) | nadie. Fuera del primario, como los dos no identificables de la 12 |

Con esto la fase tiene una **regla de parada escrita antes** (el peldaño barato antes del rediseño
caro): si en el piloto ninguno de los 3–5 tipos cae en (ii) o (iii), **no se encargan 40 tipos**; se
cambia el marco de muestreo del autor (§2.3) y se repite el piloto. Y el informe final publica la
composición de B por clase junto al resultado, para que nadie lea «las reglas generalizan» sobre un B
que era 90 % clase (i).

### 2.3 El dilema del autor ciego: tipos no obvios sin filtrarle la respuesta

El encargo lo plantea como un dilema de **instrucción** («si le digo que no sean mecánicos, le filtro
la respuesta»). No lo es. Es un problema de **marco de muestreo** y de **medición de una covariable**.
Se resuelve con cuatro piezas, ninguna de las cuales le dice al autor qué detecta el adversario.

**Pieza 1 — No le digas nada sobre mecánico o no. Cambia de dónde saca los tipos.** El riesgo de que
los tipos sean obvios (o de que sean A) viene de que el autor, sentado ante el contrato, enumera
mapeos y los perturba: eso es un generador de firmas, y es exactamente lo que hizo A. La corrección es
quitarle el contrato como fuente primaria y darle **un marco de muestreo externo y preinscrito**:

> «Al menos la mitad de los tipos deben proceder de incidentes documentados fuera de este laboratorio
> —hilos de Zulip de FHIR, issues de HAPI, IRIS o Mirth, erratas de guías de implementación, informes
> de connectathon, incidentes de su propia experiencia en producción con fecha y contexto—, tomados
> **en el orden en que los encuentre** hasta completar N, descartando solo los que este circuito no
> pueda reproducir. Cada tipo lleva su procedencia.»

La regla de orden («los primeros N que encuentre») sustituye el gusto del autor por un procedimiento.
El resto pueden venir de su experiencia como integrador, pero cada uno con una **historia de
producción** («esto pasa cuando el HIS X hace Y»): la exigencia de procedencia empuja hacia el
realismo sin mencionar la detectabilidad, y encaja con la preferencia declarada de este laboratorio
por lo parecido a producción.

**Pieza 2 — Lo que el autor recibe y lo que entrega, por escrito y publicado.**

Recibe: el circuito corriendo (caja negra); el contrato de la transformación; la interfaz del arnés
(cómo se enchufa una función de mutación en Python, el pozo de mensajes base, si el arnés admite
mutaciones de entorno o de estado previo); las **definiciones públicas de las clases de veredicto**,
incluida `RESULTADO_INCORRECTO_SILENCIOSO` (no es una fuga: es la variable dependiente); y la
**postura del contrato** sobre entrada semánticamente errónea mapeada fielmente (¿fallo del circuito
o `SIN_PROBLEMA`?), porque sin esa postura la clave de B es ambigua.

No recibe: el adversario, el catálogo, el agente, el prompt, los informes de la Fase 12, ni una sola
palabra sobre «mecánico», «firma», «regex» o «qué detecta qué».

Entrega, por tipo: nombre; descripción del fallo **en términos de producción** (qué se rompió aguas
arriba o en el motor, y por qué ocurre en el mundo real); procedencia; la función de mutación **con
parámetros** (para que no exista un literal fijo); una **variante benigna** (mismo locus, mismo
parámetro, resultado correcto) que será el gemelo; la clase de veredicto que espera; y un **puntero de
evidencia** (en cuál de las tres herramientas y dónde se ve). El puntero no va a ningún brazo: lo usa
solo la adjudicación de observabilidad (C1).

**Pieza 3 — Mide la obviedad después, como covariable, sin el adversario.** Dos autores, A1 y A2,
ciegos entre sí. Cuando entregan, **A2 recibe los casos de A1** (solo trazas y gemelos, sin la
descripción) y escribe en tiempo acotado la regla más simple que separe caso de gemelo; se registran
**minutos y longitud de la regla**. Y al revés. Eso da una **puntuación de obviedad mecánica por tipo**
que no usa v3, que el autor del tipo no ve, y que no le filtró nada a nadie. Se sella y B se
estratifica: «regla en menos de 10 minutos y una sola condición» = obvio; el resto = no obvio. El
primario se preinscribe sobre todo B*; la secundaria, sobre el estrato no obvio. Si el estrato obvio
es más del 70 % de B, la fase lo publica como tal y dice que en esa parte replica la 12.

Versión pobre con un solo autor: el **diff contra el gemelo** en las tres salidas (tamaño del diff, y
si es un token en posición fija o un cambio relacional entre HL7 y FHIR). Más ruidoso, pero también ex
ante y también sin adversario.

**Pieza 4 — La clasificación (i)–(iv) del §2.2** decide si la fase puede contestar; la obviedad de la
pieza 3 decide cómo se lee. Las dos se hacen antes de correr y se sellan.

**Lo que no haría:** pedirle «que sean difíciles»; darle ejemplos de A «para que no los repita» (le
enseña las firmas); o dejar que el autor del laboratorio filtre la entrega a ojo («este es demasiado
fácil»). Cualquiera de las tres contamina más de lo que corrige. Si un tipo es obvio, **se queda, se
etiqueta y se estratifica**. Filtrar la entrega es la forma más segura de fabricar el resultado.

**Sobre «ver el circuito».** Ver el circuito corriendo es inevitable (tiene que probar sus funciones),
pero hay que decidir si ve **el código de la transformación** o solo el contrato y el comportamiento
observable. Con el código, el autor escribe tipos contra la implementación (variantes de A, clase i);
con el contrato y la caja negra, escribe contra la especificación, que es lo que hace un integrador
que no es el desarrollador. Recomiendo **caja negra + contrato**, y publicar cuál fue.

---

## 3. El adversario congelado

**Es honesto congelarlo como un brazo. No es honesto que sea el único.** El v3 congelado es la
operacionalización literal de «nadie ha escrito una regla»: mide qué le pasa a un sistema de reglas
cuando el mundo cambia y nadie lo toca. Eso existe en producción (el intervalo entre el fallo nuevo y
la regla). Pero el encargo tiene razón en que el integrador actualiza, y la pregunta operativa es
**cuánto tarda y cuánto le cuesta**. Se miden las dos cosas, en este orden y con esta separación:

**Diseño 2×2 sobre B-test.** B* (los tipos que pasan C1–C4) se parte **por tipo**, al azar y
estratificado por clase (i)/(ii)/(iii), en B-dev y B-test; la partición se sella antes de correr nada.

| | script | agente |
|---|---|---|
| **congelado contra A** | v3 tal cual (sensor + reglas, sellado) | prompt de la 12, sellado |
| **actualizado en B-dev** | v4: el autor de v3 ve **solo B-dev** (casos + clave), presupuesto acotado y registrado | agente-v2: el afinador ve **solo B-dev**, mismo presupuesto |

Los brazos congelados corren sobre **todo B\***; los actualizados solo sobre **B-test**, que son
**tipos distintos** de los que vieron. Si el actualizado solo viera casos nuevos de los mismos tipos,
sería la Fase 12 otra vez: 100 % garantizado y nada aprendido.

**Secuencia para que no haya fuga:** (1) corren los dos congelados sobre B\*; resultados sellados y
**no mostrados** a los actualizadores; (2) el autor de v3 recibe B-dev y produce v4 en tiempo acotado
(p. ej. dos jornadas), con registro de horas, iteraciones y reglas añadidas; el afinador recibe B-dev
y produce agente-v2 con el mismo presupuesto; los dos se sellan; (3) v4 y agente-v2 corren sobre
B-test; (4) se abre todo. Si el autor de v3 viera qué tipos detectó el agente, escribiría reglas para
esos, y el «valor del modelo» se evaporaría por construcción.

**Qué significa cada celda, preinscrito:**

| resultado | lectura |
|---|---|
| v3 se hunde en B\*, agente aguanta | hay prior que las reglas no tienen; el valor es **la detección durante el intervalo** |
| v4 alcanza techo en B-test (tipos no vistos) con pocas horas | las reglas **generalizan una vez que alguien mira**: el valor del modelo queda acotado por horas de integrador; se publica el coste |
| v4 no alcanza techo en B-test | los tipos de B no son «regla-bles» con ese presupuesto: el resultado más fuerte posible para el modelo, **si** el agente aguanta |
| v3 aguanta en B\* por reglas **invariantes** | las reglas generalizan de verdad; publicable |
| v3 aguanta en B\* por reglas **de firma** | B era A (F1); no se aprende nada del script, y algo malo de B |
| agente-v2 mejora mucho sobre el congelado | la capacidad del agente es afinado, no prior; refuerza F5 |

**Atribución por regla, la pieza que falta en el encargo.** Antes de que exista B, el autor de v3
clasifica cada regla de v3 como **invariante del contrato** (cruza HL7 con FHIR o con el acuse) o
**firma del catálogo** (reconoce la huella de un operador), y lo sella. En la tanda, cada detección
del script sobre B registra **qué regla disparó**. Sin esto, «el script aguanta» es ilegible; con
esto, distingue las dos últimas filas de la tabla. Es medio día de trabajo.

**El orden importa también aquí:** v3 corre sobre B **antes** que el agente, y su atribución (por
regla, por sensor, por clase) se hace y se sella antes de ver un solo veredicto del agente. Así el
«se hunde / aguanta» del script no se interpreta con la retrospectiva del resultado del agente.

---

## 4. El endpoint, sin la trampa de la agregación

**Unidad: el tipo.** Nunca el caso (los casos de un tipo comparten firma: contarlos es
pseudo-replicar), nunca un escalar que mezcle clases.

**Endpoint primario.** Sobre B\* (clases i–iii, observables, con clave verificada), para cada brazo
congelado *a* y cada tipo *t*:

> `detecta_a(t)` := al menos 3 de 5 casos de *t* con veredicto **exactamente** igual a la clase
> sellada (para los tipos silenciosos, `RESULTADO_INCORRECTO_SILENCIOSO`; `NO_SE` no cuenta).

La tabla de discordancia **por tipo**, que es la misma que cerró la Fase 12 pero en la unidad
correcta:

```
   agente SÍ, script NO : n10   <- lo que aporta el modelo
   agente NO, script SÍ : n01
   los dos              : n11
   ninguno              : n00
```

Estadístico primario: **n10 − n01**, con test de signos exacto sobre n10 + n01, unilateral en la
dirección preinscrita, α = 0,05. Se publican los cuatro números siempre.

**Compañeros inseparables, publicados en la misma tabla, nunca restados:**

- `FA_a` := número de **gemelos benignos** de B\* en los que el brazo *a* emite algo distinto de
  `SIN_PROBLEMA`, sobre el total de gemelos; y la regresión sobre los 22 limpios de A dentro de la
  tanda.
- `NS_a` := fracción de casos de B\* con `NO_SE`. Un agente que responde `NO_SE` a todo lo raro no
  generaliza: se abstiene.
- **Techo preinscrito:** si `FA_a` supera el techo (propongo 5 % de gemelos, o 2 de los 22 limpios de
  A), el brazo **no cualifica**: sus detecciones se publican, pero la conclusión de la fase no puede
  descansar en él. Es un cortafuegos, no una penalización que se sume.

**Desglose obligatorio junto al primario** (cada uno con su n10/n01):

1. por clase (i) / (ii) / (iii) — es el desglose que contesta la pregunta;
2. por visibilidad al sensor (`medido_*` distinto del gemelo o no);
3. por estrato de obviedad (§2.3, pieza 3);
4. por dónde está la evidencia (HL7 crudo / recorrido-acuse / log);
5. por autor;
6. para el script, atribución por regla (invariante / firma) en cada detección;
7. para el agente, las tres pasadas, con la primera como primaria.

**Secundarios:** el puntuador macro de la 12 (θ = 0,225, K = 0,5) por clase, **solo por continuidad**,
nunca como titular; Wilcoxon de rangos con signo sobre las tasas de detección por tipo (agente −
script), que tiene más potencia que el signo pero es menos legible; la caída descriptiva de cada brazo
de A a B (no comparable en dificultad: descriptiva, sin test); duración por caso y llamadas por
herramienta; y los brazos actualizados sobre B-test (§3) con sus horas.

**Prohibido:** un total que sume clases; un «gana/pierde» en una palabra; elegir a posteriori qué
desglose es el titular. El titular es la tabla de discordancia sobre B\* y, debajo, la misma tabla por
clase (i)/(ii)/(iii).

---

## 5. Tamaño y potencia

**La unidad es el tipo, y la potencia la fijan los tipos discordantes, no los casos.** En la 12 el
reservado tenía un caso por operador: cada «detecta / no detecta» por operador era una Bernoulli con
la temperatura del modelo dentro. Eso vale para un techo con oráculo (16 de 18 no deja dudas); no
vale para una comparación pareada donde se esperan tipos a medias.

**Casos por tipo: k = 5, umbral ≥ 3 de 5.** Con k = 1, un tipo que el agente acierta el 50 % de las
veces entra en la tabla como cara o cruz. Con k = 5 y umbral 3, un tipo con tasa real 0,8 cuenta como
detectado el 94 % de las veces (contra 80 % con k = 1) y uno con tasa 0,2 solo el 6 % (contra 20 %).
Por encima de k = 6 la ganancia es marginal y el coste crece linealmente. Los 5 casos de cada tipo
van sobre **5 mensajes base distintos** del pozo de A, y cada uno lleva su gemelo benigno.

**Cuántos tipos.** Test de signos sobre discordantes, α = 0,05 unilateral, suponiendo agente al 50 %
por tipo en B (algo por debajo de su 56 % en A) y detecciones independientes entre brazos:

| escenario | script en B | N = 20 | N = 30 | N = 40 |
|---|---|---|---|---|
| **colapso** | 5 % | potencia ≈ 0,91 | > 0,95 | > 0,95 |
| **moderado** | 20 % | ≈ 0,38 | ≈ 0,65 | ≈ 0,80 |
| **parcial** | 35 % | < 0,15 | < 0,20 | ≈ 0,25 |

(Región de rechazo: con 10 discordantes, n01 ≤ 1; con 15, n01 ≤ 3; con 20, n01 ≤ 5.)

Lectura honesta: **esta fase está potenciada para detectar un colapso del script, no una diferencia
moderada, y una diferencia parcial está fuera de alcance con cualquier N realista.** El encargo espera
un colapso («el adversario se hunde»); si lo que sale es parcial, el resultado se preinscribe como
**indeterminado**, no como negativo. Esto hay que escribirlo antes, porque es exactamente el tipo de
resultado que después se lee como se quiera.

**Umbrales absolutos preinscritos** (con N = 30 utilizables; se reescalan al N final antes de abrir):

- script **se hunde** := detecta ≤ 6 de 30 tipos (≤ 20 %); **aguanta** := ≥ 18 de 30 (≥ 60 %); entre
  medias, «parcial»;
- agente **aguanta** := ≥ 10 de 30 (≥ 33 %; bajo p = 0,56 sale con prob. 0,99, bajo p = 0,15 con
  0,01); **se hunde** := ≤ 5 de 30; entre medias, «indeterminado».

**Recomendación de tamaño:** encargar **40 tipos a dos autores (20 + 20)**; con un rendimiento de
60–75 % tras C1–C4 quedan **24–30 tipos en B\***. Volumen: 30 × 5 = 150 casos de fallo + 150 gemelos +
22 limpios de A + 5 canarios de A ≈ **330 casos**, por 3 pasadas del agente ≈ 1 000 ejecuciones. El
coste en horas se saca de la duración por caso medida en la 12 (dato que no tengo): 330 × 3 × *d*.
El script cuesta cero. Lo caro es la autoría: es el recurso que hay que proteger con el piloto.

**Regla adaptativa, decidida sobre el piloto (quemado), nunca sobre los datos primarios:** si en el
piloto v3 detecta entre el 30 % y el 50 % de los tipos (escenario parcial), o se sube el encargo a 60
tipos o se declara desde el principio que la fase solo distingue colapso. Si el rendimiento del piloto
es < 50 %, se encargan 60 en vez de 40.

**Dos autores no son un lujo.** Los tipos de un autor no son 20 extracciones independientes: son 20
extracciones de una cabeza. Con dos, el desglose por autor (§4) enseña si el resultado es del modelo
o del gusto de quien escribió B; y la pieza 3 del §2.3 necesita dos.

---

## 6. El estrato de fallos reales

**Merece la pena, con tres condiciones, y nunca dentro del primario.** Es el único estrato de toda la
serie 12–13 con **tasa base real**: A y B son inventados. Y prueba algo que la 12 nunca probó, porque
su reservado excluyó los `ENV_*` y no tuvo «un solo caso de `ENTORNO`»: el acuse `CE` no conforme,
el 404 en vez de 401 y el bloqueo con `PoolSize=1` son fallos de entorno o de configuración, no de
mensaje.

**Las tres condiciones:**

1. **Etiqueta y cuarentena estadística.** Se publica como tabla aparte, con las mismas columnas que
   el primario, bajo un título que diga «convenience sample, n = 8–10, autor del laboratorio no ciego,
   sin inferencia». Ningún número suyo entra en n10/n01, ni en el puntuador, ni en la frase de
   conclusión. Una frase explícita en las conclusiones: «nada del primario depende de este estrato».
2. **Cinco comprobaciones antes de correrlo, publicadas:** (a) ¿está ya en A como operador? Si sí,
   no es nuevo: sale del estrato. (b) ¿El prompt o v3 lo mencionan? Se busca por texto y se publica el
   resultado. (c) ¿El arnés puede reproducirlo? Son bugs del circuito **ya corregidos**: reproducirlos
   exige desconfigurar (entorno), y `PoolSize=1` puede dejar un mensaje sin traza que triar. (d) ¿Es
   observable por las tres herramientas? El 404 debería verse en el log, el `CE` en el acuse, el
   desescapado en HL7 contra FHIR; el bloqueo, quizá en nada. (e) ¿Tiene clase de veredicto en el
   esquema cerrado? Un mensaje atascado puede no tenerla, y eso es un hallazgo sobre el esquema, no
   sobre el agente.
3. **Uso principal: piloto de la maquinaria (§7).** Como ya existen y no necesitan autor, son el
   material ideal para probar el pipeline entero en la semana 1. La contaminación no importa para
   probar tuberías; sí importa para inferir. Se queman de cualquier inferencia y se reportan como
   estrato descriptivo.

**Lo que aportan si se hace así:** si v3 falla en fallos reales de entorno y el agente los lee en el
log, eso es una **hipótesis** para una Fase 14 con `ENTORNO` de verdad, no una conclusión. Y si el
esquema cerrado no tiene clase para «traza incompleta», eso es una **corrección** al laboratorio que
sale gratis.

**Lo que no haría:** dárselos al autor ciego «como ejemplo de lo que buscamos» (le enseña lo que el
autor del laboratorio ya sabe y le sesga hacia el entorno), ni mezclarlos en B con la excusa de que
«tienen procedencia».

---

## 7. La primera semana: qué medir para no construir sobre arena

La lección de la 12 no es «hay que escribir el adversario fuerte antes». Es **«hay que correr el
pipeline entero, con instrumento y controles, sobre un puñado de casos, antes de gastar el presupuesto
en el corpus»**. Cinco días:

**Día 1 — sellos y roles.** Huellas de v3 (reglas **y** scripts del sensor que producen `medido_*` y
`can_*`), del prompt, del puntuador, del arnés y del pozo de mensajes base, en `SELLO-FASE13.txt`. Se
sellan también: el procedimiento `comparar-B`, la clasificación (i)–(iv) y quién la hace, la partición
B-dev/B-test (como procedimiento), el endpoint del §4 y los umbrales del §5. Registro de roles: quién
escribió v3, quién afinó el prompt, quién es autor de B, quién adjudica observabilidad; y qué
documentos recibe cada uno. Auditoría del prompt: cuántos tipos enumera. El autor de v3 clasifica sus
reglas en invariante / firma y lo sella.

**Día 2 — dos números que recalibran todo, sin B.** (a) **Prompt genérico** sobre el reservado de A:
si saca 8–10 de 18, la capacidad es prior; si saca ≤ 3, la 13 va a dar «los dos se hunden» y hay que
preinscribirlo. (b) **`v3-invariante`** (o `reglas-ciegas` si hay una segunda persona) sobre el
reservado de A: cuánto de los 16 de 18 era conocer el catálogo. Y la **verificación del sensor**:
quién produce `medido_*`; correr la extracción sobre una traza nueva fuera de la tabla; confirmar que
no toca ninguna columna `esperado_*` ni metadatos del generador.

**Días 3–5 — piloto de la maquinaria completa.** Material: el estrato de fallos reales si el arnés lo
reproduce; si no, 3–5 tipos del autor 1, **quemados** (no entran en el primario aunque no cambie
nada). Se corre **todo**: función de mutación → circuito → `comparar-B` → adjudicación de
observabilidad → auditoría de solapamiento → clase (i)–(iv) → gemelos → v3 con atribución por regla →
agente (3 pasadas) → puntuador → tablas del §4. Con los controles negativos ya probados sobre B antes
de usarlos: constantes, siempre `NO_SE`, clave barajada sobre v3 (0 veredictos cambian), literal
canario ausente, y los 5 canarios de A dentro de la tanda detectados por v3 como en A.

Se miden: **rendimiento** (tipos que pasan C1–C4 / tipos entregados), **horas del autor por tipo**,
**segundos del agente por caso**, **composición por clase**, y cualquier rotura del pipeline.

**Día 5 — puerta de decisión, con la regla de parada escrita el día 1:**

| si el piloto enseña… | entonces… |
|---|---|
| ningún tipo en clase (ii) o (iii) | **no se encargan 40 tipos**; se cambia el marco de muestreo del autor y se repite el piloto |
| el prompt genérico ≤ 3 de 18 en A | se preinscribe «los dos se hunden» como esperado y la fase se reencuadra como estudio de especificidad del prompt, con agente-v2 como brazo central |
| `medido_*` lo produce el generador | se reconstruye el sensor como script sobre las tres salidas **antes** de nada; v3 se vuelve a sellar |
| rendimiento < 50 % | se encargan 60 en vez de 40 |
| v3 entre 30 % y 50 % en tipos del piloto | se declara que la fase solo distingue colapso, o se sube el encargo |
| el puntuador no puntúa alguna situación | autoprueba nueva y resello antes de la tanda |

Si el piloto pasa limpio, el encargo a los autores sale el día 6 con el texto del §2.3, y la fase
tiene por delante lo que la 12 no tuvo: un instrumento probado, controles probados y una clasificación
ex ante que hace legible cualquiera de los resultados.

---

## Anexo A — lo que necesitaría ver, sin contaminarme

Nada de esto es la clave ni el catálogo; todo son propiedades del montaje:

1. Los **nombres** de las columnas `medido_*` y `can_*` (no los valores) y **qué script las produce**.
2. Si el prompt afinado **enumera tipos de fallo**, y cuántos (un recuento, no el prompt).
3. La **interfaz del arnés**: si admite mutaciones de entorno y de estado previo, y cómo se aplica una
   función de mutación.
4. **Quién** escribió v3 y quién afinó el prompt (roles, no personas).
5. La **duración por caso** del agente en la 12.
6. Si el JSON de veredicto tiene un campo de **evidencia o motivo**: permitiría el control «acierta por
   la razón correcta» sobre B, que es la única forma de distinguir lectura de suerte por tipo.

**Aviso de contaminación, para el registro.** El scratchpad donde se me pidió escribir este informe
contiene ficheros del laboratorio (entre otros, un `triador_regex_v3.py`, un `taxonomia.py`, un
`observabilidad.py`, un `DISENO-FASE13.md` y una `revision-diseno13-fable.md` de otra sesión). He
visto **solo sus nombres** en un listado de directorio, no he abierto ninguno, y nada de este informe
se apoya en ellos. Para futuros revisores ciegos conviene darles un directorio vacío: los nombres
solos ya enseñan estructura.
