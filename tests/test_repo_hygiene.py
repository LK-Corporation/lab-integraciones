"""Guardas de higiene del repositorio público.

Este repositorio es una selección de otro, privado, que lleva dentro la clave del banco. Cada test de aquí codifica
algo que se midió mal una vez: una ruta de una máquina concreta, una huella que el README decía citada y no lo estaba,
un fichero sellado que el .gitignore no cubría, una cifra que no cuadraba con la carpeta. Son baratos, no necesitan
red ni Docker, y fallan en voz alta en vez de dejar que el mismo defecto vuelva a entrar.

    python -m pytest tests          # o, sin pytest:  python tests/test_repo_hygiene.py

La adaptación parte de tests/test_repo_hygiene.py de intersystems-community/iris-ai-examples. Lo que no puede
comprobarse desde aquí sin revelar lo que protege (los nombres de operador no publicados, las máquinas, las claves)
vive en una guarda del repositorio privado que se corre antes de cada publicación.
"""

import hashlib
import os
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
AQUI = Path(__file__).resolve()

SUFIJOS_TEXTO = {".py", ".md", ".txt", ".cls", ".html", ".css", ".yml", ".yaml", ".ini", ".sha256"}
SELLO = REPO / "preinscripciones" / "SELLO-RESERVADO.txt"
HUELLAS = REPO / "preinscripciones" / "HUELLAS.sha256"

# Raíces de ruta absoluta que no nombran una máquina: las del sistema y los caminos de una API HTTP.
RAICES_NEUTRAS = {"tmp", "usr", "etc", "dev", "proc", "var", "opt", "sys", "bin", "api"}

# Hallazgos conocidos dentro de ficheros sellados, que no se pueden editar sin romper su huella. La excepción solo vale
# mientras el fichero siga verificando: si alguien lo toca, cae la excepción y aflora el hallazgo.
EXCEPCIONES_SELLADAS = {
    ("codigo/arnes/Lab.Fase12.AgenteB.cls", "172.19.0.1"),
    ("codigo/arnes/Lab.Fase12.AgenteB.cls", "docker inspect iris-ai"),
}

# Orígenes externos que la página puede cargar. Vacío desde que las fuentes se autoalojan (30-sep-2026).
ORIGENES_PERMITIDOS = set()

RAIZ_ADMITIDA = {"README.md", "INFORME.md", "LICENSE.md", ".gitignore", "pytest.ini", "LICENSES", "diseno",
                 "encargos-y-revisiones", "preinscripciones", "medidas", "codigo", "docs", "tests", ".github"}
SUFIJOS_ADMITIDOS = SUFIJOS_TEXTO | {".woff2", ""}
TAMANO_MAXIMO = 512 * 1024


# --- infraestructura ------------------------------------------------------------------------------------------------

def git(*args):
    return subprocess.run(["git", *args], cwd=REPO, capture_output=True, text=True, check=True).stdout


def rastreados():
    return [p for p in git("ls-files", "-z").split("\0") if p]


def ficheros_texto():
    for rel in rastreados():
        ruta = REPO / rel
        if ruta.resolve() == AQUI:          # el fichero cita lo que prohíbe: se suspendería a sí mismo
            continue
        if (ruta.suffix in SUFIJOS_TEXTO or ruta.name == ".gitignore") and ruta.is_file():
            yield rel


def leer(rel):
    return (REPO / rel).read_text(encoding="utf-8", errors="replace")


def sha256(rel):
    return hashlib.sha256((REPO / rel).read_bytes()).hexdigest()


def sello():
    """{nombre en el sello: huella}, y la línea CONJUNTA."""
    filas, conjunta = {}, None
    for linea in SELLO.read_text(encoding="utf-8").splitlines():
        partes = linea.split()
        if len(partes) == 2 and partes[0] == "CONJUNTA":
            conjunta = partes[1]
        elif len(partes) == 2:
            filas[partes[1]] = partes[0]
    return filas, conjunta


def ruta_publica(nombre):
    """Dónde estaría, en este repositorio, un fichero que el sello nombra con su ruta del repositorio privado."""
    for candidato in (nombre, "codigo/" + nombre, "preinscripciones/" + nombre):
        if (REPO / candidato).is_file() and candidato in set(rastreados()):
            return candidato
    return None


def sellados_que_verifican():
    filas, _ = sello()
    return {ruta_publica(n) for n, h in filas.items() if ruta_publica(n) and sha256(ruta_publica(n)) == h}


def coincidencias(patron, flags=0, quitar_urls=False):
    rx = re.compile(patron, flags)
    buenos = sellados_que_verifican()
    fallos = []
    for rel in ficheros_texto():
        for n, linea in enumerate(leer(rel).splitlines(), 1):
            texto = re.sub(r"https?://\S+", " ", linea) if quitar_urls else linea
            for m in rx.finditer(texto):
                if rel in buenos and any(rel == f and e in linea for f, e in EXCEPCIONES_SELLADAS):
                    continue
                fallos.append("%s:%d: %s" % (rel, n, m.group(0)))
    return fallos


# --- los tests ------------------------------------------------------------------------------------------------------

def test_el_test_se_excluye_a_si_mismo():
    """El modelo lo midió: el fichero que cita las cadenas prohibidas se suspende a sí mismo al trackearse."""
    assert str(AQUI.relative_to(REPO)).replace(os.sep, "/") not in set(ficheros_texto())


def test_ninguna_ruta_absoluta_de_maquina():
    """Una ruta de una máquina concreta no le sirve al lector y describe la máquina del autor.
    Medido: medidas/VIA-D-RESULTADO.md citaba la carpeta del validador en el servidor."""
    # tras una comilla invertida de cierre es prosa («`AA`/recurso/no-recurso»), no una ruta
    fallos = [f for f in coincidencias(r"(?<![\w.:/~-])(?<!\w`)/([a-z_][\w.-]*)/[\w.-]+", quitar_urls=True)
              if re.search(r": /([a-z_][\w.-]*)/", f).group(1) not in RAICES_NEUTRAS]
    fallos += [f for f in coincidencias(r"~/(?!\.config/)[\w.-]+")]
    assert not fallos, fallos


def test_ningun_host_ni_ip_de_la_red_propia():
    """Se buscan clases, no nombres: escribir aquí los nombres de las máquinas sería publicarlos.
    La lista exacta vive en la guarda privada."""
    patron = (r"\b[\w-]+\.ts\.net\b|\b[\w-]+\.(local|lan|internal)\b"
              r"|\b100\.(6[4-9]|[7-9]\d|1[01]\d|12[0-7])\.\d+\.\d+\b"
              r"|\b10\.\d+\.\d+\.\d+\b|\b192\.168\.\d+\.\d+\b|\b172\.(1[6-9]|2\d|3[01])\.\d+\.\d+\b"
              r"|\bssh\s+(-\S+\s+)*[a-z][\w-]*\b(?!\s*=)|\b[\w-]+@[\w-]+:/"
              r"|\bdocker\s+(inspect|exec|logs)\s+[\w-]+")
    assert not coincidencias(patron), coincidencias(patron)


def test_ningun_correo():
    """Hoy protege la configuración de GitHub, no el repositorio: un commit desde otra máquina con el user.email real
    la rompe sin aviso."""
    fallos = coincidencias(r"[\w.+-]+@[\w-]+(\.[\w-]+)*\.[a-z]{2,}\b", re.I)
    correos = {c for c in git("log", "--format=%ae%n%ce").split() if c}
    fallos += sorted(c for c in correos if not c.endswith("@users.noreply.github.com"))
    assert not fallos, fallos


def test_ningun_secreto_con_forma_de_secreto():
    """El repositorio de trabajo nunca tuvo un secreto dentro, pero su .gitignore tampoco lo habría impedido."""
    patron = (r"sk-(or-v1-|ant-)?[\w-]{16,}|\bghp_\w{20,}|github_pat_\w{20,}|\bAKIA[0-9A-Z]{16}\b|\bxox[abp]-[\w-]+"
              r"|BEGIN [A-Z ]*PRIVATE KEY|Bearer [\w.-]{20,}"
              r"|(api_?key|password|contrase(ñ|n)a|token)\s*[:=]\s*[\"'](?!ollama|\$|<)[^\"']{12,}[\"']")
    assert not coincidencias(patron, re.I), coincidencias(patron, re.I)


def test_lo_que_el_gitignore_promete_no_esta_rastreado():
    """Un git add -f, o un patrón añadido después de rastrear el fichero, lo dejan dentro con la promesa al lado."""
    dentro = [p for p in git("ls-files", "-i", "-c", "--exclude-standard", "-z").split("\0") if p]
    assert not dentro, dentro


def test_todo_lo_sellado_y_no_publicado_esta_en_la_red():
    """Medido: seis ficheros que el sello nombra no estaban publicados ni cubiertos por el .gitignore.
    Sus nombres ya son públicos en el sello; lo que no puede salir es su contenido."""
    filas, _ = sello()
    sin_red = []
    for nombre in filas:
        if ruta_publica(nombre):
            continue
        # con su ruta del repositorio privado y suelto en cualquier carpeta: las dos formas de colarlo
        for candidato in (nombre, "codigo/" + os.path.basename(nombre)):
            if subprocess.run(["git", "check-ignore", "-q", "--no-index", candidato], cwd=REPO).returncode != 0:
                sin_red.append(candidato)
    assert not sin_red, sin_red


def test_las_copias_selladas_son_verbatim():
    """Un documento sellado vale porque su huella verifica; «anonimizarlo» lo dejaría sin valor."""
    filas, _ = sello()
    mal = [n for n, h in filas.items() if ruta_publica(n) and sha256(ruta_publica(n)) != h]
    assert not mal, mal
    assert len([n for n in filas if ruta_publica(n)]) >= 6        # medido el 30-sep: 6 de los 20 están publicados


def test_la_conjunta_del_sello_verifica():
    """Reordenar, recortar o retocar el sello sería indetectable sin esto. La fórmula es la de sellar_reservado.py."""
    lineas = [l for l in SELLO.read_text(encoding="utf-8").splitlines() if l and not l.startswith("CONJUNTA")]
    _, conjunta = sello()
    assert len(lineas) == 20
    assert hashlib.sha256("\n".join(lineas).encode("utf-8")).hexdigest() == conjunta


def test_cada_documento_sellado_tiene_su_huella_citada_fuera():
    """El README afirmaba que las huellas estaban citadas; para PRE-POLARIDAD.md y SELLO-RESERVADO.txt no lo estaban.
    Cada documento sellado tiene su huella (completa o un prefijo de 8 o más) en otro fichero, en la misma línea que
    su nombre; y todo prefijo pegado a un nombre de documento sellado es de verdad su huella."""
    docs = sorted(p for p in rastreados() if re.match(r"preinscripciones/(PRE-.*\.md|SELLO-RESERVADO\.txt)$", p))
    assert len(docs) == 5, docs
    sin_cita, mal_citados = [], []
    for doc in docs:
        nombre, huella = os.path.basename(doc), sha256(doc)
        citado = False
        for rel in ficheros_texto():
            if rel == doc:
                continue
            for linea in leer(rel).splitlines():
                if nombre not in linea:
                    continue
                for hx in re.findall(r"\b[0-9a-f]{8,64}\b", linea):
                    if not re.search(r"[a-f]", hx) and not re.search(r"\d", hx):
                        continue
                    if len(re.findall(r"PRE-[\w-]+\.md|SELLO-RESERVADO\.txt", linea)) > 1:
                        continue        # una línea que nombra varios documentos no ata cada prefijo a uno
                    if huella.startswith(hx):
                        citado = True
                    elif re.search(r"[0-9a-f]{8}", hx) and rel != "preinscripciones/SELLO-RESERVADO.txt":
                        mal_citados.append("%s: %s junto a %s" % (rel, hx, nombre))
        if not citado:
            sin_cita.append(doc)
    assert not sin_cita, sin_cita
    assert not mal_citados, mal_citados


def test_las_huellas_publicadas_verifican():
    """HUELLAS.sha256 es el testigo público desde el 30-sep-2026: comprobable con `sha256sum -c`."""
    filas = [l.split() for l in HUELLAS.read_text(encoding="utf-8").splitlines() if l and not l.startswith("#")]
    assert len(filas) == 5
    mal = [f for h, f in filas if sha256("preinscripciones/" + f) != h]
    assert not mal, mal


def test_los_enlaces_relativos_resuelven():
    """El último commit antes de esta guarda fue justamente «arreglado el enlace vacío»."""
    rotos = []
    for rel in ficheros_texto():
        if not rel.endswith((".md", ".html")):
            continue
        for a, b in re.findall(r"\]\(([^)\s]+)\)|(?:href|src)=\"([^\"]+)\"", leer(rel)):
            destino = (a or b).split("#")[0]
            if not destino or re.match(r"[a-z]+:", destino):
                continue
            if not (REPO / os.path.dirname(rel) / destino).exists():
                rotos.append("%s -> %s" % (rel, destino))
    assert not rotos, rotos


def test_todo_documento_es_alcanzable_desde_el_readme():
    """Ningún documento enlaza a otro: si se añade uno sin tocar el README, solo `git ls-files` lo encuentra.
    Un enlace a una carpeta alcanza todo lo que hay debajo (GitHub muestra el listado)."""
    todos = set(rastreados())
    alcanzados, pendientes = set(), ["README.md"]
    while pendientes:
        rel = pendientes.pop()
        if rel in alcanzados:
            continue
        alcanzados.add(rel)
        if not rel.endswith(".md"):
            continue
        for destino in re.findall(r"\]\(([^)\s#]+)", leer(rel)):
            if re.match(r"[a-z]+:", destino):
                continue
            ruta = os.path.normpath(os.path.join(os.path.dirname(rel), destino)).replace(os.sep, "/")
            if destino.endswith("/"):
                pendientes += [p for p in todos if p.startswith(ruta + "/")]
            elif ruta in todos:
                pendientes.append(ruta)
    sueltos = sorted(p for p in todos - alcanzados if p.endswith((".md", ".txt")))
    assert not sueltos, sueltos


def test_las_cabeceras_de_procedencia_apuntan_a_un_encargo_publicado():
    """LICENSE.md promete que la cabecera de cada revisión permite comprobar la procedencia.
    Medido: revision-quehacer-gpt.md citaba un encargo que no estaba publicado. Un encargo que no se puede publicar
    (nombra operadores del catálogo) se declara en la cabecera, y entonces no puede estar."""
    mal = []
    for rel in rastreados():
        if not re.match(r"encargos-y-revisiones/revision-.*\.md$", rel):
            continue
        primera = leer(rel).splitlines()[0]
        m = re.match(r"<!-- modelo: .* · encargo: (\S+\.md)( \(no publicado: [^)]+\))? · .*tokens -->$", primera)
        if m:
            esta = (REPO / "encargos-y-revisiones" / m.group(1)).is_file()
            if esta == bool(m.group(2)):
                mal.append("%s -> %s%s" % (rel, m.group(1), " (declarado no publicado)" if m.group(2) else ""))
        elif not primera.startswith("# "):
            mal.append("%s: sin cabecera" % rel)
    assert not mal, mal


def test_el_readme_cuenta_bien_encargos_y_revisiones():
    """Medido: el README decía «diecinueve revisiones», que era el número de ficheros de la carpeta (3 encargos y 16
    revisiones)."""
    numeros = {3: "tres", 4: "cuatro", 16: "dieciséis", 17: "diecisiete"}
    enc = len([p for p in rastreados() if re.match(r"encargos-y-revisiones/encargo_.*\.md$", p)])
    rev = len([p for p in rastreados() if re.match(r"encargos-y-revisiones/revision-.*\.md$", p)])
    fila = [l for l in leer("README.md").splitlines() if "(encargos-y-revisiones/)" in l][0]
    assert "%s encargos" % numeros.get(enc, enc) in fila and "%s revisiones" % numeros.get(rev, rev) in fila, fila


def test_las_licencias_cubren_todo_fichero_rastreado():
    """Medido: docs/index.html no caía en ninguna fila de LICENSE.md."""
    lic = leer("LICENSE.md")
    assert "MIT License" in leer("LICENSES/MIT.txt") and "Copyright (c) 2026 LK-Corporation" in leer("LICENSES/MIT.txt")
    assert "CC-BY-4.0" in leer("LICENSES/CC-BY-4.0.md")
    sin = []
    for rel in rastreados():
        ruta = Path(rel)
        clave = ruta.suffix or ruta.name
        carpetas = ["`%s/`" % "/".join(ruta.parts[:i]) for i in range(1, len(ruta.parts))]
        if "`%s`" % clave not in lic and not any(c in lic for c in carpetas):
            sin.append(rel)
    assert not sin, sin


def test_la_pagina_no_carga_nada_externo():
    """Cada recurso externo le cuenta a un tercero quién lee la página. Las fuentes se autoalojan desde el 30-sep."""
    fallos = []
    for rel in rastreados():
        if not rel.startswith("docs/") or not rel.endswith((".html", ".css")):
            continue
        texto = leer(rel)
        if "<script" in texto.lower():
            fallos.append("%s: <script>" % rel)
        cargas = [u for tipo, u in re.findall(r"<link\b[^>]*?rel=\"([^\"]+)\"[^>]*?href=\"(https?://[^\"]+)\"", texto)
                  if re.search(r"stylesheet|preload|prefetch|preconnect|icon|manifest", tipo)]   # canonical no carga
        cargas += re.findall(r"<(?:img|iframe|source|video|audio|embed)\b[^>]*?src=\"(https?://[^\"]+)\"", texto)
        cargas += re.findall(r"url\(\s*['\"]?(https?://[^)'\"]+)", texto) + re.findall(r"@import\s+['\"](https?://[^'\"]+)", texto)
        fallos += ["%s: %s" % (rel, u) for u in cargas if re.match(r"https?://([^/]+)", u).group(1) not in ORIGENES_PERMITIDOS]
    assert not fallos, fallos


def test_la_pagina_y_el_informe_dicen_las_mismas_cifras():
    """docs/index.html es un derivado manual del informe: una corrección en INFORME.md no se propaga sola. La página
    resume y no lleva todas las cifras, pero toda cifra de resultado que da tiene que estar en el informe."""
    informe = {c.replace("−", "-") for c in re.findall(r"[+−-]0,\d{3}", leer("INFORME.md"))}
    pagina = {c.replace("−", "-") for c in re.findall(r"[+−-]0,\d{3}", leer("docs/index.html"))}
    assert pagina and not pagina - informe, sorted(pagina - informe)


def test_solo_entra_lo_que_la_seleccion_admite():
    """La clave del banco vive en .tsv y .json; el .gitignore filtra por nombre y esto por tipo y lugar."""
    fuera = []
    for rel in rastreados():
        ruta = Path(rel)
        if ruta.parts[0] not in RAIZ_ADMITIDA:
            fuera.append(rel + " (lugar)")
        elif ruta.suffix not in SUFIJOS_ADMITIDOS or (ruta.suffix == "" and ruta.name not in (".gitignore",)):
            fuera.append(rel + " (tipo)")
        elif (REPO / rel).stat().st_size > TAMANO_MAXIMO:
            fuera.append(rel + " (tamaño)")
        elif ruta.suffix == ".woff2" and not rel.startswith("docs/fonts/"):
            fuera.append(rel + " (fuente fuera de docs/fonts/)")
    assert not fuera, fuera


if __name__ == "__main__":
    fallos = 0
    for nombre, prueba in sorted((n, f) for n, f in globals().items() if n.startswith("test_")):
        try:
            prueba()
            print("  ok     %s" % nombre)
        except Exception as e:
            fallos += 1
            print("  FALLA  %s: %s" % (nombre, str(e)[:600]))
    print("HIGIENE: %s" % ("TODO BIEN" if not fallos else "%d FALLAN" % fallos))
    sys.exit(1 if fallos else 0)
