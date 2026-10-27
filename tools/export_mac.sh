#!/usr/bin/env bash
# Exporta o jogo como app nativo de macOS (universal: Apple Silicon + Intel).
# Requer os export templates da mesma versão do Godot instalados
# (Editor > Gerenciar Modelos de Exportação > Baixar e instalar).
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p export
godot --headless --import >/dev/null
godot --headless --export-release "macOS" "export/Tiaraju.zip"
cd export && rm -rf Tiaraju.app && unzip -qo Tiaraju.zip && echo "Pronto: export/Tiaraju.app (abra com: open export/Tiaraju.app)"
