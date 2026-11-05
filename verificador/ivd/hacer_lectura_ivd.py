#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Etapa 32 (Q-VD-2): la lectura de la 31 (ivm/lectura_ivm.py) para las muestras de la 2.5.1, con el texto de v2.5.1, escrita
aparte en ivd/lectura_ivd251.py para que la de la 31 no cambie:
- las tablas de atributos y el índice del Apéndice A, del texto de v2.5.1 (por la carpeta de enlaces); el índice de v2.5.1 no lleva
  sangría, y el patrón la admite;
- el tipo de dato de una fila admite «varies» (ivd/texto_ivd.py lo explica: OBX-5);
- los valores de tablas, de ../privado/ivd/TABLAS-VALORES-IVD251.json;
- las citas fijas de la lectura (el nulo, extender las tablas, la 0399, los equivalentes de la 0191 y la 0125, OBX-2), con su
  línea en el texto de v2.5.1, la misma frase que en v2.5;
- la salida se llama LECTURAS-IVD251.json y los veredictos, VEREDICTOS-IVD251.jsonl, con la versión;
- después de correr, tras la revisión a ciegas: la clase X se anota aparte, como en la lectura sin texto. Un segmento con más
  campos de los que define su versión va aparte por Q-VD-3b (la del ANTES, que Jev dejó en el titular, Q-VD-3d), y las otras
  formas que el conductor no reconoce, con su forma. La lectura de la 31 descartaba la clase X sin anotarla. Ningún veredicto
  cambia.
Afirma cada sustitución.  python3 ivd/hacer_lectura_ivd.py"""
import os

AQUI = os.path.dirname(os.path.abspath(__file__))
ORIGEN = os.path.join(os.path.dirname(AQUI), "ivm", "lectura_ivm.py")
V251 = "v2.5.1, "
CAMBIOS = [
    ('"""Etapa 31 (ANTES-ETAPA-IVMUESTRAS.md): la lectura de la etapa 30',
     '"""Etapa 32, la 2.5.1 (ANTES-ETAPA-IVDECLARADA.md, Q-VD-2): la lectura de la 31 con el texto de v2.5.1, hecha con\n'
     'ivd/hacer_lectura_ivd.py. Lo que sigue es la cabecera de la 31.\n'
     'Etapa 31 (ANTES-ETAPA-IVMUESTRAS.md): la lectura de la etapa 30'),
    ('FILAS, TXT, SAL = sys.argv[1:4]\n',
     'FILAS, TXT, SAL = sys.argv[1:4]\n'
     'assert SAL.endswith("LECTURAS-IVD251.json"), "la salida tiene que llamarse LECTURAS-IVD251.json"\n'),
    ('TV = json.load(open(os.path.join(PRIV, "iv", "TABLAS-VALORES-IV.json"), encoding="utf-8"))   # los mismos de la 30',
     'TV = json.load(open(os.path.join(PRIV, "ivd", "TABLAS-VALORES-IVD251.json"), encoding="utf-8"))   # etapa 32: los de v2.5.1'),
    (r'FILA = re.compile(r"^\s+(\d+)\s+(\d+)\s+([A-Z][A-Z0-9]{1,2})\s+',
     r'FILA = re.compile(r"^\s+(\d+)\s+(\d+)\s+([A-Z][A-Z0-9]{1,2}|varies|varie)\s+'),
    (r'm = re.match(r"^\s+(HL7|User)\s+(\d{4})\s+\S", l)', r'm = re.match(r"^\s*(HL7|User)\s+(\d{4})\s+\S", l)'),
    ('F = [json.loads(l) for l in open(FILAS, encoding="utf-8")]\n',
     'F = [json.loads(l) for l in open(FILAS, encoding="utf-8")]\n'
     'assert F and all(f.get("version") == "2.5.1" for f in F), "la lectura de la 2.5.1 recibe filas de otra versión"\n'),
    ('"atributo_v25": a}', '"atributo_v251": a}'),
    ('"%s-%d es %s en la tabla de atributos de v2.5"', '"%s-%d es %s en la tabla de atributos de v2.5.1"'),
    ('"no encuentro %s-%d en las tablas de atributos de v2.5"', '"no encuentro %s-%d en las tablas de atributos de v2.5.1"'),
    ('"LEN %d en v2.5; los valores miden %s"', '"LEN %d en v2.5.1; los valores miden %s"'),
    ('"sin LEN en v2.5"', '"sin LEN en v2.5.1"'),
    ("que no es un valor de tabla (CH02.txt:392)'", "que no es un valor de tabla (%sCH02.txt:374)'" % V251),
    ('"permite extender las tablas de HL7 (CH02.txt:564; Q-IV-D-11)"', '"permite extender las tablas de HL7 (%sCH02.txt:542; Q-IV-D-11)"' % V251),
    ('«HL7 V2.2 only» (AppendixA.txt:3433)', '«HL7 V2.2 only» (%sAppendixA.txt:3473)' % V251),
    ('con su descripción (AppendixA.txt:3427)', 'con su descripción (%sAppendixA.txt:3467)' % V251),
    ('PN tiene otra descripción (AppendixA.txt:2852, 2873)', 'PN tiene otra descripción (%sAppendixA.txt:2881, 2894)' % V251),
    ('"ISO 3166, forma de tres letras (CH02.txt:4580-4585)"', '"ISO 3166, forma de tres letras (%sCH02.txt:4451-4456)"' % V251),
    ('el texto permite extender las tablas de HL7 (CH02.txt:564)"', 'el texto permite extender las tablas de HL7 (%sCH02.txt:542)"' % V251),
    ('la 0125 impresa no lo trae, y CH07.txt:2590 dice', 'la 0125 impresa no lo trae, y %sCH07.txt:2593, dice' % V251),
    ('no cabe en el LEN 2 (CH07.txt:2532), y el texto lo admite (CH07.txt:2590)',
     'no cabe en el LEN 2 (%sCH07.txt:2529), y el texto lo admite (CH07.txt:2593)' % V251),
    ('"""Q-MV-2: el motivo por el que un error no se lee con el texto de v2.5, o None."""',
     '"""Q-MV-2 (en la 32, con el texto de v2.5.1): el motivo por el que un error no se lee con el texto, o None."""'),
    ('"segmento sin tabla de atributos en v2.5"', '"segmento sin tabla de atributos en v2.5.1"'),
    ('"campo que la tabla de atributos de v2.5 no trae"', '"campo que la tabla de atributos de v2.5.1 no trae"'),
    ('"tabla que el índice del Apéndice A de v2.5 no trae"', '"tabla que el índice del Apéndice A de v2.5.1 no trae"'),
    ('salvo que su estructura no exista en el esquema 2.5', 'salvo que su estructura no exista en el esquema de su versión'),
    ('"MSH-9.3 sin estructura en el esquema 2.5; se valida', '"MSH-9.3 sin estructura en el esquema 2.5.1; se valida'),
    ('veredictos.append({"id": f["id"], "corpus": f["corpus"], ', 'veredictos.append({"id": f["id"], "corpus": f["corpus"], "version": f["version"], '),
    ('SAL.replace("LECTURAS-IVM.json", "VEREDICTOS-IVM.jsonl")', 'SAL.replace("LECTURAS-IVD251.json", "VEREDICTOS-IVD251.jsonl")'),
    # después de correr, tras la revisión a ciegas: la clase X, anotada aparte (Q-VD-3b, ivd/decision-jev-qvd3d.md)
    ('    if sin_estructura:',
     '    for p in v["errores"]:                           # etapa 32, después de correr (tras la revisión a ciegas)\n'
     '        if p["clase"] != "X":\n'
     '            continue\n'
     '        mas = re.search(r"segment (\\d+):(\\w+)\\.\\s+Segment has more fields", p.get("crudo") or "")\n'
     '        if mas and p.get("pasada") == "dn":         # Q-VD-3b, la del ANTES (Q-VD-3d): más campos, aparte\n'
     '            aparte.append({"lugar": "C|%s||" % mas.group(2), "valor": None, "idx": int(mas.group(1)), "pasada": "dn",\n'
     '                           "por": "segmento con más campos de los que define su versión (Q-VD-3b)"})\n'
     '        else:                                       # otra forma que el conductor no reconoce: aparte, como sin texto\n'
     '            aparte.append({"lugar": "X|%s||" % (p.get("seg") or ""), "pasada": p.get("pasada"), "por": "forma de error que "\n'
     '                           "el conductor no reconoce", "crudo": (p.get("crudo") or "")[:200]})\n'
     '    if sin_estructura:'),
]

t = open(ORIGEN, encoding="utf-8").read()
for viejo, nuevo in CAMBIOS:
    assert t.count(viejo) == 1, "no está (o no es único): %r (%d)" % (viejo[:80], t.count(viejo))
    t = t.replace(viejo, nuevo)
open(os.path.join(AQUI, "lectura_ivd251.py"), "w", encoding="utf-8").write(t)
print("ivd/lectura_ivd251.py: escrito desde ivm/lectura_ivm.py con %d cambios" % len(CAMBIOS))
