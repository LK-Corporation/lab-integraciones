#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Extracto de adjudicacion.py del laboratorio: solo cable(), la forma del cable en la evidencia, que usa el verificador.
El módulo completo es de la fase 13 y no se publica (lleva material de la clave)."""
import re  # noqa: F401


def cable(b):
    """Los bytes del cable, legibles: CR como fin de línea, los de control como <0xNN> (VT y FS
    con su nombre), y lo que no es UTF-8 válido, byte a byte como <0xNN>."""
    out = []
    i = 0
    while i < len(b):
        c = b[i]
        if c == 0x0d:
            out.append("\n")
            i += 1
            continue
        if c == 0x0b:
            out.append("<VT>")
            i += 1
            continue
        if c == 0x1c:
            out.append("<FS>")
            i += 1
            continue
        if c < 0x20 or c == 0x7f:
            out.append("<0x%02X>" % c)
            i += 1
            continue
        if c < 0x80:
            out.append(chr(c))
            i += 1
            continue
        n = 2 if 0xC2 <= c <= 0xDF else 3 if 0xE0 <= c <= 0xEF else 4 if 0xF0 <= c <= 0xF4 else 0
        try:
            if not n:
                raise UnicodeDecodeError("utf-8", b, i, i + 1, "no es inicio de secuencia")
            out.append(b[i:i + n].decode("utf-8"))
            i += n
        except UnicodeDecodeError:
            out.append("<0x%02X>" % c)
            i += 1
    return "".join(out)
