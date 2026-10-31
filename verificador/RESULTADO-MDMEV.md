# Resultado de la etapa 28: los otros eventos de MDM (T04, T06, T08 y T10)

**En T04, T06, T08 y T10, los conversores tratan el documento como en T02 en todos los eventos que convierten: 0 diferencias en
120 pares. Microsoft no convierte T04 ni T08, porque no tiene plantilla, y LinuxForHealth no convierte T04, T08 ni T10, como
declara su README. No hay discrepancias nuevas.**

La regla de resultado, escrita antes de medir ([`ANTES-ETAPA-MDMEV.md`](ANTES-ETAPA-MDMEV.md)), preveía este caso: si no hay
diferencias con T02, se declara así y se publica igual.

| | |
|---|---|
| Conversores | Microsoft FHIR-Converter v7.0 (`253307f`) y LinuxForHealth hl7v2-fhir-converter v1.1.0, en su caja, como en la etapa 26 |
| Corpus | 200 mensajes en v2.5, válidos en estructura y en los condicionales de TXA: las 40 bases de MDM_T02 de la etapa 26 en los cinco eventos ([`mev/bases_mdmev.py`](mev/bases_mdmev.py)). Solo cambian el evento (MSH-9 y EVN-1), el número de control y, en T06 y T10, el documento padre (TXA-13), que v2.5 exige en esos eventos (§9.6.1.13). Seis de las 40 bases (29 de los 200 mensajes) llevan en TXA-17 o TXA-19 un estado que las tablas de transiciones del capítulo 9
(figuras 9-1 y 9-2) no dan para su evento. Además, las muestras públicas de T06 y T10 |
| Juez | El de la etapa 26 (`4f9118445c22`), con el punto de los cinco eventos que ya traía preparado: la alternativa de Q-MD-D-1, diseñada a ciegas, programada y probada en la etapa 26. **El juez no cambia** |
| Cómo se compara | Cada mensaje de T04, T06, T08 o T10 es un par mínimo de su T02. Se comparan la categoría y los mecanismos que cuentan ([`mev/juzgar_mdmev.py`](mev/juzgar_mdmev.py)) |

## Lo que salió

| Conversor | T02 | T04 | T06 | T08 | T10 |
|---|---|---|---|---|---|
| Microsoft | 39 fallo, 1 rechazo | sin plantilla | **igual que T02** en las 40 | sin plantilla | **igual que T02** en las 40 |
| LinuxForHealth | 40 fallo | no lo soporta | **igual que T02** en las 40 | no lo soporta | no lo soporta |

- **«Sin plantilla».** Microsoft no trae plantilla de MDM_T04 ni de MDM_T08. La herramienta lo registra sin correr el conversor.
- **«No lo soporta».** LinuxForHealth trae ficheros de plantilla para MDM_T04, T08 y T10 dentro de su jar, pero rechaza esos
  mensajes con «Message type not yet supported». Su README lista solo MDM_T02 y MDM_T06 entre los tipos que soporta.
- **En los dos casos** el conversor no corre el evento y lo dice; no es un fallo silencioso. Por las condiciones del ANTES, no
  cuenta como discrepancia. Lo de LinuxForHealth, además, está declarado en su README.
- **Sin las seis bases** con estados fuera de la tabla, quedan 102 pares, también con 0 diferencias.
- **Las muestras públicas:**
  - Microsoft da Bundle en los 31 T06 y los 2 T10;
  - LinuxForHealth, en los 31 T06, y rechaza los 2 T10 por la misma razón.

## La previsión sellada, frente a lo que salió

La previsión se selló antes de correr: [`mev/prevision-mdmev.json`](mev/prevision-mdmev.json) (programador) y
[`mev/decision-jev-prevision-mdmev.md`](mev/decision-jev-prevision-mdmev.md) (Jev).

| | Programador | Jev | Salió |
|---|---|---|---|
| Microsoft sin T04 ni T08 | 0,85 | 1,0 | **sí** |
| Microsoft trata T06 y T10 igual que T02 | 0,6 | — | **sí** |
| LinuxForHealth trata los cuatro igual que T02 | 0,65 | — | **no**: no corre tres de ellos. El que corre, T06, sale igual |
| Algo distinto de T02 en los eventos que corre | — | 0,91 | **no** |
| Al menos una nueva confirmada | 0,3 | 0,57 | **no** |

## Lo que no dice

- **No se juzga el sentido de los eventos.** La guía no da destino al documento padre (TXA-13), al motivo del cambio (TXA-21) ni
  a las transiciones de estado. Un conversor que ignore el documento padre en un añadido no se ve.
- **El corpus deriva de las 40 bases de T02.** Cada mensaje es un par mínimo, que es lo que se quería medir. Pero un fallo que
  solo saliera con contenido propio de un añadido o de una sustitución no está buscado.
- **«Igual que T02»** quiere decir con los mismos hallazgos que T02, incluidas las nuevas de la etapa 26, que siguen en T06 y T10.
- **Esta etapa no tuvo un diseño a ciegas nuevo.** Jev eligió que lo hiciera el programador (0,54 frente a 0,46), sobre el punto
  de los cinco eventos que la etapa 26 diseñó a ciegas.

## Una corrección de la etapa 26

La revisión a ciegas de esta etapa vio que dos de las cinco nuevas de MDM_T02 se apoyaban en T02 con TXA-19 «OB» y «UN»,
estados que la figura 9-2 no da para T02. Jev decidió retirarlas, y el resultado de la etapa 26 pasa a 3 nuevas y 9 ya
declaradas. Está en [`RESULTADO-MDM.md`](RESULTADO-MDM.md).
