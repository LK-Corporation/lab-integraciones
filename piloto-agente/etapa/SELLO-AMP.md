# Sello de la ampliación del piloto del agente (AMP1, 13-oct-2026)

Se commitea **antes de la primera tirada** de cualquier brazo de AMP2 (`agente/amp/diseno-ampliacion-fable.md` §1.5). Desde aquí
no se añade, quita ni cambia ningún caso, réplica, umbral ni regla. **Es la última etapa** (S-AMP-9): ningún resultado dispara
otra ampliación. La clave (`privado/agente/amp1/amp_clave.json`) no se publica; aquí va su huella.

## 0. Decisiones (AMP0)

`agente/amp/decisiones-qamp.md`:
- Q-AMP-1, de Víctor: no cuentan los fallos ya medidos en el piloto.
- Q-AMP-2..10, de Jev: las 9 como recomendó Fable salvo Q-AMP-9 (los controles C0 entran en R-MT4, DV-AMP-1).
- Q-AMP-8 y Q-AMP-9 quedan para Víctor como «a cara o cruz en Jev».

## 1. Casos de la etapa 2

| Caso | Corpus | Caja / punto | Disparadores (grupos) | Regresión (AA / rechazos) | Categoría medida | Verdad o zona |
|---|---|---|---|---|---|---|
| H-CAB-1 (CIR-MS-1 + 1b fundidos, S-AMP-2) | H, de `14e17de` | LABORUMUT / `oru_fhir`, árbol `14e17de^` | 14: 2.4 (5), MSH-12 vacío (3), MSH-11 vacío (3), MSH-11 fuera de 0103 (3); construidos (S-AMP-3) | 60 (40 / 20) | falso_rechazo 5, código 3, aceptado_imposible 6 | 4 unidades: `OruRequest` MotivoRechazo, Storage y cabecera (propiedades nuevas); `Util.Obx` Rellenar |
| R-ADT-7 | R | LABADTMUT / `adt_fhir` | 8: A01 NE/NE (5), A08 NE/NE (3) | 65 (45 / 20), con 5 AL/AL | aceptado_imposible 8 | Item `AdtFhirIn`; `Comun.Servicio.OnInit` |
| R-ADT-8 | R | LABADTMUT / `adt_fhir` | 8: apellido latin-1 (5), dirección latin-1 (3); MSH-18 vacío | 68 (48 / 20), con 5 UTF-8 y 3 con MSH-18 = 8859/1 | falso_rechazo 5, guardado 3 (prevista: guardado; se adjudica, no se corrige) | `Comun.Servicio.OnInit`; `Comun.Mandos.Omision`; Item `AdtFhirIn` |
| R-MS-3 | R | LABORUMUT / `oru_fhir` | 8: OBR-25 F^Final (5), P^Preliminar (3) | 60 (40 / 20) | falso_rechazo 8 | `OruRequest.MotivoRechazo`; `Util.Obx` Informe, En0123, Estado0123 |
| R-MS-4 | R | LABORUMUT / `oru_fhir` | 8: OBR-4 ^Hemograma (5), ^Hemograma^ (3) | 60 (40 / 20) | falso_rechazo 8 | `OruRequest.MotivoRechazo`; `Util.Obx` Informe, Codigo; `FhirResultados.CodeableConcept` |
| R-MT1 | R | LABMULTIMUT / `ord` y `adt` | 11: ORM 2.3.1 (5), ADT 2.3 (3), MSH-12 vacío (3) | 47 (35 / 12), con vecinos del borde | aceptado_imposible 11 | `Multi.Operation.Acuse.Decidir`; `Comun.Mandos` ModoSitio y Valor; `Comun.Cabecera.Motivo` |
| R-MT4 | R | LABMULTIMUT / `adt` | 11: PID-8 = X (5), PID-7 inválida (3), C0 en PID-5 (3, DV-AMP-1) | 47 (35 / 12) | aceptado_imposible 11 | `Acuse.Decidir` y `ClaveVacia`; `Puntos.Claves`; los cinco Items `Acuse*` |
| L-multi | limpio | LABMULTIMUT / `ord` | — | — | `correcto` | — |

**n₂ = 7** (1 H + 6 R). Todos pasan sus puertas:
- falla antes (≥ 5 por grupo, o todos si el grupo es menor);
- regresión 100 % `correcto` con ≥ 10 AA y ≥ 5 rechazos correctos;
- VACÍO = 0.

H-CAB-1 pasa además las suyas: el árbol «después» (solo los hunks del fallo y las clases nuevas que llama: `Comun.Cabecera` y
`Comun.Mandos`) compila y arregla 14/14 sin colateral; el árbol «antes» no lleva ninguna pista del arreglo (puerta 5).

**Ninguno se retira.** Tampoco se construyen dos candidatos:
- **DV-AMP-2, H-CAB-2 (CIR-MS-2).** Su disparador exige inyectar entorno, y el diseño preveía retirarlo. No se intenta, para no
  gastar el tope; queda «no construido», sin ser un caso que falló.
- **DV-AMP-3, H-COM-MT2.** No se construye. El FIX de la caja nueva es el parche del implementador para R-MT1, como prevé §2.4.

## 2. Restauración por caja (§1.4.2, medido antes del sello)

| Caja | 5 fijos, firmas iguales en dos cargas | Regla |
|---|---|---|
| LABADTMUT | 2 de 5 | **veredicto** |
| LABORUMUT | 5 de 5 | firma |
| LABMULTIMUT | 5 de 5 (un válido por punto) | firma |

## 3. Controles del evaluador en LABMULTIMUT (§2.4, sobre R-MT1, `ag1_eval` sin cambios)

| Control | Resultado | Pasa |
|---|---|---|
| VACÍO | 0/11 | ✓ |
| INOCUO (un comentario de `Acuse.cls`) | 0/11, colateral 0 | ✓ |
| DAÑINO-A (AR 207 donde se construía el AA) | colateral 35 | ✓ |
| DAÑINO-B (`Decidir` devuelve siempre AA) | colateral 6 | ✓ |
| FIX (quitar la guarda del modo sitio; parche del implementador, en la clave) | 11/11, colateral 0 | ✓ |

Las otras cajas ya separaron sus controles en AG1.

## 4. Pistas y escáner de fugas (§1.4.3)

- **`verificador.json`:** copiado **byte a byte** del piloto (S-AMP-4; su sha256 va en la clave). Lleva las pistas que listó
  Fable: L-MS-1 (R-ADT-7), S97 (R-ADT-8), S98 (R-MT1), L-MT1 (R-MT4) y AMB-ORU-4 (R-MS-4).
- **Comentarios del código:**
  - las tres cajas de LABMULTI nombran CIR-MT1 (pista de R-MT1, sensibilidad viii);
  - las de LABORU nombran solo deudas cerradas (CIR-MS-1/1b y CIR-ORU-4/5/6), ninguna CIR-MS-3/4;
  - la de H-CAB-1 (árbol antes) no nombra CIR-MS-1;
  - las de LABADT nombran CIR-ADT-6 (cerrada), no ADT-7/8.
- **Escáner** sobre cada plantilla (`amp1_sellar.escanear`):
  - 0 coincidencias en `caso.json` y en `CONSIGNA.md`;
  - 0 MSH-10 originales;
  - 0 nombres de caja ni ids de caso; los `R-MS-…` hallados son subcadenas de `CIR-MS-…`;
  - 0 nombres del namespace privado.
- **Lo demás** son comentarios del propio código, como en el piloto («mutante», «piloto», «fichero privado»).

## 5. Análisis (§3; Q-AMP-5: combinación de dos etapas), con los números ya escritos

- **Etapa 1 (recalculada desde el piloto):** n₁ = 11, discordantes 5 a favor y 1 en contra, p₁ a una cola = 7/64 = 0,109,
  **Z₁ = 1,230**. En FIX: 7 a 0, p₁ = 0,0078, Z₁ = 2,418.
- **Etapa 2:** n₂ = 7; p₂ exacto a una cola sobre «alguna réplica» frente a REF; Z₂ = 0 si no hay discordantes.
- **Combinado:** Z = (√11 · Z₁ + √7 · Z₂) / √18.
- **Regla:**
  - **aporta** si Z ≥ 1,645 y Δ (sobre los 18) ≥ 0,20;
  - **no aporta** si Δ ≤ 0,10, o el IC95 de Δ contiene 0 y Δ < 0,20;
  - si no, **indeterminado, y se cierra**.
- **Con n₂ = 7,** aportar exige Z₂ ≥ 1,096 (p₂ ≤ 0,137): en los casos nuevos, al menos **3 a favor y 0 en contra**, o **5/1**, o
  **6/1**, siempre con Δ ≥ 0,20.
- **Secundarios:** (A) réplica, con los casos nuevos solos y la regla del piloto; (C) agregado ingenuo, rotulado optimista.
  También las sensibilidades (i)-(x) de §3.4.
- **Guion:** `agente/amp3.py` (huella abajo), que no se toca tras el sello.

## 6. Brazos, presupuesto y reglas de parada (§4)

**Brazos:**
- **REF:** la congelada, idéntica: n₂ + 1 = 8 pasadas.
- **AG:** `claude -p`, `claude-opus-5-5`, 2 réplicas, 16 tiradas, en orden sembrado por `AMP2|<huella>`; 200 000 tokens nuevos /
  30 llamadas / 10 min por tirada.
- **DS:** `deepseek-v4-pro`, 1 réplica sobre H + R + L-multi, tope 0,45 USD.

**Paradas:**
- las 3 primeras tiradas AG todas sin respuesta o inválidas;
- 2 inválidas;
- 3 M tokens nuevos en el brazo AG;
- 0,45 USD en DS;
- una restauración que falla dos veces en la misma caja: se recrea la caja; si vuelve a fallar, se retiran sus casos (declarado).

Una tirada con otro modelo es inválida. Una cortada por presupuesto no se repite.

## 7. Desviaciones (DV-AMP) y límites de entrada

- **DV-AMP-1.** C0 en R-MT4 (Jev, contra la recomendación de Fable).
- **DV-AMP-2.** H-CAB-2 no se construye.
- **DV-AMP-3.** H-COM-MT2 no se construye; el FIX de la caja nueva es el parche del implementador.
- **DV-AMP-4.** `ag1_cajas.py` gana la caja «multi». Los cambios son:
  - puertos 2580-2584 → 2590-2594, solo en la producción y en `Puntos`;
  - sin credencial;
  - el punto de entrada va como prefijo del id del mensaje, porque el evaluador sellado desempaqueta pares;
  - `a_caja` y `a_user` cuentan con LABMULTIMUT.

  `ag1_eval.py` no cambia.
- **DV-AMP-5.** R-ADT-8 se mide con categorías distintas de la prevista: un falso rechazo en el apellido latin-1 (5) y guardado
  en la dirección (3). Se adjudica; la previsión no se corrige.
- **L-AMP-1..8:** los del diseño, de entrada.
- **L-AMP-7:** el juez es el mismo que en el piloto. No hay cambios en los ficheros del verificador desde `6b42363`; huella de
  versión `73d36c38d23c8620`.

## 8. Huellas (sha256)

| Fichero | sha256 |
|---|---|
| `privado/agente/amp1/amp_clave.json` | `46d48eea5041688f7a8d0d36eea044c33c5ed924cf6f4b8d8693e134e6148b25` |
| `privado/agente/amp1/controles_multi.json` | `e0c884d5d8f2b5aadc0fcac02318a5480d93fa7c1d1fc1619a6d677b4a029f6f` |
| `agente/ref.py` | `647853a578944216766353823486c2b9c5a89028bdd4ab04254c51cceb6b1451` |
| `agente/unidades.py` | `1d63e438eac11c9c125efbcce5016cdc5be88509019853e66222860f17723efa` |
| `agente/CONSIGNA_AG1.md` | `fe0fbca26469bb05a957423ea08e41d251c24557749c23b65c7f2605763f6723` |
| `agente/lanzar_agente.py` | `af5ccfa8319563657148b9c4e807d9b3110f23a14f56b705caed36668cc11a93` |
| `agente/mcp_verificador_agente.json` | `ef12da0bb832e9a310c1f913f511d956f21ec29e5087ae6518e4969c617382c8` |
| `agente/ag1_eval.py` | `63da01cd6e4d5a97480d4b32b5394ba738f462210a2a9c951cf23555b0917f6e` |
| `agente/gen_cajas.py` | `2a05842e66926eeacb9eccadf6de3bb30a3e879df64dda92f383d32e6005a056` |
| `agente/ag1_cajas.py` | `e6d59b687b1a176c338aaab280e928a36c7b7d3fa1edccea2e997ee2635e3f0f` |
| `agente/amp1.py` | `72a9d2e0702d14d5bdf9fcf940984b22e8cdca59c645fa3710f37aec3630408f` |
| `agente/amp1_sellar.py` | `9334bc6c1a575a0a49622abd236160ffb2e0a3b5c1039acb0ac2c600c19255e8` |
| `agente/amp1_controles.py` | `52c83379c2f886b0693daca79a7084d12a1a7981a33b7f6bdfcddf5624fcbea7` |
| `agente/amp2.py` | `9f3703711834dc44c9eb5d699d767d876d334070330fd90ef69bab0ee0d5a045` |
| `agente/amp3.py` | `5037564f0994b084b30e5e9fc4cb55a4a330b1ca30e2d07c73691482a8b424fa` |
| `agente/ag2.py` | `b7947a5a4db01d9b0bd5def1348d5568fca0757e007cd776b31c0ee3afe1ba43` |
| `agente/ag3.py` | `3fc33e33853c650fd746b4643eeb9a1987425825a16f92b21c3c9443528b2ac0` |
| `agente/ag2_tiradas.py` | `15eb351de74bb5d58b08244c5bec525aa2ec397fb257ee3eff8aed7b9fb1ba65` |
| `agente/ag2_ds.py` | `e56df975c0081b5342022e060571fa766766a5ce36f463b9865983a2d360b5db` |
| `agente/amp/diseno-ampliacion-fable.md` | `2fd60d6df5e7515a72b5b16b0c0283e41509b56a36eedb28ed1c280d7d03df76` |

## Adenda durante AMP2: DV-AMP-6 (Q-AMP-11, Jev 0,88)

La 2.ª tirada AG escribió `respuesta.json` con un tabulador literal dentro de una cadena: es JSON no estricto, y el arnés la
leía como «sin respuesta». Se decidió (Jev) **antes de mirar qué localiza**: lector tolerante con caracteres de control dentro de
las cadenas para **todas** las tiradas de la ampliación, de los dos brazos; el estricto se reporta como sensibilidad
(`json_estricto` en cada `puntos.json`). En el piloto no hubo ninguna respuesta no estricta (0 de las del piloto), así que la
etapa 1 no cambia.
