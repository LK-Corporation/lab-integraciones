> *Copia pública: sin las rutas de la máquina del laboratorio (el corpus se pasa al contenedor de IRIS por un fichero). La huella que cita `SELLO-IV.txt` es la del original.*

# Etapa 30 (IV): diseño del aparato de medida — IRIS como lector del corpus publicado

Diseñador a ciegas (Fable). No he leído RESULTADO-*.md, ARTICULO.md ni el contenido de las auditorías; solo esquemas, cabeceras y la salida de `generar_corpus`. No se programa ni se corre nada aquí.

## 0. Lo que mide y lo que no

**Pregunta** (fija): qué dice el validador de IRIS (esquema 2.5) de los mensajes publicados; dónde coincide con los dos auditores de la 29 en las reglas que ambos ven; si alguna nueva publicada se apoya SOLO en mensajes que IRIS da por inválidos por una regla que el estándar sostiene.

**Marco**: el estándar es la verdad; IRIS es un lector más (con su esquema, que no es el estándar: tablas rellenadas a su manera, longitudes suyas). Cada error de IRIS pasa por tres filtros antes de contarse: (1) ¿se enumera entero o lo tapa otro?, (2) ¿es de una clase que el estándar hace normativa?, (3) ¿lo sostiene una cita del estándar cuando nadie más lo ve?

**Unidades**: el mensaje (una fila JSON); el error de IRIS (un objeto dentro de la fila, con clase y «cuenta/no cuenta»); la clase de nueva (afectada/tocada/intacta).

## 1. El conductor

### 1.1 Corpus de entrada (escrito en la máquina del laboratorio, en una carpeta que el contenedor de IRIS ve)

| Lote | Origen | Mensajes | Carpeta |
|---|---|---|---|
| L1 | `generar_corpus(carpeta, lab=True, minimos=True)` | 451 (263 adt, 40 oru, 40 vxu, 40 mdm, 68 minimos) | `adt/ oru/ vxu/ mdm/ minimos/` tal cual los escribe |
| L2 | `cv3_minimos_vxu.escribir` (PARES; no SECUENCIAS) | 25 pares = 50 | `pares_vxu/` |
| L3 | `md/pares_mdm.PARES` (solo importar la lista y escribir «sin»/«con»; NO correr el script, que lanza conversores) | 7 pares = 14 | `pares_mdm/` |
| L4 | `mev/bases_mdmev.derivar` (T02, T04, T06, T08, T10) | 200 | `mdmev/` |
| L5 | `au/pares_auditoria.PARES` (caso + controles; solo escribir) | 3+5 = 8 | `pares_au/` |

Todos con CR y sin BOM (`normal`), UTF-8. `MANIFIESTO-IV.txt` con sha256 por fichero y huella global; la huella de L1 tiene que coincidir con la `huella` que devuelve `generar_corpus` (eso ata el corpus de IV al publicado). Los lotes L2–L5 son opcionales según Q-IV-D-1.

Nombres: los auditores nombran `vxu/B01.hl7`, `pares_vxu/VL01-orc3-perdido-caso.hl7`, `oru/B01.hl7`, `pares_oru/M01-nm-punto-inicial-caso.hl7`; `generar_corpus` escribe `vxu/VXU-B01.hl7`, `oru/ORU-B01.hl7`, `minimos/M01-nm-punto-inicial-caso.hl7`. El conductor lleva una tabla de correspondencia `NOMBRES-IV.json` {fichero_iv → fichero_auditoria}, afirmada por sha256 del contenido (mismo texto, no solo mismo nombre): un par que no cuadre byte a byte se declara «no comparable» y no entra en el cruce.

### 1.2 Paso a IRIS

- Una clase ObjectScript (`Lab.IV.Validar`, en USER del contenedor `iris-ai`, cargada desde la carpeta compartida) con un método `Fichero(ruta, docType, banderas)` que devuelve una lista de errores, y un guion `iris session IRIS -U USER < correr.cos` que recorre `MANIFIESTO-IV.txt` y escribe la carpeta compartida. El Python de la máquina del laboratorio prepara el corpus, lanza el guion dentro del contenedor y después lee las filas. Se corre en primer plano o con `systemd-run --user`; nunca «aviso en segundo plano».
- **Importación por stream, nunca `ImportFromString`**: `%Stream.FileCharacter` con `TranslateTable="UTF8"`, `ImportFromLibraryStream`. Guarda: la fila lleva `segmentos_fichero` (contados en Python, separador CR) y `segmentos_iris` (`m.SegCount`); si difieren, `importado=false` y el mensaje sale del cruce con motivo `perdida_en_importacion`. Se cuenta también cuántos mensajes llevan bytes no ASCII (los tres `bases_*.py` los tienen), para saber cuántos dependen de esta guarda.
- **DocType**: si MSH-9.3 viene, `"2.5:"_MSH9.3`; si no (ADT^A04, VXU^V04), `##class(EnsLib.HL7.Schema).ResolveSchemaTypeToDocType("2.5", MSH9.1_"_"_MSH9.2)` (la tabla de tipos del esquema, que sigue la 0354). Si MSH-9.3 viene y no coincide con lo que resuelve el esquema, la fila lleva `doctype_discrepante=true` y se valida con el que diga Q-IV-D-2. Si el esquema no resuelve nada, `doctype_origen="ninguno"` y el mensaje cuenta como inválido de clase E con error propio `tipo_no_resuelto` (el estándar define el par evento/estructura en la 0354; un evento desconocido no tiene estructura).
- **Pasadas, bandera a bandera** (medido: un solo error por llamada, el primero tapa a los demás):

| Pasada | spec | Qué mira | Se corre sobre |
|---|---|---|---|
| P0 | `d` | DocType resuelto / parse | el original |
| P1 | `dm` y después `dm-z` | estructura; la diferencia entre ambas aísla los Z | el original |
| P2 | `dr` | campos requeridos | el **clon estructural** (ver 1.3) |
| P3 | `dl` | longitudes | el clon estructural |
| P4 | `dt` | tablas | el clon estructural |
| P5 | `dn` | repeticiones (sin efecto en la sonda; se corre igual y se registra si alguna vez dice algo) | el clon estructural |

Las pasadas P2–P5 corren sobre el clon al que ya se le ha quitado lo que rompe la estructura, porque con un segmento no reconocido IRIS puede no mapear los campos de después y entonces los errores de r/l/t serían artefactos. La fila guarda las dos cosas: los errores de P1 sobre el original y los de P2–P5 sobre el clon, con la lista de lo quitado.

### 1.3 Enumerar TODOS los errores de una clase: iteración con clon

Para cada pasada, bucle:
1. `s = clon.Validate(spec)`. Si OK → fin de pasada.
2. Si error: `$system.Status.DecomposeStatus`; parsear el texto con expresiones fijas (las cuatro formas medidas: «Required field missing in segment N:SEG. Missing field F…», «Field size restriction exceeded in segment N:SEG. Field F, repetition R…», «Invalid value 'V' appears in segment N:SEG, field F, repetition R, component C, subcomponent S, but does not appear in code table 2.5:T», «ErrMapWildSegUnrecog» y los de estructura). Lo no parseable se guarda crudo con `clase="X"` y se para la pasada (no se sabe qué enmudecer).
3. Registrar el error (crudo + campos parseados + clase, §2) y **enmudecerlo** en el clon:
   - E (segmento no esperado / no reconocido / fuera de orden): quitar ese segmento (índice N). Segmento requerido ausente: insertar `SEG|` vacío donde la estructura lo pide (tras el último segmento del grupo anterior según el esquema); si el inserto no quita el error en la siguiente vuelta, marcar `no_enmudecible` y parar la pasada.
   - Z: quitarlo (solo en `dm`; en `dm-z` ya no sale).
   - R (campo requerido vacío): poner un relleno del tipo del campo (`X` para ST/IS/ID, `1` para NM/SI, `20240101` para DT/TS, `X^X` para compuestos); P2 solo mira presencia, así que el relleno no se evalúa.
   - L (longitud): truncar la repetición señalada al tamaño que permite el esquema.
   - T (tabla): vaciar esa repetición/componente. Vale igual para las tablas de usuario vacías: hay que enmudecerlas para ver el siguiente error de tabla, aunque no cuenten.
   - N: quitar las repeticiones sobrantes.
4. Parar si: OK; mismo error dos veces seguidas (enmudecer no funcionó → `no_enmudecible`); o tope de **40 vueltas por pasada** (`tope_alcanzado=true`; se cuenta cuántas filas lo tocan; si alguna, se sube y se repite entero).

El clon es una nueva importación por stream del texto modificado (no `%ConstructClone`, para que el mapa de segmentos se recalcule).

### 1.4 Tablas: apartar los falsos positivos sin perder las tablas de HL7

Dos ejes, los dos registrados por error de tabla:
- **Eje esquema**: antes de correr, se vuelca del esquema 2.5 de IRIS la lista de tablas con su número de valores (`TABLAS-ESQUEMA-IV.json` {tabla: n_valores}). `n_valores=0` ⇒ cualquier error contra ella es `tabla_usuario_vacia` (el falso positivo medido: MSH-3 contra 0361).
- **Eje estándar**: del Apéndice A de v2.5 se saca solo la lista {número de tabla: «HL7» | «User-defined» | «externa/local»} (números y tipo; nada de valores: el texto no se redistribuye). Un error de tabla cuenta como **T-HL7** solo si la tabla es «HL7» en el estándar (tipo ID: valor fuera de tabla = inválido). Si es «User-defined» (tipo IS; el estándar da valores sugeridos y el sitio define los suyos), es **T-USR** y no es invalidez por el estándar aunque el esquema de IRIS tenga valores (PID-8 'Q' contra 0001 es de este tipo). Qué se hace con T-USR-con-valores lo fija Q-IV-D-3.

Así nunca se pierde un error de tabla de HL7: todos se enumeran (se enmudecen para seguir) y se clasifican después; «apartar» es etiquetar `cuenta=false`, nunca dejar de registrar.

### 1.5 La fila JSON por mensaje (`filas.jsonl`)

```
{"fichero":"vxu/VXU-B01.hl7","lote":"L1","corpus":"vxu","caso":"VXU-B01","sha256":…,"msh9":"VXU^V04","doctype":"2.5:VXU_V04",
 "doctype_origen":"msh9|esquema|ninguno","doctype_discrepante":false,"no_ascii":true,
 "importado":{"segmentos_fichero":9,"segmentos_iris":9,"ok":true},
 "z":["ZPI"],"quitado_para_clon":[{"idx":5,"seg":"ZPI","motivo":"Z"}],
 "errores":[{"pasada":"m","vuelta":1,"crudo":"…","seg":"PID","idx":3,"campo":3,"rep":1,"comp":1,"sub":1,"tabla":null,
             "clase":"R","cuenta":true,"motivo_no_cuenta":null,"enmudecido":"relleno"}],
 "tope_alcanzado":false,"no_enmudecible":false,
 "n_por_clase":{"E":0,"Z":1,"R":1,"L":0,"T_HL7":0,"T_USR":2,"N":0,"X":0},
 "veredicto_iris":"invalido","veredicto_iris_que_cuenta":"invalido","veredicto_sostenido":null,"lectura":null}
```
`veredicto_iris` = inválido si hay algún error de cualquier clase; `veredicto_iris_que_cuenta` = inválido si hay algún error con `cuenta=true`; `veredicto_sostenido` y `lectura` se rellenan en §3.4 (lectura del estándar) solo para las filas que lo necesiten.

## 2. Clases de regla

| Clase | Error de IRIS | ¿Comparable con los auditores? | Por qué |
|---|---|---|---|
| E estructura | segmento requerido ausente, no esperado, orden, grupo roto, tipo no resuelto | sí | los auditores leen la tabla de estructura del capítulo (3, 4, 7, 9) |
| Z | segmento Z (solo con `dm`) | sí, pero el estándar permite Z (cap. 2, segmentos definidos localmente): **aviso**, no invalidez | ver Q-IV-D-8 |
| R requerido | campo R vacío | sí | columna OPT de la tabla de atributos |
| L longitud | tamaño mayor que el esquema | sí, con reserva: el LEN de v2.5 es «recomendado» en muchas tablas y el esquema de IRIS puede traer otro; se compara contra el LEN del estándar antes de contar | cita en la lectura |
| T-HL7 | valor fuera de tabla HL7 (ID) | sí | tabla normativa |
| T-USR | valor fuera de tabla de usuario (IS) | no (aviso) | el sitio define los valores |
| N | más repeticiones que RP/# | sí si IRIS lo emite alguna vez; si P5 nunca dice nada, clase **no medida** por IRIS | se declara |
| D tipo de dato | formato interno (fecha mal formada, NM con letras) si IRIS lo emitiera | no comparable por construcción (no se sabe qué miraron); se registra | |
| X | no parseable | no | se lista aparte |

**No comparables aunque los auditores los miren**: condicionales (OPT C, p. ej. RXA-18 con RXA-20 RE, TXA-13 en T06/T10), cruces entre campos, reglas de estado/secuencia, la regla transversal XCN-8/9 (los auditores la separaron en `veredicto_sin_transversales`; IRIS no mira componentes de tipo de dato), y lo semántico. Esas reglas no entran en la matriz: cuando un auditor marca un mensaje inválido SOLO por ellas, para el cruce ese mensaje cuenta como «válido en lo comparable».

**Clasificar los defectos de los auditores**: cada `defectos[i]` se lleva a la misma rejilla por reglas sobre `donde` y `que`: «falta/ausente/requerido/obligatorio» → R (o E si `donde` es un segmento sin campo); «tabla/0NNN/valor no» → T (y el número de tabla decide HL7/USR por el eje estándar); «longitud/caracteres» → L; «orden/segmento/esperado/grupo» → E; «repetic» → N; «XCN/componente 8/9» → transversal; lo demás → NC (no comparable). La rejilla se aplica por programa y se revisa a mano en una tabla `DEFECTOS-AUDITORES-CLASIFICADOS.json` (unas 135 entradas) ANTES de ver las filas de IRIS, y se sella con el resto.

## 3. Cruce con los auditores (solo VXU y ORU: `vxu/`, `pares_vxu/`, `oru/`, `minimos/` de ORU)

### 3.1 Unidad
Dos niveles, los dos se publican (Q-IV-D-4 decide cuál manda en la frase):
- **Mensaje**: `veredicto_iris_que_cuenta` (solo clases comparables, T-USR y Z fuera) frente a `veredicto_sin_transversales` del auditor, reducido a lo comparable (si todos sus defectos de nivel «defecto» son NC, cuenta como válido-comparable; «duda» se lleva aparte).
- **Mensaje × clase** (E, R, L, T-HL7, N): «tiene algún error/defecto de esa clase» a cada lado.
- Afinado por **locus**: para cada defecto comparable del auditor, ¿hay un error de IRIS de la misma clase en el mismo segmento y campo (`donde` = «RXA-3» ↔ seg RXA campo 3)? Da «coincidencia de locus», la medida más dura.

### 3.2 Matriz (por corpus y total)

|  | auditores: inválido (comparable) | auditores: válido (comparable) | auditores: duda |
|---|---|---|---|
| IRIS: inválido (cuenta) | acuerdo-inválido | **solo IRIS** | duda-IRIS-inválido |
| IRIS: válido (cuenta) | **solo auditores** | acuerdo-válido | duda-IRIS-válido |

Se publica la matriz, el acuerdo bruto, y un kappa de Cohen sobre las dos primeras columnas (con su intervalo; n ≈ 162 mensajes auditados, menos los no comparables por sha). La misma matriz por clase.

### 3.3 Qué es coincidencia y qué discrepancia
- Coincidencia: misma celda diagonal; en mensaje×clase, misma presencia de clase; en locus, mismo seg/campo.
- Discrepancia: «solo IRIS» (IRIS ve algo que los dos lectores no vieron) y «solo auditores» (los lectores vieron algo de clase comparable que IRIS no emitió). Cada una es una fila en `DISCREPANCIAS-IV.json` con los errores/defectos implicados.
- Las celdas de «duda» no son discrepancia ni coincidencia; se cuentan y se listan.

### 3.4 Resolución leyendo el estándar
Cada discrepancia la resuelve **un lector distinto del conductor** (Q-IV-D-5), a ciegas de quién la vio (se le da: el mensaje, la regla en cuestión en una frase neutra «¿es RXA-3 requerido en VXU_V04 v2.5?», sin decir si lo dijo IRIS o un auditor). Devuelve: `sostenida_por = estandar_dice_invalido | estandar_dice_valido | no_decidible`, la **cita** (capítulo, sección, tabla, ≤15 palabras del texto) y una línea de razón. Con eso cada discrepancia queda: «IRIS tiene razón», «auditores tienen razón», «ninguno» (p. ej. longitud recomendada, no normativa) o «no decidible». Las «solo IRIS» sostenidas se añaden al catálogo de defectos del corpus; las no sostenidas van a «desviaciones del esquema de IRIS respecto al estándar», que es un resultado en sí (IRIS es un lector, no el oráculo). Se publica solo la cita breve con atribución.

## 4. Cruce con las nuevas publicadas

### 4.1 Mapa de apoyo (`APOYO-IV.json`: {id_clase: {"mensajes":[ficheros], "par":[caso, control], "origen":…, "completo":bool}})
- CV3 (`cv/CLASES-CV3.json`): `casos` trae solo recuentos por corpus; el apoyo nominal se reconstruye con `ejemplos` (ficheros nombrados) más `par_minimo` (id del par de `MIN.PARES`); `completo=false` salvo que Q-IV-D-7 autorice reconstruirlo entero desde el juicio publicado por caso.
- VX3 (`vx/CLASES-VX3.json`): `casos` es una cadena; se parsea a identificadores de base/par (`B07`, `VL06`…) con una expresión fija y se revisa a mano; más `par_minimo`.
- MD3 (`md/CLASES-MD3.json`): cada clase apunta a un `hallazgo` de `HALLAZGOS-MD3-r1.json` (que trae los casos) y a su par de `pares_mdm.PARES`; `tumbados_por_la_revision` se respeta (los tumbados no son nuevas publicadas).
- AU (`au/pares_auditoria.PARES`): los 3 pares sustituyen o acompañan al apoyo de VX-M15, VX-L8 y L-19.

### 4.2 Regla
Una nueva se marca por el estado de sus mensajes de apoyo tras §3.4 (`veredicto_sostenido`; si un mensaje no pasó por lectura porque nadie discrepó, vale `veredicto_iris_que_cuenta` solo para T-HL7/R/E de tablas y OPT inequívocos, y pasa a lectura si es el que decide):
- **afectada**: TODOS los mensajes de apoyo (los casos; y el control del par, Q-IV-D-6) son inválidos por regla sostenida.
- **tocada**: alguno sí, alguno no; se publica cuántos y cuáles.
- **intacta**: ninguno, o todos los inválidos lo son solo por reglas no sostenidas / T-USR / Z.
- **indeterminada**: apoyo `completo=false` y lo nombrado no basta para decidir (se dice).
Q-IV-D-6 decide además si la regla que invalida tiene que tocar el campo del hallazgo (p. ej. una nueva sobre RXA-5 apoyada en un mensaje inválido por PID-7) o basta cualquier regla sostenida.

## 5. Controles: antes de usar el aparato

### 5.1 Negativo (defectos inyectados; `control-negativo/` con su propio manifiesto)
Base: 5 mensajes limpios (uno por tipo: ADT_A01, ORU_R01, VXU_V04, MDM_T02, y un ADT^A04 sin MSH-9.3), que primero tienen que salir válidos en todas las pasadas (si no, se limpian hasta que lo sean; esa limpieza se documenta y es ya un primer resultado sobre el corpus). Sobre cada base, un mutante por clase y alguno combinado:

| Id | Inyección | Debe verse como |
|---|---|---|
| N-E1 | quitar PID | E, seg PID ausente |
| N-E2 | EVN después de PID | E, orden |
| N-E3 | segmento `QQQ|1` | E (no reconocido); con `-z` sigue (no es Z) |
| N-Z1 | `ZPI|1` | Z con `dm`; nada con `dm-z` |
| N-R1 | MSH-10 vacío | R, MSH campo 10 |
| N-R2 | PID-3 vacío | R, PID campo 3 |
| N-L1 | MSH-10 de 25 caracteres | L, MSH campo 10 |
| N-T1 | MSH-11 = `Q` (0103, HL7) | T-HL7, cuenta |
| N-T2 | OBX-11 = `Q` (0085, HL7) | T-HL7, cuenta |
| N-T3 | MSH-3 = `LAB` (0361, usuario, vacía en esquema) | T-USR `tabla_usuario_vacia`, no cuenta |
| N-T4 | PID-8 = `Q` (0001, usuario con valores) | T-USR, no cuenta (según Q-IV-D-3) |
| N-N1 | una repetición de más en un campo con tope finito en el esquema (se busca en el volcado del esquema; si no hay ninguno con tope, N queda «no medible») | N, o declaración |
| N-D1 | ADT^A09 sin estructura con `MSH-9.3 = ADT_A01` | `doctype_discrepante`, resuelto como diga Q-IV-D-2 |
| N-U1 | `PID-5 = Muñoz^Iñaki` (no ASCII) + N-R1 | `importado.ok=true`, segmentos iguales, y R visto |
| N-M1 | N-L1 + N-R2 + N-T2 + N-T3 + N-E3 en el mismo mensaje | las cinco, cada una en su clase, en cualquier orden |
| N-M2 | N-R1 + N-R2 + PV1-2 vacío (tres R) | tres R, tres loci distintos (prueba la iteración con clon) |

**Para fiarse**: 100 % de los inyectados vistos en su clase y su locus; cero errores que no estén en la base limpia; T3 apartado y T1/T2 contados; N-M1 y N-M2 completos (la iteración enumera, no solo el primero); N-U1 sin pérdida; dos corridas seguidas dan `filas.jsonl` idéntico (determinismo). Un solo fallo para el aparato, no se corre el corpus.

### 5.2 Positivo
- Las 5 bases limpias y sus clones «enmudecidos» salen válidos en todas las pasadas (el enmudecer no fabrica errores nuevos).
- Los pares «control» de L2/L3/L5 son por construcción «válidos en v2.5» según sus cabeceras: se predice que la mayoría salen válidos en lo que cuenta; los que no, van a lectura (eso es resultado, no fallo del aparato, salvo que la lectura diga que IRIS inventa).
- Los 3 mensajes de `a1/ejemplos_cap3.json` (versiones del laboratorio de los ejemplos del capítulo 3): se espera que salgan válidos o con desviaciones conocidas del propio laboratorio.

## 6. Previsión sellada (`PREVISION-IV.json` + sha256 en `SELLO-IV.txt`, antes de la primera corrida del corpus; los controles pueden correr antes porque no tocan el corpus)

Cantidades, cada una con valor puntual e intervalo que quien sella se compromete a dar; a ciegas, el diseñador deja un prior que puede sustituirse pero no después de correr:

| Id | Cantidad | Forma | Prior del diseñador |
|---|---|---|---|
| PV1 | % válidos (lo que cuenta) por corpus: adt, oru, vxu, mdm, minimos, pares_vxu, pares_mdm, mdmev, pares_au | 9 intervalos | adt 70–90; oru/vxu/mdm 75–95; pares 85–100 |
| PV2 | % inválidos por cualquier error (T-USR y Z dentro) | 1 intervalo | 40–80 (MSH-3/4 son 0361/0362 en todos) |
| PV3 | reparto de errores que cuentan por clase E/R/L/T-HL7/N | 5 proporciones | R y T-HL7 > 70 % del total; N ≈ 0 |
| PV4 | mensajes con `importado.ok=false` | número | 0 |
| PV5 | `tope_alcanzado` o `no_enmudecible` | número | ≤ 3 |
| PV6 | acuerdo bruto con auditores (mensaje) y kappa | 2 valores | 75–90 %; kappa 0,3–0,6 |
| PV7 | discrepancias «solo IRIS» / «solo auditores» | 2 números | 5–25 / 2–10 |
| PV8 | de las «solo IRIS», % sostenidas por el estándar | % | 40–80 (longitudes y esquema propio restan) |
| PV9 | nuevas afectadas / tocadas / intactas / indeterminadas por juez (CV3 62, VX3 41, MD3 18) | 4 números × 3 | afectadas ≤ 2 por juez; indeterminadas en CV3 > 0 |
| PV10 | mensajes con segmentos Z | número | 0 |
| PV11 | msh9 sin estructura resueltos por esquema / no resueltos | 2 números | ~todos los A04 y VXU^V04 / 0 |

Si una cantidad cae fuera del intervalo, se dice y se explica; no se reajusta el aparato para que caiga dentro.

## 7. Preguntas abiertas (las decide otro)

**Q-IV-D-1 Alcance del corpus.** (a) solo L1 (451, lo que devuelve `generar_corpus`); (b) L1+L2+L3+L5 (todos los pares, 523); (c) todo con L4 (723). Cambia: el coste, y si el cruce con MD3 y con la etapa 28 entra o no.

**Q-IV-D-2 DocType cuando MSH-9.3 falta o contradice.** (a) manda el esquema (tabla 0354) y la contradicción es error E que cuenta; (b) manda MSH-9.3 cuando viene y la contradicción es aviso; (c) se valida con los dos y se publican ambos. Cambia: qué mensajes son inválidos por E y si la 0354 se trata como normativa.

**Q-IV-D-3 Tablas de usuario con valores en el esquema (PID-8 'Q').** (a) no cuentan nunca (aviso); (b) cuentan solo si el auditor también lo señaló (entonces es acuerdo); (c) cuentan como discrepancia y van a lectura. Cambia: PV1, PV6, PV7.

**Q-IV-D-4 Unidad que manda en la frase publicada.** (a) mensaje; (b) mensaje × clase; (c) locus. Cambia: la cifra de acuerdo que se dice (las tres se publican igual).

**Q-IV-D-5 Quién lee el estándar en las discrepancias.** (a) el conductor, con cita; (b) un lector nuevo a ciegas (Agent) que no sabe quién vio qué; (c) dos lectores y se publica el desacuerdo. Cambia: independencia y coste.

**Q-IV-D-6 Criterio de «afectada».** (a) todos los apoyos inválidos por cualquier regla sostenida; (b) por regla sostenida que toca el campo del hallazgo; (c) como (a) y además el control del par inválido también afecta. Cambia: PV9 y cuántas nuevas quedan «tocadas».

**Q-IV-D-7 Apoyo de CV3 (solo recuentos).** (a) apoyo = ejemplos + par, marcado `completo=false`; (b) reconstruir desde el juicio por caso publicado (el conductor lo lee; el diseñador ya no); (c) excluir CV3 del cruce 4. Cambia: cuántas clases quedan indeterminadas.

**Q-IV-D-8 Segmentos Z.** (a) aviso (el estándar los permite); (b) cuentan como E si no van al final del grupo; (c) no se miran. Cambia: PV10 y E.

**Q-IV-D-9 Longitudes.** (a) L cuenta solo si el LEN del estándar es menor o igual que el valor (se lee la tabla); (b) L cuenta tal cual lo dice el esquema; (c) L se registra y no cuenta nunca. Cambia: PV3, PV8.

**Q-IV-D-10 Qué se publica.** (a) matriz, cifras y lista de discrepancias con cita breve; (b) además `filas.jsonl` entera (los textos de error son de IRIS, no de HL7); (c) solo las cifras. Cambia: lo que un tercero puede reproducir.

## 8. Riesgos y límites

- **El esquema de IRIS no es el estándar**: tablas rellenadas a su criterio (0001 con valores aunque sea de usuario), longitudes propias, tipos de mensaje resueltos por su tabla. Por eso ningún error cuenta sin su clase y, si nadie más lo ve, sin cita. Las desviaciones encontradas se publican como tales.
- **Un error por llamada**: el enmudecer puede crear o esconder errores (quitar un segmento esconde los de sus campos; un relleno R puede ser inválido en T, pero las pasadas van separadas). Se registra siempre lo quitado; N-M1/N-M2 vigilan la enumeración.
- **Parseo del texto de error**: si IRIS cambia la redacción (versión, idioma), la clase X crece y se nota en PV5; lo crudo se guarda siempre.
- **Importación**: la trampa de `ImportFromString` está cerrada con stream + recuento de segmentos; si aun así difieren, el mensaje sale, no se adivina.
- **Las banderas `e f c s` no hicieron nada visible**; lo que IRIS mire con ellas no se mide y no se reclama.
- **`n` sin efecto**: la clase N puede quedar «no medida por IRIS»; se dice, no se rellena con otra cosa.
- **Los auditores no son el oráculo** ni lo es IRIS: el acuerdo mide dos lectores, no la verdad; la verdad entra solo por la cita del lector de §3.4, que también es falible: se publica la cita para que se compruebe.
- **Correspondencia de nombres** entre el corpus de IV y el auditado por sha256; los no coincidentes no se comparan y se cuentan.
- **A ciegas**: este diseño no sabe qué se halló; quien lo corra sella PV1–PV11 antes de la primera corrida y no toca el aparato después salvo fallo de control negativo, y entonces vuelve a sellar.
- **Lo que no responde**: si un conversor «hace bien» en aceptar o rechazar (eso fue la 14l/20/26); si el corpus es representativo; nada sobre semántica ni condicionales.
