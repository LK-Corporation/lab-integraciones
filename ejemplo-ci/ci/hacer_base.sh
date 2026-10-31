#!/usr/bin/env bash
# El proyecto de ejemplo (etapa 24, ejemplo-ci/README.md): crea y comprueba sus dos lineas base y el defecto del run en rojo, en
# una maquina con Docker y red, desde la raiz del repositorio. Es el recetario de verificador/cv/ci/CI.md escrito en un guion,
# con las comprobaciones de verificador/cv/ci/hacer_bases.py: dos corridas iguales byte a byte, «igual» contra la base y el
# defecto, que tiene que fallar con «falla» y con «pasa». Para en el primer paso que no cuadra.
#   bash ejemplo-ci/ci/hacer_base.sh <artefactos vacios> <trabajo vacio>
set -euo pipefail
DIGEST=sha256:a0f57064cbdcd6285fa45f51237ab0b35ea8ebaed06a1f5973e89e19dfb86704
RAIZ=$(pwd)
EJ=$RAIZ/ejemplo-ci
para() { echo "PARADA: $*"; exit 1; }
test -f "$EJ/conversor.py" && test -f "$RAIZ/verificador/cv/verificar_conversor.py" || para "corre desde la raiz del repositorio"
ART=$(realpath "$1")
TRABAJO=$(realpath "$2")
[ -z "$(ls -A "$ART")" ] && [ -z "$(ls -A "$TRABAJO")" ] || para "las dos carpetas tienen que estar vacias"

echo "== 1. la imagen, por su digest"
docker pull -q "python:3.12-slim@$DIGEST"
docker tag "python@$DIGEST" python:3.12-slim
docker image inspect --format '{{index .RepoDigests 0}}' python:3.12-slim | grep -q "$DIGEST" || para "la imagen no es la del digest"

echo "== 2. preparar"
bash "$EJ/preparar.sh" "$ART"

cd "$RAIZ/verificador"
corrida() {   # <salida> [opciones mas]
  local s=$1
  shift
  python3 cv/verificar_conversor.py "$EJ/ci/adaptador.json" "$s" --artefactos "$ART" --sin-sensibilidad --corpus "$EJ/corpus" "$@" \
    > "$s.log" 2>&1 || para "la corrida $(basename "$s") salio con $? (su registro: $(basename "$s").log)"
  python3 -c 'import json,sys; c=json.load(open(sys.argv[1] + "/CORRIDA.json")); sys.exit(1 if c["sin_evidencia"] else 0)' "$s" \
    || para "$(basename "$s") tiene casos sin evidencia"
}
n_casos() {
  python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["n_casos"])' "$1"
}
esperado() {   # <lab|propio>: los casos que junta la herramienta en este commit; el numero no va a mano (etapa 27)
  python3 -c 'import os, sys, tempfile; sys.path.insert(0, "cv"); import verificar_conversor as V
co = V.generar_corpus(os.path.join(tempfile.mkdtemp(), "c"), lab=sys.argv[1] == "lab", minimos=False, propios=[sys.argv[2]])
print(len(co["casos"]))' "$1" "$EJ/corpus"
}
base() {   # <nombre> <fichero de la base> <n esperado> [opciones mas]
  local n=$1 b=$2 esperado=$3
  shift 3
  echo "== $n: dos corridas, la base y «igual»"
  corrida "$TRABAJO/$n-1" "$@"
  corrida "$TRABAJO/$n-2" "$@"
  cmp "$TRABAJO/$n-1/INFORME.json" "$TRABAJO/$n-2/INFORME.json" || para "$n: INFORME.json distinto entre dos corridas"
  python3 cv/ci/linea_base.py crear "$TRABAJO/$n-1" -o "$b"
  [ "$(n_casos "$b")" = "$esperado" ] || para "$n: $(n_casos "$b") casos y la herramienta junta $esperado en este commit"
  python3 cv/ci/linea_base.py comparar "$TRABAJO/$n-2" "$b" --esperar igual -o "$TRABAJO/$n-igual" || para "$n: la segunda corrida no da lo mismo que la base"
}

base ejemplo "$EJ/ci/LINEA-BASE.json" "$(esperado lab)"
base propio "$EJ/ci/LINEA-BASE-propio.json" "$(esperado propio)" --json-solo --sin-corpus-lab

echo "== 8. el defecto, sembrado en la copia de los artefactos"
python3 "$EJ/ci/sembrar.py" "$ART/conv/conversor.py" "$EJ/ci/DEFECTO.json"

echo "== 9. la corrida sembrada: «falla» por el hallazgo esperado, y «pasa» sale con 10 solo por el hallazgo nuevo"
corrida "$TRABAJO/ejemplo-sembrado"
ESPERADO=$(python3 -c 'import json,sys; print(json.dumps(json.load(open(sys.argv[1]))["hallazgo_esperado"]))' "$EJ/ci/DEFECTO.json")
if ! python3 cv/ci/linea_base.py comparar "$TRABAJO/ejemplo-sembrado" "$EJ/ci/LINEA-BASE.json" --esperar falla \
    --hallazgo-esperado "$ESPERADO" -o "$TRABAJO/ejemplo-sembrado-falla"; then
  python3 -c 'import json,sys; print("el juez dio", json.load(open(sys.argv[1]))["nuevos_distintos"])' "$TRABAJO/ejemplo-sembrado-falla/VEREDICTO-CI.json"
  para "el defecto no da el hallazgo esperado: escribe en DEFECTO.json lo que dio y repite"
fi
set +e
python3 cv/ci/linea_base.py comparar "$TRABAJO/ejemplo-sembrado" "$EJ/ci/LINEA-BASE.json" --esperar pasa -o "$TRABAJO/ejemplo-sembrado-pasa"
rc=$?
set -e
[ "$rc" = 10 ] || para "con «pasa», la corrida sembrada salio con $rc y no con 10"
python3 - "$TRABAJO/ejemplo-sembrado-pasa/VEREDICTO-CI.json" <<'EOF' || para "con «pasa», el motivo no es solo el hallazgo nuevo"
import json, sys
v = json.load(open(sys.argv[1]))
assert v["motivos"] == ["hallazgo_nuevo"], v["motivos"]
assert set(v["avisos"]) == {"huella_distinta"}, v["avisos"]
EOF

echo "== 10. deshacer"
python3 "$EJ/ci/sembrar.py" "$ART/conv/conversor.py" "$EJ/ci/DEFECTO.json" --deshacer
cmp "$ART/conv/conversor.py" "$EJ/conversor.py" || para "la copia no volvio a ser el conversor"

echo "== 11. lo comprobado, en $TRABAJO/BASE-EJEMPLO.json"
python3 - "$TRABAJO" "$EJ" "$DIGEST" <<'EOF'
import json, os, sys
t, ej, dig = sys.argv[1:4]
b = json.load(open(os.path.join(ej, "ci", "LINEA-BASE.json")))
p = json.load(open(os.path.join(ej, "ci", "LINEA-BASE-propio.json")))
v = json.load(open(os.path.join(t, "ejemplo-sembrado-falla", "VEREDICTO-CI.json")))
cats = {}
for k, x in b["casos"].items():
    cats.setdefault(k.split("/")[0], {}).setdefault(x["categoria"], 0)
    cats[k.split("/")[0]][x["categoria"]] += 1
r = {"huella": b["conversor"]["huella"], "huella_con_nombres": b["conversor"]["huella_con_nombres"], "imagen_digest": dig,
     "n_casos": {"LINEA-BASE.json": b["n_casos"], "LINEA-BASE-propio.json": p["n_casos"]}, "categorias": cats,
     "rojo_n_casos": len({x["caso"] for x in v["nuevos"]}), "rojo_nuevos_distintos": v["nuevos_distintos"]}
json.dump(r, open(os.path.join(t, "BASE-EJEMPLO.json"), "w"), ensure_ascii=False, indent=1)
print(json.dumps(r, ensure_ascii=False, indent=1))
EOF
