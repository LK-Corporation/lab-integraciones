# Diseño a ciegas: la regla de M-4 reconoce también el texto del juez de CV4 (etapa 38)

Diseño, no código. Responde a `cl/estado_cl.md` y a la decisión de Jev (`cl/decision-jev-cl.md`, Q-CL-1: **arreglar**, 0,84).
Todo lo que sigue se comprobó sobre una copia de `fase12` y sobre los dos juicios nombrados en el encargo; nada del laboratorio se
tocó.

## 0. Lo que hay (comprobado)

El juez escribe el hallazgo de PL.9 de Microsoft con dos textos, ambos con hecho `PV1-3`, clase `fidelidad` y ruta
`Encounter.location`, y `juzgar_cv2.asignar` los lleva a los dos al mismo mecanismo, **MC-ADT-3**:

| Juicio | «falta la descripción '…' (PL.9)» | «la descripción '…' contiene PL.9 '…' sin ser PL.9» |
|---|---:|---:|
| Del estudio (CV3, `54a90cd9`) | 16 hallazgos, 16 casos | 0 |
| De hoy (= CV4 en los 736 casos) | 8 (los casos en que la descripción lleva una secuencia de escape, `\S\`) | 8 |

La regla de M-4 en `cv/cv3_clases.py` pide el texto «falta la descripción». En `regla()`, una fila que casa por conversor y
mecanismo pero no por texto se salta, y **M-4 es la última fila de `R` para (microsoft, MC-ADT-3)**: antes van M-1 («la cadena
de Location no conserva»), M-3 («observado None») y M-2 («status: esperado»), cada una con su texto, y después no hay ninguna.
Por eso los 8 hallazgos con el texto nuevo no caen en otra clase: caen en «sin clase», que el guion imprime y no hace fallar.

Los dos textos **conviven en el mismo juicio** (8 y 8 hoy), así que la regla tiene que aceptar los dos, no cambiar uno por otro.

## 1. El cambio de la regla de M-4

Dos ediciones en `cv/cv3_clases.py`, conservando el CRLF, aplicadas por un parche idempotente `cl/parche_m4_cl.py` calcado de
`jz/parche_m28_jz.py` (afirma que cada texto a sustituir está una sola vez; sin argumentos actúa en el laboratorio y añade el
bloque del sello; con la ruta del clon público, en `verificador/cv/…`).

**a) La fila de M-4:** el texto pasa de una cadena a una tupla de textos, de los que basta uno.

```
antes:   ("M-4", MS, {"MC-ADT-3"}, "falta la descripción", None, "ya_declarada", …
después: ("M-4", MS, {"MC-ADT-3"}, ("falta la descripción", "contiene PL.9"), None, "ya_declarada", …
```

**b) `regla()`:** admite que `texto` sea una cadena o una tupla.

```
antes:   if cv != conv or mc not in mcs or (texto and texto not in q):
             continue
después: if cv != conv or mc not in mcs:
             continue
         if texto and not any(t in q for t in ((texto,) if isinstance(texto, str) else texto)):
             continue
```

Y el comentario de cabecera de `R`: «texto que debe estar en el «que», o tupla de textos de los que basta uno, o None». Nada más
cambia: ni el orden de `R`, ni `asignar`, ni la clase, el texto, la referencia o la fuerza de M-4.

**Por qué no le quita ni le da casos a ninguna otra clase.** `regla()` devuelve la primera fila que casa. Un hallazgo que llega a
la fila de M-4 ya ha pasado por M-1, M-3 y M-2 sin casar, y detrás de M-4 no hay fila para (microsoft, MC-ADT-3). Aceptar un texto
más en M-4 solo puede mover hallazgos de «sin clase» a M-4; ninguna otra fila mira el texto «contiene PL.9», y el mecanismo que
`asignar` da a ese texto es el mismo MC-ADT-3 de siempre (ruta `Encounter.location`, subtipos `dato_perdido` o
`dato_perdido+valor_distinto`). La frase no puede moverse: `D_ya_declaradas` cuenta clases «ya_declarada» con casos, y M-4 tiene
casos con las dos reglas (8 o 16); las nuevas y las convenciones no pasan por esta fila.

**Medido sobre la copia,** con `regla` + `asignar` caso a caso (lo mismo que hace `cl/reproducir_clases_cl.py`), comparando
casos y ejemplos de cada clase con `cv/CLASES-CV3.json`:

| Juicio | Regla | Sin clase | Difiere del JSON publicado |
|---|---|---|---|
| Del estudio | de hoy | ninguno | ninguna clase |
| Del estudio | nueva | ninguno | ninguna clase (y ninguna clase cambia entre las dos reglas) |
| De hoy | de hoy | 8 (microsoft, MC-ADT-3, «…contiene PL.<n>…») | M-4 (16→8), M-36 (1→0), L-24 (2→0), L-4 (92→96 en ADT) |
| De hoy | nueva | **ninguno** | M-36 (1→0), L-24 (2→0), L-4 (92→96 en ADT) |

Entre las dos reglas, con el juicio de hoy, la única clase que cambia es M-4: gana exactamente `A1-A01-03`, `A1-A02-08`,
`A1-A03-13`, `A1-A04-18`, `A1-A08-23`, `A1-A11-28`, `A1-A13-33` y `A1-A31-38`, y no pierde ninguno. Lo que sigue difiriendo del
JSON publicado es del juez, no del aparato: M-36 y L-24 por CX.4 en CV4 (falsos positivos ya apartados, que es correcto que no
tengan casos), y L-4 por el juez de la etapa 37 (ya marcado en `cv/RESULTADO-CV3.md`, «Marca de la etapa 37»).

**Descartado:**
- pedir solo el trozo común «la descripción»: casa con los dos textos sin tocar `regla()`, pero absorbería en silencio cualquier
  texto futuro del juez sobre la descripción, y la prueba no podría distinguirlos;
- una fila nueva («M-4b») con el texto de CV4: partiría los casos de M-4 en dos ids del JSON y cambiaría la tabla publicada.

## 2. La prueba en rojo antes

**Dónde vive:** `cv/prueba_cv3_clases.py`, nueva, junto a `cv/prueba_vc.py` y con su misma forma (`mira`, «TODO BIEN» si no hay
ningún MAL; sale 1 si lo hay). Va al clon público como las demás pruebas del verificador. No lee juicios ni `privado/`, no
necesita Docker: construye hallazgos sintéticos y llama a `cv3_clases.regla` y a `juzgar_cv2.asignar`.

**Qué comprueba** (cada caso cambia una cosa; los textos son los literales del juez para `A1-A01-03`):

| Id | Entrada | Esperado | Hoy |
|---|---|---|---|
| P-CL-1 | microsoft, MC-ADT-3, «Encounter.location 'UCI^3^1^HOSP^^^^^Box 3': falta la descripción 'Box 3' (PL.9)» | M-4 | bien |
| P-CL-2 | microsoft, MC-ADT-3, «Encounter.location 'UCI^3^1^HOSP^^^^^Box 3': la descripción 'UCI--3--1--HOSP--Box 3' contiene PL.9 'Box 3' sin ser PL.9» | M-4 | **MAL: None** |
| P-CL-3 | los dos textos, como hallazgo (hecho PV1-3, fidelidad, `dato_perdido` y `dato_perdido+valor_distinto`), por `asignar` | MC-ADT-3 los dos | bien |
| P-CL-4 | controles de las filas vecinas: «la cadena de Location no conserva…» → M-1; «…observado None» → M-3; «…status: esperado…» → M-2 | sin cambio | bien |
| P-CL-5 | microsoft, MC-ADT-3, un texto sin ninguna de las dos frases («Encounter.location 'X': otra cosa») | None (la fila no es un cajón de sastre) | bien |
| P-CL-6 | linuxforhealth, MC-ADT-3, el texto de CV4 | L-1, no M-4 (el conversor manda) | bien |
| P-CL-7 | forma de `R`: cada `texto` es None, cadena o tupla de cadenas, y **solo M-4 lleva tupla** (la convención no se extiende sin decirlo) | cierto | bien |

**Por qué cae con la regla de hoy:** `regla()` hace `texto not in q` con «falta la descripción», y el texto de CV4 no lo contiene;
la fila se salta y, al no haber otra para (microsoft, MC-ADT-3), devuelve `None`. Solo P-CL-2 está en rojo; las demás son los
controles de que el cambio no mueve nada más.

**Registro:** la salida contra el `cv/cv3_clases.py` de hoy (con el HEAD) en `cl/ROJO-CL.txt`, como `jz/ROJO-JZ.txt`; tras el
parche, `cl/PRUEBA-CLASES.txt` con la cabecera de `ga/PRUEBA-VC.txt` (fecha, huella del aparato y de la prueba, la orden) y
«TODO BIEN».

**La medida de conjunto, después:** volver a correr `cl/reproducir_clases_cl.py` con los dos juicios → `cl/REPRODUCCION-CL-despues.json`:
la receta sigue reproduciéndose (`se_reproduce: true`) y, con el juicio de hoy, M-4 desaparece de `clases_que_difieren` y de
`casos_que_cambian_de_clase` no sale ningún `sin_clase`. Conviene que el guion añada a su salida el `sin_clase` de cada cálculo
(hoy no lo guarda; es un guion de esta etapa, no sellado), para que «nada queda sin clase» quede escrito y no solo impreso.

## 3. El sello

**Bloque 9 de `ga/SELLO-GA.txt`,** añadido por `cl/parche_m4_cl.py` sin argumentos, con la forma del bloque 8:

```
SELLO DE LA ETAPA 33, bloque 9 (<fecha>): desde la etapa 38, M-4 reconoce también el texto del juez de CV4 (cl/decision-jev-cl.md, Q-CL-1 a)
# M-4: texto «falta la descripción» -> («falta la descripción», «contiene PL.9»), y regla() admite una tupla de textos de los que basta uno; la clase, su texto y sus casos no cambian
<sha256>  cv/cv3_clases.py
```

Los bloques 1 a 8 no se tocan. Los ficheros propios de la etapa (`cl/parche_m4_cl.py`, `cv/prueba_cv3_clases.py`, `cl/ROJO-CL.txt`,
`cl/PRUEBA-CLASES.txt`, `cl/REPRODUCCION-CL-despues.json`) van a `cl/SELLO-CL.txt`, debajo del sello de la previsión.

**Lo que no se toca:**
- `cv/CLASES-CV3.json`: conserva la huella de su juez (`54a90cd9`) y se reproduce con su receta, con la regla de hoy y con la nueva;
- los JSON de clases de etapas pasadas: `ga/CLASES-GA-v1.json`, `ga/CLASES-GA-v2.json` (bloque 4 del sello de la 33),
  `jz/CLASES-JZ-antes.json` y `jz/CLASES-JZ-despues.json`. Los cuatro llevan M-4 con 8 casos y 8 «sin clase» con la firma
  «Encounter.location <v>: la descripción <v> contiene PL.<n> <v> sin ser PL.<n>»: son el aparato de su momento, y se quedan
  como están. El resultado de esta etapa dice que esos 8 son M-4 con la regla de hoy;
- las copias selladas de `ga/sellada/`.

El clon público: `cv/cv3_clases.py` y `cv/RESULTADO-CV3.md` ya van «en su sitio» (`jz/preparar_publicacion_jz.py`, `EN_SU_SITIO`,
parcheados en el clon); la publicación de esta etapa hace lo mismo con `cl/parche_m4_cl.py <clon>` y copia la prueba nueva a
`verificador/cv/`. Tras el push, la comprobación de después con los tres `ENSAYO.json`, como siempre.

## 4. Qué se dice en lo publicado

Sin reescribir resultados sellados: marcas fechadas, como la de la etapa 37.

- **`cv/RESULTADO-CV3.md`:** «## Marca de la etapa 38 (<fecha>)», detrás de la de la 37 (y antes de la nota de copia pública si
  la hay). Dice que el juez de CV4 escribe el hallazgo de PL.9 de Microsoft con un segundo texto; que `cv/cv3_clases.py` lo
  reconoce desde esta etapa (bloque 9 del sello de la 33) y que sin él 8 hallazgos quedaban «sin clase» y M-4 daba 8 casos en vez
  de 16; que con el juicio de hoy M-4 vuelve a sus 16 y nada queda sin clase; que M-36 y L-24 no tienen casos desde CV4 porque
  eran falsos positivos de CX.4, ya apartados; y que `cv/CLASES-CV3.json` no se toca. La frase, la misma.
- **`RESULTADO-CONVERSORES.md`:** la afirmación «M-36 y L-24 ya estaban apartadas, y M-4 es ya declarada en los dos jueces» es
  cierta para la clase y **queda corta para el aparato**: con el juez de CV4, la regla de M-4 reconocía 8 de los 16 hallazgos y los
  otros 8 caían en «sin clase», no en otra clase. Se marca con un párrafo fechado al final de «Qué cambió en el juez durante la
  etapa» (o al final del documento, si se prefiere no tocar la sección), que remite a `RESULTADO-CLASES.md`. La cifra publicada
  «6 casos de PL.9 pasan a `valor_distinto`» es correcta y no se toca: 8 hallazgos cambian de texto, y 2 de ellos (`A1-A03-13`,
  `A1-A11-28`) ya llevaban `valor_distinto` en CV3 por otro hallazgo del mismo campo.
- **`RESULTADO-JUEZ.md`,** «Lo que se vio de paso»: «M-4 tenía 16 en ADT y ahora da 8 … queda fuera de la etapa». Una línea
  fechada debajo: la causa está medida en `RESULTADO-CLASES.md` (el aparato, no el juez), y `jz/CLASES-JZ-*.json` se quedan como
  se escribieron.
- **`RESULTADO-CLASES.md`** (el de la etapa, con su frase del ANTES): «Las clases publicadas del estudio de conversores **se
  reproducen** con su receta; la diferencia de M-4 viene **del aparato** (la regla pedía solo el texto del juez de CV3) y la de
  M-36 y L-24 **del juez** (CX.4 en CV4)». Con la tabla del §1 y los ocho casos.
- README y «About», al día como en cada etapa; la frase del estudio (15 nuevas, 31 ya declaradas, 16 convenciones) no cambia en
  ningún sitio.

## 5. Lo que no resuelvo, y por qué

- **El guion dice que «comprueba que nada que cuente quede sin clase», pero solo lo imprime.** Hacerlo fallar (salida distinta
  de 0 o excepción) cambia la conducta de un aparato sellado que llaman `ga/comparar_ga.py`, `ga/cifras_ga_b.py`, `ga/cruce_ga.py`,
  `ga/riesgo_ga.py` y `cl/reproducir_clases_cl.py`, y los JSON pasados se escribieron con «sin clase» no vacío. Es otra decisión
  (para Jev, fuera de esta etapa). Mientras, la prueba P-CL-7 y el `sin_clase` guardado por `reproducir_clases_cl.py` hacen el
  trabajo de aviso.
- **Los 8 casos que hoy siguen con el texto viejo** (`A1-A01-04`, `A1-A02-09`, …: la descripción lleva `\S\`, y el juez no la
  encuentra en la concatenación de Microsoft). Es conducta del juez y cuenta como M-4 con las dos reglas; si debería decir también
  «contiene PL.9» es del juez, fuera de la etapa (ANTES, «Fuera de la etapa»). Solo lo dejo visto.
- **M-36 y L-24 sin casos:** no se les devuelve ninguno. Eran falsos positivos del juez de CV3, apartados en el estudio, y el juez de
  CV4 dejó de darlos; las filas se quedan en `R` como `fuera_juez` con 0 casos, y el JSON publicado las conserva con los suyos.
- **Los JSON de clases pasados no se recalculan.** Están sellados; se dice en el resultado qué eran esos 8 «sin clase».
