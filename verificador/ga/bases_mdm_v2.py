#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Etapa 33 (ga/diseno-ga-fable.md §4; Jev P7): las 40 bases MDM^T02 de la versión 2 del corpus. Se derivan de bases_mdm.py (que no
cambia): solo B36 cambia, en TXA-12, para caber en su LEN 30 (CH09.txt:834) conservando EI.2 a EI.4; así el TXA-13 que deriva
mev/bases_mdmev.py en T06 y T10 (EI.1 + «-PADRE») tiene 29 caracteres. Escrito por ga/hacer_resto_v2.py."""
import copy
import hashlib
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import bases_mdm as BM  # noqa: E402

TXA12_V1 = "DOC0036^CSSYN^1.2.840.113619.2.1^ISO"
TXA12_V2 = "DOC0036^CSSYN^2.999^ISO"


def _v2(b):
    if b["id"] != "B36":
        return b
    b = copy.deepcopy(b)
    n = 0
    for i, s in enumerate(b["segmentos"]):
        if s.startswith("TXA|"):
            f = s.split("|")
            assert f[12] == TXA12_V1, f[12]
            f[12] = TXA12_V2
            b["segmentos"][i] = "|".join(f)
            n += 1
    assert n == 1
    return b


BASES = [_v2(b) for b in BM.BASES]
cable = BM.cable


def huella(bases=None):
    h = hashlib.sha256()
    for b in bases or BASES:
        h.update(cable(b).encode("utf-8"))
    return h.hexdigest()
