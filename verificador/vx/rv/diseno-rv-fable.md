> *Copia pública: se quitaron las alusiones al autor y a su máquina. El resto es el original del laboratorio.*

# Diseño RV0: el aparato de la etapa 22, las nueve de VXU en las ramas principales

<!-- modelo: Claude Fable 5.1; fecha: 25-oct-2026; a ciegas: leído solo el ANTES de la etapa, un ejemplo de borradores de la etapa anterior y el repositorio público, sobre todo verificador/ -->

**La pregunta fija (del ANTES):** ¿siguen en la rama principal de cada conversor las nueve discrepancias nuevas de VXU y el arrastre de estado de LinuxForHealth? Y, para las que sigan, ¿quedan listos los borradores de issues, contrastados con lo abierto hoy?

**Lo que fija el marco y no se discute:** solo terceros públicos; el código de terceros en la caja de siempre (red solo para construir una rama, como en 15A); el mismo juez a los dos lados (el del laboratorio, `bde94016ca58…` según la cabecera de `MANIFIESTO.txt`; el publicado difiere solo en textos); el aparato se prueba antes (control de las versiones fijadas contra `vx/RESULTADO-VX3-minimos.json`); los issues son del autor y los borradores no se publican; previsión sellada en un commit antes de la primera corrida con una rama principal; `RESULTADO-RAMAS-VXU.md` con la frase fija; tope de una sesión y 1,5 h por construcción; la regla de parada del control.

**Lo leído que condiciona el diseño:** `cv/cv3_minimos_vxu.py` (25 `PARES`, 1 `SECUENCIAS`, `escribir`, `secuencias`, `juzgar`/`_sale`), `vx/RESULTADO-VX3-minimos.json` (juez `11a3754fb8b6`, 25 de 26 confirmadas), `vx/CLASES-VX3.json`, `vx/VX3.md`, `RESULTADO-VXU.md`, `cv/RESULTADO-15A.md` (Microsoft `main` `70fd328` 3-jun-2026, huella `38c6d32b…`, .NET 8; LinuxForHealth `master` `2cb72c2` 11-feb-2026, huella `28c16067…`, Gradle + `copiar-libs.gradle`; artefactos `privado/cv/conversores/{ms-main,lfh-main}/`), `cv/correr_conversor.py` (`CV_VARIANTE=main`), `cv/lfh/{Arnes.java,copiar-libs.gradle,pom.xml}`, `cv/verificar_conversor.py` entero, `cv/adaptadores/*.json` (Microsoft v7.0 huella `766f8938…`, con nombres `1118ff9a…`, imagen `sha256:75752d6e7d17…`; LinuxForHealth v1.1.0 huella `ac41f71b…`, con nombres `7ad4d546…`, imagen `sha256:7bb84a451705…`), `cv/VC.md`, `cv/vc/CONTROL-VC.md`, `vx/VX2.md` (F7), `RESULTADO-ARRASTRE.md`, `cv/ar/{arrastre.py,control_ar.py,prueba_ar.py,sellar_prevision.py,PREVISION-AR.json,SELLO-AR.txt,decisiones-qar.md,diseno-ar-fable.md}`, `tests/test_repo_hygiene.py` (nombres de las guardas), `bases_vxu.py` (B17: RXA-17 `^Laboratorio Sintetico^`).

**Carpeta de la etapa:** `verificador/vx/rv/`. Prefijos: decisiones `S-RV-n`, pruebas `P-RV-n`, preguntas `Q-RV-D-n`, límites `L-RV-n`, desviaciones del programador `DV-RV-n`. Los adaptadores nuevos van en `cv/adaptadores/`, el resultado en `verificador/RESULTADO-RAMAS-VXU.md`, los borradores en `verificador/vx/BORRADORES-ISSUES-VXU.md` (no se publican).

**Un hecho del código que manda sobre varias decisiones:** `cv3_minimos_vxu.juzgar` lee `<evidencias>/<conversor>/<id>-{caso,control}.json` con `<conversor>` ∈ {`microsoft`, `linuxforhealth`}, y para la secuencia `<evidencias>/linuxforhealth/VL11-estado-fabricante-{caso,control}/L11b.json`; pero `secuencias` escribe los ficheros `1-L11a.hl7`, `2-L11b.hl7` (caso) y `1-L11b.hl7` (control), y la herramienta nombra cada evidencia por el nombre base del fichero (`evidencias/<id>/propio/2-L11b.json`). Hace falta un paso que **arme** el árbol que `juzgar` espera (S-RV-6); no se toca `cv3_minimos_vxu.py`.

---

## 1. Las decisiones (S-RV-n)

| Id | Decisión | Por qué, en una línea |
|---|---|---|
| S-RV-1 | Todo corre con `cv/verificar_conversor.py` (la herramienta de la etapa 18), nunca con `correr_conversor.py`: `--sin-corpus-lab --sin-minimos --sin-sensibilidad --json-solo --corpus <carpeta>`; los pares entran como corpus `propio` y van a `vxu_conv` por MSH-9.1 | es la herramienta controlada (0 diferencias en 368 casos, VC3) y la que corrió VX2; `correr_conversor.py` pone `adt_conv`/`oru_conv` y nunca `vxu_conv` |
| S-RV-2 | Las versiones fijadas corren con los adaptadores publicados sin tocarlos: `microsoft.json`, `linuxforhealth.json` (lote) y `linuxforhealth-mensaje.json` | condición 4: el control tiene que ser el aparato de la etapa 20 y 21, no uno nuevo |
| S-RV-3 | Las ramas principales corren con **tres adaptadores nuevos** (§2.2): `microsoft-main.json`, `linuxforhealth-main.json` y `linuxforhealth-main-mensaje.json`, con `id` `microsoft-main` / `linuxforhealth-main`, rutas `ms-main/…` y `lfh-main/…` bajo `--artefactos`, y `conversor.version` con el commit de la rama | los artefactos de 15A ya viven en `ms-main/` y `lfh-main/`; otro `id` impide que entren los 68 mínimos de ADT/ORU (Q-VC-D-3), que aquí no se quieren, y evita confundir corridas al comparar |
| S-RV-4 | **LinuxForHealth: el estado de las nueve se decide mensaje a mensaje** (`linuxforhealth-mensaje.json` / `linuxforhealth-main-mensaje.json`: un proceso Java por mensaje). El lote se corre además como control (Q-RV-D-5) y se compara, pero no decide | un proceso por mensaje no puede arrastrar estado por construcción; es exactamente lo que midió la etapa 21 (S-AR-1) |
| S-RV-5 | **Microsoft** corre como siempre (`por_grupo` con bucle, un proceso `dotnet` por fichero): no hay arrastre posible y no hace falta modo mensaje | L-AR-7: convierte un mensaje por proceso por construcción |
| S-RV-6 | `vx/rv/ramas_vxu.py armar` construye el árbol que `cv3_minimos_vxu.juzgar` espera, copiando `evidencias/<id>/propio/<pid>-{caso,control}.json` a `<evid>/<conversor>/` y `2-L11b.json` → `VL11-estado-fabricante-caso/L11b.json`, `1-L11b.json` → `VL11-estado-fabricante-control/L11b.json`; después llama a `cv3_minimos_vxu.juzgar(evid, salida.json)` tal cual | el juicio de los pares es **literalmente** el de la etapa 20 (mismo módulo, misma `_sale`); solo cambia el transporte |
| S-RV-7 | «**Sigue**» = en la rama, `confirmada: true` por `cv3_minimos_vxu.juzgar` (el objetivo sale en el caso con su hecho, subtipo y texto, y no en el control). «**Corregida**» = caso y control con `estado: bundle`, el objetivo no sale en el caso, y en el caso **no hay ningún hallazgo que cuente con el mismo hecho base** (`re.sub(r"\(\d+\)", "", hecho)`). «**Cambiada**» = el objetivo no sale pero hay otro hallazgo que cuenta en el mismo hecho. «**Par roto**» = el control sale, o algún lado no es `bundle`. K cuenta solo «sigue» (Q-RV-D-1 decide qué se hace con «cambiada») | el criterio de `juzgar` basta para «sigue» (es el que confirmó las nueve); para «corregida» hace falta además que el campo esté bien, no que el síntoma haya cambiado de forma |
| S-RV-8 | El **control** compara `RESULTADO-RV-minimos-fijada-lote.json` con `vx/RESULTADO-VX3-minimos.json` par a par y lado a lado: `confirmada`, y por conversor y lado `sale`, `estado`, `categoria`, `que`; la **única tolerancia** es la clave `juez` (hoy `bde94016…`, allí `11a3754f…`: difieren por textos de `mcp_verificador`, `RESULTADO-VXU.md`). Las diferencias se clasifican `veredicto` (sale/estado/categoria/confirmada) o `texto` (solo `que`); Q-RV-D-4 decide si `texto` bloquea | el ANTES exige «lo mismo» o explicación antes de mirar las ramas; el juez cambió solo en texto y eso se puede comprobar |
| S-RV-9 | El control se corre **en lote y mensaje a mensaje** con LinuxForHealth v1.1.0 (`fijada-lote` reproduce la etapa 20, que corrió en lote; `fijada-mensaje` es el modo que decide en la rama); los dos tienen que dar los mismos 26 veredictos. Si difieren en un par, la diferencia es «contaminación en la etapa 20», se declara, y manda mensaje a mensaje a los dos lados | así el control del aparato vale también como control de que los pares de la etapa 20 no estaban contaminados |
| S-RV-10 | **La secuencia VL11 en `master`** se mide con la lógica de `cv/ar/arrastre.py` sin tocarla: `AR.positivo_sale(lote_caso, mensaje_caso, lote_control)` y `AR.diff_bundles` sobre `2-L11b`; dos repeticiones de lote-caso y mensaje-caso y una de lote-control, como `AR.positivo_vl11`, pero con los adaptadores de la rama (función propia `secuencia_vl11(ad_lote, ad_mensaje, …)`) | «sigue el arrastre» tiene que querer decir lo mismo que «sale» en la etapa 21 |
| S-RV-11 | Las ramas se **reconstruyen solo si** el `compare` de GitHub desde el commit de 15A trae algún fichero de las listas de §4.2; si avanzaron sin tocar VXU se mide con la construcción de 15A y se anota | lo dice el ANTES («si tocan VXU, se reconstruye») y 15A ya lo hizo así |
| S-RV-12 | La **previsión se sella antes de cualquier corrida con Docker de esta etapa** (también antes del control), y antes de consultar GitHub | más estricto que el ANTES, como hizo la etapa 21; así `p_control_reproduce` y `p_rama_avanzo` son previsiones y no lecturas |
| S-RV-13 | El **contraste** se hace sobre la relectura completa de issues y PR (abiertos y cerrados) con sus comentarios, descargada con `gh api` a `privado/vx/rv/proyectos/`, y buscada por **términos de campo y de efecto** (§6.2); «ya reportada» la decide una persona entre los candidatos y queda con número, estado, URL y cita ≤ 15 palabras en `CONTRASTE-RV.json` | es el método de CV3 (DV-CV-18: cuerpos completos y comentarios); la red solo lee |
| S-RV-14 | Un **borrador por discrepancia que sigue y no está reportada**; para una reportada y abierta, un **comentario** al issue; el del arrastre es siempre un comentario al #348; en inglés, con la forma de `BORRADORES-ISSUES-estudio.md` | lo pide el ANTES; el #348 ya existe |
| S-RV-15 | No se cambia `verificar_conversor.py`, `Arnes.java`, `cv3_minimos_vxu.py`, `cv/ar/*.py`, ni ningún fichero de `mcp_verificador.FICHEROS`; todo lo nuevo vive en `vx/rv/` y en los tres adaptadores | el juez y la herramienta controlada tienen que ser los mismos a los dos lados |
| S-RV-16 | Se publican los agregados y los JSON de `vx/rv/` (sin evidencias, Bundles ni `juicio.jsonl`), el resultado y la nota en `RESULTADO-VXU.md`; **no** los borradores ni el volcado de issues | ANTES: «Los borradores no se publican; el resultado, sí»; L-VC-8 |

---

## 2. Cómo se corre

### 2.1 Los mensajes

```bash
# desde verificador/
python3 cv/cv3_minimos_vxu.py escribir    <T>/pares     # 50 .hl7: <pid>-caso.hl7 y <pid>-control.hl7 (CR, sin BOM)
python3 cv/cv3_minimos_vxu.py secuencias  <T>/vl11      # VL11-estado-fabricante-caso/{1-L11a,2-L11b}.hl7 y …-control/1-L11b.hl7
```

Los 25 pares entran juntos en una carpeta: con Microsoft da un contenedor por plantilla (`VXU_V04`) con un `dotnet` por fichero; con LinuxForHealth en lote, un contenedor y un proceso para los 50 (orden alfabético: `VL01-…-caso, VL01-…-control, …, VM15-…-control`); mensaje a mensaje, 50 contenedores. La secuencia va **en su propia carpeta** por lado (caso: 2 ficheros; control: 1) para que el lote sea exactamente «esos dos mensajes en ese orden y nada más».

### 2.2 Los adaptadores nuevos, completos

`cv/adaptadores/microsoft-main.json`:

```json
{
 "formato": "adaptador-vc/1",
 "id": "microsoft-main",
 "_que": "Etapa 22 (vx/rv/): Microsoft FHIR-Converter en su rama principal, construida como en cv/RESULTADO-15A.md (dotnet publish de la herramienta en el SDK de .NET 8); corre en el runtime de .NET 8, sin red, con la misma invocación que microsoft.json (un contenedor por plantilla, un proceso por fichero).",
 "_id": "El id no es el del estudio a propósito: los 68 mínimos de ADT/ORU no entran (Q-VC-D-3) y las corridas de la rama no se confunden con las de v7.0.",
 "_rutas": "Relativas a --artefactos: ms-main/out y ms-main/src/data/Templates/Hl7v2, la construcción de 15A o la reconstruida en esta etapa (vx/rv/RAMAS-RV.json dice cuál).",
 "_version": "La versión lleva el commit corto de la rama y su fecha; ramas_vxu.py identidades exige que coincida con RAMAS-RV.json.",
 "conversor": {
  "nombre": "microsoft-fhir-converter",
  "version": "main (70fd328, 2026-06-03)",
  "huella": {"partes": [{"carpeta": "codigo"}, {"carpeta": "plantillas"}]},
  "_huella_esperada": "si es la construcción de 15A, empieza por 38c6d32b (cv/RESULTADO-15A.md); si se reconstruye, la anota RAMAS-RV.json"
 },
 "caja": {
  "tipo": "docker",
  "imagen": "mcr.microsoft.com/dotnet/runtime:8.0",
  "imagen_digest": null,
  "_imagen_digest": "15A corrió con una imagen cuyo digest empieza por 1b2f288e; la herramienta registra el de la máquina y RAMAS-RV.json lo anota",
  "montajes": {
   "codigo": {"origen": "ms-main/out", "destino": "/app"},
   "plantillas": {"origen": "ms-main/src/data/Templates/Hl7v2", "destino": "/tpl"}
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

`cv/adaptadores/linuxforhealth-main.json`:

```json
{
 "formato": "adaptador-vc/1",
 "id": "linuxforhealth-main",
 "_que": "Etapa 22 (vx/rv/): LinuxForHealth hl7v2-fhir-converter en su rama principal (master), construida con Gradle como en cv/RESULTADO-15A.md (./gradlew jar + copiar-libs.gradle), con el mismo arnés cv/lfh/Arnes.java compilado contra ella; la misma imagen de Maven con Temurin 11, sin red; un contenedor y un proceso por carpeta, como linuxforhealth.json.",
 "_id": "El id no es el del estudio a propósito (Q-VC-D-3).",
 "_rutas": "Relativas a --artefactos: lfh-main/lib (el jar de master y sus dependencias), lfh-main/clases (Arnes compilado) y lfh-main/Arnes.java.",
 "_version": "La versión lleva el commit corto de master y su fecha; identidades la exige igual a RAMAS-RV.json.",
 "conversor": {
  "nombre": "linuxforhealth-hl7v2-fhir-converter",
  "version": "master (2cb72c2, 2026-02-11), construido con Gradle",
  "huella": {"partes": [{"carpeta": "lib"}, {"fichero": "lfh-main/Arnes.java"}]},
  "_huella_esperada": "si es la construcción de 15A, empieza por 28c16067 (cv/RESULTADO-15A.md)",
  "declara": {"no_soporta": []},
  "_declara": "master soporta más eventos que v1.1.0 (RESULTADO-CONVERSORES.md); aquí solo corre VXU y no importa"
 },
 "caja": {
  "tipo": "docker",
  "imagen": "maven:3.9-eclipse-temurin-11",
  "imagen_digest": "sha256:7bb84a451705605a47d24eb844d4d9ab03e33e131a507db76aafe25db3907f64",
  "_imagen_digest": "la imagen del estudio y de 15A; con otro digest la herramienta sale con 3 y es lo que se quiere",
  "montajes": {
   "lib": {"origen": "lfh-main/lib", "destino": "/lib2"},
   "clases": {"origen": "lfh-main/clases", "destino": "/clases"}
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
 "salida": {"fichero": "{nombre}.json", "fichero_error": "{nombre}.error", "forma": "bundle", "envoltura": null, "codificacion": "utf-8"}
}
```

`cv/adaptadores/linuxforhealth-main-mensaje.json`: **byte a byte** `linuxforhealth-main.json` salvo `_que` (añade «un contenedor y un proceso Java por mensaje, como linuxforhealth-mensaje.json (S-AR-1, S-RV-4)»), `invocacion.modo: "mensaje"`, `invocacion.contenedor: "por_mensaje"` y `orden` con el tercer argumento `{entrada_fichero}` (Arnes lo ignora, S-AR-2). P-RV-1 lo comprueba.

Si se reconstruye una rama (§4), el programador cambia **solo** `conversor.version` de los adaptadores afectados (commit y fecha nuevos), antes de sellar nada con ellos; `identidades` lo exige igual a `RAMAS-RV.json`.

### 2.3 Las corridas (lo que lanza `ramas_vxu.py`)

```bash
A=<artefactos>   # con ms/, lfh/ (VC3) y ms-main/, lfh-main/ (15A o reconstruidos)
# control, versiones fijadas (paso 3)
python3 cv/verificar_conversor.py cv/adaptadores/microsoft.json              <S>/fijada/ms           --artefactos $A --sin-corpus-lab --sin-minimos --sin-sensibilidad --json-solo --corpus <T>/pares
python3 cv/verificar_conversor.py cv/adaptadores/linuxforhealth.json         <S>/fijada/lfh-lote     … --corpus <T>/pares
python3 cv/verificar_conversor.py cv/adaptadores/linuxforhealth-mensaje.json <S>/fijada/lfh-mensaje  … --corpus <T>/pares
# VL11 fijada: lote-caso-1, lote-caso-2, mensaje-caso-1, mensaje-caso-2 sobre …-caso/, lote-control-1 sobre …-control/
# ramas (paso 6): lo mismo con microsoft-main.json, linuxforhealth-main-mensaje.json (decide), linuxforhealth-main.json (control) y VL11 con los dos de master
```

Cada corrida deja la carpeta de la herramienta; `ramas_vxu.py armar <corrida_ms> <corrida_lfh> <vl11_lote_caso> <vl11_lote_control> <evid>` monta el árbol de S-RV-6 (la secuencia se juzga con **lote**, que es donde el arrastre existe) y `cv3_minimos_vxu.juzgar(evid, <salida>.json)` escribe el JSON con la forma exacta de `vx/RESULTADO-VX3-minimos.json`. Para las ramas, `armar` recibe `--conversor-id microsoft-main linuxforhealth-main` para saber en qué `evidencias/<id>/` leer, y escribe igualmente bajo `microsoft/` y `linuxforhealth/` (lo que `juzgar` espera).

**Coste:** Microsoft ≈ 50 × 1-3 s; LinuxForHealth lote ≈ 20 s; mensaje a mensaje ≈ 50 × 3-6 s ≈ 3-5 min; VL11 ≈ 1 min. Todo el cómputo de la etapa, ≈ 20-30 min más las construcciones. En primer plano, sin fiarse de avisos en segundo plano.

### 2.4 Cómo se juzga cada una de las nueve

Objetivos (de `PARES`): VM07 `("RXA-15","valor_distinto","lotNumber")`, VM08 `("RXA-17","valor_distinto","Organization.name")`, VM10 `("NK1-3","codigo_mal_mapeado","relationship")`, VM12 `("RXA-19","dato_perdido","reasonCode")`, VM14 `("RXA-6","valor_distinto","doseQuantity.value")`, VM15 `("RXA-20","codigo_mal_mapeado","status")`, VL04 `("RXA-21","valor_distinto","status")`, VL06 `("RXA-10","dato_perdido","performer")`, VL07 `("RXA-19","dato_perdido","reasonCode")`. `ramas_vxu.py estado <fijada.json> <main.json> <ESTADO-RV.json>` aplica S-RV-7 a las nueve (lista fija `NUEVE` con id del par ↔ id VX-Mn/VX-Ln de `CLASES-VX3.json`) y exige que en `fijada.json` las nueve sigan `confirmada: true` (si no, el control no pasó y `estado` se niega). Los otros 17 pares (ya declaradas y convención) se anotan en una tabla aparte «si siguen», sin entrar en K (fuera de la etapa salvo anotar).

`ESTADO-RV.json`: `{"juez", "ramas": {"microsoft": {"commit", "fecha", "huella", "huella_con_nombres", "imagen_digest", "reconstruida"}, "linuxforhealth": {…}}, "modo_lfh_decide": "mensaje", "nueve": [{"id_vx": "VX-M7", "par": "VM07-lote-repetido", "conversor", "fuerza", "fijada": {"caso": {...}, "control": {...}}, "main": {"caso": {...}, "control": {...}}, "estado": "sigue|corregida|cambiada|par_roto", "que_main": "<texto del caso en la rama>"}], "K": k, "k_por_conversor": {"microsoft": k1, "linuxforhealth": k2}, "cambiadas": [...], "otros_17": [...], "lfh_lote_igual_a_mensaje": true, "lfh_lote_difiere_en": [...]}`.

---

## 3. El control (de las versiones fijadas)

**Qué reproduce:** los 26 elementos de `vx/RESULTADO-VX3-minimos.json.pares` (25 pares y VL11), cada uno con `confirmada` y, para `microsoft` y `linuxforhealth`, `caso` y `control` con `sale`, `estado`, `categoria`, `que`; y `confirmadas: 25`, `de: 26`. `ramas_vxu.py control <fijada-lote.json> <fijada-mensaje.json> vx/RESULTADO-VX3-minimos.json <CONTROL-RV.json>`.

**Con qué tolerancia:** solo `juez` puede diferir (se anotan las dos huellas y la causa: textos del servidor MCP, `RESULTADO-VXU.md` «El juez que se publica…»). Cada otra diferencia se escribe como `{"par", "conversor", "lado", "campo", "publicado", "hoy", "clase": "veredicto|texto"}`. Entre `fijada-lote` y `fijada-mensaje` se exige igualdad en los 25 pares (VL11 solo se mira en lote); una diferencia ahí se lista como `contaminacion_etapa_20`.

**Qué pasa si no reproduce:** `CONTROL-RV.json.reproduce` es `true` solo con 0 diferencias de clase `veredicto` y 0 de `contaminacion_etapa_20`, y (según Q-RV-D-4) 0 de `texto` o todas con `explicacion` no vacía. Con `reproduce: false` el orquestador **no lanza ninguna corrida con una rama** (código 3) y escribe el motivo; la regla de parada del ANTES: se declara, se arregla el aparato (lo más probable: artefactos o imagen distintos de los de VC3, o el árbol de `armar`), y si no se explica, la etapa se declara parada en `RESULTADO-RAMAS-VXU.md`. Las explicaciones se escriben a mano en `CONTROL-RV.json.diferencias[].explicacion` y el orquestador las relee.

**Identidades antes de correr nada (paso 1, sin Docker):** `VC.huella(microsoft.json) == 766f8938d0c12c382bec2edceeca4d3be4fd19900d0bd131ba880ac615fadf3e`, `VC.huella(linuxforhealth.json) == VC.huella(linuxforhealth-mensaje.json) == ac41f71b98ee75bac637ecd4b68f58b463f0798bf66cfa941f4194cb2a50acf2`, `huella_con_nombres` `1118ff9a…`/`7ad4d546…`; los tres adaptadores de rama validan; `huella(linuxforhealth-main.json) == huella(linuxforhealth-main-mensaje.json)`; `cv3_minimos_vxu.escribir` da 50 ficheros y `punto(texto) == "vxu_conv"` en todos; `M._version()["huella"]` anotada; `--solo-orden` de cada adaptador de rama imprime una orden con `ms-main/out` o `lfh-main/lib` y la imagen correcta.

---

## 4. Las ramas al día

### 4.1 Qué se mira (red, solo lectura, antes de construir)

```bash
gh api "repos/microsoft/FHIR-Converter/compare/70fd328...main"           > privado/vx/rv/compare-ms.json
gh api "repos/LinuxForHealth/hl7v2-fhir-converter/compare/2cb72c2...master" > privado/vx/rv/compare-lfh.json
gh api "repos/microsoft/FHIR-Converter/branches/main" ; gh api "repos/LinuxForHealth/hl7v2-fhir-converter/branches/master"   # sha y fecha de HEAD
```

`ramas_vxu.py ramas <compare-ms.json> <compare-lfh.json> <RAMAS-RV.json>` lee `ahead_by`, `commits[].sha/commit.committer.date/commit.message` y `files[].filename` (si `files` trae 300 o `ahead_by` > 250, L-RV-8: se piden los commits uno a uno con `repos/<r>/commits/<sha>` y se unen los ficheros).

### 4.2 Qué cuenta como «toca VXU» (expresiones regulares sobre `filename`)

- **Microsoft:** `^data/Templates/Hl7v2/` (cualquier `.liquid` o `CodeSystem/`; en particular `VXU_V04.liquid`, `Resource/_Immunization.liquid`, `Resource/_Organization.liquid`, `Resource/_RelatedPerson.liquid`, `DataType/_CWE*.liquid`, `_CE*.liquid`, `_XCN*.liquid`, `_XPN*.liquid`, `CodeSystem/CodeSystem.json`), `^src/Microsoft\.Health\.Fhir\.Liquid\.Converter/` (analizador, filtros, postproceso), `^src/Microsoft\.Health\.Fhir\.Liquid\.Converter\.Tool/`. **No cuenta:** `^docs/`, `^src/.*Tests/`, `.github/`, `README`, `.*\.md$`, FHIR→v2 (`data/Templates/Stu3ToR4|FhirToHl7v2`), `data/Templates/(Ccda|Json|Stu3)`.
- **LinuxForHealth:** `^src/main/resources/hl7/` (sobre todo `message/VXU_V04.yml`, `resource/Immunization.yml`, `resource/Organization.yml`, `resource/Practitioner.yml`, `datatype/*.yml`, `codesystem/v2ToFhirMapping.yml`), `^src/main/java/`, `^build\.gradle`, `^gradle/`, `^settings\.gradle`. **No cuenta:** `^src/test/`, `^docs?/`, `.*\.md$`, `.github/`.

Regla: `reconstruir = ahead_by > 0 and any(patron.match(f) for f in ficheros)`. Si `ahead_by == 0`: «no avanzó». Si avanzó sin tocar: se anotan los commits y se mide con la de 15A.

### 4.3 Cómo se construye (red, una vez; tope 1,5 h por rama, cronometrado por el orquestador)

Antes, mover la construcción de 15A a `ms-main-70fd328/` / `lfh-main-2cb72c2/` (no se borra: su huella está en `RESULTADO-15A.md`).

```bash
# Microsoft
git clone --depth 1 --branch main https://github.com/microsoft/FHIR-Converter <W>/ms && (cd <W>/ms && git rev-parse HEAD && git log -1 --format=%cI)
docker run --rm -v <W>/ms:/src -w /src mcr.microsoft.com/dotnet/sdk:8.0 dotnet publish src/Microsoft.Health.Fhir.Liquid.Converter.Tool -c Release -o /src/out
mkdir -p $A/ms-main/src/data/Templates && cp -r <W>/ms/out $A/ms-main/out && cp -r <W>/ms/data/Templates/Hl7v2 $A/ms-main/src/data/Templates/Hl7v2
# LinuxForHealth
git clone --depth 1 --branch master https://github.com/LinuxForHealth/hl7v2-fhir-converter <W>/lfh && (cd <W>/lfh && git rev-parse HEAD && git log -1 --format=%cI)
mkdir -p $A/lfh-main/lib $A/lfh-main/clases
docker run --rm -v <W>/lfh:/src -v $(pwd)/cv/lfh/copiar-libs.gradle:/init.gradle:ro -v $A/lfh-main/lib:/salida/lib -w /src maven:3.9-eclipse-temurin-11 sh -c "./gradlew --no-daemon --init-script /init.gradle jar copiarLibs && cp build/libs/*.jar /salida/lib/"
cp cv/lfh/Arnes.java $A/lfh-main/Arnes.java
docker run --rm --network none -v $A/lfh-main:/w -w /w maven:3.9-eclipse-temurin-11 javac -cp "lib/*" -d clases Arnes.java
```

Si una construcción no acaba en 1,5 h o falla: se anota en `RAMAS-RV.json` (`construida: false`, `motivo`), se mide ese conversor con la construcción de 15A **declarándolo** en el resultado, y la otra rama sigue su curso.

### 4.4 Qué se anota de cada construcción (`RAMAS-RV.json`, por conversor)

`repositorio`, `rama`, `commit_15A`, `commit_hoy` (sha completo), `fecha_commit_hoy`, `ahead_by`, `commits` (sha corto, fecha, primera línea), `ficheros_que_tocan_vxu` (lista; vacía si no), `reconstruida` (bool), `fecha_construccion`, `imagen_constructor` y su digest (`docker image inspect --format '{{index .RepoDigests 0}}'`), `orden_construccion`, `duracion_s`, `n_ficheros` (`out`: dll; `lib`: jars, 15A dio 77), `huella` y `huella_con_nombres` (con `VC.huella`/`VC.huella_con_nombres` sobre el adaptador de rama), `imagen_ejecucion` y `imagen_digest` (del `CORRIDA.json` de la primera corrida), `version_adaptador` (debe ser `main (<sha7>, <fecha>)` / `master (…)`). Nada de rutas de máquina.

---

## 5. La secuencia VL11 en `master`

`ramas_vxu.py secuencia <artefactos> <trabajo> --ad-lote cv/adaptadores/linuxforhealth-main.json --ad-mensaje cv/adaptadores/linuxforhealth-main-mensaje.json → SECUENCIA-RV.json` (y lo mismo con los fijados para el control, dentro de `CONTROL-RV.json.vl11_fijada`):

1. `cv3_minimos_vxu.secuencias(<trabajo>/vl11)`.
2. Cinco corridas con `--sin-corpus-lab --sin-minimos --sin-sensibilidad --json-solo --corpus`: `lote-caso-1`, `lote-caso-2` (ad-lote sobre `…-caso/`), `mensaje-caso-1`, `mensaje-caso-2` (ad-mensaje sobre `…-caso/`), `lote-control-1` (ad-lote sobre `…-control/`).
3. `sale_r, motivos_r = AR.positivo_sale(por_caso(lote-caso-r), por_caso(mensaje-caso-r), por_caso(lote-control-1))` para r = 1, 2, con `AR.filas`; nivel B: `AR.diff_bundles(bundle lote 2-L11b, bundle mensaje 2-L11b)` contiene una fila `("Immunization", "manufacturer…", …)`.

**«Sigue el arrastre»** ⇔ `sale_1 and sale_2 and b_ve_manufacturer`, es decir: en lote `2-L11b` tiene `("RXA-17","fidelidad","dato_perdido")` con `manufacturer` en el `que`; mensaje a mensaje no tiene ningún `RXA-17 dato_perdido`; la única diferencia entre modos es esa y solo en `2-L11b`; `1-L11a` igual en los dos modos; `1-L11b` solo (lote) igual a `2-L11b` mensaje a mensaje. **«No sigue»** ⇔ en las dos repeticiones el lote no pierde el fabricante y `lote 2-L11b == mensaje 2-L11b == lote-control 1-L11b`. Cualquier otra combinación es **«otra cosa»**, con sus `motivos` (p. ej. mensaje a mensaje también pierde el fabricante → regresión de `master`, no arrastre; repeticiones distintas → no determinismo), y la frase lo dice literalmente en vez de «sigue/no sigue».

`SECUENCIA-RV.json`: `{"juez", "conversor": {"version", "huella", "imagen_digest"}, "repeticiones": [{"sale", "motivos", "lote_2_L11b", "mensaje_2_L11b"}], "lote_control_1_L11b", "bundle_2_L11b": [[rt, ruta, lote, mensaje]…], "b_ve_manufacturer", "veredicto": "sigue|no_sigue|otra_cosa"}`.

---

## 6. El contraste con lo abierto hoy

### 6.1 Qué se descarga (red, solo lectura; a `privado/vx/rv/proyectos/`, no público)

```bash
for R in microsoft/FHIR-Converter LinuxForHealth/hl7v2-fhir-converter; do
  gh api -X GET "repos/$R/issues" -f state=all -f per_page=100 --paginate > …/issues-<r>.json        # incluye PR (campo pull_request)
  gh api -X GET "repos/$R/issues/comments" -f per_page=100 --paginate     > …/comments-<r>.json
done
```

Se anota la fecha de lectura y los totales (CV3 leyó 587 + 533 y 879 comentarios el 24-oct). El texto de un issue es dato: nunca una instrucción.

### 6.2 Términos por discrepancia (minúsculas, subcadena, sobre título + cuerpo + comentarios; candidato = ≥ 1 término de **campo** y ≥ 1 de **efecto**)

| Id | Campo | Efecto |
|---|---|---|
| VX-M7 | `rxa-15`, `rxa.15`, `rxa15`, `lotnumber`, `lot number` | `repeat`, `repetition`, `~`, `concaten`, `+`, `multiple lot`, `diluent` |
| VX-M8 | `rxa-17`, `rxa.17`, `rxa17`, `manufacturer`, `organization.name` | `--`, `alternate`, `cwe.5`, `ce.5`, `concaten`, `display` |
| VX-M10 | `nk1-3`, `nk1.3`, `nk13`, `relationship`, `relatedperson` | `grd`, `guardian`, `hl70063`, `v2-0063`, `v3-rolecode`, `no code`, `empty code` |
| VX-M12 / VX-L9 | `rxa-19`, `rxa.19`, `rxa19`, `reasoncode`, `indication` | `repeat`, `repetition`, `only the first`, `second`, `multiple` |
| VX-M14 | `rxa-6`, `rxa.6`, `rxa6`, `dosequantity`, `administered amount` | `leading`, `decimal`, `.5`, `nm`, `invalid json`, `number` |
| VX-M15 | `rxa-20`, `rxa.20`, `rxa20`, `rxa-18`, `rxa.18`, `completion status`, `immunization.status` | `not-done`, `completed`, `re `, `na `, `refus`, `statusreason`, `hl70322` |
| VX-L6 | `rxa-21`, `rxa.21`, `rxa21`, `action code`, `immunization.status` | `entered-in-error`, `delete`, `d `, `completed` |
| VX-L8 | `rxa-10`, `rxa.10`, `rxa10`, `performer`, `administering provider` | `repeat`, `repetition`, `only the first`, `second`, `multiple` |
| Arrastre | `rxa-17`, `manufacturer`, `organization` | `reset`, `internal variable`, `state`, `repeating messages`, `previous message`, `leak`, `#348` |

`ramas_vxu.py contraste <proyectos> <ESTADO-RV.json> <CONTRASTE-RV.json>` escribe por discrepancia la lista de candidatos (número, tipo issue/PR, estado, título, URL, términos que casaron, fecha de cierre, si hay PR enlazado) y deja `decision: null`. La persona rellena `decision` ∈ {`no_reportada`, `reportada_abierta`, `reportada_cerrada`, `relacionada`} con `numero`, `cita` (≤ 15 palabras) y `nota`; `contraste --comprobar` se niega a seguir con alguna `decision: null`.

**Qué cuenta como «ya reportada»:** un issue o PR, de cualquier estado, cuyo texto nombra **el mismo campo** (el segmento-campo de v2 o el elemento FHIR) **y el mismo efecto** (la pérdida, la concatenación, el código equivocado, el estado equivocado). Mismo campo con otro efecto es `relacionada` (el borrador dice «Possibly related to #N»). Una `reportada_cerrada` cuya corrección debería estar en la rama y el par sigue → Q-RV-D-3. El #348 es, por definición, `reportada_abierta` para el arrastre (si al leer está cerrado, se anota y el comentario pide reabrir).

---

## 7. Los borradores (`vx/BORRADORES-ISSUES-VXU.md`, no se publica)

### 7.1 Cabecera (en español, como el ejemplo)

Título «Borradores de issues de VXU (etapa 22; <fecha>)»; «Son del autor: no se abren sin él»; qué cumple cada uno (nueva y confirmada en `RESULTADO-VXU.md`; sigue en la rama principal según `RESULTADO-RAMAS-VXU.md`; buscado en issues y PR con sus comentarios, `vx/rv/CONTRASTE-RV.json`); en inglés; Microsoft sin plantilla de issue, LinuxForHealth con la suya; «Antes de abrir alguno»: mirar otra vez los abiertos, empezar por los fuertes (VX-M15, VX-M14, VX-M7, VX-M10, VX-L6), enlazar `verificador/RESULTADO-VXU.md`; «Los mensajes son sintéticos: no hay ningún dato de paciente»; la nota de VX-M14 (Q-RV-D-2).

### 7.2 Plantilla de issue (inglés), lo que lleva cada uno

```
### VXU-<MS|LFH>-<n>. <una línea: el efecto>
**Title:** `[HL7v2 VXU_V04] <campo> …: <efecto>`                 (Microsoft)   /   `<efecto>, VXU_V04 <campo>`   (LinuxForHealth)
**Describe the bug**  <qué hace la plantilla/el código, en dos frases, y por qué cambia el significado>
**To reproduce** (VXU_V04)   ```<el mensaje CASO del par, segmentos en líneas>```
**Actual:** <que_main del juez, en inglés: el valor observado en la rama>
**Expected:** <el valor esperado del juez; qué dato debe conservar>
**Control:** <el mensaje CONTROL en una frase: «the same message with <campo> = … converts correctly»>
**References:** <fila CSV de la guía y/o ConceptMap, de la tabla de RESULTADO-VXU.md; HL7 v2.5 cap. 4 donde aplique>
**Versions checked:** <fijada (commit)> and <rama (commit, fecha)>; order used: <la invocación de 2.2>
```

Para LinuxForHealth los epígrafes son los de su plantilla: **Describe the bug** / **To Reproduce** / **Expected behavior** / **Additional context** (versiones y control). El generador (`ramas_vxu.py borradores <ESTADO-RV.json> <CONTRASTE-RV.json> <SECUENCIA-RV.json> vx/BORRADORES-ISSUES-VXU.md`) toma el caso de `PARES`, `que_main` de `ESTADO-RV.json` y la tabla fija de abajo; una persona revisa el inglés antes de encolar.

| Borrador | Par (caso) | Cita de la guía | Esperado | Observado (versión fijada; en la rama, `que_main`) |
|---|---|---|---|---|
| VXU-MS-1 ← VX-M15 | VM15 (`RXA-20 = RE`, sin RXA-18) | `RXA_Immunization.csv:25-26`; CM `table-hl70322-to-event-status` (RE, NA → not-done) | `status: not-done` | `completed` (status taken from RXA-18 instead of RXA-20) |
| VXU-MS-2 ← VX-M14 | VM14 (`RXA-6 = .5`) | `RXA_Immunization.csv:9`; v2.5 ch. 2A, NM | `doseQuantity.value 0.5` (keep `.5`) | `5` (dose ×10; same cause as the OBX-5 NM report, MS-1 of the converter study) |
| VXU-MS-3 ← VX-M7 | VM07 (`RXA-15 = LOT-M07c~DIL-M07c`) | `RXA_Immunization.csv:20` (RXA-15 → lotNumber, 0..1) | `lotNumber: LOT-M07c` (first repetition, or one of them) | `LOT-M07c+DIL-M07c` (a lot that does not exist) |
| VXU-MS-4 ← VX-M10 | VM10 (`NK1-3 = GRD^Tutora^HL70063`) | CM `table-hl70063-to-v3-rolecode` (GRD, identity v2-0063) | `relationship.coding {v2-0063, GRD}` | coding with `example.com/…/HL70063` and **no code** |
| VXU-MS-5 ← VX-M8 | VM08 (`RXA-17 = MSD^Merck^MVX^MERCK^Merck S.A.^L`) | CM `datatype-cwe-to-organization` (CWE.2 → name) | `Organization.name: Merck` | `Merck--Merck S.A.` |
| VXU-MS-6 ← VX-M12 | VM12 (`RXA-19 = DM^Diabetes^L~ASM^Asma^L`) | `RXA_Immunization.csv:24` | two `reasonCode` | one (ASM dropped) |
| VXU-LFH-1 ← VX-L6 | VL04 (`RXA-21 = D`, RXA-20 CP) | `RXA_Immunization.csv:27` | `status: entered-in-error` | `completed` (a deleted record looks administered) |
| VXU-LFH-2 ← VX-L8 | VL06 (`RXA-10` ×2) | `RXA_Immunization.csv:13-15` | two `performer` (AP) | only the first (PR02 dropped) |
| VXU-LFH-3 ← VX-L9 | VL07 (`RXA-19` ×2) | `RXA_Immunization.csv:24` | two `reasonCode` | one (ASM dropped) |

### 7.3 El comentario al #348 (completo)

```
Another trigger for this, reproducible on master (<sha7>, <date>) and v1.1.0, converting two messages with the same HL7ToFHIRConverter instance.

Message 1 has RXA-17 with text only and no code: `RXA|0|1|20240301083000|20240301083000|03^MMR^CVX|0.5|mL^mL^UCUM|||PR01^Ensayo^Ana|||||LOT-L11a|202611|^Laboratorio Sintetico^|||CP|A`.
Message 2 is a plain VXU_V04 with `RXA-17 = MSD^Merck^MVX` (full messages below; synthetic data).

- Message 2 converted alone: Immunization.manufacturer references an Organization with identifier MSD/MVX.
- Message 2 converted after message 1, same instance: Immunization.manufacturer is missing, and the Organization is not created.
- Nothing else in message 2 changes.

The interim fix mentioned here (`condition: rxa17 NOT_NULL`) does not cover this case: RXA-17 is not null, it has text and no code. In our batch of 40 VXU messages, every message after the first one with a text-only RXA-17 lost its manufacturer (23 of 40). Converting one message per process, none did.

<the two messages, in a code block>
Versions: v1.1.0 (Maven Central) and master (<sha7>, <date>), built with Gradle; HL7 v2-to-FHIR guide: RXA-17 → Immunization.manufacturer (RXA_Immunization.csv:22).
```

Lleva: el par mínimo (la secuencia L11a → L11b), la cita, lo esperado, lo observado (de `SECUENCIA-RV.json`: `lote_2_L11b` frente a `mensaje_2_L11b`) y las versiones. Si `veredicto` no es `sigue`, el comentario no se genera y el resultado lo dice.

### 7.4 Encolado

Al final de `vx/BORRADORES-ISSUES-VXU.md`, una lista «Para la cola del autor» con una línea por borrador; y en el repositorio de trabajo (no en el público) se añade a la cola del autor una entrada: «Issues de VXU: N borradores en `vx/BORRADORES-ISSUES-VXU.md` (K siguen; el comentario al #348); abrirlos es tuyo».

---

## 8. La previsión que se sella (`vx/rv/PREVISION-RV.json`, `SELLO-RV.txt`)

Claves obligatorias (P-RV-9): `etapa`, `fecha`, `juez` (huella), `herramienta` (`{verificar_conversor, cv3_minimos_vxu, ramas_vxu, adaptadores: {microsoft-main, linuxforhealth-main, linuxforhealth-main-mensaje}}`, sha256 de cada fichero), `ramas_15A` (`{"microsoft": "70fd328", "linuxforhealth": "2cb72c2"}`), `p_control_reproduce` (las 26 filas iguales salvo `juez`), `p_lote_igual_mensaje_fijada` (los 25 pares iguales entre modos con v1.1.0), `p_rama_avanzo` (`{"microsoft": p, "linuxforhealth": p}`), `p_toca_vxu_si_avanzo` (ídem), `p_construccion_dentro_del_tope` (ídem), `p_sigue` (**nueve claves** `VX-M7 … VX-L9`, cada una `{"si_no_toca_vxu": p, "si_toca_vxu": p}`), `K_previsto` (`[lo, hi]`), `k_mas_probable` (`{"microsoft": k1, "linuxforhealth": k2}`), `p_arrastre_sigue_master` (`{"sigue": p, "no_sigue": p, "otra_cosa": p}`), `p_ya_reportada` (nueve claves, p de `reportada_*`), `p_alguna_cambiada_o_par_roto`, `tolerancia_control` («solo juez», y la decisión de Q-RV-D-4), `jev` (la previsión de Jev con estado neutro, al lado, sin cambiar la del programador). Formato: JSON con sangría 1, `ensure_ascii=False`, como `cv/ar/PREVISION-AR.json`; `PREVISION-RV.md` con la lectura en prosa.

`vx/rv/sellar_prevision_rv.py <cuerpo.json> [<carpeta>]` (copia adaptada de `cv/ar/sellar_prevision.py`): añade `fecha`, `juez` y `herramienta`, escribe `SELLO-RV.txt` (`sha256  ruta relativa` de `PREVISION-RV.json`, `PREVISION-RV.md`, `ramas_vxu.py`, `prueba_rv.py`, los tres adaptadores de rama, `cv3_minimos_vxu.py`, `verificar_conversor.py`, más la línea `juez <huella>`), se niega a pisar un sello, y `AR.comprobar_sello` lo verifica con `CLAVES_PREVISION_RV`. Después, el **commit**; el orquestador exige (como `control_ar.git_por_omision`) que el sello esté en HEAD sin cambios pendientes antes del primer `docker run` de la etapa.

**Prior orientativo del diseñador (no es el sello):** `p_rama_avanzo` Microsoft 0,6, LinuxForHealth 0,3 (su `master` llevaba 8 meses quieto el 24-oct); `p_toca_vxu_si_avanzo` 0,3 / 0,5; `p_sigue` si no toca VXU 0,97 en las nueve (15A: 14 de 15 siguieron, y la corregida lo estaba por un commit que sí tocaba su tabla); si toca VXU, Microsoft 0,85 y LinuxForHealth 0,7 (VX-L6 el más expuesto: `v2ToFhirMapping.yml` ya cambió estados en `master`); `k_mas_probable` 6 y 3; `p_arrastre_sigue_master` sigue 0,85, no sigue 0,1, otra cosa 0,05 (el #348 seguía abierto el 25-oct); `p_control_reproduce` 0,9; `p_lote_igual_mensaje_fijada` 0,95; `p_ya_reportada` ≤ 0,1 en las nueve salvo VX-M15 0,2.

---

## 9. Las pruebas en rojo (`vx/rv/prueba_rv.py`), sin Docker

Mismo arnés que `cv/ar/prueba_ar.py`: espía `Espia` (registra órdenes; `docker image inspect` devuelve el digest que se le configure; guarda el contenido de `/in`), el conversor de juguete (`cv/adaptadores/juguete.json` y su variante mensaje en memoria), filas de juicio fabricadas con `fila(...)`, artefactos falsos (`ms/out`, `ms/src/data/Templates/Hl7v2/VXU_V04.liquid`, `lfh/lib`, `lfh/clases`, `lfh/Arnes.java`, y lo mismo bajo `ms-main/`, `lfh-main/`). `python3 vx/rv/prueba_rv.py` → `PRUEBAS RV: TODO BIEN (n comprobaciones, 12 pruebas)`; `… rojo` → 0 solo si fallan las 12. Literales de contenedor compuestos (`"/in" + "/a.hl7"`) por la guarda de higiene.

| Id | Qué comprueba | Control negativo | En rojo antes porque |
|---|---|---|---|
| P-RV-1 | Los tres adaptadores validan con `VC.leer_adaptador`; `id` `microsoft-main`/`linuxforhealth-main`; `version` casa `^(main|master) \([0-9a-f]{7}, \d{4}-\d\d-\d\d\)`; Microsoft: imagen `…runtime:8.0`, montajes a `ms-main/out` y `ms-main/src/data/Templates/Hl7v2`, resto de bloques igual a `microsoft.json` (salvo `id`, `version`, imagen, orígenes); LinuxForHealth: `huella(main) == huella(main-mensaje)`, bloques iguales salvo modo/contenedor/tercer argumento; `orden_caja` del mensaje termina en `["Arnes", "/in", "/salida", "/in/a.hl7"]`; con `VC.correr` vía espía y `lab=False, minimos=True`, el corpus da `minimos: 0` | `microsoft.json` da `runtime:6.0` y `ms/out`; con `id: "microsoft"` entran 68 mínimos; `version` sin commit → la identidad falla | los ficheros no existen (`json_invalido`) |
| P-RV-2 | `armar(corrida_ms, corrida_lfh, vl11_caso, vl11_control, evid, ids)` sobre corridas de juguete con `--corpus` de los 50 pares y las dos carpetas de VL11: el árbol tiene `microsoft/<pid>-{caso,control}.json` (50), `linuxforhealth/…` (50), `linuxforhealth/VL11-estado-fabricante-caso/L11b.json` (copia de `2-L11b.json`) y `…-control/L11b.json` (de `1-L11b.json`); `cv3_minimos_vxu.juzgar(evid, out)` corre y `de == 26` | sin la carpeta de control, `juzgar` deja `control: None` y `confirmada: false`, no excepción; un fichero de más en `propio` no entra | `import ramas_vxu` falla |
| P-RV-3 | `comparar_control(nuevo, publicado)` con una copia de `vx/RESULTADO-VX3-minimos.json`: idéntica salvo `juez` → `reproduce: true`, `diferencias: []`, `jueces: [a, b]`; un `sale` invertido → una fila `veredicto`; `confirmada` cambiada → `veredicto`; solo un `que` cambiado → `texto`; la fila de VL11 también se compara; `lote_vs_mensaje` sobre dos JSON iguales → `[]`, con un par distinto → `[pid]` | copias idénticas → nada | ídem |
| P-RV-4 | `estado_nueve(fijada, main)` con JSON fabricados: `confirmada` en main → `sigue`; caso sin objetivo, sin otro hallazgo del hecho, los dos `bundle` → `corregida`; caso sin objetivo pero con `("RXA-15", …, "dato_perdido")` → `cambiada`; control sale → `par_roto`; caso `error` → `par_roto`; `K` y `k_por_conversor` cuadran; fijada con una de las nueve no confirmada → excepción `ControlNoPasa` | las 17 que no son de las nueve no entran en K | ídem |
| P-RV-5 | `decidir_ramas(compare)` con payloads fabricados: `ahead_by: 0` → `avanzo: false, reconstruir: false`; commits que tocan solo `README.md`/`src/test/...`/`docs/` → `avanzo: true, reconstruir: false` con la lista; `data/Templates/Hl7v2/VXU_V04.liquid` → `reconstruir: true`; `src/main/resources/hl7/resource/Immunization.yml` → `true`; `files` con 300 entradas → `incompleto: true` (pide por commit) | `data/Templates/Ccda/x.liquid` → `false` | ídem |
| P-RV-6 | `veredicto_vl11(reps, b)` sobre filas fabricadas como `prueba_ar.vl11()`: dos repeticiones que salen y `b_ve_manufacturer` → `sigue`; lote sin pérdida y los tres `2-L11b`/`1-L11b` iguales → `no_sigue`; mensaje a mensaje también pierde → `otra_cosa` con motivo «mensaje a mensaje, 2-L11b también pierde RXA-17»; repeticiones distintas → `otra_cosa` | `b_ve_manufacturer: false` con `sale` → `otra_cosa` | ídem |
| P-RV-7 | `candidatos(discrepancia, issues, comments)` con issues fabricados: título «lotNumber concatenates repeated RXA-15» → candidato de VX-M7 (campo + efecto); «RXA-15 is mapped» (solo campo) → no; «repeated values» (solo efecto) → no; un término en un comentario cuenta; mayúsculas no importan; PR y cerrados entran con su `estado` | un issue de ORU con `reasonCode` no es candidato de VX-M7 | ídem |
| P-RV-8 | `borradores(estado, contraste, secuencia)`: con 2 `sigue` no reportadas, 1 `sigue` reportada abierta (#N), 1 `corregida` y arrastre `sigue` → 2 secciones de issue, 1 «Comment on #N», 0 para la corregida, y el comentario al #348 con los dos mensajes; cada sección lleva Title, To reproduce con el caso de `PARES` (líneas, no `\r`), Expected, References y Versions con los dos commits; sin `VC.RUTA_MAQUINA`; sin la palabra `Prueba^Mateo` fuera de los mensajes (dato sintético) | arrastre `no_sigue` → sin comentario y la lista lo dice; `decision: null` en el contraste → excepción | ídem |
| P-RV-9 | `AR.comprobar_sello` con `CLAVES_PREVISION_RV`: un sello fabricado cuadra; un byte cambiado → `False`; una clave de menos (`p_sigue`) → `False`; `p_sigue` sin las nueve claves → `False` | — | ídem |
| P-RV-10 | El orquestador `ramas_vxu.py correr` con espía, `git` inyectado y `--desde/--hasta`: sin sello en commit → código 7 y 0 órdenes; con `CONTROL-RV.json.reproduce: false` → código 3 y ninguna orden con `ms-main`/`lfh-main`; con todo bien, las órdenes de la rama llevan `runtime:8.0` + `ms-main/out`, y LinuxForHealth mensaje da 50 contenedores con un fichero cada uno, lote 1 contenedor con 50, VL11 lote-caso 1 contenedor con `1-L11a.hl7, 2-L11b.hl7` | las corridas fijadas llevan `runtime:6.0` y `ms/out` | ídem |
| P-RV-11 | `resultado_md(estado, secuencia, contraste, ramas, control)`: contiene exactamente «De las 9 nuevas de VXU, siguen K en la rama principal de su conversor (Microsoft k1 de 6, LinuxForHealth k2 de 3); el arrastre de estado sigue en `master`» (o «no sigue»; con `otra_cosa`, la frase literal del motivo); la tabla de las nueve con fijada/rama/estado; los commits y huellas de las ramas; `reconstruida` sí/no; el control; sin rutas de máquina; sin la palabra «confirmadas» aplicada a la rama | `K` que no cuadra con la tabla → excepción | ídem |
| P-RV-12 | **Control negativo de contaminación con el juguete:** 50 mensajes ADT nominales más uno con `JUGUETE-ARRASTRE` en posición 3, en lote (juguete) → los siguientes pierden `PID-8`; el mismo corpus con el juguete en modo mensaje → ninguno; `lote_vs_mensaje` de `comparar_control` lo lista; con la directiva quitada, 0 diferencias | — | ídem (la función no existe) |

Tras el código: `python3 cv/prueba_vc.py` y `python3 cv/ar/prueba_ar.py` siguen en verde (no se tocan), la huella del juez no cambia (`ramas_vxu.py` no está en `FICHEROS`), `pytest tests/` en verde (JSON nuevos admitidos por la guarda; `vx/BORRADORES-ISSUES-VXU.md` y `privado/` fuera del público).

---

## 10. Las preguntas de diseño para Jev (Q-RV-D-n)

Solo lo que ni el ANTES ni las S-RV deciden. Se pasan con estado neutro (`vx/rv/estado_qrv.md`, `preguntas_qrv.json`, `decision-jev-qrv.md`); recomendaciones aparte en 10.6.

**Q-RV-D-1. Una de las nueve que en la rama sale «cambiada»** (el objetivo ya no sale, pero el juez cuenta otro hallazgo en el mismo campo). (a) cuenta en K como «sigue, con otro síntoma» y el borrador describe el nuevo; (b) no cuenta en K: fila aparte «cambiada, pendiente de contraste», sin borrador; (c) cuenta como corregida.

**Q-RV-D-2. El borrador de VX-M14** (RXA-6 «.5» → 5), misma causa que MS-1 de la cola del estudio (OBX-5). (a) borrador propio; (b) solo un párrafo añadido a MS-1; (c) borrador propio que remite a MS-1 y, si MS-1 se abre antes, se pega como comentario allí.

**Q-RV-D-3. Una de las nueve ya reportada y cerrada como arreglada, pero el par sigue en la rama.** (a) borrador de comentario al issue cerrado pidiendo reabrir, con el par; (b) borrador de issue nuevo que enlaza el cerrado; (c) solo anotar, sin borrador.

**Q-RV-D-4. Tolerancia del control en el texto `que`** (sale, estado, categoría y `confirmada` iguales; solo cambia el texto del hallazgo). (a) bloquea hasta que cada diferencia lleve explicación escrita; (b) el texto no cuenta, como Q-VC-D-7, y solo se lista; (c) bloquea solo si el texto cambia el valor observado (la parte tras «observado»).

**Q-RV-D-5. ¿Se corre también en lote con `master` el conjunto de los 50 pares, además de mensaje a mensaje?** (a) sí, como control: se compara con mensaje a mensaje y se declara si difiere; (b) no: VL11 basta para el arrastre y los pares se deciden solo mensaje a mensaje.

### 10.6 Recomendaciones del diseñador (aparte)
Q-RV-D-1 (b): K debe querer decir «la misma discrepancia», y lo nuevo no está contrastado. Q-RV-D-2 (c): un issue por mecanismo es el precedente de la cola, y no se pierde la reproducción en VXU. Q-RV-D-3 (a): el proyecto ya conoce el campo; lo útil es la reproducción en su rama. Q-RV-D-4 (a): el ANTES pide explicar antes de mirar las ramas, y las diferencias de texto son pocas y baratas de explicar. Q-RV-D-5 (a): una corrida de 20 s que muestra que las nueve no dependen del modo.

---

## 11. Los límites (L-RV-n)

- **L-RV-1.** «Sigue» y «corregida» valen para el par mínimo: una corrección que solo cubra otras entradas, o un fallo que solo salga con otras, no se ve.
- **L-RV-2.** La rama es la del commit anotado el día de la etapa; cualquier commit posterior puede cambiarlo.
- **L-RV-3.** Los artefactos de las ramas (`ms-main/`, `lfh-main/`) son privados; lo público son sus huellas, el commit y la receta.
- **L-RV-4.** El contraste depende de términos y de una lectura humana; un issue con otras palabras puede escaparse (como pasó con M-21 en CV3 hasta leer los comentarios).
- **L-RV-5.** VL11 prueba un solo disparador del arrastre (RXA-17 con texto y sin código) y un solo síntoma; otro arrastre en `master` no se mide.
- **L-RV-6.** El juez del laboratorio (`bde94016…`) no es byte a byte el que juzgó la etapa 20 (`11a3754f…`): la igualdad de veredictos se apoya en el control de los 26, no en una comparación del código.
- **L-RV-7.** La huella de Microsoft `main` depende de la construcción (SDK, fecha): dos construcciones del mismo commit pueden dar huellas distintas; identifica la corrida, no el commit.
- **L-RV-8.** El `compare` de GitHub trunca a 250 commits y 300 ficheros; por encima se pide por commit, y si tampoco alcanza se declara.
- **L-RV-9.** La imagen `runtime:8.0` va por etiqueta (`imagen_digest: null`); el digest se registra pero no se exige.
- **L-RV-10.** Si una construcción falla en el tope, ese conversor se mide con la de 15A: la respuesta es sobre el 24-oct, y se dice.
- **L-RV-11.** Microsoft no corre mensaje a mensaje ni hace falta; si su rama introdujera estado entre ficheros del bucle, no se vería (muy improbable: un proceso por fichero).
- **L-RV-12.** Las otras 17 (ya declaradas y convención) solo se anotan; no se contrastan ni llevan borrador.

---

## 12. El plan

Tope: una sesión; 1,5 h por construcción. `vx/rv/ramas_vxu.py correr <artefactos> <salida> [--desde N] [--hasta N] [--sello <carpeta>]` encadena y para en el primer fallo; cada paso deja su JSON en `vx/rv/` (nombres de carpeta, nunca rutas).

| Paso | Qué | Hecho cuando | Si falla |
|---|---|---|---|
| 0 | Q-RV-D-1..5 a Jev con estado neutro | decididas | — |
| 1 | `prueba_rv.py` en rojo (12 fallan por la razón prevista); commit | `rojo` sale 0 | — |
| 2 | Código: los tres adaptadores, `ramas_vxu.py`, `sellar_prevision_rv.py`; `prueba_rv.py` verde; `prueba_vc.py`, `prueba_ar.py`, `pytest tests/` verdes; commit | todo verde | — |
| 3 | **Identidades**, sin Docker (§3 último párrafo) → `CONTROL-RV.json.identidades` | cuadra | parar: no son los artefactos de VC3/15A |
| 4 | **Previsión sellada** (§8), con la de Jev al lado; commit | sello en HEAD | no se corre nada (código 7) |
| 5 | **Control**: pares con `microsoft.json`, `linuxforhealth.json`, `linuxforhealth-mensaje.json`; VL11 fijada; `armar` + `juzgar` → `RESULTADO-RV-minimos-fijada-{lote,mensaje}.json`; `control` → `CONTROL-RV.json` | `reproduce: true` (con explicaciones escritas si Q-RV-D-4 las admite) | **regla de parada**: declarar, arreglar el aparato; sin explicación, la etapa para y `RESULTADO-RAMAS-VXU.md` lo dice |
| 6 | **Ramas al día** (red, lectura): `compare` → `RAMAS-RV.json`; si toca VXU, construir (§4.3, cronómetro 1,5 h), editar `version` de los adaptadores, repetir identidades | `RAMAS-RV.json` con commit, huella, `reconstruida` | medir con 15A y declararlo |
| 7 | **Corridas de rama**: `microsoft-main.json` (pares), `linuxforhealth-main-mensaje.json` (pares, decide), `linuxforhealth-main.json` (pares, control Q-RV-D-5; VL11 lote), `linuxforhealth-main-mensaje.json` (VL11 mensaje) → `RESULTADO-RV-minimos-main.json`, `SECUENCIA-RV.json` | escritos, `juez` igual que en el control | caja: código 4, se declara lo no corrido |
| 8 | `estado` → `ESTADO-RV.json` (las nueve, K, k1, k2, cambiadas, las otras 17, lote frente a mensaje en `master`) | escrito | — |
| 9 | **Contraste** (red, lectura): descarga a `privado/vx/rv/proyectos/`, `candidatos`, decisiones a mano, `--comprobar` → `CONTRASTE-RV.json` | ninguna `decision: null` | — |
| 10 | `borradores` → `vx/BORRADORES-ISSUES-VXU.md`; revisión del inglés; entrada en la cola del autor | escrito y encolado | — |
| 11 | `resultado` → `verificador/RESULTADO-RAMAS-VXU.md` (la frase fija, la tabla de las nueve, las ramas y sus commits, el control, la secuencia, el contraste en agregado, los límites, cómo repetir); nota en `RESULTADO-VXU.md` («Lo que quedó para el autor»: «reproducidas en la rama principal el <fecha>: siguen K de 9; `RESULTADO-RAMAS-VXU.md`») | escrito, sin rutas de máquina | — |
| 12 | **Publicar con la opción B**: `vx/rv/` (encargo, este diseño, decisiones de Jev, código, pruebas, previsión y sello, `CONTROL-RV`, `RAMAS-RV`, `RESULTADO-RV-minimos-*`, `SECUENCIA-RV`, `ESTADO-RV`, `CONTRASTE-RV` sin el volcado), los tres adaptadores, el resultado y la nota; **sin** los borradores ni `privado/`; `MANIFIESTO.txt` regenerado; enlaces desde `verificador/README.md`; guarda LIMPIO, higiene, revisión a ciegas y Jev; push | push | — |

**Lo que el plan no permite:** correr una rama sin `CONTROL-RV.json.reproduce: true` (código 3) ni sin el sello en un commit (código 7); decidir el estado de una de las nueve en LinuxForHealth desde el lote; tocar `verificar_conversor.py`, `Arnes.java`, `cv3_minimos_vxu.py`, `cv/ar/*` o el juez; publicar los borradores.

**Códigos de `ramas_vxu.py correr`:** 0 todo; 1 identidades; 2 error del aparato; 3 el control no reproduce; 4 la caja falló; 5 construcción fuera del tope (se sigue con 15A y se anota); 6 contraste con decisiones vacías; 7 sello.

### Apéndice. Ficheros nuevos

| Fichero | Qué | Público |
|---|---|---|
| `cv/adaptadores/microsoft-main.json`, `linuxforhealth-main.json`, `linuxforhealth-main-mensaje.json` | §2.2 | sí |
| `vx/rv/ramas_vxu.py` | subórdenes `identidades`, `armar`, `control`, `ramas`, `secuencia`, `estado`, `contraste`, `borradores`, `resultado`, `correr`; funciones de §9; solo biblioteca estándar; `sys.path` como `cv/ar/arrastre.py`; importa `verificar_conversor as VC`, `cv3_minimos_vxu as MINV`, `arrastre as AR` (solo `positivo_sale`, `diff_bundles`, `filas`, `comprobar_sello`) | sí |
| `vx/rv/prueba_rv.py`, `sellar_prevision_rv.py`, `prevision-cuerpo-rv.json`, `PREVISION-RV.{json,md}`, `SELLO-RV.txt` | §8, §9 | sí |
| `vx/rv/CONTROL-RV.json`, `RAMAS-RV.json`, `RESULTADO-RV-minimos-fijada-{lote,mensaje}.json`, `RESULTADO-RV-minimos-main.json`, `SECUENCIA-RV.json`, `ESTADO-RV.json`, `CONTRASTE-RV.json` | los resultados (sin evidencias ni Bundles) | sí |
| `vx/rv/ENCARGO-RV0.md`, `diseno-rv-fable.md`, `estado_qrv.md`, `preguntas_qrv.json`, `decision-jev-qrv.md`, `decisiones-qrv.md` | procedencia | sí |
| `verificador/RESULTADO-RAMAS-VXU.md`; nota en `RESULTADO-VXU.md` | el documento del ANTES | sí |
| `vx/BORRADORES-ISSUES-VXU.md`; `privado/vx/rv/{proyectos,compare-*.json}`; artefactos `ms-main*/`, `lfh-main*/` | los borradores y lo de terceros | **no** |