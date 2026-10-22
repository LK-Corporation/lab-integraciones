#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""S-VE-4 (Q-MI-V-9, Q-VE-A-4): el contrato público del canónico ADT, GENERADO desde mapeador_adt.CONTRATO_CANONICO, la misma
fuente que lee el juez y que sirve consultar_tabla «canonico_adt». El .md no se edita a mano.
  cd fase12 && python3 contratos/generar_contrato.py              escribe contratos/contrato_canonico_adt.md
  cd fase12 && python3 contratos/generar_contrato.py --comprobar  sale 1 si el .md no es igual a lo que se generaría"""
import os
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
FASE = os.path.dirname(AQUI)
sys.path.insert(0, FASE)
import mapeador_adt as MA  # noqa: E402

SALIDA = os.path.join(AQUI, "contrato_canonico_adt.md")
BLOQUES = (("cabecera", "## cabecera (objeto)"), ("auxiliar", "## Auxiliares de la cabecera (no se comparan)"),
           ("nombres", "## nombres (lista; el orden es dato)"), ("direcciones", "## direcciones (lista; el orden es dato)"),
           ("telecoms", "## telecoms (lista; el orden es dato)"), ("participantes", "## participantes (lista; el orden es dato)"))


def texto():
    L = ["# Contrato del canónico ADT (`sesiones[].canonico_adt`, punto de entrada `adt_fhir`)", "",
         "*Generado por `contratos/generar_contrato.py` desde `mapeador_adt.CONTRATO_CANONICO`, la misma fuente que lee el",
         "verificador. No se edita a mano.*", "",
         "Es lo que el circuito registra de cada mensaje antes de escribir en FHIR y que el verificador compara **literalmente** con",
         "lo que esperaba. Reglas comunes:", "",
         "- **Vacío es `\"\"`**, nunca `null`, en lo esperado. Un `None` en lo esperado quiere decir «imposible»: ese campo no se",
         "  juzga (S10).",
         "- **Sin visita** (PV1-2 = N, `TieneVisita` = 0), **todos** los campos de visita van vacíos, también `ClaseCode`.",
         "- **Los códigos van ya mapeados a FHIR**, por los ConceptMap oficiales v2-to-FHIR y las tablas indicadas, no crudos.",
         "- **El mensaje se lee truncado** al LEN de v2.5 del punto de entrada (S3); si algo se truncó, `Truncado` = 1.", ""]
    for b, titulo in BLOQUES:
        L += [titulo, "", "| Campo | Origen HL7 | Tipo | Valor | Cita |", "|---|---|---|---|---|"]
        for b_, c, o, t, v, ci in MA.CONTRATO_CANONICO:
            if b_ == b:
                L.append("| `%s` | %s | %s | %s | %s |" % (c, o, t, v.replace("|", "\\|"), ci))
        L.append("")
    return "\n".join(L)


if __name__ == "__main__":
    t = texto()
    if sys.argv[1:] == ["--comprobar"]:
        igual = os.path.exists(SALIDA) and open(SALIDA, encoding="utf-8").read() == t
        print("contrato_canonico_adt.md: %s" % ("IGUAL a la generación" if igual else "DISTINTO de la generación"))
        sys.exit(0 if igual else 1)
    open(SALIDA, "w", encoding="utf-8").write(t)
    print("escrito %s (%d campos)" % (os.path.relpath(SALIDA, FASE), len(MA.CONTRATO_CANONICO)))
