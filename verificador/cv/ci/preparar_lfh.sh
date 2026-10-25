#!/usr/bin/env bash
# Etapa 23 (verificador/cv/ci/CI.md): trae LinuxForHealth v1.1.0 como en cv/CV1.md, dentro de la misma imagen del estudio y con
# red solo aqui. Deja <artefactos>/lfh/lib (el jar y sus dependencias), <artefactos>/lfh/clases (Arnes compilado) y
# <artefactos>/lfh/Arnes.java, que es lo que pide cv/adaptadores/linuxforhealth.json.
#   bash cv/ci/preparar_lfh.sh <artefactos>
set -euo pipefail
ART=$(realpath "$1")
LAB=${LAB:-$(realpath "$(dirname "$0")/../../..")}
IMAGEN=${IMAGEN:-maven:3.9-eclipse-temurin-11@sha256:7bb84a451705605a47d24eb844d4d9ab03e33e131a507db76aafe25db3907f64}
mkdir -p "$ART/lfh/lib" "$ART/lfh/clases" "$ART/.m2"
cp "$LAB/verificador/cv/lfh/Arnes.java" "$ART/lfh/Arnes.java"
cp "$LAB/verificador/cv/lfh/pom.xml" "$ART/pom.xml"
docker pull "$IMAGEN"
docker run --rm --user "$(id -u):$(id -g)" -e HOME=/tmp -e MAVEN_CONFIG=/tmp/.m2 -v "$ART:/w" -- "$IMAGEN" sh -euc '
  mvn -q -B -f /w/pom.xml -Dmaven.repo.local=/w/.m2 dependency:copy-dependencies -DoutputDirectory=/w/lfh/lib &&
  javac --release 11 -d /w/lfh/clases -cp "/w/lfh/lib/*" /w/lfh/Arnes.java'
n=$(ls "$ART/lfh/lib"/*.jar | wc -l)
echo "lfh/lib: $n jar; Arnes.class: $(ls "$ART/lfh/clases")"
test "$n" -ge 70
rm -rf "$ART/.m2" "$ART/pom.xml"
