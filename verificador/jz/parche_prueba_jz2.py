#!/usr/bin/env python3
"""Etapa 37, segundo parche de las pruebas: los controles que fijan lo que exporta el juez cambian a propósito.

  python3 jz/parche_prueba_jz2.py [<carpeta del juez>]

- P-VX-20 y P-MD-24: el perfil de ADT tiene una fila más (la Observation de un segmento sin destino, L-CV-17): 21 -> 22.
- P-MD-25 (d): la huella de INFO cambia (S-CV-5, L-CV-17 y L-CV-18); la de C no.
Su rojo se saca corriéndolas contra el juez de antes (jz/ROJO-JZ-2.txt). Conserva los finales de línea."""
import os
import sys

AQUI = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

VX = [('''    mira("control: perfil_guia_adt y _oru sin cambios", (len(CV.PERFIL_GUIA_ADT), len(CV.PERFIL_GUIA_ORU)), (21, 16))''',
       '''    mira("control: perfil_guia_adt y _oru sin cambios", (len(CV.PERFIL_GUIA_ADT), len(CV.PERFIL_GUIA_ORU)), (22, 16))  # etapa 37: L-CV-17''')]

MD = [('''ANTES = {"mdm": "75ab855348d66163", "C": "5dabbc37ec4a7909", "INFO": "d8b3a2eb651b1ac4", "TIPOS_PROY": "415c77f208321377",''',
       '''# Etapa 37 (7-nov): INFO cambia a propósito (S-CV-5, L-CV-17 y L-CV-18; antes, d8b3a2eb651b1ac4); C y lo demás, igual.
ANTES = {"mdm": "75ab855348d66163", "C": "5dabbc37ec4a7909", "INFO": "a06d3df87c0bd01c", "TIPOS_PROY": "415c77f208321377",''')]


def aplica(ruta, cambios, adicional=None):
    t = open(ruta, encoding="utf-8", newline="").read()
    for antes, despues in cambios:
        if t.count(antes) != 1:
            raise SystemExit("%s: «%s…» aparece %d veces; no se escribe nada" % (os.path.basename(ruta), antes[:50], t.count(antes)))
        t = t.replace(antes, despues)
    return t


def main(carpeta=AQUI):
    f_vx = os.path.join(carpeta, "prueba_conversion_vxu.py")
    f_md = os.path.join(carpeta, "prueba_conversion_mdm.py")
    md = open(f_md, encoding="utf-8", newline="").read()
    if "a06d3df87c0bd01c" in md:
        print("ya aplicado")
        return 0
    vx = aplica(f_vx, VX)
    md = aplica(f_md, MD)
    viejo = "(21, 16, 27)"
    if md.count(viejo) != 1:
        raise SystemExit("prueba_conversion_mdm.py: %s aparece %d veces" % (viejo, md.count(viejo)))
    md = md.replace(viejo, "(22, 16, 27)")
    open(f_vx, "w", encoding="utf-8", newline="").write(vx)
    open(f_md, "w", encoding="utf-8", newline="").write(md)
    print("controles de la etapa 37 escritos en %s y %s" % (f_vx, f_md))
    return 0


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:]))
