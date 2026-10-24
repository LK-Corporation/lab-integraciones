# Licencias

Lo que es obra del autor lleva **dos licencias**, porque tiene dos clases de contenido: el código y los documentos. Lo que
no es suyo va con la licencia de sus autores (las fuentes tipográficas) o no lo cubre ninguna (el material de HL7, abajo).

| qué | licencia | dónde |
|---|---|---|
| **El código** | **MIT** | `codigo/`, y cualquier `.py`, `.cls`, `.java`, `.gradle` o `.xml` en cualquier carpeta | 
| **Los documentos** | **CC BY 4.0** | `INFORME.md`, `README.md`, `diseno/`, `encargos-y-revisiones/`, `preinscripciones/`, `medidas/`, la página `docs/index.html`, y cualquier `.md`, `.txt`, `.html` o `.sha256` |
| **La configuración y las pruebas** | **MIT** | `tests/`, `.github/`, `pytest.ini`, `.gitignore`, y cualquier `.yml` o `.ini` |
| **Los datos del verificador** | **CC BY 4.0** | los `.json` de `verificador/`: las bases sintéticas de sus pruebas, las tablas de su rejuicio y los agregados del estudio de conversores, salvo lo que es de HL7 (abajo) |
| **Las fuentes tipográficas** | **SIL OFL 1.1**, de sus autores | [`docs/fonts/`](docs/fonts/): Newsreader, Public Sans y JetBrains Mono, con su licencia al lado (`OFL-*.txt`) |

Los textos completos están en [`LICENSES/MIT.txt`](LICENSES/MIT.txt) y
[`LICENSES/CC-BY-4.0.md`](LICENSES/CC-BY-4.0.md).

Identificadores SPDX: `MIT` para el código, la configuración y las pruebas; `CC-BY-4.0` para los
documentos; `OFL-1.1` para las fuentes, que no son obra del autor.

---

## Qué significa en la práctica

**El código** puedes usarlo, copiarlo, modificarlo y redistribuirlo, también con fines comerciales,
conservando el aviso de copyright. Sin garantía de ninguna clase.

**Los documentos** puedes compartirlos y adaptarlos, también con fines comerciales, **citando la
fuente**: el autor, un enlace a este repositorio, y si los has modificado, decirlo.

---

## Sobre las revisiones externas

La carpeta [`encargos-y-revisiones/`](encargos-y-revisiones/) contiene respuestas generadas por
modelos de lenguaje de terceros a encargos escritos por el autor. Se publican **tal cual salieron**,
con su cabecera de procedencia —modelo, vía, encargo, tiempo y tokens— para que pueda comprobarse
que lo citado es lo que contestaron.

Se incluyen como parte del registro del método, no como obra propia. El autor licencia bajo CC BY
4.0 **su parte**: los encargos, la selección, la organización y todo lo que escribió alrededor.

---

## Sobre el material de HL7

El verificador juzga contra HL7 v2.5 y necesita algunos de sus datos para correr. **No son obra del autor y estas licencias no
los cubren:**

- [`verificador/medida/encargo_medida.md`](verificador/medida/encargo_medida.md): las filas de las tablas 0003, 0004 y 0211,
  tal cual. En el laboratorio, ese fichero lleva el capítulo 2 del estándar entero, que no se publica;
- [`verificador/estructuras_25.json`](verificador/estructuras_25.json): las estructuras de mensaje y los atributos de los
  segmentos de v2.5;
- [`verificador/a1/ejemplos_cap3.json`](verificador/a1/ejemplos_cap3.json): el principio de algunos mensajes de ejemplo del
  capítulo 3;
- los códigos de tabla y las citas breves del estándar que el código del verificador lleva con su referencia;
- los mapas (ConceptMap) de la guía HL7 v2-to-FHIR que [`verificador/conversion.py`](verificador/conversion.py) lleva
  como datos. Están generados del paquete `hl7.fhir.uv.v2mappings` 1.0.0, que HL7 publica bajo CC0-1.0. Las hojas CSV de
  la guía (`HL7/v2-to-fhir`, Apache-2.0) solo se citan, por fichero y línea; no se copian.

El texto completo del estándar se obtiene de HL7 International, con su licencia. HL7® y FHIR® son marcas registradas de
Health Level Seven International.

---

## Sobre lo que no está

Este repositorio es una selección. El catálogo de operadores, las tablas de casos y los programas
que los generan **no se publican** —ver el [README](README.md)— y no están cubiertos por estas
licencias porque no están aquí.

Tampoco están los conversores que juzga el estudio de conversores: Microsoft FHIR-Converter (MIT) y LinuxForHealth
hl7v2-fhir-converter (Apache-2.0). Aquí hay solo sus versiones, sus huellas y el arnés propio que los corre.

---

Copyright © 2026 LK-Corporation
