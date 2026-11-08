#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Etapa 38 (cl/diseno-cl-fable.md §1 y §3, con cl/decision-jev-cl.md, Q-CL-1 a): la regla de M-4 reconoce también el texto con que
el juez de CV4 escribe el hallazgo de PL.9 de Microsoft («… contiene PL.9 … sin ser PL.9»), además del de CV3 («falta la
descripción»); regla() admite una tupla de textos, de los que basta uno. Y la marca de la etapa en cv/RESULTADO-CV3.md. Conserva los
finales de línea (cv3_clases.py va en CRLF). Los JSON de clases pasados no se tocan. Afirma cada texto. Idempotente.
- Sin argumentos, en el laboratorio: además, el bloque 9 del sello de la etapa 33, con la huella nueva de cv/cv3_clases.py.
- Con el clon público: en sus copias (verificador/…), en su sitio.
  cd fase12 && python3 cl/parche_m4_cl.py [<clon público>]"""
import datetime
import hashlib
import os
import sys

FASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CAMBIOS = [
    ('# (id, conversor, mecanismos, texto que debe estar en el «que» o None, casos o prefijos de caso o None,',
     '# (id, conversor, mecanismos, texto que debe estar en el «que» (o tupla de textos, de los que basta uno) o None, casos o prefijos de caso o None,'),
    ('("M-4", MS, {"MC-ADT-3"}, "falta la descripción", None,',
     '("M-4", MS, {"MC-ADT-3"}, ("falta la descripción", "contiene PL.9"), None,'),
    ('        if cv != conv or mc not in mcs or (texto and texto not in q):{nl}            continue{nl}',
     '        if cv != conv or mc not in mcs:{nl}            continue{nl}'
     '        if texto and not any(t in q for t in ((texto,) if isinstance(texto, str) else texto)):   # etapa 38: una tupla, basta uno{nl}'
     '            continue{nl}'),
]
MARCA = """## Marca de la etapa 38 (8-nov-2026)

El juez de CV4 escribe el hallazgo de PL.9 de Microsoft con un segundo texto («la descripción … contiene PL.9 … sin ser PL.9»), y
la regla de M-4 de `cv/cv3_clases.py` solo pedía el primero («falta la descripción»).
- **Con el juez publicado desde CV4,** el hallazgo de PL.9 de 8 de los 16 casos de M-4 quedaba sin clase.
- **Desde esta etapa la regla reconoce los dos** (bloque 9 del sello de la etapa 33), y M-4 vuelve a sus 16 casos.
- **M-36 y L-24 no tienen casos con el juez de CV4:** eran los falsos positivos de CX.4, ya apartados.

La frase no cambia (`RESULTADO-CLASES.md`). `cv/CLASES-CV3.json` no se toca: se reproduce con su receta, el juicio del estudio.
"""
PUB = sys.argv[1] if len(sys.argv) > 1 else None


def ruta(rel):
    return os.path.join(PUB, "verificador", rel) if PUB else os.path.join(FASE, rel)


p = ruta("cv/cv3_clases.py")
t = open(p, encoding="utf-8", newline="").read()
nl = "\r\n" if "\r\n" in t else "\n"
for viejo, nuevo in CAMBIOS:
    viejo, nuevo = viejo.replace("{nl}", nl), nuevo.replace("{nl}", nl)
    if nuevo in t:
        continue
    assert t.count(viejo) == 1, "%s: no está (o no es único): %r" % (p, viejo[:70])
    t = t.replace(viejo, nuevo)
open(p, "w", encoding="utf-8", newline="").write(t)
print("%s: M-4 con los dos textos; regla() admite una tupla" % p)

p = ruta("cv/RESULTADO-CV3.md")
t = open(p, encoding="utf-8", newline="").read()
nl = "\r\n" if "\r\n" in t else "\n"
marca = MARCA.replace("\n", nl)
LINEA_VIEJA = "- **Con el juez publicado desde CV4,** 8 de los 16 casos de M-4 quedaban sin clase."   # la primera redacción (revisión)
LINEA_NUEVA = "- **Con el juez publicado desde CV4,** el hallazgo de PL.9 de 8 de los 16 casos de M-4 quedaba sin clase."
if LINEA_VIEJA in t:
    assert t.count(LINEA_VIEJA) == 1, "%s: la línea vieja de la marca no es única" % p
    t = t.replace(LINEA_VIEJA, LINEA_NUEVA)
    open(p, "w", encoding="utf-8", newline="").write(t)
if "## Marca de la etapa 38" not in t:
    nota = nl + nl + "> *Copia pública"
    if nota in t:
        assert t.count(nota) == 1, "%s: la nota de copia pública no es única" % p
        t = t.replace(nota, nl + nl + marca.rstrip(nl) + nota)
    else:
        t = t.rstrip(nl) + nl + nl + marca
    open(p, "w", encoding="utf-8", newline="").write(t)
print("%s: marca de la etapa 38" % p)

if not PUB:
    S = os.path.join(FASE, "ga", "SELLO-GA.txt")
    t = open(S, encoding="utf-8", newline="").read()
    h = hashlib.sha256(open(os.path.join(FASE, "cv", "cv3_clases.py"), "rb").read()).hexdigest()
    bueno = "bloque 9" in t and t.endswith("%s  cv/cv3_clases.py\n" % h)
    if not bueno:
        if "bloque 9" in t:
            t = t[:t.index("SELLO DE LA ETAPA 33, bloque 9")]
        assert "bloque 8" in t, "falta el bloque 8"
        ahora = datetime.datetime.now().strftime("%d-nov-%Y, %H:%M").lstrip("0")
        t = t.rstrip("\n") + "\n" + ("\nSELLO DE LA ETAPA 33, bloque 9 (%s): desde la etapa 38, M-4 reconoce también el texto del juez de CV4 "
                                     "(cl/decision-jev-cl.md, Q-CL-1 a)\n# M-4: texto «falta la descripción» -> («falta la descripción», "
                                     "«contiene PL.9»), y regla() admite una tupla de textos de los que basta uno; la clase, su texto y su "
                                     "referencia no cambian\n%s  cv/cv3_clases.py\n" % (ahora, h))
        open(S, "w", encoding="utf-8", newline="").write(t)
    print("ga/SELLO-GA.txt: bloque 9 (%s)%s" % (h[:12], ", ya estaba" if bueno else ""))
