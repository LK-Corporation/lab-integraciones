# -*- coding: utf-8 -*-
"""Escribe la página del estudio de conversores (docs/conversores/index.html) desde los ficheros publicados.

Etapa 19 del laboratorio (diseño a ciegas: verificador/cv/pg/diseno-pg-fable.md; decisiones de Jev:
verificador/cv/pg/decision-jev-qpg.md; lo que se hizo y lo que no hace: verificador/cv/pg/PG.md). La página no lleva ninguna cifra escrita a mano: cada cifra, cada texto del juez, cada cita y cada
mensaje mínimo va en un elemento con su fuente declarada (`data-fuente`), que este guion resuelve al escribir y que
tests/test_repo_hygiene.py vuelve a resolver con su propio código. La prosa de enlace vive aquí y no lleva cifras.

  python3 codigo/hacer_pagina_conversores.py                 # escribe docs/conversores/index.html
  python3 codigo/hacer_pagina_conversores.py --comprobar     # regenera en memoria y compara: IGUAL o DISTINTA
  python3 codigo/hacer_pagina_conversores.py --comprobar <f> # compara con otro fichero

Sale con 0 (escrita o IGUAL), 1 (DISTINTA) o 2 (una fuente no resuelve)."""
import difflib
import html
import importlib.util
import json
import re
import sys
import unicodedata
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SALIDA = REPO / "docs" / "conversores" / "index.html"
SITIO = "https://lk-corporation.github.io/lab-integraciones/conversores/"
GH = "https://github.com/LK-Corporation/lab-integraciones/blob/main/"
CV = "verificador/cv/"
CLASES = CV + "CLASES-CV3.json"
MINIMOS = CV + "RESULTADO-CV3-minimos.json"
INFORME = CV + "vc/ejemplos/INFORME-microsoft.json"


class FuenteRota(Exception):
    pass


# ---------------------------------------------------------------------------- resolver una fuente
_cache = {}


def leer(rel):
    if rel not in _cache:
        _cache[rel] = (REPO / rel).read_text(encoding="utf-8")
    return _cache[rel]


def norm(s):
    s = re.sub(r"\*\*|`", "", s or "").replace(" ", " ").replace(" ", " ").replace(" ", " ")
    for a, b in ((">=", "≥"), ("<=", "≤"), ("->", "→")):
        s = s.replace(a, b)
    return re.sub(r"\s+", " ", s).strip()


def de_json(rel, puntero):
    v = json.loads(leer(rel))
    for paso in puntero.split("."):
        m = re.match(r"^(\w+)\[(\w+)=([^\]]+)\]$", paso)
        if m:
            xs = [x for x in v[m.group(1)] if str(x.get(m.group(2))) == m.group(3)]
            if len(xs) != 1:
                raise FuenteRota("%s#%s: %d elementos en %s" % (rel, puntero, len(xs), paso))
            v = xs[0]
        elif isinstance(v, list):
            v = v[int(paso)]
        else:
            v = v[paso]
    return v


def de_md(rel, patron, grupo=1):
    ms = list(re.finditer(patron, leer(rel), re.M))
    if len(ms) != 1:
        raise FuenteRota("%s: el patrón %r casa %d veces" % (rel, patron, len(ms)))
    return ms[0].group(grupo)


def de_tabla(rel, linea, fila, columna):
    lineas = leer(rel).splitlines()
    try:
        i = next(k for k, l in enumerate(lineas) if linea in l)
    except StopIteration:
        raise FuenteRota("%s: no hay línea con %r" % (rel, linea))
    while not lineas[i].startswith("|"):
        i += 1
    celdas = lambda l: [norm(c.replace("\\|", "|")) for c in re.split(r"(?<!\\)\|", l.strip()[1:-1])]  # noqa: E731
    cab = celdas(lineas[i])
    k = i + 2
    while k < len(lineas) and lineas[k].startswith("|"):
        c = celdas(lineas[k])
        if c[0] == norm(fila):
            return c[cab.index(norm(columna))]
        k += 1
    raise FuenteRota("%s: la tabla tras %r no tiene la fila %r" % (rel, linea, fila))


def _cargar_minimos():
    spec = importlib.util.spec_from_file_location("cv3_minimos_pagina", REPO / CV / "cv3_minimos.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return {pid: {"caso": caso, "control": control} for pid, _, (caso, control), _ in mod.PARES}


PARES = _cargar_minimos()


def resolver(fuente, patron=None, grupo=1):
    tipo, _, resto = fuente.partition(":")
    rel = resto.split("#", 1)[0]
    try:
        if tipo == "json":
            v = de_json(rel, resto.split("#", 1)[1])
            v = ("sí" if v else "no") if isinstance(v, bool) else str(v)
        elif tipo == "md":
            return norm(de_md(rel, patron, grupo))
        elif tipo == "tabla":
            linea, fila, columna = resto.split("#", 1)[1].split("|")
            v = de_tabla(rel, linea, fila, columna)
        elif tipo == "hl7":
            par, cual = resto.split("#")
            return PARES[par][cual].replace("\r", "\n").strip("\n")
        else:
            raise FuenteRota("tipo desconocido %r" % tipo)
    except (KeyError, IndexError, ValueError) as e:
        raise FuenteRota("%s: %s" % (fuente, e))
    if patron:
        ms = list(re.finditer(patron, v, re.M))
        if len(ms) != 1:
            raise FuenteRota("%s: el patrón %r casa %d veces" % (fuente, patron, len(ms)))
        v = ms[0].group(grupo)
    return norm(v)


# ---------------------------------------------------------------------------- escribir con fuente
def esc(s):
    return html.escape(s, quote=False)


def en_linea(s):
    """Markdown en línea a HTML, tras escapar: **x** -> <strong>, `x` -> <code>."""
    s = esc(s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    return re.sub(r"`([^`]+)`", r"<code>\1</code>", s)


def _attrs(fuente, patron, grupo):
    a = ' data-fuente="%s"' % html.escape(fuente, quote=True)
    if patron:
        a += ' data-patron="%s"' % html.escape(patron, quote=True)
    if grupo != 1:
        a += ' data-grupo="%d"' % grupo
    return a


def cifra(fuente, patron=None, grupo=1, clase="cifra"):
    """Una cifra con su fuente, en <span class="cifra"> como las de la primera página (DV-PG-3: el diseño usaba <data>)."""
    v = resolver(fuente, patron, grupo)
    return '<span class="%s"%s>%s</span>' % (clase, _attrs(fuente, patron, grupo), esc(v))


def texto(fuente, patron=None, grupo=1, md=False, tag="span", clase=None):
    """El texto tal como lo dice la fuente; con md=True, el Markdown en línea del texto original (sin normalizar)."""
    resolver(fuente, patron, grupo)
    crudo = _crudo(fuente, patron, grupo)
    cuerpo = en_linea(re.sub(r"\s+", " ", crudo).strip()) if md else esc(norm(crudo))
    return "<%s%s%s>%s</%s>" % (tag, ' class="%s"' % clase if clase else "", _attrs(fuente, patron, grupo), cuerpo, tag)


def _crudo(fuente, patron, grupo):
    """Como resolver, pero sin quitar el Markdown en línea (para mostrarlo como HTML)."""
    tipo, _, resto = fuente.partition(":")
    rel = resto.split("#", 1)[0]
    if tipo == "md":
        return de_md(rel, patron, grupo)
    if tipo == "json":
        v = de_json(rel, resto.split("#", 1)[1])
        v = ("sí" if v else "no") if isinstance(v, bool) else str(v)
    else:
        linea, fila, columna = resto.split("#", 1)[1].split("|")
        lineas = leer(rel).splitlines()
        i = next(k for k, l in enumerate(lineas) if linea in l)
        while not lineas[i].startswith("|"):
            i += 1
        celdas = lambda l: [c.strip().replace("\\|", "|") for c in re.split(r"(?<!\\)\|", l.strip()[1:-1])]  # noqa: E731
        cab = [norm(c) for c in celdas(lineas[i])]
        k = i + 2
        while not norm(celdas(lineas[k])[0]) == norm(fila):
            k += 1
        v = celdas(lineas[k])[cab.index(norm(columna))]
    if patron:
        v = list(re.finditer(patron, v, re.M))[0].group(grupo)
    return v


def _sin_msh10(l):
    """El caso y el control llevan distinto MSH-10 (su identificador); eso no es el disparador."""
    if not l.startswith("MSH"):
        return l
    p = l.split("|")
    return "|".join(p[:9] + [""] + p[10:]) if len(p) > 9 else l


def hl7(par, cual):
    """El mensaje mínimo, con las líneas que no están en el otro mensaje del par marcadas (sin contar MSH-10)."""
    otro = "control" if cual == "caso" else "caso"
    esta = PARES[par][cual].replace("\r", "\n").strip("\n").split("\n")
    otra = {_sin_msh10(l) for l in PARES[par][otro].replace("\r", "\n").strip("\n").split("\n")}
    lineas = ["<mark>%s</mark>" % esc(l) if _sin_msh10(l) not in otra else esc(l) for l in esta]
    return '<pre class="hl7" data-fuente="hl7:%s#%s">%s</pre>' % (par, cual, "\n".join(lineas))


def enlace(rel, texto_):
    return '<a href="%s%s">%s</a>' % (GH, rel, texto_)


def j(puntero, rel=CLASES):
    return "json:%s#%s" % (rel, puntero)


# ---------------------------------------------------------------------------- las frases del artículo para cada discrepancia
FRASES = {  # L-PG-2: la única tabla a mano. Cada patrón se resuelve contra ARTICULO.md al escribir
    "M-24": r"^\*\*(Un valor que se multiplica por diez)\*\* \(Microsoft\)",
    "M-23": r"^\*\*(Resultados colgados de un paciente que no existe)\*\* \(Microsoft\)",
    "M-18": r"^\*\*(Un paciente al que se da por muerto)\*\* \(Microsoft\)",
    "L-10": r"^\*\*(«Separado» que pasa a «anulado»)\*\* \(LinuxForHealth\)",
    "L-15": r"^\*\*(Resultados que desaparecen)\*\* \(LinuxForHealth\)",
    "L-16": r"^\*\*(Texto con formato y horas que se pierden)\*\* \(LinuxForHealth\)",
    "L-20": r"^\*\*(Un rango que pasa a ser un número)\*\* \(LinuxForHealth\)",
    "M-7": r"^\| Microsoft \| (De un médico remitente repetido \(PV1-8\), solo llega el primero) \|$",
    "M-10": r"^\| Microsoft \| (Un estado civil «no declarado» \(T\) se pierde; la guía da un nullFlavor) \|$",
    "L-1": r"^\| LinuxForHealth \| (No hay Encounter\.location: la ubicación del paciente \(PV1-3\) no se convierte) \|$",
    "L-11": r"^\| LinuxForHealth \| (Las partes 2 y 3 de la calle \(SAD\.2 y SAD\.3\) no llegan a la dirección) \|$",
    "L-12": r"^\| LinuxForHealth \| (Un sexo «no aplicable» \(N\) pasa a «desconocido»; la guía da «otro») \|$",
    "L-18": r"^\| LinuxForHealth \| (Un resultado borrado \(OBX-11 «D»\) pasa a «cancelado»; la guía da «introducido por error») \|$",
    "L-19": r"^\| LinuxForHealth \| (Un informe con la muestra recibida \(OBR-25 «I»\) pasa a «desconocido»; la guía da «registrado») \|$",
    "L-22": r"^\| LinuxForHealth \| (El «otro profesional» de la visita \(PV1-52\) se pierde) \|$",
}
T15 = "tabla:%sRESULTADO-CV3.md### Las 15 nuevas y confirmadas|%%s|%%s" % CV
T15A = "tabla:%sRESULTADO-15A.md### Cada nueva, en la versión fijada|%%s|Rama principal" % CV


def orden_15():
    lineas = leer(CV + "RESULTADO-CV3.md").splitlines()
    i = next(k for k, l in enumerate(lineas) if l.startswith("## Las 15 nuevas"))
    ids = []
    for l in lineas[i:]:
        m = re.match(r"^\| ([ML]-\d+) \|", l)
        if m:
            ids.append(m.group(1))
        elif ids and not l.startswith("|"):
            break
    return ids


def veredicto_par(par, conv, con_juez=True):
    """Revisión de la 19, hallazgo 2: lo que se confirma es que el hallazgo buscado salga en el caso y no en el control; la
    categoría del control puede ser fallo_silencioso por otros mecanismos."""
    p, P = de_json(MINIMOS, "pares[id=%s]" % par), "pares[id=%s]" % par
    base = "%s.%s" % (P, conv)
    if p["objetivo"]["subtipo"] == "error":
        buscado = "El rechazo buscado"
    else:
        h = p["objetivo"]["hecho"]
        hechos = " o ".join(texto(j("%s.objetivo.hecho.%d" % (P, k), MINIMOS), tag="code") for k in range(len(h))) \
            if isinstance(h, list) else texto(j(P + ".objetivo.hecho", MINIMOS), tag="code")
        buscado = "El hallazgo buscado (%s, en %s)" % (texto(j(P + ".objetivo.texto", MINIMOS), tag="code"), hechos)
    lineas = ['<p class="ver">%s sale en el caso: %s; en el control: %s. Se confirma: %s.</p>' % (
                  buscado, texto(j(base + ".caso.sale", MINIMOS), tag="strong"), texto(j(base + ".control.sale", MINIMOS), tag="strong"),
                  texto(j(P + ".confirmada", MINIMOS), tag="strong")),
              '<p class="ver">Con el conversor para el que se escribió, el caso sale %s y el control, %s.</p>' % (
                  texto(j(base + ".caso.categoria", MINIMOS), tag="code"), texto(j(base + ".control.categoria", MINIMOS), tag="code"))]
    if con_juez:
        for k, _ in enumerate(p[conv]["caso"]["que"][:2]):
            lineas.append('<p class="juez">El juez, en el caso: %s</p>' % texto(j("%s.caso.que.%d" % (base, k), MINIMOS), tag="q"))
    return "\n".join(lineas)


def bloque_par(par, conv, con_juez=True):
    return ('<div class="par">\n<div><p class="rot">Caso</p>\n%s</div>\n<div><p class="rot">Control</p>\n%s</div>\n</div>\n%s'
            % (hl7(par, "caso"), hl7(par, "control"), veredicto_par(par, conv, con_juez)))


MATICES = {  # los matices de la revisión (RESULTADO-CV3.md), cada uno en su tarjeta
    "M-18": r"^- \*\*M-18:\*\* (.+)$", "L-11": r"^- \*\*L-11:\*\* (.+)$", "L-22": r"^- \*\*L-22:\*\* (.+)$",
    "L-1": r"^- \*\*L-1:\*\* (.+)$", "L-12": r"^- \*\*L-12 y L-19:\*\* (.+\n  .+)$", "L-19": r"^- \*\*L-12 y L-19:\*\* (.+\n  .+)$",
}


def tarjeta(cid):
    c = de_json(CLASES, "clases[id=%s]" % cid)
    conv = c["conversor"]
    pares = [x.strip() for x in c["par_minimo"].split("/")]
    fuerza = unicodedata.normalize("NFKD", c["fuerza"]).encode("ascii", "ignore").decode()     # «débil» -> clase «debil»
    cab = ('<p class="disc-cab">%s · %s · %s</p>' % (
        texto(j("clases[id=%s].id" % cid), clase="disc-id"), texto(T15 % (cid, "Conversor")),
        texto(j("clases[id=%s].fuerza" % cid), clase="fuerza fuerza-%s" % fuerza)))
    det = ['<dl class="registro">',
           "<dt>Qué registró el estudio</dt><dd>%s</dd>" % texto(T15 % (cid, "Discrepancia"), md=True),
           "<dt>Cita de la guía</dt><dd>%s</dd>" % texto(T15 % (cid, "Guía"), md=True),
           "<dt>Casos en el corpus</dt><dd>%s</dd>" % texto(T15 % (cid, "Casos"), md=True),
           "<dt>En la rama principal</dt><dd>%s</dd>" % texto(T15A % cid, md=True)]
    if cid in MATICES:
        det.append("<dt>Matiz de la revisión</dt><dd>%s</dd>" % texto("md:%sRESULTADO-CV3.md" % CV, MATICES[cid], md=True))
    det.append("</dl>")
    for par in pares:
        det.append('<p class="rot">Par mínimo %s</p>' % texto(j("pares[id=%s].id" % par, MINIMOS), tag="code"))
        det.append(bloque_par(par, conv))
    return ('<article class="disc" id="%s" data-conv="%s">\n%s\n<h4>%s</h4>\n<details>\n<summary>El registro del estudio, la cita '
            'y el par mínimo</summary>\n%s\n</details>\n</article>' % (
                cid, conv, cab, texto("md:ARTICULO.md", FRASES[cid]), "\n".join(det)))


# ---------------------------------------------------------------------------- la página
def seccion(n, sid, titulo, cuerpo):
    """El número de la sección lo pone un contador de CSS: no es una cifra del estudio (`n` solo documenta el orden)."""
    return '<section id="%s" class="numerada">\n<h2><span class="num"></span>%s</h2>\n%s\n</section>' % (sid, titulo, cuerpo)


def cabecera():
    rc = "verificador/RESULTADO-CONVERSORES.md"
    return "\n".join([
        '<p class="eyebrow">Laboratorio de integraciones · %s</p>' % texto("md:ARTICULO.md", r"^\*Laboratorio de integraciones, (octubre de 2026)\.\*$"),
        "<h1>Lo que vio un juez en dos conversores</h1>",
        '<p class="standfirst">Un mensaje con una proteína C reactiva de %s entra en un conversor de código abierto y sale como %s. '
        "Nada avisa. Un juez determinista, que lee la guía HL7 v2-to-FHIR y cita cada cosa que afirma, pasó por dos conversores "
        "%s mensajes públicos.</p>" % (
            texto("md:ARTICULO.md", r"proteína C reactiva de \*\*(\.5 mg/L)\*\*", tag="strong"),
            texto("md:ARTICULO.md", r"un recurso\nFHIR con \*\*(5 mg/L)\*\*", tag="strong"), cifra(j("frase.M_mensajes"))),
        '<div class="meta">',
        "<span>Microsoft FHIR-Converter <b>%s</b></span>" % texto("md:" + rc, r"\*\*Microsoft FHIR-Converter:\*\* (v7\.0) \("),
        "<span>LinuxForHealth hl7v2-fhir-converter <b>%s</b></span>" % texto("md:" + rc, r"\*\*LinuxForHealth hl7v2-fhir-converter:\*\* (v1\.1\.0) de"),
        "<span>Referencia: %s</span>" % texto("md:" + rc, r"^\| Referencia \| (.+?) \|$", md=True),
        "<span>Corpus: <b>%s</b> mensajes (ADT %s, ORU %s y %s muestras)</span>" % (
            cifra(j("frase.M_mensajes")), cifra(j("por_conversor.microsoft.adt.n", CV + "RESULTADO-CV2.json")),
            cifra(j("por_conversor.microsoft.oru.n", CV + "RESULTADO-CV2.json")),
            cifra(j("por_conversor.microsoft.muestras.n", CV + "RESULTADO-CV2.json"))),
        "<span>Juez de los resultados sellados <b>%s</b>, del cierre y la rama principal <b>%s</b>, publicado como <b>%s</b> (se "
        "diferencia en un extracto que el juez cita, no en su lógica)</span>" % (
            texto(j("juez"), r"^(.{8})"), texto(j("juez", CV + "RESULTADO-15A-minimos-main.json"), r"^(.{8})"),
            texto("md:verificador/MANIFIESTO.txt", r"huella del juez publicado con el estudio de conversores \(24-oct\):\s+([0-9a-f]{8})")),
        "<span>Fechas: %s</span>" % texto("md:" + rc, r"^\| Fechas \| (23 y 24 de octubre),"),
        "</div>"])


def indice(secciones):
    return ('<nav class="indice" aria-label="Secciones"><ol>%s</ol></nav>' %
            "".join('<li><a href="#%s">%s</a></li>' % (sid, t) for sid, t in secciones))


def resumen():
    rc = "verificador/RESULTADO-CONVERSORES.md"
    return "\n".join([
        '<section id="resumen">',
        '<div class="tesis"><p>El verificador encuentra %s discrepancias nuevas y confirmadas en %s de %s conversores, sobre %s mensajes '
        "públicos; además ve %s de las ya declaradas, y %s diferencias son convención.</p>"
        '<span class="une" aria-hidden="true"></span><p><strong>No es una certificación.</strong> Es lo que ve un juez determinista con '
        "sus decisiones declaradas, en esas versiones y en esos dos tipos de mensaje.</p></div>" % (
            cifra(j("frase.N_nuevas_confirmadas")), cifra(j("frase.K_conversores")),
            cifra("md:" + rc, r"confirmadas en 2 de (2) conversores"),
            cifra(j("frase.M_mensajes")), cifra(j("frase.D_ya_declaradas")), cifra(j("frase.C_convenciones"))),
        "<p>De las %s, %s son de Microsoft y %s de LinuxForHealth, y %s son fuertes.</p>" % (
            cifra(j("frase.N_nuevas_confirmadas")), cifra(j("frase.N_por_conversor.microsoft")),
            cifra(j("frase.N_por_conversor.linuxforhealth")), cifra(j("frase.N_fuertes"))),
        '<dl class="reglas"><dt>Qué es «confirmada»</dt><dd>Cada una cumple %s condiciones: tiene su cita en la guía; cae en una de las %s '
        "clases que cambian el significado del dato; el proyecto no la tenía declarada en sus salidas esperadas, sus pruebas, su "
        "documentación, los comentarios de sus plantillas ni sus issues; y se reproduce con un par de mensajes mínimos, en una caja "
        "sin red.</dd></dl>" % (cifra("md:" + rc, r"Cada una cumple (cuatro) condiciones"),
                                 cifra("md:ARTICULO.md", r"una de \*\*(ocho) clases que cambian")),
        "</section>"])


def s01():
    return seccion("01", "s01", "El problema: un conversor se prueba con sus propias respuestas", "\n".join([
        "<p>Un proyecto de conversión publica sus salidas esperadas y las usa en sus pruebas. Esas salidas dicen qué hace el "
        "conversor, no si lo que hace es lo que dice la guía. Si la plantilla se equivoca, la salida esperada se equivoca con ella y "
        "la prueba pasa.</p>",
        "<p>En este estudio se comprobó con Microsoft: sus salidas esperadas, %s muestras, juzgadas con el mismo juez dan los mismos "
        "hallazgos que su conversión real. Por eso hace falta un juez que no se fíe del conversor: que lea la guía, que cite cada "
        "cosa que afirma y que diga lo que no sabe.</p>" % cifra("md:%sRESULTADO-CV3.md" % CV, r"Son (62) muestras")]))


def s02():
    filas = []
    for clase in ("valor distinto", "dato perdido", "dato inventado", "código mal mapeado", "valor imposible convertido",
                  "recurso ausente, duplicado o inventado", "referencia rota", "FHIR inválido"):
        filas.append("<tr><td>%s</td><td>%s</td></tr>" % (texto("tabla:ARTICULO.md### El juez|%s|Clase" % clase),
                                                         texto("tabla:ARTICULO.md### El juez|%s|Ejemplo" % clase)))
    return seccion("02", "s02", "El juez", "\n".join([
        "<p>El verificador nació para juzgar circuitos propios: un motor de integración que recibe HL7 v2, contesta con un acuse y "
        "escribe FHIR. Es un programa en Python, sin dependencias y sin ningún modelo de lenguaje: a la misma evidencia, el mismo "
        "veredicto. Para juzgar conversores ajenos se le añadió un perfil «guía», que toma lo esperado de los mapas de la guía "
        "v2-to-FHIR y de sus hojas, citadas por fichero y fila.</p>",
        "<p>Una discrepancia cuenta si cae en una de estas clases, que cambian el significado del dato:</p>",
        '<div class="tabla-caja"><table><thead><tr><th>Clase</th><th>Ejemplo</th></tr></thead><tbody>%s</tbody></table></div>' % "".join(filas),
        '<div class="principio"><p>Lo demás es forma y no cuenta: el orden, los identificadores, cómo se escribe una referencia. '
        "Cuando la guía admite dos lecturas, o no decide, el juez lo declara como convención y no lo cuenta.</p></div>"]))


PASOS = [  # los títulos del método, de ARTICULO.md (el número lo pone la lista), con una línea que lo explica y su documento
    (r"^1\. \*\*(La pregunta, la regla de éxito y la de fracaso, escritas antes de empezar)\*\*",
     "Si no salía al menos una discrepancia nueva y confirmada, se dejaba de invertir en el verificador.",
     "verificador/ANTES-ETAPA-CONVERSORES.md", "el ANTES"),
    (r"^2\. \*\*(El diseño, a ciegas\.)\*\*",
     "El perfil «guía» lo diseñó un modelo distinto del que lo programó, sin ver lo que devuelven los conversores. Lo que ni la "
     "guía ni el estándar deciden lo decidió un modelo de decisión, sobre un estado escrito sin recomendación.",
     CV + "diseno-conversores-fable.md", "el diseño"),
    (r"^3\. \*\*(La previsión sellada antes de correr nada)\*\*",
     "Con la huella del juez: qué proporción de casos saldría bien en cada conversor y qué mecanismos se esperaban.",
     CV + "PREVISION-CV2.md", "la previsión"),
    (r"^4\. \*\*(Los conversores, aislados\.)\*\*",
     "Docker sin red, de solo lectura, sin privilegios, con la versión fijada por su huella.", CV + "CV1.md", "la construcción"),
    (r"^5\. \*\*(El contraste con lo que el proyecto ya sabe\.)\*\*",
     "Sus salidas esperadas, sus pruebas, su documentación, los comentarios de sus plantillas, sus issues y los comentarios de "
     "esos issues.", CV + "RESULTADO-CV3.md", "el contraste"),
    (r"^6\. \*\*(Un par de mensajes mínimos por cada nueva\.)\*\*",
     "El caso trae solo el disparador y el control es el mismo mensaje sin él; cuenta solo si el fallo sale en el caso y no en "
     "el control.", CV + "cv3_minimos.py", "el generador de los pares"),
    (r"^7\. \*\*(Una revisión adversaria\.)\*\*",
     "Agentes de modelo de lenguaje, uno por conversor, recibieron las candidatas con el encargo de romperlas, en sesiones aparte.",
     CV + "RESULTADO-CV3.md", "lo que cayó"),
    (r"^8\. \*\*(La rama principal\.)\*\*",
     "Las que quedaron se volvieron a probar en la rama principal de cada proyecto, construida desde su código.",
     CV + "RESULTADO-15A.md", "las ramas principales"),
]


def s03():
    pasos = "".join("<li>%s %s (%s)</li>" % (texto("md:ARTICULO.md", p, tag="strong"), esc(expl), enlace(rel, nombre))
                    for p, expl, rel, nombre in PASOS)
    return seccion("03", "s03", "El método: escribirlo todo antes de mirar", "\n".join([
        "<p>Un juez que busca fallos ajenos corre un riesgo evidente: encontrar lo que quiere encontrar. Por eso el estudio se hizo "
        "con las mismas reglas que el resto del laboratorio:</p>",
        '<ol class="pasos">%s</ol>' % pasos,
        "<p>La revisión adversaria intentó romper las %s candidatas y tumbó %s. En la rama principal de cada proyecto, de las %s "
        "siguen %s.</p>" % (
            cifra("md:%sRESULTADO-CV3.md" % CV, r"romper las (25) candidatas y tumbó (10)"),
            cifra("md:%sRESULTADO-CV3.md" % CV, r"romper las (25) candidatas y tumbó (10)", 2),
            cifra("md:%sRESULTADO-15A.md" % CV, r"de las (15) nuevas, (14) siguen en la rama principal"),
            cifra("md:%sRESULTADO-15A.md" % CV, r"de las (15) nuevas, (14) siguen en la rama principal", 2))]))


def s04():
    ids = orden_15()
    fuertes = [x for x in ids if de_json(CLASES, "clases[id=%s]" % x)["fuerza"] == "fuerte"]
    resto = [x for x in ids if x not in fuertes]
    filtro = "\n".join([
        '<input type="radio" name="conv" id="f-todos" class="filtro-in" checked>',
        '<input type="radio" name="conv" id="f-ms" class="filtro-in">',
        '<input type="radio" name="conv" id="f-lfh" class="filtro-in">',
        '<div class="filtro" role="group" aria-label="Filtrar las discrepancias por conversor">'
        '<label for="f-todos">Los dos</label><label for="f-ms">Microsoft (%s)</label><label for="f-lfh">LinuxForHealth (%s)</label></div>' % (
            cifra(j("frase.N_por_conversor.microsoft")), cifra(j("frase.N_por_conversor.linuxforhealth")))])
    lista = ['<div class="lista">',      # con el filtro puesto, la cuenta de cada grupo se oculta: ya no es la de lo que se ve
             "<h3>Las %s que más pesan</h3>" % texto("md:ARTICULO.md", r"^### Las (siete) que más pesan$", clase="cuenta")]
    lista += [tarjeta(x) for x in fuertes]
    lista += ["<h3>Las otras %s</h3>" % texto("md:ARTICULO.md", r"^### Las otras (ocho)$", clase="cuenta")]
    lista += [tarjeta(x) for x in resto]
    lista.append("</div>")
    return seccion("04", "s04", "Lo que encontró", "\n".join([
        "<p>Están ordenadas por fuerza, como en el estudio. Los mensajes son los pares mínimos, sintéticos y en v2.5: el caso trae "
        "solo el disparador, marcado, y el control es el mismo mensaje sin él. Lo que dijo el juez se muestra tal cual, sin "
        "reescribirlo. Los Bundles que devolvieron los conversores no se publican.</p>",
        "<p>Lo que confirma una discrepancia es que el hallazgo buscado salga en el caso y no en el control. La categoría del "
        "control puede ser también fallo silencioso, por otros mecanismos que ya se cuentan aparte.</p>",
        filtro] + lista + [
        "<p>%s</p>" % texto("md:ARTICULO.md", r"^- \*\*Los dos conversores son proyectos serios y útiles\.\*\* (Las discrepancias son con una guía concreta, en una versión concreta\.)$")]))


def s05():
    t = "tabla:%sRESULTADO-15A.md#Las dos ramas se construyeron desde su código|%%s|%%s" % CV
    filas = "".join("<tr><th scope=\"row\">%s</th><td>%s</td><td>%s</td></tr>" % (fila, texto(t % (fila, "Microsoft"), md=True),
                                                                            texto(t % (fila, "LinuxForHealth"), md=True))
                    for fila in ("Rama y commit", "Cómo se construye", "Cómo corre"))
    return seccion("05", "s05", "En la rama principal", "\n".join([
        "<p>De las %s nuevas, %s siguen en la rama principal y %s está corregida allí: la de OBX-11 «D», que pasaba a «cancelado». "
        "LinuxForHealth cambió ese mapeo por su cuenta, sin saber de este laboratorio, después de la versión juzgada, y todavía no ha "
        "publicado una versión que lo lleve.</p>" % (
            cifra("md:%sRESULTADO-15A.md" % CV, r"de las (15) nuevas, (14) siguen en la rama principal y (una) está corregida"),
            cifra("md:%sRESULTADO-15A.md" % CV, r"de las (15) nuevas, (14) siguen en la rama principal y (una) está corregida", 2),
            cifra("md:%sRESULTADO-15A.md" % CV, r"de las (15) nuevas, (14) siguen en la rama principal y (una) está corregida", 3)),
        '<div class="tabla-caja"><table><thead><tr><th></th><th>Microsoft</th><th>LinuxForHealth</th></tr></thead><tbody>%s</tbody></table></div>' % filas,
        "<p>En los %s mensajes mínimos, las dos ramas se diferencian solo en dos.</p>" % cifra(
            "md:%sRESULTADO-15A.md" % CV, r"^\*\*En los (68) mensajes, las dos ramas se diferencian solo en dos")]))


EJEMPLOS_DECLARADAS = [
    r"^  - (apunta Encounter\.location al componente menos granular de la ubicación \(un issue abierto\));$",
    r"^  - (cuando dos resultados tienen el mismo código, se queda con uno \(su documentación lo explica\));$",
    r"^  - (pierde el resultado que sigue a una nota \(un issue, en sus comentarios\))\.$",
    r"^  - (toma la fecha de inicio de la visita del evento cuando falta la de admisión \(una prueba lo afirma\));$",
    r"^  - (no soporta tres de los eventos ADT probados \(su README lo dice\))\.$",
]


def s06():
    ej = "".join("<li>%s: %s</li>" % ("Microsoft" if k < 3 else "LinuxForHealth", texto("md:ARTICULO.md", p))
                 for k, p in enumerate(EJEMPLOS_DECLARADAS))
    return seccion("06", "s06", "Lo que los proyectos ya sabían", "\n".join([
        "<p>El juez vio también %s discrepancias que los proyectos ya tenían declaradas: %s de Microsoft y %s de LinuxForHealth. Son "
        "el control positivo: si el juez no viera lo que los autores ya saben, nada de lo demás valdría. Entre ellas:</p>" % (
            cifra(j("frase.D_ya_declaradas")), cifra(j("frase.D_por_conversor.microsoft")),
            cifra(j("frase.D_por_conversor.linuxforhealth"))),
        "<ul>%s</ul>" % ej,
        "<p>Cada una, con dónde la declara el proyecto, está en %s.</p>" % enlace(CV + "RESULTADO-CV3.md", "el registro del estudio")]))


def s07():
    rechazos = []
    for cid in ("M-12", "M-15"):
        c = de_json(CLASES, "clases[id=%s]" % cid)
        rechazos.append("<li>%s: %s<details><summary>El par mínimo</summary>\n%s\n</details></li>" % (
            texto(j("clases[id=%s].id" % cid)), texto(j("clases[id=%s].que" % cid), md=True),
            bloque_par(c["par_minimo"], c["conversor"], con_juez=False)))
    return seccion("07", "s07", "Lo que no cuenta", "\n".join([
        "<p>%s diferencias son convención: formas que la guía admite, o sobre las que no decide. Son %s mecanismos de nota del juez "
        "final, repartidos entre los dos conversores, más el tipo «VN» de PV1-19 en los dos. Se cuentan aparte y no entran en lo que "
        "se encontró.</p>" % (
            cifra(j("frase.C_convenciones")), cifra("md:%sRESULTADO-CV3.md" % CV, r"^\*\*Son (14) mecanismos de nota")),
        "<p>Hay además %s rechazos nuevos de Microsoft, que no entran en la frase porque un rechazo falla a la vista:</p>" % cifra(j("frase.rechazos_nuevos")),
        "<ul>%s</ul>" % "".join(rechazos),
        "<p>%s más son dudosas y no cuentan: las preguntas Q-CV-D-15 y Q-CV-D-16 siguen abiertas. Y la revisión adversaria tumbó %s "
        "candidatas, cada una con su motivo y su cita en %s.</p>" % (
            cifra(j("frase.dudosas")), cifra("md:%sRESULTADO-CV3.md" % CV, r"^## Las (10) que cayeron en la revisión"),
            enlace(CV + "RESULTADO-CV3.md", "el registro del estudio"))]))


def s08():
    t = "tabla:verificador/RESULTADO-CONVERSORES.md### Qué cambió en el juez durante la etapa|%s|%s"
    filas = "".join("<tr><td>%s</td><td>%s</td><td>%s</td></tr>" % (texto(t % (f, "Fase")), texto(t % (f, "Huella"), md=True),
                                                                   texto(t % (f, "Qué"), md=True))
                    for f in ("CV1", "CV2, repetición 1", "CV3, rejuicios 1 y 2", "CV4"))
    return seccion("08", "s08", "Lo que el juez se equivocó, y se corrigió", "\n".join([
        "<p>Un juez que juzga a otros tiene que mirarse primero. Durante el estudio se le encontraron %s defectos, cada uno "
        "arreglado con su prueba en rojo antes del código: %s al revisar el primer juicio, %s en los que la guía admitía lo "
        "observado y %s que dejó el contraste. El más claro, un falso positivo: los dos conversores ponen el nombre de la autoridad "
        "que asigna el identificador transformado, y el juez buscaba el texto literal.</p>" % (
            cifra("md:ARTICULO.md", r"se le encontraron \*\*(once) defectos\*\*"),
            cifra("md:ARTICULO.md", r"^- \*\*(4), al revisar el primer juicio\.\*\*"),
            cifra("md:ARTICULO.md", r"^- \*\*(4) en los que la guía admitía lo observado\.\*\*"),
            cifra("md:ARTICULO.md", r"^- \*\*(3) que dejó el contraste\.\*\*")),
        '<div class="tabla-caja"><table><thead><tr><th>Fase</th><th>Huella</th><th>Qué</th></tr></thead><tbody>%s</tbody></table></div>' % filas,
        '<div class="principio"><p>Lo que no se hizo fue mover la previsión.</p></div>']))


def s09():
    t = "tabla:%sRESULTADO-CV2.md### Lo que salió, frente a lo previsto|%%s|%%s" % CV
    filas = "".join("<tr><td>%s</td><td class=\"n\">%s</td><td class=\"n\">%s</td><td class=\"n\">%s</td><td class=\"n\">%s</td></tr>" % (
        texto(t % (f, "Conversor · familia")), texto(t % (f, "n")), texto(t % (f, "correcto")), texto(t % (f, "fallo_silencioso")),
        texto(t % (f, "rechazo_incorrecto")))
        for f in ("Microsoft · ADT", "Microsoft · ORU", "LinuxForHealth · ADT", "LinuxForHealth · ORU"))
    prev = "".join("<tr><td>%s</td><td class=\"n\">%s</td><td class=\"n\">%s</td></tr>" % (
        d, texto(j("frase_prevista.%s" % k, CV + "PREVISION-CV2.json")), cifra(j(s)))
        for k, d, s in (("N", "discrepancias nuevas y confirmadas", "frase.N_nuevas_confirmadas"),
                        ("K", "conversores con alguna", "frase.K_conversores"),
                        ("D", "ya declaradas que el juez ve", "frase.D_ya_declaradas"),
                        ("C", "convenciones", "frase.C_convenciones")))
    return seccion("09", "s09", "La previsión sellada, frente a lo que salió", "\n".join([
        "<p>La previsión se selló con la huella del juez antes de correr nada. Falló por mucho, y eso queda escrito, no corregido.</p>",
        '<div class="tabla-caja"><table><caption>Categorías por conversor y familia. Entre corchetes, el rango sellado.</caption>'
        '<thead><tr><th>Conversor · familia</th><th class="n">n</th><th class="n">correcto</th><th class="n">fallo silencioso</th>'
        '<th class="n">rechazo incorrecto</th></tr></thead><tbody>%s</tbody></table></div>' % filas,
        '<div class="tabla-caja"><table><caption>La frase prevista y la que salió</caption><thead><tr><th></th><th class="n">Prevista</th>'
        '<th class="n">Salió</th></tr></thead><tbody>%s</tbody></table></div>' % prev,
        "<p>De los rechazos de Microsoft, %s eran un mensaje mal hecho del propio corpus del laboratorio: un segmento GT1 desplazado "
        "un campo. Los %s de LinuxForHealth en ADT eran eventos que esa versión no soporta.</p>" % (
            cifra(j("clases[id=M-11].casos.adt")), cifra(j("clases[id=L-4].casos.adt")))]))


def s10():
    vc, rd = CV + "VC.md", "verificador/README.md"
    pasos = "".join("<li>%s</li>" % texto("md:" + rd, r"^%d\. (.+?)[;.]$" % k, md=True) for k in range(1, 6))
    cv = "tabla:%svc/CONTROL-VC.md# VC3:|%%s|%%s" % CV
    control = "".join("<tr><td>%s</td><td class=\"n\">%s</td><td class=\"n\">%s</td></tr>" % (f, texto(cv % (f, "Microsoft")),
                                                                                        texto(cv % (f, "LinuxForHealth")))
                      for f in ("Casos comparados", "Diferencias"))
    codigos = "".join("<tr><td class=\"n\">%s</td><td>%s</td></tr>" % (
        texto("tabla:%s#**Los códigos de salida:**|%s|Código" % (vc, k)), texto("tabla:%s#**Los códigos de salida:**|%s|Qué quiere decir" % (vc, k), md=True))
        for k in ("0", "2", "3", "4", "5", "1"))
    caja = "".join("<li>%s</li>" % texto(j("caja.restricciones.%d" % k, INFORME), tag="code") for k in range(7))
    limites = "".join("<li>%s</li>" % texto(j("limites.L-VC.%s" % k, INFORME))
                      for k in ("L-VC-1", "L-VC-2", "L-VC-3", "L-VC-4", "L-VC-7", "L-VC-9", "L-VC-14", "L-VC-15"))
    return seccion("10", "s10", "Pasa tu conversor por el mismo juez", "\n".join([
        "<p>Cualquiera puede pasar su conversor HL7 v2 → FHIR R4 por el verificador con un fichero de adaptador JSON y una orden, "
        "sin escribir código:</p>",
        texto("md:" + vc, r"^(python3 cv/verificar_conversor\.py .+)$", tag="pre"),
        "<p>La herramienta:</p><ol>%s</ol>" % pasos,
        '<div class="principio"><p class="rot">Lo que no puede saber</p><p>%s</p></div>' % texto(
            j("contraste_con_el_proyecto.texto", INFORME), md=True),
        "<p>El adaptador es un JSON declarativo con %s bloques: el conversor, la caja, la invocación, la salida y los límites. Se copia "
        "uno de los de ejemplo y se cambian los datos: el nombre, la versión y las partes de la huella; la imagen y los montajes, "
        "siempre de solo lectura; la orden con sus marcadores; y cómo se lee la salida. Los de ejemplo están en %s, y cómo se usa, "
        "en %s.</p>" % (cifra("md:" + vc, r"Es un JSON declarativo con (cinco) bloques"),
                        enlace(CV + "adaptadores", "la carpeta de adaptadores"), enlace(vc, "su documento")),
        "<p>El conversor corre en una caja que el adaptador no puede relajar:</p><ul class=\"caja\">%s</ul>" % caja,
        '<div class="tabla-caja"><table><caption>El control: con los adaptadores de los dos conversores del estudio, frente al juicio '
        'del estudio con su juez final</caption><thead><tr><th></th><th class="n">Microsoft</th><th class="n">LinuxForHealth</th>'
        '</tr></thead><tbody>%s</tbody></table></div>' % control,
        "<p>Los pares mínimos coinciden los %s. La comparación caso por caso se hizo con un detalle del estudio que no es público; lo "
        "que se puede repetir desde el repositorio lo dice %s.</p>" % (
            cifra("md:" + vc, r"coinciden los (34)\."), enlace(CV + "vc/CONTROL-VC.md", "el documento del control")),
        '<div class="tabla-caja"><table><caption>Los códigos de salida</caption><thead><tr><th class="n">Código</th><th>Qué quiere '
        'decir</th></tr></thead><tbody>%s</tbody></table></div>' % codigos,
        "<p>Lo que no hace:</p><ul class=\"limites\">%s</ul>" % limites]))


NO_DICE = [  # el grupo empieza en el «**» de apertura, para que en_linea vea el par entero (revisión de la 19, hallazgo 1)
    r"^- \*\*No es una certificación de conformidad\.\*\* (Es lo que un juez con sus decisiones declaradas ve en estos mensajes y en estas\n  versiones):$",
    r"^  - (\*\*Microsoft FHIR-Converter v7\.0\.\*\*)$",
    r"^  - (\*\*LinuxForHealth hl7v2-fhir-converter v1\.1\.0,\*\* la última publicada en Maven Central\. En GitHub hay una etiqueta v1\.1\.1 y una\n    rama principal que soportan más eventos\. La v1\.1\.0 rechaza tres de los ocho eventos ADT probados, y eso se contó como\n    rechazo, no como discrepancia\.)$",
    r"^  - (\*\*Las ramas principales de los dos,\*\* tal como estaban en octubre de 2026\.)$",
    r"^- (\*\*Cubre ocho eventos ADT y ORU\^R01\.\*\* No cubre programación de citas \(SIU\), documentos \(MDM\), vacunas \(VXU\) ni los demás tipos\.)$",
    r"^- (\*\*Los mensajes son sintéticos o públicos\.\*\* No hay datos de ningún paciente\.)$",
    r"^- (\*\*El juez lee los tipos de datos de v2\.5\.\*\* Las muestras de los proyectos son casi todas de v2\.8, y lo que dependía de\n  componentes posteriores se apartó\.)$",
    r"^- (\*\*Los dos conversores son proyectos serios y útiles\.\*\* Las discrepancias son con una guía concreta, en una versión concreta\.\n  Parte de lo que encontró el juez ya estaba en su documentación, y una la ha cambiado el propio proyecto\.)$",
]


def s11():
    versiones = "".join("<li>%s</li>" % texto("md:ARTICULO.md", p, md=True) for p in NO_DICE[1:4])
    items = ['<li><strong>No es una certificación de conformidad.</strong> %s:<ul class="versiones">%s</ul></li>' % (
        texto("md:ARTICULO.md", NO_DICE[0]), versiones)]
    items += ["<li>%s</li>" % texto("md:ARTICULO.md", p, md=True) for p in NO_DICE[4:]]
    return seccion("11", "s11", "Lo que esto no dice", '<ul class="limites">%s</ul>' % "".join(items))


def s12():
    return seccion("12", "s12", "Cómo reproducirlo", "\n".join([
        "<p>El verificador corre con Python y nada más. Sus pruebas, incluidas las %s comprobaciones del perfil «guía», pasan sin el "
        "laboratorio (%s). Para repetir el estudio hacen falta además Docker, para la caja; los dos conversores, construidos como "
        "dice %s; y las muestras públicas de cada proyecto.</p>" % (
            cifra("md:ARTICULO.md", r"incluidas las (116) comprobaciones"), enlace("verificador/README.md", "su documento"),
            enlace(CV + "CV1.md", "el registro de la construcción")),
        "<p>Los %s mensajes mínimos salen de %s.</p>" % (
            cifra("md:ARTICULO.md", r"^Los (68) mensajes mínimos salen de"),
            texto("md:ARTICULO.md", r"^Los 68 mensajes mínimos salen de `(python3 verificador/cv/cv3_minimos\.py escribir <carpeta>)`\.$",
                  tag="code")),
        "<p>El estudio entero, contado de corrido, está en %s, y el cierre, en %s.</p>" % (
            enlace("ARTICULO.md", "el artículo"), enlace("verificador/RESULTADO-CONVERSORES.md", "su resultado"))]))


SECCIONES = [("resumen", "Resumen"), ("s01", "El problema"), ("s02", "El juez"), ("s03", "El método"), ("s04", "Lo que encontró"),
             ("s05", "En la rama principal"), ("s06", "Lo que ya sabían"), ("s07", "Lo que no cuenta"),
             ("s08", "Lo que el juez se equivocó"), ("s09", "La previsión"), ("s10", "Pasa tu conversor"),
             ("s11", "Lo que esto no dice"), ("s12", "Cómo reproducirlo")]

DESC = ("Lo que vio un juez determinista en dos conversores HL7 v2 a FHIR de código abierto: cada discrepancia con su cita, su par "
        "de mensajes mínimos y lo que no dice, y cómo pasar tu propio conversor por el mismo juez.")

ESTILO_PROPIO = """
  main { counter-reset: seccion; }
  .numerada { counter-increment: seccion; }
  .numerada h2 .num::before { content: counter(seccion, decimal-leading-zero); }
  .salto { position: absolute; left: -999px; top: .5rem; background: var(--surface); padding: .4rem .8rem; font-family: var(--sans); }
  .salto:focus { left: .5rem; }
  .volver { display: inline-block; margin-bottom: 1.4rem; font-family: var(--sans); font-size: .8125rem; }
  .indice ol { columns: 2; list-style: none; font-family: var(--sans); font-size: .875rem; margin: 0 0 3rem; padding-left: 0; }
  #f-ms:checked ~ .lista .cuenta, #f-lfh:checked ~ .lista .cuenta { display: none; }
  .limites .versiones { list-style: disc; padding-left: 1.2rem; margin: .4rem 0 0; }
  .limites .versiones li { border: 0; padding: .2rem 0; }
  .limites .versiones li::before { content: none; }
  .indice li { margin-bottom: .2rem; }
  :focus-visible { outline: 2px solid var(--accent); outline-offset: 2px; }
  .pasos li { margin-bottom: .45rem; }
  .filtro-in { position: absolute; opacity: 0; width: 1px; height: 1px; }
  .filtro { display: flex; flex-wrap: wrap; gap: .5rem; margin: 0 0 1.2rem; font-family: var(--sans); font-size: .875rem; }
  .filtro label { border: 1px solid var(--rule-firm); padding: .3rem .75rem; cursor: pointer; background: var(--surface); }
  #f-todos:checked ~ .filtro label[for="f-todos"], #f-ms:checked ~ .filtro label[for="f-ms"],
  #f-lfh:checked ~ .filtro label[for="f-lfh"] { background: var(--accent-w); border-color: var(--accent); color: var(--ink); }
  #f-todos:focus-visible ~ .filtro label[for="f-todos"], #f-ms:focus-visible ~ .filtro label[for="f-ms"],
  #f-lfh:focus-visible ~ .filtro label[for="f-lfh"] { outline: 2px solid var(--accent); outline-offset: 2px; }
  #f-ms:checked ~ .lista .disc:not([data-conv="microsoft"]),
  #f-lfh:checked ~ .lista .disc:not([data-conv="linuxforhealth"]) { display: none; }
  .disc { border-top: 1px solid var(--rule); padding-block: 1.1rem; scroll-margin-top: 1rem; }
  .disc:target { outline: 2px solid var(--accent); outline-offset: 4px; }
  .disc h4 { font-family: var(--sans); font-size: 1.05rem; margin: .3rem 0 .6rem; }
  .disc-cab { font-family: var(--mono); font-size: .75rem; color: var(--ink-soft); margin: 0; }
  .fuerza { text-transform: uppercase; letter-spacing: .06em; }
  .fuerza-fuerte { color: var(--warn); } .fuerza-media { color: var(--accent); } .fuerza-debil { color: var(--ink-faint); }
  details summary { cursor: pointer; font-family: var(--sans); font-size: .875rem; color: var(--accent); }
  details[open] summary { margin-bottom: .8rem; }
  .registro dt { font-family: var(--sans); font-weight: 600; font-size: .85rem; margin-top: .6rem; }
  .registro dd { margin: .15rem 0 0; font-size: .95rem; }
  .rot { font-family: var(--mono); font-size: .68rem; letter-spacing: .1em; text-transform: uppercase; color: var(--ink-soft);
         margin: 1rem 0 .3rem; }
  .par { display: grid; grid-template-columns: minmax(0, 1fr) minmax(0, 1fr); gap: .8rem; }
  .par > div { min-width: 0; }
  .par pre { font-size: .72rem; white-space: pre; overflow-x: auto; margin: 0; }
  mark { background: var(--warn-w); color: var(--ink); box-shadow: inset 0 -2px var(--warn); }
  .ver, .juez { font-size: .92rem; margin: .5rem 0 0; }
  .juez q { font-family: var(--mono); font-size: .8rem; }
  caption { text-align: left; font-family: var(--sans); font-size: .8125rem; color: var(--ink-soft); padding-bottom: .5rem; }
  .caja { font-size: .9rem; }
  .pie-repo { font-family: var(--sans); font-size: .8125rem; color: var(--ink-faint); max-width: 40em; margin: 1rem auto 0; padding-inline: 20px; }
  @media (max-width: 720px) { .par { grid-template-columns: minmax(0, 1fr); } .indice ol { columns: 1; } }
  @media print { .salto, .indice, .filtro, .filtro-in { display: none; } }
"""


def estilo_base():
    t = leer("docs/index.html")
    return re.findall(r"<style>(.*?)</style>", t, re.S)[1]


def pagina():
    cuerpo = "\n".join([resumen(), s01(), s02(), s03(), s04(), s05(), s06(), s07(), s08(), s09(), s10(), s11(), s12()])
    return """<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="description" content="%(desc)s">
<meta name="color-scheme" content="light dark">
<link rel="canonical" href="%(sitio)s">
<meta property="og:type" content="article">
<meta property="og:title" content="Lo que vio un juez en dos conversores">
<meta property="og:description" content="%(desc)s">
<meta property="og:url" content="%(sitio)s">
<meta name="twitter:card" content="summary">
<title>Lo que vio un juez en dos conversores</title>
<link rel="stylesheet" href="../fonts/fuentes.css">
<style>
  *, *::before, *::after { box-sizing: border-box; }
  html { color-scheme: light dark; -webkit-text-size-adjust: 100%%; }
  body { margin: 0; }
  [hidden] { display: none !important; }
%(base)s
%(propio)s</style>
</head>
<body>
<a class="salto" href="#contenido">Saltar al contenido</a>
<div class="wrap">
<a class="volver" href="../">← La primera página: el agente que no hacía falta</a>
%(cabecera)s
%(indice)s
<main id="contenido">
%(cuerpo)s
</main>
<footer>En este repositorio no hay datos de ningún paciente: los mensajes son sintéticos o ejemplos del propio estándar. El
verificador no es una herramienta de conformidad certificada. El código va bajo MIT y los documentos bajo CC BY 4.0. HL7® y
FHIR® son marcas registradas de Health Level Seven International. Este laboratorio no tiene relación con los proyectos
juzgados.</footer>
</div>
<p class="pie-repo">El código del juez, los documentos del estudio, el guion que escribe esta página y las guardas que la
comprueban están en <a href="https://github.com/LK-Corporation/lab-integraciones">github.com/LK-Corporation/lab-integraciones</a>.</p>
</body>
</html>
""" % {"desc": esc(DESC), "sitio": SITIO, "base": estilo_base(), "propio": ESTILO_PROPIO, "cabecera": cabecera(),
       "indice": indice(SECCIONES), "cuerpo": cuerpo}


def main(argv):
    try:
        nueva = pagina()
    except FuenteRota as e:
        print("una fuente no resuelve: %s" % e)
        return 2
    if argv[:1] == ["--comprobar"]:
        ruta = Path(argv[1]) if len(argv) > 1 else SALIDA
        vieja = ruta.read_text(encoding="utf-8") if ruta.is_file() else ""
        if vieja == nueva:
            print("IGUAL")
            return 0
        d = next(difflib.unified_diff(vieja.splitlines(), nueva.splitlines(), lineterm="", n=0), None)
        print("DISTINTA: %s" % next((l for l in difflib.unified_diff(vieja.splitlines(), nueva.splitlines(), lineterm="", n=0)
                                     if l.startswith(("-", "+")) and not l.startswith(("---", "+++"))), d))
        return 1
    SALIDA.parent.mkdir(parents=True, exist_ok=True)
    with open(SALIDA, "w", encoding="utf-8", newline="\n") as g:
        g.write(nueva)
    print("escrita %s (%d bytes, %d fuentes)" % (SALIDA.relative_to(REPO), len(nueva.encode("utf-8")), nueva.count("data-fuente=")))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
