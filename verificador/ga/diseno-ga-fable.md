# Diseño de la etapa GA: corpus versión 2, válido en HL7 v2.5

Diseño a ciegas, escrito desde el texto de v2.5 y desde el código de los generadores. No se ha mirado ningún conversor, ningún
resultado ni ningún juicio. Las citas van como `FICHERO.txt:línea` sobre la carpeta `estandares/hl7v2/HL7_Messaging_v25/txt/`.

Convenciones de este documento:

- **Fila de atributos**: `SEQ LEN DT OPT TBL` tal como la da la tabla de atributos del segmento.
- **Veredicto de la versión 1**: `OK` (válido en tipo, tabla y longitud), `ERROR` (viola el tipo, una tabla de HL7 o una
  longitud), `AVISO` (valor fuera del conjunto sugerido de una tabla de usuario, o uso de un componente retirado), `FALTA`
  (campo obligatorio ausente).
- **Tablas**: «tabla de HL7» y «tabla de usuario» según el texto de v2.5 (CH02.txt:541-560): los valores de una tabla de usuario
  son «sugeridos» y el sitio puede redefinirlos; los de una tabla de HL7 son los únicos válidos. Cuando una tabla de usuario no
  trae valores sugeridos («No suggested values defined»), cualquier valor del tipo es válido.
- Los tipos de dato: optionalidad, tabla y longitud de cada componente vienen de las tablas de componentes de CH02A
  (CH02.txt:484-487).

Hechos generales del estándar que se usan varias veces:

- Nulo: «Except where noted, HL7 data fields may take on the null value», transmitido como `""` (CH02.txt:390-395). Un nulo es un
  valor presente, distinto de omitir el campo.
- Longitud: la del campo es normativa y se calcula con los separadores de componente y subcomponente, sin el de repetición
  (CH02.txt:426-433). Las longitudes de componente vienen de las tablas de tipos (CH02.txt:484-487).
- Optionalidad R/O/C/B/X/W (CH02.txt:457-479); «B» es un campo conservado por compatibilidad.
- Segmentos Z: reservados a definiciones locales, el estándar no define ninguno (CH02.txt:335-336); el receptor ignora lo que no
  espera (CH02.txt:932-936).
- Escapes `\F\ \S\ \T\ \R\ \E\`: válidos dentro de un ST (CH02.txt:958-968).
- Juego de caracteres: con MSH-18 vacío, el mensaje es ASCII de 7 bits (CH02.txt:4599-4602); ST admite los imprimibles 0x20-0x7E
  (CH02A.txt:5061-5063).

---

## 1. GENADT v2

### 1.1 Las familias: propósito (del código) y cómo lo conserva la versión 2

`gen_adt.py` produce 216 bases: 8 eventos (A01, A02, A03, A04, A08, A11, A13, A31) × 9 familias × 3 repeticiones, con `random.Random(1)`.
Las estructuras son las de v2.5: A01/A04/A08/A13 → ADT_A01 (Ch03.txt:216), A02 → ADT_A02 (Ch03.txt:325), A03 → ADT_A03
(Ch03.txt:414), A31 → ADT_A05 (Ch03.txt:599), A11 → ADT_A09 (Ch03.txt:1052); `EVENT_PRE`/`EVENT_POST` siguen esas gramáticas.

| familia | lo que ejercita (del código) | segmentos opcionales | en la versión 2 |
|---|---|---|---|
| `minimo` | MSH, EVN, PID (3, 5, 7, 8) y PV1 (2, 3): el mensaje más corto | ninguno | igual salvo lo de §1.5 (EVN-4, PL.6) |
| `completo` | todos los opcionales del evento y los campos «de más» de PID y PV1 (PID-2, 12, 22, 29, 30, 33, 34; PV1-4, 7, 8, 10, 11, 14, 18, 19, 44, y 6/36/37/45 por evento) | todos | se arreglan los campos inválidos; se conservan todos los segmentos y campos |
| `repeticiones` | repeticiones en PID-3 (MR/PI/PT), PID-5, PID-11, PID-13 | ninguno | igual salvo §1.5 |
| `escapes` | `\F\ \S\ \T\` en PID-5 y `\R\ \E\` en PID-11 | ninguno | igual salvo §1.5 |
| `delimitadores` | MSH-1/MSH-2 `#$%*!` en todo el mensaje | ninguno | igual salvo §1.5 |
| `nulos` | `""` en campos de PID, PV1 y en cada opcional | todos | los nulos se quedan en campos O; los campos R reciben valor (§1.4) |
| `fechas` | precisiones de TS: año, mes, día, hora, minuto, segundo con fracción y zona (EVN-2/3, PID-7/29/33, PV1-44/45) | ninguno | igual salvo §1.5 |
| `opcionales` | opcionales presentes; la repetición 1 solo PD1, PV2, DB1, OBX, DG1 | según repetición | como `completo` |
| `z` | un segmento local ZAD tras PV1 | ZAD | igual salvo §1.5 |

Las 144 bases de `minimo`, `repeticiones`, `escapes`, `delimitadores`, `fechas` y `z` no escriben ningún campo con error de tipo o
de tabla de HL7 (§1.3). Solo tienen dos avisos de tabla de usuario comunes a todas las familias (EVN-4 y PL.6, §1.5), que son la
pregunta abierta P1.

### 1.2 Regla: los valores nuevos no sacan números del azar

Todos los valores que la versión 2 añade o cambia son **constantes** o **se derivan de valores ya sorteados** en la versión 1 para
esa misma base (`event_time`, `discharge_ts`, `seq`). Ninguna línea nueva llama a `rng`. Así el flujo de `random.Random(1)` es el
mismo byte a byte y los nombres, fechas, direcciones y teléfonos de cada base coinciden con los de la versión 1.

Cómo se garantiza (dos guardas, las dos en la comprobación «solo cambia esto», §8):

1. **Diff por campo**: para cada una de las 216 bases, se parte cada segmento por campos y se comparan versión 1 y versión 2. El
   conjunto de `(familia, segmento, campo)` que difieren tiene que estar contenido en la lista de §1.6, y los ids, eventos,
   familias y el número y orden de segmentos tienen que ser idénticos. Cualquier otro campo distinto (un apellido, una fecha) es
   fallo.
2. **Contador del azar**: `gen_adt_v2.bases(1)` corre con un `random.Random` envuelto que cuenta llamadas; la cuenta tiene que ser
   la misma que con `gen_adt.bases(1)`. Esto caza una llamada nueva a `rng` aunque no cambie ningún valor visible.

### 1.3 Campo por campo

Para cada campo que escribe el generador: fila de atributos (con cita), valor de la versión 1 y veredicto, valor de la versión 2 y
razón. «todas» = todas las familias que escriben el campo. Cuando un campo es idéntico en las tres familias de interés no se
repite por familia.

#### MSH (CH02.txt:4336-4361)

| campo | SEQ LEN DT OPT TBL | versión 1 | veredicto | versión 2 |
|---|---|---|---|---|
| MSH-1 | 1 1 ST R | `\|` (`#` en `delimitadores`) | OK | igual |
| MSH-2 | 2 4 ST R | `^~\&` (`$%*!`) | OK | igual |
| MSH-3 | 3 227 HD O 0361 | `GENADT` | OK: HD.1 es IS sobre 0361, sin valores sugeridos (CH02.txt:4393-4395) | igual |
| MSH-4 | 4 227 HD O 0362 | `LAB` | OK (0362 sin valores, CH02.txt:4418-4420) | igual |
| MSH-5 | 5 227 HD O 0361 | `DEST` | OK | igual |
| MSH-6 | 6 227 HD O 0362 | `HIS` | OK | igual |
| MSH-7 | 7 26 TS R | `19881028021607-0500`; en `fechas` con fracción `20140302225542.32+0100` | OK: formato DTM `YYYY[MM[DD[HH[MM[SS[.S…]]]]]][+/-ZZZZ]` (CH02A.txt:1729) | igual |
| MSH-8 | 8 40 ST O | vacío | OK | igual |
| MSH-9 | 9 15 MSG R | `ADT^A01^ADT_A01` (A11: `ADT_A09`; A31: `ADT_A05`) | OK: MSG.1 en 0076, MSG.2 en 0003, MSG.3 en 0354, los tres R (CH02A.txt:2809-2811); 15 caracteres justos | igual |
| MSH-10 | 10 20 ST R | `A01-comp-004` (`evento-fam[:4]-seq`) | OK, ≤ 12 caracteres | igual |
| MSH-11 | 11 3 PT R | `P` | OK (0103, CH02A.txt:3912-3916) | igual |
| MSH-12 | 12 60 VID R | `2.5` | OK (0104, CH02.txt:4525-4533) | igual |

#### EVN (Ch03.txt:4637-4645)

| campo | SEQ LEN DT OPT TBL | versión 1 | veredicto | versión 2 |
|---|---|---|---|---|
| EVN-1 | 1 3 ID B 0003 | el evento | OK (A01…A31 en 0003) | igual |
| EVN-2 | 2 26 TS R | `event_time` | OK | igual |
| EVN-3 | 3 26 TS O | solo `fechas`: segundo con fracción sin zona | OK | igual |
| EVN-4 | 4 3 IS O 0062 | `00` (todas) | AVISO: tabla de usuario con valores sugeridos `01 02 03 O U` (Ch03.txt:4679-4690); `00` no está | `01` (P1); constante |

#### PID (Ch03.txt:4798-4838)

| campo | SEQ LEN DT OPT TBL | versión 1 | veredicto | versión 2 |
|---|---|---|---|---|
| PID-2 | 2 20 CX B | `completo`: `EXT0004^^^GENADT^PI` | OK: 19 caracteres ≤ 20; CX.5 `PI` en 0203 (CH02A.txt:1115) | igual |
| PID-3 | 3 250 CX R Y | `P00004^^^GENADT^MR`; `repeticiones`: tres con MR, PI, PT | OK: CX.1 ST(15), CX.4 HD, CX.5 ID 0203 (CH02A.txt:988-1000); MR, PI, PT en 0203 | igual |
| PID-5 | 5 250 XPN R Y | `LOPEZ^DAVID^PEDRO^^^^L`; `escapes` con `\F\ \S\ \T\`; `repeticiones` dos | OK: FN, ST, ST, XPN.7 ID 0200 (CH02A.txt:6150-6171); `L` en 0200 (CH02A.txt:6454) | igual |
| PID-6 | 6 250 XPN O Y | `nulos`: `""` | OK (nulo en campo O) | igual |
| PID-7 | 7 26 TS O | día; `fechas`: año | OK (CH02A.txt:1731-1734) | igual |
| PID-8 | 8 1 IS O 0001 | `M`/`F` | OK (0001, Ch03.txt:5037) | igual |
| PID-11 | 11 250 XAD O Y | `AVDA DEL PARQUE^^BARCELONA^B^28414^^`; `nulos` `""`; `escapes` `\R\ \E\`; `repeticiones` dos | OK: SAD, ST, ST(50), ST(50), ST(12) (CH02A.txt:5661-5680) | igual |
| PID-12 | 12 4 IS B 0289 | `completo`: `01`/`02`/`03`; `nulos` `""` | OK: 0289 sin valores sugeridos (CH02A.txt:5763) | igual |
| PID-13 | 13 250 XTN O Y | `678957265^PRN^PH`; `nulos` `""` | OK: XTN.2 `PRN` en 0201, XTN.3 `PH` en 0202 (CH02A.txt:6583, 6598). XTN.1 es B («deprecated as of 2.3», CH02A.txt:6534-6535): aviso de componente retirado, no error | igual (el componente retirado se queda: es lo que escriben muchos emisores y es válido) |
| PID-22 | 22 250 CE O Y 0189 | `completo`: `H` | OK: `H` está entre los sugeridos de 0189 | igual |
| PID-29 | 29 26 TS O | `completo`, `fechas` | OK | igual |
| PID-30 | 30 1 ID O 0136 | `N` | OK (CH02.txt:6705-6709) | igual |
| PID-33 | 33 26 TS O | día | OK | igual |
| PID-34 | 34 241 HD O | `HIS` | OK | igual |

#### PV1 (Ch03.txt:5654-5720)

| campo | SEQ LEN DT OPT TBL | versión 1 | veredicto | versión 2 |
|---|---|---|---|---|
| PV1-2 | 2 1 IS R 0004 | `I` (A04 `O`, A31 `N`) | OK (0004, Ch03.txt:5736-5745) | igual |
| PV1-3 | 3 80 PL O | `^^ICU^001^HOSPITAL^A^B^1^` (todas) | tipo OK: PL.3 IS 0304, PL.4 HD, PL.5 IS 0306, PL.7/8 IS 0307/0308, sin valores sugeridos (CH02A.txt:3377-3395). AVISO en PL.6 `A`: 0305 sugiere `C D H N O P S` (CH02A.txt:3488). La disposición (punto de atención en PL.3, centro en PL.5) es semánticamente rara pero válida; cf. el ejemplo `4E^136^B^CommunityHospital^^N^^^` (CH02A.txt:3416) | PL.6 `A` → `N` (P1); la disposición es P2 |
| PV1-4 | 4 2 IS O 0007 | `completo` `E`; `nulos` `""` | OK (0007, Ch03.txt:5787-5795) | igual |
| PV1-6 | 6 80 PL O | A02 `completo`: `^^OLD^002^HOSPITAL^A^B^1^` | como PV1-3 | como PV1-3 |
| PV1-7 | 7 250 XCN O Y 0010 | `^DOCTOR^ATTENDING^^^^`; `nulos` `""` | OK: XCN.1 puede faltar («either the ID or the name may be absent», Ch03.txt:6600); 0010 sin valores (Ch03.txt:5889) | igual |
| PV1-8 | 8 250 XCN O Y 0010 | `^DOCTOR^REFERRING^^^^` | OK | igual |
| PV1-10 | 10 3 IS O 0069 | `MED` | OK (Ch03.txt:6003) | igual |
| PV1-11 | 11 80 PL O | `^^PRE^000^HOSPITAL^A^B^1^`; `nulos` `""` | como PV1-3 | como PV1-3 |
| PV1-14 | 14 6 IS O 0023 | `completo`: `A` | AVISO: 0023 sugiere `1`…`9` (Ch03.txt:6062-6072) | `1` (P1) |
| PV1-18 | 18 2 IS O 0018 | `P` | OK: 0018 sin valores (Ch03.txt:6171) | igual |
| PV1-19 | 19 250 CX O | `VN0004^^^GENADT^VN` | OK: `VN` en 0203 | igual |
| PV1-36 | 36 3 IS O 0112 | A03 `completo`: `01` | OK (Ch03.txt:6347) | igual |
| PV1-37 | 37 47 DLD O 0113 | A03 `completo`: `^^HOME^001^HOSPITAL^A^B^1^` | **ERROR de tipo**: DLD tiene dos componentes, IS(20) sobre 0113 y TS (CH02A.txt:1557-1563); aquí hay nueve y el tercero en adelante no existen en el tipo. No lo marca el validador (no ve tipos) | `HOME^` + `discharge_ts` → p. ej. `HOME^20020525102851+0100`; 0113 no trae valores (CH02A.txt:1575-1577), y la fecha ya estaba sorteada |
| PV1-44 | 44 26 TS O | `event_time`; `fechas` hora | OK | igual |
| PV1-45 | 45 26 TS O Y | A03/A13 `completo`, `fechas` | OK | igual |

#### PD1 (Ch03.txt:8496-8520)

| campo | SEQ LEN DT OPT TBL | versión 1 | veredicto | versión 2 |
|---|---|---|---|---|
| PD1-3 | 3 250 XON O Y | `HOSPITAL`; `nulos` `""` | OK: XON.1 es el nombre de la organización, ST (Ch03.txt:8550-8554) | igual |
| PD1-4 | 4 250 XCN B Y | `FACULTY`; `nulos` `""` | OK por tipo (XCN.1 ST); campo B | igual |

#### ROL (CH15.txt:1563-1577)

ROL aparece hasta cuatro veces: tras PID, tras PV2, dentro de PROCEDURE y dentro de INSURANCE.

| campo | SEQ LEN DT OPT TBL | versión 1 | veredicto | versión 2 |
|---|---|---|---|---|
| ROL-1 | 1 60 EI C | no se escribe | OK: «optional when used in ADT and Finance messages» (CH15.txt:1589-1590) | igual |
| ROL-2 | 2 2 ID R 0287 | no se escribe (todas) | FALTA | `AD` en los cuatro ROL; 0287 es tabla de HL7 (CH12.txt:1688-1696): `AD CO DE LI UC UN UP` |
| ROL-3 | 3 250 CE R 0443 | `CP` (tras PID y PV2), `PP` (PROCEDURE), `IN` (INSURANCE); `nulos` `""` tras PID y PV2 | `CP`, `PP` OK; `IN` AVISO: 0443 es de usuario y sugiere `AD AT CP FHCP PP RP RT` (CH15.txt:1614-1622); en `nulos` el `""` va en un campo R (P3) | `IN` → `FHCP` (en el ROL tras IN3, PP o FHCP «is related to the health plan», CH15.txt:1623-1625). En `nulos`: `CP` |
| ROL-4 | 4 250 XCN R Y | `^DOCTOR^ASSISTANT^^^^`, `^DOC^PROC^^^^`, `^DOC^INS^^^^`; en `nulos` (tras PID y PV2) ausente | OK / FALTA | en `nulos`: `^DOCTOR^ASSISTANT^^^^` |
| ROL-5 | 5 26 TS O | no se escribe | — | en `nulos`: `""` (el nulo de la familia se traslada a un campo O) |

Segmento ROL de `nulos` en la versión 2 (tras PID y tras PV2): `ROL||AD|CP|^DOCTOR^ASSISTANT^^^^|""`.

#### NK1 (Ch03.txt:7234-7280)

| campo | SEQ LEN DT OPT TBL | versión 1 | veredicto | versión 2 |
|---|---|---|---|---|
| NK1-1 | 1 4 SI R | `1`; `nulos` ausente | OK / FALTA (Ch03.txt:7289-7292) | `nulos`: `1` |
| NK1-2 | 2 250 XPN O Y | `ESP_CARE^FAMILY^^^^^L`; `nulos` `""` | OK | igual |
| NK1-3 | 3 250 CE O 0063 | `SPOUSE` | AVISO: 0063 sugiere `SPO` para cónyuge (Ch03.txt:7329) | `SPO` |
| NK1-4 | 4 250 XAD O Y | `STREET^^CITY^STATE^ZIP^^` | OK por tipo | igual |
| NK1-5 | 5 250 XTN O Y | `611111111^PRN^PH` | OK (XTN.1 retirado, como PID-13) | igual |

#### PV2 (Ch03.txt:6612-6660)

| campo | SEQ LEN DT OPT TBL | versión 1 | veredicto | versión 2 |
|---|---|---|---|---|
| PV2-3 | 3 250 CE O | `PV2`; `nulos` `""` | OK (CE.1 ST(20), Ch03.txt:6694) | igual |
| PV2-4 | 4 250 CE O | `PV2_DATA` | OK | igual |

#### DB1 (Ch03.txt:8827-8836)

| campo | SEQ LEN DT OPT TBL | versión 1 | veredicto | versión 2 |
|---|---|---|---|---|
| DB1-1 | 1 4 SI R | `1`; `nulos` `""` | OK / nulo en campo R (P3) | `nulos`: `1` |
| DB1-2 | 2 2 IS O 0334 | no se escribe | — | `nulos`: `""` |
| DB1-3 | 3 250 CX O Y | `DISA` | OK | igual |

Segmento DB1 de `nulos` en la versión 2: `DB1|1|""`.

#### OBX (CH07.txt:2529-2548)

| campo | SEQ LEN DT OPT TBL | versión 1 | veredicto | versión 2 |
|---|---|---|---|---|
| OBX-1 | 1 4 SI O | `1`; `nulos` ausente | OK | `nulos`: `1` |
| OBX-2 | 2 2 ID C 0125 | `ST`; `nulos` `""` | OK; «must be valued if OBX-11 … is not valued with an 'X'» (CH07.txt:2574-2575): en `nulos` el nulo no es un valor de 0125 | `nulos`: `ST` |
| OBX-3 | 3 250 CE R | `Height`; `nulos` ausente | OK / FALTA | `nulos`: `Height` |
| OBX-5 | 5 99999 varía C | `170` (ST por OBX-2) | OK | igual; `nulos`: `170` |
| OBX-6 | 6 250 CE O | no se escribe | — | `nulos`: `""` |
| OBX-11 | 11 1 ID R 0085 | no se escribe (todas) | FALTA: «It is a required field» (CH07.txt:3233) | `F` (0085, CH07.txt:3262) |

Segmento OBX de `nulos` en la versión 2: `OBX|1|ST|Height||170|""|||||F`.

#### AL1 (Ch03.txt:7840-7848)

| campo | SEQ LEN DT OPT TBL | versión 1 | veredicto | versión 2 |
|---|---|---|---|---|
| AL1-1 | 1 4 SI R | `1`; `nulos` ausente | OK / FALTA | `nulos`: `1` |
| AL1-2 | 2 250 CE O 0127 | no se escribe | — | `nulos`: `""` |
| AL1-3 | 3 250 CE R | `PEN`; `nulos` `""` | OK / nulo en campo R (P3) | `nulos`: `PEN` |
| AL1-4 | 4 250 CE O 0128 | `MODERATE` | AVISO: 0128 sugiere `SV MO MI U` (Ch03.txt:7900-7905) | `MO` |

Segmento AL1 de `nulos` en la versión 2: `AL1|1|""|PEN`.

#### DG1 (CH06.txt:1528-1556)

| campo | SEQ LEN DT OPT TBL | versión 1 | veredicto | versión 2 |
|---|---|---|---|---|
| DG1-1 | 1 4 SI R | `1`; `nulos` ausente | OK / FALTA | `nulos`: `1` |
| DG1-2 | 2 2 ID (B) R 0053 | no se escribe | la tabla dice «(B) R» y la definición «retained for backward compatibility only» (CH06.txt:1570-1573); 0053 sin valores (CH06.txt:1575-1577). Ambiguo: P4 | `I9` (2 caracteres, LEN 2; ver nota) |
| DG1-3 | 3 250 CE O 0051 | `I10`; `nulos` `""` | OK (0051 sin valores) | igual |
| DG1-4 | 4 40 ST B | `HYPERTENSION` | OK | igual |
| DG1-6 | 6 2 IS R 0052 | no se escribe (todas) | FALTA | `A` (0052: `A W F`, CH06.txt:1616-1620) |

Nota sobre DG1-2: LEN 2 y tipo ID sobre una tabla de usuario sin valores sugeridos, así que vale cualquier valor de 2
caracteres. Se elige `I9` porque ICD9 es «the recommended coding methodology» para el uso retroactivo del campo (CH06.txt:1572);
`I10` no cabe (3 caracteres).

Segmento DG1 de `nulos` en la versión 2: `DG1|1|I9|""|||A`.

#### DRG (CH06.txt:1846-1858)

| campo | SEQ LEN DT OPT TBL | versión 1 | veredicto | versión 2 |
|---|---|---|---|---|
| DRG-1 | 1 250 CE O 0055 | `1`; `nulos` `""` | OK (0055 de usuario, sin valores en el Apéndice A) | igual |

#### PR1 (CH06.txt:1972-1993)

| campo | SEQ LEN DT OPT TBL | versión 1 | veredicto | versión 2 |
|---|---|---|---|---|
| PR1-1 | 1 4 SI R | `1` | OK | igual |
| PR1-2 | 2 3 IS (B) R 0089 | `PR1` | **por la letra, OK**: IS de 3 caracteres sobre una tabla de usuario sin valores sugeridos (CH06.txt:2019-2021). Es un relleno sin sentido, no un error de tipo; el comprobador no lo cazará (§6.4) | `L` (método de codificación local, coherente con `L` como sistema local en 0396, CH02.txt:6299-6302) |
| PR1-3 | 3 250 CE R 0088 | `P001` | OK (0088 sin valores) | igual |
| PR1-5 | 5 26 TS R | no se escribe (todas) | FALTA (CH06.txt:2039-2043) | `event_time` de la base (ya sorteado) |

#### GT1 (CH06.txt:2418-2437)

| campo | SEQ LEN DT OPT TBL | versión 1 | veredicto | versión 2 |
|---|---|---|---|---|
| GT1-1 | 1 4 SI R | `1`; `nulos` ausente | OK / FALTA | `nulos`: `1` |
| GT1-2 | 2 250 CX O Y | `GUARANTOR^LAST^^^^^L`; `nulos` `""` | **ERROR de tipo**: CX.2 (dígito de control) es ST de longitud 1 y lleva `LAST`; CX.7 (fecha efectiva) es DT y lleva `L` (CH02A.txt:988-1000). Es «el nombre en el número» del encargo, y sí deja firma mecánica | `G0001^^^GENADT^AN` (`AN` «account number» está en 0203) |
| GT1-3 | 3 250 XPN R Y | `STREET^^CITY^STATE^ZIP^^`; `nulos` ausente | **por tipo, OK** (todo son ST en FN, ST, ST, ST); es «la dirección en el nombre» del encargo, error semántico que el comprobador no puede cazar (§6.4). En `nulos`, FALTA | `GUARANTOR^LAST^^^^^L` (el nombre que la versión 1 ponía en GT1-2); `nulos`: lo mismo |

Segmento GT1 de `nulos` en la versión 2: `GT1|1|""|GUARANTOR^LAST^^^^^L`.

#### IN1, IN2, IN3 (CH06.txt:3269-3290, 4060-4073, 5120-5133)

| campo | SEQ LEN DT OPT TBL | versión 1 | veredicto | versión 2 |
|---|---|---|---|---|
| IN1-1 | 1 4 SI R | `1` | OK | igual |
| IN1-2 | 2 250 CE R 0072 | `INS1` | OK (0072 sin valores, CH06.txt:1138-1140) | igual |
| IN1-3 | 3 250 CX R Y | `INSURANCE_CO` | OK: CX.1 ST(15), 12 caracteres | igual |
| IN2-1 | 1 250 CX O Y | `1` | OK | igual |
| IN2-2 | 2 11 ST O | `INS2` | OK | igual |
| IN3-1 | 1 4 SI R | `1` | OK | igual |
| IN3-2 | 2 250 CX O | `CERT1` | OK | igual |

#### ACC (CH06.txt:5592-5606)

| campo | SEQ LEN DT OPT TBL | versión 1 | veredicto | versión 2 |
|---|---|---|---|---|
| ACC-1 | 1 26 TS O | `1`; `nulos` `""` | **ERROR de tipo**: DTM exige al menos `YYYY` (CH02A.txt:1729-1732) | `event_time` de la base |
| ACC-2 | 2 250 CE O 0050 | `ACC` | OK (0050 sin valores, CH06.txt:5629-5631) | igual |

#### UB1 (CH06.txt:5775-5800)

| campo | SEQ LEN DT OPT TBL | versión 1 | veredicto | versión 2 |
|---|---|---|---|---|
| UB1-1 | 1 4 SI O | `1`; `nulos` `""` | OK | igual |
| UB1-2 | 2 1 NM B | `B` | **ERROR de tipo**: NM es signo opcional, dígitos y punto opcional (CH02A.txt:2958-2969) | `0` |

#### UB2 (CH06.txt:5986-6005)

| campo | SEQ LEN DT OPT TBL | versión 1 | veredicto | versión 2 |
|---|---|---|---|---|
| UB2-1 | 1 4 SI O | `1`; `nulos` `""` | OK | igual |
| UB2-2 | 2 3 ST O | `C` | OK (es ST, no NM: CH06.txt:6021) | igual |

#### PDA (Ch03.txt:8917-8930)

| campo | SEQ LEN DT OPT TBL | versión 1 | veredicto | versión 2 |
|---|---|---|---|---|
| PDA-1 | 1 250 CE O Y | `1`; `nulos` `""` | OK | igual |
| PDA-2 | 2 80 PL O | `Y` | OK por tipo (PL.1 IS 0302 sin valores); semánticamente vacío pero válido | igual |

#### ZAD (familia `z`)

Segmento local (CH02.txt:335-336): no hay tabla de atributos; el comprobador no lo juzga. Igual en la versión 2.

### 1.4 La familia `nulos`: dónde puede ir un nulo y dónde no

- Un nulo puede ir en cualquier campo «except where noted» (CH02.txt:390-392). En los segmentos que escribe GENADT la única nota
  de este tipo es la de GT1: si el garante es una organización se envía `""` en GT1-3 y si es una persona, en GT1-21
  (CH06.txt:2563, 2854); y la de IN1-2, que admite nulo para eliminar un plan (CH06.txt:3359-3360). Ninguna prohíbe el nulo.
- Un nulo en un campo R: el estándar no lo prohíbe en §2.5.3 y su propio ejemplo de borrado en modo instantánea manda
  `DG1|""|""|…` con todos los campos a nulo, incluidos DG1-1 (SI R) y DG1-6 (IS R) (CH02.txt:2051-2062). Pero «R» significa
  requerido (CH02.txt:464) y un nulo no es un valor de la tabla ni del tipo. Es la pregunta abierta P3.
- Decisión de diseño que vale con cualquier respuesta a P3: en la versión 2 **ningún campo R lleva `""`**. Los nulos de la familia
  se quedan en campos O (PID-6, PID-11, PID-12, PID-13, PV1-4, PV1-7, PV1-11, PD1-3, PD1-4, NK1-2, PV2-3, DRG-1, GT1-2, ACC-1,
  UB1-1, UB2-1, PDA-1) y los tres que estaban en campos R o C (ROL-3, AL1-3, DB1-1, OBX-2) se trasladan a un campo O del mismo
  segmento (ROL-5, AL1-2, DB1-2, OBX-6). Así cada segmento opcional sigue llevando un nulo, que era el propósito de la familia.

### 1.5 Cambios comunes a las nueve familias (pregunta P1)

Dos valores fuera del conjunto sugerido de una tabla de usuario están en las 216 bases: EVN-4 `00` (0062) y PL.6 `A` en PV1-3
(y en PV1-6, PV1-11 de `completo`). Por la letra son válidos (tabla de usuario: CH02.txt:541-549); el alcance de la etapa («el
tipo y la tabla de cada campo que escriben los generadores») los cubre. La versión 2 los cambia a `01` y `N` en todas las
familias, salvo que P1 diga lo contrario. Son constantes: no tocan el azar.

### 1.6 Lista exacta de lugares que pueden cambiar entre la versión 1 y la 2

Es la lista que afirma la comprobación «solo cambia esto» (§8.4). Formato `familia: segmento-campo`. Un segmento repetido
(ROL) se identifica por su posición en la gramática.

**Todas las familias (si P1 = sí):**
- `*: EVN-4` (`00` → `01`)
- `*: PV1-3` (solo el componente 6: `A` → `N`)
- `completo: PV1-6` (A02) y `completo: PV1-11` (componente 6)

**`completo` y `opcionales` (en `opcionales`, solo cuando el segmento está presente):**
- `ROL-2` en los cuatro ROL (ausente → `AD`)
- `ROL-3` del ROL de INSURANCE (`IN` → `FHCP`)
- `NK1-3` (`SPOUSE` → `SPO`)
- `OBX-11` (ausente → `F`)
- `AL1-4` (`MODERATE` → `MO`)
- `DG1-2` (ausente → `I9`), `DG1-6` (ausente → `A`)
- `PR1-2` (`PR1` → `L`), `PR1-5` (ausente → `event_time`)
- `GT1-2` (→ `G0001^^^GENADT^AN`), `GT1-3` (→ `GUARANTOR^LAST^^^^^L`)
- `ACC-1` (`1` → `event_time`)
- `UB1-2` (`B` → `0`)
- `completo: PV1-14` (`A` → `1`, P1)
- `completo: PV1-37` (A03: → `HOME^` + `discharge_ts`)

**`nulos`:**
- `ROL-2, ROL-3, ROL-4, ROL-5` de los ROL tras PID y tras PV2 (`ROL|||""` → `ROL||AD|CP|^DOCTOR^ASSISTANT^^^^|""`)
- `ROL-2` de los ROL de PROCEDURE e INSURANCE; `ROL-3` del de INSURANCE
- `NK1-1`
- `DB1-1, DB1-2`
- `OBX-1, OBX-2, OBX-3, OBX-5, OBX-6, OBX-11`
- `AL1-1, AL1-2, AL1-3`
- `DG1-1, DG1-2, DG1-6`
- `PR1-2, PR1-5`
- `GT1-1, GT1-3`
- `ACC`: no cambia (`ACC|""` se queda)
- `UB1`, `UB2`, `PDA`, `DRG`, `PV2`, `PD1`, `PID`, `PV1` (salvo P1): no cambian

Todo lo demás, en las 216 bases, tiene que ser idéntico byte a byte: MSH entero, PID entero (salvo nada), nombres, fechas,
`colocado`, ids, orden de segmentos y número de segmentos.

---

## 2. A1 v2

`gen_bases_a1.py` escribe 40 bases (8 eventos × 5 familias), sin azar, con PID-1 y PV1-1 a `1`.

### 2.1 Errores accidentales de tipo o tabla

Revisados campo por campo contra las mismas filas de §1.3:

- **Familia `contactos`, PID-5 `de&la&Fuente^Ana^María^^Dra^^L`**: `María` lleva `í`, fuera del ASCII de 7 bits que rige con
  MSH-18 vacío (CH02.txt:4599-4602; ST: CH02A.txt:5061-5063). Es accidental: la familia ejercita subcomponentes de FN, dos
  nombres, XAD.7, XTN.4 y XTN.12, no el juego de caracteres. **Arreglo**: `Maria`. La alternativa (declarar MSH-18, tabla 0211)
  es la pregunta P9.
- Nada más. En detalle, lo que podía parecer error y no lo es: `Sanz^Luis Miguel` (espacio en ST, válido); `C/ Real 5&Piso
  3&Puerta B` (SAD con tres subcomponentes ST, CH02A.txt:4739-4745); `ESP` en XAD.6 (0399, tres letras ISO 3166); `B` y `M` en
  XAD.7 (0190, CH02A.txt:93); `NET`/`Internet` y `PRN`/`PH` en XTN.2/3; `WPN`/`FX` en PID-14; XTN.12 (C) con el número sin
  formato; PID-16 `A D M S W U T G`, todos en 0002; PV1-4 `R` (0007); PV1-10 `CAR` (0069); PV1-14 `7` (0023); PV1-36 `01`
  (0112); PL.9 `Box 3` (ST); PID-7 `198002` y `197512312359` (precisión mes y minuto); PID-29 TS; PID-30 Y/N; MSH-10 de 16
  caracteres como mucho; `VN000^^^HOSP^VN` (0203).

### 2.2 Lo que hace a propósito y se queda

| base(s) | campo | valor | por qué es inválido o especial | cita |
|---|---|---|---|---|
| `pv12vacio` (8) | PV1-2 | vacío | campo R | Ch03.txt:5657 |
| `clases` k=6, k=7 | PV1-2 | `o`, `X` | minúscula / fuera de los sugeridos de 0004 (tabla de usuario: aviso) | Ch03.txt:5736-5745 |
| `clases` k=4, k=5 | PID-8 | `f`, `X` | ídem con 0001 | Ch03.txt:5037 |
| `escapes_251` (8) | PID-8 | `Z` | fuera de 0001 | Ch03.txt:5037 |
| `escapes_251` (7; A31 lleva `I`) | PV1-2 | `Z` | fuera de 0004 | Ch03.txt:5736 |
| `escapes_251` (8) | MSH-12 | `2.5.1` | VID.1 es ID sobre 0104, que acaba en `2.5` | CH02.txt:4525-4533 |

Estas marcas van a la lista del corpus (§7) con la razón.

---

## 3. Las copias completadas del capítulo 3

Los 7 fragmentos de `ejemplos_cap3.json` se quedan byte a byte, marcados «fragmento del estándar». Cada uno recibe una copia
completada con el id del fragmento más el sufijo `-completada`. Reglas de completado: se añade solo lo que exige la gramática
de v2.5 (MSH, EVN, PID, PV1 obligatorios en ADT_A01/A02/A03: Ch03.txt:216, 325, 414) y los campos R de esos segmentos; los
valores añadidos son sintéticos y deterministas (no se copia más texto del estándar); lo que el fragmento trae no se toca, salvo
el caso P5.

Valores comunes de lo añadido: EVN-2 = MSH-7 del fragmento; PID-3 = `CAP3<nn>^^^CAP3^MR`; PID-5 = `EJEMPLO^CAPITULO^^^^^L`;
PV1-2 = `I` (A01, A02, A03) u `O` (A04, paciente no ingresado).

| id | fragmento (Ch03.txt) | le falta | se añade |
|---|---|---|---|
| `cap3-08-A01` → `cap3-08-A01-completada` | 9094-9095 (§3.5.1): solo MSH hasta MSH-10 `MSG00001-` | MSH-11, MSH-12, EVN, PID, PV1 | `MSH-11 P`, `MSH-12 2.5`; `EVN\|A01\|198808181126`; `PID\|\|\|CAP308^^^CAP3^MR\|\|EJEMPLO^CAPITULO^^^^^L`; `PV1\|\|I`. MSH-10 se queda `MSG00001-` (ST válido) |
| `cap3-10-A04` → `-completada` | 9155-9156 (§3.5.3): MSH y EVN | PID, PV1 | `PID\|\|\|CAP310^^^CAP3^MR\|\|EJEMPLO^CAPITULO^^^^^L`; `PV1\|\|O` |
| `cap3-12-A02` → `-completada` | 9239-9241 (§3.5.5): MSH, EVN y PID cortado en PID-3 | PID-5, PV1 | PID-5 `EJEMPLO^CAPITULO^^^^^L` (PID-3 cortado `191919^^^GENHOS^MR~371-66-` es CX válido); `PV1\|\|I` |
| `cap3-14-A02` → `-completada` | 9270-9272 (§3.5.7) | PID-5, PV1 | ídem |
| `cap3-15-A03` → `-completada` | §3.5.8 | PID-5, PV1 | ídem |
| `cap3-36-A04` → `-completada` | 10866-10868: MSH `ADT^A04` sin estructura ni MSH-10/11/12, sin EVN; PID cortado en PID-11 | MSG.3, MSH-10, MSH-11, MSH-12, EVN, PV1 | `MSH-9 ADT^A04^ADT_A01` (MSG.3 es R: CH02A.txt:2811), `MSH-10 CAP336`, `P`, `2.5`; `EVN\|A04\|199902171830`; `PV1\|\|O`. Queda un error del propio ejemplo: PID-5 `Jones^Fluffy^^^^^^D` pone `D` en XPN.8 (código de representación, 0465 = `A I P`, CH02A.txt:3761): P5. PID-8 `S` es aviso (0001 de usuario) y se queda |
| `cap3-37-A04` → `-completada` | 10890-10891: como el anterior; PID cortado en PID-3 | MSG.3, MSH-10/11/12, EVN, PID-5, PV1 | como el anterior más PID-5 `EJEMPLO^CAPITULO^^^^^L`. MSH-4 `Foothill Veterinary Clinic` tiene 26 caracteres en HD.1 (IS, 20): longitud de componente, P8 |

Por qué es lo mínimo: cada añadido es un segmento R de la estructura o un campo R de un segmento presente; no se añade ningún
campo O ni se corrige nada que el fragmento traiga válido.

---

## 4. B36 v2

TXA-12 es EI con LEN 30, R (CH09.txt:834); TXA-13 es EI, LEN 30, C, obligatorio en T05, T06, T09 y T10 (CH09.txt:835,
1417-1421). EI = ST(199) ^ IS(20) sobre 0363 ^ ST(199) ^ ID(6) sobre 0301 (CH02A.txt:1886-1893); con EI.4 = `ISO` el EI.3 es un
OID (0301, CH02A.txt:2344). La longitud cuenta los separadores (CH02.txt:431-433).

- Versión 1: `DOC0036^CSSYN^1.2.840.113619.2.1^ISO` = 36 caracteres; TXA-13 derivado en T06/T10 = 42.
- Versión 2: **`DOC0036^CSSYN^2.999^ISO`** = 23 caracteres. Conserva EI.1 (`DOC%04d`, el patrón de las 40 bases), EI.2 `CSSYN`,
  EI.4 `ISO`, y cambia solo EI.3 por un OID más corto. `2.999` es el arco que ITU-T X.660 reserva para ejemplos; esto no sale de
  v2.5 (que solo pide un OID con tipo ISO) y se anota como decisión del autor (P7).
- TXA-13 que darán T06 y T10 con la derivación de `mev/bases_mdmev.py` (EI.1 + `-PADRE`, EI.2-EI.4 iguales):
  **`DOC0036-PADRE^CSSYN^2.999^ISO`** = 29 caracteres ≤ 30. Esta es la restricción que fija el tamaño: con cualquier OID de más de
  6 caracteres el TXA-13 derivado se pasa de 30.
- Alternativa equivalente: `DOC36^CSSYN^2.999.36^ISO` (24) → TXA-13 de 30 justos; rompe el patrón `DOC%04d`, por eso no se elige.
- `bases_mdm.py` no cambia (§8.3). B36 v2 se deriva (§8.1).

---

## 5. Los gemelos

### 5.1 Base en el estándar

- OBX-6 (CE, CH07.txt:2548) y RXA-7 (CE, CH04.txt:11169) llevan el sistema de codificación en CE.3, ID sobre la tabla 0396
  (CH02A.txt:315).
- 0396 (CH02.txt:6297 y siguientes) trae `ISO+` («ISO 2955.83 (units of measure) with HL7 extensions», CH02.txt:6503), `ANS+`
  (CH02.txt:6308-6309) y `L`/`99zzz` para códigos locales (CH02.txt:6299-6302). No trae `UCUM`: de ahí que los 23 queden sin
  decidir.
- El sistema por omisión de las unidades es ISO+ (CH07.txt:2916-2928); se «anima» a usarlo y se permiten ANSI X3.50 y locales
  (CH07.txt:2931-2935). La figura 7-9 es la lista ISO+ (CH07.txt:8106-8109).
- Las cuatro unidades que aparecen en los 39 ficheros están en la figura 7-9 con esa misma grafía: `mL` (CH07.txt:8415), `mg/dL`
  (CH07.txt:8397), `mg/L` (CH07.txt:8411), `mmol/L` (CH07.txt:8464). No hace falta ANS+ ni local para ninguna.

### 5.2 Tabla de gemelos

El gemelo cambia **solo CE.3** del campo de unidades (`UCUM` → `ISO+`), en todos los OBX/RXA del mensaje. CE.1 y CE.2 se quedan
tal cual (la grafía ya es la de ISO+).

| fichero | tipo | campo | versión 1 | gemelo |
|---|---|---|---|---|
| G01-original (`VXU-AU1c`) | VXU | RXA-7 | `mL^mL^UCUM` | `mL^mL^ISO+` |
| G01-control-1 (`VXU-AU1k`) | VXU | RXA-7 | `mL^mL^UCUM` | `mL^mL^ISO+` |
| G02-original / control-1 (`VXU-AU2c/k`) | VXU | RXA-7 | `mL^mL^UCUM` | `mL^mL^ISO+` |
| G03-original / control-1 (`L09c/k`) | ORU | OBX-6 | `mg/dL^mg/dL^UCUM` | `mg/dL^mg/dL^ISO+` |
| G04-original / control-1 (`M01c/k`) | ORU | OBX-6 | `mg/dL^mg/dL^UCUM` | `mg/dL^mg/dL^ISO+` |
| G05-original / control-1 (`M07c/k`) | ORU | OBX-6 | `mg/dL^mg/dL^UCUM` | `mg/dL^mg/dL^ISO+` |
| G06-original (`ORU-B20`) | ORU | OBX-6 | `mg/dL^mg/dL^UCUM` | `mg/dL^mg/dL^ISO+` |
| G07-original (`ORU-B29`) | ORU | OBX(1)-6, OBX(2)-6 | `mg/L^mg/L^UCUM`, `mmol/L^mmol/L^UCUM` | `mg/L^mg/L^ISO+`, `mmol/L^mmol/L^ISO+` |
| G08-original (`ORU-B30`) | ORU | OBX-6 | `mg/dL^mg/dL^UCUM` | `mg/dL^mg/dL^ISO+` |
| G09…G14-original (`VXU-B11, B16, B18, B21, B37, B40`) | VXU | RXA-7 | `mL^^UCUM` | `mL^^ISO+` (CE.2 vacío se queda vacío) |
| G15…G23-original y control-1 (`VXU-L04, L06, L07, M07, M08, M10, M12, M14, M15`, `c`/`k`) | VXU | RXA-7 | `mL^mL^UCUM` | `mL^mL^ISO+` |

Total: 23 originales + 16 controles = 39 gemelos.

### 5.3 Qué más tiene que quedar igual

Todo lo demás, byte a byte: cada segmento, cada campo, el orden, los `\r`, el `\r` final; en particular lo que hace de cada par
mínimo un par (G01: RXA-18; G02: la segunda repetición de RXA-10; G03: OBX-11; G04: `.5`/`0.5` en OBX-5; G05: la falta de PID;
G15: RXA-21 `D`/`A`; G16: RXA-10; G17/G21: RXA-19; G18: RXA-15; G19: RXA-17; G20: NK1-3; G22: RXA-6 `.5`; G23: RXA-18). La guarda
de §8.4 lo afirma: el diff por campo entre original y gemelo solo puede tocar OBX-6 o RXA-7, y en ellos solo el componente 3
(y MSH-10 si P6 = sufijo).

### 5.4 Cómo se nombran

- Fichero: el nombre del mensaje de origen más `-ISO` antes de `.hl7`: `VXU-AU1c-ISO.hl7`, `VXU-AU1k-ISO.hl7`, `ORU-B20-ISO.hl7`,
  `L09c-ISO.hl7`, …; el nombre de origen es el MSH-10 del mensaje, que es como se llaman los 23 en `/tmp/ga_gemelos`.
- Id en la lista del corpus: el del original más `-ISO`; marca `gemelo_de: <id original>`; corpus `gemelos` (§7, §8).
- MSH-10: igual que el original o con sufijo `-ISO` (≤ 20 caracteres en los 39: el más largo, `VXU-M10k-ISO`, tiene 12). Es P6;
  la recomendación es el sufijo.

---

## 6. El comprobador de tipos

Instrumento nuevo: `ga/comprobar_tipos.py`. Entrada: un mensaje (texto con `\r`). Salida: lista de hallazgos
`(segmento, índice de aparición, campo, repetición, componente, subcomponente, regla, gravedad, valor)`. No sustituye al validador
de IRIS (estructura y obligatorios); se superpone en lo que IRIS no ve.

Fuentes de datos: `estructuras_hl7.CAMPOS` para LEN/DT/OPT/TBL por campo (ya extraído del texto); una tabla nueva de componentes
por tipo de dato, escrita a mano desde CH02A con cita (abajo); `iv/TABLAS-TIPO-IV.json` para saber si una tabla es de HL7 o de
usuario; `privado/iv/TABLAS-VALORES-IV.json` para los valores (no se publica, igual que en la etapa 30).

### 6.1 Reglas por tipo de dato

Tipos que aparecen en los campos que escriben los generadores de ADT: ST, NM, SI, ID, IS, DT, DTM, TS, HD, CX, XPN, FN, XCN, XAD,
SAD, XTN, PL, CE, EI, MSG, PT, VID, XON, DLD. Cada regla: qué comprueba, gravedad, cita.

Reglas comunes:

- **C0 nulo**: un campo o componente que es exactamente `""` es el valor nulo (CH02.txt:390-392); no se le aplica ninguna regla de
  tipo ni tabla. Si está en un campo R, se anota `nulo_en_R` (gravedad según P3; por omisión aviso).
- **C1 componentes de más**: un valor con más componentes (o subcomponentes) de los que define el tipo → error (los componentes
  vienen fijados por la tabla del tipo, CH02.txt:484-487).
- **C2 longitud de campo**: el campo entero, con separadores de componente y subcomponente y sin el de repetición, no puede pasar
  de LEN → error (CH02.txt:426-433).
- **C3 longitud de componente**: un componente que pasa la LEN de su tabla de tipo → aviso (P8).
- **C4 ASCII**: un carácter fuera de 0x20-0x7E con MSH-18 vacío → error (CH02.txt:4599-4602; CH02A.txt:5061-5063). Los escapes
  `\F\ \S\ \T\ \R\ \E\` son válidos (CH02.txt:958-968); un `\` que no abra una secuencia de la lista → error.
- **C5 tabla**: para ID (y para los componentes ID de tipos compuestos), el valor tiene que estar en la tabla; si la tabla es de
  HL7 → error; si es de usuario y tiene valores sugeridos → aviso; si no tiene valores → nada (CH02.txt:541-560; CH02A.txt:2410-2434).
  Para IS igual, con gravedad aviso siempre (es una tabla de sitio por definición). Los patrones del Apéndice A (`99zzz`,
  `HL7nnnn`, `ISOnnnn`) cuentan como pertenencia.
- **C6 componente retirado**: un componente B/«deprecated» valorado → aviso (XTN.1, XCN.7, XPN.6, TS.2).

Primitivos:

| tipo | regla | gravedad | cita |
|---|---|---|---|
| ST | C4; LEN 199 por omisión | error / C3 | CH02A.txt:5051-5063 |
| NM | `^[+-]?(\d+(\.\d*)?\|\.\d+)$`; sin otros caracteres | error | CH02A.txt:2958-2969 |
| SI | entero no negativo, hasta 4 dígitos (0-9999) | error | CH02A.txt:4824-4832 |
| ID | C5 contra la tabla del campo o del componente; tabla de HL7 | error | CH02A.txt:2410-2420 |
| IS | C5; tabla de usuario; LEN 20 | aviso | CH02A.txt:2424-2434 |
| DT | `YYYY[MM[DD]]`, 4/6/8 dígitos, mes 01-12, día 01-31 | error | CH02A.txt:1677-1700 |
| DTM | `YYYY[MM[DD[HH[MM[SS[.S[S[S[S]]]]]]]]][+/-ZZZZ]`, longitudes 4, 6, 8, 10, 12, 14, 16-19; hora 00-23, minuto 00-59, segundo 00-59; zona `[+-]\d{4}` | error | CH02A.txt:1729-1745 |
| TS | TS.1 DTM (R); TS.2 ID 0529 y retirado (C6) | error / aviso | CH02A.txt:5380-5386 |

Compuestos (componente: tipo, tabla, opt; se aplican C1, C3 y las reglas del tipo del componente):

| tipo | componentes comprobados | cita |
|---|---|---|
| HD | 1 IS 0300/0361/0362/0363 según campo; 2 ST; 3 ID 0301 (C: si hay HD.2 tiene que haber HD.3 y al revés) | CH02A.txt:2196-2202 |
| CX | 1 ST(15) R; 2 ST(1); 3 ID 0061; 4 HD; 5 ID 0203; 6 HD; 7 DT; 8 DT; 9-10 CWE | CH02A.txt:988-1000 |
| FN | 1 ST(50) R; 2 ST(20); 3 ST(50); 4 ST(20); 5 ST(50) | CH02A.txt:2079-2087 |
| XPN | 1 FN; 2 ST(30); 3 ST(30); 4 ST(20); 5 ST(20); 6 IS 0360 (B); 7 ID 0200; 8 ID 0465; 9 CE; 10 DR (B); 11 ID 0444; 12 TS; 13 TS; 14 ST | CH02A.txt:6150-6171 |
| XCN | 1 ST(15); 2 FN; 3 ST(30); 4 ST(30); 5 ST(20); 6 ST(20); 7 IS 0360 (B); 8 IS 0297; 9 HD; 10 ID 0200; 11 ST(1); 12 ID 0061; 13 ID 0203; 14 HD; 15 ID 0465; 16 CE; 17 DR (B); 18 ID 0444; 19 TS; 20 TS; 21 ST; 22-23 CWE | CH02A.txt:5808-5835 |
| SAD | 1 ST(120); 2 ST(50); 3 ST(12) | CH02A.txt:4739-4745 |
| XAD | 1 SAD; 2 ST(120); 3 ST(50); 4 ST(50); 5 ST(12); 6 ID 0399; 7 ID 0190; 8 ST(50); 9 IS 0289; 10 IS 0288; 11 ID 0465; 12 DR (B); 13 TS; 14 TS | CH02A.txt:5661-5680 |
| XTN | 1 ST (B); 2 ID 0201; 3 ID 0202; 4 ST; 5 NM(3); 6 NM(5); 7 NM(9); 8 NM(5); 9 ST; 10 ST(4); 11 ST(6); 12 ST | CH02A.txt:6529-6552 |
| PL | 1 IS 0302; 2 IS 0303; 3 IS 0304; 4 HD; 5 IS 0306; 6 IS 0305; 7 IS 0307; 8 IS 0308; 9 ST; 10 EI; 11 HD | CH02A.txt:3377-3395 |
| CE | 1 ST(20); 2 ST(199); 3 ID 0396; 4 ST(20); 5 ST(199); 6 ID 0396. Si el campo tiene tabla (TBL#) se comprueba CE.1 contra ella con la gravedad de C5 | CH02A.txt:309-316 |
| EI | 1 ST(199); 2 IS 0363; 3 ST(199); 4 ID 0301; C: EI.3 y EI.4 van juntos | CH02A.txt:1886-1893 |
| MSG | 1 ID 0076 R; 2 ID 0003 R; 3 ID 0354 R; y MSG.3 tiene que ser la estructura que 0354 da para MSG.2 (`T0354` de `estructuras_hl7`) | CH02A.txt:2804-2811 |
| PT | 1 ID 0103; 2 ID 0207 | CH02A.txt:3892-3897 |
| VID | 1 ID 0104; 2 CE; 3 CE | CH02A.txt:5550-5557 |
| XON | 1 ST(50); 2 IS 0204; 3 NM; 4 NM; 5 ID 0061; 6 HD; 7 ID 0203; 8 HD; 9 ID 0465; 10 ST | CH02A.txt:6026 y siguientes |
| DLD | 1 IS 0113 R; 2 TS | CH02A.txt:1557-1563 |

Tipos de HL7 y de usuario que entran en juego (según `TABLAS-TIPO-IV.json`): de HL7 → 0003, 0061, 0076, 0085, 0103, 0104, 0125,
0136, 0190, 0200, 0201, 0202, 0203, 0207, 0287, 0301, 0354, 0396, 0399, 0444, 0465, 0529; de usuario → 0001, 0002, 0004, 0007, 0010,
0018, 0023, 0050, 0051, 0052, 0053, 0055, 0062, 0063, 0069, 0072, 0088, 0089, 0112, 0113, 0127, 0128, 0189, 0289, 0300, 0302-0308,
0334, 0360, 0361, 0362, 0363, 0443. (0203 figura «con conflicto» en el texto; el Apéndice A la da como de HL7: se trata como de
HL7.)

### 6.2 Qué cuenta como error y qué como aviso

- **Error**: formato de NM, SI, DT, DTM, TS roto; valor fuera de una tabla de HL7 (ID, CE.3, MSG, PT, VID, XPN.7/8, XTN.2/3, CX.5,
  XAD.6/7, HD.3, EI.4); más componentes de los definidos; longitud de campo > LEN; carácter fuera de ASCII; MSG.3 incoherente con
  MSG.2; campo R ausente (si se activa la capa de obligatorios con `CAMPOS[...]["opt"] == "R"`; por omisión activa, para que el
  control positivo de §6.3 cubra los «obligatorios vacíos» del encargo).
- **Aviso**: valor fuera del conjunto sugerido de una tabla de usuario; componente retirado valorado; longitud de componente >
  LEN de componente (P8); `""` en campo R (P3); minúscula donde la tabla solo tiene mayúsculas se trata como «fuera de tabla» (no
  hay comparación insensible a mayúsculas: los valores de tabla son literales).
- **Nada**: tabla de usuario sin valores sugeridos; segmentos Z; campos sin tipo conocido.

### 6.3 Control del instrumento antes de usarlo

**Control positivo en la versión 1** (tiene que encontrar, con el lugar exacto):

| hallazgo esperado | regla | dónde |
|---|---|---|
| GT1-2: CX.2 `LAST` pasa ST(1); CX.7 `L` no es DT | C3 (aviso), DT (error) | `completo`, `opcionales` con GT1 |
| UB1-2 `B` no es NM | NM | `completo`, `opcionales` |
| ACC-1 `1` no es DTM | DTM | ídem |
| PV1-37 con 9 componentes (DLD tiene 2) | C1 | A03 `completo` (3 bases) |
| ROL-2, OBX-11, DG1-6, PR1-5 ausentes | R ausente | `completo`, `opcionales` |
| NK1-1, AL1-1, DG1-1, GT1-1, GT1-3, OBX-3, ROL-4 ausentes | R ausente | `nulos` |
| EVN-4 `00`, PL.6 `A`, PV1-14 `A`, NK1-3 `SPOUSE`, AL1-4 `MODERATE`, ROL-3 `IN` fuera de los sugeridos | C5 usuario | aviso, familias correspondientes |
| XTN.1 valorado en PID-13, NK1-5 | C6 | aviso |
| `UCUM` fuera de 0396 | CE.3 | los 39 gemelos de origen |
| MSH-12 `2.5.1` fuera de 0104 | VID | A1 `escapes_251` |
| PID-8 `f X Z`, PV1-2 `o X Z` | C5 usuario | A1, aviso |
| PV1-2 vacío | R ausente | A1 `pv12vacio` |
| `María` fuera de ASCII | C4 | A1 `contactos` |
| XPN.8 `D` fuera de 0465 | ID | `cap3-36` |
| HD.1 de 26 caracteres | C3 | `cap3-37`, aviso |

Y **no** tiene que encontrar nada (ni error ni aviso) en lo que el estándar admite: por ejemplo, PR1-2 `PR1` (tabla de usuario sin
valores) y GT1-3 con una dirección (todo ST). Esas dos limitaciones se dejan escritas: el comprobador mide tipo y tabla, no
sentido.

**Control negativo**: las 144 bases de las seis familias sin cambios tienen que dar cero errores (solo los dos avisos de §1.5), y
la versión 2 entera cero errores y cero avisos salvo los «a propósito» de la lista del corpus (§7) y los avisos conocidos que
P1/P8 dejen.

**Mutantes**: cada regla tiene un mutante que debe cazar (`debe`) y, por regla, un mutante válido que no debe cazar (`no_debe`).
Todos derivan de la base `A01-001` (`minimo`) de la versión 2 cambiando un solo campo; se guardan en `ga/mutantes_tipos.json`
con `regla`, `campo`, `valor`, `esperado`.

| regla | mutante `debe` | mutante `no_debe` |
|---|---|---|
| NM | UB1-2 = `B` (añadido a la base) | UB1-2 = `-1.5`; `0` |
| SI | PID-1 = `A`; `12345`; `-1` | PID-1 = `1`; `9999`; `0` |
| DT | GT1-13 = `2024-01-01`; `202413` | GT1-13 = `2024`; `202401`; `20240131` |
| DTM/TS | PID-7 = `1`; `2024010112`+`60` (minuto 60); `20240101+01` | PID-7 = `2024`; `20240101120000.1234-0500`; `202401011200` |
| ID tabla HL7 | MSH-11 = `Q`; OBX-11 = `Z`; PID-30 = `S` | MSH-11 = `T`; OBX-11 = `X`; PID-30 = `Y` |
| IS tabla usuario con sugeridos | PV1-2 = `Z` → aviso | PV1-2 = `E`; PV1-18 = `ZZ` (0018 sin sugeridos: nada) |
| C1 componentes de más | PV1-37 = `A^B^C`; PID-8 = `M^F` | PV1-37 = `HOME^20240101` |
| C2 longitud de campo | MSH-10 de 21 caracteres; PID-2 de 21 | MSH-10 de 20; PID-2 de 20 |
| C3 longitud de componente | MSH-3 HD.1 de 21 caracteres → aviso | MSH-3 de 20 |
| C4 ASCII | PID-5 = `GARCÍA^JUAN` → error; PID-5 = `GAR\Q\CIA` → error | PID-5 = `GAR\F\CIA\S\^JUAN\T\`; `\E\`, `\R\` |
| C5 CE.3 | OBX-6 = `mL^mL^UCUM` (añadiendo OBX) | OBX-6 = `mL^mL^ISO+`; `mL^mL^99LAB`; `x^y^HL70063`; `x^y^L` |
| CE.1 contra tabla del campo | NK1-3 = `SPOUSE` → aviso | NK1-3 = `SPO`; `SPO^Spouse^HL70063` |
| MSG | MSH-9 = `ADT^A01^ADT_A02`; `ADT^A01`; `ADT^Z99^ADT_A01` | MSH-9 = `ADT^A04^ADT_A01` |
| CX | PID-3 = `P1^LAST^^GENADT^MR` (CX.2); `P1^^^GENADT^ZZ` (CX.5); `P1^^^GENADT^MR^^L` (CX.7) | PID-3 = `P1^4^M11^GENADT^MR^^20240101` |
| XPN | PID-5 = `A^B^^^^^Q` (XPN.7); `A^B^^^^^^D` (XPN.8) | PID-5 = `A^B^^^^^L^A`; `de&la&Fuente^Ana` |
| XTN | PID-13 = `1^XXX^PH`; `1^PRN^XX`; `^PRN^PH^^34^91^abc` (NM) | PID-13 = `^PRN^PH^^34^91^5551234`; `^NET^Internet^a@b.c` |
| XAD | PID-11 = `S^^C^ST^Z^ES^Q` (0190); `S^^C^ST^Z^ESPAÑA` (C4 y 0399) | PID-11 = `S^^C^ST^Z^ESP^H` |
| HD | MSH-4 = `LAB^1.2^ZZZ` (0301); `LAB^1.2` (HD.3 falta con HD.2) | MSH-4 = `LAB^1.2.3^ISO` |
| EI | ROL-1 = `R1^NS^1.2^ZZ`; TXA-12 (en un MDM) de 31 caracteres | ROL-1 = `R1^NS^1.2^ISO` |
| PL | PV1-3 = `ICU^001^A^HOSP^^A` → aviso (0305) | PV1-3 = `ICU^001^A^HOSP^^N` |
| PT / VID | MSH-11 = `P^Z`; MSH-12 = `2.5.1` | MSH-11 = `P^A`; MSH-12 = `2.5` |
| C6 retirado | PID-13 = `611111111^PRN^PH` → aviso | PID-13 = `^PRN^PH^^^^611111111` |
| C0 nulo | AL1-3 = `""` → `nulo_en_R` (aviso); PID-11 = `""` → nada | — |
| R ausente | quitar PV1-2; quitar OBX-11 de un OBX añadido | OBX con OBX-11 = `F` |

Cada mutante `debe` tiene que producir exactamente el hallazgo esperado en ese campo y ninguno más; cada `no_debe`, ninguno. El
comprobador no se usa sobre el corpus hasta que la tabla entera pasa.

### 6.4 Límites escritos

- No ve sentido: PR1-2 `PR1`, GT1-3 con una dirección, PDA-2 `Y`, PV1-3 con el punto de atención en PL.3 pasan.
- No ve condiciones entre campos salvo las codificadas (OBX-2 con OBX-11, HD.2/HD.3, EI.3/EI.4, MSG.2/MSG.3).
- No ve estructura de mensaje (eso es el validador de IRIS y `estructuras_hl7`).

---

## 7. La lista del corpus v2

Fichero `ga/LISTA-CORPUS-V2.jsonl`, una fila por mensaje, escrito por `generar_corpus` (versión 2) a partir del manifiesto y de las
marcas que cada generador declara. Esquema de la fila:

```
{
 "id":        "A01-004",                         # el id del generador (GENADT, A1, cap3, B36, ORU, VXU) o el del gemelo
 "origen":    "genadt" | "a1" | "cap3" | "cap3-completada" | "oru" | "vxu" | "mdm" | "gemelo" | "muestras" | "minimos" | "propio",
 "version":   2,                                 # versión del corpus a la que pertenece la fila
 "fichero":   "adt/A01-004.hl7",                 # ruta relativa en la carpeta del corpus, como en CASOS.json
 "huella":    "<sha256 del texto normalizado>",  # la misma que en MANIFIESTO.txt
 "evento":    "A01", "familia": "completo",      # cuando el origen los tiene
 "marcas": {
   "a_proposito":        [{"campo": "PV1-2", "que": "vacío", "por_que": "regla que tolera PV1-2 vacío", "cita": "Ch03.txt:5657"}],
   "fragmento_estandar": "Ch03.txt:9094-9095",   # solo cap3: de dónde viene el fragmento
   "copia_completada_de": "cap3-08-A01",         # solo cap3-completada
   "gemelo_de":          "VXU-AU1c",             # solo gemelo; con "campo": "RXA-7" y "de": "UCUM", "a": "ISO+"
   "avisos_conocidos":   [{"campo": "PID-8", "valor": "S", "tabla": "0001"}]   # lo que el comprobador avisa y se acepta
 }
}
```

Marcas «a propósito» que lleva la versión 2 (de §2.2 y del encargo): las 8 bases A1 `pv12vacio` (PV1-2 vacío); `clases` k=4..7
(PID-8 y PV1-2 en minúscula o fuera de tabla); las 8 `escapes_251` (MSH-12 `2.5.1`, PID-8 `Z`, PV1-2 `Z`); los 7 fragmentos
cap3 (estructura incompleta: «fragmento del estándar»); y los avisos de las copias completadas (cap3-36 PID-8 `S`, cap3-37
MSH-4 largo) salvo lo que decidan P5 y P8. Los 39 gemelos llevan `gemelo_de`. Los 7 completados llevan `copia_completada_de`.

Una guarda recorre la lista: toda fila sin marca tiene que dar cero errores y cero avisos en el comprobador (§6) y «válido» en el
validador de IRIS; toda marca tiene que corresponder a un hallazgo real (una marca sin hallazgo es un error de la lista).

---

## 8. Cómo convive la versión 2 con la 1

### 8.1 Ficheros y módulos nuevos (todos en `fase12/ga/`)

| fichero | qué es |
|---|---|
| `ga/gen_adt_v2.py` | copia de `bases_adt/gen_adt.py` con los cambios de §1.6 y nada más; `bases(1)` escribe `ga/bases_adt_v2.json` (216 bases, mismos ids) |
| `ga/bases_adt_v2.json` | las 216 bases v2 |
| `ga/gen_bases_a1_v2.py` → `ga/bases_a1_v2.json` | copia de `a1/gen_bases_a1.py` con `María` → `Maria` (§2.1) |
| `ga/ejemplos_cap3_v2.json` | los 7 fragmentos (idénticos a `a1/ejemplos_cap3.json`) + las 7 copias completadas (§3) |
| `ga/bases_mdm_v2.py` | importa `bases_mdm` (v1) y deriva `BASES` con el TXA-12 de B36 cambiado (§4); su propia `HUELLA`; `cable()` delega en `bases_mdm.cable`. No copia las 40 bases: las deriva, como hace `mev/bases_mdmev.py` |
| `ga/gemelos.py` → `ga/gemelos/*.hl7` + `MANIFIESTO.txt` | deriva los 39 gemelos de los textos de origen cambiando CE.3 (§5); afirma que solo cambia eso |
| `ga/comprobar_tipos.py`, `ga/tipos_v25.json`, `ga/mutantes_tipos.json` | el comprobador (§6), su tabla de componentes con citas y sus mutantes |
| `ga/solo_cambia_esto.py` | la comprobación de §8.4 |
| `ga/LISTA-CORPUS-V2.jsonl` | la lista de §7 |

### 8.2 Cómo elige versión `generar_corpus`

Firma nueva: `generar_corpus(carpeta, lab=True, minimos=True, propios=(), muestras=None, limite=None, version=2)`.

- `version == 1`: el cuerpo actual, sin cambiar una línea (lee `bases_adt/bases_e2.json`, `a1/ejemplos_cap3.json`,
  `a1/bases_a1.json`, `BM.BASES`).
- `version == 2`: `adt` = `ga/bases_adt_v2.json` + `ga/ejemplos_cap3_v2.json` + `ga/bases_a1_v2.json`; `mdm` = `ga.bases_mdm_v2.BASES`;
  `oru` y `vxu` igual que hoy; corpus nuevo `gemelos` = los 39 ficheros de `ga/gemelos/`, con su nombre. La clave `gemelos` se
  añade al final de `CORPUS` para no mover las existentes.
- `CASOS.json` lleva además `"version": 2`; `MANIFIESTO.txt` y las huellas se calculan igual (la huella global y
  `huella_adt_oru_muestras` cambian, como es natural con otro corpus). `LISTA-CORPUS-V2.jsonl` se escribe junto a ellos.
- Por omisión, 2. Todo lo que esté sellado y vuelva a llamar a `generar_corpus` tiene que pasar `version=1` explícitamente (P10:
  desde aquí no se pueden ver esos llamadores).

### 8.3 Lo que no debe cambiar ni un byte

`bases_adt/gen_adt.py`, `bases_adt/bases_e2.json`, `bases_adt/e2_comprobacion.json`, `a1/gen_bases_a1.py`, `a1/bases_a1.json`,
`a1/ejemplos_cap3.json`, `bases_mdm.py`, `bases_mdm.jsonl`, `bases_mdm/`, `mev/bases_mdmev.py`, `estructuras_hl7.py`,
`estructuras_25.json`, `iv/tablas_iv.py`, `iv/TABLAS-TIPO-IV.json`, `privado/iv/TABLAS-VALORES-IV.json`, los módulos de ORU y VXU
(`BO`, `BV`) y, en `cv/verificar_conversor.py`, todo salvo la firma y el cuerpo de `generar_corpus` (que conserva el camino de la
versión 1 literal). La guarda de la etapa guarda el sha256 de esa lista antes y lo compara después.

### 8.4 La comprobación «solo cambia esto»

`ga/solo_cambia_esto.py` afirma, y falla si no:

1. GENADT: 216 bases en los dos ficheros, mismos ids, eventos, familias, mismo número y orden de segmentos; el conjunto de
   `(familia, segmento, posición, campo)` distintos está contenido en §1.6; en PV1-3/6/11 solo cambia el componente 6; el
   contador de llamadas al azar coincide (§1.2).
2. A1: 40 bases, idénticas salvo `A1-*-contactos` PID-5, y en él solo `í` → `i`.
3. cap3: los 7 primeros registros idénticos a `a1/ejemplos_cap3.json`; las 7 copias contienen el fragmento como prefijo de
   segmentos (cada segmento del fragmento está, igual o solo prolongado por campos añadidos al final; en cap3-36 además el
   cambio de P5 si se decide).
4. MDM: las 40 bases v2 idénticas a las v1 salvo B36 TXA-12; `mev.derivar` sobre B36 v2 da TXA-13 de 29 caracteres.
5. Gemelos: 39 ficheros; diff por campo con el origen solo en OBX-6/RXA-7 componente 3 (`UCUM` → `ISO+`) y en MSH-10 si P6.
6. Comprobador: la tabla de mutantes entera pasa; el control positivo de §6.3 sobre la versión 1 encuentra cada hallazgo
   esperado; la versión 2 da cero errores fuera de las marcas de la lista.

---

## 9. Preguntas abiertas

Lo que el estándar no decide y tiene que decidir otro. Para cada una, opciones y hechos de los dos lados.

**P1. Valores fuera del conjunto sugerido de una tabla de usuario en familias por lo demás válidas** (EVN-4 `00` en las 216;
PL.6 `A` en PV1-3/6/11 de las 216; PV1-14 `A` en `completo`; también NK1-3, AL1-4, ROL-3 `IN`, que están en las familias que se
arreglan de todas formas).
- Opción A (la del diseño): cambiarlos en la versión 2 a un valor sugerido (`01`, `N`, `1`, `SPO`, `MO`, `FHCP`).
- Opción B: dejarlos y anotarlos como «aviso conocido» en la lista.
- A favor de A: el alcance dice «la tabla de cada campo»; el texto recomienda usar los sugeridos «where applicable»
  (CH02.txt:557); son constantes y no tocan el azar.
- A favor de B: una tabla de usuario «may be redefined locally» (CH02.txt:558-559) y una IS se define como valor de una tabla
  «site-defined» (CH02A.txt:2428-2430): no es inválido; y A toca 216 mensajes (EVN-4, PV1-3) de familias que el validador da por
  válidas, lo que ensancha la lista de §1.6.

**P2. La disposición de PL en PV1-3/6/11** (`^^ICU^001^HOSPITAL^A^B^1^`: punto de atención en PL.3 «bed», centro en PL.5
«location status»).
- Opción A: dejarla (válida por tipo; el diseño la deja).
- Opción B: reescribirla como `ICU^001^^HOSPITAL^^N` en las 216.
- A favor de A: por tipo es válida (CH02A.txt:3377-3395); PV1-3 está en `colocado` de todas las bases y lo que la herramienta
  espera de él no se puede ver desde aquí.
- A favor de B: el ejemplo del estándar pone el punto de atención en PL.1 y el centro en PL.4 (CH02A.txt:3413-3416); un
  conversor razonable lee PL.1 como la unidad.

**P3. `""` en un campo R.**
- Opción A (la del comprobador por omisión): aviso `nulo_en_R`; la versión 2 no lo usa.
- Opción B: error.
- Opción C: nada (es un valor presente).
- A favor de C: «Except where noted, HL7 data fields may take on the null value» (CH02.txt:391) y el ejemplo `DG1|""|""|…` con
  DG1-1 y DG1-6 (R) a nulo (CH02.txt:2051-2062). A favor de B: R = «required» (CH02.txt:464) y un nulo no está en ninguna tabla
  ni cumple ningún formato. Hecho de partida: el validador no marcó los `""` de ROL-3, AL1-3 y DB1-1 en `nulos`.

**P4. DG1-2 y PR1-2 «(B) R».**
- Opción A (la del diseño): valorarlos en la versión 2 (`I9`, `L`) y que el comprobador los trate como B (no exigidos).
- Opción B: tratarlos como R (exigidos) también en el comprobador.
- A favor de A: las definiciones dicen «retained for backward compatibility only» (CH06.txt:1570-1571, 2005-2006) y B es «left in
  for backward compatibility» (CH02.txt:476-478); hecho de partida: el validador no marcó DG1-2 ausente. A favor de B: la columna
  OPT de las dos tablas dice «(B) R» (CH06.txt:1532, 1976) y la nota de 2.5.3.4 manda documentar la optionalidad en la definición,
  que aquí no lo hace.

**P5. XPN.8 `D` en PID-5 del ejemplo veterinario (cap3-36).**
- Opción A (recomendada): en la copia completada, `Jones^Fluffy^^^^^D` (el `D` pasa a XPN.7, tipo de nombre, donde `D` = display
  name existe en 0200, CH02A.txt:6454); el fragmento no se toca.
- Opción B: dejarlo y anotarlo como error conocido de la copia.
- A favor de A: 0465 solo admite `A I P` (CH02A.txt:3761) y el séptimo separador parece un desliz del ejemplo. A favor de B: la
  copia se llama «completada», no «corregida»; cambiar un valor del ejemplo es más que completar.

**P6. MSH-10 de los gemelos.**
- Opción A (recomendada): sufijo `-ISO`.
- Opción B: el mismo MSH-10 que el original.
- A favor de A: MSH-10 «uniquely identifies the message» (CH02.txt:4490-4491); dos ficheros del mismo corpus con el mismo control
  serían un duplicado para cualquier receptor real. A favor de B: el gemelo es «el mismo mensaje con otro sistema de unidades» y
  cuantos menos campos cambien, más limpio es el par; con B la guarda de §5.3 es más estricta.

**P7. El OID de B36.**
- Opción A (la del diseño): `DOC0036^CSSYN^2.999^ISO` (arco de ejemplos de X.660; dato ajeno a v2.5).
- Opción B: `DOC36^CSSYN^2.999.36^ISO` u otro OID corto.
- v2.5 solo exige EI.4 `ISO` con un OID en EI.3 (CH02A.txt:2344) y 30 caracteres en TXA-12 y TXA-13 (CH09.txt:834-835); la
  restricción real es TXA-13 con `-PADRE` (6 caracteres más). Cualquier OID de ≤ 6 caracteres sirve con `DOC0036`.

**P8. Longitud de componente (p. ej. HD.1 de 26 caracteres en MSH-4 de cap3-37; CX.2 `LAST`).**
- Opción A (la del comprobador): aviso.
- Opción B: error.
- A favor de B: «For version 2.5 and higher, the optionality, table references, and lengths of data type components are supplied
  in component tables» (CH02.txt:484-485). A favor de A: lo que el texto llama normativo es la longitud del campo
  (CH02.txt:426-427), y la del componente no lleva esa palabra.

**P9. `María` en A1 `contactos`.**
- Opción A (la del diseño): `Maria`.
- Opción B: declarar MSH-18 (`8859/1` o `UNICODE`, tabla 0211) y dejar la tilde.
- A favor de A: la familia no ejercita juegos de caracteres y el resto del laboratorio ya escribe sin tildes (`Begona`,
  `Subcutanea`). A favor de B: el estándar prevé exactamente ese mecanismo (CH02.txt:4593-4607) y un HIS español manda tildes.

**P10. Llamadores sellados de `generar_corpus`.** El valor por omisión pasa a 2; cualquier script sellado que vuelva a generar el
corpus debe pasar `version=1`. Desde este encargo no se pueden leer el resto de `cv/` ni los resultados, así que la lista de
llamadores la tiene que hacer quien ejecute la etapa (`grep -rn "generar_corpus(" fase12`). Alternativa más segura: dejar la
versión 1 por omisión y que la herramienta nueva pase `version=2`; va contra la decisión tomada («la 2 por omisión»), por eso se
deja como pregunta y no como diseño.

**P11. ROL-2: `AD` o `UC`.** 0287 es de HL7 y cualquiera de los dos vale (CH12.txt:1688-1696). `AD` (añadir) encaja en A01/A04;
`UC` («no information to be modified», CH12.txt:1697-1699) encaja en A08/A31. El diseño pone `AD` en todos por simplicidad de la
lista de §1.6; si se prefiere `UC`, cambia una constante.
