# Un juez determinista para conversiones HL7 v2 → FHIR, y lo que encontró en dos conversores de código abierto

*Laboratorio de integraciones, octubre de 2026.*

Un mensaje HL7 v2 con una proteína C reactiva de **.5 mg/L** entra en el conversor de código abierto de Microsoft, y sale un recurso
FHIR con **5 mg/L**. No hay ningún error en el registro y el Bundle está bien formado. El dato está mal, y nada avisa.

Este artículo cuenta cómo se buscan fallos así **sin fiarse del conversor**. La herramienta es un juez determinista que lee el
estándar y cita cada cosa que afirma. Se le pasaron dos conversores de código abierto, Microsoft FHIR-Converter y LinuxForHealth
hl7v2-fhir-converter, y 368 mensajes públicos. Encontró **15 discrepancias nuevas con la guía oficial de HL7**. Las 15 tienen su
cita, cambian el significado del dato, no estaban declaradas por los proyectos y se reproducen con un mensaje mínimo.

Además, el juez vio **31 que los proyectos ya conocían**. Y **16 diferencias** resultaron ser formas que la guía admite, o sobre
las que no decide.

**Qué hay en este repositorio:**
- el código del juez y sus pruebas;
- el generador de los mensajes mínimos;
- los documentos de cada paso: [`verificador/RESULTADO-CONVERSORES.md`](verificador/RESULTADO-CONVERSORES.md).

Los conversores, las muestras de los proyectos y el detalle por caso no están aquí. [`verificador/README.md`](verificador/README.md)
dice qué falta y dónde encontrarlo.

---

## El problema: un conversor se prueba con sus propias respuestas

Convertir HL7 v2 a FHIR es el pan de cada día de la integración sanitaria. Hay guía oficial, la **HL7 v2-to-FHIR**: hojas que
dicen de qué campo sale cada elemento, y mapas de vocabulario entre las tablas de v2 y los códigos de FHIR. Hay conversores de
código abierto que la siguen, en mayor o menor medida.

Una forma habitual de probar un conversor tiene un problema de base: se compara su salida con **una salida esperada que escribió
el propio proyecto**. Muchas veces, ese esperado es una foto de lo que el conversor ya hacía. Aquí se comprobó con las 62
salidas esperadas que publica Microsoft: juzgadas con el mismo juez, dan exactamente los mismos hallazgos que su conversión
real. Las pruebas de LinuxForHealth son de otro tipo, con aserciones campo a campo, y varias de ellas afirman comportamientos
distintos de los de la guía.

Una prueba así confirma que el conversor no ha cambiado. No dice si estaba bien. Si el conversor siempre convirtió «.5» en 5, su
salida esperada también lo dirá.

Hace falta un juez que no salga del conversor:
- que lea lo que manda la guía;
- que mire lo que salió;
- que diga dónde no coinciden, y por qué, con cita.

## El juez

El verificador de este laboratorio nació para juzgar circuitos propios: un motor de integración que recibe HL7 v2 por MLLP,
contesta con un acuse y escribe FHIR. Es un programa en Python, sin dependencias y **sin ningún modelo de lenguaje**: a la misma
evidencia, el mismo veredicto.

Para juzgar conversores ajenos se le añadió un **perfil «guía»**, que toma lo esperado de dos fuentes:
- **los mapas de la guía v2-to-FHIR**, generados del paquete que publica HL7;
- **sus hojas**, citadas por fichero y fila.

Cada discrepancia que cuenta cae en una de **ocho clases que cambian el significado del dato**:

| Clase | Ejemplo |
|---|---|
| valor distinto | un número que no es el del mensaje |
| dato perdido | un campo valorado que no llega |
| dato inventado | algo que el mensaje no dice |
| código mal mapeado | un código traducido a otro concepto |
| valor imposible convertido | un código fuera de su tabla, convertido como si valiera |
| recurso ausente, duplicado o inventado | un resultado que desaparece o se repite |
| referencia rota | un sujeto que no existe |
| FHIR inválido | un código fuera de un valor obligatorio de FHIR |

**Lo demás es forma y no cuenta:** el orden, los identificadores, los `display`, cómo se escribe una referencia.

Cuando la guía admite dos lecturas, o no decide (un código sin destino en su mapa, por ejemplo), el juez lo declara como
convención y no lo cuenta.

## El método: escribirlo todo antes de mirar

Un juez que busca fallos ajenos tiene un riesgo evidente: encontrar lo que quiere encontrar. Por eso el estudio se hizo con las
mismas reglas que el resto del laboratorio.

1. **La pregunta, la regla de éxito y la de fracaso, escritas antes de empezar**
   ([`verificador/ANTES-ETAPA-CONVERSORES.md`](verificador/ANTES-ETAPA-CONVERSORES.md)).
   - Si no salía al menos una discrepancia nueva y confirmada, el verificador se declaraba pieza de portfolio y se dejaba de
     invertir en él.
   - «Confirmada» tenía cuatro condiciones fijadas de antemano: tener cita, cambiar el significado, que el proyecto no la tenga
     declarada y que se reproduzca con un mensaje público.
2. **El diseño, a ciegas.** El perfil «guía» lo diseñó un modelo de lenguaje distinto del que lo programó. Nunca vio lo que
   devuelven los conversores.
   - Las decisiones donde ni el estándar ni la guía deciden las tomó un modelo de decisión que da una probabilidad en cada
     respuesta. Las tomó sobre un estado escrito sin recomendación.
   - Hubo doce en el diseño, como qué hacer con un sexo vacío o si el orden de una lista importa, y cuatro más durante el
     contraste.
3. **La previsión sellada antes de correr nada**, con la huella del juez ([`verificador/cv/PREVISION-CV2.md`](verificador/cv/PREVISION-CV2.md)).
   Decía qué proporción de casos saldría bien en cada conversor y qué mecanismos de fallo se esperaban. Todo lo que quedara
   fuera de ella había que explicarlo.
4. **Los conversores, aislados.** Cada uno corre en una caja: Docker sin red, sistema de ficheros de solo lectura, usuario sin
   privilegios y versión fijada con su huella.
5. **El contraste con lo que el proyecto ya sabe.** Antes de llamar «nueva» a una discrepancia, se buscó en todo lo que el
   proyecto publica:
   - sus salidas esperadas;
   - sus pruebas y su documentación;
   - los comentarios de sus plantillas;
   - sus issues y los comentarios de esos issues.
6. **Un par de mensajes mínimos por cada nueva.** El caso trae solo el disparador; el control es el mismo mensaje sin él. Cuenta
   solo si el fallo sale en el caso y no en el control.
7. **Una revisión adversaria.** Dos agentes de modelo de lenguaje, uno por conversor, recibieron las candidatas de su conversor
   con un encargo: romperlas. Trabajaron en sesiones aparte y sin la conclusión de quien las había clasificado. **De las 25
   candidatas tumbaron 10.**
8. **La rama principal.** Las 15 que quedaron se volvieron a probar en la rama principal de cada proyecto, construida desde su
   código. Siguen 14.

## Lo que encontró

Cada discrepancia, con su cita a la hoja o al mapa de la guía, su par mínimo y lo que le dejó la revisión, está en
[`verificador/cv/RESULTADO-CV3.md`](verificador/cv/RESULTADO-CV3.md).

Los mensajes de abajo están abreviados. Los fragmentos de salida son de los Bundles que devolvió cada conversor; los Bundles
completos no se publican. Lo que registró el juez está en `verificador/cv/RESULTADO-CV3-minimos.json`.

### Las siete que más pesan

**Un valor que se multiplica por diez** (Microsoft). Es un caso del corpus (ORU-B29):

```
OBX|1|NM|1988-5^PCR^LN||.5|mg/L^mg/L^UCUM|<5|N|||F
```

```json
"valueQuantity": { "value": 5, … }
```

En HL7 v2 un número puede empezar por el punto decimal (v2.5, capítulo 2A, tipo NM). La plantilla escribe `"value":.5`, que no
es JSON válido. El paso que analiza y arregla el JSON se salta el punto y lo deja en 5.

**Resultados colgados de un paciente que no existe** (Microsoft). En un ORU^R01 el paciente es opcional (v2.5, capítulo 7). Sin
el segmento PID:
- el conversor escribe `subject: Patient/364bf61f-…` en cada Observation;
- ese Patient no está en el Bundle;
- el identificador se calcula con PID-3 (`data/Templates/Hl7v2/ID/_Patient.liquid`), así que sin PID sale siempre el mismo. Se
  vio en los dos mensajes sin PID que se probaron, uno del corpus y el mínimo.

Resultados de personas distintas acabarían apuntando al mismo paciente inexistente.

**Un paciente al que se da por muerto** (Microsoft). En un traslado (ADT^A02), un segmento PDA sin datos de muerte basta para
escribir `deceasedBoolean: true`. Aquí, el PDA solo lleva el nulo explícito `""` en su primer campo. El mensaje no dice en ningún
sitio que el paciente haya muerto. Con un PDA relleno, inferir la muerte sería razonable; con uno así, no.

```
PID|1||P0001^^^HOSP^MR||PRUEBA^ANA||19800101|F
PDA|""
```

**«Separado» que pasa a «anulado»** (LinuxForHealth). PID-16 «A» es *Separated* en la tabla HL7 0002. El conversor copia la
letra al sistema de códigos de FHIR, donde «A» es *Annulled*. La guía da «L», *Legally Separated*.

```json
"maritalStatus": { "coding": [{ "system": ".../v3-MaritalStatus", "code": "A", "display": "Annulled" }] }
```

**Resultados que desaparecen** (LinuxForHealth). Un OBX sin tipo de valor y sin valor no da ninguna Observation, y el informe
sale sin resultados. Es una forma válida de mandar un resultado que no se pudo obtener (OBX-11 «X») o que está pendiente («I»):
OBX-2 es condicional.

```
OBX|1||2345-7^Glucosa^LN||||||||X
```

Su propia plantilla dice en un comentario que en ese caso sí debe crearla.

**Texto con formato y horas que se pierden** (LinuxForHealth). Un OBX de tipo FT (texto con formato) o TM (hora) da una
Observation sin valor. La plantilla solo escribe `valueString` para el tipo ST.

**Un rango que pasa a ser un número** (LinuxForHealth). El valor estructurado «1-5» se escribe como valueQuantity **1**.

```
OBX|1|SN|2345-7^Glucosa^LN||^1^-^5|mg/dL^mg/dL^UCUM
```

```json
"valueQuantity": { "value": 1, … }
```

### Las otras ocho

| Conversor | Discrepancia |
|---|---|
| Microsoft | De un médico remitente repetido (PV1-8), solo llega el primero |
| Microsoft | Un estado civil «no declarado» (T) se pierde; la guía da un nullFlavor |
| LinuxForHealth | No hay Encounter.location: la ubicación del paciente (PV1-3) no se convierte |
| LinuxForHealth | Las partes 2 y 3 de la calle (SAD.2 y SAD.3) no llegan a la dirección |
| LinuxForHealth | Un sexo «no aplicable» (N) pasa a «desconocido»; la guía da «otro» |
| LinuxForHealth | Un resultado borrado (OBX-11 «D») pasa a «cancelado»; la guía da «introducido por error» |
| LinuxForHealth | Un informe con la muestra recibida (OBR-25 «I») pasa a «desconocido»; la guía da «registrado» |
| LinuxForHealth | El «otro profesional» de la visita (PV1-52) se pierde |

**Tres de estas tienen matiz:**
- en «no aplicable» y en OBR-25, la guía elige una traducción y el conversor eligió otra; para «no aplicable», tanto «otro» como
  «desconocido» pierden algo;
- PV1-52 es un campo que v2.5 conserva por compatibilidad;
- el mensaje mínimo de SAD.2 y SAD.3 lleva un texto artificial en esas partes.

**En la rama principal de cada proyecto siguen 14 de las 15.** La otra es «borrado» que pasaba a «cancelado». LinuxForHealth
cambió ese mapeo por su cuenta en febrero de 2026, sin saber de este laboratorio: es lo más cercano a una confirmación
independiente. Lo hizo después de la versión juzgada, y todavía no ha publicado una versión que lo lleve.

### Lo que los proyectos ya sabían

El juez vio también **31 discrepancias que los proyectos ya tenían declaradas**. Son el control positivo: si el juez no viera lo
que los autores ya saben, nada de lo demás valdría. Entre ellas:

- **Microsoft:**
  - apunta Encounter.location al componente menos granular de la ubicación (un issue abierto);
  - cuando dos resultados tienen el mismo código, se queda con uno (su documentación lo explica);
  - pierde el resultado que sigue a una nota (un issue, en sus comentarios).
- **LinuxForHealth:**
  - toma la fecha de inicio de la visita del evento cuando falta la de admisión (una prueba lo afirma);
  - no soporta tres de los eventos ADT probados (su README lo dice).

## Lo que el juez se equivocó, y se corrigió

Un juez que juzga a otros tiene que mirarse primero. Durante el estudio se le encontraron **once defectos**, cada uno arreglado
con su prueba en rojo antes del código:
- **4, al revisar el primer juicio.** Por ejemplo: no conocía PID-12, el código de condado, y no admitía las formas que la guía
  permite para un resultado repetido.
- **4 en los que la guía admitía lo observado.** Por ejemplo: «5.» es lo mismo que 5, y el identificador de la visita lleva el
  tipo «VN» fijo en la hoja del segmento.
- **3 que dejó el contraste.** El más claro, un falso positivo: los dos conversores ponen el nombre de la autoridad que asigna el
  identificador transformado («urn:id:NIST_MPI»), y el juez buscaba el texto literal.

**Lo que no se hizo fue mover la previsión.** Estaba sellada y falló por mucho:
- **Los casos ADT correctos:** esperaba entre un 30 y un 65 %, y salieron entre un 2 y un 4 %. El mecanismo, la ubicación del
  paciente, estaba previsto; nadie previó que se llevara casi todos los casos.
- **Los rechazos:** esperaba que se quedaran por debajo del 5-10 %, y salieron del 27 % y el 35 %.
  - De los de Microsoft, 30 eran un mensaje mal hecho del propio corpus del laboratorio: un segmento GT1 desplazado un campo.
  - Los de LinuxForHealth eran eventos que esa versión no soporta.

Eso queda escrito, no corregido.

## Lo que esto no dice

- **No es una certificación de conformidad.** Es lo que un juez con sus decisiones declaradas ve en estos mensajes y en estas
  versiones:
  - **Microsoft FHIR-Converter v7.0.**
  - **LinuxForHealth hl7v2-fhir-converter v1.1.0,** la última publicada en Maven Central. En GitHub hay una etiqueta v1.1.1 y una
    rama principal que soportan más eventos. La v1.1.0 rechaza tres de los ocho eventos ADT probados, y eso se contó como
    rechazo, no como discrepancia.
  - **Las ramas principales de los dos,** tal como estaban en octubre de 2026.
- **Cubre ocho eventos ADT y ORU^R01.** No cubre programación de citas (SIU), documentos (MDM), vacunas (VXU) ni los demás tipos.
- **Los mensajes son sintéticos o públicos.** No hay datos de ningún paciente.
- **El juez lee los tipos de datos de v2.5.** Las muestras de los proyectos son casi todas de v2.8, y lo que dependía de
  componentes posteriores se apartó.
- **Los dos conversores son proyectos serios y útiles.** Las discrepancias son con una guía concreta, en una versión concreta.
  Parte de lo que encontró el juez ya estaba en su documentación, y una la ha cambiado el propio proyecto.

## Cómo reproducirlo

El verificador corre con Python 3 y nada más. Sus pruebas, incluidas las 116 comprobaciones del perfil «guía», pasan sin el
laboratorio ([`verificador/README.md`](verificador/README.md)). Para repetir el estudio hacen falta además cuatro cosas:
- **Docker,** para la caja.
- **Los dos conversores:** Microsoft, construido desde su código; LinuxForHealth, el jar que publica en Maven Central; y las
  ramas principales de los dos, desde su código ([`verificador/cv/CV1.md`](verificador/cv/CV1.md) y
  [`verificador/cv/RESULTADO-15A.md`](verificador/cv/RESULTADO-15A.md)).
- **Las muestras públicas de cada proyecto.**
- **El paquete `hl7.fhir.uv.v2mappings` 1.0.0,** solo si se quieren regenerar los mapas de la guía, que el juez ya lleva.

Los 68 mensajes mínimos salen de `python3 verificador/cv/cv3_minimos.py escribir <carpeta>`.

## Lo que se lleva uno a su trabajo

- **Probar un conversor contra la guía, no contra su foto.** Las salidas esperadas de un proyecto dicen qué hace, no si está
  bien.
- **Un par mínimo vale más que cien casos reales.** Un mensaje con solo el disparador, y otro sin él, deja una discrepancia sin
  discusión.
- **Lo que se espera, escrito antes.** La previsión de este estudio falló por mucho, y eso enseñó tanto como lo que encontró. El
  mecanismo más frecuente estaba previsto, pero se llevó casi todos los casos. Y una parte de los rechazos era un defecto del
  propio corpus.
- **Buscar fuera de los casos bonitos:** un nulo explícito, un PID ausente, un número que empieza por el punto, un resultado
  pendiente. Ahí estaban casi todos los fallos que importan.

---

*El código va bajo MIT y los documentos bajo CC BY 4.0 ([`LICENSE.md`](LICENSE.md)). HL7® y FHIR® son marcas registradas de
Health Level Seven International. Este laboratorio no tiene relación con los proyectos juzgados.*
