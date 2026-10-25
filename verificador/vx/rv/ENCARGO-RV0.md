> *Copia pública: se quitaron las alusiones al autor y a su máquina. El resto es el original del laboratorio.*

# Encargo RV0: diseño del aparato de la etapa 22, las nueve de VXU en las ramas principales

Diseñas, sin programar, el aparato y el procedimiento de una etapa ya fijada. Quien lo programe será otro modelo y seguirá tu
diseño al pie de la letra; no podrá preguntarte. Responde en español.

## Dónde mirar

**Lee solo** estas dos cosas:
- una carpeta aparte: el ANTES de la etapa (`ANTES-ETAPA-RAMAS-VXU.md`), que es tu marco y no se negocia, y los borradores de issues de la
  etapa anterior del estudio (`BORRADORES-ISSUES-estudio.md`), como ejemplo de forma;
- el repositorio público, este (sobre todo `verificador/`).

No leas nada fuera de esas dos rutas, no modifiques nada, no ejecutes Docker ni Java, no corras conversores y no uses la red.
Puedes correr `python3` para inspeccionar, sin escribir fuera de esa carpeta aparte.

**Lo que tienes que entender:**
- **Las nueve y su contraste:** `verificador/vx/VX3.md`, `verificador/vx/CLASES-VX3.json`, `verificador/vx/RESULTADO-VX3-minimos.json`
  y `verificador/RESULTADO-VXU.md`.
- **Los pares y la secuencia:** `verificador/cv/cv3_minimos_vxu.py` (`PARES`, `SECUENCIAS`, modos `escribir`, `secuencias` y
  `juzgar`).
- **El precedente en ADT y ORU:** `verificador/cv/RESULTADO-15A.md` (cómo se construyeron y corrieron las ramas principales),
  `verificador/cv/correr_conversor.py` (la variante `CV_VARIANTE=main`) y `verificador/cv/lfh/`.
- **La herramienta y sus adaptadores:** `verificador/cv/verificar_conversor.py`, `verificador/cv/adaptadores/` (también el de
  LinuxForHealth mensaje a mensaje) y `verificador/cv/VC.md`.
- **El arrastre de estado:** `verificador/vx/VX2.md` (F7), `verificador/RESULTADO-ARRASTRE.md` y `verificador/cv/ar/`.

## Lo que tienes que decidir y escribir

1. **Cómo se corren los pares y la secuencia** con las versiones fijadas (el control) y con las ramas principales. En especial:
   - con qué herramienta y qué adaptadores; si las ramas principales necesitan adaptadores propios, escríbelos completos;
   - cómo se evita que el arrastre de estado contamine unos pares con otros en LinuxForHealth;
   - cómo se juzga, con el mismo juez, y qué cuenta como «sigue» y «corregida» para cada una de las nueve (el criterio exacto de
     `cv3_minimos_vxu.juzgar`, o el que propongas si ese no basta, con su porqué).
2. **El control de las versiones fijadas:** qué tiene que reproducir de `vx/RESULTADO-VX3-minimos.json`, con qué tolerancia, y qué
   se hace si no lo reproduce.
3. **Las ramas al día:** cómo se decide si hay que reconstruir `main` y `master` (qué se mira en su historia desde los commits del
   24-oct, qué ficheros cuentan como «tocan VXU»), y qué se anota de cada construcción.
4. **La secuencia VL11 en `master`:** procedimiento, y qué cuenta como «sigue el arrastre».
5. **El contraste con lo abierto hoy:** qué se busca en cada proyecto (issues y PR, abiertos y cerrados, con sus comentarios),
   con qué términos por cada discrepancia, y qué cuenta como «ya reportada». Solo lectura de lo público; la red la usará quien
   programe, no tú.
6. **Los borradores:** la plantilla, en inglés, con la forma de `BORRADORES-ISSUES-estudio.md`. Incluye el del arrastre, que es
   un comentario a un issue ya abierto. Di qué lleva cada uno: par mínimo, cita de la guía, esperado, observado y versiones.
7. **La previsión que se sella:** sus claves y su formato.
8. **Las pruebas en rojo** (P-RV-1, 2…) para todo el código nuevo, con su control negativo; deben correr sin Docker.
9. **Las preguntas de diseño para Jev** (Q-RV-D-1, 2…): solo las que ni el ANTES ni lo de arriba deciden, con dos o tres opciones
   y tu recomendación aparte.
10. **Los límites** (L-RV-1, 2…) y **el plan,** respetando el tope del ANTES.

## Qué devuelves

Un único documento de diseño, en Markdown, con estas secciones:
- las decisiones (S-RV-n, cada una con su porqué en una línea);
- cómo se corre;
- el control;
- las ramas al día;
- la secuencia;
- el contraste;
- los borradores;
- la previsión;
- las pruebas;
- las Q-RV-D;
- los límites;
- el plan.

Sé concreto: nombres de ficheros, opciones, formatos y órdenes. El programador no podrá preguntarte.
