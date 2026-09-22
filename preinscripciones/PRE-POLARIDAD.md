# Preinscripción PRE-POLARIDAD — 21-sep-2026

**Se escribe y se sella ANTES de encargar las redacciones y antes de medir nada.** Si este
documento aparece en el repositorio después de la tanda, no vale para nada.

---

## 1. Qué se pone a prueba

En la primera batería de fragilidad, diez paráfrasis encargadas a ciegas sobre el conjunto de
desarrollo (72 silenciosos + 72 limpios, T=0, pareadas) dieron:

| polaridad | n | macro primario | falsa alarma |
|---|---|---|---|
| positiva | 8 | 0,578 – 0,760 | 2–7 de 72 |
| invertida | 2 | 0,029 y 0,108 | 22 y 31 de 72 |

**Ese contraste es post hoc y descansa en dos redacciones.** Salió porque los dos modelos a los
que se encargaron las paráfrasis eligieron, cada uno por su cuenta, invertir justo su quinta. No
estaba predicho.

**Hipótesis a confirmar:** una pregunta binaria de polaridad **invertida** —aquella en la que
«SI» significa que hay un problema— destruye la detección del peldaño 1, mientras que la
**positiva** la conserva, y eso es una propiedad de la polaridad y no del azar de dos redacciones.

## 2. El diseño, y el control que la primera tanda no tenía

Se encargan **diez redacciones nuevas a un tercer modelo** que no participó en la primera tanda:
**cinco de polaridad positiva y cinco invertidas**, en el mismo encargo y a ciegas del resultado
anterior.

**Las cinco positivas son el control de lote.** Sin ellas, si las invertidas fallan quedaría la
duda de si el lote nuevo es sencillamente peor que el primero. Con ellas, la comparación es
interna al lote.

Mismo conjunto, misma muestra con la misma semilla, misma temperatura, mismos casos, pareadas.
La original de la primera tanda se vuelve a correr como ancla.

## 3. Las predicciones, con números

Sobre el **macro primario** (media macro por operador, 17 operadores, con `ideal_b`):

| | predicción |
|---|---|
| **P1** | las cinco **positivas** caen en **[0,50 · 0,80]** |
| **P2** | las cinco **invertidas** caen **por debajo de 0,30** |
| **P3** | **ninguna invertida supera a ninguna positiva** — separación completa |
| **P4** | la falsa alarma de las invertidas es **> 0,15** (11 de 72); la de las positivas, **< 0,15** |
| **P5** | en las invertidas, el mapeo de la respuesta al veredicto **sigue siendo correcto** para su polaridad en **> 90 %** de los casos: lo que falla es contestar, no traducir |

## 4. La regla de decisión, escrita antes

- **CONFIRMADA** si se cumplen P2 y P3: las cinco invertidas por debajo de 0,30 y separación
  completa respecto de las positivas.
- **REFUTADA** si **dos o más** invertidas caen dentro del rango de las positivas del mismo lote.
- **PARCIAL** en cualquier otro caso —por ejemplo, una sola invertida dentro del rango—, y se
  reporta como parcial sin redondear hacia donde convenga.

Si **P1 falla** —las positivas nuevas no reproducen el rango de la primera tanda— **la tanda no
concluye nada sobre polaridad**, porque habría un efecto de lote que lo confunde todo. Eso se
declara aquí para que no se pueda reinterpretar después.

**P5 es independiente de las otras cuatro** y se reporta aparte: dice si el fallo está en
contestar o en traducir, y esa es la parte mecanicista.

## 5. Lo que NO se va a hacer

- No se eligen redacciones: se usan las diez que lleguen, tal cual.
- No se retoca ninguna, ni aunque parezca mejorable.
- No se añaden condiciones después de ver los resultados.
- No se cambia el umbral de 0,30 ni el de 0,15 después de medir.
- Si el resultado sale ambiguo, se reporta ambiguo.

## 6. Lo que esto no prueba aunque salga confirmada

Un modelo, una temperatura, una tarea, un idioma. Confirma que **en este montaje** la polaridad
importa. No dice nada de otros modelos ni de otras tareas, y el documento que salga lo dirá así.
