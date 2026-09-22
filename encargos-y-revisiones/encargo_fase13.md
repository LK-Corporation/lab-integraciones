# Encargo: diseñar la Fase 13, sabiendo exactamente por qué fracasó la Fase 12

Eres consultor de metodología experimental. Se te pide **diseñar una fase nueva**, y sobre todo
decir **qué la haría incapaz de contestar su propia pregunta** — porque eso es justo lo que le pasó
a la anterior y no se vio hasta gastar un mes.

**Contaminación.** No pidas el catálogo de mutaciones, la clave ni las mediciones caso a caso. Si
crees que necesitas alguno, dilo en vez de suponerlo.

---

## 1. El laboratorio, en cuatro líneas

Un circuito **ADT^A01 por MLLP → FHIR Patient** en InterSystems IRIS for Health, congelado y
verificado. Un agente de triaje (`qwen3-coder:30b` local) que, dado el identificador de una traza,
lee tres herramientas —el HL7 crudo, el recorrido con el canónico y el acuse, y el log— y emite un
veredicto en JSON de esquema cerrado. Un puntuador firmado con 16 autopruebas. Un banco de
adversarios que el agente tiene que batir.

## 2. Lo que midió la Fase 12, y por qué fracasó

**El resultado, en dos frases que van juntas.** El agente **funciona** —detecta 10 de 18 operadores
de fallo silencioso sin una sola falsa alarma en 22 casos limpios, sobre un conjunto reservado que
nadie había visto— **y aun así no hace falta**: un script de expresiones regulares sin modelo lo
bate **+0,873 contra +0,629** y no le queda ni una detección propia (1 caso de 55, y ni siquiera
era una detección).

Cinco hipótesis preinscritas y selladas antes de abrir el reservado. **Las cinco se cumplieron.**

**Por qué, y es el hallazgo:** el corpus se construye aplicando **operadores de mutación
declarativos** —63 tipos de fallo catalogados, cada uno con su regla de generación—. Por
construcción cada operador deja una **firma mecánica**: para eso es un catálogo. Un detector
escrito contra esas firmas llega al **100 % de lo observable** (16 de 18 operadores a 8 de 8).

Dicho con más precisión: **el script no ganó porque sus reglas sean mejores que el modelo. Ganó
porque el conjunto de operadores está cerrado y el autor lo conoce entero.** 63 operadores, 63
reglas.

**Un banco de mutaciones declarativas no puede contestar si el modelo aporta.** Lo decidió la
forma de construirlo, y no se vio hasta que alguien escribió el adversario fuerte — que lo pidió
una revisión externa, el último día.

## 3. La pregunta que propongo para la Fase 13

> **¿Generaliza el modelo a tipos de fallo para los que nadie ha escrito una regla?**

Es la diferencia operativa de verdad entre un sistema de reglas —que hay que actualizar cada vez
que aparece algo nuevo— y uno que no.

## 4. El diseño que propongo, para que lo rompas

**Conjunto A** — los 63 operadores actuales. Adversario y agente se desarrollan contra él.

**Conjunto B, ciego** — N tipos de fallo **nuevos**, encargados a un autor que ve el circuito y el
contrato de la transformación pero **no** ve el adversario, ni el catálogo de A, ni el agente.
Entrega, por tipo: una entrada de catálogo y una función de mutación en Python.

**Los dos corren sobre B, con el adversario congelado contra A.**

Tres salidas, y ninguna es mala:

- el adversario se hunde y el modelo aguanta → **ahí está el valor del modelo, medido**;
- los dos se hunden → el modelo tampoco generalizaba, reconocía las mismas firmas;
- el adversario aguanta → **las reglas mecánicas generalizan**, y eso también es publicable.

**El orden, que es la lección de la Fase 12:** el adversario fuerte va **primero**. Ya existe.

**Estrato secundario propuesto:** los **fallos reales** que la bitácora apuntó al construir el
laboratorio —un acuse `CE` no conforme al modo declarado, entrada sin desescapar, una credencial
inexistente devolviendo 404 en vez de 401, el servicio bloqueándose con `PoolSize=1`—. No tienen
firma diseñada porque **nadie los diseñó**. Serán ocho o diez, y **el autor del laboratorio ya los
conoce**, que es exactamente la contaminación que se intenta evitar.

---

## 5. Lo que te pido

### 5.1 La pregunta

¿Es «generalizar a tipos no vistos» la pregunta correcta, o hay una mejor que el montaje ya
permite? Critícala. Si crees que sigue sin ser contestable con este laboratorio, dilo ahora.

### 5.2 **Qué haría que la Fase 13 tampoco pueda contestar su pregunta**

**Esta es la más importante.** La Fase 12 tenía un defecto fatal de construcción invisible hasta el
último día. Dime cuáles son los de este diseño, y **qué medida barata los destaparía al principio
en vez de al final**.

Al menos una que ya veo y quiero que valores: **el autor ciego puede escribir tipos que resulten
igual de mecánicamente obvios**, y entonces el adversario vuelve a ganar y no se aprende nada
nuevo. Pero pedirle «que no sean mecánicos» le filtra la respuesta. ¿Cómo se resuelve eso sin
contaminar el encargo?

### 5.3 El adversario congelado

Congelarlo contra A es el núcleo del diseño, pero un integrador de verdad **también actualizaría
sus reglas** al ver un fallo nuevo. ¿Es honesto congelarlo? ¿Habría que medir las dos cosas —el
adversario congelado y uno actualizado contra B— y qué significaría cada una?

### 5.4 El endpoint, sin la trampa de la agregación

En la Fase 12 el total escondió el hallazgo: un brazo ganaba en limpios justo lo que perdía en
silenciosos, y la resta salía casi cero. ¿Cuál debe ser el endpoint primario aquí, en qué unidad, y
qué desglose es obligatorio publicar junto a él?

### 5.5 Tamaño y potencia

¿Cuántos tipos nuevos, cuántos casos por tipo, y qué potencia hace falta para distinguir «el
adversario se hunde» de ruido? En la Fase 12 la unidad firmada era la media macro **por operador**,
y el conjunto reservado tenía un caso por operador.

### 5.6 El estrato de fallos reales

¿Merece la pena con la contaminación admitida, o es mejor dejarlo fuera? Si merece la pena, ¿cómo
se reporta para que esa contaminación no se cuele en la conclusión?

---

## Formato

Markdown, concreto, y contradíceme donde haga falta. Ordena por: (1) la pregunta; (2) **cómo
fracasaría esta fase y qué medida barata lo destaparía antes**; (3) el adversario congelado;
(4) endpoint y desglose obligatorio; (5) tamaño y potencia; (6) el estrato de fallos reales;
(7) lo que medirías en la primera semana para no construir sobre arena.
