<!-- Modelo: Claude Fable 5.1 (claude-fable-5-1). Fecha: 13-oct-2026. BU0: diseño del estudio «agente con bucle de prueba»; a ciegas de los resultados por caso del piloto y de la ampliación; leído solo scratchpad/bucle -->

# Diseño del estudio «agente con bucle de prueba» (BU0, 13-oct-2026)

Referencia contra la que se medirá el estudio. Lo implementa otro (Claude), que declara cada desviación como DV-BU-n y fija
en git la regla de decisión y las de parada **antes** de medir. Etiquetas: S-BU (decisión propuesta), Q-BU (pregunta: a Jev
las de diseño, a Víctor las de alcance), L-BU (límite declarado de entrada), DV-BU (reservada a la implementación). Todo lo
que este diseño no nombra queda **como en el piloto y la ampliación** (`piloto/piloto-agente/agente/diseno-agente-fable.md`,
en adelante D-AG; `.../amp/diseno-ampliacion-fable.md`, D-AMP; y sus sellos).

Lo que el ANTES da por fijado (13-oct): **un solo factor**, la herramienta `probar_parche`; las demás mejoras (más casos del
mismo fallo, texto del juez enriquecido, «decisión declarada», esquemas cargados desde el principio) quedan fuera; el corpus
son los 18 casos reales de las dos etapas más los limpios; la medida primaria es **FIX, apareada por caso**; el presupuesto por
tirada no se cambia para que el bucle quepa; el código del modelo corre solo en la caja; tope 1,5 sesiones.

Lo que BU-pre obliga: el bucle cabe (≤ 36 s por prueba con la caja arrancada en LABADTMUT y LABMULTIMUT, 8-11 s en
LABORUMUT); lo caro es medir, no compilar; con la caja arrancada caben 3-4 pruebas en una tirada de 10 minutos; el precio es que
el circuito congelado (USER) queda parado mientras la tirada está abierta. **BU-pre no midió LABMUT** (6 de los 18 casos) ni
ningún caso con entorno inyectado (R1, R3): §3.3 lo convierte en puerta de BU1.

---

## 0. La pregunta y la hipótesis, en una frase cada una

> **Pregunta:** si el agente de hoy puede aplicar su parche en la caja, compilarlo y leer el veredicto del juez sobre unos
> pocos mensajes de prueba, ¿**arregla más casos** (FIX) sin que su ventaja venga de contentar al juez en lo que ve?

> **Hipótesis (del ANTES):** sí, porque los parches rechazados de hoy son sobre todo arreglos a medias (arregla el mensaje que
> ve y no los demás que fallan por la misma causa) y, en un caso, un error de sintaxis que una carga habría cazado.

**Previsión escrita antes de medir (L-BU-1):** el agente de hoy arregla 8,5 de 18. De los 9,5 restantes, al menos tres son
casi seguro inalcanzables para cualquier parche (R-ADT-8, cuya previsión sellada es «localiza, no arregla»; R-MT4 con los
controles C0, «casi seguro FIX = 0»; R1, que depende de un tiempo de espera). El techo realista del bucle son unos 6 casos, y
la hipótesis apunta a 3-4 (los arreglos a medias). Con la regla de §4.3, eso cae **en la frontera entre «aporta» e
«indeterminado»**: «indeterminado» es el resultado más probable y es válido.

Vocabulario nuevo:

| Término | Significado |
|---|---|
| **prueba** | Una llamada a `probar_parche` que llega a cargar la caja: aplica el parche sobre el árbol base, compila, arranca y envía el **conjunto de prueba** |
| **conjunto de prueba** (`D_v`, `R_v`) | Los disparadores y mensajes de regresión que el agente puede probar: `D_v` = el caso mostrado y hasta 2 más; `R_v` = 5 de la regresión. Sellados por caso |
| **conjunto oculto** (`D_h`, `R_h`) | El resto de disparadores y de la regresión sellados. Nunca pasan por la herramienta |
| **FIX** | Como en D-AG §4.2: aplica + compila + `correcto` en el 100 % de **todos** los disparadores (`D_v ∪ D_h`) + 0 colateral en **toda** la regresión (`R_v ∪ R_h`). Es la misma medida que la de hoy, con los mismos conjuntos |
| **FIX_visible** | `correcto` en el 100 % de `D_v` y 0 colateral en `R_v`: lo que el agente puede ver por sí mismo |
| **sobreajuste** | `FIX_visible = 1` y `FIX = 0`: el parche contenta a lo que ve y falla en lo que no ve. Es la firma de «adaptarse al juez» |
| **brazo AG₀** | El agente de hoy **ya medido** (piloto 12-oct + ampliación 13-oct): sus FIX por caso están fijos y no se remiden |
| **brazo AG₁** | El agente de hoy **remedido** en BU2, en las mismas condiciones y días que BU (§4.1) |
| **brazo BU** | El agente de hoy con `probar_parche` y la consigna de §1.7; nada más cambia |
| **tirada abierta** | El intervalo entre «abrir la caja» y «cerrarla» (§1.4): la caja del circuito está arrancada y las demás producciones, USER incluida, paradas |

---

## 1. La herramienta `probar_parche`

### 1.1 Qué recibe y qué devuelve (S-BU-1)

**Recibe** exactamente el `parche` del esquema de `respuesta.json`: `{"cambios": [{"fichero", "viejo", "nuevo"}]}`. Ningún
otro parámetro: ni qué mensajes, ni qué caja, ni cuántos. La caja y los mensajes los fija el arnés al abrir la tirada (§1.4);
el agente no puede elegirlos. `cambios: []` se admite (es «probar el árbol tal cual», Q-BU-7).

**Devuelve** un JSON con esta forma, y solo esta:

```json
{
 "prueba": 2, "quedan": 2,
 "aplica": true, "compila": true,
 "disparadores": {"arreglados": 2, "de": 3, "por_mensaje": [
   {"id": "m-3f2a", "mostrado": true, "veredicto": {"categoria": "correcto", "subtipo": null}, "hallazgos": []},
   {"id": "m-91c0", "mostrado": false, "veredicto": {"categoria": "acuse_incorrecto", "subtipo": "codigo"},
    "hallazgos": [{"clase": "acuse", "subtipo": "codigo", "que": "…", "esperado": "AE 100", "observado": "AR 101", "certeza": "literal"}]},
   {"id": "m-c07d", "mostrado": false, "veredicto": {"categoria": "correcto", "subtipo": null}, "hallazgos": []}]},
 "regresion": {"siguen_correcto": 5, "de": 5, "por_mensaje": [
   {"id": "m-0a11", "veredicto": {"categoria": "correcto", "subtipo": null}, "hallazgos": []}, "…"]},
 "segundos": 34.1
}
```

- **Veredicto completo, por mensaje, sin evidencia.** Por cada mensaje del conjunto de prueba: `veredicto` (categoría y
  subtipo) y los `hallazgos` que cuentan (`cuenta: true`) con `clase`, `subtipo`, `que`, `esperado`, `observado` y `certeza`:
  los mismos campos que el agente ya ve en `caso.json` para el caso mostrado. **Sin** `evidencia` (ni mensaje, ni ACK, ni log,
  ni recorrido, ni canónico, ni almacén), sin `citas`, sin `hechos_de_tabla`, sin `entrada`. El caso mostrado lleva
  `mostrado: true`; los demás ids son opacos (`sha256("BU1|" + id + "|" + opaco)[:4]`, prefijo `m-`), estables dentro de la
  tirada.
- **Por qué este nivel y no otro (Q-BU-2).** Solo la categoría (1 bit por mensaje) impediría diagnosticar por qué un arreglo a
  medias sigue fallando en los otros dos disparadores, que es justo lo que la hipótesis dice que falta; la evidencia completa
  de los tres disparadores sería «enseñar más casos del mismo fallo», que el ANTES deja fuera. El hallazgo (campo, esperado,
  observado) es el mínimo que distingue «misma causa, no cerrada» de «arreglado», y es lo que un ingeniero lee en la salida de
  un test: qué aserto falló, no el volcado entero.
- **Agregados** (`arreglados/de`, `siguen_correcto/de`) además del detalle, para que el agente no tenga que contar.
- **`segundos`**: lo que tardó; el agente sabe cuánto le queda de reloj.

### 1.2 Contra qué mensajes prueba (S-BU-2)

Contra el **conjunto de prueba** sellado del caso (§2.1): `|D_v|` = 3 si el caso tiene ≥ 6 disparadores, 2 si tiene 5
(ninguno tiene menos: puerta «falla antes ≥ 5» de AG1/AMP1); `|R_v|` = 5 siempre. En un caso limpio `D_v` = {el caso
mostrado} (veredicto `correcto`) y `R_v` = 5. Los mismos mensajes en todas las pruebas de todas las tiradas y réplicas del
caso: el agente no puede pedir otros.

Los casos con entorno inyectado (R1: puerto FHIR cerrado; R3/R3b: credencial o ruta inválidas, DV-AG-3) se prueban como los
evalúa hoy `ag1_eval`: dos cargas por prueba, una con el entorno para `D_v` y otra sin él para `R_v`. Cuesta ~3 s más; su
latencia real la mide BU1 (§3.3).

### 1.3 Cuántas veces (S-BU-3)

**4 pruebas por tirada.** Una prueba es una llamada que llega a **cargar la caja**: aplica y compila (con o sin error). Una
llamada cuyo parche **no aplica** (§1.5) no carga nada y **no gasta prueba**, hasta un tope de 10 llamadas así por tirada
(la 11.ª devuelve error). La 5.ª prueba devuelve `{"error": "presupuesto_de_pruebas_agotado", "pruebas_hechas": 4}` sin tocar
la caja. Por qué 4: BU-pre dice que con la caja arrancada caben 3-4 en 10 minutos (4 × 36 s ≈ 2,4 min en la caja más lenta
medida); 4 da para «ver cómo falla» (1), «arreglar» (2), «cerrar lo que quedó» (3) y «comprobar» (4), y no da para escalar a
ciegas sobre el juez. Las llamadas a `probar_parche` cuentan dentro de las 30 llamadas y el tiempo de cada prueba dentro de
los 10 minutos de la tirada: **el presupuesto no cambia** (ANTES). Es Q-BU-6 (contar o no las que no aplican).

### 1.4 Cómo se integra con el agente aislado (S-BU-4)

Hoy el agente corre en la máquina del usuario (`claude -p`, carpeta cerrada) y el MCP del verificador en la máquina del
laboratorio, por `ssh` en stdio. La caja es una producción IRIS en esa misma máquina, y cargarla exige los privilegios con los
que hoy corre `ag2.py evaluar`. El diseño separa dos procesos:

| Pieza | Dónde | Qué hace |
|---|---|---|
| **`bu_caja.py`, el guardián de la caja** (un proceso por tirada) | Máquina del laboratorio, con los privilegios de `ag2.py evaluar` | `abrir <opaco>`: toma un **cerrojo** (`bu_caja.lock`, con el opaco y la hora), lee de la clave sellada el caso del opaco (caja, árbol base, `D_v`, `R_v`, entorno), hace `a_caja(circ)` (para las demás producciones, USER incluida; arranca la caja) y escucha en un socket local con el nombre del opaco. Por cada petición: copia el árbol base de la plantilla → `aplicar` (el de `ag1_eval`, sin cambios) → `cargar` (recarga el árbol **completo**: las clases que sobran se borran, como hoy) → rearrancar solo la caja → `medir` sobre `D_v` y `R_v` (el `medir` de `ag1_cajas`, con la limpieza del almacén por identificador que ya hace) → responde con la forma de §1.1 → registra la petición y la respuesta completas en `privado/agente/bu2/<opaco>/pruebas.jsonl`. `cerrar <opaco>`: recarga el árbol base, mide los 5 fijos y los juzga por la regla de la caja (firma en LABMUT y LABORUMUT y LABMULTIMUT; veredicto en LABADTMUT, S-AMP-8), hace `a_user()` (USER en marcha, huella del congelado, sonda AA), suelta el cerrojo y devuelve el resumen de la tirada (pruebas, segundos, restauración) |
| **`mcp_caja.py`, el cliente MCP** | Lanzado por `claude -p` por `ssh` en stdio, como `mcp_verificador.py`, con un único argumento: el opaco | Expone una sola herramienta, `probar_parche(parche)`. Reenvía la petición al socket del guardián y devuelve su respuesta tal cual. Si el guardián no está (`abrir` falló, o la tirada ya se cerró) devuelve `{"error": "caja_no_disponible"}`. No tiene privilegios ni acceso a la clave |
| **El lanzador** (`lanzar_agente.py` + un `bu2_tiradas.py` calcado de `ag2_tiradas.py`) | Máquina del usuario | Por tirada BU: `ssh … bu_caja.py abrir <opaco>` (espera a que la caja esté arrancada, ≈ 10 s) → escribe `mcp_bu_<opaco>.json` con **dos** servidores, `verificador` (idéntico al de hoy) y `caja` (`mcp_caja.py <opaco>`) → `claude -p` con `--allowedTools` = las de hoy + `mcp__caja__probar_parche` → al terminar, cortada o no, `ssh … bu_caja.py cerrar <opaco>` y **espera** a que devuelva. Por tirada AG₁: el lanzador sellado de hoy, byte a byte, con el MCP de hoy (la herramienta `caja` ni siquiera existe para ese brazo) |

Reglas que esto garantiza, y que el sello comprueba:

1. **Una producción a la vez.** `a_caja` ya para todas las demás. Además, `ag2.py evaluar` / `amp2.py evaluar` (la
   evaluación de aceptación) **se niegan a arrancar si existe `bu_caja.lock`**, y `abrir` se niega si hay una evaluación en
   curso (cerrojo simétrico `eval.lock`). Las tiradas son secuenciales; la evaluación de aceptación se hace **al final**, en
   lote, como hoy (o en las ventanas en que corren tiradas AG₁, que no usan la caja; el implementador elige, bajo los dos
   cerrojos).
2. **El agente no elige la caja ni los mensajes.** El opaco va en la configuración del MCP de la tirada, no en la llamada.
3. **La tirada cortada no deja la caja a medias.** Si `claude -p` muere a los 10 minutos en mitad de una prueba, el guardián
   termina esa prueba (≤ 90 s), la registra y `cerrar` restaura y devuelve USER. El lanzador no abre la siguiente tirada hasta
   que `cerrar` vuelve.
4. **El circuito congelado durante la tirada abierta:** USER parado desde `abrir` hasta `cerrar`: ≤ 10 min de tirada + ≤ 1,5
   min de última prueba y restauración ≈ **12 min como máximo por tirada BU**, ≈ 44 tiradas → unas 6-8 horas acumuladas de
   USER parado, repartidas (§5.2). Entre tiradas, USER vuelve a estar en marcha con huella y sonda, como hoy (no se encadena
   una caja arrancada entre tiradas aunque sea la misma: lo que se ahorra son 15 s y lo que se gana es el estado conocido).
5. **Auditoría de la transcripción**, como hoy, con una herramienta más permitida; `pruebas.jsonl` del guardián y la
   transcripción tienen que coincidir en número de pruebas (una discrepancia invalida la tirada).
6. **Nada del modelo corre fuera de la caja:** el guardián solo escribe en la caja del opaco; el cliente MCP no escribe nada.

Alternativa de implementación (no cambia la medida; si se elige es DV-BU, no Q): un solo proceso `mcp_caja.py` lanzado por
`ssh` con privilegio limitado a ese guion, que abra la caja en su arranque y la cierre al morir. Lo desaconsejo: si `claude -p`
muere, el proceso muere con la caja a medias y sin `a_user()`.

### 1.5 Qué hace con un parche que no aplica o no compila (S-BU-5)

| Situación | Qué devuelve | ¿Gasta prueba? | Qué queda en la caja |
|---|---|---|---|
| No aplica (`viejo` 0 o > 1 veces; > 6 cambios o > 3 ficheros; fichero inexistente; toca `Port`/credenciales/rutas FHIR: el `PROHIBIDO` de `ag1_eval`, sin cambios) | `{"aplica": false, "motivo": "<el motivo de ag1_eval.aplicar, literal>", "prueba": n, "quedan": q}` | No (tope 10) | Nada: no se carga |
| Aplica y no compila | `{"aplica": true, "compila": false, "error": "<las primeras 30 líneas del error del compilador>", "prueba": n, "quedan": q}` | **Sí** | El guardián recarga el árbol base antes de la siguiente prueba (cada prueba parte siempre de base + parche, nunca de la anterior) |
| Aplica, compila, la producción no arranca en 30 s | `{"aplica": true, "compila": true, "arranca": false, "error": "…"}` | Sí | Ídem |
| Error del aparato (ssh caído, caja sin socket, timeout de 120 s) | `{"error": "caja_no_disponible"}` | No | La tirada sigue; se cuenta como **incidencia de aparato** (§5.3) |

El texto del error del compilador se **depura** antes de devolverlo: se sustituyen el nombre del namespace de la caja y
cualquier ruta de disco por `<caja>`, y se pasa el escáner de fugas de AMP (§1.6). Se devuelve porque es exactamente lo que el
ANTES señala («un parche no compiló por un error de sintaxis que una carga en la caja habría cazado»): sin el texto, el agente
sabría que no compila pero no dónde.

### 1.6 Lo que la herramienta no devuelve nunca, y cómo se comprueba

Nunca: texto de ningún mensaje (ni de `D_v` ni de `R_v`), ACK, log, canónico, almacén, nombres de caja, puertos, rutas, ids de
caso, nombres de ficheros del arnés, ni nada de `D_h`/`R_h` (que el guardián ni siquiera carga en memoria durante la
tirada). En BU1 se pasa el **escáner de fugas de D-AMP §1.4.3** (las mismas expresiones: `CIR-…`, `deuda`, `DV-…`, ids de
caso, nombres de caja, MSH-10 originales, sufijos de construcción, nombre del namespace privado) sobre la salida de la
herramienta en los 6 controles de cada caja (§3.4) y en las 18 pruebas de consistencia (§3.3); durante BU2 el guardián lo
pasa sobre cada respuesta antes de devolverla y, si algo casa, lo sustituye por `<redactado>` y lo registra (DV-BU al cierre).

### 1.7 La consigna del brazo BU y la descripción de la herramienta (preinscritas)

`CONSIGNA_BU.md` = `CONSIGNA_AG1.md` sellado **con estos tres cambios y ninguno más** (el diff se sella):

1. En «Reglas», tras la línea del MCP `verificador`, se añade:
   ```
   - Puedes probar tu parche en una copia aislada del circuito con la herramienta `probar_parche` del MCP `caja`: lo aplica,
     lo compila, envía unos pocos mensajes (el de `caso.json`, hasta 2 más que hoy fallan como él y 5 que hoy pasan) y te
     devuelve el veredicto del juez por mensaje, sin la evidencia. Tienes 4 pruebas que lleguen a compilar; un parche que no
     aplica no gasta prueba. Cada prueba parte del código actual más tu parche, y el tiempo que tarda (hasta un minuto y medio)
     cuenta en tus minutos.
   ```
2. La línea «Tu arreglo lo aplicará y medirá otro, con el juez, sobre muchos mensajes, no solo este. No tienes forma de
   ejecutar el circuito.» pasa a: «Tu arreglo lo aplicará y medirá otro, con el juez, sobre **muchos más mensajes que los de
   tus pruebas**: un parche que solo contenta a los mensajes de prueba no sirve. Prueba tu parche antes de entregarlo si te
   queda presupuesto; entregar sin probar también vale.»
3. En «Qué debes entregar», al final del punto de `parche`, se añade: «Si probaste varios, entrega el que quieras: el que
   entregues es el que se mide.»

Nada más cambia: mismos campos, mismo `respuesta.json`, mismo presupuesto escrito (200 000 / 30 / 10). Lo de «entregar sin
probar también vale» hace que el factor sea «**puede** probar», no «se le obliga a probar»; es Q-BU-4. La descripción de la
herramienta en el esquema MCP (lo que `claude -p` lee al cargarla) es el texto del punto 1 sin la primera frase, y se sella.
**No se retoca después de la primera tirada.**

---

## 2. Lo que el agente prueba y lo que decide la aceptación

### 2.1 Los conjuntos, con números (S-BU-6)

Por caso, sobre los disparadores `D` y la regresión `R` **ya sellados** (AG1, AMP1; cables con su sha256):

| Conjunto | Tamaño | Cómo se eligen (en BU1, semilla `BU1|<id de caso>`, sellado) |
|---|---|---|
| `D_v` | 3 si `|D| ≥ 6`; 2 si `|D| = 5` | El caso mostrado siempre (es el primero por el orden sellado). Los demás, **uno por grupo de disparadores** por orden sembrado dentro del grupo, recorriendo los grupos en el orden sellado y saltando el del caso mostrado primero; si sobran plazas, se siguen sacando por orden sembrado del conjunto entero. Con 4 grupos (H-CAB-1), uno queda sin representar en `D_v`; se declara |
| `D_h` | `|D| − |D_v|` ≥ 2 (R1, R6: 2; los demás ≥ 5) | El resto |
| `R_v` | 5 | Por orden sembrado, con la restricción de ≥ 2 aceptados (AA `correcto`) y ≥ 1 rechazo correcto cuando la regresión los tiene (todos los casos de AMP; ninguno de los R del piloto, cuya regresión son 60 basales aceptados). Si los 5 fijos de la restauración (`reg[:5]`) cumplen la restricción, `R_v` = esos 5 |
| `R_h` | `|R| − 5` ≥ 15 (20 en los H del piloto con regresión corta; ≥ 42 en los demás) | El resto |

Por qué estratificar `D_v` por grupo (Q-BU-3): la hipótesis es que el agente arregla el mensaje que ve y no los que fallan
por la misma causa; en los casos con grupos (R3 + R3b; R-ADT-7, R-ADT-8, R-MS-3, R-MS-4 con dos; R-MT1, R-MT4 con tres;
H-CAB-1 con cuatro; R2, R4, R7 con dos recetas) la «misma causa» tiene variantes, y una prueba cuyo `D_v` las muestra es la
que puede revelar que el arreglo es parcial. Es lo que haría un ingeniero con los mensajes que tiene a mano: probar uno de cada
clase. Lo oculto de cada grupo (los demás mensajes del grupo, en `D_h`) comprueba que el arreglo no es «para ese mensaje».

### 2.2 Por qué un parche que solo contenta a los visibles no se acepta

`FIX` exige el 100 % de `D_v ∪ D_h` y 0 colateral en `R_v ∪ R_h`: **al menos la mitad de los disparadores (≥ 2, normalmente
≥ 5) y al menos el 75 % de la regresión (≥ 15, normalmente ≥ 42) nunca pasan por la herramienta.** Un parche que reconozca
los mensajes de prueba (por su MSH-10 opaco, por un valor de campo, por una longitud) o que fuerce lo que el juez espera solo en
ellos deja `D_h` fallando o `R_h` con colateral, y FIX = 0. Además:

- **`sobreajuste`** (FIX_visible = 1 ∧ FIX = 0) se cuenta por brazo y por caso y se publica. En AG₁ no puede ocurrir por
  casualidad más que por azar de muestreo (no vio `D_v`); en BU es la firma de adaptación. Se preinscribe: si BU tiene ≥ 3
  tiradas con sobreajuste **y** FIX_visible(BU) − FIX(BU) ≥ 0,15, la frase dice «el agente contenta a lo que ve».
- **Escáner de literales de prueba** (nuevo, mecánico, en BU3): para cada parche entregado, cada cadena literal de ≥ 6
  caracteres de un `nuevo` que no exista en el árbol base se busca en los cables de `D_v ∪ R_v` (MSH-10 opacos, PID-3, PID-5,
  fechas, cualquier campo). Una coincidencia marca el parche `literal_de_prueba`. Se aplica a los tres brazos (AG₀ incluido,
  donde se espera 0). Marca → se lee (abajo); no cambia la puntuación.
- **Lectura de parches aceptados (sigue, L-AG-3):** Jev clasifica (`arregla_la_causa` / `adapta_al_juez` /
  `no_se_puede_saber`) **4 parches aceptados de BU sorteados** (`sha256("BU3|<huella>|lectura")`), más **todos** los parches
  de BU con sobreajuste o con `literal_de_prueba` (aceptados o no), más **2 aceptados de AG₁** como línea base. Un
  `adapta_al_juez` en un parche **aceptado** se publica con el caso (opaco) y no se quita del FIX: la verdad es la del juez
  (L-AG-3); se dice en la frase.
- **La secuencia de pruebas de cada tirada se publica agregada:** cuántas pruebas, cuántas compilaron, FIX_visible de cada
  una, y si el parche entregado es el último probado (`entregado = último probado`: sí/no/no probó). Un brazo que entrega
  parches distintos del último probado está haciendo algo que no es «probar y entregar», y se describe.

### 2.3 Lo que decide la aceptación, exactamente como hoy

El evaluador es `ag1_eval.evaluar` **sin cambios** (misma huella que en SELLO-AMP), sobre `D` y `R` completos sellados, con la
restauración por caja de S-AMP-8 y los grupos (R3/R3b, los de AMP) como en `ag2.py`/`amp2.py evaluar`. Así FIX(BU) y FIX(AG₁)
son la misma medida que FIX(AG₀), y la comparación es apareada de verdad. Secundarios por tirada: `FIX_parcial` (sobre `D`),
**`FIX_parcial_oculto`** (sobre `D_h` solo: la ganancia en lo no visto), `colateral` (número; y `colateral_oculto` sobre
`R_h`), `FIX_visible`, `sobreajuste`, `no_aplica`, `no_compila`.

---

## 3. El corpus: los 18 casos reales y los limpios

### 3.1 Se reutilizan los 18 (S-BU-7)

| Etapa | Casos | Caja | Observaciones para BU |
|---|---|---|---|
| Piloto, H | H-ORU-1, H-ORU-2, H-ORU-4, H-ORU-5, H-ORU-6 | LABORUMUT | Prueba barata (8-11 s). Hay FIX real para los controles |
| Piloto, R | R1, R2, R3 (+R3b), R4, R6, R7 | LABMUT | **Latencia sin medir** (§3.3). R1 y R3 con entorno inyectado: dos cargas por prueba. R1 y R6 tienen 5 disparadores: `D_v` = 2 |
| Ampliación, H | H-CAB-1 | LABORUMUT | 4 grupos; `D_v` cubre 3 |
| Ampliación, R | R-ADT-7, R-ADT-8 | LABADTMUT | 35 s por prueba; R-ADT-7: un arreglo que deje de acusar hace esperar al emisor (~8 s por disparador): prueba ≈ 60 s |
| Ampliación, R | R-MS-3, R-MS-4 | LABORUMUT | Barata |
| Ampliación, R | R-MT1, R-MT4 | LABMULTIMUT | 35 s; FIX solo por acuse (L-AMP-4) |
| Limpios | L-adt, L-oru, L-mut, L-multi | las cuatro | Control negativo de los dos brazos; en BU, además, «¿prueba un parche en un caso sin fallo?» se cuenta |

**Por qué se reutilizan todos y qué implica que ya se usaran para decidir:**

- El modelo del agente no recuerda tiradas anteriores (sesiones nuevas, carpeta aislada, sin memoria: medido en AG0). Los
  árboles, cables, claves y cajas no cambian; los sellos AG1/AMP1 siguen valiendo y sus huellas se citan.
- Los 18 ya decidieron dos cosas: la ampliación (parada opcional, corregida en AMP3) y la verdad ampliada de R para
  **localizar**. Ninguna toca FIX ni los conjuntos de disparadores y regresión. Lo que sí pasó es que la **hipótesis de BU se
  formó mirando los FIX de estos 18** («arreglos a medias: 6 de 14, 3 de 14, 5 de 11»): el estudio contrasta en el mismo corpus
  una hipótesis que ese corpus sugirió. No hay corpus de reserva (D-AMP: «H se agotó»; S-AMP-9). Se declara (L-BU-2) y se
  mitiga con tres cosas: la regla se escribe antes (§4.3); el brazo de control se **remide** (§4.1), con lo que la comparación no
  depende de los valores que motivaron la hipótesis; y los casos no se eligen: entran los 18, también los que hoy ya se arreglan
  (donde el bucle no puede ganar nada y sí perder: un agente que se fía del test y entrega un parche con colateral oculto).
- **Quien implementa conoce el FIX por caso de AG₀.** La herramienta es idéntica para todos los casos (un solo código, sin
  parámetros por caso salvo los conjuntos sellados por semilla); los conjuntos se eligen por semilla, no a mano; los controles de
  §3.4 se hacen con parches escritos antes de ver nada de BU2. Igual que con la referencia del piloto, lo que la implementación
  no puede hacer es afinar nada después de la primera tirada.
- **No se añade ningún caso** (ni M, ni Mirth, ni R5): no hay fuente nueva y la regla de D-AMP sigue. R5 y H-MI-1 son controles
  de cadena (§3.4). Mirth no entra: no tiene casos que cuenten y su caja es efímera por medida (L-BU-3).

### 3.2 Lo que se mide de cada caso en BU1 (sin tiradas)

Por caso: `D_v`, `R_v` (ids y sha256 de cable), grupos cubiertos, la **latencia de una prueba** (dos pasadas con el parche
vacío) y la **consistencia**: el veredicto por mensaje de `D_v ∪ R_v` con el parche vacío tiene que coincidir con el sellado
(«falla antes» para `D_v`, `correcto` para `R_v`) en las dos pasadas. Un mensaje de `D_v`/`R_v` cuyo veredicto cambie entre las
dos pasadas se sustituye por el siguiente del mismo grupo por orden sembrado (una sola vez; se declara); si vuelve a cambiar, el
caso se retira de BU como «caja inestable para el bucle» y se declara. Un mensaje inestable en el conjunto de prueba haría que el
agente persiguiera un fantasma, y eso no mide el bucle.

### 3.3 La puerta de latencia que BU-pre dejó abierta (S-BU-8)

BU-pre midió LABORUMUT, LABADTMUT y LABMULTIMUT con un caso cada una y sin entorno. En BU1, la consistencia de §3.2 da la
latencia de los 18 (36 pasadas). Regla del ANTES aplicada por caso: **una prueba > 90 s con la caja arrancada**, en cualquiera
de las dos pasadas, retira ese caso del estudio (declarado, con su tiempo), **sin bajar `D_v` ni `R_v` para que quepa**. Si se
retiran ≥ 5 casos (quedan < 14), o cualquiera de las cuatro cajas entera, se para BU y se publica «el bucle no cabe en la caja X» (Q-BU-5:
retirar casos frente a parar todo). Previsión: LABMUT se comportará como LABADTMUT (~35 s: es el mismo tipo de circuito, con
espera de sesión y acuse); R1 es el que puede pasar de 90 s (el tiempo de espera de la operación FHIR con el puerto cerrado,
por disparador); R-ADT-7 ≈ 60 s si el parche deja de acusar.

### 3.4 Controles del aparato (BU1, en el sello)

**Por caja (4 cajas), con la herramienta tal cual la verá el agente** (misma salida, mismo escáner), sobre un caso de la caja
(LABORUMUT: H-ORU-4; LABMUT: R5 como control de cadena y R4 para VACÍO/INOCUO/DAÑINO; LABADTMUT: R-ADT-7; LABMULTIMUT: R-MT1):

| Control | Parche | Pasa si la herramienta devuelve |
|---|---|---|
| VACÍO | `cambios: []` | `aplica` y `compila` true; `arreglados = 0`; `siguen_correcto = 5`; veredictos iguales a los sellados |
| FIX | El arreglo real (H-ORU-4), el parche de AG-pre (R5), el del implementador para R-MT1 (en la clave de AMP1); en LABADTMUT, el mutante MA1 del piloto con su árbol bueno expresado como parche (la línea del mutante deshecha), como en el control de AG1 | `arreglados = |D_v|`, `siguen_correcto = 5` |
| INOCUO | Un comentario | `arreglados = 0`, `siguen_correcto = 5` |
| DAÑINO-A | La operación devuelve AR 207 donde construía el AA | `siguen_correcto < 5` (colateral visible) |
| NO COMPILA | Un `Return:(a) || (b) 1` sin paréntesis (el error real del piloto) | `compila: false` con texto del compilador no vacío y sin nombre de caja ni ruta |
| NO APLICA | Un `viejo` que aparece dos veces; otro que toca `Port` | `aplica: false` con los dos motivos; no consume prueba |

Más: **el cerrojo** (abrir con `eval.lock` presente → se niega; `evaluar` con `bu_caja.lock` presente → se niega); **la
tirada cortada** (matar `claude -p` en mitad de una prueba → `cerrar` restaura y USER vuelve con huella y sonda); **la
cadena entera** una vez de punta a punta con el agente real sobre R5 (control de AG-pre, no cuenta): el agente tiene que
llamar a `probar_parche` al menos una vez y el guardián registrar la prueba; su FIX esperado es 1 (ya lo resolvió sin bucle).
Si un control no separa, no se mide hasta explicarlo (lección 7).

---

## 4. La comparación y su regla

### 4.1 Se remide el agente de hoy (S-BU-9; Q-BU-1)

**Recomendación: sí, entero.** AG₁ = el agente de hoy, 2 réplicas × 22 casos (18 + 4 limpios), con el lanzador, la consigna, el
MCP y el presupuesto sellados byte a byte (las mismas huellas de SELLO-AMP), **entremezclado con BU en un único orden
sembrado** (`BU2|<huella>`, tiradas de los dos brazos alternadas por azar). Primario: **BU frente a AG₁**. Secundarios: BU
frente a AG₀, y **AG₁ frente a AG₀** (la deriva, que es un resultado en sí: cuánto se replica el agente de ayer hoy).

Por qué: (1) la deriva del modelo (mismo nombre, pesos o sistema distintos) y de la herramienta (`claude -p` cambia de versión
sin avisar) es real y no se puede descartar desde fuera; con AG₀ como control, cualquier diferencia podría ser «el modelo de
hoy frente al de ayer»; (2) AG₀ tiene valores por caso que **motivaron la hipótesis**: comparar contra ellos deja entrar la
regresión a la media en los casos con una réplica acertada de dos; con AG₁ los dos brazos se miden frescos; (3) el
entremezclado anula la deriva dentro de BU2 (si el proveedor cambia algo a mitad, afecta a los dos brazos por igual).
Alternativa: AG₀ como control y **6 casos** sembrados de AG₁ con 1 réplica como sonda de deriva (si en esos 6 la media de FIX
difiere de la de AG₀ en ≥ 0,34, se declara deriva y el primario pasa a ser «no comparable»). Qué cambia: la alternativa ahorra
≈ 2 M tokens y ≈ 3 h de caja, y deja el primario expuesto a la deriva y a la regresión a la media; la recomendación cuesta eso y
convierte la comparación en una medida del factor y nada más. Víctor decide (alcance: presupuesto).

### 4.2 Medida primaria y secundarias

- **Primaria: FIX en los 18, apareada por caso.** Por caso y brazo, FIX = media de las 2 réplicas (0, ½, 1). Δ = media de
  (FIX_BU − FIX_AG₁). Para los pares discordantes se usa «alguna réplica» (binario), como en el piloto: b = casos con BU = 1 y
  AG₁ = 0; c = al revés.
- **Secundarias (descriptivas, sin corrección):** FIX_parcial_oculto; colateral medio por tirada; sobreajuste; no_compila
  (previsión: BU 0, porque lo caza la prueba); `entregado = último probado`; tiradas cortadas por tiempo (previsión: BU más
  que AG₁, porque gasta reloj en pruebas); coste (tokens nuevos por tirada y por arreglo aceptado; segundos de caja por
  tirada); LOC3 (no es primaria; se reporta para ver que el bucle no empeora localizar); falsas alarmas y negaciones falsas.
- **Sensibilidades preinscritas (FIX, BU frente a AG₁):** (i) «las dos réplicas» en vez de «alguna»; (ii) sin las tiradas
  cortadas por tiempo en cualquiera de los dos brazos (apareado sobre los casos que quedan enteros); (iii) solo casos
  multigrupo (R2, R3, R4, R7, H-CAB-1, los 6 R de AMP) frente a solo monogrupo (R1, R6, los 5 H del piloto): es donde la
  hipótesis predice la ganancia; (iv) sin las deudas por decisión (R-ADT-7, R-ADT-8, R-MT1, R-MT4); (v) por caja; (vi) BU
  frente a AG₀ y AG₁ frente a AG₀; (vii) solo tiradas BU que probaron ≥ 1 vez (**no** es apareada limpia: se rotula
  «descriptiva, condicionada a usar la herramienta»).

### 4.3 La regla de decisión, en números, preinscrita

La hipótesis tiene dirección («arregla más»), un solo factor, una sola comparación primaria y una sola métrica: **no hay
multiplicidad que corregir**; la corrección que sí hace falta es la de la selección (§3.1: AG₁ remedido, regla antes).

- **Estadístico:** p exacto de McNemar **a una cola** (dirección BU > AG₁) sobre (b, c): p = P(X ≥ b | b + c, ½); IC95 de Δ
  por bootstrap sobre casos (10 000, semilla `BU3|<huella>`).
- **Aporta** si p ≤ 0,05 **y** Δ ≥ 0,20 (≥ 3,6 casos netos de 18 en medias de réplicas).
- **No aporta** si Δ ≤ 0,10, **o** el IC95 de Δ contiene 0 y Δ < 0,20.
- **Si no, «indeterminado: n insuficiente para la diferencia observada»**, y **se cierra**: no se añaden casos ni réplicas,
  no hay BU-bis (S-BU-10).
- **Daña** (se publica como frase propia) si Δ ≤ −0,10 o si colateral medio por tirada (BU) ≥ 2 × colateral (AG₁) + 0,1.

Lo que eso exige, para que se vea que la regla no es laxa (pares discordantes a favor / en contra, p a una cola):

| a favor | máximo en contra con el que aún aporta | p con ese máximo | el siguiente, que ya no |
|---|---|---|---|
| 4 | ninguno basta | 4/0 = 0,063 | — |
| 5 | 0 | 0,031 | 5/1 = 0,109 |
| 6 | 0 | 0,016 | 6/1 = 0,063 |
| 7 | 1 | 0,035 | 7/2 = 0,090 |
| 8 | 1 | 0,020 | 8/2 = 0,055 |
| 9 | 2 | 0,033 | 9/3 = 0,073 |
| 10 | 3 | 0,046 | 10/4 = 0,090 |

En palabras: **aporta si al menos 5 casos de 18 pasan de no arreglados a arreglados sin que ninguno vaya al revés, o 7 u 8
con uno al revés, o 9 con dos, o 10 con tres, y además la Δ de medias llega a 0,20.** Con el techo realista de ~6 casos (§0),
«aporta» exige que el bucle convierta casi todo lo convertible. Q-BU-8 ofrece el α = 0,10 a dos colas del piloto (equivalente
en la práctica: 4/0 sigue sin bastar, 5/0 sí, 7/1 sí, 9/2 sí).

### 4.4 Formato fijo de la frase de `RESULTADO-BU.md`

> «Con el bucle de prueba, el agente arregla sin colateral {k}/18 casos reales (IC95 {a}-{b}) frente a {k'}/18 del agente de
> hoy remedido ({k''}/18 en el piloto y la ampliación): **{aporta | no aporta | indeterminado | daña}** (Δ {Δ}, IC {…};
> {b} casos a favor y {c} en contra, p = {p} a una cola). El agente probó en {t}/{T} tiradas ({m} pruebas de media), con
> sobreajuste en {s} tiradas y {l} parches con literal de prueba; de {r} parches aceptados leídos, {r'} arreglan la causa.
> Coste: {x} tokens por tirada, {y} por arreglo aceptado, {z} s de caja por tirada. Este estudio se cierra con este resultado.»

---

## 5. Brazos, réplicas, presupuesto y reglas de parada

### 5.1 Brazos y tiradas

| Brazo | Qué | Tiradas | Presupuesto por tirada |
|---|---|---|---|
| **AG₀** | Ya medido; valores por caso de `privado/agente/ag3/analisis.json` y `amp3/analisis.json` | 0 nuevas | — |
| **AG₁** | `claude -p`, `claude-opus-5-5` (una tirada con otro modelo es inválida), consigna, lanzador, MCP y presupuesto sellados, 2 réplicas × 22 | **44** | 200 000 tokens nuevos / 30 llamadas / 10 min |
| **BU** | Ídem + `caja` (§1) + `CONSIGNA_BU.md` (§1.7), 2 réplicas × 22 | **44** | Ídem + **4 pruebas** (≤ 10 llamadas sin aplicar) |
| REF, DS | No corren: REF no tiene bucle y su FIX es 0/18; DS no tiene saldo (0,08 USD) y recargarlo es decisión de Víctor fuera del estudio | 0 | L-BU-4 |

Orden: un solo `orden.json` con las 88 tiradas sembradas por `sha256("BU2|<huella>|<caso>|<brazo>|<réplica>")`, carpetas
opacas con ese prefijo, bajo la carpeta de cajas del agente, fuera del repositorio. El lado de la máquina del usuario ve «i
plantilla carpeta brazo», sin ids de caso, como hoy.

### 5.2 Presupuesto, en números

- **Tokens:** AG₁ ≈ 44 × 60 000 (media de las dos etapas, 42-57 mil; margen) ≈ 2,6 M; BU ≈ 44 × 85 000 (los 60 000 de hoy
  más 4 respuestas de prueba de ~4 000 tokens y el razonamiento sobre ellas) ≈ 3,7 M. Previsto **≈ 6,3 M tokens nuevos; tope
  duro del estudio 9 M** (≈ 60-90 USD nominales al precio del piloto). No se añaden tiradas para gastarlo.
- **Caja (máquina del laboratorio):** tiradas BU ≈ 44 × (≤ 12 min, previstos 7) ≈ 5 h con USER parado a ratos; evaluación de
  aceptación ≈ (44 + 44 − parches nulos) ≈ 70 parches × 3-4 min ≈ 4 h; BU1 (controles, consistencia, latencia) ≈ 1,5 h.
  Total ≈ 10-11 h de caja en segundo plano. Las tiradas AG₁ no usan la caja.
- **Reloj de la máquina del usuario:** 88 tiradas × ~6 min ≈ 9 h, secuenciales, en segundo plano; el PC está siempre encendido.
- **Sesiones:** 1,5 (§7).

### 5.3 Reglas de parada de BU2 (en el sello, como números)

- Las **3 primeras tiradas BU** por orden sembrado, todas sin respuesta o inválidas → parar, diagnosticar el lanzador o el
  guardián (DV-BU), reanudar una vez; si se repite, parar el brazo.
- **El agente no usa la herramienta:** si en las **6 primeras tiradas BU** ≥ 5 no hacen ninguna prueba → parar y publicar
  «el agente no toma la prueba» con esas 6. No se reescribe la consigna para que la use (sería afinar tras ver tiradas); el
  ANTES siguiente decide. Previsión: usa la herramienta en ≥ 4 de 6 (es más tangible que `verificar_caso`, que casi no usó).
- Tiradas **inválidas** (auditoría; modelo distinto; discrepancia transcripción/`pruebas.jsonl`) ≥ **2** → arreglar (DV-BU) y
  reanudar; si vuelve a pasar, parar.
- **Incidencias de aparato** (`caja_no_disponible`, `abrir` que no arranca la caja en 30 s, `cerrar` que no devuelve en 3
  min): la tirada afectada **se repite una vez** con carpeta nueva (es el aparato, no el agente; la original se guarda como
  inválida); ≥ **3** incidencias en el estudio → parar y arreglar (DV-BU); si tras arreglar vuelve a pasar, parar.
- **Restauración** (al cerrar una tirada o tras una evaluación) que falla dos veces en la misma caja → recrear la caja; si tras
  recrearla vuelve a fallar dos veces, se retiran sus casos (declarado; n se recalcula).
- **Tokens nuevos del estudio ≥ 9 M** → parar los dos brazos.
- Una tirada cortada por presupuesto (tokens, llamadas, reloj) **no se repite**: «sin respuesta» (y en BU, las pruebas hechas
  se guardan igual).
- Si al llegar al tope de BU2 (0,5 sesión) faltan tiradas, siguen en segundo plano y BU3 espera; no se recorta el corpus.

### 5.4 La caja y el circuito congelado mientras una tirada está abierta (resumen de §1.4)

Con la tirada abierta: la caja del circuito del caso arrancada; USER y las demás producciones paradas; ninguna evaluación de
aceptación puede arrancar (cerrojo). Al cerrar: árbol base recargado, 5 fijos comprobados por la regla de la caja, USER en
marcha con huella del congelado y sonda AA, cerrojo suelto. Duración máxima 12 min; registrada por tirada y publicada
agregada (minutos de USER parado en total). Nada del modelo toca git, USER, LABADT, LABORU ni LABMULTI.

### 5.5 El sellado (`etapa/SELLO-BU.md`, commiteado antes de la primera tirada)

Lleva: las respuestas a las Q-BU; la tabla de los 18 casos con `|D_v|`, grupos cubiertos, `|D_h|`, `|R_h|`, latencia medida,
consistencia (y los retirados con motivo); los 6 controles por caja y los controles de cerrojo, de tirada cortada y de cadena
(R5); el resultado del escáner de fugas sobre las salidas de la herramienta; `CONSIGNA_BU.md`, el diff con `CONSIGNA_AG1.md` y
la descripción de la herramienta; la configuración MCP de los dos brazos; los sha256 de todo lo congelado que no cambia
(`ag1_eval.py`, `ag1_cajas.py`, `gen_cajas.py`, `unidades.py`, `lanzar_agente.py`, `mcp_verificador_agente.json`,
`CONSIGNA_AG1.md`) y de lo nuevo (`bu_caja.py`, `mcp_caja.py`, `bu2_tiradas.py`, `bu2.py`, `bu3.py`, `bu_clave.json`); la
huella del verificador (tiene que ser `73d36c38d23c8620…`, la de las dos etapas; si no, se declara y se lista el diff de
`version.ficheros`); la regla de §4.3 con la tabla de discordantes; las reglas de §5.3; y la previsión de §0.

---

## 6. Amenazas a la validez

1. **Adaptarse al juez (la principal).** El agente ve el veredicto del mismo juez que decide la aceptación. Mitigación en
   capas: conjunto oculto (≥ 50 % de `D`, ≥ 75 % de `R`); salida sin evidencia (no puede leer los mensajes de prueba, y mucho
   menos los ocultos); 4 pruebas (no da para escalar sobre el juez); `sobreajuste` contado y con umbral preinscrito; escáner de
   literales; lectura por Jev de 4 aceptados sorteados + todos los sospechosos; secuencia de pruebas publicada. Residual: un
   parche que satisfaga al juez en **todos** los mensajes sin arreglar la causa (L-AG-3): lo acota la lectura, no lo elimina.
2. **El factor no es puro: la herramienta enseña dos disparadores más.** Hoy el agente ve un mensaje y el número
   `otros_casos_que_fallan`; con el bucle ve, tras probar, el veredicto y los hallazgos de hasta 2 disparadores más, y puede
   probar el árbol tal cual para verlos antes de escribir nada (Q-BU-7). Es inherente a un bucle de prueba (quien tiene tests,
   los corre primero). Se declara (L-BU-5) y se describe: cuántas tiradas BU hacen una prueba vacía primero, y la sensibilidad
   (iii) de §4.2 (multigrupo frente a monogrupo) dice si la ganancia va donde «ver variantes» importa.
3. **Deriva del modelo y de la herramienta.** AG₁ remedido y entremezclado (§4.1). Si Víctor elige la alternativa, la sonda de
   6 casos y la etiqueta «no comparable» si difiere.
4. **El reloj compartido.** BU gasta hasta ~2,5 min de sus 10 en pruebas: menos tiempo para leer. Es parte del factor (el
   presupuesto no cambia, ANTES); se reporta cortadas por brazo y la sensibilidad (ii). Si BU se corta por tiempo en ≥ 25 % de
   las tiradas y AG₁ en < 10 %, la frase lo dice: «el bucle no cabe en 10 minutos para este agente».
5. **Caja inestable o lenta.** Firma inestable en ADT (resuelta por veredicto); mensajes de prueba inestables (§3.2);
   latencia de LABMUT y de los casos con entorno (§3.3); un `caja_no_disponible` en mitad de una tirada (repetición una vez).
   Un agente que recibe una prueba que falla por el aparato persigue un fantasma: por eso las incidencias se cuentan y la
   tirada se repite.
6. **Hipótesis generada y contrastada en el mismo corpus (L-BU-2).** Sin reserva. Mitigado por la regla previa, AG₁ fresco y
   todos los casos; no eliminable. La conclusión vale para estos circuitos y este juez.
7. **Quien implementa conoce los resultados por caso.** Herramienta única, conjuntos por semilla, controles con parches
   escritos antes de BU2, nada afinado tras la primera tirada (§3.1).
8. **Una producción a la vez, y USER parado horas acumuladas.** Cerrojos y `cerrar` con huella y sonda; se publica el total de
   minutos parado. Si en algún momento el laboratorio necesita USER, el orquestador se para entre tiradas (nunca dentro).
9. **Fragilidad de la consigna.** Un solo texto, tres cambios declarados, sin retoques. No hay subestudio de fragilidad
   (el del piloto dio «estable»); el riesgo de que la redacción del punto 2 de §1.7 (recomendar probar) determine el uso se
   acota con la regla de «no usa la herramienta» y con el recuento de uso por tirada.
10. **n = 18 y techo bajo.** Previsión de §0: «indeterminado» probable. Es un resultado válido y se cierra con él (S-BU-10).

---

## 7. El plan BU0-BU3, con «hecho cuando» y tope por fase (total 1,5 sesiones)

| Fase | Qué se hace | Hecho cuando | Tope y regla de parada |
|---|---|---|---|
| **BU0** Diseño | Este documento; Q-BU decididas (Jev las de diseño; Víctor Q-BU-1 y Q-BU-5) | `diseno-bucle-fable.md` en el repo y las respuestas en `SELLO-BU.md` §0 | **0,15 sesión.** Una Q de alcance sin decidir al cerrar BU0 → se sigue con la recomendación y se declara |
| **BU1** Herramienta, conjuntos y sello | **Primero el eslabón débil que queda:** latencia de LABMUT (R4 y R1) con el guardián mínimo. Luego: `bu_caja.py` y `mcp_caja.py`; cerrojos; `bu_clave.json` con `D_v`/`R_v` por semilla; consistencia y latencia de los 18 (§3.2-3.3); 6 controles por caja + cerrojo + tirada cortada + cadena R5 (§3.4); escáner de fugas sobre las salidas; `CONSIGNA_BU.md` y descripción; `bu2_tiradas.py`/`bu2.py` (orden de 88, reglas de §5.3), `bu3.py` (§4.2-4.4, incluido el escáner de literales y la lectura sorteada); `SELLO-BU.md` commiteado | Todo medido y en el sello; ≥ 14 casos siguen (18 menos retirados por latencia o inestabilidad); los controles separan en las 4 cajas; la cadena R5 llama a la herramienta y da FIX 1 | **0,5 sesión.** Se para y se publica («no se pudo construir el bucle» o «el bucle no cabe en la caja X») si al agotar el tope la cadena R5 no pasa, o quedan < 14 casos, o una caja entera cae por latencia. Ninguna puerta se relaja; `D_v`/`R_v` no se recortan |
| **BU2** Tiradas | Las 88 en orden sembrado, secuenciales, en segundo plano desde la máquina del usuario; el guardián por tirada BU; evaluación de aceptación de todos los parches en lote al final (o en ventanas AG₁ bajo cerrojo), con restauración por caja | 88 tiradas con transcripción auditada, `respuesta.json`, `puntos.json`, `fix.json` (con `FIX_visible`, `FIX_parcial_oculto`, `sobreajuste`), `pruebas.jsonl` en las BU, coste, minutos de USER parado | **0,5 sesión** activa (el resto en segundo plano; BU3 espera). Reglas de §5.3 |
| **BU3** Análisis y cierre | `bu3.py` sin cambios; tabla por caso (opaco) y brazo; frase de §4.4; sensibilidades (i)-(vii); secuencias de prueba agregadas; escáner de literales; lectura por Jev (4 + sospechosos + 2 de AG₁); amenazas con lo observado; `RESULTADO-BU.md`; cajas paradas, USER en marcha con huella y sonda, `antes_de_publicar.py` LIMPIO; publicación del diseño, el sello y los agregados (sin clave, sin transcripciones con datos, sin `pruebas.jsonl`); memoria: una ficha con la frase y «cerrado» | `RESULTADO-BU.md` da la frase con la regla preinscrita, salga lo que salga; guarda LIMPIO | **0,35 sesión.** No se añade caso ni réplica tras ver datos; no hay BU-bis |

---

## 8. Preguntas (Q-BU), límites (L-BU) y resumen de decisiones (S-BU)

| Q | A quién | Pregunta | Recomendación | Alternativa | Qué cambia en la medida |
|---|---|---|---|---|---|
| **Q-BU-1** | Víctor (alcance) | ¿Se remide entero el agente de hoy (AG₁, 44 tiradas) como control? | Sí, 2 réplicas, entremezclado con BU (§4.1) | AG₀ como control + sonda de deriva de 6 casos × 1 réplica | La alternativa ahorra ≈ 2 M tokens y ≈ 3 h de caja; deja el primario expuesto a la deriva y a la regresión a la media de los valores que motivaron la hipótesis |
| **Q-BU-2** | Jev | ¿Qué devuelve `probar_parche` por mensaje? | Veredicto completo (categoría, subtipo, hallazgos con que/esperado/observado/certeza) **sin evidencia** (§1.1) | (a) solo categoría; (b) evidencia completa de los 8 | (a) deja al agente sin saber por qué sigue fallando: mide menos de lo que la hipótesis necesita; (b) mezcla el factor con «enseñar más casos» |
| **Q-BU-3** | Jev | ¿`D_v` estratificado por grupo de disparadores o sembrado puro? | Uno por grupo, con el caso mostrado (§2.1) | Sembrado puro sobre `D` | Con sembrado puro, en casos de 2-3 grupos `D_v` puede caer entero en el grupo del mostrado: la prueba no revela el arreglo a medias y el bucle no puede ayudar donde la hipótesis dice que ayuda |
| **Q-BU-4** | Jev | ¿La consigna recomienda probar o lo exige? | Recomienda («entregar sin probar también vale»), con regla de parada si no usa la herramienta (§5.3) | Exige ≥ 1 prueba antes de entregar | Exigir mide «herramienta + obligación»; recomendar mide «herramienta disponible», que es lo que tendría en guardia; el riesgo (no la usa) lo acota la parada |
| **Q-BU-5** | Víctor (alcance) | Si en BU1 un caso (o LABMUT) pasa de 90 s por prueba, ¿se retira el caso o se para el estudio? | Retirar el caso, declarado; parar solo si caen ≥ 5 (quedan < 14) o una caja entera (§3.3) | Parar el estudio a la primera, como la regla literal del ANTES | Retirar baja n (18 → ≥ 14) y sesga hacia casos baratos; parar deja el estudio sin hacer por un caso que depende de un tiempo de espera |
| **Q-BU-6** | Jev | ¿Una llamada cuyo parche no aplica gasta prueba? | No (tope 10); solo gastan las que cargan la caja (§1.3) | Toda llamada gasta | La alternativa mide también la torpeza con `viejo` (un blanco de más cuesta ¼ del presupuesto); la recomendación mide el bucle |
| **Q-BU-7** | Jev | ¿Se admite `cambios: []` (probar el árbol tal cual)? | Sí, gasta prueba, se cuenta cuántas tiradas lo hacen primero (§6.2) | Error «parche vacío» | Prohibirlo reduce la fuga «ver más casos» pero quita lo que haría cualquiera con tests (correrlos antes); admitirlo se declara como parte del factor (L-BU-5) |
| **Q-BU-8** | Jev | ¿α = 0,05 a una cola (hipótesis con dirección) o 0,10 a dos colas como el piloto? | Una cola, 0,05 (§4.3) | Dos colas, 0,10 | Casi equivalentes (5/0, 7/1 y 9/2 aportan en los dos); con dos colas una Δ negativa grande también daría p pequeño, que la frase «daña» ya cubre aparte |

**Límites declarados de entrada (L-BU):**

- **L-BU-1.** Techo realista de ~6 casos y previsión «indeterminado» (§0); n = 18 no detecta Δ < 0,20.
- **L-BU-2.** La hipótesis se formó en estos 18 casos y se contrasta en ellos; no hay corpus de reserva.
- **L-BU-3.** Mirth no entra (sin casos que cuenten; caja efímera); las frases hablan de circuitos IRIS.
- **L-BU-4.** Sin REF (FIX 0/18, sin bucle) ni DS (sin saldo): no hay contraste de independencia en BU.
- **L-BU-5.** El factor «puede probar» incluye ver el veredicto de hasta 2 disparadores más y poder probar el árbol tal cual:
  no se separa de «más ejemplos» dentro de este estudio.
- **L-BU-6.** El juez es la verdad por decisión (L-AG-3): un parche que lo satisface en todos los mensajes sin arreglar la
  causa cuenta como FIX; la lectura lo acota.
- **L-BU-7.** El presupuesto por tirada no cambia: BU tiene menos reloj para leer; es parte de lo que se mide.
- **L-BU-8.** No puedo verificar desde fuera que `claude -p` sea hoy el mismo agente que el 12-13 de octubre; AG₁ lo mide,
  no lo garantiza.
- **L-BU-9.** En LABMULTIMUT FIX se decide solo por el acuse (L-AMP-4); en los R de entorno la prueba cuesta dos cargas.

**Resumen de decisiones propuestas (S-BU):**

| S-BU | Decisión |
|---|---|
| S-BU-1 | `probar_parche(parche)` devuelve aplica/compila (con el error del compilador depurado) y el veredicto completo por mensaje sin evidencia; nada más |
| S-BU-2 | Prueba contra `D_v` (3, o 2 si `|D| = 5`; uno por grupo; el mostrado siempre) y `R_v` (5), sellados por semilla |
| S-BU-3 | 4 pruebas que carguen la caja por tirada; las que no aplican no gastan (tope 10); llamadas y tiempo dentro del presupuesto de hoy |
| S-BU-4 | Guardián de la caja por tirada (privilegios de la evaluación, cerrojo, `abrir`/`cerrar` con restauración y `a_user`) + cliente MCP sin privilegios por `ssh` en stdio con el opaco fijado en la configuración |
| S-BU-5 | No aplica → motivo literal, sin carga; no compila → texto del compilador, gasta prueba; aparato → `caja_no_disponible`, incidencia |
| S-BU-6 | Conjunto oculto ≥ 50 % de `D` y ≥ 75 % de `R`; FIX como hoy sobre todo; `FIX_visible`, `sobreajuste`, `FIX_parcial_oculto` secundarios; escáner de literales; lectura de 4 + sospechosos + 2 |
| S-BU-7 | Los 18 casos y los 4 limpios, sin añadir ni quitar a priori; retiradas solo por latencia o inestabilidad medidas en BU1 |
| S-BU-8 | Puerta de latencia por caso (> 90 s retira el caso; ≥ 4 o una caja entera para el estudio) y de consistencia (dos pasadas) |
| S-BU-9 | AG₁ remedido entero y entremezclado; primario BU frente a AG₁; AG₀ como secundario y medida de deriva |
| S-BU-10 | FIX apareado; aporta si p ≤ 0,05 a una cola y Δ ≥ 0,20; no aporta si Δ ≤ 0,10 o IC con 0 y Δ < 0,20; si no, indeterminado y se cierra; «daña» como frase propia |
| S-BU-11 | 88 tiradas, ≈ 6,3 M tokens (tope 9 M), ≈ 10-11 h de caja en segundo plano, 1,5 sesiones (0,15 / 0,5 / 0,5 / 0,35) |
| S-BU-12 | Consigna BU = la sellada + tres cambios declarados; descripción de la herramienta sellada; sin retoques tras la primera tirada |
