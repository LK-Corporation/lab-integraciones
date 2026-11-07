#!/usr/bin/env bash
# Etapa 34 (en/diseno-en-fable.md §5; Q-EN-8: diff -r): los dos controles del ANTES, con el ensayo de hoy y el arreglado.
# - negativo: un clon limpio en 74a6a99 y su exportación sin .git; la demo (pruebas, negativo, positivo), el ejemplo y el rojo;
#   las dos versiones con la misma carpeta de trabajo, que se mueve después de cada corrida;
# - positivo: el estado de la etapa 33 (HEAD en 371937c, índice y árbol en 54e8b9f), con las dos versiones, y la demo de hoy sobre
#   un clon limpio en 54e8b9f (el triángulo).
# No toca el clon: trabaja en clones nuevos. Escribe <carpeta>/res/ (registros, CODIGOS.txt y CONTROLES-EN.json) y HECHO al final.
#   bash en/controles_en.sh <clon limpio del público, en 74a6a99> <ensayo de hoy> <ensayo arreglado> <carpeta vacía fuera del clon>
set -euo pipefail
CLON=$(realpath "$1")
HOY=$(realpath "$2")
ARR=$(realpath "$3")
B=$(realpath "$4")
C74=74a6a99a3ba4b6c329fdb4d1ae61ad3142ca7a9c
C54=54e8b9f9017ea7fb7e0b245783b02ad55d49ab21
C37=371937c9fb43b6fea89221262b9f777cb14aae15
para() { echo "PARADA: $*" | tee -a "$B/HECHO"; exit 1; }
[ -z "$(ls -A "$B")" ] || { echo "PARADA: $B no está vacía"; exit 1; }
[ "$(git -C "$CLON" rev-parse HEAD)" = $C74 ] || para "el clon no está en 74a6a99"
[ -z "$(git -C "$CLON" status --porcelain --untracked-files=all)" ] || para "el clon no está limpio"

echo "== los estados"
git clone -q "$CLON" "$B/limpio"
mkdir "$B/export"
git -C "$B/limpio" checkout-index -a --prefix="$B/export/"
git clone -q "$CLON" "$B/pos"
git -C "$B/pos" -c advice.detachedHead=false checkout -q $C37
git -C "$B/pos" read-tree -u --reset $C54
[ -z "$(git -C "$B/pos" status --porcelain --untracked-files=all | grep -v '^[MADR]  ' || true)" ] || para "el estado de la 33 tiene algo sin add o sin seguimiento"
[ "$(git -C "$B/pos" write-tree)" = "$(git -C "$B/pos" rev-parse $C54^{tree})" ] || para "el índice del estado de la 33 no es el árbol de 54e8b9f"
git clone -q "$CLON" "$B/limpio54"
git -C "$B/limpio54" -c advice.detachedHead=false checkout -q $C54
mkdir -p "$B/res"
W="$B/w"

correr() {   # <estado> <flujo> <versión> <ensayo> <repo> <argumentos del ensayo…>
  local estado=$1 nombre=$2 version=$3 ens=$4 repo=$5
  shift 5
  echo "== $estado $nombre $version"
  set +e
  python3 "$ens" "$repo" "$W" "$@" > "$B/salida.txt" 2>&1
  local rc=$?
  set -e
  mkdir -p "$B/res/$estado/$nombre"
  mv "$W" "$B/res/$estado/$nombre/$version"
  mv "$B/salida.txt" "$B/res/$estado/$nombre/$version.salida.txt"
  echo "$estado $nombre $version rc=$rc" | tee -a "$B/res/CODIGOS.txt"
}

for estado in limpio export; do
  for v in hoy arreglo; do
    if [ $v = hoy ]; then E=$HOY; else E=$ARR; fi
    correr $estado demo $v "$E" "$B/$estado" pruebas,negativo,positivo --flujo demo-ci
    correr $estado ejemplo $v "$E" "$B/$estado" ejemplo,ejemplo-propio --flujo ejemplo-ci
    correr $estado rojo $v "$E" "$B/$estado" rojo --flujo rojo-ci --rojo rojo
  done
done
correr pos demo hoy "$HOY" "$B/pos" pruebas,negativo,positivo --flujo demo-ci
correr pos demo arreglo "$ARR" "$B/pos" pruebas,negativo,positivo --flujo demo-ci
correr limpio54 demo hoy "$HOY" "$B/limpio54" pruebas,negativo,positivo --flujo demo-ci

echo "== la comparación"
python3 - "$B/res" "$C37" "$C54" <<'EOF'
import hashlib, json, os, re, subprocess, sys
R, c37, c54 = sys.argv[1], sys.argv[2], sys.argv[3]
CLAVES = ("flujo", "jobs", "esperado_rojo", "como_se_esperaba", "informes_iguales", "needs")
out = {"negativo": {}, "positivo": {}}


def rel(p):
    return os.path.relpath(p, R)


for estado in ("limpio", "export"):
    for n in ("demo", "ejemplo", "rojo"):
        h, a = os.path.join(R, estado, n, "hoy"), os.path.join(R, estado, n, "arreglo")
        eh, ea = [json.load(open(os.path.join(x, "ENSAYO.json"), encoding="utf-8")) for x in (h, a)]
        lineas = subprocess.run(["diff", "-rq", h, a], capture_output=True, text=True).stdout.splitlines()
        distintos = []
        for l in lineas:
            m = re.match(r"Files (.+) and (.+) differ$", l)
            if m:
                d = subprocess.run(["diff", m.group(1), m.group(2)], capture_output=True, text=True).stdout.splitlines()
                distintos.append({"fichero": rel(m.group(1)), "lineas_del_diff": d[:40], "n_lineas_del_diff": len(d)})
            else:
                distintos.append({"solo_en": l.replace(R + "/", "")})
        out["negativo"]["%s/%s" % (estado, n)] = {
            "claves_iguales": {k: eh.get(k) == ea.get(k) for k in CLAVES},
            "clon_en_el_arreglo": ea.get("clon"),
            "distintos": distintos}


def informe(d, job):
    p = os.path.join(d, job, "trabajo", "corrida", "INFORME.json")
    return hashlib.sha256(open(p, "rb").read()).hexdigest() if os.path.exists(p) else None


ph, pa, l54 = (os.path.join(R, "pos", "demo", "hoy"), os.path.join(R, "pos", "demo", "arreglo"),
               os.path.join(R, "limpio54", "demo", "hoy"))
sal = {k: open(d + ".salida.txt", encoding="utf-8").read() for k, d in (("hoy", ph), ("arreglo", pa), ("hoy_54", l54))}
ea = json.load(open(os.path.join(pa, "ENSAYO.json"), encoding="utf-8"))
out["positivo"] = {
    "lineas_del_laboratorio": {k: [l.strip() for l in s.splitlines() if "El laboratorio" in l] for k, s in sal.items()},
    "git_archive_del_head_viejo": {k: ("git archive %s" % c37[:12]) in s for k, s in sal.items()},
    "ultima_linea": {k: s.strip().splitlines()[-1] for k, s in sal.items()},
    "clon_en_el_arreglo": {k: ea.get("clon", {}).get(k) for k in ("tipo", "publicado", "head")},
    "arbol_de_54e8b9f": subprocess.run(["git", "-C", os.path.join(os.path.dirname(R), "pos"), "rev-parse", c54 + "^{tree}"],
                                       capture_output=True, text=True).stdout.strip(),
    "informes": {job: {"hoy_en_33": informe(ph, job), "arreglo_en_33": informe(pa, job), "hoy_en_54e8b9f": informe(l54, job)}
                 for job in ("negativo", "positivo")}}
json.dump(out, open(os.path.join(R, "CONTROLES-EN.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(json.dumps({"negativo": {k: (all(v["claves_iguales"].values()), len(v["distintos"])) for k, v in out["negativo"].items()},
                  "positivo": out["positivo"]["informes"]}, ensure_ascii=False, indent=1))
EOF
echo "fin=$(date +%H:%M)" > "$B/HECHO"
