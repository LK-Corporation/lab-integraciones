> *Copia pública: se quitaron las alusiones al autor y a su máquina. El resto es el original del laboratorio.*

# Diseño AR0: el aparato de la etapa 21, el arrastre de estado de LinuxForHealth en el estudio publicado

<!-- modelo: Claude Fable 5.1 (claude-fable-5-1); fecha: 25-oct-2026; a ciegas: leído solo ANTES-ETAPA-ARRASTRE.md y el repositorio público -->

**La pregunta fija (del ANTES):** ¿cambia algún veredicto del estudio de conversores publicado cuando LinuxForHealth convierte cada mensaje en su propio proceso, en vez de todos en un solo proceso, como se hizo en el estudio?

**Lo que fija el marco y aquí no se discute:** solo terceros públicos; LinuxForHealth v1.1.0 (el jar de Maven Central) en la caja de siempre; el mismo juez a los dos lados; control positivo (VL11) y negativo (dos corridas del mismo modo) antes de usar el aparato; previsión sellada en un commit antes de la primera corrida del corpus; el corpus del estudio (ADT 263, ORU 40, mínimos 68, muestras 65 = **436 casos**); comparación caso a caso de estado, categoría, subtipo y hallazgos que cuentan; cada diferencia adjudicada (arrastre, no determinismo u otra causa); `RESULTADO-ARRASTRE.md` con una de las dos frases; fe de erratas con la opción B si cambia algo; tope de una sesión y antes del 20-nov; las dos reglas de parada.

**Lo que se leyó para diseñar** (todo en `publicacion/`): `verificador/cv/verificar_conversor.py` entero (validación del adaptador, `agrupar`, `orden_caja`, `_valores`, `Corrida._contenedor`, `leer_salida`, `juzgar`, `_valor`, `comparar`, `--desde-evidencias`, `--comparar`, `--limite-casos`), `cv/adaptadores/*.json`, `cv/lfh/Arnes.java`, `cv/correr_conversor.py`, `cv/VC.md`, `cv/vc/CONTROL-VC.md`, `cv/vc/control_vc.py`, `cv/prueba_vc.py`, `cv/conversor_juguete.py`, `cv/cv3_minimos.py`, `cv/cv3_minimos_vxu.py` (`SECUENCIAS`, modo `secuencias`), `cv/cv3_clases.py`, `cv/juzgar_cv2.py`, `cv/cv3_mecanismos.py`, `vx/VX2.md` (F7), `vx/VX3.md`, `vx/CLASES-VX3.json` (VX-L14), `RESULTADO-CONVERSORES.md`, `cv/RESULTADO-CV3.md`, `cv/CLASES-CV3.json`, `cv/RESULTADO-CV3-minimos.json`, `cv/RESULTADO-CV2.json`, `cv/vc/ejemplos/INFORME-linuxforhealth.json`, `cv/CORPUS-CV2-MANIFIESTO.txt`, `cv/RESULTADO-15A.md`, `codigo/hacer_pagina_conversores.py`, `ARTICULO.md`, `README.md`, `verificador/README.md`, `verificador/MANIFIESTO.txt`, `tests/test_repo_hygiene.py`, `cv/pg/PG.md`, `cv/SELLO-CV2.txt`.

**Carpeta de la etapa:** `verificador/cv/ar/`. Prefijos: decisiones `S-AR-n`, pruebas `P-AR-n`, preguntas `Q-AR-D-n`, límites `L-AR-n`, desviaciones del programador `DV-AR-n`.

---

## 1. Las decisiones (S-AR-n)

| Id | Decisión | Por qué, en una línea |
|---|---|---|
| S-AR-1 | Mensaje a mensaje se corre con **un segundo adaptador**, `cv/adaptadores/linuxforhealth-mensaje.json`, en modo `mensaje` y contenedor `por_mensaje`, con el **mismo arnés compilado, el mismo `lib`, la misma imagen** y el mismo `id` (`linuxforhealth`) | la herramienta ya sabe hacer un contenedor por mensaje (`agrupar` + `_contenedor`), no hace falta tocarla ni compilar nada, y la huella del conversor (`lib` + `Arnes.java`) queda idéntica, `ac41f71b…` |
| S-AR-2 | La orden del adaptador mensaje es `java -cp /clases:/lib2/* Arnes {entrada_dir} {salida_dir} {entrada_fichero}`: Arnes sigue leyendo la carpeta `/in`, que en `por_mensaje` contiene **un solo fichero**; el tercer argumento lo exige la validación del modo mensaje (`mensaje_sin_fichero`) y `Arnes.main` lo ignora (solo usa `args[0]` y `args[1]`) | es la intervención mínima que cumple «mismo conversor, misma caja» sin un arnés nuevo (que cambiaría la huella) ni una excepción en el validador (que cambiaría la herramienta controlada en VC) |
| S-AR-3 | El `id` del adaptador mensaje es `linuxforhealth`, igual que el de lote | los 68 mínimos solo entran si `ad["id"] in ESTUDIO` (Q-VC-D-3), y la clave de `--comparar` y de `VC.comparar` es `(conversor, corpus, caso)` |
| S-AR-4 | El adaptador mensaje fija `imagen_digest` al del estudio, `sha256:7bb84a451705605a47d24eb844d4d9ab03e33e131a507db76aafe25db3907f64`; el lote se corre con el adaptador publicado sin tocarlo, y el paso de identidades exige que el digest registrado en `CORRIDA.json` de cada corrida sea ese | condición 2 del ANTES: misma caja y misma versión; con otro digest la herramienta sale con 3 (Q-VC-D-4) y no se mide nada |
| S-AR-5 | El lado «lote» de la comparación es la herramienta en modo lote (un contenedor por corpus, `agrupar` con `modo == "lote"`), no una corrida nueva de `correr_conversor.py` | VC3 dio 0 diferencias en los 368 casos entre la herramienta en lote y el juicio del estudio: la herramienta en lote **es** el veredicto publicado, con el mismo orden alfabético que Arnes |
| S-AR-6 | «El mismo veredicto» es exactamente `verificar_conversor._valor`: estado, categoría, subtipo y el conjunto de `(hecho, clase, subtipo)` de los hallazgos que cuentan; el texto `que` no cuenta (Q-VC-D-7), y la comparación la hace `VC.comparar` sin reescribirla | una «diferencia» debe querer decir lo mismo que en el control de la etapa 18; el ANTES pide hecho y subtipo, y `clase` solo afina |
| S-AR-7 | **Se compara también el Bundle crudo**, en una capa aparte e informativa, con los UUID normalizados y una **máscara de ruido** que sale del control negativo | sirve para medir y declarar el ruido de fondo con precisión, y para ver arrastre que no mueve el veredicto; nunca entra en N ni en K |
| S-AR-8 | El control positivo es **triple**: VL11 con los dos adaptadores (el del ANTES); el corpus VXU, que entra en las corridas de todos modos, tiene que dar **exactamente las 23 diferencias de F7** (VXU-B18..B40, solo RXA-17 `dato_perdido`); y un positivo **sembrado en ADT con el conversor de juguete**, sin Docker, que prueba el aparato entero (P-AR-6, P-AR-7) | no existe un disparador conocido de LinuxForHealth en ADT/ORU que sembrar: lo que se puede probar es que el aparato ve arrastre en ADT (juguete) y en el corpus real (VXU), no solo en una secuencia de dos mensajes |
| S-AR-9 | El control negativo son **dos corridas completas de cada modo** (L1, L2, M1, M2) sobre los 476 mensajes; el ruido se mide a tres niveles: veredicto, Bundle normalizado y firma del texto de error | M2 hace falta igual para adjudicar «no determinismo» caso a caso; medir el ruido en una muestra dejaría cada diferencia sin su segunda corrida |
| S-AR-10 | Un caso cuenta como **igual** solo si `V_L1 = V_L2 = V_M1 = V_M2`; como **diferente** solo si `V_L1 = V_L2 ≠ V_M1 = V_M2`; cualquier otra combinación es **no determinista** | así ninguna diferencia depende de una sola corrida, y la adjudicación «no determinismo» del ANTES es mecánica |
| S-AR-11 | Cada diferencia se reproduce con **bisección sobre el prefijo del lote** (los mensajes anteriores en el orden alfabético del corpus), después el culpable solo, y si no basta, poda uno a uno; se da por reproducida con **3 de 3** corridas de la secuencia mínima y **3 de 3** del caso solo | el arrastre de F7 es persistente (monótono en el prefijo) y la bisección lo aísla en ≤ 9 corridas de ≤ 263 mensajes; la poda cubre un estado acumulado; 3 de 3 separa del no determinismo |
| S-AR-12 | Las cifras publicadas se recalculan **con un solo juez y los dos modos**: `cv3_minimos.juzgar` y `cv3_clases.main` sobre un ensamblado {Microsoft en lote (idéntico al estudio por VC3), LinuxForHealth en lote} y otro {Microsoft, LinuxForHealth mensaje a mensaje}; la **deriva del juez** (CV3/CV4 → el actual) se declara aparte comparando el ensamblado lote con lo publicado | el juez no se toca; el efecto del arrastre es la resta entre los dos ensamblados, y no se mezcla con lo que cambió el juez desde que se sellaron los resultados |
| S-AR-13 | Los controles **mandan el orden**: `arrastre.py comparar` se niega (código 6) si `POSITIVO-AR.json` y `RUIDO-AR.json` no existen con `pasa: true`; `control_ar.py` se niega a correr el corpus si `SELLO-AR.txt` no verifica `PREVISION-AR.json` y no está en un commit | «el aparato se prueba antes de usarlo» y «la previsión se sella antes de correr» quedan en el código, no en la memoria de quien lo corre |
| S-AR-14 | El conversor de juguete gana una directiva, `JUGUETE-ARRASTRE^<n>`, que envenena los mensajes **siguientes del mismo proceso** (salen sin `Patient.gender`); en `--fichero` nunca afecta a otro mensaje | es el único programa que la herramienta corre fuera de Docker (S-VC-4), y así el positivo sembrado y toda la adjudicación se prueban sin Docker |
| S-AR-15 | No se cambia `verificar_conversor.py`, ni `Arnes.java`, ni ningún fichero de la huella del juez (`mcp_verificador.FICHEROS`), ni `cv3_clases.py`, ni `cv3_minimos.py` | la herramienta controlada en VC y el juez de los resultados sellados tienen que ser los mismos a los dos lados; todo lo nuevo vive en `cv/ar/` y en el adaptador |
| S-AR-16 | El resultado publica solo agregados y las diferencias (`COMPARACION-AR.json` sin las filas iguales); los `juicio.jsonl`, las evidencias y los Bundles siguen privados | como L-VC-8: el detalle por caso del estudio no es público, y el Bundle de un tercero no se redistribuye |
| S-AR-17 | VXU entra en las corridas (la herramienta lo genera siempre con `lab=True` y no hay opción para quitarlo) pero **no entra en N**: N = 436 | el ANTES fija el corpus del estudio; VXU es control, no resultado |

---

## 2. Cómo se corre mensaje a mensaje

### 2.1 Lo que hace la herramienta en `mensaje` / `por_mensaje` (leído del código)

- `agrupar`: con `contenedor == "por_mensaje"` la clave del grupo lleva el `caso`, así que hay **un grupo por mensaje**, ordenados por corpus y, dentro, por nombre de caso.
- `Corrida._contenedor`: copia a `tin` **solo los ficheros del grupo** (`_copiar`) → `/in` contiene un fichero; tiempo máximo `_limite(1) = min(3600, 60·1 + 30) = 90 s`; `multiple` es falso, así que **no hay reintento**; `reg_rc` es el código del contenedor y `leer_salida` lee `<nombre>.json`, si no `<nombre>.error`, si no `error <rc>` o `vacio` (igual que en lote salvo el reintento).
- `orden_caja`: sustituye `{entrada_dir}` → `/in`, `{salida_dir}` → `/salida`, `{entrada_fichero}` → `/in/<fichero>` (`_valores`). La caja (`CAJA`, `--pids-limit`, montajes `:ro`, `--`) es la misma que en lote.
- La validación exige en modo mensaje `contenedor ∈ {por_mensaje, por_grupo}` y `{entrada_fichero}` en la orden; en lote prohíbe cualquier marcador que no sea `{entrada_dir}`/`{salida_dir}` (`lote_marcador`).
- `Arnes.main`: lista `args[0]`, ordena (`sorted()` de `Path`, byte a byte), convierte con **un solo** `HL7ToFHIRConverter`, escribe `<nombre>.json` o `<nombre>.error`, imprime `<nombre> <ms> ms`. Con un fichero en `/in`, un proceso convierte un mensaje. `args[2]` no se lee.
- La huella: `partes = [{carpeta: lib}, {fichero: lfh/Arnes.java}]` → `huella` = `ac41f71b98ee75bac637ecd4b68f58b463f0798bf66cfa941f4194cb2a50acf2` y `huella_con_nombres` = `7ad4d5463640901ae4eccd12afd34d6a6ce70c7fa169575caca148c8232db6aa` (`vc/ejemplos/INFORME-linuxforhealth.json`). La orden **no** entra en la huella; va en la evidencia como `conversion.conversor.invocacion`, que el juez no juzga.

### 2.2 El adaptador, completo: `verificador/cv/adaptadores/linuxforhealth-mensaje.json`

```json
{
 "formato": "adaptador-vc/1",
 "id": "linuxforhealth",
 "_que": "Etapa 21 (arrastre, cv/ar/): LinuxForHealth hl7v2-fhir-converter v1.1.0, el mismo jar, el mismo arnés compilado y la misma imagen que linuxforhealth.json, pero un contenedor y un solo proceso Java por mensaje (S-AR-1). Es la forma de medir si el estudio, que corrió un proceso por carpeta, arrastró estado entre mensajes (issue #348 del proyecto; vx/VX2.md F7).",
 "_id": "El id es el mismo que en lote a propósito: los 68 mínimos solo entran con los identificadores del estudio (Q-VC-D-3) y la clave de --comparar es (conversor, corpus, caso) (S-AR-3).",
 "_orden": "Arnes lee la carpeta /in, que en por_mensaje contiene un solo fichero. El tercer argumento, {entrada_fichero}, lo exige la validación del modo mensaje (mensaje_sin_fichero) y Arnes lo ignora: usa args[0] y args[1] (S-AR-2).",
 "_rutas": "Las rutas son relativas a --artefactos, la misma carpeta que para linuxforhealth.json: lfh/lib, lfh/clases y lfh/Arnes.java.",
 "conversor": {
  "nombre": "linuxforhealth-hl7v2-fhir-converter",
  "version": "v1.1.0 (Maven Central; DV-CV-3)",
  "huella": {"partes": [{"carpeta": "lib"}, {"fichero": "lfh/Arnes.java"}]},
  "_huella_esperada": "ac41f71b98ee75bac637ecd4b68f58b463f0798bf66cfa941f4194cb2a50acf2, la misma que en lote: las partes no cambian (cv/PREVISION-CV2.json)",
  "declara": {"no_soporta": ["ADT^A02", "ADT^A11", "ADT^A13"]},
  "_declara": "como en linuxforhealth.json (L-4 de cv/CLASES-CV3.json)"
 },
 "caja": {
  "tipo": "docker",
  "imagen": "maven:3.9-eclipse-temurin-11",
  "imagen_digest": "sha256:7bb84a451705605a47d24eb844d4d9ab03e33e131a507db76aafe25db3907f64",
  "_imagen_digest": "el del estudio (cv/CV1.md, cv/vc/CONTROL-VC.md); con otro digest la herramienta sale con 3 (Q-VC-D-4), y es lo que se quiere (S-AR-4)",
  "montajes": {
   "lib": {"origen": "lfh/lib", "destino": "/lib2"},
   "clases": {"origen": "lfh/clases", "destino": "/clases"}
  },
  "entorno": {},
  "limites": {"segundos_por_mensaje": 60, "segundos_por_contenedor": 3600, "pids": 1024, "memoria_mb": null}
 },
 "invocacion": {
  "modo": "mensaje",
  "contenedor": "por_mensaje",
  "orden": ["java", "-cp", "/clases:/lib2/*", "Arnes", "{entrada_dir}", "{salida_dir}", "{entrada_fichero}"],
  "plantilla": null,
  "duracion_stdout": "^(?P<nombre>\\S+) (?P<ms>\\d+) ms$"
 },
 "salida": {
  "fichero": "{nombre}.json",
  "fichero_error": "{nombre}.error",
  "forma": "bundle",
  "envoltura": null,
  "codificacion": "utf-8"
 }
}
```

Todo lo que no es `_que`, `_id`, `_orden`, `_imagen_digest`, `invocacion.modo`, `invocacion.contenedor` y el tercer argumento de `orden` es **byte a byte** lo del adaptador de lote. P-AR-1 lo comprueba.

### 2.3 Las órdenes

Desde `verificador/`, con `<art>` la carpeta de artefactos del control VC3 (`lfh/lib`, `lfh/clases`, `lfh/Arnes.java`) y `<muestras>` la carpeta de muestras de ese mismo control (subcarpetas `ms/` y `lfh/`; las muestras no viajan con el repositorio, L-VC-7):

```bash
# comprobar antes de correr nada: valida, huella e imprime la orden del primer grupo (un fichero)
python3 cv/verificar_conversor.py cv/adaptadores/linuxforhealth-mensaje.json <salida> --artefactos <art> --solo-orden

# humo: un mensaje por corpus (5 contenedores), para ver la fontanería con el conversor real
python3 cv/verificar_conversor.py cv/adaptadores/linuxforhealth-mensaje.json <salida>/humo --artefactos <art> --limite-casos 1

# las corridas del corpus (las lanza cv/ar/control_ar.py; aquí, lo que lanza)
python3 cv/verificar_conversor.py cv/adaptadores/linuxforhealth.json         <salida>/L1 --artefactos <art> --muestras <muestras>
python3 cv/verificar_conversor.py cv/adaptadores/linuxforhealth.json         <salida>/L2 --artefactos <art> --muestras <muestras>
python3 cv/verificar_conversor.py cv/adaptadores/linuxforhealth-mensaje.json <salida>/M1 --artefactos <art> --muestras <muestras> --comparar <salida>/L1/juicio.jsonl
python3 cv/verificar_conversor.py cv/adaptadores/linuxforhealth-mensaje.json <salida>/M2 --artefactos <art> --muestras <muestras> --comparar <salida>/L1/juicio.jsonl
```

Cada corrida es una carpeta de la herramienta (`ADAPTADOR.json`, `CORRIDA.json`, `corpus/`, `cajas/`, `evidencias/linuxforhealth/<corpus>/<caso>.json`, `juicio.jsonl`, `INFORME.json`, `INFORME.md`, y `CONTROL.json` en M1 y M2). El `--comparar` de M1/M2 es redundante con `arrastre.py comparar` (misma función) y vale como comprobación cruzada: M1 sale con 5 si hay diferencias.

**El corpus de cada corrida son 476 mensajes** (adt 263, oru 40, vxu 40, muestras 65, mínimos 68), con el manifiesto que escribe `generar_corpus`; las 368 líneas de adt, oru y muestras tienen que ser las de `cv/CORPUS-CV2-MANIFIESTO.txt` (paso 1 del control).

**El orden del lote** (lo que ve Arnes en cada contenedor; es el de `CASOS.json` dentro de cada corpus y el de Python `sorted`, idéntico byte a byte al de Java): adt `A01-001 … A08-027, A1-A01-00 … A1-A31-39, A11-001 … A13-027, A31-001 … A31-027, cap3-08-A01 … cap3-37-A04`; oru `ORU-B01 … ORU-B40`; vxu `VXU-B01 … VXU-B40`; muestras `lfh-ORU-multiline-short-mixed, lfh-ORU-multiline-short, lfh-sample_unix, ms-ADT-A01-01 … ms-ORU-R01-RMGEAD`; mínimos `L01-sin-location-caso, L01-sin-location-control, L02-…, … L18-…, M01-…, M03b-…, M06b/c/d-…, M10-…, R01-…, R02-…` (**en cada par el caso va antes que su control, en el mismo proceso**).

**Coste.** En lote, el estudio tardó 17 s de contenedor para 476 mensajes. Mensaje a mensaje son 476 contenedores, cada uno con arranque de Docker, de la JVM y del conversor (carga de plantillas): estímese 3-6 s por mensaje → **25-50 min por corrida**, dos corridas (M1, M2) → 1-2 h. Los nombres de contenedor llevan el PID (DV-VC-11) y las carpetas de salida son distintas: M1 y M2 pueden lanzarse en paralelo si la máquina tiene núcleos de sobra; si no, en serie. Hay que lanzarlos en primer plano o con `systemd-run --user` y esperar, no fiarse de un aviso en segundo plano.

### 2.4 Lo que no se hace, y por qué

- **No se escribe un arnés nuevo** (`ArnesUno.java`): cambiaría la huella del conversor (añadiría o sustituiría una parte) y exigiría compilar.
- **No se corre la herramienta 436 veces con `--corpus <carpeta de un mensaje>`:** el corpus saldría como `propio` y los casos con otros nombres, y los mínimos no entrarían con los identificadores del estudio: `--comparar` no casaría nada.
- **No se relaja `mensaje_sin_fichero` en el validador:** tocaría la herramienta controlada en VC.

---

## 3. La comparación

### 3.1 Niveles

| Nivel | Qué | Con qué código | Decide |
|---|---|---|---|
| **V, veredicto** | `_valor`: `estado`, `categoria`, `subtipo`, `{(hecho, clase, subtipo)}` de `cuentan` | `VC.comparar(filas_M, filas_L)` tal cual (M es la «corrida», L la «referencia»); `arrastre.comparar_juicios` solo reparte por corpus y aplica S-AR-10 con las cuatro corridas | **N, K y la frase** |
| **B, Bundle normalizado** | el multiconjunto de recursos del Bundle, cada uno serializado con claves ordenadas tras sustituir todo UUID (`[0-9a-fA-F]{8}-(…){4}-…-[0-9a-fA-F]{12}`, también dentro de `urn:uuid:` y de `Tipo/<uuid>`) por `<uuid>` y quitar `resource.id` y `entry.fullUrl`; el Bundle en sí (`type`, `identifier`, `timestamp`) como un pseudorrecurso `Bundle` | `arrastre.firma_recurso`, `multiset_bundle`, `diff_bundles` → lista de `(resourceType, ruta, valor_lote, valor_mensaje)`; las rutas de listas llevan `[]` y no el índice; recursos sin pareja → `(resourceType, "<recurso>", presente/ausente)`; emparejamiento por `resourceType` y, dentro, por orden de firma | el **ruido declarado** y las «diferencias que el juez no ve» |
| **E, errores** | `error.codigo` + `cv3_mecanismos.firma(primera línea de error.texto)` | `arrastre.firma_error` | el ruido de los textos de error (el de Microsoft en VC; en LinuxForHealth son trazas Java) |

La **máscara de ruido** es el conjunto de `(resourceType, ruta)` que difieren entre dos corridas del mismo modo en cualquier caso (§4.2). Entre modos, una diferencia de nivel B en una pareja enmascarada no se cuenta.

### 3.2 La regla por caso (S-AR-10)

Para cada `(corpus, caso)` de `CASOS.json` con fila en las cuatro corridas:

| `V_L1 = V_L2` | `V_M1 = V_M2` | `V_L1 = V_M1` | Clase |
|---|---|---|---|
| sí | sí | sí | **igual** |
| sí | sí | no | **diferente** (candidata a arrastre; va a §5) |
| no | cualquiera | — | **no determinista en lote** |
| cualquiera | no | — | **no determinista en mensaje** |

Un caso sin fila en alguna corrida (`sin_evidencia`: la caja falló) es **sin par** y no entra en ninguna clase. Un caso con `estado` `sin_respuesta` (tiempo vencido: en `por_mensaje` no hay reintento) en alguna corrida es **caja** y se trata en §5.4 antes de clasificarlo.

La comparación principal es **L1 frente a M1**; L2 y M2 solo sirven para S-AR-10 (y la comparación L2 frente a M2 tiene que dar el mismo conjunto de casos diferentes; si no, esos casos son no deterministas por construcción).

### 3.3 Por corpus

`adt`, `oru`, `muestras` y `minimos` son **resultado** (N = 436). `vxu` es **control** (§4.1, positivo 2) y se informa aparte. Para `minimos` se compara además, por par, `INFORME.json.pares_minimos.detalle[].reproduce` de L1 y M1 (los 34; los 18 escritos para LinuxForHealth son los que mueven `confirmada_con_par`).

### 3.4 `COMPARACION-AR.json` (lo que escribe `arrastre.py comparar`)

```
{
 "juez": "<huella, igual en las cuatro corridas>",
 "conversor": {"huella": "ac41f71b…", "huella_con_nombres": "7ad4d546…", "imagen_digest": "sha256:7bb84a45…"},
 "herramienta": {"verificar_conversor": "<huella>", "arrastre": "<sha256 de cv/ar/arrastre.py>"},
 "corridas": {"lote": ["L1", "L2"], "mensaje": ["M1", "M2"]},          # nombres de carpeta, nunca rutas de máquina
 "controles": {"positivo_vl11": true, "positivo_vxu": true, "negativo": true},
 "n": {"comparados": 436, "iguales": …, "diferentes": …, "no_deterministas": …, "sin_par": …, "caja": …},
 "por_corpus": {"adt": {"n": 263, "iguales": …, "diferentes": …, …}, "oru": …, "muestras": …, "minimos": …},
 "control_vxu": {"esperado": ["VXU-B18", …, "VXU-B40"], "observado": […], "solo_en_rxa17_dato_perdido": true, "sale": true},
 "diferencias": [
  {"corpus": "adt", "caso": "A04-012", "posicion_en_lote": 93,
   "lote": {_valor}, "mensaje": {_valor},
   "solo_en_lote": [["PV1-52", "fidelidad", "dato_perdido"]], "solo_en_mensaje": [],
   "que": {"lote": ["…"], "mensaje": ["…"]},                         # el texto, solo para leer
   "bundle": [["Encounter", "participant[].individual.reference", "<uuid>", null]]}
 ],
 "no_deterministas": [{"corpus", "caso", "lote": [V_L1, V_L2], "mensaje": [V_M1, V_M2]}],
 "sin_par": [], "caja": [],
 "pares_minimos": {"lote": {"L01-sin-location": true, …}, "mensaje": {…}, "cambian": ["…"]},
 "bundle": {"mascara": [["Bundle", "identifier.value"], …],
            "casos_con_diferencia_sin_veredicto": [{"corpus", "caso", "diferencias": [[rt, ruta, lote, mensaje]]}],
            "n": …}
}
```

---

## 4. Los controles

### 4.1 Positivo

**P+1, VL11 (el del ANTES).** Procedimiento exacto (`arrastre.py positivo`):

1. `python3 cv/cv3_minimos_vxu.py secuencias <trabajo>/vl11` → `VL11-estado-fabricante-caso/{1-L11a.hl7, 2-L11b.hl7}` y `VL11-estado-fabricante-control/1-L11b.hl7`.
2. Cinco corridas de la herramienta, cada una `--sin-corpus-lab --sin-minimos --corpus <carpeta>`:
   - `lote-caso-1` y `lote-caso-2`: adaptador de lote sobre `…-caso/` (un contenedor, dos mensajes en orden `1-L11a`, `2-L11b`);
   - `mensaje-caso-1` y `mensaje-caso-2`: adaptador mensaje sobre `…-caso/` (dos contenedores);
   - `lote-control-1`: adaptador de lote sobre `…-control/`.
3. Se leen los `_valor` de `propio/2-L11b` y `propio/1-L11a`.

**«Sale»** si y solo si, en las dos repeticiones:
- `lote-caso`: `2-L11b` tiene en `hallazgos` la tupla `("RXA-17", "fidelidad", "dato_perdido")` y algún `que` de ese hallazgo contiene `manufacturer`;
- `mensaje-caso`: `2-L11b` **no** tiene ninguna tupla `("RXA-17", *, "dato_perdido")`;
- `VC.comparar(mensaje-caso, lote-caso)` da **exactamente una** diferencia, la de `2-L11b`, y `solo_en_lote` de esa diferencia es exactamente `{("RXA-17", "fidelidad", "dato_perdido")}` (nada más cambia);
- `1-L11a` es igual en los dos modos;
- `lote-control` `1-L11b` es igual a `mensaje-caso` `2-L11b`;
- en el nivel B, `diff_bundles(lote 2-L11b, mensaje 2-L11b)` contiene una fila `("Immunization", "manufacturer…", …)` (el nivel B también ve el arrastre).

Si no sale: **regla de parada 1**. Se escribe `POSITIVO-AR.json` con `pasa_vl11: false` y lo observado, y se arregla el aparato antes de seguir (lo más probable: la caja, el adaptador o el `digest`).

**P+2, el corpus VXU.** Tras L1 y M1: el conjunto de casos `vxu` diferentes (S-AR-10 con L2 y M2) tiene que ser **exactamente** `{VXU-B18 … VXU-B40}` (23), y en cada uno `solo_en_lote == {("RXA-17", "fidelidad", "dato_perdido")}` y `solo_en_mensaje == ∅` (`vx/VX2.md` F7; `vx/VX3.md`; `CLASES-VX3.json` VX-L14). Si no: el aparato o la construcción no son los de VX2 → **regla de parada 1**, y se declara qué salió. Esto se evalúa antes de interpretar nada de ADT/ORU: `comparar` escribe `controles.positivo_vxu` y solo con `true` escribe la sección de resultado.

**P+3, sembrado en ADT con el juguete** (P-AR-6 y P-AR-7, sin Docker, antes de cualquier corrida). Prueba que el aparato ve arrastre en mensajes ADT y que la bisección lo aísla. **No prueba que LinuxForHealth arrastre en ADT** (L-AR-5): no hay disparador conocido suyo fuera de VXU, y sembrar uno exigiría conocerlo.

**¿Basta un solo positivo?** No: VL11 solo prueba la secuencia de dos mensajes VXU. P+2 prueba el aparato sobre un corpus real con 23 casos y un disparador en la posición 17; P+3 prueba la mecánica sobre ADT. Los tres son obligatorios.

### 4.2 Negativo

**Modos y población:** los dos modos, el corpus entero (476), dos corridas cada uno: `L1`/`L2` y `M1`/`M2`.

**Qué se mide (`arrastre.py ruido`, que escribe `RUIDO-AR.json`):**

| Nivel | Medida | Esperado |
|---|---|---|
| V | `VC.comparar(L2, L1)` y `VC.comparar(M2, M1)`: lista de casos con `_valor` distinto | 0 y 0 (VC3: «los veredictos se mantienen») |
| B | por caso con `estado == "bundle"` en las dos: `diff_bundles`; la unión de `(resourceType, ruta)` es la **máscara**; se cuenta cuántos casos tienen alguna diferencia y cuántas rutas distintas | UUID normalizados → quizá `Bundle.identifier`, `Bundle.timestamp`, `meta.lastUpdated`; la máscara se publica tal cual |
| E | por caso con `estado == "error"`: `firma_error` distinta entre corridas | 0 (trazas Java deterministas) |
| fichero | `INFORME.json` byte a byte igual (P-VC-20) | sí, salvo que E ≠ 0 |

**Cómo se declara:** `RUIDO-AR.json` lleva, por modo, las listas de casos de V y E, la máscara de B con el número de casos por ruta, y `pasa`; `RESULTADO-ARRASTRE.md` lo copia en una tabla («ruido de fondo medido: veredicto 0/0; Bundle: estas rutas en n casos; errores 0/0»).

**Qué dispara la regla de parada 2:**
- `|V_lote ∪ V_mensaje|` mayor que el umbral de Q-AR-D-1 (recomendación: 2 % de los comparados, 8 de 436, sin contar `vxu`) → la etapa para: «el control negativo da diferencias que no se pueden separar del arrastre»;
- o, por debajo del umbral, **un caso no determinista que además es diferente entre modos y cuya secuencia mínima no sale 3 de 3** (§5.2): ese caso es inseparable; si hay al menos uno, la etapa para con ese resultado declarado (el ANTES no admite dejarlo a medias).

Con ruido V = 0 (lo esperado), el negativo pasa y la máscara B queda declarada. Con 0 < ruido ≤ umbral, el negativo pasa **con declaración**: esos casos se adjudican `no_determinismo` y se restan de N en la frase («de los 436, k no deterministas»).

---

## 5. La adjudicación

### 5.1 Categorías y orden

Cada caso **diferente** (S-AR-10) se adjudica a una de: `arrastre`, `no_determinismo`, `caja`, `adaptador`, `otra_causa`, `no_aislada`. Los no deterministas de §3.2 ya son `no_determinismo`. Se adjudica por corpus, en el orden del lote, con el procedimiento de 5.2; antes de bisecar se prueba el **culpable ya conocido** del mismo corpus (5.3).

### 5.2 La secuencia mínima (`arrastre.aislar`)

Entradas: el caso `c`, la lista `P` de los mensajes anteriores a `c` en el orden del lote de su corpus (de `CASOS.json`), dos corredores y dos veredictos de referencia: `V_L(c)` (lote) y `V_M(c)` (mensaje).

- `correr_secuencia(seq)`: escribe los ficheros de `seq` en una carpeta temporal con nombres `%03d-<caso>.hl7` (el orden alfabético reproduce el de la lista), corre el **adaptador de lote** con `--sin-corpus-lab --sin-minimos --sin-sensibilidad --corpus <carpeta>` y devuelve `{caso: _valor}` (quitando el prefijo `%03d-`). Un contenedor, un proceso, toda la secuencia.
- `correr_solo(c)`: lo mismo con el **adaptador mensaje** y la carpeta con solo `c`.

Algoritmo (cada `repro(seq)` es **una** corrida de `seq + [c]` y comprueba `_valor(c) == V_L(c)`; todo queda en `registro`):

1. **Prefijo entero:** si `not repro(P)` → la diferencia no se reproduce con el prefijo (Arnes convierte en orden y escribe cada salida antes de leer la siguiente: nada posterior a `c` puede influir) → `otra_causa` con el registro; se repite `repro(P)` dos veces más: si alguna reproduce → `no_determinismo`.
2. **Caso solo en un proceso de lote:** si `repro([])` → el caso solo, por el adaptador de lote, ya da el veredicto del lote: el arrastre no es la causa; se corre `correr_solo(c)` 3 veces: si da `V_L(c)` alguna vez → `no_determinismo`; si da siempre `V_M(c)` → `adaptador` (la diferencia está entre los dos adaptadores, no en el estado: parar y mirar el adaptador).
3. **Bisección sobre k** (el menor `k` con `repro(P[:k])`; invariante: `repro(P[:hi])` cierto, `repro(P[:lo])` falso, `lo = 0`, `hi = len(P)`): mientras `hi - lo > 1`: `mid = (lo + hi) // 2`; si `repro(P[:mid])` → `hi = mid`, si no `lo = mid`. Culpable: `P[hi - 1]`. ≤ ⌈log₂ 263⌉ = 9 corridas.
4. **¿Basta el culpable?** si `repro([culpable])` → secuencia mínima `[culpable, c]`.
5. **Si no, estado acumulado:** poda uno a uno sobre `S = P[:hi]` (se conserva siempre el último, el culpable): para `i` de `len(S) - 2` a 0, `T = S[:i] + S[i+1:]`; si `repro(T)` → `S = T`. Secuencia mínima `S + [c]`.
6. **Repeticiones:** la secuencia mínima 3 de 3 (`repro`), y `correr_solo(c)` 3 de 3 igual a `V_M(c)`. Las dos → **`arrastre`, reproducida**. Si alguna falla → `no_determinismo` (y, si el caso ya era diferente entre modos, es el caso inseparable de §4.2).
7. **Presupuesto:** 40 corridas por caso y 90 min de reloj para toda la adjudicación (Q: el tope es una sesión). Agotado → `no_aislada`, con la secuencia parcial y el registro.

Lo que se guarda por caso en `ADJUDICACION-AR.json`: `tipo`, `culpable`, `secuencia_minima` (nombres de caso), `registro` (cada corrida: secuencia, `_valor(c)`, segundos), `repeticiones` (3+3), y el `diff_bundles` de `c` entre la secuencia mínima y el caso solo (para contar el mecanismo con el campo exacto).

### 5.3 Economía

- **Culpable conocido primero:** en un corpus con un culpable ya aislado, cada candidata siguiente prueba primero `[culpable, c]` (1 corrida) y, si reproduce, pasa directamente al paso 6 (6 corridas): 7 corridas de 2 mensajes, unos 30 s por caso. Con un solo disparador temprano (como B17 en VXU) la adjudicación de cien casos cabe en una hora.
- **Agrupación:** las candidatas con el mismo `solo_en_lote`/`solo_en_mensaje` en el mismo corpus se adjudican en orden de posición; la primera biseca, las demás prueban el culpable.
- Cada corrida de lote de ≤ 263 mensajes cuesta ~5-15 s (VC3: 17 s por 476).

### 5.4 Caja, timeouts y sin par

- Un caso con `sin_respuesta` (timeout de 90 s) o `sin_evidencia` en una corrida M: se corre solo 3 veces (`correr_solo`); si las tres dan el mismo `_valor`, ese es su `V_M` y se clasifica con S-AR-10; si no, `no_determinismo`. Se anota `caja` con el detalle. Si en M1 o M2 hay más de 5 casos así, se repite la corrida entera una vez antes de seguir.
- Un caso sin fila en L1 o L2 (`sin_evidencia` en lote) tumba el corpus entero de esa corrida: se repite la corrida.

### 5.5 Si la causa no se aísla dentro del tope

El caso se adjudica `no_aislada` con todo lo intentado, se cuenta aparte en la frase («y j diferencias no se aislaron dentro del tope») y en `RESULTADO-ARRASTRE.md` se dice qué faltó. No se declara arrastre sin secuencia reproducida, y no se corrige ninguna cifra publicada por un caso `no_aislada`: va a la cola como pendiente, con su registro.

### 5.6 Las diferencias de nivel B sin cambio de veredicto

Se listan en `COMPARACION-AR.json.bundle`, agrupadas por `(resourceType, ruta)`. Según Q-AR-D-4 (recomendación: adjudicar, acotado), se aísla con 5.2 **solo el primer caso de cada firma** y el resto prueba el culpable; el resultado va a `RESULTADO-ARRASTRE.md` como «lo que el juez no ve» y a la cola de VX-L14/#348, nunca a N, K ni a las cifras.

---

## 6. De las diferencias a las cifras publicadas

### 6.1 Qué cifras dependen de un caso de LinuxForHealth y cómo se recalculan sin tocar el juez

| Dónde se publica | Cifra | De dónde sale | Depende de | Cómo se recalcula |
|---|---|---|---|---|
| `RESULTADO-CONVERSORES.md` (la frase), `ARTICULO.md`, `README.md` raíz (líneas 12-26), `verificador/README.md` («El estudio de conversores»), página `resumen` y `s04`/`s06`/`s09` | N = 15, N por conversor 5/10, N fuertes 7, K = 2, D = 31 (19/12), C = 16, M = 368 | `cv/CLASES-CV3.json` → `frase` | por clase `L-n`: `casos` no vacío y `confirmada_con_par`; por convención: notas del juez por evidencia | `cv3_clases.main` sobre el ensamblado (6.2) |
| `cv/RESULTADO-CV3.md`, tabla «Las 15 nuevas y confirmadas», columna **Casos** (L-10 «2», L-15 «ORU-B18, B22», L-16 «ORU-B11, B13», L-20 «ORU-B07», L-1 «160 + 15 muestras», L-11 «5 + 12 muestras», L-12 «1», L-18 «ORU-B20», L-19 «ORU-B22, B31», L-22 «10 muestras»); página `tarjeta` (`T15`) | casos por discrepancia | `CLASES-CV3.json` → `clases[id].casos` y `ejemplos` | cada caso | el mismo recálculo; la tabla a mano a partir de `CIFRAS-AR.json` |
| `cv/RESULTADO-CV3.md` «31 ya declaradas», «16 convenciones» («14 mecanismos de nota … más PV1-19») | D, C | `CLASES-CV3.json` → `clases`, `convenciones` | las notas de convención por evidencia | ídem |
| `cv/RESULTADO-CV3-minimos.json` (`pares[].linuxforhealth.caso/control.sale`, `categoria`, `que`, `confirmada`; `confirmadas` = 31); página `veredicto_par` | los 18 pares L | `cv3_minimos.juzgar` | las 36 evidencias de mínimos de LinuxForHealth | `cv3_minimos.juzgar` sobre el ensamblado |
| `cv/RESULTADO-CV2.json` y `cv/RESULTADO-CV2.md` (tabla «Lo que salió, frente a lo previsto», filas «LinuxForHealth · ADT/ORU»); página `s09` | ADT 263: correcto 11, fallo silencioso 160, rechazo 92; ORU 40: 4, 36, 0; muestras 65: 3/23/3/36 | `INFORME.json.por_corpus` | categorías | `por_corpus` de M1 frente a L1 |
| `RESULTADO-CONVERSORES.md` «Las siete fuertes» / «Las otras 8», `ARTICULO.md` (B18/B22, B11/B13, B07, B20, B22/B31) | ids de casos en prosa | — | un caso | a mano desde `CIFRAS-AR.json` |
| `cv/vc/ejemplos/INFORME-linuxforhealth.{json,md}`, `cv/VC.md`, `cv/vc/CONTROL-VC.md` | «0 diferencias», pares 34 | lote frente al estudio | no cambian (los dos lados son lote) | solo una nota (Q-AR-D-3) |
| `cv/RESULTADO-15A.md` «14 de 15 siguen» | rama principal | corrida en lote de los 68 mínimos | fuera de la etapa | L-AR-8, nota |
| `docs/conversores/index.html` | todo lo anterior | `codigo/hacer_pagina_conversores.py` | las fuentes `data-fuente` | regenerar tras corregir las fuentes; `tests/test_repo_hygiene.py` |

### 6.2 El recálculo (`arrastre.py recalcular`)

1. **Microsoft, con el juez actual.** Si existe la carpeta de la corrida de Microsoft del control VC3 (`<salida VC>/microsoft/`, con `--muestras`), `python3 cv/verificar_conversor.py cv/adaptadores/microsoft.json <esa carpeta> --artefactos <art> --desde-evidencias` (rejuzga sin Docker). Si no existe, se corre entera (233 s). Microsoft es por fichero por construcción y VC3 probó que coincide con el estudio: solo hace falta que lo juzgue **el mismo juez** que a LinuxForHealth.
2. **Ensamblar** dos árboles, `recalculo/lote/` y `recalculo/mensaje/`, cada uno con:
   - `evidencias/<conversor>/{adt,oru,muestras}/<caso>.json` (**sin** `vxu` ni `minimos`: `cv3_clases` hace `glob("*/*/*.json")` para las convenciones y contaría lo que no es del estudio);
   - `minimos/<conversor>/<id>-{caso,control}.json` (la forma que lee `cv3_minimos.juzgar`);
   - `juicio.jsonl` = filas de Microsoft + filas de LinuxForHealth, filtradas a `corpus ∈ {adt, oru, muestras}` (`cv3_clases` lee `conversor`, `corpus`, `caso`, `cuentan[].{hecho, clase, subtipo, que}`; no necesita `mc`).
   Microsoft es el mismo en los dos árboles; LinuxForHealth sale de L1 en uno y de M1 en el otro.
3. `cv3_minimos.juzgar(<árbol>/minimos, <árbol>/minimos-AR.json)` y `cv3_clases.main(<árbol>/juicio.jsonl, <árbol>/minimos-AR.json, <árbol>/evidencias, <árbol>/CLASES-AR.json)`, los dos con `redirect_stdout`, para cada árbol. Comprobar que `CLASES-AR-*.json.juez` coincide con el de las corridas.
4. `diferencias_cifras` → `CIFRAS-AR.json`: una fila por cifra que difiere entre **lote y mensaje**: `frase.*`, `clases[id].casos[corpus]`, `clases[id].confirmada_con_par`, `sin_clase`, `convenciones`, `minimos.pares[id].confirmada` y `.linuxforhealth.caso/control.sale`, `INFORME.por_corpus[corpus].categorias`, `pares_minimos.reproduce`; cada fila con `donde_se_publica` (la columna 1 de 6.1, como tabla fija `CIFRAS_PUBLICADAS` en `arrastre.py`) y los valores `lote`, `mensaje`, `publicado`.
5. **Deriva del juez**, aparte: las mismas filas entre `CLASES-AR-lote.json` y `cv/CLASES-CV3.json` (juez `54a90cd9`), y entre `minimos-AR-lote.json` y `cv/RESULTADO-CV3-minimos.json`. Lo esperado es lo documentado en `RESULTADO-CONVERSORES.md` («Qué cambió en el juez», CV4: CX.4, Q-CV-D-14, el hecho `PID`) y en `cv/vc/CONTROL-VC.md` paso 3 (L16-cx-4); cualquier otra fila es un hallazgo sobre el juez, no sobre el arrastre, y se declara.
6. **La cifra corregida** de cada fila es `publicado + (mensaje − lote)`, los dos últimos con un solo juez; si la deriva toca la misma fila, el resultado da las dos cosas por separado.

`sin_clase` no vacío en el árbol `mensaje` (un hallazgo que ninguna regla `R` de `cv3_clases.py` cubre) es un **mecanismo nuevo**: no se clasifica aquí (exige el contraste con el proyecto y un par mínimo, que es trabajo de persona como en CV3); se declara en `RESULTADO-ARRASTRE.md` como «sin clase, pendiente de contraste» y va a la cola.

### 6.3 Dónde van las correcciones (según Q-AR-D-2)

Con **K = 0**: una nota con la primera frase en `RESULTADO-CONVERSORES.md` (sección nueva al final, «Etapa 21: mensaje a mensaje», con enlace a `RESULTADO-ARRASTRE.md`) y en `verificador/README.md`; `cv/VC.md` gana una línea sobre el segundo adaptador; la página **no cambia** (no cambia ninguna cifra).

Con **K > 0**: fe de erratas en `RESULTADO-CONVERSORES.md` y `cv/RESULTADO-CV3.md` (tabla publicado → corregido, con el caso y la secuencia mínima), `ARTICULO.md` y los README corregidos en el texto con la nota, los JSON según Q-AR-D-2, la página regenerada y la guarda de higiene en verde.

---

## 7. Las pruebas en rojo (P-AR-n): `verificador/cv/ar/prueba_ar.py`

Corren **sin Docker**, con el conversor de juguete (adaptadores `juguete.json` en lote y uno en modo mensaje construido en memoria como en P-VC-11), con un **espía** copiado de `prueba_vc.py` (15 líneas; `digest` = `maven:3.9-eclipse-temurin-11@sha256:7bb84a45…`, el fijado en el adaptador, y que además guarda `os.listdir` de la carpeta montada en `/in` en el momento de `_run`) y con filas de juicio fabricadas. `python3 cv/ar/prueba_ar.py` → `PRUEBAS AR: TODO BIEN (n comprobaciones, 12 pruebas)`; `python3 cv/ar/prueba_ar.py rojo` → sale 0 solo si fallan las 12. Cada prueba cambia una cosa y lleva su control negativo. Los literales con rutas de contenedor se componen (`"/in" + "/a.hl7"`) para no entrar en `EXCEPCIONES_MANIFIESTO` de la guarda de higiene.

| Id | Qué comprueba | Control negativo | Por qué está en rojo antes del código |
|---|---|---|---|
| P-AR-1 | `leer_adaptador(linuxforhealth-mensaje.json, artefactos_lfh())`: `id == "linuxforhealth"`, `modo == "mensaje"`, `contenedor == "por_mensaje"`, `imagen_digest == "sha256:7bb84a45…"`; `huella` y `huella_con_nombres` **iguales** a las del adaptador de lote sobre los mismos artefactos; bloques `caja`, `salida`, `conversor` iguales salvo `imagen_digest`; `orden_caja(ad, 1, None, "/T/in", "/T/out", art, ["a.hl7"])` termina en `["Arnes", "/in", "/salida", "/in/a.hl7"]` y las diez restricciones de la caja están en el mismo orden que en el de lote (`indice_secuencia`, como P-VC-3) | el mismo adaptador con `modo: lote` → `lote_marcador`; sin `{entrada_fichero}` → `mensaje_sin_fichero`; un byte cambiado en `lib` → otra huella | el fichero no existe: `json_invalido` |
| P-AR-2 | Con el espía, tres mensajes (dos ADT y un ORU) por el adaptador mensaje → **3 corridas**, cada `/in` con exactamente un fichero, el del grupo, y el último argumento de la orden es `/in/<ese fichero>`; con `lab=False, minimos=True` (vía `VC.correr`) el corpus trae `minimos: 68` | el adaptador de lote → 1 corrida con 3 ficheros; una copia con `id: "linuxforhealth-mensaje"` → `minimos: 0`, y `VC.comparar` contra filas con conversor `linuxforhealth` lo deja todo en `solo_en_*` | el adaptador no existe |
| P-AR-3 | `comparar_juicios(L1, L2, M1, M2)` sobre filas fabricadas: clases de S-AR-10 (igual, diferente, no determinista en lote/mensaje, sin par), `vxu` fuera de `n` y en `control_vxu`, `por_corpus` cuadra con `n`, `diferencias[].solo_en_lote/solo_en_mensaje` iguales a la resta de `_valor`, y el conjunto `diferentes` igual al de `VC.comparar(M1, L1)` cuando L2 = L1 y M2 = M1 | cuatro ficheros iguales → todo igual; solo `que` cambiado → igual (Q-VC-D-7); `hallazgos` cambiados → diferente | `import arrastre` falla |
| P-AR-4 | `multiset_bundle`: dos Bundles iguales salvo UUID (en `id`, `fullUrl`, `reference`, `urn:uuid:`) → iguales; entradas permutadas → iguales; `diff_bundles` con un `gender` cambiado → `[("Patient", "gender", "female", "male")]`; con máscara `{("Patient","gender")}` → `[]`; un recurso de más → `("Observation", "<recurso>", …)` | un valor de fecha distinto no se enmascara sin máscara; la máscara no tapa otra ruta | ídem |
| P-AR-5 | `positivo_sale(...)` sobre filas fabricadas de VL11: `True` solo con la diferencia exacta `{("RXA-17","fidelidad","dato_perdido")}` en `2-L11b` del lote, `1-L11a` igual y el control igual al mensaje | diferencia también en `1-L11a` → `False`; otro hecho → `False`; sin diferencia → `False`; sin `manufacturer` en `que` → `False` | ídem |
| P-AR-6 | **Positivo sembrado en ADT:** corpus propio `1-n1, 2-arr, 3-n3, 4-n4` (todos `JUGUETE-NOMINAL`; `2-arr` lleva `JUGUETE-ARRASTRE` en MSH-8); juguete en lote y juguete en mensaje por la herramienta → `comparar_juicios` da **exactamente** `3-n3` y `4-n4` diferentes, con `solo_en_lote == {("PID-8","fidelidad","dato_perdido")}`, `1-n1` y `2-arr` iguales, categoría de `2-arr` `correcto` en los dos modos | sin la directiva → 0 diferencias; `JUGUETE-ARRASTRE^2` con una sola directiva → 0 | la directiva no existe: el juguete devuelve el genérico y no hay diferencias |
| P-AR-7 | `aislar` con corredores de juguete (los mismos `hacer_corredores`, con adaptadores de juguete): lote `n1, n2, ARR, n3, n4, n5`, candidata `n5` → culpable `ARR`, secuencia `[ARR, n5]`, `arrastre` 3/3, ≤ 12 corridas; candidata `n2` → `otra_causa` (el prefijo no reproduce); con `ARR^2` en posiciones 1 y 3 → paso 4 falla, la poda deja `[ARR1, ARR2, n5]`, `arrastre`; con `presupuesto=3` → `no_aislada` con registro | un candidato cuyo `V_L == V_M` no se adjudica (`igual`) | ídem |
| P-AR-8 | `adjudicar_caso(vL1, vL2, vM1, vM2, aislamiento)` y `regla_parada(ruido, n, umbral)`: `(a,a,b,b)` + reproducida → `arrastre`; `(a,a,b,b)` + no → lo que diga `aislamiento.tipo`; `(a,c,·,·)` → `no_determinismo`; `(a,a,a,a)` → `igual`; 9 de 436 con umbral 2 % → para; 8 → no | invertidos | ídem |
| P-AR-9 | `ensamblar` sobre corridas de juguete (relabeladas a `microsoft` y `linuxforhealth`): el árbol tiene solo `evidencias/<conv>/{adt,oru,muestras}` (sin `vxu` ni `minimos`), `minimos/<conv>/<id>-{caso,control}.json` (68 por conversor) y `juicio.jsonl` filtrado; `cv3_minimos.juzgar` y `cv3_clases.main` corren sobre él sin excepción (34 pares; `sin_clase` no vacío es lo esperado con el juguete); `diferencias_cifras` sobre una copia de `CLASES-CV3.json` con `clases[L-15].casos.oru` 2→1 y `frase.N_nuevas_confirmadas` 15→14 devuelve exactamente esas dos filas con su `donde_se_publica` | copias idénticas → `[]` | ídem |
| P-AR-10 | `resultado_md(control)`: con K = 0 contiene la frase exacta «Convertidos mensaje a mensaje, los 436 casos del estudio dan los mismos veredictos que en lote»; con K = 3 la segunda frase con «cambian 3 casos de 436» y la tabla de cifras; `VC.RUTA_MAQUINA` no casa nada; VXU no entra en N; con no deterministas, la coletilla «k no deterministas» | K > 0 sin `CIFRAS-AR.json` → excepción | ídem |
| P-AR-11 | `comprobar_sello(PREVISION-AR.json, SELLO-AR.txt)`: la sha256 cuadra y existen las claves obligatorias (§10.3) | un byte cambiado → `False`; una clave de menos → `False` | ídem |
| P-AR-12 | `arrastre.py comparar` como CLI con `POSITIVO-AR.json`/`RUIDO-AR.json` `pasa: false` → código 6 y no escribe `COMPARACION-AR.json`; con los dos `true` → escribe; `control_ar.py` con `--desde 6` (L1) y sello no verificado → código 7 sin lanzar nada (espía sin corridas) | con sello verificado y commit → lanza | ídem |

Además, tras el código: `python3 cv/prueba_vc.py` sigue en `TODO BIEN (152 comprobaciones, 26 pruebas)` (la directiva nueva no toca lo nominal; P-VC-17 fija la lista de 13 pares del juguete y no cambia) y las suites del juez no se tocan (su huella no cambia: `conversor_juguete.py` no está en `FICHEROS`).

---

## 8. Las preguntas de diseño para Jev (Q-AR-D-n)

Solo lo que ni el ANTES ni las S-AR deciden. Se pasan con estado neutro; las recomendaciones van en 8.5, aparte.

### Q-AR-D-1. El umbral de ruido de veredicto que para la etapa
El ANTES dice «dos corridas en el mismo modo tienen que salir iguales, o la diferencia de fondo se mide y se declara» y «diferencias que no se pueden separar del arrastre: para». No fija cuánto ruido de veredicto es «no separable».
- (a) **Cero:** cualquier caso con veredicto distinto entre dos corridas del mismo modo para la etapa.
- (b) **≤ 2 % de los comparados** (8 de 436): se declaran como no deterministas y se restan de N; por encima, para.
- (c) **≤ 5 %** (21 de 436), igual que (b).

### Q-AR-D-2. Cómo entran las correcciones en lo publicado, si K > 0
- (a) **En sitio con fe de erratas:** se corrigen las filas de `cv/RESULTADO-CV3.md`, `cv/CLASES-CV3.json`, `cv/RESULTADO-CV3-minimos.json` y `cv/RESULTADO-CV2.{json,md}`, cada fichero con una marca de erratum y el valor original; la página regenera sin tocar el guion.
- (b) **Ficheros nuevos y la página apunta a ellos:** `cv/ar/CLASES-AR.json` y `cv/ar/RESULTADO-ARRASTRE-minimos.json` (juez actual, mensaje a mensaje); los publicados quedan intactos salvo una cabecera; `hacer_pagina_conversores.py` cambia `CLASES`/`MINIMOS` y las fuentes `tabla:` a los nuevos; la fe de erratas en los `.md`.
- (c) **Ficheros nuevos y la página sin cambiar las cifras,** con un aviso de erratum enlazando `RESULTADO-ARRASTRE.md`.

### Q-AR-D-3. Qué adaptador de LinuxForHealth es el de referencia después de la etapa
- (a) **Sigue el de lote** (`linuxforhealth.json`); el de mensaje se publica al lado y `VC.md` lo explica.
- (b) **Pasa a ser el de mensaje**: se renombra `linuxforhealth.json` → `linuxforhealth-lote.json` y el nuevo ocupa su nombre; `vc/ejemplos/INFORME-linuxforhealth.*` se regenera mensaje a mensaje.
- (c) **(a) si K = 0 y (b) si K > 0.**

### Q-AR-D-4. Las diferencias de Bundle sin cambio de veredicto
- (a) **Se adjudican, acotado:** la secuencia mínima solo para el primer caso de cada firma `(resourceType, ruta)`; el resto prueba el culpable.
- (b) **Solo se cuentan y se listan**, sin adjudicar.
- (c) **No se miden** (se quita el nivel B salvo para la máscara).

### 8.5 Recomendaciones del diseñador (aparte)
- Q-AR-D-1: **(b)**. Lo esperado es 0 (VC3) y (a) convertiría un parpadeo en el fin de la etapa; (c) deja demasiado margen para que un caso no determinista pase por arrastre.
- Q-AR-D-2: **(b)**. «Los resultados sellados conservan su huella» es la regla de la casa (`RESULTADO-CONVERSORES.md`); la página ya resuelve cada cifra por su fuente, así que apuntarla a los ficheros nuevos es cambiar dos constantes y las fuentes `tabla:` de las filas afectadas.
- Q-AR-D-3: **(c)**. Si no cambia nada, no hay por qué mover lo que el control VC3 validó; si cambia, lo reproducible por un tercero (sin orden) debe ser lo de referencia, y el arrastre, un hallazgo con su secuencia.
- Q-AR-D-4: **(a)**. Es lo que #348 necesita y cuesta poco con el culpable conocido.

---

## 9. Los límites (L-AR-n)

- **L-AR-1, el orden.** «Lote» aquí es un proceso por corpus (adt, oru, vxu, muestras, mínimos) en el orden alfabético byte a byte de los nombres, el de la herramienta y el de Arnes. VC3 garantiza que da los veredictos publicados; qué carpetas exactas corrió el estudio en cada proceso no está en lo público. Otro orden, todo en un solo proceso, o el tráfico real de un servicio de larga vida, puede arrastrar distinto y no se mide.
- **L-AR-2, solo lo que ve el juez.** N y K son de nivel veredicto; el nivel B está enmascarado por el ruido medido y no mira el texto `que`.
- **L-AR-3, arrastre dentro de un mensaje** (entre grupos repetidos del mismo mensaje) no se ve: los dos modos lo comparten.
- **L-AR-4, el disparador tiene que estar en el corpus y antes del caso.** Un arrastre que necesite un mensaje que no está, o que esté después, no se ve.
- **L-AR-5, el positivo sembrado es del juguete.** Prueba el aparato en ADT, no que LinuxForHealth arrastre en ADT/ORU: no hay disparador conocido suyo fuera de VXU.
- **L-AR-6, la huella no cubre `lfh/clases`.** Cubre `lib` y `Arnes.java`; se asume, como en el estudio, que el `.class` montado corresponde a la fuente.
- **L-AR-7, Microsoft queda fuera.** Es por fichero por construcción (un `dotnet` por mensaje), pero no se mide si algo compartido en el contenedor por grupo (`/tmp`) influye.
- **L-AR-8, la rama principal.** `RESULTADO-15A.md` («14 de 15 siguen») se midió en lote sobre los 68 mínimos; si hay arrastre en los mínimos, ese resultado queda por repetir mensaje a mensaje, fuera de la etapa.
- **L-AR-9, dos corridas.** Un no determinismo con probabilidad baja por caso puede pasar por determinismo; el 3 de 3 de la adjudicación lo reduce, no lo elimina.
- **L-AR-10, tiempos.** 90 s por mensaje en modo mensaje, sin reintento dentro de la corrida; los casos de caja se tratan aparte (§5.4) y se declaran.
- **L-AR-11, VXU viaja en las corridas** pero no en N; sus 23 diferencias son control. No hay opción en la herramienta para dejarlo fuera.
- **L-AR-12, la deriva del juez** desde los resultados sellados se declara aparte y no se corrige aquí; el erratum usa un solo juez para los dos modos.
- **L-AR-13, un mecanismo sin clase** (`sin_clase`) no se clasifica en la etapa: exige el contraste con el proyecto y un par mínimo, trabajo de persona.
- **L-AR-14, las muestras no viajan:** un tercero repite adt, oru y mínimos (371 de 436) desde el repositorio.
- **L-AR-15, no se mide rendimiento ni memoria;** un arrastre por tiempo o por recursos solo se vería si cambiara la salida.

---

## 10. El plan

Tope: una sesión, antes del 20-nov. Cómputo estimado: 2-3 h (dos corridas mensaje a mensaje de 25-50 min, el resto minutos). Cada paso escribe su JSON y `CONTROL-AR.json` (como `CONTROL-VC.json`, sin rutas de máquina: carpetas por su nombre); `control_ar.py <art> <muestras> <salida> [--desde N] [--ms <carpeta de Microsoft de VC3>]` los encadena y para en el primer fallo.

| Paso | Qué | Hecho cuando | Si falla |
|---|---|---|---|
| 0 | Q-AR-D-1..4 a Jev con estado neutro (`cv/ar/estado_qar.md`, `preguntas_qar.json`, `decision-jev-qar.md`) | decididas las cuatro | — |
| 1 | `prueba_ar.py` en rojo: las 12 fallan por la razón prevista; commit | `prueba_ar.py rojo` sale 0 | — |
| 2 | Código: `adaptadores/linuxforhealth-mensaje.json`, la directiva del juguete, `cv/ar/arrastre.py`, `cv/ar/control_ar.py`; `prueba_ar.py` en verde; `prueba_vc.py` sigue en verde; `tests/test_repo_hygiene.py` en verde (los JSON nuevos en `JSON_ADMITIDOS`; `.jsonl` no se publican) | todo verde; commit | — |
| 3 | **Identidades, sin Docker** (`control_ar.py --desde 3`): huella de los dos adaptadores = `ac41f71b…` y `huella_con_nombres` = `7ad4d546…`; `generar_corpus` con las muestras → 476 y las 368 líneas del manifiesto iguales; juez: `M._version()["huella"]` registrada; `--solo-orden` del adaptador mensaje imprime `Arnes /in /salida /in/<fichero>` | cuadra | parar: no es el conversor, el corpus o la herramienta del estudio |
| 4 | **Humo** con Docker: `--limite-casos 1` con el adaptador mensaje (5 contenedores); `CORRIDA.json.imagen_digest == sha256:7bb84a45…`; 5 evidencias con `estado` `bundle`/`error` y `duracion_ms` de la salida de Arnes | cuadra | parar: caja o adaptador |
| 5 | **Positivo VL11** (`arrastre.py positivo`) → `POSITIVO-AR.json` con `pasa_vl11` | `sale` | **regla de parada 1**: arreglar el aparato |
| 6 | **Previsión sellada:** `cv/ar/PREVISION-AR.json` y `.md` (10.3), `cv/ar/SELLO-AR.txt` con la forma de `cv/SELLO-CV2.txt` (sha256 de los dos ficheros, de `arrastre.py` y de los dos adaptadores, y la huella del juez); **commit**. `control_ar.py` comprueba el sello, que está en HEAD y que no hay cambios sin commit en esos ficheros, y anota el commit y su fecha | sellado antes de L1 | no se corre nada |
| 7 | L1, L2 (lote; minutos) → `ruido` lote | V = 0 (o ≤ umbral, declarado) | **regla de parada 2** |
| 8 | M1, M2 (mensaje; 1-2 h; en paralelo si se puede) → `ruido` mensaje → `RUIDO-AR.json` con `pasa` y la máscara | ídem; sin `sin_evidencia`; `caja` ≤ 5 por corrida (si no, repetir una vez) | **regla de parada 2** |
| 9 | **Positivo 2**, VXU en L1/M1 (`control_vxu`) → `POSITIVO-AR.json.pasa_vxu` | exactamente VXU-B18..B40, solo RXA-17 | **regla de parada 1** |
| 10 | `arrastre.py comparar` → `COMPARACION-AR.json` (exige los dos `pasa`) | escrito | — |
| 11 | `arrastre.py adjudicar` → `ADJUDICACION-AR.json` (90 min de reloj, 40 corridas por caso) | cada diferente con tipo; ningún inseparable (si lo hay, regla 2: parar y declarar) | parar con lo declarado |
| 12 | `arrastre.py recalcular` (Microsoft rejuzgado con `--desde-evidencias`) → `CLASES-AR-{lote,mensaje}.json`, `minimos-AR-*.json`, `CIFRAS-AR.json`, deriva del juez | escrito; `juez` igual en todo | — |
| 13 | `arrastre.py resultado` → `verificador/RESULTADO-ARRASTRE.md` con una de las dos frases, los controles, el ruido, la tabla por corpus, las diferencias adjudicadas con su secuencia mínima, las cifras que cambian (o «ninguna»), lo que el juez no ve, los límites y «cómo repetir»; `comprobar` sin rutas de máquina | escrito | — |
| 14 | **Publicar con la opción B:** documentos de 6.3; `README.md` raíz y `verificador/README.md` al día; `cv/ar/` con `ENCARGO-AR0.md`, este diseño, las decisiones, el código, las pruebas, la previsión y su sello, y los JSON (`POSITIVO`, `RUIDO`, `COMPARACION` sin filas iguales, `ADJUDICACION`, `CIFRAS`, `CONTROL`); `MANIFIESTO.txt` regenerado; enlaces desde un README (guarda de alcanzabilidad); guarda LIMPIO, higiene, revisión a ciegas y Jev; push | push | — |

### 10.1 Lo que el plan no permite
- Correr L1 sin el sello en un commit (paso 6 antes del 7, en el código).
- Interpretar la comparación sin `POSITIVO-AR.json` y `RUIDO-AR.json` en `pasa: true` (código 6).
- Declarar arrastre sin secuencia mínima 3 de 3 y caso solo 3 de 3.
- Tocar `verificar_conversor.py`, `Arnes.java`, `cv3_clases.py`, `cv3_minimos.py` o el juez.

### 10.2 Salida de `control_ar.py`
Códigos: 0 todo; 1 identidades; 2 humo; 3 positivo VL11; 4 ruido; 5 positivo VXU; 6 comparación sin controles; 7 sello; 8 inseparable en la adjudicación; 9 tope agotado. Cada uno deja `CONTROL-AR.json` con el paso y el motivo.

### 10.3 La previsión que se sella (formato)
`cv/ar/PREVISION-AR.json`, claves obligatorias (P-AR-11): `etapa`, `fecha`, `juez` (huella), `conversor` (`ac41f71b…`), `imagen_digest`, `herramienta` (huellas de `verificar_conversor.py` y `arrastre.py`), `probabilidad_al_menos_una_diferencia_por_arrastre` (`{"veredicto": p, "bundle_sin_veredicto": p}`), `K_previsto` (`[lo, hi]`), `direccion` (más o menos hallazgos mensaje a mensaje), `mecanismos_que_podrian_cambiar` (ids `L-n` de `CLASES-CV3.json`), `pares_que_podrian_cambiar`, `cifras_que_podrian_cambiar` (nombres de 6.1), `ruido_previsto` (`{"veredicto": 0, "bundle": [rutas]}`), `umbral_q_ar_d_1`. La escribe quien programa, con Jev, antes del paso 7. La del diseñador va en el apéndice A como referencia, **no** como sello.

---

## Apéndice A. La previsión orientativa del diseñador (no es el sello)

- **Mecanismo plausible.** #348 habla de «internal variables» que no se reinician. El disparador de F7 es un CWE con texto y sin código (RXA-17) en un campo del que LinuxForHealth construye un **recurso anidado** (Organization → `manufacturer`). Lo análogo en ADT/ORU: Practitioner desde XCN (PV1-7/8/9/17/52, OBR-16, ORC-12, OBX-16), Organization desde PID-3.4 (assigner), PL.4 (L-1 dice que de PV1-3 solo queda PL.4 como Organization) y OBX-23, con texto y sin id o código. En E2 («comp», «opci») y en las muestras hay campos así.
- **Probabilidad de al menos una diferencia por arrastre:** veredicto **0,45**; Bundle sin veredicto **0,70** (el juez no cuenta todos los recursos anidados).
- **K previsto:** 0-40; dirección: **menos hallazgos** mensaje a mensaje (el lote añade `dato_perdido` tras el disparador), con `correcto` en ADT subiendo de 11.
- **Mecanismos que podrían cambiar:** L-22 (PV1-52, 10 muestras), L-7/L-8 (ContactPoint), L-23 (sufijo), L-11 (dirección), L-17 (`CodeableConcept.text`), L-13 (OBX-8), L-26 (unidad), L-14 (`presentedForm`). Poco probable: L-1, L-10, L-12, L-15, L-16, L-18, L-19, L-20 (son de plantilla, no de estado).
- **Pares que podrían cambiar:** L03, L13, L14, L15, L18 (los que llevan XCN/CWE con texto); en los mínimos el control va justo detrás del caso en el mismo proceso.
- **Ruido previsto:** veredicto 0 y 0; Bundle: `id`, `fullUrl` y `reference` (UUID, ya normalizados) y quizá `Bundle.identifier`/`timestamp`; errores 0.

## Apéndice B. Ficheros nuevos y dónde van

| Fichero | Qué | Publicado |
|---|---|---|
| `cv/adaptadores/linuxforhealth-mensaje.json` | §2.2 | sí (`JSON_ADMITIDOS`) |
| `cv/conversor_juguete.py` | + directiva `JUGUETE-ARRASTRE^<n>` (S-AR-14): estado de módulo `{vistos, envenenado}`; el mensaje con la directiva se convierte como `JUGUETE-NOMINAL`; a partir del n-ésimo (1 por omisión) todos los siguientes del proceso salen sin `gender` (`re.sub(r',\s*"gender":\s*"[^"]*"', "", contenido)`, sin reserializar: conserva `1.20`); en `--fichero` el proceso es nuevo y nunca afecta a otro mensaje; docstring actualizado | sí (cambia su línea en `MANIFIESTO.txt`) |
| `cv/ar/arrastre.py` | subórdenes `positivo`, `ruido`, `comparar`, `adjudicar`, `recalcular`, `resultado`; funciones `filas`, `valor` (= `VC._valor`), `comparar_juicios`, `firma_recurso`, `multiset_bundle`, `diff_bundles`, `firma_error`, `ruido`, `positivo_vl11`, `positivo_sale`, `positivo_vxu`, `hacer_corredores`, `aislar`, `adjudicar_caso`, `regla_parada`, `ensamblar`, `recalcular`, `diferencias_cifras`, `CIFRAS_PUBLICADAS`, `resultado_md`, `comprobar_sello`; `sys.path` como `control_vc.py`; solo biblioteca estándar | sí |
| `cv/ar/control_ar.py` | el orquestador de §10 | sí |
| `cv/ar/prueba_ar.py` | P-AR-1..12 | sí |
| `cv/ar/PREVISION-AR.{json,md}`, `SELLO-AR.txt` | §10.3 | sí |
| `cv/ar/POSITIVO-AR.json`, `RUIDO-AR.json`, `COMPARACION-AR.json` (sin filas iguales), `ADJUDICACION-AR.json`, `CIFRAS-AR.json`, `CONTROL-AR.json`, `CLASES-AR-{lote,mensaje}.json`, `minimos-AR-{lote,mensaje}.json` | los resultados | sí (`JSON_ADMITIDOS`); `juicio.jsonl`, evidencias y Bundles, no |
| `verificador/RESULTADO-ARRASTRE.md` | el documento del ANTES | sí |
| `cv/ar/ENCARGO-AR0.md`, `diseno-ar-fable.md`, `estado_qar.md`, `preguntas_qar.json`, `decision-jev-qar.md` | la procedencia | sí |

Todo documento nuevo tiene que quedar enlazado desde `verificador/README.md` (guarda `test_todo_documento_es_alcanzable_desde_el_readme`) y ningún fichero puede llevar una ruta de máquina (`RUTA_MAQUINA`, `test_ninguna_ruta_absoluta_de_maquina`): las carpetas se nombran `L1`, `M1`, `recalculo/lote`, nunca con su ruta.