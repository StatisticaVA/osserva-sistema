@echo off
cd /d "%~dp0"
title Estrattore SDMX ISTAT
echo === Estrattore SDMX ISTAT - avvio ===
where python >nul 2>&1
if errorlevel 1 ( echo Python non installato: https://www.python.org/downloads/ & pause & exit /b 1 )
echo Controllo librerie (prima volta)...
python -m pip install --quiet --disable-pip-version-check requests pandas openpyxl lxml
python "sdmx_gui.py"
if errorlevel 1 ( echo. & echo Problema rilevato. & pause )
