# Generado por ga/hacer_gen_adt_v2.py desde bases_adt/gen_adt.py (etapa 33, versión 2 del corpus). No editar a mano.
import random
import json


class Delims:
    def __init__(self, fs, comp, rep, esc, sub):
        self.fs = fs
        self.comp = comp
        self.rep = rep
        self.esc = esc
        self.sub = sub


DEFAULT = Delims('|', '^', '~', '\\', '&')
CUSTOM = Delims('#', '$', '%', '*', '!')

SURNAMES = [
    "GARCIA", "MARTINEZ", "LOPEZ", "RODRIGUEZ", "FERNANDEZ",
    "PEREZ", "GONZALEZ", "SANCHEZ", "MUNOZ", "JIMENEZ",
    "RUIZ", "DIAZ", "MORENO", "ALONSO", "RAMIREZ"
]
GIVENS_M = [
    "JUAN", "CARLOS", "MIGUEL", "PEDRO", "LUIS",
    "JORGE", "MARIO", "FRANCISCO", "DAVID", "RAUL"
]
GIVENS_F = [
    "MARIA", "ANA", "LUISA", "CARMEN", "ELENA",
    "SARA", "LAURA", "ROSA", "MARTA", "PAULA"
]
STREETS = [
    "AVDA DEL PARQUE", "CALLE MAYOR", "PLAZA DE LA CRUZ",
    "CAMINO REAL", "RONDA SUR"
]
CITIES = ["MADRID", "BARCELONA", "VALENCIA", "SEVILLA", "BILBAO"]
STATES = ["M", "B", "V", "S"]

EVENT_STRUCT = {
    "A01": "ADT_A01",
    "A02": "ADT_A02",
    "A03": "ADT_A03",
    "A04": "ADT_A01",
    "A08": "ADT_A01",
    "A11": "ADT_A09",
    "A13": "ADT_A01",
    "A31": "ADT_A05",
}

EVENT_PRE = {
    "A01": ["PD1", "ROL", "NK1"],
    "A02": ["PD1", "ROL"],
    "A03": ["PD1", "ROL", "NK1"],
    "A04": ["PD1", "ROL", "NK1"],
    "A08": ["PD1", "ROL", "NK1"],
    "A11": ["PD1"],
    "A13": ["PD1", "ROL", "NK1"],
    "A31": ["PD1", "ROL", "NK1"],
}

EVENT_POST = {
    "A01": ["PV2", "ROL", "DB1", "OBX", "AL1", "DG1", "DRG", "PROC", "GT1", "INS", "ACC", "UB1", "UB2", "PDA"],
    "A02": ["PV2", "ROL", "DB1", "OBX", "PDA"],
    "A03": ["PV2", "ROL", "DB1", "AL1", "DG1", "DRG", "PROC", "OBX", "GT1", "INS", "ACC", "PDA"],
    "A04": ["PV2", "ROL", "DB1", "OBX", "AL1", "DG1", "DRG", "PROC", "GT1", "INS", "ACC", "UB1", "UB2", "PDA"],
    "A08": ["PV2", "ROL", "DB1", "OBX", "AL1", "DG1", "DRG", "PROC", "GT1", "INS", "ACC", "UB1", "UB2", "PDA"],
    "A11": ["PV2", "DB1", "OBX", "DG1"],
    "A13": ["PV2", "ROL", "DB1", "OBX", "AL1", "DG1", "DRG", "PROC", "GT1", "INS", "ACC", "UB1", "UB2", "PDA"],
    "A31": ["PV2", "ROL", "DB1", "OBX", "AL1", "DG1", "DRG", "PROC", "GT1", "INS", "ACC", "UB1", "UB2"],
}


def format_ts(rng, precision='second', fraction=False, zone=False):
    year = f"{rng.randint(1980, 2024):04d}"
    month = f"{rng.randint(1, 12):02d}"
    day = f"{rng.randint(1, 28):02d}"
    hour = f"{rng.randint(0, 23):02d}"
    minute = f"{rng.randint(0, 59):02d}"
    second = f"{rng.randint(0, 59):02d}"

    base = year
    if precision in ('month', 'day', 'hour', 'minute', 'second'):
        base += month
        if precision in ('day', 'hour', 'minute', 'second'):
            base += day
            if precision in ('hour', 'minute', 'second'):
                base += hour
                if precision in ('minute', 'second'):
                    base += minute
                    if precision == 'second':
                        base += second

    if fraction:
        digits = rng.randint(1, 4)
        max_val = 10 ** digits - 1
        base += "." + str(rng.randint(0, max_val)).zfill(digits)

    if zone:
        base += rng.choice(['+0100', '-0500'])

    return base


def make_ts_set(rng):
    return {
        'event': format_ts(rng, 'second', fraction=True, zone=True),
        'event_planned_nozone': format_ts(rng, 'second', fraction=True, zone=False),
        'birth_y': format_ts(rng, 'year', fraction=False, zone=False),
        'death_ym': format_ts(rng, 'month', fraction=False, zone=False),
        'last_update_d': format_ts(rng, 'day', fraction=False, zone=False),
        'admit_h': format_ts(rng, 'hour', fraction=False, zone=False),
        'discharge_min': format_ts(rng, 'minute', fraction=False, zone=False),
    }


def xpn(comp, family_name, given_name, middle_name='', suffix='', prefix='', degree='', name_type='L'):
    return comp.join([family_name, given_name, middle_name, suffix, prefix, degree, name_type])


def xcn(comp, last_name, first_name, middle_name=''):
    return comp.join(['', last_name, first_name, middle_name, '', '', ''])


def cx(comp, value, type_code):
    return comp.join([value, '', '', 'GENADT', type_code])


def xad(comp, street, city, state, zip_code):
    return comp.join([street, '', city, state, zip_code, '', ''])


def xtn(comp, phone, use_code='PRN', equipment='PH'):
    return comp.join([phone, use_code, equipment])


def make_pl(comp, point, room, facility):
    return comp.join(['', '', point, room, facility, 'A', 'B', '1', ''])


def build_seg(seg_id, fields_dict, delims):
    if not fields_dict:
        return seg_id, {}

    max_idx = max(fields_dict.keys())
    fields = [''] * max_idx
    for idx, val in fields_dict.items():
        fields[idx - 1] = val

    while fields and fields[-1] == '':
        fields.pop()

    if fields:
        seg_str = seg_id + delims.fs + delims.fs.join(fields)
    else:
        seg_str = seg_id

    captured = {idx: val for idx, val in fields_dict.items()}
    return seg_str, captured


def build_msh(delims, event, struct, event_time, control_id):
    enc = delims.comp + delims.rep + delims.esc + delims.sub
    fields = {
        3: 'GENADT',
        4: 'LAB',
        5: 'DEST',
        6: 'HIS',
        7: event_time,
        8: '',
        9: f"ADT{delims.comp}{event}{delims.comp}{struct}",
        10: control_id,
        11: 'P',
        12: '2.5',
    }
    tokens = ['MSH', enc]
    for i in range(3, 13):
        tokens.append(fields.get(i, ''))
    return delims.fs.join(tokens)


def generate_pid_fields(event, family, seq, rng, delims, birth_ts, death_ts, last_update_ts):
    comp = delims.comp
    rep = delims.rep

    sex = rng.choice(['M', 'F'])
    given_pool = GIVENS_F if sex == 'F' else GIVENS_M
    surname = rng.choice(SURNAMES)
    given = rng.choice(given_pool)
    middle = rng.choice(GIVENS_F if sex == 'F' else GIVENS_M)

    if family == 'escapes':
        surname += "\\F\\"
        given += "\\S\\"
        middle += "\\T\\"

    name = xpn(comp, surname, given, middle)

    if family == 'repeticiones':
        name2 = xpn(comp, rng.choice(SURNAMES), rng.choice(given_pool), rng.choice(given_pool))
        name = rep.join([name, name2])

    if family == 'repeticiones':
        pid3 = rep.join([
            cx(comp, f"ID{seq}A", "MR"),
            cx(comp, f"ID{seq}B", "PI"),
            cx(comp, f"ID{seq}C", "PT"),
        ])
    else:
        pid3 = cx(comp, f"P{seq:05d}", "MR")

    fields = {3: pid3, 5: name, 7: birth_ts, 8: sex}

    street = rng.choice(STREETS)
    city = rng.choice(CITIES)
    state = rng.choice(STATES)
    zip_code = f"{rng.randint(28000, 28999)}"
    phone = xtn(comp, f"6{rng.randint(10000000, 99999999)}")

    if family in ('completo', 'delimitadores', 'opcionales'):
        fields[11] = xad(comp, street, city, state, zip_code)
        fields[13] = phone

    if family == 'repeticiones':
        address2 = xad(comp, rng.choice(STREETS), rng.choice(CITIES), state, zip_code)
        phone2 = xtn(comp, f"6{rng.randint(10000000, 99999999)}")
        fields[11] = rep.join([xad(comp, street, city, state, zip_code), address2])
        fields[13] = rep.join([phone, phone2])

    if family == 'escapes':
        street += "\\R\\"
        city += "\\E\\"
        fields[11] = xad(comp, street, city, state, zip_code)

    if family == 'completo':
        fields[2] = cx(comp, f"EXT{seq:04d}", "PI")
        fields[12] = rng.choice(['01', '02', '03'])
        fields[22] = 'H'
        if death_ts:
            fields[29] = death_ts
        fields[30] = 'N'
        if last_update_ts:
            fields[33] = last_update_ts
        fields[34] = 'HIS'

    if family == 'nulos':
        fields[6] = '""'
        fields[11] = '""'
        fields[12] = '""'
        fields[13] = '""'

    if family == 'fechas':
        fields[29] = death_ts
        fields[33] = last_update_ts

    return fields, sex


def generate_pv1_fields(event, family, seq, rng, delims, event_time, admit_ts, discharge_ts):
    comp = delims.comp

    if event == 'A04':
        patient_class = 'O'
    elif event == 'A31':
        patient_class = 'N'
    else:
        patient_class = 'I'

    loc_point = {
        'A01': 'ICU', 'A02': 'ICU', 'A03': 'MED', 'A04': 'ER',
        'A08': 'MED', 'A11': 'MED', 'A13': 'MED', 'A31': 'NONA'
    }
    location = make_pl(comp, loc_point.get(event, 'MED'), f"{seq:03d}", 'HOSPITAL')

    fields = {2: patient_class, 3: location}

    if family == 'completo':
        fields[4] = 'E'
        fields[7] = xcn(comp, 'DOCTOR', 'ATTENDING')
        fields[8] = xcn(comp, 'DOCTOR', 'REFERRING')
        fields[10] = 'MED'
        fields[11] = make_pl(comp, 'PRE', '000', 'HOSPITAL')
        fields[14] = 'A'
        fields[18] = 'P'
        fields[19] = cx(comp, f'VN{seq:04d}', 'VN')
        fields[44] = event_time

        if event == 'A02':
            fields[6] = make_pl(comp, 'OLD', '002', 'HOSPITAL')
        if event == 'A03':
            fields[36] = '01'
            fields[37] = 'HOME' + comp + discharge_ts
            fields[45] = discharge_ts if discharge_ts else event_time
        if event == 'A13':
            fields[45] = discharge_ts if discharge_ts else event_time
        if event == 'A31':
            fields[2] = 'N'

    elif family == 'nulos':
        fields[4] = '""'
        fields[7] = '""'
        fields[11] = '""'

    elif family == 'fechas':
        fields[44] = admit_ts
        fields[45] = discharge_ts

    return fields


def generate_base(event, family, rep_idx, rng, seq):
    delims = CUSTOM if family == 'delimitadores' else DEFAULT
    struct = EVENT_STRUCT[event]
    control_id = f"{event}-{family[:4]}-{seq:03d}"

    if family == 'fechas':
        ts_set = make_ts_set(rng)
        event_time = ts_set['event']
        birth_ts = ts_set['birth_y']
        death_ts = ts_set['death_ym']
        last_update_ts = ts_set['last_update_d']
        admit_ts = ts_set['admit_h']
        discharge_ts = ts_set['discharge_min']
        evn_ts_set = ts_set
    else:
        event_time = format_ts(rng, 'second', fraction=False, zone=True)
        birth_ts = format_ts(rng, 'day', fraction=False, zone=False)
        death_ts = format_ts(rng, 'second', fraction=False, zone=True) if family in ('completo',) else ''
        last_update_ts = format_ts(rng, 'day', fraction=False, zone=False) if family in ('completo',) else ''
        admit_ts = format_ts(rng, 'minute', fraction=False, zone=False) if family in ('completo',) else ''
        discharge_ts = format_ts(rng, 'second', fraction=False, zone=True) if family in ('completo',) else ''
        evn_ts_set = None

    segs = []
    colocado = []
    seen = set()

    def add_segment(seg_id, fields_dict, track_fields=()):
        seg, captured = build_seg(seg_id, fields_dict, delims)
        segs.append(seg)
        for f in track_fields:
            key = (seg_id, f)
            if f in fields_dict and key not in seen:
                colocado.append({"seg": seg_id, "campo": f, "valor": fields_dict[f]})
                seen.add(key)

    def include_optional(seg):
        if family in ('minimo', 'repeticiones', 'escapes', 'delimitadores', 'fechas', 'z'):
            return False
        if family in ('completo', 'nulos'):
            return True
        if family == 'opcionales':
            if rep_idx == 1:
                return seg in ('PD1', 'PV2', 'DB1', 'OBX', 'DG1')
            return True
        return False

    # ===== Funciones para segmentos opcionales =====
    def seg_pd1():
        if family == 'nulos':
            return {3: '""', 4: '""'}
        return {
            3: 'HOSPITAL',
            4: 'FACULTY',
        }

    def seg_rol():
        if family == 'nulos':
            return {2: 'UC', 3: 'CP', 4: xcn(delims.comp, 'DOCTOR', 'ASSISTANT'), 5: '""'}
        return {
            2: 'UC',
            3: 'CP',
            4: xcn(delims.comp, 'DOCTOR', 'ASSISTANT')
        }

    def seg_nk1():
        if family == 'nulos':
            return {1: '1', 2: '""'}
        return {
            1: '1',
            2: xpn(delims.comp, 'ESP_CARE', 'FAMILY'),
            3: 'SPOUSE',
            4: xad(delims.comp, 'STREET', 'CITY', 'STATE', 'ZIP'),
            5: xtn(delims.comp, '611111111')
        }

    def seg_db1():
        if family == 'nulos':
            return {1: '1', 2: '""'}
        return {
            1: '1',
            3: 'DISA',
        }

    def seg_obx():
        if family == 'nulos':
            return {1: '1', 2: 'ST', 3: 'Height', 5: '170', 6: '""', 11: 'F'}
        return {
            1: '1',
            2: 'ST',
            3: 'Height',
            5: '170',
            11: 'F',
        }

    def seg_al1():
        if family == 'nulos':
            return {1: '1', 2: '""', 3: 'PEN'}
        return {
            1: '1',
            3: 'PEN',
            4: 'MODERATE',
        }

    def seg_dg1():
        if family == 'nulos':
            return {1: '1', 2: 'I9', 3: '""', 6: 'A'}
        return {
            1: '1',
            2: 'I9',
            3: 'I10',
            4: 'HYPERTENSION',
            6: 'A',
        }

    def seg_drg():
        if family == 'nulos':
            return {1: '""'}
        return {
            1: '1',
        }

    def seg_gt1():
        if family == 'nulos':
            return {1: '1', 2: '""', 3: xpn(delims.comp, 'GUARANTOR', 'LAST')}
        return {
            1: '1',
            2: cx(delims.comp, 'G0001', 'AN'),
            3: xpn(delims.comp, 'GUARANTOR', 'LAST'),
        }

    def seg_acc():
        if family == 'nulos':
            return {1: '""'}
        return {
            1: event_time,
            2: 'ACC',
        }

    def seg_ub1():
        if family == 'nulos':
            return {1: '""'}
        return {
            1: '1',
            2: '0',
        }

    def seg_ub2():
        if family == 'nulos':
            return {1: '""'}
        return {
            1: '1',
            2: 'C',
        }

    def seg_pda():
        if family == 'nulos':
            return {1: '""'}
        return {
            1: '1',
            2: 'Y',
        }

    def seg_pv2():
        if family == 'nulos':
            return {3: '""'}
        return {
            3: 'PV2',
            4: 'PV2_DATA',
        }

    def add_opt_segment(seg):
        fields_map = {
            'PD1': seg_pd1(),
            'ROL': seg_rol(),
            'NK1': seg_nk1(),
            'PV2': seg_pv2(),
            'DB1': seg_db1(),
            'OBX': seg_obx(),
            'AL1': seg_al1(),
            'DG1': seg_dg1(),
            'DRG': seg_drg(),
            'GT1': seg_gt1(),
            'ACC': seg_acc(),
            'UB1': seg_ub1(),
            'UB2': seg_ub2(),
            'PDA': seg_pda(),
        }
        fields = fields_map.get(seg, {})
        add_segment(seg, fields, [])

    def add_proc_group():
        add_segment('PR1', {
            1: '1',
            2: 'L',
            3: 'P001',
            5: event_time,
        }, [])
        if include_optional('ROL'):
            add_segment('ROL', {
                2: 'UC',
                3: 'PP',
                4: xcn(delims.comp, 'DOC', 'PROC')
            }, [])

    def add_ins_group():
        add_segment('IN1', {
            1: '1',
            2: 'INS1',
            3: 'INSURANCE_CO',
        }, [])
        if include_optional('IN2'):
            add_segment('IN2', {1: '1', 2: 'INS2'}, [])
        if include_optional('IN3'):
            add_segment('IN3', {1: '1', 2: 'CERT1'}, [])
        if include_optional('ROL'):
            add_segment('ROL', {
                2: 'UC',
                3: 'IN',
                4: xcn(delims.comp, 'DOC', 'INS')
            }, [])

    # ===== Generación principal =====
    # MSH
    segs.append(build_msh(delims, event, struct, event_time, control_id))

    # EVN
    if family == 'fechas':
        add_segment('EVN', {
            1: event,
            2: evn_ts_set['event'],
            3: evn_ts_set['event_planned_nozone'],
            4: '00',
        }, [2, 3])
    else:
        add_segment('EVN', {
            1: event,
            2: event_time,
            4: '00',
        }, [])

    # PID
    pid_fields, _ = generate_pid_fields(
        event, family, seq, rng, delims, birth_ts, death_ts, last_update_ts
    )
    track_pid = [3, 5, 7, 8]
    for f in (11, 13, 6, 12, 29, 33):
        if f in pid_fields and f not in track_pid:
            track_pid.append(f)
    add_segment('PID', pid_fields, track_pid)

    # Segmentos opcionales antes de PV1
    for seg in EVENT_PRE.get(event, []):
        if include_optional(seg):
            add_opt_segment(seg)

    # PV1
    pv1_fields = generate_pv1_fields(
        event, family, seq, rng, delims, event_time, admit_ts, discharge_ts
    )
    track_pv1 = [2, 3]
    for f in (4, 6, 36, 37, 44, 45):
        if f in pv1_fields and f not in track_pv1:
            track_pv1.append(f)
    add_segment('PV1', pv1_fields, track_pv1)

    # Segmentos opcionales después de PV1
    for seg in EVENT_POST.get(event, []):
        if include_optional(seg):
            if seg == 'PROC':
                add_proc_group()
            elif seg == 'INS':
                add_ins_group()
            else:
                add_opt_segment(seg)

    if family == 'z':
        add_segment('ZAD', {2: 'synthetic'}, [2])

    return {
        "id": f"{event}-{seq:03d}",
        "evento": event,
        "familia": family,
        "mensaje": "\r".join(segs),
        "colocado": colocado,
    }


def bases(semilla: int) -> list:
    rng = random.Random(semilla)
    eventos = ["A01", "A02", "A03", "A04", "A08", "A11", "A13", "A31"]
    familias = ["minimo", "completo", "repeticiones", "escapes", "delimitadores", "nulos", "fechas", "opcionales", "z"]
    resultado = []

    for ev in eventos:
        seq = 1
        for fam in familias:
            for rep in range(3):
                base = generate_base(ev, fam, rep, rng, seq)
                resultado.append(base)
                seq += 1

    return resultado


if __name__ == "__main__":
    print(json.dumps(bases(1)))
