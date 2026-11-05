#!/bin/sh
# Etapa 32: el bloque del sello tras la revisión a ciegas (ivd/SELLO-IVD.txt). Desde fase12: sh ivd/sellar_ivd2.sh
set -e
cd ivd
grep -q 'tras la revisión a ciegas' SELLO-IVD.txt && { echo "ya está"; exit 0; }
{
  echo "# --- tras la revisión a ciegas (5-nov, un lector; dos bloqueantes): Q-VD-3 por tercera vez, después de correr, con los hechos de los dos lados y el efecto medido (Q-VD-3c: sin decidir, estado_qvd3c.md); las dos lecturas dejan sin decidir los campos de más, y la de la 2.5.1 anota aparte las otras formas que el conductor no reconoce; el control, con N-C2, N-C3 y el negativo de N-C3 (TODO BIEN); el cruce mide la pasada de repeticiones en las FILAS y da las tres respuestas a Q-VD-3. El conductor y la clase de IRIS no cambian; la corrida no se repite. Lo de arriba queda como historia. Las de abajo son las finales"
  sha256sum estado_qvd3c.md preguntas_qvd3c.json decision-jev-qvd3c.md hacer_lectura_ivd.py lectura_ivd251.py lectura_ivdst.py \
    control_ivd.py CONTROL-IVD.json cruce_ivd.py
  echo "# los veredictos de la lectura sellada, guardados aparte, y los finales (privados: solo su huella)"
  sha256sum ../../privado/ivd/VEREDICTOS-IVD251-sellada.jsonl ../../privado/ivd/VEREDICTOS-IVDST-sellada.jsonl \
    ../../privado/ivd/VEREDICTOS-IVD251.jsonl ../../privado/ivd/VEREDICTOS-IVDST.jsonl
} >> SELLO-IVD.txt
tail -n 15 SELLO-IVD.txt | cut -c1-120
