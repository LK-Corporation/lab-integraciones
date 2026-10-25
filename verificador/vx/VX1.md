# VX1: el punto `vxu_conv` en el juez (etapa 20)

**Qué hay.** El diseño es `vx/diseno-vx-fable.md` y las decisiones son las de Jev (`vx/decisiones-qvx.md`).

- **La gramática.** `VXU_V04` está en `estructuras_25.json`, extraída de `ch04.md:7288` (VX1-a).
- **El punto de entrada.** `vxu_conv` está en `puntos_entrada.py`, debajo de `oru_conv` (§2.1).
- **El juez de VXU.** Vive en `conversion_vxu.py`, que solo usa la biblioteca estándar. Tiene los grupos ORDER, el emparejamiento de §2.2, el perfil de §3, las tablas de §3.4 comprobadas contra el paquete, `PERFIL_GUIA_VXU`, `S_VX`, `L_VX` y `AMB_VX`.
- **Los ganchos.** Hay cinco, en `conversion.py`, aplicados con `vx/parche_conversion_vxu.py`.
- **El servidor MCP.** `mcp_verificador.py` gana `perfil_guia_vxu`, pasa a `SERVIDOR` 1.3 y nombra `vxu_conv` en las descripciones (`vx/parche_pe_mcp_vxu.py`).
- **Las pruebas.** Están en `prueba_conversion_vxu.py`: P-VX-1..23, en rojo antes del código (`c136b7d`).

**Lo que no cambia.** El rejuicio (`vx/rejuicio_vx.py comparar`) da 0 diferencias en las 1.008 evidencias del estudio. `prueba_conversion.py` pasa sus 28 pruebas sin editarla. `ve/comprobar.sh` sale verde, con la regresión de 2.721 en CASA.

## Desviaciones declaradas (DV-VX-n)

| DV | Qué | Por qué |
|---|---|---|
| DV-VX-1 | `prueba_multitipo.py` salta las estructuras sin punto de acuse. | `VXU_V04` solo entra por `vxu_conv`, que no tiene acuse (VX1-a). |
| DV-VX-2 | `conversion_vxu` registra al importarse sus claves de cita en `conversion.C` (solo claves nuevas: RXA, RXR, ORC, NK1, PD1) y su INFO en `conversion.INFO["vxu"]`. `conversion.py` lo importa al final. | Las funciones de `conversion.py` que se reutilizan (`_fecha`, `_sujeto`, `_observacion`…) citan por la clave del hecho. Las claves PID, PV1 y OBX ya son de ADT u ORU, y no se tocan. Para ellas, `conversion_vxu` pasa sus citas de VXU explícitamente y corrige la del Patient ausente. La autoprueba comprueba que ninguna clave choca. |
| DV-VX-3 | Si al `coding` de RXA-5 le falta el system de CVX, el hallazgo es `dato_perdido`. Un system distinto, por ejemplo el OID de CVX, es `codigo_mal_mapeado`. | Es la regla de `CV._codigo` para LN, SCT y UCUM. La tabla de §7 (P-VX-3) decía `codigo_mal_mapeado` también para el system ausente; se mantiene la clase del juez. Q-VX-D-1 (fijar) decide que un system distinto cuenta. |
| DV-VX-4 | `prueba_multitipo.py` fija la lista de puntos de entrada de `info_verificador`, que gana `vxu_conv`. | Es lo mismo que hizo DV-CV-6 con `adt_conv` y `oru_conv`. |
| DV-VX-5 | `cv/prueba_vc.py` p06 cuenta 40 casos más en el corpus del laboratorio (`vxu`): 303 → 343 sin mínimos. | Es el cambio declarado en §6 del diseño. Los ficheros de `adt` y `oru` y sus huellas no cambian (P-VX-21). |

## Lecturas tomadas al programar (el diseño callaba)

- **Encounter sin PV1.** Es `recurso_inventado` (hecho PV1). Una `Immunization.encounter` que apunta a él es nota, porque ya cuenta el Encounter. Una que no apunta a nada, sin PV1, es `dato_inventado` (hecho PV1-19).
- **`recorded` sin fuente.** Si no hay ni ORC-9 ni RXA-22 con A, y el valor tampoco es RXA-22, el hecho es ORC-9 (la fuente por omisión de la regla de Jev).
- **Dos Encounter con PV1.** Se emparejan como en `adt_conv`: si no se distinguen ni por identifier ni por subject, el resultado es `indeterminado/emparejamiento`.
- **Código fuera de la tabla, sin coding.** En la ruta o el sitio, un código fuera de la tabla y sin `coding` en la salida es silencio, como en `CV._codigo_tabla`.
- **Hecho del NK1 ausente.** Es `NK1(k)-2`, como dice §2.2.

## Pruebas retocadas después del commit en rojo y antes del código

Siguen en rojo con el código de entonces.

- **P-VX-3.** El control sin system pasa a esperar `dato_perdido` (DV-VX-3), y se añade el control con el OID (`codigo_mal_mapeado`).
- **P-VX-15.** El NK1 ausente pasa a esperar el hecho `NK1-2` (§2.2).
- **P-VX-16.** El Encounter de la prueba es coherente con su PV1: PV1-2 O, AMB e in-progress. Se separan dos casos: `encounter` sin PV1 y sin Encounter, que es `dato_inventado`; y un Encounter sin PV1, que es `recurso_inventado`. Los dos Encounter de la prueba se distinguen por identifier.
- **P-VX-19.** El caso de `dato_inventado` usa `statusReason` (0..1), porque `reasonCode` es repetible y da nota. El Patient duplicado lleva otro identifier; con el mismo, el juez lo da por ambiguo.

## VX1-e: los primeros Bundles reales

Las ocho salidas de VX-pre (los dos conversores sobre las cuatro muestras VXU de Microsoft, `privado/vx/vxpre/`) se rejuzgaron con
`vxu_conv`. El emparejador lee todas. Aparecieron dos defectos del juez, no de los conversores; cada uno tiene una prueba nueva,
que fue roja antes del arreglo:

- **Observation emparejada con el grupo equivocado.** Un OBX sin Observation propia se llevaba, por código, la Observation de otro
  grupo que traía ese código en CE.4. Microsoft lo hace en VXU-V04-02. Ahora se empareja primero todo por partOf y después por
  código, y por código quedan al final las que son parte de otra Immunization (P-VX-14).
- **RelatedPerson de GT1 e IN1.** La guía también crea RelatedPerson desde GT1 e IN1, y Microsoft lo hace. Esos segmentos no se
  juzgan (L-VX-10): sus RelatedPerson sobrantes son nota `fuera_proyeccion` hasta tantos como GT1 + IN1. Con GT1 o IN1 en el
  mensaje, un RelatedPerson ya no ocupa por orden el sitio del NK1 (P-VX-15).

Con el juez arreglado, lo que queda en esas ocho salidas es conducta de los conversores, y se adjudica en VX3:

- RXA-6 = 999 sin doseQuantity, la convención de los CDC (L-VX-9).
- OBX absorbidos sin Observation (Q-VX-D-4).
- Systems propios para CVX, MVX y el sitio.
- `primarySource` por omisión (Q-VX-D-7).
- Linuxforhealth sin Immunization en los mensajes 2.8.

## VX2a: la herramienta y el corpus

**El corpus.** `bases_vxu.py` trae las 40 bases de §4.2. Su autoprueba comprueba siete cosas:

- que cada base se lee y da la estructura `VXU_V04`, sin segmentos ausentes ni fuera de orden;
- que los TS y NM son válidos;
- que RXA-20/21 y RXR-1/2 están en sus tablas o son locales declarados;
- que los apellidos son de la lista cerrada;
- que solo hay texto no ASCII con MSH-18 UTF-8;
- la firma: todo par de bases difiere en 3 o más campos, sin contar MSH-7 ni MSH-10;
- la cobertura frente a `PERFIL_GUIA_VXU`, y la huella del conjunto, fijada en `5734cc3b9d6d`.

**La herramienta** (`vx/parche_vc_vxu.py`):

- `punto()` lleva VXU a `vxu_conv`;
- `CORPUS` gana `vxu`, y `L-VC-2` lo dice;
- el juguete escribe el nominal de VXU y gana `JUGUETE-RUTA`.

Las 23 pruebas P-VX están en verde.

**Robustez.** Se juzgaron las 40 bases con tres salidas: un Bundle vacío, el genérico del juguete y un `error`. No hubo ninguna
excepción. Apareció un defecto más del juez, con prueba roja antes del arreglo (P-VX-18): una ruta local declarada
(`JET^…^L`, base B29) se trataba como valor imposible, y un `error` sobre ella salía como rechazo aceptable. Ahora solo es
imposible un código fuera de la 0162 sin sistema o con HL70162.
