> *Copia pública: se quitaron las alusiones al autor y a su máquina. El resto es el original del laboratorio.*

# Encargo CI0: diseño de la etapa 23, el verificador en la integración continua de un conversor

Diseñas, sin programar, el aparato de una etapa ya fijada. Quien lo programe será otro modelo y seguirá tu diseño al pie de la
letra; no podrá preguntarte. Responde en español.

## Dónde mirar

**Lee solo** estas dos cosas:
- una carpeta aparte, con `ANTES-ETAPA-CI.md`: la etapa, fijada antes de medir. Es tu marco y no se negocia.
- el repositorio público, este: el verificador, su herramienta y la integración continua que ya
  tiene (`.github/workflows/higiene.yml`, `tests/test_repo_hygiene.py`).

No leas nada fuera de esas dos rutas, no modifiques nada, no ejecutes Docker ni Java, no corras conversores y no uses la red.
Puedes correr `python3` para inspeccionar, sin escribir fuera de esa carpeta aparte.

**Lo que tienes que entender:**
- **La herramienta:** `verificador/cv/verificar_conversor.py` (sus opciones, `juicio.jsonl`, `INFORME.json`, `--comparar`, los
  códigos de salida), `verificador/cv/VC.md`, `verificador/cv/adaptadores/` y `verificador/cv/conversor_juguete.py`, con sus
  directivas.
- **Cómo se obtiene LinuxForHealth v1.1.0:** `verificador/cv/CV1.md`, `verificador/cv/lfh/` (el `pom.xml`, el arnés y cómo se
  copian las dependencias) y la huella que el estudio fijó para él.
- **La imagen de Docker y su digest,** en los adaptadores y en `verificador/cv/vc/CONTROL-VC.md`.
- **El arrastre de estado de LinuxForHealth en lote** (`verificador/RESULTADO-ARRASTRE.md`) y su adaptador mensaje a mensaje.
- **La integración continua que ya hay** y lo que la higiene admite en `.github/`.

## Lo que tienes que decidir y escribir

1. **La línea base.** Su formato; con qué orden se crea desde una corrida de la herramienta; y la regla exacta de comparación:
   - qué es un «hallazgo nuevo» y qué hace fallar el cambio;
   - qué pasa con lo que desaparece (un arreglo), con un caso nuevo o un caso que falta, con un error de la caja y con un cambio de
     categoría sin hallazgo nuevo;
   - cómo se actualiza la línea base cuando el proyecto acepta un cambio.

   Di si basta una opción nueva de la herramienta o hace falta un guion aparte, sin tocar el juez.
2. **El flujo reutilizable** (`on: workflow_call`), completo en YAML:
   - sus entradas: el adaptador, cómo se preparan los artefactos del conversor, el corpus, la línea base y la imagen;
   - sus permisos, y lo que deja: el informe como artefacto y un resumen en la página del job;
   - el código de salida, y cómo se garantiza la caja en el runner;
   - cómo se fija la imagen por su digest, para que el runner use la misma que el laboratorio.
3. **La demostración en el repositorio del laboratorio,** completa en YAML, con los tres controles del ANTES:
   - el negativo y el positivo sembrado con el juguete; el positivo tiene que comprobar que el flujo falla y por qué hallazgo;
   - el real con LinuxForHealth v1.1.0 traído en el runner, con su huella comprobada.

   Cuándo corre (en qué eventos y rutas), cuánto cuesta y cómo se evita que gaste minutos sin necesidad.
4. **El determinismo:** qué del runner puede cambiar el resultado frente al laboratorio (la imagen, la zona horaria, el orden de
   los ficheros, la red, el modo lote o mensaje) y cómo se neutraliza cada cosa.
5. **La línea base del control real:** de qué corrida del laboratorio sale, con qué corpus, y cómo se comprueba antes de publicarla.
6. **La guía para un tercero** (`cv/ci/CI.md`): lo que tiene que poner en su proyecto, con un ejemplo completo.
7. **La previsión que se sella:** sus claves.
8. **Las pruebas en rojo** (P-CI-1, 2…) para todo el código nuevo, incluida una validación estática de los YAML, con su control
   negativo; deben correr sin Docker y sin red.
9. **Las preguntas de diseño para Jev** (Q-CI-D-1, 2…): solo las que ni el ANTES ni lo de arriba deciden, con dos o tres opciones
   y tu recomendación aparte.
10. **Los límites** (L-CI-1, 2…) y **el plan,** respetando el tope del ANTES: cada push al público pasa por la opción B.

## Qué devuelves

Un único documento de diseño, en Markdown, con estas secciones:
- las decisiones (S-CI-n, cada una con su porqué en una línea);
- la línea base;
- el flujo;
- la demostración;
- el determinismo;
- la línea base del control real;
- la guía;
- la previsión;
- las pruebas;
- las Q-CI-D;
- los límites;
- el plan.

Sé concreto: nombres de ficheros, opciones, formatos y YAML completo. El programador no podrá preguntarte.
