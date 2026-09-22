# La mitad v2 de la vía (d), medida: también ciega, y ahora se sabe por qué (22-sep-2026)

**Predicción sellada antes de instalar nada** — `PRE-VIA-D-V2.md`, huella `f7c897ac`, commit
`2dd740d`. Decía **0 de 2**. Fue 0 de 2.

Con la mitad FHIR (`VIA-D-RESULTADO.md`), **las dos mitades de la vía (d) son ciegas al fallo
silencioso.**

## Lo que se montó

`hl7apy` **1.3.5** —biblioteca v2 de terceros, ni mía ni de InterSystems— en un entorno virtual
aparte, para no tocar el python del sistema. Valida un mensaje contra su perfil: segmentos
requeridos, cardinalidades, tipos de dato y valores de tabla.

**Control negativo, corrido antes que nada:** al mismo acuse se le quitó el segmento `MSA`, que es
obligatorio en un `ACK`. Protestó — `ValidationError: Missing required child ACK.MSA`. La
herramienta mide.

📏 **Un artefacto del instrumento, declarado:** los payloads traen `MSH-7 = <hora oculta>` porque el
arnés enmascara los relojes absolutos a propósito desde el paso 4. Eso no es del circuito, así que
se sustituyó por una marca válida en los 10 mensajes antes de validar. Sin esa sustitución, el único
error de todos los acuses habría sido mío y habría tapado lo que se buscaba.

## Lo primero que apareció, y no era la medida

📏 **De los tres fallos vivos que la mitad v2 iba a mirar, uno no está al alcance de ninguna
herramienta que trabaje sobre mensajes.** El `MSA|CE` del FailureTimeout **no deja acuse almacenado**:
la traza dice «no se devolvió ningún ACK de aplicación» en los dos casos mirados, y el `CE` solo
existe como línea del log —`Constructing ACK with code CE`—. El acuse que el motor construye al
agotar el plazo **no se conserva en forma de mensaje**.

Quedan dos comprobables: el 4xx contestado `AR` con `ERR-3=102`, y el `PV1` fuera de sitio contestado
con `ERR-3=101` teniendo el identificador presente.

## La primera comparación estaba confundida, y hay que decirlo

La comparación automática entre acuses de fallo y acuses limpios dio **1,00 contra 0,00** y mi propio
criterio la leyó como *«P1 refutada o matizada»*. **Era un falso positivo, y de manual.**

**Los acuses limpios no llevan segmento `ERR`.** Cualquier hallazgo sobre el `ERR` crea una
diferencia con los limpios que no es detección: un detector que dispare con «hay `ERR`» acierta el
100 % sin entender nada. Es exactamente el modo de fallo **F8** del diseño —«B es rara por
construcción»— apareciendo **dentro del propio oráculo**, y en la primera medida que se hizo con él.

**Corolario que vale para el diseño entero:** un control de discriminación tiene que comparar
**correcto contra incorrecto en la misma estructura**, no **fallo contra limpio**.

## El control que decide

Para cada acuse de fallo se construyó su variante **corregida** y se validaron las dos:

| operador | como está | corregido | ¿distingue? |
|---|---|---|---|
| `ENV_FHIR_CREDENCIAL_401` ×2 | `ERR-3=102` Data type error | `ERR-3=207` Application internal error | **no, idéntico** |
| `ENV_FHIR_RUTA_404` ×2 | `ERR-3=102` Data type error | `ERR-3=207` Application internal error | **no, idéntico** |
| `SEG_ORDEN_PV1_ANTES_PID` ×2 | `ERR-3=101` Required field missing | `ERR-3=100` Segment sequence error | **no, idéntico** |

**6 de 6 idénticos.** El comprobador dice exactamente lo mismo con el código bueno que con el malo.

## Y lo único que dijo de los acuses de fallo era un falso positivo suyo

El aviso, idéntico en los seis: `Value HL70357 not in table HL70396 in element ERR_3.CWE_3`.

**Mirado en el estándar antes de apuntarlo como fleco**, que está en disco
(`estandares/hl7v2/HL7_Messaging_v25/txt/CH02A.txt`):

> «When an HL7 table is used for a CE data type, the name of coding system component is defined as
> HL7nnnn where nnnn is the HL7 table number.»

**`HL70357` es correcto.** El aviso es una laguna de la copia de la tabla 0396 de `hl7apy`, no un
defecto del circuito. Un fleco falso menos: tres minutos de lectura, como la Fase 11bis ya enseñó.

## Contra la predicción

- **P1 — «0 de 2»: confirmada**, por el control de correcto-contra-incorrecto.
- **P2 — «lo que reporte será igual»: confirmada**, con el matiz de que la igualdad hay que buscarla
  en la comparación buena y no en la ingenua.
- **P3 dispara**, y es lo que se lleva esta medida:

> **Un oráculo de estantería comprueba que el mensaje esté bien formado y que sus códigos existan.
> Un fallo silencioso es un valor válido en la situación equivocada. Son cosas distintas, y ninguna
> herramienta de conformidad puede ver la segunda.**

## Lo que hace con el diseño

La vía (d) se decidió (§11.5) porque aportaba **un oráculo cuya firma no es la mía**. Medidas las dos
mitades: **el oráculo independiente que se prometió no existe con herramientas de estantería en este
circuito**. Quedan dos salidas y las dos son honestas si se dicen:

1. **Pagar el mapeador de referencia** desde el IG normativo, que sí vería los tres, **declarando que
   la firma es mía**. Deja de ser «un tercero» y pasa a ser «yo con el mapeo publicado delante», que
   es una cosa más modesta pero todavía útil: es la misma categoría que `v3-invariante`, que ya está
   medida en +0,705.
2. **Aceptar que aquí no hay oráculo independiente** y escribirlo en el informe, con la razón, que
   transfiere a cualquier integración y no solo a esta.

**Lo que ya no se puede decir** es que la vía (d) aporta una firma ajena. Eso está medido y es que
no.
