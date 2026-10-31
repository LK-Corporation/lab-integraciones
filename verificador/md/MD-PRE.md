# MD-pre: el eslabón débil de la etapa 26 (31-oct-2026)

Antes del diseño. Todo es de solo lectura salvo E-MD-3, que corrió los conversores en la caja sin juzgar.

| Sonda | Resultado |
|---|---|
| E-MD-1 | **Pasa.** Las hojas dan fila con destino para los cuatro campos de la regla de parada: TXA-2 → `type`, TXA-12 → `masterIdentifier`, TXA-17 → `docStatus` y OBX-5 → `content`, según OBX-2. ED va a `attachment`; FT, con `text/hl7v2`; RP, a `url`; y TX, a `data` con `application/text`. <br>Hay dos huecos que decide el diseño: **TXA-2 y TXA-17 no traen mapa de vocabulario** en las hojas, y TXA-19 lleva una condición: «AV» da `current`, y «CA», «OB» y «UN» van a una extensión. <br>Los ConceptMap del paquete 1.0.0 dicen lo mismo, con 15 elementos en TXA → `DocumentReference` y 6 en OBX |
| E-MD-2 | **Contestada. Ninguna muestra pública está en v2.5,** así que el corpus principal tiene que ser sintético y en v2.5, como en VXU. Las muestras quedan como corpus secundario, en `privado/mdm/muestras/`: <br>- **Microsoft:** 11 mensajes MDM (`data/SampleData/Hl7v2`, v7.0, `253307f`). De T02 hay 3: 2 en v2.8 y 1 en v2.3. Los otros 8 son T05, T06, T09 y T10. <br>- **LinuxForHealth:** no publica ficheros .hl7 de MDM. Sus 64 mensajes salen de los literales de sus pruebas Java (v1.1.0), todos en v2.6: 35 de T02 y 29 de T06. Se sacaron con `md/extraer_mdm_lfh.py`, que ignora los comentarios y concatena los literales de cada sentencia. Las pruebas parametrizadas pasan MSH-9 por una variable de `@ValueSource`, y sale un mensaje por valor. No queda ninguna variable sin resolver ni ningún duplicado |
| E-MD-3 | **Pasa.** Los dos conversores corren MDM_T02 en la caja, con sus adaptadores tal cual: **38 de 38 Bundles cada uno** (3 de Microsoft y 35 de LinuxForHealth). <br>En los demás eventos, LinuxForHealth da error en T05 y T09, que no tienen plantilla en su proyecto, y en los dos T10 de v2.8. Microsoft da Bundle en los 75. <br>Con la herramienta de hoy, los MDM van a `adt_conv` y salen fuera de alcance, como se esperaba (`privado/mdm/mdpre/`) |
| E-MD-4 | **Contestada.** Está en `privado/mdm/contraste/INVENTARIO.md`, que no se le pasa al diseñador. <br>- **Microsoft** publica salidas esperadas de MDM_T02 (3) y de los otros eventos. <br>- **LinuxForHealth** no publica salidas esperadas; lo que espera lo afirma en cuatro ficheros de pruebas. <br>- **Issues y PR que nombran MDM, `DocumentReference` o TXA:** 28 de LinuxForHealth (21 PR) y 4 de Microsoft (2 PR), con sus comentarios guardados |

## Las hojas de la guía

- **Las de MDM:** se trajeron del repositorio `HL7/v2-to-fhir`, commit `873b331` (CC0), con su sha256 en
  `privado/mdm/guia_csv/FUENTES.txt` (`md/traer_guia_mdm.py`). Son doce:
  - el mensaje MDM_T02;
  - TXA hacia `DocumentReference` y hacia `Provenance`;
  - OBX y NTE hacia `DocumentReference`;
  - ORC y OBR hacia `ServiceRequest`;
  - EVN hacia `Provenance`;
  - ED y RP, hacia `DocumentReference` y hacia `Attachment`.
- **Las que ya usaba el juez** (PID, PV1 y OBX) son idénticas a las de ese commit.

## La caja del diseño

`md/caja_md0.py` monta `/tmp/md0`, con 340 ficheros.
- **Qué lleva:**
  - el juez, sus pruebas y lo que declara, con `bases_oru.py` y `bases_vxu.py` como ejemplo;
  - los ANTES, los diseños y las decisiones de los estudios de conversores y de VXU;
  - HL7 v2.5, capítulos 2, 2A, 3, 4, 7 y 9;
  - los perfiles y ValueSet de FHIR R4 que hacen falta;
  - la guía: los ConceptMap y las hojas.
- **Qué no lleva:** nada de lo que devuelven los conversores, ni sus plantillas, ni sus muestras, ni el contraste ni los pares
  mínimos de los estudios. El guion se para si encuentra algo de eso.
