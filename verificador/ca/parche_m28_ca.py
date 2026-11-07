#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Etapa 36 (Q-CA-2, ca/decision-jev-ca3.md y ca3b): la descripción de M-28 se queda corta. También cuenta la Observation de ACC
(injury-incident), como en la muestra ADT-A31-01, que lleva ACC y no PDA. Se corrige en la tabla de cv/RESULTADO-CV3.md, con su
marca, y en cv/cv3_clases.py. Los finales de línea de cada fichero se conservan (cv3_clases.py va en CRLF). Los JSON de clases de las
corridas pasadas no se tocan. Afirma cada texto. Idempotente.
- Sin argumentos, en el laboratorio: además, el bloque 7 del sello de la etapa 33, con la huella nueva de cv/cv3_clases.py.
- Con el clon público: en sus copias (verificador/…), que no son iguales a las del laboratorio (la de RESULTADO-CV3.md lleva una
  nota de copia pública).
  cd fase12 && python3 ca/parche_m28_ca.py [<clon público>]"""
import datetime
import hashlib
import os
import sys

FASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CAMBIOS = [
    ("cv/RESULTADO-CV3.md", "| M-28 | Observation de PDA | salidas esperadas |",
     "| M-28 | Observation de PDA o de ACC (descripción corregida en la etapa 36) | salidas esperadas |"),
    ("cv/cv3_clases.py", '     "Observation de PDA (certificado de defunción, autopsia…) que la guía no mapea"),',
     '     "Observation de PDA (certificado de defunción, autopsia…) o de ACC (injury-incident) que la guía no mapea"),'),
]
PUB = sys.argv[1] if len(sys.argv) > 1 else None
for rel, viejo, nuevo in CAMBIOS:
    p = os.path.join(PUB, "verificador", rel) if PUB else os.path.join(FASE, rel)
    t = open(p, encoding="utf-8", newline="").read()
    if nuevo not in t:
        assert t.count(viejo) == 1, "%s: no está (o no es único): %r" % (p, viejo[:70])
        open(p, "w", encoding="utf-8", newline="").write(t.replace(viejo, nuevo))
    print("%s: M-28, con ACC" % p)

if not PUB:
    S = os.path.join(FASE, "ga", "SELLO-GA.txt")
    t = open(S, encoding="utf-8", newline="").read()
    h = hashlib.sha256(open(os.path.join(FASE, "cv", "cv3_clases.py"), "rb").read()).hexdigest()
    bueno = "bloque 7" in t and t.endswith("%s  cv/cv3_clases.py\n" % h) and "\n\n\nSELLO DE LA ETAPA 33, bloque 7" not in t
    if not bueno:                                                           # si ya está con la huella buena, no se toca
        if "bloque 7" in t:
            t = t[:t.index("SELLO DE LA ETAPA 33, bloque 7")]
        assert "bloque 6" in t, "falta el bloque 6"
        ahora = datetime.datetime.now().strftime("%d-nov-%Y, %H:%M").lstrip("0")
        t = t.rstrip("\n") + "\n" + ("\nSELLO DE LA ETAPA 33, bloque 7 (%s): desde la etapa 36, la descripción de M-28 corregida (Q-CA-2, "
                                     "ca/decision-jev-ca3.md)\n# M-28 también cuenta la Observation de ACC (injury-incident); solo "
                                     "cambia su texto, no la clase ni sus casos\n%s  cv/cv3_clases.py\n" % (ahora, h))
        open(S, "w", encoding="utf-8", newline="").write(t)
    print("ga/SELLO-GA.txt: bloque 7 (%s)%s" % (h[:12], "" if not bueno else ", ya estaba"))
