#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Etapa 35, tras la revisión a ciegas (bloqueante 1 y menor 4; M17 a M28, de su segunda pasada): mutantes de
cv/ci/comprobar_publicado.py. Cada uno rompe a propósito una cosa que la comprobación tiene que hacer, y alguna P-CR tiene que caer
con él. Trabaja en una copia de la carpeta
verificador/ que se le da (una exportación del público), y en cada mutante corre solo las P-CR, en un proceso aparte. Escribe una
línea por mutante y, al final, cuántos mueren. Sale con 0 si mueren todos. No se publica la copia.
  python3 cr/mutantes_cr.py <verificador/ de una exportación del índice> [<salida.txt>]"""
import os
import shutil
import subprocess
import sys
import tempfile

MUTANTES = [
    ("M1, iguales siempre", '"igual": e["arbol"] == arbol', '"igual": True'),
    ("M2, sin las rutas que difieren", "    return [l for l in salida(git(repo, \"diff\"", "    return []\n    return [l for l in salida(git(repo, \"diff\""),
    ("M3, dos ensayos del mismo flujo no paran", 'raise NoSePuede("dos ensayos de %s" % e["flujo"])', 'pass'),
    ("M4, el umbral de los commits intermedios", 'c["commits_nuevos"] > (1 if e["tipo"] == "arbol" else 0)', 'c["commits_nuevos"] > 0'),
    ("M5, sin el aviso de otra historia", 'if c["igual"] and c["otra_historia"]:', 'if False:'),
    ("M6, sin los jobs mínimos", 'faltan = [j for j in minimos.get(f, []) if j not in e["jobs"]] or ([] if e["jobs"] else ["ningún job"])',
     'faltan = []'),
    ("M7, sin el aviso de un ensayo en rojo", 'elif e["rojo"]:', 'elif False:'),
    ("M8, la fusión con conflictos como si no los hubiera", 'return arbol if r.returncode == 0 and SHA40.match(arbol) else None',
     'return arbol if SHA40.match(arbol) else None'),
    ("M9, un flujo sin ensayo no abre el círculo", 'abiertos.append("%s sin ensayo" % f)', 'pass'),
    ("M10, sin fetch", '        git(repo, "fetch", "-q", remoto, rama)\n', '        pass\n'),
    ("M11, la rama de seguimiento del clon en vez del remoto", 'r = git(repo, "ls-remote", remoto, "refs/heads/" + rama)',
     'r = git(repo, "show-ref", "refs/remotes/%s/%s" % (remoto, rama))'),
    ("M12, el HEAD del clon en vez del remoto", 'commit = lineas[0].split()[0]', 'commit = salida(git(repo, "rev-parse", "HEAD"))'),
    ("M13, ningún flujo da verde", '        if not flujos:\n', '        if False:\n'),
    ("M14, un ENSAYO.json raro no para", '    def raro(que):\n        raise NoSePuede(', '    def raro(que):\n        return\n        raise NoSePuede('),
    ("M15, sin la frase del amend", 'c["amend"] = e["tipo"] == "commit" and not desciende', 'c["amend"] = False'),
    ("M16, un ensayo que no ensayó pasa por uno sin árbol", 'if d.get("no_ensayado"):', 'if False:'),
    # M17 a M28: los que probó la segunda pasada de la revisión a ciegas, con este mismo arnés
    ("M17, otro árbol no abre el círculo", 'abiertos.append("%s se ensayó sobre otro árbol" % f)', 'pass'),
    ("M18, la fusión siempre igual", '"igual": fa is not None and fa in ensayados}', '"igual": True}'),
    ("M19, la fusión sin fetch de la base", 'if git(repo, "fetch", "-q", remoto, base).returncode != 0:', 'if False:'),
    ("M20, main no captura los argumentos", 'except (IndexError, ValueError) as ex:', 'except ZeroDivisionError as ex:'),
    ("M21, el diff al revés", 'ensayado, publicado_)).splitlines()', 'publicado_, ensayado)).splitlines()'),
    ("M22, igual contra el árbol del HEAD del clon", '"igual": e["arbol"] == arbol',
     '"igual": e["arbol"] == salida(git(repo, "rev-parse", "HEAD^{tree}"))'),
    ("M23, un ENSAYO.json sin árbol no abre", 'abiertos.append("%s: %s" % (f, motivo.split(" (")[0].split(":")[0]))', 'pass'),
    ("M24, un job que falta no abre", 'abiertos.append("%s no corrió %s" % (f, ", ".join(faltan)))', 'pass'),
    ("M25, el rojo al revés", 'if not v]\n', 'if v]\n'),
    ("M26, ignora --remoto", 'remoto, rama = opts["--remoto"], opts["--rama"]', 'remoto, rama = "origin", opts["--rama"]'),
    ("M27, el código 0 aunque haya abiertos", '            res["codigo"] = 1\n', '            res["codigo"] = 0\n'),
    ("M28, otro árbol solo abre si lista rutas", '            if not c["igual"]:\n                abiertos.append',
     '            if not c["igual"] and c["diferencia"]:\n                abiertos.append'),
    ("M29, main no captura un fichero que no se lee o no se escribe", '    except OSError as ex:', '    except ZeroDivisionError as ex:'),
]
SOLO_CR = r'''
import sys
sys.argv = ["x"]
sys.path.insert(0, "cv/ci")
import prueba_ci as P
for p in [p for p in P.PRUEBAS if p.__name__.startswith("cr")]:
    P.grupo[0] = "P-CR-%d" % int(p.__name__[2:])
    try:
        p()
    except Exception as ex:
        P.FALLAN.add(P.grupo[0])
import shutil
shutil.rmtree(P.RAIZ, ignore_errors=True)                                  # la carpeta temporal de las pruebas
print("CAEN:", " ".join(sorted(P.FALLAN, key=lambda x: int(x.split("-")[-1]))) or "ninguna")
'''


def main(origen, salida=None):
    raiz = tempfile.mkdtemp(prefix="mutantes_cr_")
    v = os.path.join(raiz, "verificador")
    shutil.copytree(origen, v, ignore=shutil.ignore_patterns("__pycache__"))
    ruta = os.path.join(v, "cv", "ci", "comprobar_publicado.py")
    original = open(ruta, encoding="utf-8").read()
    lineas, vivos = [], []
    base = subprocess.run([sys.executable, "-c", SOLO_CR], cwd=v, capture_output=True, text=True).stdout.strip().splitlines()[-1:]
    lineas.append("sin mutar: %s" % (base[0] if base else "sin salida"))
    for nombre, viejo, nuevo in MUTANTES:
        assert original.count(viejo) == 1, "%s: el texto no está o no es único" % nombre
        open(ruta, "w", encoding="utf-8").write(original.replace(viejo, nuevo))
        r = subprocess.run([sys.executable, "-c", SOLO_CR], cwd=v, capture_output=True, text=True)
        caen = (r.stdout.strip().splitlines() or ["CAEN: (sin salida) " + r.stderr.strip()[-200:]])[-1]
        muere = not caen.endswith("ninguna")
        lineas.append("%s: %s  %s" % ("muere" if muere else "VIVE ", nombre, caen))
        if not muere:
            vivos.append(nombre)
    open(ruta, "w", encoding="utf-8").write(original)
    lineas.append("mueren %d de %d" % (len(MUTANTES) - len(vivos), len(MUTANTES)))
    texto = "\n".join(lineas) + "\n"
    print(texto, end="")
    if salida:
        open(salida, "w", encoding="utf-8").write(texto)
    shutil.rmtree(raiz, ignore_errors=True)
    return 0 if not vivos and base and base[0].endswith("ninguna") else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None))
