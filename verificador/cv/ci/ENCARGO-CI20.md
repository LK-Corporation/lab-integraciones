> *Copia pública: se quitaron las alusiones al autor y a su máquina. El resto es el original del laboratorio.*

# Encargo CI20: diseño de la etapa 24, lo abierto de la integración continua

Diseñas, sin programar, el aparato de una etapa ya fijada. Quien lo programe será otro modelo y seguirá tu diseño al pie de la
letra; no podrá preguntarte. Responde en español.

## Dónde mirar

**Lee solo** estas dos cosas:
- una carpeta aparte, con `ANTES-ETAPA-CI2.md`: la etapa, fijada antes de medir. Es tu marco y no se negocia.
- el repositorio público, este. Sobre todo:
  - `.github/workflows/` (el flujo reutilizable, su demostración y la higiene);
  - `verificador/cv/ci/` (`CI.md`, `linea_base.py`, `prueba_ci.py`, `ensayo_flujo.py`, `decisiones-qci.md`, las bases);
  - `verificador/RESULTADO-CI.md`;
  - `verificador/cv/verificar_conversor.py` y `verificador/cv/conversor_juguete.py`;
  - `tests/test_repo_hygiene.py`.

No leas nada fuera de esas dos rutas, no modifiques nada, no ejecutes Docker ni Java, no corras conversores y no uses la red.
Puedes correr `python3` para inspeccionar, sin escribir fuera de esa carpeta aparte.

**Lo que tienes que entender:**
- **Cómo corre hoy el flujo de la etapa 23,** paso a paso, y cómo lo llama la demostración (`uses: ./…`, todo bajo `lab/`).
- **Qué salió en el runner y qué no se recorrió:** la sección «Lo que no dice» de `RESULTADO-CI.md`.
- **Lo que la revisión a ciegas de la etapa 23 dejó sin hacer:** las cuatro observaciones del ANTES, y el defecto del `-e` de
  GitHub que se arregló en DV-CI-12 (`decisiones-qci.md`).
- **Cómo ensaya los YAML `ensayo_flujo.py`** y qué no puede ensayar.

## Lo que tienes que decidir y escribir

1. **Los cuatro endurecimientos,** cada uno con el YAML exacto que cambia:
   - las entradas por variables de entorno en cada paso `run:`, sin ninguna `${{ inputs.* }}` dentro de un `run:`;
   - las acciones fijadas por SHA. Tú no puedes usar la red, así que di cómo obtiene el programador cada SHA (la orden exacta) y
     cómo se comprueba que corresponde a la etiqueta;
   - `laboratorio_ref`: obligatoria o no, qué pasa con quien ya lo usa y qué dice `CI.md`;
   - el repositorio del laboratorio en la demo, para que funcione en un fork.
2. **El proyecto de ejemplo:**
   - dónde vive en el repositorio, con qué conversor, con qué adaptador, con qué corpus sintético propio y con qué línea base;
   - cómo se crea su base.
3. **La llamada por la forma remota,** `uses: LK-Corporation/lab-integraciones/.github/workflows/verificador-conversor.yml@<commit>`.
   - En `uses:` no caben expresiones, y el commit con el flujo endurecido no existe hasta después de su push. Di cómo se resuelve,
     en cuántos pushes y qué commit se fija.
   - Qué entradas recorre: `esperar: pasa`, `corpus`, `opciones`, `artefacto_completo` y `sin_corpus_lab` si cabe.
   - Qué tiene que salir.
4. **El run en rojo a propósito:**
   - solo a mano (`workflow_dispatch`), en un fichero aparte o no;
   - qué defecto lo pone en rojo, con `esperar: pasa`;
   - cómo comprueba un job de fuera que falló por ese hallazgo y no por otro, que dejó su resumen y que el artefacto lleva su
     veredicto;
   - qué conclusión queda en la corrida.
5. **`pull_request`:** si se recorre o no, y cómo, dentro de las condiciones del ANTES. Si se recorre con un PR del propio
   repositorio, di cómo y qué se hace con él después. Puede ser una pregunta para Jev.
6. **Lo que no puede romperse:** que los tres controles de la etapa 23 siguen en verde con los mismos informes, y cómo se
   comprueba.
7. **Las pruebas en rojo** (P-CI-16, 17…) para todo lo nuevo, con su control negativo. Deben correr sin Docker y sin red, e
   incluir:
   - una guarda estática de que ninguna `${{ inputs.* }}` queda en un `run:`;
   - una de que toda acción va por SHA.
8. **El ensayo local:** qué tiene que aprender `ensayo_flujo.py` para ensayar lo nuevo (la forma remota, el run en rojo), o qué
   queda fuera.
9. **La previsión que se sella:** sus claves.
10. **Las preguntas de diseño para Jev** (Q-CI2-D-1, 2…): solo las que ni el ANTES ni lo de arriba deciden, con dos o tres opciones
    y tu recomendación aparte.
11. **Los límites** (L-CI2-1, 2…) y **el plan,** respetando el tope del ANTES: cada push al público pasa por la opción B.

## Qué devuelves

Un único documento de diseño, en Markdown, con estas secciones:
- las decisiones (S-CI2-n, cada una con su porqué en una línea);
- los endurecimientos;
- el proyecto de ejemplo;
- la forma remota;
- el run en rojo;
- `pull_request`;
- lo que no se rompe;
- las pruebas;
- el ensayo;
- la previsión;
- las Q-CI2-D;
- los límites;
- el plan.

Sé concreto: nombres de ficheros, opciones, formatos y YAML completo de lo que cambia. El programador no podrá preguntarte.
