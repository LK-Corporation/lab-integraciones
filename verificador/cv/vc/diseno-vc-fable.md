> *Copia pública: se quitaron las alusiones al trabajo del autor y a su máquina. El resto es el original del laboratorio.*

# Diseño VC0: «verifica tu conversor en un comando» (etapa 18)

<!-- modelo: Claude Fable 5.1 (claude-fable-5-1); fecha: 24-oct-2026; a ciegas del repositorio privado: leído solo publicacion/ -->

**La pregunta fija:** ¿puede un tercero pasar su conversor HL7 v2 → FHIR por el verificador con un fichero de adaptador y una
orden, sin escribir código, y obtener el mismo juicio que obtuvo el laboratorio a mano en el estudio de conversores (14l)?

**La respuesta de este diseño:** una herramienta de línea de órdenes, `verificador/cv/verificar_conversor.py`, que lee un
adaptador JSON, levanta el conversor en la caja de siempre, escribe una evidencia por mensaje con la forma que ya lee el juez
(S-CV-2), juzga con `verificador.verificar` sin tocarlo, agrega por las ocho clases de S-CV-5 y escribe un informe que dice lo
que ve y lo que no puede saber. Los dos adaptadores reales (Microsoft y LinuxForHealth) caben sin una línea de código: están en
§2.4 y §2.5, y reproducen la orden de `cv/correr_conversor.py` flag por flag.

Lo que aquí se llama «el juez» es el de hoy: huella `40bbc3ef…` en el laboratorio, `0dd3ae5c…` en la copia pública (difieren
solo por el extracto de `medida/encargo_medida.md`). Ningún fichero de `mcp_verificador.FICHEROS` cambia.

---

## 1. Decisiones (S-VC-n)

| Id | Decisión | Porqué, en una línea |
|---|---|---|
| S-VC-1 | La herramienta es `verificador/cv/verificar_conversor.py`, solo biblioteca estándar; **importa** el juez (`verificador`, `puntos_entrada`, `conversion`, `mcp_verificador`) y no edita ningún fichero de la huella. | Condición 3: el juez no cambia; la huella sigue siendo `40bbc3ef`/`0dd3ae5c`. |
| S-VC-2 | El adaptador es un JSON **declarativo** con cinco bloques (`conversor`, `caja`, `invocacion`, `salida`, y `limites` dentro de `caja`); no admite ganchos, scripts ni expresiones. Lo que no cabe en él es un límite declarado (L-VC-3), no un script. | «Sin escribir código» quiere decir que el tercero solo rellena datos. |
| S-VC-3 | Las restricciones de la caja **no son configurables**: el adaptador elige imagen, montajes (siempre `:ro`), variables de entorno y límites; la herramienta añade siempre `--rm --network none --read-only --tmpfs /tmp --cap-drop ALL --security-opt no-new-privileges --user 65534:65534 -e HOME=/tmp --pids-limit N --name vc-<id>`. No hay campo para quitarlas. | Condición 1, y es la caja de E-CV-3 que ya corrió en el estudio. |
| S-VC-4 | Dos tipos de caja: `docker` (la única para terceros) y `proceso_local`, que la herramienta acepta **solo** si el adaptador apunta al conversor de juguete del laboratorio (`conversor.nombre` empieza por `juguete-` y la orden ejecuta `cv/conversor_juguete.py`, comprobado por ruta real). | Condición 4 (pruebas sin Docker) sin romper la 1: el único código que corre fuera de la caja es del laboratorio. |
| S-VC-5 | La evidencia por mensaje es **exactamente** la de S-CV-2: `{punto_entrada, mensaje, conversion: {conversor: {nombre, version, huella, plantilla, invocacion}, salida: {estado, bundle|error, duracion_ms}, perfil_valor: "guia"}}`, validada contra `mcp_verificador.E_PROPS["conversion"]` con `mcp_verificador.validar`. Lo demás de la corrida (imagen, digest, orden, fecha, tiempos) va en `CORRIDA.json`. | El juez y el MCP ya leen esa forma; nada nuevo que juzgar. |
| S-VC-6 | Tres formas de correr, declaradas en `invocacion`: `lote` (el conversor recorre `/in` y escribe en `/salida`), `mensaje/por_mensaje` (un contenedor por mensaje) y `mensaje/por_grupo` (un contenedor por grupo con un bucle `sh` que la herramienta escribe y que registra `.rc` y `.log` por mensaje). Los grupos son por plantilla si la hay; si no, uno solo. | Es lo que hizo el estudio (DV-CV-11): Microsoft fichero a fichero en un contenedor por plantilla; LinuxForHealth en lote. |
| S-VC-7 | La plantilla se elige por una **regla declarada** (`msh9_tipo_evento`, `msh9_tipo` o `fija`), leyendo MSH-9 con los separadores del propio mensaje (DV-CV-12), en mayúsculas; con `comprobar_fichero` opcional, un mensaje sin plantilla da `error/sin_plantilla` sin entrar en la caja. | Microsoft necesita `-r ADT_A01`; E2 trae mensajes con `#$%*!`. |
| S-VC-8 | La salida se lee por una **forma declarada**: `bundle` (el fichero es el Bundle) o `envuelto` (el Bundle está bajo una ruta de claves, con un estado bajo otra). El Bundle envuelto se **recorta del texto original** por posiciones (`json.JSONDecoder.raw_decode`), nunca se reserializa. | La precisión decimal cuenta (Q-CV-D-10): `json.loads`+`dumps` convierte `1.20` en `1.2`. |
| S-VC-9 | Tabla cerrada de estados por mensaje: `bundle`, `error`, `vacio`, `sin_respuesta`, y fuera de la evidencia `sin_evidencia` (fallo de la caja). La herramienta **nunca inventa un `error`**: solo lo que el conversor escribió (fichero de error, estado de la envoltura, código de salida registrado). | Lo pide el encargo; L-CV-8 ya dice que el juez no distingue caja de conversor. |
| S-VC-10 | El corpus por omisión es el del laboratorio: `adt/` (263: E2 + cap. 3 + A1, en ese orden), `oru/` (40, generadas en memoria desde `bases_oru.py`) y `minimos/` (68, desde `cv3_minimos.PARES`), normalizado como DV-CV-10 (CR, sin BOM) y con `MANIFIESTO.txt` (sha256 por fichero y huella global). `--corpus` añade mensajes propios; `--muestras` las de los proyectos. | Reproducir el estudio y servir al tercero con lo que es público. |
| S-VC-11 | El juicio es `verificador.verificar(e)` con el punto que la propia evidencia declara, más las tres alternativas de sensibilidad (`conversion.con_alternativas`). Una fila por caso en `juicio.jsonl` con las **mismas claves** que `cv/juzgar_cv2.py` (`conversor, corpus, caso, punto, estado, categoria, subtipo, cuentan[{hecho, clase, subtipo, que}], notas, alternativas`) y tres más (`citas`, `convenciones`, `plantilla`). | El mismo juez; y `--comparar` puede leer el detalle del estudio tal cual. |
| S-VC-12 | La agregación es por las **ocho clases de S-CV-5**, y dentro por `(hecho sin índice, ruta, firma)`, donde `ruta` es la primera palabra del `que` (como `juzgar_cv2.ruta`) y `firma` es `cv3_mecanismos.firma(que)`. Los rechazos van aparte («no son de las ocho clases»). Los MC-ADT/ORU-n de la previsión **no** se usan: eran la previsión del estudio. | Lo pide el encargo; es independiente de qué conversor sea. |
| S-VC-13 | El informe lleva `contraste_con_el_proyecto: {hecho: false}` y cada mecanismo `clase_cv: "sin_contraste"`; no usa las palabras «nueva», «confirmada» ni «ya declarada» para lo que encontró. La frase fija del estudio **no se imprime**. | Lo que la herramienta no puede saber (si el proyecto ya lo declara) no debe aparentarlo. |
| S-VC-14 | `INFORME.json` es **determinista**: sin fechas, tiempos ni rutas de máquina. Lo variable (`fecha`, duraciones, digest resuelto, rutas) está en `CORRIDA.json`. | Dos corridas iguales dan el mismo informe byte a byte, y se prueba. |
| S-VC-15 | Códigos de salida fijos: `0` todo juzgado; `2` adaptador inválido; `3` caja no disponible (Docker o imagen ausentes) antes de correr; `4` la caja falló en alguna corrida (hay informe, con lo no juzgado); `5` `--comparar` encontró diferencias; `1` error interno. | Automatizable y sin leer texto. |
| S-VC-16 | Las pruebas, `cv/prueba_vc.py` (P-VC-1..26), corren **sin Docker** con `cv/conversor_juguete.py` y un `EjecutorLocal`; la orden Docker se prueba como lista de argumentos construida por una función pura. El juguete es del laboratorio y escribe sus Bundles a mano, no desde el perfil. | Condición 4; y «un error de la proyección no se confirma a sí mismo» (CV1-b). |
| S-VC-17 | El control compara **caso por caso** con el detalle privado del rejuicio de CV4 (clave `(conversor, corpus, caso)` → `estado, categoria, subtipo, {(hecho, clase, subtipo)}`) y, desde lo público, los agregados de `RESULTADO-CV2.json` y los 68 mínimos; toda diferencia se adjudica por escrito en `cv/CONTROL-VC.md` (arnés, corpus, juez, conversor o herramienta). | Condición 5; el detalle por caso del estudio no es público. |
| S-VC-18 | Los orígenes de los montajes y de la huella son rutas **relativas a `--artefactos`** (o a `VC_ARTEFACTOS`); un adaptador publicado no lleva rutas de máquina. | La guarda de higiene prohíbe rutas absolutas de máquina. |
| S-VC-19 | La herramienta **no descarga nada**: la imagen debe estar ya en la máquina (`docker image inspect`); si no, para con `3` y dice la orden `docker pull` que el usuario debe correr él. El digest resuelto se registra. | Sin red en la herramienta; la caja sigue sin red. |
| S-VC-20 | Cada contenedor lleva `--name vc-<id>-<n>`; al vencer el tiempo la herramienta hace `docker kill <nombre>` y marca `sin_respuesta/timeout`. | `--rm` no basta cuando se mata al cliente `docker run`. |
| S-VC-21 | Las claves que empiezan por `_` en el adaptador son comentarios y se ignoran. | JSON no tiene comentarios y el adaptador publicado necesita explicarse. |
| S-VC-22 | La herramienta decide el punto de entrada **solo por MSH-9.1**: `ORU` → `oru_conv`; todo lo demás → `adt_conv`. El juez dice `fuera_de_alcance` para lo que no cubre. | Es la regla de `correr_conversor.main`; cambiarla rompería el control. |

---

## 2. El formato del adaptador

### 2.1 Esquema

Un fichero JSON, `formato: "adaptador-vc/1"`. Tipos y topes se validan con `mcp_verificador.validar` sobre el esquema
`ESQUEMA_ADAPTADOR` (un dict con `type`, `enum`, `required`, `maxLength`, `properties`, `items`, como `E_PROPS`); lo que el
esquema no puede decir lo comprueba `validar_adaptador()` y lo rechaza con `ErrorEntrada(codigo, campo, texto)`. Todo rechazo
imprime `adaptador inválido: <campo>: <texto>` y sale con `2`.

```
{
 "formato": "adaptador-vc/1",                       # obligatorio, literal
 "id": "<[a-z0-9-]{1,32}>",                         # nombre de la carpeta en evidencias/; «microsoft», «linuxforhealth»…
 "conversor": {
   "nombre":  "<≤128>",                             # va a la evidencia tal cual
   "version": "<≤64>",                              # idem; etiqueta publicada + commit si se conoce
   "huella":  {"partes": [ {"carpeta": "<nombre de montaje | ruta relativa>"} | {"fichero": "<ruta relativa>"} , … ]},
   "declara": {"no_soporta": ["ADT^A02", …]}        # opcional (Q-VC-D-8); solo separa rechazos en el informe
 },
 "caja": {
   "tipo": "docker" | "proceso_local",              # proceso_local: solo el juguete (S-VC-4)
   "imagen": "<repositorio:etiqueta>",              # obligatorio con docker; no se descarga (S-VC-19)
   "imagen_digest": "sha256:<64 hex>" | null,       # si se da, debe coincidir con el digest local (Q-VC-D-4)
   "montajes": { "<nombre>": {"origen": "<ruta relativa a --artefactos>", "destino": "</ruta absoluta en el contenedor>"}, … },
   "entorno":  { "<[A-Z_][A-Z0-9_]*>": "<valor literal ≤256>", … },   # HOME no se admite: lo pone la herramienta
   "limites":  {"segundos_por_mensaje": 60, "segundos_por_contenedor": 3600, "pids": 1024, "memoria_mb": null}
 },
 "invocacion": {
   "modo": "lote" | "mensaje",
   "contenedor": "por_mensaje" | "por_grupo",       # solo en modo mensaje; por_grupo exige sh en la imagen
   "orden": ["<programa>", "<arg con {marcadores}>", …],   # argv, sin shell; en por_grupo se envuelve en sh -c
   "plantilla": null | {"regla": "msh9_tipo_evento" | "msh9_tipo" | "fija", "valor": "<solo con fija>",
                        "comprobar_fichero": null | {"montaje": "<nombre>", "patron": "<con {plantilla}>"}},
   "duracion_stdout": null | "<regex con grupos (?P<nombre>…) y (?P<ms>…)>"
 },
 "salida": {
   "fichero":       "<patrón con {base} o {nombre}>",   # lo que escribe el conversor por mensaje, dentro de /salida
   "fichero_error": null | "<patrón>",                  # si el conversor escribe un fichero por excepción
   "forma": "bundle" | "envuelto",
   "envoltura": null | {"ruta_bundle": ["<clave>", …], "ruta_estado": ["<clave>", …] | null, "estado_ok": "<valor>" | null},
   "codificacion": "utf-8" | "utf-8-sig"
 }
}
```

**Marcadores de la orden** (los únicos; otro `{…}` → `adaptador_invalido/marcador_desconocido`):

| Marcador | Valor | Modos |
|---|---|---|
| `{entrada_dir}` | `/in` | todos |
| `{salida_dir}` | `/salida` | todos |
| `{entrada_fichero}` | `/in/<nombre>` | `mensaje` |
| `{salida_fichero}` | `/salida/` + `salida.fichero` rellenado | `mensaje` |
| `{salida_error}` | `/salida/` + `salida.fichero_error` rellenado | `mensaje` |
| `{nombre}` | nombre del fichero con extensión (`A01-001.hl7`) | `mensaje` |
| `{base}` | sin extensión (`A01-001`) | `mensaje` |
| `{plantilla}` | la elegida por la regla | `mensaje`, con `plantilla` declarada |
| `{msh9_tipo}`, `{msh9_evento}` | MSH-9.1 y MSH-9.2 en mayúsculas | `mensaje` |

**Reglas que el esquema no dice** (`validar_adaptador`, cada una con su código de rechazo):

- `destino` de un montaje: absoluto, no `/in`, `/salida`, `/tmp`, `/` ni `/proc`, sin repetirse (`montaje_destino`).
- `origen` existe y es carpeta tras resolverlo contra `--artefactos` (`montaje_inexistente`); nunca se monta `rw`.
- `huella.partes` no vacío; cada parte resuelve a una carpeta o fichero existentes (`huella_parte`).
- `entorno` no contiene `HOME`, `PATH` ni `LD_PRELOAD` (`entorno_reservado`); nombres por la regex (`entorno_nombre`).
- `limites`: `1 ≤ segundos_por_mensaje ≤ 600`, `segundos_por_mensaje ≤ segundos_por_contenedor ≤ 7200`, `16 ≤ pids ≤ 4096`,
  `memoria_mb` null o `≥ 256` (`limite_fuera_de_rango`).
- `modo = lote` solo admite `{entrada_dir}` y `{salida_dir}` y exige `salida.fichero` con `{nombre}` o `{base}` (`lote_marcador`).
- `modo = mensaje` exige `contenedor` y `{entrada_fichero}` en la orden (`mensaje_sin_fichero`).
- `{plantilla}` en la orden exige `invocacion.plantilla` (`plantilla_sin_regla`); `fija` exige `valor`.
- `forma = envuelto` exige `envoltura.ruta_bundle` no vacía (`envoltura_sin_ruta`).
- `caja.tipo = proceso_local`: `conversor.nombre` empieza por `juguete-` **y** `orden[0:2] == ["python3", "<ruta>"]` con
  `os.path.realpath(<ruta>) == realpath(cv/conversor_juguete.py)` junto a la herramienta (`proceso_local_solo_juguete`).
- Claves desconocidas que no empiecen por `_` → `clave_desconocida`.

### 2.2 La huella del conversor

`huella = sha256( concat( hex(parte_1), hex(parte_2), … ) )`, con las partes **en el orden declarado**, donde
`hex(carpeta) = sha256( concat( sha256(bytes de cada fichero) en orden de os.walk ordenado por carpeta y nombre ) )` y
`hex(fichero) = sha256(bytes)`. Es la fórmula de `correr_conversor.huella_carpeta`: con las partes `[out, Templates/Hl7v2]` da
la de Microsoft del estudio (`766f8938d0c12c382bec2edceeca4d3be4fd19900d0bd131ba880ac615fadf3e`) y con `[lib, Arnes.java]` la de
LinuxForHealth (`ac41f71b98ee75bac637ecd4b68f58b463f0798bf66cfa941f4194cb2a50acf2`), las dos públicas en
`cv/PREVISION-CV2.json`. La fórmula no ve nombres ni rutas (L-VC-5; Q-VC-D-1 decide si se añade una segunda huella con nombres
en `CORRIDA.json`). `CORRIDA.json` registra además `imagen` e `imagen_digest` resuelto.

### 2.3 Cómo se lee la salida y se decide el estado

Por cada mensaje, en este orden, el primero que case:

| Lo que hay en `/salida` y en el registro | `salida.estado` | `error.codigo` / `texto` |
|---|---|---|
| `salida.fichero` existe, `forma = bundle` | `bundle` = texto del fichero (decodificado con `codificacion`) | — |
| `salida.fichero` existe, `forma = envuelto`, el JSON se lee, `ruta_estado` vale `estado_ok` (o no hay `ruta_estado`) y `ruta_bundle` existe | `bundle` = **recorte textual** del valor bajo `ruta_bundle` | — |
| idem pero `ruta_estado` ≠ `estado_ok` | `error` | `codigo = str(estado)`, `texto = JSON[:4000]` |
| idem pero el JSON de la envoltura no se lee, o falta `ruta_bundle` | `bundle` = texto entero del fichero (el juez dirá `indeterminado/lectura`) | — |
| `bundle` con más de 4.000.000 caracteres (DV-CV-5) | `error` | `demasiado_grande` / `"<n> caracteres"` |
| `salida.fichero_error` existe | `error` | `excepcion` / texto del fichero `[:4000]` |
| no hay fichero y hay registro por mensaje (`.rc` en `por_grupo`; código del proceso en `por_mensaje`) con `rc ≠ 0` | `error` | `str(rc)` / cola del `.log` o de stdout+stderr `[-4000:]` |
| no hay fichero y el registro por mensaje dice `rc = 0` (o el contenedor de `lote` salió con 0) | `vacio` (Q-VC-D-2) | — |
| no hay fichero ni registro por mensaje: el contenedor murió, salió ≠ 0 en `lote`, o venció el tiempo | `sin_respuesta` | `timeout` o `str(rc)` / cola de stdout+stderr |
| `docker run` devolvió 125, 126 o 127, `docker` no está, la imagen no está, o `/salida` no se puede leer | **no hay evidencia**: `sin_evidencia/caja` para todo el grupo, en `no_juzgado` | se guarda `cajas/<grupo>.log` |

`duracion_ms`: medido por mensaje en `por_mensaje`; en `por_grupo` y `lote`, el tiempo del contenedor dividido por sus mensajes
(como el estudio), salvo que `duracion_stdout` case una línea para ese `nombre`. No se juzga (L-VC-10).

**El recorte textual (S-VC-8):** un recorrido del objeto raíz con `json.JSONDecoder().raw_decode(texto, idx)`: se lee cada
clave (`raw_decode` sobre la cadena), se salta `:` y espacios, se anota `inicio`, se lee el valor con `raw_decode` (que consume
el valor entero, anidado o no) y se obtiene `fin`; si la clave es la buscada, se baja un nivel o se devuelve `texto[inicio:fin]`.
Unas 25 líneas; nada se reserializa.

### 2.4 Adaptador de ejemplo: Microsoft FHIR-Converter v7.0

Reproduce `correr_conversor.correr_microsoft`: un contenedor por plantilla con un bucle dentro, fichero a fichero (DV-CV-11),
telemetría apagada, plantilla por MSH-9 (DV-CV-12), salida envuelta `{Status, FhirResource}`. Rutas relativas a `--artefactos`
(en el laboratorio, la carpeta de artefactos de CV1; `ms/` dentro).

```json
{
 "formato": "adaptador-vc/1",
 "id": "microsoft",
 "_que": "Microsoft FHIR-Converter v7.0 (commit 253307f), construido desde su código como dice cv/CV1.md; corre en el runtime de .NET 6 sin red.",
 "conversor": {
  "nombre": "microsoft-fhir-converter",
  "version": "v7.0 (253307f)",
  "huella": {"partes": [{"carpeta": "codigo"}, {"carpeta": "plantillas"}]},
  "_huella_esperada": "766f8938d0c12c382bec2edceeca4d3be4fd19900d0bd131ba880ac615fadf3e (cv/PREVISION-CV2.json)"
 },
 "caja": {
  "tipo": "docker",
  "imagen": "mcr.microsoft.com/dotnet/runtime:6.0",
  "imagen_digest": null,
  "_imagen_digest": "el estudio corrió con sha256:75752d6e… (cv/CV1.md); el control lo fija con el digest resuelto en la máquina",
  "montajes": {
   "codigo":     {"origen": "ms/out", "destino": "/app"},
   "plantillas": {"origen": "ms/src/data/Templates/Hl7v2", "destino": "/tpl"}
  },
  "entorno": {"DOTNET_CLI_TELEMETRY_OPTOUT": "1"},
  "limites": {"segundos_por_mensaje": 60, "segundos_por_contenedor": 3600, "pids": 1024, "memoria_mb": null}
 },
 "invocacion": {
  "modo": "mensaje",
  "contenedor": "por_grupo",
  "orden": ["dotnet", "/app/Microsoft.Health.Fhir.Liquid.Converter.Tool.dll", "convert",
            "-d", "/tpl", "-r", "{plantilla}", "-n", "{entrada_fichero}", "-f", "{salida_fichero}"],
  "plantilla": {"regla": "msh9_tipo_evento", "comprobar_fichero": {"montaje": "plantillas", "patron": "{plantilla}.liquid"}},
  "duracion_stdout": null
 },
 "salida": {
  "fichero": "{base}.json",
  "fichero_error": null,
  "forma": "envuelto",
  "envoltura": {"ruta_bundle": ["FhirResource"], "ruta_estado": ["Status"], "estado_ok": "OK"},
  "codificacion": "utf-8"
 }
}
```

La orden que la herramienta construye para el grupo `ADT_A01` (lo que imprime `--solo-orden`), con `<tin>`/`<tout>` las carpetas
temporales del grupo:

```
docker run --rm --network none --read-only --tmpfs /tmp --cap-drop ALL --security-opt no-new-privileges
  --user 65534:65534 -e HOME=/tmp --pids-limit 1024 --name vc-microsoft-1
  -e DOTNET_CLI_TELEMETRY_OPTOUT=1
  -v <ms/out>:/app:ro -v <ms/src/data/Templates/Hl7v2>:/tpl:ro -v <tin>:/in:ro -v <tout>:/salida
  mcr.microsoft.com/dotnet/runtime:6.0
  sh -c 'for f in /in/*.hl7; do b=$(basename "$f" .hl7); dotnet /app/Microsoft.Health.Fhir.Liquid.Converter.Tool.dll convert -d /tpl -r ADT_A01 -n "$f" -f "/salida/$b.json" > "/salida/$b.log" 2>&1; echo $? > "/salida/$b.rc"; done'
```

Es la de `correr_conversor.py` con tres añadidos que no cambian el conversor: `--pids-limit`, `--name` y el orden de los `-e`.
En el bucle, `{entrada_fichero}` pasa a `"$f"`, `{base}` a `"$b"` y `{salida_fichero}` a `"/salida/$b.json"`; la herramienta
escapa cada argumento con `shlex.quote` antes de sustituir y nunca interpreta el contenido del mensaje.

### 2.5 Adaptador de ejemplo: LinuxForHealth hl7v2-fhir-converter v1.1.0

Reproduce `correr_conversor.correr_lfh`: un contenedor para toda la carpeta, el arnés `Arnes` (`cv/lfh/Arnes.java`, compilado en
`lfh/clases/`) escribe `<nombre>.json` o `<nombre>.error` e imprime `<nombre> <ms> ms` por mensaje. El comodín `/lib2/*` lo
expande la JVM, no un shell.

```json
{
 "formato": "adaptador-vc/1",
 "id": "linuxforhealth",
 "_que": "LinuxForHealth hl7v2-fhir-converter v1.1.0, el jar de Maven Central y sus 77 dependencias (cv/lfh/pom.xml, DV-CV-3), con el arnés cv/lfh/Arnes.java; corre en la imagen de Maven con Temurin 11 sin red.",
 "conversor": {
  "nombre": "linuxforhealth-hl7v2-fhir-converter",
  "version": "v1.1.0 (Maven Central; DV-CV-3)",
  "huella": {"partes": [{"carpeta": "lib"}, {"fichero": "lfh/Arnes.java"}]},
  "_huella_esperada": "ac41f71b98ee75bac637ecd4b68f58b463f0798bf66cfa941f4194cb2a50acf2 (cv/PREVISION-CV2.json)",
  "declara": {"no_soporta": ["ADT^A02", "ADT^A11", "ADT^A13"]},
  "_declara": "README.md:7-26 del proyecto (L-4 de CLASES-CV3.json); el juez sigue diciendo rechazo_incorrecto (Q-CV-D-13)"
 },
 "caja": {
  "tipo": "docker",
  "imagen": "maven:3.9-eclipse-temurin-11",
  "imagen_digest": null,
  "_imagen_digest": "el estudio corrió con sha256:7bb84a45… (cv/CV1.md)",
  "montajes": {
   "lib":    {"origen": "lfh/lib",    "destino": "/lib2"},
   "clases": {"origen": "lfh/clases", "destino": "/clases"}
  },
  "entorno": {},
  "limites": {"segundos_por_mensaje": 60, "segundos_por_contenedor": 3600, "pids": 1024, "memoria_mb": null}
 },
 "invocacion": {
  "modo": "lote",
  "orden": ["java", "-cp", "/clases:/lib2/*", "Arnes", "{entrada_dir}", "{salida_dir}"],
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

Orden construida:

```
docker run --rm --network none --read-only --tmpfs /tmp --cap-drop ALL --security-opt no-new-privileges
  --user 65534:65534 -e HOME=/tmp --pids-limit 1024 --name vc-linuxforhealth-1
  -v <lfh/lib>:/lib2:ro -v <lfh/clases>:/clases:ro -v <tin>:/in:ro -v <tout>:/salida
  maven:3.9-eclipse-temurin-11 java -cp /clases:/lib2/* Arnes /in /salida
```

**Para las ramas principales (15a)** valen los mismos dos adaptadores cambiando `version`, los orígenes (`ms-main/`, `lfh-main/`)
y, en Microsoft, `imagen` a `mcr.microsoft.com/dotnet/runtime:8.0`: es lo que hacía `CV_VARIANTE=main`.

### 2.6 Adaptador del conversor de juguete (para las pruebas)

```json
{
 "formato": "adaptador-vc/1", "id": "juguete",
 "conversor": {"nombre": "juguete-laboratorio", "version": "1", "huella": {"partes": [{"fichero": "conversor_juguete.py"}]}},
 "caja": {"tipo": "proceso_local", "montajes": {}, "entorno": {}, "limites": {"segundos_por_mensaje": 5, "segundos_por_contenedor": 60, "pids": 64, "memoria_mb": null}},
 "invocacion": {"modo": "lote", "orden": ["python3", "conversor_juguete.py", "{entrada_dir}", "{salida_dir}"], "plantilla": null, "duracion_stdout": null},
 "salida": {"fichero": "{base}.json", "fichero_error": "{base}.error", "forma": "bundle", "envoltura": null, "codificacion": "utf-8"}
}
```

Con `--artefactos` apuntando a `verificador/cv/`. Las pruebas lo derivan en memoria (`modo: mensaje`, `forma: envuelto`…) para
cada escenario; en `proceso_local`, `{entrada_dir}` y `{salida_dir}` son las carpetas temporales reales y no hay montajes.

---

## 3. La orden y sus pasos

```
python3 cv/verificar_conversor.py <adaptador.json> <salida> [opciones]       # desde verificador/
```

| Opción | Qué hace | Por omisión |
|---|---|---|
| `--artefactos <carpeta>` | Base de las rutas relativas del adaptador (o `VC_ARTEFACTOS`) | la carpeta del adaptador |
| `--corpus <carpeta>` (repetible) | Mensajes propios (`*.hl7`, cualquier salto de línea, BOM tolerado) → corpus `propio` | ninguno |
| `--muestras <carpeta>` | Las muestras públicas de los proyectos, como en `corpus_cv2.py` (`ms/`, `lfh/`) → corpus `muestras` | ninguno |
| `--sin-corpus-lab` | No genera `adt/` ni `oru/` | se generan |
| `--sin-minimos` | No genera ni juzga los 68 mínimos (Q-VC-D-3) | se juzgan |
| `--sin-sensibilidad` | No calcula las alternativas de Q-CV-D-3/5/9 | se calculan |
| `--limite-casos N` | Solo los N primeros de cada corpus (humo) | todos |
| `--solo-orden` | Valida, calcula la huella, genera el corpus, imprime la orden Docker del primer grupo y sale con 0 sin correr nada | — |
| `--desde-evidencias` | No corre: juzga `<salida>/evidencias/` tal como está y rehace juicio, agregados e informe | — |
| `--comparar <detalle.jsonl>` | Tras juzgar, compara caso por caso con otro `juicio.jsonl` (el del estudio o el de otra corrida) y escribe `CONTROL.json`; sale con 5 si hay diferencias | — |
| `--json-solo` | No escribe `INFORME.md` | se escribe |

**Los pasos, en orden.** Cada uno imprime una línea `[n/9] …` y para en el primero que falla con su código de salida.

1. **Leer y validar el adaptador** (§2.1). Se copia normalizado (sin claves `_`) a `<salida>/ADAPTADOR.json`. Falla → `2`.
2. **Comprobar la caja.** `docker`: `shutil.which("docker")`, `docker version --format '{{.Server.Version}}'`,
   `docker image inspect --format '{{index .RepoDigests 0}}' <imagen>`; si falta algo → `3` con el remedio (`docker pull <imagen>`,
   que corre el usuario, no la herramienta). Si `imagen_digest` viene y no coincide → `3`. `proceso_local`: la comprobación de
   S-VC-4. Con `--desde-evidencias` se salta.
3. **Calcular la huella** (§2.2) y escribir `CORRIDA.json` (juez: `mcp_verificador._version()`; conversor; imagen y digest;
   herramienta: versión y sha256 de `verificar_conversor.py`; fecha; límites; orden tipo de la caja con los montajes como
   `<nombre>:<destino>:ro`, sin rutas de máquina). Se completa al final con las duraciones.
4. **Generar el corpus** en `<salida>/corpus/`: `adt/` (263: `bases_adt/bases_e2.json` + `a1/ejemplos_cap3.json` +
   `a1/bases_a1.json`, nombre `<id>.hl7`), `oru/` (40: la lista de bases de `bases_oru.py` —la función que usa `escribir()`—,
   nombre `ORU-B<nn>.hl7`), `minimos/` (68: `cv3_minimos.PARES`, nombre `<id>-caso|control.hl7`), `propio/` y `muestras/` si
   se piden. Normalización DV-CV-10: `re.sub(r"\r\n|\n|\r", "\r", t.lstrip("﻿").strip()) + "\r"`. Un fichero sin MSH
   legible va a `no_juzgado/sin_msh`; un MSH-9.1 que no sea ADT ni ORU se juzga igual (S-VC-22) y el juez lo apartará. Se
   escribe `corpus/MANIFIESTO.txt` (líneas `<sha256>  <corpus>/<fichero>`, en el orden `adt, oru, muestras, minimos, propio`) y
   la huella global como en `corpus_cv2.py` (sha256 de la concatenación de las huellas en ese orden; con solo `adt`+`oru`+`muestras`
   debe dar `aa83359a…`).
5. **Correr en la caja.** Por corpus y por grupo (§2.3): carpeta temporal de entrada (`0o755`, ficheros `0o644`) y de salida
   (`0o777`), orden de §2.4/§2.5, `subprocess.run(..., capture_output=True, text=True, timeout=T)` con
   `T = min(segundos_por_contenedor, segundos_por_mensaje × n + 30)`; al vencer, `docker kill <nombre>` (S-VC-20) y, si
   Q-VC-D-9 lo decide, los mensajes del grupo sin salida se reintentan una vez uno a uno. Cada contenedor deja
   `cajas/<corpus>-<grupo>.log` (stdout+stderr) y `.rc`. Un grupo con fallo de caja (§2.3 última fila) no para la corrida:
   se anota y al final se sale con `4`.
6. **Escribir las evidencias** en `evidencias/<id>/<corpus>/<caso>.json`, una por mensaje, con la forma de S-VC-5; antes de
   escribir cada una se valida con `mcp_verificador.validar(e["conversion"], E_PROPS["conversion"])` (un fallo aquí es error
   interno, `1`). La disposición `<id>/<corpus>/<caso>` es la que leen `cv/juzgar_cv2.py` y `cv/cv3_clases.py`, para que el
   control pueda pasarlos por los scripts del estudio sin tocarlos.
7. **Juzgar**: por cada evidencia, `V.verificar(e)` y, salvo `--sin-sensibilidad`, `CV.verificar(e, PE.resolver(None, e),
   CV.con_alternativas(q))` por cada `q` de `CV.ALTERNATIVA`. Una fila por caso en `juicio.jsonl` (S-VC-11); a cada hallazgo que
   cuenta se le añaden `ruta`, `firma` y `clase8` (§4.2).
8. **Agregar**: `INFORME.json` (§4). Los mínimos se evalúan por pares: `reproduce = sale(caso) and not sale(control)` con la
   regla exacta de `cv3_minimos.juzgar` (mismo `hecho`, el `texto` objetivo dentro de algún `que`; para los pares `R0n`, `sale`
   es `estado != "bundle"`).
9. **El informe**: `INFORME.md` desde `INFORME.json`, y la línea final por stdout:
   `verificar_conversor <id> · juez <huella12> · <n> mensajes · juzgados <k> · no juzgados <j> · INFORME en <salida>/INFORME.md`.

Disposición de `<salida>/`:

```
ADAPTADOR.json  CORRIDA.json  corpus/{adt,oru,minimos,propio,muestras}/*.hl7  corpus/MANIFIESTO.txt
cajas/*.log *.rc  evidencias/<id>/<corpus>/<caso>.json  juicio.jsonl  INFORME.json  INFORME.md  [CONTROL.json]
```

---

## 4. El informe

### 4.1 `INFORME.json` (determinista, S-VC-14)

```
{
 "herramienta": {"nombre": "verificar_conversor", "version": "1.0", "huella": "<sha256 del script>"},
 "juez":        {"huella": "<64 hex>", "servidor": "1.2", "revision": "<texto de mcp_verificador>"},
 "conversor":   {"id", "nombre", "version", "huella", "imagen", "imagen_digest"},
 "corpus":      {"huella": "<64 hex>", "n": {"adt": 263, "oru": 40, "minimos": 68, "propio": 0, "muestras": 0}},
 "caja":        {"tipo": "docker", "restricciones": ["--network none", "--read-only", "--tmpfs /tmp", "--cap-drop ALL",
                 "--security-opt no-new-privileges", "--user 65534:65534", "--pids-limit 1024"], "limites": {…}},
 "por_familia": {"adt": {"n", "estados": {bundle, error, vacio, sin_respuesta}, "categorias": {correcto, fallo_silencioso,
                 rechazo_incorrecto, indeterminado, fuera_de_alcance}, "porcentajes": {…}}, "oru": {…}},
 "mecanismos":  {"valor_distinto": [FILA…], "dato_perdido": [...], "dato_inventado": [...], "codigo_mal_mapeado": [...],
                 "valor_imposible_convertido": [...], "recurso": [...], "referencia_rota": [...], "fhir_invalido": [...]},
 "rechazos":    {"incorrectos": [{"firma_texto", "n", "ejemplo": {"caso", "texto"}, "declarado_por_adaptador": false}],
                 "aceptables": {"n", "por_motivo": {"PID-8": n, "PID-7": n, "OBX-5": n, "sin PID": n, …}}},
 "convenciones": {"n": C, "detalle": [{"hecho", "firma", "n"}]},
 "pares_minimos": {"n": 34, "reproducidos": k, "detalle": [{"id", "para_conversor", "objetivo": {hecho, subtipo, texto},
                   "caso": {"estado", "categoria", "sale", "que": [≤2]}, "control": {…}, "reproduce": bool}]},
 "no_juzgado":  {"fuera_de_alcance": [{"caso", "msh9"}], "indeterminado": {"sin_salida": [casos], "lectura": [casos],
                 "emparejamiento": [casos]}, "sin_evidencia": [{"corpus", "grupo", "casos": [...], "motivo"}],
                 "sin_msh": [ficheros], "muestras": "no disponibles" | "n = 65"},
 "sensibilidad": {"Q-CV-D-3": {"fallo_silencioso_con_jev": n, "con_alternativa": n}, "Q-CV-D-5": {…}, "Q-CV-D-9": {…}},
 "contraste_con_el_proyecto": {"hecho": false, "texto": "<la frase fija de §4.3>"},
 "limites": ["L-CV-1", …, "L-CV-16", "L-VC-1", …]
}
```

`FILA` de un mecanismo: `{"hecho": "OBX-5", "ruta": "Observation.valueQuantity.value", "firma": "<cv3_mecanismos.firma>",
"n": casos, "familias": {"adt": n, "oru": n}, "ejemplo": {"caso": "ORU-B29", "que": "<texto entero>"}, "citas": ["[CM …]",
"[G …]"], "clase_cv": "sin_contraste"}`. Las filas van ordenadas por `n` descendente y luego por `hecho`.

### 4.2 Las ocho clases y cómo se asigna cada hallazgo

`clase8(subtipo)`: se parte el subtipo por `+` y cada pieza va a su clase: `valor_distinto`, `dato_perdido`, `dato_inventado`,
`codigo_mal_mapeado`, `valor_imposible_convertido`, `recurso` (= `recurso_ausente`, `recurso_duplicado`, `recurso_inventado`),
`referencia_rota`, `fhir_invalido`. Un hallazgo con subtipo compuesto aparece en cada clase de sus piezas (se dice en el
informe: «un hallazgo puede estar en dos clases; los casos no se suman entre clases»). La clase `rechazo/incorrecto` no es de las
ocho y va a `rechazos`; `rechazo/aceptable` a `rechazos.aceptables`. El `hecho` se normaliza quitando el índice de ocurrencia
(`OBX(2)-3` → `OBX-3`), como hace `conversion._cit`.

### 4.3 `INFORME.md`

Secciones, en este orden, con las mismas cifras que el JSON:

1. **Cabecera**: conversor (nombre, versión, huella, imagen y digest), juez (huella, servidor), corpus (n por corpus, huella),
   caja (las siete restricciones y los límites), herramienta.
2. **Lo que esta herramienta no puede saber** (antes de los resultados, no al final): la frase fija
   > «Este informe dice qué hallazgos ve el juez y con qué cita. **No dice si el proyecto del conversor ya los tiene
   > declarados** (salidas esperadas, pruebas, documentación o issues): ese contraste lo hace una persona, como en
   > `cv/RESULTADO-CV3.md`, y hasta entonces ningún mecanismo de aquí es «nuevo» ni «confirmado». De las cuatro condiciones del
   > estudio, la herramienta comprueba tres (cita, clase, par mínimo) y deja la cuarta sin hacer.»
3. **Categorías por familia**: la tabla de `por_familia`, con `n`, estados y categorías en número y porcentaje.
4. **Mecanismos que cuentan, por clase**: una tabla por clase (hecho, ruta, n, familias, ejemplo con su `que`, citas, y la
   columna `contraste` siempre «sin hacer»); las clases vacías se listan con «ninguno».
5. **Rechazos**: incorrectos por firma de texto, con `n` y ejemplo, separando los que el adaptador declara no soportar
   (Q-VC-D-8) con la nota «el juez los cuenta igual (Q-CV-D-13)»; y los aceptables (Q-CV-D-7) con su motivo.
6. **Pares mínimos del laboratorio**: «34 sondas escritas en el estudio para Microsoft y LinuxForHealth (`cv/cv3_minimos.py`);
   un par que se reproduce aquí quiere decir que este conversor muestra el mismo mecanismo; uno que no, nada más que eso». Tabla:
   id, para qué conversor se escribió, objetivo, caso (estado/categoría/sale), control, reproduce.
7. **Lo que no se juzgó**: cada lista de `no_juzgado` con sus casos; los totales cuadran: `n corpus = juzgados + no juzgados`.
8. **Sensibilidad**: las tres filas.
9. **Convenciones**: C y el detalle.
10. **Límites**: L-CV-1..16 por su clave y L-VC-1..n con su texto.
11. **Cómo repetir**: la orden exacta (`python3 cv/verificar_conversor.py …`) y la orden Docker tipo.

Prohibiciones comprobadas por `comprobar_informe()` (P-VC-19): el texto no contiene «nueva», «nuevas», «confirmada(s)» ni
«ya declarada(s)» fuera de la frase fija de la sección 2; no contiene la frase del estudio («discrepancias nuevas y confirmadas»);
no contiene rutas de máquina.

---

## 5. El conversor de juguete y las pruebas

### 5.1 `cv/conversor_juguete.py`

Del laboratorio; es el accesorio de las pruebas, no el código bajo prueba, y se escribe **con** las pruebas. Dos formas de
llamada: `python3 conversor_juguete.py <entrada_dir> <salida_dir>` (lote) y `python3 conversor_juguete.py --fichero <in>
--salida <out>` (mensaje). Por cada `.hl7` lee MSH-3 (aplicación emisora) como **directiva** y MSH-10 como clave:

| MSH-3 | Hace |
|---|---|
| `JUGUETE` | Escribe `<base>.json` con el Bundle: si MSH-10 está en su tabla (`A01-NOMINAL`, `ORU-NOMINAL`, `M01c`, `M01k`, `L02c`, `L02k`), el Bundle escrito a mano para ese mensaje (el nominal A01 es el `adt_bundle()` de `prueba_conversion.py` copiado, no importado; `M01c` lleva `"value":5`, `M01k` `"value":0.5`; `L02c` `maritalStatus` v3 «A», `L02k` «M»); si no, un Bundle genérico Patient+Encounter (o Patient+DiagnosticReport+Observation) con PID-3.1, PID-5, PID-7, PID-8 (mapa 0001 escrito a mano), PV1-19, PV1-2 (E/I/O/P → EMER/IMP/AMB/PRENC) |
| `JUGUETE-GENERO` | Como `JUGUETE` con `gender` cambiado a `male` |
| `JUGUETE-ERROR` | Escribe `<base>.error` con una traza de tres líneas y nada más |
| `JUGUETE-NADA` | No escribe nada y sigue (el proceso termina con 0) |
| `JUGUETE-RC3` | No escribe nada y el proceso termina con 3 (en lote, tras procesar los demás) |
| `JUGUETE-LENTO` | Duerme los segundos de MSH-4 (por omisión 5) antes de escribir el Bundle nominal |
| `JUGUETE-ENVUELTO` | Escribe `{"Status": "OK", "FhirResource": <Bundle>}` con un `"value":1.20` literal dentro |
| `JUGUETE-ENVUELTO-FALLO` | Escribe `{"Status": "Fail", "Error": "sin plantilla para X"}` |
| `JUGUETE-GRANDE` | El Bundle nominal con un `text.div` de relleno hasta pasar de 4.000.000 caracteres |
| `JUGUETE-ILEGIBLE` | Escribe `<base>.json` con texto que no es JSON |

Imprime `<nombre> <ms> ms` por mensaje (para probar `duracion_stdout`). Deterministas todos. No importa `conversion` ni
ningún módulo del juez.

### 5.2 `cv/prueba_vc.py`: P-VC-1..26

Mismo estilo que `prueba_conversion.py`: `mira(nombre, obtenido, esperado)`, una función por prueba, `python3 cv/prueba_vc.py`
termina en `PRUEBAS VC: TODO BIEN (<n> comprobaciones, 26 pruebas)` y `python3 cv/prueba_vc.py rojo` sale con 0 solo si fallan
las 26. **En rojo, antes del código, fallan todas por la misma razón prevista:** `import verificar_conversor as VC` lanza
`ModuleNotFoundError` (el fichero no existe); el juguete sí existe, porque se escribe con las pruebas. Las pruebas corren sin
Docker: usan `caja.tipo = proceso_local` (el juguete) y, para Docker, las funciones puras `VC.orden_caja(adaptador, grupo)`,
`VC.orden_matar(nombre)` y un `EjecutorEspia` que registra las órdenes sin ejecutarlas. Cada prueba cambia una sola cosa y
lleva su control negativo.

| Id | Qué comprueba | Control negativo | Rojo antes del código |
|---|---|---|---|
| P-VC-1 | `leer_adaptador` acepta el del juguete (§2.6), ignora las claves `_` y rellena los valores por omisión (`codificacion`, `duracion_stdout`, `plantilla`) | Sin `conversor.nombre` → `ErrorEntrada` con `campo = "conversor.nombre"` y salida `2` | `ModuleNotFoundError` |
| P-VC-2 | Adaptadores mal formados, uno por código de §2.1: JSON roto; `formato` distinto; `id` con mayúsculas; `caja.imagen` ausente con docker; montaje con destino `/in`; montaje con origen inexistente; `entorno` con `HOME`; `entorno` con nombre `1abc`; `limites.segundos_por_mensaje = 0`; marcador `{foo}`; `modo = lote` con `{base}` en la orden; `modo = mensaje` sin `contenedor`; `{plantilla}` sin regla; `envuelto` sin `ruta_bundle`; clave desconocida `cajita`. Cada uno → su código | Los mismos quince adaptadores corregidos pasan | idem |
| P-VC-3 | `orden_caja` para el adaptador de Microsoft (§2.4) con un grupo `ADT_A01` de dos ficheros: la lista empieza por `docker run` y contiene, **una vez cada una y en este orden**, `--rm`, `--network none`, `--read-only`, `--tmpfs /tmp`, `--cap-drop ALL`, `--security-opt no-new-privileges`, `--user 65534:65534`, `-e HOME=/tmp`, `--pids-limit 1024`, `--name vc-microsoft-1`; cada `-v` de montaje termina en `:ro`; `-v <tin>:/in:ro` y `-v <tout>:/salida` sin `:ro`; la imagen; `sh -c <bucle>` con `-r ADT_A01`, `"$f"`, `"/salida/$b.json"`, `> "/salida/$b.log" 2>&1` y `echo $? > "/salida/$b.rc"` | Un adaptador con `"privilegiado": true` o un montaje `"modo": "rw"` → `clave_desconocida` (no hay campo que relaje la caja); y en la lista no aparece ningún `--network` distinto de `none` ni `--privileged` | idem |
| P-VC-4 | `proceso_local` con `conversor.nombre = "juguete-laboratorio"` y orden `python3 <ruta real de cv/conversor_juguete.py>` → aceptado | `nombre = "acme-conv"` → `proceso_local_solo_juguete`; nombre correcto pero orden a otro `.py` → el mismo código | idem |
| P-VC-5 | `huella` sobre una carpeta temporal con tres ficheros y un fichero suelto: igual a la fórmula de §2.2 calculada a mano en la prueba; igual a `correr_conversor.huella_carpeta` (importada solo aquí) para la parte carpeta | Partes en el otro orden → huella distinta; un byte cambiado en un fichero → distinta; **renombrar** un fichero → igual (L-VC-5, se afirma para que quede escrito) | idem |
| P-VC-6 | `generar_corpus` del laboratorio: 263 + 40 + 68 ficheros; cada línea `adt/…` y `oru/…` de `cv/CORPUS-CV2-MANIFIESTO.txt` (303 de 368) coincide con el sha256 del fichero generado; los 68 mínimos coinciden byte a byte con `cv3_minimos.escribir` en otra carpeta | Si la normalización deja LF (se parchea `normal` en la prueba), 0 líneas coinciden; `--sin-minimos` → 303 ficheros | idem |
| P-VC-7 | `--corpus` con tres ficheros (uno con CRLF y BOM, uno con LF, uno sin MSH): los dos primeros quedan en `propio/` con CR y sin BOM y punto `adt_conv`/`oru_conv` por MSH-9.1; el tercero en `no_juzgado.sin_msh` | Un `SIU^S12` queda en `propio/` con `adt_conv` y el juez lo pone en `fuera_de_alcance` (S-VC-22) | idem |
| P-VC-8 | `plantilla(texto, regla)`: `msh9_tipo_evento` da `ADT_A01` para `ADT^A01^ADT_A01`, `ORU_R01` para `ORU^R01`, `ADT_A01` con separadores `#$%*!` (DV-CV-12), mayúsculas desde `adt^a01`; `msh9_tipo` da `ADT`; `fija` da `valor`. Igual que `correr_conversor.plantilla` (importada solo aquí) sobre los mismos textos. Con `comprobar_fichero` y una carpeta temporal sin `ADT_A05.liquid`, un A05 da `error/sin_plantilla` **sin llamar al ejecutor** (`EjecutorEspia.llamadas == []`) | Con el fichero presente, el ejecutor sí se llama | idem |
| P-VC-9 | Agrupación: tres mensajes (dos `ADT_A01`, un `ORU_R01`) en `mensaje/por_grupo` → dos grupos en orden alfabético, un bucle por grupo, `.rc` y `.log` por mensaje | `por_mensaje` → tres órdenes, sin `sh -c`; `lote` → una | idem |
| P-VC-10 | Juguete nominal en `lote` (EjecutorLocal): tres evidencias con la forma de S-VC-5, que pasan `mcp_verificador.validar(…, E_PROPS["conversion"])`; `estado = bundle`; `punto_entrada` correcto; `perfil_valor = guia`; `conversor.invocacion` sin rutas de máquina; el nominal A01 da `("correcto", None)` por `V.verificar` | `JUGUETE-GENERO` → `fallo_silencioso/convertido` con `[("fidelidad", "valor_distinto", "PID-8")]` | idem |
| P-VC-11 | `JUGUETE-ERROR` → `error`, `codigo = "excepcion"`, `texto` ≤ 4000 con la traza; juicio `rechazo_incorrecto/error`. En `mensaje/por_mensaje`, `JUGUETE-RC3` → `error`, `codigo = "3"`, `texto` = cola de stdout+stderr | El nominal del mismo lote → `bundle`; un mensaje con PID-8 `Z` y `JUGUETE-ERROR` → `correcto` con nota `rechazo/aceptable` (Q-CV-D-7: el juez decide, no la herramienta) | idem |
| P-VC-12 | `JUGUETE-NADA` en lote (proceso termina 0) → `vacio`; juicio `indeterminado/sin_salida` | `JUGUETE-RC3` en lote (sin fichero, proceso 3, sin registro por mensaje) → `sin_respuesta`, `codigo = "3"`; un proceso matado por la prueba (`SIGKILL` desde el ejecutor) → `sin_respuesta` | idem |
| P-VC-13 | `JUGUETE-LENTO` (MSH-4 = 5) con `segundos_por_mensaje = 1` → `sin_respuesta/timeout`; el proceso está muerto al volver (`poll() is not None`); la corrida tarda < 3 s. Para Docker: `orden_matar("vc-x-1") == ["docker", "kill", "vc-x-1"]` y `EjecutorEspia` recibe la orden de matar tras un timeout simulado | Con `segundos_por_mensaje = 10` → `bundle` | idem |
| P-VC-14 | `JUGUETE-ENVUELTO` con `forma = envuelto` → `bundle` es el recorte textual: contiene `"value":1.20` literal y `json.loads(bundle)["resourceType"] == "Bundle"`; **y es distinto** de `json.dumps(json.loads(fichero)["FhirResource"])`, que lleva `1.2` | `JUGUETE-ENVUELTO-FALLO` → `error`, `codigo = "Fail"`, `texto` = el JSON; `forma = bundle` sobre el envuelto → el juez dice `indeterminado/lectura` («ni Bundle ni recurso proyectado») | idem |
| P-VC-15 | `JUGUETE-GRANDE` → `error/demasiado_grande` con `texto = "<n> caracteres"` | Un Bundle de 3.999.999 caracteres → `bundle` | idem |
| P-VC-16 | Agregación sobre un lote de seis mensajes con verdictos conocidos (nominal, GENERO, ERROR, NADA, un A05, un ORU nominal): `por_familia.adt.categorias == {correcto: 1, fallo_silencioso: 1, rechazo_incorrecto: 1, indeterminado: 1, fuera_de_alcance: 1}`, `oru == {correcto: 1}`; `mecanismos.valor_distinto` tiene una fila con `hecho = PID-8`, `n = 1`, `citas` no vacías y `clase_cv = sin_contraste`; las otras siete clases vacías | Cambiar GENERO por nominal mueve el 1 de `valor_distinto` a `correcto` | idem |
| P-VC-17 | Pares: con el juguete sobre los 68 mínimos, `M01-nm-punto-inicial.reproduce == True` (el juguete escribe 5 en `M01c` y 0.5 en `M01k`) y `L02-estado-civil-a.reproduce == True`; los otros 32, `False`; `pares_minimos.n == 34`, `reproducidos == 2`; `para_conversor` viene de `PARES` | Si el juguete escribiera 5 también en `M01k` (directiva en la prueba), `reproduce == False` (caso sí **y** control sí no reproduce) | idem |
| P-VC-18 | `no_juzgado`: el A05 en `fuera_de_alcance` con su `msh9`; NADA en `indeterminado.sin_salida`; un grupo cuyo ejecutor lanza `CajaNoDisponible` queda en `sin_evidencia` con sus casos y `motivo`; la corrida sale con `4`; `n corpus == juzgados + no juzgados` | Sin el fallo de caja, `sin_evidencia == []` y salida `0` | idem |
| P-VC-19 | `comprobar_informe(md, json)`: `contraste_con_el_proyecto.hecho is False`; todas las filas `clase_cv == "sin_contraste"`; el `.md` contiene la frase fija de §4.3 y ninguna otra aparición de «nueva(s)», «confirmada(s)», «ya declarada(s)» ni «discrepancias nuevas y confirmadas»; ninguna ruta absoluta de máquina | Un informe falso con «3 discrepancias nuevas y confirmadas» → `comprobar_informe` falla con el texto encontrado | idem |
| P-VC-20 | Determinismo: dos corridas del mismo lote en carpetas distintas → `INFORME.json` iguales byte a byte y `juicio.jsonl` iguales; `CORRIDA.json` difiere solo en `fecha`, `duraciones` y rutas | Cambiar `conversor.version` → `INFORME.json` difiere solo en `conversor.version` | idem |
| P-VC-21 | `--solo-orden` con el adaptador de Microsoft y `--artefactos` a una carpeta temporal con las dos carpetas vacías: imprime la orden de §2.4, no llama al ejecutor, no escribe `evidencias/`, sale `0` | Sin la opción, el ejecutor espía recibe llamadas | idem |
| P-VC-22 | `--desde-evidencias` sobre la carpeta de P-VC-16: mismo `INFORME.json` sin volver a correr (ejecutor no llamado) | Carpeta sin `evidencias/` → mensaje claro y salida `1` | idem |
| P-VC-23 | Caja no disponible: con un `docker` falso en `PATH` (script que sale 1 en `image inspect`) → salida `3`, texto con `docker pull <imagen>`, nada en `evidencias/`; con `PATH` sin `docker` → `3` | El `docker` falso que contesta un digest a `image inspect` y `version` → pasa el paso 2 y `CORRIDA.json` lleva el digest | idem |
| P-VC-24 | `--comparar` con un `juicio.jsonl` de referencia igual → `CONTROL.json` con `diferencias == []` y salida `0`; se compara `(estado, categoria, subtipo, {(hecho, clase, subtipo)})` por `(conversor, corpus, caso)` | Cambiar un `subtipo` en la referencia → una diferencia con los dos valores y salida `5`; un caso que falta en la referencia → `solo_en_corrida` | idem |
| P-VC-25 | Los dos adaptadores publicados (`cv/adaptadores/microsoft.json`, `linuxforhealth.json`) validan; `orden_caja` de cada uno reproduce la invocación de `correr_conversor.py`: mismos destinos (`/app`, `/tpl` / `/lib2`, `/clases`), misma imagen, misma orden del conversor, y las siete restricciones | El de LinuxForHealth cambiado a `modo = mensaje` produce otra orden (`{entrada_fichero}` en vez de `/in`) | idem |
| P-VC-26 | Entorno: `DOTNET_CLI_TELEMETRY_OPTOUT=1` aparece como `-e`; `HOME=/tmp` aparece aunque el adaptador no lo diga; `entorno` con `HOME` → `entorno_reservado` | Un valor con comillas y espacios pasa entero como un solo argumento (sin shell) | idem |

Comprobaciones previstas: unas 140. Añadidos al README de `verificador/`: la fila `python3 cv/prueba_vc.py` →
`PRUEBAS VC: TODO BIEN (… comprobaciones, 26 pruebas)`.

---

## 6. El control con los dos conversores reales (VC3)

**Qué se necesita** (todo en la máquina del laboratorio; nada se descarga durante el control): Docker; los artefactos de CV1
(`ms/out`, `ms/src/data/Templates/Hl7v2`, `lfh/lib`, `lfh/clases`, `lfh/Arnes.java`) bajo una carpeta `--artefactos`; las dos
imágenes ya presentes; las muestras de los proyectos (`--muestras`); el detalle privado del rejuicio del corpus con el juez de CV4
(`40bbc3ef`; `RESULTADO-CONVERSORES.md` lo cita como `cv/RESULTADO-CV4-rejuicio.json` y su `juicio.jsonl`), y
`cv/RESULTADO-15A-minimos-fijada.json`. Si el detalle de CV4 no está en formato `juicio.jsonl`, se regenera con
`cv/juzgar_cv2.py` sobre las evidencias guardadas del estudio y el juez de hoy, antes de correr la herramienta.

**Orden de los pasos** (el eslabón débil primero):

0. **La caja, con el juguete dentro de Docker.** Adaptador del juguete con `caja.tipo = docker`, `imagen = python:3.12-slim`,
   montaje `cv/` → `/juguete:ro`, orden `python3 /juguete/conversor_juguete.py /in /salida`. Los seis mensajes de P-VC-16 deben
   dar los mismos verdictos que con `proceso_local`. Si no, la caja altera al juguete y se para aquí hasta entender por qué.
1. **Identidades, antes de correr nada.** `--solo-orden` con cada adaptador: la huella de Microsoft es
   `766f8938…` y la de LinuxForHealth `ac41f71b…` (las de `cv/PREVISION-CV2.json`); la huella del juez es `40bbc3ef…`; las 303
   líneas `adt/`+`oru/` y las 65 `muestras/` del manifiesto generado coinciden con `cv/CORPUS-CV2-MANIFIESTO.txt` y la huella
   global es `aa83359a…`. Una identidad que no cuadra para el control: no se corre con un artefacto, un corpus o un juez
   distintos de los del estudio.
2. **Correr** los dos adaptadores con `--muestras` y `--comparar <juicio CV4>.jsonl`. Tope: dos horas de máquina por conversor
   (el estudio tardó minutos en las muestras; el corpus entero no está medido en público).
3. **Comparar caso por caso.** `CONTROL.json` lista, por `(conversor, corpus, caso)`, las diferencias en
   `(estado, categoria, subtipo, {(hecho, clase, subtipo)})` (Q-VC-D-7). **Hecho cuando hay 0 diferencias**, o cuando cada
   diferencia está adjudicada a algo que no es la herramienta.
4. **Comprobaciones públicas**, que valen aunque falte el detalle privado:
   - `por_familia` de `adt` y `oru` de cada conversor igual, categoría por categoría, a `cv/RESULTADO-CV2.json`
     (`por_conversor.<cv>.<fam>.categorias`): los cambios de CV4 (`RESULTADO-CONVERSORES.md`) no tocan categorías en esos dos
     corpus. En `muestras`, Microsoft pasa a `correcto: 3, fallo_silencioso: 25` (la muestra LRI); en LinuxForHealth desaparecen
     los dos `Patient.identifier|dato_perdido` de CX.4 y su categoría se adjudica mirando el caso.
   - Los pares mínimos con las versiones fijadas y el juez de CV4: `reproduce` igual a `confirmada` de
     `cv/RESULTADO-CV3-minimos.json` salvo `L16-cx-4-solo-nombre` (ahora `false`: era el falso positivo del juez arreglado en CV4,
     `cv/RESULTADO-15A.md`); es decir, 30 de 34 (`M03b`, `M06c`, `L15`, `L16` en `false`). Con `ms-main`/`lfh-main`, igual a
     `cv/RESULTADO-15A-minimos-main.json` (29 de 34: además `L09`).
   - Pasar `evidencias/` por `cv/juzgar_cv2.py` y `cv/cv3_minimos.py juzgar` (reorganizando los mínimos como esperan esos scripts)
     y obtener los mismos agregados que la herramienta: comprueba la agregación con los scripts del estudio.

**Qué se hace con una diferencia.** Cada una se escribe en `cv/CONTROL-VC.md` con el caso, los dos valores, la causa y la cita,
y se adjudica a una de estas:

| Adjudicación | Cómo se reconoce | Qué se hace |
|---|---|---|
| `arnés del estudio` | `estado` distinto con el mismo fichero de salida del conversor; o un valor que `correr_conversor.py` alteraba (p. ej. la reserialización del Bundle envuelto de Microsoft, `json.loads`+`dumps`, que convierte `1.20` en `1.2`; o el `error/"0"` donde la herramienta dice `vacio`) | La herramienta tiene razón si el fichero bruto la respalda; se declara, y si la diferencia cambia una categoría del estudio publicado, se escribe como errata en `RESULTADO-CONVERSORES.md` con el visto bueno |
| `corpus` | La línea del manifiesto no coincide | Se para y se arregla la generación; no se compara con un corpus distinto |
| `juez` | La huella del juez no es `40bbc3ef` | Se para; el control es con el mismo juez |
| `conversor` | Dos corridas seguidas de la herramienta dan distinto en ese caso | Se declara como no determinista (L-VC-11); no cuenta contra la herramienta |
| `herramienta` | Lo demás | Se escribe la prueba P-VC-n en rojo que lo reproduce, se corrige y se repite el control entero. Bloquea VC4 |

Una diferencia de `duracion_ms`, `plantilla`, `invocacion` o del texto `que` (con el mismo `hecho`, `clase` y `subtipo`) no
es diferencia. Un caso que la herramienta deja en `sin_evidencia` por fallo de la caja se repite antes de adjudicar.

**Lo que el control no puede hacer desde lo público** (L-VC-8): el detalle por caso del estudio está fuera de git; la copia
pública permite las comprobaciones del paso 4 y nada más. `cv/CONTROL-VC.md` lo dice y publica los agregados de la corrida de
control (`INFORME.json` de cada conversor), no el detalle.

---

## 7. Preguntas de diseño para Jev (Q-VC-D-n)

Solo las que no deciden ni la pregunta ni las condiciones. Cada una con sus opciones y, aparte, mi recomendación. Lo que
cambia según la respuesta está en la última columna; el programador implementa la decisión de Jev, no la mía.

| Q | Pregunta | Opciones | Qué cambia |
|---|---|---|---|
| Q-VC-D-1 | ¿Qué fórmula lleva la huella del conversor? | (a) la del estudio (§2.2: sin nombres de fichero; comparable con `766f8938`/`ac41f71b`); (b) con rutas relativas y nombres (más fuerte; no comparable con el estudio); (c) (a) en la evidencia y (b) como `huella_con_nombres` en `CORRIDA.json` e informe | El paso 1 del control (igualdad con las huellas publicadas) solo vale con (a) o (c); L-VC-5 desaparece con (b) |
| Q-VC-D-2 | Un conversor que termina con código 0 sin escribir salida ni error, ¿qué estado da? | (a) `vacio` → el juez dice `indeterminado/sin_salida` (L-CV-8); (b) `error` con `codigo = "0"`, como hacía `correr_conversor.py` para Microsoft → `rechazo_incorrecto` o `correcto` según el mensaje | Con (a) puede aparecer una diferencia `arnés del estudio` en el control; con (b) se hereda la imprecisión |
| Q-VC-D-3 | ¿Se juzgan los 68 mínimos del laboratorio con un conversor que no es Microsoft ni LinuxForHealth? | (a) siempre, en la sección «pares mínimos del laboratorio» con la nota de para quién se escribió cada uno; (b) solo con `--minimos`; (c) solo si `id` es `microsoft` o `linuxforhealth` | Con (b)/(c) el informe de un tercero pierde la tercera condición del estudio (par mínimo) salvo que la pida |
| Q-VC-D-4 | ¿Imagen por etiqueta o por digest? | (a) exigir `imagen_digest` siempre; (b) admitir la etiqueta, resolver el digest local con `docker image inspect` y registrarlo en `CORRIDA.json` e informe; exigir igualdad solo si el adaptador lo declara; (c) admitir la etiqueta y solo avisar | (a) hace reproducible la caja pero obliga al tercero a conocer el digest; con (b) los adaptadores del control llevan el digest y los de un tercero pueden no llevarlo |
| Q-VC-D-5 | ¿Cómo se extrae el Bundle envuelto? | (a) recorte textual por posiciones (S-VC-8: conserva `1.20`, tipos y orden); (b) `json.loads` + `json.dumps` como el arnés del estudio (comparable con el estudio, pierde precisión); (c) `json.loads(parse_float=str)` + `dumps` (los números salen como cadenas) | Con (a), un caso del estudio con un decimal con cero final en un Bundle de Microsoft puede cambiar de veredicto y hay que adjudicarlo como `arnés del estudio`; con (b) se perpetúa un defecto del arnés; (c) oculta números escritos como cadenas |
| Q-VC-D-6 | ¿Límite de memoria por omisión en la caja? | (a) ninguno, como el estudio (`memoria_mb: null`), con `--pids-limit` siempre; (b) 2048 MB; (c) obligatorio declararlo | Con (b), la JVM de LinuxForHealth toma por omisión un cuarto del límite (512 MB) y un OOM daría `sin_respuesta` donde el estudio dio Bundle |
| Q-VC-D-7 | ¿Qué es «el mismo veredicto» en el control? | (a) `categoria` y `subtipo`; (b) además el conjunto de hallazgos que cuentan como `(hecho, clase, subtipo)`; (c) además los textos `que` | (a) deja pasar cambios de mecanismo; (c) falla por redacción (`que` lleva valores) |
| Q-VC-D-8 | Un adaptador que declara `no_soporta` (tipos que el proyecto dice no convertir), ¿cómo se trata? | (a) el juez no cambia (`rechazo_incorrecto`, Q-CV-D-13); el informe separa esos rechazos de los demás; (b) no se admite la clave: nada que el proyecto diga entra en la herramienta; (c) se excluyen del corpus antes de correr | (c) rompería el control (el estudio los corrió y contó 92); (b) hace el informe de LinuxForHealth menos legible |
| Q-VC-D-9 | En `por_grupo`, al vencer el tiempo del contenedor, ¿qué pasa con los mensajes del grupo que no tenían salida? | (a) todos `sin_respuesta/timeout` y se declara (L-VC-6); (b) se reintentan una vez, uno a uno, en `por_mensaje`, con su propio límite | (b) añade una pasada y puede dar un estado distinto al del estudio para el mensaje lento; (a) deja que un mensaje lento arrastre a 100 |

**Mis recomendaciones, aparte:** Q-VC-D-1 (c); Q-VC-D-2 (a); Q-VC-D-3 (a); Q-VC-D-4 (b); Q-VC-D-5 (a); Q-VC-D-6 (a);
Q-VC-D-7 (b); Q-VC-D-8 (a); Q-VC-D-9 (b). Las dos que más pesan son Q-VC-D-5 y Q-VC-D-2, porque son las únicas que pueden
hacer que la herramienta no dé «el mismo juicio» que el estudio, y en las dos la herramienta tendría razón y el arnés del
estudio no. El diseño lo dice en vez de esconderlo detrás de la compatibilidad.

---

## 8. Límites (L-VC-n)

| Id | Límite |
|---|---|
| L-VC-1 | La herramienta no sabe si una discrepancia la tiene declarada el proyecto: no lee salidas esperadas, pruebas, documentación ni issues. La clase nueva / ya declarada / convención la pone una persona (L-CV-10); aquí todo es `sin_contraste`. |
| L-VC-2 | Solo juzga lo que juzgan `adt_conv` y `oru_conv`: ADT de los ocho eventos y ORU^R01. Otro tipo de mensaje entra en el corpus y el juez lo aparta como `fuera_de_alcance`. |
| L-VC-3 | Solo conversores que corran como programa de línea de órdenes dentro de un contenedor Docker, leyendo ficheros y escribiendo ficheros. Un servicio HTTP, una biblioteca que haya que llamar desde código o un conversor que necesite red no caben en el adaptador. |
| L-VC-4 | La imagen debe estar ya en la máquina: la herramienta no descarga nada y no comprueba de dónde salió la imagen; solo registra su digest. |
| L-VC-5 | La huella del conversor con la fórmula del estudio no ve nombres ni rutas de fichero: renombrar o mover ficheros no la cambia (salvo Q-VC-D-1 b/c). |
| L-VC-6 | `vacio` y `sin_respuesta` no distinguen la caja del conversor (L-CV-8). En `por_grupo` y `lote`, el tiempo vencido o la muerte del contenedor afecta a todos los mensajes del grupo sin salida (según Q-VC-D-9). |
| L-VC-7 | Las muestras de los proyectos no viajan con el repositorio: sin `--muestras`, el corpus por omisión son las bases A1/E2, las ORU y los 68 mínimos, todos sintéticos y en v2.5. |
| L-VC-8 | El control caso por caso exige el detalle privado del estudio. Desde la copia pública solo se comprueban las identidades (huellas, manifiesto del corpus), los agregados por categoría y los 68 mínimos. |
| L-VC-9 | Las restricciones de la caja se comprueban en la orden construida, no en el núcleo: un demonio Docker en modo rootless, con `--userns-remap` o con otro runtime puede comportarse distinto y la herramienta no lo detecta. |
| L-VC-10 | `duracion_ms` es aproximado en `por_grupo` y `lote` (tiempo del contenedor entre sus mensajes); la herramienta no mide rendimiento. |
| L-VC-11 | No se comprueba que el conversor sea determinista; una corrida es una corrida. |
| L-VC-12 | Un Bundle de más de 4.000.000 caracteres no se juzga (`error/demasiado_grande`, DV-CV-5). |
| L-VC-13 | Un mensaje sin plantilla disponible (`comprobar_fichero`) se marca `error/sin_plantilla` sin entrar en la caja: no se sabe qué habría dicho el conversor. |
| L-VC-14 | La herramienta hereda las decisiones de Jev (Q-CV-D-1..14), los límites L-CV-1..16 y las ambigüedades del juez; no los cambia ni los expone de otra forma que como los expone `info_verificador`. |
| L-VC-15 | Los 68 mínimos son sondas escritas para dos conversores concretos: que un tercero no reproduzca ninguno no dice que esté bien, y que reproduzca uno no dice que sea una discrepancia confirmada. |

---

## 9. El plan

| Fase | Qué | Hecho cuando | Regla de parada | Tope |
|---|---|---|---|---|
| **VC0** | Este diseño; las Q-VC-D a Jev con el estado neutro | Decisiones escritas en `cv/decision-jev-qvc.md` | — | hecho |
| **VC1, pruebas en rojo** | `cv/conversor_juguete.py` (accesorio) y `cv/prueba_vc.py` con P-VC-1..26 y sus controles; los dos adaptadores publicados en `cv/adaptadores/`; el del juguete | `python3 cv/prueba_vc.py rojo` → `fallan 26 de 26 (TODAS)`, todas por `ModuleNotFoundError: verificar_conversor`; el juguete corre solo y produce lo de §5.1; las suites del juez siguen en verde | Si una prueba no puede escribirse sin Docker, se reescribe sobre `orden_caja`/`EjecutorEspia`; nunca se salta | ½ sesión |
| **VC2, el código** | `cv/verificar_conversor.py`: `leer_adaptador`, `validar_adaptador`, `huella`, `generar_corpus`, `plantilla`, `agrupar`, `orden_caja`, `orden_matar`, `EjecutorDocker`, `EjecutorLocal`, `leer_salida` (con el recorte textual), `evidencia`, `juzgar`, `agregar`, `informe_md`, `comprobar_informe`, `comparar`, `main`; con las decisiones de Jev | `prueba_vc.py` en verde; `ve/comprobar.sh` entero en verde; la huella del juez sigue siendo `40bbc3ef` (`mcp_verificador._version()`); `--solo-orden` imprime §2.4 y §2.5; `python3 -X importtime` no importa nada fuera de la biblioteca estándar y del juez | Si para pasar una prueba hace falta tocar un fichero de la huella, se para: es un defecto del diseño o de la prueba, se escribe como DV-VC-n y se pregunta | 1-2 sesiones |
| **VC3, el control** | §6, en la máquina del laboratorio: el juguete en Docker, identidades, las dos corridas, `CONTROL.json`, `cv/CONTROL-VC.md` | 0 diferencias, o todas adjudicadas a algo que no es la herramienta; las comprobaciones públicas del paso 4 cuadran; cada adjudicación `arnés del estudio` con su fichero bruto citado | El juguete en Docker no da lo mismo que en local → se para la caja; una identidad no cuadra → no se corre; más del 5 % de casos distintos adjudicados a la herramienta → vuelta a VC2 con pruebas nuevas en rojo | 1 sesión |
| **VC4, publicación** | `verificador/README.md` (la fila de `prueba_vc.py`, un apartado «Verifica tu conversor» con la orden y los dos adaptadores), `cv/VC.md` con el resultado del control, `tests/test_repo_hygiene.py` con los `.json` nuevos en `JSON_ADMITIDOS`, `MANIFIESTO.txt` al día, el README principal y el «About» si procede | `antes_de_publicar.py` en LIMPIO; la guarda pública (`pytest tests`) en verde; visto bueno del autor al diff; después, el push | Sin visto bueno no sale nada (condición 6 del ANTES de conversores) | ½ sesión |

**Total previsto:** tres sesiones y media; **tope:** cuatro sesiones, y el calendario lo pone el autor. Desviaciones del diseño
al implementar: `DV-VC-n`, en `cv/VC.md`, cada una con su porqué.

**Los tres riesgos que más me preocupan:**
1. **Que la caja cambie al conversor** (permisos de `/salida`, `HOME`, `--pids-limit`, el shell del bucle): por eso el juguete
   entra en Docker antes que ningún conversor real (paso 0 del control).
2. **Que el estudio arrastrara un defecto de arnés** (la reserialización del Bundle envuelto, el `error/"0"`): la herramienta no
   lo copia, y si eso mueve un veredicto, el control lo dirá y habrá que publicarlo como errata, no esconderlo.
3. **Que el informe se lea como el del estudio**: una tabla de «mecanismos» con sus citas parece una lista de hallazgos
   confirmados. La frase fija va antes de los resultados, `clase_cv` es `sin_contraste` en cada fila y P-VC-19 lo vigila.
