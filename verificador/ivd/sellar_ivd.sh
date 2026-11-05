#!/bin/sh
# Etapa 32: el sello antes de correr (ivd/SELLO-IVD.txt). Desde fase12: sh ivd/sellar_ivd.sh
set -e
cd ivd
{
  echo "# sellado el 5-nov-2026, antes de pasar ninguna muestra por el aparato de la 32; control en TODO BIEN (CONTROL-IVD.json)"
  sha256sum ../ANTES-ETAPA-IVDECLARADA.md estado_qvd.md preguntas_qvd.json decision-jev-qvd.md estado_qvd3b.md \
    preguntas_qvd3b.json decision-jev-qvd3b.md estado_prevision_ivd.md preguntas_prevision_ivd.json \
    decision-jev-prevision-ivd.md PREVISION-IVD.json Lab.IVD.Validar.cls cargar_ivd.txt prueba_ivd.txt prueba_lote_ivd.py \
    texto_ivd.py hacer_vista_251.sh tablas_ivd.py TABLAS-TIPO-IVD251.json hacer_validar_ivd.py validar_ivd251.py \
    validar_ivdst.py hacer_lectura_ivd.py lectura_ivd251.py lectura_ivdst.py corpus_ivd.py CORPUS-IVD-lista.json \
    control_ivd.py CONTROL-IVD.json
  echo "# lo que no se publica (el texto de HL7 no se redistribuye; las muestras están en sus proyectos), solo su huella"
  sha256sum ../../privado/ivd/TABLAS-VALORES-IVD251.json ../../privado/ivd/corpus251/CORPUS-IV.json ../../privado/ivd/corpusst/CORPUS-IV.json
  echo "# de los que salen las copias, sin cambios desde la 31"
  sha256sum ../ivm/validar_ivm.py ../ivm/lectura_ivm.py ../iv/tablas_iv.py
} > SELLO-IVD.txt
wc -l SELLO-IVD.txt
