# Encargo: rompe la v2 antes de que se monte la capa de perturbación

Es la **v2 del diseño de la Fase 13**, escrita después de que rompierais la v1. Vuestras tres
roturas —el oráculo es un brazo, Q2 está vacía con un B declarado, el DiD se fabrica— se aceptaron
enteras, y 🧑 eligió la salida cara: **B por emergencia**. Este documento es lo que sale de ahí.

Su propia §7 termina en **F6: «el modo de fallo que yo no sé ver»**, y la v1 demostró que existe.
Aquí está la v2. Rompedla.

---

## Contexto en cinco líneas

La **Fase 12** terminó con las cinco hipótesis preinscritas cumplidas y un resultado negativo: el
agente funciona (10 de 18 operadores, cero falsas alarmas en 22 limpios) **y aun así no hace
falta**, porque un script de expresiones regulares lo bate +0,873 contra +0,629.

La causa **no fue el modelo, fue el banco**: un corpus de **mutaciones declarativas** deja por
construcción una firma mecánica por operador, y un detector escrito contra esas firmas llega al
100 % de lo observable (16 de 18 operadores a 8 de 8). Los dos que falla son exactamente los dos
que la matriz de observabilidad había declarado no identificables **sin correr ningún modelo**.

La **v1 de la Fase 13** intentaba arreglarlo con un B declarado por un autor ciego, estratificado
por un oráculo de mecanicidad. La rompisteis: un B declarado es una función que se puede invertir,
así que **contesta coste, no capacidad**.

La **v2** cambia la forma de producir B: ya no se declara, **emerge de ejecutar el sistema**. Este
encargo es para que su defecto, si lo tiene, salga **hoy** —antes de montar la capa de perturbación
y antes de contratar a nadie.

---

## Lo que os pido, por orden de importancia

### 1. El séptimo modo de fallo

La v1 nombraba cuatro y admitía un quinto desconocido; vosotros nombrasteis el que la mató. Esta v2
nombra seis (§7). **Nombrad el séptimo**, y con él **la medida barata que lo destaparía antes de
contratar al curador**. Es el patrón que ya salvó este diseño una vez.

Pistas de dónde mirar, por si ayudan: las relaciones metamórficas las escribo **yo**, del estándar;
el piloto lo corro **yo**; el curador ve el contrato, el estándar, el ejecutor y las relaciones, y
nada más; el agente está congelado desde la Fase 12 con un prompt **afinado durante un mes contra el
catálogo A**; y el puntuador sigue siendo mío.

### 2. ¿Es la emergencia de verdad emergencia, o es el contrato con otro nombre?

La §4.1 admite el problema —**para meter un fallo en B hay que saber que es un fallo, y cualquier
oráculo automático imprime su firma en B**— y responde declarando tres vías y publicando la
proporción de cada una. **¿Basta?** En particular:

- Las **relaciones metamórficas** (vía b) salen del estándar y del contrato, no de un catálogo de
  fallos. ¿Es esa distinción real, o es la misma inversión de función de la v1 con una capa más
  encima? Si un fallo solo entra en B cuando viola una invariante que yo escribí, ¿en qué se
  diferencia de un operador de mutación leído al revés?
- La **vía (a)** —caídas, cuelgues, conexiones reseteadas, recursos que nunca se escriben— no tiene
  oráculo y por tanto no tiene sesgo. Pero ¿tiene el problema contrario: recoger solo lo que ya es
  **ruidoso**, que es justo lo que no interesa, porque el fallo que importa es el silencioso?
- La **vía (c)**, humana sobre muestra, es la única insesgada que ve silencios. ¿Qué tamaño de
  muestra la hace informativa, y qué pasa si la tasa base es del 1 %?
- **¿Hay una cuarta vía que no se me ocurre?**

### 3. El endpoint, que ahora es «el residuo»

El primario es la nota del agente sobre **el subconjunto que el autor de la regla actualizada
declara, por escrito y bajo protocolo, no poder cubrir con una regla estática**. Eso pone el
endpoint en manos de **una declaración humana**, que es un tipo de mando que la Fase 12 no tuvo.

- ¿Qué impide que ese autor declare **de más** (le conviene: hace su derrota más digna) o **de
  menos** (le conviene: hace su script más potente)? ¿Qué protocolo lo acota sin filtrarle nada?
- ¿Cambia la respuesta si el autor es **un modelo** en vez de una persona?
- ¿Tiene su propia trampa, como el total la tuvo en la Fase 12 y el DiD en la v1?
- Si el residuo sale **vacío** —todo B resulta cubrible con reglas—, ¿es eso un resultado publicable
  o es otra vez un banco que no puede contestar?

### 4. El brazo del prompt afinado: ¿simetría o ventaja?

La §5 argumenta que el prompt afinado es el brazo justo porque lo que compró el mes de trabajo fue
**el contrato de la transformación**, y el autor de la regla actualizada también lo recibe. Los
números del paso 29, sobre 456 casos:

```
v3 completo, conoce el catalogo           +0.875
prompt afinado, modo techo                +0.787
v3-invariante, solo contrato publicado    +0.705
agente con herramientas                   +0.642
prompt generico, modo techo               +0.615
```

Y el desglose que motiva el argumento: fuera de la clase de fallo silencioso el prompt genérico
(1.174 caracteres) es **igual o mejor** que el afinado (17.136); dentro de ella el afinado pasa de
−0,229 a +0,500.

**¿Es simetría de verdad, o le estoy dando el contrato al modelo y no a las reglas?** Y al revés:
¿hay algo en esos 17.136 caracteres que no sea el contrato y que en B se convierta en ventaja
indebida —o en lastre?

### 5. El tamaño, que en un B emergente no se elige

N y k salen de lo que produzca la capa. **¿Cómo se preinscribe un análisis cuyo tamaño se
desconoce** sin dejar la puerta abierta a mirar primero y decidir después? La §8 fija «N mínimo para
que el primario se publique como primario» y manda apartar los tipos con una sola instancia, pero el
número lo deja 🧑. ¿Qué regla lo cierra de verdad?

### 6. Lo barato que falta o que sobra

Los pasos 1 a 6 de la §9 no encargan nada y cualquiera puede matar la fase. ¿Falta alguno? ¿Sobra
alguno? **¿Cuál tiene más probabilidad de matarla, y se puede adelantar al primer puesto?**

---

## Lo que NO os pido

- **No rediscutáis la Fase 12.** Está cerrada, medida y publicada con su resultado negativo.
- **No propongáis un B declarado.** Esa salida existía —la vuestra, la «reescritura mínima de una
  tarde»— y 🧑 eligió la otra sabiendo que es más cara. Si creéis que la emergencia es inviable,
  decid **por qué es inviable**, no «volved a la declarada».
- **No me deis un diseño nuevo entero.** Romped éste, y si proponéis, que sea el cambio mínimo que
  arregla lo que habéis roto.

## Control de contaminación

Lo que tenéis delante es este encargo y nada más. **No** habéis visto el catálogo A, las tablas de
casos, el agente, `triador_regex_v3.py`, el puntuador, el afinado ni el conjunto reservado. Si para
contestar necesitáis algo de eso, **pedidlo y decid para qué**, en vez de suponerlo: en la ronda
anterior la suposición de un revisor sobre qué lee el `v3` generó una alarma que costó una tarde
comprobar, y resultó falsa (0 de 456 veredictos cambiaban).

---
---

# Fase 13 — Diseño, v2 (22-sep-2026). **B por emergencia, no por declaración**

**Estado: BORRADOR. No se monta la capa de perturbación ni se encarga la curación hasta firmar 🧑
y hasta que este documento pase por el panel (§7, modo de fallo F6).**

Cambio respecto a la v1: 🧑 decidió el 22-sep que **B se obtiene ejecutando el sistema, no
escribiendo operadores** (§7.2 de la quinta revisión). No es un ajuste del diseño anterior: cambia
la pregunta que la fase puede contestar, elimina tres de sus cuatro modos de fallo y crea otros
que hay que nombrar aquí.

Convención: 📏 sale de una medida, 🔍 de una revisión externa, 🧑 lo decide Víctor.

---

## 1. Qué mató a la v1

La v1 encargaba N tipos nuevos a un autor ciego y estratificaba el resultado por un «oráculo de
mecanicidad». El panel la rompió por tres sitios y los tres son la misma rotura:

1. 🔍 **El oráculo es un brazo.** Agrupar los tipos por «¿se le puede inducir una regla?» y
   preguntar dónde gana el modelo es condicionar en el desenlace del comparador. «El modelo gana
   donde falla un escritor de reglas automático» ya se sabía desde la Fase 12.
2. 🔍 **Q2 está vacía con un B declarado.** Todo tipo definido por una función de mutación admite
   una regla estática: la función leída al revés y proyectada sobre la traza. La regla actualizada
   llega al 100 % de lo observable **por construcción**, igual que el v3 llegó en A. El DiD sale
   decidido antes de correr nada, y «detecciones propias contra la actualizada» vale 0 por
   construcción: el número que la v1 ponía en portada estaba muerto antes de nacer.
3. 🔍 **El DiD se fabrica.** La corrección de la §5.2 de la v1 —pedirle más tipos al autor hasta
   que baje el solapamiento— selecciona el banco contra el comparador.

Y la frase que ordena el resto: **cualquier tipo declarado es una función que se puede invertir.**
Da igual que lo escriba un autor ciego, un modelo o yo. **Un B declarado contesta coste, no
capacidad.**

📏 La Fase 12 ya lo había medido sin saberlo: 16 de 18 operadores a 8 de 8 para el script, y los
dos que falla son exactamente los dos que la matriz de observabilidad declaró no identificables el
día antes, sin correr ningún modelo.

---

## 2. Por qué la emergencia sí cambia algo

Los únicos fallos de este laboratorio que **no** eran invertibles el primer día son los diez que la
bitácora fue apuntando, y ninguno salió de escribir operadores: salieron de **ejecutar el sistema**.

| # | fallo | cómo apareció |
|---|---|---|
| 1 | el `MSA` con código `CE` del FailureTimeout, no conforme al modo de acuse declarado | mandando un mensaje con FHIR caído |
| 2 | el circuito no desescapa la entrada: la secuencia de escape llega literal a FHIR, con `AA` | validando el juego de datos |
| 3 | una credencial inexistente da 404, no 401 | rompiendo la credencial a propósito |
| 4 | el servicio MLLP se bloquea con `PoolSize=1`: 7 de 8 conexiones reseteadas | mandando ocho seguidos |
| 5 | el `AE` de transporte no llega nunca | apagando FHIR |
| 6 | 404/401 de FHIR se contestan `AR` con `ERR-3=102`: le dice al emisor que el error es suyo | derivando el catálogo |
| 7 | `MAXREP=10` descarta un `MR` en la repetición 11 y usa el de respaldo sin decir nada | dos operadores del catálogo |
| 8 | `PV1` antes de `PID` contesta 101 con el identificador presente; el correcto es 100 | leyendo el estándar |
| 9 | los acentos: dos bugs que se cancelaban, y arreglar uno empeoró lo visible | una prueba de punta a punta con un acento de verdad |
| 10 | `iris_production_item(set_settings)` acepta ajustes de Adaptador y no los aplica | el puerto cerrado contestaba `AA` |

**Ninguno tiene firma diseñada, porque nadie los diseñó.** Ese es el proceso que hay que
industrializar, y es la única razón por la que esta fase puede contestar algo que la anterior no.

**Consecuencia para el comparador, y es la que rescata la fase:** con un B emergente, la regla
actualizada **ya no vale ≈ 1 por construcción**. Puede haber fallos cuya evidencia discriminante no
esté en la traza, o que exijan estado entre mensajes, o que solo aparezcan bajo concurrencia.
Cuánto de B es así deja de ser un supuesto y pasa a ser **un dato medido**.

---

## 3. La pregunta

> **¿Detecta el modelo congelado, sin haberlo visto nunca y sin que nadie se lo describa, un fallo
> que el sistema produce y que nadie diseñó —con una tasa de falsas alarmas que no lo invalide?**

Es H4 de la Fase 12 sobre un conjunto que ningún autor escribió, y **va sola**: no lleva comparador
de reglas en el primario, porque la congelada no anticipa por definición y la actualizada ya ha
visto B. Las reglas van al lado, midiendo otra cosa (§6).

🔍 Lo que esta fase **no** va a contestar, escrito ahora para no venderlo después: no dice si el
modelo es rentable, ni si generaliza a otra integración, ni si un humano con tiempo ilimitado le
gana. Dice si hay un residuo que las reglas no alcanzan, y cómo de grande es.

---

## 4. Cómo se produce B

Cinco familias de perturbación sobre el circuito congelado (MLLP → ADT^A01 → FHIR Patient).
**El autor del laboratorio no controla qué sale.**

| familia | qué se perturba |
|---|---|
| **transporte** | marco MLLP partido, dos mensajes en un marco, terminador ausente, relleno; reset a mitad de mensaje, half-close, retardo entre bytes, tamaños extremos |
| **codificación** | UTF-8 mal formado, latin1, BOM, caracteres de ancho cero, NFC contra NFD, secuencias de escape HL7, MSH-18 declarado y contradicho |
| **gramática y perfil** | segmentos repetidos, faltantes o fuera de orden; más componentes de los definidos; delimitadores no estándar en MSH-2; MSH-12 de otra versión; eventos vecinos (A04, A08, A28) |
| **carga y entorno** | N conexiones contra el `PoolSize`; el mismo MSH-10 reenviado; llegada fuera de orden; FHIR lento, intermitente o con 5xx; credencial rotada a mitad; reinicio del contenedor en mitad de una transacción |
| **corpus real** | mensajes v2 reales con sus irregularidades naturales — ya están en local, en `estandares/hl7_catalogo/extraido/`, 326 ficheros de texto en la familia v2 |

Buena parte es fuzzing de estantería. Lo que no lo es —carga, entorno, reinicios— es justo donde
salieron 4 de los 10 fallos de la §2.

### 4.1 El oráculo, que es la parte cara y la que puede arruinarlo

Para que un fallo entre en B hay que **saber que es un fallo**, y **cualquier oráculo automático
imprime su firma en B**. Es el error de la Fase 12 con otro traje, así que se declaran tres vías
con su sesgo escrito al lado:

- **(a) Sin oráculo — gratis y sin sesgo.** Caídas, cuelgues, excepciones en el log, conexiones
  reseteadas, mensajes procesados fuera de orden, recursos que nunca se escriben, acuses que no
  llegan. No necesitan contrato.
- **(b) Metamórfico — el caballo de batalla.** Relaciones **de invariancia sacadas del estándar y
  del contrato**, no de un catálogo de fallos: un mensaje y su equivalente con escapes conformes
  tienen que producir el mismo `Patient`; reordenar repeticiones que el estándar declara no
  ordenadas no cambia el recurso; NFC y NFD dan el mismo nombre; un acuse `AA` obliga a que el
  recurso exista. **Se escriben del estándar y se sellan ANTES de correr nada.**
  📏 Su sesgo está acotado y medido: el brazo 2 del paso 29 mostró que unas reglas escritas solo con
  el contrato publicado sacan **+0,705**. La firma que (b) imprime es la del contrato — que es
  exactamente la que el autor de la regla actualizada también recibe, así que no favorece a ningún
  brazo.
- **(c) Humano sobre muestra — caro, insesgado, y es el que da la tasa base.** El curador adjudica a
  mano una muestra aleatoria de ejecuciones contra el contrato y el estándar. Acota lo que (a) y (b)
  se dejan fuera.

**La proporción de B que viene de cada vía se publica.** Si el 100 % viene de (b), el banco mide el
contrato y no la emergencia, y hay que decirlo con esas palabras.

### 4.2 La adjudicación

Un fallo que nadie diseñó no trae clase esperada puesta. Por eso:

- La clase esperada sale del **contrato publicado y del estándar en disco**, nunca del catálogo A.
  Es la regla que la Fase 11bis ya pagó: mirar antes de decidir cuesta tres minutos, suponer cuesta
  una tarde.
- **La regla de adjudicación y el `ideal_b` de B se escriben y se sellan antes de curar.**
- Un candidato entra en B solo si el curador puede **señalar la cláusula** que incumple. Si no, va
  al cajón de **disputados**, que se reporta y queda fuera del primario.
- **κ entre dos codificadores ciegos entre sí** sobre una muestra. Si el acuerdo es bajo, las
  etiquetas no son datos y no hay banco.

---

## 5. Los brazos

| brazo | qué es | por qué está |
|---|---|---|
| **agente congelado** | el de la Fase 12, prompt afinado con huella, sin reentrenar | **el primario** |
| **prompt genérico** | los 1.174 caracteres del paso 29, misma pregunta binaria byte a byte | mide cuánto del mes de prompt viaja a tipos que nadie escribió |
| **v3 congelado** | `triador_regex_v3.py`, sin tocar | **comprobación de novedad**, no se resta |
| **v3 actualizado** | el mismo, con reglas escritas viendo B por alguien que no ve el agente | el coste de ponerse al día, **y el residuo** (§6) |
| **inductor** | suelo automático, calibrado en A **antes** de ver B | descriptor y suelo. **Nunca estratifica el primario** |

📏 **Por qué el prompt afinado es el brazo justo y no una ventaja:** lo que el mes de trabajo compró
fue exactamente una cosa —el contrato de la transformación—, y el autor de la regla actualizada
también lo recibe. El paso 29 lo midió: fuera de la clase de fallo silencioso el genérico es igual o
mejor (+0,961 contra +0,938 en limpios, +0,727 contra +0,710 en fallo de mensaje), y dentro de ella
el afinado pasa de −0,229 a +0,500. Correr los dos cuesta una pasada más y contesta si esa compra
transfiere.

---

## 6. El endpoint, y el residuo

**Primario:** tasa de detección **por tipo curado** del agente congelado sobre B a exposición cero,
macro por tipo, **con veto**: más falsas alarmas que el v3 congelado sobre los limpios de B invalida
la ventaja aunque el número salga alto.

**Al lado, nunca agregados con el primario** (🔍 la regla anti-Fase-12 se mantiene tal cual: la resta
que salió «casi cero» sigue prohibida como endpoint):

1. **El residuo.** El autor de la regla actualizada entrega, además del script, **la lista de tipos
   que declara no poder cubrir con una regla estática, y por qué**, bajo protocolo escrito. Con un B
   emergente esto deja de ser un supuesto. **Es el número que contesta la pregunta de la fase**, y
   la nota del agente sobre ese subconjunto va en portada.
2. **Coste por tipo** del autor de la regla actualizada, registrado mientras trabaja.
3. **v3 congelado sobre B**, crudo y tipo a tipo, nunca en media: cuánto de B resultó ser firma
   vieja.
4. **Detecciones propias** del agente contra el v3 actualizado **fuera de muestra**: el autor ve 2
   de las k instancias de cada tipo y se puntúa sobre las otras.
   📏 En la Fase 12 fue 1 de 55 y ni siquiera era una detección. Es el número más honesto que hay.
5. **Prompt genérico contra afinado**, por clase y nunca agregado.
6. **Origen de cada tipo de B**: vía (a), (b) o (c), y familia de perturbación.

🔍 **Cada mando discrecional de este diseño tiene una dirección que favorece al modelo.** La
protección de la Fase 12 fue predecir el propio fracaso; ésta no tiene equivalente automático, así
que los mandos se clavan aquí y por escrito:

| mando | cómo queda clavado |
|---|---|
| qué entra en B | lo decide el curador, ciego al agente y al v3 |
| qué es «fallo silencioso» | las relaciones metamórficas, selladas antes de correr |
| `ideal_b` sobre B | escrito y con huella antes de curar |
| cuál es el primario | escrito en esta §6 |
| el prompt | congelado con la huella de la Fase 12 |
| «detección propia» | **la mitad o más de las instancias del tipo**, no una sola |

**El negativo, en números, firmado antes de que exista B** 🧑. Propuesta, para que 🧑 ponga el
número:

> «Si el agente congelado detecta menos del **25 %** de los tipos curados de B a exposición cero
> —con el criterio de la mitad o más de sus instancias—, o si sus falsas alarmas en los limpios de B
> superan las del v3 congelado, entonces el modelo tampoco aporta en fallos que nadie diseñó, y la
> Fase 13 cierra en negativo.»

---

## 7. Cómo fracasaría ESTA fase, y qué lo destapa barato

Las cuatro primeras corren **sin agente, sin curador y sin encargar nada**.

**F1 · El fuzzing solo produce fallos ruidosos.** Todo se cae fuerte o se rechaza con `AE`/`AR`, y B
se queda sin lo único que importa.
**Lo destapa:** una tanda piloto de unas 200 ejecuciones con las relaciones metamórficas puestas. Si
la tasa de silenciosos es menor del 2 %, el proceso no produce banco y hay que cambiar la capa antes
de contratar a nadie. 📏 Hay motivo para esperar que sí produzca: los diez de la §2 salieron en un
mes de uso normal, sin fuzzing.

**F2 · Todo B sale de la misma familia** (todo codificación, por ejemplo). Entonces el N efectivo es
1 o 2 y la macro por tipo miente.
**Lo destapa:** la distribución por familia en el piloto. Si una aporta más del 60 %, se declara y
se reporta como techo del dominio, no se disimula.

**F3 · El oráculo metamórfico imprime su firma en B.** El fallo de la Fase 12 con otro traje.
**Lo destapa:** la proporción de B por vía (§4.1). Las relaciones se sellan antes; la vía (a) no
tiene oráculo, y su cuota es la prueba de que B no es solo el contrato leído al revés.

**F4 · Contaminación por los diez conocidos.** Yo los conozco, y el agente se afinó en un
laboratorio donde ya existen.
**Lo destapa:** los diez están enumerados en la §2 y se sellan con huella. Todo tipo curado que
coincida con uno de ellos va a un **estrato aparte, declarado y fuera del primario**.

**F5 · El curador no es ciego de verdad.** Si ve A, el agente o el v3, adjudica hacia ellos.
**Lo destapa:** el paquete de contexto del curador se escribe y se sella: contrato, estándar,
ejecutor y relaciones metamórficas. Ni el catálogo A, ni el agente, ni el v3, ni el puntuador. Su
identidad —y su familia, si es un modelo— queda registrada.

**F6 · 🧑 El que yo no sé ver.** La Fase 12 enseñó que existe y la v1 de este documento lo confirmó:
el panel la rompió por donde yo no miraba. **Este diseño va al panel antes de montar la capa de
perturbación.**

---

## 8. El tamaño, que en un B emergente no se elige

📏 La v1 dimensionaba N = 30 tipos y k = 5 con la varianza medida de la Fase 12 (intra-tipo
**0,0000** para la regla, **0,057** para el agente; entre tipos 0,43 y 0,31). Eso **decae**: en un B
emergente ni N ni k se eligen — salen de cuántos fallos distintos produce la capa y de cuántas veces
reaparece cada uno.

Lo que sí se fija de antemano:

- **N mínimo para que el primario se publique como primario**, y por debajo de él la fase se reporta
  como descriptiva. 🧑
- **k por tipo**: se toma lo que salga, se publica la distribución, y los tipos con una sola
  instancia van aparte, porque una detección sobre una instancia no distingue capacidad de azar.
- 🔍 **Si la capa no produce N tipos genuinamente distintos, eso es en sí un resultado** —sobre el
  proceso, no sobre el dominio— y se dice con esas palabras en vez de rebajar N en silencio.

---

## 9. El orden

```
  1. relaciones metamorficas, escritas del estandar y selladas   sin agente, sin curador
  2. capa de perturbacion + TANDA PILOTO (~200 ejecuciones)      <- puede decir "esto no produce banco"
  3. distribucion por familia y por via (a)/(b)/(c)              <- puede decir "N efectivo = 2"
  4. inductor calibrado en A (descriptor y suelo)
  5. regla de adjudicacion e ideal_b, con huella; kappa entre dos codificadores
  6. el negativo, en numeros, firmado
  ------------------------------------------------------------- hasta aqui, nada encargado
  7. curacion a ciegas
  8. congelar, preinscribir, sellar
  9. UNA pasada
```

**Nunca más un mes de trabajo antes de saber si el banco puede contestar la pregunta.**

---

## 10. Lo que se hereda y lo que decae

**Se hereda** —un mes de trabajo que no se repite—: el circuito congelado con su huella y sus 27
pruebas, el arnés (`Datos`, `HerrA/B/C`), las tres clases del agente, el puntuador con sus 16
autopruebas, `comparar.py`, la maquinaria de sellado, la matriz de observabilidad, el banco de
adversarios y los tres triadores (`v3`, `v3-invariante`, congelado).

**Decae de la v1**, y se documenta como sustituido por inalcanzable, no por incómodo:

- el oráculo de mecanicidad **como estratificador** (sobrevive como descriptor y suelo);
- el **DiD** como primario, y con él los cuartiles;
- **Q1 / Q2** como par: con B emergente, Q1 pasa a ser el coste registrado y Q2 pasa a ser el
  residuo declarado;
- **N = 30, k = 5** como dimensionado.

---

## 11. Abierto 🧑

1. **El número del negativo** (propuesta: 25 % de los tipos curados, con la mitad o más de sus
   instancias cada uno).
2. **N mínimo** para que el primario se publique como primario.
3. **Quién cura**, persona o modelo, y con qué familia registrada.
4. **Quién corre el piloto.** Propuesta: el piloto lo corro yo —es solo tasa base y distribución—,
   la curación no.
5. **Presupuesto de ejecuciones** de la capa de perturbación.
6. Si el **estrato de los diez conocidos** se corre igualmente como descriptivo.
7. **Rotar las dos claves de API** antes de cualquier ronda de panel: siguen quemadas desde el
   20-sep.
