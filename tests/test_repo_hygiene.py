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
import html.parser
import importlib.util
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
AQUI = Path(__file__).resolve()

SUFIJOS_TEXTO = {".py", ".md", ".txt", ".cls", ".html", ".css", ".yml", ".yaml", ".ini", ".sha256",
                 ".java", ".gradle", ".xml",                    # 24-oct-2026: el arnés de LinuxForHealth del estudio de conversores
                 ".sh"}                                         # 25-oct-2026: el guion que trae LinuxForHealth en la integración continua
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

# El verificador (22-oct-2026) se publica tal como se preparó, con la huella de cada fichero en su MANIFIESTO.txt; varios entran
# en la huella del juez y no se pueden tocar. Estos hallazgos son valores de prueba o genéricos, no la red ni el correo del autor.
# Como en las selladas, la excepción solo vale mientras el fichero siga coincidiendo con su línea del manifiesto.
MANIFIESTO = REPO / "verificador" / "MANIFIESTO.txt"
EXCEPCIONES_MANIFIESTO = {
    ("verificador/mcp_verificador.py", "100.64.0.0"),               # el rango CGNAT (RFC 6598) que admite su servidor HTTP
    ("verificador/prueba_mcp_verificador.py", "100.64.0.0"),
    ("verificador/prueba_mcp_verificador.py", "192.168.1.10"),      # una dirección de LAN que P74 espera ver rechazada
    ("verificador/prueba_verificador.py", "172.19.0.1"),            # una línea de registro de IRIS, la misma que el arnés
    ("verificador/prueba_verificador.py", "7@EnsLib.HL7.Message"),  # una referencia a objeto de IRIS, no un correo
    ("verificador/mapeador_adt.py", "a@b.es"),                      # el correo sintético de sus autopruebas
    ("verificador/a1/bases_a1.json", "ana@hosp.es"),                # el de la paciente ficticia de las bases A1
    ("piloto-agente/bucle/diseno-bucle-fable.md", "ssh caído"),     # prosa, no una orden
    ("verificador/cv/correr_conversor.py", "/app/Microsoft"),       # rutas de dentro del contenedor del arnés
    ("verificador/cv/adaptadores/microsoft.json", "/app/Microsoft"),   # rutas de dentro del contenedor
    ("verificador/cv/prueba_vc.py", "/app/Microsoft"),
    ("verificador/cv/prueba_vc.py", "/in/a.hl7"),
    ("verificador/cv/vc/juguete-docker.json", "/juguete/conversor_juguete.py"),
    ("verificador/cv/vc/diseno-vc-fable.md", "/app/Microsoft"),
    ("verificador/cv/vc/diseno-vc-fable.md", "/juguete/conversor_juguete.py"),
    ("verificador/cv/vc/ejemplos/INFORME-linuxforhealth.json", "ana@hosp.es"),  # la paciente ficticia de A1
    ("verificador/cv/vc/ejemplos/INFORME-linuxforhealth.md", "ana@hosp.es"),
    ("verificador/cv/lfh/copiar-libs.gradle", "/salida/lib"),
    ("verificador/cv/ar/CONTROL-AR.json", "Arnes /in /salida /in/A01-001.hl7"),   # la orden de la caja: rutas de dentro
    ("verificador/cv/ar/control_ar.py", "Arnes /in /salida /in/A01-001.hl7"),
    ("verificador/cv/ar/decisiones-qar.md", "Arnes /in /salida /in/A01-001.hl7"),
    ("verificador/cv/ar/diseno-ar-fable.md", '"/in/a.hl7"'),
    ("verificador/cv/adaptadores/microsoft-main.json", "/app/Microsoft"),   # etapa 22: rutas de dentro del contenedor
    ("verificador/vx/rv/diseno-rv-fable.md", "/app/Microsoft"),
    ("verificador/vx/rv/diseno-rv-fable.md", '"/in/a.hl7"'),
    ("verificador/vx/rv/diseno-rv-fable.md", "evidencias/<id>/propio/2-L11b.json"),
    ("verificador/vx/rv/diseno-rv-fable.md", "<S>/fijada/"),
    ("verificador/vx/rv/diseno-rv-fable.md", "-o /src/out"),
    ("verificador/vx/rv/diseno-rv-fable.md", "<W>/ms/out"),
    ("verificador/vx/rv/diseno-rv-fable.md", "/salida/lib"),
    ("verificador/cv/ci/preparar_lfh.sh", "/w/pom.xml"),            # etapa 23: rutas de dentro del contenedor
    ("verificador/cv/ci/preparar_lfh.sh", "javac --release 11 -d /w/lfh/clases"),
    ("verificador/cv/ci/preparar_lfh.sh", "<artefactos>/lfh/"),     # y rutas bajo un marcador
    ("verificador/cv/ci/diseno-ci-fable.md", "/w/pom.xml"),
    ("verificador/cv/ci/diseno-ci-fable.md", "javac --release 11 -d /w/lfh/clases"),
    ("verificador/cv/ci/diseno-ci-fable.md", "<artefactos>/lfh/"),
    ("verificador/cv/ci/diseno-ci-fable.md", "cmp <S>/lfh-1/INFORME.json"),
    ("verificador/cv/ci/diseno-ci-fable.md", "<tu repo>/ci/LINEA-BASE.json"),
    ("verificador/cv/ci/diseno-ci-fable.md", "ni `docker inspect X`, ni `ssh x`"),   # describe la regla de la higiene
    ("verificador/cv/ci/CI.md", "<tu repo>/ci/LINEA-BASE.json"),
}
# La clave del banco vive en .json: del verificador se admiten por nombre, no por tipo.
JSON_ADMITIDOS = {"verificador/cv/pg/preguntas_qpg.json", "verificador/cv/adaptadores/microsoft.json", "verificador/cv/adaptadores/linuxforhealth.json",
                  "verificador/cv/adaptadores/juguete.json", "verificador/cv/vc/juguete-docker.json",
                  "verificador/cv/vc/preguntas_qvc.json", "verificador/cv/vc/ejemplos/INFORME-microsoft.json",
                  "verificador/cv/vc/ejemplos/INFORME-linuxforhealth.json",
                  "verificador/estructuras_25.json", "verificador/a1/ejemplos_cap3.json", "verificador/a1/bases_a1.json",
                  "verificador/bases_adt/bases_e2.json", "verificador/ve/PREVISION-VE2.json",
                  "verificador/ve/ADJUDICACION-VE2.json", "verificador/ve/TABLA-VE2.json",
                  # 24-oct-2026, el estudio de conversores: la previsión sellada y los agregados
                  "verificador/cv/PREVISION-CV2.json", "verificador/cv/CUENTAS-CV2.json", "verificador/cv/RESULTADO-CV2.json",
                  "verificador/cv/ADJUDICACION-CV2.json", "verificador/cv/CLASES-CV3.json",
                  "verificador/cv/RESULTADO-CV3-minimos.json", "verificador/cv/RESULTADO-15A-minimos-main.json",
                  # 25-oct-2026, la etapa de VXU: las preguntas a Jev, la previsión sellada, las clases y los pares
                  "verificador/vx/preguntas_qvx.json", "verificador/vx/prevision-vxu.json", "verificador/vx/CLASES-VX3.json",
                  "verificador/vx/RESULTADO-VX3-minimos.json",
                  # 25-oct-2026, el arrastre de estado: el adaptador mensaje, las preguntas a Jev, la previsión y los resultados
                  "verificador/cv/adaptadores/linuxforhealth-mensaje.json", "verificador/cv/ar/preguntas_qar.json",
                  "verificador/cv/ar/preguntas_prevision_ar.json", "verificador/cv/ar/PREVISION-AR.json",
                  "verificador/cv/ar/POSITIVO-AR.json", "verificador/cv/ar/RUIDO-AR.json", "verificador/cv/ar/COMPARACION-AR.json",
                  "verificador/cv/ar/ADJUDICACION-AR.json", "verificador/cv/ar/CIFRAS-AR.json", "verificador/cv/ar/CONTROL-AR.json",
                  "verificador/cv/ar/CLASES-AR-lote.json", "verificador/cv/ar/CLASES-AR-mensaje.json",
                  "verificador/cv/ar/minimos-AR-lote.json", "verificador/cv/ar/minimos-AR-mensaje.json",
                  "verificador/cv/ar/prevision-cuerpo.json", "verificador/cv/ar/COMPARACION-AR-primer-paso9.json",
                  # 25-oct-2026, las nueve de VXU en las ramas: los adaptadores de rama, las preguntas, la previsión y los resultados
                  "verificador/cv/adaptadores/microsoft-main.json", "verificador/cv/adaptadores/linuxforhealth-main.json",
                  "verificador/cv/adaptadores/linuxforhealth-main-mensaje.json", "verificador/vx/rv/preguntas_qrv.json",
                  "verificador/vx/rv/preguntas_prevision_rv.json", "verificador/vx/rv/prevision-cuerpo-rv.json",
                  "verificador/vx/rv/PREVISION-RV.json", "verificador/vx/rv/IDENTIDADES-RV.json", "verificador/vx/rv/CONTROL-RV.json",
                  "verificador/vx/rv/RAMAS-RV.json", "verificador/vx/rv/RESULTADO-RV-minimos-fijada-lote.json",
                  "verificador/vx/rv/RESULTADO-RV-minimos-fijada-mensaje.json", "verificador/vx/rv/RESULTADO-RV-minimos-main.json",
                  "verificador/vx/rv/SECUENCIA-RV.json", "verificador/vx/rv/ESTADO-RV.json", "verificador/vx/rv/CONTRASTE-RV.json",
                  "verificador/vx/rv/CORRIDAS-RV.json",
                  # 25-oct-2026, la integración continua: las líneas base, el positivo, las preguntas y la previsión
                  "verificador/cv/ci/LINEA-BASE-juguete.json", "verificador/cv/ci/LINEA-BASE-linuxforhealth.json",
                  "verificador/cv/ci/LINEA-BASE-linuxforhealth-mensaje.json", "verificador/cv/ci/POSITIVO-CI.json",
                  "verificador/cv/ci/preguntas_qci.json", "verificador/cv/ci/preguntas_prevision_ci.json",
                  "verificador/cv/ci/prevision-cuerpo-ci.json", "verificador/cv/ci/PREVISION-CI.json",
                  "verificador/cv/ci/CORRIDA-CI-1.json", "verificador/cv/ci/CORRIDA-CI-2.json"}   # las corridas en GitHub Actions

# Orígenes externos que la página puede cargar. Vacío desde que las fuentes se autoalojan (30-sep-2026).
ORIGENES_PERMITIDOS = set()

RAIZ_ADMITIDA = {"README.md", "INFORME.md", "ARTICULO.md", "LICENSE.md", ".gitignore", "pytest.ini", "LICENSES", "diseno",
                 "encargos-y-revisiones", "preinscripciones", "medidas", "codigo", "docs", "tests", ".github", "piloto-agente",
                 "verificador"}
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
        if (ruta.suffix in SUFIJOS_TEXTO or ruta.name == ".gitignore" or rel in JSON_ADMITIDOS) and ruta.is_file():
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


def del_manifiesto():
    """Las rutas que hoy coinciden con su línea de verificador/MANIFIESTO.txt («huella  ruta»; «#» abre un comentario)."""
    if not MANIFIESTO.is_file():
        return set()
    filas = dict(reversed(l.split()) for l in MANIFIESTO.read_text(encoding="utf-8").splitlines()
                 if len(l.split()) == 2 and not l.startswith("#"))
    return {r for r, h in filas.items() if (REPO / r).is_file() and sha256(r) == h}


def coincidencias(patron, flags=0, quitar_urls=False):
    rx = re.compile(patron, flags)
    buenos, manifiesto = sellados_que_verifican(), del_manifiesto()
    fallos = []
    for rel in ficheros_texto():
        for n, linea in enumerate(leer(rel).splitlines(), 1):
            texto = re.sub(r"https?://\S+", " ", linea) if quitar_urls else linea
            for m in rx.finditer(texto):
                if rel in buenos and any(rel == f and e in linea for f, e in EXCEPCIONES_SELLADAS):
                    continue
                if rel in manifiesto and any(rel == f and e in linea for f, e in EXCEPCIONES_MANIFIESTO):
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
        texto = re.sub(r"(?ms)^```.*?^```", "", leer(rel)) if rel.endswith(".md") else leer(rel)   # etapa 19: un bloque
        if rel.endswith(".md"):                                                               # etapa 20: ni el código
            texto = re.sub(r"`[^`\n]*`", "", texto)                                          # en línea
        for a, b in re.findall(r"\]\(([^)\s]+)\)|(?:href|src)=\"([^\"]+)\"", texto):          # de código no enlaza
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
        if re.search(r"<[^>]*\son\w+\s*=", texto) or re.search(r"href=\"\s*javascript:", texto, re.I):
            fallos.append("%s: un atributo on…= o un enlace javascript:" % rel)   # etapa 19
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
        elif (ruta.suffix not in SUFIJOS_ADMITIDOS and rel not in JSON_ADMITIDOS) \
                or (ruta.suffix == "" and ruta.name not in (".gitignore",)):
            fuera.append(rel + " (tipo)")
        elif (REPO / rel).stat().st_size > TAMANO_MAXIMO:
            fuera.append(rel + " (tamaño)")
        elif ruta.suffix == ".woff2" and not rel.startswith("docs/fonts/"):
            fuera.append(rel + " (fuente fuera de docs/fonts/)")
    assert not fuera, fuera


# --- la página del estudio de conversores (etapa 19, pg/diseno-pg-fable.md §4-§5) ----------------------------------------
# La página la escribe un guion desde los ficheros publicados, y cada cifra, texto del juez, cita o mensaje mínimo lleva su
# fuente en `data-fuente`. Estas guardas la resuelven con su propio código, sin importar el guion, y cada una lleva su control
# negativo: una guarda que no ve un cambio hecho a propósito no vale.

PAGINA_CV = "docs/conversores/index.html"
GUION_CV = "codigo/hacer_pagina_conversores.py"
PALABRAS_NUMERO = re.compile(r"\b(tres|cuatro|cinco|seis|siete|ocho|nueve|diez|once|doce|trece|catorce|quince|diecis[eé]is|"
                             r"diecisiete|dieciocho|diecinueve|veinte|treinta|cuarenta|cincuenta|sesenta|setenta|ochenta|"
                             r"noventa|cien|ciento|mil)\b", re.I)
IDENTIFICADORES = [re.compile(p) for p in (
    r"\bHL7\b", r"\bv2(\.\d)?\b", r"\bR4\b", r"\bv2-to-FHIR\b", r"\bv3-[A-Za-z]+\b", r"\bv2-0\d{3}\b", r"\bhl70\d{3}\b",
    r"\b[A-Z][A-Z0-9]{1,2}(\(\d+\))?-\d{1,2}(\.\d{1,2})?\b", r"\b[A-Z]{2,3}\.\d{1,2}\b",
    r"\b(ADT|ORU|SIU|MDM|VXU|ORM|OML)(\^|_)[A-Z]\d{2}\b", r"\bA\d{2}\b", r"\bR01\b", r"\b0\d{3}\b",
    r"\b(Q|L|S|DV|P|MC|AMB|E)-[A-Z]{1,3}(-[A-Z]{1,3})?-\d{1,3}\b", r"\b[ML]-\d{1,2}\b", r"\b[MLR]\d{2}[a-z]?\b",
    r"#\d+\b", r"\b(?=[0-9a-f]*[a-f])[0-9a-f]{7,64}\b", r"\bCC BY 4\.0\b",
    r"\b[A-Z]{2}\d\b",                                               # nombres de segmento: PV1, GT1, NK1
    r"\bhl7v2-fhir-converter\b")]                                     # el nombre de un proyecto


class _Pagina(html.parser.HTMLParser):
    """Recorre la página: los elementos con fuente (con su texto), los `<pre class="hl7">`, el texto que queda fuera de ellos
    (sin <style>), el título, la descripción, y lo que mira la guarda de accesibilidad."""
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.con_fuente, self.abiertos, self.fuera, self.titulo, self.desc = [], [], [], [], ""
        self.pila, self.en_style, self.en_title = [], 0, False
        self.etiquetas = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        self.etiquetas.append((tag, a))
        if tag in ("meta",) and a.get("name") == "description":
            self.desc = a.get("content") or ""
        if tag in ("meta", "link", "br", "hr", "img", "input", "source", "wbr"):
            return
        if tag == "style":
            self.en_style += 1
        if tag == "title":
            self.en_title = True
        captura = "data-fuente" in a or (tag == "pre" and "hl7" in (a.get("class") or "").split())
        if captura:
            r = {"tag": tag, "attrs": a, "texto": []}
            self.con_fuente.append(r)
            self.abiertos.append(r)
        self.pila.append((tag, captura))

    def handle_endtag(self, tag):
        while self.pila:
            t, captura = self.pila.pop()
            if captura:
                self.abiertos.pop()
            if t == "style":
                self.en_style -= 1
            if t == "title":
                self.en_title = False
            if t == tag:
                break

    def handle_data(self, data):
        if self.en_style:
            return
        if self.en_title:
            self.titulo.append(data)
        for r in self.abiertos:
            r["texto"].append(data)
        if not self.abiertos and not self.en_title:
            self.fuera.append(data)


def _leer_pagina(texto):
    p = _Pagina()
    p.feed(texto)
    p.close()
    return p


def _norm(s):
    s = re.sub(r"\*\*|`", "", s or "").replace(" ", " ").replace(" ", " ").replace(" ", " ")
    for a, b in ((">=", "≥"), ("<=", "≤"), ("->", "→")):
        s = s.replace(a, b)
    return re.sub(r"\s+", " ", s).strip()


def _tabla(rel, linea, fila, columna):
    lineas = leer(rel).splitlines()
    i = next(k for k, l in enumerate(lineas) if linea in l)
    while not lineas[i].startswith("|"):
        i += 1
    celdas = lambda l: [_norm(c.replace("\\|", "|")) for c in re.split(r"(?<!\\)\|", l.strip()[1:-1])]  # noqa: E731
    cab = celdas(lineas[i])
    k = i + 2
    while k < len(lineas) and lineas[k].startswith("|"):
        c = celdas(lineas[k])
        if c[0] == _norm(fila):
            return c[cab.index(_norm(columna))]
        k += 1
    raise KeyError("no hay fila %r" % fila)


def _par_minimo(par, cual):
    spec = importlib.util.spec_from_file_location("cv3_minimos_guarda", REPO / "verificador" / "cv" / "cv3_minimos.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    for pid, _, (caso, control), _ in mod.PARES:
        if pid == par:
            return (caso if cual == "caso" else control).replace("\r", "\n").strip("\n")
    raise KeyError("no hay par %r" % par)


def _json(rel, puntero):
    v = json.loads(leer(rel))
    for paso in puntero.split("."):
        m = re.match(r"^(\w+)\[(\w+)=([^\]]+)\]$", paso)
        if m:
            v = [x for x in v[m.group(1)] if str(x.get(m.group(2))) == m.group(3)]
            if len(v) != 1:
                raise KeyError("%s: %d elementos" % (paso, len(v)))
            v = v[0]
        elif isinstance(v, list):
            v = v[int(paso)]
        else:
            v = v[paso]
    return v


def resolver_fuente(a):
    """-> el texto que la fuente dice (normalizado); KeyError/StopIteration/ValueError si no resuelve."""
    fuente, patron, grupo = a["data-fuente"], a.get("data-patron"), int(a.get("data-grupo") or 1)
    tipo, _, resto = fuente.partition(":")
    rel = resto.split("#", 1)[0]
    if tipo in ("json", "md", "tabla") and rel not in set(rastreados()):
        raise KeyError("%s no es un fichero rastreado" % rel)
    if tipo == "json":
        v = _json(rel, resto.split("#", 1)[1])
        v = ("sí" if v else "no") if isinstance(v, bool) else str(v)
    elif tipo == "md":
        if not patron:
            raise KeyError("md sin data-patron")
        v = leer(rel)
    elif tipo == "tabla":
        linea, fila, columna = resto.split("#", 1)[1].split("|")
        v = _tabla(rel, linea, fila, columna)
    elif tipo == "hl7":
        par, cual = resto.split("#")
        return _par_minimo(par, cual)
    else:
        raise KeyError("tipo de fuente desconocido: %s" % tipo)
    if patron:
        ms = list(re.finditer(patron, v, re.M))
        if len(ms) != 1:
            raise ValueError("el patrón casa %d veces (ambiguo o roto)" % len(ms))
        v = ms[0].group(grupo)
    return _norm(v)


def fallos_fuentes(texto):
    fallos = []
    for r in _leer_pagina(texto).con_fuente:
        a, visto = r["attrs"], "".join(r["texto"])
        if r["tag"] == "pre" and "hl7" in (a.get("class") or "").split() and not (a.get("data-fuente") or "").startswith("hl7:"):
            fallos.append("pre hl7 sin fuente hl7: %s" % visto[:60])
            continue
        try:
            dice = resolver_fuente(a)
        except (KeyError, ValueError, StopIteration, IndexError, TypeError) as e:
            fallos.append("%s no resuelve: %s" % (a["data-fuente"], e))
            continue
        if a["data-fuente"].startswith("hl7:"):
            ok = visto.strip("\n") == dice
        elif "**" in visto or "`" in visto:                        # _norm los quita de los dos lados: aquí se verían crudos
            fallos.append("%s: Markdown sin convertir en %r" % (a["data-fuente"], visto[:80]))
            continue
        else:
            ok = _norm(visto) == dice or _norm(visto).replace(",", ".") == dice
        if "value" in a and a["value"] != dice:
            ok = False
        if not ok:
            fallos.append("%s: la página dice %r y la fuente %r" % (a["data-fuente"], _norm(visto)[:80], dice[:80]))
    return fallos


def fallos_cifras(texto):
    p = _leer_pagina(texto)
    fallos = []
    for donde, t in (("texto", " ".join(p.fuera)), ("title", " ".join(p.titulo)), ("description", p.desc)):
        t = re.sub(r"\s+", " ", t)
        buenos = [m.span() for rx in IDENTIFICADORES for m in rx.finditer(t)]
        for m in list(re.finditer(r"\d+", t)) + list(PALABRAS_NUMERO.finditer(t)):
            if not any(a <= m.start() and m.end() <= b for a, b in buenos):
                fallos.append("%s: %r en «%s»" % (donde, m.group(0), t[max(0, m.start() - 20):m.end() + 20]))
    return fallos


def fallos_tarjetas(texto):
    """Una tarjeta por cada nueva de CLASES-CV3.json, en el orden de la tabla de RESULTADO-CV3.md, y ninguna más; y la celda
    «Rama principal» de 15A dice «sigue» si y solo si el par se confirma en la rama principal."""
    p = _leer_pagina(texto)
    vistas = [a.get("id") for t, a in p.etiquetas if t == "article" and "disc" in (a.get("class") or "").split()]
    nuevas = [c["id"] for c in json.loads(leer("verificador/cv/CLASES-CV3.json"))["clases"] if c["clase"] == "nueva"]
    lineas = leer("verificador/cv/RESULTADO-CV3.md").splitlines()
    i = next(k for k, l in enumerate(lineas) if l.startswith("## Las 15 nuevas"))
    orden = []
    for l in lineas[i:]:
        m = re.match(r"^\| ([ML]-\d+) \|", l)
        if m:
            orden.append(m.group(1))
        elif orden and not l.startswith("|"):
            break
    fallos = ["falta la tarjeta %s" % x for x in nuevas if x not in vistas]
    fallos += ["tarjeta de más: %s" % x for x in vistas if x not in nuevas or vistas.count(x) > 1]
    if not fallos and vistas != orden:
        fallos.append("orden: %s frente a %s" % (vistas, orden))
    main = {x["id"]: x["confirmada"] for x in json.loads(leer("verificador/cv/RESULTADO-15A-minimos-main.json"))["pares"]}
    clases = {c["id"]: c for c in json.loads(leer("verificador/cv/CLASES-CV3.json"))["clases"]}
    for x in nuevas:
        rama = _tabla("verificador/cv/RESULTADO-15A.md", "## Cada nueva, en la versión fijada", x, "Rama principal")
        pares = [y.strip() for y in clases[x]["par_minimo"].split("/")]
        sigue = all(main.get(y) for y in pares if y in main)
        if rama.startswith("sigue") != sigue:
            fallos.append("%s: 15A dice %r y el par en la rama principal %s" % (x, rama, sigue))
    return fallos


def fallos_accesibles(rel, texto):
    p = _leer_pagina(texto)
    f = []
    if not re.search(r'<html lang="es"', texto):
        f.append('%s: sin <html lang="es">' % rel)
    if 'name="viewport"' not in texto or "color-scheme" not in texto:
        f.append("%s: sin viewport o color-scheme" % rel)
    if sum(1 for t, _ in p.etiquetas if t == "h1") != 1:
        f.append("%s: no hay un solo <h1>" % rel)
    if len(re.findall(r"<details\b", texto)) != len(re.findall(r"<details\b[^>]*>\s*<summary\b", texto)):
        f.append("%s: un <details> sin <summary> al principio" % rel)
    for t, a in p.etiquetas:
        if t == "svg" and (a.get("role") != "img" or not a.get("aria-label")):
            f.append("%s: <svg> sin role=img o aria-label" % rel)
        if re.match(r"^[1-9]", a.get("tabindex") or ""):
            f.append("%s: tabindex positivo" % rel)
        if t == "input" and a.get("id") and not re.search(r'<label\b[^>]*for="%s"' % re.escape(a["id"]), texto):
            f.append("%s: el control %s no tiene etiqueta" % (rel, a["id"]))
    return f


def _pagina_cv():
    assert (REPO / PAGINA_CV).is_file(), "no existe %s" % PAGINA_CV
    return leer(PAGINA_CV)


def test_la_pagina_de_conversores_es_la_que_genera_su_guion():
    r = subprocess.run([sys.executable, GUION_CV, "--comprobar"], cwd=REPO, capture_output=True, text=True, timeout=300)
    assert r.returncode == 0 and "IGUAL" in r.stdout, (r.returncode, r.stdout[-400:], r.stderr[-400:])


def test_la_guarda_de_regeneracion_ve_un_cambio():
    t = _pagina_cv()
    m = re.search(r'(<span class="cifra" data-fuente="json:verificador/cv/CLASES-CV3.json#frase.N_nuevas_confirmadas">)15<', t)
    assert m, "no está el 15 de la frase"
    with tempfile.TemporaryDirectory() as d:
        otra = os.path.join(d, "index.html")
        open(otra, "w", encoding="utf-8").write(t[:m.end(1)] + "16" + t[m.end(1) + 2:])
        r = subprocess.run([sys.executable, GUION_CV, "--comprobar", otra], cwd=REPO, capture_output=True, text=True, timeout=300)
    assert r.returncode == 1 and "DISTINTA" in r.stdout, (r.returncode, r.stdout[-300:])


def test_toda_cifra_de_la_pagina_de_conversores_tiene_fuente_y_coincide():
    t = _pagina_cv()
    n = len(_leer_pagina(t).con_fuente)
    fallos = fallos_fuentes(t)
    assert n > 150 and not fallos, (n, fallos[:10])


def test_la_guarda_de_fuentes_ve_un_cambio():
    t = _pagina_cv()
    m = re.search(r'(<span class="cifra" data-fuente="json:verificador/cv/CLASES-CV3.json#frase.N_nuevas_confirmadas">)15<', t)
    assert m, "no está la cifra de la frase"
    cambio = t[:m.end(1)] + "16" + t[m.end(1) + 2:]
    assert any("frase.N_nuevas_confirmadas" in f for f in fallos_fuentes(cambio))
    crudo = t[:m.end(1)] + "**15**" + t[m.end(1) + 2:]
    assert any("Markdown sin convertir" in f for f in fallos_fuentes(crudo))
    roto = t.replace("frase.N_nuevas_confirmadas", "frase.N_inventada", 1)
    assert any("no resuelve" in f for f in fallos_fuentes(roto))
    i = t.index('<pre class="hl7"')
    j = t.index("MSH", i)
    assert any("hl7:" in f for f in fallos_fuentes(t[:j] + "XSH" + t[j + 3:]))
    k = t.index('data-patron="')
    ambiguo = t[:k] + 'data-patron="(\\d+)"' + t[t.index('"', k + len('data-patron="')) + 1:]
    assert any("casa" in f for f in fallos_fuentes(ambiguo))


def test_la_pagina_de_conversores_no_lleva_cifras_sueltas():
    fallos = fallos_cifras(_pagina_cv())
    assert not fallos, fallos[:10]


def test_la_guarda_de_cifras_ve_una_cifra_suelta():
    t = _pagina_cv()
    f = fallos_cifras(t.replace("</main>", "<p>Se juzgaron 42 casos.</p></main>"))
    assert len(f) == 1 and "42" in f[0], f
    f = fallos_cifras(t.replace("</main>", "<p>Cuatro condiciones.</p></main>"))
    assert len(f) == 1 and "Cuatro" in f[0], f
    f = fallos_cifras(re.sub(r'(<meta name="description" content=")', r"\g<1>15 discrepancias. ", t, 1))
    assert len(f) == 1 and "15" in f[0], f
    assert not fallos_cifras(t.replace("</main>", "<p>PV1-3, ORU^R01, A02, #624 y 40bbc3ef</p></main>"))


def test_las_tarjetas_de_la_pagina_de_conversores_estan_completas():
    fallos = fallos_tarjetas(_pagina_cv())
    assert not fallos, fallos


def test_la_guarda_de_tarjetas_ve_un_cambio():
    t = _pagina_cv()
    a = [m.start() for m in re.finditer(r'<article class="disc"', t)]
    assert len(a) > 2
    fin = lambda i: t.index("</article>", i) + len("</article>")  # noqa: E731
    sin = t[:a[0]] + t[fin(a[0]):]
    assert any(f.startswith("falta la tarjeta") for f in fallos_tarjetas(sin))
    doble = t[:fin(a[0])] + t[a[0]:fin(a[0])] + t[fin(a[0]):]
    assert any(f.startswith("tarjeta de más") for f in fallos_tarjetas(doble))
    cambiado = t[:a[0]] + t[a[1]:fin(a[1])] + t[fin(a[0]):a[1]] + t[a[0]:fin(a[0])] + t[fin(a[1]):]
    assert any(f.startswith("orden") for f in fallos_tarjetas(cambiado))


def test_las_paginas_son_accesibles_sin_javascript():
    fallos = []
    for rel in rastreados():
        if rel.startswith("docs/") and rel.endswith(".html"):
            fallos += fallos_accesibles(rel, leer(rel))
    assert not fallos, fallos


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
