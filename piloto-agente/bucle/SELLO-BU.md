# Sello del estudio «agente con bucle de prueba» (BU1, 13-oct-2026)

Se commitea **antes de la primera tirada** de BU2 (`agente/bucle/diseno-bucle-fable.md` §5.5). Desde aquí no se añade ni quita
ningún caso, réplica, umbral ni regla, y la consigna no se retoca. **Este estudio se cierra con su resultado**, sin BU-bis
(S-BU-10). La clave (`privado/agente/bu1/bu_clave.json`) no se publica; aquí va su huella.

## 0. Decisiones (BU0)

`agente/bucle/decisiones-qbu.md`:
- **Víctor:** Q-BU-1, se remide entero el agente de hoy; Q-BU-5, un caso de más de 90 s se retira.
- **Jev,** las seis de diseño, todas como recomendó Fable:
  - Q-BU-2: veredicto completo sin evidencia;
  - Q-BU-3: un disparador visible por grupo;
  - Q-BU-4: recomendar probar, sin obligar;
  - Q-BU-6: un parche que no aplica no gasta prueba;
  - Q-BU-7: se admite el parche vacío;
  - Q-BU-8: α = 0,05 a una cola.

## 1. Casos

Los 18 reales del piloto y la ampliación, los 4 limpios y R5 como control de cadena. **Ninguno se retira:** todos pasan la
consistencia (dos pruebas con parche vacío dan los mismos veredictos, los disparadores visibles fallan y la regresión visible
pasa). La prueba más lenta tarda 22,5 s (R1, con entorno inyectado), lejos de los 90 s. La tabla por caso está al final (§9).

**Conjuntos:**
- **`D_v`:** el disparador mostrado y uno por grupo, hasta 3 (2 si el caso tiene 5).
- **`R_v`:** 5.
- **Lo oculto:** `D_h` es al menos la mitad de los disparadores, y `R_h` al menos el 75 % de la regresión.
- **En H-CAB-1** (4 grupos), `D_v` cubre 3.

## 2. Controles de la herramienta, tal como la verá el agente (§3.4)

| Caja | Caso | VACÍO | INOCUO | DAÑINO-A | NO COMPILA | NO APLICA (doble y `Port`) | FIX |
|---|---|---|---|---|---|---|---|
| LABORUMUT | H-ORU-4 | 0/3, 5/5 | 0/3, 5/5 | regresión 3/5 | `compila: false` con el error | los dos `aplica: false` | 3/3, 5/5 (parche aceptado del piloto) |
| LABMUT | R4 (FIX: R5) | 0/3, 5/5 | 0/3, 5/5 | regresión 0/5 | ídem | ídem | 2/2, 5/5 (parche de AG-pre) |
| LABADTMUT | R-ADT-8 | 0/3, 5/5 | 0/3, 5/5 | regresión 4/5 | ídem | ídem | 3/3, 5/5 (parche aceptado de la ampliación) |
| LABMULTIMUT | R-MT1 | 0/3, 5/5 | 0/3, 5/5 | regresión 3/5 | ídem | ídem | 3/3, 5/5 (parche del implementador) |

Las cuatro cajas separan, y todas las restauraciones dan «ok».

**Aparato:**
- abrir se niega con una evaluación en curso;
- evaluar se niega con una tirada abierta;
- **la tirada cortada** (el cliente muere en mitad de una prueba) cierra, restaura y devuelve USER.

**Cadena R5 con el agente real:**
- llamó a `probar_parche` 1 vez, y la transcripción y el guardián coinciden;
- entregó el parche que había probado;
- la aceptación da FIX 1, 5/5 y 0 colateral.

## 3. Comparación, regla y formato (§4, sin cambios)

- **Comparación:** FIX en los 18, apareado por caso, BU frente a AG₁ (el agente de hoy remedido y entremezclado). Pares
  discordantes con «alguna réplica».
- **Estadístico:** p exacto de McNemar a una cola; IC95 de Δ por bootstrap con la semilla `BU3|<huella>`.
- **Regla:**
  - **aporta** si p ≤ 0,05 y Δ ≥ 0,20 (en la práctica: 5/0, 6/0, 7/1, 8/1, 9/2 o 10/3);
  - **no aporta** si Δ ≤ 0,10, o el IC contiene 0 y Δ < 0,20;
  - si no, **indeterminado, y se cierra**;
  - **daña** si Δ ≤ −0,10 o el colateral de BU ≥ 2 × el de AG₁ + 0,1.
- **Sobreajuste:** si BU tiene ≥ 3 tiradas con sobreajuste y FIX_visible − FIX ≥ 0,15, se dice que «contenta a lo que ve».
- **Guion:** `agente/bu3.py`.

## 4. Brazos, presupuesto y reglas de parada (§5)

**88 tiradas:** AG₁ 44 y BU 44, en un único orden sembrado (`BU2|<huella>`).
- **Por tirada:** 200 000 tokens nuevos, 30 llamadas y 10 min.
- **BU además:** 4 pruebas que carguen la caja, y hasta 10 llamadas que no aplican.

**Paradas:**
- las 3 primeras BU todas sin respuesta o inválidas;
- ≥ 5 de las 6 primeras BU sin ninguna prueba («no toma la prueba»);
- 2 inválidas;
- 3 incidencias de aparato;
- 9 M tokens nuevos;
- una restauración que falla dos veces.

Una tirada cortada no se repite. REF y DS no corren (L-BU-4).

## 5. Desviaciones (DV-BU)

- **DV-BU-1.** En los casos del piloto, `R_v` = los 5 primeros de la regresión sellada (los fijos de restauración). La
  restricción «≥ 2 AA y ≥ 1 rechazo» solo se aplica donde AA y rechazo se conocen por mensaje (los casos de la ampliación).
- **DV-BU-2.** Los limpios toman `R_v` de un R de la misma caja y del mismo árbol (L-adt de R-ADT-7, L-oru de R-MS-3, L-mut de
  R1, L-multi de R-MT1).
- **DV-BU-3.** El FIX de la caja ADT es el de R-ADT-8, porque R-ADT-7 no tiene ningún parche aceptado. El de ORU es un parche
  aceptado del piloto para H-ORU-4, no el arreglo histórico expresado como parche.
- **DV-BU-4.** La aceptación (`bu2.py evaluar`) usa `ag1_eval.aplicar` y `_medir_arbol`, las mismas reglas que
  `ag1_eval.evaluar`, pero guarda el veredicto por mensaje para separar lo visible de lo oculto. Lleva el cerrojo simétrico.
- **DV-BU-5.** BU1 cazó cuatro fallos del arnés antes del sello, y los cuatro se arreglaron:
  - **cables de los limpios incompletos:** la clave se rehizo;
  - **el punto de entrada en el id del limpio de LABMULTI;**
  - **el guardián comprobaba el presupuesto antes que el parche:** un «no aplica» sin pruebas restantes decía «agotado»;
  - **el guardián se caía si el cliente moría a mitad de una prueba,** sin restaurar y con USER parado. Se detectó en el
    control y se devolvió USER a mano; ahora restaura en toda salida.
- **DV-BU-6.** La descripción de la herramienta es literalmente el punto 1 de §1.7 sin su primera frase; la consigna la
  completa.

## 6. Previsión (§0, sin cambios)

El agente de hoy arregla 8,5 de 18, y el techo realista del bucle está en unos 6 casos más. **«Indeterminado» es el resultado
más probable**, y es válido.

## 7. Lo que no cambia (huellas iguales a SELLO-AMP)

`ag1_eval.py`, `gen_cajas.py`, `unidades.py`, `lanzar_agente.py`, `mcp_verificador_agente.json` y `CONSIGNA_AG1.md`. El
verificador no cambió desde el sello del piloto. `ag1_cajas.py` cambió solo en DV-AMP-4 (la caja multi), ya sellado.

## 8. Huellas (sha256)

| Fichero | sha256 |
|---|---|
| `privado/agente/bu1/bu_clave.json` | `a728d0ab6b91a77afa7240cfd016b269ebb5e03be99901778c2d286aaff3481c` |
| `agente/ag1_eval.py` | `63da01cd6e4d5a97480d4b32b5394ba738f462210a2a9c951cf23555b0917f6e` |
| `agente/ag1_cajas.py` | `e6d59b687b1a176c338aaab280e928a36c7b7d3fa1edccea2e997ee2635e3f0f` |
| `agente/gen_cajas.py` | `2a05842e66926eeacb9eccadf6de3bb30a3e879df64dda92f383d32e6005a056` |
| `agente/unidades.py` | `1d63e438eac11c9c125efbcce5016cdc5be88509019853e66222860f17723efa` |
| `agente/lanzar_agente.py` | `af5ccfa8319563657148b9c4e807d9b3110f23a14f56b705caed36668cc11a93` |
| `agente/mcp_verificador_agente.json` | `ef12da0bb832e9a310c1f913f511d956f21ec29e5087ae6518e4969c617382c8` |
| `agente/CONSIGNA_AG1.md` | `fe0fbca26469bb05a957423ea08e41d251c24557749c23b65c7f2605763f6723` |
| `agente/CONSIGNA_BU.md` | `7696ab80871d209cb3718f938274088ffc02d7e3ab7a26542410fe03a241ec48` |
| `agente/bu1.py` | `4d48f5a1c00040531e88340ee17fce6ddf26d4d9cec373fd6821bdb22d7ab072` |
| `agente/bu_caja.py` | `6261fa5e37af48c1ff4031fe0e77065d12598ea956f704a6061bd29deb48e66f` |
| `agente/mcp_caja.py` | `ab191d051505a997f4046b6b203f077372e6aef70307f1034a668b4b3f6cb8b7` |
| `agente/bu2.py` | `2d34fe593876f6b67a9713ff2c989c0f2f9d81bf3ff2c7a7d44d49271d6e4649` |
| `agente/bu2_tiradas.py` | `6915f361b795665b7ffb92c4d05d34b09478a0129100d3ee1e6198f1f7cb70d1` |
| `agente/bu3.py` | `ca435e9e95041ad9aa75782a44038804d99fc010f7cb486dda2423cb4a570435` |
| `agente/bu1_puertas.py` | `2000ab85267624bfca67ec29c968d31879bf9a879c252cb02a44bf5cdca74251` |
| `agente/bu1_cadena.py` | `4b914fd408676c241f3f90c3f7745a6daa12866629b11f599774a125c10d932d` |
| `agente/bucle/diseno-bucle-fable.md` | `e81a0abb9229b41025f7e9c93d5f877750d95a14e6fd3256f0d7912e8abaf6ce` |

## 9. Casos: conjuntos, latencia y consistencia (BU1)

| Caso | Caja | Grupos | `D_v` | `D_h` | `R_v` | `R_h` | Latencia máx. (s) | Consistente |
|---|---|---|---|---|---|---|---|---|
| H-CAB-1 | oru | 4 | 3 | 11 | 5 | 55 | 11.4 | sí |
| H-ORU-1 | oru | 1 | 3 | 3 | 5 | 55 | 9.1 | sí |
| H-ORU-2 | oru | 1 | 3 | 22 | 5 | 55 | 11.9 | sí |
| H-ORU-4 | oru | 1 | 3 | 22 | 5 | 55 | 11.3 | sí |
| H-ORU-5 | oru | 1 | 3 | 22 | 5 | 55 | 11.8 | sí |
| H-ORU-6 | oru | 1 | 3 | 14 | 5 | 55 | 11.4 | sí |
| L-adt | adt | 0 | 1 | 0 | 5 | 60 | 9.2 | sí |
| L-multi | multi | 0 | 1 | 0 | 5 | 42 | 10.0 | sí |
| L-mut | mut | 0 | 1 | 0 | 5 | 55 | 7.0 | sí |
| L-oru | oru | 0 | 1 | 0 | 5 | 55 | 10.6 | sí |
| R-ADT-7 | adt | 2 | 3 | 5 | 5 | 60 | 11.0 | sí |
| R-ADT-8 | adt | 2 | 3 | 5 | 5 | 63 | 9.1 | sí |
| R-MS-3 | oru | 2 | 3 | 5 | 5 | 55 | 9.9 | sí |
| R-MS-4 | oru | 2 | 3 | 5 | 5 | 55 | 10.4 | sí |
| R-MT1 | multi | 3 | 3 | 8 | 5 | 42 | 9.7 | sí |
| R-MT4 | multi | 3 | 3 | 8 | 5 | 42 | 10.6 | sí |
| R1 | mut | 1 | 2 | 3 | 5 | 55 | 22.5 | sí |
| R2 | mut | 1 | 3 | 5 | 5 | 55 | 13.0 | sí |
| R3 | mut | 2 | 3 | 5 | 5 | 55 | 18.5 | sí |
| R4 | mut | 1 | 3 | 7 | 5 | 55 | 13.1 | sí |
| R5 (control) | mut | 1 | 2 | 3 | 5 | 55 | 12.7 | sí |
| R6 | mut | 1 | 2 | 3 | 5 | 55 | 12.7 | sí |
| R7 | mut | 1 | 3 | 5 | 5 | 55 | 12.9 | sí |

## Adenda durante BU2: DV-BU-7 (Q-BU-9, Jev 0,64)

La tirada 35 (AG₁) salió inválida en la auditoría: el agente buscó en el fichero donde la propia herramienta guardó, en su
sesión, la salida grande de una llamada al verificador. El fichero está fuera de la carpeta, pero solo contiene la respuesta
que el agente ya había recibido; es el artefacto que ya se vio en AG-pre, y puede tocar a los dos brazos. Jev decidió
**corregir la regla y aplicarla a todas las tiradas**: no cuenta como «fuera de la carpeta» leer las salidas guardadas de la
sesión de esa misma tirada (`bu2.py puntuar`, sin tocar el lanzador sellado). La tirada pasa a válida, sin repetirla, antes de
evaluarla. Cada `puntos.json` guarda la auditoría original y cuántas lecturas así hubo, y se reportan por brazo.

## Adenda durante BU2: DV-BU-8 (corrección del recuento de la auditoría, no del diseño)

La tirada 39 (BU) salió inválida por «la transcripción y el guardián no coinciden en número de pruebas»: 3 frente a 2. La
primera llamada nunca llegó a la herramienta, porque `claude -p` no pudo leer como JSON lo que escribió el agente
(`InputValidationError`) y la rechazó antes de enviarla. El recuento de la transcripción contaba esas llamadas. Ahora cuenta
solo las que llegan a la herramienta, que es lo que la comprobación pretendía. Se volvieron a puntuar todas las tiradas BU
hechas, y la 39 pasa a válida.
