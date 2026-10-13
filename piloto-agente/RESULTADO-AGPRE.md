# RESULTADO AG-pre: el eslabón débil del piloto del agente, 12-oct-2026

`ANTES-PILOTO-AGENTE.md` (fijado en `56f2f4f`). Se probaron dos casos de punta a punta, uno en cada caja:
1. el verificador falla;
2. un agente mínimo (subagente de Claude, carpeta cerrada y MCP del verificador) localiza la causa y propone un parche;
3. el arnés aplica el parche en la caja, sin tocar git;
4. el verificador vuelve a juzgar los casos que fallaban y una regresión.

## Los dos casos

| | Mirth (H) | IRIS (R) |
|---|---|---|
| Caso | **H-MI-1:** el nulo `""` de PV1-4/10/14/36 llegaba como código al canónico y al Encounter. Es un fallo real del 12-oct, reintroducido en una copia del canal | **R5:** con PV1 antes de PID, el circuito congelado contesta AR 101 y debe ser AE 100. Es un fallo vivo (`CONOCIDOS-ANTES-DEL-SELLO.md`) |
| Caja | Contenedor Mirth efímero (`mirth/agpre.py`) | Namespace LABMUT (`mirth/agpre_iris.py`, sobre `mutacion.py`), con `a_user()` en el `finally` |
| Lo que ve el agente | El veredicto de 1 caso (PV1-4) y la fuente del canal | El veredicto de 1 caso y las 10 clases del circuito |
| Casos que fallan | 11 de 263 | 5 de 5 disparadores; la regresión da 60 de 60 `correcto` |
| Localización | Las líneas del fallo (paso_2_canonico.js:123-126) | La DTL, `MotivoRechazo()` y la operación FHIR. El fallo es una ausencia: no hay comprobación de estructura |
| Parche | Envolver los 4 campos en `T()`. Es distinto del arreglo de referencia (que solo trataba `""`) y más amplio | Comprobación de estructura en la DTL, una propiedad nueva en el canónico con su `Storage`, `MotivoRechazo()` con AE 100, y la operación toma MSA-1 y el texto del motivo. **Toca 3 clases y compila** |
| **Medida** | **Arregla 11 de 11; colateral 0 en 252** | **Arregla 5 de 5; colateral 0 en 60** |
| Controles del evaluador | Parche vacío: 0 de 11. Arreglo de referencia: 11 de 11 | Parche vacío: 0 de 5 |
| Coste | ~115 mil tokens, 2 minutos, 14 llamadas | ~155 mil tokens, 3,8 minutos, 16 llamadas |

Tras el caso IRIS, USER volvió a quedar en marcha, con la huella del congelado intacta y la sonda en AA, y LABMUT con sus
clases base recargadas.

**Regla de AG-pre: pasa.**
- La tarea cabe en un subagente.
- Los dos arneses aplican un parche ajeno en su caja, lo compilan si hace falta y lo miden con el verificador, sin tocar git
  ni USER.
- Los evaluadores discriminan: el parche vacío no arregla nada y el de referencia lo arregla todo.

Lo que no mide AG-pre:
- **Si el agente aporta.** Dos casos no dicen nada contra la referencia sin modelo, que aún no existe. AG-pre solo prueba que
  la cadena funciona.

## Lo que AG-pre obliga a cambiar o decidir en el diseño (AG0)

1. **Huella de la reconstrucción (fuga).** Al reintroducir el fallo H-MI-1 quedó una línea con sangría sobrante. El agente lo
   vio («la línea 123, con sangría anómala»), y es una pista que un fallo real no tiene. **El corpus H tiene que reconstruir el
   árbol exacto de antes del arreglo** (`git show <arreglo>^:<fichero>` para todo el circuito), no editar la versión actual.
2. **La salida grande del MCP sale de la caja.** `info_verificador` no cabe en la respuesta y la herramienta la guardó en un
   fichero fuera de la carpeta. El agente lo leyó con grep. Hay dos salidas: darle en la caja una copia de lo que necesite, o
   quitarle esa herramienta.
3. **El agente usa al juez como oráculo.** Los dos pasaron variantes construidas por `acuse_esperado` y `verificar_caso` antes
   de proponer: uno ocho, otro unas pocas. Es una capacidad real que la búsqueda sin modelo no tiene. El diseño debe decidir si
   la referencia también puede consultar al juez (por ejemplo, sondas sistemáticas por campo) para que la comparación sea
   justa, y declararlo.
4. **Los parches buenos no se parecen al de referencia.** H-MI-1 se arregló de otra forma (más amplia) y R5 no tiene diff de
   referencia. La aceptación debe ser la del verificador (como fijó Q-AG-2), y la localización necesita una regla de
   adjudicación para R y para los parches que tocan varios sitios.
5. **Coste.** Unos 115-155 mil tokens por caso. Con 70 casos y 2 réplicas serían unos 20 M de tokens de subagente. El diseño
   debe ajustar casos y réplicas al tope (Q-AG-7) o proponer otro reparto.
6. **El MCP de esta sesión enseña el enum de puntos de entrada sin `adt_fhir`**, aunque el servidor lo acepta: está viejo.
   Hay que reconectar el MCP antes de AG2.
7. **Un parche puede cambiar el `Storage` de una clase persistente.** En la caja da igual, pero la restauración tiene que
   recargar la clase base y comprobarlo, como hace `restaurar_todo`.

## Siguiente

**AG0:** el diseño de Fable, a ciegas de los arreglos de H, con estos 7 puntos como entrada. Después, las Q a Jev.
