# ¿Puede un modelo local de 30B triar fallos de integración HL7?

**Informe del laboratorio — septiembre de 2026**

---

## Resumen

Se montó un circuito de integración sanitaria real —mensajes HL7 v2 por MLLP, transformación,
escritura de recursos FHIR y acuse al emisor—, se le construyó un banco de fallos, y se midió si un
agente de IA local triaba esos fallos mejor que una lectura mecánica de la misma evidencia.

**El resultado va en dos frases que no se separan. El agente funciona: detecta 10 de 18 operadores
de fallo silencioso sin una sola falsa alarma en 22 casos limpios, sobre un conjunto reservado con
las hipótesis selladas antes de abrirlo. Y aun así no hace falta: un script de expresiones regulares
sin modelo lo bate +0,873 contra +0,629, y al agente no le queda ni una detección propia.**

Quedarse con la primera frase sería propaganda; con la segunda, derrotismo.

**Pero el hallazgo que se lleva el trabajo no es del modelo, es del método:** un banco construido con
**operadores de mutación declarativos** no puede contestar si el modelo aporta, porque por
construcción cada operador deja una firma mecánica y un detector escrito contra esas firmas llega al
100 % de lo observable. El defecto era de construcción y fue invisible hasta el último día.

Y dos cosas más, que son las que transfieren fuera de este laboratorio:

1. **Lo que el modelo aporta se concentra en una sola clase de fallo** —la que exige cruzar el
   mensaje de entrada con el resultado producido— y **necesita el contrato de la transformación
   delante** para aportarlo. Fuera de ahí, un prompt genérico de mil caracteres rinde igual que uno
   afinado durante un mes, y unas reglas escritas con ese mismo contrato rinden más.
2. **Los oráculos de conformidad de estantería no pueden ver un fallo silencioso.** Comprueban que
   el mensaje esté bien formado y que sus códigos existan; un fallo silencioso es **un valor válido
   en la situación equivocada**. Son preguntas distintas.

---

## 1. Qué se montó

Un circuito completo y realista, congelado con huella antes de medir nada:

- un **servicio MLLP** que recibe mensajes `ADT^A01`;
- una **transformación** a un mensaje canónico interno;
- una **operación** que escribe recursos `Patient` en un servidor FHIR R4;
- un **acuse de aplicación** al emisor: `AA` si se creó, `AE` si hay que reintentar, `AR` si no.

Revisado por un modelo externo con sus 16 hallazgos corregidos, contrastado contra las tablas
normativas de HL7, y con **27 pruebas unitarias**. El circuito no se tocó durante ninguna medición:
su huella se comprobó al principio y al final.

El **agente** es un modelo local de 30B servido por Ollama, corriendo **dentro** del motor de
integración y con tres herramientas de solo lectura acotadas por traza: el mensaje tal como llegó
por el cable, el recorrido del mensaje con el canónico y el acuse, y el Event Log de esa sesión.

---

## 2. La pregunta, y cómo se blindó antes de contestarla

> *Un agente local de 30B, con mensaje, traza y log por herramientas, tría fallos de integración
> HL7 —incluidos los silenciosos— mejor que cualquier lectura mecánica de la misma evidencia, usa la
> evidencia y no la memoria, y sabe cuándo no puede saberlo.*

El **fallo silencioso** es el que importa: el circuito contesta «todo bien», escribe algo, y lo
escrito está mal. No está en el mensaje ni en el log: está en la **discrepancia** entre los dos.

Lo que se hizo para que la pregunta pudiera salir que no:

- **327 casos** generados con 63 operadores de mutación sobre mensajes base, cada uno verificado
  contra su firma;
- un **puntuador con 16 autopruebas**, rehecho entero después de que dos revisiones externas lo
  rompieran;
- un **banco de 20 adversarios sin cerebro** como suelo, porque el criterio exige batir *cualquier*
  lectura mecánica y no solo la primera que se te ocurra;
- **tres conjuntos disjuntos** —principal, desarrollo y reservado— con sales distintas, comprobados
  disjuntos en identificador y contenido;
- y una **preinscripción sellada con huella** antes de abrir el reservado, con sus cinco hipótesis y
  sus umbrales. Se reescribió tres veces porque dos rondas de panel externo la rompieron, y **la
  versión final predice el propio fracaso del autor**.

El conjunto reservado se corrió **una vez**.

---

## 3. El resultado

Una pasada, 55 casos, las cinco hipótesis preinscritas:

| | |
|---|---|
| **H1 · primaria** | agente **+0,629** · script sin modelo **+0,873**. Pierde por 0,244, dentro del intervalo predicho |
| **H2** | un solo caso propio del agente, y **no era una detección** |
| **H3 · arriesgada** | los dos operadores declarados no identificables siguen a **cero**, por ambos |
| **H4** | **10 de 18** operadores de fallo silencioso (pedía ≥9) y **22 de 22** limpios (pedía ≥20) |
| **H5** | 55 de 55 con una llamada a cada herramienta · canario 0 |

**Las cinco. Todas.**

**H3 es la que más dice del aparato.** Era la apuesta arriesgada —bastaba *una* detección para
tumbarla— y se sostiene. Un análisis mecánico previo había predicho **en frío, sin correr ningún
modelo**, exactamente qué dos operadores serían invisibles para cualquiera. Siguen invisibles para
el agente y para el script, en datos que nadie había visto.

---

## 4. Por qué perdió: no fue el modelo, fue el banco

Un corpus generado aplicando **operadores de mutación declarativos** tiene una propiedad que no se
ve hasta que alguien la busca: **por construcción, cada operador deja una firma mecánica** —para eso
es un catálogo—. Un detector escrito contra esas firmas llega al **100 % de lo observable**: 16 de
18 operadores a 8 de 8.

Y los dos que falla son **exactamente** los dos que el análisis de observabilidad había declarado no
identificables el día anterior.

Lo decidió la forma de construir el banco un mes antes, y **no se vio hasta que alguien escribió el
adversario mecánico fuerte** — que lo pidió una revisión externa, no el autor. El adversario ya
estaba escrito sin saberlo: era la propia rutina de análisis.

**De ahí sale la primera regla reutilizable: construir el adversario mecánico fuerte ANTES de
construir el agente.** Si el script llega al techo de lo observable, el banco no puede contestar la
pregunta, y eso se sabe en una tarde en vez de en un mes.

Subir la barra solo puede equivocarse en una dirección: un adversario demasiado fuerte causa un
falso negativo —concluir que el modelo no aporta cuando quizá aporta— pero nunca un falso positivo.
Por eso es legítimo escribir sus reglas mirando los datos; afinar el prompt del agente con lo mismo
sería trampa.

---

## 5. Lo que el modelo sí aporta, y es lo que transfiere

Sobre 456 casos, cinco brazos:

```
reglas que conocen el catalogo entero          +0,875
prompt afinado un mes, con la evidencia servida +0,787
reglas escritas SOLO con el contrato publicado  +0,705
el agente real, que llama a herramientas        +0,642
prompt generico de 1.174 caracteres             +0,615
```

Leída de arriba abajo: **un mes de prompt afinado, en las condiciones más favorables posibles,
apenas supera a unas reglas escritas con el contrato publicado delante.** Y el agente real, el que
tiene que acertar las llamadas, queda por debajo de esas reglas.

Tres comprobaciones baratas, hechas en una tarde y sin gastar un solo caso reservado, contestan qué
significa esa escalera:

**¿Estaban los dos brazos leyendo la misma evidencia?** Una revisión avisó de que el script leía
columnas derivadas y el agente texto crudo, y que si eso importaba la comparación estaría sesgada a
favor del script. Se reconstruyó el informe entero **solo desde lo que ve el agente**: **0 de 456
veredictos cambian**, misma nota. La comparación era justa.

**¿Ganó el script por conocer la clave del banco?** Se partieron sus reglas en dos: las que salen
del **contrato publicado** y las que solo se te ocurren **viendo el catálogo**. Las de solo contrato
sacan +0,705 y **siguen batiendo al agente**. La victoria no venía de conocer la respuesta.

**¿Cuánto valía el mes de prompt?** Se escribió el prompt que escribiría cualquiera —la tarea, los
veredictos, el contrato de salida, y nada más: 1.174 caracteres contra 17.136— y se corrió en las
mismas condiciones:

| clase | genérico | afinado |
|---|---|---|
| rechazo por política | +1,000 | +1,000 |
| sin problema | **+0,961** | +0,938 |
| fallo del mensaje | **+0,727** | +0,710 |
| **fallo silencioso** | **−0,229** | **+0,500** |
| operadores silenciosos detectados | 4 de 18 | 15 de 18 |

**En todo salvo una clase, el prompt de mil caracteres es igual o mejor.** El mes de trabajo compró
exactamente una cosa: **detectar fallos silenciosos**. Y tiene sentido, porque lo que hace falta
para ver infidelidad es **el contrato de la transformación**, que es justo lo que el genérico no
lleva.

> **Lo transferible, dicho entero:** lo que el modelo aporta se concentra en una sola clase —la que
> exige cruzar el mensaje con el resultado— y hace falta darle el contrato de la transformación para
> que lo aporte. Fuera de ahí un prompt genérico rinde igual, y unas reglas escritas con ese mismo
> contrato rinden más.

---

## 6. Al intentar arreglarlo aparecieron dos cosas más

La conclusión de la §4 pedía un banco distinto: fallos **sin firma mecánica**, que emergieran de
*ejecutar* el sistema en vez de escribirse como operadores. Al diseñarlo aparecieron dos resultados
que valen por sí solos.

### 6.1 La clase que haría falta puede estar vacía, y se midió

Respecto al paquete de evidencia que recibe un brazo, todo fallo cae en una de estas clases:
**cubierto por reglas derivadas del contrato**; **cubierto solo por reglas escritas tras ver el
catálogo**; **detectado por el modelo y por ninguna regla**; o **no observable por nadie**. Solo la
tercera justificaría seguir.

Medida sobre los 456 casos, clase de fallo silencioso:

```
cubierto por reglas del contrato ................  8 operadores
cubierto solo con el catalogo delante ...........  8
DETECTADO POR EL MODELO Y POR NINGUNA REGLA .....  0
no lo detecta nadie .............................  2
```

**Cero de 18.** Y de paso: el agente **falla por completo tres operadores que las reglas cubren a 8
de 8**, dos de ellos con solo el contrato. No es que no haya ventaja; hay déficit.

**Lo que ese cero significa, y no más.** No es probabilidad cero: la cota superior al 95 % es del
**15,3 %**, y eso suponiendo independencia entre operadores, que es falsa. Y el instrumento con que
se midió —un script escrito por el propio autor usando solo el contrato— mezcla *expresabilidad* con
*que se te ocurra*, y conocer el catálogo **sesga hacia el cero que salió**. Es un *prior*, no una
respuesta, y se publica con la dirección de su sesgo escrita al lado.

### 6.2 Los oráculos de estantería no ven el fallo silencioso

Para construir un banco emergente hace falta un **oráculo**: algo que diga que un resultado está
mal. Y todo oráculo imprime su firma en lo que recoge. La salida obvia era usar herramientas de
terceros, cuya firma no fuera la del autor. Se probaron las dos disponibles, **con la predicción
escrita y sellada antes de instalarlas**:

**El validador oficial de FHIR**, sobre los recursos realmente escritos por el circuito. El circuito
había escrito, entre otras cosas, un apellido con **una secuencia de escape HL7 literal dentro** y
otro con un **carácter de sustitución** donde iba una letra acentuada. Resultado: **0 de 3 fallos
vistos**, y exactamente **la misma única advertencia en los dieciséis recursos**, defectuosos y
correctos por igual. Contra el perfil base, una secuencia de escape literal es una cadena
perfectamente válida.

**Un comprobador de conformidad HL7 v2**, sobre los acuses. Aquí los fallos eran de código: el
circuito contesta un error de **entorno** diciéndole al emisor que el error es *suyo*, y contesta un
segmento fuera de sitio con el código de *campo obligatorio ausente*. El control decisivo fue
construir la **variante corregida** de cada acuse y validar las dos: **6 de 6 idénticas**. El
comprobador dice exactamente lo mismo con el código bueno que con el malo.

> **El principio, y transfiere a cualquier integración:** un oráculo de conformidad comprueba que el
> mensaje esté bien formado y que sus códigos **existan**. Un fallo silencioso es **un valor válido
> en la situación equivocada**. Ninguna herramienta de conformidad contesta la segunda pregunta — y
> por tanto, si quieres un oráculo que vea el silencio, tienes que escribirlo contra el contrato, y
> entonces lleva tu firma, que es justo lo que querías evitar.

---

## 7. Lo que este trabajo **no** puede afirmar

Escrito aquí para no tener que discutirlo después:

- **No prueba que un modelo mayor no aportara.** Un modelo, una temperatura, un circuito.
- **No prueba que la clase útil esté vacía.** El cero es un prior con cota del 15,3 %, sesgado hacia
  sí mismo, y medido sobre el terreno más favorable posible a las reglas.
- **No dice nada sobre fallos emergentes**, que es exactamente lo que no se llegó a construir.
- **No generaliza a otro circuito, otro estándar u otra implementación.** Un solo mapeo
  `ADT^A01`→`Patient`.
- **No mide coste operativo** ni tiempo de detección en producción, que son preguntas reales y
  distintas.
- **Los 55 casos del reservado son pocos**, sin un solo caso de fallo de entorno, y sobre corpus
  sintético con datos clínicos inventados.

**La conclusión general defendible es la metodológica**, no la del modelo.

---

## 8. El método, que es lo más reutilizable

Las reglas que salieron de equivocarse, cada una con el error que la produjo:

1. **Construir el adversario mecánico fuerte antes que el agente.** Si llega al techo de lo
   observable, el banco no puede contestar la pregunta.
2. **Una comprobación tiene que poder decir que no, y eso se prueba rompiendo el sistema a
   propósito.** Aquí una herramienta anunciaba «producción actualizada» llamando a una función que
   no existía, porque el error venía dentro de una respuesta correcta.
3. **Un control de discriminación compara correcto contra incorrecto en la misma estructura**, no
   defectuoso contra limpio. Comparar acuses con error contra acuses sin error dio una diferencia
   que no era detección: los limpios no llevaban el segmento que la disparaba.
4. **Predecir el propio fracaso, por escrito y sellado, antes de medir.** Es la única protección
   real contra reinterpretar un resultado incómodo, y aquí funcionó tres veces.
5. **Todo parámetro del que dependa la medición viaja escrito con la medición.** Dos filas de la
   misma tabla no eran comparables porque el plazo de espera no estaba en ninguna columna.
6. **Un verde puede ser falso, y es peor que un rojo.** Un marco de pruebas anuncia «todo correcto»
   cuando ejecuta cero pruebas; un ajuste con un valor inválido se ignora sin protestar; un segmento
   direccionado mal devuelve cadena vacía en vez de error. Los tres fallan **hacia el silencio**.
7. **Dos bugs que se cancelan dan un resultado correcto, y arreglar uno solo lo empeora.** Cuando un
   arreglo correcto empeora lo que se ve, no deshacerlo: buscar el segundo fallo.
8. **Mirar el estándar antes de decidir cuesta tres minutos; suponer cuesta un diagnóstico
   equivocado y una tarde.** Pasó en las dos direcciones: eligiendo un código de error de memoria, y
   a punto de anotar como defecto del circuito algo que el estándar declara correcto.
9. **Reportar las dos frases juntas.** «Funciona» y «no hace falta» son el resultado; quedarse con
   una es propaganda o derrotismo.

---

## 9. Qué haría falta para contestar la pregunta de verdad

Un corpus de fallos **sin firma mecánica**: que emerjan de ejecutar el sistema —perturbación del
transporte, de la codificación, de la gramática, carga, entorno, mensajes reales con sus
irregularidades naturales— y que los etiquete alguien externo que no haya visto ni el catálogo ni el
agente. Con preinscripción, conjunto reservado, y reglas escritas por autores independientes bajo un
presupuesto declarado.

**Está diseñado y no está pagado.** El diseño pasó por cuatro rondas de panel externo y sobrevive en
su cuarta versión, partido en dos etapas: una barata que solo puede decir «sigue» o «para de
gastar», y la cara, que es la única que podría concluir.

Y hay una razón honesta para no haberlo hecho todavía: el prior está medido en cero, la única clase
que justificaría la fase puede no existir, y la herramienta independiente que se necesitaba para
construir el banco **resultó ser ciega**. Cuando se sabe eso antes de pagar, no pagar es el
resultado, no la rendición.

---

*Todos los datos clínicos utilizados son sintéticos. Ni un dato de ningún paciente real.*
