# VE1-b: las pruebas, en rojo antes del código (22-oct-2026)

**Hecho.** Las pruebas del diseño (`ve/diseno-verificador-ve-fable.md` §1.4, §2.5 y §3.3) están escritas en
`ve/prueba_ve.py`. Cada una fija lo que da el juez de hoy y lo que debe dar después.

| Pasada | Resultado |
|---|---|
| `python3 ve/prueba_ve.py hoy` (juez de hoy) | **TODO BIEN**: 21 pruebas, **14 en rojo por la razón prevista y 7 controles** |
| `python3 ve/prueba_ve.py` (lo de después, con el juez de hoy) | Fallan **exactamente las 14** que no son control; los 7 controles pasan |
| Ficheros de la huella del juez | **sin tocar** (`git status` vacío, huella `73d36c38…`); la regresión, CASA contra la línea base |

## Las pruebas

| Prueba | Mecanismo | Hoy | Después |
|---|---|---|---|
| P-VE-1 | M12, adt_fhir: AA + L16 sin canónico | `correcto` | `fallo_silencioso`, `fidelidad/sin_canonico` |
| P-VE-2 | M12, adt_a01: AA + L01 sin canónico | `correcto` | ídem |
| P-VE-3 | M12, oru_fhir: AA + L15 sin canónico, ORU válido | `correcto` | ídem |
| P-VE-3b | M12, oru_fhir con OBX-5 «1,5» en un NM | `fallo_silencioso` por el acuse | se añade `sin_canonico` |
| P-VE-4 | **control:** un fallo de lectura del canónico declarado por el lector | `indeterminado/lectura` | igual |
| C-1, C-2, C-4 | **controles:** AA con canónico; AR 201 sin canónico; AA sin log ni canónico (L5) | `correcto` | igual |
| P-VE-5 | M19: A31 con PV1-2 = N, un Encounter del paciente | `correcto` | `fallo_silencioso`, `fidelidad/almacen` PV1-2 |
| P-VE-6 | M19: el mismo Encounter, en `previos` | `correcto` sin nota | `correcto` con la nota `almacen_previos` |
| P-VE-7 | **control:** el mismo Encounter por visita y por paciente | `correcto` | igual (se cuenta una vez) |
| P-VE-8a-d | M19 con PV1-19 vacío (S78): 1 igual a la proyección / status cambiado / 0 / 2 | `correcto` con la nota L-ADT-19 | `correcto` sin nota / `fidelidad/almacen` PV1-2 / `fidelidad/ausente` PV1 / `fidelidad/duplicado` PV1 |
| P-VE-9 | M19: AE 102 y un Encounter del paciente | sin `rechazo_con_escritura` | con `acuse/rechazo_con_escritura` |
| P-VE-12 | MS9, acuse: MSH-12 vacío y PID-8 = V en un perfil con versión asumida | AA, con la tolerancia S22 y la alternativa S26 | AE 103 en PID-8, sin alternativa |
| P-VE-12b, 12c | **controles:** 2.6 escrito (S22 y S26 como hoy); perfil lab con MSH-12 vacío (AR 101) | | igual |
| P-VE-13 | MS9, verificar con AA | un hallazgo de PID-8 que solo da el mapeador | uno solo, fusionado, de acuse y mapeador |
| P-VE-13b | MS9, verificar con AE 103 | `correcto`, con la alternativa S26 | `correcto` sin S26 |

**El perfil con versión asumida** es un perfil mínimo en memoria (`_ve`: MSH-12 vacío es 2.6, regla H4), como proponía el
diseño. El del sitio no se carga ni se nombra.

## Desviaciones (DV-VE)

- **DV-VE-4.** Las pruebas viven en `ve/prueba_ve.py` y no repartidas por las suites, como decía el diseño. Así no se tocan
  los ficheros de la huella del juez antes del código, y el rojo se mide contra el juez de hoy intacto. En VE1-c pueden
  pasar a las suites, declarándolo.
- **DV-VE-5.** P-VE-3, tal como la escribió el diseño (OBX-5 «1,5» con NM), no estaba en rojo. El acuse ya lo caza hoy
  (`contenido/aceptado_imposible`), aunque falte el canónico. Se partió en dos:
  - P-VE-3, un ORU válido sin canónico, que es el rojo de MMI-12 en oru_fhir;
  - P-VE-3b, el «1,5», donde solo cambia que se añade `sin_canonico`.
- **DV-VE-6.** P-VE-4 no se puede poner en rojo. Hoy cualquier fallo declarado por el lector del almacén ya da
  `indeterminado/lectura`, y el canal que el diseño quería crear ya existe. Pasa a **control**: protege que el
  `sin_canonico` nuevo no le gane a un fallo de lectura.
- **DV-VE-7.** El control del lote de varios mensajes (AA + L01 con canónico, junto a AR + L03 sin canónico) no se escribió
  a mano. Lo cubre la foto de la regresión, que trae lotes (2.752 mensajes en 2.721 instancias), y en E-VE1-1 los 34
  mensajes no AA sin canónico tienen que conservar sus hallazgos.
- **P-VE-10 y P-VE-11** (los lectores contra FHIR) no son de VE1-b: van en VE1-c y VE1-d.

**Siguiente: VE1-c, el código**, de menor a mayor: MS9 → M12 → M19 en el juez → M19 en los lectores → CT. Cada paso deja
en verde sus pruebas sin romper ninguna otra.
