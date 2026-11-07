#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Etapa 33 (ga/diseno-ga-fable.md §1; Jev: ga/decision-jev-gad.md y gad2): escribe ga/gen_adt_v2.py desde bases_adt/gen_adt.py con
sustituciones literales, cada una afirmada una sola vez, y después ga/bases_adt_v2.json con bases(1). gen_adt.py no se toca.

Lo que cambia (§1.6 del diseño, con las decisiones):
- ROL-2 = UC en los cuatro ROL (P11, gad2);
- OBX-11 = F; DG1-2 = I9 y DG1-6 = A (P4: B, pero valorado); PR1-2 = L y PR1-5 = event_time;
- GT1-2 = G0001^^^GENADT^AN y GT1-3 = el nombre (GUARANTOR^LAST^^^^^L);
- ACC-1 = event_time; UB1-2 = 0; PV1-37 (A03 completo) = HOME^discharge_ts;
- nulos: ningún "" en un campo R; el nulo pasa a un campo O del mismo segmento (ROL-5, DB1-2, OBX-6, AL1-2) y los R reciben valor.
Lo que NO cambia (DV-GA-1): los valores válidos fuera de los sugeridos de una tabla de usuario (EVN-4, PL.6, PV1-14, NK1-3, AL1-4,
ROL-3 «IN»). P1 decidió anotarlos y no cambiarlos; se aplica igual a los de las familias que se arreglan.
Ningún valor nuevo saca números del azar: son constantes o event_time / discharge_ts, ya sorteados.
  cd fase12 && python3 ga/hacer_gen_adt_v2.py"""
import json
import os
import sys

FASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ORIGEN = os.path.join(FASE, "bases_adt", "gen_adt.py")
DESTINO = os.path.join(FASE, "ga", "gen_adt_v2.py")
SALIDA = os.path.join(FASE, "ga", "bases_adt_v2.json")

CAMBIOS = [
    ("rol", """    def seg_rol():
        if family == 'nulos':
            return {3: '""'}
        return {
            3: 'CP',
            4: xcn(delims.comp, 'DOCTOR', 'ASSISTANT')
        }""", """    def seg_rol():
        if family == 'nulos':
            return {2: 'UC', 3: 'CP', 4: xcn(delims.comp, 'DOCTOR', 'ASSISTANT'), 5: '""'}
        return {
            2: 'UC',
            3: 'CP',
            4: xcn(delims.comp, 'DOCTOR', 'ASSISTANT')
        }"""),
    ("nk1", """    def seg_nk1():
        if family == 'nulos':
            return {2: '""'}""", """    def seg_nk1():
        if family == 'nulos':
            return {1: '1', 2: '""'}"""),
    ("db1", """    def seg_db1():
        if family == 'nulos':
            return {1: '""'}""", """    def seg_db1():
        if family == 'nulos':
            return {1: '1', 2: '""'}"""),
    ("obx", """    def seg_obx():
        if family == 'nulos':
            return {2: '""'}
        return {
            1: '1',
            2: 'ST',
            3: 'Height',
            5: '170',
        }""", """    def seg_obx():
        if family == 'nulos':
            return {1: '1', 2: 'ST', 3: 'Height', 5: '170', 6: '""', 11: 'F'}
        return {
            1: '1',
            2: 'ST',
            3: 'Height',
            5: '170',
            11: 'F',
        }"""),
    ("al1", """    def seg_al1():
        if family == 'nulos':
            return {3: '""'}""", """    def seg_al1():
        if family == 'nulos':
            return {1: '1', 2: '""', 3: 'PEN'}"""),
    ("dg1", """    def seg_dg1():
        if family == 'nulos':
            return {3: '""'}
        return {
            1: '1',
            3: 'I10',
            4: 'HYPERTENSION',
        }""", """    def seg_dg1():
        if family == 'nulos':
            return {1: '1', 2: 'I9', 3: '""', 6: 'A'}
        return {
            1: '1',
            2: 'I9',
            3: 'I10',
            4: 'HYPERTENSION',
            6: 'A',
        }"""),
    ("gt1", """    def seg_gt1():
        if family == 'nulos':
            return {2: '""'}
        return {
            1: '1',
            2: xpn(delims.comp, 'GUARANTOR', 'LAST'),
            3: xad(delims.comp, 'STREET', 'CITY', 'STATE', 'ZIP'),
        }""", """    def seg_gt1():
        if family == 'nulos':
            return {1: '1', 2: '""', 3: xpn(delims.comp, 'GUARANTOR', 'LAST')}
        return {
            1: '1',
            2: cx(delims.comp, 'G0001', 'AN'),
            3: xpn(delims.comp, 'GUARANTOR', 'LAST'),
        }"""),
    ("acc", """        return {
            1: '1',
            2: 'ACC',
        }""", """        return {
            1: event_time,
            2: 'ACC',
        }"""),
    ("ub1", """        return {
            1: '1',
            2: 'B',
        }""", """        return {
            1: '1',
            2: '0',
        }"""),
    ("pr1", """        add_segment('PR1', {
            1: '1',
            2: 'PR1',
            3: 'P001',
        }, [])
        if include_optional('ROL'):
            add_segment('ROL', {
                3: 'PP',""", """        add_segment('PR1', {
            1: '1',
            2: 'L',
            3: 'P001',
            5: event_time,
        }, [])
        if include_optional('ROL'):
            add_segment('ROL', {
                2: 'UC',
                3: 'PP',"""),
    ("rol_in", """            add_segment('ROL', {
                3: 'IN',""", """            add_segment('ROL', {
                2: 'UC',
                3: 'IN',"""),
    ("pv1_37", """            fields[37] = make_pl(comp, 'HOME', '001', 'HOSPITAL')""",
     """            fields[37] = 'HOME' + comp + discharge_ts"""),
]

CABECERA = ('# Generado por ga/hacer_gen_adt_v2.py desde bases_adt/gen_adt.py (etapa 33, versión 2 del corpus). No editar a mano.\n')


def main():
    t = open(ORIGEN, encoding="utf-8").read()
    for nombre, viejo, nuevo in CAMBIOS:
        n = t.count(viejo)
        if n != 1:
            sys.exit("PARADA: la sustitución %s aparece %d veces" % (nombre, n))
        t = t.replace(viejo, nuevo)
    open(DESTINO, "w", encoding="utf-8").write(CABECERA + t)
    sys.path.insert(0, os.path.dirname(DESTINO))
    import gen_adt_v2
    b = gen_adt_v2.bases(1)
    json.dump(b, open(SALIDA, "w", encoding="utf-8"))
    print("escrito %s y %s: %d bases, %d sustituciones" % (os.path.relpath(DESTINO, FASE), os.path.relpath(SALIDA, FASE), len(b),
                                                           len(CAMBIOS)))


if __name__ == "__main__":
    main()
