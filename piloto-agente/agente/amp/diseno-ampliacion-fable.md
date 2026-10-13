<!-- Modelo: Claude Fable 5.1 (claude-fable-5-1). Fecha: 13-oct-2026. AMP0: diseño de la ampliación del piloto del agente; a ciegas de los resultados por caso del piloto y de los diffs de los commits de cierre; leído solo scratchpad/amp -->

# Diseño de la ampliación del piloto «agente que se apoya en el verificador» (AMP0, 13-oct-2026)

Referencia contra la que se medirá la ampliación. Lo implementa otro (Claude), que declara cada desviación como DV-AMP-n y
fija en git la regla de parada **antes** de medir. Etiquetas: S-AMP (decisión propuesta), Q-AMP (pregunta: a Jev, salvo las de
alcance, que son de Víctor), L-AMP (límite declarado de entrada), DV-AMP (reservada a la implementación). Todo lo que este
diseño no nombra queda **como en el piloto** (`piloto/agente/diseno-agente-fable.md`, en adelante «D-AG», y sus sellos).

Lo que el ANTES da por fijado (13-oct): se amplía el corpus con H de los commits de cierre (pieza común `14e17de` y cabecera
común) y con R de las seis deudas vivas (CIR-ADT-7, CIR-ADT-8, CIR-MS-3, CIR-MS-4, CIR-MT1, CIR-MT4); brazos AG (2 réplicas) y
REF congelada sin tocar; consigna, lanzador, evaluador, puertas por caso y formato de las dos frases como en el piloto; DS solo
si alcanza el saldo (≈ 0,5 USD); tope 1,5 sesiones; si tras las puertas quedan < 4 casos nuevos que cuentan, se para y se
publica «la ampliación no da casos».

Lo que el ANTES obliga a resolver aquí, y dónde: (1) el análisis con n ampliado tras ver p = 0,22 → §3; (2) las puertas de los
casos nuevos (regresión sin aceptados, firma no estable, pistas textuales) → §1.4; (3) la caja LABMULTI → §2; (4) coste y reglas
de parada en números → §4.

---

## 0. La pregunta no cambia; cambia el estudio

Las dos frases son las de D-AG §0 y §4.5. La ampliación **no es más piloto**: es una segunda etapa con diseño propio, cuyo n se
decidió después de ver el p de la primera. Eso tiene una consecuencia estadística (§3) y una de honestidad: la frase 2 de la
ampliación se publica siempre con tres números al lado (el del piloto, el de los casos nuevos solos y el combinado), y esta es
**la última etapa**: no habrá una tercera ampliación decida lo que decida el resultado (S-AMP-9).

Vocabulario nuevo:

| Término | Significado |
|---|---|
| **etapa 1** | El piloto (AG2/AG3): 11 casos H + R sellados el 12-oct, resultados fijos; no se remide nada |
| **etapa 2** | La ampliación: los casos nuevos que pasen las puertas de AMP1 (n₂, fijado en el sello) |
| **combinado** | El estadístico que junta las dos etapas con pesos fijados antes de medir la etapa 2 (§3.2) |
| **deuda por decisión** | Un fallo que el juez cuenta pero que el circuito hace adrede por una decisión declarada (S97, S98, el contrato de LABMULTI, L-MT1); se mide igual, se reporta aparte (§1.3, §5) |
| **grupo de disparadores** | Dentro de un caso, un subconjunto construido con la misma receta (como R3/R3b); FIX exige el 100 % de todos los grupos |

---

## 1. Los casos nuevos, uno a uno, como plantilla

### 1.1 Regla previa: un fallo cuenta una vez en todo el estudio (S-AMP-1)

Los commits de cierre arreglaron fallos que **ya estaban en el corpus del piloto** con otro nombre: la pieza común `14e17de`
cerró CIR-MT3 / CIR-ADT-6 / CIR-ORU-2 (el `SINID` inventado), que es el **R6** del piloto en el congelado, y CIR-MT2 / CIR-ORU-1
(`Validate "dm"` que rechaza Z y opcionales fuera de sitio), que es el mutante de control **MA11** del piloto. Un mismo defecto en
otra copia del mismo código, resuelto por el mismo modelo, no es una observación independiente para McNemar; contarlo inflaría
la etapa 2 con lo que ya se midió. Regla: **un caso de la etapa 2 no cuenta si su causa (la unidad de la verdad y el hallazgo
del juez) es la de un caso H, R o M de la etapa 1**; se construye igual si es barato y sirve de control (§1.2), pero no entra en
n₂. Es la Q-AMP-1 (alcance: Víctor), porque reduce lo «previsto 1-3» del ANTES a 1-2 H.

Correspondencia preinscrita (la implementación la confirma con los diffs reales en AMP1, y si un hunk cierra algo que **no**
está en esta tabla, ese es un H candidato nuevo y se declara):

| Commit | Fallo que cerró | ¿Ya en la etapa 1? | Destino en AMP |
|---|---|---|---|
| pieza común `14e17de` | CIR-MT2 / CIR-ORU-1: `Validate("dm")` rechazaba segmentos Z, TQ1 y opcionales fuera de sitio | Sí: MA11 (M, LABADTMUT) | **H-COM-MT2, control de cadena** de la caja LABMULTI (§2.4), no cuenta |
| pieza común `14e17de` | CIR-MT3 / CIR-ADT-6 / CIR-ORU-2: MSA-2 «SINID…» con MSH-10 vacío | Sí: R6 (R, LABMUT) | No se construye |
| cabecera común | CIR-MS-1: LABORU rechazaba 2.4 con AR 203 y daba AR 203 a MSH-12 vacío (AMB-2: AR 101) | No | **H-CAB-1** (cuenta) |
| cabecera común | CIR-MS-1b: LABORU no juzgaba MSH-11 (P2c) | No | Se **funde con H-CAB-1** si comparte unidad de verdad (S-AMP-2); si no, H-CAB-1b aparte |
| cabecera común | CIR-MS-2: la última red de FhirAdt / FhirResultados contestaba AE 207 (S29: AR) | No (M10 es «207 por 200», otro fallo) | **H-CAB-2**, candidato con entorno inyectado; prevista su retirada por falta de disparador reproducible |

**S-AMP-2. Fusión por unidad de verdad.** Dos candidatos cuya verdad (unidades de los hunks, §1.2) es el mismo conjunto, o uno
contiene al otro, son **un caso** con grupos de disparadores (como R3 + R3b): FIX exige el 100 % en todos los grupos; LOC3 se
puntúa contra la unión. Evita contar dos veces la misma línea arreglada con dos mensajes distintos.

### 1.2 H desde los commits de cierre: aislamiento por hunks (plantilla)

No conozco los diffs. La plantilla fija el **cómo**; los números se rellenan en AMP1 sin que yo intervenga.

| Campo de la clave | Cómo se obtiene | Regla |
|---|---|---|
| `commit_arreglo` | El commit de cierre (`14e17de`; el de la cabecera común, identificado por su mensaje) | Si el cierre se repartió en varios commits consecutivos sin medida entre ellos, el «arreglo» es el rango y el «antes» es el padre del primero (como D-AG §1.2) |
| `hunks_del_fallo` | Del diff `padre → commit`, restringido a ficheros del circuito (sin tests ni documentación), **los hunks que cierran ese fallo y solo ese** (DV-AG-2): la implementación los elige leyendo el diff y escribe en la clave, por hunk, por qué pertenece al fallo | Un hunk que cierra dos fallos de la tabla de §1.1 pertenece a los dos; dos candidatos con los mismos hunks se funden (S-AMP-2) |
| `arbol_antes` | `exportar(padre, circuito + comun)` en la revisión padre: el circuito **con la copia de la pieza común que tenía entonces** | Es lo que ve el agente. La caja es la del circuito donde se observó el fallo: H-CAB-1 en LABORUMUT; H-CAB-2 en LABORUMUT (o LABADTMUT si el disparador solo se reproduce allí); H-COM-MT2 en LABMULTIMUT |
| `arbol_despues` | `arbol_antes` con **solo** `hunks_del_fallo` aplicados (no el commit entero) | Solo para construir la clave y el brazo FIX; nunca entra en la caja. Tiene que compilar en la caja; si no compila aislado, el aislamiento es incompleto y el caso se retira (declarado) |
| `verdad` | Por hunk: fichero y líneas **del árbol antes** quitadas o modificadas; para un hunk de pura inserción, la línea del árbol antes anterior al punto de inserción. **Un fichero nuevo en el diff no aporta verdad** (no existe en el árbol antes); la verdad de un cierre que añade una clase nueva son las líneas del punto de llamada que cambian. Si tras esta regla la verdad queda vacía, el caso no es localizable y se retira (declarado) | De cada línea se deriva su unidad (`unidades.py`, congelado) |
| `disparadores` | `D(H) = {m : antes(m) ≠ correcto ∧ despues(m) = correcto}` sobre el banco del circuito (bases reales y construidas, incluidas las de las campañas MS). **Si el banco da < 3, se construyen** (S-AMP-3): funciones de construcción escritas en AMP1 sobre basales aceptados, con la misma receta que los R, y la puerta sigue siendo la misma (fallan antes, pasan después). Mínimo 3; máximo 25 por orden sembrado (`AMP1\|H-n`) | H-CAB-1 previsible: ORU con MSH-12 = 2.4; con MSH-12 vacío; con MSH-11 vacío; con MSH-11 fuera de 0103. Los grupos se declaran |
| `regresion` | `R(H) = {m : antes(m) = correcto ∧ despues(m) = correcto}`, hasta 60, estratificada, **con la regla de aceptados de §1.4** | |
| `excluidos` | No `correcto` con ninguno de los dos árboles (otros fallos vivos de esa revisión) | Se listan; no son disparador ni regresión |
| `categoria_prevista` | Por definición con la leyenda, antes de medir | H-CAB-1: `acuse_incorrecto` (falso rechazo 203 donde S19 acepta; código 203 donde AMB-2 pide 101; `fallo_silencioso` para el MSH-11 no juzgado). H-CAB-2: `acuse_incorrecto`/codigo (AE donde S29 pide AR) |
| `caso_mostrado` | El primer disparador por orden sembrado | Como en el piloto |

**S-AMP-3. Disparadores construidos también para H, declarados.** El piloto retiró H-COM-1 y H-COM-2 con 0 disparadores: la
puerta «falla antes» dependía de que el banco tuviera el mensaje justo. Para un cierre de cabecera (versión, processing id) el
banco puede no tener nada; construirlos no cambia la verdad (que es el diff) y la puerta FIX sigue probando que el arreglo real
los arregla sin colateral. La construcción se escribe **antes** de mirar el diff del otro commit y se guarda en la clave.
Alternativa: solo banco, como en el piloto; el coste es perder H-CAB-1 por una razón de corpus, no de agente.

Las **tres puertas** de D-AG §1.2 se mantienen tal cual (falla antes ≥ 3; FIX = 100 % y 0 colateral; VACÍO = 0 y aparato
estable), con dos añadidos:

4. **Aislamiento compila:** `arbol_despues` (solo los hunks del fallo) compila y arranca en la caja.
5. **Sin pista del arreglo en el árbol antes:** se busca en `arbol_antes` el texto de cada línea nueva del hunk (sin blancos); si
   alguna ya aparece (p. ej. en un comentario que anticipa el cambio), se lista como pista de código (§1.4.3). No retira el caso.

H-CAB-2 (CIR-MS-2) tiene una condición más: su disparador exige llegar a «la última red» (un error no previsto en la operación),
y eso solo se puede provocar con entorno inyectado en la copia cargada (DV-AG-3: puerto cerrado, credencial vacía, ruta
inexistente) o con una respuesta de FHIR inesperada. La implementación prueba las tres inyecciones de `ag1_r.py` sobre
`arbol_antes`; si ninguna produce AE 207 donde `arbol_despues` produce AR 207 en ≥ 3 mensajes, **se retira y se declara**
(«H-CAB-2: sin disparador reproducible»). No se busca ninguna otra forma de provocarlo.

**H-COM-MT2 como control (no cuenta).** Se aísla igual (hunks de `14e17de` que sustituyen `Validate("dm")` por
`Lab.HL7.Comun.Estructura.Validar` en `Lab.HL7.Multi.Operation.Acuse` y el fichero nuevo `Lab.HL7.Comun.Estructura.cls`), en
LABMULTIMUT, con disparadores construidos (un mensaje válido de cada punto más un segmento `ZXX` al final → antes AE 100, después
AA). Sirve para dos cosas: el **brazo FIX de la caja nueva** (§2.4) y la prueba de que el aislamiento por hunks funciona cuando el
diff añade una clase. Si no cabe en el tope de AMP1, el control FIX de la caja es el parche del implementador para R-MT1 (§2.4).

### 1.3 R desde las deudas vivas (plantilla, 6 filas, 4-6 que pueden contar)

Todas salen de `deudas_circuito_*` de `info_verificador.json`, que el agente **no ve** (gen_cajas las quita). Los disparadores se
construyen sobre basales aceptados del circuito (los de A1/A4 para LABADT, O4/Q1 para LABORU, `multi.valido(pe, …)` para
LABMULTI); la regresión sigue §1.4.1. Como en el piloto, para R no hay diff: la clave de localización es una **zona preinscrita**
(la escribe el implementador en AMP1 antes de cualquier tirada; mi lectura a ciegas va abajo como control; la sellada es la unión
si difieren) y el arreglo aceptado es el del verificador sin colateral.

| Caso | Deuda | Caja / PE | Disparadores (construcción; n) | Categoría prevista por definición | Zona preinscrita (mi lectura a ciegas) | ¿Código, entorno o perfil? | Cuenta |
|---|---|---|---|---|---|---|---|
| **R-ADT-7** | LABADT acusa siempre, también con MSH-15/16 = NE | LABADTMUT / `adt_fhir` | 5 basales A01 aceptados con `MSH-15 = NE` y `MSH-16 = NE`; 3 A08 igual (grupo b) | `acuse_incorrecto` / recuento-existencia (hay ACK donde no debe haberlo) | `Lab.HL7.Adt.Production.cls` Item `AdtFhirIn` (Setting `AckMode`); `Lab.HL7.Comun.Servicio.OnInit` | **Código y perfil a la vez**: en el perfil lab es fallo; el del sitio pide ACK siempre (H1). El arreglo natural es un Setting (`AckMode` App → Msh) o código en el servicio; el evaluador lo admite (no es puerto ni credencial) | **Con reserva (eslabón débil, §1.3.1)**: solo si el juez da `correcto` a «sin ACK con NE/NE» |
| **R-ADT-8** | El servicio decodifica como UTF-8: un cable latin-1 con MSH-18 vacío guarda las letras estropeadas | LABADTMUT / `adt_fhir` | 5 basales A01/A08 aceptados con PID-5.1 y PID-5.2 en **bytes latin-1** (p. ej. `NÚÑEZ^JOSÉ` codificado en ISO-8859-1) y MSH-18 vacío; 3 iguales con PID-11 (grupo b) | `fallo_silencioso` / fidelidad-guardado (S9) | `Lab.HL7.Comun.Servicio.OnInit`; `Lab.HL7.Comun.Mandos.Omision` (`JuegoPorOmision`); `Lab.HL7.Adt.Production.cls` Item `AdtFhirIn` (`DefCharEncoding`) | **Deuda por decisión** (S97: «UTF-8 en lab, CIR-ADT-8 sigue»). El arreglo conforme a S9/S38 exige detectar UTF-8 válido y caer a latin-1 si no: no es un Setting. Previsión: localiza, no arregla | Sí (Q-AMP-10) |
| **R-MS-3** | LABORU contesta AE 103 por un OBR-25 compuesto | LABORUMUT / `oru_fhir` | 5 basales ORU 2.5 aceptados con `OBR-25 = F^Final`; 3 con `OBR-25 = P^Preliminar` (grupo b) | `acuse_incorrecto` / falso rechazo (S46: se trunca a la longitud antes de juzgar la tabla; S3: se acepta truncado) | `Lab.HL7.Msg.OruRequest.MotivoRechazo` (rama 103 y rama 104 por `Truncado`); `Lab.HL7.Oru.Util.Obx.Informe` (lectura de OBR-25, `pTrunc`); `Util.Obx.En0123` / `Estado0123` | Código. Ojo: arreglado el 103, el mismo mensaje cae en el **104** por `Truncado` (L-MS-4): el arreglo aceptado toca dos ramas. Es un caso multisitio de verdad | Sí |
| **R-MS-4** | LABORU contesta AE 101 por OBR-4 sin CE.1 | LABORUMUT / `oru_fhir` | 5 basales ORU 2.5 aceptados con `OBR-4 = ^Hemograma`; 3 con `OBR-4 = ^Hemograma^` (grupo b) | `acuse_incorrecto` / falso rechazo (OBR-4 está valorado; AMB-ORU-4: display sin code) | `Lab.HL7.Msg.OruRequest.MotivoRechazo` (rama 101 `CodigoCode = ""`); `Util.Obx.Informe` / `Util.Obx.Codigo`; `Lab.HL7.Oru.Operation.FhirResultados.CodeableConcept` (coding con display y sin code) | Código. FIX exige además que el almacén releído lleve `coding[1].display` sin `code` (el juez compara el recurso): puede exigir tres sitios | Sí |
| **R-MT1** | LABMULTI no comprueba MSH-12 | LABMULTIMUT / `ord` | 5 ORM^O01 válidos con `MSH-12 = 2.3.1`; 3 ADT^A01 válidos por `adt` con `MSH-12 = 2.3` (grupo b); 3 ORM con **MSH-12 vacío** (grupo c, esperado AR 101 por AMB-2) | `fallo_silencioso` / aceptado-imposible (AA donde S19 pide AR 203; AA donde AMB-2 pide AR 101) | `Lab.HL7.Multi.Operation.Acuse.Decidir` (paso 0, la guarda `ModoSitio()`); `Lab.HL7.Comun.Mandos.ModoSitio` / `Valor`; `Lab.HL7.Comun.Cabecera.Motivo` | **Deuda por decisión** (S98, confianza 0,16): con el interruptor apagado no mira la cabecera. El arreglo que el juez acepta es quitar la guarda (una línea). Los mensajes con MSH-11 fuera de 0103 fallan antes y después de ese arreglo si el parche no los toca: van a `excluidos`, no a la regresión | Sí (Q-AMP-3) |
| **R-MT4** | LABMULTI no valida contenido | LABMULTIMUT / `adt` | 5 ADT^A01 válidos 2.5 con `PID-8 = X` (esperado AE 103); 3 con `PID-7 = 20261332` (grupo b, esperado AE 102). Sin controles C0 (Q-AMP-9) | `fallo_silencioso` / aceptado-imposible | `Lab.HL7.Multi.Operation.Acuse.Decidir` (paso 2) y `ClaveVacia`; `Lab.HL7.Multi.Production.cls` Items `AcuseAdt…` (Setting `Validacion`); `Lab.HL7.Multi.Puntos.Claves` | **Deuda por contrato** (§8.3 del multitipo, L-MT1): «correcto» en LABMULTI prueba acuse de estructura y claves. Es un fallo de **ausencia** (falta la comprobación): la localización por unidad lo admite (Q-AG-11); el arreglo exige dos comprobaciones nuevas con dos códigos distintos | Sí |

Puertas de R en AMP1, como en el piloto: cada caso falla con el árbol base en ≥ 5 de sus disparadores (o en todos si el grupo
tiene menos de 5); la regresión da el 100 % `correcto`; VACÍO = 0 arreglados; firma (o veredicto, §1.4.2) estable entre dos
pasadas. Si la categoría medida difiere de la prevista, se adjudica y se anota; no se corrige la previsión. Lo que la clave
guarda además: la zona sellada, mi lectura de arriba, el grupo de cada disparador, los `excluidos` y el apartado
`decision_declarada` (S97 / S98 / contrato L-MT1 / H1) para las deudas por decisión, que AMP3 usa para la sensibilidad (ix).

#### 1.3.1 El eslabón débil de R-ADT-7: ¿sabe el juez juzgar un silencio correcto?

Un arreglo de R-ADT-7 **no envía ACK**. El verificador declara (L-MT11, S11) que «un ACK que el circuito no envía nunca y uno
perdido en la red son indistinguibles desde el emisor: D0 ausente → `fallo_entorno`». Si eso vale también con MSH-15/16 = NE,
ningún parche puede dar `correcto` y el caso no mide nada del agente: mide al juez. Puerta previa, **en seco y antes de construir
nada más** (probar primero el eslabón débil): con `verificar_caso` sobre dos evidencias construidas a mano, el mismo A01 con
NE/NE, (a) con `ack: null`, conexión establecida y el log de aceptación L13/L16, y (b) con el ACK AA del circuito:

- (a) `correcto` **y** (b) no `correcto` → el caso entra y FIX se mide con el evaluador tal cual (el emisor espera 8 s y la
  evidencia dice «no llegó ACK»); el tiempo de caja sube ~8 s por disparador, aceptable.
- Cualquier otra combinación → R-ADT-7 **se retira como «del juez / del perfil», se declara** (Q-AMP-2) y no se toca el
  verificador para hacerlo entrar (tocar al juez durante el estudio cambiaría la medida de todos los casos).

El evaluador no cambia: FIX = 100 % `correcto` en disparadores, 0 colateral. La regresión de R-ADT-7 lleva, además de lo que
manda §1.4.1, ≥ 5 mensajes con MSH-15/16 = AL/AL (S13: el AA síncrono es perfil aceptable) y ≥ 5 con MSH-15/16 vacíos (modo
original): un parche que silencie todo deja colateral ahí. Prevision escrita: el Setting `AckMode = Msh` de IRIS podría tratar
los vacíos como «sin acuse»; si es así, FIX = 0 con colateral, y es una medida legítima del arreglo, no del aparato.

#### 1.3.2 Bytes crudos en R-ADT-8

El disparador es el cable **tal cual** (bytes ISO-8859-1 en PID-5, MSH-18 vacío). Control del aparato, antes del sello: la
evidencia del caso mostrado tiene que llevar los bytes marcados `<0xD1>` / `<0xC9>` en `mensaje` (adjudicacion.cable) y el
canónico observado las letras estropeadas; si el arnés normaliza el cable a UTF-8 por el camino (`lab.mllp`, `observar`), el
disparador se destruye en silencio y el caso daría `correcto`: se ve en la puerta «falla antes» (0 de 5) y se arregla el arnés,
no el caso. La regresión lleva ≥ 5 mensajes UTF-8 multibyte válido con MSH-18 vacío (S38: se leen como UTF-8) y ≥ 3 con
`MSH-18 = 8859/1` y bytes latin-1 (un MSH-18 valorado manda): un parche «latin-1 por omisión» deja colateral en los primeros.

### 1.4 Lo que se aprendió en el piloto, convertido en reglas

#### 1.4.1 Regresión con aceptados y con rechazos correctos (L-AG-14, L-AG-16)

Cuatro M del piloto tenían regresión vacía y en otro el daño al AA no tenía dónde verse. Regla numérica para **todo caso nuevo**:
la regresión sellada contiene **≥ 10 mensajes `correcto` con AA** y **≥ 5 mensajes `correcto` con un rechazo esperado** (AE o AR
que el juez da por bueno: tipo ajeno AR 200, evento no aceptado AR 201, PID-3 vacío AE 101…), además de los estratos de siempre
(hasta 60, sembrados). Un caso cuya regresión no llega a esos dos mínimos **no se sella** hasta tenerlos (se construyen; es
barato), y si no se pueden construir se retira y se declara. Así el daño en las dos direcciones (romper el AA; aceptar lo que se
rechazaba) deja colateral, y el DAÑINO-B de §2.4 lo comprueba en la caja nueva. Para R-MT1 y R-MT4 la regresión lleva, además,
los **vecinos del borde** del arreglo esperado: versiones aceptadas (2.4, 2.5, 2.5.1, 2.6), `PID-8` en `f` minúscula (S4:
tolerancia), `PID-7` con precisión reducida (`1990`, `199001`) y un `PID-8 = X` en un mensaje 2.5.1 (S22: tolerado; S26: AE 103
también aceptable, así que no es trampa, pero está).

#### 1.4.2 Firma no estable (DV-AG-16): decidido antes, por caja, con medida

En ADT la firma de un mismo mensaje cambia entre dos medidas del árbol base. Para **cada caja que se use en AMP** (LABADTMUT,
LABORUMUT, LABMULTIMUT) se mide antes del sello: el árbol base se carga dos veces y se envían los 5 fijos de la regresión (en
LABMULTIMUT, el `valido(pe)` de cada punto). Si las 5 firmas coinciden en las dos pasadas, la restauración se juzga por **firma**;
si no, por **veredicto** (DV-AG-16), y se escribe en el sello cuál es la regla de cada caja. No se decide sobre la marcha.

#### 1.4.3 Pistas textuales: lista preinscrita, comprobación de fugas y sensibilidades

El agente ve `verificador.json` (la copia sin `desviaciones_*` ni `deudas_circuito_*`) y el árbol. Leyendo la copia de esta
carpeta y los árboles actuales, **estas son las pistas que ya sé que existen** (la implementación confirma líneas sobre el
árbol exportado y no añade nada después del sello):

| Caso | En `verificador.json` (lo recibe solo el que lo lee: AG y DS; REF no lo usa) | En el código del árbol (lo ven los tres brazos) |
|---|---|---|
| R-ADT-7 | **L-MS-1**: «CIR-ADT-7 no se salda: los servicios acusan aunque MSH-15/16 pidan NE» (es el diagnóstico literal); L-MT11 | Comentario de `Lab.HL7.Adt.Production.cls` sobre `AckMode App` |
| R-ADT-8 | **S97**: «juego por omisión UTF-8 en lab (CIR-ADT-8 sigue en lab)»; S9, S38 (describen el comportamiento esperado, no el circuito); L-MS-10 | Cabecera de `Lab.HL7.Comun.Servicio.cls` («S97: UTF8 en lab») |
| R-MS-3 | S46 (truncar antes de juzgar la tabla), S3; L-MS-4 (el 104 de LABORU «queda como estaba») | — |
| R-MS-4 | AMB-ORU-4 («CE ^texto sin código») | `Lab.HL7.Msg.OruInforme.cls`: «OBR-4.1 … Vacio -> AE 101» |
| R-MT1 | **S98**: «LABMULTI juzga la cabecera solo con el modo sitio; con el interruptor apagado sigue CIR-MT1» (nombra la deuda y la causa) | `Lab.HL7.Multi.Operation.Acuse.cls` paso 0: «(S98; CIR-MT1 sigue)»; `Lab.HL7.Multi.Rule.Ord.cls`: «el circuito no mira MSH-12, y lo que el verificador diga de eso (S19) es hallazgo, no arreglo» |
| R-MT4 | L-MT1 («correcto prueba acuse, no procesamiento») | Cabecera de `Lab.HL7.Multi.Operation.Acuse.cls`: «el circuito valida estructura y no contenido, y ESO es su contrato» |
| H-CAB-1 | S19, AMB-2 (comportamiento esperado) | En el árbol **antes** no están los comentarios que hoy nombran CIR-MS-1/1b en `OruRequest.MotivoRechazo` (se comprueba) |

Dos de las pistas de `verificador.json` (L-MS-1, S98) y dos comentarios del código (Acuse paso 0, Rule.Ord) **nombran la deuda
por su id o describen su causa**. Decisión (S-AMP-4): `verificador.json` se mantiene **byte a byte idéntico** al del piloto (su
sha256 va en el sello) por tres razones: es lo que el juez declara y un ingeniero de guardia también lo tendría; las dos etapas
tienen que ser comparables; recortar ahora, con el corpus conocido, sería diseñar la caja mirando los casos. Los comentarios del
código tampoco se tocan (D-AG §6.1: es una condición real). A cambio: (a) se listan aquí y en el sello; (b) se añaden dos
sensibilidades a §3.4: **(iii-amp)** sin los casos con pista en `verificador.json` (R-ADT-7, R-ADT-8, R-MT1, R-MT4, más R4 y R6
del piloto) y **(viii)** sin los casos con comentario en el código que nombre la deuda o su causa (R-MT1, R-MT4); (c) L-AMP-2.
Es la Q-AMP-4 (Jev), con la alternativa de recortar solo los cuatro paréntesis que nombran `CIR-*`.

**Comprobación de fugas por otra vía (obligatoria, en AMP1, resultado en el sello).** Sobre **cada caja generada** (todos los
ficheros: `caso.json`, `verificador.json`, `fuente/*`, `CONSIGNA.md`) se pasa un escáner con estas expresiones, y cada
coincidencia se lista con la decisión (pista declarada / retirada / fuga corregida):
`CIR-[A-Z]+-?\d`, `deuda`, `DV-(AG|AMP|MS|MT|ADT|ORU)`, `AG[0-9]`, `AMP[0-9]`, `piloto`, `mutante`, `labmut|LABMUT|LABADTMUT|LABORUMUT|LABMULTIMUT`,
`privado`, los ids de caso (`R-ADT-7`, `H-CAB-1`…), los sufijos de construcción (`/ne`, `/latin1`, `/obr25`…) y el MSH-10 original
de cada disparador (tiene que estar opacado en toda la evidencia, también dentro de los textos de log y del almacén releído).
Un nombre de namespace de caja dentro de `fuente/` (p. ej. en un comentario de la producción) es una fuga y se corrige en el
exportador, no a mano.

#### 1.4.4 Un limpio nuevo (L-multi)

Para la caja nueva hace falta su control negativo: **L-multi**, un ORM^O01 válido 2.5 por el punto `ord`, veredicto `correcto`,
misma consigna. 2 réplicas AG, 1 REF, DS si alcanza. Falsa alarma como en D-AG §2.3. Los tres limpios del piloto no se repiten.

### 1.5 El sellado

Como D-AG §1.7, con estos cambios de nombre para que nada de la etapa 2 colisione con la 1: clave en
`privado/agente/amp1/amp_clave.json`; sello en `etapa/SELLO-AMP.md`, commiteado antes de la primera tirada de cualquier brazo;
cajas en `caja/<8 hex de sha256("AMP1|" + id + "|" + réplica)>/` bajo la carpeta de cajas del agente, fuera del repositorio; ids de mensaje opacados con semilla
`AMP1` (`gen_cajas.opacar`); orden de tiradas sembrado con `AMP2|<huella de amp_clave>`. El sello lleva: la tabla de casos que
cuentan y los retirados con motivo; **n₂**; la regla de restauración por caja (§1.4.2); la lista de pistas (§1.4.3) y el
resultado del escáner; los controles del evaluador por caja (§2.4); la huella del verificador usado en las puertas (si no es la
del piloto, se declara y se lista el diff de `version.ficheros`); los sha256 de todo lo congelado que **no cambia** (ref.py,
unidades.py, CONSIGNA_AG1.md, lanzar_agente.py, mcp_verificador_agente.json, ag1_eval.py, gen_cajas.py, verificador.json) y de lo
nuevo (el exportador y evaluador de LABMULTI, las construcciones de disparadores, el guion de análisis `amp3.py`); la regla de
decisión de §3 **con Z₁ y los pesos ya escritos**; y las reglas de parada de §4.

---

## 2. La caja LABMULTI

### 2.1 Qué es y qué no es

LABMULTI es un circuito **sin destino**: cinco servicios MLLP (adt 2580, oru 2581, siu 2582, ord 2583, mdm 2584) que solo
acusan; sin FHIR, sin credencial, sin canónico, sin tabla del sexo (L-MT1). Eso simplifica la caja (nada que limpiar, ningún
almacén que compartir) y la hace distinta: FIX se decide **solo por el acuse**, y eso se dice al reportar FIX por caja (L-AMP-4).

**S-AMP-5. Caja `LABMULTIMUT`**, namespace aparte con la receta de `ag1_cajas.crear_caja` (base de datos propia, interoperabilidad
habilitada; **sin** paso de credencial), puertos **2590-2594** (adt 2590, oru 2591, siu 2592, ord 2593, mdm 2594), alcanzados
por la IP del contenedor como los 2580-2584 (no hay que publicar nada ni reiniciar el contenedor). Puertos distintos de los de
LABMULTI aunque las dos producciones nunca estén en marcha a la vez: un puerto que se queda cogido fue la trampa medida en Mirth y
no hace falta correr el riesgo. Libres hoy: 2575 USER, 2576 LABMUT, 2580-84 LABMULTI, 2585 LABORU, 2586 LABADT, 2595 LABORUMUT,
2596 LABADTMUT.

### 2.2 Exportación del árbol (el mismo exportador, una entrada más)

`CAJAS["multi"] = {ns: "LABMULTIMUT", dir: "multi/fuente", prod: "Lab.HL7.Multi.Production", puertos: {2580: 2590, 2581: 2591,
2582: 2592, 2583: 2593, 2584: 2594}}`. `exportar(rev, "multi", destino)` saca `multi/fuente` de la revisión con `git archive`
(nunca del directorio de trabajo), normaliza `\r\n`, y sustituye los cinco puertos **con límite de palabra** (la expresión `258[0-4]` sin otra cifra delante ni detrás)
en **dos** ficheros, y solo en esos: `Lab.HL7.Multi.Production.cls` (Settings `Port`, los `Comment` «escucha MLLP en el 2580» y
la `Description`) y `Lab.HL7.Multi.Puntos.cls` (`ClassMethod Puerto` y el comentario «2580-2584»). Así el árbol de la caja es
coherente consigo mismo (la producción y el vocabulario dicen lo mismo), igual para todos los casos y brazos: no lleva
información. Se registra el hash del árbol y el sha256 de cada fichero tras la sustitución, y el sello lista los dos ficheros
tocados. Las clases comunes (`Lab.HL7.Comun.*`, `Util.Ack`, `Multi.Operation.Rechazo`, `Multi.Puntos`) van en `multi/fuente`
como copias, igual que en LABADT/LABORU: el árbol exportado es completo.

### 2.3 Medir en la caja: una producción a la vez, un punto por mensaje

- `TODOS_NS` del arnés pasa a incluir `LABMULTIMUT`; `a_caja("multi")` para todo lo demás (USER, LABMUT, el privado, LABMULTI,
  LABORU, LABADT, LABADTMUT, LABORUMUT), arranca `Lab.HL7.Multi.Production` en LABMULTIMUT y comprueba estado 1; `a_user()` en
  `finally` lo devuelve todo (USER en marcha, huella del congelado y sonda AA), como hoy.
- Los mensajes de un caso LABMULTI llevan punto: `[(id, bytes, pe)]`. `medir("multi", …)` usa la mecánica de `multi.py`
  (`apuntar(pe)`: `lab.uno/consulta` al namespace de la caja, `lab.mllp` a la IP y al puerto **de la caja** del punto,
  `_sesion_nueva` por el servicio del punto, `observar` sin limpieza y con `SISTEMA_SIN_ALMACEN`), parametrizada por namespace y
  mapa de puertos (hoy `multi.py` lleva `NS` y `PUNTOS` fijos: se añaden a `ACTUAL`, sin anidar parches). La evidencia lleva
  `punto_entrada = pe`; el verificador lo lee del bundle. `comparar_canonico` devuelve `isError` para estos puntos: REF sigue
  sin esa sonda (D-AG §3.3) y el agente recibe el mismo error; es igual para los dos.
- **Modo lab garantizado:** antes de cada medida se comprueba en la caja `##class(Lab.HL7.Comun.Mandos).ModoSitio() = 0` y que no
  hay filas de System Default Settings para el item `Perfil` en LABMULTIMUT (`comun.py modo` nunca apunta a la caja). Si hay,
  se borran y se declara. Con el modo sitio encendido R-MT1 desaparece y la regresión cambia: es la fuga más fácil de esta caja.
- `cargar("multi", carpeta)` como hoy: para la producción, borra las clases `Lab.*` que sobren, `LoadDir` con compilación, y
  comprueba que cada clase del árbol existe compilada. Sin `Storage` persistente propio (no hay canónico), el punto 7 de D-AG
  pesa menos; la regla de recarga completa se mantiene igual.

### 2.4 Evaluación, restauración y controles de la caja nueva

El evaluador es `ag1_eval.evaluar` sin cambios de regla (aplica, compila, 100 % disparadores, 0 colateral; PROHIBIDO igual:
`Port`, credenciales, rutas), con `circ = "multi"` y los mensajes con punto. Restauración: recarga del árbol base completo y 5
fijos (uno por punto, los `valido(pe)`), por firma o por veredicto según §1.4.2; dos fallos seguidos → recrear la caja.

Controles **antes del sello**, en un caso R de LABMULTIMUT (R-MT1), resultados en el sello:

| Control | Qué es | Pasa si |
|---|---|---|
| VACÍO | El árbol tal cual | 0 arreglados |
| INOCUO | Cambia el texto de un comentario de `Acuse.cls` | 0 arreglados, 0 colateral |
| DAÑINO-A | `Acusar` devuelve AR 207 donde construía el AA | colateral > 0 (en los aceptados de la regresión) |
| **DAÑINO-B** (nuevo) | `Decidir` devuelve siempre `AA` (se anula la rama de rechazo) | colateral > 0 (en los rechazos correctos de la regresión, §1.4.1) |
| FIX | El parche del implementador para R-MT1 (quitar la guarda del modo sitio en `Decidir`), guardado en la clave y nunca en la caja; **o** el diff aislado de H-COM-MT2 sobre su árbol antes (§1.2) | 100 % de los disparadores (todos los grupos), 0 colateral |

Si un control no separa, no se mide con esa caja hasta explicarlo (lección 7). DAÑINO-B se añade porque los arreglos esperados
en LABMULTI **añaden rechazos** (R-MT1, R-MT4): hay que probar que el evaluador vería un parche que acepta de más, y en las otras
cajas no se había comprobado esa dirección; se pasa también en LABADTMUT y LABORUMUT si cabe en el tope (deseable, no
obligatorio: ya tienen su FIX real como control).

---

## 3. El análisis, sabiendo que n se amplió después de ver p = 0,22

### 3.1 El problema y las tres opciones

El piloto preinscribió «indeterminado no dispara añadir casos» y, aun así, Víctor decide ampliar. Si los 11 casos se juntan con
los nuevos y se calcula McNemar como si fueran 19, el p es **optimista**: la decisión de seguir se tomó mirando el p de la etapa
1 (parada opcional). Opciones:

| Opción | Qué se calcula | A favor | En contra |
|---|---|---|---|
| (A) Réplica independiente | Solo los n₂ nuevos, con la regla del piloto | Limpia; no toca la etapa 1 | Con n₂ ≈ 6-8 solo puede «aportar» con ≥ 5 discordantes a favor y 0 en contra (p < 0,10 a dos colas); tira la información de la etapa 1 |
| (B) **Combinación con pesos fijos** (inverso-normal, Lehmacher-Wassmer) | Un estadístico que junta el p de cada etapa con pesos escritos antes de medir la 2 | Válida aunque n₂ se haya elegido tras ver la etapa 1 (es el principio de los diseños adaptativos: la etapa 2 se evalúa condicionada a la 1); usa toda la información; es una fórmula con números | Hay que fijar los pesos ahora y explicarla |
| (C) Juntar sin más | McNemar sobre 11 + n₂ | Lo que haría cualquiera | Optimista; no se puede publicar como primario |

**S-AMP-6. Primario: (B). (A) y (C) se publican al lado como secundarios**, (A) con el rótulo «réplica» y (C) con el rótulo
«agregado ingenuo, optimista». Es la Q-AMP-5 (Jev), con (A) como alternativa.

### 3.2 La regla de decisión, en números, preinscrita

Primario: **LOC3 en H + R, AG frente a REF**, con «alguna réplica» para los pares (como el piloto) y la verdad ampliada de R.

- **Etapa 1 (fija, del piloto):** n₁ = 11; discordantes 5 a favor de AG, 1 en contra; p₁ exacto de McNemar a **una cola** (la
  dirección «AG > REF») = P(X ≥ 5 | 6, ½) = 7/64 = **0,109**; Z₁ = Φ⁻¹(1 − 0,109) = **1,229**. La implementación lo recalcula
  desde `privado/agente/ag3/analisis.json`; si no sale eso, se declara y se usa lo que salga, sin tocar nada más.
- **Etapa 2:** sobre los n₂ casos nuevos (fijado en el sello), b₂ = casos con AG (alguna réplica) = 1 y REF = 0, c₂ = AG = 0 y
  REF = 1; p₂ = P(X ≥ b₂ | b₂ + c₂, ½), exacto a una cola; Z₂ = Φ⁻¹(1 − p₂). Si b₂ + c₂ = 0 (ningún par discordante) la etapa
  no informa: **Z₂ = 0**. Para el cálculo p₂ se acota a [0,0005, 0,9995].
- **Combinado:** Z = (√11 · Z₁ + √n₂ · Z₂) / √(11 + n₂); pesos √n fijados aquí, con n₂ el del sello.
- **Δ** = media de (LOC3_AG − LOC3_REF) por caso sobre los 11 + n₂ (LOC3_AG = media de las 2 réplicas), con IC95 por bootstrap
  sobre casos (10 000, semilla `AMP3|<huella de amp_clave>`); también Δ₁ (= +0,36) y Δ₂ (solo nuevos) al lado.

**Decisión (frase 2, localizar):**
- **Aporta** si Z ≥ 1,645 (α = 0,05 a una cola, que es el 0,10 a dos colas del piloto en la dirección que importa) **y** Δ ≥ 0,20.
- **No aporta** si Δ ≤ 0,10, **o** el IC95 de Δ contiene 0 y Δ < 0,20.
- Si no, **«indeterminado: n insuficiente para la diferencia observada»**, y **se cierra**: esta es la última etapa (S-AMP-9).

Lo que eso exige de la etapa 2, para que se vea que la regla no es laxa: con Z₁ = 1,229 y n₂ entre 4 y 10, aportar exige
Z₂ ≥ 1,09-1,15, es decir **p₂ ≤ 0,126-0,137**. Con el test exacto a una cola, los pares discordantes (a favor / en contra) de
los casos nuevos que bastan son:

| a favor | en contra que todavía aporta | p₂ |
|---|---|---|
| 3 | 0 | 0,125 |
| 4 | 0 | 0,063 (4/1 = 0,188 no) |
| 5 | 0-1 | 0,031 / 0,109 |
| 6 | 0-1 | 0,016 / 0,063 (6/2 = 0,145 no) |
| 7 | 0-2 | ≤ 0,090 |
| 8 | 0-3 | ≤ 0,113 |

En palabras: **la ampliación aporta si los casos nuevos dan al menos 3 discordantes a favor del agente sin ninguno en contra, 5
con uno en contra, 7 con dos, u 8 con tres, y la Δ combinada sigue en ≥ 0,20.** Es más exigente que (C) (que con solo 2/0 nuevos,
5/1 + 2/0 = 7/1 agregados, ya daría p = 0,07 a dos colas) y menos que (A) (que exige 5/0). Si la etapa 2 da ≤ 2 discordantes a favor, el resultado es indeterminado o peor, y se
publica así.

**Frase 1 (absoluta)** sobre los 11 + n₂, con los umbrales del piloto: LOC3(AG) con límite inferior de Wilson > 0,33 y LOC3 en M
≥ 0,75 (M no se remide: vale el 1,00 del piloto, y se dice); FIX(AG) con límite inferior > 0,20 y colateral medio por tirada
< 1. Se reporta también sobre los n₂ solos.

**FIX (secundario, descriptivo, sin corrección):** la misma combinación (B) con sus propios Z₁ (7 a 0 en el piloto → p₁ =
1/128 = 0,0078, Z₁ = 2,42) y Z₂; frente a VACÍO como en el piloto (aporta exige FIX(AG) ≥ 0,30).

### 3.3 Qué se publica en cada combinación de resultados

La frase 2 publicada es la del **combinado**; la tabla de `RESULTADO-AMP.md` lleva siempre las tres columnas (piloto / nuevos
solos / combinado) con Δ, discordantes, p y decisión. Y el texto que acompaña, según lo que salga:

| Combinado | Nuevos solos (A) | Qué se publica |
|---|---|---|
| aporta | aporta | «Aporta, **replicado**: la etapa 2 por sí sola también lo da» |
| aporta | indeterminado | «Aporta **por acumulación**: la etapa 2 sola no basta (Δ₂, p₂), pero sumada a la 1 cruza la regla preinscrita» |
| aporta | no aporta | Imposible con esta regla (p₂ ≤ 0,137 exige ≥ 3 a favor netos en n₂ ≤ 10, luego Δ₂ > 0,10); si ocurriera, se publica el cálculo y se declara error de diseño |
| indeterminado | aporta | «Indeterminado en conjunto; la etapa 2 sola aporta pero el combinado no (puede pasar con Δ combinada < 0,20)» |
| indeterminado | indeterminado | «Indeterminado con n = 11 + n₂; **se cierra el estudio**: no se amplía más; la diferencia observada queda como descriptiva» |
| indeterminado | no aporta | «Indeterminado, y **los casos nuevos no replican** la ventaja del piloto (Δ₂ ≤ 0,10): la ventaja se concentró en los H de ORU de la etapa 1» |
| no aporta | cualquiera | «No aporta» (Δ combinada ≤ 0,10 o IC con 0 y Δ < 0,20), con Δ₁ y Δ₂ al lado |

En todos los casos se publica también (C) con el rótulo «optimista», para que quien lea vea cuánto cambia la corrección.

### 3.4 Sensibilidades preinscritas (LOC3, AG frente a REF)

(i) R con la verdad sellada; (ii) solo H (11 + n₂); (iii-amp) sin pista en `verificador.json` (quita R4, R6, R-ADT-7, R-ADT-8,
R-MT1, R-MT4); (iv) DS frente a REF sobre lo que DS haya medido; (v) «las dos réplicas»; (vi) = (A), solo nuevos; (vii) = (C),
agregado ingenuo; (viii) sin los casos con comentario de código que nombre la deuda o su causa (R-MT1, R-MT4); (ix) sin las
deudas por decisión (R-ADT-8, R-MT1, R-MT4, y R-ADT-7 si cuenta), que es la lectura «solo fallos que nadie decidió»; (x) etapa
2 por caja (LABADTMUT / LABORUMUT / LABMULTIMUT), descriptiva, porque en LABMULTI FIX es solo acuse. Las negaciones falsas se
reportan por caso, y en las deudas por decisión se clasifica la `explicacion` del agente como «razonada» (cita S97/S98/el
contrato) o no; no cambia ninguna puntuación.

### 3.5 Formato fijo de las dos frases en `RESULTADO-AMP.md`

> «Con la ampliación (n = 11 + {n₂}), el agente **{funciona | …}**: localiza top-3 en {k}/{n} casos reales (IC95 {a}-{b}; azar {c})
> y arregla sin colateral {k'}/{n} (IC95 {a'}-{b'}). Frente a la búsqueda sin modelo **{aporta | no aporta | indeterminado}**
> (combinado de dos etapas: Z = {Z}, Δ {Δ}, IC {…}); piloto Δ +0,36 (5/1, p 0,22); casos nuevos Δ {Δ₂} ({b₂}/{c₂}, p₂ {p₂});
> agregado ingenuo p {p_C}, optimista. Esta es la última etapa. Coste: {t} tokens por tirada, {t/FIX} por arreglo aceptado.»

---

## 4. Brazos, réplicas, presupuesto y reglas de parada

### 4.1 Lo mínimo que cambia respecto al piloto, y por qué

| Qué | Piloto | Ampliación | Por qué |
|---|---|---|---|
| Casos | 5 H + 6 R + 12 M + 3 L | **1-2 H + 4-6 R + 0 M + 1 L** (L-multi) | M calibró REF y evaluador y no se remide; L-multi es el control negativo de la caja nueva |
| Brazo AG | `claude -p`, `claude-opus-5-5`, 2 réplicas, 200 k / 30 / 10 min | **Igual**; si el modelo por defecto de la herramienta ya no es `claude-opus-5-5`, el lanzador pasa `--model claude-opus-5-5` (DV-AMP) | La etapa 2 tiene que ser el mismo agente que la 1; una tirada con otro modelo es inválida (DV-AG-12) |
| Brazo REF | congelada (sha en SELLO-AG1) | **Idéntica, sin una fila más** | Ahora el corpus es conocido: cualquier fila nueva sería memorizar la clave. Su debilidad prevista en ajustes/`AckMode`/juego de caracteres se declara (L-AMP-3) |
| Brazo DS | 1 réplica, ≤ 1,8 USD | 1 réplica sobre H + R nuevos + L-multi en orden sembrado, **tope 0,45 USD** (saldo ≈ 0,5; margen 0,05); lo no medido se reporta | Q-AMP-7; sigue siendo el contraste de independencia, ahora parcial (~4 tiradas a ~0,10 USD) |
| Subestudio de fragilidad | 6 tiradas en M | **No se hace** | Ya medido (estable, no depende del oráculo); no hay M |
| Evaluador | 4 controles por caja | 4 + **DAÑINO-B** en LABMULTIMUT (§2.4) | Los arreglos esperados añaden rechazos |
| Regresión | hasta 60 sembrados | + mínimos de §1.4.1 (≥ 10 AA, ≥ 5 rechazos correctos) + vecinos del borde | L-AG-14/16 |
| Restauración | firma; ADT por veredicto (DV-AG-16) | Por caja, medida antes (§1.4.2) | No decidir sobre la marcha |
| Disparadores H | solo banco | banco, y construidos si < 3 (S-AMP-3) | H-COM-1/2 cayeron por el banco |
| Análisis | McNemar + Δ, n = 11 | Combinación de dos etapas con pesos fijos (§3) | Parada opcional |
| Consigna, lanzador, MCP, puertas, formato | fijos | **fijos** (sha iguales) | ANTES |

### 4.2 Números

- **Tiradas:** AG = 2 × (n₂ + 1 limpio) → con n₂ = 6-8, **14-18 tiradas**; REF = n₂ + 1; DS ≤ 4-5.
- **Tokens del brazo AG:** media del piloto 42 040 nuevos por tirada, máximo 98 712 → previsto **0,6-0,8 M**, cota con el máximo
  1,8 M, repeticiones por inválida ≤ 10 %. **Tope duro del brazo: 3 M tokens nuevos.** No se añaden tiradas para gastarlo.
- **Caja:** evaluaciones con parche ≤ 18 AG + ≤ 1 REF + ≤ 5 DS ≈ 24 × 3-4 min ≈ 1,5 h; puertas de AMP1 ≈ 30 cargas × 3 min ≈
  1,5 h; todo en segundo plano con `systemd-run --user`, lo que llama fuera en primer plano.
- **Sesiones:** 1,5 en total (§6).

### 4.3 Reglas de parada de AMP2 (en el sello, como números)

- Las **3 primeras tiradas AG** por orden sembrado, todas «sin respuesta» o inválidas → se para, se diagnostica el lanzador (DV-AMP)
  y se reanuda una vez; si se repite, se para el brazo.
- Tiradas inválidas por la auditoría ≥ **2** (de ≤ 18) → se arregla la caja (DV-AMP) y se reanuda; si vuelve a pasar, se para.
- Tokens nuevos del brazo AG ≥ **3 M** → se para el brazo.
- DS ≥ **0,45 USD** → se para ese brazo; los casos no medidos se reportan.
- Una restauración falla **dos veces** en la misma caja → se recrea la caja; si tras recrearla vuelve a fallar dos veces, los casos
  de esa caja se retiran (declarado) y se sigue con los demás; n₂ se recalcula y se declara (DV-AMP).
- Una tirada con modelo distinto de `claude-opus-5-5` es inválida y cuenta para la regla de inválidas.
- Una tirada cortada por presupuesto no se repite: «sin respuesta».
- Si al llegar al tope de AMP2 (0,4 sesión) faltan tiradas, siguen en segundo plano y AMP3 espera; no se recorta el corpus.

---

## 5. Amenazas a la validez nuevas (frente a D-AG §6)

1. **Parada opcional.** n₂ se eligió tras ver p = 0,22. Mitigación: combinación con pesos fijados antes de medir la etapa 2 (§3.2),
   (C) publicado solo como «optimista», y esta etapa declarada última (S-AMP-9). Lo que no mitiga: que la decisión de ampliar
   fuera condicionada a un resultado prometedor sesga qué estudios se amplían; se dice en el informe.
2. **Pistas más densas que en el piloto.** 4 de 6 R nuevos tienen su diagnóstico, o su id de deuda, en `verificador.json`, y dos
   lo tienen en comentarios del código. Mitigación: lista preinscrita, sensibilidades (iii-amp), (viii), L-AMP-2. Riesgo
   residual: si el «aporta» desaparece en (iii-amp), la frase 2 lo dice en su texto («aporta solo con las pistas del juez»).
3. **Deudas por decisión.** R-ADT-8, R-MT1 y R-MT4 son comportamientos que el laboratorio decidió mantener (S97, S98, contrato
   L-MT1). El juez los cuenta como fallo y eso es la verdad por decisión (L-AG-3); pero un agente que responda «no hay fallo,
   es una decisión declarada» está razonando bien y puntúa 0. Mitigación: sensibilidad (ix) y el recuento de negaciones
   razonadas; L-AMP-1. Es también una pregunta de producto: en la guardia real esas deudas existen y el ingeniero tiene que
   saber que lo son.
4. **Correlación con la etapa 1.** El mismo fallo en otra copia del código (SINID, `Validate dm`) no es una observación nueva:
   S-AMP-1. Riesgo residual: fallos «parecidos» sin ser el mismo (otro 1xx en otra rama de `MotivoRechazo`); se acepta.
5. **Dos etapas con poblaciones distintas.** La etapa 1 tenía 5 H de ORU (donde el agente sacó toda la ventaja); la 2 tiene
   sobre todo R de configuración y de ausencia. El combinado mezcla; por eso se publican Δ₁ y Δ₂ al lado y la sensibilidad (x).
6. **La referencia no fue calibrada para esto.** REF se afinó con M (fidelidad de una línea, códigos de acuse). `AckMode`,
   `DefCharEncoding`, una guarda de modo y una comprobación ausente no tienen fila propia en su tabla (`MSH-18` sí la tiene). Un
   «aporta» en la etapa 2 puede ser «REF débil en ajustes». No se corrige (sería afinar con el corpus conocido); se declara
   (L-AMP-3) y la lectura de §3.3 lo nombra si (viii)/(ix) lo cambian.
7. **El juez como parte del caso.** R-ADT-7 puede ser imposible de aceptar por el juez (L-MT11). Mitigación: puerta en seco
   antes de construir (§1.3.1) y retirada declarada; el verificador no se toca durante el estudio.
8. **Caja sin almacén.** En LABMULTIMUT FIX solo exige el acuse: es más fácil que en LABORUMUT (almacén releído). Se reporta FIX
   por caja (x) y se dice en la frase.
9. **Bytes crudos.** El arnés puede normalizar el cable de R-ADT-8 en silencio. Mitigación: control de `<0xNN>` en la evidencia
   (§1.3.2) antes del sello.
10. **El tope de 1,5 sesiones con una caja nueva.** Riesgo de sellar con prisa. Mitigación: la regla del ANTES (< 4 casos que
    cuentan → se para y se publica eso) y los topes por fase (§6); las puertas no se relajan para llegar a 4.
11. **Pocos casos por caja y por tipo.** Con n₂ ≈ 6, un solo caso vale 0,17 de Δ₂. La regla de §3.2 lo absorbe (exige 3 a favor
    netos); las frases no afirman nada por caja.

---

## 6. El plan AMP0-AMP3, con «hecho cuando» y tope por fase (total 1,5 sesiones)

| Fase | Qué se hace | Hecho cuando | Tope y regla de parada |
|---|---|---|---|
| **AMP0** Diseño | Este documento; Q-AMP decididas (Jev; las de alcance, Víctor) | `diseno-ampliacion-fable.md` en el repo con las Q-AMP respondidas en `etapa/SELLO-AMP.md` §0 | **0,15 sesión.** Si una Q de alcance no está decidida al cerrar AMP0, se sigue con la recomendación y se declara |
| **AMP1** Casos, caja y sello | Puerta en seco de R-ADT-7 (§1.3.1) **lo primero**; caja LABMULTIMUT (creación, exportador, medir, restaurar, 5 controles del evaluador); firma/veredicto por caja (§1.4.2); R: construcciones, zonas preinscritas, puertas, regresiones con los mínimos de §1.4.1; H: hunks de los dos commits, correspondencia con §1.1, H-CAB-1 (y 1b/2 si salen), H-COM-MT2 como control si cabe; L-multi; cajas generadas; escáner de fugas (§1.4.3); n₂; `amp_clave.json` y `SELLO-AMP.md` commiteados | Todo lo anterior medido y escrito; el sello lleva n₂, Z₁, los pesos, las reglas de restauración y de parada, los controles por caja y la lista de pistas | **0,7 sesión.** Se para (y se publica «la ampliación no da casos» con las puertas medidas) si al agotar el tope hay **< 4** casos nuevos que cuentan (ANTES). Ninguna puerta se relaja para llegar a 4 |
| **AMP2** Tiradas | REF sobre n₂ + 1 → AG 2 réplicas en orden sembrado `AMP2\|<huella>` → DS hasta 0,45 USD → evaluación de cada parche en su caja con restauración | Todas las tiradas con transcripción auditada, `respuesta.json`, `puntos.json`, `fix.json`, coste | **0,4 sesión** (el resto en segundo plano). Reglas de §4.3 |
| **AMP3** Análisis y cierre | `amp3.py` (el guion de §3, escrito y sellado en AMP1, sin cambios); verdad ampliada de R; tabla por caso y brazo; las tres columnas; sensibilidades (i)-(x); lectura manual de **2** parches aceptados nuevos si los hay (Jev; no cambia puntuaciones); amenazas con lo observado; `RESULTADO-AMP.md` con el formato de §3.5; cajas paradas, USER en marcha con huella y sonda AA; `antes_de_publicar.py` LIMPIO; publicación del diseño, el sello y los agregados (sin clave ni transcripciones con datos); memoria: ficha con las dos frases y «última etapa» | `RESULTADO-AMP.md` da las dos frases con la regla preinscrita aunque salgan «no aporta» o «indeterminado»; guarda LIMPIO | **0,25 sesión.** No se añade ningún caso ni réplica tras ver los datos; no habrá AMP4 de corpus |

---

## 7. Preguntas (Q-AMP), límites (L-AMP) y resumen de decisiones (S-AMP)

| Q | A quién | Pregunta | Recomendación | Alternativa | Qué cambia en la medida |
|---|---|---|---|---|---|
| **Q-AMP-1** | Víctor (alcance) | ¿Cuenta un H de la pieza común cuyo fallo ya estuvo en el piloto como R6 o como el mutante MA11? | No (S-AMP-1); se usa como control de la caja nueva | Sí: H-COM-MT2 y H-COM-MT3 cuentan | Con la alternativa n₂ sube en 2 con casos correlacionados con la etapa 1 y que el mismo modelo ya resolvió: el p₂ se infla por construcción |
| **Q-AMP-2** | Jev | Si el juez no da `correcto` a «sin ACK con MSH-15/16 = NE», ¿qué se hace con R-ADT-7? | Retirarlo como «del juez / del perfil», declarado; no tocar el verificador | Arreglar el verificador antes del sello y remedir | La alternativa cambia al juez en mitad del estudio: la etapa 2 se mediría con otro juez que la 1 |
| **Q-AMP-3** | Jev | ¿Cuenta R-MT1, que es una decisión declarada (S98, confianza 0,16)? | Sí, con la sensibilidad (ix) y el recuento de negaciones razonadas | No: solo como control | Sin R-MT1, n₂ baja en 1 y se pierde el único caso de «guarda de modo»; con él, un `hay_fallo: false` bien argumentado puntúa 0 |
| **Q-AMP-4** | Jev | ¿Se recortan de `verificador.json` los cuatro paréntesis que nombran `CIR-*` (L-MS-1, S97, S98) y describen la causa? | No: idéntico al piloto, pistas listadas, sensibilidades (iii-amp) y (viii) | Recortar solo esos paréntesis | Recortar hace la etapa 2 no comparable con la 1 y es diseñar la caja mirando el corpus; no recortar favorece a AG y DS (REF no lo lee) en 4 de 6 R: lo acota la sensibilidad, no lo elimina |
| **Q-AMP-5** | Jev | ¿Cómo se analiza con n ampliado tras ver p? | (B) combinación inverso-normal con pesos √11 y √n₂, α = 0,05 a una cola; (A) y (C) secundarios | (A) réplica independiente como primario | Con (A) aportar exige 5/0 en n₂ ≈ 6-8: casi solo puede salir «indeterminado»; con (B) exige 3/0, 5/1, 7/2 u 8/3 |
| **Q-AMP-6** | Jev | ¿Se construyen disparadores para H cuando el banco no los tiene? | Sí (S-AMP-3), construcción escrita antes de mirar el otro commit | Solo banco, como el piloto | Sin construcción H-CAB-1 probablemente cae con 0 disparadores, como H-COM-1/2 |
| **Q-AMP-7** | Jev | ¿Corre DS con 0,45 USD (≈ 4 tiradas)? | Sí, en orden sembrado, descriptivo, lo no medido reportado | No correr DS | Sin DS no hay contraste de independencia en la etapa 2; con 4 tiradas es parcial y se dice |
| **Q-AMP-8** | Jev | ¿Se fusionan MS-1 y MS-1b en un caso si comparten unidad de verdad? | Sí (S-AMP-2) | Dos casos | Dos casos con la misma unidad serían dos observaciones de la misma localización |
| **Q-AMP-9** | Jev | ¿R-MT4 incluye los controles C0 (S10) entre sus disparadores? | No: PID-8 fuera de tabla y PID-7 inválida | Sí, un tercer grupo | Con C0, FIX exige tres comprobaciones nuevas y la mecánica de `<0xNN>`; sube el realismo y casi seguro FIX = 0 |
| **Q-AMP-10** | Jev | ¿Cuenta R-ADT-8, que S97 decidió dejar en lab y cuyo arreglo conforme exige detectar el juego? | Sí, para localizar y arreglar, con la previsión «localiza, no arregla» escrita | Solo para localizar | Si solo cuenta para localizar, FIX se calcula sobre n₂ − 1 y la frase 1 lo dice |

**Límites declarados de entrada (L-AMP):**

- **L-AMP-1.** Tres de los R nuevos (cuatro si R-ADT-7 cuenta) son deudas por decisión: el juez los cuenta como fallo, el circuito los
  hace adrede. Una negación razonada del agente puntúa 0; se reporta aparte.
- **L-AMP-2.** `verificador.json` y los comentarios del código llevan el diagnóstico de 4 de 6 R nuevos; solo lo acotan las
  sensibilidades (iii-amp) y (viii).
- **L-AMP-3.** REF se congeló calibrada con M; no tiene filas para `AckMode`, juego de caracteres por omisión, guardas de modo ni
  comprobaciones ausentes. Un «aporta» en la etapa 2 puede ser «REF débil en ajustes»; no se afina.
- **L-AMP-4.** En LABMULTIMUT FIX se decide solo por el acuse (no hay almacén): es más fácil que en las otras cajas.
- **L-AMP-5.** n₂ ≈ 4-8: la etapa 2 sola no detecta diferencias < 0,30; el combinado hereda el poder del piloto.
- **L-AMP-6.** La decisión de ampliar fue condicionada a un p prometedor; la combinación corrige el cálculo, no la selección de
  qué estudios se amplían.
- **L-AMP-7.** El verificador de hoy puede no ser el del 12-oct; los 11 casos del piloto no se remiden. Se declara la huella.
- **L-AMP-8.** Mirth sigue sin casos que cuenten: las frases hablan de circuitos IRIS (L-AG-7).

**Resumen de decisiones propuestas (S-AMP):**

| S-AMP | Decisión |
|---|---|
| S-AMP-1 | Un fallo cuenta una vez en todo el estudio: los H de la pieza común que repiten R6 / MA11 no entran en n₂ |
| S-AMP-2 | Candidatos con la misma unidad de verdad se funden en un caso con grupos de disparadores |
| S-AMP-3 | Disparadores construidos también para H cuando el banco da < 3, declarados y escritos antes de mirar el otro commit |
| S-AMP-4 | `verificador.json` idéntico al del piloto; pistas listadas y comprobación de fugas por escáner sobre cada caja; sensibilidades (iii-amp) y (viii) |
| S-AMP-5 | Caja `LABMULTIMUT` en puertos 2590-2594, exportador con sustitución acotada en Production y Puntos, modo lab comprobado, 5 controles del evaluador (DAÑINO-B nuevo) |
| S-AMP-6 | Análisis primario por combinación de dos etapas con pesos fijos; réplica y agregado ingenuo como secundarios |
| S-AMP-7 | Regresión con ≥ 10 aceptados y ≥ 5 rechazos correctos en todo caso nuevo; vecinos del borde en R-MT1 y R-MT4 |
| S-AMP-8 | Restauración por firma o por veredicto decidida por caja con medida antes del sello |
| S-AMP-9 | Esta es la última etapa: ningún resultado dispara una tercera ampliación del corpus |
| S-AMP-10 | Presupuesto: AG ≤ 3 M tokens nuevos, DS ≤ 0,45 USD, 1,5 sesiones (0,15 / 0,7 / 0,4 / 0,25); < 4 casos nuevos que cuentan → se para y se publica |
