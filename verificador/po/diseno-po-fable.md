# Diseño de la etapa 41: la Observation de PD1-7 en un ORU (a ciegas, Fable, 8-nov-2026)

Encargo: `po/encargo-diseno-po.md`. Lo fijado: `ANTES-ETAPA-PD17ORU.md`. La etapa anterior: `RESULTADO-PD17.md`. Las rutas van
relativas a `fase12/` (el `verificador/` publicado), como en ese resultado. Se diseña; no se programa ni se publica.

**En una frase:** el paso de PD1-7 de la etapa 40 (`_origen_pd17` en el emparejamiento, `_livingwill` y el recurso ausente en el
juicio) se saca a dos ayudantes comunes y la rama de ORU los llama igual que la de ADT; la Observation de PD1-7 se aparta **antes**
de casar las de los OBX, y lo que se juzga de ella es exactamente lo de la 40. Lo medido hoy sobre una copia del juez: con PD1-7 = F
y su Observation como la crea la guía, un ORU sale `recurso_inventado` (OBX); sin la Observation, `correcto`; con un OBX fuera de
ORDER_OBSERVATION sin su Observation, la de PD1-7 ocupa su hueco de L-CV-7 y sale una nota en vez de contar.

## 1. Qué hace el juez después en un ORU

### 1.1 La base, con sus citas

- **La guía crea la misma Observation en las dos hojas.** `MSG_ADT_A01.csv:19` y `MSG_ORU_R01.csv:17`: «IF PD1-7 VALUED»,
  `PD1[Observation-LivingWill]`, con `Observation[n].subject.reference=Patient[1].id` como única referencia. En ORU la fila está
  dentro de PATIENT (4.1.2), no de ORDER_OBSERVATION. El mapa de segmento (`ConceptMap segment-pd1-livingwill-to-observation`) tiene
  un solo elemento, PD1-7 → `valueCodeableConcept` por `table-hl70315-to-v2-0315`, identidad sobre Y, F, N, I y U. No fija
  `code`, `effective[x]` ni nada más; tampoco pone la Observation en `DiagnosticReport.result`: eso la hoja lo hace solo para
  `Observation[2]`, la de los OBX de ORDER_OBSERVATION (`MSG_ORU_R01.csv:67-73`).
- **En v2.5,** ORU_R01 lleva `[PD1]` justo tras el PID, dentro de PATIENT (CH07.txt, estructura ORU^R01^ORU_R01), y PD1-7 es un IS
  con la tabla de usuario 0315 (Ch03.txt:8504, 8630-8643). En v2.5 PATIENT no lleva OBX; los OBX fuera de ORDER_OBSERVATION que
  cuenta L-CV-7 son los de la hoja de la guía (PATIENT_OBSERVATION, SPECIMEN_OBSERVATION).
- **FHIR R4** pide `Observation.status` (1..1, required); `DiagnosticReport.result` son «las Observation que forman parte del
  informe».
- **Lo ya decidido en la 40 vale tal cual,** porque la fila de la hoja es la misma: Q-PD-1 (reconocerla solo por el dato), Q-PD-3
  (sin ella, recurso ausente que cuenta). Q-PD-2 y Q-PD-4 son de ACC y PDA, que ORU_R01 no lleva: no se aplican, y no hace falta
  ninguna regla de la 0136 en ORU.

### 1.2 Dónde se reconoce: antes de casar las de los OBX

En `emparejar`, rama ORU, justo después de formar `ob` (las Observation de primer nivel) y antes de casar los DiagnosticReport y los
OBX: `ob = apartar_pd17(ob)`, donde `apartar_pd17` es el mismo trozo que hoy tiene la rama ADT, sacado a una función interna que
usa `rol`:

    pd17 = _origen_pd17(m, obs)
    si no es None: rol("Observation#PD1", "PD1-7", entry, por, candidatas) y se quita la candidata de la lista

`_origen_pd17` no cambia: ya excluye toda Observation con el código de **cualquier** OBX del mensaje (también los de fuera de
ORDER_OBSERVATION), y elige una sola candidata, la primera con el sistema de la 0315 y, si ninguna lo lleva, la primera con el
código de PD1-7.

**Por qué antes y no después:**
1. Es el mismo orden que en ADT (Q-PD-2 a: el dato manda, no la eliminación): un solo camino de código para las dos familias.
2. El resultado del casado de los OBX no depende de ello: `_origen_pd17` excluye las Observation con código de OBX, y el casado de
   los OBX busca solo por el código de OBX-3, así que ninguna Observation puede ser a la vez candidata de PD1-7 y de un OBX.
   Lo único que cambia frente a «después de los OBX y antes de las sobrantes» es `candidatos` de los roles `Observation#i.j`
   (`len(ob)`, uno menos), que no entra en ningún juicio guardado ni en las bases. Por eso no es una decisión abierta.
3. Lo que sí importa es que esté **antes de las sobrantes**: hoy la de PD1-7 ocupa un hueco de L-CV-7 (`k < fuera`) y puede
   dejar la Observation legítima de un OBX fuera de ORDER_OBSERVATION como `recurso_inventado` (medido: con `[of, op]` la nota es
   para `of`; con `[op, of]`, la nota es para `op` y `of` cuenta como inventada). Apartada antes, los huecos de L-CV-7 son para las
   que son.

Los DiagnosticReport no se tocan: una referencia `result` a la Observation de PD1-7 la mete en `propias` del OBR, pero el casado
exige el código del OBX, así que no la casa (y ya no está en `libres_o`).

### 1.3 Qué juzga de ella: lo de la 40, por un ayudante común

En `_juzgar`, el bloque de ADT (`v7 = _valor_pd17(m)`; sin rol o sin entry, `recurso_ausente` PD1-7; si no, `_livingwill`) se saca
a `_juzgar_pd17(J, m, roles, pat_entry, familia)` y se llama desde las dos ramas: en ADT donde está hoy (tras el Encounter, para que
el orden de los hallazgos de un ADT no cambie), y en ORU tras el bucle de los OBR y antes de las sobrantes. `_livingwill` no cambia
en lo que juzga: `status`, el valor por la 0315 y el sujeto; `code`, `effective[x]` y lo demás no se juzgan, porque el mapa no los
fija. El hecho sigue siendo `PD1-7` y el rol `Observation#PD1`, para que el aparato de la 40 (clasificador, pruebas) valga.

### 1.4 Caso a caso (PD1-7 = F si no se dice otra cosa; «hoy» medido sobre una copia del juez)

| Caso en un ORU | Hoy | Después | Cuenta |
|---|---|---|---|
| PD1-7 valorado y la Observation (v2-0315, F), con uno o con varios OBR, sin referirla desde ningún DiagnosticReport | `recurso_inventado` OBX | Correcto; rol `Observation#PD1`, por «sistema» | No |
| Igual, referida desde `DiagnosticReport.result` | `recurso_inventado` OBX y `referencia_rota` OBR («no es una Observation de su OBR») | De PD1-7; el DiagnosticReport conserva su `referencia_rota` (Q-PO-1 a; con b, nota) | Sí, la del OBR |
| PD1-7 valorado y sin la Observation, en 2.5 y en 2.8 | Correcto | `recurso_ausente` PD1-7, con la cita de la hoja de ORU | Sí, en toda versión |
| (v2-0315, Y) con PD1-7 = F | Inventada | `valor_distinto` | Sí |
| El código F sin sistema, o con el de la 0136 | Inventada | `codigo_mal_mapeado` | Sí |
| PD1-7 = X (fuera de la 0315) con el código X | Inventada | Nada, ni nota | No |
| PD1-7 = X con (v2-0315, W) | Inventada | Nota de convención en 2.5; de versión en 2.8 | No |
| `valueString` F | Inventada | `recurso_ausente` PD1-7 e inventada (L-CV-18, como en ADT) | Sí |
| Sin `status` / `subject` a otro Patient / sin `subject` | Inventada | `fhir_invalido` / `referencia_rota` / `dato_perdido`, de PD1-7 | Sí |
| Un OBX cuyo código coincide con el de PD1-7 (OBX-3 = F) y las dos Observation | La de código F es del OBX; la otra, inventada | La de código F es del OBX; la otra, de PD1-7 | No |
| Un OBX cuyo valor coincide (OBX-5 = F^^HL70315 como CE) y las dos Observation | La del OBX, por su código; la otra inventada | Las dos en su sitio | No |
| Igual, solo la del OBX (con su código y valor (v2-0315, F)) | Correcto | Es la del OBX (tiene su código); PD1-7 `recurso_ausente` | Sí |
| Igual, la del OBX sin su `code` y sin la de PD1-7 | `recurso_ausente` OBX-3, `referencia_rota` OBR, inventada | `recurso_ausente` OBX-3, `referencia_rota` OBR, y la Observation pasa por la de PD1-7 (correcta si lleva (v2-0315, F)). Riesgo declarado en L-CV-18, el mismo que en ADT | Sí |
| Un OBX fuera de ORDER_OBSERVATION sin su Observation, y la de PD1-7 | Nota L-CV-7 (la de PD1-7 ocupa el hueco) y correcto | De PD1-7, sin nota | No |
| Un OBX fuera con su Observation, y la de PD1-7, en los dos órdenes | Nota para la primera e inventada la segunda | La del OBX con la nota; la de PD1-7 en su rol | No |
| La Observation con el código del OBX fuera y el valor (v2-0315, F), sin la de PD1-7 | Nota L-CV-7 | Nota L-CV-7 (tiene código de OBX: no es candidata) y `recurso_ausente` PD1-7 | Sí |
| PD1 con PD1-7 vacío y una Observation de más | Inventada | Inventada (control) | Sí |
| 2.8, PD1-7 = `F^Living will on file^HL70315` (CWE) y (v2-0315, F) | Inventada | Correcto: se lee el primer componente | No |
| Cualquier ADT | Lo de la 40 | Lo mismo, byte a byte (Q-PO-2 b) | |

Los recuentos no cambian en ningún caso (la Observation se cuenta igual con rol o sin él).

### 1.5 Lo que dice de sí mismo

- `L-CV-18`: la última frase («Solo en ADT: la hoja de ORU también la crea … y en oru_conv sigue como recurso_inventado») pasa a
  «En ADT y, desde la etapa 41, en ORU (`MSG_ORU_R01.csv:17`): se aparta antes de casar los OBX y nunca ocupa un hueco de L-CV-7;
  una referencia desde `DiagnosticReport.result` sigue siendo referencia_rota del OBR, porque la hoja no la pone en `result`
  (Q-PO-1); se lee el primer PD1, como el primer PID; con el código de un OBX, también de uno fuera de ORDER_OBSERVATION, es la de
  ese OBX, y una Observation de un OBX que pierde su código y lleva el valor de PD1-7 pasa por la de PD1-7». Mismo identificador:
  no hay L-CV-19, y así la base de los informes de P-MD-25 (c), que guarda qué límites hay y no su texto, no se rehace.
- `S-CV-4`: «la de PD1-7 por su valor o el sistema de la 0315» gana «en ADT y en ORU».
- `PERFIL_GUIA_ORU`: una fila nueva, «Observation (de PD1-7)», como la de ADT, con la cita `[G MSG_ORU_R01.csv:17]`; de 16 a 17.
- `C["PD1-7"]` y las citas: Q-PO-2.
- `mcp_verificador.REVISION`: una entrada nueva al principio, «etapa 41: la Observation de PD1-7 también en oru_conv (S-CV-4,
  L-CV-18); antes, etapa 40: …».

## 2. Decisiones abiertas, para Jev

**Q-PO-1. La Observation de PD1-7 referida desde `DiagnosticReport.result`.**
- **(a) Sigue siendo `referencia_rota` del OBR, como hoy** (recomendada). Hechos: la hoja solo pone en `result` a
  `Observation[2]` (`MSG_ORU_R01.csv:67-73`); la fila de PD1-7 solo da `subject`; el perfil de ORU dice «exactamente las
  Observation de los OBX de su OBR»; en R4, `result` son las Observation que forman parte del informe, y un indicador de
  testamento vital no lo es. Toca: nada en el juez (la prueba fija lo que ya hace); la frase de L-CV-18. La huella del juez cambia
  igualmente por el resto de la etapa.
- **(b) Nota de convención.** Hechos: la Observation existe y es la que la guía crea; el conversor solo la cuelga del informe, y
  el dato no se pierde ni se inventa. Toca: `_informe` (si una `result` resuelve a la entry del rol `Observation#PD1`, nota
  `convencion` con hecho `OBR-i` en vez de `referencia_rota`), L-CV-18, P-CV-35 y la regla R2 del clasificador (una nota de OBR
  que entra). Cambia la huella del juez (ya cambia) y añade una forma nueva a la conducta.

**Q-PO-2. Las citas de los hallazgos de PD1-7.**
- **(a) Una lista: `C["PD1-7"]` gana `[G MSG_ORU_R01.csv:17]`.** Hechos: las dos filas son ciertas para esa Observation; es un
  solo cambio en `C`. En contra: los hallazgos de PD1-7 de un ADT ganan una cita de la hoja de ORU, así que «en ADT no cambia nada»
  solo vale para veredictos y subtipos, no byte a byte (el rejuicio lo vería en una evidencia de ADT con PD1-7, y no hay ninguna).
  Toca: `conversion.py` (`C`), P-MD-25 (d) (huella de `C`).
- **(b) Por familia** (recomendada): `C["PD1-7"]` queda como está (la hoja de ADT) y `CITAS_PD17 = {"adt": C["PD1-7"],
  "oru": la misma lista con la hoja de ORU en el sitio de la de ADT}`; `_juzgar_pd17` y `_livingwill` reciben las citas, y
  `_sujeto` gana un parámetro `citas=None` (por omisión, lo de hoy) para que el `dato_perdido` del sujeto no cite la hoja de ADT
  en un ORU. Hechos: un ADT sale byte a byte igual, hasta las citas; cada hallazgo cita la fila que lo crea. En contra: tres
  firmas cambian y hay un mutante más («ORU cita la hoja de ADT»). Toca: `conversion.py`; la huella de `C` **no** cambia (P-MD-25 d
  solo por `INFO`), la fila nueva del perfil de ORU cita `CITAS_PD17["oru"]`.

En las dos preguntas, ninguna opción cambia una sola evidencia guardada (ninguna de ORU lleva PD1-7 valorado) ni la frase del
estudio.

## 3. Las pruebas, en rojo antes

### 3.1 Nuevas, en `prueba_conversion.py`

- **P-CV-35, la conducta en ORU:** las filas de §1.4 que no son controles, con `oru_msg()` + `con_pd1(...)` (ya pone el PD1 tras
  el PID), `oru_bundle(...)` y `obs_pd1(...)`; un ayudante `oru_fuera(m)` que mete un OBX antes del primer OBR (fuera de
  ORDER_OBSERVATION según `_grupos_oru`, medido: `fuera = 1`); con dos OBR, `oru_msg(dos=True)` y `oru_dos(sobrante=False)`. Se
  comprueban `cuentan(r)`, `cat(r)`, `de_pd1(r)` (rol, «sistema»/«codigo», fullUrl), `de_hecho(r, "PD1-7")`, la nota L-CV-7 y, en
  el recurso ausente, que las citas lleven `[G MSG_ORU_R01.csv:17]`. **Caen hoy** porque el juez de hoy no tiene rol
  `Observation#PD1` en ORU: la Observation sale `recurso_inventado` (o nota L-CV-7) y sin ella sale `correcto`. Los controles
  (PD1-7 vacío, la del OBX con su código, la del OBX fuera con su código) pasan con los dos jueces.
- **P-CV-36, lo que dice de sí mismo:** `PERFIL_GUIA_ORU` con 17 filas y una de PD1-7 que cuenta y cita la hoja de ORU; L-CV-18
  nombra `oru_conv`, `DiagnosticReport.result` y L-CV-7, y ya no dice «sigue como recurso_inventado»; S-CV-4 dice «ORU»;
  `REVISION`: la primera entrada empieza por «etapa 41» y nombra L-CV-18, la segunda por «etapa 40»; según Q-PO-2, `C["PD1-7"]`
  o `CITAS_PD17["oru"]` llevan la cita de la hoja de ORU. Caen hoy todas.
- **`po/prueba_rejuicio_po.py`:** el clasificador de §4 sobre juicios sintéticos de ORU (la conducta, y los controles con su
  regla), antes de que exista; es el rojo del clasificador, como `pd/ROJO-PD-2.txt`.

### 3.2 Existentes que cambian

| Prueba | Hoy | Después |
|---|---|---|
| P-CV-33, último control «ORU: con PD1, la Observation de más sigue inventada» | Fija lo viejo | Pasa a «ORU con PD1 y PD1-7 vacío: sigue inventada»; el caso con PD1-7 valorado va a P-CV-35. Las 23 comprobaciones de ADT no se tocan |
| P-CV-34, `REVISION` | `entradas[0]` es la 40, `[1]` la 37 | `entradas[1]` la 40, `[2]` la 37 (la 41 queda en P-CV-36); «L-CV-18 nombra ORU» sigue |
| P-CV-32, `REVISION` | la 37 es la segunda | Sigue siendo una sola entrada «etapa 37»: no cambia |
| P-VX-20 | `(23, 16)` | `(23, 17)` |
| P-MD-24 | `(23, 16, 27)` | `(23, 17, 27)` |
| P-MD-25 (d) | huellas de `C`, `INFO`, `TIPOS_PROY`, `CVX.TIPOS`, `PUNTOS`, `MAPAS` | `INFO` nueva (L-CV-18, S-CV-4); `C` solo con Q-PO-2 a; las demás iguales |
| P-MD-25 (b), (c) | rejuicio de su línea base y los informes | Deben seguir pasando sin rehacer nada: ninguna evidencia con PD1-7 y ningún límite nuevo. Si (b) se corre al poner en verde, declararlo en el sello, como en la 40 |

Las cifras del rojo se dan del repositorio publicado: hoy 34 pruebas y 180 comprobaciones en `prueba_conversion.py`; después, 36
pruebas. `pd/prueba_rejuicio_pd.py` y `pd/mutantes_pd.py` quedan como sellos de la 40: el segundo deja de aplicar al juez nuevo
porque sus anclas de texto se mueven al ayudante (la indentación cambia), y no se toca.

### 3.3 Los mutantes del juez (`po/mutantes_po.py`, sobre una copia del juez; `prueba_conversion.py` tiene que caer con cada uno)

Los 18 de la 40, con las anclas puestas donde quede el texto (siguen muriendo por P-CV-33), y estos de la 41:

| Mutante | Lo caza |
|---|---|
| La rama ORU sin `apartar_pd17` | P-CV-35: inventada |
| La rama ORU sin `_juzgar_pd17` | P-CV-35: sin recurso ausente, sin valor distinto |
| `apartar_pd17` después de las sobrantes (la de PD1-7 con rol y como sobrante) | P-CV-35: inventada o nota de más |
| `_origen_pd17` excluye solo los códigos de los OBX de ORDER_OBSERVATION | P-CV-35: la del OBX fuera con valor (v2-0315, F) pasa por la de PD1-7 |
| `_juzgar_pd17` solo con `familia == "adt"` | P-CV-35: sin recurso ausente |
| Las citas de ORU con la hoja de ADT (Q-PO-2 b) o sin la de ORU (a) | P-CV-35: la cita del recurso ausente |
| Sin la fila del perfil de ORU; L-CV-18 con la frase vieja; S-CV-4 sin ORU; `REVISION` sin la 41 | P-CV-36 |
| Con Q-PO-1 b: la nota del `result` también para una Observation que no es la de PD1-7 | P-CV-35 y P-CV-6 (control cruzado) |

Un mutante equivalente que no se pone: «apartar después de casar los OBX y antes de las sobrantes» da los mismos hallazgos
(§1.2, punto 2); solo cambia `candidatos`, que ninguna prueba debe fijar.

## 4. El rejuicio

### 4.1 El clasificador: `po/rejuicio_po.py`

Las 30.118 evidencias, con el juez de antes (línea base de `md/rejuicio_md.py linea_base`, que ya existe de la 40) y el nuevo.
Reutiliza de `pd/rejuicio_pd.py`, importándolo sin tocarlo: `valor_pd17`, `msh12`, `_diferencia`, `_url`, `SUB_PD17`, la R3 y la
R5 enteras y el esqueleto de `pasada`/`main`. Una diferencia es de la conducta de PD1-7 en ORU si no falla ninguna regla, mirando
el caso (el mensaje) y no solo la forma:

- **R1, el caso:** el punto es `oru_conv` y el mensaje trae PD1 con PD1-7 valorado (su primer componente). Un ADT que cambie
  sale «fuera» por R1: es la regla de parada de «que en ADT no cambie nada».
- **R2, la forma:** lo que sale es `recurso_inventado` de OBX o la nota `fuera_proyeccion` de OBX; lo que entra, eso mismo o un
  hallazgo de PD1-7 de la lista cerrada de la 40 (`SUB_PD17`); ningún rechazo; ningún `recurso_sin_mapa` (no hay ACC ni PDA en
  ORU). Con Q-PO-1 b, además una nota `convencion` con hecho `OBR` u `OBR(i)` puede entrar si sale una `referencia_rota` del mismo
  hecho que cita la Observation que entra como de PD1-7.
- **R3, el valor:** la de la 40, tal cual: los hallazgos de PD1-7 que entran dicen el valor de PD1-7 del mensaje, la nota es de
  convención en 2.5 y de versión en otra, y el recurso ausente no viene con otro hallazgo de PD1-7.
- **R4, el libro de las Observation,** por `fullUrl`: ninguna pareja (`recurso_inventado`, url) entra; sale una como mucho (la de
  PD1-7, o la de otra Observation que baja a un hueco de L-CV-7 y deja de contar: medido en §1.4, nunca dos); la nota
  `fuera_proyeccion` solo puede salir si el mensaje trae OBX fuera de ORDER_OBSERVATION (se cuentan en el mensaje crudo con un
  lector de secuencia de segmentos como `_grupos_oru`: OBX antes del primer OBR o tras un SPM), y nunca entra sola.
- **R5, el veredicto:** recuentos iguales; el veredicto solo pasa entre `correcto` y `fallo_silencioso` «convertido».

`comparar` sale con 1 si hay alguna «fuera», alguna que falte o algún punto de la herramienta que cambie. Lo que no mira, como en la
40: si la Observation que ahora es de PD1-7 lleva de verdad el sistema o el código; eso lo prueba P-CV-35.

### 4.2 El control: defectos con la forma de la conducta que no lo son

Cada pasada siembra un defecto en el juez y toda evidencia con el defecto tiene que salir «fuera»; se guardan las reglas que la sacan
y la firma de lo que cambia (`po/CONTROL-PO.json`, `po/FIRMAS-CONTROL-PO.json`):

| Defecto sembrado | Reglas que deben cazarlo |
|---|---|
| `recurso_ausente` de PD1-7 en todo ORU sin PD1-7 | R1 y R3 |
| `recurso_ausente` de PD1-7 con otro valor, en un ORU con PD1 (69) | R1 y R3 |
| La Observation de un OBX sacada de su sitio en un ORU sin PD1-7 (`recurso_ausente` OBX-k entra, inventada entra) | R1, R2 y R4 |
| Una sobrante de L-CV-7 dada por inventada, en los ORU con la nota (si la línea base no trae ninguno, marca 0 y se declara) | R1 y R4 |
| `valor_distinto` en OBX-5 y en PID-5 | R1 y R2 |
| `recurso_ausente` de PD1-7 en todo ADT sin PD1-7 (la pasada 1 de la 40) | R1, por la familia, y R3 |

En el corpus no hay PD1-7 en ORU, así que R1 falla siempre; R3 y R4 solas, con PD1-7 valorado, las prueba `po/prueba_rejuicio_po.py`
con juicios sintéticos (la conducta: inventada que sale; nota L-CV-7 que sale con OBX fuera; una inventada ajena que baja a nota;
recurso ausente que entra; y los controles: dos parejas que salen, la nota que sale sin OBX fuera, una inventada que entra, un
ADT, PD1-7 vacío, otro valor, convención en 2.8, un subtipo de PD1-7 que el juez no da, un rechazo, recuentos que cambian).

## 5. La previsión (`po/prever_po.py`, sellada antes de correr el juez nuevo)

Como `pd/prever_pd.py`, que ya cuenta por punto, sobre la línea base del juez de antes y los mensajes:

| | Previsto | Por qué |
|---|---|---|
| Diferencias en el rejuicio | 0 | Ninguna de las 4.424 evidencias de `oru_conv` lleva PD1-7 valorado (69 traen PD1 vacío en el 7); el paso nuevo y el juicio nuevo solo se dan con él, y en ADT el código es el mismo movido de sitio, con la llamada en el mismo punto |
| Fuera, faltan, punto que cambia | 0 | Lo mismo |
| El control | Toda evidencia con el defecto, «fuera» | R1 falla en todas; la regla propia se ve en la firma |
| ORU sin PD1-7 con recurso ausente sembrado | Más de 0 y como mucho 4.424 (las que llegan al juicio) | |
| ORU con PD1 y otro valor | Como mucho 69 | |
| ORU con la Observation de un OBX fuera de sitio | Las de ORU con algún rol `Observation#i.j` casado en la línea base (se cuenta) | |
| Sobrante de L-CV-7 dada por inventada | Las de ORU con la nota `fuera_proyeccion` en la línea base (se cuenta; con 0, se declara) | |
| ADT con recurso ausente sembrado | 15.979, las de la 40 | El camino hasta `_juzgar` no cambia |
| Las clases del estudio (`cv/cv3_clases.py`) | Iguales caso a caso salvo la huella del juez; la frase sigue en 15 / 31 / 16 con 0 sin clase | Ningún hallazgo de PD1-7 en ninguna evidencia |
| Las bases de la demostración | En las tres cambia solo `creada_de.juez.huella`; ningún caso; el juguete sembrado sale en los mismos 344 casos | Los casos de la CI están entre las evidencias rejuzgadas (`ci`, `ci2`, `mant`) y ninguno trae PD1-7 |
| Las del proyecto de ejemplo | Solo la huella del juez; ningún caso | |

Si P-MD-25 (b) se corre con el juez nuevo al poner las pruebas en verde antes de sellar, se declara en el sello, como en la 40: la
previsión se apoya en el recuento de PD1-7, que no depende del juez.

## 6. Lo que arrastra

- **La huella del juez:** cambian `conversion.py` y `mcp_verificador.py` (los dos en `FICHEROS`). Toda la cadena de la 40 se repite.
- **Las tres bases de la demostración:** `base_nc.sh` (unos 50 minutos), dos corridas iguales byte a byte y «igual» contra la
  base; comprobadas con `po/comprobar_bases_po.py`, copia de `pd/comprobar_bases_pd.py` que toma la huella publicada por argumento
  en vez de la constante (la de la 40 está sellada con la suya), con su control de cuatro defectos.
- **El proyecto de ejemplo:** sus dos bases con `ejemplo-ci/ci/hacer_base.sh` y el pin de `ejemplo-ci.yml` y `rojo-ci.yml` en un
  segundo push; `cv/ci/CI.md` puede nombrar la 41 junto a la 40 como juez que cambia sin cambiar ningún caso (texto, sin huella).
- **La información del juez:** S-CV-4 y L-CV-18 (texto), el perfil de ORU (17 filas), `C["PD1-7"]` o `CITAS_PD17` según Q-PO-2, y
  la entrada «etapa 41» al principio de `REVISION`. `SERVIDOR` sigue en 1.4.
- **Las pruebas que fijan huellas o tamaños:** P-VX-20, P-MD-24, P-MD-25 (d), P-CV-34; y las cifras de pruebas de la tabla
  «Correrlo» del README de `verificador/`, si las lleva, como en la 40.
- **Cada push por la opción B:** ensayo con `ensayo_flujo.py` y, tras el push, `comprobar_publicado.py` con los tres
  `ENSAYO.json`.

## 7. Lo que no resuelvo y por qué

- **Varios PATIENT_RESULT en un ORU** (v2.5 lo admite): el juez lee el primer PID y leerá el primer PD1, aunque esté en otro grupo.
  Es la lectura de un paciente que el juez ya tiene; se declara en L-CV-18 y no se arregla aquí (otros fallos del juez están fuera
  de la etapa).
- **La Observation de un OBX que pierde su código y lleva el valor de PD1-7** pasa por la de PD1-7 (candidata por código). El
  mismo riesgo existe en ADT desde la 40; el juez no tiene con qué separarlas, se declara.
- **Otro `value[x]`** (`valueString`, `valueBoolean`) sigue sin reconocerse, como en la 40 (L-CV-18).
- **Los tipos de 2.6 y posteriores:** se lee el primer componente de PD1-7 y nada más; fuera de la etapa por el ANTES.

Nada de lo anterior cambia la frase del estudio de conversores (15 nuevas, 31 ya declaradas, 16 convenciones): ningún hallazgo de
PD1-7 existe en las evidencias y el clasificador de clases no mira el juez más que por su huella.
