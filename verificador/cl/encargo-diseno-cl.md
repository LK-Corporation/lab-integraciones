> *Copia pública: las rutas de la máquina del laboratorio van cambiadas por las relativas a su raíz, su nombre por «la máquina del laboratorio», los nombres de sus cuadernos por «los cuadernos del laboratorio» y la carpeta de trabajo del diseñador por `<carpeta de trabajo>`; las carpetas temporales (`/tmp/…`) y el resto van literales.*

Eres el diseñador a ciegas de una etapa pequeña de un laboratorio de integración sanitaria (HL7 v2 → FHIR R4). Tu trabajo es DISEÑAR,
no programar ni publicar nada. Escribe en español.

## Contexto

El laboratorio publicó un estudio de dos conversores HL7 v2 → FHIR. Sus clases (nueva, ya declarada, convención…) las escribe
`cv/cv3_clases.py`, que aplica una regla por clase sobre el juicio del juez, caso a caso. El resultado publicado es
`cv/CLASES-CV3.json`.

La etapa 38 midió lo siguiente (no lo discutas; puedes comprobarlo):
- con el juicio del estudio (`privado/cv/cv3/juicio-rejuicio2.jsonl`, juez de CV3), el `cv/cv3_clases.py` de hoy reproduce el JSON
  publicado, y nada queda sin clase;
- el juez cambió en CV4 (`RESULTADO-CONVERSORES.md`, «Qué cambió en el juez»). Entre otras cosas, la descripción de Location que
  contiene PL.9 sin ser PL.9 pasa de un hallazgo «falta la descripción…» a uno «la descripción … contiene PL.9 … sin ser PL.9»
  (Q-CV-D-14);
- la regla de M-4 en `cv/cv3_clases.py` pide el texto «falta la descripción». Con el juicio del juez de hoy
  (`privado/jz/juicio-cv-despues.jsonl`, idéntico al de CV4 en los 736 casos), 8 hallazgos de Microsoft quedan sin clase y M-4 baja
  de 16 casos a 8;
- Jev decidió arreglar la regla de M-4 para que reconozca también el texto del juez de CV4 (`cl/decision-jev-cl.md`, con su estado
  `cl/estado_cl.md`).

Así se hizo con M-28 en la etapa 37: `jz/parche_m28_jz.py`, con un bloque 8 en el sello de la etapa 33 (`ga/SELLO-GA.txt`).

## Lo que puedes leer (en la máquina del laboratorio, desde la herramienta Bash, SOLO LECTURA)

- **Lo fijado:** `fase12/ANTES-ETAPA-CLASES.md`, `cl/estado_cl.md`, `cl/decision-jev-cl.md`. Empieza por aquí.
- **El aparato:** `fase12/cv/cv3_clases.py` (va en CRLF), `cv/juzgar_cv2.py` (`asignar`), `cv/cv3_mecanismos.py`
  (`firma`) y `cv/RESULTADO-CV3.md` (la tabla de clases, M-4).
- **Lo medido:** `cl/reproducir_clases_cl.py` y su salida, `cl/REPRODUCCION-CL.json`.
- **El precedente:** `jz/parche_m28_jz.py` y `ga/SELLO-GA.txt`.
- **Los juicios:** `privado/cv/cv3/juicio-rejuicio2.jsonl` y
  `privado/jz/juicio-cv-despues.jsonl`. Solo esos dos ficheros de `privado/`.

**NO leas nada más de `privado/`, ni los cuadernos del laboratorio.** No corras nada que escriba fuera de
`/tmp/disenador38/`. Si quieres probar algo, hazlo sobre una copia tuya de `fase12` en `/tmp/disenador38/`.

## Lo que tienes que entregar: un documento de diseño

Escríbelo con la herramienta Write en
`<carpeta de trabajo>\cl\diseno-cl-fable.md`.
Va a publicarse. No pongas rutas de la máquina; usa las relativas a la raíz del laboratorio.

Tiene que decir, breve:
1. **El cambio de la regla de M-4:** cuál, exactamente, y por qué no le quita ni le da casos a ninguna otra clase. Compruébalo sobre
   los dos juicios: con el del estudio, el JSON publicado se sigue reproduciendo; con el de hoy, M-4 recupera sus 16 casos y nada
   queda sin clase, y ninguna otra clase cambia salvo M-36 y L-24, por el juez.
2. **La prueba en rojo antes:** qué comprueba, dónde vive y por qué cae con la regla de hoy.
3. **El sello:** qué va en el bloque 9 de `ga/SELLO-GA.txt` y qué no se toca (el JSON publicado y los JSON de clases de etapas
   pasadas).
4. **Qué se dice en lo publicado:** dónde se marca (`cv/RESULTADO-CV3.md`, `RESULTADO-CONVERSORES.md`…) y qué afirmación publicada
   queda corta (por ejemplo, «M-4 es ya declarada en los dos jueces»), sin reescribir resultados sellados.
5. **Lo que no resuelves y por qué,** si algo.

Sé concreto. Nada de lo que propongas puede cambiar la frase del estudio (15 nuevas, 31 ya declaradas, 16 convenciones): si lo
hiciera, dilo y para.
