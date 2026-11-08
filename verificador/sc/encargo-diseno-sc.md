> *Copia pública: las rutas de la máquina del laboratorio van cambiadas por las relativas a su raíz, su nombre por «la máquina del laboratorio», los nombres de sus cuadernos por «los cuadernos del laboratorio» y la carpeta de trabajo del diseñador por `<carpeta de trabajo>`; las carpetas temporales (`/tmp/…`) y el resto van literales.*

Eres el diseñador a ciegas de una etapa pequeña de un laboratorio de integración sanitaria (HL7 v2 → FHIR R4). Tu trabajo es DISEÑAR,
no programar ni publicar nada. Escribe en español.

## Contexto

El laboratorio publicó un estudio de dos conversores HL7 v2 → FHIR. Sus clases las escribe `cv/cv3_clases.py`, que aplica una regla
por clase sobre el juicio del juez, caso a caso, y lista en su salida lo que queda sin clase (`sin_clase`), sin fallar. El aparato
está sellado en la etapa 33 (`ga/SELLO-GA.txt`, bloques 1 a 9).

La etapa 39 midió lo sin clase de hoy (`sc/SINCLASE-SC.json`, de `sc/medir_sinclase_sc.py`), y Jev decidió dos cosas
(`sc/decision-jev-sc.md`, con su estado `sc/estado_sc.md`):
- **Q-SC-1 a:** en la versión 2 del corpus de la etapa 33, quedan 30 sin clase: las Observation de ACC de Microsoft en 30 ADT del
  corpus del laboratorio, que el juez cuenta como «recurso sin mapa». La etapa 36 las clasificó como M-28. La regla de M-28 reconoce
  ese mecanismo, pero solo en los casos que empiezan por `ms-ADT` (las muestras). Jev: que la regla de M-28 reconozca también el
  corpus del laboratorio para ese hallazgo, **sin que su otro mecanismo (MC-ORU-7) alcance otros corpus**;
- **Q-SC-2 b:** que el aparato no falle con lo sin clase, pero que avise al final y lo cuente en su salida, para que no pase sin
  verse.

Hay que tener en cuenta que lo sin clase es también un canal: `ga/comparar_ga.py` toma como candidatas nuevas lo que queda sin clase
en la versión 2 y no en la 1.

## Lo que puedes leer (en la máquina del laboratorio, desde la herramienta Bash, SOLO LECTURA)

- **Lo fijado:** `fase12/ANTES-ETAPA-SINCLASE.md`, `sc/estado_sc.md`, `sc/decision-jev-sc.md`. Empieza por aquí.
- **El aparato:** `fase12/cv/cv3_clases.py` (va en CRLF; mira `R`, `regla()` y `main()`), `cv/juzgar_cv2.py`
  (`asignar`), `cv/cv3_mecanismos.py` (`firma`) y `cv/RESULTADO-CV3.md` (M-28).
- **Lo medido:** `sc/medir_sinclase_sc.py` y `sc/SINCLASE-SC.json`; y `RESULTADO-CANDIDATAS.md` (la etapa 36, M-28).
- **Quién usa el aparato:** `ga/comparar_ga.py`, `ga/cifras_ga_b.py`, `ga/cruce_ga.py`, `ga/riesgo_ga.py`, `cv/ar/arrastre.py`
  (`juzgar_arbol`) y `cl/reproducir_clases_cl.py`.
- **Los precedentes:** `jz/parche_m28_jz.py` y `cl/parche_m4_cl.py`, con los bloques 8 y 9 de `ga/SELLO-GA.txt`, y la prueba
  `cv/prueba_cv3_clases.py`.
- **Los corpus,** solo para medir: `privado/ga/corridas/comparacion/arbol-v1` y `arbol-v2`, y
  `privado/cv/cv2/ev` con su juicio, `privado/jz/juicio-cv-despues.jsonl`. Nada
  más de `privado/`.

**NO leas los cuadernos del laboratorio.** No corras nada que escriba fuera de `/tmp/disenador39/`. Si quieres
probar algo, hazlo sobre copias tuyas en `/tmp/disenador39/` (de `fase12` y de los árboles).

## Lo que tienes que entregar: un documento de diseño

Escríbelo con la herramienta Write en
`<carpeta de trabajo>\sc\diseno-sc-fable.md`.
Va a publicarse. No pongas rutas de la máquina; usa las relativas a la raíz del laboratorio.

Tiene que decir, breve:
1. **El cambio de M-28:** cuál, exactamente, y por qué el hallazgo de ACC del corpus del laboratorio cae en M-28 y MC-ORU-7 no
   alcanza otros corpus. Mídelo: con el juicio de hoy del estudio, las clases no cambian; en la versión 2 con el juez de hoy, lo sin
   clase pasa de 30 a 0 y solo cambian los casos de M-28; en la versión 1, nada.
2. **El aviso:** qué escribe el aparato (en su salida JSON y al final de su ejecución) cuando queda algo sin clase, y qué no cambia
   (el código de salida, el canal de `ga/comparar_ga.py`, los guiones que lo llaman sin consola).
3. **La prueba en rojo antes:** qué comprueba, dónde (por ejemplo, ampliando `cv/prueba_cv3_clases.py`) y por qué cae hoy.
4. **El sello:** qué va en el bloque 10 de `ga/SELLO-GA.txt`, y qué no se toca (los JSON de clases publicados y los de etapas
   pasadas).
5. **Qué se dice en lo publicado:** dónde se marca (`cv/RESULTADO-CV3.md`, `RESULTADO-CANDIDATAS.md`, `RESULTADO-GENERADORES.md`…),
   sin reescribir resultados sellados. Ten en cuenta que la frase de la versión 2 da hoy 17 convenciones con el juez de hoy, y que
   la 33 publicó 16 con el de entonces.
6. **Lo que no resuelves y por qué,** si algo.

Sé concreto. Nada de lo que propongas puede cambiar la frase del estudio (15 nuevas, 31 ya declaradas, 16 convenciones, sobre el
estudio): si lo hiciera, dilo y para.
