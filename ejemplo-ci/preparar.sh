#!/usr/bin/env bash
# El proyecto de ejemplo (etapa 24, verificador/cv/ci/CI.md): deja el conversor donde el adaptador lo espera,
# $ARTEFACTOS/conv/conversor.py. Es la orden «preparar» del proyecto; este conversor no necesita red ni construccion.
#   bash ejemplo-ci/preparar.sh <artefactos>
set -euo pipefail
ART=$(realpath "$1")
AQUI=$(dirname "$(realpath "$0")")
mkdir -p "$ART/conv"
cp "$AQUI/conversor.py" "$ART/conv/conversor.py"
echo "conv/conversor.py: $(sha256sum "$ART/conv/conversor.py" | cut -c1-16)"
