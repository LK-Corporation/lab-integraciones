# Etapa 21: las decisiones de Jev y las desviaciones del programador

El diseño es `diseno-ar-fable.md` (Fable, a ciegas). Las cuatro preguntas de su §8 se pasaron a Jev con un estado neutro
(`estado_qar.md`, `preguntas_qar.json`); la respuesta está en `decision-jev-qar.md`.

## Las decisiones (Q-AR-D)

| Pregunta | Jev | Confianza | Recomendación del diseñador | Qué cambia en el aparato |
|---|---|---|---|---|
| Q-AR-D-1, umbral de ruido de veredicto | **cero** | 0,95 | hasta el 2 % | `arrastre.UMBRAL = 0.0`: cualquier caso con veredicto distinto entre dos corridas del mismo modo para la etapa (regla de parada 2) |
| Q-AR-D-2, cómo entran las correcciones si cambia algo | **en sitio**, con fe de erratas | 0,23 | ficheros nuevos y la página apunta a ellos | solo si K > 0: se corrigen las filas publicadas con marca de erratum y el valor original, y la página se regenera |
| Q-AR-D-3, el adaptador de referencia después | **según el resultado** | 0,77 | igual | con K = 0 sigue el de lote; con K > 0 pasa a serlo el de mensaje |
| Q-AR-D-4, diferencias de Bundle sin cambio de veredicto | **no se miden**, salvo para el ruido | 0,45 | aislar, acotado | el nivel B queda para medir el ruido (la máscara) y para comprobar que ve el `manufacturer` de VL11; no hay sección «lo que el juez no ve» ni se aísla ninguna |

## Las desviaciones (DV-AR-n)

- **DV-AR-1.** `control_ar.py` gana `--hasta N`, y su `main` admite un `git` y una `carpeta_ar` inyectables. Sirven para que
  P-AR-12 compruebe sin Docker y sin un repositorio de verdad que, con el sello en un commit, el control lanza L1, y que sin él
  sale con 7 sin lanzar nada. La prueba usa `--desde 6 --hasta 7`.
- **DV-AR-2.** `arrastre.juzgar_arbol(arbol)` envuelve las dos llamadas del §6.2, paso 3 (`cv3_minimos.juzgar` y
  `cv3_clases.main`), sin tocarlas, con `sys.argv` guardado y restaurado.
- **DV-AR-3.** Las rutas de `SELLO-AR.txt` son relativas a la carpeta del sello, `cv/ar/`, y no a la del juez como en
  `cv/SELLO-CV2.txt`.
- **DV-AR-4.** Por Q-AR-D-4, `COMPARACION-AR.json` no lleva la sección `bundle` del §3.4, ni `pares_minimos`. El cambio de los
  pares mínimos se ve en el recálculo (`minimos.*` de `CIFRAS-AR.json`).
- **DV-AR-5.** `arrastre.py comparar` devuelve 0 en cuanto escribe `COMPARACION-AR.json`, aunque el positivo VXU no salga; lo
  deja en `controles.positivo_vxu`, y es `control_ar.py` quien sale con 5. Así lo pide P-AR-12, cuyas filas no traen los 23 de F7.
- **DV-AR-6.** El §5.4 (los casos de caja que se corren solos tres veces) no está automatizado: un caso de caja se lista en
  `COMPARACION-AR.json` y, si aparece, se trata a mano y se declara. `RUIDO-AR.json` no pasa si alguna corrida tiene
  `sin_evidencia`.
- **DV-AR-7.** Las identidades comprueban la orden del primer grupo del adaptador mensaje con el primer caso del corpus:
  `Arnes /in /salida /in/A01-001.hl7`.
- **DV-AR-8.** El recálculo copia la corrida de Microsoft del control de la etapa 18 a `<salida>/MS` y la rejuzga allí con
  `--desde-evidencias`, para no tocar la original.
- **DV-AR-9.** `regla_parada` cuenta una sola vez un caso que cambia en los dos modos.
- **DV-AR-10.** `positivo_vl11` exige, además de lo del §4.1, que las dos repeticiones salgan. La comprobación del nivel B
  (`manufacturer` en el `diff_bundles` de 2-L11b) se hace sobre la primera.
- **DV-AR-11, después del sello y del primer paso 9 (25-oct).** El positivo VXU (§4.1, P+2) no salió con el criterio del
  diseño. Los casos VXU que cambiaban eran exactamente VXU-B18 a VXU-B40, y en todos solo se perdía en lote el fabricante. Pero
  en tres de ellos (B33, B34 y B35, con varias vacunas en el mismo mensaje) el juez nombra el hallazgo del grupo n como
  `RXA(n)-17`, y el criterio pedía literalmente `RXA-17`. Era un defecto de la especificación, no del aparato, que sí veía el
  arrastre.
  - Se arregló por la regla de parada 1: se declara y se arregla el aparato. Primero la prueba en rojo, P-AR-13, en su propio
    commit. Después el cambio: `positivo_vxu` admite el RXA-17 de cualquier grupo, solo con `dato_perdido` y nada mensaje a
    mensaje.
  - `arrastre.py` y `prueba_ar.py` cambiaron, así, después del sello: `SELLO-AR.txt` ya no los verifica, y es lo esperado.
    La previsión no cambió.
  - Cuando se vio el fallo, la comparación de los 436 ya estaba escrita. Esa comparación no usa `positivo_vxu`, y se volvió a
    calcular igual. La de aquel primer paso, con `controles.positivo_vxu` en `false`, se guardó en
    `COMPARACION-AR-primer-paso9.json`.
- **DV-AR-12, tras la revisión a ciegas de la publicación (25-oct).** La revisión aprobó y dejó hallazgos menores. Se
  arreglaron así:
  - **`control_ar.py --sello <carpeta>`:** la orden de repetir no corría tal cual, porque el sello publicado ya no verifica dos
    ficheros. Quien repite sella su propia previsión en otra carpeta con `sellar_prevision.py <cuerpo> <carpeta>`, que ahora
    acepta la carpeta y escribe las rutas del sello relativas a ella. Primero, la prueba en rojo en P-AR-12.
  - **Las columnas de la deriva del juez en `CIFRAS-AR.json`** se llaman ahora `publicado` y `con_el_juez_actual`. Antes
    reutilizaban `lote` y `mensaje`, que ahí no significaban eso. Se regeneró con los pasos 12 y 13.
  - **`CONTROL-AR.json` lleva un `_nota`** con lo que se le quitó al publicarlo: la ruta de los artefactos y el commit del
    sello.
  - **`control_ar.py` también cambió después del sello**, con `--sello`. El sello ya no verifica, así, tres ficheros:
    `arrastre.py`, `prueba_ar.py` y `control_ar.py`.
  - **La segunda pasada de la revisión aprobó.** De sus sugerencias se aplicaron estas:
    - `sellar_prevision.py` se niega a pisar un `SELLO-AR.txt` que ya exista;
    - la huella del conversor que escribe es la esperada del estudio, y lo dice un comentario;
    - el límite del orden cita el apoyo público.

    La glosa de «opción B» no se añadió al ANTES, que está fijado.
