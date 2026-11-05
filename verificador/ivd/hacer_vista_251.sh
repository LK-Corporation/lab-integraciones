#!/bin/sh
# Etapa 32 (Q-VD-2): una carpeta de enlaces simbólicos al texto de v2.5.1 con los nombres de fichero del de v2.5, para leerlo con
# los analizadores de la 30 y la 31. No copia texto. Desde fase12: sh ivd/hacer_vista_251.sh
set -e
D=../estandares/hl7v2/HL7_Messaging_v251
mkdir -p "$D/vista_v25"
cd "$D/vista_v25"
for f in ../txt/V251_*.txt; do
  n=$(basename "$f" .txt)
  n=${n#V251_}
  case $n in
    Appendix_A) n=AppendixA ;; Appendix_B) n=AppendixB ;; Appendix_C) n=AppendixC ;; Appendix_D) n=AppendixD ;;
    Appendix_E) n=AppendixE ;; CH03) n=Ch03 ;;
  esac
  ln -sf "$f" "$n.txt"
done
ls | wc -l
