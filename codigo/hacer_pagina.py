# -*- coding: utf-8 -*-
"""Envuelve la pagina del informe para que se sirva sola en GitHub Pages.

POR QUE HACE FALTA ENVOLVERLA. `informe.html` se escribio para la plataforma de
artifacts, que anade por su cuenta el doctype, el <head> y un reset minimo. Un
servidor estatico no hace nada de eso, asi que aqui se pone lo que falta:
la cabecera, el reset equivalente, y las etiquetas que hacen que el enlace se
vea bien cuando alguien lo comparte.

Lo que NO se toca es el cuerpo ni el CSS: es la misma pagina.

Uso: python3 hacer_pagina.py <informe.html> <docs/index.html>
"""
import io
import re
import sys

REPO = "https://github.com/LK-Corporation/lab-integraciones"
SITIO = "https://lk-corporation.github.io/lab-integraciones/"
DESC = ("Un agente local de 30B triando fallos de integracion HL7 v2 hacia FHIR: "
        "funciona y no hace falta. El hallazgo que se lleva el trabajo es del metodo.")

CABECERA = """<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="description" content="%(desc)s">
<meta name="color-scheme" content="light dark">
<link rel="canonical" href="%(sitio)s">

<meta property="og:type" content="article">
<meta property="og:title" content="El agente que no hacia falta">
<meta property="og:description" content="%(desc)s">
<meta property="og:url" content="%(sitio)s">
<meta name="twitter:card" content="summary">

<style>
  *, *::before, *::after { box-sizing: border-box; }
  html { color-scheme: light dark; -webkit-text-size-adjust: 100%%; }
  body { margin: 0; }
  img { max-width: 100%%; }
  [hidden] { display: none !important; }
  .volver {
    display: inline-block;
    margin-top: .9rem;
    font-family: var(--sans);
    font-size: .8125rem;
  }
</style>
""" % {"desc": DESC, "sitio": SITIO}

PIE = """
<p style="max-width:50rem;margin:0 auto;padding:0 20px 3rem;font-family:var(--sans);
   font-size:.8125rem;color:var(--ink-faint)">
  El c&oacute;digo, el dise&ntilde;o, las revisiones externas y las predicciones selladas est&aacute;n en
  <a href="%s" style="color:var(--accent)">github.com/LK-Corporation/lab-integraciones</a>.
</p>
</body>
</html>
""" % REPO


def main():
    if len(sys.argv) < 3:
        raise SystemExit(__doc__)
    t = io.open(sys.argv[1], encoding="utf-8").read()

    # El <title> y el <link> de fuentes viven al principio del cuerpo suelto:
    # se suben a la cabecera, que es su sitio en un documento completo.
    m_t = re.search(r"<title>.*?</title>\s*", t, re.S)
    m_l = re.search(r'<link rel="stylesheet"[^>]*>\s*', t)
    titulo = m_t.group(0).strip() if m_t else "<title>El agente que no hacía falta</title>"
    fuentes = m_l.group(0).strip() if m_l else ""
    cuerpo = t
    if m_t:
        cuerpo = cuerpo.replace(m_t.group(0), "", 1)
    if m_l:
        cuerpo = cuerpo.replace(m_l.group(0), "", 1)

    salida = (CABECERA.replace("<style>", titulo + "\n" + fuentes + "\n<style>", 1)
              + "</head>\n<body>\n" + cuerpo.strip() + "\n" + PIE)

    io.open(sys.argv[2], "w", encoding="utf-8", newline="\n").write(salida)
    print("escrita %s (%d caracteres)" % (sys.argv[2], len(salida)))
    for etiqueta in ("<!doctype html>", "<title>", "og:title", "</head>", "<body>",
                     "</body>", "</html>"):
        print("  %-18s %s" % (etiqueta, "si" if etiqueta in salida else "NO <<<"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
