> *Copia pública: se quitaron las alusiones al autor y a su máquina. El resto es el original del laboratorio.*

# ANTES: etapa 22, las nueve de VXU en las ramas principales (FIJADO el 25-oct-2026)

**Fijado en autónomo**, dentro de la hoja de ruta del laboratorio (`HOJA-DE-RUTA.md`, no publicada). Jev eligió esta etapa
con 0,99 (`decision-jev-ruta5.md`, no publicada); la segunda opción, contar VXU y el arrastre en el artículo y la página, quedó
en 0,01.

## La pregunta (fija)

> ¿Siguen en la rama principal de cada conversor las nueve discrepancias nuevas de VXU y el arrastre de estado de LinuxForHealth?
> Y, para las que sigan, ¿quedan listos los borradores de issues, contrastados con lo que cada proyecto tiene abierto hoy?

## Punto de partida (medido)

- **Las nueve** se midieron en las versiones fijadas del estudio, Microsoft v7.0 y LinuxForHealth v1.1.0, y cada una se
  confirmó con un par de mensajes mínimos de `cv/cv3_minimos_vxu.py` (`vx/CLASES-VX3.json`, `vx/RESULTADO-VX3-minimos.json`):
  - **Microsoft:** VX-M7 (VM07), VX-M8 (VM08), VX-M10 (VM10), VX-M12 (VM12), VX-M14 (VM14) y VX-M15 (VM15);
  - **LinuxForHealth:** VX-L6 (VL04), VX-L8 (VL06) y VX-L9 (VL07).
- **El arrastre de estado de LinuxForHealth** tiene su secuencia, VL11. Es el síntoma de su issue abierto #348, con un disparador
  (RXA-17 con solo texto) que su arreglo provisional no cubre. La etapa 21 añadió que en el corpus del estudio solo se ve en VXU.
- **Las ramas principales ya se construyeron el 24-oct** (`cv/RESULTADO-15A.md`): Microsoft `main` en `70fd328` y LinuxForHealth
  `master` en `2cb72c2`. Con ellas, de las 15 nuevas de ADT y ORU siguieron 14, y la otra la había corregido el proyecto.
- **En la etapa 20, los pares de LinuxForHealth se corrieron en lote,** un proceso por carpeta. Tras la etapa 21 se sabe que ese
  conversor arrastra estado entre mensajes del mismo proceso.
- **No hay borradores de issues de VXU.** Los del estudio de conversores (`cv/BORRADORES-ISSUES.md`) esperan en la cola del autor.

## Condiciones que no se negocian

1. **Solo terceros públicos.**
2. **El código de terceros corre en la caja de siempre.** La red solo se usa para construir una rama principal, como en 15A.
3. **El mismo juez a los dos lados:** el del laboratorio, que es el publicado salvo el corte C19, que no toca VXU.
4. **El aparato se prueba antes de usarlo.** Los pares corridos hoy con las versiones fijadas tienen que dar lo mismo que
   `vx/RESULTADO-VX3-minimos.json`, o la diferencia se explica antes de mirar las ramas principales.
5. **Los issues son del autor:** se preparan y se encolan, nunca se abren. Los borradores no se publican; el resultado, sí.

## Qué se mide

- **Las ramas, hoy.** Si `main` y `master` avanzaron desde el 24-oct: si tocan VXU, se reconstruye la rama al día, y se anota el
  commit.
- **Cada una de las nueve:** si sigue en la rama principal o está corregida, con su par (el caso sale y el control no).
- **El arrastre en `master`:** la secuencia VL11, en lote y mensaje a mensaje.
- **El contraste de hoy:** si cada una que siga ya tiene un issue o un PR abierto o cerrado en su proyecto, a la fecha de la etapa.
- **Los borradores:** uno por discrepancia que siga, con el par mínimo, la cita de la guía, lo esperado y lo observado. El del
  arrastre es un comentario al #348.

## Previsión (se sella antes de correr las ramas principales)

La probabilidad de que siga cada una, y de que siga el arrastre, se escribe y se sella en un commit antes de la primera corrida
con una rama principal.

## Hecho cuando

- **El control de las versiones fijadas** da lo mismo que en la etapa 20, o la diferencia está explicada.
- **Un documento de resultado,** `RESULTADO-RAMAS-VXU.md`, con la frase: «De las 9 nuevas de VXU, siguen K en la rama principal
  de su conversor (Microsoft k1 de 6, LinuxForHealth k2 de 3); el arrastre de estado [sigue/no sigue] en `master`».
- **Los borradores,** en `vx/BORRADORES-ISSUES-VXU.md`, contrastados con lo abierto, y encolados en la cola del autor.
- **Lo publicado, al día con la opción B:** el resultado y su nota en `RESULTADO-VXU.md`, sin los borradores.

## Tope

**Una sesión.** Si una rama no se construye en 1,5 h, se declara y se mide lo que se pueda.

## Regla de parada

- **El control de las versiones fijadas no reproduce lo de la etapa 20 y la diferencia no se explica:** se declara y no se mira
  ninguna rama principal hasta arreglar el aparato.

## Fuera de la etapa

- Arreglar los conversores.
- Abrir los issues, que es del autor.
- Las discrepancias ya declaradas o de convención, salvo para anotar si siguen.
