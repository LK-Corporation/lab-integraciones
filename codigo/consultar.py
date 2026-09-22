#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Manda un encargo a un modelo externo y guarda la respuesta entera.

Generaliza lo que `pedir_ciego.py` hacia solo para el atacante ciego. Se
guarda la respuesta TAL CUAL, sin recortar ni reformatear, para que se pueda
comprobar despues que lo que se cito es lo que contesto el modelo.

La clave sale de ~/.config/lab-fase12/, nunca de la linea de ordenes ni del
entorno: las dos se ven en `ps`.

LAS DOS CLAVES, cada una a lo suyo:
     openrouter.key   cualquier modelo, via OpenRouter   -> prefijo "or:"
     deepseek.key     DeepSeek, VIA DIRECTA              -> sin prefijo

Pedir DeepSeek con el prefijo "or:" funciona, pero paga el margen de
OpenRouter teniendo llave directa, y ademas pierde los datos de uso que solo
da la via directa. El programa avisa cuando pasa.

Uso: python3 consultar.py <encargo.md> <modelo> <salida.md> [sistema]
     modelo = "deepseek-v4-pro" | "or:<proveedor>/<modelo>"
"""
import io
import json
import os
import sys
import time
import urllib.error
import urllib.request

CLAVES = os.path.expanduser("~/.config/lab-fase12")

SISTEMA = ("Eres consultor senior de arquitectura de sistemas con LLM y de "
           "metodologia experimental. Contestas en espanol, en Markdown, con "
           "concrecion tecnica y sin relleno. Cuando el encargo contiene un "
           "error de razonamiento, lo dices antes que nada.")


def clave(nombre):
    with io.open(os.path.join(CLAVES, nombre + ".key")) as fh:
        return fh.read().strip()


def pedir(modelo, sis, usr, intentos=3, plazo=1800):
    if modelo.startswith("or:"):
        url = "https://openrouter.ai/api/v1/chat/completions"
        auth, nombre = clave("openrouter"), modelo[3:]
        if "deepseek" in nombre.lower():
            # No se reenruta en silencio: ver la cabecera del parche.
            print("   AVISO: %s va por OpenRouter teniendo llave directa de"
                  " DeepSeek." % modelo)
            print("          Para la via directa, pide %s sin el prefijo."
                  % nombre.split("/")[-1])
    else:
        url = "https://api.deepseek.com/chat/completions"
        auth, nombre = clave("deepseek"), modelo
    cuerpo = {"model": nombre, "temperature": 0.3,
              "messages": [{"role": "system", "content": sis},
                           {"role": "user", "content": usr}]}
    datos = json.dumps(cuerpo).encode("utf-8")
    ultimo = ""
    for n in range(intentos):
        req = urllib.request.Request(url, data=datos, method="POST")
        req.add_header("Authorization", "Bearer " + auth)
        req.add_header("Content-Type", "application/json")
        try:
            with urllib.request.urlopen(req, timeout=plazo) as r:
                d = json.loads(r.read().decode("utf-8"))
            m = d["choices"][0]["message"]
            txt = m.get("content") or ""
            raz = m.get("reasoning") or m.get("reasoning_content") or ""
            uso = dict(d.get("usage") or {})
            # El endpoint de verdad, no la cadena que se pidio: es lo que
            # hace falta para reproducir.
            uso["_endpoint"] = url.split("/")[2]
            return txt, raz, uso
        except urllib.error.HTTPError as e:
            ultimo = "HTTP %d: %s" % (e.code,
                                      e.read().decode("utf-8", "replace")[:300])
        except Exception as e:                                   # noqa: BLE001
            ultimo = "%s: %s" % (type(e).__name__, e)
        if n + 1 < intentos:
            time.sleep(5 * (n + 1))
    raise RuntimeError(ultimo)


def main():
    if len(sys.argv) < 4:
        raise SystemExit(__doc__)
    encargo = io.open(sys.argv[1], encoding="utf-8").read()
    modelo, salida = sys.argv[2], sys.argv[3]
    sis = sys.argv[4] if len(sys.argv) > 4 else SISTEMA
    if os.path.exists(salida):
        raise SystemExit("ABORTA: %s ya existe. No se pisa una respuesta."
                         % salida)
    t0 = time.time()
    print("  %-42s <- %d caracteres" % (modelo, len(encargo)), flush=True)
    txt, raz, uso = pedir(modelo, sis, encargo)
    cab = ("<!-- modelo: %s · via: %s · encargo: %s · %d s · %s tokens -->\n\n"
           % (modelo, uso.get("_endpoint", "?"),
              os.path.basename(sys.argv[1]), time.time() - t0,
              uso.get("total_tokens", "?")))
    with io.open(salida, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(cab + txt)
        if raz:
            fh.write("\n\n---\n\n## Razonamiento del modelo\n\n" + raz)
    print("  %-42s -> %s (%d car., %.0f s)"
          % (modelo, salida, len(txt), time.time() - t0), flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
