#!/bin/sh
# Etapa 32: el bloque del sello tras la segunda pasada de la revisión a ciegas (ivd/SELLO-IVD.txt). Desde fase12: sh ivd/sellar_ivd3.sh
set -e
cd ivd
grep -q 'tras la segunda pasada de la revisión a ciegas' SELLO-IVD.txt && { echo "ya está"; exit 0; }
{
  echo "# --- tras la segunda pasada de la revisión a ciegas (5-nov; un bloqueante: el estado de Q-VD-3c no era neutral ni traía todos los hechos): Q-VD-3d (estado_qvd3d.md), qué regla va en el titular: la del ANTES (aparte, Q-VD-3b), con «sin decidir» y «dentro» como sensibilidad. Las dos lecturas vuelven a poner aparte los campos de más (la de la 2.5.1 sigue anotando la clase X, sin cambiar ningún veredicto: los finales son los de la lectura sellada); N-C2 espera «aparte» en la lectura; el cruce da las tres respuestas y deja de dar la previsión con la lectura sellada. El bloque de arriba queda como historia. Las versiones de antes de correr de lo que cambió, en sellada/ (sus huellas son las del primer bloque). Las de abajo son las finales"
  sha256sum estado_qvd3d.md preguntas_qvd3d.json decision-jev-qvd3d.md hacer_lectura_ivd.py lectura_ivd251.py lectura_ivdst.py \
    control_ivd.py CONTROL-IVD.json cruce_ivd.py sellada/*
  echo "# los veredictos finales (privados: solo su huella), iguales en veredicto a los sellados"
  sha256sum ../../privado/ivd/VEREDICTOS-IVD251.jsonl ../../privado/ivd/VEREDICTOS-IVDST.jsonl
} >> SELLO-IVD.txt
tail -n 18 SELLO-IVD.txt | cut -c1-110
