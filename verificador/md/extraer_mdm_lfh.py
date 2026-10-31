#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Etapa 26 (MD-pre, E-MD-2): saca los mensajes MDM de los literales de las pruebas Java de LinuxForHealth, como se hizo con
VXU en la etapa 20 (vx/VX2.md, «La re-extracción»). Un lexer con estados (código, cadena, carácter, comentario de línea y de
bloque, bloque de texto) recorre cada fichero, ignora los comentarios y concatena los literales "..." de cada sentencia (hasta
el ';', '{' o '}' en código). Una expresión entre dos literales (`" + message + "`) deja una marca. Si la prueba es @ParameterizedTest
con @ValueSource(strings = {...}), la marca se sustituye por cada valor y sale un mensaje por valor; si no, queda como
<VARIABLE> y el manifiesto lo dice. Una sentencia es un mensaje si su texto empieza por MSH y su MSH-9 contiene MDM^. Resuelve
los escapes de Java y no normaliza los separadores: cada segmento queda con el salto que usa la prueba. Solo lee; con -I.
  python3 -I md/extraer_mdm_lfh.py <src/test de la copia fijada> <carpeta de salida vacía> <descripción de la fuente>"""
import hashlib
import os
import re
import sys

ESCAPES = {"n": "\n", "r": "\r", "t": "\t", "b": "\b", "f": "\f", "0": "\0", "\\": "\\", '"': '"', "'": "'", "s": " "}
MARCA = "\x00"


def sin_escapes(s):
    out, i = [], 0
    while i < len(s):
        c = s[i]
        if c == "\\" and i + 1 < len(s):
            n = s[i + 1]
            if n == "u":
                j = i + 2
                while j < len(s) and s[j] == "u":
                    j += 1
                out.append(chr(int(s[j:j + 4], 16)))
                i = j + 4
                continue
            out.append(ESCAPES.get(n, n))
            i += 2
            continue
        out.append(c)
        i += 1
    return "".join(out)


def sentencias(texto):
    """-> [(offset de inicio, línea de inicio, texto con MARCA donde había una expresión entre literales)] por sentencia."""
    res, partes, inicio, i, n, linea, hueco = [], [], None, 0, len(texto), 1, []

    def literal(valor, desde):
        nonlocal inicio, hueco
        if inicio is None:
            inicio = (desde, linea)
        elif re.sub(r"[\s+]", "", "".join(hueco)):
            partes.append(MARCA)
        partes.append(valor)
        hueco = []

    while i < n:
        c = texto[i]
        if texto.startswith("//", i):
            j = texto.find("\n", i)
            i = n if j < 0 else j
            continue
        if texto.startswith("/*", i):
            j = texto.find("*/", i + 2)
            j = n if j < 0 else j + 2
            linea += texto.count("\n", i, j)
            i = j
            continue
        if texto.startswith('"""', i):
            j = texto.find('"""', i + 3)
            j = n if j < 0 else j
            cuerpo = texto[i + 3:j]
            cuerpo = cuerpo[cuerpo.find("\n") + 1:] if "\n" in cuerpo else cuerpo
            literal(sin_escapes(cuerpo), i)
            linea += texto.count("\n", i, j + 3)
            i = j + 3
            continue
        if c == '"':
            j = i + 1
            while j < n and texto[j] != '"':
                j += 2 if texto[j] == "\\" else 1
            literal(sin_escapes(texto[i + 1:j]), i)
            i = j + 1
            continue
        if c == "'":
            j = i + 1
            while j < n and texto[j] != "'":
                j += 2 if texto[j] == "\\" else 1
            i = j + 1
            continue
        if c == "\n":
            linea += 1
        if c in ";{}":   # también las llaves: los literales de una anotación no se pegan al cuerpo
            if partes:
                res.append((inicio[0], inicio[1], "".join(partes)))
            partes, inicio, hueco = [], None, []
        elif inicio is not None:
            hueco.append(c)
        i += 1
    return res


def valores_parametrizados(texto, offset):
    """-> los strings del @ValueSource de la prueba que contiene `offset`, si la anotación más cercana es @ParameterizedTest."""
    antes = texto[:offset]
    anot = [(m.start(), m.group(1)) for m in re.finditer(r"@(Test|ParameterizedTest)\b", antes)]
    if not anot or anot[-1][1] != "ParameterizedTest":
        return None
    m = re.search(r"@ValueSource\s*\(\s*strings\s*=\s*\{([^}]*)\}", antes[anot[-1][0]:])
    return [sin_escapes(v) for v in re.findall(r'"((?:[^"\\]|\\.)*)"', m.group(1))] if m else None


def main(origen, salida, fuente):
    assert not os.path.exists(salida) or not os.listdir(salida), "la carpeta de salida tiene que estar vacía"
    os.makedirs(salida, exist_ok=True)
    filas = []
    for raiz, _, ficheros in sorted(os.walk(origen)):
        for f in sorted(ficheros):
            if not f.endswith(".java"):
                continue
            ruta = os.path.join(raiz, f)
            texto = open(ruta, encoding="utf-8").read()
            for offset, linea, m in sentencias(texto):
                if not m.startswith("MSH"):
                    continue
                valores = valores_parametrizados(texto, offset) if MARCA in m else None
                variantes = [(v, m.replace(MARCA, v)) for v in valores] if valores else [("", m.replace(MARCA, "<VARIABLE>"))]
                for valor, msg in variantes:
                    campos = re.split(r"[\r\n]", msg, 1)[0].split(msg[3]) if len(msg) > 3 else []
                    msh9 = campos[8] if len(campos) > 8 else ""
                    if "MDM^" not in msh9:
                        continue
                    msh12 = campos[11] if len(campos) > 11 else ""
                    b = msg.encode("utf-8")
                    sufijo = "__" + re.sub(r"[^A-Za-z0-9]", "", valor) if valor else ""
                    nombre = "%s__L%d%s.hl7" % (f[:-5], linea, sufijo)
                    nota = ("parametro=%s" % valor) if valor else ("CON <VARIABLE>" if "<VARIABLE>" in msg else "")
                    open(os.path.join(salida, nombre), "wb").write(b)
                    filas.append("\t".join([f, str(linea), msh9, msh12, str(len(b)), hashlib.sha256(b).hexdigest(), nombre, nota]))
    cab = ["MANIFIESTO — mensajes MDM de LinuxForHealth hl7v2-fhir-converter",
           "Fuente: %s" % fuente,
           "Origen: literales de cadena de las pruebas Java, leídos por md/extraer_mdm_lfh.py: ignora los comentarios, concatena",
           "  los literales de cada sentencia y resuelve los escapes de Java, sin normalizar los saltos. Una expresión entre literales",
           "  se sustituye por cada valor del @ValueSource de su prueba (un mensaje por valor) o queda como <VARIABLE>.",
           "Cada fila: fichero Java, línea de inicio (1-indexada), MSH-9, MSH-12, bytes, sha256, fichero .hl7, nota.", "",
           "fichero\tlinea\tmsh9\tmsh12\tbytes\tsha256\tsalida\tnota"]
    open(os.path.join(salida, "MANIFIESTO.txt"), "w", encoding="utf-8").write("\n".join(cab + filas) + "\n")
    print("%d mensajes MDM" % len(filas))
    for f in filas:
        print("  " + f)


if __name__ == "__main__":
    main(*sys.argv[1:4])
