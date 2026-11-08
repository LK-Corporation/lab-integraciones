#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Etapa 39 (sc/diseno-sc-fable.md §1, §2 y §4, con sc/decision-jev-sc.md): en cv/cv3_clases.py,
- Q-SC-1 a: «casos» admite un diccionario por mecanismo, y M-28 pasa a {"MC-ORU-7": ("ms-ADT",),
  "fuera:Observation|recurso_sin_mapa": None}: la Observation sin mapa es M-28 en cualquier corpus de Microsoft, y MC-ORU-7 sigue
  limitado a los casos ms-ADT;
- Q-SC-2 b: main() cuenta lo sin clase en su salida («n_sin_clase», fuera de la frase) y, si queda algo, avisa al final por la
  salida de error; no falla. La cabecera deja de decir que «comprueba» que nada quede sin clase.
Y la marca de la etapa en cv/RESULTADO-CV3.md. Conserva los finales de línea (cv3_clases.py va en CRLF). Los JSON de clases pasados no
se tocan. Afirma cada texto. Idempotente.
- Sin argumentos, en el laboratorio: además, el bloque 10 del sello de la etapa 33, con la huella nueva de cv/cv3_clases.py.
- Con el clon público: en sus copias (verificador/…), en su sitio.
  cd fase12 && python3 sc/parche_sc.py [<clon público>]"""
import datetime
import hashlib
import os
import sys

FASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CAMBIOS = [
    ("del juez final, y comprueba que nada que cuente quede sin clase.",
     "del juez final, y lista lo que queda sin clase: no falla por ello, pero lo cuenta en su salida y avisa al final (etapa 39)."),
    ("# (id, conversor, mecanismos, texto que debe estar en el «que» (o tupla de textos, de los que basta uno) o None, casos o prefijos de caso o None,",
     "# (id, conversor, mecanismos, texto que debe estar en el «que» (o tupla de textos, de los que basta uno) o None, casos o prefijos de caso o None"
     " (o, por mecanismo, {mecanismo: eso}),"),
    ('("M-28", MS, {"MC-ORU-7", "fuera:Observation|recurso_sin_mapa"}, None, ("ms-ADT",),',
     '("M-28", MS, {"MC-ORU-7", "fuera:Observation|recurso_sin_mapa"}, None, {"MC-ORU-7": ("ms-ADT",), "fuera:Observation|recurso_sin_mapa": None},'),
    ("        if casos is not None and not (caso in casos if isinstance(casos, set) else caso.startswith(casos)):{nl}",
     "        if isinstance(casos, dict):   # etapa 39: el límite de casos, por mecanismo (M-28: MC-ORU-7 solo en las muestras){nl}"
     "            casos = casos[mc]{nl}"
     "        if casos is not None and not (caso in casos if isinstance(casos, set) else caso.startswith(casos)):{nl}"),
    ('           "sin_clase": {"%s | %s | %s" % k: n for k, n in sin.items()},{nl}',
     '           "sin_clase": {"%s | %s | %s" % k: n for k, n in sin.items()}, "n_sin_clase": sum(sin.values()),{nl}'),
    ('    for k, n in sorted(res["convenciones"].items()):{nl}        print("   %3d %s" % (n, k[:150])){nl}',
     '    for k, n in sorted(res["convenciones"].items()):{nl}        print("   %3d %s" % (n, k[:150])){nl}'
     '    if sin:   # etapa 39 (Q-SC-2 b): lo sin clase no para el aparato, pero no pasa sin verse; por stderr, que arrastre.py no redirige{nl}'
     '        print("AVISO cv3_clases: %d entradas sin clase (%d firmas) en %s: %s" % ({nl}'
     '            sum(sin.values()), len(sin), os.path.join(*os.path.normpath(salida).split(os.sep)[-2:]),{nl}'
     '            json.dumps(res["sin_clase"], ensure_ascii=False)), file=sys.stderr){nl}'),
]
# tras la revisión a ciegas: el aviso cuenta entradas («que») y firmas, no hallazgos y mecanismos; de la primera versión a esta
MEJORAS = [
    ('    if sin:   # etapa 39 (Q-SC-2 b): lo sin clase no para el aparato, pero no pasa sin verse; por stderr, que nadie redirige{nl}'
     '        print("AVISO cv3_clases: %d hallazgos sin clase (%d mecanismos) en %s: %s" % ({nl}',
     '    if sin:   # etapa 39 (Q-SC-2 b): lo sin clase no para el aparato, pero no pasa sin verse; por stderr, que arrastre.py no redirige{nl}'
     '        print("AVISO cv3_clases: %d entradas sin clase (%d firmas) en %s: %s" % ({nl}'),
]
MARCA_LINEA_VIEJA = ("  del sello de la etapa 33). El mecanismo con que la veía el juez de antes de la etapa 37 (MC-ORU-7) sigue limitado a las "
                     "muestras.")
MARCA_LINEA_NUEVA = ("  del sello de la etapa 33). El mecanismo con que la veía el juez de antes de la etapa 37 (MC-ORU-7) sigue limitado a los{nl}"
                     "  casos `ms-ADT`.")
MARCA = """## Marca de la etapa 39 (8-nov-2026)

- **La Observation «recurso sin mapa» de ACC o PDA es M-28 en cualquier corpus de Microsoft,** no solo en las muestras (bloque 10
  del sello de la etapa 33). El mecanismo con que la veía el juez de antes de la etapa 37 (MC-ORU-7) sigue limitado a los
  casos `ms-ADT`.
- **En el estudio no cambia nada:** M-28 sigue con sus 7 muestras.
- **`cv/cv3_clases.py` ya no deja pasar sin verse lo que queda sin clase:** lo cuenta en su salida (`n_sin_clase`) y avisa al final,
  sin fallar (`RESULTADO-SINCLASE.md`).
"""
PUB = sys.argv[1] if len(sys.argv) > 1 else None


def ruta(rel):
    return os.path.join(PUB, "verificador", rel) if PUB else os.path.join(FASE, rel)


p = ruta("cv/cv3_clases.py")
t = open(p, encoding="utf-8", newline="").read()
nl = "\r\n" if "\r\n" in t else "\n"
for viejo, nuevo in MEJORAS:
    viejo, nuevo = viejo.replace("{nl}", nl), nuevo.replace("{nl}", nl)
    if viejo in t:
        assert t.count(viejo) == 1, "%s: la primera versión del aviso no es única" % p
        t = t.replace(viejo, nuevo)
for viejo, nuevo in CAMBIOS:
    viejo, nuevo = viejo.replace("{nl}", nl), nuevo.replace("{nl}", nl)
    if nuevo in t:
        continue
    assert t.count(viejo) == 1, "%s: no está (o no es único): %r" % (p, viejo[:70])
    t = t.replace(viejo, nuevo)
open(p, "w", encoding="utf-8", newline="").write(t)
print("%s: M-28 con su límite por mecanismo; n_sin_clase y el aviso" % p)

p = ruta("cv/RESULTADO-CV3.md")
t = open(p, encoding="utf-8", newline="").read()
nl = "\r\n" if "\r\n" in t else "\n"
marca = MARCA.replace("\n", nl)
if MARCA_LINEA_VIEJA in t:
    assert t.count(MARCA_LINEA_VIEJA) == 1, "%s: la línea vieja de la marca no es única" % p
    t = t.replace(MARCA_LINEA_VIEJA, MARCA_LINEA_NUEVA.replace("{nl}", nl))
    open(p, "w", encoding="utf-8", newline="").write(t)
if "## Marca de la etapa 39" not in t:
    nota = nl + nl + "> *Copia pública"
    if nota in t:
        assert t.count(nota) == 1, "%s: la nota de copia pública no es única" % p
        t = t.replace(nota, nl + nl + marca.rstrip(nl) + nota)
    else:
        t = t.rstrip(nl) + nl + nl + marca
    open(p, "w", encoding="utf-8", newline="").write(t)
print("%s: marca de la etapa 39" % p)

if not PUB:
    S = os.path.join(FASE, "ga", "SELLO-GA.txt")
    t = open(S, encoding="utf-8", newline="").read()
    h = hashlib.sha256(open(os.path.join(FASE, "cv", "cv3_clases.py"), "rb").read()).hexdigest()
    bueno = "bloque 10" in t and t.endswith("%s  cv/cv3_clases.py\n" % h)
    if not bueno:
        if "bloque 10" in t:
            t = t[:t.index("SELLO DE LA ETAPA 33, bloque 10")]
        assert "bloque 9" in t, "falta el bloque 9"
        ahora = datetime.datetime.now().strftime("%d-nov-%Y, %H:%M").lstrip("0")
        t = t.rstrip("\n") + "\n" + (
            "\nSELLO DE LA ETAPA 33, bloque 10 (%s): desde la etapa 39, M-28 reconoce el corpus del laboratorio para la Observation sin "
            "mapa, y el aparato avisa de lo sin clase (sc/decision-jev-sc.md, Q-SC-1 a y Q-SC-2 b)\n# M-28: casos (\"ms-ADT\",) -> "
            "{\"MC-ORU-7\": (\"ms-ADT\",), \"fuera:Observation|recurso_sin_mapa\": None}, y regla() admite un diccionario de casos por "
            "mecanismo; main() escribe n_sin_clase y avisa por stderr al final; la clase, su texto y su referencia no cambian, ni el código "
            "de salida\n%s  cv/cv3_clases.py\n" % (ahora, h))
        open(S, "w", encoding="utf-8", newline="").write(t)
    print("ga/SELLO-GA.txt: bloque 10 (%s)%s" % (h[:12], ", ya estaba" if bueno else ""))
