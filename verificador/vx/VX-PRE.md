# VX-pre: el eslabón débil de la etapa 20 (25-oct-2026)

Antes del diseño, de solo lectura salvo E-VX-3, que corrió los conversores en la caja sin juzgar.

| Sonda | Resultado |
|---|---|
| E-VX-1 | **Pasa por los ConceptMap; la cita por fila la cierra el diseño.** Los ConceptMap de la guía mapean RXA-3 a `occurrenceDateTime`, RXA-5 a `vaccineCode` y RXA-20 a `status`: los tres de la regla de parada. El mapa de RXA tiene 18 elementos; el de RXR, 2; el de ORC hacia Immunization, 13; el del mensaje, 39 |
| E-VX-2 | **Contestada.** Ninguna muestra pública está en v2.5, así que el juez no juzgará la legalidad de sus códigos (L-CV-1) y el corpus principal tiene que ser sintético y en v2.5. Las muestras quedan como corpus secundario (`privado/vxu/muestras/`): <br>- **Microsoft:** 4 mensajes VXU, 2 en v2.5.1 y 2 en v2.8. Sus bytes son los de v7.0 (`253307f`). <br>- **LinuxForHealth:** no publica ficheros .hl7 de VXU. Los 79 mensajes (81 tras re-extraerlos en VX2-c, `vx/VX2.md`) se sacaron de los literales de sus pruebas Java (v1.1.0): 39 en v2.6, 39 en v2.5.1 y 1 en v2.3. La extracción pegaba cadenas de comentarios en al menos 2; está pedido rehacerla |
| E-VX-3 | **Pasa.** Los dos conversores corren VXU en la caja con sus adaptadores tal cual: 4 de 4 Bundles cada uno. Con la herramienta de hoy, los VXU van a `adt_conv` y salen fuera de alcance, como se esperaba |
| E-VX-4 | **Contestada.** Está en `privado/vxu/contraste/INVENTARIO.md`, que no se le pasa al diseñador. <br>- **Microsoft** publica salidas esperadas de VXU_V04. <br>- **LinuxForHealth** no publica salidas esperadas; lo que espera lo afirma dentro de sus pruebas. <br>- **Issues y PR sobre VXU e Immunization:** 43 de LinuxForHealth y 4 de Microsoft, con sus comentarios guardados |

## Las hojas de la guía

- **Las de VXU:** se trajeron del repositorio `HL7/v2-to-fhir`, commit `873b331` (CC0), con su sha256 en
  `privado/vxu/guia_csv/FUENTES.txt` (`vx/traer_guia_vxu.py`). Son las de VXU_V04, RXA, RXR, ORC y PD1 hacia sus recursos, y
  las dos de NK1.
- **Las que ya usaba el juez** (PID, PV1, OBX) son idénticas a las de ese commit.

## La caja del diseño

`vx/caja_vx0.py` monta `/tmp/vx0`: 322 ficheros. El escáner de cajas la da LIMPIA.
- **Qué lleva:** el juez, sus pruebas y lo que declara; el ANTES, el diseño y las decisiones del estudio; HL7 v2.5 (capítulos
  2, 2A, 3, 4 y 7); los perfiles FHIR R4 que hacen falta; y la guía (ConceptMap y hojas).
- **Qué no lleva:** nada de lo que devuelven los conversores, ni sus plantillas, ni sus muestras, ni el contraste ni los pares
  mínimos del estudio. El guion para si encuentra algo de eso.
