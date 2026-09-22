#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Le pasa un ESTADO y unas PREGUNTAS TIPADAS a Jev, y guarda sus decisiones.

POR QUE HACE FALTA UN PROGRAMA APARTE. `consultar.py` habla `chat/completions`
y Jev no: vive en `POST /api/alpha/decisions`, que es otro endpoint y otra
forma. Por eso `typesafe/jev-1.13` no aparece en `/api/v1/models` y buscarlo
ahi da cero. Ver `nota_jev.md`.

QUE ES Y QUE NO. No genera texto. Recibe un estado y un mapa de preguntas
tipadas -`noul` si/no, `choice` una de varias, `score` ordinal- y devuelve
decisiones CON PROBABILIDAD CALIBRADA. Es lo unico del panel que da un numero
calibrado en vez de prosa y conviccion.

Y SU LIMITE, que va escrito aqui para que viaje con el resultado: juzga EL
ESTADO QUE SE LE ESCRIBE, no el repositorio. No puede ir a leer los bundles ni
el catalogo. Hereda el encuadre de quien redacta el estado, asi que NO es un
revisor mas: es una segunda opinion sobre un resumen. Si el resumen esta
sesgado, Jev lo confirma con dos decimales.

EL ESCOLLO, Y SON DOS. En `choice`, `criteria` va como REGISTRO
`opcion -> descripcion` -no una lista, no una cadena JSON-, que es lo que decia
la nota. Y en `score` va como LISTA ordenada de niveles. Pedir un `score` con
`criteria` en forma de registro da HTTP 400 diciendo `expected array`. El
programa comprueba las dos formas ANTES de gastar la llamada.

LA CLAVE sale de ~/.config/lab-fase12/, nunca de la linea de ordenes ni del
entorno: las dos se ven en `ps`.

Uso: python3 decidir.py <estado.md> <preguntas.json> <salida.md>
     python3 decidir.py <estado.md> <preguntas.json> <salida.md> --crudo
"""
import io
import json
import os
import sys
import time
import urllib.error
import urllib.request

CLAVES = os.path.expanduser("~/.config/lab-fase12")
URL = "https://openrouter.ai/api/alpha/decisions"
MODELO = "typesafe/jev-1.13"


def clave(nombre):
    with io.open(os.path.join(CLAVES, nombre + ".key")) as fh:
        return fh.read().strip()


def pedir(estado, preguntas, intentos=3, plazo=600):
    cuerpo = {"model": MODELO, "state": estado, "questions": preguntas}
    datos = json.dumps(cuerpo, ensure_ascii=False).encode("utf-8")
    ultimo = ""
    for n in range(intentos):
        req = urllib.request.Request(URL, data=datos, method="POST")
        req.add_header("Authorization", "Bearer " + clave("openrouter"))
        req.add_header("Content-Type", "application/json")
        try:
            with urllib.request.urlopen(req, timeout=plazo) as r:
                return json.loads(r.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            # El cuerpo del error ENTERO: si la forma de la peticion esta mal,
            # es lo unico que lo dice. Recortarlo aqui costaria una iteracion.
            ultimo = "HTTP %d\n%s" % (e.code, e.read().decode("utf-8",
                                                              "replace"))
            if e.code in (400, 404, 422):
                break          # no se reintenta un error de forma
        except Exception as e:                                   # noqa: BLE001
            ultimo = "%s: %s" % (type(e).__name__, e)
        if n + 1 < intentos:
            time.sleep(5 * (n + 1))
    raise RuntimeError(ultimo)


def formatea(nombre, a):
    """Una respuesta, legible, sin perder nada de lo que trae."""
    t = a.get("type", "?")
    if t == "noul":
        return "- **%s** (noul): **%s**" % (nombre, a.get("noul"))
    if t == "choice":
        probs = a.get("probabilities") or {}
        orden = sorted(probs.items(), key=lambda kv: -kv[1])
        detalle = " · ".join("%s %s" % (k, v) for k, v in orden)
        return ("- **%s** (choice): **%s**   [confianza %s]\n  %s"
                % (nombre, a.get("choice"), a.get("confidence"), detalle))
    if t == "score":
        return ("- **%s** (score): **%s**   [confianza %s]"
                % (nombre, a.get("score"), a.get("confidence")))
    return "- **%s** (%s): %s" % (nombre, t, json.dumps(a, ensure_ascii=False))


def main():
    if len(sys.argv) < 4:
        raise SystemExit(__doc__)
    ruta_estado, ruta_preg, salida = sys.argv[1:4]
    crudo = "--crudo" in sys.argv
    if os.path.exists(salida):
        raise SystemExit("ABORTA: %s ya existe. No se pisa una respuesta."
                         % salida)

    estado = io.open(ruta_estado, encoding="utf-8").read()
    preguntas = json.load(io.open(ruta_preg, encoding="utf-8"))

    # Control de forma antes de gastar la llamada: el escollo de la nota.
    FORMA = {"choice": (dict, "un registro opcion->descripcion"),
             "score": (list, "una lista ordenada de niveles")}
    for k, q in preguntas.items():
        esperado = FORMA.get(q.get("type"))
        if esperado and not isinstance(q.get("criteria"), esperado[0]):
            raise SystemExit("La pregunta %r es de tipo %s, asi que `criteria` "
                             "tiene que ser %s, y es %s"
                             % (k, q.get("type"), esperado[1],
                                type(q.get("criteria")).__name__))

    t0 = time.time()
    print("  %-22s <- estado %d car., %d preguntas"
          % (MODELO, len(estado), len(preguntas)), flush=True)
    d = pedir(estado, preguntas)
    seg = time.time() - t0

    ans = d.get("answers") or {}
    uso = d.get("usage") or {}
    cab = ("<!-- modelo: %s · via: openrouter.ai/api/alpha/decisions · estado: "
           "%s · %d s · %s in / %s out · coste %s -->\n\n"
           % (MODELO, os.path.basename(ruta_estado), seg,
              uso.get("input_tokens", "?"), uso.get("output_tokens", "?"),
              uso.get("cost", "?")))

    cuerpo = ["# Decisiones de Jev sobre %s\n" % os.path.basename(ruta_estado),
              "> Jev juzga **el estado que se le escribe**, no el repositorio.",
              "> No es un revisor mas: es una segunda opinion sobre un resumen.\n"]
    for k in preguntas:
        if k in ans:
            cuerpo.append(formatea(k, ans[k]))
        else:
            cuerpo.append("- **%s**: SIN RESPUESTA" % k)
    for k in ans:
        if k not in preguntas:
            cuerpo.append(formatea(k + " (no preguntada)", ans[k]))
    if crudo:
        cuerpo.append("\n---\n\n## Respuesta cruda\n\n```json\n%s\n```"
                      % json.dumps(d, ensure_ascii=False, indent=2))

    with io.open(salida, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(cab + "\n".join(cuerpo) + "\n")
    print("  %-22s -> %s (%d respuestas, %.0f s)"
          % (MODELO, salida, len(ans), seg), flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
