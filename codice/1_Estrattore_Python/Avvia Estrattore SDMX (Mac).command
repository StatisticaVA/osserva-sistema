#!/bin/bash
cd "$(dirname "$0")" || exit 1
clear
echo "=== Estrattore SDMX ISTAT - avvio ==="
if command -v python3 >/dev/null 2>&1; then PY=python3
elif command -v python >/dev/null 2>&1; then PY=python
else echo "Python 3 non installato: https://www.python.org/downloads/"; read -r -p "Invio per chiudere..."; exit 1; fi
echo "Controllo librerie (prima volta)..."
$PY -m pip install --user --quiet --disable-pip-version-check requests pandas openpyxl lxml 2>/dev/null \
  || $PY -m pip install --user --quiet --break-system-packages requests pandas openpyxl lxml 2>/dev/null
$PY "sdmx_gui.py"
[ $? -ne 0 ] && read -r -p "Problema rilevato. Invio per chiudere..."
