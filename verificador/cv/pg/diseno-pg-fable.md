<!-- modelo: Claude Fable 5.1 (claude-fable-5-1); fecha: 25-oct-2026; a ciegas: leído solo el clon del repositorio público (publicacion/) y el encargo ENCARGO-PG0.md; nada del repositorio privado, nada ejecutado, nada modificado -->

# Diseño PG0: la página del estudio de conversores (etapa 19)

**El encargo:** una página web estática que cuente a quien llega al repositorio qué encontró el verificador en dos conversores
HL7 v2 → FHIR de código abierto, y cómo pasar el suyo por el mismo juez. Sin JavaScript, sin nada externo, con las mismas
reglas que `docs/index.html`, y **sin una sola cifra escrita a mano**.

**La respuesta de este diseño, en cuatro líneas:**
- La página es `docs/conversores/index.html`, servida en `https://lk-corporation.github.io/lab-integraciones/conversores/`,
  con el mismo estilo, las mismas fuentes autoalojadas y la misma estructura (cabecera, resumen, secciones numeradas,
  límites, pie) que la página del primer estudio.
- **La escribe un guion**, `codigo/hacer_pagina_conversores.py`, que lee solo ficheros publicados y envuelve cada cifra, cada
  texto del juez, cada cita y cada mensaje mínimo en un elemento con su **fuente declarada** (`data-fuente`). La prosa de enlace
  vive en el guion; los datos, no.
- **Una guarda nueva** resuelve cada fuente y comprueba que la página dice lo mismo; otra busca cifras sin fuente y las hace
  fallar; otra comprueba que la página es byte a byte la que genera el guion. Las tres llevan su control negativo.
- Lo interactivo es `<details>` por discrepancia (el par mínimo con el disparador marcado y lo que dijo el juez), anclas por
  identificador y una figura SVG con texto accesible. Nada que exija JavaScript.

Lo que **no** se toca: el juez (`verificador/`, su `MANIFIESTO.txt`), los documentos del estudio, el cuerpo de
`docs/index.html` (solo su pie), las fuentes de `docs/fonts/`.

---

## 0. De dónde sale lo que la página cuenta

| Fichero publicado | Qué da a la página |
|---|---|
| `verificador/cv/CLASES-CV3.json` | la frase (`frase.*`: 15, 5/10, 7, 2, 31, 19/12, 16, 2, 3, 368); cada mecanismo con `id`, `clase`, `que`, `referencia`, `par_minimo`, `fuerza`, `casos`, `ejemplos`; el juez `54a90cd9…` |
| `verificador/cv/RESULTADO-CV3.md` | la tabla de las 15 (cita de la guía, casos, fuerza), la de las 10 que cayeron, los matices de la revisión, «lo que no cuenta» |
| `verificador/cv/RESULTADO-CV3-minimos.json` | por par mínimo: lo que dijo el juez (`que`), la categoría del caso y del control, en los dos conversores |
| `verificador/cv/cv3_minimos.py` | el texto de los mensajes mínimos (`PARES`), importado, no copiado |
| `verificador/cv/RESULTADO-15A.md` y `RESULTADO-15A-minimos-main.json` | qué pasa con cada nueva en la rama principal (14 siguen, 1 corregida); las ramas, sus commits y cómo se construyeron |
| `verificador/cv/RESULTADO-CV2.json` y `RESULTADO-CV2.md` | las categorías por conversor y corpus, con el rango sellado al lado |
| `verificador/cv/PREVISION-CV2.json` | la frase prevista (N ≥ 2, K 1 o 2, D ≥ 3, C ≥ 10), las versiones y huellas de los conversores |
| `verificador/RESULTADO-CONVERSORES.md` | la frase fija, las cuatro condiciones, fechas, referencia, qué cambió en el juez, lo que el resultado no dice |
| `ARTICULO.md` | el hilo del relato: el problema, el juez, las ocho clases, los ocho pasos del método, la frase de cada discrepancia, los once defectos del juez, lo que esto no dice, cómo reproducirlo |
| `verificador/cv/VC.md`, `verificador/cv/vc/CONTROL-VC.md`, `verificador/cv/vc/ejemplos/INFORME-*.json` | la orden, lo que hace la herramienta, lo que no puede saber, el control (368/0/34), los códigos de salida, la caja, los límites L-VC-n |
| `verificador/MANIFIESTO.txt` | la huella del juez publicado (`0dd3ae5c…`) frente a la del laboratorio (`40bbc3ef…`) |
| `README.md`, `LICENSE.md` | la entrada del lector y el aviso del pie |

Lo que **no** se lee ni se muestra: los Bundles de los conversores (no son públicos), las muestras de los proyectos, el detalle
por caso del estudio (condición 5 y L-VC-8).

---

## 1. Decisiones (S-PG-n)

| Id | Decisión | Porqué, en una línea |
|---|---|---|
| S-PG-1 | La página la **genera un guion**, `codigo/hacer_pagina_conversores.py`, solo biblioteca estándar; `docs/conversores/index.html` es su salida y se publica junto al guion. | Condición 2: una cifra que sale de un fichero no se puede escribir a mano, y una guarda puede regenerar y comparar. |
| S-PG-2 | **Toda cifra, todo texto del juez, toda cita y todo mensaje mínimo va dentro de un elemento con `data-fuente`** (§2.3), que dice fichero y campo. La prosa de enlace no lleva cifras. | Así «de qué fichero y campo sale» es un atributo legible, no una nota del diseño. |
| S-PG-3 | **La página no calcula.** Cada cifra que se lee es un valor literal de un fichero (JSON, celda de tabla o frase de un `.md`). El guion solo escala barras, y las etiquetas de las barras son valores literales. | Un porcentaje calculado aquí es una cifra nueva; las que hay ya están escritas en `RESULTADO-CV2.md` y en los `INFORME-*.json`. |
| S-PG-4 | **Las cantidades van en numerales**, nunca en letras, salvo cuando la fuente las escribe en letras («ocho clases», «once defectos», «cuatro condiciones»); entonces van en letras **y con fuente**. | La guarda ve dígitos; las palabras-número de la fuente se verifican igual. |
| S-PG-5 | **Nada sobre los dos proyectos que no esté en el estudio:** la frase de cada discrepancia es la de `ARTICULO.md`, el registro es el de `RESULTADO-CV3.md`/`CLASES-CV3.json`, los matices de la revisión se copian, y la línea «son proyectos serios y útiles» va en la página. No se usan las palabras «bug», «error del proyecto» ni «fallo» para una discrepancia. | Condición 4. |
| S-PG-6 | **De cada par mínimo se muestran el caso, el control, el disparador marcado y lo que dijo el juez. Ningún fragmento de Bundle.** | Condición 5. |
| S-PG-7 | **«Lo que esto no dice» es una sección entera de la página** (§2.2, sección 11), con el texto de los límites, no un enlace. Lo mismo para «lo que la herramienta no puede saber» (L-VC-1) y «lo que no hace». | Condición 3. |
| S-PG-8 | **Mismas reglas que la primera página:** sin `<script`, sin `on…=`, sin `javascript:`, sin recurso externo; fuentes de `docs/fonts/` por `../fonts/fuentes.css`; claro y oscuro por `prefers-color-scheme` y `data-theme`; `<html lang="es">`, `viewport`, `color-scheme`. | Condición 1; `test_la_pagina_no_carga_nada_externo` ya vigila `docs/`. |
| S-PG-9 | **El estilo se copia, no se comparte:** los tokens (`--ground`, `--ink`, `--accent`…), las fuentes y las clases base (`.wrap`, `.eyebrow`, `h2 .num`, `.tesis`, `.principio`, `.limites`, `.tabla-caja`, `pre`) se copian del `<style>` de `docs/index.html` al de la nueva página, y se añaden las nuevas (`.disc`, `.par`, `mark`, `.indice`, `.salto`). | La primera página está publicada y revisada; extraer un CSS común la tocaría sin necesidad. |
| S-PG-10 | **Interacción solo con HTML y CSS:** `<details>/<summary>` por discrepancia y por lista larga; anclas por identificador (`#M-24`) con `:target`; un índice de secciones; una figura SVG con `role="img"` y `aria-label`. Sin pestañas por radio ni filtros (ver Q-PG-D-6). | Lo que da HTML es accesible por teclado sin escribir nada. |
| S-PG-11 | **La URL es `https://lk-corporation.github.io/lab-integraciones/conversores/`** (carpeta con `index.html`), no `conversores.html`. | Deja sitio a más páginas de la familia (Mirth y los que vengan) sin cambiar la forma. |
| S-PG-12 | **La página dice qué juez firma cada cifra:** los resultados sellados (`54a90cd9…`), el cierre y la rama principal (`40bbc3ef…`) y el juez publicado (`0dd3ae5c…`, misma lógica). | Hay tres huellas en los documentos y el lector tiene que poder cuadrarlas con `MANIFIESTO.txt`. |
| S-PG-13 | **Los mensajes mínimos se importan de `cv3_minimos.PARES`**, no se copian al guion; la guarda compara el `<pre>` con el módulo. | El estudio ya los genera byte a byte; dos copias divergirían. |
| S-PG-14 | **Tres guardas nuevas con control negativo** (§4 y §5): regeneración idéntica, fuentes resueltas, y ninguna cifra ni palabra-número suelta. Los controles mutan la página en memoria y exigen que la guarda lo vea. | «Un verde puede ser falso»: la guarda se prueba rompiendo la página a propósito. |
| S-PG-15 | **La descripción `<meta>` y el `<title>` no llevan cifras** (salvo «HL7», «v2», «R4»). | Son texto que un lector ve al compartir el enlace y no caben en un `data-fuente`. |
| S-PG-16 | **Enlaces a ficheros del repositorio por su URL absoluta de GitHub** (`https://github.com/LK-Corporation/lab-integraciones/blob/main/…`), como hace la primera página; enlaces relativos solo a `../` y a `../fonts/`. | GitHub Pages sirve solo `docs/`; un enlace relativo a `ARTICULO.md` no resolvería en el sitio. |
| S-PG-17 | **La primera página enlaza a la segunda desde su pie** (y `codigo/hacer_pagina.py` se actualiza igual), y el README desde «Por dónde empezar», en la viñeta de `ARTICULO.md`. | Mínimo cambio en lo publicado; la entrada del lector sigue siendo el README. |

---

## 2. La estructura de la página

### 2.1 Esqueleto

```
<!doctype html> <html lang="es">
<head>  charset · viewport · description (sin cifras) · color-scheme · canonical · og:* · twitter:card
        <title> · <link rel="stylesheet" href="../fonts/fuentes.css"> · <style> (reset + tokens + reglas)
<body>
  <a class="salto" href="#contenido">Saltar al contenido</a>
  <div class="wrap">
    <a class="volver" href="../">← La primera página: el agente que no hacía falta</a>
    <p class="eyebrow">…</p>  <h1>…</h1>  <p class="standfirst">…</p>  <div class="meta">…</div>
    <nav class="indice" aria-label="Secciones"><ol>…</ol></nav>
    <main id="contenido">
      <section id="resumen">     RESUMEN
      <section id="s01">         01 El problema
      <section id="s02">         02 El juez
      <section id="s03">         03 El método
      <section id="s04">         04 Lo que encontró (las 15)
      <section id="s05">         05 En la rama principal
      <section id="s06">         06 Lo que los proyectos ya sabían (las 31)
      <section id="s07">         07 Lo que no cuenta
      <section id="s08">         08 Lo que el juez se equivocó
      <section id="s09">         09 La previsión sellada frente a lo que salió
      <section id="s10">         10 Pasa tu conversor por el mismo juez
      <section id="s11">         11 Lo que esto no dice
      <section id="s12">         12 Cómo reproducirlo
    </main>
    <footer>…</footer>
  </div>
  <p class="pie-repo">El código, el juez, los documentos y las guardas están en github.com/LK-Corporation/lab-integraciones.</p>
```

La numeración, la cabecera y el pie siguen la forma de `docs/index.html` (`.eyebrow`, `h1`, `.standfirst`, `.meta`, `h2 .num`,
`footer`, el párrafo final al repositorio).

### 2.2 Sección por sección

Convención de la columna «Fuente»: `json:<ruta>#<puntero>`, `md:<ruta>` + patrón, `tabla:<ruta>#<línea>|<fila>|<columna>`,
`hl7:PAR#caso|control`. El contrato exacto está en §2.3. Lo que no lleva fuente es prosa de enlace, escrita en el guion.

**Cabecera.**

| Elemento | Qué dice | Fuente |
|---|---|---|
| `.eyebrow` | «Laboratorio de integraciones · octubre de 2026» | `md:ARTICULO.md` patrón `Laboratorio de integraciones, (octubre de 2026)\.` |
| `h1` | el título (Q-PG-D-1); recomendado «Un juez que no se fía del conversor» | prosa |
| `.standfirst` | «Un mensaje con una proteína C reactiva de **.5 mg/L** entró en un conversor de código abierto y salió como **5 mg/L**. Nada avisó. Un juez determinista, que lee la guía HL7 v2-to-FHIR y cita cada cosa que afirma, pasó por dos conversores **368** mensajes públicos.» | `md:ARTICULO.md` patrones `de \*\*(\.5 mg/L)\*\*` y `con \*\*(5 mg/L)\*\*`; `json:verificador/cv/CLASES-CV3.json#frase.M_mensajes` |
| `.meta` conversores | «Microsoft FHIR-Converter **v7.0** · LinuxForHealth hl7v2-fhir-converter **v1.1.0**» | `md:verificador/RESULTADO-CONVERSORES.md` patrones `Microsoft FHIR-Converter:\*\* (v7\.0)` y `hl7v2-fhir-converter:\*\* (v1\.1\.0)` |
| `.meta` referencia | la celda «Referencia» entera: «Guía HL7 v2-to-FHIR 1.0.0 (hojas CSV de `873b331`, ConceptMap del paquete), HL7 v2.5 y FHIR R4» | `md:verificador/RESULTADO-CONVERSORES.md` patrón `^\| Referencia \| (.+?) \|$` |
| `.meta` corpus | «**368** mensajes: ADT **263** · ORU **40** · **65** muestras» | `json:verificador/cv/CLASES-CV3.json#frase.M_mensajes`; `json:verificador/cv/RESULTADO-CV2.json#por_conversor.microsoft.adt.n`, `por_conversor.microsoft.oru.n`, `por_conversor.microsoft.muestras.n` |
| `.meta` juez | «resultados sellados **54a90cd9**… · cierre y rama principal **40bbc3ef**… · publicado como **0dd3ae5c**…» | `json:verificador/cv/CLASES-CV3.json#juez` patrón `^(.{8})`; `json:verificador/cv/RESULTADO-15A-minimos-main.json#juez` patrón `^(.{8})`; `md:verificador/MANIFIESTO.txt` patrón `huella del juez publicado:\s+([0-9a-f]{8})` |
| `.meta` fechas | «**23 y 24 de octubre**» | `md:verificador/RESULTADO-CONVERSORES.md` patrón `^\| Fechas \| (23 y 24 de octubre)` |
| `.indice` | enlaces a las 13 secciones | prosa |

**RESUMEN.** Caja `.tesis` con la frase fija, y debajo qué significa «confirmada».

| Elemento | Qué dice | Fuente |
|---|---|---|
| `.tesis` | «El verificador encuentra **15** discrepancias nuevas y confirmadas en **2 de 2** conversores, sobre **368** mensajes públicos; además ve **31** de las ya declaradas, y **16** diferencias son convención.» | `frase.N_nuevas_confirmadas`, `md:…RESULTADO-CONVERSORES.md` patrón `en (2 de 2) conversores`, `frase.M_mensajes`, `frase.D_ya_declaradas`, `frase.C_convenciones` (todas `json:verificador/cv/CLASES-CV3.json#…`) |
| `.tesis .une` + p | «└─ y a la vez ─ **No es una certificación.** Es lo que ve un juez determinista con sus decisiones declaradas, en esas versiones y en esos dos tipos de mensaje.» | prosa de `README.md` («Lo que no es») |
| p | «**7** son fuertes: **5** en Microsoft y **10** en LinuxForHealth.» | `frase.N_fuertes`, `frase.N_por_conversor.microsoft`, `frase.N_por_conversor.linuxforhealth` |
| `.reglas` (dl) | «Confirmada» = **cuatro** condiciones: tiene su fila CSV o su ConceptMap; cae en una de las **ocho** clases que cambian el significado; no aparece en ninguna salida esperada, prueba, documentación, comentario de plantilla, issue ni comentario de issue del proyecto; se reproduce con un par mínimo (caso y control) en la caja. | `md:…RESULTADO-CONVERSORES.md` patrón `cumple (cuatro) condiciones`; `md:ARTICULO.md` patrón `una de \*\*(ocho) clases`; las cuatro frases, prosa de `RESULTADO-CONVERSORES.md` §«La pregunta, y la respuesta» |

**01 El problema: un conversor se prueba con sus propias respuestas.** Prosa de `ARTICULO.md` §«El problema». Una cifra: las
**62** salidas esperadas de Microsoft, que juzgadas con el mismo juez dan los mismos hallazgos que su conversión real
(`md:verificador/cv/RESULTADO-CV3.md` patrón `Son (62) muestras`). Cierra con las tres cosas que hace falta que haga un juez
(lista de `ARTICULO.md`).

**02 El juez.** Prosa de `ARTICULO.md` §«El juez» (nació para juzgar circuitos propios; Python sin dependencias y sin modelo de
lenguaje; perfil «guía» con mapas del paquete y hojas citadas por fichero y fila). Tabla de las **ocho** clases:

| Columna | Fuente |
|---|---|
| Clase (8 filas: valor distinto, dato perdido, dato inventado, código mal mapeado, valor imposible convertido, recurso ausente/duplicado/inventado, referencia rota, FHIR inválido) | las ocho filas de la tabla de `ARTICULO.md` §«El juez»; cada nombre `tabla:ARTICULO.md#El juez|<clase>|Clase` |
| Ejemplo | `tabla:ARTICULO.md#El juez|<clase>|Ejemplo` |

Debajo, en `.principio`: «Lo demás es forma y no cuenta: el orden, los identificadores, los `display`, cómo se escribe una
referencia. Cuando la guía admite dos lecturas, o no decide, el juez lo declara como convención y no lo cuenta.» (prosa de
`ARTICULO.md`).

**03 El método: escribirlo todo antes de mirar.** Lista ordenada con los ocho pasos de `ARTICULO.md` §«El método», cada uno con
su enlace al documento del repositorio (S-PG-16). Cifras:

| Cifra | Fuente |
|---|---|
| la revisión adversaria tumbó **10** de las **25** candidatas | `md:verificador/cv/RESULTADO-CV3.md` patrón `romper las (25) candidatas y tumbó (10)` → dos elementos, uno por grupo (ver §2.3: `data-grupo`) |
| en la rama principal siguen **14** de las **15** | `md:verificador/cv/RESULTADO-15A.md` patrón `de las (15) nuevas, (14) siguen en la rama principal` |

Sin la cuenta de decisiones de Jev (la fuente la escribe en letras y no aporta al relato).

**04 Lo que encontró.** La sección central. Primero una línea: «Están ordenadas por fuerza, como en el estudio. Los mensajes
son los pares mínimos, sintéticos y en v2.5; lo que registró el juez es lo que registró el juez. Los Bundles que devolvieron
los conversores no se publican.» Después **15 tarjetas** `<article class="disc" id="ID">`, en el orden de la tabla «Las 15
nuevas y confirmadas» de `RESULTADO-CV3.md` (fuertes primero), bajo dos `h3`: «Las siete que más pesan» y «Las otras ocho»
(títulos de `ARTICULO.md`).

Cada tarjeta:

| Parte | Qué muestra | Fuente |
|---|---|---|
| cabecera | `Id` · conversor · fuerza (chip `.fuerza-fuerte/-media/-debil`) | `json:verificador/cv/CLASES-CV3.json#clases[id=ID].id`, `clases[id=ID].conversor`, `clases[id=ID].fuerza` (ID es el identificador de la tarjeta) |
| `h4` | la frase del artículo («Un valor que se multiplica por diez», «De un médico remitente repetido (PV1-8), solo llega el primero»…) | `md:ARTICULO.md` con el patrón de esa frase (tabla `FRASES_ARTICULO` del guion: Id → patrón; 7 negritas de §«Las siete que más pesan» y 8 celdas de §«Las otras ocho») |
| `<details>` abierto por `<summary>` «El registro del estudio, la cita y el par mínimo» | | |
| · Qué registró el estudio | la celda «Discrepancia» | `tabla:verificador/cv/RESULTADO-CV3.md#Las 15 nuevas y confirmadas|ID|Discrepancia` |
| · Cita de la guía | la celda «Guía» | `tabla:verificador/cv/RESULTADO-CV3.md#Las 15 nuevas y confirmadas|ID|Guía` |
| · Casos en el corpus | la celda «Casos» y los ejemplos | `tabla:verificador/cv/RESULTADO-CV3.md#Las 15 nuevas y confirmadas|ID|Casos`; `json:verificador/cv/CLASES-CV3.json#clases[id=ID].ejemplos.adt.0` (y `.oru.`, `.muestras.`, índices siguientes) |
| · Par mínimo `<div class="par">` | dos `<pre class="hl7">` lado a lado (apilados en teléfono): **caso** y **control**, con el segmento que difiere en `<mark>`; debajo, por conversor: categoría del caso, del control, y lo que dijo el juez en el caso (hasta dos líneas); y «confirmada: sí/no» | `hl7:PAR#caso`, `hl7:PAR#control`; `json:verificador/cv/RESULTADO-CV3-minimos.json#pares[id=PAR].CONV.caso.categoria`, `pares[id=PAR].CONV.control.categoria`, `pares[id=PAR].CONV.caso.que.0`, `pares[id=PAR].CONV.caso.que.1` (si existe), `pares[id=PAR].confirmada` (PAR es el identificador del par y CONV, `microsoft` o `linuxforhealth`) |
| · En la rama principal | la celda «Rama principal» de 15A («**sigue**» o «**corregida** (`master` da «entered-in-error»)») | `tabla:verificador/cv/RESULTADO-15A.md#Cada nueva, en la versión fijada y en la rama principal|ID|Rama principal` |

El par de cada Id sale de `clases[id=ID].par_minimo`; `L-16` tiene dos («L07-ft / L08-tm»), separados por « / », y se
muestran los dos. El `<mark>` lo calcula el guion con `difflib.SequenceMatcher` sobre la lista de segmentos (lo que no está en
el otro mensaje se marca); no es una cifra y no lleva fuente. Si Q-PG-D-3 dice «solo el conversor objetivo», la tabla de
veredictos tiene una fila; si dice «los dos», dos.

Cierra la sección un bloque «Matices que deja la revisión» con los cinco puntos de `RESULTADO-CV3.md` (M-18, L-11, L-22, L-1,
L-12 y L-19), copiados como prosa con fuente `md:` por frase, y la línea del artículo: «Los dos conversores son proyectos
serios y útiles. Las discrepancias son con una guía concreta, en una versión concreta.»

**05 En la rama principal.**

| Elemento | Qué dice | Fuente |
|---|---|---|
| p | «De las **15** nuevas, **14** siguen en la rama principal y **una** está corregida allí.» | `md:verificador/cv/RESULTADO-15A.md` patrón `de las (15) nuevas, (14) siguen en la rama principal y (una) está corregida` (tres grupos) |
| p | L-18: «borrado» que pasaba a «cancelado»; LinuxForHealth lo cambió por su cuenta, después de la versión juzgada, y ninguna versión publicada lo lleva | prosa de `ARTICULO.md` y `RESULTADO-15A.md`; la fecha del commit, `tabla:…RESULTADO-15A.md#15a|Rama y commit|LinuxForHealth` |
| tabla | rama y commit, cómo se construye, cómo corre, por conversor | `tabla:verificador/cv/RESULTADO-15A.md#15a|<fila>|Microsoft` y `|LinuxForHealth` para «Rama y commit», «Cómo se construye», «Cómo corre» (la celda entera, con su `code`) |
| p | las dos ramas difieren solo en dos mensajes de los **68** | `md:…RESULTADO-15A.md` patrón `En los (68) mensajes, las dos ramas se diferencian solo en dos` |

**06 Lo que los proyectos ya sabían.** «Las **31** ya declaradas son el control positivo: si el juez no viera lo que los
autores ya saben, nada de lo demás valdría.» (`frase.D_ya_declaradas`; prosa de `ARTICULO.md`). Dos `<details>`: «Microsoft
(**19**)» y «LinuxForHealth (**12**)» (`frase.D_por_conversor.*`), cada uno con una tabla de tres columnas, una fila por
mecanismo de `CLASES-CV3.json` con `clase == "ya_declarada"` y ese conversor, en el orden del fichero: `id`, `que`,
`referencia` (`json:verificador/cv/CLASES-CV3.json#clases[id=ID].que` y `clases[id=ID].referencia`). Delante, los cinco ejemplos que da el artículo, como prosa. Si
Q-PG-D-2 dice «solo cifras», los `<details>` se sustituyen por la cifra y el enlace a `RESULTADO-CV3.md`.

**07 Lo que no cuenta.**

| Bloque | Qué dice | Fuente |
|---|---|---|
| convenciones | «**16** diferencias son convención: **14** mecanismos de nota del juez final, por conversor, más PV1-19 «VN» en los dos.» Debajo, las cuatro formas que resume `RESULTADO-CV3.md` (status sin destino en el ConceptMap; OBX-5 repetido en una forma que la guía admite; interpretation y maritalStatus fuera del ConceptMap; gender en minúscula) | `frase.C_convenciones`; el **14** no se cuenta de las claves de `CLASES-CV3.json#convenciones` (S-PG-3): se toma literal, `md:verificador/cv/RESULTADO-CV3.md` patrón `Son (14) mecanismos de nota`; las cuatro formas, prosa de esa sección. La lista de firmas del JSON no se copia (sus claves llevan puntos y barras); se enlaza |
| rechazos nuevos | «**2** rechazos nuevos, que no entran en la frase porque fallan a la vista»; `<details>` con los pares R01 y R02 (mismo bloque `.par` que en 04) | `frase.rechazos_nuevos`; descripción `json:verificador/cv/CLASES-CV3.json#clases[id=M-12].que` y `clases[id=M-15].que`; mensajes `hl7:R01-nulo-en-dtm#caso`, `hl7:R01-nulo-en-dtm#control`, `hl7:R02-nm-cero-inicial#caso`, `hl7:R02-nm-cero-inicial#control` |
| dudosas | «**3** dudosas, que no cuentan»: el formato del teléfono (Q-CV-D-15, empate) y el comparador «<>» (Q-CV-D-16) | `frase.dudosas`; prosa de `RESULTADO-CV3.md` §«Lo que no cuenta» |
| las 10 que cayeron | `<details>` con la tabla «Id · Por qué cae · Cita» | `tabla:verificador/cv/RESULTADO-CV3.md#Las 10 que cayeron en la revisión|ID|Por qué cae` y `|Cita`, para los diez Id (M-9, M-16, M-21, M-25, L-6, L-21, L-23, L-24, L-25, L-26) |
| fuera, con motivo | tabla «Motivo · Ids · Qué» | `tabla:…RESULTADO-CV3.md#Fuera, con motivo|<Motivo>|Ids` y `|Qué` |

**08 Lo que el juez se equivocó, y se corrigió.** Prosa de `ARTICULO.md`: «se le encontraron **once** defectos, cada uno
arreglado con su prueba en rojo antes del código»: **4** al revisar el primer juicio, **4** en los que la guía admitía lo
observado, **3** que dejó el contraste; el falso positivo de CX.4 como ejemplo. Fuentes: `md:ARTICULO.md` patrones
`encontraron \*\*(once) defectos`, `\*\*(4), al revisar el primer juicio`, `\*\*(4) en los que la guía admitía`,
`\*\*(3) que dejó el contraste`. Debajo, la tabla «Qué cambió en el juez» de `RESULTADO-CONVERSORES.md` (`tabla:…#Qué cambió
en el juez durante la etapa|<Fase>|Huella` y `|Qué`), y en `.principio`: «Lo que no se hizo fue mover la previsión.»

**09 La previsión sellada, frente a lo que salió.** Una figura SVG (Q-PG-D-4) y dos tablas.

| Elemento | Qué muestra | Fuente |
|---|---|---|
| `<figure><svg role="img" aria-label="…">` | cuatro barras apiladas (Microsoft · ADT, Microsoft · ORU, LinuxForHealth · ADT, LinuxForHealth · ORU), tramos `correcto` / `fallo_silencioso` / `rechazo_incorrecto`, anchura proporcional a `n`; a la derecha de cada barra, su etiqueta | geometría: `json:verificador/cv/RESULTADO-CV2.json#por_conversor.CONV.FAM.categorias.CAT` y `por_conversor.CONV.FAM.n` (no se muestran; FAM es `adt` u `oru` y CAT una de las tres categorías); etiquetas `<text data-fuente=…>`: las celdas de `tabla:verificador/cv/RESULTADO-CV2.md#Lo que salió, frente a lo previsto|<Conversor · familia>|correcto`, `|fallo_silencioso`, `|rechazo_incorrecto` («6 (2,3 %) [35-65]»…) |
| `figcaption` | «Entre corchetes, el rango sellado antes de correr nada. Los `correcto` de ADT salieron por debajo del rango en los dos; los rechazos, por encima. En ORU, Microsoft salió por encima y LinuxForHealth por debajo.» | prosa de `RESULTADO-CV2.md` (las celdas ya traen el rango) |
| tabla «La frase prevista» | N / K / D / C: previsto y salió | previsto: `json:verificador/cv/PREVISION-CV2.json#frase_prevista.N` («>= 2», se muestra tal cual con `≥` → ver §2.3, normalización) …; salió: `frase.N_nuevas_confirmadas`, `frase.K_conversores`, `frase.D_ya_declaradas`, `frase.C_convenciones` |
| p | la adjudicación de los rechazos: 30 de Microsoft son un defecto del corpus (GT1 desplazado); los de LinuxForHealth, eventos sin soporte | `json:verificador/cv/CLASES-CV3.json#clases[id=M-11].casos.adt` (30) y `clases[id=M-11].que`; `clases[id=L-4].casos.adt` (92) y `clases[id=L-4].referencia` |

**10 Pasa tu conversor por el mismo juez.**

| Elemento | Qué dice | Fuente |
|---|---|---|
| `pre` | `python3 cv/verificar_conversor.py <adaptador.json> <carpeta de salida> --artefactos <carpeta con el conversor>` | `md:verificador/cv/VC.md` patrón ```` ```bash\n(python3 cv/verificar_conversor\.py .+?)\n``` ```` |
| lista «hace cinco cosas» | las cinco líneas del README del verificador | `md:verificador/README.md` patrones `^1\. (corre el conversor .+);$` … `^5\. (escribe .+)\.$` |
| `.principio` «Lo que la herramienta no puede saber» | el texto entero del aviso del informe | `json:verificador/cv/vc/ejemplos/INFORME-microsoft.json#contraste_con_el_proyecto.texto` (Markdown → HTML: `**`→`strong`, backticks→`code`) |
| tabla «El control» | casos comparados **368** y **368**; diferencias **0** y **0**; pares mínimos: coinciden los **34** | `tabla:verificador/cv/vc/CONTROL-VC.md#VC3|Casos comparados|Microsoft`, `|LinuxForHealth`; `…|Diferencias|…`; `md:verificador/cv/VC.md` patrón `coinciden los (34)` |
| «El adaptador»: cinco bloques y lo que se cambia | prosa de `VC.md` §«Cómo se usa» (copiar uno de `adaptadores/`, cambiar nombre, versión y huella; imagen y montajes solo lectura; la orden con sus marcadores; cómo se lee la salida) | prosa; el ejemplo de adaptador se enlaza (`adaptadores/juguete.json`), no se incrusta |
| «La caja» | las siete restricciones | `json:verificador/cv/vc/ejemplos/INFORME-microsoft.json#caja.restricciones.0` … `caja.restricciones.6` |
| tabla «Códigos de salida» | 0, 2, 3, 4, 5, 1 y su significado | `tabla:verificador/cv/VC.md#Los códigos de salida|<código>|Qué quiere decir` |
| «Dos informes de ejemplo» | enlaces a `INFORME-microsoft.md` e `INFORME-linuxforhealth.md`, con la nota de la huella del juez publicado | prosa de `VC.md`; huellas, `md:verificador/MANIFIESTO.txt` (como en la meta) |
| «Lo que no hace» (`.limites`) | L-VC-1, L-VC-2, L-VC-3, L-VC-4, L-VC-7, L-VC-15, texto entero | `json:verificador/cv/vc/ejemplos/INFORME-microsoft.json#limites.L-VC.L-VC-1` … `limites.L-VC.L-VC-15` |

**11 Lo que esto no dice.** Lista `.limites` (el «no» en el margen, como en la primera página), con el texto de
`ARTICULO.md` §«Lo que esto no dice» y `RESULTADO-CONVERSORES.md` §«Lo que el resultado no dice», completo:
- no es una certificación de conformidad;
- las versiones: Microsoft FHIR-Converter **v7.0**; LinuxForHealth hl7v2-fhir-converter **v1.1.0**, la última en Maven
  Central (GitHub tiene una **v1.1.1** y una rama principal que soportan más eventos; la v1.1.0 rechaza **tres** de los
  **ocho** eventos ADT probados, y eso se contó como rechazo); las ramas principales tal como estaban en octubre de 2026;
- cubre **ocho** eventos ADT y ORU^R01; no SIU, MDM, VXU ni los demás;
- los mensajes son sintéticos o públicos;
- el juez lee los tipos de datos de v2.5; las muestras de los proyectos son casi todas de v2.8;
- los límites declarados del juez siguen en pie (L-CV-14, L-CV-15, L-CV-16, AMB-CV-10) y dos preguntas siguen abiertas
  (Q-CV-D-15 y Q-CV-D-16);
- los dos conversores son proyectos serios y útiles.

Fuentes: `md:ARTICULO.md` patrones por frase (`rechaza (tres) de los (ocho) eventos`, `Cubre (ocho) eventos ADT`, `etiqueta
(v1\.1\.1)`); los L-CV, `json:verificador/cv/vc/ejemplos/INFORME-microsoft.json#limites.L-CV.0` (y siguientes) si el fichero lleva el texto, y si solo lleva los
identificadores, prosa de `RESULTADO-CONVERSORES.md`.

**12 Cómo reproducirlo.** Prosa de `ARTICULO.md` §«Cómo reproducirlo»: Python 3 y nada más para el juez; las **116**
comprobaciones del perfil «guía» (`md:ARTICULO.md` patrón `las (116) comprobaciones`); Docker, los dos conversores, las muestras
y el paquete `hl7.fhir.uv.v2mappings` para repetir el estudio; «Los **68** mensajes mínimos salen de `python3
verificador/cv/cv3_minimos.py escribir <carpeta>`» (`md:ARTICULO.md` patrón `Los (68) mensajes mínimos`).

**Pie.** «En este repositorio no hay datos de ningún paciente: los mensajes son sintéticos o ejemplos del propio estándar. El
verificador no es una herramienta de conformidad certificada. El código va bajo MIT y los documentos bajo CC BY 4.0. HL7® y
FHIR® son marcas registradas de Health Level Seven International. Este laboratorio no tiene relación con los proyectos
juzgados.» (prosa de `README.md` §Aviso y del pie de `ARTICULO.md`; «4.0» se escribe dentro de un `data-fuente`
`md:ARTICULO.md` patrón `los documentos bajo CC BY (4\.0) \(`, que en ese fichero casa una sola vez; en `LICENSE.md` casaría
varias). Y el párrafo final al repositorio, como en la primera página.

### 2.3 El contrato de las fuentes (`data-fuente`)

Cualquier elemento puede llevarlo (`<data>`, `<span>`, `<td>`, `<pre>`, `<text>` dentro del SVG, `<time>`). El texto que el
elemento muestra tiene que coincidir con lo que la fuente dice.

```
data-fuente="json:<ruta>#<puntero>"       <puntero> = claves e índices separados por «.» (no por «/»: la guarda de
                                          rutas de máquina leería «clases[id=M-24]» seguido de «/casos» y «/adt» como una ruta); ninguna clave que la
                                          página usa lleva punto;
                                          un paso «lista[clave=valor]» elige el elemento de la lista cuyo campo «clave»
                                          vale «valor» (clases[id=M-24], pares[id=L06-obx-sin-tipo])
data-fuente="md:<ruta>"                   exige data-patron; se busca en el texto del fichero con re.M;
                                          tiene que haber exactamente UNA coincidencia; se compara el grupo
data-fuente="tabla:<ruta>#<línea>|<fila>|<columna>"
                                          la primera tabla Markdown que sigue a la primera línea del fichero que
                                          contiene <línea>; la fila cuya primera celda es <fila>; la columna que se
                                          llama <columna> (nombres sin backticks). Celda sin «**», sin backticks,
                                          «\|» → «|», espacios colapsados
data-fuente="hl7:<id del par>#caso|control"
                                          el mensaje de cv3_minimos.PARES, con «\r» → «\n»; solo en <pre class="hl7">
data-patron="<regex con grupos>"          opcional para json (sobre el valor como texto) y obligatorio para md
data-grupo="2"                            qué grupo del patrón muestra este elemento (por omisión, el 1)
value="<valor>"                           solo en <data>; para json numéricos, str(valor)
```

**Comparación.** Texto del elemento = `html.unescape` de su contenido sin etiquetas (los `<mark>`, `<code>` y `<strong>`
interiores se quitan), espacios colapsados, sin espacios finos ni duros. Valor de la fuente, según el tipo:
- json número → `str`; el texto se compara tras cambiar la coma decimal por punto («2,3» ↔ `2.3`);
- json booleano → «sí» / «no»;
- json cadena → tal cual, o el grupo de `data-patron`;
- md → el grupo; tabla → la celda normalizada; hl7 → el mensaje.
- Tres sustituciones tipográficas se admiten en los dos sentidos: `>=` ↔ `≥`, `<=` ↔ `≤`, `->` ↔ `→`.

El guion los escribe con tres ayudantes: `cifra(fuente, patron=None)` → `<data value=… data-fuente=…>texto</data>`;
`texto(fuente, patron=None, md=False)` → `<span data-fuente=…>…</span>` (con `md=True` convierte `**`, backticks y `«»`);
`hl7(par, cual, otro)` → `<pre class="hl7" data-fuente="hl7:…">` con `<mark>`. Los tres **resuelven la fuente al generar**:
si un puntero o un patrón no resuelve, el guion para con error y no escribe nada. La guarda (§5) vuelve a resolverlos con
su propio código, sin importar el guion.

### 2.4 Lo interactivo, sin JavaScript

| Qué | Cómo | Teclado |
|---|---|---|
| Desplegar cada discrepancia (registro, cita, par, rama principal) | `<details><summary>` | `summary` recibe el foco; Intro/Espacio abre |
| Desplegar las listas largas (31 declaradas, 10 caídas, rechazos) | `<details>` | ídem |
| Ir a una discrepancia por enlace (`#M-24`) | `id` en cada `<article>`; `.disc:target { outline: 2px solid var(--accent) }`; `scroll-margin-top: 1rem` | los enlaces del índice y de la prosa |
| Ver el disparador del par | `<mark>` en el segmento que difiere; `.par` en dos columnas (`grid`) que pasan a una bajo 720 px | no interactivo |
| Saltar al contenido | `.salto`, fuera de pantalla hasta `:focus` | primer Tab |
| Volver a la primera página | `.volver` arriba y enlace en el pie | enlace |
| Tema | `prefers-color-scheme` + `:root[data-theme]`, como la primera página; sin botón | no aplica |
| Impresión | `@media print`: ocultar `.salto`, `.indice`; los `<details>` cerrados no se abren (L-PG-3) | no aplica |

Reglas de accesibilidad que la guarda comprueba (§4): `lang="es"`; `viewport`; `color-scheme`; cada `<details>` con
`<summary>`; cada `<svg>` con `role="img"` y `aria-label`; ningún `tabindex` positivo; `:focus-visible` definido; sin
`on…=` ni `javascript:`; el `<h1>` único y los `h2`/`h3`/`h4` en orden.

### 2.5 Estilo, claro y oscuro, teléfono

- Tokens y tipografía copiados de `docs/index.html` (líneas del `<style>` del cuerpo): `--ground`, `--surface`, `--ink`,
  `--ink-soft`, `--ink-faint`, `--rule`, `--rule-firm`, `--accent`, `--accent-w`, `--warn`, `--warn-w`, `--good`, y las tres
  familias (`--serif` Newsreader, `--sans` Public Sans, `--mono` JetBrains Mono). Oscuro con `@media (prefers-color-scheme:
  dark) { :root:not([data-theme="light"]) … }` y `:root[data-theme="dark"]`, los mismos valores.
- Nuevo: `mark { background: var(--warn-w); color: var(--ink); box-shadow: inset 0 -2px var(--warn) }`; `.fuerza-fuerte`
  con `--warn`, `.fuerza-media` con `--accent`, `.fuerza-debil` con `--ink-faint`; `.disc` con `border-top: 1px solid
  var(--rule)` y `padding-block: 1.2rem`; `.par pre` con `font-size: .78rem`, `white-space: pre`, `overflow-x: auto`
  (un segmento HL7 no se parte: partirlo engaña).
- Teléfono: `.wrap` a 50rem con 20 px de margen; `.meta` con `flex-wrap`; `.tabla-caja { overflow-x: auto }` en toda
  tabla; `.par` en una columna bajo 720 px; la figura SVG con `viewBox` y `width: 100%`; tamaños de letra como la primera
  página.
- Figura: `.barras .correcto { fill: var(--good) }`, `.fallo { fill: var(--warn) }`, `.rechazo { fill: var(--rule-firm) }`;
  textos con `font-family: var(--sans)`/`var(--mono)` como `.escalera` en la primera página.

---

## 3. Cómo se construye

### 3.1 El generador: `codigo/hacer_pagina_conversores.py`

```
python3 codigo/hacer_pagina_conversores.py                  # escribe docs/conversores/index.html
python3 codigo/hacer_pagina_conversores.py --comprobar      # regenera en memoria y compara con el fichero: IGUAL / DISTINTA
python3 codigo/hacer_pagina_conversores.py --comprobar <f>  # compara con otro fichero (lo usa el control negativo)
```

- Solo biblioteca estándar (`json`, `re`, `html`, `difflib`, `string`, `pathlib`, `importlib`). Python 3.12, como la CI.
- Lee únicamente los ficheros de §0, por rutas relativas a la raíz del repositorio (`REPO = Path(__file__).resolve().parent.parent`).
- Importa `verificador/cv/cv3_minimos.py` con `importlib.util.spec_from_file_location` (el módulo mete su carpeta en
  `sys.path` al cargarse; no importa el juez: `juzgar_cv2` y `mcp_verificador` solo se importan dentro de `juzgar()`).
- La plantilla es una cadena `string.Template` (`$marcador`), para que los `%` del CSS no estorben; al final, `assert "$" not in
  salida_sin_estilo` (ningún marcador sin rellenar).
- Determinista: sin fecha de generación, sin rutas de máquina, orden de los ficheros JSON tal cual, `sorted` donde haya
  conjuntos. Dos ejecuciones dan el mismo fichero byte a byte; `newline="\n"`, UTF-8.
- Todo texto que viene de un fichero pasa por `html.escape` antes de convertir Markdown en línea (`**`→`<strong>`, backticks
  →`<code>`). Los `que` del juez llevan comillas y `<>`; sin escape romperían la página.
- `FRASES_ARTICULO`: la única tabla a mano del guion: `{Id: patrón en ARTICULO.md}` para las 15 (siete negritas y ocho celdas).
  Cada patrón se resuelve contra el artículo al generar (si una frase cambiara de texto, el guion pararía).
- Salida: `docs/conversores/index.html`. Código de salida: `0` escrita o IGUAL; `1` DISTINTA (imprime la primera línea que
  difiere); `2` una fuente no resuelve (imprime fichero, puntero o patrón).

### 3.2 Dónde vive y con qué URL

| | |
|---|---|
| Fichero | `docs/conversores/index.html` |
| URL | `https://lk-corporation.github.io/lab-integraciones/conversores/` (GitHub Pages ya sirve `docs/` para la primera) |
| Fuentes | `../fonts/fuentes.css` (relativo; `test_los_enlaces_relativos_resuelven` lo comprueba) |
| `canonical`, `og:url` | la URL de arriba |
| Generador | `codigo/hacer_pagina_conversores.py`, al lado de `codigo/hacer_pagina.py` |
| Licencias | la página, CC BY 4.0 («cualquier `.html`»); el guion, MIT («cualquier `.py`»). `LICENSE.md` cambia «la página `docs/index.html`» por «las páginas de `docs/`» |
| Tamaño previsto | 90-140 KB (15 tarjetas con 16 pares, 31 declaradas, 10 caídas, la figura); muy por debajo de los 512 KB de la guarda |

### 3.3 Enlaces desde `docs/index.html` y desde el README

**`docs/index.html`**, en el párrafo final (el que empieza «El código, el diseño, las revisiones externas…»), añadir una
segunda frase:

```html
  Hay una segunda p&aacute;gina, del estudio de conversores (octubre de 2026):
  <a href="conversores/" style="color:var(--accent)">un juez que no se f&iacute;a del conversor</a>.
```

y lo mismo en `PIE` de `codigo/hacer_pagina.py`, para que regenerar la primera página no lo pierda. Nada más de
`docs/index.html` cambia (Q-PG-D-5 decide si además va una línea bajo la cabecera).

**`README.md`**, en «Por dónde empezar», la viñeta de `ARTICULO.md` pasa a:

```
- **El estudio de conversores, contado de corrido:** [`ARTICULO.md`](ARTICULO.md). Qué encontró el verificador en dos
  conversores de código abierto, cómo se buscó sin fiarse de ellos y qué no dice. Hay una versión para leer en el navegador,
  con el par de mensajes mínimos de cada discrepancia, en
  [lk-corporation.github.io/lab-integraciones/conversores](https://lk-corporation.github.io/lab-integraciones/conversores/).
```

La fila de `docs/` no existe en la tabla «Qué hay aquí» y no hace falta añadirla: la carpeta ya se explica en la viñeta de
`INFORME.md`. `test_el_readme_cuenta_bien_encargos_y_revisiones` y `test_todo_documento_es_alcanzable_desde_el_readme` no se
ven afectados (la página no es `.md`).

---

## 4. La prueba de higiene nueva

Va en `tests/test_repo_hygiene.py`, con el resto, y corre sin red ni Docker. Tres funciones y sus controles.

### 4.1 `test_la_pagina_de_conversores_no_lleva_cifras_sueltas`

**Qué comprueba exactamente.** Que en `docs/conversores/index.html` **no hay ningún dígito ni ninguna palabra-número fuera
de un elemento con `data-fuente`**, salvo los identificadores de la lista blanca.

Procedimiento, sobre el texto del fichero:
1. Quitar comentarios HTML, `<style>…</style>`, y los atributos de todas las etiquetas (se conservan `<title>` y el
   `content` de `<meta name="description">`, que se analizan aparte con la misma regla).
2. Quitar entero cada elemento que lleve `data-fuente` (con su contenido), y cada `<pre class="hl7">`.
3. Quitar las etiquetas restantes y deshacer entidades.
4. En el texto que queda, cada secuencia de dígitos y cada palabra-número tiene que estar dentro de un token de la lista
   blanca; si no, es un fallo con su contexto (20 caracteres a cada lado).

Lista blanca, **solo identificadores, nunca cantidades**:

| Clase | Patrón | Ejemplos |
|---|---|---|
| nombres del estándar | `\bHL7\b`, `\bv2(\.\d)?\b`, `\bR4\b`, `\bv2-to-FHIR\b`, `\bv3-[A-Za-z]+\b`, `\bv2-0\d{3}\b`, `\bhl70\d{3}\b` | HL7, v2.5, FHIR R4, v3-MaritalStatus |
| campo y componente HL7 | `\b[A-Z][A-Z0-9]{1,2}(\(\d+\))?-\d{1,2}(\.\d{1,2})?\b`, `\b[A-Z]{2,3}\.\d{1,2}\b` | PV1-3, OBX(2)-3, MSH-9.3, SAD.2, CX.4, XTN.12 |
| evento y estructura | `\b(ADT|ORU|SIU|MDM|VXU|ORM)(\^|_)[A-Z]\d{2}\b`, `\bA\d{2}\b`, `\bR01\b` | ADT^A02, ORU_R01, A01 |
| tablas de HL7 | `\b0\d{3}\b` | 0002, 0136 |
| identificadores del laboratorio | `\b(Q|L|S|DV|P|MC|AMB|E)-[A-Z]{1,3}(-[A-Z]{1,3})?-\d{1,3}\b`, `\b[ML]-\d{1,2}\b`, `\b[MLR]\d{2}[a-z]?\b` | Q-CV-D-15, L-VC-1, M-24, L06 |
| referencias a issues | `#\d+\b` | #624 |
| huellas y commits | `\b(?=[0-9a-f]*[a-f])[0-9a-f]{7,64}\b` | 40bbc3ef, 253307f |
| palabras-número vigiladas | `\b(tres|cuatro|cinco|seis|siete|ocho|nueve|diez|once|doce|trece|catorce|quince|diecis[eé]is|diecisiete|dieciocho|diecinueve|veinte|treinta|cuarenta|cincuenta|sesenta|setenta|ochenta|noventa|cien|ciento|mil)\b` (insensible a mayúsculas) | fallan si no llevan fuente |

«dos», «un» y «una» **no** se vigilan: «los dos conversores» es la identidad del estudio y «un/una» son artículos (L-PG-6).
El `<title>` y la descripción se analizan con la misma lista: no pueden llevar cifras (S-PG-15).

**Control negativo (`test_la_guarda_de_cifras_ve_una_cifra_suelta`).** La misma función, aplicada a tres copias en memoria:
- la página con `<p>Se juzgaron 42 casos.</p>` insertado antes de `</main>` → exactamente un fallo, que contiene «42»;
- la página con `<p>Cuatro condiciones.</p>` → un fallo con «Cuatro»;
- la página con la descripción cambiada a «… 15 discrepancias …» → un fallo con «15».
Y una copia con `<p>PV1-3, ORU^R01, A02, #624 y 40bbc3ef</p>` → **cero** fallos (la lista blanca deja pasar identificadores).

### 4.2 `test_la_pagina_de_conversores_es_la_que_genera_su_guion`

**Qué comprueba.** `subprocess.run([sys.executable, "codigo/hacer_pagina_conversores.py", "--comprobar"], cwd=REPO)` sale con
`0` y su salida contiene `IGUAL`. Es la misma idea que `contratos/generar_contrato.py --comprobar` para el contrato del canónico.

**Control negativo.** Se copia la página a un fichero temporal (`tempfile`, no una fixture: el fichero también corre sin
pytest), se cambia un carácter de un `<data>` (el primer `>15<` por `>16<`), y `--comprobar <temporal>` tiene que salir con
`1` y decir `DISTINTA`.

### 4.3 Lo que se añade a las guardas que ya existen

- `test_la_pagina_no_carga_nada_externo` ya recorre `docs/**/*.html`; se le añaden dos comprobaciones a cada página:
  ningún atributo `on\w+=` y ningún `href="javascript:`.
- Nueva `test_las_paginas_son_accesibles_sin_javascript`, para todo `docs/**/*.html`: `lang="es"`, `viewport`,
  `color-scheme`, un solo `<h1>`, cada `<details>` con `<summary>`, cada `<svg>` con `role="img"` y `aria-label`, ningún
  `tabindex="[1-9]`. La primera página la pasa tal como está (tiene un SVG con `role` y `aria-label`, y ningún `details`).
- `JSON_ADMITIDOS`, `RAIZ_ADMITIDA`, `SUFIJOS_ADMITIDOS` no cambian: la página es `.html` bajo `docs/` y el guion `.py` bajo
  `codigo/`.

---

## 5. Las pruebas de que la página dice lo que dicen los documentos

### 5.1 `test_toda_cifra_de_la_pagina_de_conversores_tiene_fuente_y_coincide`

**Qué comprueba.** Para **cada** elemento con `data-fuente` de la página (se esperan más de doscientos), resuelve la fuente
con un resolutor propio de la guarda (unas cuarenta líneas, **sin importar el guion**) y exige que el texto mostrado coincida
según el contrato de §2.3. Además:
- cada `data-fuente` apunta a un fichero **rastreado por git** dentro del repositorio (no vale un fichero del laboratorio);
- un patrón `md:` tiene exactamente una coincidencia (dos sería ambigüedad; cero, cita rota);
- un `<pre class="hl7">` siempre lleva `data-fuente="hl7:…"`, y su texto es el de `cv3_minimos.PARES` (importado por ruta,
  como en el guion); así los 34 mensajes de la página son los del estudio;
- un `<data>` con `value` numérico muestra ese número (con coma decimal, si la tiene).

El fallo dice el elemento (sus primeros 60 caracteres), la fuente y los dos textos.

**Control negativo (`test_la_guarda_de_fuentes_ve_un_cambio`).** Sobre copias en memoria:
- cambiar el texto de un `<data>` (el `15` de la frase por `16`) → un fallo que nombra `frase.N_nuevas_confirmadas`;
- cambiar un `data-fuente` a un puntero inexistente (`frase.N_inventada`) → un fallo «no resuelve»;
- cambiar un carácter de un `<pre class="hl7">` → un fallo que nombra el par;
- cambiar un `data-patron` por uno que case dos veces (`(\d+)`) → un fallo «ambiguo».

### 5.2 `test_las_tablas_de_la_pagina_de_conversores_estan_completas`

**Qué comprueba.** Que la página no deja fuera nada que el estudio cuenta ni mete nada que no cuenta:
- hay exactamente un `<article class="disc" id=…>` por cada `clase == "nueva"` de `CLASES-CV3.json`, con esos mismos `id`,
  en el orden de la tabla «Las 15 nuevas y confirmadas» de `RESULTADO-CV3.md`; y ninguno más;
- la tabla de las 31 declaradas tiene una fila por `clase == "ya_declarada"` (19 y 12 por conversor), y ninguna más;
- la tabla de las caídas tiene las diez filas de la sección «Las 10 que cayeron»;
- la tabla de las ocho clases tiene las ocho filas de `ARTICULO.md`, y los ocho nombres coinciden con las ocho claves de
  `mecanismos` de `INFORME-microsoft.json` tras pasar de `snake_case` a palabras (`recurso` ↔ «recurso ausente, duplicado o
  inventado» se admite como la única excepción, escrita en la prueba);
- el texto de cada `<pre class="hl7">` del par de una discrepancia es el del `par_minimo` de su `clases[id=…]`.

**Control negativo.** Quitar un `<article>` → fallo que nombra el `id` que falta; duplicar uno → fallo «de más»; cambiar el
orden de dos → fallo «orden».

### 5.3 `test_la_pagina_de_conversores_cuadra_con_la_rama_principal`

**Qué comprueba.** Coherencia entre las dos fuentes de «rama principal» que la página usa: para cada nueva, la celda «Rama
principal» de `RESULTADO-15A.md` empieza por «sigue» si y solo si `pares[id=PAR].confirmada` es `true` en
`RESULTADO-15A-minimos-main.json` (para L-16, los dos pares). Hoy: 14 «sigue», 1 «corregida» (L-18, par L09). Si un día se
publicara un 15A nuevo con otra cuenta, la página no podría decir «14» sin tocar su fuente.

**Control negativo.** Con una copia del JSON en memoria donde `L09-obx-11-d` pasa a `true` → fallo que nombra L-18.

### 5.4 Lo que **no** se prueba mecánicamente (y quién lo mira)

La prosa de enlace y la asociación Id ↔ frase del artículo (`FRASES_ARTICULO`) no tienen oráculo mecánico. Las mira la
revisión a ciegas de la fase PG4, con una consigna fija: «Cada afirmación sobre Microsoft o LinuxForHealth, ¿está en
`ARTICULO.md`, `RESULTADO-CONVERSORES.md` o `RESULTADO-CV3.md` con el mismo sentido? ¿Cada frase del artículo está junto a
la discrepancia que describe?» Lo que no pase se quita, no se matiza (L-PG-1, L-PG-2).

---

## 6. Preguntas de diseño para Jev (Q-PG-D-n)

Solo las que no deciden ni la pregunta ni las condiciones. Cada una con sus opciones y qué cambia. La recomendación va aparte
(§7), para que el estado que lea Jev sea neutro.

| Q | Pregunta | Opciones | Qué cambia según la respuesta |
|---|---|---|---|
| Q-PG-D-1 | ¿Qué título lleva la página? | (a) «Un juez que no se fía del conversor»; (b) «Lo que vio un juez en dos conversores»; (c) «Quince discrepancias con cita» | `<title>`, `og:title`, `h1` y el texto del enlace en el pie de la primera página. (c) lleva una palabra-número y tendría que ir con fuente `md:` dentro del `h1`; (a) y (b) no llevan cifra |
| Q-PG-D-2 | Las 31 ya declaradas y las 10 que cayeron, ¿con su lista en la página o solo con la cifra y el enlace? | (a) listas completas en `<details>` (id, qué, dónde lo declara); (b) solo las cifras, los cinco ejemplos del artículo y el enlace a `RESULTADO-CV3.md` | (a) añade unos 12 KB y 41 filas con texto de los proyectos (todo de `CLASES-CV3.json`); (b) deja el «control positivo» como afirmación sin su tabla. La guarda 5.2 cambia: con (b) no comprueba las 31 ni las 10 |
| Q-PG-D-3 | En cada par mínimo, ¿se muestra el veredicto de los dos conversores o solo el del conversor para el que se escribió? | (a) los dos (dos filas: categoría del caso, del control, y lo que dijo el juez); (b) solo el objetivo | (a) enseña que el otro conversor no muestra el mecanismo (o sí: M05, L03, L12 lo muestran en los dos), con la advertencia de L-VC-15; (b) una fila menos por tarjeta y una lectura menos comparativa |
| Q-PG-D-4 | ¿Lleva la sección 09 la figura de barras, o solo la tabla? | (a) SVG de cuatro barras apiladas con las celdas de `RESULTADO-CV2.md` como etiquetas; (b) la tabla de `RESULTADO-CV2.md` tal cual, sin figura | (a) unas 40 líneas de geometría en el guion y un `aria-label` largo; (b) nada que escalar, la misma información |
| Q-PG-D-5 | ¿Desde dónde enlaza la primera página a la segunda? | (a) solo desde su párrafo final; (b) también con una línea bajo su `.meta` («Hay una segunda página…») | (b) toca el cuerpo de `docs/index.html` (hasta hoy, intacto desde su publicación) y pide la misma línea en `hacer_pagina.py` |
| Q-PG-D-6 | ¿Un filtro por conversor sobre las 15 tarjetas, con dos radios y CSS, o ninguno? | (a) ninguno; (b) radios `name="conv"` antes de la lista y reglas `:checked ~ … [data-conv] { display: none }` | (b) añade una interacción no estándar que hay que probar con teclado y lector de pantalla, y oculta tarjetas con `display: none` (no se encuentran con la búsqueda del navegador) |

---

## 7. La recomendación del diseñador (aparte del estado)

Q-PG-D-1 (a): es el hilo del artículo («sin fiarse del conversor») y no nombra a un proyecto en el título. Q-PG-D-2 (a): el
control positivo es un argumento y hay que poder leerlo; todo el texto ya es público en `CLASES-CV3.json`. Q-PG-D-3 (a): el
JSON lo trae y L-VC-15 pide decirlo. Q-PG-D-4 (a): es el único «salieron por mucho» de la página y una barra lo cuenta en un
golpe de vista; las etiquetas son celdas literales, así que la figura no introduce ninguna cifra. Q-PG-D-5 (a): mínimo cambio
en lo publicado, y el README ya da la entrada. Q-PG-D-6 (a): con cinco y diez tarjetas un filtro no compensa lo que cuesta
en accesibilidad.

---

## 8. Límites (L-PG-n)

| Id | Límite |
|---|---|
| L-PG-1 | La prosa de enlace no se verifica mecánicamente: solo las cifras, los textos con fuente y los mensajes. La guarda es la revisión a ciegas (§5.4). |
| L-PG-2 | La asociación Id ↔ frase del artículo es una tabla a mano del guion. La guarda comprueba que cada frase está en `ARTICULO.md`, no que esté junto al Id correcto. |
| L-PG-3 | Sin JavaScript no hay botón de tema, ni búsqueda propia, ni copiar un mensaje al portapapeles, ni abrir todos los `<details>` para imprimir: la impresión saca los `<details>` como estén. |
| L-PG-4 | Las fuentes `md:` y `tabla:` dependen de la forma de los documentos. Los documentos del estudio no cambian (condición 6); si uno cambiara, la guarda fallaría en voz alta y habría que mover el selector, no la cifra. |
| L-PG-5 | La lista blanca de la guarda de cifras deja pasar una cantidad escrita con la forma de un identificador (por ejemplo «A01» o «#15»). El control negativo cubre las formas corrientes. |
| L-PG-6 | «dos», «un» y «una» no se vigilan como palabras-número. |
| L-PG-7 | De cada par se muestran como mucho dos líneas del juez: es lo que guarda el JSON (`[:2]`). El Bundle no se muestra ni se publica. |
| L-PG-8 | Las cuentas por caso (`casos`, `ejemplos`) y la frase son del juez de CV3 (`54a90cd9…`); CV4 movió casos de PL.9 y tres falsos positivos en muestras sin cambiar la frase. La página lo dice en la meta y en 08. |
| L-PG-9 | La página no se regenera sola: se regenera a mano y la guarda comprueba que coincide con el guion. Un cambio en el guion sin regenerar deja la CI en rojo, que es lo que se quiere. |
| L-PG-10 | El sitio solo sirve la página si GitHub Pages sigue sirviendo `docs/` desde `main`; desde aquí no se puede comprobar. |
| L-PG-11 | Los enlaces a ficheros del repositorio apuntan a `blob/main/…`; si la rama por omisión cambiara de nombre, se romperían (la guarda de enlaces relativos no los ve: son URL absolutas). |
| L-PG-12 | La página está solo en español, como todo el repositorio. |

---

## 9. El plan, por fases; «hecho cuando»; regla de parada; tope

**Tope: una sesión.** Las fases van en orden; cada una deja la CI en verde.

| Fase | Qué | Hecho cuando |
|---|---|---|
| PG1 (≈ 25 %) | El guion con los cuatro tipos de fuente y los tres ayudantes; la plantilla con `<head>`, cabecera, `.meta`, índice, RESUMEN y pie; `--comprobar`. Las guardas 4.1, 4.2, 5.1 y sus controles **en rojo primero** (la página no existe), después en verde con esta página mínima | `python3 codigo/hacer_pagina_conversores.py --comprobar` dice IGUAL; `python -m pytest tests -q` en verde, con las guardas nuevas contadas |
| PG2 (≈ 35 %) | Secciones 01-07: el problema, el juez, el método, **las 15 tarjetas** con sus pares y marcas, la rama principal, las 31, lo que no cuenta. Guardas 5.2 y 5.3 con sus controles | las 15 tarjetas pasan 5.1 y 5.2; los 34 `<pre>` coinciden con `cv3_minimos`; 5.3 en verde |
| PG3 (≈ 20 %) | Secciones 08-12 y la figura; `.limites` con los textos enteros; guarda 4.3 (accesibilidad); revisión a ojo en claro, oscuro y anchura de teléfono (navegador local, sin red); teclado: Tab por toda la página | 4.3 en verde; nada se corta a 360 px; todo `summary` y enlace alcanzable con Tab y con el foco visible |
| PG4 (≈ 20 %) | Las Q-PG-D a Jev con el estado neutro (sin §7) y aplicar lo decidido; enlaces en `README.md`, `docs/index.html`, `hacer_pagina.py` y `LICENSE.md`; **revisión a ciegas** de la página por otro modelo con la consigna de §5.4; guarda LIMPIO; publicar con la opción B | la revisión no deja ninguna afirmación sobre los proyectos sin fuente en el estudio; higiene en verde; el README y el pie de la primera página enlazan |

**«Hecho cuando», en conjunto:**
- la página existe en `docs/conversores/index.html`, se genera con `codigo/hacer_pagina_conversores.py` y `--comprobar` dice
  IGUAL;
- toda cifra, todo texto del juez, toda cita y todo mensaje mínimo llevan `data-fuente` y la guarda 5.1 los resuelve; la
  guarda 4.1 no encuentra ninguna cifra ni palabra-número suelta; los controles negativos de las dos ven el cambio;
- la página pasa `test_la_pagina_no_carga_nada_externo` y la guarda de accesibilidad; no tiene `<script`, ni `on…=`, ni
  recurso externo;
- «Lo que esto no dice» y «lo que la herramienta no puede saber» están en la página, con su texto;
- `README.md` y `docs/index.html` enlazan a la página; `LICENSE.md` la nombra;
- la revisión a ciegas no deja nada sobre los proyectos que el estudio no diga.

**Regla de parada.**
- Si al 70 % de la sesión la guarda 4.1 no pasa sin ampliar la lista blanca más allá de las clases de identificadores
  documentadas en §4.1, **se recorta la página** a lo mínimo que cumple el encargo (cabecera, RESUMEN, 04, 10, 11 y pie) y se
  declara como DV-PG-1, con lo que quedó fuera y por qué. No se amplía la lista blanca con cantidades.
- Si el guion no puede leer una tabla Markdown de forma fiable (celdas con `|` escapado, filas partidas), esas cifras pasan
  a fuentes `json:` donde las haya, y donde no las haya la celda se enlaza en vez de copiarse (DV-PG-2); la guarda sigue
  exigiendo fuente para toda cifra que quede.
- Si la revisión a ciegas encuentra una afirmación sobre un proyecto que el estudio no hace, **se quita**; no se reformula.
- Si la sesión acaba con la CI en rojo, no se publica: la página espera a la siguiente sesión con la higiene en verde.
