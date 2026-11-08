#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Etapa 37: con el juez nuevo, la Observation de ACC o PDA ya no sale como «recurso_inventado» con hecho OBX (el mecanismo
MC-ORU-7 por el que el estudio reconocía M-28) sino como «recurso_sin_mapa» (fuera:Observation|recurso_sin_mapa). M-28 reconoce
también ese mecanismo; sin esto se quedaría sin casos y las ya declaradas pasarían de 31 a 30. Y la marca de la etapa en
cv/RESULTADO-CV3.md. Conserva los finales de línea (cv3_clases.py va en CRLF). Los JSON de clases pasados no se tocan.
Afirma cada texto. Idempotente.
- Sin argumentos, en el laboratorio: además, el bloque 8 del sello de la etapa 33, con la huella nueva de cv/cv3_clases.py.
- Con el clon público: en sus copias (verificador/…), en su sitio.
  cd fase12 && python3 jz/parche_m28_jz.py [<clon público>]"""
import datetime
import hashlib
import os
import sys

FASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VIEJO = '("M-28", MS, {"MC-ORU-7"}, None, ("ms-ADT",),'
NUEVO = '("M-28", MS, {"MC-ORU-7", "fuera:Observation|recurso_sin_mapa"}, None, ("ms-ADT",),'
MARCA_VIEJA = "## Marca de la etapa 37 (7-nov-2026)"         # la fecha, a la de la etapa publicada (8-nov, tras la revisión a ciegas)
MARCA = """## Marca de la etapa 37 (8-nov-2026)

El juez de la etapa 37 (`RESULTADO-JUEZ.md`) deja de contar mal las dos conductas que encontró la etapa 36. Con él, el corpus de
este estudio da la misma frase (15 nuevas, 31 ya declaradas, 16 convenciones):
- **M-28:** la Observation de ACC o de PDA sale ahora como «recurso sin mapa», con el segmento por hecho. `cv/cv3_clases.py`
  reconoce también ese mecanismo (bloque 8 del sello de la etapa 33); sin él, M-28 se quedaría sin casos.
- **L-4:** suma 4 casos (`A1-A02-09`, `A1-A11-25`, `A1-A11-29` y `A1-A13-34`). LinuxForHealth los rechaza por el tipo de
  mensaje, y el juez de antes daba el rechazo por aceptable por su PID-8 `X` o `Z`.

`cv/CLASES-CV3.json` no se toca: conserva la huella de su juez.
"""
PUB = sys.argv[1] if len(sys.argv) > 1 else None


def ruta(rel):
    return os.path.join(PUB, "verificador", rel) if PUB else os.path.join(FASE, rel)


p = ruta("cv/cv3_clases.py")
t = open(p, encoding="utf-8", newline="").read()
if NUEVO not in t:
    assert t.count(VIEJO) == 1, "%s: no está (o no es único): %r" % (p, VIEJO)
    open(p, "w", encoding="utf-8", newline="").write(t.replace(VIEJO, NUEVO))
print("%s: M-28 con fuera:Observation|recurso_sin_mapa" % p)

p = ruta("cv/RESULTADO-CV3.md")
t = open(p, encoding="utf-8", newline="").read()
nl = "\r\n" if "\r\n" in t else "\n"
marca = MARCA.replace("\n", nl)
if MARCA_VIEJA in t:
    assert t.count(MARCA_VIEJA) == 1, "%s: la marca vieja no es única" % p
    t = t.replace(MARCA_VIEJA, MARCA.split("\n")[0])
    open(p, "w", encoding="utf-8", newline="").write(t)
if "## Marca de la etapa 37" not in t:
    nota = nl + nl + "> *Copia pública"
    if nota in t:
        assert t.count(nota) == 1, "%s: la nota de copia pública no es única" % p
        t = t.replace(nota, nl + nl + marca.rstrip(nl) + nota)
    else:
        t = t.rstrip(nl) + nl + nl + marca
    open(p, "w", encoding="utf-8", newline="").write(t)
print("%s: marca de la etapa 37" % p)

if not PUB:
    S = os.path.join(FASE, "ga", "SELLO-GA.txt")
    t = open(S, encoding="utf-8", newline="").read()
    h = hashlib.sha256(open(os.path.join(FASE, "cv", "cv3_clases.py"), "rb").read()).hexdigest()
    bueno = "bloque 8" in t and t.endswith("%s  cv/cv3_clases.py\n" % h)
    if not bueno:
        if "bloque 8" in t:
            t = t[:t.index("SELLO DE LA ETAPA 33, bloque 8")]
        assert "bloque 7" in t, "falta el bloque 7"
        ahora = datetime.datetime.now().strftime("%d-nov-%Y, %H:%M").lstrip("0")
        t = t.rstrip("\n") + "\n" + ("\nSELLO DE LA ETAPA 33, bloque 8 (%s): desde la etapa 37, M-28 reconoce también el hallazgo nuevo "
                                     "del juez (jz/decision-jev-jz.md, Q-JZ-2 a)\n# M-28: {MC-ORU-7} -> {MC-ORU-7, "
                                     "fuera:Observation|recurso_sin_mapa}; la clase, su texto y sus casos no cambian\n%s  cv/cv3_clases.py\n" % (ahora, h))
        open(S, "w", encoding="utf-8", newline="").write(t)
    print("ga/SELLO-GA.txt: bloque 8 (%s)%s" % (h[:12], ", ya estaba" if bueno else ""))
