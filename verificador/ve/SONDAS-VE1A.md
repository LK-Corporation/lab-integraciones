> *Copia pública: la procedencia y el desglose por origen de la muestra privada del sitio están redactados (punto 4 de la revisión de la publicación). Los totales y el mecanismo son los del original.*

# VE1-a: las sondas antes de escribir pruebas ni código (22-oct-2026)

El diseño (`ve/diseno-verificador-ve-fable.md` §7) pone estas cuatro sondas en cabeza de VE1. **Las cuatro están
contestadas y ninguna regla de parada salta.** Víctor aceptó antes Q-VE-A-1..5 tal como se recomendaban
(`ve/decisiones-qve.md`).

El guion es `ve/ve1_sondas.py` (e1 a e4, y `limpiar`). El detalle está en `privado/ve/ve1a/`. Salvo E-VE1-2, todo fue de
solo lectura.

## E-VE1-2: ¿encuentra el FHIR de iris-ai un Encounter sin identifier por su paciente? **Sí, por `_lastUpdated`**

Se sembró un Encounter de sonda, sin identifier, con `subject` lógico (`subject.identifier`) y un sistema propio
(`urn:lab:ve1:sonda-mrn`) que no usa nada del laboratorio. Luego se borró por id.

| Vía (escalera del diseño §2.2) | Resultado |
|---|---|
| 1. `Encounter?subject:identifier=…` | **HTTP 400**: IRIS no admite el modificador `:identifier`. El control (otro valor) da lo mismo |
| — `Encounter?patient:identifier=…` (informativo) | HTTP 400 |
| 2. `Encounter?_lastUpdated=ge<t>` con filtro exacto en cliente por `subject.identifier` | **Funciona**: 1 devuelto, exacto, con el id de la sonda |
| 3. Barrido `Encounter?_count=100` | **HTTP 413 `too-costly` (`SearchTooCostly`)**: el almacén tiene 2.560 Encounter y la búsqueda sin filtro supera el límite del servidor |
| Limpieza | DELETE 204 y después GET 410. La segunda pasada de `limpiar` encuentra 0 |

**Para el lector (VE1-c):**
- La vía es la 2. La parte del lector de MMI-19 no pasa a L-VE-3.
- **El instante de partida** se toma del reloj del servidor, con la cabecera `Date` de un GET justo antes de enviar, que IRIS
  manda.
- **La ventana tiene que ser corta,** un mensaje cada vez, porque una ventana con más Encounter que el límite también da
  413. El 413 se declara como fallo de lectura (`fallos.paso = "busqueda"`), nunca como «ninguno».
- `subject:identifier` queda fuera. El censo previo y la limpieza por paciente usan la misma consulta por `_lastUpdated`,
  como pide el riesgo 1 del diseño.

**Incidencia de la sonda.** El primer intento leyó mal la cabecera `location` (IRIS la manda en minúsculas) y no borró el
Encounter que acababa de crear. `limpiar` lo encontró por su sistema propio, lo confirmó al releerlo por id y lo borró, y
la sonda borra ahora también en `finally`. No quedó ninguno.

## E-VE1-1: lotes con un AA sin fila de éxito y sin canónico. **0**

- Lotes con algún canónico: los mensajes sin canónico son **34, todos no AA**, en la regresión `adt_a01`. **0** con AA y sin
  fila de éxito, y 0 con AA y fila de éxito.
- La foto de la regresión: **0 instancias** cuentan hoy `fidelidad/sin_canonico`.
- **Para la previsión:**
  - la cota abierta de M12 es 0;
  - los 34 no AA conservan sus hallazgos de hoy, porque las ramas `trama` y `acuse/recuento` van delante en el manejador
    (§1.3 del diseño). VE2 lo comprueba con la foto.

## E-VE1-3: evidencia adt_fhir con PV1-2 = N o PV1-19 vacío

| Corpus | n (en A1, las aceptadas por el acuse) | PV1-2 = N | PV1-19 vacío (con visita) | Las dos | Candidatas |
|---|---|---|---|---|---|
| A1, lab | 136 | 3 | 86 | 10 | **99** |
| A1, sitio | 144 | 3 | 86 | 10 | **99** |
| Casos de los agentes | 9 | 0 | 7 | 1 | **8** |

**Para la previsión:**
- La evidencia exacta de A1 se regenera con el juez nuevo, y `almacen_sintetico` añade `visitas_por_paciente`. Así que en
  A1 salen **0 notas** L-VE-3, y las 86 con PV1-19 vacío pasan a compararse por contenido (Q-VE-D-4) y deben seguir
  `correcto`.
- Los 8 casos de los agentes son evidencia guardada sin `visitas_por_paciente`: **8 notas** L-VE-3 (N1, M19), sin cambio en
  N2 ni en N3.

## E-VE1-4: perfil del sitio, MSH-12 vacío, AA tolerado por S22, por campo

De 1.091 mensajes ADT distintos con MSH-12 vacío (A1 y la muestra privada del sitio):
- **PID-8: 39,** los mismos que contó VE-pre.
- **PV1-2, PID-30 y cualquier otro campo: 0.**

**Para la previsión:** la cota de MS9 es exactamente 39, todos en PID-8. La «clase no censada» del riesgo 2 del diseño es 0.

## Lo que pasa a la previsión de VE2 (§6.3 del diseño)

| Corpus | N3 | N2 | N1 |
|---|---|---|---|
| Regresión 2.721 | 0 | 0 | 0 |
| A1, lab y sitio (exacta, regenerada) | 0 en lab; en el sitio, MS9 sobre los de MSH-12 vacío con PID-8 fuera de la 0001, que en A1 son 0 | 0 | 0 notas L-VE-3 |
| Casos de los agentes (23) | 0 | 0 | 8 notas L-VE-3 |
| MS9 en total | ≤ 39, todos en PID-8, en el perfil del sitio con MSH-12 vacío | | |

**Siguiente: VE1-b.** Las pruebas P-VE-1..9, 12 y 13, escritas y en rojo con el juez de hoy, antes de cambiar código.
