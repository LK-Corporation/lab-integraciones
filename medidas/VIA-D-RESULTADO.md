# La vía (d), medida: el peldaño barato es ciego (22-sep-2026)

**La predicción estaba sellada antes de instalar nada** — `PRE-VIA-D.md`, huella `7c2e6779`,
commit `2f25e3e`. Decía que el validador oficial no vería ninguno de los tres fallos. **No vio
ninguno.**

## Qué se montó

- **Java 21** (`default-jre-headless`, Ubuntu 24.04) y el **validador oficial de FHIR**,
  `validator_cli.jar` v6.10.4, 192 MB, de la release de `hapifhir/org.hl7.fhir.core`. Fuera del
  repo, en `/datos/lab-integraciones/validador/`.
- `via_d_traer.py`: trae de FHIR los recursos `Patient` **realmente escritos** por el circuito
  congelado, localizándolos por el `Identifier` del canónico. **16 recursos, 0 sin traer.**
- `via_d_analizar.py`: cruza la salida del validador con la tabla de casos, con los limpios dentro
  como control de discriminación.

📏 **Y de paso, confirmado en el recurso final y no en el intermedio:** el circuito escribió en FHIR
`family = "Ferrándiz\S\Soler"` con la secuencia de escape literal, `family = "Ferr?diz"` y
`"Mu?z"` con el carácter de sustitución, y el `identifier` `X302207`, que es el primer `PI` en vez
del `MR` de la repetición 11. Los tres fallos están **dentro del recurso publicado**.

## La medida

Tres operadores de fallo (3 casos cada uno) y tres de limpio (3 + 2 + 2), validados contra el perfil
base de `Patient` de R4:

| operador | casos | fatal | error | warning | info |
|---|---|---|---|---|---|
| `PID3_MR_EN_REPETICION_11` | 3 | 0 | 0 | 3 | 0 |
| `PID5_ESCAPE_HL7` | 3 | 0 | 0 | 3 | 0 |
| `PID5_LATIN1_EN_EL_CABLE` | 3 | 0 | 0 | 3 | 0 |
| `NINGUNA_BASE` | 3 | 0 | 0 | 3 | 0 |
| `NINGUNA_MSH5_MSH6` | 2 | 0 | 0 | 2 | 0 |
| `NINGUNA_PV1_DISTINTO` | 2 | 0 | 0 | 2 | 0 |

**Un aviso por recurso, y es literalmente el mismo en los dieciséis:**

```
Constraint failed: dom-6: 'A resource should have narrative for robust management'
```

**Cero errores y cero fatales, en fallos y en limpios.** Uno por caso en los dos grupos: `1,00`
contra `1,00`.

## Contra la predicción

- **H1 — «0 de 3»: confirmada, exacta.** Contra el perfil base, `Ferrándiz\S\Soler` es un `string`
  válido, `Ferr?diz` también, y un `identifier` con el valor equivocado es un `Identifier` bien
  formado. El validador no tiene con qué saber que están mal.
- **H2 — «no correlacionado con el operador»: confirmada**, y de la forma más fuerte posible: no es
  que la correlación sea débil, es que **la salida es idéntica en los seis operadores**.
- **El control de que la prueba podía salir mal, pasado.** El validador **sí dijo algo** —el
  `dom-6`—, así que está funcionando. La diferencia entre «ciego» y «roto» estaba escrita de
  antemano y cae del lado de **ciego**.

## H3, que es la que obliga a tocar el diseño

> **El peldaño barato de la vía (d) es ciego al fallo silencioso**, que es el objeto de la fase.

La decisión §11.5 se tomó con el argumento de que (d) aportaba **un oráculo cuya firma no es la
mía**. Medido, la mitad FHIR de (d) aporta un oráculo que **no ve nada**, y eso no es lo mismo.

**Lo que queda, y hay que decirlo sin adornos:**

1. **La otra mitad de (d) sigue sin probar, y es donde vive su única esperanza.** El validador de
   conformidad **v2 sobre el acuse** no se ha corrido, y es el que podría ver los otros tres fallos
   vivos —el `CE` en modo original, el `AE` que no llega y el 4xx contestado `AR` con
   `ERR-3=102`—, que son violaciones de conformidad de verdad y no de tipo de dato. **Es la próxima
   medida, y es barata.**
2. **El mapeador de referencia desde el IG normativo sí vería los tres**, porque compara campo a
   campo contra el mapeo publicado. Pero **lo escribiría yo**, y eso le devuelve mi firma — que es
   exactamente lo que (d) existía para evitar. Sigue siendo defendible si se declara el sesgo, pero
   entonces **(d) deja de ser «un tercero» y pasa a ser «yo con el IG delante»**.
3. **Si la mitad v2 tampoco ve nada**, la conclusión honesta es que **ninguna vía ve el silencio sin
   firma propia**, y eso es un hallazgo sobre el diseño, no un contratiempo: significa que la
   independencia del oráculo, tal como se prometió en la §4.3, **no es alcanzable con herramientas
   de estantería** en este circuito.

## El subproducto, que no es el objeto pero es real

📏 **El circuito escribe `Patient` sin `text` narrativo**, en los dieciséis, limpios incluidos. Es un
aviso, no un error —`dom-6` dice *should*, no *shall*— pero es una no conformidad real con el perfil
base de R4 y no estaba anotada en ninguna parte. Va a flecos.
