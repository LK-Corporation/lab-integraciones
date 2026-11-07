#!/usr/bin/env bash
# Etapa 35 (cr/diseno-cr-fable.md §6): los controles del ANTES, con un remoto de prueba local. No toca el clon ni su origin: hace un
# remoto vacío a partir del clon, una copia de él, un cambio real en un fichero que los flujos leen (cv/ci/CI.md), el ensayo de los
# tres flujos sobre ese índice (una vez; los tres controles comparten los ENSAYO.json, como un push de verdad) y tres pushes al
# remoto de prueba, cada uno comprobado:
#   negativo: commit y push del índice ensayado            -> tiene que dar 0
#   positivo-add: un fichero de más tras el ensayo           -> tiene que dar 1, con esa ruta
#   positivo-amend: un cambio con commit --amend tras él     -> tiene que dar 1, con esa ruta
# Escribe <carpeta>/res/ (las salidas, CODIGOS.txt con el código y los segundos de cada comprobación, y PUBLICADO.json de cada una)
# y HECHO al final.
#   bash cr/controles_cr.sh <clon limpio del público> <comprobar_publicado.py> <ensayo_flujo.py> <carpeta vacía fuera del clon>
set -euo pipefail
CLON=$(realpath "$1")
COMP=$(realpath "$2")
ENS=$(realpath "$3")
B=$(realpath "$4")
para() { echo "PARADA: $*" | tee -a "$B/HECHO"; exit 1; }
[ -z "$(ls -A "$B")" ] || { echo "PARADA: $B no está vacía"; exit 1; }
[ -z "$(git -C "$CLON" status --porcelain --untracked-files=all)" ] || para "el clon no está limpio"
C="$B/copia"
gitc() { git -C "$C" -c user.name=controles -c user.email=controles@localhost -c commit.gpgsign=false -c core.hooksPath=/dev/null "$@"; }

echo "== el remoto de prueba y la copia"
git clone -q --bare "$CLON" "$B/remoto.git"
git clone -q "$B/remoto.git" "$C"
echo "Línea de control de la etapa 35." >> "$C/verificador/cv/ci/CI.md"
gitc add verificador/cv/ci/CI.md

echo "== el ensayo de los tres flujos, una vez"
mkdir -p "$B/ens" "$B/res"
ensayo() {   # <nombre> <argumentos del ensayo…>
  local n=$1
  shift
  python3 "$ENS" "$C" "$B/ens/$n" "$@" > "$B/ens/$n.salida.txt" 2>&1 || para "el ensayo de $n salió con $?"
  tail -n 1 "$B/ens/$n.salida.txt"
}
ensayo demo pruebas,negativo,positivo --flujo demo-ci
ensayo ejemplo ejemplo,ejemplo-propio --flujo ejemplo-ci
ensayo rojo rojo --flujo rojo-ci --rojo rojo
python3 - "$B/ens" "$(gitc write-tree)" <<'EOF' || para "los tres ensayos no son del índice"
import json, sys
d, t = sys.argv[1], sys.argv[2]
for n in ("demo", "ejemplo", "rojo"):
    c = json.load(open("%s/%s/ENSAYO.json" % (d, n)))["clon"]
    assert (c["tipo"], c["arbol"]) == ("arbol", t), (n, c["tipo"], c["arbol"], t)
print("los tres ensayos, sobre el árbol del índice", t[:12])
EOF

comprobar() {   # <control> <rama>
  local t0 t1 rc
  t0=$(date +%s.%N)
  set +e
  python3 "$COMP" "$C" "$B/ens/demo/ENSAYO.json" "$B/ens/ejemplo/ENSAYO.json" "$B/ens/rojo/ENSAYO.json" --rama "$2" -o "$B/res/$1" \
    > "$B/res/$1.salida.txt" 2>&1
  rc=$?
  set -e
  t1=$(date +%s.%N)
  echo "$1 rc=$rc s=$(python3 -c "print(round($t1 - $t0, 2))")" | tee -a "$B/res/CODIGOS.txt"
  tail -n 1 "$B/res/$1.salida.txt"
}

echo "== negativo"
gitc commit -q -m "control negativo"
NEG=$(git -C "$C" rev-parse HEAD)
gitc push -q origin HEAD:refs/heads/negativo
comprobar negativo negativo

echo "== positivo: un git add de más"
gitc reset -q --soft HEAD~1
echo "de más" > "$C/verificador/DE-MAS-35.txt"
gitc add verificador/DE-MAS-35.txt
gitc commit -q -m "control positivo add"
gitc push -q origin HEAD:refs/heads/positivo-add
comprobar positivo-add positivo-add

echo "== positivo: un commit --amend"
gitc reset -q --hard "$NEG"
echo "Otra línea de control de la etapa 35." >> "$C/verificador/cv/ci/CI.md"
gitc add verificador/cv/ci/CI.md
gitc commit -q --amend --no-edit
gitc push -q origin HEAD:refs/heads/positivo-amend
comprobar positivo-amend positivo-amend

echo "fin=$(date +%H:%M)" > "$B/HECHO"
