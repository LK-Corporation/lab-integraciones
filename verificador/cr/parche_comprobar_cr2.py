#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Etapa 35, tras la segunda pasada de la revisión a ciegas (menor 3; DV-CR-3): en cv/ci/comprobar_publicado.py, un fichero que no
se lee (un ENSAYO.json sin permiso) o una salida que no se escribe (-o sobre un fichero) salen con 2 y no con una traza y 1. Se
aplica después de cr/parche_comprobar_cr.py. Afirma cada texto. Idempotente.  cd fase12 && python3 cr/parche_comprobar_cr2.py"""
import os

FASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(FASE, "cv", "ci", "comprobar_publicado.py")
CAMBIOS = [
    ("  mismo flujo, ningún flujo que comprobar, o los argumentos están mal.\n",
     "  mismo flujo, ningún flujo que comprobar, los argumentos están mal, o un fichero no se lee o no se escribe.\n"),
    ("        print(\"no se pudo comprobar: los argumentos están mal (%s)\" % ex)\n"
     "        return 2\n",
     "        print(\"no se pudo comprobar: los argumentos están mal (%s)\" % ex)\n"
     "        return 2\n"
     "    except OSError as ex:                                               # un fichero que no se lee o no se escribe\n"
     "        print(\"no se pudo comprobar: %s\" % ex)\n"
     "        return 2\n"),
]
t = open(P, encoding="utf-8").read()
if "    except OSError as ex:" not in t:
    for viejo, nuevo in CAMBIOS:
        assert t.count(viejo) == 1, "no está (o no es único): %r" % viejo[:80]
        t = t.replace(viejo, nuevo)
    open(P, "w", encoding="utf-8").write(t)
print("cv/ci/comprobar_publicado.py: un fichero que no se lee o no se escribe, con 2")
