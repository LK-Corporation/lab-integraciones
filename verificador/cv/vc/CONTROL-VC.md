# VC3: el control de `verificar_conversor.py` con los dos conversores del estudio (24-oct-2026)

**Hecho: la herramienta da exactamente los mismos veredictos que el estudio, caso por caso, en los dos conversores.**

Se comparó con el juicio del estudio en su última versión (CV4, juez `40bbc3ef`), sobre el mismo corpus: 368 mensajes por
conversor. «El mismo veredicto» es lo que decidió Jev (Q-VC-D-7): estado de la salida, categoría, subtipo y el conjunto de
hallazgos que cuentan, cada uno como (hecho, clase, subtipo); el hecho es el campo HL7, como `PV1-3`.

| | Microsoft | LinuxForHealth |
|---|---|---|
| Casos comparados | 368 | 368 |
| Diferencias | **0** | **0** |
| Casos que faltan en un lado o en el otro | 0 | 0 |
| Mensajes que la caja no pudo correr | 0 | 0 |
| Reintentos por tiempo vencido | 0 | 0 |
| Pares mínimos escritos para el conversor: `reproduce` igual a la confirmación de CV4 | 16 de 16 (se reproducen 14) | 18 de 18 (se reproducen 16) |
| Tiempo de la corrida, con los 68 mínimos | 233 s | 17 s |

La herramienta controlada es la que se publica: huella `1ea91cf28e2a2e83…`. El control se corrió tres veces, y las tres dan lo
mismo:
- la primera;
- otra tras cambiar una expresión regular de la comprobación del informe;
- otra tras los cambios de la revisión a ciegas: la imagen se valida y va tras `--`, la ayuda de cada opción y el código 2 para
  una carpeta de salida ocupada.

El guion es [`control_vc.py`](control_vc.py). El orden de los pasos pone primero el eslabón débil, y cada paso podía parar el
control.

## Paso 0: la caja no cambia al conversor

El conversor de juguete se corrió dos veces sobre seis mensajes de veredicto conocido: fuera de Docker y dentro de la caja
(imagen `python:3.12-slim`, adaptador [`juguete-docker.json`](juguete-docker.json)). **Los seis veredictos son iguales.** Si no
lo hubieran sido, el control se paraba aquí: la caja estaría alterando al conversor.

## Paso 1: las identidades, antes de correr nada

| Qué | Esperado (del estudio) | Medido |
|---|---|---|
| El juez | `40bbc3ef…` (CV4) | `40bbc3ef439a5f2a…` |
| Microsoft v7.0 | `766f8938…` ([`../PREVISION-CV2.json`](../PREVISION-CV2.json)) | `766f8938d0c12c38…` |
| LinuxForHealth v1.1.0 | `ac41f71b…` (ídem) | `ac41f71b98ee75ba…` |
| El corpus: adt, oru y muestras | `aa83359a…` y las 368 líneas de [`../CORPUS-CV2-MANIFIESTO.txt`](../CORPUS-CV2-MANIFIESTO.txt) | `aa83359aa283082f…`; 368 de 368 iguales |

La herramienta regenera el corpus del estudio por su cuenta: las ORU desde `bases_oru.py` y los mínimos desde
`cv3_minimos.py`. Las dos huellas de los conversores salen de la fórmula del estudio aplicada a las partes que declara cada
adaptador.

El control se corrió con el juez de CV4, el mismo del estudio. La copia pública tiene otra huella, `0dd3ae5c…`: se diferencia
solo por un extracto de un documento que el juez cita, no por su lógica (ver [`../../MANIFIESTO.txt`](../../MANIFIESTO.txt)).
Por eso los informes de [`ejemplos/`](ejemplos/) dicen `40bbc3ef…` en su cabecera. Corridos desde esta copia dirán `0dd3ae5c…`,
y todo lo demás debe coincidir: categorías, mecanismos y pares.

## Paso 2: las dos corridas, caso por caso

Cada adaptador se corrió con `--muestras` y `--comparar <juicio de CV4>`. Las dos corridas salieron con código 0, y las dos
comparaciones dan **0 diferencias**.

Las dos imágenes son las del estudio:
- Microsoft: `mcr.microsoft.com/dotnet/runtime:6.0`, `sha256:75752d6e…`;
- LinuxForHealth: `maven:3.9-eclipse-temurin-11`, `sha256:7bb84a45…`.

## Paso 3: lo que se comprueba desde lo público

- **Las categorías por corpus, frente a [`../RESULTADO-CV2.json`](../RESULTADO-CV2.json):**
  - **ADT y ORU:** iguales en los dos conversores.
  - **Muestras de LinuxForHealth:** iguales.
  - **Muestras de Microsoft:** salen 3 correctos y 25 fallos silenciosos, donde `RESULTADO-CV2.json` dice 2 y 26. Es lo que el
    diseño preveía. `RESULTADO-CV2.json` se escribió con el juez de CV2 (`be73697f`); después, en CV3 y CV4, se arreglaron
    falsos positivos del juez. Con el de CV4, la muestra LRI de Microsoft pasa a `correcto` (ver «Qué cambió en el juez» en
    [`RESULTADO-CONVERSORES.md`](../../RESULTADO-CONVERSORES.md)). Frente al juicio de CV4, el del paso 2, no hay diferencia.
- **Los pares mínimos**, cada uno con el conversor para el que se escribió:
  - **frente a lo público,** [`../RESULTADO-CV3-minimos.json`](../RESULTADO-CV3-minimos.json), juzgado con el juez de CV3
    (`54a90cd9`): coinciden 33 de 34. La excepción es el par `L16-cx-4-solo-nombre`, la sonda de CX.4. Allí salía confirmado, y
    era el falso positivo del juez que CV4 arregló (L-24 en [`../RESULTADO-CV3.md`](../RESULTADO-CV3.md));
  - **frente a la confirmación de CV4,** que es privada (de ella sale [`../RESULTADO-15A.md`](../RESULTADO-15A.md)): coinciden
    los 34.

  Se reproducen 30 de 34. No se reproducen los pares `M03b-pda-en-a01`, `M06c-nte-al-final`, `L15-xtn-12` y
  `L16-cx-4-solo-nombre`.

## Paso 4: lo que obtiene un tercero desde el repositorio

Las muestras de los proyectos no viajan con el repositorio (L-VC-7). Por eso cada adaptador se corrió también sin ellas, con el
corpus del laboratorio y los 68 mínimos, que es lo que puede repetir cualquiera. Esos dos informes son los de
[`ejemplos/`](ejemplos/). Pasan la comprobación del propio informe: la frase de lo que no se sabe, ninguna palabra de contraste
fuera de ella y ninguna ruta de máquina.

## Lo que el control no puede mostrar desde aquí

- **El detalle por caso del estudio no es público** (L-VC-8). El paso 2 compara con él en la máquina del laboratorio. Desde el
  repositorio se pueden repetir, con los conversores construidos:
  - los pasos 0 y 4;
  - el 1, con las muestras de los proyectos tomadas de sus repositorios, porque las 65 líneas de muestras del manifiesto no
    viajan con este (L-VC-7);
  - el 3, con su ancla pública. Si falta el fichero privado de CV4, el guion lo avisa.

  El guion pide la ruta del juicio de CV4 como argumento, pero solo la lee el paso 2: sin él, vale cualquier fichero.
- **Una corrida es una corrida** (L-VC-11). No se comprobó que los conversores sean deterministas. Lo que sí se vio:
  - **Los veredictos se mantienen:** los conversores, corridos de nuevo por la herramienta el 24 y el 25-oct, dan los mismos
    veredictos que sus salidas del estudio, del 23-oct, juzgadas con el mismo juez.
  - **El texto de algunos errores de Microsoft no:** lleva identificadores aleatorios. Entre dos corridas cambia el texto de
    ese rechazo en el informe, y su veredicto no.
- **No se adjudicó nada**, porque no hubo nada que adjudicar. La tabla de adjudicaciones del diseño (§6) quedó sin usar.
