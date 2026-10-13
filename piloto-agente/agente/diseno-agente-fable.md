<!-- Modelo: Claude Fable 5.1 (claude-fable-5-1). Fecha: 12-oct-2026. AG0: diseño del piloto del agente; a ciegas de los arreglos de H; leído solo scratchpad/ag0 -->

# Diseño del piloto «agente que se apoya en el verificador» (AG0, 12-oct-2026)

Referencia contra la que se medirá todo. Lo implementa otro (Claude), que declara cada desviación como DV-AG-n y fija en git la
regla de parada **antes** de medir. Etiquetas: S-AG (decisión propuesta), Q-AG (pregunta a Jev, desde la 8), L-AG (límite
declarado de entrada), DV-AG (reservada a la implementación).

Lo que este diseño da por fijado (ANTES, 12-oct): cuentan H + R, M es control y calibración (Q-AG-1); se mide localizar (top-3) y
parchear, por separado, y el parche lo juzga el verificador en la caja (Q-AG-2); el agente es un subagente de Claude en una
carpeta cerrada, con un segundo brazo DeepSeek si alcanza el saldo (Q-AG-3); la referencia sin modelo se construye, controla y
congela antes que el agente (Q-AG-4); el agente ve el veredicto, la fuente y el MCP, y nada más (Q-AG-5); este diseño es a ciegas
de los arreglos de H (Q-AG-6); tres sesiones, ≤ 70 casos × 2 réplicas, DeepSeek ≤ 2 USD (Q-AG-7).

Lo que AG-pre obliga a resolver aquí, y dónde se resuelve: (1) huella de la reconstrucción → §1.1 y §1.5; (2) la salida grande del
MCP → §2.1; (3) el agente usa al juez como oráculo → §2.4 y §3.3; (4) los parches buenos no se parecen al de referencia → §4.1
y §4.2; (5) coste → §2.5 y §4.4; (6) el enum viejo del MCP → §5 (puerta de AG1); (7) un parche cambia el `Storage` → §1.5.

---

## 0. La pregunta, en las dos frases que se contestarán

> Dado un circuito que falla y el veredicto del verificador, ¿un agente con modelo **localiza la causa en el código** y **propone
> un arreglo que el verificador da por bueno** (frase 1: «funciona»), **mejor que una búsqueda sin modelo** (frase 2: «hace
> falta»)?

Las dos frases se reportan juntas, cada una con su intervalo, y «no aporta» es un resultado válido (§4.5).

Vocabulario fijo del diseño:

| Término | Significado |
|---|---|
| **caso** | Un fallo de un circuito: un árbol de fuente que falla, sus **disparadores** (mensajes que el verificador juzga no `correcto` por ese fallo) y su **regresión** (mensajes que el verificador juzga `correcto` con ese árbol y deben seguir así) |
| **caja** | El sitio donde se carga un árbol con un cambio y se mide: LABMUT (congelado), las cajas de LABADT y LABORU (§1.1, Q-AG-8) y el contenedor Mirth efímero |
| **clave** | La verdad de referencia de cada caso: qué unidad del código es la causa, disparadores y regresión, y para H el diff del arreglo. Está fuera de la caja, sellada con huella |
| **unidad** | La granularidad de la localización: el bloque que contiene una línea (§4.1) |
| **tirada** | Una ejecución de un brazo sobre un caso (el agente tiene 2 tiradas por caso: las réplicas) |
| **brazo** | Quien resuelve el caso: `REF` (referencia sin modelo), `AG` (subagente de Claude), `DS` (DeepSeek), y los controles `VACIO` (parche vacío) y `FIX` (arreglo de referencia de H) |

---

## 1. Los corpus, caso a caso como plantilla

### 1.1 Las cajas y el exportador común (sin huella)

**S-AG-1. Un solo exportador de árboles para los tres corpus.** Todo árbol que entre en una caja del agente sale de la misma función
`exportar(arbol, destino)`: lee los ficheros de una **revisión de git** (nunca del directorio de trabajo), escribe con `\n`, UTF-8
sin BOM, sin fichero oculto, sin `.git`, con los nombres de fichero tal cual y ordenados, y registra en la clave el hash del árbol
(`git rev-parse <rev>:<dir>`) y el sha256 de cada fichero exportado. H exporta la revisión **padre del commit del arreglo**; R exporta
la revisión del congelado; M exporta la revisión actual y aplica la sustitución del mutante **sobre el texto exportado**, con la
misma sangría que la línea sustituida (el arnés lo comprueba: la línea nueva empieza con los mismos blancos que la vieja). Así ninguna
caja lleva una pista de «cómo se construyó», que fue la fuga de AG-pre (punto 1).

**S-AG-2. Las cajas de IRIS son namespaces aparte, nunca los circuitos de producción del laboratorio.** LABMUT ya existe
(`mutacion.py crear`: copia del congelado con puerto 2576 y `SistemaIdent` propio). Para LABADT y LABORU hacen falta dos cajas
iguales: `LABADTMUT` (puerto 2596, `SistemaIdent`/`SistemaVisita` → `urn:lab:mutantes:mrn` / `urn:lab:mutantes:visit`) y
`LABORUMUT` (puerto 2595, sistemas propios), creadas con la misma receta que LABMUT (crear el namespace, cargar el árbol, copiar la
credencial sin imprimirla, nunca dos producciones del mismo circuito en marcha a la vez). Las tres cajas comparten el servidor FHIR
real: los sistemas de identificación propios evitan que sus recursos se mezclen con los de los circuitos vivos. Alternativa y por qué
no: el mecanismo de A5/MS3 (cargar el mutante en el namespace de producción, restaurar y comprobar la huella) ya está probado, pero un
parche ajeno puede tocar `Storage`, dejar globals y pasar por la producción viva (punto 7); «nada del agente toca los circuitos de
producción» es un «hecho cuando» del ANTES. Es Q-AG-8.

La pieza común se mide en la caja del circuito donde se observó el fallo: su árbol pre-arreglo se exporta **junto con** el árbol del
circuito en la misma revisión (padre del commit del arreglo), de modo que la caja contiene exactamente lo que había entonces.

Mirth: contenedor efímero (`mi3.copia` + `agpre.py`), sin cambio.

### 1.2 Corpus H: fallos históricos reales (plantilla, 8 filas, 7 que pueden contar)

Estoy a ciegas de los arreglos (Q-AG-6): la plantilla fija **cómo** se construye y se valida cada caso, y los números se rellenan en
AG1 sin que yo intervenga.

Para cada H-n (1 de LABADT, 5 de LABORU, 2 de la pieza común; H-MI-1 no cuenta, §1.6):

| Campo de la clave | Cómo se obtiene | Regla |
|---|---|---|
| `commit_arreglo` | El commit que arregló el fallo | Un commit por caso. Si el arreglo se repartió en varios commits consecutivos sin medida entre ellos, el «arreglo» es el rango y el «antes» es el padre del primero (se declara) |
| `arbol_antes` | `exportar(commit_arreglo^, circuito + comun)` | Es lo que ve el agente como «fuente actual» |
| `arbol_despues` | `exportar(commit_arreglo, …)` | Solo para construir la clave; nunca entra en la caja |
| `verdad` | Los hunks del diff `antes → despues` restringidos a ficheros del circuito (sin tests ni documentación): por hunk, fichero, líneas **del árbol antes** quitadas o modificadas; para un hunk de pura inserción, la línea del árbol antes **anterior** al punto de inserción. De cada línea se deriva su **unidad** (§4.1) | Es la clave de localización. Se guarda también `n_unidades_verdad` (parches que tocan varios sitios, punto 4) |
| `disparadores` | Los mensajes del banco del circuito (sus bases reales y construidas, las del A4/MS2/ORU v1.1) que, con **el verificador de hoy**, dan no `correcto` con `arbol_antes` **y** `correcto` con `arbol_despues` | `D(H) = {m : antes(m) ≠ correcto ∧ despues(m) = correcto}`. Mínimo 3; si hay menos, el caso no entra (se declara). Si hay más de 25, se toman 25 por orden sembrado (semilla `AG1|H-n`) |
| `regresion` | Los mensajes `correcto` con los dos árboles | `R(H) = {m : antes(m) = correcto ∧ despues(m) = correcto}`, hasta 60 por orden sembrado, estratificados por lote (al menos 5 de cada lote del banco si existen) |
| `excluidos` | Los que no son `correcto` con ninguno de los dos árboles | Son otros fallos vivos de aquella revisión: no cuentan ni como disparador ni como regresión, y se listan en la clave |
| `categoria_prevista` | La categoría del veredicto en los disparadores, **por definición** con la leyenda (lección 4) | Se escribe antes de medir; si la medida difiere, se adjudica y se anota, no se corrige la previsión |
| `caso_mostrado` | El primer disparador por orden sembrado | Es el único mensaje cuya evidencia ve el agente; el resto solo como recuento (`otros_casos_que_fallan`) |

Cada H pasa **tres puertas** en AG1 (y si no las pasa, no cuenta, se declara y se sigue):

1. **Falla antes:** `|D(H)| ≥ 3` con el verificador de hoy. Si el verificador de hoy ya no ve el fallo (porque cambió desde el
   arreglo), el caso se retira: «H-n: invisible para el juez actual».
2. **El arreglo de referencia lo arregla:** brazo `FIX` (aplicar el diff en la caja sobre `arbol_antes`, compilar, medir): `correcto`
   en el 100 % de `D(H)` y **0 colateral** en `R(H)`. Por construcción debería ser así; si no lo es, el evaluador o el árbol están
   mal y el caso no entra hasta que se explique.
3. **El parche vacío no arregla nada:** brazo `VACIO`: 0 de `|D(H)|` `correcto`, y la firma (`observar_uno`) de cada disparador es
   igual a la de la medida de la puerta 1 (el aparato es estable entre dos pasadas).

Las tres puertas se guardan como `controles_H-n.json` con fecha, huella del verificador (`version.huella`) y hash del árbol.

### 1.3 Corpus R: los 7 fallos vivos del congelado (caja LABMUT)

Todos salen de `CONOCIDOS-ANTES-DEL-SELLO.md`. Los disparadores se construyen sobre los basales de `mutacion.pool()["P1"]` (los
mismos que usó `agpre_iris.py`), con funciones de construcción nuevas donde falten; la regresión es la de AG-pre: los 60 primeros
basales (60 de 60 `correcto` medido el 12-oct). Para R no hay diff: la clave de localización es una **zona preinscrita** (§4.1,
regla R) y el arreglo aceptado es el del verificador sin colateral.

| Caso | Fallo (CONOCIDOS) | Disparadores (construcción sobre basales AA; n = 5 salvo que se diga) | Categoría prevista por definición | Zona preinscrita (la escribe el implementador en AG1 y se sella; **mi** lectura a ciegas, solo como control de la suya) | Cuenta |
|---|---|---|---|---|---|
| **R1** | `MSA\|CE` no conforme con FHIR inalcanzable, y el `AE` razonado que nunca llega | 5 basales con el puerto FHIR cerrado en la caja (`operador del catálogo (no publicado)`; el entorno se describe en la evidencia como manda A-18) | `acuse_incorrecto` (el acuse que fabrica el motor: ERR-3 vacío, sin MSH-9.3); si el verificador lo lee como entorno, se adjudica | `Lab.HL7.Operation.FhirPatient.Enviar` (rama «sin respuesta HTTP») y/o la configuración del servicio en `Lab.HL7.Production` (quién fabrica el CE: el motor cuando la operación no devuelve ACK a tiempo) | Sí, con reserva: el fallo depende de un tiempo de espera; si en la caja no se reproduce en 5 de 5, se retira (Q-AG-10) |
| **R2** | La entrada no se desescapa: `\S\` llega literal al canónico y a FHIR, con AA | 5 basales con `PID-5.1 = X\S\Y` (`r2` de `agpre_iris.py`) y 3 más con `\T\` y `\E\` en PID-5.2 | `fallo_silencioso` / fidelidad PID-5 | `Lab.HL7.Util.Pid` (`Apellidos`, `Nombre`, `UnirSubcomponentes`): no llama a `Lab.HL7.Util.Ack.DesescaparHL7`, que existe | Sí |
| **R3** | Un 4xx de FHIR se contesta AR 102, culpando al emisor de un fallo de entorno | 5 basales con credencial inválida (`ENV_FHIR_CREDENCIAL_401`) y 3 con ruta inexistente (`ENV_FHIR_RUTA_404`), entorno declarado | `acuse_incorrecto` / codigo (esperado AR 207 por S29) | `Lab.HL7.Operation.FhirPatient.Enviar`, bloque «Hallazgo 6» (`tEsCliente` → 102) | Sí |
| **R4** | `MAXREP = 10`: un MR o un L en la repetición 11 se ignora | 5 con `PID-3` con el MR en la repetición 11 (`PID3_MR_EN_REPETICION_11`) y 5 con la L de `PID-5` en la 11 | `fallo_silencioso` / fidelidad PID-3 y PID-5 | `Lab.HL7.Util.Pid` (`Parameter MAXREP`, `Identificador`, `RepeticionNombre`) | Sí |
| **R5** | PV1 antes de PID se contesta AR 101; lo correcto es AE 100 | 5 con PID y PV1 intercambiados (`r5`) | `acuse_incorrecto` / codigo | `Lab.HL7.Transform.AdtToPatient` (sin comprobación de estructura) + `Lab.HL7.Msg.PatientRequest.MotivoRechazo` + `FhirPatient.Enviar` (AR fijo). **Tres unidades**: es el caso de parche multisitio de R | **No cuenta: es el caso de AG-pre** (el arnés y la consigna se afinaron sobre él). Entra como control positivo de la cadena IRIS (Q-AG-10) |
| **R6** | Con MSH-10 vacío el acuse lleva un `SINID` inventado, distinto en cada ejecución | 5 basales con `MSH-10` vacío (`operador del catálogo (no publicado)`) | `acuse_incorrecto` (MSA-2 debe ser vacío/íntegro, S100) | `Lab.HL7.Util.Ack.Construir` (`"SINID"_$zcrc(...)`) | Sí |
| **R7** | `ERR-3 = 104`, que no existe en la 0357 | 5 con `PID-3.1` de 200 caracteres (`operador del catálogo (no publicado)`) y 3 con `PID-5.1` de 300 | `acuse_incorrecto` / codigo (esperado: por S3 se acepta truncado → AA; si el juez de hoy espera otra cosa, se adjudica por definición antes de sellar) | `Lab.HL7.Msg.PatientRequest.MotivoRechazo` (rama `..Truncado` → 104) y `Lab.HL7.Transform.AdtToPatient` (marca `Truncado`) | Sí |

Puertas de R en AG1: cada caso **falla** con el congelado en LABMUT en ≥ 5 de sus disparadores (si no, se retira o se reconstruye
el disparador, declarado); la regresión da 60 de 60 `correcto`; `VACIO` = 0 arreglados. No hay `FIX` para R (no hay diff); el control
positivo de la cadena es el parche de AG-pre para R5 (5 de 5, 0 colateral, medido).

Lo que la clave de R guarda además: la **zona preinscrita** (unidades), escrita por el implementador en AG1 **antes** de cualquier
tirada y sellada con el resto, y mi lectura a ciegas de arriba como segunda opinión (si las dos difieren, la zona sellada es la unión y
se declara).

### 1.4 Corpus M: control y calibración (12 mutantes, estratificados por la decisión que sirven)

M no cuenta en las frases; sirve para **tres decisiones**, y cada mutante se elige por una de ellas:

| Decisión que sirve | Mutantes | Caja | Por qué estos |
|---|---|---|---|
| **(a) Calibrar la referencia** (¿es un adversario fuerte? debe localizarlos en top-3 por unidad) y comprobar que el agente al menos encuentra fallos con firma | `M01` (apellidos↔nombre), `M04` (sexo siempre `unknown`), `M03` (día↔mes en PID-7), `MA1` (status fijo), `MMI-6` (Gender crudo) | LABMUT ×3, LABADTMUT, Mirth | Fallos de fidelidad de **una línea** que nombran el campo: la firma mecánica más clara. Si la referencia no los encuentra, es débil y se refuerza antes de congelar (§3.5) |
| **(b) Calibrar «acuse»**: códigos y MSA-1 | `M10` (207 por 200), `M07` (AE fijo), `MSM-8` (MSA-2 inventado), `MMI-1` (MSA-2 = «1») | LABMUT ×2, LABMULTI-caja o LABADTMUT (`comun`), Mirth | Fallos del acuse: la plantilla de parche T1 (§3.2) debería cerrarlos; si la referencia los parchea, el agente tiene que superar algo más que un parche vacío |
| **(c) Ausencias y estructura** (el fallo es que falta una comprobación, o está en XML/configuración) | `MA11` (Validate `dm` de más: rechaza Z y opcionales fuera de sitio), `MA10` (PV1-2 = N crea Encounter), `M09` (regla de enrutado a A08) | LABADTMUT ×2, LABMUT | Firmas más débiles (una línea borrada, una regla XML): miden si la referencia cae donde el agente quizá no |

Para cada mutante: disparadores = su población mordida ya medida (A5, MS3, MI3, `mutacion.py`), hasta 10; regresión = 10 de control
`correcto`; puertas = las de su campaña (muerde ≥ 95 % con la previsión, colateral 0). Se reaprovechan los números ya medidos; en AG1
solo se vuelve a medir el **caso mostrado** de cada uno (una pasada) para tener la evidencia que ve el agente con el verificador de hoy.

**Casos limpios (control negativo de los dos brazos, 3):** tres cajas con el árbol actual sin cambio y la evidencia de un mensaje
`correcto` (una de LABADT, una de LABORU, una del congelado), presentadas con la misma consigna. La respuesta buena es «no hay fallo
que localizar» (§2.3). Un brazo que proponga localización o parche en un caso limpio suma una **falsa alarma**. `E01` (cambio de
comentario, equivalente) sirve de cuarto caso limpio en LABMUT si el tiempo alcanza.

### 1.5 Restauración entre tiradas y el `Storage` (punto 7)

Tras cada evaluación de parche en una caja de IRIS: parar la producción; recargar el **árbol base completo** de la caja (no solo los
ficheros tocados); para cada fichero tocado por el parche, bajar el fuente vivo por Atelier y comprobar que es **idéntico byte a byte**
al exportado (no solo que no contiene las marcas del mutante, como hace `restaurar_todo`); arrancar; mandar 5 mensajes de la regresión
(los mismos siempre, sembrados) y exigir que su firma sea igual a la del brazo 0 de AG1. Si una clase persistente cambió de `Storage`,
el fuente vivo no coincidirá y la comprobación lo verá; la recarga del base lo deja como estaba. Los globals de datos de
`Lab.HL7.Msg.*` quedan (son compatibles: una propiedad nueva solo añade un subíndice) y no entran en la evidencia. Si la comprobación
falla dos veces seguidas, la caja se destruye y se vuelve a crear desde el exportador (es barato y realista).

En Mirth la caja es efímera por tirada: nada que restaurar.

### 1.6 Lo que no cuenta y por qué

- **H-MI-1** (Mirth, AG-pre): la consigna y el evaluador se afinaron con él; el agente ya lo vio. Es el control de la cadena Mirth.
- **R5** (IRIS, AG-pre): idem. Control de la cadena IRIS (Q-AG-10).
- Los H que no pasen las tres puertas, con su motivo escrito.

### 1.7 El sellado

La clave vive fuera de la caja (`privado/agente/ag1_clave.json`): por caso, id interno, corpus, circuito, caja, hash del árbol,
`verdad` o zona preinscrita, disparadores y regresión (ids de mensajes y sha256 del cable de cada uno), categoría prevista, y los
resultados de las puertas. Se sella así:

1. `sha256(ag1_clave.json)` se escribe en `etapa/SELLO-AG1.md` y **se commitea antes de la primera tirada** de cualquier brazo;
   la clave en sí no se publica (lleva ids de los H y, en el futuro, los parches).
2. Cada caja se genera desde la clave con un nombre **opaco** (`caja/<8 hex de sha256("AG1|" + id + "|" + réplica)>/`), y el mapa
   opaco → caso está solo en la clave. Nada del contenido de la caja lleva el id del caso: los ids de mensaje de la evidencia se
   sustituyen por `m-<4 hex>` (en AG-pre la clave de pool era `piloto/<i>/R5`: eso es una fuga y no puede repetirse).
3. La **referencia** se congela antes: su código, sus tablas y los resultados de sus tres controles (§3.5) con sha256 en el mismo
   `SELLO-AG1.md`.
4. La **consigna** (§2.2), el presupuesto por caso (§2.5) y el guion de análisis (§4) se commitean en el mismo sello.
5. Las reglas de parada (§5) van en el sello, como números.

---

## 2. El protocolo del agente

### 2.1 Qué ve (y qué no)

Una carpeta por tirada, generada por el arnés, con exactamente:

| Fichero | Contenido |
|---|---|
| `CONSIGNA.md` | El texto fijo de §2.2 |
| `caso.json` | `evidencia` (lo que vio el juez: mensaje, ACK, log, recorrido, canónico y almacén releído si los hay), `veredicto`, `hallazgos` **solo los que cuentan** (`cuenta: true`), `otros_casos_que_fallan` (un número). Ids de mensaje opacos. Sin claves de pool, sin nombres de fichero del arnés, sin fechas de construcción |
| `fuente/` | El árbol exportado (§1.1). Para el congelado, las 10 clases; para LABADT/LABORU, el circuito y la pieza común; para Mirth, los 7 ficheros del canal |
| `verificador.json` | **Copia en la caja** de lo que daría `info_verificador`, con las secciones que describen implementaciones de circuitos quitadas (como la copia MI0: sin `desviaciones_*` ni `deudas_circuito_*`). Es idéntica para todos los casos y brazos. Resuelve el punto 2: la salida grande no sale de la caja porque no se pide |

**S-AG-3. El MCP del agente es el `verificador` con cinco herramientas:** `verificar_caso`, `ficha_experto`, `acuse_esperado`,
`comparar_canonico`, `consultar_tabla`. **Sin `info_verificador`** (está en la caja). Si otra herramienta derrama su salida a un
fichero por tamaño, el directorio de derrame se configura **dentro de la caja** (`caja/<id>/mcp_out/`); si no se puede configurar, la
herramienta se quita y se declara DV-AG. El enum de puntos de entrada del MCP debe listar `adt_fhir` y `oru_fhir` (puerta de AG1,
punto 6).

**S-AG-4. Lo que el agente no ve ni puede tocar:** git, diffs, huellas, la versión buena, la clave, otras cajas, el disco fuera de la
carpeta, la red, IRIS, Mirth. Cómo se impide (tres capas, las tres obligatorias):

1. **Lanzamiento cerrado:** el subagente se lanza en modo no interactivo con la carpeta de la tirada como directorio de trabajo y con
   la lista de herramientas restringida a `Read`, `Grep`, `Glob`, `Write` y las cinco del MCP (sin `Bash`, sin web, sin otros MCP).
   La carpeta está **fuera del repositorio del laboratorio y fuera de su scratchpad** (un proyecto distinto para la herramienta:
   una carpeta `ag-caja/<id>/` en el directorio del usuario), para que no herede la memoria ni el `CLAUDE.md` del laboratorio (§6.2, L-AG-5).
2. **Auditoría de la transcripción:** el arnés guarda la transcripción completa (JSON) de cada tirada y la escanea: toda ruta
   leída o escrita debe estar bajo la carpeta de la tirada; toda llamada MCP es de las cinco; la única escritura es
   `respuesta.json`. Una tirada que viole esto queda **inválida** (no cuenta, se repite una vez con una carpeta nueva, se registra).
3. **Nada que robar:** aunque saliera de la carpeta, la clave y los árboles «después» no están en la misma máquina que la caja
   del agente durante AG2 (la clave se copia a la otra máquina solo en AG3 para adjudicar), o están cifrados en reposo con una clave que
   el arnés solo lee al adjudicar. Mínimo exigido: no estar bajo ninguna ruta legible desde la carpeta de la tirada.

### 2.2 La consigna fija (preinscrita; una sola redacción para H, R, M y limpios)

El texto siguiente se usa tal cual. Las partes entre `{}` las rellena el arnés desde la clave y toman solo dos valores por campo
(motor IRIS/Mirth y punto de entrada), nunca el id del caso.

```
# Consigna: diagnostica y, si lo hay, arregla un fallo de un circuito de integración

Eres el ingeniero de guardia de un circuito de integración HL7 v2.5 → FHIR R4 construido en {MOTOR: «InterSystems IRIS for Health
(ObjectScript, interoperabilidad)» | «Mirth Connect 4.5.2 (JavaScript Rhino, ES5)»}. Un verificador determinista (el juez) ha
juzgado un mensaje. Tu trabajo es: (1) decidir si el veredicto señala un fallo del circuito; (2) si lo señala, encontrar en el código
la causa; (3) proponer un arreglo. El juez no se toca: lo que decide es él.

## Reglas
- Lee solo dentro de esta carpeta. No uses red, ni ssh, ni git, ni otras rutas del disco. No ejecutes nada.
- Puedes usar las herramientas del MCP `verificador` (`verificar_caso`, `ficha_experto`, `acuse_esperado`, `comparar_canonico`,
  `consultar_tabla`). Lo que declara el verificador (decisiones S-n, supuestos, límites, puntos de entrada) está en
  `verificador.json`. El punto de entrada de este circuito es `{PE}`.
- Presupuesto: {PRESUPUESTO_TOKENS} tokens, {PRESUPUESTO_LLAMADAS} llamadas a herramientas y {PRESUPUESTO_MINUTOS} minutos. Al agotarlo
  se te corta y la tirada cuenta como «sin respuesta»: escribe `respuesta.json` antes.
- Tu arreglo lo aplicará y medirá otro, con el juez, sobre muchos mensajes, no solo este. No tienes forma de ejecutar el circuito.

## Qué hay en la carpeta
| Ruta | Qué es |
|---|---|
| `caso.json` | `evidencia` (lo que vio el juez), `veredicto` y `hallazgos` del juez, y `otros_casos_que_fallan` (cuántos mensajes más fallan igual; 0 si el veredicto es `correcto`) |
| `fuente/` | El código actual del circuito |
| `verificador.json` | Lo que el juez declara |

## Qué debes entregar
Escribe `respuesta.json` en esta carpeta (con la herramienta de escritura):
{
  "hay_fallo": true | false,
  "localizacion": [ {"fichero": "…", "linea": 123, "por_que": "una frase"} ],
  "parche": {"cambios": [ {"fichero": "…", "viejo": "texto exacto actual", "nuevo": "texto nuevo"} ]} | null,
  "explicacion": "cinco líneas como máximo: causa, por qué el arreglo es correcto y qué otros mensajes podría arreglar"
}
- `hay_fallo`: false si, leído el veredicto y el código, concluyes que no hay nada que arreglar en el circuito; entonces
  `localizacion` va vacía y `parche` es null.
- `localizacion`: hasta 3 líneas, la más probable primero. Vacía si no encuentras la causa (es una respuesta válida).
- `parche`: sustituciones de texto; cada `viejo` debe aparecer exactamente una vez en su fichero; como máximo 6 cambios en 3 ficheros;
  no toques puertos, credenciales ni ajustes de conexión. {IRIS: «La clase tiene que compilar en IRIS.»} El arreglo tiene que dejar
  `correcto` los mensajes que fallan por esta causa sin romper ninguno de los que hoy pasan. Si no tienes un arreglo del que fiarte,
  pon null: un parche que rompe lo que pasaba vale menos que ninguno.

Al terminar, devuelve solo el contenido de `respuesta.json`.
```

Diferencias con la consigna de AG-pre, y por qué: `hay_fallo` (para los casos limpios y para que «no encontrar» sea una respuesta,
§2.3); sin `info_verificador` (punto 2); presupuesto explícito (punto 5); «no toques puertos ni credenciales» (el evaluador rechaza
esos parches, §4.2); «null vale más que romper» (porque colateral 0 es condición de aceptación). No hay más cambios: lo demás es el
texto que ya funcionó en AG-pre. **No se retoca después de la primera tirada** (fragilidad: §6.4).

### 2.3 Qué hace si no encuentra nada

`hay_fallo: true`, `localizacion: []`, `parche: null` es una respuesta válida: cuenta como **no localizado** y **no arreglado**, sin
penalización extra. `hay_fallo: false` en un caso con fallo cuenta igual (no localizado, no arreglado) y además como **negación
falsa** (se reporta aparte). En un caso limpio, `hay_fallo: false` es la respuesta correcta; cualquier localización o parche es
**falsa alarma**. Una tirada cortada por presupuesto sin `respuesta.json` es «sin respuesta» = no localizado, no arreglado, y se cuenta
cuántas hay por brazo.

### 2.4 El juez como oráculo (punto 3)

**S-AG-5. Se permite, se cuenta y se iguala.** El agente puede llamar a las cinco herramientas cuantas veces quepa en el presupuesto
(§2.5); el arnés registra por tirada cuántas llamadas, a qué herramienta y con qué punto de entrada, y lo reporta como coste y como
descripción del comportamiento («sondeó n variantes antes de proponer»). La referencia hace **tres sondas fijas** con las mismas
herramientas (§3.3). Ninguno de los dos puede ejecutar el circuito: `verificar_caso` juzga evidencias construidas a mano, no un
circuito parcheado; eso es igual para ambos. Alternativa (Q-AG-9): quitar el MCP a los dos y medir solo lectura de código; se pierde lo
que AG-pre vio que el agente hace de verdad.

### 2.5 Modelo, réplicas y presupuesto por caso

- **Brazo AG:** el mismo modelo y la misma herramienta de subagente que en AG-pre (declarados en el sello con nombre y versión); si
  el implementador elige otro, es DV-AG con motivo. **2 réplicas** por caso, temperatura la de la herramienta (la variación entre
  réplicas es parte de la medida), carpetas distintas, orden de tiradas sembrado (§5, AG2).
- **Brazo DS:** DeepSeek (modelo de chat con herramientas, el que acepte el MCP por un adaptador mínimo; declarado), **1 réplica**,
  solo sobre H + R + 3 limpios, tope 1,8 USD (se para en el caso en que se alcance; los que falten se reportan como no medidos). Es
  el contraste de independencia (§6.1): no comparte memoria, sesión ni fabricante con quien diseñó ni con quien implementa.
- **Presupuesto por tirada:** 200 000 tokens (entrada + salida), 30 llamadas a herramientas (lecturas incluidas), 10 minutos; lo
  primero que se agote corta. AG-pre gastó 115-155 mil tokens y 14-16 llamadas; el tope deja margen sin permitir bucles de oráculo.
- **Coste total previsto del brazo AG:** (12 M + 7 H + 6 R + 3 limpios) = 28 casos × 2 réplicas = 56 tiradas × ~140 k ≈ **7,9 M
  tokens**; con repeticiones por tirada inválida (≤ 10 %) y el subestudio de fragilidad (§6.4, 6 tiradas) ≈ **9,5 M**; tope duro
  **12 M**. Cabe en el tope de Q-AG-7 (≤ 70 casos × 2 réplicas) con holgura; no se añaden casos para gastarla (§4.5).

---

## 3. La referencia sin modelo (`REF`), construida y congelada antes que el agente

Es el adversario mecánico fuerte de la lección 1. Recibe **exactamente la misma carpeta** que el agente (caso, fuente, verificador.json)
y produce el mismo `respuesta.json`. Se escribe en Python, sin modelo de lenguaje ni embeddings; su único acceso externo son las tres
sondas MCP de §3.3.

### 3.1 Localizar: del hallazgo a líneas ordenadas

**Paso 1. Extraer claves del caso.** De `caso.json`:
- `campos`: los campos HL7 nombrados en `hallazgos[].hecho` (p. ej. `PID-8`, `PV1-4`, `MSH-10`) y los que aparezcan en `esperado`/
  `observado`/`que` con la forma `SEG-n(.m)`;
- `codigos`: los códigos de acuse observados y esperados cuando la clase es `acuse` (`AA`/`AE`/`AR`/`CE`, y los ERR-3 `100`-`207`);
- `propiedades`: los nombres de propiedad del canónico que difieren (de la sonda 2, §3.3) y, sin sonda, las claves de
  `evidencia.canonico` cuyo valor aparece en `observado`;
- `clase` y `subtipo` del veredicto y de cada hallazgo que cuenta.

**Paso 2. Expandir cada clave en términos de búsqueda** con una tabla **fija y genérica**, escrita aquí a ciegas (el implementador solo
puede añadir filas motivadas por M, cada una declarada DV-AG; ninguna fila puede ser un nombre de método de un solo fichero, un
número de línea ni un texto de diff):

| Clave | Términos (todos cuentan igual dentro de la fila) |
|---|---|
| `SEG-n` | `SEG-n`, `SEG:n`, `'SEG-n'`, `SEG:n(`, `SEG-n.`, `SEG:n.`, `, n)` solo si va tras `'SEG-n'` en la misma línea (patrón Mirth `C(seg, 'SEG-n', n)`), y el nombre canónico del campo por la tabla de abajo |
| nombre canónico | `PID-3`→`Identifier|Identificador|MRN|PID3`; `PID-5`→`FamilyName|GivenName|Apellidos|Nombre|Nombres|RepeticionNombre|XPN`; `PID-7`→`BirthDate|Fecha|FechaFhir|TS|DTM`; `PID-8`→`Gender|Sexo|0001|AdministrativeGender`; `PID-11`→`Direccion|Address|XAD`; `PID-13/14`→`Telecom|XTN`; `PV1-2`→`Clase|class|0004|TieneVisita`; `PV1-3/6/11`→`Localizacion|Location|PL`; `PV1-4`→`TipoAdmision`; `PV1-7/8/17`→`Participante|Practitioner|XCN`; `PV1-10`→`Servicio`; `PV1-14`→`OrigenIngreso`; `PV1-19`→`VisitaId|visit`; `PV1-36`→`DisposicionAlta`; `PV1-44/45`→`Inicio|Fin|Estado|status|period`; `MSH-10`→`MsgControlId|ControlId|MSA-2|Ctrl|SINID`; `MSH-11`→`ProcessingId|0103|Proceso`; `MSH-12`→`Version|0104`; `MSH-18`→`CharEncoding|Juego|0211`; `MSH-9`→`MsgType|MsgEvent|DocType|0003|0076`; `OBR-n`→`Informe|DiagnosticReport|OBR`; `OBX-2`→`ValorTipo|0125`; `OBX-5`→`Valor|value`; `OBX-11`→`EstadoResultado|0085`; `OBX-14`→`effective|OBX-14`; `EVN-n`→`EVN|evento` |
| código de acuse `c` | la cadena `"c"` entre comillas (`"101"`, `"AR"`), `'c'`, y para ERR-3 el texto de la 0357 (sonda 3: p. ej. `Segment sequence error`) |
| `clase=acuse` | `MSA`, `ERR`, `Ack`, `Construir`, `MotivoRechazo|Motivo|Rechazo|fin(|codigo|postproc` |
| `clase=fidelidad`, subtipo `guardado|transformado` | `Set target.`, `cab.`, `Transform`, `Util`, `GetValueAt`, `labComps|labCampo|T(` |
| `clase=fidelidad`, subtipo `almacen|duplicado|ausente` | `Bundle|entry|request|PUT|POST|ifNoneExist|UrlCondicional|identifier|system` |
| `clase=estructura` o código `100` | `Estructura|Validate|SegCount|GetSegmentAt|orden|pos[` |
| `clase=entorno` o código `207|206|205` | `StatusCode|tCodigo|HTTP|Adapter|destino|responseStatus` |
| escapes (`\S\`, `\T\`, `\E\`, `\R\`, `\F\` en observado) | `Desescapar|Escapar|labTexto|T(|\\S\\|\\T\\|escape` |
| nulo `""` en observado | `""|crudo|nulo|null` |
| longitud / truncado | `MAXLEN|$extract|substring|Truncado|longitud|LEN|trunc` |
| repetición | `MAXREP|repetic|Rep(|~|GetValueAt(".*(\"_i` |

**Paso 3. Prior por etapa.** Cada fichero recibe un factor según la clase del veredicto, por su **papel** (deducido del nombre, no
de su contenido): `Transform|Util|Msg|paso_2` ×1,5 para fidelidad/guardado y transformado; `Ack|Rechazo|Acuse|paso_1|postproc` ×1,5
para acuse; `Operation|Fhir|paso_3|destino` ×1,5 para almacén y entorno; `Estructura|Cabecera|paso_1` ×1,5 para estructura;
`Production|Rule|ajustes` ×1,0 siempre; `Test` **×0 (excluido)**; el resto ×1,0.

**Paso 4. Puntuar líneas.** Para cada línea de cada fichero de `fuente/`: `puntos = Σ_filas (peso_fila × hay_término)` con
peso 3 para campos, 2 para nombres canónicos y propiedades, 2 para códigos de acuse, 1 para los términos de clase; una línea que es
solo comentario (`///`, `//`, `<annotation>`, `/* */`, `#`) se multiplica por 0,5; se multiplica por el prior del fichero; se suaviza
con ±2 líneas al 50 %. Empates: por orden de fichero y número de línea (determinista).

**Paso 5. Top-3 por unidad.** Se toman las líneas de mayor puntuación de **tres unidades distintas** (§4.1): la mejor línea de la
mejor unidad, luego la mejor de la segunda, luego de la tercera. Si menos de tres líneas superan el umbral mínimo (puntos ≥ 2),
se devuelven las que lo superan (puede ser `localizacion: []`).

**Caso limpio:** si `veredicto.categoria = correcto` o no hay hallazgo que cuente, `hay_fallo: false` y nada más (es la única regla
que mira la categoría para callarse; es lo que haría cualquier script razonable).

### 3.2 «Parchear» mecánico: tres plantillas y, si no, nada

Se aplica sobre la línea top-1 (y solo sobre ella) cuando su forma casa con una plantilla; si no casa, `parche: null`. Declaro de
entrada que esto es débil: la frase «hace falta» para el parche se contesta contra esto **y** contra `VACIO` (L-AG-2).

| Plantilla | Condición | Sustitución |
|---|---|---|
| **T1 código de acuse** | clase `acuse`, hay un código observado `Y` y uno esperado `X` (de los hallazgos o de la sonda 1), y la línea top-1 contiene la cadena literal `"Y"` o `'Y'` exactamente una vez en el fichero | `"Y"` → `"X"` en esa línea (misma regla para MSA-1 `AR`↔`AE` cuando difieren) |
| **T2 parámetro numérico** | la línea top-1 es `Parameter NOMBRE = n;` (IRIS) o `var NOMBRE = n;` (JS) y el hallazgo habla de repetición o longitud con un número `k` en `esperado`/`citas` | `n` → `max(n, k)`; si no hay `k`, sin parche |
| **T3 envolver con el normalizador que ya existe** | fidelidad con escape o nulo en `observado`, la línea top-1 es una asignación `Set target.P = expr` / `cab.P = expr` y en el árbol existe exactamente un método/función con nombre que case `Desescapar|labTexto|^T$` | `expr` → `##class(Clase).Metodo(expr)` o `T(expr)` |

Restricciones iguales a las del agente (6 cambios, 3 ficheros, nada de puertos ni credenciales). Ninguna plantilla «sabe» nada de un
caso concreto.

### 3.3 Las tres sondas fijas al juez (para igualar el punto 3)

En este orden, con las herramientas tal cual las usa el agente, y **solo una vez cada una**:

1. `acuse_esperado(mensaje, pe)` → el ACK esperado; se compara con el ACK observado y de ahí salen `codigos` (observado, esperado).
2. `comparar_canonico(mensaje, canonico_observado, pe)` (solo si hay canónico en la evidencia y el punto de entrada tiene mapeador)
   → las propiedades que difieren; de ahí `propiedades`.
3. `consultar_tabla("0357", codigo_esperado)` → el texto del código, que entra como término.

Si una sonda devuelve `isError`, se sigue sin ella (se registra). Tres llamadas frente a hasta 30 del agente: la diferencia es la
capacidad que se quiere medir, y queda escrita.

### 3.4 Lo que la referencia no hace, a propósito

No lee la clave ni ningún fichero fuera de la carpeta (control 2); no cambia de reglas entre casos; no usa el nombre de la carpeta; no
mira si el caso es H, R o M. Sus reglas se escriben mirando **M y las descripciones públicas de R**; nunca los diffs de H. La lección 1
permite afinarla con datos porque subir la barra del adversario solo puede causar un falso negativo para el agente; aun así, afinarla
sobre H sería memorizar la clave, no buscar (Q-AG-16).

### 3.5 Los tres controles de la referencia (antes de congelar; resultados en el sello)

1. **Clave barajada.** Se emparejan los `caso.json` de los casos con las carpetas `fuente/` de otros casos (permutación sembrada sin
   puntos fijos, dentro del mismo motor). La tasa de acierto top-3 por unidad debe caer a **≤ azar + 0,10**, donde azar =
   3 / (número de unidades del árbol). Si no cae, hay una fuga (p. ej. una regla que acierta por el nombre del fichero más probable) y
   se corrige antes de congelar.
2. **Columnas que lee.** Se ejecuta con un gancho sobre `open()` y sobre el cliente MCP: el registro debe contener solo ficheros bajo
   la carpeta de la tirada y solo las tres sondas. Se publica el registro de una tirada de ejemplo.
3. **Casos limpios y calibración con M.** Sobre los 3 limpios: 0 falsas alarmas. Sobre los 12 M: localiza en top-3 por unidad
   **≥ 9 de 12** (es la barra para considerarla adversario fuerte). Si da < 9, se refuerza (tabla de §3.1, pesos) en **como máximo
   dos iteraciones**, cada una registrada; después se congela esté donde esté, y su resultado en M se publica como su fuerza medida.

---

## 4. La métrica y la regla de decisión, preinscritas

### 4.1 Localización

**Unidad.** Para `.cls`: el bloque `Method`, `ClassMethod`, `Property`, `Parameter`, `Query` o `XData` que contiene la línea (de su
cabecera al `}` que lo cierra a columna 0; para `XData` con DTL, cada `<assign>` o `<code>` es una unidad propia; las líneas fuera de
todo bloque forman la unidad «cabecera de clase»). Para `.js` de Mirth: la `function` de nivel superior que contiene la línea; en
scripts planos, ventanas fijas de 15 líneas alineadas al inicio del fichero. Para `.properties` y `Production.cls` sin métodos: cada
`<Item>` o cada clave es una unidad. El extractor de unidades forma parte del arnés congelado y se prueba sobre los 12 M (la línea del
mutante cae en la unidad que se espera).

**Acierto top-k.** `LOC3 = 1` si alguna de las (hasta) tres líneas propuestas cae en una unidad de la verdad; `LOC1` lo mismo con la
primera. Tres líneas en la misma unidad cuentan como una. **Secundario**: `LOC3-línea` (la línea propuesta está a ≤ 3 líneas de una
línea de la verdad) y, para parches multisitio, `cobertura = |unidades de la verdad tocadas por el top-3| / |unidades de la verdad|`.

**Verdad por corpus:**
- **H:** las unidades de los hunks del diff (§1.2). Multisitio: `LOC3` es «alguna» (primario), `cobertura` secundario.
- **R (adjudicación preinscrita):** la zona sellada en AG1 (§1.3). Tras AG2, la verdad se **amplía** con las unidades tocadas por
  cualquier parche **aceptado** (§4.2) de cualquier brazo, porque un parche que el juez acepta sin colateral demuestra que esa unidad
  es una causa; se reporta R con las dos verdades (sellada / ampliada) y la primaria es la **ampliada**. Ninguna unidad se quita de la
  zona sellada.
- **M:** la línea del mutante.

**Chance:** 3 / unidades del árbol (≈ 0,05-0,08 según circuito); se reporta junto a cada tasa.

### 4.2 Arreglo aceptado

`FIX = 1` si y solo si: el parche **aplica** (cada `viejo` casa una vez; ≤ 6 cambios, ≤ 3 ficheros; no toca `Port`, `Credentials`,
`SSLConfig`, direcciones ni rutas de FHIR del `Production`/`ajustes`; si lo hace, «no aplica»), **compila** (IRIS) o despliega (Mirth),
da `correcto` en el **100 %** de los disparadores y **0 colateral** en la regresión (ningún mensaje `correcto` deja de serlo; se
compara la categoría, no la firma: un cambio de firma con veredicto `correcto` no es colateral). Secundarios: `FIX-parcial`
(fracción de disparadores arreglados), `colateral` (número), `no_aplica`/`no_compila` (recuentos por brazo).

Controles del evaluador por caso, medidos en AG1 (§1.2 puertas): `VACIO` → 0 arreglados; `FIX` (solo H) → 100 % y 0 colateral.
Control de **discriminación negativa**: por cada caja, un parche deliberadamente inofensivo (cambiar un comentario) y otro
deliberadamente dañino (devolver siempre `AR 207` en la operación) → 0 arreglados el primero, colateral > 0 el segundo. Si un evaluador
no separa los cuatro, no se mide con él (lección 7).

### 4.3 Agregación por caso y por brazo

- Por caso y brazo AG: `LOC3 = media de las 2 réplicas` (0, 0,5, 1); igual `FIX`. Sensibilidad: «alguna réplica» y «las dos».
- `REF` es determinista: 1 tirada. `DS`: 1 tirada.
- Por brazo: tasa = media de los casos que cuentan (H + R, n ≈ 13), con intervalo de Wilson al 95 % calculado sobre la suma de medias
  (para AG se reporta además el intervalo con «alguna» y «las dos», que son binarios).
- M y limpios se reportan aparte, nunca mezclados con H + R.

### 4.4 Coste

Por tirada: tokens de entrada y salida, llamadas por herramienta (MCP y lectura), minutos de reloj, y si acabó por presupuesto. Por
brazo: medias y máximos; coste de `REF` = 3 llamadas MCP y segundos. Se reporta el **coste por arreglo aceptado** (tokens / FIX).

### 4.5 Tratamiento estadístico con n pequeño y las dos frases

n que cuenta ≈ 13 (7 H + 6 R) si todos pasan las puertas; mínimo para reportar las frases: **10**. Comparaciones **apareadas** por
caso (mismo caso, dos brazos).

**Frase 1, «el agente funciona» (absoluta, sobre H + R):**
- Localiza: `LOC3(AG)` con límite inferior de Wilson 95 % **> 0,33**, y además `LOC3(AG)` en M ≥ 0,75 (si en M no llega a 0,75,
  «no funciona ni con firma»: se dice así).
- Arregla: `FIX(AG)` con límite inferior de Wilson 95 % **> 0,20** y `colateral` medio por tirada < 1.
- Se dice «funciona» si se cumplen las dos; «funciona para localizar, no para arreglar» (o al revés) si una; «no funciona» si ninguna.

**Frase 2, «el agente hace falta» (relativa, AG frente a REF, sobre H + R):**
- Estadístico: diferencia apareada media `Δ = mean(LOC3_AG − LOC3_REF)` y su intervalo por bootstrap sobre casos (10 000 remuestreos,
  percentil, semilla fija); y el test exacto de McNemar sobre los pares discordantes usando «alguna réplica» (binario), dos colas.
- **Aporta** si `Δ ≥ +0,20` (≥ 2-3 casos de 13) **y** `p_McNemar < 0,10`.
- **No aporta** si `Δ ≤ +0,10` **o** el intervalo de `Δ` contiene 0 y `Δ < 0,20`.
- En medio: **«indeterminado: n insuficiente para la diferencia observada»**, que es un resultado válido y **no** dispara añadir casos
  en este piloto (sería mirar los datos para decidir n).
- Lo mismo, por separado, para `FIX` (frente a `REF` y frente a `VACIO`; con `VACIO`, «aporta» exige `FIX(AG) ≥ 0,30`).
- Multiplicidad declarada: dos resultados (LOC3, FIX) × una comparación primaria (AG vs REF) sobre un corpus (H + R). **Primario:
  LOC3 en H + R.** Todo lo demás es secundario y se lee como descriptivo, sin corrección (lección 2).
- Sensibilidades preinscritas: (i) R con la verdad sellada en vez de la ampliada; (ii) solo H; (iii) quitando los casos de R con
  pista textual en `verificador.json` (§6.2); (iv) `DS` frente a `REF` con el mismo criterio (1 réplica, descriptivo); (v) «las dos
  réplicas» en vez de la media.

**Las dos frases juntas, formato fijo del informe de AG3:**

> «El agente **{funciona | funciona para localizar | funciona para arreglar | no funciona}**: localiza top-3 en {k}/{n} casos reales
> (IC95 {a}-{b}; azar {c}) y arregla sin colateral {k'}/{n} (IC95 {a'}-{b'}). El agente **{aporta | no aporta | indeterminado}** frente
> a la búsqueda sin modelo: Δ localización {Δ} (IC {…}; McNemar p = {p}), Δ arreglo {Δ'}; la referencia sola localiza {k''}/{n} y
> arregla {k'''}/{n}. Coste: {t} tokens por caso, {t/FIX} por arreglo aceptado.»

---

## 5. El plan AG1-AG4 con la regla de parada de cada fase, en números

| Fase | Qué se hace | Regla de parada / pasa (escrita antes; en el sello) |
|---|---|---|
| **AG1** Sellado + referencia (≈ 1,5 sesiones) | Exportador (§1.1); cajas `LABADTMUT` y `LABORUMUT` (Q-AG-8); H: tres puertas por caso; R: disparadores y zona preinscrita; M: 12 cajas y casos mostrados; 3 limpios; `verificador.json` recortado; MCP reconectado con el enum nuevo; evaluador con sus 4 controles por caja; referencia escrita y sus 3 controles; consigna, presupuesto y guion de análisis; `SELLO-AG1.md` commiteado | **Pasa** si: H que cuentan ≥ **5**; R que cuentan ≥ **5**; H + R ≥ **10**; M con caso mostrado = **12**; limpios = **3**; evaluador separa los 4 controles en **todas** las cajas; MCP lista `adt_fhir` y `oru_fhir`; referencia: clave barajada ≤ azar + 0,10, registro de lectura limpio, 0 falsas alarmas, M ≥ 9/12 (o 2 iteraciones hechas y resultado publicado); AG-pre repetido con la cadena nueva: R5 y H-MI-1 dan los números de AG-pre (5/5 y 11/11, colateral 0). **Para** (y se escribe por qué) si H + R < 10 tras una sesión y media: se reporta el piloto como «no medible con este corpus» con lo que haya |
| **AG2** Tiradas (≈ 1 sesión, en segundo plano con `systemd-run --user`, en primer plano lo que llame fuera) | Orden: `REF` sobre los 31 casos (determinista, barato) → `AG` 2 réplicas × 31 en orden sembrado (semilla `AG2|<sello>`), intercalando corpus → `DS` 1 × (H + R + limpios) hasta 1,8 USD → evaluación de cada parche en su caja con restauración (§1.5) → subestudio de fragilidad (§6.4). Cada tirada: transcripción, auditoría, `respuesta.json`, evaluación, coste, todo en `privado/agente/ag2/<opaco>/` | **Para** si: el agente, en los **primeros 6 M** por orden sembrado, localiza top-3 en **< 3** (no encuentra ni firmas: se va a AG3 con eso); tiradas inválidas (auditoría) ≥ **3** (se arregla la caja, DV-AG, y se reanuda; si vuelve a pasar, se para); tokens del brazo AG ≥ **12 M**; DeepSeek ≥ 1,8 USD (solo ese brazo); una restauración falla **dos veces** en la misma caja (se recrea la caja). Si una tirada se corta por presupuesto, no se repite: cuenta «sin respuesta» |
| **AG3** Análisis (≈ 0,3 sesión) | Adjudicación de R (ampliación con parches aceptados); tablas por caso y brazo; las dos frases con el guion de §4.5; sensibilidades; coste; amenazas con lo observado (§6); lectura manual de 3 parches aceptados por Víctor o Jev (no cambia puntuaciones; se reporta si el parche «hace trampa al juez», L-AG-3) | Se publica aunque el resultado sea «no aporta» o «indeterminado». No se añade ningún caso ni réplica tras ver los datos |
| **AG4** Cierre (≈ 0,2 sesión) | Cajas paradas o destruidas; USER, LABADT, LABORU, LABMULTI en marcha con huella; `antes_de_publicar.py` en LIMPIO; publicación del diseño, el sello, los resultados agregados y las transcripciones **sin** la clave de H ni datos de paciente; memoria: una ficha con las dos frases | `comprobar` = huella en los 4 circuitos y sonda AA en USER; guarda LIMPIO |

---

## 6. Amenazas a la validez

### 6.1 Contaminación: ¿pudo el modelo ver estos fallos?

- **Por entrenamiento:** los arreglos de H y el documento de R son de sep-oct 2026, posteriores al corte de conocimiento del modelo
  del agente (y del mío). Se declara la fecha del corte del modelo usado en el sello. Riesgo bajo; no nulo si el modelo cambia.
- **Por sesión:** el implementador conoce los arreglos de H. Mitigación: no escribe nada específico en la consigna (es fija, §2.2), el
  agente se lanza desde una carpeta sin la memoria del laboratorio (§2.1), y el brazo `DS` es el contraste: si `AG ≫ DS` **solo** en los
  casos cuyo arreglo está descrito en la memoria o en documentos del laboratorio, se sospecha fuga y se dice.
- **Por la propia caja:** el árbol «antes» de H puede contener comentarios que describan el fallo (un `TODO`, una revisión que lo
  nombró). Es una condición real (un ingeniero de guardia también los ve) y se acepta; en AG3 se lista por caso si la unidad de la
  verdad tiene un comentario que nombre el fallo, y se reporta la tasa con y sin esos casos.

### 6.2 Huellas en el corpus

- **Reconstrucción:** resuelta por el exportador único desde revisiones de git (§1.1), nombres opacos e ids de mensaje opacos (§1.7).
- **`verificador.json` lleva pistas de R.** Lo veo en la copia de esta carpeta: la decisión «V» («el límite de 10 repeticiones del
  contrato es un defecto») apunta a R4; S100 y L-MT11 rozan R6; L23 y L-MS-4 describen comportamientos del congelado. Decisión: **no se
  recorta** (es lo que el juez declara y los dos brazos lo reciben igual; recortarlo cambiaría al juez), se lista en AG1 qué casos de R
  tienen pista textual y se reporta la sensibilidad (iii) de §4.5. Las secciones `desviaciones_*` y `deudas_circuito_*` sí se quitan
  (describen implementaciones y podrían nombrar H).
- **La memoria del laboratorio** se inyecta a los subagentes (lo compruebo en mí mismo: recibí fichas como «ImportFromString y texto no
  ASCII», que describe un fallo real de un circuito). Mitigación en §2.1; límite L-AG-5.
- **Mutantes con estilo raro:** M es control; aun así el exportador exige sangría idéntica (§1.1).

### 6.3 El agente que usa al juez como oráculo

Permitido y contado (§2.4); la referencia tiene sus tres sondas (§3.3). Lo que puede pasar y cómo se lee: si el agente acierta más
**porque sondea**, es una capacidad real del agente con juez, que es lo que el piloto pregunta; para separarlo, el subestudio de §6.4
(b) corre 6 M con el MCP limitado a 3 llamadas. Lo que no puede hacer ningún brazo: ejecutar el circuito parcheado. Riesgo residual: un
parche que haga emitir lo que el juez espera sin arreglar la causa (L-AG-3); lo ve la regresión y la lectura manual de AG3.

### 6.4 Fragilidad de la consigna

Una sola consigna preinscrita; nada se afina tras la primera tirada. **Subestudio de fragilidad (solo M, 6 tiradas, 1 réplica):** (a)
3 M con una segunda redacción de la consigna (misma información, otro orden y otras palabras, escrita en AG1 y sellada); (b) 3 M con
el MCP limitado a 3 llamadas. Si (a) cambia ≥ 2 de 3 aciertos, el efecto es frágil y se dice en la frase 1; si (b) baja ≥ 2 de 3, el
agente depende del oráculo y se dice en la frase 2.

### 6.5 Un evaluador que no discrimina

Cuatro controles por caja (§4.2): vacío, arreglo de referencia (H) o parche de AG-pre (R5), inofensivo, dañino. Más: cada evaluación
registra de qué evidencia salió cada veredicto (lección 7): id opaco del mensaje, puerto y caja a la que se envió, firma del ACK y
hash del canónico; una evaluación cuyo registro no case con la caja prevista se descarta y repite.

### 6.6 El coste (punto 5)

≈ 9,5 M tokens del brazo AG (tope 12 M), ≤ 1,8 USD DeepSeek, y unas 5-6 horas de caja (≈ 90 evaluaciones × 3-4 min) en segundo
plano. La reducción respecto a los 20 M que extrapolaba AG-pre viene de no correr los ~50 mutantes (12 bastan para calibrar) y de
medir `VACIO`/`FIX` una vez por caso en AG1, no por tirada.

### 6.7 Otras

- **El implementador conoce H y escribe la referencia:** controles 1-3 de §3.5 y la regla de que sus filas sean genéricas; la tabla
  inicial la escribo yo a ciegas (§3.1).
- **n pequeño:** la regla de §4.5 tiene un tercer resultado («indeterminado») para no forzar una frase.
- **Un solo motor cuenta de verdad:** Mirth no tiene H que cuente; las frases hablan de circuitos IRIS (L-AG-7).

---

## 7. Preguntas para Jev (Q-AG, desde la 8) y límites declarados (L-AG)

Cada Q lleva recomendación, alternativa y qué cambia en la medida.

| Q | Pregunta | Recomendación | Alternativa | Qué cambia según la respuesta |
|---|---|---|---|---|
| **Q-AG-8** | ¿Dónde se parchean LABADT y LABORU? | Dos namespaces caja nuevos (`LABADTMUT`, `LABORUMUT`) con la receta de LABMUT (§1.1, S-AG-2) | El mecanismo de A5/MS3: cargar en el namespace de producción, restaurar y comprobar la huella | Con la alternativa, la medida es la misma pero se incumple «nada del agente toca los circuitos de producción» y un parche con `Storage` o globals pasa por la producción viva; con la recomendación, media sesión más en AG1 |
| **Q-AG-9** | ¿Puede la referencia consultar al juez? | Sí, tres sondas fijas (§3.3), y el agente sin límite dentro del presupuesto, contado | Ni la referencia ni el agente usan el MCP (solo lectura de código) | Con la alternativa se mide «lectura de código» y se pierde lo que el agente hizo en AG-pre; la frase 2 compararía capacidades distintas de las que habrá en producción |
| **Q-AG-10** | ¿Cuentan R5 y H-MI-1 (los de AG-pre)? ¿Y R1 si no se reproduce en 5/5? | No cuentan: son controles de la cadena. R1 se retira si no se reproduce en 5 de 5 | Contar R5 (sube n a 14) | Contar R5 añade un caso sobre el que se afinó el arnés y que el modelo ya resolvió: sesgo a favor del agente en una muestra de 13 |
| **Q-AG-11** | Granularidad primaria de la localización | Unidad (método/función/bloque), top-3 (§4.1) | Línea ± 3, top-1 | Por línea, un parche de ausencia (R5: «falta la comprobación») casi nunca acierta ni para la verdad de H (inserciones); por unidad la barra es más justa y el azar sigue siendo < 0,1 |
| **Q-AG-12** | Réplicas | 2 en todos los 31 casos; una 3.ª réplica **solo en H + R** si al cerrar AG2 quedan ≥ 3 M tokens del tope, decidida antes de mirar resultados (se escribe en el sello) | 3 réplicas en H + R y 1 en M desde el principio | Con 3 réplicas en H + R la media por caso toma valores {0, ⅓, ⅔, 1} y la sensibilidad «las dos/todas» se endurece; M con 1 réplica calibra peor pero es control |
| **Q-AG-13** | ¿Qué modelo es el agente y entra DeepSeek? | El mismo subagente que en AG-pre (declarado); DeepSeek 1 réplica en H + R + limpios hasta 1,8 USD como contraste de independencia | Solo Claude; o Fable como agente | Sin DS no hay contraste contra la fuga por sesión/memoria (§6.1); con Fable como agente, el diseñador y el diagnosticador son el mismo modelo (no invalida, pero se declara) |
| **Q-AG-14** | Aislamiento de la memoria del subagente | Lanzar en modo no interactivo desde una carpeta-proyecto fuera del laboratorio, herramientas restringidas, auditoría de transcripción (§2.1) | Lanzar con la herramienta `Agent` desde la sesión del laboratorio, como en AG-pre, y auditar solo | La alternativa hereda la memoria del laboratorio (vi fichas sobre fallos de circuitos en la mía): la frase 2 podría medir memoria, no diagnóstico |
| **Q-AG-15** | Umbrales de «aporta» | `Δ ≥ 0,20` y McNemar p < 0,10 (§4.5), con «indeterminado» en medio | Solo el intervalo bootstrap de Δ que excluya 0 | Con n = 13, excluir 0 por bootstrap exige ≈ 4-5 casos discordantes a favor; la recomendación acepta 3 con un p laxo declarado y deja el resto como indeterminado |
| **Q-AG-16** | ¿Con qué datos se puede afinar la referencia antes de congelar? | Solo M y las descripciones públicas de R; dos iteraciones como máximo; filas genéricas (§3.4) | También con H (la lección 1 lo permite: un adversario más fuerte solo causa falsos negativos) | Afinar con H convierte la referencia en una clave memorizada y la frase 2 deja de medir «búsqueda»; además el control de clave barajada dejaría de ser informativo |
| **Q-AG-17** | H con otros fallos vivos en su revisión | Excluir de la regresión los mensajes no `correcto` con los dos árboles (§1.2) y mantener el caso | Retirar el caso | Retirar baja n; excluir mantiene n y declara qué mensajes no se juzgan en ese caso |

**Límites declarados de entrada (L-AG):**

- **L-AG-1.** n ≈ 13 casos reales: el piloto no detecta diferencias < 0,20 y una frase 2 «indeterminado» es probable; se asume.
- **L-AG-2.** El «parchear» de la referencia son tres plantillas: la frase 2 para el arreglo es, en la práctica, «el agente frente a
  nada»; se contesta igual y se dice así.
- **L-AG-3.** El juez es la verdad por decisión (Q-AG-2): un parche que satisface al juez sin arreglar la causa cuenta como aceptado; la
  regresión y la lectura manual de tres parches lo acotan, no lo eliminan.
- **L-AG-4.** `verificador.json` lleva pistas textuales de algunos R (§6.2); se reciben por igual y se mide la sensibilidad.
- **L-AG-5.** No puedo verificar desde fuera qué contexto inyecta la herramienta al subagente (memoria, `CLAUDE.md` global); solo lo
  acoto con el lanzamiento desde otra carpeta-proyecto y con el contraste DS.
- **L-AG-6.** La verdad de localización de R es post-hoc en parte (ampliada con parches aceptados); se reporta también con la zona
  sellada.
- **L-AG-7.** Mirth no tiene H que cuente; MI3 solo como control: las frases hablan de circuitos IRIS.
- **L-AG-8.** Dos réplicas estiman mal la variabilidad del agente; se reportan las tres lecturas (media, alguna, las dos).
- **L-AG-9.** `correcto` en disparadores construidos de R no prueba el arreglo en tráfico real; prueba que el juez lo acepta.
- **L-AG-10.** Los disparadores y la regresión de H se miden con el verificador de hoy, no con el de la fecha del arreglo: un H que el
  juez de hoy no ve se retira y se declara (§1.2 puerta 1).
- **L-AG-11.** La evidencia de un solo mensaje por caso: un fallo que solo se entiende con varios mensajes (secuencias, reenvíos) queda
  en desventaja para los dos brazos; `otros_casos_que_fallan` es un número, no evidencia.
- **L-AG-12.** El presupuesto por tirada (200 k tokens, 30 llamadas, 10 min) es una decisión de diseño y acota lo que el agente puede
  hacer; se reporta cuántas tiradas lo agotan.

---

## Resumen de decisiones propuestas (S-AG)

| S-AG | Decisión |
|---|---|
| S-AG-1 | Un exportador único desde revisiones de git para H, R y M; sangría idéntica en mutantes |
| S-AG-2 | Cajas de IRIS como namespaces aparte (`LABMUT`, `LABADTMUT`, `LABORUMUT`); Mirth efímero |
| S-AG-3 | MCP del agente con cinco herramientas, sin `info_verificador`; copia recortada en la caja; derrame dentro de la caja |
| S-AG-4 | Tres capas contra la fuga: lanzamiento cerrado, auditoría de transcripción, clave fuera de alcance |
| S-AG-5 | El juez como oráculo se permite, se cuenta y se iguala con tres sondas fijas en la referencia |
| S-AG-6 | Corpus: 7 H (plantilla con tres puertas), 6 R que cuentan + R5 control, 12 M por decisión, 3 limpios |
| S-AG-7 | Localización por unidad, top-3 primario; R con zona sellada y ampliación por parches aceptados |
| S-AG-8 | Arreglo aceptado = aplica + compila + 100 % disparadores + 0 colateral; cuatro controles del evaluador por caja |
| S-AG-9 | Dos frases con reglas numéricas, tercer resultado «indeterminado», sin añadir casos tras ver datos |
| S-AG-10 | Presupuesto por tirada 200 k / 30 llamadas / 10 min; tope del brazo AG 12 M tokens; DS ≤ 1,8 USD |
